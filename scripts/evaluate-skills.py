#!/usr/bin/env python3
"""Evaluate local Codex skills with deterministic structure and prompt metrics.

The script is offline and read-only. It inspects Skill metadata, SKILL.md body
size, direct reference links, bundled resources, scripts, fixtures, and
repo-level validation hooks. It also inspects realistic positive and hard
negative prompt fixtures. It does not execute an Agent or grade domain truth;
it highlights static maintainability and trigger-readiness signals.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIRS = sorted(path.parent.name for path in ROOT.glob("*/SKILL.md"))
SCRIPTLESS_VALIDATED_SKILLS = {
    "wind-coding-conventions",
}
REQUIRED_VALIDATE_HOOKS = [
    "scripts/validate-trigger-paths.py",
    "scripts/audit-reference-indexes.py",
    "scripts/audit-source-map.py",
    "scripts/audit-skill-eval-fixtures.py --self-test",
    "scripts/archive-source-evidence.py --self-test",
    "scripts/skillx_export_adapter.py --self-test",
    "scripts/validate-installed-skills.sh",
    "./sync-skills.sh --dry-run all",
]
SKILL_EVAL_PROMPT_FIXTURE = ROOT / "fixtures" / "skill-eval" / "prompt-cases.json"
REQUIRED_PROMPT_DIMENSIONS = {
    "trigger_accuracy",
    "output_quality",
    "efficiency_metrics",
    "baseline_comparison",
    "variance_check",
}
PROGRESSIVE_HEADER_TERMS = [
    "## 使用时机",
    "## 不适用场景",
    "## 读取后必须产出",
    "## 需要继续读取的 reference",
]
TASK_INDEX_HEADING = "## 按任务读取索引"
TASK_INDEX_COLUMNS = ["| 任务 | 优先读取 | 跳过 |"]
REFERENCE_FILE_SOFT_LIMIT = 400
REFERENCE_FILE_HARD_LIMIT = 550
REFERENCE_SECTION_SOFT_LIMIT = 120
REFERENCE_SECTION_HARD_LIMIT = 180
SENIOR_REFERENCE_TOTAL_SOFT_LIMIT = 7000
SENIOR_REFERENCE_TOTAL_HARD_LIMIT = 8000
CONTROLLED_REFERENCE_SEARCHABILITY_SCORE = 85
TOP_LARGE_REFERENCE_COUNT = 5
TOP_LARGE_SECTION_COUNT = 5
REFERENCE_SPLIT_TRIGGERS = [
    "more than one independent task entry in one reference",
    "a single section longer than 120 lines",
    "the same rule repeated across multiple references",
    "more than eight level-2 topics in one reference",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_count(text: str) -> int:
    return text.count("\n") + 1


def extract_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text
    frontmatter_text, body = parts[1], parts[2]
    data: dict[str, str] = {}
    current_key: str | None = None
    block_values: list[str] = []
    for raw_line in frontmatter_text.splitlines():
        line = raw_line.rstrip()
        if current_key and (line.startswith("  ") or not line.strip()):
            block_values.append(line.strip())
            continue
        if current_key:
            data[current_key] = "\n".join(value for value in block_values if value).strip()
            current_key = None
            block_values = []
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        if value == "|":
            current_key = key
            block_values = []
        else:
            data[key] = value.strip().strip("\"'")
    if current_key:
        data[current_key] = "\n".join(value for value in block_values if value).strip()
    return data, body


def direct_reference_links(text: str) -> list[str]:
    return sorted(set(re.findall(r"`(references/[^`]+)`", text)))


def files_under(skill_dir: Path, subdir: str, pattern: str = "*") -> list[Path]:
    root = skill_dir / subdir
    if not root.exists():
        return []
    return sorted(path for path in root.glob(pattern) if path.is_file())


def fixture_files_under(skill_dir: Path) -> list[Path]:
    root = skill_dir / "fixtures"
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def score_ratio(value: int, target: int, full_score: int) -> int:
    if target <= 0:
        return 0
    return min(full_score, round(full_score * min(value, target) / target))


def has_progressive_headers(text: str) -> bool:
    return all(term in text for term in PROGRESSIVE_HEADER_TERMS)


def has_task_index(text: str) -> bool:
    return TASK_INDEX_HEADING in text and all(column in text for column in TASK_INDEX_COLUMNS)


def score_metadata(description_len: int, has_agent_yaml: bool) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 100
    if description_len < 80:
        score -= 18
        warnings.append("description too short for reliable trigger recognition")
    elif description_len > 420:
        score -= 10
        warnings.append("description is long; watch metadata context cost")
    elif description_len > 320:
        score -= 4
        warnings.append("description is near the upper comfort band")
    if not has_agent_yaml:
        score -= 15
        warnings.append("missing agents/openai.yaml")
    return max(score, 0), warnings


def score_progressive(skill_lines: int, ref_links: int, missing_refs: list[str]) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 100
    if skill_lines > 500:
        score -= 30
        warnings.append("SKILL.md exceeds 500 lines")
    elif skill_lines > 350:
        score -= 10
        warnings.append("SKILL.md is growing; consider moving detail to references")
    if ref_links == 0:
        score -= 18
        warnings.append("SKILL.md has no direct reference links")
    if missing_refs:
        score -= 40
        warnings.append(f"missing direct references: {', '.join(missing_refs)}")
    return max(score, 0), warnings


def relative_reference_stats(skill_dir: Path, refs: list[Path]) -> list[dict[str, Any]]:
    stats = []
    for ref in refs:
        ref_text = read(ref)
        sections = reference_section_stats(ref.relative_to(skill_dir).as_posix(), ref_text)
        stats.append(
            {
                "path": ref.relative_to(skill_dir).as_posix(),
                "lines": line_count(ref_text),
                "level_2_sections": len(sections),
                "largest_section_lines": sections[0]["lines"] if sections else 0,
                "has_progressive_headers": has_progressive_headers(ref_text),
                "has_task_index": has_task_index(ref_text),
            }
        )
    return sorted(stats, key=lambda item: (-item["lines"], item["path"]))


def reference_section_stats(relative_path: str, text: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_start = 1
    current_lines = 0
    in_fenced_code = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("```"):
            in_fenced_code = not in_fenced_code
        if line.startswith("## "):
            if not in_fenced_code and current:
                current["lines"] = current_lines
                sections.append(current)
            if not in_fenced_code:
                current = {
                    "path": relative_path,
                    "title": line[3:].strip(),
                    "start_line": line_number,
                }
                current_start = line_number
                current_lines = 1
        elif current:
            current_lines = line_number - current_start + 1
    if current:
        current["lines"] = current_lines
        sections.append(current)
    return sorted(sections, key=lambda item: (-item["lines"], item["path"], item["start_line"]))


def all_reference_sections(skill_dir: Path, refs: list[Path]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for ref in refs:
        sections.extend(
            reference_section_stats(
                ref.relative_to(skill_dir).as_posix(),
                read(ref),
            )
        )
    return sorted(sections, key=lambda item: (-item["lines"], item["path"], item["start_line"]))


def reference_searchability_score(
    reference_count: int,
    reference_lines: int,
    reference_stats: list[dict[str, Any]],
    section_stats: list[dict[str, Any]],
) -> int:
    if reference_count == 0:
        return 0
    large_refs = [
        item
        for item in reference_stats
        if item["lines"] >= REFERENCE_FILE_SOFT_LIMIT
        or item["level_2_sections"] > 8
    ]
    score = 0
    score += score_ratio(
        sum(1 for item in reference_stats if item["has_progressive_headers"]),
        min(reference_count, 8),
        22,
    )
    score += score_ratio(
        sum(1 for item in large_refs if item["has_task_index"]),
        len(large_refs) or 1,
        28,
    )
    largest_file = reference_stats[0]["lines"] if reference_stats else 0
    largest_section = section_stats[0]["lines"] if section_stats else 0
    if largest_file <= REFERENCE_FILE_SOFT_LIMIT:
        score += 18
    elif largest_file <= REFERENCE_FILE_HARD_LIMIT:
        score += 10
    if largest_section <= REFERENCE_SECTION_SOFT_LIMIT:
        score += 18
    elif largest_section <= REFERENCE_SECTION_HARD_LIMIT:
        score += 8
    average_lines = reference_lines / reference_count
    if average_lines <= 220:
        score += 14
    elif average_lines <= 300:
        score += 8
    elif average_lines <= 400:
        score += 4
    return min(score, 100)


def score_references(
    skill_name: str,
    reference_count: int,
    reference_lines: int,
    reference_headers: int,
    reference_stats: list[dict[str, Any]],
    section_stats: list[dict[str, Any]],
    searchability_score: int,
) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 70
    score += score_ratio(reference_count, 10, 18)
    score += score_ratio(reference_headers, min(reference_count, 8), 12) if reference_count else 0
    if reference_count == 0:
        warnings.append("no bundled references")
    if reference_lines > 8000:
        score -= 8
        warnings.append("reference set is large; keep indexes sharp")
    elif reference_lines > 5000 and searchability_score < CONTROLLED_REFERENCE_SEARCHABILITY_SCORE:
        score -= 4
        warnings.append("reference set is sizable; monitor searchability")
    over_soft = [
        item
        for item in reference_stats
        if item["lines"] > REFERENCE_FILE_SOFT_LIMIT
    ]
    over_hard = [
        item
        for item in reference_stats
        if item["lines"] > REFERENCE_FILE_HARD_LIMIT
    ]
    if over_hard:
        score -= 10
        names = ", ".join(f"{item['path']}={item['lines']}" for item in over_hard)
        warnings.append(f"reference hard budget exceeded: {names}")
    elif over_soft:
        names = ", ".join(f"{item['path']}={item['lines']}" for item in over_soft[:3])
        warnings.append(
            "reference soft budget exceeded; inspect split triggers, "
            f"does not force mechanical splitting: {names}"
        )
    oversized_sections = [
        item
        for item in section_stats
        if item["lines"] > REFERENCE_SECTION_SOFT_LIMIT
    ]
    hard_oversized_sections = [
        item
        for item in section_stats
        if item["lines"] > REFERENCE_SECTION_HARD_LIMIT
    ]
    if hard_oversized_sections:
        score -= 6
        names = ", ".join(
            f"{item['path']}#{item['title']}={item['lines']}"
            for item in hard_oversized_sections[:3]
        )
        warnings.append(f"reference section hard budget exceeded: {names}")
    elif oversized_sections:
        names = ", ".join(
            f"{item['path']}#{item['title']}={item['lines']}"
            for item in oversized_sections[:3]
        )
        warnings.append(
            "reference section soft budget exceeded; inspect whether one topic should split: "
            f"{names}"
        )
    if (
        skill_name == "senior-software-architect"
        and reference_lines > SENIOR_REFERENCE_TOTAL_SOFT_LIMIT
        and searchability_score < CONTROLLED_REFERENCE_SEARCHABILITY_SCORE
    ):
        warnings.append(
            "senior reference total exceeds soft budget; monitor large_reference_files"
        )
        if reference_lines > SENIOR_REFERENCE_TOTAL_HARD_LIMIT:
            score -= 8
            warnings.append("senior reference total exceeds hard budget")
    return max(min(score, 100), 0), warnings


def score_deterministic(
    skill_name: str,
    script_count: int,
    fixture_count: int,
    has_self_test_signal: bool,
    prompt_stats: dict[str, Any],
) -> tuple[int, list[str]]:
    warnings: list[str] = []
    if script_count == 0 and skill_name in SCRIPTLESS_VALIDATED_SKILLS:
        score = 80
        if prompt_stats["positive_cases"] >= 2 and prompt_stats["hard_negative_cases"] >= 2:
            score += 10
        if prompt_stats["positive_without_name_cases"] >= 1:
            score += 5
        return max(min(score, 100), 0), warnings

    score = 65
    score += score_ratio(script_count, 2, 20)
    score += score_ratio(fixture_count, 2, 10)
    if has_self_test_signal:
        score += 5
    else:
        warnings.append("no obvious self-test signal for bundled scripts")
    return max(min(score, 100), 0), warnings


def score_trigger(skill_name: str, prompt_fixture: dict[str, Any]) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 80
    expected_terms = {
        "wise-agent": ["知止者", "自己判断并推进", "只读 CR", "补单元测试"],
        "document-authoring": ["document-authoring", "正式报告", "DOCX"],
        "hanzi-philology": ["hanzi-philology", "甲骨文", "《说文解字》"],
        "java-service-code-generator": ["CREATE TABLE", "字段表格", "Java Entity"],
        "product-architecture-expert": ["PRD", "业务能力地图", "验收种子"],
        "senior-software-architect": ["CR", "架构", "TDD"],
        "wind-coding-conventions": ["Wind 编码约规", "Entity 不外露", "AGENTS.md"],
    }
    trigger_text = "\n".join(
        case.get("query", "")
        for case in prompt_fixture.get("cases", [])
        if case.get("skill") == skill_name and case.get("should_trigger") is True
    )
    terms = expected_terms.get(skill_name, [])
    hits = sum(1 for term in terms if term.casefold() in trigger_text.casefold())
    score += score_ratio(hits, len(terms) or 1, 20)
    if hits < len(terms):
        missing = [term for term in terms if term.casefold() not in trigger_text.casefold()]
        warnings.append(f"trigger fixtures may miss: {', '.join(missing)}")
    return max(min(score, 100), 0), warnings


def load_prompt_fixture() -> dict[str, Any]:
    if not SKILL_EVAL_PROMPT_FIXTURE.exists():
        return {}
    return json.loads(read(SKILL_EVAL_PROMPT_FIXTURE))


def prompt_fixture_stats(skill_name: str, prompt_fixture: dict[str, Any]) -> dict[str, Any]:
    cases = [
        case
        for case in prompt_fixture.get("cases", [])
        if case.get("skill") == skill_name
    ]
    positive = [case for case in cases if case.get("should_trigger") is True]
    negative = [case for case in cases if case.get("should_trigger") is False]
    hard_negative = [case for case in negative if case.get("hard_negative") is True]
    positive_without_name = [
        case
        for case in positive
        if skill_name not in case.get("query", "").casefold()
    ]
    dimensions = sorted(
        {
            dimension
            for case in cases
            for dimension in case.get("dimensions", [])
        }
    )
    return {
        "cases": len(cases),
        "positive_cases": len(positive),
        "negative_cases": len(negative),
        "hard_negative_cases": len(hard_negative),
        "positive_without_name_cases": len(positive_without_name),
        "dimensions": dimensions,
    }


def score_prompt_fixtures(skill_name: str, stats: dict[str, Any], prompt_fixture: dict[str, Any]) -> tuple[int, list[str]]:
    warnings: list[str] = []
    if not prompt_fixture:
        return 0, ["missing Skill Eval prompt fixture"]

    score = 55
    score += score_ratio(stats["positive_cases"], 2, 12)
    score += score_ratio(stats["negative_cases"], 2, 12)
    score += score_ratio(stats["hard_negative_cases"], 2, 10)
    score += score_ratio(stats["positive_without_name_cases"], 1, 6)
    score += score_ratio(len(stats["dimensions"]), 4, 5)

    if stats["positive_cases"] < 2:
        warnings.append(f"{skill_name}: realistic prompt fixture has too few positive cases")
    if stats["negative_cases"] < 2:
        warnings.append(f"{skill_name}: realistic prompt fixture has too few negative cases")
    if stats["hard_negative_cases"] < 2:
        warnings.append(f"{skill_name}: realistic prompt fixture has too few hard negatives")
    if stats["positive_without_name_cases"] < 1:
        warnings.append(f"{skill_name}: realistic prompt fixture has no positive case without explicit skill name")

    fixture_dimensions = set(prompt_fixture.get("evaluation_dimensions", []))
    missing_dimensions = REQUIRED_PROMPT_DIMENSIONS - fixture_dimensions
    if missing_dimensions:
        score -= 12
        warnings.append(f"Skill Eval fixture missing dimensions: {', '.join(sorted(missing_dimensions))}")

    source = prompt_fixture.get("source", {})
    if source.get("read_status") != "title_author_time_body_read":
        score -= 10
        warnings.append("Skill Eval source is not recorded as title/author/time/body read")

    return max(min(score, 100), 0), warnings


@dataclass
class SkillEvaluation:
    name: str
    score: int
    dimensions: dict[str, int]
    metrics: dict[str, Any]
    warnings: list[str]


def evaluate_skill(skill_dir: Path, validate_text: str) -> SkillEvaluation:
    skill_md = skill_dir / "SKILL.md"
    text = read(skill_md)
    frontmatter, _ = extract_frontmatter(text)
    refs = files_under(skill_dir, "references", "*.md")
    reference_stats = relative_reference_stats(skill_dir, refs)
    section_stats = all_reference_sections(skill_dir, refs)
    scripts = files_under(skill_dir, "scripts")
    fixtures = fixture_files_under(skill_dir)
    ref_links = direct_reference_links(text)
    missing_refs = [ref for ref in ref_links if not (skill_dir / ref).exists()]
    reference_headers = sum(1 for item in reference_stats if item["has_progressive_headers"])
    reference_task_indexes = sum(1 for item in reference_stats if item["has_task_index"])
    reference_searchability = reference_searchability_score(
        len(refs),
        sum(item["lines"] for item in reference_stats),
        reference_stats,
        section_stats,
    )
    script_text = "\n".join(read(script) for script in scripts if script.suffix in {".py", ".sh"})
    has_self_test_signal = "--self-test" in script_text or f"{skill_dir.name}/scripts" in validate_text
    prompt_fixture = load_prompt_fixture()
    prompt_stats = prompt_fixture_stats(skill_dir.name, prompt_fixture)

    metadata_score, metadata_warnings = score_metadata(
        len(frontmatter.get("description", "")),
        (skill_dir / "agents" / "openai.yaml").exists(),
    )
    progressive_score, progressive_warnings = score_progressive(
        line_count(text),
        len(ref_links),
        missing_refs,
    )
    reference_score, reference_warnings = score_references(
        skill_dir.name,
        len(refs),
        sum(item["lines"] for item in reference_stats),
        reference_headers,
        reference_stats,
        section_stats,
        reference_searchability,
    )
    deterministic_score, deterministic_warnings = score_deterministic(
        skill_dir.name,
        len(scripts),
        len(fixtures),
        has_self_test_signal,
        prompt_stats,
    )
    trigger_score, trigger_warnings = score_trigger(skill_dir.name, prompt_fixture)
    prompt_score, prompt_warnings = score_prompt_fixtures(skill_dir.name, prompt_stats, prompt_fixture)

    dimensions = {
        "metadata_trigger": metadata_score,
        "progressive_loading": progressive_score,
        "reference_quality": reference_score,
        "deterministic_execution": deterministic_score,
        "trigger_fixtures": trigger_score,
        "realistic_prompt_fixtures": prompt_score,
    }
    weighted = (
        metadata_score * 0.18
        + progressive_score * 0.22
        + reference_score * 0.18
        + deterministic_score * 0.18
        + trigger_score * 0.12
        + prompt_score * 0.12
    )
    metrics = {
        "description_len": len(frontmatter.get("description", "")),
        "skill_lines": line_count(text),
        "direct_reference_links": len(ref_links),
        "reference_files": len(refs),
        "reference_lines": sum(item["lines"] for item in reference_stats),
        "reference_files_with_progressive_headers": reference_headers,
        "reference_files_with_task_indexes": reference_task_indexes,
        "reference_searchability_score": reference_searchability,
        "largest_reference_lines": reference_stats[0]["lines"] if reference_stats else 0,
        "large_reference_files": reference_stats[:TOP_LARGE_REFERENCE_COUNT],
        "largest_reference_section_lines": section_stats[0]["lines"] if section_stats else 0,
        "large_reference_sections": section_stats[:TOP_LARGE_SECTION_COUNT],
        "reference_files_over_soft_limit": [
            item
            for item in reference_stats
            if item["lines"] > REFERENCE_FILE_SOFT_LIMIT
        ],
        "reference_files_over_hard_limit": [
            item
            for item in reference_stats
            if item["lines"] > REFERENCE_FILE_HARD_LIMIT
        ],
        "reference_sections_over_soft_limit": [
            item
            for item in section_stats
            if item["lines"] > REFERENCE_SECTION_SOFT_LIMIT
        ],
        "reference_sections_over_hard_limit": [
            item
            for item in section_stats
            if item["lines"] > REFERENCE_SECTION_HARD_LIMIT
        ],
        "reference_budget": {
            "file_soft_limit": REFERENCE_FILE_SOFT_LIMIT,
            "file_hard_limit": REFERENCE_FILE_HARD_LIMIT,
            "section_soft_limit": REFERENCE_SECTION_SOFT_LIMIT,
            "section_hard_limit": REFERENCE_SECTION_HARD_LIMIT,
            "senior_total_soft_limit": SENIOR_REFERENCE_TOTAL_SOFT_LIMIT,
            "senior_total_hard_limit": SENIOR_REFERENCE_TOTAL_HARD_LIMIT,
            "controlled_searchability_score": CONTROLLED_REFERENCE_SEARCHABILITY_SCORE,
            "split_triggers": REFERENCE_SPLIT_TRIGGERS,
            "note": "Soft budget triggers review only and does not force mechanical splitting.",
        },
        "script_files": len(scripts),
        "fixture_files": len(fixtures),
        "skill_eval_prompt_fixture": prompt_stats,
        "skill_eval_prompt_source": prompt_fixture.get("source", {}),
        "openai_yaml": (skill_dir / "agents" / "openai.yaml").exists(),
        "missing_reference_links": missing_refs,
    }
    warnings = (
        metadata_warnings
        + progressive_warnings
        + reference_warnings
        + deterministic_warnings
        + trigger_warnings
        + prompt_warnings
    )
    return SkillEvaluation(
        name=skill_dir.name,
        score=round(weighted),
        dimensions=dimensions,
        metrics=metrics,
        warnings=warnings,
    )


def evaluate_all() -> dict[str, Any]:
    validate_text = read(ROOT / "scripts" / "validate.sh")
    evaluations = [
        evaluate_skill(ROOT / skill_dir, validate_text)
        for skill_dir in SKILL_DIRS
    ]
    overall = round(sum(item.score for item in evaluations) / len(evaluations))
    return {
        "overall_score": overall,
        "skills": [
            {
                "name": item.name,
                "score": item.score,
                "dimensions": item.dimensions,
                "metrics": item.metrics,
                "warnings": item.warnings,
            }
            for item in evaluations
        ],
    }


def print_text(report: dict[str, Any]) -> None:
    print(f"Overall skill score: {report['overall_score']}/100")
    for item in report["skills"]:
        print(f"\n== {item['name']} ==")
        print(f"score: {item['score']}/100")
        print("dimensions:")
        for key, value in item["dimensions"].items():
            print(f"  - {key}: {value}")
        print("metrics:")
        for key, value in item["metrics"].items():
            print(f"  - {key}: {value}")
        if item["warnings"]:
            print("warnings:")
            for warning in item["warnings"]:
                print(f"  - {warning}")
        else:
            print("warnings: none")


def run_self_test() -> None:
    report = evaluate_all()
    legacy_wind_skill = "wind-project-" + "coding-conventions"
    if legacy_wind_skill in SKILL_DIRS or "wind-coding-conventions" not in SKILL_DIRS:
        raise SystemExit("Wind coding conventions skill ID migration is incomplete")
    if report["overall_score"] < 85:
        raise SystemExit(f"overall score too low: {report['overall_score']}")
    expected = set(SKILL_DIRS)
    found = {item["name"] for item in report["skills"]}
    if found != expected:
        raise SystemExit(f"unexpected skill set: {sorted(found)}")
    hanzi = next(item for item in report["skills"] if item["name"] == "hanzi-philology")
    if any("甲骨文" in warning for warning in hanzi["warnings"]):
        raise SystemExit("hanzi-philology: trigger scoring ignored prompt fixture query text")
    for item in report["skills"]:
        metrics = item["metrics"]
        if not metrics["openai_yaml"]:
            raise SystemExit(f"{item['name']}: missing openai yaml")
        if metrics["missing_reference_links"]:
            raise SystemExit(f"{item['name']}: missing reference links")
        if metrics["skill_lines"] > 500:
            raise SystemExit(f"{item['name']}: SKILL.md too large")
        if item["dimensions"]["realistic_prompt_fixtures"] < 90:
            raise SystemExit(
                f"{item['name']}: realistic prompt fixture score too low: "
                f"{item['dimensions']['realistic_prompt_fixtures']}"
            )
        if (
            item["name"] == "wind-coding-conventions"
            and item["metrics"]["fixture_files"] < 2
        ):
            raise SystemExit(f"{item['name']}: missing runnable fixture files")
        if metrics["reference_files_over_hard_limit"]:
            names = ", ".join(
                f"{ref['path']}={ref['lines']}"
                for ref in metrics["reference_files_over_hard_limit"]
            )
            raise SystemExit(f"{item['name']}: reference file too large: {names}")
        if (
            item["name"] == "senior-software-architect"
            and metrics["reference_lines"] > SENIOR_REFERENCE_TOTAL_HARD_LIMIT
        ):
            raise SystemExit(
                f"{item['name']}: reference total too large: {metrics['reference_lines']}"
            )
        if (
            item["name"] == "senior-software-architect"
            and metrics["reference_lines"] > SENIOR_REFERENCE_TOTAL_SOFT_LIMIT
            and metrics["reference_searchability_score"] < CONTROLLED_REFERENCE_SEARCHABILITY_SCORE
        ):
            raise SystemExit(
                f"{item['name']}: reference searchability too low: "
                f"{metrics['reference_searchability_score']}"
            )
    print("OK skill evaluation self-test")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument("--self-test", action="store_true", help="run deterministic score guard")
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0

    report = evaluate_all()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
