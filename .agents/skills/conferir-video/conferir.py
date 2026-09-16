#!/usr/bin/env python3
"""Conferência de vídeo renderizado — amostra os instantes que erram.

Nasceu de um teste com HyperFrames em que os TRÊS erros que sobreviveram
estavam no meio de uma troca de cena e NENHUM aparecia no snapshot de repouso dos
cards. Conferir o repouso não basta: o erro mora na transição.

Dois modos:

  python conferir.py video.mp4 --em 5.5,11,21.35,26.5
  python conferir.py video.mp4 --storyboard storyboard.json [--folga 0.25]

No modo storyboard ele calcula sozinho os instantes que importam: pouco antes e
pouco depois de cada entrada e de cada saída de card. É onde o rosto encolhe cedo,
onde o contador mostra zero e onde sobra vão entre duas cenas.

Sai um JPG por instante e um mosaico com o tempo carimbado em cada quadro.
"""
import argparse, json, os, subprocess, sys

FONTE = "C:/Windows/Fonts/arialbd.ttf"


def instantes_do_storyboard(caminho, folga):
    sb = json.load(open(caminho, encoding="utf-8"))
    fim = sb.get("composition", {}).get("durationSeconds")
    pontos = set()
    for c in sb.get("cards", []):
        for t in (c["startSec"] - folga, c["startSec"] + folga,
                  c["endSec"] - folga, c["endSec"] + folga):
            if t > 0 and (fim is None or t < fim):
                pontos.add(round(t, 2))
    return sorted(pontos)


def extrair(video, t, destino, largura):
    vf = "scale=%d:-1" % largura
    if os.path.exists(FONTE):
        # No filtro do ffmpeg os dois-pontos separam opções: o "C:" do caminho
        # precisa virar "C\:", senão ele lê o resto da linha como opção solta.
        fonte = FONTE.replace(":", r"\:")
        vf += (",drawtext=fontfile='%s':text='%.2fs':x=14:y=12:fontsize=30:fontcolor=white"
               ":box=1:boxcolor=0x0D0900@0.75:boxborderw=10" % (fonte, t))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % t, "-i", video,
         "-frames:v", "1", "-vf", vf, destino],
        check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--em", help="instantes em segundos, separados por vírgula")
    ap.add_argument("--storyboard", help="storyboard.json — calcula as transições sozinho")
    ap.add_argument("--folga", type=float, default=0.25, help="quanto antes/depois de cada troca")
    ap.add_argument("--saida", default="conferencia")
    ap.add_argument("--largura", type=int, default=640)
    a = ap.parse_args()

    if a.em:
        pontos = [float(x) for x in a.em.split(",") if x.strip()]
    elif a.storyboard:
        pontos = instantes_do_storyboard(a.storyboard, a.folga)
    else:
        sys.exit("informe --em ou --storyboard")

    os.makedirs(a.saida, exist_ok=True)
    arquivos = []
    for i, t in enumerate(pontos):
        destino = os.path.join(a.saida, "q%03d.jpg" % i)
        extrair(a.video, t, destino, a.largura)
        arquivos.append(destino)
        print("  %6.2fs -> %s" % (t, os.path.basename(destino)))

    # Grade o mais quadrada possível, no máximo 4 por linha.
    colunas = min(4, len(arquivos))
    linhas = -(-len(arquivos) // colunas)
    mosaico = os.path.join(a.saida, "mosaico.jpg")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(a.saida, "q%03d.jpg"),
         "-filter_complex", "tile=%dx%d:padding=8:color=0x0D0900" % (colunas, linhas),
         "-frames:v", "1", mosaico],
        check=True)
    print("\n%d quadros | mosaico %dx%d em %s" % (len(arquivos), colunas, linhas, mosaico))


if __name__ == "__main__":
    main()
