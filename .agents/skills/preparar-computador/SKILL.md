---
name: preparar-computador
description: Prepara o computador do aluno para editar vídeo com IA nesta pasta — confere e instala Node.js, FFmpeg, Python, faster-whisper e NumPy, instala as skills oficiais do HyperFrames (ou do Remotion) e faz um render de teste de 3 segundos. Use na primeira vez, quando um comando "não existe" ou quando o aluno pedir para atualizar as ferramentas.
---

# Preparar o computador

Objetivo: sair daqui com tudo verde no `checar.mjs` e um MP4 de teste de 3 segundos em `exportacoes/teste-3s.mp4`.

## 1. Conferir (somente leitura, pode rodar sem perguntar)

```bash
node --version          # se falhar, o Node não está instalado: vá direto ao passo 2
node <pasta desta skill>/checar.mjs
```

A pasta desta skill é `.claude/skills/preparar-computador/` (Claude) ou `.agents/skills/preparar-computador/` (ChatGPT/Codex).
O `checar.mjs` mostra o sistema, o que está instalado, o que falta e quais skills já estão na pasta.

## 2. Instalar só o que faltou

Instalar muda o computador: diga ao aluno o que vai instalar e por quê antes de rodar. Nunca instale uma segunda cópia do que já existe.

| Item | Windows | macOS | Linux (Debian/Ubuntu) | Fonte oficial |
|---|---|---|---|---|
| Node.js LTS | `winget install OpenJS.NodeJS.LTS` | `brew install node` | instalador do site | https://nodejs.org/en/download |
| FFmpeg + ffprobe | `winget install Gyan.FFmpeg` | `brew install ffmpeg` | `sudo apt install ffmpeg` | https://ffmpeg.org/download.html |
| Python 3.10+ | `winget install Python.Python.3.12` | `brew install python` | `sudo apt install python3 python3-venv` | https://www.python.org/downloads/ |

Depois de instalar, **feche e abra o terminal** (e a sessão do agente) para o PATH novo valer.

Pacotes Python num ambiente só desta pasta:

```bash
python -m venv .venv
# Windows: .venv\Scripts\python -m pip install faster-whisper numpy
# macOS/Linux: .venv/bin/python -m pip install faster-whisper numpy
```

A partir daí, rode os scripts Python das skills com esse Python (`.venv\Scripts\python` ou `.venv/bin/python`).

GPU (opcional, só placa NVIDIA): `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cuda-runtime-cu12 nvidia-cuda-nvrtc-cu12` no mesmo `.venv`. Sem placa, a transcrição roda na CPU — mais lenta, funciona.

## 3. Motor de vídeo — escolher UM por projeto

**HyperFrames (padrão desta aula).** Siga o quickstart atual: https://hyperframes.heygen.com/quickstart

```bash
npx hyperframes skills update     # instala/atualiza as skills oficiais nesta pasta
```

- As skills do HyperFrames **não vêm no kit de propósito**: elas mudam com frequência e sempre se instalam da origem oficial. Para atualizar depois, rode o mesmo comando.
- Confira onde elas foram parar: Claude lê `.claude/skills/`, ChatGPT/Codex lê `.agents/skills/`. Se só um dos dois recebeu, consulte `npx hyperframes skills --help` e a documentação — não copie pastas à mão de uma versão antiga.
- Crie o projeto em `projeto/` como o quickstart manda (a skill não baixa o motor de render sozinha).

**Remotion (alternativa, React).** Só se o aluno escolher:

```bash
npx skills add remotion-dev/skills
```

Documentação: https://www.remotion.dev/docs/ai/skills. Licença gratuita para pessoa física e empresas de até 3 pessoas — acima disso, conferir https://www.remotion.dev/license. Não misture Remotion e HyperFrames no mesmo projeto.

## 4. Teste de 3 segundos

Com a skill do motor, crie uma composição sintética de 3 s (texto animado sobre fundo liso) e renderize em `exportacoes/teste-3s.mp4`. Confira com:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 exportacoes/teste-3s.mp4
```

## 5. Registrar

Crie ou atualize `VERSOES.md` com: sistema, versões de Node, npm, FFmpeg, Python, faster-whisper, motor e skills, e o resultado do teste. **Reinicie a sessão do agente** para ele enxergar as skills novas.

## Armadilhas

| Sintoma | O que é |
|---|---|
| `'node' não é reconhecido` / `command not found` | instalou mas o terminal é antigo: reabra |
| Windows: `python` abre a Microsoft Store | é o atalho do Windows, não o Python: instale pelo `winget` ou python.org e desative o alias em *Configurações → Aplicativos → Aliases de execução* |
| `ffmpeg` funciona no terminal e não no agente | o agente abriu antes da instalação: reinicie a sessão |
| `cublas64_12.dll is not found` | faltam os pacotes `nvidia-*-cu12` do passo 2, ou use `--device cpu` |
| skill instalada e o agente "não conhece" | a sessão começou antes: reinicie; confira `.claude/skills` × `.agents/skills` |
| comando do motor não existe | versão diferente da documentação: rode `--help`, não invente flag |
