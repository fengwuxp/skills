#!/usr/bin/env python3
"""Offline regression tests for evidence, pattern revisions and version outcomes.

Inputs are synthetic fixtures. Writes stay in temporary directories; no network,
installed Skills, private learning data or Git operations are involved.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LEDGER = load_module("learning_ledger", ROOT / "wise-agent/scripts/skill-learning-ledger.py")
EVOLUTION = load_module("evolution_control", ROOT / "scripts/skill-evolution-control.py")
BASELINE = "# Demo\n\n## Safety\n- Preserve evidence\n\n## Rules\n- Read input\n"
CANDIDATE = BASELINE + "- Verify output\n"
POLICY = {
    "skill_id": "demo-skill",
    "frozen_sections": ["## Safety"],
    "editable_sections": ["## Rules"],
    "max_changed_lines": 2,
    "first_round_human_approval": True,
}


class LearningLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "learning" / "wise-agent"
        self.pattern = {
            "status": "active",
            "summary": "Output checks are omitted.",
            "scope": "Explicit Skill maintenance tasks.",
            "strategies": ["Check output against the task contract."],
            "counterexamples": [],
            "record_refs": [],
            "evidence_refs": ["fixture:missing-output-check"],
            "reason": "Owner reviewed a reproducible fixture failure.",
        }
        self.registry = EVOLUTION.new_registry("demo-skill", BASELINE)
        self.manifest = EVOLUTION.check_candidate(POLICY, BASELINE, CANDIDATE)
        self.version = self.manifest["version_id"]

    def revise(self, **changes):
        return LEDGER.revise_pattern(
            self.home, "demo-skill", "output-check", {**self.pattern, **changes},
            "skill-owner", "public-safe",
        )

    def register(self) -> None:
        EVOLUTION.add_candidate(
            self.registry, self.manifest, CANDIDATE, self.base / "artifacts", "output-check"
        )

    def import_impact(self) -> int:
        return LEDGER.record_impact(
            self.home, "demo-skill", "output-check", self.registry, self.version,
            "skill-owner", "public-safe",
        )

    def lookup(self):
        return LEDGER.lookup_patterns(self.home, "demo-skill", "output-check")["patterns"][0]

    def canary(self, delta: float) -> None:
        EVOLUTION.approve_candidate(self.registry, self.version, "skill-owner")
        EVOLUTION.record_checker(self.registry, self.version, True, "checker", "fixture:checker-pass")
        EVOLUTION.record_canary(self.registry, self.version, {
            "schema_version": 1, "status": "COMPLETED", "experiment_id": "fixture:experiment",
            "skill_id": "demo-skill", "control_version_id": self.registry["current_version"],
            "candidate_version_id": self.version, "primary_metric": "task_success_rate",
            "primary_lower_bound_delta": delta, "guardrails_pass": True,
            "sample_ratio_ok": True, "attribution_complete": True, "data_fresh": True,
            "rules_hash": "fixture:rules", "config_hash": "fixture:config",
            "evidence_ref": "fixture:canary",
        })

    def test_rejection_keeps_observation_and_pattern(self) -> None:
        with redirect_stdout(io.StringIO()):
            LEDGER.enable(self.home)
            record = LEDGER.write_candidate(self.home, argparse.Namespace(
                skill="demo-skill", slug="output-check", evidence_kind="validator-failure",
                task_ref="fixture:current-task", observed_failure="Output was not checked.",
                expected_behavior="Verify the output.", evidence_ref=["fixture:failure"],
                reuse_scope="Output-producing tasks", proposed_authority="demo-skill/SKILL.md",
                validation="Run the output fixture.", sensitivity_check="public-safe",
            ))
        original = record.read_bytes()
        self.revise(record_refs=[str(record.relative_to(self.home))])
        self.register()
        EVOLUTION.reject_candidate(
            self.registry, self.version, "Too broad for the observed failure.",
            "skill-owner", "review:rejected-001",
        )
        self.assertEqual(self.import_impact(), 1)
        knowledge = self.lookup()
        self.assertEqual(knowledge["current"]["status"], "active")
        self.assertEqual(knowledge["impacts"][0]["outcome"], "REJECTED")
        self.assertEqual(knowledge["impacts"][0]["version_id"], self.version)
        self.assertEqual(record.read_bytes(), original)
        self.assertIn(str(record.relative_to(self.home)), knowledge["current"]["record_digests"])

    def test_new_evidence_revises_or_retracts_without_erasing_history(self) -> None:
        first = self.revise()
        original = first.read_bytes()
        self.revise(status="retracted", summary="The failure was in the fixture, not the Skill.",
                    counterexamples=["A valid response failed the broken fixture."],
                    evidence_refs=["fixture:corrected-checker"], reason="The root cause was disproved.")
        knowledge = self.lookup()
        self.assertEqual(knowledge["current"]["status"], "retracted")
        self.assertEqual(len(knowledge["revisions"]), 2)
        self.assertEqual(first.read_bytes(), original)
        self.assertNotIn("fixture:missing-output-check", knowledge["current"]["evidence_refs"])

    def test_failed_trial_remains_queryable_and_import_is_idempotent(self) -> None:
        self.revise()
        self.register()
        self.canary(-0.02)
        self.assertEqual(self.import_impact(), 2)
        self.assertEqual(self.import_impact(), 0)
        EVOLUTION.reject_candidate(self.registry, self.version, "No improvement.", "owner", "review:no-gain")
        self.assertEqual(self.import_impact(), 1)
        self.assertEqual([event["outcome"] for event in self.lookup()["impacts"]],
                         ["CHECKER_PASSED", "CANARY_FAILED", "REJECTED"])

    def test_rollback_keeps_knowledge_and_all_version_outcomes(self) -> None:
        revision = self.revise()
        original = revision.read_bytes()
        baseline_version = self.registry["current_version"]
        self.register()
        self.canary(0.02)
        EVOLUTION.promote_candidate(self.registry, self.version, "owner", baseline_version)
        self.assertEqual(self.import_impact(), 3)
        registry_path = self.base / "registry.json"
        registry_path.write_text(json.dumps(self.registry), encoding="utf-8")
        original_registry = registry_path.read_bytes()
        command = [
            "rollback", "--registry", str(registry_path),
            "--reason", "Observed guardrail breach.", "--actor", "owner",
        ]
        for expected_version, error in (
            (None, "--expected-current-version"),
            (baseline_version, "rollback compare-and-set failed"),
            (self.version, None),
        ):
            with self.subTest(expected_version=expected_version):
                arguments = [] if expected_version is None else ["--expected-current-version", expected_version]
                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    try:
                        exit_code = EVOLUTION.main(command + arguments)
                    except SystemExit as exc:
                        exit_code = exc.code
                self.assertEqual(exit_code, 2 if error else 0, stderr.getvalue())
                if error:
                    self.assertIn(error, stderr.getvalue())
                    self.assertEqual(registry_path.read_bytes(), original_registry)
        self.registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(self.import_impact(), 1)
        self.assertEqual(self.registry["current_version"], baseline_version)
        self.assertEqual(revision.read_bytes(), original)
        self.assertEqual([event["outcome"] for event in self.lookup()["impacts"]],
                         ["CHECKER_PASSED", "CANARY_PASSED", "PROMOTED", "ROLLED_BACK"])
        self.assertTrue(Path(self.registry["candidates"][self.version]["artifact_path"]).is_file())

    def test_reregistration_cannot_reset_decisions_or_rebind_pattern(self) -> None:
        self.register()
        EVOLUTION.record_checker(self.registry, self.version, False, "checker", "fixture:checker-fail")
        previous = json.dumps(self.registry, sort_keys=True)
        self.register()
        self.assertEqual(json.dumps(self.registry, sort_keys=True), previous)
        with self.assertRaisesRegex(EVOLUTION.StateError, "already registered"):
            EVOLUTION.add_candidate(self.registry, self.manifest, CANDIDATE,
                                    self.base / "artifacts", "different-pattern")

    def test_same_second_results_keep_sequence_not_timestamp_deduplication(self) -> None:
        self.revise()
        self.register()
        with patch.object(EVOLUTION, "_now", return_value="2026-09-09T00:00:00+00:00"):
            EVOLUTION.record_checker(self.registry, self.version, True, "checker", "fixture:check")
            EVOLUTION.record_checker(self.registry, self.version, True, "checker", "fixture:check")
        self.assertEqual(self.import_impact(), 2)
        self.assertEqual([event["sequence"] for event in self.lookup()["impacts"]], [1, 2])

    def test_reregistration_does_not_claim_missing_artifact_is_intact(self) -> None:
        self.register()
        Path(self.registry["candidates"][self.version]["artifact_path"]).unlink()
        with self.assertRaisesRegex(EVOLUTION.StateError, "artifact"):
            self.register()

    def test_malformed_review_status_and_outcome_are_validation_errors(self) -> None:
        with self.assertRaises(ValueError):
            self.revise(status=[])
        self.revise()
        self.register()
        EVOLUTION.record_checker(self.registry, self.version, False, "checker", "fixture:fail")
        self.registry["candidates"][self.version]["outcomes"][0]["outcome"] = []
        with self.assertRaises(ValueError):
            self.import_impact()

    def test_failed_snapshot_write_does_not_publish_partial_revision(self) -> None:
        first = self.revise()
        with patch.object(LEDGER, "write_all", side_effect=OSError("fixture:disk-full")):
            with self.assertRaises(OSError):
                self.revise(reason="New evidence.")
        self.assertEqual(list(first.parent.iterdir()), [first])
        self.assertEqual(len(self.lookup()["revisions"]), 1)

    def test_import_cannot_rewrite_an_existing_outcome(self) -> None:
        self.revise()
        self.register()
        EVOLUTION.record_checker(self.registry, self.version, False, "checker", "fixture:failed")
        self.import_impact()
        self.registry["candidates"][self.version]["outcomes"][0]["evidence_ref"] = "fixture:rewritten"
        with self.assertRaisesRegex(ValueError, "immutable outcome"):
            self.import_impact()
        self.assertEqual(self.lookup()["impacts"][0]["evidence_ref"], "fixture:failed")

    def test_second_intervention_reuses_pattern_and_preserves_first_rejection(self) -> None:
        self.revise()
        self.register()
        rejected_version = self.version
        EVOLUTION.reject_candidate(self.registry, self.version, "Too broad.", "owner", "review:too-broad")
        self.import_impact()
        self.revise(strategies=["Check only output obligations in the explicit task contract."],
                    counterexamples=["Mandatory full validation for a prose-only task adds no value."],
                    evidence_refs=["review:too-broad"], reason="Narrow the intervention, retain the problem.")
        second = CANDIDATE.replace("Verify output", "Verify the explicit output contract")
        manifest = EVOLUTION.check_candidate(POLICY, BASELINE, second)
        self.version = manifest["version_id"]
        EVOLUTION.add_candidate(self.registry, manifest, second, self.base / "artifacts", "output-check")
        self.canary(0.02)
        EVOLUTION.promote_candidate(self.registry, self.version, "owner", self.registry["current_version"])
        self.import_impact()
        EVOLUTION.rollback(self.registry, "A later guardrail failed.", "owner", self.version)
        self.import_impact()
        knowledge = self.lookup()
        self.assertEqual(knowledge["current"]["revision"], 2)
        self.assertEqual(knowledge["current"]["status"], "active")
        self.assertEqual(len(knowledge["impacts"]), 5)
        self.assertTrue(any(event["version_id"] == rejected_version and event["outcome"] == "REJECTED"
                            for event in knowledge["impacts"]))
        self.assertTrue(all(Path(event["artifact_ref"]).is_file() for event in knowledge["impacts"]))

    def test_manual_review_does_not_change_candidate_write_grant(self) -> None:
        self.revise()
        self.assertFalse((self.home / "mode.json").exists())
        with redirect_stdout(io.StringIO()):
            LEDGER.enable(self.home)
            LEDGER.disable(self.home)
        mode = (self.home / "mode.json").read_bytes()
        self.revise(reason="Separately authorized review while automatic recording is disabled.")
        self.assertEqual((self.home / "mode.json").read_bytes(), mode)
        with self.assertRaises(ValueError):
            LEDGER.revise_pattern(self.home, "demo-skill", "output-check", self.pattern, "", "public-safe")

    def test_lookup_is_skill_scoped_and_does_not_create_or_chmod_files(self) -> None:
        empty = LEDGER.lookup_patterns(self.home, "demo-skill")
        self.assertEqual(empty["patterns"], [])
        self.assertFalse(self.home.exists())
        revision = self.revise()
        revision.chmod(0o640)
        (self.home / "patterns" / "unrelated-skill").symlink_to(self.base / "not-readable")
        self.assertEqual(len(LEDGER.lookup_patterns(self.home, "demo-skill")["patterns"]), 1)
        self.assertEqual(revision.stat().st_mode & 0o777, 0o640)
        with self.assertRaises(ValueError):
            LEDGER.lookup_patterns(self.home, "../other")

    def test_pattern_directories_and_files_reject_links(self) -> None:
        self.home.mkdir(parents=True)
        outside = self.base / "outside"
        outside.mkdir()
        (self.home / "patterns").symlink_to(outside)
        with self.assertRaises(ValueError):
            self.revise()
        self.assertEqual(list(outside.iterdir()), [])
        (self.home / "patterns").unlink()
        revision = self.revise()
        os.link(revision, outside / "linked.json")
        with self.assertRaises(ValueError):
            self.lookup()

    def test_record_references_cannot_escape_or_cross_skills(self) -> None:
        for reference in ("../private.md", "records/other-skill/0001-test.md", "records/demo-skill/missing.md"):
            with self.subTest(reference=reference), self.assertRaises((ValueError, OSError)):
                self.revise(record_refs=[reference])
        self.assertFalse((self.home / "patterns").exists())

    def test_import_checks_skill_pattern_and_sensitive_material_before_writing(self) -> None:
        self.revise()
        self.register()
        EVOLUTION.record_checker(self.registry, self.version, False, "checker", "fixture:fail")
        candidate = self.registry["candidates"][self.version]
        candidate["pattern_id"] = "wrong-pattern"
        with self.assertRaises(ValueError):
            self.import_impact()
        candidate["pattern_id"] = "output-check"
        self.registry["skill_id"] = "other-skill"
        with self.assertRaises(ValueError):
            self.import_impact()
        self.registry["skill_id"] = "demo-skill"
        candidate["outcomes"][0]["reason"] = "password=do-not-store"
        with self.assertRaisesRegex(ValueError, "sensitive"):
            self.import_impact()
        self.assertEqual(self.lookup()["impacts"], [])

    def test_cli_supports_explicit_review_and_scoped_lookup(self) -> None:
        source = self.base / "review.json"
        source.write_text(json.dumps(self.pattern), encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(LEDGER.main([
                "--home", str(self.home.parent), "revise-pattern", "--skill", "demo-skill",
                "--pattern-id", "output-check", "--input", str(source), "--reviewer", "owner",
                "--sensitivity-check", "public-safe",
            ]), 0)
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(LEDGER.main(["--home", str(self.home.parent), "lookup", "--skill", "demo-skill"]), 0)
        self.assertEqual(len(json.loads(output.getvalue())["patterns"]), 1)
        self.register()
        registry_path = self.base / "registry.json"
        registry_path.write_text(json.dumps(self.registry), encoding="utf-8")
        self.assertEqual(EVOLUTION.main([
            "reject", "--registry", str(registry_path), "--version-id", self.version,
            "--reason", "Rejected in explicit review.", "--actor", "owner", "--evidence-ref", "review:cli",
        ]), 0)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(LEDGER.main([
                "--home", str(self.home.parent), "record-impact", "--skill", "demo-skill",
                "--pattern-id", "output-check", "--registry", str(registry_path),
                "--version-id", self.version, "--reviewer", "owner", "--sensitivity-check", "public-safe",
            ]), 0)
        self.assertEqual(self.lookup()["impacts"][0]["outcome"], "REJECTED")


if __name__ == "__main__":
    unittest.main()
