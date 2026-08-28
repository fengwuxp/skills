#!/usr/bin/env python3
"""Validate candidate system-intervention card structure.

Input is one JSON document on stdin. Output is a JSON report on stdout. The
checker is offline and read-only; it proves structural completeness
only, not causality, solution quality, authorization, or production readiness.
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
    }


def input_error(error: str) -> dict[str, Any]:
    return {
        "status": "input_error",
        "mode": None,
        "errors": [error],
        "warnings": [],
        "proof_limit": "structure_only",
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
