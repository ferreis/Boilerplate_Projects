# Convenções do Projeto

## Backends

- Os backends disponíveis ficam em `backend/<tipo>/`.
- Dockerfiles e comandos de inicialização ficam em `docker/backend/<tipo>/`.
- O backend selecionado é definido por `BACKEND_TYPE` na `.env` da raiz.
- Valores atualmente suportados: `python`, `drogon` e `symfony`.
- Todo backend deve respeitar `backend/CONTRACT.md`.
- O serviço Docker deve continuar se chamando `backend` e atender HTTP internamente na porta `8000`.
- Não duplique os arquivos Docker Compose para cada linguagem.
- Não adicione `command` de runtime ao Compose; use `entrypoint.sh`.

## Scripts

- Todo script novo deve ser criado na pasta `scripts/`.
- Scripts devem ter nomes descritivos e informar como são usados quando necessário.

## Arquivos de ambiente

- Os arquivos `env/*.dev.env` são o modelo de configuração do projeto.
- Backends utilizam o padrão `env/backend.<tipo>.dev.env`.
- Arquivos padrão de produção não usam `.example`: use `env/backend.<tipo>.env`, `env/database.env` e equivalentes.
- Para gerar os arquivos padrão, use `scripts/create-production-envs.sh`.
- Arquivos de produção não devem conter valores versionados que sejam segredos.

### Padrão obrigatório de comentários

- Separe as variáveis por grupos lógicos.
- Cada grupo deve começar com um título de primeiro nível: `# Configuração de Autenticação`.
- Cada variável deve ter, logo acima, uma descrição de segundo nível.
- Use uma linha em branco entre grupos.
- Explique formato, unidade, valores aceitos, impacto de segurança e comportamento em produção quando forem relevantes.
- Preserve a mesma estrutura de grupos e comentários ao gerar o arquivo padrão; apenas os valores devem ser limpos.

Exemplo:

```env
# Configuração de Autenticação
## Chave usada para assinar os tokens JWT. Use ao menos 32 caracteres aleatórios.
JWT_SECRET=
```
