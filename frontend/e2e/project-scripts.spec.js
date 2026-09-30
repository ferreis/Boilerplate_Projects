import { execFileSync } from 'node:child_process'
import { cpSync, mkdtempSync, mkdirSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { expect, test } from '@playwright/test'

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')

const fixturePaths = [
  'AGENTS.md',
  'README.md',
  'backend',
  'docker/backend',
  'docker/frontend',
  'docker/nginx',
  'env',
  'scripts/select-backend.sh',
  'scripts/replace-project-name.sh',
  'scripts/templates',
  'docker-compose.dev.yml',
  'docker-compose.prd.yml',
]

function createFixture() {
  const root = mkdtempSync(join(tmpdir(), 'boilerplate-project-scripts-'))

  for (const relativePath of fixturePaths) {
    const source = join(repositoryRoot, relativePath)
    const destination = join(root, relativePath)
    mkdirSync(dirname(destination), { recursive: true })
    cpSync(source, destination, { recursive: true })
  }

  return root
}

function runScript(root, relativePath, ...args) {
  return execFileSync('bash', [join(root, relativePath), ...args], {
    cwd: root,
    encoding: 'utf8',
    stdio: 'pipe',
  })
}

function read(root, relativePath) {
  return readFileSync(join(root, relativePath), 'utf8')
}

test('remove __SELECT_BACKEND__ mesmo quando o projeto é renomeado antes da seleção', () => {
  const root = createFixture()

  try {
    runScript(root, 'scripts/replace-project-name.sh', 'ebisu')
    expect(read(root, 'docker-compose.dev.yml')).toContain('__SELECT_BACKEND__')

    runScript(root, 'scripts/select-backend.sh', 'python')

    const developmentCompose = read(root, 'docker-compose.dev.yml')
    const productionCompose = read(root, 'docker-compose.prd.yml')

    expect(developmentCompose).not.toContain('__SELECT_BACKEND__')
    expect(productionCompose).not.toContain('__SELECT_BACKEND__')
    expect(developmentCompose).toContain('backend-ebisu-dev:')
    expect(developmentCompose).toContain('dockerfile: docker/backend/Dockerfile')
    expect(developmentCompose).toContain('- ./backend:/app')
    expect(developmentCompose).toContain('- ./env/backend.dev.env')
    expect(productionCompose).toContain('backend-ebisu-prd:')
    expect(productionCompose).toContain('- ./env/backend.env')
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})

test('renomeia serviços, containers, redes e Nginx de forma idempotente', () => {
  const root = createFixture()

  try {
    runScript(root, 'scripts/select-backend.sh', 'python')
    runScript(root, 'scripts/replace-project-name.sh', 'ebisu')
    runScript(root, 'scripts/replace-project-name.sh', '2core-app')

    const files = [
      'docker-compose.dev.yml',
      'docker-compose.prd.yml',
      'docker/nginx/nginx.dev.conf',
      'docker/nginx/nginx.prd.conf',
    ]
    const firstPass = Object.fromEntries(files.map((file) => [file, read(root, file)]))

    expect(firstPass['docker-compose.dev.yml']).toContain('nginx-2core-app-dev:')
    expect(firstPass['docker-compose.dev.yml']).toContain('container_name: nginx-2core-app-dev')
    expect(firstPass['docker-compose.dev.yml']).toContain('- frontend-2core-app-dev')
    expect(firstPass['docker-compose.dev.yml']).toContain('database-2core-app-dev:')
    expect(firstPass['docker-compose.dev.yml']).toContain('- edgeNet-2core-app-dev')
    expect(firstPass['docker-compose.dev.yml']).toContain('BASE_URL: /2core-app/api')
    expect(firstPass['docker-compose.dev.yml']).toContain('VITE_BASE_PATH: /2core-app/')

    expect(firstPass['docker-compose.prd.yml']).toContain('nginx-2core-app-prd:')
    expect(firstPass['docker-compose.prd.yml']).toContain('container_name: backend-2core-app-prd')
    expect(firstPass['docker-compose.prd.yml']).toContain('PROJECT_NAME: "2core-app"')
    expect(firstPass['docker-compose.prd.yml']).toContain('- backendNet-2core-app-prd')

    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('server backend-2core-app-dev:8000;')
    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('server frontend-2core-app-dev:5173;')
    expect(firstPass['docker/nginx/nginx.prd.conf']).toContain('server backend-2core-app-prd:8000 resolve;')

    for (const content of Object.values(firstPass)) {
      expect(content).not.toContain('ebisu')
      expect(content).not.toContain('-dev-dev')
      expect(content).not.toContain('-prd-prd')
    }

    runScript(root, 'scripts/replace-project-name.sh', '2core-app')

    for (const file of files) {
      expect(read(root, file)).toBe(firstPass[file])
    }
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})

test('rejeita caracteres fora da lista permitida', () => {
  const root = createFixture()

  try {
    expect(() => runScript(root, 'scripts/replace-project-name.sh', 'nome;touch-invalido')).toThrow()
    expect(read(root, 'docker-compose.dev.yml')).toContain('{nome_projeto}')
  } finally {
    rmSync(root, { recursive: true, force: true })
  }
})
