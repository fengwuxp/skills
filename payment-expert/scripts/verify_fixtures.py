#!/usr/bin/env python3
"""Run public-safe fixtures through the payment external-rule checker."""

from __future__ import annotations

from pathlib import Path

from check_external_rules import missing_fields


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
CASES = (
    (FIXTURES / "external-rules-valid.md", True),
    (FIXTURES / "external-rules-invalid.md", False),
    (FIXTURES / "external-rules-placeholder.md", False),
    (FIXTURES / "external-rules-negated.md", False),
    (FIXTURES / "external-rules-invalid-date.md", False),
    (FIXTURES / "external-rules-semantic-placeholder.md", False),
)


def main() -> int:
    failures: list[str] = []
    for path, should_pass in CASES:
        if not path.exists():
            failures.append(f"missing fixture: {path.name}")
            continue
        missing = missing_fields(path.read_text(encoding="utf-8"))
        passed = not missing
        if passed != should_pass:
            failures.append(
                f"fixture expectation failed: {path.name}: "
                f"expected {'pass' if should_pass else 'fail'}, missing={','.join(missing) or 'none'}"
            )
        else:
            print(f"OK payment fixture {path.name}")

    if failures:
        print("FAIL payment fixture verification")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Payment fixture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
