#!/usr/bin/env python3
"""Validate payment behavior-case coverage and handoff contracts.

This checker validates local JSON only. It does not run a model or access the
network. With --prepare-eval-batches it writes or replaces two JSON files only
inside the explicit output directory; otherwise it does not write files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = ROOT / "test-prompts.json"
PUBLIC_CORE_CASES_FILE = ROOT / "fixtures" / "public-core-behavior-cases.json"
METHOD_CARDS = ROOT / "references" / "payment-method-cards.md"
METHODS = {f"M{index:02d}" for index in range(1, 10)}
KINDS = {"should_trigger", "should_ask", "should_stop", "should_not_trigger"}
DECISIONS = {"answer", "ask", "stop", "pending", "route"}
PUBLIC_CORE_VERSION = 1
PUBLIC_CORE_CONTRACT_SHA256 = "dd86cdc6a7d82753cbd5b27261137aec3835f6b0745634387eca75f746fd6ab8"
PUBLIC_CORE_PROVENANCE_BY_ID = {
    "object-layers-and-retry-history": "candidate-comparison",
    "late-payout-failure": "candidate-comparison",
    "duplicate-out-of-order-events": "candidate-comparison",
    "multi-party-funds-responsibility": "candidate-comparison",
    "refund-dispute-double-compensation": "candidate-comparison",
    "reconciliation-schema-change": "candidate-comparison",
    "sandbox-production-evidence": "candidate-comparison",
    "adjacent-non-payment-state": "candidate-comparison",
    "connected-account-scope-mismatch": "post-merge-forward",
    "report-schema-and-period-balance": "post-merge-forward",
    "ordinary-content-state": "post-merge-forward",
}
PUBLIC_CORE_BATCH_IDS = {"candidate-comparison", "post-merge-forward"}
PUBLIC_CORE_CONTRACT_FIELDS = (
    "version",
    "rubric",
    "release_gate",
    "eval_batches",
    "cases",
)


def audit_cases(data: object) -> list[str]:
    if not isinstance(data, list) or not data:
        return ["root must be a non-empty array"]

    failures: list[str] = []
    seen_ids: set[str] = set()
    covered_methods: set[str] = set()
    negative_routes: set[str] = set()
    negative_boundaries: set[str] = set()

    for index, case in enumerate(data, start=1):
        label = f"case[{index}]"
        if not isinstance(case, dict):
            failures.append(f"{label}: must be an object")
            continue

        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            failures.append(f"{label}: id must be a non-empty string")
        elif case_id in seen_ids:
            failures.append(f"{label}: duplicate id {case_id}")
        else:
            seen_ids.add(case_id)

        query = case.get("query")
        if not isinstance(query, str) or not query.strip():
            failures.append(f"{label}: query must be a non-empty string")

        kind = case.get("kind")
        if kind not in KINDS:
            failures.append(f"{label}: kind must be one of {sorted(KINDS)}")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            failures.append(f"{label}: expected must be an object")
            continue

        skill = expected.get("skill")
        decision = expected.get("decision")
        if not isinstance(skill, str) or not skill.strip():
            failures.append(f"{label}: expected.skill must be a non-empty string")
        if decision not in DECISIONS:
            failures.append(f"{label}: expected.decision must be one of {sorted(DECISIONS)}")

        method = expected.get("method")
        must_include = expected.get("must_include")
        if kind == "should_not_trigger":
            if skill == "payment-expert":
                failures.append(f"{label}: hard negative cannot select payment-expert")
            if isinstance(skill, str):
                negative_routes.add(skill)
            boundary = case.get("boundary")
            if not isinstance(boundary, str) or not boundary.strip():
                failures.append(f"{label}: hard negative requires boundary")
            else:
                negative_boundaries.add(boundary)
        else:
            if skill != "payment-expert":
                failures.append(f"{label}: payment behavior case must select payment-expert")
            if method not in METHODS:
                failures.append(f"{label}: expected.method must be M01-M09")
            else:
                covered_methods.add(method)
            if not isinstance(must_include, list) or not must_include or not all(
                isinstance(term, str) and term.strip() for term in must_include
            ):
                failures.append(f"{label}: expected.must_include must contain non-empty strings")

    missing_methods = sorted(METHODS - covered_methods)
    if missing_methods:
        failures.append("missing method coverage: " + ", ".join(missing_methods))
    for required_route in ["product-architecture-expert", "senior-software-architect"]:
        if required_route not in negative_routes:
            failures.append(f"missing hard-negative route: {required_route}")
    for required_boundary in [
        "generic-refund",
        "generic-order",
        "generic-account",
        "inventory-ledger",
        "accounting-advice",
    ]:
        if required_boundary not in negative_boundaries:
            failures.append(f"missing hard-negative boundary: {required_boundary}")
    referenced_pressure_tests = set(
        re.findall(r"`(PT-\d{3})`", METHOD_CARDS.read_text(encoding="utf-8"))
    )
    missing_pressure_tests = sorted(referenced_pressure_tests - seen_ids)
    if missing_pressure_tests:
        failures.append("unresolved method-card pressure tests: " + ", ".join(missing_pressure_tests))
    return failures


def public_core_contract_sha256(data: dict[str, object]) -> str:
    contract = {field: data.get(field) for field in PUBLIC_CORE_CONTRACT_FIELDS}
    payload = json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def audit_public_core_cases(data: object) -> list[str]:
    if not isinstance(data, dict):
        return ["public core root must be an object"]

    failures: list[str] = []
    if data.get("version") != PUBLIC_CORE_VERSION:
        failures.append(f"public core version must be {PUBLIC_CORE_VERSION}")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        failures.append("public core cases must be a non-empty array")
        return failures

    seen_ids: set[str] = set()
    for index, case in enumerate(cases, start=1):
        label = f"public_core_case[{index}]"
        if not isinstance(case, dict):
            failures.append(f"{label}: must be an object")
            continue

        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            failures.append(f"{label}: id must be a non-empty string")
        elif case_id in seen_ids:
            failures.append(f"{label}: duplicate id {case_id}")
        else:
            seen_ids.add(case_id)

        provenance = case.get("provenance")
        expected_provenance = PUBLIC_CORE_PROVENANCE_BY_ID.get(case_id)
        if expected_provenance is not None and provenance != expected_provenance:
            failures.append(f"{label}: provenance must be {expected_provenance}")

        for field in ["category", "risk", "prompt"]:
            value = case.get(field)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"{label}: {field} must be a non-empty string")

        criteria = case.get("criteria")
        if not isinstance(criteria, list) or not criteria or not all(
            isinstance(item, str) and item.strip() for item in criteria
        ):
            failures.append(f"{label}: criteria must contain non-empty strings")

    expected_ids = set(PUBLIC_CORE_PROVENANCE_BY_ID)
    missing_ids = sorted(expected_ids - seen_ids)
    unexpected_ids = sorted(seen_ids - expected_ids)
    if missing_ids:
        failures.append("missing public core cases: " + ", ".join(missing_ids))
    if unexpected_ids:
        failures.append("unexpected public core cases: " + ", ".join(unexpected_ids))
    eval_batches = data.get("eval_batches")
    seen_batch_ids: set[str] = set()
    covered_case_ids: set[str] = set()
    if not isinstance(eval_batches, list) or not eval_batches:
        failures.append("public core eval_batches must be a non-empty array")
    else:
        for index, batch in enumerate(eval_batches, start=1):
            label = f"public_core_batch[{index}]"
            if not isinstance(batch, dict):
                failures.append(f"{label}: must be an object")
                continue
            batch_id = batch.get("id")
            if not isinstance(batch_id, str) or not batch_id.strip():
                failures.append(f"{label}: id must be a non-empty string")
            elif batch_id in seen_batch_ids:
                failures.append(f"{label}: duplicate id {batch_id}")
            else:
                seen_batch_ids.add(batch_id)
            case_ids = batch.get("case_ids")
            if not isinstance(case_ids, list) or not 5 <= len(case_ids) <= 8:
                failures.append(f"{label}: case_ids must contain 5 to 8 cases")
                continue
            if len(case_ids) != len(set(case_ids)):
                failures.append(f"{label}: case_ids must be unique")
            unknown_case_ids = sorted(set(case_ids) - expected_ids)
            if unknown_case_ids:
                failures.append(f"{label}: unknown cases: " + ", ".join(unknown_case_ids))
            covered_case_ids.update(case_ids)

    missing_batch_ids = sorted(PUBLIC_CORE_BATCH_IDS - seen_batch_ids)
    unexpected_batch_ids = sorted(seen_batch_ids - PUBLIC_CORE_BATCH_IDS)
    if missing_batch_ids:
        failures.append("missing public core batches: " + ", ".join(missing_batch_ids))
    if unexpected_batch_ids:
        failures.append("unexpected public core batches: " + ", ".join(unexpected_batch_ids))
    uncovered_case_ids = sorted(expected_ids - covered_case_ids)
    if uncovered_case_ids:
        failures.append(
            "public core cases missing from behavior batches: "
            + ", ".join(uncovered_case_ids)
        )

    actual_sha256 = public_core_contract_sha256(data)
    if actual_sha256 != PUBLIC_CORE_CONTRACT_SHA256:
        failures.append(
            "public core contract sha256 mismatch: "
            f"expected {PUBLIC_CORE_CONTRACT_SHA256}, got {actual_sha256}"
        )
    return failures


def build_public_core_eval_batches(data: dict[str, object]) -> dict[str, dict[str, object]]:
    failures = audit_public_core_cases(data)
    if failures:
        raise ValueError("invalid public core behavior contract: " + "; ".join(failures))

    cases_by_id = {case["id"]: case for case in data["cases"]}
    return {
        batch["id"]: {
            "version": PUBLIC_CORE_VERSION,
            "batch_id": batch["id"],
            "description": f"payment-expert public core regression: {batch['id']}",
            "source_fixture": "payment-expert/fixtures/public-core-behavior-cases.json",
            "rubric": deepcopy(data["rubric"]),
            "release_gate": deepcopy(data["release_gate"]),
            "cases": [deepcopy(cases_by_id[case_id]) for case_id in batch["case_ids"]],
        }
        for batch in data["eval_batches"]
    }


def write_public_core_eval_batches(
    data: dict[str, object], output_dir: Path
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for batch_id, batch in build_public_core_eval_batches(data).items():
        output = output_dir / f"{batch_id}.json"
        output.write_text(
            json.dumps(batch, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        written.append(output)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepare-eval-batches",
        type=Path,
        metavar="OUTPUT_DIR",
        help="write or replace only candidate-comparison.json and post-merge-forward.json",
    )
    args = parser.parse_args()

    try:
        data = json.loads(CASES_FILE.read_text(encoding="utf-8"))
        public_core_data = json.loads(PUBLIC_CORE_CASES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL payment behavior cases: {exc}")
        return 1

    failures = audit_cases(data) + audit_public_core_cases(public_core_data)
    if failures:
        print("FAIL payment behavior cases")
        for failure in failures:
            print(f"- {failure}")
        return 1

    if args.prepare_eval_batches is not None:
        try:
            outputs = write_public_core_eval_batches(
                public_core_data, args.prepare_eval_batches
            )
        except OSError as exc:
            print(f"FAIL payment public core behavior batches: {exc}")
            return 1
        for output in outputs:
            print(f"OK payment public core behavior batch: {output}")
        return 0

    print(
        "OK payment behavior cases: "
        f"{len(data)} method cases and {len(public_core_data['cases'])} public core cases"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
