#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "==> skill supply-chain audit"

status=0

warn() {
  echo "WARN $*" >&2
  status=1
}

check_required_files() {
  local skill_dir
  while IFS= read -r skill_md; do
    skill_dir="$(dirname "${skill_md}")"
    [[ -f "${skill_dir}/agents/openai.yaml" ]] || warn "${skill_dir}: missing agents/openai.yaml"
  done < <(find . -mindepth 2 -maxdepth 2 -name SKILL.md -type f | sort)
}

check_learning_data_not_in_repo() {
  local matches
  matches="$(find . \
    \( -path './.git' -o -path './.serena' \) -prune -o \
    \( -name 'consent.md' -o -name '.skill-learning' -o -path './.skill-learning/*' \) -print)"
  if [[ -n "${matches}" ]]; then
    warn "local learning data must not be stored in this repo:"
    echo "${matches}" >&2
  fi
}

check_script_patterns() {
  local pattern
  pattern='(^|[^[:alnum:]_])(curl|wget|nc|ncat|scp|sftp|ftp|ssh|osascript|eval|base64)([[:space:]]|$)|exec[[:space:]]*\(|subprocess|os\.system|popen|shutil\.rmtree|chmod[[:space:]]+\+|rm[[:space:]]+-rf|git[[:space:]]+reset|git[[:space:]]+push|git[[:space:]]+clean|GITHUB_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_ACCESS_KEY|AWS_SECRET|PASSWORD[[:space:]]*=|SECRET[[:space:]]*=|TOKEN[[:space:]]*='

  local files=()
  while IFS= read -r file; do
    files+=("${file}")
  done < <(find . \
    \( -path './.git' -o -path './.serena' \) -prune -o \
    -type f \( -path '*/scripts/*' -o -name '*.sh' -o -name '*.py' \) -print | sort)

  if [[ ${#files[@]} -eq 0 ]]; then
    return 0
  fi

  local output
  output="$(grep -EIn "${pattern}" "${files[@]}" || true)"
  output="$(echo "${output}" | grep -Ev 'scripts/audit-skills\.sh:|scripts/validate\.sh:.*rm -rf "\$\{tmp_dir\}"|sync-skills\.sh:.*rsync|scripts/archive-source-evidence\.py:.*shutil\.copy2|java-service-code-generator/scripts/verify_fixtures\.py:.*subprocess|java-service-code-generator/scripts/verify_fixtures\.py:.*shutil|java-service-code-generator/scripts/verify_fixtures\.py:.*rmtree\(base_tmp\)|scripts/audit-skill-eval-fixtures\.py:.*skill eval fixture|scripts/validate-trigger-paths\.py:.*OK skill eval fixture self-test' || true)"

  if [[ -n "${output}" ]]; then
    warn "review high-risk script patterns:"
    echo "${output}" >&2
  fi
}

check_external_urls() {
  local count
  count="$(grep -RIE 'https?://' . \
    --exclude-dir .git \
    --exclude-dir .serena \
    --exclude '*.pyc' | wc -l | tr -d ' ' || true)"
  if [[ "${count}" != "0" ]]; then
    echo "INFO external URL references found: ${count}; ensure they are intentional and source-attributed."
    echo "INFO inspect with: grep -RInE 'https?://' . --exclude-dir .git --exclude-dir .serena"
  fi
}

check_required_files
check_learning_data_not_in_repo
check_script_patterns
check_external_urls

if [[ ${status} -ne 0 ]]; then
  echo "Skill audit completed with warnings." >&2
  exit "${status}"
fi

echo "Skill audit passed."
