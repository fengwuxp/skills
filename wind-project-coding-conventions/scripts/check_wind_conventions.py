#!/usr/bin/env python3
"""Offline structural guard for high-signal Wind project coding conventions."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {".git", ".idea", ".gradle", "target", "build", "node_modules", "__pycache__"}
TEST_OR_DEMO_PARTS = {"test", "tests", "fixture", "fixtures", "demo", "sandbox"}


@dataclass(frozen=True)
class Finding:
    severity: str
    path: Path
    line_no: int
    message: str


def is_face_path(path: Path) -> bool:
    text = path.as_posix()
    return "-face/" in text or "/face/" in text or any(part.endswith("-face") for part in path.parts)


def is_prod_path(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    return not lowered.intersection(TEST_OR_DEMO_PARTS)


def java_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.java"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def stripped(line: str) -> str:
    return line.strip()


def check_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.relative_to(root)
    text = path.read_text(encoding="utf-8", errors="ignore")

    for idx, raw in enumerate(text.splitlines(), start=1):
        line = stripped(raw)
        if not line or line.startswith("//") or line.startswith("*"):
            continue

        if re.search(r"\bprivate\s+String\s+(currency|currencyCode|currencyIsoCode)\b", line):
            findings.append(Finding("ERROR", rel, idx, "币种字段不得使用 String，统一使用 CurrencyIsoCode"))

        if is_face_path(rel):
            leaks_import = re.search(r"^import\s+.*\.(dal\.entities|dal\.mapper|repository)\.", line)
            leaks_signature = re.search(r"\b\w*Entity\b|\b\w*Mapper\b|\b\w*Repository\b|\bPage\s*[<,)]", line)
            if leaks_import or ("(" in line and ")" in line and leaks_signature):
                findings.append(Finding("ERROR", rel, idx, "face 对外契约不得暴露 Entity、Mapper、Repository 或 MyBatis Page"))

        if path.name.endswith("Service.java") and re.search(r"\bquery[A-Z]\w*ById\s*\(", line):
            findings.append(Finding("WARN", rel, idx, "新服务 ID 查询优先使用 getXxxById / findXxxById 表达存在性"))

        if path.name.endswith("ServiceImpl.java") and re.search(r"\b\w+Mapper\.update\s*\(", line):
            findings.append(Finding("WARN", rel, idx, "写库默认使用 selective；需要全量 update 时说明业务语义"))

    if is_prod_path(rel) and re.search(r"\b(class|interface)\s+(InMemory|Fake|Mock)\w*Service\b", text):
        findings.append(Finding("ERROR", rel, 1, "生产源码路径不得新增内存版 / Fake / Mock 业务 Service"))

    return findings


def run(root: Path) -> list[Finding]:
    if not root.exists():
        raise SystemExit(f"root not found: {root}")
    findings: list[Finding] = []
    for path in java_files(root):
        findings.extend(check_file(path, root))
    return findings


def print_findings(findings: list[Finding]) -> None:
    for item in findings:
        print(f"{item.severity} {item.path}:{item.line_no}: {item.message}")
    errors = sum(1 for item in findings if item.severity == "ERROR")
    warnings = sum(1 for item in findings if item.severity == "WARN")
    print(f"Wind convention guard: {errors} error(s), {warnings} warning(s)")


def self_test() -> None:
    fixture_root = Path(__file__).resolve().parents[1] / "fixtures"

    valid = run(fixture_root / "valid")
    if valid:
        print_findings(valid)
        raise SystemExit("valid fixture should pass")

    invalid = run(fixture_root / "invalid")
    messages = "\n".join(item.message for item in invalid)
    expected = ["不得使用 String", "不得暴露 Entity", "不得新增内存版"]
    missing = [item for item in expected if item not in messages]
    if missing:
        print_findings(invalid)
        raise SystemExit("invalid fixture missing: " + ", ".join(missing))
    print("OK wind convention guard self-test")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Wind project root to scan")
    parser.add_argument("--self-test", action="store_true", help="run embedded positive and negative fixtures")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    findings = run(args.root.resolve())
    print_findings(findings)
    return 1 if any(item.severity == "ERROR" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
