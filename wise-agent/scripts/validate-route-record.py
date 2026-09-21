#!/usr/bin/env python3
"""Validate the small route record used by wise-agent before execution.

The record is an internal execution contract.  It makes the selected owner,
the reason for collaboration, the checker evidence and the stop boundary
machine-checkable without trying to classify natural-language requests.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RISK_LEVELS = {"low", "medium", "high"}
REQUIRED_TASK_FIELDS = {
    "deliverable",
    "domain_object",
    "risk",
    "write_scope",
    "authorization",
}


class ContractError(ValueError):
    """Raised when a route record cannot be used safely."""


def _non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    if "\n" in value or "\r" in value:
        raise ContractError(f"{field} must be a single line")
    return value.strip()


def _string_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        requirement = "a non-empty list" if not allow_empty else "a list"
        raise ContractError(f"{field} must be {requirement}")
    result = [_non_empty_string(item, f"{field}[{index}]") for index, item in enumerate(value)]
    if len(result) != len(set(result)):
        raise ContractError(f"{field} must not contain duplicates")
    return result


def _skill_list(value: Any, field: str) -> list[str]:
    result = _string_list(value, field, allow_empty=True)
    for index, skill in enumerate(result):
        if skill != "direct" and not SKILL_ID.fullmatch(skill):
            raise ContractError(f"{field}[{index}] has invalid Skill ID: {skill!r}")
    return result


def validate_route_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ContractError("route record must be an object")
    if record.get("version") != 1:
        raise ContractError("version must be 1")

    task = record.get("task")
    if not isinstance(task, dict):
        raise ContractError("task must be an object")
    missing = sorted(REQUIRED_TASK_FIELDS - set(task))
    if missing:
        raise ContractError(f"task is missing: {', '.join(missing)}")
    for field in ("deliverable", "domain_object", "authorization"):
        _non_empty_string(task[field], f"task.{field}")
    if task["risk"] not in RISK_LEVELS:
        raise ContractError("task.risk must be low, medium or high")
    _string_list(task["write_scope"], "task.write_scope")

    route = record.get("route")
    if not isinstance(route, dict):
        raise ContractError("route must be an object")
    primary = _non_empty_string(route.get("primary"), "route.primary")
    if primary != "direct" and not SKILL_ID.fullmatch(primary):
        raise ContractError(f"route.primary has invalid Skill ID: {primary!r}")
    collaborators = _skill_list(route.get("collaborators"), "route.collaborators")
    skipped = _skill_list(route.get("skip"), "route.skip")
    if primary in collaborators or primary in skipped:
        raise ContractError("route.primary must not also be a collaborator or skipped Skill")
    if set(collaborators) & set(skipped):
        raise ContractError("route.collaborators and route.skip must be disjoint")
    _string_list(route.get("selection_basis"), "route.selection_basis")

    verification = record.get("verification")
    if not isinstance(verification, list) or not verification:
        raise ContractError("verification must be a non-empty list")
    for index, item in enumerate(verification):
        if not isinstance(item, dict):
            raise ContractError(f"verification[{index}] must be an object")
        _non_empty_string(item.get("kind"), f"verification[{index}].kind")
        _non_empty_string(item.get("evidence"), f"verification[{index}].evidence")

    _string_list(record.get("stop_conditions"), "stop_conditions")
    return record


def _valid_record() -> dict[str, Any]:
    return {
        "version": 1,
        "task": {
            "deliverable": "修复并验证 Java 服务",
            "domain_object": "Wind 订单服务",
            "risk": "medium",
            "write_scope": ["src/main", "src/test"],
            "authorization": "本地修改与运行测试",
        },
        "route": {
            "primary": "senior-software-architect",
            "collaborators": ["wind-coding-conventions", "llm-coding-hygiene"],
            "skip": ["payment-expert"],
            "selection_basis": ["交付物是代码修复", "适用 Java/Wind 工程约规"],
        },
        "verification": [
            {"kind": "target-tests", "evidence": "目标模块测试结果与源码回读"}
        ],
        "stop_conditions": ["发现超出本地写入授权的生产动作时停止"],
    }


def self_test() -> None:
    validate_route_record(_valid_record())

    cases = []
    missing_deliverable = _valid_record()
    del missing_deliverable["task"]["deliverable"]
    cases.append((missing_deliverable, "task is missing"))

    overlap = _valid_record()
    overlap["route"]["skip"].append("senior-software-architect")
    cases.append((overlap, "primary"))

    no_evidence = _valid_record()
    del no_evidence["verification"][0]["evidence"]
    cases.append((no_evidence, "verification[0].evidence"))

    for invalid, expected in cases:
        try:
            validate_route_record(invalid)
        except ContractError as error:
            if expected not in str(error):
                raise AssertionError(f"expected {expected!r}, got {error}") from error
        else:
            raise AssertionError(f"invalid route record was accepted: {expected}")
    print("OK route record contract self-test")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", type=Path, help="JSON route record to validate")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.record is None:
        parser.error("record is required unless --self-test is used")
    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
        validate_route_record(data)
    except (OSError, json.JSONDecodeError, ContractError) as error:
        print(f"FAIL route record: {error}", file=sys.stderr)
        return 1
    print(f"OK route record: {args.record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
