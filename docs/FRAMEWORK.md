# Componentes do framework e adaptações

O projeto contém uma **reimplementação parcial e adaptada** da arquitetura didática de *Developing Graphics Frameworks with Python and OpenGL*, de Lee Stemkoski e Michael Pascale, referência exigida no enunciado. Os componentes usados estão incluídos em `framework/`. Não há dependência de download do framework durante a execução.

A arquitetura separa objeto transformável, cena, câmera, malha, geometria, material e renderizador. A implementação local concentra classes pequenas em módulos e explicita os três atributos de vértice. Não pretende reproduzir integralmente o livro nem manter compatibilidade de API com todos os seus exemplos.

| Conteúdo | Componente local | Aplicação |
|---|---|---|
| Cap. 1: pipeline e conceitos | Fluxo em `main.py` e `Renderer.render` | CPU calcula poses; GPU transforma, rasteriza, ilumina e testa profundidade. |
| Cap. 2: Pygame, OpenGL, atributos, uniforms | `main.py`, `Program`, `Renderer.geometry` | Janela/eventos, compilação GLSL, buffers e ligação dos dados. |
| Cap. 3: matrizes | `framework/matrix.py`, `Object3D.local_matrix` | Translação, rotações, escala e projeções. |
| Cap. 4: grafo de cena e primitivas | `Object3D`, `Scene`, `Mesh`, `Camera`, `Material`, `Geometry` | Composição de corpos, rotores e ambiente; herança de transformações. |
| Cap. 5: texturas | `Renderer.texture`, UVs, `HUD` | Imagens do piso/helipontos, painel RGBA e faixas procedurais. |
| Cap. 6: luz e sombra | `Shadow`, `lit.frag`, `depth.vert/.frag` | Normais, luz direcional, reflexão e shadow mapping em dois passes. |

## Decisões da adaptação

1. **Transformações declarativas:** cada nó possui posição, rotação Euler e escala, reconstruindo a matriz local a cada consulta. Isso evita acumular erro de multiplicações durante os ciclos de animação.
2. **Atributos intercalados:** posição, normal e UV compartilham um VBO com passo de 32 bytes, em vez de uma abstração independente para cada atributo.
3. **Uniforms:** a classe `Program` envia matrizes, vetores, inteiros e escalares e guarda as localizações; não há uma classe separada `Uniform`.
4. **Geometrias compartilhadas:** caixas, esferas e cilindros são armazenados em cache. A mesma primitiva pode gerar vários objetos com escalas diferentes; o renderizador reutiliza VAO/VBO.
5. **Materiais:** uma estrutura imutável reúne cor, imagem, repetição UV, brilho especular, emissão e opção procedural. As aeronaves e o piso usam o mesmo programa de iluminação com valores distintos.
6. **Textura de profundidade:** o primeiro passe usa `GL_DEPTH_COMPONENT24` em um FBO sem buffer de cor. O segundo compara a profundidade do fragmento na câmera da luz com a profundidade armazenada. É a abordagem de shadow mapping solicitada na seção 6.9; não se usam silhuetas achatadas ou manchas desenhadas no chão.
7. **Aprimoramentos da sombra:** bias dependente da inclinação e PCF 3×3 ajudam a reduzir autossombra e bordas serrilhadas. São escolhas locais, não uma afirmação de transcrição exata dos exemplos do livro.
8. **Câmera:** controle orbital com deslocamento do alvo substitui um rig em primeira pessoa. Satisfaz o controle de orientação/posição por teclado.
9. **Animação:** a aplicação possui uma linha do tempo compartilhada por etapas; essa lógica pertence à cena e fica fora do renderizador.
10. **Geometria paramétrica adicional:** `torus` produz os protetores de hélice do drone com posições, normais analíticas e UVs. Os triângulos têm orientação externa verificada pelos testes.
11. **Janela:** `framework/window.py` solicita MSAA 4×, com nova tentativa sem MSAA caso o driver rejeite o contexto. Isso suaviza contornos de geometria; PCF continua responsável pelas bordas das sombras.
12. **Câmera e painel:** acompanhamento exponencial da formação, órbita por arrasto e cliques na linha do tempo. A navegação preserva o estado de pausa e não depende do renderizador para calcular poses.

## Convenções

- Sistema destro, Y para cima; câmera olha no sentido −Z de suas coordenadas locais.
- Vetores-coluna; matriz mundo do filho = matriz mundo do pai × matriz local do filho.
- Matriz local = `T × Ry × Rx × Rz × S`; o ponto recebe escala primeiro.
- NumPy armazena as matrizes por linhas. `glUniformMatrix*fv(..., GL_TRUE, ...)` transpõe a representação para a convenção esperada pelo OpenGL desktop.
- Ângulos em radianos e tempo em segundos. O `deltaTime` da missão não é truncado para uma quantidade fixa por quadro.
- Escalas das malhas são não nulas; normais usam a inversa transposta da parte 3×3 da matriz mundo.

## Fontes

- [Livro, DOI 10.1201/9781003181378](https://doi.org/10.1201/9781003181378).
- [Repositório público three.py, dos autores](https://github.com/stemkoski/three.py), referência de organização de classes. Não foram copiados arquivos desse repositório.
- O apoio de IA, abrangendo a implementação local, está declarado no README.
