#!/usr/bin/env python3
"""Structural tests for the legacy trigger-path validator boundary."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-trigger-paths.py"
VALIDATE_SCRIPT = ROOT / "scripts" / "validate.sh"
SYNC_SCRIPT = ROOT / "sync-skills.sh"
EVIDENCE_FUNCTIONS = {
    "behavior_fixture_fingerprint",
    "file_fingerprint",
    "source_set_fingerprint",
}


class TriggerValidatorStructureTests(unittest.TestCase):
    def test_repo_agents_delegates_conditional_detail(self) -> None:
        agents_rules = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("resource-capability-distiller/references/distillation-contract.md", agents_rules)
        self.assertIn("wise-agent/references/engineering-governance.md", agents_rules)
        self.assertIn("wise-agent/references/skill-learning-backflow.md", agents_rules)
        self.assertIn("wise-agent/references/code-delivery.md", agents_rules)
        self.assertNotIn("1. `library / API reference`", agents_rules)
        self.assertNotIn("目标 Skill:\n触发样例:", agents_rules)

    def test_behavior_evidence_is_not_owned_by_trigger_validator(self) -> None:
        tree = ast.parse(VALIDATOR.read_text(encoding="utf-8"))
        definitions = {
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }

        self.assertFalse(EVIDENCE_FUNCTIONS & definitions)
        self.assertFalse(EVIDENCE_FUNCTIONS & calls)

    def test_unified_validation_runs_the_evidence_checker(self) -> None:
        validate_script = VALIDATE_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("scripts/test-check-skill-evidence.py", validate_script)
        self.assertIn("scripts/check-skill-evidence.py", validate_script)

    def test_sync_blocks_non_current_evidence(self) -> None:
        sync_script = SYNC_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("scripts/check-skill-evidence.py", sync_script)
        self.assertIn("Skill evidence is not current", sync_script)
        self.assertIn("Cannot sync all: evidence is not current", sync_script)
        self.assertIn("All sync aborted before writing", sync_script)


if __name__ == "__main__":
    unittest.main()
