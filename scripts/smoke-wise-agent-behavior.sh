#!/usr/bin/env bash
set -euo pipefail

# Input: current Codex installation, its configured provider, and this repository.
# Output: final responses under --output-dir (default: /tmp/wise-agent-smoke-<timestamp>).
# Writes: output directory only. Network: codex exec may call the configured provider.
# Failure: exits non-zero when a response misses the contract; installed-skill modes also require repository parity.
# Source semantic-contract smoke: scripts/smoke-wise-agent-behavior.sh --mode semantic-contract
# Learning backflow smoke: scripts/smoke-wise-agent-behavior.sh --mode learning

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
  assert_none "${file}" "华夏经世智慧" "老祖宗智慧" "周易" "道德经" "阴阳五行"
}

assert_huaxia_decision() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "事实" "待确认" "行动" "止损" "验证"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "可逆" "试点" "可回退" "试行" || return 1
  assert_none "${file}" "保证成功" "必然成功" "替代专业判断"
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

assert_design_composition_product() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  grep -Fq "万能" "${file}" || return 1
  assert_any "${file}" "拒绝" "不采用" "不应" "不能" || return 1
  assert_any "${file}" "目标层" "目标、业务流程和产品能力分层" || return 1
  for term in "对象不变量" "变化轴"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "独立验收" "独立验证" || return 1
  grep -Eq '(不把|不将|不能把|不得把)[^。；]*(能力|能力图)[^。；]*(等同|映射)[^。；]*(服务|接口|数据库|工作流)|能力(图)?[^。；]*(不等同|不能等同)[^。；]*(服务|接口|数据库|工作流)' "${file}" || return 1
  assert_none "${file}" "采用万能能力" "保留万能能力" "由万能能力统一处理"
}

assert_design_composition_engineering() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  assert_any "${file}" "UnifiedFlowOrchestrator" "统一编排器" || return 1
  assert_any "${file}" "拒绝" "不应把" "不能把" "不得把" || return 1
  for term in "业务规则" "不变量" "顺序" "事务" "补偿"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "状态机" "状态" || return 1
  grep -Eq '(不|不得|不能|避免)[^。；]*透传服务' "${file}" || return 1
  grep -Eq '(不|不得|不能|避免)[^。；]*(预设|等同|机械拆分)[^。；]*微服务|微服务[^。；]*(不|不得|不能)[^。；]*(预设|等同|机械拆分)' "${file}" || return 1
  assert_none "${file}" "由 UnifiedFlowOrchestrator 承载全部规则" "由统一编排器承载全部规则"
}

assert_in_order() {
  local file="$1" body term
  shift
  body="$(tr '\n' ' ' < "${file}")"
  for term in "$@"; do
    [[ "${body}" == *"${term}"* ]] || return 1
    body="${body#*"${term}"}"
  done
}

assert_design_document_product() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  assert_in_order "${file}" "背景" "目标" "定性" "概要设计" "详细设计" "关键流程" "业务规则" "接口抽象" "验收摘要" || return 1
  for term in "能力提供者" "共性" "特殊性" "执行计划"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_none "${file}" "按每个需求复制" "验收摘要放在背景之前" "不需要执行计划"
}

assert_design_document_engineering() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  assert_in_order "${file}" "背景" "目标" "定性" "概要设计" "详细设计" "关键流程" "业务规则" "接口抽象" "验收摘要" || return 1
  for term in "能力提供者" "对象" "不变量" "特殊性" "变化轴" "执行计划"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_none "${file}" "按每个需求复制" "验收摘要放在背景之前" "不需要执行计划"
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

assert_fast_coding() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "编码先行" "测试后置" "验证债务" "实现已完成，测试与验证待补"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "集中补测试、验证和 CR" "补测试、验证和 CR" || return 1
  assert_none "${file}" "测试可选" "无需测试" "任务已完成" "可直接提交"
}

assert_fast_coding_high_risk() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "不得默认进入" "公共契约" "数据库" "Owner" "测试"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "停止编码" "退出快速路径" || return 1
  assert_none "${file}" "直接推进" "测试可以省略" "可直接发布"
}

assert_standard_engineering() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "标准工程流程" "测试" "验证" "CR"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "不进入快速编码" "不走快速编码" || return 1
  assert_any "${file}" "不创建 Goal" "无需 Goal" || return 1
  assert_any "${file}" "不进入受控工程执行 Loop" "无需受控工程执行 Loop" || return 1
  assert_none "${file}" "CAD Candidate" "CAD Loop Active" "CAD Grant" "Loop Active [engineering]"
}

assert_controlled_engineering_loop() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "受控工程执行 Loop" "Goal 状态" "Active" "执行方式" "Pick" "Build/Test" "Review" "Verify" "Record" "Continue/Pause"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "输入别名" "别名" || return 1
  assert_any "${file}" "Execution Grant" "Plan Grant" || return 1
  assert_none "${file}" "CAD Candidate" "CAD Loop Active" "CAD Grant" "Loop Active [engineering]" "Paused" "Escalated"
}

