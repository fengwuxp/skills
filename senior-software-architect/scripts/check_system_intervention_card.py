#!/usr/bin/env python3
"""Validate a system-intervention card read from stdin.

Input is one JSON document. Output is a JSON report on stdout. The checker is
offline and read-only; it proves structural completeness only, not causality,
solution quality, authorization, or production readiness.
"""

from __future__ import annotations

import json
import sys
from typing import Any


MODES = {"feedback", "backcasting", "combined"}
EVIDENCE_STATUSES = {"fact", "inference", "pending"}
INTERVENTION_FIELDS = (
    "action",
    "owner",
    "observation_window",
    "feedback_source",
    "success_signal",
    "failure_signal",
    "stop_condition",
    "rollback",
)


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_string(container: Any, field: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(container, dict) or not non_empty_string(container.get(field)):
        errors.append(f"{prefix}.{field}")


def require_string_list(container: Any, field: str, prefix: str, errors: list[str]) -> None:
    value = container.get(field) if isinstance(container, dict) else None
    if not isinstance(value, list) or not value or any(not non_empty_string(item) for item in value):
        errors.append(f"{prefix}.{field}")


def validate_problem(card: dict[str, Any], errors: list[str]) -> None:
    problem = card.get("problem")
    require_string(problem, "behavior_over_time", "problem", errors)
    require_string(problem, "system_boundary", "problem", errors)
    require_string_list(problem, "non_negotiable_constraints", "problem", errors)
    constraints = problem.get("non_negotiable_constraints") if isinstance(problem, dict) else None
    if isinstance(constraints, list) and any(
        non_empty_string(item) and item.strip().casefold() in {"n/a", "遵守红线"}
        for item in constraints
    ):
        errors.append("problem.non_negotiable_constraints")
    evidence = problem.get("evidence") if isinstance(problem, dict) else None
    if not isinstance(evidence, list) or not evidence:
        errors.append("problem.evidence")
        return
    for index, item in enumerate(evidence):
        prefix = f"problem.evidence[{index}]"
        require_string(item, "statement", prefix, errors)
        require_string(item, "basis", prefix, errors)
        if not isinstance(item, dict) or item.get("status") not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.status")


def validate_intervention(card: dict[str, Any], errors: list[str]) -> None:
    intervention = card.get("intervention")
    for field in INTERVENTION_FIELDS:
        require_string(intervention, field, "intervention", errors)


def validate_feedback(card: dict[str, Any], errors: list[str]) -> None:
    model = card.get("feedback_model")
    for field in ("reinforcing_loop", "balancing_loop", "leverage_point"):
        require_string(model, field, "feedback_model", errors)
    require_string_list(model, "delays", "feedback_model", errors)


def validate_backcasting(card: dict[str, Any], errors: list[str]) -> None:
    foresight = card.get("foresight")
    scenarios = foresight.get("scenarios") if isinstance(foresight, dict) else None
    if not isinstance(scenarios, list) or len(scenarios) < 2:
        errors.append("foresight.scenarios")
    else:
        for index, scenario in enumerate(scenarios):
            prefix = f"foresight.scenarios[{index}]"
            for field in ("name", "condition", "early_signal"):
                require_string(scenario, field, prefix, errors)
    require_string(foresight, "review_condition", "foresight", errors)

    target = card.get("target")
    require_string(target, "owner", "target", errors)
    controllability = target.get("controllability") if isinstance(target, dict) else None
    for field in ("controllable", "partially_controllable", "uncontrollable"):
        require_string_list(controllability, field, "target.controllability", errors)
    require_string_list(target, "forward_check", "target", errors)


def render_card(card: dict[str, Any]) -> str:
    problem = card["problem"]
    lines = [
        "### 事实与边界",
        f"- 行为变化：{problem['behavior_over_time']}",
        f"- 系统边界：{problem['system_boundary']}",
        "- 不可退让约束：" + "；".join(problem["non_negotiable_constraints"]),
        "- 证据：",
    ]
    lines.extend(
        f"  - [{item['status']}] {item['statement']}（依据：{item['basis']}）"
        for item in problem["evidence"]
    )

    if card["mode"] in {"feedback", "combined"}:
        model = card["feedback_model"]
        lines.extend(
            [
                "",
                "### 反馈模型",
                f"- 强化环：{model['reinforcing_loop']}",
                f"- 平衡环：{model['balancing_loop']}",
                "- 时间延迟：" + "；".join(model["delays"]),
                f"- 杠杆点：{model['leverage_point']}",
            ]
        )

    if card["mode"] in {"backcasting", "combined"}:
        foresight = card["foresight"]
        target = card["target"]
        controllability = target["controllability"]
        lines.extend(["", "### 前瞻与回溯", "- 情景："])
        lines.extend(
            f"  - {item['name']}：{item['condition']}；早期信号：{item['early_signal']}"
            for item in foresight["scenarios"]
        )
        lines.extend(
            [
                f"- 复核条件：{foresight['review_condition']}",
                f"- 目标 Owner：{target['owner']}",
                "- 可控：" + "；".join(controllability["controllable"]),
                "- 部分可控：" + "；".join(controllability["partially_controllable"]),
                "- 不可控：" + "；".join(controllability["uncontrollable"]),
                "- 前向校验：" + "；".join(target["forward_check"]),
            ]
        )

    intervention = card["intervention"]
    lines.extend(
        [
            "",
            "### 最小可逆干预",
            f"- 动作：{intervention['action']}",
            f"- Owner：{intervention['owner']}",
            f"- 观察窗口：{intervention['observation_window']}",
            f"- 反馈源：{intervention['feedback_source']}",
            f"- 成功信号：{intervention['success_signal']}",
            f"- 失败信号：{intervention['failure_signal']}",
            f"- 停止条件：{intervention['stop_condition']}",
            f"- 回退：{intervention['rollback']}",
        ]
    )
    return "\n".join(lines)


def validate_card(card: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(card, dict):
        errors.append("root")
        mode = None
    else:
        if card.get("version") != 1:
            errors.append("version")
        mode = card.get("mode")
        if mode not in MODES:
            errors.append("mode")
        validate_problem(card, errors)
        validate_intervention(card, errors)
        if mode in {"feedback", "combined"}:
            validate_feedback(card, errors)
        if mode in {"backcasting", "combined"}:
            validate_backcasting(card, errors)
    return {
        "status": "failed" if errors else "passed",
        "mode": mode,
        "errors": errors,
        "warnings": [],
        "proof_limit": "structure_only",
        "rendered_markdown": render_card(card) if not errors else "",
    }


def input_error(error: str) -> dict[str, Any]:
    return {
        "status": "input_error",
        "mode": None,
        "errors": [error],
        "warnings": [],
        "proof_limit": "structure_only",
        "rendered_markdown": "",
    }


def main() -> int:
    try:
        card = json.load(sys.stdin)
    except (UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps(input_error(type(exc).__name__), ensure_ascii=False, sort_keys=True))
        return 2

    report = validate_card(card)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
