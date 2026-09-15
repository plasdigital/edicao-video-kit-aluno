# Quando acrescentar imagens, vídeos ou 3D

O exemplo principal da aula usa motion em HTML. Isso inclui textos, interfaces, gráficos, máscaras e ilustrações SVG; pode ter acabamento profissional.

| Pedido | Caminho sugerido |
|---|---|
| Gráfico crescendo com valores corretos | SVG/canvas e animação por código; usar os dados reais |
| Borboleta desenhada batendo asas | Ilustração com asas separadas e animação por código |
| Borboleta realista voando | Vídeo próprio, banco licenciado ou geração de vídeo por IA |
| Objeto 3D com câmera e iluminação controláveis | Modelo e renderização 3D; pode usar Three.js ou ferramenta 3D |
| Cena com aparência 3D, sem necessidade de editar geometria | Imagem ou vídeo gerado por IA pode atender |

3D não exige IA. Um vídeo gerado com aparência 3D normalmente não entrega um modelo 3D editável. Uma imagem estática permite zoom e parallax, mas não cria automaticamente movimento natural de asas.

Para compor por cima da câmera: prefira transparência verdadeira; caso contrário, use remoção de fundo ou máscara. Um fundo quadriculado desenhado na imagem não é transparência. Confira bordas, oclusão, escala, direção da luz e direitos de uso. Para passar atrás do apresentador, é necessário recortá-lo ou segmentá-lo.

Peça ao agente: “Planeje um material visual para [CENA], com [ESTILO], duração [TEMPO] e fundo [TRANSPARENTE/OUTRO]. Diga quais arquivos preciso fornecer e se há custo antes de gerar. Depois integre à composição no trecho [FRASE]”.

Este ramo é opcional. A aula básica não precisa de assinatura extra de geração de imagem ou vídeo.
