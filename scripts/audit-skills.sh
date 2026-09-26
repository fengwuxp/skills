#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "==> skill supply-chain audit"

status=0

python3 scripts/audit-skill-security.py --root . --ignore-local-generated-pyc

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

check_no_nested_skills() {
  local matches
  matches="$(find . -mindepth 3 -type f -name SKILL.md \
    -not -path './.git/*' \
    -not -path './.serena/*' | sort)"
  if [[ -n "${matches}" ]]; then
    warn "skill subdirectories must not contain nested SKILL.md files because Codex may auto-discover them:"
    echo "${matches}" >&2
  fi
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
  output="$(echo "${output}" | grep -Ev 'scripts/audit-skills\.sh:|scripts/audit-skill-security\.py:|scripts/test-audit-skill-security\.py:|scripts/validate\.sh:.*rm -rf "\$\{tmp_dir\}"|scripts/validate-superpowers-install\.sh:.*rm -rf "\$\{tmp\}"|sync-skills\.sh:.*rsync|scripts/archive-source-evidence\.py:.*shutil\.copy2|java-service-code-generator/scripts/verify_fixtures\.py:.*subprocess|java-service-code-generator/scripts/verify_fixtures\.py:.*shutil|java-service-code-generator/scripts/verify_fixtures\.py:.*rmtree\(base_tmp\)|scripts/audit-skill-eval-fixtures\.py:.*skill eval fixture|scripts/validate-trigger-paths\.py:.*OK skill eval fixture self-test|scripts/validate-trigger-paths\.py:.*AI 原型/eval 到 PRD-Lite/OpenSpec/Harness/GSD/CAD|scripts/validate-trigger-paths\.py:.*从 AI 原型/eval 到 PRD-Lite、OpenSpec、GSD/CAD 编排准入结论|scripts/validate-trigger-paths\.py:.*AI 原型 / eval / dogfooding|scripts/validate-trigger-paths\.py:.*用 AI Native 研发流程设计一套从 AI 原型/eval|scripts/validate-trigger-paths\.py:.*用 AI Native 研发流程编排设计一套从 AI 原型/eval' || true)"

  local reviewed_consumer_patterns
  reviewed_consumer_patterns='^\./scripts/(prepare-skill-consumer-eval|test-prepare-skill-consumer-eval)\.py:[0-9]+:import subprocess$|^\./scripts/prepare-skill-consumer-eval\.py:[0-9]+:[[:space:]]*(result = subprocess\.run\(command, cwd=ROOT, env=environment,|stdout=subprocess\.PIPE, stderr=subprocess\.STDOUT, text=True\))$|^\./scripts/test-prepare-skill-consumer-eval\.py:[0-9]+:[[:space:]]*(with (self\.subTest\(output=output\), )?patch\.object\(self\.module\.subprocess, "run"(, (return_value=result|wraps=subprocess\.run))?\) as run:|result = subprocess\.CompletedProcess\(\[\], 1, "controlled failure\\n"\)|(failed|passed) = subprocess\.run\(checker, cwd=self\.output, capture_output=True, text=True\))$'
  output="$(echo "${output}" | grep -Ev "${reviewed_consumer_patterns}" || true)"

  # These two fixture commands only compile and run the checked-in Java sample.
  local reviewed_java_fixture_patterns
  reviewed_java_fixture_patterns='^\./scripts/test-prepare-skill-consumer-eval\.py:[0-9]+:[[:space:]]*compilation = subprocess\.run\(\["javac", "-d", str\(classes\), \*sources\], capture_output=True, text=True\)$|^\./scripts/test-prepare-skill-consumer-eval\.py:[0-9]+:[[:space:]]*execution = subprocess\.run\(\["java", "-cp", str\(classes\), "sample\.OrderLabelTests"\], capture_output=True, text=True\)$'
  output="$(echo "${output}" | grep -Ev "${reviewed_java_fixture_patterns}" || true)"

  # Reviewed offline YAML reader: fixed local Ruby argv, no shell/network/writes.
  # Pin both caller and parser; any change restores the required review.
  local invocation_caller_sha invocation_parser_sha
  if [[ -f scripts/check-skill-admission.py && -f scripts/read-agent-invocation-policy.rb ]]; then
    invocation_caller_sha="$(shasum -a 256 scripts/check-skill-admission.py)"
    invocation_parser_sha="$(shasum -a 256 scripts/read-agent-invocation-policy.rb)"
    if [[ "${invocation_caller_sha%% *}" == "ba9d38dc730b700c77ce4fc809eac753152ff7f0e54ea199f5379873e633867b" \
       && "${invocation_parser_sha%% *}" == "d4b9731a7038b8b863463f03b9c5859c563a4297edbb5193356c8841a0afcaf1" ]]; then
      output="$(printf '%s\n' "${output}" | awk -v prefix='./scripts/check-skill-admission.py:' 'index($0, prefix) != 1')"
    fi
  fi

  # 已审查的分发回归只执行暂存目录中的固定 Python 脚本；内容变化后重新复核。
  local distributed_test_sha
  if [[ -f scripts/test-distributed-skill-bundles.py ]]; then
    distributed_test_sha="$(shasum -a 256 scripts/test-distributed-skill-bundles.py)"
    if [[ "${distributed_test_sha%% *}" == "c01dcd522b80562549c003c07b61ce73e2f02c2c82642c6335294de01fbcc855" ]]; then
      output="$(printf '%s\n' "${output}" | awk -v prefix='./scripts/test-distributed-skill-bundles.py:' 'index($0, prefix) != 1')"
    fi
  fi

  # Reviewed historical pilots are never executed by validation. The runner still
  # requires separate model/network authorization. Any file edit restores review.
  # The supply-chain scanner above continues to inspect both complete files.
  local reviewed_sha reviewed_path actual_sha
  while read -r reviewed_sha reviewed_path; do
    [[ -f "${reviewed_path}" ]] || continue
    actual_sha="$(shasum -a 256 "${reviewed_path}")"
    if [[ "${actual_sha%% *}" == "${reviewed_sha}" ]]; then
      output="$(printf '%s\n' "${output}" | awk -v prefix="./${reviewed_path}:" 'index($0, prefix) != 1')"
    fi
  done <<'REVIEWED_PILOTS'
4cd0cc51f343b35a9ab7007514fb440a7029ccbbddb64c0f8d7ce0cc5d7224b7 docs/reviews/2026-09-09-learning-behavior-pilot/prepare.py
a94df8997bffa46200c84b8628bee07cf4d7158799147c0d2fa395b8568e724d docs/reviews/2026-09-09-learning-behavior-pilot/run-pilot.py
REVIEWED_PILOTS

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
check_no_nested_skills
check_learning_data_not_in_repo
check_script_patterns
check_external_urls

if [[ ${status} -ne 0 ]]; then
  echo "Skill audit completed with warnings." >&2
  exit "${status}"
fi

echo "Skill audit passed."
