#!/usr/bin/env python3
"""Check product deliverable completeness for high-value output types.

The script only inspects local text or an explicit local file. It does not
access the network, upload content, read secrets, or judge business quality.
It is a deterministic completeness guard before human product review.
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
    "prd": [
        RequiredGroup("goal_and_scope", ["目标", "非目标", "范围", "不做范围", "成功指标"], 3),
        RequiredGroup("actors_and_roles", ["用户", "主体", "角色", "验收方", "责任边界"], 2),
        RequiredGroup("objects_and_states", ["对象", "状态", "字段", "生命周期", "不变量", "状态机图", "对象关系图"], 2),
        RequiredGroup("flows", ["主流程", "逆向流程", "异常流程", "人工处理", "业务流程", "用例图", "流程图", "泳道图"], 2),
        RequiredGroup("rules", ["规则", "权限", "审批", "额度", "计费", "版本", "验收样例"], 2),
        RequiredGroup("data_and_audit", ["数据", "指标", "报表", "埋点", "审计", "追溯"], 2),
        RequiredGroup("risk_and_confirmation", ["风险", "依赖", "待确认", "确认方", "影响范围"], 2),
        RequiredGroup("acceptance", ["验收", "测试场景", "边界路径", "异常路径", "验收标准"], 2),
    ],
    "product-architecture": [
        RequiredGroup("business_goal", ["业务目标", "用户价值", "成功指标", "非目标"], 2),
        RequiredGroup("capability_map", ["能力地图", "能力域", "前台能力", "后台能力", "数据能力"], 1),
        RequiredGroup("domain_objects", ["业务对象", "对象模型", "字段口径", "生命周期", "状态"], 2),
        RequiredGroup("process_and_state", ["业务流程", "主流程", "异常流程", "状态机", "人工兜底"], 2),
        RequiredGroup("rule_matrix", ["规则矩阵", "触发条件", "判断逻辑", "优先级", "版本"], 2),
        RequiredGroup("operations_and_data", ["运营后台", "指标", "报表", "审计", "数据口径"], 2),
        RequiredGroup("risks_and_acceptance", ["风险", "待确认", "验收", "确认方", "发布"], 2),
    ],
    "diagram-brief": [
        RequiredGroup("diagram_goal", ["图形目标", "用途", "目标读者", "读者"], 1),
        RequiredGroup("diagram_type", ["图形类型", "能力地图", "流程图", "状态机", "产品架构图", "资金流图"], 1),
        RequiredGroup("semantic_nodes", ["节点", "分组", "角色", "对象", "系统"], 2),
        RequiredGroup("semantic_edges", ["箭头", "关系", "流向", "同步", "异步", "状态迁移"], 1),
        RequiredGroup("assumptions", ["假设", "待确认", "风险", "边界"], 1),
        RequiredGroup("output_format", ["SVG", "输出格式", "正式图形化交付"], 1),
    ],
}

SELF_TESTS: dict[str, tuple[str, str]] = {
    "prd": (
        "目标：提升运营效率；非目标：不改结算规则；范围：后台审核。"
        "用户：运营；主体：平台；角色：审核员；验收方：产品和运营。"
        "对象：申请单；状态：待审、通过、驳回；字段：amount；生命周期：创建到关闭。"
        "主流程：提交、审核、通知；异常流程：重复提交；人工处理：补录；流程图：审核路径。"
        "规则：权限、审批、版本和验收样例。数据：指标、报表、审计和追溯。"
        "风险：外部依赖待确认，确认方为业务，影响范围是审核上线。"
        "验收：验收标准、边界路径、异常路径和测试场景。",
        "目标：提升效率。",
    ),
    "product-architecture": (
        "业务目标：提升审核效率；用户价值：减少等待；非目标：不改交易规则。"
        "能力地图：能力域包含前台能力、后台能力和数据能力。"
        "业务对象：申请单；对象模型：申请、审核记录；字段口径：amount；生命周期：创建到关闭；状态：待审、通过、驳回。"
        "业务流程：提交、审核、通知；主流程和异常流程齐全；人工兜底为运营复核。"
        "规则矩阵：触发条件、判断逻辑、优先级和版本。"
        "运营后台：查询、审核和导出；指标、报表、审计和数据口径。"
        "风险：外部依赖待确认；确认方：业务；验收：产品和运营验收；发布：灰度。",
        "业务目标：提升审核效率。能力地图：后台能力。",
    ),
    "diagram-brief": (
        "图形目标：说明运营后台能力；目标读者：产品和研发；图形类型：能力地图。"
        "节点：角色、对象、系统；分组：前台和后台；箭头：审批关系；关系：数据流。"
        "假设：权限模型待确认；输出格式：SVG。",
        "图形目标：说明能力；图形类型：能力地图。",
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
        print("FAIL product deliverable self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK product deliverable self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查产品架构交付物的结构完整性")
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
        print("FAIL product deliverable check: empty input", file=sys.stderr)
        return 2

    missing = missing_groups(args.kind, text)
    if missing:
        print(
            f"FAIL product deliverable check: kind={args.kind} missing " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    print(f"OK product deliverable check: kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
