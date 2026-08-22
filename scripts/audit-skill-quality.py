#!/usr/bin/env python3
"""Report advisory quality signals for local Codex skills.

This script is offline and read-only. It warns about maintainability smells
such as long trigger metadata or large SKILL.md bodies, but it does not fail validation by default
because these signals require human review.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


DESCRIPTION_WARN_CHARS = 260
DESCRIPTION_INFO_CHARS = 180
BODY_WARN_LINES = 200
BODY_HARD_HINT_LINES = 500
DEFAULT_PROMPT_WARN_CHARS = 190
DEFAULT_PROMPT_WORKFLOW_MARKERS = (
    "正式正文按",
    "详细执行控制",
    "完整工作流",
    "逐步执行以下流程",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    frontmatter = match.group(1)
    result: dict[str, str] = {}
    lines = frontmatter.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("name:"):
            result["name"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            if value in {"|", ">"}:
                block: list[str] = []
                i += 1
                while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                    block.append(lines[i].strip())
                    i += 1
                result["description"] = " ".join(part for part in block if part).strip()
                continue
            result["description"] = value.strip().strip('"')
        i += 1
    return result


def count_list_markers(description: str) -> int:
    return description.count("、") + description.count("/") + description.count("；")


def extract_default_prompt(text: str) -> str:
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("default_prompt:"):
            continue
        value = stripped.split(":", 1)[1].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value.strip()
    return ""


def analyze_skill(skill_md: Path) -> list[str]:
    text = read_text(skill_md)
    meta = extract_frontmatter(text)
    description = meta.get("description", "")
    body_lines = len(text.splitlines())
    warnings: list[str] = []
    rel = skill_md.as_posix()

    if not description:
        warnings.append(f"WARN {rel}: missing description")
        return warnings

    desc_len = len(description)
    marker_count = count_list_markers(description)
    if desc_len > DESCRIPTION_WARN_CHARS:
        warnings.append(
            f"WARN {rel}: description is {desc_len} chars; consider keeping trigger metadata concise"
        )
    elif desc_len > DESCRIPTION_INFO_CHARS:
        warnings.append(
            f"INFO {rel}: description is {desc_len} chars; review whether it is trigger-only"
        )
    if marker_count >= 12:
        warnings.append(
            f"WARN {rel}: description has {marker_count} list separators; check for capability-list bloat"
        )

    if body_lines > BODY_HARD_HINT_LINES:
        warnings.append(
            f"WARN {rel}: SKILL.md is {body_lines} lines; repository guidance says split long details to references"
        )
    elif body_lines > BODY_WARN_LINES:
        warnings.append(
            f"INFO {rel}: SKILL.md is {body_lines} lines; consider moving scenario details to references"
        )

    return warnings


def analyze_agent_metadata(skill_dir: Path) -> list[str]:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.is_file():
        return []
    prompt = extract_default_prompt(read_text(path))
    if not prompt:
        return [f"WARN {path.as_posix()}: missing default_prompt"]
    warnings: list[str] = []
    if len(prompt) > DEFAULT_PROMPT_WARN_CHARS:
        warnings.append(
            f"WARN {path.as_posix()}: default_prompt is {len(prompt)} chars; keep Level-1 metadata concise"
        )
    markers = [marker for marker in DEFAULT_PROMPT_WORKFLOW_MARKERS if marker in prompt]
    if markers:
        warnings.append(
            f"WARN {path.as_posix()}: default_prompt contains workflow detail: {', '.join(markers)}"
        )
    return warnings


def audit(root: Path) -> list[str]:
    warnings: list[str] = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        warnings.extend(analyze_skill(skill_md))
        warnings.extend(analyze_agent_metadata(skill_md.parent))
    return warnings


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill_dir = root / "sample-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
name: sample-skill
description: |
  Use when A、B、C、D、E、F、G、H、I、J、K、L、M、N and the agent needs a long trigger description that starts to behave like a workflow summary rather than a routing signal.
---

# Sample
"""
            + "\n".join(f"- line {i}" for i in range(220)),
            encoding="utf-8",
        )
        warnings = audit(root)
        assert any("description" in warning for warning in warnings), warnings
        assert any("SKILL.md is" in warning for warning in warnings), warnings
    print("OK skill quality audit self-test")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run local self-test")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return non-zero when WARN lines are emitted; INFO lines remain advisory",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0

    warnings = audit(Path("."))
    for warning in warnings:
        print(warning)
    if not warnings:
        print("OK skill quality audit")
    if args.strict and any(warning.startswith("WARN ") for warning in warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
