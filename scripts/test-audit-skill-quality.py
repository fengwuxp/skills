#!/usr/bin/env python3
"""Behavior tests for Skill Level-1 metadata quality auditing."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit-skill-quality.py"

SPEC = importlib.util.spec_from_file_location("audit_skill_quality", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SkillQualityAuditTests(unittest.TestCase):
    @staticmethod
    def write_skill(root: Path, default_prompt: str) -> None:
        skill = root / "sample-skill"
        (skill / "agents").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            "description: Use when reviewing a sample Skill package and its metadata.\n"
            "---\n\n"
            "# Sample\n",
            encoding="utf-8",
        )
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: \"Sample\"\n"
            "  short_description: \"Sample metadata\"\n"
            f"  default_prompt: \"{default_prompt}\"\n"
            "policy:\n"
            "  allow_implicit_invocation: true\n",
            encoding="utf-8",
        )

    def test_short_invocation_prompt_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_skill(root, "Use $sample-skill 完成当前范围内的样例审查。")

            warnings = MODULE.audit(root)

            self.assertFalse(any("default_prompt" in warning for warning in warnings))

    def test_workflow_heavy_default_prompt_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_skill(
                root,
                "Use $sample-skill 先判断方向，再展开全部对象、流程、规则和页面；"
                "正式正文按背景、目标、定性、概要、详细设计、流程、规则、风险和验收展开；"
                "详细执行控制进入执行计划。",
            )

            warnings = MODULE.audit(root)

            self.assertTrue(
                any("default_prompt" in warning and "workflow" in warning for warning in warnings)
            )

    def test_oversized_default_prompt_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_skill(root, "Use $sample-skill " + "详细步骤" * 60)

            warnings = MODULE.audit(root)

            self.assertTrue(
                any("default_prompt" in warning and "chars" in warning for warning in warnings)
            )


if __name__ == "__main__":
    unittest.main()
