#!/usr/bin/env python3
"""Validate an explicit, redacted evidence batch for Skill learning candidates.

Input: one JSON batch supplied by the current task; no history discovery.
Output: validation result on stdout and a non-zero exit code on failure.
Writes: none.
Network: never.

The validator only proves the shape and linkage of a candidate proposal. It
does not confirm a pattern, promote a candidate, edit a Skill, or measure
behavioral improvement.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


EVIDENCE_KINDS = {
    "repeated-failure",
    "confirmed-correction",
    "validator-failure",
    "cr-root-cause",
    "source-staleness",
}
EDIT_ACTIONS = {"add", "delete", "rewrite", "extract", "reject"}
DESTINATIONS = {
    "agents",
    "skill",
    "reference",
    "script",
    "fixture",
    "task-only",
    "reject",
}
SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(?:身份证(?:号|号码)?|identity[-_ ]?card)\s*[:：=]?\s*\d{17}[\dXx]"),
    re.compile(r"(?i)(?:手机号|手机号码|联系电话|mobile|phone)\s*[:：=]?\s*1[3-9]\d{9}"),
    re.compile(r"(?i)(?:银行卡(?:号|号码)?|bank[-_ ]?card|card[-_ ]?number)\s*[:：=]?\s*\d[\d -]{11,25}\d"),
)
RAW_KEYS = {
    "raw",
    "raw_text",
    "transcript",
    "transcript_text",
    "full_text",
    "content",
    "messages",
    "conversation",
}


class ValidationError(ValueError):
    """A user-facing schema or evidence-boundary failure."""


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{name} must be an object")
    return value


def _require_string(value: Any, name: str, *, max_length: int = 800) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")
    if len(value) > max_length:
        raise ValidationError(f"{name} exceeds {max_length} characters")
    return value.strip()


def _require_int(value: Any, name: str, *, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValidationError(f"{name} must be an integer >= {minimum}")
    return value


def _require_string_list(value: Any, name: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        suffix = "" if allow_empty else " and non-empty"
        raise ValidationError(f"{name} must be an array{suffix}")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_require_string(item, f"{name}[{index}]", max_length=240))
    return result


def _check_keys(value: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValidationError(f"{name} contains unsupported fields: {', '.join(unknown)}")


def _scan_for_raw_or_sensitive(value: Any, path: str = "batch") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in RAW_KEYS:
                raise ValidationError(f"{path}.{key} must not contain raw transcript content")
            _scan_for_raw_or_sensitive(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_raw_or_sensitive(child, f"{path}[{index}]")
        return
    if isinstance(value, str) and any(pattern.search(value) for pattern in SENSITIVE_PATTERNS):
        raise ValidationError(f"{path} contains sensitive material; keep only a redacted summary and hash")


def validate_batch(payload: Any) -> dict[str, Any]:
    root = _require_object(payload, "root")
    _check_keys(root, {"version", "batch", "evidence", "pattern", "edits", "review"}, "root")
    if root.get("version") != 1:
        raise ValidationError("version must be 1")
    _scan_for_raw_or_sensitive(root)

    batch = _require_object(root.get("batch"), "batch")
    _check_keys(batch, {"objective", "min_independent_tasks", "max_edits", "max_changed_lines"}, "batch")
    _require_string(batch.get("objective"), "batch.objective", max_length=500)
    min_tasks = _require_int(batch.get("min_independent_tasks"), "batch.min_independent_tasks", minimum=2)
    max_edits = _require_int(batch.get("max_edits"), "batch.max_edits")
    if "max_changed_lines" in batch:
        _require_int(batch["max_changed_lines"], "batch.max_changed_lines")

    evidence = root.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValidationError("evidence must be a non-empty array")
    evidence_by_id: dict[str, dict[str, Any]] = {}
    task_refs: set[str] = set()
    for index, item in enumerate(evidence):
        entry = _require_object(item, f"evidence[{index}]")
        _check_keys(
            entry,
            {"id", "task_ref", "kind", "source_ref", "summary", "excerpt_sha256", "sensitivity_check"},
            f"evidence[{index}]",
        )
        evidence_id = _require_string(entry.get("id"), f"evidence[{index}].id", max_length=120)
        if evidence_id in evidence_by_id:
            raise ValidationError(f"duplicate evidence id: {evidence_id}")
        task_ref = _require_string(entry.get("task_ref"), f"evidence[{index}].task_ref", max_length=240)
        kind = _require_string(entry.get("kind"), f"evidence[{index}].kind", max_length=80)
        if kind not in EVIDENCE_KINDS:
            raise ValidationError(f"unsupported evidence kind: {kind}")
        _require_string(entry.get("source_ref"), f"evidence[{index}].source_ref", max_length=240)
        _require_string(entry.get("summary"), f"evidence[{index}].summary", max_length=800)
        digest = _require_string(entry.get("excerpt_sha256"), f"evidence[{index}].excerpt_sha256", max_length=64)
        if not SHA256_RE.fullmatch(digest):
            raise ValidationError(f"evidence[{index}].excerpt_sha256 must be a lowercase SHA-256 digest")
        if entry.get("sensitivity_check") != "public-safe":
            raise ValidationError(f"evidence[{index}].sensitivity_check must be public-safe")
        evidence_by_id[evidence_id] = entry
        task_refs.add(task_ref)
    if len(task_refs) < min_tasks:
        raise ValidationError(
            f"evidence needs at least {min_tasks} independent task_ref values; got {len(task_refs)}"
        )

    pattern = _require_object(root.get("pattern"), "pattern")
    _check_keys(
        pattern,
        {
            "target_skill",
            "observed_failure",
            "expected_behavior",
            "reuse_scope",
            "proposed_authority",
            "validation",
            "evidence_refs",
        },
        "pattern",
    )
    target_skill = _require_string(pattern.get("target_skill"), "pattern.target_skill", max_length=120)
    if not SKILL_ID_RE.fullmatch(target_skill):
        raise ValidationError("pattern.target_skill must be a lowercase Skill id")
    for field in ("observed_failure", "expected_behavior", "reuse_scope", "proposed_authority", "validation"):
        _require_string(pattern.get(field), f"pattern.{field}")
    pattern_refs = _require_string_list(pattern.get("evidence_refs"), "pattern.evidence_refs")
    if len(pattern_refs) != len(set(pattern_refs)):
        raise ValidationError("pattern.evidence_refs must not contain duplicates")
    unknown_pattern_refs = sorted(set(pattern_refs) - set(evidence_by_id))
    if unknown_pattern_refs:
        raise ValidationError(f"pattern.evidence_refs contain unknown ids: {', '.join(unknown_pattern_refs)}")
    pattern_task_refs = {evidence_by_id[ref]["task_ref"] for ref in pattern_refs}
    if len(pattern_task_refs) < min_tasks:
        raise ValidationError("pattern.evidence_refs must cover the declared independent task count")

    edits = root.get("edits")
    if not isinstance(edits, list):
        raise ValidationError("edits must be an array")
    if len(edits) > max_edits:
        raise ValidationError(f"edits count {len(edits)} exceeds batch.max_edits {max_edits}")
    edit_ids: set[str] = set()
    for index, item in enumerate(edits):
        edit = _require_object(item, f"edits[{index}]")
        _check_keys(edit, {"id", "action", "destination", "target", "reason", "evidence_refs"}, f"edits[{index}]")
        edit_id = _require_string(edit.get("id"), f"edits[{index}].id", max_length=120)
        if edit_id in edit_ids:
            raise ValidationError(f"duplicate edit id: {edit_id}")
        edit_ids.add(edit_id)
        action = _require_string(edit.get("action"), f"edits[{index}].action", max_length=40)
        if action not in EDIT_ACTIONS:
            raise ValidationError(f"unsupported edit action: {action}")
        destination = _require_string(edit.get("destination"), f"edits[{index}].destination", max_length=40)
        if destination not in DESTINATIONS:
            raise ValidationError(f"unsupported edit destination: {destination}")
        if action == "reject" and destination != "reject":
            raise ValidationError("reject edits must use the reject destination")
        if action != "reject" and destination == "reject":
            raise ValidationError("non-reject edits cannot use the reject destination")
        _require_string(edit.get("target"), f"edits[{index}].target", max_length=240)
        _require_string(edit.get("reason"), f"edits[{index}].reason", max_length=800)
        edit_refs = _require_string_list(edit.get("evidence_refs"), f"edits[{index}].evidence_refs")
        if len(edit_refs) != len(set(edit_refs)):
            raise ValidationError(f"edits[{index}].evidence_refs must not contain duplicates")
        unknown_edit_refs = sorted(set(edit_refs) - set(evidence_by_id))
        if unknown_edit_refs:
            raise ValidationError(f"edits[{index}].evidence_refs contain unknown ids: {', '.join(unknown_edit_refs)}")

    review = _require_object(root.get("review"), "review")
    _check_keys(review, {"status", "owner", "sensitivity_check"}, "review")
    if review.get("status") != "candidate":
        raise ValidationError("review.status must remain candidate; confirmation and promotion are human actions")
    _require_string(review.get("owner"), "review.owner", max_length=160)
    if review.get("sensitivity_check") != "public-safe":
        raise ValidationError("review.sensitivity_check must be public-safe")

    return {
        "status": "PASS",
        "independent_tasks": len(task_refs),
        "evidence_count": len(evidence),
        "edit_count": len(edits),
        "target_skill": target_skill,
    }


def validate_file(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValidationError(f"input must be a regular file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON input: {exc}") from exc
    return validate_batch(payload)


def _valid_fixture() -> dict[str, Any]:
    digest = hashlib.sha256(b"redacted evidence").hexdigest()
    return {
        "version": 1,
        "batch": {
            "objective": "收敛重复的规则偏离证据",
            "min_independent_tasks": 2,
            "max_edits": 2,
            "max_changed_lines": 40,
        },
        "evidence": [
            {
                "id": "evidence-a",
                "task_ref": "task:alpha",
                "kind": "validator-failure",
                "source_ref": "fixture:alpha",
                "summary": "独立任务在同一触发点缺少候选状态检查。",
                "excerpt_sha256": digest,
                "sensitivity_check": "public-safe",
            },
            {
                "id": "evidence-b",
                "task_ref": "task:beta",
                "kind": "confirmed-correction",
                "source_ref": "fixture:beta",
                "summary": "人工纠正再次要求先保留候选状态并等待评审。",
                "excerpt_sha256": digest,
                "sensitivity_check": "public-safe",
            },
        ],
        "pattern": {
            "target_skill": "wise-agent",
            "observed_failure": "重复任务把候选经验当成已确认规则。",
            "expected_behavior": "候选只进入显式评审，不参与普通任务运行时决策。",
            "reuse_scope": "Skill 学习回流候选记录。",
            "proposed_authority": "wise-agent/references/skill-learning-backflow.md",
            "validation": "离线 validator 加 fixture 负例。",
            "evidence_refs": ["evidence-a", "evidence-b"],
        },
        "edits": [
            {
                "id": "edit-a",
                "action": "add",
                "destination": "reference",
                "target": "wise-agent/references/skill-learning-backflow.md",
                "reason": "补充证据批次的脱敏与独立任务门禁。",
                "evidence_refs": ["evidence-a", "evidence-b"],
            }
        ],
        "review": {
            "status": "candidate",
            "owner": "skill-owner",
            "sensitivity_check": "public-safe",
        },
    }


def run_self_test() -> None:
    valid = _valid_fixture()
    result = validate_batch(valid)
    if result["status"] != "PASS":
        raise AssertionError("valid fixture did not pass")

    one_task = copy.deepcopy(valid)
    one_task["evidence"][1]["task_ref"] = one_task["evidence"][0]["task_ref"]
    try:
        validate_batch(one_task)
    except ValidationError:
        pass
    else:
        raise AssertionError("one-task batch was accepted")

    promoted = copy.deepcopy(valid)
    promoted["review"]["status"] = "promoted"
    try:
        validate_batch(promoted)
    except ValidationError:
        pass
    else:
        raise AssertionError("promoted review was accepted")

    raw = copy.deepcopy(valid)
    raw["evidence"][0]["raw_text"] = "private transcript"
    try:
        validate_batch(raw)
    except ValidationError:
        pass
    else:
        raise AssertionError("raw evidence was accepted")
    print("PASS validate-learning-evidence self-test")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="JSON evidence batch")
    parser.add_argument("--self-test", action="store_true", help="run offline validator tests")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            run_self_test()
            return 0
        if args.input is None:
            parser.error("provide an evidence batch JSON file or --self-test")
        result = validate_file(args.input)
    except (ValidationError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
