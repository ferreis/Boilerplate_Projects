# Backends disponíveis no template

Esta pasta existe em formato multi-backend somente antes da inicialização do projeto.

As opções disponíveis são:

- `python` — FastAPI;
- `drogon` — C++/Drogon;
- `symfony` — PHP/Symfony;
- `hyper` — Rust/Hyper.

Escolha uma implementação executando na raiz:

```bash
./scripts/select-backend.sh python
```

```bash
./scripts/select-backend.sh drogon
```

```bash
./scripts/select-backend.sh symfony
```

```bash
./scripts/select-backend.sh hyper
```

O script não apenas marca uma opção. Ele remove as implementações descartadas e promove a escolhida para a própria pasta `backend/`.

Depois da execução, esta estrutura:

```text
backend/
├── CONTRACT.md
├── README.md
├── python/
├── drogon/
├── symfony/
└── hyper/
```

é substituída pelo conteúdo do backend escolhido:

```text
backend/
├── README.md
└── ... implementação selecionada
```

O mesmo processo ocorre em `docker/backend/` e nos arquivos `env/backend.*.dev.env`.

Depois da seleção, não existe mais mecanismo de troca de backend no projeto gerado. Para escolher outra implementação, utilize uma nova cópia do boilerplate ou reverta a seleção pelo Git.

Todas as opções do template devem respeitar `CONTRACT.md` antes da seleção.
