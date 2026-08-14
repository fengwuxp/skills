#!/usr/bin/env python3
"""Manage the opt-in wise-agent user collaboration profile.

Input: explicit current-task collaboration preferences supplied on the command line.
Output: private JSON profile and metadata-only audit entries under WISE_USER_CONTEXT_HOME.
Writes: only the selected profile home; never the repository, Codex Skills, or learning ledger.
Network: never. Failure: rejects disabled writes, sensitive content, and unsafe locations.
"""

from __future__ import annotations

import argparse
import fcntl
import io
import json
import os
import re
import signal
import stat
import sys
import tempfile
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence


ALLOWED_CATEGORIES = {"communication", "workflow", "evidence", "expertise", "tooling"}
FORBIDDEN_CATEGORIES = {"psychological", "personality", "protected-trait", "authorization"}
EVIDENCE_KINDS = {"direct-user", "repeated-observation"}
ACTIVE_STATUSES = {"candidate", "confirmed"}
SCOPE_RE = re.compile(r"^(?:global|project:[a-zA-Z0-9._/-]+|task-type:[a-zA-Z0-9._-]+)$")
SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(?:身份证(?:号|号码)?|identity[-_ ]?card)\s*[:：=]?\s*\d{17}[\dXx]"),
    re.compile(r"(?i)(?:手机号|手机号码|联系电话|mobile|phone)\s*[:：=]?\s*1[3-9]\d{9}"),
    re.compile(r"(?i)(?:银行卡(?:号|号码)?|bank[-_ ]?card|card[-_ ]?number)\s*[:：=]?\s*\d[\d -]{11,25}\d"),
    re.compile(r"(?i)\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b"),
    re.compile(r"(?:心理画像|人格类型|政治倾向|宗教信仰|民族|种族|性取向|健康状况|生物识别)"),
)
PROFILE_SUBJECT = r"(?:用户|本人|我|其|他|她)\s*(?:目前|曾经|已经|曾)?\s*"
PROFILE_IDENTITY_SUBJECT = r"(?:用户|本人|我|其|他|她)\s*(?:是|为)\s*"
PROTECTED_PROFILE_PATTERNS = (
    re.compile(
        PROFILE_SUBJECT
        + r"(?:信奉|信仰|皈依)(?:了|于)?\s*(?:佛教|道教|基督教|天主教|伊斯兰教|犹太教|印度教|佛门|宗教)"
    ),
    re.compile(PROFILE_SUBJECT + r"(?:患有|得了|被?确诊(?:为|患有)?)"),
    re.compile(PROFILE_SUBJECT + r"(?:有|存在)[^。；，,\n]{0,12}病史"),
    re.compile(
        PROFILE_SUBJECT
        + r"(?:支持|加入(?:了)?)(?:某|该|一个|[\u4e00-\u9fff]{0,8})?(?:政党|党派|共产党|民主党|共和党)"
    ),
    re.compile(
        PROFILE_IDENTITY_SUBJECT
        + r"(?:佛教徒|道教徒|基督徒|天主教徒|穆斯林|犹太教徒|印度教徒)"
    ),
    re.compile(PROFILE_IDENTITY_SUBJECT + r"[^。；，,\n]{1,12}(?:患者|病人)"),
    re.compile(PROFILE_IDENTITY_SUBJECT + r"(?:某|[\u4e00-\u9fff]{1,8})党党员"),
)
DEFAULT_MODE = {
    "schema_version": 1,
    "status": "enabled",
    "write_policy": "explicit-current-task-only",
    "read_policy": "confirmed-only",
    "history_scan": False,
    "candidate_active": False,
    "authority_grants": False,
}


def profile_home(value: str | None = None) -> Path:
    configured = value or os.environ.get("WISE_USER_CONTEXT_HOME") or "~/.wise-agent/user-context"
    return Path(configured).expanduser().resolve()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_home(root: Path) -> None:
    if root in {Path("/"), Path.home().resolve()}:
        raise ValueError("profile home is too broad")
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve()
    if is_within(root, codex_home / "skills"):
        raise ValueError("profile home must not be inside the Codex Skills installation")
    for parent in (root, *root.parents):
        if (parent / ".git").exists():
            raise ValueError("profile home must not be inside a Git repository")


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)


def require_single_regular_file(path: Path, metadata: os.stat_result) -> None:
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{path.name} must be a regular file")
    if metadata.st_nlink != 1:
        raise ValueError(f"{path.name} must not have hard links")


