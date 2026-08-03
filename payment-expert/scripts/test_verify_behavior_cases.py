#!/usr/bin/env python3
"""Regression tests for the payment public-core behavior contract."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAYMENT_SCRIPT = Path(__file__).with_name("verify_behavior_cases.py")
EVALUATOR_SCRIPT = ROOT / "scripts" / "evaluate-skill-behavior.py"
CASES_FILE = ROOT / "payment-expert" / "fixtures" / "public-core-behavior-cases.json"
HISTORICAL_CASES_FILE = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "payment-expert-public-sources"
    / "eval"
    / "behavior-cases.json"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


PAYMENT = load_module("verify_payment_behavior_cases", PAYMENT_SCRIPT)
EVALUATOR = load_module("evaluate_payment_skill_behavior", EVALUATOR_SCRIPT)


class PublicCoreBehaviorContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(CASES_FILE.read_text(encoding="utf-8"))

    def test_rejects_prompt_and_criteria_drift(self) -> None:
        changed = deepcopy(self.data)
        changed["cases"][0]["prompt"] = "x"
        changed["cases"][0]["criteria"] = ["x"]

        self.assertTrue(PAYMENT.audit_public_core_cases(changed))

    def test_rejects_provenance_swap(self) -> None:
        changed = deepcopy(self.data)
        changed["cases"][0]["provenance"], changed["cases"][8]["provenance"] = (
            changed["cases"][8]["provenance"],
            changed["cases"][0]["provenance"],
        )

        self.assertTrue(PAYMENT.audit_public_core_cases(changed))

    def test_materializes_evaluator_valid_batches(self) -> None:
        batches = PAYMENT.build_public_core_eval_batches(self.data)

        self.assertEqual(set(batches), {"candidate-comparison", "post-merge-forward"})
        self.assertEqual({case["id"] for batch in batches.values() for case in batch["cases"]}, {
            case["id"] for case in self.data["cases"]
        })
        for batch in batches.values():
            EVALUATOR.validate_cases(batch)

    def test_candidate_comparison_matches_frozen_history(self) -> None:
        historical = json.loads(HISTORICAL_CASES_FILE.read_text(encoding="utf-8"))
        fields = ("id", "category", "risk", "prompt", "criteria")
        current_cases = [
            {field: case[field] for field in fields}
            for case in self.data["cases"]
            if case["provenance"] == "candidate-comparison"
        ]
        historical_cases = [
            {field: case[field] for field in fields} for case in historical["cases"]
        ]

        self.assertEqual(current_cases, historical_cases)


if __name__ == "__main__":
    unittest.main()