assert_controlled_engineering_loop_blocked() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "工程 Loop 条件不足" "状态载体" "反馈源" "验证者" "最大轮次" "无进展检测" "授权"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "不开始写入" "不执行写入" "不得开始写入" || return 1
  assert_any "${file}" "Draft" "Ready" || return 1
  assert_none "${file}" "CAD Candidate" "CAD Loop Active" "CAD Grant" "Loop Active [engineering]" "直接开始修改" "已开始写入" "立即执行代码"
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
  for term in "D-1" "B" "C" "docs/goal-ledger.md"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  grep -Eq '(只按|仅可按|仅允许执行|只能执行|仅执行)[^。；]*D-1|D-1[^。；]*(唯一|仅|只)' "${file}" || return 1
  grep -Eq '(不得|不能|不应)[^。；]*B|B[^。；]*(不得|不能|不应)' "${file}" || return 1
  grep -Eq '(不得|不能|不应)[^。；]*C|C[^。；]*(不得|不能|不应)' "${file}" || return 1
  assert_any "${file}" "待确认" "脑补" "作决定" "假定" || return 1
}

assert_skill_improvement() {
  local file="$1" term
  for term in "目标 Skill" "可复用规则" "wise-agent" "单一专业" "权威落点" "最小修改" "订单优惠券"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "真实失败模式" "真实失败" || return 1
  assert_any "${file}" "验证方式" "验证" || return 1
  assert_any "${file}" "fixture" "负例" "validator" "评测" "校验脚本" "evaluate-skills.py" || return 1
  assert_any "${file}" "不得吸收" "不回流" "任务噪声" || return 1
  assert_any "${file}" "授权边界" "授权" || return 1
  grep -Eq '不得吸收[：:][^。；]*(订单优惠券)|任务噪声[^。；]*(订单优惠券)|订单优惠券[^。；]*(不得吸收|不回流|排除|不得写入|不写入|任务噪声)' "${file}" || return 1
  grep -Eq '(不|不得|未授权)[^。；]*(修改|写入)|(修改|写入|Git)[^。；]*(需|须)[^。；]*授权' "${file}" || return 1
  grep -Eq '(不|不得|未授权)[^。；]*(提交|commit)|(提交|commit|Git)[^。；]*(需|须)[^。；]*授权' "${file}" || return 1
  grep -Eq '(不|不得|未授权)[^。；]*(同步|发布)|(同步|发布|Git)[^。；]*(需|须)[^。；]*授权' "${file}" || return 1
  assert_none "${file}" "已修改" "已经修改" "已提交" "已经提交" "已同步" "已经同步" || return 1
}

question_record_count() {
  awk '{
    count += gsub(/本轮问题[：:]/, "")
    count += gsub(/需要 Owner 回答的一个问题[：:]/, "")
    count += gsub(/(^|[[:space:]])问题[：:]/, "")
  } END { print count + 0 }' "$1"
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

assert_approved_product_contract_conflict() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "PRD" "工程" "验证"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "规范性目标" "目标契约" "产品契约" || return 1
  assert_any "${file}" "保持权威" "仍是权威" "继续作为权威" "继续保持权威" "保持有效" || return 1
  assert_any "${file}" "实现偏差" "工程偏差" || return 1
  assert_any "${file}" "修复" "迁移" || return 1
  assert_none "${file}" "把原产品决策重新标为 PENDING" "将 PRD 重新标为 PENDING" "PRD 重新标为 PENDING"
}

