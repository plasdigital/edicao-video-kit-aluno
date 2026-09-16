# Agente de edição

Esta pasta orienta edição local com HyperFrames e motion em HTML/CSS/JavaScript.

Antes de criar uma edição, leia `docs/preferencias.md`. Ele registra gostos do dono desta pasta e vídeos de referência. Se estiver vazio, preencha com o aluno a partir de referências e da primeira prévia. Atualize depois de cada feedback com exemplo, trecho e motivo. Preferências são revisáveis.

Para transições e desenho de som, siga docs/transicoes-e-som.md: planejar eventos na timeline final, usar sons apenas onde acrescentam, variar timbres quando útil, misturar sem duplicação e verificar inteligibilidade. Entregar mapa de eventos e fontes dos efeitos com o projeto. NumPy é dependência opcional apenas para síntese em Python; checar com `python -c "import numpy; print(numpy.__version__)"`. O pacote wave faz parte do Python.

## Possibilidades

| Pedido | Ação |
|---|---|
| Checar ambiente (somente leitura) | `node --version`, `npm --version`, `ffmpeg -version`, `ffprobe -version` |
| Inspecionar vídeo (somente leitura) | `ffprobe -v error -show_streams -show_format -of json entrada/arquivo.mov` |
| Preparar ambiente (instalação local) | Seguir COMECE-AQUI.md e quickstart oficial; preservar instalações existentes |
| Instalar skills (altera projeto) | `npx hyperframes skills update`, conferindo destino e documentação atual |
| Editar e renderizar (cria arquivos) | Usar skills oficiais instaladas, criar projeto/, prévias e exportacoes/ |
| Transcrever (cria cache local) | Preferir faster-whisper local; instalar Python e pacote apenas se necessário |
| Publicar ou usar geração paga | Exigir autorização que cubra destino ou custo; não faz parte do fluxo básico |

## Configuração

Node/npm para motor e skills; mídia legível para editar; FFmpeg/ffprobe para inspeção e acabamento; Python/faster-whisper somente se precisar produzir transcrição local. A transcrição fornecida pode ser usada após conferir alinhamento. Para testar o pacote local: `python -c "import faster_whisper; print(faster_whisper.__version__)"`. CPU é caminho válido; GPU/CUDA são opcionais e dependem do ambiente.

Consulte https://hyperframes.heygen.com/quickstart. Não invente flags de inicialização/render: confira a versão instalada e a ajuda. Registre versões do motor, skills e dependências em VERSOES.md; preserve lockfile. Faça um MP4 sintético de 3 segundos antes do vídeo completo.

## Execução

Leia docs/prompts.md e docs/preferencias.md. Examine os arquivos em `referencias/` e registre o que aproveitar de cada um antes do storyboard. Analise a fala, duração, orientação, rotação, taxa de quadros, espaço de cor e áudio. Planeje cenas pelo significado. Preserve fonte imutável; não re-transcreva fonte inalterada. Não avance áudio em 0,6 s por padrão: diagnostique sincronização. Não corte palavras ou pausas demonstrativas. Use só dados fornecidos em gráficos; marque dados fictícios como ilustrativos.

Use HTML, CSS, SVG e JavaScript para motion; HyperFrames controla a renderização. Não use Remotion simultaneamente por padrão. Siga o contrato de timeline da versão instalada. Escolha fontes legíveis e cores do aluno. Recursos realistas são opcionais conforme docs/recursos-extras.md.

Revise frames-chave e o vídeo com som; confira duração dos streams de áudio e vídeo, timestamps, último frame/frase, fonte carregada e ausência de mídia faltando. Na concatenação, normalize codecs, dimensões, fps, timescale e espaço de cor; não faça concat com stream copy presumindo compatibilidade. Relate o que foi verificado e o que não foi.

## Travas e armadilhas

Não publicar/enviar/apagar originais sem prévia e autorização correspondente. Não consumir serviços pagos sem autorização. Preservar alterações do aluno. Sem uploads da gravação para serviços externos por conveniência.

Comando não reconhecido: verificar PATH e reabrir terminal. Skill não disponível: verificar escopo e atualizar contexto do agente. CUDA falhou: usar CPU, não exigir placa NVIDIA. Export curto ou dessincronizado: comparar streams, cortes e timestamps. Render lento: reduzir resolução da prévia; não prometer tempo fixo. “HTML pronto” não significa “vídeo conferido”.

Porquês e pré-requisitos: docs/ferramentas.md. Direção criativa: docs/prompts.md e docs/preferencias.md. Materiais opcionais: docs/recursos-extras.md.
