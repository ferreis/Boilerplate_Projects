# Boilerplate Vue + API

Boilerplate para aplicações web com frontend Vue/Vite, Nginx como único ponto de entrada externo, PostgreSQL e API HTTP.

Backend selecionado para este projeto: **__BACKEND_DISPLAY__**.

## Arquitetura de rede

### Desenvolvimento

```text
Navegador
    |
    v
Nginx :80 / :443
    |
    +--------------------------+
    |                          |
    v                          v
Vue / Vite :5173         backend :8000
                                |
                                v
                         PostgreSQL :5432
```

### Produção

```text
Internet
   |
   v
Nginx :80 / :443
   |
   +---------------------------+
   |                           |
   v                           v
Frontend estático         backend :8000
                                |
                                v
                         PostgreSQL :5432
```

Somente o Nginx publica portas externas em produção. O backend e o PostgreSQL permanecem acessíveis apenas pelas redes internas do Docker Compose.

## Estrutura principal

```text
.
├── backend/
├── docker/
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── frontend/
│   └── nginx/
├── env/
│   ├── backend.dev.env
│   ├── database.dev.env
│   └── frontend.dev.env
├── frontend/
├── scripts/
├── docker-compose.dev.yml
└── docker-compose.prd.yml
```

A documentação específica da API fica em `backend/README.md` quando disponível.

## Contrato do backend

O serviço Docker se chama `backend` e deve:

- executar uma API HTTP;
- escutar em `0.0.0.0:8000`;
- não publicar a porta `8000` diretamente para o host;
- utilizar o hostname Docker `database` para PostgreSQL;
- disponibilizar `GET /health` retornando `{"status":"ok"}`;
- manter o comando de inicialização em `docker/backend/entrypoint.sh`.

## Nome do projeto

Substitua o marcador `{nome_projeto}` antes de iniciar o desenvolvimento:

```bash
./scripts/replace-project-name.sh meu-projeto
```

## Desenvolvimento

Revise os arquivos:

```text
env/backend.dev.env
env/database.dev.env
env/frontend.dev.env
```

Depois execute:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Para executar em segundo plano:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Para encerrar:

```bash
docker compose -f docker-compose.dev.yml down
```

## Produção

Gere os arquivos de ambiente de produção:

```bash
./scripts/create-production-envs.sh
```

Preencha os valores necessários em:

```text
env/backend.env
env/database.env
env/frontend.env
```

Configure os certificados TLS em:

```text
docker/nginx/ssl/nginx.crt
docker/nginx/ssl/nginx.key
```

Depois execute:

```bash
docker compose -f docker-compose.prd.yml up -d --build
```

## Nginx

O Nginx continua sendo independente da tecnologia usada pelo backend. Ele encaminha a API para:

```text
backend:8000
```

O prefixo público permanece:

```text
/{nome_projeto}/api/
```

Exemplo:

```text
/meu-projeto/api/health -> backend:8000/health
```

## Segurança da infraestrutura

- somente Nginx publica `80/443` em produção;
- backend não publica `8000`;
- PostgreSQL não publica `5432`;
- Nginx não participa da rede do banco;
- PostgreSQL não participa da rede externa;
- arquivos de ambiente de produção não devem ser versionados;
- comandos de runtime ficam nos respectivos `entrypoint.sh`.
