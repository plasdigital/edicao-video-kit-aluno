# Ferramentas e pré-requisitos

Tronco: computador → agente local → Node/npm + HyperFrames e skills → mídia → prévia → MP4.
Ramo de transcrição (skill `transcrever-video`, incluída): áudio → Python + faster-whisper → termos corrigidos → tempos revisados.
Ramo opcional: imagens/vídeos externos → licença e fundo verificados → composição.

| Item | Quando precisa | Se faltar | Pode começar sem? |
|---|---|---|---|
| Computador e pasta gravável (óbvio) | Sempre neste fluxo local | Não salva projeto/export | Não |
| Internet | Instalações, downloads e agente online | Não baixa componentes nem acessa agente online | Só com ambiente já preparado e agente disponível |
| Agente: Claude Code ou ChatGPT (Codex) | Para executar por conversa | Sem edição comandada por IA | Pode editar manualmente, fora da aula |
| Node.js/npm | HyperFrames e instalador de skills | Comandos não executam | Não para renderizar neste fluxo |
| HyperFrames e navegador de renderização | Composição e MP4 | Não renderiza | Pode preparar mídia antes |
| Skills do kit (preparar, transcrever, conferir) | Sempre; já vêm na pasta | Agente improvisa cada etapa | Vêm prontas |
| Skills oficiais do motor | Fluxo guiado da aula | Agente sem instruções específicas | Tecnicamente sim; a skill `preparar-computador` instala |
| FFmpeg/ffprobe | Cortes, áudio e verificação do fluxo | Faltam inspeção/acabamento | Pode planejar antes |
| Gravação | Editar sua fala | Só exemplo sintético | Sim, para testar instalação |
| Transcrição com tempos | Legendas e sincronização com fala | Menor precisão ao localizar falas | Sim, para motion sem fala |
| Python + faster-whisper | Produzir transcrição local quando não fornecida | Não roda esse transcritor | Sim, se já tiver transcrição adequada |
| GPU | Opcional para acelerar tarefas compatíveis | CPU pode ser lenta | Sim |
| Prints/logos | Só cenas que dependem deles | Cena fica sem material real | Sim, com outra composição |
| Geração de imagem/vídeo paga | Só se escolhida pelo aluno | Sem aquele material | Sim, não integra a base |

HyperFrames usa HTML/CSS/JavaScript e renderiza localmente. Skills são instruções para o agente; não são o renderizador. Renderização local não usa créditos HeyGen; o agente e serviços opcionais podem ter custos próprios. Fonte: https://hyperframes.heygen.com/quickstart e https://github.com/heygen-com/hyperframes (Apache 2.0).

Remotion é alternativa baseada em React; não é requisito de HyperFrames. Instalação de suas skills: `npx skills add remotion-dev/skills`. A licença da ferramenta é gratuita para indivíduos/empresas até 3 pessoas, sujeita aos termos; organizações maiores devem conferir a licença. Fontes: https://www.remotion.dev/docs/ai/skills e https://www.remotion.dev/ . Verifique novamente antes de distribuir a aula.

Transcrição local: https://github.com/SYSTRAN/faster-whisper . O modelo é baixado na primeira utilização; depois, pode trabalhar localmente. Use CPU como base portátil e GPU apenas quando configurada. A transcrição não exige YouTube.

As skills do kit ficam em `.claude/skills/` (Claude) e `.agents/skills/` (ChatGPT/Codex). Não distribuímos node_modules, executáveis, cache de modelos nem cópias locais das skills oficiais do HyperFrames e do Remotion — elas se atualizam pela origem. A instalação guiada evita arquivos específicos de outro sistema e mantém origem/licenças visíveis. Registre as versões efetivamente usadas para reproduzir o exemplo.
