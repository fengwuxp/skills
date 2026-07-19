#!/usr/bin/env bash
set -euo pipefail

# Input: current Codex installation, its configured provider, and this repository.
# Output: final responses under --output-dir (default: /tmp/wise-agent-smoke-<timestamp>).
# Writes: output directory only. Network: codex exec may call the configured provider.
# Failure: exits non-zero when installed Skills differ from the repository or a response misses the contract.

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="all"
OUTPUT_DIR="/tmp/wise-agent-smoke-$(date +%Y%m%d-%H%M%S)"
RUNS=1

assert_product() {
  local file="$1" term
  for term in "事实" "推断" "待确认" "验收"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_no_orchestration "${file}"
}

assert_engineering() {
  local file="$1" term
  for term in "严重级别" "证据" "测试" "残余风险"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_no_orchestration "${file}"
}

assert_any() {
  local file="$1" term
  shift
  for term in "$@"; do
    if grep -Fq "${term}" "${file}"; then
      return 0
    fi
  done
  return 1
}

assert_none() {
  local file="$1" term
  shift
  for term in "$@"; do
    if grep -Fq "${term}" "${file}"; then
      return 1
    fi
  done
}

assert_no_orchestration() {
  assert_none "$1" "wise-agent" "知止者" "SDLC" "Goal" "Loop" "Worker" "Checker" "Harness"
}

assert_superpowers_product() {
  local file="$1" term
  for term in "知止者" "brainstorming" "grill-me"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "不进入工程计划" "暂不写工程计划" "不生成工程计划" "先不写工程计划" || return 1
}

assert_superpowers_debugging() {
  local file="$1" term
  for term in "知止者"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "systematic-debugging" "系统化调试" "根因" || return 1
  assert_any "${file}" "test-driven-development" "TDD" || return 1
  assert_any "${file}" "verification-before-completion" "新鲜" || return 1
}

assert_superpowers_git() {
  local file="$1" term
  for term in "Git" "worktree"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "未授权" "不允许" "不得" "禁止" || return 1
  if grep -Eq '(^|[。；[:space:]])(允许|可以)[^。；]*(commit|push|PR|worktree)' "${file}"; then
    return 1
  fi
}

assert_lightweight() {
  local file="$1" chars
  [[ -s "${file}" ]] || return 1
  assert_any "${file}" "修改" "更正" "回读" || return 1
  assert_no_orchestration "${file}" || return 1
  chars="$(wc -m < "${file}")"
  [[ "${chars}" -le 220 ]]
}

assert_simple_wording() {
  local file="$1" chars
  [[ -s "${file}" ]] || return 1
  assert_no_orchestration "${file}" || return 1
  chars="$(wc -m < "${file}")"
  [[ "${chars}" -le 220 ]]
}

assert_state_resume() {
  local file="$1" term
  for term in "D-1" "B" "不得复活" "C" "不得脑补" "docs/goal-ledger.md"; do
    grep -Fq "${term}" "${file}" || return 1
  done
}

question_record_count() {
  awk '{ count += gsub(/本轮问题[：:]/, "") } END { print count + 0 }' "$1"
}

assert_grill_evidence_closed() {
  local file="$1" term
  for term in "confirmed" "D-101"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "PRD" "product-requirements" || return 1
  assert_any "${file}" "知识库" "domain-knowledge" || return 1
  assert_any "${file}" "测试" "RefundPolicyTests" || return 1
  assert_any "${file}" "源码" "代码" "实现" "Java" "RefundPolicy" || return 1
  assert_any "${file}" "fact-confirmed" "decision-reused" || return 1
  assert_none "${file}" "ask-owner" "请确认" "本轮问题" || return 1
  [[ "$(question_record_count "${file}")" -eq 0 ]]
}

assert_grill_evidence_conflict() {
  local file="$1" term
  for term in "ask-owner" "D-102"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "PRD" "product-requirements" || return 1
  assert_any "${file}" "源码" "代码" "实现" "Java" "RefundPolicy" || return 1
  assert_any "${file}" "推荐" "建议" || return 1
  assert_any "${file}" "pending" "conflict" || return 1
  assert_any "${file}" "不执行" "不得执行" "停止执行" "未执行" || return 1
  assert_none "${file}" "开始修改" "已修改" "正在执行" "开始执行" || return 1
  [[ "$(question_record_count "${file}")" -eq 1 ]]
}

