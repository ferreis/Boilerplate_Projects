# Boilerplate Vue + API multi-backend

Boilerplate para aplicações web com frontend Vue/Vite, Nginx como único ponto de entrada externo, PostgreSQL e backend intercambiável.

O projeto permite escolher entre:

- **Python + FastAPI**;
- **C++ + Drogon**;
- **PHP + Symfony**.

Todos os backends são APIs HTTP e utilizam o mesmo serviço Docker `backend`, a mesma porta interna `8000` e o mesmo proxy do Nginx.

## Selecionando o backend

A seleção é feita por uma única variável na raiz do projeto:

```env
BACKEND_TYPE=python
```

Valores aceitos:

```text
python
drogon
symfony
```

Crie a configuração local:

```bash
cp .env.example .env
```

Depois edite `BACKEND_TYPE` ou use o script:

```bash
./scripts/select-backend.sh python
./scripts/select-backend.sh drogon
./scripts/select-backend.sh symfony
```

Também é possível sobrescrever a opção apenas para um comando:

```bash
BACKEND_TYPE=drogon docker compose -f docker-compose.dev.yml up --build
```

## Como a seleção funciona

Os arquivos Compose mantêm um único serviço chamado `backend` e resolvem os arquivos dinamicamente:

```text
backend/${BACKEND_TYPE}
docker/backend/${BACKEND_TYPE}/Dockerfile
env/backend.${BACKEND_TYPE}.dev.env
env/backend.${BACKEND_TYPE}.env
```

Exemplo com Symfony:

```text
backend/symfony
docker/backend/symfony/Dockerfile
env/backend.symfony.dev.env
env/backend.symfony.env
```

Isso significa que o frontend e o Nginx não precisam saber qual linguagem está executando a API.

## Contrato entre infraestrutura e backend

Toda implementação deve:

- executar uma API HTTP;
- escutar em `0.0.0.0:8000` por padrão;
- aceitar `BACKEND_PORT` quando aplicável;
- permanecer sem portas publicadas diretamente para o host;
- utilizar o hostname Docker `database` para PostgreSQL quando precisar do banco;
- disponibilizar `GET /health` retornando `{"status":"ok"}`;
- manter comandos de inicialização em `docker/backend/<tipo>/entrypoint.sh`.

O contrato completo está em [`backend/CONTRACT.md`](backend/CONTRACT.md).

## Estado das implementações

### Python / FastAPI

É a implementação mais completa atualmente.

Inclui:

- arquitetura modular orientada a domínio;
- autenticação por usuário e senha;
- bcrypt;
- access token JWT;
- refresh token em cookie HttpOnly;
- controle de roles;
- middlewares de segurança;
- health check;
- testes de domínio, aplicação e integração.

A documentação arquitetural específica está em:

```text
backend/python/ARCHITECTURE.md
```

### C++ / Drogon

Base de API usando Drogon e C++20.

Inclui atualmente:

- projeto CMake;
- build Docker de desenvolvimento;
- build multi-stage para produção;
- API HTTP interna em `8000`;
- `GET /health`.

Alterações de C++ em desenvolvimento exigem reiniciar o serviço `backend` para recompilar.

### PHP / Symfony

Base de API usando Symfony 7.4 LTS, PHP 8.4 e FrankenPHP.

Inclui atualmente:

- estrutura mínima Symfony;
- controller HTTP por atributo;
- FrankenPHP como servidor interno;
- configuração distinta de desenvolvimento e produção;
- suporte preparado para `pdo_pgsql`;
- `GET /health`.

## Paridade de funcionalidades

Os três backends respeitam o contrato operacional e o health check, mas **ainda não possuem paridade completa de funcionalidades**.

Atualmente a autenticação existe somente no backend Python.

Antes de trocar `BACKEND_TYPE` em uma aplicação que já dependa de endpoints específicos, esses endpoints devem ser portados para a implementação escolhida mantendo o mesmo contrato HTTP.

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

A porta do frontend, backend e PostgreSQL não é publicada diretamente no host.

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

Somente o Nginx expõe portas para o mundo externo.

As redes internas mantêm o fluxo:

```text
Internet -> Nginx -> backend -> PostgreSQL
```

O Nginx não participa da rede do banco e o PostgreSQL não participa da rede do Nginx.

## Rotas públicas

O Nginx publica a aplicação abaixo do marcador `{nome_projeto}`.

Exemplo após configurar o projeto como `meu-sistema`:

```text
https://dominio.com/meu-sistema/
https://dominio.com/meu-sistema/api/health
```

O Nginx remove `/meu-sistema/api/` antes de encaminhar a requisição ao backend. Portanto:

```text
/meu-sistema/api/health -> backend:8000/health
```

## Estrutura principal

