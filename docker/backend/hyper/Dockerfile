FROM rust:1-bookworm AS base

WORKDIR /app
COPY docker/backend/hyper/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000

FROM base AS development
COPY backend/hyper/ /app/
ENTRYPOINT ["/entrypoint.sh"]

FROM rust:1-bookworm AS builder
WORKDIR /app
COPY backend/hyper/ /app/
RUN cargo build --release

FROM debian:bookworm-slim AS production
RUN useradd --system --uid 10001 --no-create-home appuser
COPY --from=builder /app/target/release/boilerplate-api /usr/local/bin/boilerplate-api
USER appuser
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/boilerplate-api"]
