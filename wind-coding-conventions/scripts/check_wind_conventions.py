#!/usr/bin/env python3
"""Offline structural guard for generic Java and high-signal Wind conventions."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {".git", ".idea", ".gradle", "target", "build", "node_modules", "__pycache__"}
TEST_OR_DEMO_PARTS = {"test", "tests", "fixture", "fixtures", "demo", "sandbox"}
TEST_ANNOTATION = re.compile(
    r"@(?:org\.junit(?:\.jupiter\.(?:api|params))?\.)?"
    r"(?:Test|ParameterizedTest|RepeatedTest|TestFactory|TestTemplate)\b"
)
METHOD_DECLARATION = re.compile(
    r"\b(?:public\s+|protected\s+|private\s+)?(?:static\s+)?(?:final\s+)?"
    r"[\w<>,.?@\[\]]+\s+(?P<name>\w+)\s*\("
)
TEST_METHOD_NAME = re.compile(r"test[A-Z0-9]\w*")


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


def is_test_path(path: Path) -> bool:
    return bool({part.lower() for part in path.parts}.intersection({"test", "tests"}))


def java_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.java"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def stripped(line: str) -> str:
    return line.strip()


def check_test_method_names(path: Path, root: Path, text: str) -> list[Finding]:
    if not is_test_path(path.relative_to(root)):
        return []

    findings: list[Finding] = []
    annotation_line: int | None = None
    signature: list[str] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        line = stripped(raw)
        annotation = TEST_ANNOTATION.search(line)
        if annotation:
            annotation_line = idx
            signature = []
            line = line[annotation.end() :].strip()
            if not line:
                continue
        if annotation_line is None or not line or line.startswith("@"):
            continue

        signature.append(line)
        declaration = METHOD_DECLARATION.search(" ".join(signature))
        if declaration:
            method_name = declaration.group("name")
            if not TEST_METHOD_NAME.fullmatch(method_name):
                findings.append(
                    Finding(
                        "ERROR",
                        path.relative_to(root),
                        idx,
                        "测试方法必须使用 testXxx 格式",
                    )
                )
            annotation_line = None
            signature = []
        elif "{" in line or ";" in line:
            annotation_line = None
            signature = []

    return findings


def check_file(path: Path, root: Path, profile: str = "wind") -> list[Finding]:
    findings: list[Finding] = []
    rel = path.relative_to(root)
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings.extend(check_test_method_names(path, root, text))

    if profile == "java":
        return findings

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


def run(root: Path, profile: str = "wind") -> list[Finding]:
    if not root.exists():
        raise SystemExit(f"root not found: {root}")
    findings: list[Finding] = []
    for path in java_files(root):
        findings.extend(check_file(path, root, profile))
    return findings


def print_findings(findings: list[Finding]) -> None:
    for item in findings:
        print(f"{item.severity} {item.path}:{item.line_no}: {item.message}")
    errors = sum(1 for item in findings if item.severity == "ERROR")
    warnings = sum(1 for item in findings if item.severity == "WARN")
    print(f"Wind convention guard: {errors} error(s), {warnings} warning(s)")


def self_test() -> None:
    fixture_root = Path(__file__).resolve().parents[1] / "fixtures"

    valid = run(fixture_root / "valid", profile="java")
    if valid:
        print_findings(valid)
        raise SystemExit("valid generic Java fixture should pass")

    invalid_java = run(fixture_root / "invalid", profile="java")
    invalid_test_names = [item for item in invalid_java if "testXxx" in item.message]
    if len(invalid_test_names) != 3:
        print_findings(invalid_java)
        raise SystemExit(
            f"invalid generic Java fixture expected 3 testXxx findings, got {len(invalid_test_names)}"
        )

    valid = run(fixture_root / "valid", profile="wind")
    if valid:
        print_findings(valid)
        raise SystemExit("valid Wind fixture should pass")

    invalid = run(fixture_root / "invalid", profile="wind")
    messages = "\n".join(item.message for item in invalid)
    expected = [
        "不得使用 String",
        "不得暴露 Entity",
        "不得新增内存版",
        "getXxxById / findXxxById",
        "selective",
        "测试方法必须使用 testXxx",
    ]
    missing = [item for item in expected if item not in messages]
    if missing:
        print_findings(invalid)
        raise SystemExit("invalid fixture missing: " + ", ".join(missing))
    print("OK wind convention guard self-test")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Java project root to scan")
    parser.add_argument(
        "--profile",
        choices=("java", "wind"),
        default="wind",
        help="scan generic Java rules only, or generic Java plus Wind rules",
    )
    parser.add_argument("--self-test", action="store_true", help="run embedded positive and negative fixtures")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    findings = run(args.root.resolve(), profile=args.profile)
    print_findings(findings)
    return 1 if any(item.severity == "ERROR" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
