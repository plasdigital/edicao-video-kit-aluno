#!/usr/bin/env python3
"""
Acha as pausas do video e devolve os ranges de corte, em SEGUNDOS.

Faz as duas coisas numa chamada so: roda o ffmpeg silencedetect no audio de verdade
e converte o resultado em ranges de remocao, aparando cada pausa longa mas deixando
um respiro (senao a emenda fica robotica e a fala colada demais).

Uso:
  silencios.py bruto.mp4 [--limiar 0.6] [--merge-gap 0.15] [--noise -30] [--dur-min 0.35]
  silencios.py entrada/video.mp4 -o transcricao/silencios.json

  --limiar     so apara pausa MAIOR que isso. 0.5 agressivo, 0.6 equilibrado, 0.8 conservador
  --noise      o que conta como silencio, em dB (default -30)
  --dur-min    duracao minima pro ffmpeg reportar um silencio (default 0.35)
  --merge-gap  junta silencios separados por menos que isso. LER A NOTA
  --respiro    segundos de pausa que ficam de cada lado da emenda (default 0.13/0.17)

POR QUE ffmpeg E NAO A TRANSCRICAO: o timestamp do ASR e uma ESTIMATIVA de
alinhamento, nao uma medida do audio. Ele erra pros dois lados, e de um jeito que
muda por motor e por modelo - nao da pra corrigir com um fator, so da pra nao usar.
O silencedetect le o audio e nao depende de modelo nenhum.

NOTA MERGE-GAP (leia antes de aumentar esse valor):
  O silencedetect FRAGMENTA uma pausa longa quando tem um estalo, respiracao ou
  ruido de boca no meio dela. Uma pausa real de 2s vira tres silencios de 0.5s
  separados por ~0.05s de "fala" que nao e fala. Cada pedaco fica abaixo do limiar,
  todos sao descartados, e a pausa longa sobrevive inteira no corte final.

  MAS o intervalo entre dois silencios pode ser FALA DE VERDADE. Esse script so ve
  os timestamps, nao o audio: ele nao distingue um estalo de uma palavra curta.
  Fundir por cima de fala APAGA a palavra, e apaga em silencio.

  Por isso o default e 0.15s: estalo e respiracao duram ~50-150ms, palavra nao.
  Medido pelo autor do original num video de 12min: com 0.7s comia 21 palavras
  faladas; com 0.3s comia 3; com 0.15s nao comeu nenhuma e ainda fundiu os slivers.

Saida: resumo em stderr + JSON dos ranges (ordenados, sem overlap) no stdout.
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path


def duracao(fonte):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(fonte)], capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        sys.exit(f"erro: ffprobe nao leu a duracao de {fonte}")
    return float(r.stdout.strip())


def detecta(fonte, noise_db, dur_min):
    """roda o silencedetect e devolve [(inicio_s, fim_s, duracao_s)]"""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(fonte),
         "-af", f"silencedetect=noise={noise_db}dB:d={dur_min}", "-f", "null", "-"],
        capture_output=True, text=True)
    out, start = [], None
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", line)
        if m:
            start = max(0.0, float(m.group(1)))
            continue
        m = re.search(r"silence_end: ([\d.]+).*silence_duration: ([\d.]+)", line)
        if m and start is not None:
            out.append((start, float(m.group(1)), float(m.group(2))))
            start = None
    return out


def merge_proximos(sils, gap):
    """junta silencios separados por < gap (estalo/respiracao no meio da pausa)"""
    if not sils:
        return []
    sils = sorted(sils)
    out = [list(sils[0])]
    for a, b, _ in sils[1:]:
        if a - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b, 0])
    return [(a, b, b - a) for a, b, _ in out]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fonte")
    p.add_argument("--config", help="opcional: le silencio.* de um config.json")
    p.add_argument("--limiar", type=float, default=None)
    p.add_argument("--merge-gap", type=float, default=None)
    p.add_argument("--noise", type=float, default=None, help="dB, default -30")
    p.add_argument("--dur-min", type=float, default=None)
    p.add_argument("--respiro-head", type=float, default=None, help="segundos")
    p.add_argument("--respiro-tail", type=float, default=None, help="segundos")
    p.add_argument("-o", "--out", help="grava o JSON tambem num arquivo")
    args = p.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("erro: ffmpeg nao esta no PATH.")
    if not Path(args.fonte).exists():
        sys.exit(f"erro: fonte nao encontrada: {args.fonte}")

    cfg = {}
    if args.config:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8")).get("silencio", {})

    def val(flag, chave, padrao):
        if flag is not None:
            return flag
        return cfg.get(chave, padrao)

    limiar = val(args.limiar, "limiar_s", 0.6)
    merge_gap = val(args.merge_gap, "merge_gap_s", 0.15)
    noise = val(args.noise, "noise_db", -30)
    dur_min = val(args.dur_min, "dur_min_s", 0.35)
    head = val(args.respiro_head, "respiro_head_s", 0.13)
    tail = val(args.respiro_tail, "respiro_tail_s", 0.17)

    total = duracao(args.fonte)
    brutos = detecta(args.fonte, noise, dur_min)
    if not brutos:
        sys.stderr.write(f"nenhum silencio detectado ({noise}dB, >={dur_min}s). "
                         "Video ja e corrido, ou o limiar de ruido esta baixo demais.\n")
        print("[]")
        return

    sils = merge_proximos(brutos, merge_gap)
    fundidos = len(brutos) - len(sils)

    ranges, removido = [], 0.0
    for a, b, d in sils:
        if d <= limiar:
            continue
        ca, cb = a + head, min(b - tail, total)
        if cb - ca < 0.15:      # aparo minusculo nao vale a emenda
            continue
        ranges.append([round(ca, 3), round(cb, 3)])
        removido += cb - ca

    ranges.sort()
    limpos = []
    for r in ranges:
        if limpos and r[0] <= limpos[-1][1]:
            limpos[-1][1] = max(limpos[-1][1], r[1])
        else:
            limpos.append(list(r))

    sys.stderr.write(
        f"fonte: {total / 60:.1f}min\n"
        f"silencios: {len(brutos)} brutos -> {len(sils)} apos merge (<{merge_gap}s juntados: {fundidos})\n"
        f"acima do limiar {limiar}s: {len(limpos)} aparos\n"
        f"remove {removido:.1f}s ({removido / total * 100:.1f}% do video)\n")
    if merge_gap > 0.25 and fundidos:
        sys.stderr.write(
            f"AVISO: --merge-gap {merge_gap}s e alto. Um intervalo desse tamanho entre\n"
            f"  silencios costuma ser FALA, nao estalo. {fundidos} silencios foram fundidos e a\n"
            f"  fala entre eles vai ser APAGADA sem aviso no video final.\n")

    saida = json.dumps(limpos)
    if args.out:
        Path(args.out).write_text(saida, encoding="utf-8")
        sys.stderr.write(f"-> {args.out}\n")
    print(saida)


if __name__ == "__main__":
    main()
