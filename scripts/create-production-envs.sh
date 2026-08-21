#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIRECTORY="$(cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
readonly ENVIRONMENT_DIRECTORY="${PROJECT_DIRECTORY}/env"

overwrite_existing_files=false

print_usage() {
  printf 'Uso: %s [--force]\n' "$(basename -- "$0")"
  printf 'Cria arquivos env de produ\303\247\303\243o a partir dos arquivos *.dev.env, mantendo coment\303\241rios e removendo todos os valores.\n'
}

for command_argument in "$@"; do
  case "${command_argument}" in
    --force)
      overwrite_existing_files=true
      ;;
    --help|-h)
      print_usage
      exit 0
      ;;
    *)
      printf 'Argumento inv\303\241lido: %s\n' "${command_argument}" >&2
      print_usage >&2
      exit 1
      ;;
  esac
done

shopt -s nullglob
source_environment_files=("${ENVIRONMENT_DIRECTORY}"/*.dev.env)
shopt -u nullglob

if (( ${#source_environment_files[@]} == 0 )); then
  printf 'Nenhum arquivo *.dev.env foi encontrado em %s.\n' "${ENVIRONMENT_DIRECTORY}" >&2
  exit 1
fi

for source_environment_file in "${source_environment_files[@]}"; do
  source_filename="$(basename -- "${source_environment_file}")"
  target_filename="${source_filename%.dev.env}.env"
  target_environment_file="${ENVIRONMENT_DIRECTORY}/${target_filename}"

  if [[ -e "${target_environment_file}" && "${overwrite_existing_files}" != true ]]; then
    printf 'O arquivo %s j\303\241 existe. Execute com --force para substitu\303\255-lo.\n' "${target_environment_file}" >&2
    exit 1
  fi
done

for source_environment_file in "${source_environment_files[@]}"; do
  source_filename="$(basename -- "${source_environment_file}")"
  target_filename="${source_filename%.dev.env}.env"
  target_environment_file="${ENVIRONMENT_DIRECTORY}/${target_filename}"
  temporary_environment_file="$(mktemp "${target_environment_file}.tmp.XXXXXX")"

  awk '
    /^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*=.*/ {
      assignment_position = index($0, "=")
      print substr($0, 1, assignment_position)
      next
    }
    { print }
  ' "${source_environment_file}" > "${temporary_environment_file}"

  mv "${temporary_environment_file}" "${target_environment_file}"
  printf 'Criado: %s\n' "${target_environment_file}"
done
