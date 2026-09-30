#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIRECTORY="$(cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
readonly PROJECT_NAME_PLACEHOLDER='{nome_projeto}'

print_usage() {
  printf 'Uso: %s <nome-do-projeto>\n' "$(basename -- "$0")"
  printf 'Atualiza nomes de serviços, containers, redes, Nginx e caminhos base do projeto.\n'
  printf 'Use apenas letras minúsculas, números e hífens; o nome deve começar com letra ou número.\n'
}

if (( $# != 1 )); then
  print_usage >&2
  exit 1
fi

project_name="$1"

if [[ ! "${project_name}" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  printf 'Nome de projeto inválido: %s\n' "${project_name}" >&2
  print_usage >&2
  exit 1
fi

configuration_files=(
  'docker-compose.dev.yml'
  'docker-compose.prd.yml'
  'docker/nginx/nginx.dev.conf'
  'docker/nginx/nginx.prd.conf'
)

for relative_file_path in "${configuration_files[@]}"; do
  if [[ ! -f "${PROJECT_DIRECTORY}/${relative_file_path}" ]]; then
    printf 'Arquivo obrigatório não encontrado: %s\n' "${relative_file_path}" >&2
    exit 1
  fi
done

current_project_name="$(
  sed -nE 's#^[[:space:]]*PROJECT_NAME:[[:space:]]*"?([a-z0-9][a-z0-9-]*)"?[[:space:]]*$#\1#p' \
    "${PROJECT_DIRECTORY}/docker-compose.prd.yml" | head -n 1
)"

if [[ -z "${current_project_name}" ]]; then
  current_project_name="$(
    sed -nE 's#^[[:space:]]*BASE_URL:[[:space:]]*/([a-z0-9][a-z0-9-]*)/api[[:space:]]*$#\1#p' \
      "${PROJECT_DIRECTORY}/docker-compose.prd.yml" | head -n 1
  )"
fi

rewrite_compose() {
  local configuration_file="$1"
  local environment="$2"
  local temporary_file
  local with_container_names

  temporary_file="$(mktemp "${configuration_file}.tmp.XXXXXX")"
  with_container_names="$(mktemp "${configuration_file}.containers.XXXXXX")"

  sed -E \
    -e '/^    container_name:[[:space:]]*/d' \
    -e "s,^([[:space:]]*)(nginx|database|backend|frontend)(-[a-z0-9-]+-(dev|prd))?:([[:space:]]*)$,\\1\\2-${project_name}-${environment}:\\5," \
    -e "s,^([[:space:]]*-[[:space:]]*)(nginx|database|backend|frontend)(-[a-z0-9-]+-(dev|prd))?([[:space:]]*)$,\\1\\2-${project_name}-${environment}\\5," \
    -e "s,^([[:space:]]*)(edgeNet|frontendNet|backendNet|databaseNet)(-[a-z0-9-]+-(dev|prd))?:([[:space:]]*)$,\\1\\2-${project_name}-${environment}:\\5," \
    -e "s,^([[:space:]]*-[[:space:]]*)(edgeNet|frontendNet|backendNet|databaseNet)(-[a-z0-9-]+-(dev|prd))?([[:space:]]*)$,\\1\\2-${project_name}-${environment}\\5," \
    -e "s,^([[:space:]]*BASE_URL:[[:space:]]*).*$,\\1/${project_name}/api," \
    -e "s,^([[:space:]]*VITE_BASE_PATH:[[:space:]]*).*$,\\1/${project_name}/," \
    -e "s,^([[:space:]]*PROJECT_NAME:[[:space:]]*).*$,\\1\"${project_name}\"," \
    "${configuration_file}" > "${temporary_file}"

  awk -v project="${project_name}" -v environment="${environment}" '
    {
      print
      if ($0 == "  nginx-" project "-" environment ":" || $0 == "  database-" project "-" environment ":" || $0 == "  backend-" project "-" environment ":" || $0 == "  frontend-" project "-" environment ":") {
        name = substr($0, 3, length($0) - 3)
        print "    container_name: " name
      }
    }
  ' "${temporary_file}" > "${with_container_names}"

  cat "${with_container_names}" > "${configuration_file}"
  rm -f "${temporary_file}" "${with_container_names}"
}

rewrite_nginx() {
  local configuration_file="$1"
  local environment="$2"
  local temporary_file

  temporary_file="$(mktemp "${configuration_file}.tmp.XXXXXX")"

  sed -E \
    -e "s,^([[:space:]]*server[[:space:]]+)backend(-[a-z0-9-]+-(dev|prd))?(:8000.*)$,\\1backend-${project_name}-${environment}\\4," \
    -e "s,^([[:space:]]*server[[:space:]]+)frontend(-[a-z0-9-]+-(dev|prd))?(:5173.*)$,\\1frontend-${project_name}-${environment}\\4," \
    -e "s,/\\{nome_projeto\\},/${project_name},g" \
    "${configuration_file}" > "${temporary_file}"

  if [[ -n "${current_project_name}" && "${current_project_name}" != "${project_name}" ]]; then
    sed -E \
      "/^[[:space:]]*(location|return|try_files)[[:space:]]/ s,/${current_project_name}(/|[[:space:]]|;),/${project_name}\\1,g" \
      "${temporary_file}" > "${configuration_file}"
    rm -f "${temporary_file}"
  else
    cat "${temporary_file}" > "${configuration_file}"
    rm -f "${temporary_file}"
  fi
}

rewrite_compose "${PROJECT_DIRECTORY}/docker-compose.dev.yml" 'dev'
rewrite_compose "${PROJECT_DIRECTORY}/docker-compose.prd.yml" 'prd'
rewrite_nginx "${PROJECT_DIRECTORY}/docker/nginx/nginx.dev.conf" 'dev'
rewrite_nginx "${PROJECT_DIRECTORY}/docker/nginx/nginx.prd.conf" 'prd'

printf 'Arquivos atualizados:\n'
for relative_file_path in "${configuration_files[@]}"; do
  printf '  - %s\n' "${relative_file_path}"
done
printf 'Substituição concluída para o projeto: %s\n' "${project_name}"
