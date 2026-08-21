# Boilerplate Python + Vue

Boilerplate para iniciar aplicações web com frontend em Vue, backend em FastAPI, banco de dados PostgreSQL, proxy reverso Nginx e ambiente completamente containerizado com Docker Compose.

O projeto possui configurações separadas para desenvolvimento e produção, com foco em isolamento dos serviços, organização da infraestrutura e uma base inicial de autenticação.

## Tecnologias

- Vue
- Vite
- Vue Router
- FastAPI
- Uvicorn
- PostgreSQL 18
- Nginx
- Docker
- Docker Compose
- JWT
- bcrypt

## Arquitetura

### Desenvolvimento

No ambiente de desenvolvimento, o Nginx funciona como ponto de entrada da aplicação e encaminha as requisições para o servidor Vite ou para o FastAPI.

```text
Navegador
    |
    v
Nginx :80 / :443
    |
    +-------------------+
    |                   |
    v                   v
Vue / Vite :5173    FastAPI :8000
                        |
                        v
                  PostgreSQL :5432
```

O Vite continua disponível somente dentro das redes Docker. As portas `5173`, `8000` e `5432` não são publicadas diretamente no host.

### Produção

Em produção não existe um container Node executando o frontend.

O Vue é compilado durante o build multi-stage da imagem do Nginx. O resultado do `vite build` é copiado para a imagem final e servido diretamente pelo Nginx.

```text
Internet
   |
   v
Nginx :80 / :443
   |
   +----------------------+
   |                      |
   v                      v
Frontend estático     FastAPI :8000
                          |
                          v
                    PostgreSQL :5432
```

Somente o Nginx publica portas para o host.

O backend utiliza `expose`, mas não utiliza `ports`. Portanto, não pode ser acessado diretamente pela rede externa através do Docker Compose.

O PostgreSQL também não publica nenhuma porta e fica em uma rede interna compartilhada somente com o backend.

## Isolamento das redes em produção

O `docker-compose.prd.yml` separa a aplicação em três redes:

```text
edgeNet
   |
 Nginx
   |
backendNet (internal)
   |
Backend
   |
databaseNet (internal)
   |
PostgreSQL
```

### `edgeNet`

Rede utilizada pelo Nginx como ponto de entrada da aplicação.

### `backendNet`

Rede interna compartilhada apenas entre:

- Nginx
- Backend

O banco de dados não participa dessa rede.

### `databaseNet`

Rede interna compartilhada apenas entre:

- Backend
- PostgreSQL

O Nginx não participa dessa rede e, portanto, não consegue acessar diretamente o banco de dados.

A comunicação entre os serviços fica organizada desta forma:

```text
Internet -> Nginx -> Backend -> PostgreSQL
```

> O frontend Vue é executado no navegador do usuário. Por isso, as chamadas HTTP feitas pelo frontend para a API chegam ao Nginx como qualquer outra requisição HTTP. O isolamento impede acesso direto aos containers do backend e do banco, mas não substitui autenticação e autorização nos endpoints da API.

## Estrutura do projeto

```text
.
├── backend/
│   ├── routes/
│   ├── tests/
│   ├── authentication.py
│   ├── core.py
│   ├── main.py
│   ├── middleware.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── docker/
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   │
│   ├── frontend/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   │
│   └── nginx/
│       ├── Dockerfile
│       ├── entrypoint.sh
│       ├── nginx.dev.conf
│       └── nginx.prd.conf
│
├── env/
│   ├── backend.dev.env
│   ├── database.dev.env
│   └── frontend.dev.env
│
├── scripts/
│   ├── create-production-envs.sh
│   └── replace-project-name.sh
│
├── docker-compose.dev.yml
└── docker-compose.prd.yml
```

## Dockerfiles

Os Dockerfiles utilizam a raiz do repositório como contexto de build.

Exemplo:

```yaml
build:
  context: .
  dockerfile: docker/backend/Dockerfile
```

Isso permite que um Dockerfile armazenado dentro de `docker/` copie arquivos da aplicação, como:

