# Guia técnico para explicar a implementação

## 1. Do tempo ao pixel

`main.py` recebe eventos e mede segundos com `time.perf_counter`. `Mission.advance(dt)` atualiza o relógio somente quando a missão está ativa. `sample(time)` encontra a etapa e interpola as posições. `apply_mission` aplica as poses aos nós das aeronaves e define a rotação dos rotores.

O renderizador percorre a hierarquia, obtém matrizes mundo e desenha as mesmas malhas duas vezes: primeiro na câmera da luz, depois na câmera do observador. Ao final, desenha a textura do painel sem teste de profundidade, com mistura alfa.

## 2. Modelagem e hierarquia

`box`, `sphere` e `cylinder` retornam primitivas de dimensão unitária com posição, normal e UV. O cilindro aceita raio superior menor para produzir a cauda afunilada. A esfera escalada forma a fuselagem e a cabine; caixas formam pás, patins e estabilizadores.

```text
Scene
├── Helicopter (posição e orientação da aeronave)
│   ├── fuselagem, cabine, cauda, estabilizadores e patins
│   ├── rotor_principal (rotação local Y)
│   │   ├── pás
│   │   └── pontas amarelas e cubo
│   └── rotor_cauda (rotação local X)
├── Drone (posição e orientação da aeronave)
│   ├── corpo, braços, motores e patins
│   ├── quatro nós de hélice (rotação local Y)
│   └── gimbal e lente
└── piso, helipontos, hangar e torre
```

Uma pá gira ao redor do centro do nó de rotor, não ao redor da origem global. Ao mover o helicóptero, todas as suas partes recebem a transformação do pai. Escalar uma esfera por fatores diferentes produz um elipsoide, exigindo correção apropriada das normais.

## 3. Transformações e projeção

Para um ponto local `p`, a posição de recorte é:

```text
p_mundo = M_pai × T × Ry × Rx × Rz × S × p
p_clip  = P_câmera × V_câmera × p_mundo
```

A GPU divide `p_clip.xyz` por `p_clip.w` para obter coordenadas normalizadas e depois mapeia para o viewport. A câmera principal usa perspectiva de 48°, plano próximo 0,1 e distante 100; objetos distantes aparentam ser menores.

A câmera da luz usa projeção ortográfica porque os raios da luz direcional são paralelos. O volume de sombra cobre a base e os percursos, sem acompanhar a câmera do observador.

## 4. Atributos de vértice

Cada vértice ocupa oito floats de 32 bits (32 bytes). `Renderer.geometry` configura um VAO e um VBO compartilhados por primitiva.

| Nome GLSL | Localização | Tipo | Offset | Finalidade |
|---|---|---|---|---|
| `vertexPosition` | 0 | `vec3` | 0 bytes | Posição no sistema local da primitiva. |
| `vertexNormal` | 1 | `vec3` | 12 bytes | Direção perpendicular à superfície para iluminação. |
| `vertexUV` | 2 | `vec2` | 24 bytes | Coordenadas da imagem aplicada ao triângulo. |

As caixas repetem vértices entre faces para que cada face tenha uma normal constante e UVs próprios. Esferas têm normais radiais. Cilindros possuem normais laterais e normais distintas nas tampas. A costura do mapeamento da esfera repete a posição com `u=0` e `u=1`.

## 5. Shaders e uniforms utilizados

### Programa de iluminação: `lit.vert` + `lit.frag`

O vertex shader produz posição e normal em espaço mundo, UV e posição na câmera da luz. Esses valores são interpolados pelo rasterizador. O fragment shader consulta a imagem, calcula reflexão e testa a visibilidade da luz.

