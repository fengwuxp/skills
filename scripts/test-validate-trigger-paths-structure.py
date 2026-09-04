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
LEGACY_VALIDATOR_MAX_LINES = 25_086


class TriggerValidatorStructureTests(unittest.TestCase):
    def test_legacy_validator_is_frozen_for_new_invariants(self) -> None:
        validator_source = VALIDATOR.read_text(encoding="utf-8")
        agents_rules = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(validator_source.splitlines()), LEGACY_VALIDATOR_MAX_LINES)
        self.assertIn("New invariants belong in Skill-local fixtures or validators", validator_source)
        self.assertIn("validate-trigger-paths.py` 只修复或删除既有检查", agents_rules)

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

    def test_sync_blocks_non_ready_delivery_gate(self) -> None:
        sync_script = SYNC_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("scripts/check-skill-evidence.py", sync_script)
        self.assertIn("Skill delivery gate is not ready", sync_script)
        self.assertIn("Cannot sync all: delivery gate is not ready", sync_script)
        self.assertIn("All sync aborted before writing", sync_script)

    def test_runtime_parity_is_an_explicit_validation_gate(self) -> None:
        validate_script = VALIDATE_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("--require-installed-parity", validate_script)
        self.assertIn("VALIDATE_INSTALLED_SKILLS", validate_script)
        self.assertIn("SKIP installed parity", validate_script)

    def test_runtime_parity_fails_closed_on_dependency_or_evidence_drift(self) -> None:
        parity_script = (ROOT / "scripts" / "validate-installed-skills.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("installed skill has non-installable dependencies", parity_script)
        self.assertIn("installed skill delivery gate is not ready", parity_script)
        self.assertNotIn("SKIP installed parity: ${skill_name} has", parity_script)
        self.assertNotIn("SKIP installed parity: ${skill_name} evidence", parity_script)


if __name__ == "__main__":
    unittest.main()
