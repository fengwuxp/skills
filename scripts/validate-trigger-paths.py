#!/usr/bin/env python3
"""Validate high-value skill trigger and reference routing invariants.

This is a small regression guard for the repo's most important skill routes.
It is not a natural-language router or a complete prompt evaluation suite.
Keep checks focused on durable invariants that should survive wording changes.
"""

from typing import NamedTuple
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
testing = "senior-software-architect/references/testing.md"
coding = "senior-software-architect/references/coding-standards.md"
review = "senior-software-architect/references/coding-review-deep-dive.md"
debugging = "senior-software-architect/references/debugging-diagnosis.md"
language_agnostic = "senior-software-architect/references/language-agnostic-architecture.md"
security = "senior-software-architect/references/security-architecture.md"
architecture_deliverable_checker = "senior-software-architect/scripts/check_architecture_deliverable.py"
reference_index_audit = "scripts/audit-reference-indexes.py"
codegen_generator = "java-service-code-generator/scripts/generate_scaffold.py"
codegen_fixture_verifier = "java-service-code-generator/scripts/verify_fixtures.py"
codegen_rules = "java-service-code-generator/references/code-generation-rules.md"
project_governance_refs = [
    "senior-software-architect/references/project-governance-codebase-and-modules.md",
    "senior-software-architect/references/project-governance-service-api-modeling.md",
    "senior-software-architect/references/project-governance-data-security-quality.md",
    "senior-software-architect/references/project-governance-delivery-and-platform.md",
]
testing_practice_refs = [
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
product_diagram = "product-architecture-expert/references/diagram-output.md"
product_prd = "product-architecture-expert/references/product-design-and-prd.md"
regulatory = "product-architecture-expert/references/regulatory-baseline.md"
payment_methodology = "product-architecture-expert/references/payment-methodology.md"
clearing_settlement = "product-architecture-expert/references/clearing-settlement.md"
global_payment = "product-architecture-expert/references/global-payment-emerging.md"
card_network = "product-architecture-expert/references/card-network-and-card-rails.md"
payment_risk = "product-architecture-expert/references/payment-risk-fraud-and-merchant-operations.md"
payment_routing = "product-architecture-expert/references/payment-scenario-routing.md"
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
product_terms = ["产品", "PRD", "模板", "清结算", "对账", "合规", "商户", "SaaS", "B2B", "运营后台", "规则矩阵", "能力地图", "业务流程图", "资金流图", "外卡收单", "Mastercard", "商户到账"]
product_general_route_terms = ["SaaS", "B2B", "业务流程", "业务流程图", "能力地图", "运营后台", "规则矩阵"]
payment_terms = ["清结算", "对账", "支付", "资金", "商户", "合规", "外卡收单", "Mastercard", "Clearing Core", "Financial Presentment", "商户到账", "merchant payout", "收单风控"]
external_dependency_terms = ["SDK", "API", "云产品", "版本", "升级"]
diagram_terms = ["画图", "图形化", "可视化", "架构图", "流程图", "时序图", "状态机", "ER 图", "类图", "部署图", "迁移图", "关系图", "资金流图"]

reference_headers = [
    senior_routing,
    senior_diagram,
    workflow,
    ai_engineering,
    testing,
    debugging,
    product_routing,
    payment_routing,
    product_diagram,
    product_prd,
    regulatory,
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
    "product metadata triggers diagram output",
    all(
        term in frontmatter(product_skill)
        for term in ["PRD", "需求说明", "产品架构图", "业务流程图", "状态机", "默认产出 SVG", "Mermaid/Markdown 草图", "外卡收单", "Mastercard", "合规待确认", "工程实现"]
    ),
)
check(
    "product openai yaml mentions visual output",
    has_all(product_agent, ["能力流程状态图", "默认输出 SVG", "Mermaid/Markdown 草图", "PNG/PDF/截图", "待确认项"]),
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
            "senior-software-architect/references/system-analysis-design.md",
            "senior-software-architect/references/ai-assisted-engineering.md",
            "senior-software-architect/references/knowledge-graph.md",
            "senior-software-architect/references/coding-standards.md",
            "product-architecture-expert/references/product-prd-template.md",
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
    "workflow routes AI/CAD to AI engineering reference",
    contains(workflow, "AI 协作、多 Agent 或 CAD Mode 必须继续读取 `ai-assisted-engineering.md`"),
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
    has_all(product_routing, ["product-prd-template.md", "product-design-and-prd.md"]),
)
check(
    "PRD generation gate points to semantic gate",
    has_all(product_prd, ["## 0.1 PRD 生成门禁", "产品语义门禁"]),
)
check(
    "payment route keeps regulatory baseline",
    has_all(product_routing, ["payment-scenario-routing.md", "regulatory-baseline.md"]),
)
check(
    "product route sends payment clearing ecosystem to clearing reference",
    has_all(
        "product-architecture-expert/references/payment-scenario-routing.md",
        [
            "支付清算生态、网联/银联/央行/银行、备付金、跨机构清算",
            "生态参与者分层、跨机构清算链路、备付金/额度口径、待专业确认项",
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
            "卡网络角色定位、授权核心、清算账务承接、商户可用资金、结算净额和风控闭环",
            "跨境支付、多币种、Swift/GPI、Nostro/Vostro、代理行、本地清算网络、外清内结",
            "跨境五层拆解、资金流、币种/汇率/费用、合规待确认项",
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
            "卡组织清结算：四方/三方模式、BIN/IIN 路由、授权前置裁决、Authorization Core、Stand-In/SAF、open-to-buy、Financial Presentment、Matching/ARN、费用拆分、Posting、结算与网络费用",
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
            "https://mp.weixin.qq.com/s/7sZhZPeBE7XmBLjik8al8w",
            "支付系统五层拆解、支付核心主流程、收银台、路由、通道管理、退款和广义通道",
            "https://mp.weixin.qq.com/s/4P1PuButME_rr5anXeK2ng",
            "支付清算生态分层、交易平台七段链路、跨机构清算、备付金/额度口径",
            "https://mp.weixin.qq.com/s/86gPuhw8eUYb65gRhALH6A",
            "全球支付清算基础、Nostro/Vostro、外清内结、清算行/代理行/NRA 模式",
            "https://mp.weixin.qq.com/s/FM6h2bbN5xLXZQLJYG-cWg",
            "全球支付信息流和资金流五层拆解",
            "https://mp.weixin.qq.com/s/r2bUyLICOvWV40GOIfBbGw",
            "支付账本观、多套账本、清算/结算双层",
            "https://mp.weixin.qq.com/s/atTMCmIoQaG0EIsed2TATg",
            "支付知识体系主题索引和能力地图校准",
            "https://mp.weixin.qq.com/s/NVmy4mKSB83bP18u6XEzHA",
            "卡组织支付清结算、四方/三方模式、BIN/IIN 路由",
            "https://mp.weixin.qq.com/s/ZhKc64tXXguEFJYxozuMtw",
            "三方支付机构全链路",
            "https://mp.weixin.qq.com/s/04oIhVhypiZv7sRWygtOoA",
            "会计恒等式、会计循环、总账/明细账",
            "https://mp.weixin.qq.com/s/WWhjG9ACi3qmqeqPFvBaaA",
            "账务核心架构、账户体系、热点账户",
            "https://mp.weixin.qq.com/s/FVx1lUcxCF3jUl0Xh6UydA",
            "支付合规、KYC/KYB/KYT/KYA",
            "https://mp.weixin.qq.com/s/vQh7wUILKVTLP9xq6xDvmw",
            "清算、结算、清结算在理论、机构命名、平台产品和内部核算语境中的差异",
            "https://mp.weixin.qq.com/s/Dh22dNM6Ze4fHgytthN0ng",
            "Mastercard 授权作为网络级前置裁决、授权消息家族、Stand-In/SAF/Advice/Reversal、open-to-buy 管理、Trace ID 和授权数据准确性",
            "https://mp.weixin.qq.com/s/gyLFP4J0syasU4DahMYy9A",
            "Mastercard 作为 payment network、transaction processing、participant role、responsibility management、cost/billing 和 network governance 的能力栈视角",
            "https://mp.weixin.qq.com/s/rgZSbR_2zfkISFhSuHmMPg",
            "Authorization Core、Authorization Lifecycle、Hold/Reference Chain、network session boundary、ISO 8583 semantic carrier、scheme adapter、SAF recovery 和授权可观测性",
            "https://mp.weixin.qq.com/s/uuEwioL-Xx3JKeGvG7AyCg",
            "Clearing 不是文件状态更新，而是 Financial Presentment、账务确认、费用责任和后续争议追溯的入口",
            "https://mp.weixin.qq.com/s/iSvq8LO0zjHlW20ZUf_S6Q",
            "Matching Core、ARN / Reference Model、Fee & Amount Decomposition、Posting Model、异常隔离和清算到账务承接",
            "https://mp.weixin.qq.com/s/Y1O4BsLo4DD0HgkKYSRQnw",
            "外卡收单中 authorization、clearing、settlement 的语义差异，以及清算连接交易、账务、费用、责任、对账和争议的产品视角",
            "https://mp.weixin.qq.com/s/hilJTPiiakSQvDLYAzHtuA",
            "settlement 不是商户打款动作，而是 network member settlement、platform allocation/netting、merchant payout、bank arrival、risk reserve、delayed settlement 和商户可用资金管理",
            "https://mp.weixin.qq.com/s/MXKNyFtROB-F-mEM1nNoPQ",
            "外卡收单风控贯穿 merchant onboarding、transaction、capture / fulfillment、settlement、dispute feedback 和 funds strategy，而不是单点交易拦截",
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
        name="bug diagnosis",
        prompt="线上出现 NullPointerException，帮我定位根因并补回归测试",
        routes={"senior", "debugging-diagnosis.md", "testing.md", "workflow.md"},
    ),
    RouteFixture(
        name="AI coding CAD",
        prompt="根据 OpenSpec 用多 Agent 推进这批代码实现，可以进入 CAD Mode 吗",
        routes={"senior", "workflow.md", "ai-assisted-engineering.md", "negative-constraints.md"},
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
        name="payment product",
        prompt="设计商户清结算和对账产品方案，注意外部规则和合规",
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
