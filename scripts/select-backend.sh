#!/usr/bin/env sh
set -eu

SCRIPT_DIRECTORY="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_DIRECTORY="$(CDPATH= cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
TEMPLATE_DIRECTORY="${SCRIPT_DIRECTORY}/templates"

print_usage() {
    echo "Uso: $0 <python|drogon|symfony>" >&2
}

if [ "$#" -ne 1 ]; then
    print_usage
    exit 1
fi

BACKEND_TYPE="$1"
case "${BACKEND_TYPE}" in
    python)
        BACKEND_DISPLAY="Python + FastAPI"
        ;;
    drogon)
        BACKEND_DISPLAY="C++ + Drogon"
        ;;
    symfony)
        BACKEND_DISPLAY="PHP + Symfony"
        ;;
    *)
        echo "Backend inválido: ${BACKEND_TYPE}" >&2
        print_usage
        exit 1
        ;;
esac

BACKEND_SOURCE="${PROJECT_DIRECTORY}/backend/${BACKEND_TYPE}"
DOCKER_SOURCE="${PROJECT_DIRECTORY}/docker/backend/${BACKEND_TYPE}"
DEV_ENV_SOURCE="${PROJECT_DIRECTORY}/env/backend.${BACKEND_TYPE}.dev.env"
PROD_ENV_SOURCE="${PROJECT_DIRECTORY}/env/backend.${BACKEND_TYPE}.env"

if [ ! -d "${BACKEND_SOURCE}" ]; then
    echo "Código do backend não encontrado: backend/${BACKEND_TYPE}" >&2
    exit 1
fi

if [ ! -f "${DOCKER_SOURCE}/Dockerfile" ]; then
    echo "Dockerfile do backend não encontrado: docker/backend/${BACKEND_TYPE}/Dockerfile" >&2
    exit 1
fi

if [ ! -f "${DEV_ENV_SOURCE}" ]; then
    echo "Arquivo de ambiente não encontrado: env/backend.${BACKEND_TYPE}.dev.env" >&2
    exit 1
fi

if [ ! -f "${TEMPLATE_DIRECTORY}/README.selected.md" ] || [ ! -f "${TEMPLATE_DIRECTORY}/AGENTS.selected.md" ]; then
    echo "Templates pós-seleção não encontrados em scripts/templates." >&2
    exit 1
fi

TEMP_DIRECTORY="$(mktemp -d "${PROJECT_DIRECTORY}/.backend-selection.XXXXXX")"
cleanup() {
    rm -rf "${TEMP_DIRECTORY}"
}
trap cleanup EXIT HUP INT TERM

mv "${BACKEND_SOURCE}" "${TEMP_DIRECTORY}/backend"
mv "${DOCKER_SOURCE}" "${TEMP_DIRECTORY}/docker-backend"
mv "${DEV_ENV_SOURCE}" "${TEMP_DIRECTORY}/backend.dev.env"

if [ -f "${PROD_ENV_SOURCE}" ]; then
    mv "${PROD_ENV_SOURCE}" "${TEMP_DIRECTORY}/backend.env"
fi

rm -rf "${PROJECT_DIRECTORY}/backend"
mv "${TEMP_DIRECTORY}/backend" "${PROJECT_DIRECTORY}/backend"

rm -rf "${PROJECT_DIRECTORY}/docker/backend"
mv "${TEMP_DIRECTORY}/docker-backend" "${PROJECT_DIRECTORY}/docker/backend"

rm -f \
    "${PROJECT_DIRECTORY}/env/backend.dev.env" \
    "${PROJECT_DIRECTORY}/env/backend.env" \
    "${PROJECT_DIRECTORY}"/env/backend.*.dev.env \
    "${PROJECT_DIRECTORY}"/env/backend.*.env

mv "${TEMP_DIRECTORY}/backend.dev.env" "${PROJECT_DIRECTORY}/env/backend.dev.env"
if [ -f "${TEMP_DIRECTORY}/backend.env" ]; then
    mv "${TEMP_DIRECTORY}/backend.env" "${PROJECT_DIRECTORY}/env/backend.env"
fi

sed -i \
    -e "s#backend/${BACKEND_TYPE}/#backend/#g" \
    -e "s#docker/backend/${BACKEND_TYPE}/#docker/backend/#g" \
    "${PROJECT_DIRECTORY}/docker/backend/Dockerfile"

sed -i \
    -e 's#docker/backend/__SELECT_BACKEND__/Dockerfile#docker/backend/Dockerfile#g' \
    -e 's#./backend/__SELECT_BACKEND__:/app#./backend:/app#g' \
    -e 's#./env/backend.__SELECT_BACKEND__.dev.env#./env/backend.dev.env#g' \
    "${PROJECT_DIRECTORY}/docker-compose.dev.yml"

sed -i \
    -e 's#docker/backend/__SELECT_BACKEND__/Dockerfile#docker/backend/Dockerfile#g' \
    -e 's#./env/backend.__SELECT_BACKEND__.env#./env/backend.env#g' \
    "${PROJECT_DIRECTORY}/docker-compose.prd.yml"

if [ -f "${PROJECT_DIRECTORY}/.env" ]; then
    CLEAN_ENV_FILE="${TEMP_DIRECTORY}/root.env"
    awk '
        /^BACKEND_TYPE=/ { next }
        /^# Backend utilizado pelos arquivos Docker Compose\.$/ { next }
        /^# Valores aceitos: python, drogon, symfony\.$/ { next }
        { print }
    ' "${PROJECT_DIRECTORY}/.env" > "${CLEAN_ENV_FILE}"

    if grep -Eq '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*=' "${CLEAN_ENV_FILE}"; then
        mv "${CLEAN_ENV_FILE}" "${PROJECT_DIRECTORY}/.env"
    else
        rm -f "${PROJECT_DIRECTORY}/.env"
    fi
fi

sed "s#__BACKEND_DISPLAY__#${BACKEND_DISPLAY}#g" \
    "${TEMPLATE_DIRECTORY}/README.selected.md" > "${PROJECT_DIRECTORY}/README.md"
cp "${TEMPLATE_DIRECTORY}/AGENTS.selected.md" "${PROJECT_DIRECTORY}/AGENTS.md"

rm -rf "${TEMPLATE_DIRECTORY}"

printf 'Backend selecionado: %s\n' "${BACKEND_DISPLAY}"
printf 'As outras implementações e referências de seleção foram removidas do projeto.\n'
printf 'Estrutura final: backend/, docker/backend/ e env/backend.dev.env.\n'

trap - EXIT HUP INT TERM
rm -rf "${TEMP_DIRECTORY}"
rm -f "${SCRIPT_DIRECTORY}/select-backend.sh"