assert_blocking_data_semantics() {
  local file="$1" term
  [[ -s "${file}" ]] || return 1
  for term in "来源表" "退款" "时区" "SQL"; do
    grep -Fq "${term}" "${file}" || return 1
  done
  assert_any "${file}" "阻断性 PENDING" "阻断项" "阻断性待确认" || return 1
  assert_any "${file}" "owner" "Owner" "责任人" || return 1
  grep -Eq '(停止|阻断|不得|不能|不应|暂不)[^。；]*(SQL|下游)|(SQL|下游)[^。；]*(停止|阻断|不得|不能|不应|暂不)' "${file}" || return 1
  assert_none "${file}" "可直接生成 SQL" "继续生成 SQL" "先生成 SQL 再确认"
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

run_codex_learning_smoke() {
  local output_file="$1" learning_home="$2" prompt="$3"
  rm -f "${output_file}"
  if ! SKILL_LEARNING_HOME="${learning_home}" codex exec -c 'model_reasoning_effort="low"' --ephemeral --sandbox workspace-write --output-last-message "${output_file}" "${prompt}"; then
    if [[ ! -s "${output_file}" ]]; then
      echo "FAIL codex learning smoke produced no final response: ${output_file}" >&2
      return 1
    fi
    echo "WARN codex learning smoke returned non-zero after producing a final response: ${output_file}" >&2
  fi
}

learning_record_count() {
  find "$1/wise-agent/records" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' '
}

if [[ "${1:-}" == "--self-test" ]]; then
  sample_dir="$(mktemp -d)"
  cleanup_self_test() {
    rm -f \
      "${sample_dir}/product.txt" \
      "${sample_dir}/engineering.txt" \
      "${sample_dir}/huaxia.txt" \
      "${sample_dir}/huaxia-variant.txt" \
      "${sample_dir}/bad-huaxia.txt" \
      "${sample_dir}/bad-engineering-huaxia.txt" \
      "${sample_dir}/superpowers-product.txt" \
      "${sample_dir}/superpowers-debugging.txt" \
      "${sample_dir}/superpowers-git.txt" \
      "${sample_dir}/lightweight.txt" \
      "${sample_dir}/fast-coding.txt" \
      "${sample_dir}/fast-coding-high-risk.txt" \
      "${sample_dir}/standard-engineering.txt" \
      "${sample_dir}/controlled-engineering-loop.txt" \
      "${sample_dir}/controlled-engineering-loop-blocked.txt" \
      "${sample_dir}/simple-wording.txt" \
      "${sample_dir}/bad-product.txt" \
      "${sample_dir}/design-product.txt" \
      "${sample_dir}/bad-design-product.txt" \
      "${sample_dir}/design-engineering.txt" \
      "${sample_dir}/bad-design-engineering.txt" \
      "${sample_dir}/design-document-product.txt" \
      "${sample_dir}/bad-design-document-product.txt" \
      "${sample_dir}/design-document-engineering.txt" \
      "${sample_dir}/bad-design-document-engineering.txt" \
      "${sample_dir}/bad-lightweight.txt" \
      "${sample_dir}/bad-fast-coding.txt" \
      "${sample_dir}/bad-fast-coding-high-risk.txt" \
      "${sample_dir}/bad-standard-engineering.txt" \
      "${sample_dir}/bad-controlled-engineering-loop.txt" \
      "${sample_dir}/bad-controlled-engineering-loop-blocked.txt" \
      "${sample_dir}/bad-superpowers-git.txt" \
      "${sample_dir}/state-resume.txt" \
      "${sample_dir}/state-resume-variant.txt" \
      "${sample_dir}/state-resume-variant-2.txt" \
      "${sample_dir}/state-resume-variant-3.txt" \
      "${sample_dir}/skill-improvement.txt" \
      "${sample_dir}/skill-improvement-coordinated-auth.txt" \
      "${sample_dir}/skill-improvement-semantic-variant.txt" \
      "${sample_dir}/bad-skill-improvement-noise.txt" \
      "${sample_dir}/bad-skill-improvement-authorization.txt" \
      "${sample_dir}/grill-closed.txt" \
      "${sample_dir}/grill-conflict.txt" \
      "${sample_dir}/grill-conflict-variant.txt" \
      "${sample_dir}/bad-grill-closed.txt" \
      "${sample_dir}/bad-grill-conflict.txt" \
      "${sample_dir}/approved-product-contract.txt" \
      "${sample_dir}/bad-approved-product-contract.txt" \
      "${sample_dir}/blocking-data-semantics.txt" \
      "${sample_dir}/bad-blocking-data-semantics.txt"
    rmdir "${sample_dir}"
  }
  trap cleanup_self_test EXIT
  printf '%s\n' '事实：访谈。推断：有需求。待确认：owner。验收：场景通过。' > "${sample_dir}/product.txt"
  printf '%s\n' '严重级别：P1。证据：源码。测试：补回归。残余风险：并发。' > "${sample_dir}/engineering.txt"
  printf '%s\n' '事实：目标一致。待确认：责任 owner。行动：做可逆试点。止损：责任不清则停止。验证：复盘结果。' > "${sample_dir}/huaxia.txt"
  printf '%s\n' '事实：目标一致。待确认：责任 owner。最小行动：选择可回退流程试行。止损：成本触顶则停止。验证：对照基线。' > "${sample_dir}/huaxia-variant.txt"
  printf '%s\n' '顺其自然即可，必然成功。' > "${sample_dir}/bad-huaxia.txt"
  printf '%s\n' '严重级别：P1。证据：源码。测试：补回归。残余风险：并发。按周易阴阳五行处理。' > "${sample_dir}/bad-engineering-huaxia.txt"
  printf '%s\n' '知止者先用 brainstorming 收敛，关键分叉再用 grill-me；暂不写工程计划。' > "${sample_dir}/superpowers-product.txt"
  printf '%s\n' '知止者采用 systematic-debugging、test-driven-development、verification-before-completion。' > "${sample_dir}/superpowers-debugging.txt"
  printf '%s\n' 'Git 和 worktree 未授权；不允许 commit，也不允许 push 或创建 PR。' > "${sample_dir}/superpowers-git.txt"
  printf '%s\n' '回读后直接修改错别字。' > "${sample_dir}/lightweight.txt"
  printf '%s\n' '进入快速编码：编码先行，测试后置；实现回读后标记“实现已完成，测试与验证待补”，记录验证债务，再集中补测试、验证和 CR。' > "${sample_dir}/fast-coding.txt"
  printf '%s\n' '支付状态机、公共契约和数据库变更不得默认进入快速编码；停止编码，先由 Owner 确认，测试与验证不能省略。' > "${sample_dir}/fast-coding-high-risk.txt"
  printf '%s\n' '使用标准工程流程完成最小修改、测试、验证和 CR；不进入快速编码，不创建 Goal，也不进入受控工程执行 Loop。' > "${sample_dir}/standard-engineering.txt"
  printf '%s\n' 'CAD 是受控工程执行 Loop 的输入别名。Goal 状态：Active；执行方式：受控工程执行 Loop；适用授权：Execution Grant。每轮按 Pick -> Build/Test -> Review -> Verify -> Record -> Continue/Pause 推进。' > "${sample_dir}/controlled-engineering-loop.txt"
  printf '%s\n' '工程 Loop 条件不足，不开始写入；Goal 保持 Ready。缺口：状态载体、反馈源、验证者、最大轮次、无进展检测、停止条件和适用授权。' > "${sample_dir}/controlled-engineering-loop-blocked.txt"
  printf '%s\n' '本次变更完善了校验。' > "${sample_dir}/simple-wording.txt"
  printf '%s\n' '事实：访谈。推断：有需求。待确认：owner。验收：场景通过。再启动 SDLC。' > "${sample_dir}/bad-product.txt"
  printf '%s\n' '拒绝万能能力。按目标层、流程层和能力层拆分；能力围绕对象不变量、真实变化轴和独立验收划分，不把产品能力图等同于服务、接口、数据库或工作流。' > "${sample_dir}/design-product.txt"
  printf '%s\n' '采用万能能力，由万能能力统一处理全部流程；目标层、对象不变量、变化轴和独立验收以后再补，产品能力图直接映射服务。' > "${sample_dir}/bad-design-product.txt"
  printf '%s\n' '不应把全部规则放进 UnifiedFlowOrchestrator。编排只负责顺序、事务和补偿，领域能力持有业务规则、状态机和不变量；不新增透传服务，不预设微服务拆分。' > "${sample_dir}/design-engineering.txt"
  printf '%s\n' '由 UnifiedFlowOrchestrator 承载全部规则；领域对象只保存状态，新增透传服务并预设微服务拆分，以统一顺序、事务和补偿。' > "${sample_dir}/bad-design-engineering.txt"
  printf '%s\n' '能力提供者先察同共性，再按证据辨别特殊性。正文依次为背景、目标、定性、概要设计、详细设计、关键流程、业务规则、接口抽象和验收摘要；详细验收矩阵进入执行计划。' > "${sample_dir}/design-document-product.txt"
  printf '%s\n' '按每个需求复制一套能力。验收摘要放在背景之前，详细验收矩阵铺在正文开头，不需要执行计划。' > "${sample_dir}/bad-design-document-product.txt"
  printf '%s\n' '系统以能力提供者承接共同目标、对象和不变量，特殊性只进入有证据的变化轴。正文依次为背景、目标、定性、概要设计、详细设计、关键流程、业务规则、接口抽象和验收摘要；详细验收矩阵进入执行计划。' > "${sample_dir}/design-document-engineering.txt"
  printf '%s\n' '按每个需求复制模块。验收摘要放在背景之前，详细验收矩阵铺在正文开头，不需要执行计划。' > "${sample_dir}/bad-design-document-engineering.txt"
  printf '%s\n' '先建立 Goal，再派 Worker 修改。' > "${sample_dir}/bad-lightweight.txt"
  printf '%s\n' '快速编码后任务已完成，测试可选，可以直接提交。' > "${sample_dir}/bad-fast-coding.txt"
  printf '%s\n' '公共契约和数据库直接推进，测试可以省略，可直接发布。' > "${sample_dir}/bad-fast-coding-high-risk.txt"
  printf '%s\n' '直接进入快速编码并创建 Goal 和工程 Loop，测试以后再说。' > "${sample_dir}/bad-standard-engineering.txt"
  printf '%s\n' '进入 CAD Mode，状态写成 CAD Loop Active，并创建 CAD Grant。' > "${sample_dir}/bad-controlled-engineering-loop.txt"
  printf '%s\n' '工程 Loop 条件不足，但直接开始修改；状态载体、反馈源、验证者、最大轮次、无进展检测和授权以后再补。' > "${sample_dir}/bad-controlled-engineering-loop-blocked.txt"
  printf '%s\n' 'Git 未授权；可以创建 worktree 并 commit。' > "${sample_dir}/bad-superpowers-git.txt"
  printf '%s\n' '从 docs/goal-ledger.md 恢复，只按 D-1 推进；已排除的 B 不得复活，C 不得脑补。' > "${sample_dir}/state-resume.txt"
  printf '%s\n' '从 docs/goal-ledger.md 恢复，只按 D-1 推进；不得转向已排除的 B，不得推进待确认的 C。' > "${sample_dir}/state-resume-variant.txt"
  printf '%s\n' '从 docs/goal-ledger.md 恢复，仅允许执行已确认的 D-1；不得触碰已排除的 B，也不得替 C 作决定。' > "${sample_dir}/state-resume-variant-2.txt"
  printf '%s\n' '从 docs/goal-ledger.md 恢复，仅可按已确认的 D-1 推进；不得执行 B，也不得假定 C。' > "${sample_dir}/state-resume-variant-3.txt"
  printf '%s\n' 'Skill Improvement Card；目标 Skill：wise-agent；真实失败模式：单一专业只读 CR 被误触发；可复用规则：单一专业任务直接加载对应 Skill；权威落点：wise-agent/SKILL.md；最小修改位置：metadata；验证方式：回归 fixture / validator；不得吸收：订单优惠券业务细节；授权边界：只读，不修改、不提交、不同步。' > "${sample_dir}/skill-improvement.txt"
  printf '%s\n' '目标 Skill：wise-agent；真实失败模式：普通单一专业源码 CR 误触发；可复用规则：单一专业任务只加载架构师；权威落点：metadata；最小修改：保持零 diff；验证方式：fixture 与 validator；不得吸收：订单优惠券类名；授权边界：只读，不修改、提交、同步或发布。' > "${sample_dir}/skill-improvement-coordinated-auth.txt"
  printf '%s\n' '目标 Skill：wise-agent；真实失败：普通单一专业源码 CR 误触发；可复用规则：只加载架构师；权威落点：触发评测契约；最小修改：加强 hard-negative fixture；验证：旧样例转绿；任务噪声：订单优惠券类名不具跨项目价值，不得写入 Skill；授权：本轮仅审查，不修改、提交、同步或发布。' > "${sample_dir}/skill-improvement-semantic-variant.txt"
  printf '%s\n' 'Skill Improvement Card；目标 Skill：wise-agent；真实失败模式：单一专业只读 CR 被误触发；可复用规则：把订单优惠券类名写入通用规则；权威落点：wise-agent/SKILL.md；最小修改位置：metadata；验证方式：回归 fixture / validator；不得吸收：无；授权边界：只读，不修改、不提交、不同步。' > "${sample_dir}/bad-skill-improvement-noise.txt"
  printf '%s\n' 'Skill Improvement Card；目标 Skill：wise-agent；真实失败模式：单一专业只读 CR 被误触发；可复用规则：单一专业任务直接加载对应 Skill；权威落点：wise-agent/SKILL.md；最小修改位置：metadata；验证方式：回归 fixture / validator；不得吸收：订单优惠券业务细节；授权边界：已修改、已提交并同步。' > "${sample_dir}/bad-skill-improvement-authorization.txt"
  printf '%s\n' '裁决动作：decision-reused；最终结论：confirmed；证据：PRD、D-101、知识库、源码和测试一致。' > "${sample_dir}/grill-closed.txt"
  printf '%s\n' '裁决动作：ask-owner；最终结论：conflict；证据冲突：PRD 对 D-102 未确认，源码不能定义业务意图；证据链接：decision?id=D-102；本轮不执行方案。推荐答案：人工复核。本轮问题：是否确认人工复核？' > "${sample_dir}/grill-conflict.txt"
  printf '%s\n' '裁决动作：ask-owner；最终结论：conflict；证据冲突：PRD 对 D-102 未确认，Java 实现不能定义业务意图；未确认不得执行方案。推荐答案：人工复核。需要 Owner 回答的一个问题：是否确认人工复核？' > "${sample_dir}/grill-conflict-variant.txt"
  printf '%s\n' '裁决动作：decision-reused；最终结论：confirmed；证据：PRD、D-101、知识库、源码和测试一致。请确认？' > "${sample_dir}/bad-grill-closed.txt"
  printf '%s\n' '裁决动作：ask-owner；最终结论：pending；证据冲突：PRD 对 D-102 未确认，源码不能定义业务意图；本轮不执行方案。推荐答案：人工复核。本轮问题：是否自动重试？本轮问题：是否人工复核？' > "${sample_dir}/bad-grill-conflict.txt"
  printf '%s\n' '业务 owner 已批准 PRD 的全局唯一目标契约，该规范性目标保持权威；当前数据库属于工程实现偏差。停止受影响实现，由工程 owner 制定修复或迁移方案并提供验证证据。' > "${sample_dir}/approved-product-contract.txt"
  printf '%s\n' '业务 owner 已批准 PRD，但当前数据库不同，所以把原产品决策重新标为 PENDING，工程继续兼容。' > "${sample_dir}/bad-approved-product-contract.txt"
  printf '%s\n' '来源表、退款与时区均是阻断性 PENDING；责任 owner 确认前停止 SQL 和下游构造，不猜测口径。' > "${sample_dir}/blocking-data-semantics.txt"
  printf '%s\n' '来源表、退款与时区待确认，但可直接生成 SQL，后续再由 owner 修正。' > "${sample_dir}/bad-blocking-data-semantics.txt"
  assert_product "${sample_dir}/product.txt"
  assert_engineering "${sample_dir}/engineering.txt"
  assert_huaxia_decision "${sample_dir}/huaxia.txt"
  assert_huaxia_decision "${sample_dir}/huaxia-variant.txt"
  assert_design_composition_product "${sample_dir}/design-product.txt"
  assert_design_composition_engineering "${sample_dir}/design-engineering.txt"
  assert_design_document_product "${sample_dir}/design-document-product.txt"
  assert_design_document_engineering "${sample_dir}/design-document-engineering.txt"
  assert_superpowers_product "${sample_dir}/superpowers-product.txt"
  assert_superpowers_debugging "${sample_dir}/superpowers-debugging.txt"
  assert_superpowers_git "${sample_dir}/superpowers-git.txt"
  assert_lightweight "${sample_dir}/lightweight.txt"
  assert_fast_coding "${sample_dir}/fast-coding.txt"
  assert_fast_coding_high_risk "${sample_dir}/fast-coding-high-risk.txt"
  assert_standard_engineering "${sample_dir}/standard-engineering.txt"
  assert_controlled_engineering_loop "${sample_dir}/controlled-engineering-loop.txt"
  assert_controlled_engineering_loop_blocked "${sample_dir}/controlled-engineering-loop-blocked.txt"
  assert_simple_wording "${sample_dir}/simple-wording.txt"
  assert_state_resume "${sample_dir}/state-resume.txt"
  assert_state_resume "${sample_dir}/state-resume-variant.txt"
  assert_state_resume "${sample_dir}/state-resume-variant-2.txt"
  assert_state_resume "${sample_dir}/state-resume-variant-3.txt"
  assert_skill_improvement "${sample_dir}/skill-improvement.txt"
  assert_skill_improvement "${sample_dir}/skill-improvement-coordinated-auth.txt"
  assert_skill_improvement "${sample_dir}/skill-improvement-semantic-variant.txt"
  assert_grill_evidence_closed "${sample_dir}/grill-closed.txt"
  assert_grill_evidence_conflict "${sample_dir}/grill-conflict.txt"
  assert_grill_evidence_conflict "${sample_dir}/grill-conflict-variant.txt"
  assert_approved_product_contract_conflict "${sample_dir}/approved-product-contract.txt"
  assert_blocking_data_semantics "${sample_dir}/blocking-data-semantics.txt"
  if assert_product "${sample_dir}/engineering.txt"; then
    echo "FAIL product smoke accepted an engineering-only response" >&2
    exit 1
  fi
  if assert_huaxia_decision "${sample_dir}/bad-huaxia.txt"; then
    echo "FAIL Huaxia smoke accepted slogan-only certainty" >&2
    exit 1
  fi
  if assert_engineering "${sample_dir}/bad-engineering-huaxia.txt"; then
    echo "FAIL engineering smoke accepted Huaxia framing for ordinary engineering CR" >&2
    exit 1
  fi
  if assert_product "${sample_dir}/bad-product.txt"; then
    echo "FAIL product smoke accepted an orchestration-heavy response" >&2
    exit 1
  fi
  if assert_design_composition_product "${sample_dir}/bad-design-product.txt"; then
    echo "FAIL product design composition smoke accepted a universal capability" >&2
    exit 1
  fi
  if assert_design_composition_engineering "${sample_dir}/bad-design-engineering.txt"; then
    echo "FAIL engineering design composition smoke accepted a god orchestrator" >&2
    exit 1
  fi
  if assert_design_document_product "${sample_dir}/bad-design-document-product.txt"; then
    echo "FAIL product design document smoke accepted mechanical output" >&2
    exit 1
  fi
  if assert_design_document_engineering "${sample_dir}/bad-design-document-engineering.txt"; then
    echo "FAIL engineering design document smoke accepted mechanical output" >&2
    exit 1
  fi
  if assert_lightweight "${sample_dir}/bad-lightweight.txt"; then
    echo "FAIL lightweight smoke accepted an orchestration-heavy response" >&2
    exit 1
  fi
  if assert_fast_coding "${sample_dir}/bad-fast-coding.txt"; then
    echo "FAIL fast-coding smoke accepted verification-free completion" >&2
    exit 1
  fi
  if assert_fast_coding_high_risk "${sample_dir}/bad-fast-coding-high-risk.txt"; then
    echo "FAIL fast-coding smoke accepted a high-risk direct path" >&2
    exit 1
  fi
  if assert_standard_engineering "${sample_dir}/bad-standard-engineering.txt"; then
    echo "FAIL standard engineering smoke accepted the wrong execution path" >&2
    exit 1
  fi
  if assert_controlled_engineering_loop "${sample_dir}/bad-controlled-engineering-loop.txt"; then
    echo "FAIL controlled engineering smoke accepted deprecated CAD state or grant" >&2
    exit 1
  fi
  if assert_controlled_engineering_loop_blocked "${sample_dir}/bad-controlled-engineering-loop-blocked.txt"; then
    echo "FAIL controlled engineering smoke accepted execution without a Loop contract" >&2
    exit 1
  fi
  if assert_superpowers_git "${sample_dir}/bad-superpowers-git.txt"; then
    echo "FAIL Superpowers Git smoke accepted an authorization-contradictory response" >&2
    exit 1
  fi
  if assert_skill_improvement "${sample_dir}/bad-skill-improvement-noise.txt"; then
    echo "FAIL Skill self-improvement smoke accepted business noise" >&2
    exit 1
  fi
  if assert_skill_improvement "${sample_dir}/bad-skill-improvement-authorization.txt"; then
    echo "FAIL Skill self-improvement smoke accepted unauthorized delivery" >&2
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
  if assert_approved_product_contract_conflict "${sample_dir}/bad-approved-product-contract.txt"; then
    echo "FAIL semantic-contract smoke accepted demotion of an approved product contract" >&2
    exit 1
  fi
  if assert_blocking_data_semantics "${sample_dir}/bad-blocking-data-semantics.txt"; then
    echo "FAIL semantic-contract smoke accepted SQL construction with blocking semantics unresolved" >&2
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
  all|product|engineering|design-composition|superpowers|governance|self-improvement|learning|grill-me|huaxia|semantic-contract) ;;
  *) echo "--mode must be all, product, engineering, design-composition, superpowers, governance, self-improvement, learning, grill-me, huaxia, or semantic-contract" >&2; exit 2 ;;
