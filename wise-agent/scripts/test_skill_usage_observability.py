#!/usr/bin/env python3
"""Contract tests for the local wise-agent usage observability helper."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).with_name("skill-usage-observability.py")
ROOT = Path(__file__).resolve().parents[2]


def load_module():
    assert SCRIPT.is_file(), f"missing production script: {SCRIPT}"
    spec = importlib.util.spec_from_file_location("skill_usage_observability", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_package() -> dict[str, object]:
    return {
        "status": "ready",
        "source": "/Users/example/project/wise-agent/references/capability-routing.md",
        "source_sha256": "a" * 64,
        "query": "控制成本与停止",
        "matched_task": "控制成本与停止",
        "selections": [
            {
                "kind": "section",
                "heading_path": ["二 C、章节级 JIT 加载"],
                "start_line": 88,
                "end_line": 107,
            }
        ],
        "estimated_full_tokens": 5000,
        "estimated_selected_tokens": 1200,
        "estimated_selected_tokens_range": [900, 1500],
        "estimated_savings_ratio": 0.76,
        "token_estimate_method": "final JSON package mixed-text heuristic; not model billing telemetry",
        "content": "PRIVATE SOURCE CONTENT MUST NOT BE STORED",
    }


def sample_metrics() -> dict[str, object]:
    return {
        "resourceMetrics": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "codex"}},
                        {"key": "private.attribute", "value": {"stringValue": "DO NOT STORE"}},
                    ]
                },
                "scopeMetrics": [
                    {
                        "metrics": [
                            {
                                "name": "codex.turn.token_usage",
                                "histogram": {
                                    "aggregationTemporality": 1,
                                    "dataPoints": [
                                        {
                                            "attributes": [
                                                {"key": "token_type", "value": {"stringValue": "input"}},
                                                {"key": "model", "value": {"stringValue": "gpt-test"}},
                                            ],
                                            "timeUnixNano": "1000000000",
                                            "sum": 321,
                                        }
                                    ]
                                },
                            },
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
                                            "timeUnixNano": "1000000001",
                                            "asInt": "1",
                                        }
                                    ]
                                },
                            },
                            {
                                "name": "codex.thread.skills.kept_total",
                                "gauge": {
                                    "dataPoints": [
                                        {"timeUnixNano": "1000000002", "asInt": "7"}
                                    ]
                                },
                            },
                        ]
                    }
                ],
            }
        ]
    }


def sample_logs(observed_at: int = 2000000000) -> dict[str, object]:
    return {
        "resourceLogs": [
            {
                "scopeLogs": [
                    {
                        "logRecords": [
                            {
                                "timeUnixNano": str(observed_at),
                                "body": {"stringValue": "PRIVATE TOOL OUTPUT MUST NOT BE STORED"},
                                "attributes": [
                                    {"key": "event.name", "value": {"stringValue": "codex.sse_event"}},
                                    {"key": "kind", "value": {"stringValue": "response.completed"}},
                                    {"key": "conversation.id", "value": {"stringValue": "thr_test"}},
                                    {"key": "input_tokens", "value": {"intValue": "400"}},
                                    {"key": "cached_input_tokens", "value": {"intValue": "100"}},
                                    {"key": "output_tokens", "value": {"intValue": "50"}},
                                ],
                            }
                        ]
                    }
                ]
            }
        ]
    }


def gauge_metric(value: int, observed_at: int) -> dict[str, object]:
    return {
        "resourceMetrics": [
            {
                "scopeMetrics": [
                    {
                        "metrics": [
                            {
                                "name": "codex.thread.skills.kept_total",
                                "gauge": {
                                    "dataPoints": [
                                        {
                                            "timeUnixNano": str(observed_at),
                                            "asInt": str(value),
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


def cumulative_token_metric(value: int, observed_at: int) -> dict[str, object]:
    return {
        "resourceMetrics": [
            {
                "scopeMetrics": [
                    {
                        "metrics": [
                            {
                                "name": "codex.turn.token_usage",
                                "histogram": {
                                    "aggregationTemporality": 2,
                                    "dataPoints": [
                                        {
                                            "attributes": [
                                                {"key": "token_type", "value": {"stringValue": "output"}}
                                            ],
                                            "startTimeUnixNano": "1000",
                                            "timeUnixNano": str(observed_at),
                                            "sum": value,
                                        }
                                    ],
                                },
                            }
                        ]
                    }
                ]
            }
        ]
    }


def delta_token_metric(value: int, observed_at: int) -> dict[str, object]:
    payload = cumulative_token_metric(value, observed_at)
    histogram = payload["resourceMetrics"][0]["scopeMetrics"][0]["metrics"][0]["histogram"]
    histogram["aggregationTemporality"] = 1
    return payload


def read_events(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted((root / "events").glob("*.jsonl")):
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
    return rows


def assert_repository_integration() -> None:
    skill = (ROOT / "wise-agent" / "SKILL.md").read_text(encoding="utf-8")
    reference_path = ROOT / "wise-agent" / "references" / "skill-usage-observability.md"
    assert reference_path.is_file(), f"missing usage reference: {reference_path}"
    reference = reference_path.read_text(encoding="utf-8")
    validate = (ROOT / "scripts" / "validate.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "references/skill-usage-observability.md" in skill
    for expected in (
        "精确遥测",
        "静态估算",
        "不得保存 prompt、回答正文、源码正文或原始遥测载荷",
        "skill-usage-observability.py enable",
        "skill-usage-observability.py report",
        "确定性事件 ID",
        "`Gauge` 与 `Cumulative`",
        "`integrity.rejected_tail_records`",
        "接收器健康",
    ):
        assert expected in reference
    assert "skill-usage-observability.py --self-test" in validate
    assert "test_skill_usage_observability.py" in validate
    assert "skill-usage-observability.py enable" in readme


def main() -> None:
    module = load_module()
    assert_repository_integration()
    with tempfile.TemporaryDirectory() as temp_dir:
        shared_base = Path(temp_dir) / "shared-base"
        shared_base.mkdir(mode=0o755)
        unsafe_root = shared_base / "wise-agent"
        unsafe_root.mkdir(mode=0o700)
        victim = Path(temp_dir) / "mode-victim.txt"
        victim.write_text("KEEP", encoding="utf-8")
        (unsafe_root / "mode.json.tmp").symlink_to(victim)
        module.enable(unsafe_root)
        assert victim.read_text(encoding="utf-8") == "KEEP", "mode write followed a temporary symlink"
        assert stat.S_IMODE(shared_base.stat().st_mode) == 0o755, "enable changed caller-owned base permissions"

        event_root = Path(temp_dir) / "event-root"
        module.enable(event_root)
        event_dir = event_root / "events"
        event_dir.mkdir(mode=0o700)
        event_victim = Path(temp_dir) / "event-victim.txt"
        event_victim.write_text("KEEP", encoding="utf-8")
        event_path = event_dir / f"{datetime.now(timezone.utc).date().isoformat()}.jsonl"
        event_path.symlink_to(event_victim)
        try:
            module.append_event(event_root, {"event_type": "fixture"})
        except (OSError, ValueError):
            pass
        else:
            raise AssertionError("event append followed a symlink")
        assert event_victim.read_text(encoding="utf-8") == "KEEP"

        event_dir_root = Path(temp_dir) / "event-dir-root"
        module.enable(event_dir_root)
        event_dir_victim = Path(temp_dir) / "event-dir-victim"
        event_dir_victim.mkdir()
        (event_dir_root / "events").symlink_to(event_dir_victim, target_is_directory=True)
        try:
            module.append_event(event_dir_root, {"event_type": "fixture"})
        except (OSError, ValueError):
            pass
        else:
            raise AssertionError("event append followed a symlinked events directory")
        assert not list(event_dir_victim.iterdir())

        root = Path(temp_dir) / "usage" / "wise-agent"
        module.enable(root)
        assert module.read_mode(root)["readiness"] == "PILOT_PENDING"
        assert stat.S_IMODE(root.stat().st_mode) == 0o700
        assert stat.S_IMODE((root / "mode.json").stat().st_mode) == 0o600

        hook = {
            "session_id": "thr_test",
            "turn_id": "turn_test",
            "cwd": "/Users/example/project",
            "model": "gpt-test",
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {
                "command": "python3 wise-agent/scripts/read-reference-sections.py wise-agent/references --query test"
            },
            "tool_response": {"output": json.dumps(sample_package(), ensure_ascii=False)},
        }
        assert module.capture_hook(root, hook) == 1
        assert module.capture_hook(root, {**hook, "turn_id": "turn_unified", "tool_name": "unified_exec"}) == 1
        assert module.capture_hook(root, {**hook, "tool_input": {"command": "git status"}}) == 0
        assert module.ingest_otlp(root, "metrics", sample_metrics()) == 3
        assert module.ingest_otlp(root, "metrics", cumulative_token_metric(100, 2000)) == 1
        assert module.ingest_otlp(root, "metrics", cumulative_token_metric(150, 3000)) == 1
        assert module.ingest_otlp(root, "metrics", delta_token_metric(10, 4000)) == 1
        assert module.ingest_otlp(root, "metrics", delta_token_metric(10, 4000)) == 0
        assert module.ingest_otlp(root, "metrics", gauge_metric(9, 5000000000)) == 1
        assert module.ingest_otlp(root, "logs", sample_logs()) == 1
        assert module.ingest_otlp(root, "logs", sample_logs()) == 0

        events = read_events(root)
        serialized = json.dumps(events, ensure_ascii=False)
        assert "PRIVATE SOURCE CONTENT" not in serialized
        assert "PRIVATE TOOL OUTPUT" not in serialized
        assert "DO NOT STORE" not in serialized
        assert "/Users/example" not in serialized
        reference = next(row for row in events if row["event_type"] == "reference_selection")
        assert reference["artifact"] == "wise-agent/references/capability-routing.md"
        assert reference["estimated_selected_tokens"] == 1200
        assert any(row.get("metric") == "codex.turn.token_usage" for row in events)
        assert any(row.get("skill") == "wise-agent" for row in events)
        assert any(row["event_type"] == "response_token_usage" for row in events)

        report = module.build_report(root)
        assert report["reference_selections"] == 2
        reference_usage = report["reference_usage"]["wise-agent/references/capability-routing.md"]
        assert reference_usage["loads"] == 2
        assert reference_usage["estimated_selected_tokens"] == 2400
        assert report["skill_injections"]["wise-agent:loaded"] == 1
        assert report["thread_skill_counts"]["kept_total"] == 9
        assert report["turn_tokens"]["input"] == 321
        assert report["turn_tokens"]["output"] == 160
        assert report["response_tokens"]["input"] == 400

        assert module.OTLP_SUCCESS_BODY == b"{}"

        class HealthyResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            @staticmethod
            def read() -> bytes:
                return b'{"service":"wise-agent-skill-usage","status":"ok"}'

        assert module.receiver_health(4318, lambda *_args, **_kwargs: HealthyResponse()) == "live"

        request_body = json.dumps(sample_logs(2000000001)).encode("utf-8")
        handler = object.__new__(module.OtlpHandler)
        handler.root = root
        handler.path = "/v1/logs"
        handler.headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(request_body)),
        }
        handler.rfile = io.BytesIO(request_body)
        handler.wfile = io.BytesIO()
        statuses = []
        handler.send_response = statuses.append
        handler.send_header = lambda *_args: None
        handler.end_headers = lambda: None
        handler.send_error = lambda code, *_args: statuses.append(code)
        handler.do_POST()
        assert statuses == [200]
        assert handler.wfile.getvalue() == b"{}"

        missing_temporality = sample_metrics()
        del missing_temporality["resourceMetrics"][0]["scopeMetrics"][0]["metrics"][0][
            "histogram"
        ]["aggregationTemporality"]
        try:
            module.ingest_otlp(root, "metrics", missing_temporality)
        except ValueError as exc:
            assert "aggregationTemporality" in str(exc)
        else:
            raise AssertionError("metric without aggregation temporality was accepted")

        snippet = module.config_snippet("/absolute/path/to/skill-usage-observability.py")
        assert "127.0.0.1:4318" in snippet
        assert "log_user_prompt = false" in snippet
        assert "unified_exec" in snippet

        module.disable(root)
        try:
            module.ingest_otlp(root, "metrics", sample_metrics())
        except ValueError as exc:
            assert "does not grant" in str(exc)
        else:
            raise AssertionError("disabled usage mode accepted telemetry")

    with tempfile.TemporaryDirectory() as temp_dir:
        base = Path(temp_dir)
        root = base / "usage" / "wise-agent"
        module.enable(root)
        assert module.ingest_otlp(root, "logs", sample_logs()) == 1
        event_path = next((root / "events").glob("*.jsonl"))
        event_path.unlink()
        victim = base / "event-hardlink-victim.jsonl"
        victim.write_text("hardlink sentinel\n", encoding="utf-8")
        os.link(victim, event_path)
        try:
            module.ingest_otlp(root, "logs", sample_logs(2000000001))
        except (OSError, ValueError):
            pass
        else:
            raise AssertionError("event writer accepted a hardlinked event file")
        assert victim.read_text(encoding="utf-8") == "hardlink sentinel\n"

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "usage" / "wise-agent"
        module.enable(root)
        assert module.ingest_otlp(root, "logs", sample_logs()) == 1
        event_path = next((root / "events").glob("*.jsonl"))
        with event_path.open("ab") as stream:
            stream.write(b'{"truncated":')
        report = module.build_report(root)
        assert report["integrity"]["rejected_tail_records"] == 1
        assert report["response_tokens"]["input"] == 400

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "usage" / "wise-agent"
        module.enable(root)
        assert module.ingest_otlp(root, "logs", sample_logs()) == 1
        event_path = next((root / "events").glob("*.jsonl"))
        event_path.write_bytes(event_path.read_bytes().rstrip(b"\n"))
        assert module.ingest_otlp(root, "logs", sample_logs(2000000001)) == 1
        assert module.build_report(root)["response_tokens"]["input"] == 800

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "usage" / "wise-agent"
        module.enable(root)
        assert module.ingest_otlp(root, "logs", sample_logs()) == 1
        event_path = next((root / "events").glob("*.jsonl"))
        event_path.rename(event_path.with_name("2000-01-01.jsonl"))
        assert module.ingest_otlp(root, "logs", sample_logs()) == 0
        assert len(list((root / "events").glob("*.jsonl"))) == 1

    print("skill usage observability contract tests: OK")


if __name__ == "__main__":
    main()
