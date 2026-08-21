FROM nginx:alpine AS nginx-base

RUN apk add --no-cache openssl

COPY docker/nginx/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]

FROM nginx-base AS development

FROM node:24-alpine AS frontend-builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}

RUN npm run build

FROM nginx-base AS production

COPY docker/nginx/nginx.prd.conf /etc/nginx/nginx.conf
COPY --from=frontend-builder /app/dist /opt/frontend-dist
