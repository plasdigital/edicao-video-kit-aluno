#!/usr/bin/env python3
"""
Aplica os cortes com ffmpeg e exporta o video final.

Recebe ranges de REMOCAO (em segundos), inverte pra segmentos de MANUTENCAO,
renderiza cada segmento e concatena. Substitui o editor
externo do original: aqui e ffmpeg puro, sem app pago e sem clonar repo de terceiro.

Uso:
  cortar.py bruto.mp4 --remove @cortes.json -o final.mp4
  cortar.py bruto.mp4 --remove @marcadores.json --remove @silencio.json -o final.mp4
  cortar.py bruto.mp4 --remove @cortes.json --dry-run
  cortar.py bruto.mp4 --remove @cortes.json -o preview.mp4 --preview
  cortar.py tela.mp4 --fonte cara=cara.mp4 --remove @cortes.json \
            --camera '[[0,12.4,"cara"],[12.4,48.9,"tela"]]' -o final.mp4

  --remove   JSON [[a,b],...] ou @arquivo.json. Pode repetir: a uniao e feita aqui.
  --camera   multicam: [[inicio,fim,"nome"],...] no tempo da FONTE (antes do corte).
             O nome bate com --fonte nome=arquivo.mp4; a fonte posicional e o default.
  --preview  720p e preset ultrafast: pra conferir o corte sem queimar tempo no final.
  --dry-run  so mostra o plano (quantos cortes, duracao antes/depois), nao renderiza.

POR QUE RE-ENCODA: corte sem re-encode (-c copy) so cai em keyframe, entao o corte
sai varios frames longe de onde foi pedido - o suficiente pra comer palavra ou
deixar sobra do erro. Re-encodar por segmento corta no frame exato.

FADE NA EMENDA: 30ms de fade no audio na entrada e na saida de cada segmento. Sem
isso, emendar duas ondas em fases diferentes estala.

VERIFICACAO: no fim confere a duracao do arquivo com o ffprobe contra a esperada.
Render trunca as vezes e finaliza curto, cortando o fim no meio da frase.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

FADE = 0.03  # segundos de fade no audio em cada ponta do segmento


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(fonte):
    r = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_entries",
            "format=duration:stream=codec_type,width,height,r_frame_rate", str(fonte)])
    if r.returncode:
        sys.exit(f"erro: ffprobe falhou em {fonte}\n{r.stderr}")
    d = json.loads(r.stdout)
    info = {"duracao": float(d["format"]["duration"]), "w": None, "h": None, "fps": None}
    for s in d.get("streams", []):
        if s.get("codec_type") == "video" and info["w"] is None:
            info["w"], info["h"] = s.get("width"), s.get("height")
            num, _, den = (s.get("r_frame_rate") or "30/1").partition("/")
            info["fps"] = round(float(num) / float(den or 1), 3)
    return info


def carrega_ranges(v):
    if v.startswith("@"):
        txt = Path(v[1:]).read_text(encoding="utf-8").strip()
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return json.loads(txt.splitlines()[-1])   # tolera log + JSON na ultima linha
    return json.loads(v)


def normaliza(rs):
    """ordena e funde ranges que encostam ou se sobrepoem"""
    rs = sorted([list(map(float, r[:2])) for r in rs if float(r[1]) > float(r[0])])
    out = []
    for r in rs:
        if out and r[0] <= out[-1][1]:
            out[-1][1] = max(out[-1][1], r[1])
        else:
            out.append(r)
    return out


def inverte(remover, total):
    """ranges de remocao -> segmentos que ficam"""
    manter, cursor = [], 0.0
    for a, b in remover:
        a, b = max(0.0, a), min(total, b)
        if a > cursor:
            manter.append([cursor, a])
        cursor = max(cursor, b)
    if cursor < total:
        manter.append([cursor, total])
    return [s for s in manter if s[1] - s[0] > 0.04]   # segmento de 1 frame nao ajuda ninguem


def qual_fonte(t, camera, padrao):
    for a, b, nome in camera:
        if a <= t < b:
            return nome
    return padrao


def fmt(s):
    return f"{int(s // 60):02d}:{s % 60:06.3f}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fonte")
    p.add_argument("--fonte-extra", action="append", default=[], metavar="nome=arquivo",
                   dest="fontes", help="fonte adicional pro multicam")
    p.add_argument("--remove", action="append", default=[], required=True)
    p.add_argument("--camera", help='multicam: [[inicio,fim,"nome"],...]')
    p.add_argument("-o", "--out", default="final.mp4")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--crf", type=int, default=18)
    args = p.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("erro: ffmpeg nao esta no PATH.")
    if not Path(args.fonte).exists():
        sys.exit(f"erro: fonte nao encontrada: {args.fonte}")

    principal = Path(args.fonte).resolve()
    nome_principal = principal.stem
    fontes = {nome_principal: principal}
    for f in args.fontes:
        nome, _, caminho = f.partition("=")
        if not caminho or not Path(caminho).exists():
            sys.exit(f"erro: --fonte-extra invalida ou arquivo inexistente: {f}")
        fontes[nome] = Path(caminho).resolve()

    info = probe(principal)
    total = info["duracao"]

    remover = normaliza([r for v in args.remove for r in carrega_ranges(v)])
    manter = inverte(remover, total)
    if not manter:
        sys.exit("erro: os cortes cobrem o video inteiro. Confere os ranges.")

    camera = json.loads(args.camera) if args.camera else []
    if camera:
        faltando = {c[2] for c in camera} - set(fontes)
        if faltando:
            sys.exit(f"erro: --camera cita fonte(s) sem arquivo: {faltando}. Usa --fonte-extra nome=arquivo.")

    dur_final = sum(b - a for a, b in manter)
    removido = total - dur_final
    print(f"fonte     {principal.name}  {total / 60:.2f}min  {info['w']}x{info['h']} @ {info['fps']}fps")
    print(f"cortes    {len(remover)} trechos removidos, {removido:.1f}s ({removido / total * 100:.1f}%)")
    print(f"final     {dur_final / 60:.2f}min em {len(manter)} segmentos")
    if args.dry_run:
        print("\nsegmentos que ficam:")
        for i, (a, b) in enumerate(manter, 1):
            fonte_seg = qual_fonte(a, camera, nome_principal) if camera else nome_principal
            print(f"  {i:3d}  {fmt(a)} -> {fmt(b)}  ({b - a:6.2f}s)  {fonte_seg}")
        return

    escala = "scale=-2:720" if args.preview else f"scale={info['w']}:{info['h']}"
    preset = "ultrafast" if args.preview else "veryfast"
    crf = 28 if args.preview else args.crf

    tmp = Path(tempfile.mkdtemp(prefix="editar-video-"))
    partes = []
    try:
        for i, (a, b) in enumerate(manter):
            dur = b - a
            fonte_seg = fontes[qual_fonte(a, camera, nome_principal)] if camera else principal
            saida = tmp / f"seg{i:04d}.mp4"
            fade_out = max(0.0, dur - FADE)
            af = f"afade=t=in:st=0:d={FADE},afade=t=out:st={fade_out:.3f}:d={FADE}"
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                   "-ss", f"{a:.3f}", "-i", str(fonte_seg), "-t", f"{dur:.3f}",
                   "-vf", f"{escala},fps={info['fps']}", "-af", af,
                   "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                   "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                   str(saida)]
            r = sh(cmd)
            if r.returncode or not saida.exists():
                sys.exit(f"erro no segmento {i} ({fmt(a)}->{fmt(b)}):\n{r.stderr[-800:]}")
            partes.append(saida)
            sys.stderr.write(f"\rsegmento {i + 1}/{len(manter)}   ")
        sys.stderr.write("\n")

        lista = tmp / "lista.txt"
        lista.write_text("".join(f"file '{p.as_posix()}'\n" for p in partes), encoding="utf-8")
        out = Path(args.out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        r = sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(out)])
        if r.returncode or not out.exists():
            sys.exit(f"erro ao concatenar:\n{r.stderr[-800:]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    real = probe(out)["duracao"]
    desvio = real - dur_final
    print(f"\n-> {out}")
    print(f"   esperado {dur_final:.2f}s, arquivo {real:.2f}s (desvio {desvio:+.2f}s)")
    if abs(desvio) > 1.0:
        print("   AVISO: desvio acima de 1s. Render truncado corta o fim no meio da frase - confere o final do video.")


if __name__ == "__main__":
    main()
