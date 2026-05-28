# 资深架构师知识图谱

本文是知识域定位器，不是百科全书。它只回答三个问题：当前问题属于哪个知识域、应优先读取哪个 reference、哪些细节可以跳过。

## 使用时机

- 需要判断问题属于哪个知识域、应读取哪个 reference。
- 需要把新经验归入架构、代码、测试、运维、AI 协作或项目治理知识域。
- 需要快速解释资深架构师能力图谱，而不是直接产出完整方案。

## 不适用场景

- 已经明确具体规则文件时，直接读取对应 reference。
- 需要完整编码规约、系分模板、测试专项或生产检查时，不在本文展开细节。
- 不把本文当作最终方法论来源；本文只做导航。

## 读取后必须产出

- 当前问题所属知识域。
- 优先 reference 和需要跳过的 reference。
- 后续验证方式或交付物入口。

## 需要继续读取的 reference

- 编码读 `coding-standards.md`，Review 读 `coding-review-deep-dive.md`。
- 测试读 `testing.md` 和 `testing-practices.md`。
- 系分读 `system-analysis-design.md`，完整模板读 `system-analysis-template.md`。
- 生产、发布和回滚读 `production-readiness.md` 与 `workflow.md`。
- 项目治理读 `project-governance-standards.md`，再按任务进入治理专题。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 定位知识域或 reference | 本文的知识域路由、归档规则 | 各领域专项细则 |
| 产品语义到工程映射 | `product-design.md`, `system-analysis-design.md` | 基础设施和 K8s 细节 |
| 架构设计、质量属性、取舍 | `architecture.md`, `adr-and-tradeoff.md`, `diagram-output.md` | Java 编码细则 |
| Java/Spring/Wind 设计或 Review | `coding-standards.md`, `wind-projects-patterns.md`, `project-governance-standards.md` | 通用能力解释 |
| 测试、TDD、验收验证 | `testing.md`, `testing-practices.md` | 平台治理细节 |
| 生产排障、安全、可观测性 | `debugging-diagnosis.md`, `production-readiness.md`, `security-architecture.md` | 产品语义细节 |
| AI 协作或 CAD Mode | `ai-assisted-engineering.md`, `cad-mode.md`, `workflow.md` | 语言运行时细节 |
| 经验沉淀或 Skill 维护 | 本文的归档规则、`source-map.md` | 具体业务方案细节 |

## 1. 根节点

```text
资深架构师知识图谱
├── 业务与产品语义
├── 架构设计与取舍
├── 系统分析与设计表达
├── 编码质量与 Java/Spring/Wind
├── 测试驱动设计与验证
├── 调试诊断与生产韧性
├── 安全、数据与合规边界
├── 平台、交付与项目治理
└── AI 编码协作与经验沉淀
```

## 2. 知识域路由

| 知识域 | 典型问题 | 优先 reference | 关键输出 |
| --- | --- | --- | --- |
| 业务与产品语义 | 目标、非目标、参与方、对象状态、验收种子 | `product-design.md`，复杂 PRD 交给 `产品架构专家` | 产品语义到工程资产追踪 |
| 架构设计与取舍 | 边界、抽象、依赖方向、质量属性、服务拆分 | `architecture.md`, `adr-and-tradeoff.md`, `distributed-consistency.md` | 方案、取舍、ADR、质量属性场景 |
| 系统分析与设计表达 | 系分、详细设计、视图、模板、评审门禁 | `system-analysis-design.md`, `system-analysis-template.md`, `diagram-output.md` | 可评审系分和图形 brief |
| 编码质量与 Java/Spring/Wind | 命名、异常、日志、契约、MapStruct、MyBatis Flex | `coding-standards.md`, `coding-review-deep-dive.md`, `wind-projects-patterns.md` | Review 结论、整改建议、验证命令 |
| 测试驱动设计与验证 | TDD、测试层级、失败测试、验收资产 | `testing.md`, `testing-practices.md` | 测试计划、失败测试候选、验证矩阵 |
| 调试诊断与生产韧性 | Bug、线上现象、根因、回滚、Runbook | `debugging-diagnosis.md`, `production-readiness.md`, `workflow.md` | 证据链、最小修复、回归验证 |
| 安全、数据与合规边界 | 认证授权、租户隔离、审计、敏感数据 | `security-architecture.md`, `negative-constraints.md` | 风险清单、控制点、确认方 |
| 平台、交付与项目治理 | 模块治理、API、Git/PR、K8s、演进 | `project-governance-standards.md`，再进入治理专题 | 治理结论、门禁、演进路径 |
| AI 编码协作与经验沉淀 | OpenSpec、Harness、CAD Mode、Skill 维护 | `ai-assisted-engineering.md`, `cad-mode.md`, `workflow.md`, `source-map.md` | 协作边界、授权门禁、来源边界 |

## 3. 典型判断路径

| 问题信号 | 先判断 | 再读取 |
| --- | --- | --- |
| “这个方案怎么设计” | 业务目标、边界、质量属性、验收是否清楚 | `product-design.md` -> `architecture.md` -> `system-analysis-design.md` |
| “代码这样写对不对” | 是否违反契约、边界、异常日志、测试红线 | `coding-review-deep-dive.md` -> `coding-standards.md` |
| “补测试 / TDD 推进” | 保护的业务事实、测试层级、第一批失败反馈 | `testing.md` -> 对应 `testing-practices-*` |
| “线上异常 / 测试失败” | 是否有可重复反馈环和证据链 | `debugging-diagnosis.md` -> `production-readiness.md` |
| “要不要拆服务/上中台/引入 MQ” | 业务边界、团队能力、运维成本和验证方式 | `architecture.md` -> `adr-and-tradeoff.md` |
| “外部 SDK/API/云产品版本变化” | 权威来源、版本、生效日期、本地依赖树 | `workflow.md` -> `adr-and-tradeoff.md` |

## 4. 经验归档规则

新增知识时先归位，避免把所有内容塞回本文：

| 经验类型 | 放置位置 |
| --- | --- |
| 架构原则、质量属性、服务边界 | `architecture.md` |
| 系分写法、模板、评审门禁 | `system-analysis-design.md` 或 `system-analysis-template.md` |
| Java/Spring/Wind 编码规则 | `coding-standards.md` 或 `wind-projects-patterns.md` |
| 测试策略和具体测试实践 | `testing.md` 或 `testing-practices.md` |
| 生产变更、发布、回滚、Runbook | `production-readiness.md` 或 `workflow.md` |
| 项目级治理细则 | `project-governance-standards.md` 及其专题文件 |
| 外部来源和吸收边界 | `source-map.md` |

## 5. 维护边界

- 本文只保留导航和归档规则，不沉淀专题长知识。
- 新增条目必须能指向一个权威 reference；没有权威 reference 时，先创建或补充专项文件。
- 与专项 reference 重复的知识，保留专项原文，本文只保留一句定位。
- 修改本文后运行 `scripts/audit-reference-indexes.py`、`python3 scripts/evaluate-skills.py --json` 和 `./scripts/validate.sh`。
