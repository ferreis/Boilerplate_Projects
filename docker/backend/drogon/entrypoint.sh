#!/bin/sh
set -eu

if [ "${DEPLOY_ENV:-development}" = "production" ]; then
    exec "${APP_BINARY:-/usr/local/bin/boilerplate-api}"
fi

BUILD_DIRECTORY="/tmp/boilerplate-drogon-build"
rm -rf "${BUILD_DIRECTORY}"

cmake -S /app -B "${BUILD_DIRECTORY}" -DCMAKE_BUILD_TYPE=Debug
cmake --build "${BUILD_DIRECTORY}" --parallel "${BUILD_JOBS:-2}"

exec "${BUILD_DIRECTORY}/boilerplate_api"
