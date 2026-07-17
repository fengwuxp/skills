#!/usr/bin/env python3
"""Validate a portable wise-agent Goal and recovery state contract.

Input: one JSON file explicitly supplied by the caller.
Output: validation result on stdout/stderr. Writes: none. Network: none.
Failure: exits non-zero when required state, decision, budget, or recovery data is invalid.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence


STATUSES = {"Draft", "Ready", "Active", "Blocked", "Verified", "Closed", "Superseded"}
STRING_FIELDS = {
    "goal_id",
    "objective",
    "state_carrier",
    "checker",
    "recovery_entry",
    "residual_risk_owner",
}
LIST_FIELDS = {
    "success_criteria",
    "non_goals",
    "confirmed_decisions",
    "excluded_options",
    "pending_items",
    "execution_basis",
    "write_scope",
    "verification_evidence",
    "stop_conditions",
}


def read_contract(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("root must be a JSON object")
    return data


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = data.get("status")
    if status not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")

    for field in sorted(STRING_FIELDS):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string")

    for field in sorted(LIST_FIELDS):
        value = data.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{field} must be a list of non-empty strings")

    for field in ("success_criteria", "non_goals", "write_scope", "stop_conditions"):
        if isinstance(data.get(field), list) and not data[field]:
            errors.append(f"{field} must not be empty")

    maximum = data.get("max_iterations")
    no_progress = data.get("no_progress_limit")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
        errors.append("max_iterations must be a positive integer")
    if not isinstance(no_progress, int) or isinstance(no_progress, bool) or no_progress < 1:
        errors.append("no_progress_limit must be a positive integer")
    elif isinstance(maximum, int) and not isinstance(maximum, bool) and no_progress > maximum:
        errors.append("no_progress_limit must not exceed max_iterations")

    decision_fields = ("confirmed_decisions", "excluded_options", "pending_items", "execution_basis")
    if all(isinstance(data.get(field), list) for field in decision_fields):
        confirmed = set(data["confirmed_decisions"])
        excluded = set(data["excluded_options"])
        pending = set(data["pending_items"])
        basis = set(data["execution_basis"])
        if confirmed & excluded or confirmed & pending or excluded & pending:
            errors.append("confirmed, excluded, and pending decisions must be disjoint")
        if not basis <= confirmed:
            errors.append("execution_basis must contain confirmed decisions only")

    next_action = data.get("next_action")
    if status not in {"Closed", "Superseded"} and (
        not isinstance(next_action, str) or not next_action.strip()
    ):
        errors.append("next_action must be a non-empty string before closure")
    if status in {"Ready", "Active"} and isinstance(data.get("execution_basis"), list) and not data["execution_basis"]:
        errors.append(f"{status} requires at least one confirmed execution_basis decision")
    if status in {"Verified", "Closed"} and isinstance(data.get("verification_evidence"), list) and not data["verification_evidence"]:
        errors.append(f"{status} requires verification_evidence")

    return errors


def run_self_test() -> None:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    valid_errors = validate(read_contract(fixtures / "state-contract-valid.json"))
    if valid_errors:
        raise SystemExit(f"valid fixture rejected: {valid_errors}")
    invalid_errors = validate(read_contract(fixtures / "state-contract-invalid.json"))
    expected = {
        "execution_basis must contain confirmed decisions only",
        "recovery_entry must be a non-empty string",
        "no_progress_limit must not exceed max_iterations",
    }
    missing = expected - set(invalid_errors)
    if missing:
        raise SystemExit(f"invalid fixture missed errors: {sorted(missing)}; got={invalid_errors}")
    print("OK wise-agent state contract self-test")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, help="state contract JSON file")
    parser.add_argument("--self-test", action="store_true", help="run bundled fixture checks")
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0
    if args.path is None:
        parser.error("path is required unless --self-test is used")
    try:
        errors = validate(read_contract(args.path))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR {args.path}: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR {args.path}: {error}", file=sys.stderr)
        return 1
    print(f"OK wise-agent state contract: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
