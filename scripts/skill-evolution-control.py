#!/usr/bin/env python3
"""Manual-first, local-only control plane for Skill candidate promotion.

The tool never calls a model, accesses the network, or edits a source Skill.
It stores immutable candidate artifacts and an explicit runtime pointer in a
caller-provided registry file. Production integration must provide the
business experiment and metric evidence consumed by ``record-canary``.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GateError(ValueError):
    """Raised when a candidate violates a Skill evolution policy."""


class StateError(ValueError):
    """Raised when a registry transition is not allowed."""


SECTION_PATTERN = re.compile(r"^##\s+.+$")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _non_empty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sections(text: str) -> dict[str, tuple[str, ...]]:
    sections: dict[str, list[str]] = {"<preamble>": []}
    current = "<preamble>"
    for line in text.splitlines():
        if SECTION_PATTERN.fullmatch(line):
            current = line.strip()
            sections.setdefault(current, [])
        else:
            sections[current].append(line)
    return {name: tuple(lines) for name, lines in sections.items()}


def _changed_line_count(baseline: str, candidate: str) -> int:
    old = baseline.splitlines()
    new = candidate.splitlines()
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    return sum((i2 - i1) + (j2 - j1) for tag, i1, i2, j1, j2 in matcher.get_opcodes() if tag != "equal")


def _validate_policy(policy: dict[str, Any]) -> None:
    _non_empty(policy.get("skill_id"), "policy.skill_id")
    for field in ("frozen_sections", "editable_sections"):
        values = policy.get(field)
        if not isinstance(values, list) or not values or any(not isinstance(item, str) for item in values):
            raise ValueError(f"policy.{field} must be a non-empty string list")
        if len(values) != len(set(values)):
            raise ValueError(f"policy.{field} contains duplicates")
    if set(policy["frozen_sections"]) & set(policy["editable_sections"]):
        raise ValueError("frozen and editable sections must not overlap")
    budget = policy.get("max_changed_lines")
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 1:
        raise ValueError("policy.max_changed_lines must be a positive integer")
    if policy.get("first_round_human_approval") is not True:
        raise ValueError("first_round_human_approval must be true")


def check_candidate(policy: dict[str, Any], baseline: str, candidate: str) -> dict[str, Any]:
    """Validate a bounded candidate and return an auditable manifest."""

    _validate_policy(policy)
    if not isinstance(baseline, str) or not isinstance(candidate, str):
        raise GateError("baseline and candidate must be text")
    if baseline == candidate:
        raise GateError("candidate has no changes")

    baseline_sections = _sections(baseline)
    candidate_sections = _sections(candidate)
    for section in policy["frozen_sections"]:
        if section not in baseline_sections or section not in candidate_sections:
            raise GateError(f"frozen section missing: {section}")
        if baseline_sections[section] != candidate_sections[section]:
            raise GateError(f"frozen section changed: {section}")

    all_sections = set(baseline_sections) | set(candidate_sections)
    changed_sections = {
        section
        for section in all_sections
        if baseline_sections.get(section) != candidate_sections.get(section)
    }
    allowed = set(policy["editable_sections"])
    disallowed = changed_sections - allowed
    if disallowed:
        raise GateError("changed section is not editable: " + ", ".join(sorted(disallowed)))

    diff_lines = _changed_line_count(baseline, candidate)
    if diff_lines > policy["max_changed_lines"]:
        raise GateError(
            f"candidate changes {diff_lines} lines, limit is {policy['max_changed_lines']}"
        )

    version_id = _sha256(candidate)
    return {
        "schema_version": 1,
        "skill_id": policy["skill_id"],
        "version_id": version_id,
        "parent_version_id": _sha256(baseline),
        "content_sha256": version_id,
        "policy_sha256": _sha256(json.dumps(policy, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
        "frozen_section_hashes": {
            section: _sha256("\n".join(baseline_sections[section]))
            for section in policy["frozen_sections"]
        },
        "diff_lines": diff_lines,
        "state": "CHECKED",
        "created_at": _now(),
    }


def new_registry(skill_id: str, baseline: str) -> dict[str, Any]:
    skill_id = _non_empty(skill_id, "skill_id")
    baseline_version = _sha256(baseline)
    return {
        "schema_version": 1,
        "skill_id": skill_id,
        "baseline_version": baseline_version,
        "current_version": baseline_version,
        "last_known_good": baseline_version,
        "automation": {
            "enabled": False,
            "first_round_completed": False,
            "enabled_by": None,
        },
        "versions": {
            baseline_version: {
                "version_id": baseline_version,
                "kind": "baseline",
                "content_sha256": baseline_version,
            }
        },
        "candidates": {},
        "promotion_decisions": [],
        "rollback_events": [],
    }


def _candidate(registry: dict[str, Any], version_id: str) -> dict[str, Any]:
    try:
        value = registry["candidates"][version_id]
    except (KeyError, TypeError) as exc:
        raise StateError(f"unknown candidate: {version_id}") from exc
    if not isinstance(value, dict):
        raise StateError(f"invalid candidate record: {version_id}")
    return value


def add_candidate(
    registry: dict[str, Any], manifest: dict[str, Any], content: str, artifacts_dir: Path
) -> None:
    if manifest.get("state") != "CHECKED":
        raise StateError("only CHECKED candidates can be registered")
    if manifest.get("skill_id") != registry.get("skill_id"):
        raise StateError("candidate skill_id does not match registry")
    version_id = _non_empty(manifest.get("version_id"), "candidate.version_id")
    if manifest.get("content_sha256") != _sha256(content) or version_id != _sha256(content):
        raise StateError("candidate content hash does not match manifest")
    artifacts_dir = artifacts_dir.expanduser().resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    if not artifacts_dir.is_dir() or artifacts_dir.is_symlink():
        raise StateError("artifacts_dir must be a real directory")
    artifact_path = artifacts_dir / f"{version_id}.md"
    if artifact_path.exists():
        if artifact_path.is_symlink() or not artifact_path.is_file():
            raise StateError("candidate artifact path is not a regular file")
        if artifact_path.read_text(encoding="utf-8") != content:
            raise StateError("immutable candidate artifact already contains different content")
    else:
        with artifact_path.open("x", encoding="utf-8") as handle:
            handle.write(content)
    record = dict(manifest)
    record["artifact_path"] = str(artifact_path)
    registry["candidates"][version_id] = record
    registry["versions"][version_id] = {
        "version_id": version_id,
        "kind": "candidate",
        "content_sha256": version_id,
        "artifact_path": str(artifact_path),
    }


def approve_candidate(registry: dict[str, Any], version_id: str, reviewer: str) -> None:
    reviewer = _non_empty(reviewer, "reviewer")
    candidate = _candidate(registry, version_id)
    if candidate.get("state") != "CHECKED":
        raise StateError("candidate is not pending human approval")
    candidate["state"] = "APPROVED_FOR_CANARY"
    candidate["approved_by"] = reviewer
    candidate["approved_at"] = _now()
    registry["promotion_decisions"].append(
        {"type": "APPROVE_FOR_CANARY", "version_id": version_id, "actor": reviewer, "at": _now()}
    )


def record_checker(
    registry: dict[str, Any],
    version_id: str,
    passed: bool,
    checker_id: str,
    evidence_ref: str,
) -> None:
    candidate = _candidate(registry, version_id)
    if candidate.get("state") not in {"CHECKED", "APPROVED_FOR_CANARY"}:
        raise StateError("candidate is not ready for independent checker evidence")
    checker_id = _non_empty(checker_id, "checker_id")
    evidence_ref = _non_empty(evidence_ref, "evidence_ref")
    if any(character.isspace() for character in evidence_ref):
        raise StateError("evidence_ref must not contain whitespace")
    if not isinstance(passed, bool):
        raise StateError("checker passed must be boolean")
    candidate["checker"] = {
        "checker_id": checker_id,
        "passed": passed,
        "evidence_ref": evidence_ref,
        "recorded_at": _now(),
    }
    if not passed:
        candidate["state"] = "CHECKER_FAILED"


def record_canary(
    registry: dict[str, Any],
    version_id: str,
    evidence: dict[str, Any],
) -> None:
    candidate = _candidate(registry, version_id)
    automation = registry.get("automation", {})
    automated = candidate.get("state") == "CHECKED" and automation.get("enabled") is True
    if candidate.get("state") != "APPROVED_FOR_CANARY" and not automated:
        raise StateError("candidate requires human approval before canary")
    if candidate.get("checker", {}).get("passed") is not True:
        raise StateError("independent checker evidence is required before canary")
    required = {
        "schema_version",
        "status",
        "experiment_id",
        "skill_id",
        "control_version_id",
        "candidate_version_id",
        "primary_metric",
        "primary_lower_bound_delta",
        "guardrails_pass",
        "sample_ratio_ok",
        "attribution_complete",
        "data_fresh",
        "rules_hash",
        "config_hash",
        "evidence_ref",
    }
    if not isinstance(evidence, dict) or not required.issubset(evidence):
        raise StateError("complete experiment evidence is required before canary")
    if evidence.get("schema_version") != 1 or evidence.get("status") != "COMPLETED":
        raise StateError("experiment evidence must be completed with schema_version 1")
    if evidence.get("skill_id") != registry.get("skill_id"):
        raise StateError("experiment evidence skill_id does not match registry")
    if evidence.get("candidate_version_id") != version_id:
        raise StateError("experiment evidence candidate does not match version")
    if evidence.get("control_version_id") != registry.get("current_version"):
        raise StateError("experiment evidence control does not match current version")
    for field in ("experiment_id", "primary_metric", "rules_hash", "config_hash", "evidence_ref"):
        value = _non_empty(evidence.get(field), f"evidence.{field}")
        if any(character.isspace() for character in value):
            raise StateError(f"evidence.{field} must not contain whitespace")
    for field in ("guardrails_pass", "sample_ratio_ok", "attribution_complete", "data_fresh"):
        if not isinstance(evidence.get(field), bool):
            raise StateError(f"evidence.{field} must be boolean")
    primary_lower_bound_delta = evidence.get("primary_lower_bound_delta")
    if (
        not isinstance(primary_lower_bound_delta, (int, float))
        or isinstance(primary_lower_bound_delta, bool)
        or not math.isfinite(primary_lower_bound_delta)
    ):
        raise StateError("evidence.primary_lower_bound_delta must be finite numeric")
    if automated:
        candidate["approval_mode"] = "AUTOMATION_POLICY"
    passed = primary_lower_bound_delta > 0 and all(
        evidence[field] is True
        for field in ("guardrails_pass", "sample_ratio_ok", "attribution_complete", "data_fresh")
    )
    candidate["canary"] = dict(evidence)
    candidate["canary"]["evidence_sha256"] = _sha256(
        json.dumps(evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    candidate["canary"]["passed"] = passed
    candidate["canary"]["recorded_at"] = _now()
    candidate["state"] = "CANARY_PASSED" if passed else "CANARY_FAILED"


def enable_automation(registry: dict[str, Any], actor: str) -> None:
    actor = _non_empty(actor, "actor")
    automation = registry.setdefault(
        "automation", {"enabled": False, "first_round_completed": False, "enabled_by": None}
    )
    if automation.get("paused_reason"):
        raise StateError("automation is paused after rollback and requires manual review")
    if automation.get("first_round_completed") is not True:
        raise StateError("automation requires a completed manual round")
    automation["enabled"] = True
    automation["enabled_by"] = actor
    automation["enabled_at"] = _now()


def promote_candidate(
    registry: dict[str, Any], version_id: str, actor: str, expected_current_version: str
) -> None:
    actor = _non_empty(actor, "actor")
    expected_current_version = _non_empty(expected_current_version, "expected_current_version")
    if registry.get("current_version") != expected_current_version:
        raise StateError("current version changed; promotion compare-and-set failed")
    candidate = _candidate(registry, version_id)
    automation = registry.get("automation", {})
    automated = candidate.get("approval_mode") == "AUTOMATION_POLICY" and automation.get("enabled") is True
    if candidate.get("approved_by") is None and not automated:
        raise StateError("human approval is required before promotion")
    if candidate.get("state") != "CANARY_PASSED":
        raise StateError("positive canary evidence is required before promotion")
    previous = registry["current_version"]
    registry["last_known_good"] = previous
    registry["current_version"] = version_id
    candidate["state"] = "PROMOTED"
    candidate["promoted_at"] = _now()
    canary = candidate["canary"]
    if candidate.get("approved_by") is not None:
        automation["first_round_completed"] = True
        automation.pop("paused_reason", None)
        automation.pop("paused_at", None)
    registry["promotion_decisions"].append(
        {
            "type": "PROMOTE",
            "version_id": version_id,
            "previous_version_id": previous,
            "actor": actor,
            "experiment_id": canary["experiment_id"],
            "rules_hash": canary["rules_hash"],
            "config_hash": canary["config_hash"],
            "evidence_sha256": canary["evidence_sha256"],
            "at": _now(),
        }
    )


def rollback(
    registry: dict[str, Any], reason: str, actor: str, expected_current_version: str
) -> None:
    reason = _non_empty(reason, "reason")
    actor = _non_empty(actor, "actor")
    expected_current_version = _non_empty(expected_current_version, "expected_current_version")
    if registry.get("current_version") != expected_current_version:
        raise StateError("current version changed; rollback compare-and-set failed")
    previous = registry["current_version"]
    target = registry["last_known_good"]
    if previous == target:
        raise StateError("no promoted version is available to roll back")
    current_candidate = registry.get("candidates", {}).get(previous)
    if isinstance(current_candidate, dict):
        current_candidate["state"] = "ROLLED_BACK"
    registry["current_version"] = target
    automation = registry.get("automation")
    if isinstance(automation, dict):
        automation["enabled"] = False
        automation["paused_at"] = _now()
        automation["paused_reason"] = reason
    registry["rollback_events"].append(
        {
            "from_version_id": previous,
            "to_version_id": target,
            "reason": reason,
            "actor": actor,
            "at": _now(),
        }
    )


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _read_text(path: Path) -> str:
    path = path.expanduser().resolve(strict=True)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{path}: expected a regular file")
    return path.read_text(encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="check a baseline/candidate pair")
    check.add_argument("--policy", type=Path, required=True)
    check.add_argument("--baseline", type=Path, required=True)
    check.add_argument("--candidate", type=Path, required=True)
    check.add_argument("--output", type=Path, required=True)

    init = commands.add_parser("init", help="create a registry from a baseline Skill")
    init.add_argument("--skill-id", required=True)
    init.add_argument("--baseline", type=Path, required=True)
    init.add_argument("--registry", type=Path, required=True)

    register = commands.add_parser("register", help="register a checked candidate artifact")
    register.add_argument("--manifest", type=Path, required=True)
    register.add_argument("--candidate", type=Path, required=True)
    register.add_argument("--registry", type=Path, required=True)
    register.add_argument("--artifacts-dir", type=Path, required=True)

    approve = commands.add_parser("approve", help="record manual approval for canary")
    approve.add_argument("--registry", type=Path, required=True)
    approve.add_argument("--version-id", required=True)
    approve.add_argument("--reviewer", required=True)

    checker = commands.add_parser("record-checker", help="record independent checker evidence")
    checker.add_argument("--registry", type=Path, required=True)
    checker.add_argument("--version-id", required=True)
    checker.add_argument("--passed", action="store_true")
    checker.add_argument("--checker-id", required=True)
    checker.add_argument("--evidence-ref", required=True)

    canary = commands.add_parser("record-canary", help="record external canary evidence")
    canary.add_argument("--registry", type=Path, required=True)
    canary.add_argument("--version-id", required=True)
    canary.add_argument("--evidence", type=Path, required=True)

    enable = commands.add_parser("enable-automation", help="enable bounded automation after a manual round")
    enable.add_argument("--registry", type=Path, required=True)
    enable.add_argument("--actor", required=True)

    promote = commands.add_parser("promote", help="switch the runtime pointer")
    promote.add_argument("--registry", type=Path, required=True)
    promote.add_argument("--version-id", required=True)
    promote.add_argument("--actor", required=True)
    promote.add_argument("--expected-current-version", required=True)

    rollback_parser = commands.add_parser("rollback", help="restore last-known-good")
    rollback_parser.add_argument("--registry", type=Path, required=True)
    rollback_parser.add_argument("--reason", required=True)
    rollback_parser.add_argument("--actor", required=True)
    rollback_parser.add_argument("--expected-current-version", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "check":
            manifest = check_candidate(_load_json(args.policy), _read_text(args.baseline), _read_text(args.candidate))
            _write_json(args.output, manifest)
            print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
        elif args.command == "init":
            _write_json(args.registry, new_registry(args.skill_id, _read_text(args.baseline)))
        elif args.command == "register":
            registry = _load_json(args.registry)
            manifest = _load_json(args.manifest)
            add_candidate(registry, manifest, _read_text(args.candidate), args.artifacts_dir)
            _write_json(args.registry, registry)
        elif args.command == "approve":
            registry = _load_json(args.registry)
            approve_candidate(registry, args.version_id, args.reviewer)
            _write_json(args.registry, registry)
        elif args.command == "record-checker":
            registry = _load_json(args.registry)
            record_checker(
                registry,
                args.version_id,
                args.passed,
                args.checker_id,
                args.evidence_ref,
            )
            _write_json(args.registry, registry)
        elif args.command == "record-canary":
            registry = _load_json(args.registry)
            record_canary(registry, args.version_id, _load_json(args.evidence))
            _write_json(args.registry, registry)
        elif args.command == "enable-automation":
            registry = _load_json(args.registry)
            enable_automation(registry, args.actor)
            _write_json(args.registry, registry)
        elif args.command == "promote":
            registry = _load_json(args.registry)
            promote_candidate(registry, args.version_id, args.actor, args.expected_current_version)
            _write_json(args.registry, registry)
        elif args.command == "rollback":
            registry = _load_json(args.registry)
            rollback(registry, args.reason, args.actor, args.expected_current_version)
            _write_json(args.registry, registry)
        else:
            raise ValueError(f"unknown command: {args.command}")
    except (OSError, ValueError, GateError, StateError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
