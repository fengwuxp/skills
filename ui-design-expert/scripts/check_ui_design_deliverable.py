#!/usr/bin/env python3
"""Check UI design deliverable structure before human review.

The script reads only explicit local text or a local file. It does not access
the network, write files, inspect secrets, or judge visual and usability quality.
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
    "design-brief": (
        RequiredGroup("facts_goal_scope", ("用户", "场景", "主任务", "成功", "非目标", "产品规则"), 4),
        RequiredGroup("information_architecture", ("信息架构", "关键路径", "页面层级", "导航"), 2),
        RequiredGroup(
            "states_and_recovery",
            ("状态矩阵", "loading", "empty", "error", "权限", "弱网", "失败恢复", "保留用户输入"),
            4,
        ),
        RequiredGroup("responsive", ("响应式", "窄屏", "桌面", "移动"), 2),
        RequiredGroup("accessibility", ("可访问性", "键盘", "焦点", "可访问名称", "200%", "WCAG"), 3),
        RequiredGroup("visual_system", ("视觉系统", "tokens", "组件", "颜色", "密度"), 2),
        RequiredGroup("verification", ("验证", "浏览器", "桌面", "移动", "停止", "不宣称"), 3),
    ),
    "ui-review": (
        RequiredGroup("conclusion_and_scope", ("结论", "范围", "P0", "P1", "P2", "P3"), 2),
        RequiredGroup("finding_evidence", ("触发条件", "用户影响", "证据", "页面", "组件", "状态", "源码"), 3),
        RequiredGroup("minimal_fix", ("最小修复", "修复方向", "保留", "恢复", "焦点"), 2),
        RequiredGroup("verification_and_risk", ("验证", "复测", "残余风险", "owner", "停止"), 3),
    ),
    "usability-plan": (
        RequiredGroup("question_and_scope", ("验证问题", "范围", "假设", "非目标"), 3),
        RequiredGroup("participants", ("目标用户", "参与者", "招募", "新手", "熟练", "排除"), 3),
        RequiredGroup("task_and_success", ("任务", "起点", "成功标准", "失败", "恢复", "求助"), 4),
        RequiredGroup(
            "method_and_protocol",
            ("认知走查", "任务测试", "主持人", "记录", "浏览器", "权限", "同意", "隐私"),
            4,
        ),
        RequiredGroup(
            "evidence_and_judgment",
            ("完成", "错误", "求助次数", "用时", "信心", "触发步骤", "原话", "严重度", "外推"),
            5,
        ),
        RequiredGroup(
            "retest_and_stop",
            ("复测", "Design QA", "窄屏", "键盘", "焦点", "owner", "停止", "残余风险", "不宣称"),
            4,
        ),
    ),
    "prototype-plan": (
        RequiredGroup("goal_scope", ("验证问题", "范围", "非目标", "假设", "owner"), 5),
        RequiredGroup(
            "design_system_and_components",
            ("设计系统姿态", "组件来源", "语义 tokens", "组件状态", "偏离项", "owner"),
            6,
        ),
        RequiredGroup(
            "screens_states_content",
            ("入口", "退出", "重置", "页面图", "状态图", "loading", "empty", "error", "权限", "弱网", "真实"),
            6,
        ),
        RequiredGroup(
            "interactions_and_recovery",
            (
                "交互表",
                "source",
                "trigger",
                "condition",
                "action",
                "destination",
                "feedback",
                "failure",
                "overlay",
                "setReactionsAsync",
                "保留用户输入",
                "焦点",
            ),
            7,
        ),
        RequiredGroup(
            "responsive_accessibility",
            ("响应式", "桌面", "移动", "键盘", "焦点", "可访问名称", "对比", "200%"),
            4,
        ),
        RequiredGroup(
            "evidence_and_stop",
            ("成功", "失败", "验证", "证据", "版本", "任务走查", "停止", "残余风险", "不宣称", "不证明"),
            5,
        ),
    ),
}

PROTOTYPE_LEVEL_CHECKS: dict[str, tuple[RequiredGroup, ...]] = {
    "l0": (
        RequiredGroup(
            "flow_contract_evidence",
            ("owner 确认", "页面图", "状态图", "交互表", "不证明可点击", "不证明可访问", "不证明可实现"),
            5,
        ),
    ),
    "l1": (
        RequiredGroup(
            "figma_structure",
            ("components", "Code Connect", "Figma variables", "Auto Layout", "语义命名", "annotations", "dev resources"),
            5,
        ),
        RequiredGroup(
            "figma_interaction_evidence",
            ("setReactionsAsync", "Figma preview", "frame 链接", "overlay", "返回", "重置", "不证明可点击"),
            5,
        ),
        RequiredGroup(
            "figma_code_handoff",
            (
                "exact node",
                "get_design_context",
                "get_metadata",
                "get_screenshot",
                "项目组件",
                "tokens",
                "路由",
                "状态",
                "数据模式",
                "senior-software-architect",
            ),
            6,
        ),
    ),
    "l2": (
        RequiredGroup(
            "browser_execution",
            ("浏览器", "Playwright", "URL", "表单", "请求失败", "桌面", "移动", "键盘", "焦点"),
            6,
        ),
        RequiredGroup(
            "browser_handoff",
            ("项目组件", "tokens", "路由", "状态", "数据模式", "senior-software-architect", "测试"),
            4,
        ),
    ),
}

SECTION_ORDER: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "design-brief": (
        ("section_facts", ("事实、目标与边界", "事实 / 推断 / 待确认")),
        ("section_structure", ("信息架构与关键路径", "信息架构")),
        ("section_states", ("状态矩阵与失败恢复", "状态与失败恢复")),
        ("section_accessibility", ("响应式与可访问性",)),
        ("section_visual", ("视觉系统约束", "视觉方向")),
        ("section_verification", ("验证证据与停止条件", "验证与停止条件")),
    ),
    "ui-review": (
        ("section_conclusion", ("评审结论与范围", "评审结论")),
        ("section_findings", ("Findings", "评审发现")),
        ("section_fix", ("最小修复方向", "修复建议")),
        ("section_verification", ("验证与残余风险",)),
    ),
    "usability-plan": (
        ("section_question", ("研究问题与范围", "验证问题与范围")),
        ("section_participants", ("目标用户与任务", "参与者与任务")),
        ("section_method", ("方法与执行", "验证方法与执行")),
        ("section_evidence", ("证据与判断", "观察证据与判断")),
        ("section_retest", ("复测与停止条件", "复测、风险与停止条件")),
    ),
    "prototype-plan": (
        ("section_goal", ("目标、层级与边界", "目标、原型层级与边界")),
        ("section_screens", ("页面、状态与真实内容", "页面与状态")),
        ("section_interactions", ("交互与失败恢复",)),
        ("section_handoff", ("工程交接与可访问性", "交接与可访问性")),
        ("section_verification", ("验证证据与停止条件", "验证与停止条件")),
    ),
}

HEADING_PATTERN = re.compile(r"(?m)^#{2,6}\s+(.+?)\s*$")
PLACEHOLDER_PATTERN = re.compile(r"〈[^〉\n]+〉|\{\{[^}\n]+\}\}|\bTBD\b", re.IGNORECASE)
FINDING_PATTERN = re.compile(r"(?mi)^\s*(?:(?:#{2,6}|[-*])\s*)?\[P[0-3]\]")
PROTOTYPE_LEVEL_PATTERN = re.compile(
    r"(?:选择|选定|交付层级|原型层级)\s*(?:为|是|[:：])?\s*(l[012])(?=$|[^0-9a-z])",
    re.IGNORECASE,
)
PROTOTYPE_MIN_NON_KEYWORD_SECTION_CHARS = 12
NEGATED_FIGMA_STRUCTURE = re.compile(
    r"(?:不提供|未提供|没有|缺少|无需|不需要|不采用).{0,24}"
    r"(?:components|Code Connect|Figma variables|Auto Layout|setReactionsAsync)",
    re.IGNORECASE,
)
NEGATED_CODE_HANDOFF = re.compile(
    r"(?:不提供|未提供|没有|缺少|无需|不需要|不采用).{0,24}"
    r"(?:exact node|get_design_context|get_metadata|get_screenshot)",
    re.IGNORECASE,
)
L1_NO_CODE_HANDOFF = re.compile(
    r"(?:本轮|非目标|范围外).{0,16}(?:不进入|不做|不交付|无需)(?:代码|工程)(?:实现|交接)|"
    r"仅(?:做|用于).{0,12}(?:概念|交互|可用性).{0,8}验证",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def missing_sections(kind: str, text: str) -> list[str]:
    headings = [normalize(match.group(1)) for match in HEADING_PATTERN.finditer(text)]
    missing: list[str] = []
    positions: list[int] = []
    for name, aliases in SECTION_ORDER[kind]:
        position = next(
            (index for index, heading in enumerate(headings) if any(normalize(alias) in heading for alias in aliases)),
            None,
        )
        if position is None:
            missing.append(name)
        else:
            positions.append(position)
    if not missing and positions != sorted(positions):
        missing.append("section_order")
    return missing


def has_keyword_only_section(kind: str, text: str) -> bool:
    matches = list(HEADING_PATTERN.finditer(text))
    groups = CHECKS[kind]
    if kind == "prototype-plan":
        groups += tuple(group for level_groups in PROTOTYPE_LEVEL_CHECKS.values() for group in level_groups)
    keywords = sorted(
        {
            normalize(alias)
            for group in groups
            for alias in group.aliases
        }
        | {
            normalize(alias)
            for _, aliases in SECTION_ORDER[kind]
            for alias in aliases
        },
        key=len,
        reverse=True,
    )
    required_headings = [alias for _, aliases in SECTION_ORDER[kind] for alias in aliases]
    for index, match in enumerate(matches):
        heading = normalize(match.group(1))
        if not any(normalize(alias) in heading for alias in required_headings):
            continue
        if (
            kind == "ui-review"
            and any(normalize(alias) in heading for alias in ("Findings", "评审发现"))
            and index + 1 < len(matches)
            and re.search(r"\[P[0-3]\]", matches[index + 1].group(1), re.IGNORECASE)
        ):
            continue
        body = normalize(text[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(text)])
        for keyword in keywords:
            body = body.replace(keyword, "")
        minimum_chars = PROTOTYPE_MIN_NON_KEYWORD_SECTION_CHARS if kind == "prototype-plan" else 2
        if len(re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", body)) < minimum_chars:
            return True
    return False


def missing_groups(kind: str, text: str) -> list[str]:
    normalized = normalize(text)
    missing = [
        group.name
        for group in CHECKS[kind]
        if sum(1 for alias in group.aliases if normalize(alias) in normalized) < group.min_hits
    ]
    if kind == "prototype-plan":
        selected_levels = {match.group(1).casefold() for match in PROTOTYPE_LEVEL_PATTERN.finditer(text)}
        skips_code_handoff = False
        if len(selected_levels) != 1:
            missing.append("prototype_level")
        else:
            selected_level = selected_levels.pop()
            level_groups = PROTOTYPE_LEVEL_CHECKS[selected_level]
            if selected_level == "l1" and L1_NO_CODE_HANDOFF.search(text):
                skips_code_handoff = True
                level_groups = tuple(group for group in level_groups if group.name != "figma_code_handoff")
            missing.extend(
                group.name
                for group in level_groups
                if sum(1 for alias in group.aliases if normalize(alias) in normalized) < group.min_hits
            )
            if NEGATED_FIGMA_STRUCTURE.search(text) or (
                NEGATED_CODE_HANDOFF.search(text) and not skips_code_handoff
            ):
                missing.append("negated_ui_evidence")
    missing.extend(missing_sections(kind, text))
    if has_keyword_only_section(kind, text):
        missing.append("keyword_only_section")
    if kind == "ui-review" and not FINDING_PATTERN.search(text):
        missing.append("severity_finding")
    if PLACEHOLDER_PATTERN.search(text):
        missing.append("placeholder_fields")
    return missing


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    return sys.stdin.read()


def run_self_test() -> int:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    cases = (
        ("design-brief", fixtures / "design-brief-valid.md"),
        ("ui-review", fixtures / "ui-review-valid.md"),
        ("usability-plan", fixtures / "usability-plan-valid.md"),
        ("prototype-plan", fixtures / "prototype-plan-valid.md"),
        ("prototype-plan", fixtures / "prototype-plan-l0-valid.md"),
        ("prototype-plan", fixtures / "prototype-plan-l2-valid.md"),
    )
    failures = [
        f"{kind}: {', '.join(missing)}"
        for kind, path in cases
        if (missing := missing_groups(kind, path.read_text(encoding="utf-8")))
    ]
    invalid_cases = (
        ("design-brief", "invalid-incomplete.md"),
        ("design-brief", "keyword-stuffed-invalid.md"),
        ("ui-review", "ui-review-invalid-no-severity.md"),
        ("usability-plan", "usability-plan-invalid.md"),
        ("prototype-plan", "prototype-plan-invalid.md"),
        ("prototype-plan", "prototype-plan-keyword-stuffed-invalid.md"),
        ("prototype-plan", "prototype-plan-level-invalid.md"),
    )
    for invalid_kind, invalid_name in invalid_cases:
        if not missing_groups(invalid_kind, (fixtures / invalid_name).read_text(encoding="utf-8")):
            failures.append(f"{invalid_kind}: invalid fixture unexpectedly passed: {invalid_name}")
    l1_text = (fixtures / "prototype-plan-valid.md").read_text(encoding="utf-8")
    no_code_handoff = re.sub(
        r"交接给 AI 编码时提供 exact node.*?由 `senior-software-architect` 负责。",
        "本轮仅用于交互验证，非目标是不进入代码实现或工程交接，因此不需要 exact node、get_design_context、get_metadata 或 get_screenshot。",
        l1_text,
        flags=re.DOTALL,
    )
    if missing := missing_groups("prototype-plan", no_code_handoff):
        failures.append("prototype-plan: valid L1 without code handoff failed: " + ", ".join(missing))
    negated_evidence = l1_text.replace(
        "组件优先复用现有 Figma components，并核对 Code Connect、Figma variables、Auto Layout",
        "本轮不提供 Figma components、Code Connect、Figma variables 或 Auto Layout",
    )
    if "negated_ui_evidence" not in missing_groups("prototype-plan", negated_evidence):
        failures.append("prototype-plan: negated Figma evidence unexpectedly passed")
    if failures:
        print("FAIL UI design deliverable checker self-test")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("OK UI design deliverable checker self-test")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=sorted(CHECKS))
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text")
    source.add_argument("--file")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if not args.kind:
        print("FAIL UI design deliverable: --kind is required", file=sys.stderr)
        return 2
    try:
        text = read_input(args)
    except (OSError, UnicodeError) as error:
        print(f"ERROR UI design deliverable: {error}", file=sys.stderr)
        return 2
    missing = missing_groups(args.kind, text)
    if missing:
        print(f"FAIL UI design deliverable {args.kind}: missing {', '.join(missing)}")
        return 1
    print(f"OK UI design deliverable {args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
