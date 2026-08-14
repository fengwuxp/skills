#!/usr/bin/env python3
"""Manage the opt-in, candidate-only wise-agent learning ledger.

Input: explicit current-task evidence supplied on the command line.
Output: mode.json and candidate Markdown records under SKILL_LEARNING_HOME.
Writes: only the selected learning home; never the repository or Codex Skills.
Network: never. Git and Skill promotion: unsupported by design.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import stat
import sys
import tempfile
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(?:身份证(?:号|号码)?|identity[-_ ]?card)\s*[:：=]?\s*\d{17}[\dXx]"),
    re.compile(r"(?i)(?:手机号|手机号码|联系电话|mobile|phone)\s*[:：=]?\s*1[3-9]\d{9}"),
    re.compile(r"(?i)(?:银行卡(?:号|号码)?|bank[-_ ]?card|card[-_ ]?number)\s*[:：=]?\s*\d[\d -]{11,25}\d"),
    re.compile(r"(?:用户|本人|我|其|他|她)\s*(?:目前|曾经|已经|曾)?\s*(?:患有|得了|被?确诊(?:为|患有)?|信奉|信仰|皈依|支持|加入(?:了)?)"),
    re.compile(r"(?:用户|本人|我|其|他|她)\s*(?:是|为)\s*[^。；，,\n]{0,16}(?:患者|病人|教徒|党员)"),
)
ACTIVE_STATUSES = {"candidate", "confirmed"}
EVIDENCE_KINDS = {
    "repeated-failure",
    "confirmed-correction",
    "validator-failure",
    "cr-root-cause",
    "source-staleness",
}
DEFAULT_MODE = {
    "schema_version": 1,
    "status": "enabled",
    "scope": "wise-agent-and-loaded-skills",
    "write_policy": "candidate-only",
    "read_policy": "dedup-and-explicit-review-only",
    "evidence_policy": "current-task-explicit-evidence-only",
    "candidate_write_grant": True,
    "history_scan": False,
    "auto_confirm": False,
    "auto_promote": False,
    "git_actions": False,
}


def learning_home(value: str | None = None) -> Path:
    base = value or os.environ.get("SKILL_LEARNING_HOME") or "~/.skill-learning"
    return Path(base).expanduser().resolve() / "wise-agent"


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_home(root: Path) -> None:
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve()
    if is_within(root, codex_home / "skills"):
        raise ValueError("learning home must not be inside the Codex Skills installation")
    for parent in (root, *root.parents):
        if (parent / ".git").exists():
            raise ValueError("learning home must not be inside a Git repository")


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    metadata = os.lstat(path)
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise ValueError(f"{path.name} must be a real directory")
    os.chmod(path, 0o700)


def require_single_regular_file(path: Path, metadata: os.stat_result) -> None:
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{path.name} must be a regular file")
    if metadata.st_nlink != 1:
        raise ValueError(f"{path.name} must not have hard links")


def open_regular(path: Path, flags: int, mode: int = 0o600) -> int:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    nonblock = getattr(os, "O_NONBLOCK", 0)
    truncate = bool(flags & os.O_TRUNC)
    open_flags = (flags & ~os.O_TRUNC) | nofollow | nonblock
    try:
        before = os.lstat(path)
    except FileNotFoundError:
        before = None
        if flags & os.O_CREAT:
            open_flags |= os.O_EXCL
    else:
        require_single_regular_file(path, before)
    descriptor = os.open(path, open_flags, mode)
    try:
        after = os.fstat(descriptor)
        require_single_regular_file(path, after)
        if before is not None and (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
            raise ValueError(f"{path.name} changed while being opened")
        if truncate:
            os.ftruncate(descriptor, 0)
        os.fchmod(descriptor, 0o600)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def write_all(descriptor: int, content: bytes) -> None:
    remaining = content
    while remaining:
        written = os.write(descriptor, remaining)
        if written <= 0:
            raise OSError("file write made no progress")
        remaining = remaining[written:]
    os.fsync(descriptor)


def read_private_text(path: Path) -> str:
    descriptor = open_regular(path, os.O_RDONLY)
    try:
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 65536):
            chunks.append(chunk)
        return b"".join(chunks).decode("utf-8")
    finally:
        os.close(descriptor)


def write_private_text(path: Path, content: str) -> None:
    descriptor = open_regular(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    try:
        write_all(descriptor, content.encode("utf-8"))
    finally:
        os.close(descriptor)


def atomic_write_json(path: Path, value: dict[str, object]) -> None:
    ensure_private_dir(path.parent)
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor = open_regular(path, os.O_RDWR | os.O_CREAT)
    try:
        old = b""
        while chunk := os.read(descriptor, 65536):
            old += chunk
        try:
            os.lseek(descriptor, 0, os.SEEK_SET)
            os.ftruncate(descriptor, 0)
            write_all(descriptor, payload)
        except BaseException:
            os.lseek(descriptor, 0, os.SEEK_SET)
            os.ftruncate(descriptor, 0)
            write_all(descriptor, old)
            raise
    finally:
        os.close(descriptor)


def mode_path(root: Path) -> Path:
    return root / "mode.json"


def read_mode(root: Path) -> dict[str, object]:
    path = mode_path(root)
    try:
        raw = read_private_text(path)
    except FileNotFoundError:
        raise ValueError(f"learning mode is not initialized: {path}")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("mode.json must contain an object")
    return value


def enable(root: Path) -> None:
    validate_home(root)
    ensure_private_dir(root)
    path = mode_path(root)
    if path.exists():
        current = read_mode(root)
        if current.get("schema_version") != 1:
            raise ValueError("unsupported learning mode schema")
        current.update(DEFAULT_MODE)
        atomic_write_json(path, current)
        print(f"ENABLED {path}")
        return
    atomic_write_json(path, dict(DEFAULT_MODE))
    print(f"ENABLED {path}")


def disable(root: Path) -> None:
    validate_home(root)
    current = read_mode(root)
    current["status"] = "disabled"
    current["candidate_write_grant"] = False
    atomic_write_json(mode_path(root), current)
    print(f"DISABLED {mode_path(root)}")


def require_candidate_mode(root: Path) -> dict[str, object]:
    mode = read_mode(root)
    required = {
        "status": "enabled",
        "write_policy": "candidate-only",
        "evidence_policy": "current-task-explicit-evidence-only",
        "candidate_write_grant": True,
        "history_scan": False,
        "auto_confirm": False,
        "auto_promote": False,
        "git_actions": False,
    }
    mismatches = [key for key, expected in required.items() if mode.get(key) != expected]
    if mismatches:
        raise ValueError(f"learning mode does not grant candidate-only writes: {', '.join(mismatches)}")
    return mode


def clean_text(name: str, value: str, limit: int = 2000) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{name} must not be empty")
    if len(text) > limit:
        raise ValueError(f"{name} exceeds {limit} characters")
    if any(pattern.search(text) for pattern in SENSITIVE_PATTERNS):
        raise ValueError(f"{name} appears to contain sensitive material")
    return text


def fingerprint(skill: str, observed: str, expected: str) -> str:
    normalized = "\n".join(
        " ".join(value.casefold().split())
        for value in (skill, observed, expected)
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def record_metadata(path: Path) -> tuple[str | None, str | None]:
    status = None
    record_fingerprint = None
    for line in read_private_text(path).splitlines()[:12]:
        if line.startswith("Status: "):
            status = line.removeprefix("Status: ").strip()
        elif line.startswith("Fingerprint: "):
            record_fingerprint = line.removeprefix("Fingerprint: ").strip()
    return status, record_fingerprint


def next_number(record_dir: Path) -> int:
    numbers = []
    for path in record_dir.glob("[0-9][0-9][0-9][0-9]-*.md"):
        try:
            numbers.append(int(path.name[:4]))
        except ValueError:
            continue
    return max(numbers, default=0) + 1


def write_candidate(root: Path, args: argparse.Namespace) -> Path | None:
    validate_home(root)
    require_candidate_mode(root)
    if not SKILL_ID_RE.fullmatch(args.skill):
        raise ValueError("skill must be a lowercase hyphenated Skill ID")
    if not SLUG_RE.fullmatch(args.slug):
        raise ValueError("slug must use lowercase letters, digits, and hyphens")
    if args.evidence_kind not in EVIDENCE_KINDS:
        raise ValueError(f"unsupported evidence kind: {args.evidence_kind}")
    if args.sensitivity_check != "public-safe":
        raise ValueError("sensitivity-check must be public-safe")

    observed = clean_text("observed-failure", args.observed_failure)
    expected = clean_text("expected-behavior", args.expected_behavior)
    task_ref = clean_text("task-ref", args.task_ref, 500)
    reuse_scope = clean_text("reuse-scope", args.reuse_scope, 1000)
    authority = clean_text("proposed-authority", args.proposed_authority, 1000)
    validation = clean_text("validation", args.validation, 1000)
    evidence_refs = list(dict.fromkeys(clean_text("evidence-ref", ref, 1000) for ref in args.evidence_ref))
    if args.evidence_kind == "repeated-failure" and len(evidence_refs) < 2:
        raise ValueError("repeated-failure requires at least two distinct evidence references")

    digest = fingerprint(args.skill, observed, expected)
    records_root = root / "records"
    record_dir = records_root / args.skill
    ensure_private_dir(root)
    ensure_private_dir(records_root)
    ensure_private_dir(record_dir)
    for existing in sorted(record_dir.glob("*.md")):
        status, existing_digest = record_metadata(existing)
        if status in ACTIVE_STATUSES and existing_digest == digest:
            print(f"SKIP duplicate {existing}")
            return None

    number = next_number(record_dir)
    record_id = f"LR-{number:04d}"
    path = record_dir / f"{number:04d}-{args.slug}.md"
    evidence_lines = "\n".join(f"- {ref}" for ref in evidence_refs)
    content = f"""# {record_id}: {args.slug}

