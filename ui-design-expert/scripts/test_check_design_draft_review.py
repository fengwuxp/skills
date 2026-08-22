#!/usr/bin/env python3
"""Tests for the structured design-draft fidelity review validator."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path
from typing import NamedTuple
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ui-design-expert" / "scripts" / "check_design_draft_review.py"
VALID = ROOT / "ui-design-expert" / "fixtures" / "design-draft-review-valid.md"
MOCKINGBOT_VALID = ROOT / "ui-design-expert" / "fixtures" / "design-draft-review-mockingbot-valid.md"


class Result(NamedTuple):
    returncode: int
    stdout: str
    stderr: str


SPEC = importlib.util.spec_from_file_location("check_design_draft_review", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class DesignDraftReviewTests(unittest.TestCase):
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

    def test_valid_review_passes(self) -> None:
        result = self.run_validator(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_valid_mockingbot_preview_review_passes(self) -> None:
        result = self.run_validator(MOCKINGBOT_VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_draft_cannot_be_content_authority(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "design-draft-review-invalid-source.md"
        result = self.run_validator(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("target_role", result.stderr)

    def test_review_requires_content_completeness(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        marker = "[check]\nid: content-completeness\n"
        if marker in text:
            before, remainder = text.split(marker, 1)
            _, after = remainder.split("[/check]", 1)
            text = before + after
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "content-completeness"):
            VALIDATOR.parse_review(text)

    def test_text_wrap_requires_evidence(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "design-draft-review-invalid-wrap.md"
        result = self.run_validator(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("text-wrap", result.stderr)

    def test_review_requires_multiple_viewports(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "design-draft-review-invalid-viewport.md"
        result = self.run_validator(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("viewports", result.stderr)

    def test_source_of_truth_cannot_equal_source_locator(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "source_of_truth: approved-brief-v1.md",
            "source_of_truth: https://www.figma.com/design/target/file?node-id=1-2",
        )
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "source_of_truth"):
            VALIDATOR.parse_review(text)

    def test_approved_review_requires_e2_or_higher(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "evidence_level: E2", "evidence_level: E1"
        ).replace("status: ready-for-review", "status: approved")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "approved"):
            VALIDATOR.parse_review(text)

    def test_approved_review_rejects_failed_checks(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "status: ready-for-review", "status: approved"
        ).replace("status: pass", "status: fail", 1)
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "approved"):
            VALIDATOR.parse_review(text)

    def test_layout_and_responsive_evidence_cover_each_viewport(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "screenshot:home-1440x900; screenshot:home-1280x800",
            "screenshot:home-1440x900-1280x800",
        )
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "独立"):
            VALIDATOR.parse_review(text)

    def test_review_requires_source_kind(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("source_kind: figma\n", "")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "source_kind"):
            VALIDATOR.parse_review(text)

    def test_figma_source_locator_must_include_exact_node(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: https://www.figma.com/design/target/file",
        )
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "source_locator"):
            VALIDATOR.parse_review(text)

    def test_screenshot_source_cannot_claim_e2(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: screenshot")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: file:screenshot-home.png#sha256=demo",
            1,
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: local-file")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "screenshot.*E1"):
            VALIDATOR.parse_review(text)

    def test_mockingbot_preview_can_reach_e2_with_annotation_evidence(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: mockingbot")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: https://modao.cc/proto/example",
            1,
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: mockingbot-preview-annotation")
        text = text.replace("target_figma: https://www.figma.com/design/target/file?node-id=1-2\n", "")
        text = text.replace("target_node: https://www.figma.com/design/target/file?node-id=1-2\n", "")
        text = text.replace(
            "design-context:node-1-2; screenshot:home-default-v1",
            "mockingbot-page-inventory:home-inquiry; annotation:home-default; screenshot:home-default-v1",
        )
        VALIDATOR.parse_review(text)

    def test_mockingbot_export_cannot_claim_e2(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: mockingbot")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: file:mockingbot-export.zip#sha256=demo",
            1,
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: mockingbot-export")
        text = text.replace("target_figma: https://www.figma.com/design/target/file?node-id=1-2\n", "")
        text = text.replace("target_node: https://www.figma.com/design/target/file?node-id=1-2\n", "")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "mockingbot.*E1"):
            VALIDATOR.parse_review(text)

    def test_mockingbot_preview_requires_page_and_annotation_evidence(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: mockingbot")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: https://modao.cc/proto/example",
            1,
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: mockingbot-preview")
        text = text.replace("target_figma: https://www.figma.com/design/target/file?node-id=1-2\n", "")
        text = text.replace("target_node: https://www.figma.com/design/target/file?node-id=1-2\n", "")
        text = text.replace("design-context:node-1-2; ", "")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "页面.*标注"):
            VALIDATOR.parse_review(text)

    def test_screenshot_e2_fixture_is_rejected(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "design-draft-review-invalid-screenshot-e2.md"
        result = self.run_validator(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("screenshot", result.stderr)

    def test_mockingbot_export_e2_fixture_is_rejected(self) -> None:
        path = ROOT / "ui-design-expert" / "fixtures" / "design-draft-review-invalid-mockingbot-export-e2.md"
        result = self.run_validator(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("mockingbot", result.stderr)

    def test_runtime_source_requires_e3_or_e4(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: runtime")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: http://127.0.0.1:4173/home",
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: browser-playwright")
        text = text.replace("target_role: current-draft-only", "target_role: runtime-implementation")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "runtime.*E3"):
            VALIDATOR.parse_review(text)

    def test_runtime_e3_requires_browser_and_screenshot_evidence(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: runtime")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: http://127.0.0.1:4173/home",
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: browser-playwright")
        text = text.replace("target_role: current-draft-only", "target_role: runtime-implementation")
        text = text.replace("evidence_level: E2", "evidence_level: E3")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "browser.*screenshot"):
            VALIDATOR.parse_review(text)

    def test_runtime_e4_requires_user_or_production_evidence(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: runtime")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: http://127.0.0.1:4173/home",
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: browser-playwright")
        text = text.replace("target_role: current-draft-only", "target_role: runtime-implementation")
        text = text.replace("evidence_level: E2", "evidence_level: E4")
        text = text.replace("design-context:node-1-2", "browser:home")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "E4.*用户.*运行"):
            VALIDATOR.parse_review(text)

    def test_blocked_layout_can_record_missing_viewport(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace(
            "id: layout-fit\ncategory: layout\nstatus: pass",
            "id: layout-fit\ncategory: layout\nstatus: blocked",
        )
        text = text.replace(
            "evidence: screenshot:home-1440x900; screenshot:home-1280x800",
            "evidence: screenshot:home-1440x900",
            1,
        )
        VALIDATOR.parse_review(text)

    def test_target_role_must_be_supported(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "target_role: current-draft-only", "target_role: anything"
        )
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "target_role"):
            VALIDATOR.parse_review(text)

    def test_screenshot_locator_must_be_traceable(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: screenshot")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: unknown",
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: local-file")
        text = text.replace("evidence_level: E2", "evidence_level: E1")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "screenshot source_locator"):
            VALIDATOR.parse_review(text)

    def test_runtime_requires_browser_locator_and_access_mode(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("source_kind: figma", "source_kind: runtime")
        text = text.replace(
            "source_locator: https://www.figma.com/design/target/file?node-id=1-2",
            "source_locator: unknown",
        )
        text = text.replace("access_mode: figma-mcp-read-only", "access_mode: manual")
        text = text.replace("target_role: current-draft-only", "target_role: runtime-implementation")
        text = text.replace("evidence_level: E2", "evidence_level: E3")
        text = text.replace("design-context:node-1-2", "browser:home")
        with self.assertRaisesRegex(VALIDATOR.ReviewError, "runtime source_locator"):
            VALIDATOR.parse_review(text)


if __name__ == "__main__":
    unittest.main()
