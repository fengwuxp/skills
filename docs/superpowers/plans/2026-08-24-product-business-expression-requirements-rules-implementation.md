# 产品专家业务表达、需求与规则能力增强实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `product-architecture-expert` 建立业务表达、原子需求和业务规则的单一契约，增强 PRD 模板，并以可复现负例、确定性检查和静态行为 case 守住边界。

**Architecture:** `product-design-and-prd.md` 持有唯一详细契约；PRD 模板只投影可填写结构；方法论与 Skill 入口只路由。现有 `check_product_deliverable.py` 只增加可确定的字段、引用和明显模糊表达检查，业务正确性继续交行为评测与人工走读。

**Tech Stack:** Markdown、Python 3 标准库、现有 `evaluate-skill-behavior.py` 和仓库校验脚本；不增加依赖，不安装外部 Skill。

**Execution Boundary:** 用户已授权在当前工作区实施，但未授权 Git commit、push、同步或安装。本计划不创建分支、不提交、不推送。

---

### Task 1: 用 PRD 负例建立 RED 基线

**Files:**
- Create: `product-architecture-expert/fixtures/prd-invalid-ambiguous-rule.md`
- Create: `product-architecture-expert/fixtures/prd-invalid-requirement-contract.md`
- Create: `product-architecture-expert/fixtures/prd-invalid-external-rule.md`
- Create: `product-architecture-expert/fixtures/prd-invalid-success-metric.md`
- Modify: `product-architecture-expert/scripts/verify_fixtures.py`

- [ ] **Step 1: 创建四个单一失败原因 fixture**

四个 fixture 均保留标准 PRD 的章节、场景和验收结构，只分别引入以下缺口：

```text
prd-invalid-ambiguous-rule.md
规则条件：按相关业务规则处理；视情况及时完成。
预期：ambiguous_rule_language

prd-invalid-requirement-contract.md
产品需求陈述只有“系统应审核并通知并生成报表”，缺主体条件、边界、来源和验收。
预期：requirement_contract_incomplete

prd-invalid-external-rule.md
声明版本化 / 外部规则，但缺来源、版本、生效范围、Owner 和未确认前处理。
预期：external_rule_governance_missing

prd-invalid-success-metric.md
成功指标只有“提升审核效率、结果可观察”。
预期：success_metric_incomplete
```

- [ ] **Step 2: 把负例登记到 fixture verifier**

在 `CASES` 中加入：

```python
(
    "prd",
    FIXTURES / "prd-invalid-ambiguous-rule.md",
    False,
    {"ambiguous_rule_language"},
),
(
    "prd",
    FIXTURES / "prd-invalid-requirement-contract.md",
    False,
    {"requirement_contract_incomplete"},
),
(
    "prd",
    FIXTURES / "prd-invalid-external-rule.md",
    False,
    {"external_rule_governance_missing"},
),
(
    "prd",
    FIXTURES / "prd-invalid-success-metric.md",
    False,
    {"success_metric_incomplete"},
),
```

- [ ] **Step 3: 运行 RED 验证**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 product-architecture-expert/scripts/verify_fixtures.py
```

Expected: FAIL；四个新 fixture 当前被错误放行，输出 `fixture expectation failed` 或缺少预期 failure code。确认失败来自能力缺失，不是文件语法错误。

### Task 2: 建立三契约唯一权威并增强 PRD 模板

**Files:**
- Modify: `product-architecture-expert/SKILL.md`
- Modify: `product-architecture-expert/references/product-design-and-prd.md`
- Modify: `product-architecture-expert/references/product-prd-template.md`
- Modify: `product-architecture-expert/references/product-prd-quality-gates.md`
- Modify: `product-architecture-expert/references/product-architecture-methodology.md`
- Modify: `product-architecture-expert/fixtures/prd-valid.md`

- [ ] **Step 1: 在唯一权威中增加一体三契约**

在 `product-design-and-prd.md` 增加一个可按任务检索的章节，完整定义：

```text
Business Expression Contract
目标读者 / 判断；事实 / 来源；问题 / 影响；产品判断 / 边界；承诺 / 非目标；推断 / 待确认 / Owner。

