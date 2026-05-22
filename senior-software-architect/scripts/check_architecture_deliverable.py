#!/usr/bin/env python3
"""Check architecture deliverable completeness for high-value output types.

The script only inspects local text or an explicit local file. It does not
access the network, upload content, read secrets, or judge technical quality.
It is a deterministic completeness guard before architecture review.
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
    "architecture-plan": [
        RequiredGroup("background_and_goal", ["背景", "目标", "非目标", "成功标准"], 2),
        RequiredGroup("current_state", ["现状", "约束", "问题", "影响范围"], 1),
        RequiredGroup("core_decisions", ["核心决策", "选型", "职责", "边界", "取舍"], 2),
        RequiredGroup("contracts", ["接口契约", "入参", "出参", "错误码", "幂等", "兼容"], 2),
        RequiredGroup("data_and_consistency", ["数据方案", "事务边界", "一致性", "补偿", "对账"], 2),
        RequiredGroup("reliability_security", ["可靠性", "安全", "权限", "审计", "告警"], 2),
        RequiredGroup("verification", ["验证方案", "测试", "静态检查", "压测", "回归"], 2),
        RequiredGroup("release_and_risk", ["发布", "灰度", "回滚", "风险", "待确认"], 2),
    ],
    "system-design": [
        RequiredGroup("requirements", ["需求背景", "背景", "问题", "不做的风险"], 2),
        RequiredGroup("goal_boundary", ["目标", "非目标", "系统边界", "数据边界", "安全边界"], 3),
        RequiredGroup("overview_design", ["概要设计", "核心方案", "关键依赖", "同步", "异步"], 2),
        RequiredGroup("detail_design", ["详细设计", "模块", "类设计", "接口设计", "数据设计"], 3),
        RequiredGroup("state_or_flow", ["状态机", "主流程", "异常流程", "补偿流程", "人工介入"], 2),
        RequiredGroup("quality", ["非功能", "性能", "容量", "可用性", "兼容性", "生产就绪"], 2),
        RequiredGroup("testing", ["测试设计", "单元测试", "集成测试", "契约测试", "回归测试"], 2),
        RequiredGroup("plan", ["研发计划", "负责人", "里程碑", "验收方式"], 2),
    ],
    "code-review": [
        RequiredGroup("findings", ["发现", "P0", "P1", "P2", "P3"], 2),
        RequiredGroup("risk", ["风险", "后果", "业务", "数据", "安全", "稳定性"], 1),
        RequiredGroup("evidence", ["证据", "文件", "行号", "调用链", "状态流转", "测试缺口"], 2),
        RequiredGroup("suggestion", ["建议", "修复", "整改", "替代方案"], 1),
        RequiredGroup("verification", ["验证", "测试", "检查", "回归"], 1),
    ],
    "production-change": [
        RequiredGroup("impact", ["影响范围", "用户", "模块", "数据", "外部依赖"], 2),
        RequiredGroup("release", ["灰度", "开关", "准入条件", "退出条件"], 1),
        RequiredGroup("rollback", ["回滚", "回退", "前滚修复", "恢复方式"], 1),
        RequiredGroup("observability", ["监控", "告警", "指标", "日志", "链路"], 2),
        RequiredGroup("runbook", ["Runbook", "应急", "止血", "负责人", "升级机制"], 1),
        RequiredGroup("verification", ["验证", "测试", "压测", "数据校验", "验收"], 2),
        RequiredGroup("risk", ["风险", "残余风险", "待确认", "风险等级"], 1),
    ],
    "diagram-brief": [
        RequiredGroup("diagram_goal", ["图形目标", "用途", "目标读者", "读者"], 1),
        RequiredGroup("diagram_type", ["图形类型", "架构图", "时序图", "状态机", "ER 图", "部署图"], 1),
        RequiredGroup("engineering_anchor", ["工程落点", "模块", "接口", "部署", "监控", "验证"], 2),
        RequiredGroup("semantic_nodes", ["节点", "分组", "系统", "组件", "领域"], 2),
        RequiredGroup("semantic_edges", ["箭头", "关系", "调用", "数据流", "同步", "异步"], 1),
        RequiredGroup("assumptions", ["假设", "待确认", "风险", "边界"], 1),
        RequiredGroup("output_format", ["SVG", "输出格式", "正式图形化交付"], 1),
    ],
}

SELF_TESTS: dict[str, tuple[str, str]] = {
    "architecture-plan": (
        "背景：订单链路慢；目标：降低延迟；非目标：不改外部协议。"
        "现状：同步调用多，约束是兼容旧接口，问题影响范围是订单链路。"
        "核心决策：按边界拆应用服务并说明取舍。"
        "接口契约：入参、出参、错误码、幂等和兼容。"
        "数据方案：事务边界、一致性、补偿和对账。"
        "可靠性：超时重试；安全：权限、审计和告警。"
        "验证方案：测试、静态检查和回归。发布：灰度、回滚、风险和待确认。",
        "背景：需要优化。",
    ),
    "system-design": (
        "需求背景：解决回调超时问题；背景：订单处理慢；问题：积压；不做的风险：生产延迟。"
        "目标：降低 RT；非目标：不迁移数据库；系统边界、数据边界和安全边界明确。"
        "概要设计：核心方案、关键依赖、同步和异步关系。"
        "详细设计：模块、类设计、接口设计和数据设计。"
        "状态机：待处理到完成；主流程、异常流程、补偿流程和人工介入。"
        "非功能：性能和容量。测试设计：单元测试、集成测试和回归测试。"
        "研发计划：负责人、里程碑和验收方式。",
        "需求背景：解决回调超时问题。",
    ),
    "code-review": (
        "发现：[P1] service.java:10 事务内吞异常。风险：会造成业务、数据和稳定性后果。"
        "证据：文件、行号和调用链显示事务回滚缺失。建议：修复异常包装并补偿。"
        "验证：补测试和回归检查。",
        "发现：代码需要优化。",
    ),
    "production-change": (
        "影响范围：用户、模块、数据和外部依赖。灰度：白名单；开关：默认关闭；准入条件和退出条件明确。"
        "回滚：支持回退和前滚修复；恢复方式为关闭开关。"
        "监控：成功率和耗时；告警：错误率；指标、日志和链路齐全。"
        "Runbook：应急止血、负责人和升级机制。验证：测试、压测、数据校验和验收。"
        "风险：残余风险和待确认项已列出。",
        "影响范围：用户。",
    ),
    "diagram-brief": (
        "图形目标：说明订单链路；目标读者：研发和 SRE；图形类型：架构图。"
        "工程落点：模块、接口、部署、监控和验证。节点：系统、组件、领域；分组：应用层和基础设施层。"
        "箭头：同步调用；关系：数据流。假设：容量边界待确认；输出格式：SVG。",
        "图形目标：说明链路；图形类型：架构图。",
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
        print("FAIL architecture deliverable self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK architecture deliverable self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查架构师交付物的结构完整性")
    parser.add_argument("--kind", choices=sorted(CHECKS), help="交付物类型")
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
        print("FAIL architecture deliverable check: empty input", file=sys.stderr)
        return 2

    missing = missing_groups(args.kind, text)
    if missing:
        print(
            f"FAIL architecture deliverable check: kind={args.kind} missing " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    print(f"OK architecture deliverable check: kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
