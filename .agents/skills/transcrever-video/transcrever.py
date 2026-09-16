#!/usr/bin/env python3
"""
Transcreve com timestamp POR PALAVRA (faster-whisper, local e gratuito).

Saídas, na mesma pasta de -o:
  flat.txt          1 palavra por linha: indice|inicio|fim|texto  (para cortes e legendas)
  transcricao.md    frases com [m:ss] (para ler, revisar e corrigir termos)

Uso:
  python transcrever.py entrada/video.mp4 -o transcricao/flat.txt
  python transcrever.py entrada/video.mp4 -o transcricao/flat.txt --modelo small   # sem GPU
  python transcrever.py entrada/video.mp4 -o transcricao/flat.txt --device cpu

DISPOSITIVO (--device, padrão auto): tenta a placa NVIDIA e cai para a CPU se ela
não existir. Na CPU o modelo medium é lento em vídeo longo; use --modelo small.

CACHE: fica em .cache/ ao lado da saída e é reutilizado. Não re-transcreve fonte que
não mudou. --force ignora.

MODELO (--modelo, padrão medium): timestamp ruim vira CORTE ruim, e corte ruim só
aparece depois do render. Se a transcrição é só para LER, 'small' resolve.
"""
import argparse, hashlib, json, os, site, subprocess, sys
from pathlib import Path


def add_cuda_dlls():
    """Registra as DLLs do CUDA 12 instaladas via pip (pacotes nvidia-*-cu12).

    Sem isso o faster-whisper morre com "cublas64_12.dll is not found or cannot be
    loaded" no Windows. O pacote decisivo e o nvidia-cuda-runtime-cu12 (fornece o
    cudart64_12.dll, do qual o cuBLAS depende).
    """
    subdirs = ("nvidia/cuda_runtime/bin", "nvidia/cublas/bin",
               "nvidia/cudnn/bin", "nvidia/cuda_nvrtc/bin")
    for sp in set(site.getsitepackages() + [site.getusersitepackages()]):
        for d in subdirs:
            p = os.path.join(sp, *d.split("/"))
            if os.path.isdir(p):
                os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
                try:
                    os.add_dll_directory(p)
                except OSError:
                    pass


def sha_fonte(path):
    h = hashlib.sha256()
    st = os.stat(path)
    h.update(f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}".encode())
    return h.hexdigest()[:16]


def extrai_audio(video, dest):
    """16kHz mono wav: menor, mais rapido, e o que os motores querem"""
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video),
         "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(dest)],
        check=True)
    return dest


# ---- motores: devolvem [{"text","start","end"}] com start/end em SEGUNDOS ----

def via_faster_whisper(audio, idioma, modelo, device):
    auto = device == "auto"
    if auto:
        device = "cuda"
    if device != "cpu":
        add_cuda_dlls()
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("erro: faster-whisper nao instalado.\n  pip install faster-whisper")

    def carrega(dev, ct):
        sys.stderr.write(f"whisper: modelo '{modelo}' em {dev} ({ct})...\n")
        return WhisperModel(modelo, device=dev, compute_type=ct)

    try:
        m = carrega(device, "int8_float16" if device == "cuda" else "int8")
    except Exception as e:
        if device != "cuda":
            raise
        if auto:
            sys.stderr.write("whisper: sem GPU compatível; usando a CPU (em vídeo longo, prefira --modelo small).\n")
        else:
            sys.stderr.write(f"whisper: GPU falhou ({type(e).__name__}: {e}); caindo pra CPU.\n")
        m = carrega("cpu", "int8")

    segmentos, _ = m.transcribe(str(audio), language=idioma, word_timestamps=True,
                                vad_filter=False)
    palavras = []
    for seg in segmentos:
        for w in (seg.words or []):
            t = (w.word or "").strip()
            if t:
                palavras.append({"text": t, "start": float(w.start), "end": float(w.end)})
    return palavras


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fonte")
    p.add_argument("-o", "--out", default="flat.txt")
    p.add_argument("--idioma", default="pt")
    p.add_argument("--modelo", default="medium", help="tiny/base/small/medium/large-v3")
    p.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    p.add_argument("--unit", choices=["s", "ms", "frames"], default="s")
    p.add_argument("--fps", type=float, default=30.0)
    p.add_argument("--force", action="store_true", help="ignora o cache")
    args = p.parse_args()

    if not Path(args.fonte).exists():
        sys.exit(f"erro: fonte nao encontrada: {args.fonte}")

    motor = "whisper"

    cache_dir = Path(args.out).resolve().parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    # A chave inclui modelo e idioma: sem isso, pedir --modelo large depois de rodar
    # com medium devolvia o resultado do medium CALADO - e subir de modelo e
    # justamente a rota de recuperacao quando o timestamp derrapa.
    chave = f"{sha_fonte(args.fonte)}-{motor}"
    if motor == "whisper":
        chave += f"-{args.modelo}"
    chave += f"-{args.idioma}"
    cache = cache_dir / f"{chave}.json"

    if cache.exists() and not args.force:
        sys.stderr.write(f"cache: reusando {cache.name} (--force pra refazer)\n")
        palavras = json.loads(cache.read_text(encoding="utf-8"))
    else:
        wav = cache_dir / f"{sha_fonte(args.fonte)}.wav"
        if not wav.exists():
            sys.stderr.write("extraindo audio...\n")
            extrai_audio(args.fonte, wav)
        palavras = via_faster_whisper(wav, args.idioma, args.modelo, args.device)
        cache.write_text(json.dumps(palavras), encoding="utf-8")
        sys.stderr.write(f"cache: gravado em {cache.name}\n")

    if not palavras:
        sys.exit("erro: transcricao vazia. Conferiu se a fonte tem audio?")

    def conv(seg):
        if args.unit == "frames":
            return round(seg * args.fps)
        if args.unit == "ms":
            return round(seg * 1000)
        return round(seg, 3)

    with open(args.out, "w", encoding="utf-8") as f:
        for i, w in enumerate(palavras, 1):
            f.write(f"{i}|{conv(w['start'])}|{conv(w['end'])}|{w['text']}\n")

    # versão para ler: frases com o tempo de início
    md = Path(args.out).with_name("transcricao.md")
    linhas, atual, ini = [], [], None
    for i, w in enumerate(palavras):
        if ini is None:
            ini = w["start"]
        atual.append(w["text"])
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        if (prox is None or w["text"][-1:] in ".?!" or len(atual) >= 25
                or prox["start"] - w["end"] > 0.8):
            linhas.append(f"[{int(ini // 60)}:{ini % 60:05.2f}] " + " ".join(atual))
            atual, ini = [], None
    md.write_text(f"# Transcrição: {Path(args.fonte).name}\n\n---\n\n" + "\n\n".join(linhas) + "\n",
                  encoding="utf-8")

    dur = palavras[-1]["end"]
    sys.stderr.write(f"ok: {len(palavras)} palavras, {dur / 60:.1f}min, "
                     f"unidade={args.unit}\n-> {args.out}\n-> {md}\n")


if __name__ == "__main__":
    main()
