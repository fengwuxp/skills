#!/usr/bin/env python3
"""Check Harness Plan completeness for AI coding orchestration.

The script only inspects local text or an explicit local file. It does not access the network, upload content, read secrets, or judge technical quality.
It is a deterministic guard for the collaboration layer before GSD or controlled engineering work.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class RequiredGroup(NamedTuple):
    name: str
    aliases: list[str]
    min_hits: int = 1


CHECKS: dict[str, list[RequiredGroup]] = {
    "lightweight": [
        RequiredGroup("task_identity", ["Task ID", "任务", "目标"], 2),
        RequiredGroup("owner", ["Owner", "负责人", "执行者", "角色"], 1),
        RequiredGroup("write_scope", ["写入范围", "写入文件", "允许修改", "可改"], 1),
        RequiredGroup("read_scope", ["只读范围", "只读参考", "参考文档", "只读"], 1),
        RequiredGroup("order", ["依赖关系", "执行顺序", "先后顺序", "Wave", "阶段"], 1),
        RequiredGroup("validation", ["验证命令", "测试", "编译", "lint", "检查"], 1),
        RequiredGroup("stop_conditions", ["停止条件", "阻塞条件", "人工确认", "待确认"], 1),
        RequiredGroup("handoff", ["交接", "handoff", "恢复入口", "残余风险"], 1),
    ],
    "gsd-wave": [
        RequiredGroup("task_identity", ["Task ID", "任务", "原子任务", "所属阶段"], 3),
        RequiredGroup("owner", ["Owner", "负责人", "执行者", "角色"], 1),
        RequiredGroup("scope", ["写入范围", "写入文件", "只读范围", "只读参考"], 3),
        RequiredGroup("wave_boundary", ["Wave", "并行", "互不重叠", "依赖关系", "执行顺序"], 2),
        RequiredGroup("context_ledger", ["上下文账本", "阶段状态", "OpenSpec", "验证矩阵", "handoffs"], 2),
        RequiredGroup("constraints", ["禁止事项", "禁止动作", "非目标", "不得"], 1),
        RequiredGroup("validation", ["验收场景", "验证命令", "完成条件", "回归", "Review"], 2),
        RequiredGroup("handoff", ["交接要求", "handoff", "恢复入口", "回滚提示"], 1),
    ],
    "engineering-loop": [
        RequiredGroup("task_identity", ["Task ID", "任务", "目标", "阶段切片"], 2),
        RequiredGroup("owner", ["Owner", "负责人", "执行者", "角色"], 1),
        RequiredGroup("scope", ["写入范围", "写入文件", "只读范围", "只读参考"], 3),
        RequiredGroup("validation", ["验收场景", "验证命令", "测试", "编译", "完成条件"], 2),
        RequiredGroup("superpowers", ["TDD", "Review", "Refactor", "编码红线", "AI 产物复核"], 2),
        RequiredGroup("execution_grant", ["Execution Grant", "授权范围", "Git 策略", "禁止事项", "撤销方式"], 2),
        RequiredGroup("human_gate", ["人工确认", "停止条件", "阻塞条件", "待确认", "中断"], 1),
        RequiredGroup("handoff", ["交接", "handoff", "恢复入口", "回写", "残余风险"], 1),
    ],
}

SELF_TESTS: dict[str, tuple[str, str]] = {
    "lightweight": (
        "Task ID: DEMO-001。任务：补齐服务边界验证。目标：覆盖空值失败路径。"
        "Owner：助手。写入范围：src/test。只读范围：docs 和 service。"
        "执行顺序：先测试后实现。验证命令：mvn test。"
        "停止条件：公共契约变化需人工确认。交接：说明残余风险和恢复入口。",
        "任务：补测试。验证命令：mvn test。",
    ),
    "gsd-wave": (
        "Task ID: W1-001。原子任务：稳定 DTO 契约。所属阶段：Stage 1。"
        "Owner：实现 Agent。写入文件：dto 和 tests。只读参考：OpenSpec。写入范围：仅 DTO。只读范围：docs。"
        "Wave 1，任务互不重叠；依赖关系：Wave 0 完成后执行。"
        "上下文账本：01-context-ledger.md；阶段状态：03-state.md；验证矩阵：05-verification-matrix.md。"
        "禁止事项：不得改数据库。验收场景：兼容旧字段；验证命令：mvn test；完成条件：Review 通过。"
        "交接要求：写入 handoffs；回滚提示：还原 DTO diff。",
        "Task ID: W1-001。写入文件：src。验证命令：mvn test。",
    ),
    "engineering-loop": (
        "Task ID: ENG-001。任务：修复授权边界。目标：补齐失败路径。"
        "Owner：助手。写入文件：service 和 tests。写入范围：授权服务。只读参考：OpenSpec。只读范围：docs。"
        "验收场景：无权限失败；验证命令：mvn test；完成条件：测试通过。"
        "TDD：先红后绿；Review：检查编码红线；AI 产物复核：无幻觉 API。"
        "Execution Grant：授权范围限 service/tests；Git 策略 summary_only；禁止事项：不改 DTO；撤销方式：用户暂停。"
        "人工确认：公共契约变化即停止。交接：回写阶段状态、残余风险和恢复入口。",
        "Task ID: ENG-001。写入文件：service。验证命令：mvn test。",
    ),
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def missing_groups(kind: str, text: str) -> list[str]:
    normalized = normalize(text)
    missing: list[str] = []
    for group in CHECKS[kind]:
        hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
        if hits < group.min_hits:
            missing.append(group.name)
    return missing


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    return sys.stdin.read()


def run_self_test() -> int:
    failures: list[str] = []
    for kind, (valid_text, invalid_text) in SELF_TESTS.items():
        valid_missing = missing_groups(kind, valid_text)
        if valid_missing:
            failures.append(f"{kind}: valid fixture missing {', '.join(valid_missing)}")
        invalid_missing = missing_groups(kind, invalid_text)
        if not invalid_missing:
            failures.append(f"{kind}: invalid fixture unexpectedly passed")
    if failures:
        print("FAIL harness plan self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK harness plan self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 Harness Plan 的结构完整性")
    parser.add_argument("--kind", choices=sorted(CHECKS), help="Harness Plan 类型")
    parser.add_argument("--file", help="待检查的本地 Markdown/文本文件")
    parser.add_argument("--text", help="直接传入待检查文本")
    parser.add_argument("--self-test", action="store_true", help="运行内置正反例自测")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.kind:
        parser.error("--kind is required unless --self-test is used")

    text = read_input(args)
    if not text.strip():
        print("FAIL harness plan check: empty input", file=sys.stderr)
        return 2

    missing = missing_groups(args.kind, text)
    if missing:
        print(f"FAIL harness plan check: kind={args.kind} missing " + ", ".join(missing), file=sys.stderr)
        return 1

    print(f"OK harness plan check: kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
