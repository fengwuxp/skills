#!/usr/bin/env python3
"""Validate one local Business Website Contract.

The checker is offline and read-only. It validates structure and approved
planning invariants; it does not judge business truth, visual quality, legal
sufficiency, Figma state, implementation quality, or production readiness.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


BLOCK_PATTERN = re.compile(
    r"```(?P<tag>business-website-plan|website-modules|metric-suggestions|reference-dna|responsive-media|website-handoff)\s*\n"
    r"(?P<body>.*?)```",
    re.DOTALL,
)
RECORD_PATTERNS = {
    "module": re.compile(r"\[module\]\s*(?P<body>.*?)\s*\[/module\]", re.DOTALL),
    "metric": re.compile(r"\[metric\]\s*(?P<body>.*?)\s*\[/metric\]", re.DOTALL),
    "reference": re.compile(r"\[reference\]\s*(?P<body>.*?)\s*\[/reference\]", re.DOTALL),
    "media": re.compile(r"\[media\]\s*(?P<body>.*?)\s*\[/media\]", re.DOTALL),
}

CONTRACT_KEYS = (
    "plan_id",
    "business_authority",
    "business_type",
    "company_subject",
    "target_customers",
    "business_scope",
    "non_goals",
    "organization_mode",
    "reference_mode",
    "design_carrier",
    "design_carrier_override",
    "owner",
    "status",
)
MODULE_KEYS = ("id", "kind", "role", "required", "placement", "evidence", "owner")
METRIC_KEYS = (
    "name",
    "business_meaning",
    "reference_example_value",
    "owner_confirmed_value",
    "publish",
)
REFERENCE_KEYS = ("source", "read_status", "adopt", "reject", "limitations")
MEDIA_KEYS = (
    "id",
    "role",
    "source",
    "focal_point",
    "text_safe_area",
    "crop_variants",
    "target_viewports",
    "owner",
)
HANDOFF_KEYS = (
    "ui_owner",
    "design_carrier",
    "figma_write_authorization",
    "engineering_owner",
    "acceptance_owner",
    "legal_data_conditions",
    "stop_conditions",
)

EMPTY_MARKERS = {
    "",
    "none",
    "n/a",
    "na",
    "pending",
    "tbd",
    "todo",
    "unknown",
    "latest",
    "current",
    "待确认",
    "待定",
    "未知",
}
ORGANIZATION_MODES = {"single-page", "core-plus-conditional", "multi-business"}
REFERENCE_MODES = {"none", "public", "user-provided"}
PLAN_STATUSES = {"draft", "ready-for-owner", "ready-for-ui", "superseded"}
MODULE_KINDS = {"suggested", "conditional"}
READ_STATUSES = {"body-read", "body-read-with-limitations", "user-provided"}


class WebsitePlanError(ValueError):
    """A user-fixable Business Website Contract violation."""


@dataclass(frozen=True)
class WebsitePlanParts:
    contract: dict[str, str]
    modules: list[dict[str, str]]
    metrics: list[dict[str, str]]
    references: list[dict[str, str]]
    media: list[dict[str, str]]
    handoff: dict[str, str]


def parse_key_values(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise WebsitePlanError(f"无法解析字段行: {line}")
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            raise WebsitePlanError(f"字段名不规范: {key}")
        if key in values:
            raise WebsitePlanError(f"字段重复: {key}")
        values[key] = value.strip()
    return values


def extract_block(text: str, tag: str) -> str:
    blocks = [match.group("body") for match in BLOCK_PATTERN.finditer(text) if match.group("tag") == tag]
    if len(blocks) != 1:
        raise WebsitePlanError(f"必须且只能有一个 {tag} block")
    return blocks[0]


def parse_records(body: str, kind: str, *, required: bool = True) -> list[dict[str, str]]:
    records = [parse_key_values(match.group("body")) for match in RECORD_PATTERNS[kind].finditer(body)]
    if required and not records:
        raise WebsitePlanError(f"至少需要一个 [{kind}] 记录")
    return records


def require_keys(values: dict[str, str], keys: tuple[str, ...], scope: str) -> None:
    missing = [key for key in keys if not values.get(key)]
    if missing:
        raise WebsitePlanError(f"{scope} 缺少字段: {', '.join(missing)}")


def is_empty(value: str) -> bool:
    return value.strip().casefold() in EMPTY_MARKERS


def validate_contract(contract: dict[str, str]) -> None:
    require_keys(contract, CONTRACT_KEYS, "business website plan")
    for field in ("business_authority", "business_type", "company_subject", "target_customers", "business_scope", "owner"):
        if is_empty(contract[field]):
            raise WebsitePlanError(f"{field} is required and cannot be unresolved")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", contract["business_type"]):
        raise WebsitePlanError("business_type 必须使用 kebab-case")
    if contract["organization_mode"] not in ORGANIZATION_MODES:
        raise WebsitePlanError(f"organization_mode 不受支持: {contract['organization_mode']}")
    if contract["reference_mode"] not in REFERENCE_MODES:
        raise WebsitePlanError(f"reference_mode 不受支持: {contract['reference_mode']}")
    if contract["status"] not in PLAN_STATUSES:
        raise WebsitePlanError(f"status 不受支持: {contract['status']}")
    override = contract["design_carrier_override"].strip().casefold()
    if is_empty(override):
        if contract["design_carrier"] != "figma":
            raise WebsitePlanError("figma is the default design_carrier unless the user explicitly overrides it")
    elif not override.startswith("user-specified-"):
        raise WebsitePlanError("design_carrier_override 必须使用 user-specified-* 记录使用者明确选择")


def validate_unique(records: list[dict[str, str]], key: str, scope: str) -> None:
    seen: set[str] = set()
    for record in records:
        value = record[key]
        if value in seen:
            raise WebsitePlanError(f"{scope} {key} 重复: {value}")
        seen.add(value)


def validate_modules(modules: list[dict[str, str]]) -> None:
    for index, module in enumerate(modules, start=1):
        scope = f"module[{module.get('id', index)}]"
        require_keys(module, MODULE_KEYS, scope)
        if module["kind"] not in MODULE_KINDS:
            raise WebsitePlanError(f"{scope} kind 必须是 suggested 或 conditional")
        if module["required"] not in {"true", "false"}:
            raise WebsitePlanError(f"{scope} required 必须是 true 或 false")
    validate_unique(modules, "id", "module")


def validate_metrics(metrics: list[dict[str, str]]) -> None:
    for index, metric in enumerate(metrics, start=1):
        scope = f"metric[{metric.get('name', index)}]"
        require_keys(metric, METRIC_KEYS, scope)
        if is_empty(metric["reference_example_value"]):
            raise WebsitePlanError(f"metric[{metric['name']}] reference_example_value 不能为空或占位")
        if metric["publish"] not in {"true", "false"}:
            raise WebsitePlanError(f"{scope} publish 必须是 true 或 false")
        if metric["publish"] == "true" and is_empty(metric["owner_confirmed_value"]):
            raise WebsitePlanError(f"metric[{metric['name']}] cannot publish an unconfirmed reference example")
    validate_unique(metrics, "name", "metric")


def validate_references(reference_mode: str, references: list[dict[str, str]]) -> None:
    if reference_mode == "none" and references:
        raise WebsitePlanError("reference_mode none 不能包含 reference 记录")
    for index, reference in enumerate(references, start=1):
        scope = f"reference[{index}]"
        require_keys(reference, REFERENCE_KEYS, scope)
        for field in ("source", "adopt", "reject"):
            if is_empty(reference[field]):
                raise WebsitePlanError(f"{scope} {field} 不能为空或占位")
        if reference["read_status"] not in READ_STATUSES:
            raise WebsitePlanError(f"{scope} read_status 不受支持")
        if reference_mode == "public" and reference["read_status"] == "user-provided":
            raise WebsitePlanError(f"{scope} public reference 必须实际读取正文")
    validate_unique(references, "source", "reference")


def validate_media(media: list[dict[str, str]]) -> None:
    viewports: list[str] = []
    for index, item in enumerate(media, start=1):
        scope = f"media[{item.get('id', index)}]"
        require_keys(item, MEDIA_KEYS, scope)
        if is_empty(item["source"]):
            raise WebsitePlanError(f"{scope} source 不能为空或占位")
        viewports.extend(part.strip().casefold() for part in item["target_viewports"].split(","))
    validate_unique(media, "id", "media")
    if not any("mobile" in viewport or "h5" in viewport for viewport in viewports):
        raise WebsitePlanError("responsive media target_viewports 必须包含 mobile 或 H5")
    if not any(any(size in viewport for size in ("1920", "2560", "3440", "ultrawide")) for viewport in viewports):
        raise WebsitePlanError("responsive media target_viewports 必须包含大屏或超宽屏")


def validate_handoff(contract: dict[str, str], handoff: dict[str, str]) -> None:
    require_keys(handoff, HANDOFF_KEYS, "website handoff")
    for field in ("ui_owner", "engineering_owner", "acceptance_owner", "stop_conditions"):
        if is_empty(handoff[field]):
            raise WebsitePlanError(f"website handoff {field} 不能为空或占位")
    if handoff["design_carrier"] != contract["design_carrier"]:
        raise WebsitePlanError("website handoff design_carrier 与 contract 不一致")


def parse_plan(text: str) -> WebsitePlanParts:
    contract = parse_key_values(extract_block(text, "business-website-plan"))
    validate_contract(contract)
    modules = parse_records(extract_block(text, "website-modules"), "module")
    metrics = parse_records(extract_block(text, "metric-suggestions"), "metric")
    references = parse_records(
        extract_block(text, "reference-dna"),
        "reference",
        required=contract["reference_mode"] != "none",
    )
    media = parse_records(extract_block(text, "responsive-media"), "media")
    handoff = parse_key_values(extract_block(text, "website-handoff"))
    validate_modules(modules)
    validate_metrics(metrics)
    validate_references(contract["reference_mode"], references)
    validate_media(media)
    validate_handoff(contract, handoff)
    return WebsitePlanParts(contract, modules, metrics, references, media, handoff)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="local Markdown Business Website Contract")
    path = Path(parser.parse_args().file)
    try:
        parse_plan(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, WebsitePlanError) as error:
        print(f"FAIL business website plan {path}: {error}", file=sys.stderr)
        return 2
    print(f"VALID business website plan: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
