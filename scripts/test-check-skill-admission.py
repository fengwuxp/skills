#!/usr/bin/env python3
"""Behavior tests for repository Skill admission."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-skill-admission.py"

SPEC = importlib.util.spec_from_file_location("check_skill_admission", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SkillAdmissionTests(unittest.TestCase):
    def test_candidate_policy_requires_a_real_boolean_at_the_policy_path(self) -> None:
        policies = {
            "block-scalar": "notes: |\n  allow_implicit_invocation: false\n",
            "wrong-parent": "interface:\n  allow_implicit_invocation: false\n",
            "quoted-boolean": 'policy:\n  allow_implicit_invocation: "false"\n',
            "duplicate-policy": "policy:\n  allow_implicit_invocation: false\npolicy: {}\n",
            "duplicate-field": "policy:\n  allow_implicit_invocation: false\n  allow_implicit_invocation: false\n",
            "multiple-documents": "policy:\n  allow_implicit_invocation: false\n---\npolicy: {}\n",
        }
        for name, text in policies.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                skill_dir = self.write_skill(root, "candidate", {
                    "status": "candidate", "updated_at": "2026-09-24",
                    "blockers": [{"id": "Q-1", "summary": "pending", "owner": "Owner"}],
                })
                (skill_dir / "agents" / "openai.yaml").write_text(text, encoding="utf-8")

                _, failures = MODULE.audit_skill(skill_dir)

                self.assertTrue(any("invocation" in item for item in failures), failures)
                with self.assertRaisesRegex(ValueError, "invocation"):
                    MODULE.explicit_invocation_skills(root)

    def test_candidate_policy_accepts_valid_flow_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.write_skill(root, "candidate", {
                "status": "candidate", "updated_at": "2026-09-24",
                "blockers": [{"id": "Q-1", "summary": "pending", "owner": "Owner"}],
            })
            (skill_dir / "agents" / "openai.yaml").write_text(
                "policy: {allow_implicit_invocation: false}\n", encoding="utf-8"
            )

            _, failures = MODULE.audit_skill(skill_dir)

            self.assertEqual([], failures)
            self.assertEqual({"candidate"}, MODULE.explicit_invocation_skills(root))

    def test_invocation_policy_rejects_unreadable_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.write_skill(
                root, "new-capability", {"status": "installable", "blockers": []}
            )
            with self.assertRaisesRegex(ValueError, "openai.yaml"):
                MODULE.explicit_invocation_skills(root)
            (skill_dir / "admission.json").write_text("{invalid", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                MODULE.explicit_invocation_skills(root)

    def test_invocation_policy_follows_metadata_not_skill_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.write_skill(
                root, "new-capability", {"status": "installable", "blockers": []}
            )
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir()
            policy = agents_dir / "openai.yaml"
            policy.write_text("policy:\n  allow_implicit_invocation: false\n", encoding="utf-8")
            self.assertEqual(MODULE.explicit_invocation_skills(root), {"new-capability"})
            policy.write_text("policy:\n  allow_implicit_invocation: true\n", encoding="utf-8")
            self.assertEqual(MODULE.explicit_invocation_skills(root), set())
            metadata = {
                "status": "candidate", "evidence_mode": "structural-only", "blockers": []
            }
            (skill_dir / "admission.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            self.assertEqual(MODULE.explicit_invocation_skills(root), {"new-capability"})
            _, failures = MODULE.audit_skill(skill_dir)
            self.assertTrue(any(
                "candidate must set allow_implicit_invocation: false" in failure
                for failure in failures
            ))

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

    def test_dependency_check_rejects_invalid_and_outside_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            outside = Path(temp_dir) / "outside"
            root.mkdir()
            outside.mkdir()
            self.write_skill(outside, "target", {"status": "installable", "blockers": []})
            for dependency in ("../outside/target", str(outside / "target")):
                with self.subTest(dependency=dependency):
                    caller = self.write_skill(
                        root,
                        "caller",
                        {
                            "status": "installable",
                            "blockers": [],
                            "requires": [dependency],
                        },
                    )

                    failures = MODULE.audit_dependencies(caller, root)

                    self.assertTrue(any("valid Skill ID" in item for item in failures), failures)
                    output = StringIO()
                    with patch.object(
                        sys,
                        "argv",
                        [str(SCRIPT), "--check-dependencies", str(caller)],
                    ), redirect_stdout(output):
                        self.assertEqual(1, MODULE.main())
                    self.assertIn("valid Skill ID", output.getvalue())
                    for path in caller.iterdir():
                        path.unlink()
                    caller.rmdir()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            outside = Path(temp_dir) / "outside"
            root.mkdir()
            outside.mkdir()
            self.write_skill(outside, "target", {"status": "installable", "blockers": []})
            (root / "target").symlink_to(outside / "target")
            caller = self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": [], "requires": ["target"]},
            )

            failures = MODULE.audit_dependencies(caller, root)

            self.assertTrue(any("outside repository root" in item for item in failures), failures)

    def test_candidate_caller_can_depend_on_an_installable_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            caller = self.write_skill(
                root,
                "candidate",
                {
                    "status": "candidate",
                    "updated_at": "2026-09-26",
                    "blockers": [{"id": "Q-1", "summary": "pending", "owner": "Owner"}],
                    "requires": ["provider"],
                },
            )
            self.write_skill(root, "provider", {"status": "installable", "blockers": []})

            self.assertEqual([], MODULE.audit_dependencies(caller, root))

    def test_dependency_check_rejects_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            caller = self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": [], "requires": ["provider"]},
            )
            self.write_skill(
                root,
                "provider",
                {"status": "installable", "blockers": [], "requires": ["caller"]},
            )

            failures = MODULE.audit_dependencies(caller, root)

            self.assertTrue(any("dependency cycle caller -> provider -> caller" in item for item in failures), failures)

    def test_dependency_check_keeps_root_aliases_as_distinct_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first_target = root / "one" / "shared"
            second_target = root / "two" / "shared"
            first_target.parent.mkdir()
            second_target.parent.mkdir()
            self.write_skill(first_target.parent, "shared", {"status": "installable", "blockers": []})
            self.write_skill(
                second_target.parent,
                "shared",
                {"status": "installable", "blockers": [], "requires": ["missing"]},
            )
            (root / "first").symlink_to(first_target)
            (root / "second").symlink_to(second_target)
            caller = self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": [], "requires": ["first", "second"]},
            )

            failures = MODULE.audit_dependencies(caller, root)

            self.assertTrue(any("requires unknown skill missing" in item for item in failures), failures)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first_target = root / "one" / "shared"
            second_target = root / "two" / "shared"
            first_target.parent.mkdir()
            second_target.parent.mkdir()
            self.write_skill(first_target.parent, "shared", {"status": "installable", "blockers": []})
            self.write_skill(
                second_target.parent,
                "shared",
                {"status": "installable", "blockers": [], "requires": ["provider"]},
            )
            self.write_skill(root, "provider", {"status": "installable", "blockers": []})
            (root / "first").symlink_to(first_target)
            (root / "second").symlink_to(second_target)
            caller = self.write_skill(
                root,
                "caller",
                {"status": "installable", "blockers": [], "requires": ["first", "second"]},
            )

            self.assertEqual([], MODULE.audit_dependencies(caller, root))

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
