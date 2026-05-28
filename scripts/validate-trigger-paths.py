#!/usr/bin/env python3
"""Validate high-value skill trigger and reference routing invariants.

This is a small regression guard for the repo's most important skill routes.
It is not a natural-language router or a complete prompt evaluation suite.
Keep checks focused on durable invariants that should survive wording changes.
"""

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


def expected_subset(name: str, actual: set[str], expected: set[str]) -> None:
    missing = expected - actual
    detail = f" missing={sorted(missing)}" if missing else ""
    check(f"scenario fixture routes {name}{detail}", not missing)


def expected_absent(name: str, actual: set[str], unexpected: set[str]) -> None:
    present = unexpected & actual
    detail = f" present={sorted(present)}" if present else ""
    check(f"scenario fixture avoids {name}{detail}", not present)


senior_skill = "senior-software-architect/SKILL.md"
senior_agent = "senior-software-architect/agents/openai.yaml"
senior_routing = "senior-software-architect/references/scenario-routing.md"
senior_diagram = "senior-software-architect/references/diagram-output.md"
workflow = "senior-software-architect/references/workflow.md"
ai_engineering = "senior-software-architect/references/ai-assisted-engineering.md"
cad_mode = "senior-software-architect/references/cad-mode.md"
negative_constraints = "senior-software-architect/references/negative-constraints.md"
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
architecture_fixture_verifier = "senior-software-architect/scripts/verify_fixtures.py"
reference_index_audit = "scripts/audit-reference-indexes.py"
source_archive = "scripts/archive-source-evidence.py"
source_map_audit = "scripts/audit-source-map.py"
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
codegen_route = {"codegen", "code-generation-rules.md", "nobe-patterns.md", "generate_scaffold.py"}
codegen_safety_route = codegen_route | {"requires-confirmation"}
codegen_source_terms = ["CREATE TABLE", "DDL", "SQL", "建表语句", "schema", "字段表格", "字段说明", "Java 类", "表结构"]
codegen_action_terms = ["生成", "转换", "转成", "脚手架", "配套代码", "代码生成"]
codegen_target_terms = ["Wind/Nobe", "Service", "Mapper", "DTO", "Request", "Query", "Converter", "Entity", "代码"]
codegen_safety_terms = ["覆盖", "overwrite", "已有文件", "模块对不唯一", "多个 face/impl", "多个模块", "基础包名不唯一"]
product_terms = ["产品", "产品方案", "PRD", "模板", "原型", "页面截图", "页面说明", "交互稿", "反推 PRD", "反推需求", "验收种子", "交给架构师", "清结算", "对账", "合规", "商户", "SaaS", "B2B", "运营后台", "规则矩阵", "能力地图", "业务流程图", "资金流图", "外卡收单", "Mastercard", "商户到账"]
product_general_route_terms = ["产品方案", "验收种子", "交给架构师", "SaaS", "B2B", "业务流程", "业务流程图", "能力地图", "运营后台", "规则矩阵", "原型", "页面截图", "页面说明", "交互稿", "反推 PRD", "反推需求"]
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
]
external_dependency_terms = ["SDK", "API", "云产品", "版本", "升级"]
diagram_terms = ["画图", "图形化", "可视化", "架构图", "流程图", "时序图", "状态机", "ER 图", "类图", "部署图", "迁移图", "关系图", "资金流图"]

reference_headers = [
    senior_routing,
    senior_diagram,
    workflow,
    ai_engineering,
    testing,
    coding,
    knowledge_graph,
    debugging,
    product_routing,
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
] + project_governance_refs + testing_practice_refs + skill_tree_refs

