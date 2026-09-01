#!/usr/bin/env python3
"""Select bounded local Markdown sections and print a JSON reading package.

Input is one explicitly supplied Markdown file or a non-recursive directory.
The script is offline and read-only. It exits non-zero when selection is
missing or ambiguous, and never treats retrieval as factual or authorization
evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SAFETY_HEADINGS = ("使用时机", "不适用场景", "读取后必须产出")
TASK_INDEX_HEADING = "按任务读取索引"
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
BACKTICK_RE = re.compile(r"`([^`]+)`")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
PRIMARY_TASK_SCORE = 0.45
FALLBACK_TASK_SCORE = 0.3
FALLBACK_TASK_MIN_OVERLAP = 2


@dataclass(frozen=True)
class Section:
    title: str
    level: int
    start: int
    end: int
    parent: str | None

    @property
    def heading_path(self) -> list[str]:
        return [self.parent, self.title] if self.parent else [self.title]


def normalize(value: str) -> str:
    return re.sub(r"[^0-9a-z\u3400-\u9fff]+", "", value.casefold())


def title_key(value: str) -> str:
    return re.sub(r"^(?:[一二三四五六七八九十]+|\d+(?:[A-Z])?(?:\.\d+)*)[、.．]?", "", normalize(value))


def estimate_tokens(text: str) -> dict[str, int]:
    cjk = len(CJK_RE.findall(text))
    ascii_count = sum(ord(char) < 128 for char in text)
    other = len(text) - cjk - ascii_count
    low = round(cjk * 0.5 + ascii_count / 4.5 + other * 0.5)
    high = round(cjk + ascii_count / 2.5 + other)
    return {"low": low, "high": high, "midpoint": round((low + high) / 2)}


def read_regular_bytes(path: Path) -> bytes:
    if path.is_symlink():
        raise ValueError(f"symbolic links are not accepted: {path}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError(f"reference is not a regular file: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(descriptor)


def parse_sections(lines: list[str]) -> list[Section]:
    headings: list[tuple[int, int, str, str | None]] = []
    parent: str | None = None
    fence: str | None = None
    for index, line in enumerate(lines):
        if fence is not None:
            if re.fullmatch(
                rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*",
                line,
            ):
                fence = None
            continue
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            info = line[fence_match.end() :]
            if marker[0] == "~" or "`" not in info:
                fence = marker
                continue
        match = None if fence else HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        if level == 2:
            parent = None
            headings.append((index, level, title, None))
            parent = title
        else:
            headings.append((index, level, title, parent))

    sections: list[Section] = []
    for position, (start, level, title, section_parent) in enumerate(headings):
        end = len(lines)
        for next_start, next_level, _, _ in headings[position + 1 :]:
            if next_level <= level:
                end = next_start
                break
        sections.append(Section(title, level, start, end, section_parent))
    return sections


def section_text(lines: list[str], section: Section) -> str:
    text = "\n".join(lines[section.start : section.end]).rstrip()
    if section.parent:
        return f"## {section.parent}\n\n{text}"
    return text


def find_section(sections: list[Section], requested: str) -> Section | None:
    requested_number = requested.strip().rstrip("、.．")
    if re.fullmatch(r"\d+(?:\.\d+)*(?:[A-Za-z])?", requested_number):
        numbered = [
            section
            for section in sections
            if re.match(
                rf"^{re.escape(requested_number)}(?:[\s、.．:：]|$)",
                section.title,
                re.IGNORECASE,
            )
        ]
        if len(numbered) == 1:
            return numbered[0]
    requested_normalized = normalize(requested)
    requested_key = title_key(requested)
    exact = [section for section in sections if normalize(section.title) == requested_normalized]
    if len(exact) == 1:
        return exact[0]
    keyed = [section for section in sections if title_key(section.title) == requested_key]
    if len(keyed) == 1 and requested_key:
        return keyed[0]
    prefix = [
        section
        for section in sections
        if requested_normalized
        and normalize(section.title).startswith(requested_normalized)
    ]
    if len(prefix) == 1:
        return prefix[0]
    contained = [
        section
        for section in sections
        if len(requested_normalized) >= 4
        and requested_normalized in normalize(section.title)
    ]
    return contained[0] if len(contained) == 1 else None


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def task_rows(lines: list[str], sections: list[Section]) -> tuple[list[str], list[dict[str, Any]]]:
    index_section = find_section(sections, TASK_INDEX_HEADING)
    if not index_section:
        return [], []
    table_lines = lines[index_section.start + 1 : index_section.end]
    header: list[str] = []
    rows: list[dict[str, Any]] = []
    for line in table_lines:
        if not line.lstrip().startswith("|"):
            continue
        cells = split_table_row(line)
        if not header:
            header = cells
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if len(cells) != len(header):
            continue
        row = dict(zip(header, cells))
        task = row.get("任务", "")
        preferred = row.get("优先读取", row.get("按需展开", ""))
        skipped = row.get("跳过", "")
        if task and preferred:
            rows.append(
                {
                    "task": task,
                    "preferred": preferred,
                    "headings": BACKTICK_RE.findall(preferred),
                    "skipped": skipped,
                    "raw": line.rstrip(),
                }
            )
    return header, rows


def character_terms(value: str) -> set[str]:
    normalized = normalize(value)
    cjk = "".join(CJK_RE.findall(normalized))
    terms = {cjk[index : index + 2] for index in range(max(0, len(cjk) - 1))}
    terms.update(re.findall(r"[a-z0-9]{2,}", normalized))
    return {term for term in terms if term}


def task_score(query: str, task: str) -> float:
    query_normalized = normalize(query)
    task_normalized = normalize(task)
    if not query_normalized or not task_normalized:
        return 0.0
    if query_normalized == task_normalized:
        return 1.0
    if task_normalized in query_normalized or query_normalized in task_normalized:
        return 0.9
    query_terms = character_terms(query)
    task_terms = character_terms(task)
    if not query_terms or not task_terms:
        return 0.0
    return len(query_terms & task_terms) / len(task_terms)


def task_overlap_count(query: str, task: str) -> int:
    return len(character_terms(query) & character_terms(task))


def match_task(query: str, rows: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    ranked = sorted(
        ({**row, "score": round(task_score(query, row["task"]), 3)} for row in rows),
        key=lambda row: (-row["score"], row["task"]),
    )
    candidates = [
        row
        for row in ranked
        if row["score"] >= PRIMARY_TASK_SCORE
        or (
            row["score"] >= FALLBACK_TASK_SCORE
            and task_overlap_count(query, row["task"]) >= FALLBACK_TASK_MIN_OVERLAP
        )
    ][:3]
    if not candidates:
        return None, []
    if len(candidates) > 1 and candidates[0]["score"] == candidates[1]["score"]:
        return None, candidates
    return candidates[0], candidates


def required_context(lines: list[str], sections: list[Section]) -> list[str]:
    first_section_start = min((section.start for section in sections), default=len(lines))
    parts = ["\n".join(lines[:first_section_start]).rstrip()]
    for title in SAFETY_HEADINGS:
        section = find_section(sections, title)
        if section:
            parts.append(section_text(lines, section))
    return [part for part in parts if part]


def entry_matches(
    path: Path,
    lines: list[str],
    sections: list[Section],
    query: str,
) -> list[tuple[Section, int, int]]:
    if path.name != "source-map.md":
        return []
    query_normalized = normalize(query)
    matches: list[tuple[Section, int, int]] = []
    for section in sections:
        entry_collection = any(
            marker in section.title
            for marker in ("公开来源", "一手来源", "参考来源", "外部来源状态")
        )
        if section.level != 2 or not entry_collection:
            continue
        index = section.start + 1
        while index < section.end:
            line = lines[index]
            if line.startswith("- "):
                start = index
                index += 1
                while index < section.end and (lines[index].startswith("  ") or not lines[index].strip()):
                    index += 1
                text = "\n".join(lines[start:index])
                if query_normalized and query_normalized in normalize(text):
                    matches.append((section, start, index))
                continue
            index += 1
    return matches


def prune_nested_sections(sections: list[Section]) -> list[Section]:
    selected: list[Section] = []
    for section in sorted(sections, key=lambda item: (item.start, item.level)):
        if any(parent.start <= section.start < parent.end for parent in selected):
            continue
        selected.append(section)
    return selected


def build_package(
    path: Path,
    query: str,
    *,
    headings: list[str] | None = None,
    max_sections: int = 3,
    entry_threshold_tokens: int = 4000,
    min_savings_ratio: float = 0.3,
) -> dict[str, Any]:
    raw = read_regular_bytes(path)
    text = raw.decode("utf-8")
    lines = text.splitlines()
    sections = parse_sections(lines)
    header, rows = task_rows(lines, sections)
    selected_sections: list[Section] = []
    matched_task: str | None = None
    skipped = ""
    task_row: dict[str, Any] | None = None
    candidates: list[dict[str, Any]] = []
    followups: list[str] = []
    missing_explicit_headings: list[str] = []

    requested_headings = headings or []
    if requested_headings:
        for requested in requested_headings:
            section = find_section(sections, requested)
            if section:
                selected_sections.append(section)
            else:
                missing_explicit_headings.append(requested)
    else:
        task_row, candidates = match_task(query, rows)
        if task_row:
            matched_task = task_row["task"]
            skipped = task_row["skipped"]
            for requested in task_row["headings"]:
                if requested.lower().endswith(".md"):
                    followups.append(requested)
                    continue
                section = find_section(sections, requested)
                if section and section not in selected_sections:
                    selected_sections.append(section)
                elif not section:
                    followups.append(requested)
        else:
            section = find_section(sections, query)
            if section:
                selected_sections.append(section)

    selected_sections = prune_nested_sections(selected_sections)
    too_many_sections = len(selected_sections) > max_sections

    selections: list[dict[str, Any]] = []
    content_parts = required_context(lines, sections)
    if task_row and header:
        content_parts.append(
            "\n".join(
                [
                    "## 按任务读取索引（命中行）",
                    "",
                    "| " + " | ".join(header) + " |",
                    "| " + " | ".join("---" for _ in header) + " |",
                    task_row["raw"],
                ]
            )
        )

    for section in ([] if too_many_sections or missing_explicit_headings else selected_sections):
        content_parts.append(section_text(lines, section))
        selections.append(
            {
                "kind": "section",
                "heading_path": section.heading_path,
                "start_line": section.start + 1,
                "end_line": section.end,
            }
        )

    matching_entries = entry_matches(path, lines, sections, query)
    if not selections:
        if len(matching_entries) == 1:
            section, start, end = matching_entries[0]
            full_section = section_text(lines, section)
            if estimate_tokens(full_section)["midpoint"] >= entry_threshold_tokens:
                content_parts.append(f"## {section.title}\n\n" + "\n".join(lines[start:end]).rstrip())
                selections.append(
                    {
                        "kind": "entry",
                        "heading_path": section.heading_path,
                        "start_line": start + 1,
                        "end_line": end,
                    }
                )

    content = "\n\n".join(dict.fromkeys(part for part in content_parts if part)).rstrip() + "\n"
    full_estimate = estimate_tokens(text)
    if too_many_sections or followups or len(matching_entries) > 1:
        status = "ambiguous"
    elif missing_explicit_headings:
        status = "not-found"
    else:
        status = "ready" if selections else ("ambiguous" if candidates else "not-found")
    if status != "ready":
        content = ""

    candidate_output = (
        [
            {"task": candidate["task"], "score": candidate["score"]}
            for candidate in candidates
        ]
        + [
            {
                "entry_heading": section.title,
                "start_line": start + 1,
                "end_line": end,
            }
            for section, start, end in matching_entries[:5]
        ]
        + [
            {"heading_path": section.heading_path}
            for section in selected_sections[:5]
            if too_many_sections
        ]
    )

    def result_for(package_content: str, package_selections: list[dict[str, Any]]) -> dict[str, Any]:
        result = {
            "status": status,
            "source": str(path),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "query": query,
            "matched_task": matched_task,
            "skipped": skipped,
            "followups": followups,
            "missing_headings": missing_explicit_headings,
            "selections": package_selections,
            "candidates": candidate_output,
            "estimated_full_tokens": full_estimate["midpoint"],
            "estimated_selected_tokens": 0,
            "estimated_selected_content_tokens": estimate_tokens(package_content)["midpoint"],
            "estimated_full_tokens_range": [full_estimate["low"], full_estimate["high"]],
            "estimated_selected_tokens_range": [0, 0],
            "estimated_savings_ratio": 0.0,
            "token_estimate_method": "final JSON package mixed-text heuristic; not model billing telemetry",
            "content": package_content,
        }
        for _ in range(2):
            selected = estimate_tokens(json.dumps(result, ensure_ascii=False, indent=2))
            result["estimated_selected_tokens"] = selected["midpoint"]
            result["estimated_selected_tokens_range"] = [selected["low"], selected["high"]]
            if status == "ready" and full_estimate["midpoint"]:
                result["estimated_savings_ratio"] = round(
                    max(0.0, 1 - selected["midpoint"] / full_estimate["midpoint"]),
                    4,
                )
        return result

    result = result_for(content, selections)
    if status == "ready" and re.search(r"(?:资金|支付|安全|权限|Git|生产|部署|密钥|删除|不可逆)", query, re.IGNORECASE):
        content = text if text.endswith("\n") else text + "\n"
        selections = [
            {
                "kind": "file",
                "heading_path": [],
                "start_line": 1,
                "end_line": len(lines),
            }
        ]
        result = result_for(content, selections)
        result["estimated_savings_ratio"] = 0.0
        result["forced_full_reason"] = "high-risk-query"
        return result
    if status == "ready" and result["estimated_savings_ratio"] < min_savings_ratio:
        content = text if text.endswith("\n") else text + "\n"
        selections = [
            {
                "kind": "file",
                "heading_path": [],
                "start_line": 1,
                "end_line": len(lines),
            }
        ]
        result = result_for(content, selections)
        result["estimated_savings_ratio"] = 0.0
    return result


def build_from_path(
    path: Path,
    query: str,
    *,
    headings: list[str] | None = None,
    max_sections: int = 3,
    min_savings_ratio: float = 0.3,
) -> dict[str, Any]:
    if path.is_symlink():
        return {
            "status": "not-found",
            "source": str(path),
            "query": query,
            "candidates": [],
        }
    if path.is_file():
        return build_package(
            path,
            query,
            headings=headings,
            max_sections=max_sections,
            min_savings_ratio=min_savings_ratio,
        )
    if not path.is_dir():
        return {
            "status": "not-found",
            "source": str(path),
            "query": query,
            "candidates": [],
        }

    references = sorted(
        reference
        for reference in path.glob("*.md")
        if reference.is_file() and not reference.is_symlink()
    )
    if headings:
        heading_candidates: list[Path] = []
        for reference in references:
            lines = read_regular_bytes(reference).decode("utf-8").splitlines()
            sections = parse_sections(lines)
            if all(find_section(sections, heading) for heading in headings):
                heading_candidates.append(reference)
        if len(heading_candidates) == 1:
            return build_package(
                heading_candidates[0],
                query,
                headings=headings,
                max_sections=max_sections,
                min_savings_ratio=min_savings_ratio,
            )
        return {
            "status": "ambiguous" if heading_candidates else "not-found",
            "source": str(path),
            "query": query,
            "candidates": [str(reference) for reference in heading_candidates],
        }

    candidates: list[dict[str, Any]] = []
    for reference in references:
        lines = read_regular_bytes(reference).decode("utf-8").splitlines()
        _, rows = task_rows(lines, parse_sections(lines))
        task, _ = match_task(query, rows)
        if task:
            candidates.append(
                {
                    "path": reference,
                    "task": task["task"],
                    "score": task["score"],
                }
            )
    candidates.sort(key=lambda item: (-item["score"], str(item["path"])))
    if not candidates:
        return {
            "status": "not-found",
            "source": str(path),
            "query": query,
            "candidates": [],
        }
    top_score = candidates[0]["score"]
    tied = [candidate for candidate in candidates if candidate["score"] == top_score]
    if len(tied) != 1:
        return {
            "status": "ambiguous",
            "source": str(path),
            "query": query,
            "candidates": [
                {
                    "source": str(candidate["path"]),
                    "task": candidate["task"],
                    "score": candidate["score"],
                }
                for candidate in candidates[:5]
            ],
        }
    return build_package(
        tied[0]["path"],
        query,
        headings=headings,
        max_sections=max_sections,
        min_savings_ratio=min_savings_ratio,
    )


def run_self_test() -> None:
    markdown = """# Reference

