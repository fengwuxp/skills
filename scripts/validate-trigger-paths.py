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
readme = "README.md"
repo_source_map = "references/source-map.md"
reference_index_audit = "scripts/audit-reference-indexes.py"


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


DECISION_GRILL_BOUNDARY_TERMS = (
    "决策澄清门禁是小闭环总门禁",
    "`grill-me` 是命中升级条件后的升级盘问",
)

WISE_AGENT_CORE_TERMS = [
    "统一智能行动主体",
    "知止而后有定",
    "知止不是不行",
    "你不是流程编排器",
    "专业能力来源",
    "察 -> 辨 -> 谋 -> 行 -> 验 -> 化",
    "默认只加载一个主能力",
    "能力不以本表为上限",
    "专业能力完成后仍由知止者综合结果",
    "单体工作优先",
    "Checker 独立",
    "决策澄清门禁",
    "完成必须同时具备",
    "联网、安装、Git、密钥、部署、生产、删除、不可逆操作",
    "单个领域词不等于专项证据",
]


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
    """Check the declared fixture contract; this does not execute an Agent."""
    cases = json.loads(read(skill_eval_prompt_fixture))["cases"]
    case = next((item for item in cases if item.get("id") == case_id), None)
    handling = "" if case is None else case.get("expected_handling", "")
    missing = [term for term in required_terms if term not in handling]
    detail = f" missing={missing}" if missing else ""
    check(f"prompt fixture expected handling outlines {case_id}{detail}", case is not None and not missing)


def negative_reason_has(case_id: str, required_terms: tuple[str, ...]) -> None:
    """Check why a hard-negative fixture must not trigger; this does not execute an Agent."""
    cases = json.loads(read(skill_eval_prompt_fixture))["cases"]
    case = next((item for item in cases if item.get("id") == case_id), None)
    reason = "" if case is None else case.get("negative_reason", "")
    missing = [term for term in required_terms if term not in reason]
    detail = f" missing={missing}" if missing else ""
    check(f"prompt fixture negative reason outlines {case_id}{detail}", case is not None and not missing)


def behavior_contract_has(case_id: str, required_keys: tuple[str, ...], required_terms: tuple[str, ...]) -> None:
    cases = json.loads(read(skill_eval_prompt_fixture))["cases"]
    case = next((item for item in cases if item.get("id") == case_id), None)
    contract = {} if case is None else case.get("behavior_contract", {})
    missing_keys = [key for key in required_keys if key not in contract]
    contract_text = json.dumps(contract, ensure_ascii=False, sort_keys=True)
    missing_terms = [term for term in required_terms if term not in contract_text]
    detail_parts = []
    if missing_keys:
        detail_parts.append(f"missing_keys={missing_keys}")
    if missing_terms:
        detail_parts.append(f"missing_terms={missing_terms}")
    detail = f" {' '.join(detail_parts)}" if detail_parts else ""
    check(
        f"prompt fixture behavior contract outlines {case_id}{detail}",
        case is not None and isinstance(contract, dict) and not missing_keys and not missing_terms,
    )


senior_skill = "senior-software-architect/SKILL.md"
senior_agent = "senior-software-architect/agents/openai.yaml"
senior_routing = "senior-software-architect/references/scenario-routing.md"
wind_skill = "wind-coding-conventions/SKILL.md"
wind_skill_agent = "wind-coding-conventions/agents/openai.yaml"
wind_skill_conventions = "wind-coding-conventions/references/wind-coding-conventions.md"
wind_skill_agents_template = "wind-coding-conventions/references/wind-project-agents-template.md"
wind_skill_examples = "wind-coding-conventions/references/wind-coding-examples.md"
wind_skill_java = "wind-coding-conventions/references/java-coding-conventions.md"
wind_skill_architecture = "wind-coding-conventions/references/wind-architecture-patterns.md"
wind_skill_source_map = "wind-coding-conventions/references/source-map.md"
senior_diagram = "senior-software-architect/references/diagram-output.md"
workflow = "senior-software-architect/references/workflow.md"
ai_engineering = "senior-software-architect/references/ai-assisted-engineering.md"
production_readiness = "senior-software-architect/references/production-readiness.md"
ai_large_project = "senior-software-architect/references/ai-large-project-orchestration.md"
cad_mode = "senior-software-architect/references/cad-mode.md"
negative_constraints = "senior-software-architect/references/negative-constraints.md"
architecture = "senior-software-architect/references/architecture.md"
testing = "senior-software-architect/references/testing.md"
coding = wind_skill_java
knowledge_graph = "senior-software-architect/references/knowledge-graph.md"
review = "senior-software-architect/references/coding-review-deep-dive.md"
debugging = "senior-software-architect/references/debugging-diagnosis.md"
adr_tradeoff = "senior-software-architect/references/adr-and-tradeoff.md"
language_agnostic = "senior-software-architect/references/language-agnostic-architecture.md"
security = "senior-software-architect/references/security-architecture.md"
system_analysis_template = "senior-software-architect/references/system-analysis-template.md"
refactoring_design_template = "senior-software-architect/references/refactoring-design-template.md"
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
product_business_architecture = "product-architecture-expert/references/business-architecture-planning.md"
product_concept_lifecycle = "product-architecture-expert/references/product-concept-lifecycle.md"
product_judgment_action_chain = "product-architecture-expert/references/product-judgment-action-chain.md"
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
document_skill = "document-authoring/SKILL.md"
document_agent = "document-authoring/agents/openai.yaml"
document_checker = "document-authoring/scripts/check_document_deliverable.py"
document_style_checker = "document-authoring/scripts/check_document_style.py"
document_routing = "document-authoring/references/scenario-routing.md"
hanzi_skill = "hanzi-philology/SKILL.md"
hanzi_agent = "hanzi-philology/agents/openai.yaml"
hanzi_checker = "hanzi-philology/scripts/check_philology_evidence.py"
hanzi_evidence_method = "hanzi-philology/references/evidence-method.md"
hanzi_source_map = "hanzi-philology/references/source-map.md"
huaxia_skill = "huaxia-practical-wisdom/SKILL.md"
huaxia_agent = "huaxia-practical-wisdom/agents/openai.yaml"
huaxia_classical_lenses = "huaxia-practical-wisdom/references/classical-lenses.md"
huaxia_decision_practice = "huaxia-practical-wisdom/references/decision-practice.md"
huaxia_evidence_boundaries = "huaxia-practical-wisdom/references/evidence-boundaries.md"
huaxia_source_map = "huaxia-practical-wisdom/references/source-map.md"
grill_me_skill = "grill-me/SKILL.md"
grill_me_agent = "grill-me/agents/openai.yaml"
grill_me_question_ledger = "grill-me/references/question-ledger.md"
grill_me_source_map = "grill-me/references/source-map.md"
wise_agent_skill = "wise-agent/SKILL.md"
wise_agent_agent = "wise-agent/agents/openai.yaml"
professional_skill_files = sorted(
    path.relative_to(ROOT).as_posix()
    for path in ROOT.glob("*/SKILL.md")
    if path.parent.name != "wise-agent"
)
wise_agent_cognition_model = "wise-agent/references/cognition-and-capability-model.md"
wise_agent_delivery_lifecycle = "wise-agent/references/delivery-lifecycle.md"
wise_agent_product_to_engineering = "wise-agent/references/product-to-engineering-lifecycle.md"
wise_agent_prd_system_design_review = "wise-agent/references/prd-system-design-review.md"
wise_agent_engineering_governance = "wise-agent/references/engineering-governance.md"
wise_agent_planning_execution_admission = "wise-agent/references/planning-execution-admission.md"
wise_agent_code_understanding_tools = "wise-agent/references/code-understanding-tools.md"
wise_agent_domain_expert_distillation = "wise-agent/references/domain-expert-distillation.md"
wise_agent_spec_template_practices = "wise-agent/references/spec-template-practices.md"
wise_agent_code_delivery = "wise-agent/references/code-delivery.md"
wise_agent_goal_governance = "wise-agent/references/goal-governance.md"
wise_agent_delivery_execution_control = "wise-agent/references/delivery-execution-control.md"
wise_agent_verification_release = "wise-agent/references/verification-review-release.md"
wise_agent_superpowers_library = "wise-agent/references/superpowers-skill-library.md"
wise_agent_skill_type_owner_routing = "wise-agent/references/capability-routing.md"
wise_agent_source_map = "wise-agent/references/source-map.md"
codegen_route = {"codegen", "code-generation-rules.md", "nobe-patterns.md", "generate_scaffold.py"}
codegen_safety_route = codegen_route | {"requires-confirmation"}
codegen_source_terms = ["CREATE TABLE", "DDL", "SQL", "建表语句", "schema", "字段表格", "字段说明", "Java 类", "表结构"]
codegen_action_terms = ["生成", "转换", "转成", "脚手架", "配套代码", "代码生成"]
codegen_target_terms = ["Wind/Nobe", "Service", "Mapper", "DTO", "Request", "Query", "Converter", "Entity", "代码"]
codegen_safety_terms = ["覆盖", "overwrite", "已有文件", "模块对不唯一", "多个 face/impl", "多个模块", "基础包名不唯一"]
wise_agent_terms = [
    "AI Native",
    "知止者",
    "SDLC",
    "Agentic SDLC",
    "Agentic DevOps",
    "AI Native Loop",
    "AI Native 研发流程",
    "AI 流程",
    "AI 工作流",
    "AI 工作量",
    "CDD",
    "Capability Discovery",
    "Capability-Driven Development",
    "能力发现",
    "先找能力，再写代码",
    "AI 时代产品到研发编码流程",
    "$wise-agent",
    "wise-agent",
    "角色 Loop",
    "角色loop",
    "产研协同",
    "产品判断 Loop",
    "可用性安全性评估",
    "可用性 / 安全性 / 可靠性评估",
    "意图到生产交付",
    "Intent-to-Production",
    "产研协同研发流程",
    "Agentic Engineering",
    "PRD-Lite",
    "OpenSpec",
    "Superpowers",
    "Matt Pocock",
    "mattpocock/skills",
    "grill-me",
    "grill-me 触发不稳定",
    "grill-me 触发不稳",
    "轻量问询",
    "角色 Loop 问询推进",
    "角色 Loop 问询修复",
    "问询修复",
    "任务树",
    "Trellis",
    "GStack",
    "/office-hours",
    "/plan-ceo-review",
    "/plan-eng-review",
    "/plan-design-review",
    "/review",
    "/qa",
    "/ship",
    "Office Hours",
    "CEO Review",
    "Eng Review",
    "Design Review",
    "QA Lead",
    "Release Engineer",
    "forcing questions",
    "生产交付审查",
    "生产交付审查卡",
    "生产交付验证",
    "生产生效验证",
    "生产生效验证卡",
    "业务场景模拟验收",
    "预发环境",
    "版本回读",
    "配置回读",
    "冒烟验证",
    "发布前评审",
    "交付生产",
    "Harness",
    "Prompt Engineering",
    "Context Engineering",
    "Harness Engineering",
    "L1-L4",
    "四层嵌套",
    "产研交付视图",
    "只读理解视图",
    "验证发布视图",
    "知识回流视图",
    "上下文治理视图",
    "Context System",
    "上下文治理",
    "知识库治理",
    "业务专家蒸馏",
    "蒸馏业务专家",
    "领域专家 Skill Pack",
    "可追溯业务专家",
    "目标计划",
    "目标计划组合",
    "目标计划按任务计划推进",
    "计划分波",
    "原子执行",
    "原子执行候选",
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
    "小闭环",
    "任务结束责任闭环",
    "交付责任自检",
    "下一任务计划问询",
    "最小计划草案",
    "决策澄清门禁",
    "自决推进",
    "询问 owner",
    "自动问询",
    "自动决策",
    "生产可用 Loop",
    "生产可用门禁",
    "生产可用混一模型",
    "混一",
    "一言而终",
    "本于阴阳",
    "神用无方",
    "一个入口",
    "一个契约",
    "一个准出",
    "生产可用准出卡",
    "架构排熵 Loop",
    "架构排熵",
    "腐朽门禁",
    "Architecture Entropy Card",
    "Loop 取舍校准",
    "东方判断层",
    "Wisdom Lens",
    "华夏经世智慧",
    "经世致用",
    "huaxia-practical-wisdom",
    "东方智慧",
    "老祖宗",
    "老祖宗视角",
    "周易",
    "易经",
    "易传",
    "道德经",
    "老子",
    "庄子",
    "论语",
    "中医",
    "黄帝内经",
    "五德终始",
    "五德始终",
    "阴阳五德始终",
    "本于阴阳",
    "神用无方",
    "病机",
    "正名",
    "阴平阳秘",
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
    "生产交付卡",
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
    "渐进式 SDD",
    "渐进式 Spec",
    "Spec Coding",
    "PrismSpec",
    "Lattice Harness",
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
    "Drift Check",
    "Loop Learn",
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
    "Skill 自我改进",
    "经验归位",
    "上下文资产化",
    "知识生产",
    "技术早报",
    "WorkBuddy",
    "本地执行型 Coding Agent",
    "AI bug report",
    "AI patch",
    "AI 找到 bug",
    "AI 生成补丁",
    "创可贴式修复",
    "同类影响",
    "Karpathy",
    "Andrej",
    "外科手术式变更",
    "Surgical Changes",
    "Harness Engineering",
    "Skill 原理",
    "Skill 最佳实践",
    "Claude Code Skills",
    "Perplexity Agent Skills",
    "Lessons from building Claude Code",
    "agent skills at Perplexity",
    "Skill 治理三问",
    "Skill Tax",
    "eval-first",
    "description 路由",
    "Gotchas flywheel",
    "SKILL.md 路由器",
    "资源加载契约",
    "触发测试",
    "功能走查",
    "反向验证",
    "架构真功夫",
    "专才 Agent",
    "专项 Skill",
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
    "华夏经世智慧",
    "经世致用",
    "huaxia-practical-wisdom",
    "东方智慧",
    "老祖宗",
    "老祖宗视角",
    "周易",
    "易经",
    "易传",
    "道德经",
    "老子",
    "庄子",
    "论语",
    "中医",
    "黄帝内经",
    "五德终始",
    "五德始终",
    "阴阳五德始终",
    "病机",
    "正名",
    "阴平阳秘",
    "阴阳平衡",
    "先为不可胜",
    "庖丁解牛",
    "治未病",
    "中庸之道",
    "循名责实",
    "无为而治",
    "每日三省",
    "知行合一",
    "一张一弛",
]
huaxia_explicit_terms = [
    "$huaxia-practical-wisdom",
    "huaxia-practical-wisdom",
    "华夏经世智慧",
    "经世致用",
    "老祖宗智慧",
]
huaxia_implicit_terms = [
    "变与不变",
    "名实是否相符",
    "名实相符",
    "当前时序",
    "时势与变化",
    "最坏失败",
    "可逆的小步",
    "可逆试点",
]
huaxia_decision_terms = [
    "现实决策",
    "决策校准",
    "长期合作决定",
    "组织协作",
    "行动取舍",
    "止损",
    "何时停止",
]
huaxia_negative_terms = [
    "不需要传统文化",
    "只做源码 CR",
    "只做文献与训诂证据",
    "底本、章句、异文",
    "替代医院检查",
    "治疗方案",
    "医学诊断",
    "占卜",
    "测字",
    "命理",
]
grill_me_explicit_terms = [
    "$grill-me",
    "grill-me",
    "grill me",
    "盘问这个",
    "拷问这个",
    "压力测试这份",
]
grill_me_implicit_terms = [
    "逐个关闭关键分叉",
    "每轮只提出一个最重要问题",
    "不要换个说法重复问",
    "先回看之前已经确认",
    "方案决策审查",
    "自行决定并留痕",
    "只继续审查和询问",
]
grill_me_negative_terms = [
    "只要事实和文件路径",
    "已经由 owner 确认",
    "不要重新发起需求澄清",
]
grill_me_unresolved_terms = [
    "仍是",
    "待确认",
    "剩余",
    "只继续",
    "冲突",
    "风险升级",
]
product_terms = ["产品", "产品方案", "PRD", "模板", "原型", "页面截图", "页面说明", "交互稿", "反推 PRD", "反推需求", "验收种子", "交给架构师", "业务架构", "业务架构规划", "业务 IT 对齐", "战略落项目", "战略到项目组合", "项目组合治理", "投资取舍", "投资决策支持", "能力-项目-系统映射", "知识库回流", "产品洞察", "需求洞察", "根源需求", "产品定义", "产品边界", "产品 DNA", "业务不变量", "功能先行、规则后补", "稳定点/变化点", "稳定点 / 变化点", "边界坐标", "概念定名", "概念生命周期", "概念退役", "新旧概念", "事实源分裂", "只加不减", "旧规则", "旧入口", "需求止损", "需求无止境", "价值 / 意义边界", "价值意义摇摆", "非标产品问题", "非标诉求", "不是传话筒", "解决方案假设", "老板", "销售", "客户", "运营", "目标用户", "UED", "产品阶段", "PMF", "贡献方式", "不按岗位分工", "原型验证", "真实交付", "复杂度清扫", "增长放大", "可靠维护", "资料资产化", "机会雷达", "竞品动态", "标杆实践", "Backlog", "机会清单", "机会点", "需求优先级", "User Story", "pm-skills", "产品判断成流程", "产品动作链", "产品判断动作链", "路线图取舍", "发布复盘", "增长实验", "清结算", "对账", "合规", "商户", "SaaS", "B2B", "运营后台", "规则矩阵", "能力地图", "用例图", "业务流程图", "资金流图", "外卡收单", "Mastercard", "商户到账", "产品大师", "MAGI", "多视角", "合议评审", "需求评审", "评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "产品头脑风暴", "问题探索", "假设挑战", "HMW", "OODA", "逆向头脑风暴"]
product_general_route_terms = ["产品方案", "验收种子", "交给架构师", "SaaS", "B2B", "业务流程", "业务流程图", "用例图", "能力地图", "业务架构", "业务架构规划", "业务 IT 对齐", "战略落项目", "战略到项目组合", "项目组合治理", "投资取舍", "投资决策支持", "重复建设识别", "能力-项目-系统映射", "知识库回流", "运营后台", "规则矩阵", "原型", "页面截图", "页面说明", "交互稿", "反推 PRD", "反推需求", "根源需求", "产品定义", "产品边界", "产品 DNA", "业务不变量", "功能先行、规则后补", "稳定点/变化点", "稳定点 / 变化点", "边界坐标", "概念定名", "概念生命周期", "概念退役", "新旧概念", "事实源分裂", "只加不减", "旧规则", "旧入口", "需求止损", "需求无止境", "价值 / 意义边界", "价值意义摇摆", "非标产品问题", "非标诉求", "不是传话筒", "解决方案假设", "老板", "销售", "客户", "运营", "目标用户", "UED", "产品阶段", "PMF", "贡献方式", "不按岗位分工", "原型验证", "真实交付", "复杂度清扫", "增长放大", "可靠维护", "产品经理方法论", "产品经理知识体系", "产品专家基础能力", "基础工作法", "产品洞察", "需求洞察", "资料资产化", "机会雷达", "客户访谈", "竞品动态", "标杆实践", "证据来源", "推理链", "机会清单", "Backlog", "需求优先级", "User Story", "AC", "pm-skills", "产品判断成流程", "产品动作链", "产品判断动作链", "路线图取舍", "发布复盘", "增长实验", "AI-shaped", "readiness", "AI 工作流", "AI 成熟度", "产品团队 AI", "AI 产品工作成熟度", "AI Native", "Product Builder", "业务 dogfooding", "MVP harden", "放下 PRD", "PRD 可执行上下文", "产品大师", "MAGI", "多视角", "合议评审", "PM/Reviewer", "AI 生成方案", "需求评审", "评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "产品头脑风暴", "问题探索", "方案发散", "假设挑战", "HMW", "第一性原理", "OODA", "逆向头脑风暴"]
product_judgment_terms = ["pm-skills", "phuryn/pm-skills", "产品判断成流程", "产品动作链", "产品判断动作链", "产品判断 Loop", "路线图取舍", "发布复盘", "增长实验", "不只是写文档"]
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
    wise_agent_product_to_engineering,
    wise_agent_delivery_lifecycle,
    wise_agent_prd_system_design_review,
    wise_agent_engineering_governance,
    wise_agent_planning_execution_admission,
    wise_agent_code_understanding_tools,
    wise_agent_domain_expert_distillation,
    wise_agent_spec_template_practices,
    wise_agent_code_delivery,
    wise_agent_goal_governance,
    wise_agent_delivery_execution_control,
    wise_agent_verification_release,
    wise_agent_superpowers_library,
    wise_agent_skill_type_owner_routing,
    wise_agent_source_map,
    grill_me_question_ledger,
    grill_me_source_map,
    huaxia_classical_lenses,
    huaxia_decision_practice,
    huaxia_evidence_boundaries,
    huaxia_source_map,
] + project_governance_refs + [wind_skill_java, wind_skill_architecture, wind_skill_conventions, wind_skill_agents_template, wind_skill_examples, wind_skill_source_map] + testing_practice_refs + skill_tree_refs

for path in reference_headers:
    check(f"{path} has progressive-disclosure header", has_reference_header(path))

check(
    "specialized skills use wise-agent as the internal orchestration owner",
    has_none(
        senior_skill,
        [
            "优先交给 AI Native",
            "当 AI Native 交来",
            "被 AI Native 分派",
            "退回产品专家或 AI Native",
            "AI Native 交来轻量问询结论",
            "端到端流程准入先由 AI Native 编排",
            "AI Native 交接消费",
        ],
    )
    and has_none(
        product_skill,
        [
            "被 AI Native 或架构师调用",
            "不替代 AI Native 的跨角色准入",
            "AI Native 交来轻量问询结论",
            "交给 AI Native / 架构师",
            "AI Native 前置门禁",
        ],
    )
    and has_none(codegen_skill, ["被 AI Native 分派", "交回 AI Native / 架构师"])
    and has_none(wind_skill, ["AI Native 项目约规入口"]),
)

expected_handling_has(
    "wind-coding-conventions-should-trigger-generic-java",
    ("通用 Java 约规", "不加载 Wind 专项约规"),
)
negative_reason_has(
    "wind-coding-conventions-negative-non-java-jvm-project",
    ("不能单独证明项目包含 Java 源码", "不得加载 Java/Wind 编码约规", "资深架构师"),
)
expected_handling_has(
    "wind-coding-conventions-should-apply-alibaba-manual-selectively",
    (
        "通用 Java 约规的阿里手册选择性采纳检查",
        "不创建独立 Skill",
        "Maven / Gradle 依赖治理",
        "dependency:tree",
        "Objects.equals",
        "serialVersionUID",
        "禁止 finally 返回",
        "禁止 SELECT *",
        "测试方法按团队通用规则强制使用 testXxx",
        "不把该规则归因于阿里手册",
        "不采用机械作者日期、统一覆盖率百分比",
    ),
)
expected_handling_has(
    "wind-coding-conventions-should-apply-clean-code-boundaries",
    (
        "命令与查询分离",
        "不隐式修改状态、持久化写入、发送消息或触发外部副作用",
        "最小学习测试或兼容性测试",
        "Fast、Independent、Repeatable、Self-Validating、Timely",
        "允许多个服务于同一场景的必要断言",
        "不加载 Wind 专项",
        "不把每个测试一个断言、统一未检查异常、禁止 null 或固定函数/类行数升级为机械强制规则",
        "senior-software-architect",
    ),
)

check(
    "wise-agent and precise specialist capabilities support implicit loading in one agent",
    contains(wise_agent_agent, "allow_implicit_invocation: true")
    and all(
        contains(path, "allow_implicit_invocation: true")
        for path in [
            product_agent,
            senior_agent,
            document_agent,
            hanzi_agent,
            "java-service-code-generator/agents/openai.yaml",
            wind_skill_agent,
        ]
    )
    and has_all(
        wise_agent_skill,
        ["精确 description", "同一 Agent", "不产生多个行动主体"],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        ["专业 Skill 也按精确 description 隐式匹配", "同一 Agent", "不产生第二人格或重复 Owner"],
    )
    and has_all(product_skill, ["知止者按需装载", "显式调用本 Skill 只表示优先装载该能力"])
    and has_all(senior_skill, ["知止者按需装载", "显式调用本 Skill 只表示优先装载工程能力"])
    and has_all(document_skill, ["知止者按需装载", "显式调用只表示优先装载成文能力"])
    and has_all(hanzi_skill, ["知止者按需装载", "显式调用只表示优先装载考据能力"])
    and has_all(codegen_skill, ["知止者按需装载的确定性 Java Service 代码生成能力包"])
    and has_all(wind_skill, ["知止者按需装载的 Java 项目分层约规能力包"]),
)
expected_handling_has(
    "wind-coding-conventions-should-trigger-wind-dependency",
    ("依赖或源码上下文", "叠加 Wind 专项约规"),
)
expected_handling_has(
    "wind-coding-conventions-should-gate-optional-dependencies",
    (
        "Wind 项目的币种字段无条件统一使用 CurrencyIsoCode",
        "JSpecify、MapStruct、MyBatis Flex 只在对应依赖或源码上下文存在时启用",
        "不要求项目为了套约规新增依赖",
        "Wind MySQL 表约规",
    ),
)

check(
    "Java convention trigger requires Java source evidence",
    has_all(
        wind_skill,
        [
            "包含 Java 源码",
            "Maven、Gradle 或 JVM 只能作为构建上下文",
            "不能单独证明适用本 Skill",
        ],
    )
    and has_none(
        wind_skill,
        [
            "检查任意 Java/JVM/Spring/Maven/Gradle 项目",
            "检查 Java/JVM/Spring 项目编码规范",
        ],
    ),
)

check(
    "Wind conventions separate universal dependency and database profiles",
    has_all(
        wind_skill_conventions,
        [
            "Wind 通用专项",
            "依赖专项",
            "项目数据库专项",
            "Wind 项目一旦出现币种字段",
            "必须统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode`",
            "项目已依赖 JSpecify 时",
            "项目已使用 MapStruct 时",
            "项目实际使用 MyBatis Flex 时",
            "项目已采用 Wind MySQL 表约规时",
            "不得为了启用依赖专项新增依赖",
        ],
    ),
)

check(
    "Wind skill packages its external source boundaries",
    (ROOT / wind_skill_source_map).exists()
    and contains(wind_skill, "references/source-map.md")
    and has_all(
        wind_skill_source_map,
        [
            "阿里 Java 开发手册",
            "Wind 项目族公开样本",
            "读取状态",
            "采纳边界",
            "不吸收",
            "`testXxx` 是团队规则，不归因于该手册",
        ],
    ),
)

check(
    "generic Java conventions absorb Clean Code boundaries without mechanical dogma",
    has_all(
        wind_skill_java,
        [
            "命令与查询分离",
            "不得隐式修改状态、持久化写入、发送消息或触发外部副作用",
            "最小学习测试或兼容性测试",
            "Fast、Independent、Repeatable、Self-Validating、Timely",
            "允许多个服务于同一场景的必要断言",
        ],
    )
    and has_all(
        wind_skill_source_map,
        [
            "代码整洁之道，读书笔记",
            "岁月如风",
            "2025-05-01 18:54",
            "2026-07-19",
            "9780132350884",
            "What Is Clean Code?",
            "不吸收",
        ],
    ),
)

check(
    "generic Java conventions cover equality money and untrusted execution boundaries",
    has_all(
        wind_skill_java,
        [
            "覆写 `equals` 时必须同时覆写 `hashCode`",
            "实现 `Comparable` 时必须明确 `compareTo` 与相等语义是否一致",
            "`BigDecimal` 数值大小比较使用 `compareTo`",
            "参数化 API、白名单或安全解析器",
            "任意类型实例化、SSRF 与路径穿越",
            "--profile java",
        ],
    ),
)
expected_handling_has(
    "wind-coding-conventions-should-trigger-generic-java-agents",
    ("普通 Java 项目 AGENTS.md", "不读取 Wind 项目模板"),
)
expected_handling_has(
    "senior-should-code-review-service-transaction",
    ("java-coding-conventions.md", "不加载 Wind 专项", "不把 wind-coding-conventions 作为第二 owner"),
)
negative_reason_has(
    "senior-negative-pure-java-conventions",
    ("纯约规检查", "wind-coding-conventions 主责", "不应触发资深架构师"),
)
negative_reason_has(
    "wind-coding-conventions-negative-wind-source-review",
    ("源码级 CR", "资深架构师主责", "不是第二个执行 owner"),
)

check(
    "Java coding conventions load universally and gate Wind rules by evidence without a legacy alias",
    has_all(
        wind_skill,
        [
            "name: wind-coding-conventions",
            "Java 项目编码约规 Skill",
            "所有包含 Java 源码的项目先使用通用 Java 约规",
            "Maven/Gradle 坐标、包名或 import",
            "只有孤立的 `face`、`impl`、`ServiceImpl` 或通用 MyBatis 用法时，不判为 Wind",
            "references/wind-coding-conventions.md",
            "references/java-coding-conventions.md",
            "references/wind-architecture-patterns.md",
            "references/wind-project-agents-template.md",
            "references/wind-coding-examples.md",
            "senior-software-architect",
            "java-service-code-generator",
            "Java Rule Check Card",
            "普通 Java 项目初始化或改进 `AGENTS.md`",
            "不读取 Wind 项目模板",
            "没有 Wind/Nobe 高置信度信号时，不加载 Wind",
            "币种字段才统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode`",
            "业务唯一性和请求重放幂等分层处理",
            "不得仅因“未来可能并发”预埋本地锁、分布式锁或锁 Wrapper",
            "查询字段/方法",
            "内网 API",
            "字典国际化",
            "生产源码路径不得新增内存版业务 Service",
        ],
    )
    and has_all(
        wind_skill_agent,
        [
            "Java/Wind 编码约规",
            "Java 源码项目通用约规",
            "按上下文启用 Wind/Nobe 专项",
            "$wind-coding-conventions",
        ],
    )
    and has_all(
        senior_skill,
        [
            "`wind-coding-conventions`",
            "Java 项目在本地规范之后读取 `wind-coding-conventions` 的通用层",
            "架构师负责源码级设计、TDD、CR 和验证",
        ],
    )
    and has_all(
        wind_skill_java,
        [
            "Java/Spring 通用编码约规",
            "所有 Java 项目的通用编码行为",
            "不得为了套规约新增依赖",
            "项目本地 `AGENTS.md`",
            "源码级设计、Review、测试与生产风险仍交 `资深架构师`",
        ],
    )
    and has_all(
        wind_skill_architecture,
        [
            "Wind 架构与 API 模式",
            "具体编码强规约优先读 `java-coding-conventions.md`",
            "Wind 落地要求",
        ],
    )
    and has_all(
        senior_routing,
        [
            "Java 通用约规 + Wind 条件专项",
            "纯 Java/Wind 约规检查不触发本 Skill",
            "普通 Java 源码任务",
            "Wind/Nobe 高置信度信号",
            "规则 Skill 不成为第二 owner",
            "只有孤立的 face、impl、ServiceImpl 或普通 MyBatis 用法时，不启用 Wind 专项",
        ],
    )
    and not (ROOT / ("wind-project-" + "coding-conventions")).exists()
    and not (ROOT / ("senior-software-architect/references/" + "coding-standards.md")).exists()
    and not (ROOT / "senior-software-architect/references/wind-projects-patterns.md").exists()
    and has_none(
        senior_skill,
        [
            "references/java-coding-conventions.md",
            "references/" + "coding-standards.md",
            "references/wind-projects-patterns.md",
            "Wind 编码约规的兼容索引",
        ],
    )
    and has_reference_header(wind_skill_conventions)
    and has_task_reading_index(wind_skill_conventions)
    and has_all(
        wind_skill_conventions,
        [
            "`wind-coding-conventions` Skill 的 Wind 专项规则",
            "依赖坐标、包名/import、Wind 类型或模块上下文",
            "wind-integration / nobe / capte-domain 源码观察",
            "face/impl 模块边界",
            "接口放置",
            "基础服务",
            "方法签名",
            "服务命名",
            "模型命名",
            "枚举命名",
            "应用层服务",
            "查询字段命名",
            "内网 API",
            "系统字典/国际化",
            "DTO/Request/Query/Entity",
            "模型包归位",
            "分包规则",
            "MyBatis Flex",
            "`web-api` / `web-security` 放 Controller、Web VO、Web 登录/表单 Request 和 Web 层 Converter",
            "放置四问",
            "对外或跨模块调用进 `*-face`",
            "模块内部实现进 `*-impl`",
            "跨模块稳定公共能力进 `core`",
            "技术适配和框架配置进 `infrastructure`",
            "`model/dto`、`model/request`、`model/query`、`model/command`",
            "历史兼容场景允许继续使用既有 `dto`、`request`、`query`、`command` 包",
            "`*-impl` 一般不放对外 DTO/Request/Query/Command",
            "回调入口、扩展点或业务 SPI 的 `callback/spi`",
            "`core` 放跨模块稳定基础契约、值对象、枚举、事件、上下文、规则、告警、缓存兑换、操作人等公共能力",
            "`infrastructure` 放消息发送、KMS、MyBatis Flex helper、通用工具和框架配置等技术适配",
            "源码样本中 `*-face` 常见 `service/services`",
            "`*-impl` 常见 `service/impl`、`application/impl`、`dal/entities`、`dal/mapper`、`mapstruct`",
            "capte-domain platform 样本补充",
            "`platform/*-face` 中稳定出现 `service`、`dto`、`request`、`query`、`enums`、`task`",
            "`platform/*-impl` 中稳定出现 `service/impl`、`dal/entities`、`dal/mapper`、`mapstruct`",
            "必要的 `application` 契约",
            "同一 face 有多个业务子域时，可按业务名继续分包",
            "`domain` 必须表示稳定业务语义，不得作为杂物包",
            "`*-impl` 放内部 `service` / `service/impl`、`application/impl`、`domain` / `domain/impl`",
            "listener",
            "webhook",
            "接口落位",
            "完整用例契约才放 `*-face/application`",
            "只被本模块实现层使用的接口留在 `*-impl/service`、`*-impl/domain` 或 `*-impl/support`",
            "face Service 和跨模块接口只暴露 `DTO`、`Request`、`Query`、`Command`、枚举或值对象，不暴露 `Entity`",
            "接口放 `*-face/application`，实现放 `*-impl/application/impl`",
            "内部基础服务可以封装稳定查询或基础数据访问，但不能只是 Mapper 透传",
            "基础服务通用模板",
            "基础服务必须识别并发下的业务不变量",
            "唯一性、状态流转和一般读改写",
            "分别优先使用表内业务 UK 或联合 UK、带前置状态的原子条件更新和乐观锁",
            "事务只保证本地操作的原子提交和回滚",
            "普通 `SELECT -> Java 校验 -> UPDATE` 即使使用 `@Transactional` 也不能单独防止丢失更新",
            "明确并发入口、冲突资源",
            "失败场景、测试或生产证据",
            "已验证持有者身份、安全释放、租约续期或有界执行语义的平台原语",
            "`XxxService`，实现为 `XxxServiceImpl`",
            "`createXxx(CreateXxxRequest)` 返回 `@NonNull Long`",
            "`WindPagination<XxxDTO> queryXxxs(XxxQuery query, WindQuery<? extends QueryOrderField> options)`",
            "ServiceImpl 通用实现",
            "`createQueryWrapper` 或 `fillQueryWrapper`",
            "公开查询接口优先返回 `DTO` 或 `WindPagination<DTO>`",
            "`WindQuery<? extends QueryOrderField>`",
            "`DomainService` / `DomainQueryService` 不是 Wind 项目强制分层",
            "四类服务是判断框，不是强制新增层",
            "查询方法命名",
            "`get` 表示必然存在",
            "`find` 表示可能不存在",
            "`query` 表示条件查询、列表、分页或统计",
            "服务层不得使用 `select/load/fetch`",
            "写操作用业务动词",
            "Controller、face Service、ApplicationService 对外方法、Facade、Adapter、跨模块接口、事件/消息契约不得以 Entity、Mapper、Repository 或 MyBatis `Page` 作为入参、返回值或泛型",
            "离开 `*-impl` 边界前必须转换为 `DTO`、`Request`、`Query`、`Command`、`Event` 或值对象",
            "新代码的 `DTO`、`Request`、`Query`、`Command` 优先放在 `*-face` 或 `core` 的 `model/dto`、`model/request`、`model/query`、`model/command` 下",
            "模型命名",
            "查询字段命名",
            "默认等值查询不加后缀",
            "`Contains/StartsWith/EndsWith`",
            "`Min/Max`",
            "`IsNull/IsNotNull`",
            "`CreateXxxRequest`、`UpdateXxxRequest`、`SaveXxxRequest`、`ExecuteXxxRequest`",
            "对应 Java 包名通常是 `*.model.dto`、`*.model.request`、`*.model.query`、`*.model.command`",
            "历史兼容场景允许继续使用既有 `dto`、`request`、`query`、`command` 包",
            "对应 `*.dto`、`*.request`、`*.query`、`*.command`",
            "`*-impl` 一般不放 DTO/Request/Query/Command",
            "`domain` 仅用于跨子域、稳定业务概念",
            "业务/通道事件 Converter 可放 `*-impl` 的 `converter` 或 `support`",
            "事件/消息契约跟业务 owner 走",
            "事件监听器、Webhook handler、投递 executor 放 `*-impl/listener` 或 `*-impl/webhook`",
            "Web 展示 VO、登录/表单 Request 和页面组合模型放 `web-api` / `web-security`，不得回流到 face 契约",
            "跨域共享模型只有在两个以上业务模块稳定复用且不依赖 Web/DAL 时，才放 `core` 的 `model`、`enums` 或 `event`",
            "公共接口、公有方法、DTO/Request/Query、配置属性和扩展点要有 Javadoc",
            "primitive 或包装类型按缺省、零值和序列化语义选择",
            "并发 Atomic 类型不得进入数据传输契约",
            "Wind 项目一旦出现币种字段，必须统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode` 枚举",
            "外部协议中的字符串币种只在 Adapter/Converter 边界转换",
            "业务唯一性和请求重放幂等分层处理",
            "项目已采用 Wind MySQL 表约规时",
            "数据表强制包含 `id bigint`、`gmt_create datetime`、`gmt_modified datetime`",
            "新增必填字段必须有兼容迁移方案",
            "通用表字段",
            "外部 `Idempotency-Key` / `requestSn` 可以用于请求重放去重",
            "不得冒充业务身份",
            "参数摘要、有效期、并发冲突、结果回放和过期后重用语义",
            "枚举命名和模板",
            "生命周期用 `XxxState`，分类用 `XxxType`，动作/指令用 `XxxAction`",
            "公开枚举优先实现 `DescriptiveEnum`",
            "系统字典、国际化和业务事件",
            "业务逻辑、持久化判断和状态机只能依赖 code、enum、errorCode 或 eventKey",
            "业务事件、审计展示和可回放消息存 `{eventKey, params}`",
            "`MybatisQueryHelper.from(options)`",
            "`XxxNameRefs`",
            "`orderFields` / `orderTypes`",
            "`Pagination.empty()`",
            "内网 API 路径表达安全分类",
            "路径只表达分类，不构成安全控制",
            "默认拒绝并逐请求鉴权",
            "`/inc/basic/**`",
            "`/inc/secure/**`",
            "impl 的 `webhook`、`listener`、`handler`、`executor` 负责协议解析、签名校验、状态映射、幂等和投递",
            "ApplicationService / ServiceImpl 流程测试保留真实内部协作者",
            "TDD 先写能失败的行为测试",
            "基础服务测试重点验证 QueryWrapper、Mapper 语义、分页、排序、selective 写库、事务事实和异常语义",
            "完成 TDD 或 AI 生成实现后做设计质量回看",
            "生产源码路径不得新增 `InMemoryXxxService`",
            "Entity 是否泄漏到服务层/接口契约",
            "模型包归位",
            "`XxxQuery` 字段后缀",
            "字典/国际化 Key",
            "core/infrastructure 是否变成公共垃圾桶",
            "项目本地 `AGENTS.md` 明确声明是最强信号",
            "wind-project-agents-template.md",
            "知止者能按项目规则调度产品、架构、Wind 规则和代码生成能力",
            "需要最佳实践正反例时读 `wind-coding-examples.md`",
        ],
    )
    and has_reference_header(wind_skill_agents_template)
    and has_task_reading_index(wind_skill_agents_template)
    and has_all(
        wind_skill_agents_template,
        [
            "`wind-coding-conventions` Skill 的项目本地 `AGENTS.md` 模板",
            "wind-integration / nobe / capte-domain",
            "知止者",
            "Karpathy-style 工程纪律",
            "不知道就问",
            "没要求的不写",
            "只改被要求的部分",
            "给验收标准、验证结果和停止条件",
            "从第一性原理看原始需求和问题本质",
            "每一行修改都要能回到用户目标、验收标准、源码事实或失败测试",
            "本项目遵守 Wind 编码约规",
            "项目身份",
            "AI 协作入口",
            "项目约规入口",
            "Wind 规则权威只读 `wind-coding-conventions`",
            "本文件不复制完整规则",
            "项目级红线",
            "交付格式",
            "face/impl",
            "模型归位",
            "不把 Entity、Mapper、Repository、MyBatis Page 或 QueryWrapper 暴露到 Controller、face Service、ApplicationService 对外方法、Facade、Adapter、跨模块接口或事件消息契约",
            "不新增一行透传方法、Mapper 包装、浅服务、似是而非的 ApplicationService、内存版业务 Service",
            "TDD 和测试按公开契约黑盒验证",
            "不得把“可继续推进”写成“已经授权”",
            "不把 `capte-domain`、`nobe`、`wind-integration` 的历史包名、业务模块名或命令照搬成新项目事实",
        ],
    )
    and has_reference_header(wind_skill_examples)
    and has_task_reading_index(wind_skill_examples)
    and has_all(
        wind_skill_examples,
        [
            "`wind-coding-conventions` Skill 的示例参考",
            "Wind 项目编码最佳实践示例",
            "不是代码生成模板",
            "ApplicationService 不是透传层",
            "基础服务不是 Mapper 包装",
            "模型边界不穿透",
            "模型包归位清晰",
            "Face Service 返回 `XxxEntity`",
            "face Service 返回 `XxxDTO`",
            "公开接口签名不得出现 Entity",
            "Web 页面 VO 放进 `*-face` 的 DTO 包",
            "把 `domain` 当杂物包",
            "把只给本模块用的接口提前放进 face/core",
            "业务契约模型新代码优先放 `*-face` 的 `model/dto`、`model/request`、`model/query`、`model/command`",
            "对应 Java 包名 `*.model.dto`、`*.model.request`、`*.model.query`、`*.model.command`",
            "历史兼容既有 `dto/request/query/command`",
            "跨模块稳定 Service 放 `*-face/service`",
            "回调入口和业务 SPI 放 `*-face/callback/*`",
            "`domain/model/dto|request` 等子包表达稳定业务语义",
            "业务/通道事件适配 Converter 可放 `*-impl/converter`",
            "内部领域规则放 `*-impl/domain|domain/impl`",
            "内部 DTO/Request/Query/Command 只能留在 impl 内部",
            "Web VO 和登录/表单 Request 放 `web-api` / `web-security`",
            "跨模块稳定公共能力放 `core`",
            "技术适配和框架配置放 `infrastructure`",
            "MyBatis Flex 查询集中表达",
            "公开接口返回 `WindPagination<DTO>`",
            "`MybatisQueryHelper.from(options)`",
            "`Pagination.empty()`",
            "TDD 测真实链路",
            "未来可能并发",
            "先证明锁的准入条件",
            "普通事务不能单独防止无条件读后写的丢失更新",
            "不提供可直接复制的固定租约锁模板",
            "持有者身份、安全释放、续期或有界执行",
            "源码样本只提炼稳定共性",
            "`wind-integration / nobe / capte-domain 源码观察`",
            "`dal/entities`、`dal/mapper`、`mapstruct`",
            "当前代码更接近反例还是正例",
            "不把示例当模板复制",
            "平台基础服务模板可复用但不硬套",
            "`createXxx(CreateXxxRequest) -> Long`",
            "`queryXxxs(XxxQuery, WindQuery<? extends QueryOrderField>) -> WindPagination<XxxDTO>`",
            "枚举是业务语言，不是字符串常量袋",
            "`XxxState`、`XxxType`、`XxxAction`",
            "Query 字段命名表达语义",
            "默认等值不加后缀",
            "`nameContains`",
            "`createdAtMin` / `createdAtMax`",
            "内网 API 路径表达分类但不替代鉴权",
            "`/inc/basic/{domain}/{resource}/{action}`",
            "`/inc/secure/{domain}/{resource}/{action}`",
            "字典国际化不驱动业务逻辑",
            "`{eventKey, params}`",
        ],
    )
    and has_all(
        "README.md",
        [
            "Java 项目通用编码约规，或按依赖/上下文启用 Wind/Nobe 专项",
            "`wind-coding-conventions`",
            "Wind 项目按实际依赖和上下文补专项入口",
            "路径：[wind-coding-conventions](./wind-coding-conventions)",
            "只做规则判断和偏差说明",
            "没有 Wind/Nobe 高置信度信号时不加载 Wind face/impl、API 或模型专项",
        ],
    ),
)

check(
    "Java rule authority and source execution keep single owners",
    has_all(
        wind_skill,
        [
            "纯约规检查由本 Skill 主责",
            "源码设计、代码 CR、Bug 修复、TDD 和验证不触发本 Skill 主责",
        ],
    )
    and has_all(
        senior_skill,
        [
            "Java 设计、源码级 CR、TDD、Bug 修复和验证统一读取",
            "只消费规则结论，不复制 Java/Wind 约规正文",
        ],
    )
    and has_all(
        senior_routing,
        [
            "纯 Java/Wind 约规检查不触发本 Skill",
            "普通 Java 源码任务",
            "Wind/Nobe 高置信度信号",
        ],
    )
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and all(
        has_none(
            path,
            [
                "LambdaQueryWrapper",
                "insertSelective",
                "gmt_create",
                "测试类以 `Tests`",
                "测试方法以 `test`",
                "DescriptiveEnum",
                "JSpecify",
                "MapStruct 只做",
                "Lombok 服务",
            ],
        )
        for path in [
            "senior-software-architect/references/project-governance-codebase-and-modules.md",
            "senior-software-architect/references/project-governance-service-api-modeling.md",
            "senior-software-architect/references/project-governance-data-security-quality.md",
            "senior-software-architect/references/coding-review-deep-dive.md",
        ]
    ),
)

check(
    "generic Java conventions keep documentation contextual and test naming explicit",
    has_none(
        wind_skill_java,
        [
            "【强制】公共接口、公有方法、DTO/Request/Query、配置属性、扩展点必须有 Javadoc",
            "【强制】测试类以被测类名开头、`Tests` 结尾；测试方法以 `test` 开头",
            "测试类和测试方法命名优先服从项目既有约定",
            "不强制使用 `test` 前缀",
            "快速代码 CR 或编码红线",
            "公有方法必须完整说明业务语义",
            "超过 5 个参数按强制规则处理",
        ],
    )
    and has_all(
        wind_skill_java,
        [
            "公共契约、扩展点和配置属性",
            "简单 DTO/Request/Query",
            "测试方法必须使用 `testXxx` 格式",
            "测试类命名优先服从项目既有约定",
            "不为统一形式批量重命名未触及的历史测试",
            "快速约规核对或编码红线",
            "无法从签名识别",
            "公有方法参数超过 5 个是 Review 信号，不是机械门禁",
        ],
    ),
)

check(
    "generic Java conventions split control mechanics only when they obscure business flow",
    has_all(
        wind_skill_java,
        [
            "已经掩盖业务主路径、状态变化或副作用",
            "简单、内聚且可直接读懂的用例编排保留在同一方法",
            "不为形式分离制造 helper、状态机或浅调用链",
        ],
    )
    and has_none(
        wind_skill_java,
        [
            "【强制】业务逻辑与控制逻辑不得混杂在同一方法中",
            "一个方法不应同时负责取数、遍历、分支、状态修改、异步调度和业务决策",
        ],
    ),
)

check(
    "Alibaba Java manual is selectively absorbed into the generic Java authority",
    has_all(
        wind_skill_java,
        [
            "Maven / Gradle 依赖治理",
            "SNAPSHOT",
            "dependencyManagement",
            "dependency:tree",
            "Objects.equals",
            "serialVersionUID",
            "finally",
            "SELECT *",
            "隐式类型转换",
            "不设置统一覆盖率百分比",
            "服务器运行参数",
        ],
    )
    and has_none(
        wind_skill_java,
        [
            "所有的类都必须添加创建者和创建日期",
            "语句覆盖率达到70%",
            "Xms和Xmx设置一样",
            "调小TCP协议的time_wait",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "https://www.yuque.com/iv8gga/qgf69v",
            "1.3.1",
            "23 篇",
            "2017-11-30",
            "2026-07-16",
            "依赖治理",
            "不吸收",
            "time_wait",
            "Xms/Xmx",
            "固定覆盖率",
            "测试方法统一使用 `testXxx` 是团队明确规则",
            "不归因于该手册",
        ],
    ),
)

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
            "最小交付与第一性原则",
            "不知道就问",
            "没要求的不写",
            "只改被要求的范围",
            "优先给验收标准、验证结果和停止条件",
            "外科手术式变更",
            "每一行修改都必须能回到用户目标、验收标准、源码事实或验证失败",
            "不顺手重构、不改无关注释格式、不做未要求的“顺便优化”",
        ],
    ),
)

check(
    "wise agent anchors product architect and senior architect collaboration",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_verification_release,
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
        wise_agent_code_delivery,
        [
            "# 代码交付",
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
            "知识生产",
            "先资产化业务背景、术语、标准格式、常用模板和历史坑点",
            "不把厂商工具写成默认依赖",
            "L0 项目级上下文",
            "L1 模块级上下文",
            "L2 任务级上下文",
            "`update-context` 不是新增顶层 Skill",
            "每个阶段必须有输入输出契约",
            "生产可用混一模型",
            "一个入口：知止者",
            "一个契约：交付契约",
            "一个准出：生产可用准出卡",
            "生产可用准出卡",
            "真实业务入口",
            "独立 CR",
            "发布观测",
            "回滚 / 人工接管",
        ],
    )
    and has_all(
        wise_agent_planning_execution_admission,
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
        wise_agent_product_to_engineering,
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
    "wise agent normalizes progressive SDD and Lattice Harness without adding a parallel flow",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_spec_template_practices,
        [
            "2.1 渐进式 SDD 四档",
            "不把所有需求推成重流程",
            "Spec 是约束，不是文档",
            "Spec 负责收敛，验证负责裁决",
        ],
    )
    and has_all(
        wise_agent_code_delivery,
        [
            "1B. 渐进式 SDD / Lattice Harness 收口",
            "Intent -> Context -> Spec -> Orchestrator -> Verification -> Evidence / Eval -> Drift Check -> Loop / Learn",
            "生成者可以修复问题，但不能自己宣布通过",
            "准出必须来自测试、静态检查、验收覆盖、漂移检查、只读 Checker 或人工 owner",
            "裁判缺口补 Verification",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "爆肝长文：SDD 实战上篇，从 Vibe Coding 到渐进式 Spec驱动开发",
            "爆肝长文：SDD 实战下篇，从渐进式 SDD 到 Lattice Harness：AI Coding 的团队级闭环",
            "Spec 是约束不是文档",
            "Context / Orchestrator / Verification / Evidence / Eval / Drift Check / Loop Learn",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "爆肝长文：SDD 实战上篇，从 Vibe Coding 到渐进式 Spec驱动开发",
            "爆肝长文：SDD 实战下篇，从渐进式 SDD 到 Lattice Harness：AI Coding 的团队级闭环",
            "默认工具、执行授权、测试通过、CR 结论或上线审批",
            "当前默认工具、自动执行授权、合并判断或生产审批",
        ],
    ),
)

check(
    "wise agent treats context and knowledge base as governed Context System",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_code_delivery,
        [
            "5B. Context System 与知识库治理门禁",
            "先建设 Context System，再评估知识库工具",
            "Context / 知识库准入四问",
            "外部知识库、向量库、代码图谱或 Understand Anything 只在 L0/L1 权威材料已经清楚",
            "不得回写：一次性过程草稿、未验证推断",
        ],
    )
    and has_all(
        wise_agent_code_understanding_tools,
        [
            "知识库工具判断",
            "工具摘要不得替代源码、测试、CR 或 owner 结论",
        ],
    ),
)

check(
    "ai-native source quality review loop covers architecture business and clean implementation",
    has_all(
        wise_agent_verification_release,
        [
            "遵循编码规范",
            "不踩红线",
            "高屋建瓴",
            "深入细节",
            "业务语义",
            "业务不变量",
            "架构边界",
            "设计原则",
            "代码坏味道",
            "整洁代码与架构实现",
            "规范 / 红线",
            "业务 / 架构判断",
            "坏味道",
            "整洁实现建议",
        ],
    ),
)

check(
    "project-owned grill-me keeps upstream core and wise-agent boundary",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_none(
        wise_agent_skill,
        [
            "grill-me 决策快照，只保留",
            "执行 / 写文件 / 生成计划前必须先做执行前对账",
        ],
    )
    and has_all(
        wise_agent_delivery_lifecycle,
        [
            "轻量问询结论",
            "`grill-me` 盘问结论",
            *DECISION_GRILL_BOUNDARY_TERMS,
            "装载这一独立 Skill",
            "完整盘问、问题台账、历史去重、自决和决策快照由该 Skill 负责",
            "Loop 推进中适时装载 `grill-me`",
            "执行前对账读 `delivery-execution-control.md`",
        ],
    )
    and has_none(
        wise_agent_delivery_lifecycle,
        ["grill-me 退出后形成决策快照", "被排除方案不得复活"],
    )
    and has_all(
        wise_agent_delivery_execution_control,
        [
            "盘问、问题台账、历史去重和决策快照由独立 `grill-me` 负责",
            "完整盘问、问题台账、历史去重、自决和红线规则",
            "本节只消费决策快照并做执行前对账",
            "已确认选择、被排除方案、待确认项、red_lines、下一阶段输入和写回位置",
            "被排除方案不得复活",
            "待确认项不得脑补",
            "快照缺失或不一致时停止并问 Owner",
            "领域知识分流",
            "只有 Owner 已确认",
            "冲突证据与影响范围",
            "按业务域或模块写入术语与对象表、证据地图或领域知识卡",
            "难以逆转",
            "缺少背景会令人困惑",
            "真实方案取舍",
            "未获写入授权时只输出候选回流位置",
            "不创建 `CONTEXT.md`、ADR 或知识库目录",
            "任务树真相源",
            "Task Tree / 任务树",
            "目标、输入、owner、验收标准、依赖、状态和停止条件",
            "不默认安装或依赖外部服务",
        ],
    )
    and has_all(
        wise_agent_superpowers_library,
        [
            "Matt Pocock 与 grill-me",
            "复杂或模糊计划的升级盘问能力",
            "一次一个问题",
            "Facts 先查",
            "Decisions 等 owner",
            "关键分叉未决、回答含糊或连续返工时升级",
            "不得重复问同一问题",
            "项目自有独立 Skill",
            "问题台账、历史去重、自决边界、红线与决策快照",
            "上游只作来源参考",
            "不安装全仓库",
        ],
    )
    and has_all(
        grill_me_source_map,
        [
            "Matt Pocock skills",
            "2026-07-15 核验上游 `main`",
            "上游当时的 `grill-me` 只调用 `/grilling`",
            "一次一问、推荐答案、Facts 自查、Decisions 等 Owner 和 shared understanding",
            "项目自有独立 `grill-me`",
            "不安装上游全仓库",
            "不保留 `/grilling` alias",
        ],
    )
    and has_none(
        wise_agent_superpowers_library,
        [
            "入口 alias",
            "快捷触发别名",
            "转入 `grill-me`",
            "安装 `grill-me` 与 `grilling`",
        ],
    )
    and has_none(
        grill_me_source_map,
        [
            "安装最小 Markdown 对 `grill-me` 与 `grilling`",
        ],
    )
    and has_all(
        product_skill,
        [
            "轻量问询不写进正式 PRD",
            "`wise-agent` 交来轻量问询结论、`grill-me` 结论或任务树节点",
            "产品上下文交接卡",
        ],
    )
    and has_all(
        senior_skill,
        [
            "轻量问询只收敛工程分叉",
            "`wise-agent` 交来轻量问询结论、`grill-me` 结论或任务树节点",
            "问询过程不进入正式系分、ADR 或代码注释",
        ],
    )
    and has_all(
        "README.md",
        [
            "决策澄清门禁只处理真正未决的 Decisions",
            "`grill-me` 是升级盘问，不是每个任务的必经流程",
            "复杂或模糊任务一次只问一个主 blocker",
            "Facts 先从材料、源码、测试或日志自答",
            "Decisions 才问 owner",
            "路径：[grill-me](./grill-me)",
            "已确认或已排除的问题不得换个说法重问",
            "自决不扩大授权",
        ],
    ),
)

check(
    "project-owned grill-me keeps stateful handoff boundaries",
    has_all(
        grill_me_skill,
        [
            "优先恢复已有问题台账、决策快照、Issue、Goal、Spec、ADR、PRD、源码、测试、日志、项目约规和知识库",
            "没有获准的持久载体时",
            "每次裁决和实际问题都写入问题台账",
            "退出时",
        ],
    )
    and has_all(
        grill_me_question_ledger,
        ["Issue / Goal Ledger / Spec / Decision Log", "当前任务中维护并在退出前输出", "不得为了台账自动创建"],
    )
    and has_all(
        grill_me_source_map,
        [
            "如何看待 grill-me（拷问我）这个 Skill？",
            "LastWhisperDev",
            "2026-07-10 15:50",
            "Taste Injection",
            "Shared Context",
            "Issue / PR",
            "Hand-off Prompt",
        ],
    ),
)

check(
    "wise agent absorbs WorkBuddy as context asset practice not dependency",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_code_delivery,
        [
            "调研、早报、教程、培训、行业情报或团队知识传播",
            "知识生产",
            "先资产化业务背景、术语、标准格式、常用模板和历史坑点",
            "不要每次从空白提示词重建上下文",
            "不把厂商工具写成默认依赖",
            "不替代架构判断、CR、测试结果、Git 授权或发布审批",
        ],
    )
    and has_all(
        product_insight,
        [
            "团队知识传播做成产品侧知识资产",
            "产品侧知识资产包",
            "业务理解、验收种子、团队复用和过期清理",
        ],
    )
    and has_all(
        ai_engineering,
        [
            "工程知识资产判断",
            "最小工程知识资产包包含目标读者、使用场景、资料范围、入口路径",
            "代码库教程、架构培训、技术早报和方案沉淀必须能回链源码路径",
            "不要用字数、生成速度或内容条数当工程价值指标",
        ],
    )
    and has_all(
        "README.md",
        [
            "进入知识生产",
            "上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀",
            "上下文资产",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "20年架构老兵的AI探索，让WorkBuddy帮你超越身边的人",
            "腾讯云开发者",
            "知识库先行、常用工作流固化成专家、信息整理可自动化、规则越具体越稳定、工具按职责分工",
            "不把 WorkBuddy 写成默认依赖",
        ],
    ),
)

check(
    "wise agent gates WorkBuddy style local coding agent without replacing project standards",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_code_understanding_tools,
        [
            "WorkBuddy / 本地执行型 Coding Agent",
            "读项目上下文 -> 对齐项目 / 架构 / Wind 约规 -> 明确写入范围 -> 生成候选 diff",
            "依赖 / 配置冲突决策澄清门禁",
            "Java 项目以 `wind-coding-conventions` 的通用层为规则来源",
            "Wind/Nobe 专项按声明、依赖、包名、类型或模块上下文启用",
            "系统设计、TDD、源码级 CR、安全可靠性、生产风险和受控工程执行仍回 `资深架构师`",
            "不把 WorkBuddy 类工具输出当成项目编码约规",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "WorkBuddy 驱动 SpringBoot 应用开发实战：一句话生成 JWT 登录+RabbitMQ 消费+MyBatis-Plus 全套代码",
            "行者全栈开发",
            "本地 IDE / 文件系统执行",
            "不把 WorkBuddy 写成默认依赖、当前会话可用工具、项目编码约规、Wind 项目约规替代、架构师 CR 替代、TDD 替代、Git 授权、测试通过或上线审批",
            "可以吸收 WorkBuddy 类本地执行型 Coding Agent 的上下文扫描、项目规则读取、写入范围确认、候选 diff、依赖 / 配置冲突决策澄清门禁、验证命令和交接闭环",
        ],
    ),
)

check(
    "wise agent absorbs Karpathy coding hygiene without new dependency",
    has_all(
        agents_rules,
        [
            "外科手术式变更",
            "每一行修改都必须能回到用户目标、验收标准、源码事实或验证失败",
            "只清理本次改动制造的 orphan",
        ],
    )
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_source_map,
        [
            "multica-ai/andrej-karpathy-skills",
            "Think Before Coding",
            "Simplicity First",
            "Surgical Changes",
            "Goal-Driven Execution",
            "先暴露假设和分歧、简单优先、外科手术式变更、把任务转成可验证目标并循环验证",
            "不安装该仓库",
            "不得把其变成新流程、安装依赖、替代 TDD / 架构师 CR / 项目编码规范",
        ],
    ),
)

check(
    "design pattern guidance is gated by real variation axis",
    has_all(
        wise_agent_delivery_lifecycle,
        [
            "设计和编码进入下一阶段前，必须先识别稳定点 / 变化点",
            "业务规则、状态行为、外部依赖、平台差异、技术选型",
            "真实证据",
            "没有 owner、验收方式和测试边界的未来想象，按过度设计风险处理",
        ],
    )
    and has_all(
        product_skill,
        [
            "先找变化轴再交工程",
            "区分稳定业务事实与会变的业务规则、状态行为、外部依赖、平台差异和扩展场景",
            "没有证据的未来变化只标为待观察",
            "不作为架构拆分或平台化依据",
        ],
    )
    and has_all(
        architecture,
        [
            "先找真实变化轴，再封装变化",
            "业务规则、状态行为、外部依赖、平台差异或技术选型",
            "owner 和测试边界",
            "没有同类需求或没有验收方式的变化，不作为抽象依据",
        ],
    )
    and has_all(
        coding,
        [
            "不得为了套设计模式而新增接口、策略、工厂、状态对象、规则层或配置项",
            "真实变化轴",
            "owner、验收方式和测试边界",
        ],
    )
    and has_all(
        wind_skill_conventions,
        [
            "服务、接口、策略、工厂、状态机、规则层和配置化必须来自真实变化轴",
            "业务规则、状态行为、外部通道、平台差异或技术选型",
            "不为套设计模式新增浅服务或单实现抽象",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "设计模式的本质",
            "找到变化，封装变化",
            "真实变化轴、稳定边界、职责分离、依赖倒置",
            "不把策略、工厂、状态机、规则引擎、接口隔离或依赖倒置写成默认答案",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "设计模式的本质",
            "真实变化轴、稳定边界、职责分离、依赖倒置",
            "不把策略、工厂、状态机、规则引擎、接口隔离或依赖倒置写成默认答案",
        ],
    ),
)

check(
    "grill-me is a standalone project-owned capability",
    frontmatter(grill_me_skill).strip().startswith("name: grill-me")
    and has_all(
        grill_me_skill,
        [
            "# Grill Me",
            "一次只问一个",
            "每问给推荐答案",
            "Facts 先查",
            "Decisions 才问",
            "问题台账",
            "每条记录都必须原样保留 `裁决动作：<action>` 与 `最终结论：<state>`",
            "语义重复",
            "shared understanding",
            "未确认前不执行",
            "red_lines",
            "huaxia-practical-wisdom",
        ],
    )
    and has_all(
        grill_me_agent,
        [
            'display_name: "Grill Me"',
            "$grill-me",
            "allow_implicit_invocation: true",
        ],
    )
    and has_reference_header(grill_me_question_ledger)
    and has_task_reading_index(grill_me_question_ledger)
    and has_reference_header(grill_me_source_map)
    and has_task_reading_index(grill_me_source_map)
    and has_all(
        grill_me_source_map,
        [
            "mattpocock/skills",
            "K4CN1LxsZgFR2FYv7f8Y3w",
            "jw7pqTwco_lLGnN_KmExig",
            "项目自有独立 `grill-me`",
            "不安装上游全仓库",
        ],
    )
    and has_all(wise_agent_source_map, ["../../grill-me/references/source-map.md"])
    and has_none(
        wise_agent_source_map,
        [
            "https://mp.weixin.qq.com/s/K4CN1LxsZgFR2FYv7f8Y3w",
            "https://mp.weixin.qq.com/s/jw7pqTwco_lLGnN_KmExig",
        ],
    )
    and has_all(
        grill_me_question_ledger,
        [
            "问题 ID",
            "决策主题",
            "已查证据",
            "最终结论",
            "语义重复",
            "自决边界",
            "证据先行的问询裁决",
            "命题类型",
            "ask-owner",
            "裁决动作到最终结论的确定映射",
            "每条记录都必须原样包含 `裁决动作：<action>` 和 `最终结论：<state>`",
            "fact-confirmed` -> `confirmed",
            "decision-reused` -> 沿用原最终结论",
            "ask-owner` -> `pending",
            "red_lines",
            "决策快照",
        ],
    )
    and has_all(
        wise_agent_skill,
        [
            "按需装载独立能力 `grill-me`",
            "问题台账、历史去重和决策快照由该 Skill 负责",
            "方案、计划或设计的关键分叉盘问、历史去重和决策快照",
        ],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "方案、计划或设计的决策压力测试",
            "`grill-me`",
            "问题台账、历史去重、决策快照与执行前对账",
        ],
    ),
)

check(
    "wise agent metadata requires coordination evidence rather than generic verification",
    has_all(
        wise_agent_skill,
        [
            "跨专业协同、跨阶段交付、跨轮状态管理、能力组合、状态恢复或知识回流",
            "单一专业任务（包括只读 CR）直接加载对应 Skill",
        ],
    )
    and has_none(
        wise_agent_skill,
        ["能力组合、独立验证或知识回流"],
    ),
)

check(
    "huaxia practical wisdom is an independent routed capability",
    frontmatter(huaxia_skill).strip().startswith("name: huaxia-practical-wisdom")
    and has_all(
        huaxia_skill,
        [
            "# 华夏经世智慧",
            "现实决策与行动校准",
            "察实",
            "正名",
            "审时",
            "权衡",
            "行验",
            "化",
            "经世决策卡",
        ],
    )
    and has_all(
        huaxia_agent,
        [
            'display_name: "华夏经世智慧"',
            "$huaxia-practical-wisdom",
            "allow_implicit_invocation: true",
        ],
    )
    and "老祖宗智慧" in frontmatter(huaxia_skill)
    and has_all(
        wise_agent_skill,
        [
            "按需装载独立能力 `huaxia-practical-wisdom`",
            "不复制其框架和方法",
        ],
    )
    and has_none(
        wise_agent_skill,
        [
            "阴阳互根",
            "庖丁解牛",
            "无为而治",
            "先为不可胜",
            "知行合一",
            "治未病与一张一弛",
        ],
    )
    and has_none(
        wise_agent_source_map,
        ["Gitee 仓库 `aiami/huaxia-wisdom`"],
    )
    and has_none(
        wise_agent_verification_release,
        [
            "Wisdom Lens 只参与工程取舍：阴阳平衡",
            "Wisdom Lens 只做反偏：循名责实",
        ],
    )
    and has_none(
        wise_agent_domain_expert_distillation,
        ["## 8. 老祖宗反偏问题"],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "现实决策、组织协作、长期成长、时势与行动取舍",
            "`huaxia-practical-wisdom`",
            "事实回读、决策卡、可逆行动、止损与反馈验证",
        ],
    ),
)
check(
    "huaxia practical wisdom keeps classic lenses practical and bounded",
    has_reference_header(huaxia_classical_lenses)
    and has_task_reading_index(huaxia_classical_lenses)
    and has_all(
        huaxia_classical_lenses,
        [
            "周易与阴阳",
            "道德经与庄子",
            "儒家与法家",
            "兵家",
            "中医系统观",
            "阴阳五行与五德终始",
            "最多选三个镜片",
            "不得用卦象、爻辞或五行生克预测具体结果",
            "不得据此判断疾病或给出治疗方案",
            "不用于预测王朝、组织命运、个人吉凶或证明任何权力合法性",
        ],
    )
    and has_all(
        huaxia_decision_practice,
        [
            "已知事实、合理推断、待确认项、范围外不做",
            "最小可逆动作",
            "最坏失败",
            "经世决策卡",
            "不追求“古今思想统一”",
        ],
    ),
)
check(
    "huaxia practical wisdom preserves evidence and source boundaries",
    has_reference_header(huaxia_evidence_boundaries)
    and has_reference_header(huaxia_source_map)
    and has_all(
        huaxia_evidence_boundaries,
        [
            "现实事实",
            "经典原文",
            "现代解释",
            "现实类比",
            "未核对不得加引号或写“原话”",
            "不诊断、不处方、不替代就医",
            "`hanzi-philology`",
        ],
    )
    and has_all(
        huaxia_source_map,
        [
            "aiami/huaxia-wisdom",
            "eef49d54e6266b1afc568ef591a6a2d4abd5ad8e",
            "只参考其 24 个框架的场景分类和行动工具思路",
            "不复制正文、示例、固定输出、古风人格、宽泛自动触发",
            "外部 Skill 不是本 Skill 的运行依赖",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "作为项目自有 `huaxia-practical-wisdom` 的内容参考来源",
            "不复制原文、示例、固定输出、宽泛自动触发、古风人格或“全家桶”结构",
        ],
    ),
)
check(
    "wise agent gates AI bug reports and patches with wisdom lens",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(huaxia_skill, ["表象反复、预防不足", "中医系统观", "不输出工程准出结论"])
    and has_all(
        wise_agent_verification_release,
        [
            "## 5B. AI bug / 补丁门禁",
            "复现 / 触发条件",
            "源码锚点",
            "根因假设",
            "同类影响范围",
            "最小修复",
            "验证命令 / 结果",
            "创可贴式修复",
            "可进入 CR",
            "继续根因分析",
            "退回待确认",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "Linus一句话说透AI局限",
            "https://mp.weixin.qq.com/s/J6YC2K4PDavJ_4j_KN0D3g",
            "AI bug report 需要人类维护者验证",
            "AI patch 不能自证",
            "创可贴式修复需要退回根因分析",
            "复现 / 根因 / 同类影响 / 独立验证",
            "不得把模型自述、补丁候选、局部 guard、放宽断言或工具告警写成已修复、测试通过、CR 结论、合并判断或上线审批",
        ],
    ),
)
check(
    "wise agent keeps three-card handoff protocol",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_product_to_engineering,
        [
            "3A. 三卡交接协议",
            "Product Context Card / 产品上下文交接卡",
            "Engineering Handoff Card / 工程执行交接卡",
            "生产交付卡 / 生产 Loop 交接卡",
            "规范主题 / 产品文档路径:",
            "规范主题 / 产品文档路径 / 目标系分文档路径:",
            "同一能力从产品到系分必须保持规范主题和精确路径",
            "三卡都不是 Execution Grant",
            "三卡必须区分事实、推断、待确认和范围外不做",
        ],
    )
    and has_all(
        wise_agent_planning_execution_admission,
        [
            "三卡交接结论",
            "7A. 三卡到架构师的消费规则",
            "Product Context Card",
            "Engineering Handoff Card",
            "生产交付卡",
            "缺失时回 `产品架构专家`",
            "缺失时停在知止者",
            "缺失时只标记 Loop Candidate",
        ],
    )
    and has_all(
        product_skill,
        [
            "产品交接只交事实与验收",
            "Product Context Card / 产品上下文交接卡",
            "不判定 GSD/CAD 准入",
            "不生成 Engineering Handoff Card、生产交付卡、Plan Grant、Execution Grant 或上线审批",
            "产品合议只评产品内容",
            "不替代 `wise-agent` 的跨角色准入、工程分派、发布门禁",
            "也不判定系分或代码可执行性",
        ],
    )
    and has_all(
        product_ai_native_context,
        [
            "Product Context Card / 产品上下文交接卡",
            "不生成 Engineering Handoff Card、生产交付卡或 Execution Grant",
            "产品专家不输出 Engineering Handoff Card、生产交付卡、Plan Grant、Execution Grant、CAD Grant 或上线批准",
        ],
    )
    and has_all(
        senior_skill,
        [
            "消费交接卡而不重开流程",
            "Product Context Card",
            "Engineering Handoff Card",
            "生产交付卡",
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
            "生产交付卡",
            "三卡都不是 Plan Grant / Execution Grant、测试通过、CR 结论、生产审批或 Git 授权",
        ],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "三卡交接",
            "Product Context Card",
            "Engineering Handoff Card",
            "生产交付卡",
            "不让任一卡替代 Execution Grant、测试通过或上线审批",
        ],
    )
    and has_none(
        wise_agent_planning_execution_admission,
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
    "wise agent decision wayfinding stays upstream of spec and execution",
    has_all(
        wise_agent_skill,
        [
            "决策寻路",
            "目标大致存在，但到达目标的路线仍模糊",
            "planning-execution-admission.md",
        ],
    )
    and has_all(
        wise_agent_planning_execution_admission,
        [
            "## 2A. 决策寻路准入",
            "Destination",
            "Decisions so far",
            "Frontier",
            "Not yet specified",
            "Out of scope",
            "Next decision",
            "地图只作索引",
            "每轮最多关闭一个决策",
            "grill-me",
            "research",
            "prototype",
            "prerequisite task",
            "不得自动创建 Issue、分支、Worker 或外部任务系统",
            "路线清晰后才进入 Spec、最小计划或 Goal Ready",
        ],
    )
    and has_all(
        wise_agent_goal_governance,
        [
            "决策寻路尚未完成",
            "不能从 `Draft` 进入 `Ready`",
        ],
    )
    and has_all(
        wise_agent_product_to_engineering,
        [
            "-> [跨轮且路线模糊时] 决策寻路",
            "| 决策寻路 |",
            "不是所有问题地图的必经阶段",
        ],
    )
    and has_all(
        "README.md",
        [
            "决策寻路",
            "目标大致明确，但路线仍模糊",
            "不要生成 Spec、计划或执行任务",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "https://mp.weixin.qq.com/s/_u7U-aXg0KXXzyFNtLcvIw",
            "https://www.aihero.dev/skills-wayfinder",
            "mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md",
            "地图是索引而不是决策正文",
            "不安装 wayfinder",
        ],
    ),
)
check(
    "wise agent keeps capability loading and responsibility boundary",
    has_reference_header(wise_agent_skill_type_owner_routing)
    and has_task_reading_index(wise_agent_skill_type_owner_routing)
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "# 能力装载与责任路由",
            "人类责任 Owner",
            "知止者",
            "专业能力",
            "独立 Checker",
            "最小装载算法",
            "一个主能力",
            "不限制未来新增的安全能力",
            "product verification",
            "code quality and review",
            "CI/CD and deployment",
            "runbooks",
            "infrastructure operations",
            "新能力接入门禁",
            "模型默认不知道、团队反复踩坑或确定性脚本",
            "与现有能力抢触发、复制规则或成为第二行动主体",
            "安装、同步和高风险权限是否已获用户授权",
            "普通一步任务不触发知止者重流程",
            "跨能力任务只产生一个综合结论",
            "source-map.md",
        ],
    ),
)
check(
    "ai-native source map records Harness Engineering split boundary",
    has_all(
        wise_agent_source_map,
        [
            "给野马套上缰绳：Agent Harness 工程实践",
            "Harness Engineering",
            "2 Agent + N Skill",
            "工具签名即文档",
            "事务边界",
            "独立 Reviewer",
            "capability-routing.md",
            "不把多 Agent、Sub-Agent、RPA、外部 Harness、自动开 PR、状态文件或任一工具能力写成当前会话默认可用",
        ],
    ),
)
check(
    "wise agent metadata triggers real work and excludes simple answers",
    "name: wise-agent" in frontmatter(wise_agent_skill)
    and all(
        term in frontmatter(wise_agent_skill)
        for term in [
            "用户显式说“知止者”“wise-agent”“自己判断并推进”“按需调用能力”",
            "跨专业协同、跨阶段交付、跨轮状态管理",
            "单一专业任务（包括只读 CR）直接加载对应 Skill",
            "简单问答、翻译和一步措辞不触发",
        ]
    )
    and has_all(
        wise_agent_agent,
        [
            "理解事实，知所止而后行动",
            "统一行动主体",
            "先定目标、权限、完成证据和停止条件",
            "装载最小专业能力",
            "独立证据验证",
        ],
    ),
)
check(
    "wise agent defaults to Chinese while preserving requested and literal language",
    has_all(
        wise_agent_skill,
        [
            "默认使用中文与用户交流、说明判断并交付结果",
            "用户明确要求其他语言时遵从用户要求",
            "代码、命令、协议字段、专有名词和原文引用保持原样",
        ],
    )
    and has_all(
        wise_agent_agent,
        [
            "默认使用中文响应",
            "用户明确要求其他语言时除外",
            "代码、命令、协议字段、专有名词和原文引用保持原样",
        ],
    ),
)
check(
    "wise agent keeps stable canonical identity and capability model",
    has_all(
        wise_agent_skill,
        [
            "# 知止者",
            "“知止”不是消极停止",
            "目标所止、权限所止、证据所止",
            "知止而后有定",
            "统一智能行动主体",
            "能力不以本表为上限",
            "专业能力完成后仍由知止者综合结果",
        ],
    )
    and has_all(
        wise_agent_agent,
        ['display_name: "知止者"', "知所止而后行动", "先定目标、权限、完成证据和停止条件"],
    )
    and has_all(
        agents_rules,
        [
            "默认交互与责任模型",
            "`wise-agent` 是它的显式协同能力入口",
            "不能混写成“所有任务都必须加载 `wise-agent`”",
            "它不是少做或不行动",
            "何时应停止或交还人类",
        ],
    )
    and has_all(
        "README.md",
        ["### 3. 知止者如何工作", "它不是不行动", "有方向、有分寸、有收口"],
    )
    and has_all(
        wise_agent_cognition_model,
        ["目标止于何处", "权限止于何处", "何种证据才算完成", "何时停止或交还人类"],
    )
    and has_none(
        wise_agent_skill,
        ["产研智人", "知行者", "智止者", "AI Native Harness Contract", "只负责调度和门禁"],
    )
    and has_none("README.md", ["知行者", "智止者"])
    and has_none(
        wise_agent_engineering_governance,
        ["AI Native Harness Contract"],
    ),
)
check(
    "wise agent defines minimal default output",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS),
)
check(
    "wise agent avoids heavy default output template",
    has_none(
        wise_agent_skill,
        [
            "默认输出骨架",
            "角色 Loop 场景视图：只读理解 / 产研交付 / 验证发布 / 知识回流（不是并列入口）",
            "当前阶段：设计 / 设计评审 / TDD-测试设计 / 编码实现 / 编码评审 / 可用性-安全性-可靠性评估 / 发布复盘",
            "角色视角：主责角色 / 协作角色 / AI Maker / AI Checker / 人工 owner",
            "Loop Contract：Goal / State / Plan / Action / Observe / Decide / 决策澄清门禁 / Verify / 停止交接",
            "自我问询：已知问题 / 可自答问题 / 需 owner 问题",
            "自我回答：答案 / 证据来源 / 置信度 / 进入下一阶段理由",
            "小闭环决策澄清门禁：自决推进 / 询问 owner / 继续收敛 / 停止交接",
        ],
    ),
)
check(
    "wise agent references preserve lifecycle governance and source boundaries",
    has_all(
        wise_agent_product_to_engineering,
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
            "知止者交接结论",
            "AI 代码交付闭环",
            "code-delivery.md",
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
        wise_agent_engineering_governance,
        [
            "OpenSpec 定义做什么，Superpowers 定义怎么高质量地做，Harness 定义谁做、按什么顺序做、能改哪里、怎么验证、怎么交接",
            "Superpowers 官方插件状态、能力调度矩阵、MIT 许可和安全边界读 `superpowers-skill-library.md`",
            "调度 Superpowers skills",
            "交付执行契约 v3",
            "内部执行契约版本",
            "pre-flight plan review",
            "单一 Task Reviewer",
            "文件化 handoff",
            "progress ledger",
            "final broad review",
            "model / cost policy",
            "execution state gate",
            "authorized workspace policy",
            "本仓库不再复制 Superpowers 上游 Skill 或 helper",
            "外部插件目录、脚本、本地服务、`.superpowers/` 或其他状态目录只有用户或项目规则明确授权时才可创建或运行",
            "外部 release、marketplace、bootstrap、脚本和工具支持变化只作为带日期的 source-map 事实",
            "交付执行契约版本: v1 / v2 / v3",
            "SDD 套件版本: 无 / SDD v6 方法契约 / 外部工具已授权",
            "执行状态: Ready / Running / Review / Fix / Verified / Blocked / Handoff",
            "Superpowers 通过官方 Codex 插件独立提供",
            "Superpowers 只补 brainstorming、计划、TDD、调试、CR 和完成前验证等方法纪律",
            "插件已安装也不能自动获得脚本、worktree、Git、subagent、联网或项目写入授权",
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
            "planning-execution-admission.md",
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
        wise_agent_planning_execution_admission,
        [
            "知止者的产研交付视图准入结论",
            "是否需要 GSD Round 0",
            "Wave / Atomic Task 候选",
            "Superpowers 方法门禁",
            "CAD 候选缺口",
            "GSD/CAD 授权策略卡",
            "默认授权哪些任务",
            "Codex 的“替我审批”模式",
            "Execution Grant 缺口",
            "下一步 owner",
            "知止者决定“是否进入产研交付视图、是否启用 GSD/CAD 内部层，以及下一步 owner”",
            "GSD-like 决定“哪些阶段和任务可以被执行”",
            "CAD Mode 决定“当前选中的原子任务是否可以自动执行”",
            "Execution Grant 决定“本轮实际允许做什么”",
            "授权策略不是让每个任务都重新问一次，也不是让所有动作无条件通过",
            "把授权前移到 Goal 任务计划、Wave 或 CAD Grant 层",
            "Skill 自行开启",
            "Superpowers 在 GSD 中只作为方法纪律层",
            "官方插件可以独立安装并由知止者按需调度",
            "启用状态不能成为运行脚本、创建 worktree、启动 subagent、采用外部 Git 默认动作或扩大项目写入的授权",
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
            "在知止者中复制 CAD 每轮 Pick / Red / Green / Review / Refactor / Verify / Record 细则",
        ],
    )
    and has_all(
        wise_agent_code_understanding_tools,
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
            "当前机器已验证 Gemini CLI `0.49.0` 可在 Node `20.20.2` 下启动",
            "作为只读候选",
            "当前状态核验通过",
            "先读懂真实上下文、数据流和项目约规",
            "代码变少是结果，不是 code golf",
            "外部 benchmark 和收益数据只能作为参考",
            "不把某台机器的安装路径、版本、shell 配置或登录状态写成默认可用能力",
            "不把任何工具写成默认依赖",
            "不默认安装、联网、登录、写文件、写配置或改代码",
            "不默认运行远端安装脚本、插件安装命令、lifecycle hook、`/understand`、`/understand --auto-update`、dashboard、本地服务、post-commit hook 或 Git LFS 配置",
            "不默认写入 `.github/copilot-instructions.md`、`.vscode/mcp.json`",
            "不默认写入、提交或同步 `.understand-anything/`、`knowledge-graph.json`、图谱中间产物、dashboard 产物或 hook",
            "不把工具输出当作 Execution Grant、CAD 授权、测试通过、发布批准或合规结论",
            "不把 Ponytail 的“少写”当作删除输入校验、错误处理、安全、可访问性、资金/权限/生产兜底或必要测试的理由",
            "不把外部 benchmark、star 数或插件生态热度写成当前项目收益、工程质量、测试通过、CR 结论或上线依据",
        ],
    )
    and has_all(
        wise_agent_verification_release,
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
            "生产生效验证门禁",
            "生产生效验证卡",
            "版本回读",
            "配置回读",
            "冒烟验证",
            "观测确认",
            "工单 / Goal 回写",
            "观测和回滚",
            "复盘闭环",
            "当前可信度判断",
            "残余风险清单",
            "先给结论",
            "交付完整性要求",
            "code-delivery.md",
            "spec-template-practices.md",
            "Spec 强度",
            "Spec / AC 编号",
            "AC 覆盖",
            "漂移检查",
            "独立验证证据",
            "知识回流",
            "一次通过率",
            "CR 高频问题",
            "知识沉淀、规范统一、质量底线",
            "技术债归类",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "微信“环境异常”验证页，未读取到正文",
            "不把该链接作为已吸收来源",
            "第 3 篇：一个好的 Loop 到底由什么组成",
            "Seeek X",
            "知止者统一入口和 GSD/CAD/Goal 压缩重构",
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
            "code-delivery.md",
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
            "代码写完了，谁负责确认写对了，预发环境是OK吗？",
            "大鱼北游",
            "生产生效验证门禁",
            "版本回读、配置回读、冒烟验证、观测确认和工单回写",
            "不把“已部署”“已推配置”“测试通过”“页面能打开”写成预发 OK、生产 OK、合并判断或上线审批",
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
            "2026-07-17",
            "superpowers@openai-api-curated",
            "installed, enabled",
            "11c74d6b",
            "manifest 版本为 `5.1.3`",
            "superpowers-skill-library.md",
            "仓库退役 `references/external-superpowers/` 和本地 helper",
            "不再复制上游 Skill",
        ],
    ),
)
check(
    "wise agent keeps intent to production lifecycle",
    has_reference_header(wise_agent_delivery_lifecycle)
    and has_task_reading_index(wise_agent_delivery_lifecycle)
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_lifecycle,
        [
            "# 交付生命周期",
            "Role Collaboration Loop Map",
            "Intent-to-Production Role Loop Map",
            "生产生效验证结论",
            "## 1A. 阶段与能力衔接",
            "阶段只回答“现在位于生命周期哪里”",
            "能力路由只回答“当前需要什么专业能力和独立验证”",
            "能力边界变化时只修改 `capability-routing.md`",
            "具体主能力与协同能力始终回到 `capability-routing.md` 判断",
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
            "运行支持 / 维护演进 / 能力退役",
            "生命周期覆盖审查",
            "UED / 交互设计",
            "属于产品岗",
            "AI Maker",
            "AI Checker",
            "Design Reviewer",
            "Code Reviewer",
            "Usability / Safety / Security Reviewer",
            "GStack 角色链映射",
            "forcing questions",
            "八段准出链",
            "生产交付审查卡",
            "生产生效验证卡",
            "/office-hours",
            "/plan-ceo-review",
            "/plan-eng-review",
            "/plan-design-review",
            "/review",
            "/qa",
            "/ship",
            "命令名只作触发别名",
            "质量 / 测试门禁",
            "发布 owner",
            "版本回读",
            "配置回读",
            "冒烟",
            "product-architecture-expert/references/product-design-and-prd.md",
            "senior-software-architect/references/testing.md",
            "senior-software-architect/references/coding-review-deep-dive.md",
            "写代码的 Agent 不能自证通过",
            "不允许模拟模块、内存版业务 Service 或无业务入口 demo",
            "把阶段名当能力来源",
            "目标、计划、原子执行、执行契约和授权边界都是本流程的内部层",
            "小闭环决策澄清门禁结论",
            "自决推进",
            "询问 owner",
            "继续收敛",
            "停止交接",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "Loop Engineering：让 AI 自己跑起来，你只管验收",
            "https://mp.weixin.qq.com/s/Ng_qit1H5t6yhqjVGNIHzg",
            "作者/账号字段为 `算法屋`",
            "delivery-lifecycle.md",
            "Automations、Worktrees、Skills、Connectors、Sub-agents、State",
            "从意图 / 需求收集到生产交付的多角色 Loop",
            "不把 `/goal`、定时器、连接器、自动开 PR、sub-agent、worktree 或任何工具能力写成当前会话默认可用",
        ],
    )
    and has_all(
        "README.md",
        [
            "默认交互与责任模型",
            "`$wise-agent` 是显式协同入口",
            "不表示每个任务都必须加载它",
            "察 -> 辨 -> 谋 -> 行 -> 验 -> 化",
            "简单任务直接完成",
            "复杂任务才使用计划、SDLC、Goal、Loop、Worker 或 Checker",
            "专业能力按需渐进加载",
            "无论内部用了多少能力，对用户只形成一个综合结论",
        ],
    ),
)
check(
    "wise agent coordinates specialized skills by role",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_lifecycle,
        [
            "## 1A. 阶段与能力衔接",
            "能力 owner、专业 Skill、Worker / Checker 和最小装载规则统一读取 `capability-routing.md`",
            "两者不得各自维护一套 owner 表",
            "选择一个主能力、必要的协同能力、明确不加载的能力和独立 Checker",
            "外部工具或框架只能补当前阶段的一个方法缺口",
            "能力边界变化时只修改 `capability-routing.md`",
            "具体主能力与协同能力始终回到 `capability-routing.md` 判断",
        ],
    )
    and has_none(
        wise_agent_delivery_lifecycle,
        ["主 Skill", "角色协作判断矩阵", "能力来源与协同矩阵", "知止者编排者"],
    ),
)
check(
    "wise agent keeps three layer feedback cadence",
    has_all(
        wise_agent_delivery_lifecycle,
        [
            "三层反馈节奏",
            "Agentic Coding Loop",
            "Developer Feedback Loop",
            "External Feedback Loop",
            "外层慢反馈如何修正 Vision",
            "中层如何修正 Spec",
            "内层如何执行和验证",
            "不让内层 AI 自测替代产品判断或真实用户反馈",
            "越外层越慢、越决定方向",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "吴恩达对 Loop Engineering 的理解真犀利。",
            "https://mp.weixin.qq.com/s/ryi2RRG-eZjtoy-n3cnFnw",
            "AI产品阿颖",
            "2026-07-01 10:44:36 Asia/Shanghai",
            "Agentic Coding Loop、Developer Feedback Loop、External Feedback Loop",
            "外层慢反馈修正 Vision",
            "中层把上下文翻译成 Spec",
            "内层按 Spec / Evals 执行和验证",
        ],
    ),
)
check(
    "wise agent keeps gstack production delivery review",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_lifecycle,
        [
            "GStack 角色链审查结论",
            "forcing questions",
            "连续逼问",
            "生产交付审查卡",
            "生产生效验证卡",
            "八段准出链",
            "Ship 只按生产交付审查卡和生产生效验证卡准出",
        ],
    )
    and has_all(
        wise_agent_verification_release,
        [
            "生产交付审查标准",
            "生产交付审查卡",
            "生产生效验证门禁",
            "生产生效验证卡",
            "业务场景模拟验收",
            "业务场景模拟验收卡",
            "场景来源",
            "公开资料、业内共识、行业标准规范",
            "版本回读证据",
            "配置回读证据",
            "工单 / Goal 回写",
            "Ready / Not Ready / Human Approval Required",
            "Git/PR/merge/部署授权",
            "P0 blockers",
            "不把测试通过、PR 数或 Agent 自述当上线批准",
        ],
    )
    and has_all(
        wise_agent_superpowers_library,
        [
            "角色链审查",
            "产品、设计、工程、QA、安全和发布视角",
            "不是知止者之外的新主流程",
        ],
    ),
)
check(
    "wise agent keeps autonomous discovery delivery loop",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_lifecycle,
        [
            "自我挖掘与确认边界",
            "自主交付控制卡",
            "可自我挖掘",
            "可自我规划",
            "可自动执行",
            "必须人工确认",
            "确认规则",
            "不能确认业务意图、需求价值、用户验收、架构批准、测试通过、CR 准出、Git 授权或上线审批",
            "每个阶段的小闭环完成后，先自问再问人",
            "完整盘问、问题台账、历史去重、自决和决策快照由该 Skill 负责",
            "自决推进",
            "询问 owner",
        ],
    )
    and has_all(
        wise_agent_delivery_execution_control,
        [
            "自主推进边界",
            "Discover evidence",
            "Confirm boundary",
            "Requirement CR",
            "TDD candidate / RED",
            "Complete / Loop / Stop / Human handoff",
            "小闭环决策澄清门禁",
            "自决推进",
            "询问 owner",
            "继续收敛",
            "停止交接",
            "自我规划当人工确认",
            "任务结束责任闭环",
            "交付责任自检",
            "下一任务计划问询",
            "当前主 blocker / 建议答案 / 依据 / 影响 / 默认暂停点:",
            "不要同时摊开多个 blocker",
        ],
    )
    and has_all(
        wise_agent_code_delivery,
        [
            "自主交付完成判断",
            "Agent 自述触发",
            "Complete / Loop / Stop / Human handoff",
            "必须人工确认项",
            "不能把任务标记为完成",
        ],
    )
    and has_all(
        wise_agent_source_map,
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
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_product_to_engineering,
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
        wise_agent_source_map,
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
        repo_source_map,
        [
            "问题核心诊断、反脑补证据边界、概念定名、需求止损",
            "定向 / 定性 / 定位 / 定量变化治理",
            "不把传统文化或医学观点写成产品事实、架构结论、合规结论、生产审批或 Execution Grant",
        ],
    ),
)
check(
    "wise agent keeps Superpowers skill library boundary",
    has_reference_header(wise_agent_superpowers_library)
    and has_task_reading_index(wise_agent_superpowers_library)
    and has_all(
        wise_agent_superpowers_library,
        [
            "# Superpowers Skill Library 能力调度",
            "不是第二套主流程",
            "外部能力只能补方法",
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
            "superpowers@openai-api-curated",
            "2026-07-17",
            "11c74d6b",
            "manifest 版本为 `5.1.3`",
            "release `v6.1.1`",
            "已安装不等于执行授权",
            "Superpowers 不成为第二 Owner",
            "关键分叉未决才升级 `grill-me`",
            "外部框架归位",
            "GStack",
            "角色链审查",
            "仓库级记忆",
            "MIT License",
            "本仓库不再复制上游 Skill",
            "插件脚本、本地服务、`.superpowers/`、依赖安装和联网访问必须逐项满足当前任务需要",
            "Git 提交、推送、PR、merge、worktree 创建与清理继续遵守仓库 `AGENTS.md`",
            "安装、升级与退役闭环",
            "调度结论格式",
        ],
    ),
)
check(
    "wise-agent routes installed official Superpowers without vendored snapshot",
    has_all(
        wise_agent_superpowers_library,
        [
            "superpowers@openai-api-curated",
            "installed, enabled",
            "用户授权 / 项目 `AGENTS.md` > 知止者 > 专业 Skill > Superpowers",
            "Superpowers 不成为第二 Owner",
            "已安装不等于执行授权",
            "不再复制上游 Skill",
            "删除 `external-superpowers/`",
            "新会话行为冒烟",
        ],
    )
    and has_none(
        wise_agent_superpowers_library,
        [
            "上游原始 Skill 统一保存为 `upstream-skill.md`",
            "external-superpowers/subagent-driven-development/upstream-skill.md",
        ],
    )
    and not (ROOT / "wise-agent/references/external-superpowers").exists(),
)
check(
    "plan generation waits for owner decisions",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_execution_control,
        [
            "计划生成准入先于计划审查",
            "仍夹带未决 Owner 判断",
            "装载独立 `grill-me` 关闭最高价值 Decision",
            "决策快照经 Owner 确认后",
        ],
    ),
)
check(
    "Trellis remains an evidence-gated optional carrier",
    has_all(
        wise_agent_superpowers_library,
        [
            "`Trellis` 是仓库级 Agent Harness",
            "`@mindfoldhq/trellis`",
            "现有 `AGENTS.md`、Issue、Spec、Goal Ledger",
            "重复失败证据",
            "`.trellis/spec/`、`.trellis/tasks/`、`.trellis/workspace/`",
            "AGPL-3.0",
            "非关键任务",
            "显式授权",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "Superpowers不再是最佳实践：2026下半年你该换个思路了",
            "FF的客栈",
            "2026年7月1日 08:15",
            "计划生成准入先于计划审查",
            "不吸收文中的效率比例、可提交质量比例",
            "mindfold-ai/Trellis",
            "@mindfoldhq/trellis",
            ".trellis/spec",
            ".trellis/tasks",
            ".trellis/workspace",
            "AGPL-3.0",
        ],
    ),
)
check(
    "wise agent keeps spec template practices gate",
    has_reference_header(wise_agent_spec_template_practices)
    and has_task_reading_index(wise_agent_spec_template_practices)
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_spec_template_practices,
        [
            "# Spec 模板最佳实践",
            "本文定义知止者研发流程中 Spec / SDD / OpenSpec / Harness 输入的模板落地方式",
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
            "Delta Spec",
            "ADDED / MODIFIED / REMOVED",
            "影响的 PRD、SDD / OpenSpec、实现 Spec、AC、测试、接口 / 事件、发布风险和通知 owner",
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
            "代码偏离、Spec 缺失或需求变化",
            "Spec 缺失先补 Spec 并重新 Review",
            "风险自查",
            "AI 生成失败时，先把失败场景回写到 Spec / AC / 测试或项目规则",
            "Spec 也是实现和 CR 的检查清单",
            "轻重切换",
        ],
    )
    and has_all(
        wise_agent_code_delivery,
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
        wise_agent_product_to_engineering,
        [
            "spec-template-practices.md",
            "可评审 Spec 模板",
            "Spec 强度、五段式骨架、AC 与测试映射、spec-lint、AC 覆盖和漂移检查",
        ],
    )
    and has_all(
        wise_agent_engineering_governance,
        [
            "spec-template-practices.md",
            "AC 编号与测试映射",
            "spec-lint / AC 覆盖 / 漂移检查",
            "可评审 Spec 模板",
        ],
    )
    and has_all(
        wise_agent_verification_release,
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
        wise_agent_source_map,
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
        repo_source_map,
        [
            "Spec/SDD 模板最佳实践",
            "Spec 驱动开发：让 AI 知道该写什么，不该写什么",
            "规范驱动开发（SDD）：用 AI 写生产级代码的完整指南",
        ],
    ),
)
check(
    "wise agent keeps goal governance gate",
    has_reference_header(wise_agent_goal_governance)
    and has_task_reading_index(wise_agent_goal_governance)
    and has_all(
        wise_agent_goal_governance,
        [
            "# 目标治理",
            "Goal 是显式目标管理和持续推进契约",
            "对外统一归入知止者",
            "Goal 是目标层",
            "GSD 是分波计划层",
            "CAD 是原子执行子循环",
            "当前任务使用了哪些内部层",
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
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_product_to_engineering,
        [
            "goal-governance.md",
            "是否需要 Goal 组合",
            "Goal 卡、GSD Wave / Goal 映射",
        ],
    )
    and has_all(
        wise_agent_engineering_governance,
        [
            "goal-governance.md",
            "Goal ID",
            "Goal 状态",
            "Goal Ledger 更新",
            "不把 Goal 写成 Execution Grant",
        ],
    )
    and has_all(
        wise_agent_spec_template_practices,
        [
            "goal-governance.md",
            "关联 Goal",
            "Goal 成功标准",
            "Goal / AC 映射",
        ],
    )
    and has_all(
        wise_agent_code_delivery,
        [
            "goal-governance.md",
            "Goal 交付闭环",
            "Goal 追踪",
            "目标闭环",
        ],
    )
    and has_all(
        wise_agent_verification_release,
        [
            "goal-governance.md",
            "Goal 完成度判断",
            "Goal ID / 成功标准",
            "是否可以把 Goal 标记为 Verified 或 Closed",
        ],
    )
    and has_all(
        "README.md",
        [
            "生产可用能力",
            "交付推进视图",
            "做生产交付审查",
            "对应授权",
        ],
    ),
)
check(
    "wise agent keeps delivery execution control gate",
    has_reference_header(wise_agent_delivery_execution_control)
    and has_task_reading_index(wise_agent_delivery_execution_control)
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_execution_control,
        [
            "# 交付执行控制",
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
            "生产准出门禁",
            "L1-L4 工程成熟度诊断",
            "Prompt Engineering -> Context Engineering -> Harness Engineering -> Loop Engineering",
            "先定位层级，再开药方",
            "L3 未扎实时不进入 L4",
            "理解债或认知投降风险",
            "自动化心跳",
            "隔离执行",
            "Maker / Checker 解耦",
            "可复现状态",
            "观测 / 审计",
            "人工接管",
            "发布 / 回滚",
            "理解债控制",
            "Skill 是复用单位",
            "AI 编码框架分层映射",
            "Superpowers、GSD、GStack、Trellis 不是四个并列主流程",
            "方法纪律层",
            "角色链审查层",
            "仓库级记忆层",
            "不把 Loop 写成无条件自动授权",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "Loop Engineering又是啥？一文讲清企业Agent落地的四层工程进化论",
            "Prompt / Context / Harness / Loop 四层嵌套关系",
            "Agent 生产不稳分层诊断",
            "L3 先于 L4",
            "最小 L4 试点",
            "认知投降风险门禁",
            "作者字段为 `李伟山`",
            "账号字段为 `腾讯云开发者`",
            "不把 GPT-5.5、Claude、Gemini、Codex / Claude Code、`/goal`、`/loop`、automation 等工具能力写成当前会话默认事实",
            "四大AI编码框架深度解析：Superpowers、GSD、GStack、Trellis",
            "AI编程汇",
            "2026-07-03 通过 Codex in-app Browser 插件读取标题、账号、发布时间和 `#js_content` 正文",
            "Superpowers 方法纪律、GSD 上下文 / Spec / 状态、GStack 角色链审查、Trellis 仓库级记忆",
            "不默认安装 GStack / Trellis / GSD / Superpowers",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "Loop Engineering又是啥？一文讲清企业Agent落地的四层工程进化论",
            "L1-L4 工程成熟度诊断参考来源",
            "L3 优先加固",
            "理解债 / 认知投降风险",
            "不把单篇文章写成默认授权、工具能力、测试通过、CR 结论或上线审批",
        ],
    )
    and has_all(
        wise_agent_engineering_governance,
        [
            "delivery-execution-control.md",
            "Loop 是运行循环契约",
            "Loop Orchestrator",
            "状态载体",
            "反馈源",
            "验证者",
            "无进展检测",
        ],
    )
    and has_all(
        wise_agent_goal_governance,
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
        wise_agent_code_delivery,
        [
            "Agent Loop 反馈闭环",
            "Loop 是否有状态载体、反馈源、验证者、预算和停止条件",
            "生产可用 Loop 准出判断",
            "Loop 是否具备隔离执行、可复现状态、Maker / Checker 解耦、观测审计、人工接管和发布/回滚",
            "生产生效验证卡",
            "版本回读、配置回读、冒烟验证、观测确认、工单 / Goal 回写",
            "连续两轮没有新增证据",
            "Loop 稳定性",
        ],
    )
    and has_all(
        wise_agent_planning_execution_admission,
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
        wise_agent_source_map,
        [
            "【译】别再手动写 Prompt 了，去写 Loop——但 Loop 到底是什么？",
            "Loop Engineering（Agent 闭环工程）",
            "delivery-execution-control.md",
            "code-delivery.md",
            "GSD + Goal + Loop",
            "生产准出门禁",
            "Maker / Checker 解耦",
            "状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件",
            "Skill 作为复用单位",
            "不把 `/goal`、`/loop` 或 auto mode 写成无条件授权",
        ],
    ),
)
check(
    "wise agent keeps unified yinyang execution principle",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_execution_control,
        [
            "混一总纲",
            "以真实交付为体，以证据闭环为用",
            "阴定边界，阳促推进",
            "随事取最小可验证路径",
            "体不清则不动",
            "用无证则不收",
            "阴不足则停",
            "阳不足则问",
            "神用无方",
            "不把它们写成并列菜单",
        ],
    ),
)
check(
    "wise agent keeps CDD capability discovery gate",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_execution_control,
        [
            "能力发现 / 最小正确实现门禁",
            "Capability Discovery",
            "触发条件、输入、动作、边界和验收证据",
            "artifact / validator / readback / 用户确认",
            "缺口明确后才新增实现",
            "不把工具名当能力",
            "不绕过既有 QC、readback、权限边界、失败处理、测试、CR、owner 确认或 Git / 上线授权",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "CDD：先找能力，再写代码",
            "Willis x AI",
            "2026-07-04 14:46:40 Asia/Shanghai",
            "Capability-Driven Development",
            "先找已有 Skill、Tool、Workflow、脚本、自动化和验收证据",
            "不把工具名写成能力",
        ],
    ),
)
check(
    "wise agent keeps architecture entropy loop gate",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_delivery_execution_control,
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
        wise_agent_source_map,
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
            "让 AI 少写一半代码：拆解爆火的 ponytail",
            "古法程序员",
            "少写是结果、理解上下文不偷懒、benchmark 不等于项目收益",
            "最小正确实现门禁",
            "过度设计专项 CR",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "架构排熵",
            "内部路由",
            "深度思考：架构腐朽 & Loop Engineering",
        ],
    ),
)
check(
    "wise agent keeps knowledge expression and nonstandard problem gates",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_product_to_engineering,
        [
            "Round 0E：知识表达门禁",
            "Knowledge-to-Execution Card",
            "Round 0F：非标问题门禁",
            "非标问题处理包",
            "文章观点、管理要求、产品口号、工具能力、AI 草稿和用户愿望只能作为输入",
        ],
    )
    and has_all(
        wise_agent_source_map,
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
            "第一性原理先于模板",
            "不知道就问，没要求的不写",
            "验收标准、解决方案假设和待确认项",
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
            "验收优先于步骤",
            "只改被要求的范围",
            "Bug 修复先追根因",
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
    "wise agent keeps code delivery gate",
    has_reference_header(wise_agent_code_delivery)
    and has_task_reading_index(wise_agent_code_delivery)
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_code_delivery,
        [
            "# 代码交付",
            "编码阶段提速明显，但端到端交付、CR、测试、对齐或返工没有明显改善",
            "最小 Spec 强度",
            "Harness 三层闭环",
            "Orchestrator",
            "Knowledge",
            "Delivery",
            "机器验证与独立证据",
            "生成者不能自己给自己签字",
            "SDD v6 任务闭环",
            "Task Reviewer",
            "can't verify from diff",
            "final broad review",
            "只有用户或项目规则明确授权时，才可运行插件脚本或创建 `.superpowers/`",
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
        wise_agent_product_to_engineering,
        [
            "code-delivery.md",
            "AI 代码交付闭环",
            "编码提速但 CR、测试、对齐、返工或上线质量没有改善",
        ],
    )
    and has_all(
        wise_agent_engineering_governance,
        [
            "code-delivery.md",
            "Delivery Gate Agent",
            "独立验证证据",
            "知识回流位置",
            "交付指标",
        ],
    )
    and has_all(
        wise_agent_verification_release,
        [
            "code-delivery.md",
            "最终代码交付能力",
            "Spec 强度",
            "Harness 摘要",
            "CR 高频问题",
            "一次通过率、CR 轮次、缺陷密度、知识回流命中、上下文漂移、机器门禁覆盖",
            "知识沉淀、规范统一、质量底线",
            "技术债归类",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "万字长文 | Spec 驱动开发实战：半年踩坑，我们如何让 AI 编码的交付真正闭环",
            "我们落地了 SDD，为什么团队效率没有体感提升？",
            "规范驱动开发（SDD）：用 AI 写生产级代码的完整指南",
            "code-delivery.md",
            "失败回写 Spec 再重试",
            "Orchestrator / Knowledge / Delivery 三层 Harness",
            "代码质量不是洁癖：Code Review与技术债治理的落地方法",
            "Code Review 的三目标",
            "代码写完了，谁负责确认写对了，预发环境是OK吗？",
            "生产生效验证门禁",
            "版本回读、配置回读、冒烟验证、观测确认和工单回写",
            "`obra/superpowers` v6.0.3",
            "`obra/superpowers` v6.1.1",
            "Token 砍半、速度翻倍：Superpowers 6.0.3 到底升级了什么？",
            "superpowers@openai-api-curated",
            "installed, enabled",
            "不再保留或运行 `task-brief`、`review-package`、`sdd-workspace` helper",
            "不等于 Codex 市场安装标识或本机 manifest 版本",
            "不把外部 Harness 写成当前会话默认依赖或执行授权",
            "不把文章中的比例和团队经验写成通用事实或项目当前指标",
        ],
    )
)
check(
    "wise agent supports evidence-backed business expert distillation",
    has_reference_header(wise_agent_domain_expert_distillation)
    and has_task_reading_index(wise_agent_domain_expert_distillation)
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and contains(wise_agent_skill, "业务专家蒸馏与知识演进")
    and has_all(
        wise_agent_domain_expert_distillation,
        [
            "领域专家 Skill Pack",
            "cangjie-skill",
            "业务专家学习闭环",
            "会话内领域建模回流",
            "先读取已有术语与对象表",
            "不把当前代码自动认定为正确业务事实",
            "冲突证据、影响范围和待确认项",
            "owner 追认后才写入",
            "只在项目已有且授权时写入 `CONTEXT.md`",
            "同时难以逆转、缺少背景会令人困惑、且源于真实方案取舍",
            "adr-and-tradeoff.md",
            "预习定域 -> 逐篇精读 -> 横向建模 -> 三重验证 -> owner 追认 -> 结果归档",
            "学习结果知识库规划",
            "先按业务域或模块分区",
            "再在分区内按结果类型归位",
            "cross-domain",
            "逐篇学习台账",
            "证据地图",
            "术语与对象表",
            "领域知识卡",
            "流程状态与判断规则",
            "接口事件与数据",
            "待确认与压测",
            "claim / evidence / source_id / owner / domain_or_module / maturity / updated_at / target_file",
            "`maturity` 只用 D0 / D1 / D2 / D3",
            "事实 / 推断 / 待确认 / 范围外不做",
            "V1 证据交叉",
            "V2 可回答新问题",
            "V3 领域特异性",
            "owner 追认",
            "按需装载 `huaxia-practical-wisdom`",
            "不复制经典镜片",
            "不把业务专家写成自由发挥角色",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "cangjie-skill",
            "RIA-TV++",
            "V1 证据交叉",
            "V2 可回答新问题",
            "V3 领域特异性",
            "不把业务专家写成自由发挥角色",
        ],
    ),
)
check(
    "repo centralizes skill self-improvement and avoids professional skill duplication",
    has_all(
        agents_rules,
        [
            "## Skill 自我改进外循环",
            "Skills 源仓库维护门禁",
            "运行时识别、分发和回流编排",
            "专业 Skill 不复制本节",
            "内循环",
            "外循环",
            "Skill Improvement Card",
        ],
    )
    and has_all(
        wise_agent_skill,
        [
            "## 自我演进",
            "才进入 Skill 改进外循环",
            "仓库维护门禁遵循 Skills 源仓库 `AGENTS.md`",
            "运行时流程读取 `references/code-delivery.md`",
            "生成 Skill Improvement Card",
            "专业 Skill 不复制通用外循环",
            "未经授权不提交、同步或发布",
        ],
    )
    and all(
        has_none(
            path,
            [
                "## Skill 自我改进外循环",
                "Skill 自我改进外循环遵循仓库",
                "Skill 改进必须遵循仓库",
            ],
        )
        for path in professional_skill_files
    )
    and has_all(
        wise_agent_code_delivery,
        [
            "知止者运行时的知识回流与 Skill 改进编排",
            "Skills 源仓库的维护准入、隐私、授权和 Git 边界以根目录 `AGENTS.md` 为准",
            "经验归位判断",
            "Skill 自我改进外循环",
            "Knowledge Harness",
            "症状 / 根因 / 解决方案 / 预防策略 / 适用条件 / 验证证据",
            "不默认新建 `docs/solutions/`",
            "稳定上下文、项目规则、验证样例或 Skill 规则没有进入合适载体",
            "项目公共知识",
            "Skill 方法增强",
            "Skill Improvement Card",
            "目标 Skill、触发样例、错误表现、反馈证据、最小修改位置、验证方式和不得吸收项",
            "目标 Skill / 真实失败模式 / 可复用规则 / 权威落点 / 验证方式",
            "不把业务对象写进知止者",
            "只更新对应 Skill 或 reference",
            "同步更新触发 fixture / validator",
            "已回流、建议回流、待人工确认、不得回流",
            "不得把个人长期偏好、个人工作方式或私有对话历史写进本仓库或安装目录",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "一个让Codex变得越来越聪明的小方法",
            "如何为你的 Skills 构建自我改进循环",
            "有人把 5.7 万星 OpenSpec 和 24 万星 Superpowers 融合成一个工作流在 Github 开源",
            "Spec-First：每次 AI coding 的经验，都不应该消失",
            "Delta Spec",
            "Knowledge Harness",
            "像素与咖啡时光",
            "Skill 自我改进外循环",
            "经验归位",
            "内循环执行 Skill、外循环按执行记录和人工反馈审查并生成最小 Skill 改进 diff",
            "不把个人长期偏好、私有对话轨迹或用户背景写入仓库、安装目录或 Skill 改进材料",
            "不把外循环写成自动合并、自动提交、自动同步、读取私有轨迹或个人记忆机制",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "一个让Codex变得越来越聪明的小方法",
            "Skill 自我改进外循环",
            "Skill Improvement Card",
            "有人把 5.7 万星 OpenSpec 和 24 万星 Superpowers 融合成一个工作流在 Github 开源",
            "Spec-First：每次 AI coding 的经验，都不应该消失",
            "不得把个人长期偏好、私有对话轨迹、客户资料、生产数据、密钥、外部文章原文、工具宣传或 Agent 自述写入仓库",
        ],
    ),
)
check(
    "wise agent separates knowledge freshness and bounds routing fanout",
    has_all(
        agents_rules,
        [
            "## 知识变更频率分层",
            "稳定知识",
            "时效知识",
            "任务知识",
            "上下文范围分层与变更频率分层是两条正交轴",
            "维护粒度与读取粒度可以不同",
            "不设置机械文件数或行数阈值",
            "旧事实 / 旧行为",
            "新事实 / 新行为",
            "旧值清除检查",
            "新值到位检查",
            "不得静默采集用户纠错、重复提问或放弃对话",
        ],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "### 二 A、路由消歧、后置加载与加载扇出",
            "先主能力、后协同能力",
            "正向信号、负向信号、优先级和停止条件",
            "证据出现后再加载",
            "加载扇出",
            "精确到章节",
            "正例、负例或消歧 fixture",
        ],
    )
    and has_all(
        wise_agent_code_delivery,
        [
            "Knowledge Change Register",
            "旧事实 / 旧行为",
            "新事实 / 新行为",
            "权威来源",
            "影响位置",
            "旧值清除检查",
            "新值到位检查",
            "回归 fixture / validator",
            "不得静默采集用户纠错、重复提问或放弃对话",
        ],
    )
    and contains(reference_index_audit, 'ROOT / "wise-agent" / "references"')
    and has_all(
        wise_agent_source_map,
        [
            "https://mp.weixin.qq.com/s/mF3TyV_GzkBdoyYfK14fWQ",
            "面向复杂业务场景的智能分析 Skills 架构设计与演进实践",
            "钟雨洁",
            "2026-07-18",
            "稳定知识与时效知识",
            "维护粒度与读取粒度",
            "不静默采集用户反馈",
            "不吸收固定文件行数、方法数量、行业数量或压缩比例",
        ],
    ),
)
check(
    "ai-native governance keeps codebase visual understanding gate",
    has_all(
        wise_agent_engineering_governance,
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
        wise_agent_source_map,
        [
            "如何让 AI 画出高质量架构图，一个Skill搞定",
            "日积月码",
            "图形化理解 brief",
            "不安装文中提到的外部 Skill",
            "不把外部工具生成结果当作架构质量结论",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "如何让 AI 画出高质量架构图，一个Skill搞定",
            "陌生代码库图形化理解",
            "不安装文中提到的外部 Skill",
        ],
    ),
)
check(
    "wise agent keeps PRD and system design deliberation review gate",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_reference_header(wise_agent_prd_system_design_review)
    and has_task_reading_index(wise_agent_prd_system_design_review)
    and has_all(
        wise_agent_prd_system_design_review,
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
        wise_agent_product_to_engineering,
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
        wise_agent_engineering_governance,
        [
            "prd-system-design-review.md",
            "预审 Agent",
            "ACCEPT/REJECT/PENDING",
            "PRD / 系分是否已在需要时做合议预审",
        ],
    )
    and has_all(
        wise_agent_verification_release,
        [
            "prd-system-design-review.md",
            "PRD / 系分合议预审进入验证矩阵",
            "ACCEPT",
            "REJECT",
            "PENDING",
        ],
    )
    and has_all(
        wise_agent_source_map,
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
    "wise agent has realistic prompt fixtures and evaluation coverage",
    has_all(
        skill_eval_prompt_fixture,
        [
            "wise-agent-should-end-to-end-product-engineering-workflow",
            "wise-agent-should-gsd-cad-handoff",
            "wise-agent-should-prd-system-design-deliberation-review",
            "wise-agent-should-final-deliverable-document-gate",
            "wise-agent-should-planning-execution-admission-gate",
            "wise-agent-should-gsd-cad-default-authorization",
            "wise-agent-should-gsd-goal-governance",
            "wise-agent-should-delivery-execution-control",
            "wise-agent-should-map-sdlc-without-renaming-main-flow",
            "wise-agent-should-default-lightweight-lifecycle-routing",
            "wise-agent-should-backflow-confirmed-domain-term-after-grill",
            "wise-agent-should-stop-domain-writeback-on-code-conflict",
            "wise-agent-should-avoid-adr-for-reversible-wording-choice",
            "wise-agent-should-loop-task-end-accountability",
            "wise-agent-should-decision-gate-blocker-progression",
            "wise-agent-should-review-ai-coding-process",
            "wise-agent-should-code-delivery",
            "wise-agent-should-production-sdd-source-of-truth",
            "wise-agent-should-knowledge-expression-gate",
            "wise-agent-should-nonstandard-problem-mode",
            "wise-agent-should-practical-coding-loop",
            "wise-agent-should-feedback-loop-verification-cluster",
            "wise-agent-should-spec-template-practices",
            "wise-agent-should-development-standards-gate",
            "wise-agent-should-product-system-dna-gate",
            "wise-agent-should-quality-test-gate",
            "wise-agent-should-change-understanding-gate",
            "wise-agent-should-codebase-understanding-brief",
            "wise-agent-should-tool-install-admission",
            "wise-agent-should-design-code-alignment",
            "wise-agent-should-fact-boundary-check",
            "wise-agent-should-route-prd-work",
            "wise-agent-should-route-cr-work",
            "wise-agent-should-route-codegen-work",
            "wise-agent-should-route-wind-agents-init",
            "wise-agent-should-deliver-prd-from-prototype",
            "wise-agent-should-deliver-code-review",
            "wise-agent-should-read-and-fix-single-code-file",
            "wise-agent-should-deliver-structured-codegen",
            "wise-agent-should-deliver-business-architecture",
            "wise-agent-should-deliver-system-design",
            "wise-agent-should-write-tests",
            "wise-agent-should-handle-production-incident",
            "wise-agent-should-direct-lightweight-local-edit",
            "wise-agent-should-resume-from-state-contract",
            "wise-agent-should-select-control-mechanisms-by-evidence",
            "wise-agent-should-avoid-worker-for-coupled-task",
            "wise-agent-should-use-checker-without-worker",
            "wise-agent-negative-single-domain-prd",
            "wise-agent-negative-single-domain-system-design",
            "wise-agent-negative-single-domain-source-review",
            "wise-agent-negative-single-domain-codegen",
            "wise-agent-negative-single-domain-document",
            "wise-agent-negative-single-domain-philology",
            "wise-agent-negative-single-domain-java-conventions",
            "wise-agent-negative-simple-translation",
            "wise-agent-negative-simple-fact",
            "wise-agent-negative-simple-wording",
            "wise-agent-negative-simple-definition",
            "wise-agent-negative-simple-synonyms",
            "product-should-nonstandard-problem-solution",
            "senior-should-nonstandard-engineering-problem",
            "senior-should-invariant-verification-cluster",
            "wise-agent",
        ],
    )
    and has_all(
        skill_evaluator,
        [
            "\"wise-agent\"",
            "\"知止者\"",
            "\"自己判断并推进\"",
            "\"只读 CR\"",
            "\"补单元测试\"",
        ],
    ),
)
single_domain_wise_agent_positive_ids = [
    "wise-agent-should-deliver-prd-from-prototype",
    "wise-agent-should-deliver-code-review",
    "wise-agent-should-read-and-fix-single-code-file",
    "wise-agent-should-deliver-structured-codegen",
    "wise-agent-should-deliver-business-architecture",
    "wise-agent-should-deliver-system-design",
    "wise-agent-should-keep-lightweight-refund-on-generic-product-path",
    "wise-agent-should-write-tests",
    "wise-agent-should-handle-production-incident",
    "wise-agent-should-direct-lightweight-local-edit",
]
skill_eval_cases_by_id = {
    case["id"]: case for case in json.loads(read(skill_eval_prompt_fixture))["cases"]
}
check(
    "single-domain wise-agent positives require explicit invocation",
    all(
        case_id in skill_eval_cases_by_id
        and skill_eval_cases_by_id[case_id].get("should_trigger") is True
        and any(
            term in skill_eval_cases_by_id[case_id].get("query", "")
            for term in ["$wise-agent", "进入知止者", "自己判断并推进", "按需调用能力"]
        )
        for case_id in single_domain_wise_agent_positive_ids
    ),
)
check(
    "README explains wise agent interaction and load boundary",
    has_all(
        "README.md",
        [
            "## 用户使用指南",
            "仓库把知止者设计为默认交互与责任模型",
            "`$wise-agent` 是显式协同入口",
            "不表示每个任务都必须加载它",
            "单一领域且边界清楚的任务可直接加载对应专业 Skill",
            "跨专业、跨阶段、跨轮",
            "多 Skill 只为同一 Agent 补充专业上下文",
            "不产生第二人格或重复 Owner",
            "日常不需要选角色或背 Skill 名称",
            "### 1. 30 秒上手",
            "通用任务模板",
            "任务明显跨专业、跨阶段、跨轮",
            "再在前面加 `$wise-agent：`",
            "我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>",
            "常见任务可以直接这样说",
            "我有 PRD 和代码路径，只做只读 CR，不改代码",
            "自己判断并推进",
            "把这轮 CR 结论沉淀到项目约规",
            "### 2. 任务与专业能力",
            "| 你要交付 | 专业能力与路径 | 最小输入 | 边界 |",
            "产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图",
            "系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图",
            "DDL/schema/Java 类/字段表格到 Java Service 脚手架",
            "Java 项目通用编码约规，或按依赖/上下文启用 Wind/Nobe 专项",
            "复杂可编辑架构图、代码库结构转图或架构描述转图",
            "正式图形默认 SVG，PNG 仅在明确要求时导出",
            "### 3. 知止者如何工作",
            "加载 `$wise-agent` 时",
            "不是流程路由器",
            "察 -> 辨 -> 谋 -> 行 -> 验 -> 化",
            "人类责任 Owner、知止者、专业能力和独立 Checker 分开",
            "专业能力按需渐进加载",
            "只读理解视图",
            "交付推进视图",
            "验证发布视图",
            "知识回流视图",
            "决策澄清门禁",
            "复杂或模糊任务一次只问一个主 blocker",
            "Facts 先从材料、源码、测试或日志自答",
            "Decisions 才问 owner",
            "`grill-me` 是升级盘问",
            "你只需要回答接受建议、改答案、补材料或停止",
            "退出：确认 shared understanding",
            "红线、底线、不能碰、不可、禁止、必须",
            "按你建议推进",
            "自决推进",
            "询问 owner",
            "继续收敛",
            "停止交接",
            "### 3.3 知识如何回流",
            "知识回流不是把任务总结整篇复制进知识库",
            "按业务域或模块找到已有权威位置",
            "| 稳定知识 |",
            "| 时效知识 |",
            "| 任务知识 |",
            "没有权威位置或写入授权时，只给候选落点",
            "### 4. 编写文档的友好指令",
            "### 5. 边界与授权",
            "Ready / Not Ready / Human Approval Required",
            "不要先设计一套角色接力再描述任务",
            "不要让多个专业 Skill 分别向用户作最终承诺",
            "内存版业务 Service",
            "路径：[wise-agent](./wise-agent)",
            "不限于产研",
            "产品、架构、文档、考据、生成和约规不是平级角色",
            "复杂任务才使用计划、SDLC、Goal、Loop、Worker 或 Checker",
            "从 AI 原型到工程化",
            "## 安装",
            "## 验证与同步安全",
            "./scripts/validate.sh",
            "scripts/smoke-wise-agent-behavior.sh",
            "--mode self-improvement --runs 3",
            "--mode grill-me --runs 3",
            "普通使用这些能力不需要运行安装校验",
        ],
    )
    and has_none(
        "README.md",
        ["最推荐的指令只有一条", "$wise-agent：我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>"],
    ),
)
check(
    "README user guide avoids heavy default output template",
    has_none(
        "README.md",
        [
            "默认输出骨架固定为",
            "按默认输出骨架",
            "进入自主交付闭环",
            "## 完整能力索引",
            "### 提示词公式",
            "用 <Skill 名称> + <任务类型> + <输入材料> + <目标产物> + <边界/风险> + <验证要求>",
            "输出当前阶段、角色视角、能力来源、自我问询/回答、owner、交接物、Loop Contract、验证门禁、停止条件和下一步分派",
        ],
    ),
)
check(
    "README exposes friendly canonical document authoring prompts",
    has_all(
        "README.md",
        [
            "### 4. 编写文档的友好指令",
            "产品、系分、重构三类正式设计文档各有一个权威模板入口",
            "产品设计用 `product-prd-template.md`",
            "系分设计用 `system-analysis-template.md`",
            "迁移型重构用 `refactoring-design-template.md`",
            "只评审 <文档路径>，不要改文件",
            "已有正式文档默认原路径更新",
            "不因模板升级另建“新版”“最终版”或日期副本",
        ],
    ),
)
check(
    "README explains specialist capabilities under wise agent",
    has_all(
        "README.md",
        [
            "### 2. 任务与专业能力",
            "路径：[product-architecture-expert](./product-architecture-expert)",
            "产品语义",
            "业务架构规划",
            "Backlog",
            "不负责工程实现、代码 Review 和生产排障",
            "路径：[senior-software-architect](./senior-software-architect)",
            "系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图",
            "不替代产品专家定义复杂业务语义、PRD 和金融产品规则",
            "路径：[document-authoring](./document-authoring)",
            "路径：[hanzi-philology](./hanzi-philology)",
            "路径：[java-service-code-generator](./java-service-code-generator)",
            "路径：[wind-coding-conventions](./wind-coding-conventions)",
            "产品、架构、文档、考据、生成和约规不是平级角色",
            "简单任务直接完成",
            "不限于产研",
            "必须先完成安全审查并取得对应授权",
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
            "优先使用 `product-architecture-expert`",
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
    "Java authority and review guard comment readability without senior duplication",
    has_none(senior_skill, ["不得用注释替代可读性重构", "Why not"])
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
        for term in ["架构", "系统分析设计", "系分", "工程图", "代码评审", "测试/TDD", "生产变更", "接手代码库"]
    ),
)
check(
    "product and senior metadata disambiguate diagram semantics",
    all(term in frontmatter(product_skill) for term in ["产品语义图", "系统实现", "工程图"])
    and all(term in frontmatter(senior_skill) for term in ["工程图", "产品业务语义"]),
)
negative_reason_has(
    "product-negative-ambiguous-state-machine",
    ("不能仅凭“状态机”", "先澄清", "业务状态与验收", "系统实现与工程落点"),
)
negative_reason_has(
    "senior-negative-ambiguous-state-machine",
    ("不能仅凭“状态机”", "先澄清", "业务状态与验收", "系统实现与工程落点"),
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
    "product skill separates PRD review from rewrite",
    has_all(
        product_skill,
        [
            "当用户只要求评审 PRD、需求评审、评审会前 AI 预扫描、找问题或给修改建议时",
            "输出问题清单、必改项、待确认项、owner 和验收影响",
            "不要默认重写全文",
            "用户明确要求“按评审结论重写/整理最终版”时，再进入 PRD 产出工作流",
        ],
    ),
)
check(
    "product routing separates PRD review from rewrite",
    has_all(
        product_routing,
        [
            "写作、生成、完善、补全或改写 PRD",
            "用户只要求需求评审、PRD 评审会前扫描或需求评审 Skill 化",
            "不默认重写全文",
        ],
    )
    and has_none(
        product_routing,
        [
            "写作、生成、完善或评审 PRD",
            "完善 PRD、评审 PRD",
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
    "wise agent and product capability gate isolated domain words before vertical references",
    has_all(
        wise_agent_skill,
        [
            "单个领域词不等于专项证据",
            "高置信度信号",
            "不得因“退款”“账户”“订单”等孤立词展开整棵支付、金融或工程知识树",
        ],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "目标产物未要求专项细节时停在通用路径",
            "只要求为“退款申请”补通用验收种子",
            "只装载产品通用路径",
            "不读取支付专项 reference",
        ],
    )
    and has_all(
        product_skill,
        [
            "孤立领域词不触发专项树",
            "不得因“退款”“账户”“订单”等单词展开整棵垂直知识树",
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
        for term in ["复杂业务需求", "原型或页面材料", "PRD", "产品架构", "业务架构规划", "产品语义图", "支付资金产品", "外卡收单", "Mastercard", "系统实现", "代码评审"]
    ),
)
check(
    "product openai yaml mentions visual output",
    has_all(product_agent, ["原型", "页面截图", "默认输出 SVG", "待确认项"]),
)
check(
    "product openai yaml mentions acquiring specialty",
    has_all(product_agent, ["支付资金", "外卡收单"]),
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
            "被 `wise-agent` 分派时，先消费 Engineering Handoff Card、授权策略和写入范围",
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
    "codegen hands convention checks to wind and source review to senior",
    has_all(codegen_skill, ["`wind-coding-conventions`", "通用 Java 约规", "Wind/Nobe 专项", "源码级 CR"])
    and has_all(codegen_rules, ["`wind-coding-conventions`", "通用 Java 约规", "Wind/Nobe 专项", "源码级 CR"])
    and has_none(codegen_skill, ["`资深架构师` 的代码约规"])
    and has_none(codegen_rules, ["`资深架构师` 编码约规"]),
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
            wind_skill_architecture,
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
            wind_skill_java,
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
            "does not execute an Agent or grade domain truth",
            "ROOT.glob(\"*/SKILL.md\")",
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
        repo_source_map,
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
            "日常不需要选角色或背 Skill 名称",
            "### 1. 30 秒上手",
            "我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>",
            "自己判断并推进",
            "### 2. 任务与专业能力",
            "| 你要交付 | 专业能力与路径 | 最小输入 | 边界 |",
            "产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图",
            "系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图",
            "DDL/schema/Java 类/字段表格到 Java Service 脚手架",
            "Java 项目通用编码约规，或按依赖/上下文启用 Wind/Nobe 专项",
            "复杂可编辑架构图、代码库结构转图或架构描述转图",
            "PNG 仅在明确要求时导出",
            "### 3. 知止者如何工作",
            "不是流程路由器",
            "察 -> 辨 -> 谋 -> 行 -> 验 -> 化",
            "专业能力按需渐进加载",
            "只读理解视图",
            "交付推进视图",
            "验证发布视图",
            "生产交付审查",
            "知识回流视图",
            "决策澄清门禁",
            "自决推进",
            "询问 owner",
            "继续收敛",
            "停止交接",
            "常用短句",
            "进入知止者",
            "进入只读理解视图",
            "默认不写文件、不联网、不安装",
            "做生产交付审查",
            "做质量门禁",
            "做源码质量评审",
            "不要先设计一套角色接力再描述任务",
            "不要让多个专业 Skill 分别向用户作最终承诺",
            "进入知识回流视图",
            "初始化/更新项目 AGENTS.md",
            "### 5. 边界与授权",
            "直接生成生产代码",
            "不要把工具、模板、目标、计划或授权机制名当主流程",
            "内存版业务 Service",
            "路径：[wise-agent](./wise-agent)",
            "路径：[senior-software-architect](./senior-software-architect)",
            "路径：[product-architecture-expert](./product-architecture-expert)",
            "路径：[java-service-code-generator](./java-service-code-generator)",
            "## 安装",
            "sync-skills.sh --dry-run all",
            "./scripts/validate.sh",
            "从 AI 原型到工程化",
            "常见组合",
            "从普通图到复杂图",
            "## 维护者与高级扩展",
        ],
    ),
)
check(
    "repo source map records Superpowers skills library source",
    has_all(
        repo_source_map,
        [
            "obra/superpowers",
            "外部方法能力来源",
            "用于澄清、计划、TDD、评审、调试和完成前验证",
            "2026-06-07",
            "6fd4507659784c351abbd2bc264c7162cfd386dc",
            "ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3",
            "MIT",
            "superpowers@openai-api-curated",
            "installed, enabled",
            "11c74d6b",
            "manifest 版本为 `5.1.3`",
            "superpowers-skill-library.md",
            "退役 `wise-agent/references/external-superpowers/` 和本地 helper",
            "不再复制上游 Skill",
            "已安装不等于执行授权",
            "v6.1.1",
        ],
    ),
)
check(
    "repo source map records intent to production loop engineering source",
    has_all(
        repo_source_map,
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
    "repo source map records huaxia wisdom source boundary",
    has_all(
        repo_source_map,
        [
            "aiami/huaxia-wisdom",
            "项目自有 `huaxia-practical-wisdom`",
            "现实决策校准",
            "2026-06-16",
            "eef49d54e6266b1afc568ef591a6a2d4abd5ad8e",
            "不复制原文、示例、固定输出、宽泛自动触发、古风人格或“全家桶”结构",
            "不把传统智慧框架写成事实证据、医学建议、占卜命理、项目制度、Execution Grant、测试通过、CR 结论、Git 授权或上线审批",
        ],
    ),
)
check(
    "repo source map records Anthropic internal skills practice source",
    has_all(
        repo_source_map,
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
    "repo source map records official Anthropic skills methodology and Perplexity pending boundary",
    has_all(
        repo_source_map,
        [
            "Lessons from building Claude Code: How we use skills",
            "https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills",
            "Skill 是 instructions / scripts / resources 文件夹",
            "`SKILL.md` 做导航",
            "gotchas 优先",
            "重复能力脚本化",
            "Skill 类型分组",
            "description 服务发现",
            "真实使用检验",
            "Perplexity Research 文章",
            "2026-07-06 普通抓取、HEAD 请求和 Playwright 访问均超时",
            "不把该链接作为已吸收来源",
        ],
    ),
)
check(
    "repo source map records AI product postmortem source boundary",
    has_all(
        repo_source_map,
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
    "repo source map records AI full-stack workflow article boundary",
    has_all(
        repo_source_map,
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
    "repo source map records fireworks tech graph reference source",
    has_all(
        repo_source_map,
        [
            "yizhiyanhua-ai/fireworks-tech-graph",
            "图形化 Skill 产品化、风格系统、语义形状/箭头、模板化、fixture 化、SVG 导出和渲染校验思路",
            "PNG/PDF/截图等派生格式只在使用者明确提出时处理",
            "供应链安全审查",
        ],
    ),
)
check(
    "repo source map records Google engineering practices reference source",
    has_all(
        repo_source_map,
        [
            "google/eng-practices",
            "代码评审标准、评论分级、变更颗粒度、作者/评审者协作和持续改善代码健康",
            "不把它扩展为完整架构设计方法论",
            "CC-BY 3.0 归因要求",
        ],
    ),
)
check(
    "repo source map records Ivy skills reference source",
    has_all(
        repo_source_map,
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
    "repo source map records cg0x frame analysis reference source",
    has_all(
        repo_source_map,
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
    "repo source map records SkillX reference source",
    has_all(
        repo_source_map,
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
    "repo source map records architecture principles WeChat source",
    has_all(
        repo_source_map,
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
    "repo source map records architect thinking WeChat source",
    has_all(
        repo_source_map,
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
    "repo source map records communication complexity WeChat source",
    has_all(
        repo_source_map,
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
    "repo source map records software design philosophy source",
    has_all(
        repo_source_map,
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
    "repo source map records AI diagram and UX mapping sources",
    has_all(
        repo_source_map,
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
    "repo source map records requirements analysis and design source",
    has_all(
        repo_source_map,
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
    "repo source map records AI-shaped readiness advisor boundary",
    has_all(
        repo_source_map,
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
    "repo source map records product manager methodology book boundary",
    has_all(
        repo_source_map,
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
    "repo source map records business-driven architecture reference sources",
    has_all(
        repo_source_map,
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
    "validate script runs grill-me install validator self-test",
    has_all(
        "scripts/validate.sh",
        [
            "python3 -m py_compile scripts/validate-grill-me-install.py",
            "python3 scripts/validate-grill-me-install.py --self-test",
            'if [[ "${VALIDATE_GRILL_ME_INSTALL:-}" == "1" ]]; then',
            "  python3 scripts/validate-grill-me-install.py",
        ],
    ),
)
check(
    "validate script runs Superpowers install validator self-test",
    has_all(
        "scripts/validate.sh",
        [
            "bash -n scripts/validate-superpowers-install.sh",
            "scripts/validate-superpowers-install.sh --self-test",
            'if [[ "${VALIDATE_SUPERPOWERS_INSTALL:-}" == "1" ]]; then',
            "  scripts/validate-superpowers-install.sh",
        ],
    ),
)
check(
    "Superpowers install validator checks official plugin and retired snapshot",
    has_all(
        "scripts/validate-superpowers-install.sh",
        [
            "superpowers@openai-api-curated",
            "installed, enabled",
            "REQUIRED_SKILLS",
            ".codex-plugin/plugin.json",
            "wise-agent/references/external-superpowers",
            "missing required Skill",
            "accepted the retired snapshot",
        ],
    ),
)
check(
    "wise-agent behavior smoke uses holdout prompts and negative orchestration guards",
    has_all(
        "scripts/smoke-wise-agent-behavior.sh",
        [
            "assert_none",
            "assert_no_orchestration",
            "assert_superpowers_product",
            "assert_superpowers_debugging",
            "assert_superpowers_git",
            "assert_lightweight",
            "assert_simple_wording",
            "assert_state_resume",
            "assert_skill_improvement",
            "assert_grill_evidence_closed",
            "assert_grill_evidence_conflict",
            "all|product|engineering|superpowers|governance|self-improvement|grill-me",
            "scripts/validate-superpowers-install.sh",
            "systematic-debugging",
            "test-driven-development",
            "verification-before-completion",
            "会员按等级获得权益",
            "请给出最重要的问题、判断依据、需要补的验证",
            "当前先调用哪种探索方法、何时升级强盘问",
            "请选择从定位、修复到完成声明的方法链",
            "未授权任何 Git 或隔离工作区动作",
            "不允许 commit，也不允许 push",
            "authorization-contradictory response",
            "只返回改写后的句子",
            "orchestration-heavy response",
            "不得复活",
            "不得脑补",
            "state-resume-variant-3",
            "不得执行 B，也不得假定 C",
            "Skill Improvement Card",
            "单一专业源码 CR",
            "讨论过订单优惠券类名",
            "Owner 连续三次纠正",
            "skill-improvement-coordinated-auth.txt",
            "不修改、提交、同步或发布",
            "bad-skill-improvement-noise.txt",
            "bad-skill-improvement-authorization.txt",
            "accepted business noise",
            "accepted unauthorized delivery",
            "grill-me/fixtures/behavior-evidence",
            "fact-confirmed",
            "decision-reused",
            "ask-owner",
            "证据冲突",
        ],
    )
    and has_none(
        "scripts/smoke-wise-agent-behavior.sh",
        [
            "按事实、推断、待确认、验收四项答复",
            "按严重级别、证据、测试、残余风险四项答复",
            "明确写出“不生成工程实现计划”",
            "用“Superpowers 已安装不等于”开头",
            "已确认的可复用方向是单一专业任务直接加载对应 Skill",
            "只输出 Skill Improvement Card，必须包含",
        ],
    ),
)
check(
    "wise-agent keeps lightweight execution and resumable state guards",
    has_all(
        wise_agent_skill,
        [
            "不展开完整 SDLC",
            "不装载 Superpowers",
            "scripts/check_state_contract.py",
        ],
    )
    and has_all(
        wise_agent_cognition_model,
        [
            "状态契约",
            "被排除方案不得复活",
            "待确认项不得脑补",
        ],
    )
    and has_all(
        "scripts/validate.sh",
        [
            "python3 wise-agent/scripts/check_state_contract.py --self-test",
            "python3 -m py_compile wise-agent/scripts/check_state_contract.py",
        ],
    )
    and has_all(
        "wise-agent/scripts/check_state_contract.py",
        [
            "Input: one JSON file explicitly supplied by the caller",
            "Writes: none. Network: none",
            "execution_basis must contain confirmed decisions only",
            "no_progress_limit must not exceed max_iterations",
            "--self-test",
        ],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "能力选择与责任路由的唯一权威来源",
        ],
    )
    and has_all(
        wise_agent_delivery_execution_control,
        [
            "Loop、跨轮状态、执行前对账、预算、停止和恢复规则的唯一权威来源",
        ],
    )
    and has_all(
        wise_agent_verification_release,
        [
            "验证矩阵、独立 Checker、CR 准出、发布证据和复盘规则的唯一权威来源",
        ],
    ),
)
check(
    "wise-agent documents one control mechanism trigger path",
    has_all(
        wise_agent_skill,
        [
            "## 控制强度路由",
            "默认直接工作",
            "SDLC 是阶段地图",
            "Goal 是跨轮目标契约",
            "Loop 是反复执行契约",
            "Worker 是执行拓扑",
            "Checker 是独立验证机制",
            "Worker 与 Checker 不是顺序阶段",
        ],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "Worker 和 Checker 是两条正交判断",
            "可以只用 Checker 而不派 Worker",
        ],
    )
    and has_all(
        "README.md",
        [
            "### 3.1 什么时候启用 SDLC、Goal、Loop、Worker、Checker",
            "按完整 SDLC 覆盖",
            "建立 Goal 并持续推进",
            "允许进入 Loop",
            "可并行时再派 Worker",
            "增加独立 Checker",
        ],
    )
    and has_all(
        wise_agent_agent,
        [
            "默认直接完成",
            "SDLC、Goal、Loop、Worker 或 Checker",
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
            "不把成长型思维、复盘思维或数据思维泛化为用户画像、个人长期偏好或 Skill 自我改进证据",
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
    "senior source maps record Clean Architecture dependency rule source",
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
        repo_source_map,
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
    "senior source maps record DDD principles architecture tradeoff article group",
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
        repo_source_map,
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
            "Clean Architecture 的落点是依赖规则，不是机械四层模板",
            "层数可变，依赖方向不可逆",
            "核心业务规则与用例定义稳定契约和端口",
            "外层实现数据库、Web、消息、缓存与第三方适配",
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
            "## 通信复杂度视角",
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
    "senior architecture keeps split merge collaboration lens",
    has_all(
        senior_skill,
        [
            "专业分工和协作关系",
            "拆分让职责单纯",
            "合并让稳定能力复用",
            "不能替代功能归类、边界划分、颗粒度和长期交付成本判断",
        ],
    )
    and has_all(
        "senior-software-architect/references/architecture.md",
        [
            "架构真功夫先体现在专业分工与协作关系",
            "### 5.3.3 拆分与合并的 V 字判断",
            "向下按角色、职责、用例和变化点拆到模块单纯、实现清楚",
            "向上把相似职责和稳定能力合并成可复用元素",
            "只拆不合会碎片化，只合不拆会臃肿化",
            "稳定元素和变化关系",
            "微服务、SOA、EDA、中台只是承载方式",
            "长期交付成本是否保持稳定",
            "组件复杂度是否明显上升",
            "只拆不合碎片化",
            "只合不拆臃肿化",
            "框架替代边界思考",
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
    "senior source maps record GSD workflow boundary",
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
        repo_source_map,
        [
            "GSD工作流-适合中大型项目的精准框架",
            "中大型 AI 编码流程治理、上下文衰减、阶段状态、多 Agent 编排、Wave 依赖、原子可追溯和 Git 版本化意识",
            "不复制 GSD 命令体系、文件模板、XML 示例、动图、截图、工具宣传语或作者表达",
            "不把自动提交视为默认授权",
        ],
    ),
)
check(
    "senior source maps record Codex runtime collaboration boundary",
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
        repo_source_map,
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
    "senior source maps record AI Native architect boundary",
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
        repo_source_map,
        [
            "放下代码：AI Native是通往架构师的快车道",
            "AI Native 架构师角色升级、hardened 标准、Agent 工作流设计、系统判断和技术战略职责",
            "不复制原文、引用案例、播客转述、作者表达或岗位评价",
        ],
    ),
)
check(
    "senior source maps record AI old-system postmortem boundary",
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
        repo_source_map,
        [
            "阿里内网万言离职书〈置身钉内〉原文，已刷屏",
            "公开转述/OCR 复盘参考来源",
            "AI 进入旧系统的 context 架构、权限与权力边界、技术债、多端一致性、成本稳定性和灰度止损门禁",
            "不把它写成钉钉/ONE 官方事实、行业结论、当前工具能力或 Execution Grant",
        ],
    ),
)
check(
    "senior source maps record AI full-stack workflow boundary",
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
        repo_source_map,
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
            "每个规则组必须能说明原因、适用范围、反例或示例和验证方式",
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
            "是否已经先复用现有代码、标准库、平台原生能力和已安装依赖",
            "可删除抽象、无主配置、单实现接口或无证扩展点",
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
            "AC-xxx",
            "QA-xxx",
            "可代码化",
            "可观测化",
            "可评审化",
            "第一批失败反馈候选",
            "系统分析模板中的追踪矩阵和验证章节",
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
            "任何轨迹学习、个人长期偏好、业务背景或用户协作习惯不得自动沉淀",
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
            "AI Native 产品到工程的端到端链路由 `wise-agent` 维护",
            "AI Native 交接结论",
            "OpenSpec / context ledger / verification matrix",
            "GSD Stage / Wave / Atomic Task",
            "CAD 候选 / Execution Grant 缺口",
            "产品上下文包回答“这个产品候选是否值得工程化、工程化必须保留哪些业务事实”",
            "知止者持续持有端到端目标与状态",
            "按需装载产品、工程和验证能力",
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
            "`wise-agent/references/planning-execution-admission.md` 或产品侧交接结论",
            "不得把业务 MVP、PRD、产品上下文包或 GSD Roadmap 直接当授权",
        ],
    )
    and has_all(
        senior_routing,
        [
            "PRD/产品方案/AI Native 产品上下文到系统设计 / 业务驱动架构",
            "AI Native 端到端产品到研发流程先由 `wise-agent` 编排",
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
            "模板占位符统一使用 `〈...〉`",
            "正式文档不得保留未替换占位符",
            "## 文档标识与文件命名",
            "`〈主题〉-系分设计.md`",
            "消费 Product Context Card 或产品文档时必须复用其规范主题",
            "将冲突列为待确认并询问 owner",
            "只有用户明确授权项目约规治理时才修改",
            "更新既有文档默认保持原路径",
            "只有用户明确进入命名迁移任务时才改名",
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
            "数据库约规来源",
            "字段类型与精度",
            "变更类型",
            "业务唯一性",
            "不得为了通过 DDL 虚构业务默认值",
            "命中 Wind/Nobe 专项的项目将以下字段并入字段清单",
            "`id bigint(20)`、`gmt_create datetime`、`gmt_modified datetime` 为强制",
            "默认值、分阶段回填或暂时允许为空",
            "查询/排序场景",
            "数据校验与回滚",
            "## 5. 状态、流程与专项设计模板",
            "### 4.5 运行时场景与流程/时序设计",
            "### 4.5A 状态与工程规则",
            "第一批失败测试",
            "### 4.11 规则落地表",
            "## 6. 非功能、实施验证与交接模板",
            "## 六、实施、验证与 Engineering Handoff",
            "# 〈规范主题〉系统分析设计",
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
    "design documents bridge semantics rules engineering and evidence",
    has_all(
        product_prd_template,
        [
            "核心名相",
            "场景与流程",
            "状态与业务规则",
            "Product Context Card",
        ],
    )
    and has_all(
        system_analysis_template,
        [
            "运行时场景",
            "状态与工程规则",
            "规则落地表",
            "第一批失败测试",
            "Engineering Handoff",
        ],
    )
    and has_all(
        wise_agent_product_to_engineering,
        [
            "名 -> 事 ->（图）-> 法 -> 器 -> 验",
            "规则是产品事实与工程实现之间的承接点",
            "规则落地表",
            "局部、行为保持且可测试的重构不创建正式重构设计文档",
        ],
    ),
)
check(
    "design flow uses diagrams as an optional modeling gate",
    has_all(
        wise_agent_product_to_engineering,
        [
            "名 -> 事 ->（图）-> 法 -> 器 -> 验",
            "图是按需建模门禁",
            "不创建独立图形阶段文档",
            "轻量任务可明确不需要单独画图",
        ],
    )
    and has_all(
        product_prd_template,
        [
            "名 -> 事 ->（图）-> 法 -> 器 -> 验",
            "最小关键图",
            "图不是新的产品事实源",
        ],
    )
    and has_all(
        system_analysis_template,
        [
            "名 -> 事 ->（图）-> 法 -> 器 -> 验",
            "设计视图清单",
            "无需单独画图",
            "图不能替代规则落地表或验证证据",
        ],
    ),
)
check(
    "design templates use an optional reference and evidence index",
    has_all(
        product_prd_template,
        ["参考资料与证据索引（按需）", "链接或路径", "引用标识为可选"],
    )
    and has_all(
        system_analysis_template,
        ["## 七、参考资料与证据索引", "链接或路径", "引用标识为可选"],
    )
    and has_all(
        refactoring_design_template,
        ["## 八、参考资料与证据索引（按需）", "链接或路径", "引用标识为可选"],
    ),
)
check(
    "standalone refactoring design is gated and verifiable",
    (ROOT / refactoring_design_template).exists()
    and has_reference_header(refactoring_design_template)
    and has_task_reading_index(refactoring_design_template)
    and has_all(
        refactoring_design_template,
        [
            "行为不变量",
            "模板占位符统一使用 `〈...〉`",
            "正式文档不得保留未替换占位符",
            "MIG 切片",
            "双写",
            "回填",
            "灰度切流",
            "特征测试",
            "契约测试",
            "旧能力下线条件",
            "回滚",
        ],
    )
    and has_all(
        senior_skill,
        [
            "`references/refactoring-design-template.md`",
            "局部、行为保持且可测试的重构不创建独立设计文档",
        ],
    )
    and contains(architecture_deliverable_checker, '"refactoring-design"'),
)
check(
    "AI Native spec templates keep final specs separate from process assets",
    has_all(
        wise_agent_spec_template_practices,
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
    "architecture health scan keeps scope evidence and output bounded",
    has_all(
        senior_routing,
        [
            "最近改动 / diff、指定模块、全仓或仅架构层",
            "默认快速体检只返回 3-5 个最高价值候选",
            "用户明确要求深度扫描才扩展",
        ],
    )
    and has_all(
        review,
        [
            "| 架构坏味扫描 | `架构健康扫描契约`",
            "## 架构健康扫描契约",
            "候选信号",
            "确认问题",
            "项目已有静态分析、测试、查询日志、profiler 或依赖图",
            "N+1 / 循环内 I/O",
            "循环内重复线性扫描",
            "循环内排序",
            "错误数据结构",
            "渲染路径重复计算",
            "默认不生成健康分数、坏味数量排行榜或 3-12 个月路线图",
            "扫描结果不得自动触发重构",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "https://mp.weixin.qq.com/s/q7aKFiBeldJcjEhZ7v2Smg",
            "寻找你代码中的臭味：一个让 AI 帮你嗅出架构腐化的开源 Skill",
            "smallnest/goal-workflow",
            "2026-07-18",
            "不吸收固定行数、方法数、参数数阈值",
            "不默认启动多 Agent",
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
            "项目已依赖 JSpecify 时，内部 Java 契约使用 `org.jspecify.annotations.Nullable`、`NonNull`、`NullMarked`",
            "已由空值注解标为非空的参数、返回值和字段，不再额外添加无业务语义的重复空判断",
        ],
    ),
)
check(
    "review consumes Java rules without copying nullability details",
    has_all(review, ["## 规则结果消费", "规则 Skill 只提供适用层级和偏差", "规则发现不得直接决定严重级别"])
    and has_none(review, ["org.jspecify.annotations", "JSpecify"]),
)
check(
    "Java common utility reuse rule is encoded in coding standards",
    has_all(
        coding,
        [
            "优先使用 JDK 标准库",
            "`String.isBlank()`",
            "`Collection.isEmpty()`",
            "项目已依赖 Spring Framework 或 Apache Commons 时",
            "不得仅为使用这些工具新增依赖",
        ],
    )
    and has_none(
        coding,
        [
            "不得手写 `hasText`、`isBlank`、`isEmpty` 等同义工具",
            "优先使用 Spring Framework 或 Apache Commons 已提供的成熟工具",
        ],
    ),
)
check(
    "review does not copy Java utility rules",
    has_none(review, ["`hasText`", "`isBlank`", "`isEmpty`"])
    and has_all(review, ["项目本地规范和 `wind-coding-conventions` 的通用 Java 层"]),
)
check(
    "Java coding style stays in the rule authority",
    has_none(senior_skill, ["编码风格以项目为准", "不得按个人偏好或通用模板自行发挥"])
    and has_all(
        coding,
        [
            "项目统一编码规范优先",
            "局部风格服从项目已有代码、自动化检查和团队约规",
            "编码前先查项目统一编码规范、格式化配置、lint/静态检查和邻近模块既有代码",
            "不得自创一套写法",
        ],
    ),
)
check(
    "Java reserved identifiers are banned from coding names",
    has_all(
        coding,
        [
            "Java 标识符不得使用 Java 关键字、保留字或受限标识符",
            "`record`",
            "`var`",
            "`yield`",
            "字段、局部变量、方法参数、模型属性",
            "@Column",
            "@JsonProperty",
        ],
    )
    and has_all(
        codegen_skill,
        [
            "Java 关键字 / 保留字 / 受限标识符命名",
            "命名净化",
        ],
    )
    and has_all(
        codegen_rules,
        [
            "Java 关键字、保留字或受限标识符必须重命名",
            "字段表格显式提供的 Java 属性名同样必须净化",
            "`record -> recordValue`",
            "`var -> varValue`",
            "`yield -> yieldValue`",
        ],
    ),
)
check(
    "Java service split rule stays in the authority and review",
    has_none(senior_skill, ["接口和服务拆分必须有真实业务职责", "只透传调用"])
    and has_all(
        coding,
        [
            "接口、Service、ApplicationService、Facade、Adapter 的拆分必须承载真实业务职责",
            "用例编排、事务边界、权限/审计、状态转换、跨资源协调",
            "不得新增只透传调用、只改名转发、一行包装或似是而非的抽象",
            "没有新增业务职责时，优先直接复用现有服务或保持局部实现",
        ],
    )
    and has_all(
        review,
        [
            "服务拆分职责检查",
            "新增接口、Service、ApplicationService、Facade 或 Adapter 是否承载真实业务职责",
            "透传式应用服务",
            "用例编排、事务边界、权限/审计、状态转换、跨资源协调或对外契约隔离",
        ],
    ),
)
check(
    "Java pass-through rule stays in the authority and review",
    has_none(senior_skill, ["不得保留无业务语义的单行透传方法", "原样转调、原样传参"])
    and has_all(
        coding,
        [
            "不得保留无业务语义的单行透传方法",
            "公有或私有方法如果只是原样转调、原样传参、改名包装或返回下游结果",
            "单行方法只有在承载领域语言、兼容 API、框架回调、权限边界、异常语义、埋点审计或可替换策略时才有保留价值",
        ],
    )
    and has_all(
        review,
        [
            "直通包装",
            "单行透传方法无论公有或私有，都应优先删除并内联",
            "业务语义、边界保护、错误聚合、观测或测试隔离",
        ],
    ),
)
check(
    "Java DTO field types preserve contract semantics",
    has_all(
        coding,
        [
            "primitive 或包装类型必须按契约语义选择",
            "缺省与零值",
            "并发 Atomic 类型不得进入 DTO、VO、Request、Response、Query、Command、Event",
        ],
    ),
)
check(
    "review delegates Java DTO type details to rule authority",
    has_all(review, ["契约完整性", "规则结果消费", "规则发现不得直接决定严重级别"])
    and has_none(review, ["primitive 或包装类型", "并发 Atomic 类型"]),
)

check(
    "senior core keeps Wind implementation details behind opt in",
    has_none(
        senior_skill,
        [
            "查询禁止 `LambdaQueryWrapper`",
            "使用 MyBatis Flex `XxxRefs`",
            "写库默认使用 selective 方法",
        ],
    )
    and has_all(
        senior_skill,
        [
            "Java 设计、源码级 CR、TDD、Bug 修复和验证统一读取",
            "只有存在 Wind/Nobe 高置信度信号时才叠加专项",
            "只消费规则结论，不复制 Java/Wind 约规正文",
        ],
    ),
)
check(
    "senior keeps concise cross-language source decision red lines",
    has_all(
        senior_skill,
        [
            "跨语言、始终生效",
            "项目规则优先",
            "失败与敏感信息不可丢失",
            "公共契约和边界不可静默破坏",
            "业务职责不得错层",
            "不得引入无主复杂度",
            "以风险和证据裁决",
        ],
    )
    and has_none(
        senior_skill,
        [
            "`System.out.println`",
            "`new BigDecimal(double)`",
            "`InMemoryXxxService`",
            "`Supplier`",
        ],
    ),
)
check(
    "clean code treats parameter count as a review signal",
    has_all(
        "senior-software-architect/references/clean-code.md",
        [
            "参数过多是职责或契约可读性的 Review 信号",
            "保持显式参数或引入稳定业务类型",
            "不为降低数量制造一次性参数对象",
        ],
    )
    and has_none(
        "senior-software-architect/references/clean-code.md",
        ["参数过多时优先抽取参数对象"],
    ),
)

check(
    "Java rule consumers do not revive a mechanical five parameter gate",
    all(
        has_none(
            path,
            [
                "超过 5 个公有参数",
                "公有方法参数不得超过 5 个",
                "公有方法超过 5 个参数必须先和用户确认",
                "公有方法可能超过 5 个参数",
            ],
        )
        for path in [
            codegen_skill,
            "java-service-code-generator/references/code-generation-rules.md",
            "java-service-code-generator/references/nobe-patterns.md",
            "senior-software-architect/references/ai-assisted-engineering.md",
            "senior-software-architect/references/cad-mode.md",
        ]
    )
    and has_all(
        "java-service-code-generator/references/code-generation-rules.md",
        [
            "参数数量只是职责或契约可读性的 Review 信号",
            "不为降低参数数量制造一次性参数对象",
        ],
    ),
)

check(
    "system design consumes contextual required field migration policy",
    all(
        has_all(
            path,
            [
                "新增必填字段必须给兼容迁移方案",
                "默认值、分阶段回填或暂时允许为空",
                "不得为了通过 DDL 虚构业务默认值",
            ],
        )
        and has_none(
            path,
            [
                "新增字段如果为必填，必须有默认值；否则字段必须可空",
                "新增字段如果为必填，必须有默认值；没有真实业务默认值时字段必须可空",
            ],
        )
        for path in [
            "senior-software-architect/references/system-analysis-design.md",
            "senior-software-architect/references/system-analysis-template.md",
        ]
    ),
)

check(
    "general coding rules treat policy thresholds as contextual",
    has_all(
        coding,
        [
            "公有方法参数超过 5 个是 Review 信号，不是机械门禁",
            "数据库外键、审计字段和必填字段默认值属于项目数据治理决策",
            "不得作为所有 Java 项目的通用强制规则",
        ],
    ),
)
check(
    "Java production implementation rule stays in the authority and execution reference",
    has_none(senior_skill, ["业务代码不得用内存版 Service 冒充生产实现", "`InMemoryXxxService`"])
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
    "product expert exposes product judgment action chain",
    has_reference_header(product_judgment_action_chain)
    and has_task_reading_index(product_judgment_action_chain)
    and has_all(
        product_skill,
        [
            "产品判断要动作化",
            "product-judgment-action-chain.md",
            "产品判断动作链",
            "pm-skills",
        ],
    )
    and has_all(
        product_routing,
        [
            "产品判断动作链 / pm-skills 工作流参考",
            "product-judgment-action-chain.md",
            "不安装或照搬外部 `pm-skills`",
        ],
    )
    and has_all(
        product_judgment_action_chain,
        [
            "产品判断动作链卡",
            "已知事实 / 证据",
            "判断动作",
            "取舍结论",
            "不做项",
            "下一产物",
            "owner",
            "验收 / 停止条件",
            "知止者前置门禁",
            "不安装 `phuryn/pm-skills`",
        ],
    )
    and has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_product_to_engineering,
        [
            "产品判断 Loop 准入卡",
            "有材料但无判断",
            "有判断但无取舍",
            "有取舍但无验收种子",
            "只有证据、取舍、owner、验收和停止条件同时具备",
        ],
    )
    and has_all(
        product_source_map,
        [
            "产品判断动作链",
            "pm-skills：让产品判断成流程",
            "https://mp.weixin.qq.com/s/LR6GB8m9lUSfJGZxUweg-g",
            "phuryn/pm-skills",
            "不安装该仓库",
            "不得让 AI 替产品 owner 做路线图取舍",
        ],
    )
    and has_all(
        wise_agent_source_map,
        [
            "产品判断 Loop 准入",
            "pm-skills：让产品判断成流程",
            "phuryn/pm-skills",
            "不得让 AI Native 替产品 owner 做路线图取舍",
        ],
    )
    and has_all(
        "README.md",
        [
            "产品判断动作链",
            "pm-skills",
            "知止者装载产品判断动作链",
            "形成产品上下文包并继续持有后续目标、验证和停止条件",
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
            "业务架构规划与项目组合",
            "官方规则与监管",
        ],
    ),
)
check(
    "product expert routes business architecture planning",
    has_all(
        product_skill,
        [
            "业务架构规划",
            "业务 IT 对齐",
            "战略落项目",
            "项目组合治理",
            "能力-项目-系统映射",
            "business-architecture-planning.md",
            "按业务域或模块分区的知识库回流计划",
            "不替代组织设计、系统架构、Execution Grant 或上线审批",
        ],
    )
    and has_all(
        product_agent,
        [
            "业务架构规划",
            "能力地图",
        ],
    )
    and has_all(
        product_routing,
        [
            "业务架构规划",
            "业务 IT 对齐",
            "战略落项目",
            "项目组合治理",
            "投资取舍",
            "重复建设识别",
            "能力-项目-系统映射",
            "business-architecture-planning.md",
            "复杂图形化表达加读 `diagram-output.md`",
            "知识库回流计划",
            "不把业务架构降级为组织架构图、系统清单、图形美观或 Execution Grant",
        ],
    )
    and has_reference_header(product_business_architecture)
    and has_task_reading_index(product_business_architecture)
    and has_all(
        product_business_architecture,
        [
            "# 业务架构规划",
            "业务架构准入卡",
            "业务能力地图",
            "价值流 / 关键业务流程",
            "核心对象与规则卡",
            "能力-项目-系统映射",
            "差距 / 依赖 / 优先级矩阵",
            "项目组合 / 路线图",
            "## 5A. 图形化辅助路由",
            "diagram-output.md",
            "战略到能力：业务能力地图",
            "端到端价值实现：价值流 / 跨角色流程图",
            "能力落地现状：能力-项目-系统-数据映射图",
            "投资取舍：差距 / 依赖 / 路线图",
            "工程交接：产品到系统上下文图",
            "高风险对象：对象生命周期 / 状态机 / 规则决策图",
            "正式图形化交付默认只生成 SVG",
            "图不能替代业务确认、产品判断、工程设计、Execution Grant 或上线审批",
            "按业务域或模块分区保存",
            "知识库规划卡",
            "Product Context Card",
            "这些交接卡都不是 Execution Grant、测试通过、CR 结论、上线审批或 Git 授权",
        ],
    ),
)
check(
    "AI Native routes business architecture planning to product expert",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_product_to_engineering,
        [
            "业务架构规划",
            "业务能力地图",
            "战略到项目组合",
            "项目组合治理",
            "能力-项目-系统映射",
            "business-architecture-planning.md",
            "知止者只做交接成熟度、owner、验证与停止条件",
            "不把能力地图、项目组合或知识库回流计划当 Execution Grant",
        ],
    ),
)
check(
    "product source maps record product brainstorming boundary",
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
        repo_source_map,
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
        repo_source_map,
        [
            "从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战",
            "产品架构专家",
            "不复制原文、项目案例、页面设计、图片、提示词或作者表达",
        ],
    ),
)
check(
    "product source maps record product insight article boundary",
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
        repo_source_map,
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
            "端到端 GSD/CAD 准入与 AI 工具编排交给 `wise-agent`",
            "不把“放下 PRD”理解为跳过产品语义、评审、留痕、合规和验收",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "放下 PRD：写给AI Native时代的产品经理朋友们",
            "PRD 从静态翻译文档升级为上下文包、验收种子和工程交接门禁",
            "不把“放下 PRD”理解为跳过产品语义、评审、留痕、合规和验收",
        ],
    ),
)
check(
    "product source maps record backlog decision article boundary",
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
        repo_source_map,
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
    "source maps record architecture demand analysis source",
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
        wise_agent_source_map,
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
        repo_source_map,
        [
            "架构30：架构思维：需求分析",
            "需求分析协同门禁、根源需求、产品定义、产品边界、上下游分工、稳定点 / 变化点、边界坐标",
            "公开 HTML 读取标题、作者、发布时间和正文",
            "不把单篇文章观点写成组织制度、项目事实、执行授权或架构师必须越过产品 owner 的理由",
        ],
    ),
)
check(
    "source maps record requirements standards sources",
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
        wise_agent_source_map,
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
        repo_source_map,
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
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_product_to_engineering,
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
        wise_agent_source_map,
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
        repo_source_map,
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
    "source maps record business architecture product value sources",
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
        wise_agent_source_map,
        [
            "业务 / 产品 / 技术交叉准入",
            "技术架构服务业务复制、业务同质性、价值函数、成本函数、主要矛盾",
            "不得把技术平台、AI 原型或架构升级直接等同于产品价值",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "业务 / 产品 / 技术交叉准入参考来源",
            "业务同质性、价值函数、成本函数、主要矛盾",
            "Codex in-app Browser 的 Playwright 接口",
            "架构批准或 Execution Grant",
        ],
    ),
)
check(
    "product source map records business architecture planning source",
    has_all(
        product_source_map,
        [
            "业务架构规划与项目组合",
            "业务架构到底有什么用？",
            "https://mp.weixin.qq.com/s/Xvu7hT4IH8D3BBY2PrTbnA",
            "企业架构EA之家",
            "2026-07-07 13:50:00 Asia/Shanghai",
            "2026-07-08",
            "Android MicroMessenger UA 公开 HTML 读取标题、作者、发布时间和正文",
            "business-architecture-planning.md",
            "共同业务语言、业务能力地图、战略到项目组合、能力-项目-系统映射、投资决策支持",
            "知识库回流",
            "不把文章观点写成组织制度、预算审批、系统设计、Execution Grant 或上线审批",
        ],
    ),
)
check(
    "AI Native source map records software design philosophy complexity gate",
    has_all(
        wise_agent_source_map,
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
    "source maps record architecture true-skill article",
    has_all(
        wise_agent_source_map,
        [
            "认知跃迁16-如何练成架构设计真功夫",
            "https://mp.weixin.qq.com/s/6EFJZpH39ryWA3u_Wlxuzw",
            "作者字段为 `李文强`",
            "2026-06-03 15:54:27",
            "小闭环决策澄清门禁",
            "专业分工与协作关系",
            "拆分 / 合并 V 字判断",
            "长期交付成本稳定",
            "自动问询 / 决策",
            "不得把微服务、SOA、EDA、中台或框架名称当成边界",
        ],
    )
    and has_all(
        senior_source_map,
        [
            "微信公众号文章：认知跃迁16-如何练成架构设计真功夫",
            "https://mp.weixin.qq.com/s/6EFJZpH39ryWA3u_Wlxuzw",
            "作者：`李文强`",
            "2026-06-03 15:54:27",
            "拆分与合并的 V 字判断",
            "长期交付成本",
            "小闭环决策澄清门禁",
            "不能替代功能归类、边界划分、颗粒度和长期交付成本判断",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "认知跃迁16-如何练成架构设计真功夫",
            "https://mp.weixin.qq.com/s/6EFJZpH39ryWA3u_Wlxuzw",
            "小闭环决策澄清门禁",
            "拆分 / 合并 V 字判断",
            "稳定元素 / 变化关系",
            "长期交付成本判断",
            "作者字段为 `李文强`",
            "2026-06-03 15:54:27",
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
        wise_agent_source_map,
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
        wise_agent_source_map,
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
    "AI Native source map records official Anthropic skills methodology and Perplexity pending boundary",
    has_all(
        wise_agent_source_map,
        [
            "Lessons from building Claude Code: How we use skills",
            "https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills",
            "Skill 是 instructions / scripts / resources 文件夹",
            "`SKILL.md` 做导航",
            "gotchas 优先",
            "重复能力脚本化",
            "Skill 类型分组",
            "description 服务发现",
            "真实使用检验",
            "Perplexity Research 文章",
            "2026-07-06 普通抓取、HEAD 请求和 Playwright 访问均超时",
            "不把该链接作为已吸收来源",
        ],
    ),
)
check(
    "AI Native source maps record good skill design methodology source",
    has_all(
        wise_agent_source_map,
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
        repo_source_map,
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
    "AI Native source maps record Harness skill best practices source",
    has_all(
        wise_agent_source_map,
        [
            "Harness 工程之道：Skill 原理与最佳实践",
            "https://mp.weixin.qq.com/s/yo2f5edeNNkYtCte9P0yhQ",
            "Skill 反向验证参考来源",
            "渐进性披露、`SKILL.md` 路由器、description 触发机制、资源加载契约、工具权限最小化、脚本确定性、状态快照、触发测试、功能走查和性能对比",
            "张梦杰",
            "阿里云开发者",
            "2026-07-01 08:30:00 Asia/Shanghai",
            "2026-07-01 普通 `curl` 返回微信“环境异常”验证页，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者、页面时间字段和 `#js_content` 正文",
            "不复制原文、图片、目录结构",
            "平台宣传",
            "不把文中工具能力、个人偏好持久化、自动执行或外部 Harness 写成当前 Codex 默认能力、执行授权、测试通过、CR 结论或上线审批",
            "可以吸收 Skill 反向验证方法",
            "资源引用必须说明触发时机 / 资源位置 / 预期产出",
            "真实提示词覆盖触发测试、功能走查、负向路径和对照评估",
        ],
    )
    and has_all(
        repo_source_map,
        [
            "Harness 工程之道：Skill 原理与最佳实践",
            "https://mp.weixin.qq.com/s/yo2f5edeNNkYtCte9P0yhQ",
            "仓库级 Skill 反向验证",
            "`AI Native 研发流程编排` 工程化参考来源",
            "渐进性披露、`SKILL.md` 路由器、description 触发、资源加载契约、工具权限最小化、脚本确定性、状态快照、触发测试、功能走查和性能对比",
            "张梦杰",
            "阿里云开发者",
            "2026-07-01 08:30:00 Asia/Shanghai",
            "通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者、页面时间字段和正文",
            "不复制原文、图片、案例",
            "平台宣传",
            "不把外部机制写成当前 Codex 默认能力、执行授权、测试通过、CR 结论或上线审批",
        ],
    ),
)
check(
    "repo source map records PRD AI prescan source boundary",
    has_all(
        repo_source_map,
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
    "product source maps record deliberation workflow sources",
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
        repo_source_map,
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
            "端到端流程和 GSD/CAD 准入交给 `wise-agent`",
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
            "GSD/CAD 准入结论由 `wise-agent` 编排",
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
            "### 6.2 验收种子到测试驱动设计",
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
            "按角色分层消费",
            "决策层回答 Why / What 和成功标准",
            "方案层回答 How、取舍、成本和风险",
            "实现层回答输入、输出、边界、异常、接口和验收",
            "功能名不能替代需求",
            "需求变更必须更新版本号、影响范围、通知对象、当前评审结论和过程记录链接",
            "需求变更必须生成影响清单",
            "目标/范围、流程/交互、规则/字段、接口/事件、验收种子、测试用例、发布风险和通知对象",
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
        wise_agent_prd_system_design_review,
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
            "## 文档标识与文件命名",
            "`〈主题〉-产品设计.md`",
            "规范主题 + 产品文档精确路径",
            "将冲突列为待确认并询问 owner",
            "只有用户明确授权项目约规治理时才修改",
            "更新既有文档默认保持原路径",
            "只有用户明确进入命名迁移任务时才改名",
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
            "核心名相、用户、主体与角色/对象",
            "场景与流程、能力与功能",
            "需求链卡片",
            "状态与业务规则、产品 DNA 和图形视图",
            "产品能力、数据、权限、风险与待确认",
            "验收与产品到架构交接",
            "Product Context Card",
            "附录按需展开",
            "精简输出规则",
            "来源/问题ID",
            "需求ID",
            "验收种子ID",
            "质量属性ID",
            "验收种子交接矩阵",
            "验收标准：〈可复核的通过条件〉",
            "边界路径：〈临界值、空值、重复、权限或状态边界〉",
            "异常路径：〈失败、超时、中断、外部不可用或人工兜底〉",
            "模板占位符使用 `〈...〉`",
            "每个 P0/P1 需求必须能回到问题、目标、场景、规则和验收",
            "每个进入开发候选的需求必须能关联场景、能力或功能、关键规则和验收种子",
            "正式 PRD 以最终标准版本为主",
            "文档控制只保留当前版本号、状态、owner、发布日期、评审结论摘要和过程记录链接",
            "按角色分层消费",
            "决策层服务业务 / 管理者",
            "方案层服务产品 / 设计 / 架构",
            "实现层服务开发 / 测试 / 发布",
            "需求变更必须补影响清单",
            "影响清单进入过程资产，正式 PRD 只保留当前有效结论和链接",
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
            "核心概念、业务抽象、关键图形视图、完整状态机、生命周期、字段口径和规则矩阵",
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
            "definition_and_boundary",
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
            "PLACEHOLDER_FIELD",
            "placeholder_fields",
            "placeholder fixture unexpectedly passed",
        ],
    ),
)
check(
    "senior skill exposes deterministic architecture deliverable checker",
    has_all(
        senior_skill,
        [
            "scripts/check_architecture_deliverable.py",
            "架构方案、系统分析设计、重构设计、代码 Review、生产变更和图形 brief",
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
            "产品语义输入、背景目标、边界、运行时场景、工程规则、详细设计、规则落地、非功能、测试和实施交接",
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
            '"refactoring-design"',
            '"code-review"',
            '"production-change"',
            '"diagram-brief"',
            "background_and_goal",
            "release_and_risk",
            "engineering_anchor",
            "PLACEHOLDER_FIELD",
            "placeholder_fields",
            "placeholder fixture unexpectedly passed",
            "TABLE_DESIGN_CHECKS",
            "table_identity",
            "table_fields",
            "table_uniqueness",
            "table_access_path",
            "table_compatibility",
            "incomplete table fixture unexpectedly passed",
            "complete table fixture unexpectedly failed",
            "WIND_REQUIRED_FIELDS",
            "wind_required_fields",
            "wind_required_field_defaults",
            "wind_request_id_as_business_key",
            "invalid Wind table fixture unexpectedly passed",
            "valid Wind table fixture unexpectedly failed",
            "invalid second Wind table fixture unexpectedly passed",
            "request id business key fixture unexpectedly passed",
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
            "refactoring-design-valid.md",
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
    "java service generator aligns templates with Wind coding conventions",
    has_all(
        codegen_skill,
        [
            "基础服务、DTO、Request、Query、Entity、Mapper、MapStruct、Service、ServiceImpl 模板是 Wind 编码约规的标准生成面",
            "权威规则以 `wind-coding-conventions` Skill 为准",
            "生成后规则审查回到 `wind-coding-conventions`",
            "源码级 CR / TDD 回到 `senior-software-architect`",
            "Entity 不外露",
        ],
    )
    and has_all(
        codegen_rules,
        [
            "Wind 编码约规的标准模板实现面",
            "规则权威来源是 `wind-coding-conventions` Skill",
            "face 模块生成的 Service 契约只暴露 DTO/Request/Query/WindQuery/分页结果",
            "不暴露 Entity、Mapper、Repository 或 MyBatis `Page`",
        ],
    )
    and has_all(
        codegen_nobe_patterns,
        [
            "Wind 编码约规的标准实现样本",
            "以 `wind-coding-conventions` 和项目本地 `AGENTS.md` 为准",
            "DTO / Request / Query / Service 是 face 对外契约",
            "Entity 只在 ServiceImpl、DAL、Mapper 和 Converter 内部流转",
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
        routes={"senior", "coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="cross language complexity hotspot scan",
        prompt="只看最近改动里的 N+1、循环内 I/O、循环内重复线性扫描和错误数据结构，做一次复杂度热点检查",
        routes={"senior", "coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="service layer architecture smell",
        prompt="这个 Spring Service 有跨层调用、事务边界混乱和公共模块垃圾桶问题，帮我做架构坏味 CR",
        routes={"senior", "coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="in memory business service review",
        prompt="做一轮代码 CR：这个 Spring Boot 业务模块新增了 InMemoryOrderService 和 Map 存储实现，Controller 直接调用它，判断是否能作为生产实现交付",
        routes={"senior", "coding-review-deep-dive.md", "negative-constraints.md"},
    ),
    RouteFixture(
        name="generic java coding conventions",
        prompt="这是一个普通 Maven Java 21 项目，没有 Wind/Nobe 依赖。请按通用 Java 约规检查命名、空值契约、异常日志、金额时间处理和测试代码，不要套 face/impl 或 Wind API 规则。",
        routes={"wind", "java-coding-conventions.md"},
    ),
    RouteFixture(
        name="ordinary Java source CR loads generic conventions",
        prompt="请对这个普通 Maven Java 21 项目的 OrderService 做源码 CR，检查事务边界、异常契约和测试缺口；项目没有 Wind/Nobe 依赖。",
        routes={"senior", "java-coding-conventions.md", "coding-review-deep-dive.md"},
    ),
    RouteFixture(
        name="Wind source CR loads conditional conventions",
        prompt="请对这个明确使用 Wind/Nobe 依赖的 ServiceImpl 做源码 CR，按 Wind 编码约规检查模块边界、事务和测试缺口。",
        routes={"senior", "java-coding-conventions.md", "wind-coding-conventions.md", "coding-review-deep-dive.md"},
    ),
    RouteFixture(
        name="wind dependency enables specialized conventions",
        prompt="这个 Java 项目的 AGENTS.md 没写 Wind opt-in，但 pom.xml 依赖 Wind/Nobe 组件，源码 import 了 WindPagination、WindQuery 和 com.wind.transaction.core.enums.CurrencyIsoCode，请判断应启用哪些编码约规。",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="generic java agents conventions init",
        prompt="给这个普通 Gradle Java 21 项目初始化 AGENTS.md 编码约规入口；项目没有 Wind/Nobe 依赖，不要加入 face/impl 或 Wind API 规则。",
        routes={"wind", "java-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind optional dependencies stay conditional",
        prompt="这个 Java 项目已明确遵守 Wind 编码约规，包含币种字段，但没有 JSpecify、MapStruct 或 MyBatis Flex 依赖。请判断应启用哪些规则。",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project coding conventions opt in review",
        prompt="这个 capte-domain 项目的 AGENTS.md 标明遵守 Wind 编码约规，帮我 CR face/impl 模块、基础服务、ApplicationService、DTO/Entity 分层和 MyBatis Flex 查询",
        routes={"senior", "java-coding-conventions.md", "project-governance-service-api-modeling.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project entity exposure review",
        prompt="这个项目遵守 Wind 编码约规，帮我做源码 CR，检查服务层和接口设计有没有 Entity 暴露到 face Service、ApplicationService、Controller、Facade、Adapter 或跨模块接口",
        routes={"senior", "java-coding-conventions.md", "project-governance-service-api-modeling.md", "coding-review-deep-dive.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project model package ownership review",
        prompt="结合 capte-domain 的包名划分，补充 Wind 编码约规里包、接口、模型应该放哪个模块：DTO、Request、Query、Command 优先放 *.model.dto、*.model.request、*.model.query、*.model.command 还是兼容 *.dto、*.request、*.query、*.command；Event、VO、Entity、Mapper、MapStruct、application、domain、converter、callback/spi、listener、webhook、core、infrastructure 分别怎么归位",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md", "wind-coding-examples.md"},
    ),
    RouteFixture(
        name="wind project currency enum redline",
        prompt="这个项目遵守 Wind 编码约规，检查 DTO、Request、Entity 和事件里的币种字段是否统一使用 com.wind.transaction.core.enums.CurrencyIsoCode 枚举，不要用 String currency",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project idempotency unique key redline",
        prompt="这个项目遵守 Wind 编码约规，检查幂等或唯一处理是否依赖外部 requestSn，而不是使用表内业务 UK 或联合 UK",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project speculative locking redline",
        prompt="这个项目已 opt-in Wind 编码约规，基础服务为了未来可能并发准备先加本地锁、分布式锁和 LocksWrapper，请评审",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project source observation conventions",
        prompt="阅读 wind-integration、nobe、capte-domain 代码库的项目结构、模块划分、包名划分、命名风格、编码习惯和 API 使用，完善 Wind 编码约规",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md", "wind-coding-examples.md"},
    ),
    RouteFixture(
        name="wind project platform service enum template",
        prompt="阅读 capte-domain platform 目录下的 system、alert、iam 相关模块，完善 Wind 编码约规：基础服务通用模板、方法签名、服务命名、DTO/Request/Query 放置位置、枚举命名和枚举类模板",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md", "wind-coding-examples.md"},
    ),
    RouteFixture(
        name="wind project query api dictionary conventions",
        prompt="这个项目已 opt-in Wind 编码约规，参考查询字段命名、服务层查询方法命名、内网 API 命名及安全、系统字典配置与国际化规范做规则检查，并确认架构师 reference 不再复制这些细则",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project coding conventions opt in tdd",
        prompt="这个 wind 项目 AGENTS.md 已标明遵守 Wind 编码约规，帮我按 TDD 给 ServiceImpl 和基础服务补测试，重点看真实内部链路、QueryWrapper、Mapper 语义和外部端口替身边界",
        routes={"senior", "java-coding-conventions.md", "testing.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind project coding examples",
        prompt="这个项目已 opt-in Wind 编码约规，给 AI Maker 一些服务层、基础服务、DTO/Entity、MyBatis Flex 和 TDD 的最佳实践正反例参考",
        routes={"wind", "java-coding-conventions.md", "wind-coding-conventions.md", "wind-coding-examples.md"},
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
        routes={"senior", "testing.md", "workflow.md"},
    ),
    RouteFixture(
        name="business-driven validation to tdd",
        prompt="会员权益方案已有验收样例和质量属性种子，把业务驱动验证映射成 TDD 测试计划，区分失败测试、监控指标和人工确认门禁",
        routes={"senior", "testing.md", "workflow.md"},
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
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "planning-execution-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native GSD CAD handoff",
        prompt="产品上下文包已有目标对象规则和验收种子，评估如何把 GSD Wave 和 CAD 原子任务结合，输出 Harness 摘要、Execution Grant 缺口和停止条件",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "planning-execution-admission.md"},
    ),
    RouteFixture(
        name="wise-agent decision wayfinding before spec",
        prompt="使用 $wise-agent 推进权限系统重构。目标大致明确，但角色、策略、组织、自定义权限和迁移之间的路线仍很模糊，明显不是一次会话能可靠写成 Spec 或实施计划的；先不要实现，也不要把猜测拆成开发任务。",
        routes={"wise-agent", "planning-execution-admission.md"},
    ),
    RouteFixture(
        name="wise-agent explicit Wayfinder method absorption",
        prompt="使用 $wise-agent 按 Wayfinder 的决策地图方法处理这个跨轮模糊任务，但不要安装外部 Skill 或创建 Issue。",
        routes={"wise-agent", "planning-execution-admission.md", "superpowers-skill-library.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native GSD wise agent",
        prompt="进入 GSD 产研协同研发流程：目标是交付生产可用能力，不是让 AI 随机推进模拟模块、内存版业务 Service 或样子货；产品专家先做需求分析、产品设计和确认，架构师再做系分设计、编码、TDD、CR 和验证",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "planning-execution-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="SDLC maps into stable collaboration domains",
        prompt="参考 Agentic SDLC、Agentic DevOps 和 Loop Engineering 评估现有 AI 工作流，确认 SDLC 是否应该替换 Loop，并避免以后每出现一个行业概念就重命名流程",
        routes={"wise-agent", "delivery-lifecycle.md", "engineering-governance.md", "delivery-execution-control.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native demand analysis collaboration gate",
        prompt="AI Native 研发流程进入需求分析协同门禁：用户原始诉求里混了功能解法，先输出需求分析结论卡，明确根源需求、产品定义、产品边界、稳定点/变化点、边界坐标和上下游分工，再判断能否进入 PRD / 系分预审或 GSD Round 0",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "planning-execution-admission.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native core problem diagnosis gate",
        prompt="进入 AI Native 问题核心诊断模式：这次需求无止境、价值意义摇摆，还混着工具方案和架构动作；先抓住问题的核心，输出概念定名、需求止损、定向定性定位定量、整体 / 系统 / 科学诊断，再决定是否进入 GSD 或系分",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native development standards gate",
        prompt="AI Native 研发流程补需求 / 设计 / 编码标准门禁：系统需求或产品需求未确认时，不进入 SDD、测试、代码或 CAD；输出需求基线稳定性、需求条目质量、HLR/LLR 设计追踪、编码规则原因示例验证方式和防御式编程检查",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "spec-template-practices.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native real variation axis design review",
        prompt="参考设计模式的本质是找到变化、封装变化，进入 AI Native 设计评审：让产品专家先标出稳定业务事实和真实变化轴，架构师再检查接口、策略、工厂、状态机、规则层和配置化是否有 owner、验收方式和测试边界；Wind 项目不要为了套设计模式新增浅服务或单实现抽象",
        routes={"wise-agent", "delivery-lifecycle.md", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "engineering-governance.md", "source-map.md", "product", "product-scenario-routing.md", "senior", "java-coding-conventions.md", "wind"},
    ),
    RouteFixture(
        name="AI Native product system DNA gate",
        prompt="进入 GSD 前先做产品 / 系统 DNA 门禁：当前只有功能清单和页面草图，检查核心对象、业务不变量、状态流转、责任边界、演化规则和验证方式，避免功能先行、规则后补",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "spec-template-practices.md", "planning-execution-admission.md", "product"},
    ),
    RouteFixture(
        name="AI Native intent to production role loop",
        prompt="参考 Loop Engineering，把 AI 工作流从意图 / 需求收集做到生产交付闭环，区分业务 owner、产品专家、UED、架构师、AI Maker、AI Checker、质量 / 测试门禁和发布 owner 在每个阶段的分工、交接物、验证门禁和停止条件；需求变更进入 Loop 时先识别 PRD 决策层 / 方案层 / 实现层、系分、接口 / 事件、规则 / 字段、验收种子、测试用例、发布风险、通知对象和过程记录链接的影响",
        routes={"wise-agent", "delivery-lifecycle.md", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "engineering-governance.md", "delivery-execution-control.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native three layer feedback loop cadence",
        prompt="参考吴恩达对 Loop Engineering 的理解，优化 AI Native 分角色 Loop：区分 Agentic Coding Loop、Developer Feedback Loop、External Feedback Loop 三个时间尺度，说明外层真实用户/市场反馈如何修正 Vision，中层开发者如何改 Spec，内层 AI 如何按 Spec/Evals 执行验证，并结合老祖宗智慧校准快慢节奏。",
        routes={"wise-agent", "delivery-lifecycle.md", "product-to-engineering-lifecycle.md", "engineering-governance.md", "delivery-execution-control.md", "code-delivery.md", "verification-review-release.md", "huaxia-practical-wisdom", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native autonomous discovery to delivery loop",
        prompt="进入 AI Native 产研协同，让 AI 自我挖掘需求和代码上下文，确认边界，设计并 CR 需求，再执行 TDD、编码、代码 CR、验证实际可行，最后判断完成、继续 Loop、停止或需要人工确认，输出自主交付控制卡",
        routes={"wise-agent", "delivery-lifecycle.md", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "engineering-governance.md", "delivery-execution-control.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native small loop decision gate",
        prompt="完善 AI Native Loop 的自驱能力：每一个小闭环完成后尝试自动问询或自动决策，并把自决推进、询问 owner、继续收敛或停止交接 写入下一个流程",
        routes={"wise-agent", "delivery-lifecycle.md", "delivery-execution-control.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native loop task end accountability",
        prompt="进入 AI Native 产研协同：每一次任务结束都要先对交付内容负责，做交付责任自检和决策澄清门禁，再判断修复、交接、停止，还是开启下一任务计划问询或最小计划草案",
        routes={"wise-agent", "delivery-lifecycle.md", "delivery-execution-control.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native decision gate blocker progression",
        prompt="进入 AI Native 产研协同 问询推进：我接受你对当前 blocker 的建议，按你的建议推进下一步；不要重新展开全局规划，只关闭当前 blocker、写入下一阶段输入，再挑下一最高价值 blocker。",
        routes={"wise-agent", "delivery-lifecycle.md", "delivery-execution-control.md"},
    ),
    RouteFixture(
        name="AI Native questioning repair",
        prompt="$wise-agent 做一轮问询修复吧",
        routes={"wise-agent", "delivery-lifecycle.md", "delivery-execution-control.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native PRD system design deliberation review",
        prompt="对这份 AI 生成的 PRD 和系分设计做 MAGI 三角色合议预审，按 review_task、evaluation_task、reporting_task 输出 ACCEPT/REJECT/PENDING 决策日志、风险清单、owner、验证方式和下一步路由，不要直接改正文",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native PRD AI prescan review",
        prompt="做 PRD 评审会前 AI 预扫描：先让产品专家按完整性、一致性、可测试性、二义性找疑似问题和追问点，再接入 MAGI 预审的 review_task、evaluation_task、reporting_task，输出 ACCEPT/REJECT/PENDING 和 owner",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "product", "product-scenario-routing.md", "product-prd-quality-gates.md", "product-design-and-prd.md"},
    ),
    RouteFixture(
        name="AI Native final PRD system design document gate",
        prompt="整理最终 PRD / 系分：正式交付文档不要保留讨论过程、迭代草稿、AI 推理轨迹或被拒方案，把过程内容迁移到评审报告、Decision Log、Goal Ledger 或任务计划，只保留当前有效结论和验收",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "spec-template-practices.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native target plan atomic admission gate",
        prompt="做目标计划 / 原子执行准入：判断是否需要 Round 0、Wave/Atomic Task、原子执行候选缺口和 Execution Grant 缺口",
        routes={"wise-agent", "engineering-governance.md", "planning-execution-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native target plan default authorization",
        prompt="优化 AI Native 产研交付视图：不希望每个任务都单独审批，目标计划 / 原子执行内部层按授权边界默认推进；Codex 替我审批模式用于低风险任务自动通过",
        routes={"wise-agent", "engineering-governance.md", "planning-execution-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native goal target plan composition",
        prompt="做 Goal + 目标计划组合：这个中大型项目需要持续推进，把业务目标、生产可用能力、成功标准、计划分波、原子执行候选、验证证据、预算时间盒、停止条件、Goal 状态和交接节奏串起来，不要把 Goal 当 Execution Grant",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "planning-execution-admission.md", "goal-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native goal plan grant",
        prompt="使用 Goal + 目标计划按任务计划推进，不希望每个任务都被 Execution Grant 阻塞；形成 Plan Grant，低风险本地任务直接推进，Git 默认只给提交切片和建议 commit message，联网、生产和高风险业务仍显式确认",
        routes={"wise-agent", "engineering-governance.md", "planning-execution-admission.md", "goal-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native goal staged commits",
        prompt="使用 Goal + 目标计划按任务计划推进，并在每个已验证任务阶段提交代码；形成提交切片和 commit_after_verified_task，但不要 push、不要联网、不要生产操作",
        routes={"wise-agent", "engineering-governance.md", "planning-execution-admission.md", "goal-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native agent loop engineering",
        prompt="参考 Loop Engineering：用 /goal 或 /loop 持续推进目标计划，但必须有状态载体、反馈源、自我验证、最大轮次、无进展检测、预算上限、停止条件和交接物，不能把 auto mode 当无条件授权",
        routes={"wise-agent", "engineering-governance.md", "delivery-execution-control.md", "goal-governance.md", "planning-execution-admission.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native production ready agent loop",
        prompt="完善 AI 工作量 loop 流程，使其真正生产可用：检查自动化心跳、隔离执行、状态落盘、Skill 上下文、连接器权限、Maker / Checker 解耦、独立验证、观测审计、人工接管、发布回滚和理解债，不能把能自动跑当能上线",
        routes={"wise-agent", "engineering-governance.md", "delivery-execution-control.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native agent loop maturity diagnosis",
        prompt="这个 Agent Demo 里表现很好，但上线后总是把客户信息和政策搞混，还反复用废弃 API；请不要先改 Prompt 或直接上 Loop，先按 Prompt Engineering、Context Engineering、Harness Engineering、Loop Engineering 四层嵌套判断当前瓶颈、最小修复和是否允许 L4 试点",
        routes={"wise-agent", "engineering-governance.md", "delivery-execution-control.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native wisdom lens for loop scheduling",
        prompt="请用独立的华夏经世智慧能力和 Loop 取舍校准增强 AI Native Loop，并对当前 AI 工作流做一轮完整 CR：在准入前、计划拆解、执行核验、授权纠偏和复盘回流中，借用阴阳平衡、先为不可胜、庖丁解牛、中庸之道、循名责实、无为而治、每日三省、知行合一和一张一弛做取舍、止损、节奏、停止判断和评审发现；不要替代事实、测试、CR、授权或上线审批",
        routes={"wise-agent", "huaxia-practical-wisdom", "delivery-execution-control.md", "planning-execution-admission.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native classic wisdom lens supplement",
        prompt="结合周易、道德经、庄子、论语、中医、阴阳五德始终论等经典来源，补足独立的华夏经世智慧能力：只沉淀现实取舍问题，不做玄学、医学建议或经典考据",
        routes={"wise-agent", "huaxia-practical-wisdom", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native AI bug patch gate with wisdom lens",
        prompt="AI 找到一个 bug 并给了补丁，参考 Linus 对 AI bug report 和创可贴式修复的提醒，结合老祖宗的循名责实、庖丁解牛、治未病做门禁：先判断是否有复现证据、根因、同类影响、最小修复、独立验证和下一 owner，不要让 AI patch 自证可合并",
        routes={"wise-agent", "verification-review-release.md", "huaxia-practical-wisdom", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native three card handoff protocol",
        prompt="进入三卡交接：产品专家输出 Product Context Card 和验收种子，AI Native 输出 Engineering Handoff Card，生产可用 Loop 再补 生产交付卡，缺任一卡都不要进入实现、CAD 或自动 Loop",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "planning-execution-admission.md", "delivery-execution-control.md", "verification-review-release.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native target plan atomic handoff state machine",
        prompt="进入知止者的目标计划和原子执行协同流程，梳理 Round0 到 Wave Plan、Plan Grant Active、Loop Candidate、Atomic Candidate、Atomic Loop Active、Verified/Paused/Escalated/Closed 的状态机，并输出 Engineering Handoff Card、Plan Grant + Loop 预算绑定、失败回写和下一 owner",
        routes={"wise-agent", "engineering-governance.md", "delivery-execution-control.md", "goal-governance.md", "planning-execution-admission.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native routes Superpowers skills library",
        prompt="Codex 已支持官方 Superpowers 插件：安装并加入知止者调度，验证真实协同后删除 external-superpowers 快照，说明脚本、Git/worktree/subagent 边界和验证门禁",
        routes={"wise-agent", "engineering-governance.md", "superpowers-skill-library.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="wise-agent coordinates Superpowers debugging methods",
        prompt="知止者接手 Java 服务测试失败：先定位根因，再补回归测试和最小修复，完成前给出新鲜验证证据；Superpowers 已安装，按需调度即可",
        routes={"wise-agent", "senior", "systematic-debugging", "test-driven-development", "verification-before-completion", "superpowers-skill-library.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="wise-agent coordinates Superpowers product brainstorming",
        prompt="知止者把模糊产品想法收敛成目标、对象、边界和验收种子；Superpowers 已安装，可按需使用 brainstorming，但不要生成工程实现计划",
        routes={"wise-agent", "product", "brainstorming", "superpowers-skill-library.md"},
    ),
    RouteFixture(
        name="AI Native layers AI coding frameworks",
        prompt="参考 Superpowers、GSD、GStack、Trellis 这些 AI 编码框架，判断它们如何纳入 知止者，不要新增流程或默认安装工具",
        routes={"wise-agent", "engineering-governance.md", "delivery-execution-control.md", "superpowers-skill-library.md", "code-delivery.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native maps GStack role chain template",
        prompt="参考 GStack 模板流程优化 AI Native：/office-hours 先做产品思考，/plan-ceo-review 收敛 MVP，/plan-eng-review 做工程评审，/plan-design-review 做 UI 设计评审，然后开发、/review、/qa、/ship，要求映射到产研协同，不新增外部命令菜单。",
        routes={"wise-agent", "delivery-lifecycle.md", "product-to-engineering-lifecycle.md", "prd-system-design-review.md", "engineering-governance.md", "delivery-execution-control.md", "superpowers-skill-library.md", "code-delivery.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native coordinates specialized skill roles",
        prompt="AI Native 继续完善分角色流程，用于控制不同 skills 完成任务：产品专家做需求分析、产品设计和验收；资深架构师做架构设计、系分设计、代码设计、TDD、编码和 CR；Wind 编码约规作为架构师按需消费的唯一规则来源；代码阅读理解、架构图、流程图作为辅助能力接入。",
        routes={"wise-agent", "delivery-lifecycle.md", "product-to-engineering-lifecycle.md", "engineering-governance.md", "code-understanding-tools.md", "verification-review-release.md", "product", "senior", "diagram-output.md"},
    ),
    RouteFixture(
        name="AI Native role skill tool framework collaboration matrix",
        prompt="AI Native 出一个分角色 Loop、Skill、工具、框架的协作判断矩阵，覆盖产品专家、架构师、Wind 编码约规 / wind-coding-conventions、画图能力、Superpowers/GStack 等辅助框架，说明每个节点谁主责、调用哪个 Skill、哪些工具只是辅助、交接物和不替代项。",
        routes={"wise-agent", "delivery-lifecycle.md", "product-to-engineering-lifecycle.md", "engineering-governance.md", "superpowers-skill-library.md", "code-understanding-tools.md", "verification-review-release.md", "product", "senior", "wind", "diagram-output.md"},
    ),
    RouteFixture(
        name="AI Native GStack production delivery review standard",
        prompt="结合 GStack 流程：/office-hours 六个 forcing questions、/plan-ceo-review 收敛 MVP、/plan-eng-review、/plan-design-review、开发、/review、/qa、/ship，完善 AI Native 流程，并整理生产交付审查标准。",
        routes={"wise-agent", "delivery-lifecycle.md", "engineering-governance.md", "delivery-execution-control.md", "superpowers-skill-library.md", "code-delivery.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native production effectiveness gate",
        prompt="参考代码写完了谁负责确认写对了、预发环境是否 OK 这篇文章，增强角色 Loop 的生产交付验证：代码变更要做版本回读、配置回读、冒烟验证、业务场景模拟验收、观测确认和工单回写；实际业务场景可通过 owner 问询、项目材料、公开资料、业内共识或行业标准规范确认，避免只是测试通过或页面看似可用。",
        routes={"wise-agent", "delivery-lifecycle.md", "code-delivery.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native unifies production ready workflow with wisdom lens",
        prompt="如何混一 AI 工作流，使其更加生产可用，结合老祖宗智慧看看：把 GSD、CAD、GStack、Goal、Harness 和工具链收成一个入口、一个契约、一个准出。",
        routes={"wise-agent", "delivery-lifecycle.md", "engineering-governance.md", "delivery-execution-control.md", "goal-governance.md", "planning-execution-admission.md", "superpowers-skill-library.md", "code-delivery.md", "huaxia-practical-wisdom", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native reusable work asset loop",
        prompt="参考给产品经理的 loop engineering，把 PRD 评审规则、客户访谈总结器、发布检查清单和每周产品信号做成可复用工作资产 Loop，要有触发器、动作、证据、记忆、停止条件和可复测样例。",
        routes={"wise-agent", "delivery-execution-control.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native CDD capability discovery gate",
        prompt="参考外部文章 CDD：先找能力，再写代码，强化 AI Native 落地执行能力；非 T0 的代码、文件、报告或外部写入任务，先做 Capability Discovery，查已有 Skill、Tool、Workflow、脚本和自动化，再判断缺口是否需要新实现。",
        routes={"wise-agent", "delivery-execution-control.md", "code-delivery.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native upgrades SDD suite and Harness contract",
        prompt="AI Native 看下整体升级 SDD/SSD 套件以及 Harness 版本，参考 Superpowers 6.0 的 task-reviewer、task-brief、review-package、progress ledger 和 pre-flight plan review，补验证门禁和停止条件，但不要默认运行外部脚本",
        routes={"wise-agent", "engineering-governance.md", "superpowers-skill-library.md", "code-delivery.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native checks Superpowers 6.x latest boundary",
        prompt="知止者确认 Superpowers 当前上游 release、Codex 官方市场安装标识和 manifest 版本，区分三条版本轴、插件启用状态、权限边界和不默认运行外部脚本",
        routes={"wise-agent", "engineering-governance.md", "superpowers-skill-library.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native routes Matt Pocock grill-me skills",
        prompt="AI Native 看下安装 mattpocock/skills，用 grill-me 协同产品专家和任务树推进模糊需求，说明安装边界和安全风险",
        routes={"wise-agent", "delivery-execution-control.md", "delivery-lifecycle.md", "superpowers-skill-library.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native grill-me loop progression gate",
        prompt="参考 grill-me 方法，加强 AI 工作流：Loop 推进中如果关键分叉未决、用户回答含糊或连续返工，适时进入 grill-me 盘问，一次只问一个问题、给推荐答案、能查先查，并把决策摘要写回下一阶段输入。",
        routes={"wise-agent", "delivery-execution-control.md", "delivery-lifecycle.md", "superpowers-skill-library.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native skill type owner routing",
        prompt="参考 Anthropic 内部 Skills 经验，细化 AI 流程、产品专家和架构师能力，但 AI Native 仍作为主入口；判断产品验证、代码质量、Runbook、CI/CD、模板脚手架、数据分析和基础设施操作分别由谁负责、交接物和验证证据是什么",
        routes={"wise-agent", "capability-routing.md", "product-to-engineering-lifecycle.md", "engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="wise agent control mechanism selection",
        prompt="知止者判断这个跨阶段、跨轮项目是否需要 SDLC、Goal、Loop、Worker 和 Checker：三个模块低耦合可并行，但公共契约和发布风险要独立验证，不要机械启用全部机制",
        routes={"wise-agent", "delivery-lifecycle.md", "goal-governance.md", "delivery-execution-control.md", "capability-routing.md", "engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="wise agent checker without worker",
        prompt="知止者只读判断一个高风险公共 API 发布证据是否需要 Checker；没有独立并行子任务，不派 Worker，也不调用外部代码评审工具",
        routes={"wise-agent", "capability-routing.md", "engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native skill split gate",
        prompt="AI Native 参考 Harness Engineering 和架构真功夫，评估项目下的 skill 是否应该多拆分几个更专项的 skill，再由 AI 流程统一调用；请判断哪些只更新 reference、哪些补 fixture / validator、哪些未来才新建顶层 Skill",
        routes={"wise-agent", "capability-routing.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native Harness skill best practices reverse validation",
        prompt="AI Native 参考《Harness 工程之道：Skill 原理与最佳实践》，对项目下的 Skill 做反向验证和最小重构：检查 SKILL.md 是否只是路由器、description 是否触发准确、references/scripts/fixtures 是否按需加载和可验证，并提炼最佳实践原则；不要照搬外部权限字段、运行钩子、用户偏好持久化或自动推送机制",
        routes={"wise-agent", "capability-routing.md", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native official skill methodology with wisdom lens",
        prompt="AI Native 参考 Anthropic 官方 Lessons from building Claude Code: How we use skills 和 Perplexity Agent Skills 文章，结合老祖宗的循名责实、庖丁解牛、治未病，推进 Skill 治理：description 做路由、gotchas 优先、重复动作脚本化、先补正负触发 fixture，再决定是否拆 Skill",
        routes={"wise-agent", "capability-routing.md", "huaxia-practical-wisdom", "source-map.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI coding workflow CR",
        prompt="评审我们的 AI 编码流程是否有 OpenSpec、Superpowers、Harness、权限边界、验证矩阵、代码 CR、发布监控和复盘闭环",
        routes={"wise-agent", "engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native code delivery closed loop",
        prompt="我们落地了 SDD / Spec / Harness，AI 编码更快，但 CR、测试、对齐、返工和上线质量没有明显改善。做 AI 代码交付闭环评审，输出瓶颈、Spec 强度、Harness 独立验证、CR 减负、知识回流和一次通过率返工率缺陷密度指标",
        routes={"wise-agent", "engineering-governance.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native progressive SDD Lattice Harness",
        prompt="参考渐进式 Spec Coding / PrismSpec 和 Lattice Harness，重构精简 AI 工作流：不要新增并列流程，按低风险轻量、中风险可评审、高风险 Harness、高不确定 TDD 分级，并用 Context、Verification、Evidence、Drift Check、Loop Learn 证明交付真的做对了。",
        routes={"wise-agent", "engineering-governance.md", "spec-template-practices.md", "code-delivery.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native update context gate",
        prompt="AI Native 执行 update-context：判断本轮交付后哪些 L0/L1/L2 上下文应回写，哪些不得自动写入 AGENTS.md、CONTEXT.md、ADR、Skill 或 fixture",
        routes={"wise-agent", "code-delivery.md"},
    ),
    RouteFixture(
        name="AI Native context system knowledge base governance",
        prompt="结合渐进式 SDD、Lattice Harness 和老祖宗智慧，给项目落地 context / 知识库治理：先梳理 AGENTS.md、CONTEXT.md、ADR、模块 reference、source-map、测试资产和 update-context，不要一上来就建设外部知识库。",
        routes={"wise-agent", "code-delivery.md", "huaxia-practical-wisdom", "code-understanding-tools.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native workflow yinyang unification",
        prompt="AI Native skill 中各式各样的 AI 工作流，做一轮混一，知其要者，一言而终，本于阴阳，神用无方",
        routes={"wise-agent", "delivery-execution-control.md", "code-delivery.md", "huaxia-practical-wisdom", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native domain expert distillation",
        prompt="AI Native 阅读这些 PRD / 系分 / 产品设计文档，把支付账务域蒸馏成可追溯业务专家和领域专家 Skill Pack，要求规划学习方式和学习路径，整理学习资料，提前学习内容，按业务域或模块分开保存学习结果，输出学习结果知识库规划、owner 追认和 test-prompts 压力测试。",
        routes={"wise-agent", "domain-expert-distillation.md", "product-to-engineering-lifecycle.md", "verification-review-release.md", "source-map.md", "product", "senior"},
    ),
    RouteFixture(
        name="AI Native spec template practices",
        prompt="落地 Spec 模板最佳实践：把产品上下文和系分交给 AI 编码，先区分 PRD / SDD / 实现 Spec 三层是否齐备，输出 Spec 强度、五段式骨架、AC 与测试映射、spec-lint、AC 覆盖、漂移检查、风险自查和轻重切换",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "spec-template-practices.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native production SDD source of truth",
        prompt="规范驱动开发 SDD：让 AI 写生产级代码，先检查 Spec 是否能作为事实来源，补结构化契约、正反例、边界错误处理、测试计划和五支柱验证，失败时回写 Spec 再重试",
        routes={"wise-agent", "engineering-governance.md", "spec-template-practices.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native knowledge expression gate",
        prompt="进入知识表达门禁：这个需求只有老板一句话、几篇文章和一个 AI 草稿，请判断是否足以让 AI 执行，输出目标、对象、规则、约束、验收样例、反馈源和缺口 owner；不要直接进 GSD/CAD/Loop",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native nonstandard problem mode",
        prompt="进入非标问题模式：客户和运营都说这个能力必须做，但没人能说清标准答案，请先定义问题主体、影响面、已知事实、关键不确定性、研究路径、候选方案、最小可逆实验、决策标准和停止条件",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "engineering-governance.md", "product", "product-scenario-routing.md"},
    ),
    RouteFixture(
        name="AI Native practical coding loop",
        prompt="进入实际项目编码 Loop：这个 GSD Wave 里有一个明确 Task ID，需要在真实代码库持续推进，请给 Coding Loop Contract，包含写入范围、只读范围、失败测试或验收样例、TDD 顺序、验证命令、独立 Checker、状态回写位置、提交切片、回滚方式和停止条件",
        routes={"wise-agent", "delivery-execution-control.md", "planning-execution-admission.md", "code-delivery.md", "verification-review-release.md", "senior", "testing.md", "workflow.md"},
    ),
    RouteFixture(
        name="AI Native feedback loop verification cluster",
        prompt="AI Coding 已经能快速生成和修复代码，但测试通过和覆盖率提升并不能证明系统没有变坏。请给 AI Native Loop 增加反馈闭环成熟度门禁，围绕支付幂等等高风险业务不变量建立验证簇，说明 L2/L3/L4/L5、生产证据、独立 Checker、预算和停止条件",
        routes={"wise-agent", "delivery-execution-control.md", "verification-review-release.md", "senior", "testing.md"},
    ),
    RouteFixture(
        name="AI Native architecture entropy loop",
        prompt="进入架构排熵 Loop：系统长期只加不删，出现承重 bug、废弃 API、循环依赖、概念膨胀、治理规则失效和局部性丧失。请设计持续巡检、状态回写、低风险修复、Maker/Checker、人工 triage、守卫自检和停止条件，不要把能扫描当成能自动删除",
        routes={"wise-agent", "delivery-execution-control.md", "verification-review-release.md", "senior", "evolutionary-architecture.md", "coding-review-deep-dive.md"},
    ),
    RouteFixture(
        name="AI Native quality test gate",
        prompt="做质量门禁：输出测试矩阵、验证顺序、CR 前置条件、失败回退和架构师 testing.md 调用点",
        routes={"wise-agent", "verification-review-release.md", "engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native change understanding gate",
        prompt="做理解门禁：把这次 diff / 重构计划整理成入口路径、影响模块、调用关系、源码锚点、验证证据和 CR 交接条件",
        routes={"wise-agent", "verification-review-release.md", "engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native codebase understanding brief",
        prompt="最近 Google Gemini CLI 和 Microsoft AgentRC 这类工具能快速阅读代码库、生成上下文和总结结论，帮我抽象进 AI Native 研发流程，设计代码库理解结论包和进入架构师 CR 的门禁，但不要默认安装工具",
        routes={"wise-agent", "verification-review-release.md", "engineering-governance.md", "code-understanding-tools.md"},
    ),
    RouteFixture(
        name="AI Native Ponytail minimal implementation admission",
        prompt="用 知止者评估 Ponytail 是否适合加入编码 Loop：要求编码前做最小正确实现检查，CR 时做过度设计专项检查，但不要默认启用 hook 或替代 TDD、安全和架构师源码级 Review",
        routes={"wise-agent", "code-understanding-tools.md", "verification-review-release.md", "source-map.md", "senior", "coding-review-deep-dive.md"},
    ),
    RouteFixture(
        name="AI Native Open Code Review checker admission",
        prompt="安装并接入 alibaba/open-code-review：希望它作为编码评审阶段的独立 Checker，消费 Java/Wind 项目约规后交给架构师做源码 CR，但不要替代 TDD、Git 授权或自动修复审批",
        routes={"wise-agent", "code-understanding-tools.md", "verification-review-release.md", "source-map.md", "senior", "coding-review-deep-dive.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="AI Native source quality review loop",
        prompt="参考 Code Review 与技术债治理文章，AI Native 结合现有编码约规、代码阅读工具、Open Code Review / OCR、Ponytail、Gemini/AgentRC/Understand Anything、Wind 项目约规和老祖宗 Wisdom Lens，落地一个高效可用的代码 CR 流程，并把好的 CR 结论和业务知识回流到项目上下文",
        routes={"wise-agent", "verification-review-release.md", "code-understanding-tools.md", "huaxia-practical-wisdom", "source-map.md", "senior", "coding-review-deep-dive.md", "java-coding-conventions.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="AI Native Karpathy coding hygiene admission",
        prompt="参考 Andrej Karpathy / karpathy-guidelines 优化 AI 编码 Loop：要求先暴露假设和分歧、简单优先、外科手术式变更、把任务转成可验证目标，但不要新增流程或替代 TDD、架构师 CR 和项目编码规范",
        routes={"wise-agent", "verification-review-release.md", "source-map.md", "senior", "coding-review-deep-dive.md"},
    ),
    RouteFixture(
        name="AI Native skill self-improvement and knowledge flow",
        prompt="参考让 Codex 越用越聪明的方法，完善 AI 流程里的经验回流、Skill 自我改进、知识归位和不要把个人长期偏好写进仓库的边界",
        routes={"wise-agent", "engineering-governance.md", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native skill self-improvement from repeated chat feedback",
        prompt="结合这几轮聊天交互，对 AI Native / Wind 编码约规做 Skill 自我改进外循环：把反复 CR 出来的职责归位、基础服务、Mapper default、同步已安装 Skill 和验证门禁沉淀到正确 Skill，不要把订单优惠券业务细节写进 AI Native",
        routes={"wise-agent", "code-delivery.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native knowledge production loop",
        prompt="参考 WorkBuddy 做 AI 技术早报和团队培训流程，把资料、业务背景和常用模板先上下文资产化，再设计知识生产、来源标识、验收 owner、更新频率和停用条件，但不要把厂商工具写成默认依赖",
        routes={"wise-agent", "code-delivery.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native WorkBuddy local coding agent admission",
        prompt="参考 WorkBuddy 的本地 IDE 和文件系统执行方式，增强 AI Native 的本地执行型 Coding Agent 准入：先读项目上下文、明确写入范围、生成候选代码 diff、跑验证、依赖和配置冲突决策澄清门禁，再消费通用 Java 约规和按需 Wind 编码约规并交给架构师 CR；不要制造第二套编码约规",
        routes={"wise-agent", "code-understanding-tools.md", "code-delivery.md", "verification-review-release.md", "source-map.md", "senior", "workflow.md", "ai-assisted-engineering.md", "negative-constraints.md", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="AI Native visual understanding for unfamiliar codebase",
        prompt="这个陌生多 Agent 代码库看不懂，先做图形化理解和架构描述转图的门禁，说明组件入口、启动顺序、认证权限、外部系统、数据消息流、源码锚点和进入 CR 的条件",
        routes={"wise-agent", "verification-review-release.md", "engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native read analyze codebase",
        prompt="阅读分析代码库：先做代码库理解结论包；评估是否需要 Gemini CLI / AgentRC / Understand Anything，但不要默认安装或联网",
        routes={"wise-agent", "verification-review-release.md", "engineering-governance.md", "code-understanding-tools.md"},
    ),
    RouteFixture(
        name="AI Native read code with Gemini readonly",
        prompt="要求阅读或分析代码时，优先启动 Gemini CLI 这类代码阅读工具，只读扫描入口路径、模块职责、调用关系和源码锚点，不能写文件或替代架构师 CR",
        routes={"wise-agent", "code-understanding-tools.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native tool install admission",
        prompt="评估 Gemini CLI / AgentRC / Understand Anything：列来源、安装认证联网写入边界、只读范围、隐私风险、人工替代路径和 CR 条件；Understand Anything 还要列 .understand-anything、dashboard、auto-update、hook 和图谱提交边界",
        routes={"wise-agent", "code-understanding-tools.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native Understand Anything knowledge graph admission",
        prompt="用 AI Native 研发流程编排评估是否需要安装 Understand Anything：大型代码库需要生成代码库知识图谱、dashboard、diff impact 和 onboarding guide；先列安装联网写 ~/.understand-anything 和项目 .understand-anything、auto-update、post-commit hook、图谱提交、敏感文件排除和 CR owner，不要默认安装",
        routes={"wise-agent", "code-understanding-tools.md", "verification-review-release.md", "source-map.md"},
    ),
    RouteFixture(
        name="AI Native design code alignment",
        prompt="做设计-代码对齐：对齐 OpenSpec / 系分设计与当前代码，输出设计条款、代码入口、实现状态、偏差和测试证据",
        routes={"wise-agent", "code-understanding-tools.md", "verification-review-release.md", "engineering-governance.md"},
    ),
    RouteFixture(
        name="AI Native fact boundary check",
        prompt="做事实边界检查：这份 AI 生成的 GSD/CAD 流程里有推测和额外实现建议，请区分事实、推断、待确认和范围外不做，禁止无根据猜测、模型脑补或超出用户目标的实现扩张",
        routes={"wise-agent", "engineering-governance.md", "planning-execution-admission.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native minimal delivery first principles",
        prompt="用 AI Native 研发流程约束 AI 不要乱写代码：不知道就问，没要求的不写，只改被要求的范围，给验收标准别给步骤，并用第一性原理判断目标是否清楚、路径是否最短",
        routes={"wise-agent", "engineering-governance.md", "verification-review-release.md", "product-to-engineering-lifecycle.md"},
    ),
    RouteFixture(
        name="AI Native routes PRD work",
        prompt="用 AI Native 研发流程编排先判断这批客户访谈和运营后台截图能否进入 PRD，输出成熟度、owner、交接物和停止条件，再分派给产品架构专家写正文",
        routes={"wise-agent", "product-to-engineering-lifecycle.md"},
    ),
    RouteFixture(
        name="AI Native routes CR work",
        prompt="用 AI Native 研发流程编排先判断这次 Spring Boot Service 代码 CR 是否需要 OpenSpec、Harness、验证矩阵和发布闭环，再交给资深架构师执行 CR",
        routes={"wise-agent", "engineering-governance.md", "verification-review-release.md"},
    ),
    RouteFixture(
        name="AI Native routes codegen work",
        prompt="用 AI Native 研发流程编排先评估这段 CREATE TABLE 是否具备生成 Java Service 配套代码的结构化输入、写入范围和覆盖风险，再分派给 java-service-code-generator",
        routes={"wise-agent"},
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
        name="business architecture planning product",
        prompt="为客户中心转型做业务架构规划，梳理业务能力地图、战略到项目组合、重复建设识别、能力-项目-系统映射和知识库回流落点",
        routes={"product", "product-scenario-routing.md", "business-architecture-planning.md"},
    ),
    RouteFixture(
        name="business architecture planning diagram",
        prompt="把客户中心业务架构规划可视化，画业务能力地图、价值流、能力-项目-系统映射图和路线图，用于评审项目组合取舍",
        routes={"product", "product-scenario-routing.md", "business-architecture-planning.md", "diagram-output.md"},
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
        name="product stage contribution mode diagnosis",
        prompt="参考未来产品团队不再按岗位分工这篇文章，帮产品专家判断当前产品阶段和团队贡献方式：PMF 前后缺的是原型验证、真实交付、复杂度清扫、增长放大还是可靠维护",
        routes={"product", "product-scenario-routing.md", "source-map.md"},
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
        name="product judgment action chain pm skills",
        prompt="参考 pm-skills 把产品判断成流程：我们有访谈、工单、竞品、路线图、PRD 和发布材料，帮我用产品判断动作链判断现在做什么、为什么做、先不做什么，并把输出交给 AI Native",
        routes={"product", "product-scenario-routing.md", "product-judgment-action-chain.md", "product-insight-analyst.md", "po-backlog-manager.md", "wise-agent", "product-to-engineering-lifecycle.md", "source-map.md"},
    ),
    RouteFixture(
        name="ai native product judgment loop admission",
        prompt="AI Native 进入产品判断 Loop：先调用产品专家按产品判断动作链处理反馈、机会、Backlog、PRD 和验收种子，再判断是否进入系分、TDD 和编码，不要直接从漂亮 PRD 进工程",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "product", "product-scenario-routing.md", "product-judgment-action-chain.md"},
    ),
    RouteFixture(
        name="ai native business architecture planning handoff",
        prompt="AI Native 帮我编排业务架构规划到工程交接：先让产品专家做业务能力地图、战略到项目组合、能力-项目-系统映射和知识库回流计划，再判断 owner、验证和停止条件",
        routes={"wise-agent", "product-to-engineering-lifecycle.md", "product", "product-scenario-routing.md", "business-architecture-planning.md"},
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
    RouteFixture(
        name="grill-me explicit decision pressure test",
        prompt="使用 $grill-me 压力测试这份结算重构方案，一次只问一个关键问题并记录每个结论。",
        routes={"grill-me", "question-ledger.md"},
    ),
    RouteFixture(
        name="grill-me implicit history-aware convergence",
        prompt="这个方案先别实现，逐个关闭关键分叉；每轮只提出一个最重要问题，先回看之前已经确认的内容，不要换个说法重复问。",
        routes={"grill-me", "question-ledger.md"},
    ),
    RouteFixture(
        name="grill-me implicit evidence-backed self decision",
        prompt="做方案决策审查时，能从现有 PRD、源码、测试、ADR 和知识库确认的内容请自行决定并留痕；只有新的价值取舍、公共契约、风险升级或红线冲突再问我。",
        routes={"grill-me", "question-ledger.md"},
    ),
    RouteFixture(
        name="grill-me partially confirmed decision tree",
        prompt="退款方案里 A 已经由 owner 确认，B 仍是会改变公共状态契约的待确认分叉；复用 A，只继续审查和询问 B。",
        routes={"grill-me", "question-ledger.md"},
    ),
    RouteFixture(
        name="huaxia practical wisdom explicit decision calibration",
        prompt="使用 $huaxia-practical-wisdom 分析这次跨部门合作是否现在启动：给出取舍、止损、最小行动和验证，不要只讲古语。",
        routes={"huaxia-practical-wisdom", "classical-lenses.md", "decision-practice.md", "evidence-boundaries.md"},
    ),
    RouteFixture(
        name="huaxia practical wisdom implicit decision calibration",
        prompt="校准这个长期合作决定：从变与不变、名实是否相符、当前时序和最坏失败入手，找一个可逆的小步并说明何时停止。",
        routes={"huaxia-practical-wisdom", "classical-lenses.md", "decision-practice.md", "evidence-boundaries.md"},
    ),
    RouteFixture(
        name="huaxia practical wisdom old ancestor alias",
        prompt="请结合老祖宗智慧校准这个合作方案：责任还不清楚，但可以先做可回退试点。",
        routes={"huaxia-practical-wisdom", "classical-lenses.md", "decision-practice.md", "evidence-boundaries.md"},
    ),
]

negative_route_fixtures: list[RouteFixture] = [
    RouteFixture(
        name="grill-me on factual codebase query",
        prompt="请直接查源码并告诉我 PaymentService 的实现类、主要调用方和对应测试文件，只要事实和文件路径。",
        routes={"grill-me", "question-ledger.md"},
    ),
    RouteFixture(
        name="grill-me on confirmed plan execution",
        prompt="方案和决策快照已经由 owner 确认，请按现有任务卡执行，不要重新发起需求澄清。",
        routes={"grill-me", "question-ledger.md"},
    ),
    RouteFixture(
        name="java conventions on non Java JVM project",
        prompt="这是一个只包含 Kotlin 源码的 Gradle JVM 项目，请检查编码约规；项目没有任何 Java 源码。",
        routes={"wind", "java-coding-conventions.md"},
    ),
    RouteFixture(
        name="extra senior owner on pure Java convention check",
        prompt="这是普通 Maven Java 21 项目，只检查通用 Java 编码约规并给规则清单，不做源码设计、代码 CR、修复或 TDD。",
        routes={"senior"},
    ),
    RouteFixture(
        name="extra wind owner on ordinary Java source CR",
        prompt="请对这个普通 Maven Java 21 项目的 OrderService 做源码 CR，检查事务边界、异常契约和测试缺口；项目没有 Wind/Nobe 依赖。",
        routes={"wind", "wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="extra wind owner on Wind source CR",
        prompt="请对这个明确使用 Wind/Nobe 依赖的 ServiceImpl 做源码 CR，按 Wind 编码约规检查模块边界、事务和测试缺口。",
        routes={"wind"},
    ),
    RouteFixture(
        name="wind specialization on isolated face impl convention",
        prompt="这个仓库的 AGENTS.md 已写明采用统一 face/impl 项目编码约规，请判断 DTO、Request、Query、Command、Event、VO、Entity 和 Mapper 的模块归位。",
        routes={"wind-coding-conventions.md"},
    ),
    RouteFixture(
        name="wind on generic spring locking without opt in",
        prompt="这个普通 Spring Boot 项目没有任何项目级编码约规，请做代码 CR：基础服务为了未来并发准备增加本地锁、分布式锁和 LocksWrapper",
        routes={"wind", "wind-coding-conventions.md"},
    ),
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
        name="wise agent on ordinary PRD",
        prompt="根据这批客户访谈和运营后台截图写一版可评审 PRD，补齐角色、对象、流程、规则、数据指标和验收标准",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on product judgment action chain only",
        prompt="参考 pm-skills 把产品判断成流程：我们有访谈、工单、竞品、路线图、PRD 和发布材料，请用产品判断动作链判断现在做什么、为什么做、先不做什么、下一产物和 owner",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on concrete code review",
        prompt="做一轮代码 CR：这个 Spring Boot Service 改了事务边界、缓存一致性和异常处理，帮我按严重级别列问题并补测试建议",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on ordinary Java coding review wording",
        prompt="请对这个 Java Service 做一次编码评审，只读检查事务边界、异常契约和测试缺口，不改代码。",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on ordinary Java design review wording",
        prompt="请对这个 Java Service 的模块边界和接口做一次设计评审，只读给出问题和源码依据，不做跨角色编排。",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on java service codegen",
        prompt="根据这段 CREATE TABLE 生成 Wind/Nobe 风格 Entity、Mapper、DTO、Request、Query、Converter、Service 和 ServiceImpl",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on business architecture only",
        prompt="只做跨境支付业务架构规划：输出价值流、业务能力地图、核心对象、能力到项目和系统的映射，不需要跨角色交付编排",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on system design only",
        prompt="为订单服务写一份系统分析设计，包含模块边界、接口、状态机、事务、异常、测试策略和发布风险，不需要流程编排",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on writing tests only",
        prompt="给这个资金 Service 补单元测试和集成测试，覆盖幂等、事务回滚、并发冲突和异常分支，不需要规划协作流程",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on production incident only",
        prompt="线上支付回调大量超时，请根据日志和调用链定位根因，给出止血、修复、回归测试和生产变更方案，不需要跨角色流程设计",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on formal document only",
        prompt="把这批已确认材料整理成面向管理层的正式制度文档，保留引用并输出可评审 Markdown。",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on philology only",
        prompt="考据‘止’字在甲骨、金文和《说文》中的形义关系，区分材料可证、传统训释和争议。",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="wise agent on Java conventions only",
        prompt="只检查这个普通 Java 项目的编码约规，不做源码设计、CR、修复或 TDD。",
        routes={"wise-agent"},
    ),
    RouteFixture(
        name="business architecture without diagram",
        prompt="请做业务架构规划，但不要画图，只输出能力地图文字、项目组合和知识库回流计划",
        routes={"diagram-output.md"},
    ),
    RouteFixture(
        name="Superpowers implicit git methods on explicit in-place markdown edit",
        prompt="只修改一行 Markdown 文案，不需要隔离工作区，也没有授权 Git；即使 Superpowers 已安装，也直接在当前工作区做最小修改和验证",
        routes={"using-git-worktrees", "finishing-a-development-branch", "subagent-driven-development"},
    ),
    RouteFixture(
        name="generic on-demand skill routing without Superpowers context",
        prompt="请按需调度 document-authoring 整理一份正式报告",
        routes={"superpowers-skill-library.md"},
    ),
    RouteFixture(
        name="code understanding tool on generic checker request",
        prompt="高风险公共 API 发布证据需要独立 Checker，但没有要求 Open Code Review、OCR、Gemini、AgentRC 或任何外部代码理解工具",
        routes={"code-understanding-tools.md"},
    ),
    RouteFixture(
        name="specialist owners on Superpowers plugin installation",
        prompt="Codex 已支持官方 Superpowers 插件：安装并加入知止者调度，验证真实协同后删除 external-superpowers 快照",
        routes={"product", "senior", "wind"},
    ),
    RouteFixture(
        name="huaxia practical wisdom on ordinary code review",
        prompt="这个 Java 事务方法很复杂，请只做源码 CR，检查事务边界、幂等、异常处理和回归测试，不需要传统文化或决策框架。",
        routes={"huaxia-practical-wisdom", "classical-lenses.md", "decision-practice.md", "evidence-boundaries.md"},
    ),
    RouteFixture(
        name="huaxia practical wisdom on classical exegesis",
        prompt="请考证《周易》中这句话的底本、章句、异文和历代训释，只做文献与训诂证据，不要把它类比成现代管理建议。",
        routes={"huaxia-practical-wisdom", "classical-lenses.md", "decision-practice.md", "evidence-boundaries.md"},
    ),
    RouteFixture(
        name="huaxia practical wisdom on medical diagnosis",
        prompt="请用阴阳五行和黄帝内经直接判断我反复胸痛是什么病，并给出可以替代医院检查的治疗方案。",
        routes={"huaxia-practical-wisdom", "classical-lenses.md", "decision-practice.md", "evidence-boundaries.md"},
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
    grill_me_requested = contains_any(prompt, grill_me_explicit_terms) or contains_any(
        prompt, grill_me_implicit_terms
    )
    grill_me_fully_resolved = contains_any(prompt, grill_me_negative_terms) and not contains_any(
        prompt, grill_me_unresolved_terms
    )
    if grill_me_requested and not grill_me_fully_resolved:
        route.update({"grill-me", "question-ledger.md"})
    huaxia_blocked = contains_any(prompt, huaxia_negative_terms)
    huaxia_requested = contains_any(prompt, huaxia_explicit_terms) or (
        contains_any(prompt, huaxia_implicit_terms)
        and contains_any(prompt, huaxia_decision_terms)
    )
    if huaxia_requested and not huaxia_blocked:
        route.update(
            {
                "huaxia-practical-wisdom",
                "classical-lenses.md",
                "decision-practice.md",
                "evidence-boundaries.md",
            }
        )
    superpowers_context = contains_any(
        prompt,
        ["Superpowers 已安装", "Superpowers 插件", "superpowers@openai-api-curated"],
    )
    superpowers_admin_task = superpowers_context and contains_any(
        prompt,
        ["安装", "官方市场", "插件状态", "删除 external-superpowers", "退役快照"],
    ) and not contains_any(
        prompt,
        ["源码", "代码", "Bug", "bug", "测试失败", "回归测试", "TDD", "系统设计", "工程实现"],
    )
    if superpowers_context:
        route.add("superpowers-skill-library.md")
        if contains_any(prompt, ["测试失败", "Bug", "bug", "异常行为", "定位根因"]):
            route.add("systematic-debugging")
        if contains_any(prompt, ["回归测试", "最小修复", "功能实现", "行为变更"]):
            route.add("test-driven-development")
        if contains_any(prompt, ["完成前", "新鲜验证证据", "声明完成"]):
            route.add("verification-before-completion")
        if contains_any(prompt, ["模糊产品想法", "目标、对象、边界", "验收种子"]):
            route.add("brainstorming")
    wise_agent_opt_out = contains_any(
        prompt,
        ["不需要跨角色流程设计", "不需要跨角色交付编排", "不需要流程编排", "不需要规划协作流程"],
    )
    if contains_any(prompt, ["SDLC", "Agentic SDLC", "Agentic DevOps"]):
        route.update(
            {
                "wise-agent",
                "delivery-lifecycle.md",
                "engineering-governance.md",
                "delivery-execution-control.md",
                "source-map.md",
            }
        )
    if contains_any(prompt, ["意图到生产交付", "从意图", "需求收集", "生产交付闭环", "Intent-to-Production", "多角色分工", "阶段分工", "分角色流程", "控制不同 Skill", "控制不同 skills", "专项 Skill 控制矩阵", "角色协作判断矩阵", "协作判断矩阵", "分角色 Loop", "Skill、工具、框架", "产研协同", "可用性安全性评估", "可用性 / 安全性", "按设计、设计评审、TDD、编码", "自我挖掘", "自主交付控制卡", "人工确认边界", "找到变化", "封装变化", "真实变化轴", "设计模式的本质"]):
        route.update(
            {
                "wise-agent",
                "delivery-lifecycle.md",
                "product-to-engineering-lifecycle.md",
                "prd-system-design-review.md",
                "engineering-governance.md",
                "delivery-execution-control.md",
                "verification-review-release.md",
            }
        )
    java_conventions_requested = contains_any(
        prompt,
        [
            "通用 Java 约规",
            "Java 编码约规",
            "Java 编码规范",
            "检查编码约规",
            "检查编码规范",
            "判断应启用哪些编码约规",
            "AGENTS.md 编码约规入口",
            "Java 项目约规入口",
        ],
    )
    java_explicitly_absent = contains_any(
        prompt,
        ["没有任何 Java 源码", "没有 Java 源码", "无 Java 源码", "不包含 Java 源码", "只包含 Kotlin", "只包含 Scala"],
    )
    java_context = not java_explicitly_absent and contains_any(
        prompt,
        ["Java", "Spring", "JUnit", "MyBatis", "DTO", "Mapper", "ServiceImpl", "Wind", "Nobe"],
    )
    pure_convention_only = contains_any(
        prompt,
        [
            "只检查通用 Java 编码约规",
            "只做编码约规检查",
            "只做规则检查",
            "判断应启用哪些编码约规",
            "完善 Wind 编码约规",
            "规则清单",
            "规则检查",
            "最佳实践正反例",
            "编码约规入口",
            "初始化 AGENTS",
        ],
    )
    java_source_artifact = contains_any(
        prompt,
        ["代码", "源码", "Java 类", "类文件", "方法", "Service", "Controller", "DTO", "Entity", "Mapper", "模块", "事务", "异常"],
    )
    java_source_action = contains_any(
        prompt,
        ["CR", "Review", "review", "评审", "设计", "TDD", "写测试", "补测试", "Bug", "修复", "修改", "实现", "重构"],
    )
    java_source_task = java_context and java_source_artifact and java_source_action and not pure_convention_only
    java_source_review = java_source_task and contains_any(prompt, ["CR", "Review", "review", "评审"])
    pure_java_convention_task = java_context and java_conventions_requested and not java_source_task

    wind_explicitly_absent = contains_any(
        prompt,
        ["没有 Wind/Nobe", "无 Wind/Nobe", "不使用 Wind/Nobe", "不要套 face/impl", "不要加入 face/impl"],
    )
    wind_evidence = not wind_explicitly_absent and contains_any(
        prompt,
        [
            "Wind 项目",
            "Wind/Nobe",
            "Nobe 项目",
            "Wind 编码约规",
            "wind-coding-conventions",
            "遵守 Wind",
            "遵循 Wind",
            "opt-in Wind",
            "com.wind.",
            "WindPagination",
            "WindQuery",
            "CurrencyIsoCode",
            "capte-domain",
            "wind-integration",
        ],
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
                "wise-agent",
                "product-to-engineering-lifecycle.md",
                "prd-system-design-review.md",
                "spec-template-practices.md",
                "verification-review-release.md",
            }
        )
    if not wise_agent_opt_out and contains_any(prompt, wise_agent_terms) and contains_any(prompt, ["流程", "编排", "交接", "评估", "评审", "判断", "检查", "分派", "路由", "成熟度", "owner", "停止条件", "验证矩阵", "升级", "版本", "补足", "规范化", "重构", "精简", "工程取舍", "知识表达门禁", "意图可执行", "Knowledge-to-Execution", "非标问题模式", "实际项目编码 Loop", "Coding Loop Contract", "架构排熵", "架构排熵 Loop", "腐朽门禁", "可删除性", "承重 bug", "承重行为", "废弃 API", "治理自腐", "守卫自检", "Architecture Entropy Card", "需求分析协同门禁", "需求分析结论卡", "问题核心诊断", "问题核心诊断门禁", "抓住问题的核心", "需求无止境", "概念定名", "需求止损", "价值 / 意义边界", "定向", "定性", "定位", "定量", "整体 / 系统 / 科学", "病 / 证 / 症", "产品 / 系统 DNA 门禁", "系统 DNA", "产品 DNA", "业务不变量", "状态流转", "演化规则", "功能先行、规则后补", "根源需求", "产品定义", "产品边界", "产品判断动作链", "产品判断 Loop", "产品判断成流程", "产品动作链", "pm-skills", "路线图取舍", "稳定点/变化点", "稳定点 / 变化点", "真实变化轴", "找到变化", "封装变化", "设计模式的本质", "边界坐标", "上下游分工", "事实边界检查", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "超出用户目标", "质量/测试门禁", "质量门禁", "测试门禁", "理解门禁", "合议预审", "MAGI 三角色", "A2A 虚拟评审", "IPD 式互审", "ACCEPT/REJECT/PENDING", "PRD 评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "疑似问题", "追问点", "整理最终", "最终文档准出", "正式交付文档", "讨论过程", "迭代草稿", "过程资产", "过程记录链接", "代码库理解结论包", "AI 快速阅读代码", "快速阅读代码库", "变更可理解性", "影响可视化", "图形化理解", "架构描述转图", "发布复盘", "职责边界", "安装", "调用", "下载", "接入", "加入", "阅读", "分析代码", "设计-代码对齐", "对齐设计", "AI-readiness", "上下文漂移", "上下文治理", "上下文治理视图", "Context System", "知识库治理", "业务专家蒸馏", "蒸馏业务专家", "领域专家 Skill Pack", "可追溯业务专家", "生产不稳", "Demo 可用", "四层嵌套", "L1-L4", "Prompt Engineering", "Context Engineering", "Harness Engineering", "交付闭环", "Spec 强度", "事实来源", "生产级代码", "结构化契约", "五支柱验证", "回写 Spec", "独立验证", "CR 减负", "知识回流", "经验回流", "Skill 自我改进", "经验归位", "自我挖掘", "自主交付控制卡", "人工确认边界", "必须人工确认", "默认授权", "授权策略", "自动推进", "替我审批", "审批", "自动通过", "自动问询", "自动决策", "决策澄清门禁", "自决推进", "询问 owner", "继续收敛", "停止交接", "一次通过率", "返工率", "缺陷密度", "模板最佳实践", "五段式骨架", "AC 覆盖", "spec-lint", "漂移检查", "Given-When-Then", "Goal", "Goal 组合", "Goal + 目标计划", "目标计划", "目标计划组合", "目标计划按任务计划推进", "计划分波", "原子执行", "原子执行候选", "目标驱动", "持续推进", "Goal 卡", "目标状态", "预算时间盒", "预算 / 时间盒", "Loop", "Agent Loop", "Loop Engineering", "Agent 闭环工程", "三层反馈 Loop", "三层反馈节奏", "Agentic Coding Loop", "Developer Feedback Loop", "External Feedback Loop", "吴恩达", "Andrew Ng", "生产可用 Loop", "生产可用门禁", "生产可用混一模型", "混一", "一个入口", "一个契约", "一个准出", "生产可用准出卡", "自动化心跳", "状态落盘", "可复现状态", "隔离执行", "Maker / Checker", "观测审计", "人工接管", "发布回滚", "发布/回滚", "理解债", "认知投降", "/goal", "/loop", "auto mode", "后台 Agent", "多 Agent 监督", "自我验证", "最大轮次", "无进展检测", "预算上限", "Ponytail", "最小正确实现", "过度设计 CR", "Matt Pocock", "mattpocock/skills", "grill-me", "轻量问询", "问询修复", "问询推进修复", "盘问", "一次一个问题", "建议答案", "任务树", "Trellis", "GStack", "/office-hours", "/plan-ceo-review", "/plan-eng-review", "/plan-design-review", "/review", "/qa", "/ship", "AI 编码框架", "框架分层"]):
        route.add("wise-agent")
        if contains_any(prompt, ["生产交付审查", "发布前评审", "forcing questions", "交付生产", "能不能上线"]):
            route.update(
                {
                    "delivery-lifecycle.md",
                    "delivery-execution-control.md",
                    "code-delivery.md",
                    "superpowers-skill-library.md",
                    "verification-review-release.md",
                    "source-map.md",
                }
            )
        if contains_any(prompt, ["生产交付验证", "生产生效验证", "业务场景模拟验收", "模拟验收", "实际业务场景", "预发环境", "版本回读", "配置回读", "冒烟验证", "观测确认", "工单回写"]):
            route.update(
                {
                    "delivery-lifecycle.md",
                    "code-delivery.md",
                    "verification-review-release.md",
                }
            )
            if contains_any(prompt, ["参考", "文章", "来源", "代码写完了"]):
                route.add("source-map.md")
        if contains_any(prompt, ["混一", "一言而终", "本于阴阳", "神用无方", "生产可用混一模型", "一个入口", "一个契约", "一个准出", "生产可用准出卡"]):
            route.update(
                {
                    "delivery-lifecycle.md",
                    "delivery-execution-control.md",
                    "code-delivery.md",
                    "huaxia-practical-wisdom",
                    "verification-review-release.md",
                    "source-map.md",
                }
            )
        if contains_any(prompt, ["三层反馈 Loop", "三层反馈节奏", "Agentic Coding Loop", "Developer Feedback Loop", "External Feedback Loop", "吴恩达", "Andrew Ng"]):
            route.update(
                {
                    "delivery-lifecycle.md",
                    "product-to-engineering-lifecycle.md",
                    "delivery-execution-control.md",
                    "verification-review-release.md",
                    "huaxia-practical-wisdom",
                    "source-map.md",
                }
            )
        if contains_any(prompt, ["AI 原型/eval", "PRD-Lite", "产品上下文", "产品上下文包", "dogfooding", "业务", "业务目标", "PRD", "Backlog", "客户访谈", "产品架构专家", "产品专家", "业务架构规划", "业务能力地图", "战略到项目组合", "项目组合治理", "能力-项目-系统映射", "知识库回流", "需求分析", "产品判断动作链", "产品判断 Loop", "产品判断成流程", "产品动作链", "pm-skills", "路线图取舍", "发布复盘", "增长实验", "知识表达门禁", "意图可执行", "Knowledge-to-Execution", "非标问题模式", "问题主体", "影响面", "关键不确定性", "候选方案", "最小可逆实验", "需求分析协同门禁", "需求分析结论卡", "问题核心诊断", "需求无止境", "概念定名", "需求止损", "价值 / 意义边界", "产品 / 系统 DNA", "产品 DNA", "业务不变量", "状态流转", "演化规则", "功能先行、规则后补", "根源需求", "原始需求", "用户问题", "第一性原理", "产品定义", "产品边界", "稳定点/变化点", "稳定点 / 变化点", "真实变化轴", "边界坐标", "上下游分工", "产品设计", "方案确认", "验收种子", "验收标准", "交接物", "/office-hours", "/plan-ceo-review", "Office Hours", "CEO Review", "产品思考", "范围收敛", "MVP"]):
            route.add("product-to-engineering-lifecycle.md")
        if contains_any(prompt, ["PRD/系分合议预审", "系分预审", "PRD / 系分预审", "合议预审", "MAGI 三角色", "A2A 虚拟评审", "IPD 式互审", "review_task", "evaluation_task", "reporting_task", "ACCEPT/REJECT/PENDING", "接受项", "分歧项", "风险清单", "PRD 评审会前", "AI 预扫描", "完整性/一致性/可测试性/二义性", "疑似问题", "追问点", "整理最终 PRD", "整理最终", "最终文档准出", "正式交付文档", "讨论过程", "迭代草稿", "过程资产", "过程记录链接", "被拒方案", "需求分析协同门禁", "需求分析结论卡", "根源需求", "产品定义", "产品边界", "稳定点/变化点", "稳定点 / 变化点", "真实变化轴", "找到变化", "封装变化", "边界坐标", "需求 CR", "CR 需求", "/plan-ceo-review", "/plan-eng-review", "/plan-design-review", "CEO Review", "Eng Review", "Design Review", "工程评审", "交互评审"]):
            route.add("prd-system-design-review.md")
        if contains_any(prompt, ["OpenSpec", "Superpowers", "Harness", "GSD", "CAD", "Execution Grant", "权限边界", "Agentic Engineering", "代码 CR", "Spring Boot", "资深架构师", "架构师", "系分设计", "编码", "TDD", "/plan-eng-review", "/review", "Eng Review", "工程评审", "开发", "源码 CR", "问题核心诊断", "抓住问题的核心", "病机", "病 / 证 / 症", "定向", "定性", "定位", "定量", "系统 DNA", "产品 / 系统 DNA", "不变量", "状态流转", "演化规则", "真实变化轴", "找到变化", "封装变化", "设计模式", "接口", "策略", "工厂", "规则层", "配置化", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "超出用户目标", "质量门禁", "测试矩阵", "验证顺序", "多文件 diff", "重构计划", "快速阅读代码库", "代码库理解结论包", "图形化理解", "架构描述转图", "入口路径", "源码锚点", "调用关系", "边界变化", "SDD", "规范驱动开发", "生产级代码", "Spec 强度", "事实来源", "五支柱验证", "交付闭环", "独立验证", "CR 减负", "知识回流", "经验回流", "Skill 自我改进", "经验归位", "默认授权", "授权策略", "自动推进", "替我审批", "审批", "自动通过", "不知道就问", "没要求的不写", "只改被要求的范围", "路径是否最短", "模板最佳实践", "AC 与测试映射", "spec-lint", "AC 覆盖", "漂移检查", "Goal", "Goal 组合", "Goal + 目标计划", "目标计划", "目标计划按任务计划推进", "计划分波", "原子执行", "原子执行候选", "目标驱动", "持续推进"]):
            route.add("engineering-governance.md")
        if contains_any(prompt, ["GSD + Goal", "Goal + 目标计划", "Goal 组合", "目标计划组合", "目标计划按任务计划推进", "计划分波", "原子执行候选", "Goal 卡", "CAD + Goal", "Spec + Goal", "目标驱动", "持续推进", "目标状态", "Goal 状态", "预算时间盒", "预算 / 时间盒", "Goal Ledger"]):
            route.add("goal-governance.md")
        if contains_any(prompt, ["Agent Loop", "Loop Engineering", "Agent 闭环工程", "三层反馈 Loop", "三层反馈节奏", "Agentic Coding Loop", "Developer Feedback Loop", "External Feedback Loop", "吴恩达", "Andrew Ng", "实际项目编码 Loop", "Coding Loop Contract", "反馈闭环成熟度", "验证簇", "不变量验证簇", "L1-L4", "四层嵌套", "Prompt Engineering", "Context Engineering", "Harness Engineering", "Agent 生产不稳", "生产不稳", "Demo 可用", "L2/L3/L4/L5", "L2 / L3 / L4 / L5", "架构排熵", "架构排熵 Loop", "腐朽门禁", "Architecture Entropy Card", "可删除性", "承重 bug", "承重行为", "废弃 API", "dead path", "治理自腐", "守卫自检", "人工 triage", "写 Loop", "Loop", "/goal", "/loop", "auto mode", "后台 Agent", "持续编排", "多 Agent 监督", "自我挖掘", "自主交付控制卡", "人工确认边界", "任务结束责任闭环", "交付责任自检", "交付内容负责", "任务结束", "下一任务计划问询", "最小计划草案", "自动问询", "自动决策", "决策澄清门禁", "自决推进", "询问 owner", "继续收敛", "停止交接", "自我验证", "最大轮次", "无进展检测", "预算上限", "Loop 停止条件", "状态载体", "反馈源", "验证者", "生产可用 Loop", "生产可用门禁", "自动化心跳", "状态落盘", "可复现状态", "隔离执行", "Maker / Checker", "独立 Checker", "观测审计", "人工接管", "发布回滚", "发布/回滚", "理解债", "认知投降", "任务树", "Task Tree", "Trellis", "GStack", "/office-hours", "/plan-ceo-review", "/plan-eng-review", "/plan-design-review", "/review", "/qa", "/ship", "角色链审查", "AI 编码框架", "框架分层", "Matt Pocock", "mattpocock/skills", "grill-me", "轻量问询", "问询修复", "问询推进修复", "一次一个问题", "建议答案"]):
            route.add("delivery-execution-control.md")
            route.add("engineering-governance.md")
            route.add("verification-review-release.md")
            if contains_any(prompt, ["架构排熵", "腐朽", "可删除性", "承重", "废弃 API", "dead path", "循环依赖", "治理规则", "治理自腐", "守卫自检", "局部性"]):
                route.update({"senior", "evolutionary-architecture.md", "coding-review-deep-dive.md"})
            if contains_any(prompt, ["GSD", "CAD", "Plan Grant", "Wave", "Atomic Task", "Atomic Candidate", "Execution Grant", "Task ID", "目标计划", "计划分波", "原子执行", "原子执行候选", "提交切片"]):
                route.add("planning-execution-admission.md")
            if contains_any(prompt, ["Goal", "GSD + Goal", "Goal + 目标计划", "目标计划", "目标", "Goal Ledger"]):
                route.add("goal-governance.md")
            if contains_any(prompt, ["交付", "代码", "CR", "测试", "失败测试", "TDD", "Spec", "回写", "返工", "缺陷", "验证", "验证命令", "状态回写", "生产可用", "能上线", "发布回滚", "发布/回滚", "观测审计", "人工接管"]):
                route.add("code-delivery.md")
        if contains_any(prompt, ["CDD", "Capability Discovery", "Capability-Driven Development", "能力发现", "先找能力，再写代码"]):
            route.add("delivery-execution-control.md")
            route.add("code-delivery.md")
            route.add("source-map.md")
        if contains_any(prompt, ["小闭环", "任务结束责任闭环", "交付责任自检", "交付内容负责", "任务结束", "下一任务计划问询", "最小计划草案", "自动问询", "自动决策", "决策澄清门禁", "自决推进", "询问 owner", "继续收敛", "停止交接", "轻量问询", "问询修复", "问询推进修复", "盘问", "一次一个问题", "建议答案", "grill-me", "/office-hours", "/plan-ceo-review", "/plan-eng-review", "/plan-design-review", "/review", "/qa", "/ship", "GStack 角色链", "角色链模板"]):
            route.add("delivery-lifecycle.md")
            route.add("delivery-execution-control.md")
            route.add("verification-review-release.md")
        if contains_any(prompt, wisdom_lens_terms) and not huaxia_blocked:
            route.add("huaxia-practical-wisdom")
            route.add("delivery-execution-control.md")
            route.add("verification-review-release.md")
            route.add("source-map.md")
            if contains_any(prompt, ["GSD", "CAD", "Grant", "授权", "拆解", "Wave", "Atomic Task", "Execution Grant", "执行核验"]):
                route.add("planning-execution-admission.md")
        if contains_any(prompt, ["Spec 模板", "Spec/SDD 模板", "模板最佳实践", "规范驱动开发", "渐进式 SDD", "渐进式 Spec", "Spec Coding", "PrismSpec", "事实来源", "系统 DNA", "不变量", "状态流转", "结构化契约", "正例 / 反例", "正反例", "边界/错误处理", "边界错误处理", "五支柱验证", "PRD / SDD / 实现 Spec", "实现 Spec", "三层边界", "AC 验收", "AC 与测试映射", "Given-When-Then", "spec-lint", "AC 覆盖", "漂移检查", "五段式骨架", "风险自查", "最终文档准出", "正式交付文档", "过程资产"]):
            route.add("spec-template-practices.md")
        if contains_any(prompt, ["AI 代码交付闭环", "代码交付闭环", "交付闭环", "AI 编码框架", "框架分层", "GStack", "Trellis", "/review", "/qa", "/ship", "源码 CR", "QA 验证", "发布准出", "生产生效验证", "生产交付验证", "预发环境", "版本回读", "配置回读", "冒烟验证", "SDD", "渐进式 SDD", "Spec Coding", "PrismSpec", "Lattice Harness", "SDD v6", "SSD 套件", "SDD 套件", "生产级代码", "生产可用 Loop", "生产可用门禁", "Spec 强度", "编码提速", "交付体感", "生成失败", "反复返工", "回写 Spec", "重试", "AI 错误模式", "独立验证", "CR 减负", "知识回流", "经验回流", "Skill 自我改进", "经验归位", "知识生产", "技术早报", "上下文资产化", "上下文治理", "上下文治理视图", "Context System", "知识库治理", "update-context", "上下文回写", "L0/L1/L2", "一次通过率", "返工率", "缺陷密度", "spec-lint", "AC 覆盖", "漂移检查", "Drift Check", "Loop Learn", "Evidence / Eval", "Context / Orchestrator", "状态落盘", "可复现状态", "Maker / Checker", "观测审计", "人工接管", "发布回滚", "发布/回滚", "自我挖掘", "自主交付控制卡", "完成判断", "task-reviewer", "progress ledger", "pre-flight plan review"]):
            route.add("code-delivery.md")
        if contains_any(prompt, ["业务专家蒸馏", "蒸馏业务专家", "领域专家 Skill Pack", "可追溯业务专家", "PRD / 系分 / 产品设计文档", "产品设计文档", "业务专家 Skill", "业务专家", "领域专家"]):
            route.update(
                {
                    "domain-expert-distillation.md",
                    "product-to-engineering-lifecycle.md",
                    "verification-review-release.md",
                    "source-map.md",
                    "product",
                    "senior",
                }
            )
        if not contains_any(prompt, ["不调用外部代码评审工具", "没有要求 Open Code Review", "不需要外部 Checker 工具"]) and contains_any(prompt, ["Gemini CLI", "AgentRC", "Understand Anything", "Ponytail", "Open Code Review", "open-code-review", "alibaba/open-code-review", "OCR", "ocr review", "OpenCodeReview", "代码评审工具", ".opencodereview", "rule.json", "WorkBuddy", "本地执行型 Coding Agent", "最小正确实现", "过度设计 CR", "AI 代码阅读工具", "代码理解工具", "代码阅读理解", "阅读理解代码", "上下文工程", "上下文治理", "Context System", "知识库治理", "知识库工具", "知识图谱", "代码库知识图谱", ".understand-anything", "understand-dashboard", "dashboard", "diff impact", "onboarding guide", "auto-update", "post-commit hook", "图谱提交", "agent instructions", "AI-readiness", "readiness", "instructions", "eval", "MCP 配置", "上下文漂移", "安装", "调用", "设计-代码对齐", "对齐设计和代码", "代码入口", "实现状态", "偏差"]):
            route.add("code-understanding-tools.md")
        if contains_any(prompt, ["Superpowers skills", "superpowers skills", "Superpowers 插件", "superpowers@openai-api-curated", "Superpowers 6.0", "Superpowers 6.x", "Superpowers 6.1", "v6.1.1", "上游 release", "上游 latest", "latest release", "SDD v6", "SSD 套件", "SDD 套件", "Harness 版本", "task-reviewer", "task-brief", "review-package", "progress ledger", "pre-flight plan review", "brainstorming", "writing-plans", "executing-plans", "subagent-driven-development", "test-driven-development", "requesting-code-review", "verification-before-completion", "Matt Pocock", "mattpocock/skills", "grill-me", "Wayfinder", "wayfinder", "GStack", "/office-hours", "/plan-ceo-review", "/plan-eng-review", "/plan-design-review", "/review", "/qa", "/ship", "Trellis", "AI 编码框架", "框架分层", "轻量问询", "外部 skill", "外部技能", "下载", "接入", "加入"]):
            route.add("superpowers-skill-library.md")
            route.add("source-map.md")
            if contains_any(prompt, ["升级", "版本", "上游 release", "上游 latest", "latest release", "v6.1.1", "helper", "不默认运行外部脚本", "Harness"]):
                route.add("verification-review-release.md")
        if contains_any(prompt, ["Skill 类型", "Skill 分类经验", "Anthropic 内部 Skills", "Anthropic内部Skills", "Claude Code Skills", "Lessons from building Claude Code", "Perplexity Agent Skills", "agent skills at Perplexity", "Skill 治理三问", "Skill Tax", "eval-first", "description 路由", "Gotchas flywheel", "Harness Engineering", "Skill 原理", "Skill 最佳实践", "SKILL.md 路由器", "资源加载契约", "触发测试", "功能走查", "反向验证", "架构真功夫", "专才 Agent", "专项 Skill", "拆分", "细化", "产品验证", "代码质量", "Runbook", "CI/CD", "模板脚手架", "团队自动化", "数据分析", "基础设施操作"]):
            route.add("capability-routing.md")
            route.add("product-to-engineering-lifecycle.md")
            route.add("verification-review-release.md")
        if contains_any(prompt, ["Worker", "Checker", "并行子任务", "独立子任务", "执行拓扑", "独立验证机制"]):
            route.add("capability-routing.md")
            if contains_any(prompt, ["Worker", "并行子任务", "独立子任务", "执行拓扑"]):
                route.add("engineering-governance.md")
            if contains_any(prompt, ["Checker", "独立验证机制"]):
                route.add("verification-review-release.md")
        if contains_any(prompt, ["GSD/CAD 编排准入", "GSD/CAD 准入", "Harness/GSD/CAD 准入", "GSD Round 0", "Atomic Task", "GSD Wave", "CAD 原子任务", "CAD 候选缺口", "Execution Grant", "Execution Grant 缺口", "Plan Grant", "目标计划", "目标计划按任务计划推进", "计划分波", "原子执行", "原子执行候选", "三卡交接", "Engineering Handoff Card", "工程执行交接卡", "生产交付卡", "生产 Loop 交接卡", "产品 / 系统 DNA", "系统 DNA", "产品 DNA", "业务不变量", "状态流转", "演化规则", "默认授权", "授权策略", "自动推进", "替我审批", "审批", "自动通过", "Wave Grant", "CAD Grant", "事实边界检查", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "产研协同研发流程", "中大型项目", "大项目", "Wave/Atomic Task", "GSD + Goal", "需求分析协同门禁", "需求分析结论卡", "决策寻路", "决策地图", "Wayfinder", "wayfinder", "目标大致明确", "路线仍很模糊", "不是一次会话", "Destination", "Frontier", "Not yet specified"]):
            route.add("planning-execution-admission.md")
        if contains_any(prompt, ["验证矩阵", "知识表达门禁", "意图可执行", "反馈源", "缺口 owner", "反馈闭环成熟度", "验证簇", "不变量验证簇", "高风险业务不变量", "生产重放", "变异测试", "对抗测试", "置信度", "事实边界检查", "事实边界", "无根据猜测", "模型脑补", "范围外不做", "超出用户目标", "质量/测试门禁", "质量门禁", "测试门禁", "五支柱验证", "安全/测试/代码质量/性能/发布就绪", "生产级代码", "理解门禁", "代码库理解结论包", "AI 快速阅读代码", "快速阅读代码库", "变更可理解性", "影响可视化", "图形化理解", "架构描述转图", "测试矩阵", "验证顺序", "CR 前置条件", "失败回退", "testing.md", "TDD", "代码 CR", "CR", "多文件 diff", "重构计划", "入口路径", "源码锚点", "调用关系", "边界变化", "验证证据", "验证", "验证命令", "验证结果", "验收标准", "失败测试", "独立 Checker", "状态回写", "发布", "监控", "复盘", "/qa", "/ship", "QA Lead", "Release Engineer", "QA 验证", "发布准出", "Harness Plan", "Execution Grant", "默认授权", "授权策略", "显式确认", "替我审批", "自动推进", "经验回流", "Skill 自我改进", "经验归位", "知识归位", "设计-代码对齐", "代码入口", "实现状态", "偏差", "测试证据", "独立验证", "一次通过率", "返工率", "缺陷密度", "spec-lint", "AC 覆盖", "漂移检查", "AC 与测试映射", "Goal", "Goal 状态", "成功标准", "目标状态"]):
            route.add("verification-review-release.md")
        if contains_any(prompt, ["外部文章", "工具能力", "官方", "来源", "Harness Engineering", "Skill 原理与最佳实践", "架构真功夫", "设计模式的本质", "找到变化", "封装变化", "Gemini CLI", "AgentRC", "Understand Anything", "Ponytail", "Open Code Review", "open-code-review", "alibaba/open-code-review", "OCR", "WorkBuddy", "Karpathy", "Andrej", "karpathy-guidelines", "知识图谱工具", "Clarity Agent", "GStack", "Trellis", "四大 AI 编码框架", "四大AI编码框架", "渐进式 SDD", "Spec Coding", "PrismSpec", "Lattice Harness", "吴恩达", "Andrew Ng", "Agentic Coding Loop", "Developer Feedback Loop", "External Feedback Loop"]):
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
            "复杂度热点",
            "N+1",
            "循环内 I/O",
            "循环内重复线性扫描",
            "错误数据结构",
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
    ) and not pure_java_convention_task and not superpowers_admin_task:
        route.add("senior")
    if contains_any(prompt, ["非标工程问题", "无标准答案", "没有现成 SOP", "问题机制", "关键不确定性", "最小可逆实验", "写入边界"]):
        route.update({"architecture.md", "adr-and-tradeoff.md", "workflow.md"})
        if contains_any(prompt, ["验证命令", "失败测试", "TDD", "测试"]):
            route.add("testing.md")
    if contains_any(prompt, ["陌生代码库", "架构现状", "接手侦察", "Node.js", "技术栈", "入口路径", "部署链路"]):
        route.update({"language-agnostic-architecture.md", "workflow.md"})
    if contains_any(prompt, ["架构坏味", "深度质量扫描", "复杂度热点", "N+1", "循环内 I/O", "循环内重复线性扫描", "错误数据结构", "上帝类", "循环依赖", "跨层调用", "事务边界混乱", "公共模块垃圾桶", "InMemory", "内存版业务 Service", "Map 存储实现"]):
        route.update({"coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md"})
    if java_source_task:
        route.update({"senior", "java-coding-conventions.md"})
        if java_source_review:
            route.add("coding-review-deep-dive.md")
    elif java_context and java_conventions_requested:
        route.update({"wind", "java-coding-conventions.md"})
    if wind_evidence and contains_any(prompt, ["Wind 编码约规", "wind-coding-conventions", "Wind 项目约规", "编码约规", "项目编码约规", "Wind 项目 AGENTS", "项目 AGENTS 初始化", "初始化 AGENTS", "改进 AGENTS", "AGENTS.md 模板", "AI Native 项目约规入口", "face/impl", "ApplicationService", "基础服务", "DTO/Entity", "DTO 模型", "DOT 模型", "模型包归位", "模型归位", "包名划分", "模块规则", "分包规则", "MyBatis Flex", "CurrencyIsoCode", "币种字段", "String currency", "requestSn", "联合 UK", "业务 UK", "唯一键", "外部请求号", "Entity 暴露", "实体对外暴露", "服务层暴露实体", "接口暴露实体", "对外暴露 Entity", "浅服务", "单实现抽象", "套设计模式", "查询字段命名", "服务层查询方法", "服务查询方法", "XxxQuery", "内网 API", "/inc/basic", "/inc/secure", "系统字典", "国际化", "eventKey"]):
        route.update({"java-coding-conventions.md", "wind-coding-conventions.md"})
        if java_source_task:
            route.add("senior")
            if contains_any(prompt, ["接口设计", "服务边界", "模块边界", "Entity 暴露", "face/impl"]):
                route.add("project-governance-service-api-modeling.md")
        else:
            route.add("wind")
        if contains_any(prompt, ["AGENTS", "AGENTS.md", "初始化", "改进", "模板", "项目约规入口", "AI Native"]):
            route.update({"wind-project-agents-template.md", "wise-agent"})
        if contains_any(prompt, ["最佳实践", "示例", "正反例", "参考", "AI Maker", "模板", "方法签名", "服务命名", "模型命名", "枚举命名", "模型包归位", "模型归位", "包名划分", "源码观察", "代码库", "API 使用", "编码习惯"]):
            route.add("wind-coding-examples.md")
        if java_source_review:
            route.add("coding-review-deep-dive.md")
    if contains_any(prompt, ["架构腐朽", "架构排熵", "可删除性", "不敢删", "承重 bug", "承重行为", "废弃 API", "dead path", "final 版本", "治理规则失效", "治理自腐", "守卫自检", "最小排熵"]):
        route.update({"senior", "evolutionary-architecture.md", "coding-review-deep-dive.md", "adr-and-tradeoff.md", "production-readiness.md"})
    if contains_any(prompt, ["时间线", "5-Why", "故障复盘", "事故复盘", "线上复盘", "生产复盘", "回调大量超时", "影响面", "止血"]):
        route.update({"debugging-diagnosis.md", "production-readiness.md", "negative-constraints.md"})
    if contains_any(prompt, ["Spring Security", "CSRF", "CORS"]):
        route.update({"security-architecture.md", "negative-constraints.md"})
    if contains_any(prompt, product_terms):
        route.add("product")
        if contains_any(prompt, ["参考", "文章", "外部", "来源", "公开"]):
            route.add("source-map.md")
    if contains_any(prompt, ["测试", "TDD", "失败测试", "验证簇", "不变量验证簇", "高风险业务不变量", "生产重放", "变异测试", "对抗测试", "覆盖率"]):
        route.update({"testing.md", "workflow.md"})
    if contains_any(prompt, ["实际项目编码 Loop", "Coding Loop Contract", "代码写入范围", "只读范围", "状态回写位置", "提交切片"]):
        route.update({"senior", "testing.md", "workflow.md"})
    if contains_any(prompt, ["Ponytail", "Open Code Review", "open-code-review", "alibaba/open-code-review", "OCR", "ocr review", "OpenCodeReview", "外部 Checker", "独立 Checker", "Karpathy", "Andrej", "karpathy-guidelines", "最小正确实现", "外科手术式变更", "外科手术式改动", "过度设计 CR", "过度设计专项", "源码级 Review", "设计模式", "找到变化", "封装变化", "真实变化轴", "接口", "策略", "工厂", "状态机", "规则层", "配置化"]):
        route.update({"senior", "coding-review-deep-dive.md"})
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
    if contains_any(prompt, ["业务架构规划", "业务 IT 对齐", "业务能力地图", "战略落项目", "战略到项目组合", "项目组合治理", "投资取舍", "投资决策支持", "重复建设识别", "能力-项目-系统映射", "知识库回流"]):
        route.add("business-architecture-planning.md")
        if contains_any(prompt, ["画图", "图形化", "可视化", "出图", "生成图", "映射图", "上下文图", "流程图", "状态机"]) and not contains_any(prompt, ["不要画图", "不画图", "无需画图", "只输出文字"]):
            route.add("diagram-output.md")
    if contains_any(prompt, product_judgment_terms):
        route.update({"product", "product-scenario-routing.md", "product-judgment-action-chain.md"})
        if contains_any(prompt, ["访谈", "工单", "反馈", "竞品", "资料", "数据", "机会"]):
            route.add("product-insight-analyst.md")
        if contains_any(prompt, ["Backlog", "路线图", "优先级", "取舍", "User Story", "AC"]):
            route.add("po-backlog-manager.md")
        if contains_any(prompt, ["AI Native", "工程", "系分", "TDD", "编码", "架构师"]):
            route.update({"wise-agent", "product-to-engineering-lifecycle.md"})
        if contains_any(prompt, ["pm-skills", "phuryn/pm-skills"]):
            route.add("source-map.md")
        if contains_any(prompt, ["Open Code Review", "open-code-review", "alibaba/open-code-review", "OCR", "ocr review", "OpenCodeReview", ".opencodereview", "rule.json", "外部 Checker", "独立 Checker"]):
            route.add("code-understanding-tools.md")
            route.add("verification-review-release.md")
            route.add("coding-review-deep-dive.md")
            if contains_any(prompt, ["Wind", "Wind 项目约规", "Wind 编码约规", "项目约规"]):
                route.add("wind")
                route.add("wind-coding-conventions.md")
    if contains_any(prompt, ["产品洞察", "需求洞察", "资料资产化", "机会雷达", "客户访谈", "竞品动态", "标杆实践", "证据来源", "推理链"]):
        route.add("product-insight-analyst.md")
    if contains_any(prompt, ["产品大师", "MAGI", "多视角", "合议评审", "PM/Reviewer", "Reviewer", "AI 生成的", "AI 生成方案"]):
        route.add("product-deliberation-workflow.md")
    if contains_any(prompt, ["Backlog", "机会清单", "机会点", "需求池", "需求优先级", "P0/P1/P2", "User Story"]):
        route.add("po-backlog-manager.md")
    if contains_any(prompt, diagram_terms) and not contains_any(prompt, ["不要画图", "不画图", "无需画图", "只输出文字"]):
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

wise_agent_outline_terms = (
    "默认最小输出",
    "结论",
    "当前阶段",
    "owner",
    "交接物",
    "授权策略",
    "验证与停止条件",
    "停止条件",
)

for case_id in [
    "wise-agent-should-end-to-end-product-engineering-workflow",
    "wise-agent-should-gsd-cad-handoff",
    "wise-agent-should-compress-gsd-cad-goal-into-loop",
    "wise-agent-should-gsd-wise-agent",
    "wise-agent-should-demand-analysis-collaboration-gate",
    "wise-agent-should-development-standards-gate",
    "wise-agent-should-intent-to-production-role-loop",
    "wise-agent-should-three-layer-feedback-loop-cadence",
    "wise-agent-should-autonomous-discovery-to-delivery-loop",
    "wise-agent-should-role-collaboration-loop-main-flow",
    "wise-agent-should-knowledge-expression-gate",
    "wise-agent-should-nonstandard-problem-mode",
    "wise-agent-should-practical-coding-loop",
    "wise-agent-should-feedback-loop-verification-cluster",
    "wise-agent-should-architecture-entropy-loop",
    "wise-agent-should-plan-to-goal-bridge-without-new-flow",
    "wise-agent-should-planning-execution-admission-gate",
    "wise-agent-should-gsd-goal-governance",
    "wise-agent-should-delivery-execution-control",
    "wise-agent-should-map-sdlc-without-renaming-main-flow",
    "wise-agent-should-default-lightweight-lifecycle-routing",
    "wise-agent-should-backflow-confirmed-domain-term-after-grill",
    "wise-agent-should-stop-domain-writeback-on-code-conflict",
    "wise-agent-should-avoid-adr-for-reversible-wording-choice",
    "wise-agent-should-agent-loop-maturity-diagnosis",
    "wise-agent-should-design-engineering-loop-not-prompting",
    "wise-agent-should-reusable-work-asset-loop",
    "wise-agent-should-cdd-capability-discovery-gate",
    "wise-agent-should-wisdom-lens-loop-scheduling",
    "wise-agent-should-review-ai-coding-process",
    "wise-agent-should-code-delivery",
    "wise-agent-should-progressive-sdd-lattice-harness",
    "wise-agent-should-production-effectiveness-gate",
    "wise-agent-should-context-system-knowledge-base-governance",
    "wise-agent-should-domain-expert-distillation",
    "wise-agent-should-fact-boundary-check",
    "wise-agent-should-route-prd-work",
    "wise-agent-should-route-cr-work",
]:
    expected_handling_has(case_id, wise_agent_outline_terms)

expected_handling_has(
    "wise-agent-should-reusable-work-asset-loop",
    (
        "可复用工作资产 Loop",
        "delivery-execution-control",
        "source-map",
        "工作资产 Loop 卡",
        "流程名称",
        "触发器",
        "输入",
        "动作",
        "质量证据 / 评测样例",
        "记忆 / 保存位置",
        "回流方式",
        "停止条件",
        "人工决策点",
        "可复测样例",
        "不得吸收",
        "高频、低风险、有证据",
        "不临时加长 Prompt",
        "Skill、reference、fixture、脚本、AGENTS / CONTEXT、ADR、Goal Ledger 或项目知识库",
        "未核验业务知识",
        "战略取舍",
        "客户承诺",
        "路线图改动",
        "上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-cdd-capability-discovery-gate",
    (
        "CDD / 能力发现门禁",
        "delivery-execution-control",
        "code-delivery",
        "source-map",
        "非 T0",
        "Capability Discovery",
        "已有 Skill / Tool / Workflow / 脚本 / 自动化",
        "触发条件、输入、动作、边界和验收证据",
        "artifact、validator、readback 或用户确认",
        "缺口明确后才新增实现",
        "不把工具名当能力",
        "不绕过既有 QC、readback、权限边界、失败处理、测试、CR、owner 确认或 Git/上线授权",
    ),
)

expected_handling_has(
    "wise-agent-should-progressive-sdd-lattice-harness",
    (
        "渐进式 SDD / Lattice Harness 规范化路径",
        "spec-template-practices",
        "code-delivery",
        "engineering-governance",
        "source-map",
        "不新增并列流程",
        "不复制外部命令或目录",
        "低风险轻量任务卡",
        "中风险可评审 Spec",
        "高风险 Harness/GSD Spec",
        "高不确定 TDD 优先",
        "Intent -> Context -> Spec -> Orchestrator -> Verification -> Evidence / Eval -> Drift Check -> Loop / Learn",
        "Spec 是约束不是文档",
        "生成者可以修复但不能自己宣布通过",
        "准出必须来自测试、静态检查、验收覆盖、漂移检查、只读 Checker 或人工 owner",
        "缺上下文补 Context",
        "缺裁判补 Verification",
        "缺追踪补 Evidence",
        "缺漂移补 drift-check",
        "缺学习补 Loop / Learn",
    ),
)

expected_handling_has(
    "wise-agent-should-context-system-knowledge-base-governance",
    (
        "上下文治理视图 / 知识回流视图",
        "code-delivery",
        "huaxia-practical-wisdom",
        "code-understanding-tools",
        "source-map",
        "先落 Context System，再评估知识库工具",
        "L0 项目级上下文",
        "L1 模块级上下文",
        "L2 任务级上下文",
        "update-context 门禁",
        "权威落点",
        "owner",
        "证据锚点",
        "不得回写内容",
        "停止条件",
        "需要经典取舍视角时按需装载",
        "外部知识库、向量库、代码图谱或 Understand Anything 只能作为加速器",
        "不替代源码、测试、CR、owner 确认或项目约规",
    ),
)

expected_handling_has(
    "wise-agent-should-domain-expert-distillation",
    (
        "业务专家蒸馏 / 领域知识回流路径",
        "domain-expert-distillation",
        "product-to-engineering-lifecycle",
        "verification-review-release",
        "huaxia-practical-wisdom",
        "source-map",
        "准入结论",
        "资料范围",
        "目标业务域",
        "证据成熟度",
        "owner",
        "写入范围",
        "敏感边界",
        "学习路径",
        "学习结果知识库规划",
        "先按业务域或模块分区",
        "cross-domain",
        "逐篇学习台账",
        "证据地图",
        "术语与对象表",
        "领域知识卡",
        "流程状态与判断规则",
        "接口事件与数据",
        "待确认与压测",
        "domain_or_module / maturity / updated_at",
        "业务证据地图",
        "领域专家 Skill Pack 草案",
        "三重验证",
        "答题协议",
        "压力测试清单",
        "V1 证据交叉",
        "V2 可回答新问题",
        "V3 领域特异性",
        "事实 / 推断 / 待确认 / 范围外不做",
        "经典镜片不能把业务专家写成自由发挥角色",
        "产品 owner 替代",
        "架构 owner 替代",
        "默认安装 Skill",
    ),
)

expected_handling_has(
    "wise-agent-should-route-wind-agents-init",
    (
        "知止者读取项目事实",
        "装载 wind-coding-conventions",
        "Wind/Nobe 证据",
        "wind-coding-conventions",
        "wind-project-agents-template.md",
        "最小项目 AGENTS.md",
        "装载工程能力",
        "不得猜测构建命令、生产流程、模块事实或 Git 授权",
    ),
)

expected_handling_has(
    "wise-agent-should-coordinate-specialized-skills",
    (
        "知止者保持统一行动主体",
        "capability-routing",
        "delivery-lifecycle",
        "装载最小能力",
        "产品架构能力",
        "工程能力",
        "java-service-code-generator",
        "Java/Wind 约规作为规则能力",
        "不设置第二行动主体",
        "代码理解和图形能力只补当前缺口",
        "最终由知止者综合一个结果",
        "工具摘要不得替代测试、CR、owner 确认、Git 授权或上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-deliver-prd-from-prototype",
    (
        "显式调用 $wise-agent",
        "装载 product-architecture-expert",
        "同一 Agent",
        "第二人格或第二 Owner",
        "直接交付可评审 PRD",
    ),
)

behavior_contract_has(
    "wise-agent-should-deliver-prd-from-prototype",
    (
        "activation",
        "action_subject",
        "must_not",
    ),
    (
        "显式调用 $wise-agent",
        "未点名的普通 PRD",
        "product-architecture-expert",
        "同一 Agent",
        "第二人格",
        "重复 Owner",
        "互相转交责任",
    ),
)

expected_handling_has(
    "wise-agent-should-autonomously-deliver-read-only-cr",
    (
        "统一行动主体",
        "精确 description",
        "同时加载工程能力",
        "只读 CR",
        "严重级别",
        "文件行号",
        "验证缺口",
        "残余风险",
        "不得修改文件",
        "第二 Owner",
    ),
)

expected_handling_has(
    "wise-agent-should-harness-skill-best-practices-review",
    (
        "Skill 工程化反向验证路径",
        "capability-routing",
        "source-map",
        "verification-review-release",
        "文章已读取正文",
        "不吸收边界",
        "Metadata 触发",
        "能力输入输出",
        "按需资源",
        "确定性脚本",
        "独立验证",
        "最小重构",
        "source-map",
        "fixture",
        "validator",
        "evaluate-skills.py",
        "不把外部权限字段、运行钩子、用户偏好持久化、日志埋点、自动推送或 skill-creator 操作流程写成本仓库默认能力",
    ),
)

expected_handling_has(
    "wise-agent-should-official-skill-methodology-with-wisdom-lens",
    (
        "能力接入与 Skill 治理评估",
        "capability-routing",
        "huaxia-practical-wisdom",
        "source-map",
        "verification-review-release",
        "官方 Anthropic 是否已读正文",
        "Perplexity 是否已读正文或仅为待核验线索",
        "名实相符",
        "最小正确层级",
        "正向触发",
        "邻近 Skill 负例",
        "不吸收边界",
        "不把未读取正文的来源",
        "Claude hooks",
        "marketplace",
        "持久 memory",
    ),
)

expected_handling_has(
    "wise-agent-should-superpowers-skills-library",
    (
        "Superpowers 官方插件迁移模式",
        "openai-api-curated",
        "installed/enabled",
        "知止者保持唯一行动主体",
        "产品判断回产品架构专家",
        "工程判断回资深架构师",
        "用户授权 / 项目 AGENTS.md > 知止者 > 专业 Skill > Superpowers",
        "已安装不等于脚本、Git、worktree、subagent、联网或写入授权",
        "新会话行为冒烟",
        "删除 external-superpowers 离线快照",
    ),
)

expected_handling_has(
    "wise-agent-should-coordinate-superpowers-debugging",
    (
        "工程责任 Owner 为人类维护方",
        "资深架构师是主工程能力",
        "systematic-debugging",
        "test-driven-development",
        "verification-before-completion",
        "Superpowers 不成为第二 Owner",
        "不因插件已安装自动创建 worktree、启动 subagent、提交或推送 Git",
    ),
)

expected_handling_has(
    "wise-agent-should-coordinate-superpowers-brainstorming",
    (
        "产品责任 Owner 为人类产品负责人",
        "产品架构专家是主产品能力",
        "brainstorming 只作为",
        "关键分叉未决时才升级 grill-me",
        "避免 brainstorming 与 grill-me 重复问询",
        "不进入 writing-plans、TDD、编码、worktree 或 Git",
    ),
)

expected_handling_has(
    "wise-agent-should-block-superpowers-implicit-git-actions",
    (
        "不得因为 using-superpowers、using-git-worktrees 或 finishing-a-development-branch",
        "创建 worktree、分支、提交、推送、PR 或清理工作区",
        "已安装插件不扩大授权",
    ),
)

expected_handling_has(
    "wise-agent-should-layer-ai-coding-frameworks",
    (
        "AI 编码框架分层映射路径",
        "superpowers-skill-library",
        "delivery-execution-control",
        "code-delivery",
        "source-map",
        "Superpowers 归为方法纪律层",
        "GSD 归为上下文 / Spec / 状态层",
        "GStack 归为角色链审查层",
        "Trellis 归为仓库级记忆 / 任务树层",
        "不新增并列流程",
        "不默认创建 .trellis",
        "不安装 npm",
        "不运行脚本",
        "不写入 Git",
    ),
)

expected_handling_has(
    "wise-agent-should-admit-trellis-only-for-proven-context-loss",
    (
        "Trellis 可选载体准入判断",
        "仓库级 Agent Harness / 记忆与任务状态载体",
        "不是新的产研主流程",
        "现有 AGENTS.md、Issue、Spec、Goal Ledger 和知识库",
        "真实证据",
        "不安装 Trellis",
        "非关键任务做隔离试点",
        "显式授权",
        "@mindfoldhq/trellis",
        "AGPL-3.0",
        ".trellis/spec",
        ".trellis/tasks",
        ".trellis/workspace",
        "平台接入文件",
    ),
)

expected_handling_has(
    "wise-agent-should-map-gstack-role-chain-template",
    (
        "GStack 角色链模板映射路径",
        "delivery-lifecycle",
        "product-to-engineering-lifecycle",
        "prd-system-design-review",
        "superpowers-skill-library",
        "verification-review-release",
        "source-map",
        "/office-hours 映射为产品思考",
        "/plan-ceo-review 映射为范围收敛",
        "/plan-eng-review 映射为工程评审",
        "/plan-design-review 映射为交互评审",
        "开发映射为 TDD / 编码实现",
        "/review 映射为源码 CR",
        "/qa 映射为 QA 验证",
        "/ship 映射为发布准出",
        "命令名只作触发别名",
        "不作为外部工具、默认命令菜单或新流程",
        "产品思考回产品架构专家",
        "工程评审、TDD、编码和源码 CR 回资深架构师",
        "Git、PR、merge、部署和生产操作必须显式授权",
    ),
)

expected_handling_has(
    "wise-agent-should-gstack-production-delivery-review",
    (
        "GStack 角色链 + 生产交付审查路径",
        "delivery-lifecycle",
        "verification-review-release",
        "code-delivery",
        "superpowers-skill-library",
        "source-map",
        "/office-hours 映射为产品思考 forcing questions",
        "/plan-ceo-review 映射为范围收敛",
        "/plan-eng-review 映射为工程评审",
        "/plan-design-review 映射为交互评审",
        "开发映射为 TDD / 最小实现",
        "/review 映射为独立源码 CR",
        "/qa 映射为 QA 验证",
        "/ship 映射为生产交付审查 / 发布准出",
        "生产交付审查卡",
        "产品价值",
        "范围收敛",
        "发布观测",
        "回滚 / 人工接管",
        "不新增命令菜单",
        "不把测试通过、PR 数、Agent 自述、Git/PR/merge/部署或上线审批写成自动准出",
    ),
)

expected_handling_has(
    "wise-agent-should-production-effectiveness-gate",
    (
        "验证发布视图 / 生产生效验证门禁",
        "delivery-lifecycle",
        "verification-review-release",
        "code-delivery",
        "source-map",
        "代码变更",
        "配置 / 开关 / prompt 变更",
        "文档 / Skill-only 变更",
        "高风险变更",
        "版本回读",
        "配置回读",
        "冒烟验证",
        "业务场景模拟验收",
        "观测确认",
        "工单 / Goal 回写",
        "生产生效验证卡",
        "公开资料、业内共识或行业标准规范只能作为补偿场景来源",
        "不把已部署、已推配置、测试通过、页面能打开、接口能调用、公开资料或 Agent 自述写成预发 OK、生产 OK、CR 结论、Git 授权或上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-unify-production-ready-workflow-with-wisdom-lens",
    (
        "生产可用混一模型路径",
        "huaxia-practical-wisdom",
        "code-delivery",
        "delivery-lifecycle",
        "delivery-execution-control",
        "verification-review-release",
        "source-map",
        "一个入口",
        "一个契约",
        "一个准出",
        "知止者作为入口",
        "交付契约",
        "生产可用准出卡",
        "真实业务入口",
        "独立 CR",
        "发布观测",
        "回滚 / 人工接管",
        "经典镜片只校准取舍、推进与边界、目标与工具、完成名实",
        "不新增流程名、命令菜单、外部工具依赖",
        "不把华夏经世智慧替代事实、测试、CR、授权或上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-intent-to-production-role-loop",
    (
        "产研协同",
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
    "wise-agent-should-three-layer-feedback-loop-cadence",
    (
        "知止者三层反馈节奏校准路径",
        "delivery-lifecycle",
        "huaxia-practical-wisdom",
        "Agentic Coding Loop",
        "Developer Feedback Loop",
        "External Feedback Loop",
        "内层 AI Maker",
        "Spec / Evals / 失败测试",
        "更接近当前 Spec",
        "产品 / 架构 owner",
        "Vision、范围和交互判断翻译成 Spec",
        "真实用户、市场、A/B、工单、监控或复盘慢反馈修正 Vision",
        "经典镜片只校准时序、节奏和名实",
        "不得让 AI 自测、开发者品味、经典类比或工具输出替代产品判断、真实用户反馈、测试通过、CR 结论、发布审批或执行授权",
    ),
)

expected_handling_has(
    "wise-agent-should-autonomous-discovery-to-delivery-loop",
    (
        "自主挖掘到交付",
        "产研协同",
        "delivery-lifecycle",
        "delivery-execution-control",
        "code-delivery",
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
    "wise-agent-should-role-collaboration-loop-main-flow",
    (
        "知止者主流程",
        "delivery-lifecycle",
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
        "需求变更进入 Loop 时，先做影响识别再改文档或代码",
        "PRD 决策层 / 方案层 / 实现层、系分、接口 / 事件、规则 / 字段、验收种子、测试用例、发布风险、通知对象和过程记录链接",
        "产品/交互设计和验收种子回到产品架构专家",
        "TDD/测试设计、编码实现、编码评审、安全可靠和发布风险回到资深架构师",
        "结构化 Java Service 生成回到 java-service-code-generator",
        "不能把阶段名当成自由发挥提示词",
        "目标、计划、原子执行、执行契约和授权边界只作内部层",
    ),
)

expected_handling_has(
    "wise-agent-should-decision-gate-blocker-progression",
    (
        "小闭环决策澄清门禁",
        "问询推进",
        "自我问询 / 自我回答",
        "一个主 blocker",
        "按你建议推进",
        "关闭当前 blocker",
        "下一阶段输入",
        "下一最高价值 blocker",
        "建议答案",
        "默认暂停点",
        "不重新摊开全局方案",
        "不同时展开多个 blocker",
        "不把续作写成已授权",
    ),
)

expected_handling_has(
    "wise-agent-should-block-plan-before-owner-decisions",
    (
        "计划生成准入门禁",
        "delivery-execution-control",
        "Facts / Decisions",
        "需 owner 判断的关键假设",
        "禁止先生成长计划让 owner 审查 AI 假设",
        "一个主 blocker",
        "推荐答案",
        "证据",
        "默认暂停点",
        "决策快照",
        "owner 确认",
        "最小计划",
    ),
)

behavior_contract_has(
    "wise-agent-should-block-plan-before-owner-decisions",
    (
        "plan_generation_gate",
        "first_response_must_include",
        "first_response_must_not_include",
        "advance_gate",
    ),
    (
        "未决 owner 判断",
        "完整方案",
        "长计划",
        "Facts / Decisions",
        "一个主 blocker",
        "推荐答案",
        "证据",
        "影响",
        "默认暂停点",
        "多分支执行清单",
        "已授权执行",
        "决策快照",
        "owner 确认",
        "最小计划",
    ),
)

expected_handling_has(
    "wise-agent-should-wayfind-before-spec",
    (
        "决策寻路路径",
        "Destination",
        "Decisions so far",
        "Frontier",
        "Not yet specified",
        "Out of scope",
        "Next decision",
        "地图只作索引",
        "每轮最多关闭一个决策",
        "grill-me",
        "research",
        "prototype",
        "prerequisite task",
        "不执行最终方案",
    ),
)

behavior_contract_has(
    "wise-agent-should-wayfind-before-spec",
    ("entry_gate", "map_must_include", "node_routes", "must_not_do"),
    (
        "Destination",
        "Decisions so far",
        "Frontier",
        "Not yet specified",
        "Out of scope",
        "Next decision",
        "grill-me",
        "research",
        "prototype",
        "prerequisite task",
        "不得自动创建 Issue、分支、Worker 或外部任务系统",
    ),
)

expected_handling_has(
    "wise-agent-should-skip-wayfinding-for-clear-plan",
    (
        "跳过决策寻路",
        "当前会话可完成",
        "按现有工程交付路径执行和验证",
        "不创建 Destination 地图、Frontier、Not yet specified、Issue 或新的 Goal",
        "不重新进入 grill-me",
    ),
)

expected_handling_has(
    "wise-agent-should-questioning-repair",
    (
        "问询修复路径",
        "delivery-execution-control",
        "delivery-lifecycle",
        "verification-review-release",
        "当前问询触发",
        "主 blocker",
        "已自答证据",
        "需 owner 判断项",
        "只修复问询推进",
        "不重开全局方案",
        "不新增并列流程",
        *DECISION_GRILL_BOUNDARY_TERMS,
        "每次只处理一个主 blocker",
        "建议答案",
        "默认暂停点",
        "关闭当前 blocker",
        "下一阶段输入",
        "下一最高价值 blocker",
        "再升级 grill-me",
        "`grill-me` 是唯一入口",
        "不写成并列流程",
    ),
)

expected_handling_has(
    "wise-agent-should-grill-me-loop-progression",
    (
        "grill-me 盘问门禁",
        *DECISION_GRILL_BOUNDARY_TERMS,
        "Loop 推进",
        "delivery-execution-control",
        "delivery-lifecycle",
        "superpowers-skill-library",
        "source-map",
        "显式提到 grill-me 触发不稳定或角色 Loop 自动触发时，先审计四类信号",
        "`grill-me` 是唯一入口",
        "废弃本地 `grilling`",
        "不新增并列流程",
        "关键分叉未决",
        "回答含糊",
        "连续返工",
        "一次只问一个问题",
        "给推荐答案",
        "Facts / Decisions",
        "Facts 用代码库、文档、测试或日志自答",
        "Decisions 才等待 owner 反馈",
        "shared understanding",
        "模糊回答 push back",
        "决策树分支",
        "已确认选择",
        "被排除方案",
        "待确认项",
        "写回产品上下文卡、工程交接卡、任务树 / 计划切片、验证矩阵或下一阶段输入",
        "不把 grill-me 写成默认执行授权、长时间访谈、产品 owner 决策、架构批准、测试通过、CR 结论、Git 授权或上线审批",
    ),
)

behavior_contract_has(
    "wise-agent-should-grill-me-loop-progression",
    (
        "first_response_must_include",
        "first_response_must_not_include",
        "advance_gate",
        "repeat_question_gate",
        "exit_summary_must_include",
    ),
    (
        "触发原因",
        "当前分支",
        "一个问题",
        "推荐答案",
        "依据",
        "默认暂停点",
        "question_id",
        "已问问题",
        "答案状态",
        "同义重复问题",
        "只追问缺失项",
        "关闭当前 blocker",
        "第二个待答问题",
        "完整方案",
        "执行清单",
        "等待 owner 反馈",
        "owner 确认",
        "Facts / Decisions",
        "shared understanding",
        "已确认选择",
        "被排除方案",
        "待确认项",
        "下一阶段输入",
        "写回位置",
    ),
)

expected_handling_has(
    "wise-agent-should-reconcile-grill-me-snapshot-before-execution",
    (
        "grill-me 决策快照",
        "执行前对账门禁",
        "delivery-lifecycle",
        "verification-review-release",
        "不新建并列流程",
        "决策快照",
        "已确认选择",
        "被排除方案",
        "待确认项",
        "下一阶段输入",
        "写回位置",
        "执行 / 写文件 / 生成计划前必须先对账",
        "本轮执行依据哪条已确认选择",
        "被排除方案不得复活",
        "待确认项不得脑补",
        "不一致",
        "停止并问 owner",
        "不能靠上下文记忆、模型推测",
        "红线",
        "底线",
        "不能碰",
        "重点关注并记录",
    ),
)

behavior_contract_has(
    "wise-agent-should-reconcile-grill-me-snapshot-before-execution",
    (
        "pre_execution_gate",
        "snapshot_must_include",
        "must_not_do",
        "redline_terms",
    ),
    (
        "执行 / 写文件 / 生成计划前必须先对账决策快照",
        "不一致时停止并问 owner",
        "已确认选择",
        "被排除方案",
        "待确认项",
        "下一阶段输入",
        "写回位置",
        "被排除方案不得复活",
        "待确认项不得脑补",
        "上下文记忆",
        "模型推测",
        "红线",
        "底线",
        "不能碰",
        "不可",
        "禁止",
        "必须",
    ),
)

expected_handling_has(
    "wise-agent-should-backflow-confirmed-domain-term-after-grill",
    (
        "grill-me 决策快照与知识回流路径",
        "执行前先对账",
        "业务 owner 追认",
        "PRD、代码和测试锚点一致",
        "按业务域或模块",
        "现有知识库",
        "术语与对象表",
        "证据地图",
        "来源、owner、成熟度、更新时间与影响范围",
        "精确写回位置",
        "不新建 Skill",
        "不自动创建 CONTEXT.md、ADR 或知识库目录",
        "不把知识回流当 Execution Grant",
    ),
)

expected_handling_has(
    "wise-agent-should-stop-domain-writeback-on-code-conflict",
    (
        "领域知识冲突门禁",
        "现有术语与对象表",
        "知识库、代码和测试作为并列证据",
        "不把当前代码自动认定为正确事实",
        "冲突证据、影响范围和待确认项",
        "停止覆盖知识库和后续实现",
        "询问业务 owner",
        "owner 未确认前不得提升成熟度",
        "不得脑补统一术语",
        "不得创建 CONTEXT.md、ADR 或新知识库目录",
        "不得把暂时的 grill-me 理解写成工程事实",
    ),
)

expected_handling_has(
    "wise-agent-should-avoid-adr-for-reversible-wording-choice",
    (
        "知识回流与 ADR 准入判断",
        "可逆",
        "不影响公共契约",
        "不存在真实方案取舍",
        "决策快照、现有产品文档或交接卡",
        "不创建 ADR 或 CONTEXT.md",
        "同时难以逆转、缺少背景会令人困惑、且源于真实方案取舍",
        "资深架构师",
        "adr-and-tradeoff.md",
        "未获项目写入授权时只输出候选回流位置",
    ),
)

expected_handling_has(
    "wise-agent-should-assetize-grill-me-handoff",
    (
        "grill-me 盘问门禁",
        "知识回流视图",
        "delivery-execution-control",
        "delivery-lifecycle",
        "source-map",
        "不新增并列流程",
        "不默认安装外部 grill-me skill",
        "长链路",
        "结果分叉多",
        "返工成本高",
        "人的 Taste / 偏好 / 红线会影响方案",
        "隐性判断显式化为可执行决策",
        "每次只问一个问题",
        "给推荐答案",
        "Facts 用代码库、文档、测试或日志自答",
        "Decisions 才问 owner",
        "shared understanding",
        "退出条件不是问完所有问题",
        "决策快照",
        "交接资产",
        "写回位置",
        "项目 Context / AGENTS / Spec / ADR / fixture / 脚本 / Issue / PR / hand-off prompt",
        "不得只依赖聊天上下文、模型记忆或问询过程",
        "不得把外部文章原文、作者口吻、工具宣传或未验证经验写入长期资产",
    ),
)

behavior_contract_has(
    "wise-agent-should-assetize-grill-me-handoff",
    (
        "trigger_gate",
        "assetization_gate",
        "writeback_targets",
        "must_not_do",
    ),
    (
        "长链路",
        "结果分叉多",
        "返工成本高",
        "人的 Taste / 偏好 / 红线会影响方案",
        "可写回的决策快照和交接资产",
        "项目 Context",
        "AGENTS",
        "Spec",
        "ADR",
        "fixture",
        "脚本",
        "Issue",
        "PR",
        "hand-off prompt",
        "不新增并列流程",
        "不默认安装外部 grill-me skill",
        "不得只依赖聊天上下文、模型记忆或问询过程",
    ),
)

expected_handling_has(
    "wise-agent-should-install-mattpocock-grill-me-v1-1",
    (
        "skill-installer",
        "Matt Pocock skills",
        "v1.1.0",
        "移除旧本地 `grill-me`",
        "移除旧本地 `grilling`",
        "只安装 `grill-me`",
        "`grill-me` 是唯一入口",
        "废弃本地 `grilling`",
        "VALIDATE_GRILL_ME_INSTALL=1 ./scripts/validate.sh",
        "scripts/validate-grill-me-install.py",
        "安装层校验",
        "未通过不得宣称完成",
        "Facts / Decisions",
        "shared understanding",
        "不安装全仓库",
        "不运行 npm、package scripts、Claude plugin、Trellis 或 hooks",
        "更新 source-map、superpowers-skill-library、fixture 和 validator",
    ),
)

expected_handling_has(
    "wise-agent-should-knowledge-expression-gate",
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
    "wise-agent-should-nonstandard-problem-mode",
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
    "wise-agent-should-practical-coding-loop",
    (
        "实际项目编码 Loop",
        "delivery-execution-control",
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
    "wise-agent-should-feedback-loop-verification-cluster",
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
    "wise-agent-should-architecture-entropy-loop",
    (
        "架构排熵 Loop / 腐朽门禁模式",
        "delivery-execution-control",
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
    "wise-agent-should-plan-to-goal-bridge-without-new-flow",
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
    "wise-agent-should-map-sdlc-without-renaming-main-flow",
    (
        "主能力域",
        "协同域",
        "以交付编排为主能力域，以工程治理为协同域",
        "知止者是稳定主入口",
        "交付编排、工程治理、知识演进是稳定能力域",
        "SDLC 只作为构想、开发、运行支持、维护演进和退役的生命周期覆盖框架",
        "安全、权限、风险、可追溯性和知识回流横贯各阶段",
        "Loop 只是阶段内和跨阶段的反馈机制",
        "规划、执行、评估只是受控执行机制",
        "不新增并列流程、不再次改名",
    ),
)

expected_handling_has(
    "wise-agent-should-default-lightweight-lifecycle-routing",
    (
        "轻量生命周期定位",
        "当前只定位设计评审阶段",
        "主责 owner",
        "主能力",
        "一个主 blocker",
        "交接物",
        "验证与停止条件",
        "角色 Loop",
        "不因用户未提 SDLC 或生命周期而跳过定位",
        "不展开实现、发布、维护退役等无关阶段",
        "不把轻量定位升级为完整 SDLC 覆盖审查",
    ),
)

expected_handling_has(
    "wise-agent-should-product-judgment-loop-admission",
    (
        "知止者装载产品架构能力",
        "product-judgment-action-chain",
        "访谈、工单、竞品、路线图、PRD 和复盘材料",
        "直接完成产品判断",
        "已知事实 / 证据",
        "判断动作",
        "取舍结论",
        "不做项",
        "下一产物",
        "产品 owner",
        "工程交接结论",
        "不进入系分、TDD、编码或 Execution Grant",
        "不安装或照搬外部 pm-skills",
    ),
)

expected_handling_has(
    "wise-agent-should-route-business-architecture-planning",
    (
        "知止者装载产品架构能力",
        "直接交付业务架构准入卡",
        "owner",
        "授权",
        "验证与停止条件",
        "business-architecture-planning",
        "业务架构准入卡",
        "业务能力地图",
        "价值流",
        "核心对象与规则",
        "能力-项目-系统映射",
        "差距 / 依赖 / 优先级",
        "项目组合 / 路线图",
        "按业务域或模块分区",
        "不直接脑补系统设计、TDD、编码任务或 Execution Grant",
    ),
)

expected_handling_has(
    "product-should-update-existing-prd-without-renaming",
    (
        "既有 PRD 更新路径",
        "保持 docs/member-prd-v2.md 原路径",
        "本次不是命名迁移",
        "不得自动改名为 〈主题〉-产品设计.md",
        "不得修改 AGENTS.md / README.md",
        "将冲突列为待确认并询问 owner",
        "只有用户明确授权项目约规治理时才修改项目约规",
        "模板回退命名只用于新文档",
        "只有用户明确进入命名迁移任务时才改名并同步所有引用",
    ),
)

expected_handling_has(
    "product-should-pm-skills-judgment-action-chain",
    (
        "产品判断动作链路径",
        "product-judgment-action-chain",
        "产品判断动作链卡",
        "已知事实 / 证据",
        "合理推断",
        "待确认项",
        "范围外不做",
        "判断动作",
        "取舍结论",
        "不做项 / 延后项",
        "下一产物",
        "owner",
        "验收 / 停止条件",
        "交接路由",
        "知止者前置门禁",
        "不安装、复制或照搬外部 pm-skills",
    ),
)

expected_handling_has(
    "product-should-business-architecture-planning",
    (
        "业务架构规划路径",
        "business-architecture-planning",
        "真实问题",
        "战略意图",
        "决策场景",
        "业务架构准入卡",
        "业务能力地图",
        "价值流",
        "核心对象与规则",
        "能力-项目-系统映射",
        "差距 / 依赖 / 优先级",
        "项目组合 / 路线图",
        "Product Context Card",
        "按业务域或模块分区",
        "知识库回流计划",
        "不把业务架构降级为全公司大图、组织架构图、系统清单或 Execution Grant",
    ),
)

expected_handling_has(
    "product-should-business-architecture-diagram-route",
    (
        "业务架构规划图形化路由",
        "business-architecture-planning",
        "diagram-output",
        "业务能力地图",
        "价值流 / 跨角色流程图",
        "能力-项目-系统-数据映射图",
        "差距 / 依赖 / 路线图",
        "正式图形化交付默认只生成 SVG",
        "图只辅助评审与沟通",
        "不替代业务确认、产品判断、工程设计、Execution Grant 或上线审批",
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
    "senior-should-update-existing-system-design-without-renaming",
    (
        "既有系分更新路径",
        "保持 docs/member-system-design-v1.md 原路径",
        "本次不是命名迁移",
        "不得自动改名为 〈主题〉-系分设计.md",
        "不得修改 AGENTS.md / README.md",
        "将冲突列为待确认并询问 owner",
        "只有用户明确授权项目约规治理时才修改项目约规",
        "模板回退命名只用于新文档",
        "只有用户明确进入命名迁移任务时才改名并同步所有引用",
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
    "wise-agent-should-delivery-execution-control",
    (
        "Agent Loop Engineering",
        "delivery-execution-control",
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
    "wise-agent-should-agent-loop-maturity-diagnosis",
    (
        "Agent Loop Engineering / L1-L4 工程成熟度诊断",
        "delivery-execution-control",
        "L1-L4 诊断结论",
        "当前瓶颈层",
        "不先做",
        "最小修复",
        "是否允许 L4 试点",
        "L1 Prompt",
        "L2 Context",
        "L3 Harness",
        "L4 Loop",
        "先定位层级再开药方",
        "生产不稳先加固 L3",
        "不把 L2 问题误修成 Prompt",
        "不跳过 L3 直接上 L4",
        "低风险高频任务",
        "Maker / Checker",
        "理解债 / 认知投降",
    ),
)

expected_handling_has(
    "wise-agent-should-design-engineering-loop-not-prompting",
    (
        "Agent Loop Engineering / 设计工程 Loop",
        "delivery-execution-control",
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
    "wise-agent-should-wisdom-lens-loop-scheduling",
    (
        "按需装载 huaxia-practical-wisdom",
        "事实、推断和待确认",
        "工程主能力完成源码级 CR",
        "严重级别、文件/行号、验证证据、残余风险和修复优先级",
        "没有证据的只写待确认",
        "名实、时势、风险和行动反偏",
        "不替代事实、测试、CR、Execution Grant、上线审批或专业确认",
    ),
)

expected_handling_has(
    "wise-agent-should-unify-ai-workflows-with-yinyang-principle",
    (
        "知止者混一总纲",
        "huaxia-practical-wisdom",
        "delivery-execution-control",
        "code-delivery",
        "verification-review-release",
        "source-map",
        "以真实交付为体，以证据闭环为用",
        "经典镜片只校准边界、推进、名实和最小有效组合",
        "GSD、CAD、Goal、Harness、SDD、Loop、Checker 和知识回流只作为内部用法归位",
        "不作为并列工作流外显",
        "不把阴阳、神用无方、华夏经世智慧或任何外部工作流写成事实证据、测试通过、CR 结论、Git 授权或上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-classic-wisdom-lens-supplement",
    (
        "huaxia-practical-wisdom 的经典镜片补足路径",
        "classical-lenses",
        "evidence-boundaries",
        "source-map",
        "周易",
        "变与不变",
        "时位",
        "可逆实验",
        "道德经",
        "庄子",
        "少干预和顺纹理",
        "儒家与法家",
        "正名",
        "兵家",
        "不可胜与止损",
        "中医系统观",
        "表象、结构、机制",
        "治未病",
        "五德终始",
        "阶段承接与退场",
        "只选择命中的 1-3 个镜片",
        "不得把传统智慧写成事实证据、医学建议、占卜命理、工程验证、Execution Grant、测试通过、CR 结论或上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-gate-ai-bug-report-and-patch-with-wisdom-lens",
    (
        "AI bug / 补丁门禁",
        "verification-review-release",
        "huaxia-practical-wisdom",
        "待确认、继续根因分析或可进入 CR",
        "复现 / 触发条件",
        "源码锚点",
        "根因假设",
        "同类影响范围",
        "最小修复",
        "验证命令 / 结果",
        "下一 owner",
        "名实、根因、预防、失败回退和过度修复",
        "不得把模型自述、工具告警、局部 guard、放宽断言或 AI patch 写成测试通过、CR 结论、合并判断或上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-development-standards-gate",
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
    "wise-agent-should-prd-ai-prescan-review",
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
    "wise-agent-should-final-deliverable-document-gate",
    (
        "最终文档准出模式",
        "正式 PRD/系分/Spec 正文与过程资产",
        "正文只保留当前有效目标、范围、规则、设计取舍、风险、待确认、验收、版本状态和过程记录链接",
        "讨论过程、迭代草稿、AI 推理轨迹、被拒方案",
    ),
)

expected_handling_has(
    "wise-agent-should-spec-template-practices",
    (
        "PRD / SDD / 实现 Spec 三层边界",
        "不可让 AI 猜",
        "实现 Spec 作为实现和 CR 检查清单",
        "更新 Spec",
    ),
)

expected_handling_has(
    "wise-agent-should-production-sdd-source-of-truth",
    (
        "SDD 生产代码模式",
        "spec-template-practices",
        "code-delivery",
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
    "wise-agent-should-fact-boundary-check",
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

expected_handling_has(
    "wise-agent-should-admit-open-code-review",
    (
        "工具准入",
        "Open Code Review / OCR",
        "CLI",
        "Codex plugin",
        "LLM provider",
        "preview 文件覆盖/排除清单",
        "Wind 约规",
        "外部 Checker 证据",
        "资深架构师",
        "不替代 TDD",
        "源码级 CR",
        "Git 授权",
        "上线审批",
    ),
)

expected_handling_has(
    "wise-agent-should-source-quality-review-loop",
    (
        "源码质量评审 Loop",
        "verification-review-release",
        "code-understanding-tools",
        "huaxia-practical-wisdom",
        "准入定界",
        "只读理解",
        "规则装载",
        "规则装载 / 红线",
        "业务架构裁决",
        "代码坏味道细查",
        "工具补扫",
        "修复验证",
        "回流收口",
        "遵循编码规范",
        "不踩红线",
        "高屋建瓴",
        "深入细节",
        "业务语义",
        "架构边界",
        "设计原则",
        "代码坏味道",
        "整洁代码与架构实现",
        "Open Code Review / OCR",
        "Ponytail",
        "Gemini CLI",
        "AgentRC",
        "Understand Anything",
        "证据源，不是最终 CR",
        "Wind/Nobe 专项",
        "wind-coding-conventions",
        "coding-review-deep-dive.md",
        "testing.md",
        "经典镜片只补工程取舍问题",
        "不参与最终源码裁决",
        "未采纳工具建议",
        "残余风险",
    ),
)

expected_handling_has(
    "wind-coding-conventions-should-trigger-opt-in",
    (
        "Java/Wind 编码约规规则检查",
        "项目已声明 Wind 约规作为高置信度信号",
        "wind-coding-conventions.md 专项规则",
        "查询字段命名",
        "get/find/query 服务查询方法",
        "/inc/basic 与 /inc/secure 内网 API",
        "系统字典/国际化",
        "适用层级",
        "上下文证据",
        "触发约规",
        "java-coding-conventions.md",
        "wind-architecture-patterns.md",
        "先读取 java-coding-conventions.md 通用层",
        "源码级设计、TDD、CR、调试、测试策略和生产风险继续交给资深架构师",
    ),
)

expected_handling_has(
    "wind-coding-conventions-should-trigger-agents-template",
    (
        "Wind 项目 AGENTS 初始化",
        "知止者做项目约规入口编排",
        "wind-project-agents-template.md",
        "AGENTS.md 草案",
        "项目事实待确认项",
        "授权边界",
        "验收标准",
        "不猜测构建命令、生产流程、模块事实或 Git 授权",
    ),
)

expected_handling_has(
    "wind-coding-conventions-should-reject-speculative-locking",
    (
        "Wind 基础服务并发与锁边界检查",
        "区分唯一性、带前置状态的状态流转和一般读改写",
        "不得仅因未来可能并发预埋本地锁、分布式锁或锁 Wrapper",
        "分别优先使用表内业务 UK 或联合 UK、原子条件更新和乐观锁",
        "事务只保证本地操作的原子提交和回滚",
        "普通 SELECT -> Java 校验 -> UPDATE 即使使用 @Transactional 也不能单独防止丢失更新",
        "明确并发入口和冲突资源",
        "失败场景、测试或生产证据",
        "已验证持有者身份、安全释放、租约续期或有界执行语义的平台原语",
        "fencing/version 防护",
        "没有这些证据时删除预埋锁",
        "不复制固定租约的通用代码模板",
    ),
)

expected_handling_has(
    "wind-coding-conventions-should-separate-business-uniqueness-from-request-idempotency",
    (
        "Wind 幂等与业务唯一性分层检查",
        "表内业务 UK、联合 UK、状态条件或版本约束",
        "外部 Idempotency-Key/requestSn 可以用于请求重放去重",
        "不得冒充业务身份",
        "参数摘要、有效期、并发冲突、结果回放和过期后重用语义",
        "没有自然业务 UK 时不得为了形式完整虚构联合 UK",
        "不能机械要求所有请求幂等键与业务 UK 合并",
    ),
)

expected_handling_has(
    "wise-agent-should-route-practical-design-documents",
    (
        "核心名相",
        "场景与流程",
        "状态与业务规则",
        "规则落地表",
        "工程承接",
        "验证证据",
        "Engineering Handoff Card",
        "名 -> 事 ->（图）-> 法 -> 器 -> 验",
        "最小关键图",
        "轻量任务可明确不需要单独画图",
        "图不是新的事实源",
        "局部、行为保持且可测试的重构不创建正式重构设计文档",
    ),
)

expected_handling_has(
    "wise-agent-should-keep-lightweight-refund-on-generic-product-path",
    (
        "知止者保持统一行动主体",
        "产品通用能力",
        "工程测试视角",
        "单个退款词不等于支付专项证据",
        "不读取 payment-scenario-routing",
        "不展开整棵垂直知识树",
    ),
)

expected_handling_has(
    "wise-agent-should-use-optional-reference-index",
    (
        "参考资料与证据索引",
        "链接或路径",
        "Markdown 链接",
        "引用标识为可选",
        "轻量文档可不单独展开",
        "不把 AI 推理、讨论草稿和被拒方案列为正式参考资料",
    ),
)

expected_handling_has(
    "senior-should-standalone-refactoring-design-for-migration",
    (
        "独立重构设计",
        "行为不变量",
        "MIG 切片",
        "双写",
        "回填",
        "灰度切流",
        "旧能力下线条件",
        "特征测试",
        "契约测试",
        "回滚",
    ),
)

expected_handling_has(
    "senior-should-skip-refactoring-document-for-local-change",
    (
        "不创建正式重构设计文档",
        "实现任务卡",
        "行为不变量",
        "验证命令",
        "最小修改",
        "不新增抽象层",
    ),
)

check(
    "document authoring has scoped routes and deterministic validation",
    (ROOT / document_skill).exists()
    and (ROOT / document_agent).exists()
    and has_all(
        document_skill,
        [
            "正式报告、制度、手册、研究说明、总结",
            "由 `product-architecture-expert` 主责",
            "由 `senior-software-architect` 主责",
            "交给 `hanzi-philology`",
            "scripts/check_document_deliverable.py",
            "所有正式文档都遵守无背景色",
            "scripts/check_document_style.py",
            "不判断事实正确",
        ],
    )
    and has_all(document_routing, ["复合任务", "载体转换不得改变领域结论"])
    and has_all(
        "document-authoring/references/format-and-rendering.md",
        [
            "页图出现方框、缺字或字体替换时",
            "即使 PDF 文本可提取也判定失败",
            "回退 Markdown",
            "不添加背景色、底纹、色块、渐变或荧光笔效果",
            "默认只用加粗",
            "表头不加底色，不使用斑马纹",
            "标题层级、留白、短段落和对齐",
            "不使用装饰性文本框、卡片或横幅",
            "所有正式文档均读取",
            "scripts/check_document_style.py --file <path>",
        ],
    )
    and (ROOT / document_style_checker).exists()
    and has_all(
        document_style_checker,
        ["TEXT_SUFFIXES", "docx_style_violations", "background_style", "docx_shading", "run_self_test"],
    )
    and has_all(
        document_checker,
        [
            "SELF_TESTS",
            '"report"',
            '"policy"',
            '"manual"',
            '"research-note"',
            "invalid-placeholder-report.md",
            "placeholder_required_fields",
            "common placeholder variant unexpectedly passed",
        ],
    ),
)

check(
    "hanzi philology enforces multi-source evidence and Shuowen boundary",
    (ROOT / hanzi_skill).exists()
    and (ROOT / hanzi_agent).exists()
    and has_all(
        hanzi_skill,
        [
            "不设单一权威书",
            "《说文解字》只作为汉代字书和传统解释材料之一",
            "形、音、义、辞例和时代必须互证",
            "材料可证、传统训释、现代通说、争议或待考",
            "scripts/check_philology_evidence.py",
            "交给 `document-authoring`",
        ],
    )
    and has_all(hanzi_evidence_method, ["出土材料", "传世文献", "传统训释", "音韵材料", "现代研究"])
    and has_all(
        hanzi_source_map,
        [
            "2026-07-16",
            "https://xiaoxue.iis.sinica.edu.tw/guide/",
            "https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/",
            "https://ctext.org/introduction/zh",
            "不批量下载",
        ],
    )
    and has_all(
        hanzi_checker,
        [
            "SELF_TESTS",
            "invalid-placeholder-character-form.md",
            "invalid-negated-shuowen-overclaim.md",
            "placeholder_required_fields",
            "shuowen_single_source_overreach",
            "common placeholder variant unexpectedly passed",
            "negated Shuowen overclaim was rejected",
            "contrastive negation bypassed Shuowen overclaim guard",
            "negated evidence bypassed Shuowen overclaim guard",
        ],
    ),
)

check(
    "wise agent routes document and philology owners",
    has_all(wise_agent_skill, WISE_AGENT_CORE_TERMS)
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "专业文档撰写",
            "汉字学与训诂",
            "训诂证据卡",
            "不设单一权威书",
        ],
    ),
)

check(
    "product and architecture documents preserve domain ownership across authoring",
    has_all(
        product_skill,
        [
            "结论稳定后可协同 `document-authoring`",
            "重新运行产品交付物检查",
            "`hanzi-philology` 只在命名确有古文、字源或训诂证据问题时按需参与",
        ],
    )
    and has_all(
        senior_skill,
        [
            "结论稳定后可协同 `document-authoring`",
            "重新运行架构交付物检查",
            "不得改动接口、字段、状态、规则编号或验证语义",
        ],
    )
    and has_all(
        document_routing,
        [
            "同一权威版本",
            "重新运行领域 Skill 的交付物检查",
            "只对实际派生载体执行渲染检查",
        ],
    ),
)

check(
    "philology is optional evidence for product terms and excluded from engineering naming",
    has_all(
        hanzi_skill,
        [
            "业务名相确有古文、字源或训诂证据问题",
            "只提供命名证据",
            "不得替代产品判断",
            "API、类名、方法名、字段名和数据库命名",
        ],
    )
    and has_all(
        wise_agent_skill_type_owner_routing,
        [
            "可选证据协作者",
            "领域统一语言",
            "重新运行产品或架构交付物检查",
        ],
    ),
)

expected_handling_has(
    "wise-agent-should-explain-zhizhi-canonical-name",
    ("目标止点", "权限边界", "完成证据", "停止 / 交还条件", "知止不是不行", "察 -> 辨 -> 谋 -> 行 -> 验 -> 化", "本义就是行走"),
)
expected_handling_has(
    "document-authoring-should-formalize-report",
    (
        "文档契约",
        "目标读者",
        "事实源",
        "事实、推断、待确认",
        "owner",
        "所有正式文档",
        "不添加背景色或底纹",
        "只对重要描述或概念名词加粗",
        "结构检查通过",
    ),
)
expected_handling_has(
    "document-authoring-should-review-and-deliver-docx",
    (
        "权威版本",
        "冲突",
        "DOCX",
        "不添加背景色或底纹",
        "只对重要描述或概念名词加粗",
        "逐页检查",
        "文本截断",
        "视觉验收",
    ),
)
expected_handling_has(
    "product-should-collaborate-with-document-authoring",
    ("产品架构专家保持产品语义和正文主责", "同一权威版本", "不得改变产品结论", "重新运行产品交付物检查", "文档结构、渲染检查"),
)
expected_handling_has(
    "senior-should-collaborate-with-document-authoring",
    ("资深架构师保持系分和工程结论主责", "同一权威版本", "不得改动接口、字段、状态、规则编号或验证语义", "重新运行架构交付物检查", "文档结构、渲染检查"),
)
expected_handling_has(
    "hanzi-philology-should-analyze-character-forms",
    ("合集号", "器号", "隶定", "音韵", "反证", "待考"),
)
expected_handling_has(
    "hanzi-philology-should-exegesis-with-multiple-sources",
    ("底本", "异文", "《尔雅》", "《说文解字》", "音韵", "不设单一权威书"),
)
expected_handling_has(
    "hanzi-philology-should-block-shuowen-overclaim",
    ("拒绝单一证据越权", "合集号或器号", "传统训释", "争议或待考"),
)
expected_handling_has(
    "hanzi-philology-should-support-product-term-evidence",
    ("可选命名证据协作者", "训诂证据卡中的命名证据", "产品架构专家", "领域统一语言", "训诂不得替代产品判断"),
)
expected_handling_has(
    "grill-me-should-stress-test-with-question-ledger",
    ("独立 grill-me 能力", "建立问题台账", "一次只问一个主 blocker", "推荐答案", "最终结论", "shared understanding 前不执行"),
)
expected_handling_has(
    "grill-me-should-review-history-before-next-question",
    ("历史去重路径", "恢复已确认、已排除、待确认和红线", "语义重复", "不得复问", "证据变化、结论冲突或风险升级"),
)
expected_handling_has(
    "grill-me-should-self-decide-from-authoritative-evidence",
    ("Facts 与 Decisions", "权威证据", "自决并写入问题台账", "新的价值取舍、公共契约、高风险事项和红线", "证据冲突时停止覆盖"),
)
expected_handling_has(
    "grill-me-should-decide-whether-to-ask-from-project-evidence",
    ("证据先行的问询裁决路径", "意图与约束", "当前实现", "历史决策", "风险与红线", "裁决动作", "唯一的最终结论状态", "同时原样输出裁决动作与最终结论", "fact-confirmed", "decision-reused", "self-decided", "ask-owner", "剩余 Decision"),
)
behavior_contract_has(
    "grill-me-should-decide-whether-to-ask-from-project-evidence",
    ("evidence_gate", "decision_actions", "ask_gate", "ledger_must_include", "must_not_do"),
    ("待裁决命题", "命题类型", "证据锚点", "证据冲突", "裁决动作", "置信边界", "不得把知识库或当前代码天然视为业务真相"),
)
expected_handling_has(
    "grill-me-should-continue-after-partially-confirmed-history",
    ("剩余 Decision 路径", "decision-reused / confirmed", "不因出现已确认内容而整体退出 grill-me", "ask-owner / pending", "一次只问 B", "统一写入同一状态模型"),
)
negative_reason_has(
    "grill-me-negative-factual-codebase-query",
    ("可从代码库直接查证", "没有未决方案或设计分叉", "不进入 grill-me"),
)
negative_reason_has(
    "grill-me-negative-confirmed-plan-execution",
    ("关键决策已经确认", "按授权执行和验证", "不得重新进入 grill-me"),
)
expected_handling_has(
    "huaxia-practical-wisdom-should-calibrate-real-world-decision",
    ("现实决策校准路径", "事实、推断和待确认", "察实、正名、审时、权衡、行验、化", "经世决策卡", "最少必要框架", "行动、止损与验证", "经典原文、现代解释和现实类比分层"),
)
expected_handling_has(
    "huaxia-practical-wisdom-should-calibrate-without-explicit-name",
    ("现实决策与行动校准", "事实、名相、时势、取舍、行动、止损和验证", "没有可靠经典出处时不写成原文", "明确待确认"),
)
expected_handling_has(
    "huaxia-practical-wisdom-should-trigger-old-ancestor-alias",
    ("自然语言别名", "事实和待确认", "最小可逆行动、止损和验证", "不只讲古语"),
)
negative_reason_has(
    "huaxia-practical-wisdom-negative-ordinary-code-review",
    ("普通工程词不能触发", "senior-software-architect", "工程证据"),
)
negative_reason_has(
    "huaxia-practical-wisdom-negative-classical-exegesis",
    ("古籍文本、异文和训诂考据", "hanzi-philology", "不得越权解释文本"),
)
negative_reason_has(
    "huaxia-practical-wisdom-negative-medical-diagnosis",
    ("不提供医学诊断或治疗", "高风险症状", "合格医疗专业人员"),
)
expected_handling_has(
    "wise-agent-should-direct-lightweight-local-edit",
    ("直接完成", "不展开完整 SDLC", "不装载 Superpowers", "不派 Worker", "不创建 Goal"),
)
expected_handling_has(
    "wise-agent-should-resume-from-state-contract",
    ("D-1", "B 不得复活", "C 不得脑补", "check_state_contract.py", "不靠模型记忆猜测"),
)
expected_handling_has(
    "wise-agent-should-select-control-mechanisms-by-evidence",
    ("SDLC 作为跨阶段地图", "Goal 作为跨轮目标", "状态载体", "低耦合时才派 Worker", "独立 Checker", "不是顺序阶段"),
)
expected_handling_has(
    "wise-agent-should-avoid-worker-for-coupled-task",
    ("保持单体工作", "不满足 Worker 准入", "不派 Worker", "风险升高时才增加独立 Checker"),
)
expected_handling_has(
    "wise-agent-should-use-checker-without-worker",
    ("不派 Worker", "要求独立 Checker", "验证机制", "不替代发布 Owner"),
)
negative_reason_has(
    "wise-agent-negative-single-domain-prd",
    ("单一产品领域任务", "product-architecture-expert", "不为维持默认人格概念额外加载 wise-agent"),
)
negative_reason_has(
    "wise-agent-negative-single-domain-system-design",
    ("单一工程设计任务", "senior-software-architect", "不额外加载 wise-agent"),
)
negative_reason_has(
    "wise-agent-negative-single-domain-source-review",
    ("单一源码 CR", "senior-software-architect", "不加载 wise-agent"),
)
negative_reason_has(
    "wise-agent-negative-single-domain-codegen",
    ("结构化 Java 代码生成任务", "java-service-code-generator", "不先加载 wise-agent"),
)
negative_reason_has(
    "wise-agent-negative-single-domain-document",
    ("单一正式成文任务", "document-authoring", "不加载 wise-agent"),
)
negative_reason_has(
    "wise-agent-negative-single-domain-philology",
    ("单一汉字学与训诂任务", "hanzi-philology", "不因需要证据互证就额外加载 wise-agent"),
)
negative_reason_has(
    "wise-agent-negative-single-domain-java-conventions",
    ("纯 Java 约规任务", "wind-coding-conventions", "不升级为工程执行或 wise-agent 协同"),
)
negative_reason_has(
    "wise-agent-negative-simple-wording",
    ("一步措辞改写", "不加载知止者工作闭环"),
)
negative_reason_has(
    "wise-agent-negative-simple-definition",
    ("简单定义问答", "不触发知止者"),
)
negative_reason_has(
    "wise-agent-negative-simple-synonyms",
    ("一步语言生成", "直接回答"),
)

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} {name}")

if failed:
    raise SystemExit("Trigger-path validation failed:\n" + "\n".join(f"- {name}" for name in failed))

print("Trigger-path validation passed.")
