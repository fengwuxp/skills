#!/usr/bin/env python3
"""Integration checks for bounded reading of project Skill references."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "wise-agent" / "scripts" / "read-reference-sections.py"
SYSTEM_INTERVENTION_REFERENCE = (
    ROOT
    / "senior-software-architect"
    / "references"
    / "system-intervention-and-backcasting.md"
)
SPEC = importlib.util.spec_from_file_location("read_reference_sections", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ReferenceSelectionIntegrationTests(unittest.TestCase):
    def test_payment_method_card_selects_one_method(self) -> None:
        result = MODULE.build_package(
            ROOT / "payment-expert" / "references" / "payment-method-cards.md",
            "",
            headings=["M01"],
        )

        self.assertEqual("ready", result["status"])
        self.assertGreater(result["estimated_savings_ratio"], 0.5)

    def test_wind_contract_task_selects_indexed_sections(self) -> None:
        result = MODULE.build_package(
            ROOT / "wind-coding-conventions" / "references" / "java-coding-conventions.md",
            "契约异常日志",
        )

        self.assertEqual("ready", result["status"])
        self.assertEqual("契约、异常、日志、安全", result["matched_task"])
        self.assertGreater(result["estimated_savings_ratio"], 0.3)

    def test_system_feedback_selects_intervention_reference(self) -> None:
        self.assertTrue(
            SYSTEM_INTERVENTION_REFERENCE.is_file(),
            "system intervention reference must exist before it can be routed",
        )
        result = MODULE.build_package(
            SYSTEM_INTERVENTION_REFERENCE,
            "反复症状、跨边界反馈、政策阻力与时间延迟",
        )

        self.assertEqual("ready", result["status"])
        self.assertEqual("系统反馈、政策阻力与杠杆点", result["matched_task"])
        self.assertIn("强化环", result["content"])
        self.assertIn("平衡环", result["content"])

    def test_linear_local_bug_does_not_select_intervention_reference(self) -> None:
        self.assertTrue(
            SYSTEM_INTERVENTION_REFERENCE.is_file(),
            "system intervention reference must exist before its hard negative can be checked",
        )
        result = MODULE.build_package(
            SYSTEM_INTERVENTION_REFERENCE,
            "根因已定位、路径线性、单点可逆的局部 Bug",
        )

        self.assertEqual("not-found", result["status"])


if __name__ == "__main__":
    unittest.main()
