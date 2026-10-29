# Validação da entrega

Validação realizada em **28/10/2026**. Ambiente: Linux, Python 3.14.8, NumPy 2.5.4, pygame-ce 2.5.8 (SDL 2.32.10) e PyOpenGL 3.1.10.

O contexto real utilizado foi **OpenGL 4.6 Core Profile, Mesa 26.2.4-arch1.1**, com renderização por software **llvmpipe (LLVM 23.1.1, 256 bits)**. Os shaders solicitam GLSL 330 e a aplicação solicita contexto OpenGL 3.3 core. Os resultados não constituem teste em todos os sistemas ou GPUs.

## Testes unitários: 27 aprovados

Comando:

```bash
python -m unittest discover -s tests -v
```

Cobertura dos testes:

- Poses equivalentes no mesmo instante a 24, 30, 60 e 144 FPS.
- Pausa, retomada, reinício, velocidade e passos temporais que atravessam ciclos.
- Drone aguardando a chegada do helicóptero; helicóptero aguardando a inspeção.
- Deslocamento relativo constante durante a escolta.
- Continuidade das posições e orientações nos limites das nove etapas e na repetição.
- Posições finitas e separação das origens dos modelos ao longo do ciclo.
- Herança de transformações, reparenting e rejeição de ciclos no grafo.
- Normais unitárias, UVs no intervalo esperado e orientação externa dos triângulos.
- Matriz normal preservando perpendicularidade sob escala não uniforme.
- Matrizes de câmera, planos de recorte e movimento da câmera independente da missão.
- Quatro rotores independentes e existência de todas as imagens necessárias.
- Integral da potência dos rotores e continuidade da fase durante partida, parada e repetição.
- Inclinação durante o deslocamento e retorno à horizontal nos limites das etapas.
- Acompanhamento da câmera equivalente em diferentes taxas de quadros; controle manual libera o acompanhamento.
- Cliques na linha do tempo em 1280×800, 960×640 e 480×480; botões de pausa e acompanhamento.
- Fallback de criação da janela quando o driver rejeita MSAA, verificado por simulação dessa falha.

O teste de separação mede distâncias entre as origens; não é um detector de colisão das malhas.

## Teste de renderização real: aprovado

```bash
python tools/validate_render.py
```

O teste compila e liga os três programas GLSL, cria VAOs/VBOs, carrega as imagens e verifica o FBO de profundidade. Em 960×640, com MSAA 4× e mapa de 1024×1024, a ativação das sombras alterou **8.675 pixels** acima do limiar de 12 níveis por canal utilizado pelo teste, reduzindo a contribuição luminosa total.

Também foram verificados:

- Mapa de profundidade com valores finitos e geometria registrada.
- Atualização do mapa ao mudar a posição das aeronaves.
- Imagem da cena estável quando a missão está pausada.
- Imagem diferente quando se move a câmera durante a pausa.
- Painel e ajuda desenhados sem erro OpenGL.

## Execução e inspeção visual

Foi executado um ciclo de 37 segundos simulados, usando 223 quadros e `--fixed-dt 0.1666666667`, com finalização sem erro OpenGL. Foram geradas e inspecionadas capturas com sombras em 2048 e 512 pixels de resolução, além de comparação sem sombras.

O bias foi ajustado à inclinação da superfície e à resolução do mapa após a detecção de autossombra nas capturas iniciais. A captura final de apresentação está em [preview.png](preview.png).

Na revisão visual foram conferidos os protetores de hélice, janelas da cabine, painéis solares, UVs das tampas circulares e a interface em 480×480. O contexto confirmou MSAA 4×; também foi executado `--msaa 0`. Um enquadramento próximo está em [encontro.png](encontro.png).

Foi executado também um teste de oito quadros do loop real com eventos de teclado sintetizados: pausa, retomada, avanço de etapa, reinício, mudança de velocidade, presets de câmera, restauração, ajuda e ativação/desativação dos efeitos. O relógio e as opções ao final coincidiram com os valores esperados. Isso valida o tratamento programático dos eventos, não substitui uma sessão com teclado físico na máquina da aula.

A revisão acrescentou um teste de nove quadros do loop real com clique na linha do tempo durante a pausa, ativação do acompanhamento, ocultação do painel, arrasto, zoom por roda e retomada. O instante final foi 17,5 s, com o acompanhamento ativo e a distância da câmera alterada para 22 unidades.

## Verificação estática

`ruff check` e `ruff format --check` passaram nos arquivos Python. Os módulos também passaram por compilação com `compileall`. Ruff é apenas ferramenta de desenvolvimento; não é necessário para executar a aplicação.

## Conferências restantes da dupla

Preencher nomes, matrículas e contribuições reais, executar a aplicação com janela no computador de apresentação e ensaiar as explicações individuais. A interação física com a janela e a compatibilidade do driver desse computador não foram verificadas neste ambiente sem display acessível.
