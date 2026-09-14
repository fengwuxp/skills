#!/usr/bin/env python3
"""Validate product qualification and local PRD concept definitions.

Input: explicit UTF-8 text/file or stdin. Output: deterministic structural
errors only. The checker does not access the network, write files, or decide
whether a business classification is semantically correct.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


QUALIFICATION_OBJECTS = {
    "产品",
    "商业供给",
    "产品能力",
    "业务主体",
    "业务对象",
    "业务流程",
    "业务规则",
    "业务状态",
    "业务指标",
    "交互载体",
    "协议",
    "技术机制",
}
CHANGE_TYPES = {"新建", "增强", "治理", "风险约束", "运营提效", "迁移", "退役", "验证"}
DOCUMENT_STRENGTHS = {"轻量", "标准", "增强"}
EMPTY_VALUES = {"", "-", "无", "暂无", "待定", "待确认", "n/a", "na", "null", "none"}
PLACEHOLDER = re.compile(r"〈[^〉\n]+〉")


def normalize(value: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value.casefold())


def labeled_values(text: str, label: str) -> list[str]:
    pattern = re.compile(
        rf"(?m)^\s*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*|__|`)?\s*{re.escape(label)}\s*"
        rf"(?:\*\*|__|`)?\s*[：:]\s*([^；;。\n|]+)",
        re.IGNORECASE,
    )
    return [match.group(1).strip().strip("`*_").strip() for match in pattern.finditer(text)]


def labeled_value(text: str, label: str) -> str | None:
    values = labeled_values(text, label)
    return values[0] if values else None


def has_conflicting_values(text: str, label: str) -> bool:
    values = {normalize(value) for value in labeled_values(text, label) if meaningful(value)}
    return len(values) > 1


def meaningful(value: str | None) -> bool:
    return bool(
        value
        and normalize(value) not in {normalize(item) for item in EMPTY_VALUES}
        and PLACEHOLDER.search(value) is None
    )


def qualification_issues(text: str) -> list[str]:
    issues: list[str] = []
    qualification_object = labeled_value(text, "定性对象")
    if has_conflicting_values(text, "定性对象"):
        issues.append("qualification_object_conflict")
    elif not meaningful(qualification_object):
        issues.append("qualification_object_missing")
    elif qualification_object not in QUALIFICATION_OBJECTS:
        issues.append("qualification_object_invalid")

    change_type = labeled_value(text, "本期变化")
    if has_conflicting_values(text, "本期变化"):
        issues.append("change_type_conflict")
    elif not meaningful(change_type):
        issues.append("change_type_missing")
    elif change_type not in CHANGE_TYPES:
        issues.append("change_type_invalid")

    if not meaningful(labeled_value(text, "责任边界")):
        issues.append("responsibility_boundary_missing")

    strength = labeled_value(text, "文档强度")
    if has_conflicting_values(text, "文档强度"):
        issues.append("document_strength_conflict")
    elif not meaningful(strength):
        issues.append("document_strength_missing")
    elif strength not in DOCUMENT_STRENGTHS:
        issues.append("document_strength_invalid")

    rationale = re.search(
        r"(?m)^\s*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*|__|`)?\s*文档强度\s*"
        r"(?:\*\*|__|`)?\s*[：:].*?[；;]\s*依据\s*[：:]\s*(\S.+?)\s*$",
        text,
    )
    if rationale is None or not meaningful(rationale.group(1)):
        issues.append("document_strength_rationale_missing")
    return issues


def concept_section(text: str) -> str | None:
    headings = list(re.finditer(r"(?m)^(#{2,6})\s+(.+?)\s*$", text))
    for index, heading in enumerate(headings):
        if "核心概念与业务口径" not in heading.group(2):
            continue
        level = len(heading.group(1))
        end = len(text)
        for following in headings[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        return text[heading.end() : end]
    return None


def table_records(section: str) -> list[dict[str, str]] | None:
    lines = section.splitlines()
    records: list[dict[str, str]] = []
    required = {
        "concept": lambda header: header == "概念",
        "type": lambda header: header == "类型",
        "definition": lambda header: header in {"统一定义", "本prd中的定义"},
        "boundary": lambda header: header == "边界不等于",
    }
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        if index and lines[index - 1].strip().startswith("|"):
            continue
        headers = [cell.strip().strip("`*_").strip() for cell in line.strip().strip("|").split("|")]
        normalized_headers = [normalize(header) for header in headers]
        positions = {
            name: next((pos for pos, header in enumerate(normalized_headers) if matches(header)), None)
            for name, matches in required.items()
        }
        if any(position is None for position in positions.values()):
            return None
        for row in lines[index + 1 :]:
            if not row.strip().startswith("|"):
                break
            cells = [cell.strip().strip("`*_").strip() for cell in row.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            records.append(
                {
                    name: cells[position] if position is not None and position < len(cells) else ""
                    for name, position in positions.items()
                }
            )
    return records or None


def concept_paragraph_records(section: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    pattern = r"(?m)^\*\*([^*\n]+)\*\*[：:]([^\n]*(?:\n(?!\s*$|\*\*|#|\|)[^\n]+)*)"
    for match in re.finditer(pattern, section):
        sentences = re.split(r"[。\n]", match.group(2).strip(), maxsplit=1)
        definition = sentences[0].strip()
        boundary = sentences[1].strip() if len(sentences) > 1 else ""
        definition_shape = re.search(
            r"^(?:一[项组类种份套条个].+|供.+的.+|同一.+(?:的|在).+|当前.+(?:的|版本)|"
            r"由.+的|对.+设置|记录.+(?:主体|对象|结果)|先保存.+再|.+适用于|(?:是|指).+|"
            r"将.+转换为.+的.+|在.+下的一份.+|面向.+的.+|.+下的一次.+|"
            r"目标.+形成的.+|引导.+的.+|.+为.+签发.+的.+)",
            definition,
        )
        boundary_shape = re.search(
            r"只|不等于|不属于|不得|不能|不授予|仍由|适用|范围|负责人|稳定值|业务规则|独立|历史|不改变",
            boundary,
        )
        records.append({
            "concept": match.group(1).strip(),
            "definition": definition if definition_shape else "",
            "boundary": boundary if boundary_shape else "",
        })
    return records


def concept_issues(text: str) -> list[str]:
    section = concept_section(text)
    if section is None:
        return []
    table_rows = table_records(section)
    records = (table_rows or []) + concept_paragraph_records(section)
    if not records:
        return ["concept_definition_table_incomplete"] if re.search(r"(?m)^\s*\|", section) else [
            "concept_expression_manual_review_required"
        ]
    issues: list[str] = []
    if re.search(r"(?m)^\s*\|", section) and not table_rows:
        issues.append("concept_definition_table_incomplete")
    seen: set[str] = set()
    for record in records:
        if not meaningful(record["concept"]):
            issues.append("concept_name_missing")
        elif normalize(record["concept"]) in seen:
            issues.append("concept_name_duplicate")
        else:
            seen.add(normalize(record["concept"]))
        if "type" in record and record["type"] not in QUALIFICATION_OBJECTS:
            issues.append("concept_type_invalid")
        if not meaningful(record["definition"]):
            issues.append("concept_definition_missing")
        if not meaningful(record["boundary"]):
            issues.append("concept_boundary_missing")
    return issues


def check(text: str) -> list[str]:
    return list(dict.fromkeys(qualification_issues(text) + concept_issues(text)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--file")
    source.add_argument("--text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()
    issues = check(text)
    if issues:
        print("FAIL product qualification")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("OK product qualification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
