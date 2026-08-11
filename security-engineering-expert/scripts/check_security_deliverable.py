#!/usr/bin/env python3
"""Check the minimum contract of a security engineering deliverable.

The checker reads one explicit local file or stdin. It never writes files,
uses the network, reads secrets, judges semantic relevance, performs an
independent control assessment, or authorizes a system.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECTION_FIELDS = {
    "范围与证据": (
        "范围",
        "环境",
        "准出目标",
        "证据来源",
        "安全工程 Owner",
        "独立评估 Owner",
        "授权 Owner",
        "非目标",
    ),
    "资产与资损": ("资产", "资损"),
    "主体与信任边界": ("主体", "信任边界"),
    "保护需求与安全要求": ("保护需求", "安全要求", "验收条件"),
    "威胁与滥用路径": ("风险", "前提", "路径", "后果"),
    "控制与恢复": ("控制", "控制失效与旁路", "预防", "检测", "响应", "恢复"),
    "验证证据": ("安全声明", "证据", "验证方式", "结果", "证据位置"),
    "风险控制证据追踪": (),
    "残余风险与工程建议": (
        "残余风险",
        "风险 Owner",
        "截止时间",
        "复核触发器",
        "未闭合阻断项",
        "停止条件",
        "工程建议",
    ),
}

TARGET_LEVELS = {
    "DESIGN_D1": 1,
    "IMPLEMENTATION_D2": 2,
    "ENABLEMENT_D3": 3,
    "RUNTIME_D4": 4,
    "PRODUCTION_D5": 5,
}
EVIDENCE_LEVELS = {
    "D1_DESIGN": 1,
    "D2_IMPLEMENTATION": 2,
    "D3_ENABLED": 3,
    "D4_RUNTIME": 4,
    "D5_PRODUCTION": 5,
}
VALID_RECOMMENDATIONS = {
    "ENGINEERING_READY",
    "ENGINEERING_READY_WITH_RISK",
    "ENGINEERING_BLOCKED",
}
VALID_PRIORITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
VALID_TRACE_STATUSES = {"CLOSED", "CONDITIONAL", "OPEN"}
NON_BLOCKED_RESOLVED_FIELDS = (
    ("范围与证据", "环境"),
    ("范围与证据", "证据来源"),
    ("范围与证据", "安全工程 Owner"),
    ("范围与证据", "独立评估 Owner"),
    ("范围与证据", "授权 Owner"),
    ("验证证据", "结果"),
    ("验证证据", "证据位置"),
    ("残余风险与工程建议", "风险 Owner"),
    ("残余风险与工程建议", "截止时间"),
    ("残余风险与工程建议", "复核触发器"),
)
TRACE_HEADERS = (
    "风险 ID",
    "优先级",
    "保护需求 ID",
    "安全要求 ID",
    "控制 ID",
    "控制 Owner",
    "声明 ID",
    "证据 ID",
    "实际证据等级",
    "状态",
)
ID_PATTERNS = {
    "RISK": re.compile(r"\bRISK-[A-Z0-9][A-Z0-9-]*\b"),
    "PN": re.compile(r"\bPN-[A-Z0-9][A-Z0-9-]*\b"),
    "SR": re.compile(r"\bSR-[A-Z0-9][A-Z0-9-]*\b"),
    "CTRL": re.compile(r"\bCTRL-[A-Z0-9][A-Z0-9-]*\b"),
    "CLAIM": re.compile(r"\bCLAIM-[A-Z0-9][A-Z0-9-]*\b"),
    "EVID": re.compile(r"\bEVID-[A-Z0-9][A-Z0-9-]*\b"),
}
PLACEHOLDER_SUFFIXES = ("已填写", "已补充", "待填写", "待补充")
BLOCKING_PREFIXES = (
    "no evidence",
    "not implemented",
    "not enabled",
    "not verified",
    "unverified",
    "failed",
    "fail",
    "无证据",
    "无可复核证据",
    "未实现",
    "未启用",
    "未验证",
    "失败",
    "不通过",
)
ENGLISH_UNRESOLVED_MARKER = re.compile(
    r"(?<![A-Za-z0-9_./-])(?:PENDING|TBD|TODO|UNKNOWN)(?![A-Za-z0-9_./-])"
)
CHINESE_UNRESOLVED_MARKER = re.compile(r"(?:待确认|待定|待填写|待补充)")
CHINESE_UNKNOWN_MARKER = re.compile(
    r"(?<![/._-])(?:未知|未明确)(?![\u3400-\u9fffA-Za-z0-9_./-])"
)
CHINESE_UNKNOWN_FIELDS = {
    "范围",
    "环境",
    "证据来源",
    "安全工程 Owner",
    "独立评估 Owner",
    "授权 Owner",
    "资产",
    "资损",
    "信任边界",
    "控制",
    "控制失效与旁路",
    "预防",
    "检测",
    "响应",
    "恢复",
    "证据",
    "验证方式",
    "结果",
    "证据位置",
    "风险 Owner",
    "截止时间",
    "复核触发器",
    "未闭合阻断项",
    "停止条件",
}
STATE_ENUM_CONTEXT = re.compile(
    r"(?i)(?:`(?:pending|unknown)`\s*(?:业务|对象|领域)状态(?:枚举)?|(?:业务|对象|领域)状态(?:枚举)?\s*(?:为|=|:|：)?\s*`(?:pending|unknown)`)"
)
STATE_ENUM_FIELDS = {
    "资产",
    "安全要求",
    "验收条件",
    "风险",
    "前提",
    "路径",
    "后果",
    "安全声明",
}
LEGACY_CONCLUSION = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:结论|安全结论|准出结论|发布结论|上线结论|工程建议)\s*[：:]\s*(?:READY_WITH_RISK|READY|BLOCKED)\b"
)
FIELD_BLOCKING_PATTERNS = {
    "证据来源": (r"^(?:当前)?(?:没有|无)(?:任何)?可复核证据(?:$|[，,。.;；])",),
    "安全工程 Owner": (r"^(?:当前)?(?:无人负责|没有负责人|无负责人)(?:$|[，,。.;；])",),
    "独立评估 Owner": (r"^(?:当前)?(?:无人负责|没有负责人|无负责人)(?:$|[，,。.;；])",),
    "授权 Owner": (r"^(?:当前)?(?:无人负责|没有负责人|无负责人)(?:$|[，,。.;；])",),
    "风险 Owner": (r"^(?:当前)?(?:无人负责|没有负责人|无负责人)(?:$|[，,。.;；])",),
    "结果": (
        r"^(?:当前)?(?:测试|验证|演练|控制)(?:结果)?(?:仍|尚)?(?:失败|未通过|未生效)(?:$|[，,。.;；])",
    ),
}


def enum_value(value: str | None) -> str | None:
    return value.strip().rstrip(".。").upper() if value else None


def owner_identity(value: str) -> str:
    return re.sub(r"[\s,，.。;；:：]+$", "", value).strip().casefold()


def sections(text: str) -> dict[str, str]:
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            heading = match.group(1)
            current = heading if heading in SECTION_FIELDS else None
            if current:
                found.setdefault(current, [])
        elif current:
            found[current].append(line)
    return {heading: "\n".join(body).strip() for heading, body in found.items()}


def field_value(body: str, field: str) -> str | None:
    match = re.search(
        rf"(?m)^\s*(?:[-*]\s*)?{re.escape(field)}\s*[：:]\s*(\S.*)$",
        body,
    )
    return match.group(1).strip() if match else None


def is_placeholder_value(value: str, field: str) -> bool:
    raw = value.strip().casefold()
    if raw in {"...", "…", "n/a", "na", "placeholder"}:
        return True
    normalized = re.sub(r"[\s.。:：]+", "", value).casefold()
    normalized_field = re.sub(r"\s+", "", field).casefold()
    return any(
        normalized == normalized_field + suffix for suffix in PLACEHOLDER_SUFFIXES
    )


def unresolved_candidate(value: str, field: str) -> str:
    return STATE_ENUM_CONTEXT.sub("", value) if field in STATE_ENUM_FIELDS else value


def has_unresolved_marker(value: str, field: str, *, strict_unknown: bool = False) -> bool:
    candidate = unresolved_candidate(value, field)
    return bool(
        ENGLISH_UNRESOLVED_MARKER.search(candidate)
        or CHINESE_UNRESOLVED_MARKER.search(candidate)
        or (
            (strict_unknown or field in CHINESE_UNKNOWN_FIELDS)
            and CHINESE_UNKNOWN_MARKER.search(candidate)
        )
    )


def is_blocking_value(value: str, field: str) -> bool:
    normalized = value.strip().casefold()
    separators = " \t:：,，.。;；([（"
    has_blocking_prefix = any(
        normalized == prefix
        or (
            normalized.startswith(prefix)
            and len(normalized) > len(prefix)
            and normalized[len(prefix)] in separators
        )
        for prefix in BLOCKING_PREFIXES
    )
    return (
        has_blocking_prefix
        or has_unresolved_marker(value, field)
        or any(
            re.search(pattern, normalized)
            for pattern in FIELD_BLOCKING_PATTERNS.get(field, ())
        )
    )


def is_none_value(value: str | None) -> bool:
    return enum_value(value) == "NONE"


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def trace_rows(body: str) -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    lines = [line for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return [], ["风险控制证据追踪: missing header, separator, or data row"]

    headers = split_table_row(lines[0])
    if tuple(headers) != TRACE_HEADERS:
        failures.append(
            "风险控制证据追踪: headers must be " + ", ".join(TRACE_HEADERS)
        )
        return [], failures
    separator = split_table_row(lines[1])
    if len(separator) != len(headers) or not is_table_separator(separator):
        failures.append("风险控制证据追踪: invalid markdown table separator")
        return [], failures

    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(lines[2:], start=1):
        cells = split_table_row(line)
        if len(cells) != len(headers):
            failures.append(
                f"风险控制证据追踪: row {line_number} has {len(cells)} cells, expected {len(headers)}"
            )
            continue
        row = dict(zip(headers, cells, strict=True))
        for header, value in row.items():
            if not value or is_placeholder_value(value, header):
                failures.append(
                    f"风险控制证据追踪: row {line_number} missing resolved {header}"
                )
        rows.append(row)
    return rows, failures


def ids(value: str, kind: str) -> set[str]:
    return set(ID_PATTERNS[kind].findall(value.upper()))


def validate_trace_rows(parsed: dict[str, str]) -> tuple[list[dict[str, str]], list[str]]:
    rows, failures = trace_rows(parsed.get("风险控制证据追踪", ""))
    declared = {
        "RISK": ids(parsed.get("威胁与滥用路径", ""), "RISK"),
        "PN": ids(parsed.get("保护需求与安全要求", ""), "PN"),
        "SR": ids(parsed.get("保护需求与安全要求", ""), "SR"),
        "CTRL": ids(parsed.get("控制与恢复", ""), "CTRL"),
        "CLAIM": ids(parsed.get("验证证据", ""), "CLAIM"),
        "EVID": ids(parsed.get("验证证据", ""), "EVID"),
    }
    id_columns = {
        "风险 ID": "RISK",
        "保护需求 ID": "PN",
        "安全要求 ID": "SR",
        "控制 ID": "CTRL",
        "声明 ID": "CLAIM",
        "证据 ID": "EVID",
    }
    traced = {kind: set() for kind in ID_PATTERNS}
    seen_risks: set[str] = set()

    for row_number, row in enumerate(rows, start=1):
        for column, kind in id_columns.items():
            referenced = ids(row[column], kind)
            if not referenced:
                failures.append(
                    f"风险控制证据追踪: row {row_number} {column} requires {kind}-* ID"
                )
                continue
            traced[kind].update(referenced)
            missing = referenced - declared[kind]
            if missing:
                failures.append(
                    f"风险控制证据追踪: row {row_number} {column} references undeclared {', '.join(sorted(missing))}"
                )
        risk_ids = ids(row["风险 ID"], "RISK")
        if len(risk_ids) != 1:
            failures.append(
                f"风险控制证据追踪: row {row_number} must describe exactly one risk"
            )
        elif seen_risks & risk_ids:
            failures.append(
                f"风险控制证据追踪: duplicate risk row {next(iter(risk_ids))}"
            )
        seen_risks.update(risk_ids)

        if enum_value(row["优先级"]) not in VALID_PRIORITIES:
            failures.append(
                f"风险控制证据追踪: row {row_number} invalid 优先级"
            )
        if enum_value(row["实际证据等级"]) not in EVIDENCE_LEVELS:
            failures.append(
                f"风险控制证据追踪: row {row_number} invalid 实际证据等级"
            )
        if enum_value(row["状态"]) not in VALID_TRACE_STATUSES:
            failures.append(f"风险控制证据追踪: row {row_number} invalid 状态")
        if is_blocking_value(row["控制 Owner"], "风险 Owner"):
            failures.append(
                f"风险控制证据追踪: row {row_number} unresolved 控制 Owner"
            )
        for column, value in row.items():
            if has_unresolved_marker(value, column, strict_unknown=True):
                failures.append(
                    f"风险控制证据追踪: row {row_number} unresolved {column}"
                )

    for kind, declared_ids in declared.items():
        missing_from_trace = declared_ids - traced[kind]
        if missing_from_trace:
            failures.append(
                f"风险控制证据追踪: declared {kind}-* IDs missing from trace: "
                + ", ".join(sorted(missing_from_trace))
            )

    return rows, failures


def audit(text: str) -> list[str]:
    failures: list[str] = []
    if LEGACY_CONCLUSION.search(text):
        failures.append(
            "legacy READY/READY_WITH_RISK/BLOCKED conclusion is not allowed; use ENGINEERING_* only"
        )
    parsed = sections(text)
    for heading, fields in SECTION_FIELDS.items():
        body = parsed.get(heading)
        if body is None:
            failures.append(f"missing section: {heading}")
            continue
        for field in fields:
            value = field_value(body, field)
            if not value:
                failures.append(f"{heading}: missing non-blank field {field}")
            elif is_placeholder_value(value, field):
                failures.append(f"{heading}: placeholder value for {field}")

    rows, trace_failures = validate_trace_rows(parsed)
    failures.extend(trace_failures)

    range_body = parsed.get("范围与证据", "")
    owner_values = [
        field_value(range_body, field)
        for field in ("安全工程 Owner", "独立评估 Owner", "授权 Owner")
    ]
    if all(owner_values) and len({owner_identity(value) for value in owner_values if value}) != 3:
        failures.append(
            "范围与证据: 安全工程 Owner, 独立评估 Owner, and 授权 Owner must be pairwise distinct"
        )
    target = enum_value(field_value(range_body, "准出目标"))
    if target and target not in TARGET_LEVELS:
        failures.append(
            "范围与证据: 准出目标 must be DESIGN_D1, IMPLEMENTATION_D2, ENABLEMENT_D3, RUNTIME_D4, or PRODUCTION_D5"
        )

    recommendation_body = parsed.get("残余风险与工程建议", "")
    recommendation = enum_value(field_value(recommendation_body, "工程建议"))
    if recommendation and recommendation not in VALID_RECOMMENDATIONS:
        failures.append(
            "残余风险与工程建议: 工程建议 must be ENGINEERING_READY, ENGINEERING_READY_WITH_RISK, or ENGINEERING_BLOCKED"
        )

    blockers = field_value(recommendation_body, "未闭合阻断项")
    non_blocked = recommendation in {
        "ENGINEERING_READY",
        "ENGINEERING_READY_WITH_RISK",
    }
    if non_blocked:
        for heading, fields in SECTION_FIELDS.items():
            for field in fields:
                value = field_value(parsed.get(heading, ""), field)
                if value and has_unresolved_marker(value, field):
                    failures.append(
                        f"{heading}: {recommendation} conflicts with unresolved field {field}"
                    )
        for row_number, row in enumerate(rows, start=1):
            for column, value in row.items():
                if has_unresolved_marker(value, column, strict_unknown=True):
                    failures.append(
                        f"风险控制证据追踪: row {row_number} {recommendation} conflicts with unresolved {column}"
                    )
        for heading, field in NON_BLOCKED_RESOLVED_FIELDS:
            value = field_value(parsed.get(heading, ""), field)
            if value and is_blocking_value(value, field):
                failures.append(
                    f"{heading}: {recommendation} conflicts with unresolved field {field}"
                )
        if not is_none_value(blockers):
            failures.append(
                f"残余风险与工程建议: {recommendation} requires 未闭合阻断项 NONE"
            )
        if target in TARGET_LEVELS:
            for row_number, row in enumerate(rows, start=1):
                level = enum_value(row["实际证据等级"])
                if level in EVIDENCE_LEVELS and EVIDENCE_LEVELS[level] < TARGET_LEVELS[target]:
                    failures.append(
                        f"风险控制证据追踪: row {row_number} evidence {level} is below target {target}"
                    )
                status = enum_value(row["状态"])
                if status == "OPEN":
                    failures.append(
                        f"风险控制证据追踪: row {row_number} OPEN conflicts with {recommendation}"
                    )
                if recommendation == "ENGINEERING_READY" and status == "CONDITIONAL":
                    failures.append(
                        f"风险控制证据追踪: row {row_number} CONDITIONAL requires ENGINEERING_READY_WITH_RISK"
                    )

    if recommendation == "ENGINEERING_READY" and not is_none_value(
        field_value(recommendation_body, "残余风险")
    ):
        failures.append(
            "残余风险与工程建议: ENGINEERING_READY requires 残余风险 NONE"
        )

    if recommendation == "ENGINEERING_READY_WITH_RISK":
        if rows and not any(enum_value(row["状态"]) == "CONDITIONAL" for row in rows):
            failures.append(
                "残余风险与工程建议: ENGINEERING_READY_WITH_RISK requires at least one CONDITIONAL risk"
            )
        for field in ("残余风险", "风险 Owner", "截止时间", "复核触发器"):
            value = field_value(recommendation_body, field)
            if not value or is_none_value(value) or is_placeholder_value(value, field) or is_blocking_value(value, field):
                failures.append(
                    f"残余风险与工程建议: ENGINEERING_READY_WITH_RISK requires resolved field {field}"
                )

    if recommendation == "ENGINEERING_BLOCKED":
        has_open_risk = any(enum_value(row["状态"]) == "OPEN" for row in rows)
        has_low_evidence = bool(
            target in TARGET_LEVELS
            and any(
                enum_value(row["实际证据等级"]) in EVIDENCE_LEVELS
                and EVIDENCE_LEVELS[enum_value(row["实际证据等级"])] < TARGET_LEVELS[target]
                for row in rows
            )
        )
        if is_none_value(blockers) and not has_open_risk and not has_low_evidence:
            failures.append(
                "残余风险与工程建议: ENGINEERING_BLOCKED requires an explicit blocker, OPEN risk, or evidence below target"
            )
    return failures


def valid_sample() -> str:
    return """# 开放平台安全评审

