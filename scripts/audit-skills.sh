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
  local url_lines
  url_lines="$(grep -RIE 'https?://' . \
    --exclude-dir .git \
    --exclude-dir .serena \
    --exclude '*.pyc' || true)"
  local line_count
  line_count="$(printf '%s\n' "${url_lines}" | sed '/^$/d' | wc -l | tr -d ' ')"
  local unique_urls
  unique_urls="$(printf '%s\n' "${url_lines}" | grep -Eoh 'https?://[^[:space:]`)"]+' | sort -u || true)"
  local unique_count
  unique_count="$(printf '%s\n' "${unique_urls}" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [[ "${line_count}" != "0" ]]; then
    echo "INFO external URL reference lines found: ${line_count}; unique external URLs: ${unique_count}; ensure they are intentional and source-attributed."
    echo "INFO inspect with: grep -RInE 'https?://' . --exclude-dir .git --exclude-dir .serena"
  fi

  local high_risk_urls
  high_risk_urls="$(grep -RIEoh 'https?://[^[:space:]`)"]*(nacha|visa|mastercard|stripe|adyen|marqeta|highnote|formance|docs\.aws\.amazon|learn\.microsoft|docs\.stripe|docs\.adyen|docs\.highnote|docs\.formance|api|sdk|rules|regulat|pci|ach|bank|payment|issuing|acquiring|dispute|fraud)[^[:space:]`)"]*' . \
    --exclude-dir .git \
    --exclude-dir .serena \
    --exclude '*.pyc' | sort -u || true)"
  local high_risk_count
  high_risk_count="$(printf '%s\n' "${high_risk_urls}" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [[ "${high_risk_count}" != "0" ]]; then
    echo "INFO unique freshness-sensitive external URLs found: ${high_risk_count}; current task conclusions must re-verify official/current sources."
  fi

  local freshness_text
  freshness_text="$(grep -RIE '外部知识时效性门禁|不代表来源仍然最新可用|不把读取日期当成当前核验日期|最新公开来源|最新官方来源|项目 lockfile|本地依赖树|核验日期|确认方' \
    README.md AGENTS.md product-architecture-expert senior-software-architect scripts \
    --exclude-dir .git \
    --exclude-dir .serena \
    --exclude '*.pyc' || true)"
  for required in \
    "外部知识时效性门禁" \
    "不代表来源仍然最新可用" \
    "不把读取日期当成当前核验日期" \
    "核验日期" \
    "确认方"; do
    if [[ "${freshness_text}" != *"${required}"* ]]; then
      warn "freshness-sensitive URL guard missing required term: ${required}"
    fi
  done
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
