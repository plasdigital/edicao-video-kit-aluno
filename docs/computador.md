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