for path in reference_headers:
    check(f"{path} has progressive-disclosure header", has_reference_header(path))

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
    "senior metadata triggers diagram output",
    all(
        term in frontmatter(senior_skill)
        for term in ["架构图", "时序图", "状态机", "默认产出 SVG", "Mermaid/Markdown 草图", "ADR", "生产变更", "陌生代码库"]
    ),
)
check(
    "senior openai yaml mentions visual output",
    has_all(senior_agent, ["默认输出 SVG", "Mermaid/Markdown 草图", "PNG/PDF/截图", "发布回滚和生产风险"]),
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
    "product metadata triggers diagram output",
    all(
        term in frontmatter(product_skill)
        for term in ["PRD", "需求说明", "原型/HTML/页面截图/交互稿反推 PRD", "产品架构图", "业务流程图", "状态机", "默认产出 SVG", "Mermaid/Markdown 草图", "外卡收单", "Mastercard", "合规待确认", "工程实现"]
    ),
)
check(
    "product openai yaml mentions visual output",
    has_all(product_agent, ["原型反推", "页面截图", "交互稿", "能力流程状态图", "默认输出 SVG", "Mermaid/Markdown 草图", "PNG/PDF/截图", "待确认项"]),
)
check(
    "product openai yaml mentions acquiring specialty",
    has_all(product_agent, ["支付资金与外卡收单专项"]),
)
check(
    "codegen metadata triggers only structured generation",
    has_all(
        codegen_skill,
        [
            "DDL/SQL",
            "schema 文件",
            "字段表格",
            "MyBatis-Flex Entity",
            "ServiceImpl",
            "仅在用户明确要求“生成/转换/脚手架/配套代码”时触发",
            "代码评审、Bug 修复和补测试优先交给架构师",
        ],
    )
    and has_all(
        "java-service-code-generator/agents/openai.yaml",
        [
            "DDL/schema",
            "字段表格",
            "Wind/Nobe Service 脚手架",
            "Entity、Mapper、DTO、Request、Query、Converter、Service 和 ServiceImpl",
        ],
    ),
)
check(
    "large references expose task-level reading indexes",
    all(
        has_all(
            path,
            [
                "## 按任务读取索引",
                "| 任务 | 优先读取 | 跳过 |",
            ],
        )
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
            "工程落点",
            "AI Agent Systems",
            "微信公众号文章《如何画架构图：技术负责人带你画技术（系统）架构》",
            "第二篇《如何画架构图：业务架构的画法》当前链接只能访问校验页",
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
            "## 视觉风格路由",
            "## 语义形状和箭头",
            "## 稳定提示配方",
            "默认使用 SVG 作为正式图形化交付物",
            "Mermaid/Markdown 草图",
            "正式图形化交付默认只生成 SVG",
            "PNG/PDF/截图等其他格式",
            "Finance Ledger",
            "支付资金四流",
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
            "### 先选哪个 Skill",
            "[资深架构师](./senior-software-architect)",
            "[产品架构专家](./product-architecture-expert)",
            "[java-service-code-generator](./java-service-code-generator)",
            "原型/HTML/页面截图/交互稿反推 PRD",
            "默认产出 SVG",
            "调用 `$fireworks-tech-graph` 续作",
            "## 5 分钟上手",
            "sync-skills.sh --dry-run all",
            "./scripts/validate.sh",
            "先定业务和验收",
            "根据页面截图反推可评审 PRD",
            "错误截图、日志截图、测试失败截图",
            "先输出到 /tmp/order-scaffold 评审目录",
            "### 常用组合路线",
            "从想法到工程",
            "从原型到 PRD",
            "从普通图到复杂图",
            "### 提示词公式",
            "用 <Skill 名称> + <任务类型> + <输入材料> + <目标产物> + <边界/风险> + <验证要求>",
            "### 常见误用",
            "不要让 `java-service-code-generator` 从纯自然语言直接生成生产代码",
            "不要把产品专家对支付、资金、卡组织或监管的输出当作最终合规结论",
            "## 维护者与高级扩展",
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
    "senior system design preserves business-driven validation route",
    has_all(
        "senior-software-architect/references/system-analysis-design.md",
        [
            "PRD/产品方案到系分 / 业务驱动系统设计",
            "业务驱动追踪表",
            "质量属性场景",
            "业务 driver",
            "系统边界、模块、接口、数据、质量属性和测试",
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
            "CAD Mode、Execution Grant 或自动分轮推进必须继续读取 `cad-mode.md`",
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
            "不得把“用户说继续”解释为跳过 OpenSpec、Harness Plan、Execution Grant、验证或高风险人工确认点",
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
            "不得把“用户说继续”解释为跳过 OpenSpec、Harness Plan、Execution Grant、验证或高风险人工确认点",
            "AI 协作总纲不得复制这些细节",
        ],
    )
    and has_all(
        cad_mode,
        [
            "## 使用时机",
            "## 按任务读取索引",
            "受控自治开发模式",
            "Execution Grant 是 CAD Mode 的权限边界",
            "每轮执行闭环",
            "5 秒",
            "平台权限边界优先于 Execution Grant",
        ],
    ),
)
check(
    "negative constraints routes CAD authority to CAD mode",
    has_all(
        negative_constraints,
        [
            "`cad-mode.md` 定义的 Execution Grant",
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
    "product architecture methodology keeps multi-frame exploration gate",
    has_all(
        product_architecture,
        [
            "## 2. 设计顺序",
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
            "通用产品架构与业务驱动验证",
            "官方规则与监管",
        ],
    ),
)
check(
    "product source map records business-driven product verification sources",
    has_all(
        product_source_map,
        [
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
            "优先级口径",
            "P0：没有它不能上线",
            "P1：核心体验或主流程必须具备",
            "P2：增强体验、运营效率或后续扩展能力",
            "产品到架构交接",
            "业务驱动架构交接",
            "product-architecture-methodology.md",
            "假设/问题ID",
            "需求ID",
            "验收种子ID",
            "质量属性ID",
            "验收种子交接矩阵",
            "发布后验证",
            "业务驱动架构交接包",
            "可代码化/可观测化/可评审化",
            "product-prd-quality-gates.md",
            "product-prd-financial-appendix.md",
            "product-prd-operations-and-data.md",
            "正式评审、提交前检查、CR、触发验证或符合性评审时读取 `product-prd-quality-gates.md`",
        ],
    )
    and has_all(
        product_prd_quality_gates,
        [
            "## 使用时机",
            "## 按任务读取索引",
            "## 1. PRD 质量门禁",
            "## 2. 可验收性门禁",
            "## 3. 已有 PRD 符合性评审输出",
            "符合项：已经满足模板、可验收性或专项门禁的内容",
            "必改：会阻断评审、研发、测试、上线或专业确认的缺口",
            "每条评审项必须说明章节或位置、问题、影响和建议改法",
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
            "Airwallex 类全球金融平台、Global Accounts、Connected Accounts、Global Treasury、BaaS、Payments for Platforms",
            "全球金融产品能力地图、平台账户/客户主体、账户收款、付款、发卡、嵌入式金融边界和待确认项",
            "全球付款、Payouts、受益人管理、付款审批、批量付款、付款失败和回执",
            "transfer / beneficiary / payer / batch / approval 对象模型、付款状态机、失败处理、回执和出款对账",
            "Airwallex 类全球金融平台能力分析",
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
            "PRD、产品架构方案和图形 brief",
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
            '"prd"',
            '"product-architecture"',
            '"diagram-brief"',
            "goal_and_scope",
            "risk_and_confirmation",
            "output_format",
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
        name="architecture diagram output",
        prompt="画一张系统架构图和状态机，说明工程落点和验证方式",
        routes={"senior", "diagram-output.md"},
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
    if contains_any(
        prompt,
        [
            "代码",
            "测试",
            "TDD",
            "失败测试",
            "陌生代码库",
            "架构现状",
            "接手侦察",
            "Node.js",
            "技术栈",
            "入口路径",
            "部署链路",
            "架构坏味",
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
        ],
    ):
        route.add("senior")
    if contains_any(prompt, ["陌生代码库", "架构现状", "接手侦察", "Node.js", "技术栈", "入口路径", "部署链路"]):
        route.update({"language-agnostic-architecture.md", "workflow.md"})
    if contains_any(prompt, ["架构坏味", "深度质量扫描", "上帝类", "循环依赖", "跨层调用", "事务边界混乱", "公共模块垃圾桶"]):
        route.update({"coding-review-deep-dive.md", "clean-code.md", "negative-constraints.md"})
        if contains_any(prompt, ["Java", "Spring"]):
            route.add("coding-standards.md")
    if contains_any(prompt, ["时间线", "5-Why", "故障复盘", "事故复盘", "线上复盘", "生产复盘", "回调大量超时", "影响面", "止血"]):
        route.update({"debugging-diagnosis.md", "production-readiness.md", "negative-constraints.md"})
    if contains_any(prompt, ["Spring Security", "CSRF", "CORS"]):
        route.update({"security-architecture.md", "negative-constraints.md"})
    if contains_any(prompt, product_terms):
        route.add("product")
    if contains_any(prompt, ["测试", "TDD", "失败测试"]):
        route.update({"testing.md", "coding-standards.md", "workflow.md"})
    if contains_any(prompt, ["NullPointerException", "根因", "线上"]):
        route.update({"debugging-diagnosis.md", "testing.md", "workflow.md"})
    if contains_any(prompt, ["OpenSpec", "Agent", "CAD"]):
        route.update({"workflow.md", "ai-assisted-engineering.md", "negative-constraints.md"})
    if contains_any(prompt, ["CAD", "Execution Grant", "自动分轮", "自动提交"]):
        route.add("cad-mode.md")
    if contains_any(prompt, external_dependency_terms):
        route.update({"workflow.md", "adr-and-tradeoff.md", "production-readiness.md", "negative-constraints.md"})
    if contains_any(prompt, ["PRD", "模板"]):
        route.update({"product-scenario-routing.md", "product-prd-template.md", "product-design-and-prd.md"})
    if contains_any(prompt, payment_terms):
        route.update({"payment-scenario-routing.md", "regulatory-baseline.md"})
    if contains_any(prompt, product_general_route_terms):
        route.update({"product-scenario-routing.md"})
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

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} {name}")

if failed:
    raise SystemExit("Trigger-path validation failed:\n" + "\n".join(f"- {name}" for name in failed))

print("Trigger-path validation passed.")
