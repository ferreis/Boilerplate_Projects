# Backend Python

Implementação do backend utilizando FastAPI.

A API escuta internamente na porta `8000` e mantém a arquitetura modular orientada a domínio documentada em `ARCHITECTURE.md`.

## Desenvolvimento

```bash
docker compose -f docker-compose.dev.yml up --build
```

O Uvicorn é iniciado com reload pelo `docker/backend/entrypoint.sh`.

## Produção

```bash
docker compose -f docker-compose.prd.yml up -d --build
```

O Uvicorn é iniciado sem reload e a quantidade de workers pode ser configurada por `UVICORN_WORKERS`.

## Funcionalidades atuais

- autenticação por usuário e senha;
- bcrypt;
- access token JWT;
- refresh token em cookie HttpOnly;
- autorização por roles;
- middlewares de segurança;
- `GET /health`;
- testes de domínio, aplicação, infraestrutura e integração.

## Arquitetura

Consulte:

```text
backend/ARCHITECTURE.md
```
