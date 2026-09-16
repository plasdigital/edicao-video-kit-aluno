# Comece aqui

1. **Tenha um agente de IA instalado.** Serve qualquer um dos dois (ambos são pagos, confira o plano):
   - **Claude Code** — https://claude.com/pricing
   - **ChatGPT com Codex** — https://chatgpt.com/codex
2. **Baixe esta pasta** (botão *Code → Download ZIP* no GitHub) e extraia num lugar em que você possa criar arquivos. Não trabalhe dentro do ZIP.
3. **Abra a pasta no agente**, com acesso a arquivos e terminal, na sua própria conta.
4. **Prepare o computador.** Envie:

> Use a skill preparar-computador. Confira o que já existe, instale só o que faltar pelas fontes oficiais, instale as skills oficiais do HyperFrames nesta pasta, faça o render de teste de 3 segundos e registre tudo em VERSOES.md. Me diga antes o que vai instalar. Não use serviços pagos, não publique nada e não altere outros projetos.

   Depois, **feche e abra a sessão do agente** para ele enxergar as skills novas. Prefere Remotion? Troque "HyperFrames" por "Remotion" no pedido.
5. **Coloque o material.** Crie `entrada/` com o vídeo original e `referencias/` com prints, logos e exemplos. Coloque um ou dois vídeos que você gostou e, se houver, um que não gostou. Diga suas cores. Nada disso vai para o GitHub.
6. **Transcreva.** Envie:

> Use a skill transcrever-video no vídeo de entrada/. Depois me mostre as correções de termos antes de aplicar e me diga o que achou estranho na transcrição.

   A transcrição roda no seu computador; não precisa publicar no YouTube. Nome de ferramenta que o Whisper errar vai para [docs/glossario.md](docs/glossario.md).
7. **Corte (opcional).** Se você gravou falando “erro erro erro” quando errou, ou quer aparar pausas, peça: “Use a skill cortar-video, me mostre o plano de cortes antes de aplicar”.
8. **Registre suas referências** em [docs/preferencias.md](docs/preferencias.md) com o agente.
9. **Edite.** Envie o prompt de edição de [docs/prompts.md](docs/prompts.md). O agente cria uma prévia.
10. **Assista com áudio e ajuste.** Peça uma coisa concreta, por exemplo: “No trecho sobre automação, aumente o texto e coloque minha câmera na lateral com borda laranja”. Diga também o que ficou bom; o agente registra em `docs/preferencias.md` para as próximas edições.
11. **Receba** `exportacoes/final.mp4`, o projeto editável e o relatório da skill `conferir-video`. Assista inteiro antes de usar.

Se um comando não existir na versão instalada, envie o erro ao agente. Ele consulta `--help` e a documentação, sem improvisar comandos antigos. Uma prévia no navegador não comprova que o MP4 está correto.
