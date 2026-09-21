#!/usr/bin/env python3
"""Validate the write-before-change contract for interfaces, methods, and models.

Input: one explicitly supplied JSON contract.
Output: validation result on stdout/stderr.
Writes: none. Network: none.
Failure: non-zero when design ownership, consumer, compatibility, or evidence
boundaries are missing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ITEM_KINDS = {"interface", "method", "model"}
COMPATIBILITY = {"new", "preserve", "change", "delete"}
ADOPTION = {"candidate", "provider-verified", "consumer-adopted", "runtime-accepted", "blocked"}
CLAIM_STATES = {"fact", "inference", "pending", "not_done"}
EVIDENCE_KINDS = {
    "source",
    "test",
    "validator",
    "consumer_compile",
    "runtime",
    "owner_confirmation",
    "independent_review",
}
EVIDENCE_RESULTS = {"pass", "fail", "pending"}


class ContractError(ValueError):
    """Raised when an engineering change contract is not safe to use."""


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ContractError(f"{field} must be a non-empty list")
    values = [_string(item, f"{field}[{index}]") for index, item in enumerate(value)]
    if len(values) != len(set(values)):
        raise ContractError(f"{field} must not contain duplicates")
    return values


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an object")
    return value


def _evidence_refs(value: Any, field: str, evidence: dict[str, dict[str, Any]]) -> list[str]:
    refs = _string_list(value, field)
    for ref in refs:
        if ref not in evidence:
            raise ContractError(f"{field} references unknown evidence {ref!r}")
    return refs


def validate_contract(contract: Any) -> dict[str, Any]:
    root = _object(contract, "contract")
    if root.get("version") != 1:
        raise ContractError("version must be 1")

    task = _object(root.get("task"), "task")
    _string(task.get("objective"), "task.objective")
    _string_list(task.get("write_scope"), "task.write_scope")
    _string_list(task.get("non_goals"), "task.non_goals")
    _string_list(task.get("stop_conditions"), "task.stop_conditions")

    raw_evidence = root.get("evidence")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        raise ContractError("evidence must be a non-empty list")
    evidence: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw_evidence):
        entry = _object(item, f"evidence[{index}]")
        evidence_id = _string(entry.get("id"), f"evidence[{index}].id")
        if evidence_id in evidence:
            raise ContractError(f"evidence id must be unique: {evidence_id}")
        kind = _string(entry.get("kind"), f"evidence[{index}].kind")
        if kind not in EVIDENCE_KINDS:
            raise ContractError(f"evidence[{index}].kind must be one of {sorted(EVIDENCE_KINDS)}")
        result = _string(entry.get("result"), f"evidence[{index}].result")
        if result not in EVIDENCE_RESULTS:
            raise ContractError(f"evidence[{index}].result must be one of {sorted(EVIDENCE_RESULTS)}")
        _string(entry.get("ref"), f"evidence[{index}].ref")
        _string(entry.get("fingerprint"), f"evidence[{index}].fingerprint")
        evidence[evidence_id] = entry

    change = _object(root.get("change"), "change")
    adoption = _string(change.get("adoption"), "change.adoption")
    if adoption not in ADOPTION:
        raise ContractError(f"change.adoption must be one of {sorted(ADOPTION)}")
    items = change.get("items")
    if not isinstance(items, list) or not items:
        raise ContractError("change.items must be a non-empty list")
    item_names: set[str] = set()
    item_evidence: dict[str, set[str]] = {}
    for index, item in enumerate(items):
        entry = _object(item, f"change.items[{index}]")
        kind = _string(entry.get("kind"), f"change.items[{index}].kind")
        if kind not in ITEM_KINDS:
            raise ContractError(f"change.items[{index}].kind must be one of {sorted(ITEM_KINDS)}")
        name = _string(entry.get("name"), f"change.items[{index}].name")
        if name in item_names:
            raise ContractError(f"change item name must be unique: {name}")
        item_names.add(name)
        _string(entry.get("owner"), f"change.items[{index}].owner")
        _string_list(entry.get("consumers"), f"change.items[{index}].consumers")
        _string(entry.get("responsibility"), f"change.items[{index}].responsibility")
        _string_list(entry.get("invariants"), f"change.items[{index}].invariants")
        compatibility = _string(entry.get("compatibility"), f"change.items[{index}].compatibility")
        if compatibility not in COMPATIBILITY:
            raise ContractError(
                f"change.items[{index}].compatibility must be one of {sorted(COMPATIBILITY)}"
            )
        _string(entry.get("reason"), f"change.items[{index}].reason")
        if compatibility in {"change", "delete"}:
            _string(entry.get("compatibility_note"), f"change.items[{index}].compatibility_note")
        refs = _evidence_refs(entry.get("verification_refs"), f"change.items[{index}].verification_refs", evidence)
        item_evidence[name] = set(refs)

    claims = root.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ContractError("claims must be a non-empty list")
    claim_ids: set[str] = set()
    claim_states: set[str] = set()
    for index, claim in enumerate(claims):
        entry = _object(claim, f"claims[{index}]")
        claim_id = _string(entry.get("id"), f"claims[{index}].id")
        if claim_id in claim_ids:
            raise ContractError(f"claim id must be unique: {claim_id}")
        claim_ids.add(claim_id)
        _string(entry.get("text"), f"claims[{index}].text")
        state = _string(entry.get("state"), f"claims[{index}].state")
        if state not in CLAIM_STATES:
            raise ContractError(f"claims[{index}].state must be one of {sorted(CLAIM_STATES)}")
        claim_states.add(state)
        refs = entry.get("evidence_refs", [])
        if state in {"fact", "inference"}:
            refs = _evidence_refs(refs, f"claims[{index}].evidence_refs", evidence)
            results = [evidence[ref]["result"] for ref in refs]
            if state == "fact" and any(result != "pass" for result in results):
                raise ContractError(f"claims[{index}] fact may reference only passing evidence")
            if state == "inference" and "pass" not in results:
                raise ContractError(f"claims[{index}] inference needs at least one passing evidence")
            if state == "inference":
                _string(entry.get("basis"), f"claims[{index}].basis")
        else:
            if refs:
                _evidence_refs(refs, f"claims[{index}].evidence_refs", evidence)
            _string(entry.get("owner"), f"claims[{index}].owner")
            _string(entry.get("reason"), f"claims[{index}].reason")

    passing = [entry for entry in evidence.values() if entry["result"] == "pass"]
    passing_ids = {entry["id"] for entry in passing}
    passing_kinds = {entry["kind"] for entry in passing}
    if adoption == "provider-verified" and not {"source", "test"} <= passing_kinds:
        raise ContractError("provider-verified requires passing source and test evidence")
    if adoption == "consumer-adopted" and not {
        "source",
        "test",
        "consumer_compile",
    } <= passing_kinds:
        raise ContractError(
            "consumer-adopted requires passing source, test and consumer_compile evidence"
        )
    if adoption == "runtime-accepted" and not {
        "source",
        "test",
        "consumer_compile",
        "runtime",
    } <= passing_kinds:
        raise ContractError(
            "runtime-accepted requires passing source, test, consumer_compile and runtime evidence"
        )
    if adoption == "runtime-accepted" and claim_states & {"pending", "not_done"}:
        raise ContractError("runtime-accepted cannot contain pending or not_done claims")
    if adoption == "blocked" and not (
        any(entry["result"] == "fail" for entry in evidence.values())
        or claim_states & {"pending", "not_done"}
    ):
        raise ContractError("blocked requires failed evidence or pending/not_done claims")
    if adoption == "provider-verified" and any(
        not refs & passing_ids for refs in item_evidence.values()
    ):
        raise ContractError("every change item needs at least one passing verification reference")
    if adoption in {"consumer-adopted", "runtime-accepted"} and any(
        not refs & passing_ids for refs in item_evidence.values()
    ):
        raise ContractError("every change item needs at least one passing verification reference")
    required_item_evidence = {
        "consumer-adopted": "consumer_compile",
        "runtime-accepted": "runtime",
    }.get(adoption)
    if required_item_evidence:
        for name, refs in item_evidence.items():
            if not any(
                evidence[ref]["result"] == "pass"
                and evidence[ref]["kind"] == required_item_evidence
                for ref in refs
            ):
                raise ContractError(
                    f"{name} needs passing {required_item_evidence} evidence in verification_refs"
                )
    return root


def _valid_contract() -> dict[str, Any]:
    return {
        "version": 1,
        "task": {
            "objective": "收敛一个查询契约",
            "write_scope": ["src/main", "src/test"],
            "non_goals": ["不新增 HTTP 路由"],
            "stop_conditions": ["发现未登记消费者时停止"],
        },
        "change": {
            "adoption": "provider-verified",
            "items": [
                {
                    "kind": "interface",
                    "name": "ValueQuery.query",
                    "owner": "查询模块",
                    "consumers": ["报表服务"],
                    "responsibility": "返回固定版本的查询结果",
                    "invariants": ["版本语义不丢失", "失败不伪装成零值"],
                    "compatibility": "preserve",
                    "reason": "统一已有查询入口",
                    "verification_refs": ["src", "tests"],
                },
                {
                    "kind": "model",
                    "name": "QueryCriteria",
                    "owner": "查询模块",
                    "consumers": ["ValueQuery.query"],
                    "responsibility": "承载共享查询条件",
                    "invariants": ["不携带指标身份"],
                    "compatibility": "new",
                    "reason": "消除重复条件对象",
                    "verification_refs": ["src", "tests"],
                },
            ],
        },
        "evidence": [
            {
                "id": "src",
                "kind": "source",
                "ref": "source-manifest",
                "fingerprint": "sha256:source",
                "result": "pass",
            },
            {
                "id": "tests",
                "kind": "test",
                "ref": "focused-tests.xml",
                "fingerprint": "sha256:tests",
                "result": "pass",
            },
            {
                "id": "consumer",
                "kind": "consumer_compile",
                "ref": "consumer-compile",
                "fingerprint": "sha256:consumer",
                "result": "pending",
            },
        ],
        "claims": [
            {"id": "c1", "text": "提供者测试已通过", "state": "fact", "evidence_refs": ["tests"]},
            {
                "id": "c2",
                "text": "消费者尚未接入",
                "state": "pending",
                "owner": "消费者 Owner",
                "reason": "等待 Java 21 编译和真实调用链验证",
                "evidence_refs": ["consumer"],
            },
        ],
    }


def self_test() -> None:
    validate_contract(_valid_contract())

    missing_consumer = _valid_contract()
    del missing_consumer["change"]["items"][0]["consumers"]
    try:
        validate_contract(missing_consumer)
    except ContractError as error:
        assert "consumers" in str(error)
    else:
        raise AssertionError("missing consumer was accepted")

    false_adoption = _valid_contract()
    false_adoption["change"]["adoption"] = "consumer-adopted"
    try:
        validate_contract(false_adoption)
    except ContractError as error:
        assert "consumer_compile" in str(error)
    else:
        raise AssertionError("consumer adoption without compile evidence was accepted")

    unlinked_consumer_evidence = _valid_contract()
    unlinked_consumer_evidence["change"]["adoption"] = "consumer-adopted"
    unlinked_consumer_evidence["evidence"][2]["result"] = "pass"
    try:
        validate_contract(unlinked_consumer_evidence)
    except ContractError as error:
        assert "verification_refs" in str(error)
    else:
        raise AssertionError("consumer evidence not linked to an item was accepted")

    missing_provider_evidence = _valid_contract()
    missing_provider_evidence["change"]["adoption"] = "consumer-adopted"
    missing_provider_evidence["evidence"][2]["result"] = "pass"
    for item in missing_provider_evidence["change"]["items"]:
        item["verification_refs"].append("consumer")
    missing_provider_evidence["evidence"] = [
        entry for entry in missing_provider_evidence["evidence"] if entry["id"] != "src"
    ]
    for item in missing_provider_evidence["change"]["items"]:
        item["verification_refs"].remove("src")
    try:
        validate_contract(missing_provider_evidence)
    except ContractError as error:
        assert "source" in str(error)
    else:
        raise AssertionError("consumer adoption without provider source evidence was accepted")

    missing_runtime_provider_evidence = _valid_contract()
    missing_runtime_provider_evidence["change"]["adoption"] = "runtime-accepted"
    missing_runtime_provider_evidence["evidence"][2]["result"] = "pass"
    missing_runtime_provider_evidence["evidence"].append(
        {
            "id": "runtime",
            "kind": "runtime",
            "ref": "runtime-run",
            "fingerprint": "sha256:runtime",
            "result": "pass",
        }
    )
    missing_runtime_provider_evidence["claims"] = [missing_runtime_provider_evidence["claims"][0]]
    for item in missing_runtime_provider_evidence["change"]["items"]:
        item["verification_refs"].extend(["consumer", "runtime"])
        item["verification_refs"].remove("src")
    missing_runtime_provider_evidence["evidence"] = [
        entry for entry in missing_runtime_provider_evidence["evidence"] if entry["id"] != "src"
    ]
    try:
        validate_contract(missing_runtime_provider_evidence)
    except ContractError as error:
        assert "source" in str(error)
    else:
        raise AssertionError("runtime acceptance without provider source evidence was accepted")

    blocked_without_evidence = _valid_contract()
    blocked_without_evidence["change"]["adoption"] = "blocked"
    blocked_without_evidence["claims"] = [blocked_without_evidence["claims"][0]]
    try:
        validate_contract(blocked_without_evidence)
    except ContractError as error:
        assert "blocked" in str(error)
    else:
        raise AssertionError("blocked contract without a blocker was accepted")

    false_fact = _valid_contract()
    false_fact["claims"][0]["evidence_refs"] = ["consumer"]
    try:
        validate_contract(false_fact)
    except ContractError as error:
        assert "passing evidence" in str(error)
    else:
        raise AssertionError("fact based on pending evidence was accepted")
    print("OK engineering change contract self-test")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.contract is None:
        parser.error("contract is required unless --self-test is used")
    try:
        validate_contract(json.loads(args.contract.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ContractError) as error:
        print(f"FAIL engineering change contract: {error}", file=sys.stderr)
        return 1
    print(f"OK engineering change contract: {args.contract}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
