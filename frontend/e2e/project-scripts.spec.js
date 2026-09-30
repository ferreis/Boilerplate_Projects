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
    expect(firstPass['docker-compose.dev.yml']).toContain('"${NGINX_HTTP_PORT:-80}:80"')
    expect(firstPass['docker-compose.dev.yml']).toContain('"${NGINX_HTTPS_PORT:-443}:443"')

    expect(firstPass['docker-compose.prd.yml']).toContain('nginx-2core-app-prd:')
    expect(firstPass['docker-compose.prd.yml']).toContain('container_name: backend-2core-app-prd')
    expect(firstPass['docker-compose.prd.yml']).toContain('PROJECT_NAME: "2core-app"')
    expect(firstPass['docker-compose.prd.yml']).toContain('- backendNet-2core-app-prd')

    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('server backend-2core-app-dev:8000;')
    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('server frontend-2core-app-dev:5173;')
    expect(firstPass['docker/nginx/nginx.prd.conf']).toContain('server backend-2core-app-prd:8000 resolve;')
    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('location = /2core-app/api {')
    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('return 308 /2core-app/api/;')
    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('location /2core-app/api/ {')
    expect(firstPass['docker/nginx/nginx.dev.conf']).toContain('proxy_pass http://backend_upstream/;')

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

test('preserva caminhos de sistema do Nginx ao trocar nomes que coincidem com diretórios Unix', () => {
  for (const protectedName of ['etc', 'var', 'usr']) {
    const root = createFixture()

    try {
      runScript(root, 'scripts/replace-project-name.sh', protectedName)
      runScript(root, 'scripts/replace-project-name.sh', 'ebisu')

      const developmentNginx = read(root, 'docker/nginx/nginx.dev.conf')
      const productionNginx = read(root, 'docker/nginx/nginx.prd.conf')

      expect(developmentNginx).toContain('include /etc/nginx/mime.types;')
      expect(developmentNginx).toContain('ssl_certificate /etc/nginx/ssl/nginx.crt;')
      expect(developmentNginx).toContain('ssl_certificate_key /etc/nginx/ssl/nginx.key;')
      expect(productionNginx).toContain('pid /var/run/nginx.pid;')
      expect(productionNginx).toContain('error_log /var/log/nginx/error.log warn;')
      expect(productionNginx).toContain('access_log /var/log/nginx/access.log main;')
      expect(productionNginx).toContain('root /usr/share/nginx/html;')
      expect(productionNginx).toContain('include /etc/nginx/mime.types;')
      expect(productionNginx).toContain('ssl_certificate /etc/nginx/ssl/nginx.crt;')
      expect(productionNginx).toContain('ssl_certificate_key /etc/nginx/ssl/nginx.key;')
      expect(productionNginx).toContain('https://${host}__HTTPS_PORT_SUFFIX__${request_uri}')
      expect(productionNginx).toContain('location = /ebisu/api {')
      expect(productionNginx).toContain('return 308 /ebisu/api/;')

      expect(developmentNginx).not.toContain('/ebisu/nginx/mime.types')
      expect(productionNginx).not.toContain('/ebisu/run/nginx.pid')
      expect(productionNginx).not.toContain('/ebisu/share/nginx/html')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
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
