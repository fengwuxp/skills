#!/usr/bin/env python3
"""Find a few high-confidence UI source anti-patterns.

The checker reads explicit local paths, writes nothing, and does not access the network.
It is intentionally not a parser and does not prove usability, semantics, or WCAG conformance.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SOURCE_SUFFIXES = {".css", ".htm", ".html", ".jsx", ".less", ".sass", ".scss", ".svelte", ".tsx", ".vue"}
IGNORED_DIRS = {".git", ".next", "build", "coverage", "dist", "node_modules"}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str
    message: str


LINE_RULES = (
    (
        "zoom-disabled",
        re.compile(r'<meta\b(?=[^>]*\bname\s*=\s*["\']viewport["\'])[^>]*(?:user-scalable\s*=\s*(?:no|0)|maximum-scale\s*=\s*1(?:\.0+)?)', re.I),
        "Do not disable browser zoom in the viewport declaration.",
    ),
    (
        "transition-all",
        re.compile(r"\btransition-all\b|\btransition\s*:\s*all\b", re.I),
        "Transition named properties instead of every property.",
    ),
    (
        "non-semantic-click",
        re.compile(r"<(?:div|span)\b[^>]*\sonclick\s*=", re.I),
        "Use a semantic interactive element instead of a clickable div or span.",
    ),
    (
        "paste-blocked",
        re.compile(r"\sonpaste\s*=.*\bpreventdefault\s*\(", re.I),
        "Do not block paste in form controls.",
    ),
)

BLOCK_COMMENT_PATTERN = re.compile(r"/\*.*?\*/|<!--.*?-->", re.DOTALL)
LINE_COMMENT_PATTERN = re.compile(r"(?m)(?<!:)//.*$")


def mask_comments(text: str) -> str:
    masked = BLOCK_COMMENT_PATTERN.sub(lambda match: re.sub(r"[^\n]", " ", match.group()), text)
    return LINE_COMMENT_PATTERN.sub(lambda match: " " * len(match.group()), masked)


# ponytail: line-level matching stays dependency-free; use language parsers if false results become material.
def scan_text(text: str, path: Path = Path("<text>")) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(mask_comments(text).splitlines(), start=1):
        for rule, pattern, message in LINE_RULES:
            if pattern.search(line):
                findings.append(Finding(path, line_number, rule, message))
    return findings


def scan_file(path: Path) -> list[Finding]:
    return scan_text(path.read_text(encoding="utf-8"), path)


def iter_source_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in SOURCE_SUFFIXES:
                yield path
            continue
        for candidate in path.rglob("*"):
            if any(part in IGNORED_DIRS for part in candidate.parts):
                continue
            if candidate.is_file() and candidate.suffix.lower() in SOURCE_SUFFIXES:
                yield candidate


def self_test() -> int:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    valid = scan_file(fixtures / "source-valid.tsx")
    invalid = {finding.rule for finding in scan_file(fixtures / "source-invalid.tsx")}
    expected = {"zoom-disabled", "transition-all", "non-semantic-click", "paste-blocked"}
    if valid or invalid != expected:
        print(f"FAIL UI source checker: valid={valid}, invalid={sorted(invalid)}")
        return 1
    print("UI source checker self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="UI source files or directories")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.paths:
        parser.error("provide at least one file or directory")
    missing = [path for path in args.paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"ERROR path does not exist: {path}", file=sys.stderr)
        return 2

    try:
        findings = [finding for path in iter_source_files(args.paths) for finding in scan_file(path)]
    except (OSError, UnicodeError) as error:
        print(f"ERROR unable to read UI source: {error}", file=sys.stderr)
        return 2

    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.rule} - {finding.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
