#!/usr/bin/env python3
"""Behavior tests for Skill evidence-bound delivery gates."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-skill-evidence.py"
EVALUATOR_PATH = ROOT / "scripts" / "evaluate-skill-behavior.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


CHECKER = load_module("check_skill_evidence", CHECKER_PATH)
EVALUATOR = load_module("skill_behavior_evaluator_for_evidence_test", EVALUATOR_PATH)


class SkillEvidenceTests(unittest.TestCase):
    def build_repository(self, root: Path, *, scored: bool = True) -> Path:
        (root / "scripts").mkdir()
        fixtures = root / "fixtures" / "skill-eval"
        fixtures.mkdir(parents=True)
        skill_dir = root / "demo-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        (root / "baseline.txt").write_text("baseline\n", encoding="utf-8")
        (root / "candidate.txt").write_text("candidate\n", encoding="utf-8")

        previous_root = EVALUATOR.ROOT
        EVALUATOR.ROOT = root
        try:
            case_data = {
                "version": 1,
                "description": "test behavior contract",
                "source_profiles": {
                    "baseline": {
                        "id": "baseline",
                        "paths": ["baseline.txt"],
                        "sha256": EVALUATOR.source_set_digest(["baseline.txt"]),
                    },
                    "candidate": {
                        "id": "candidate",
                        "paths": ["candidate.txt"],
                        "sha256": EVALUATOR.source_set_digest(["candidate.txt"]),
                    },
                },
                "rubric": {
                    "scale": {"min": 1, "max": 5},
                    "weights": {
                        "correctness": 0.4,
                        "autonomy": 0.15,
                        "actionability": 0.2,
                        "safety": 0.15,
                        "concision": 0.1,
                    },
                },
                "release_gate": {
                    "mode": "non_regression",
                    "candidate_blockers_must_be_zero": True,
                    "max_correctness_regression": 0.0,
                    "max_safety_regression": 0.0,
                    "candidate_weighted_score_must_improve": False,
                    "require_auditable_judgments": True,
                    "high_risk_candidate_criteria_min_pass_rate": 1.0,
                },
                "cases": [
                    {
                        "id": f"case-{index}",
                        "category": "delivery",
                        "risk": "high",
                        "prompt": f"prompt {index}",
                        "criteria": ["preserves the contract"],
                    }
                    for index in range(1, 6)
                ],
            }
            cases_path = fixtures / "demo-behavior-cases.json"
            cases_path.write_text(
                json.dumps(case_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            gate: dict[str, object] = {
                "cases": "fixtures/skill-eval/demo-behavior-cases.json"
            }
            if scored:
                responses = []
                case_digest = EVALUATOR._case_digest(case_data)
                for case in case_data["cases"]:
                    for condition in EVALUATOR.CONDITIONS:
                        profile = case_data["source_profiles"][condition]
                        responses.append(
                            {
                                "case_id": case["id"],
                                "case_sha256": case_digest,
                                "condition": condition,
                                "trial": 1,
                                "response": f"{case['id']} {condition}",
                                "runner": "maker",
                                "model": "model",
                                "source_profile": profile["id"],
                                "source_sha256": profile["sha256"],
                            }
                        )
                blind_rows, key = EVALUATOR.blind_responses(
                    case_data, responses, seed=731
                )
                score_rows = []
                for task in blind_rows:
                    for response in task["responses"]:
                        score_rows.append(
                            {
                                "pair_id": task["pair_id"],
                                "label": response["label"],
                                "correctness": 4,
                                "autonomy": 4,
                                "actionability": 4,
                                "safety": 4,
                                "concision": 4,
                                "blocker": False,
                                "criteria": [True],
                                "notes": "passes",
                                "blind_sha256": key["blind_sha256"],
                                "evaluation_id": "evaluation",
                                "judge": "checker",
                                "judge_model": "judge-model",
                                "judged_at": "2026-08-22T12:00:00+08:00",
                            }
                        )
                responses_path = fixtures / "demo-responses.jsonl"
                scores_path = fixtures / "demo-scores.jsonl"
                EVALUATOR.write_jsonl(responses_path, responses)
                EVALUATOR.write_jsonl(scores_path, score_rows)
                gate.update(
                    {
                        "responses": "fixtures/skill-eval/demo-responses.jsonl",
                        "scores": "fixtures/skill-eval/demo-scores.jsonl",
                        "seed": 731,
                    }
                )

            (skill_dir / "admission.json").write_text(
                json.dumps(
                    {
                        "status": "installable",
                        "blockers": [],
                        "evidence_mode": "behavior-scored" if scored else "contract-only",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (fixtures / "evidence-gates.json").write_text(
                json.dumps(
                    {"version": 1, "skills": {"demo-skill": [gate]}},
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            return skill_dir
        finally:
            EVALUATOR.ROOT = previous_root

    def test_valid_scored_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root)

            self.assertEqual([], CHECKER.audit_evidence(skill_dir, root))

    def test_source_drift_blocks_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root)
            (root / "candidate.txt").write_text("changed\n", encoding="utf-8")

            failures = CHECKER.audit_evidence(skill_dir, root)

            self.assertTrue(any("source set changed" in failure for failure in failures))

    def test_response_case_digest_drift_blocks_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root)
            cases_path = root / "fixtures" / "skill-eval" / "demo-behavior-cases.json"
            case_data = json.loads(cases_path.read_text(encoding="utf-8"))
            case_data["cases"][0]["prompt"] = "changed prompt"
            cases_path.write_text(json.dumps(case_data, indent=2) + "\n", encoding="utf-8")

            failures = CHECKER.audit_evidence(skill_dir, root)

            self.assertTrue(any("case_sha256" in failure for failure in failures))

    def test_contract_only_checks_case_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root, scored=False)

            self.assertEqual([], CHECKER.audit_evidence(skill_dir, root))

    def test_contract_only_fixture_drift_does_not_claim_live_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root, scored=False)
            (root / "candidate.txt").write_text("changed\n", encoding="utf-8")

            self.assertEqual([], CHECKER.audit_evidence(skill_dir, root))
            self.assertEqual(
                "OK skill contract: demo-skill "
                "(mode=contract-only; source-profile freshness=deferred)",
                CHECKER.readiness_summary("demo-skill", "contract-only"),
            )

    def test_repository_summary_preserves_mixed_evidence_modes(self) -> None:
        self.assertEqual(
            "OK skill delivery gates: repository "
            "(modes declared per admission.json; "
            "contract-only source-profile freshness=deferred per Skill)",
            CHECKER.repository_readiness_summary(),
        )

    def test_incomplete_scored_gate_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root, scored=False)
            manifest = root / "fixtures" / "skill-eval" / "evidence-gates.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["skills"]["demo-skill"][0]["responses"] = (
                "fixtures/skill-eval/demo-responses.jsonl"
            )
            manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            failures = CHECKER.audit_evidence(skill_dir, root)

            self.assertTrue(any("responses, scores, and seed" in failure for failure in failures))

    def test_missing_evidence_mode_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root, scored=False)
            metadata_path = skill_dir / "admission.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata.pop("evidence_mode")
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

            failures = CHECKER.audit_evidence(skill_dir, root)

            self.assertTrue(any("evidence_mode" in failure for failure in failures))

    def test_behavior_scored_requires_a_scored_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = self.build_repository(root, scored=False)
            metadata_path = skill_dir / "admission.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["evidence_mode"] = "behavior-scored"
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

            failures = CHECKER.audit_evidence(skill_dir, root)

            self.assertTrue(any("behavior-scored" in failure for failure in failures))

    def test_contract_only_requires_a_case_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixtures = root / "fixtures" / "skill-eval"
            fixtures.mkdir(parents=True)
            (fixtures / "evidence-gates.json").write_text(
                json.dumps({"version": 1, "skills": {}}), encoding="utf-8"
            )
            skill_dir = root / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
            (skill_dir / "admission.json").write_text(
                json.dumps(
                    {
                        "status": "installable",
                        "evidence_mode": "contract-only",
                        "blockers": [],
                    }
                ),
                encoding="utf-8",
            )

            failures = CHECKER.audit_evidence(skill_dir, root)

            self.assertTrue(any("requires at least one case gate" in failure for failure in failures))

    def test_repository_rejects_unwired_behavior_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture_dir = root / "fixtures" / "skill-eval"
            fixture_dir.mkdir(parents=True)
            (fixture_dir / "evidence-gates.json").write_text(
                json.dumps({"version": 1, "skills": {}}), encoding="utf-8"
            )
            skill_dir = root / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
            (skill_dir / "admission.json").write_text(
                json.dumps(
                    {
                        "status": "installable",
                        "evidence_mode": "contract-only",
                        "blockers": [],
                    }
                ),
                encoding="utf-8",
            )
            (fixture_dir / "orphan-behavior-cases.json").write_text("{}", encoding="utf-8")

            failures = CHECKER.audit_repository(root)

            self.assertTrue(any("orphan-behavior-cases.json" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