```dockerfile
COPY backend/requirements.txt ./requirements.txt
COPY backend/ .
```

O mesmo padrão é utilizado no frontend e no build do Nginx.

## Entrypoints

Os comandos responsáveis por iniciar os serviços não ficam definidos no Docker Compose.

Cada serviço possui seu próprio `entrypoint.sh` dentro da pasta `docker/` correspondente.

### Backend

```text
docker/backend/entrypoint.sh
```

Em desenvolvimento inicia o Uvicorn com reload.

Em produção inicia o Uvicorn sem reload e permite configurar a quantidade de workers através de:

```env
UVICORN_WORKERS=2
```

### Frontend

```text
docker/frontend/entrypoint.sh
```

É utilizado pelo container de desenvolvimento para iniciar o Vite.

### Nginx

```text
docker/nginx/entrypoint.sh
```

No ambiente de desenvolvimento pode gerar automaticamente um certificado TLS autoassinado.

Em produção os certificados precisam existir previamente.

## Nome do projeto

Os arquivos de infraestrutura utilizam o marcador:

```text
{nome_projeto}
```

Para substituir esse marcador pelo nome real da aplicação, utilize:

```bash
./scripts/replace-project-name.sh meu-projeto
```

O nome deve:

- começar com uma letra minúscula;
- conter apenas letras minúsculas, números e hífens.

Exemplo:

```bash
./scripts/replace-project-name.sh sistema-exemplo
```

O comando atualiza os arquivos Docker Compose e as configurações do Nginx.

Essa substituição deve normalmente ser realizada uma única vez ao criar um novo projeto a partir deste boilerplate.

## Base path

A aplicação é preparada para funcionar abaixo de um prefixo de URL.

Exemplo para um projeto chamado `sistema-exemplo`:

```text
https://dominio.com/sistema-exemplo/
```

A API fica disponível através de:

```text
https://dominio.com/sistema-exemplo/api/
```

O Vite recebe o prefixo através de:

```env
VITE_BASE_PATH=/sistema-exemplo/
```

Isso faz com que os assets gerados no build utilizem o caminho correto.

## Ambiente de desenvolvimento

### 1. Configure o nome do projeto

```bash
./scripts/replace-project-name.sh meu-projeto
```

### 2. Configure as variáveis de ambiente

Revise principalmente:

```text
env/backend.dev.env
env/database.dev.env
env/frontend.dev.env
```

O backend exige uma chave JWT com pelo menos 32 caracteres:

```env
JWT_SECRET=
```

Também é necessário configurar um hash bcrypt para o usuário inicial:

```env
AUTH_PASSWORD_HASH=
```

