#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate high-value skill trigger and reference routing invariants.

This is a small regression guard for the repo's most important skill routes.
It is not a natural-language router or a complete prompt evaluation suite.
Keep checks focused on durable invariants that should survive wording changes.
"""

import json
from typing import NamedTuple
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
agents_rules = "AGENTS.md"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


checks: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    checks.append((name, bool(condition)))


class RouteFixture(NamedTuple):
    name: str
    prompt: str
    routes: set[str]


class ExpectedHandlingFixture(NamedTuple):
    case_id: str
    required_terms: tuple[str, ...]


def contains_any(text: str, needles: list[str]) -> bool:
    folded_text = text.casefold()
    return any(needle.casefold() in folded_text for needle in needles)


def contains(path: str, text: str) -> bool:
    return text in read(path)


def has_all(path: str, texts: list[str]) -> bool:
    body = read(path)
    return all(text in body for text in texts)


def has_none(path: str, texts: list[str]) -> bool:
    body = read(path)
    return all(text not in body for text in texts)


def frontmatter(path: str) -> str:
    text = read(path)
    if not text.startswith("---\n"):
        return ""
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return ""
    return parts[1]


def has_reference_header(path: str) -> bool:
    return has_all(
        path,
        [
            "## 使用时机",
            "## 不适用场景",
            "## 读取后必须产出",
            "## 需要继续读取的 reference",
        ],
    )


def has_task_reading_index(path: str) -> bool:
    body = read(path)
    return "## 按任务读取索引" in body and (
        "| 任务 | 优先读取 | 跳过 |" in body
        or "| 任务 | 主文档保留 | 按需展开 |" in body
    )


def expected_subset(name: str, actual: set[str], expected: set[str]) -> None:
    missing = expected - actual
    detail = f" missing={sorted(missing)}" if missing else ""
    check(f"scenario fixture routes {name}{detail}", not missing)


def expected_absent(name: str, actual: set[str], unexpected: set[str]) -> None:
    present = unexpected & actual
    detail = f" present={sorted(present)}" if present else ""
    check(f"scenario fixture avoids {name}{detail}", not present)


def expected_handling_has(case_id: str, required_terms: tuple[str, ...]) -> None:
    cases = json.loads(read(skill_eval_prompt_fixture))["cases"]
    case = next((item for item in cases if item.get("id") == case_id), None)
    handling = "" if case is None else case.get("expected_handling", "")
    missing = [term for term in required_terms if term not in handling]
    detail = f" missing={missing}" if missing else ""
    check(f"prompt fixture expected handling outlines {case_id}{detail}", case is not None and not missing)


senior_skill = "senior-software-architect/SKILL.md"
senior_agent = "senior-software-architect/agents/openai.yaml"
senior_routing = "senior-software-architect/references/scenario-routing.md"
senior_diagram = "senior-software-architect/references/diagram-output.md"
workflow = "senior-software-architect/references/workflow.md"
ai_engineering = "senior-software-architect/references/ai-assisted-engineering.md"
production_readiness = "senior-software-architect/references/production-readiness.md"
ai_large_project = "senior-software-architect/references/ai-large-project-orchestration.md"
cad_mode = "senior-software-architect/references/cad-mode.md"
negative_constraints = "senior-software-architect/references/negative-constraints.md"
architecture = "senior-software-architect/references/architecture.md"
testing = "senior-software-architect/references/testing.md"
coding = "senior-software-architect/references/coding-standards.md"
knowledge_graph = "senior-software-architect/references/knowledge-graph.md"
review = "senior-software-architect/references/coding-review-deep-dive.md"
debugging = "senior-software-architect/references/debugging-diagnosis.md"
adr_tradeoff = "senior-software-architect/references/adr-and-tradeoff.md"
language_agnostic = "senior-software-architect/references/language-agnostic-architecture.md"
security = "senior-software-architect/references/security-architecture.md"
system_analysis_template = "senior-software-architect/references/system-analysis-template.md"
senior_source_map = "senior-software-architect/references/source-map.md"
architecture_deliverable_checker = "senior-software-architect/scripts/check_architecture_deliverable.py"
harness_plan_checker = "senior-software-architect/scripts/check_harness_plan.py"
architecture_fixture_verifier = "senior-software-architect/scripts/verify_fixtures.py"
reference_index_audit = "scripts/audit-reference-indexes.py"
source_archive = "scripts/archive-source-evidence.py"
source_map_audit = "scripts/audit-source-map.py"
skill_quality_audit = "scripts/audit-skill-quality.py"
skill_evaluator = "scripts/evaluate-skills.py"
skill_eval_methodology = "references/skill-evaluation-methodology.md"
skill_eval_fixture_audit = "scripts/audit-skill-eval-fixtures.py"
skill_eval_prompt_fixture = "fixtures/skill-eval/prompt-cases.json"
skillx_export_spec = "references/skillx-to-codex-skill-package.md"
skillx_export_adapter = "scripts/skillx_export_adapter.py"
skillx_export_fixture = "fixtures/skillx/sample-candidate.json"
skillx_export_schema = "schemas/skillx-candidate.schema.json"
codegen_generator = "java-service-code-generator/scripts/generate_scaffold.py"
codegen_fixture_verifier = "java-service-code-generator/scripts/verify_fixtures.py"
codegen_rules = "java-service-code-generator/references/code-generation-rules.md"
codegen_nobe_patterns = "java-service-code-generator/references/nobe-patterns.md"
project_governance_refs = [
    "senior-software-architect/references/project-governance-codebase-and-modules.md",
    "senior-software-architect/references/project-governance-service-api-modeling.md",
    "senior-software-architect/references/project-governance-data-security-quality.md",
    "senior-software-architect/references/project-governance-delivery-and-platform.md",
]
testing_practice_refs = [
    "senior-software-architect/references/testing-practices-java-spring-common.md",
    "senior-software-architect/references/testing-practices-java-unit-db.md",
    "senior-software-architect/references/testing-practices-java-web.md",
    "senior-software-architect/references/testing-practices-java-service-flow.md",
    "senior-software-architect/references/testing-practices-business-funds.md",
    "senior-software-architect/references/testing-practices-non-java-and-selection.md",
]
skill_tree_refs = [
    "senior-software-architect/references/skill-tree-architecture-design.md",
    "senior-software-architect/references/skill-tree-engineering-quality.md",
    "senior-software-architect/references/skill-tree-platform-leadership-ai.md",
]

product_skill = "product-architecture-expert/SKILL.md"
product_agent = "product-architecture-expert/agents/openai.yaml"
product_routing = "product-architecture-expert/references/product-scenario-routing.md"
product_architecture = "product-architecture-expert/references/product-architecture-methodology.md"
product_concept_lifecycle = "product-architecture-expert/references/product-concept-lifecycle.md"
product_insight = "product-architecture-expert/references/product-insight-analyst.md"
po_backlog_manager = "product-architecture-expert/references/po-backlog-manager.md"
product_deliberation = "product-architecture-expert/references/product-deliberation-workflow.md"
product_ai_native_context = "product-architecture-expert/references/ai-native-product-context.md"
product_diagram = "product-architecture-expert/references/diagram-output.md"
product_prd = "product-architecture-expert/references/product-design-and-prd.md"
product_prd_template = "product-architecture-expert/references/product-prd-template.md"
product_prd_quality_gates = "product-architecture-expert/references/product-prd-quality-gates.md"
product_prd_financial_appendix = "product-architecture-expert/references/product-prd-financial-appendix.md"
product_prd_operations_and_data = "product-architecture-expert/references/product-prd-operations-and-data.md"
regulatory = "product-architecture-expert/references/regulatory-baseline.md"
payment_methodology = "product-architecture-expert/references/payment-methodology.md"
clearing_settlement = "product-architecture-expert/references/clearing-settlement.md"
global_payment = "product-architecture-expert/references/global-payment-emerging.md"
card_network = "product-architecture-expert/references/card-network-and-card-rails.md"
payment_risk = "product-architecture-expert/references/payment-risk-fraud-and-merchant-operations.md"
dispute_refund = "product-architecture-expert/references/dispute-refund-and-chargeback-operations.md"
payment_routing = "product-architecture-expert/references/payment-scenario-routing.md"
payment_checklists = "product-architecture-expert/references/payment-design-checklists.md"
product_skill_tree = "product-architecture-expert/references/skill-tree.md"
product_source_map = "product-architecture-expert/references/source-map.md"
product_rule_checker = "product-architecture-expert/scripts/check_external_rules.py"
product_deliverable_checker = "product-architecture-expert/scripts/check_product_deliverable.py"

codegen_skill = "java-service-code-generator/SKILL.md"
ai_native_workflow_skill = "ai-native-engineering-workflow/SKILL.md"
ai_native_workflow_agent = "ai-native-engineering-workflow/agents/openai.yaml"
ai_native_intent_to_production = "ai-native-engineering-workflow/references/intent-to-production-loop.md"
ai_native_product_to_engineering = "ai-native-engineering-workflow/references/product-to-engineering-lifecycle.md"
ai_native_prd_system_design_review = "ai-native-engineering-workflow/references/prd-system-design-review.md"
ai_native_agentic_governance = "ai-native-engineering-workflow/references/agentic-engineering-governance.md"
ai_native_gsd_cad_admission = "ai-native-engineering-workflow/references/gsd-cad-admission.md"
ai_native_code_understanding_tools = "ai-native-engineering-workflow/references/code-understanding-tools.md"
ai_native_spec_template_practices = "ai-native-engineering-workflow/references/spec-template-practices.md"
ai_native_code_delivery_closed_loop = "ai-native-engineering-workflow/references/code-delivery-closed-loop.md"
ai_native_goal_composition = "ai-native-engineering-workflow/references/goal-composition.md"
ai_native_agent_loop_engineering = "ai-native-engineering-workflow/references/agent-loop-engineering.md"
ai_native_wisdom_loop_lens = "ai-native-engineering-workflow/references/wisdom-loop-lens.md"
ai_native_verification_release = "ai-native-engineering-workflow/references/verification-review-release.md"
ai_native_superpowers_library = "ai-native-engineering-workflow/references/superpowers-skill-library.md"
ai_native_skill_type_owner_routing = "ai-native-engineering-workflow/references/skill-type-owner-routing.md"
ai_native_source_map = "ai-native-engineering-workflow/references/source-map.md"
codegen_route = {"codegen", "code-generation-rules.md", "nobe-patterns.md", "generate_scaffold.py"}
codegen_safety_route = codegen_route | {"requires-confirmation"}
codegen_source_terms = ["CREATE TABLE", "DDL", "SQL", "建表语句", "schema", "字段表格", "字段说明", "Java 类", "表结构"]
codegen_action_terms = ["生成", "转换", "转成", "脚手架", "配套代码", "代码生成"]
codegen_target_terms = ["Wind/Nobe", "Service", "Mapper", "DTO", "Request", "Query", "Converter", "Entity", "代码"]
codegen_safety_terms = ["覆盖", "overwrite", "已有文件", "模块对不唯一", "多个 face/impl", "多个模块", "基础包名不唯一"]
ai_native_terms = [
    "AI Native Engineering Loop",
    "AI Native 研发流程",
    "AI 流程",
    "AI 工作流",
    "AI 工作量",
    "AI 时代产品到研发编码流程",
    "角色协作 Loop",
    "设计评审",
    "编码评审",
    "可用性安全性评估",
    "可用性 / 安全性 / 可靠性评估",
    "意图到生产交付",
    "Intent-to-Production",
    "产研协同研发流程",
    "Agentic Engineering",
    "PRD-Lite",
    "OpenSpec",
    "Superpowers",
    "Harness",
    "GSD",
    "GSD + Goal",
    "Goal",
    "Goal 组合",
    "Goal 卡",
    "目标驱动",
    "持续推进",
    "Agent Loop",
    "Loop Engineering",
    "Agent 闭环工程",
    "生产可用 Loop",
    "生产可用门禁",
    "架构排熵 Loop",
    "架构排熵",
    "腐朽门禁",
    "Architecture Entropy Card",
    "Loop 取舍校准",
    "东方判断层",
    "Wisdom Lens",
    "huaxia-wisdom",
    "东方智慧",
    "阴阳平衡",
    "先为不可胜",
    "庖丁解牛",
    "中庸之道",
    "循名责实",
    "无为而治",
    "每日三省",
    "知行合一",
    "一张一弛",
    "知识表达",
    "意图可执行",
    "Knowledge-to-Execution Card",
    "非标问题",
    "实际项目编码 Loop",
    "Coding Loop Contract",
    "可删除性",
    "承重 bug",
    "承重行为",
    "废弃 API",
    "治理自腐",
    "失败测试",
    "独立 Checker",
    "状态回写",
    "提交切片",
    "三卡交接",
    "Product Context Card",
    "产品上下文交接卡",
    "Engineering Handoff Card",
    "工程执行交接卡",
    "Production Loop Card",
    "生产 Loop 交接卡",
    "/goal",
    "/loop",
    "auto mode",
    "后台 Agent",
    "多 Agent 监督",
    "自我验证",
    "无进展检测",
    "最大轮次",
    "预算上限",
    "目标状态",
    "进入 GSD",
    "CAD",
    "GSD/CAD 编排准入",
    "GSD Round 0",
    "Atomic Task",
    "Execution Grant",
    "AI 原型/eval",
    "需求分析协同门禁",
    "需求分析结论卡",
    "问题核心诊断",
    "问题核心诊断模式",
    "问题核心诊断门禁",
    "抓住问题的核心",
    "需求无止境",
    "概念定名",
    "需求止损",
    "价值 / 意义边界",
    "价值意义摇摆",
    "定向",
    "定性",
    "定位",
    "定量",
    "整体 / 系统 / 科学",
    "病 / 证 / 症",
    "需求基线稳定性",
    "需求 / 设计 / 编码标准门禁",
    "产品 / 系统 DNA 门禁",
    "系统 DNA",
    "产品 DNA",
    "业务不变量",
    "状态流转",
    "演化规则",
    "开发标准门禁",
    "需求标准",
    "设计标准",
    "编码标准",
    "可验证性",
    "可追踪性",
    "衍生需求",
    "根源需求",
    "产品定义",
    "产品边界",
    "稳定点/变化点",
    "稳定点 / 变化点",
    "边界坐标",
    "上下游分工",
    "PRD/系分合议预审",
    "PRD 评审会前",
    "AI 预扫描",
    "完整性/一致性/可测试性/二义性",
    "整理最终 PRD",
    "最终文档准出",
    "正式交付文档",
    "过程资产",
    "过程记录链接",
    "合议预审",
    "MAGI 三角色",
    "A2A 虚拟评审",
    "IPD 式互审",
    "AI 编码流程",
    "AI 代码交付闭环",
    "SDD",
    "规范驱动开发",
    "生产级代码",
    "Spec 驱动开发",
    "Spec/SDD 模板",
    "Spec 模板",
    "模板最佳实践",
    "AC 验收",
    "Given-When-Then",
    "spec-lint",
    "AC 覆盖",
    "漂移检查",
    "Form Follows Reviewer",
    "编码提速",
    "交付闭环",
    "验证矩阵",
    "代码 CR",
    "发布复盘",
    "反馈闭环成熟度",
    "验证簇",
    "不变量验证簇",
    "高风险不变量",
    "测试通过不是事实",
    "覆盖率提升",
    "L2/L3/L4/L5",
    "生产重放",
    "变异测试",
    "对抗测试",
    "自我挖掘",
    "自主交付控制卡",
    "人工确认边界",
    "默认授权",
    "自动推进",
    "按任务计划推进",
    "计划授权",
    "Plan Grant",
    "阶段提交",
    "任务提交",
    "commit_after_verified_task",
    "替我审批",
    "授权策略",
    "Wave Grant",
    "CAD Grant",
    "事实边界检查",
    "事实边界",
    "无根据猜测",
    "模型脑补",
    "范围外不做",
    "超出用户目标",
    "质量门禁",
    "测试门禁",
    "理解门禁",
    "系分设计",
    "代码库理解结论包",
    "代码库级理解",
    "阅读分析代码库",
    "AI 快速阅读代码",
    "Gemini CLI",
    "AgentRC",
    "Superpowers skills",
    "superpowers skills",
    "brainstorming",
    "writing-plans",
    "executing-plans",
    "subagent-driven-development",
    "test-driven-development",
    "requesting-code-review",
    "verification-before-completion",
    "设计-代码对齐",
    "AI-readiness",
    "上下文漂移",
    "变更可理解性",
    "影响可视化",
    "复杂度投资",
    "战术化编码",
    "浅模块",
    "直通包装",
    "图形化理解",
    "架构描述转图",
    "授权学习",
    "经验归位",
    "Skill 类型",
    "Skill 分类经验",
    "Anthropic内部Skills",
    "Anthropic 内部 Skills",
    "产品验证",
    "代码质量",
    "Runbook",
    "CI/CD",
    "模板脚手架",
    "团队自动化",
    "数据分析",
    "基础设施操作",
]
wisdom_lens_terms = [
    "Loop 取舍校准",
    "东方判断层",
    "Wisdom Lens",
    "huaxia-wisdom",
    "东方智慧",
    "阴阳平衡",
    "先为不可胜",
    "庖丁解牛",
    "中庸之道",
    "循名责实",
    "无为而治",
    "每日三省",
    "知行合一",
    "一张一弛",
]
product_terms = ["产品", "产品方案", "PRD", "模板", "原型", "页面截图", "页面说明", "交互稿", "反推 PRD", "反推需求", "验收种子", "交给架构师", "产品洞察", "需求洞察", "根源需求", "产品定义", "产品边界", "产品 DNA", "业务不变量", "功能先行、规则后补", "稳定点/变化点", "稳定点 / 变化点", "边界坐标", "概念定名", "概念生命周期", "概念退役", "新旧概念", "事实源分裂", "只加不减", "旧规则", "旧入口", "需求止损", "需求无止境", "价值 / 意义边界", "价值意义摇摆", "非标产品问题", "非标诉求", "不是传话筒", "解决方案假设", "老板", "销售", "客户", "运营", "目标用户", "UED", "资料资产化", "机会雷达", "竞品动态", "标杆实践", "Backlog", "机会清单", "机会点", "需求优先级", "User Story", "清结算", "对账", "合规", "商户", "SaaS", "B2B", "运营后台", "规则矩阵", "能力地图", "用例图", "业务流程图", "资金流图", "外卡收单", "Mastercard", "商户到账", "产品大师", "MAGI", "多视角", "合议评审", "需求评审", "评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "产品头脑风暴", "问题探索", "假设挑战", "HMW", "OODA", "逆向头脑风暴"]
product_general_route_terms = ["产品方案", "验收种子", "交给架构师", "SaaS", "B2B", "业务流程", "业务流程图", "用例图", "能力地图", "运营后台", "规则矩阵", "原型", "页面截图", "页面说明", "交互稿", "反推 PRD", "反推需求", "根源需求", "产品定义", "产品边界", "产品 DNA", "业务不变量", "功能先行、规则后补", "稳定点/变化点", "稳定点 / 变化点", "边界坐标", "概念定名", "概念生命周期", "概念退役", "新旧概念", "事实源分裂", "只加不减", "旧规则", "旧入口", "需求止损", "需求无止境", "价值 / 意义边界", "价值意义摇摆", "非标产品问题", "非标诉求", "不是传话筒", "解决方案假设", "老板", "销售", "客户", "运营", "目标用户", "UED", "产品经理方法论", "产品经理知识体系", "产品专家基础能力", "基础工作法", "产品洞察", "需求洞察", "资料资产化", "机会雷达", "客户访谈", "竞品动态", "标杆实践", "证据来源", "推理链", "机会清单", "Backlog", "需求优先级", "User Story", "AC", "AI-shaped", "readiness", "AI 工作流", "AI 成熟度", "产品团队 AI", "AI 产品工作成熟度", "AI Native", "Product Builder", "业务 dogfooding", "MVP harden", "放下 PRD", "PRD 可执行上下文", "产品大师", "MAGI", "多视角", "合议评审", "PM/Reviewer", "AI 生成方案", "需求评审", "评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "产品头脑风暴", "问题探索", "方案发散", "假设挑战", "HMW", "第一性原理", "OODA", "逆向头脑风暴"]
payment_terms = [
    "清结算",
    "对账",
    "支付",
    "资金",
    "商户",
    "合规",
    "外卡收单",
    "Mastercard",
    "Clearing Core",
    "Financial Presentment",
    "商户到账",
    "merchant payout",
    "收单风控",
    "Airwallex",
    "Global Accounts",
    "Connected Accounts",
    "Payouts",
    "Issuing",
    "Global Treasury",
    "BaaS",
    "Payments for Platforms",
    "全球金融平台",
    "嵌入式金融",
    "白标金融",
    "平台责任边界",
    "Transactional FX",
    "换汇",
    "汇率",
    "多币种",
    "费用舍入",
    "全球金融平台交付包",
    "WorldFirst",
    "万里汇",
    "AI 出海",
    "全球资金管理",
    "Agent 支付",
    "Token 计费",
    "token 计费",
    "用量计费",
    "VCC",
]
external_dependency_terms = ["SDK", "API", "云产品", "版本", "升级"]
diagram_terms = ["画图", "图形化", "可视化", "架构图", "用例图", "流程图", "时序图", "状态机", "ER 图", "类图", "部署图", "迁移图", "关系图", "资金流图"]

reference_headers = [
    senior_routing,
    senior_diagram,
    workflow,
    ai_engineering,
    production_readiness,
    ai_large_project,
    testing,
    coding,
    knowledge_graph,
    debugging,
    product_routing,
    po_backlog_manager,
    product_insight,
    payment_routing,
    product_diagram,
    product_prd,
    product_prd_template,
    product_prd_quality_gates,
    product_prd_financial_appendix,
    product_prd_operations_and_data,
    regulatory,
    codegen_rules,
    codegen_nobe_patterns,
    ai_native_product_to_engineering,
    ai_native_intent_to_production,
    ai_native_prd_system_design_review,
    ai_native_agentic_governance,
    ai_native_gsd_cad_admission,
    ai_native_code_understanding_tools,
    ai_native_spec_template_practices,
    ai_native_code_delivery_closed_loop,
    ai_native_goal_composition,
    ai_native_agent_loop_engineering,
    ai_native_wisdom_loop_lens,
    ai_native_verification_release,
    ai_native_superpowers_library,
    ai_native_skill_type_owner_routing,
    ai_native_source_map,
] + project_governance_refs + testing_practice_refs + skill_tree_refs

for path in reference_headers:
    check(f"{path} has progressive-disclosure header", has_reference_header(path))

check(
    "repo agents constrain final deliverable documents",
    has_all(
        agents_rules,
        [
            "正式 PRD、系分、OpenSpec/SDD 等交付文档以最终标准版本为主",
            "不保留讨论过程、迭代草稿、AI 推理轨迹或被拒方案展开",
            "过程内容进入任务计划、评审报告、Decision Log、Goal Ledger、ADR 或中间任务文档",
        ],
    ),
)
check(
    "repo agents define top-level conduct principles",
    has_all(
        agents_rules,
        [
            "## 顶层处事原则",
            "先读事实，后生判断",
            "先抓核心，后开药方",
            "先定名，后扩需求",
            "先定向、定性、定位，再定量",
            "先整体，后局部",
            "以体统用，以用证体",
            "以真实交付为准",
            "事实、推断、待确认分层表达",
            "最终文档只放最终结论",
            "授权按风险分级，执行按证据闭环",
        ],
    ),
)

check(
    "ai-native workflow skill anchors product architect and senior architect collaboration",
    has_all(
        ai_native_workflow_skill,
        [
            "AI Native Engineering Loop 的角色协作与准入门禁",
            "默认进入角色协作 Loop",
            "角色协作 Loop 统一外显，能力内部化",
            "阶段名不是能力来源",
            "本技能不得绕开专项 Skill 自由发挥",
            "角色 Loop 场景视图：只读理解 / 产研交付 / 验证发布 / 知识回流（不是并列入口）",
            "Loop Contract：Goal / State / Plan / Action / Observe / Decide / Verify / Stop-Handoff",
            "内部层：Goal / GSD-Wave / CAD-Atomic / Harness / Grant",
            "能力 / 约规来源：产品架构专家 / 资深架构师 / java-service-code-generator / reference / script",
            "产品 / 交互设计",
            "设计评审",
            "TDD / 测试设计",
            "编码实现",
            "编码评审",
            "可用性 / 安全性 / 可靠性评估",
            "产品语义、业务对象、机会雷达、Backlog、PRD、产品上下文包和 Product Context Card 由 `产品架构专家` 主导",
            "系统设计、OpenSpec、完整 Harness Plan、GSD/CAD 工程执行策略、代码实现、测试、CR、生产风险和 CAD Mode 由 `资深架构师` 主导",
            "本技能负责端到端角色协作 Loop 准入、owner、阶段顺序、角色视角、停止条件、授权策略和交接结论",
            "GSD、CAD、Goal、Harness、Grant、Agent Loop 都是角色协作 Loop 的内部层",
            "产研交付视图",
            "角色协作主流程",
            "目标与大项目编排",
            "评审与规格门禁",
            "质量门禁 / CR 发布模式",
            "人必须能解释目标、当前状态、关键变更、证据链、残余风险和停止理由",
            "实际项目编码 Loop",
            "证据边界：事实 / 推断 / 待确认 / 范围外不做",
            "协同有效性 / 能力归属性",
            "不能只写“产品 / 架构 / TDD / 编码”阶段名",
            "内存版业务 Service",
            "不做无根据的猜测、推导、补全、脑补式需求扩张或超出用户目标的实现",
            "不把 PR 数、执行轮数、自动化次数、Agent 数量或“全程手机审批”当成工程价值",
            "不把 Codex “替我审批”用于 Git、联网、依赖安装、密钥、生产、部署、不可逆操作或高风险业务变更的自动放行",
            "references/product-to-engineering-lifecycle.md",
            "references/agentic-engineering-governance.md",
            "references/agent-loop-engineering.md",
            "references/gsd-cad-admission.md",
            "references/code-understanding-tools.md",
            "references/spec-template-practices.md",
            "references/code-delivery-closed-loop.md",
            "references/goal-composition.md",
            "references/verification-review-release.md",
            "references/superpowers-skill-library.md",
            "references/wisdom-loop-lens.md",
            "references/skill-type-owner-routing.md",
            "references/source-map.md",
        ],
    )
    and has_all(
        ai_native_verification_release,
        [
            "质量 / 测试门禁",
            "测试矩阵",
            "验证顺序",
            "CR 前置条件",
            "失败回退",
            "残余风险交接",
            "能力 / 约规来源",
            "每个门禁必须写明调用哪个专项能力",
            "结构化 Java Service 生成回到 `java-service-code-generator`",
        ],
    )
    and has_all(
        ai_native_code_delivery_closed_loop,
        [
            "AI 代码交付闭环",
            "最小 Spec 强度",
            "Harness 三层闭环",
            "CR 减负",
            "知识回流",
            "一次通过率",
            "返工率",
            "缺陷密度",
            "AI 注释去噪与可读性门禁",
            "注释是否复述显而易见的 What / How",
            "优先进入测试资产",
        ],
    )
    and has_all(
        ai_native_gsd_cad_admission,
        [
            "GSD 的目标是交付生产可用能力",
            "GSD Round 0 缺口",
            "Atomic Task 候选",
            "CAD 候选缺口",
            "授权策略",
            "Execution Grant 缺口",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "需求分析结论卡",
            "根源需求",
            "产品定义",
            "产品边界",
            "需求 / 设计 / 编码标准门禁",
            "需求基线稳定性",
        ],
    ),
)
check(
    "ai-native workflow exposes wisdom lens for Loop judgment",
    has_reference_header(ai_native_wisdom_loop_lens)
    and has_task_reading_index(ai_native_wisdom_loop_lens)
    and has_all(
        ai_native_workflow_skill,
        [
            "Loop 取舍校准 / Wisdom Lens",
            "references/wisdom-loop-lens.md",
            "huaxia-wisdom",
            "阴阳平衡",
            "先为不可胜",
            "庖丁解牛",
            "循名责实",
            "不替代事实、证据、测试、CR、授权或上线审批",
        ],
    )
    and has_all(
        ai_native_wisdom_loop_lens,
        [
            "Wisdom Lens Card",
            "准入前",
            "拆解时",
            "执行中",
            "复盘后",
            "Loop Contract、Grant、Verification 和 Stop/Handoff",
            "不把传统智慧框架当作项目事实、合规结论、架构批准、Execution Grant、测试通过或生产审批",
        ],
    )
    and has_all(
        "README.md",
        [
            "Wisdom Lens",
            "内部路由",
            "Gitee 仓库 [aiami/huaxia-wisdom]",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "Gitee 仓库 `aiami/huaxia-wisdom`",
            "eef49d54e6266b1afc568ef591a6a2d4abd5ad8e",
            "Wisdom Lens",
            "不复制原文、示例、口吻或经典表达",
            "不把传统智慧框架写成事实证据、项目制度、Execution Grant、测试通过、CR 结论、Git 授权或上线审批",
        ],
    ),
)
check(
    "ai-native workflow keeps three-card handoff protocol",
    has_all(
        ai_native_workflow_skill,
        [
            "三卡交接",
            "三卡交接包",
            "Product Context Card",
            "Engineering Handoff Card",
            "Production Loop Card",
            "三卡可消费性",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "3A. 三卡交接协议",
            "Product Context Card / 产品上下文交接卡",
            "Engineering Handoff Card / 工程执行交接卡",
            "Production Loop Card / 生产 Loop 交接卡",
            "三卡都不是 Execution Grant",
            "三卡必须区分事实、推断、待确认和范围外不做",
        ],
    )
    and has_all(
        ai_native_gsd_cad_admission,
        [
            "三卡交接结论",
            "7A. 三卡到架构师的消费规则",
            "Product Context Card",
            "Engineering Handoff Card",
            "Production Loop Card",
            "缺失时回 `产品架构专家`",
            "缺失时停在 AI Native 编排",
            "缺失时只标记 Loop Candidate",
        ],
    )
    and has_all(
        product_skill,
        [
            "产品交接只交事实与验收",
            "Product Context Card / 产品上下文交接卡",
            "不判定 GSD/CAD 准入",
            "不生成 Engineering Handoff Card、Production Loop Card、Plan Grant、Execution Grant 或上线审批",
            "产品合议只评产品内容",
            "不替代 AI Native 的跨角色准入、工程分派、发布门禁",
            "也不判定系分或代码可执行性",
        ],
    )
    and has_all(
        product_ai_native_context,
        [
            "Product Context Card / 产品上下文交接卡",
            "不生成 Engineering Handoff Card、Production Loop Card 或 Execution Grant",
            "产品专家不输出 Engineering Handoff Card、Production Loop Card、Plan Grant、Execution Grant、CAD Grant 或上线批准",
        ],
    )
    and has_all(
        senior_skill,
        [
            "消费交接卡而不重开流程",
            "Product Context Card",
            "Engineering Handoff Card",
            "Production Loop Card",
            "不把交接卡当成 Execution Grant、测试通过、Git 授权或上线审批",
            "声明角色视角再行动",
            "设计者、设计评审者、TDD / 测试设计者、编码实现者、编码评审者、可用性 / 安全性 / 可靠性评估者或发布风险评估者",
            "Maker 和 Checker 分离",
        ],
    )
    and has_all(
        ai_engineering,
        [
            "AI Native 交接卡消费结论",
            "1D. AI Native 交接卡消费协议",
            "Product Context Card",
            "Engineering Handoff Card",
            "Production Loop Card",
            "三卡都不是 Plan Grant / Execution Grant、测试通过、CR 结论、生产审批或 Git 授权",
        ],
    )
    and has_all(
        ai_native_skill_type_owner_routing,
        [
            "三卡交接",
            "Product Context Card",
            "Engineering Handoff Card",
            "Production Loop Card",
            "不让任一卡替代 Execution Grant、测试通过或上线审批",
        ],
    )
    and has_all(
        "README.md",
        [
            "三卡交接",
            "Product Context Card",
            "Engineering Handoff Card",
            "Production Loop Card",
            "三卡都不是 Execution Grant、测试通过或上线审批",
        ],
    )
    and has_none(
        ai_native_gsd_cad_admission,
        [
            "Execution Handoff Card",
        ],
    )
    and has_none(
        "fixtures/skill-eval/prompt-cases.json",
        [
            "Execution Handoff Card",
        ],
    ),
)
check(
    "ai-native workflow keeps skill type owner routing boundary",
    has_reference_header(ai_native_skill_type_owner_routing)
    and has_task_reading_index(ai_native_skill_type_owner_routing)
    and has_all(
        ai_native_workflow_skill,
        [
            "Skill 类型路由",
            "references/skill-type-owner-routing.md",
            "Skill 类型 owner 路由包",
        ],
    )
    and has_all(
        ai_native_skill_type_owner_routing,
        [
            "# Skill 类型与 Owner 路由",
            "不新增顶层 Skill",
            "product verification",
            "code quality and review",
            "CI/CD and deployment",
            "runbooks",
            "infrastructure operations",
            "只更新 reference",
            "补 fixture / validator",
            "补脚本",
            "新建顶层 Skill",
            "产品专家被 AI Native 调用",
            "产品验证种子",
            "架构师被 AI Native 调用",
            "Runbook 与生产诊断",
            "CI/CD 与发布门禁",
            "基础设施操作",
            "source-map.md",
        ],
    ),
)
check(
    "ai-native workflow metadata triggers orchestration not implementation",
    all(
        term in frontmatter(ai_native_workflow_skill)
        for term in [
            "AI Native Engineering Loop 的角色协作与准入门禁",
            "跨产品 UED 架构 AI Maker-Checker 到质量发布",
            "GSD/CAD/Goal 等旧说法要求流程编排",
            "可交接可验证可停止",
            "普通 PRD、Bug、测试、源码级 CR 或 Java Service 生成优先路由专门 Skill",
        ]
    )
    and has_all(
        ai_native_workflow_agent,
        [
            "以角色协作 Loop 编排产品专家、UED、架构师、AI Maker/Checker、TDD、CR、质量发布和内部 GSD/CAD/Goal",
            "按当前材料进入角色协作 Loop",
            "当前阶段、角色视角",
            "owner、交接物、Loop Contract、授权策略、验证门禁、停止条件和下一步分派",
        ],
    ),
)
check(
    "ai-native workflow defines stable default output skeleton",
    has_all(
        ai_native_workflow_skill,
        [
            "默认输出骨架",
            "结论：",
            "当前阶段：设计 / 设计评审 / TDD-测试设计 / 编码实现 / 编码评审 / 可用性-安全性-可靠性评估 / 发布复盘",
            "角色视角：主责角色 / 协作角色 / AI Maker / AI Checker / 人工 owner",
            "角色 Loop 场景视图：只读理解 / 产研交付 / 验证发布 / 知识回流（不是并列入口）",
            "Owner / 下一步分派：",
            "交接物：",
            "Loop Contract：Goal / State / Plan / Action / Observe / Decide / Verify / Stop-Handoff",
            "证据边界：事实 / 推断 / 待确认 / 范围外不做",
            "授权策略：只读 / 计划内低风险执行 / Plan Grant / Wave Grant / CAD Grant / 显式确认",
            "验证门禁：",
            "停止条件：",
            "残余风险 / 需要确认：",
            "只有用户要求完整方案、评审报告或模板时",
        ],
    ),
)
check(
    "ai-native workflow references preserve lifecycle governance and source boundaries",
    has_all(
        ai_native_product_to_engineering,
        [
            "机会/反馈/业务意图",
            "问题地图",
            "AI 原型 / eval / dogfooding",
            "产品上下文包",
            "可开发系统秩序链",
            "Round 0A：需求基线稳定性",
            "Round 0C：业务同质性和价值成本门禁",
            "业务 / 产品 / 技术交叉准入",
            "技术复制成本",
            "不能进入 GSD Wave、CAD 候选、Execution Grant 或代码生成",
            "需求条目说明外部可见行为，而不是内部实现方案",
            "P0/P1 需求具备原子性、完整性、一致性、必要性、无二义性、可行性、可验证性和可追踪性",
            "图、流程、原型或表格有正文解释、需求 ID 或验收种子回链",
            "衍生需求、异常恢复、安全监控、状态异常处理和鲁棒性要求",
            "系统/产品需求未确认、需求条目不可验证、图文不可追踪或衍生需求无 owner",
            "模糊需求",
            "结构化需求文档",
            "业务流 / 状态 / 规则",
            "原型或页面说明",
            "开发执行任务",
            "PRD-Lite / OpenSpec 输入",
            "Hardened Candidate",
            "工程交接清单",
            "AI Native 交接结论",
            "AI 代码交付闭环",
            "code-delivery-closed-loop.md",
            "CAD 候选缺口",
            "瘦身边界",
            "最小产品上下文",
            "Round 0 补齐清单",
            "需求分析结论卡",
            "根源需求",
            "产品定义",
            "产品边界",
            "稳定点 / 变化点",
            "边界坐标",
            "是否可以进入 OpenSpec",
            "可评审 Spec 模板",
            "人类能否 Review，Agent 能否执行，机器能否验证",
            "spec-template-practices.md",
            "Spec 强度、五段式骨架、AC 与测试映射、spec-lint、AC 覆盖和漂移检查",
            "不能跳到代码生成、GSD Wave 或 CAD 候选",
            "前后台 / 多端 / 运营能力分工",
        ],
    )
    and has_all(
        ai_native_agentic_governance,
        [
            "OpenSpec 定义做什么，Superpowers 定义怎么高质量地做，Harness 定义谁做、按什么顺序做、能改哪里、怎么验证、怎么交接",
            "Superpowers skills 下载资源、外部 skill 调度矩阵、MIT 许可和安全边界读 `superpowers-skill-library.md`",
            "调度 Superpowers skills",
            "`obra/superpowers` 已作为外部 skill library 下载并隔离到 `external-superpowers/`",
            "brainstorming 用于前置澄清",
            "writing-plans 用于计划拆解",
            "test-driven-development 用于红绿重构纪律",
            "requesting-code-review / receiving-code-review 用于 CR 反馈闭环",
            "verification-before-completion 用于完成前证据门禁",
            "外部 skill 的默认目录、插件安装、hooks、worktree、自动提交、Git 推送",
            "轻量执行",
            "Harness / GSD",
            "CAD 候选",
            "计划内授权 / 自动推进",
            "GSD/CAD 自动推进、计划内授权、减少每个任务审批",
            "授权策略判断",
            "授权策略: 只读 / 计划内低风险执行 / Plan Grant / Wave Grant / CAD Grant / 显式确认",
            "Codex 替我审批: 未启用 / 已启用但仅低风险 / 不适用",
            "GSD/CAD 授权必须按风险分级",
            "Codex “替我审批”只能记录为当前会话已启用的低风险审批通道",
            "权限边界",
            "Wave 0",
            "gsd-cad-admission.md",
            "可执行性判断",
            "最小 Harness 摘要",
            "事实边界判断",
            "事实 / 推断 / 待确认 / 范围外不做:",
            "不能把无根据猜测、外部文章观点、工具总结或模型脑补写成任务、实现或授权",
            "是否有事实边界门禁",
            "是否有授权策略",
            "能否自动推进",
            "是否有根据",
            "变更可理解性要求",
            "代码库理解结论包",
            "独立验证证据",
            "知识回流位置",
            "交付指标",
            "业务意图、入口路径、影响模块、关键调用关系、边界变化和源码锚点",
            "能不能做",
            "是否看懂",
            "能改哪里",
            "何时停止",
            "spec-template-practices.md",
            "AC 编号与测试映射",
            "spec-lint / AC 覆盖 / 漂移检查",
            "可评审 Spec 模板",
            "把“自动推进”“默认授权”或 Codex “替我审批”写成无条件放行",
        ],
    )
    and has_all(
        ai_native_gsd_cad_admission,
        [
            "角色协作 Loop 产研交付视图准入结论",
            "是否需要 GSD Round 0",
            "Wave/Atomic Task 候选",
            "Superpowers 方法门禁",
            "CAD 候选缺口",
            "GSD/CAD 授权策略卡",
            "默认授权哪些任务",
            "Codex 的“替我审批”模式",
            "Execution Grant 缺口",
            "下一步 owner",
            "AI Native Engineering Loop 决定“是否进入角色协作 Loop 的产研交付视图、是否启用 GSD/CAD 内部层，以及下一步 owner”",
            "GSD-like 决定“哪些阶段和任务可以被执行”",
            "CAD Mode 决定“当前选中的原子任务是否可以自动执行”",
            "Execution Grant 决定“本轮实际允许做什么”",
            "授权策略不是让每个任务都重新问一次，也不是让所有动作无条件通过",
            "把授权前移到 Goal 任务计划、Wave 或 CAD Grant 层",
            "Skill 自行开启",
            "Superpowers 在 GSD 中只作为方法纪律层",
            "GSD 可以默认支持 Superpowers 方法门禁",
            "不能默认安装 Superpowers 插件、运行外部脚本、创建 worktree、启动 subagent 或采用外部 Git 默认动作",
            "AI 产品工程化准入卡",
            "业务 context",
            "真实工作流",
            "用户收益 / 负担",
            "权限与责任",
            "旧系统接入",
            "灰度与止损",
            "成本与稳定性",
            "不把战略风口、发布会、DAU 或 demo 当准入证据",
            "不满足准入卡时，只能输出 Round 0 补齐清单或回到产品专家",
            "GSD 的目标是交付生产可用能力",
            "它服务哪个真实业务目标",
            "落在哪个生产边界或真实入口",
            "产品 / 系统 DNA 是否清楚",
            "产品 / 系统 DNA 锚点",
            "产品 / 系统 DNA 缺口",
            "除了缓存能力、测试替身、fixture、沙盒模拟或明确标注的 demo",
            "业务代码不应提供内存版 Service 实现来冒充生产能力",
            "`InMemoryXxxService`",
            "`FakeXxxService`",
            "`MockXxxService`",
            "Map/List 存储型业务实现",
            "GSD Round 0 缺口",
            "当前授权策略是否清楚",
            "是否需要 Superpowers 方法门禁",
            "需求澄清是否需要 `brainstorming`",
            "任务拆解是否需要 `writing-plans`",
            "实现是否需要 `test-driven-development`",
            "CR 是否需要 `requesting-code-review` / `receiving-code-review`",
            "完成前是否需要 `verification-before-completion`",
            "Atomic Task 候选",
            "生产可用能力锚点",
            "事实/推断/待确认边界",
            "建议授权模式",
            "Superpowers 方法纪律候选",
            "TDD 切入点",
            "最小 Review 输入包",
            "完成前验证命令",
            "是否已有 Superpowers/TDD/Review/Verification 方法门禁",
            "CAD 候选但缺授权策略",
            "CAD Grant 候选",
            "只读侦察",
            "计划内低风险执行",
            "Wave Grant",
            "显式确认",
            "Codex 替我审批通道",
            "Grant 最小字段",
            "默认审批通道",
            "未开启时不得假定开启",
            "Git 默认需要显式确认",
            "只说“继续”“按建议推进”“自动跑起来”",
            "事实边界红线",
            "无根据猜测、模型脑补、工具总结、外部文章观点或超出用户目标的功能扩张",
            "事实依据、推断依据、待确认项和范围外不做",
            "未区分时不能进入 CAD",
            "事实边界:",
            "交给 `senior-software-architect/references/ai-large-project-orchestration.md`",
            "交给 `senior-software-architect/references/cad-mode.md`",
            "不写成执行授权",
            "不是 Execution Grant",
            "不建议进入 CAD",
            "让 AI 随机推进模拟模块、mock 流程、无业务入口 demo、空服务骨架或看上去可用的样子货",
            "只检查页面能打开、接口能返回假数据或测试桩能跑通",
            "把内存版业务 Service、Map/List 存储实现、Fake/Mock 服务或进程内状态当成生产实现",
            "把 Superpowers skills 当成 GSD 的默认插件安装、默认外部脚本、默认 worktree、默认 subagent 或默认 Git 操作",
            "把计划内低风险执行写成无条件自动通过",
            "让 Codex 替我审批绕过工具权限、sandbox、项目规则和用户授权",
            "在 AI Native 中复制 CAD 每轮 Pick / Red / Green / Review / Refactor / Verify / Record 细则",
        ],
    )
    and has_all(
        ai_native_code_understanding_tools,
        [
            "AI 代码理解工具入口",
            "Gemini CLI",
            "AgentRC",
            "Understand Anything",
            "Ponytail",
            "最小正确实现工具",
            "过度设计门禁",
            "安装 / 调用准入",
            "设计-代码对齐",
            "知识图谱",
            "AI-readiness",
            "上下文漂移",
            ".understand-anything/",
            "只读范围",
            "联网需求",
            "认证 / token",
            "工具输出交接格式",
            "环境可用性记录规则",
            "不把某台机器的安装路径、版本、shell 配置或登录状态写成默认可用能力",
            "不把任何工具写成默认依赖",
            "不默认安装、联网、登录、写文件、写配置或改代码",
            "不默认运行远端安装脚本、插件安装命令、lifecycle hook、`/understand`、`/understand --auto-update`、dashboard、本地服务、post-commit hook 或 Git LFS 配置",
            "不默认写入 `.github/copilot-instructions.md`、`.vscode/mcp.json`",
            "不默认写入、提交或同步 `.understand-anything/`、`knowledge-graph.json`、图谱中间产物、dashboard 产物或 hook",
            "不把工具输出当作 Execution Grant、CAD 授权、测试通过、发布批准或合规结论",
            "不把 Ponytail 的“少写”当作删除输入校验、错误处理、安全、可访问性、资金/权限/生产兜底或必要测试的理由",
        ],
    )
    and has_all(
        ai_native_verification_release,
        [
            "验证矩阵",
            "质量 / 测试门禁",
            "代码库理解 / 影响可视化门禁",
            "code-understanding-tools.md",
            "测试策略、TDD、补测试、测试实现和测试代码 CR 回到 `senior-software-architect/references/testing.md`",
            "OpenSpec 规定测什么业务事实",
            "产品专家提供验收种子",
            "资深架构师设计和实现测试",
            "本技能编排质量门禁",
            "测试矩阵",
            "验证顺序",
            "CR 前置条件",
            "失败回退",
            "残余风险交接",
            "业务意图",
            "入口路径",
            "影响模块",
            "关键调用关系",
            "边界变化",
            "源码锚点",
            "事实 / 推断",
            "置信度",
            "owner 复述",
            "AI 快速阅读、上下文生成和可视化可以是依赖图、调用导览、模块边界图、diff 覆盖层、仓库指令文件或源码锚定的结构视图",
            "代码库理解结论包必须区分“源码事实”和“模型推断”",
            "只有当团队反复需要跨项目测试策略治理",
            "Eval 和测试不是同一个东西",
            "AI 代码 Review 优先顺序",
            "发布门禁",
            "观测和回滚",
            "复盘闭环",
            "当前可信度判断",
            "残余风险清单",
            "先给结论",
            "交付完整性要求",
            "code-delivery-closed-loop.md",
            "spec-template-practices.md",
            "Spec 强度",
            "Spec / AC 编号",
            "AC 覆盖",
            "漂移检查",
            "独立验证证据",
            "知识回流",
            "一次通过率",
            "CR 高频问题",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "微信“环境异常”验证页，未读取到正文",
            "不把该链接作为已吸收来源",
            "第 3 篇：一个好的 Loop 到底由什么组成",
            "Seeek X",
            "AI Native Engineering Loop 统一入口和 GSD/CAD/Goal 压缩重构",
            "Loop Contract",
            "四类场景视图",
            "GSD/CAD/Goal 内部层映射",
            "自主交付控制卡",
            "终于有人开始解决 AI Coding 最大的问题了：看不懂代码",
            "变更可理解性、结构上下文、影响可视化",
            "任何外部可视化 CLI、IDE 插件或厂商预览能力写成默认依赖",
            "Google Gemini CLI",
            "Microsoft AgentRC",
            "Egonex-AI Understand Anything",
            "代码库知识图谱",
            "不默认安装、联网、写 `~/.understand-anything`、写/提交 `.understand-anything/`、启动 dashboard、本地服务或 auto-update",
            "Microsoft Clarity Agent",
            "万字长文 | Spec 驱动开发实战：半年踩坑，我们如何让 AI 编码的交付真正闭环",
            "我们落地了 SDD，为什么团队效率没有体感提升？",
            "code-delivery-closed-loop.md",
            "spec-template-practices.md",
            "减层",
            "上下文注入",
            "机器验证",
            "自适应强度",
            "Form Follows Reviewer",
            "Spec 五段式骨架",
            "spec-lint",
            "AC 覆盖",
            "漂移检查",
            "一次通过率 / 返工率 / 缺陷密度",
            "代码库理解结论包",
            "上下文漂移",
            "Anthropic 官方博客",
            "OpenAI Codex",
            "GitHub Copilot coding agent",
            "Google People + AI Guidebook",
            "NIST AI Risk Management Framework Generative AI Profile",
            "OWASP Top 10 for LLM Applications 2025",
            "ISO/IEC 42001",
            "不把任一工具的能力写成当前会话必然可用",
            "阿里内网万言离职书〈置身钉内〉原文，已刷屏",
            "公开转述/OCR 复盘参考来源",
            "AI 产品从战略叙事、AI 原型或发布会目标进入工程化前应检查业务 context、真实工作流、用户收益/负担、权限责任、旧系统接入、灰度止损、成本稳定性和事实边界",
            "不把文章内容写成钉钉/ONE 官方事实、行业结论、当前工具能力或 Execution Grant",
            "从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战",
            "KEEN的创享",
            "2026-06-04 21:39",
            "移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文",
            "模糊需求 -> 结构化需求文档 -> 业务流 -> 原型/页面说明 -> 开发执行任务 -> 验收发布路径",
            "`obra/superpowers`",
            "2026-06-07",
            "6fd4507659784c351abbd2bc264c7162cfd386dc",
            "ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3",
            "references/external-superpowers/",
            "superpowers-skill-library.md",
            "不复制或运行外部脚本、hooks、插件 manifest、package 脚本",
        ],
    ),
)
check(
    "ai-native workflow keeps intent to production role loop",
    has_reference_header(ai_native_intent_to_production)
    and has_task_reading_index(ai_native_intent_to_production)
    and has_all(
        ai_native_workflow_skill,
        [
            "角色协作 Loop",
            "references/intent-to-production-loop.md",
            "Role Collaboration Loop Map",
            "Intent-to-Production Role Loop Map",
            "从意图 / 需求收集到生产交付",
            "AI Maker / Checker",
            "能力 / 约规来源",
            "设计评审",
            "编码评审",
            "可用性 / 安全性 / 可靠性评估",
        ],
    )
    and has_all(
        ai_native_intent_to_production,
        [
            "# 角色协作 Loop：意图到生产交付",
            "Role Collaboration Loop Map",
            "Intent-to-Production Role Loop Map",
            "能力 / 约规来源",
            "阶段能力与约规来源",
            "阶段名只是编排坐标，不是能力来源",
            "每个阶段必须回指专项 Skill、reference 或脚本",
            "意图 / 反馈 / 业务目标",
            "需求收集与事实分层",
            "产品 / 交互设计与验收种子",
            "设计评审 / PRD-系分合议预审",
            "TDD / 测试设计",
            "编码实现 / AI Maker 执行",
            "编码评审 / AI Checker / 架构师 CR",
            "可用性 / 安全性 / 可靠性评估",
            "验证发布 / 监控 / 回滚准备",
            "生产反馈 / 复盘 / 知识回流",
            "UED / 交互设计",
            "属于产品岗",
            "AI Maker",
            "AI Checker",
            "Design Reviewer",
            "Code Reviewer",
            "Usability / Safety / Security Reviewer",
            "质量 / 测试门禁",
            "发布 owner",
            "product-architecture-expert/references/product-design-and-prd.md",
            "senior-software-architect/references/testing.md",
            "senior-software-architect/references/coding-review-deep-dive.md",
            "java-service-code-generator/references/code-generation-rules.md",
            "写代码的 Agent 不能自证通过",
            "不允许模拟模块、内存版业务 Service 或无业务入口 demo",
            "把阶段名当能力来源",
            "GSD、CAD、Goal、Harness、Grant、Agent Loop 都是本流程的内部处理层或边缘流程",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "Loop Engineering：让 AI 自己跑起来，你只管验收",
            "https://mp.weixin.qq.com/s/Ng_qit1H5t6yhqjVGNIHzg",
            "作者/账号字段为 `算法屋`",
            "intent-to-production-loop.md",
            "Automations、Worktrees、Skills、Connectors、Sub-agents、State",
            "从意图 / 需求收集到生产交付的多角色 Loop",
            "不把 `/goal`、定时器、连接器、自动开 PR、sub-agent、worktree 或任何工具能力写成当前会话默认可用",
        ],
    )
    and has_all(
        "README.md",
        [
            "进入角色协作 Loop",
            "能力来源：产品 / 交互设计和验收种子回到 `产品架构专家`",
            "系分、TDD、编码、最小正确实现检查、CR、安全可靠和发布回到 `资深架构师`",
            "结构化 Java Service 生成回到 `java-service-code-generator`",
            "设计、设计评审、TDD、编码、编码评审、可用性/安全性评估、验证发布",
        ],
    ),
)
check(
    "ai-native workflow keeps autonomous discovery delivery loop",
    has_all(
        ai_native_workflow_skill,
        [
            "自主交付闭环",
            "自我挖掘",
            "自主交付控制卡",
            "必须人工确认",
            "不把“可继续推进”写成“已经授权”",
        ],
    )
    and has_all(
        ai_native_intent_to_production,
        [
            "自我挖掘与确认边界",
            "自主交付控制卡",
            "可自我挖掘",
            "可自我规划",
            "可自动执行",
            "必须人工确认",
            "确认规则",
            "不能确认业务意图、需求价值、用户验收、架构批准、测试通过、CR 准出、Git 授权或上线审批",
        ],
    )
    and has_all(
        ai_native_agent_loop_engineering,
        [
            "自主推进边界",
            "Discover evidence",
            "Confirm boundary",
            "Requirement CR",
            "TDD candidate / RED",
            "Complete / Loop / Stop / Human handoff",
            "自我规划当人工确认",
        ],
    )
    and has_all(
        ai_native_code_delivery_closed_loop,
        [
            "自主交付完成判断",
            "Agent 自述触发",
            "Complete / Loop / Stop / Human handoff",
            "必须人工确认项",
            "不能把任务标记为完成",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "自主交付控制卡",
            "需求确认",
            "AI 自述完成",
            "Complete / Loop / Stop / Human handoff",
        ],
    ),
)
check(
    "core problem diagnosis sources and routing stay wired",
    has_all(
        ai_native_workflow_skill,
        [
            "问题核心诊断",
            "先抓核心，后开药方",
            "Knowledge-to-Execution Card",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "Round 0D：问题核心诊断门禁",
            "问题核心诊断卡",
            "不用流程勤奋掩盖战略懒惰",
            "进入 PRD / OpenSpec / GSD / CAD / Loop / 工具准入结论",
        ],
    )
    and has_all(
        product_skill,
        [
            "本技能继承仓库 `AGENTS.md` 的顶层处事原则",
            "概念定名先于扩需求",
            "需求扩张时先区分用户价值、组织收益、文化/品牌意义和单纯欲望",
            "产品原则不替代证据",
        ],
    )
    and has_all(
        product_architecture,
        [
            "1.3 概念定名与需求止损",
            "需求无止境 / 概念定名 / 价值意义摇摆",
            "价值 / 意义边界",
            "概念定名与需求止损卡",
        ],
    )
    and has_all(
        senior_skill,
        [
            "本技能继承仓库 `AGENTS.md` 的顶层处事原则",
            "先抓病机再开药方",
            "顶层原则落到工程证据",
        ],
    )
    and has_all(
        "senior-software-architect/references/architecture.md",
        [
            "1.2 问题核心诊断",
            "可用三层诊断",
            "病",
            "证",
            "症",
            "5.11 四定变化治理",
            "先定方向，再定性质，再定位置，最后定量",
            "GSD/CAD 任务拆解必须能说明每个 Atomic Task 的定向、定性、定位和验证方式",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "欲读经典，先开心门",
            "产品的创新｜需求是无止境的吗？",
            "一阖一辟谓之变，往来不穷谓之通｜变通",
            "如何抓住问题的核心？",
            "反脑补阅读纪律、问题核心诊断、概念定名、需求止损、变化治理和证据边界",
        ],
    )
    and has_all(
        product_source_map,
        [
            "问题核心、概念定名与需求止损",
            "产品的创新｜需求是无止境的吗？",
            "概念定名、需求止损、价值 / 意义边界",
            "不把传统文化或医学观点写成产品事实、用户研究结论、Backlog 决策、合规结论或 Execution Grant",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "问题核心诊断与变化治理组",
            "四篇文章均已通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者线索、页面时间字段和正文 / meta 正文",
            "变化治理中的定向、定性、定位、定量顺序",
            "病 / 证 / 症",
            "不把传统文化、医学类比或个人修习语境写成架构标准、项目事实、合规结论、生产审批或 Execution Grant",
        ],
    )
    and has_all(
        "README.md",
        [
            "问题核心诊断、反脑补证据边界、概念定名、需求止损",
            "定向 / 定性 / 定位 / 定量变化治理",
            "不把传统文化或医学观点写成产品事实、架构结论、合规结论、生产审批或 Execution Grant",
        ],
    ),
)
check(
    "ai-native workflow keeps Superpowers skill library boundary",
    has_reference_header(ai_native_superpowers_library)
    and has_task_reading_index(ai_native_superpowers_library)
    and has_all(
        ai_native_superpowers_library,
        [
            "# Superpowers Skill Library 外部参考",
            "不是本仓库的顶层可安装 Skill",
            "不是当前会话的自动执行授权",
            "brainstorming",
            "writing-plans",
            "executing-plans",
            "subagent-driven-development",
            "test-driven-development",
            "requesting-code-review",
            "receiving-code-review",
            "systematic-debugging",
            "verification-before-completion",
            "using-git-worktrees",
            "finishing-a-development-branch",
            "writing-skills",
            "2026-06-07",
            "6fd4507659784c351abbd2bc264c7162cfd386dc",
            "ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3",
            "MIT License",
            "仅复制 `skills/` 下 Markdown 资源和 LICENSE",
            "未复制外部脚本、hooks、插件 manifest、package 脚本",
            "外部 skill 原文里出现的 Git 提交、Git 推送、worktree、subagent、插件安装",
            "当前仓库 Git 操作仍遵守 `AGENTS.md`",
            "当前仓库 OpenSpec / Superpowers / Harness 生成的文档或计划默认使用中文",
            "Superpowers 调度结论",
            "不采用的外部默认流程",
        ],
    ),
)
check(
    "ai-native workflow keeps spec template practices gate",
    has_reference_header(ai_native_spec_template_practices)
    and has_task_reading_index(ai_native_spec_template_practices)
    and has_all(
        ai_native_workflow_skill,
        [
            "Spec / SDD / OpenSpec 模板最佳实践",
            "Spec 模板落地包",
            "references/spec-template-practices.md",
        ],
    )
    and has_all(
        ai_native_spec_template_practices,
        [
            "# Spec 模板最佳实践",
            "本文定义 AI Native 研发流程中 Spec / SDD / OpenSpec / Harness 输入的模板落地方式",
            "不把外部 Harness 写成默认依赖",
            "Spec 强度建议",
            "Spec 分层判断",
            "PRD / SDD / 实现 Spec 三层边界",
            "规范事实源与可生成性门禁",
            "规范事实源与可生成性检查",
            "系统 DNA: 不变量 / 状态流转 / 边界 / 演化规则 / 验证方式",
            "系统 DNA 门禁",
            "结构化契约",
            "正例 / 反例",
            "五支柱验证",
            "需求 / 设计 / 编码标准门禁",
            "需求标准",
            "设计标准",
            "编码标准",
            "防御式编程",
            "需求基线稳定性门禁",
            "系统/产品需求未确认、需求条目不可验证、图文不可追踪或衍生需求无 owner",
            "关键标准没有强制/推荐分级、原因/示例、验证方式或适用范围",
            "五段式结构",
            "Form Follows Reviewer",
            "More Context, Less Control",
            "轻量任务卡",
            "可评审 Spec",
            "Harness/GSD Spec",
            "CAD 候选 Spec",
            "AC 与测试映射",
            "Given-When-Then",
            "spec-lint",
            "AC 覆盖",
            "漂移检查",
            "风险自查",
            "AI 生成失败时，先把失败场景回写到 Spec / AC / 测试或项目规则",
            "Spec 也是实现和 CR 的检查清单",
            "轻重切换",
        ],
    )
    and has_all(
        ai_native_code_delivery_closed_loop,
        [
            "spec-template-practices.md",
            "Spec 模板落地建议",
            "Spec 回写与重试闭环",
            "识别 AI 错误模式",
            "重试次数必须有上限",
            "Form Follows Reviewer",
            "spec-lint",
            "ac-coverage",
            "drift-check",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "spec-template-practices.md",
            "可评审 Spec 模板",
            "Spec 强度、五段式骨架、AC 与测试映射、spec-lint、AC 覆盖和漂移检查",
        ],
    )
    and has_all(
        ai_native_agentic_governance,
        [
            "spec-template-practices.md",
            "AC 编号与测试映射",
            "spec-lint / AC 覆盖 / 漂移检查",
            "可评审 Spec 模板",
        ],
    )
    and has_all(
        ai_native_verification_release,
        [
            "spec-template-practices.md",
            "Spec / AC 编号",
            "AC 覆盖",
            "漂移检查",
            "五支柱验证",
            "AI 生成代码和人工代码使用同一合并标准",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "spec-template-practices.md",
            "Form Follows Reviewer",
            "Spec 五段式骨架",
            "Spec 驱动开发：让 AI 知道该写什么，不该写什么",
            "规范驱动开发（SDD）：用 AI 写生产级代码的完整指南",
            "PRD / SDD / 实现 Spec 三层边界",
            "Spec 作为事实来源",
            "五支柱验证",
            "失败回写 Spec 再重试",
            "Spec 作为实现和 CR 检查清单",
            "AC 编号",
            "Given-When-Then",
            "spec-lint",
            "AC 覆盖",
            "漂移检查",
            "不复制原文、图片、案例细节、ASD / SSD Harness 命令体系",
        ],
    )
    and has_all(
        "README.md",
        [
            "Spec/SDD 模板最佳实践",
            "Spec 驱动开发：让 AI 知道该写什么，不该写什么",
            "规范驱动开发（SDD）：用 AI 写生产级代码的完整指南",
        ],
    ),
)
check(
    "ai-native workflow keeps goal composition gate",
    has_reference_header(ai_native_goal_composition)
    and has_task_reading_index(ai_native_goal_composition)
    and has_all(
        ai_native_goal_composition,
        [
            "# Loop 目标层与 Goal 组合",
            "Goal 是显式目标管理和持续推进契约",
            "对外统一说法是 Loop",
            "Goal 是 Loop 的目标层",
            "GSD 是 Loop 的分波计划层",
            "CAD 是 Loop 的原子执行子循环",
            "当前 Loop 使用了哪些内部层",
            "GSD + Goal",
            "CAD + Goal",
            "Spec + Goal",
            "CR/发布 + Goal",
            "Goal 卡",
            "Goal ID",
            "成功标准",
            "预算 / 时间盒",
            "停止条件",
            "Goal Ledger",
            "Draft / Ready / Active / Blocked / Verified / Closed / Superseded",
            "Goal 不会自动创建运行时 Goal",
            "只有在用户明确要求按任务计划推进且 Plan Grant 字段齐备时",
            "GSD/CAD 默认授权收敛到 Goal / Plan Grant / Wave / CAD Grant",
            "Goal 可以挂接 Plan Grant、Wave Grant 或 CAD Grant",
            "GSD 规划必须给出阶段/任务提交切片",
            "每个 Wave 的授权策略",
            "每个 Wave 的提交切片",
            "Plan Grant 用来把 `GSD + Goal` 从目标管理变成可推进的低风险执行边界",
            "Plan Grant: Draft / Active / Suspended",
            "建议 commit message",
            "范围内低风险本地任务按计划推进",
            "Wave Grant 只能覆盖该 Wave 内互不冲突、低风险、可验证、可回滚的任务",
            "Codex 替我审批只可作为当前 CAD Grant 范围内低风险工具审批通道",
            "用 Goal、Wave 状态或 Codex 替我审批扩大默认授权范围",
            "GSD 管 Wave 和任务顺序，Goal 管目标、成功标准、状态、预算、停止条件、验证证据和交接节奏",
            "在 GSD 场景中，Goal 的完成线必须是生产可用能力",
            "真实业务入口、生产边界、验收种子、验证证据、发布/回滚条件和责任 owner",
            "生产可用能力:",
            "demo 可跑",
            "mock 已通",
        ],
    )
    and has_all(
        ai_native_workflow_skill,
        [
            "目标与大项目编排",
            "Goal 组合包",
            "references/goal-composition.md",
            "Execution Grant 缺口",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "goal-composition.md",
            "是否需要 Goal 组合",
            "Goal 卡、GSD Wave / Goal 映射",
        ],
    )
    and has_all(
        ai_native_agentic_governance,
        [
            "goal-composition.md",
            "Goal ID",
            "Goal 状态",
            "Goal Ledger 更新",
            "不把 Goal 写成 Execution Grant",
        ],
    )
    and has_all(
        ai_native_spec_template_practices,
        [
            "goal-composition.md",
            "关联 Goal",
            "Goal 成功标准",
            "Goal / AC 映射",
        ],
    )
    and has_all(
        ai_native_code_delivery_closed_loop,
        [
            "goal-composition.md",
            "Goal 交付闭环",
            "Goal 追踪",
            "目标闭环",
        ],
    )
    and has_all(
        ai_native_verification_release,
        [
            "goal-composition.md",
            "Goal 完成度判断",
            "Goal ID / 成功标准",
            "是否可以把 Goal 标记为 Verified 或 Closed",
        ],
    )
    and has_all(
        "README.md",
        [
            "生产可用能力",
            "按目标和任务计划推进",
            "目标不等于执行授权",
            "不要把目标当授权",
        ],
    ),
)
check(
    "ai-native workflow keeps agent loop engineering gate",
    has_reference_header(ai_native_agent_loop_engineering)
    and has_task_reading_index(ai_native_agent_loop_engineering)
    and has_all(
        ai_native_workflow_skill,
        [
            "实际项目编码 Loop",
            "Coding Loop Contract",
            "references/agent-loop-engineering.md",
            "状态载体",
            "反馈源",
            "验证者",
            "预算 / 最大轮次",
            "无进展检测",
            "生产可用 Loop 门禁",
        ],
    )
    and has_all(
        ai_native_agent_loop_engineering,
        [
            "# Agent Loop Engineering",
            "Loop 不是更长的 Prompt",
            "Goal -> State -> Plan -> Act -> Observe -> Decide -> Verify -> Stop / Handoff",
            "角色 Loop 场景视图",
            "四类场景视图",
            "真实项目编码 Loop 额外字段",
            "Coding Loop Contract",
            "实际项目编码 Loop",
            "内部层映射",
            "反馈闭环成熟度",
            "L2 / L3 / L4 / L5",
            "Verification Cluster Gate",
            "业务不变量",
            "验证簇 ID",
            "生产重放样本",
            "有限变异 / 对抗检查",
            "测试通过、覆盖率提高和 bug 下降都只是证据",
            "L5 只能作为目标架构",
            "代码写入范围",
            "只读范围",
            "失败测试 / 验收样例",
            "TDD 顺序",
            "最小正确实现门禁",
            "复杂度投资门禁",
            "控制 AI 战术化编码和复杂性扩散",
            "不把测试变绿、PR 变多或代码更短当设计质量",
            "如果简单需求牵动大量文件",
            "浅模块",
            "直通包装",
            "测试变绿，但设计更难理解",
            "验证命令",
            "独立 Checker",
            "状态回写位置",
            "提交切片",
            "GSD + Goal + Loop",
            "反馈与验证",
            "预算和停止条件",
            "最大轮次",
            "无进展检测",
            "状态载体优先级",
            "Plan Grant 与 Loop 预算绑定",
            "失败回写路径",
            "生产可用 Loop 门禁",
            "自动化心跳",
            "隔离执行",
            "Maker / Checker 解耦",
            "可复现状态",
            "观测 / 审计",
            "人工接管",
            "发布 / 回滚",
            "理解债控制",
            "Skill 是复用单位",
            "不把 Loop 写成无条件自动授权",
        ],
    )
    and has_all(
        ai_native_agentic_governance,
        [
            "agent-loop-engineering.md",
            "Loop 是运行循环契约",
            "Loop Orchestrator",
            "状态载体",
            "反馈源",
            "验证者",
            "无进展检测",
        ],
    )
    and has_all(
        ai_native_goal_composition,
        [
            "GSD + Goal + Loop",
            "Loop ID",
            "状态载体",
            "反馈源",
            "验证者",
            "无进展检测",
            "Loop 完成只代表某轮循环达到停止条件",
        ],
    )
    and has_all(
        ai_native_code_delivery_closed_loop,
        [
            "Agent Loop 反馈闭环",
            "Loop 是否有状态载体、反馈源、验证者、预算和停止条件",
            "生产可用 Loop 准出判断",
            "Loop 是否具备隔离执行、可复现状态、Maker / Checker 解耦、观测审计、人工接管和发布/回滚",
            "连续两轮没有新增证据",
            "Loop 稳定性",
        ],
    )
    and has_all(
        ai_native_gsd_cad_admission,
        [
            "Agent Loop 准入卡",
            "GSD / Loop / CAD 协同状态机",
            "Engineering Handoff Card",
            "Plan Grant Active",
            "CAD Loop Active",
            "Wave Loop 与 CAD Loop 的差异",
            "Loop 预算",
            "失败回写",
            "Goal + 状态载体 + 反馈源 + 验证者 + 预算/最大轮次 + 无进展检测 + 停止条件",
            "只能作为待补齐的 Loop 候选",
        ],
    )
    and has_all(
        "README.md",
        [
            "AI 代码交付闭环",
            "内部路由",
            "Agent Loop Engineering",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "【译】别再手动写 Prompt 了，去写 Loop——但 Loop 到底是什么？",
            "Loop Engineering（Agent 闭环工程）",
            "agent-loop-engineering.md",
            "code-delivery-closed-loop.md",
            "GSD + Goal + Loop",
            "生产可用 Loop 门禁",
            "Maker / Checker 解耦",
            "状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件",
            "Skill 作为复用单位",
            "不把 `/goal`、`/loop` 或 auto mode 写成无条件授权",
        ],
    ),
)
check(
    "ai-native workflow keeps architecture entropy loop gate",
    has_all(
        ai_native_workflow_skill,
        [
            "架构排熵 Loop",
            "腐朽门禁",
            "Architecture Entropy Card",
            "排熵与复杂度投资优先于战术生成",
            "低风险动作",
        ],
    )
    and has_all(
        ai_native_agent_loop_engineering,
        [
            "## 4E. 架构排熵 Loop",
            "Architecture Entropy Card",
            "可删除性",
            "局部推理边界",
            "承重行为",
            "废弃 API / dead path",
            "概念膨胀 / 事实源分裂",
            "治理自腐 / 守卫自检",
            "可执行约束 / 可追溯理由链",
            "时间边界三问",
            "复杂度棘轮",
            "熵增仪表",
            "理由保鲜",
            "低风险动作",
            "人工 triage owner",
            "不把能自动扫描当成可以自动删除",
            "守卫自检必须和扫描结果一起输出",
            "Ponytail-style 过度设计检查只能标注可删除复杂度候选",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "深度思考：架构腐朽 & Loop Engineering",
            "https://mp.weixin.qq.com/s/wINKSDQCroWBvf29h567zA",
            "作者字段为 `lencx`",
            "账号字段为 `浮之静`",
            "架构排熵 Loop",
            "Architecture Entropy Card",
            "2026-06-22",
            "可执行约束 / 可追溯理由链",
            "时间边界三问",
            "不把能自动扫描写成可以自动删除、迁移、重写、合并、测试通过、CR 结论、执行授权或上线审批",
            "DietrichGebert Ponytail",
            "最小正确实现门禁",
            "过度设计专项 CR",
        ],
    )
    and has_all(
        "README.md",
        [
            "架构排熵",
            "内部路由",
            "深度思考：架构腐朽 & Loop Engineering",
        ],
    ),
)
check(
    "ai-native workflow keeps knowledge expression and nonstandard problem gates",
    has_all(
        ai_native_workflow_skill,
        [
            "知识表达",
            "非标问题",
            "Knowledge-to-Execution Card",
            "实际项目编码 Loop",
            "Coding Loop Contract",
            "执行可靠性",
            "知识表达、真实编码 Loop、反馈闭环",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "Round 0E：知识表达门禁",
            "Knowledge-to-Execution Card",
            "Round 0F：非标问题门禁",
            "非标问题处理包",
            "文章观点、管理要求、产品口号、工具能力、AI 草稿和用户愿望只能作为输入",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "回到本质：软件到底应该怎么造？",
            "高水平工程师都擅长解决“非标问题”",
            "一文读懂什么是Loop",
            "知识表达门禁",
            "实际项目编码 Loop 契约",
            "不得让 Loop 在缺少失败测试 / 验收样例、写入范围、验证命令、独立 Checker 和状态回写位置时修改生产代码",
        ],
    ),
)
check(
    "product and senior skills keep nonstandard problem responsibility",
    has_all(
        product_skill,
        [
            "非标诉求不做传话筒",
            "产品岗提供解决方案，不被动搬运需求",
        ],
    )
    and has_all(
        product_routing,
        [
            "非标产品问题",
            "1.4 非标问题与解决方案责任",
            "不做传话筒",
        ],
    )
    and has_all(
        product_architecture,
        [
            "1.4 非标问题与解决方案责任",
            "非标产品问题卡",
            "产品岗和 UED 同属产品侧",
            "解决方案假设",
            "验收种子",
        ],
    )
    and has_all(
        product_source_map,
        [
            "高水平工程师都擅长解决“非标问题”",
            "非标诉求",
            "避免退化为传话筒",
        ],
    )
    and has_all(
        senior_skill,
        [
            "非标工程问题先建模",
            "最小可逆实验",
        ],
    )
    and has_all(
        senior_routing,
        [
            "非标工程问题 / 无标准答案",
            "1.3 非标工程问题",
            "最小可逆实验",
        ],
    )
    and has_all(
        architecture,
        [
            "1.3 非标工程问题",
            "非标工程问题卡",
            "问题机制",
            "最小可逆实验",
            "验证命令",
            "进入实际项目编码 Loop 时还要有状态回写位置和独立 Checker",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "软件本质与非标工程问题",
            "回到本质：软件到底应该怎么造？",
            "高水平工程师都擅长解决“非标问题”",
        ],
    ),
)
check(
    "ai-native workflow keeps code delivery closed-loop gate",
    has_reference_header(ai_native_code_delivery_closed_loop)
    and has_task_reading_index(ai_native_code_delivery_closed_loop)
    and has_all(
        ai_native_workflow_skill,
        [
            "AI 代码交付闭环",
            "Spec / SDD / OpenSpec",
            "知识回流",
            "references/code-delivery-closed-loop.md",
        ],
    )
    and has_all(
        ai_native_code_delivery_closed_loop,
        [
            "AI 代码交付闭环",
            "编码阶段提速明显，但端到端交付、CR、测试、对齐或返工没有明显改善",
            "最小 Spec 强度",
            "Harness 三层闭环",
            "Orchestrator",
            "Knowledge",
            "Delivery",
            "机器验证与独立证据",
            "生成者不能自己给自己签字",
            "Spec 回写与重试闭环",
            "处理 AI 生成失败或反复返工",
            "AI 生成失败不是只换提示词",
            "CR 减负与可理解交接",
            "知识回流",
            "CONTEXT.md",
            "AGENTS.md",
            "CLAUDE.md",
            "一次通过率",
            "返工率",
            "缺陷密度",
            "规范命中率",
            "生成成功率",
            "缺陷模式回写率",
            "三问法",
            "外部 Harness",
            "不把外部文章中的 ASD / SSD Harness、命令体系、目录结构或脚本写成本技能默认依赖",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "code-delivery-closed-loop.md",
            "AI 代码交付闭环",
            "编码提速但 CR、测试、对齐、返工或上线质量没有改善",
        ],
    )
    and has_all(
        ai_native_agentic_governance,
        [
            "code-delivery-closed-loop.md",
            "Delivery Gate Agent",
            "独立验证证据",
            "知识回流位置",
            "交付指标",
        ],
    )
    and has_all(
        ai_native_verification_release,
        [
            "code-delivery-closed-loop.md",
            "最终代码交付能力",
            "Spec 强度",
            "Harness 摘要",
            "CR 高频问题",
            "一次通过率、CR 轮次、缺陷密度、知识回流命中、上下文漂移、机器门禁覆盖",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "万字长文 | Spec 驱动开发实战：半年踩坑，我们如何让 AI 编码的交付真正闭环",
            "我们落地了 SDD，为什么团队效率没有体感提升？",
            "规范驱动开发（SDD）：用 AI 写生产级代码的完整指南",
            "code-delivery-closed-loop.md",
            "失败回写 Spec 再重试",
            "Orchestrator / Knowledge / Delivery 三层 Harness",
            "不把外部 Harness 写成当前会话默认依赖或执行授权",
            "不把文章中的比例和团队经验写成通用事实或项目当前指标",
        ],
    )
)
check(
    "ai-native workflow keeps authorized learning and experience placement",
    has_all(
        ai_native_code_delivery_closed_loop,
        [
            "学习归位判断",
            "授权学习与经验归位",
            "稳定上下文、项目规则和用户偏好没有进入合适载体",
            "项目公共知识",
            "Skill 方法增强",
            "用户长期偏好",
            "~/.skill-learning/",
            "只有用户明确同意后才能读取或写入",
            "已回流、建议回流、需要用户授权、不得回流",
            "未经授权，不得创建 `~/.skill-learning/`",
            "不得把用户长期偏好、个人工作方式或对话历史写进本仓库",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "一个让Codex变得越来越聪明的小方法",
            "像素与咖啡时光",
            "授权学习",
            "经验归位",
            "不把用户长期偏好写入仓库、安装目录或未授权学习目录",
        ],
    )
    and has_all(
        "README.md",
        [
            "一个让Codex变得越来越聪明的小方法",
            "授权学习、经验归位和知识回流",
            "不把用户长期偏好写入仓库、安装目录或未授权学习目录",
        ],
    ),
)
check(
    "ai-native governance keeps codebase visual understanding gate",
    has_all(
        ai_native_agentic_governance,
        [
            "图形化理解包",
            "组件/入口",
            "启动顺序",
            "认证权限",
            "外部系统",
            "数据/消息/状态流",
            "源码锚点",
            "未确认连接",
            "图只能降低认知负荷",
            "图形化理解 brief",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "如何让 AI 画出高质量架构图，一个Skill搞定",
            "日积月码",
            "图形化理解 brief",
            "不安装文中提到的外部 Skill",
            "不把外部工具生成结果当作架构质量结论",
        ],
    )
    and has_all(
        "README.md",
        [
            "如何让 AI 画出高质量架构图，一个Skill搞定",
            "陌生代码库图形化理解",
            "不安装文中提到的外部 Skill",
        ],
    ),
)
check(
    "ai-native workflow keeps PRD and system design deliberation review gate",
    has_all(
        ai_native_workflow_skill,
        [
            "PRD / 系分合议预审",
            "MAGI",
            "references/prd-system-design-review.md",
            "PRD / 系分合议预审报告",
        ],
    )
    and has_reference_header(ai_native_prd_system_design_review)
    and has_task_reading_index(ai_native_prd_system_design_review)
    and has_all(
        ai_native_prd_system_design_review,
        [
            "PRD 与系分合议预审",
            "MAGI 三角色",
            "A2A 虚拟评审",
            "IPD 式互审",
            "流程控制位",
            "主笔 / 决策 owner",
            "挑战者位",
            "review_task",
            "evaluation_task",
            "reporting_task",
            "ACCEPT",
            "REJECT",
            "PENDING",
            "预审报告和决策日志是过程资产",
            "进入正式文档时，只吸收 `ACCEPT` 后的最终结论",
            "根源需求",
            "产品定义",
            "产品边界",
            "稳定点 / 变化点",
            "边界坐标",
            "扩展点、抽象层和可配置能力是否能回指真实变化轴",
            "过度设计风险",
            "正式 PRD 是否只保留最终标准版本",
            "正式系分是否只保留当前有效设计",
            "双向追踪只记录当前有效条款、偏差、决策和下一步",
            "每条意见必须有锚点",
            "PRD 预审门禁",
            "系分预审门禁",
            "双向追踪",
            "准出与停止",
            "不能替代产品 owner、架构 owner、正式评审、测试通过或 Execution Grant",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "prd-system-design-review.md",
            "合议预审",
            "ACCEPT",
            "REJECT",
            "PENDING",
            "产品上下文包和 PRD-Lite 只保留工程化必须消费的最终业务事实",
        ],
    )
    and has_all(
        ai_native_agentic_governance,
        [
            "prd-system-design-review.md",
            "预审 Agent",
            "ACCEPT/REJECT/PENDING",
            "PRD / 系分是否已在需要时做合议预审",
        ],
    )
    and has_all(
        ai_native_verification_release,
        [
            "prd-system-design-review.md",
            "PRD / 系分合议预审进入验证矩阵",
            "ACCEPT",
            "REJECT",
            "PENDING",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "PRD 评审总返工？跟我把IPD的6个强角色、3个硬任务塞进你的Agent系统",
            "prd-system-design-review.md",
            "A2A 虚拟评审",
            "IPD 多角色反向拷问",
            "ACCEPT/REJECT/PENDING",
            "不把虚拟评审写成正式 IPD、合规确认、架构批准或 Execution Grant",
        ],
    ),
)
check(
    "ai-native workflow has realistic prompt fixtures and evaluation coverage",
    has_all(
        skill_eval_prompt_fixture,
        [
            "ai-native-should-end-to-end-product-engineering-workflow",
            "ai-native-should-gsd-cad-handoff",
            "ai-native-should-prd-system-design-deliberation-review",
            "ai-native-should-final-deliverable-document-gate",
            "ai-native-should-gsd-cad-admission-gate",
            "ai-native-should-gsd-cad-default-authorization",
            "ai-native-should-gsd-goal-composition",
            "ai-native-should-agent-loop-engineering",
            "ai-native-should-review-ai-coding-process",
            "ai-native-should-code-delivery-closed-loop",
            "ai-native-should-production-sdd-source-of-truth",
            "ai-native-should-knowledge-expression-gate",
            "ai-native-should-nonstandard-problem-mode",
            "ai-native-should-practical-coding-loop",
            "ai-native-should-feedback-loop-verification-cluster",
            "ai-native-should-spec-template-practices",
            "ai-native-should-development-standards-gate",
            "ai-native-should-product-system-dna-gate",
            "ai-native-should-quality-test-gate",
            "ai-native-should-change-understanding-gate",
            "ai-native-should-codebase-understanding-brief",
            "ai-native-should-tool-install-admission",
            "ai-native-should-design-code-alignment",
            "ai-native-should-fact-boundary-check",
            "ai-native-should-route-prd-work",
            "ai-native-should-route-cr-work",
            "ai-native-should-route-codegen-work",
            "ai-native-negative-prd-from-prototype",
            "ai-native-negative-code-review",
            "ai-native-negative-structured-codegen",
            "product-should-nonstandard-problem-solution",
            "senior-should-nonstandard-engineering-problem",
            "senior-should-invariant-verification-cluster",
            "ai-native-engineering-workflow",
        ],
    )
    and has_all(
        skill_evaluator,
        [
            "\"ai-native-engineering-workflow\"",
            "\"ai-native workflow\"",
            "\"GSD/CAD\"",
            "\"验证矩阵\"",
        ],
    ),
)
check(
    "README routes AI Native engineering workflow skill",
    has_all(
        "README.md",
        [
            "## 用户使用指南",
            "安装或同步后，Codex 会根据每个 `SKILL.md` 的 `name` 和 `description` 自动触发技能",
            "使用时不用先背 Skill 名称",
            "先帮我选路",
            "### 1. 一句话讲清目标",
            "我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>",
            "目标、材料、边界、风险、验证",
            "### 2. 按交付物选入口",
            "产品语义 / PRD / Backlog / 验收",
            "系分 / 架构 / 代码 / Bug / 测试 / CR / 发布",
            "跨角色产研交付 / 目标拆解 / 任务计划 / Spec / Harness / 质量发布闭环",
            "默认进入角色协作 Loop",
            "按设计、设计评审、TDD、编码、编码评审、可用性/安全性评估、验证发布和复盘回流分角色推进",
            "目标层、计划层、原子执行层和执行契约是内部层",
            "角色协作阶段只是编排坐标，不是能力来源",
            "能力来源：产品 / 交互设计和验收种子回到 `产品架构专家`",
            "系分、TDD、编码、最小正确实现检查、CR、安全可靠和发布回到 `资深架构师`",
            "结构化 Java Service 生成回到 `java-service-code-generator`",
            "Java Service 脚手架",
            "复杂可编辑架构图、代码库结构转图或架构描述转图",
            "正式图形默认 SVG，PNG 仅在明确要求时导出",
            "### 3. AI Native 只做编排",
            "`AI Native Engineering Loop` 是编排入口，不是万能执行入口",
            "默认先判断当前处于角色协作 Loop 的哪个阶段，再选最小场景视图",
            "只读理解视图",
            "产研交付视图",
            "验证发布视图",
            "知识回流视图",
            "默认输出骨架固定为",
            "证据边界必须区分事实、推断、待确认和范围外不做",
            "授权策略必须区分只读、计划内低风险执行、分波执行授权、原子任务授权和显式确认",
            "### 4. 产品到工程的默认闭环",
            "产品发现",
            "三卡交接",
            "编排准入",
            "工程执行",
            "质量理解门禁",
            "交付复盘",
            "每个阶段都要写能力 / 约规来源",
            "### 5. 体用原则",
            "体用合一",
            "避免体用混一",
            "阴阳互根",
            "执简驭繁",
            "### 6. 常用短句",
            "先帮我选路",
            "进入角色协作 Loop",
            "按目标和任务计划推进",
            "目标不等于执行授权",
            "进入自主交付闭环",
            "进入只读理解 Loop",
            "默认不写文件、不联网、不安装",
            "做质量门禁",
            "测试矩阵、验证顺序、CR 前置条件、失败回退和残余风险交接",
            "### 7. 最小输入清单",
            "`AI Native 研发流程编排`：当前材料成熟度",
            "`产品架构专家`：业务目标",
            "`资深架构师`：代码或文档路径",
            "`java-service-code-generator`：DDL/schema/Java 类/字段表格",
            "画图 / 工具准入",
            "### 8. 不要这样用",
            "只写一份普通 PRD、产品方案或 Backlog 决策",
            "只做系统设计、代码 CR、Bug、测试或生产变更",
            "角色协作 Loop 的目标是交付生产可用能力",
            "内存版业务 Service",
            "## 完整能力索引",
            "### AI Native Engineering Loop",
            "路径：[ai-native-engineering-workflow](./ai-native-engineering-workflow)",
            "跨产品、UED、架构、AI Maker / Checker",
            "目标拆解、任务计划",
            "Spec/Harness",
            "AI 代码交付闭环",
            "Gemini CLI / AgentRC / Understand Anything",
            "代码库知识图谱",
            "设计-代码对齐",
            "质量门禁",
            "只负责成熟度、owner、交接物、停止条件、授权策略和工具边界",
            "产品正文交给产品专家",
            "工程实现、最小正确实现检查和过度设计 CR 交给架构师",
            "结构化代码生成交给代码生成器",
            "内部路由",
            "从 AI 原型到工程化",
            "### 提示词公式",
            "用 <Skill 名称> + <任务类型> + <输入材料> + <目标产物> + <边界/风险> + <验证要求>",
            "用 AI Native Engineering Loop：按当前材料进入角色协作 Loop，输出当前阶段、角色视角、能力来源、owner、交接物、Loop Contract、验证门禁、停止条件和下一步分派。",
            "不覆盖现有文件",
            "### 最佳实践",
            "修改技能后先运行 `./scripts/validate.sh`",
            "`./sync-skills.sh --dry-run all`",
        ],
    ),
)
check(
    "README explains product expert and AI Native workflow usage",
    has_all(
        "README.md",
        [
            "### 产品架构专家",
            "路径：[product-architecture-expert](./product-architecture-expert)",
            "PRD、产品方案、需求说明",
            "产品洞察/机会雷达",
            "Backlog 决策",
            "原型/HTML/页面截图/交互稿反推 PRD",
            "能力地图、业务流程、状态机、规则矩阵",
            "支付与资金是重点能力",
            "输入材料、目标产物、业务边界、评审重点、验证要求",
            "Product Context Card",
            "业务目标、非目标、角色 / 主体、核心对象与状态、主流程与异常、关键规则、验收种子、风险与待确认项、专业确认方",
            "不负责工程实现、代码 Review 和生产排障",
            "### 资深架构师",
            "路径：[senior-software-architect](./senior-software-architect)",
            "架构设计、系统分析设计、技术方案、ADR、代码 Review、Bug 修复、测试/TDD、生产变更",
            "架构腐朽 / 排熵 / 可删除性评审",
            "代码或文档路径、现象/目标、运行环境、约束、期望验证命令",
            "不替代产品专家定义复杂业务语义、PRD 和金融产品规则",
            "### AI Native Engineering Loop",
            "`AI Native Engineering Loop` 是编排入口，不是万能执行入口",
            "产品正文交给 `产品架构专家`",
            "工程实现交给 `资深架构师`",
            "角色协作阶段只是编排坐标，不是能力来源",
            "不允许让 AI 随机推进模拟模块",
            "内存版业务 Service",
            "Gemini CLI / AgentRC / Understand Anything / Ponytail 准入",
            "用 AI Native Engineering Loop：按当前材料进入角色协作 Loop，输出当前阶段、角色视角、能力来源、owner、交接物、Loop Contract、验证门禁、停止条件和下一步分派。",
        ],
    ),
)
check(
    "senior skill uses three-step loading",
    has_all(
        senior_skill,
        [
            "运行时按三步加载",
            "复杂任务先读 `references/scenario-routing.md`",
            "只读取当前任务必要的 reference",
        ],
    ),
)
check(
    "senior skill routes diagram output",
    has_all(
        senior_skill,
        [
            "references/diagram-output.md",
            "系统架构图",
            "正式图形化交付默认只生成 SVG",
        ],
    ),
)
check(
    "senior skill delegates complete routing to scenario reference",
    has_all(
        senior_skill,
        [
            "`references/scenario-routing.md` 是本技能唯一完整路由表",
            "复杂产品语义",
            "优先使用 `产品架构专家`",
        ],
    ),
)
check(
    "senior skill anchors context-responsive architecture",
    has_all(
        senior_skill,
        [
            "因境制宜",
            "业务阶段、组织能力、代码现状、运行环境和验证成本",
            "外部方法论只能辅助判断",
        ],
    ),
)
check(
    "senior skill anchors AI-era constraint first",
    has_all(
        senior_skill,
        [
            "约束优先",
            "代码生成越便宜",
            "前置约束控制复杂度和注意力成本",
        ],
    ),
)
check(
    "senior skill and references guard comment readability",
    has_all(
        senior_skill,
        [
            "不得用注释替代可读性重构",
            "命名、方法抽取、常量/枚举、强类型和值对象、测试表达意图",
            "Why not",
        ],
    )
    and has_all(
        coding,
        [
            "注释说明“为什么这样做、为什么不那样做、边界是什么、风险是什么”",
            "不得用注释掩盖弱命名、长方法、魔法值、弱类型或隐式契约",
            "AI 生成代码交付前必须做注释去噪",
            "测试用例名、Given/When/Then 结构和关键断言可以作为可执行文档",
        ],
    )
    and has_all(
        review,
        [
            "注释与可读性重构",
            "注释替代表达",
            "AI 注释噪声",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "编写高质量代码注释与可读性重构指南",
            "注释只补充业务约束、设计取舍、外部规则、历史坑点和 Why not",
            "不得用注释掩盖弱命名、长方法、魔法值、弱类型、隐式契约或缺测试",
        ],
    ),
)
check(
    "senior metadata triggers diagram output",
    all(
        term in frontmatter(senior_skill)
        for term in ["架构图", "时序图", "状态机", "ADR", "生产变更", "陌生代码库"]
    ),
)
check(
    "senior openai yaml mentions visual output",
    has_all(senior_agent, ["默认输出 SVG", "发布回滚和生产风险"]),
)
check(
    "product skill uses three-step loading",
    has_all(
        product_skill,
        [
            "运行时按三步加载",
            "复杂产品问题先读 `references/product-scenario-routing.md`",
            "只读取当前任务必要的 reference",
        ],
    ),
)
check(
    "product skill routes diagram output",
    has_all(
        product_skill,
        [
            "references/diagram-output.md",
            "产品架构图",
            "正式图形化交付默认只生成 SVG",
        ],
    ),
)
check(
    "product skill anchors simplicity over complexity",
    has_all(
        product_skill,
        [
            "执简驭繁",
            "用最少稳定对象、流程、规则和验收口径统摄复杂业务",
            "复杂知识下沉到 references",
            "可重复、可审计动作交给 scripts",
        ],
    ),
)
check(
    "product skill guards low cost feature noise",
    has_all(
        product_skill,
        [
            "AI 生成和低成本原型场景",
            "避免无效功能噪声",
            "先控噪声再扩展",
        ],
    ),
)
check(
    "product expert hands off domain naming to reduce comment debt",
    has_all(
        product_skill,
        [
            "领域术语",
            "产品上下文交接卡（Product Context Card）",
        ],
    )
    and has_all(
        product_ai_native_context,
        [
            "领域术语 / 业务命名建议",
            "下游建模、代码命名、测试命名和规则追踪",
            "减少工程注释债",
        ],
    )
    and has_all(
        product_prd,
        [
            "领域术语、规则名、状态名和异常名",
            "不要让研发只能用注释解释未命名的业务规则",
            "领域命名",
        ],
    )
    and has_all(
        product_source_map,
        [
            "领域命名与工程可读性",
            "编写高质量代码注释与可读性重构指南",
            "减少下游工程只能靠注释解释未命名业务规则的注释债",
        ],
    ),
)
check(
    "product metadata triggers diagram output",
    all(
        term in frontmatter(product_skill)
        for term in ["PRD", "需求说明", "原型/页面截图/交互稿反推需求", "用例图", "产品架构图", "流程图", "状态机", "外卡收单", "Mastercard", "工程实现"]
    ),
)
check(
    "product openai yaml mentions visual output",
    has_all(product_agent, ["原型", "页面截图", "默认输出 SVG", "待确认项"]),
)
check(
    "product openai yaml mentions acquiring specialty",
    has_all(product_agent, ["支付资金专项"]),
)
check(
    "codegen metadata triggers only structured generation",
    has_all(
        codegen_skill,
        [
            "DDL/SQL",
            "schema 文件",
            "字段表格",
            "有结构化输入",
            "被 AI Native 分派时，先消费 Engineering Handoff Card、授权策略和写入范围",
            "生成后交接卡至少包含",
            "生成 / 修改文件、写入目录和是否覆盖既有文件",
            "输入来源、结构化字段、脚本参数和推断假设",
            "已执行的验证命令、结果、未执行原因和残余风险",
            "ServiceImpl",
            "仅在用户明确要求生成、转换、脚手架或配套代码",
            "代码评审、Bug 修复和补测试优先交给架构师",
        ],
    )
    and has_all(
        "java-service-code-generator/agents/openai.yaml",
        [
            "DDL/schema",
            "字段表格",
            "Wind/Nobe Service 脚手架",
            "文件清单、关键假设、验证结果和交接风险",
        ],
    ),
)
check(
    "large references expose task-level reading indexes",
    all(
        has_task_reading_index(path)
        for path in [
            "senior-software-architect/references/project-governance-standards.md",
            *project_governance_refs,
            "senior-software-architect/references/testing-practices.md",
            *testing_practice_refs,
            "senior-software-architect/references/skill-tree.md",
            *skill_tree_refs,
            "senior-software-architect/references/architecture.md",
            "senior-software-architect/references/clean-code.md",
            "senior-software-architect/references/coding-review-deep-dive.md",
            "senior-software-architect/references/language-agnostic-architecture.md",
            "senior-software-architect/references/product-design.md",
            "senior-software-architect/references/production-readiness.md",
            "senior-software-architect/references/review-and-output-templates.md",
            "senior-software-architect/references/security-architecture.md",
            "senior-software-architect/references/source-map.md",
            "senior-software-architect/references/wind-projects-patterns.md",
            "senior-software-architect/references/system-analysis-design.md",
            "senior-software-architect/references/system-analysis-template.md",
            "senior-software-architect/references/scenario-routing.md",
            "senior-software-architect/references/workflow.md",
            "senior-software-architect/references/ai-assisted-engineering.md",
            "senior-software-architect/references/cad-mode.md",
            "senior-software-architect/references/testing.md",
            "senior-software-architect/references/debugging-diagnosis.md",
            "senior-software-architect/references/diagram-output.md",
            "senior-software-architect/references/knowledge-graph.md",
            "senior-software-architect/references/coding-standards.md",
            "product-architecture-expert/references/product-prd-template.md",
            "product-architecture-expert/references/product-prd-quality-gates.md",
            "product-architecture-expert/references/product-prd-financial-appendix.md",
            "product-architecture-expert/references/product-prd-operations-and-data.md",
            "product-architecture-expert/references/product-design-and-prd.md",
            "product-architecture-expert/references/product-insight-analyst.md",
            "product-architecture-expert/references/po-backlog-manager.md",
            "product-architecture-expert/references/payment-methodology.md",
            "product-architecture-expert/references/clearing-settlement.md",
            "product-architecture-expert/references/payment-design-checklists.md",
            "product-architecture-expert/references/card-network-and-card-rails.md",
            "product-architecture-expert/references/global-payment-emerging.md",
            "product-architecture-expert/references/glossary.md",
            "product-architecture-expert/references/diagram-output.md",
            "product-architecture-expert/references/dispute-refund-and-chargeback-operations.md",
            "product-architecture-expert/references/formance-reference-patterns.md",
            "product-architecture-expert/references/highnote-reference-patterns.md",
            "product-architecture-expert/references/payment-channel-routing-and-operations.md",
            "product-architecture-expert/references/payment-rails-ach-and-bank-transfers.md",
            "product-architecture-expert/references/payment-risk-fraud-and-merchant-operations.md",
            "product-architecture-expert/references/payment-scenario-routing.md",
            "product-architecture-expert/references/product-architecture-methodology.md",
            "product-architecture-expert/references/product-scenario-routing.md",
            "product-architecture-expert/references/regulatory-baseline.md",
            "product-architecture-expert/references/skill-tree.md",
            "product-architecture-expert/references/source-map.md",
            "product-architecture-expert/references/virtual-card-and-vcc.md",
        ]
    )
    and has_all(
        reference_index_audit,
        [
            "REQUIRED_INDEX_THRESHOLD",
            "REQUIRED_HEADING",
            "ALTERNATIVE_REQUIRED_COLUMNS",
            "REQUIRED_INDEX_FILES",
            "OK reference index audit",
        ],
    ),
)
check(
    "source map audit guards unverifiable external articles",
    has_all(
        source_map_audit,
        [
            "Audit source-map attribution and unverifiable-source boundaries",
            "does not access the",
            "network",
            "KNOWN_UNVERIFIABLE_URLS",
            "公开 HTML 中可读取到标题、作者、发布时间和正文",
            "HTML fallback source missing trace term",
            "HTML fallback source must record read date",
            "SENIOR_SOURCE_MAP",
            "SENIOR_RULE_TERMS",
            "FRESHNESS_TERMS",
            "require_freshness_terms=True",
            "product-missing-freshness-gate",
            "product-missing-current-verification-boundary",
            "senior-missing-freshness-gate",
            "不把读取日期当成当前核验日期",
            "不代表来源仍然最新可用",
            "外部知识时效性门禁",
            "不作为生产、资金、安全、合规、外部 API、SDK、云产品、法规规则或上线结论",
            "https://mp.weixin.qq.com/s/vHJ7LlePC8o5qV84XVtU4Q",
            "2026-05-26 Playwright 核验结果为页面已被发布者删除",
            "正文不可复核",
            "不得作为已吸收来源",
            "stale attribution for deleted clearing article",
            "--self-test",
            "absorbed-unverifiable",
            "missing-audit-date",
            "missing-downgrade-term",
            "stale-deleted-clearing-attribution",
            "duplicate-url",
            "wechat-missing-readable-or-audit-status",
            "html-fallback-missing-playwright-trace",
            "html-fallback-missing-date",
            "html-fallback-missing-fields",
            "html-fallback-rule-wording-detected",
            "OK source map audit",
            "OK source map self-test",
        ],
    )
    and has_all(
        "scripts/validate.sh",
        [
            "==> source map audit",
            "scripts/audit-source-map.py",
            "scripts/audit-source-map.py --self-test",
        ],
    ),
)
check(
    "skill supply-chain audit surfaces freshness-sensitive URL risk",
    has_all(
        "scripts/audit-skills.sh",
        [
            "external URL reference lines found",
            "unique external URLs",
            "unique freshness-sensitive external URLs found",
            "current task conclusions must re-verify official/current sources",
            "sort -u",
            "外部知识时效性门禁",
            "不代表来源仍然最新可用",
            "不把读取日期当成当前核验日期",
            "核验日期",
            "确认方",
            "freshness-sensitive URL guard missing required term",
        ],
    ),
)
check(
    "senior source map preserves freshness boundary",
    has_all(
        senior_source_map,
        [
            "不把读取日期当成当前核验日期",
            "不代表来源仍然最新可用",
            "外部知识时效性门禁",
            "来源、版本或发布日期",
            "核验日期",
            "确认方",
            "不作为生产、资金、安全、合规、外部 API、SDK、云产品、法规规则或上线结论",
            "必须按最新官方来源、项目 lockfile、本地依赖树、合同或专业确认结果复核",
        ],
    ),
)
check(
    "product source map preserves freshness boundary",
    has_all(
        product_source_map,
        [
            "不把读取日期当成当前核验日期",
            "不代表来源仍然最新可用",
            "外部知识时效性门禁",
            "来源、版本或发布日期",
            "核验日期",
            "确认方",
            "金融、合规、监管、云产品、SDK/API、外部服务、卡组织、ACH、银行、通道、税务或会计准则",
            "必须按最新公开来源、官方规则、项目 lockfile、本地依赖树、合同或专业确认结果复核",
        ],
    ),
)
check(
    "senior knowledge graph stays navigational",
    has_all(
        knowledge_graph,
        [
            "本文是知识域定位器，不是百科全书",
            "本文只保留导航和归档规则",
            "不沉淀专题长知识",
            "新增条目必须能指向一个权威 reference",
        ],
    ),
)
check(
    "source evidence archive stays private and offline",
    has_all(
        source_archive,
        [
            "Archive externally read source evidence outside this repository",
            "intentionally offline",
            "never fetches URLs",
            "uploads files",
            "reads secrets",
            "modifies repository content",
            "SKILL_SOURCE_ARCHIVE_HOME",
            "~/.skill-source-archive/",
            "raw evidence must not be stored inside this repository",
            "archive home must be outside this repository",
            "repo stores only source metadata; raw evidence stays outside git",
            "evidence_sha256",
            "--self-test",
            "OK source evidence archive self-test",
        ],
    )
    and has_all(
        "scripts/validate.sh",
        [
            "python3 -m py_compile scripts/archive-source-evidence.py",
            "==> source evidence archive",
            "scripts/archive-source-evidence.py --self-test",
        ],
    )
    and has_all(
        "scripts/audit-skills.sh",
        [
            "scripts/archive-source-evidence\\.py:.*shutil\\.copy2",
        ],
    ),
)
check(
    "skill evaluator tracks structure metrics without replacing review",
    has_all(
        skill_evaluator,
        [
            "Evaluate local Codex skills with deterministic structure and prompt metrics",
            "offline and read-only",
            "does not grade domain truth",
            "metadata_trigger",
            "progressive_loading",
            "reference_quality",
            "deterministic_execution",
            "trigger_fixtures",
            "realistic_prompt_fixtures",
            "SKILL_EVAL_PROMPT_FIXTURE",
            "REQUIRED_PROMPT_DIMENSIONS",
            "prompt_fixture_stats",
            "score_prompt_fixtures",
            "Skill Eval source is not recorded as title/author/time/body read",
            "REFERENCE_FILE_SOFT_LIMIT",
            "REFERENCE_FILE_HARD_LIMIT",
            "REFERENCE_SECTION_SOFT_LIMIT",
            "REFERENCE_SECTION_HARD_LIMIT",
            "SENIOR_REFERENCE_TOTAL_SOFT_LIMIT",
            "SENIOR_REFERENCE_TOTAL_HARD_LIMIT",
            "TASK_INDEX_HEADING",
            "TASK_INDEX_COLUMNS",
            "CONTROLLED_REFERENCE_SEARCHABILITY_SCORE",
            "has_progressive_headers",
            "has_task_index",
            "reference_searchability_score",
            "large_reference_files",
            "largest_reference_lines",
            "large_reference_sections",
            "largest_reference_section_lines",
            "reference_files_with_task_indexes",
            "reference_searchability_score",
            "reference_files_over_soft_limit",
            "reference_files_over_hard_limit",
            "reference_sections_over_soft_limit",
            "reference_sections_over_hard_limit",
            "controlled_searchability_score",
            "reference section soft budget exceeded",
            "in_fenced_code",
            "does not force mechanical splitting",
            "more than one independent task entry in one reference",
            "a single section longer than 120 lines",
            "the same rule repeated across multiple references",
            "more than eight level-2 topics in one reference",
            "Overall skill score",
            "OK skill evaluation self-test",
        ],
    )
    and has_all(
        "scripts/validate.sh",
        [
            "python3 -m py_compile scripts/evaluate-skills.py",
            "python3 -m py_compile scripts/audit-skill-eval-fixtures.py",
            "==> Skill Eval prompt fixtures",
            "scripts/audit-skill-eval-fixtures.py --self-test",
            "==> skill evaluation",
            "scripts/evaluate-skills.py --self-test",
        ],
    ),
)
check(
    "skill quality advisory audit reports metadata and body smells without blocking",
    has_all(
        skill_quality_audit,
        [
            "Report advisory quality signals for local Codex skills",
            "offline and read-only",
            "does not fail validation by default",
            "DESCRIPTION_WARN_CHARS",
            "DESCRIPTION_INFO_CHARS",
            "BODY_WARN_LINES",
            "BODY_HARD_HINT_LINES",
            "list separators",
            "capability-list bloat",
            "--strict",
            "OK skill quality audit self-test",
        ],
    )
    and has_all(
        "scripts/validate.sh",
        [
            "python3 -m py_compile scripts/audit-skill-quality.py",
            "==> skill quality advisory",
            "scripts/audit-skill-quality.py",
            "scripts/audit-skill-quality.py --self-test",
        ],
    ),
)
check(
    "Skill Eval methodology and prompt fixtures are grounded and offline",
    has_all(
        skill_eval_methodology,
        [
            "# Skill Eval 方法论",
            "## 使用时机",
            "## 不适用场景",
            "## 读取后必须产出",
            "## 需要继续读取的 reference",
            "## 按任务读取索引",
            "触发准确率",
            "输出质量",
            "效率指标",
            "对照实验",
            "方差检查",
            "Prompt 矩阵规则",
            "每个 Skill 至少有两个应该触发的真实请求",
            "每个 Skill 至少有两个不应该触发的难负例",
            "每个 Skill 至少有一个正例不直接点名 Skill",
            "https://mp.weixin.qq.com/s/JWz6EscFlcDeHhTjsDybgg",
            "2026-05-28",
            "已通过浏览器自动化读取标题、账号、作者、发布时间和正文",
            "不复制文章原文、示例代码、投资策略样例或社群引导内容",
        ],
    )
    and has_all(
        skill_eval_fixture_audit,
        [
            "Audit Skill Eval prompt fixtures",
            "offline and read-only",
            "does not run agents",
            "call networks",
            "REQUIRED_DIMENSIONS",
            "title_author_time_body_read",
            "needs at least 2 positive cases",
            "needs at least 2 hard negatives",
            "positive case without explicit skill name",
            "toy prompt",
            "appears to contain sensitive data",
            "OK skill eval fixture self-test",
        ],
    )
    and has_all(
        skill_eval_prompt_fixture,
        [
            "\"evaluation_dimensions\"",
            "\"trigger_accuracy\"",
            "\"output_quality\"",
            "\"efficiency_metrics\"",
            "\"baseline_comparison\"",
            "\"variance_check\"",
            "\"read_status\": \"title_author_time_body_read\"",
            "\"should_trigger\": true",
            "\"should_trigger\": false",
            "\"hard_negative\": true",
            "\"preferred_skill\"",
            "\"negative_reason\"",
        ],
    )
    and has_all(
        "README.md",
        [
            "如何评估你写的 SKILL.md 质量？一套完整的 Eval 方法论",
            "触发准确率、输出质量、效率指标、真实 prompt、难负例、对照实验和方差检查",
            "2026-05-28 已通过浏览器自动化读取标题、账号、作者、发布时间和正文",
            "不复制文章原文、策略案例、社群引导或未逐篇读取的外部链接",
        ],
    ),
)
check(
    "senior diagram reference keeps delivery and safety boundaries",
    has_all(
        senior_diagram,
        [
            "图是工程判断的表达面，不是架构本身",
            "## 卓越图形能力要求",
            "## AI 辅助可编辑图治理",
            "图形目标、目标读者、视图层级、输入材料、范围边界、节点/分组、箭头语义、风险节点、输出格式和验收标准",
            "业务上下文、容器/应用、组件、运行时交互、部署拓扑、数据/消息和观测支撑",
            "SVG、draw.io XML、Mermaid 或生成脚本",
            "数据边界、凭据边界、联网行为和写入范围",
            "## 技术架构图三级视图",
            "整体技术架构图",
            "子领域技术架构图",
            "应用粒度技术架构图",
            "## 从业务到技术的六步推导",
            "从业务架构推演技术骨架",
            "从用例和验收场景推导非功能模块",
            "## 视觉风格路由",
            "## 语义形状和箭头",
            "布局语义保持稳定",
            "## 稳定提示配方",
            "## 常见反模式",
            "组件堆叠图",
            "粒度混乱",
            "默认使用 SVG 作为正式图形化交付物",
            "Mermaid/Markdown 草图",
            "正式图形化交付默认只生成 SVG",
            "PNG/PDF/截图等其他格式",
            "PNG 不默认导出",
            "工程落点",
            "AI Agent Systems",
            "AI 辅助画图 / draw.io 可编辑图 / 文档转图",
            "AI 辅助可编辑图",
            "Architecture Diagram Generator 准入",
            "Architecture Diagram Generator 路由",
            "复杂分层架构图",
            "架构描述转可编辑图",
            "生成器输出只能作为可编辑草案",
            "不能写成架构质量结论、CR 通过、测试通过、Execution Grant 或上线审批",
            "微信公众号文章《如何画架构图：技术负责人带你画技术（系统）架构》",
            "第二篇《如何画架构图：业务架构的画法》当前链接只能访问校验页",
            "微信公众号文章《架构师必备--让AI画架构图》",
            "C4 Model、arc42 和 draw.io 官方文档",
            "`Architecture Diagram Generator` 可作为复杂架构图、代码库理解图和架构描述转图的候选生成后端",
            "未提供明确仓库、Skill 包或安装来源前，只能作为待审查工具名记录在路由中",
            "可选续作：fireworks-tech-graph",
            "调用 `$fireworks-tech-graph`",
            "供应链安全审查",
        ],
    ),
)
check(
    "product diagram reference keeps delivery and safety boundaries",
    has_all(
        product_diagram,
        [
            "图形化交付是产品表达的一部分",
            "## 卓越图形能力要求",
            "## 用户旅程与服务蓝图",
            "用户旅程图",
            "服务蓝图",
            "客户动作、前台触点、后台动作、支撑流程、证据/物料和系统依赖",
            "旅程图 + 服务蓝图 + 能力地图 + 状态机",
            "## AI 辅助可编辑图治理",
            "角色/主体混用、步骤缺失、异常路径遗漏、前后台混淆",
            "## 视觉风格路由",
            "## 语义形状和箭头",
            "## 稳定提示配方",
            "用户旅程",
            "服务蓝图",
            "AI 辅助可编辑图",
            "Architecture Diagram Generator 准入",
            "Architecture Diagram Generator 路由",
            "产品到系统的上下文图、容器/模块候选图或依赖边界图",
            "以下场景继续使用原有产品图形能力",
            "生成器输出不能替代产品判断、合规确认、工程设计或验收结论",
            "默认使用 SVG 作为正式图形化交付物",
            "Mermaid/Markdown 草图",
            "正式图形化交付默认只生成 SVG",
            "PNG/PDF/截图等其他格式",
            "PNG 不默认导出",
            "Finance Ledger",
            "支付资金四流",
            "`Architecture Diagram Generator` 可作为复杂架构图生成后端的候选能力",
            "未提供明确仓库、Skill 包或安装来源前，只能作为待审查工具名记录在路由中",
            "NN/g 的 UX mapping、journey mapping 和 service blueprinting 文章",
            "draw.io 官方文档",
            "可选续作：fireworks-tech-graph",
            "调用 `$fireworks-tech-graph`",
            "供应链安全审查",
        ],
    ),
)
check(
    "README keeps user guide anchors",
    has_all(
        "README.md",
        [
            "## 用户使用指南",
            "使用时不用先背 Skill 名称",
            "### 1. 一句话讲清目标",
            "我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>",
            "先帮我选路",
            "### 2. 按交付物选入口",
            "产品语义 / PRD / Backlog / 验收",
            "跨角色产研交付 / 目标拆解 / 任务计划 / Spec / Harness / 质量发布闭环",
            "默认进入角色协作 Loop",
            "按设计、设计评审、TDD、编码、编码评审、可用性/安全性评估、验证发布和复盘回流分角色推进",
            "系分 / 架构 / 代码 / Bug / 测试 / CR / 发布",
            "Java Service 脚手架",
            "复杂可编辑架构图、代码库结构转图或架构描述转图",
            "PNG 仅在明确要求时导出",
            "### 3. AI Native 只做编排",
            "默认先判断当前处于角色协作 Loop 的哪个阶段，再选最小场景视图",
            "只读理解视图",
            "产研交付视图",
            "验证发布视图",
            "知识回流视图",
            "### 4. 产品到工程的默认闭环",
            "产品发现",
            "编排准入",
            "角色协作",
            "工程执行",
            "质量理解门禁",
            "交付复盘",
            "### 5. 体用原则",
            "体：业务目标、用户/主体、生产边界、风险责任、验收标准和证据边界",
            "用：Skill、工具、模板、图、代码、测试、提交和发布动作",
            "体用合一",
            "避免体用混一",
            "阴阳互根",
            "执简驭繁",
            "### 6. 常用短句",
            "先帮我选路",
            "进入角色协作 Loop",
            "按目标和任务计划推进",
            "目标不等于执行授权",
            "进入自主交付闭环",
            "进入只读理解 Loop",
            "默认不写文件、不联网、不安装",
            "做质量门禁",
            "### 7. 最小输入清单",
            "`AI Native 研发流程编排`：当前材料成熟度",
            "`产品架构专家`：业务目标",
            "`资深架构师`：代码或文档路径",
            "`java-service-code-generator`：DDL/schema/Java 类/字段表格",
            "画图 / 工具准入",
            "### 8. 不要这样用",
            "只写一份普通 PRD、产品方案或 Backlog 决策",
            "只做系统设计、代码 CR、Bug、测试或生产变更",
            "从纯自然语言直接生成生产代码",
            "不要把工具、模板、目标、计划或授权机制名当主流程",
            "角色协作 Loop 的目标是交付生产可用能力",
            "内存版业务 Service",
            "## 完整能力索引",
            "日常使用优先看上面的快速指南",
            "路径：[ai-native-engineering-workflow](./ai-native-engineering-workflow)",
            "路径：[senior-software-architect](./senior-software-architect)",
            "路径：[product-architecture-expert](./product-architecture-expert)",
            "路径：[java-service-code-generator](./java-service-code-generator)",
            "原型/HTML/页面截图/交互稿反推 PRD",
            "正式图形默认 SVG",
            "需要精细视觉时再调用 `$fireworks-tech-graph`",
            "## 5 分钟上手",
            "sync-skills.sh --dry-run all",
            "./scripts/validate.sh",
            "从 AI 原型到工程化",
            "产品专家补产品上下文包、Backlog 和 PRD-Lite",
            "架构师补 OpenSpec、Harness、测试策略、TDD、源码级 CR 和发布风险",
            "### 常见组合",
            "从想法到工程",
            "从普通图到复杂图",
            "复杂可编辑架构图、代码库结构转图或多层架构图",
            "### 提示词公式",
            "用 <Skill 名称> + <任务类型> + <输入材料> + <目标产物> + <边界/风险> + <验证要求>",
            "### 最佳实践",
            "不要把 AI 原生工具的产品宣传或历史文章能力描述当作当前会话可用工具、执行授权、合规结论或生产审批",
            "## 维护者与高级扩展",
        ],
    ),
)
check(
    "README records Superpowers skills library source",
    has_all(
        "README.md",
        [
            "obra/superpowers",
            "外部 skills library",
            "brainstorming、writing-plans、executing-plans、subagent-driven-development、test-driven-development",
            "2026-06-07",
            "6fd4507659784c351abbd2bc264c7162cfd386dc",
            "ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3",
            "MIT",
            "ai-native-engineering-workflow/references/external-superpowers/",
            "superpowers-skill-library.md",
            "不复制或运行外部脚本、hooks、插件 manifest、package 脚本",
            "不把外部默认文档路径、自动提交、Git 推送、worktree、subagent 连续执行要求写成本仓库默认行为",
        ],
    ),
)
check(
    "README records intent to production loop engineering source",
    has_all(
        "README.md",
        [
            "Loop Engineering：让 AI 自己跑起来，你只管验收",
            "https://mp.weixin.qq.com/s/Ng_qit1H5t6yhqjVGNIHzg",
            "意图到生产交付角色 Loop",
            "Automations、Worktrees、Skills、Connectors、Sub-agents、State",
            "作者/账号字段为 `算法屋`",
            "不把 `/goal`、定时器、连接器、自动开 PR、sub-agent、worktree 或任何工具能力写成当前会话默认可用",
        ],
    ),
)
check(
    "README records huaxia wisdom source boundary",
    has_all(
        "README.md",
        [
            "aiami/huaxia-wisdom",
            "Loop 取舍校准 / Wisdom Lens",
            "Loop 准入、GSD 拆解、执行核验、授权纠偏和复盘回流",
            "2026-06-16",
            "eef49d54e6266b1afc568ef591a6a2d4abd5ad8e",
            "不复制原文、示例、口吻或经典表达",
            "不把传统智慧框架写成事实证据、项目制度、Execution Grant、测试通过、CR 结论、Git 授权或上线审批",
        ],
    ),
)
check(
    "README records Anthropic internal skills practice source",
    has_all(
        "README.md",
        [
            "重磅！Anthropic内部Skills经验公开了！",
            "仓库级 Skill 治理",
            "Skill 类型接入门禁、渐进式加载、gotchas 优先、验证优先、脚本化复用、setup 缺口、组合边界和高风险 guardrail",
            "Datawhale",
            "Anthropic团队",
            "2026-06-07 22:03:28 Asia/Shanghai",
            "2026-06-11 通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者、发布时间和正文",
            "不复制原文、图片、内部案例细节、Claude Code 专用变量、hooks、marketplace、usage measurement 机制或作者表达",
            "不把 Anthropic 内部做法写成 Codex 当前能力、组织制度、执行授权、默认持久化记忆或默认外部插件机制",
        ],
    ),
)
check(
    "README records AI product postmortem source boundary",
    has_all(
        "README.md",
        [
            "阿里内网万言离职书〈置身钉内〉原文，已刷屏",
            "公开转述/OCR 复盘参考来源",
            "AI 产品发心与定位",
            "AI 产品工程化准入卡",
            "AI 进入旧系统的 context 架构、权限与权力边界、技术债、多端一致性、成本稳定性和灰度止损门禁",
            "Codex in-app Browser 的 Playwright 接口",
            "页面正文声明内容由 AI 识图整理",
            "不把它写成钉钉/ONE 官方事实、行业结论、当前工具能力或 Execution Grant",
        ],
    ),
)
check(
    "README records AI full-stack workflow article boundary",
    has_all(
        "README.md",
        [
            "从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战",
            "AI Native 研发流程编排",
            "产品架构专家",
            "资深架构师",
            "模糊需求到结构化需求文档、业务流、原型/页面说明、开发任务和验收发布路径",
            "移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文",
            "不把示例项目写成通用模板、当前工程事实或执行授权",
        ],
    ),
)
check(
    "README records fireworks tech graph reference source",
    has_all(
        "README.md",
        [
            "yizhiyanhua-ai/fireworks-tech-graph",
            "图形化 Skill 产品化、风格系统、语义形状/箭头、模板化、fixture 化、SVG 导出和渲染校验思路",
            "PNG/PDF/截图等派生格式只在使用者明确提出时处理",
            "供应链安全审查",
        ],
    ),
)
check(
    "README records Google engineering practices reference source",
    has_all(
        "README.md",
        [
            "google/eng-practices",
            "代码评审标准、评论分级、变更颗粒度、作者/评审者协作和持续改善代码健康",
            "不把它扩展为完整架构设计方法论",
            "CC-BY 3.0 归因要求",
        ],
    ),
)
check(
    "README records Ivy skills reference source",
    has_all(
        "README.md",
        [
            "Ivy-piger/Ivy-skills",
            "陌生代码库侦察",
            "Java 架构坏味启发式扫描",
            "生产故障时间线",
            "5-Why 复盘草稿",
            "Spring Boot 安全检查清单",
            "不安装或复制 Claude Code 专用 frontmatter",
            "供应链安全审查",
        ],
    ),
)
check(
    "README records cg0x frame analysis reference source",
    has_all(
        "README.md",
        [
            "cg0x-skills/cg0x-frame-analysis",
            "探索期反路径锁定、多框架分析、假设/盲区/失败条件自检",
            "不引入 `alwaysApply`、`/on` `/off` 开关",
            "复杂问题先展开问题地图",
            "正式交付仍必须回到可评审、可验证、可验收的产物",
        ],
    ),
)
check(
    "README records SkillX reference source",
    has_all(
        "README.md",
        [
            "zjunlp/SkillX",
            "SkillX: Automatically Constructing Skill Knowledge Bases for Agents",
            "规划技能、功能技能、原子技能",
            "经验分层、过滤噪音、合并重复、工具约束和失败模式进入确定性验证",
            "不引入自动读取历史轨迹、自动学习用户数据、外部训练流水线或未审查代码",
        ],
    ),
)
check(
    "README records architecture principles WeChat source",
    has_all(
        "README.md",
        [
            "架构8：架构设计三原则",
            "https://mp.weixin.qq.com/s/wc3xeSbBqb6ktEDz2ZuK7g",
            "合适、简单、演化三类架构评审原则",
            "当前约束匹配、结构/逻辑复杂度评估和演进式设计门禁",
            "不复制文章案例、代码示例、图片或作者表达",
        ],
    ),
)
check(
    "README records architect thinking WeChat source",
    has_all(
        "README.md",
        [
            "架构师底层思维能力要求-这7种尽早练习",
            "https://mp.weixin.qq.com/s/Veb3P2ug8XVmyBFmIoDJ7Q",
            "抽象、逻辑、结构化、批判、成长型、复盘和数据思维",
            "底层思维能力框架、架构判断落点和常见误区",
            "不复制原文图片、推荐书目、排版结构或作者表达",
        ],
    ),
)
check(
    "README records communication complexity WeChat source",
    has_all(
        "README.md",
        [
            "软件复杂性的本质是通信复杂性",
            "https://mp.weixin.qq.com/s/1MbijKDxD2B4wa1E9QTnAw",
            "通信复杂度、节点/边/状态传播、抽象隐藏边、复杂度转移检查，以及业务驱动架构/TDD 桥接",
            "架构评审、业务验证、测试资产和图形检查项",
            "不复制原文、SVG 插图、产品对比或作者表达",
            "不把通信复杂度绝对化为唯一复杂度来源",
        ],
    ),
)
check(
    "README records software design philosophy source",
    has_all(
        "README.md",
        [
            "《软件设计的哲学》：复杂性的本质与模块化设计",
            "https://mp.weixin.qq.com/s/gXhOwvKH5t6BxsxcoqUS2w",
            "《软件设计的哲学》：实践智慧与超越代码的哲学",
            "https://mp.weixin.qq.com/s/J9d5Ws6rIdsATPbT-UutAA",
            "复杂性治理、深模块/浅模块、信息隐藏、设计两次、错误处理聚合、注释命名意图表达、AI 战术化编码风险和 TDD 后设计质量回看",
            "南山斯帕克",
            "深安斯帕克",
            "2026-06-22 10:38:07",
            "2026-06-23 07:47:00",
            "移动端微信 UA `curl` 公开 HTML 读取标题、作者、账号、发布时间和正文",
            "不把读书笔记写成官方标准、执行授权、测试通过、CR 结论或 AI 自动扩大范围的理由",
        ],
    ),
)
check(
    "README records AI diagram and UX mapping sources",
    has_all(
        "README.md",
        [
            "架构师必备--让AI画架构图",
            "https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg",
            "AI 辅助可编辑画图、文档转图、draw.io XML、版本历史和本地模型/凭据边界",
            "图形 brief、可编辑源文件、人工校验、权限和敏感信息边界",
            "NN/g UX Mapping Methods",
            "https://www.nngroup.com/articles/ux-mapping-cheat-sheet/",
            "NN/g Service Blueprints",
            "https://www.nngroup.com/articles/service-blueprints-definition/",
            "draw.io GitHub integration",
            "https://www.drawio.com/docs/integrations/github/",
            "用户旅程、服务蓝图、体验地图、可编辑图资产和仓库化维护",
            "不复制 NN/g 表格/图示/课程材料、draw.io 集成步骤或品牌表达",
        ],
    ),
)
check(
    "README records requirements analysis and design source",
    has_all(
        "README.md",
        [
            "需求分析和设计活动关键要点总结",
            "https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q",
            "功能定义、功能分配追溯、需求分析外部视角和设计内部视角分工",
            "功能不是头脑风暴清单",
            "功能来自上层对象分配",
            "正逆追溯",
            "不复制原文推荐书目、GJB 章节表述、课程/书籍引导或作者表达",
        ],
    ),
)
check(
    "README records AI-shaped readiness advisor boundary",
    has_all(
        "README.md",
        [
            "现在我敢评测这个 skill 了，产品负责人来看看这个自评卡吧",
            "https://mp.weixin.qq.com/s/ZUwtGYYTzt-c2YRXn8ryJw",
            "deanpeters/Product-Manager-Skills",
            "ai-shaped-readiness-advisor",
            "AI 产品工作成熟度",
            "AI-first 与 AI-shaped 区分",
            "上下文结构化、工作流编排、学习周期、人工责任和差异化指标",
            "不安装外部 Skill",
            "不复制交互协议、评分 rubrics、示例案例、图片、自评卡排版或作者表达",
        ],
    ),
)
check(
    "README records product manager methodology book boundary",
    has_all(
        "README.md",
        [
            "产品经理方法论",
            "赵丹阳",
            "https://m.dushu.com/book/13884861/",
            "文档分型、流程图、原型图、产品架构图、用户研究、需求管理、数据分析、技术协作、项目管理、行业/商业分析和知识库沉淀",
            "不复制书籍正文、章节内容、示例、图表或作者表达",
            "不把基础岗位知识体系替代复杂业务产品架构专家能力",
        ],
    ),
)
check(
    "README records business-driven architecture reference sources",
    has_all(
        "README.md",
        [
            "SEI ATAM",
            "Microsoft Azure Domain Analysis",
            "AWS Well-Architected REL03-BP02",
            "Dan North: Introducing BDD",
            "Impact Mapping",
            "NASA SWE-052 Bidirectional Traceability",
            "arc42",
            "C4 Model",
            "Atlassian PRD guide",
            "ISO/IEC 25010 质量模型摘要",
            "业务目标、业务域/限界上下文、质量属性场景、行为验收和产品到架构追踪",
            "需求到设计到验证的追踪、架构视图、质量属性和 PRD 假设/发布验证",
            "Use-Case 2.0 官方站点本轮受 Cloudflare 阻断，未作为已吸收来源",
            "不复制外部模板、图示、示例或品牌化流程",
        ],
    ),
)
check(
    "README routes SkillX export specification",
    has_all(
        "README.md",
        [
            "### SkillX 导出规范",
            "SkillX 到 Codex Skill Package 导出规范",
            "输入契约、安全门禁、三层映射、生成流程和验证流程",
            "不自动读取历史轨迹、不采集用户数据、不引入外部训练流水线",
            "schemas/skillx-candidate.schema.json",
            "scripts/skillx_export_adapter.py",
            "fixtures/skillx/sample-candidate.json",
            "REVIEW.md",
            "fixtures/trigger-prompts.md",
            "--check-input",
            "--validate-output",
        ],
    ),
)
check(
    "SkillX export spec defines package governance",
    has_all(
        skillx_export_spec,
        [
            "# SkillX 到 Codex Skill Package 导出规范",
            "## 使用时机",
            "## 不适用场景",
            "## 读取后必须产出",
            "## 需要继续读取的 reference",
            "## 按任务读取索引",
            "## 输入契约",
            "Planning Skills -> 路由与计划",
            "Functional Skills -> Reference 方法",
            "Atomic Skills -> 脚本、fixture 与工具约束",
            "## 安全门禁",
            "## 质量门禁",
            "## 验证流程",
            "## Adapter 第一版范围",
            "schemas/skillx-candidate.schema.json",
            "scripts/skillx_export_adapter.py",
            "fixtures/skillx/sample-candidate.json",
            "人工审查后的 SkillX JSON",
            "REVIEW.md",
            "fixtures/trigger-prompts.md",
            "--check-input",
            "--validate-output",
            "用户历史对话、私人目录、密钥、token、客户数据、内部合同、生产配置、生产日志或不可公开组织信息",
            "第一版 adapter 只做离线转换",
        ],
    ),
)
check(
    "SkillX export adapter stays offline and guarded",
    has_all(
        skillx_export_adapter,
        [
            "Offline adapter from reviewed SkillX candidate JSON to a Codex Skill package",
            "Network: never",
            "SCHEMA = ROOT / \"schemas\" / \"skillx-candidate.schema.json\"",
            "OFFLINE_ONLY = \"第一版 adapter 只做离线转换\"",
            "validate_candidate_schema(data)",
            "validate_trigger_fixture",
            "validate_generated_output",
            "candidate_input_report",
            "render_review_md",
            "usability_summary",
            "safety.{field} must be false for offline conversion",
            "source.reviewer must identify a completed human review",
            "sensitive or private-looking content rejected",
            "requires_network",
            "--dry-run",
            "--check-input",
            "--validate-output",
            "--self-test",
        ],
    ),
)
check(
    "SkillX export schema defines strict reviewed input",
    has_all(
        skillx_export_schema,
        [
            "\"title\": \"SkillX Candidate Package\"",
            "\"additionalProperties\": false",
            "\"skill_id\"",
            "\"planning_skills\"",
            "\"functional_skills\"",
            "\"atomic_skills\"",
            "\"safety\"",
            "\"contains_private_data\"",
            "\"requires_network\"",
            "\"textOrTextList\"",
        ],
    ),
)
check(
    "SkillX export fixture is public safe and complete",
    has_all(
        skillx_export_fixture,
        [
            "\"skill_id\": \"skillx-product-reviewer\"",
            "\"reviewer\": \"repo-maintainer\"",
            "\"contains_private_data\": false",
            "\"contains_external_code\": false",
            "\"requires_network\": false",
            "\"requires_user_consent\": false",
            "只能读取用户显式提供的本地 Markdown 或 JSON",
        ],
    ),
)
check(
    "validate script runs SkillX export adapter self-test",
    has_all(
        "scripts/validate.sh",
        [
            "python3 -m py_compile scripts/skillx_export_adapter.py",
            "python3 scripts/skillx_export_adapter.py --self-test",
        ],
    ),
)
check(
    "AGENTS defines skill experience layering",
    has_all(
        agents_rules,
        [
            "Skill 经验抽象可按三类归位",
            "规划层经验：任务识别、触发路由、阶段顺序、依赖关系、分支门禁和停止条件",
            "功能层经验：可复用子任务流程、模板、评审清单、输出结构、领域方法论和组合模式",
            "原子层经验：工具调用约束、脚本参数、输入输出 schema、常见失败模式、负例、fixture 和确定性校验",
            "过滤一次性探索、回退、试错、临时偏好和未验证结论",
        ],
    ),
)
check(
    "AGENTS defines skill type admission gate",
    has_all(
        agents_rules,
        [
            "## Skill 类型与接入门禁",
            "Skill 不是提示词大杂烩，而是围绕任务组织的可复用材料包",
            "library / API reference",
            "product verification",
            "data fetching and analysis",
            "business process and team automation",
            "code scaffolding and templates",
            "code quality and review",
            "CI/CD and deployment",
            "runbooks",
            "infrastructure operations",
            "只保留一个主类型",
            "`description` 面向模型触发",
            "`SKILL.md` 做目录和路标",
            "gotchas",
            "验证类能力优先级最高",
            "程序化断言",
            "setup 要提前想清楚",
            "记忆、日志、hooks 和使用度量只能在用户授权、仓库规则和供应链安全边界内使用",
            "高风险操作类 Skill 必须先通知、再确认、再执行",
        ],
    ),
)
check(
    "AGENTS requires Playwright fallback for unreadable external articles",
    has_all(
        agents_rules,
        [
            "## 外部文章读取约规",
            "必须以实际读取到的正文为依据",
            "常规抓取、网页搜索或 `curl` 无法取得正文",
            "必须改用 Playwright 或等价浏览器自动化加载页面",
            "不得把未读取到正文的文章写成已吸收结论",
        ],
    ),
)
check(
    "AGENTS defines private source evidence archive boundary",
    has_all(
        agents_rules,
        [
            "## 外部文章本地证据归档约规",
            "本仓库只保存公开索引、读取日期、读取状态、结构化提炼、核验边界、`archive_id` 和 `evidence_sha256` 等轻量 metadata",
            "不得提交文章全文、原图、截图包、MHTML、PDF、付费内容或大段摘录",
            "默认 `~/.skill-source-archive/`",
            "SKILL_SOURCE_ARCHIVE_HOME",
            "归档脚本只处理已经通过浏览器、Playwright 或人工方式取得的本地证据文件",
            "不默认联网、不上传、不读取密钥、不扫描用户私有目录",
        ],
    ),
)
check(
    "senior source map records Google eng-practices application",
    has_all(
        senior_source_map,
        [
            "# 架构师公开来源与应用记录",
            "google/eng-practices",
            "读取日期：2026-05-27",
            "CC-BY 3.0",
            "已读取文件",
            "应用记录",
            "coding-review-deep-dive.md",
            "workflow.md",
            "production-readiness.md",
            "scripts/validate-trigger-paths.py",
            "不把 `google/eng-practices` 扩展为完整架构设计",
        ],
    )
    and contains(senior_skill, "references/source-map.md"),
)
check(
    "senior records business-driven architecture verification sources",
    has_all(
        senior_source_map,
        [
            "业务驱动架构与验证公开来源组",
            "Architecture Tradeoff Analysis Method Collection",
            "https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis",
            "https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_service_architecture_business_domains.html",
            "https://dannorth.net/blog/introducing-bdd/",
            "https://www.impactmapping.org/book.html",
            "具体产品侧交接矩阵以 `product-architecture-expert/references/source-map.md`",
            "https://swehb.nasa.gov/x/AwIfBg",
            "https://arc42.org/overview",
            "https://c4model.com/diagrams",
            "ISO/IEC 25010",
            "Use-Case 2.0",
            "Cloudflare 阻断页，未作为已吸收来源",
            "SEI `Quality Attribute Workshop` 旧直链返回 404，未作为已吸收来源",
            "未作为已吸收来源",
        ],
    ),
)
check(
    "senior records architecture principles WeChat source",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：架构设计三原则",
            "https://mp.weixin.qq.com/s/wc3xeSbBqb6ktEDz2ZuK7g",
            "架构8：架构设计三原则",
            "泛终端操作系统",
            "开心就好TF",
            "2026-05-18 18:06",
            "公开 HTML 读取标题、公众号、作者、发布时间和正文",
            "本机 Chrome headless",
            "合适、简单、演化",
            "当前人力、技术积累、业务规模、运行约束和验证成本",
            "结构复杂度、逻辑复杂度、故障面和排障成本",
            "当前最小稳定结构、复审触发条件和下一阶段路径",
            "不复制文章中的公司案例、比喻、可用性计算代码",
        ],
    ),
)
check(
    "senior records architect thinking WeChat source",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：架构师底层思维能力要求",
            "https://mp.weixin.qq.com/s/Veb3P2ug8XVmyBFmIoDJ7Q",
            "架构师底层思维能力要求-这7种尽早练习",
            "面汤放盐",
            "面汤放盐-uzong",
            "2026-04-10 14:42",
            "公开 HTML 读取标题、公众号、作者、发布时间和正文",
            "本机 Chrome headless",
            "抽象、逻辑、结构化、批判、成长型、复盘、数据",
            "架构设计、Review、诊断和生产风险判断",
            "不复制文章图片、排版结构、推荐书目",
            "本地协作学习授权边界",
        ],
    ),
)
check(
    "senior records communication complexity WeChat source",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：软件复杂性的本质是通信复杂性",
            "https://mp.weixin.qq.com/s/1MbijKDxD2B4wa1E9QTnAw",
            "高盛盛",
            "2026-03-30 19:31",
            "2026-05-29",
            "公开 HTML 读取标题、公众号、作者、发布时间和正文",
            "本机 Chrome headless",
            "通信复杂度视角",
            "节点、边、状态传播和可观测性",
            "技术选型通常转移复杂度而非消灭复杂度",
            "业务驱动架构、TDD 的桥接",
            "测试、观测和评审门禁用于证明关键边上的业务事实、状态传播和失败语义",
            "删除节点或边",
            "不把“通信复杂性”绝对化为软件复杂度的唯一来源",
        ],
    ),
)
check(
    "senior source map records software design philosophy notes",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：《软件设计的哲学》读书笔记组",
            "https://mp.weixin.qq.com/s/gXhOwvKH5t6BxsxcoqUS2w",
            "《软件设计的哲学》：复杂性的本质与模块化设计",
            "https://mp.weixin.qq.com/s/J9d5Ws6rIdsATPbT-UutAA",
            "《软件设计的哲学》：实践智慧与超越代码的哲学",
            "深安斯帕克",
            "南山斯帕克",
            "2026-06-22 10:38:07 Asia/Shanghai",
            "2026-06-23 07:47:00 Asia/Shanghai",
            "公开 HTML 读取标题、作者、账号、发布时间和正文",
            "深模块与信息隐藏原则",
            "复杂度可控、错误处理低层屏蔽 / 高层聚合",
            "复杂性投资检查",
            "复杂度投资门禁",
            "不把“定义错误不存在”解释为吞异常",
            "不把 TDD 反思写成反对测试",
        ],
    ),
)
check(
    "senior source map and README record Clean Architecture dependency rule source",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：Clean Architecture 整洁架构",
            "https://mp.weixin.qq.com/s/7zj5v-B_-fClCYyR3SnMLA",
            "Clean Architecture 整洁架构",
            "智氪AI",
            "2026-06-03 09:00:00 Asia/Shanghai",
            "公开 HTML 读取标题、账号、发布时间和正文",
            "层数可变、依赖方向不可逆",
            "端口倒置失败",
            "不启动数据库、Web 容器或真实 SDK",
            "不把 Clean Architecture 固化为必须四层",
            "不复制原文、图示、比喻、表格或作者表达",
            "不把文章中的示例技术栈、数据库、框架或外部工具写成项目默认选择",
        ],
    )
    and has_all(
        "README.md",
        [
            "Clean Architecture 整洁架构",
            "Clean Architecture 依赖规则、依赖反转、业务规则/用例规则分离和可测试性诊断",
            "源代码依赖方向、端口位置、adapter 边界和不启动数据库/Web 容器/真实 SDK 的核心业务测试诊断",
            "不复制原文、图示、比喻、表格或作者表达",
            "不把 Clean Architecture 固化为必须四层或固定目录模板",
        ],
    ),
)
check(
    "senior source map and README record DDD principles architecture tradeoff article group",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：DDD、开发原则与架构取舍组",
            "https://mp.weixin.qq.com/s/3A5SAp1Dzw8s3sECM2SNhQ",
            "用了 DDD 还是写不好业务代码？因为你把它当成了架构模式",
            "https://mp.weixin.qq.com/s/zJphqS80r3fg_wLXHaFmHQ",
            "7 条开发原则你都知道，但一条都用不对",
            "https://mp.weixin.qq.com/s/e1ft2s2Js8K0Zaw6PNfYMQ",
            "学了那么多软件架构，现实工作我们该怎么权衡",
            "公开 HTML 读取标题、账号、作者、发布时间和正文",
            "DDD 战略设计/战术设计",
            "原则冲突",
            "收益、代价、前置条件",
            "不复制原文、表格、代码示例、图示、参考资料列表或作者表达",
            "不把 DDD、Clean、微服务、CQRS、Event Sourcing、12-Factor 或 Reactive 写成默认架构套餐",
        ],
    )
    and has_all(
        "README.md",
        [
            "用了 DDD 还是写不好业务代码？因为你把它当成了架构模式",
            "7 条开发原则你都知道，但一条都用不对",
            "学了那么多软件架构，现实工作我们该怎么权衡",
            "DDD 战略/战术分层、开发原则判断框架和架构风格取舍框架",
            "通用语言、限界上下文、上下文映射、原则冲突判断、架构族收益/代价/前置条件和 CR 检查项",
            "不复制原文、表格、代码示例、参考资料列表、图示、标题传播话术或作者表达",
            "不把 DDD、Clean、微服务、CQRS、Event Sourcing、12-Factor 或 Reactive 写成默认架构套餐",
        ],
    ),
)
check(
    "senior architecture records DDD and architecture tradeoff framework",
    has_all(
        "senior-software-architect/references/architecture.md",
        [
            "### 5.10 架构风格取舍框架",
            "架构风格不是技术名词菜单，而是约束下的收益和代价选择",
            "它牺牲什么换取什么",
            "DDD / 领域架构族",
            "Clean / Hexagonal / Onion",
            "Microservices / SOA",
            "CQRS / Event Sourcing",
            "PACELC / BASE / FLP",
            "12-Factor / Reactive / 运行架构",
            "战略设计：通用语言、限界上下文、上下文映射和防腐层",
            "战术设计：聚合、实体、值对象、领域事件、领域服务、仓储和应用服务",
            "Repository 面向聚合根和领域集合",
            "ApplicationService 当业务规则容器",
            "领域语言是否能在代码、文档、测试和业务对话中一致出现",
            "是否说明它牺牲什么、换取什么，以及满足哪些前置条件",
        ],
    ),
)
check(
    "senior clean code and review turn principles into judgment frameworks",
    has_all(
        "senior-software-architect/references/clean-code.md",
        [
            "### 1.1 开发原则判断框架",
            "开发原则是提醒维度，不是自动结论",
            "两段代码是否表达同一业务知识",
            "KISS",
            "认知复杂度",
            "YAGNI",
            "提前设计接口边界",
            "POLA / 最小惊讶",
            "Boy Scout Rule",
            "Fail Fast",
            "SoC / 关注点分离",
            "DRY 与 KISS 冲突",
            "原则冲突时",
            "它是否为了 DRY 抽象掉了不同业务知识，或为了 YAGNI 拒绝了必要的接口边界",
        ],
    )
    and has_all(
        review,
        [
            "原则和 DDD 误用扫描",
            "再看领域语言",
            "DDD 战略缺失",
            "Repository 退化 DAO",
            "原则误用",
            "架构风格误用",
            "## 原则误用 CR 提示",
            "原则名不是问题证据",
            "这里违反 DRY。",
            "这里用了 DDD 但不像 DDD。",
            "这里应该上微服务/CQRS/Event Sourcing。",
        ],
    ),
)
check(
    "senior clean code deepens Clean Architecture dependency rule",
    has_all(
        "senior-software-architect/references/clean-code.md",
        [
            "### 2.1 Clean Architecture 依赖规则诊断",
            "Clean Architecture 首先检查依赖方向，不首先检查层数",
            "层数可变，依赖方向不可逆",
            "内层定义端口，外层实现适配器",
            "Clean Architecture 的 Entities 是架构层概念，不等同于 DDD Entity",
            "SRP 在架构层对应变化原因隔离",
            "DIP 对应依赖规则和端口反转",
            "OCP 对应通过外层适配器或新增用例扩展",
            "如果业务规则或用例流程必须启动数据库、Web 容器或真实 SDK 才能测试，先怀疑依赖方向",
            "Clean Architecture 不是固定四层目录模板",
        ],
    ),
)
check(
    "senior review testing and module governance detect Clean Architecture dependency leaks",
    has_all(
        review,
        [
            "伪 Clean 分层",
            "端口倒置失败",
            "Clean Architecture 反向依赖",
            "将端口契约移到内层，外层 adapter 实现端口",
            "不启动 DB/Web/SDK 的核心业务测试",
        ],
    )
    and has_all(
        testing,
        [
            "Clean Architecture 核心业务与用例",
            "不启动数据库、Web 容器或真实 SDK",
            "Clean Architecture 诊断：如果业务规则或用例流程必须启动 DB/Web 才能测规则",
            "架构测试负责守住包依赖方向，领域/用例测试负责证明核心业务可以脱离外层细节独立运行",
        ],
    )
    and has_all(
        "senior-software-architect/references/project-governance-codebase-and-modules.md",
        [
            "Clean Architecture 在 Wind 模块中的落点是依赖规则，不是机械四层模板",
            "层数可变，依赖方向不可逆",
            "`core/biz` 定义 port 和业务契约，`infrastructure` 提供 adapter",
        ],
    )
    and has_all(
        "senior-software-architect/references/architecture.md",
        [
            "是否只画了分层图却没有约束源代码依赖方向、端口位置和外层 adapter 边界",
            "核心业务规则和用例流程能否脱离数据库、Web 容器、消息中间件和真实 SDK 被测试",
        ],
    ),
)
check(
    "senior records AI diagram and architecture diagram sources",
    has_all(
        senior_source_map,
        [
            "AI 辅助画图与架构图公开来源组",
            "架构师必备--让AI画架构图",
            "https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg",
            "方兴集",
            "2026-04-30 16:28:31",
            "AI + draw.io 的自然语言生成、文档转图、图像参考、版本历史、可编辑 draw.io XML 和本地模型/凭据边界",
            "C4 Model Diagrams",
            "https://c4model.com/diagrams",
            "System Context、Container、Component、Code、Dynamic、Deployment",
            "arc42 Template Overview",
            "https://arc42.org/overview",
            "Building Block View、Runtime View、Deployment View",
            "draw.io 官方 GitHub 集成文档",
            "https://www.drawio.com/docs/integrations/github/",
            "可编辑图文件和源码/文档同库维护",
            "不把 next-ai-draw-io、draw.io、Mermaid、SVG 或 `$fireworks-tech-graph` 的生成结果写成架构质量结论",
        ],
    ),
)
check(
    "senior records requirements analysis and design source",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：需求分析和设计活动关键要点总结",
            "https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q",
            "需求分析和设计活动关键要点总结",
            "软件需求分析和设计",
            "常识",
            "2026-05-26 10:29:23",
            "公开 HTML 读取标题、公众号、作者、发布时间和正文",
            "本机 Chrome headless",
            "功能不是头脑风暴功能点",
            "对象对外提供的可见、有价值交互行为",
            "正向分解和逆向追溯",
            "需求分析外部视角和设计内部视角",
            "不复制文章中的 GJB 章节表述、书籍推荐、课程机构推荐、作者自述或原文表达",
        ],
    ),
)
check(
    "senior architecture keeps fit simplicity evolution gates",
    has_all(
        "senior-software-architect/references/architecture.md",
        [
            "### 5.1.1 业务同质性和复制成本",
            "技术架构本质上是业务架构的支撑结构",
            "架构复用的前提是业务同质性",
            "不把技术平台当产品本身",
            "如果赚钱业务无法在该技术架构上运行",
            "### 5.1.2 合适优先",
            "人力失配",
            "积累失配",
            "场景失配",
            "结构复杂度来自更多组件、更多依赖、更多失败点和更长排障链路",
            "逻辑复杂度来自单个组件承担过多职责、状态流转和规则判断",
            "演进式设计优于一步到位",
            "复审触发条件",
            "当前人力、技术积累、业务规模、运行约束和验证成本",
            "行业领先搬运",
            "一步到位幻觉",
        ],
    ),
)
check(
    "senior architecture keeps communication complexity lens",
    has_all(
        "senior-software-architect/references/architecture.md",
        [
            "### 5.2.1 通信复杂度视角",
            "节点是服务、模块、函数、批任务、数据存储、Agent、工具或外部系统",
            "边是同步调用、异步事件、数据读写、配置依赖、状态传播、控制策略或观测链路",
            "技术选型通常不会消灭复杂度，只会改变复杂度的位置和可见性",
            "解耦是降低边密度",
            "抽象是把子图封装成复合节点",
            "治理是减少环路、跨层依赖和隐式状态传播",
            "删除节点或边",
            "业务目标、用例和验收示例是判断节点和边是否必要的依据",
            "TDD、监控和评审门禁是让关键边上的业务事实、状态传播和失败语义变成反馈的手段",
            "通信复杂度搬家",
            "隐藏边抽象",
        ],
    ),
)
check(
    "senior architecture keeps deep module information hiding lens",
    has_all(
        "senior-software-architect/references/architecture.md",
        [
            "### 5.3.2 深模块与信息隐藏",
            "深模块",
            "浅模块",
            "信息隐藏",
            "按任务职责分解",
            "设计两次",
            "多文件小改动信号",
            "长度不是坏味本身，复杂性才是",
            "减少直通包装",
            "模块是否像深模块一样用简单接口封装复杂性",
            "一个小需求是否出现多文件小改动、直通包装、重复协议知识、重复状态码或重复文件格式解析",
            "是否比较过至少两种可行设计",
        ],
    ),
)
check(
    "senior routes communication complexity through decisions and templates",
    has_all(
        senior_routing,
        [
            "关键节点/通信边",
            "复杂度从哪里转移到哪里",
            "隐藏边是否可观测、可追踪和可回滚",
            "新增节点、通信边、隐藏状态、观测入口和退出策略",
        ],
    )
    and has_all(
        adr_tradeoff,
        [
            "复杂度位置：新增、删除或隐藏了哪些节点和通信边",
            "复杂度是被删除、被暴露，还是转移到网络、配置、框架黑箱、隐式状态或运维排障",
            "服务间通信边清楚",
            "隐藏调用、上下文、状态传播或重试链路",
            "隐藏通信边、隐式状态传播或框架黑箱",
        ],
    )
    and has_all(
        "senior-software-architect/references/review-and-output-templates.md",
        [
            "通信复杂度：关键节点和通信边、同步/异步关系、状态传播、隐藏边、观测入口",
            "复杂度从哪里转移到哪里",
        ],
    ),
)
check(
    "senior AI collaboration exposes hidden communication edges",
    has_all(
        ai_engineering,
        [
            "隐藏通信边和后验修补倾向",
            "通信边界：关键调用、工具、上下文、状态传播、读写关系和观测入口",
            "是否隐藏关键通信边",
            "AI 生成的框架封装、工具调用、上下文传递、异步任务和重试链路必须可追踪、可观测、可复现",
        ],
    ),
)
check(
    "senior knowledge map and skill tree expose communication complexity",
    has_all(
        knowledge_graph,
        [
            "服务拆分、通信复杂度",
            "关键节点和通信边",
            "这个框架/SDK/Agent 编排会不会让系统更复杂",
            "复杂度从哪里转移到哪里，关键通信边和状态传播是否可观测",
        ],
    )
    and has_all(
        "senior-software-architect/references/skill-tree-architecture-design.md",
        [
            "通信复杂度显式化",
            "节点、边和状态传播的图",
            "解耦收益 vs 新增通信边和观测成本",
        ],
    ),
)
check(
    "senior diagram output keeps communication complexity graph checks",
    has_all(
        "senior-software-architect/references/diagram-output.md",
        [
            "### 通信复杂度图形检查",
            "架构图应暴露系统复杂度在哪些节点和边上",
            "边是否标明同步调用、异步事件、数据读写、状态传播、控制策略、补偿、降级或监控链路",
            "边过密、交叉过多、跨层连线过多或出现依赖环",
            "隐藏了关键调用、上下文、状态或失败路径",
            "上下文图、关键链路图、状态传播图或故障传播图",
        ],
    ),
)
check(
    "senior source map and README record GSD workflow boundary",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：GSD 工作流",
            "https://mp.weixin.qq.com/s/VA_GhniSSrcJotXWlgk_lw",
            "让AI编程从\"越写越烂\"到\"持续稳定输出\"：GSD工作流-适合中大型项目的精准框架。",
            "`ai-large-project-orchestration.md`",
            "类 GSD 的大项目编排工作流",
            "项目上下文账本、初始化流程、阶段拆分、原子任务包、Wave 依赖、GSD-CAD 双层协议",
            "不默认在项目中创建 `PROJECT.md`、`STATE.md`、`ROADMAP.md`、`CONTEXT.md`",
            "不把“子 Agent + Wave 并行”写成默认开发方式",
            "不把自动原子提交视为默认授权",
            "不把外部工具的命令、术语或自动化习惯凌驾于本仓库 `AGENTS.md`",
        ],
    )
    and has_all(
        "README.md",
        [
            "GSD工作流-适合中大型项目的精准框架",
            "中大型 AI 编码流程治理、上下文衰减、阶段状态、多 Agent 编排、Wave 依赖、原子可追溯和 Git 版本化意识",
            "不复制 GSD 命令体系、文件模板、XML 示例、动图、截图、工具宣传语或作者表达",
            "不把自动提交视为默认授权",
        ],
    ),
)
check(
    "senior source map and README record Codex runtime collaboration boundary",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：Codex 官方团队：如何把 Codex 用到极致",
            "https://mp.weixin.qq.com/s/6t8hu_XU48jC3T-fc_B5FQ",
            "Codex 官方团队：如何把 Codex 用到极致",
            "durable / pinned thread、voice / transcript、steering / queuing",
            "thread automation / scheduled automation、goal、side panel / artifact",
            "不把平台功能当成当前工具可用性或执行授权",
            "不作为 OpenAI 官方当前产品能力、模型、工具可用性或官方承诺依据",
            "必须核验 OpenAI 官方文档或当前会话工具状态",
            "不把该微信文章当作 OpenAI 官方当前能力、产品可用性、模型、工具或路线图承诺",
            "不默认创建 pinned thread、automation、goal、vault、外部 connector、长期 memory",
            "不把 voice/transcript、thread transcript、queue 或 automation 当作规格、授权、验证结果或 Git/部署许可",
        ],
    )
    and has_all(
        "README.md",
        [
            "Codex 官方团队：如何把 Codex 用到极致",
            "Codex 运行时协作、durable thread、voice/transcript、steering/queuing、tool reach、automation/goal、side panel/artifact 和 shared written context",
            "持续工作流治理、可验证 goal、显式上下文和权限边界",
            "不把平台功能当成默认工具可用性或执行授权",
            "涉及 Codex 当前产品能力、模型、工具可用性或官方承诺时，仍必须核验 OpenAI 官方文档或当前会话工具状态",
        ],
    ),
)
check(
    "senior source map and README record AI Native architect boundary",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：放下代码：AI Native是通往架构师的快车道",
            "https://mp.weixin.qq.com/s/fhEzrPbeez-_2bmJHqExCQ",
            "放下代码：AI Native是通往架构师的快车道",
            "2026-05-23 12:00:00",
            "AI Native 架构师工作面",
            "hardened 标准",
            "Agent 工作流设计",
            "Hardened Candidate",
            "不能直接作为 Execution Grant",
            "不把“放下代码”理解为放弃编码能力、代码审查、测试、验证或生产责任",
        ],
    )
    and has_all(
        "README.md",
        [
            "放下代码：AI Native是通往架构师的快车道",
            "AI Native 架构师角色升级、hardened 标准、Agent 工作流设计、系统判断和技术战略职责",
            "不复制原文、引用案例、播客转述、作者表达或岗位评价",
        ],
    ),
)
check(
    "senior source map and README record AI old-system postmortem boundary",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：置身钉内",
            "https://mp.weixin.qq.com/s/_D20O0vpPXjSzjAKJmBYuA",
            "阿里内网万言离职书《置身钉内》原文，已刷屏",
            "爬梯意外簿",
            "Corgi/滕雅辛",
            "Codex in-app Browser 的 Playwright 接口",
            "公开转述/OCR 复盘材料",
            "AI 进入旧系统的架构门禁",
            "context 架构、权限与权力边界、旧系统技术债、多端一致性、任务闭环、成本稳定性、可观测审计和演进切片",
            "AI 产品工程化准入卡",
            "AI 产品发心、定位和用户张力门禁",
            "不把公开转述/OCR 内容写成钉钉、ONE 或阿里官方事实",
            "不把单个企业协作产品复盘绝对化为所有 AI 产品或所有 SaaS 的通用结论",
        ],
    )
    and has_all(
        "README.md",
        [
            "阿里内网万言离职书〈置身钉内〉原文，已刷屏",
            "公开转述/OCR 复盘参考来源",
            "AI 进入旧系统的 context 架构、权限与权力边界、技术债、多端一致性、成本稳定性和灰度止损门禁",
            "不把它写成钉钉/ONE 官方事实、行业结论、当前工具能力或 Execution Grant",
        ],
    ),
)
check(
    "senior source map and README record AI full-stack workflow boundary",
    has_all(
        senior_source_map,
        [
            "微信公众号文章：从一份模糊需求，到一套可开发系统",
            "https://mp.weixin.qq.com/s/HzbdrmNkT-OTRKdQh0c0Ug",
            "从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战",
            "KEEN的创享",
            "Codex in-app Browser 的 Playwright 接口",
            "可开发系统工程化门禁",
            "目标/非目标、前后台和多端边界、业务流、对象状态、规则权限、数据安全、接口候选、测试验收和发布路径",
            "不把高保真原型、AI 生成页面或示例系统当成当前项目工程边界、OpenSpec、Harness Plan 或 Execution Grant",
        ],
    )
    and has_all(
        "README.md",
        [
            "从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战",
            "模糊需求到结构化需求文档、业务流、原型/页面说明、开发任务和验收发布路径",
            "不把示例项目写成通用模板、当前工程事实或执行授权",
        ],
    ),
)
check(
    "senior skill tree exposes AI context decay capability",
    has_all(
        "senior-software-architect/references/skill-tree-platform-leadership-ai.md",
        [
            "中大型 AI 编码、长任务上下文衰减、多 Agent/Wave 编排读 `ai-large-project-orchestration.md`",
            "长任务上下文衰减",
            "上下文账本",
            "子 Agent / Wave 并行",
            "研究、规划、执行和验证",
            "明确小修、一次性 demo 或快速 MVP 验证走轻量闭环",
            "外部工作流命令、状态文件命名或自动提交习惯",
        ],
    )
    and has_all(
        knowledge_graph,
        [
            "AI 协作、上下文衰减或 CAD Mode",
            "`ai-large-project-orchestration.md`",
            "OpenSpec、Harness、上下文账本、Wave 编排、CAD Mode",
            "AI 写到后面越来越乱 / 长任务上下文太重",
        ],
    )
    and contains("senior-software-architect/references/skill-tree.md", "上下文账本、阶段状态、Wave 编排、协作交接和验证闭环"),
)
check(
    "senior architecture keeps architect thinking model",
    has_all(
        "senior-software-architect/references/architecture.md",
        [
            "### 1.1 架构师底层思维",
            "抽象思维",
            "逻辑思维",
            "结构化思维",
            "批判思维",
            "成长型思维",
            "复盘思维",
            "数据思维",
            "Object",
            "Map",
            "String",
            "排除法、假设验证和反例检查",
            "质疑、验证、适配",
            "指标、日志、压测、用户行为、收益/成本和运行数据",
        ],
    ),
)
check(
    "senior system design preserves business-driven validation route",
    has_all(
        "senior-software-architect/references/system-analysis-design.md",
        [
            "PRD/产品方案到系分 / 业务驱动系统设计",
            "系分前需求分析门禁",
            "原始诉求和根源需求",
            "产品定义",
            "产品边界",
            "稳定点 / 变化点",
            "边界坐标",
            "系统边界、模块拆分、接口契约、数据模型和测试矩阵必须能回指产品定义、产品边界、稳定点 / 变化点或业务不变量",
            "扩展点、抽象层、规则引擎、平台化、缓存、MQ 或微服务拆分",
            "真实变化轴、owner 和验收方式",
            "过度设计风险",
            "业务驱动追踪表",
            "质量属性场景",
            "业务 driver",
            "系统边界、模块、接口、数据、质量属性和测试",
        ],
    ),
)
check(
    "senior standards gate protects requirements design coding and testing",
    has_all(
        "senior-software-architect/references/system-analysis-design.md",
        [
            "若系统需求、产品需求或外部规则未确认，不进入详细设计、编码或测试设计",
            "需求条目应表达外部可见行为",
            "衍生需求、异常恢复、安全监控、状态异常处理和鲁棒性要求必须标明来源、owner、验收方式和是否回写上游",
            "高层 / 详细设计分工",
            "高层设计说明系统对外做什么、边界和分配关系是什么",
            "详细设计说明内部如何实现",
        ],
    )
    and has_all(
        coding,
        [
            "规则写法要求",
            "每条强制 / 推荐规则必须说明原因、适用范围、反例或示例、验证方式",
            "防御式编程规则覆盖输入校验、边界检查、类型转换、金额/精度、除零、异常传播、故障隔离和统一错误处理",
            "避免无上限递归、无界循环、共享全局状态、不可控随机/时间和有副作用表达式",
            "最小正确",
            "编码前执行最小正确实现门禁",
            "已有实现可复用、标准库/平台原生/已安装依赖可覆盖",
            "单实现接口、单调用工厂",
            "不得以“少写代码”为理由删除输入校验、错误处理、防御式编程、安全/权限/资金兜底",
            "复杂度可控",
            "错误处理优先低层屏蔽",
            "定义错误不存在",
            "变量、方法、类和测试命名以阅读者能否理解为准",
            "## 19. 设计质量回看",
            "接口是否照顾 90% 常用场景",
            "测试是否保护设计",
        ],
    )
    and has_all(
        testing,
        [
            "需求驱动测试门禁",
            "系统/产品需求未确认、需求条目不可验证、图文不可追踪或衍生需求无 owner",
            "不直接设计测试或用测试替代需求确认",
            "鲁棒性、异常恢复、安全监控、越界输入、状态异常和失败处理测试必须回链需求、AC、质量属性或已确认风险",
            "测试发现需求缺失、矛盾或不可测时，先回写 PRD / OpenSpec / 系分或待确认项",
        ],
    ),
)
check(
    "senior review keeps minimal implementation and over-engineering pass",
    has_all(
        review,
        [
            "过度设计专项 CR",
            "最小正确实现 / 过度设计专项 CR",
            "不替代正确性、安全、性能和业务语义 Review",
            "是否无需新增、是否已有 helper / type / pattern 可复用",
            "JDK / Spring / 数据库 / 平台原生能力是否覆盖",
            "单实现接口、单调用工厂、没人设置的配置项",
            "输出每条建议时保持四要素：位置、可删内容、替代方案、不可删边界",
            "替代方案优先级为：不做、复用仓库已有能力、标准库、平台原生能力、已安装依赖、最小显式实现",
            "不得把过度设计专项 CR 当成正确性、安全、性能或发布准出结论",
            "复杂性和模块边界 Review",
            "追加复杂性投资检查",
            "浅模块堆叠",
            "直通包装",
            "信息泄露",
            "多文件小改动",
            "战术 AI 代码",
            "浅模块 / Classitis",
        ],
    ),
)
check(
    "senior product semantics preserves demand analysis collaboration gate",
    has_all(
        "senior-software-architect/references/product-design.md",
        [
            "架构师不能只被动接收二手 PRD",
            "应参与需求澄清",
            "用户原始诉求和根源需求是否分清",
            "功能名、页面控件或 AI 原型不能直接推导模块、表、缓存、MQ 或微服务",
            "产品定义要说明对象、能力、可见价值行为和成功口径",
            "产品边界、稳定点 / 变化点",
            "本产品负责、合作方负责、外部系统负责、人工/运营承接和本期不做",
            "稳定点 / 变化点必须带边界坐标",
            "没有真实变化轴、owner 和验收方式的扩展点按过度设计风险处理",
        ],
    ),
)
check(
    "senior system design preserves functional allocation boundary",
    has_all(
        "senior-software-architect/references/system-analysis-design.md",
        [
            "功能分配关系",
            "功能不是头脑风暴得到的功能点",
            "对象对外提供的可见、有价值交互行为",
            "下层系统、模块或 CSCI 的功能应来自上层对象目标和功能分解",
            "正向分解和逆向追溯",
            "需求分析与设计分工",
            "需求分析站在对象外部",
            "设计站在对象内部",
            "功能是否能追溯到上层目标或父对象功能分配",
            "在需求分析阶段过早展开内部结构",
        ],
    ),
)
check(
    "senior architecture template includes business-driven trace and quality scenarios",
    has_all(
        "senior-software-architect/references/review-and-output-templates.md",
        [
            "业务驱动追踪：业务目标、参与方、核心行为、对象规则和验收示例",
            "质量属性场景：业务 driver、触发条件、受影响资产、期望响应、度量验收和取舍",
            "业务驱动 TDD 映射",
        ],
    ),
)
check(
    "senior bridges communication complexity with business-driven TDD",
    has_all(
        "senior-software-architect/references/product-design.md",
        [
            "业务驱动架构与通信复杂度视角是同一件事的两面",
            "产品语义决定哪些节点、通信边、状态传播和观测链路必须存在",
            "验收示例决定这些边上哪些业务事实需要被证明",
            "节点、通信边和状态传播",
            "先决定该边应暴露、观测、删除还是交给评审门禁",
        ],
    )
    and has_all(
        "senior-software-architect/references/testing.md",
        [
            "若验证对象是节点、通信边或状态传播",
            "不要为了覆盖隐藏边而断言内部调用顺序",
            "关键通信边和状态传播",
            "删节点/删边的前提和债务到期条件",
        ],
    )
    and has_all(
        senior_routing,
        [
            "节点/通信边和状态传播分为可代码化、可观测化和可评审化",
            "隐藏边排障",
        ],
    ),
)
check(
    "senior product design maps business-driven validation to TDD assets",
    has_all(
        "senior-software-architect/references/product-design.md",
        [
            "### 3.3 业务驱动验证到 TDD 映射",
            "业务驱动验证到 TDD 映射矩阵",
            "AC-xxx",
            "QA-xxx",
            "追踪ID",
            "业务目标/验收种子/质量属性",
            "可代码化",
            "可观测化",
            "可评审化",
            "第一批失败反馈候选",
            "人工确认门禁",
        ],
    ),
)
check(
    "senior testing separates code observable and review verification assets",
    has_all(
        "senior-software-architect/references/testing.md",
        [
            "业务驱动验证进入 TDD 前",
            "AC-xxx",
            "QA-xxx",
            "保留追踪 ID",
            "只有可代码化项进入 red-green-refactor",
            "可观测化和可评审化项仍然是验证资产",
            "业务驱动验证到 TDD 映射矩阵",
        ],
    ),
)

lifecycle_stages = ["Clarify", "Design", "Plan", "Build", "Verify", "Review/Ship"]
check("workflow defines engineering lifecycle gate", contains(workflow, "## 工程生命周期门禁"))
check("workflow defines external knowledge freshness gate", contains(workflow, "## 外部知识时效性门禁"))
check(
    "external knowledge gate rejects model-memory-only answers",
    has_all(
        workflow,
        [
            "不得只依赖模型记忆或历史经验",
            "名称、版本、生效/发布日期、核验日期、适用模块",
            "来源、版本或发布日期、适用法域/主体、生效日期、确认方",
        ],
    ),
)
check("workflow includes all lifecycle stages", all(contains(workflow, stage) for stage in lifecycle_stages))
check(
    "workflow preserves test-driven design boundary",
    contains(workflow, "设计前必须先构造用例、测试用例、边界条件、异常路径和验收标准"),
)
check(
    "workflow preserves PR description and small change rules",
    has_all(
        workflow,
        [
            "一个提交/PR 默认只承载一个自包含变更",
            "相关测试应随同一变更提交",
            "大重构、搬迁和重命名通常与功能修改、Bug 修复分开提交",
            "## PR/CL 说明质量",
            "第一行清楚说明本次变更具体做了什么",
            "提交前应回看并更新说明",
        ],
    ),
)
check(
    "workflow routes AI and CAD references separately",
    has_all(
        workflow,
        [
            "AI 协作或多 Agent 必须继续读取 `ai-assisted-engineering.md`",
            "CAD Mode、Plan Grant / Execution Grant 或自动分轮推进必须继续读取 `cad-mode.md`",
        ],
    ),
)
check(
    "production readiness defines emergency change boundary",
    has_all(
        "senior-software-architect/references/production-readiness.md",
        [
            "## 紧急变更边界",
            "真实生产风险或硬截止日期",
            "不构成紧急情况",
            "事后完整 Review、测试、复盘和技术债登记",
        ],
    ),
)
check(
    "AI engineering maps to workflow lifecycle",
    has_all(
        ai_engineering,
        [
            "## 工程生命周期映射",
            "必须服从 `workflow.md`",
            "不得把“用户说继续”解释为跳过 OpenSpec、Harness Plan、Plan Grant / Execution Grant、验证或高风险人工确认点",
        ],
    ),
)
check(
    "AI engineering codifies OpenSpec Superpowers Harness split",
    has_all(
        ai_engineering,
        [
            "OpenSpec / Superpowers / Harness 的责任边界",
            "OpenSpec | 规定要做什么",
            "Superpowers | 规定怎么高质量地做",
            "Harness | 规定谁做、按什么顺序做、能改哪里、怎么验证、怎么交接",
            "轻量修改：目标 + 写入范围 + 验证命令",
            "中高风险 AI 编码：OpenSpec + Harness Plan + Superpowers 检查",
            "中大型项目：OpenSpec + context ledger + GSD Stage/Wave/Atomic Task + Harness Plan + verification matrix",
            "受控自动推进：上述门禁 + 单个 CAD 候选任务 + Plan Grant / Execution Grant",
        ],
    )
    and has_all(
        workflow,
        [
            "谁做、按什么顺序做、能改哪里、只读哪里、怎么验证、何时停止、怎么交接",
            "OpenSpec 规定要做什么，Superpowers 规定怎么高质量地做，Harness 规定谁做、按什么顺序做、能改哪里、怎么验证、怎么交接",
        ],
    ),
)
check(
    "AI Native routes architect code quality and production capabilities to senior architect",
    has_all(
        ai_engineering,
        [
            "AI Native 调用架构师做代码质量与 Review",
            "源码锚点",
            "行为影响",
            "质量风险",
            "验证闭环",
            "交接结果",
            "产品语义缺失退回 `产品架构专家` 或 AI Native Round 0",
        ],
    )
    and has_all(
        production_readiness,
        [
            "AI Native 调用架构师的生产能力细化",
            "Runbook、CI/CD、发布门禁、data fetching and analysis 或 infrastructure operations",
            "只承接工程判断和可执行验证",
            "告警/日志/指标/trace",
            "CI 结果",
            "dry-run、备份、分批、审计、回滚材料、复核记录和残余风险",
            "生产数据、配置、数据库迁移、真实支付/资金、删除、重放、部署、依赖安装、密钥或外部账号操作必须显式确认",
            "无 dry-run、备份、分批、审计、回滚和负责人时，只能输出计划，不能建议执行",
        ],
    ),
)
check(
    "senior harness plan checker is wired and scoped",
    has_all(
        senior_skill,
        [
            "`scripts/check_harness_plan.py`",
            "`--kind lightweight|gsd-wave|cad-candidate`",
            "缺少 Task ID、Owner、写入范围、只读范围、依赖顺序、验证命令、停止条件、交接或 Execution Grant 关联时返回非 0",
            "脚本通过不等于 CAD 授权、测试通过或生产审批",
        ],
    )
    and has_all(
        "scripts/validate.sh",
        [
            "python3 -m py_compile senior-software-architect/scripts/check_harness_plan.py",
            "senior-software-architect/scripts/check_harness_plan.py --self-test",
        ],
    )
    and has_all(
        harness_plan_checker,
        [
            "CHECKS",
            "lightweight",
            "gsd-wave",
            "cad-candidate",
            "SELF_TESTS",
            "FAIL harness plan check",
            "OK harness plan self-test",
            "does not access the network",
            "does not access the network, upload content, read secrets, or judge technical quality",
        ],
    ),
)
check(
    "Harness plan becomes executable collaboration contract",
    has_all(
        ai_engineering,
        [
            "Harness 的产物不是“再写一份项目计划”，而是当前任务的可执行协作契约",
            "Task ID：本任务的稳定追踪编号",
            "Harness Plan 分级",
            "lightweight",
            "gsd-wave",
            "cad-candidate",
            "需要正式检查 Harness Plan 时，使用 `scripts/check_harness_plan.py`",
            "Harness 交接最小格式",
            "不允许 Harness Plan 的写入范围宽到“整个仓库”“整个 src”而没有进一步切片",
        ],
    )
    and has_all(
        ai_large_project,
        [
            "Harness Plan 最小模板",
            "Task ID:",
            "依赖顺序:",
            "停止条件:",
            "恢复入口:",
            "Execution Grant 关联: 无/待确认/已确认",
            "Harness Plan 必须体现一句话原则",
            "senior-software-architect/scripts/check_harness_plan.py --kind gsd-wave",
        ],
    ),
)
check(
    "CAD mode split keeps AI engineering as overview",
    has_all(
        senior_skill,
        [
            "`references/ai-assisted-engineering.md`",
            "`references/cad-mode.md`",
            "CAD Mode 唯一详细规则源",
        ],
    )
    and has_all(
        ai_engineering,
        [
            "CAD Mode 详细执行规则只读 `cad-mode.md`",
            "不得把“用户说继续”解释为跳过 OpenSpec、Harness Plan、Plan Grant / Execution Grant、验证或高风险人工确认点",
            "AI 协作总纲不得复制这些细节",
        ],
    )
    and has_all(
        cad_mode,
        [
            "## 使用时机",
            "## 按任务读取索引",
            "受控自治开发模式",
            "Plan Grant / Execution Grant 是 CAD Mode 的权限边界",
            "每轮执行闭环",
            "5 秒",
            "平台权限边界优先于 Plan Grant / Execution Grant",
        ],
    ),
)
check(
    "GSD-CAD protocol keeps planning separate from execution authorization",
    has_all(
        ai_large_project,
        [
            "## 8. GSD-CAD 双层协议",
            "GSD-like 编排管大盘，CAD Mode 跑单元",
            "不得对整个大项目直接开启 CAD",
            "GSD defines what can be executed",
            "CAD decides whether it may be executed automatically",
            "Plan Grant / Execution Grant decides what is actually allowed",
            "Validation decides whether it may continue",
            "CAD 候选任务必须同时满足",
            "已准备 Plan Grant / Execution Grant",
            "已准备提交切片",
            "commit_after_verified_task",
            "CAD 输出必须回写阶段状态、验证矩阵和 handoff",
            "只有原子任务包满足 CAD 门禁时，才建议进入 CAD",
        ],
    )
    and has_all(
        cad_mode,
        [
            "中大型项目、长任务、上下文衰减或 Wave 编排读 `ai-large-project-orchestration.md`",
            "CAD 只消费其中已满足门禁的单个任务包或阶段切片",
            "CAD 不直接消费整个 Roadmap",
            "Plan Grant: Active",
            "用户只给了 GSD-like Roadmap、Wave 或任务清单，但没有选定单个任务包、写入范围、验证命令，也没有 Plan Grant / Execution Grant",
            "必须已选定单个 Task ID 或阶段切片",
            "GSD-CAD 联动审查",
            "回写阶段状态、验证矩阵和 handoff",
            "Harness Plan 已形成：Task ID、Owner、任务拆分、写入范围、只读范围、依赖顺序、验证命令、停止条件、交接方式和恢复入口清楚",
            "通过 `scripts/check_harness_plan.py --kind cad-candidate`",
            "Harness Plan 中的写入范围与 Plan Grant / Execution Grant 的授权范围一致",
        ],
    )
    and has_all(
        senior_routing,
        [
            "GSD-like 编排管大盘，CAD Mode 只消费已满足门禁的单个任务包或阶段切片",
            "GSD-like 编排 + CAD Mode",
            "不得对整个大项目直接开启 CAD",
            "不得把 Roadmap、Wave 或任务清单当作 Plan Grant / Execution Grant",
        ],
    ),
)
check(
    "negative constraints routes CAD authority to CAD mode",
    has_all(
        negative_constraints,
        [
            "`cad-mode.md` 定义的 Plan Grant / Execution Grant",
            "Git 策略和自动提交边界以 `cad-mode.md` 为准",
            "统一以 `cad-mode.md` 为唯一详细规则源",
        ],
    )
    and has_none(
        negative_constraints,
        [
            "`ai-assisted-engineering.md` 定义的 Execution Grant",
            "Git 策略和自动提交边界以 `ai-assisted-engineering.md` 为准",
            "统一以 `ai-assisted-engineering.md` 为唯一详细规则源",
        ],
    ),
)
check(
    "AI engineering absorbs external skill methods without becoming a menu",
    has_all(
        ai_engineering,
        [
            "外部 AI Skill 方法论只作为工程纪律参考，不作为本技能的新能力菜单",
            "先澄清再编码、简单优先、最小变更、目标驱动验证、领域语言对齐、TDD、诊断闭环和 Review 防越界",
            "SkillX 类技能知识库方法只作为 AI 经验沉淀参考",
            "规划技能、功能技能、原子技能三分法",
            "每个实现步骤都必须回指当前 OpenSpec、用户目标或验收标准",
            "## AI 经验沉淀门禁",
            "规划层经验",
            "功能层经验",
            "原子层经验",
            "过滤探索噪音、回退路径、一次性修补、临时偏好和未经验证的模型猜测",
            "未获明确同意不得写入 `~/.skill-learning/`",
            "不默认创建额外 `CONTEXT.md`",
            "不允许把外部 Skill 的工作流、术语或自动化步骤凌驾于当前仓库 `AGENTS.md`、OpenSpec、Harness Plan、测试和用户授权之上",
        ],
    ),
)
check(
    "AI engineering guards generation complexity",
    has_all(
        ai_engineering,
        [
            "代码生成降低的是执行成本，不降低系统复杂度",
            "不要写什么、必须删什么、何时停止",
            "复杂度与注意力成本",
        ],
    ),
)
check(
    "senior AI engineering governs long-task context decay",
    has_all(
        ai_engineering,
        [
            "长任务的上下文账本、阶段状态、交接方式和恢复入口",
            "中大型 AI 编码或上下文衰减治理",
            "上下文衰减",
            "可审查、可版本化、可恢复的载体",
            "详细流程、账本文件、阶段模板、原子任务包、Wave 依赖、暂停恢复、Git 边界和收口模板统一读 `ai-large-project-orchestration.md`",
            "最小上下文账本",
            "阶段状态",
            "原子任务计划",
            "子 Agent 与 Wave 编排",
            "研究者",
            "规划者",
            "执行者",
            "验证者",
            "同一 Wave 只能包含互不重叠、无顺序依赖、可独立验证的任务",
            "Git 操作仍服从项目规则和用户授权",
            "不把外部工作流命令、XML 示例或文件命名照搬进项目",
            "低风险小修、3 分钟内可完成的明确改动、一次性 demo 或 MVP 快速验证",
        ],
    ),
)
check(
    "senior AI large project orchestration defines GSD-like workflow",
    has_all(
        ai_large_project,
        [
            "# AI 大项目编排工作流",
            "不依赖外部 GSD 工具",
            "## 使用时机",
            "## 不适用场景",
            "## 读取后必须产出",
            "## 需要继续读取的 reference",
            "## 按任务读取索引",
            "docs/ai-orchestration/<initiative-id>/",
            "00-open-spec.md",
            "01-context-ledger.md",
            "03-state.md",
            "04-harness-plan.md",
            "Task ID:",
            "Wave 0：只读侦察",
            "同一 Wave 内任务必须互不重叠、无顺序依赖、可独立验证",
            "GSD-CAD 双层协议",
            "CAD 候选：是/否，原因",
            "Execution Grant 要求",
            "暂停前必须更新 `03-state.md`",
            "恢复时先读",
            "大项目编排鼓励原子可追溯，且必须在规划阶段给出提交切片",
            "是否实际执行 Git 写操作由 Grant 和工具权限决定",
            "Codex 持续协作边界",
            "Thread automation",
            "Scheduled automation",
            "Goal",
            "Side panel / artifact",
            "Shared written context",
            "必须包含 outcome、success criterion、verifier、停止条件和失败处理",
            "不把 automation、goal 或 queue 当成 Git、联网、外部消息、桌面 GUI、生产操作或长期记忆授权",
            "外部 GSD 来源边界",
            "Codex 官方团队文章来源边界",
            "不作为 OpenAI 官方当前产品能力、模型、工具可用性或路线图承诺依据",
            "涉及 Codex 当前能力、工具状态、产品规则或官方承诺时，必须核验 OpenAI 官方文档或当前会话工具状态",
            "不把该微信文章当作 OpenAI 官方当前能力、产品可用性、模型、工具或路线图承诺",
            "不安装、不调用、不复刻外部 GSD 工具",
        ],
    )
    and has_all(
        senior_skill,
        [
            "中大型项目、长任务、上下文衰减、多 Agent/Wave 编排读 `references/ai-large-project-orchestration.md`",
            "`references/ai-large-project-orchestration.md`",
            "不安装或照搬外部 GSD 工具",
        ],
    )
    and has_all(
        senior_routing,
        [
            "`ai-large-project-orchestration.md`",
            "中大型长任务",
            "原子任务包",
            "GSD-like 编排 + CAD Mode",
            "验证矩阵、暂停恢复和收口流程",
        ],
    ),
)
check(
    "senior diagram output keeps codebase visual understanding package",
    has_all(
        senior_diagram,
        [
            "陌生代码库图形化理解",
            "文字总结容易堆成无法评审的长段落",
            "只读提取架构描述",
            "启动入口",
            "认证与权限入口",
            "外部系统",
            "数据/消息/状态流",
            "关键源码锚点",
            "未确认连接",
            "进入实现/CR 的结论",
            "如果只有自然语言描述而没有源码锚点",
            "不能作为架构结论、重构计划或 CR 准出依据",
            "如何让 AI 画出高质量架构图，一个Skill搞定",
            "不安装文中提到的外部 Skill",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "如何让 AI 画出高质量架构图，一个Skill搞定",
            "日积月码",
            "页面时间字段为 2026-05-12",
            "陌生代码库先形成架构描述",
            "图形化理解包",
            "不安装《如何让 AI 画出高质量架构图，一个Skill搞定》中提到的外部 Skill",
        ],
    ),
)
check(
    "senior AI Native architect and hardening gates are routed",
    has_all(
        ai_engineering,
        [
            "AI Native 架构师工作面",
            "AI 进入旧系统的架构门禁",
            "可开发系统工程化门禁",
            "Context 架构",
            "权限与权力边界",
            "旧系统技术债",
            "多端一致性",
            "任务闭环",
            "成本与稳定性",
            "可观测与审计",
            "演进切片",
            "AI 旧系统接入 OpenSpec 补充",
            "判断什么是好的系统",
            "定义 hardened 标准",
            "设计 Agent 工作流",
            "审查 AI 代码时，重点不是证明每一行都由人工重新理解",
            "产出整体满足 hardened 标准",
            "不把“少写代码”理解为放弃编码能力、验证或生产责任",
            "前后台和多端边界",
            "业务流",
            "对象状态",
            "规则权限",
            "接口候选",
            "测试验收",
            "不从页面愿望直接拆代码任务",
        ],
    )
    and has_all(
        ai_large_project,
        [
            "AI Native 产品到工程的端到端链路由 `ai-native-engineering-workflow` 维护",
            "AI Native 交接结论",
            "OpenSpec / context ledger / verification matrix",
            "GSD Stage / Wave / Atomic Task",
            "CAD 候选 / Execution Grant 缺口",
            "产品上下文包回答“这个产品候选是否值得工程化、工程化必须保留哪些业务事实”",
            "`ai-native-engineering-workflow` 回答“端到端流程如何流转、是否进入 GSD/CAD 编排候选、谁负责、何时停止”",
            "消费 AI Native 编排交接结论",
            "本文件只消费以下工程输入",
            "业务方能跑通 MVP，就直接让 CAD 改代码",
        ],
    )
    and has_all(
        cad_mode,
        [
            "从 AI Native 产品上下文或 MVP harden 进入 CAD",
            "不把产品上下文包、Hardened Candidate 或业务 MVP 当授权",
            "`ai-native-engineering-workflow/references/gsd-cad-admission.md` 或产品侧交接结论",
            "不得把业务 MVP、PRD、产品上下文包或 GSD Roadmap 直接当授权",
        ],
    )
    and has_all(
        senior_routing,
        [
            "PRD/产品方案/AI Native 产品上下文到系统设计 / 业务驱动架构",
            "AI Native 端到端产品到研发流程先由 `ai-native-engineering-workflow` 编排",
            "架构师只消费已确认的 Hardened Candidate 或 AI Native 交接结论",
            "来自业务 MVP 或 AI Native 产品上下文时只消费已确认的 Hardened Candidate 或 AI Native 交接结论",
        ],
    ),
)
check(
    "workflow and routing expose AI context ledger gates",
    has_all(
        workflow,
        [
            "上下文账本、阶段状态、子任务交接和恢复入口",
            "不得依赖主会话长期记忆维持目标、决策、阻塞项和验证证据",
            "多 Agent、长任务或跨模块 AI 编码还必须明确上下文账本、阶段状态、原子任务计划、Wave 依赖、交接说明和会话恢复入口",
            "AI 多 Agent 或 Wave 编排产生的变更应保持原子可追溯",
        ],
    )
    and has_all(
        senior_routing,
        [
            "AI 编码协作 / OpenSpec 到代码 / 多 Agent 编排 / 上下文衰减治理",
            "上下文账本、阶段状态、原子任务包、Wave 依赖、暂停恢复、交接和收口",
            "先判断是需求不清还是上下文衰减",
            "明确小修、一次性 demo 或快速 MVP 验证不启动重型并行流程",
        ],
    ),
)
check(
    "workflow requires diff traceability to goals",
    contains(workflow, "每个代码 diff、测试和重构都必须能回指用户目标、OpenSpec 条款、缺陷复现或验收场景"),
)
check(
    "senior architecture keeps AI-era complexity control",
    has_all(
        "senior-software-architect/references/architecture.md",
        [
            "代码生成和 AI 协作场景",
            "定义问题、控制复杂度、分配团队注意力",
            "低成本代码变成高成本理解和维护",
            "是否因为实现成本低而引入了无效尝试",
        ],
    ),
)
check(
    "senior ADR reference keeps multi-frame exploration gate",
    has_all(
        adr_tradeoff,
        [
            "## 探索期多框架分析",
            "过早推荐单一方案会锁死后续设计",
            "保留 3-5 个真正不同的判断框架",
            "默认假设是什么",
            "容易忽略哪些成本、风险或组织能力",
            "与其他框架冲突在哪里",
            "什么条件下该框架失效",
            "不要把同一个结论包装成多个框架",
            "收敛到备选方案、选择理由、放弃理由、风险缓解、验证方式和复审条件",
        ],
    ),
)
check(
    "system analysis template is split from design guidance",
    has_all(
        senior_skill,
        [
            "`references/system-analysis-design.md`",
            "`references/system-analysis-template.md`",
        ],
    )
    and has_all(
        "senior-software-architect/references/system-analysis-design.md",
        [
            "读取 `system-analysis-template.md` 获取可复制模板",
            "## 3. 章节写作要求",
            "## 5. 评审清单",
        ],
    )
    and has_all(
        system_analysis_template,
        [
            "# 系统分析设计模板",
            "## 使用时机",
            "## 不适用场景",
            "## 读取后必须产出",
            "## 需要继续读取的 reference",
            "## 按任务读取索引",
            "PRD/产品方案到系分",
            "### 1.3 产品语义输入",
            "追踪ID",
            "QA-001 | 质量属性种子",
            "### 3.1A 设计视图清单",
            "上下文视图",
            "### 3.1B 业务驱动追踪表",
            "### 4.10 业务驱动验证承接",
            "业务目标/验收种子/质量属性",
            "### 5.2A 质量属性场景",
            "质量属性ID",
            "可代码化/可观测化/可评审化",
            "## 文档状态与版本信息",
            "过程记录链接",
            "本系分正文只保留当前有效设计、取舍、风险、待确认和验证计划",
            "## 1. 文档头、背景与目标模板",
            "## 2. 概要设计模板",
            "## 3. 模块与接口设计模板",
            "## 4. 数据设计模板",
            "## 5. 状态、流程与专项设计模板",
            "## 6. 非功能、研发计划与参考资料模板",
            "# <需求/系统/模块名称> 系统分析设计文档",
        ],
    ),
)
check(
    "system analysis design keeps final document process separation",
    has_all(
        "senior-software-architect/references/system-analysis-design.md",
        [
            "文档状态与版本信息",
            "正式系分以最终标准版本为主",
            "完整修订流水、评审争论、AI 推理轨迹、迭代草稿和被拒方案进入评审报告、ADR、Decision Log、任务计划或中间任务文档",
            "不得把旧版本方案、历史讨论和多轮草稿与当前设计结论混写",
        ],
    ),
)
check(
    "AI Native spec templates keep final specs separate from process assets",
    has_all(
        ai_native_spec_template_practices,
        [
            "Spec / SDD / OpenSpec 是当前实现约束，不是评审过程记录",
            "讨论过程、迭代草稿、AI 推理轨迹、被拒方案和 Goal Ledger 流水只作为过程资产链接，不复制进正文",
            "是否把讨论过程、迭代草稿、AI 推理轨迹、被拒方案或完整 Goal Ledger 流水写进 Spec 正文",
            "不要把过程记录回流成最终交付正文",
        ],
    ),
)
check(
    "senior route sends code changes through workflow",
    has_all(
        senior_routing,
        [
            "用户要“改代码”",
            "Clarify、Design、Plan、Build、Verify、Review/Ship 生命周期门禁",
        ],
    ),
)
check(
    "senior route sends AI collaboration through workflow first",
    has_all(
        senior_routing,
        [
            "`workflow.md`、`ai-assisted-engineering.md`",
            "`cad-mode.md`",
            "先过工程生命周期门禁",
        ],
    ),
)
check(
    "senior route sends external dependency changes through freshness gate",
    has_all(
        senior_routing,
        [
            "外部 API / SDK / 云产品 / 第三方服务 / 版本升级",
            "先过外部知识时效性门禁",
            "官方文档、release notes、项目 lockfile 或本地依赖树",
        ],
    ),
)
check(
    "senior route sends visual deliverables to diagram output",
    has_all(
        senior_routing,
        [
            "图形化架构交付读 `diagram-output.md`",
            "架构图 / 流程图 / 时序图 / 状态机 / ER 图 / 类图 / 部署图 / 迁移图 / 可视化产物",
            "图形目标、图形类型、工程落点",
        ],
    ),
)
check(
    "senior route sends codebase onboarding to language agnostic reconnaissance",
    has_all(
        senior_routing,
        [
            "陌生代码库接手 / 项目现状分析",
            "项目清单、技术指纹、入口路径、目录语义、配置、测试、数据和运行链路侦察",
        ],
    ),
)
check(
    "language agnostic reference defines codebase reconnaissance",
    has_all(
        language_agnostic,
        [
            "## 2. 技术栈识别",
            "### 2.1 陌生代码库侦察",
            "项目清单",
            "技术指纹",
            "入口路径",
            "目录语义",
            "测试与质量",
            "关键链路",
            "不要自动创建新的上手文档",
        ],
    ),
)
check(
    "senior route sends architecture smell scan to review guidance",
    has_all(
        senior_routing,
        [
            "架构坏味 / 深度代码质量扫描",
            "上帝类、循环依赖、过长方法、Feature Envy、Data Clumps",
        ],
    ),
)
check(
    "review guidance defines architecture smell heuristic scan",
    has_all(
        review,
        [
            "## Java 架构坏味启发式扫描",
            "上帝类 / God Class",
            "循环依赖",
            "过长方法",
            "Feature Envy",
            "Data Clumps",
            "公共模块垃圾桶",
            "以下阈值是提示信号，不是机械定罪",
        ],
    ),
)
check(
    "review guidance absorbs Google review collaboration rules",
    has_all(
        review,
        [
            "Review 的目标是让代码库长期健康持续变好",
            "评论分级建议",
            "Review 导航顺序",
            "重大设计问题先反馈",
            "明确审查范围",
            "不评价作者个人",
        ],
    ),
)
check(
    "debugging reference defines incident timeline and 5 why",
    has_all(
        debugging,
        [
            "## 生产故障时间线",
            "事实、假设、判断分开写",
            "顺序推测",
            "## 5-Why 复盘草稿",
            "证据等级和待人工确认项",
            "短期止血",
            "中期加固",
            "长期预防",
        ],
    ),
)
check(
    "security reference defines Spring Boot security checklist",
    has_all(
        security,
        [
            "## Spring Boot 安全落地检查",
            "SecurityFilterChain",
            "方法级授权",
            "CSRF",
            "CORS",
            "X-Forwarded-For",
            "限流与滥用",
            "错误响应",
        ],
    ),
)
check(
    "write tests route enters testing before practices",
    has_all(
        senior_routing,
        [
            "写测试 / 补测试 / 加测试 / 按 TDD 推进",
            "`testing.md`",
            "只有命中 `testing.md` 第 6/12 节专项条件时再读 `testing-practices.md`",
        ],
    ),
)
check(
    "testing reference keeps testing-practices boundary",
    has_all(
        testing,
        [
            "## 12. 何时读取 testing-practices.md",
            "不要绕过本文件的测试选择",
        ],
    ),
)
check(
    "senior testing keeps invariant verification cluster method",
    has_all(
        testing,
        [
            "不变量支撑的验证簇",
            "测试通过、覆盖率提高、bug 下降都只是证据，不是事实本身",
            "高风险业务不变量",
            "验证簇 ID",
            "场景测试",
            "属性 / 变形测试",
            "历史回归入口",
            "生产重放样本",
            "有限变异 / 对抗检查",
            "置信度",
            "来源",
            "CI 分层",
            "生产重放只能作为证据，不能反向定义需求",
        ],
    ),
)
check(
    "JSpecify nullability rule is encoded in coding standards",
    has_all(
        coding,
        [
            "内部 Java 契约优先使用 `org.jspecify.annotations.Nullable`、`NonNull`、`NullMarked`",
            "已由 JSpecify 标注为非空的参数、返回值和字段，不再额外添加无业务语义的 `AssertUtils.notNull`",
        ],
    ),
)
check(
    "JSpecify nullability rule is encoded in review guidance",
    has_all(
        review,
        [
            "内部契约使用 `org.jspecify.annotations` 表达 nullability",
            "已由 JSpecify 标注为非空的普通参数、返回值和字段，不再重复写无业务语义的空判断",
        ],
    ),
)
check(
    "Java common utility reuse rule is encoded in coding standards",
    has_all(
        coding,
        [
            "不得手写 `hasText`、`isBlank`、`isEmpty` 等同义工具",
            "优先使用 Spring Framework 或 Apache Commons 已提供的成熟工具",
            "`org.springframework.util.StringUtils`",
            "`org.apache.commons.lang3.StringUtils`",
        ],
    ),
)
check(
    "Java common utility reuse rule is encoded in review guidance",
    has_all(
        review,
        [
            "检查是否手写 `hasText`、`isBlank`、`isEmpty` 等基础工具",
            "优先使用 Spring Framework 或 Apache Commons 成熟工具",
        ],
    ),
)
check(
    "Java DTO atomic field ban is encoded in coding standards",
    has_all(
        coding,
        [
            "数据传输对象的成员变量不得使用 `boolean`",
            "`int`",
            "`long`",
            "Java 原生基本类型",
            "不得使用 `AtomicInteger`",
            "`AtomicLong`",
            "`AtomicBoolean`",
            "`AtomicReference`",
            "`LongAdder`",
            "`DoubleAdder`",
            "数据传输对象是序列化契约和数据快照",
            "可缺省、默认值、精度和序列化语义",
        ],
    ),
)
check(
    "Java DTO atomic field ban is encoded in review guidance",
    has_all(
        review,
        [
            "数据传输对象的成员变量不得使用 `boolean`",
            "Java 原生基本类型",
            "不得使用 `AtomicInteger`",
            "可缺省、默认值、精度和序列化语义",
            "契约污染",
            "线程安全增强",
        ],
    ),
)
check(
    "Java production code bans in-memory business service implementations",
    has_all(
        senior_skill,
        [
            "业务代码不得用内存版 Service 冒充生产实现",
            "`InMemoryXxxService`",
            "Map/List 存储型业务实现",
            "只在进程内保留状态的应用服务",
        ],
    )
    and has_all(
        coding,
        [
            "业务代码不得用内存版 Service 冒充生产实现",
            "除缓存能力、测试替身/fixture、沙盒模拟或明确 demo 外",
            "`InMemoryXxxService`",
            "`FakeXxxService`",
            "`MockXxxService`",
            "Map/List 存储型业务实现",
            "生产源码路径",
            "不能代表生产能力",
        ],
    )
    and has_all(
        review,
        [
            "生产实现与内存服务",
            "业务代码不得用内存版 Service 冒充生产实现",
            "Map/List 存储型业务实现",
            "缺少持久化、一致性、并发、审计、恢复、发布回滚和真实验证能力",
            "缓存、测试替身、fixture、沙盒模拟或明确 demo 必须隔离在对应边界内",
        ],
    )
    and has_all(
        negative_constraints,
        [
            "除缓存能力、测试替身/fixture、沙盒模拟或明确 demo 外",
            "`InMemoryXxxService`",
            "Map/List 存储型业务实现",
            "进程内状态应用服务承载真实业务能力",
        ],
    ),
)

product_gates = ["术语", "主体", "目标", "对象", "流程", "规则", "数据", "风险", "验收"]
check("product route defines semantic gate", contains(product_routing, "## 产品语义门禁"))
check("product semantic gate covers core gates", all(contains(product_routing, f"| {gate} |") for gate in product_gates))
check(
    "product route records external rule freshness",
    has_all(
        product_routing,
        [
            "外部规则、政策、通道协议、卡组织/ACH/银行规则、云产品限制、第三方平台 API 或 SDK 版本会随时间变化",
            "来源、版本或发布日期、适用范围、核验日期和确认方",
            "继续读取 `regulatory-baseline.md`",
        ],
    ),
)
check(
    "product top-level route sends acquiring signals to payment specialty",
    has_all(
        product_routing,
        [
            "外卡收单、Mastercard、卡组织清算、Clearing Core、商户到账或收单风控同样先进入支付资金专项",
            "外卡收单、Mastercard、Clearing Core、商户到账",
            "支付、资金、账本、清结算、对账、VCC、ACH、银行卡/卡组织、外卡收单、Mastercard、Clearing Core、商户到账、争议",
        ],
    ),
)
check(
    "product route sends visual deliverables to diagram output",
    has_all(
        product_routing,
        [
            "图形化产品交付读 `diagram-output.md`",
            "画图、流程图、状态机、关系图、产品架构图、资金流图、运营后台结构图、可视化产物",
            "用途、假设、验证和待确认项",
        ],
    ),
)
check(
    "PRD route loads template and design references",
    has_all(
        product_routing,
        [
            "product-prd-template.md",
            "product-design-and-prd.md",
            "product-prd-quality-gates.md",
            "product-prd-financial-appendix.md",
            "product-prd-operations-and-data.md",
        ],
    ),
)
check(
    "product route supports prototype to PRD",
    has_all(
        product_routing,
        [
            "原型/HTML/页面截图/交互稿反推 PRD",
            "原型、HTML、页面截图、页面说明或交互稿",
            "错误截图、日志截图或测试失败截图",
            "优先使用 `资深架构师`",
            "先反推角色、对象、流程、规则、状态和验收",
            "不要只描述页面控件",
        ],
    ),
)
check(
    "senior architect keeps architecture decay and entropy review gate",
    has_all(
        senior_skill,
        [
            "架构代谢",
            "可执行约束",
            "可追溯理由链",
            "时间边界先过三问",
            "可删除性",
            "排熵通道",
        ],
    )
    and has_all(
        senior_routing,
        [
            "架构腐朽 / 排熵 / 可删除性评审 / 不敢删 / 承重 bug",
            "evolutionary-architecture.md",
            "coding-review-deep-dive.md",
            "治理自腐",
            "守卫自检",
            "最小排熵计划",
        ],
    )
    and has_all(
        "senior-software-architect/references/evolutionary-architecture.md",
        [
            "架构腐朽与排熵评审",
            "Architecture Entropy Review",
            "可删除性下降",
            "局部推理边界丢失",
            "承重行为",
            "废弃路径堆积",
            "概念膨胀",
            "治理自腐",
            "守卫自检",
            "最小正确实现 / 过度设计候选",
            "可执行约束 / 可追溯理由链",
            "时间边界三问",
            "棘轮基线",
            "熵增仪表",
            "理由保鲜",
            "非对称稳定性",
            "最小排熵计划",
            "不得把自动扫描结果直接等同于可删除、可迁移、可重写或可上线结论",
            "Ponytail-style 过度设计检查只能提出可删除复杂度候选",
        ],
    )
    and has_all(
        architecture,
        [
            "架构规则 = 被持续执行的约束 x 能追溯的理由链",
            "执行点",
            "理由指针",
        ],
    )
    and has_all(
        review,
        [
            "时间边界三问",
            "重启之后",
            "重放之时",
            "状态不明时",
            "时间边界缺失",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "架构腐朽与排熵 Loop",
            "深度思考：架构腐朽 & Loop Engineering",
            "https://mp.weixin.qq.com/s/wINKSDQCroWBvf29h567zA",
            "Architecture Entropy Review",
            "2026-06-22",
            "可执行约束 / 可追溯理由链",
            "时间边界三问",
            "不把自动扫描、Loop、Checker 或规则检查写成可以自动删除、迁移、重写、合并、测试通过、CR 结论、执行授权或上线审批",
        ],
    ),
)
check(
    "product expert keeps concept lifecycle and retirement gate",
    has_all(
        product_skill,
        [
            "概念生命周期要能退役",
            "新增概念、规则、页面、状态或能力",
            "谁拥有、替代什么",
            "何时复审与退役",
        ],
    )
    and has_all(
        product_routing,
        [
            "概念膨胀",
            "新旧概念并存",
            "概念生命周期与退役",
            "Concept Lifecycle Card",
            "新增/替代关系",
            "净增概念数",
            "复审日期",
            "退役条件",
            "不把概念退役写成工程删除授权",
        ],
    )
    and has_all(
        product_concept_lifecycle,
        [
            "产品概念生命周期与退役",
            "Concept Lifecycle Card",
            "当前事实源",
            "新增 / 替代关系",
            "净增概念数",
            "与旧概念 / 旧规则关系",
            "收敛 / 合并 / 废弃规则",
            "迁移路径",
            "下线 owner",
            "复审日期",
            "退役条件",
            "产品专家不把概念退役写成工程删除授权",
        ],
    )
    and has_all(
        product_source_map,
        [
            "概念生命周期与退役",
            "深度思考：架构腐朽 & Loop Engineering",
            "https://mp.weixin.qq.com/s/wINKSDQCroWBvf29h567zA",
            "2026-06-22",
            "新增 / 替代关系",
            "净增概念数",
            "复审日期",
            "退役条件",
            "不把概念退役写成工程删除、数据迁移、公共契约变更、执行授权或上线审批",
        ],
    ),
)
check(
    "product architecture methodology keeps multi-frame exploration gate",
    has_all(
        product_architecture,
        [
            "## 2. 探索期收敛",
            "### 2.0 探索期多框架分析",
            "避免过早把问题锁进单一路径",
            "保留 3-5 个真正不同的框架",
            "关注什么问题",
            "默认假设是什么",
            "与其他框架的冲突点在哪里",
            "在什么条件下会失效",
            "不要为了显得完整制造伪多样性",
            "形成可评审交付物",
        ],
    ),
)
check(
    "product methodology keeps feedback evidence problem map",
    has_all(
        product_architecture,
        [
            "反馈证据与问题地图",
            "原始反馈",
            "真实问题",
            "使用场景",
            "影响范围",
            "证据强度",
            "潜在机会",
            "AI 可以先做聚类、去重、归类和初稿表格",
        ],
    ),
)
check(
    "product methodology keeps demand analysis product definition gate",
    has_all(
        product_architecture,
        [
            "根源需求到产品定义",
            "保留原始诉求",
            "追到根源需求",
            "定义产品对象和能力",
            "划定产品边界",
            "识别稳定点和变化点",
            "声明边界坐标",
            "需求分析结论卡",
            "产品定义是需求分析的收口",
            "产品边界会直接影响系统边界、模块拆分、接口契约和上下游责任",
            "不为未确认、无证据、无 owner 的未来想象提前平台化",
            "真实变化轴",
            "### 1.2 价值 / 成本函数与主要矛盾",
            "产品专家不是把客户语言翻译成功能清单",
            "不把抱怨、功能愿望或技术平台包装成产品",
            "价值函数是什么",
            "成本函数是什么",
            "需求是否具备业务同质性",
        ],
    )
    and has_all(
        product_prd,
        [
            "根源需求",
            "产品定义",
            "产品边界",
            "稳定点 / 变化点",
            "上下游分工",
            "原始诉求已转换为根源需求",
            "产品定义说明对象、能力、可见价值行为和成功口径",
            "产品边界说明本产品负责、合作方 / 外部系统负责、本期不做和人工/运营承接部分",
            "没有证据的未来变化不作为平台化、扩展点或系统拆分依据",
        ],
    ),
)
check(
    "product methodology keeps product insight and opportunity radar",
    has_all(
        product_skill,
        [
            "产品洞察/机会雷达",
            "product-insight-analyst.md",
        ],
    )
    and has_all(
        product_agent,
        [
            "产品洞察",
            "机会雷达",
        ],
    )
    and has_all(
        product_architecture,
        [
            "产品洞察与机会雷达",
            "product-insight-analyst.md",
            "资料资产化",
            "客户视角、竞品视角和标杆视角",
            "机会雷达",
            "不要把资料摘要当机会决策",
        ],
    )
    and has_all(
        product_insight,
        [
            "# 产品洞察与机会雷达",
            "它不是独立 Skill",
            "资料资产化",
            "客户视角",
            "竞品视角",
            "标杆视角",
            "证据与推理链",
            "机会雷达模板",
            "未发现相关材料",
            "不超过 15 个",
            "不要让机会雷达直接替代 Backlog 决策",
        ],
    ),
)
check(
    "product methodology keeps backlog decision and opportunity convergence",
    has_all(
        product_skill,
        [
            "机会清单/Backlog 决策",
            "需求优先级",
            "User Story/AC",
            "po-backlog-manager.md",
        ],
    )
    and has_all(
        product_agent,
        [
            "Backlog决策",
            "机会清单",
            "User Story",
            "AC",
        ],
    )
    and has_all(
        product_architecture,
        [
            "Backlog 决策与机会收敛",
            "转读 `po-backlog-manager.md`",
            "本文只保留总原则",
            "不要把洞察清单直接改写成研发任务",
        ],
    )
    and has_all(
        po_backlog_manager,
        [
            "# PO Backlog Manager",
            "它不是独立 Skill",
            "产品架构专家",
            "Backlog 决策包",
            "输入归一化",
            "决策门禁",
            "BV / Business Value",
            "EE / Engineering Effort",
            "三桌校验",
            "P0",
            "P1",
            "P2",
            "拒绝",
            "延后",
            "User Story",
            "AC / Acceptance Criteria",
            "owner",
            "验证方式",
            "不能进入可执行 Backlog",
            "不要把 Backlog 决策写成 Execution Grant",
            "拒绝或延后理由",
        ],
    ),
)
check(
    "product methodology keeps fuzzy requirement system-order gate",
    has_all(
        product_architecture,
        [
            "模糊需求到内容/多端系统",
            "可开发系统秩序链",
            "结构化需求",
            "业务流",
            "对象与规则",
            "原型/页面说明",
            "开发交接",
            "不是一个页面，而是一套系统",
            "投稿/审核/发布/运营后台/多端展示/动态配置/素材管理/权限/统计/日志",
            "不能只输出页面清单或高保真原型",
            "高保真 HTML 原型之后没有回到对象、接口、数据、测试和验收任务",
            "工程无法接",
        ],
    ),
)
check(
    "product methodology keeps deliberation workflow and multi-role review",
    has_all(
        product_skill,
        [
            "product-deliberation-workflow.md",
            "复杂 PRD、AI 生成方案、原型候选、多方争议",
            "合议式产品评审",
        ],
    )
    and has_all(
        product_routing,
        [
            "产品大师、MAGI",
            "`product-deliberation-workflow.md`",
            "合议评审结论：触发原因、阶段门、共识、分歧、必改、建议、待确认、owner、验证方式和下一步去向",
            "用户要多视角、多个 AI、PM/Reviewer、产品大师、MAGI 或合议式评审",
            "不要新增独立产品大师 Skill",
        ],
    )
    and has_reference_header(product_deliberation)
    and has_task_reading_index(product_deliberation)
    and has_all(
        product_deliberation,
        [
            "# 产品合议评审工作流",
            "它不是独立 Skill",
            "多个 AI、PM / Reviewer、产品大师、MAGI",
            "流程控制位",
            "产品主笔位",
            "挑战者位",
            "Round 0：前置依赖确认",
            "阶段一：方案共识",
            "阶段二：交互、图形或原型验证",
            "阶段三：PRD / Backlog / 上下文包定稿",
            "共识",
            "分歧",
            "必改",
            "待确认",
            "owner",
            "验证方式",
            "scripts/check_product_deliverable.py --kind product-review",
            "把外部仓库的工具调用、平台机制、看门狗脚本或领域专项规则当作本仓库默认能力",
        ],
    )
    and has_all(
        product_prd,
        [
            "product-deliberation-workflow.md",
            "多视角或合议评审是否有触发原因、阶段门、共识、分歧、必改、建议、待确认、owner 和验证方式",
        ],
    )
    and has_all(
        product_prd_quality_gates,
        [
            "合议式产品评审",
            "product-deliberation-workflow.md",
            "scripts/check_product_deliverable.py --kind product-review",
            "触发原因、阶段门、共识、分歧、必改、建议、待确认、owner、验证方式和下一步去向",
        ],
    ),
)
check(
    "product methodology keeps functional allocation boundary",
    has_all(
        product_architecture,
        [
            "能力不是头脑风暴出来的功能点清单",
            "某对象或主体对外提供的可见、有价值交互行为",
            "上层目标或父能力来源",
            "目标用户/主执行者",
            "可观察结果和验收口径",
            "不要只写按钮、页面、内部系统动作或技术组件",
            "每个能力应能追溯到产品目标、父能力或上层业务对象",
            "无法追溯的能力先放入观察池或非目标",
            "外显价值行为和正逆追溯",
        ],
    ),
)
check(
    "product methodology keeps brainstorming as exploration discipline",
    has_all(
        product_architecture,
        [
            "产品头脑风暴纪律",
            "思考伙伴",
            "不是交付物生成器",
            "问题探索",
            "方案发散",
            "假设挑战",
            "HMW",
            "第一性原理",
            "反转/逆向头脑风暴",
            "OODA",
            "删除或少做选项",
            "下一步验证动作",
            "不把发散想法直接写成 PRD 或研发任务",
        ],
    ),
)
check(
    "product methodology keeps low cost generation constraints",
    has_all(
        product_architecture,
        [
            "低成本生成场景的约束",
            "每个功能、页面、实验或自动生成方案必须回到目标、假设、非目标、成功指标和停止条件",
            "是否存在更低成本、注意力消耗更小的验证方式",
        ],
    ),
)
check(
    "product routing exposes brainstorming exploration discipline",
    has_all(
        product_routing,
        [
            "产品头脑风暴、问题探索、方案发散、假设挑战、HMW、第一性原理、OODA、逆向头脑风暴",
            "产品头脑风暴纪律",
            "头脑风暴结论",
            "删除/少做选项",
            "下一步验证动作",
            "不直接变研发任务",
        ],
    ),
)
check(
    "product methodology keeps AI-shaped readiness as internalized review",
    has_all(
        product_architecture,
        [
            "AI-shaped 产品工作成熟度",
            "不安装外部 advisor、不照搬外部术语",
            "优势、流程、上下文、编排、责任和指标",
            "AI 要带来什么业务优势，而不只是省时间或多写文档",
            "哪些产品发现、需求评审、验证、决策或复盘流程真的被改了",
            "事实、约束、术语、证据标准和上下文边界已经结构化",
            "高频产品任务能重复运行、保留输入输出、记录判断依据并可追溯",
            "AI 输出由谁验证、谁拍板、谁承担结果责任",
            "验证周期、决策质量、返工率、错误率和学习速度",
            "若竞品购买同类工具即可复制，不能写成战略差异化",
            "不要把 `AI-shaped`、`Context Design`、`Agent Orchestration` 等术语直接写进团队口号",
        ],
    ),
)
check(
    "product methodology keeps AI product intention and user tension gate",
    has_all(
        product_architecture,
        [
            "AI 产品发心、定位和用户张力门禁",
            "公开文章、离职复盘或内部转述只能作为反模式和问题框架来源",
            "主发心是什么",
            "首批服务谁",
            "先做什么",
            "用户收益是否大于新增负担",
            "权力与责任如何平衡",
            "如何灰度和止损",
            "AI 产品发心与定位卡",
            "战略叙事、行业风口、发布会表达、竞品对标或组织意志",
            "保留必要的协作弹性",
        ],
    ),
)
check(
    "product methodology keeps product manager basics as architecture calibration",
    has_all(
        product_architecture,
        [
            "产品经理基础方法校准",
            "把基础方法升格为复杂业务产品可交付能力",
            "文档分型",
            "流程表达",
            "原型与注释",
            "产品架构图",
            "用户研究",
            "需求管理",
            "数据分析",
            "技术与项目协作",
            "行业商业分析与知识库",
            "对象模型、规则矩阵、数据验收、跨团队交接、风险治理和领域知识",
            "不把基础岗位清单替代复杂产品架构",
        ],
    ),
)
check(
    "product source map records AI complexity article reference",
    has_all(
        product_source_map,
        [
            "代码不再稀缺，稀缺的是你如何对抗复杂度",
            "https://mp.weixin.qq.com/s/TxU2D0Plf__Xh-yUD2zjPA",
            "实现成本下降、复杂度/注意力成本上升",
        ],
    ),
)
check(
    "product source map keeps topic index",
    has_all(
        product_source_map,
        [
            "## 来源主题索引",
            "支付系统与支付账本",
            "卡组织、发卡与 VCC",
            "全球支付与基础设施",
            "收单、争议与风险运营",
            "AI / Skill / 通用复杂度",
            "产品头脑风暴与假设挑战",
            "AI Native 产品上下文",
            "AI 产品发心与定位复盘",
            "模糊需求到可开发系统",
            "产品洞察与机会雷达",
            "Backlog 决策与机会收敛",
            "产品图形化与服务蓝图",
            "AI-shaped 产品工作成熟度",
            "产品经理方法论与基础能力",
            "需求分析与设计基础",
            "AI 辅助 PRD 与问题地图",
            "PRD 文档质量治理",
            "通用产品架构与业务驱动验证",
            "产品价值 / 成本函数与业务同质性",
            "官方规则与监管",
        ],
    ),
)
check(
    "product source map and README record product brainstorming boundary",
    has_all(
        product_source_map,
        [
            "产品头脑风暴与假设挑战",
            "`product-brainstorming` Skill 原文中文版",
            "https://mp.weixin.qq.com/s/cz-9HnmlC_VNcVpdd_e0Vw",
            "AIML实验室",
            "2026-04-21",
            "knowledge-work-plugins/product-management/skills/product-brainstorming/SKILL.md",
            "GitHub raw 原始 `SKILL.md` 未及时返回",
            "问题探索、方案发散、假设挑战、HMW、第一性原理、类比、反转、OODA 和逆向头脑风暴",
            "不把头脑风暴输出直接写成 PRD、Backlog 或研发任务",
        ],
    )
    and has_all(
        "README.md",
        [
            "`product-brainstorming` Skill 原文中文版",
            "产品头脑风暴、问题探索、方案发散和假设挑战纪律",
            "HMW、第一性原理、类比、反转、OODA 和逆向头脑风暴",
            "本轮 GitHub raw 原始文件未成功拉取",
            "不把头脑风暴结果直接写成 PRD、Backlog 或研发任务",
        ],
    ),
)
check(
    "product source map records AI product intention article boundary",
    has_all(
        product_source_map,
        [
            "AI 产品发心与定位复盘",
            "阿里内网万言离职书〈置身钉内〉原文，已刷屏",
            "https://mp.weixin.qq.com/s/_D20O0vpPXjSzjAKJmBYuA",
            "Corgi/滕雅辛",
            "爬梯意外簿",
            "Codex in-app Browser 的 Playwright 接口",
            "公开转述/OCR 复盘材料",
            "AI 产品发心、定位、用户张力、真实工作流、灰度止损和反模式门禁",
            "不把文章内容写成钉钉/ONE 官方事实",
        ],
    ),
)
check(
    "product source map records fuzzy requirement to developable system boundary",
    has_all(
        product_source_map,
        [
            "模糊需求到可开发系统",
            "从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战",
            "https://mp.weixin.qq.com/s/HzbdrmNkT-OTRKdQh0c0Ug",
            "KEEN的创享",
            "2026-06-04 21:39",
            "移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文",
            "结构化需求、业务流、对象规则、原型说明和开发交接秩序",
            "不把文章示例项目写成通用产品模板",
        ],
    )
    and has_all(
        "README.md",
        [
            "从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战",
            "产品架构专家",
            "不复制原文、项目案例、页面设计、图片、提示词或作者表达",
        ],
    ),
)
check(
    "product source map and README record product insight article boundary",
    has_all(
        product_source_map,
        [
            "产品洞察与机会雷达",
            "product-insight-analyst.md",
            "为什么你的 AI 只能写总结，别的产品经理已经用AI在挖需求机会了？附skill模板和调试方法",
            "https://mp.weixin.qq.com/s/jsuVbuvKJxEXl8dZyzh23g",
            "糖糖",
            "产品AI力学",
            "2026-04-23 19:30:00 Asia/Shanghai",
            "普通 curl/mobile UA 返回微信验证页",
            "Chrome headless",
            "资料资产化",
            "客户/竞品/标杆",
            "机会雷达",
            "证据与推理链",
            "不复制原文、模板正文、固定路径、外部 Skill 名称体系、作者表达或标题传播话术",
        ],
    )
    and has_all(
        "README.md",
        [
            "产品洞察/机会雷达",
            "为什么你的 AI 只能写总结，别的产品经理已经用AI在挖需求机会了？附skill模板和调试方法",
            "product-insight-analyst.md",
            "产品洞察、资料资产化、客户/竞品/标杆情报分拣、机会雷达、证据与推理链和产品负责人决策边界",
            "普通 curl/mobile UA 返回微信验证页",
            "Chrome headless",
            "不复制原文、模板正文、固定路径、外部 Skill 名称体系、作者表达或标题传播话术",
        ],
    ),
)
check(
    "product source map records AI Native product context boundary",
    has_all(
        product_source_map,
        [
            "AI Native 产品上下文",
            "放下 PRD：写给AI Native时代的产品经理朋友们",
            "https://mp.weixin.qq.com/s/5TEAxFYueNc6MD5ngKEgGg",
            "大数据随笔",
            "2026-05-25 18:00:00",
            "PRD 从静态翻译文档转为可运行证据、对象规则、验收种子和工程交接门禁的上下文包",
            "Product Builder、业务 owner + Agent、业务 dogfooding、MVP/原型 harden 和产品侧交接",
            "端到端 GSD/CAD 准入与 AI 工具编排交给 `ai-native-engineering-workflow`",
            "不把“放下 PRD”理解为跳过产品语义、评审、留痕、合规和验收",
        ],
    )
    and has_all(
        "README.md",
        [
            "放下 PRD：写给AI Native时代的产品经理朋友们",
            "PRD 从静态翻译文档升级为上下文包、验收种子和工程交接门禁",
            "不把“放下 PRD”理解为跳过产品语义、评审、留痕、合规和验收",
        ],
    ),
)
check(
    "product source map and README record backlog decision article boundary",
    has_all(
        product_source_map,
        [
            "Backlog 决策与机会收敛",
            "po-backlog-manager.md",
            "有了洞察还不够，产品负责人真正值钱的是 Backlog 决策",
            "https://mp.weixin.qq.com/s/stj1HjCpaG5PzXhxfxlWSg",
            "糖糖",
            "产品AI力学",
            "2026-04-10 07:30:00 Asia/Shanghai",
            "公开 HTML 读取标题、作者、发布时间和正文",
            "BV/EE",
            "业务/用户/工程三桌校验",
            "P0/P1/P2",
            "User Story",
            "AC",
            "技术现实主义",
            "拒绝或延后理由",
            "不复制原文图片、外部 Skill 名称体系、作者表达、标题传播话术或前置文章内容",
        ],
    )
    and has_all(
        "README.md",
        [
            "有了洞察还不够，产品负责人真正值钱的是 Backlog 决策",
            "洞察/机会清单到 Backlog 决策",
            "BV/EE",
            "业务/用户/工程三桌校验",
            "User Story、AC、技术现实主义和 P0/P1/P2 排序",
            "机会收敛、拒绝/延后理由、研发可执行边界和决策偏好自检",
            "不复制原文图片、外部 Skill 名称体系、作者表达或标题传播话术",
        ],
    ),
)
check(
    "product source map records product manager methodology book boundary",
    has_all(
        product_source_map,
        [
            "产品经理方法论与基础能力",
            "产品经理方法论：构建完整的产品知识体系",
            "https://m.dushu.com/book/13884861/",
            "赵丹阳",
            "人民邮电出版社",
            "9787115571144",
            "2026-06-02",
            "公开图书页、内容简介、作者简介和目录",
            "文档分型、流程图、原型图、产品架构图、用户研究、需求管理、数据分析、技术协作、项目管理、行业/商业分析、产品实践、学习方法和职业进阶",
            "不复制书籍正文、章节内容、示例、图表、训练材料或作者表达",
            "不把基础岗位知识体系替代复杂业务产品架构专家能力",
        ],
    ),
)
check(
    "product source map records AI-shaped readiness advisor boundary",
    has_all(
        product_source_map,
        [
            "AI-shaped 产品工作成熟度",
            "现在我敢评测这个 skill 了，产品负责人来看看这个自评卡吧",
            "https://mp.weixin.qq.com/s/ZUwtGYYTzt-c2YRXn8ryJw",
            "糖糖",
            "产品AI力学",
            "2026-05-02 10:00:00",
            "ai-shaped-readiness-advisor",
            "deanpeters/Product-Manager-Skills",
            "https://raw.githubusercontent.com/deanpeters/Product-Manager-Skills/main/skills/ai-shaped-readiness-advisor/SKILL.md",
            "Context Design、Agent Orchestration、Outcome Acceleration、Team-AI Facilitation 和 Strategic Differentiation",
            "不安装该 Skill",
            "不复制交互协议、评分 rubrics、示例案例、关联 Skill 链接或外部执行流程",
        ],
    ),
)
check(
    "product source map records requirements analysis and design source",
    has_all(
        product_source_map,
        [
            "需求分析与设计基础",
            "需求分析和设计活动关键要点总结",
            "https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q",
            "软件需求分析和设计",
            "常识",
            "2026-05-26 10:29:23",
            "功能定义、功能分配追溯、需求分析外部视角和设计内部视角的分工",
            "不复制原文中的 GJB 章节表述、推荐书目、课程机构推荐或作者表达",
            "不把军标/适航语境写成通用产品强制流程",
        ],
    ),
)
check(
    "source maps and README record architecture demand analysis source",
    has_all(
        product_source_map,
        [
            "需求分析与产品定义",
            "架构30：架构思维：需求分析",
            "https://mp.weixin.qq.com/s/B8Rap_MmAKmVN3f7eAnvCw",
            "开心就好TF",
            "2026-06-07 09:34:00 Asia/Shanghai",
            "2026-06-09",
            "公开 HTML 读取标题、作者、发布时间和正文",
            "根源需求、产品定义、产品边界、上下游分工、稳定点 / 变化点和边界坐标门禁",
            "不复制原文、案例、作者表达、标题传播话术或时间投入比例",
            "不把文章观点写成组织制度、项目事实或执行授权",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "微信公众号文章：架构30：架构思维：需求分析",
            "https://mp.weixin.qq.com/s/B8Rap_MmAKmVN3f7eAnvCw",
            "开心就好TF",
            "2026-06-07 09:34:00 Asia/Shanghai",
            "2026-06-09",
            "公开 HTML 读取标题、作者、发布时间和正文",
            "用于 `product-design.md` 的需求澄清门禁",
            "`system-analysis-design.md` 的系分前需求分析门禁",
            "AI Native / 产品专家的需求分析结论卡",
            "不把单篇文章观点写成组织制度、项目事实、执行授权",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "架构30：架构思维：需求分析",
            "需求分析协同门禁",
            "PRD / 系分预审和 GSD Round 0",
            "公开 HTML 读取标题、作者、发布时间和正文",
            "根源需求、产品定义、产品边界 / 上下游分工、稳定点 / 变化点必须带边界坐标",
            "不把文章观点写成组织制度、当前项目事实或执行授权",
        ],
    )
    and has_all(
        "README.md",
        [
            "架构30：架构思维：需求分析",
            "需求分析协同门禁、根源需求、产品定义、产品边界、上下游分工、稳定点 / 变化点、边界坐标",
            "公开 HTML 读取标题、作者、发布时间和正文",
            "不把单篇文章观点写成组织制度、项目事实、执行授权或架构师必须越过产品 owner 的理由",
        ],
    ),
)
check(
    "source maps and README record requirements standards sources",
    has_all(
        product_source_map,
        [
            "需求标准与可验证 PRD",
            "标准不是摆设",
            "需求是软件的根本",
            "https://mp.weixin.qq.com/s/W44YHT-9bUCrSjsrZIYItw",
            "https://mp.weixin.qq.com/s/MO8EsLHm9QNauNLDQ1Z05Q",
            "AIIIIlIIII",
            "2026-05-23 07:24:00",
            "2026-05-26 06:21:00",
            "需求条目标准、图文追踪、系统/外部需求未确认不下钻、衍生需求、可验证性和可追踪性门禁",
            "不把文章观点写成产品团队制度、合规结论或执行授权",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "微信公众号文章：标准与需求基线",
            "[013] 标准不是摆设",
            "[014] 85%返工都是需求的锅",
            "https://mp.weixin.qq.com/s/W44YHT-9bUCrSjsrZIYItw",
            "https://mp.weixin.qq.com/s/MO8EsLHm9QNauNLDQ1Z05Q",
            "AIIIIlIIII",
            "通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文",
            "需求基线和高层/详细设计分工",
            "规则原因/示例/验证方式与防御式编程",
            "需求驱动测试门禁",
            "不把单篇文章写成通用合规结论、项目制度或 Execution Grant",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "[013] 标准不是摆设",
            "[014] 85%返工都是需求的锅",
            "需求基线稳定性、需求 / 设计 / 编码标准门禁、Spec 模板和测试门禁",
            "需求条目质量、图文追踪、衍生需求、系统需求未确认不下钻",
            "HLR/LLR 分工、需求驱动测试、编码规则原因/示例/验证方式和防御式编程门禁",
            "不复制原文、适航/DO-178C 语境、标题比例、案例、作者表达或标准条文",
        ],
    )
    and has_all(
        "README.md",
        [
            "[013] 标准不是摆设",
            "[014] 85%返工都是需求的锅",
            "需求基线稳定性、需求标准、设计标准、编码标准、HLR/LLR 分工、图文追踪、衍生需求、需求驱动测试、防御式编程和标准可执行性门禁",
            "不复制原文、适航/DO-178C 语境、标题比例、案例、作者表达或标准条文",
            "不把单篇文章写成通用合规结论、项目制度或 Execution Grant",
        ],
    ),
)
check(
    "source maps and references record system DNA and life-like architecture sources",
    has_all(
        ai_native_workflow_skill,
        [
            "产品 / 系统 DNA",
            "product-to-engineering-lifecycle.md",
        ],
    )
    and has_all(
        ai_native_product_to_engineering,
        [
            "Round 0B：产品 / 系统 DNA 门禁",
            "产品 / 系统 DNA 固化核心对象、不变量、状态流转、责任边界、演化规则和验证方式",
            "没有产品 / 系统 DNA，就按功能清单拆研发任务",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "系统生长顺序与生命化架构组",
            "软件工程最大的 Bug：我们把系统生长顺序做反了",
            "为什么优秀架构越来越像生命？",
            "霍旭东",
            "ThinkingInDev",
            "系统 DNA、核心不变量、状态流转、边界、演化规则和事故沉淀式架构",
            "复杂系统分化、事件驱动协作、失败可恢复、可观测性、自治/协作平衡",
        ],
    )
    and has_all(
        product_source_map,
        [
            "产品 DNA 与规则先行",
            "软件工程最大的 Bug：我们把系统生长顺序做反了",
            "为什么优秀架构越来越像生命？",
            "产品 DNA、核心对象、业务不变量、生命周期 / 状态、责任边界、演化规则、验收方式",
            "功能先行、规则后补",
            "不把产品 DNA 写成替代用户研究、业务 owner 确认、合规确认、系统设计或 Execution Grant",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "软件工程最大的 Bug：我们把系统生长顺序做反了",
            "为什么优秀架构越来越像生命？",
            "产品 / 系统 DNA 门禁",
            "事故沉淀式架构",
            "复杂系统分化",
            "事件驱动协作",
            "自治/协作平衡",
        ],
    )
    and has_all(
        "README.md",
        [
            "软件工程最大的 Bug：我们把系统生长顺序做反了",
            "为什么优秀架构越来越像生命？",
            "产品 / 系统 DNA 门禁、核心不变量、状态流转、责任边界、演化规则、验证方式",
            "不把文章观点写成组织制度、项目事实、技术选型结论、执行授权或 AI 自主扩大范围的理由",
        ],
    )
    and has_all(
        "senior-software-architect/references/architecture.md",
        [
            "系统 DNA 先于实现",
            "生命化复杂系统治理要求",
            "事故沉淀式架构",
        ],
    )
    and has_all(
        "product-architecture-expert/references/product-architecture-methodology.md",
        [
            "产品 DNA",
            "功能先行、规则后补",
            "产品 DNA 不是完整大模板",
        ],
    )
    and has_all(
        "product-architecture-expert/references/product-prd-template.md",
        [
            "产品 DNA 卡 D-001",
            "对象、状态、规则或责任边界会长期演化",
            "默认 SVG",
        ],
    ),
)
check(
    "source maps and README record business architecture product value sources",
    has_all(
        product_source_map,
        [
            "产品价值 / 成本函数与业务同质性",
            "所有的技术架构，本质上都是业务架构",
            "兑现那个问题“产品需要做什么”",
            "大象无棱",
            "2026-04-25 09:32",
            "2026-06-10 09:11",
            "价值 / 成本函数、主要矛盾、用户逻辑、业务同质性、技术平台不是产品",
            "Codex in-app Browser 的 Playwright 接口",
            "不复制原文、故事经历、比喻、图片",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "业务架构 / 技术架构同质性来源",
            "技术架构服务业务架构、业务同质性、技术平台不是产品和复制成本门禁",
            "架构批准或 Execution Grant",
        ],
    )
    and has_all(
        ai_native_source_map,
        [
            "业务 / 产品 / 技术交叉准入",
            "技术架构服务业务复制、业务同质性、价值函数、成本函数、主要矛盾",
            "不得把技术平台、AI 原型或架构升级直接等同于产品价值",
        ],
    )
    and has_all(
        "README.md",
        [
            "业务 / 产品 / 技术交叉准入参考来源",
            "业务同质性、价值函数、成本函数、主要矛盾",
            "Codex in-app Browser 的 Playwright 接口",
            "架构批准或 Execution Grant",
        ],
    ),
)
check(
    "AI Native source map records software design philosophy complexity gate",
    has_all(
        ai_native_source_map,
        [
            "《软件设计的哲学》：复杂性的本质与模块化设计",
            "https://mp.weixin.qq.com/s/gXhOwvKH5t6BxsxcoqUS2w",
            "《软件设计的哲学》：实践智慧与超越代码的哲学",
            "https://mp.weixin.qq.com/s/J9d5Ws6rIdsATPbT-UutAA",
            "复杂度投资门禁、AI 战术化编码风险、人类理解责任和 Coding Loop 设计质量回看",
            "深安斯帕克",
            "南山斯帕克",
            "2026-06-22 10:38:07",
            "2026-06-23 07:47:00",
            "移动端微信 UA `curl` 公开 HTML 读取标题、作者、账号、发布时间和正文",
            "测试变绿、PR 变多或代码更短",
            "浅模块、直通包装、公共知识泄露、多文件小改动、AI 注释噪声和只为过测试的战术实现",
            "可以吸收复杂度投资门禁、深模块 / 浅模块、信息隐藏、设计两次",
            "不得把读书笔记写成官方标准、吞异常依据、执行授权、测试通过、CR 结论或 AI 自动扩大范围的理由",
        ],
    ),
)
check(
    "product source map records diagram and service blueprint sources",
    has_all(
        product_source_map,
        [
            "产品图形化与服务蓝图",
            "架构师必备--让AI画架构图",
            "https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg",
            "方兴集",
            "2026-04-30 16:28:31",
            "AI + draw.io 的自然语言生成、文档转图、图像参考、版本历史、可编辑 draw.io XML 和本地模型/凭据边界",
            "NN/g 文章《UX Mapping Methods Compared: A Cheat Sheet》",
            "https://www.nngroup.com/articles/ux-mapping-cheat-sheet/",
            "empathy map、customer journey map、experience map 和 service blueprint 的适用边界",
            "NN/g 文章《Service Blueprints: Definition》",
            "https://www.nngroup.com/articles/service-blueprints-definition/",
            "服务蓝图把客户动作、前台动作、后台动作、支撑流程和证据/物料关联到特定用户旅程",
            "draw.io 官方 GitHub 集成文档",
            "https://www.drawio.com/docs/integrations/github/",
            "可编辑图资产与代码/文档同库维护",
        ],
    ),
)
check(
    "product source map records PRD document quality article",
    has_all(
        product_source_map,
        [
            "B端产品经理实战经验分享系列 - 如何写出高质量的需求文档",
            "https://mp.weixin.qq.com/s/_KU0j5sy1HBMdx03bhlYGg",
            "AI产品经理老李",
            "2026-04-22 08:00",
            "2026-06-01",
            "需求文档质量治理",
            "PRD/MRD/BRD 类型区分",
            "版本记录、变更同步和评审闭环",
            "不复制原文案例、指标数字、图片、排版或作者表达",
        ],
    ),
)
check(
    "product source map records PRD AI prescan article",
    has_all(
        product_source_map,
        [
            "完整不等于可测：需求评审的四个AI新维度",
            "https://mp.weixin.qq.com/s/7EiFz1Oka1tYQmfbBferQg",
            "Maywen测开AI手记",
            "2026-06-08 12:52:41 Asia/Shanghai",
            "移动端微信 UA 读取标题、作者、发布时间和正文",
            "公开内容用于参考需求评审前 AI 预扫描",
            "完整性、一致性、可测试性和二义性",
            "AI 只列疑似问题和追问点",
            "人工过滤、排序和 owner 决策",
            "不把预扫描替代正式需求评审",
        ],
    ),
)
check(
    "AI Native source map records PRD AI prescan article",
    has_all(
        ai_native_source_map,
        [
            "完整不等于可测：需求评审的四个AI新维度",
            "https://mp.weixin.qq.com/s/7EiFz1Oka1tYQmfbBferQg",
            "PRD 评审会前 AI 预扫描",
            "完整性、一致性、可测试性、二义性四维预扫描",
            "疑似问题清单",
            "人工过滤/排序和 owner 决策边界",
            "不把 AI 预扫描写成正式评审、测试设计或产品决策的替代品",
        ],
    ),
)
check(
    "AI Native source map records Anthropic internal skills practice source",
    has_all(
        ai_native_source_map,
        [
            "重磅！Anthropic内部Skills经验公开了！",
            "https://mp.weixin.qq.com/s/FCKdRHxi9c6Vby2ZRKjVTw",
            "AI Native 研发流程和仓库级 Skill 治理",
            "Skill 类型接入门禁、渐进式加载、gotchas 优先、验证优先、脚本化复用、setup 缺口、组合边界和高风险 guardrail",
            "Datawhale",
            "Anthropic团队",
            "2026-06-07 22:03:28 Asia/Shanghai",
            "2026-06-11 通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者、发布时间和正文",
            "不复制原文、图片、内部案例细节、Claude Code 专用变量、hooks、marketplace、usage measurement 机制或作者表达",
            "不把 Anthropic 内部做法写成 Codex 当前能力、组织制度、执行授权、默认持久化记忆或默认外部插件机制",
            "可以吸收 Skill 类型接入门禁、单一职责、description 触发准确性、渐进式加载、gotchas 优先、验证优先、脚本化复用、setup 缺口、组合边界、高风险 guardrail 和 advisory quality audit",
            "不得把 Claude Code 内部 hooks、marketplace、持久化目录、usage measurement、内部团队机制、单篇文章经验或行数经验写成本仓库默认能力或硬性失败规则",
        ],
    ),
)
check(
    "AI Native source map and README record good skill design methodology source",
    has_all(
        ai_native_source_map,
        [
            "设计一个好 Skill，通用方法论",
            "https://mp.weixin.qq.com/s/KEDcjuDFFAeeL0iqsHejIQ",
            "仓库级 Skill 质量治理",
            "单一职责、description 触发准确性、指令可验证、避免冲突规则、上下文窗口节制、渐进式加载、何时使用、迭代测试和把 Skill 当代码管理",
            "雅东Talk",
            "2026-06-10 18:00:00 Asia/Shanghai（UTC 2026-06-10 10:00:00）",
            "2026-06-11 通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、页面时间字段和正文",
            "metadata 瘦身",
            "advisory audit",
            "不复制原文、图片、案例、标题传播话术、作者表达或平台宣传",
            "不把单篇文章写成新增顶层 Skill、硬性行数失败、自动安装外部工具或执行授权",
            "可以吸收 Skill 类型接入门禁、单一职责、description 触发准确性、渐进式加载、gotchas 优先、验证优先、脚本化复用、setup 缺口、组合边界、高风险 guardrail 和 advisory quality audit",
            "不得把 Claude Code 内部 hooks、marketplace、持久化目录、usage measurement、内部团队机制、单篇文章经验或行数经验写成本仓库默认能力或硬性失败规则",
        ],
    )
    and has_all(
        "README.md",
        [
            "设计一个好 Skill，通用方法论",
            "https://mp.weixin.qq.com/s/KEDcjuDFFAeeL0iqsHejIQ",
            "仓库级 Skill 质量治理",
            "`AI Native 研发流程编排` metadata 瘦身",
            "单一职责、description 触发准确性、指令可验证、避免冲突、上下文窗口节制、渐进式加载、何时使用、迭代测试和把 Skill 当代码管理",
            "2026-06-11 已通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、页面时间字段和正文",
            "雅东Talk",
            "2026-06-10 18:00:00 Asia/Shanghai（UTC 2026-06-10 10:00:00）",
            "advisory audit",
            "不把单篇文章写成新增顶层 Skill、硬性行数失败、自动安装外部工具或执行授权",
        ],
    ),
)
check(
    "README records PRD AI prescan source boundary",
    has_all(
        "README.md",
        [
            "完整不等于可测：需求评审的四个AI新维度",
            "https://mp.weixin.qq.com/s/7EiFz1Oka1tYQmfbBferQg",
            "完整性、一致性、可测试性、二义性四维度预扫描",
            "疑似问题",
            "人工过滤/排序/owner 决策边界",
            "不把 AI 预扫描写成正式需求评审、QA 设计或产品 owner 决策的替代品",
        ],
    ),
)
check(
    "product source map records business-driven product verification sources",
    has_all(
        product_source_map,
        [
            "产品经理别再只让 AI 写 PRD 了，先把用户反馈整理成一张问题地图",
            "https://mp.weixin.qq.com/s/sY6cw6wE5ePyrZmRYbXApg",
            "用户反馈证据整理、问题地图、原始反馈到真实问题的转换",
            "Impact Mapping 官方图书页",
            "https://www.impactmapping.org/book.html",
            "Dan North 文章《Introducing BDD》",
            "https://dannorth.net/blog/introducing-bdd/",
            "目标、参与方、行为影响和交付物之间的验证链路",
            "Given / When / Then 验收标准",
            "产品侧验收种子交接矩阵",
            "Atlassian Product Requirements",
            "https://www.atlassian.com/agile/product-management/requirements",
            "https://swehb.nasa.gov/x/AwIfBg",
            "需求ID",
            "验收种子ID",
            "质量属性ID",
        ],
    ),
)
check(
    "product source map and README record deliberation workflow sources",
    has_all(
        product_source_map,
        [
            "产品合议评审与多 Agent PRD",
            "我让3个AI吵了一整天架，它们把PRD写完了",
            "https://mp.weixin.qq.com/s/13wn5wS8AwyMNBrMQpTyEg",
            "Kira2red",
            "产品异兽 Prod.Monster",
            "2026-05-17 10:05:10 Asia/Shanghai",
            "公开 HTML 读取标题、作者、发布时间和正文",
            "product-deliberation-workflow.md",
            "Controller / PM / Reviewer 工作位",
            "强制阶段门",
            "用户确认点",
            "复杂度评估",
            "类型分流",
            "分批产出",
            "不复制原文、图片、外部平台工具调用、watchdog 脚本、车载专项规则、作者表达或标题传播话术",
            "Kira2red/magi-product",
            "https://github.com/Kira2red/magi-product",
            "Kira2red/Kira-product-monster-skills",
            "https://github.com/Kira2red/Kira-product-monster-skills",
            "不复制 OpenClaw/Hermes 专属命令",
            "不复制外部 Skill 结构",
            "不复制游戏 Skill",
        ],
    )
    and has_all(
        "README.md",
        [
            "我让3个AI吵了一整天架，它们把PRD写完了",
            "Kira2red/magi-product",
            "Kira2red/Kira-product-monster-skills",
            "product-deliberation-workflow.md",
            "Controller / PM / Reviewer 工作位",
            "强制阶段门",
            "分批产出",
            "证据审查和准出检查",
            "不复制原文、图片、外部平台工具调用、watchdog 脚本、车载专项规则、外部 Skill 结构",
        ],
    ),
)
check(
    "product routing exposes business-driven architecture handoff",
    has_all(
        product_routing,
        [
            "业务驱动架构交接 / 产品方案交给架构师",
            "业务驱动架构交接包",
            "验收种子到 TDD 交接",
            "验收种子交接矩阵",
            "质量属性种子",
            "用户要交给架构师继续设计或业务驱动架构交接",
        ],
    ),
)
check(
    "product routing exposes product manager methodology calibration",
    has_all(
        product_routing,
        [
            "产品经理方法论 / 产品专家基础能力补齐",
            "不把基础岗位清单替代复杂产品架构",
            "产品经理方法论、产品专家能力补齐、产品经理知识体系、基础工作法校准",
            "文档分型、流程表达、原型注释、产品架构图、用户研究、需求管理、数据分析、技术/项目协作、行业商业分析、知识库沉淀",
            "用户要补齐产品经理方法论或产品专家基础能力",
            "哪些能力需要提升到复杂业务对象、规则、验收和交接",
        ],
    ),
)
check(
    "product routing exposes AI-shaped readiness review",
    has_all(
        product_routing,
        [
            "AI 产品工作成熟度 / AI-shaped readiness / AI 工作流改造",
            "不安装外部 advisor，不把外部术语当团队结论",
            "AI 产品工作成熟度、AI-shaped readiness、产品团队 AI 工作流改造、AI 是否形成产品优势",
            "业务优势、流程变化、上下文结构化、可追溯任务、人工责任、验证周期/决策质量/返工率指标",
            "用户要评估 AI 产品工作成熟度或 AI-shaped readiness",
            "默认只借鉴方法，不安装或调用外部 Skill",
        ],
    ),
)
check(
    "product routing and PRD references expose product insight",
    has_all(
        product_routing,
        [
            "产品洞察 / 资料分析 / 机会雷达",
            "`product-insight-analyst.md`",
            "客户/竞品/标杆",
            "证据与推理链",
            "用户要基于资料、访谈、竞品、行业/政策或知识库做产品洞察、需求洞察或机会雷达",
            "没有材料的类别明确留白",
        ],
    )
    and has_all(
        product_prd,
        [
            "资料洞察转产品机会或 PRD 候选",
            "product-insight-analyst.md",
            "机会雷达和证据推理链",
            "当输入主要来自资料、访谈、竞品、行业/政策、标杆实践或知识库笔记时",
            "洞察是否有证据与推理链",
            "不能从资料摘要直接写功能范围",
        ],
    ),
)
check(
    "product routing and PRD references expose backlog decision",
    has_all(
        product_routing,
        [
            "Backlog 决策 / 机会清单优先级 / User Story/AC",
            "洞察太多、机会清单、需求池、路线图候选、Backlog 决策、优先级、P0/P1/P2、User Story、AC",
            "`po-backlog-manager.md`",
            "Backlog 决策包：BV/EE、业务/用户/工程三桌校验、P0/P1/P2、拒绝理由、User Story、AC、技术现实主义风险和待确认项",
            "用户要消化洞察、机会清单或需求池，做 Backlog 决策、优先级、User Story 或 AC",
            "输入归一化",
            "不要把洞察清单直接改写成研发任务",
        ],
    )
    and has_all(
        product_prd,
        [
            "机会清单/需求池转 Backlog、User Story 或 AC",
            "po-backlog-manager.md",
            "Backlog 优先级是否有依据",
            "P0/P1/P2 应能追溯到 BV/EE、业务/用户/工程三桌校验、拒绝或延后理由",
            "优先级：<P0/P1/P2；依据 BV/EE 和三桌校验>",
            "价值：<为什么现在值得做；不做会损失什么>",
            "依赖/风险：<数据、系统、合规、运营或工程确认方>",
            "它的 AC 能覆盖输入、输出、正常、边界、异常、不能接受情况和完成标准",
        ],
    ),
)
check(
    "product routing exposes AI Native product context handoff",
    has_all(
        product_routing,
        [
            "AI Native Product Builder / 业务 dogfooding / MVP harden / 放下 PRD",
            "`ai-native-product-context.md`",
            "不把 AI Demo 直接当需求",
            "不把产品上下文包当 Execution Grant",
            "AI Native Product Builder、业务 dogfooding、MVP/原型 harden、放下 PRD、PRD 可执行上下文、交给 AI Native 编排/架构师",
            "Hardened Candidate 门禁",
            "产品侧交接条件",
            "端到端流程和 GSD/CAD 准入交给 `ai-native-engineering-workflow`",
            "用户要 AI Native 产品流程、Product Builder、业务 dogfooding、MVP harden 或 PRD 可执行上下文",
        ],
    ),
)
check(
    "product AI Native context reference defines hardened candidate package",
    has_reference_header(product_ai_native_context)
    and has_all(
        product_ai_native_context,
        [
            "# AI Native 产品上下文包",
            "不是要求放弃 PRD",
            "AI Native 产品上下文包",
            "Hardened Candidate",
            "业务 owner",
            "验收种子",
            "Product Builder",
            "MVP / 原型 harden 门禁",
            "与 AI Native 编排和架构师的交接",
            "不得直接判定 GSD/CAD 准入或 Execution Grant",
            "GSD/CAD 准入结论由 `ai-native-engineering-workflow` 编排",
            "产品上下文包、Hardened Candidate 或 GSD Roadmap 都不是 Execution Grant",
            "不把“放下 PRD”写成跳过产品语义、评审、留痕、合规和验收",
        ],
    ),
)
check(
    "product AI Native context refines product verification handoff",
    has_all(
        product_ai_native_context,
        [
            "## 6A. AI Native 调用产品专家的细化能力",
            "产品侧只补产品事实和验收种子，不接管流程编排、测试实现或工程授权",
            "产品验证",
            "AC、Given-When-Then、可观察结果、验收 owner",
            "业务流程自动化",
            "数据分析",
            "模板脚手架输入",
            "发布业务验收",
            "已确认业务事实、MVP / 原型 / dogfooding 观察、合理假设、待确认项和范围外不做",
            "退回 Round 0 补齐",
            "不把 Demo、页面或功能清单包装成工程可执行输入",
        ],
    ),
)
check(
    "product methodology provides acceptance seeds for TDD handoff",
    has_all(
        product_architecture,
        [
            "### 5.2 验收种子到测试驱动设计",
            "验收种子交接矩阵",
            "需求ID",
            "质量属性ID",
            "业务前置条件",
            "可观察结果",
            "风险红线",
            "产品专家不替架构师写工程测试代码",
            "可代码化",
            "可观测化",
            "可评审化",
            "第一批失败测试候选",
        ],
    ),
)
check(
    "prompt fixtures cover business-driven handoff and validation",
    has_all(
        skill_eval_prompt_fixture,
        [
            "senior-should-system-design-business-driver-validation",
            "senior-should-map-business-driven-validation-to-tdd",
            "product-should-business-driven-architecture-handoff",
            "product-should-provide-acceptance-seeds-for-tdd",
            "业务驱动架构交接包",
            "质量属性场景",
            "可代码化、可观测化和可评审化",
        ],
    ),
)
check(
    "PRD generation gate points to semantic gate",
    has_all(product_prd, ["## 0.1 PRD 生成门禁", "产品语义门禁"]),
)
check(
    "PRD reference keeps document quality governance",
    has_all(
        product_prd,
        [
            "PRD 文档质量治理 / 文档过厚过薄 / 版本评审同步",
            "## 0.0 PRD 文档质量治理",
            "高质量 PRD 不是越长越好，也不是越短越好",
            "先定文档目标和读者",
            "PRD 说明要做什么和如何验收",
            "MRD 说明市场、客户机会和为什么做",
            "BRD 说明商业价值、投入产出和决策依据",
            "功能名不能替代需求",
            "需求变更必须更新版本号、影响范围、通知对象、当前评审结论和过程记录链接",
            "最终 PRD 不保留讨论过程、迭代草稿、AI prompt/回答轨迹、多角色争论或被拒方案展开",
        ],
    ),
)
check(
    "PRD references expose AI prescan four dimensions",
    has_all(
        product_prd_quality_gates,
        [
            "AI 预扫描四维度",
            "完整性",
            "一致性",
            "可测试性",
            "二义性",
            "疑似问题",
            "建议追问",
            "ACCEPT / REJECT / PENDING",
            "预扫描只负责找疑似问题和追问点",
            "不能替代正式需求评审、QA 测试设计或产品 owner 决策",
        ],
    )
    and has_all(
        product_prd,
        [
            "PRD / 需求评审会前预扫描",
            "完整性、一致性、可测试性、二义性四维度只产出疑似问题和追问点",
            "不能替代正式评审或 owner 决策",
        ],
    )
    and has_all(
        product_routing,
        [
            "需求评审、PRD 评审会前扫描、需求评审 Skill",
            "AI 预扫描疑似问题清单",
            "完整性/一致性/可测试性/二义性检查",
            "不把 AI 扫描结果当已确认缺陷",
        ],
    ),
)
check(
    "product PRD references keep requirement standards gate",
    has_all(
        product_prd_quality_gates,
        [
            "P0/P1 需求条目符合需求标准",
            "一个条目只表达一个可见业务事实或验收事实",
            "完整性、一致性、必要性、无二义性、可行性、可验证性和可追踪性",
            "图表不替代需求条目",
            "流程图、用例图、状态机图和表格必须有正文解释、需求 ID、规则编号或验收种子回链",
            "衍生需求、异常恢复、安全监控、状态异常处理和鲁棒性要求",
        ],
    )
    and has_all(
        product_prd,
        [
            "需求条目标准",
            "一个条目只表达一个外部可见业务事实、规则事实或验收事实",
            "P0/P1 条目必须可验证、可追踪、无二义性且不绑定内部实现",
            "系统需求、外部规则或业务 owner 未确认时",
            "不得只用图表达未确认的业务结论",
        ],
    ),
)
check(
    "AI Native PRD review consumes AI prescan without replacing owners",
    has_all(
        ai_native_prd_system_design_review,
        [
            "PRD AI 预扫描接入",
            "完整性",
            "一致性",
            "可测试性",
            "二义性",
            "预扫描输出只作为 `review_task` 的候选锚点和追问点",
            "ACCEPT",
            "REJECT",
            "PENDING",
            "AI 预扫描不能替代正式 PRD 评审、QA 测试设计、业务 owner 决策或架构 owner 判断",
            "未确认的疑似问题继续留在评审报告、Decision Log 或任务计划",
        ],
    ),
)
check(
    "PRD reference keeps feedback-to-problem gate",
    has_all(
        product_prd,
        [
            "用户反馈整理成 PRD",
            "反馈到问题的证据链",
            "功能请求不是问题定义",
            "原始反馈、真实问题、使用场景、影响范围、证据强度和潜在机会",
            "AI 初稿只能作为聚类和表格化辅助",
        ],
    ),
)
check(
    "PRD reference keeps generation completion and compliance review modes",
    has_all(
        product_prd,
        [
            "product-prd-template.md",
            "product-prd-quality-gates.md",
            "product-prd-financial-appendix.md",
            "product-prd-operations-and-data.md",
            "## 0.2 PRD 生成、补全与符合性评审模式",
            "生成、补全还是评审",
            "符合项 / 必改 / 建议 / 可选",
            "## 0.3 PRD 连环追问与原型反推",
            "PRD 是产品思考结构，不只是文档模板",
            "问题 ID、待确认问题、影响章节、风险等级、建议选项、未确认前处理",
            "原型、HTML、页面截图、交互稿或页面说明",
            "错误截图、日志截图、测试失败截图不是本节的输入材料",
            "用户故事是否包含角色、能力和价值",
            "成功指标是否可衡量",
            "验收标准是否能回到需求 ID",
            "scripts/check_product_deliverable.py --kind prd",
            "脚本发现的结构缺口合并进“必改”",
        ],
    ),
)
check(
    "PRD template keeps acceptability and priority gates",
    has_all(
        product_prd_template,
        [
            "反馈证据与问题地图",
            "信息传递流程",
            "事实 -> 判断 -> 决策 -> 承诺 -> 验证",
            "描述可靠性必须可见",
            "表达结构选择",
            "图形化视图选择",
            "用例图：用于说明角色、系统边界、核心用例和责任主体",
            "流程图：用于说明主流程、逆向流程、异常流程和人工兜底",
            "泳道图：用于说明用户、运营、风控、财务、外部机构和系统之间的交接",
            "状态机图：用于说明对象生命周期、状态迁移、触发事件、守卫条件、终态和回滚",
            "每张图必须说明图形目标、目标读者、对应 PRD 章节、关键假设、待确认项和与验收/规则的追踪关系",
            "表格只用于比较、矩阵或追踪",
            "原始反馈",
            "真实问题",
            "证据强度",
            "处理结论",
            "优先级口径",
            "P0：没有它不能上线",
            "P1：核心体验或主流程必须具备",
            "P2：增强体验、运营效率或后续扩展能力",
            "产品到架构交接",
            "业务驱动架构交接",
            "product-architecture-methodology.md",
            "假设/问题ID",
            "默认 PRD 主模板",
            "需求概览",
            "背景、问题与证据",
            "目标、范围与非目标",
            "用户、主体与角色/场景",
            "场景、能力与功能",
            "需求链卡片",
            "对象、流程、图形视图与规则",
            "数据、权限、风险与待确认",
            "验收与产品到架构交接",
            "附录按需展开",
            "精简输出规则",
            "来源/问题ID",
            "需求ID",
            "验收种子ID",
            "质量属性ID",
            "验收种子交接矩阵",
            "每个 P0/P1 需求必须能回到问题、目标、场景、规则和验收",
            "每个进入开发候选的需求必须能关联场景、能力或功能、关键规则和验收种子",
            "正式 PRD 以最终标准版本为主",
            "文档控制只保留当前版本号、状态、owner、发布日期、评审结论摘要和过程记录链接",
            "最终 PRD 不保留“第一版/第二版怎么改”",
            "默认不展开文档控制、完整状态机、字段字典、规则矩阵、权限矩阵、非功能、发布运营和金融资金全表",
            "主文档优先用短句、卡片和编号流程帮助扫读",
            "默认不强制每份 PRD 生成图片",
            "多角色、多对象、多状态、多团队交接或高风险评审时，至少选择一张关键图帮助建立共同理解",
            "发布后验证",
            "业务驱动架构交接包",
            "可代码化、可观测化、可评审化",
            "product-prd-quality-gates.md",
            "product-prd-financial-appendix.md",
            "product-prd-operations-and-data.md",
            "正式评审、提交前检查、CR、触发验证或符合性评审时读取 `product-prd-quality-gates.md`",
            "文档目标、目标读者和文档类型",
            "不能把轻量需求写成无人评审的长文",
        ],
    )
    and has_all(
        product_prd_quality_gates,
        [
            "## 使用时机",
            "## 按任务读取索引",
            "## 1. PRD 质量门禁",
            "## 2. 文档治理门禁",
            "## 3. 可验收性门禁",
            "## 4. 已有 PRD 符合性评审输出",
            "符合项：已经满足模板、可验收性或专项门禁的内容",
            "必改：会阻断评审、研发、测试、上线或专业确认的缺口",
            "每条评审项必须说明章节或位置、问题、影响和建议改法",
        ],
    ),
)
check(
    "PRD template supports on-demand core concepts and business abstraction",
    has_all(
        product_prd_template,
        [
            "核心概念、业务抽象、对象、流程、图形视图与规则",
            "按需启用条件",
            "业务术语、运营口径、系统命名或既有文档存在冲突",
            "核心概念卡 C-001",
            "概念名称",
            "不等于",
            "业务抽象卡 A-001",
            "抽象目的",
            "不抽象范围",
            "轻量 PRD 可合并为 3-5 行术语说明",
            "核心概念表、业务抽象卡",
        ],
    )
    and has_all(
        product_prd,
        [
            "按需补核心概念和业务抽象",
            "术语存在歧义",
            "抽象目的、边界、反例、不变量和验收追踪",
            "核心概念、业务抽象、核心对象、状态、字段口径和不变量能支撑流程",
            "核心概念与业务抽象",
        ],
    )
    and has_all(
        product_prd_quality_gates,
        [
            "核心概念、业务抽象、核心对象、状态机、业务规则和字段口径可以解释所有关键流程",
            "必须有核心概念与业务抽象章节",
            "定义、适用范围、反例、责任方和与对象/规则/验收的追踪关系",
            "验收标准能回到概念定义、抽象边界、不变量、对象状态或规则编号",
        ],
    )
    and has_all(
        product_routing,
        [
            "核心概念、业务抽象、核心对象、字段口径、生命周期、状态和不变量是否能解释流程",
            "先补概念定义、抽象边界、对象模型和状态",
            "核心概念与业务抽象",
            "哪些能力、规则或关系需要抽象",
            "覆盖问题背景、用户故事、功能范围、核心概念、业务抽象、业务规则",
        ],
    ),
)
check(
    "PRD quality gates keep document governance checks",
    has_all(
        product_prd_quality_gates,
        [
            "文档过厚、过薄、未更新、未评审",
            "## 2. 文档治理门禁",
            "文档目标、目标读者和文档类型清楚",
            "主文档可扫读",
            "复杂细节拆到附录、矩阵或图",
            "图形化视图选择合理",
            "图文一致",
            "信息传递顺序清楚",
            "表格只用于比较、矩阵或追踪",
            "描述可靠性清楚",
            "正式 PRD 是最终交付标准版本",
            "不能只写功能名",
            "P0/P1 需求能通过主模板需求链回到问题/证据、目标、场景、能力/功能、规则和验收种子",
            "版本治理保留当前版本号、状态、owner、评审结论摘要、影响范围、通知对象和过程记录链接",
            "合议式产品评审报告是过程资产",
            "文档、原型、规则矩阵、验收标准和工程交接口径一致",
            "验收种子能回到需求 ID、场景编号、规则编号或质量属性 ID",
            "图形化验收路径清楚",
            "验收描述必须包含可观察结果",
        ],
    ),
)
check(
    "product routing covers PRD document governance",
    has_all(
        product_routing,
        [
            "PRD 文档质量治理 / 文档过厚过薄 / 版本评审同步",
            "PRD 文档过厚、过薄、未更新、未评审、版本状态不清或过程稿混入正文",
            "文档目标/受众、裁剪建议、必改项、版本状态/过程记录链接和最终正文准出机制",
        ],
    ),
)
check(
    "product skill tree includes PRD document governance",
    has_all(
        "product-architecture-expert/references/skill-tree.md",
        [
            "文档治理",
            "PRD/MRD/BRD",
            "主文档/附录裁剪",
            "最终正文",
            "版本状态",
            "过程记录链接",
        ],
    ),
)
check(
    "PRD financial appendix keeps payment funding gates",
    has_all(
        product_prd_financial_appendix,
        [
            "## 使用时机",
            "## 按任务读取索引",
            "## 1. 主体、法域与资质",
            "## 2. 四流说明",
            "## 3. 账务矩阵",
            "## 4. 资金与风险红线",
            "不混同客户资金、商户资金和平台自有资金",
            "不把授权成功、清算成功、结算完成、资金可用和商户出款混为一个状态",
        ],
    ),
)
check(
    "PRD operations and data appendix keeps operational closure",
    has_all(
        product_prd_operations_and_data,
        [
            "## 使用时机",
            "## 按任务读取索引",
            "## 1. 运营后台与人工处理",
            "## 2. 通知、消息与任务",
            "## 3. 数据指标、埋点与报表",
            "## 4. 发布与运营计划",
            "什么情况下进入人工处理",
            "指标口径",
            "报表与导出",
        ],
    ),
)
check(
    "payment route keeps regulatory baseline",
    has_all(product_routing, ["payment-scenario-routing.md", "regulatory-baseline.md"]),
)
check(
    "product payment routing enters financial business master frame",
    has_all(
        payment_routing,
        [
            "复杂或高风险支付资金问题",
            "金融业务总纲",
            "谁的钱，因什么业务，在什么主体和账户下，沿哪条支付轨道，以什么规则流转，何时可用，谁承担风险，谁最终确认",
            "支付/资金方案的总纲、四流、单据、能力地图和专家交付口径",
            "主轴不清时，先输出假设、澄清问题、待确认项和最小补齐计划",
        ],
    ),
)
check(
    "product route sends payment clearing ecosystem to clearing reference",
    has_all(
        "product-architecture-expert/references/payment-scenario-routing.md",
        [
            "支付清算生态、网联/银联/央行/银行、备付金、跨机构清算",
            "生态参与者分层、跨机构清算链路、备付金/额度口径、待专业确认项",
            "多业务线清结算全局规划、线下 Excel 核算、财务人工打款、清结算中台",
            "现状问题盘点、资金路径、五中心能力切分、分期迁移路线、全局规划图",
        ],
    ),
)
check(
    "product route sends global payment and compliance signals to references",
    has_all(
        "product-architecture-expert/references/payment-scenario-routing.md",
        [
            "支付合规、KYC/KYB/KYT/KYA、AML/CFT、大额交易、可疑交易",
            "卡组织、银行卡收单、预授权、Stand-In/SAF、open-to-buy、tokenization、PCI、BIN/IIN、三方/四方模式",
            "卡交易流程、授权/清算/结算、授权恢复、争议、网络费用和 PCI 边界",
            "外卡收单、Mastercard、卡网络角色、Authorization Core、Financial Presentment、Clearing Core、ARN、scheme fee、merchant payout、收单风控",
            "卡网络角色定位、授权核心、清算生命周期治理、商户可用资金、结算净额、replay / investigation 和风控闭环",
            "全球支付接受能力、Global Payment Orchestration、外卡收单 + 钱包 + 本地支付方式 + APM/RTP/A2A、多国家收款编排",
            "全球支付编排方案，覆盖卡轨、钱包轨、本地轨、认证、风控、结算、争议、资金控制和运营治理",
            "跨境支付、多币种、Swift/GPI、Nostro/Vostro、代理行、本地清算网络、外清内结",
            "跨境五层拆解、资金流、币种/汇率/费用、合规待确认项",
        ],
    ),
)
check(
    "product route sends Airwallex-style platform signals to references",
    has_all(
        "product-architecture-expert/references/payment-scenario-routing.md",
        [
            "Airwallex / WorldFirst 类全球金融平台、Global Accounts、Connected Accounts、Global Treasury、BaaS、Payments for Platforms",
            "全球金融产品能力地图、平台账户/客户主体、账户收款、付款、发卡、嵌入式金融边界和待确认项",
            "AI 出海、全球资金管理、token / 用量计费、全球订阅、AI Agent 支付、VCC 控制、平台白标金融",
            "AI 企业收、管、付、控方案，覆盖全球收款、多币种财资、批量付款、Agent 授权、VCC 控制、对账和待确认项",
            "全球付款、Payouts、受益人管理、付款审批、批量付款、付款失败和回执",
            "transfer / beneficiary / payer / batch / approval 对象模型、付款状态机、失败处理、回执和出款对账",
            "Airwallex 类全球金融平台能力分析",
            "AI 出海全球资金管理",
            "状态事件、报表、沙盒验证、复杂性承接和客户侧确定性",
        ],
    ),
)
check(
    "product payment channel reference keeps global orchestration frame",
    has_all(
        "product-architecture-expert/references/payment-channel-routing-and-operations.md",
        [
            "## 全球支付编排不是通道清单",
            "Global Payment Orchestration",
            "接受入口",
            "服务商分层",
            "认证与风控",
            "资金控制",
            "争议与证据",
            "全球覆盖 × 本地适配 × 数据与风控 × 资金控制 × 争议治理",
        ],
    ),
)
check(
    "product payment channel reference keeps platform operations closure",
    has_all(
        "product-architecture-expert/references/payment-channel-routing-and-operations.md",
        [
            "## 平台文档的运营闭环抽象",
            "状态参考",
            "事件参考",
            "报表参考",
            "验证参考",
            "状态、webhook、报表、错误码、沙盒模拟和上线检查纳入产品验收",
        ],
    ),
)
check(
    "product payment methodology keeps payment system architecture frames",
    has_all(
        payment_methodology,
        [
            "## 支付系统五层拆解",
            "支付渠道层",
            "支付网关层",
            "支付核心层",
            "统一支付能力层",
            "支付接入层",
            "## 十二字能力地图",
            "买、收、付、退、充、提、转、调、算、结、管、对",
            "## 支付核心主流程检查",
            "## 收银台与接入产品检查",
            "## 广义通道与支付创新",
        ],
    ),
)
check(
    "product payment methodology keeps financial business master frame",
    has_all(
        payment_methodology,
        [
            "## 金融业务总纲",
            "谁的钱，因什么业务，在什么主体和账户下，沿哪条支付轨道，以什么规则流转，何时可用，谁承担风险，谁最终确认",
            "支付与资金产品语境",
            "不扩展为信贷、证券、保险等全域金融方案",
            "主体与资质",
            "资金归属与账户",
            "业务事实与支付事件",
            "账务与清结算",
            "风控合规与外部规则",
            "数据证据与运营闭环",
            "支付成功、清算入账、清账完成、结算出款和资金到账不得混写",
        ],
    ),
)
check(
    "product payment methodology keeps payment ledger perspective",
    has_all(
        payment_methodology,
        [
            "## 账本观",
            "哪一本账在说话",
            "付款人账本减少、收款人账本增加",
            "信息流驱动各方账本变化，再由资金流验证和校正",
            "客户可见账",
            "平台内部账本",
            "外部机构账",
            "真实资金账",
            "会计账",
            "实体资金户",
            "内部虚拟账本",
            "不能把客户可见余额、内部账本余额、通道清算结果和银行真实到账都叫“余额正确”",
        ],
    ),
)
check(
    "product payment methodology keeps Airwallex-style platform abstraction",
    has_all(
        payment_methodology,
        [
            "Airwallex 类全球金融平台或公开产品文档分析场景",
            "Connected Accounts、Accounts、Payments、Transactional FX、Payouts、Issuing、Spend 和 Embedded Finance",
            "产品专家吸收的是能力地图、对象边界、状态事件、报表和验证闭环",
            "## 全球账户与付款补充",
            "Global Accounts、平台账户、全球收款、供应商付款、商户出款、批量付款或多币种资金运营",
        ],
    ),
)
check(
    "product payment methodology keeps embedded finance responsibility and FX gates",
    has_all(
        payment_methodology,
        [
            "嵌入式金融、平台收单、BaaS、Global Treasury 或白标金融能力场景",
            "平台、客户、商户、最终用户、银行/持牌机构、PSP、卡组织和本地合作方",
            "用户解释视图",
            "多币种、跨境、收单、出款、发卡或全球账户场景",
            "交易币种、账户币种、清算币种、结算币种、记账本位币",
            "费用承担、舍入规则、汇损益归属",
            "## 嵌入式金融与平台责任补充",
            "嵌入式金融不是“把 API 给客户”",
        ],
    ),
)
check(
    "product payment methodology keeps global platform deliverable package",
    has_all(
        payment_methodology,
        [
            "全球金融平台方案还要补交付包判断",
            "能力地图、主体责任、对象生命周期、四流资金路径、FX/费用、运营报表、风险合规、验证上线",
            "全球金融平台、BaaS、跨境、多币种、Payouts 或 Issuing 方案应在上述骨架上追加八个交付包",
            "13. 能力地图",
            "14. 主体责任矩阵",
            "15. 对象生命周期",
            "20. 验证与上线包",
            "## 生命周期与退出补充",
            "没有退出设计的金融产品是不完整的",
        ],
    ),
)
check(
    "product global payment reference keeps Airwallex-style capability map",
    has_all(
        global_payment,
        [
            "## 全球金融平台能力地图",
            "Connected Accounts / 平台账户",
            "Accounts / Global Accounts",
            "Payouts / 付款",
            "Issuing / 发卡",
            "Embedded Finance / 嵌入式金融",
            "## 状态、事件、报表、沙盒四件套",
        ],
    ),
)
check(
    "product global payment reference keeps AI outbound money management frame",
    has_all(
        global_payment,
        [
            "## AI 出海全球资金管理",
            "AI SaaS / API / 模型服务",
            "token 计费",
            "GPU / 云资源 / 算力平台",
            "AI Agent 平台",
            "收、管、付、控",
            "每个 Agent / 任务独立 VCC 或受控支付凭证",
            "覆盖国家、币种、到账时效、牌照数量",
        ],
    ),
)
check(
    "product global payment reference keeps responsibility and FX matrix",
    has_all(
        global_payment,
        [
            "## 平台责任边界矩阵",
            "客户/商户入网",
            "账户与资金",
            "换汇与费用",
            "数据与报表",
            "最终用户看到的品牌主体",
            "## FX、费用和舍入口径",
            "报价层次",
            "舍入层次",
            "归属层次",
            "解释层次",
        ],
    ),
)
check(
    "product global payment reference keeps deliverable package and maturity ladder",
    has_all(
        global_payment,
        [
            "## 全球金融平台交付包",
            "能力地图",
            "主体与责任矩阵",
            "对象与生命周期",
            "验证与上线包",
            "## 生命周期主轴",
            "入网 -> 配置 -> 交易/资金动作 -> 状态事件 -> 清结算/账务 -> 报表/对账 -> 异常/争议 -> 退出/留存",
            "## 运营成熟度阶梯",
            "L1 接口接入",
            "L5 可解释金融基础设施",
        ],
    ),
)
check(
    "product source map records Airwallex official docs boundary",
    has_all(
        product_source_map,
        [
            "Airwallex Docs Home",
            "Airwallex Accounts Docs",
            "Airwallex Payments Docs",
            "Airwallex Payouts Docs",
            "Airwallex Issuing Docs",
            "不固化覆盖国家、币种、费率、接口字段或商业承诺",
            "不把 Airwallex 或其他全球支付厂商的品牌叙事",
        ],
    ),
)
check(
    "product source map records WorldFirst AI outbound article boundary",
    has_all(
        product_source_map,
        [
            "万里汇，太牛了！AI出海的全球资金管理，算是让它玩明白了",
            "WorldFirst",
            "AI 出海企业全球资金管理",
            "token / 用量计费",
            "VCC / Agent 支付控制",
            "不吸收厂商覆盖国家、币种、时效、牌照数量、费率",
        ],
    ),
)
check(
    "product bank transfer reference keeps payouts object model",
    has_all(
        "product-architecture-expert/references/payment-rails-ach-and-bank-transfers.md",
        [
            "## Payouts 对象模型",
            "Transfer",
            "Beneficiary",
            "Payer",
            "Batch Transfer",
            "Approval",
            "Confirmation / Receipt",
            "受益人字段、银行清单、地区要求和税务材料具有强时效性",
        ],
    ),
)
check(
    "product VCC reference keeps issuing simulation frame",
    has_all(
        "product-architecture-expert/references/virtual-card-and-vcc.md",
        [
            "远程授权或协同授权",
            "告警阈值和控制规则要分开",
            "## 交易生命周期与仿真验证",
            "overcapture",
            "验收时应设计交易仿真或沙盒用例",
        ],
    ),
)
check(
    "product checklist keeps embedded finance responsibility and FX checks",
    has_all(
        payment_checklists,
        [
            "嵌入式金融、BaaS、Payments for Platforms 或白标能力是否有平台责任边界矩阵",
            "最终用户看到的品牌、合同主体、资金服务主体、隐私主体、账单主体和客服入口是否一致",
            "## FX、费用和舍入补充",
            "汇率来源、报价有效期、锁价时点、重新报价、报价撤销和异常兜底是否明确",
            "固定费、比例费、跨境费、网络费、processor fee、FX markup、退款费、拒付费、退汇费和人工处理费",
            "舍入规则、最小货币单位、差额归属、批量轧差和报表展示精度",
        ],
    ),
)
check(
    "product checklist keeps global platform deliverable and lifecycle checks",
    has_all(
        payment_checklists,
        [
            "## 全球金融平台交付包检查",
            "是否输出能力地图",
            "是否输出主体责任矩阵",
            "是否输出对象生命周期",
            "是否输出验证与上线包",
            "## 生命周期与运营成熟度检查",
            "入网 -> 配置 -> 交易/资金动作 -> 状态事件 -> 清结算/账务 -> 报表/对账 -> 异常/争议 -> 退出/留存",
            "是否评估当前能力成熟度处于接口接入、对象化、运营闭环、平台化还是可解释金融基础设施阶段",
        ],
    ),
)
check(
    "product payment checklist keeps financial expert gate",
    has_all(
        payment_checklists,
        [
            "## 金融业务专家总检",
            "谁的钱、因什么业务、在什么主体和账户下、沿哪条支付轨道、以什么规则流转、何时可用、谁承担风险、谁最终确认",
            "客户资金、商户待结算资金、平台自有资金、保证金、准备金、授信额度、预算额度、手续费收入和通道成本",
            "业务确认、支付受理、授权成功、清算入账、清账完成、结算出款、资金到账、财务确认",
            "四流、单据状态、账户/账务、清结算/对账、风险合规、数据证据和验收确认方",
            "法域、主体资质、外部规则版本、数据边界和待专业确认项",
        ],
    ),
)
check(
    "product payment checklist keeps multi-ledger settlement gates",
    has_all(
        payment_checklists,
        [
            "客户可见账、平台内部账本、外部机构账、真实资金账和会计账",
            "支付、退款、撤销、清分、结算、调账、长短款、拒付或退汇",
            "加记、减记、冻结、解冻、冲正、挂账",
            "内部可见额度、通道/清算机构账、银行/存管真实资金和财务确认",
            "垫资、授信、准备金、限额和风控承接",
            "往来户模式或代理结算模式",
            "代理结算、平台代收代付、多 PSP 或跨境收付",
            "内部账本与底层资金账户的映射规则",
            "大账户、备付金账户、清算账户、Nostro/Vostro 或资金池",
        ],
    ),
)
check(
    "product payment checklist keeps clearing delay and dispute gates",
    has_all(
        payment_checklists,
        [
            "清算文件未按预期到达、迟到、缺失或处理状态异常",
            "交易日、清算日、入账/结算日",
            "accepted but delayed",
            "rejected / held",
            "三段链路归因",
            "同一 MID 大面积 reject",
            "卡争议与非卡争议",
            "Alert / Inquiry / Retrieval / Chargeback / Representment / Pre-arbitration / Arbitration",
            "争议率/CB 率",
            "分型、止血、按原因码组证、判断 representment",
            "前置预防、预警处置、正式争议、反馈回流",
        ],
    ),
)
check(
    "product clearing reference keeps payment clearing ecosystem frames",
    has_all(
        clearing_settlement,
        [
            "## 支付清算生态分层",
            "交易平台层",
            "支付服务层",
            "清算服务层",
            "金融服务层",
            "央行/金融基础设施层",
            "## 交易平台七段全链路",
            "## 跨机构清算四步",
            "联机交易",
            "实时清算",
            "定时结算",
            "日终处理",
            "## 备付金与额度口径",
            "集中存管账户余额",
            "映射额度",
            "可用额度",
        ],
    ),
)
check(
    "product clearing reference keeps multi-ledger and agency settlement gates",
    has_all(
        clearing_settlement,
        [
            "## 账本观与虚实分离",
            "付款人账本减少、收款人账本增加",
            "一堆账本",
            "两个动作",
            "双层结构",
            "虚实结合",
            "大账户、备付金账户、清算账户、Nostro/Vostro 或资金池是真实资金户",
            "客户余额、商户待结算、VA、子账户或钱包余额通常是内部虚拟账本",
            "## 跨机构支付两种模式",
            "往来户模式",
            "代理结算模式",
            "内部可见额度",
            "底层资金账户",
            "清算场次",
            "轧差规则",
            "失败回退",
        ],
    ),
)
check(
    "product clearing reference keeps clearing file delay gate",
    has_all(
        clearing_settlement,
        [
            "## 清算文件异常延迟排查门禁",
            "清算文件未按预期到达、迟到、缺失或处理状态异常时，不能先归因于网关慢",
            "交易日、清算日、入账/结算日",
            "Processing Calendar / Holiday Schedule",
            "accepted but delayed",
            "rejected / held",
            "ACK、确认号、批次 ID",
            "商户/PSP 到收单处理、卡组织/清算网络、银行/代理行/币种中转",
            "连续多批次缺失、同一 MID 大面积 reject、金额轧差突然偏离",
        ],
    ),
)
check(
    "product global payment reference keeps cross-border frames",
    has_all(
        global_payment,
        [
            "## 跨境支付五层分析法",
            "交易层",
            "支付处理层",
            "代理结算层",
            "清算网络层",
            "最终清算层",
            "## Nostro/Vostro 与跨境三模式",
            "清算行模式",
            "代理行模式",
            "NRA/非居民账户模式",
            "外清、内结",
        ],
    ),
)
check(
    "product dispute reference keeps acquiring dispute governance",
    has_all(
        dispute_refund,
        [
            "## 外卡争议治理链路",
            "资金归属权的后半场",
            "卡争议",
            "非卡争议",
            "Alert -> Inquiry / Retrieval -> Chargeback -> Representment -> Pre-arbitration / Arbitration",
            "分型",
            "止血",
            "按原因码组证",
            "判断 representment",
            "结果回流",
            "前置预防、预警处置、正式争议、反馈回流",
            "具体阈值、区域、生效日、排除项必须按 Visa/Mastercard/收单行/通道最新官方规则确认",
        ],
    ),
)
check(
    "product clearing reference keeps settlement and accounting frames",
    has_all(
        clearing_settlement,
        [
            "## 清算、结算、清结算辨析",
            "理论二元语境",
            "机构命名语境",
            "平台产品语境",
            "内部核算语境",
            "## 账务核心与会计基础",
            "外围驱动",
            "凭证规则",
            "会计循环",
            "总分核对",
        ],
    ),
)
check(
    "product clearing reference keeps clearing settlement reconciliation gate",
    has_all(
        clearing_settlement,
        [
            "## 清账、结算、对账三段门禁",
            "先清账，再结算",
            "结算只认清账结果",
            "先对清账，再对结算",
            "交易/订单、手续费、退款、调账、冲正、补结、扣回、拒付或退单",
            "渠道、银行或清算机构文件中的负项、调账项和非正常交易不能只在结算层处理",
            "渠道到账金额、银行流水或上游结算文件只能用于合理性校验和资金对账",
            "对账顺序必须区分清账对账和结算对账",
            "结算系统不得把渠道或银行到账金额当作商户应结金额的直接来源",
        ],
    ),
)
check(
    "product clearing reference keeps global planning frame",
    has_all(
        clearing_settlement,
        [
            "## 跨业务线清结算全局规划",
            "不再归因于已删除、当前不可复核的历史文章链接",
            "项目事实、资金路径、财务/账务负责人意见和可核验资料确认",
            "现状盘点",
            "线上线下两层皮",
            "系统只出报表不记账",
            "对账只对不处理",
            "五中心能力切分",
            "清算中心",
            "账务中心",
            "账户中心",
            "结算中心",
            "对账中心",
            "专业化",
            "模块化",
            "配置化",
            "线上化先行",
            "清算中心跟进",
            "账务账户收口",
            "业务接入层",
            "场景解决方案层",
            "核心能力层",
            "基础连接层",
        ],
    ),
)
check(
    "product card network reference keeps card organization clearing frames",
    has_all(
        card_network,
        [
            "## 卡组织网络与三/四方模式",
            "四方模式",
            "三方模式",
            "卡 BIN / IIN 路由",
            "专线与前置系统",
            "跨境卡交易还要额外区分四个口径",
            "## 授权网络与前置裁决",
            "authorization request/response",
            "authorization advice",
            "network management",
            "## Stand-In、SAF 与授权恢复",
            "代理裁决不是默认放行",
            "SAF / advice 如何把临时授权结果送回 issuer",
            "open-to-buy",
            "## 授权数据与生命周期追踪",
            "Trace ID",
            "Original Data Elements",
            "授权数据准确性",
            "## 卡网络能力栈与角色定位",
            "Transaction processing",
            "Participant role",
            "Responsibility management",
            "Cost and billing",
            "Network governance",
            "## 授权核心建模",
            "Authorization Lifecycle",
            "Authorization / Hold / Reference Chain",
            "Network session boundary",
            "scheme adapter",
            "## Clearing Core 与账务承接",
            "Financial Presentment",
            "Matching Core",
            "ARN / Reference Model",
            "Fee & Amount Decomposition",
            "Posting Model",
            "## Clearing Core 生命周期治理",
            "transaction lifecycle",
            "accounting consistency",
            "reference continuity",
            "dispute traceability",
            "replay / investigation",
            "ARN、STAN、RRN、DE90",
            "金额一致性",
            "关系一致性",
            "结构一致性",
            "锚点一致性",
            "Authorization -> Clearing",
            "Clearing -> Posting",
            "Posting -> Settlement",
            "Reference chain -> Dispute",
            "Time chain",
            "## Settlement 与商户可用资金",
            "Network member settlement",
            "Platform allocation and netting",
            "Merchant settlement / payout",
            "Bank arrival",
            "## 收单风控闭环",
            "merchant onboarding",
            "capture / fulfillment",
            "dispute feedback",
        ],
    ),
)
check(
    "product clearing reference keeps acquiring settlement frames",
    has_all(
        clearing_settlement,
        [
            "## 外卡收单结算补充",
            "Clearing / Financial Presentment",
            "Network member settlement",
            "Platform allocation and netting",
            "Merchant settlement / payout",
            "Bank arrival",
            "gross settlement basis",
            "net settlement amount",
            "withheld amount",
            "in-transit amount",
        ],
    ),
)
check(
    "product risk reference keeps acquiring risk lifecycle",
    has_all(
        payment_risk,
        [
            "## 外卡收单风控闭环",
            "Merchant onboarding risk",
            "Transaction risk",
            "Capture and fulfillment risk",
            "Settlement and funds risk",
            "Dispute feedback risk",
            "3DS 是认证增强和部分责任划分能力",
            "rules、risk scoring、manual review、funds strategy、case management",
        ],
    ),
)
check(
    "product regulatory baseline keeps KYC lifecycle",
    has_all(
        regulatory,
        [
            "## KYC / KYB / KYT / KYA 生命周期",
            "**KYC**",
            "**KYB**",
            "**KYT**",
            "**KYA**",
            "持续监控",
        ],
    ),
)
check(
    "product risk reference points to KYC lifecycle",
    has_all(
        payment_risk,
        [
            "KYC/KYB/KYT/KYA 生命周期",
            "入网前确认主体与业务真实性",
            "结算前评估退款、拒付、负余额和准备金",
        ],
    ),
)
check(
    "product skill tree exposes payment system architecture frames",
    has_all(
        product_skill_tree,
        [
            "支付五层：支付渠道层、支付网关层、支付核心层、统一支付能力层、支付接入层",
            "跨境支付五层：交易层、支付处理层、代理结算层、清算网络层、最终清算层",
            "支付十二字能力地图：买、收、付、退、充、提、转、调、算、结、管、对",
            "支付账本观：支付本质是多方账本、账户归属和真实资金路径的协同变化",
            "卡组织清结算：四方/三方模式、BIN/IIN 路由、授权前置裁决、Authorization Core、Stand-In/SAF、open-to-buy、Financial Presentment、Matching/ARN、费用拆分、Posting、生命周期对账、reference continuity、replay / investigation、结算与网络费用",
            "全球支付编排：把卡轨、钱包、本地支付、APM/RTP/A2A、PSP/网关、认证、风控、结算、争议和资金控制组织成可运营网络",
            "全球覆盖、本地适配、数据与风控、资金控制和争议治理",
            "外卡收单风控：商户准入、3DS/规则/评分、capture / fulfillment 控制、保证金/延迟结算、争议反馈和商户风险闭环",
            "账务核心：外围驱动、凭证规则、账户结构、会计循环、总分核对和日切批处理",
            "支付清算生态：交易平台层、支付服务层、清算服务层、金融服务层、央行/金融基础设施层",
            "跨机构清算：联机交易、实时清算、定时结算、日终处理",
            "KYC/KYB/KYT/KYA：身份、商户/业务、交易、地址和持续监控",
        ],
    ),
)
check(
    "senior skill tree exposes architecture diagram literacy",
    has_all(
        "senior-software-architect/references/skill-tree-platform-leadership-ai.md",
        [
            "技术架构图必须区分整体、子领域和应用粒度",
            "架构图要表达职责、关系、同步/异步、数据流、容量或瓶颈",
            "图形应随代码、接口、部署、监控和关键决策演进",
            "AI 辅助画图只能生成可编辑草案",
            "视图层级、节点责任、箭头语义、敏感信息、版权边界和工程验证闭环",
        ],
    ),
)
check(
    "senior skill tree exposes functional allocation literacy",
    has_all(
        "senior-software-architect/references/skill-tree-architecture-design.md",
        [
            "对象对外可见、有价值的交互行为",
            "上层对象或父能力分配而来",
            "正向分解和逆向追溯",
            "需求分析的外部视角和设计活动的内部视角",
            "避免在需求阶段过早按内部结构拆功能",
        ],
    ),
)
check(
    "product skill tree exposes product diagram literacy",
    has_all(
        product_skill_tree,
        [
            "图形化表达",
            "能力地图、用户旅程、服务蓝图、流程图、状态机、资金四流和指标链路",
            "AI 辅助画图只作为可编辑草案",
            "必须回到 PRD、规则、证据和验收",
        ],
    ),
)
check(
    "product skill tree exposes product manager foundational methods",
    has_all(
        product_skill_tree,
        [
            "产品经理方法论 / 基础能力补齐",
            "产品经理基础方法能力",
            "文档分型",
            "流程表达",
            "原型注释",
            "用户研究",
            "需求管理",
            "数据分析",
            "技术/项目协作",
            "行业商业分析",
            "知识库与能力复制",
            "不把基础岗位清单当作专家能力终点",
        ],
    ),
)
check(
    "product skill tree exposes functional allocation literacy",
    has_all(
        product_skill_tree,
        [
            "功能分配",
            "对象对外可见、有价值的交互行为",
            "追溯到目标、父能力或上层业务对象",
            "分配到对象、流程、规则、数据和验收",
        ],
    ),
)
check(
    "product skill tree exposes AI-shaped product workflow maturity",
    has_all(
        product_skill_tree,
        [
            "AI 产品工作成熟度评估",
            "不把工具熟练度当成熟度",
            "AI 产品工作流成熟度",
            "区分 AI 工具提效和 AI-shaped 工作重构",
            "业务优势、流程变化、上下文结构化、任务编排、人工责任、验证周期、决策质量和返工率",
        ],
    ),
)
check(
    "senior skill tree records external AI skill method boundary",
    has_all(
        "senior-software-architect/references/skill-tree.md",
        [
            "公开 AI Skill 方法论",
            "`obra/superpowers`",
            "`multica-ai/andrej-karpathy-skills`",
            "`mattpocock/skills`",
            "只吸收原则，不复制仓库结构、安装流程或技能菜单",
        ],
    ),
)
check(
    "product route keeps semantic questioning product-scoped",
    has_all(
        product_routing,
        [
            "语义追问：当用户目标、对象、流程或规则含混时",
            "不要用工程代理式执行计划替代产品语义澄清",
            "共享语言服务于产品对象、规则和验收，不是额外文档本身",
        ],
    ),
)
check(
    "senior product design stays engineering scoped",
    has_all(
        "senior-software-architect/references/product-design.md",
        [
            "不是 PRD 生成指南",
            "不替代 `产品架构专家`",
            "工程设计",
            "产品语义",
        ],
    ),
)
check(
    "product source map records payment system article reference",
    has_all(
        product_source_map,
        [
            "## 读取与归因规则",
            "## 本地证据归档规则",
            "默认 `~/.skill-source-archive/`",
            "SKILL_SOURCE_ARCHIVE_HOME",
            "`archive_id`",
            "`evidence_sha256`",
            "不得写入文章全文、原图、截图包、MHTML、PDF、付费内容或大段摘录",
            "未读取到正文、页面删除、只剩验证页或正文为空的条目",
            "不得作为已吸收来源",
            "不代表原文逐字表述",
            "https://mp.weixin.qq.com/s/7sZhZPeBE7XmBLjik8al8w",
            "支付系统五层拆解、支付核心主流程、收银台、路由、通道管理、退款和广义通道",
            "https://mp.weixin.qq.com/s/4P1PuButME_rr5anXeK2ng",
            "支付清算生态分层、跨机构清算、备付金/额度口径",
            "https://mp.weixin.qq.com/s/86gPuhw8eUYb65gRhALH6A",
            "全球支付清算基础、Nostro/Vostro、外清内结、清算行/代理行/NRA 模式",
            "https://mp.weixin.qq.com/s/FM6h2bbN5xLXZQLJYG-cWg",
            "全球支付信息流和资金流五层拆解",
            "https://mp.weixin.qq.com/s/r2bUyLICOvWV40GOIfBbGw",
            "支付账本观、多套账本、清算/结算双层",
            "https://mp.weixin.qq.com/s/atTMCmIoQaG0EIsed2TATg",
            "支付知识体系主题索引和能力地图校准",
            "https://mp.weixin.qq.com/s/NVmy4mKSB83bP18u6XEzHA",
            "卡组织支付清结算、四方/三方模式、BIN 路由",
            "https://mp.weixin.qq.com/s/ZhKc64tXXguEFJYxozuMtw",
            "三方支付机构全链路",
            "https://mp.weixin.qq.com/s/04oIhVhypiZv7sRWygtOoA",
            "会计恒等式、会计循环、总账/明细账",
            "https://mp.weixin.qq.com/s/WWhjG9ACi3qmqeqPFvBaaA",
            "账务核心架构、账户体系、热点账户、账户合并",
            "https://mp.weixin.qq.com/s/FVx1lUcxCF3jUl0Xh6UydA",
            "支付合规、KYC/KYB/KYT/KYA、持续监控、交易限额、反洗钱/反恐怖融资",
            "https://mp.weixin.qq.com/s/vQh7wUILKVTLP9xq6xDvmw",
            "清算、结算、清结算在理论概念、机构命名、平台产品和企业信息层处理语境中的差异",
            "https://mp.weixin.qq.com/s/vHJ7LlePC8o5qV84XVtU4Q",
            "2026-05-26 Playwright 核验结果为页面已被发布者删除",
            "正文不可复核",
            "仅保留为历史索引线索",
            "不得作为已吸收来源",
            "https://mp.weixin.qq.com/s/oXTAGAvE_OwNJfq1JXLZ0w",
            "先清账再结算、先对清账再对结算、调账/冲正/负项必须进入清账模型",
            "https://mp.weixin.qq.com/s/Dh22dNM6Ze4fHgytthN0ng",
            "Mastercard 授权作为网络级前置裁决、授权消息家族、Stand-In/SAF/Advice/Reversal、open-to-buy 管理、Trace ID 和授权数据准确性",
            "https://mp.weixin.qq.com/s/gyLFP4J0syasU4DahMYy9A",
            "Mastercard 作为支付网络、交易处理、参与方角色、责任管理、成本计收和网络治理的能力栈视角",
            "https://mp.weixin.qq.com/s/rgZSbR_2zfkISFhSuHmMPg",
            "Authorization Core、Authorization Lifecycle、Hold/Reference Chain、network session boundary、ISO 8583 semantic carrier、scheme adapter、SAF recovery 和授权可观测性",
            "https://mp.weixin.qq.com/s/uuEwioL-Xx3JKeGvG7AyCg",
            "Clearing 不是文件状态更新，而是 Financial Presentment、账务进入、费用拆分和后续争议追溯的入口",
            "https://mp.weixin.qq.com/s/iSvq8LO0zjHlW20ZUf_S6Q",
            "Matching Core、ARN / Reference Model、Fee & Amount Decomposition、Posting Model、异常处理/隔离和清算到账务承接",
            "https://mp.weixin.qq.com/s/sU_Opre7z9cRVdtOB1y-Zg",
            "Clearing Core 作为生命周期治理能力，覆盖 transaction lifecycle、accounting consistency、reference continuity、dispute traceability、replay / investigation、四层 reconciliation、清算异常按交易链影响分类，以及多卡组核心语义与适配边界",
            "https://mp.weixin.qq.com/s/Y1O4BsLo4DD0HgkKYSRQnw",
            "外卡收单中 authorization、clearing、settlement 的语义差异，以及清算连接交易、账务、费用、责任、对账和争议的产品视角",
            "https://mp.weixin.qq.com/s/hilJTPiiakSQvDLYAzHtuA",
            "settlement 不是商户打款动作，而是成员级结算、平台内部分配/轧差、商户结算/打款、银行到账、保证金/延迟结算和商户可用资金管理",
            "https://mp.weixin.qq.com/s/MXKNyFtROB-F-mEM1nNoPQ",
            "外卡收单风控贯穿商户准入、交易、capture / 履约、结算、争议反馈和资金策略，而不是单点交易拦截",
            "https://mp.weixin.qq.com/s/IpEWgr-8pMzUP480TDWlFw",
            "外卡收单从接卡组/API 升级为全球支付编排能力",
            "卡组、钱包、本地支付方式、APM/RTP/A2A、PSP/网关、认证风控、结算资金、争议治理和运营闭环",
            "清算文件迟到 24 小时：财务骂网关之前，该对齐的 5 个问题",
            "bab6c18e89728feaf921bccbc5cb88d3",
            "交易日/清算日/入账结算日、cut-off、processing calendar、时区、ACK/reject",
            "外卡收单钱收到了，战争才刚开始",
            "a171eb833dc25e6e83be75c407ad69ff",
            "Alert / Inquiry / Retrieval / Chargeback / Representment / Pre-arbitration / Arbitration",
            "Visa/Mastercard 监控阈值、生效日和区域规则以官方资料、收单行或通道合同为准",
            "https://mp.weixin.qq.com/s/IvaaVh_li9ysvghSjUjnhQ",
            "PRD Skill 化、团队模板清单化、生成/补全/符合性评审双模式",
            "不复制原文模板或另建重复 PRD Skill",
            "https://mp.weixin.qq.com/s/qRv1Qe3GjQ_jbQqWGQcHfQ",
            "PRD 作为产品思考结构、模糊需求连续追问、原型/HTML/页面截图/交互稿反推 PRD",
            "不复制原文模板、安装说明、外部 Skill 结构或效率营销表述",
        ],
    ),
)
check(
    "regulatory baseline requires professional confirmation",
    has_all(
        regulatory,
        [
            "待法务/合规/财务/通道/持牌机构确认项",
            "不得写成确定性上线依据",
        ],
    ),
)
check(
    "product skill exposes deterministic external rule checker",
    has_all(
        product_skill,
        [
            "scripts/check_external_rules.py",
            "不访问网络、不上传文件、不读取密钥",
            "规则真实性、适用性和可上线性",
        ],
    )
    and has_all(
        product_routing,
        [
            "scripts/check_external_rules.py",
            "只做完整性检查",
            "不联网、不写文件",
        ],
    )
    and has_all(
        product_rule_checker,
        [
            "--self-test",
            "VALID_SELF_TEST",
            "INVALID_SELF_TEST",
            "REQUIRED_FIELDS",
            "rule_source",
            "version_or_publish_date",
            "jurisdiction_or_scope",
            "verified_at",
            "confirming_party",
        ],
    ),
)
check(
    "product skill exposes deterministic deliverable checker",
    has_all(
        product_skill,
        [
            "scripts/check_product_deliverable.py",
            "PRD、产品架构方案、图形 brief 和产品合议评审报告",
            "正式、完整、可评审、提交前、CR 或触发验证场景",
            "不写文件、不访问网络、不上传文件、不读取密钥",
            "不判断方案业务质量",
            "无法运行脚本时必须说明原因、人工检查结果和残余风险",
        ],
    )
    and has_all(
        product_routing,
        [
            "scripts/check_product_deliverable.py",
            "--kind prd",
            "--kind product-architecture",
            "--kind diagram-brief",
            "--kind product-review",
            "必须运行",
            "只做本地文本完整性检查",
            "不联网、不写文件",
            "无法运行时必须说明原因、人工检查结果和残余风险",
        ],
    )
    and has_all(
        product_prd,
        [
            "scripts/check_product_deliverable.py --kind prd",
            "scripts/check_product_deliverable.py --kind product-architecture",
            "必须运行",
            "不替代产品判断、业务确认或合规审查",
        ],
    )
    and has_all(
        product_diagram,
        [
            "scripts/check_product_deliverable.py --kind diagram-brief",
            "图形目标、目标读者、图形类型、节点/分组、箭头语义",
            "必须运行",
            "不判断图形美观度、业务正确性或渲染质量",
        ],
    )
    and has_all(
        product_deliverable_checker,
        [
            "--self-test",
            "SELF_TESTS",
            '"prd":',
            '"product-architecture":',
            '"diagram-brief":',
            '"product-review":',
            "goal_and_scope",
            "risk_and_confirmation",
            "状态机图",
            "用例图",
            "流程图",
            "泳道图",
            "output_format",
            "review_context",
            "disagreement",
            "pending_confirmation",
            "verification",
        ],
    ),
)
check(
    "senior skill exposes deterministic architecture deliverable checker",
    has_all(
        senior_skill,
        [
            "scripts/check_architecture_deliverable.py",
            "架构方案、系统分析设计、代码 Review、生产变更和图形 brief",
            "正式、完整、可评审、提交前、CR 或触发验证场景",
            "不写文件、不访问网络、不上传文件、不读取密钥",
            "不判断架构质量",
            "无法运行脚本时必须说明原因、人工检查结果和残余风险",
        ],
    )
    and has_all(
        "senior-software-architect/references/review-and-output-templates.md",
        [
            "scripts/check_architecture_deliverable.py --kind architecture-plan",
            "--kind code-review",
            "--kind production-change",
            "必须运行",
            "不替代架构判断、代码阅读、测试验证或生产审批",
        ],
    )
    and has_all(
        "senior-software-architect/references/system-analysis-design.md",
        [
            "scripts/check_architecture_deliverable.py --kind system-design",
            "背景目标、边界、概要设计、详细设计、流程状态、非功能、测试和研发计划",
            "必须运行",
            "不替代架构评审或工程验证",
        ],
    )
    and has_all(
        senior_diagram,
        [
            "scripts/check_architecture_deliverable.py --kind diagram-brief",
            "图形目标、目标读者、图形类型、工程落点、节点/分组、箭头语义",
            "必须运行",
            "不判断架构质量、视觉美观度或渲染质量",
        ],
    )
    and has_all(
        architecture_deliverable_checker,
        [
            "--self-test",
            "SELF_TESTS",
            '"architecture-plan"',
            '"system-design"',
            '"code-review"',
            '"production-change"',
            '"diagram-brief"',
            "background_and_goal",
            "release_and_risk",
            "engineering_anchor",
        ],
    ),
)
check(
    "senior architecture deliverable checker has public fixtures",
    has_all(
        architecture_fixture_verifier,
        [
            "architecture-plan-valid.md",
            "system-design-valid.md",
            "code-review-valid.md",
            "production-change-valid.md",
            "diagram-brief-valid.md",
            "invalid-incomplete.md",
            "Architecture fixture verification passed.",
        ],
    )
    and has_all(
        "scripts/validate.sh",
        [
            "senior-software-architect/scripts/check_architecture_deliverable.py --self-test",
            "senior-software-architect/scripts/verify_fixtures.py",
        ],
    ),
)
check(
    "java service generator routes structured input to deterministic script",
    has_all(
        codegen_skill,
        [
            "DDL/SQL",
            "schema 文件路径",
            "Java 类",
            "字段说明表格",
            "references/code-generation-rules.md",
            "references/nobe-patterns.md",
            "scripts/generate_scaffold.py",
            "不访问网络、不上传文件、不读取密钥",
            "已有文件不允许覆盖",
            "多个 face/impl 模块对存在歧义",
            "字段表格缺少目标表名",
        ],
    ),
)
check(
    "java service generator keeps public-safe fixtures",
    has_all(
        codegen_fixture_verifier,
        [
            'BASE_PACKAGE = "com.example.skill.codegen"',
            "sample_order.sql",
            "SampleChannel.java",
            "sample_batch_fields.md",
            "SampleOrder",
            "SampleChannel",
            "SampleBatch",
        ],
    )
    and has_all(
        codegen_generator,
        [
            "无法推断基础包名，请传入 --base-package",
            "基础包名，例如 com.example.skill.codegen",
        ],
    )
    and has_all(
        codegen_rules,
        [
            "com.example.skill.codegen",
            "t_sample_order",
            "/tmp/skill-codegen-sample",
        ],
    )
    and has_none(
        codegen_fixture_verifier,
        [
            "com." + "capte",
            "com/" + "capte",
            "payment_" + "order.sql",
            "Payment" + "Channel.java",
            "settlement_" + "batch_fields.md",
        ],
    ),
)

scenario_fixtures: list[RouteFixture] = [
    RouteFixture(
        name="codebase onboarding reconnaissance",
        prompt="这个陌生代码库我不熟，帮我先做架构现状分析和接手侦察",
        routes={"senior", "language-agnostic-architecture.md", "workflow.md"},
    ),
    RouteFixture(
        name="non java node service diagnosis",
        prompt="这个 Node.js 服务我第一次接手，先帮我识别技术栈、入口路径、测试命令和部署链路，不要套 Java 规则",
        routes={"senior", "language-agnostic-architecture.md", "workflow.md"},
    ),
    RouteFixture(
        name="architecture smell scan",
        prompt="这批 Java 代码帮我做一次深度质量扫描，看看有没有架构坏味、上帝类和循环依赖",
        routes={"senior", "coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md", "coding-standards.md"},
    ),
    RouteFixture(
        name="service layer architecture smell",
        prompt="这个 Spring Service 有跨层调用、事务边界混乱和公共模块垃圾桶问题，帮我做架构坏味 CR",
        routes={"senior", "coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md", "coding-standards.md"},
    ),
    RouteFixture(
        name="in memory business service review",
        prompt="做一轮代码 CR：这个 Spring Boot 业务模块新增了 InMemoryOrderService 和 Map 存储实现，Controller 直接调用它，判断是否能作为生产实现交付",
        routes={"senior", "coding-review-deep-dive.md", "negative-constraints.md", "coding-standards.md"},
    ),
    RouteFixture(
        name="architecture decay entropy review",
        prompt="请用资深架构师视角 CR 这个遗留模块是否已经架构腐朽：大家不敢删旧代码，出现承重 bug、废弃 API、新旧 final 版本并存、循环依赖和治理规则失效。给出可删除性评审、守卫自检和最小排熵计划，不要建议大重写",
        routes={"senior", "evolutionary-architecture.md", "coding-review-deep-dive.md", "adr-and-tradeoff.md", "production-readiness.md"},
    ),
    RouteFixture(
        name="incident timeline and 5 why",
        prompt="昨晚线上故障帮我整理时间线并做 5-Why 复盘",
        routes={"senior", "debugging-diagnosis.md", "production-readiness.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="incident postmortem",
        prompt="帮我做一次生产故障复盘，给出止血、根因、改进和验证",
        routes={"senior", "debugging-diagnosis.md", "production-readiness.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="production incident readonly evidence",
        prompt="线上订单回调大量超时，先只读分析影响面、日志指标、时间线、止血方案和回滚风险",
        routes={"senior", "debugging-diagnosis.md", "production-readiness.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="spring security review",
        prompt="帮我看一下这个 Spring Boot 后台的 Spring Security、CSRF 和 CORS 安全设计",
        routes={"senior", "security-architecture.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="write tests",
        prompt="给这个 Application Service 补一组 TDD 测试，先写失败测试",
        routes={"senior", "testing.md", "coding-standards.md", "workflow.md"},
    ),
    RouteFixture(
        name="business-driven validation to tdd",
        prompt="会员权益方案已有验收样例和质量属性种子，把业务驱动验证映射成 TDD 测试计划，区分失败测试、监控指标和人工确认门禁",
        routes={"senior", "testing.md", "coding-standards.md", "workflow.md"},
    ),
    RouteFixture(
        name="bug diagnosis",
        prompt="线上出现 NullPointerException，帮我定位根因并补回归测试",
        routes={"senior", "debugging-diagnosis.md", "testing.md", "workflow.md"},
    ),
    RouteFixture(
        name="AI coding CAD",
        prompt="根据 OpenSpec 用多 Agent 推进这批代码实现，可以进入 CAD Mode 吗",
        routes={"senior", "workflow.md", "ai-assisted-engineering.md", "cad-mode.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="OpenSpec Superpowers Harness AI coding governance",
        prompt="按照 OpenSpec 规定要做什么、Superpowers 规定怎么高质量地做、Harness 规定谁做按什么顺序做能改哪里怎么验证怎么交接，增强架构师 AI 编码约规和流程能力",
        routes={"senior", "workflow.md", "ai-assisted-engineering.md", "ai-large-project-orchestration.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="AI large project orchestration",
        prompt="目前确实有中大型项目，需要类似 GSD 的 AI 编码能力，做上下文衰减治理、Wave 编排和暂停恢复",
        routes={"senior", "workflow.md", "ai-assisted-engineering.md", "ai-large-project-orchestration.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="GSD with CAD execution",
        prompt="把 GSD 大项目编排和 CAD Mode 结合起来，只对满足门禁的原子任务包自动分轮推进，并用 Execution Grant 控制授权",
        routes={"senior", "workflow.md", "ai-assisted-engineering.md", "ai-large-project-orchestration.md", "cad-mode.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="AI Native product engineering workflow",
        prompt="用 AI Native 研发流程编排设计一套从 AI 原型 / 评测到 PRD-Lite、OpenSpec、Harness/GSD/CAD 准入、验证矩阵草案、代码 CR、发布复盘的研发编码流程",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "gsd-cad-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native GSD CAD handoff",
        prompt="产品上下文包已有目标对象规则和验收种子，评估如何把 GSD Wave 和 CAD 原子任务结合，输出 Harness 摘要、Execution Grant 缺口和停止条件",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "gsd-cad-admission.md"},
    ),
    RouteFixture(
        name="AI Native GSD product engineering collaboration",
        prompt="进入 GSD 产研协同研发流程：目标是交付生产可用能力，不是让 AI 随机推进模拟模块、内存版业务 Service 或样子货；产品专家先做需求分析、产品设计和确认，架构师再做系分设计、编码、TDD、CR 和验证",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "gsd-cad-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native demand analysis collaboration gate",
        prompt="AI Native 研发流程进入需求分析协同门禁：用户原始诉求里混了功能解法，先输出需求分析结论卡，明确根源需求、产品定义、产品边界、稳定点/变化点、边界坐标和上下游分工，再判断能否进入 PRD / 系分预审或 GSD Round 0",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "gsd-cad-admission.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native core problem diagnosis gate",
        prompt="进入 AI Native 问题核心诊断模式：这次需求无止境、价值意义摇摆，还混着工具方案和架构动作；先抓住问题的核心，输出概念定名、需求止损、定向定性定位定量、整体 / 系统 / 科学诊断，再决定是否进入 GSD 或系分",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native development standards gate",
        prompt="AI Native 研发流程补需求 / 设计 / 编码标准门禁：系统需求或产品需求未确认时，不进入 SDD、测试、代码或 CAD；输出需求基线稳定性、需求条目质量、HLR/LLR 设计追踪、编码规则原因示例验证方式和防御式编程检查",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "spec-template-practices.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native product system DNA gate",
        prompt="进入 GSD 前先做产品 / 系统 DNA 门禁：当前只有功能清单和页面草图，检查核心对象、业务不变量、状态流转、责任边界、演化规则和验证方式，避免功能先行、规则后补",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "spec-template-practices.md", "gsd-cad-admission.md", "product"},
    ),
    RouteFixture(
        name="AI Native intent to production role loop",
        prompt="参考 Loop Engineering，把 AI 工作流从意图 / 需求收集做到生产交付闭环，区分业务 owner、产品专家、UED、架构师、AI Maker、AI Checker、质量 / 测试门禁和发布 owner 在每个阶段的分工、交接物、验证门禁和停止条件",
        routes={"ai-native", "intent-to-production-loop.md", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "agentic-engineering-governance.md", "agent-loop-engineering.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native autonomous discovery to delivery loop",
        prompt="进入 AI Native 角色协作 Loop，让 AI 自我挖掘需求和代码上下文，确认边界，设计并 CR 需求，再执行 TDD、编码、代码 CR、验证实际可行，最后判断完成、继续 Loop、停止或需要人工确认，输出自主交付控制卡",
        routes={"ai-native", "intent-to-production-loop.md", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "agentic-engineering-governance.md", "agent-loop-engineering.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native PRD system design deliberation review",
        prompt="对这份 AI 生成的 PRD 和系分设计做 MAGI 三角色合议预审，按 review_task、evaluation_task、reporting_task 输出 ACCEPT/REJECT/PENDING 决策日志、风险清单、owner、验证方式和下一步路由，不要直接改正文",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "agentic-engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native PRD AI prescan review",
        prompt="做 PRD 评审会前 AI 预扫描：先让产品专家按完整性、一致性、可测试性、二义性找疑似问题和追问点，再接入 MAGI 预审的 review_task、evaluation_task、reporting_task，输出 ACCEPT/REJECT/PENDING 和 owner",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "product", "product-scenario-routing.md", "product-prd-quality-gates.md", "product-design-and-prd.md"},
    ),
    RouteFixture(
        name="AI Native final PRD system design document gate",
        prompt="整理最终 PRD / 系分：正式交付文档不要保留讨论过程、迭代草稿、AI 推理轨迹或被拒方案，把过程内容迁移到评审报告、Decision Log、Goal Ledger 或任务计划，只保留当前有效结论和验收",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "spec-template-practices.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native GSD CAD admission gate",
        prompt="做 GSD/CAD 准入：判断是否进入 Round 0、Wave/Atomic Task、CAD 候选缺口和 Execution Grant 缺口",
        routes={"ai-native", "agentic-engineering-governance.md", "gsd-cad-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native GSD CAD default authorization",
        prompt="优化 AI Native GSD 流程：不希望每个任务都单独审批，GSD/CAD 模式下默认授权或自动推进；Codex 替我审批模式用于低风险任务自动通过",
        routes={"ai-native", "agentic-engineering-governance.md", "gsd-cad-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native GSD goal composition",
        prompt="做 GSD + Goal 组合：这个中大型项目需要持续推进，把业务目标、生产可用能力、成功标准、GSD Wave、CAD 候选、验证证据、预算时间盒、停止条件、Goal 状态和交接节奏串起来，不要把 Goal 当 Execution Grant",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "gsd-cad-admission.md", "goal-composition.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native GSD goal plan grant",
        prompt="使用 GSD + Goal 按任务计划推进，不希望每个任务都被 Execution Grant 阻塞；形成 Plan Grant，低风险本地任务直接推进，Git 默认只给提交切片和建议 commit message，联网、生产和高风险业务仍显式确认",
        routes={"ai-native", "agentic-engineering-governance.md", "gsd-cad-admission.md", "goal-composition.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native GSD goal staged commits",
        prompt="使用 GSD + Goal 按任务计划推进，并在每个已验证任务阶段提交代码；形成提交切片和 commit_after_verified_task，但不要 push、不要联网、不要生产操作",
        routes={"ai-native", "agentic-engineering-governance.md", "gsd-cad-admission.md", "goal-composition.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native agent loop engineering",
        prompt="参考 Loop Engineering：用 /goal 或 /loop 持续推进 GSD + Goal，但必须有状态载体、反馈源、自我验证、最大轮次、无进展检测、预算上限、停止条件和交接物，不能把 auto mode 当无条件授权",
        routes={"ai-native", "agentic-engineering-governance.md", "agent-loop-engineering.md", "goal-composition.md", "gsd-cad-admission.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native production ready agent loop",
        prompt="完善 AI 工作量 loop 流程，使其真正生产可用：检查自动化心跳、隔离执行、状态落盘、Skill 上下文、连接器权限、Maker / Checker 解耦、独立验证、观测审计、人工接管、发布回滚和理解债，不能把能自动跑当能上线",
        routes={"ai-native", "agentic-engineering-governance.md", "agent-loop-engineering.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native wisdom lens for loop scheduling",
        prompt="用 Loop 取舍校准增强 AI Native Loop：在准入前、GSD 拆解、执行核验、授权纠偏和复盘回流中，借用 huaxia-wisdom 的阴阳平衡、先为不可胜、庖丁解牛、中庸之道、循名责实、无为而治、每日三省、知行合一和一张一弛做取舍、止损、节奏和停止判断；不要替代事实、测试、CR、授权或上线审批",
        routes={"ai-native", "wisdom-loop-lens.md", "agent-loop-engineering.md", "gsd-cad-admission.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native three card handoff protocol",
        prompt="进入三卡交接：产品专家输出 Product Context Card 和验收种子，AI Native 输出 Engineering Handoff Card，生产可用 Loop 再补 Production Loop Card，缺任一卡都不要进入实现、CAD 或自动 Loop",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "gsd-cad-admission.md", "agent-loop-engineering.md", "verification-review-release.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native GSD loop CAD handoff state machine",
        prompt="进入 GSD + Goal + Loop 协同流程，梳理 Round0 到 Wave Plan、Plan Grant Active、Loop Candidate、CAD Candidate、CAD Loop Active、Verified/Paused/Escalated/Closed 的状态机，并输出 Engineering Handoff Card、Plan Grant + Loop 预算绑定、失败回写和下一 owner",
        routes={"ai-native", "agentic-engineering-governance.md", "agent-loop-engineering.md", "goal-composition.md", "gsd-cad-admission.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native routes Superpowers skills library",
        prompt="下载 superpowers skills，并加入到 AI Native 的调度流程，要求说明哪些外部 skill 可参考、是否安装插件、是否运行脚本、Git/worktree/subagent 边界和验证门禁",
        routes={"ai-native", "agentic-engineering-governance.md", "superpowers-skill-library.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native skill type owner routing",
        prompt="参考 Anthropic 内部 Skills 经验，细化 AI 流程、产品专家和架构师能力，但 AI Native 仍作为主入口；判断产品验证、代码质量、Runbook、CI/CD、模板脚手架、数据分析和基础设施操作分别由谁负责、交接物和验证证据是什么",
        routes={"ai-native", "skill-type-owner-routing.md", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI coding workflow CR",
        prompt="评审我们的 AI 编码流程是否有 OpenSpec、Superpowers、Harness、权限边界、验证矩阵、代码 CR、发布监控和复盘闭环",
        routes={"ai-native", "agentic-engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native code delivery closed loop",
        prompt="我们落地了 SDD / Spec / Harness，AI 编码更快，但 CR、测试、对齐、返工和上线质量没有明显改善。做 AI 代码交付闭环评审，输出瓶颈、Spec 强度、Harness 独立验证、CR 减负、知识回流和一次通过率返工率缺陷密度指标",
        routes={"ai-native", "agentic-engineering-governance.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native spec template practices",
        prompt="落地 Spec 模板最佳实践：把产品上下文和系分交给 AI 编码，先区分 PRD / SDD / 实现 Spec 三层是否齐备，输出 Spec 强度、五段式骨架、AC 与测试映射、spec-lint、AC 覆盖、漂移检查、风险自查和轻重切换",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "spec-template-practices.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native production SDD source of truth",
        prompt="规范驱动开发 SDD：让 AI 写生产级代码，先检查 Spec 是否能作为事实来源，补结构化契约、正反例、边界错误处理、测试计划和五支柱验证，失败时回写 Spec 再重试",
        routes={"ai-native", "agentic-engineering-governance.md", "spec-template-practices.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native knowledge expression gate",
        prompt="进入知识表达门禁：这个需求只有老板一句话、几篇文章和一个 AI 草稿，请判断是否足以让 AI 执行，输出目标、对象、规则、约束、验收样例、反馈源和缺口 owner；不要直接进 GSD/CAD/Loop",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native nonstandard problem mode",
        prompt="进入非标问题模式：客户和运营都说这个能力必须做，但没人能说清标准答案，请先定义问题主体、影响面、已知事实、关键不确定性、研究路径、候选方案、最小可逆实验、决策标准和停止条件",
        routes={"ai-native", "product-to-engineering-lifecycle.md", "agentic-engineering-governance.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native practical coding loop",
        prompt="进入实际项目编码 Loop：这个 GSD Wave 里有一个明确 Task ID，需要在真实代码库持续推进，请给 Coding Loop Contract，包含写入范围、只读范围、失败测试或验收样例、TDD 顺序、验证命令、独立 Checker、状态回写位置、提交切片、回滚方式和停止条件",
        routes={"ai-native", "agent-loop-engineering.md", "gsd-cad-admission.md", "code-delivery-closed-loop.md", "verification-review-release.md", "senior", "testing.md", "workflow.md"},
    ),
    RouteFixture(
        name="AI Native feedback loop verification cluster",
        prompt="AI Coding 已经能快速生成和修复代码，但测试通过和覆盖率提升并不能证明系统没有变坏。请给 AI Native Loop 增加反馈闭环成熟度门禁，围绕支付幂等等高风险业务不变量建立验证簇，说明 L2/L3/L4/L5、生产证据、独立 Checker、预算和停止条件",
        routes={"ai-native", "agent-loop-engineering.md", "verification-review-release.md", "senior", "testing.md"},
    ),
    RouteFixture(
        name="AI Native architecture entropy loop",
        prompt="进入架构排熵 Loop：系统长期只加不删，出现承重 bug、废弃 API、循环依赖、概念膨胀、治理规则失效和局部性丧失。请设计持续巡检、状态回写、低风险修复、Maker/Checker、人工 triage、守卫自检和停止条件，不要把能扫描当成能自动删除",
        routes={"ai-native", "agent-loop-engineering.md", "verification-review-release.md", "senior", "evolutionary-architecture.md", "coding-review-deep-dive.md"},
    ),
    RouteFixture(
        name="AI Native quality test gate",
        prompt="做质量门禁：输出测试矩阵、验证顺序、CR 前置条件、失败回退和架构师 testing.md 调用点",
        routes={"ai-native", "verification-review-release.md", "agentic-engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native change understanding gate",
        prompt="做理解门禁：把这次 diff / 重构计划整理成入口路径、影响模块、调用关系、源码锚点、验证证据和 CR 交接条件",
        routes={"ai-native", "verification-review-release.md", "agentic-engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native codebase understanding brief",
        prompt="最近 Google Gemini CLI 和 Microsoft AgentRC 这类工具能快速阅读代码库、生成上下文和总结结论，帮我抽象进 AI Native 研发流程，设计代码库理解结论包和进入架构师 CR 的门禁，但不要默认安装工具",
        routes={"ai-native", "verification-review-release.md", "agentic-engineering-governance.md", "code-understanding-tools.md"},
    ),
    RouteFixture(
        name="AI Native Ponytail minimal implementation admission",
        prompt="用 AI Native Engineering Loop 评估 Ponytail 是否适合加入编码 Loop：要求编码前做最小正确实现检查，CR 时做过度设计专项检查，但不要默认启用 hook 或替代 TDD、安全和架构师源码级 Review",
        routes={"ai-native", "code-understanding-tools.md", "verification-review-release.md", "source-map.md", "senior", "coding-review-deep-dive.md", "coding-standards.md"},
    ),
    RouteFixture(
        name="AI Native authorized learning and knowledge flow",
        prompt="参考让 Codex 越用越聪明的方法，完善 AI 流程里的经验回流、授权学习、知识归位和不要把用户长期偏好写进仓库的边界",
        routes={"ai-native", "agentic-engineering-governance.md", "code-delivery-closed-loop.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native visual understanding for unfamiliar codebase",
        prompt="这个陌生多 Agent 代码库看不懂，先做图形化理解和架构描述转图的门禁，说明组件入口、启动顺序、认证权限、外部系统、数据消息流、源码锚点和进入 CR 的条件",
        routes={"ai-native", "verification-review-release.md", "agentic-engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native read analyze codebase",
        prompt="阅读分析代码库：先做代码库理解结论包；评估是否需要 Gemini CLI / AgentRC / Understand Anything，但不要默认安装或联网",
        routes={"ai-native", "verification-review-release.md", "agentic-engineering-governance.md", "code-understanding-tools.md"},
    ),
    RouteFixture(
        name="AI Native tool install admission",
        prompt="评估 Gemini CLI / AgentRC / Understand Anything：列来源、安装认证联网写入边界、只读范围、隐私风险、人工替代路径和 CR 条件；Understand Anything 还要列 .understand-anything、dashboard、auto-update、hook 和图谱提交边界",
        routes={"ai-native", "code-understanding-tools.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native Understand Anything knowledge graph admission",
        prompt="用 AI Native 研发流程编排评估是否需要安装 Understand Anything：大型代码库需要生成代码库知识图谱、dashboard、diff impact 和 onboarding guide；先列安装联网写 ~/.understand-anything 和项目 .understand-anything、auto-update、post-commit hook、图谱提交、敏感文件排除和 CR owner，不要默认安装",
        routes={"ai-native", "code-understanding-tools.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native design code alignment",
        prompt="做设计-代码对齐：对齐 OpenSpec / 系分设计与当前代码，输出设计条款、代码入口、实现状态、偏差和测试证据",
        routes={"ai-native", "code-understanding-tools.md", "verification-review-release.md", "agentic-engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native fact boundary check",
        prompt="做事实边界检查：这份 AI 生成的 GSD/CAD 流程里有推测和额外实现建议，请区分事实、推断、待确认和范围外不做，禁止无根据猜测、模型脑补或超出用户目标的实现扩张",
        routes={"ai-native", "agentic-engineering-governance.md", "gsd-cad-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native routes PRD work",
        prompt="用 AI Native 研发流程编排先判断这批客户访谈和运营后台截图能否进入 PRD，输出成熟度、owner、交接物和停止条件，再分派给产品架构专家写正文",
        routes={"ai-native", "product-to-engineering-lifecycle.md"},
    ),
    RouteFixture(
        name="AI Native routes CR work",
        prompt="用 AI Native 研发流程编排先判断这次 Spring Boot Service 代码 CR 是否需要 OpenSpec、Harness、验证矩阵和发布闭环，再交给资深架构师执行 CR",
        routes={"ai-native", "agentic-engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native routes codegen work",
        prompt="用 AI Native 研发流程编排先评估这段 CREATE TABLE 是否具备生成 Java Service 配套代码的结构化输入、写入范围和覆盖风险，再分派给 java-service-code-generator",
        routes={"ai-native"},
    ),
    RouteFixture(
        name="architecture diagram output",
        prompt="画一张系统架构图和状态机，说明工程落点和验证方式",
        routes={"senior", "diagram-output.md"},
    ),
    RouteFixture(
        name="senior nonstandard engineering problem",
        prompt="这是一个跨订单支付账务的非标工程问题，没有现成 SOP，线上状态偶发不一致。请先输出问题机制、影响面、证据、关键不确定性、候选方案、最小可逆实验、验证命令、写入边界和停止条件，不要直接大范围重构",
        routes={"senior", "architecture.md", "adr-and-tradeoff.md", "workflow.md", "testing.md"},
    ),
    RouteFixture(
        name="senior invariant verification cluster",
        prompt="支付幂等和账务状态机是高风险域，AI 补了很多测试但语义仍然不强。请基于核心业务不变量设计验证簇，而不是盲目堆覆盖率，区分场景测试、属性/变形测试、历史回归、生产重放样本、有限变异/对抗检查、置信度和 CI 分层",
        routes={"senior", "testing.md", "workflow.md"},
    ),
    RouteFixture(
        name="external sdk freshness ignores case",
        prompt="升级 gemini sdk 并确认最新 api 用法和兼容性",
        routes={"senior", "workflow.md", "adr-and-tradeoff.md", "production-readiness.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="PRD",
        prompt="帮我生成一份产品 PRD 模板，包含验收标准",
        routes={"product", "product-scenario-routing.md", "product-prd-template.md", "product-design-and-prd.md"},
    ),
    RouteFixture(
        name="prototype to PRD",
        prompt="我有一份运营后台页面截图和交互稿，帮我反推成可评审 PRD，并列出待确认问题",
        routes={"product", "product-scenario-routing.md", "product-prd-template.md", "product-design-and-prd.md"},
    ),
    RouteFixture(
        name="payment product",
        prompt="设计商户清结算和对账产品方案，注意外部规则和合规",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="payment ledger perspective product",
        prompt="设计一个平台代收代付的多套账本产品方案，说明客户可见余额、内部账本、备付金真实资金、代理结算和会计账如何对齐",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="airwallex global platform product",
        prompt="参考 Airwallex Docs 设计全球金融平台产品能力地图，覆盖 Global Accounts、Payouts、Issuing 和 Embedded Finance",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="global accounts payouts product",
        prompt="设计 Global Accounts + Payouts 的多币种资金运营产品方案，包含受益人、付款审批、失败回执和对账",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="embedded finance responsibility product",
        prompt="设计一个 BaaS 白标金融产品方案，重点说明平台责任、用户解释视图、Transactional FX 和费用舍入口径",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="global financial platform deliverable package",
        prompt="做一份 Airwallex 类全球金融平台 PRD 交付包，包含对象生命周期、运营成熟度、go-live 和退出留存",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="AI outbound global treasury product",
        prompt="参考万里汇和 WorldFirst 这类能力，设计 AI 出海全球资金管理产品方案，覆盖 token 计费、批量付款、Agent 支付和 VCC 控制",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="acquiring mastercard product",
        prompt="设计外卡收单 Mastercard 清算和商户到账产品方案，覆盖 Clearing Core、merchant payout 和收单风控",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
    RouteFixture(
        name="complex non-payment product",
        prompt="设计一个 SaaS B2B 运营后台产品方案，包含角色权限、能力地图、规则矩阵和验收标准",
        routes={"product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="product acceptance seeds for tdd handoff",
        prompt="会员权益产品方案要交给架构师按 TDD 推进，请补验收种子，区分可代码化、可观测化和可评审化，不要写工程测试代码",
        routes={"product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="product AI-shaped readiness review",
        prompt="评估一下产品团队的 AI-shaped readiness，看看 AI 工作流是不是只在提效，还是形成了可复盘的产品优势",
        routes={"product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="product brainstorming exploration",
        prompt="先不要写 PRD，帮我做一次产品头脑风暴和问题探索，用 HMW、第一性原理、OODA、逆向头脑风暴挑战关键假设，输出下一步验证动作",
        routes={"product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="product insight opportunity radar",
        prompt="这里有一批客户访谈、工单、竞品动态和行业资料，请帮我做产品洞察，输出机会雷达，说明证据来源、推理链、置信度和哪些机会可以进入 Backlog",
        routes={"product", "product-scenario-routing.md", "product-insight-analyst.md"},
    ),
    RouteFixture(
        name="product deliberation AI generated PRD",
        prompt="这份 AI 生成的会员权益 PRD 有点发散，请用产品大师/MAGI 的方式做多视角合议评审，输出共识、分歧、必改、待确认、owner 和验证方式，先不要重写全文",
        routes={"product", "product-scenario-routing.md", "product-deliberation-workflow.md"},
    ),
    RouteFixture(
        name="product backlog decision from opportunity list",
        prompt="这里有 15 个客户、销售和老板提的机会点，请帮我做 Backlog 决策，按 BV/EE 排 P0/P1/P2，并转成 User Story 和 AC，说明哪些要拒绝或延后",
        routes={"product", "product-scenario-routing.md", "po-backlog-manager.md"},
    ),
    RouteFixture(
        name="product nonstandard problem solution",
        prompt="老板、销售和客户都说要做一个智能运营能力，但表达很散，UED 也反馈现有流程交互阻塞。请不要做传话筒，先输出真实问题、影响面、失败成本、当前替代方式、目标用户、解决方案假设、验收种子、UED 重点验证的交互状态和下一步验证动作",
        routes={"product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native product context to GSD CAD handoff",
        prompt="业务方已经 dogfooding 出一个 MVP，想按 AI Native Product Builder 流程 harden 成产品上下文包，再交给架构师接入 GSD 和 CAD，判断能不能进 Execution Grant",
        routes={"product", "product-scenario-routing.md", "senior", "workflow.md", "ai-assisted-engineering.md", "ai-large-project-orchestration.md", "cad-mode.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="product manager methodology calibration",
        prompt="阅读一下产品经理方法论这本书，看一下对于产品专家的基础能力是否可以补齐",
        routes={"product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="product diagram output",
        prompt="为 SaaS B2B 运营后台画能力地图、流程图和状态机，输出可视化产物",
        routes={"product", "product-scenario-routing.md", "diagram-output.md"},
    ),
    RouteFixture(
        name="product capability map diagram",
        prompt="画一张能力地图，说明角色、业务流程图和验收路径",
        routes={"product", "product-scenario-routing.md", "diagram-output.md"},
    ),
    RouteFixture(
        name="payment funds flow diagram",
        prompt="画一张资金流图，区分业务流、支付信息流、账务流和真实资金流",
        routes={"product", "payment-scenario-routing.md", "regulatory-baseline.md", "diagram-output.md"},
    ),
    RouteFixture(
        name="java service generator structured input",
        prompt="根据 sql 建表语句和 schema 表结构生成 wind/nobe 配套代码",
        routes=codegen_route,
    ),
    RouteFixture(
        name="java service generator field table",
        prompt="根据字段说明转换成 Wind/Nobe Entity 和 Service",
        routes=codegen_route,
    ),
    RouteFixture(
        name="java service generator safety guard",
        prompt="根据 DDL 生成 Wind/Nobe Service，但已有文件会覆盖且有多个 face/impl 模块对",
        routes=codegen_safety_route,
    ),
]

negative_route_fixtures: list[RouteFixture] = [
    RouteFixture(
        name="codegen on java service review or tests",
        prompt="对这个 Java 类的 Service 做一次 CR 并补测试，重点看契约和空值",
        routes=codegen_route,
    ),
    RouteFixture(
        name="product on bug screenshot",
        prompt="这张错误截图显示 NullPointerException，帮我定位根因并补回归测试",
        routes={"product", "product-scenario-routing.md", "product-prd-template.md", "product-design-and-prd.md"},
    ),
    RouteFixture(
        name="ai native on ordinary PRD",
        prompt="根据这批客户访谈和运营后台截图写一版可评审 PRD，补齐角色、对象、流程、规则、数据指标和验收标准",
        routes={"ai-native"},
    ),
    RouteFixture(
        name="ai native on concrete code review",
        prompt="做一轮代码 CR：这个 Spring Boot Service 改了事务边界、缓存一致性和异常处理，帮我按严重级别列问题并补测试建议",
        routes={"ai-native"},
    ),
    RouteFixture(
        name="ai native on java service codegen",
        prompt="根据这段 CREATE TABLE 生成 Wind/Nobe 风格 Entity、Mapper、DTO、Request、Query、Converter、Service 和 ServiceImpl",
        routes={"ai-native"},
    ),
]


def routes_codegen(prompt: str) -> bool:
    """Structured input becomes codegen only with source, action, and target intent."""
    return (
        contains_any(prompt, codegen_source_terms)
        and contains_any(prompt, codegen_action_terms)
        and contains_any(prompt, codegen_target_terms)
    )


def route_fixture(prompt: str) -> set[str]:
    """Tiny deterministic route simulation for high-value regression fixtures."""
    route: set[str] = set()
    if contains_any(prompt, ["意图到生产交付", "从意图", "需求收集", "生产交付闭环", "Intent-to-Production", "多角色分工", "阶段分工", "角色协作 Loop", "设计评审", "编码评审", "可用性安全性评估", "可用性 / 安全性", "按设计、设计评审、TDD、编码", "自我挖掘", "自主交付控制卡", "人工确认边界"]):
        route.update(
            {
                "ai-native",
                "intent-to-production-loop.md",
                "product-to-engineering-lifecycle.md",
                "prd-system-design-review.md",
                "agentic-engineering-governance.md",
                "agent-loop-engineering.md",
                "verification-review-release.md",
            }
        )
    if contains_any(
        prompt,
        [
            "需求 / 设计 / 编码标准门禁",
            "开发标准门禁",
            "需求基线稳定性",
            "需求标准",
            "设计标准",
            "编码标准",
            "HLR/LLR",
            "防御式编程",
        ],
    ):
        route.update(
            {
                "ai-native",
                "product-to-engineering-lifecycle.md",
                "prd-system-design-review.md",
                "spec-template-practices.md",
                "verification-review-release.md",
            }
        )
    if contains_any(prompt, ai_native_terms) and contains_any(prompt, ["流程", "编排", "交接", "评估", "评审", "判断", "检查", "分派", "路由", "成熟度", "owner", "停止条件", "验证矩阵", "知识表达门禁", "意图可执行", "Knowledge-to-Execution", "非标问题模式", "实际项目编码 Loop", "Coding Loop Contract", "架构排熵", "架构排熵 Loop", "腐朽门禁", "可删除性", "承重 bug", "承重行为", "废弃 API", "治理自腐", "守卫自检", "Architecture Entropy Card", "需求分析协同门禁", "需求分析结论卡", "问题核心诊断", "问题核心诊断门禁", "抓住问题的核心", "需求无止境", "概念定名", "需求止损", "价值 / 意义边界", "定向", "定性", "定位", "定量", "整体 / 系统 / 科学", "病 / 证 / 症", "产品 / 系统 DNA 门禁", "系统 DNA", "产品 DNA", "业务不变量", "状态流转", "演化规则", "功能先行、规则后补", "根源需求", "产品定义", "产品边界", "稳定点/变化点", "稳定点 / 变化点", "边界坐标", "上下游分工", "事实边界检查", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "超出用户目标", "质量/测试门禁", "质量门禁", "测试门禁", "理解门禁", "合议预审", "MAGI 三角色", "A2A 虚拟评审", "IPD 式互审", "ACCEPT/REJECT/PENDING", "PRD 评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "疑似问题", "追问点", "整理最终", "最终文档准出", "正式交付文档", "讨论过程", "迭代草稿", "过程资产", "过程记录链接", "代码库理解结论包", "AI 快速阅读代码", "快速阅读代码库", "变更可理解性", "影响可视化", "图形化理解", "架构描述转图", "发布复盘", "职责边界", "安装", "调用", "下载", "接入", "加入", "阅读", "分析代码", "设计-代码对齐", "对齐设计", "AI-readiness", "上下文漂移", "交付闭环", "Spec 强度", "事实来源", "生产级代码", "结构化契约", "五支柱验证", "回写 Spec", "独立验证", "CR 减负", "知识回流", "经验回流", "授权学习", "经验归位", "自我挖掘", "自主交付控制卡", "人工确认边界", "必须人工确认", "默认授权", "授权策略", "自动推进", "替我审批", "审批", "自动通过", "一次通过率", "返工率", "缺陷密度", "模板最佳实践", "五段式骨架", "AC 覆盖", "spec-lint", "漂移检查", "Given-When-Then", "Goal", "Goal 组合", "目标驱动", "持续推进", "Goal 卡", "目标状态", "预算时间盒", "预算 / 时间盒", "Loop", "Agent Loop", "Loop Engineering", "Agent 闭环工程", "生产可用 Loop", "生产可用门禁", "自动化心跳", "状态落盘", "可复现状态", "隔离执行", "Maker / Checker", "观测审计", "人工接管", "发布回滚", "发布/回滚", "理解债", "/goal", "/loop", "auto mode", "后台 Agent", "多 Agent 监督", "自我验证", "最大轮次", "无进展检测", "预算上限", "Ponytail", "最小正确实现", "过度设计 CR"]):
        route.add("ai-native")
        if contains_any(prompt, ["AI 原型/eval", "PRD-Lite", "产品上下文", "产品上下文包", "dogfooding", "业务", "业务目标", "PRD", "Backlog", "客户访谈", "产品架构专家", "产品专家", "需求分析", "知识表达门禁", "意图可执行", "Knowledge-to-Execution", "非标问题模式", "问题主体", "影响面", "关键不确定性", "候选方案", "最小可逆实验", "需求分析协同门禁", "需求分析结论卡", "问题核心诊断", "需求无止境", "概念定名", "需求止损", "价值 / 意义边界", "产品 / 系统 DNA", "产品 DNA", "业务不变量", "状态流转", "演化规则", "功能先行、规则后补", "根源需求", "产品定义", "产品边界", "稳定点/变化点", "稳定点 / 变化点", "边界坐标", "上下游分工", "产品设计", "方案确认", "验收种子", "交接物"]):
            route.add("product-to-engineering-lifecycle.md")
        if contains_any(prompt, ["PRD/系分合议预审", "系分预审", "PRD / 系分预审", "合议预审", "MAGI 三角色", "A2A 虚拟评审", "IPD 式互审", "review_task", "evaluation_task", "reporting_task", "ACCEPT/REJECT/PENDING", "接受项", "分歧项", "风险清单", "PRD 评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "疑似问题", "追问点", "整理最终 PRD", "整理最终", "最终文档准出", "正式交付文档", "讨论过程", "迭代草稿", "过程资产", "过程记录链接", "被拒方案", "需求分析协同门禁", "需求分析结论卡", "根源需求", "产品定义", "产品边界", "稳定点/变化点", "稳定点 / 变化点", "边界坐标", "需求 CR", "CR 需求"]):
            route.add("prd-system-design-review.md")
        if contains_any(prompt, ["OpenSpec", "Superpowers", "Harness", "GSD", "CAD", "Execution Grant", "权限边界", "Agentic Engineering", "代码 CR", "Spring Boot", "资深架构师", "架构师", "系分设计", "编码", "TDD", "问题核心诊断", "抓住问题的核心", "病机", "病 / 证 / 症", "定向", "定性", "定位", "定量", "系统 DNA", "产品 / 系统 DNA", "不变量", "状态流转", "演化规则", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "超出用户目标", "质量门禁", "测试矩阵", "验证顺序", "多文件 diff", "重构计划", "快速阅读代码库", "代码库理解结论包", "图形化理解", "架构描述转图", "入口路径", "源码锚点", "调用关系", "边界变化", "SDD", "规范驱动开发", "生产级代码", "Spec 强度", "事实来源", "五支柱验证", "交付闭环", "独立验证", "CR 减负", "知识回流", "经验回流", "授权学习", "经验归位", "默认授权", "授权策略", "自动推进", "替我审批", "审批", "自动通过", "模板最佳实践", "AC 与测试映射", "spec-lint", "AC 覆盖", "漂移检查", "Goal", "Goal 组合", "目标驱动", "持续推进"]):
            route.add("agentic-engineering-governance.md")
        if contains_any(prompt, ["GSD + Goal", "Goal 组合", "Goal 卡", "CAD + Goal", "Spec + Goal", "目标驱动", "持续推进", "目标状态", "Goal 状态", "预算时间盒", "预算 / 时间盒", "Goal Ledger"]):
            route.add("goal-composition.md")
        if contains_any(prompt, ["Agent Loop", "Loop Engineering", "Agent 闭环工程", "实际项目编码 Loop", "Coding Loop Contract", "反馈闭环成熟度", "验证簇", "不变量验证簇", "L2/L3/L4/L5", "L2 / L3 / L4 / L5", "架构排熵", "架构排熵 Loop", "腐朽门禁", "Architecture Entropy Card", "可删除性", "承重 bug", "承重行为", "废弃 API", "dead path", "治理自腐", "守卫自检", "人工 triage", "写 Loop", "Loop", "/goal", "/loop", "auto mode", "后台 Agent", "持续编排", "多 Agent 监督", "自我挖掘", "自主交付控制卡", "人工确认边界", "自我验证", "最大轮次", "无进展检测", "预算上限", "Loop 停止条件", "状态载体", "反馈源", "验证者", "生产可用 Loop", "生产可用门禁", "自动化心跳", "状态落盘", "可复现状态", "隔离执行", "Maker / Checker", "独立 Checker", "观测审计", "人工接管", "发布回滚", "发布/回滚", "理解债"]):
            route.add("agent-loop-engineering.md")
            route.add("agentic-engineering-governance.md")
            route.add("verification-review-release.md")
            if contains_any(prompt, ["架构排熵", "腐朽", "可删除性", "承重", "废弃 API", "dead path", "循环依赖", "治理规则", "治理自腐", "守卫自检", "局部性"]):
                route.update({"senior", "evolutionary-architecture.md", "coding-review-deep-dive.md"})
            if contains_any(prompt, ["GSD", "CAD", "Plan Grant", "Wave", "Atomic Task", "Execution Grant", "Task ID", "提交切片"]):
                route.add("gsd-cad-admission.md")
            if contains_any(prompt, ["Goal", "GSD + Goal", "目标", "Goal Ledger"]):
                route.add("goal-composition.md")
            if contains_any(prompt, ["交付", "代码", "CR", "测试", "失败测试", "TDD", "Spec", "回写", "返工", "缺陷", "验证", "验证命令", "状态回写", "生产可用", "能上线", "发布回滚", "发布/回滚", "观测审计", "人工接管"]):
                route.add("code-delivery-closed-loop.md")
        if contains_any(prompt, wisdom_lens_terms):
            route.add("wisdom-loop-lens.md")
            route.add("agent-loop-engineering.md")
            route.add("verification-review-release.md")
            route.add("source-map.md")
            if contains_any(prompt, ["GSD", "CAD", "Grant", "授权", "拆解", "Wave", "Atomic Task", "Execution Grant", "执行核验"]):
                route.add("gsd-cad-admission.md")
        if contains_any(prompt, ["Spec 模板", "Spec/SDD 模板", "模板最佳实践", "规范驱动开发", "事实来源", "系统 DNA", "不变量", "状态流转", "结构化契约", "正例 / 反例", "正反例", "边界/错误处理", "边界错误处理", "五支柱验证", "PRD / SDD / 实现 Spec", "实现 Spec", "三层边界", "AC 验收", "AC 与测试映射", "Given-When-Then", "spec-lint", "AC 覆盖", "漂移检查", "五段式骨架", "风险自查", "最终文档准出", "正式交付文档", "过程资产"]):
            route.add("spec-template-practices.md")
        if contains_any(prompt, ["AI 代码交付闭环", "代码交付闭环", "交付闭环", "SDD", "生产级代码", "生产可用 Loop", "生产可用门禁", "Spec 强度", "编码提速", "交付体感", "生成失败", "反复返工", "回写 Spec", "重试", "AI 错误模式", "独立验证", "CR 减负", "知识回流", "经验回流", "授权学习", "经验归位", "一次通过率", "返工率", "缺陷密度", "spec-lint", "AC 覆盖", "漂移检查", "状态落盘", "可复现状态", "Maker / Checker", "观测审计", "人工接管", "发布回滚", "发布/回滚", "自我挖掘", "自主交付控制卡", "完成判断"]):
            route.add("code-delivery-closed-loop.md")
        if contains_any(prompt, ["Gemini CLI", "AgentRC", "Understand Anything", "Ponytail", "最小正确实现", "过度设计 CR", "AI 代码阅读工具", "代码理解工具", "上下文工程", "知识图谱", "代码库知识图谱", ".understand-anything", "understand-dashboard", "dashboard", "diff impact", "onboarding guide", "auto-update", "post-commit hook", "图谱提交", "agent instructions", "AI-readiness", "readiness", "instructions", "eval", "MCP 配置", "上下文漂移", "安装", "调用", "设计-代码对齐", "对齐设计和代码", "代码入口", "实现状态", "偏差"]):
            route.add("code-understanding-tools.md")
        if contains_any(prompt, ["Superpowers skills", "superpowers skills", "brainstorming", "writing-plans", "executing-plans", "subagent-driven-development", "test-driven-development", "requesting-code-review", "verification-before-completion", "外部 skill", "外部技能", "下载", "接入", "加入"]):
            route.add("superpowers-skill-library.md")
            route.add("source-map.md")
        if contains_any(prompt, ["Skill 类型", "Skill 分类经验", "Anthropic 内部 Skills", "Anthropic内部Skills", "拆分", "细化", "产品验证", "代码质量", "Runbook", "CI/CD", "模板脚手架", "团队自动化", "数据分析", "基础设施操作"]):
            route.add("skill-type-owner-routing.md")
            route.add("product-to-engineering-lifecycle.md")
            route.add("verification-review-release.md")
        if contains_any(prompt, ["GSD/CAD 编排准入", "GSD/CAD 准入", "Harness/GSD/CAD 准入", "GSD Round 0", "Atomic Task", "GSD Wave", "CAD 原子任务", "CAD 候选缺口", "Execution Grant 缺口", "三卡交接", "Engineering Handoff Card", "工程执行交接卡", "Production Loop Card", "生产 Loop 交接卡", "产品 / 系统 DNA", "系统 DNA", "产品 DNA", "业务不变量", "状态流转", "演化规则", "默认授权", "授权策略", "自动推进", "替我审批", "审批", "自动通过", "Wave Grant", "CAD Grant", "事实边界检查", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "产研协同研发流程", "中大型项目", "大项目", "Wave/Atomic Task", "GSD + Goal", "需求分析协同门禁", "需求分析结论卡"]):
            route.add("gsd-cad-admission.md")
        if contains_any(prompt, ["验证矩阵", "知识表达门禁", "意图可执行", "反馈源", "缺口 owner", "反馈闭环成熟度", "验证簇", "不变量验证簇", "高风险业务不变量", "生产重放", "变异测试", "对抗测试", "置信度", "事实边界检查", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "超出用户目标", "质量/测试门禁", "质量门禁", "测试门禁", "五支柱验证", "安全/测试/代码质量/性能/发布就绪", "生产级代码", "理解门禁", "代码库理解结论包", "AI 快速阅读代码", "快速阅读代码库", "变更可理解性", "影响可视化", "图形化理解", "架构描述转图", "测试矩阵", "验证顺序", "CR 前置条件", "失败回退", "testing.md", "TDD", "代码 CR", "CR", "多文件 diff", "重构计划", "入口路径", "源码锚点", "调用关系", "边界变化", "验证证据", "验证", "验证命令", "失败测试", "独立 Checker", "状态回写", "发布", "监控", "复盘", "Harness Plan", "Execution Grant", "默认授权", "授权策略", "显式确认", "替我审批", "自动推进", "经验回流", "授权学习", "经验归位", "知识归位", "设计-代码对齐", "代码入口", "实现状态", "偏差", "测试证据", "独立验证", "一次通过率", "返工率", "缺陷密度", "spec-lint", "AC 覆盖", "漂移检查", "AC 与测试映射", "Goal", "Goal 状态", "成功标准", "目标状态"]):
            route.add("verification-review-release.md")
        if contains_any(prompt, ["外部文章", "工具能力", "官方", "来源", "Gemini CLI", "AgentRC", "Understand Anything", "Ponytail", "知识图谱工具", "Clarity Agent"]):
            route.add("source-map.md")
    if contains_any(
        prompt,
        [
            "代码",
            "测试",
            "TDD",
            "失败测试",
            "验证簇",
            "不变量验证簇",
            "高风险业务不变量",
            "生产重放",
            "变异测试",
            "对抗测试",
            "陌生代码库",
            "架构现状",
            "接手侦察",
            "Node.js",
            "技术栈",
            "入口路径",
            "部署链路",
            "架构坏味",
            "架构腐朽",
            "架构排熵",
            "可删除性",
            "承重 bug",
            "承重行为",
            "废弃 API",
            "治理自腐",
            "守卫自检",
            "深度质量扫描",
            "上帝类",
            "循环依赖",
            "跨层调用",
            "事务边界混乱",
            "公共模块垃圾桶",
            "时间线",
            "5-Why",
            "故障复盘",
            "事故复盘",
            "线上复盘",
            "生产复盘",
            "回调大量超时",
            "Spring Security",
            "CSRF",
            "CORS",
            "NullPointerException",
            "根因",
            "OpenSpec",
            "Superpowers",
            "Harness",
            "AI 编码",
            "编码约规",
            "流程能力",
            "Agent",
            "CAD",
            "SDK",
            "API",
            "架构图",
            "流程图",
            "时序图",
            "状态机",
            "ER 图",
            "类图",
            "部署图",
            "迁移图",
            "非标工程问题",
            "无标准答案",
            "没有现成 SOP",
            "问题机制",
            "最小可逆实验",
        ],
    ):
        route.add("senior")
    if contains_any(prompt, ["非标工程问题", "无标准答案", "没有现成 SOP", "问题机制", "关键不确定性", "最小可逆实验", "写入边界"]):
        route.update({"architecture.md", "adr-and-tradeoff.md", "workflow.md"})
        if contains_any(prompt, ["验证命令", "失败测试", "TDD", "测试"]):
            route.add("testing.md")
    if contains_any(prompt, ["陌生代码库", "架构现状", "接手侦察", "Node.js", "技术栈", "入口路径", "部署链路"]):
        route.update({"language-agnostic-architecture.md", "workflow.md"})
    if contains_any(prompt, ["架构坏味", "深度质量扫描", "上帝类", "循环依赖", "跨层调用", "事务边界混乱", "公共模块垃圾桶", "InMemory", "内存版业务 Service", "Map 存储实现"]):
        route.update({"coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md"})
        if contains_any(prompt, ["Java", "Spring"]):
            route.add("coding-standards.md")
    if contains_any(prompt, ["架构腐朽", "架构排熵", "可删除性", "不敢删", "承重 bug", "承重行为", "废弃 API", "dead path", "final 版本", "治理规则失效", "治理自腐", "守卫自检", "最小排熵"]):
        route.update({"senior", "evolutionary-architecture.md", "coding-review-deep-dive.md", "adr-and-tradeoff.md", "production-readiness.md"})
    if contains_any(prompt, ["时间线", "5-Why", "故障复盘", "事故复盘", "线上复盘", "生产复盘", "回调大量超时", "影响面", "止血"]):
        route.update({"debugging-diagnosis.md", "production-readiness.md", "negative-constraints.md"})
    if contains_any(prompt, ["Spring Security", "CSRF", "CORS"]):
        route.update({"security-architecture.md", "negative-constraints.md"})
    if contains_any(prompt, product_terms):
        route.add("product")
    if contains_any(prompt, ["测试", "TDD", "失败测试", "验证簇", "不变量验证簇", "高风险业务不变量", "生产重放", "变异测试", "对抗测试", "覆盖率"]):
        route.update({"testing.md", "coding-standards.md", "workflow.md"})
    if contains_any(prompt, ["实际项目编码 Loop", "Coding Loop Contract", "代码写入范围", "只读范围", "状态回写位置", "提交切片"]):
        route.update({"senior", "testing.md", "workflow.md"})
    if contains_any(prompt, ["Ponytail", "最小正确实现", "过度设计 CR", "过度设计专项", "源码级 Review"]):
        route.update({"senior", "coding-review-deep-dive.md", "coding-standards.md"})
    if contains_any(prompt, ["NullPointerException", "根因", "线上"]):
        route.update({"debugging-diagnosis.md", "testing.md", "workflow.md"})
    if contains_any(prompt, ["OpenSpec", "Superpowers", "Harness", "AI 编码", "编码约规", "流程能力", "Agent", "CAD"]):
        route.update({"workflow.md", "ai-assisted-engineering.md", "negative-constraints.md"})
    if contains_any(prompt, ["GSD", "中大型", "大项目", "长任务", "上下文衰减", "Wave", "暂停恢复", "Harness"]):
        route.update({"senior", "workflow.md", "ai-assisted-engineering.md", "ai-large-project-orchestration.md", "negative-constraints.md"})
    if contains_any(prompt, ["CAD", "Execution Grant", "自动分轮", "自动提交"]):
        route.add("cad-mode.md")
    if contains_any(prompt, external_dependency_terms):
        route.update({"workflow.md", "adr-and-tradeoff.md", "production-readiness.md", "negative-constraints.md"})
    if contains_any(prompt, ["PRD", "模板"]):
        route.update({"product-scenario-routing.md", "product-prd-template.md", "product-design-and-prd.md"})
    if contains_any(prompt, ["需求评审", "评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "疑似问题", "追问点"]):
        route.update({"product-scenario-routing.md", "product-prd-quality-gates.md", "product-design-and-prd.md"})
    if contains_any(prompt, payment_terms):
        route.update({"payment-scenario-routing.md", "regulatory-baseline.md"})
    if contains_any(prompt, product_general_route_terms):
        route.update({"product-scenario-routing.md"})
    if contains_any(prompt, ["产品洞察", "需求洞察", "资料资产化", "机会雷达", "客户访谈", "竞品动态", "标杆实践", "证据来源", "推理链"]):
        route.add("product-insight-analyst.md")
    if contains_any(prompt, ["产品大师", "MAGI", "多视角", "合议评审", "PM/Reviewer", "Reviewer", "AI 生成的", "AI 生成方案"]):
        route.add("product-deliberation-workflow.md")
    if contains_any(prompt, ["Backlog", "机会清单", "机会点", "需求池", "需求优先级", "P0/P1/P2", "User Story"]):
        route.add("po-backlog-manager.md")
    if contains_any(prompt, diagram_terms):
        route.add("diagram-output.md")
    if routes_codegen(prompt):
        route.update(codegen_route)
        if contains_any(prompt, codegen_safety_terms):
            route.add("requires-confirmation")
    return route


for fixture in scenario_fixtures:
    expected_subset(fixture.name, route_fixture(fixture.prompt), fixture.routes)

for fixture in negative_route_fixtures:
    expected_absent(fixture.name, route_fixture(fixture.prompt), fixture.routes)

ai_native_outline_terms = (
    "默认输出骨架",
    "结论",
    "角色 Loop 场景视图",
    "owner/下一步分派",
    "交接物",
    "Loop Contract",
    "证据边界",
    "验证门禁",
    "停止条件",
    "残余风险",
)

for case_id in [
    "ai-native-should-end-to-end-product-engineering-workflow",
    "ai-native-should-gsd-cad-handoff",
    "ai-native-should-compress-gsd-cad-goal-into-loop",
    "ai-native-should-gsd-product-engineering-collaboration",
    "ai-native-should-demand-analysis-collaboration-gate",
    "ai-native-should-development-standards-gate",
    "ai-native-should-intent-to-production-role-loop",
    "ai-native-should-autonomous-discovery-to-delivery-loop",
    "ai-native-should-role-collaboration-loop-main-flow",
    "ai-native-should-knowledge-expression-gate",
    "ai-native-should-nonstandard-problem-mode",
    "ai-native-should-practical-coding-loop",
    "ai-native-should-feedback-loop-verification-cluster",
    "ai-native-should-architecture-entropy-loop",
    "ai-native-should-plan-to-goal-bridge-without-new-flow",
    "ai-native-should-gsd-cad-admission-gate",
    "ai-native-should-gsd-goal-composition",
    "ai-native-should-agent-loop-engineering",
    "ai-native-should-design-engineering-loop-not-prompting",
    "ai-native-should-wisdom-lens-loop-scheduling",
    "ai-native-should-review-ai-coding-process",
    "ai-native-should-code-delivery-closed-loop",
    "ai-native-should-fact-boundary-check",
    "ai-native-should-route-prd-work",
    "ai-native-should-route-cr-work",
]:
    expected_handling_has(case_id, ai_native_outline_terms)

expected_handling_has(
    "ai-native-should-intent-to-production-role-loop",
    (
        "角色协作 Loop",
        "意图到生产交付角色 Loop",
        "Role Collaboration Loop Map",
        "Intent-to-Production Role Loop Map",
        "能力/约规来源",
        "意图收集",
        "需求事实分层",
        "产品/交互设计",
        "设计评审",
        "TDD/测试设计",
        "编码实现/AI Maker",
        "编码评审/AI Checker",
        "可用性/安全性/可靠性评估",
        "验证发布",
        "生产反馈回流",
        "业务 owner",
        "产品专家",
        "UED",
        "资深架构师",
        "质量/测试门禁",
        "发布 owner",
        "产品/交互设计和验收种子回到产品架构专家",
        "TDD/测试设计、编码实现、编码评审、安全可靠和发布风险回到资深架构师",
        "写代码的 Agent 不能自证通过",
        "不等于默认授权、测试通过、CR 结论或上线审批",
    ),
)

expected_handling_has(
    "ai-native-should-autonomous-discovery-to-delivery-loop",
    (
        "自主挖掘到交付",
        "角色协作 Loop",
        "intent-to-production-loop",
        "agent-loop-engineering",
        "code-delivery-closed-loop",
        "verification-review-release",
        "自主交付控制卡",
        "已读事实源",
        "候选需求/问题",
        "可自我挖掘",
        "可自我规划",
        "可自动执行",
        "必须人工确认",
        "置信度",
        "状态回写位置",
        "产品/交互设计",
        "需求 CR/设计评审",
        "TDD/测试设计",
        "编码实现",
        "代码 CR",
        "验证发布",
        "产品/交互设计和验收种子回到产品架构专家",
        "TDD/测试设计、编码实现、代码 CR、安全可靠和发布风险回到资深架构师",
        "Complete / Loop / Stop / Human handoff",
        "不能把自我规划当授权",
        "不能把 Agent 自述完成当证据",
        "公共契约、生产、Git、联网、部署、安全合规、不可逆动作和多方案取舍必须人工确认",
    ),
)

expected_handling_has(
    "ai-native-should-role-collaboration-loop-main-flow",
    (
        "角色协作 Loop 主流程",
        "intent-to-production-loop",
        "verification-review-release",
        "当前阶段",
        "角色视角",
        "能力/约规来源",
        "主责 owner",
        "协作角色",
        "AI Maker",
        "AI Checker",
        "设计",
        "设计评审",
        "TDD/测试设计",
        "编码实现",
        "编码评审",
        "可用性/安全性/可靠性评估",
        "验证发布",
        "复盘回流",
        "产品/交互设计和验收种子回到产品架构专家",
        "TDD/测试设计、编码实现、编码评审、安全可靠和发布风险回到资深架构师",
        "结构化 Java Service 生成回到 java-service-code-generator",
        "不能把阶段名当成自由发挥提示词",
        "GSD/CAD/Goal/Harness 只作为",
    ),
)

expected_handling_has(
    "ai-native-should-knowledge-expression-gate",
    (
        "知识表达 / 意图可执行门禁",
        "Knowledge-to-Execution Card",
        "业务目标",
        "业务对象",
        "状态/生命周期",
        "规则/策略",
        "约束/非目标",
        "验收样例",
        "反馈源",
        "待确认缺口",
        "不进入执行 Loop、代码修改或执行授权",
    ),
)

expected_handling_has(
    "ai-native-should-nonstandard-problem-mode",
    (
        "非标问题模式",
        "非标问题处理包",
        "问题主体",
        "影响面",
        "已知事实",
        "关键不确定性",
        "研究/证据路径",
        "候选方案",
        "最小可逆实验",
        "决策标准",
        "不能把无标准答案问题拆成机械执行清单",
    ),
)

expected_handling_has(
    "ai-native-should-practical-coding-loop",
    (
        "实际项目编码 Loop",
        "agent-loop-engineering",
        "Coding Loop Contract",
        "任务 ID/关联 Goal/Wave",
        "代码写入范围",
        "只读范围",
        "失败测试/验收样例",
        "TDD 顺序",
        "验证命令",
        "独立 Checker",
        "状态回写位置",
        "提交切片",
        "回滚/撤销方式",
        "路由资深架构师",
    ),
)

expected_handling_has(
    "ai-native-should-feedback-loop-verification-cluster",
    (
        "反馈闭环成熟度 / 验证簇准入模式",
        "L2/L3/L4/L5",
        "测试通过",
        "覆盖率",
        "bug 下降只是证据不是事实",
        "Verification Cluster Gate",
        "高风险业务不变量",
        "验证簇 ID",
        "场景测试",
        "属性/变形测试",
        "历史回归",
        "生产重放样本",
        "有限变异/对抗检查",
        "置信度",
        "独立 Checker",
        "预算/分层执行",
        "L5 只能标为目标架构",
    ),
)

expected_handling_has(
    "ai-native-should-architecture-entropy-loop",
    (
        "架构排熵 Loop / 腐朽门禁模式",
        "agent-loop-engineering",
        "Architecture Entropy Card",
        "可删除性",
        "局部推理边界",
        "承重行为",
        "废弃 API / dead path",
        "概念膨胀",
        "事实源分裂",
        "治理自腐",
        "守卫自检",
        "状态回写位置",
        "低风险动作",
        "Maker / Checker",
        "人工 triage",
        "架构师路由",
        "不把能自动扫描当成可以自动删除、迁移、重写或上线",
    ),
)

expected_handling_has(
    "ai-native-should-plan-to-goal-bridge-without-new-flow",
    (
        "Plan-to-Goal",
        "不是新增场景视图或独立流程",
        "计划成熟度",
        "成功标准",
        "假设",
        "执行步骤",
        "验证证据",
        "阻塞项",
        "Goal / Plan Grant",
        "确认后创建 Goal",
        "Plan Grant 字段齐备",
        "验证证据对照成功标准",
        "不把步骤执行完等同于 Goal Verified / Closed",
    ),
)

expected_handling_has(
    "product-should-nonstandard-problem-solution",
    (
        "非标产品问题与解决方案责任路径",
        "非标产品问题卡",
        "真实问题",
        "影响面",
        "失败成本",
        "当前替代方式",
        "解决方案假设",
        "验收种子",
        "UED",
        "不把老板/销售/客户/运营诉求原样转发给研发",
    ),
)

expected_handling_has(
    "product-should-concept-lifecycle-retirement",
    (
        "概念定名与概念生命周期治理路径",
        "Concept Lifecycle Card",
        "核心概念",
        "事实源",
        "目标主体",
        "与旧概念关系",
        "进入条件",
        "收敛/合并/废弃规则",
        "迁移路径",
        "用户/运营影响面",
        "验收种子",
        "下线 owner",
        "产品专家不能只加新名词",
    ),
)

expected_handling_has(
    "senior-should-nonstandard-engineering-problem",
    (
        "非标工程问题路径",
        "architecture.md",
        "非标工程问题卡",
        "问题背景",
        "可见症状",
        "结构证据",
        "核心机制",
        "影响面",
        "关键不确定性",
        "候选方案",
        "最小可逆实验",
        "验证命令/观测指标",
        "写入边界",
        "停止条件",
        "不直接大范围重构",
    ),
)

expected_handling_has(
    "senior-should-invariant-verification-cluster",
    (
        "不变量验证簇方法",
        "高风险业务不变量",
        "业务 owner",
        "验证簇 ID",
        "关联需求/AC",
        "场景测试",
        "属性/变形测试",
        "历史回归",
        "生产重放样本",
        "有限变异/对抗检查",
        "置信度",
        "CI 分层",
        "测试通过、覆盖率提高和 AI 生成测试数量不是事实本身",
        "生产重放只能作为证据",
    ),
)

expected_handling_has(
    "senior-should-architecture-decay-entropy-review",
    (
        "遗留系统改造 / 架构排熵评审路径",
        "evolutionary-architecture",
        "coding-review-deep-dive",
        "Architecture Entropy Review",
        "可删除性",
        "局部推理边界",
        "承重行为",
        "废弃 API / dead path",
        "概念膨胀",
        "事实源分裂",
        "治理自腐",
        "守卫自检",
        "下线候选",
        "契约测试",
        "灰度/回滚",
        "最小排熵计划",
        "不直接大重写",
    ),
)

expected_handling_has(
    "ai-native-should-agent-loop-engineering",
    (
        "Agent Loop Engineering",
        "agent-loop-engineering",
        "Loop 准入结论",
        "内部层映射",
        "Engineering Handoff Card",
        "关联 Goal",
        "状态载体",
        "反馈源",
        "验证者",
        "自我验证",
        "Plan Grant + Loop 预算绑定",
        "预算 / 最大轮次",
        "无进展检测",
        "失败回写",
        "停止条件",
        "授权策略",
        "交接物",
        "知识回流位置",
        "/goal",
        "/loop",
        "auto mode",
        "不能替代 Goal、Harness、Plan Grant、Execution Grant、测试、CR 或上线审批",
    ),
)

expected_handling_has(
    "ai-native-should-design-engineering-loop-not-prompting",
    (
        "Agent Loop Engineering / 设计工程 Loop",
        "agent-loop-engineering",
        "不是继续堆 Prompt",
        "可运行、可验证、可停止、可接管的工程循环",
        "Automations",
        "Worktrees",
        "Skills",
        "Plugins / Connectors",
        "Sub-agents / Maker-Checker",
        "Memory / 状态载体",
        "反馈源",
        "验证者",
        "预算 / 最大轮次",
        "无进展检测",
        "失败回写",
        "人类理解检查",
        "知识回流位置",
        "不看 PR 数、执行轮数或 Agent 数量",
        "合并率",
        "返工率",
        "缺陷率",
        "回滚率",
        "Review 成本",
        "用户价值",
        "团队理解程度",
        "不能让人类只剩点同意",
        "人类 owner 能解释目标、状态、关键变更、证据、残余风险和停止理由",
    ),
)

expected_handling_has(
    "ai-native-should-wisdom-lens-loop-scheduling",
    (
        "Loop 取舍校准 / Wisdom Lens 模式",
        "wisdom-loop-lens",
        "Wisdom Lens Card",
        "触发原因",
        "Loop 阶段",
        "推荐框架",
        "反偏问题",
        "底线问题",
        "证据要求",
        "回写位置",
        "不替代项",
        "准入前用阴阳平衡和先为不可胜",
        "拆解时用庖丁解牛和中庸之道",
        "执行中用循名责实和无为而治",
        "复盘后用每日三省、知行合一和一张一弛",
        "不能替代事实、测试、CR、Execution Grant、上线审批或专业确认",
    ),
)

expected_handling_has(
    "ai-native-should-development-standards-gate",
    (
        "开发标准门禁模式",
        "需求基线稳定性",
        "不进入 SDD、测试、代码或 CAD",
        "需求条目质量",
        "需求标准",
        "设计标准",
        "编码标准",
        "HLR/LLR 设计追踪",
        "规则原因/示例/验证方式",
        "防御式编程",
        "需求驱动测试",
    ),
)

expected_handling_has(
    "ai-native-should-prd-ai-prescan-review",
    (
        "PRD AI 预扫描 + 合议预审模式",
        "product-prd-quality-gates",
        "完整性",
        "一致性",
        "可测试性",
        "二义性",
        "疑似问题",
        "review_task",
        "evaluation_task",
        "reporting_task",
        "ACCEPT/REJECT/PENDING",
        "不能替代正式需求评审、QA 测试设计或产品 owner 决策",
    ),
)

expected_handling_has(
    "ai-native-should-final-deliverable-document-gate",
    (
        "最终文档准出模式",
        "正式 PRD/系分/Spec 正文与过程资产",
        "正文只保留当前有效目标、范围、规则、设计取舍、风险、待确认、验收、版本状态和过程记录链接",
        "讨论过程、迭代草稿、AI 推理轨迹、被拒方案",
    ),
)

expected_handling_has(
    "ai-native-should-spec-template-practices",
    (
        "PRD / SDD / 实现 Spec 三层边界",
        "不可让 AI 猜",
        "实现 Spec 作为实现和 CR 检查清单",
        "更新 Spec",
    ),
)

expected_handling_has(
    "ai-native-should-production-sdd-source-of-truth",
    (
        "SDD 生产代码模式",
        "spec-template-practices",
        "code-delivery-closed-loop",
        "verification-review-release",
        "清晰、完整、上下文化、具体、可测试",
        "事实来源",
        "结构化契约",
        "正反例",
        "五支柱验证",
        "回写失败场景到 Spec/AC/测试",
        "重试上限",
        "人工 owner",
    ),
)

expected_handling_has(
    "ai-native-should-fact-boundary-check",
    (
        "事实",
        "推断",
        "待确认",
        "范围外不做",
        "禁止无根据猜测",
        "模型脑补",
        "外部文章观点",
        "工具总结",
        "超出用户目标的实现扩张",
        "GSD Wave",
        "Atomic Task",
        "CAD 候选",
        "实现建议",
        "授权缺口",
    ),
)

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} {name}")

if failed:
    raise SystemExit("Trigger-path validation failed:\n" + "\n".join(f"- {name}" for name in failed))

print("Trigger-path validation passed.")
