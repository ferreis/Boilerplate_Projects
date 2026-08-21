FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/backend/python/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

FROM base AS development
COPY backend/python/ /app/
ENTRYPOINT ["/entrypoint.sh"]

FROM base AS production
COPY backend/python/ /app/
ENTRYPOINT ["/entrypoint.sh"]
