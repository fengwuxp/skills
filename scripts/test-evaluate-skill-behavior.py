#!/usr/bin/env python3
"""Behavior tests for the offline Skill baseline/candidate evaluator."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


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

    def response_rows(self) -> list[dict[str, object]]:
        rows = []
        for case in self.case_data["cases"]:
            for condition in ("baseline", "candidate"):
                rows.append(
                    {
                        "case_id": case["id"],
                        "trial": 1,
                        "condition": condition,
                        "response": f"response {len(rows) + 1} for {case['id']}",
                        "runner": "fixture-runner",
                        "model": "fixture-model",
                    }
                )
        return rows

    def score_rows(self, key: dict[str, object]) -> list[dict[str, object]]:
        rows = []
        for pair in key["pairs"]:
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
                    }
                )
        return rows

    def test_fixture_is_bounded_and_valid(self) -> None:
        self.assertGreaterEqual(len(self.case_data["cases"]), 5)
        self.assertLessEqual(len(self.case_data["cases"]), 8)
        self.assertAlmostEqual(sum(self.case_data["rubric"]["weights"].values()), 1.0)

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


if __name__ == "__main__":
    unittest.main()