Requirement Statement Contract
名称；类型；责任主体；场景 / 前置状态；规范强度；行为或业务结果；度量 / 时限 / 边界；来源可靠性；关联规则；验收样例。

Business Rule Contract
名称；性质；动机；对象与范围；输入事实；当；则；Owner；正例 / 边界例 / 反例；复杂场景条件升级字段。
```

同时定义 `必须 / 不得 / 应 / 可 / 建议` 的规范强度，并明确需求、规则、流程、执行机制和验收证据的名相边界。

- [ ] **Step 2: 增强 PRD 模板而不增加平行权威**

在 `product-prd-template.md`：

```text
5.1 业务场景设计
5.2 产品能力与对象设计
5.3 产品需求陈述
```

`5.3` 只引用 Requirement Statement Contract 并给出填写槽位。`7.1` 只引用 Business Rule Contract，删除旧规则卡的缩水字段；简单规则用短卡，多规则比较用矩阵，复杂命中才用决策表。第 9 节验收摘要增加正常、边界、禁止、失败状态、恢复、数据/审计证据和验收 Owner。

- [ ] **Step 3: 对齐模板强度和质量门禁**

在 `product-prd-quality-gates.md` 增加：

```text
需求：适切、必要、原子、无歧义、自包含、可理解、可验证、可追踪。
规则：独立于流程、声明式、显式条件与结论、Owner、例外、版本和正反例。
读者走读：业务能复述，研发无需作者口述，测试能推导正反路径。
```

轻量 PRD 允许合并需求与规则，不强制独立规则卡；标准 / 增强 PRD 必须有产品需求陈述。

- [ ] **Step 4: 删除方法论中的平行 schema**

将 `product-architecture-methodology.md` 的独立规则矩阵收敛为使用时机和指针：

```text
业务规则详细契约以 product-design-and-prd.md 为唯一权威；本节只说明何时从简单规则升级为矩阵或决策表。
```

不复制三契约字段。

- [ ] **Step 5: 更新 Skill 路由摘要**

在 `SKILL.md` 的 PRD 路由中补一句：业务表达、正式需求陈述或业务规则描述任务读取 `product-design-and-prd.md` 的三契约；详细字段不进入入口正文。保持 frontmatter 和 `agents/openai.yaml` 不变。

- [ ] **Step 6: 提升有效 PRD fixture**

`prd-valid.md` 必须增加：

```text
成功指标：基线、目标、观察窗口、Owner。
产品需求陈述：类型、主体、前置状态、规范强度、行为结果、边界、来源和验收。
业务规则：性质、范围、条件、结论、Owner 和正反例。
```

避免仅用“提升效率”“可观察”“记录版本”等关键词。

- [ ] **Step 7: 检查文档单一权威和格式**

Run:

```bash
rg -n "Business Expression Contract|Requirement Statement Contract|Business Rule Contract" product-architecture-expert
rg -n '[[:blank:]]+$' product-architecture-expert/SKILL.md product-architecture-expert/references product-architecture-expert/fixtures
```

Expected: 三契约详细字段只在 `product-design-and-prd.md` 出现；模板和其它 reference 只有摘要与指针；无尾随空格。

### Task 3: 最小实现 PRD 语义反模式检查

**Files:**
- Modify: `product-architecture-expert/scripts/check_product_deliverable.py`

- [ ] **Step 1: 增加稳定字段组和模糊词常量**

使用现有 `field_values`、`table_column_values`、`section_body` 和 `normalize`，不增加 parser 类或依赖。新增：

```python
REQUIREMENT_FIELD_GROUPS = (
    ("requirement_type", ("需求类型",)),
    ("responsible_subject", ("责任主体", "主体")),
    ("requirement_context", ("场景 / 前置状态", "场景/前置状态", "前置条件")),
    ("normative_force", ("规范强度",)),
    ("required_outcome", ("要求的行为或业务结果", "行为或结果", "业务结果")),
    ("acceptance_example", ("验收样例", "验收引用")),
)

RULE_FIELD_GROUPS = (
    ("rule_type", ("规则性质",)),
    ("rule_scope", ("适用对象与范围", "适用场景 / 步骤", "适用场景/步骤")),
    ("rule_condition", ("当", "触发与判断条件", "条件")),
    ("rule_outcome", ("则", "处理结果", "结论")),
    ("rule_owner", ("Owner", "规则 Owner", "规则 owner")),
    ("rule_examples", ("正例 / 边界例 / 反例", "验收样例")),
)