run_codex_smoke() {
  local output_file="$1" prompt="$2"
  rm -f "${output_file}"
  if ! codex exec -c 'model_reasoning_effort="low"' --ephemeral --sandbox read-only --output-last-message "${output_file}" "${prompt}"; then
    if [[ ! -s "${output_file}" ]]; then
      echo "FAIL codex behavior smoke produced no final response: ${output_file}" >&2
      return 1
    fi
    echo "WARN codex behavior smoke returned non-zero after producing a final response: ${output_file}" >&2
  fi
}

if [[ "${1:-}" == "--self-test" ]]; then
  sample_dir="$(mktemp -d)"
  cleanup_self_test() {
    rm -f \
      "${sample_dir}/product.txt" \
      "${sample_dir}/engineering.txt" \
      "${sample_dir}/superpowers-product.txt" \
      "${sample_dir}/superpowers-debugging.txt" \
      "${sample_dir}/superpowers-git.txt" \
      "${sample_dir}/lightweight.txt" \
      "${sample_dir}/simple-wording.txt" \
      "${sample_dir}/bad-product.txt" \
      "${sample_dir}/bad-lightweight.txt" \
      "${sample_dir}/bad-superpowers-git.txt" \
      "${sample_dir}/state-resume.txt" \
      "${sample_dir}/grill-closed.txt" \
      "${sample_dir}/grill-conflict.txt" \
      "${sample_dir}/bad-grill-closed.txt" \
      "${sample_dir}/bad-grill-conflict.txt"
    rmdir "${sample_dir}"
  }
  trap cleanup_self_test EXIT
  printf '%s\n' '事实：访谈。推断：有需求。待确认：owner。验收：场景通过。' > "${sample_dir}/product.txt"
  printf '%s\n' '严重级别：P1。证据：源码。测试：补回归。残余风险：并发。' > "${sample_dir}/engineering.txt"
  printf '%s\n' '知止者先用 brainstorming 收敛，关键分叉再用 grill-me；暂不写工程计划。' > "${sample_dir}/superpowers-product.txt"
  printf '%s\n' '知止者采用 systematic-debugging、test-driven-development、verification-before-completion。' > "${sample_dir}/superpowers-debugging.txt"
  printf '%s\n' 'Git 和 worktree 未授权；不允许 commit，也不允许 push 或创建 PR。' > "${sample_dir}/superpowers-git.txt"
  printf '%s\n' '回读后直接修改错别字。' > "${sample_dir}/lightweight.txt"
  printf '%s\n' '本次变更完善了校验。' > "${sample_dir}/simple-wording.txt"
  printf '%s\n' '事实：访谈。推断：有需求。待确认：owner。验收：场景通过。再启动 SDLC。' > "${sample_dir}/bad-product.txt"
  printf '%s\n' '先建立 Goal，再派 Worker 修改。' > "${sample_dir}/bad-lightweight.txt"
  printf '%s\n' 'Git 未授权；可以创建 worktree 并 commit。' > "${sample_dir}/bad-superpowers-git.txt"
  printf '%s\n' '从 docs/goal-ledger.md 恢复，只按 D-1 推进；B 不得复活，C 不得脑补。' > "${sample_dir}/state-resume.txt"
  printf '%s\n' '裁决动作：decision-reused；最终结论：confirmed；证据：PRD、D-101、知识库、源码和测试一致。' > "${sample_dir}/grill-closed.txt"
  printf '%s\n' '裁决动作：ask-owner；最终结论：conflict；证据冲突：PRD 对 D-102 未确认，源码不能定义业务意图；证据链接：decision?id=D-102；本轮不执行方案。推荐答案：人工复核。本轮问题：是否确认人工复核？' > "${sample_dir}/grill-conflict.txt"
  printf '%s\n' '裁决动作：decision-reused；最终结论：confirmed；证据：PRD、D-101、知识库、源码和测试一致。请确认？' > "${sample_dir}/bad-grill-closed.txt"
  printf '%s\n' '裁决动作：ask-owner；最终结论：pending；证据冲突：PRD 对 D-102 未确认，源码不能定义业务意图；本轮不执行方案。推荐答案：人工复核。本轮问题：是否自动重试？本轮问题：是否人工复核？' > "${sample_dir}/bad-grill-conflict.txt"
  assert_product "${sample_dir}/product.txt"
  assert_engineering "${sample_dir}/engineering.txt"
  assert_superpowers_product "${sample_dir}/superpowers-product.txt"
  assert_superpowers_debugging "${sample_dir}/superpowers-debugging.txt"
  assert_superpowers_git "${sample_dir}/superpowers-git.txt"
  assert_lightweight "${sample_dir}/lightweight.txt"
  assert_simple_wording "${sample_dir}/simple-wording.txt"
  assert_state_resume "${sample_dir}/state-resume.txt"
  assert_grill_evidence_closed "${sample_dir}/grill-closed.txt"
  assert_grill_evidence_conflict "${sample_dir}/grill-conflict.txt"
  if assert_product "${sample_dir}/engineering.txt"; then
    echo "FAIL product smoke accepted an engineering-only response" >&2
    exit 1
  fi
  if assert_product "${sample_dir}/bad-product.txt"; then
    echo "FAIL product smoke accepted an orchestration-heavy response" >&2
    exit 1
  fi
  if assert_lightweight "${sample_dir}/bad-lightweight.txt"; then
    echo "FAIL lightweight smoke accepted an orchestration-heavy response" >&2
    exit 1
  fi
  if assert_superpowers_git "${sample_dir}/bad-superpowers-git.txt"; then
    echo "FAIL Superpowers Git smoke accepted an authorization-contradictory response" >&2
    exit 1
  fi
  if assert_grill_evidence_closed "${sample_dir}/bad-grill-closed.txt"; then
    echo "FAIL grill-me evidence-closed smoke accepted a redundant question" >&2
    exit 1
  fi
  if assert_grill_evidence_conflict "${sample_dir}/bad-grill-conflict.txt"; then
    echo "FAIL grill-me conflict smoke accepted multiple questions" >&2
    exit 1
  fi
  echo "OK wise-agent behavior smoke self-test"
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --runs) RUNS="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

