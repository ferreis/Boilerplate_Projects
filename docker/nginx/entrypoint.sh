#!/bin/sh
set -eu

SSL_DIR="/etc/nginx/ssl"
SSL_KEY="${SSL_DIR}/nginx.key"
SSL_CRT="${SSL_DIR}/nginx.crt"
NGINX_ENV="${NGINX_ENV:-development}"

mkdir -p "${SSL_DIR}"

if [ "${NGINX_ENV}" = "development" ]; then
    if [ ! -f "${SSL_KEY}" ] || [ ! -f "${SSL_CRT}" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "${SSL_KEY}" \
            -out "${SSL_CRT}" \
            -subj "/C=BR/ST=Santa Catarina/L=Itajai/O=boilerplate/OU=Development/CN=localhost"
    fi
else
    if [ ! -f "${SSL_KEY}" ] || [ ! -f "${SSL_CRT}" ]; then
        echo "Certificado TLS de produção não encontrado em ${SSL_DIR}." >&2
        exit 1
    fi
fi

if [ -d /opt/frontend-dist ]; then
    PROJECT_NAME="${PROJECT_NAME:-}"

    case "${PROJECT_NAME}" in
        ""|[!a-z]*|*[!a-z0-9-]*)
            echo "PROJECT_NAME inválido: use letras minúsculas, números e hífens, iniciando por letra." >&2
            exit 1
            ;;
    esac

    FRONTEND_TARGET="/usr/share/nginx/html/${PROJECT_NAME}"
    rm -rf "${FRONTEND_TARGET}"
    mkdir -p "${FRONTEND_TARGET}"
    cp -a /opt/frontend-dist/. "${FRONTEND_TARGET}/"
fi

exec nginx -g "daemon off;"
