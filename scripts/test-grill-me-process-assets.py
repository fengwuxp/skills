#!/usr/bin/env python3
"""Regression check for the grill-me process-asset contract."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def require_markers(path: Path, markers: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return [f"{path}: missing fixture"]
    text = path.read_text(encoding="utf-8")
    return [f"{path}: missing {marker}" for marker in markers if marker not in text]


def check_fixture_structure(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []
    blocks = re.findall(
        r"^- 资产 ID: (PA-\d+)\n(?P<body>.*?)(?=\n- 资产 ID:|\n## Question record)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    expected = {"PA-001", "PA-002", "PA-003"}
    found = {asset_id for asset_id, _ in blocks}
    if found != expected:
        errors.append(f"{path}: asset IDs are not exactly {sorted(expected)}")
    for asset_id, body in blocks:
        for marker in (
            "类型:",
            "来源锚点:",
            "状态:",
            "正典效力:",
            "queue_state:",
            "deferred_until:",
            "影响 / 下游消费者:",
        ):
            if marker not in body:
                errors.append(f"{path}: {asset_id} missing {marker}")
    question = text.split("## Question record", 1)[-1]
    for asset_id in sorted(expected):
        if asset_id not in question:
            errors.append(f"{path}: question record does not reference {asset_id}")
    if "正典效力: process assets are not the business decision" not in question:
        errors.append(f"{path}: pending decision boundary is missing")
    return errors


def check_resolution_fixtures() -> list[str]:
    errors = []
    fixture_dir = ROOT / "grill-me" / "fixtures" / "behavior-evidence"
    errors.extend(
        require_markers(
            fixture_dir / "deferred-resolution.md",
            (
                "设计分辨率",
                "queue_state: deferred",
                "deferred_until:",
                "不继续下钻",
                "最终结论：pending",
            ),
        )
    )
    errors.extend(
        require_markers(
            fixture_dir / "mixed-answer-intent.md",
            (
                "A + 部分 B",
                "行动意图",
                "结果：pending",
                "不推定命中",
            ),
        )
    )
    return errors


def main() -> int:
    errors = []
    errors.extend(
        require_markers(
            ROOT / "grill-me" / "SKILL.md",
            (
                "过程资产",
                "过程资产索引",
                "仅交接，不构成正典",
                "设计分辨率",
                "queue_state",
                "deferred_until",
                "意图与结果",
                "写回检查点",
            ),
        )
    )
    errors.extend(
        require_markers(
            ROOT / "grill-me" / "references" / "question-ledger.md",
            (
                "过程资产索引",
                "资产 ID",
                "正典效力",
                "升格条件",
                "领域载荷",
                "相关过程资产供恢复/交接核对",
                "当前交付",
                "设计分辨率",
                "queue_state: active / deferred",
                "deferred_until",
                "行动意图",
                "结果 / 后果",
                "写回检查点",
                "名相与决策写回路由",
                "领域名相",
                "产品概念",
                "工程决策",
                "过程细节",
                "ADR candidate",
                "难逆",
                "无背景会意外",
                "真实取舍",
                "writeback candidate",
                "candidate_status",
                "target_status",
                "目标权威支持版本替代时",
                "不自动创建 `CONTEXT.md`",
            ),
        )
    )
    errors.extend(
        require_markers(
            ROOT / "grill-me" / "references" / "source-map.md",
            (
                "2026-09-01",
                "grill-with-docs",
                "domain-modeling",
                "CONTEXT.md",
                "ADR 编号并发",
                "旧词条失效",
                "不新增平级 `grill-with-docs`",
            ),
        )
    )
    fixture = ROOT / "grill-me" / "fixtures" / "behavior-evidence" / "process-asset-decision.md"
    errors.extend(
        require_markers(
            fixture,
            (
                "accepted-detail",
                "process-only",
                "handoff-only",
                "状态:",
                "正典效力:",
                "过程资产索引",
                "最终结论：pending",
                "替代记录 / replacement",
            ),
        )
    )
    if fixture.exists():
        errors.extend(check_fixture_structure(fixture))
    errors.extend(check_resolution_fixtures())
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("OK grill-me process-asset contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
