#!/usr/bin/env python3
"""Evaluate local Codex skills with deterministic structure metrics.

The script is offline and read-only. It inspects Skill metadata, SKILL.md body
size, direct reference links, bundled resources, scripts, fixtures, and
repo-level validation hooks. It does not grade domain truth; it highlights
maintainability and trigger-readiness signals that should trend over time.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIRS = [
    "java-service-code-generator",
    "product-architecture-expert",
    "senior-software-architect",
]
REQUIRED_VALIDATE_HOOKS = [
    "scripts/validate-trigger-paths.py",
    "scripts/audit-reference-indexes.py",
    "scripts/audit-source-map.py",
    "scripts/archive-source-evidence.py --self-test",
    "scripts/skillx_export_adapter.py --self-test",
    "./sync-skills.sh --dry-run all",
]
PROGRESSIVE_HEADER_TERMS = [
    "## 使用时机",
    "## 不适用场景",
    "## 读取后必须产出",
    "## 需要继续读取的 reference",
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


def score_ratio(value: int, target: int, full_score: int) -> int:
    if target <= 0:
        return 0
    return min(full_score, round(full_score * min(value, target) / target))


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


def score_references(reference_count: int, reference_lines: int, reference_headers: int) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 70
    score += score_ratio(reference_count, 10, 18)
    score += score_ratio(reference_headers, min(reference_count, 8), 12) if reference_count else 0
    if reference_count == 0:
        warnings.append("no bundled references")
    if reference_lines > 8000:
        score -= 8
        warnings.append("reference set is large; keep indexes sharp")
    elif reference_lines > 5000:
        score -= 4
        warnings.append("reference set is sizable; monitor searchability")
    return max(min(score, 100), 0), warnings


def score_deterministic(script_count: int, fixture_count: int, has_self_test_signal: bool) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 65
    score += score_ratio(script_count, 2, 20)
    score += score_ratio(fixture_count, 2, 10)
    if has_self_test_signal:
        score += 5
    else:
        warnings.append("no obvious self-test signal for bundled scripts")
    return max(min(score, 100), 0), warnings


def score_trigger(skill_name: str, trigger_text: str) -> tuple[int, list[str]]:
    warnings: list[str] = []
    score = 80
    expected_terms = {
        "java-service-code-generator": ["java service generator", "structured input", "codegen"],
        "product-architecture-expert": ["payment product", "product diagram", "airwallex"],
        "senior-software-architect": ["architecture diagram", "bug diagnosis", "write tests"],
    }
    terms = expected_terms.get(skill_name, [])
    hits = sum(1 for term in terms if term.casefold() in trigger_text.casefold())
    score += score_ratio(hits, len(terms) or 1, 20)
    if hits < len(terms):
        missing = [term for term in terms if term.casefold() not in trigger_text.casefold()]
        warnings.append(f"trigger fixtures may miss: {', '.join(missing)}")
    return max(min(score, 100), 0), warnings


@dataclass
class SkillEvaluation:
    name: str
    score: int
    dimensions: dict[str, int]
    metrics: dict[str, Any]
    warnings: list[str]


def evaluate_skill(skill_dir: Path, trigger_text: str, validate_text: str) -> SkillEvaluation:
    skill_md = skill_dir / "SKILL.md"
    text = read(skill_md)
    frontmatter, _ = extract_frontmatter(text)
    refs = files_under(skill_dir, "references", "*.md")
    scripts = files_under(skill_dir, "scripts")
    fixtures = files_under(skill_dir, "fixtures")
    ref_links = direct_reference_links(text)
    missing_refs = [ref for ref in ref_links if not (skill_dir / ref).exists()]
    reference_headers = 0
    for ref in refs:
        ref_text = read(ref)
        if all(term in ref_text for term in PROGRESSIVE_HEADER_TERMS):
            reference_headers += 1
    script_text = "\n".join(read(script) for script in scripts if script.suffix in {".py", ".sh"})
    has_self_test_signal = "--self-test" in script_text or f"{skill_dir.name}/scripts" in validate_text

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
        len(refs),
        sum(line_count(read(ref)) for ref in refs),
        reference_headers,
    )
    deterministic_score, deterministic_warnings = score_deterministic(
        len(scripts),
        len(fixtures),
        has_self_test_signal,
    )
    trigger_score, trigger_warnings = score_trigger(skill_dir.name, trigger_text)

    dimensions = {
        "metadata_trigger": metadata_score,
        "progressive_loading": progressive_score,
        "reference_quality": reference_score,
        "deterministic_execution": deterministic_score,
        "trigger_fixtures": trigger_score,
    }
    weighted = (
        metadata_score * 0.20
        + progressive_score * 0.25
        + reference_score * 0.20
        + deterministic_score * 0.20
        + trigger_score * 0.15
    )
    metrics = {
        "description_len": len(frontmatter.get("description", "")),
        "skill_lines": line_count(text),
        "direct_reference_links": len(ref_links),
        "reference_files": len(refs),
        "reference_lines": sum(line_count(read(ref)) for ref in refs),
        "reference_files_with_progressive_headers": reference_headers,
        "script_files": len(scripts),
        "fixture_files": len(fixtures),
        "openai_yaml": (skill_dir / "agents" / "openai.yaml").exists(),
        "missing_reference_links": missing_refs,
    }
    warnings = (
        metadata_warnings
        + progressive_warnings
        + reference_warnings
        + deterministic_warnings
        + trigger_warnings
    )
    return SkillEvaluation(
        name=skill_dir.name,
        score=round(weighted),
        dimensions=dimensions,
        metrics=metrics,
        warnings=warnings,
    )


def evaluate_all() -> dict[str, Any]:
    trigger_text = read(ROOT / "scripts" / "validate-trigger-paths.py")
    validate_text = read(ROOT / "scripts" / "validate.sh")
    evaluations = [
        evaluate_skill(ROOT / skill_dir, trigger_text, validate_text)
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
    if report["overall_score"] < 85:
        raise SystemExit(f"overall score too low: {report['overall_score']}")
    expected = set(SKILL_DIRS)
    found = {item["name"] for item in report["skills"]}
    if found != expected:
        raise SystemExit(f"unexpected skill set: {sorted(found)}")
    for item in report["skills"]:
        metrics = item["metrics"]
        if not metrics["openai_yaml"]:
            raise SystemExit(f"{item['name']}: missing openai yaml")
        if metrics["missing_reference_links"]:
            raise SystemExit(f"{item['name']}: missing reference links")
        if metrics["skill_lines"] > 500:
            raise SystemExit(f"{item['name']}: SKILL.md too large")
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
