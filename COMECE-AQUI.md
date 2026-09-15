# Comece aqui

1. Baixe e extraia a pasta em um local em que você possa criar arquivos (óbvio). Não trabalhe dentro do ZIP.
2. Abra a pasta no aplicativo do seu agente de IA, com acesso local a arquivos e terminal. Use sua própria conta e confira os limites do seu plano. A aula usa Astra; o procedimento não depende de uma conta do professor.
3. Envie o prompt de preparação abaixo. O agente deve conferir o sistema operacional e o que já existe antes de instalar.

> Leia AGENTS.md e CLAUDE.md. Prepare esta pasta para edição local com HyperFrames, HTML, CSS e JavaScript. Confira Node.js, npm, FFmpeg e ffprobe; instale somente o que faltar por fontes oficiais, respeitando as permissões do sistema. Instale as skills oficiais de HyperFrames no escopo deste projeto. Siga a documentação oficial atual, crie o projeto em projeto/ e faça uma renderização sintética de 3 segundos. Registre versões, comandos e resultado em VERSOES.md. Não use serviços pagos de geração, não publique nada e não altere outros projetos.

4. Se Node.js estiver ausente e o agente não conseguir instalá-lo, use o instalador LTS de https://nodejs.org/en/download e reabra o terminal. FFmpeg e ffprobe: siga os links para seu sistema em https://ffmpeg.org/download.html. No Windows, extraia ambos e inclua a pasta bin no PATH; reabra o terminal. Evite instalar uma segunda cópia se já houver uma compatível.
5. A instalação das skills segue https://hyperframes.heygen.com/quickstart. O comando documentado é `npx hyperframes skills update`; confira o destino informado pelo instalador. Instalar a skill não substitui criar o projeto e baixar o motor de renderização. O agente deve seguir o quickstart para concluir essa parte.
6. Crie `entrada/` para o vídeo original e `referencias/` para prints, logos e exemplos. Informe suas cores e quais imagens podem aparecer. Não é necessário Git, YouTube, conta HeyGen ou servidor para a renderização local básica.
7. Envie o prompt de edição de [docs/prompts.md](docs/prompts.md). O agente analisa o arquivo, obtém uma transcrição com tempos quando necessária e cria uma prévia.
8. Assista à prévia com áudio. Peça um ajuste concreto, por exemplo: “No trecho sobre automação, aumente o texto e coloque minha câmera na lateral com borda laranja”.
9. Receba `exportacoes/final.mp4`, projeto editável e relatório de verificação. Confira a frase final, a sincronização e os textos antes de usar.

Se um comando não existir na versão instalada, envie o erro ao agente. Ele deve consultar `--help` e a documentação, sem improvisar comandos antigos. Uma prévia no navegador não comprova que o MP4 está correto.
