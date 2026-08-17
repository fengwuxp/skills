#!/usr/bin/env python3
"""Behavior tests for the offline Skill baseline/candidate evaluator."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate-skill-behavior.py"
CASES = ROOT / "fixtures" / "skill-eval" / "behavior-cases.json"

SPEC = importlib.util.spec_from_file_location("evaluate_skill_behavior", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SkillBehaviorEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case_data = MODULE.load_json(CASES)
        MODULE.validate_cases(cls.case_data)

    def response_rows(self, case_data: dict[str, object] | None = None) -> list[dict[str, object]]:
        case_data = case_data or self.case_data
        source_profiles = case_data.get("source_profiles")
        rows = []
        for case in case_data["cases"]:
            for condition in ("baseline", "candidate"):
                row = {
                    "case_id": case["id"],
                    "trial": 1,
                    "condition": condition,
                    "response": f"response {len(rows) + 1} for {case['id']}",
                    "runner": "fixture-runner",
                    "model": "fixture-model",
                }
                if isinstance(source_profiles, dict):
                    row["case_sha256"] = MODULE._case_digest(case_data)
                    row["source_sha256"] = source_profiles[condition]["sha256"]
                rows.append(row)
        return rows

    def source_bound_case_data(self) -> dict[str, object]:
        case_data = deepcopy(self.case_data)
        candidate_path = "novelist/SKILL.md"
        digest = hashlib.sha256()
        digest.update(candidate_path.encode())
        digest.update(b"\0")
        digest.update((ROOT / candidate_path).read_bytes())
        digest.update(b"\0")
        case_data["source_profiles"] = {
            "baseline": {
                "id": "no-skill",
                "paths": [],
                "sha256": hashlib.sha256().hexdigest(),
            },
            "candidate": {
                "id": "novelist-current",
                "paths": [candidate_path],
                "sha256": digest.hexdigest(),
            },
        }
        case_data["release_gate"]["require_auditable_judgments"] = True
        return case_data

    def score_rows(self, key: dict[str, object]) -> list[dict[str, object]]:
        rows = []
        for pair in key["pairs"]:
            case = next(
                case for case in self.case_data["cases"] if case["id"] == pair["case_id"]
            )
            for label, condition in pair["labels"].items():
                score = 4 if condition == "baseline" else 5
                rows.append(
                    {
                        "pair_id": pair["pair_id"],
                        "label": label,
                        "correctness": 4,
                        "autonomy": score,
                        "actionability": score,
                        "safety": 4,
                        "concision": score,
                        "blocker": False,
                        "notes": "fixture",
                        "evaluation_id": "fixture-evaluation-1",
                        "judge": "fixture-independent-judge",
                        "judge_model": "fixture-judge-model",
                        "judged_at": "2026-08-15T00:00:00Z",
                        "criteria": [True] * len(case["criteria"]),
                        **(
                            {"blind_sha256": key["blind_sha256"]}
                            if "blind_sha256" in key
                            else {}
                        ),
                    }
                )
        return rows

    def test_source_bound_scores_require_auditable_independent_judgments(self) -> None:
        case_data = self.source_bound_case_data()
        blind_rows, key = MODULE.blind_responses(
            case_data, self.response_rows(case_data), seed=731
        )
        scores = self.score_rows(key)

        missing_provenance = deepcopy(scores)
        del missing_provenance[0]["evaluation_id"]
        with self.assertRaisesRegex(MODULE.ContractError, "evaluation_id"):
            MODULE.score_judgments(
                case_data, missing_provenance, key, blind_rows=blind_rows
            )

        same_runner = deepcopy(scores)
        for row in same_runner:
            row["judge"] = key["runner"]
        with self.assertRaisesRegex(MODULE.ContractError, "independent"):
            MODULE.score_judgments(case_data, same_runner, key, blind_rows=blind_rows)

        incomplete_criteria = deepcopy(scores)
        incomplete_criteria[0]["criteria"].pop()
        with self.assertRaisesRegex(MODULE.ContractError, "criteria"):
            MODULE.score_judgments(
                case_data, incomplete_criteria, key, blind_rows=blind_rows
            )

        failed_criterion = deepcopy(scores)
        candidate_label = next(
            label
            for label, condition in key["pairs"][0]["labels"].items()
            if condition == "candidate"
        )
        candidate_score = next(
            row
            for row in failed_criterion
            if row["pair_id"] == key["pairs"][0]["pair_id"]
            and row["label"] == candidate_label
        )
        candidate_score["criteria"][0] = False
        report = MODULE.score_judgments(
            case_data, failed_criterion, key, blind_rows=blind_rows
        )
        self.assertFalse(report["passed"])
        self.assertTrue(any("criterion" in reason for reason in report["reasons"]))

    def test_fixture_is_bounded_and_valid(self) -> None:
        self.assertGreaterEqual(len(self.case_data["cases"]), 5)
        self.assertLessEqual(len(self.case_data["cases"]), 8)
        self.assertAlmostEqual(sum(self.case_data["rubric"]["weights"].values()), 1.0)

    def test_committed_responses_are_bound_to_current_sources(self) -> None:
        fixture_dir = ROOT / "fixtures" / "skill-eval"
        response_files = sorted(fixture_dir.glob("*-responses.jsonl"))
        self.assertTrue(response_files)

        for response_path in response_files:
            prefix = response_path.name.removesuffix("-responses.jsonl")
            cases_path = fixture_dir / f"{prefix}-behavior-cases.json"
            with self.subTest(responses=response_path.name):
                self.assertTrue(cases_path.is_file())
                case_data = MODULE.load_json(cases_path)
                self.assertIn(
                    "source_profiles",
                    case_data,
                    f"{cases_path.name}: committed behavior evidence must bind its sources",
                )

    def test_blinding_hides_conditions_and_rejects_model_drift(self) -> None:
        tasks, key = MODULE.blind_responses(self.case_data, self.response_rows(), seed=731)

        serialized_tasks = json.dumps(tasks, ensure_ascii=False)
        self.assertNotIn("baseline", serialized_tasks)
        self.assertNotIn("candidate", serialized_tasks)
        self.assertEqual(len(tasks), len(self.case_data["cases"]))
        self.assertEqual({item["label"] for item in tasks[0]["responses"]}, {"A", "B"})
        self.assertEqual(len(key["pairs"]), len(tasks))

        drifted = self.response_rows()
        drifted[1]["model"] = "different-model"
        with self.assertRaises(MODULE.ContractError):
            MODULE.blind_responses(self.case_data, drifted, seed=731)

    def test_source_profiles_bind_responses_key_and_current_files(self) -> None:
        case_data = self.source_bound_case_data()
        rows = self.response_rows(case_data)

        stale_case_rows = deepcopy(rows)
        stale_case_rows[0]["case_sha256"] = "0" * 64
        with self.assertRaises(MODULE.ContractError):
            MODULE.blind_responses(case_data, stale_case_rows, seed=731)

        changed_cases = deepcopy(case_data)
        changed_cases["cases"][0]["prompt"] += " changed"
        with self.assertRaises(MODULE.ContractError):
            MODULE.blind_responses(changed_cases, rows, seed=731)

        stale_response = deepcopy(rows)
        stale_response[0]["source_sha256"] = "0" * 64
        with self.assertRaises(MODULE.ContractError):
            MODULE.blind_responses(case_data, stale_response, seed=731)

        blind_rows, key = MODULE.blind_responses(case_data, rows, seed=731)
        self.assertEqual(key["source_profiles"], case_data["source_profiles"])
        self.assertEqual(
            {row["blind_sha256"] for row in blind_rows},
            {key["blind_sha256"]},
        )

        stale_key = deepcopy(key)
        stale_key["source_profiles"]["candidate"]["sha256"] = "0" * 64
        with self.assertRaises(MODULE.ContractError):
            MODULE.score_judgments(
                case_data, self.score_rows(key), stale_key, blind_rows=blind_rows
            )

        stale_mapping = deepcopy(key)
        stale_mapping["pairs"][0]["labels"] = {
            "A": key["pairs"][0]["labels"]["B"],
            "B": key["pairs"][0]["labels"]["A"],
        }
        with self.assertRaises(MODULE.ContractError):
            MODULE.score_judgments(
                case_data, self.score_rows(key), stale_mapping, blind_rows=blind_rows
            )

        changed_rows = deepcopy(rows)
        changed_rows[0]["response"] += " changed"
        changed_blind_rows, changed_key = MODULE.blind_responses(
            case_data, changed_rows, seed=731
        )
        with self.assertRaises(MODULE.ContractError):
            MODULE.score_judgments(
                case_data,
                self.score_rows(key),
                changed_key,
                blind_rows=changed_blind_rows,
            )

        stale_blind_rows = deepcopy(blind_rows)
        stale_blind_rows[0]["responses"][0]["text"] += " changed"
        with self.assertRaises(MODULE.ContractError):
            MODULE.score_judgments(
                case_data, self.score_rows(key), key, blind_rows=stale_blind_rows
            )

        stale_source = deepcopy(case_data)
        stale_source["source_profiles"]["candidate"]["sha256"] = "0" * 64
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_cases(stale_source)

    def test_source_profile_paths_cannot_escape_through_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
            root = Path(root_dir)
            outside = Path(outside_dir) / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            (root / "escape.md").symlink_to(outside)
            with patch.object(MODULE, "ROOT", root):
                with self.assertRaises(MODULE.ContractError):
                    MODULE.source_set_digest(["escape.md"])

    def test_release_gate_blocks_findings_and_material_regressions(self) -> None:
        _, key = MODULE.blind_responses(self.case_data, self.response_rows(), seed=731)
        scores = self.score_rows(key)

        passing = MODULE.score_judgments(self.case_data, scores, key)
        self.assertTrue(passing["passed"])

        truncated_key = deepcopy(key)
        removed_pair_id = truncated_key["pairs"].pop()["pair_id"]
        truncated_scores = [row for row in scores if row["pair_id"] != removed_pair_id]
        with self.assertRaises(MODULE.ContractError):
            MODULE.score_judgments(self.case_data, truncated_scores, truncated_key)

        blocked = deepcopy(scores)
        candidate_label = next(
            label
            for label, condition in key["pairs"][0]["labels"].items()
            if condition == "candidate"
        )
        candidate_score = next(
            row
            for row in blocked
            if row["pair_id"] == key["pairs"][0]["pair_id"]
            and row["label"] == candidate_label
        )
        candidate_score["blocker"] = True
        self.assertFalse(MODULE.score_judgments(self.case_data, blocked, key)["passed"])

        regressed = deepcopy(scores)
        candidate_score = next(
            row
            for row in regressed
            if row["pair_id"] == key["pairs"][0]["pair_id"]
            and row["label"] == candidate_label
        )
        candidate_score["correctness"] = 3
        report = MODULE.score_judgments(self.case_data, regressed, key)
        self.assertFalse(report["passed"])
        self.assertTrue(any("correctness" in reason for reason in report["reasons"]))

    def test_non_regression_gate_allows_ties_and_rejects_regressions(self) -> None:
        case_data = deepcopy(self.case_data)
        case_data["release_gate"]["mode"] = "non_regression"
        case_data["release_gate"]["candidate_weighted_score_must_improve"] = False
        MODULE.validate_cases(case_data)

        invalid_mode = deepcopy(case_data)
        invalid_mode["release_gate"]["mode"] = "preserve"
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_cases(invalid_mode)

        _, key = MODULE.blind_responses(case_data, self.response_rows(), seed=731)
        equal_scores = self.score_rows(key)
        for row in equal_scores:
            for dimension in MODULE.DIMENSIONS:
                row[dimension] = 4
        self.assertTrue(MODULE.score_judgments(case_data, equal_scores, key)["passed"])

        regressed = deepcopy(equal_scores)
        candidate_label = next(
            label
            for label, condition in key["pairs"][0]["labels"].items()
            if condition == "candidate"
        )
        candidate_score = next(
            row
            for row in regressed
            if row["pair_id"] == key["pairs"][0]["pair_id"]
            and row["label"] == candidate_label
        )
        candidate_score["actionability"] = 3
        report = MODULE.score_judgments(case_data, regressed, key)
        self.assertFalse(report["passed"])
        self.assertTrue(any("weighted_score regressed" in reason for reason in report["reasons"]))

    def test_high_risk_concision_variance_does_not_override_aggregate_improvement(self) -> None:
        _, key = MODULE.blind_responses(self.case_data, self.response_rows(), seed=731)
        scores = self.score_rows(key)
        pair = next(
            pair
            for pair in key["pairs"]
            if next(
                case for case in self.case_data["cases"] if case["id"] == pair["case_id"]
            )["risk"]
            == "high"
        )
        for row in scores:
            if row["pair_id"] != pair["pair_id"]:
                continue
            for dimension in MODULE.DIMENSIONS:
                row[dimension] = 5
            if pair["labels"][row["label"]] == "candidate":
                row["concision"] = 4

        report = MODULE.score_judgments(self.case_data, scores, key)
        self.assertTrue(report["passed"], report["reasons"])


if __name__ == "__main__":
    unittest.main()
