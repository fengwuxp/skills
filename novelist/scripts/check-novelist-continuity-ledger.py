#!/usr/bin/env python3
"""Check stable decision IDs and references in a Markdown fiction project.

Input: an explicit project root and a ledger path relative to that root.
Output: a local summary on stdout or validation errors on stderr.
Writes/network: none.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


DECISION_ID = re.compile(r"(?<![A-Za-z0-9_-])RW-[0-9]{3}(?![A-Za-z0-9_-])")
DEFINITION = re.compile(r"^\|\s*(RW-[0-9]{3})\s*\|")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check(root: Path, ledger: Path) -> list[str]:
    root = root.resolve(strict=True)
    ledger = ledger.resolve(strict=True)
    errors: list[str] = []
    definitions: dict[str, int] = {}

    for line_number, line in enumerate(read_text(ledger).splitlines(), start=1):
        match = DEFINITION.match(line)
        if not match:
            continue
        decision_id = match.group(1)
        if decision_id in definitions:
            errors.append(
                f"duplicate definition {decision_id}: "
                f"{ledger.relative_to(root)}:{definitions[decision_id]} and {line_number}"
            )
        else:
            definitions[decision_id] = line_number

    references: dict[str, list[str]] = defaultdict(list)
    markdown_files: list[tuple[Path, Path]] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        resolved = path.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError:
            errors.append(f"Markdown file is outside project root: {relative}")
            continue
        markdown_files.append((relative, resolved))

    for relative, path in markdown_files:
        for line_number, line in enumerate(read_text(path).splitlines(), start=1):
            for decision_id in DECISION_ID.findall(line):
                references[decision_id].append(f"{relative}:{line_number}")

    for decision_id in sorted(references.keys() - definitions.keys()):
        errors.append(f"unresolved reference {decision_id}: {references[decision_id][0]}")

    if not definitions:
        errors.append(f"no decision definitions found in {ledger.relative_to(root)}")

    if not errors:
        print(
            "OK continuity ledger: "
            f"{len(definitions)} definitions, {len(references)} referenced IDs, "
            f"{len(markdown_files)} Markdown files"
        )
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check unique RW-nnn definitions and resolvable Markdown references."
    )
    parser.add_argument("--root", type=Path, required=True, help="fiction project root")
    parser.add_argument(
        "--ledger",
        type=Path,
        required=True,
        help="decision ledger path relative to the project root",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    ledger = (root / args.ledger).resolve()

    if not root.is_dir():
        print(f"FAIL project root is not a directory: {root}", file=sys.stderr)
        return 1
    try:
        ledger.relative_to(root)
    except ValueError:
        print(f"FAIL ledger is outside project root: {ledger}", file=sys.stderr)
        return 1
    if not ledger.is_file():
        print(f"FAIL ledger does not exist: {ledger}", file=sys.stderr)
        return 1

    try:
        errors = check(root, ledger)
    except (OSError, UnicodeError) as error:
        print(f"FAIL cannot read project Markdown: {error}", file=sys.stderr)
        return 1

    for error in errors:
        print(f"FAIL {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