case "${MODE}" in
  all|product|engineering|superpowers|governance|grill-me) ;;
  *) echo "--mode must be all, product, engineering, superpowers, governance, or grill-me" >&2; exit 2 ;;
esac
if [[ ! "${RUNS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "--runs must be a positive integer" >&2
  exit 2
fi

cd "${ROOT_DIR}"
scripts/validate-installed-skills.sh
if [[ "${MODE}" == "all" || "${MODE}" == "superpowers" ]]; then
  scripts/validate-superpowers-install.sh
fi
mkdir -p "${OUTPUT_DIR}"

if [[ "${MODE}" == "all" || "${MODE}" == "product" ]]; then
  run_codex_smoke "${OUTPUT_DIR}/product.txt" \
    '我们只有两条材料：会员按等级获得权益；运营可配置并追溯规则版本。请判断是否足以直接写需求文档，指出成立内容、推测成分、还缺谁确认以及怎样证明可验收；只读，控制在 300 字。'
  assert_product "${OUTPUT_DIR}/product.txt" || { echo "FAIL product behavior smoke: ${OUTPUT_DIR}/product.txt" >&2; exit 1; }
fi

if [[ "${MODE}" == "all" || "${MODE}" == "engineering" ]]; then
  run_codex_smoke "${OUTPUT_DIR}/engineering.txt" \
    '只读审查：一个 Spring Service 在事务提交前先删除缓存，异常被 catch 后只记录日志并返回成功。请给出最重要的问题、判断依据、需要补的验证和仍不能排除的风险；控制在 300 字，不写文件。'
  assert_engineering "${OUTPUT_DIR}/engineering.txt" || { echo "FAIL engineering behavior smoke: ${OUTPUT_DIR}/engineering.txt" >&2; exit 1; }
fi

if [[ "${MODE}" == "all" || "${MODE}" == "superpowers" ]]; then
  run_codex_smoke "${OUTPUT_DIR}/superpowers-product.txt" \
    '一个模糊产品想法需要先收敛目标、对象、边界和验收；Superpowers 插件已安装。请判断当前先调用哪种探索方法、何时升级强盘问、何时才进入工程计划；只读，控制在 300 字。'
  assert_superpowers_product "${OUTPUT_DIR}/superpowers-product.txt" || { echo "FAIL Superpowers product behavior smoke: ${OUTPUT_DIR}/superpowers-product.txt" >&2; exit 1; }

  run_codex_smoke "${OUTPUT_DIR}/superpowers-debugging.txt" \
    'Java 服务出现稳定回归，已有失败测试；Superpowers 插件已安装。请选择从定位、修复到完成声明的方法链，并说明每一步的准出证据；只读，控制在 300 字，不运行测试。'
  assert_superpowers_debugging "${OUTPUT_DIR}/superpowers-debugging.txt" || { echo "FAIL Superpowers debugging behavior smoke: ${OUTPUT_DIR}/superpowers-debugging.txt" >&2; exit 1; }

  run_codex_smoke "${OUTPUT_DIR}/superpowers-git.txt" \
    '用户只要求原地改一行 Markdown，未授权任何 Git 或隔离工作区动作；Superpowers 插件已安装。请判断当前允许做什么；只读，控制在 200 字。'
  assert_superpowers_git "${OUTPUT_DIR}/superpowers-git.txt" || { echo "FAIL Superpowers Git behavior smoke: ${OUTPUT_DIR}/superpowers-git.txt" >&2; exit 1; }
fi

if [[ "${MODE}" == "all" || "${MODE}" == "governance" ]]; then
  run_codex_smoke "${OUTPUT_DIR}/lightweight.txt" \
    '用户只要求在当前 README 改一个错别字并回读，没有 Git 授权。请给最短处理判断；只读，不写文件。'
  assert_lightweight "${OUTPUT_DIR}/lightweight.txt" || { echo "FAIL lightweight behavior smoke: ${OUTPUT_DIR}/lightweight.txt" >&2; exit 1; }

  run_codex_smoke "${OUTPUT_DIR}/simple-wording.txt" \
    '把“本次变更主要是针对校验能力进行了进一步的完善”改得简洁自然，只返回改写后的句子。'
  assert_simple_wording "${OUTPUT_DIR}/simple-wording.txt" || { echo "FAIL simple wording behavior smoke: ${OUTPUT_DIR}/simple-wording.txt" >&2; exit 1; }

  run_codex_smoke "${OUTPUT_DIR}/state-resume.txt" \
    '长任务上下文已经压缩。允许的状态载体 docs/goal-ledger.md 记录：Goal G-17=Active，确认 D-1，排除 B，C 待确认，下一动作只允许执行 D-1。请在 200 字内判断恢复后能做什么以及何时停止；只读判断。'
  assert_state_resume "${OUTPUT_DIR}/state-resume.txt" || { echo "FAIL state resume behavior smoke: ${OUTPUT_DIR}/state-resume.txt" >&2; exit 1; }
fi

if [[ "${MODE}" == "all" || "${MODE}" == "grill-me" ]]; then
  for ((run = 1; run <= RUNS; run++)); do
    run_codex_smoke "${OUTPUT_DIR}/grill-evidence-closed-${run}.txt" \
      '使用 $grill-me 只读审查退款过期时间。实际读取 grill-me/fixtures/behavior-evidence 下的 PRD、决策记录、知识库、Java 源码和测试；按当前协议裁决是否需要问 Owner。只输出本轮台账记录和结论，不执行方案，控制在 350 字。'
    assert_grill_evidence_closed "${OUTPUT_DIR}/grill-evidence-closed-${run}.txt" || { echo "FAIL grill-me evidence-closed behavior smoke: ${OUTPUT_DIR}/grill-evidence-closed-${run}.txt" >&2; exit 1; }

    run_codex_smoke "${OUTPUT_DIR}/grill-evidence-conflict-${run}.txt" \
      '使用 $grill-me 只读审查供应商超时后的退款重试策略。实际读取 grill-me/fixtures/behavior-evidence 下的 PRD、决策记录、知识库和 Java 源码；按当前协议处理意图与实现冲突。只输出本轮台账和需要 Owner 回答的一个问题，不执行方案，控制在 350 字。'
    assert_grill_evidence_conflict "${OUTPUT_DIR}/grill-evidence-conflict-${run}.txt" || { echo "FAIL grill-me evidence-conflict behavior smoke: ${OUTPUT_DIR}/grill-evidence-conflict-${run}.txt" >&2; exit 1; }
  done
fi

echo "OK wise-agent behavior smoke: ${OUTPUT_DIR}"
