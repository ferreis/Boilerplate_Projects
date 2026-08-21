# Convenções do Projeto

## Backend

- O código da API fica em `backend/`.
- O Dockerfile e o comando de inicialização ficam em `docker/backend/`.
- O serviço Docker deve continuar se chamando `backend` e atender HTTP internamente na porta `8000`.
- Não adicione `command` de runtime ao Docker Compose; use `docker/backend/entrypoint.sh`.
- Não publique a porta do backend diretamente no host em produção.
- O PostgreSQL deve ser acessado pelo hostname Docker `database` através da rede interna.
- Preserve a arquitetura e as convenções documentadas dentro de `backend/`.

## Scripts

- Todo script novo deve ser criado na pasta `scripts/`.
- Scripts devem ter nomes descritivos e informar como são usados quando necessário.

## Arquivos de ambiente

- `env/backend.dev.env`, `env/database.dev.env` e `env/frontend.dev.env` são os modelos de desenvolvimento.
- Arquivos padrão de produção não usam `.example`: use `env/backend.env`, `env/database.env` e equivalentes.
- Para gerar os arquivos padrão a partir dos modelos, use `scripts/create-production-envs.sh`.
- Arquivos de produção não devem conter valores versionados que sejam segredos.

### Padrão obrigatório de comentários

- Separe as variáveis por grupos lógicos.
- Cada grupo deve começar com um título de primeiro nível: `# Configuração de Autenticação`.
- Cada variável deve ter, logo acima, uma descrição de segundo nível.
- Use uma linha em branco entre grupos.
- Explique formato, unidade, valores aceitos, impacto de segurança e comportamento em produção quando forem relevantes.
- Preserve a mesma estrutura de grupos e comentários ao gerar o arquivo padrão; apenas os valores devem ser limpos.
