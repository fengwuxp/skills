#!/usr/bin/env python3
"""Validate one local requirement-acceptance report.

The checker is offline and read-only. It validates structure, traceability,
evidence sufficiency, and verdict consistency; it does not run tests, inspect
the target system, judge requirement truth, or authorize release.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


BLOCK_PATTERN = re.compile(
    r"```(?P<tag>acceptance-contract|acceptance-criteria|acceptance-evidence|acceptance-verdict)\s*\n"
    r"(?P<body>.*?)```",
    re.DOTALL,
)
RECORD_PATTERNS = {
    "criterion": re.compile(r"\[criterion\]\s*(?P<body>.*?)\s*\[/criterion\]", re.DOTALL),
    "evidence": re.compile(r"\[evidence\]\s*(?P<body>.*?)\s*\[/evidence\]", re.DOTALL),
}
HEX_256 = re.compile(r"[0-9a-f]{64}")

CONTRACT_KEYS = (
    "acceptance_id", "requirement_source", "requirement_version", "requirement_fingerprint",
    "implementation_target", "implementation_version", "scope", "non_goals", "environment",
    "test_data", "risk_level", "requirement_owner", "acceptance_owner", "checker",
    "authorization_boundary", "status",
)
CRITERION_KEYS = (
    "id", "requirement_anchor", "verification_kind", "required", "preconditions", "action",
    "expected", "unacceptable", "owner", "outcome", "evidence_refs", "finding_id",
    "retest_scope", "rationale",
)
EVIDENCE_KEYS = (
    "id", "criterion_ids", "evidence_type", "source", "source_fingerprint", "environment",
    "command_or_method", "result", "captured_at", "producer", "independent_reviewer", "limitations",
)
VERDICT_KEYS = (
    "verdict", "summary", "required_total", "pass_count", "fail_count", "blocked_count",
    "cant_tell_count", "untested_count", "not_applicable_count", "residual_risks", "next_owner",
)

RISKS = {"low", "medium", "high", "critical"}
CONTRACT_STATUSES = {"draft", "ready", "running", "completed", "superseded"}
KINDS = {
    "business-logic", "api-contract", "data-side-effect", "ui-interaction", "visual-fidelity",
    "accessibility", "runtime-observation", "manual-owner",
}
OUTCOMES = {"pass", "fail", "blocked", "cant-tell", "untested", "not-applicable"}
EVIDENCE_TYPES = {
    "test-report", "contract-report", "api-response", "db-state", "message-state", "audit-log",
    "browser-trace", "browser-assertion", "design-context", "runtime-screenshot", "visual-review",
    "accessibility-report", "runtime-metric", "manual-decision",
}
VERDICTS = {"pass", "fail", "blocked", "need-owner"}
EMPTY_MARKERS = {"", "none", "n/a", "na"}
UNRESOLVED_MARKERS = EMPTY_MARKERS | {"tbd", "todo", "pending", "unknown", "latest", "current", "待确认", "待定", "未知"}
COUNT_FIELDS = {
    "pass": "pass_count", "fail": "fail_count", "blocked": "blocked_count",
    "cant-tell": "cant_tell_count", "untested": "untested_count",
    "not-applicable": "not_applicable_count",
}
KIND_EVIDENCE = {
    "business-logic": ({"test-report", "db-state", "audit-log"}, "one-of"),
    "api-contract": ({"contract-report", "api-response"}, "one-of"),
    "data-side-effect": ({"db-state", "message-state", "audit-log"}, "one-of"),
    "ui-interaction": ({"browser-trace", "browser-assertion"}, "one-of"),
    "visual-fidelity": ({"design-context", "runtime-screenshot", "visual-review"}, "all"),
    "accessibility": ({"accessibility-report", "browser-assertion"}, "all"),
    "runtime-observation": ({"runtime-metric", "audit-log"}, "one-of"),
    "manual-owner": ({"manual-decision"}, "all"),
}


class AcceptanceError(ValueError):
    """A user-fixable acceptance contract violation."""


@dataclass(frozen=True)
class AcceptanceParts:
    contract: dict[str, str]
    criteria: list[dict[str, str]]
    evidence: list[dict[str, str]]
    verdict: dict[str, str]


def parse_key_values(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise AcceptanceError(f"无法解析字段行: {line}")
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            raise AcceptanceError(f"字段名不规范: {key}")
        if key in values:
            raise AcceptanceError(f"字段重复: {key}")
        values[key] = value.strip()
    return values


def extract_block(text: str, tag: str) -> str:
    blocks = [match.group("body") for match in BLOCK_PATTERN.finditer(text) if match.group("tag") == tag]
    if len(blocks) != 1:
        raise AcceptanceError(f"必须且只能有一个 {tag} block")
    return blocks[0]


def parse_records(body: str, kind: str) -> list[dict[str, str]]:
    records = [parse_key_values(match.group("body")) for match in RECORD_PATTERNS[kind].finditer(body)]
    if not records:
        raise AcceptanceError(f"至少需要一个 [{kind}] 记录")
    return records


def require_keys(values: dict[str, str], keys: tuple[str, ...], scope: str) -> None:
    missing = [key for key in keys if not values.get(key)]
    if missing:
        raise AcceptanceError(f"{scope} 缺少字段: {', '.join(missing)}")


def split_refs(value: str) -> list[str]:
    if value.strip().lower() in EMPTY_MARKERS:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_contract(contract: dict[str, str]) -> None:
    require_keys(contract, CONTRACT_KEYS, "acceptance contract")
    if contract["requirement_source"].strip().casefold() in UNRESOLVED_MARKERS:
        raise AcceptanceError("requirement_source 必须指向可回读的需求权威")
    if contract["requirement_version"].strip().casefold() in UNRESOLVED_MARKERS:
        raise AcceptanceError("requirement_version 必须是已冻结的需求版本")
    if contract["risk_level"] not in RISKS:
        raise AcceptanceError(f"risk_level 不受支持: {contract['risk_level']}")
    if contract["status"] not in CONTRACT_STATUSES:
        raise AcceptanceError(f"status 不受支持: {contract['status']}")
    if not HEX_256.fullmatch(contract["requirement_fingerprint"]):
        raise AcceptanceError("requirement_fingerprint 必须是 64 位小写十六进制 SHA-256")


def validate_criteria(criteria: list[dict[str, str]]) -> None:
    seen: set[str] = set()
    for index, criterion in enumerate(criteria, start=1):
        scope = f"criterion[{criterion.get('id', index)}]"
        require_keys(criterion, CRITERION_KEYS, scope)
        if criterion["id"] in seen:
            raise AcceptanceError(f"criterion id 重复: {criterion['id']}")
        seen.add(criterion["id"])
        if criterion["verification_kind"] not in KINDS:
            raise AcceptanceError(f"{scope} verification_kind 不受支持")
        if criterion["required"] not in {"true", "false"}:
            raise AcceptanceError(f"{scope} required 必须是 true 或 false")
        if criterion["outcome"] not in OUTCOMES:
            raise AcceptanceError(f"{scope} outcome 不受支持")
        if criterion["outcome"] == "fail" and criterion["finding_id"].lower() in EMPTY_MARKERS:
            raise AcceptanceError(f"{scope} fail 必须引用 finding_id")
        if criterion["outcome"] == "not-applicable" and criterion["required"] == "true":
            raise AcceptanceError(f"{scope} required criterion 不能是 not-applicable")


def validate_evidence(evidence: list[dict[str, str]], criterion_ids: set[str]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for index, item in enumerate(evidence, start=1):
        scope = f"evidence[{item.get('id', index)}]"
        require_keys(item, EVIDENCE_KEYS, scope)
        if item["id"] in indexed:
            raise AcceptanceError(f"evidence id 重复: {item['id']}")
        if item["evidence_type"] not in EVIDENCE_TYPES:
            raise AcceptanceError(f"{scope} evidence_type 不受支持")
        if item["result"] not in {"pass", "fail", "blocked"}:
            raise AcceptanceError(f"{scope} result 不受支持")
        if not HEX_256.fullmatch(item["source_fingerprint"]):
            raise AcceptanceError(f"{scope} source_fingerprint 必须是 64 位小写十六进制 SHA-256")
        refs = split_refs(item["criterion_ids"])
        unknown = sorted(set(refs) - criterion_ids)
        if not refs or unknown:
            raise AcceptanceError(f"{scope} criterion_ids 缺失或未知: {', '.join(unknown) or 'none'}")
        indexed[item["id"]] = item
    return indexed


def validate_links(
    contract: dict[str, str], criteria: list[dict[str, str]], evidence: dict[str, dict[str, str]]
) -> None:
    for criterion in criteria:
        criterion_id = criterion["id"]
        refs = split_refs(criterion["evidence_refs"])
        unknown = sorted(set(refs) - evidence.keys())
        if unknown:
            raise AcceptanceError(f"criterion[{criterion_id}] evidence_refs 未知: {', '.join(unknown)}")
        if criterion["outcome"] == "pass" and not refs:
            raise AcceptanceError(f"criterion[{criterion_id}] pass 缺少 evidence")
        linked = [evidence[ref] for ref in refs]
        if any(criterion_id not in split_refs(item["criterion_ids"]) for item in linked):
            raise AcceptanceError(f"criterion[{criterion_id}] evidence 未反向引用该 criterion")
        if criterion["outcome"] == "fail":
            if not any(item["result"] == "fail" for item in linked):
                raise AcceptanceError(f"criterion[{criterion_id}] fail 缺少 fail evidence")
            continue
        if criterion["outcome"] != "pass":
            continue
        conflicting_results = sorted({item["result"] for item in linked} - {"pass"})
        if conflicting_results:
            raise AcceptanceError(
                f"criterion[{criterion_id}] pass 关联了 {', '.join(conflicting_results)} evidence"
            )
        types = {item["evidence_type"] for item in linked if item["result"] == "pass"}
        required_types, rule = KIND_EVIDENCE[criterion["verification_kind"]]
        sufficient = bool(types & required_types) if rule == "one-of" else required_types <= types
        if not sufficient:
            raise AcceptanceError(
                f"criterion[{criterion_id}] {criterion['verification_kind']} evidence 不充分"
            )
        if contract["risk_level"] in {"high", "critical"} and criterion["required"] == "true":
            for item in linked:
                reviewer = item["independent_reviewer"].strip().casefold()
                if reviewer in EMPTY_MARKERS or reviewer == item["producer"].strip().casefold():
                    raise AcceptanceError(f"evidence[{item['id']}] 缺少 independent_reviewer")


def parse_count(verdict: dict[str, str], field: str) -> int:
    try:
        value = int(verdict[field])
    except ValueError as error:
        raise AcceptanceError(f"{field} 必须是非负整数") from error
    if value < 0:
        raise AcceptanceError(f"{field} 必须是非负整数")
    return value


def expected_verdict(criteria: list[dict[str, str]]) -> str:
    required = [item for item in criteria if item["required"] == "true"]
    outcomes = {item["outcome"] for item in required}
    if "fail" in outcomes:
        return "fail"
    if outcomes & {"blocked", "untested"}:
        return "blocked"
    if "cant-tell" in outcomes:
        return "need-owner"
    return "pass"


def validate_verdict(verdict: dict[str, str], criteria: list[dict[str, str]]) -> None:
    require_keys(verdict, VERDICT_KEYS, "acceptance verdict")
    if verdict["verdict"] not in VERDICTS:
        raise AcceptanceError(f"verdict 不受支持: {verdict['verdict']}")
    counts = Counter(item["outcome"] for item in criteria)
    required_total = sum(item["required"] == "true" for item in criteria)
    if required_total == 0:
        raise AcceptanceError("至少需要一个 required criterion")
    if parse_count(verdict, "required_total") != required_total:
        raise AcceptanceError("required_total 与 criteria 不一致")
    for outcome, field in COUNT_FIELDS.items():
        if parse_count(verdict, field) != counts[outcome]:
            raise AcceptanceError(f"{field} 与 criteria 不一致")
    expected = expected_verdict(criteria)
    if verdict["verdict"] != expected:
        raise AcceptanceError(f"verdict 应为 {expected}，当前为 {verdict['verdict']}")


def parse_report(text: str) -> AcceptanceParts:
    contract = parse_key_values(extract_block(text, "acceptance-contract"))
    criteria = parse_records(extract_block(text, "acceptance-criteria"), "criterion")
    evidence = parse_records(extract_block(text, "acceptance-evidence"), "evidence")
    verdict = parse_key_values(extract_block(text, "acceptance-verdict"))
    validate_contract(contract)
    validate_criteria(criteria)
    indexed_evidence = validate_evidence(evidence, {item["id"] for item in criteria})
    validate_links(contract, criteria, indexed_evidence)
    validate_verdict(verdict, criteria)
    return AcceptanceParts(contract, criteria, evidence, verdict)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="local Markdown requirement-acceptance report")
    parser.add_argument("--require-pass", action="store_true", help="return non-zero unless the report verdict is pass")
    args = parser.parse_args()
    path = Path(args.file)
    try:
        parts = parse_report(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, AcceptanceError) as error:
        print(f"FAIL requirement acceptance {path}: {error}", file=sys.stderr)
        return 2
    verdict = parts.verdict["verdict"]
    if args.require_pass and verdict != "pass":
        print(f"FAIL requirement acceptance gate {path}: verdict={verdict}", file=sys.stderr)
        return 1
    print(f"VALID requirement acceptance report: {path} verdict={verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
