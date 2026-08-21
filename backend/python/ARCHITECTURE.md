# Arquitetura do Backend

O backend é organizado por domínio/feature e segue uma separação inspirada em Clean Architecture e DDD.

A regra principal é manter regras de negócio e casos de uso independentes de FastAPI, banco de dados e bibliotecas de infraestrutura.

## Módulos atuais

### `authentication`

Domínio responsável por autenticação, sessão JWT e autorização por roles.

```text
authentication/
├── domain/
│   ├── entities/
│   ├── policies/
│   └── exceptions.py
├── application/
│   ├── dto/
│   ├── interfaces/
│   └── use_cases/
├── infrastructure/
│   ├── providers/
│   └── security/
└── presentation/
    ├── routes/
    ├── schemas/
    ├── dependencies.py
    └── middleware.py
```

### `system`

Contém endpoints técnicos da aplicação, como `/health`.

Esse módulo possui somente a camada necessária. Não são criadas camadas `domain`, `application` ou `infrastructure` vazias quando não existe responsabilidade para elas.

### `shared`

Contém responsabilidades transversais que não pertencem a um domínio específico, como carregamento de configuração e middlewares HTTP gerais.

## Direção das dependências

```text
presentation
     |
     v
application
     |
     v
domain

infrastructure ---> application interfaces / domain
```

### Domain

Não deve importar:

- FastAPI;
- Pydantic;
- PyJWT;
- bcrypt;
- SQLAlchemy;
- PostgreSQL;
- Redis;
- Celery;
- clientes HTTP;
- detalhes de configuração ou persistência.

### Application

Coordena os casos de uso e depende de contratos definidos em `application/interfaces`.

A aplicação não conhece a implementação concreta de JWT, bcrypt ou origem das credenciais.

### Infrastructure

Implementa os contratos necessários pelos casos de uso.

Atualmente existem adapters para:

- credenciais provenientes das variáveis de ambiente;
- verificação de senha com bcrypt;
- emissão e leitura de tokens JWT com PyJWT.

Quando persistência for adicionada ao backend, os models de banco e implementações concretas de repositories devem ser adicionados nesta camada.

Não existe repository atualmente porque o backend ainda não utiliza o PostgreSQL no código Python.

### Presentation

Contém FastAPI, schemas HTTP, cookies, status HTTP e conversão das exceções da aplicação/domínio para respostas HTTP.

As rotas não devem implementar regras de negócio.

## Composition root

`main.py` é o ponto de composição da aplicação.

É nele que:

1. as configurações são carregadas e validadas;
2. os adapters concretos são instanciados;
3. os casos de uso recebem suas dependências;
4. os middlewares são registrados;
5. os routers são adicionados ao FastAPI.

Isso mantém as implementações concretas fora dos casos de uso.

## Testes

Os testes acompanham a estrutura do backend:

```text
tests/
├── authentication/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── integration/
└── shared/
```

Testes de `domain` e `application` devem evitar FastAPI e infraestrutura sempre que possível.

Testes de integração podem validar adapters, middleware e contratos HTTP.

## Novos domínios

Ao adicionar uma nova feature:

1. identifique primeiro as responsabilidades e regras reais;
2. crie apenas as camadas necessárias;
3. coloque regras puras em `domain`;
4. crie casos de uso pequenos em `application/use_cases`;
5. defina interfaces somente quando existir uma dependência que precise ser invertida;
6. coloque implementações concretas em `infrastructure`;
7. mantenha FastAPI e Pydantic em `presentation`;
8. adicione testes próximos ao nível arquitetural que está sendo validado.

Evite criar services genéricos gigantes, repositories sem persistência real ou classes vazias apenas para preencher a estrutura.
