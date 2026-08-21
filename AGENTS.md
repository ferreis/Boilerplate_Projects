# Convenções do Projeto

## Scripts

- Todo script novo deve ser criado na pasta `scripts/`.
- Scripts devem ter nomes descritivos e informar como são usados quando necessário.

## Arquivos de ambiente

- Os arquivos `env/*.dev.env` são o modelo de configuração do projeto.
- Arquivos padrão de produção não usam `.example`: use `env/backend.env`, `env/database.env` e equivalentes.
- Para gerar os arquivos padrão a partir dos modelos, use `scripts/create-production-envs.sh`.
- Arquivos de produção não devem conter valores versionados que sejam segredos.

### Padrão obrigatório de comentários

- Separe as variáveis por grupos lógicos.
- Cada grupo deve começar com um título de primeiro nível: `# Configuração de Autenticação`.
- Cada variável deve ter, logo acima, uma descrição de segundo nível: `## Chave usada para assinar os tokens JWT.`
- Use uma linha em branco entre grupos.
- Explique formato, unidade, valores aceitos, impacto de segurança e comportamento em produção quando forem relevantes.
- Preserve a mesma estrutura de grupos e comentários ao gerar o arquivo padrão; apenas os valores devem ser limpos.

Exemplo:

```env
# Configuração de Autenticação
## Chave usada para assinar os tokens JWT. Use ao menos 32 caracteres aleatórios.
JWT_SECRET=
```
