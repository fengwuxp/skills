#!/usr/bin/env python3
"""Run public-safe fixtures through the UI design deliverable checker."""

from __future__ import annotations

from pathlib import Path

try:
    from check_ui_design_deliverable import CHECKS, missing_groups
except ModuleNotFoundError:
    print("FAIL UI fixture verification: missing check_ui_design_deliverable.py")
    raise SystemExit(1)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"

VALID_CASES = [
    ("design-brief", FIXTURES / "design-brief-valid.md"),
    ("ui-review", FIXTURES / "ui-review-valid.md"),
    ("ui-review", FIXTURES / "ui-review-heading-valid.md"),
    ("usability-plan", FIXTURES / "usability-plan-valid.md"),
]
INVALID_CASES = [
    ("design-brief", FIXTURES / "invalid-incomplete.md"),
    ("design-brief", FIXTURES / "keyword-stuffed-invalid.md"),
    ("ui-review", FIXTURES / "ui-review-invalid-no-severity.md"),
    ("usability-plan", FIXTURES / "usability-plan-invalid.md"),
]


def read_fixture(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    for kind, path in VALID_CASES:
        if kind not in CHECKS:
            failures.append(f"checker kind missing: {kind}")
            continue
        missing = missing_groups(kind, read_fixture(path))
        if missing:
            failures.append(f"valid fixture failed: {kind} {path.name}: {', '.join(missing)}")
        else:
            print(f"OK UI design fixture {kind}")

    for invalid_kind, invalid_path in INVALID_CASES:
        if invalid_kind not in CHECKS:
            continue
        if not missing_groups(invalid_kind, read_fixture(invalid_path)):
            failures.append(f"invalid fixture unexpectedly passed: {invalid_kind} {invalid_path.name}")
        else:
            print(f"OK negative UI design fixture {invalid_kind} {invalid_path.name}")

    if failures:
        print("FAIL UI fixture verification")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("UI design fixture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