Um hash pode ser gerado com:

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'sua-senha', bcrypt.gensalt()).decode())"
```

### 3. Suba os containers

```bash
docker compose -f docker-compose.dev.yml up --build
```

Para executar em segundo plano:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

### 4. Encerrar o ambiente

```bash
docker compose -f docker-compose.dev.yml down
```

## Ambiente de produção

### 1. Gere os arquivos de ambiente de produção

O script abaixo cria os arquivos de produção a partir dos arquivos `*.dev.env`, mantendo comentários e removendo os valores existentes:

```bash
./scripts/create-production-envs.sh
```

Serão criados arquivos como:

```text
env/backend.env
env/database.env
env/frontend.env
```

Esses arquivos não devem ser versionados com credenciais reais.

### 2. Configure as variáveis de produção

Preencha os arquivos gerados com valores seguros.

Em produção, utilize obrigatoriamente:

```env
APP_ENV=production
AUTH_COOKIE_SECURE=true
```

Também configure:

- `JWT_SECRET` com um segredo longo e aleatório;
- `AUTH_PASSWORD_HASH` com um hash bcrypt válido;
- usuário e senha fortes para o PostgreSQL;
- hosts e origens permitidas de acordo com o domínio real.

### 3. Configure TLS

Os certificados devem existir em:

```text
docker/nginx/ssl/nginx.crt
docker/nginx/ssl/nginx.key
```

O Nginx não gera certificado autoassinado quando `NGINX_ENV=production`.

### 4. Suba a aplicação

```bash
docker compose -f docker-compose.prd.yml up -d --build
```

### 5. Encerrar a aplicação

```bash
docker compose -f docker-compose.prd.yml down
```

## Persistência do PostgreSQL

O projeto utiliza PostgreSQL 18.

O volume é montado em:

```text
/var/lib/postgresql
```

Os dados são persistidos em volumes Docker separados para desenvolvimento e produção:

```text
database_dev_data
database_prd_data
```

Isso evita compartilhar acidentalmente o banco de desenvolvimento com o ambiente de produção.

## Nginx

Existem duas configurações distintas:

```text
docker/nginx/nginx.dev.conf
docker/nginx/nginx.prd.conf
```

### Desenvolvimento

O Nginx encaminha:

```text
/{nome_projeto}/        -> frontend:5173
/{nome_projeto}/api/    -> backend:8000
```

O proxy do Vite mantém suporte a WebSocket, necessário para HMR.

### Produção

O Nginx serve diretamente os arquivos compilados do Vue e encaminha apenas o caminho da API para o backend.

Outros caminhos fora do prefixo da aplicação retornam `404`.

## Backend

O backend utiliza FastAPI e possui uma base inicial para:

- autenticação com usuário e senha;
- hash de senha com bcrypt;
- access token JWT;
- refresh token JWT em cookie `HttpOnly`;
- middleware de autenticação;
- controle de roles;
- limite de tamanho das requisições;
- CORS configurável;
- validação de hosts confiáveis;
- headers básicos de segurança.

O Redis não faz parte deste boilerplate.

## Frontend

O frontend utiliza Vue com Vite e Vue Router.

O `vite.config.js` utiliza `VITE_BASE_PATH` para permitir que a aplicação seja publicada abaixo do prefixo definido para o projeto.

No desenvolvimento, o Vite é executado dentro de seu próprio container.

Na produção, o Vite é utilizado apenas durante o processo de build e não permanece executando.

## Segurança

A infraestrutura de produção segue algumas regras básicas:

- somente Nginx publica portas para o host;
- backend não publica a porta `8000`;
- PostgreSQL não publica a porta `5432`;
- redes do backend e banco são marcadas como internas;
- Nginx não participa da rede do PostgreSQL;
- PostgreSQL não participa da rede do Nginx;
- containers compatíveis utilizam `no-new-privileges:true`;
- TLS é obrigatório no ponto de entrada de produção;
- arquivos `.env` de produção não devem ser versionados;
- arquivos ocultos são bloqueados pelo Nginx;
- a versão do Nginx não é exibida nas respostas de produção.

O isolamento de rede não substitui controles de segurança da aplicação. Endpoints do backend continuam precisando aplicar autenticação, autorização, validação de entrada e demais controles necessários.

## Comandos úteis

### Desenvolvimento

```bash
docker compose -f docker-compose.dev.yml up --build
```

```bash
docker compose -f docker-compose.dev.yml down
```

### Produção

```bash
docker compose -f docker-compose.prd.yml up -d --build
```

```bash
docker compose -f docker-compose.prd.yml down
```

### Logs

```bash
docker compose -f docker-compose.dev.yml logs -f
```

```bash
docker compose -f docker-compose.prd.yml logs -f
```

### Reconstruir um serviço

```bash
docker compose -f docker-compose.dev.yml build backend
```

```bash
docker compose -f docker-compose.dev.yml build frontend
```

```bash
docker compose -f docker-compose.prd.yml build nginx
```

## Fluxo recomendado para novos projetos

```text
1. Clonar ou utilizar este repositório como template
2. Executar replace-project-name.sh
3. Configurar os arquivos de ambiente
4. Subir docker-compose.dev.yml
5. Desenvolver a aplicação
6. Gerar os arquivos de ambiente de produção
7. Configurar certificados TLS e segredos
8. Subir docker-compose.prd.yml
```
