#!/bin/sh
set -eu

SSL_DIR="/etc/nginx/ssl"
SSL_KEY="${SSL_DIR}/nginx.key"
SSL_CRT="${SSL_DIR}/nginx.crt"
NGINX_ENV="${NGINX_ENV:-development}"
NGINX_HTTPS_PORT="${NGINX_HTTPS_PORT:-443}"
NGINX_CONFIG_SOURCE="/etc/nginx/nginx.conf"
NGINX_CONFIG_RUNTIME="/tmp/nginx.conf"

case "${NGINX_HTTPS_PORT}" in
    ''|*[!0-9]*)
        echo "NGINX_HTTPS_PORT inválida: use uma porta numérica entre 1 e 65535." >&2
        exit 1
        ;;
esac

if [ "${NGINX_HTTPS_PORT}" -lt 1 ] || [ "${NGINX_HTTPS_PORT}" -gt 65535 ]; then
    echo "NGINX_HTTPS_PORT inválida: use uma porta entre 1 e 65535." >&2
    exit 1
fi

if [ "${NGINX_HTTPS_PORT}" = "443" ]; then
    HTTPS_PORT_SUFFIX=""
else
    HTTPS_PORT_SUFFIX=":${NGINX_HTTPS_PORT}"
fi

sed "s|__HTTPS_PORT_SUFFIX__|${HTTPS_PORT_SUFFIX}|g" \
    "${NGINX_CONFIG_SOURCE}" > "${NGINX_CONFIG_RUNTIME}"

if grep -Fq '__HTTPS_PORT_SUFFIX__' "${NGINX_CONFIG_RUNTIME}"; then
    echo "Falha ao configurar a porta HTTPS pública no Nginx." >&2
    exit 1
fi

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
        ""|[!a-z0-9]*|*[!a-z0-9-]*)
            echo "PROJECT_NAME inválido: use letras minúsculas, números e hífens." >&2
            exit 1
            ;;
    esac

    FRONTEND_TARGET="/usr/share/nginx/html/${PROJECT_NAME}"
    rm -rf "${FRONTEND_TARGET}"
    mkdir -p "${FRONTEND_TARGET}"
    cp -a /opt/frontend-dist/. "${FRONTEND_TARGET}/"
fi

nginx -t -c "${NGINX_CONFIG_RUNTIME}"
exec nginx -c "${NGINX_CONFIG_RUNTIME}" -g "daemon off;"
