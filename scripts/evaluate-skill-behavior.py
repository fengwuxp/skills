#!/usr/bin/env python3
"""Prepare, blind, and score offline Skill behavior comparisons.

The script never invokes an Agent or accesses the network. It reads only the
explicit case, response, score, and key files, and writes only explicit output
paths. Response collection and judging remain separate, reviewable steps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "fixtures" / "skill-eval" / "behavior-cases.json"
CONDITIONS = ("baseline", "candidate")
LABELS = ("A", "B")
DIMENSIONS = ("correctness", "autonomy", "actionability", "safety", "concision")
RISKS = ("low", "medium", "high")


class ContractError(ValueError):
    """Raised when an evaluation artifact violates the public contract."""


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractError(f"{path}: expected a JSON object")
    return data


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            row = json.loads(raw_line)
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
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label}: expected a non-empty string")
    return value.strip()


def _case_digest(case_data: dict[str, Any]) -> str:
    payload = {
        "version": case_data["version"],
        "rubric": case_data["rubric"],
        "release_gate": case_data["release_gate"],
        "cases": case_data["cases"],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_cases(data: dict[str, Any]) -> None:
    if data.get("version") != 1:
        raise ContractError("cases: version must be 1")
    cases = data.get("cases")
    if not isinstance(cases, list) or not 5 <= len(cases) <= 8:
        raise ContractError("cases: expected 5 to 8 behavior cases")

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
    if any(not isinstance(value, (int, float)) or value <= 0 for value in weights.values()):
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
    for field in ("max_correctness_regression", "max_safety_regression"):
        value = gate.get(field)
        if not isinstance(value, (int, float)) or value < 0:
            raise ContractError(f"release_gate.{field}: expected a non-negative number")


def build_plan(case_data: dict[str, Any], trials: int) -> list[dict[str, Any]]:
    validate_cases(case_data)
    if not isinstance(trials, int) or trials < 1:
        raise ContractError("trials: expected a positive integer")
    return [
        {
            "case_id": case["id"],
            "trial": trial,
            "condition": condition,
            "prompt": case["prompt"],
            "risk": case["risk"],
            "criteria": case["criteria"],
        }
        for case in case_data["cases"]
        for trial in range(1, trials + 1)
        for condition in CONDITIONS
    ]


def blind_responses(
    case_data: dict[str, Any], response_rows: list[dict[str, Any]], *, seed: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_cases(case_data)
    cases_by_id = {case["id"]: case for case in case_data["cases"]}
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
        _non_empty_string(row.get("response"), f"responses[{index}].response")
        runner = _non_empty_string(row.get("runner"), f"responses[{index}].runner")
        model = _non_empty_string(row.get("model"), f"responses[{index}].model")
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
            baseline_label = "A" if rng.randrange(2) == 0 else "B"
            candidate_label = "B" if baseline_label == "A" else "A"
            labels = {baseline_label: "baseline", candidate_label: "candidate"}
            pair_id = f"{case['id']}:{trial}"
            tasks.append(
                {
                    "pair_id": pair_id,
                    "case_id": case["id"],
                    "trial": trial,
                    "prompt": case["prompt"],
                    "risk": case["risk"],
                    "criteria": case["criteria"],
                    "responses": [
                        {"label": label, "text": pair[labels[label]]["response"]}
                        for label in LABELS
                    ],
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
    return tasks, key


def score_judgments(
    case_data: dict[str, Any], score_rows: list[dict[str, Any]], key: dict[str, Any]
) -> dict[str, Any]:
    validate_cases(case_data)
    if key.get("version") != 1 or key.get("case_sha256") != _case_digest(case_data):
        raise ContractError("key: version or case digest does not match the selected cases")
    key_pairs = key.get("pairs")
    if not isinstance(key_pairs, list) or not key_pairs:
        raise ContractError("key.pairs: expected a non-empty list")
    _non_empty_string(key.get("runner"), "key.runner")
    _non_empty_string(key.get("model"), "key.model")

    mappings = {}
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
        trial_sets[case_id].add(trial)

    first_trials = next(iter(trial_sets.values()))
    if not first_trials or any(trials != first_trials for trials in trial_sets.values()):
        raise ContractError("key.pairs: every case must contain the same non-empty trial set")
    if first_trials != set(range(1, max(first_trials) + 1)):
        raise ContractError("key.pairs: trials must be contiguous and start at 1")

    scale = case_data["rubric"]["scale"]
    scores_by_pair: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for index, row in enumerate(score_rows):
        pair_id = _non_empty_string(row.get("pair_id"), f"scores[{index}].pair_id")
        if pair_id not in mappings:
            raise ContractError(f"scores[{index}].pair_id: unknown pair {pair_id}")
        label = row.get("label")
        if label not in LABELS:
            raise ContractError(f"scores[{index}].label: expected A or B")
        if label in scores_by_pair[pair_id]:
            raise ContractError(f"scores: duplicate {pair_id} label {label}")
        for dimension in DIMENSIONS:
            value = row.get(dimension)
            if not isinstance(value, (int, float)) or not scale["min"] <= value <= scale["max"]:
                raise ContractError(
                    f"scores[{index}].{dimension}: expected {scale['min']} to {scale['max']}"
                )
        if not isinstance(row.get("blocker"), bool):
            raise ContractError(f"scores[{index}].blocker: expected a boolean")
        scores_by_pair[pair_id][label] = row

    aggregates = {
        condition: {dimension: [] for dimension in DIMENSIONS} | {"blockers": 0}
        for condition in CONDITIONS
    }
    pair_condition_scores: dict[str, dict[str, dict[str, float]]] = {}
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

    gate = case_data["release_gate"]
    reasons = []
    if summaries["candidate"]["blockers"]:
        reasons.append("candidate has blocking findings")
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
    for pair_id in mappings:
        case_id = pair_id.rsplit(":", 1)[0]
        if cases_by_id[case_id]["risk"] != "high":
            continue
        pair_scores = pair_condition_scores[pair_id]
        baseline_score = sum(pair_scores["baseline"][item] * weights[item] for item in DIMENSIONS)
        candidate_score = sum(pair_scores["candidate"][item] * weights[item] for item in DIMENSIONS)
        if candidate_score < baseline_score:
            reasons.append(f"candidate high-risk {pair_id} weighted_score regressed")
    if gate.get("mode", "improvement") == "improvement":
        if summaries["candidate"]["weighted_score"] <= summaries["baseline"]["weighted_score"]:
            reasons.append("candidate weighted_score did not improve")
    elif summaries["candidate"]["weighted_score"] < summaries["baseline"]["weighted_score"]:
        reasons.append("candidate weighted_score regressed")

    return {
        "version": 1,
        "passed": not reasons,
        "reasons": reasons,
        "runner": key.get("runner"),
        "model": key.get("model"),
        "rubric": case_data["rubric"],
        "release_gate": gate,
        "conditions": summaries,
    }


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
            "runner": "self-test-runner",
            "model": "self-test-model",
        }
        for index, item in enumerate(build_plan(case_data, 1), start=1)
    ]
    tasks, key = blind_responses(case_data, responses, seed=731)
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
                    "notes": "self-test",
                }
            )
    report = score_judgments(case_data, scores, key)
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
    regressed_report = score_judgments(case_data, regressed_scores, key)
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
    weighted_regressed_scores = [dict(row) for row in scores]
    for row in weighted_regressed_scores:
        if row["pair_id"] == high_risk_pair["pair_id"] and row["label"] == candidate_label:
            row["autonomy"] = 1
            row["actionability"] = 1
            row["concision"] = 1
    weighted_regressed_report = score_judgments(case_data, weighted_regressed_scores, key)
    if weighted_regressed_report["passed"] or not any(
        "high-risk" in reason and "weighted_score regressed" in reason
        for reason in weighted_regressed_report["reasons"]
    ):
        raise SystemExit("self-test failed: high-risk weighted regression was hidden by aggregate scores")
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
            report = score_judgments(case_data, read_jsonl(args.scores), load_json(args.key))
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
