# Publicação no GitHub

Destino: [possagabriel/Trabalho-Computacao-Grafica](https://github.com/possagabriel/Trabalho-Computacao-Grafica), branch `master`.

O commit `6c2405f` — “Implementa cena 3D com drone e helicóptero” — foi preservado. A revisão foi registrada em seis commits, agrupados por assunto para que cada etapa possa ser lida e verificada isoladamente.

| Passo | Data | Commit | Conteúdo |
|---|---|---|---|
| 1 | 28/10/2026 21:58 | `feat(framework): melhora câmera, geometria e contexto OpenGL` | Órbita por arrasto, acompanhamento exponencial, MSAA com fallback, toro paramétrico e ambiente hemisférico. |
| 2 | 28/10/2026 22:47 | `feat(missao): calcula rotores e inclinação a partir do tempo contínuo` | Integral da potência, inclinação por velocidade, navegação da linha do tempo e testes correspondentes. |
| 3 | 28/10/2026 23:41 | `feat(cena): detalha aeronaves, helipontos e base aérea` | Protetores de hélice, cabine, painéis solares, acabamento da base, textura `solar.png` e testes de geometria/rotores. |
| 4 | 29/10/2026 00:36 | `feat(interface): adiciona mapa, linha do tempo e câmera por mouse` | Painel responsivo, mapa XZ, potência dos rotores, botões, cliques e novos atalhos. |
| 5 | 29/10/2026 01:24 | `test: valida controles do painel e renderização com MSAA` | Hit testing em três resoluções, botões, fallback MSAA e teste de integração OpenGL. |
| 6 | 29/10/2026 02:29 | `docs(entrega): atualiza guias, evidências e empacotamento` | README, guia técnico, roteiro, validação, capturas, script de publicação e ZIP. |

Cada mensagem de commit descreve o que foi alterado e como o código funciona. Os testes que dependem de um recurso foram registrados depois dos recursos correspondentes.

## Executar

No terminal local, dentro deste repositório, com Git configurado e acesso autenticado ao GitHub:

```bash
bash tools/publish_github.sh
```

O script:

1. recusa um index com alterações já preparadas, para não misturar trabalho;
2. executa os testes unitários com o Python do `.venv`, quando existir;
3. confere se `origin` aponta para o repositório solicitado;
4. busca a branch remota e interrompe se houver commits ausentes localmente — não usa `--force`, reset ou descarte;
5. gera `dist/base-aurora-entrega.zip`;
6. envia a **branch atual** com `--set-upstream`;
7. compara o hash de `HEAD` com `git ls-remote` para confirmar o envio.

Se a autenticação falhar, configure o método usado no terminal (`gh auth login` e `gh auth setup-git`) e execute novamente. Credenciais não devem ser colocadas no script nem no código.

## Conferência

```bash
git log --format='%h %ad %s' --date=format:'%d/%m/%Y %H:%M' -7
git status --short
git ls-remote origin refs/heads/master
```

O histórico deve mostrar o commit `6c2405f` seguido dos seis commits desta revisão, e o hash remoto deve coincidir com `git rev-parse HEAD`.

## Campos pessoais

Nomes, matrículas e contribuições individuais continuam pendentes no README. Eles não foram inventados durante a preparação e devem ser preenchidos pela dupla antes da entrega.
