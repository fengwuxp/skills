#!/usr/bin/env python3
"""Regression tests for the payment public-core behavior contract."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAYMENT_SCRIPT = Path(__file__).with_name("verify_behavior_cases.py")
CASES_FILE = ROOT / "payment-expert" / "fixtures" / "public-core-behavior-cases.json"
METHOD_CASES_FILE = ROOT / "payment-expert" / "test-prompts.json"
HISTORICAL_CANDIDATE_COMPARISON_SHA256 = (
    "5a1f092b2a596bb6f9c53899f82475717f4b2d6633ef85f73cd6c5f760abd0d0"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


PAYMENT = load_module("verify_payment_behavior_cases", PAYMENT_SCRIPT)


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

    def test_candidate_comparison_matches_frozen_history(self) -> None:
        fields = ("id", "category", "risk", "prompt", "criteria")
        current_cases = [
            {field: case[field] for field in fields}
            for case in self.data["cases"]
            if case["provenance"] == "candidate-comparison"
        ]
        canonical = json.dumps(
            current_cases,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            HISTORICAL_CANDIDATE_COMPARISON_SHA256,
        )

    def test_limitations_do_not_claim_deleted_model_evidence(self) -> None:
        limitations = "\n".join(self.data["limitations"])

        self.assertIn("未保留在仓库内", limitations)
        self.assertNotIn("继续保存在仓库过程工件中", limitations)


class MethodBehaviorContractTests(unittest.TestCase):
    def test_rejects_missing_m10_acquiring_case(self) -> None:
        data = json.loads(METHOD_CASES_FILE.read_text(encoding="utf-8"))
        changed = [case for case in data if case["id"] != "PT-042"]

        self.assertIn(
            "missing M10 acquiring cases: PT-042",
            PAYMENT.audit_cases(changed),
        )

    def test_requires_sandbox_capability_negative(self) -> None:
        data = json.loads(METHOD_CASES_FILE.read_text(encoding="utf-8"))
        changed = [case for case in data if case["id"] != "PT-043"]

        self.assertIn(
            "missing M10 acquiring cases: PT-043",
            PAYMENT.audit_cases(changed),
        )

    def test_rejects_m10_hard_negative_contract_drift(self) -> None:
        data = json.loads(METHOD_CASES_FILE.read_text(encoding="utf-8"))
        changed = deepcopy(data)
        for case in changed:
            if case["id"] in {f"PT-{index:03d}" for index in range(37, 44)}:
                case["kind"] = "should_trigger"
                case["expected"]["decision"] = "answer"

        self.assertTrue(
            any(
                "M10 acquiring contract sha256 mismatch" in failure
                for failure in PAYMENT.audit_cases(changed)
            )
        )


if __name__ == "__main__":
    unittest.main()
