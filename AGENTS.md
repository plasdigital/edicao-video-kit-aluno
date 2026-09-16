# Agente de edição (ChatGPT/Codex e outros agentes)

Mesmo conteúdo do CLAUDE.md. As skills desta pasta estão em `.agents/skills/`.

Esta pasta edita a gravação do aluno com IA: transcrição local, motion em HTML/CSS/JavaScript renderizado pelo HyperFrames (ou Remotion), efeitos sonoros e conferência do MP4.

Antes de criar uma edição, leia `docs/preferencias.md`. Ele registra gostos do dono desta pasta e vídeos de referência. Se estiver vazio, preencha com o aluno a partir de referências e da primeira prévia. Atualize depois de cada feedback com exemplo, trecho e motivo. Preferências são revisáveis.

## Skills desta pasta

Ficam em `.claude/skills/` (Claude) e `.agents/skills/` (ChatGPT/Codex) — o mesmo conteúdo nos dois lugares.

| Skill | Quando |
|---|---|
| `preparar-computador` | primeira vez, comando "não existe", atualizar ferramentas |
| `transcrever-video` | **sempre antes de planejar a edição** |
| `cortar-video` | tirar erros marcados e pausas, aplicar cortes, juntar trechos, mixar som, nivelar volume (FFmpeg) |
| `conferir-video` | depois de todo render completo, antes de entregar |

As skills do motor **não vêm no kit**: HyperFrames (`npx hyperframes skills update`) e Remotion (`npx skills add remotion-dev/skills`) instalam-se da origem oficial, e é assim que se atualizam.

## O processo (sempre nesta ordem)

1. Ambiente pronto (`preparar-computador`).
2. Transcrição com tempo por palavra, termos corrigidos e lida por inteiro (`transcrever-video`).
3. Referências em `referencias/` examinadas e anotadas em `docs/preferencias.md`.
4. Cortes com FFmpeg, plano aprovado antes (`cortar-video`); vídeo cortado transcrito de novo.
5. Plano de cenas pelo significado da fala → prévia.
6. Feedback do aluno → ajuste → registro em `docs/preferencias.md`.
7. Som e volume (`cortar-video`, receitas) → export → `conferir-video` → entrega.

## Possibilidades

| Pedido | Ação |
|---|---|
| Checar ambiente (somente leitura) | `node .claude/skills/preparar-computador/checar.mjs` (ou `.agents/...`) |
| Inspecionar vídeo (somente leitura) | `ffprobe -v error -show_streams -show_format -of json entrada/arquivo.mov` |
| Preparar ambiente (instala) | skill `preparar-computador`; preservar instalações existentes |
| Transcrever (cria cache local) | skill `transcrever-video` → `transcricao/flat.txt` e `transcricao/transcricao.md` |
| Corrigir termos da transcrição (altera arquivo) | `corrigir_termos.py` sem `--aplicar`, mostrar, aplicar com OK |
| Achar erros marcados / medir pausas (somente leitura) | `achar-marcadores.py`, `silencios.py`, `movimento.py` da skill `cortar-video` |
| Cortar, juntar, mixar, nivelar (cria arquivos) | skill `cortar-video`; `--dry-run` aprovado antes |
| Editar e renderizar (cria arquivos) | skills oficiais do motor instalado; `projeto/`, prévias e `exportacoes/` |
| Efeitos sonoros (cria arquivos) | `docs/transicoes-e-som.md` |
| Conferir export (somente leitura) | skill `conferir-video` |
| Publicar ou usar geração paga | exigir autorização que cubra destino ou custo; não faz parte do fluxo básico |

## Configuração

| Precisa | Para | Checa |
|---|---|---|
| Node.js/npm | motor e instalador de skills | `node --version` |
| FFmpeg/ffprobe | inspeção, áudio, cortes, conferência | `ffmpeg -version` |
| Python + faster-whisper (no `.venv`) | transcrição | `python -c "import faster_whisper; print(faster_whisper.__version__)"` |
| NumPy | síntese de efeitos sonoros | `python -c "import numpy; print(numpy.__version__)"` |
| GPU NVIDIA | opcional; acelera a transcrição | `nvidia-smi` |

Documentação do motor: https://hyperframes.heygen.com/quickstart · https://www.remotion.dev/docs/ai/skills. Não invente flags: confira a versão instalada e `--help`. Registre versões em `VERSOES.md`; preserve lockfile. Faça um MP4 sintético de 3 segundos antes do vídeo completo.

## Execução

Examine os arquivos em `referencias/` e registre o que aproveitar de cada um antes do storyboard. Analise fala, duração, orientação, rotação, taxa de quadros, espaço de cor e áudio. Planeje cenas pelo significado, usando os tempos do `flat.txt`. Preserve fonte imutável; não re-transcreva fonte inalterada. Não avance áudio em 0,6 s por padrão: diagnostique sincronização. Não corte palavras nem pausas demonstrativas. Use só dados fornecidos em gráficos; marque dados fictícios como ilustrativos.

Um motor por projeto: HyperFrames é o padrão; Remotion só se o aluno escolher. Siga o contrato de timeline da versão instalada. Escolha fontes legíveis e cores do aluno. Recursos realistas são opcionais conforme `docs/recursos-extras.md`.

Na concatenação, normalize codecs, dimensões, fps, timescale e espaço de cor; não faça concat com stream copy presumindo compatibilidade. Relate o que foi verificado e o que não foi.

## Travas

- Não publicar, enviar ou apagar originais sem prévia e autorização correspondente.
- Não consumir serviços pagos sem autorização. Não subir a gravação para serviço externo por conveniência — a transcrição é local.
- Não aplicar correção de termos sem mostrar a lista ao aluno.
- Preservar alterações do aluno e versões aprovadas; ajuste pontual gera cópia nova.

## Armadilhas

| Sintoma | Significa |
|---|---|
| comando não reconhecido | PATH antigo: reabrir terminal e sessão do agente |
| skill "não existe" | sessão aberta antes da instalação, ou instalada só em `.claude/` ou só em `.agents/` |
| `cublas64_12.dll` | GPU sem DLLs: `--device cpu` ou pacotes da `preparar-computador` |
| transcrição lenta | CPU com modelo `medium`: usar `--modelo small` |
| legenda fora de tempo após corte | usou a transcrição do original: transcrever o cortado |
| export curto ou dessincronizado | comparar streams, cortes e timestamps (`conferir-video`) |
| render lento / computador travando | perfil MODESTO: modo leve de `docs/computador.md`; se não bastar, ofereça a VPS (mesmo documento, mínimo KVM 4, link com cupom `PEDROALMEIDA`: https://www.hostg.xyz/aff_c?offer_id=6&aff_id=214984&url_id=5038); não prometer tempo fixo |
| "HTML pronto" | não significa "vídeo conferido" |

Computador modesto: `docs/computador.md`. Porquês e pré-requisitos: `docs/ferramentas.md`. Direção criativa: `docs/prompts.md` e `docs/preferencias.md`. Termos da transcrição: `docs/glossario.md`. Materiais opcionais: `docs/recursos-extras.md`.
