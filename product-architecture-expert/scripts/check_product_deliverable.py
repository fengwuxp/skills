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
BUSINESS_ARCHITECTURE_VIEW_CHECKS: dict[str, RequiredGroup] = {
    "capability_map": RequiredGroup(
        "capability_map", ["业务能力地图", "能力分层", "能力 owner", "能力边界", "业务结果"], 3
    ),
    "value_stream": RequiredGroup(
        "value_stream", ["价值流", "利益相关者", "价值结果", "价值阶段", "价值形成", "价值交付"], 3
    ),
    "business_process": RequiredGroup(
        "business_process", ["业务流程", "触发", "参与者", "交接", "异常", "人工节点", "结束条件"], 4
    ),
    "objects_and_rules": RequiredGroup(
        "objects_and_rules", ["核心对象", "生命周期", "业务不变量", "关键规则", "规则 owner"], 3
    ),
    "capability_mapping": RequiredGroup(
        "capability_mapping", ["能力-项目-系统", "现有项目", "现有系统", "数据源", "重复建设"], 3
    ),
    "portfolio": RequiredGroup(
        "portfolio", ["能力差距", "依赖", "优先级", "项目组合", "路线图", "停止条件"], 3
    ),
}
BUSINESS_ARCHITECTURE_VIEW_NAMES: dict[str, tuple[str, ...]] = {
    "capability_map": ("业务能力地图", "能力地图"),
    "value_stream": ("价值流",),
    "business_process": ("业务流程", "跨角色流程"),
    "objects_and_rules": ("核心对象与规则", "对象与规则", "对象规则"),
    "capability_mapping": ("能力-项目-系统映射", "能力-项目-系统"),
    "portfolio": ("项目组合", "路线图"),
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
SCENARIO_HEADING_PATTERN = re.compile(
    r"(?i)(?:\b(?:SCN|UC)-[A-Z0-9-]+\b|(?:业务)?场景(?:契约|设计)?\s*[：:]\s*\S+)"
)
SCENARIO_ID_PATTERN = re.compile(r"(?i)\b(?:SCN|UC)-[A-Z0-9-]+\b")
SCENARIO_FIELD_GROUPS = (
    ("business_problem", ("业务问题与期望结果", "业务问题", "真实问题")),
    ("participants", ("参与者与责任", "参与者", "业务主体")),
    ("trigger_context", ("触发与前置事实", "触发条件", "前置事实", "前置条件")),
    ("main_path", ("主路径与状态变化", "主路径", "状态变化", "能力编排")),
    ("rule_scope", ("适用规则", "规则引用")),
    ("observable_result", ("完成证据与验收种子", "完成证据", "可观察结果", "完成定义")),
    ("exception_closure", ("逆向、异常与停止", "异常与人工兜底", "异常处理")),
)
PRD_STRENGTHS = {"轻量", "标准", "增强"}
SCENARIO_CONTRACT_STRENGTHS = {"标准", "增强"}
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
STRUCTURE_ONLY_MESSAGE = "仅通过结构检查，不代表语义和视觉验收通过"
IMPLEMENTATION_LANGUAGE_TERMS = (
    "Handler",
    "@Transactional",
    "事务边界",
    "MQ",
    "Outbox",
    "Saga",
    "Repository",
    "ServiceImpl",
    "实现类",
    "Kafka",
    "Redis",
)
VALUED_GROUP_KINDS = {"business-architecture", "product-review"}

SELF_TESTS: dict[str, tuple[str, str]] = {
    "business-architecture": (
        "战略意图：提升客户经营效率；真实问题：项目重复建设；决策场景：项目组合取舍；范围边界：客户中心。"
        "选用视图：业务能力地图、价值流、核心对象与规则、能力-项目-系统映射、项目组合。"
        "跳过视图及理由：业务流程不影响本轮投资取舍。"
        "业务能力地图包含能力分层、能力 owner、业务结果和能力边界。"
        "价值流面向利益相关者说明从客户准入到持续经营的价值阶段、价值结果、价值形成和价值交付。"
        "核心对象为客户与客户关系；生命周期、业务不变量、关键规则和规则 owner 明确。"
        "能力-项目-系统映射列出现有项目、现有系统、数据源和重复建设。"
        "能力差距、依赖、优先级、项目组合、路线图和停止条件明确。"
        "证据来源、待确认项、验收、知识库回流位置和复审机制明确。",
        "战略意图：提升效率。业务能力地图：客户管理。",
    ),
    "prd": (
        "文档强度：标准。\n"
        "## 阅读摘要\n当前结论：统一审核入口；产品定义 / 产品视图：为运营提供可追踪的审核能力；主链路：提交、审核、通知；核心对象与边界：申请单由平台管理，不改变交易订单。\n"
        "## 一、背景与问题\n背景：审核积压影响运营；问题：人工路径不清。\n"
        "## 二、目标与非目标\n目标：提升运营效率；非目标：不改结算规则。\n"
        "## 三、定性与范围\n产品定性：存量审核流程治理；总体判断：先统一口径；范围和产品边界为后台审核。\n"
        "## 四、概要设计\n概要设计：核心方案是统一审核入口和能力布局，并说明总体流程。\n"
        "核心名相：审核任务；定义：等待运营判断的申请；不是什么：交易订单；归属主体：平台。"
        "用户：运营；主体：平台；角色：审核员；验收方：产品和运营。\n"
        "## 五、详细设计\n以下场景说明申请单如何形成可追踪的审核结论。\n"
        "### SCN-001 运营审核申请\n"
        "业务问题与期望结果：审核员需要在统一入口完成判断，申请单最终形成可追踪结论。\n"
        "参与者与责任：审核员处理，平台持有申请事实，产品和运营负责验收。\n"
        "触发与前置事实：申请已提交且材料来源可信，状态为待审。\n"
        "主路径与状态变化：审核员核对材料并裁决，申请单由待审变为通过或驳回。\n"
        "适用规则：跨场景不变量和审批规则适用于裁决步骤。\n"
        "完成证据与验收种子：审核结论、操作者和时间可查询，重复处理不改变终态。\n"
        "逆向、异常与停止：材料不足时驳回补充，外部来源不可用时停止裁决并转人工处理。\n"
        "## 六、关键流程\n主流程：提交、审核、通知；异常流程：重复提交；人工处理：补录；流程图：审核路径。\n"
        "## 七、业务规则与接口抽象\n"
        "规则性质：场景裁决规则。适用场景 / 步骤：SCN-001 / 审核裁决。触发与判断条件：只有待审申请可裁决；审批结论必须记录版本和验收样例。产品接口抽象说明业务契约、输入、输出和失败语义。\n"
        "## 八、数据与风险\n数据：指标、报表、审计和追溯。"
        "风险：外部依赖待确认，确认方为业务，影响范围是审核上线。\n"
        "## 九、验收摘要\n对应场景：SCN-001。正常结果：通过或驳回结论、操作者和时间可查询；关键边界：重复裁决不改变终态；异常与兜底：来源不可用时停止并转人工；红线：不得生成无审计记录的结论。",
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


def markdown_sections(text: str) -> list[tuple[str, str]]:
    matches = list(HEADING_PATTERN.finditer(text))
    return [
        (match.group(1), text[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(text)])
        for index, match in enumerate(matches)
    ]


def matching_heading_positions(headings: list[str], aliases: tuple[str, ...]) -> list[int]:
    return [
        index
        for index, heading in enumerate(headings)
        if any(alias.casefold() in heading for alias in aliases)
    ]


def missing_ordered_sections(text: str, sections: list[tuple[str, tuple[str, ...]]]) -> list[str]:
    headings = [normalize(heading) for heading, _ in markdown_sections(text)]
    missing: list[str] = []
    positions: list[int] = []
    positions_by_section: dict[str, list[int]] = {}
    for name, aliases in sections:
        matched = matching_heading_positions(headings, aliases)
        positions_by_section[name] = matched
        if not matched:
            missing.append(name)
        else:
            positions.append(matched[0])
    if len(headings) != len(set(headings)):
        missing.append("duplicate_headings")
    heading_owners: dict[int, list[str]] = {}
    for name, matched in positions_by_section.items():
        for position in matched:
            heading_owners.setdefault(position, []).append(name)
    if any(len(owners) > 1 for owners in heading_owners.values()):
        missing.append("section_heading_reused")
    if not missing and positions != sorted(positions):
        missing.append("section_order")
    return missing


def has_keyword_only_section(text: str) -> bool:
    sections = markdown_sections(text)
    headings = [heading.casefold() for heading, _ in sections]
    keywords = sorted(
        {
            alias.casefold()
            for group in CHECKS["prd"]
            for alias in group.aliases
        }
        | {alias.casefold() for _, aliases in PRD_SECTION_ORDER for alias in aliases},
        key=len,
        reverse=True,
    )
    for _, aliases in PRD_SECTION_ORDER:
        matched = matching_heading_positions(headings, aliases)
        if len(matched) != 1:
            continue
        body = sections[matched[0]][1].casefold()
        for keyword in keywords:
            body = body.replace(keyword, "")
        residue = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", body)
        if len(residue) < 2:
            return True
    return False


def scenario_blocks(text: str) -> list[tuple[str, str]]:
    headings = list(re.finditer(r"(?m)^(#{3,6})\s+(.+?)\s*$", text))
    blocks: list[tuple[str, str]] = []
    for index, heading in enumerate(headings):
        title = heading.group(2)
        if not SCENARIO_HEADING_PATTERN.search(title):
            continue
        level = len(heading.group(1))
        end = len(text)
        for following in headings[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        blocks.append((title, text[heading.end() : end]))
    return blocks


def has_meaningful_alias_value(text: str, aliases: tuple[str, ...]) -> bool:
    return any(has_meaningful_labeled_value(text, alias) for alias in aliases)


def labeled_values(text: str, label: str) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [cell.strip().strip("`*_").strip() for cell in stripped.strip("|").split("|")]
            if len(cells) >= 2 and normalize(cells[0]) == normalize(label):
                values.append(cells[1])
    pattern = re.compile(
        rf"(?m)^\s*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*|__|`)?\s*{re.escape(label)}\s*"
        rf"(?:\*\*|__|`)?\s*[：:]\s*([^；;。\n|]+)",
        re.IGNORECASE,
    )
    values.extend(match.group(1).strip().strip("`*_").strip() for match in pattern.finditer(text))
    return values


def meaningful_values(values: list[str]) -> list[str]:
    return [
        value
        for value in values
        if normalize(value) not in EMPTY_LABELED_VALUES and not PLACEHOLDER_FIELD.search(value)
    ]


def field_values(text: str, label: str) -> list[str]:
    values = labeled_values(text, label)
    first = labeled_value(text, label)
    if first is not None and first not in values:
        values.append(first)
    return meaningful_values(values)


def all_check_groups(kind: str) -> list[RequiredGroup]:
    groups = CHECKS[kind]
    if kind == "business-architecture":
        return groups + list(BUSINESS_ARCHITECTURE_VIEW_CHECKS.values())
    return groups


def selected_business_architecture_views(text: str) -> set[str]:
    tokens = business_architecture_view_tokens(text, "选用视图")
    return {
        name
        for name, aliases in BUSINESS_ARCHITECTURE_VIEW_NAMES.items()
        if any(normalize(alias) in tokens for alias in aliases)
    }


def business_architecture_view_tokens(text: str, label: str) -> set[str]:
    return {
        normalize(token)
        for value in field_values(text, label)
        for token in re.split(r"[,，、]+", value)
        if normalize(token)
    }


def unknown_business_architecture_views(text: str) -> set[str]:
    known = {
        normalize(alias)
        for aliases in BUSINESS_ARCHITECTURE_VIEW_NAMES.values()
        for alias in aliases
    }
    return business_architecture_view_tokens(text, "选用视图") - known


def table_column_values(text: str, aliases: tuple[str, ...]) -> list[str]:
    lines = text.splitlines()
    normalized_aliases = {normalize(alias) for alias in aliases}
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        headers = [cell.strip().strip("`*_").strip() for cell in line.strip().strip("|").split("|")]
        column = next(
            (position for position, header in enumerate(headers) if normalize(header) in normalized_aliases),
            None,
        )
        if column is None:
            continue
        values: list[str] = []
        for row in lines[index + 1 :]:
            if not row.strip().startswith("|"):
                break
            cells = [cell.strip().strip("`*_").strip() for cell in row.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            if column < len(cells):
                values.append(cells[column])
        return meaningful_values(values)
    return []


def scenario_contract_issues(text: str) -> list[str]:
    blocks = scenario_blocks(section_body(text, ("详细设计",)))
    if not blocks:
        return ["scenario_contract_missing"]
    scenario_ids = [match.group(0).upper() for title, _ in blocks if (match := SCENARIO_ID_PATTERN.search(title))]
    issues: list[str] = []
    if len(scenario_ids) != len(set(scenario_ids)):
        issues.append("duplicate_scenario_ids")
    if any(
        not all(has_meaningful_alias_value(body, aliases) for _, aliases in SCENARIO_FIELD_GROUPS)
        for _, body in blocks
    ):
        issues.append("scenario_contract_incomplete")
    return issues


def section_body(text: str, aliases: tuple[str, ...]) -> str:
    headings = list(re.finditer(r"(?m)^(#{2,6})\s+(.+?)\s*$", text))
    for index, heading in enumerate(headings):
        title = heading.group(2)
        if not any(alias.casefold() in title.casefold() for alias in aliases):
            continue
        level = len(heading.group(1))
        end = len(text)
        for following in headings[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        return text[heading.end() : end]
    return ""


def declared_prd_strength(text: str) -> str | None:
    value = labeled_value(text, "文档强度")
    if value is None:
        return None
    normalized = normalize(value)
    return normalized if normalized in PRD_STRENGTHS else "invalid"


def has_rule_scope(text: str) -> bool:
    rules = section_body(text, ("业务规则与接口抽象", "业务规则和接口抽象"))
    rule_types = field_values(rules, "规则性质") or table_column_values(rules, ("规则性质",))
    scopes = (
        field_values(rules, "适用场景 / 步骤")
        + field_values(rules, "适用场景/步骤")
        + field_values(rules, "适用场景")
    ) or table_column_values(rules, ("适用场景 / 步骤", "适用场景/步骤", "适用场景"))
    return bool(rule_types and scopes)


def defined_scenario_ids(text: str) -> set[str]:
    return {
        match.group(0).upper()
        for title, _ in scenario_blocks(section_body(text, ("详细设计",)))
        if (match := SCENARIO_ID_PATTERN.search(title))
    }


def rule_scenario_issues(text: str) -> list[str]:
    rules = section_body(text, ("业务规则与接口抽象", "业务规则和接口抽象"))
    referenced_ids = {match.group(0).upper() for match in SCENARIO_ID_PATTERN.finditer(rules)}
    return ["undefined_rule_scenario_reference"] if referenced_ids - defined_scenario_ids(text) else []


def acceptance_scenario_issues(text: str) -> list[str]:
    acceptance = section_body(text, ("验收摘要",))
    values = field_values(acceptance, "对应场景")
    if not values:
        return ["acceptance_scenario_missing"]
    referenced_ids = {
        match.group(0).upper()
        for value in values
        for match in SCENARIO_ID_PATTERN.finditer(value)
    }
    defined_ids = defined_scenario_ids(text)
    issues: list[str] = []
    if referenced_ids - defined_ids:
        issues.append("undefined_scenario_reference")
    if defined_ids - referenced_ids:
        issues.append("uncovered_scenarios")
    return issues


def contains_term(text: str, term: str) -> bool:
    if term.isascii() and term.replace("@", "").isalnum():
        return bool(re.search(rf"(?i)(?<![a-z0-9_]){re.escape(term)}(?![a-z0-9_])", text))
    return term.casefold() in text.casefold()


def valued_group_hits(kind: str, group: RequiredGroup, text: str) -> int:
    aliases = [alias.casefold() for alias in group.aliases]
    all_aliases = sorted(
        {alias.casefold() for candidate in all_check_groups(kind) for alias in candidate.aliases},
        key=len,
        reverse=True,
    )
    valued: set[str] = set()
    for clause in re.split(r"[。；;\n|]", text):
        normalized = normalize(clause)
        hits = [alias for alias in aliases if alias in normalized]
        if not hits:
            continue
        residue = normalized
        for alias in all_aliases:
            residue = residue.replace(alias, "")
        if len(re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", residue)) >= 2:
            valued.update(hits)
    return len(valued)


def is_keyword_shell(kind: str, text: str) -> bool:
    residue = normalize(text)
    for alias in sorted(
        {alias.casefold() for group in all_check_groups(kind) for alias in group.aliases},
        key=len,
        reverse=True,
    ):
        residue = residue.replace(alias, "")
    meaningful = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", residue)
    return len(meaningful) < len(all_check_groups(kind)) * 2


def warning_groups(kind: str, text: str) -> list[str]:
    if kind != "prd":
        return []
    warnings: list[str] = []
    detail_design = re.search(r"(?m)^#{2,6}\s+.*详细设计.*$", text)
    product_view = re.search(r"产品定义\s*/\s*产品视图|产品视图", text)
    if detail_design and product_view and product_view.start() > detail_design.start():
        warnings.append("product_view_late")
    if any(contains_term(text, term) for term in IMPLEMENTATION_LANGUAGE_TERMS):
        warnings.append("implementation_language")
    return warnings


def missing_groups(kind: str, text: str) -> list[str]:
    normalized = normalize(text)
    missing: list[str] = []
    for group in CHECKS[kind]:
        hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
        if hits < group.min_hits:
            missing.append(group.name)
        elif kind in VALUED_GROUP_KINDS and valued_group_hits(kind, group, text) < group.min_hits:
            missing.append(f"unvalued_{group.name}")
    if kind == "business-architecture":
        selected_views = selected_business_architecture_views(text)
        declared_view_tokens = business_architecture_view_tokens(text, "选用视图")
        if not declared_view_tokens and all(
            sum(1 for alias in group.aliases if alias.casefold() in normalized) >= group.min_hits
            and valued_group_hits(kind, group, text) >= group.min_hits
            for group in BUSINESS_ARCHITECTURE_VIEW_CHECKS.values()
        ):
            selected_views = set(BUSINESS_ARCHITECTURE_VIEW_CHECKS)
        if not selected_views:
            missing.append("selected_views_missing")
        if unknown_business_architecture_views(text):
            missing.append("selected_views_unknown")
        for name in selected_views:
            group = BUSINESS_ARCHITECTURE_VIEW_CHECKS[name]
            hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
            if hits < group.min_hits:
                missing.append(group.name)
            elif valued_group_hits(kind, group, text) < group.min_hits:
                missing.append(f"unvalued_{group.name}")
        unselected_views = set(BUSINESS_ARCHITECTURE_VIEW_CHECKS) - selected_views
        if unselected_views:
            skipped_values = field_values(text, "跳过视图及理由")
            if not skipped_values:
                missing.append("skipped_views_rationale_missing")
            else:
                skipped_text = normalize(" ".join(skipped_values))
                if any(
                    not any(normalize(alias) in skipped_text for alias in BUSINESS_ARCHITECTURE_VIEW_NAMES[name])
                    for name in unselected_views
                ):
                    missing.append("skipped_views_rationale_incomplete")
    if kind in VALUED_GROUP_KINDS and is_keyword_shell(kind, text):
        missing.append("keyword_shell")
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
        strength = declared_prd_strength(text)
        if strength is None:
            missing.append("document_strength_missing")
        elif strength == "invalid":
            missing.append("document_strength_invalid")
        if strength != "轻量":
            missing.extend(missing_ordered_sections(text, PRD_SECTION_ORDER))
        elif len(re.findall(r"(?m)^##\s+", text)) < 5:
            missing.append("lightweight_sections_missing")
        if has_keyword_only_section(text):
            missing.append("keyword_only_section")
        if strength == "轻量" and is_keyword_shell("prd", text):
            missing.append("keyword_shell")
        if strength in SCENARIO_CONTRACT_STRENGTHS:
            missing.extend(scenario_contract_issues(text))
            if not has_rule_scope(text):
                missing.append("rule_scope_missing")
            missing.extend(rule_scenario_issues(text))
            missing.extend(acceptance_scenario_issues(text))
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
    minimal_process_architecture = (
        "战略意图：降低投诉转交时延；真实问题：客服与运营反复转交；决策场景：优化一次投诉处理；范围边界：不做系统重构。\n"
        "选用视图：业务流程、核心对象与规则。\n"
        "跳过视图及理由：价值流、业务能力地图、能力-项目-系统映射和项目组合与本轮运营流程决策无关。\n"
        "业务流程：投诉进入后由客服受理、运营复核、责任人处置并由客服回告；触发、参与者、交接、异常、人工节点和结束条件明确。\n"
        "核心对象：投诉单；生命周期：待受理、处理中、已关闭；业务不变量：每次转交留痕；关键规则：超时升级；规则 owner：运营负责人。\n"
        "证据来源：工单日志；待确认：SLA；验收：平均转交次数下降；复审：两周后。"
    )
    if missing_groups("business-architecture", minimal_process_architecture):
        failures.append("business-architecture: selected minimal process views unexpectedly failed")
    process_masquerading_as_value_stream = (
        "战略意图：降低投诉转交时延；真实问题：客服与运营反复转交；决策场景：验证价值形成；范围边界：投诉处理。\n"
        "选用视图：价值流。\n"
        "跳过视图及理由：其他视图不在本轮范围。\n"
        "业务流程：投诉进入后的主链路由客服受理、运营复核和责任人处置组成；异常链路处理材料不全，人工节点负责超时升级。\n"
        "证据来源：工单日志；待确认：SLA；验收：转交次数下降；复审：两周后。"
    )
    if "value_stream" not in missing_groups("business-architecture", process_masquerading_as_value_stream):
        failures.append("business-architecture: process text unexpectedly satisfied selected value stream")
    undeclared_business_architecture = (
        SELF_TESTS["business-architecture"][0]
        .replace("选用视图：业务能力地图、价值流、核心对象与规则、能力-项目-系统映射、项目组合。", "", 1)
        .replace("跳过视图及理由：业务流程不影响本轮投资取舍。", "", 1)
    )
    if "selected_views_missing" not in missing_groups("business-architecture", undeclared_business_architecture):
        failures.append("business-architecture: undeclared view selection unexpectedly passed")
    legacy_all_views = (
        SELF_TESTS["business-architecture"][0]
        .replace("选用视图：业务能力地图、价值流、核心对象与规则、能力-项目-系统映射、项目组合。", "", 1)
        .replace("跳过视图及理由：业务流程不影响本轮投资取舍。", "", 1)
        + "业务流程由投诉触发，客服与运营参与并交接；材料缺失走异常处理，人工节点复核，回告客户后结束。"
    )
    if missing_groups("business-architecture", legacy_all_views):
        failures.append("business-architecture: complete legacy all-view document unexpectedly failed")
    unknown_selected_view = minimal_process_architecture.replace(
        "选用视图：业务流程、核心对象与规则。",
        "选用视图：业务流程、火星视图。",
        1,
    )
    if "selected_views_unknown" not in missing_groups(
        "business-architecture", unknown_selected_view
    ):
        failures.append("business-architecture: unknown selected view unexpectedly passed")
    incomplete_skip_rationale = minimal_process_architecture.replace(
        "跳过视图及理由：价值流、业务能力地图、能力-项目-系统映射和项目组合与本轮运营流程决策无关。",
        "跳过视图及理由：价值流与本轮运营流程决策无关。",
        1,
    )
    if "skipped_views_rationale_incomplete" not in missing_groups(
        "business-architecture", incomplete_skip_rationale
    ):
        failures.append("business-architecture: incomplete skipped-view rationale unexpectedly passed")
    for kind in VALUED_GROUP_KINDS:
        stuffed = " ".join(alias for group in CHECKS[kind] for alias in group.aliases) + " 内容完整"
        if not missing_groups(kind, stuffed):
            failures.append(f"{kind}: one valued clause supplied unrelated groups")
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
    reused_heading_prd = (
        SELF_TESTS["prd"][0]
        .replace("## 五、详细设计\n", "## 五、详细设计与关键流程\n", 1)
        .replace("## 六、关键流程\n", "", 1)
    )
    if "section_heading_reused" not in missing_groups("prd", reused_heading_prd):
        failures.append("prd: one heading satisfied multiple sections")
    duplicate_heading_prd = SELF_TESTS["prd"][0] + "\n## 五、详细设计\n补充说明：审核结果可追踪。"
    if "duplicate_headings" not in missing_groups("prd", duplicate_heading_prd):
        failures.append("prd: duplicate heading unexpectedly passed")
    nested_flow_prd = SELF_TESTS["prd"][0].replace(
        "## 六、关键流程\n",
        "## 六、关键流程\n### 6.1 业务流程\n流程补充：审核员处理申请单并输出可观察结果。\n",
        1,
    )
    if "duplicate_headings" in missing_groups("prd", nested_flow_prd):
        failures.append("prd: nested flow heading incorrectly treated as duplicate")
    keyword_only_prd = (
        "## 背景与问题\n背景 问题 现状 目标 非目标 成功指标\n"
        "## 目标与非目标\n背景 问题 现状 目标 非目标 成功指标\n"
        "## 定性与范围\n定性 总体判断 产品定位 范围 边界 不做范围\n"
        "## 概要设计\n概要设计 方案概述 核心方案 能力布局 总体流程\n"
        "## 详细设计\n核心名相 定义 不是什么 归属主体 产品边界 用户 主体 角色 验收方 责任边界 详细设计 场景 功能 对象 状态 生命周期 不变量 状态机图\n"
        "## 关键流程\n主流程 逆向流程 异常流程 人工处理 业务流程 用例图 流程图 泳道图\n"
        "## 业务规则与接口抽象\n规则 权限 审批 额度 计费 版本 验收样例 接口抽象 产品接口 业务契约 输入 输出 失败语义 责任边界\n"
        "## 数据与风险\n数据 指标 报表 埋点 审计 追溯 风险 依赖 待确认 确认方 影响范围\n"
        "## 验收摘要\n验收摘要 业务结果 关键边界 红线 验收标准"
    )
    if "keyword_only_section" not in missing_groups("prd", keyword_only_prd):
        failures.append("prd: keyword-only sections unexpectedly passed")
    abstract_prd = re.sub(
        r"(?ms)^### SCN-001.*?(?=^## 六、关键流程)",
        "详细设计：申请单场景覆盖用户、对象、状态、功能和生命周期。\n",
        SELF_TESTS["prd"][0],
    )
    if "scenario_contract_missing" not in missing_groups("prd", abstract_prd):
        failures.append("prd: abstract complete document unexpectedly passed without a scenario contract")
    light_prd = (
        "文档强度：轻量。\n"
        "## 一、背景、问题与目标\n背景：审核积压；问题：处理路径不清；目标：缩短时长；非目标：不改交易。\n"
        "## 二、定性、范围与概要\n产品定性：流程治理；总体判断：统一入口；范围和产品边界为后台审核。"
        "概要设计采用统一入口；方案概述说明申请如何流转。核心名相为审核任务，定义是待处理申请。"
        "用户为运营，角色是审核员，责任边界不变。\n"
        "## 三、详细设计与业务场景\n详细设计：审核员处理申请单场景；功能围绕对象状态和生命周期提供审核反馈。\n"
        "## 四、流程、规则与产品接口\n主流程是提交、审核、通知；异常流程处理重复请求和人工处理。"
        "规则覆盖权限和审批。产品接口抽象说明业务契约、输入、输出和失败语义。\n"
        "## 五、数据、风险与待确认\n数据包括指标、报表和审计。风险和依赖待确认，确认方为业务，影响范围为上线。\n"
        "## 六、验收摘要\n验收摘要覆盖业务结果、关键边界、红线和验收标准。"
    )
    if missing_groups("prd", light_prd):
        failures.append("prd: merged lightweight document unexpectedly failed")
    flat_light_prd = (
        "文档强度：轻量。\n"
        + " ".join(alias for group in CHECKS["prd"] for alias in group.aliases)
        + " 内容完整。"
    )
    flat_light_missing = set(missing_groups("prd", flat_light_prd))
    if not {"lightweight_sections_missing", "keyword_shell"}.issubset(flat_light_missing):
        failures.append("prd: flat lightweight keyword shell unexpectedly passed")
    missing_strength_prd = SELF_TESTS["prd"][0].replace("文档强度：标准。\n", "", 1)
    if "document_strength_missing" not in missing_groups("prd", missing_strength_prd):
        failures.append("prd: missing document strength unexpectedly passed")
    invalid_strength_prd = SELF_TESTS["prd"][0].replace("文档强度：标准", "文档强度：非标准", 1)
    if "document_strength_invalid" not in missing_groups("prd", invalid_strength_prd):
        failures.append("prd: non-enum document strength unexpectedly passed")
    named_scenario_prd = (
        SELF_TESTS["prd"][0]
        .replace("### SCN-001 运营审核申请", "### 业务场景：运营审核申请", 1)
        .replace("SCN-001 / 审核裁决", "运营审核申请 / 审核裁决", 1)
        .replace("对应场景：SCN-001", "对应场景：运营审核申请", 1)
    )
    if missing_groups("prd", named_scenario_prd):
        failures.append("prd: named scenario without an id unexpectedly failed")
    duplicate_scenario_prd = SELF_TESTS["prd"][0].replace(
        "## 六、关键流程",
        "### SCN-001 重复场景\n业务问题与期望结果：重复定义用于验证。\n\n## 六、关键流程",
        1,
    )
    if "duplicate_scenario_ids" not in missing_groups("prd", duplicate_scenario_prd):
        failures.append("prd: duplicate scenario ids unexpectedly passed")
    dangling_acceptance_prd = SELF_TESTS["prd"][0].replace("对应场景：SCN-001", "对应场景：SCN-999", 1)
    if "undefined_scenario_reference" not in missing_groups("prd", dangling_acceptance_prd):
        failures.append("prd: undefined acceptance scenario unexpectedly passed")
    unbound_rule_prd = SELF_TESTS["prd"][0].replace(
        "规则性质：场景裁决规则。适用场景 / 步骤：SCN-001 / 审核裁决。",
        "规则说明：相关规则见场景中的跨场景不变量说明。",
        1,
    )
    if "rule_scope_missing" not in missing_groups("prd", unbound_rule_prd):
        failures.append("prd: rule scope outside the rule section unexpectedly passed")
    matrix_rule_prd = SELF_TESTS["prd"][0].replace(
        "规则性质：场景裁决规则。适用场景 / 步骤：SCN-001 / 审核裁决。触发与判断条件：只有待审申请可裁决；审批结论必须记录版本和验收样例。产品接口抽象说明业务契约、输入、输出和失败语义。\n",
        "| 规则编号 | 规则名称 | 规则性质 | 适用场景 / 步骤 | 触发条件 | 判断逻辑 | 验收样例 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| R-001 | 审核裁决 | 场景裁决规则 | SCN-001 / 审核裁决 | 申请待审 | 记录结论版本 | 重复审批不改变终态 |\n"
        "产品接口抽象说明业务契约、输入、输出和失败语义。\n",
        1,
    )
    if missing_groups("prd", matrix_rule_prd):
        failures.append("prd: rule matrix with scenario scope unexpectedly failed")
    dangling_rule_prd = SELF_TESTS["prd"][0].replace(
        "适用场景 / 步骤：SCN-001 / 审核裁决",
        "适用场景 / 步骤：SCN-999 / 审核裁决",
        1,
    )
    if "undefined_rule_scenario_reference" not in missing_groups("prd", dangling_rule_prd):
        failures.append("prd: undefined rule scenario unexpectedly passed")
    first_scenario = re.search(r"(?ms)^### SCN-001.*?(?=^## 六、关键流程)", SELF_TESTS["prd"][0])
    if first_scenario is None:
        failures.append("prd: self-test scenario block missing")
    else:
        multi_scenario_prd = SELF_TESTS["prd"][0].replace(
            "## 六、关键流程",
            first_scenario.group(0).replace("SCN-001", "SCN-002") + "## 六、关键流程",
            1,
        )
        if "uncovered_scenarios" not in missing_groups("prd", multi_scenario_prd):
            failures.append("prd: scenario without acceptance coverage unexpectedly passed")
    appendix_uc_prd = SELF_TESTS["prd"][0] + "\n### UC-LEGACY 历史索引\n历史编号仅用于来源追溯。"
    if missing_groups("prd", appendix_uc_prd):
        failures.append("prd: appendix use-case heading unexpectedly treated as a scenario contract")
    warning_checker = globals().get("warning_groups")
    if not callable(warning_checker):
        failures.append("prd: warning analyzer missing")
    else:
        if warning_checker("prd", SELF_TESTS["prd"][0]):
            failures.append("prd: clean fixture unexpectedly warned")
        late_product_view_prd = SELF_TESTS["prd"][0].replace(
            "产品定义 / 产品视图：为运营提供可追踪的审核能力；",
            "",
            1,
        ) + "\n产品视图：审核能力。"
        if "product_view_late" not in warning_checker("prd", late_product_view_prd):
            failures.append("prd: late product view warning missing")
        product_view_before_detail_prd = SELF_TESTS["prd"][0].replace(
            "产品定义 / 产品视图：为运营提供可追踪的审核能力；",
            "",
            1,
        ).replace(
            "## 五、详细设计",
            "产品视图：为运营提供可追踪的审核能力。\n\n## 五、详细设计",
            1,
        )
        if "product_view_late" in warning_checker("prd", product_view_before_detail_prd):
            failures.append("prd: product view before detail design unexpectedly warned")
        implementation_prd = SELF_TESTS["prd"][0] + "\n实现说明：Handler 通过 MQ 和 Outbox 驱动 Saga。"
        if "implementation_language" not in warning_checker("prd", implementation_prd):
            failures.append("prd: implementation language warning missing")
    boundary_message = globals().get("STRUCTURE_ONLY_MESSAGE", "")
    if "仅通过结构检查" not in boundary_message or "不代表语义和视觉验收通过" not in boundary_message:
        failures.append("checker: structure-only acceptance boundary missing")
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

    for warning in warning_groups(args.kind, text):
        print(f"WARN product deliverable check: kind={args.kind} {warning}", file=sys.stderr)
    print(f"OK product deliverable check: kind={args.kind}; {STRUCTURE_ONLY_MESSAGE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
