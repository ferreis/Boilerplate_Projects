#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIRECTORY="$(cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
readonly PROJECT_NAME_PLACEHOLDER='{nome_projeto}'

print_usage() {
  printf 'Uso: %s <nome-do-projeto>\n' "$(basename -- "$0")"
  printf 'Substitui {nome_projeto} nos arquivos Docker e Nginx do projeto.\n'
  printf 'Use apenas letras minúsculas, números e hífens; o nome deve começar com uma letra.\n'
}

if (( $# != 1 )); then
  print_usage >&2
  exit 1
fi

project_name="$1"

if [[ ! "${project_name}" =~ ^[a-z][a-z0-9-]*$ ]]; then
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

processed_files=0

for relative_file_path in "${configuration_files[@]}"; do
  configuration_file="${PROJECT_DIRECTORY}/${relative_file_path}"

  if [[ ! -f "${configuration_file}" ]]; then
    continue
  fi

  if ! grep -Fq "${PROJECT_NAME_PLACEHOLDER}" "${configuration_file}"; then
    printf 'Sem marcador: %s\n' "${relative_file_path}"
    continue
  fi

  temporary_file="$(mktemp "${configuration_file}.tmp.XXXXXX")"
  sed "s|${PROJECT_NAME_PLACEHOLDER}|${project_name}|g" "${configuration_file}" > "${temporary_file}"
  mv "${temporary_file}" "${configuration_file}"

  printf 'Atualizado: %s\n' "${relative_file_path}"
  ((processed_files += 1))
done

if (( processed_files == 0 )); then
  printf 'Nenhum marcador %s foi encontrado.\n' "${PROJECT_NAME_PLACEHOLDER}" >&2
  exit 1
fi

printf 'Substituição concluída para o projeto: %s\n' "${project_name}"
