# Contrato dos backends

Todos os backends deste boilerplate devem respeitar este contrato para que possam ser trocados sem alterar Nginx, frontend ou topologia Docker.

## Contrato operacional

- o serviço Docker continua se chamando `backend`;
- o processo HTTP deve escutar em `0.0.0.0`;
- a porta interna padrão é `8000` e pode ser recebida por `BACKEND_PORT`;
- nenhum backend publica portas diretamente para o host;
- o Nginx é o único ponto de entrada externo;
- o PostgreSQL é acessível somente pela rede interna `databaseNet`;
- comandos de inicialização ficam em `docker/backend/<tipo>/entrypoint.sh`, não em `command` no Compose.

## Contrato HTTP mínimo

Cada implementação deve expor:

```http
GET /health
```

Resposta esperada:

```json
{"status":"ok"}
```

O Nginx remove o prefixo público `/{nome_projeto}/api/` antes de encaminhar a requisição. Assim, uma rota interna `/health` é publicada como `/{nome_projeto}/api/health`.

## Funcionalidades específicas

O contrato mínimo não significa que todas as implementações já tenham paridade funcional completa. Atualmente:

- `python`: inclui autenticação JWT e health check;
- `drogon`: base de API com health check;
- `symfony`: base de API com health check.

Ao portar uma feature para outro backend, preserve os contratos HTTP utilizados pelo frontend antes de trocar `BACKEND_TYPE` em uma aplicação que dependa dessa feature.
