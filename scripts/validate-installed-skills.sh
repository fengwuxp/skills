#!/usr/bin/env bash
set -euo pipefail

# Input: repository top-level skills and $CODEX_HOME/skills.
# Output: content and executable-bit differences on stderr; success summary on stdout.
# Writes/network: none. Any missing, stale, or mode-drifted managed skill returns non-zero.

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"
TARGET_ROOT="${CODEX_HOME_DIR}/skills"
status=0

fail() {
  echo "FAIL $*" >&2
  status=1
}

while IFS= read -r skill_md; do
  source_dir="$(dirname "${skill_md}")"
  skill_name="$(basename "${source_dir}")"
  target_dir="${TARGET_ROOT}/${skill_name}"

  if [[ ! -f "${target_dir}/SKILL.md" ]]; then
    fail "installed skill missing: ${target_dir}"
    continue
  fi

  differences="$(diff -qr \
    -x '.DS_Store' \
    -x '.idea' \
    -x '__pycache__' \
    -x '*.pyc' \
    "${source_dir}" "${target_dir}" || true)"
  if [[ -n "${differences}" ]]; then
    fail "installed skill differs: ${skill_name}"
    echo "${differences}" >&2
  fi

  while IFS= read -r -d '' source_file; do
    case "${source_file}" in
      */.DS_Store|*/.idea/*|*/__pycache__/*|*.pyc)
        continue
        ;;
    esac
    relative_path="${source_file#"${source_dir}/"}"
    target_file="${target_dir}/${relative_path}"
    if [[ ! -f "${target_file}" ]]; then
      continue
    fi
    if { [[ -x "${source_file}" ]] && [[ ! -x "${target_file}" ]]; } \
      || { [[ ! -x "${source_file}" ]] && [[ -x "${target_file}" ]]; }; then
      fail "installed executable bit differs: ${skill_name}/${relative_path}"
    fi
  done < <(find "${source_dir}" -type f -print0)
done < <(find "${ROOT_DIR}" -mindepth 2 -maxdepth 2 -name SKILL.md -type f | sort)

for retired in wind-project-coding-conventions delivery-collab huaxia-wisdom; do
  if [[ -e "${TARGET_ROOT}/${retired}" ]]; then
    fail "retired skill remains installed: ${TARGET_ROOT}/${retired}"
  fi
done

if [[ ${status} -ne 0 ]]; then
  exit "${status}"
fi

echo "OK installed skills match repository"
