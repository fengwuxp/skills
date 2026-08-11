#!/usr/bin/env python3
"""Check the minimum structure of a security engineering deliverable.

The checker reads one explicit local file or stdin. It never writes files,
uses the network, reads secrets, or decides whether a system is secure.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECTION_FIELDS = {
    "范围与证据": ("范围", "环境", "证据来源", "Owner"),
    "资产与资损": ("资产", "资损"),
    "主体与信任边界": ("主体", "信任边界"),
    "威胁与滥用路径": ("前提", "路径", "后果"),
    "控制与恢复": ("预防", "检测", "响应", "恢复"),
    "验证证据": ("证据等级", "验证方式", "结果"),
    "残余风险与准出": ("残余风险", "风险 Owner", "停止条件", "结论"),
}
VALID_GATES = {"READY", "READY_WITH_RISK", "BLOCKED"}
READY_WITH_RISK_REQUIRED_FIELDS = ("截止时间", "复核触发器")
READY_REQUIRED_FIELDS = (
    ("范围与证据", "环境"),
    ("范围与证据", "证据来源"),
    ("范围与证据", "Owner"),
    ("资产与资损", "资产"),
    ("资产与资损", "资损"),
    ("主体与信任边界", "主体"),
    ("主体与信任边界", "信任边界"),
    ("控制与恢复", "预防"),
    ("控制与恢复", "检测"),
    ("控制与恢复", "响应"),
    ("控制与恢复", "恢复"),
    ("验证证据", "验证方式"),
    ("验证证据", "结果"),
    ("残余风险与准出", "风险 Owner"),
)
PLACEHOLDER_SUFFIXES = ("已填写", "已补充", "待填写", "待补充")
BLOCKING_PREFIXES = (
    "pending",
    "tbd",
    "todo",
    "unknown",
    "no evidence",
    "not implemented",
    "not enabled",
    "not verified",
    "unverified",
    "failed",
    "fail",
    "待确认",
    "待定",
    "未知",
    "未明确",
    "无证据",
    "无可复核证据",
    "未实现",
    "未启用",
    "未验证",
    "失败",
    "不通过",
)
FIELD_BLOCKING_PATTERNS = {
    "证据来源": (r"^(?:当前)?(?:没有|无)(?:任何)?可复核证据(?:$|[，,。.;；])",),
    "Owner": (r"^(?:当前)?(?:无人负责|没有负责人|无负责人)(?:$|[，,。.;；])",),
    "风险 Owner": (r"^(?:当前)?(?:无人负责|没有负责人|无负责人)(?:$|[，,。.;；])",),
    "结果": (
        r"^(?:当前)?(?:测试|验证|演练|控制)(?:结果)?(?:仍|尚)?(?:失败|未通过|未生效)(?:$|[，,。.;；])",
    ),
}


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


def is_blocking_value(value: str, field: str) -> bool:
    normalized = value.strip().casefold()
    separators = " \t:：,，.。;；([（"
    has_blocking_prefix = any(
        normalized == prefix or (
            normalized.startswith(prefix)
            and len(normalized) > len(prefix)
            and normalized[len(prefix)] in separators
        )
        for prefix in BLOCKING_PREFIXES
    )
    return has_blocking_prefix or any(
        re.search(pattern, normalized) for pattern in FIELD_BLOCKING_PATTERNS.get(field, ())
    )


def audit(text: str) -> list[str]:
    failures: list[str] = []
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

    gate_body = parsed.get("残余风险与准出", "")
    gate = field_value(gate_body, "结论")
    if gate and gate not in VALID_GATES:
        failures.append("残余风险与准出: 结论 must be READY, READY_WITH_RISK, or BLOCKED")
    if gate in {"READY", "READY_WITH_RISK"}:
        for heading, field in READY_REQUIRED_FIELDS:
            value = field_value(parsed.get(heading, ""), field)
            if value and is_blocking_value(value, field):
                failures.append(f"{heading}: {gate} conflicts with unresolved field {field}")
    if gate == "READY_WITH_RISK":
        for field in READY_WITH_RISK_REQUIRED_FIELDS:
            value = field_value(gate_body, field)
            if not value or is_placeholder_value(value, field) or is_blocking_value(value, field):
                failures.append(f"残余风险与准出: READY_WITH_RISK requires resolved field {field}")
    return failures


def valid_sample() -> str:
    return """# 开放平台安全评审