## 范围与证据
- 范围：商户 OAuth 接入与回调链路。
- 环境：生产候选版本 2.1；法律适用性不在本轮安全工程建议范围。
- 准出目标：RUNTIME_D4
- 证据来源：接口契约、配置回读、测试报告和告警演练记录。
- 安全工程 Owner：平台安全架构负责人。
- 独立评估 Owner：平台安全评估组。
- 授权 Owner：生产变更委员会负责人。
- 非目标：法律合规结论和生产授权。

## 资产与资损
- 资产：商户身份、授权码、token 与交易指令。
- 资损：账户接管后伪造指令并扩大资金损失。

## 主体与信任边界
- 主体：商户管理员、平台服务、授权服务器和第三方客户端。
- 信任边界：浏览器、商户后端、平台网关与授权服务器之间。

## 保护需求与安全要求
- 保护需求：PN-001 防止授权码被非预期客户端兑换。
- 安全要求：SR-001 授权服务器只接受登记且精确匹配的 redirect URI，并绑定 PKCE。
- 验收条件：篡改 redirect URI 或缺少正确 verifier 的请求必须失败。

## 威胁与滥用路径
- 风险：RISK-001 攻击者篡改回调地址并截获授权码。
- 前提：攻击者取得弱保护的 redirect URI 配置权限。
- 路径：跨越商户配置与授权服务器边界，截获授权码后换取 token。
- 后果：冒用商户身份访问受保护能力。