| Uniform | Tipo | Enviado por / função |
|---|---|---|
| `modelMatrix` | `mat4` | Matriz mundo da malha; muda por objeto. |
| `viewMatrix` | `mat4` | `Camera.view_matrix`; transforma mundo para câmera. |
| `projectionMatrix` | `mat4` | Perspectiva ajustada à proporção da janela. |
| `lightMatrix` | `mat4` | Produto projeção ortográfica × visão da luz. |
| `normalMatrix` | `mat3` | Inversa transposta da parte linear da matriz mundo. |
| `baseColor` | `vec3` | Cor do material. |
| `lightDirection` | `vec3` | Direção de propagação dos raios; o shader usa seu oposto. |
| `cameraPosition` | `vec3` | Posição do observador para reflexão especular e névoa de distância. |
| `colorTexture` | `sampler2D` | Imagem RGBA na unidade de textura 0. |
| `shadowMap` | `sampler2D` | Profundidade da luz na unidade 1. |
| `useTexture` | `bool` | Material possui uma imagem? |
| `shadowsEnabled` | `bool` | Permite comparar imagem com/sem sombra usando P. |
| `proceduralEnabled` | `bool` | Ativa faixas calculadas por UV nas molduras do hangar. |
| `uvRepeat` | `vec2` | Repetição da textura (8×8 no piso). |
| `specularStrength` | `float` | Intensidade do brilho especular. |
| `shininess` | `float` | Expoente do brilho especular. |
| `emission` | `float` | Mistura com cor sem iluminação nos sinais e luzes decorativas. |

As cores de referência do ambiente e da luz são constantes do fragment shader, não uniforms. A luz ambiente mistura uma cor de chão e uma cor de céu conforme `N.y`, valorizando a orientação das superfícies. Um termo de brilho rasante baseado em `pow(1-dot(N,V),3)` reforça contornos nos materiais especulares; é uma aproximação artística, não reflexão de objetos da cena. Os sinais emissivos não iluminam outros objetos: são apenas superfícies cuja cor permanece visível.

### Programa de profundidade: `depth.vert` + `depth.frag`

O vertex shader usa apenas `vertexPosition`, `modelMatrix` e `lightMatrix`. Calcula `lightMatrix × modelMatrix × vec4(position,1)`. O fragment shader não escreve cor: o rasterizador grava a profundidade no attachment do FBO após o teste de profundidade.

### Programa de painel: `overlay.vert` + `overlay.frag`

Não há atributos de vértice no VBO: `gl_VertexID` gera um triângulo que cobre a tela. O único uniform é `overlayTexture`, `sampler2D` da unidade 0. O texto e os cartões desenhados pelo Pygame são enviados como imagem RGBA; o shader a amostra usando UVs.

## 6. Normais e iluminação

Normais não são posições: não recebem translação. Quando há escala não uniforme, multiplicá-las diretamente pela matriz mundo pode deixá-las não perpendiculares à superfície. Por isso:

```text
N = normalize(transpose(inverse(mat3(M_mundo))) × normal_local)
L = normalize(-lightDirection)
V = normalize(cameraPosition - worldPosition)
H = normalize(L + V)
difusa   = max(dot(N,L), 0)
especular = specularStrength × max(dot(N,H),0)^shininess
```

A reflexão especular só é aplicada quando a superfície está voltada para a luz. A contribuição ambiente permanece mesmo em sombra. O resultado usa um modelo ambiente + Lambert + Blinn–Phong simplificado, suficiente para identificar volumes, curvatura e brilho.

**Sombreamento** é a variação de cor/brilho de uma superfície conforme normal, material, luz e observador. **Sombra projetada** é a redução da luz recebida porque outro objeto obstrui o caminho até a fonte. Ao apertar P, a sombra no chão desaparece, mas o sombreamento das fuselagens permanece.

## 7. Shadow mapping — requisito da seção 6.9

1. `Shadow` cria textura `GL_DEPTH_COMPONENT24`, FBO, matriz da luz e verifica se o framebuffer está completo.
2. O renderizador muda o viewport para a resolução do mapa e limpa a profundidade.
3. As malhas com `cast_shadow=True` são desenhadas do ponto de vista da luz. O depth test mantém a superfície mais próxima em cada texel.
4. O renderizador retorna ao framebuffer da janela, restaura o viewport e usa a câmera em perspectiva.
5. O fragmento é transformado para a câmera da luz, dividido por W e remapeado de `[-1,1]` para `[0,1]`.
6. Se a profundidade atual, descontado um pequeno bias, exceder a profundidade armazenada, há um bloqueador entre o ponto e a luz.
7. A visibilidade multiplica as parcelas difusa e especular; a parcela ambiente continua presente.

São feitas nove comparações em texels vizinhos (**PCF 3×3**). A média suaviza a borda. O bias reduz o padrão de autossombra chamado *shadow acne*. Um bias excessivo separaria visualmente a sombra do contato (*peter-panning*), por isso requer equilíbrio. Fora do volume da luz, o shader considera o fragmento iluminado.

