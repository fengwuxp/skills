#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check that the installed grill-me preserves the project-owned contract."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


REQUIRED_SKILL_MARKERS = (
    "name: grill-me",
    "shared understanding",
    "一次只问一个",
    "推荐答案",
    "Facts",
    "Decisions",
    "问题台账",
    "证据裁决",
    "ask-owner",
    "每条记录都必须原样保留 `裁决动作：<action>` 与 `最终结论：<state>`",
    "未确认前不执行",
)

REQUIRED_LEDGER_MARKERS = (
    "问题 ID",
    "决策主题",
    "已查证据",
    "最终结论",
    "red_lines",
    "语义重复",
    "证据先行的问询裁决",
    "命题类型",
    "置信边界",
    "裁决动作到最终结论的确定映射",
    "历史恢复、语义去重和决策快照只读取最终结论",
    "每条记录都必须原样包含 `裁决动作：<action>` 和 `最终结论：<state>`",
)

BANNED_MARKERS = (
    "name: grilling",
    "Run a `/grilling`",
    "/grilling",
    "grilling",
)


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()


def validate_install(codex_home: Path) -> list[str]:
    skill_root = codex_home / "skills"
    grill_me = skill_root / "grill-me" / "SKILL.md"
    question_ledger = skill_root / "grill-me" / "references" / "question-ledger.md"
    grilling = skill_root / "grilling"
    errors: list[str] = []

    if grilling.exists():
        errors.append(f"unexpected legacy skill exists: {grilling}")

    if not grill_me.exists():
        errors.append(f"missing grill-me skill: {grill_me}")
        return errors

    text = grill_me.read_text(encoding="utf-8")
    for marker in REQUIRED_SKILL_MARKERS:
        if marker not in text:
            errors.append(f"missing required marker in grill-me: {marker}")
    for marker in BANNED_MARKERS:
        if marker in text:
            errors.append(f"banned alias marker in grill-me: {marker}")

    if not question_ledger.exists():
        errors.append(f"missing grill-me question ledger: {question_ledger}")
        return errors

    ledger_text = question_ledger.read_text(encoding="utf-8")
    for marker in REQUIRED_LEDGER_MARKERS:
        if marker not in ledger_text:
            errors.append(f"missing required marker in question ledger: {marker}")

    return errors


def write_skill(codex_home: Path, body: str, ledger_body: str | None = None) -> None:
    target = codex_home / "skills" / "grill-me"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(body, encoding="utf-8")
    if ledger_body is not None:
        references = target / "references"
        references.mkdir()
        (references / "question-ledger.md").write_text(ledger_body, encoding="utf-8")


def self_test() -> None:
    with TemporaryDirectory() as tmp:
        codex_home = Path(tmp)
        write_skill(
            codex_home,
            "---\nname: grill-me\n---\nRun a `/grilling` session instead.\n",
        )
        (codex_home / "skills" / "grilling").mkdir()
        errors = validate_install(codex_home)
        assert any("legacy skill" in error for error in errors), errors
        assert any("/grilling" in error for error in errors), errors

    with TemporaryDirectory() as tmp:
        codex_home = Path(tmp)
        write_skill(
            codex_home,
            (
                "---\n"
                "name: grill-me\n"
                "---\n"
                "一次只问一个问题并给推荐答案，Facts 先查，Decisions 再问。\n"
                "先做证据裁决，只有 ask-owner 才提问。\n"
                "每条记录都必须原样保留 `裁决动作：<action>` 与 `最终结论：<state>`。\n"
                "维护问题台账，达到 shared understanding 前未确认前不执行。\n"
            ),
            "问题 ID / 决策主题 / 已查证据 / 最终结论 / red_lines / 语义重复\n"
            "证据先行的问询裁决 / 命题类型 / 置信边界\n"
            "裁决动作到最终结论的确定映射\n"
            "历史恢复、语义去重和决策快照只读取最终结论\n"
            "每条记录都必须原样包含 `裁决动作：<action>` 和 `最终结论：<state>`\n",
        )
        assert validate_install(codex_home) == []


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        self_test()
        print("OK validate-grill-me-install self-test")
        return 0
    if argv:
        print("usage: validate-grill-me-install.py [--self-test]", file=sys.stderr)
        return 2

    errors = validate_install(default_codex_home())
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    print(f"OK grill-me install: {default_codex_home() / 'skills' / 'grill-me' / 'SKILL.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
