#!/usr/bin/env python3
"""Integration checks for bounded reading of project Skill references."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "wise-agent" / "scripts" / "read-reference-sections.py"
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


if __name__ == "__main__":
    unittest.main()
