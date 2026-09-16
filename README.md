# Edição de vídeo Kit Aluno

Transforme sua gravação em um vídeo com textos animados, gráficos, prints, mudanças de enquadramento e efeitos sonoros. Abra esta pasta no **Claude Code** ou no **ChatGPT (Codex)** e converse em português.

**O que vem na pasta**
- Quatro skills prontas, para os dois agentes (`.claude/skills/` e `.agents/skills/`): **preparar-computador**, **transcrever-video** (Whisper local, com correção de termos), **cortar-video** (cortes, pausas, mixagem e volume com FFmpeg) e **conferir-video**.
- O manual do agente (`CLAUDE.md` e `AGENTS.md`), os [prompts](docs/prompts.md), suas [preferências](docs/preferencias.md), o [glossário da transcrição](docs/glossario.md) e o guia de [transições e som](docs/transicoes-e-som.md).

**O que se instala na hora, da fonte oficial:** Node.js, FFmpeg, Python, faster-whisper e as skills do HyperFrames (caminho principal) ou do Remotion. Elas mudam com frequência; por isso não vêm copiadas aqui.

**Você precisa de:** computador (veja [o que pesa e o modo leve](docs/computador.md)), internet na configuração, um agente com acesso a arquivos e terminal (pago), sua gravação e espaço para renderizar.

Ordem de leitura: [COMECE-AQUI.md](COMECE-AQUI.md) → [ferramentas](docs/ferramentas.md) → [prompts](docs/prompts.md). Imagens realistas ou 3D: [recursos extras](docs/recursos-extras.md).
