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
    "owner",
    "status",
)
MODULE_KEYS = (
    "id",
    "kind",
    "role",
    "required",
    "placement",
    "evidence",
    "owner",
    "page_role",
    "primary_question",
    "client_value",
    "content_depth",
    "handoff_to",
    "overlap_with",
    "overlap_disposition",
)
METRIC_KEYS = (
    "name",
    "business_meaning",
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
CONTENT_DEPTHS = {"summary", "decision-support", "detailed"}
OVERLAP_DISPOSITIONS = {"none", "keep-shared", "summarize", "deep-link", "merge", "remove"}
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


def extract_block(text: str, tag: str, *, optional: bool = False) -> str | None:
    blocks = [match.group("body") for match in BLOCK_PATTERN.finditer(text) if match.group("tag") == tag]
    if not blocks and optional:
        return None
    if len(blocks) != 1:
        raise WebsitePlanError(f"必须且只能有一个 {tag} block")
    return blocks[0]


def parse_records(body: str, kind: str, *, required: bool = True) -> list[dict[str, str]]:
    # 捕获组保留完整记录的正文，间隔中残留的标记意味着有记录缺少配对。
    segments = RECORD_PATTERNS[kind].split(body)
    for gap in segments[::2]:
        for line in gap.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if f"[{kind}]" in line or f"[/{kind}]" in line:
                raise WebsitePlanError(f"[{kind}] 与 [/{kind}] 须成对出现")
    records = [parse_key_values(record) for record in segments[1::2]]
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
    override = contract.get("design_carrier_override", "").strip().casefold()
    if not is_empty(override) and not override.startswith("user-specified-"):
        raise WebsitePlanError("design_carrier_override 必须使用 user-specified-* 记录使用者明确选择")


def validate_unique(records: list[dict[str, str]], key: str, scope: str) -> None:
    seen: set[str] = set()
    for record in records:
        value = record[key]
        if value in seen:
            raise WebsitePlanError(f"{scope} {key} 重复: {value}")
        seen.add(value)


def validate_modules(modules: list[dict[str, str]], plan_status: str) -> None:
    for index, module in enumerate(modules, start=1):
        scope = f"module[{module.get('id', index)}]"
        require_keys(module, MODULE_KEYS, scope)
        if module["kind"] not in MODULE_KINDS:
            raise WebsitePlanError(f"{scope} kind 必须是 suggested 或 conditional")
        if module["required"] not in {"true", "false"}:
            raise WebsitePlanError(f"{scope} required 必须是 true 或 false")
        for field in ("page_role", "primary_question", "client_value"):
            if is_empty(module[field]):
                raise WebsitePlanError(f"{scope} {field} 不能为空或占位")
        if module["content_depth"] not in CONTENT_DEPTHS:
            raise WebsitePlanError(f"{scope} content_depth 不受支持")
        if module["overlap_disposition"] not in OVERLAP_DISPOSITIONS:
            raise WebsitePlanError(f"{scope} overlap_disposition 不受支持")
    validate_unique(modules, "id", "module")

    module_ids = {module["id"] for module in modules}
    removed_ids = {module["id"] for module in modules if module["overlap_disposition"] == "remove"}
    detailed_questions: dict[str, list[str]] = {}
    for module in modules:
        scope = f"module[{module['id']}]"
        handoff_to = module["handoff_to"].strip()
        if handoff_to.casefold() != "none" and handoff_to not in module_ids:
            raise WebsitePlanError(f"{scope} handoff_to unknown module id: {handoff_to}")
        if plan_status == "ready-for-ui" and module["id"] not in removed_ids:
            unresolved = [field for field in ("evidence", "owner") if is_empty(module[field])]
            if unresolved:
                raise WebsitePlanError(f"{scope} 移交 UI 前须确认 {', '.join(unresolved)}")
            if handoff_to in removed_ids:
                raise WebsitePlanError(f"{scope} handoff_to 指向已移除的模块 {handoff_to}")
        overlap_refs = (
            []
            if module["overlap_with"].strip().casefold() == "none"
            else [item.strip() for item in module["overlap_with"].split(",") if item.strip()]
        )
        unknown = sorted(set(overlap_refs) - module_ids)
        if unknown:
            raise WebsitePlanError(f"{scope} overlap_with unknown module ids: {', '.join(unknown)}")
        disposition = module["overlap_disposition"]
        if overlap_refs and disposition == "none":
            raise WebsitePlanError(f"{scope} overlap_disposition 不能为 none")
        if not overlap_refs and disposition != "none":
            raise WebsitePlanError(f"{scope} 无 overlap_with 时 overlap_disposition 必须为 none")
        if module["content_depth"] == "detailed":
            question = module["primary_question"].strip().casefold()
            detailed_questions.setdefault(question, []).append(module["id"])

    for question, module_ids_for_question in detailed_questions.items():
        if len(module_ids_for_question) > 1:
            raise WebsitePlanError(
                "primary_question 重复且均为 detailed: "
                f"{question} ({', '.join(module_ids_for_question)})"
            )


def validate_metrics(metrics: list[dict[str, str]]) -> None:
    for index, metric in enumerate(metrics, start=1):
        scope = f"metric[{metric.get('name', index)}]"
        require_keys(metric, METRIC_KEYS, scope)
        if "reference_example_value" in metric and is_empty(metric["reference_example_value"]):
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


def viewport_set(value: str) -> set[str]:
    viewports = {part.strip().casefold() for part in value.split(",")}
    if any(is_empty(viewport) for viewport in viewports):
        raise WebsitePlanError("target_viewports 须列出约定的目标视口")
    return viewports


def validate_media(media: list[dict[str, str]], required_viewports: str | None) -> None:
    covered = set()
    for index, item in enumerate(media, start=1):
        scope = f"media[{item.get('id', index)}]"
        require_keys(item, MEDIA_KEYS, scope)
        if is_empty(item["source"]):
            raise WebsitePlanError(f"{scope} source 不能为空或占位")
        covered.update(viewport_set(item["target_viewports"]))
    validate_unique(media, "id", "media")
    if required_viewports is not None:
        missing = viewport_set(required_viewports) - covered
        if missing:
            raise WebsitePlanError("缺少已约定的媒体视口: " + ", ".join(sorted(missing)))
    elif media:
        if not any("mobile" in viewport or "h5" in viewport for viewport in covered):
            raise WebsitePlanError("responsive media target_viewports 必须包含 mobile 或 H5")
        if not any(any(size in viewport for size in ("1920", "2560", "3440", "ultrawide")) for viewport in covered):
            raise WebsitePlanError("responsive media target_viewports 必须包含大屏或超宽屏")


def validate_handoff(contract: dict[str, str], handoff: dict[str, str]) -> None:
    require_keys(handoff, HANDOFF_KEYS, "website handoff")
    owner_fields = [field for field in ("ui_owner", "engineering_owner", "acceptance_owner") if field in handoff]
    if not owner_fields or (contract["status"] == "ready-for-ui" and "ui_owner" not in handoff):
        raise WebsitePlanError("website handoff 缺少本轮承接人，移交 UI 时须填 ui_owner")
    for field in (*owner_fields, "stop_conditions"):
        if is_empty(handoff[field]):
            raise WebsitePlanError(f"website handoff {field} 不能为空或占位")
    carrier = contract.get("design_carrier", "").casefold()
    if carrier == "figma":
        require_keys(handoff, ("figma_write_authorization",), "website handoff")
    if handoff.get("design_carrier", "").casefold() != carrier:
        raise WebsitePlanError("website handoff design_carrier 与 contract 不一致")


def parse_plan(text: str) -> WebsitePlanParts:
    contract = parse_key_values(extract_block(text, "business-website-plan"))
    validate_contract(contract)
    modules = parse_records(extract_block(text, "website-modules"), "module")
    metric_block = extract_block(text, "metric-suggestions", optional=True)
    metrics = parse_records(metric_block, "metric") if metric_block is not None else []
    references_required = contract["reference_mode"] != "none"
    reference_block = extract_block(text, "reference-dna", optional=not references_required)
    references = parse_records(reference_block or "", "reference", required=references_required)
    media_block = extract_block(text, "responsive-media", optional=True)
    media = parse_records(media_block, "media") if media_block is not None else []
    handoff_block = extract_block(text, "website-handoff", optional=contract["status"] != "ready-for-ui")
    handoff = parse_key_values(handoff_block) if handoff_block is not None else {}
    validate_modules(modules, contract["status"])
    validate_metrics(metrics)
    validate_references(contract["reference_mode"], references)
    validate_media(media, contract.get("media_target_viewports"))
    if handoff_block is not None:
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