AMBIGUOUS_BUSINESS_PHRASES = (
    "按相关规则处理", "视情况", "必要时", "适当", "及时", "合理", "尽快",
    "原则上", "包括但不限于",
)
```

- [ ] **Step 2: 增加最小检查函数**

实现：

```python
def requirement_contract_issues(text: str) -> list[str]: ...
def business_rule_contract_issues(text: str) -> list[str]: ...
def success_metric_issues(text: str) -> list[str]: ...
```

规则：

- 标准 / 增强 PRD 缺 `产品需求陈述` 或任一必需字段，返回 `requirement_contract_missing` 或 `requirement_contract_incomplete`。
- 正式需求或规则出现未定义的模糊词，分别返回 `ambiguous_requirement_language` 或 `ambiguous_rule_language`。
- 版本化 / 外部规则缺来源、版本、生效范围、Owner 或未确认前处理，返回 `external_rule_governance_missing`。
- 标准 / 增强 PRD 的成功指标缺基线、目标、观察窗口或 Owner，返回 `success_metric_incomplete`。
- 轻量 PRD 不强制独立需求 / 规则章节；模糊词只进入 `warning_groups`。

- [ ] **Step 3: 接入 `missing_groups` 与 warning**

在 `kind == "prd"` 分支中只对标准 / 增强调用三个检查函数；轻量 PRD 只把模糊表达映射为 `ambiguous_business_language` warning。

- [ ] **Step 4: 扩充 self-test**

内置 self-test 至少证明：

```text
有效标准 PRD 通过。
缺产品需求陈述失败。
“按相关业务规则处理”失败。
外部规则缺治理字段失败。
成功指标只有“提升效率”失败。
量化定义后的“及时”不因字面出现误报。
```

- [ ] **Step 5: 运行 GREEN 验证**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 product-architecture-expert/scripts/check_product_deliverable.py --self-test
env PYTHONDONTWRITEBYTECODE=1 python3 product-architecture-expert/scripts/verify_fixtures.py
```

Expected: self-test PASS；全部 product fixtures 按预期通过或失败。

- [ ] **Step 6: 运行单文件 CLI 验证**

Run:

```bash
python3 product-architecture-expert/scripts/check_product_deliverable.py --kind prd --file product-architecture-expert/fixtures/prd-valid.md
python3 product-architecture-expert/scripts/check_product_deliverable.py --kind prd --file product-architecture-expert/fixtures/prd-invalid-ambiguous-rule.md
```

Expected: valid 返回 0 并保留“仅通过结构检查”边界；ambiguous rule 返回 1 且包含 `ambiguous_rule_language`。

### Task 4: 增加行为 case，但不伪造行为证据

**Files:**
- Create: `fixtures/skill-eval/product-business-expression-requirements-behavior-cases.json`
- Modify: `scripts/validate.sh`
- Modify: `scripts/validate-trigger-paths.py`

- [ ] **Step 1: 编写八个行为 case**

case IDs：

```text
product-expression-should-separate-fact-judgment-and-pending
product-expression-should-translate-technical-question-to-business-decision
product-requirement-should-rewrite-ambiguous-language
product-requirement-should-split-compound-outcomes
product-rule-should-resolve-overlapping-rules
product-rule-should-block-stale-external-rule
product-requirement-should-keep-lightweight-scope
product-requirement-negative-marketing-or-implementation
```

source profile 只包含实际影响行为的当前文件：`SKILL.md`、三个 PRD reference 和检查器；生成后使用 `source_set_digest` 的实际值，不写占位 hash。

baseline 固定为本轮开始前的仓库提交，release gate 使用 `improvement`，要求 candidate blockers 为 0、正确性和安全性不回退、加权分提升且判断可审计。当前只创建 case contract，不创建 responses、scores 或 evidence-gate 登记。

- [ ] **Step 2: 接入静态行为 case 验证**

在 `scripts/validate.sh` 的 product checker 段增加：

