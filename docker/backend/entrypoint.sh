#!/bin/sh
set -eu

if [ "${APP_ENV:-development}" = "production" ]; then
    exec uvicorn main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers "${UVICORN_WORKERS:-2}"
fi

exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
