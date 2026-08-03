#!/usr/bin/env python3
"""Behavior tests for repository Skill admission."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-skill-admission.py"

SPEC = importlib.util.spec_from_file_location("check_skill_admission", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SkillAdmissionTests(unittest.TestCase):
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

    def test_missing_admission_metadata_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "new-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# New Skill\n", encoding="utf-8")

            status, failures = MODULE.audit_skill(skill_dir)

            self.assertEqual(status, "invalid")
            self.assertTrue(any("missing admission.json" in item for item in failures))

    def test_installable_skill_cannot_depend_on_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            caller = self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": [], "requires": ["candidate"]},
            )
            self.write_skill(
                root,
                "candidate",
                {
                    "status": "candidate",
                    "updated_at": "2026-08-03",
                    "blockers": [
                        {"id": "Q-1", "summary": "pending", "owner": "Owner"}
                    ],
                },
            )

            failures = MODULE.audit_dependencies(caller, root)

            self.assertEqual(MODULE.dependency_names(caller), ["candidate"])
            self.assertTrue(
                any(
                    "requires non-installable skill candidate (candidate)" in item
                    for item in failures
                )
            )

    def test_repository_rejects_unknown_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": [], "requires": ["missing"]},
            )

            failures = MODULE.audit_repository(root)

            self.assertTrue(any("requires unknown skill missing" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
