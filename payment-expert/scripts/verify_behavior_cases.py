#!/usr/bin/env python3
"""Validate payment behavior-case coverage and handoff contracts.

This checker validates local JSON only. It does not run a model, access the
network, write files, or claim that an installed Skill behaves correctly.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = ROOT / "test-prompts.json"
METHOD_CARDS = ROOT / "references" / "payment-method-cards.md"
METHODS = {f"M{index:02d}" for index in range(1, 10)}
KINDS = {"should_trigger", "should_ask", "should_stop", "should_not_trigger"}
DECISIONS = {"answer", "ask", "stop", "pending", "route"}


def audit_cases(data: object) -> list[str]:
    if not isinstance(data, list) or not data:
        return ["root must be a non-empty array"]

    failures: list[str] = []
    seen_ids: set[str] = set()
    covered_methods: set[str] = set()
    negative_routes: set[str] = set()
    negative_boundaries: set[str] = set()

    for index, case in enumerate(data, start=1):
        label = f"case[{index}]"
        if not isinstance(case, dict):
            failures.append(f"{label}: must be an object")
            continue

        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            failures.append(f"{label}: id must be a non-empty string")
        elif case_id in seen_ids:
            failures.append(f"{label}: duplicate id {case_id}")
        else:
            seen_ids.add(case_id)

        query = case.get("query")
        if not isinstance(query, str) or not query.strip():
            failures.append(f"{label}: query must be a non-empty string")

        kind = case.get("kind")
        if kind not in KINDS:
            failures.append(f"{label}: kind must be one of {sorted(KINDS)}")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            failures.append(f"{label}: expected must be an object")
            continue

        skill = expected.get("skill")
        decision = expected.get("decision")
        if not isinstance(skill, str) or not skill.strip():
            failures.append(f"{label}: expected.skill must be a non-empty string")
        if decision not in DECISIONS:
            failures.append(f"{label}: expected.decision must be one of {sorted(DECISIONS)}")

        method = expected.get("method")
        must_include = expected.get("must_include")
        if kind == "should_not_trigger":
            if skill == "payment-expert":
                failures.append(f"{label}: hard negative cannot select payment-expert")
            if isinstance(skill, str):
                negative_routes.add(skill)
            boundary = case.get("boundary")
            if not isinstance(boundary, str) or not boundary.strip():
                failures.append(f"{label}: hard negative requires boundary")
            else:
                negative_boundaries.add(boundary)
        else:
            if skill != "payment-expert":
                failures.append(f"{label}: payment behavior case must select payment-expert")
            if method not in METHODS:
                failures.append(f"{label}: expected.method must be M01-M09")
            else:
                covered_methods.add(method)
            if not isinstance(must_include, list) or not must_include or not all(
                isinstance(term, str) and term.strip() for term in must_include
            ):
                failures.append(f"{label}: expected.must_include must contain non-empty strings")

    missing_methods = sorted(METHODS - covered_methods)
    if missing_methods:
        failures.append("missing method coverage: " + ", ".join(missing_methods))
    for required_route in ["product-architecture-expert", "senior-software-architect"]:
        if required_route not in negative_routes:
            failures.append(f"missing hard-negative route: {required_route}")
    for required_boundary in [
        "generic-refund",
        "generic-order",
        "generic-account",
        "inventory-ledger",
        "accounting-advice",
    ]:
        if required_boundary not in negative_boundaries:
            failures.append(f"missing hard-negative boundary: {required_boundary}")
    referenced_pressure_tests = set(
        re.findall(r"`(PT-\d{3})`", METHOD_CARDS.read_text(encoding="utf-8"))
    )
    missing_pressure_tests = sorted(referenced_pressure_tests - seen_ids)
    if missing_pressure_tests:
        failures.append("unresolved method-card pressure tests: " + ", ".join(missing_pressure_tests))
    return failures


def main() -> int:
    try:
        data = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL payment behavior cases: {exc}")
        return 1

    failures = audit_cases(data)
    if failures:
        print("FAIL payment behavior cases")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"OK payment behavior cases: {len(data)} cases, methods M01-M09 covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
