#!/usr/bin/env python3
"""Run public-safe fixtures through the product deliverable checker."""

from __future__ import annotations

from pathlib import Path

from check_product_deliverable import missing_groups


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
CASES = (
    ("prd", FIXTURES / "prd-valid.md", True, set()),
    (
        "prd",
        FIXTURES / "prd-invalid.md",
        False,
        {"scenario_contract_missing", "rule_scope_missing", "acceptance_scenario_missing"},
    ),
    ("business-architecture", FIXTURES / "business-architecture-valid.md", True, set()),
    ("business-architecture", FIXTURES / "business-architecture-invalid.md", False, set()),
    ("product-review", FIXTURES / "product-review-valid.md", True, set()),
    ("product-review", FIXTURES / "product-review-invalid.md", False, set()),
)


def main() -> int:
    failures: list[str] = []
    for kind, path, should_pass, expected_missing in CASES:
        if not path.exists():
            failures.append(f"missing fixture: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = missing_groups(kind, text)
        passed = not missing
        if passed != should_pass:
            failures.append(
                f"fixture expectation failed: {path.name}: "
                f"expected {'pass' if should_pass else 'fail'}, missing={','.join(missing) or 'none'}"
            )
        elif not expected_missing.issubset(set(missing)):
            failures.append(
                f"fixture failure reason mismatch: {path.name}: "
                f"expected={','.join(sorted(expected_missing))}, missing={','.join(missing) or 'none'}"
            )
        else:
            print(f"OK product fixture {path.name}")

    if failures:
        print("FAIL product fixture verification")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Product fixture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
