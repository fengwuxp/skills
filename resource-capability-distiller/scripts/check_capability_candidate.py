#!/usr/bin/env python3
"""Validate a structured resource-capability candidate package.

Input is one local JSON file. The checker is offline and read-only; it checks
structure and review gates, not source truth or domain correctness.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path


ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
STATUSES = {"candidate", "accepted", "rejected"}
READ_STATUSES = {"read", "read-with-limitations", "unavailable"}
DESTINATIONS = {"new-skill", "existing-skill", "reference", "script", "asset", "fixture", "task"}
SOURCE_FIELDS = (
    "source_id",
    "type",
    "title_or_path",
    "source_anchor",
    "version_or_date",
    "read_status",
    "applicable_scope",
    "license_or_usage_boundary",
    "freshness_risk",
    "sensitive_content",
)
ACCEPTED_TEXT_FIELDS = (
    "reuse_scope",
    "version_and_freshness",
    "license_and_privacy_boundary",
    "support_rationale",
)
ACCEPTED_LIST_FIELDS = (
    "trigger_signals",
    "non_trigger_signals",
    "preconditions",
    "inputs",
    "ordered_procedure",
    "tools_and_parameters",
    "branches_and_failures",
    "recovery_or_stop_conditions",
    "outputs",
    "acceptance_evidence",
    "source_anchors",
)


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(nonempty_text(item) for item in value)


def validate(data: object) -> list[str]:
    if not isinstance(data, dict):
        return ["root must be an object"]

    errors: list[str] = []
    overview = data.get("resource_overview")
    if (
        not isinstance(overview, dict)
        or not nonempty_text(overview.get("purpose"))
        or not nonempty_text(overview.get("structure"))
        or not (nonempty_text(overview.get("limitations")) or nonempty_text_list(overview.get("limitations")))
    ):
        errors.append("resource_overview requires purpose, structure, and limitations")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        sources = []
    source_statuses: dict[str, object] = {}
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = [key for key in SOURCE_FIELDS if not nonempty_text(source.get(key))]
        if missing:
            errors.append(f"{label} missing {', '.join(missing)}")
        if source.get("read_status") not in READ_STATUSES:
            errors.append(f"{label}.read_status must be read, read-with-limitations, or unavailable")
        source_id = source.get("source_id")
        if nonempty_text(source_id):
            if source_id in source_statuses:
                errors.append(f"duplicate source_id: {source_id}")
            source_statuses[source_id] = source.get("read_status")

    capabilities = data.get("capabilities")
    if not isinstance(capabilities, list):
        return errors + ["capabilities must be a list"]
    capability_ids: set[str] = set()
    for index, capability in enumerate(capabilities):
        label = f"capabilities[{index}]"
        if not isinstance(capability, dict):
            errors.append(f"{label} must be an object")
            continue
        capability_id = capability.get("capability_id")
        if not isinstance(capability_id, str) or not ID_PATTERN.fullmatch(capability_id):
            errors.append(f"{label}.capability_id must use kebab-case")
        elif capability_id in capability_ids:
            errors.append(f"duplicate capability_id: {capability_id}")
        else:
            capability_ids.add(capability_id)
        status = capability.get("status")
        if status not in STATUSES:
            errors.append(f"{label}.status must be candidate, accepted, or rejected")
        if not nonempty_text(capability.get("stable_responsibility")):
            errors.append(f"{label}.stable_responsibility must be non-empty text")
        anchors = capability.get("source_anchors")
        if not nonempty_text_list(anchors):
            errors.append(f"{label}.source_anchors must be a non-empty text list")
            anchors = []
        for anchor in anchors:
            source_id, separator, claim = anchor.partition("#")
            if not separator or not source_id or not claim:
                errors.append(f"{label}.source_anchors item must use <source_id>#<claim>")
            elif source_id not in source_statuses:
                errors.append(f"{label}.source_anchors references unknown source: {source_id}")
            elif status == "accepted" and source_statuses[source_id] == "unavailable":
                errors.append(f"{label}.source_anchors uses unavailable source: {source_id}")

        if status == "accepted":
            for field in ACCEPTED_LIST_FIELDS:
                if not nonempty_text_list(capability.get(field)):
                    errors.append(f"{label}.{field} must be a non-empty text list")
            for field in ACCEPTED_TEXT_FIELDS:
                if not nonempty_text(capability.get(field)):
                    errors.append(f"{label}.{field} must be non-empty text")
            destination = capability.get("recommended_destination")
            if destination not in DESTINATIONS:
                errors.append(f"{label}.recommended_destination is invalid")
            for field in ("predictive_test", "non_obviousness"):
                assessment = capability.get(field)
                if not isinstance(assessment, dict) or assessment.get("passed") is not True or not nonempty_text(assessment.get("rationale")):
                    errors.append(f"{label}.{field} requires passed=true and rationale")
        elif status == "rejected":
            if not nonempty_text(capability.get("failed_gate")) or not nonempty_text(capability.get("rejection_reason")):
                errors.append(f"{label} rejected entries require failed_gate and rejection_reason")

    return errors


def sample() -> dict:
    return {
        "resource_overview": {
            "purpose": "Turn governed knowledge sources into reusable capability candidates.",
            "structure": "Authority, evidence, procedure, and acceptance layers.",
            "limitations": ["Owner confirmation remains external."],
        },
        "sources": [
            {
                "source_id": "s1",
                "type": "repository-document",
                "title_or_path": "docs/knowledge/README.md",
                "source_anchor": "docs/knowledge/README.md#authority",
                "read_status": "read",
                "version_or_date": "2026-07-23",
                "applicable_scope": "knowledge governance",
                "license_or_usage_boundary": "internal repository",
                "freshness_risk": "recheck when repository rules change",
                "sensitive_content": "none observed",
            }
        ],
        "capabilities": [
            {
                "capability_id": "route-knowledge-evidence",
                "status": "accepted",
                "stable_responsibility": "Route evidence to the smallest authoritative location.",
                "reuse_scope": "knowledge governance tasks",
                "trigger_signals": ["new evidence needs a durable home"],
                "non_trigger_signals": ["one-off summary"],
                "preconditions": ["the target repository authority is readable"],
                "inputs": ["source material", "target authority"],
                "ordered_procedure": ["classify", "route", "verify"],
                "tools_and_parameters": ["repository search with the target authority path"],
                "branches_and_failures": ["stop when authority is unknown"],
                "recovery_or_stop_conditions": ["owner decision is required"],
                "outputs": ["minimal routed change"],
                "acceptance_evidence": ["source anchor and authority check"],
                "source_anchors": ["s1#authority"],
                "version_and_freshness": "valid until repository authority changes",
                "license_and_privacy_boundary": "internal repository; no sensitive content",
                "support_rationale": "The repository authority contract and operating rules agree.",
                "predictive_test": {"passed": True, "rationale": "Routes a new test report without adding a parallel document."},
                "non_obviousness": {"passed": True, "rationale": "Prevents knowledge-base evidence from becoming production authority."},
                "recommended_destination": "existing-skill",
            },
            {
                "capability_id": "summarize-anything",
                "status": "rejected",
                "stable_responsibility": "Summarize arbitrary content.",
                "source_anchors": ["s1#scope"],
                "failed_gate": "non-obviousness",
                "rejection_reason": "Generic summarization is not a distinct reusable capability.",
            },
        ],
    }


def run_self_test() -> int:
    failures: list[str] = []
    valid = sample()
    if errors := validate(valid):
        failures.append("valid sample failed: " + "; ".join(errors))
    invalid = deepcopy(valid)
    invalid["capabilities"][0].pop("branches_and_failures")
    if not any("branches_and_failures" in item for item in validate(invalid)):
        failures.append("missing accepted field was not rejected")
    invalid = deepcopy(valid)
    invalid["capabilities"][0]["predictive_test"]["passed"] = False
    if not any("predictive_test" in item for item in validate(invalid)):
        failures.append("failed predictive test was accepted")
    invalid = deepcopy(valid)
    invalid["capabilities"].append(deepcopy(invalid["capabilities"][0]))
    if not any("duplicate capability_id" in item for item in validate(invalid)):
        failures.append("duplicate capability id was accepted")
    invalid = deepcopy(valid)
    invalid["sources"][0]["read_status"] = "title_only"
    if not any("read_status" in item for item in validate(invalid)):
        failures.append("title-only source was accepted")
    invalid = deepcopy(valid)
    invalid["capabilities"][0].pop("preconditions")
    if not any("preconditions" in item for item in validate(invalid)):
        failures.append("missing contract field was accepted")
    invalid = deepcopy(valid)
    invalid["sources"][0].pop("type")
    if not any("type" in item for item in validate(invalid)):
        failures.append("missing source field was accepted")
    invalid = deepcopy(valid)
    invalid["capabilities"][0]["source_anchors"] = ["missing-source#claim"]
    if not any("unknown source" in item for item in validate(invalid)):
        failures.append("unknown source anchor was accepted")
    invalid = deepcopy(valid)
    invalid["sources"][0]["read_status"] = "unavailable"
    if not any("unavailable source" in item for item in validate(invalid)):
        failures.append("accepted capability used an unavailable source")
    invalid = deepcopy(valid)
    invalid["capabilities"][0]["stable_responsibility"] = True
    if not any("stable_responsibility" in item for item in validate(invalid)):
        failures.append("non-text responsibility was accepted")
    invalid = deepcopy(valid)
    invalid["capabilities"][0]["ordered_procedure"] = [""]
    if not any("ordered_procedure" in item for item in validate(invalid)):
        failures.append("empty list item was accepted")
    if failures:
        print("FAIL resource capability candidate self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK resource capability candidate self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="校验资源炼技结构化候选包")
    parser.add_argument("--file", help="待校验的 JSON 文件；未提供时从 stdin 读取")
    parser.add_argument("--self-test", action="store_true", help="运行内置正反例自测")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    try:
        text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
        data = json.loads(text)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR capability candidate check: {error}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        print("FAIL capability candidate check", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("OK capability candidate check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
