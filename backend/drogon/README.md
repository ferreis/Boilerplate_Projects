# Backend Drogon

Implementação C++ do backend utilizando Drogon.

Esta base expõe uma API HTTP na porta interna `8000` e implementa o contrato mínimo `GET /health`.

## Desenvolvimento

Selecione o backend:

```bash
./scripts/select-backend.sh drogon
```

Depois execute o Compose normalmente:

```bash
docker compose -f docker-compose.dev.yml up --build
```

O código é montado em `/app` e compilado pelo `entrypoint.sh`. Após alterar C++, reinicie o serviço `backend` para recompilar.

## Produção

O Dockerfile compila o binário em um estágio separado de build e a imagem de produção executa somente o binário já compilado.

## Organização futura

Ao adicionar funcionalidades, prefira módulos por domínio/feature em `src/`, mantendo controllers HTTP separados das regras de negócio e adapters de infraestrutura.
