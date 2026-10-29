#!/usr/bin/env bash
# Execute no terminal local: bash tools/publish_github.sh
# Valida, empacota e envia os commits já registrados; não cria nem reescreve histórico.
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$project_root"
repository_url='https://github.com/possagabriel/Trabalho-Computacao-Grafica.git'

if [[ "$(git rev-parse --show-toplevel)" != "$project_root" ]]; then
    printf 'Execute dentro do repositório Trabalho-Computacao-Grafica.\n' >&2
    exit 1
fi
branch="$(git symbolic-ref --quiet --short HEAD)"
if ! git diff --cached --quiet; then
    printf 'Existem alterações já preparadas no index. Resolva-as antes de executar este script.\n' >&2
    exit 1
fi
if ! git diff --quiet; then
    printf 'Existem alterações não registradas. Faça o commit antes de publicar.\n' >&2
    exit 1
fi
git var GIT_AUTHOR_IDENT >/dev/null

python_command='python3'
if [[ -x .venv/bin/python ]]; then
    python_command='.venv/bin/python'
fi
printf 'Executando os testes unitários antes do envio...\n'
"$python_command" -m unittest discover -s tests -v

if git remote get-url origin >/dev/null 2>&1; then
    case "$(git remote get-url origin)" in
        https://github.com/possagabriel/Trabalho-Computacao-Grafica|\
        https://github.com/possagabriel/Trabalho-Computacao-Grafica.git|\
        git@github.com:possagabriel/Trabalho-Computacao-Grafica.git) ;;
        *) printf 'O remoto origin aponta para outro repositório; nenhum remoto foi alterado.\n' >&2; exit 1 ;;
    esac
else
    git remote add origin "$repository_url"
fi

# Falhas de rede/autenticação interrompem antes do push.
git fetch origin
if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
    if ! git merge-base --is-ancestor "origin/$branch" HEAD; then
        printf 'A branch remota tem commits ausentes localmente. Integre-os antes de publicar.\n' >&2
        exit 1
    fi
fi

printf 'Validando e empacotando os commits já registrados...\n'
"$python_command" tools/package_project.py
git push --set-upstream origin "$branch"

# Confirma que o HEAD publicado corresponde ao último commit local.
local_head="$(git rev-parse HEAD)"
remote_head="$(git ls-remote origin "refs/heads/$branch" | cut -f1)"
if [[ "$local_head" != "$remote_head" ]]; then
    printf 'O push terminou, mas não foi possível confirmar o HEAD remoto.\n' >&2
    exit 1
fi
printf '\nPublicação confirmada na branch %s: %s\n' "$branch" "$local_head"
git log -7 --oneline