Authority preamble.

## 使用时机

Use for controlled loops.

## 不适用场景

Do not use for one-step work.

## 读取后必须产出

Return a bounded decision.

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 控制成本与停止 | `6. 预算和停止条件` | 不允许无限循环 |

## 6. 预算和停止条件

Stop when the budget is exhausted.

### 6.1 无进展

Stop after two rounds without evidence.

## 7. 生产准出

Production rules that must not be loaded for this task.
""" + "\n".join(
        f"Unrelated production detail {index}: do not load for budget control."
        for index in range(40)
    ) + """
"""
    source_map = """# Sources

Source authority.

## 已参考的公开来源

- GitHub [Matt Pocock](https://example.com/matt): section-level loading.
- GitHub [Unrelated](https://example.com/other): unrelated material.

## 提炼边界

Do not copy source text.
"""
    release = """# Release

Release authority.

## 使用时机

Use before a release.

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 发布前门禁 | `7. 发布门禁` | 不展开复盘 |

## 7. 发布门禁

Verify version, configuration, rollback, and observation.
"""
    with tempfile.TemporaryDirectory() as temp_dir:
        reference = Path(temp_dir) / "reference.md"
        reference.write_text(markdown, encoding="utf-8")
        result = build_package(reference, "控制成本与停止")
        assert result["status"] == "ready"
        assert result["matched_task"] == "控制成本与停止"
        assert result["source_sha256"]
        assert result["estimated_selected_tokens"] < result["estimated_full_tokens"]
        assert result["estimated_savings_ratio"] > 0.4
        excerpt = result["content"]
        assert "Authority preamble." in excerpt
        assert "## 使用时机" in excerpt
        assert "## 不适用场景" in excerpt
        assert "## 读取后必须产出" in excerpt
        assert "不允许无限循环" in excerpt
        assert "## 6. 预算和停止条件" in excerpt
        assert "### 6.1 无进展" in excerpt
        assert "## 7. 生产准出" not in excerpt
        selected = result["selections"][0]
        assert selected["heading_path"] == ["6. 预算和停止条件"]
        assert selected["start_line"] < selected["end_line"]

        release_reference = Path(temp_dir) / "release.md"
        release_reference.write_text(release, encoding="utf-8")
        directory_result = build_from_path(Path(temp_dir), "发布前门禁")
        assert directory_result["status"] == "ready"
        assert directory_result["source"].endswith("release.md")
        assert directory_result["matched_task"] == "发布前门禁"

        shifted = "Extra preamble line.\n\n" + markdown
        reference.write_text(shifted, encoding="utf-8")
        shifted_result = build_package(reference, "控制成本与停止")
        assert shifted_result["status"] == "ready"
        assert shifted_result["selections"][0]["heading_path"] == ["6. 预算和停止条件"]
        assert shifted_result["selections"][0]["start_line"] == selected["start_line"] + 2

        source = Path(temp_dir) / "source-map.md"
        source.write_text(source_map, encoding="utf-8")
        source_result = build_package(
            source,
            "Matt Pocock",
            entry_threshold_tokens=1,
            min_savings_ratio=0,
        )
        assert source_result["status"] == "ready"
        assert source_result["selections"][0]["kind"] == "entry"
        assert "Matt Pocock" in source_result["content"]
        assert "Unrelated" not in source_result["content"]

        ambiguous_source = build_package(
            source,
            "GitHub",
            entry_threshold_tokens=1,
            min_savings_ratio=0,
        )
        assert ambiguous_source["status"] == "ambiguous"
        assert not ambiguous_source["content"]

        cross_file = release.replace(
            "| 发布前门禁 | `7. 发布门禁` | 不展开复盘 |",
            "| 发布前门禁 | `7. 发布门禁`、`other.md` | 不展开复盘 |",
        )
        release_reference.write_text(cross_file, encoding="utf-8")
        cross_file_result = build_package(release_reference, "发布前门禁")
        assert cross_file_result["status"] == "ambiguous"
        assert cross_file_result["followups"] == ["other.md"]
        assert not cross_file_result["content"]

        policy_dir = Path(temp_dir) / "policy-map"
        policy_dir.mkdir()
        policy = policy_dir / "source-map.md"
        policy.write_text(
            "# Policy\n\n## 删除控制\n\n"
            "- 删除账本数据前必须有 Owner 授权、备份和回滚。\n"
            "- special-delete 需要先 dry-run。\n"
            + "\n".join(f"- 其他约束 {index}。" for index in range(500)),
            encoding="utf-8",
        )
        policy_result = build_package(
            policy,
            "special-delete",
            min_savings_ratio=0,
        )
        assert policy_result["status"] != "ready"

        fenced = Path(temp_dir) / "fenced.md"
        fenced.write_text(
            "# Reference\n\n## 按任务读取索引\n\n"
            "| 任务 | 优先读取 | 跳过 |\n"
            "| --- | --- | --- |\n"
            "| 安全核验 | `伪造门禁` | 不跳过 |\n\n"
            "~~~markdown\n## 伪造门禁\n危险内容\n~~~\n\n"
            "## 真门禁\n安全内容\n"
            + "无关内容。\n" * 80,
            encoding="utf-8",
        )
        fenced_result = build_package(fenced, "安全核验", min_savings_ratio=0)
        assert fenced_result["status"] != "ready"
        assert "危险内容" not in fenced_result["content"]

        reference_dir = Path(temp_dir) / "references"
        reference_dir.mkdir()
        outside = Path(temp_dir) / "outside.md"
        outside.write_text(
            "# Secret\n\n## 按任务读取索引\n\n"
            "| 任务 | 优先读取 | 跳过 |\n"
            "| --- | --- | --- |\n"
            "| 私密材料 | `凭证` | 不跳过 |\n\n"
            "## 凭证\nsecret-value\n"
            + "x\n" * 100,
            encoding="utf-8",
        )
        (reference_dir / "escape.md").symlink_to(outside)
        symlink_result = build_from_path(reference_dir, "私密材料", min_savings_ratio=0)
        assert symlink_result["status"] != "ready"
        assert "secret-value" not in symlink_result.get("content", "")
        direct_symlink_result = build_from_path(
            reference_dir / "escape.md",
            "私密材料",
            min_savings_ratio=0,
        )
        assert direct_symlink_result["status"] != "ready"
        assert "secret-value" not in direct_symlink_result.get("content", "")

        boundary = Path(temp_dir) / "boundary.md"
        boundary.write_text(
            "# R\n\n## 使用时机\nU\n\n## 不适用场景\nN\n\n"
            "## 读取后必须产出\nO\n\n## 按任务读取索引\n\n"
            "| 任务 | 优先读取 | 跳过 |\n"
            "| --- | --- | --- |\n"
            "| 核验任务 | `门禁` | 不跳过 |\n\n"
            "## 门禁\n必须复核。\n\n## 其他\n"
            + "无关内容。\n" * 58,
            encoding="utf-8",
        )
        boundary_result = build_package(boundary, "核验任务", min_savings_ratio=0.3)
        assert boundary_result["selections"][0]["kind"] == "file"
        assert boundary_result["estimated_savings_ratio"] == 0
        actual_boundary_tokens = estimate_tokens(
            json.dumps(boundary_result, ensure_ascii=False, indent=2)
        )["midpoint"]
        assert boundary_result["estimated_selected_tokens"] == actual_boundary_tokens

        high_risk = Path(temp_dir) / "high-risk.md"
        high_risk.write_text(
            "# High Risk\n\n## 使用时机\n用于受控执行。\n\n"
            "## 按任务读取索引\n\n| 任务 | 优先读取 | 跳过 |\n| --- | --- | --- |\n"
            "| 执行生产删除 | `执行步骤` | 不跳过 |\n\n"
            "## 执行步骤\n先运行命令。\n\n"
            "## 授权红线\n生产删除必须由 Owner 明确授权并保留回滚。\n"
            + "无关说明。\n" * 80,
            encoding="utf-8",
        )
        high_risk_result = build_package(high_risk, "执行生产删除", min_savings_ratio=0)
        assert high_risk_result["status"] == "ready"
        assert high_risk_result["selections"][0]["kind"] == "file"
        assert "生产删除必须由 Owner 明确授权" in high_risk_result["content"]

    print("OK wise-agent reference section reader self-test")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read bounded Markdown reference sections without network or file writes."
    )
    parser.add_argument("reference", nargs="?", type=Path)
    parser.add_argument("--query", default="")
    parser.add_argument("--heading", action="append", default=[])
    parser.add_argument("--max-sections", type=int, default=3)
    parser.add_argument("--min-savings", type=float, default=0.3)
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if not args.reference:
        parser.error("reference is required")
    if not args.reference.exists() or not (args.reference.is_file() or args.reference.is_dir()):
        parser.error(f"reference is not a file or directory: {args.reference}")
    if not args.query and not args.heading:
        parser.error("--query or --heading is required")
    if not 1 <= args.max_sections <= 5:
        parser.error("--max-sections must be between 1 and 5")
    if not 0 <= args.min_savings < 1:
        parser.error("--min-savings must be at least 0 and lower than 1")
    result = build_from_path(
        args.reference,
        args.query,
        headings=args.heading,
        max_sections=args.max_sections,
        min_savings_ratio=args.min_savings,
    )
    if args.metadata_only:
        result = {key: value for key, value in result.items() if key != "content"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
