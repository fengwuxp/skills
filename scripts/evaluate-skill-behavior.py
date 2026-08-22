#!/usr/bin/env python3
"""Prepare, blind, and score offline Skill behavior comparisons.

The script never invokes an Agent or accesses the network. It reads only the
explicit evaluation artifacts and source/input files declared by the selected
case contract, and writes only explicit output paths. Responses may include
redacted execution evidence. Collection and judging remain separate,
reviewable steps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "fixtures" / "skill-eval" / "behavior-cases.json"
CONDITIONS = ("baseline", "candidate")
LABELS = ("A", "B")
DIMENSIONS = ("correctness", "autonomy", "actionability", "safety", "concision")
RISKS = ("low", "medium", "high")
EXECUTION_EVIDENCE_PATTERN = re.compile(
    r"^(?:(?:tool|validation):[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?"
    r"|artifact:[0-9a-f]{64}):(passed|failed|completed|skipped)$"
)
EXECUTION_EVIDENCE_SECRET_PATTERN = re.compile(
    r":(?:sk-|gh[opusr]_|github_pat_|xox[baprs]-)"
)


class ContractError(ValueError):
    """Raised when an evaluation artifact violates the public contract."""


def _reject_json_constant(value: str) -> None:
    raise ContractError(f"invalid JSON constant: {value}")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(
        path.read_text(encoding="utf-8"), parse_constant=_reject_json_constant
    )
    if not isinstance(data, dict):
        raise ContractError(f"{path}: expected a JSON object")
    return data


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            row = json.loads(raw_line, parse_constant=_reject_json_constant)
        except json.JSONDecodeError as exc:
            raise ContractError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ContractError(f"{path}:{line_number}: expected a JSON object")
        rows.append(row)
    if not rows:
        raise ContractError(f"{path}: expected at least one JSONL row")
    return rows


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
        for row in rows
    )
    path.write_text(text, encoding="utf-8")


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label}: expected a non-empty string")
    return value.strip()


def _finite_number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _validate_execution_evidence(row: dict[str, Any], label: str) -> None:
    if "execution_evidence" not in row:
        return
    evidence = row["execution_evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ContractError(f"{label}.execution_evidence: expected a non-empty string list")
    for index, item in enumerate(evidence):
        item_label = f"{label}.execution_evidence[{index}]"
        value = _non_empty_string(item, item_label)
        if (
            EXECUTION_EVIDENCE_PATTERN.fullmatch(value) is None
            or any(condition in value for condition in CONDITIONS)
            or EXECUTION_EVIDENCE_SECRET_PATTERN.search(value) is not None
        ):
            raise ContractError(
                f"{item_label}: expected a safe summary "
                "tool:id:status, validation:id:status, or artifact:sha256:status"
            )


def _case_digest(case_data: dict[str, Any]) -> str:
    payload = {
        "version": case_data["version"],
        "rubric": case_data["rubric"],
        "release_gate": case_data["release_gate"],
        "cases": case_data["cases"],
    }
    if "source_profiles" in case_data:
        payload["source_profiles"] = case_data["source_profiles"]
    if "input_profile" in case_data:
        payload["input_profile"] = case_data["input_profile"]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _blind_digest(rows: list[dict[str, Any]]) -> str:
    payload = [{key: value for key, value in row.items() if key != "blind_sha256"} for row in rows]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def source_set_digest(paths: Sequence[str]) -> str:
    digest = hashlib.sha256()
    root = ROOT.resolve()
    for path in paths:
        relative_path = Path(path)
        if relative_path.is_absolute() or ".." in relative_path.parts or not path:
            raise ContractError(f"source profile path must stay under the repository root: {path!r}")
        try:
            source_path = (ROOT / relative_path).resolve(strict=True)
            source_path.relative_to(root)
        except (OSError, ValueError) as exc:
            raise ContractError(
                f"source profile path must stay under the repository root: {path!r}"
            ) from exc
        if not source_path.is_file():
            raise ContractError(f"source profile path is not a file: {path}")
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update(source_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def input_set_digest(root: str | Path, paths: Sequence[str]) -> str:
    input_root = Path(root)
    if not input_root.is_absolute():
        raise ContractError("input_profile.root: expected an absolute directory")
    try:
        input_root = input_root.resolve(strict=True)
    except OSError as exc:
        raise ContractError("input_profile.root: expected an existing directory") from exc
    if not input_root.is_dir():
        raise ContractError("input_profile.root: expected an existing directory")

    digest = hashlib.sha256()
    for path in paths:
        relative_path = Path(path)
        if relative_path.is_absolute() or ".." in relative_path.parts or not path:
            raise ContractError(f"input profile path must stay under input root: {path!r}")
        try:
            input_path = (input_root / relative_path).resolve(strict=True)
            input_path.relative_to(input_root)
        except (OSError, ValueError) as exc:
            raise ContractError(
                f"input profile path must stay under input root: {path!r}"
            ) from exc
        if not input_path.is_file():
            raise ContractError(f"input profile path is not a file: {path}")
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update(input_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def validate_source_profiles(data: dict[str, Any]) -> None:
    profiles = data.get("source_profiles")
    if profiles is None:
        return
    if not isinstance(profiles, dict) or set(profiles) != set(CONDITIONS):
        raise ContractError("source_profiles: expected baseline and candidate")
    for condition in CONDITIONS:
        profile = profiles[condition]
        if not isinstance(profile, dict) or set(profile) != {"id", "paths", "sha256"}:
            raise ContractError(
                f"source_profiles.{condition}: expected id, paths, and sha256"
            )
        _non_empty_string(profile.get("id"), f"source_profiles.{condition}.id")
        paths = profile.get("paths")
        if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
            raise ContractError(f"source_profiles.{condition}.paths: expected a string list")
        if len(paths) != len(set(paths)):
            raise ContractError(f"source_profiles.{condition}.paths: duplicate path")
        expected_sha256 = profile.get("sha256")
        if (
            not isinstance(expected_sha256, str)
            or len(expected_sha256) != 64
            or expected_sha256.lower() != expected_sha256
        ):
            raise ContractError(f"source_profiles.{condition}.sha256: expected lowercase SHA-256")
        try:
            int(expected_sha256, 16)
        except ValueError as exc:
            raise ContractError(
                f"source_profiles.{condition}.sha256: expected lowercase SHA-256"
            ) from exc
        actual_sha256 = source_set_digest(paths)
        if actual_sha256 != expected_sha256:
            raise ContractError(
                f"source_profiles.{condition}: source set changed "
                f"expected={expected_sha256} actual={actual_sha256}"
            )


def validate_input_profile(data: dict[str, Any]) -> None:
    profile = data.get("input_profile")
    if profile is None:
        return
    if not isinstance(profile, dict) or set(profile) != {"id", "root", "paths", "sha256"}:
        raise ContractError("input_profile: expected id, root, paths, and sha256")
    _non_empty_string(profile.get("id"), "input_profile.id")
    root = _non_empty_string(profile.get("root"), "input_profile.root")
    paths = profile.get("paths")
    if (
        not isinstance(paths, list)
        or not paths
        or any(not isinstance(path, str) for path in paths)
    ):
        raise ContractError("input_profile.paths: expected a non-empty string list")
    if len(paths) != len(set(paths)):
        raise ContractError("input_profile.paths: duplicate path")
    expected_sha256 = profile.get("sha256")
    if (
        not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or expected_sha256.lower() != expected_sha256
    ):
        raise ContractError("input_profile.sha256: expected lowercase SHA-256")
    try:
        int(expected_sha256, 16)
    except ValueError as exc:
        raise ContractError("input_profile.sha256: expected lowercase SHA-256") from exc
    actual_sha256 = input_set_digest(root, paths)
    if actual_sha256 != expected_sha256:
        raise ContractError(
            "input_profile: input set changed "
            f"expected={expected_sha256} actual={actual_sha256}"
        )


def _input_binding(profile: dict[str, Any]) -> dict[str, str]:
    return {"id": profile["id"], "sha256": profile["sha256"]}


def _reject_external_input_path(
    text: str, label: str, profile: dict[str, Any]
) -> None:
    root = Path(profile["root"])
    markers = {str(root), str(root.resolve(strict=True))}
    for path in profile["paths"]:
        input_path = root / path
        markers.update((path, str(input_path), str(input_path.resolve(strict=True))))
    if any(marker in text for marker in markers):
        raise ContractError(f"{label}: external input path must not enter blind content")


def validate_cases(data: dict[str, Any]) -> None:
    if data.get("version") != 1:
        raise ContractError("cases: version must be 1")
    cases = data.get("cases")
    if not isinstance(cases, list) or not 5 <= len(cases) <= 10:
        raise ContractError("cases: expected 5 to 10 behavior cases")

    seen_ids = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ContractError(f"cases[{index}]: expected an object")
        case_id = _non_empty_string(case.get("id"), f"cases[{index}].id")
        if case_id in seen_ids:
            raise ContractError(f"cases[{index}].id: duplicate {case_id}")
        seen_ids.add(case_id)
        _non_empty_string(case.get("category"), f"cases[{index}].category")
        risk = _non_empty_string(case.get("risk"), f"cases[{index}].risk")
        if risk not in RISKS:
            raise ContractError(f"cases[{index}].risk: expected {', '.join(RISKS)}")
        _non_empty_string(case.get("prompt"), f"cases[{index}].prompt")
        criteria = case.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            raise ContractError(f"cases[{index}].criteria: expected a non-empty list")
        for criterion_index, criterion in enumerate(criteria):
            _non_empty_string(criterion, f"cases[{index}].criteria[{criterion_index}]")

    rubric = data.get("rubric")
    if not isinstance(rubric, dict):
        raise ContractError("rubric: expected an object")
    scale = rubric.get("scale")
    if not isinstance(scale, dict) or scale.get("min") != 1 or scale.get("max") != 5:
        raise ContractError("rubric.scale: expected min=1 and max=5")
    weights = rubric.get("weights")
    if not isinstance(weights, dict) or set(weights) != set(DIMENSIONS):
        raise ContractError(f"rubric.weights: expected dimensions {', '.join(DIMENSIONS)}")
    if any(not _finite_number(value) or value <= 0 for value in weights.values()):
        raise ContractError("rubric.weights: all weights must be positive numbers")
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ContractError("rubric.weights: weights must total 1.0")

    gate = data.get("release_gate")
    if not isinstance(gate, dict):
        raise ContractError("release_gate: expected an object")
    gate_mode = gate.get("mode", "improvement")
    if gate_mode not in ("improvement", "non_regression"):
        raise ContractError("release_gate.mode: expected improvement or non_regression")
    if gate.get("candidate_blockers_must_be_zero") is not True:
        raise ContractError("release_gate: candidate blockers must be zero")
    must_improve = gate.get("candidate_weighted_score_must_improve")
    if must_improve is not (gate_mode == "improvement"):
        raise ContractError("release_gate: weighted score policy must match mode")
    require_auditable = gate.get("require_auditable_judgments", False)
    if not isinstance(require_auditable, bool):
        raise ContractError("release_gate.require_auditable_judgments: expected a boolean")
    high_risk_min_pass_rate = gate.get("high_risk_candidate_criteria_min_pass_rate")
    if high_risk_min_pass_rate is not None and (
        isinstance(high_risk_min_pass_rate, bool)
        or not _finite_number(high_risk_min_pass_rate)
        or not 0 < high_risk_min_pass_rate <= 1
    ):
        raise ContractError(
            "release_gate.high_risk_candidate_criteria_min_pass_rate: "
            "expected a number greater than 0 and at most 1"
        )
    if high_risk_min_pass_rate is not None and not require_auditable:
        raise ContractError(
            "release_gate.high_risk_candidate_criteria_min_pass_rate: "
            "requires auditable judgments"
        )
    for field in ("max_correctness_regression", "max_safety_regression"):
        value = gate.get(field)
        if not _finite_number(value) or value < 0:
            raise ContractError(f"release_gate.{field}: expected a non-negative number")
    validate_source_profiles(data)
    validate_input_profile(data)
    input_profile = data.get("input_profile")
    if isinstance(input_profile, dict):
        for index, case in enumerate(cases):
            _reject_external_input_path(
                case["id"], f"cases[{index}].id", input_profile
            )
            _reject_external_input_path(
                case["prompt"], f"cases[{index}].prompt", input_profile
            )
            for criterion_index, criterion in enumerate(case["criteria"]):
                _reject_external_input_path(
                    criterion,
                    f"cases[{index}].criteria[{criterion_index}]",
                    input_profile,
                )


def build_plan(case_data: dict[str, Any], trials: int) -> list[dict[str, Any]]:
    validate_cases(case_data)
    if not isinstance(trials, int) or trials < 1:
        raise ContractError("trials: expected a positive integer")
    source_profiles = case_data.get("source_profiles")
    input_profile = case_data.get("input_profile")
    tasks = []
    for case in case_data["cases"]:
        for trial in range(1, trials + 1):
            for condition in CONDITIONS:
                task = {
                    "case_id": case["id"],
                    "trial": trial,
                    "condition": condition,
                    "prompt": case["prompt"],
                    "risk": case["risk"],
                }
                if isinstance(source_profiles, dict) or isinstance(input_profile, dict):
                    task["case_sha256"] = _case_digest(case_data)
                if isinstance(source_profiles, dict):
                    profile = source_profiles[condition]
                    task["source_profile"] = profile["id"]
                    task["source_paths"] = profile["paths"]
                    task["source_sha256"] = profile["sha256"]
                if isinstance(input_profile, dict):
                    task["input_profile"] = input_profile["id"]
                    task["input_root"] = input_profile["root"]
                    task["input_paths"] = input_profile["paths"]
                    task["input_sha256"] = input_profile["sha256"]
                tasks.append(task)
    return tasks


def blind_responses(
    case_data: dict[str, Any], response_rows: list[dict[str, Any]], *, seed: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_cases(case_data)
    cases_by_id = {case["id"]: case for case in case_data["cases"]}
    source_profiles = case_data.get("source_profiles")
    input_profile = case_data.get("input_profile")
    indexed: dict[tuple[str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    profiles = set()

    for index, row in enumerate(response_rows):
        case_id = _non_empty_string(row.get("case_id"), f"responses[{index}].case_id")
        if case_id not in cases_by_id:
            raise ContractError(f"responses[{index}].case_id: unknown case {case_id}")
        trial = row.get("trial")
        if not isinstance(trial, int) or trial < 1:
            raise ContractError(f"responses[{index}].trial: expected a positive integer")
        condition = row.get("condition")
        if condition not in CONDITIONS:
            raise ContractError(f"responses[{index}].condition: expected baseline or candidate")
        response = _non_empty_string(row.get("response"), f"responses[{index}].response")
        if isinstance(input_profile, dict):
            _reject_external_input_path(
                response, f"responses[{index}].response", input_profile
            )
        _validate_execution_evidence(row, f"responses[{index}]")
        runner = _non_empty_string(row.get("runner"), f"responses[{index}].runner")
        model = _non_empty_string(row.get("model"), f"responses[{index}].model")
        if isinstance(source_profiles, dict) or isinstance(input_profile, dict):
            case_sha256 = _non_empty_string(
                row.get("case_sha256"), f"responses[{index}].case_sha256"
            )
            if case_sha256 != _case_digest(case_data):
                raise ContractError(
                    f"responses[{index}].case_sha256: does not match the selected cases"
                )
        if isinstance(source_profiles, dict):
            source_sha256 = _non_empty_string(
                row.get("source_sha256"), f"responses[{index}].source_sha256"
            )
            expected_sha256 = source_profiles[condition]["sha256"]
            if source_sha256 != expected_sha256:
                raise ContractError(
                    f"responses[{index}].source_sha256: does not match {condition} source profile"
                )
        if isinstance(input_profile, dict):
            input_sha256 = _non_empty_string(
                row.get("input_sha256"), f"responses[{index}].input_sha256"
            )
            if input_sha256 != input_profile["sha256"]:
                raise ContractError(
                    f"responses[{index}].input_sha256: does not match input profile"
                )
        profiles.add((runner, model))
        pair = indexed[(case_id, trial)]
        if condition in pair:
            raise ContractError(f"responses: duplicate {case_id} trial {trial} {condition}")
        pair[condition] = row

    if len(profiles) != 1:
        raise ContractError("responses: baseline and candidate must use one identical runner/model profile")
    trial_sets = {
        case_id: {trial for observed_case, trial in indexed if observed_case == case_id}
        for case_id in cases_by_id
    }
    first_trials = next(iter(trial_sets.values()))
    if not first_trials or any(trials != first_trials for trials in trial_sets.values()):
        raise ContractError("responses: every case must contain the same non-empty trial set")
    if first_trials != set(range(1, max(first_trials) + 1)):
        raise ContractError("responses: trials must be contiguous and start at 1")

    rng = random.Random(seed)
    tasks = []
    key_pairs = []
    for case in case_data["cases"]:
        for trial in sorted(first_trials):
            pair = indexed.get((case["id"], trial), {})
            if set(pair) != set(CONDITIONS):
                raise ContractError(
                    f"responses: {case['id']} trial {trial} must contain baseline and candidate"
                )
            if len({"execution_evidence" in pair[condition] for condition in CONDITIONS}) != 1:
                raise ContractError(
                    f"responses: {case['id']} trial {trial} execution evidence must be paired"
                )
            baseline_label = "A" if rng.randrange(2) == 0 else "B"
            candidate_label = "B" if baseline_label == "A" else "A"
            labels = {baseline_label: "baseline", candidate_label: "candidate"}
            pair_id = f"{case['id']}:{trial}"
            blinded_responses = []
            for label in LABELS:
                response = {"label": label, "text": pair[labels[label]]["response"]}
                if "execution_evidence" in pair[labels[label]]:
                    response["execution_evidence"] = pair[labels[label]][
                        "execution_evidence"
                    ]
                blinded_responses.append(response)
            tasks.append(
                {
                    "pair_id": pair_id,
                    "case_id": case["id"],
                    "trial": trial,
                    "prompt": case["prompt"],
                    "risk": case["risk"],
                    "criteria": case["criteria"],
                    "responses": blinded_responses,
                }
            )
            key_pairs.append(
                {
                    "pair_id": pair_id,
                    "case_id": case["id"],
                    "trial": trial,
                    "labels": labels,
                }
            )

    runner, model = next(iter(profiles))
    key = {
        "version": 1,
        "case_sha256": _case_digest(case_data),
        "seed": seed,
        "runner": runner,
        "model": model,
        "pairs": key_pairs,
    }
    blind_sha256 = _blind_digest(tasks)
    for task in tasks:
        task["blind_sha256"] = blind_sha256
    key["blind_sha256"] = blind_sha256
    if isinstance(source_profiles, dict):
        key["source_profiles"] = source_profiles
    if isinstance(input_profile, dict):
        key["input_profile"] = _input_binding(input_profile)
    return tasks, key


def score_judgments(
    case_data: dict[str, Any],
    score_rows: list[dict[str, Any]],
    key: dict[str, Any],
    *,
    blind_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    validate_cases(case_data)
    if key.get("version") != 1 or key.get("case_sha256") != _case_digest(case_data):
        raise ContractError("key: version or case digest does not match the selected cases")
    key_pairs = key.get("pairs")
    if not isinstance(key_pairs, list) or not key_pairs:
        raise ContractError("key.pairs: expected a non-empty list")
    _non_empty_string(key.get("runner"), "key.runner")
    _non_empty_string(key.get("model"), "key.model")
    source_profiles = case_data.get("source_profiles")
    if isinstance(source_profiles, dict) and key.get("source_profiles") != source_profiles:
        raise ContractError("key.source_profiles: does not match the selected cases")
    input_profile = case_data.get("input_profile")
    if isinstance(input_profile, dict) and key.get("input_profile") != _input_binding(input_profile):
        raise ContractError("key.input_profile: does not match the selected cases")
    if not blind_rows:
        raise ContractError("blind: required for scoring")
    blind_sha256 = _blind_digest(blind_rows)
    if key.get("blind_sha256") != blind_sha256:
        raise ContractError("key.blind_sha256: does not match the selected blind responses")
    if any(row.get("blind_sha256") != blind_sha256 for row in blind_rows):
        raise ContractError("blind.blind_sha256: does not match the selected blind responses")

    mappings = {}
    pair_trials = {}
    cases_by_id = {case["id"]: case for case in case_data["cases"]}
    trial_sets = {case_id: set() for case_id in cases_by_id}
    for index, pair in enumerate(key_pairs):
        if not isinstance(pair, dict):
            raise ContractError(f"key.pairs[{index}]: expected an object")
        pair_id = _non_empty_string(pair.get("pair_id"), f"key.pairs[{index}].pair_id")
        case_id = _non_empty_string(pair.get("case_id"), f"key.pairs[{index}].case_id")
        if case_id not in cases_by_id:
            raise ContractError(f"key.pairs[{index}].case_id: unknown case {case_id}")
        trial = pair.get("trial")
        if not isinstance(trial, int) or trial < 1:
            raise ContractError(f"key.pairs[{index}].trial: expected a positive integer")
        if pair_id != f"{case_id}:{trial}":
            raise ContractError(f"key.pairs[{index}].pair_id: does not match case_id and trial")
        labels = pair.get("labels")
        if not isinstance(labels, dict) or set(labels) != set(LABELS):
            raise ContractError(f"key.pairs[{index}].labels: expected A and B")
        if set(labels.values()) != set(CONDITIONS):
            raise ContractError(f"key.pairs[{index}].labels: expected baseline and candidate")
        if pair_id in mappings:
            raise ContractError(f"key.pairs[{index}].pair_id: duplicate {pair_id}")
        mappings[pair_id] = labels
        pair_trials[pair_id] = trial
        trial_sets[case_id].add(trial)

    first_trials = next(iter(trial_sets.values()))
    if not first_trials or any(trials != first_trials for trials in trial_sets.values()):
        raise ContractError("key.pairs: every case must contain the same non-empty trial set")
    if first_trials != set(range(1, max(first_trials) + 1)):
        raise ContractError("key.pairs: trials must be contiguous and start at 1")
    seed = key.get("seed")
    if not isinstance(seed, int):
        raise ContractError("key.seed: expected an integer")
    rng = random.Random(seed)
    for case in case_data["cases"]:
        for trial in sorted(first_trials):
            baseline_label = "A" if rng.randrange(2) == 0 else "B"
            expected_labels = {
                baseline_label: "baseline",
                "B" if baseline_label == "A" else "A": "candidate",
            }
            pair_id = f"{case['id']}:{trial}"
            if mappings[pair_id] != expected_labels:
                raise ContractError(f"key.pairs: {pair_id} labels do not match seed")

    scale = case_data["rubric"]["scale"]
    require_auditable = case_data["release_gate"].get(
        "require_auditable_judgments", False
    )
    scores_by_pair: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    judgment_profiles = set()
    for index, row in enumerate(score_rows):
        pair_id = _non_empty_string(row.get("pair_id"), f"scores[{index}].pair_id")
        if pair_id not in mappings:
            raise ContractError(f"scores[{index}].pair_id: unknown pair {pair_id}")
        label = row.get("label")
        if label not in LABELS:
            raise ContractError(f"scores[{index}].label: expected A or B")
        score_blind_sha256 = _non_empty_string(
            row.get("blind_sha256"), f"scores[{index}].blind_sha256"
        )
        if score_blind_sha256 != key["blind_sha256"]:
            raise ContractError(
                f"scores[{index}].blind_sha256: does not match the selected blind responses"
            )
        if require_auditable:
            evaluation_id = _non_empty_string(
                row.get("evaluation_id"), f"scores[{index}].evaluation_id"
            )
            judge = _non_empty_string(row.get("judge"), f"scores[{index}].judge")
            if judge == key["runner"]:
                raise ContractError(
                    f"scores[{index}].judge: independent judge must differ from response runner"
                )
            judge_model = _non_empty_string(
                row.get("judge_model"), f"scores[{index}].judge_model"
            )
            judged_at = _non_empty_string(
                row.get("judged_at"), f"scores[{index}].judged_at"
            )
            try:
                parsed_judged_at = datetime.fromisoformat(judged_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContractError(
                    f"scores[{index}].judged_at: expected an ISO-8601 timestamp"
                ) from exc
            if parsed_judged_at.tzinfo is None:
                raise ContractError(
                    f"scores[{index}].judged_at: expected a timezone-aware timestamp"
                )
            case_id = pair_id.rsplit(":", 1)[0]
            criteria = row.get("criteria")
            expected_criteria = cases_by_id[case_id]["criteria"]
            if (
                not isinstance(criteria, list)
                or len(criteria) != len(expected_criteria)
                or any(not isinstance(passed, bool) for passed in criteria)
            ):
                raise ContractError(
                    f"scores[{index}].criteria: expected {len(expected_criteria)} booleans"
                )
            judgment_profiles.add((evaluation_id, judge, judge_model, judged_at))
        if label in scores_by_pair[pair_id]:
            raise ContractError(f"scores: duplicate {pair_id} label {label}")
        for dimension in DIMENSIONS:
            value = row.get(dimension)
            if not _finite_number(value) or not scale["min"] <= value <= scale["max"]:
                raise ContractError(
                    f"scores[{index}].{dimension}: expected {scale['min']} to {scale['max']}"
                )
        if not isinstance(row.get("blocker"), bool):
            raise ContractError(f"scores[{index}].blocker: expected a boolean")
        scores_by_pair[pair_id][label] = row

    if require_auditable and len(judgment_profiles) != 1:
        raise ContractError(
            "scores: auditable judgments must use one evaluation_id, judge, judge_model, and judged_at"
        )

    aggregates = {
        condition: {dimension: [] for dimension in DIMENSIONS}
        | {"blockers": 0, "criteria_passed": 0, "criteria_total": 0}
        for condition in CONDITIONS
    }
    pair_condition_scores: dict[str, dict[str, dict[str, float]]] = {}
    candidate_criterion_failures: dict[tuple[str, int], set[int]] = defaultdict(set)
    candidate_case_criteria: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for pair_id, labels in mappings.items():
        pair_scores = scores_by_pair.get(pair_id, {})
        if set(pair_scores) != set(LABELS):
            raise ContractError(f"scores: {pair_id} must contain judgments for A and B")
        for label, condition in labels.items():
            row = pair_scores[label]
            pair_condition_scores.setdefault(pair_id, {})[condition] = {
                dimension: float(row[dimension]) for dimension in DIMENSIONS
            }
            for dimension in DIMENSIONS:
                aggregates[condition][dimension].append(float(row[dimension]))
            aggregates[condition]["blockers"] += int(row["blocker"])
            if require_auditable:
                passed_criteria = row["criteria"]
                aggregates[condition]["criteria_passed"] += sum(passed_criteria)
                aggregates[condition]["criteria_total"] += len(passed_criteria)
                if condition == "candidate":
                    case_id = pair_id.rsplit(":", 1)[0]
                    candidate_case_criteria[case_id][0] += sum(passed_criteria)
                    candidate_case_criteria[case_id][1] += len(passed_criteria)
                    for index, passed in enumerate(passed_criteria, start=1):
                        if not passed:
                            candidate_criterion_failures[(case_id, index)].add(
                                pair_trials[pair_id]
                            )

    weights = case_data["rubric"]["weights"]
    summaries = {}
    raw_means = {}
    for condition in CONDITIONS:
        means = {
            dimension: sum(aggregates[condition][dimension])
            / len(aggregates[condition][dimension])
            for dimension in DIMENSIONS
        }
        raw_means[condition] = means
        summaries[condition] = {
            **{dimension: round(value, 4) for dimension, value in means.items()},
            "weighted_score": round(sum(means[item] * weights[item] for item in DIMENSIONS), 4),
            "blockers": aggregates[condition]["blockers"],
            "responses": len(aggregates[condition][DIMENSIONS[0]]),
        }
        if require_auditable:
            summaries[condition]["criteria_passed"] = aggregates[condition][
                "criteria_passed"
            ]
            summaries[condition]["criteria_total"] = aggregates[condition][
                "criteria_total"
            ]
            summaries[condition]["criteria_pass_rate"] = round(
                aggregates[condition]["criteria_passed"]
                / aggregates[condition]["criteria_total"],
                4,
            )

    gate = case_data["release_gate"]
    reasons = []
    if summaries["candidate"]["blockers"]:
        reasons.append("candidate has blocking findings")
    if require_auditable:
        for (case_id, index), failed_trials in candidate_criterion_failures.items():
            if failed_trials == first_trials:
                reasons.append(
                    f"candidate {case_id} criterion {index} failed in all trials"
                )
        high_risk_min_pass_rate = gate.get("high_risk_candidate_criteria_min_pass_rate")
        if high_risk_min_pass_rate is not None:
            for case_id, case in cases_by_id.items():
                if case["risk"] != "high":
                    continue
                passed, total = candidate_case_criteria[case_id]
                pass_rate = passed / total
                if pass_rate + 1e-12 < high_risk_min_pass_rate:
                    reasons.append(
                        f"candidate high-risk {case_id} criteria pass rate "
                        f"{pass_rate:.4f} is below {high_risk_min_pass_rate:.4f}"
                    )
    for dimension, field in (
        ("correctness", "max_correctness_regression"),
        ("safety", "max_safety_regression"),
    ):
        if raw_means["candidate"][dimension] + gate[field] < raw_means["baseline"][dimension]:
            reasons.append(f"candidate {dimension} regressed beyond {gate[field]}")
        for pair_id, labels in mappings.items():
            case_id = pair_id.rsplit(":", 1)[0]
            if cases_by_id[case_id]["risk"] != "high":
                continue
            pair_scores = pair_condition_scores[pair_id]
            if pair_scores["candidate"][dimension] + gate[field] < pair_scores["baseline"][dimension]:
                reasons.append(f"candidate high-risk {case_id} {dimension} regressed beyond {gate[field]}")
    if gate.get("mode", "improvement") == "improvement":
        if summaries["candidate"]["weighted_score"] <= summaries["baseline"]["weighted_score"]:
            reasons.append("candidate weighted_score did not improve")
    elif summaries["candidate"]["weighted_score"] < summaries["baseline"]["weighted_score"]:
        reasons.append("candidate weighted_score regressed")

    report = {
        "version": 1,
        "passed": not reasons,
        "reasons": reasons,
        "runner": key.get("runner"),
        "model": key.get("model"),
        "rubric": case_data["rubric"],
        "release_gate": gate,
        "conditions": summaries,
    }
    report["blind_sha256"] = key["blind_sha256"]
    if isinstance(source_profiles, dict):
        report["source_profiles"] = source_profiles
    if isinstance(input_profile, dict):
        report["input_profile"] = _input_binding(input_profile)
    if require_auditable:
        evaluation_id, judge, judge_model, judged_at = next(iter(judgment_profiles))
        report["judgment"] = {
            "evaluation_id": evaluation_id,
            "judge": judge,
            "judge_model": judge_model,
            "judged_at": judged_at,
        }
    return report


def run_self_test() -> None:
    case_data = load_json(DEFAULT_CASES)
    validate_cases(case_data)
    invalid_risk_cases = json.loads(json.dumps(case_data))
    invalid_risk_cases["cases"][0]["risk"] = "critical"
    try:
        validate_cases(invalid_risk_cases)
    except ContractError:
        pass
    else:
        raise SystemExit("self-test failed: unknown risk level was accepted")
    responses = [
        {
            "case_id": item["case_id"],
            "trial": item["trial"],
            "condition": item["condition"],
            "response": f"fixture response {index}",
            "execution_evidence": [
                f"tool:fixture-{index}:completed",
                f"artifact:{hashlib.sha256(str(index).encode()).hexdigest()}:completed",
            ],
            "runner": "self-test-runner",
            "model": "self-test-model",
        }
        for index, item in enumerate(build_plan(case_data, 1), start=1)
    ]
    tasks, key = blind_responses(case_data, responses, seed=731)
    if any(
        "execution_evidence" not in response
        for task in tasks
        for response in task["responses"]
    ):
        raise SystemExit("self-test failed: execution evidence was not preserved for judging")
    uneven_evidence = [dict(row) for row in responses]
    uneven_evidence[0].pop("execution_evidence")
    try:
        blind_responses(case_data, uneven_evidence, seed=731)
    except ContractError:
        pass
    else:
        raise SystemExit("self-test failed: uneven execution evidence was accepted")
    scores = []
    for pair in key["pairs"]:
        for label, condition in pair["labels"].items():
            score = 4 if condition == "baseline" else 5
            scores.append(
                {
                    "pair_id": pair["pair_id"],
                    "label": label,
                    "correctness": 4,
                    "autonomy": score,
                    "actionability": score,
                    "safety": 4,
                    "concision": score,
                    "blocker": False,
                    "blind_sha256": key["blind_sha256"],
                    "notes": "self-test",
                }
            )
    report = score_judgments(case_data, scores, key, blind_rows=tasks)
    if not report["passed"] or len(tasks) != len(case_data["cases"]):
        raise SystemExit(f"self-test failed: {report}")
    high_risk_ids = {case["id"] for case in case_data["cases"] if case["risk"] == "high"}
    high_risk_pair = next(pair for pair in key["pairs"] if pair["case_id"] in high_risk_ids)
    regressed_scores = [dict(row) for row in scores]
    candidate_label = next(
        label for label, condition in high_risk_pair["labels"].items() if condition == "candidate"
    )
    for row in regressed_scores:
        labels = next(pair["labels"] for pair in key["pairs"] if pair["pair_id"] == row["pair_id"])
        if labels[row["label"]] == "candidate":
            row["correctness"] = 5
            row["safety"] = 5
        if row["pair_id"] == high_risk_pair["pair_id"] and row["label"] == candidate_label:
            row["correctness"] = 1
            row["safety"] = 1
    regressed_report = score_judgments(case_data, regressed_scores, key, blind_rows=tasks)
    if any(
        reason.startswith("candidate correctness regressed")
        or reason.startswith("candidate safety regressed")
        for reason in regressed_report["reasons"]
    ):
        raise SystemExit("self-test failed: aggregate gate unexpectedly caught the isolated regression")
    if regressed_report["passed"] or not any(
        "candidate high-risk" in reason for reason in regressed_report["reasons"]
    ):
        raise SystemExit("self-test failed: high-risk case regression was hidden by aggregate scores")

    strict_case_data = json.loads(json.dumps(case_data))
    strict_case_data["release_gate"].update(
        {
            "mode": "non_regression",
            "candidate_weighted_score_must_improve": False,
            "require_auditable_judgments": True,
            "high_risk_candidate_criteria_min_pass_rate": 0.75,
        }
    )
    strict_responses = [
        {
            "case_id": item["case_id"],
            "trial": item["trial"],
            "condition": item["condition"],
            "response": f"strict fixture response {index}",
            "runner": "self-test-runner",
            "model": "self-test-model",
        }
        for index, item in enumerate(build_plan(strict_case_data, 2), start=1)
    ]
    strict_tasks, strict_key = blind_responses(strict_case_data, strict_responses, seed=731)
    strict_scores = []
    high_risk_id = next(
        case["id"] for case in strict_case_data["cases"] if case["risk"] == "high"
    )
    criteria_by_case = {
        case["id"]: case["criteria"] for case in strict_case_data["cases"]
    }
    for pair in strict_key["pairs"]:
        for label, condition in pair["labels"].items():
            criteria = [True] * len(criteria_by_case[pair["case_id"]])
            if condition == "candidate" and pair["case_id"] == high_risk_id and pair["trial"] == 1:
                criteria = [False] * len(criteria)
            strict_scores.append(
                {
                    "pair_id": pair["pair_id"],
                    "label": label,
                    "correctness": 5,
                    "autonomy": 5,
                    "actionability": 5,
                    "safety": 5,
                    "concision": 5,
                    "blocker": False,
                    "blind_sha256": strict_key["blind_sha256"],
                    "criteria": criteria,
                    "notes": "self-test",
                    "evaluation_id": "self-test-evaluation",
                    "judge": "self-test-judge",
                    "judge_model": "self-test-judge-model",
                    "judged_at": "2026-08-17T00:00:00+00:00",
                }
            )
    strict_report = score_judgments(
        strict_case_data, strict_scores, strict_key, blind_rows=strict_tasks
    )
    if strict_report["passed"] or not any(
        "candidate high-risk" in reason and "criteria pass rate" in reason
        for reason in strict_report["reasons"]
    ):
        raise SystemExit(
            "self-test failed: high-risk per-case criteria threshold was not enforced"
        )
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "report.json"
        write_json(output, report)
        if load_json(output) != report:
            raise SystemExit("self-test failed: JSON output did not round-trip")
    print("OK Skill behavior evaluation self-test")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run deterministic contract checks")
    subparsers = parser.add_subparsers(dest="command")

    validate = subparsers.add_parser("validate", help="validate the behavior case contract")
    validate.add_argument("--cases", type=Path, default=DEFAULT_CASES)

    prepare = subparsers.add_parser("prepare", help="write an identical baseline/candidate task manifest")
    prepare.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    prepare.add_argument("--trials", type=int, default=3)
    prepare.add_argument("--output", type=Path, required=True)

    blind = subparsers.add_parser("blind", help="blind collected response pairs for independent judging")
    blind.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    blind.add_argument("--responses", type=Path, required=True)
    blind.add_argument("--output", type=Path, required=True)
    blind.add_argument("--key-output", type=Path, required=True)
    blind.add_argument("--seed", type=int, default=731)

    score = subparsers.add_parser("score", help="score blind judgments and apply the release gate")
    score.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    score.add_argument("--scores", type=Path, required=True)
    score.add_argument("--key", type=Path, required=True)
    score.add_argument("--blind", type=Path, required=True)
    score.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            run_self_test()
            return 0
        if args.command is None:
            parser.error("a command or --self-test is required")

        case_data = load_json(args.cases)
        if args.command == "validate":
            validate_cases(case_data)
            print(f"OK behavior cases={len(case_data['cases'])}")
            return 0
        if args.command == "prepare":
            write_jsonl(args.output, build_plan(case_data, args.trials))
            print(f"OK wrote {args.output}")
            return 0
        if args.command == "blind":
            tasks, key = blind_responses(case_data, read_jsonl(args.responses), seed=args.seed)
            write_jsonl(args.output, tasks)
            write_json(args.key_output, key)
            print(f"OK wrote {args.output} and {args.key_output}")
            return 0
        if args.command == "score":
            report = score_judgments(
                case_data,
                read_jsonl(args.scores),
                load_json(args.key),
                blind_rows=read_jsonl(args.blind) if args.blind else None,
            )
            if args.output:
                write_json(args.output, report)
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if report["passed"] else 1
    except (ContractError, json.JSONDecodeError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
