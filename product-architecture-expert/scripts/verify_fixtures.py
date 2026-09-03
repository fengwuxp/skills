#!/usr/bin/env python3
"""Run public-safe fixtures through the product deliverable checker."""

from __future__ import annotations

import re
from pathlib import Path

from check_product_deliverable import missing_groups, warning_groups
from check_product_qualification import check as qualification_issues


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
CASES = (
    ("prd", FIXTURES / "prd-light-readable-valid.md", True, set()),
    ("prd", FIXTURES / "prd-valid.md", True, set()),
    ("prd", FIXTURES / "prd-enhanced-readable-valid.md", True, set()),
    (
        "prd",
        FIXTURES / "prd-invalid.md",
        False,
        {"scenario_contract_missing", "rule_scope_missing", "acceptance_scenario_missing"},
    ),
    (
        "prd",
        FIXTURES / "prd-invalid-ambiguous-rule.md",
        False,
        {"ambiguous_rule_language"},
    ),
    (
        "prd",
        FIXTURES / "prd-invalid-requirement-contract.md",
        False,
        {"requirement_contract_incomplete"},
    ),
    (
        "prd",
        FIXTURES / "prd-invalid-external-rule.md",
        False,
        {"external_rule_governance_missing"},
    ),
    (
        "prd",
        FIXTURES / "prd-invalid-success-metric.md",
        False,
        {"success_metric_incomplete"},
    ),
    ("business-architecture", FIXTURES / "business-architecture-valid.md", True, set()),
    ("business-architecture", FIXTURES / "business-architecture-invalid.md", False, set()),
    ("product-review", FIXTURES / "product-review-valid.md", True, set()),
    ("product-review", FIXTURES / "product-review-invalid.md", False, set()),
    ("prototype-scope-plan", FIXTURES / "prototype-scope-plan-valid.md", True, set()),
    (
        "prototype-scope-plan",
        FIXTURES / "prototype-scope-plan-invalid.md",
        False,
        {
            "covered_carrier_missing",
            "requirement_coverage_invalid",
            "requirement_trace_missing",
            "required_coverage_missing",
            "unknown_carrier_reference",
            "unknown_requirement_trace",
            "orphan_carrier",
            "unresolved_coverage_owner_missing",
            "unresolved_coverage_handling_missing",
        },
    ),
)
EXACT_FAILURE_CASES = {
    "prd-invalid-ambiguous-rule.md",
    "prd-invalid-requirement-contract.md",
    "prd-invalid-external-rule.md",
    "prd-invalid-success-metric.md",
}


