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
        RequiredGroup("flows", ["主流程", "逆向流程", "异常流程", "人工处理", "业务流程", "责任推进", "异常与收口", "用例图", "流程图", "泳道图"], 2),
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
    "prototype-scope-plan": [
        RequiredGroup("goal_and_scope", ["目标", "范围", "非目标", "owner"], 3),
        RequiredGroup("requirement_coverage", ["需求覆盖矩阵", "需求 ID", "AC ID", "应用", "客户端"], 4),
        RequiredGroup("carrier_inventory", ["原型载体清单", "承接 ID", "类型", "应用", "客户端"], 4),
        RequiredGroup("page_annotations", ["产品级页面标注", "业务对象", "权限", "状态变化", "异常", "AC"], 4),
        RequiredGroup("client_differences", ["多端差异矩阵", "不变", "差异", "证据", "回退"], 3),
        RequiredGroup("cross_application_handoff", ["跨应用衔接", "身份", "状态同步", "失败恢复", "审计"], 3),
        RequiredGroup("prototype_trace", ["原型覆盖追踪", "关系姿态", "覆盖状态", "未覆盖前处理"], 3),
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
SCENARIO_SHORT_FIELD_GROUPS = (
    ("scenario_statement", ("场景说明",)),
    ("participants", ("参与者", "参与者与责任")),
    ("flow", ("流程",)),
    ("business_result", ("业务结果",)),
    ("exception_handling", ("异常处理",)),
    ("rules_and_acceptance", ("规则与验收",)),
)
SCENARIO_NARRATIVE_FIELD_GROUPS = (
    ("business_context", ("业务情境",)),
    ("responsibility_flow", ("责任推进",)),
    ("decision_and_state", ("裁决与状态",)),
    ("exception_and_closure", ("异常与收口",)),
)
SCENARIO_LEGACY_FIELD_GROUPS = (
    ("business_problem", ("业务问题与期望结果", "业务问题", "真实问题")),
    ("participants", ("参与者与责任", "参与者", "业务主体")),
    ("trigger_context", ("触发与前置事实", "触发条件", "前置事实", "前置条件")),
    ("main_path", ("主路径与状态变化", "主路径", "状态变化", "能力编排")),
    ("rule_scope", ("适用规则", "规则引用")),
    ("observable_result", ("完成证据与验收种子", "完成证据")),
    ("exception_closure", ("逆向、异常与停止", "异常与人工兜底")),
)
REQUIREMENT_FIELD_GROUPS = (
    ("requirement_name", ("需求名称",)),
    ("requirement_type", ("需求类型",)),
    ("responsible_subject", ("责任主体", "主体")),
    ("requirement_context", ("场景 / 前置状态", "场景/前置状态", "前置状态", "前置条件")),
    ("normative_force", ("规范强度",)),
    ("required_outcome", ("要求的行为或业务结果", "行为或结果", "业务结果")),
    ("requirement_boundary", ("度量、时限或边界", "度量 / 时限 / 边界", "需求边界")),
    ("requirement_source", ("来源与可靠性", "来源 / 可靠性", "需求来源")),
    ("acceptance_example", ("验收样例", "验收引用")),
)
REQUIREMENT_COMPACT_FIELD_GROUPS = (
    ("name_and_type", ("需求名称 / 类型", "需求名称/类型")),
    ("subject_and_context", ("责任主体 / 场景 / 前置状态", "责任主体/场景/前置状态")),
    ("force_and_outcome", ("规范强度 / 行为或业务结果", "规范强度/行为或业务结果")),
    ("boundary", ("度量、时限或边界",)),
    ("source_rule_acceptance", ("来源与可靠性 / 关联规则 / 验收样例", "来源与可靠性/关联规则/验收样例")),
)
RULE_FIELD_GROUPS = (
    ("rule_name", ("规则名称",)),
    ("rule_type", ("规则性质",)),
    ("rule_motivation", ("业务动机",)),
    ("rule_scope", ("适用对象与范围", "适用场景 / 步骤", "适用场景/步骤")),
    ("rule_input_facts", ("输入事实",)),
    ("rule_condition", ("当", "触发与判断条件", "条件")),
    ("rule_outcome", ("则", "处理结果", "结论")),
    ("rule_owner", ("Owner", "规则 Owner", "规则 owner")),
    ("rule_examples", ("正例 / 边界例 / 反例", "验收样例")),
)
RULE_COMPACT_FIELD_GROUPS = (
    ("name_type_motivation", ("规则名称 / 性质 / 业务动机", "规则名称/性质/业务动机")),
    ("scenario_scope", ("适用场景 / 步骤", "适用场景/步骤")),
    ("object_and_facts", ("适用对象与范围 / 输入事实", "适用对象与范围/输入事实")),
    ("condition_outcome_owner", ("当 / 则 / Owner", "当/则/Owner")),
    ("examples", ("正例 / 边界例 / 反例",)),
)
DOCUMENT_CONTROL_FIELD_GROUPS = (
    ("current_version", ("当前版本",)),
    ("document_status", ("文档状态",)),
    ("product_owner", ("产品 owner", "产品 Owner")),
    ("business_owner", ("业务 owner", "业务 Owner")),
    ("updated_at", ("更新时间",)),
    ("authority_source", ("权威来源", "权威边界")),
)
ARCHITECTURE_SPINE_FIELD_GROUPS = (
    ("architecture_spine", ("产品架构主脊", "概要主链", "核心授权结构", "方案概述与核心方案")),
    ("core_capability", ("核心能力", "能力地图", "本期价值与范围")),
    ("core_object_relation", ("核心对象与关系", "核心名相", "核心概念与业务口径")),
    ("interaction_boundary", ("关键交互与边界", "参与方与责任", "分层责任边界")),
    ("view_choice", ("关键图 / 不画图理由", "关键图/不画图理由", "产品视图")),
)
PRODUCT_INTERFACE_FIELD_GROUPS = (
    ("interface_name", ("产品接口名称",)),
    ("interface_consumer", ("接口使用方",)),
    ("interface_input", ("接口输入与前置条件",)),
    ("interface_output", ("接口业务输出与副作用",)),
    ("interface_failure", ("接口失败语义",)),
    ("interface_boundary", ("接口责任边界",)),
)
AMBIGUOUS_BUSINESS_PHRASES = (
    "按相关规则处理",
    "视情况",
    "必要时",
    "适当",
    "及时",
    "合理",
    "尽快",
    "原则上",
    "包括但不限于",
)
NORMATIVE_FORCES = {"必须", "不得", "应", "可"}
PRD_STRENGTHS = {"轻量", "标准", "增强"}
SCENARIO_CONTRACT_STRENGTHS = {"标准", "增强"}
SCENARIO_RELATIONSHIPS = ("串联", "并行", "分支", "互斥", "独立")
PRD_SECTION_ORDER = [
    ("section_background", ("背景与问题",)),
    ("section_goal", ("目标与非目标",)),
    ("section_qualitative", ("定性与范围", "定性、范围")),
    ("section_overview", ("概要设计",)),
    ("section_detail", ("详细设计",)),
    ("section_requirements", ("产品需求陈述",)),
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
        "当前版本：1.0。\n文档状态：评审中。\n文档强度：标准。\n"
        "产品 owner：审核产品负责人。\n业务 owner：运营负责人。\n"
        "更新时间：2026-09-01 09:00 +08:00。\n权威来源：当前 PRD。\n"
        "## 阅读摘要\n当前结论：统一审核入口；产品定义 / 产品架构主脊：为运营提供可追踪的审核能力；主链路：提交、审核、通知；核心对象与边界：申请单由平台管理，不改变交易订单。\n"
        "## 一、背景与问题\n背景：审核积压影响运营；问题：人工路径不清。\n"
        "## 二、目标与非目标\n目标：缩短审核处理时间；非目标：不改结算规则。"
        "成功指标：当前审核中位处理时长基线为 24 小时，上线 30 天内目标降至 8 小时，观察窗口为上线后连续 30 天，Owner 为运营负责人。\n"
        "## 三、定性与范围\n产品定性：存量审核流程治理；总体判断：先统一口径；范围和产品边界为后台审核。\n"
        "## 四、概要设计\n概要设计：核心方案是统一审核入口和能力布局，并说明总体流程。\n"
        "产品架构主脊：缩短审核时长 -> SCN-001 -> 审核裁决能力 -> 申请状态 -> R-001 -> 可查询结论。\n"
        "核心能力：待审查询、审核裁决、异常转人工和审计查询。\n"
        "核心对象与关系：申请单产生当前审核任务，审核任务持有当前结论。\n"
        "关键交互与边界：审核员裁决，平台保存事实，运营处理异常。\n"
        "关键图 / 不画图理由：无需单独画图，单场景和三状态可由编号流程复述。\n"
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
        "### 产品需求陈述\n"
        "需求名称：保存唯一审核结论。\n需求类型：功能。\n责任主体：审核平台。\n"
        "场景 / 前置状态：SCN-001，申请处于待审状态。\n规范强度：必须。\n"
        "要求的行为或业务结果：审核平台必须保存唯一的当前审核结论并向审核员反馈。\n"
        "度量、时限或边界：同一申请重复裁决不得改变已形成的终态。\n"
        "来源与可靠性：运营审核规则，已确认。\n关联规则：R-001。\n"
        "验收样例：重复提交裁决时仍返回原终态和原审计记录。\n"
        "## 六、关键流程\n主流程：提交、审核、通知；异常流程：重复提交；人工处理：补录；流程图：审核路径。\n"
        "## 七、业务规则与接口抽象\n"
        "规则编号：R-001。规则名称：待审申请裁决。规则性质：场景裁决规则。"
        "业务动机：防止终态被重复操作覆盖。适用场景 / 步骤：SCN-001 / 审核裁决。"
        "适用对象与范围：待审申请。输入事实：申请状态和材料完整性。"
        "当：申请处于待审状态且材料完整。则：记录通过或驳回结论。"
        "Owner：运营负责人。正例 / 边界例 / 反例：待审申请可裁决；终态重复提交保持原结果；非待审申请不得生成新结论。"
        "产品接口名称：审核申请裁决。接口使用方：审核员。"
        "接口输入与前置条件：待审申请、材料和权限。"
        "接口业务输出与副作用：形成结论、变更状态并记录审计。"
        "接口失败语义：非待审返回原结论，来源不可用时保持待审。"
        "接口责任边界：平台保存事实，运营处理异常。\n"
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


def table_records(text: str, columns: dict[str, tuple[str, ...]]) -> list[dict[str, str]]:
    lines = text.splitlines()
    normalized_aliases = {
        name: {normalize(alias) for alias in aliases}
        for name, aliases in columns.items()
    }
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        headers = [cell.strip().strip("`*_").strip() for cell in line.strip().strip("|").split("|")]
        positions = {
            name: next(
                (position for position, header in enumerate(headers) if normalize(header) in aliases),
                None,
            )
            for name, aliases in normalized_aliases.items()
        }
        if any(position is None for position in positions.values()):
            continue
        records: list[dict[str, str]] = []
        for row in lines[index + 1 :]:
            if not row.strip().startswith("|"):
                break
            cells = [cell.strip().strip("`*_").strip() for cell in row.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            records.append({name: cells[position] if position < len(cells) else "" for name, position in positions.items()})
        return records
    return []


def contract_table_records(
    text: str,
    groups: tuple[tuple[str, tuple[str, ...]], ...],
    anchor_aliases: tuple[str, ...],
) -> list[dict[str, str]]:
    normalized_groups = {
        name: {normalize(alias) for alias in aliases}
        for name, aliases in groups
    }
    normalized_anchors = {normalize(alias) for alias in anchor_aliases}
    lines = text.splitlines()
    records: list[dict[str, str]] = []
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        headers = [cell.strip().strip("`*_").strip() for cell in line.strip().strip("|").split("|")]
        if not any(normalize(header) in normalized_anchors for header in headers):
            continue
        positions = {
            name: next(
                (position for position, header in enumerate(headers) if normalize(header) in aliases),
                None,
            )
            for name, aliases in normalized_groups.items()
        }
        for row in lines[index + 1 :]:
            if not row.strip().startswith("|"):
                break
            cells = [cell.strip().strip("`*_").strip() for cell in row.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            records.append({
                **{
                    name: cells[position] if position is not None and position < len(cells) else ""
                    for name, position in positions.items()
                },
                "__text__": "\n".join(
                    f"{header}: {cells[position] if position < len(cells) else ''}"
                    for position, header in enumerate(headers)
                ),
            })
    return records


def valid_stable_id(value: str) -> bool:
    return bool(re.fullmatch(r"[\w.:-]+", value, re.UNICODE)) and bool(meaningful_values([value]))


def is_standalone_html_prototype(text: str) -> bool:
    value = labeled_value(text, "原型交付形态")
    return bool(
        value
        and normalize(value)
        in {"standalone-html", "standalone html", "自包含 html"}
    )


def valid_html_annotation_anchor(value: str) -> bool:
    return bool(
        re.fullmatch(r"#[A-Za-z][A-Za-z0-9_-]*", value)
        or re.fullmatch(r'\[data-[a-z0-9-]+="[A-Za-z0-9_.:-]+"\]', value)
    )


def html_annotation_contract_issues(
    text: str,
    requirement_pairs: set[tuple[str, str]],
    carriers: list[dict[str, str]],
    traces: list[dict[str, str]],
) -> list[str]:
    if not is_standalone_html_prototype(text):
        return []

    body = section_body(text, ("HTML 原型标注契约",))
    if not body:
        return ["html_annotation_contract_missing"]

    issues: list[str] = []
    contract_values = {
        "默认模式": "experience",
        "审阅入口": "review-query-or-toggle",
        "标注数据源": "embedded-json",
        "模式隔离": "preserve-task-state",
        "可访问性": "keyboard-and-name",
    }
    if not has_meaningful_labeled_value(body, "原型修订") or any(
        not has_meaningful_labeled_value(body, label) for label in contract_values
    ):
        issues.append("html_annotation_contract_incomplete")
    elif any(
        normalize(labeled_value(body, label) or "") != expected
        for label, expected in contract_values.items()
    ):
        issues.append("html_annotation_contract_invalid")

    product_annotations = table_records(
        section_body(text, ("产品级页面标注",)),
        {
            "annotation_id": ("标注 ID",),
            "carrier_id": ("承接 ID",),
            "business_object": ("业务对象", "字段或内容"),
            "rule": ("前置条件 / 规则", "前置条件/规则"),
            "permission": ("权限",),
            "action_state": ("动作与状态变化",),
            "feedback": ("必须反馈的结果 / 异常", "必须反馈的结果/异常"),
            "data_source": ("数据来源 / 时效", "数据来源/时效"),
            "audit": ("埋点 / 审计", "埋点/审计"),
            "acceptance_id": ("AC", "AC ID"),
        },
    )
    if not product_annotations or any(
        not valid_stable_id(row["annotation_id"])
        or not valid_stable_id(row["carrier_id"])
        or not valid_stable_id(row["acceptance_id"])
        or not all(
            meaningful_values([row[field]])
            for field in (
                "business_object",
                "rule",
                "permission",
                "action_state",
                "feedback",
                "data_source",
                "audit",
            )
        )
        for row in product_annotations
    ):
        issues.append("html_annotation_product_facts_invalid")
    product_annotation_ids = [row["annotation_id"] for row in product_annotations]
    if len(product_annotation_ids) != len(set(product_annotation_ids)):
        issues.append("duplicate_product_annotation_id")

    annotations = table_records(
        body,
        {
            "annotation_id": ("标注 ID",),
            "carrier_id": ("承接 ID",),
            "anchor": ("HTML 锚点",),
            "annotation_type": ("类型", "标注类型"),
            "fact_status": ("事实状态",),
            "requirement_id": ("需求 ID",),
            "acceptance_id": ("AC ID",),
            "owner": ("Owner", "负责人"),
        },
    )
    if not annotations:
        return issues + ["html_annotation_table_missing"]

    if any(
        not all(
            valid_stable_id(row[field])
            for field in ("annotation_id", "carrier_id", "requirement_id", "acceptance_id")
        )
        or normalize(row["annotation_type"])
        not in {"scope", "范围", "content", "内容", "rule", "规则", "interaction", "交互", "trace", "追踪"}
        or normalize(row["fact_status"])
        not in {"confirmed", "已确认", "inferred", "推断", "pending", "待确认"}
        or not meaningful_values([row["owner"]])
        for row in annotations
    ):
        issues.append("html_annotation_invalid")
    if any(not valid_html_annotation_anchor(row["anchor"]) for row in annotations):
        issues.append("html_annotation_anchor_invalid")

    annotation_ids = [row["annotation_id"] for row in annotations]
    if len(annotation_ids) != len(set(annotation_ids)):
        issues.append("duplicate_html_annotation_id")

    product_annotations_by_id = {
        row["annotation_id"]: row
        for row in product_annotations
        if meaningful_values([row["annotation_id"]])
    }
    if set(annotation_ids) != set(product_annotations_by_id) or any(
        row["annotation_id"] in product_annotations_by_id
        and (
            row["carrier_id"] != product_annotations_by_id[row["annotation_id"]]["carrier_id"]
            or row["acceptance_id"] != product_annotations_by_id[row["annotation_id"]]["acceptance_id"]
        )
        for row in annotations
    ):
        issues.append("html_annotation_fact_reference_missing")

    carrier_ids = {row["carrier_id"] for row in carriers}
    annotation_pairs = {(row["requirement_id"], row["acceptance_id"]) for row in annotations}
    annotation_triples = {
        (row["requirement_id"], row["acceptance_id"], row["carrier_id"])
        for row in annotations
    }
    trace_triples = {
        (row["requirement_id"], row["acceptance_id"], row["carrier_id"])
        for row in traces
        if meaningful_values([row["carrier_id"]])
    }
    if {row["carrier_id"] for row in annotations} - carrier_ids:
        issues.append("unknown_html_annotation_carrier")
    if annotation_pairs - requirement_pairs:
        issues.append("unknown_html_annotation_requirement")
    if annotation_triples - trace_triples:
        issues.append("html_annotation_trace_mismatch")

    carrier_types = {row["carrier_id"]: normalize(row["carrier_type"]) for row in carriers}
    page_carrier_types = {"页面", "page", "页面状态", "状态", "state"}
    if any(
        row["carrier_id"] in carrier_types
        and carrier_types[row["carrier_id"]] not in page_carrier_types
        for row in annotations
    ):
        issues.append("html_annotation_non_page_carrier")
    required_page_triples = {
        (row["requirement_id"], row["acceptance_id"], row["carrier_id"])
        for row in traces
        if normalize(row["posture"]) in {"required", "必需"}
        and normalize(row["coverage"]) in {"已覆盖", "covered"}
        and carrier_types.get(row["carrier_id"]) in page_carrier_types
    }
    if required_page_triples - annotation_triples:
        issues.append("html_annotation_required_coverage_missing")
    return issues


def prototype_scope_issues(text: str) -> list[str]:
    requirements = table_records(
        text,
        {
            "requirement_id": ("需求 ID",),
            "acceptance_id": ("AC ID",),
            "role": ("角色",),
            "application": ("应用",),
            "client": ("客户端",),
            "status": ("状态",),
        },
    )
    carriers = table_records(
        text,
        {
            "carrier_id": ("承接 ID",),
            "carrier_type": ("类型",),
            "application": ("应用",),
            "client": ("客户端",),
            "owner": ("Owner", "负责人"),
        },
    )
    traces = table_records(
        text,
        {
            "requirement_id": ("需求 ID",),
            "acceptance_id": ("AC ID",),
            "carrier_id": ("承接 ID",),
            "posture": ("关系姿态",),
            "coverage": ("覆盖状态",),
            "owner": ("Owner", "负责人"),
            "handling": ("未覆盖前处理",),
        },
    )
    issues: list[str] = []
    if not requirements:
        issues.append("requirement_coverage_table_missing")
    if not carriers:
        issues.append("carrier_inventory_table_missing")
    if not traces:
        issues.append("prototype_trace_table_missing")
    if issues:
        return issues

    requirement_pairs = {(row["requirement_id"], row["acceptance_id"]) for row in requirements}
    trace_pairs = {(row["requirement_id"], row["acceptance_id"]) for row in traces}
    carrier_ids = {row["carrier_id"] for row in carriers}
    used_carriers = {row["carrier_id"] for row in traces if meaningful_values([row["carrier_id"]])}

    if any(not valid_stable_id(row[field]) for row in requirements for field in ("requirement_id", "acceptance_id")):
        issues.append("requirement_id_invalid")
    if any(
        not all(meaningful_values([row[field]]) for field in ("role", "application", "client"))
        or not row["status"].strip()
        or PLACEHOLDER_FIELD.search(row["status"])
        for row in requirements
    ):
        issues.append("requirement_coverage_invalid")
    if len(requirement_pairs) != len(requirements):
        issues.append("duplicate_requirement_trace_source")
    if any(
        not valid_stable_id(row["carrier_id"])
        or normalize(row["carrier_type"]) not in {"页面", "page", "页面状态", "状态", "state", "非页面能力", "non-page"}
        or not all(meaningful_values([row[field]]) for field in ("application", "client", "owner"))
        for row in carriers
    ):
        issues.append("carrier_inventory_invalid")
    if len(carrier_ids) != len(carriers):
        issues.append("duplicate_carrier_id")
    if len({(row["requirement_id"], row["acceptance_id"], row["carrier_id"]) for row in traces}) != len(traces):
        issues.append("duplicate_prototype_trace")
    if requirement_pairs - trace_pairs:
        issues.append("requirement_trace_missing")
    if trace_pairs - requirement_pairs:
        issues.append("unknown_requirement_trace")
    if used_carriers - carrier_ids:
        issues.append("unknown_carrier_reference")
    if carrier_ids - used_carriers:
        issues.append("orphan_carrier")
    if any(normalize(row["posture"]) not in {"required", "必需", "target", "目标", "informational", "信息性", "optional", "可选"} for row in traces):
        issues.append("relationship_posture_invalid")
    if any(normalize(row["coverage"]) not in {"已覆盖", "covered", "待覆盖", "pending", "不适用", "not-applicable"} for row in traces):
        issues.append("coverage_status_invalid")
    if any(
        normalize(row["coverage"]) in {"已覆盖", "covered"}
        and not meaningful_values([row["carrier_id"]])
        for row in traces
    ):
        issues.append("covered_carrier_missing")

    unresolved = [row for row in traces if normalize(row["coverage"]) not in {"已覆盖", "covered"}]
    if any(
        normalize(row["posture"]) in {"required", "必需"}
        and (normalize(row["coverage"]) not in {"已覆盖", "covered"} or not meaningful_values([row["carrier_id"]]))
        for row in traces
    ):
        issues.append("required_coverage_missing")
    if any(not meaningful_values([row["owner"]]) for row in unresolved):
        issues.append("unresolved_coverage_owner_missing")
    if any(not meaningful_values([row["handling"]]) for row in unresolved):
        issues.append("unresolved_coverage_handling_missing")
    issues.extend(html_annotation_contract_issues(text, requirement_pairs, carriers, traces))
    return issues


def scenario_contract_issues(text: str) -> list[str]:
    blocks = scenario_blocks(section_body(text, ("详细设计",)))
    if not blocks:
        return ["scenario_contract_missing"]
    scenario_ids = [match.group(0).upper() for title, _ in blocks if (match := SCENARIO_ID_PATTERN.search(title))]
    issues: list[str] = []
    if len(scenario_ids) != len(set(scenario_ids)):
        issues.append("duplicate_scenario_ids")
    def complete(body: str, groups: tuple[tuple[str, tuple[str, ...]], ...]) -> bool:
        return all(has_meaningful_alias_value(body, aliases) for _, aliases in groups)

    if any(
        not complete(body, SCENARIO_SHORT_FIELD_GROUPS)
        and not complete(body, SCENARIO_NARRATIVE_FIELD_GROUPS)
        and not complete(body, SCENARIO_LEGACY_FIELD_GROUPS)
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


def contract_group_values(text: str, aliases: tuple[str, ...]) -> list[str]:
    values = [value for alias in aliases for value in field_values(text, alias)]
    values.extend(table_column_values(text, aliases))
    return meaningful_values(values)


def labeled_record_blocks(text: str, anchor_aliases: tuple[str, ...]) -> list[str]:
    anchors = "|".join(re.escape(alias) for alias in anchor_aliases)
    pattern = re.compile(
        rf"(?m)^\s*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*|__|`)?\s*"
        rf"(?:{anchors})\s*(?:\*\*|__|`)?\s*[：:]"
    )
    matches = list(pattern.finditer(text))
    if not matches:
        return []
    return [
        text[match.start() : matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        for index, match in enumerate(matches)
    ]


def contract_records(
    text: str,
    groups: tuple[tuple[str, tuple[str, ...]], ...],
    anchor_aliases: tuple[str, ...],
) -> list[dict[str, str]]:
    rows = contract_table_records(text, groups, anchor_aliases)
    narrative_text = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("|")
    )
    blocks = labeled_record_blocks(narrative_text, anchor_aliases)
    if not rows and not blocks:
        blocks = [narrative_text]
    narrative_records = [
        {
            **{
                name: " ".join(contract_group_values(block, aliases))
                for name, aliases in groups
            },
            "__text__": block,
        }
        for block in blocks
    ]
    return rows + narrative_records


def business_rule_records(text: str) -> list[dict[str, str]]:
    rows = contract_table_records(text, RULE_FIELD_GROUPS, ("规则编号", "规则名称"))
    narrative = "\n".join(line for line in text.splitlines() if not line.strip().startswith("|"))
    blocks = labeled_record_blocks(narrative, ("规则编号", "规则名称"))
    merged: list[str] = []
    pending_identifier = ""
    numbered = re.compile(
        r"^\s*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*|__|`)?\s*规则编号\s*(?:\*\*|__|`)?\s*[：:]"
    )
    for block in blocks:
        starts_with_number = bool(numbered.match(block))
        identifier_only = starts_with_number and not any(
            contract_group_values(block, aliases) for _, aliases in RULE_FIELD_GROUPS
        )
        if pending_identifier and starts_with_number:
            merged.append(pending_identifier)
            pending_identifier = ""
        if identifier_only:
            pending_identifier = block
            continue
        if pending_identifier:
            block = f"{pending_identifier}\n{block}"
            pending_identifier = ""
        merged.append(block)
    if pending_identifier:
        merged.append(pending_identifier)
    if not rows and not merged:
        merged = [narrative]
    return rows + [
        {
            **{
                name: " ".join(contract_group_values(block, aliases))
                for name, aliases in RULE_FIELD_GROUPS
            },
            "__text__": block,
        }
        for block in merged
    ]


def phrase_is_defined(text: str, phrase: str) -> bool:
    numeric_definition = re.search(
        rf"{re.escape(phrase)}\s*(?:定义为|是指|[：:])\s*[^。；;\n]{{0,40}}"
        rf"\d+(?:\.\d+)?\s*(?:毫秒|秒|分钟|小时|天|次|个|%|％)",
        text,
        re.IGNORECASE,
    )
    named_deadline = re.search(
        rf"{re.escape(phrase)}\s*(?:定义为|是指|[：:])\s*"
        rf"(?:当日|次日|本工作日|下一个工作日|SLA\s*[-:：]?\s*\w+|[^。；;\n]{{1,30}}(?:之前|结束前|开始前))",
        text,
        re.IGNORECASE,
    )
    return bool(numeric_definition or named_deadline)


def ambiguous_business_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    for phrase in AMBIGUOUS_BUSINESS_PHRASES:
        candidate = text.replace("合理推断", "") if phrase == "合理" else text
        if contains_term(candidate, phrase) and not phrase_is_defined(candidate, phrase):
            phrases.append(phrase)
    return phrases


def slash_group_complete(values: list[str], expected_parts: int) -> bool:
    for value in values:
        parts = [part.strip().strip("。") for part in value.split("/")]
        if len(parts) < expected_parts or any(
            not meaningful_values([part]) for part in parts[:expected_parts]
        ):
            return False
    return bool(values)


def requirement_contract_issues(text: str) -> list[str]:
    requirements = section_body(text, ("产品需求陈述",))
    if not requirements.strip():
        return ["requirement_contract_missing"]
    issues: list[str] = []
    compact_values = {
        name: [
            value
            for alias in aliases
            for value in field_values(requirements, alias)
        ]
        for name, aliases in REQUIREMENT_COMPACT_FIELD_GROUPS
    }
    if all(compact_values.values()):
        if any(len(values) != 1 for values in compact_values.values()):
            return ["requirement_contract_incomplete"]
        expected_parts = {
            "name_and_type": 2,
            "subject_and_context": 3,
            "force_and_outcome": 2,
            "boundary": 1,
            "source_rule_acceptance": 3,
        }
        if any(
            not slash_group_complete(compact_values[name], count)
            for name, count in expected_parts.items()
        ):
            issues.append("requirement_contract_incomplete")
        force = compact_values["force_and_outcome"][0]
        if re.match(r"\s*(必须|不得|应|可)(?:\s*/|$)", force) is None:
            issues.append("normative_force_invalid")
        if ambiguous_business_phrases(requirements):
            issues.append("ambiguous_requirement_language")
        return issues
    records = contract_records(requirements, REQUIREMENT_FIELD_GROUPS, ("需求名称",))
    if any(any(not record[name] for name, _ in REQUIREMENT_FIELD_GROUPS) for record in records):
        issues.append("requirement_contract_incomplete")
    if any(
        normalize(record["normative_force"]).rstrip("。.") not in NORMATIVE_FORCES
        for record in records
        if record["normative_force"]
    ):
        issues.append("normative_force_invalid")
    if any(ambiguous_business_phrases(record["__text__"]) for record in records):
        issues.append("ambiguous_requirement_language")
    return issues


def business_rule_contract_issues(text: str) -> list[str]:
    rules = section_body(text, ("业务规则与接口抽象", "业务规则和接口抽象"))
    issues: list[str] = []
    compact_values = {
        name: [
            value
            for alias in aliases
            for value in field_values(rules, alias)
        ]
        for name, aliases in RULE_COMPACT_FIELD_GROUPS
    }
    if all(compact_values.values()):
        if any(len(values) != 1 for values in compact_values.values()):
            return ["rule_contract_incomplete"]
        expected_parts = {
            "name_type_motivation": 3,
            "scenario_scope": 2,
            "object_and_facts": 2,
            "condition_outcome_owner": 3,
            "examples": 3,
        }
        if any(
            not slash_group_complete(compact_values[name], count)
            for name, count in expected_parts.items()
        ):
            issues.append("rule_contract_incomplete")
        if ambiguous_business_phrases(rules):
            issues.append("ambiguous_rule_language")
        rule_identity = compact_values["name_type_motivation"][0]
        if "版本化" in rule_identity or "外部规则" in rule_identity:
            external_groups = (
                ("来源",),
                ("版本",),
                ("生效期", "生效范围"),
                ("Owner", "规则 Owner", "规则 owner"),
                ("未确认前处理", "失效时处理", "外部不可用"),
            )
            if any(
                not contract_group_values(rules, aliases)
                for aliases in external_groups
            ):
                issues.append("external_rule_governance_missing")
        return issues
    records = business_rule_records(rules)
    if any(any(not record[name] for name, _ in RULE_FIELD_GROUPS) for record in records):
        issues.append("rule_contract_incomplete")
    if any(ambiguous_business_phrases(record["__text__"]) for record in records):
        issues.append("ambiguous_rule_language")

    for record in records:
        if "版本化" not in record["rule_type"] and "外部规则" not in record["rule_type"]:
            continue
        external_groups = (
            ("来源",),
            ("版本",),
            ("生效期", "生效范围"),
            ("Owner", "规则 Owner", "规则 owner"),
            ("未确认前处理", "失效时处理", "外部不可用"),
        )
        if any(not contract_group_values(record["__text__"], aliases) for aliases in external_groups):
            issues.append("external_rule_governance_missing")
            break
    return issues


def declared_scenario_relationship(detail: str) -> str | None:
    values = field_values(detail, "场景关系")
    if len(values) != 1:
        return None
    normalized = normalize(values[0])
    matches = [
        relation
        for relation in SCENARIO_RELATIONSHIPS
        if normalized.startswith(normalize(relation))
    ]
    return matches[0] if len(matches) == 1 else None


def scenario_relationship_issues(text: str) -> list[str]:
    detail = section_body(text, ("详细设计",))
    if len(scenario_blocks(detail)) <= 1:
        return []
    values = field_values(detail, "场景关系")
    if not values:
        legacy_flow = any(
            "关键流程" in heading and "跨场景" not in heading
            for heading, _ in markdown_sections(text)
        )
        return [] if legacy_flow else ["scenario_relationship_missing"]
    return [] if declared_scenario_relationship(detail) else ["scenario_relationship_invalid"]


def cross_scenario_flow_issues(text: str) -> list[str]:
    detail = section_body(text, ("详细设计",))
    scenarios = scenario_blocks(detail)
    if len(scenarios) <= 1:
        return []
    relationship_issues = scenario_relationship_issues(text)
    if relationship_issues:
        return []
    if declared_scenario_relationship(detail) == "独立":
        return []
    shared_flow = section_body(detail, ("跨场景端到端流程", "跨场景关键流程"))
    if not shared_flow.strip():
        shared_flow = section_body(text, ("关键流程",))
    return [] if shared_flow.strip() else ["cross_scenario_flow_missing"]


def cross_scenario_view_contract_issues(text: str) -> list[str]:
    detail = section_body(text, ("详细设计",))
    headings = list(re.finditer(r"(?m)^(#{2,6})\s+(.+?)\s*$", detail))
    target: tuple[int, str] | None = None
    for index, heading in enumerate(headings):
        title = normalize(heading.group(2))
        if "图形视图" not in title or not any(
            alias in title for alias in ("跨场景端到端流程", "跨场景关键流程")
        ):
            continue
        level = len(heading.group(1))
        end = len(detail)
        for following in headings[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        target = (level, detail[heading.end() : end])
        break
    if target is None:
        return []

    level, body = target
    normalized = normalize(body)

    def assigned_values(labels: tuple[str, ...]) -> list[str]:
        values = [value for label in labels for value in field_values(body, label)]
        for label in labels:
            pattern = re.compile(
                rf"(?:^|[；;\n])\s*{re.escape(label)}\s*=\s*([^；;\n]+)",
                re.IGNORECASE,
            )
            values.extend(match.group(1).strip() for match in pattern.finditer(body))
        return meaningful_values(values)

    has_scope = (
        any(marker in normalized for marker in ("作用边界", "只表达", "只描述", "只展开"))
        and any(marker in normalized for marker in ("场景关系", "分支关系", "责任交接", "共享生命周期", "状态变化"))
        and any(marker in normalized for marker in ("不重复", "不复述"))
    )
    has_coverage = bool(
        assigned_values(("实际覆盖", "覆盖场景", "覆盖范围", "覆盖"))
        or re.search(
            r"(?:实际)?覆盖[^。；\n]{1,80}(?:(?:SCN|UC)-[A-Z0-9-]+|场景|流程|路径)",
            body,
            re.IGNORECASE,
        )
    )
    has_trace = (
        all(marker in normalized for marker in ("规则", "风险", "验收"))
        and any(marker in normalized for marker in ("追踪", "回链", "入口", "关联", "见第"))
    )

    issues: list[str] = []
    if not all((has_scope, has_coverage, has_trace)):
        issues.append("cross_scenario_view_contract_incomplete")
    if level >= 3 and re.search(
        r"本章\s*(?:只|主要|用于)(?:描述|展开|表达|说明)?", body
    ):
        issues.append("cross_scenario_heading_level_mismatch")

    expression_values = assigned_values(("表达选择", "表达方式", "图形选择", "首选图形"))
    has_expression_choice = bool(expression_values) or bool(
        re.search(
            r"(?:采用|使用|选择)[^。；\n]{0,30}(?:编号|流程图|泳道图|状态机|用例图|能力地图|图形)",
            body,
        )
    )
    has_visual = bool(
        re.search(
            r"!\[[^\]]*\]\([^)]+\)|\[[^\]]+\]\([^)]+\.(?:svg|png|jpe?g|webp)(?:#[^)]*)?\)|"
            r"```(?:mermaid|dot|plantuml)|~~~(?:mermaid|dot|plantuml)",
            body,
            re.IGNORECASE,
        )
    )
    if not has_visual:
        has_numbered_rationale = (
            has_expression_choice
            and "编号" in normalized
            and any(marker in normalized for marker in ("足够", "足以", "已经能够", "可以说明", "可说明", "即可"))
            and bool(re.search(r"(?:无须|无需|不需要|不)[^。；\n]{0,40}(?:图|图形)", body))
        )
        if not has_numbered_rationale:
            issues.append("cross_scenario_expression_rationale_missing")
    return issues


def conditional_flow_order_issues(text: str) -> list[str]:
    heading_matches = list(re.finditer(r"(?m)^(#{2,6})\s+(.+?)\s*$", text))
    headings = [normalize(match.group(2)) for match in heading_matches]
    flows = matching_heading_positions(
        headings, ("跨场景端到端流程", "跨场景关键流程", "关键流程")
    )
    if not flows:
        return []
    details = matching_heading_positions(headings, ("详细设计",))
    requirements = matching_heading_positions(headings, ("产品需求陈述",))
    rules = matching_heading_positions(
        headings, ("业务规则与接口抽象", "业务规则和接口抽象")
    )
    embedded_flow = "跨场景" in headings[flows[0]] if len(flows) == 1 else False
    legacy_order_valid = (
        len(flows) == 1
        and len(details) == 1
        and len(rules) == 1
        and details[0] < flows[0] < rules[0]
    )
    embedded_order_valid = (
        legacy_order_valid
        and len(requirements) == 1
        and flows[0] < requirements[0]
        and len(heading_matches[flows[0]].group(1))
        > len(heading_matches[details[0]].group(1))
    )
    if (
        len(flows) != 1
        or len(details) != 1
        or len(rules) != 1
        or (embedded_flow and not embedded_order_valid)
        or (not embedded_flow and not legacy_order_valid)
    ):
        return ["conditional_flow_order"]
    return []


def document_control_issues(text: str) -> list[str]:
    return ["document_control_incomplete"] if any(
        not has_meaningful_alias_value(text, aliases)
        for _, aliases in DOCUMENT_CONTROL_FIELD_GROUPS
    ) else []


def architecture_spine_issues(text: str) -> list[str]:
    detail = re.search(r"(?m)^#{2,6}\s+.*详细设计.*$", text)
    early_product_design = text[: detail.start()] if detail else text

    def present(aliases: tuple[str, ...]) -> bool:
        return has_meaningful_alias_value(early_product_design, aliases) or bool(
            section_body(early_product_design, aliases).strip()
        )

    return ["architecture_spine_incomplete"] if any(
        not present(aliases)
        for _, aliases in ARCHITECTURE_SPINE_FIELD_GROUPS
    ) else []


def has_compact_product_interface_contract(text: str) -> bool:
    rules_and_interface = section_body(
        text, ("业务规则与接口抽象", "业务规则和接口抽象")
    )
    for line in rules_and_interface.splitlines():
        if not line.strip().startswith("|"):
            continue
        headers = [normalize(cell) for cell in line.strip().strip("|").split("|")]
        has_name = any(header in {"产品能力", "产品接口"} for header in headers)
        has_input = any(header in {"输入与前置", "输入与前置条件"} for header in headers)
        has_output_failure = any(
            header in {"输出与失败语义", "业务输出与失败语义"} for header in headers
        )
        if has_name and has_input and has_output_failure:
            return True
    return False


def has_full_product_interface_contract(text: str) -> bool:
    rules_and_interface = section_body(
        text, ("业务规则与接口抽象", "业务规则和接口抽象")
    )
    return all(
        has_meaningful_alias_value(rules_and_interface, aliases)
        for _, aliases in PRODUCT_INTERFACE_FIELD_GROUPS
    )


def product_interface_contract_issues(text: str) -> list[str]:
    return [] if (
        has_full_product_interface_contract(text)
        or has_compact_product_interface_contract(text)
    ) else ["product_interface_contract_incomplete"]


def success_metric_issues(text: str) -> list[str]:
    goals = section_body(text, ("目标与非目标",))
    marker = goals.find("成功指标")
    if marker < 0:
        return ["success_metric_incomplete"]
    normalized = normalize(goals[marker:])

    def has_value(pattern: str) -> bool:
        match = re.search(pattern, normalized)
        return bool(match and meaningful_values([match.group(1)]))

    has_baseline = has_value(r"基线(?:值)?\s*(?:为|[：:])\s*([^；;。]+)")
    no_history_baseline = bool(
        re.search(r"(?:无|暂无)历史基线|基线(?:尚未建立|待建立)", normalized)
    )
    has_baseline_plan = has_value(
        r"(?:基线建立方式|基线采集计划|基线测量计划)\s*(?:为|[：:])\s*([^；;。]+)"
    )
    has_baseline = has_baseline or (no_history_baseline and has_baseline_plan)
    has_target = bool(
        has_value(r"(?<!非)目标(?:值|状态)?\s*(?:为|降至|达到|提升至|[：:])\s*([^；;。，,]+)")
        or has_value(r"(?:降至|提升至|达到)\s*([^；;。，,]+)")
    )
    has_window = has_value(r"观察窗口\s*(?:为|[：:])\s*([^；;。]+)") or bool(
        re.search(r"上线(?:后)?\s*\d+\s*(?:天|小时|周|个月)内", normalized)
    )
    has_owner = has_value(r"(?:owner|负责人)\s*(?:为|[：:])\s*([^；;。]+)")
    return [] if all((has_baseline, has_target, has_window, has_owner)) else ["success_metric_incomplete"]


def lightweight_prd_contract_issues(text: str) -> list[str]:
    issues: list[str] = []
    if scenario_contract_issues(text):
        issues.append("lightweight_scenario_incomplete")

    detail = section_body(text, ("详细设计",))
    projected_requirement = f"## 产品需求陈述\n{detail}"
    if requirement_contract_issues(projected_requirement):
        issues.append("lightweight_requirement_incomplete")

    acceptance = section_body(text, ("验收摘要",))
    has_observable_result = any(
        contains_term(acceptance, marker)
        for marker in ("显示", "保留", "可查询", "可操作", "通知", "记录", "状态")
    )
    has_boundary = any(
        contains_term(acceptance, marker)
        for marker in ("不得", "禁止", "边界", "失败", "恢复", "重试", "人工")
    )
    has_acceptance_owner = any(
        contains_term(acceptance, marker)
        for marker in ("验收 Owner", "产品负责人", "业务负责人", "运营确认", "业务确认")
    )
    if not all((acceptance.strip(), has_observable_result, has_boundary, has_acceptance_owner)):
        issues.append("lightweight_acceptance_incomplete")
    return issues


def has_rule_scope(text: str) -> bool:
    rules = section_body(text, ("业务规则与接口抽象", "业务规则和接口抽象"))
    rule_types = (
        field_values(rules, "规则性质")
        or field_values(rules, "规则名称 / 性质 / 业务动机")
        or field_values(rules, "规则名称/性质/业务动机")
        or table_column_values(rules, ("规则性质",))
    )
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


def _goal_statement_body(text: str) -> str:
    goals = section_body(text, ("目标与非目标",))
    boundaries = [
        position
        for marker in ("成功指标", "成功标准", "本期非目标", "本期不做", "非目标")
        if (position := goals.find(marker)) >= 0
    ]
    return goals[: min(boundaries)] if boundaries else goals


def goal_mechanism_leak(text: str) -> bool:
    goal_body = _goal_statement_body(text)
    mechanism_markers = (
        "resourceId",
        "httpMethod",
        "Provider",
        "scopeType",
        "explicitRefs",
        "schema",
        "SQL",
        "Repository",
        "Handler",
        "Mapper",
        "HTTP_METHOD",
        "字段组合",
        "取并集",
        "并集",
        "交集",
        "路由算法",
    )
    return sum(1 for marker in mechanism_markers if contains_term(goal_body, marker)) >= 3


def non_goal_current_concept_conflict(text: str) -> bool:
    goals = section_body(text, ("目标与非目标",))
    starts = [
        position
        for marker in ("本期非目标", "本期不做", "非目标")
        if (position := goals.find(marker)) >= 0
    ]
    if not starts:
        return False
    non_goals = goals[min(starts) :]
    excluded_identifiers = set(re.findall(r"`([A-Z][A-Za-z0-9_]{4,})`", non_goals))
    if not excluded_identifiers:
        return False
    concepts = section_body(text, ("核心概念与业务口径",))
    current_rows = "\n".join(
        line for line in concepts.splitlines() if re.search(r"\|\s*当前\s*\|", line)
    )
    current_identifiers = set(re.findall(r"`([A-Z][A-Za-z0-9_]{4,})`", current_rows))
    return bool(excluded_identifiers & current_identifiers)


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
    product_view = re.search(
        r"产品定义\s*/\s*(?:产品视图|产品架构主脊)|产品视图|产品架构主脊",
        text,
    )
    if detail_design and product_view and product_view.start() > detail_design.start():
        warnings.append("product_view_late")
    if any(contains_term(text, term) for term in IMPLEMENTATION_LANGUAGE_TERMS):
        warnings.append("implementation_language")
    if declared_prd_strength(text) == "轻量" and ambiguous_business_phrases(text):
        warnings.append("ambiguous_business_language")
    if goal_mechanism_leak(text):
        warnings.append("goal_mechanism_leak")
    if non_goal_current_concept_conflict(text):
        warnings.append("non_goal_current_concept_conflict")
    if (
        has_compact_product_interface_contract(text)
        and not has_full_product_interface_contract(text)
    ):
        warnings.append("compact_product_interface_contract")
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
        missing.extend(document_control_issues(text))
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
        if strength == "轻量":
            missing.extend(lightweight_prd_contract_issues(text))
        if strength in SCENARIO_CONTRACT_STRENGTHS:
            missing.extend(architecture_spine_issues(text))
            missing.extend(product_interface_contract_issues(text))
            missing.extend(scenario_contract_issues(text))
            missing.extend(scenario_relationship_issues(text))
            missing.extend(cross_scenario_flow_issues(text))
            missing.extend(cross_scenario_view_contract_issues(text))
            missing.extend(conditional_flow_order_issues(text))
            missing.extend(success_metric_issues(text))
            missing.extend(requirement_contract_issues(text))
            missing.extend(business_rule_contract_issues(text))
            if not has_rule_scope(text):
                missing.append("rule_scope_missing")
            missing.extend(rule_scenario_issues(text))
            missing.extend(acceptance_scenario_issues(text))
    if kind == "prototype-scope-plan":
        missing.extend(prototype_scope_issues(text))
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
    if "prototype-scope-plan" not in CHECKS:
        failures.append("prototype-scope-plan: missing deliverable kind")
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
        .replace("## 五、详细设计\n", "## 五、详细设计与产品需求陈述\n", 1)
        .replace("### 产品需求陈述\n", "", 1)
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
        "当前版本：1.0。\n文档状态：评审中。\n文档强度：轻量。\n"
        "产品 owner：审核产品负责人。\n业务 owner：运营负责人。\n"
        "更新时间：2026-09-01 09:00 +08:00。\n权威来源：当前 PRD。\n"
        "## 一、背景、问题与目标\n背景：审核积压；问题：处理路径不清；目标：缩短时长；非目标：不改交易。\n"
        "## 二、定性、范围与概要\n产品定性：流程治理；总体判断：统一入口；范围和产品边界为后台审核。"
        "概要设计采用统一入口；方案概述说明申请如何流转。核心名相为审核任务，定义是待处理申请。"
        "用户为运营，角色是审核员，责任边界不变。\n"
        "## 三、详细设计与业务场景\n本节说明审核员处理待审核申请的责任推进与失败收口。\n"
        "### SCN-001 审核员处理申请单\n"
        "业务情境：运营收到一条待审核申请，需要在当前工作台完成裁决。\n"
        "责任推进：审核员核对申请事实并提交通过或拒绝结论，工作台记录结果。\n"
        "裁决与状态：只有具备审核权限且事实完整时才能提交，提交后申请从待审核变为已裁决。\n"
        "异常与收口：事实缺失时保持待审核并提示补充，重复提交时显示既有结果并停止再次裁决。\n"
        "需求名称：审核裁决。需求类型：功能。责任主体：审核员。"
        "场景 / 前置状态：SCN-001，申请为待审核。规范强度：必须。"
        "要求的行为或业务结果：审核员提交后记录唯一裁决结果。"
        "度量、时限或边界：无审核权限不得提交。来源与可靠性：当前 PRD，已确认。"
        "关联规则：审核权限规则。验收样例：提交通过后申请显示已通过。\n"
        "## 四、流程、规则与产品接口\n主流程是提交、审核、通知；异常流程处理重复请求和人工处理。"
        "规则覆盖权限和审批。产品接口抽象说明业务契约、输入、输出和失败语义。\n"
        "## 五、数据、风险与待确认\n数据包括指标、报表和审计。风险和依赖待确认，确认方为业务，影响范围为上线。\n"
        "## 六、验收摘要\n业务结果：申请提交后显示唯一裁决状态；"
        "关键边界与红线：无审核权限不得提交，重复提交不得产生第二个结果；"
        "验收标准：产品负责人确认状态可查询，业务负责人确认异常时可恢复处理。"
    )
    light_prd_missing = missing_groups("prd", light_prd)
    if light_prd_missing:
        failures.append(
            "prd: merged lightweight document unexpectedly failed: "
            + ", ".join(light_prd_missing)
        )
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
    missing_requirement_prd = SELF_TESTS["prd"][0].replace(
        "### 产品需求陈述", "### 未命名内容", 1
    )
    if "requirement_contract_missing" not in missing_groups("prd", missing_requirement_prd):
        failures.append("prd: missing requirement contract unexpectedly passed")
    ambiguous_rule_prd = SELF_TESTS["prd"][0].replace(
        "当：申请处于待审状态且材料完整。",
        "当：按相关规则处理并视情况及时裁决。",
        1,
    )
    if "ambiguous_rule_language" not in missing_groups("prd", ambiguous_rule_prd):
        failures.append("prd: ambiguous business rule unexpectedly passed")
    external_rule_prd = SELF_TESTS["prd"][0].replace(
        "规则性质：场景裁决规则。", "规则性质：版本化 / 外部规则。", 1
    )
    if "external_rule_governance_missing" not in missing_groups("prd", external_rule_prd):
        failures.append("prd: incomplete external rule governance unexpectedly passed")
    vague_metric_prd = SELF_TESTS["prd"][0].replace(
        "目标：缩短审核处理时间；非目标：不改结算规则。成功指标：当前审核中位处理时长基线为 24 小时，上线 30 天内目标降至 8 小时，观察窗口为上线后连续 30 天，Owner 为运营负责人。",
        "目标：提升审核效率；非目标：不改结算规则；成功指标为处理效率可观察。",
        1,
    )
    if "success_metric_incomplete" not in missing_groups("prd", vague_metric_prd):
        failures.append("prd: vague success metric unexpectedly passed")
    defined_timely_rule_prd = SELF_TESTS["prd"][0].replace(
        "当：申请处于待审状态且材料完整。",
        "当：申请需要及时裁决，及时：30 分钟内。",
        1,
    )
    if "ambiguous_rule_language" in missing_groups("prd", defined_timely_rule_prd):
        failures.append("prd: quantified business term unexpectedly failed")
    reasonable_inference_prd = SELF_TESTS["prd"][0].replace(
        "来源与可靠性：运营审核规则，已确认。",
        "来源与可靠性：运营审核规则，合理推断，待 Owner 确认。",
        1,
    )
    if "ambiguous_requirement_language" in missing_groups("prd", reasonable_inference_prd):
        failures.append("prd: reasonable inference label unexpectedly failed")
    split_requirement_prd = re.sub(
        r"(?ms)^### 产品需求陈述.*?(?=^## 六、关键流程)",
        """### 产品需求陈述

需求名称：需求 A。
需求类型：功能。
责任主体：审核平台。
场景 / 前置状态：SCN-001，申请处于待审状态。

需求名称：需求 B。
规范强度：必须。
要求的行为或业务结果：平台保存结论。
度量、时限或边界：重复裁决不改变终态。
来源与可靠性：运营规则，已确认。
验收样例：重复提交返回原终态。

""",
        SELF_TESTS["prd"][0],
    )
    if "requirement_contract_incomplete" not in missing_groups("prd", split_requirement_prd):
        failures.append("prd: incomplete requirement records unexpectedly completed each other")
    multiple_requirement_tables_prd = re.sub(
        r"(?ms)^### 产品需求陈述.*?(?=^## 六、关键流程)",
        """### 产品需求陈述

| 需求名称 | 需求类型 | 责任主体 | 场景 / 前置状态 | 规范强度 | 要求的行为或业务结果 | 度量、时限或边界 | 来源与可靠性 | 验收样例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 保存结论 | 功能 | 审核平台 | SCN-001 / 待审 | 必须 | 保存唯一结论 | 重复裁决不改变终态 | 运营规则，已确认 | 重复提交返回原终态 |

第二个场景：

| 需求名称 | 需求类型 | 责任主体 | 场景 / 前置状态 | 规范强度 | 要求的行为或业务结果 | 度量、时限或边界 | 验收样例 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 发送通知 | 功能 | 审核平台 | SCN-001 / 已裁决 | 应 | 通知审核员 | 裁决后发送 | 通知结果可查询 |

""",
        SELF_TESTS["prd"][0],
    )
    if "requirement_contract_incomplete" not in missing_groups("prd", multiple_requirement_tables_prd):
        failures.append("prd: incomplete later requirement table unexpectedly passed")
    mixed_requirement_prd = re.sub(
        r"(?ms)^### 产品需求陈述.*?(?=^## 六、关键流程)",
        """### 产品需求陈述

需求名称：未完成的叙述需求。
需求类型：功能。

| 需求名称 | 需求类型 | 责任主体 | 场景 / 前置状态 | 规范强度 | 要求的行为或业务结果 | 度量、时限或边界 | 来源与可靠性 | 验收样例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 保存结论 | 功能 | 审核平台 | SCN-001 / 待审 | 必须 | 保存唯一结论 | 重复裁决不改变终态 | 运营规则，已确认 | 重复提交返回原终态 |

""",
        SELF_TESTS["prd"][0],
    )
    if "requirement_contract_incomplete" not in missing_groups("prd", mixed_requirement_prd):
        failures.append("prd: complete table unexpectedly hid incomplete narrative requirement")
    split_rule_prd = re.sub(
        r"(?ms)^## 七、业务规则与接口抽象.*?(?=^## 八、数据与风险)",
        """## 七、业务规则与接口抽象

规则名称：规则 A。
规则性质：场景裁决规则。
适用场景 / 步骤：SCN-001 / 审核裁决。
当：申请处于待审状态。

规则名称：规则 B。
则：记录通过或驳回结论。
Owner：运营负责人。
正例 / 边界例 / 反例：待审可裁决；终态保持；非待审禁止。

产品接口抽象说明业务契约、输入、输出、失败语义和责任边界。

""",
        SELF_TESTS["prd"][0],
    )
    if "rule_contract_incomplete" not in missing_groups("prd", split_rule_prd):
        failures.append("prd: incomplete rule records unexpectedly completed each other")
    multiple_rule_tables_prd = re.sub(
        r"(?ms)^## 七、业务规则与接口抽象.*?(?=^## 八、数据与风险)",
        """## 七、业务规则与接口抽象

| 规则名称 | 规则性质 | 业务动机 | 适用场景 / 步骤 | 输入事实 | 当 | 则 | Owner | 正例 / 边界例 / 反例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 审核裁决 | 场景裁决规则 | 防止终态被覆盖 | SCN-001 / 审核裁决 | 申请状态 | 申请待审 | 记录结论 | 运营负责人 | 待审可裁决；终态保持；非待审禁止 |

第二个场景：

| 规则名称 | 规则性质 | 业务动机 | 适用场景 / 步骤 | 输入事实 | 当 | 则 | 正例 / 边界例 / 反例 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 审核通知 | 场景裁决规则 | 告知裁决结果 | SCN-001 / 通知 | 审核结论 | 已形成结论 | 发送通知 | 已裁决发送；重复发送保持；无结论禁止 |

产品接口抽象说明业务契约、输入、输出、失败语义和责任边界。

""",
        SELF_TESTS["prd"][0],
    )
    if "rule_contract_incomplete" not in missing_groups("prd", multiple_rule_tables_prd):
        failures.append("prd: incomplete later rule table unexpectedly passed")
    mixed_rule_prd = re.sub(
        r"(?ms)^## 七、业务规则与接口抽象.*?(?=^## 八、数据与风险)",
        """## 七、业务规则与接口抽象

规则名称：未完成的叙述规则。
规则性质：场景裁决规则。

| 规则名称 | 规则性质 | 业务动机 | 适用场景 / 步骤 | 输入事实 | 当 | 则 | Owner | 正例 / 边界例 / 反例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 审核裁决 | 场景裁决规则 | 防止终态被覆盖 | SCN-001 / 审核裁决 | 申请状态 | 申请待审 | 记录结论 | 运营负责人 | 待审可裁决；终态保持；非待审禁止 |

产品接口抽象说明业务契约、输入、输出、失败语义和责任边界。

""",
        SELF_TESTS["prd"][0],
    )
    if "rule_contract_incomplete" not in missing_groups("prd", mixed_rule_prd):
        failures.append("prd: complete table unexpectedly hid incomplete narrative rule")
    numbered_table_and_unnumbered_rule_prd = re.sub(
        r"(?ms)^## 七、业务规则与接口抽象.*?(?=^## 八、数据与风险)",
        """## 七、业务规则与接口抽象

| 规则编号 | 规则名称 | 规则性质 | 业务动机 | 适用对象与范围 | 输入事实 | 当 | 则 | Owner | 正例 / 边界例 / 反例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | 审核裁决 | 场景裁决规则 | 防止终态被覆盖 | SCN-001 / 待审申请 | 申请状态 | 申请待审 | 记录结论 | 运营负责人 | 待审可裁决；终态保持；非待审禁止 |

规则名称：未完成的无编号规则。
规则性质：场景裁决规则。

产品接口抽象说明业务契约、输入、输出、失败语义和责任边界。

""",
        SELF_TESTS["prd"][0],
    )
    if "rule_contract_incomplete" not in missing_groups("prd", numbered_table_and_unnumbered_rule_prd):
        failures.append("prd: numbered table unexpectedly hid an incomplete unnumbered rule")
    state_metric_prd = SELF_TESTS["prd"][0].replace(
        "目标：缩短审核处理时间；非目标：不改结算规则。成功指标：当前审核中位处理时长基线为 24 小时，上线 30 天内目标降至 8 小时，观察窗口为上线后连续 30 天，Owner 为运营负责人。",
        "目标：保证审核结论可追溯；非目标：不优化处理时长。成功指标：基线为部分通过结论无审计记录；目标状态为所有通过结论均有审计记录；观察窗口为上线首个发布周期；Owner 为运营负责人。",
        1,
    )
    if "success_metric_incomplete" in missing_groups("prd", state_metric_prd):
        failures.append("prd: state-based success metric unexpectedly failed")
    non_goal_target_prd = SELF_TESTS["prd"][0].replace(
        "目标：缩短审核处理时间；非目标：不改结算规则。成功指标：当前审核中位处理时长基线为 24 小时，上线 30 天内目标降至 8 小时，观察窗口为上线后连续 30 天，Owner 为运营负责人。",
        "目标：保证审核结论可追溯；非目标为不改结算规则。成功指标：当前基线为 12%；观察窗口为上线 30 天内；Owner 为运营负责人。",
        1,
    )
    if "success_metric_incomplete" not in missing_groups("prd", non_goal_target_prd):
        failures.append("prd: non-goal text unexpectedly satisfied success target")
    goal_leak_metric_prd = SELF_TESTS["prd"][0].replace(
        "目标：缩短审核处理时间；非目标：不改结算规则。成功指标：当前审核中位处理时长基线为 24 小时，上线 30 天内目标降至 8 小时，观察窗口为上线后连续 30 天，Owner 为运营负责人。",
        "目标为缩短审核处理时间；非目标：不改结算规则。成功指标：当前基线为 24 小时；观察窗口为上线后连续 30 天；Owner 为运营负责人。",
        1,
    )
    if "success_metric_incomplete" not in missing_groups("prd", goal_leak_metric_prd):
        failures.append("prd: section goal unexpectedly satisfied the success metric target")
    empty_metric_fields_prd = SELF_TESTS["prd"][0].replace(
        "目标：缩短审核处理时间；非目标：不改结算规则。成功指标：当前审核中位处理时长基线为 24 小时，上线 30 天内目标降至 8 小时，观察窗口为上线后连续 30 天，Owner 为运营负责人。",
        "目标：缩短审核处理时间；非目标：不改结算规则。成功指标：基线：；目标值：；观察窗口：；Owner：。",
        1,
    )
    if "success_metric_incomplete" not in missing_groups("prd", empty_metric_fields_prd):
        failures.append("prd: empty success metric fields unexpectedly passed")
    scoped_ambiguous_rule_prd = SELF_TESTS["prd"][0].replace(
        "规则编号：R-001。规则名称：待审申请裁决。规则性质：场景裁决规则。业务动机：防止终态被重复操作覆盖。适用场景 / 步骤：SCN-001 / 审核裁决。适用对象与范围：待审申请。输入事实：申请状态和材料完整性。当：申请处于待审状态且材料完整。则：记录通过或驳回结论。Owner：运营负责人。正例 / 边界例 / 反例：待审申请可裁决；终态重复提交保持原结果；非待审申请不得生成新结论。",
        "规则编号：R-001。规则名称：高优先级裁决。规则性质：场景裁决规则。业务动机：缩短高优先级申请等待。适用场景 / 步骤：SCN-001 / 审核裁决。适用对象与范围：高优先级待审申请。输入事实：申请状态和优先级。当：申请需要及时裁决，及时：30 分钟内。则：记录通过或驳回结论。Owner：运营负责人。正例 / 边界例 / 反例：高优先级待审可裁决；终态保持；非待审禁止。\n"
        "规则编号：R-002。规则名称：普通申请裁决。规则性质：场景裁决规则。业务动机：形成普通申请结论。适用场景 / 步骤：SCN-001 / 审核裁决。适用对象与范围：普通待审申请。输入事实：申请状态和优先级。当：申请需要及时裁决。则：记录通过或驳回结论。Owner：运营负责人。正例 / 边界例 / 反例：普通待审可裁决；终态保持；非待审禁止。",
        1,
    )
    if "ambiguous_rule_language" not in missing_groups("prd", scoped_ambiguous_rule_prd):
        failures.append("prd: one rule definition unexpectedly covered another rule")
    precise_deadline_rule_prd = SELF_TESTS["prd"][0].replace(
        "当：申请处于待审状态且材料完整。",
        "当：申请需要及时裁决，及时：当日营业结束前。",
        1,
    )
    if "ambiguous_rule_language" in missing_groups("prd", precise_deadline_rule_prd):
        failures.append("prd: precise nonnumeric deadline unexpectedly failed")
    named_scenario_prd = (
        SELF_TESTS["prd"][0]
        .replace("### SCN-001 运营审核申请", "### 业务场景：运营审核申请", 1)
        .replace("SCN-001 / 审核裁决", "运营审核申请 / 审核裁决", 1)
        .replace("对应场景：SCN-001", "对应场景：运营审核申请", 1)
    )
    if missing_groups("prd", named_scenario_prd):
        failures.append("prd: named scenario without an id unexpectedly failed")
    simplified_scenario_prd = re.sub(
        r"(?ms)^### SCN-001 运营审核申请\n.*?(?=^### 产品需求陈述)",
        """### SCN-001 运营审核申请
场景说明：审核员在申请已提交且处于待审状态时完成判断，使申请形成可追踪结论。
参与者：审核员处理，平台持有申请事实，运营承接异常。
流程：审核员核对材料并裁决，申请由待审变为通过或驳回，产品反馈结果。
业务结果：审核结论、操作者和时间可查询，重复处理不改变终态。
异常处理：材料不足时要求补充，外部来源不可用时停止裁决并转人工。
规则与验收：引用 R-001；正常裁决可追踪，终态不得被重复覆盖。
""",
        SELF_TESTS["prd"][0],
        count=1,
    )
    if "scenario_contract_incomplete" in missing_groups("prd", simplified_scenario_prd):
        failures.append("prd: simplified readable scenario contract unexpectedly failed")
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
    unbound_rule_prd = re.sub(
        r"(?ms)^## 七、业务规则与接口抽象.*?(?=^## 八、数据与风险)",
        """## 七、业务规则与接口抽象

规则编号：R-001。规则名称：待审申请裁决。规则性质：场景裁决规则。
当：申请处于待审状态。则：记录通过或驳回结论。Owner：运营负责人。
正例 / 边界例 / 反例：待审可裁决；终态保持；非待审禁止。
产品接口抽象说明业务契约、输入、输出、失败语义和责任边界。

""",
        SELF_TESTS["prd"][0],
    )
    if "rule_scope_missing" not in missing_groups("prd", unbound_rule_prd):
        failures.append("prd: rule scope outside the rule section unexpectedly passed")
    matrix_rule_prd = re.sub(
        r"(?ms)^## 七、业务规则与接口抽象.*?(?=^## 八、数据与风险)",
        """## 七、业务规则与接口抽象

| 规则编号 | 规则名称 | 规则性质 | 业务动机 | 适用场景 / 步骤 | 适用对象与范围 | 输入事实 | 当 | 则 | Owner | 正例 / 边界例 / 反例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | 审核裁决 | 场景裁决规则 | 防止终态被覆盖 | SCN-001 / 审核裁决 | 待审申请 | 申请状态 | 申请待审 | 记录结论 | 运营负责人 | 待审可裁决；终态保持；非待审禁止 |

产品接口名称：审核申请裁决。接口使用方：审核员。接口输入与前置条件：待审申请、材料和权限。接口业务输出与副作用：形成结论、变更状态并记录审计。接口失败语义：非待审返回原结论。接口责任边界：平台保存事实，运营处理异常。

""",
        SELF_TESTS["prd"][0],
    )
    if missing_groups("prd", matrix_rule_prd):
        failures.append("prd: rule matrix with scenario scope unexpectedly failed")
    external_matrix_rule_prd = re.sub(
        r"(?ms)^## 七、业务规则与接口抽象.*?(?=^## 八、数据与风险)",
        """## 七、业务规则与接口抽象

| 规则编号 | 规则名称 | 规则性质 | 业务动机 | 适用场景 / 步骤 | 适用对象与范围 | 输入事实 | 当 | 则 | Owner | 正例 / 边界例 / 反例 | 来源 | 版本 | 生效期 | 未确认前处理 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-EXT-001 | 外部资质审核 | 版本化 / 外部规则 | 使用有效政策裁决 | SCN-001 / 审核裁决 | 待审申请 | 申请材料和规则状态 | 规则有效且材料完整 | 记录结论 | 业务负责人 | 有效时通过；失效时待确认；缺材料驳回 | 外部政策 | 2026.1 | 2026-08-01 起 | 保持待专业确认 |

产品接口名称：资质申请裁决。接口使用方：审核员。接口输入与前置条件：待审申请、材料、权限和规则版本。接口业务输出与副作用：形成结论、记录版本并变更状态。接口失败语义：规则不明时待专业确认。接口责任边界：平台保存事实，业务负责人确认规则。

""",
        SELF_TESTS["prd"][0],
    )
    if missing_groups("prd", external_matrix_rule_prd):
        failures.append("prd: complete external rule matrix unexpectedly failed")
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
            "产品定义 / 产品架构主脊：为运营提供可追踪的审核能力；",
            "",
            1,
        ).replace(
            "产品架构主脊：缩短审核时长 -> SCN-001 -> 审核裁决能力 -> 申请状态 -> R-001 -> 可查询结论。\n",
            "",
            1,
        ) + "\n产品视图：审核能力。"
        if "product_view_late" not in warning_checker("prd", late_product_view_prd):
            failures.append("prd: late product view warning missing")
        product_view_before_detail_prd = SELF_TESTS["prd"][0].replace(
            "产品定义 / 产品架构主脊：为运营提供可追踪的审核能力；",
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
