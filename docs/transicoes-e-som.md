# Transições e efeitos sonoros

O som deve acompanhar uma mudança visual e manter a voz compreensível. Não é obrigatório usar música nem um banco pago de efeitos.

## Método usado na edição de referência

As transições foram construídas na composição visual. Os efeitos foram sintetizados localmente em Python com NumPy, gravados em WAV estéreo a 48 kHz e misturados à voz com FFmpeg. Não vieram de geração paga nem de um banco de sons.

- **Sopro de transição (whoosh):** aproximadamente 250 ms de ruído suavizado com uma janela de 12 amostras; envelope senoidal ao quadrado para entrar e sair sem corte brusco; tom grave descendente discreto. O início foi colocado 80 ms antes da troca visual para antecipar o movimento.
- **Toque de entrada (tick):** aproximadamente 140 ms de tom senoidal com ataque rápido e decaimento exponencial. Frequências variaram a partir de 620 Hz para diferenciar entradas de ícones e números.
- **Espaço:** pequenas diferenças de nível entre canais, sem jogar o efeito inteiramente para um lado.
- **Mixagem:** voz e efeitos em pistas separadas. A voz recebeu filtro passa-altas em 65 Hz e normalização com alvo de -16 LUFS e -2 dBTP; depois houve mistura e limitador. Esses valores descrevem a referência, não substituem medir a mixagem final ou ouvir cada gravação.

O código de referência compensava o corte inicial para posicionar os eventos na timeline exportada. Em outra edição, os efeitos devem seguir os tempos finais após os cortes; copiar os segundos da referência deixaria tudo fora de lugar.

## Como o agente deve repetir o processo

1. Finalize o plano de cortes e crie uma lista de eventos com tempo na timeline final, tipo de movimento, duração e intenção do som.
2. Escolha transições motivadas: deslocamento para mudar de cena, máscara para revelar material, aproximação para destacar uma informação. Use aceleração/desaceleração suaves. Reserve transições mais fortes para mudanças de ideia.
3. Comece sonorizando no máximo uma mudança de cena sim, outra não; entradas comuns de motion ficam em silêncio. Um clique pode acompanhar um cursor que realmente clica. Acrescente outros sons apenas se a audição do vídeo inteiro mostrar que fazem falta.
4. Escolha dois ou três timbres coerentes com ações diferentes, como whoosh curto, clique de cursor e impacto suave. Varie duração, textura e volume; não repita o mesmo “vup” em sequência. Dois ou três timbres são repertório, não meta de quantidade de efeitos.
5. Sintetize arquivos WAV locais com Python/NumPy e biblioteca wave ou use efeitos fornecidos com direito de uso. Instale NumPy em ambiente local do projeto se necessário. Não use caminhos do professor nem serviços externos pagos por padrão.
6. Posicione cada som conforme o evento visual. Preserve pequenas caudas e evite estalos. Eventos antes de zero devem ser recortados de forma segura, nunca deslocar toda a trilha de voz.
7. Faça a composição de áudio uma única vez: ou coloque os WAVs na timeline do motor ou misture uma trilha SFX com FFmpeg ao final. Não adicione a mesma trilha pelos dois caminhos.
8. Mantenha a voz à frente. Reduza efeitos nas sílabas importantes; use ducking quando necessário. Não copie amplitudes numéricas como garantia de volume: compare o nível dos arquivos e meça a saída.
9. Ouça em fones e alto-falantes, inclusive em mono. Confira inteligibilidade, sincronia, clipping, começo/fim e duração dos streams. O limitador não garante sozinho o true peak final depois da codificação.
10. Entregue mapa dos eventos, script de síntese quando usado, WAVs criados e instruções de render junto ao projeto editável. Não inclua a voz do aluno em um kit público.

## Prompt pronto

> Além do motion, faça um desenho de som contido. Comece com whoosh em uma mudança de cena sim, outra não; entradas comuns de motion ficam sem efeito. Use clique apenas onde houver ação de cursor e escolha até dois ou três timbres adequados às ações. Siga docs/transicoes-e-som.md. Gere os efeitos localmente quando possível, sem contratar serviços. Adapte os eventos aos tempos finais após os cortes, mantenha a voz clara e preserve pistas separadas. Ouça o vídeo inteiro para detectar repetição cansativa. Entregue também os arquivos e o mapa dos efeitos para que eu possa ajustar depois.

## Na aula

Mostre a mesma transição sem SFX e com SFX, usando o mesmo volume de voz. Depois mostre uma sequência de várias transições e como o whoosh em todas pode cansar. A decisão final é pela audição do conjunto, não pela quantidade de animações.
