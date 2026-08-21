#!/bin/sh
set -eu

if [ "${DEPLOY_ENV:-development}" = "production" ]; then
    export APP_ENV="${APP_ENV:-production}"
    exec uvicorn main:app \
        --host 0.0.0.0 \
        --port "${BACKEND_PORT:-8000}" \
        --workers "${UVICORN_WORKERS:-2}"
fi

export APP_ENV="${APP_ENV:-development}"
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "${BACKEND_PORT:-8000}" \
    --reload
