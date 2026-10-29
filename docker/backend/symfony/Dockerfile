FROM php:8.4-fpm-trixie AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libicu-dev libpq-dev libonig-dev \
    && docker-php-ext-install -j"$(nproc)" intl mbstring pdo_pgsql opcache \
    && rm -rf /var/lib/apt/lists/*

# Preserva variáveis fornecidas pelo Docker Compose para o Symfony.
RUN printf '\nclear_env = no\n' >> /usr/local/etc/php-fpm.d/www.conf

COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer
COPY docker/backend/symfony/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV COMPOSER_ALLOW_SUPERUSER=1
EXPOSE 9000

FROM base AS development
RUN cp "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"
COPY backend/symfony/composer.json /app/composer.json
RUN composer install --no-interaction --prefer-dist
COPY backend/symfony/ /app/
ENTRYPOINT ["/entrypoint.sh"]

FROM base AS production
RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
COPY backend/symfony/composer.json /app/composer.json
RUN composer install --no-dev --no-interaction --prefer-dist --classmap-authoritative
COPY backend/symfony/ /app/
RUN composer dump-autoload --no-dev --classmap-authoritative
ENTRYPOINT ["/entrypoint.sh"]
