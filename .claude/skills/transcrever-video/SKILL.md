---
name: transcrever-video
description: Transcreve a gravação do aluno com tempo por palavra (faster-whisper, local e gratuito) e corrige os nomes de ferramenta que o Whisper erra. Use SEMPRE antes de planejar qualquer edição, legenda ou animação sincronizada com a fala — a edição inteira depende de uma transcrição conferida.
---

# Transcrever o vídeo

A pasta desta skill é `.claude/skills/transcrever-video/` (Claude) ou `.agents/skills/transcrever-video/` (ChatGPT/Codex). Chamada abaixo de `<skill>`.
Rode os `.py` com o Python do `.venv` da pasta, se existir (ver a skill `preparar-computador`).

## 1. Conferir a fonte (somente leitura)

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name -of json entrada/<video>
```

Sem stream de áudio → pare e avise o aluno.

## 2. Transcrever

```bash
python <skill>/transcrever.py entrada/<video> -o transcricao/flat.txt
```

- Gera `transcricao/flat.txt` (uma palavra por linha: `indice|inicio|fim|texto`, em segundos) e `transcricao/transcricao.md` (frases com `[m:ss]`).
- Padrão: modelo `medium`, GPU se houver. Sem GPU, avise que demora e prefira `--modelo small` para vídeo longo. Idioma: `--idioma pt` (padrão).
- A primeira execução baixa o modelo (centenas de MB a ~1,5 GB). Precisa de internet só essa vez.
- Cache em `transcricao/.cache/`: rodar de novo não re-transcreve. Trocou o vídeo ou quer outro modelo → o cache muda sozinho; `--force` refaz.
- Um vídeo por execução. Não jogue vários na mesma chamada.

## 3. Corrigir os termos (obrigatório)

O Whisper não conhece nome de ferramenta e escreve como ouviu ("Hype Frames", "Cloud Code").

```bash
python <skill>/corrigir_termos.py transcricao/            # só mostra o que trocaria
python <skill>/corrigir_termos.py transcricao/ --aplicar  # grava, depois do OK do aluno
```

- Mostre a lista ao aluno antes de `--aplicar`. Linhas com `?` são palpites: decida com ele, caso a caso.
- Corrige `transcricao.md` e `flat.txt` juntos (no `flat`, a palavra corrigida mantém o tempo das originais).
- Termo novo errado → acrescente em `docs/glossario.md` (tabela) e rode de novo. Palavra que também é comum ("remoção", "cloud") vai como `aviso`, nunca como `troca`.

## 4. Ler e conferir

Leia `transcricao.md` inteiro. Procure nomes próprios, números, siglas e frases sem sentido. Na dúvida, ouça o trecho:

```bash
ffmpeg -ss <inicio> -t 6 -i entrada/<video> -vn transcricao/trecho.wav
```

Não "melhore" a fala do aluno: a transcrição registra o que foi dito. Só corrija o que o Whisper ouviu errado.

## 5. Próximo passo

Cortes (erros marcados, pausas) → skill `cortar-video`. Motion e legendas → skill do motor, usando o `flat.txt`.

## O que a edição usa daqui

| Arquivo | Para quê |
|---|---|
| `flat.txt` | entrada de texto na palavra certa, legendas, cortes |
| `transcricao.md` | ler o vídeo, planejar cenas pelo significado |

## Armadilhas

| Sintoma | O que é |
|---|---|
| `faster-whisper nao instalado` | pacote fora do Python usado: rode com o do `.venv` |
| `cublas64_12.dll` | GPU sem as DLLs: `--device cpu` ou instalar os pacotes da `preparar-computador` |
| tempos deslocados numa frase | timestamp de palavra derrapou: rode com `--modelo large-v3` só se o corte depender disso |
| transcrição vazia | vídeo sem áudio ou áudio mudo: confira o passo 1 |