```bash
run_gate scripts/evaluate-skill-behavior.py validate --cases "fixtures/skill-eval/product-business-expression-requirements-behavior-cases.json"
```

- [ ] **Step 3: 接入 trigger-path 静态边界**

`scripts/validate-trigger-paths.py` 检查：

```text
三契约名称与唯一权威可发现。
PRD 模板包含 5.3 产品需求陈述和增强验收摘要。
质量门禁包含适切、原子、无歧义、可验证和规则独立性。
检查器接入四个失败 code。
八个行为 case IDs 存在。
```

- [ ] **Step 4: 验证 case contract 与静态路由**

Run:

```bash
scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/product-business-expression-requirements-behavior-cases.json
env PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-trigger-paths.py
```

Expected: 两条命令返回 0。报告只能称 case contract 和静态路由通过，不能称行为能力提升。

### Task 5: 更新来源边界和回归接线

**Files:**
- Modify: `product-architecture-expert/references/source-map.md`
- Modify: `scripts/audit-skill-eval-fixtures.py` only if the new case requires explicit catalog registration
- Modify: `scripts/evaluate-skills.py` only if prompt coverage needs explicit invocation metadata

- [ ] **Step 1: 登记公开来源及未吸收内容**

在 `source-map.md` 登记 2026-08-24 实际读取状态：

```text
IREB CPRE 3.3.0：需求质量和自然语言陷阱。
Business Rules Manifesto：规则独立、声明式和一致性。
OMG DMN 1.5：复杂决策表与命中策略。
RFC 2119：仅借规范强度，不宣称适用标准。
Cucumber Example Mapping：规则、例子和未决问题。
product-on-purpose、platform-product-skills、Microsoft hve-core、mattpocock/to-prd：逐项记录吸收与拒绝边界。
```

不复制外部模板、Skill 正文或受限材料，不增加运行时依赖。

- [ ] **Step 2: 检查 prompt fixture 覆盖**

现有 `product-architecture-expert-should-produce-prd-from-user-research` 已覆盖业务 PRD 触发。只有缺少业务表达或规则专项正例时，才在 `prompt-cases.json` 增加一个正例和一个 hard negative；否则不改，避免重复覆盖。

- [ ] **Step 3: 运行轻量仓库检查**

Run:

```bash
ruby scripts/validate-skill-frontmatter.rb product-architecture-expert
python3 scripts/audit-skill-eval-fixtures.py
python3 scripts/evaluate-skills.py --self-test
scripts/audit-source-map.py
git diff --check
```

Expected: 全部返回 0。

### Task 6: 完整验证、CR 与证据边界复核

**Files:**
- Review only: all files changed by Tasks 1-5

- [ ] **Step 1: 运行产品专家聚焦验证**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile product-architecture-expert/scripts/check_product_deliverable.py product-architecture-expert/scripts/verify_fixtures.py
env PYTHONDONTWRITEBYTECODE=1 python3 product-architecture-expert/scripts/check_product_deliverable.py --self-test
env PYTHONDONTWRITEBYTECODE=1 python3 product-architecture-expert/scripts/verify_fixtures.py
scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/product-business-expression-requirements-behavior-cases.json
env PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-trigger-paths.py
```

Expected: 全部返回 0。

- [ ] **Step 2: 执行全仓验证**

Run:

```bash
bash scripts/validate.sh
```

Expected: 若失败，只接受有明确证据的既有 source drift 或与本改动无关的历史 blocker；新增产品 fixture、checker、case 和 trigger path 必须通过。不能把预期历史失败写成全绿。

- [ ] **Step 3: 做 scoped CR**

检查：

```text
是否出现第二套三契约字段。
模糊词检查是否把解释性文本误判为正式需求。
轻量 PRD 是否仍可裁剪。
检查器是否越界判断业务正确性。
行为 fixture 是否把静态校验写成行为提升。
source-map 是否记录版本、许可和未吸收边界。
```

- [ ] **Step 4: 回读最终 diff 和工作区**

Run:

```bash
git diff --stat
git diff --check
git status --short
```

Expected: 只包含本规格、实施计划、产品专家目标文件和必要验证接线；无 `__pycache__`、外部安装、同步产物、responses/scores 伪证据或 Git 提交。
