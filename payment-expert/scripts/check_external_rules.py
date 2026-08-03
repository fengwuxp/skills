#!/usr/bin/env python3
"""Check whether a product方案记录了外部规则核验字段。

The script only inspects local text or an explicit local file. It does not
access the network, upload content, read secrets, or decide whether a rule is
actually current. It is a completeness guard before professional confirmation.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


REQUIRED_FIELDS: list[tuple[str, list[str]]] = [
    ("rule_source", ["规则来源", "source", "reference", "官方文档"]),
    ("version_or_publish_date", ["版本或发布日期", "版本", "发布日期", "生效日期", "effective date", "version"]),
    ("jurisdiction_or_scope", ["适用法域", "适用范围", "jurisdiction", "scope"]),
    ("verified_at", ["核验日期", "核验时间", "verified at", "checked at"]),
    ("confirming_party", ["专业确认方", "确认方", "confirming party"]),
]

PLACEHOLDER = re.compile(
    r"^(?:-|—|n/?a|none|null|tbd|todo|pending|待定|待补|未知|暂无|无|没有|未确认|不详)[。.]?$",
    re.IGNORECASE,
)
PLACEHOLDER_FRAGMENTS = (
    "待定",
    "待补",
    "稍后补充",
    "未知",
    "暂无",
    "未确认",
    "不详",
    "没有来源",
    "没有可核验",
    "没有版本",
    "没有适用",
    "没有核验",
    "没有确认",
    "无可核验",
    "无负责人",
    "pending",
    "tbd",
    "todo",
    "null",
    "n/a",
)
ISO_DATE = re.compile(r"^20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")

VALID_SELF_TEST = "规则来源：Nacha 官方规则；版本：2026；适用法域：US ACH；核验日期：2026-05-22；确认方：法务/合规/通道。"
INVALID_SELF_TEST = "规则来源：Nacha 官方规则。"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_fields(text: str) -> dict[str, str]:
    extracted: dict[str, str] = {}
    aliases = [
        (field, alias.lower())
        for field, field_aliases in REQUIRED_FIELDS
        for alias in field_aliases
    ]
    for raw_line in re.split(r"[\n；;]+", text):
        line = raw_line.strip().lstrip("-* ").strip()
        if not line:
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 2:
                line = f"{cells[0]}: {cells[1]}"
        match = re.match(r"^([^:：]{1,40})\s*[:：]\s*(.+?)\s*$", line)
        if not match:
            continue
        label = normalize(match.group(1))
        value = match.group(2).strip().rstrip("。.")
        for field, alias in aliases:
            if label == alias:
                extracted.setdefault(field, value)
                break
    return extracted


def is_placeholder(value: str) -> bool:
    normalized = normalize(value).strip("。.，,；; ")
    return bool(PLACEHOLDER.fullmatch(normalized)) or any(
        fragment in normalized for fragment in PLACEHOLDER_FRAGMENTS
    )


def is_valid_date(value: str) -> bool:
    if not ISO_DATE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def missing_fields(text: str) -> list[str]:
    fields = extract_fields(text)
    missing: list[str] = []
    for field, _ in REQUIRED_FIELDS:
        value = fields.get(field, "").strip()
        if not value or is_placeholder(value):
            missing.append(field)
            continue
        if field == "verified_at" and not is_valid_date(value):
            missing.append(field)
    return missing


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    return sys.stdin.read()


def run_self_test() -> int:
    valid_missing = missing_fields(VALID_SELF_TEST)
    invalid_missing = missing_fields(INVALID_SELF_TEST)
    failures: list[str] = []
    if valid_missing:
        failures.append("valid fixture missing " + ", ".join(valid_missing))
    if not invalid_missing:
        failures.append("invalid fixture unexpectedly passed")
    for label, text in [
        ("placeholder", "规则来源：待定；版本：待定；适用范围：待定；核验日期：待定；确认方：待定。"),
        ("semantic placeholder", "规则来源：没有可核验来源；版本：版本待补；适用范围：未知范围；核验日期：2026-05-22；确认方：暂无负责人。"),
        ("negated", "没有规则来源，没有版本，没有适用范围，也没有核验日期和确认方。"),
        ("invalid date", VALID_SELF_TEST.replace("2026-05-22", "昨天")),
        ("invalid calendar date", VALID_SELF_TEST.replace("2026-05-22", "2026-02-31")),
    ]:
        if not missing_fields(text):
            failures.append(f"{label} fixture unexpectedly passed")
    if failures:
        print("FAIL external rule self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK external rule self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查外部规则核验字段是否完整")
    parser.add_argument("--file", help="待检查的本地 Markdown/文本文件")
    parser.add_argument("--text", help="直接传入待检查文本")
    parser.add_argument("--self-test", action="store_true", help="运行内置正反例自测")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    text = read_input(args)
    if not text.strip():
        print("FAIL external rule check: empty input", file=sys.stderr)
        return 2

    missing = missing_fields(text)
    if missing:
        print("FAIL external rule check: missing " + ", ".join(missing), file=sys.stderr)
        return 1

    print("OK external rule check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
