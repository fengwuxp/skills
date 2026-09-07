#!/usr/bin/env python3
"""Behavior tests for repository Skill delivery gates."""

from __future__ import annotations

import importlib.util
import json
import runpy
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
    def test_candidate_invocation_policy_matches_both_evaluators(self) -> None:
        fixture_audit = runpy.run_path(str(ROOT / "scripts/audit-skill-eval-fixtures.py"))
        for skill in (
            "document-authoring",
            "payment-funds-review",
            "yuque-document-publisher",
        ):
            with self.subTest(skill=skill):
                self.assertIn(skill, MODULE.EXPLICIT_INVOCATION_SKILLS)
                self.assertIn(skill, fixture_audit["EXPLICIT_INVOCATION_SKILLS"])

    def test_candidate_implicit_positive_is_rejected(self) -> None:
        fixture_audit = runpy.run_path(str(ROOT / "scripts/audit-skill-eval-fixtures.py"))
        for skill in (
            "document-authoring",
            "payment-funds-review",
            "yuque-document-publisher",
        ):
            with self.subTest(skill=skill):
                payload = json.loads(
                    (ROOT / "fixtures/skill-eval/prompt-cases.json").read_text(encoding="utf-8")
                )
                case = next(
                    case for case in payload["cases"]
                    if case["skill"] == skill and case["should_trigger"]
                )
                case["query"] = "请根据已经确认的材料给出范围内的结论，不加载候选能力。"
                failures = fixture_audit["audit_data"](payload, label="candidate-policy")
                self.assertTrue(any(
                    f"{skill} positive cases require an explicit skill name" in failure
                    for failure in failures
                ))
                stats = MODULE.prompt_fixture_stats(skill, payload)
                _, warnings = MODULE.score_prompt_fixtures(skill, stats, payload)
                self.assertIn(f"{skill}: positive prompt fixture lacks explicit invocation", warnings)

    def test_entrypoint_line_count_does_not_change_quality_score(self) -> None:
        baseline, _ = MODULE.score_progressive(100, 1, [])
        for lines in (350, 351, 500, 501, 9000):
            with self.subTest(lines=lines):
                self.assertEqual(MODULE.score_progressive(lines, 1, [])[0], baseline)
        self.assertLess(
            MODULE.score_progressive(501, 1, ["references/missing.md"])[0], baseline
        )

    def test_reference_size_does_not_change_quality_score(self) -> None:
        baseline, _ = MODULE.score_references(
            "senior-software-architect", 1, 100, 8, [], [], 80
        )
        for lines in (400, 550, 551, 5001, 7001, 8001):
            with self.subTest(lines=lines):
                score, warnings = MODULE.score_references(
                    "senior-software-architect", 1, lines, 8,
                    [{"path": "references/guide.md", "lines": lines}],
                    [{"path": "references/guide.md", "title": "任务索引", "lines": lines}],
                    80,
                )
                self.assertEqual(score, baseline)
                self.assertFalse(any("hard budget" in warning for warning in warnings))

    def test_reference_searchability_measures_navigation_not_size(self) -> None:
        reference = {
            "path": "references/guide.md",
            "has_progressive_headers": True,
            "has_task_index": True,
            "level_2_sections": 4,
        }
        baseline = MODULE.reference_searchability_score(
            1, 100, [{**reference, "lines": 100}], [{"lines": 100}]
        )
        for lines in (400, 551, 8001):
            with self.subTest(lines=lines):
                self.assertEqual(
                    MODULE.reference_searchability_score(
                        1, lines, [{**reference, "lines": lines}], [{"lines": lines}]
                    ),
                    baseline,
                )
        self.assertLess(
            MODULE.reference_searchability_score(
                1, 100,
                [{**reference, "lines": 100, "has_task_index": False}],
                [{"lines": 100}],
            ),
            baseline,
        )

    def test_explicit_only_skill_counts_all_supported_invocation_aliases(self) -> None:
        stats = MODULE.prompt_fixture_stats(
            "wise-agent",
            {
                "cases": [
                    {"skill": "wise-agent", "query": "$wise-agent：推进", "should_trigger": True},
                    {"skill": "wise-agent", "query": "wise-agent，推进", "should_trigger": True},
                    {"skill": "wise-agent", "query": "知止者，推进", "should_trigger": True},
                ]
            },
        )

        self.assertEqual(stats["positive_without_name_cases"], 0)
        _, warnings = MODULE.score_prompt_fixtures("wise-agent", stats, {"evaluation_dimensions": []})
        self.assertNotIn("wise-agent: positive prompt fixture lacks explicit invocation", warnings)

    def test_learning_coach_is_evaluated_as_explicit_only(self) -> None:
        stats = MODULE.prompt_fixture_stats(
            "learning-coach",
            {
                "cases": [
                    {"skill": "learning-coach", "query": "$learning-coach：开始", "should_trigger": True},
                    {"skill": "learning-coach", "query": "learning-coach，继续", "should_trigger": True},
                    {"skill": "learning-coach", "query": "持续学习教练，复训", "should_trigger": True},
                ]
            },
        )

        self.assertIn("learning-coach", MODULE.EXPLICIT_INVOCATION_SKILLS)
        self.assertEqual(stats["positive_without_name_cases"], 0)
        _, warnings = MODULE.score_prompt_fixtures(
            "learning-coach", stats, {"evaluation_dimensions": []}
        )
        self.assertNotIn(
            "learning-coach: positive prompt fixture lacks explicit invocation", warnings
        )

    def test_extract_frontmatter_supports_folded_description_blocks(self) -> None:
        frontmatter, _ = MODULE.extract_frontmatter(
            "---\n"
            "name: review\n"
            "description: > # folded explanation\n"
            "  Use when reviewing code\n"
            "  across repositories.\n"
            "---\n\n"
            "# Review\n"
        )

        self.assertEqual(
            frontmatter["description"],
            "Use when reviewing code across repositories.",
        )

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
        return skill_dir

    def test_delivery_gates_are_reported_separately_from_static_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture_dir = root / "fixtures" / "skill-eval"
            fixture_dir.mkdir(parents=True)
            (fixture_dir / "evidence-gates.json").write_text(
                json.dumps({"version": 1, "skills": {}}),
                encoding="utf-8",
            )
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
            self.assertEqual(ready_gates["evidence_readiness"], "ready")
            self.assertEqual(ready_gates["evidence_mode"], "structural-only")
            self.assertEqual(ready_gates["installed_parity"], "not_checked")
            self.assertEqual(ready_gates["delivery_readiness"], "requires_installed_parity")
            self.assertEqual(candidate_gates["delivery_readiness"], "blocked")
            self.assertEqual(blocked_gates["dependency_readiness"], "blocked")
            self.assertIn("candidate-skill", " ".join(blocked_gates["blockers"]))

    def test_delivery_gate_blocks_stale_evidence_before_parity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture_dir = root / "fixtures" / "skill-eval"
            fixture_dir.mkdir(parents=True)
            (fixture_dir / "evidence-gates.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "skills": {
                            "ready-skill": [
                                {
                                    "cases": "fixtures/skill-eval/missing-behavior-cases.json"
                                }
                            ]
                        },
                    }
                ),
                encoding="utf-8",
            )
            skill_dir = self.write_skill(
                root,
                "ready-skill",
                {
                    "status": "installable",
                    "evidence_mode": "contract-only",
                    "blockers": [],
                    "requires": [],
                },
            )

            gates = MODULE.delivery_gates(skill_dir, root)

            self.assertEqual("blocked", gates["evidence_readiness"])
            self.assertEqual("blocked", gates["installed_parity"])
            self.assertEqual("blocked", gates["delivery_readiness"])
            self.assertTrue(any("missing-behavior-cases" in item for item in gates["blockers"]))

    def test_catalog_audit_finds_cross_source_id_and_description_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "project"
            plugin_root = root / "plugin"
            project_root.mkdir()
            plugin_root.mkdir()

            def write_catalog_skill(
                catalog_root: Path,
                directory: str,
                name: str,
                description: str,
            ) -> None:
                skill_dir = catalog_root / directory
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(
                    "---\n"
                    f"name: {name}\n"
                    f"description: {description}\n"
                    "---\n\n"
                    f"# {name}\n",
                    encoding="utf-8",
                )

            write_catalog_skill(project_root, "review", "review", "Use when reviewing code")
            write_catalog_skill(plugin_root, "review-copy", "review", "Use when checking code")
            write_catalog_skill(project_root, "docs", "docs", "Use when writing formal reports")
            write_catalog_skill(plugin_root, "reports", "reports", "Use when  writing formal reports")

            report = MODULE.audit_skill_catalog(
                [("project", project_root), ("plugin", plugin_root)]
            )

            self.assertEqual(report["status"], "conflict")
            self.assertEqual(
                [entry["source"] for entry in report["duplicate_skill_ids"]["review"]],
                ["plugin", "project"],
            )
            duplicate_descriptions = list(report["duplicate_descriptions"].values())
            self.assertEqual(
                {entry["name"] for entry in duplicate_descriptions[0]},
                {"docs", "reports"},
            )

    def test_catalog_audit_treats_same_target_symlinks_as_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agents_root = root / "agents"
            codex_root = root / "codex"
            agents_root.mkdir()
            codex_root.mkdir()
            target = agents_root / "review"
            target.mkdir()
            (target / "SKILL.md").write_text(
                "---\n"
                "name: review\n"
                "description: Use when reviewing code\n"
                "---\n\n"
                "# Review\n",
                encoding="utf-8",
            )
            (codex_root / "review").symlink_to(target, target_is_directory=True)

            report = MODULE.audit_skill_catalog(
                [("agents", agents_root), ("codex", codex_root)]
            )

            self.assertEqual(report["status"], "clean")
            self.assertEqual(report["duplicate_skill_ids"], {})
            self.assertIn("review", report["aliases"])

    def test_catalog_audit_uses_yaml_semantics_and_rejects_invalid_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first" / "review"
            second = root / "second" / "review-copy"
            invalid = root / "second" / "invalid"
            null_metadata = root / "second" / "null-metadata"
            collection_metadata = root / "second" / "collection-metadata"
            numeric_metadata = root / "second" / "numeric-metadata"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            invalid.mkdir()
            null_metadata.mkdir()
            collection_metadata.mkdir()
            numeric_metadata.mkdir()
            (first / "SKILL.md").write_text(
                "---\nname: review\ndescription: Use when reviewing code\n---\n# Review\n",
                encoding="utf-8",
            )
            (second / "SKILL.md").write_text(
                "---\nname: review # same YAML scalar\n"
                "description: Use when reviewing code # same description\n---\n# Review\n",
                encoding="utf-8",
            )
            (invalid / "SKILL.md").write_text("# Missing frontmatter\n", encoding="utf-8")
            (null_metadata / "SKILL.md").write_text(
                "---\nname: null\ndescription: ~\n---\n# Null metadata\n",
                encoding="utf-8",
            )
            (collection_metadata / "SKILL.md").write_text(
                "---\nname: []\ndescription: {}\n---\n# Collection metadata\n",
                encoding="utf-8",
            )
            (numeric_metadata / "SKILL.md").write_text(
                "---\nname: 1.2e3\ndescription: 2026-08-07\n---\n# Numeric metadata\n",
                encoding="utf-8",
            )

            report = MODULE.audit_skill_catalog(
                [("first", root / "first"), ("second", root / "second")]
            )

            self.assertEqual(report["status"], "conflict")
            self.assertIn("review", report["duplicate_skill_ids"])
            self.assertEqual(len(report["invalid_skills"]), 4)

    def test_catalog_audit_scans_nested_explicit_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            nested = root / "plugin" / "1.0.0" / "skills" / "review"
            nested.mkdir(parents=True)
            (nested / "SKILL.md").write_text(
                "---\nname: review\ndescription: Use when reviewing code\n---\n# Review\n",
                encoding="utf-8",
            )

            report = MODULE.audit_skill_catalog([("plugins", root)])

            self.assertEqual([entry["name"] for entry in report["entries"]], ["review"])


if __name__ == "__main__":
    unittest.main()
