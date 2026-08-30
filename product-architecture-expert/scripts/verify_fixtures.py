#!/usr/bin/env python3
"""Run public-safe fixtures through the product deliverable checker."""

from __future__ import annotations

from pathlib import Path

from check_product_deliverable import missing_groups


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
CASES = (
    ("prd", FIXTURES / "prd-valid.md", True, set()),
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
