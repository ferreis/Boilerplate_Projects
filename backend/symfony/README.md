# Backend Symfony

Implementação PHP do backend utilizando Symfony 7.4 LTS e FrankenPHP.

Esta base é exclusivamente uma API HTTP, escuta internamente em `8000` e implementa o contrato mínimo `GET /health`.

## Desenvolvimento

```bash
./scripts/select-backend.sh symfony
docker compose -f docker-compose.dev.yml up --build
```

O código é montado em `/app`; alterações PHP são refletidas sem recompilar a imagem. Se `vendor/` não existir, o `entrypoint.sh` executa o Composer antes de iniciar o FrankenPHP.

## Produção

O estágio `production` instala dependências sem pacotes de desenvolvimento, usa `php.ini-production` e serve Symfony com FrankenPHP atrás do Nginx principal.

## Arquitetura

Ao crescer, organize `src/` por domínio/feature e mantenha controllers em presentation, casos de uso separados e persistência/adapters em infrastructure, seguindo os mesmos limites conceituais documentados para o backend Python.
