#!/usr/bin/env python3
"""Offline, read-only pre-scan for high-confidence Agent Skill risks."""

from __future__ import annotations

import argparse
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path


MAX_TEXT_BYTES = 4 * 1024 * 1024
SKIP_DIRS = {
    ".git",
    ".idea",
    ".serena",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}
TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".csv",
    ".gradle",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsonl",
    ".kt",
    ".kts",
    ".lock",
    ".md",
    ".properties",
    ".py",
    ".rb",
    ".sh",
    ".sql",
    ".svg",
    ".toml",
    ".ts",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {"Dockerfile", "Gemfile", "Justfile", "Makefile"}
HIDDEN_UNICODE = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\u200e",
    "\u200f",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2060",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
    "\ufeff",
}
OPERATIONAL_PATTERNS = (
    (
        "remote-pipe-exec",
        re.compile(
            r"(?:curl|wget)\s+[^\n|]+\|\s*(?:ba)?sh\b|"
            r"curl\s+[^\n|]+\|\s*(?:python|ruby|perl)\b",
            re.IGNORECASE,
        ),
        "remote content is piped directly into an interpreter",
    ),
    (
        "instruction-hijack",
        re.compile(
            r"ignore\s+(?:previous|above|all)\s+(?:instructions?|rules?|prompts?)|"
            r"SYSTEM\s*OVERRIDE|<\|im_start\|>|"
            r"forget\s+(?:everything|your\s+instructions)",
            re.IGNORECASE,
        ),
        "instruction text attempts to override the active authority chain",
    ),
    (
        "memory-persistence",
        re.compile(
            r"(?:append|write|追加|写入).{0,120}"
            r"(?:~?/|\$HOME/|\$\{?CODEX_HOME\}?/)?"
            r"\.(?:codex|claude)/(?:memories|memory|skills)",
            re.IGNORECASE | re.DOTALL,
        ),
        "instructions write persistent Agent rules or skills outside the package",
    ),
    (
        "system-persistence",
        re.compile(
            r"\bcrontab\b|\bsystemctl\s+enable\b|"
            r"\blaunchctl\s+(?:load|bootstrap)\b|\bschtasks\b|authorized_keys",
            re.IGNORECASE,
        ),
        "instructions establish host persistence",
    ),
    (
        "tool-hijack",
        re.compile(
            r"\bgit\s+config(?:\s+--[\w-]+)*\s+core\.hooksPath\b|"
            r"\balias\s+(?:git|curl|python|codex)\s*=|"
            r"\b(?:cp|mv|install)\b[^\n]*(?:/usr/local/bin|\.local/bin)",
            re.IGNORECASE,
        ),
        "instructions replace or intercept a trusted tool path",
    ),
)
CREDENTIAL_PATTERN = re.compile(
    r"OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_ACCESS_KEY|AWS_SECRET|"
    r"(?:api[_-]?key|access[_-]?token|password|secret|private[_-]?key)",
    re.IGNORECASE,
)
OUTBOUND_PATTERN = re.compile(
    r"(?:requests|httpx)\.request\s*\(\s*(?:method\s*=\s*)?['\"](?:POST|PUT|PATCH)['\"]|"
    r"\.(?:post|put|patch)\s*\(|urlopen\s*\(|fetch\s*\(|"
    r"curl\s+[^\n]*(?:-d(?:\s|=)|--data(?:-[\w-]+)?(?:\s|=)|"
    r"-F(?:\s|=)|--form(?:\s|=)|-T(?:\s|=)|--upload-file(?:\s|=))",
    re.IGNORECASE,
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    code: str
    message: str


def is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def is_text_file(path: Path) -> bool:
    return path.name in TEXT_NAMES or path.suffix.lower() in TEXT_SUFFIXES


def skill_roots(root: Path) -> tuple[Path, ...]:
    if (root / "SKILL.md").is_file():
        return (root,)
    return tuple(path.parent for path in sorted(root.glob("*/SKILL.md")) if path.is_file())


def is_operational(path: Path, roots: tuple[Path, ...]) -> bool:
    if path.name == "SKILL.md":
        return True
    for skill_root in roots:
        try:
            relative = path.relative_to(skill_root)
        except ValueError:
            continue
        if relative.parts[:1] == ("scripts",):
            return True
    return False


def audit(root: Path, ignore_local_generated_pyc: bool = False) -> tuple[list[Finding], int]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    findings: list[Finding] = []
    checked_files = 0
    roots = skill_roots(root)

    def handle_walk_error(exc: OSError) -> None:
        path = Path(exc.filename) if exc.filename else root
        relative = str(path.relative_to(root)) if is_within(path, root) else str(path)
        findings.append(Finding(relative, 1, "unreadable-directory", "directory could not be read"))

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=handle_walk_error):
        current = Path(dirpath)
        retained_dirs = []
        for name in sorted(dirnames):
            path = current / name
            if name in SKIP_DIRS and not any(is_within(path, skill_root) for skill_root in roots):
                continue
            if path.is_symlink():
                target = path.resolve(strict=False)
                external = not target.exists() or not is_within(target, root)
                code = "external-symlink" if external else "symlink-entry"
                message = "symlink target is outside the audit root or missing" if external else "source packages must not contain symlinks"
                findings.append(Finding(str(path.relative_to(root)), 1, code, message))
                continue
            try:
                mode = path.stat().st_mode
            except OSError:
                findings.append(
                    Finding(str(path.relative_to(root)), 1, "unreadable-directory", "directory metadata could not be read")
                )
                continue
            if mode & 0o555 == 0:
                findings.append(
                    Finding(str(path.relative_to(root)), 1, "unreadable-directory", "directory has no read or execute permission")
                )
                continue
            retained_dirs.append(name)
        dirnames[:] = retained_dirs

        for name in sorted(filenames):
            path = current / name
            relative = str(path.relative_to(root))
            if path.is_symlink():
                target = path.resolve(strict=False)
                external = not target.exists() or not is_within(target, root)
                code = "external-symlink" if external else "symlink-entry"
                message = "symlink target is outside the audit root or missing" if external else "source packages must not contain symlinks"
                findings.append(Finding(relative, 1, code, message))
                continue
            if path.suffix.lower() == ".pyc" and any(is_within(path, skill_root) for skill_root in roots):
                if ignore_local_generated_pyc and path.parent.name == "__pycache__":
                    continue
                findings.append(Finding(relative, 1, "bytecode-entry", "Skill packages must not contain Python bytecode"))
                continue
            operational = is_operational(path, roots)
            if not operational and not is_text_file(path):
                continue
            try:
                metadata = path.stat()
            except OSError as exc:
                findings.append(Finding(relative, 1, "unreadable-text", f"text file could not be read: {exc.strerror or exc}"))
                continue
            if not stat.S_ISREG(metadata.st_mode):
                findings.append(Finding(relative, 1, "non-regular-entry", "audited source entry is not a regular file"))
                continue
            checked_files += 1
            if metadata.st_size > MAX_TEXT_BYTES:
                findings.append(Finding(relative, 1, "oversized-text", f"text file exceeds {MAX_TEXT_BYTES} bytes"))
                continue
            try:
                with path.open("rb") as handle:
                    raw = handle.read(MAX_TEXT_BYTES + 1)
            except OSError as exc:
                findings.append(Finding(relative, 1, "unreadable-text", f"text file could not be read: {exc.strerror or exc}"))
                continue
            if len(raw) > MAX_TEXT_BYTES:
                findings.append(Finding(relative, 1, "oversized-text", f"text file exceeds {MAX_TEXT_BYTES} bytes"))
                continue
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                findings.append(Finding(relative, 1, "invalid-utf8", f"text file is not valid UTF-8 at byte {exc.start}"))
                continue

            for offset, char in enumerate(text):
                if char in HIDDEN_UNICODE:
                    findings.append(
                        Finding(relative, line_number(text, offset), "hidden-unicode-control", f"contains hidden Unicode control U+{ord(char):04X}")
                    )
                    break

            if path.name == "SKILL.md" and path.parent not in roots:
                findings.append(Finding(relative, 1, "nested-skill", "nested Skill packages are not allowed"))
            if not operational:
                continue
            for code, pattern, message in OPERATIONAL_PATTERNS:
                match = pattern.search(text)
                if match:
                    findings.append(Finding(relative, line_number(text, match.start()), code, message))
            credential = CREDENTIAL_PATTERN.search(text)
            outbound = OUTBOUND_PATTERN.search(text)
            if credential and outbound:
                findings.append(
                    Finding(
                        relative,
                        line_number(text, min(credential.start(), outbound.start())),
                        "credential-exfiltration",
                        "credential-like data and an outbound write occur in the same operational file",
                    )
                )

    return sorted(set(findings)), checked_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository or Skill root to audit")
    parser.add_argument(
        "--ignore-local-generated-pyc",
        action="store_true",
        help="ignore local __pycache__ bytecode; never use for external Skill admission",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        findings, checked_files = audit(args.root, args.ignore_local_generated_pyc)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"ERROR invalid-root {args.root}: {exc}")
        return 2
    if findings:
        for finding in findings:
            print(f"ERROR {finding.code} {finding.path}:{finding.line}: {finding.message}")
        print(f"Skill security audit failed: {len(findings)} finding(s), {checked_files} text file(s) checked.")
        return 1
    print(f"Skill security audit passed: {checked_files} text file(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
