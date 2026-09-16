# Meu computador aguenta?

Aguenta, mas o tempo muda muito. Três etapas pesam; o resto (cortes, mixagem, conferência) é leve.

| Etapa | O que usa | Computador forte | Computador modesto |
|---|---|---|---|
| Transcrição | processador ou placa NVIDIA | minutos | pode passar do tempo do vídeo com o modelo `medium` |
| Render do motion (HyperFrames/Remotion) | navegador capturando quadro a quadro: processador e **memória** | minutos para uma abertura | pode levar dezenas de minutos para a mesma abertura |
| Export final (re-encode) | processador | mais rápido que o vídeo | perto do tempo do vídeo |

## Números de referência

Medidos num notebook com Ryzen 5 7535HS (12 threads), 16 GB e placa NVIDIA RTX 3050 — um computador acima da média. Incluem o carregamento do modelo.

| Tarefa | Tempo |
|---|---|
| Transcrever 40 s de fala, modelo `small`, só processador | 12 s |
| Transcrever 40 s de fala, modelo `medium`, só processador | 34 s (quase o tempo do vídeo) |
| Transcrever 40 s de fala, modelo `medium`, placa NVIDIA | 9 s |
| Renderizar abertura de 40 s com motion, 1080p a 60 quadros (HyperFrames) | 4 min 15 s (~6× o tempo do vídeo) |

Num computador com metade disso (4 núcleos, 8 GB, sem placa NVIDIA), espere algo como **duas a três vezes mais**. É uma estimativa: o `checar.mjs` e o teste de 3 segundos mostram o seu caso.

## Modo leve

1. **Transcrição com `--modelo small`.** Serve para ler e para cortar. Suba para `medium` só se os tempos das palavras derraparem num corte importante.
2. **Motion só onde vale: a abertura.** Um vídeo de 10 minutos inteiro animado vira horas de render. Anime os primeiros 30–60 segundos e deixe o resto como gravação com cortes.
3. **Prévia pequena.** Peça as prévias em 720p e 30 quadros; 1080p só no render final. No corte, use `--preview`.
4. **60 quadros só se a gravação for 60.** 30 quadros renderiza cerca de metade do trabalho.
5. **Feche o navegador e outros programas** antes de renderizar. Memória cheia é o que faz o render travar ou falhar no meio.
6. **Render final longo: deixe rodando** com o computador na tomada e sem suspender.
7. **Um vídeo por vez.** Não transcreva e renderize ao mesmo tempo.

## O que não é problema

- Não ter placa NVIDIA: tudo funciona pelo processador, só mais devagar.
- Placa AMD/Intel ou Mac: a transcrição usa o processador; no Mac com chip Apple ela é boa.
- Pouco espaço: cada render temporário ocupa alguns GB. Deixe uns 10 GB livres.

## Alternativa: rodar numa VPS

Se o modo leve não bastar, dá para fazer tudo num servidor alugado e usar o seu computador só para mandar o vídeo e assistir o resultado. Indicamos a Hostinger — com o cupom **`PEDROALMEIDA`** (10% OFF): **https://www.hostg.xyz/aff_c?offer_id=6&aff_id=214984&url_id=5038**

### Qual plano

Nenhuma VPS da Hostinger tem placa de vídeo: a transcrição sempre roda no processador (use `--modelo small`).

| Plano | vCPU | Memória | Para edição de vídeo |
|---|---|---|---|
| KVM 1 | 1 | 4 GB | não serve para render |
| KVM 2 | 2 | 8 GB | só cortes e transcrição; render de motion lento e com risco de travar |
| **KVM 4** | 4 | 16 GB | **o mínimo recomendado** para render de motion |
| **KVM 8** | 8 | 32 GB | perto de um bom computador (sem placa de vídeo) |

O preço muda com promoção e período; confira no link. Na renovação ele sobe.

### Antes de contratar, pese

- **É mensal, não por hora.** Não dá para ligar só na hora do render e pagar só aquilo.
- **Vai e vem de arquivo.** A gravação sobe pela sua internet (upload costuma ser lento) e cada versão desce para você assistir. Ajuste pequeno = mais uma rodada.
- **O agente roda lá dentro,** pelo terminal do servidor. Se você nunca usou uma VPS, comece pelo kit de VPS: https://github.com/plasdigital/vps-kit-aluno
- **Sua gravação fica num servidor na internet.** Não abra porta para ver a prévia; apague os brutos quando terminar.

### Como fica o fluxo

1. Contrate o plano com **Ubuntu** e entre por SSH: `ssh root@<IP da VPS>` (o kit de VPS ensina a criar a chave e um usuário sem ser root).
2. Instale o agente no servidor: **Claude Code** (`curl -fsSL https://claude.ai/install.sh | bash`) ou **Codex** (`npm install -g @openai/codex`, depois de ter o Node). No primeiro uso ele mostra um link para você entrar na sua conta pelo navegador do seu computador.
3. Baixe o kit: `git clone https://github.com/plasdigital/edicao-video-kit-aluno.git` e abra o agente dentro da pasta.
4. Peça a skill `preparar-computador` — no Linux ela usa `apt` para FFmpeg e Python e segue o quickstart do motor, que lista o que o navegador de render precisa no servidor.
5. Envie a gravação **do seu computador** para o servidor:

   ```bash
   scp entrada/video.mp4 root@<IP da VPS>:~/edicao-video-kit-aluno/entrada/
   ```

6. Siga o fluxo normal (transcrever → cortar → editar → conferir) conversando com o agente no servidor.
7. Traga o resultado **para o seu computador** e assista:

   ```bash
   scp root@<IP da VPS>:~/edicao-video-kit-aluno/exportacoes/final.mp4 .
   ```

   Prévia no navegador: use um túnel em vez de abrir porta — `ssh -L <porta>:localhost:<porta> root@<IP da VPS>` com a porta que o comando de prévia mostrar, e abra `http://localhost:<porta>` no seu computador.
