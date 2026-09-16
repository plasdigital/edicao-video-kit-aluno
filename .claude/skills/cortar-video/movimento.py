#!/usr/bin/env python3
"""
Mede MOVIMENTO DE TELA e usa isso pra refinar os silencios.

O problema que isso resolve: o silencios.py so ouve o AUDIO. Ele nao sabe a diferenca entre
"parou de falar porque acabou a frase" e "parou de falar porque esta clicando,
digitando ou esperando a Meta responder". Em aula de configuracao a segunda
situacao domina - e cortar ali teletransporta a tela.

Medido numa aula de 95min: a pausa de 29,9s em 01:14:32 tem SEIS momentos
de movimento e um vazio real de 9s no meio. Um teto fixo de tempo jogaria fora os
cliques e manteria 1,5s arbitrario. Cruzar com a tela corta so o vazio.

COMO MEDE: uma passada linear com ffmpeg, em 160x90 e 4 quadros por segundo,
usando tblend=difference (cada quadro vira a diferenca em relacao ao anterior) e
signalstats.YAVG (o brilho medio dessa diferenca). Tela parada da 0,02-0,5 (so
ruido de compressao); clique, scroll ou troca de aba da 2-60. A separacao e de
uma ordem de grandeza, entao o limiar nao e delicado.

Uso:
  movimento.py bruto.mp4 -o movimento.json
  movimento.py bruto.mp4 --silencio silencio.json -o silencio-refinado.json
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

# Tela parada fica em 0,02-0,55; qualquer acao passa de 2. 1.0 fica no meio do vazio.
LIMIAR = 1.0
# Quanto de video preservar em volta de cada quadro com movimento. Generoso de
# proposito: melhor manter meio segundo a mais que cortar o clique pela metade.
MARGEM_ANTES = 0.4
MARGEM_DEPOIS = 0.8
# Nao vale cortar um buraco menor que isso: a emenda custa mais que o silencio.
MINIMO_CORTE = 0.6


def medir(fonte, fps):
    """Uma passada no video inteiro -> [(tempo, score), ...]"""
    cmd = ["ffmpeg", "-hide_banner", "-v", "error", "-i", str(fonte), "-an",
           "-vf", f"fps={fps},scale=160:90,tblend=all_mode=difference,"
                  "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
           "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"erro: ffmpeg falhou\n{r.stderr[-2000:]}")
    pontos, t = [], None
    for linha in r.stdout.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", linha)
        if m:
            t = float(m.group(1)); continue
        m = re.search(r"YAVG=([0-9.eE+-]+)", linha)
        if m and t is not None:
            pontos.append((t, float(m.group(1)))); t = None
    return pontos


def janelas_com_movimento(pontos, limiar, fps):
    """quadros acima do limiar -> intervalos [inicio, fim] ja com margem e unidos"""
    jan = []
    for t, v in pontos:
        if v >= limiar:
            jan.append([t - MARGEM_ANTES, t + 1.0 / fps + MARGEM_DEPOIS])
    jan.sort()
    unidas = []
    for a, b in jan:
        if unidas and a <= unidas[-1][1]:
            unidas[-1][1] = max(unidas[-1][1], b)
        else:
            unidas.append([a, b])
    return unidas


def subtrai(alvos, buracos):
    """de cada intervalo de 'alvos', remove o que colide com 'buracos'"""
    out = []
    for a, b in alvos:
        pedacos = [[a, b]]
        for ha, hb in buracos:
            novos = []
            for pa, pb in pedacos:
                if hb <= pa or ha >= pb:
                    novos.append([pa, pb]); continue
                if ha > pa:
                    novos.append([pa, min(ha, pb)])
                if hb < pb:
                    novos.append([max(hb, pa), pb])
            pedacos = novos
        out += [p for p in pedacos if p[1] - p[0] >= MINIMO_CORTE]
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fonte")
    p.add_argument("--silencio", help="silencio.json a refinar (do silencios.py)")
    p.add_argument("-o", "--out", default="movimento.json")
    p.add_argument("--fps", type=float, default=4.0, help="quadros por segundo amostrados")
    p.add_argument("--limiar", type=float, default=LIMIAR)
    a = p.parse_args()

    print(f"medindo movimento de tela ({a.fps} quadros/s, 160x90)...", flush=True)
    pontos = medir(a.fonte, a.fps)
    if not pontos:
        sys.exit("erro: nenhuma amostra - o filtro nao produziu metadados")
    mov = janelas_com_movimento(pontos, a.limiar, a.fps)
    tot = sum(b - a_ for a_, b in mov)
    print(f"{len(pontos)} amostras | {len(mov)} janelas com movimento "
          f"({tot/60:.1f} min de tela ativa)")

    if not a.silencio:
        json.dump(mov, open(a.out, "w"), ensure_ascii=False)
        print(f"-> {a.out}")
        return

    sil = json.load(open(a.silencio))
    antes = sum(b - x for x, b in sil)
    ref = subtrai(sil, mov)
    depois = sum(b - x for x, b in ref)
    print(f"silencio: {len(sil)} aparos ({antes/60:.1f} min) -> "
          f"{len(ref)} aparos ({depois/60:.1f} min)")
    print(f"preservado por ter tela mexendo: {(antes-depois)/60:.1f} min")
    json.dump([[round(x, 3), round(b, 3)] for x, b in ref],
              open(a.out, "w"), ensure_ascii=False)
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
