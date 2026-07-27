#!/usr/bin/env python3
"""Check product deliverable completeness for high-value output types.

The script only inspects local text or an explicit local file. It does not
access the network, upload content, read secrets, or judge business quality.
It is a deterministic completeness guard before human product review.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class RequiredGroup(NamedTuple):
    name: str
    aliases: list[str]
    min_hits: int = 1


CHECKS: dict[str, list[RequiredGroup]] = {
    "business-architecture": [
        RequiredGroup("strategic_intent", ["战略意图", "真实问题", "决策场景", "范围边界"], 3),
        RequiredGroup("capability_map", ["业务能力地图", "能力分层", "能力 owner", "能力边界", "业务结果"], 3),
        RequiredGroup("value_stream", ["价值流", "价值实现", "主链路", "异常链路", "人工节点"], 2),
        RequiredGroup("objects_and_rules", ["核心对象", "生命周期", "业务不变量", "关键规则", "规则 owner"], 3),
        RequiredGroup("capability_mapping", ["能力-项目-系统", "现有项目", "现有系统", "数据源", "重复建设"], 3),
        RequiredGroup("portfolio", ["能力差距", "依赖", "优先级", "项目组合", "路线图", "停止条件"], 3),
        RequiredGroup("governance", ["证据来源", "待确认", "验收", "知识库回流", "复审"], 3),
    ],
    "prd": [
        RequiredGroup("background_and_goal", ["背景", "问题", "现状", "目标", "非目标", "成功指标"], 4),
        RequiredGroup("qualitative_and_scope", ["定性", "总体判断", "产品定位", "范围", "边界", "不做范围"], 3),
        RequiredGroup("overview_design", ["概要设计", "方案概述", "核心方案", "能力布局", "总体流程"], 2),
        RequiredGroup("definition_and_boundary", ["核心名相", "定义", "不是什么", "归属主体", "产品边界"], 2),
        RequiredGroup("actors_and_roles", ["用户", "主体", "角色", "验收方", "责任边界"], 2),
        RequiredGroup("detail_design", ["详细设计", "场景", "功能", "对象", "状态", "生命周期", "不变量", "状态机图"], 3),
        RequiredGroup("flows", ["主流程", "逆向流程", "异常流程", "人工处理", "业务流程", "用例图", "流程图", "泳道图"], 2),
        RequiredGroup("rules", ["规则", "权限", "审批", "额度", "计费", "版本", "验收样例"], 2),
        RequiredGroup("interface_abstraction", ["接口抽象", "产品接口", "业务契约", "输入", "输出", "失败语义", "责任边界"], 3),
        RequiredGroup("data_and_audit", ["数据", "指标", "报表", "埋点", "审计", "追溯"], 2),
        RequiredGroup("risk_and_confirmation", ["风险", "依赖", "待确认", "确认方", "影响范围"], 2),
        RequiredGroup("acceptance_summary", ["验收摘要", "业务结果", "关键边界", "红线", "验收标准"], 2),
    ],
    "product-architecture": [
        RequiredGroup("business_goal", ["业务目标", "用户价值", "成功指标", "非目标"], 2),
        RequiredGroup("capability_map", ["能力地图", "能力域", "前台能力", "后台能力", "数据能力"], 1),
        RequiredGroup("domain_objects", ["业务对象", "对象模型", "字段口径", "生命周期", "状态"], 2),
        RequiredGroup("process_and_state", ["业务流程", "主流程", "异常流程", "状态机", "人工兜底"], 2),
        RequiredGroup("rule_matrix", ["规则矩阵", "触发条件", "判断逻辑", "优先级", "版本"], 2),
        RequiredGroup("operations_and_data", ["运营后台", "指标", "报表", "审计", "数据口径"], 2),
        RequiredGroup("risks_and_acceptance", ["风险", "待确认", "验收", "确认方", "发布"], 2),
    ],
    "diagram-brief": [
        RequiredGroup("diagram_goal", ["图形目标", "用途", "目标读者", "读者"], 1),
        RequiredGroup("architecture_type", ["架构类型", "业务架构", "产品架构"], 2),
        RequiredGroup("view_state", ["当前态", "目标态", "As-Is", "To-Be"], 1),
        RequiredGroup("view_level", ["视图层级", "企业级", "业务域", "产品域", "场景级"], 2),
        RequiredGroup("diagram_type", ["图形类型", "能力地图", "流程图", "状态机", "产品架构图", "资金流图"], 1),
        RequiredGroup("semantic_nodes", ["节点", "分组", "角色", "对象", "系统"], 2),
        RequiredGroup("semantic_edges", ["箭头", "关系", "流向", "同步", "异步", "状态迁移"], 1),
        RequiredGroup("assumptions", ["假设", "待确认", "风险", "边界"], 1),
        RequiredGroup("output_format", ["SVG", "输出格式", "正式图形化交付"], 1),
    ],
    "product-review": [
        RequiredGroup("review_context", ["触发原因", "当前阶段", "评审对象", "PRD 类型", "方案类型"], 2),
        RequiredGroup("consensus", ["共识", "已确认", "可进入下一步"], 1),
        RequiredGroup("disagreement", ["分歧", "争议", "备选方案", "取舍"], 1),
        RequiredGroup("blocking_changes", ["必改", "阻断", "严重", "影响"], 2),
        RequiredGroup("pending_confirmation", ["待确认", "确认方", "owner", "负责人"], 2),
        RequiredGroup("verification", ["验证方式", "验收", "检查", "下一步", "去向"], 2),
    ],
}
DIAGRAM_TYPE_CHECKS: dict[str, list[RequiredGroup]] = {
    "业务架构": [
        RequiredGroup("business_decision_anchor", ["战略意图", "业务目标", "决策问题", "经营决策", "投资取舍"], 1),
        RequiredGroup("business_architecture_semantics", ["业务能力", "价值流", "业务结果", "能力 owner", "能力-项目-系统", "项目组合"], 2),
    ],
    "产品架构": [
        RequiredGroup("product_business_anchor", ["业务目标", "用户价值", "产品方案", "验收标准", "规则矩阵"], 1),
        RequiredGroup("product_architecture_semantics", ["角色", "业务对象", "业务流程", "状态", "规则", "验收"], 3),
    ],
}
PLACEHOLDER_FIELD = re.compile(r"〈[^〉\n]+〉")
EMPTY_LABELED_VALUES = {"", "-", "无", "暂无", "待定", "待确认", "n/a", "na", "null", "none"}
HEADING_PATTERN = re.compile(r"(?m)^#{2,6}\s+(.+?)\s*$")
PRD_SECTION_ORDER = [
    ("section_background", ("背景与问题",)),
    ("section_goal", ("目标与非目标",)),
    ("section_qualitative", ("定性与范围", "定性、范围")),
    ("section_overview", ("概要设计",)),
    ("section_detail", ("详细设计",)),
    ("section_flow", ("关键流程", "业务流程")),
    ("section_rules_and_interface", ("业务规则与接口抽象", "业务规则和接口抽象")),
    ("section_risk", ("数据与风险", "数据、权限、风险", "风险与待确认")),
    ("section_acceptance", ("验收摘要",)),
]

SELF_TESTS: dict[str, tuple[str, str]] = {
    "business-architecture": (
        "战略意图：提升客户经营效率；真实问题：项目重复建设；决策场景：项目组合取舍；范围边界：客户中心。"
        "业务能力地图包含能力分层、能力 owner、业务结果和能力边界。"
        "价值流说明从客户准入到持续经营的价值实现主链路、异常链路和人工节点。"
        "核心对象为客户与客户关系；生命周期、业务不变量、关键规则和规则 owner 明确。"
        "能力-项目-系统映射列出现有项目、现有系统、数据源和重复建设。"
        "能力差距、依赖、优先级、项目组合、路线图和停止条件明确。"
        "证据来源、待确认项、验收、知识库回流位置和复审机制明确。",
        "战略意图：提升效率。业务能力地图：客户管理。",
    ),
    "prd": (
        "## 一、背景与问题\n背景：审核积压影响运营；问题：人工路径不清。\n"
        "## 二、目标与非目标\n目标：提升运营效率；非目标：不改结算规则。\n"
        "## 三、定性与范围\n产品定性：存量审核流程治理；总体判断：先统一口径；范围和产品边界为后台审核。\n"
        "## 四、概要设计\n概要设计：核心方案是统一审核入口和能力布局，并说明总体流程。\n"
        "核心名相：审核任务；定义：等待运营判断的申请；不是什么：交易订单；归属主体：平台。"
        "用户：运营；主体：平台；角色：审核员；验收方：产品和运营。\n"
        "## 五、详细设计\n详细设计：场景和功能围绕申请单；对象状态为待审、通过、驳回；生命周期从创建到关闭。\n"
        "## 六、关键流程\n主流程：提交、审核、通知；异常流程：重复提交；人工处理：补录；流程图：审核路径。\n"
        "## 七、业务规则与接口抽象\n"
        "规则：权限、审批、版本和验收样例。产品接口抽象说明业务契约、输入、输出和失败语义。\n"
        "## 八、数据与风险\n数据：指标、报表、审计和追溯。"
        "风险：外部依赖待确认，确认方为业务，影响范围是审核上线。\n"
        "## 九、验收摘要\n验收摘要：业务结果可观察，验收标准覆盖关键边界和红线。",
        "目标：提升效率。",
    ),
    "product-architecture": (
        "业务目标：提升审核效率；用户价值：减少等待；非目标：不改交易规则。"
        "能力地图：能力域包含前台能力、后台能力和数据能力。"
        "业务对象：申请单；对象模型：申请、审核记录；字段口径：amount；生命周期：创建到关闭；状态：待审、通过、驳回。"
        "业务流程：提交、审核、通知；主流程和异常流程齐全；人工兜底为运营复核。"
        "规则矩阵：触发条件、判断逻辑、优先级和版本。"
        "运营后台：查询、审核和导出；指标、报表、审计和数据口径。"
        "风险：外部依赖待确认；确认方：业务；验收：产品和运营验收；发布：灰度。",
        "业务目标：提升审核效率。能力地图：后台能力。",
    ),
    "diagram-brief": (
        "图形目标：说明跨境支付产品如何完成交易闭环；目标读者：产品和研发；架构类型：产品架构；目标态；视图层级：产品域；图形类型：产品架构图。"
        "业务锚点：降低跨境交易失败；类型语义：角色、支付订单、授权、请款、退款、状态、规则和验收的产品闭环。"
        "业务目标：降低交易失败；角色：商户和运营；业务对象：支付订单；业务流程覆盖授权、请款和退款；状态、规则和验收保持一致。"
        "节点：角色、对象、系统；分组：前台和后台；箭头：状态迁移；关系：数据流；假设：争议规则待确认；输出格式：SVG。",
        "图形目标：说明能力；图形类型：能力地图。",
    ),
    "product-review": (
        "触发原因：AI 生成 PRD 存在多方争议；当前阶段：方案共识；评审对象：会员权益 PRD；方案类型：功能型。"
        "共识：目标、范围和核心对象已确认，可进入下一步。"
        "分歧：是否加入自动续费；备选方案为本期不做或灰度；影响为合规和运营成本。"
        "必改：验收标准缺少异常路径，影响测试和上线评审。"
        "待确认：退款规则由法务 owner 确认，确认方为产品负责人。"
        "验证方式：补充验收样例并运行检查；下一步进入 PRD 修订。",
        "共识：目标已确认。待确认：退款规则。",
    ),
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def labeled_value(text: str, label: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip().strip("`*_").strip() for cell in stripped.strip("|").split("|")]
        if len(cells) >= 2 and normalize(cells[0]) == normalize(label):
            return cells[1]
    match = re.search(
        rf"(?:^|[\n；;。])\s*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*|__|`)?\s*{re.escape(label)}\s*(?:\*\*|__|`)?\s*[：:]\s*([^；;。\n|]+)",
        text,
        re.IGNORECASE,
    )
    return match.group(1).strip().strip("`*_").strip() if match else None


def has_meaningful_labeled_value(text: str, label: str) -> bool:
    value = labeled_value(text, label)
    return bool(
        value is not None
        and normalize(value) not in EMPTY_LABELED_VALUES
        and not PLACEHOLDER_FIELD.search(value)
    )


def declared_architecture_type(text: str) -> str | None:
    value = labeled_value(text, "架构类型")
    if value is None:
        return None
    return next((name for name in DIAGRAM_TYPE_CHECKS if normalize(value) == name.casefold()), None)


def missing_ordered_sections(text: str, sections: list[tuple[str, tuple[str, ...]]]) -> list[str]:
    headings = [match.group(1).casefold() for match in HEADING_PATTERN.finditer(text)]
    missing: list[str] = []
    positions: list[int] = []
    for name, aliases in sections:
        position = next(
            (index for index, heading in enumerate(headings) if any(alias.casefold() in heading for alias in aliases)),
            None,
        )
        if position is None:
            missing.append(name)
        else:
            positions.append(position)
    if not missing and positions != sorted(positions):
        missing.append("section_order")
    return missing


def missing_groups(kind: str, text: str) -> list[str]:
    normalized = normalize(text)
    missing: list[str] = []
    for group in CHECKS[kind]:
        hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
        if hits < group.min_hits:
            missing.append(group.name)
    if kind == "diagram-brief":
        for label, name in (("业务锚点", "business_anchor"), ("类型语义", "type_semantics")):
            if not has_meaningful_labeled_value(text, label):
                missing.append(name)
        architecture_type = declared_architecture_type(text)
        if architecture_type is None:
            if "architecture_type" not in missing:
                missing.append("architecture_type")
        else:
            for group in DIAGRAM_TYPE_CHECKS[architecture_type]:
                hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
                if hits < group.min_hits:
                    missing.append(group.name)
    if PLACEHOLDER_FIELD.search(text):
        missing.append("placeholder_fields")
    if kind == "prd":
        missing.extend(missing_ordered_sections(text, PRD_SECTION_ORDER))
    return missing


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    return sys.stdin.read()


def run_self_test() -> int:
    failures: list[str] = []
    if "business-architecture" not in CHECKS:
        failures.append("business-architecture: missing deliverable kind")
    diagram_group_names = {group.name for group in CHECKS["diagram-brief"]}
    for required_name in ("architecture_type", "view_state", "view_level"):
        if required_name not in diagram_group_names:
            failures.append(f"diagram-brief: missing required group {required_name}")
    for kind, (valid_text, invalid_text) in SELF_TESTS.items():
        valid_missing = missing_groups(kind, valid_text)
        if valid_missing:
            failures.append(f"{kind}: valid fixture missing {', '.join(valid_missing)}")
        invalid_missing = missing_groups(kind, invalid_text)
        if not invalid_missing:
            failures.append(f"{kind}: invalid fixture unexpectedly passed")
    business_architecture_diagram = (
        "图形目标：判断跨境支付哪些能力值得投资；目标读者：业务负责人；架构类型：业务架构；目标态；视图层级：业务域；图形类型：能力地图。"
        "业务锚点：决定跨境支付能力投资次序；类型语义：业务能力、价值流、业务结果、能力 owner 和投资取舍。"
        "战略意图：提升跨境交易履约；业务能力包括商户准入、交易履约和资金结算；价值流连接签约到结算；业务结果和能力 owner 明确。"
        "节点：业务能力；分组：交易和资金；箭头：价值流；待确认：投资取舍；输出格式：SVG。"
    )
    if missing_groups("diagram-brief", business_architecture_diagram):
        failures.append("diagram-brief: business architecture fixture unexpectedly failed")
    business_architecture_mismatch = (
        "图形目标：说明跨境支付业务；目标读者：业务负责人；架构类型：业务架构；当前态；视图层级：业务域；图形类型：能力地图。"
        "战略意图、业务目标、业务能力、价值流、业务结果和能力 owner 均已明确。"
        "节点：Kafka、Redis、MySQL；分组：中间件和数据库；箭头：数据流；待确认：集群性能；输出格式：SVG。"
    )
    expected_business_mismatch = {"business_anchor", "type_semantics"}
    if not expected_business_mismatch.issubset(set(missing_groups("diagram-brief", business_architecture_mismatch))):
        failures.append("diagram-brief: keyword-stuffed business architecture unexpectedly passed")
    for formatted_diagram in (
        SELF_TESTS["diagram-brief"][0].replace("架构类型：产品架构；", "**架构类型**：产品架构；", 1),
        SELF_TESTS["diagram-brief"][0].replace("架构类型：产品架构；", "\n| 架构类型 | 产品架构 |\n", 1),
    ):
        if missing_groups("diagram-brief", formatted_diagram):
            failures.append("diagram-brief: formatted architecture type unexpectedly failed")
    diagram_without_view = SELF_TESTS["diagram-brief"][0].replace(
        "架构类型：产品架构；目标态；视图层级：产品域；",
        "",
    )
    expected_diagram_missing = {"architecture_type", "view_state", "view_level"}
    if not expected_diagram_missing.issubset(set(missing_groups("diagram-brief", diagram_without_view))):
        failures.append("diagram-brief: missing architecture view fields unexpectedly passed")
    placeholder_text = SELF_TESTS["prd"][0] + "owner：〈待填写〉"
    if "placeholder_fields" not in missing_groups("prd", placeholder_text):
        failures.append("prd: placeholder fixture unexpectedly passed")
    flat_prd = re.sub(r"(?m)^#{2,6}\s+", "", SELF_TESTS["prd"][0]).replace("\n", " ")
    if not any(item.startswith("section_") for item in missing_groups("prd", flat_prd)):
        failures.append("prd: flat keyword fixture unexpectedly passed")
    wrong_order_prd = (
        SELF_TESTS["prd"][0]
        .replace("## 一、背景与问题", "## __SWAP__", 1)
        .replace("## 二、目标与非目标", "## 一、背景与问题", 1)
        .replace("## __SWAP__", "## 二、目标与非目标", 1)
    )
    if "section_order" not in missing_groups("prd", wrong_order_prd):
        failures.append("prd: wrong section order unexpectedly passed")
    if failures:
        print("FAIL product deliverable self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK product deliverable self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查产品架构交付物的结构完整性")
    parser.add_argument("--kind", choices=sorted(CHECKS), help="交付物类型")
    parser.add_argument("--file", help="待检查的本地 Markdown/文本文件")
    parser.add_argument("--text", help="直接传入待检查文本")
    parser.add_argument("--self-test", action="store_true", help="运行内置正反例自测")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.kind:
        parser.error("--kind is required unless --self-test is used")

    text = read_input(args)
    if not text.strip():
        print("FAIL product deliverable check: empty input", file=sys.stderr)
        return 2

    missing = missing_groups(args.kind, text)
    if missing:
        print(
            f"FAIL product deliverable check: kind={args.kind} missing " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    print(f"OK product deliverable check: kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
