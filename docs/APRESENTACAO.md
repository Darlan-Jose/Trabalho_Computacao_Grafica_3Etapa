# Apresentação de 10 minutos

Preencher os nomes e as contribuições reais no README. Os dois integrantes devem conhecer a cena completa. Este roteiro distribui a fala, mas não substitui estudo e revisão.

| Tempo | Participação sugerida | Demonstração / explicação |
|---|---|---|
| 0:00–0:45 | Ambos | Identificar os temas 3 e 4 e apresentar a base aérea. |
| 0:45–1:40 | Integrante do drone | Mostrar um ciclo: espera, encontro, inspeção e escolta. Explicar por que há dependência. |
| 1:40–2:50 | Integrante do drone | Abrir `app/models.py`: quatro braços/motores/hélices, câmera e hierarquia. |
| 2:50–4:00 | Integrante do helicóptero | Mostrar fuselagem, cauda, dois rotores e patins; explicar translação, escala e rotação local. |
| 4:00–5:00 | Integrante do drone | Mostrar `Mission.advance`/`sample`: segundos, smoothstep, pausa e deslocamento relativo na escolta. |
| 5:00–6:00 | Integrante do helicóptero | Pausar com Espaço e mover câmera com setas; explicar perspectiva e matrizes. |
| 6:00–7:00 | Integrante do drone | Mostrar uma textura, UVs e os atributos posição/normal/UV. |
| 7:00–8:35 | Integrante do helicóptero | Alternar P; distinguir sombreamento de sombra. Explicar os dois passes, depth map, bias e PCF. |
| 8:35–9:10 | Ambos | Alternar B para mostrar as faixas procedurais e mencionar o bônus opcional. |
| 9:10–10:00 | Ambos | Declarar uso de IA, explicar revisões/contribuições reais e responder a perguntas. |

## Preparação da demonstração

```bash
python main.py --time 14
```

1. Usar 2 para aproximar a câmera do encontro.
2. Deixar o drone contornar o helicóptero e observar a formação.
3. Pausar; orbitar e comparar sombras com P.
4. Usar 1 para vista geral, depois R para reiniciar.
5. Usar N para chegar rapidamente a uma etapa durante perguntas.
6. Abrir `docs/GUIA_TECNICO.md` e os shaders no editor antes da fala.
7. Clicar na linha do tempo para selecionar uma etapa; usar F para acompanhar a formação e Tab para ocultar o painel.
8. Observar os rotores ganhando velocidade na preparação e desacelerando após o pouso. Explicar a integral da potência e a inclinação calculada a partir da velocidade.

## Perguntas para ensaiar

- **Por que não são movimentos independentes?** A chegada do helicóptero precede e libera a decolagem do drone; a inspeção termina antes da escolta; na escolta o drone deriva sua posição da posição do helicóptero.
- **O que acontece a 30 e 144 FPS?** São amostrados números diferentes de quadros do mesmo percurso em segundos. Os testes conferem poses equivalentes no mesmo instante.
- **Por que o rotor acompanha o helicóptero?** A matriz mundo do rotor inclui a matriz mundo do pai, antes da rotação local das pás.
- **Qual a diferença entre atributo e uniform?** Atributos variam por vértice; uniforms são constantes durante uma chamada de desenho. Ex.: posição do vértice versus matriz do modelo.
- **Por que inversa transposta nas normais?** Para preservar a perpendicularidade após escala não uniforme.
- **Por que perspectiva na câmera e ortográfica na luz?** O observador percebe diminuição com distância; a luz direcional representa raios paralelos.
- **O que é armazenado no shadow map?** A profundidade da superfície mais próxima vista pela luz em cada texel.
- **A sombra é uma imagem pronta?** Não; ela resulta da comparação de profundidades e acompanha a pose das malhas a cada quadro.
- **Como a pausa permite mover a câmera?** O relógio da missão para, enquanto os eventos, o controle da câmera e a renderização continuam.
- **O brilho das luzes de sinalização ilumina a base?** Não; emissão apenas preserva a cor dessas superfícies. A iluminação do ambiente vem da fonte direcional e da parcela ambiente.
- **Quais partes tiveram apoio de IA?** Todos os arquivos novos desta entrega. Relatar com precisão as revisões e alterações realmente feitas pela dupla.

## Checklist na máquina da apresentação

- [ ] Nomes, matrículas e contribuições reais preenchidos.
- [ ] Dependências instaladas e `python main.py` abrindo uma janela.
- [ ] Ciclo completo observado, incluindo retorno e repetição sem saltos.
- [ ] Quatro hélices do drone, rotor principal e de cauda em movimento.
- [ ] Espaço pausa/retoma; câmera continua livre; redimensionamento mantém proporção.
- [ ] P remove/recoloca sombras sem remover o sombreamento das superfícies.
- [ ] Texturas de imagem visíveis no piso e nos helipontos.
- [ ] Ambos conseguem localizar os principais arquivos e explicar os shaders.
- [ ] Arquivo ZIP atualizado e extraído/testado em outra pasta.
