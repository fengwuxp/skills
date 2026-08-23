#!/usr/bin/env python3
"""Behavior tests for the manual-first Skill evolution control plane."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill-evolution-control.py"
SPEC = importlib.util.spec_from_file_location("skill_evolution_control", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


BASELINE = """# Demo skill

## 质量红线
- 不得编造事实

## 运行规则
- 先核对输入
"""

CANDIDATE = """# Demo skill

## 质量红线
- 不得编造事实

## 运行规则
- 先核对输入
- 再验证输出
"""


def policy() -> dict[str, object]:
    return {
        "skill_id": "demo-skill",
        "frozen_sections": ["## 质量红线"],
        "editable_sections": ["## 运行规则"],
        "max_changed_lines": 2,
        "first_round_human_approval": True,
    }


def canary_evidence(
    registry: dict[str, object],
    version_id: str,
    experiment_id: str = "experiment:demo-001",
    primary_lower_bound_delta: float = 0.01,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": "COMPLETED",
        "experiment_id": experiment_id,
        "skill_id": "demo-skill",
        "control_version_id": registry["current_version"],
        "candidate_version_id": version_id,
        "primary_metric": "task_success_rate",
        "primary_lower_bound_delta": primary_lower_bound_delta,
        "guardrails_pass": True,
        "sample_ratio_ok": True,
        "attribution_complete": True,
        "data_fresh": True,
        "rules_hash": "rules:demo-001",
        "config_hash": "config:demo-001",
        "evidence_ref": f"{experiment_id}:completed",
    }


class SkillEvolutionControlTests(unittest.TestCase):
    def test_cli_exposes_independent_checker_evidence_command(self) -> None:
        args = MODULE._parser().parse_args(
            [
                "record-checker",
                "--registry",
                "/tmp/registry.json",
                "--version-id",
                "a" * 64,
                "--passed",
                "--checker-id",
                "independent-checker",
                "--evidence-ref",
                "validation:checker-001:passed",
            ]
        )
        self.assertEqual(args.command, "record-checker")

        canary_args = MODULE._parser().parse_args(
            [
                "record-canary",
                "--registry",
                "/tmp/registry.json",
                "--version-id",
                "a" * 64,
                "--evidence",
                "/tmp/experiment.json",
            ]
        )
        self.assertEqual(canary_args.evidence, Path("/tmp/experiment.json"))

    def test_candidate_must_change_only_registered_editable_sections(self) -> None:
        candidate = MODULE.check_candidate(policy(), BASELINE, CANDIDATE)
        self.assertEqual(candidate["state"], "CHECKED")
        self.assertEqual(candidate["diff_lines"], 1)
        self.assertEqual(candidate["skill_id"], "demo-skill")

        changed_redline = CANDIDATE.replace("- 不得编造事实", "- 可以编造事实")
        with self.assertRaisesRegex(MODULE.GateError, "frozen section"):
            MODULE.check_candidate(policy(), BASELINE, changed_redline)

    def test_promotion_requires_manual_approval_and_positive_canary(self) -> None:
        candidate = MODULE.check_candidate(policy(), BASELINE, CANDIDATE)
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry = MODULE.new_registry("demo-skill", BASELINE)
            MODULE.add_candidate(registry, candidate, CANDIDATE, Path(tmp_dir))

            with self.assertRaisesRegex(MODULE.StateError, "human approval"):
                MODULE.promote_candidate(
                    registry, candidate["version_id"], "automation", registry["current_version"]
                )

            MODULE.approve_candidate(registry, candidate["version_id"], "skill-owner")
            with self.assertRaisesRegex(MODULE.StateError, "checker"):
                MODULE.record_canary(registry, candidate["version_id"], canary_evidence(registry, candidate["version_id"]))
            MODULE.record_checker(
                registry,
                candidate["version_id"],
                passed=True,
                checker_id="independent-checker",
                evidence_ref="validation:checker-001:passed",
            )
            with self.assertRaisesRegex(MODULE.StateError, "canary"):
                MODULE.promote_candidate(
                    registry, candidate["version_id"], "automation", registry["current_version"]
                )

            MODULE.record_canary(registry, candidate["version_id"], canary_evidence(registry, candidate["version_id"]))
            MODULE.promote_candidate(
                registry, candidate["version_id"], "automation", registry["current_version"]
            )
            self.assertEqual(registry["current_version"], candidate["version_id"])
            self.assertEqual(registry["last_known_good"], registry["baseline_version"])
            decision = registry["promotion_decisions"][-1]
            self.assertEqual(decision["experiment_id"], "experiment:demo-001")
            self.assertEqual(decision["config_hash"], "config:demo-001")
            self.assertEqual(len(decision["evidence_sha256"]), 64)

    def test_rollback_restores_last_known_good_without_deleting_artifacts(self) -> None:
        candidate = MODULE.check_candidate(policy(), BASELINE, CANDIDATE)
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifacts = Path(tmp_dir)
            registry = MODULE.new_registry("demo-skill", BASELINE)
            MODULE.add_candidate(registry, candidate, CANDIDATE, artifacts)
            MODULE.approve_candidate(registry, candidate["version_id"], "skill-owner")
            MODULE.record_checker(
                registry,
                candidate["version_id"],
                passed=True,
                checker_id="independent-checker",
                evidence_ref="validation:checker-002:passed",
            )
            MODULE.record_canary(registry, candidate["version_id"], canary_evidence(registry, candidate["version_id"], "experiment:demo-002"))
            MODULE.promote_candidate(
                registry, candidate["version_id"], "automation", registry["current_version"]
            )
            MODULE.enable_automation(registry, "skill-owner")
            artifact_path = Path(registry["candidates"][candidate["version_id"]]["artifact_path"])
            MODULE.rollback(registry, "guardrail breach", "on-call", registry["current_version"])

            self.assertEqual(registry["current_version"], registry["last_known_good"])
            self.assertTrue(artifact_path.is_file())
            self.assertEqual(registry["rollback_events"][-1]["reason"], "guardrail breach")
            self.assertFalse(registry["automation"]["enabled"])
            with self.assertRaisesRegex(MODULE.StateError, "paused"):
                MODULE.enable_automation(registry, "skill-owner")

    def test_automation_requires_a_completed_manual_round(self) -> None:
        candidate = MODULE.check_candidate(policy(), BASELINE, CANDIDATE)
        candidate_two_text = CANDIDATE.replace("- 再验证输出", "- 再验证输出\n- 记录证据")
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifacts = Path(tmp_dir)
            registry = MODULE.new_registry("demo-skill", BASELINE)
            with self.assertRaisesRegex(MODULE.StateError, "manual round"):
                MODULE.enable_automation(registry, "skill-owner")

            MODULE.add_candidate(registry, candidate, CANDIDATE, artifacts)
            MODULE.approve_candidate(registry, candidate["version_id"], "skill-owner")
            MODULE.record_checker(
                registry,
                candidate["version_id"],
                passed=True,
                checker_id="independent-checker",
                evidence_ref="validation:checker-003:passed",
            )
            MODULE.record_canary(registry, candidate["version_id"], canary_evidence(registry, candidate["version_id"], "experiment:demo-003"))
            MODULE.promote_candidate(
                registry, candidate["version_id"], "skill-owner", registry["current_version"]
            )
            MODULE.enable_automation(registry, "skill-owner")

            candidate_two = MODULE.check_candidate(policy(), CANDIDATE, candidate_two_text)
            MODULE.add_candidate(registry, candidate_two, candidate_two_text, artifacts)
            MODULE.record_checker(
                registry,
                candidate_two["version_id"],
                passed=True,
                checker_id="independent-checker",
                evidence_ref="validation:checker-004:passed",
            )
            MODULE.record_canary(registry, candidate_two["version_id"], canary_evidence(registry, candidate_two["version_id"], "experiment:demo-004", 0.02))
            MODULE.promote_candidate(
                registry, candidate_two["version_id"], "automation", registry["current_version"]
            )
            self.assertEqual(registry["current_version"], candidate_two["version_id"])

    def test_canary_requires_complete_experiment_evidence(self) -> None:
        candidate = MODULE.check_candidate(policy(), BASELINE, CANDIDATE)
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry = MODULE.new_registry("demo-skill", BASELINE)
            MODULE.add_candidate(registry, candidate, CANDIDATE, Path(tmp_dir))
            MODULE.approve_candidate(registry, candidate["version_id"], "skill-owner")
            MODULE.record_checker(
                registry,
                candidate["version_id"],
                passed=True,
                checker_id="independent-checker",
                evidence_ref="validation:checker-005:passed",
            )
            incomplete = canary_evidence(registry, candidate["version_id"])
            incomplete.pop("attribution_complete")
            with self.assertRaisesRegex(MODULE.StateError, "experiment evidence"):
                MODULE.record_canary(registry, candidate["version_id"], incomplete)

    def test_promotion_rejects_stale_current_pointer(self) -> None:
        candidate = MODULE.check_candidate(policy(), BASELINE, CANDIDATE)
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry = MODULE.new_registry("demo-skill", BASELINE)
            MODULE.add_candidate(registry, candidate, CANDIDATE, Path(tmp_dir))
            MODULE.approve_candidate(registry, candidate["version_id"], "skill-owner")
            MODULE.record_checker(
                registry,
                candidate["version_id"],
                passed=True,
                checker_id="independent-checker",
                evidence_ref="validation:checker-006:passed",
            )
            MODULE.record_canary(registry, candidate["version_id"], canary_evidence(registry, candidate["version_id"], "experiment:demo-006"))
            with self.assertRaisesRegex(MODULE.StateError, "current version changed"):
                MODULE.promote_candidate(registry, candidate["version_id"], "skill-owner", "stale-version")


if __name__ == "__main__":
    unittest.main()
