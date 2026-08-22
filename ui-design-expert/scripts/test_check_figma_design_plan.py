#!/usr/bin/env python3
"""Tests for the deterministic Figma design-plan validator."""

from __future__ import annotations

import importlib.util
import contextlib
import io
import re
import sys
from typing import NamedTuple
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ui-design-expert" / "scripts" / "check_figma_design_plan.py"
VALID = ROOT / "ui-design-expert" / "fixtures" / "figma-design-plan-valid.md"


class Result(NamedTuple):
    returncode: int
    stdout: str
    stderr: str


SPEC = importlib.util.spec_from_file_location("check_figma_design_plan", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class FigmaDesignPlanTests(unittest.TestCase):
    def run_validator(self, path: Path) -> Result:
        stdout = io.StringIO()
        stderr = io.StringIO()
        original_argv = sys.argv
        try:
            sys.argv = [str(SCRIPT), "--file", str(path)]
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                returncode = VALIDATOR.main()
        finally:
            sys.argv = original_argv
        return Result(returncode, stdout.getvalue(), stderr.getvalue())

    def test_valid_plan_passes(self) -> None:
        result = self.run_validator(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_invalid_page_naming_fails(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "figma-design-plan-invalid-page-naming.md"
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("figma_name", result.stderr)

    def test_invalid_authority_fails(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "figma-design-plan-invalid-authority.md"
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target_role", result.stderr)

    def test_invalid_state_coverage_fails(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "figma-design-plan-invalid-state-coverage.md"
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("states", result.stderr)

    def test_completed_evidence_requires_an_evidence_reference(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "components: status=planned; evidence=component-contract-v1",
            "components: status=completed; evidence=",
        )
        path = ROOT / "ui-design-expert" / "fixtures" / ".tmp-figma-plan-invalid-evidence.md"
        path.write_text(text, encoding="utf-8")
        try:
            result = self.run_validator(path)
        finally:
            path.unlink()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence", result.stderr)

    def test_target_figma_cannot_be_authority_source(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "product_source: product-source-v1.md",
            "product_source: https://www.figma.com/design/target/file?node-id=1-2",
        )
        with self.assertRaisesRegex(VALIDATOR.ContractError, "product_source"):
            VALIDATOR.parse_plan(text)

    def test_ready_for_code_requires_completed_evidence(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "status: ready-for-figma", "status: ready-for-code"
        )
        with self.assertRaisesRegex(VALIDATOR.ContractError, "ready-for-code"):
            VALIDATOR.parse_plan(text)

    def test_web_mobile_scope_is_supported(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "client_scope: web-pc", "client_scope: web-mobile"
        ).replace("Web PC /", "Web Mobile /").replace("/ 1440 /", "/ 390 /")
        parts = VALIDATOR.parse_plan(text)
        self.assertEqual(parts.contract["client_scope"], "web-mobile")

    def test_figma_name_status_matches_page_status(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "Web PC / 10 Home / default / 1440 / Draft",
            "Web PC / 10 Home / default / 1440 / Approved",
        )
        with self.assertRaisesRegex(VALIDATOR.ContractError, "status"):
            VALIDATOR.parse_plan(text)

    def test_approved_contract_requires_approved_current_pages(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("status: ready-for-figma", "status: approved", 1)
        text = text.replace("target_role: current-draft-only", "target_role: approved-design")
        text = text.replace("status=planned", "status=completed")
        with self.assertRaisesRegex(VALIDATOR.ContractError, "approved.*page"):
            VALIDATOR.parse_plan(text)

    def test_default_only_states_require_explicit_exclusions(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^states:.*$", "states: default", text)
        text = re.sub(r"(?m)^state_notes:.*$", "state_notes: only default is documented", text)
        with self.assertRaisesRegex(VALIDATOR.ContractError, "状态覆盖"):
            VALIDATOR.parse_plan(text)


if __name__ == "__main__":
    unittest.main()
