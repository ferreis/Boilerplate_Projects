# Boilerplate Vue + API

Boilerplate para aplicações web com frontend Vue/Vite, Nginx como único ponto de entrada externo, PostgreSQL e backend selecionável durante a criação do projeto.

O template oferece três implementações iniciais:

- **Python + FastAPI**;
- **C++ + Drogon**;
- **PHP + Symfony**.

A seleção é uma etapa de inicialização do projeto. Depois de escolher uma implementação, as outras são removidas e o projeto passa a possuir apenas um backend.

## Selecionar o backend

Execute uma única vez:

```bash
./scripts/select-backend.sh python
```

ou:

```bash
./scripts/select-backend.sh drogon
```

ou:

```bash
./scripts/select-backend.sh symfony
```

### O que o script faz

A seleção é **definitiva para a cópia atual do projeto**.

O script:

1. preserva somente a implementação escolhida;
2. remove os outros diretórios de backend;
3. remove os Dockerfiles dos outros backends;
4. remove os arquivos de ambiente dos outros backends;
5. promove o backend escolhido de `backend/<tipo>/` para `backend/`;
6. promove `docker/backend/<tipo>/` para `docker/backend/`;
7. renomeia `env/backend.<tipo>.dev.env` para `env/backend.dev.env`;
8. preserva `env/backend.<tipo>.env` como `env/backend.env`, caso já exista;
9. substitui as referências dinâmicas dos arquivos Docker Compose por caminhos fixos;
10. normaliza os paths internos do Dockerfile escolhido;
11. atualiza `README.md` e `AGENTS.md` para a estrutura final;
12. remove os arquivos usados exclusivamente para a seleção, inclusive o próprio `select-backend.sh`.

Portanto, depois da seleção não existe `BACKEND_TYPE` nem referência às implementações descartadas.

## Estrutura antes da seleção

```text
backend/
├── CONTRACT.md
├── README.md
├── python/
├── drogon/
└── symfony/

docker/backend/
├── python/
├── drogon/
└── symfony/

env/
├── backend.python.dev.env
├── backend.drogon.dev.env
└── backend.symfony.dev.env
```

## Estrutura depois da seleção

Exemplo conceitual, independentemente da linguagem escolhida:

```text
backend/
├── README.md
└── ... código da API selecionada

docker/backend/
├── Dockerfile
├── entrypoint.sh
└── ... arquivos específicos do runtime

env/
├── backend.dev.env
├── database.dev.env
└── frontend.dev.env
```

Os arquivos Compose também passam a usar caminhos fixos:

```text
backend/
docker/backend/Dockerfile
env/backend.dev.env
env/backend.env
```

## Contrato comum das implementações

Antes da seleção, todas as opções devem respeitar `backend/CONTRACT.md`.

O backend escolhido deve:

- executar uma API HTTP;
- escutar em `0.0.0.0:8000` (Python/Drogon) ou receber FastCGI em `9000` (Symfony);
- permanecer sem porta publicada diretamente para o host;
- utilizar o hostname Docker `database` para PostgreSQL;
- disponibilizar `GET /health` retornando `{"status":"ok"}`;
- manter comandos de runtime no respectivo `entrypoint.sh`.

Após selecionar o backend, o Nginx mantém HTTP na porta 8000 para Python/Drogon e passa a FastCGI na porta 9000 para Symfony. Antes da seleção, o contrato HTTP padrão é:

```text
backend:8000
```

## Estado das implementações

### Python / FastAPI

É a implementação mais completa atualmente.

Inclui:

- arquitetura modular orientada a domínio;
- autenticação por usuário e senha;
- bcrypt;
- access token JWT;
- refresh token em cookie HttpOnly;
- autorização por roles;
- middlewares de segurança;
- health check;
- testes de domínio, aplicação, infraestrutura e integração.

### C++ / Drogon

Base de API usando Drogon e C++20.

Inclui:

- CMake;
- build Docker de desenvolvimento;
- build multi-stage para produção;
- API HTTP interna em `8000`;
- `GET /health`.

### PHP / Symfony

Base de API usando Symfony 7.4 LTS, PHP 8.4 e PHP-FPM.

Inclui:

- estrutura mínima Symfony;
- PHP-FPM como processo FastCGI interno na porta `9000`;
- `pdo_pgsql`, `intl`, `mbstring` e `opcache`;
- configuração distinta de desenvolvimento e produção;
- `GET /health`.

As implementações ainda não possuem paridade completa de funcionalidades. A autenticação existente está implementada no backend Python e deve ser portada caso outro backend precise oferecer o mesmo contrato funcional.

## Configurando um novo projeto

### 1. Escolha o backend

Execute `select-backend.sh` antes de começar a desenvolver.

### 2. Configure o nome do projeto

```bash
./scripts/replace-project-name.sh meu-projeto
```

Use apenas letras minúsculas, números e hífens.

### 3. Configure os ambientes

Depois da seleção, revise:

```text
env/backend.dev.env
env/database.dev.env
env/frontend.dev.env
```

### 4. Suba o desenvolvimento

```bash
docker compose -f docker-compose.dev.yml up --build
```

Em segundo plano:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Para encerrar:

```bash
docker compose -f docker-compose.dev.yml down
```

### Acesso local

Depois de configurar o nome do projeto, use esse nome no prefixo público. Para um projeto chamado `meu-projeto`, as URLs padrão são:

```text
https://localhost/meu-projeto/
https://localhost/meu-projeto/api/health
```

O acesso HTTP redireciona para HTTPS preservando o caminho. O certificado de desenvolvimento é autoassinado, portanto o navegador pode solicitar confirmação local.

As portas externas podem ser alteradas sem modificar as portas internas dos containers:

```bash
NGINX_HTTP_PORT=8080 NGINX_HTTPS_PORT=8443 docker compose -f docker-compose.dev.yml up --build
```

Nesse caso:

```text
http://localhost:8080/meu-projeto/ -> https://localhost:8443/meu-projeto/
https://localhost:8443/meu-projeto/api/health
```

O redirecionamento `/meu-projeto/api` -> `/meu-projeto/api/` é relativo e preserva host, esquema e porta. O Nginx remove o prefixo público ao encaminhar a API, então `/meu-projeto/api/health` chega ao backend como `/health`.

## Produção

Gere os arquivos de produção depois da seleção:

```bash
./scripts/create-production-envs.sh
```

Os arquivos principais serão:

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

Também é possível definir `NGINX_HTTP_PORT` e `NGINX_HTTPS_PORT` ao iniciar o Compose de produção. Apenas as portas do Nginx são publicadas; backend e PostgreSQL continuam internos.

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
Vue / Vite :5173         backend :8000 (HTTP) / :9000 (FastCGI)
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
Frontend estático         backend :8000 (HTTP) / :9000 (FastCGI)
                                |
                                v
                         PostgreSQL :5432
```

Somente o Nginx expõe portas externas em produção.

## Segurança

Em produção:

- apenas Nginx publica `80/443` por padrão;
- backend não publica `8000`;
- PostgreSQL não publica `5432`;
- `backendNet` e `databaseNet` são redes internas;
- Nginx não acessa diretamente PostgreSQL;
- arquivos de ambiente de produção não são versionados;
- TLS termina no Nginx;
- autenticação e autorização continuam sendo responsabilidade da implementação escolhida.
