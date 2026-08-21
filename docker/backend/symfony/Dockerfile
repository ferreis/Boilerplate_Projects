FROM dunglas/frankenphp:1-php8.4-trixie AS base

WORKDIR /app

RUN install-php-extensions pdo_pgsql opcache

COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer
COPY docker/backend/symfony/Caddyfile /etc/frankenphp/Caddyfile
COPY docker/backend/symfony/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV COMPOSER_ALLOW_SUPERUSER=1

EXPOSE 8000

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
