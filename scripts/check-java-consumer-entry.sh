#!/usr/bin/env bash
# 输入为 Java 消费样本的项目目录。离线编译主源码与独立验收类，在临时目录执行公开入口并清理编译产物。
# JDK、源码或装配有误以及入口结果不符时返回非零；执行对象仅限本地已审查的合成样本。
set -euo pipefail

if [[ $# -ne 1 || ! -d "$1/src/main/java" ]]; then
  echo "用法：bash scripts/check-java-consumer-entry.sh <含 src/main/java 的消费样本项目目录>" >&2
  exit 2
fi
for tool in javac java; do
  if ! command -v "${tool}" >/dev/null; then
    echo "缺少 ${tool}，请使用已有 JDK 再运行入口验收。" >&2
    exit 2
  fi
done

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$(cd -- "$1/src/main/java" && pwd)"
tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

sources=()
while IFS= read -r -d '' file; do
  sources+=("${file}")
done < <(find "${source_dir}" -type f -name '*.java' -print0)

checker="${repo_dir}/fixtures/skill-eval/checker/OrderEntryCheck.java"
if ! javac -encoding UTF-8 -proc:none -classpath "${tmp_dir}" -d "${tmp_dir}" "${sources[@]}" "${checker}"; then
  echo "编译失败，尚未验证 OrderController.getOrderLabel。" >&2
  exit 2
fi
(cd "${tmp_dir}" && java -cp . skillcheck.OrderEntryCheck)
