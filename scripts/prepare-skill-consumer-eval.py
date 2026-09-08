#!/usr/bin/env python3
"""Prepare a local consumer fixture without executing a model or its task.

Input: checked-in cases and an explicit new directory under /tmp.
Output: staged Skill, synthetic project, task and hash receipt in that directory.
Uses only the repository sync script, first dry-run then temporary staging.
No network, credentials, user configuration copy or real installation writes.
Failure retains local setup evidence without a receipt; no retries or deletion.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "fixtures/skill-eval/skill-consumer-behavior-cases.json"
PROJECT = ROOT / "fixtures/skill-eval/consumer-project"
SKILL = "senior-software-architect"


def load_cases():
    return json.loads(CASES.read_text(encoding="utf-8"))


def validate_consumer_cases(data):
    if not isinstance(data, dict) or {"source_profiles", "input_profile"} & data.keys():
        raise ValueError("consumer cases must not declare source injection profiles")
    spec = importlib.util.spec_from_file_location(
        "consumer_behavior_contract", ROOT / "scripts/evaluate-skill-behavior.py"
    )
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    evaluator.validate_cases(data)
    setup = data.get("consumer_setup", {})
    if not isinstance(setup, dict) or setup.get("skill") != SKILL:
        raise ValueError(f"consumer setup must stage only {SKILL}")
    profiles = setup.get("host_profiles")
    if not isinstance(profiles, dict) or set(profiles) != {"minimal", "approval"}:
        raise ValueError("consumer setup requires minimal and approval host profiles")
    if profiles["minimal"] is not None or not isinstance(profiles["approval"], str) or not profiles["approval"].strip():
        raise ValueError("minimal must omit policy; approval must provide policy")
    for case in data["cases"]:
        if case.get("host_profile") not in profiles:
            raise ValueError(f"unknown host profile: {case['id']}")
        writes = case.get("write_paths")
        if not isinstance(writes, list) or any(path not in ("labels.py", "report.md") for path in writes):
            raise ValueError(f"unsupported consumer write paths: {case['id']}")
        if case["host_profile"] == "approval" and writes:
            raise ValueError("pending approval case must have no writable paths")


def prepare_case(data, case_id, output_dir):
    validate_consumer_cases(data)
    case = next((case for case in data["cases"] if case["id"] == case_id), None)
    if case is None:
        raise ValueError(f"unknown consumer case: {case_id}")
    requested = Path(output_dir)
    output = requested.resolve()
    home = Path.home()
    protected = tuple(path.resolve() for path in (
        ROOT, home / ".codex", home / ".agents",
        Path(os.environ.get("CODEX_HOME", home / ".codex")),
    ))
    if (not requested.is_absolute() or requested.exists() or requested.is_symlink()
            or not output.is_relative_to(Path("/tmp").resolve())
            or any(output.is_relative_to(path) for path in protected)
            or not output.parent.is_dir()):
        raise ValueError("output must be a new directory under /tmp, outside source and runtime roots")
    output.mkdir(mode=0o700)
    environment = dict(os.environ, CODEX_HOME=str(output / "codex-home"),
                       PYTHONDONTWRITEBYTECODE="1")
    with (output / "setup.log").open("w", encoding="utf-8") as log:
        for options in (("--dry-run", SKILL), (SKILL,)):
            command = ["bash", str(ROOT / "sync-skills.sh"), *options]
            result = subprocess.run(command, cwd=ROOT, env=environment,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            log.write(result.stdout)
            log.flush()
            if result.returncode:
                raise RuntimeError(f"sync failed ({result.returncode}); see {output / 'setup.log'}")
    project = output / "project"
    shutil.copytree(PROJECT, project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    policy = data["consumer_setup"]["host_profiles"][case["host_profile"]]
    if policy is not None:
        (project / "AGENTS.md").write_text(policy, encoding="utf-8")
        (project / "approval.md").write_text("PENDING\n", encoding="utf-8")
    (output / "task.txt").write_text(case["prompt"] + "\n", encoding="utf-8")
    fingerprints = {}
    for path in sorted(output.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"unexpected staged symbolic link: {path}")
        if path.is_file() and path.name != "setup.log":
            fingerprints[path.relative_to(output).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {
        "version": 1,
        "case_id": case_id,
        "preparation_contract_sha256": hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "skill": SKILL,
        "host_profile": case["host_profile"],
        "write_paths": case["write_paths"],
        "execution_status": "NOT_RUN",
        "loading_status": "NOT_VERIFIED",
        "files_sha256": fingerprints,
    }
    (output / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate", action="store_true", help="check offline preparation contract only")
    action.add_argument("--case", help="case ID to prepare; does not execute the task")
    parser.add_argument("--output-dir", type=Path, help="explicit new directory under /tmp")
    args = parser.parse_args()
    if bool(args.output_dir) != bool(args.case):
        parser.error("--output-dir is required only with --case")
    try:
        data = load_cases()
        if args.validate:
            validate_consumer_cases(data)
            print(f"OK consumer preparation cases={len(data['cases'])}; live behavior NOT_RUN")
        else:
            prepare_case(data, args.case, args.output_dir)
            print(f"OK prepared {args.output_dir}; execution NOT_RUN; loading NOT_VERIFIED")
    except (ValueError, RuntimeError, OSError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