def main() -> int:
    failures: list[str] = []
    for kind, path, should_pass, expected_missing in CASES:
        if not path.exists():
            failures.append(f"missing fixture: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            missing = missing_groups(kind, text)
        except KeyError:
            failures.append(f"fixture kind not supported: {kind}")
            continue
        passed = not missing
        if kind == "prd" and should_pass:
            qualification_missing = qualification_issues(text)
            if qualification_missing:
                failures.append(
                    f"fixture qualification failed: {path.name}: "
                    f"issues={','.join(qualification_missing)}"
                )
        if passed != should_pass:
            failures.append(
                f"fixture expectation failed: {path.name}: "
                f"expected {'pass' if should_pass else 'fail'}, missing={','.join(missing) or 'none'}"
            )
        elif not expected_missing.issubset(set(missing)):
            failures.append(
                f"fixture failure reason mismatch: {path.name}: "
                f"expected={','.join(sorted(expected_missing))}, missing={','.join(missing) or 'none'}"
            )
        elif path.name in EXACT_FAILURE_CASES and set(missing) != expected_missing:
            failures.append(
                f"fixture has non-target failures: {path.name}: "
                f"expected={','.join(sorted(expected_missing))}, missing={','.join(missing) or 'none'}"
            )
        else:
            print(f"OK product fixture {path.name}")

    current_prd = (FIXTURES / "prd-valid.md").read_text(encoding="utf-8")
    contract_cases = (
        (
            current_prd.replace("当前版本：1.0。\n", "", 1),
            "document_control_incomplete",
            "formal PRD without document control",
        ),
        (
            current_prd.replace(
                "- 产品架构主脊：缩短审核时长 -> SCN-001 -> 审核裁决能力 -> 申请 / 审核任务及状态 -> R-001 -> 可查询且不可覆盖的结论。\n",
                "",
                1,
            ),
            "architecture_spine_incomplete",
            "standard PRD without an architecture spine",
        ),
        (
            current_prd.replace("- 产品接口名称：审核申请裁决。\n", "", 1),
            "product_interface_contract_incomplete",
            "generic product interface claim",
        ),
    )
    for candidate, expected_issue, label in contract_cases:
        if expected_issue not in missing_groups("prd", candidate):
            failures.append(f"{label} unexpectedly passed")

    authority_boundary_prd = current_prd.replace("权威来源：", "权威边界：", 1)
    if "document_control_incomplete" in missing_groups("prd", authority_boundary_prd):
        failures.append("authority boundary equivalent document control was rejected")

    combined_owner_prd = current_prd.replace(
        "产品 owner：审核产品负责人。\n业务 owner：运营负责人。",
        "owner：审核产品负责人、运营负责人。",
        1,
    )
    if "document_control_incomplete" not in missing_groups("prd", combined_owner_prd):
        failures.append("combined owner unexpectedly satisfied product and business ownership")

    equivalent_spine_prd = (
        current_prd
        .replace("产品架构主脊：", "概要主链：", 2)
        .replace("核心能力：", "能力地图：", 1)
        .replace("核心对象与关系：", "核心名相：", 1)
        .replace("关键交互与边界：", "参与方与责任：", 1)
        .replace("关键图 / 不画图理由：", "产品视图：", 1)
    )
    if "architecture_spine_incomplete" in missing_groups("prd", equivalent_spine_prd):
        failures.append("equivalent early architecture projection was rejected")

    compact_interface = """### 产品接口抽象

产品接口矩阵只固定业务输入、输出、失败语义和责任边界。

| 产品能力 | 输入与前置 | 输出与失败语义 |
| --- | --- | --- |
| 审核申请裁决 | 待审申请、完整材料、审核权限和可用材料来源 | 返回通过或驳回；非待审返回原结论，来源不可用时保持待审并由运营承接。 |

"""
    compact_interface_prd = re.sub(
        r"(?ms)^### 产品接口抽象\n.*?(?=^## 七、数据与风险)",
        compact_interface,
        current_prd,
        count=1,
    )
    compact_interface_missing = missing_groups("prd", compact_interface_prd)
    if "product_interface_contract_incomplete" in compact_interface_missing:
        failures.append("compact product interface matrix was rejected")
    if "compact_product_interface_contract" not in warning_groups(
        "prd", compact_interface_prd
    ):
        failures.append("compact product interface matrix did not emit compatibility warning")

    goal_mechanism_prd = current_prd.replace(
        "目标：缩短审核处理时间；非目标：不改结算规则。",
        "目标：通过 resourceId、httpMethod、Provider 路由和 scopeType 并集实现审核权限；非目标：不改结算规则。",
        1,
    )
    if "goal_mechanism_leak" not in warning_groups("prd", goal_mechanism_prd):
        failures.append("goal containing identifier and aggregation mechanisms was not warned")

    non_goal_current_concept_prd = current_prd.replace(
        "非目标：不改结算规则。",
        "非目标：不建设 `OrganizationDirectoryConnection`。",
        1,
    ).replace(
        "## 四、概要设计",
        """#### 核心概念与业务口径（本期投影）

| 概念 | 类型 | 本 PRD 中的定义 | 边界 / 不等于 | 状态 | Owner / 权威来源 |
| --- | --- | --- | --- | --- | --- |
| `OrganizationDirectoryConnection` | 技术机制 | 外部目录连接。 | 不等于审核任务。 | 当前 | 审核产品负责人 / 本 PRD。 |

## 四、概要设计""",
        1,
    )
    if "non_goal_current_concept_conflict" not in warning_groups(
        "prd", non_goal_current_concept_prd
    ):
        failures.append("current concept explicitly excluded by non-goal was not warned")

    api_product_goal_prd = current_prd.replace(
        "目标：缩短审核处理时间；非目标：不改结算规则。",
        "目标：为开发者提供稳定 API 产品并缩短接入时间；非目标：不定义调用方内部实现。",
        1,
    )
    if "goal_mechanism_leak" in warning_groups("prd", api_product_goal_prd):
        failures.append("API product outcome was incorrectly warned as a goal mechanism leak")

    no_history_baseline_prd = re.sub(
        r"成功指标：.*?Owner 为运营负责人。",
        "成功指标：无历史基线；基线建立方式：上线前回放最近 30 天申请；"
        "目标状态：无版本结论比例为 0%；观察窗口为上线后 30 天；"
        "Owner 为运营负责人。",
        current_prd,
        count=1,
    )
    if "success_metric_incomplete" in missing_groups("prd", no_history_baseline_prd):
        failures.append("measured no-history baseline unexpectedly failed")

    light_prd = (FIXTURES / "prd-light-readable-valid.md").read_text(encoding="utf-8")
    light_without_complete_scenario = re.sub(
        r"(?ms)^### SCN-001.*?(?=^## 四、)",
        "业务场景：用户保存失败后看到提示。\n\n",
        light_prd,
        count=1,
    )
    if "lightweight_scenario_incomplete" not in missing_groups(
        "prd", light_without_complete_scenario
    ):
        failures.append("lightweight PRD without a complete scenario unexpectedly passed")

    light_without_atomic_requirement = (
        light_prd
        .replace("规范强度：必须。", "", 1)
        .replace(
            "要求的行为或业务结果：明确显示未保存并保留用户输入和重试入口。",
            "",
            1,
        )
    )
    if "lightweight_requirement_incomplete" not in missing_groups(
        "prd", light_without_atomic_requirement
    ):
        failures.append("lightweight PRD without an atomic requirement unexpectedly passed")

    light_with_weak_acceptance = re.sub(
        r"(?ms)^## 六、验收摘要.*$",
        "## 六、验收摘要\n\n业务结果：页面正常。验收标准：测试通过。",
        light_prd,
        count=1,
    )
    if "lightweight_acceptance_incomplete" not in missing_groups(
        "prd", light_with_weak_acceptance
    ):
        failures.append("lightweight PRD with non-observable acceptance unexpectedly passed")

    if "## 六、关键流程" in current_prd:
        failures.append("single-scenario fixture kept a redundant shared-flow section")
    readable_single_missing = missing_groups("prd", current_prd)
    if readable_single_missing:
        failures.append(
            "readable single-scenario PRD unexpectedly failed: "
            + ",".join(readable_single_missing)
        )

    compact_requirement_prd = current_prd
    if "requirement_contract_incomplete" in missing_groups(
        "prd", compact_requirement_prd
    ):
        failures.append("compact requirement projection unexpectedly failed")
    incomplete_compact_requirement = compact_requirement_prd.replace(
        "保存唯一审核结论 / 功能。",
        "保存唯一审核结论。",
        1,
    )
    if "requirement_contract_incomplete" not in missing_groups(
        "prd", incomplete_compact_requirement
    ):
        failures.append("compact requirement without a type unexpectedly passed")
    repeated_compact_requirement = compact_requirement_prd.replace(
        "- 责任主体 / 场景 / 前置状态：审核平台 / SCN-001 / 申请待审。\n",
        "- 责任主体 / 场景 / 前置状态：审核平台 / SCN-001 / 申请待审。\n"
        "- 需求名称 / 类型：发送审核通知 / 功能。\n",
        1,
    )
    if "requirement_contract_incomplete" not in missing_groups(
        "prd", repeated_compact_requirement
    ):
        failures.append("multiple compact requirements unexpectedly completed each other")

    compact_rule_prd = current_prd
    if "rule_contract_incomplete" in missing_groups("prd", compact_rule_prd):
        failures.append("compact rule projection unexpectedly failed")
    incomplete_compact_rule = compact_rule_prd.replace(
        "申请待审、材料完整、来源可用且审核员有权限 / 记录通过或驳回结论并保留操作者和时间 / 运营负责人。",
        "申请待审、材料完整、来源可用且审核员有权限 / 记录通过或驳回结论并保留操作者和时间。",
        1,
    )
    if "rule_contract_incomplete" not in missing_groups(
        "prd", incomplete_compact_rule
    ):
        failures.append("compact rule without an Owner unexpectedly passed")
    repeated_compact_rule = compact_rule_prd.replace(
        "- 适用场景 / 步骤：SCN-001 / 审核裁决。\n",
        "- 适用场景 / 步骤：SCN-001 / 审核裁决。\n"
        "- 规则名称 / 性质 / 业务动机：审核通知 / 场景裁决规则 / 告知结果。\n",
        1,
    )
    if "rule_contract_incomplete" not in missing_groups("prd", repeated_compact_rule):
        failures.append("multiple compact rules unexpectedly completed each other")

    scenario = re.search(
        r"(?ms)^### SCN-001 运营审核申请\n.*?(?=^### 产品需求陈述)",
        current_prd,
    )
    if scenario is None:
        failures.append("readable scenario fixture missing")
    else:
        two_scenarios_without_flow = current_prd.replace(
            "### 产品需求陈述",
            scenario.group(0).replace("SCN-001", "SCN-002", 1)
            + "### 产品需求陈述",
            1,
        ).replace("对应场景：SCN-001。", "对应场景：SCN-001、SCN-002。", 1)
        independent_scenarios = two_scenarios_without_flow.replace(
            "以下场景说明申请单如何形成可追踪的审核结论。",
            "场景关系：独立。以下场景分别形成审核结论。",
            1,
        )
        if missing_groups("prd", independent_scenarios):
            failures.append("independent scenarios without a shared flow unexpectedly failed")

        missing_relationship = missing_groups("prd", two_scenarios_without_flow)
        if "scenario_relationship_missing" not in missing_relationship:
            failures.append("multiple scenarios without a relationship unexpectedly passed")

        serial_scenarios = two_scenarios_without_flow.replace(
            "以下场景说明申请单如何形成可追踪的审核结论。",
            "场景关系：串联。SCN-001 完成后进入 SCN-002。",
            1,
        )
        if "cross_scenario_flow_missing" not in missing_groups(
            "prd", serial_scenarios
        ):
            failures.append("related scenarios without an end-to-end flow unexpectedly passed")

        embedded_flow_section = (
            "### 跨场景端到端流程\n\n"
            "1. SCN-001 形成审核结论后，平台把申请交给 SCN-002 继续处理。\n"
            "2. SCN-002 完成后保存最终状态并通知运营。\n\n"
        )
        related_scenarios_with_flow = serial_scenarios.replace(
            "### 产品需求陈述",
            embedded_flow_section + "### 产品需求陈述",
            1,
        )
        related_missing = missing_groups("prd", related_scenarios_with_flow)
        if related_missing:
            failures.append(
                "related scenarios with an embedded end-to-end flow unexpectedly failed: "
                + ",".join(related_missing)
            )

        misplaced_embedded_flow = related_scenarios_with_flow.replace(
            embedded_flow_section,
            "",
            1,
        ).replace(
            "## 八、验收摘要",
            embedded_flow_section + "## 八、验收摘要",
            1,
        )
        if "conditional_flow_order" not in missing_groups(
            "prd", misplaced_embedded_flow
        ):
            failures.append("misplaced embedded end-to-end flow unexpectedly passed")

        invalid_relationship = two_scenarios_without_flow.replace(
            "以下场景说明申请单如何形成可追踪的审核结论。",
            "场景关系：循环。两个场景相互依赖。",
            1,
        )
        if "scenario_relationship_invalid" not in missing_groups(
            "prd", invalid_relationship
        ):
            failures.append("unsupported scenario relationship unexpectedly passed")

        negated_relationship = two_scenarios_without_flow.replace(
            "以下场景说明申请单如何形成可追踪的审核结论。",
            "场景关系：非独立。两个场景需要另行判断。",
            1,
        )
        if "scenario_relationship_invalid" not in missing_groups(
            "prd", negated_relationship
        ):
            failures.append("negated scenario relationship unexpectedly passed")

    enhanced_prd = (FIXTURES / "prd-enhanced-readable-valid.md").read_text(encoding="utf-8")
    shared_flow = re.search(
        r"(?ms)^### 跨场景端到端流程\n.*?(?=^### 产品需求陈述)",
        enhanced_prd,
    )
    if shared_flow is None:
        failures.append("enhanced fixture embedded cross-scenario flow missing")
    else:
        misplaced_flow = enhanced_prd.replace(shared_flow.group(0), "", 1).replace(
            "## 八、验收摘要",
            shared_flow.group(0) + "## 八、验收摘要",
            1,
        )
        if "conditional_flow_order" not in missing_groups("prd", misplaced_flow):
            failures.append("misplaced conditional flow unexpectedly passed")
    if "## 六、关键流程" in enhanced_prd:
        failures.append("enhanced canonical fixture kept a legacy shared-flow section")

    incomplete_scenario = re.sub(
        r"(?ms)^### SCN-001 运营审核申请\n.*?(?=^### 产品需求陈述)",
        """### SCN-001 运营审核申请

- 场景说明：审核员处理申请。
- 参与者：审核员。
- 流程：执行审核。
- 业务结果：申请结束。
- 异常处理：失败时停止。
- 适用规则：R-001。

""",
        (FIXTURES / "prd-valid.md").read_text(encoding="utf-8"),
        count=1,
    )
    if "scenario_contract_incomplete" not in missing_groups("prd", incomplete_scenario):
        failures.append("scenario without explicit acceptance unexpectedly passed")

    html_plan = (FIXTURES / "prototype-scope-plan-valid.md").read_text(encoding="utf-8").replace(
        "Owner：产品负责人。",
        "Owner：产品负责人。\n原型交付形态：standalone-html。",
        1,
    )
    html_plan_missing = set(missing_groups("prototype-scope-plan", html_plan))
    if "html_annotation_contract_missing" not in html_plan_missing:
        failures.append(
            "standalone HTML prototype without annotation contract unexpectedly passed"
        )

    html_contract = """

## HTML 原型标注契约

原型修订：r1。
默认模式：experience。
审阅入口：review-query-or-toggle。
标注数据源：embedded-json。
模式隔离：preserve-task-state。
可访问性：keyboard-and-name。

| 标注 ID | 承接 ID | HTML 锚点 | 类型 | 事实状态 | 需求 ID | AC ID | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ANN-001 | PAGE-C-001 | #claim-button | rule | confirmed | REQ-001 | AC-001 | C 端产品 |
| ANN-002 | STATE-C-001-SUCCESS | #claim-success | interaction | confirmed | REQ-001 | AC-002 | C 端产品 |
"""
    valid_html_plan = html_plan + html_contract
    valid_html_missing = missing_groups("prototype-scope-plan", valid_html_plan)
    if valid_html_missing:
        failures.append(
            "valid standalone HTML annotation contract failed: " + ",".join(valid_html_missing)
        )

    unstable_anchor_plan = valid_html_plan.replace("#claim-button", "main > div:nth-child(2)", 1)
    if "html_annotation_anchor_invalid" not in missing_groups(
        "prototype-scope-plan", unstable_anchor_plan
    ):
        failures.append("unstable HTML annotation anchor unexpectedly passed")

    missing_required_annotation_plan = valid_html_plan.replace(
        "| ANN-002 | STATE-C-001-SUCCESS | #claim-success | interaction | confirmed | REQ-001 | AC-002 | C 端产品 |\n",
        "",
        1,
    )
    if "html_annotation_required_coverage_missing" not in missing_groups(
        "prototype-scope-plan", missing_required_annotation_plan
    ):
        failures.append("required HTML prototype state without annotation unexpectedly passed")

    contradictory_contract_plan = (
        valid_html_plan
        .replace("标注数据源：embedded-json。", "标注数据源：standalone-word。")
        .replace("模式隔离：preserve-task-state。", "模式隔离：reset-task-state。")
        .replace("可访问性：keyboard-and-name。", "可访问性：mouse-only。")
    )
    if "html_annotation_contract_invalid" not in missing_groups(
        "prototype-scope-plan", contradictory_contract_plan
    ):
        failures.append("contradictory HTML annotation contract unexpectedly passed")

    missing_fact_reference_plan = valid_html_plan.replace(
        "| ANN-001 | PAGE-C-001", "| ANN-999 | PAGE-C-001", 1
    )
    if "html_annotation_fact_reference_missing" not in missing_groups(
        "prototype-scope-plan", missing_fact_reference_plan
    ):
        failures.append("HTML annotation without product fact reference unexpectedly passed")

    non_page_annotation_plan = valid_html_plan + (
        "| ANN-003 | CAP-OPS-NOTIFY | #notify-job | trace | confirmed | REQ-002 | AC-003 | 运营产品 |\n"
    )
    if "html_annotation_non_page_carrier" not in missing_groups(
        "prototype-scope-plan", non_page_annotation_plan
    ):
        failures.append("non-page HTML annotation unexpectedly passed")

    generic_l2_plan = (FIXTURES / "prototype-scope-plan-valid.md").read_text(encoding="utf-8").replace(
        "Owner：产品负责人。",
        "Owner：产品负责人。\n原型交付形态：L2 浏览器原型。",
        1,
    )
    if missing_groups("prototype-scope-plan", generic_l2_plan):
        failures.append("generic L2 browser prototype unexpectedly required standalone HTML annotations")

    branch_cases = [
        (
            valid_html_plan.replace("原型修订：r1。\n", "", 1),
            "html_annotation_contract_incomplete",
            "missing prototype revision",
        ),
        (
            valid_html_plan.replace("审阅入口：review-query-or-toggle。\n", "", 1),
            "html_annotation_contract_incomplete",
            "missing HTML annotation contract field",
        ),
        (
            valid_html_plan.replace("| ANN-001 | PAGE-C-001 | #claim-button | rule | confirmed", "| ANN-001 | PAGE-C-001 | #claim-button | magic | accepted", 1),
            "html_annotation_invalid",
            "invalid HTML annotation type and status",
        ),
        (
            valid_html_plan.replace(
                "| ANN-002 | STATE-C-001-SUCCESS | #claim-success",
                "| ANN-001 | STATE-C-001-SUCCESS | #claim-success",
                1,
            ),
            "duplicate_html_annotation_id",
            "duplicate HTML annotation ID",
        ),
        (
            valid_html_plan.replace("| ANN-001 | PAGE-C-001 | #claim-button", "| ANN-001 | PAGE-MISSING | #claim-button", 1),
            "unknown_html_annotation_carrier",
            "unknown HTML annotation carrier",
        ),
        (
            valid_html_plan.replace("| ANN-001 | PAGE-C-001 | #claim-button | rule | confirmed | REQ-001", "| ANN-001 | PAGE-C-001 | #claim-button | rule | confirmed | REQ-999", 1),
            "unknown_html_annotation_requirement",
            "unknown HTML annotation requirement",
        ),
        (
            valid_html_plan.replace("| ANN-001 | PAGE-C-001 | 会员权益", "| ANN-001 | PAGE-C-001 |  |", 1),
            "html_annotation_product_facts_invalid",
            "incomplete product annotation fact",
        ),
    ]
    for candidate, expected_issue, label in branch_cases:
        if expected_issue not in missing_groups("prototype-scope-plan", candidate):
            failures.append(f"{label} unexpectedly passed")

    if failures:
        print("FAIL product fixture verification")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Product fixture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
