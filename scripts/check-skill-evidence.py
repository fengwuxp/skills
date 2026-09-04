#!/usr/bin/env python3
"""Verify the declared Skill delivery gate before synchronization.

Input: one Skill directory and its repository-relative evidence_gates.
Output: pass/fail readiness at the declared structural, contract, or scored mode.
Writes/network: none. The checker evaluates artifacts in memory and never invokes an Agent.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = Path(__file__).resolve().with_name("evaluate-skill-behavior.py")
MANIFEST = Path("fixtures/skill-eval/evidence-gates.json")
CONTRACT_GATE_KEYS = {"cases"}
SCORED_GATE_KEYS = {"cases", "responses", "scores", "seed"}
EVIDENCE_MODES = {"structural-only", "contract-only", "behavior-scored"}
UNASSIGNED_CASE_FILES = {
    # Generic evaluator self-test corpus; it is not owned by one Skill.
    "behavior-cases.json",
}


def readiness_summary(skill: str, evidence_mode: str) -> str:
    if evidence_mode == "structural-only":
        return f"OK skill structure: {skill} (mode=structural-only)"
    if evidence_mode == "contract-only":
        return (
            f"OK skill contract: {skill} "
            "(mode=contract-only; source-profile freshness=deferred)"
        )
    return f"OK skill evidence: {skill} (mode=behavior-scored)"


def load_evaluator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "skill_behavior_evaluator_for_evidence_gate", EVALUATOR_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def resolve_file(repository_root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: expected a repository-relative path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"{label}: path must stay under repository root")
    root = repository_root.resolve(strict=True)
    try:
        path = (root / relative).resolve(strict=True)
        path.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ValueError(f"{label}: missing or outside repository root: {value}") from exc
    if not path.is_file():
        raise ValueError(f"{label}: expected a file: {value}")
    return path


def load_manifest(repository_root: Path) -> dict[str, list[dict[str, Any]]]:
    path = repository_root / MANIFEST
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"version", "skills"}:
        raise ValueError(f"{path}: expected version and skills")
    if data.get("version") != 1 or not isinstance(data.get("skills"), dict):
        raise ValueError(f"{path}: expected version 1 and a skills object")
    result: dict[str, list[dict[str, Any]]] = {}
    for skill, gates in data["skills"].items():
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError(f"{path}: skill IDs must be non-empty strings")
        if not isinstance(gates, list) or not gates:
            raise ValueError(f"{path}: {skill} must declare a non-empty gate list")
        seen_cases: set[str] = set()
        normalized: list[dict[str, Any]] = []
        for index, gate in enumerate(gates, start=1):
            label = f"{path}: {skill} evidence_gate[{index}]"
            if not isinstance(gate, dict):
                raise ValueError(f"{label} must be an object")
            keys = set(gate)
            if keys not in (CONTRACT_GATE_KEYS, SCORED_GATE_KEYS):
                raise ValueError(
                    f"{label} must declare cases only or cases, responses, scores, and seed"
                )
            for field in keys - {"seed"}:
                value = gate.get(field)
                relative = Path(value) if isinstance(value, str) else Path("/")
                if (
                    not isinstance(value, str)
                    or not value.strip()
                    or relative.is_absolute()
                    or ".." in relative.parts
                ):
                    raise ValueError(f"{label}.{field} must be repository-relative")
            if keys == SCORED_GATE_KEYS and (
                not isinstance(gate.get("seed"), int)
                or isinstance(gate.get("seed"), bool)
            ):
                raise ValueError(f"{label}.seed must be an integer")
            cases = gate["cases"]
            if cases in seen_cases:
                raise ValueError(f"{label}.cases duplicates {cases}")
            seen_cases.add(cases)
            normalized.append(gate)
        result[skill] = normalized
    return result


def validate_case_contract(
    evaluator: ModuleType,
    case_data: dict[str, Any],
    evidence_mode: str,
) -> None:
    """Validate case shape without treating contract-only fixtures as live evidence."""
    if evidence_mode == "contract-only":
        contract_data = dict(case_data)
        contract_data.pop("source_profiles", None)
        contract_data.pop("input_profile", None)
        evaluator.validate_cases(contract_data)
        return
    evaluator.validate_cases(case_data)


def audit_evidence(
    skill_dir: Path, repository_root: Path = ROOT
) -> list[str]:
    admission_path = skill_dir / "admission.json"
    try:
        admission = json.loads(admission_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{admission_path}: cannot read admission metadata: {exc}"]
    evidence_mode = admission.get("evidence_mode") if isinstance(admission, dict) else None
    if evidence_mode not in EVIDENCE_MODES:
        return [
            f"{admission_path}: evidence_mode must be one of {sorted(EVIDENCE_MODES)}"
        ]
    try:
        manifest = load_manifest(repository_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    gates = manifest.get(skill_dir.name, [])
    scored_gate_count = sum(
        1
        for gate in gates
        if isinstance(gate, dict) and set(gate) == SCORED_GATE_KEYS
    )
    if evidence_mode == "behavior-scored" and scored_gate_count == 0:
        return [
            f"{skill_dir.name}: behavior-scored requires at least one scored evidence gate"
        ]
    if evidence_mode == "contract-only" and scored_gate_count:
        return [
            f"{skill_dir.name}: contract-only cannot declare scored evidence gates"
        ]
    if evidence_mode == "contract-only" and not gates:
        return [f"{skill_dir.name}: contract-only requires at least one case gate"]
    if evidence_mode == "structural-only" and gates:
        return [f"{skill_dir.name}: structural-only cannot declare behavior gates"]
    if not gates:
        return []

    evaluator = load_evaluator()
    previous_root = evaluator.ROOT
    evaluator.ROOT = repository_root.resolve(strict=True)
    failures: list[str] = []
    try:
        for index, gate in enumerate(gates, start=1):
            label = f"evidence_gate[{index}]"
            try:
                if not isinstance(gate, dict):
                    raise ValueError(f"{label}: expected an object")
                cases_path = resolve_file(
                    repository_root, gate.get("cases"), f"{label}.cases"
                )
                case_data = evaluator.load_json(cases_path)
                validate_case_contract(evaluator, case_data, evidence_mode)
                scored_fields = {"responses", "scores", "seed"}
                present = scored_fields & set(gate)
                if not present:
                    continue
                if present != scored_fields:
                    raise ValueError(
                        f"{label}: responses, scores, and seed must be declared together"
                    )
                responses_path = resolve_file(
                    repository_root, gate.get("responses"), f"{label}.responses"
                )
                scores_path = resolve_file(
                    repository_root, gate.get("scores"), f"{label}.scores"
                )
                seed = gate.get("seed")
                if not isinstance(seed, int) or isinstance(seed, bool):
                    raise ValueError(f"{label}.seed: expected an integer")
                responses = evaluator.read_jsonl(responses_path)
                blind_rows, key = evaluator.blind_responses(
                    case_data, responses, seed=seed
                )
                scores = evaluator.read_jsonl(scores_path)
                report = evaluator.score_judgments(
                    case_data,
                    scores,
                    key,
                    blind_rows=blind_rows,
                )
                if not report["passed"]:
                    reasons = "; ".join(report.get("reasons", [])) or "release gate failed"
                    raise ValueError(f"{label}: {reasons}")
            except (OSError, ValueError, json.JSONDecodeError, evaluator.ContractError) as exc:
                failures.append(f"{skill_dir.name} {label}: {exc}")
    finally:
        evaluator.ROOT = previous_root
    return failures


def audit_repository(repository_root: Path = ROOT) -> list[str]:
    try:
        manifest = load_manifest(repository_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    known_skills = {
        skill_md.parent.name for skill_md in repository_root.glob("*/SKILL.md")
    }
    failures = [
        f"evidence manifest references unknown skill {skill}"
        for skill in sorted(set(manifest) - known_skills)
    ]
    referenced_cases = {
        Path(gate["cases"]).name
        for gates in manifest.values()
        for gate in gates
        if isinstance(gate, dict) and isinstance(gate.get("cases"), str)
    }
    unassigned_cases = sorted(
        path.name
        for path in (repository_root / "fixtures" / "skill-eval").glob(
            "*-behavior-cases.json"
        )
        if path.name not in referenced_cases and path.name not in UNASSIGNED_CASE_FILES
    )
    failures.extend(
        f"behavior case is not declared in evidence manifest: {name}"
        for name in unassigned_cases
    )
    failures.extend(
        [
            failure
            for skill_md in sorted(repository_root.glob("*/SKILL.md"))
            for failure in audit_evidence(skill_md.parent, repository_root)
        ]
    )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, help="check one top-level Skill directory")
    parser.add_argument(
        "--repository-root", type=Path, default=ROOT, help="repository root"
    )
    args = parser.parse_args()
    repository_root = args.repository_root.resolve(strict=True)
    failures = (
        audit_evidence(args.skill.resolve(strict=True), repository_root)
        if args.skill
        else audit_repository(repository_root)
    )
    if failures:
        print("FAIL skill evidence")
        for failure in failures:
            print(f"- {failure}")
        return 1
    target = args.skill.name if args.skill else "repository"
    if args.skill:
        metadata = json.loads((args.skill.resolve() / "admission.json").read_text(encoding="utf-8"))
        print(readiness_summary(target, metadata["evidence_mode"]))
    else:
        print(
            "OK skill delivery gates: repository "
            "(contract-only source-profile freshness=deferred)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
