#!/usr/bin/env sh
set -eu

SCRIPT_DIRECTORY="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_DIRECTORY="$(CDPATH= cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
ENV_FILE="${PROJECT_DIRECTORY}/.env"
EXAMPLE_FILE="${PROJECT_DIRECTORY}/.env.example"

print_usage() {
    echo "Uso: $0 <python|drogon|symfony>" >&2
}

if [ "$#" -ne 1 ]; then
    print_usage
    exit 1
fi

BACKEND_TYPE="$1"
case "${BACKEND_TYPE}" in
    python|drogon|symfony) ;;
    *)
        echo "Backend inválido: ${BACKEND_TYPE}" >&2
        print_usage
        exit 1
        ;;
esac

if [ ! -d "${PROJECT_DIRECTORY}/backend/${BACKEND_TYPE}" ]; then
    echo "Código do backend não encontrado: backend/${BACKEND_TYPE}" >&2
    exit 1
fi

if [ ! -f "${PROJECT_DIRECTORY}/docker/backend/${BACKEND_TYPE}/Dockerfile" ]; then
    echo "Dockerfile do backend não encontrado: docker/backend/${BACKEND_TYPE}/Dockerfile" >&2
    exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
    cp "${EXAMPLE_FILE}" "${ENV_FILE}"
fi

TEMP_FILE="$(mktemp)"
awk -v backend_type="${BACKEND_TYPE}" '
    BEGIN { updated = 0 }
    /^BACKEND_TYPE=/ {
        print "BACKEND_TYPE=" backend_type
        updated = 1
        next
    }
    { print }
    END {
        if (!updated) {
            print "BACKEND_TYPE=" backend_type
        }
    }
' "${ENV_FILE}" > "${TEMP_FILE}"
mv "${TEMP_FILE}" "${ENV_FILE}"

printf 'Backend selecionado: %s\n' "${BACKEND_TYPE}"
