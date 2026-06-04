#!/usr/bin/env python3
"""Audit large reference files for task-level reading indexes.

The script only inspects repository Markdown files. It does not access the
network, upload content, read secrets, or modify files. It is a lightweight
guard for progressive disclosure: large references should tell agents which
sections to read for common tasks.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOTS = [
    ROOT / "senior-software-architect" / "references",
    ROOT / "product-architecture-expert" / "references",
    ROOT / "java-service-code-generator" / "references",
]
WARN_LINE_THRESHOLD = 500
REQUIRED_INDEX_THRESHOLD = 350
REQUIRED_HEADING = "## 按任务读取索引"
REQUIRED_COLUMNS = ["任务", "优先读取", "跳过"]
ALTERNATIVE_REQUIRED_COLUMNS = ["任务", "主文档保留", "按需展开"]

REQUIRED_INDEX_FILES = {
    "senior-software-architect/references/ai-assisted-engineering.md",
    "senior-software-architect/references/architecture.md",
    "senior-software-architect/references/cad-mode.md",
    "senior-software-architect/references/clean-code.md",
    "senior-software-architect/references/coding-review-deep-dive.md",
    "senior-software-architect/references/coding-standards.md",
    "senior-software-architect/references/debugging-diagnosis.md",
    "senior-software-architect/references/diagram-output.md",
    "senior-software-architect/references/knowledge-graph.md",
    "senior-software-architect/references/language-agnostic-architecture.md",
    "senior-software-architect/references/product-design.md",
    "senior-software-architect/references/production-readiness.md",
    "senior-software-architect/references/project-governance-codebase-and-modules.md",
    "senior-software-architect/references/project-governance-data-security-quality.md",
    "senior-software-architect/references/project-governance-delivery-and-platform.md",
    "senior-software-architect/references/project-governance-service-api-modeling.md",
    "senior-software-architect/references/project-governance-standards.md",
    "senior-software-architect/references/review-and-output-templates.md",
    "senior-software-architect/references/scenario-routing.md",
    "senior-software-architect/references/security-architecture.md",
    "senior-software-architect/references/skill-tree-architecture-design.md",
    "senior-software-architect/references/skill-tree-engineering-quality.md",
    "senior-software-architect/references/skill-tree-platform-leadership-ai.md",
    "senior-software-architect/references/skill-tree.md",
    "senior-software-architect/references/source-map.md",
    "senior-software-architect/references/system-analysis-design.md",
    "senior-software-architect/references/system-analysis-template.md",
    "senior-software-architect/references/testing.md",
    "senior-software-architect/references/testing-practices-business-funds.md",
    "senior-software-architect/references/testing-practices-java-spring-common.md",
    "senior-software-architect/references/testing-practices-java-service-flow.md",
    "senior-software-architect/references/testing-practices-java-unit-db.md",
    "senior-software-architect/references/testing-practices-java-web.md",
    "senior-software-architect/references/testing-practices-non-java-and-selection.md",
    "senior-software-architect/references/testing-practices.md",
    "senior-software-architect/references/wind-projects-patterns.md",
    "senior-software-architect/references/workflow.md",
    "product-architecture-expert/references/card-network-and-card-rails.md",
    "product-architecture-expert/references/clearing-settlement.md",
    "product-architecture-expert/references/diagram-output.md",
    "product-architecture-expert/references/dispute-refund-and-chargeback-operations.md",
    "product-architecture-expert/references/formance-reference-patterns.md",
    "product-architecture-expert/references/global-payment-emerging.md",
    "product-architecture-expert/references/glossary.md",
    "product-architecture-expert/references/highnote-reference-patterns.md",
    "product-architecture-expert/references/payment-channel-routing-and-operations.md",
    "product-architecture-expert/references/payment-design-checklists.md",
    "product-architecture-expert/references/payment-methodology.md",
    "product-architecture-expert/references/payment-rails-ach-and-bank-transfers.md",
    "product-architecture-expert/references/payment-risk-fraud-and-merchant-operations.md",
    "product-architecture-expert/references/payment-scenario-routing.md",
    "product-architecture-expert/references/product-architecture-methodology.md",
    "product-architecture-expert/references/product-design-and-prd.md",
    "product-architecture-expert/references/product-prd-template.md",
    "product-architecture-expert/references/product-prd-quality-gates.md",
    "product-architecture-expert/references/product-prd-financial-appendix.md",
    "product-architecture-expert/references/product-prd-operations-and-data.md",
    "product-architecture-expert/references/product-scenario-routing.md",
    "product-architecture-expert/references/regulatory-baseline.md",
    "product-architecture-expert/references/skill-tree.md",
    "product-architecture-expert/references/source-map.md",
    "product-architecture-expert/references/virtual-card-and-vcc.md",
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def has_task_index(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return REQUIRED_HEADING in text and (
        all(column in text for column in REQUIRED_COLUMNS)
        or all(column in text for column in ALTERNATIVE_REQUIRED_COLUMNS)
    )


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    found_files: set[str] = set()

    for root in REFERENCE_ROOTS:
        for path in sorted(root.glob("*.md")):
            rel = relative(path)
            found_files.add(rel)
            count = line_count(path)
            if count > WARN_LINE_THRESHOLD:
                warnings.append(f"WARN large reference {rel}: {count} lines")
            if count >= REQUIRED_INDEX_THRESHOLD and not has_task_index(path):
                failures.append(f"{rel}: {count} lines but missing {REQUIRED_HEADING}")

    missing_tracked = sorted(REQUIRED_INDEX_FILES - found_files)
    failures.extend(f"{rel}: tracked indexed reference not found" for rel in missing_tracked)

    for rel in sorted(REQUIRED_INDEX_FILES & found_files):
        if not has_task_index(ROOT / rel):
            failures.append(f"{rel}: tracked indexed reference missing {REQUIRED_HEADING}")

    for warning in warnings:
        print(warning)

    if failures:
        print("FAIL reference index audit")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("OK reference index audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