## 范围与证据
- 范围：商户 OAuth 接入与回调链路。
- 环境：生产候选版本 2.1，法域待 Owner 复核。
- 证据来源：接口契约、配置回读和测试报告。
- Owner：平台安全负责人。

## 资产与资损
- 资产：商户身份、授权码、token 与交易指令。
- 资损：账户接管后伪造指令并扩大资金损失。

## 主体与信任边界
- 主体：商户管理员、平台服务、授权服务器和第三方客户端。
- 信任边界：浏览器、商户后端、平台网关与授权服务器之间。

## 威胁与滥用路径
- 前提：攻击者取得弱保护的 redirect URI 配置权限。
- 路径：篡改回调地址，截获授权码后换取 token。
- 后果：冒用商户身份访问受保护能力。

## 控制与恢复
- 预防：精确匹配 redirect URI，使用 PKCE 和最小 scope。
- 检测：关联异常授权、回调变更和 token 使用告警。
- 响应：吊销 token、冻结客户端并保全审计证据。
- 恢复：轮换凭证，复核授权并回归验证。

## 验证证据
- 证据等级：D4 Runtime。
- 验证方式：负向互操作测试、配置回读和告警演练。
- 结果：重定向篡改被拒绝，告警在目标时限内触发。

## 残余风险与准出
- 残余风险：第三方终端失陷仍需商户侧控制。
- 风险 Owner：平台安全负责人。
- 截止时间：2026-09-30。
- 复核触发器：依赖、权限模型或目标环境发生变化。
- 停止条件：目标环境配置无法回读或吊销演练失败。
- 结论：READY_WITH_RISK
"""


def self_test() -> None:
    sample = valid_sample()
    if audit(sample):
        raise SystemExit(f"self-test failed: valid sample rejected: {audit(sample)}")

    missing = sample.replace("## 控制与恢复", "## 其他")
    if not any("missing section: 控制与恢复" in item for item in audit(missing)):
        raise SystemExit("self-test failed: missing control section accepted")

    blank = sample.replace("- 资损：账户接管后伪造指令并扩大资金损失。", "- 资损：")
    if not any("missing non-blank field 资损" in item for item in audit(blank)):
        raise SystemExit("self-test failed: blank loss field accepted")

    invalid_gate = sample.replace("READY_WITH_RISK", "PASS")
    if not any("结论 must be" in item for item in audit(invalid_gate)):
        raise SystemExit("self-test failed: invalid gate accepted")

    contradictory_ready = (
        sample.replace("生产候选版本 2.1，法域待 Owner 复核", "PENDING")
        .replace("接口契约、配置回读和测试报告", "无可复核证据")
        .replace("平台安全负责人", "PENDING")
        .replace("商户身份、授权码、token 与交易指令", "未知")
        .replace("精确匹配 redirect URI，使用 PKCE 和最小 scope", "未实现")
        .replace("关联异常授权、回调变更和 token 使用告警", "未实现")
        .replace("吊销 token、冻结客户端并保全审计证据", "未实现")
        .replace("轮换凭证，复核授权并回归验证", "未实现")
        .replace("负向互操作测试、配置回读和告警演练", "未验证")
        .replace("重定向篡改被拒绝，告警在目标时限内触发", "失败")
        .replace("READY_WITH_RISK", "READY")
    )
    if not any("READY conflicts with unresolved" in item for item in audit(contradictory_ready)):
        raise SystemExit("self-test failed: contradictory READY accepted")

    english_unresolved = sample.replace(
        "生产候选版本 2.1，法域待 Owner 复核", "unknown"
    ).replace("READY_WITH_RISK", "READY")
    if not any("READY conflicts with unresolved" in item for item in audit(english_unresolved)):
        raise SystemExit("self-test failed: English unresolved READY accepted")

    keyword_shell = sample
    replacements = {
        "商户 OAuth 接入与回调链路。": "范围已填写",
        "生产候选版本 2.1，法域待 Owner 复核。": "环境已填写",
        "接口契约、配置回读和测试报告。": "证据来源已填写",
        "平台安全负责人。": "Owner 已填写",
        "商户身份、授权码、token 与交易指令。": "资产已填写",
        "账户接管后伪造指令并扩大资金损失。": "资损已填写",
        "商户管理员、平台服务、授权服务器和第三方客户端。": "主体已填写",
        "浏览器、商户后端、平台网关与授权服务器之间。": "信任边界已填写",
        "攻击者取得弱保护的 redirect URI 配置权限。": "前提已填写",
        "篡改回调地址，截获授权码后换取 token。": "路径已填写",
        "冒用商户身份访问受保护能力。": "后果已填写",
        "精确匹配 redirect URI，使用 PKCE 和最小 scope。": "预防已填写",
        "关联异常授权、回调变更和 token 使用告警。": "检测已填写",
        "吊销 token、冻结客户端并保全审计证据。": "响应已填写",
        "轮换凭证，复核授权并回归验证。": "恢复已填写",
        "负向互操作测试、配置回读和告警演练。": "验证方式已填写",
        "重定向篡改被拒绝，告警在目标时限内触发。": "结果已填写",
        "第三方终端失陷仍需商户侧控制。": "残余风险已填写",
        "2026-09-30。": "截止时间已填写",
        "依赖、权限模型或目标环境发生变化。": "复核触发器已填写",
        "目标环境配置无法回读或吊销演练失败。": "停止条件已填写",
    }
    for old, new in replacements.items():
        keyword_shell = keyword_shell.replace(old, new)
    if not any("placeholder" in item for item in audit(keyword_shell)):
        raise SystemExit("self-test failed: keyword-shell READY accepted")

    ellipsis_placeholder = sample.replace("商户 OAuth 接入与回调链路。", "...")
    if not any("placeholder" in item for item in audit(ellipsis_placeholder)):
        raise SystemExit("self-test failed: ellipsis placeholder accepted")

    semantic_conflict = (
        sample.replace("接口契约、配置回读和测试报告。", "当前没有可复核证据。")
        .replace("平台安全负责人。", "无人负责。")
        .replace("重定向篡改被拒绝，告警在目标时限内触发。", "测试失败，控制未生效。")
        .replace("READY_WITH_RISK", "READY")
    )
    if not any("READY conflicts with unresolved" in item for item in audit(semantic_conflict)):
        raise SystemExit("self-test failed: semantic-conflict READY accepted")

    resolved_history = sample.replace(
        "重定向篡改被拒绝，告警在目标时限内触发。",
        "测试最终通过；先前测试失败已修复并完成回归。",
    )
    if audit(resolved_history):
        raise SystemExit(f"self-test failed: resolved historical failure rejected: {audit(resolved_history)}")

    missing_risk_governance = sample.replace("- 截止时间：2026-09-30。\n", "").replace(
        "- 复核触发器：依赖、权限模型或目标环境发生变化。\n", ""
    )
    if not any("READY_WITH_RISK requires" in item for item in audit(missing_risk_governance)):
        raise SystemExit("self-test failed: READY_WITH_RISK without deadline or review trigger accepted")

    unresolved_risk_governance = sample.replace("截止时间：2026-09-30。", "截止时间：待确认")
    if not any("READY_WITH_RISK requires" in item for item in audit(unresolved_risk_governance)):
        raise SystemExit("self-test failed: READY_WITH_RISK with unresolved deadline accepted")

    blocked = contradictory_ready.replace("结论：READY", "结论：BLOCKED")
    if audit(blocked):
        raise SystemExit(f"self-test failed: honest BLOCKED rejected: {audit(blocked)}")
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
    print("OK security deliverable contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
