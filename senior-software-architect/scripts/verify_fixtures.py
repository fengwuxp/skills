#!/usr/bin/env python3
"""Run public-safe fixtures through the architecture deliverable checker."""

from __future__ import annotations

from pathlib import Path

from check_architecture_deliverable import missing_groups


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"

VALID_CASES = [
    ("architecture-plan", FIXTURES / "architecture-plan-valid.md"),
    ("system-design", FIXTURES / "system-design-valid.md"),
    ("code-review", FIXTURES / "code-review-valid.md"),
    ("production-change", FIXTURES / "production-change-valid.md"),
    ("diagram-brief", FIXTURES / "diagram-brief-valid.md"),
]
INVALID_CASE = ("system-design", FIXTURES / "invalid-incomplete.md")


def read_fixture(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    for kind, path in VALID_CASES:
        missing = missing_groups(kind, read_fixture(path))
        if missing:
            failures.append(f"valid fixture failed: {kind} {path.name}: {', '.join(missing)}")
        else:
            print(f"OK architecture fixture {kind}")

    invalid_kind, invalid_path = INVALID_CASE
    invalid_missing = missing_groups(invalid_kind, read_fixture(invalid_path))
    if not invalid_missing:
        failures.append(f"invalid fixture unexpectedly passed: {invalid_kind} {invalid_path.name}")
    else:
        print(f"OK negative architecture fixture {invalid_kind}")

    if failures:
        print("FAIL architecture fixture verification")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Architecture fixture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
