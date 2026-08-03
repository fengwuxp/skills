#!/usr/bin/env python3
"""Behavior tests for repository Skill delivery gates."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate-skills.py"

SPEC = importlib.util.spec_from_file_location("evaluate_skills", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SkillDeliveryGateTests(unittest.TestCase):
    @staticmethod
    def write_skill(root: Path, name: str, metadata: dict[str, object]) -> Path:
        skill_dir = root / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
        (skill_dir / "admission.json").write_text(
            json.dumps(metadata),
            encoding="utf-8",
        )
        return skill_dir

    def test_delivery_gates_are_reported_separately_from_static_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ready = self.write_skill(
                root,
                "ready-skill",
                {"status": "installable", "blockers": [], "requires": []},
            )
            candidate = self.write_skill(
                root,
                "candidate-skill",
                {
                    "status": "candidate",
                    "updated_at": "2026-08-03",
                    "blockers": [
                        {"id": "Q-1", "summary": "pending", "owner": "Owner"}
                    ],
                },
            )
            blocked = self.write_skill(
                root,
                "blocked-skill",
                {
                    "status": "installable",
                    "blockers": [],
                    "requires": ["candidate-skill"],
                },
            )

            ready_gates = MODULE.delivery_gates(ready, root)
            candidate_gates = MODULE.delivery_gates(candidate, root)
            blocked_gates = MODULE.delivery_gates(blocked, root)

            self.assertEqual(ready_gates["admission_status"], "installable")
            self.assertEqual(ready_gates["dependency_readiness"], "ready")
            self.assertEqual(ready_gates["installed_parity"], "not_checked")
            self.assertEqual(ready_gates["delivery_readiness"], "requires_installed_parity")
            self.assertEqual(candidate_gates["delivery_readiness"], "blocked")
            self.assertEqual(blocked_gates["dependency_readiness"], "blocked")
            self.assertIn("candidate-skill", " ".join(blocked_gates["blockers"]))


if __name__ == "__main__":
    unittest.main()
