#!/usr/bin/env python3
"""Tests for the requirement acceptance report validator."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import sys
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "requirement-acceptance-testing"
SCRIPT = SKILL_ROOT / "scripts" / "check_requirement_acceptance.py"
VALID = SKILL_ROOT / "fixtures" / "acceptance-valid.md"


SPEC = importlib.util.spec_from_file_location("check_requirement_acceptance", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


def failed_report() -> str:
    text = VALID.read_text(encoding="utf-8")
    text = text.replace("outcome: pass", "outcome: fail", 1)
    text = text.replace("finding_id: none", "finding_id: F-001", 1)
    text = text.replace("result: pass", "result: fail", 1)
    text = text.replace("verdict: pass", "verdict: fail", 1)
    text = text.replace("pass_count: 3", "pass_count: 2", 1)
    return text.replace("fail_count: 0", "fail_count: 1", 1)


class RequirementAcceptanceTests(unittest.TestCase):
    def test_valid_cross_layer_report_passes(self) -> None:
        parts = VALIDATOR.parse_report(VALID.read_text(encoding="utf-8"))
        self.assertEqual(parts.verdict["verdict"], "pass")
        self.assertEqual(len(parts.criteria), 3)

    def test_missing_requirement_source_is_rejected(self) -> None:
        path = SKILL_ROOT / "fixtures" / "acceptance-invalid-missing-source.md"
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "requirement_source"):
            VALIDATOR.parse_report(path.read_text(encoding="utf-8"))

    def test_pass_without_evidence_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("evidence_refs: EV-001", "evidence_refs: none", 1)
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "AC-001.*evidence"):
            VALIDATOR.parse_report(text)

    def test_overall_pass_with_required_failure_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("outcome: pass", "outcome: fail", 1)
        text = text.replace("finding_id: none", "finding_id: F-001", 1)
        text = text.replace("result: pass", "result: fail", 1)
        text = text.replace("pass_count: 3", "pass_count: 2")
        text = text.replace("fail_count: 0", "fail_count: 1")
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "verdict.*fail"):
            VALIDATOR.parse_report(text)

    def test_screenshot_cannot_prove_ui_interaction(self) -> None:
        path = SKILL_ROOT / "fixtures" / "acceptance-invalid-visual-overclaim.md"
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "ui-interaction"):
            VALIDATOR.parse_report(path.read_text(encoding="utf-8"))

    def test_high_risk_pass_requires_independent_reviewer(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "independent_reviewer: acceptance-checker", "independent_reviewer: none"
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "independent_reviewer"):
            VALIDATOR.parse_report(text)

    def test_verdict_counts_must_match_criteria(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("pass_count: 3", "pass_count: 2")
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "pass_count"):
            VALIDATOR.parse_report(text)

    def test_invalid_requirement_fingerprint_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "requirement_fingerprint: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "requirement_fingerprint: latest",
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "requirement_fingerprint"):
            VALIDATOR.parse_report(text)

    def test_pass_requires_at_least_one_required_criterion(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("required: true", "required: false")
        text = text.replace("required_total: 3", "required_total: 0")
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "required criterion"):
            VALIDATOR.parse_report(text)

    def test_placeholder_requirement_source_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "requirement_source: product-spec-v1.md", "requirement_source: none"
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "requirement_source"):
            VALIDATOR.parse_report(text)

    def test_independent_reviewer_must_differ_from_producer(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "independent_reviewer: acceptance-checker",
            "independent_reviewer: engineering-maker",
            1,
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "independent_reviewer"):
            VALIDATOR.parse_report(text)

    def test_pass_rejects_conflicting_linked_evidence(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        start = text.index("[evidence]\nid: EV-001")
        end = text.index("[/evidence]", start) + len("[/evidence]")
        evidence = text[start:end]
        passing_copy = evidence.replace("id: EV-001", "id: EV-X").replace(
            "source_fingerprint: " + "b" * 64,
            "source_fingerprint: " + "9" * 64,
        )
        text = text.replace("evidence_refs: EV-001", "evidence_refs: EV-001, EV-X", 1)
        text = text.replace(evidence, evidence + "\n\n" + passing_copy, 1)
        text = text.replace("result: pass", "result: fail", 1)
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "AC-001.*fail"):
            VALIDATOR.parse_report(text)

    def test_accessibility_requires_automated_and_runtime_evidence(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("verification_kind: ui-interaction", "verification_kind: accessibility", 1)
        text = text.replace("evidence_type: browser-trace", "evidence_type: accessibility-report", 1)
        text = text.replace(
            "command_or_method: Playwright submit and state assertion",
            "command_or_method: automated scanner only",
            1,
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "accessibility"):
            VALIDATOR.parse_report(text)

    def test_failed_criterion_requires_failing_evidence(self) -> None:
        text = failed_report().replace("result: fail", "result: pass", 1)
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "AC-001.*fail evidence"):
            VALIDATOR.parse_report(text)

    def test_tbd_requirement_source_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "requirement_source: product-spec-v1.md", "requirement_source: TBD", 1
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "requirement_source"):
            VALIDATOR.parse_report(text)

    def test_latest_requirement_version_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("requirement_version: v1", "requirement_version: latest", 1)
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "requirement_version"):
            VALIDATOR.parse_report(text)

    def test_cli_reports_valid_failed_verdict_without_pass_label(self) -> None:
        stdout = StringIO()
        with (
            patch.object(VALIDATOR.Path, "read_text", return_value=failed_report()),
            patch.object(VALIDATOR.sys, "argv", ["checker", "--file", "report.md"]),
            redirect_stdout(stdout),
        ):
            result = VALIDATOR.main()
        self.assertEqual(result, 0)
        self.assertIn("VALID requirement acceptance report", stdout.getvalue())
        self.assertIn("verdict=fail", stdout.getvalue())
        self.assertNotIn("PASS requirement acceptance", stdout.getvalue())

    def test_cli_require_pass_rejects_failed_verdict(self) -> None:
        stderr = StringIO()
        with (
            patch.object(VALIDATOR.Path, "read_text", return_value=failed_report()),
            patch.object(VALIDATOR.sys, "argv", ["checker", "--file", "report.md", "--require-pass"]),
            redirect_stderr(stderr),
        ):
            result = VALIDATOR.main()
        self.assertEqual(result, 1)
        self.assertIn("verdict=fail", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
