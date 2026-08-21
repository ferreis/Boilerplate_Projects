#!/bin/sh
set -eu

if [ "${APP_ENV:-development}" = "production" ]; then
    exec npm run build
fi

exec npm run dev -- --host 0.0.0.0 --port 5173
