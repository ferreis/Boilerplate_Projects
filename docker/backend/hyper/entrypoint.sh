#!/bin/sh
set -eu

cd /app
if [ "${DEPLOY_ENV:-development}" = "production" ]; then
    exec /usr/local/bin/boilerplate-api
fi

cargo build
exec /app/target/debug/boilerplate-api
