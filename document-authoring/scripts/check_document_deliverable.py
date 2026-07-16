#!/usr/bin/env python3
"""Check structural completeness of professional document deliverables.

The checker is offline and read-only. It does not judge factual accuracy,
writing quality, professional approval, or rendered layout.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class RequiredGroup(NamedTuple):
    name: str
    aliases: tuple[str, ...]
    min_hits: int = 1


CHECKS: dict[str, tuple[RequiredGroup, ...]] = {
    "report": (
        RequiredGroup("goal_and_audience", ("目标", "目的", "读者", "受众", "用途"), 2),
        RequiredGroup("sources", ("来源", "材料", "证据", "数据", "记录")),
        RequiredGroup("facts_and_scope", ("事实", "推断", "范围", "非目标", "待确认"), 2),
        RequiredGroup("conclusion", ("结论", "判断", "摘要")),
        RequiredGroup("actions", ("行动", "下一步", "owner", "负责人", "截止时间"), 2),
        RequiredGroup("risk_and_verification", ("风险", "限制", "验证", "验收", "复核"), 2),
    ),
    "policy": (
        RequiredGroup("purpose_and_scope", ("目的", "适用范围", "范围", "非适用"), 2),
        RequiredGroup("definitions_and_roles", ("定义", "术语", "角色", "职责", "负责人"), 2),
        RequiredGroup("rules", ("规则", "必须", "禁止", "要求"), 2),
        RequiredGroup("process_and_exceptions", ("流程", "步骤", "例外", "异常", "升级"), 2),
        RequiredGroup("records_and_review", ("记录", "留痕", "审计", "复审", "生效", "版本"), 2),
    ),
    "manual": (
        RequiredGroup("audience_and_prerequisites", ("读者", "适用对象", "前置条件", "准备"), 2),
        RequiredGroup("steps", ("步骤", "操作", "输入", "执行"), 2),
        RequiredGroup("expected_and_validation", ("预期结果", "结果", "验证", "检查", "成功标准"), 2),
        RequiredGroup("troubleshooting_and_limits", ("故障", "失败", "异常", "限制", "注意", "升级"), 2),
    ),
    "research-note": (
        RequiredGroup("question_and_scope", ("研究问题", "问题", "范围", "不讨论"), 2),
        RequiredGroup("sources", ("来源", "材料", "证据", "版本", "出处"), 2),
        RequiredGroup("facts_and_inferences", ("事实", "推断", "待确认", "材料可证"), 2),
        RequiredGroup("analysis_and_disagreement", ("分析", "观点", "争议", "冲突", "反证"), 2),
        RequiredGroup("conclusion_and_limits", ("结论", "局限", "限制", "待考", "置信度"), 2),
    ),
}


SELF_TESTS: dict[str, tuple[str, str]] = {
    "report": (
        "目标：形成交付判断。目标读者：项目 owner。来源：会议记录和测试数据。"
        "事实：验证已执行；范围：当前模块；待确认由业务 owner 复核。"
        "结论：暂不发布。下一步行动：负责人补齐证据。风险：错误放行。验证：重新检查。",
        "标题：项目报告。",
    ),
    "policy": (
        "目的：规范评审。适用范围：研发团队。定义：正式评审；角色与职责：owner 审批。"
        "规则：必须留痕，禁止跳过复核。流程：提交后评审；例外：紧急变更需升级。"
        "记录：保存结论；审计：季度复审；生效版本：v1。",
        "目的：规范评审。",
    ),
    "manual": (
        "适用对象：维护者；前置条件：本地环境可用。步骤：运行检查；输入：文档路径。"
        "预期结果：输出 OK；验证：检查退出码。失败处理：保留日志；限制：不判断事实；升级：交 owner。",
        "步骤：运行命令。",
    ),
    "research-note": (
        "研究问题：解释术语变化；范围：指定材料。来源：原始文献；出处和版本已记录。"
        "事实：材料可证；推断：可能存在变化。分析：比较语境；争议：两种观点并存；反证已列出。"
        "结论：暂取通说；局限：材料不足；待考：新增材料；置信度：中。",
        "问题：解释术语。结论：采用常见说法。",
    ),
}

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"
INVALID_FIXTURES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "report",
        "invalid-placeholder-report.md",
        ("placeholder_required_fields",),
    ),
)

REQUIRED_VALUE_FIELDS: dict[str, tuple[str, ...]] = {
    "report": ("目标", "目的", "读者", "受众", "来源", "事实", "结论", "行动", "下一步", "负责人", "验证"),
    "policy": ("目的", "适用范围", "定义", "角色", "职责", "规则", "流程", "记录", "复审", "生效"),
    "manual": ("读者", "适用对象", "前置条件", "步骤", "预期结果", "验证", "故障处理"),
    "research-note": ("研究问题", "问题", "范围", "来源", "事实", "分析", "结论", "局限"),
}
PLACEHOLDER_VALUE = re.compile(
    r"^(?:无|无人|暂无|待补|未知|不明|未执行|未验证|未核验|无需查|无须查|不适用|N/?A|TBD|TODO|[-—/]+)$",
    re.IGNORECASE,
)
PLACEHOLDER_PREFIXES = (
    "待补",
    "待完善",
    "待定",
    "稍后补",
    "后续补",
    "未提供",
    "未填写",
)
FIELD_ASSIGNMENT = re.compile(r"(?:^|[。；;\n|])\s*(?:[-*]\s*)?([^：:]+)[：:]\s*([^。；;\n|]*)")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def is_placeholder_value(value: str) -> bool:
    normalized = normalize(value)
    return bool(PLACEHOLDER_VALUE.fullmatch(normalized)) or normalized.startswith(PLACEHOLDER_PREFIXES)


def has_placeholder_required_field(kind: str, text: str) -> bool:
    required_fields = REQUIRED_VALUE_FIELDS[kind]
    for match in FIELD_ASSIGNMENT.finditer(text):
        field, value = (part.strip() for part in match.groups())
        if any(alias in field for alias in required_fields) and is_placeholder_value(value):
            return True
    return False


def missing_groups(kind: str, text: str) -> list[str]:
    normalized = normalize(text)
    missing: list[str] = []
    for group in CHECKS[kind]:
        hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
        if hits < group.min_hits:
            missing.append(group.name)
    if re.search(r"\b(?:TBD|TODO)\b|待确认", text, re.IGNORECASE):
        if not any(term in normalized for term in ("owner", "负责人", "确认方")):
            missing.append("placeholder_owner")
    if has_placeholder_required_field(kind, text):
        missing.append("placeholder_required_fields")
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
        if not missing_groups(kind, invalid_text):
            failures.append(f"{kind}: invalid fixture unexpectedly passed")
    for kind, fixture_name, expected_missing in INVALID_FIXTURES:
        fixture_text = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8")
        actual_missing = set(missing_groups(kind, fixture_text))
        absent = [name for name in expected_missing if name not in actual_missing]
        if absent:
            failures.append(f"{fixture_name}: expected missing {', '.join(absent)}")
    placeholder_variant = (
        "目标：待补充；读者：待补充；来源：待补充；事实：待补充；范围：待补充；"
        "结论：待补充；下一步行动：待补充；负责人：待补充；风险：待补充；验证：待补充。"
    )
    if "placeholder_required_fields" not in missing_groups("report", placeholder_variant):
        failures.append("report: common placeholder variant unexpectedly passed")
    if failures:
        print("FAIL document deliverable self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK document deliverable self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查专业文档交付物的结构完整性")
    parser.add_argument("--kind", choices=sorted(CHECKS), help="文档类型")
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
        print("FAIL document deliverable check: empty input", file=sys.stderr)
        return 2

    missing = missing_groups(args.kind, text)
    if missing:
        print(
            f"FAIL document deliverable check: kind={args.kind} missing " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    print(f"OK document deliverable check: kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
