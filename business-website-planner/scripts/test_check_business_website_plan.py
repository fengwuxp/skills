#!/usr/bin/env python3
"""Tests for the business website plan validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "business-website-planner"
SCRIPT = SKILL_ROOT / "scripts" / "check_business_website_plan.py"
VALID = SKILL_ROOT / "fixtures" / "business-website-plan-valid.md"

SPEC = importlib.util.spec_from_file_location("check_business_website_plan", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class BusinessWebsitePlanTests(unittest.TestCase):
    def test_valid_business_website_plan_passes(self) -> None:
        parts = VALIDATOR.parse_plan(VALID.read_text(encoding="utf-8"))
        self.assertEqual(parts.contract["design_carrier"], "figma")
        self.assertEqual(len(parts.metrics), 3)

    def test_missing_business_authority_is_rejected(self) -> None:
        path = SKILL_ROOT / "fixtures" / "business-website-plan-invalid-authority.md"
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "business_authority"):
            VALIDATOR.parse_plan(path.read_text(encoding="utf-8"))

    def test_tbd_business_authority_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "business_authority: owner-approved-business-brief-v1.md",
            "business_authority: TBD",
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "business_authority"):
            VALIDATOR.parse_plan(text)

    def test_tbd_company_subject_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "company_subject: Example Advertising Services Limited",
            "company_subject: TBD",
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "company_subject"):
            VALIDATOR.parse_plan(text)

    def test_unconfirmed_reference_example_cannot_publish(self) -> None:
        path = SKILL_ROOT / "fixtures" / "business-website-plan-invalid-metric.md"
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "Verified suppliers.*publish"):
            VALIDATOR.parse_plan(path.read_text(encoding="utf-8"))

    def test_tbd_metric_cannot_publish(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "owner_confirmed_value: 80+",
            "owner_confirmed_value: TBD",
            1,
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "Advertising engagements.*publish"):
            VALIDATOR.parse_plan(text)

    def test_reference_example_none_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "reference_example_value: 50+",
            "reference_example_value: none",
            1,
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "Advertising engagements.*reference_example_value"):
            VALIDATOR.parse_plan(text)

    def test_modules_are_suggestions_not_fixed_pages(self) -> None:
        parts = VALIDATOR.parse_plan(VALID.read_text(encoding="utf-8"))
        self.assertEqual({item["id"] for item in parts.modules}, {"positioning", "services", "inquiry"})

    def test_figma_is_default_without_explicit_override(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("design_carrier: figma", "design_carrier: html-prototype", 1)
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "figma.*default"):
            VALIDATOR.parse_plan(text)

    def test_explicit_non_figma_override_is_allowed(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("design_carrier: figma", "design_carrier: html-prototype")
        text = text.replace("design_carrier_override: none", "design_carrier_override: user-specified-html")
        parts = VALIDATOR.parse_plan(text)
        self.assertEqual(parts.contract["design_carrier"], "html-prototype")

    def test_agent_decided_non_figma_override_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace("design_carrier: figma", "design_carrier: html-prototype")
        text = text.replace("design_carrier_override: none", "design_carrier_override: agent-decided")
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "user-specified"):
            VALIDATOR.parse_plan(text)

    def test_reference_mode_none_allows_empty_reference_block(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("reference_mode: public", "reference_mode: none")
        text = re.sub(r"\[reference\].*?\[/reference\]", "", text, flags=re.DOTALL)
        parts = VALIDATOR.parse_plan(text)
        self.assertEqual(parts.references, [])

    def test_public_reference_mode_requires_record(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = re.sub(r"\[reference\].*?\[/reference\]", "", text, flags=re.DOTALL)
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "reference"):
            VALIDATOR.parse_plan(text)

    def test_public_reference_requires_read_status_adopt_and_reject(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "adopt: service scope, accountability and evidence-led case structure",
            "adopt:",
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "reference.*adopt"):
            VALIDATOR.parse_plan(text)

    def test_reference_none_adopt_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "adopt: service scope, accountability and evidence-led case structure",
            "adopt: none",
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "reference.*adopt"):
            VALIDATOR.parse_plan(text)

    def test_media_source_none_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "source: owner-approved-asset-library/team-collaboration.jpg",
            "source: none",
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "media.*source"):
            VALIDATOR.parse_plan(text)

    def test_unresolved_handoff_owner_is_rejected(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace("ui_owner: ui-design-expert", "ui_owner: none")
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "ui_owner"):
            VALIDATOR.parse_plan(text)

    def test_responsive_media_requires_mobile_and_large_screen_viewports(self) -> None:
        text = VALID.read_text(encoding="utf-8")
        text = text.replace(
            "mobile-390, desktop-1440, desktop-1920, ultrawide-2560, ultrawide-3440",
            "desktop-1280, desktop-1440",
        )
        text = text.replace("mobile-390, desktop-1440", "desktop-1440")
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "target_viewports"):
            VALIDATOR.parse_plan(text)

    def test_valid_modules_have_distinct_page_roles(self) -> None:
        parts = VALIDATOR.parse_plan(VALID.read_text(encoding="utf-8"))
        self.assertEqual(
            {item["page_role"] for item in parts.modules},
            {"home", "services", "shared"},
        )

    def test_detailed_duplicate_primary_question_is_rejected(self) -> None:
        path = SKILL_ROOT / "fixtures" / "business-website-plan-invalid-overlap.md"
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "primary_question.*detailed"):
            VALIDATOR.parse_plan(path.read_text(encoding="utf-8"))

    def test_overlap_reference_must_name_known_module(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "overlap_with: positioning, services",
            "overlap_with: missing-module",
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "overlap_with.*unknown"):
            VALIDATOR.parse_plan(text)

    def test_overlap_requires_non_none_disposition(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "overlap_disposition: keep-shared",
            "overlap_disposition: none",
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "overlap_disposition"):
            VALIDATOR.parse_plan(text)

    def test_handoff_reference_must_name_known_module(self) -> None:
        text = VALID.read_text(encoding="utf-8").replace(
            "handoff_to: services",
            "handoff_to: missing-module",
            1,
        )
        with self.assertRaisesRegex(VALIDATOR.WebsitePlanError, "handoff_to.*unknown"):
            VALIDATOR.parse_plan(text)


if __name__ == "__main__":
    unittest.main()
