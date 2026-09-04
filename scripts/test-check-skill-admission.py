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
        metadata = dict(metadata)
        metadata.setdefault("evidence_mode", "structural-only")
        skill_dir = root / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
        (skill_dir / "admission.json").write_text(
            json.dumps(metadata),
            encoding="utf-8",
        )
        if metadata.get("status") == "candidate":
            agent_dir = skill_dir / "agents"
            agent_dir.mkdir()
            (agent_dir / "openai.yaml").write_text(
                "policy:\n  allow_implicit_invocation: false\n",
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

    def test_candidate_must_disable_implicit_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.write_skill(
                Path(temp_dir),
                "candidate",
                {
                    "status": "candidate",
                    "updated_at": "2026-08-17",
                    "blockers": [
                        {"id": "Q-1", "summary": "pending", "owner": "Owner"}
                    ],
                },
            )
            agent_dir = skill_dir / "agents"
            agent_dir.mkdir(exist_ok=True)
            (agent_dir / "openai.yaml").write_text(
                "policy:\n  allow_implicit_invocation: true\n",
                encoding="utf-8",
            )

            _, failures = MODULE.audit_skill(skill_dir)

            self.assertTrue(
                any(
                    "candidate must set allow_implicit_invocation: false" in item
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

    def test_cross_skill_relative_reference_requires_declared_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            caller = self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": []},
            )
            (caller / "SKILL.md").write_text(
                "Read `../provider/references/contract.md`.\n",
                encoding="utf-8",
            )

            _, failures = MODULE.audit_skill(caller)

            self.assertTrue(
                any("cross-Skill relative reference requires admission.json dependency: provider" in item for item in failures)
            )

    def test_declared_cross_skill_relative_reference_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            caller = self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": [], "requires": ["provider"]},
            )
            (caller / "SKILL.md").write_text(
                "Read `../provider/references/contract.md`.\n",
                encoding="utf-8",
            )

            _, failures = MODULE.audit_skill(caller)

            self.assertEqual([], failures)

    def test_installable_allows_valid_non_distribution_restrictions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.write_skill(
                Path(temp_dir),
                "restricted-installable",
                {
                    "status": "installable",
                    "blockers": [],
                    "restrictions": [
                        {
                            "id": "R-001",
                            "scope": "distribution",
                            "summary": "local install only; distribution is not authorized",
                            "owner": "rights owner",
                        }
                    ],
                },
            )

            status, failures = MODULE.audit_skill(skill_dir)

            self.assertEqual("installable", status)
            self.assertEqual([], failures)

    def test_rejects_incomplete_restriction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.write_skill(
                Path(temp_dir),
                "invalid-restriction",
                {
                    "status": "installable",
                    "blockers": [],
                    "restrictions": [{"id": "R-001"}],
                },
            )

            _, failures = MODULE.audit_skill(skill_dir)

            self.assertTrue(
                any("restriction[1].summary must be non-empty" in item for item in failures)
            )
            self.assertTrue(
                any("restriction[1].owner must be non-empty" in item for item in failures)
            )
            self.assertTrue(
                any("restriction[1].scope must be distribution" in item for item in failures)
            )

    def test_rejects_unknown_restriction_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.write_skill(
                Path(temp_dir),
                "invalid-restriction-scope",
                {
                    "status": "installable",
                    "blockers": [],
                    "restrictions": [
                        {
                            "id": "R-001",
                            "scope": "installation",
                            "summary": "do not install",
                            "owner": "safety owner",
                        }
                    ],
                },
            )

            _, failures = MODULE.audit_skill(skill_dir)

            self.assertTrue(
                any("restriction[1].scope must be distribution" in item for item in failures)
            )

    def test_evidence_mode_must_be_declared_and_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.write_skill(
                root,
                "invalid-evidence-mode",
                {
                    "status": "installable",
                    "blockers": [],
                    "evidence_mode": "live-and-magical",
                },
            )

            _, failures = MODULE.audit_skill(skill_dir)

            self.assertTrue(any("evidence_mode" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
