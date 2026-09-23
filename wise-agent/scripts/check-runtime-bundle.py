#!/usr/bin/env python3
"""Check admission dependencies for Skills distributed by this repository.

External Skills use their provider's entrypoint and dependency contract; this
project-specific checker is not their admission gate.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


class BundleError(ValueError):
    """Raised when a selected runtime bundle is incomplete or invalid."""


def _metadata(skills_root: Path, skill: str) -> dict[str, Any]:
    skill_dir = skills_root / skill
    metadata_path = skill_dir / "admission.json"
    if not skill_dir.is_dir():
        raise BundleError(f"missing runtime Skill: {skill}")
    if not metadata_path.is_file():
        raise BundleError(f"missing admission.json for runtime Skill: {skill}")
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BundleError(f"invalid admission.json for {skill}: {error}") from error
    if not isinstance(data, dict):
        raise BundleError(f"admission.json for {skill} must be an object")
    if data.get("status") != "installable":
        raise BundleError(f"runtime Skill {skill} is not installable")
    return data


def resolve_bundle(skills_root: Path, selected: list[str]) -> list[str]:
    if not selected:
        raise BundleError("at least one Skill must be selected")
    resolved: list[str] = []
    visiting: set[str] = set()

    def visit(skill: str) -> None:
        if skill in resolved:
            return
        if skill in visiting:
            raise BundleError(f"dependency cycle detected at {skill}")
        visiting.add(skill)
        data = _metadata(skills_root, skill)
        requires = data.get("requires", [])
        if not isinstance(requires, list) or any(
            not isinstance(item, str) or not item.strip() for item in requires
        ):
            raise BundleError(f"requires for {skill} must be a list of Skill IDs")
        for dependency in requires:
            visit(dependency)
        visiting.remove(skill)
        resolved.append(skill)

    for skill in selected:
        visit(skill)
    return resolved


def _write_metadata(root: Path, skill: str, requires: list[str]) -> None:
    skill_dir = root / skill
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "admission.json").write_text(
        json.dumps({"status": "installable", "requires": requires}),
        encoding="utf-8",
    )


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        _write_metadata(root, "wind-coding-conventions", [])
        _write_metadata(root, "senior-software-architect", ["wind-coding-conventions"])
        assert resolve_bundle(root, ["senior-software-architect"]) == [
            "wind-coding-conventions",
            "senior-software-architect",
        ]

        (root / "wind-coding-conventions" / "admission.json").unlink()
        try:
            resolve_bundle(root, ["senior-software-architect"])
        except BundleError as error:
            assert "missing admission.json" in str(error)
        else:
            raise AssertionError("missing dependency was accepted")
    print("OK runtime bundle self-test")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, help="installed Skills directory")
    parser.add_argument("--skill", action="append", dest="skills", help="selected Skill ID")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.skills_root is None or not args.skills:
        parser.error("--skills-root and at least one --skill are required")
    try:
        bundle = resolve_bundle(args.skills_root, args.skills)
    except BundleError as error:
        print(f"FAIL runtime bundle: {error}", file=sys.stderr)
        return 1
    print(f"OK runtime bundle: {', '.join(bundle)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
