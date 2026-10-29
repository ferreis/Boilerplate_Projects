# Convenções do Projeto

## Seleção inicial do backend

- O boilerplate oferece `python`, `drogon` e `symfony` somente antes da inicialização.
- A escolha deve ser feita com `scripts/select-backend.sh <tipo>`.
- A seleção é destrutiva para a cópia atual: os outros backends e suas referências são removidos.
- Depois da seleção, o código escolhido fica diretamente em `backend/`.
- Depois da seleção, Dockerfile e entrypoint ficam diretamente em `docker/backend/`.
- Depois da seleção, o modelo de ambiente fica em `env/backend.dev.env`.
- O projeto gerado não deve manter `BACKEND_TYPE` nem mecanismo de troca dinâmica de backend.
- Todo backend do template deve respeitar `backend/CONTRACT.md` antes da seleção.

## Backend gerado

- O serviço Docker deve continuar se chamando `backend`: Python/Drogon atendem HTTP na porta `8000`; Symfony usa FastCGI (PHP-FPM) na porta `9000` com configuração Nginx selecionada pelo script.
- Não duplique os arquivos Docker Compose para cada linguagem.
- Não adicione `command` de runtime ao Compose; use `docker/backend/entrypoint.sh`.
- Não publique a porta `8000` diretamente no host em produção.
- PostgreSQL deve ser acessado internamente pelo hostname Docker `database`.

## Scripts

- Todo script novo deve ser criado na pasta `scripts/`.
- Scripts devem ter nomes descritivos e informar como são usados quando necessário.

## Arquivos de ambiente

Antes da seleção, cada opção possui seu próprio `env/backend.<tipo>.dev.env`.

Depois da seleção, o padrão obrigatório é:

```text
env/backend.dev.env
env/database.dev.env
env/frontend.dev.env
```

Arquivos padrão de produção não usam `.example`:

```text
env/backend.env
env/database.env
env/frontend.env
```

Para gerar os arquivos padrão a partir dos modelos, use `scripts/create-production-envs.sh`.

Arquivos de produção não devem conter valores versionados que sejam segredos.

### Padrão obrigatório de comentários

- Separe as variáveis por grupos lógicos.
- Cada grupo deve começar com um título de primeiro nível: `# Configuração de Autenticação`.
- Cada variável deve ter, logo acima, uma descrição de segundo nível.
- Use uma linha em branco entre grupos.
- Explique formato, unidade, valores aceitos, impacto de segurança e comportamento em produção quando forem relevantes.
- Preserve a mesma estrutura de grupos e comentários ao gerar o arquivo padrão; apenas os valores devem ser limpos.
