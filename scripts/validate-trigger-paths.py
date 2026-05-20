#!/usr/bin/env python3
"""Validate high-value skill trigger and reference routing invariants.

This is a small regression guard for the repo's most important skill routes.
It is not a natural-language router or a complete prompt evaluation suite.
Keep checks focused on durable invariants that should survive wording changes.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


checks: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    checks.append((name, bool(condition)))


def contains(path: str, text: str) -> bool:
    return text in read(path)


def has_all(path: str, texts: list[str]) -> bool:
    body = read(path)
    return all(text in body for text in texts)


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
    check(f"scenario fixture routes {name}", not missing)


senior_skill = "senior-software-architect/SKILL.md"
senior_routing = "senior-software-architect/references/scenario-routing.md"
workflow = "senior-software-architect/references/workflow.md"
ai_engineering = "senior-software-architect/references/ai-assisted-engineering.md"
testing = "senior-software-architect/references/testing.md"
coding = "senior-software-architect/references/coding-standards.md"
review = "senior-software-architect/references/coding-review-deep-dive.md"

product_skill = "product-architecture-expert/SKILL.md"
product_routing = "product-architecture-expert/references/product-scenario-routing.md"
product_prd = "product-architecture-expert/references/product-design-and-prd.md"
regulatory = "product-architecture-expert/references/regulatory-baseline.md"

reference_headers = [
    senior_routing,
    workflow,
    ai_engineering,
    testing,
    "senior-software-architect/references/debugging-diagnosis.md",
    product_routing,
    product_prd,
    regulatory,
]

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
    "regulatory baseline requires professional confirmation",
    has_all(
        regulatory,
        [
            "待法务/合规/财务/通道/持牌机构确认项",
            "不得写成确定性上线依据",
        ],
    ),
)

scenario_fixtures: list[tuple[str, str, set[str]]] = [
    (
        "write tests",
        "给这个 Application Service 补一组 TDD 测试，先写失败测试",
        {"senior", "testing.md", "coding-standards.md", "workflow.md"},
    ),
    (
        "bug diagnosis",
        "线上出现 NullPointerException，帮我定位根因并补回归测试",
        {"senior", "debugging-diagnosis.md", "testing.md", "workflow.md"},
    ),
    (
        "AI coding CAD",
        "根据 OpenSpec 用多 Agent 推进这批代码实现，可以进入 CAD Mode 吗",
        {"senior", "workflow.md", "ai-assisted-engineering.md", "negative-constraints.md"},
    ),
    (
        "external sdk freshness",
        "升级 Gemini SDK 并确认最新 API 用法和兼容性",
        {"senior", "workflow.md", "adr-and-tradeoff.md", "production-readiness.md", "negative-constraints.md"},
    ),
    (
        "PRD",
        "帮我生成一份产品 PRD 模板，包含验收标准",
        {"product", "product-scenario-routing.md", "product-prd-template.md", "product-design-and-prd.md"},
    ),
    (
        "payment product",
        "设计商户清结算和对账产品方案，注意外部规则和合规",
        {"product", "payment-scenario-routing.md", "regulatory-baseline.md"},
    ),
]


def route_fixture(prompt: str) -> set[str]:
    route: set[str] = set()
    if any(
        word in prompt
        for word in [
            "代码",
            "测试",
            "TDD",
            "失败测试",
            "NullPointerException",
            "根因",
            "OpenSpec",
            "Agent",
            "CAD",
            "SDK",
            "API",
        ]
    ):
        route.add("senior")
    if any(word in prompt for word in ["产品", "PRD", "模板", "清结算", "对账", "合规", "商户"]):
        route.add("product")
    if any(word in prompt for word in ["测试", "TDD", "失败测试"]):
        route.update({"testing.md", "coding-standards.md", "workflow.md"})
    if any(word in prompt for word in ["NullPointerException", "根因", "线上"]):
        route.update({"debugging-diagnosis.md", "testing.md", "workflow.md"})
    if any(word in prompt for word in ["OpenSpec", "Agent", "CAD"]):
        route.update({"workflow.md", "ai-assisted-engineering.md", "negative-constraints.md"})
    if any(word in prompt for word in ["SDK", "API", "云产品", "版本", "升级"]):
        route.update({"workflow.md", "adr-and-tradeoff.md", "production-readiness.md", "negative-constraints.md"})
    if any(word in prompt for word in ["PRD", "模板"]):
        route.update({"product-scenario-routing.md", "product-prd-template.md", "product-design-and-prd.md"})
    if any(word in prompt for word in ["清结算", "对账", "支付", "资金", "商户", "合规"]):
        route.update({"payment-scenario-routing.md", "regulatory-baseline.md"})
    return route


for name, prompt, expected in scenario_fixtures:
    expected_subset(name, route_fixture(prompt), expected)

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} {name}")

if failed:
    raise SystemExit("Trigger-path validation failed:\n" + "\n".join(f"- {name}" for name in failed))

print("Trigger-path validation passed.")