O mapa é redesenhado a cada quadro ativo de renderização, inclusive com a animação pausada. Durante a pausa, as poses e o mapa permanecem iguais; mover a câmera altera apenas o ponto de observação. As hélices também pertencem ao passe de profundidade.

Limitações: uma única luz direcional, volume ortográfico fixo, sombras de resolução finita e materiais opacos. PCF não é uma simulação física de penumbra. O cenário não usa transparência real no vidro nem reflexões do ambiente.

## 8. Independência da taxa de quadros e coordenação

O relógio é atualizado por `tempo += dt * velocidade`. Cada etapa recebe progresso normalizado entre 0 e 1. Para evitar mudanças bruscas de velocidade nos extremos, a interpolação usa `s(t)=t²(3−2t)`.

As hélices recebem `ângulo = velocidade_angular × integral_da_potência`. `rotor_motion` usa uma rampa smoothstep na partida e na parada. A primitiva de `3u²−2u³` é `u³−u⁴/2`, permitindo calcular a fase diretamente, sem integração numérica por quadro. O helicóptero acelera em 0–2 s; o drone em 9–11 s, antes da decolagem; ambos desaceleram em 35–37 s. A fase inclui a contribuição dos ciclos anteriores para não haver saltos. Não se usa `ângulo += constante` por quadro. A imagem ainda pode apresentar aliasing temporal nas pás, mas as velocidades matemáticas permanecem independentes do FPS.

`flight_tilt` projeta a velocidade do percurso nos eixos locais da aeronave e calcula pequenas inclinações de arfagem e rolagem, limitadas a aproximadamente 9° e 10°. A derivada do smoothstep é zero nos limites das etapas; as aeronaves voltam suavemente à horizontal. Essa inclinação é ilustrativa, sem dinâmica física de sustentação.

Durante a inspeção, a posição do drone é calculada relativamente ao helicóptero em uma circunferência. Durante a escolta, `posição_drone = posição_helicóptero + (2,8; 0,35; 1,7)`. Isso garante uma relação espacial explícita. Um controlador comum ordena as etapas, em vez de duas animações independentes.

A conclusão de cada percurso programado coincide com o fim da sua etapa. Não se afirma que haja sensores reais, troca de mensagens de rede ou detecção de proximidade física.

## 9. Texturas e efeito adicional

`assets/textures/concrete.png` é ruído determinístico salvo como imagem; os helipontos e a placa são desenhos 2D salvos em PNG. Durante a aplicação, são imagens carregadas por `pygame.image.load` e enviadas para a GPU com mipmaps e repetição UV.

`solar.png` acrescenta o padrão de células fotovoltaicas do telhado. As imagens dos helipontos agora são aplicadas sobre cilindros finos, usando os UVs radiais das tampas; não há mais um quadrado de textura sobre o disco.

O recurso adicional de faixas diagonais é diferente: `step(0.48, fract((uv.x+uv.y)*12.0))` escolhe entre amarelo e escuro por fragmento, sem imagem de entrada. A tecla B permite isolá-lo. As imagens continuam visíveis mesmo quando esse efeito é desligado, preservando o requisito obrigatório de textura de imagem.

## 10. Interação e antisserrilhamento

O painel desenha em um espaço lógico mínimo de 960×640 e reduz a imagem quando necessário. A posição do clique é dividida pela mesma escala antes do teste dos retângulos. `Mission.seek` escolhe etapa/progresso preservando ciclo, velocidade e pausa. Um clique consumido pelo painel não começa a arrastar a câmera.

No acompanhamento, o alvo da câmera converge ao centro entre as aeronaves com `alpha = 1-exp(-4*dt)`. Para alvo fixo, a evolução é equivalente em diferentes taxas de quadros. W/A/S/D cancela o acompanhamento e devolve o controle manual. O relógio dessa câmera continua ativo durante a pausa da missão.

MSAA 4× suaviza arestas da geometria na janela. Se a criação do contexto falhar, a aplicação tenta novamente sem MSAA. `--msaa 0` permite comparar ou reduzir custo. O mapa de sombras permanece uma textura de profundidade sem multisampling, com filtragem PCF no fragment shader.
