#!/usr/bin/env python3
"""Collect local, metadata-only wise-agent usage evidence.

Input: explicit CLI commands, Codex PostToolUse hook JSON, or OTLP/HTTP JSON.
Output: private JSONL events and aggregate JSON reports under SKILL_USAGE_HOME.
Writes: only the selected usage home. Network: loopback OTLP receiver only.
The script never reads transcripts or stores prompts, responses, source content,
tool input/output, secrets, or raw telemetry payloads.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shlex
import stat
import sys
import tempfile
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Iterable, Sequence


MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_EVENT_BYTES = 8192
OTLP_SUCCESS_BODY = b"{}"
HEALTH_BODY = b'{"service":"wise-agent-skill-usage","status":"ok"}'
MODE = {
    "schema_version": 1,
    "status": "enabled",
    "readiness": "PILOT_PENDING",
    "write_policy": "metadata-only",
    "local_only": True,
    "log_user_prompt": False,
    "log_transcript": False,
    "log_tool_content": False,
    "auto_candidate": False,
    "git_actions": False,
}
METRICS = {
    "codex.turn.token_usage",
    "codex.skill.injected",
    "codex.thread.skills.enabled_total",
    "codex.thread.skills.kept_total",
    "codex.thread.skills.truncated",
}
METRIC_FIELDS = {
    "token_type",
    "tmp_mem_enabled",
    "skill",
    "status",
    "model",
    "app.version",
    "auth_mode",
    "originator",
    "session_source",
}
TOKEN_ALIASES = {
    "input": ("input_tokens", "input_token_count", "usage_input_tokens"),
    "cached_input": ("cached_input_tokens", "cached_token_count", "usage_cached_input_tokens"),
    "output": ("output_tokens", "output_token_count", "usage_output_tokens"),
    "reasoning_output": (
        "reasoning_output_tokens",
        "reasoning_tokens",
        "usage_reasoning_output_tokens",
    ),
    "total": ("total_tokens", "total_token_count", "usage_total_tokens"),
}


def usage_home(value: str | None = None) -> Path:
    base = value or os.environ.get("SKILL_USAGE_HOME") or "~/.skill-usage"
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
        raise ValueError("usage home must not be inside the Codex Skills installation")
    for parent in (root, *root.parents):
        if (parent / ".git").exists():
            raise ValueError("usage home must not be inside a Git repository")


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


def validate_fd_path_identity(descriptor: int, path: Path) -> None:
    opened = os.fstat(descriptor)
    require_single_regular_file(path, opened)
    current = os.lstat(path)
    require_single_regular_file(path, current)
    if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
        raise ValueError(f"{path.name} changed while in use")


def read_fd_bytes(descriptor: int) -> bytes:
    os.lseek(descriptor, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while chunk := os.read(descriptor, 65536):
        chunks.append(chunk)
    return b"".join(chunks)


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
        return read_fd_bytes(descriptor).decode("utf-8")
    finally:
        os.close(descriptor)


def mode_path(root: Path) -> Path:
    return root / "mode.json"


def read_mode(root: Path) -> dict[str, Any]:
    path = mode_path(root)
    try:
        raw = read_private_text(path)
    except FileNotFoundError:
        raise ValueError(f"usage mode is not initialized: {path}")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("mode.json must contain an object")
    return value


def write_mode(root: Path, value: dict[str, Any]) -> None:
    ensure_private_dir(root)
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor = open_regular(mode_path(root), os.O_RDWR | os.O_CREAT)
    try:
        old = read_fd_bytes(descriptor)
        try:
            os.lseek(descriptor, 0, os.SEEK_SET)
            os.ftruncate(descriptor, 0)
            write_all(descriptor, payload)
            validate_fd_path_identity(descriptor, mode_path(root))
        except BaseException:
            os.lseek(descriptor, 0, os.SEEK_SET)
            os.ftruncate(descriptor, 0)
            write_all(descriptor, old)
            raise
    finally:
        os.close(descriptor)


def enable(root: Path) -> None:
    validate_home(root)
    write_mode(root, dict(MODE))


def disable(root: Path) -> None:
    validate_home(root)
    mode = read_mode(root)
    mode["status"] = "disabled"
    write_mode(root, mode)


def require_enabled(root: Path) -> dict[str, Any]:
    mode = read_mode(root)
    required = {
        "status": "enabled",
        "write_policy": "metadata-only",
        "local_only": True,
        "log_user_prompt": False,
        "log_transcript": False,
        "log_tool_content": False,
        "auto_candidate": False,
        "git_actions": False,
    }
    mismatches = [key for key, expected in required.items() if mode.get(key) != expected]
    if mismatches:
        raise ValueError(f"usage mode does not grant metadata-only writes: {', '.join(mismatches)}")
    return mode


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def event_id_for(event: dict[str, Any]) -> str:
    identity = {
        key: value
        for key, value in event.items()
        if key not in {"schema_version", "event_id", "observed_at"}
    }
    return hashlib.sha256(
        json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def decode_event_lines(data: bytes, source: str) -> tuple[list[dict[str, Any]], int, int]:
    events: list[dict[str, Any]] = []
    valid_length = 0
    lines = data.splitlines(keepends=True)
    for index, raw_line in enumerate(lines, 1):
        end = valid_length + len(raw_line)
        if not raw_line.strip():
            valid_length = end
            continue
        try:
            value = json.loads(raw_line)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            if index == len(lines) and not raw_line.endswith((b"\n", b"\r")):
                return events, valid_length, 1
            raise ValueError(f"{source}:{index}: invalid JSONL record") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{source}:{index}: JSONL record must be an object")
        events.append(value)
        valid_length = end
    return events, valid_length, 0


def encoded_event(event: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    stored = {
        **event,
        "schema_version": 1,
        "event_id": event_id_for(event),
        "observed_at": utc_now(),
    }
    payload = (json.dumps(stored, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > MAX_EVENT_BYTES:
        raise ValueError("sanitized usage event exceeds the size limit")
    return stored, payload


def append_event(root: Path, event: dict[str, Any]) -> bool:
    require_enabled(root)
    stored, payload = encoded_event(event)
    event_dir = root / "events"
    ensure_private_dir(root)
    ensure_private_dir(event_dir)
    path = event_dir / f"{datetime.now(timezone.utc).date().isoformat()}.jsonl"
    lock_path = event_dir / ".append.lock"
    lock_descriptor = open_regular(lock_path, os.O_WRONLY | os.O_CREAT)
    descriptor = -1
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        validate_fd_path_identity(lock_descriptor, lock_path)
        # ponytail: global O(n) dedupe is enough for the pilot; use SQLite only after measured volume requires it.
        for existing_path in sorted(event_dir.glob("*.jsonl")):
            existing_descriptor = open_regular(existing_path, os.O_RDONLY)
            try:
                historical, _, _ = decode_event_lines(
                    read_fd_bytes(existing_descriptor), str(existing_path)
                )
            finally:
                os.close(existing_descriptor)
            if stored["event_id"] in {
                str(item.get("event_id") or event_id_for(item)) for item in historical
            }:
                return False

        descriptor = open_regular(path, os.O_RDWR | os.O_CREAT | os.O_APPEND)
        validate_fd_path_identity(descriptor, path)
        original = read_fd_bytes(descriptor)
        existing, valid_length, rejected_tail = decode_event_lines(original, str(path))
        existing_ids = {str(item.get("event_id") or event_id_for(item)) for item in existing}
        if stored["event_id"] in existing_ids:
            return False
        try:
            os.ftruncate(descriptor, valid_length)
            recovery_payload = b""
            if rejected_tail:
                _, recovery_payload = encoded_event(
                    {"event_type": "storage_recovery", "rejected_tail_records": rejected_tail}
                )
            separator = b"\n" if valid_length and not original[:valid_length].endswith(b"\n") else b""
            write_all(descriptor, separator + recovery_payload + payload)
            validate_fd_path_identity(descriptor, path)
        except BaseException:
            os.ftruncate(descriptor, 0)
            write_all(descriptor, original)
            raise
        return True
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        os.close(lock_descriptor)


def scalar(value: Any) -> str | int | float | bool | None:
    if not isinstance(value, dict):
        return value if isinstance(value, (str, int, float, bool)) else None
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key not in value:
            continue
        item = value[key]
        if key == "intValue":
            try:
                return int(item)
            except (TypeError, ValueError):
                return None
        if key == "doubleValue":
            try:
                return float(item)
            except (TypeError, ValueError):
                return None
        return item if isinstance(item, (str, bool)) else None
    return None


def attributes(value: Any) -> dict[str, str | int | float | bool]:
    result: dict[str, str | int | float | bool] = {}
    if not isinstance(value, list):
        return result
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("key"), str):
            continue
        observed = scalar(item.get("value"))
        if observed is not None:
            result[item["key"]] = observed
    return result


def metric_points(
    metric: dict[str, Any],
) -> Iterable[tuple[dict[str, Any], int | float, str, str]]:
    for container_name in ("histogram", "sum", "gauge"):
        container = metric.get(container_name)
        if not isinstance(container, dict):
            continue
        temporality = "gauge" if container_name == "gauge" else {
            1: "delta",
            "1": "delta",
            "AGGREGATION_TEMPORALITY_DELTA": "delta",
            2: "cumulative",
            "2": "cumulative",
            "AGGREGATION_TEMPORALITY_CUMULATIVE": "cumulative",
        }.get(container.get("aggregationTemporality"), "unspecified")
        for point in container.get("dataPoints", []):
            if not isinstance(point, dict):
                continue
            value = point.get("sum")
            if value is None:
                value = point.get("asInt", point.get("asDouble"))
            try:
                number = float(value) if isinstance(value, str) and "." in value else int(value)
            except (TypeError, ValueError):
                continue
            yield point, number, temporality, container_name


def sanitize_metric_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    events = []
    for resource_metric in payload.get("resourceMetrics", []):
        if not isinstance(resource_metric, dict):
            continue
        resource = resource_metric.get("resource", {})
        resource_fields = attributes(resource.get("attributes", [])) if isinstance(resource, dict) else {}
        for scope in resource_metric.get("scopeMetrics", []):
            if not isinstance(scope, dict):
                continue
            for metric in scope.get("metrics", []):
                if not isinstance(metric, dict) or metric.get("name") not in METRICS:
                    continue
                name = metric["name"]
                for point, value, temporality, metric_kind in metric_points(metric):
                    if not point.get("timeUnixNano"):
                        raise ValueError(f"{name} is missing timeUnixNano")
                    if temporality == "unspecified":
                        raise ValueError(f"{name} is missing aggregationTemporality")
                    point_fields = attributes(point.get("attributes", []))
                    allowed = {
                        key: observed
                        for key, observed in {**resource_fields, **point_fields}.items()
                        if key in METRIC_FIELDS
                    }
                    events.append(
                        {
                            "event_type": "codex_metric",
                            "metric": name,
                            "value": value,
                            "metric_kind": metric_kind,
                            "aggregation_temporality": temporality,
                            "start_time_unix_nano": str(point.get("startTimeUnixNano", ""))[:30],
                            "time_unix_nano": str(point.get("timeUnixNano", ""))[:30],
                            **allowed,
                        }
                    )
    return events


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def first_number(values: dict[str, Any], aliases: Sequence[str]) -> int | None:
    normalized = {normalized_key(key): value for key, value in values.items()}
    for alias in aliases:
        value = normalized.get(alias)
        if isinstance(value, bool):
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def sanitize_log_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    events = []
    for resource_log in payload.get("resourceLogs", []):
        if not isinstance(resource_log, dict):
            continue
        resource = resource_log.get("resource", {})
        resource_fields = attributes(resource.get("attributes", [])) if isinstance(resource, dict) else {}
        for scope in resource_log.get("scopeLogs", []):
            if not isinstance(scope, dict):
                continue
            for record in scope.get("logRecords", []):
                if not isinstance(record, dict):
                    continue
                fields = {**resource_fields, **attributes(record.get("attributes", []))}
                event_name = fields.get("event.name", fields.get("name"))
                kind = fields.get("kind", fields.get("event.kind"))
                if event_name != "codex.sse_event" or kind != "response.completed":
                    continue
                tokens = {
                    token_type: value
                    for token_type, aliases in TOKEN_ALIASES.items()
                    if (value := first_number(fields, aliases)) is not None
                }
                if not tokens:
                    continue
                session_id = fields.get(
                    "conversation.id",
                    fields.get("conversation_id", fields.get("thread.id", fields.get("thread_id"))),
                )
                event: dict[str, Any] = {
                    "event_type": "response_token_usage",
                    "tokens": tokens,
                    "time_unix_nano": str(record.get("timeUnixNano", ""))[:30],
                    "observed_time_unix_nano": str(record.get("observedTimeUnixNano", ""))[:30],
                }
                if not any(
                    (
                        event["time_unix_nano"],
                        event["observed_time_unix_nano"],
                        fields.get("turn_id"),
                        record.get("traceId"),
                    )
                ):
                    raise ValueError("response.completed is missing a stable event identity")
                if isinstance(record.get("traceId"), str):
                    event["trace_id"] = record["traceId"][:64]
                if isinstance(record.get("spanId"), str):
                    event["span_id"] = record["spanId"][:32]
                if isinstance(session_id, str):
                    event["session_id"] = session_id[:200]
                if isinstance(fields.get("turn_id"), str):
                    event["turn_id"] = fields["turn_id"][:200]
                if isinstance(fields.get("model"), str):
                    event["model"] = fields["model"][:200]
                events.append(event)
    return events


def ingest_otlp(root: Path, kind: str, payload: dict[str, Any]) -> int:
    require_enabled(root)
    if not isinstance(payload, dict):
        raise ValueError("OTLP JSON payload must be an object")
    if kind == "metrics":
        events = sanitize_metric_events(payload)
    elif kind == "logs":
        events = sanitize_log_events(payload)
    else:
        raise ValueError("OTLP kind must be metrics or logs")
    return sum(append_event(root, event) for event in events)


def find_reader_package(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        required = {"status", "source_sha256", "selections", "token_estimate_method"}
        if required <= value.keys():
            return value
        for nested in value.values():
            if package := find_reader_package(nested):
                return package
        return None
    if isinstance(value, list):
        for nested in value:
            if package := find_reader_package(nested):
                return package
        return None
    if not isinstance(value, str) or len(value.encode("utf-8")) > MAX_INPUT_BYTES:
        return None
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", value):
        try:
            decoded, _ = decoder.raw_decode(value, match.start())
        except json.JSONDecodeError:
            continue
        if package := find_reader_package(decoded):
            return package
    return None


def safe_artifact(value: Any) -> str:
    if not isinstance(value, str):
        return "unknown"
    parts = Path(value).parts
    for index, part in enumerate(parts):
        if part == "references" and index > 0:
            return "/".join(parts[index - 1 :])
    return Path(value).name or "unknown"


def safe_selections(value: Any) -> list[dict[str, Any]]:
    result = []
    if not isinstance(value, list):
        return result
    for item in value[:5]:
        if not isinstance(item, dict):
            continue
        headings = item.get("heading_path", [])
        result.append(
            {
                "kind": str(item.get("kind", "unknown"))[:40],
                "heading_path": [str(heading)[:200] for heading in headings[:5]]
                if isinstance(headings, list)
                else [],
                "start_line": item.get("start_line") if isinstance(item.get("start_line"), int) else None,
                "end_line": item.get("end_line") if isinstance(item.get("end_line"), int) else None,
            }
        )
    return result


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def capture_hook(root: Path, payload: dict[str, Any]) -> int:
    if not isinstance(payload, dict) or payload.get("hook_event_name") != "PostToolUse":
        return 0
    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if payload.get("tool_name") not in {"Bash", "unified_exec", "exec_command"} or not isinstance(command, str):
        return 0
    if "read-reference-sections.py" not in command:
        return 0
    try:
        require_enabled(root)
    except ValueError:
        return 0
    package = find_reader_package(payload.get("tool_response"))
    if package is None:
        return 0
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else ""
    event = {
        "event_type": "reference_selection",
        "session_id": str(payload.get("session_id", ""))[:200],
        "turn_id": str(payload.get("turn_id", ""))[:200],
        "model": str(payload.get("model", ""))[:200],
        "workspace_sha256": hashlib.sha256(cwd.encode("utf-8")).hexdigest(),
        "status": str(package.get("status", "unknown"))[:40],
        "artifact": safe_artifact(package.get("source")),
        "source_sha256": str(package.get("source_sha256", ""))[:64],
        "selections": safe_selections(package.get("selections")),
        "estimated_full_tokens": integer(package.get("estimated_full_tokens")),
        "estimated_selected_tokens": integer(package.get("estimated_selected_tokens")),
        "estimated_selected_tokens_range": [
            observed
            for observed in (
                integer(item)
                for item in package.get("estimated_selected_tokens_range", [])
                if isinstance(package.get("estimated_selected_tokens_range"), list)
            )
            if observed is not None
        ][:2],
        "estimated_savings_ratio": package.get("estimated_savings_ratio")
        if isinstance(package.get("estimated_savings_ratio"), (int, float))
        else None,
        "token_precision": "static-estimate",
    }
    return int(append_event(root, event))


def iter_events(root: Path, integrity: Counter[str] | None = None) -> Iterable[dict[str, Any]]:
    event_dir = root / "events"
    try:
        metadata = os.lstat(event_dir)
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise ValueError("events must be a real directory")
    for path in sorted(event_dir.glob("*.jsonl")):
        descriptor = open_regular(path, os.O_RDONLY)
        try:
            events, _, rejected_tail = decode_event_lines(read_fd_bytes(descriptor), str(path))
        finally:
            os.close(descriptor)
        if integrity is not None:
            integrity["rejected_tail_records"] += rejected_tail
        yield from events


def build_report(root: Path) -> dict[str, Any]:
    mode = read_mode(root)
    references = 0
    reference_statuses: Counter[str] = Counter()
    reference_usage: dict[str, Counter[str]] = {}
    skill_injections: Counter[str] = Counter()
    thread_skill_counts: Counter[str] = Counter()
    turn_tokens: Counter[str] = Counter()
    response_tokens: Counter[str] = Counter()
    latest_metrics: dict[tuple[str, ...], tuple[int, dict[str, Any]]] = {}
    unclassified_metrics: Counter[str] = Counter()
    integrity: Counter[str] = Counter()
    seen_events: set[str] = set()
    sessions = set()

    def add_metric(event: dict[str, Any]) -> None:
        if event.get("metric") == "codex.skill.injected":
            key = f"{event.get('skill', 'unknown')}:{event.get('status', 'unknown')}"
            skill_injections[key] += int(event.get("value", 0))
        elif event.get("metric") == "codex.turn.token_usage":
            turn_tokens[str(event.get("token_type", "unknown"))] += int(event.get("value", 0))
        elif str(event.get("metric", "")).startswith("codex.thread.skills."):
            key = str(event["metric"]).removeprefix("codex.thread.skills.")
            thread_skill_counts[key] += int(event.get("value", 0))

    for event in iter_events(root, integrity):
        fingerprint = str(event.get("event_id") or event_id_for(event))
        if fingerprint in seen_events:
            continue
        seen_events.add(fingerprint)
        if isinstance(event.get("session_id"), str) and event["session_id"]:
            sessions.add(event["session_id"])
        if event.get("event_type") == "storage_recovery":
            integrity["rejected_tail_records"] += integer(event.get("rejected_tail_records")) or 0
        elif event.get("event_type") == "reference_selection":
            references += 1
            reference_statuses[str(event.get("status", "unknown"))] += 1
            artifact = str(event.get("artifact", "unknown"))
            usage = reference_usage.setdefault(artifact, Counter())
            usage["loads"] += 1
            for key in ("estimated_full_tokens", "estimated_selected_tokens"):
                usage[key] += integer(event.get(key)) or 0
        elif event.get("metric") in METRICS:
            temporality = event.get("aggregation_temporality")
            if temporality in {"cumulative", "gauge"}:
                series = tuple(
                    str(event.get(key, ""))
                    for key in (
                        "metric",
                        "token_type",
                        "skill",
                        "status",
                        "model",
                        "app.version",
                        "auth_mode",
                        "originator",
                        "session_source",
                        "start_time_unix_nano",
                    )
                )
                observed_at = integer(event.get("time_unix_nano")) or 0
                if series not in latest_metrics or observed_at >= latest_metrics[series][0]:
                    latest_metrics[series] = (observed_at, event)
            elif temporality == "delta":
                add_metric(event)
            else:
                unclassified_metrics[str(event.get("metric", "unknown"))] += 1
        elif event.get("event_type") == "response_token_usage":
            for token_type, value in event.get("tokens", {}).items():
                response_tokens[str(token_type)] += int(value)
    for _, event in latest_metrics.values():
        add_metric(event)
    return {
        "schema_version": 1,
        "collection_status": mode.get("status", "unknown"),
        "readiness": mode.get("readiness", "unknown"),
        "precision": {
            "turn_and_response_tokens": "native-telemetry",
            "reference_tokens": "static-estimate",
            "skill_effectiveness": "requires-separate-evaluation",
        },
        "sessions_with_ids": len(sessions),
        "reference_selections": references,
        "reference_statuses": dict(sorted(reference_statuses.items())),
        "reference_usage": {
            artifact: dict(sorted(usage.items()))
            for artifact, usage in sorted(reference_usage.items())
        },
        "skill_injections": dict(sorted(skill_injections.items())),
        "thread_skill_counts": dict(sorted(thread_skill_counts.items())),
        "turn_tokens": dict(sorted(turn_tokens.items())),
        "response_tokens": dict(sorted(response_tokens.items())),
        "unclassified_metrics": dict(sorted(unclassified_metrics.items())),
        "integrity": {
            "rejected_tail_records": integrity["rejected_tail_records"],
        },
    }


def config_snippet(script_path: str) -> str:
    script = str(Path(script_path).expanduser().resolve())
    hook_command = json.dumps(shlex.join(["python3", script, "hook"]))
    return f'''# Review and merge into ~/.codex/config.toml only after explicit authorization.
[otel]
environment = "wise-agent-local"
log_user_prompt = false
exporter = {{ otlp-http = {{ endpoint = "http://127.0.0.1:4318/v1/logs", protocol = "json" }} }}
metrics_exporter = {{ otlp-http = {{ endpoint = "http://127.0.0.1:4318/v1/metrics", protocol = "json" }} }}
trace_exporter = "none"

[[hooks.PostToolUse]]
matcher = "Bash|unified_exec"

[[hooks.PostToolUse.hooks]]
type = "command"
command = {hook_command}
async = true
timeout = 3
'''


def receiver_health(port: int, opener=urllib.request.urlopen) -> str:
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    request = urllib.request.Request(f"http://127.0.0.1:{port}/health", method="GET")
    try:
        with opener(request, timeout=0.25) as response:
            payload = json.loads(response.read())
            return (
                "live"
                if response.status == 200
                and payload == {"service": "wise-agent-skill-usage", "status": "ok"}
                else "unexpected-response"
            )
    except (OSError, ValueError, json.JSONDecodeError):
        return "unreachable"


class OtlpHandler(BaseHTTPRequestHandler):
    root: Path

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        if self.path != "/health":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(HEALTH_BODY)))
        self.end_headers()
        self.wfile.write(HEALTH_BODY)

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        kind = {"/v1/logs": "logs", "/v1/metrics": "metrics"}.get(self.path)
        if kind is None:
            self.send_error(404)
            return
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
        if content_type != "application/json":
            self.send_error(415, "OTLP receiver accepts application/json only")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "invalid Content-Length")
            return
        if length <= 0 or length > MAX_INPUT_BYTES:
            self.send_error(413, "payload size is outside the accepted range")
            return
        try:
            payload = json.loads(self.rfile.read(length))
            ingest_otlp(self.root, kind, payload)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            self.send_error(400, str(exc))
            return
        except OSError as exc:
            self.send_error(500, str(exc))
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(OTLP_SUCCESS_BODY)))
        self.end_headers()
        self.wfile.write(OTLP_SUCCESS_BODY)

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(root: Path, port: int, once: bool) -> None:
    require_enabled(root)
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    handler = type("ConfiguredOtlpHandler", (OtlpHandler,), {"root": root})
    server = HTTPServer(("127.0.0.1", port), handler)
    print(f"LISTENING http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.handle_request() if once else server.serve_forever()
    finally:
        server.server_close()


def read_json_input(path: str | None) -> dict[str, Any]:
    if path in (None, "-"):
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("input exceeds the size limit")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "usage" / "wise-agent"
        enable(root)
        payload = {
            "resourceMetrics": [
                {
                    "scopeMetrics": [
                        {
                            "metrics": [
                                {
                                    "name": "codex.skill.injected",
                                    "sum": {
                                        "aggregationTemporality": 1,
                                        "dataPoints": [
                                            {
                                                "attributes": [
                                                    {"key": "skill", "value": {"stringValue": "wise-agent"}},
                                                    {"key": "status", "value": {"stringValue": "loaded"}},
                                                ],
                                                "timeUnixNano": "1000",
                                                "asInt": "1",
                                            }
                                        ]
                                    },
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        assert ingest_otlp(root, "metrics", payload) == 1
        assert build_report(root)["skill_injections"] == {"wise-agent:loaded": 1}
        disable(root)
        assert read_mode(root)["status"] == "disabled"
    print("skill usage observability self-test: OK")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", help="usage base; defaults to SKILL_USAGE_HOME or ~/.skill-usage")
    parser.add_argument("--self-test", action="store_true", help="run isolated self-tests")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("enable", help="enable metadata-only local collection")
    subparsers.add_parser("disable", help="disable future writes without deleting events")
    status = subparsers.add_parser("status", help="print current mode and receiver health")
    status.add_argument("--port", type=int, default=4318)
    subparsers.add_parser("hook", help="consume one Codex hook JSON object from stdin")
    subparsers.add_parser("report", help="print an aggregate JSON report")
    subparsers.add_parser("config", help="print reviewed Codex config snippets without writing them")
    ingest = subparsers.add_parser("ingest", help="ingest one explicit OTLP JSON payload")
    ingest.add_argument("--kind", required=True, choices=["logs", "metrics"])
    ingest.add_argument("--input", default="-", help="JSON file or - for stdin")
    receiver = subparsers.add_parser("serve", help="serve a loopback-only OTLP/HTTP JSON receiver")
    receiver.add_argument("--port", type=int, default=4318)
    receiver.add_argument("--once", action="store_true", help="exit after one request")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        run_self_test()
        return 0
    if not args.command:
        parser.error("a command is required")
    root = usage_home(args.home)
    try:
        if args.command == "enable":
            enable(root)
            print(f"ENABLED {mode_path(root)}")
        elif args.command == "disable":
            disable(root)
            print(f"DISABLED {mode_path(root)}")
        elif args.command == "status":
            print(
                json.dumps(
                    {
                        "data_home": str(root),
                        **read_mode(root),
                        "receiver": {
                            "endpoint": f"http://127.0.0.1:{args.port}",
                            "health": receiver_health(args.port),
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "hook":
            capture_hook(root, read_json_input("-"))
        elif args.command == "report":
            print(json.dumps(build_report(root), ensure_ascii=False, indent=2, sort_keys=True))
        elif args.command == "config":
            print(config_snippet(__file__))
        elif args.command == "ingest":
            print(f"ACCEPTED {ingest_otlp(root, args.kind, read_json_input(args.input))}")
        elif args.command == "serve":
            serve(root, args.port, args.once)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