```text
.
├── backend/
│   ├── CONTRACT.md
│   ├── README.md
│   ├── python/
│   │   ├── authentication/
│   │   ├── shared/
│   │   ├── system/
│   │   ├── tests/
│   │   ├── ARCHITECTURE.md
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── drogon/
│   │   ├── src/
│   │   ├── CMakeLists.txt
│   │   └── README.md
│   └── symfony/
│       ├── config/
│       ├── public/
│       ├── src/
│       ├── composer.json
│       └── README.md
│
├── docker/
│   ├── backend/
│   │   ├── python/
│   │   ├── drogon/
│   │   └── symfony/
│   ├── frontend/
│   └── nginx/
│
├── env/
│   ├── backend.python.dev.env
│   ├── backend.drogon.dev.env
│   ├── backend.symfony.dev.env
│   ├── database.dev.env
│   └── frontend.dev.env
│
├── scripts/
│   ├── create-production-envs.sh
│   ├── replace-project-name.sh
│   └── select-backend.sh
│
├── .env.example
├── docker-compose.dev.yml
└── docker-compose.prd.yml
```

## Configurando um novo projeto

### 1. Configure o nome

```bash
./scripts/replace-project-name.sh meu-projeto
```

O nome deve começar com letra minúscula e pode conter letras minúsculas, números e hífens.

### 2. Escolha o backend

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

### 3. Configure o ambiente de desenvolvimento

Edite o arquivo correspondente ao backend escolhido:

```text
env/backend.python.dev.env
env/backend.drogon.dev.env
env/backend.symfony.dev.env
```

Também revise:

```text
env/database.dev.env
env/frontend.dev.env
```

### 4. Suba o ambiente

```bash
docker compose -f docker-compose.dev.yml up --build
```

Em segundo plano:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

### 5. Encerre

```bash
docker compose -f docker-compose.dev.yml down
```

## Produção

### 1. Gere os arquivos de produção

```bash
./scripts/create-production-envs.sh
```

O script gera, entre outros:

```text
env/backend.python.env
env/backend.drogon.env
env/backend.symfony.env
env/database.env
env/frontend.env
```

Os valores são removidos dos modelos para evitar reaproveitar segredos de desenvolvimento.

### 2. Preencha o ambiente selecionado

Se estiver usando Python:

```text
env/backend.python.env
```

Se estiver usando Drogon:

```text
env/backend.drogon.env
```

Se estiver usando Symfony:

```text
env/backend.symfony.env
```

### 3. Configure TLS

Os certificados de produção devem existir em:

```text
docker/nginx/ssl/nginx.crt
docker/nginx/ssl/nginx.key
```

### 4. Suba a aplicação

```bash
docker compose -f docker-compose.prd.yml up -d --build
```

## Dockerfiles de backend

Os três Dockerfiles possuem targets padronizados:

```text
development
production
```

O Compose de desenvolvimento sempre utiliza `development`; o Compose de produção sempre utiliza `production`.

Nenhum `command` de runtime é definido no Compose. A inicialização pertence aos respectivos `entrypoint.sh`.

## PostgreSQL

O banco utiliza PostgreSQL 18 e persiste dados no volume Docker montado em:

```text
/var/lib/postgresql
```

O banco não publica `5432` para o host.

Quando um backend implementar persistência, deve conectar internamente usando o serviço:

```text
database:5432
```

## Frontend

O frontend utiliza Vue, Vite e Vue Router.

Em desenvolvimento, o Vite roda em um container interno.

Em produção, o frontend é compilado durante o build do Nginx e servido como arquivos estáticos. Não existe servidor Node de frontend em produção.

## Nginx

O Nginx é independente do backend escolhido.

Ele sempre encaminha a API para:

```text
backend:8000
```

Por isso, adicionar uma nova linguagem de backend não deve exigir mudanças no Nginx se o contrato definido em `backend/CONTRACT.md` for respeitado.

## Adicionando outro backend

Para adicionar uma quarta implementação, por exemplo `go`:

```text
backend/go/
docker/backend/go/Dockerfile
docker/backend/go/entrypoint.sh
env/backend.go.dev.env
```

O Dockerfile precisa possuir os targets:

```text
development
production
```

Depois adicione o novo identificador à validação de `scripts/select-backend.sh`.

Não é necessário duplicar Docker Compose nem alterar o Nginx.

## Segurança

Em produção:

- apenas Nginx publica `80/443`;
- backend não publica `8000`;
- PostgreSQL não publica `5432`;
- `backendNet` e `databaseNet` são redes internas;
- Nginx não acessa diretamente PostgreSQL;
- arquivos de ambiente de produção não são versionados;
- TLS termina no Nginx;
- autenticação e autorização continuam sendo responsabilidade da implementação escolhida.
