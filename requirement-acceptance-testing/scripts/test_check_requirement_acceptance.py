#!/usr/bin/env python3
"""Tests for the requirement acceptance report validator."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import sys
import re
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

    def test_source_contract_cannot_prove_visual_fidelity(self) -> None:
        path = SKILL_ROOT / "fixtures" / "acceptance-invalid-source-contract-overclaim.md"
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "visual-fidelity"):
            VALIDATOR.parse_report(path.read_text(encoding="utf-8"))

    def test_high_risk_pass_requires_independent_reviewer(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "independent_reviewer: acceptance-checker", "independent_reviewer: none"
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "independent_reviewer"):
            VALIDATOR.parse_report(text)

    def test_high_risk_rejects_unresolved_reviewers(self) -> None:
        for reviewer in ("pending", "UNKNOWN", "待确认", "TBD"):
            with self.subTest(reviewer=reviewer):
                text = VALID.read_text(encoding="utf-8").replace(
                    "independent_reviewer: acceptance-checker", f"independent_reviewer: {reviewer}"
                )
                with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "independent_reviewer"):
                    VALIDATOR.parse_report(text)

    def test_visual_review_requires_independence_at_every_risk_level(self) -> None:
        for risk in ("low", "medium", "high", "critical"):
            text = VALID.read_text(encoding="utf-8").replace("risk_level: high", f"risk_level: {risk}")
            text = text.replace("producer: design-checker", "producer: UI-MAKER")
            with self.subTest(risk=risk):
                with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "visual-review"):
                    VALIDATOR.parse_report(text)

    def test_visual_review_producer_must_be_resolved(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("risk_level: high", "risk_level: low")
        text = text.replace("producer: design-checker", "producer: pending")
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "visual-review"):
            VALIDATOR.parse_report(text)

    def test_visual_independence_cannot_be_proven_against_unknown_maker(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("risk_level: high", "risk_level: low")
        text = text.replace("producer: ui-maker", "producer: unknown")
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "visual-review"):
            VALIDATOR.parse_report(text)

    def test_declared_pending_visual_reviewer_is_not_treated_as_unneeded(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "producer: design-checker\nindependent_reviewer: acceptance-checker",
            "producer: design-checker\nindependent_reviewer: pending",
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "independent_reviewer"):
            VALIDATOR.parse_report(text)

    def test_independent_visual_review_needs_no_fourth_reviewer(self) -> None:
        for risk in ("low", "high"):
            text = VALID.read_text(encoding="utf-8").replace("risk_level: high", f"risk_level: {risk}")
            text = text.replace(
                "producer: design-checker\nindependent_reviewer: acceptance-checker",
                "producer: design-checker\nindependent_reviewer: none",
            )
            if risk == "low":
                text = text.replace("independent_reviewer: acceptance-checker", "independent_reviewer: none")
            else:
                text = text.replace("independent_reviewer: acceptance-checker", "independent_reviewer: design-checker")
            with self.subTest(risk=risk):
                self.assertEqual(VALIDATOR.parse_report(text).verdict["verdict"], "pass")

    def test_unexecuted_report_is_valid_but_cannot_pass_release_gate(self) -> None:
        for outcome in ("blocked", "untested"):
            text = VALID.read_text(encoding="utf-8")
            text = re.sub(r"```acceptance-evidence\n[\s\S]*?```", "```acceptance-evidence\n```", text)
            text = re.sub(r"evidence_refs: .*", "evidence_refs: none", text)
            text = re.sub(r"rationale: .*", "rationale: 环境尚未开放；环境就绪后由 owner 重跑声明范围", text)
            text = text.replace("outcome: pass", f"outcome: {outcome}")
            text = text.replace("verdict: pass", "verdict: blocked").replace("pass_count: 3", "pass_count: 0")
            text = text.replace(f"{outcome}_count: 0", f"{outcome}_count: 3")
            with self.subTest(outcome=outcome):
                parts = VALIDATOR.parse_report(text)
                self.assertEqual(parts.evidence, [])
                self.assertEqual(parts.verdict["verdict"], "blocked")
                for malformed in ("无法解析的证据内容", "[evidence]\nid: EV-001"):
                    invalid = text.replace("```acceptance-evidence\n```", f"```acceptance-evidence\n{malformed}\n```")
                    with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "evidence.*记录"):
                        VALIDATOR.parse_report(invalid)
                for require_pass, expected_exit in ((False, 0), (True, 1)):
                    argv = ["checker", "--file", "report.md"]
                    if require_pass:
                        argv.append("--require-pass")
                    with (
                        patch.object(VALIDATOR.Path, "read_text", return_value=text),
                        patch.object(VALIDATOR.sys, "argv", argv),
                        redirect_stdout(StringIO()), redirect_stderr(StringIO()),
                    ):
                        self.assertEqual(VALIDATOR.main(), expected_exit)

    def test_empty_evidence_cannot_support_pass_or_fail(self) -> None:
        for text in (VALID.read_text(encoding="utf-8"), failed_report()):
            text = re.sub(r"```acceptance-evidence\n[\s\S]*?```", "```acceptance-evidence\n```", text)
            text = re.sub(r"evidence_refs: .*", "evidence_refs: none", text)
            with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "AC-001.*evidence"):
                VALIDATOR.parse_report(text)

    def test_criteria_still_cannot_be_empty(self) -> None:
        text = re.sub(
            r"```acceptance-criteria\n[\s\S]*?```",
            "```acceptance-criteria\n```",
            VALID.read_text(encoding="utf-8"),
        )
        with self.assertRaisesRegex(VALIDATOR.AcceptanceError, "criterion.*记录"):
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
