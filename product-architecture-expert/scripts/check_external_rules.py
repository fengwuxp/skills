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
from pathlib import Path


REQUIRED_FIELDS: list[tuple[str, list[str]]] = [
    ("rule_source", ["规则来源", "来源", "source", "reference", "官方文档"]),
    ("version_or_publish_date", ["版本", "发布日期", "发布日", "生效日期", "effective date", "version"]),
    ("jurisdiction_or_scope", ["适用法域", "适用范围", "地区", "jurisdiction", "scope"]),
    ("verified_at", ["核验日期", "核验时间", "verified at", "checked at"]),
    ("confirming_party", ["确认方", "待确认方", "专业确认方", "法务", "合规", "通道", "持牌机构"]),
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def missing_fields(text: str) -> list[str]:
    normalized = normalize(text)
    missing: list[str] = []
    for field, aliases in REQUIRED_FIELDS:
        if not any(alias.lower() in normalized for alias in aliases):
            missing.append(field)
    return missing


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="检查外部规则核验字段是否完整")
    parser.add_argument("--file", help="待检查的本地 Markdown/文本文件")
    parser.add_argument("--text", help="直接传入待检查文本")
    args = parser.parse_args()

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
