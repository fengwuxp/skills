#!/usr/bin/env python3
"""Validate a structured design-draft fidelity review.

This checker reads one explicit local Markdown file. It does not inspect
Figma, render images, access the network, or claim visual quality by itself.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


BLOCK_PATTERN = re.compile(
    r"```(?P<tag>draft-review|draft-checks)\s*\n(?P<body>.*?)```",
    re.DOTALL,
)
RECORD_PATTERN = re.compile(r"\[check\]\s*(?P<body>.*?)\s*\[/check\]", re.DOTALL)
VIEWPORT_PATTERN = re.compile(r"^\d{3,5}x\d{3,5}$")

CONTRACT_KEYS = (
    "review_id",
    "source_kind",
    "source_locator",
    "source_version",
    "access_mode",
    "source_limitations",
    "target_role",
    "version",
    "source_of_truth",
    "content_manifest",
    "asset_registry",
    "viewport_set",
    "viewports",
    "evidence_level",
    "reviewer",
    "status",
)
CHECK_KEYS = ("id", "category", "status", "expected", "observed", "test_case", "evidence", "owner")
REQUIRED_CHECKS = (
    "content-source",
    "content-completeness",
    "content-consistency",
    "layout-fit",
    "text-wrap",
    "overflow",
    "responsive",
    "asset-source",
    "state-coverage",
)
ALLOWED_CATEGORIES = {"content", "layout", "typography", "responsive", "assets", "states", "accessibility"}
ALLOWED_CHECK_STATUSES = {"pass", "fail", "blocked", "not-applicable"}
ALLOWED_EVIDENCE_LEVELS = {"E1", "E2", "E3", "E4"}
ALLOWED_REVIEW_STATUSES = {"draft", "ready-for-review", "blocked", "approved", "superseded"}
ALLOWED_SOURCE_KINDS = {"figma", "mockingbot", "screenshot", "runtime"}
ALLOWED_TARGET_ROLES = {"current-draft-only", "approved-design", "reference-only", "runtime-implementation"}
TRACEABLE_LOCATOR_PREFIXES = ("https://", "http://", "file:", "attachment:")


class ReviewError(ValueError):
    """A user-fixable review contract violation."""


@dataclass(frozen=True)
class ReviewParts:
    contract: dict[str, str]
    checks: list[dict[str, str]]


def parse_key_values(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ReviewError(f"无法解析字段行: {line}")
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            raise ReviewError(f"字段名不规范: {key}")
        if key in values:
            raise ReviewError(f"字段重复: {key}")
        values[key] = value.strip()
    return values


def extract_block(text: str, tag: str) -> str:
    blocks = [match.group("body") for match in BLOCK_PATTERN.finditer(text) if match.group("tag") == tag]
    if len(blocks) != 1:
        raise ReviewError(f"必须且只能有一个 {tag} block")
    return blocks[0]


def require_keys(values: dict[str, str], keys: tuple[str, ...], scope: str) -> None:
    missing = [key for key in keys if not values.get(key)]
    if missing:
        raise ReviewError(f"{scope} 缺少字段: {', '.join(missing)}")


def parse_checks(body: str) -> list[dict[str, str]]:
    checks = [parse_key_values(match.group("body")) for match in RECORD_PATTERN.finditer(body)]
    if not checks:
        raise ReviewError("draft-checks 至少需要一个 [check] 记录")
    return checks


def validate_contract(contract: dict[str, str]) -> None:
    require_keys(contract, CONTRACT_KEYS, "draft review contract")
    source_kind = contract["source_kind"]
    source_locator = contract["source_locator"]
    access_mode = contract["access_mode"].lower()
    evidence_level = contract["evidence_level"]
    if source_kind not in ALLOWED_SOURCE_KINDS:
        raise ReviewError(f"source_kind 不受支持: {source_kind}")
    if contract["target_role"] not in ALLOWED_TARGET_ROLES:
        raise ReviewError(f"target_role 不受支持: {contract['target_role']}")
    if contract["target_role"].lower() in {"content-authority", "source-of-truth", "product-source"}:
        raise ReviewError("source_of_truth/target_role 不能把当前待审设计声明为内容权威")
    if contract["source_of_truth"].strip().lower() in {"target_figma", "target figma", "current-draft"}:
        raise ReviewError("source_of_truth 不能指向当前待审设计或 current-draft")
    if contract["source_of_truth"].strip().rstrip("/") == source_locator.strip().rstrip("/"):
        raise ReviewError("source_of_truth 不能与 source_locator 相同")
    if evidence_level not in ALLOWED_EVIDENCE_LEVELS:
        raise ReviewError(f"evidence_level 不受支持: {evidence_level}")
    if source_kind == "figma":
        if "node-id=" not in source_locator and "node:" not in source_locator:
            raise ReviewError("figma source_locator 必须包含精确节点标识")
        if "figma" not in access_mode:
            raise ReviewError("figma access_mode 必须说明 MCP、Preview 或 export 读取方式")
        if evidence_level in {"E3", "E4"}:
            raise ReviewError("figma 设计稿审查最高为 E2；浏览器实现应使用 runtime 来源")
    elif source_kind == "mockingbot":
        if not source_locator.startswith(TRACEABLE_LOCATOR_PREFIXES):
            raise ReviewError("mockingbot source_locator 必须是分享链接或可追踪导出物")
        if "mockingbot" not in access_mode:
            raise ReviewError("mockingbot access_mode 必须说明 preview、annotation 或 export")
        if evidence_level in {"E2", "E3", "E4"} and not any(
            token in access_mode for token in ("preview", "annotation")
        ):
            raise ReviewError("mockingbot export 或 D2C 代码只能作为 E1 来源证据")
        if evidence_level in {"E3", "E4"}:
            raise ReviewError("mockingbot 设计稿审查最高为 E2；浏览器实现应使用 runtime 来源")
    elif source_kind == "screenshot":
        if not source_locator.startswith(TRACEABLE_LOCATOR_PREFIXES):
            raise ReviewError("screenshot source_locator 必须是可追踪文件、附件或 URL")
        if access_mode not in {"local-file", "uploaded-image", "remote-image"}:
            raise ReviewError("screenshot access_mode 不受支持")
        if evidence_level != "E1":
            raise ReviewError("screenshot 静态来源只能声明 E1")
    elif source_kind == "runtime":
        if not source_locator.startswith(("https://", "http://", "file:")):
            raise ReviewError("runtime source_locator 必须是浏览器可访问 URL")
        if not any(token in access_mode for token in ("browser", "playwright")):
            raise ReviewError("runtime access_mode 必须说明 browser 或 Playwright")
        if contract["target_role"] != "runtime-implementation":
            raise ReviewError("runtime target_role 必须是 runtime-implementation")
        if evidence_level not in {"E3", "E4"}:
            raise ReviewError("runtime 浏览器来源必须使用 E3 或 E4")
    if contract["status"] not in ALLOWED_REVIEW_STATUSES:
        raise ReviewError(f"status 不受支持: {contract['status']}")
    viewports = [item.strip() for item in contract["viewports"].split(",") if item.strip()]
    if len(viewports) < 2:
        raise ReviewError("viewports 至少需要两个目标视口")
    if len(set(viewports)) != len(viewports):
        raise ReviewError("viewports 不能重复")
    invalid = [viewport for viewport in viewports if not VIEWPORT_PATTERN.fullmatch(viewport)]
    if invalid:
        raise ReviewError(f"viewports 格式不正确: {', '.join(invalid)}")


def validate_check(check: dict[str, str], index: int) -> None:
    require_keys(check, CHECK_KEYS, f"check[{check.get('id', index)}]")
    if check["category"] not in ALLOWED_CATEGORIES:
        raise ReviewError(f"check[{index}] category 不受支持: {check['category']}")
    if check["status"] not in ALLOWED_CHECK_STATUSES:
        raise ReviewError(f"check[{index}] status 不受支持: {check['status']}")
    if check["status"] == "not-applicable":
        if not check.get("rationale"):
            raise ReviewError(f"check[{index}] not-applicable 必须填写 rationale")
        return
    if not check["evidence"]:
        raise ReviewError(f"check[{index}] evidence 不能为空")
    if check["status"] == "pass" and check["observed"].strip() == "":
        raise ReviewError(f"check[{index}] pass 必须记录 observed")
    if check["status"] in {"fail", "blocked"} and not check["owner"]:
        raise ReviewError(f"check[{index}] {check['status']} 必须有 owner")
    if check["id"] in {"content-source", "content-completeness", "content-consistency"} and not any(
        token in check["evidence"].lower() for token in ("manifest", "brief", "content")
    ):
        raise ReviewError(f"check[{index}] {check['id']} evidence 必须回到内容来源")
    if check["id"] in {"layout-fit", "text-wrap", "overflow", "responsive"} and not any(
        token in check["evidence"].lower() for token in ("screenshot", "frame", "annotation", "browser", "preview")
    ):
        raise ReviewError(f"check[{index}] {check['id']} evidence 必须包含视口或视觉复核证据")
    if check["id"] == "text-wrap" and not any(
        token in check["test_case"].lower() for token in ("longest", "cjk", "latin", "large-number", "localized", "long-content")
    ):
        raise ReviewError("check[text-wrap] test_case 必须覆盖最长标签、中英文、大数或长内容")


def validate_checks(checks: list[dict[str, str]]) -> None:
    seen: set[str] = set()
    for index, check in enumerate(checks, start=1):
        validate_check(check, index)
        if check["id"] in seen:
            raise ReviewError(f"check id 重复: {check['id']}")
        seen.add(check["id"])
    missing = [check_id for check_id in REQUIRED_CHECKS if check_id not in seen]
    if missing:
        raise ReviewError(f"Review Checks 缺少检查项: {', '.join(missing)}")


def validate_review_state(contract: dict[str, str], checks: list[dict[str, str]]) -> None:
    if contract["status"] == "approved":
        if contract["evidence_level"] == "E1":
            raise ReviewError("approved review 至少需要 E2 证据")
        if any(check["status"] in {"fail", "blocked"} for check in checks):
            raise ReviewError("approved review 不能包含 fail 或 blocked check")

    viewports = [item.strip() for item in contract["viewports"].split(",") if item.strip()]
    checks_by_id = {check["id"]: check for check in checks}
    for check_id in ("layout-fit", "responsive"):
        check = checks_by_id[check_id]
        if check["status"] != "pass":
            continue
        references = [item.strip() for item in check["evidence"].split(";") if item.strip()]
        if any(sum(viewport in reference for viewport in viewports) > 1 for reference in references):
            raise ReviewError(f"check[{check_id}] 每个视口必须使用独立证据引用")
        missing = [viewport for viewport in viewports if viewport not in check["evidence"]]
        if missing:
            raise ReviewError(f"check[{check_id}] evidence 缺少视口: {', '.join(missing)}")

    evidence = ";".join(check.get("evidence", "") for check in checks).lower()
    source_kind = contract["source_kind"]
    evidence_level = contract["evidence_level"]
    if source_kind == "figma" and evidence_level == "E2":
        if "design-context:" not in evidence or "screenshot:" not in evidence:
            raise ReviewError("figma E2 必须包含 design-context 与 screenshot 证据")
    elif source_kind == "mockingbot" and evidence_level == "E2":
        if "mockingbot-page-inventory:" not in evidence or not any(
            token in evidence for token in ("annotation:", "css:")
        ):
            raise ReviewError("mockingbot E2 必须包含页面清单与标注或 CSS 证据")
    elif source_kind == "screenshot" and "screenshot:" not in evidence:
        raise ReviewError("screenshot 来源必须包含 screenshot 证据")
    elif source_kind == "runtime" and not all(token in evidence for token in ("browser:", "screenshot:")):
        raise ReviewError("runtime E3/E4 必须包含 browser 与 screenshot 证据")
    if source_kind == "runtime" and evidence_level == "E4" and not any(
        token in evidence for token in ("user-task:", "production-observation:")
    ):
        raise ReviewError("E4 必须包含目标用户任务或生产运行观测证据")


def parse_review(text: str) -> ReviewParts:
    contract = parse_key_values(extract_block(text, "draft-review"))
    checks = parse_checks(extract_block(text, "draft-checks"))
    validate_contract(contract)
    validate_checks(checks)
    validate_review_state(contract, checks)
    return ReviewParts(contract, checks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="local Markdown design-draft review")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.file)
    try:
        parse_review(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ReviewError) as error:
        print(f"FAIL design draft review {path}: {error}", file=sys.stderr)
        return 2
    print(f"PASS design draft review: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
