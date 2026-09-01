#!/usr/bin/env python3
"""Validate and prepare a current-source PRD readability evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


EXPECTED_STRENGTHS = {"light", "standard", "enhanced"}
EXPECTED_ROLES = {"business", "product", "engineering", "testing", "operations"}
OUTPUT_FIELDS = {"summary", "key_facts", "evidence_anchors", "uncertainties"}
STATIC_SCORE_FIELDS = {
    "context_and_purpose",
    "concept_object_state",
    "subject_and_responsibility",
    "flow_causality",
    "rule_exception_determinacy",
    "result_evidence_observability",
    "reading_load_fluency",
}
BEHAVIOR_SCORE_FIELDS = {
    "recall_consistency",
    "evidence_location_quality",
    "cross_role_alignment",
}
HARD_SCORE_FIELDS = {
    "subject_and_responsibility",
    "rule_exception_determinacy",
    "result_evidence_observability",
}


class ContractError(ValueError):
    """Raised when a readability evaluation contract is invalid."""


def load_contract(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractError("contract must be a JSON object")
    return data


def source_set_digest(paths: list[str], root: Path) -> str:
    digest = hashlib.sha256()
    resolved_root = root.resolve()
    for value in paths:
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts or not value:
            raise ContractError(f"source path must stay under repository root: {value!r}")
        try:
            source = (resolved_root / relative).resolve(strict=True)
            source.relative_to(resolved_root)
        except (OSError, ValueError) as exc:
            raise ContractError(f"invalid source path: {value!r}") from exc
        if not source.is_file():
            raise ContractError(f"source path is not a file: {value}")
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def non_empty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label}: expected a non-empty string")
    return value.strip()


def validate_contract(contract: dict[str, Any], root: Path) -> None:
    required = {
        "version",
        "description",
        "proof_limit",
        "thresholds",
        "source_profile",
        "samples",
        "roles",
        "reader_output_schema",
        "tasks",
        "evidence",
    }
    if set(contract) != required or contract.get("version") != 1:
        raise ContractError("contract keys or version are invalid")
    non_empty(contract["description"], "description")
    if contract["proof_limit"] != "simulated-reader-evidence-only":
        raise ContractError("proof_limit must be simulated-reader-evidence-only")

    evidence = contract["evidence"]
    expected_evidence_keys = {
        "status",
        "reader_model",
        "judge_model",
        "collector_payload_sha256",
        "collector_launcher_sha256",
        "response_sha256",
        "judge_payload_sha256",
        "judge_launcher_sha256",
        "report_sha256",
        "responses_path",
    }
    if (
        not isinstance(evidence, dict)
        or set(evidence) != expected_evidence_keys
        or evidence["status"] != "complete"
        or evidence["reader_model"] != "gpt-5.6-sol"
        or evidence["judge_model"] != "gpt-5.6-terra"
    ):
        raise ContractError("evidence identity is invalid")
    if evidence["responses_path"] != "fixtures/skill-eval/product-prd-readability-r1-reader-evidence.jsonl":
        raise ContractError("evidence response path is invalid")
    for field in expected_evidence_keys - {
        "status",
        "reader_model",
        "judge_model",
        "responses_path",
    }:
        value = evidence[field]
        if not isinstance(value, str) or len(value) != 64:
            raise ContractError(f"evidence.{field}: invalid SHA-256")
        try:
            int(value, 16)
        except ValueError as exc:
            raise ContractError(f"evidence.{field}: invalid SHA-256") from exc

    thresholds = contract["thresholds"]
    if thresholds != {
        "static_min": 62,
        "behavior_min": 24,
        "total_min": 86,
        "hard_dimension_min": 7,
    }:
        raise ContractError("thresholds do not match the trial gate")

    profile = contract["source_profile"]
    if not isinstance(profile, dict) or set(profile) != {"id", "paths", "sha256"}:
        raise ContractError("source_profile must contain id, paths, and sha256")
    non_empty(profile["id"], "source_profile.id")
    paths = profile["paths"]
    if not isinstance(paths, list) or not paths or any(not isinstance(path, str) for path in paths):
        raise ContractError("source_profile.paths must be a non-empty string list")
    if len(paths) != len(set(paths)):
        raise ContractError("source_profile.paths contains duplicates")
    actual_digest = source_set_digest(paths, root)
    if profile["sha256"] != actual_digest:
        raise ContractError(
            f"source set changed expected={profile['sha256']} actual={actual_digest}"
        )

    samples = contract["samples"]
    if not isinstance(samples, list) or len(samples) != 3:
        raise ContractError("samples must contain light, standard, and enhanced")
    sample_by_id: dict[str, dict[str, Any]] = {}
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict) or set(sample) != {"id", "strength", "path"}:
            raise ContractError(f"samples[{index}] is invalid")
        sample_id = non_empty(sample["id"], f"samples[{index}].id")
        if sample_id in sample_by_id:
            raise ContractError("duplicate sample id")
        if sample["strength"] not in EXPECTED_STRENGTHS or sample["path"] not in paths:
            raise ContractError(f"samples[{index}] has invalid strength or path")
        sample_by_id[sample_id] = sample
    if {sample["strength"] for sample in samples} != EXPECTED_STRENGTHS:
        raise ContractError("samples must cover three document strengths")

    roles = contract["roles"]
    if not isinstance(roles, dict) or set(roles) != EXPECTED_ROLES:
        raise ContractError("roles must cover five reader roles")
    for role, definition in roles.items():
        if not isinstance(definition, dict) or set(definition) != {"focus", "criteria"}:
            raise ContractError(f"roles.{role} is invalid")
        non_empty(definition["focus"], f"roles.{role}.focus")
        criteria = definition["criteria"]
        if not isinstance(criteria, list) or len(criteria) < 3:
            raise ContractError(f"roles.{role}.criteria must contain at least three items")
        for index, criterion in enumerate(criteria):
            non_empty(criterion, f"roles.{role}.criteria[{index}]")

    schema = contract["reader_output_schema"]
    if not isinstance(schema, dict) or set(schema) != OUTPUT_FIELDS:
        raise ContractError("reader_output_schema is invalid")
    for field, description in schema.items():
        non_empty(description, f"reader_output_schema.{field}")

    tasks = contract["tasks"]
    if not isinstance(tasks, list) or len(tasks) != 15:
        raise ContractError("tasks must contain exactly fifteen sample/role pairs")
    pairs: set[tuple[str, str]] = set()
    task_ids: set[str] = set()
    for index, task in enumerate(tasks):
        if not isinstance(task, dict) or set(task) != {"id", "sample_id", "role", "prompt"}:
            raise ContractError(f"tasks[{index}] is invalid")
        task_id = non_empty(task["id"], f"tasks[{index}].id")
        sample_id = task["sample_id"]
        role = task["role"]
        non_empty(task["prompt"], f"tasks[{index}].prompt")
        if task_id in task_ids:
            raise ContractError("duplicate task id")
        task_ids.add(task_id)
        if sample_id not in sample_by_id or role not in roles:
            raise ContractError(f"tasks[{index}] references an unknown sample or role")
        pair = (sample_id, role)
        if pair in pairs:
            raise ContractError("duplicate sample/role pair")
        pairs.add(pair)
    expected_pairs = {(sample_id, role) for sample_id in sample_by_id for role in roles}
    if pairs != expected_pairs:
        raise ContractError("tasks do not cover the complete sample/role matrix")


def prepare_tasks(contract: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    validate_contract(contract, root)
    profile = contract["source_profile"]
    sample_by_id = {sample["id"]: sample for sample in contract["samples"]}
    return [
        {
            "task_id": task["id"],
            "sample_id": task["sample_id"],
            "strength": sample_by_id[task["sample_id"]]["strength"],
            "role": task["role"],
            "source_path": sample_by_id[task["sample_id"]]["path"],
            "source_profile": profile["id"],
            "source_paths": profile["paths"],
            "source_sha256": profile["sha256"],
            "proof_limit": contract["proof_limit"],
            "thresholds": contract["thresholds"],
            "focus": contract["roles"][task["role"]]["focus"],
            "prompt": task["prompt"],
            "criteria": contract["roles"][task["role"]]["criteria"],
            "output_schema": contract["reader_output_schema"],
        }
        for task in contract["tasks"]
    ]


def score_values(value: Any, fields: set[str], label: str) -> dict[str, float]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ContractError(f"{label}: invalid score dimensions")
    scores: dict[str, float] = {}
    for field in fields:
        score = value[field]
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 10:
            raise ContractError(f"{label}.{field}: invalid score")
        scores[field] = float(score)
    return scores


def validate_report(contract: dict[str, Any], report: dict[str, Any]) -> None:
    expected_keys = {
        "version",
        "evaluation_id",
        "judge_model",
        "reader_model",
        "source_sha256",
        "response_sha256",
        "proof_limit",
        "thresholds",
        "elapsed_ms",
        "samples",
        "passed",
    }
    if set(report) != expected_keys or report.get("version") != 1:
        raise ContractError("report keys or version are invalid")
    evidence = contract["evidence"]
    if (
        report["evaluation_id"] != "product-prd-readability-r1-judge"
        or report["judge_model"] != evidence["judge_model"]
        or report["reader_model"] != evidence["reader_model"]
        or report["proof_limit"] != contract["proof_limit"]
        or report["source_sha256"] != contract["source_profile"]["sha256"]
        or report["thresholds"] != contract["thresholds"]
    ):
        raise ContractError("report identity changed")
    response_sha256 = report["response_sha256"]
    if not isinstance(response_sha256, str) or len(response_sha256) != 64:
        raise ContractError("report response digest is invalid")
    try:
        int(response_sha256, 16)
    except ValueError as exc:
        raise ContractError("report response digest is invalid") from exc
    if response_sha256 != evidence["response_sha256"]:
        raise ContractError("report evidence identity changed")
    if not isinstance(report["elapsed_ms"], int) or report["elapsed_ms"] < 0:
        raise ContractError("report elapsed time is invalid")

    sample_strengths = {sample["id"]: sample["strength"] for sample in contract["samples"]}
    samples = report["samples"]
    if not isinstance(samples, list) or len(samples) != 3:
        raise ContractError("report must contain three samples")
    seen: set[str] = set()
    calculated_passes: list[bool] = []
    thresholds = contract["thresholds"]
    sample_keys = {
        "sample_id",
        "strength",
        "static_scores",
        "behavior_scores",
        "static_total",
        "behavior_total",
        "total",
        "hard_dimension_min",
        "blockers",
        "findings",
        "residual_risks",
        "passed",
    }
    for sample in samples:
        if not isinstance(sample, dict) or set(sample) != sample_keys:
            raise ContractError("report sample shape is invalid")
        sample_id = sample["sample_id"]
        if (
            sample_id not in sample_strengths
            or sample_id in seen
            or sample["strength"] != sample_strengths[sample_id]
        ):
            raise ContractError("report sample identity is invalid")
        seen.add(sample_id)
        static_scores = score_values(
            sample["static_scores"], STATIC_SCORE_FIELDS, f"samples.{sample_id}.static"
        )
        behavior_scores = score_values(
            sample["behavior_scores"], BEHAVIOR_SCORE_FIELDS, f"samples.{sample_id}.behavior"
        )
        static_total = round(sum(static_scores.values()), 2)
        behavior_total = round(sum(behavior_scores.values()), 2)
        total = round(static_total + behavior_total, 2)
        hard_min = min(static_scores[field] for field in HARD_SCORE_FIELDS)
        reported_totals: dict[str, float] = {}
        for field in ("static_total", "behavior_total", "total", "hard_dimension_min"):
            value = sample[field]
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                raise ContractError("report score totals are invalid")
            reported_totals[field] = float(value)
        if any(
            abs(reported_totals[field] - expected) > 0.001
            for field, expected in (
                ("static_total", static_total),
                ("behavior_total", behavior_total),
                ("total", total),
                ("hard_dimension_min", hard_min),
            )
        ):
            raise ContractError("score totals changed")
        for field in ("blockers", "findings", "residual_risks"):
            if not isinstance(sample[field], list) or any(
                not isinstance(item, str) for item in sample[field]
            ):
                raise ContractError(f"report sample field is invalid: {field}")
        calculated_pass = (
            static_total >= thresholds["static_min"]
            and behavior_total >= thresholds["behavior_min"]
            and total >= thresholds["total_min"]
            and hard_min >= thresholds["hard_dimension_min"]
            and not sample["blockers"]
        )
        if sample["passed"] is not calculated_pass:
            raise ContractError("sample gate result changed")
        calculated_passes.append(calculated_pass)
    if report["passed"] is not all(calculated_passes):
        raise ContractError("overall gate result changed")


def validate_report_file(contract: dict[str, Any], path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != contract["evidence"]["report_sha256"]:
        raise ContractError("report file digest changed")
    report = json.loads(raw)
    if not isinstance(report, dict):
        raise ContractError("report file must contain an object")
    validate_report(contract, report)
    return report


def validate_response_file(
    contract: dict[str, Any], path: Path, root: Path | None = None
) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != contract["evidence"]["response_sha256"]:
        raise ContractError("response file digest changed")
    if any(
        pattern.search(raw)
        for pattern in (
            re.compile(rb"/Users/"),
            re.compile(rb"sk-[A-Za-z0-9]"),
            re.compile(rb"Authorization"),
        )
    ):
        raise ContractError("response file contains a sensitive pattern")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ContractError(f"responses[{line_number}] is invalid")
        rows.append(row)
    if len(rows) != 15:
        raise ContractError("response file must contain fifteen rows")
    task_by_id = {task["id"]: task for task in contract["tasks"]}
    if [row.get("task_id") for row in rows] != list(task_by_id):
        raise ContractError("response task order or identity changed")
    sample_by_id = {sample["id"]: sample for sample in contract["samples"]}
    resolved_root = root or Path(__file__).resolve().parents[2]
    source_sha256 = {
        sample_id: hashlib.sha256(
            (resolved_root / sample["path"]).read_bytes()
        ).hexdigest()
        for sample_id, sample in sample_by_id.items()
    }
    expected_row_keys = {
        "task_id",
        "sample_id",
        "strength",
        "role",
        "model",
        "payload_sha256",
        "source_sha256",
        "runner",
        "elapsed_ms",
        "reader_output",
    }
    pairs: set[tuple[str, str]] = set()
    for row in rows:
        task = task_by_id[row["task_id"]]
        sample_id = row.get("sample_id")
        pair = (sample_id, row.get("role"))
        if (
            set(row) != expected_row_keys
            or sample_id not in sample_by_id
            or pair in pairs
            or row.get("role") != task["role"]
            or sample_id != task["sample_id"]
            or row.get("strength") != sample_by_id[sample_id]["strength"]
            or row.get("model") != contract["evidence"]["reader_model"]
            or row.get("payload_sha256") != contract["evidence"]["collector_payload_sha256"]
            or row.get("source_sha256") != source_sha256[sample_id]
            or row.get("runner") != "codex-exec-ephemeral-read-only"
            or not isinstance(row.get("elapsed_ms"), int)
            or row["elapsed_ms"] < 0
        ):
            raise ContractError(f"response identity is invalid: {row.get('task_id')}")
        pairs.add(pair)
        reader_output = row.get("reader_output")
        if not isinstance(reader_output, dict) or set(reader_output) != OUTPUT_FIELDS:
            raise ContractError(f"response output shape is invalid: {row['task_id']}")
        if not isinstance(reader_output["summary"], str) or not reader_output["summary"].strip():
            raise ContractError(f"response summary is invalid: {row['task_id']}")
        for field in OUTPUT_FIELDS - {"summary"}:
            if not isinstance(reader_output[field], list) or any(
                not isinstance(item, str) for item in reader_output[field]
            ):
                raise ContractError(f"response field is invalid: {row['task_id']}.{field}")
    if len(pairs) != 15:
        raise ContractError("response sample/role matrix is incomplete")
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or prepare PRD readability tasks")
    parser.add_argument("command", choices=("validate", "prepare", "validate-report"))
    parser.add_argument("--contract", required=True)
    parser.add_argument("--output")
    parser.add_argument("--report")
    parser.add_argument("--responses")
    args = parser.parse_args()

    contract_path = Path(args.contract).resolve()
    root = Path(__file__).resolve().parents[2]
    contract = load_contract(contract_path)
    if args.command == "validate":
        validate_contract(contract, root)
        print("OK PRD readability evaluation tasks=15 samples=3 roles=5")
        return 0
    if args.command == "validate-report":
        validate_contract(contract, root)
        if not args.report:
            parser.error("validate-report requires --report")
        if not args.responses:
            parser.error("validate-report requires --responses")
        validate_response_file(contract, Path(args.responses), root)
        validate_report_file(contract, Path(args.report))
        print("OK PRD readability report samples=3 passed=true")
        return 0
    if not args.output:
        parser.error("prepare requires --output")
    rows = prepare_tasks(contract, root)
    write_jsonl(Path(args.output), rows)
    print(f"OK wrote {args.output} tasks={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
