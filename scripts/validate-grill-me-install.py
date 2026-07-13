#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check that the local Codex grill-me skill is not a /grilling alias."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


REQUIRED_MARKERS = (
    "name: grill-me",
    "Interview me relentlessly",
    "shared understanding",
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
    grilling = skill_root / "grilling"
    errors: list[str] = []

    if grilling.exists():
        errors.append(f"unexpected legacy skill exists: {grilling}")

    if not grill_me.exists():
        errors.append(f"missing grill-me skill: {grill_me}")
        return errors

    text = grill_me.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"missing required marker in grill-me: {marker}")
    for marker in BANNED_MARKERS:
        if marker in text:
            errors.append(f"banned alias marker in grill-me: {marker}")

    return errors


def write_skill(codex_home: Path, body: str) -> None:
    target = codex_home / "skills" / "grill-me"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(body, encoding="utf-8")


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
                "Interview me relentlessly until we reach shared understanding.\n"
            ),
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
