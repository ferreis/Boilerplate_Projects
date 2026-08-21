# Backend Drogon

Implementação C++ do backend utilizando Drogon e C++20.

Esta base expõe uma API HTTP na porta interna `8000` e implementa `GET /health`.

## Desenvolvimento

Execute o Compose normalmente:

```bash
docker compose -f docker-compose.dev.yml up --build
```

O código é montado em `/app` e compilado pelo `entrypoint.sh`. Após alterar C++, reinicie o serviço `backend` para recompilar.

## Produção

O Dockerfile compila o binário em um estágio separado de build e a imagem de produção executa somente o binário resultante.

```bash
docker compose -f docker-compose.prd.yml up -d --build
```

## Organização

Ao adicionar funcionalidades, prefira módulos por domínio/feature em `src/`, mantendo controllers HTTP separados das regras de negócio e adapters de infraestrutura.
