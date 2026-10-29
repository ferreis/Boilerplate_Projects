# Backend Rust + Hyper

Servidor HTTP enxuto escrito em Rust com Hyper 1 e Tokio. Implementa o contrato comum do boilerplate: `GET /health` responde com `{"status":"ok"}`, porta interna `8000`, Nginx como único ponto de entrada público.

## Seleção

Na raiz do boilerplate (antes da seleção de outro backend):

```sh
./scripts/select-backend.sh hyper
./scripts/replace-project-name.sh meu-projeto
docker compose -f docker-compose.dev.yml up --build
```

A API responde em `https://localhost/meu-projeto/api/health`. O Nginx remove o prefixo antes de encaminhar a requisição.

## Desenvolvimento

O código Rust é montado em `/app` e compilado pelo entrypoint em cada reinicialização. Para testar:

```sh
docker compose -f docker-compose.dev.yml exec backend cargo test
```

## Produção

O Dockerfile compila um binário otimizado e executa a imagem de runtime sem toolchain Rust:

```sh
./scripts/create-production-envs.sh
docker compose -f docker-compose.prd.yml up -d --build
```

O PostgreSQL fica acessível ao backend pelo hostname `database`, mas não há implementação de persistência ou autenticação nesta base mínima. Hyper é uma biblioteca HTTP de baixo nível; roteamento avançado e middleware precisam ser construídos ou adicionados conforme o projeto.
