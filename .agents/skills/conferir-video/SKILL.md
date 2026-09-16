---
name: conferir-video
description: Confere o MP4 exportado antes de entregar — duração dos streams, quadros nas trocas de cena, volume e a última frase. Use depois de todo render de vídeo completo; prévia no navegador não substitui esta conferência.
---

# Conferir o vídeo exportado

A pasta desta skill é `.claude/skills/conferir-video/` (Claude) ou `.agents/skills/conferir-video/` (ChatGPT/Codex). Tudo aqui é somente leitura sobre o vídeo; as saídas vão para `conferencia/`.

## 1. Streams

```bash
ffprobe -v error -show_entries stream=codec_type,duration,r_frame_rate,width,height -of json exportacoes/final.mp4
```

Áudio e vídeo com durações diferentes por mais de ~0,1 s → corte ou concatenação errada. Compare também com a duração esperada pelo plano de cortes.

## 2. Quadros nas trocas de cena

O erro mora na transição, não na cena parada. Liste os instantes de cada entrada e saída de cena (±0,25 s) e extraia:

```bash
python <pasta desta skill>/conferir.py exportacoes/final.mp4 --em 5.25,5.75,11.25,11.75 --saida conferencia
```

Gera um JPG por instante e `conferencia/mosaico.jpg`. Olhe o mosaico: rosto cortado, texto fora da tela, cena vazia entre duas cenas, número zerado.

## 3. Volume

```bash
ffmpeg -i exportacoes/final.mp4 -af loudnorm=print_format=summary -f null -
```

Referência para vídeo de internet: por volta de -16 LUFS integrado e true peak abaixo de -1 dBTP. É referência, não garantia: ouça.

## 4. Fala até o fim

Re-transcreva o exportado e compare as últimas frases com a transcrição original — é o jeito de achar frase final cortada:

```bash
python <pasta da skill transcrever-video>/transcrever.py exportacoes/final.mp4 -o conferencia/flat.txt --modelo small
```

## 5. Ouvir

Peça ao aluno para assistir inteiro, com som, em fone e em alto-falante. Relate o que você conferiu (itens 1–4) e o que só a audição dele confirma (sincronia labial, cansaço de efeitos, clareza da voz). Não diga "vídeo conferido" sem os quatro itens.
