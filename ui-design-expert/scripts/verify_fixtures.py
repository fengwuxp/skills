#!/usr/bin/env python3
"""Run public-safe fixtures through the UI design deliverable checker."""

from __future__ import annotations

from pathlib import Path

try:
    from check_design_draft_review import parse_review
    from check_ui_design_deliverable import ANT_ADOPTION_SCENARIOS, CHECKS, missing_groups
    from check_ui_source import scan_file
except ModuleNotFoundError:
    print("FAIL UI fixture verification: missing UI checker")
    raise SystemExit(1)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"

VALID_CASES = [
    ("design-brief", FIXTURES / "design-brief-valid.md"),
    ("ui-review", FIXTURES / "ui-review-valid.md"),
    ("ui-review", FIXTURES / "ui-review-heading-valid.md"),
    ("usability-plan", FIXTURES / "usability-plan-valid.md"),
    ("prototype-plan", FIXTURES / "prototype-plan-valid.md"),
    ("prototype-plan", FIXTURES / "prototype-plan-l0-valid.md"),
    ("prototype-plan", FIXTURES / "prototype-plan-l2-valid.md"),
]
INVALID_CASES = [
    ("design-brief", FIXTURES / "invalid-incomplete.md"),
    ("design-brief", FIXTURES / "keyword-stuffed-invalid.md"),
    ("ui-review", FIXTURES / "ui-review-invalid-no-severity.md"),
    ("usability-plan", FIXTURES / "usability-plan-invalid.md"),
    ("prototype-plan", FIXTURES / "prototype-plan-invalid.md"),
    ("prototype-plan", FIXTURES / "prototype-plan-keyword-stuffed-invalid.md"),
    ("prototype-plan", FIXTURES / "prototype-plan-level-invalid.md"),
]
ANT_ADOPTION_VALID_CASES = [
    (scenario, FIXTURES / f"ant-adoption-{scenario}-valid.md")
    for scenario in ANT_ADOPTION_SCENARIOS
]
ANT_ADOPTION_INVALID_CASES = [
    (scenario, FIXTURES / f"ant-adoption-{scenario}-invalid.md")
    for scenario in ANT_ADOPTION_SCENARIOS
] + [
    ("cross-application", FIXTURES / "ant-adoption-cross-application-empty-rows-invalid.md"),
    ("version-upgrade", FIXTURES / "ant-adoption-version-upgrade-keyword-stuffed-invalid.md"),
]
SOURCE_VALID = FIXTURES / "source-valid.tsx"
SOURCE_INVALID = FIXTURES / "source-invalid.tsx"
DESIGN_REVIEW_VALID = [
    FIXTURES / "design-draft-review-valid.md",
    FIXTURES / "design-draft-review-mockingbot-valid.md",
]
DESIGN_REVIEW_INVALID = [
    FIXTURES / "design-draft-review-invalid-source.md",
    FIXTURES / "design-draft-review-invalid-wrap.md",
    FIXTURES / "design-draft-review-invalid-viewport.md",
    FIXTURES / "design-draft-review-invalid-screenshot-e2.md",
    FIXTURES / "design-draft-review-invalid-mockingbot-export-e2.md",
]
EXPECTED_SOURCE_RULES = {"zoom-disabled", "transition-all", "non-semantic-click", "paste-blocked"}


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

    for scenario, path in ANT_ADOPTION_VALID_CASES:
        if missing := missing_groups("ant-adoption", read_fixture(path), scenario):
            failures.append(f"valid Ant adoption fixture failed: {scenario}: {', '.join(missing)}")
        else:
            print(f"OK Ant adoption fixture {scenario}")
    cross_application = read_fixture(FIXTURES / "ant-adoption-cross-application-valid.md")
    indented_cross_application = "\n".join(
        f"  {line}  " if line.startswith("|") else line
        for line in cross_application.splitlines()
    )
    if missing := missing_groups(
        "ant-adoption", indented_cross_application, "cross-application"
    ):
        failures.append(
            "valid indented Ant adoption fixture failed: " + ", ".join(missing)
        )
    else:
        print("OK indented Ant adoption fixture cross-application")
    escaped_pipe_cross_application = cross_application.replace(
        "订单入口到筛选、编辑、失败恢复和成功",
        r"订单入口 \| 筛选、编辑、失败恢复和成功",
    )
    if missing := missing_groups(
        "ant-adoption", escaped_pipe_cross_application, "cross-application"
    ):
        failures.append(
            "valid escaped-pipe Ant adoption fixture failed: " + ", ".join(missing)
        )
    else:
        print("OK escaped-pipe Ant adoption fixture cross-application")
    for scenario, path in ANT_ADOPTION_INVALID_CASES:
        if not missing_groups("ant-adoption", read_fixture(path), scenario):
            failures.append(f"invalid Ant adoption fixture unexpectedly passed: {scenario}")
        else:
            print(f"OK negative Ant adoption fixture {scenario}")

    if findings := scan_file(SOURCE_VALID):
        failures.append(f"valid source fixture failed: {', '.join(finding.rule for finding in findings)}")
    else:
        print(f"OK UI source fixture {SOURCE_VALID.name}")

    actual_rules = {finding.rule for finding in scan_file(SOURCE_INVALID)}
    if actual_rules != EXPECTED_SOURCE_RULES:
        failures.append(
            "invalid source fixture rules mismatch: "
            f"expected {sorted(EXPECTED_SOURCE_RULES)}, got {sorted(actual_rules)}"
        )
    else:
        print(f"OK negative UI source fixture {SOURCE_INVALID.name}")

    for path in DESIGN_REVIEW_VALID:
        try:
            parse_review(read_fixture(path))
            print(f"OK design draft review fixture {path.name}")
        except ValueError as error:
            failures.append(f"valid design review fixture failed: {path.name}: {error}")
    for path in DESIGN_REVIEW_INVALID:
        try:
            parse_review(read_fixture(path))
            failures.append(f"invalid design review fixture unexpectedly passed: {path.name}")
        except ValueError:
            print(f"OK negative design draft review fixture {path.name}")

    if failures:
        print("FAIL UI fixture verification")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("UI design fixture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