esac
if [[ ! "${RUNS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "--runs must be a positive integer" >&2
  exit 2
fi

cd "${ROOT_DIR}"
if [[ "${MODE}" != "semantic-contract" ]]; then
  scripts/validate-installed-skills.sh
fi
if [[ "${MODE}" == "all" || "${MODE}" == "superpowers" ]]; then
  scripts/validate-superpowers-install.sh
fi
mkdir -p "${OUTPUT_DIR}"

if [[ "${MODE}" == "all" || "${MODE}" == "semantic-contract" ]]; then
  run_codex_smoke "${OUTPUT_DIR}/approved-product-contract.txt" \
    "只读行为验证。先读取 ${ROOT_DIR}/wise-agent/SKILL.md 和 ${ROOT_DIR}/wise-agent/references/prd-system-design-review.md，以源仓库内容作为本题规则。业务 owner 已批准 PRD 将渠道订单号全局唯一作为规范性目标契约，但数据库唯一键仍是 tenant_id + channel + order_no，历史数据也存在跨渠道重复。请判断哪一方保持权威、如何处理偏差、下一步由谁做什么以及如何验证；不得写文件，控制在 350 字。"
  assert_approved_product_contract_conflict "${OUTPUT_DIR}/approved-product-contract.txt" || { echo "FAIL approved product contract behavior smoke: ${OUTPUT_DIR}/approved-product-contract.txt" >&2; exit 1; }

  run_codex_smoke "${OUTPUT_DIR}/blocking-data-semantics.txt" \
    "只读行为验证。先读取 ${ROOT_DIR}/product-architecture-expert/SKILL.md 和 ${ROOT_DIR}/product-architecture-expert/references/product-prd-operations-and-data.md，以源仓库内容作为本题规则。商户日 GMV 报表准备交给数据开发，但来源表、退款是否扣除和跨时区口径都未确认。请给出当前交接结论，并明确现在能否构造 SQL 或下游输入；不得写文件，控制在 350 字。"
  assert_blocking_data_semantics "${OUTPUT_DIR}/blocking-data-semantics.txt" || { echo "FAIL blocking data semantics behavior smoke: ${OUTPUT_DIR}/blocking-data-semantics.txt" >&2; exit 1; }
fi

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

if [[ "${MODE}" == "all" || "${MODE}" == "huaxia" ]]; then
  for ((run = 1; run <= RUNS; run++)); do
    run_codex_smoke "${OUTPUT_DIR}/huaxia-decision-${run}.txt" \
      '使用 $huaxia-practical-wisdom 只读校准一次跨部门合作试点。已知双方目标一致、资源只够小范围试行；责任 owner 和失败成本仍待确认。请区分事实与待确认，给出最小可逆行动、止损条件、验证方式，以及何时停止或调整试点；不要用古语替代现实证据，控制在 300 字。'
    assert_huaxia_decision "${OUTPUT_DIR}/huaxia-decision-${run}.txt" || { echo "FAIL Huaxia decision behavior smoke: ${OUTPUT_DIR}/huaxia-decision-${run}.txt" >&2; exit 1; }
  done
fi

if [[ "${MODE}" == "all" || "${MODE}" == "design-composition" ]]; then
  for ((run = 1; run <= RUNS; run++)); do
    run_codex_smoke "${OUTPUT_DIR}/design-composition-product-${run}.txt" \
      '使用 $product-architecture-expert 只读评审：一个电商履约产品想把受理、库存、风险审查、履约和售后都做成一个万能业务处理能力。当前只验证通用产品能力分层，不读取垂直专项 reference；请在 350 字内给出判断、分层、拆分依据、组合方式和不做项，不写文件。'
    assert_design_composition_product "${OUTPUT_DIR}/design-composition-product-${run}.txt" || { echo "FAIL product design composition behavior smoke: ${OUTPUT_DIR}/design-composition-product-${run}.txt" >&2; exit 1; }

    run_codex_smoke "${OUTPUT_DIR}/design-composition-engineering-${run}.txt" \
      '使用 $senior-software-architect 只读评审：订单履约系统准备把下单、支付、库存、风控和物流的全部规则与状态判断写进 UnifiedFlowOrchestrator，让其它服务只读写数据。请在 350 字内给出判断、分层职责、拆分依据、编排边界和不做项，不写文件。'
    assert_design_composition_engineering "${OUTPUT_DIR}/design-composition-engineering-${run}.txt" || { echo "FAIL engineering design composition behavior smoke: ${OUTPUT_DIR}/design-composition-engineering-${run}.txt" >&2; exit 1; }

    run_codex_smoke "${OUTPUT_DIR}/design-document-product-${run}.txt" \
      '使用 $product-architecture-expert 只读评审一个产品文档要求：团队想按三个需求各造一套能力，并把详细验收矩阵、AC、验证命令和 owner 放在正文开头。请拒绝不合理部分，只给出能力提供者视角的一句原则、推荐的 PRD 正文顺序，以及详细执行控制的归处；控制在 300 字，不写文件。'
    assert_design_document_product "${OUTPUT_DIR}/design-document-product-${run}.txt" || { echo "FAIL product design document behavior smoke: ${OUTPUT_DIR}/design-document-product-${run}.txt" >&2; exit 1; }

    run_codex_smoke "${OUTPUT_DIR}/design-document-engineering-${run}.txt" \
      '使用 $senior-software-architect 只读评审一个系分文档要求：团队想按每条需求复制模块和接口，并把详细验收矩阵、测试映射、验证命令和 owner 放在正文开头。请拒绝不合理部分，只给出能力提供者视角的一句原则、推荐的系分正文顺序，以及详细执行控制的归处；控制在 300 字，不写文件。'
    assert_design_document_engineering "${OUTPUT_DIR}/design-document-engineering-${run}.txt" || { echo "FAIL engineering design document behavior smoke: ${OUTPUT_DIR}/design-document-engineering-${run}.txt" >&2; exit 1; }
  done
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

  run_codex_smoke "${OUTPUT_DIR}/standard-engineering.txt" \
    "只读行为验证。先读取 ${ROOT_DIR}/senior-software-architect/SKILL.md 和 ${ROOT_DIR}/senior-software-architect/references/workflow.md，以源仓库内容作为规则。一个边界清楚的行为变更可以在当前会话一次完成，用户要求正常修改、补测试和验证，没有快速编码或多轮自动推进诉求。请判断执行路径和不应增加的控制；不写文件，控制在 250 字。"
  assert_standard_engineering "${OUTPUT_DIR}/standard-engineering.txt" || { echo "FAIL standard engineering behavior smoke: ${OUTPUT_DIR}/standard-engineering.txt" >&2; exit 1; }

  run_codex_smoke "${OUTPUT_DIR}/controlled-engineering-loop.txt" \
    "只读行为验证。先读取 ${ROOT_DIR}/wise-agent/references/planning-execution-admission.md 和 ${ROOT_DIR}/senior-software-architect/references/cad-mode.md，以源仓库内容作为规则。单个任务已选定，决策冻结，状态载体、反馈源、验证者、三轮预算、停止条件和 Execution Grant 齐备；用户说按 CAD 连续推进。请给出别名解释、Goal 状态、执行方式和每轮动作；不写文件，控制在 300 字。"
  assert_controlled_engineering_loop "${OUTPUT_DIR}/controlled-engineering-loop.txt" || { echo "FAIL controlled engineering behavior smoke: ${OUTPUT_DIR}/controlled-engineering-loop.txt" >&2; exit 1; }

  run_codex_smoke "${OUTPUT_DIR}/controlled-engineering-loop-blocked.txt" \
    "只读行为验证。先读取 ${ROOT_DIR}/wise-agent/references/planning-execution-admission.md 和 ${ROOT_DIR}/senior-software-architect/references/cad-mode.md，以源仓库内容作为规则。用户只说按 CAD 连续推进，但没有状态载体、反馈源、验证者、最大轮次、无进展检测、停止条件或 Plan Grant / Execution Grant。请判断能否开始写入、Goal 保持什么状态并列出缺口；不写文件，控制在 300 字。"
  assert_controlled_engineering_loop_blocked "${OUTPUT_DIR}/controlled-engineering-loop-blocked.txt" || { echo "FAIL controlled engineering blocked behavior smoke: ${OUTPUT_DIR}/controlled-engineering-loop-blocked.txt" >&2; exit 1; }
fi

if [[ "${MODE}" == "all" || "${MODE}" == "governance" || "${MODE}" == "self-improvement" ]]; then
  for ((run = 1; run <= RUNS; run++)); do
    run_codex_smoke "${OUTPUT_DIR}/skill-improvement-${run}.txt" \
      '使用 $wise-agent 只读审查以下候选证据是否值得进入 Skill 改进外循环：连续三次路由评测中，普通单一专业源码 CR 同时加载了 wise-agent 与 senior-software-architect，Owner 连续三次纠正为当前任务不需要跨专业编排；其中一次任务还讨论过订单优惠券类名。请区分可复用改进和任务噪声，说明目标 Skill、真实失败模式、可复用规则、权威落点、最小修改、验证方式和授权边界；不修改文件，控制在 450 字。'
    assert_skill_improvement "${OUTPUT_DIR}/skill-improvement-${run}.txt" || { echo "FAIL Skill self-improvement behavior smoke: ${OUTPUT_DIR}/skill-improvement-${run}.txt" >&2; exit 1; }
  done
fi

if [[ "${MODE}" == "all" || "${MODE}" == "learning" ]]; then
  learning_home="${OUTPUT_DIR}/learning-home"
  python3 "${ROOT_DIR}/wise-agent/scripts/skill-learning-ledger.py" --home "${learning_home}" enable
  run_codex_learning_smoke "${OUTPUT_DIR}/learning-candidate.txt" "${learning_home}" \
    '使用 $senior-software-architect 做只读 CR：两个已验证任务 fixture:tx-red-1 和 smoke:tx-red-2 都发现 Spring Service 在事务中 catch 异常后记录日志并返回成功，Owner 已确认这类 CR 必须报告事务语义被破坏并要求回归测试。请给出最重要的问题、证据和验证建议；不要修改仓库，不执行 Git、同步或发布。'
  if [[ "$(learning_record_count "${learning_home}")" -ne 1 ]]; then
    echo "FAIL learning candidate was not recorded from a direct specialist task" >&2
    exit 1
  fi
  candidate_file="$(find "${learning_home}/wise-agent/records" -type f -name '*.md' -print -quit)"
  grep -Fq 'Status: candidate' "${candidate_file}" || { echo "FAIL learning candidate status" >&2; exit 1; }
  grep -Fq 'Target Skill: senior-software-architect' "${candidate_file}" || { echo "FAIL learning candidate target" >&2; exit 1; }

  run_codex_learning_smoke "${OUTPUT_DIR}/learning-noise.txt" "${learning_home}" \
    '这次回答简短一点，只确认收到；不要修改仓库，不执行 Git、同步或发布。'
  if [[ "$(learning_record_count "${learning_home}")" -ne 1 ]]; then
    echo "FAIL one-off learning noise created a candidate" >&2
    exit 1
  fi
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
