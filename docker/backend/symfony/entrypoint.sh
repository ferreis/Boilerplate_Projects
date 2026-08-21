#!/bin/sh
set -eu

if [ "${DEPLOY_ENV:-development}" = "production" ]; then
    export APP_ENV="${APP_ENV:-prod}"
    export APP_DEBUG="${APP_DEBUG:-0}"
else
    export APP_ENV="${APP_ENV:-dev}"
    export APP_DEBUG="${APP_DEBUG:-1}"
fi

if [ ! -f /app/vendor/autoload_runtime.php ]; then
    if [ "${DEPLOY_ENV:-development}" = "production" ]; then
        composer install --no-dev --no-interaction --prefer-dist --classmap-authoritative
    else
        composer install --no-interaction --prefer-dist
    fi
fi

exec frankenphp run --config /etc/frankenphp/Caddyfile
