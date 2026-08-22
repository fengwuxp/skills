#!/usr/bin/env python3
"""Validate the structured contract of a Figma design plan.

The checker reads one explicit local Markdown file. It does not access the
network, call Figma, write files, or judge visual quality.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


BLOCK_PATTERN = re.compile(
    r"```(?P<tag>design-contract|page-manifest|navigation-map|figma-evidence)\s*\n"
    r"(?P<body>.*?)```",
    re.DOTALL,
)
RECORD_PATTERN = re.compile(r"\[(?P<tag>page|item)\]\s*(?P<body>.*?)\s*\[/\1\]", re.DOTALL)
FIGMA_NAME_PATTERN = re.compile(
    r"^(?P<prefix>Web PC|Web Mobile) / \d{2} [^/]+ / [^/]+ / \d+ / "
    r"(?P<status>Draft|Approved|Superseded)$",
    re.IGNORECASE,
)
EVIDENCE_PATTERN = re.compile(r"^(?P<field>[a-z_]+):\s*status=(?P<status>[^;]+);\s*evidence=(?P<evidence>.*)$")

CONTRACT_KEYS = (
    "project_id",
    "client_scope",
    "change_mode",
    "product_source",
    "brief_source",
    "reference_figma",
    "target_figma",
    "target_role",
    "terminology_source",
    "asset_registry",
    "brand_boundary",
    "owner",
    "status",
)
PAGE_KEYS = (
    "id",
    "route",
    "display_name",
    "figma_name",
    "purpose",
    "source_node",
    "states",
    "state_exclusions",
    "state_notes",
    "content_source",
    "nav_label",
    "client_scope",
    "status",
    "is_current",
)
EVIDENCE_FIELDS = (
    "components",
    "variables",
    "auto_layout",
    "annotations",
    "dev_resources",
    "code_connect",
    "component_playground",
    "ready_for_dev",
    "state_matrix",
)
ALLOWED_CONTRACT_MODES = {
    "visual-adjustment",
    "visual-adjustment-with-bounded-content-optimization",
    "system-expansion",
    "new-interface",
    "redesign",
}
ALLOWED_CONTRACT_STATUSES = {"draft", "ready-for-figma", "ready-for-code", "approved", "superseded"}
ALLOWED_PAGE_STATUSES = {"draft", "approved", "superseded"}
ALLOWED_EVIDENCE_STATUSES = {"planned", "verified", "completed", "not-applicable"}
CLIENT_SCOPE_PREFIXES = {"web-pc": "Web PC", "web-mobile": "Web Mobile"}
ALLOWED_TARGET_ROLES = {"current-draft-only", "approved-design", "reference-only"}
REQUIRED_STATE_COVERAGE = {"loading", "empty", "error", "success", "permission", "return", "close"}
STATE_ALIASES = {"error": {"error", "validation"}}


class ContractError(ValueError):
    """A user-fixable design-plan contract violation."""


@dataclass(frozen=True)
class PlanParts:
    contract: dict[str, str]
    pages: list[dict[str, str]]
    navigation: list[dict[str, str]]
    evidence: dict[str, tuple[str, str]]


def parse_key_values(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ContractError(f"无法解析字段行: {line}")
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise ContractError(f"字段名不规范: {key}")
        if key in values:
            raise ContractError(f"字段重复: {key}")
        values[key] = value.strip()
    return values


def extract_block(text: str, tag: str) -> str:
    blocks = [match.group("body") for match in BLOCK_PATTERN.finditer(text) if match.group("tag") == tag]
    if len(blocks) != 1:
        raise ContractError(f"必须且只能有一个 {tag} block")
    return blocks[0]


def parse_records(body: str, tag: str) -> list[dict[str, str]]:
    records = []
    for match in RECORD_PATTERN.finditer(body):
        if match.group("tag") != tag:
            continue
        records.append(parse_key_values(match.group("body")))
    if not records:
        raise ContractError(f"{tag} block 至少需要一个 [{tag}] 记录")
    return records


def require_keys(values: dict[str, str], keys: tuple[str, ...], scope: str) -> None:
    missing = [key for key in keys if not values.get(key)]
    if missing:
        raise ContractError(f"{scope} 缺少字段: {', '.join(missing)}")


def parse_bool(value: str, field: str) -> bool:
    if value.lower() not in {"true", "false"}:
        raise ContractError(f"{field} 必须是 true 或 false")
    return value.lower() == "true"


def validate_contract(values: dict[str, str]) -> None:
    require_keys(values, CONTRACT_KEYS, "design contract")
    if values["client_scope"] not in CLIENT_SCOPE_PREFIXES:
        raise ContractError(f"client_scope 不受支持: {values['client_scope']}")
    if values["change_mode"] not in ALLOWED_CONTRACT_MODES:
        raise ContractError(f"change_mode 不受支持: {values['change_mode']}")
    if values["status"] not in ALLOWED_CONTRACT_STATUSES:
        raise ContractError(f"status 不受支持: {values['status']}")
    if values["target_role"] not in ALLOWED_TARGET_ROLES:
        raise ContractError(f"target_role 不受支持: {values['target_role']}")
    if values["target_role"].lower() in {"content-authority", "source-of-truth", "product-source"}:
        raise ContractError("target_role 不能把当前 target Figma 声明为内容权威")
    target = values["target_figma"].strip().rstrip("/")
    for field in ("product_source", "brief_source", "terminology_source", "asset_registry", "brand_boundary"):
        if values[field].strip().rstrip("/") == target:
            raise ContractError(f"{field} 不能与 target_figma 相同")


def validate_pages(pages: list[dict[str, str]], client_scope: str) -> None:
    seen_ids: set[str] = set()
    seen_routes: set[str] = set()
    seen_names: set[str] = set()
    for index, page in enumerate(pages, start=1):
        require_keys(page, PAGE_KEYS, f"page[{index}]")
        if page["id"] in seen_ids:
            raise ContractError(f"page id 重复: {page['id']}")
        if page["route"] in seen_routes:
            raise ContractError(f"route 重复: {page['route']}")
        if page["figma_name"] in seen_names:
            raise ContractError(f"figma_name 重复: {page['figma_name']}")
        seen_ids.add(page["id"])
        seen_routes.add(page["route"])
        seen_names.add(page["figma_name"])
        name_match = FIGMA_NAME_PATTERN.fullmatch(page["figma_name"])
        if not name_match:
            raise ContractError(f"figma_name 不符合 Web 页面命名规范: {page['figma_name']}")
        if page["client_scope"] != client_scope:
            raise ContractError(f"page[{index}] client_scope 与 design contract 不一致")
        if page["status"] not in ALLOWED_PAGE_STATUSES:
            raise ContractError(f"page[{index}] status 不受支持: {page['status']}")
        if name_match.group("prefix").lower() != CLIENT_SCOPE_PREFIXES[client_scope].lower():
            raise ContractError(f"page[{index}] figma_name 与 client_scope 不一致")
        if name_match.group("status").lower() != page["status"]:
            raise ContractError(f"page[{index}] figma_name 与 status 不一致")
        is_current = parse_bool(page["is_current"], f"page[{index}].is_current")
        if page["status"] == "superseded" and is_current:
            raise ContractError(f"page[{index}] superseded 页面不能是 current")
        if "node-id=" not in page["source_node"] and "node:" not in page["source_node"]:
            raise ContractError(f"page[{index}] source_node 必须包含精确节点标识")
        states = [state.strip() for state in page["states"].split(",") if state.strip()]
        if "default" not in states:
            raise ContractError(f"page[{index}] states 必须包含 default")
        exclusions = (
            []
            if page["state_exclusions"].lower() == "none"
            else [state.strip() for state in page["state_exclusions"].split(",") if state.strip()]
        )
        unknown_exclusions = sorted(set(exclusions) - REQUIRED_STATE_COVERAGE)
        if unknown_exclusions:
            raise ContractError(
                f"page[{index}] state_exclusions 不受支持: {', '.join(unknown_exclusions)}"
            )
        covered = set(exclusions)
        for required_state in REQUIRED_STATE_COVERAGE:
            aliases = STATE_ALIASES.get(required_state, {required_state})
            if any(
                state in aliases or any(state.endswith(f"-{alias}") for alias in aliases)
                for state in states
            ):
                covered.add(required_state)
        missing_states = sorted(REQUIRED_STATE_COVERAGE - covered)
        if missing_states:
            raise ContractError(
                f"page[{index}] 状态覆盖缺少声明或排除: {', '.join(missing_states)}"
            )
        if not page["state_notes"].strip():
            raise ContractError(f"page[{index}] state_notes 不能为空")


def validate_navigation(navigation: list[dict[str, str]], pages: list[dict[str, str]]) -> None:
    page_by_id = {page["id"]: page for page in pages if page["is_current"].lower() == "true"}
    seen_ids: set[str] = set()
    for index, item in enumerate(navigation, start=1):
        require_keys(item, ("page_id", "route", "label"), f"navigation[{index}]")
        if item["page_id"] in seen_ids:
            raise ContractError(f"navigation page_id 重复: {item['page_id']}")
        seen_ids.add(item["page_id"])
        page = page_by_id.get(item["page_id"])
        if page is None:
            raise ContractError(f"navigation[{index}] 指向不存在的 current page: {item['page_id']}")
        if item["route"] != page["route"] or item["label"] != page["nav_label"]:
            raise ContractError(f"navigation[{index}] 与 page manifest 不一致: {item['page_id']}")
    if seen_ids != set(page_by_id):
        raise ContractError("navigation map 必须覆盖全部 current page")


def validate_evidence(body: str) -> dict[str, tuple[str, str]]:
    evidence: dict[str, tuple[str, str]] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = EVIDENCE_PATTERN.fullmatch(line)
        if not match:
            raise ContractError(f"无法解析 Figma evidence 行: {line}")
        field = match.group("field")
        if field in evidence:
            raise ContractError(f"Figma evidence 字段重复: {field}")
        status = match.group("status").strip().lower()
        reference = match.group("evidence").strip()
        if status not in ALLOWED_EVIDENCE_STATUSES:
            raise ContractError(f"{field} evidence status 不受支持: {status}")
        if not reference or reference.lower() in {"none", "n/a", "not-required"}:
            raise ContractError(f"{field} evidence 必须提供可复核引用")
        evidence[field] = (status, reference)
    missing = [field for field in EVIDENCE_FIELDS if field not in evidence]
    if missing:
        raise ContractError(f"Figma evidence 缺少字段: {', '.join(missing)}")
    return evidence


def validate_delivery_state(
    contract: dict[str, str], pages: list[dict[str, str]], evidence: dict[str, tuple[str, str]]
) -> None:
    if contract["status"] not in {"ready-for-code", "approved"}:
        return
    if contract["target_role"] != "approved-design":
        raise ContractError(f"{contract['status']} target_role 必须是 approved-design")
    unapproved_pages = [
        page["id"]
        for page in pages
        if page["is_current"].lower() == "true" and page["status"] != "approved"
    ]
    if unapproved_pages:
        raise ContractError(
            f"{contract['status']} contract 要求全部 current page 为 approved: {', '.join(unapproved_pages)}"
        )
    incomplete = [
        field
        for field, (status, _) in evidence.items()
        if status not in {"verified", "completed"} and not (field == "code_connect" and status == "not-applicable")
    ]
    if incomplete:
        raise ContractError(f"{contract['status']} evidence 尚未完成: {', '.join(incomplete)}")


def parse_plan(text: str) -> PlanParts:
    contract = parse_key_values(extract_block(text, "design-contract"))
    pages = parse_records(extract_block(text, "page-manifest"), "page")
    navigation = parse_records(extract_block(text, "navigation-map"), "item")
    evidence = validate_evidence(extract_block(text, "figma-evidence"))
    validate_contract(contract)
    validate_pages(pages, contract["client_scope"])
    validate_navigation(navigation, pages)
    validate_delivery_state(contract, pages, evidence)
    return PlanParts(contract, pages, navigation, evidence)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="local Markdown design plan")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.file)
    try:
        parse_plan(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ContractError) as error:
        print(f"FAIL Figma design plan {path}: {error}", file=sys.stderr)
        return 2
    print(f"PASS Figma design plan: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
