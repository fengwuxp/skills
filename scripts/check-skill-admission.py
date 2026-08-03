#!/usr/bin/env python3
"""Validate repository Skill admission metadata.

Input: optional top-level skill directory and local admission.json.
Output: validation failures or the declared status.
Writes/network: normal checks write nothing and never use network; self-test writes only to a temporary directory. Missing admission.json is rejected.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"installable", "candidate"}
ISO_DATE = re.compile(r"^20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")
SKILL_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def read_metadata(skill_dir: Path) -> tuple[dict[str, Any], list[str]]:
    path = skill_dir / "admission.json"
    if not path.exists():
        return {}, [f"{path}: missing admission.json"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"{path}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"{path}: root must be an object"]
    return data, []


def audit_skill(skill_dir: Path) -> tuple[str, list[str]]:
    data, failures = read_metadata(skill_dir)
    if failures:
        return "invalid", failures

    label = skill_dir / "admission.json"
    status = data.get("status", "")
    if status not in STATUSES:
        failures.append(f"{label}: status must be installable or candidate")
        return "invalid", failures

    blockers = data.get("blockers", [])
    if not isinstance(blockers, list):
        failures.append(f"{label}: blockers must be an array")
        blockers = []
    if status == "candidate" and not blockers:
        failures.append(f"{label}: candidate requires at least one blocker")
    if status == "installable" and blockers:
        failures.append(f"{label}: installable Skill cannot retain blockers")

    for index, blocker in enumerate(blockers, start=1):
        if not isinstance(blocker, dict):
            failures.append(f"{label}: blocker[{index}] must be an object")
            continue
        for field in ["id", "summary", "owner"]:
            value = blocker.get(field)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"{label}: blocker[{index}].{field} must be non-empty")

    requires = data.get("requires", [])
    if not isinstance(requires, list):
        failures.append(f"{label}: requires must be an array")
        requires = []
    seen_requires: set[str] = set()
    for index, dependency in enumerate(requires, start=1):
        if not isinstance(dependency, str) or not SKILL_ID.fullmatch(dependency):
            failures.append(f"{label}: requires[{index}] must be a valid Skill ID")
            continue
        if dependency == skill_dir.name:
            failures.append(f"{label}: Skill cannot require itself")
        if dependency in seen_requires:
            failures.append(f"{label}: duplicate dependency {dependency}")
        seen_requires.add(dependency)

    updated_at = data.get("updated_at")
    if status == "candidate" and (
        not isinstance(updated_at, str) or not ISO_DATE.fullmatch(updated_at)
    ):
        failures.append(f"{label}: candidate updated_at must be YYYY-MM-DD")
    return status, failures


def audit_dependencies(
    skill_dir: Path,
    repository_root: Path = ROOT,
    *,
    require_installable: bool = True,
) -> list[str]:
    failures: list[str] = []
    visited: set[str] = set()
    active: list[str] = []

    def visit(current_dir: Path) -> None:
        current_name = current_dir.name
        if current_name in visited:
            return
        if current_name in active:
            cycle = " -> ".join([*active, current_name])
            failures.append(f"{skill_dir / 'admission.json'}: dependency cycle {cycle}")
            return

        data, read_failures = read_metadata(current_dir)
        if read_failures:
            failures.extend(read_failures)
            return

        active.append(current_name)
        for dependency in data.get("requires", []):
            dependency_dir = repository_root / dependency
            if not (dependency_dir / "SKILL.md").is_file():
                failures.append(
                    f"{current_dir / 'admission.json'}: requires unknown skill {dependency}"
                )
                continue
            dependency_status, dependency_failures = audit_skill(dependency_dir)
            if dependency_failures:
                failures.extend(dependency_failures)
                continue
            if require_installable and dependency_status != "installable":
                failures.append(
                    f"{current_dir / 'admission.json'}: requires non-installable skill "
                    f"{dependency} ({dependency_status})"
                )
                continue
            visit(dependency_dir)
        active.pop()
        visited.add(current_name)

    visit(skill_dir)
    return failures


def dependency_names(skill_dir: Path) -> list[str]:
    data, failures = read_metadata(skill_dir)
    if failures:
        raise ValueError("; ".join(failures))
    requires = data.get("requires", [])
    if not isinstance(requires, list):
        raise ValueError(f"{skill_dir / 'admission.json'}: requires must be an array")
    return list(requires)


def audit_repository(repository_root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    skill_files = sorted(repository_root.glob("*/SKILL.md"))
    for skill_md in skill_files:
        _, skill_failures = audit_skill(skill_md.parent)
        failures.extend(skill_failures)
    if failures:
        return failures
    for skill_md in skill_files:
        failures.extend(
            audit_dependencies(
                skill_md.parent,
                repository_root,
                require_installable=False,
            )
        )
    return failures


def self_test() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        missing_status, missing_failures = audit_skill(root)
        if missing_status != "invalid" or not any(
            "missing admission.json" in failure for failure in missing_failures
        ):
            failures.append("missing admission.json should be rejected")

        (root / "admission.json").write_text(
            json.dumps(
                {
                    "status": "candidate",
                    "updated_at": "2026-07-31",
                    "blockers": [{"id": "Q-1", "summary": "pending", "owner": "Owner"}],
                }
            ),
            encoding="utf-8",
        )
        status, candidate_failures = audit_skill(root)
        if status != "candidate" or candidate_failures:
            failures.append("valid candidate metadata should pass")

        (root / "admission.json").write_text(
            '{"status":"candidate","updated_at":"later","blockers":[]}',
            encoding="utf-8",
        )
        _, invalid_failures = audit_skill(root)
        if len(invalid_failures) < 2:
            failures.append("invalid candidate metadata was not rejected")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", type=Path, help="print one skill directory's status")
    parser.add_argument(
        "--check-dependencies",
        type=Path,
        help="fail when one skill requires a missing, invalid, or candidate Skill",
    )
    parser.add_argument(
        "--list-dependencies",
        type=Path,
        help="print direct Skill dependencies, one per line",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        failures = self_test()
    elif args.list_dependencies:
        try:
            print("\n".join(dependency_names(args.list_dependencies.resolve())))
        except ValueError as exc:
            print(f"FAIL skill dependencies\n- {exc}")
            return 1
        return 0
    elif args.check_dependencies:
        failures = audit_dependencies(args.check_dependencies.resolve())
    elif args.status:
        status, failures = audit_skill(args.status.resolve())
        if not failures:
            print(status)
            return 0
    else:
        failures = audit_repository()

    label = "skill dependencies" if args.check_dependencies else "skill admission"
    if failures:
        print(f"FAIL {label}")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"OK {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
