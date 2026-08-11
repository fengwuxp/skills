#!/usr/bin/env python3
"""Validate a portable wise-agent Goal, recovery, and optional work graph contract.

Input: one JSON file explicitly supplied by the caller.
Output: validation result on stdout/stderr. Writes: none. Network: none.
Failure: exits non-zero when required state, decision, budget, or recovery data is invalid.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import copy
from datetime import datetime
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


STATUSES = {"Draft", "Ready", "Active", "Blocked", "Verified", "Closed", "Superseded"}
WORK_NODE_STATUSES = {"Pending", "Ready", "Running", "Blocked", "Verified", "Cancelled"}
WORK_NODE_RISKS = {"low", "medium", "high"}
WORK_GRAPH_TERMINALS = {"Complete", "Stop", "Human handoff"}
FAILURE_OUTCOMES = {"fallback", "stop", "human"}
EVIDENCE_REF_TYPES = {
    "source",
    "test",
    "validator",
    "independent_review",
    "owner_confirmation",
    "runtime",
    "production",
}
NON_VALIDATOR_EVIDENCE_REF_TYPES = EVIDENCE_REF_TYPES - {"validator"}
EVIDENCE_REF_FIELDS = {"ref", "fingerprint", "method", "result", "observed_at"}
AUTHORITY_REF_STATUSES = {"current", "stale", "superseded"}
DECISION_STATES = {"new", "confirmed", "excluded", "pending"}
LOAD_BEARING_GOAL_FIELDS = {
    "objective",
    "success_criteria",
    "non_goals",
    "write_scope",
    "state_carrier",
    "checker",
    "stop_conditions",
    "recovery_entry",
    "residual_risk_owner",
    "max_iterations",
    "no_progress_limit",
    "execution_basis",
}
STRING_FIELDS = {
    "goal_id",
    "objective",
    "state_carrier",
    "checker",
    "recovery_entry",
    "residual_risk_owner",
}
LIST_FIELDS = {
    "success_criteria",
    "non_goals",
    "confirmed_decisions",
    "excluded_options",
    "pending_items",
    "execution_basis",
    "write_scope",
    "verification_evidence",
    "stop_conditions",
}


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def is_timestamp(value: Any) -> bool:
    return parse_timestamp(value) is not None


def is_later_timestamp(current: Any, previous: Any) -> bool:
    current_timestamp = parse_timestamp(current)
    previous_timestamp = parse_timestamp(previous)
    return (
        current_timestamp is not None
        and previous_timestamp is not None
        and current_timestamp > previous_timestamp
    )


def validate_authority_refs(value: Any, required: bool) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if value is None and not required:
        return [], {}
    if not isinstance(value, list) or not value:
        return ["authority_refs must be a non-empty list"], {}

    errors: list[str] = []
    refs: dict[str, dict[str, Any]] = {}
    for index, authority_ref in enumerate(value):
        prefix = f"authority_refs[{index}]"
        if not isinstance(authority_ref, dict):
            errors.append(f"{prefix} must be an object")
            continue
        ref = authority_ref.get("ref")
        if not isinstance(ref, str) or not ref.strip():
            errors.append(f"{prefix} ref must be a non-empty string")
            continue
        if ref in refs:
            errors.append(f"authority_ref {ref} must be unique")
            continue
        refs[ref] = authority_ref
        for field in ("authority_revision", "fingerprint"):
            if not isinstance(authority_ref.get(field), str) or not authority_ref[field].strip():
                errors.append(f"{prefix} {field} must be a non-empty string")
        if not is_timestamp(authority_ref.get("observed_at")):
            errors.append(f"{prefix} observed_at must be an ISO-8601 timestamp with timezone")
        recheck_on = authority_ref.get("recheck_on")
        if not is_string_list(recheck_on) or not recheck_on:
            errors.append(f"{prefix} recheck_on must be a non-empty list of strings")
        status = authority_ref.get("status")
        if status not in AUTHORITY_REF_STATUSES:
            errors.append(f"{prefix} status must be one of {sorted(AUTHORITY_REF_STATUSES)}")
        for field in ("recheck_evidence", "supersedes", "superseded_by"):
            if field in authority_ref and (
                not isinstance(authority_ref[field], str) or not authority_ref[field].strip()
            ):
                errors.append(f"{prefix} {field} must be a non-empty string")

    for ref, authority_ref in refs.items():
        status = authority_ref.get("status")
        superseded_by = authority_ref.get("superseded_by")
        if status == "superseded":
            replacement = refs.get(superseded_by) if isinstance(superseded_by, str) else None
            if replacement is None or replacement.get("supersedes") != ref:
                errors.append(
                    f"authority_ref {ref} superseded status requires a reciprocal superseded_by reference"
                )
        supersedes = authority_ref.get("supersedes")
        if isinstance(supersedes, str):
            previous = refs.get(supersedes)
            if previous is None or previous.get("status") != "superseded":
                errors.append(
                    f"authority_ref {ref} supersedes must reference a retained superseded authority_ref"
                )
    return errors, refs


def decision_states(data: dict[str, Any]) -> dict[str, str]:
    states: dict[str, str] = {}
    for field, state in (
        ("confirmed_decisions", "confirmed"),
        ("excluded_options", "excluded"),
        ("pending_items", "pending"),
    ):
        value = data.get(field)
        if is_string_list(value):
            states.update((decision, state) for decision in value)
    return states


def validate_decision_transitions(
    data: dict[str, Any], previous_contract: dict[str, Any] | None
) -> list[str]:
    transitions = data.get("decision_transitions", [])
    if not isinstance(transitions, list):
        return ["decision_transitions must be a list"]

    errors: list[str] = []
    indexed: dict[tuple[str, str, str], dict[str, Any]] = {}
    for index, transition in enumerate(transitions):
        prefix = f"decision_transitions[{index}]"
        if not isinstance(transition, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("decision", "owner", "evidence_ref", "evidence_fingerprint"):
            if not isinstance(transition.get(field), str) or not transition[field].strip():
                errors.append(f"{prefix} {field} must be a non-empty string")
        source = transition.get("from")
        target = transition.get("to")
        if not isinstance(source, str) or source not in DECISION_STATES:
            errors.append(f"{prefix} from must be one of {sorted(DECISION_STATES)}")
        if not isinstance(target, str) or target not in DECISION_STATES - {"new"}:
            errors.append(f"{prefix} to must be confirmed, excluded, or pending")
        decision = transition.get("decision")
        if (
            isinstance(decision, str)
            and isinstance(source, str)
            and source in DECISION_STATES
            and isinstance(target, str)
            and target in DECISION_STATES
        ):
            key = (decision, source, target)
            if key in indexed:
                errors.append(f"decision transition {decision} {source}->{target} must be unique")
            indexed[key] = transition

    if not isinstance(previous_contract, dict):
        return errors

    previous = decision_states(previous_contract)
    current = decision_states(data)
    expected: set[tuple[str, str, str]] = set()
    for decision in sorted(set(previous) | set(current)):
        source = previous.get(decision, "new")
        target = current.get(decision)
        if source == target:
            continue
        if target is None:
            errors.append(f"decision {decision} must not disappear across state revisions")
            continue
        if source == "new" and target == "pending":
            continue
        if source == "excluded" and target == "confirmed":
            errors.append(f"decision {decision} cannot move directly from excluded to confirmed")
            continue
        key = (decision, source, target)
        expected.add(key)
        if key not in indexed:
            errors.append(
                f"decision {decision} changed from {source} to {target} without Owner evidence"
            )
    for decision, source, target in sorted(set(indexed) - expected):
        errors.append(f"decision transition {decision} {source}->{target} does not match a state change")
    return errors


def validate_state_migration(
    data: dict[str, Any],
    previous_contract: dict[str, Any] | None,
    require_state_integrity: bool,
    require_previous: bool,
) -> list[str]:
    errors: list[str] = []
    revision = data.get("state_revision")
    if revision is None and not require_state_integrity:
        return errors
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        return ["state_revision must be a positive integer"]
    if require_previous and revision > 1 and not isinstance(previous_contract, dict):
        errors.append("state_revision > 1 requires previous contract validation")
    if not isinstance(previous_contract, dict):
        return errors

    previous_revision = previous_contract.get("state_revision")
    if previous_revision is not None and (
        not isinstance(previous_revision, int)
        or isinstance(previous_revision, bool)
        or previous_revision < 1
    ):
        errors.append("previous state_revision must be a positive integer")
        return errors
    expected_revision = 1 if previous_revision is None else previous_revision + 1
    if revision != expected_revision:
        errors.append("state_revision must increment previous revision by one")

    changed_fields = sorted(
        field for field in LOAD_BEARING_GOAL_FIELDS if data.get(field) != previous_contract.get(field)
    )
    transition = data.get("goal_transition")
    if changed_fields:
        if not isinstance(transition, dict):
            errors.append("load-bearing Goal fields changed without goal_transition")
        else:
            for field in ("owner", "reason", "evidence_ref", "evidence_fingerprint"):
                if not isinstance(transition.get(field), str) or not transition[field].strip():
                    errors.append(f"goal_transition {field} must be a non-empty string")
            transition_fields = transition.get("changed_fields")
            if not is_string_list(transition_fields) or not transition_fields:
                errors.append("goal_transition changed_fields must exactly match changed Goal fields")
            elif len(transition_fields) != len(set(transition_fields)):
                errors.append("goal_transition changed_fields must not contain duplicates")
            elif set(transition_fields) != set(changed_fields):
                errors.append("goal_transition changed_fields must exactly match changed Goal fields")
    elif transition is not None:
        errors.append("goal_transition must describe an actual load-bearing Goal change")
    return errors


def validate_authority_migration(
    current_refs: dict[str, dict[str, Any]], previous_refs: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    for ref, previous in previous_refs.items():
        current = current_refs.get(ref)
        if current is None:
            errors.append(f"authority_ref {ref} must not disappear across state revisions")
            continue
        changed = any(
            current.get(field) != previous.get(field)
            for field in ("authority_revision", "fingerprint")
        )
        previous_recheck = previous.get("recheck_evidence")
        current_recheck = current.get("recheck_evidence")
        if (
            changed
            and current.get("status") == "current"
            and (
                not current_recheck
                or current_recheck == previous_recheck
                or not is_later_timestamp(current.get("observed_at"), previous.get("observed_at"))
            )
        ):
            errors.append(
                f"authority_ref {ref} changed without recheck_evidence or stale status; "
                "current status requires fresh recheck_evidence and later observed_at"
            )
        previous_status = previous.get("status")
        current_status = current.get("status")
        if (
            previous_status == "stale"
            and current_status == "current"
            and (
                not current.get("recheck_evidence")
                or current.get("recheck_evidence") == previous.get("recheck_evidence")
                or not is_later_timestamp(current.get("observed_at"), previous.get("observed_at"))
            )
        ):
            errors.append(
                f"authority_ref {ref} cannot move from stale to current without fresh recheck_evidence and later observed_at"
            )
        if previous_status == "current" and current_status == "superseded":
            expected_tombstone = dict(previous)
            expected_tombstone["status"] = "superseded"
            expected_tombstone["superseded_by"] = current.get("superseded_by")
            if current != expected_tombstone:
                errors.append(
                    f"authority_ref {ref} first supersession must preserve the previous entry"
                )
        if previous_status == "superseded" and current != previous:
            errors.append(f"authority_ref {ref} superseded tombstone must remain immutable")
    return errors


def validate_evidence_refs(node_id: str, value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return [f"work_graph node {node_id} evidence_refs must be a list"]

    errors: list[str] = []
    for index, evidence_ref in enumerate(value):
        prefix = f"work_graph node {node_id} evidence_refs[{index}]"
        if not isinstance(evidence_ref, dict):
            errors.append(f"{prefix} must be an object")
            continue
        evidence_type = evidence_ref.get("type")
        if not isinstance(evidence_type, str) or evidence_type not in EVIDENCE_REF_TYPES:
            errors.append(f"{prefix} type must be one of {sorted(EVIDENCE_REF_TYPES)}")
        for field in sorted(EVIDENCE_REF_FIELDS):
            if not isinstance(evidence_ref.get(field), str) or not evidence_ref[field].strip():
                errors.append(f"{prefix} {field} must be a non-empty string")
    return errors


def overlapping_scopes(left: set[str], right: set[str]) -> list[str]:
    overlaps: set[str] = set()
    for left_scope in left:
        left_path = PurePosixPath(left_scope)
        for right_scope in right:
            right_path = PurePosixPath(right_scope)
            if left_path == right_path:
                overlaps.add(left_scope)
            elif left_path in right_path.parents or right_path in left_path.parents:
                overlaps.add(f"{left_scope} <-> {right_scope}")
    return sorted(overlaps)


def scope_is_within(scope: str, allowed_scopes: list[str]) -> bool:
    candidate = PurePosixPath(scope)
    if candidate.is_absolute() or ".." in candidate.parts:
        return False
    for allowed_scope in allowed_scopes:
        allowed = PurePosixPath(allowed_scope)
        if allowed.is_absolute() or ".." in allowed.parts:
            continue
        if candidate == allowed or allowed in candidate.parents:
            return True
    return False


def read_contract(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("root must be a JSON object")
    return data


def validate_work_graph(
    graph: Any,
    allowed_write_scope: Any = None,
    previous_graph: Any = None,
    require_previous: bool = True,
    max_attempts_budget: Any = None,
    strict_verified_evidence: bool = True,
) -> list[str]:
    if graph is None:
        return []
    if not isinstance(graph, dict):
        return ["work_graph must be an object"]

    errors: list[str] = []
    revision = graph.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append("work_graph revision must be a positive integer")
    revision_reason = graph.get("revision_reason", "")
    revision_evidence = graph.get("revision_evidence", [])
    if not isinstance(revision_reason, str):
        errors.append("work_graph revision_reason must be a string")
    if not is_string_list(revision_evidence):
        errors.append("work_graph revision_evidence must be a list of non-empty strings")
    if isinstance(revision, int) and not isinstance(revision, bool) and revision > 1 and (
        not isinstance(revision_reason, str)
        or not revision_reason.strip()
        or not is_string_list(revision_evidence)
        or not revision_evidence
    ):
        errors.append("work_graph revision > 1 requires revision_reason and revision_evidence")
    if (
        require_previous
        and isinstance(revision, int)
        and not isinstance(revision, bool)
        and revision > 1
        and not isinstance(previous_graph, dict)
    ):
        errors.append("work_graph revision > 1 requires previous contract validation")

    raw_nodes = graph.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        errors.append("work_graph nodes must be a non-empty list")
        return errors
    state_inputs = graph.get("state_inputs", [])
    if not is_string_list(state_inputs):
        errors.append("work_graph state_inputs must be a list of non-empty strings")
    elif len(state_inputs) != len(set(state_inputs)):
        errors.append("work_graph state_inputs must contain unique keys")

    nodes: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(raw_nodes):
        if not isinstance(node, dict):
            errors.append(f"work_graph node {index} must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            errors.append(f"work_graph node {index} id must be a non-empty string")
            continue
        if node_id in nodes:
            errors.append(f"work_graph node id {node_id} must be unique")
            continue
        nodes[node_id] = node

        if not isinstance(node.get("objective"), str) or not node["objective"].strip():
            errors.append(f"work_graph node {node_id} objective must be a non-empty string")
        status = node.get("status")
        if not isinstance(status, str) or status not in WORK_NODE_STATUSES:
            errors.append(f"work_graph node {node_id} status must be one of {sorted(WORK_NODE_STATUSES)}")
        if not is_string_list(node.get("depends_on")):
            errors.append(f"work_graph node {node_id} depends_on must be a list of non-empty strings")
        if not is_string_list(node.get("write_scope")):
            errors.append(f"work_graph node {node_id} write_scope must be a list of non-empty strings")
        elif is_string_list(allowed_write_scope):
            for scope in node["write_scope"]:
                if not scope_is_within(scope, allowed_write_scope):
                    errors.append(
                        f"work_graph node {node_id} write_scope {scope} is outside contract write_scope"
                    )
        risk = node.get("risk")
        if not isinstance(risk, str) or risk not in WORK_NODE_RISKS:
            errors.append(f"work_graph node {node_id} risk must be one of {sorted(WORK_NODE_RISKS)}")
        if not isinstance(node.get("checker"), str):
            errors.append(f"work_graph node {node_id} checker must be a string")
        if "maker" in node and (
            not isinstance(node["maker"], str) or not node["maker"].strip()
        ):
            errors.append(f"work_graph node {node_id} maker must be a non-empty string")
        if not is_string_list(node.get("evidence")):
            errors.append(f"work_graph node {node_id} evidence must be a list of non-empty strings")
        errors.extend(validate_evidence_refs(node_id, node.get("evidence_refs")))
        if not isinstance(node.get("status_reason"), str):
            errors.append(f"work_graph node {node_id} status_reason must be a string")
        if "parallel_group" in node and (
            not isinstance(node["parallel_group"], str) or not node["parallel_group"].strip()
        ):
            errors.append(f"work_graph node {node_id} parallel_group must be a non-empty string")
        for field in ("consumes", "produces"):
            if field in node and not is_string_list(node[field]):
                errors.append(
                    f"work_graph node {node_id} {field} must be a list of non-empty strings"
                )
        produces = node.get("produces", [])
        if is_string_list(produces) and produces and (
            not isinstance(node.get("writeback"), str) or not node["writeback"].strip()
        ):
            errors.append(f"work_graph node {node_id} with produces requires writeback")
        elif is_string_list(produces) and produces:
            writeback = node["writeback"]
            writeback_path = writeback.split("#", 1)[0]
            node_write_scope = node.get("write_scope")
            if not is_string_list(node_write_scope) or not scope_is_within(
                writeback_path, node_write_scope
            ):
                errors.append(
                    f"work_graph node {node_id} writeback {writeback} is outside node write_scope"
                )
            elif is_string_list(allowed_write_scope) and not scope_is_within(
                writeback_path, allowed_write_scope
            ):
                errors.append(
                    f"work_graph node {node_id} writeback {writeback} is outside contract write_scope"
                )

        transitions = node.get("transitions")
        if transitions is not None:
            if not isinstance(transitions, list) or not transitions:
                errors.append(f"work_graph node {node_id} transitions must be a non-empty list")
            else:
                default_count = 0
                for transition in transitions:
                    if not isinstance(transition, dict):
                        errors.append(f"work_graph node {node_id} transition must be an object")
                        continue
                    condition = transition.get("when")
                    target = transition.get("target")
                    if not isinstance(condition, str) or not condition.strip():
                        errors.append(
                            f"work_graph node {node_id} transition when must be a non-empty string"
                        )
                    elif condition == "default":
                        default_count += 1
                    if not isinstance(target, str) or not target.strip():
                        errors.append(
                            f"work_graph node {node_id} transition target must be a non-empty string"
                        )
                if default_count != 1:
                    errors.append(
                        f"work_graph node {node_id} transitions require exactly one default branch"
                    )

        failure_policy = node.get("failure_policy")
        if failure_policy is not None:
            if not isinstance(failure_policy, dict):
                errors.append(f"work_graph node {node_id} failure_policy must be an object")
            else:
                max_attempts = failure_policy.get("max_attempts")
                if (
                    not isinstance(max_attempts, int)
                    or isinstance(max_attempts, bool)
                    or max_attempts < 1
                ):
                    errors.append(
                        f"work_graph node {node_id} failure_policy max_attempts must be a positive integer"
                    )
                elif (
                    isinstance(max_attempts_budget, int)
                    and not isinstance(max_attempts_budget, bool)
                    and max_attempts > max_attempts_budget
                ):
                    errors.append(
                        f"work_graph node {node_id} failure_policy max_attempts "
                        "must not exceed contract max_iterations"
                    )
                on_exhausted = failure_policy.get("on_exhausted")
                if on_exhausted not in FAILURE_OUTCOMES:
                    errors.append(
                        f"work_graph node {node_id} failure_policy on_exhausted must be fallback, stop, or human"
                    )
                if "backoff" in failure_policy and (
                    not isinstance(failure_policy["backoff"], str)
                    or not failure_policy["backoff"].strip()
                ):
                    errors.append(
                        f"work_graph node {node_id} failure_policy backoff must be a non-empty string"
                    )

    known_ids = set(nodes)
    state_producers: dict[str, list[str]] = defaultdict(list)
    for node_id, node in nodes.items():
        if node.get("status") == "Cancelled":
            continue
        produces = node.get("produces", [])
        if is_string_list(produces):
            for state_key in produces:
                state_producers[state_key].append(node_id)
    for state_key, producers in state_producers.items():
        if len(producers) > 1:
            errors.append(
                f"work_graph state key {state_key} has multiple producers: {', '.join(producers)}"
            )

    dependencies: dict[str, list[str]] = {}
    for node_id, node in nodes.items():
        depends_on = node.get("depends_on")
        if not is_string_list(depends_on):
            continue
        dependencies[node_id] = []
        for dependency in depends_on:
            if dependency not in known_ids:
                errors.append(f"work_graph node {node_id} depends on unknown node {dependency}")
                continue
            dependencies[node_id].append(dependency)
            status = node.get("status")
            if isinstance(status, str) and status in {"Ready", "Running", "Verified"} and nodes[dependency].get("status") != "Verified":
                errors.append(
                    f"work_graph node {node_id} cannot be {status} before dependency {dependency} is Verified"
                )

        transitions = node.get("transitions")
        if isinstance(transitions, list):
            for transition in transitions:
                if not isinstance(transition, dict):
                    continue
                target = transition.get("target")
                if (
                    isinstance(target, str)
                    and target.strip()
                    and target not in known_ids
                    and target not in WORK_GRAPH_TERMINALS
                ):
                    errors.append(
                        f"work_graph node {node_id} transition target {target} does not exist"
                    )

        failure_policy = node.get("failure_policy")
        if isinstance(failure_policy, dict) and failure_policy.get("on_exhausted") == "fallback":
            target = failure_policy.get("target")
            if not isinstance(target, str) or not target.strip() or target not in known_ids:
                errors.append(
                    f"work_graph node {node_id} fallback requires an existing target node"
                )

    execution_successors: dict[str, set[str]] = defaultdict(set)
    execution_indegree = {node_id: 0 for node_id in nodes}

    def add_execution_edge(source: str, target: str) -> None:
        if target not in execution_successors[source]:
            execution_successors[source].add(target)
            execution_indegree[target] += 1

    for node_id, node_dependencies in dependencies.items():
        for dependency in node_dependencies:
            add_execution_edge(dependency, node_id)
    for node_id, node in nodes.items():
        transitions = node.get("transitions")
        if isinstance(transitions, list):
            for transition in transitions:
                if not isinstance(transition, dict):
                    continue
                target = transition.get("target")
                if isinstance(target, str) and target in known_ids:
                    add_execution_edge(node_id, target)
        failure_policy = node.get("failure_policy")
        if isinstance(failure_policy, dict) and failure_policy.get("on_exhausted") == "fallback":
            target = failure_policy.get("target")
            if isinstance(target, str) and target in known_ids:
                add_execution_edge(node_id, target)

    execution_ready = deque(
        node_id for node_id, degree in execution_indegree.items() if degree == 0
    )
    execution_visited = 0
    while execution_ready:
        current = execution_ready.popleft()
        execution_visited += 1
        for successor in execution_successors[current]:
            execution_indegree[successor] -= 1
            if execution_indegree[successor] == 0:
                execution_ready.append(successor)
    if execution_visited != len(nodes):
        errors.append("work_graph execution edges must be acyclic")

    indegree = {node_id: len(dependencies.get(node_id, [])) for node_id in nodes}
    successors: dict[str, list[str]] = defaultdict(list)
    for node_id, node_dependencies in dependencies.items():
        for dependency in node_dependencies:
            successors[dependency].append(node_id)
    ready = deque(node_id for node_id, degree in indegree.items() if degree == 0)
    topological_order: list[str] = []
    visited = 0
    while ready:
        current = ready.popleft()
        visited += 1
        topological_order.append(current)
        for successor in successors[current]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    if visited != len(nodes):
        errors.append("work_graph dependencies must be acyclic")
    elif is_string_list(state_inputs):
        available_state: dict[str, set[str]] = {}
        for node_id in topological_order:
            available = set(state_inputs)
            for dependency in dependencies.get(node_id, []):
                available.update(available_state.get(dependency, set()))
            consumes = nodes[node_id].get("consumes", [])
            if is_string_list(consumes):
                for state_key in consumes:
                    if state_key not in available:
                        errors.append(
                            f"work_graph node {node_id} consumes unavailable state key {state_key}"
                        )
            produces = nodes[node_id].get("produces", [])
            if is_string_list(produces):
                available.update(produces)
            available_state[node_id] = available

    if isinstance(previous_graph, dict):
        previous_revision = previous_graph.get("revision")
        previous_nodes = previous_graph.get("nodes")
        previous_nodes_by_id = {
            node["id"]: node
            for node in previous_nodes
            if isinstance(node, dict)
            and isinstance(node.get("id"), str)
            and node["id"].strip()
        } if isinstance(previous_nodes, list) else {}
        nodes_changed = nodes != previous_nodes_by_id
        previous_state_inputs = previous_graph.get("state_inputs", [])
        state_inputs_changed = (
            is_string_list(state_inputs)
            and is_string_list(previous_state_inputs)
            and set(state_inputs) != set(previous_state_inputs)
        )
        graph_semantics_changed = nodes_changed or state_inputs_changed
        valid_revisions = (
            isinstance(revision, int)
            and not isinstance(revision, bool)
            and isinstance(previous_revision, int)
            and not isinstance(previous_revision, bool)
        )
        if graph_semantics_changed:
            if valid_revisions and revision != previous_revision + 1:
                errors.append("work_graph revision must increment previous revision by one")
            if (
                not isinstance(revision_reason, str)
                or not revision_reason.strip()
                or not is_string_list(revision_evidence)
                or not revision_evidence
            ):
                errors.append(
                    "work_graph node or state_inputs changes require revision_reason and revision_evidence"
                )
        elif any(
            graph.get(field) != previous_graph.get(field)
            for field in ("revision", "revision_reason", "revision_evidence")
        ):
            errors.append("work_graph revision metadata must remain unchanged when nodes are unchanged")
        if isinstance(previous_nodes, list):
            for previous_node in previous_nodes:
                if not isinstance(previous_node, dict) or previous_node.get("status") != "Cancelled":
                    continue
                previous_id = previous_node.get("id")
                if not isinstance(previous_id, str):
                    continue
                current_node = nodes.get(previous_id)
                if current_node is None:
                    errors.append(f"work_graph Cancelled node {previous_id} must remain as tombstone")
                elif current_node.get("status") != "Cancelled":
                    errors.append(
                        f"work_graph node {previous_id} was Cancelled in previous revision and must not be revived"
                    )

    parallel_groups: dict[str, list[tuple[str, set[str]]]] = defaultdict(list)
    for node_id, node in nodes.items():
        status = node.get("status")
        evidence = node.get("evidence")
        evidence_refs = node.get("evidence_refs")
        evidence_ref_types = {
            evidence_ref.get("type")
            for evidence_ref in evidence_refs
            if isinstance(evidence_ref, dict)
        } if isinstance(evidence_refs, list) else set()
        if isinstance(status, str) and status == "Verified" and is_string_list(evidence) and not evidence:
            errors.append(f"work_graph Verified node {node_id} requires evidence")
        if strict_verified_evidence and isinstance(status, str) and status == "Verified" and (
            not isinstance(evidence_refs, list) or not evidence_refs
        ):
            errors.append(f"work_graph Verified node {node_id} requires evidence_refs")
        if (
            strict_verified_evidence
            and status == "Verified"
            and isinstance(evidence_refs, list)
            and evidence_refs
            and not evidence_ref_types & NON_VALIDATOR_EVIDENCE_REF_TYPES
        ):
            errors.append(
                f"work_graph Verified node {node_id} requires at least one non-validator evidence_ref"
            )
        if isinstance(status, str) and status in {"Blocked", "Cancelled"} and (
            not isinstance(node.get("status_reason"), str)
            or not node["status_reason"].strip()
            or not is_string_list(evidence)
            or not evidence
        ):
            errors.append(f"work_graph {status} node {node_id} requires status_reason and evidence")
        if node.get("risk") == "high" and (
            not isinstance(node.get("checker"), str) or not node["checker"].strip()
        ):
            errors.append(f"work_graph high-risk node {node_id} requires checker")
        if strict_verified_evidence and status == "Verified" and node.get("risk") == "high":
            maker = node.get("maker")
            checker = node.get("checker")
            if not isinstance(maker, str) or not maker.strip():
                errors.append(f"work_graph high-risk Verified node {node_id} requires maker")
            elif (
                isinstance(checker, str)
                and checker.strip()
                and checker.strip().casefold() == maker.strip().casefold()
            ):
                errors.append(
                    f"work_graph high-risk Verified node {node_id} requires checker different from maker"
                )
            if "independent_review" not in evidence_ref_types:
                errors.append(
                    f"work_graph high-risk Verified node {node_id} requires independent_review evidence_ref"
                )

        parallel_group = node.get("parallel_group")
        write_scope = node.get("write_scope")
        if status != "Cancelled" and isinstance(parallel_group, str) and parallel_group.strip() and is_string_list(write_scope):
            scope = set(write_scope)
            for other_id, other_scope in parallel_groups[parallel_group]:
                overlap = overlapping_scopes(other_scope, scope)
                if overlap:
                    errors.append(
                        f"work_graph nodes {other_id} and {node_id} in parallel group {parallel_group} "
                        f"have overlapping write_scope: {', '.join(overlap)}"
                    )
            parallel_groups[parallel_group].append((node_id, scope))

    return errors


def validate(
    data: dict[str, Any],
    previous_contract: dict[str, Any] | None = None,
    require_previous: bool = True,
    strict_verified_evidence: bool = True,
    require_state_integrity: bool = True,
) -> list[str]:
    errors: list[str] = []
    errors.extend(
        validate_state_migration(
            data,
            previous_contract,
            require_state_integrity,
            require_previous,
        )
    )

    authority_errors, authority_refs = validate_authority_refs(
        data.get("authority_refs"), require_state_integrity
    )
    errors.extend(authority_errors)
    previous_authority_refs: dict[str, dict[str, Any]] = {}
    if isinstance(previous_contract, dict):
        _, previous_authority_refs = validate_authority_refs(
            previous_contract.get("authority_refs"), False
        )
        errors.extend(validate_authority_migration(authority_refs, previous_authority_refs))

    status = data.get("status")
    if not isinstance(status, str) or status not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")
    elif status in {"Ready", "Active", "Verified", "Closed"} and any(
        authority_ref.get("status") == "stale" for authority_ref in authority_refs.values()
    ):
        errors.append(f"{status} cannot proceed with stale authority_refs")

    for field in sorted(STRING_FIELDS):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string")

    for field in sorted(LIST_FIELDS):
        value = data.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"{field} must be a list of non-empty strings")

    for field in ("success_criteria", "non_goals", "write_scope", "stop_conditions"):
        if isinstance(data.get(field), list) and not data[field]:
            errors.append(f"{field} must not be empty")

    maximum = data.get("max_iterations")
    no_progress = data.get("no_progress_limit")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
        errors.append("max_iterations must be a positive integer")
    if not isinstance(no_progress, int) or isinstance(no_progress, bool) or no_progress < 1:
        errors.append("no_progress_limit must be a positive integer")
    elif isinstance(maximum, int) and not isinstance(maximum, bool) and no_progress > maximum:
        errors.append("no_progress_limit must not exceed max_iterations")

    decision_fields = ("confirmed_decisions", "excluded_options", "pending_items", "execution_basis")
    if all(is_string_list(data.get(field)) for field in decision_fields):
        confirmed = set(data["confirmed_decisions"])
        excluded = set(data["excluded_options"])
        pending = set(data["pending_items"])
        basis = set(data["execution_basis"])
        if confirmed & excluded or confirmed & pending or excluded & pending:
            errors.append("confirmed, excluded, and pending decisions must be disjoint")
        if not basis <= confirmed:
            errors.append("execution_basis must contain confirmed decisions only")
    errors.extend(validate_decision_transitions(data, previous_contract))

    next_action = data.get("next_action")
    if (not isinstance(status, str) or status not in {"Closed", "Superseded"}) and (
        not isinstance(next_action, str) or not next_action.strip()
    ):
        errors.append("next_action must be a non-empty string before closure")
    if isinstance(status, str) and status in {"Ready", "Active"} and isinstance(data.get("execution_basis"), list) and not data["execution_basis"]:
        errors.append(f"{status} requires at least one confirmed execution_basis decision")
    if isinstance(status, str) and status in {"Verified", "Closed"} and isinstance(data.get("verification_evidence"), list) and not data["verification_evidence"]:
        errors.append(f"{status} requires verification_evidence")

    work_graph = data.get("work_graph")
    previous_graph = previous_contract.get("work_graph") if isinstance(previous_contract, dict) else None
    if isinstance(previous_contract, dict) and previous_contract.get("goal_id") != data.get("goal_id"):
        errors.append("previous contract goal_id must match current goal_id")
    if isinstance(previous_graph, dict) and not isinstance(work_graph, dict):
        errors.append("current contract must retain work_graph from previous revision")
    errors.extend(
        validate_work_graph(
            work_graph,
            data.get("write_scope"),
            previous_graph,
            require_previous=require_previous,
            max_attempts_budget=maximum,
            strict_verified_evidence=strict_verified_evidence,
        )
    )
    if isinstance(status, str) and status in {"Verified", "Closed"} and isinstance(work_graph, dict):
        nodes = work_graph.get("nodes")
        if isinstance(nodes, list):
            non_terminal = []
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                node_status = node.get("status")
                if not isinstance(node_status, str) or node_status not in {"Verified", "Cancelled"}:
                    non_terminal.append(str(node.get("id", "<unknown>")))
            if non_terminal:
                errors.append(
                    f"{status} requires every work_graph node to be Verified or Cancelled; "
                    f"non-terminal: {', '.join(non_terminal)}"
                )
    return errors


def validate_previous_contract(data: dict[str, Any]) -> list[str]:
    return validate(
        data,
        require_previous=False,
        strict_verified_evidence=False,
        require_state_integrity=False,
    )


def run_self_test() -> None:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    valid_contract = read_contract(fixtures / "state-contract-valid.json")
    valid_errors = validate(valid_contract)
    if valid_errors:
        raise SystemExit(f"valid fixture rejected: {valid_errors}")

    stale_authority = copy.deepcopy(valid_contract)
    stale_authority["authority_refs"][0]["status"] = "stale"
    stale_error = "Active cannot proceed with stale authority_refs"
    if stale_error not in validate(stale_authority):
        raise SystemExit("Active Goal accepted stale authority evidence")

    silent_goal_change = copy.deepcopy(valid_contract)
    silent_goal_change["state_revision"] = 2
    silent_goal_change["objective"] = "被摘要悄悄改写的目标"
    goal_change_error = "load-bearing Goal fields changed without goal_transition"
    if goal_change_error not in validate(silent_goal_change, valid_contract):
        raise SystemExit("Goal objective changed without an explicit Owner transition")

    revived_exclusion = copy.deepcopy(valid_contract)
    revived_exclusion["state_revision"] = 2
    revived_exclusion["excluded_options"] = []
    revived_exclusion["confirmed_decisions"].append("B")
    revived_exclusion["execution_basis"].append("B")
    revival_error = "decision B cannot move directly from excluded to confirmed"
    if revival_error not in validate(revived_exclusion, valid_contract):
        raise SystemExit("excluded option silently revived as an execution basis")

    promoted_pending = copy.deepcopy(valid_contract)
    promoted_pending["state_revision"] = 2
    promoted_pending["pending_items"] = []
    promoted_pending["confirmed_decisions"].append("C")
    promotion_error = "decision C changed from pending to confirmed without Owner evidence"
    if promotion_error not in validate(promoted_pending, valid_contract):
        raise SystemExit("pending decision became confirmed without Owner evidence")

    changed_authority = copy.deepcopy(valid_contract)
    changed_authority["state_revision"] = 2
    changed_authority["authority_refs"][0]["authority_revision"] = "G-17-r2"
    changed_authority["authority_refs"][0]["fingerprint"] = "sha256:fixture-goal-ledger-r2"
    authority_change_error = (
        "authority_ref docs/goal-ledger.md#G-17 changed without recheck_evidence or stale status; "
        "current status requires fresh recheck_evidence and later observed_at"
    )
    if authority_change_error not in validate(changed_authority, valid_contract):
        raise SystemExit("changed authority source stayed current without recheck evidence")

    removed_exclusion = copy.deepcopy(valid_contract)
    removed_exclusion["state_revision"] = 2
    removed_exclusion["excluded_options"] = []
    disappearance_error = "decision B must not disappear across state revisions"
    if disappearance_error not in validate(removed_exclusion, valid_contract):
        raise SystemExit("excluded option disappeared without a transition tombstone")

    valid_promotion = copy.deepcopy(valid_contract)
    valid_promotion["state_revision"] = 2
    valid_promotion["pending_items"] = []
    valid_promotion["confirmed_decisions"].append("C")
    valid_promotion["execution_basis"].append("C")
    valid_promotion["decision_transitions"] = [
        {
            "decision": "C",
            "from": "pending",
            "to": "confirmed",
            "owner": "product owner",
            "evidence_ref": "docs/goal-ledger.md#G-17/decision-C",
            "evidence_fingerprint": "sha256:fixture-decision-C",
        }
    ]
    valid_promotion["goal_transition"] = {
        "changed_fields": ["execution_basis"],
        "owner": "goal owner",
        "reason": "将已确认 C 纳入执行依据",
        "evidence_ref": "docs/goal-ledger.md#G-17/decision-C",
        "evidence_fingerprint": "sha256:fixture-decision-C",
    }
    if errors := validate(valid_promotion, valid_contract):
        raise SystemExit(f"Owner-backed pending decision promotion rejected: {errors}")

    valid_goal_change = copy.deepcopy(valid_contract)
    valid_goal_change["state_revision"] = 2
    valid_goal_change["objective"] = "按 Owner 新裁决修复长任务恢复能力"
    valid_goal_change["goal_transition"] = {
        "changed_fields": ["objective"],
        "owner": "goal owner",
        "reason": "Owner 收窄目标",
        "evidence_ref": "docs/goal-ledger.md#G-17/goal-transition-r2",
        "evidence_fingerprint": "sha256:fixture-goal-transition-r2",
    }
    if errors := validate(valid_goal_change, valid_contract):
        raise SystemExit(f"Owner-backed Goal transition rejected: {errors}")

    valid_recheck = copy.deepcopy(changed_authority)
    valid_recheck["authority_refs"][0]["observed_at"] = "2026-01-02T00:00:00Z"
    valid_recheck["authority_refs"][0]["recheck_evidence"] = "Checker readback V-2"
    if errors := validate(valid_recheck, valid_contract):
        raise SystemExit(f"rechecked authority revision rejected: {errors}")

    valid_supersession = copy.deepcopy(valid_contract)
    valid_supersession["state_revision"] = 2
    old_authority = valid_supersession["authority_refs"][0]
    old_authority["status"] = "superseded"
    old_authority["superseded_by"] = "docs/goal-ledger.md#G-17-r2"
    valid_supersession["authority_refs"].append(
        {
            "ref": "docs/goal-ledger.md#G-17-r2",
            "authority_revision": "G-17-r2",
            "fingerprint": "sha256:fixture-goal-ledger-r2",
            "observed_at": "2026-01-02T00:00:00Z",
            "recheck_on": ["source revision or fingerprint changes"],
            "status": "current",
            "supersedes": "docs/goal-ledger.md#G-17",
        }
    )
    if errors := validate(valid_supersession, valid_contract):
        raise SystemExit(f"authority supersession tombstone rejected: {errors}")

    rewritten_first_supersession = copy.deepcopy(valid_supersession)
    rewritten_first_supersession["authority_refs"][0]["authority_revision"] = "rewritten-r0"
    rewritten_first_supersession["authority_refs"][0]["fingerprint"] = (
        "sha256:rewritten-r0"
    )
    rewritten_first_supersession["authority_refs"][0]["observed_at"] = (
        "2026-01-02T00:00:00Z"
    )
    first_supersession_error = (
        "authority_ref docs/goal-ledger.md#G-17 first supersession must preserve the previous entry"
    )
    if first_supersession_error not in validate(
        rewritten_first_supersession, valid_contract
    ):
        raise SystemExit("first authority supersession rewrote the retained tombstone")

    stale_previous = copy.deepcopy(valid_contract)
    stale_previous["status"] = "Blocked"
    stale_previous["authority_refs"][0]["status"] = "stale"
    stale_reactivated = copy.deepcopy(stale_previous)
    stale_reactivated["state_revision"] = 2
    stale_reactivated["status"] = "Active"
    stale_reactivated["authority_refs"][0]["status"] = "current"
    stale_reactivation_error = (
        "authority_ref docs/goal-ledger.md#G-17 cannot move from stale to current without fresh recheck_evidence and later observed_at"
    )
    if stale_reactivation_error not in validate(stale_reactivated, stale_previous):
        raise SystemExit("stale authority returned to current without recheck evidence")
    valid_stale_recheck = copy.deepcopy(stale_reactivated)
    valid_stale_recheck["authority_refs"][0]["observed_at"] = "2026-01-02T00:00:00Z"
    valid_stale_recheck["authority_refs"][0]["recheck_evidence"] = "Checker readback V-2"
    if errors := validate(valid_stale_recheck, stale_previous):
        raise SystemExit(f"rechecked stale authority could not return to current: {errors}")
    stale_with_old_recheck = copy.deepcopy(stale_previous)
    stale_with_old_recheck["authority_refs"][0]["recheck_evidence"] = "old readback V-0"
    replayed_recheck = copy.deepcopy(stale_reactivated)
    replayed_recheck["authority_refs"][0]["recheck_evidence"] = "old readback V-0"
    if stale_reactivation_error not in validate(replayed_recheck, stale_with_old_recheck):
        raise SystemExit("stale authority replayed previous recheck evidence")
    older_observation = copy.deepcopy(stale_reactivated)
    older_observation["authority_refs"][0]["recheck_evidence"] = "new readback V-2"
    older_observation["authority_refs"][0]["observed_at"] = "2025-12-31T23:59:59Z"
    if stale_reactivation_error not in validate(older_observation, stale_previous):
        raise SystemExit("stale authority used an older observed_at as fresh evidence")
    equivalent_observation = copy.deepcopy(stale_reactivated)
    equivalent_observation["authority_refs"][0]["recheck_evidence"] = "new readback V-2"
    equivalent_observation["authority_refs"][0]["observed_at"] = "2026-01-01T00:00:00+00:00"
    if stale_reactivation_error not in validate(equivalent_observation, stale_previous):
        raise SystemExit("stale authority rewrote the same observed_at instant")

    revived_tombstone = copy.deepcopy(valid_supersession)
    revived_tombstone["state_revision"] = 3
    revived_tombstone["authority_refs"][0]["status"] = "current"
    revived_tombstone["authority_refs"][0].pop("superseded_by")
    revived_tombstone["authority_refs"][1].pop("supersedes")
    tombstone_revival_error = (
        "authority_ref docs/goal-ledger.md#G-17 superseded tombstone must remain immutable"
    )
    if tombstone_revival_error not in validate(revived_tombstone, valid_supersession):
        raise SystemExit("superseded authority tombstone was revived")
    rewritten_tombstone = copy.deepcopy(valid_supersession)
    rewritten_tombstone["state_revision"] = 3
    rewritten_tombstone["authority_refs"][0]["authority_revision"] = "rewritten-r0"
    rewritten_tombstone["authority_refs"][0]["fingerprint"] = "sha256:rewritten-r0"
    rewritten_tombstone["authority_refs"][0]["observed_at"] = "2026-01-03T00:00:00Z"
    rewritten_tombstone["authority_refs"][0]["recheck_evidence"] = "rewrite V-3"
    if tombstone_revival_error not in validate(rewritten_tombstone, valid_supersession):
        raise SystemExit("superseded authority tombstone history was rewritten")

    previous_basis = copy.deepcopy(valid_contract)
    previous_basis["confirmed_decisions"].append("D-2")
    changed_basis = copy.deepcopy(previous_basis)
    changed_basis["state_revision"] = 2
    changed_basis["execution_basis"] = ["D-2"]
    if goal_change_error not in validate(changed_basis, previous_basis):
        raise SystemExit("execution_basis changed without an explicit Goal transition")

    malformed_transition = copy.deepcopy(valid_contract)
    malformed_transition["decision_transitions"] = [
        {
            "decision": "C",
            "from": [],
            "to": "confirmed",
            "owner": "owner",
            "evidence_ref": "decision-C",
            "evidence_fingerprint": "sha256:C",
        }
    ]
    try:
        malformed_transition_errors = validate(malformed_transition)
    except TypeError as exc:
        raise SystemExit(f"malformed decision transition raised TypeError: {exc}") from exc
    if not any(error.startswith("decision_transitions[0] from must be one of") for error in malformed_transition_errors):
        raise SystemExit("malformed decision transition missed type error")
    without_graph = dict(valid_contract)
    without_graph.pop("work_graph")
    if errors := validate(without_graph):
        raise SystemExit(f"optional work_graph broke legacy contract: {errors}")
    invalid_loop_status = dict(valid_contract)
    invalid_loop_status["status"] = "Loop Active [engineering]"
    if not any(error.startswith("status must be one of") for error in validate(invalid_loop_status)):
        raise SystemExit("execution profile was accepted as a Goal status")
    malformed_errors = validate_work_graph({"revision": "2", "nodes": [{"id": "A", "status": [], "risk": []}]})
    if "work_graph revision must be a positive integer" not in malformed_errors:
        raise SystemExit(f"malformed work_graph missed type errors: {malformed_errors}")
    invalid_errors = validate(read_contract(fixtures / "state-contract-invalid.json"))
    expected = {
        "execution_basis must contain confirmed decisions only",
        "recovery_entry must be a non-empty string",
        "no_progress_limit must not exceed max_iterations",
        "work_graph revision > 1 requires revision_reason and revision_evidence",
        "work_graph node C depends on unknown node missing",
        "work_graph dependencies must be acyclic",
        "work_graph node A cannot be Running before dependency B is Verified",
        "work_graph node B cannot be Ready before dependency A is Verified",
        "work_graph nodes A and B in parallel group unsafe have overlapping write_scope: wise-agent <-> wise-agent/SKILL.md",
        "work_graph high-risk node B requires checker",
        "work_graph Verified node C requires evidence",
        "work_graph Verified node C requires evidence_refs",
        "work_graph Cancelled node D requires status_reason and evidence",
        "work_graph revision > 1 requires previous contract validation",
    }
    missing = expected - set(invalid_errors)
    if missing:
        raise SystemExit(f"invalid fixture missed errors: {sorted(missing)}; got={invalid_errors}")

    escaped_scope = copy.deepcopy(valid_contract)
    escaped_scope["work_graph"]["nodes"][1]["write_scope"] = ["outside-authorized-scope"]
    expected_scope_error = (
        "work_graph node B write_scope outside-authorized-scope is outside contract write_scope"
    )
    if expected_scope_error not in validate(escaped_scope):
        raise SystemExit("work_graph allowed node write_scope outside the contract grant")

    closed_with_pending = copy.deepcopy(valid_contract)
    closed_with_pending["status"] = "Closed"
    closed_with_pending["verification_evidence"] = ["Goal summary"]
    expected_closed_error = (
        "Closed requires every work_graph node to be Verified or Cancelled; non-terminal: B, C, D"
    )
    if expected_closed_error not in validate(closed_with_pending):
        raise SystemExit("Closed Goal allowed unfinished work_graph nodes")

    verified_before_dependency = copy.deepcopy(valid_contract)
    graph_nodes = verified_before_dependency["work_graph"]["nodes"]
    graph_nodes[0]["status"] = "Pending"
    graph_nodes[0]["evidence"] = []
    graph_nodes[1]["status"] = "Verified"
    graph_nodes[1]["evidence"] = ["fake verification"]
    expected_dependency_error = "work_graph node B cannot be Verified before dependency A is Verified"
    if expected_dependency_error not in validate(verified_before_dependency):
        raise SystemExit("Verified node bypassed an unfinished dependency")

    self_reported_verification = copy.deepcopy(valid_contract)
    self_reported_node = self_reported_verification["work_graph"]["nodes"][0]
    self_reported_node["evidence"] = ["Implementation Maker reports tests passed"]
    self_reported_node.pop("evidence_refs")
    self_report_error = "work_graph Verified node A requires evidence_refs"
    if self_report_error not in validate(self_reported_verification):
        raise SystemExit("work_graph accepted a Maker self-report as verification evidence")

    model_assertion_ref = copy.deepcopy(valid_contract)
    model_assertion_ref["work_graph"]["nodes"][0]["evidence_refs"][0]["type"] = "model_assertion"
    if not any(
        error.startswith("work_graph node A evidence_refs[0] type must be one of")
        for error in validate(model_assertion_ref)
    ):
        raise SystemExit("work_graph accepted model_assertion as a reality anchor")

    validator_only = copy.deepcopy(valid_contract)
    validator_only["work_graph"]["nodes"][0]["evidence_refs"][0]["type"] = "validator"
    validator_only_error = (
        "work_graph Verified node A requires at least one non-validator evidence_ref"
    )
    if validator_only_error not in validate(validator_only):
        raise SystemExit("work_graph accepted a validator as the only reality anchor")

    same_maker_checker = copy.deepcopy(valid_contract)
    same_maker_node = same_maker_checker["work_graph"]["nodes"][0]
    same_maker_node["risk"] = "high"
    same_maker_node["maker"] = "implementation-maker"
    same_maker_node["checker"] = "implementation-maker"
    same_maker_node["evidence_refs"].append(
        {
            "type": "independent_review",
            "ref": "reviews/G-17-A.md",
            "fingerprint": "sha256:fixture-independent-review",
            "method": "review source and test evidence",
            "result": "passed",
            "observed_at": "2026-01-01T00:00:00Z",
        }
    )
    same_maker_error = (
        "work_graph high-risk Verified node A requires checker different from maker"
    )
    if same_maker_error not in validate(same_maker_checker):
        raise SystemExit("work_graph allowed the Maker to act as its own Checker")

    missing_independent_review = copy.deepcopy(valid_contract)
    high_risk_node = missing_independent_review["work_graph"]["nodes"][0]
    high_risk_node["risk"] = "high"
    high_risk_node["maker"] = "implementation-maker"
    high_risk_node["checker"] = "independent-checker"
    independent_review_error = (
        "work_graph high-risk Verified node A requires independent_review evidence_ref"
    )
    if independent_review_error not in validate(missing_independent_review):
        raise SystemExit("work_graph allowed high-risk verification without independent review")

    legacy_previous = copy.deepcopy(valid_contract)
    legacy_previous["work_graph"]["nodes"][0].pop("evidence_refs")
    if errors := validate_previous_contract(legacy_previous):
        raise SystemExit(f"legacy previous contract cannot be migrated: {errors}")
    migrated_current = copy.deepcopy(valid_contract)
    migrated_current["state_revision"] = 2
    migrated_current["work_graph"]["revision"] = 2
    migrated_current["work_graph"]["revision_reason"] = "补充结构化证据引用"
    migrated_current["work_graph"]["revision_evidence"] = ["Migration M-1"]
    if errors := validate(migrated_current, legacy_previous):
        raise SystemExit(f"strict current rejected legacy previous migration: {errors}")

    broken_state_handoff = copy.deepcopy(valid_contract)
    broken_state_handoff["work_graph"]["state_inputs"] = ["decision_snapshot"]
    broken_state_handoff["work_graph"]["nodes"][3]["consumes"] = ["missing_report_input"]
    handoff_error = "work_graph node D consumes unavailable state key missing_report_input"
    if handoff_error not in validate(broken_state_handoff):
        raise SystemExit("work_graph allowed a broken Search -> Clean -> Report state handoff")

    broken_conditional_route = copy.deepcopy(valid_contract)
    broken_conditional_route["work_graph"]["nodes"][0]["transitions"] = [
        {"when": "blocked", "target": "missing-node"}
    ]
    route_errors = set(validate(broken_conditional_route))
    expected_route_errors = {
        "work_graph node A transition target missing-node does not exist",
        "work_graph node A transitions require exactly one default branch",
    }
    if not expected_route_errors <= route_errors:
        raise SystemExit("work_graph allowed an incomplete sensitive-check conditional route")

    unbounded_retry = copy.deepcopy(valid_contract)
    unbounded_retry["work_graph"]["nodes"][1]["failure_policy"] = {
        "max_attempts": 0,
        "on_exhausted": "retry",
    }
    retry_errors = set(validate(unbounded_retry))
    expected_retry_errors = {
        "work_graph node B failure_policy max_attempts must be a positive integer",
        "work_graph node B failure_policy on_exhausted must be fallback, stop, or human",
    }
    if not expected_retry_errors <= retry_errors:
        raise SystemExit("work_graph allowed an unbounded crawler retry policy")

    escaped_writeback = copy.deepcopy(valid_contract)
    escaped_writeback["work_graph"]["nodes"][1]["writeback"] = "../../outside.md"
    writeback_error = "work_graph node B writeback ../../outside.md is outside node write_scope"
    if writeback_error not in validate(escaped_writeback):
        raise SystemExit("work_graph allowed writeback outside the node grant")

    duplicate_output = copy.deepcopy(valid_contract)
    duplicate_output["work_graph"]["nodes"][1]["produces"] = ["shared_result"]
    duplicate_output["work_graph"]["nodes"][2]["produces"] = ["shared_result"]
    duplicate_output["work_graph"]["nodes"][3]["consumes"] = ["shared_result"]
    producer_error = "work_graph state key shared_result has multiple producers: B, C"
    if producer_error not in validate(duplicate_output):
        raise SystemExit("work_graph allowed ambiguous parallel state producers")

    route_cycle = copy.deepcopy(valid_contract)
    route_cycle["work_graph"]["nodes"][3]["transitions"] = [
        {"when": "default", "target": "A"}
    ]
    if "work_graph execution edges must be acyclic" not in validate(route_cycle):
        raise SystemExit("work_graph allowed a conditional route back edge")

    oversized_retry = copy.deepcopy(valid_contract)
    oversized_retry["work_graph"]["nodes"][3]["failure_policy"] = {
        "max_attempts": 100,
        "on_exhausted": "stop",
    }
    retry_budget_error = (
        "work_graph node D failure_policy max_attempts must not exceed contract max_iterations"
    )
    if retry_budget_error not in validate(oversized_retry):
        raise SystemExit("work_graph retry policy exceeded the Goal iteration budget")

    malformed_root = copy.deepcopy(valid_contract)
    malformed_root["status"] = []
    malformed_root["confirmed_decisions"] = [[]]
    try:
        malformed_root_errors = validate(malformed_root)
    except TypeError as exc:
        raise SystemExit(f"malformed root contract raised TypeError: {exc}") from exc
    if "status must be one of" not in "\n".join(malformed_root_errors):
        raise SystemExit(f"malformed root contract missed type errors: {malformed_root_errors}")

    valid_next_revision = copy.deepcopy(valid_contract)
    valid_next_revision["state_revision"] = 2
    if errors := validate(valid_next_revision, valid_contract):
        raise SystemExit(f"valid state-only revision rejected: {errors}")
    skipped_revision = copy.deepcopy(valid_next_revision)
    skipped_revision["work_graph"]["revision"] = 3
    skipped_revision_error = (
        "work_graph revision metadata must remain unchanged when nodes are unchanged"
    )
    if skipped_revision_error not in validate(skipped_revision, valid_contract):
        raise SystemExit("work_graph allowed revision metadata to change without node changes")

    previous_revision = copy.deepcopy(valid_contract)
    previous_revision["state_revision"] = 2
    previous_revision["work_graph"]["revision"] = 2
    previous_revision["work_graph"]["revision_reason"] = "Owner 取消 B"
    previous_revision["work_graph"]["revision_evidence"] = ["Decision D-2"]
    previous_revision["work_graph"]["nodes"][1]["status"] = "Cancelled"
    previous_revision["work_graph"]["nodes"][1]["status_reason"] = "Owner 取消 B"
    previous_revision["work_graph"]["nodes"][1]["evidence"] = ["Decision D-2"]
    revived_revision = copy.deepcopy(previous_revision)
    revived_revision["state_revision"] = 3
    revived_revision["work_graph"]["revision"] = 3
    revived_revision["work_graph"]["revision_reason"] = "重新启用 B"
    revived_revision["work_graph"]["revision_evidence"] = ["Agent note"]
    revived_revision["work_graph"]["nodes"][1]["status"] = "Ready"
    revived_revision["work_graph"]["nodes"][1]["status_reason"] = ""
    revived_revision["work_graph"]["nodes"][1]["evidence"] = []
    revival_error = "work_graph node B was Cancelled in previous revision and must not be revived"
    if revival_error not in validate(revived_revision, previous_revision):
        raise SystemExit("Cancelled work_graph node silently revived across revisions")
    deleted_tombstone = copy.deepcopy(revived_revision)
    deleted_tombstone["work_graph"]["nodes"] = [
        node for node in deleted_tombstone["work_graph"]["nodes"] if node["id"] != "B"
    ]
    tombstone_error = "work_graph Cancelled node B must remain as tombstone"
    if tombstone_error not in validate(deleted_tombstone, previous_revision):
        raise SystemExit("Cancelled work_graph tombstone disappeared across revisions")

    dropped_graph = copy.deepcopy(valid_next_revision)
    dropped_graph.pop("work_graph")
    dropped_graph_error = "current contract must retain work_graph from previous revision"
    if dropped_graph_error not in validate(dropped_graph, valid_contract):
        raise SystemExit("current contract silently dropped the previous work_graph")

    malformed_closed = copy.deepcopy(valid_contract)
    malformed_closed["status"] = "Closed"
    malformed_closed["verification_evidence"] = ["Goal summary"]
    malformed_closed["work_graph"]["nodes"][1]["status"] = []
    try:
        malformed_closed_errors = validate(malformed_closed)
    except TypeError as exc:
        raise SystemExit(f"malformed Closed work_graph raised TypeError: {exc}") from exc
    if "work_graph node B status must be one of" not in "\n".join(malformed_closed_errors):
        raise SystemExit(f"malformed Closed work_graph missed type errors: {malformed_closed_errors}")

    regression_failures: list[str] = []

    revision_two_previous = copy.deepcopy(valid_contract)
    revision_two_previous["state_revision"] = 2
    if errors := validate_previous_contract(revision_two_previous):
        regression_failures.append(
            f"revision-two previous snapshot rejected without its predecessor: {errors}"
        )

    previous_with_recheck = copy.deepcopy(valid_contract)
    previous_with_recheck["authority_refs"][0]["recheck_evidence"] = "Checker readback V-1"
    replayed_authority_recheck = copy.deepcopy(previous_with_recheck)
    replayed_authority_recheck["state_revision"] = 2
    replayed_authority_recheck["authority_refs"][0]["authority_revision"] = "G-17-r2"
    replayed_authority_recheck["authority_refs"][0]["fingerprint"] = (
        "sha256:fixture-goal-ledger-r2"
    )
    fresh_authority_error = (
        "authority_ref docs/goal-ledger.md#G-17 changed without recheck_evidence or stale status; "
        "current status requires fresh recheck_evidence and later observed_at"
    )
    if fresh_authority_error not in validate(
        replayed_authority_recheck, previous_with_recheck
    ):
        regression_failures.append(
            "changed current authority accepted replayed recheck evidence and observed_at"
        )

    stale_changed_authority = copy.deepcopy(valid_contract)
    stale_changed_authority["state_revision"] = 2
    stale_changed_authority["status"] = "Blocked"
    stale_changed_authority["authority_refs"][0]["authority_revision"] = "G-17-r2"
    stale_changed_authority["authority_refs"][0]["fingerprint"] = (
        "sha256:fixture-goal-ledger-r2"
    )
    stale_changed_authority["authority_refs"][0]["status"] = "stale"
    if errors := validate(stale_changed_authority, valid_contract):
        regression_failures.append(
            f"stale changed authority incorrectly required recheck evidence: {errors}"
        )

    state_only_revision = copy.deepcopy(valid_contract)
    state_only_revision["state_revision"] = 2
    if errors := validate(state_only_revision, valid_contract):
        regression_failures.append(
            f"state-only revision rejected unchanged work_graph revision: {errors}"
        )

    reordered_nodes = copy.deepcopy(valid_contract)
    reordered_nodes["state_revision"] = 2
    reordered_nodes["work_graph"]["nodes"].reverse()
    if errors := validate(reordered_nodes, valid_contract):
        regression_failures.append(
            f"node ordering was mistaken for work_graph semantic change: {errors}"
        )

    reordered_state_inputs = copy.deepcopy(valid_contract)
    reordered_state_inputs["state_revision"] = 2
    reordered_state_inputs["work_graph"]["state_inputs"] = [
        "secondary_context",
        "goal_ledger",
    ]
    previous_state_inputs = copy.deepcopy(valid_contract)
    previous_state_inputs["work_graph"]["state_inputs"] = [
        "goal_ledger",
        "secondary_context",
    ]
    if errors := validate(reordered_state_inputs, previous_state_inputs):
        regression_failures.append(
            f"state_inputs ordering was mistaken for work_graph semantic change: {errors}"
        )

    duplicate_state_inputs = copy.deepcopy(valid_contract)
    duplicate_state_inputs["work_graph"]["state_inputs"] = ["goal_ledger", "goal_ledger"]
    duplicate_state_inputs_error = "work_graph state_inputs must contain unique keys"
    if duplicate_state_inputs_error not in validate(duplicate_state_inputs):
        regression_failures.append("work_graph state_inputs accepted duplicate keys")

    added_state_input_without_revision = copy.deepcopy(valid_contract)
    added_state_input_without_revision["state_revision"] = 2
    added_state_input_without_revision["work_graph"]["state_inputs"].append(
        "secondary_context"
    )
    added_state_input_errors = set(
        validate(added_state_input_without_revision, valid_contract)
    )
    required_state_input_change_errors = {
        "work_graph revision must increment previous revision by one",
        "work_graph node or state_inputs changes require revision_reason and revision_evidence",
    }
    if not required_state_input_change_errors <= added_state_input_errors:
        regression_failures.append(
            "state_inputs semantic change did not require graph revision, reason, and evidence"
        )

    added_state_input_with_revision = copy.deepcopy(added_state_input_without_revision)
    added_state_input_with_revision["work_graph"]["revision"] = 2
    added_state_input_with_revision["work_graph"]["revision_reason"] = (
        "增加恢复所需初始状态"
    )
    added_state_input_with_revision["work_graph"]["revision_evidence"] = [
        "Goal recovery contract r2"
    ]
    if errors := validate(added_state_input_with_revision, valid_contract):
        regression_failures.append(
            f"valid state_inputs graph revision rejected: {errors}"
        )

    changed_node_without_revision = copy.deepcopy(valid_contract)
    changed_node_without_revision["state_revision"] = 2
    changed_node_without_revision["work_graph"]["nodes"][1]["objective"] = (
        "修改后的节点目标"
    )
    changed_node_errors = set(validate(changed_node_without_revision, valid_contract))
    required_graph_change_errors = {
        "work_graph revision must increment previous revision by one",
        "work_graph node or state_inputs changes require revision_reason and revision_evidence",
    }
    if not required_graph_change_errors <= changed_node_errors:
        regression_failures.append(
            "node semantic change did not require graph revision, reason, and evidence"
        )

    unordered_goal_change = copy.deepcopy(valid_contract)
    unordered_goal_change["state_revision"] = 2
    unordered_goal_change["objective"] = "收窄后的恢复目标"
    unordered_goal_change["confirmed_decisions"].append("D-2")
    unordered_goal_change["execution_basis"] = ["D-2"]
    unordered_goal_change["decision_transitions"] = [
        {
            "decision": "D-2",
            "from": "new",
            "to": "confirmed",
            "owner": "goal owner",
            "evidence_ref": "docs/goal-ledger.md#G-17/decision-D-2",
            "evidence_fingerprint": "sha256:fixture-decision-D-2",
        }
    ]
    unordered_goal_change["goal_transition"] = {
        "changed_fields": ["objective", "execution_basis"],
        "owner": "goal owner",
        "reason": "Owner 同时收窄目标并切换执行依据",
        "evidence_ref": "docs/goal-ledger.md#G-17/goal-transition-r2",
        "evidence_fingerprint": "sha256:fixture-goal-transition-r2",
    }
    exact_goal_fields_error = (
        "goal_transition changed_fields must exactly match changed Goal fields"
    )
    if exact_goal_fields_error in validate(unordered_goal_change, valid_contract):
        regression_failures.append("goal_transition changed_fields was order-sensitive")

    duplicate_goal_fields = copy.deepcopy(unordered_goal_change)
    duplicate_goal_fields["goal_transition"]["changed_fields"].append("objective")
    duplicate_goal_fields_error = (
        "goal_transition changed_fields must not contain duplicates"
    )
    if duplicate_goal_fields_error not in validate(duplicate_goal_fields, valid_contract):
        regression_failures.append("goal_transition changed_fields accepted duplicates")

    if regression_failures:
        raise SystemExit("regression failures: " + "; ".join(regression_failures))
    print("OK wise-agent state contract self-test")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, help="state contract JSON file")
    parser.add_argument("--previous", type=Path, help="previous state contract for revision transition checks")
    parser.add_argument("--self-test", action="store_true", help="run bundled fixture checks")
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0
    if args.path is None:
        parser.error("path is required unless --self-test is used")
    try:
        current_contract = read_contract(args.path)
        previous_contract = read_contract(args.previous) if args.previous else None
        if previous_contract is not None:
            previous_errors = validate_previous_contract(previous_contract)
            if previous_errors:
                for error in previous_errors:
                    print(f"ERROR {args.previous}: {error}", file=sys.stderr)
                return 1
        errors = validate(current_contract, previous_contract)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ERROR {args.path}: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR {args.path}: {error}", file=sys.stderr)
        return 1
    print(f"OK wise-agent state contract: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
