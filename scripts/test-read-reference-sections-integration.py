#!/usr/bin/env python3
"""Integration checks for bounded reading of project Skill references."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "wise-agent" / "scripts" / "read-reference-sections.py"
MOTION_CANDIDATE = (
    ROOT
    / "fixtures"
    / "skill-eval"
    / "source-profiles"
    / "ui-motion-craft-candidate.md"
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
        result = MODULE.build_from_path(
            ROOT / "senior-software-architect" / "references",
            "反复症状、跨边界反馈、政策阻力与时间延迟",
        )

        self.assertEqual("ready", result["status"])
        self.assertTrue(result["source"].endswith("system-intervention-and-backcasting.md"))
        self.assertEqual("系统反馈、政策阻力与杠杆点", result["matched_task"])
        self.assertIn("强化环", result["content"])
        self.assertIn("平衡环", result["content"])

    def test_linear_local_bug_does_not_select_intervention_reference(self) -> None:
        result = MODULE.build_from_path(
            ROOT / "senior-software-architect" / "references",
            "根因已定位、路径线性、单点可逆的局部 Bug",
        )

        self.assertEqual("not-found", result["status"])

    def test_motion_audit_selects_motion_craft_reference(self) -> None:
        self.assertTrue(MOTION_CANDIDATE.is_file())
        result = MODULE.build_package(
            MOTION_CANDIDATE,
            "审计 Web 动效、缓动、可中断性和减少动效",
        )

        self.assertEqual("ready", result["status"])
        self.assertEqual("动效审计、缓动、可中断与减少动效 / 修复计划", result["matched_task"])
        self.assertIn("动效决策门", result["content"])
        self.assertIn("被拒候选", result["content"])

    def test_motion_candidate_routes_interruptible_drawer_language(self) -> None:
        self.assertTrue(MOTION_CANDIDATE.is_file())
        result = MODULE.build_package(
            MOTION_CANDIDATE,
            "抽屉拖拽回弹途中再次抓住并反向拖动",
        )

        self.assertEqual("ready", result["status"])
        self.assertEqual(
            "抽屉拖拽回弹途中再次抓住并反向拖动 / 可中断交互",
            result["matched_task"],
        )
        self.assertIn("连续与可中断", result["content"])

    def test_motion_candidate_routes_vocabulary_language(self) -> None:
        self.assertTrue(MOTION_CANDIDATE.is_file())
        result = MODULE.build_package(
            MOTION_CANDIDATE,
            "iOS 列表拖过边界后越来越难拖、松手又回来的效果叫什么",
        )

        self.assertEqual("ready", result["status"])
        self.assertEqual(
            "拖过边界后越来越难拖、松手回来的效果叫什么 / Rubber-banding",
            result["matched_task"],
        )
        self.assertIn("Rubber-banding", result["content"])

    def test_motion_candidate_stays_outside_installable_skill(self) -> None:
        self.assertTrue(MOTION_CANDIDATE.is_file())
        self.assertFalse(
            (ROOT / "ui-design-expert" / "references" / "motion-and-interaction-craft.md").exists()
        )


if __name__ == "__main__":
    unittest.main()
