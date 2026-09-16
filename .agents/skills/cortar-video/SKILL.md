---
name: cortar-video
description: Edição com FFmpeg na gravação do aluno — tira os erros marcados na fala, apara pausas sem cortar quem está clicando na tela, aplica os cortes no frame exato e faz as operações de acabamento (juntar trechos, mixar efeitos sonoros, nivelar volume, extrair áudio). Use depois da transcrição e antes ou depois do motion, sempre com o plano aprovado pelo aluno.
---

# Cortar e montar com FFmpeg

A pasta desta skill é `.claude/skills/cortar-video/` (Claude) ou `.agents/skills/cortar-video/` (ChatGPT/Codex). Chamada abaixo de `<skill>`.
Pré-requisito: `transcricao/flat.txt` (skill `transcrever-video`). Os JSONs de corte vão para `cortes/`. O original em `entrada/` nunca é alterado.

A ordem importa — cada etapa usa os tempos do vídeo original, e o corte é feito uma vez só no fim.

## 1. Erros marcados na fala

Técnica de gravação: ao errar, o aluno fala uma frase que nunca diria por acaso (sugestão: **"erro erro erro"**), respira e refaz o trecho.

```bash
python <skill>/achar-marcadores.py transcricao/flat.txt --marcadores "erro erro erro:curto"
```

O script **acha, não corta**: mostra cada ocorrência com o texto em volta e fronteiras candidatas. Você decide o corte lendo:

- **Início** = o FIM da última palavra boa antes do erro (usar o início dela come a palavra).
- **Fim** = o INÍCIO da primeira palavra boa da retomada. A refeita costuma repetir as palavras de antes do erro: o corte começa onde a frase errada começou, não só no marcador.
- Marcador dito como conteúdo (explicando a técnica) fica.
- Revise as SUSPEITAS: o Whisper às vezes quebra o marcador.

Grave os cortes decididos em `cortes/erros.json` no formato `[[inicio, fim], ...]` (segundos).

## 2. Pausas (opcional)

```bash
python <skill>/silencios.py entrada/<video> -o cortes/silencios.json
```

Mede no áudio, não na transcrição. `--limiar 0.8` conservador, `0.6` equilibrado, `0.5` agressivo. **Nunca suba `--merge-gap` acima de 0.25**: apaga palavra curta sem avisar.

Gravação de tela (aula, tutorial)? Silêncio pode ser o aluno clicando. Cruze com o movimento da tela:

```bash
python <skill>/movimento.py entrada/<video> --silencio cortes/silencios.json -o cortes/silencios-refinado.json
```

Aparar pausa deixa o ritmo mais rápido, mas muitos cortes secos seguidos parecem pulos. Mostre ao aluno uma amostra antes de aplicar no vídeo todo; se ele preferir, corte só os erros.

## 3. Plano → aprovação

```bash
python <skill>/cortar.py entrada/<video> --remove @cortes/erros.json --remove @cortes/silencios.json --dry-run
```

Mostra quanto sai e os segmentos que ficam. **Mostre ao aluno e espere o OK** — corte errado só aparece depois do render.

## 4. Cortar

```bash
python <skill>/cortar.py entrada/<video> --remove @cortes/erros.json -o exportacoes/cortado-preview.mp4 --preview   # 720p rápido
python <skill>/cortar.py entrada/<video> --remove @cortes/erros.json -o exportacoes/cortado.mp4
```

Re-encoda cada trecho (corte no frame exato, não no keyframe), põe 30 ms de fade no áudio de cada emenda e confere a duração no fim. Duas câmeras gravadas juntas: `--fonte-extra nome=arquivo.mp4 --camera '[[0,12.4,"nome"],...]'`.

**Depois do corte, os tempos mudam.** Para motion e legendas sobre o vídeo cortado, transcreva o `cortado.mp4` de novo (cache novo, é outro arquivo) e confira que nenhum marcador sobrou:

```bash
python <pasta da skill transcrever-video>/transcrever.py exportacoes/cortado.mp4 -o transcricao/cortado/flat.txt
python <skill>/achar-marcadores.py transcricao/cortado/flat.txt --marcadores "erro erro erro:curto"   # tem de dar 0
```

## 5. Receitas de acabamento

Informações do arquivo (somente leitura):

```bash
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,duration -of json <arquivo>
```

Extrair o áudio:

```bash
ffmpeg -i exportacoes/cortado.mp4 -vn -ac 1 -ar 48000 cortes/voz.wav
```

Mixar a trilha de efeitos (WAV da mesma duração, feita conforme `docs/transicoes-e-som.md`) sem abafar a voz:

```bash
ffmpeg -i exportacoes/editado.mp4 -i cortes/sfx.wav -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k exportacoes/com-som.mp4
```

Nivelar o volume para internet (duas passadas dão resultado mais preciso; esta é a de uma passada):

```bash
ffmpeg -i exportacoes/com-som.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k exportacoes/final.mp4
```

Juntar abertura e corpo **com formatos diferentes** (não use `-c copy` no concat sem conferir que tudo bate):

```bash
ffmpeg -i abertura.mp4 -i corpo.mp4 -filter_complex "[0:v]scale=1920:1080,fps=30,format=yuv420p,setsar=1[v0];[1:v]scale=1920:1080,fps=30,format=yuv420p,setsar=1[v1];[0:a]aresample=48000[a0];[1:a]aresample=48000[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset veryfast -c:a aac -b:a 192k exportacoes/juntado.mp4
```

Ajuste resolução e fps ao vídeo principal (veja no `ffprobe`). No fim, rode a skill `conferir-video`.

## Travas

- Não sobrescrever nada em `entrada/`. Cada versão é um arquivo novo em `exportacoes/`.
- Não aplicar corte sem o plano (`--dry-run`) aprovado.
- Não renderizar o vídeo inteiro antes de uma prévia aprovada.

## Armadilhas

| Sintoma | O que é |
|---|---|
| corte comeu o fim de uma palavra | usou o início da palavra boa como início do corte: use o fim |
| sobrou metade da frase errada | o corte começou no marcador: volte até onde a frase errada começou |
| estalo na emenda | segmento sem fade (use o `cortar.py`, não `-c copy`) |
| vídeo final mais curto que o esperado | render truncado: o `cortar.py` avisa o desvio; confira o fim |
| legenda fora de tempo depois do corte | usou o `flat.txt` do original: transcreva o cortado |
| áudio some depois do `amix` | trilha de efeitos mais longa/curta ou mono × estéreo: confira com `ffprobe` |