def regular_file_exists(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except FileNotFoundError:
        return False
    require_single_regular_file(path, metadata)
    return True


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

    fd = os.open(path, open_flags, mode)
    try:
        after = os.fstat(fd)
        require_single_regular_file(path, after)
        if before is not None and (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
            raise ValueError(f"{path.name} changed while being opened")
        if truncate:
            os.ftruncate(fd, 0)
        return fd
    except BaseException:
        os.close(fd)
        raise


def tighten_private_file(path: Path) -> None:
    fd = open_regular(path, os.O_RDONLY)
    try:
        os.fchmod(fd, 0o600)
    finally:
        os.close(fd)


def read_fd_bytes(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while chunk := os.read(fd, 65536):
        chunks.append(chunk)
    return b"".join(chunks)


def write_fd_bytes(fd: int, content: bytes) -> None:
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    remaining = content
    while remaining:
        written = os.write(fd, remaining)
        if written <= 0:
            raise OSError("file write made no progress")
        remaining = remaining[written:]
    os.fsync(fd)


def validate_fd_path_identity(fd: int, path: Path) -> None:
    opened = os.fstat(fd)
    require_single_regular_file(path, opened)
    current = os.lstat(path)
    require_single_regular_file(path, current)
    if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
        raise ValueError(f"{path.name} changed while in use")


def write_private(path: Path, content: str) -> None:
    ensure_private_dir(path.parent)
    fd = open_regular(path, os.O_RDWR | os.O_CREAT)
    try:
        opened = os.fstat(fd)
        original = read_fd_bytes(fd)
        try:
            os.fchmod(fd, 0o600)
            write_fd_bytes(fd, content.encode("utf-8"))
            after = os.fstat(fd)
            require_single_regular_file(path, after)
            current_path = os.lstat(path)
            require_single_regular_file(path, current_path)
            if (opened.st_dev, opened.st_ino) != (
                current_path.st_dev,
                current_path.st_ino,
            ):
                raise ValueError(f"{path.name} changed while being written")
        except BaseException:
            try:
                write_fd_bytes(fd, original)
            except BaseException:
                pass
            raise
    finally:
        os.close(fd)


def create_private_file_if_missing(path: Path, content: bytes) -> None:
    ensure_private_dir(path.parent)
    try:
        fd = open_regular(path, os.O_RDWR | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        tighten_private_file(path)
        return
    try:
        os.fchmod(fd, 0o600)
        write_fd_bytes(fd, content)
        validate_fd_path_identity(fd, path)
    finally:
        os.close(fd)


def write_json(path: Path, value: dict[str, object]) -> None:
    write_private(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> dict[str, object]:
    fd = open_regular(path, os.O_RDONLY)
    with os.fdopen(fd, "r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain an object")
    return value


def mode_path(root: Path) -> Path:
    return root / "mode.json"


def profile_path(root: Path) -> Path:
    return root / "profile.json"


def audit_path(root: Path) -> Path:
    return root / "audit.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_audit(root: Path, record_id: str, action: str) -> None:
    path = audit_path(root)
    fd = open_regular(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        validate_fd_path_identity(fd, path)
        original_length = os.fstat(fd).st_size
        try:
            append_audit_fd(fd, record_id, action)
            os.fsync(fd)
            validate_fd_path_identity(fd, path)
        except BaseException:
            os.ftruncate(fd, original_length)
            os.fsync(fd)
            raise
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def append_audit_fd(fd: int, record_id: str, action: str) -> None:
    line = json.dumps(
        {"at": now(), "record_id": record_id, "action": action},
        ensure_ascii=False,
    ) + "\n"
    os.fchmod(fd, 0o600)
    remaining = line.encode("utf-8")
    while remaining:
        written = os.write(fd, remaining)
        if written <= 0:
            raise OSError("audit write made no progress")
        remaining = remaining[written:]


TransactionUpdate = tuple[
    dict[str, object] | None,
    str | None,
    str | None,
    str,
]


def write_json_with_audit(
    root: Path,
    path: Path,
    update: Callable[[dict[str, object]], TransactionUpdate],
) -> str:
    audit_file = audit_path(root)
    audit_fd = open_regular(
        audit_file,
        os.O_WRONLY | os.O_CREAT | os.O_APPEND,
    )
    state_fd = -1
    try:
        fcntl.flock(audit_fd, fcntl.LOCK_EX)
        validate_fd_path_identity(audit_fd, audit_file)
        state_fd = open_regular(path, os.O_RDWR)
        fcntl.flock(state_fd, fcntl.LOCK_EX)
        validate_fd_path_identity(state_fd, path)
        original_state = read_fd_bytes(state_fd)
        value = json.loads(original_state.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"{path.name} must contain an object")
        current, record_id, action, output = update(value)
        if current is None:
            validate_fd_path_identity(state_fd, path)
            validate_fd_path_identity(audit_fd, audit_file)
            return output
        assert record_id is not None and action is not None
        original_audit_length = os.fstat(audit_fd).st_size
        try:
            write_fd_bytes(
                state_fd,
                (json.dumps(current, ensure_ascii=False, indent=2) + "\n").encode(
                    "utf-8"
                ),
            )
            validate_fd_path_identity(state_fd, path)
            validate_fd_path_identity(audit_fd, audit_file)
            append_audit_fd(audit_fd, record_id, action)
            os.fsync(audit_fd)
            validate_fd_path_identity(state_fd, path)
            validate_fd_path_identity(audit_fd, audit_file)
        except BaseException:
            try:
                os.ftruncate(audit_fd, original_audit_length)
                os.fsync(audit_fd)
            finally:
                write_fd_bytes(state_fd, original_state)
            raise
        return output
    finally:
        if state_fd >= 0:
            fcntl.flock(state_fd, fcntl.LOCK_UN)
            os.close(state_fd)
        fcntl.flock(audit_fd, fcntl.LOCK_UN)
        os.close(audit_fd)


def read_mode(root: Path) -> dict[str, object]:
    if not regular_file_exists(mode_path(root)):
        raise ValueError("user collaboration profile is not initialized")
    return read_json(mode_path(root))


def read_profile(root: Path) -> dict[str, object]:
    if not regular_file_exists(profile_path(root)):
        raise ValueError("user collaboration profile is not initialized")
    value = read_json(profile_path(root))
    if value.get("schema_version") != 1 or not isinstance(value.get("records"), list):
        raise ValueError("unsupported profile schema")
    return value


def profile_records(profile: dict[str, object]) -> list[object]:
    records = profile.get("records")
    if profile.get("schema_version") != 1 or not isinstance(records, list):
        raise ValueError("unsupported profile schema")
    return records


def require_enabled(root: Path) -> None:
    mode = read_mode(root)
    if any(mode.get(key) != value for key, value in DEFAULT_MODE.items()):
        raise ValueError("user collaboration profile is disabled or unsafe")


def clean_text(name: str, value: str, limit: int = 1000) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{name} must not be empty")
    if len(text) > limit:
        raise ValueError(f"{name} exceeds {limit} characters")
    if any(pattern.search(text) for pattern in SENSITIVE_PATTERNS):
        raise ValueError(f"{name} appears to contain sensitive or profiling material")
    if any(pattern.search(text) for pattern in PROTECTED_PROFILE_PATTERNS):
        raise ValueError(f"{name} appears to contain protected profile material")
    return text


def enable(root: Path) -> None:
    validate_home(root)
    ensure_private_dir(root)
    disabled_mode = dict(DEFAULT_MODE)
    disabled_mode["status"] = "disabled"
    create_private_file_if_missing(audit_path(root), b"")
    create_private_file_if_missing(
        profile_path(root),
        (json.dumps({"schema_version": 1, "records": []}, indent=2) + "\n").encode(
            "utf-8"
        ),
    )
    create_private_file_if_missing(
        mode_path(root),
        (json.dumps(disabled_mode, indent=2) + "\n").encode("utf-8"),
    )

    def update(_mode: dict[str, object]) -> TransactionUpdate:
        return dict(DEFAULT_MODE), "profile", "enabled", f"ENABLED {root}"

    print(write_json_with_audit(root, mode_path(root), update))


def disable(root: Path) -> None:
    validate_home(root)

    def update(mode: dict[str, object]) -> TransactionUpdate:
        updated_mode = dict(mode)
        updated_mode["status"] = "disabled"
        return updated_mode, "profile", "disabled", f"DISABLED {root}"

    print(write_json_with_audit(root, mode_path(root), update))


def next_id(records: list[object]) -> str:
    numbers = [int(record["id"].removeprefix("UC-")) for record in records if isinstance(record, dict) and re.fullmatch(r"UC-\d{4}", str(record.get("id", "")))]
    return f"UC-{max(numbers, default=0) + 1:04d}"


def record(root: Path, args: argparse.Namespace) -> None:
    validate_home(root)
    require_enabled(root)
    if args.category in FORBIDDEN_CATEGORIES or args.category not in ALLOWED_CATEGORIES:
        raise ValueError("category is unsupported; psychological and authorization profiles are forbidden")
    if not SCOPE_RE.fullmatch(args.scope):
        raise ValueError("scope must be global, project:<id>, or task-type:<id>")
    statement = clean_text("statement", args.statement)
    refs = list(dict.fromkeys(clean_text("evidence-ref", item, 300) for item in args.evidence_ref))
    if args.evidence_kind not in EVIDENCE_KINDS:
        raise ValueError("unsupported evidence kind")
    if args.evidence_kind == "repeated-observation" and len(refs) < 2:
        raise ValueError("repeated-observation requires two distinct current-task evidence refs")

    def update(profile: dict[str, object]) -> TransactionUpdate:
        require_enabled(root)
        records = profile_records(profile)
        normalized = " ".join(statement.casefold().split())
        for existing in records:
            if not isinstance(existing, dict) or existing.get("status") not in ACTIVE_STATUSES:
                continue
            if existing.get("category") == args.category and existing.get("scope") == args.scope and " ".join(str(existing.get("statement", "")).casefold().split()) == normalized:
                return None, None, None, f"SKIP duplicate {existing['id']}"

        record_id = next_id(records)
        timestamp = now()
        updated_profile = dict(profile)
        updated_records = list(records)
        updated_records.append({
            "id": record_id,
            "category": args.category,
            "scope": args.scope,
            "statement": statement,
            "evidence_kind": args.evidence_kind,
            "evidence_refs": refs,
            "status": "candidate",
            "created_at": timestamp,
            "updated_at": timestamp,
        })
        updated_profile["records"] = updated_records
        return (
            updated_profile,
            record_id,
            "recorded-candidate",
            f"RECORDED {record_id}",
        )

    print(write_json_with_audit(root, profile_path(root), update))


def find_record(profile: dict[str, object], record_id: str) -> dict[str, object]:
    records = profile["records"]
    assert isinstance(records, list)
    for item in records:
        if isinstance(item, dict) and item.get("id") == record_id:
            return item
    raise ValueError(f"unknown record: {record_id}")


def transition(root: Path, record_id: str, status: str, reference: str, replacement_id: str | None = None) -> None:
    validate_home(root)
    require_enabled(root)

    def update(profile: dict[str, object]) -> TransactionUpdate:
        require_enabled(root)
        records = profile_records(profile)
        updated_profile = dict(profile)
        updated_profile["records"] = [
            dict(item) if isinstance(item, dict) else item for item in records
        ]
        item = find_record(updated_profile, record_id)
        if item.get("status") not in ACTIVE_STATUSES:
            raise ValueError(f"record is already {item.get('status')}")
        if status == "confirmed" and item.get("status") != "candidate":
            raise ValueError("only a candidate can be confirmed")
        if status == "superseded":
            if not replacement_id or replacement_id == record_id:
                raise ValueError("supersede requires a different replacement")
            replacement = find_record(updated_profile, replacement_id)
            if replacement.get("status") != "confirmed":
                raise ValueError("replacement must already be confirmed")
            item["superseded_by"] = replacement_id
        item["status"] = status
        item["decision_ref"] = clean_text("decision-ref", reference, 300)
        item["updated_at"] = now()
        return updated_profile, record_id, status, f"{status.upper()} {record_id}"

    print(write_json_with_audit(root, profile_path(root), update))


def list_records(root: Path, status: str | None, scope: str | None) -> None:
    validate_home(root)
    profile = read_profile(root)
    records = profile["records"]
    assert isinstance(records, list)
    selected = [item for item in records if isinstance(item, dict) and (not status or item.get("status") == status) and (not scope or item.get("scope") == scope)]
    print(json.dumps({"records": selected}, ensure_ascii=False, indent=2))


def resolve(root: Path, scope: str) -> None:
    validate_home(root)
    require_enabled(root)
    if not SCOPE_RE.fullmatch(scope):
        raise ValueError("invalid scope")
    profile = read_profile(root)
    records = profile["records"]
    assert isinstance(records, list)
    scopes = {"global", scope}
    selected = [item for item in records if isinstance(item, dict) and item.get("status") == "confirmed" and item.get("scope") in scopes]
    print(json.dumps({"application_rule": "current-instruction-first", "records": selected}, ensure_ascii=False, indent=2))


def export_profile(root: Path) -> None:
    validate_home(root)
    mode = read_mode(root)
    profile = read_profile(root)
    print(json.dumps({"mode": mode, "records": profile["records"]}, ensure_ascii=False, indent=2))


def purge(root: Path, confirmation: str) -> None:
    validate_home(root)
    if confirmation != "DELETE-USER-CONTEXT":
        raise ValueError("purge requires --confirm DELETE-USER-CONTEXT")
    expected = {mode_path(root), profile_path(root), audit_path(root)}
    if set(root.iterdir()) != expected:
        raise ValueError("profile home contains unexpected or unsafe entries")
    root.chmod(0o700)
    ordered_paths = (audit_path(root), mode_path(root), profile_path(root))
    opened: list[tuple[Path, int]] = []
    originals: dict[int, bytes] = {}
    try:
        for path in ordered_paths:
            fd = open_regular(path, os.O_RDWR)
            opened.append((path, fd))
            fcntl.flock(fd, fcntl.LOCK_EX)
            validate_fd_path_identity(fd, path)
            os.fchmod(fd, 0o600)
            originals[fd] = read_fd_bytes(fd)

        mode_fd = opened[1][1]
        profile_fd = opened[2][1]
        audit_fd = opened[0][1]
        mode = json.loads(originals[mode_fd].decode("utf-8"))
        if not isinstance(mode, dict):
            raise ValueError("mode.json must contain an object")
        profile = json.loads(originals[profile_fd].decode("utf-8"))
        if not isinstance(profile, dict):
            raise ValueError("profile.json must contain an object")
        profile_records(profile)
        disabled_mode = dict(DEFAULT_MODE)
        disabled_mode["status"] = "disabled"
        write_fd_bytes(
            mode_fd,
            (json.dumps(disabled_mode, ensure_ascii=False, indent=2) + "\n").encode(
                "utf-8"
            ),
        )
        write_fd_bytes(
            profile_fd,
            (
                json.dumps(
                    {"schema_version": 1, "records": []},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n"
            ).encode("utf-8"),
        )
        write_fd_bytes(audit_fd, b"")
        for path, fd in opened:
            validate_fd_path_identity(fd, path)
    except BaseException:
        for _path, fd in opened:
            original = originals.get(fd)
            if original is not None:
                try:
                    write_fd_bytes(fd, original)
                except BaseException:
                    pass
        raise
    finally:
        for _path, fd in reversed(opened):
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
    print(f"PURGED {root}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", help="profile home; defaults to WISE_USER_CONTEXT_HOME or ~/.wise-agent/user-context")
    parser.add_argument("--self-test", action="store_true", help="run an isolated contract test")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("enable")
    commands.add_parser("disable")
    commands.add_parser("status")
    record_parser = commands.add_parser("record")
    record_parser.add_argument("--category", required=True)
    record_parser.add_argument("--scope", required=True)
    record_parser.add_argument("--statement", required=True)
    record_parser.add_argument("--evidence-kind", required=True)
    record_parser.add_argument("--evidence-ref", action="append", required=True)
    confirm = commands.add_parser("confirm")
    confirm.add_argument("record_id")
    confirm.add_argument("--confirmation-ref", required=True)
    reject = commands.add_parser("reject")
    reject.add_argument("record_id")
    reject.add_argument("--reason", required=True)
    supersede = commands.add_parser("supersede")
    supersede.add_argument("record_id")
    supersede.add_argument("--replacement-id", required=True)
    supersede.add_argument("--reason", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--status", choices=["candidate", "confirmed", "rejected", "superseded"])
    listing.add_argument("--scope")
    resolving = commands.add_parser("resolve")
    resolving.add_argument("--scope", required=True)
    commands.add_parser("export")
    deleting = commands.add_parser("purge")
    deleting.add_argument("--confirm", required=True)
    return parser


def run_self_test() -> None:
    global append_audit_fd, write_json_with_audit
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_base = Path(temp_dir)
        unsafe_io: list[str] = []

        audit_link_root = temp_base / "audit-link"
        audit_link_root.mkdir()
        audit_victim = temp_base / "audit-victim.txt"
        audit_victim.write_text("audit sentinel", encoding="utf-8")
        audit_path(audit_link_root).symlink_to(audit_victim)
        try:
            enable(audit_link_root)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("enable accepted a symlinked audit file")
        if audit_victim.read_text(encoding="utf-8") != "audit sentinel":
            unsafe_io.append("enable wrote through a symlinked audit file")

        append_link_root = temp_base / "append-link"
        enable(append_link_root)
        append_victim = temp_base / "append-victim.txt"
        append_victim.write_text("append sentinel", encoding="utf-8")
        audit_path(append_link_root).unlink()
        audit_path(append_link_root).symlink_to(append_victim)
        try:
            disable(append_link_root)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("disable appended through a symlinked audit file")
        if append_victim.read_text(encoding="utf-8") != "append sentinel":
            unsafe_io.append("append followed audit.jsonl outside the profile home")

        temp_link_root = temp_base / "temp-link"
        enable(temp_link_root)
        temp_victim = temp_base / "temp-victim.txt"
        temp_victim.write_text("temp sentinel", encoding="utf-8")
        profile_path(temp_link_root).with_suffix(".json.tmp").symlink_to(temp_victim)
        temp_args = argparse.Namespace(
            category="communication",
            scope="global",
            statement="用户明确要求先给结论。",
            evidence_kind="direct-user",
            evidence_ref=["task:temp-link"],
        )
        record(temp_link_root, temp_args)
        if temp_victim.read_text(encoding="utf-8") != "temp sentinel":
            unsafe_io.append("write_private followed its fixed temporary file")

        read_link_root = temp_base / "read-link"
        read_link_root.mkdir()
        mode_victim = temp_base / "mode-victim.json"
        mode_victim.write_text(json.dumps(DEFAULT_MODE), encoding="utf-8")
        mode_path(read_link_root).symlink_to(mode_victim)
        try:
            read_mode(read_link_root)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("read_mode followed a symlinked mode file")

        mode_root = temp_base / "mode-tightening"
        enable(mode_root)
        mode_root.chmod(0o755)
        profile_path(mode_root).chmod(0o644)
        audit_path(mode_root).chmod(0o644)
        enable(mode_root)
        if mode_root.stat().st_mode & 0o777 != 0o700:
            unsafe_io.append("repeated enable did not restore profile home mode 0700")
        for owned_path in (mode_path(mode_root), profile_path(mode_root), audit_path(mode_root)):
            if owned_path.stat().st_mode & 0o777 != 0o600:
                unsafe_io.append(f"repeated enable did not restore {owned_path.name} mode 0600")

        audit_hardlink_root = temp_base / "audit-hardlink"
        audit_hardlink_root.mkdir()
        audit_hardlink_victim = temp_base / "audit-hardlink-victim.txt"
        audit_hardlink_victim.write_text("audit hardlink sentinel", encoding="utf-8")
        os.link(audit_hardlink_victim, audit_path(audit_hardlink_root))
        try:
            enable(audit_hardlink_root)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("enable accepted a hardlinked audit file")
        if audit_hardlink_victim.read_text(encoding="utf-8") != "audit hardlink sentinel":
            unsafe_io.append("enable modified a hardlinked audit victim")

        temp_hardlink_root = temp_base / "temp-hardlink"
        enable(temp_hardlink_root)
        temp_hardlink_victim = temp_base / "temp-hardlink-victim.txt"
        temp_hardlink_victim.write_text("temp hardlink sentinel", encoding="utf-8")
        os.link(
            temp_hardlink_victim,
            profile_path(temp_hardlink_root).with_suffix(".json.tmp"),
        )
        record(temp_hardlink_root, temp_args)
        if temp_hardlink_victim.read_text(encoding="utf-8") != "temp hardlink sentinel":
            unsafe_io.append("write_private modified a hardlinked temporary victim")

        fifo_root = temp_base / "audit-fifo"
        fifo_root.mkdir()
        os.mkfifo(audit_path(fifo_root))
        previous_alarm_handler = signal.getsignal(signal.SIGALRM)

        def reject_blocking_fifo(_signum: int, _frame: object) -> None:
            raise TimeoutError("FIFO open blocked")

        signal.signal(signal.SIGALRM, reject_blocking_fifo)
        signal.setitimer(signal.ITIMER_REAL, 0.2)
        try:
            append_audit(fifo_root, "profile", "fifo-test")
        except TimeoutError:
            unsafe_io.append("open_regular blocked while rejecting a FIFO")
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("open_regular accepted a FIFO")
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_alarm_handler)

        race_target = temp_base / "race-target.tmp"
        race_target.write_text("owned temp sentinel", encoding="utf-8")
        race_victim = temp_base / "race-victim.txt"
        race_victim.write_text("race victim sentinel", encoding="utf-8")
        original_open = os.open
        swap_pending = True

        def swap_before_open(path: object, flags: int, mode: int = 0o777) -> int:
            nonlocal swap_pending
            if swap_pending and Path(path) == race_target:
                swap_pending = False
                race_target.unlink()
                race_victim.replace(race_target)
            return original_open(path, flags, mode)

        os.open = swap_before_open
        try:
            open_regular(race_target, os.O_WRONLY | os.O_TRUNC)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("open_regular accepted a path replacement race")
        finally:
            os.open = original_open
        if race_target.read_text(encoding="utf-8") != "race victim sentinel":
            unsafe_io.append("open_regular truncated a replacement inode before validation")

        replace_entry_root = temp_base / "replace-entry-handoff"
        enable(replace_entry_root)
        replace_entry_victim = temp_base / "replace-entry-victim.txt"
        replace_entry_victim.write_text("replace entry sentinel", encoding="utf-8")
        replace_profile_before = profile_path(replace_entry_root).read_text(encoding="utf-8")
        replace_parked = temp_base / "replace-entry-owned.tmp"
        original_replace = os.replace
        replace_entry_triggered = False

        def swap_at_replace_entry(source: object, target: object) -> None:
            nonlocal replace_entry_triggered
            source_path = Path(source)
            if (
                not replace_entry_triggered
                and Path(target) == profile_path(replace_entry_root)
                and source_path.parent == replace_entry_root
                and source_path.name.endswith(".tmp")
            ):
                replace_entry_triggered = True
                original_replace(source_path, replace_parked)
                os.link(replace_entry_victim, source_path)
            original_replace(source_path, target)

        os.replace = swap_at_replace_entry
        try:
            record(replace_entry_root, temp_args)
        except (OSError, ValueError):
            pass
        else:
            if replace_entry_triggered:
                unsafe_io.append("record reported success after a replace-entry handoff")
        finally:
            os.replace = original_replace
        if replace_entry_victim.read_text(encoding="utf-8") != "replace entry sentinel":
            unsafe_io.append("replace-entry handoff modified its victim")
        if replace_entry_triggered and profile_path(replace_entry_root).read_text(encoding="utf-8") != replace_profile_before:
            unsafe_io.append("replace-entry handoff published a victim as the profile")

        unlink_entry_root = temp_base / "unlink-entry-handoff"
        enable(unlink_entry_root)
        unlink_entry_victim = temp_base / "unlink-entry-victim.txt"
        unlink_entry_victim.write_text("unlink entry sentinel", encoding="utf-8")
        unlink_victim_fd = os.open(unlink_entry_victim, os.O_RDONLY)
        unlink_parked = temp_base / "unlink-entry-owned.tmp"
        original_lstat = os.lstat
        original_unlink = os.unlink
        fail_publish_check = True
        unlink_entry_triggered = False

        def fail_before_cleanup(candidate: object) -> os.stat_result:
            nonlocal fail_publish_check
            candidate_path = Path(candidate)
            if (
                fail_publish_check
                and candidate_path.parent == unlink_entry_root
                and candidate_path.name.startswith(".profile.json.")
                and candidate_path.name.endswith(".tmp")
            ):
                fail_publish_check = False
                raise OSError("forced publication check failure")
            return original_lstat(candidate_path)

        def swap_at_unlink_entry(candidate: object, *args: object, **kwargs: object) -> None:
            nonlocal unlink_entry_triggered
            candidate_path = Path(candidate)
            if (
                not unlink_entry_triggered
                and candidate_path.parent == unlink_entry_root
                and candidate_path.name.startswith(".profile.json.")
                and candidate_path.name.endswith(".tmp")
            ):
                unlink_entry_triggered = True
                original_replace(candidate_path, unlink_parked)
                original_replace(unlink_entry_victim, candidate_path)
            original_unlink(candidate_path, *args, **kwargs)

        os.lstat = fail_before_cleanup
        os.unlink = swap_at_unlink_entry
        try:
            record(unlink_entry_root, temp_args)
        except (OSError, ValueError):
            pass
        else:
            if unlink_entry_triggered:
                unsafe_io.append("record reported success after an unlink-entry handoff")
        finally:
            os.lstat = original_lstat
            os.unlink = original_unlink
        try:
            if os.fstat(unlink_victim_fd).st_nlink == 0:
                unsafe_io.append("unlink-entry cleanup deleted a replacement victim")
        finally:
            os.close(unlink_victim_fd)

        partial_audit_root = temp_base / "partial-audit"
        enable(partial_audit_root)
        partial_profile_before = read_profile(partial_audit_root)
        partial_audit_before = audit_path(partial_audit_root).read_bytes()
        partial_audit_identity = os.lstat(audit_path(partial_audit_root))
        original_write = os.write
        partial_write_stage = 0

        def fail_after_partial_audit(fd: int, data: bytes) -> int:
            nonlocal partial_write_stage
            opened = os.fstat(fd)
            is_audit = (opened.st_dev, opened.st_ino) == (
                partial_audit_identity.st_dev,
                partial_audit_identity.st_ino,
            )
            if is_audit and partial_write_stage == 0:
                partial_write_stage = 1
                prefix_length = max(1, len(data) // 2)
                return original_write(fd, data[:prefix_length])
            if is_audit and partial_write_stage == 1:
                partial_write_stage = 2
                raise OSError("forced partial audit failure")
            return original_write(fd, data)

        os.write = fail_after_partial_audit
        try:
            record(partial_audit_root, temp_args)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("record accepted a partial audit write")
        finally:
            os.write = original_write
        if read_profile(partial_audit_root) != partial_profile_before:
            unsafe_io.append("partial audit failure left an unaudited candidate")
        if audit_path(partial_audit_root).read_bytes() != partial_audit_before:
            unsafe_io.append("partial audit failure left a truncated JSONL record")

        for audit_fails in (False, True):
            case_name = "failure" if audit_fails else "success"
            state_swap_root = temp_base / f"state-path-swap-{case_name}"
            enable(state_swap_root)
            state_before = profile_path(state_swap_root).read_bytes()
            audit_before = audit_path(state_swap_root).read_bytes()
            state_parked = temp_base / f"state-path-swap-{case_name}.parked"
            state_victim = temp_base / f"state-path-swap-{case_name}-victim.txt"
            state_victim.write_text(f"state {case_name} victim", encoding="utf-8")
            original_append_audit_fd = append_audit_fd
            state_swap_triggered = False

            def swap_state_before_audit(fd: int, record_id: str, action: str) -> None:
                nonlocal state_swap_triggered
                if not state_swap_triggered:
                    state_swap_triggered = True
                    os.replace(profile_path(state_swap_root), state_parked)
                    os.link(state_victim, profile_path(state_swap_root))
                if audit_fails:
                    raise OSError("forced audit failure after state path swap")
                original_append_audit_fd(fd, record_id, action)

            append_audit_fd = swap_state_before_audit
            try:
                record(state_swap_root, temp_args)
            except (OSError, ValueError):
                pass
            else:
                unsafe_io.append(f"record reported success after state path swap with audit {case_name}")
            finally:
                append_audit_fd = original_append_audit_fd
            if state_victim.read_text(encoding="utf-8") != f"state {case_name} victim":
                unsafe_io.append(f"state path swap with audit {case_name} overwrote its victim")
            if state_parked.read_bytes() != state_before:
                unsafe_io.append(f"state path swap with audit {case_name} did not restore the opened state inode")
            if audit_path(state_swap_root).read_bytes() != audit_before:
                unsafe_io.append(f"state path swap with audit {case_name} left an audit record")

        audit_swap_root = temp_base / "audit-path-swap"
        enable(audit_swap_root)
        audit_swap_profile_before = read_profile(audit_swap_root)
        audit_swap_before = audit_path(audit_swap_root).read_bytes()
        audit_parked = temp_base / "audit-path-swap.parked"
        audit_victim = temp_base / "audit-path-swap-victim.txt"
        audit_victim.write_text("audit path victim", encoding="utf-8")
        original_append_audit_fd = append_audit_fd
        audit_swap_triggered = False

        def swap_audit_path(fd: int, record_id: str, action: str) -> None:
            nonlocal audit_swap_triggered
            if not audit_swap_triggered:
                audit_swap_triggered = True
                os.replace(audit_path(audit_swap_root), audit_parked)
                os.link(audit_victim, audit_path(audit_swap_root))
            original_append_audit_fd(fd, record_id, action)

        append_audit_fd = swap_audit_path
        try:
            record(audit_swap_root, temp_args)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("record reported success after audit path swap")
        finally:
            append_audit_fd = original_append_audit_fd
        if read_profile(audit_swap_root) != audit_swap_profile_before:
            unsafe_io.append("audit path swap left an unaudited candidate")
        if audit_victim.read_text(encoding="utf-8") != "audit path victim":
            unsafe_io.append("audit path swap modified its victim")
        if audit_parked.read_bytes() != audit_swap_before:
            unsafe_io.append("audit path swap left a record on the parked audit inode")

        concurrent_root = temp_base / "concurrent-records"
        enable(concurrent_root)
        ready_read, ready_write = os.pipe()
        release_read, release_write = os.pipe()
        original_transaction = write_json_with_audit

        def wait_before_transaction(*args: object, **kwargs: object) -> str:
            os.write(ready_write, b"1")
            os.read(release_read, 1)
            return original_transaction(*args, **kwargs)

        write_json_with_audit = wait_before_transaction
        child_pids: list[int] = []
        for index in range(2):
            pid = os.fork()
            if pid == 0:
                concurrent_args = argparse.Namespace(**vars(temp_args))
                concurrent_args.statement = f"并发偏好 {index}"
                concurrent_args.evidence_ref = [f"task:concurrent-{index}"]
                try:
                    record(concurrent_root, concurrent_args)
                except BaseException:
                    os._exit(1)
                os._exit(0)
            child_pids.append(pid)
        os.close(ready_write)
        ready_count = 0
        while ready_count < 2:
            ready_count += len(os.read(ready_read, 2 - ready_count))
        os.write(release_write, b"11")
        child_statuses = [os.waitpid(pid, 0)[1] for pid in child_pids]
        write_json_with_audit = original_transaction
        for pipe_fd in (ready_read, release_read, release_write):
            os.close(pipe_fd)
        if any(status != 0 for status in child_statuses):
            unsafe_io.append("concurrent record worker failed")
        concurrent_profile = read_profile(concurrent_root)
        concurrent_records = concurrent_profile["records"]
        assert isinstance(concurrent_records, list)
        concurrent_ids = {
            item.get("id") for item in concurrent_records if isinstance(item, dict)
        }
        if len(concurrent_records) != 2 or len(concurrent_ids) != 2:
            unsafe_io.append("concurrent records reused an ID or lost an update")

        enable_disable_root = temp_base / "concurrent-enable-disable"
        enable(enable_disable_root)
        audit_before = [
            json.loads(line)
            for line in audit_path(enable_disable_root)
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        ]
        ready_read, ready_write = os.pipe()
        release_read, release_write = os.pipe()
        enable_disable_pids: list[int] = []
        for action in ("enable", "disable"):
            pid = os.fork()
            if pid == 0:
                os.write(ready_write, b"1")
                os.read(release_read, 1)
                try:
                    if action == "enable":
                        enable(enable_disable_root)
                    else:
                        disable(enable_disable_root)
                except BaseException:
                    os._exit(1)
                os._exit(0)
            enable_disable_pids.append(pid)
        os.close(ready_write)
        ready_count = 0
        while ready_count < 2:
            ready_count += len(os.read(ready_read, 2 - ready_count))
        os.write(release_write, b"11")
        enable_disable_statuses = [
            os.waitpid(pid, 0)[1] for pid in enable_disable_pids
        ]
        for pipe_fd in (ready_read, release_read, release_write):
            os.close(pipe_fd)
        if any(status != 0 for status in enable_disable_statuses):
            unsafe_io.append("concurrent enable/disable worker failed")
        audit_after = [
            json.loads(line)
            for line in audit_path(enable_disable_root)
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        ]
        concurrent_actions = [
            entry.get("action") for entry in audit_after[len(audit_before) :]
        ]
        if sorted(concurrent_actions) != ["disabled", "enabled"]:
            unsafe_io.append("concurrent enable/disable did not serialize both actions")
        elif read_mode(enable_disable_root).get("status") != concurrent_actions[-1]:
            unsafe_io.append("concurrent enable/disable mode disagrees with final audit")

        purge_handoff_root = temp_base / "purge-path-handoff"
        enable(purge_handoff_root)
        record(purge_handoff_root, temp_args)
        purge_victim = temp_base / "purge-victim.txt"
        purge_victim.write_text("purge victim", encoding="utf-8")
        purge_victim_fd = os.open(purge_victim, os.O_RDONLY)
        purge_parked = temp_base / "purge-profile.parked"
        original_unlink = os.unlink
        purge_handoff_triggered = False

        def swap_at_purge_unlink(
            candidate: os.PathLike[str] | str,
            *args: object,
            **kwargs: object,
        ) -> None:
            nonlocal purge_handoff_triggered
            if (
                not purge_handoff_triggered
                and Path(candidate) == profile_path(purge_handoff_root)
            ):
                purge_handoff_triggered = True
                os.replace(candidate, purge_parked)
                os.replace(purge_victim, candidate)
            original_unlink(candidate, *args, **kwargs)

        os.unlink = swap_at_purge_unlink
        try:
            purge(purge_handoff_root, "DELETE-USER-CONTEXT")
        except (OSError, ValueError):
            pass
        finally:
            os.unlink = original_unlink
        if os.fstat(purge_victim_fd).st_nlink == 0:
            unsafe_io.append("purge pathname deletion removed a replacement victim")
        os.close(purge_victim_fd)
        if not purge_handoff_root.is_dir():
            unsafe_io.append("purge removed the profile home instead of leaving a disabled shell")
        else:
            if read_mode(purge_handoff_root).get("status") != "disabled":
                unsafe_io.append("purge did not leave disabled mode")
            if read_profile(purge_handoff_root).get("records") != []:
                unsafe_io.append("purge did not clear profile records")
            if audit_path(purge_handoff_root).read_bytes() != b"":
                unsafe_io.append("purge did not clear the audit")

        disable_audit_root = temp_base / "disable-audit-failure"
        enable(disable_audit_root)
        disable_victim = temp_base / "disable-audit-victim.txt"
        disable_victim.write_text("disable audit sentinel", encoding="utf-8")
        audit_path(disable_audit_root).unlink()
        audit_path(disable_audit_root).symlink_to(disable_victim)
        mode_before_failed_disable = read_mode(disable_audit_root)
        try:
            disable(disable_audit_root)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("disable accepted an unsafe audit file")
        if read_mode(disable_audit_root) != mode_before_failed_disable:
            unsafe_io.append("disable left an unaudited mode transition")

        record_audit_root = temp_base / "record-audit-failure"
        enable(record_audit_root)
        record_victim = temp_base / "record-audit-victim.txt"
        record_victim.write_text("record audit sentinel", encoding="utf-8")
        audit_path(record_audit_root).unlink()
        os.link(record_victim, audit_path(record_audit_root))
        profile_before_failed_record = read_profile(record_audit_root)
        try:
            record(record_audit_root, temp_args)
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("record accepted an unsafe audit file")
        if read_profile(record_audit_root) != profile_before_failed_record:
            unsafe_io.append("record left an unaudited candidate")

        transition_audit_root = temp_base / "transition-audit-failure"
        enable(transition_audit_root)
        record(transition_audit_root, temp_args)
        audit_path(transition_audit_root).unlink()
        os.mkfifo(audit_path(transition_audit_root))
        profile_before_failed_transition = read_profile(transition_audit_root)
        try:
            transition(
                transition_audit_root,
                "UC-0001",
                "confirmed",
                "user:current",
            )
        except (OSError, ValueError):
            pass
        else:
            unsafe_io.append("transition accepted an unsafe audit file")
        if read_profile(transition_audit_root) != profile_before_failed_transition:
            unsafe_io.append("transition left an unaudited status change")

        if unsafe_io:
            raise AssertionError("; ".join(unsafe_io))

        root = Path(temp_dir) / "user-context"
        args = argparse.Namespace(
            category="communication",
            scope="global",
            statement="用户明确要求默认使用中文并先给结论。",
            evidence_kind="direct-user",
            evidence_ref=["task:current"],
        )
        try:
            record(root, args)
        except ValueError:
            pass
        else:
            raise AssertionError("disabled profile accepted a record")

        enable(root)
        record(root, args)
        profile = read_profile(root)
        assert profile["records"][0]["id"] == "UC-0001"
        output = io.StringIO()
        with redirect_stdout(output):
            resolve(root, "global")
        assert json.loads(output.getvalue())["records"] == []

        transition(root, "UC-0001", "confirmed", "user:current")
        output = io.StringIO()
        with redirect_stdout(output):
            resolve(root, "global")
        assert json.loads(output.getvalue())["records"][0]["id"] == "UC-0001"
        assert "默认使用中文" not in audit_path(root).read_text(encoding="utf-8")

        forbidden = argparse.Namespace(**vars(args))
        forbidden.category = "psychological"
        try:
            record(root, forbidden)
        except ValueError:
            pass
        else:
            raise AssertionError("psychological profile was accepted")
        sensitive = argparse.Namespace(**vars(args))
        sensitive.statement = "用户手机号 13800138000。"
        try:
            record(root, sensitive)
        except ValueError:
            pass
        else:
            raise AssertionError("sensitive profile material was accepted")

        protected_profile = argparse.Namespace(**vars(args))
        protected_profile.statement = "用户信奉佛教，患有抑郁症，并支持某政党。"
        try:
            record(root, protected_profile)
        except ValueError:
            pass
        else:
            raise AssertionError("natural-language protected profile was accepted")

        direct_protected_profiles = (
            "用户是佛教徒。",
            "用户是抑郁症患者。",
            "用户得了抑郁症。",
            "用户是民主党党员。",
        )
        for statement in direct_protected_profiles:
            direct_profile = argparse.Namespace(**vars(args))
            direct_profile.statement = statement
            try:
                record(root, direct_profile)
            except ValueError:
                pass
            else:
                raise AssertionError(f"direct protected profile was accepted: {statement}")

        expertise = argparse.Namespace(**vars(args))
        expertise.category = "expertise"
        expertise.statement = "用户擅长医疗行业研究。"
        expertise.evidence_ref = ["task:expertise"]
        record(root, expertise)
        profile = read_profile(root)
        assert any(
            isinstance(item, dict) and item.get("statement") == expertise.statement
            for item in profile["records"]
        )

        disable(root)
        try:
            record(root, args)
        except ValueError:
            pass
        else:
            raise AssertionError("disabled profile accepted a record")
        assert root.stat().st_mode & 0o777 == 0o700
        assert all(path.stat().st_mode & 0o777 == 0o600 for path in (mode_path(root), profile_path(root), audit_path(root)))

        unrelated = Path(temp_dir) / "unrelated"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("keep", encoding="utf-8")
        try:
            purge(unrelated, "DELETE-USER-CONTEXT")
        except ValueError:
            pass
        else:
            raise AssertionError("purge accepted a non-profile directory")
        assert (unrelated / "keep.txt").is_file()
        try:
            purge(root, "WRONG")
        except ValueError:
            pass
        else:
            raise AssertionError("purge accepted a wrong confirmation")
        purge(root, "DELETE-USER-CONTEXT")
        assert root.is_dir()
        assert read_mode(root).get("status") == "disabled"
        assert read_profile(root).get("records") == []
        assert audit_path(root).read_bytes() == b""
    print("OK wise-agent user collaboration profile self-test")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        run_self_test()
        return 0
    if not args.command:
        parser.error("a command is required")
    root = profile_home(args.home)
    try:
        if args.command == "enable":
            enable(root)
        elif args.command == "disable":
            disable(root)
        elif args.command == "status":
            print(json.dumps(read_mode(root), ensure_ascii=False, indent=2))
        elif args.command == "record":
            record(root, args)
        elif args.command == "confirm":
            transition(root, args.record_id, "confirmed", args.confirmation_ref)
        elif args.command == "reject":
            transition(root, args.record_id, "rejected", args.reason)
        elif args.command == "supersede":
            transition(root, args.record_id, "superseded", args.reason, args.replacement_id)
        elif args.command == "list":
            list_records(root, args.status, args.scope)
        elif args.command == "resolve":
            resolve(root, args.scope)
        elif args.command == "export":
            export_profile(root)
        elif args.command == "purge":
            purge(root, args.confirm)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
