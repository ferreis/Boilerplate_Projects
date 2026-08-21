# Backends disponíveis

O projeto suporta múltiplas implementações de backend sem alterar o Nginx ou o frontend.

```text
backend/
├── CONTRACT.md
├── python/
├── drogon/
└── symfony/
```

A escolha é feita por `BACKEND_TYPE`.

```env
BACKEND_TYPE=python
```

Valores aceitos:

- `python` — FastAPI;
- `drogon` — C++/Drogon;
- `symfony` — PHP/Symfony.

Também é possível usar:

```bash
./scripts/select-backend.sh python
./scripts/select-backend.sh drogon
./scripts/select-backend.sh symfony
```

O Compose resolve dinamicamente:

```text
backend/${BACKEND_TYPE}
docker/backend/${BACKEND_TYPE}/Dockerfile
env/backend.${BACKEND_TYPE}.dev.env
env/backend.${BACKEND_TYPE}.env
```

Independentemente da implementação, o container continua se chamando `backend` e utiliza a porta interna `8000`.

Consulte `CONTRACT.md` antes de adicionar um novo backend.
