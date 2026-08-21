FROM drogonframework/drogon:latest AS base

WORKDIR /app

COPY docker/backend/drogon/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

FROM base AS development
COPY backend/drogon/ /app/
ENTRYPOINT ["/entrypoint.sh"]

FROM base AS builder
WORKDIR /src
COPY backend/drogon/ /src/
RUN cmake -S /src -B /build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /build --parallel 2

FROM base AS production
COPY --from=builder /build/boilerplate_api /usr/local/bin/boilerplate-api
ENV APP_BINARY=/usr/local/bin/boilerplate-api
ENTRYPOINT ["/entrypoint.sh"]