## 控制与恢复
- 控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。
- 控制失效与旁路：配置通配、历史客户端豁免或 verifier 未校验会绕过控制。
- 预防：默认拒绝未登记回调和不完整 PKCE 请求。
- 检测：关联异常授权、回调变更和 token 使用告警。
- 响应：吊销 token、冻结客户端并保全审计证据。
- 恢复：轮换凭证，复核授权并回归验证。

## 验证证据
- 安全声明：CLAIM-001 回调篡改和错误 verifier 在目标环境均被拒绝。
- 证据：EVID-001 生产候选版本负向互操作测试与告警演练记录。
- 验证方式：负向互操作测试、配置回读和告警演练。
- 结果：重定向篡改被拒绝，告警在目标时限内触发。
- 证据位置：security-evidence/oauth-review-2.1.md。

## 风险控制证据追踪
| 风险 ID | 优先级 | 保护需求 ID | 安全要求 ID | 控制 ID | 控制 Owner | 声明 ID | 证据 ID | 实际证据等级 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | HIGH | PN-001 | SR-001 | CTRL-001 | 平台安全负责人 | CLAIM-001 | EVID-001 | D4_RUNTIME | CONDITIONAL |

## 残余风险与工程建议
- 残余风险：第三方终端失陷仍需商户侧控制。
- 风险 Owner：平台安全负责人。
- 截止时间：2026-09-30。
- 复核触发器：依赖、权限模型或目标环境发生变化。
- 未闭合阻断项：NONE
- 停止条件：目标环境配置无法回读或吊销演练失败。
- 工程建议：ENGINEERING_READY_WITH_RISK
"""


def self_test() -> None:
    sample = valid_sample()
    if audit(sample):
        raise SystemExit(f"self-test failed: valid sample rejected: {audit(sample)}")

    owner_overlap_error = (
        "范围与证据: 安全工程 Owner, 独立评估 Owner, and 授权 Owner must be pairwise distinct"
    )
    owner_overlap_cases = {
        "all owners": sample.replace(
            "独立评估 Owner：平台安全评估组。",
            "独立评估 Owner：平台安全架构负责人。",
        ).replace(
            "授权 Owner：生产变更委员会负责人。",
            "授权 Owner：平台安全架构负责人。",
        ),
        "security and assessment owners": sample.replace(
            "独立评估 Owner：平台安全评估组。",
            "独立评估 Owner：平台安全架构负责人。",
        ),
        "security and authorization owners": sample.replace(
            "授权 Owner：生产变更委员会负责人。",
            "授权 Owner：平台安全架构负责人。",
        ),
        "assessment and authorization owners": sample.replace(
            "授权 Owner：生产变更委员会负责人。",
            "授权 Owner：平台安全评估组。",
        ),
    }
    for overlap, invalid_sample in owner_overlap_cases.items():
        if owner_overlap_error not in audit(invalid_sample):
            raise SystemExit(f"self-test failed: overlapping {overlap} accepted")

    missing = sample.replace("## 控制与恢复", "## 其他")
    if not any("missing section: 控制与恢复" in item for item in audit(missing)):
        raise SystemExit("self-test failed: missing control section accepted")

    blank = sample.replace("- 资损：账户接管后伪造指令并扩大资金损失。", "- 资损：")
    if not any("missing non-blank field 资损" in item for item in audit(blank)):
        raise SystemExit("self-test failed: blank loss field accepted")

    legacy_gate = sample.replace("ENGINEERING_READY_WITH_RISK", "READY_WITH_RISK")
    if not any("工程建议 must be" in item for item in audit(legacy_gate)):
        raise SystemExit("self-test failed: authorization-ambiguous gate accepted")

    hidden_legacy_gate = sample + "\n结论：READY\n"
    if not any("legacy READY" in item for item in audit(hidden_legacy_gate)):
        raise SystemExit("self-test failed: hidden legacy READY conclusion accepted")

    low_evidence = sample.replace("D4_RUNTIME | CONDITIONAL", "D1_DESIGN | CONDITIONAL")
    if not any("below target RUNTIME_D4" in item for item in audit(low_evidence)):
        raise SystemExit("self-test failed: D1 evidence accepted for runtime target")

    pending_owner = sample.replace(
        "平台安全架构负责人。", "平台安全架构负责人，审批仍 PENDING。"
    )
    if not any("unresolved field 安全工程 Owner" in item for item in audit(pending_owner)):
        raise SystemExit("self-test failed: suffixed PENDING owner accepted")

    pending_result = sample.replace(
        "重定向篡改被拒绝，告警在目标时限内触发。",
        "已有部分结果，但运行证据 PENDING，待补齐。",
    )
    if not any("unresolved field 结果" in item for item in audit(pending_result)):
        raise SystemExit("self-test failed: embedded PENDING result accepted")

    pending_critical_fields = {
        "资产": sample.replace(
            "资产：商户身份、授权码、token 与交易指令。", "资产：PENDING"
        ),
        "控制": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 控制实现 PENDING",
        ),
        "恢复": sample.replace(
            "恢复：轮换凭证，复核授权并回归验证。", "恢复：PENDING"
        ),
    }
    for field, pending_case in pending_critical_fields.items():
        if not any(f"unresolved field {field}" in item for item in audit(pending_case)):
            raise SystemExit(f"self-test failed: PENDING {field} accepted")

    undeclared_mapping = sample.replace(
        "| RISK-001 | HIGH | PN-001 | SR-001 | CTRL-001 |",
        "| RISK-001 | HIGH | PN-001 | SR-999 | CTRL-001 |",
    )
    if not any("references undeclared SR-999" in item for item in audit(undeclared_mapping)):
        raise SystemExit("self-test failed: undeclared risk mapping accepted")

    unmapped_declarations = {
        "RISK-002": sample.replace(
            "风险：RISK-001 攻击者篡改回调地址并截获授权码。",
            "风险：RISK-001 攻击者篡改回调地址并截获授权码；RISK-002 未映射风险。",
        ),
        "PN-002": sample.replace(
            "保护需求：PN-001 防止授权码被非预期客户端兑换。",
            "保护需求：PN-001 防止授权码被非预期客户端兑换；PN-002 防止令牌泄露。",
        ),
        "CLAIM-002": sample.replace(
            "安全声明：CLAIM-001 回调篡改和错误 verifier 在目标环境均被拒绝。",
            "安全声明：CLAIM-001 回调篡改和错误 verifier 在目标环境均被拒绝；CLAIM-002 令牌不可重放。",
        ),
    }
    for missing_id, unmapped_case in unmapped_declarations.items():
        if not any(missing_id in item and "missing from trace" in item for item in audit(unmapped_case)):
            raise SystemExit(f"self-test failed: unmapped declaration {missing_id} accepted")

    open_ready = sample.replace("D4_RUNTIME | CONDITIONAL", "D4_RUNTIME | OPEN")
    if not any("OPEN conflicts" in item for item in audit(open_ready)):
        raise SystemExit("self-test failed: OPEN risk accepted as ready")

    design_ready = (
        sample.replace("RUNTIME_D4", "DESIGN_D1")
        .replace("D4_RUNTIME | CONDITIONAL", "D1_DESIGN | CLOSED")
        .replace("第三方终端失陷仍需商户侧控制。", "NONE")
        .replace("ENGINEERING_READY_WITH_RISK", "ENGINEERING_READY")
    )
    if audit(design_ready):
        raise SystemExit(f"self-test failed: valid DESIGN_D1 ready rejected: {audit(design_ready)}")

    ready_with_residual_risk = design_ready.replace(
        "残余风险：NONE",
        "残余风险：第三方终端失陷仍需商户侧控制。",
    )
    ready_residual_error = (
        "残余风险与工程建议: ENGINEERING_READY requires 残余风险 NONE"
    )
    if ready_residual_error not in audit(ready_with_residual_risk):
        raise SystemExit(
            "self-test failed: ENGINEERING_READY accepted a CLOSED non-NONE residual risk"
        )

    legitimate_threat_wording = design_ready.replace(
        "防止授权码被非预期客户端兑换。",
        "防止授权码被未知客户端兑换。",
    )
    if audit(legitimate_threat_wording):
        raise SystemExit(
            "self-test failed: threat wording was mistaken for unresolved state: "
            f"{audit(legitimate_threat_wording)}"
        )

    legitimate_pending_state = design_ready.replace(
        "授权服务器只接受登记且精确匹配的 redirect URI，并绑定 PKCE。",
        "提现指令的业务状态为 `PENDING` 时不得进入放款。",
    )
    if audit(legitimate_pending_state):
        raise SystemExit(
            "self-test failed: code-formatted PENDING state was mistaken for unresolved work: "
            f"{audit(legitimate_pending_state)}"
        )

    legitimate_pending_prefix = design_ready.replace(
        "授权服务器只接受登记且精确匹配的 redirect URI，并绑定 PKCE。",
        "`PENDING` 业务状态的提现指令不得进入放款。",
    )
    if audit(legitimate_pending_prefix):
        raise SystemExit(
            "self-test failed: prefixed business PENDING state was rejected: "
            f"{audit(legitimate_pending_prefix)}"
        )

    hidden_backtick_work = {
        "安全工程 Owner": sample.replace(
            "安全工程 Owner：平台安全架构负责人。", "安全工程 Owner：`PENDING`"
        ),
        "控制": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 `TODO`",
        ),
        "结果": sample.replace(
            "重定向篡改被拒绝，告警在目标时限内触发。",
            "运行证据 `PENDING`",
        ),
        "控制状态": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 控制状态为 `PENDING`",
        ),
        "验证状态": sample.replace(
            "重定向篡改被拒绝，告警在目标时限内触发。",
            "验证状态为 `PENDING`",
        ),
        "风险评审状态": sample.replace(
            "授权服务器只接受登记且精确匹配的 redirect URI，并绑定 PKCE。",
            "SR-001 风险评审状态为 `PENDING`",
        ),
        "裸 UNKNOWN 控制": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 UNKNOWN",
        ),
        "裸 UNKNOWN 安全要求": sample.replace(
            "授权服务器只接受登记且精确匹配的 redirect URI，并绑定 PKCE。",
            "SR-001 UNKNOWN",
        ),
        "中文未知控制": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 未知",
        ),
        "中文未知恢复": sample.replace(
            "恢复：轮换凭证，复核授权并回归验证。", "恢复：未知"
        ),
        "中文未知控制续句": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 当前未知，后续补齐。",
        ),
        "中文未知结果续句": sample.replace(
            "重定向篡改被拒绝，告警在目标时限内触发。",
            "结果当前未知，需进一步验证。",
        ),
        "中文未知 Owner 续句": sample.replace(
            "安全工程 Owner：平台安全架构负责人。",
            "安全工程 Owner：当前未知，由平台团队后续确认。",
        ),
        "中文未明确控制续句": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 当前未明确，后续补齐。",
        ),
        "追踪表未知控制 Owner": sample.replace(
            "| CTRL-001 | 平台安全负责人 |",
            "| CTRL-001 | 当前未知，后续补齐 |",
        ),
        "括号未知控制": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001（当前未知，后续补齐）。",
        ),
        "括号未知结果": sample.replace(
            "重定向篡改被拒绝，告警在目标时限内触发。",
            "当前未知（需进一步验证）。",
        ),
        "括号未明确 Owner": sample.replace(
            "安全工程 Owner：平台安全架构负责人。",
            "安全工程 Owner：未明确（由平台团队后续确认）。",
        ),
        "追踪表括号未明确 Owner": sample.replace(
            "| CTRL-001 | 平台安全负责人 |",
            "| CTRL-001 | 未明确（后续确认） |",
        ),
        "目前未知控制": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 目前未知，后续补齐。",
        ),
        "暂未明确控制": sample.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 暂未明确，后续补齐。",
        ),
    }
    for field, hidden_case in hidden_backtick_work.items():
        if not any("unresolved" in item for item in audit(hidden_case)):
            raise SystemExit(f"self-test failed: backtick-hidden unresolved {field} accepted")

    legitimate_english_unknown = design_ready.replace(
        "授权服务器只接受登记且精确匹配的 redirect URI，并绑定 PKCE。",
        "Prevent an unknown client from redeeming an authorization code.",
    ).replace(
        "security-evidence/oauth-review-2.1.md。",
        "security-evidence/unknown-client-review.md。",
    )
    if audit(legitimate_english_unknown):
        raise SystemExit(
            "self-test failed: natural-language unknown/path was rejected: "
            f"{audit(legitimate_english_unknown)}"
        )

    legitimate_chinese_unknown = (
        design_ready.replace(
            "控制：CTRL-001 精确匹配 redirect URI，使用 PKCE 和最小 scope。",
            "控制：CTRL-001 拒绝未知客户端并记录审计日志。",
        )
        .replace(
            "预防：默认拒绝未登记回调和不完整 PKCE 请求。",
            "预防：默认拒绝未明确授权的请求。",
        )
        .replace(
            "重定向篡改被拒绝，告警在目标时限内触发。",
            "未知客户端请求均被拒绝，验证通过。",
        )
        .replace(
            "security-evidence/oauth-review-2.1.md。",
            "security-evidence/未知客户端-review.md。",
        )
    )
    if audit(legitimate_chinese_unknown):
        raise SystemExit(
            "self-test failed: Chinese unknown object/action/path was rejected: "
            f"{audit(legitimate_chinese_unknown)}"
        )

    legitimate_unknown_ids = design_ready.replace(
        "RISK-001", "RISK-UNKNOWN-CLIENT"
    ).replace("CTRL-001", "CTRL-UNKNOWN-CLIENT")
    if audit(legitimate_unknown_ids):
        raise SystemExit(
            "self-test failed: UNKNOWN inside IDs was rejected: "
            f"{audit(legitimate_unknown_ids)}"
        )

    missing_risk_governance = sample.replace("- 截止时间：2026-09-30。\n", "").replace(
        "- 复核触发器：依赖、权限模型或目标环境发生变化。\n", ""
    )
    if not any("missing non-blank field 截止时间" in item for item in audit(missing_risk_governance)):
        raise SystemExit("self-test failed: conditional recommendation without governance accepted")

    resolved_history = sample.replace(
        "重定向篡改被拒绝，告警在目标时限内触发。",
        "测试最终通过；先前测试失败已修复并完成回归。",
    )
    if audit(resolved_history):
        raise SystemExit(f"self-test failed: resolved historical failure rejected: {audit(resolved_history)}")

    blocked = (
        low_evidence.replace("D1_DESIGN | CONDITIONAL", "D1_DESIGN | OPEN")
        .replace("未闭合阻断项：NONE", "未闭合阻断项：RISK-001 运行证据不足")
        .replace("ENGINEERING_READY_WITH_RISK", "ENGINEERING_BLOCKED")
    )
    if audit(blocked):
        raise SystemExit(f"self-test failed: honest ENGINEERING_BLOCKED rejected: {audit(blocked)}")
    print("OK security deliverable checker self-test")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="UTF-8 security deliverable; omit to read stdin")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    failures = audit(text)
    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        return 1
    print("OK security engineering deliverable contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
