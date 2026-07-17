#!/usr/bin/env bash
set -euo pipefail

# Input: current Codex installation, its configured provider, and this repository.
# Output: final responses under --output-dir (default: /tmp/wise-agent-smoke-<timestamp>).
# Writes: output directory only. Network: codex exec may call the configured provider.
# Failure: exits non-zero when installed Skills differ from the repository or a response misses the contract.

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="all"
OUTPUT_DIR="/tmp/wise-agent-smoke-$(date +%Y%m%d-%H%M%S)"

assert_product() {
  local file="$1" term
  for term in "事实" "推断" "待确认" "验收"; do
    grep -Fq "${term}" "${file}" || return 1
  done
}

assert_engineering() {
  local file="$1" term
  for term in "严重级别" "证据" "测试" "残余风险"; do
    grep -Fq "${term}" "${file}" || return 1
  done
}

if [[ "${1:-}" == "--self-test" ]]; then
  sample_dir="$(mktemp -d)"
  cleanup_self_test() {
    rm -f "${sample_dir}/product.txt" "${sample_dir}/engineering.txt"
    rmdir "${sample_dir}"
  }
  trap cleanup_self_test EXIT
  printf '%s\n' '事实：访谈。推断：有需求。待确认：owner。验收：场景通过。' > "${sample_dir}/product.txt"
  printf '%s\n' '严重级别：P1。证据：源码。测试：补回归。残余风险：并发。' > "${sample_dir}/engineering.txt"
  assert_product "${sample_dir}/product.txt"
  assert_engineering "${sample_dir}/engineering.txt"
  if assert_product "${sample_dir}/engineering.txt"; then
    echo "FAIL product smoke accepted an engineering-only response" >&2
    exit 1
  fi
  echo "OK wise-agent behavior smoke self-test"
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

case "${MODE}" in
  all|product|engineering) ;;
  *) echo "--mode must be all, product, or engineering" >&2; exit 2 ;;
esac

cd "${ROOT_DIR}"
scripts/validate-installed-skills.sh
mkdir -p "${OUTPUT_DIR}"

if [[ "${MODE}" == "all" || "${MODE}" == "product" ]]; then
  codex exec -c 'model_reasoning_effort="low"' --ephemeral --sandbox read-only --output-last-message "${OUTPUT_DIR}/product.txt" \
    '只读判断以下摘要是否足以进入 PRD：用户希望按等级获得不同权益，运营需要可配置并能追溯规则版本。请在 300 字内按事实、推断、待确认、验收四项答复；不写文件，不运行额外校验。'
  assert_product "${OUTPUT_DIR}/product.txt" || { echo "FAIL product behavior smoke: ${OUTPUT_DIR}/product.txt" >&2; exit 1; }
fi

if [[ "${MODE}" == "all" || "${MODE}" == "engineering" ]]; then
  codex exec -c 'model_reasoning_effort="low"' --ephemeral --sandbox read-only --output-last-message "${OUTPUT_DIR}/engineering.txt" \
    '只读 CR：一个 Spring Service 在事务提交前先删除缓存，异常被 catch 后只记录日志并返回成功。请在 300 字内按严重级别、证据、测试、残余风险四项答复；不写文件，不运行额外校验。'
  assert_engineering "${OUTPUT_DIR}/engineering.txt" || { echo "FAIL engineering behavior smoke: ${OUTPUT_DIR}/engineering.txt" >&2; exit 1; }
fi

echo "OK wise-agent behavior smoke: ${OUTPUT_DIR}"