Status: candidate
Target Skill: {args.skill}
Evidence Kind: {args.evidence_kind}
Task Ref: {task_ref}
Fingerprint: {digest}
Created At: {datetime.now(timezone.utc).isoformat()}
Sensitivity Check: public-safe

## Observed Failure

{observed}

## Expected Behavior

{expected}

## Evidence Refs

{evidence_lines}

## Reuse Scope

{reuse_scope}

## Proposed Authority

{authority}

## Validation

{validation}

## Promotion Boundary

This record is a candidate only. Owner confirmation, an auditable repository diff,
independent validation, Git, sync, and release remain separate actions.
"""
    write_private_text(path, content)
    print(f"RECORDED {path}")
    return path


def list_records(root: Path, skill: str | None, status_filter: str | None) -> None:
    validate_home(root)
    read_mode(root)
    records_root = root / "records"
    paths = sorted((records_root / skill).glob("*.md")) if skill else sorted(records_root.glob("*/*.md"))
    for path in paths:
        status, _ = record_metadata(path)
        if status_filter and status != status_filter:
            continue
        print(f"{status or 'unknown'}\t{path.relative_to(root)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", help="learning home; defaults to SKILL_LEARNING_HOME or ~/.skill-learning")
    parser.add_argument("--self-test", action="store_true", help="run isolated self-tests")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("enable", help="enable candidate-only learning backflow")
    subparsers.add_parser("disable", help="disable writes without deleting records")
    subparsers.add_parser("status", help="print the current mode")

    record = subparsers.add_parser("record", help="write one deduplicated candidate record")
    record.add_argument("--skill", required=True)
    record.add_argument("--slug", required=True)
    record.add_argument("--evidence-kind", required=True, choices=sorted(EVIDENCE_KINDS))
    record.add_argument("--task-ref", required=True)
    record.add_argument("--observed-failure", required=True)
    record.add_argument("--expected-behavior", required=True)
    record.add_argument("--evidence-ref", action="append", required=True)
    record.add_argument("--reuse-scope", required=True)
    record.add_argument("--proposed-authority", required=True)
    record.add_argument("--validation", required=True)
    record.add_argument("--sensitivity-check", required=True, choices=["public-safe"])

    listing = subparsers.add_parser("list", help="list records for explicit review")
    listing.add_argument("--skill")
    listing.add_argument("--status", choices=["candidate", "confirmed", "promoted", "rejected", "superseded"])
    return parser


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        shared_base = Path(temp_dir) / "shared-base"
        shared_base.mkdir(mode=0o755)
        unsafe_root = shared_base / "wise-agent"
        unsafe_root.mkdir(mode=0o700)
        victim = Path(temp_dir) / "mode-victim.txt"
        victim.write_text("KEEP", encoding="utf-8")
        mode_path(unsafe_root).with_suffix(".json.tmp").symlink_to(victim)
        enable(unsafe_root)
        assert victim.read_text(encoding="utf-8") == "KEEP", "mode write followed a temporary symlink"
        assert shared_base.stat().st_mode & 0o777 == 0o755, "enable changed the caller-owned base directory"

        root = learning_home(temp_dir)
        enable(root)
        mode = read_mode(root)
        assert mode["write_policy"] == "candidate-only"
        assert root.stat().st_mode & 0o777 == 0o700
        assert mode_path(root).stat().st_mode & 0o777 == 0o600
        args = argparse.Namespace(
            skill="wise-agent",
            slug="explicit-git-trigger",
            evidence_kind="repeated-failure",
            task_ref="fixture:wise-agent-git-trigger",
            observed_failure="Explicit Git delivery did not trigger the coordination owner.",
            expected_behavior="Explicit Git delivery loads wise-agent and checks evidence before staging.",
            evidence_ref=["fixture:red-1", "smoke:red-2"],
            reuse_scope="Explicit Git delivery prompts.",
            proposed_authority="wise-agent/SKILL.md and trigger fixtures.",
            validation="Run trigger validator and a clean-session smoke.",
            sensitivity_check="public-safe",
        )
        first = write_candidate(root, args)
        assert first is not None and first.is_file()
        assert first.stat().st_mode & 0o777 == 0o600
        assert first.parent.stat().st_mode & 0o777 == 0o700
        second = write_candidate(root, args)
        assert second is None
        different_kind = argparse.Namespace(**vars(args))
        different_kind.slug = "same-learning-different-kind"
        different_kind.evidence_kind = "confirmed-correction"
        assert write_candidate(root, different_kind) is None
        sensitive = argparse.Namespace(**vars(args))
        sensitive.slug = "sensitive-pii"
        sensitive.evidence_kind = "confirmed-correction"
        sensitive.observed_failure = "客户身份证号 110101199001011234、手机号 13800138000 被写入记录。"
        sensitive.expected_behavior = "学习记录不得保存客户个人信息。"
        try:
            write_candidate(root, sensitive)
        except ValueError as exc:
            assert "sensitive material" in str(exc)
        else:
            raise AssertionError("sensitive PII was accepted")
        protected = argparse.Namespace(**vars(args))
        protected.slug = "protected-profile"
        protected.evidence_kind = "confirmed-correction"
        protected.observed_failure = "用户患有抑郁症并信仰佛教。"
        try:
            write_candidate(root, protected)
        except ValueError as exc:
            assert "sensitive material" in str(exc)
        else:
            raise AssertionError("protected profile material was accepted")
        assert len(list((root / "records" / "wise-agent").glob("*.md"))) == 1
        disable(root)
        try:
            write_candidate(root, args)
        except ValueError as exc:
            assert "does not grant" in str(exc)
        else:
            raise AssertionError("disabled mode accepted a candidate")
        output = io.StringIO()
        with redirect_stdout(output):
            list_records(root, "wise-agent", "candidate")
        assert "candidate\trecords/wise-agent/0001-explicit-git-trigger.md" in output.getvalue()
    print("OK wise-agent skill learning ledger self-test")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        run_self_test()
        return 0
    if not args.command:
        parser.error("a command is required unless --self-test is used")
    root = learning_home(args.home)
    try:
        if args.command == "enable":
            enable(root)
        elif args.command == "disable":
            disable(root)
        elif args.command == "status":
            print(json.dumps(read_mode(root), ensure_ascii=False, indent=2))
        elif args.command == "record":
            write_candidate(root, args)
        elif args.command == "list":
            list_records(root, args.skill, args.status)
        else:
            parser.error(f"unsupported command: {args.command}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
