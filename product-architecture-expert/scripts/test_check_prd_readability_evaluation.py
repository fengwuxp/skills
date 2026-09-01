#!/usr/bin/env python3
"""Tests for the PRD readability evaluation contract checker."""

from __future__ import annotations

import importlib.util
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_prd_readability_evaluation.py")
SPEC = importlib.util.spec_from_file_location("check_prd_readability_evaluation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "product-architecture-expert" / "fixtures" / "prd-readability-evaluation.json"
REPORT = ROOT / "fixtures" / "skill-eval" / "product-prd-readability-r1-report.json"
RESPONSES = ROOT / "fixtures" / "skill-eval" / "product-prd-readability-r1-reader-evidence.jsonl"


class PrdReadabilityEvaluationTests(unittest.TestCase):
    def test_repository_contract_is_valid_and_complete(self) -> None:
        contract = MODULE.load_contract(CONTRACT)

        MODULE.validate_contract(contract, ROOT)

        self.assertEqual(15, len(contract["tasks"]))
        self.assertEqual(
            {"business", "product", "engineering", "testing", "operations"},
            {task["role"] for task in contract["tasks"]},
        )

    def test_prepare_freezes_fifteen_unique_tasks(self) -> None:
        contract = MODULE.load_contract(CONTRACT)

        rows = MODULE.prepare_tasks(contract, ROOT)

        self.assertEqual(15, len(rows))
        self.assertEqual(15, len({row["task_id"] for row in rows}))
        self.assertTrue(all(len(row["source_sha256"]) == 64 for row in rows))

    def test_duplicate_sample_role_pair_is_rejected(self) -> None:
        contract = MODULE.load_contract(CONTRACT)
        contract["tasks"][1]["sample_id"] = contract["tasks"][0]["sample_id"]
        contract["tasks"][1]["role"] = contract["tasks"][0]["role"]

        with self.assertRaisesRegex(MODULE.ContractError, "duplicate sample/role"):
            MODULE.validate_contract(contract, ROOT)

    def test_stale_source_digest_is_rejected(self) -> None:
        contract = MODULE.load_contract(CONTRACT)
        contract["source_profile"]["sha256"] = "0" * 64

        with self.assertRaisesRegex(MODULE.ContractError, "source set changed"):
            MODULE.validate_contract(contract, ROOT)

    def test_prepare_writes_only_explicit_output(self) -> None:
        contract = MODULE.load_contract(CONTRACT)
        rows = MODULE.prepare_tasks(contract, ROOT)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "tasks.jsonl"

            MODULE.write_jsonl(output, rows)

            written = [json.loads(line) for line in output.read_text().splitlines()]
            self.assertEqual(rows, written)

    def test_repository_report_matches_contract_and_passes(self) -> None:
        contract = MODULE.load_contract(CONTRACT)
        responses = MODULE.validate_response_file(contract, RESPONSES)
        report = MODULE.validate_report_file(contract, REPORT)

        self.assertEqual(15, len(responses))
        self.assertTrue(report["passed"])

    def test_tampered_report_total_is_rejected(self) -> None:
        contract = MODULE.load_contract(CONTRACT)
        report = copy.deepcopy(MODULE.load_contract(REPORT))
        report["samples"][0]["total"] += 1

        with self.assertRaisesRegex(MODULE.ContractError, "score totals changed"):
            MODULE.validate_report(contract, report)

    def test_tampered_response_identity_is_rejected(self) -> None:
        contract = MODULE.load_contract(CONTRACT)
        report = copy.deepcopy(MODULE.load_contract(REPORT))
        report["response_sha256"] = "0" * 64

        with self.assertRaisesRegex(MODULE.ContractError, "report evidence identity changed"):
            MODULE.validate_report(contract, report)

    def test_non_numeric_report_total_is_rejected(self) -> None:
        contract = MODULE.load_contract(CONTRACT)
        report = copy.deepcopy(MODULE.load_contract(REPORT))
        report["samples"][0]["total"] = "nan"

        with self.assertRaisesRegex(MODULE.ContractError, "report score totals are invalid"):
            MODULE.validate_report(contract, report)


if __name__ == "__main__":
    unittest.main()
