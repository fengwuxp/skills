# Skill 类型与 Owner 路由

本文把仓库级 `AGENTS.md` 的 Skill 类型接入门禁映射到 AI Native 产品到研发流程。它不新增顶层 Skill，而是帮助 `ai-native-engineering-workflow` 判断当前任务属于哪类能力、谁负责落地、需要什么交接物和验证证据。

## 使用时机

- 用户要求根据 Anthropic / Claude Code Skills 经验拆分、细化或治理 AI 流程、产品专家、架构师能力。
- 用户提出产品验证、代码质量、Runbook、CI/CD、团队自动化、模板脚手架、数据分析或基础设施操作等跨 Skill 任务。
- 需要判断是否新增 Skill、只扩展 reference、补脚本 / fixture，还是保留 AI Native 编排并路由到产品专家或架构师。

## 不适用场景

- 不直接产出 PRD、系分、代码、测试或生产变更；这些仍交给对应 Skill。
- 不把 Claude Code 内部 hooks、marketplace、持久化目录、usage measurement 机制写成本仓库默认能力。
- 不因为某类任务出现一次就新建顶层 Skill；只有触发稳定、产物独立、验证脚本明确、现有 Skill 承载过重时才评估拆分。

## 读取后必须产出

- 当前任务的主类型、默认 owner、协作 owner 和不应触发的 owner。
- 需要的交接物、验证证据、停止条件和回流位置。
- 建议是新增 reference、补脚本 / fixture、更新触发描述，还是未来再抽独立 Skill。

## 需要继续读取的 reference

- 产品到工程生命周期读 `product-to-engineering-lifecycle.md`。
- Agentic Engineering 治理读 `agentic-engineering-governance.md`。
- 验证、CR、发布和复盘读 `verification-review-release.md`。
- Superpowers 调度读 `superpowers-skill-library.md`。
- 产品侧上下文包读 `product-architecture-expert/references/ai-native-product-context.md`。
- 架构师 AI 协作和生产门禁读 `senior-software-architect/references/ai-assisted-engineering.md`、`production-readiness.md`。
- 三卡交接读 `product-to-engineering-lifecycle.md` 的 `3A. 三卡交接协议`，产品侧回 `Product Context Card`，工程侧回 `Engineering Handoff Card`，持续推进回 `Production Loop Card`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否要拆新 Skill | `1. 路由矩阵`、`2. 拆分门禁` | 不直接新建目录 |
| 产品验证和验收种子 | `1. 路由矩阵`、`3. 产品侧细化`，再读产品上下文包 | 不把验收实现交给产品专家 |
| 代码质量、Runbook、发布 | `1. 路由矩阵`、`4. 架构侧细化`，再读架构师 reference | 不让 AI Native 做源码级判断 |
| 流程可用性 CR | `5. 回流与验证` | 不只更新说明文字 |
| 产品/AI Native/架构师三卡交接 | `1. 路由矩阵`、`3. 产品侧细化`、`4. 架构侧细化` | 不让任一卡替代 Execution Grant、测试通过或上线审批 |

## 1. 路由矩阵

| Skill 类型 | AI Native 负责 | 产品专家负责 | 架构师负责 | 典型验证证据 |
| --- | --- | --- | --- | --- |
| `library / API reference` | 判断是否需要外部来源核验、时效性边界和工具准入。 | 定义业务术语、外部规则适用法域、产品侧口径。 | 定义 SDK/API 使用边界、版本风险、集成测试和 fallback。 | 官方来源、版本号、源码锚点、集成测试或手工核验。 |
| `product verification` | 编排验证矩阵、验收顺序、失败回退和 owner。 | 提供业务事实、用户旅程、验收种子、运营和数据验收。 | 把验收种子转成 TDD、契约测试、集成验证、监控指标。 | Given-When-Then、AC 映射、测试结果、运营核对。 |
| `data fetching and analysis` | 判断数据读取权限、字段口径 owner、分析结果能否进入决策。 | 定义指标、数据口径、业务解释和待确认项。 | 提供查询入口、数据血缘、审计、性能和安全边界。 | 数据源说明、查询脚本、字段口径、样本和复核记录。 |
| `business process and team automation` | 编排流程、责任、停止条件、交接和知识回流。 | 定义业务流程、协作节点、审批和运营动作。 | 定义自动化脚本、权限边界、失败重试、审计和回滚。 | RACI、流程图、dry-run、日志和人工确认点。 |
| `code scaffolding and templates` | 判断模板是否有 Spec、输入契约、覆盖风险和验收。 | 提供业务对象、字段、规则和验收样例。 | 负责系统设计、代码生成/改造、测试和项目约规。 | schema、模板输入、生成 diff、测试和静态检查。 |
| `code quality and review` | 编排 CR 前置条件、Review 视角、质量门禁和残余风险交接。 | 提供产品语义、业务规则和验收期望。 | 做源码级 CR、架构坏味、测试缺口、安全和生产风险判断。 | diff、源码锚点、测试结果、CR findings。 |
| `CI/CD and deployment` | 编排发布准入、验证顺序、授权边界和复盘回流。 | 提供上线业务目标、灰度用户、运营观察和验收口径。 | 负责构建、发布、灰度、监控、回滚和生产变更方案。 | CI 结果、发布计划、监控面板、回滚预案。 |
| `runbooks` | 编排症状到 owner 的路由、只读证据和升级条件。 | 提供业务影响、用户/运营反馈和恢复验收口径。 | 建立时间线、日志/指标/trace 路径、止血、恢复和复盘。 | 告警、request id、日志查询、影响面、恢复验证。 |
| `infrastructure operations` | 判断是否允许执行、是否需要显式授权、是否必须停止。 | 标明业务影响、窗口期、风险接受人和通知对象。 | 负责 dry-run、备份、分批、审计、回滚和执行脚本。 | dry-run 输出、备份、审批、审计、回滚记录。 |

## 2. 拆分门禁

优先级从低到高：

1. **只更新 reference**：任务只是细化现有 owner 的判断清单、模板或方法。
2. **补 fixture / validator**：任务容易触发错路由、遗漏验证或误把流程建议当授权。
3. **补脚本**：任务可确定、重复、容易写错，需要真实解析、生成或校验。
4. **新建顶层 Skill**：满足以下全部条件才考虑：触发词稳定、产物独立、owner 不属于现有产品/架构/代码生成 Skill、验证脚本明确、不会和 AI Native 主入口抢职责。

已拆出的稳定能力包：

- `wind-project-coding-conventions`：项目通过 `AGENTS.md` opt-in 后，作为 Wind/Nobe Java 项目编码约规的规则权威；AI Native 只负责流程编排，`资深架构师` 负责源码级设计、TDD、CR 和验证，`java-service-code-generator` 负责结构化代码生成。

专项 Skill 拆分先走 V 字判断：

- **向下拆清职责**：先确认它解决的是稳定能力包，而不是 AI Native 流程里的一个阶段名；输入、输出、owner、停止条件和验证证据必须能单独成立。
- **向上合并复用**：相同职责仍能被产品专家、架构师、代码生成器或现有 reference 承载时，不新建 Skill，只补 reference、fixture 或脚本。
- **Harness 校验**：拆分后必须缩小上下文、工具和权限选择空间，并能落到状态文件、验证命令、独立 Checker 或交接物；如果只是多一个提示词入口，就不拆。
- **运行一段再抽离**：质量 / 测试门禁、Spec 治理、知识生产、产品评审、编码评审等先作为 AI Native 编排位或专家 reference 运行；只有反复独立触发、现有 owner 明显过载、验证脚本清楚时，才升为顶层 Skill。

不建议拆分的情况：

- 只是 AI Native 流程中的一个门禁位，例如质量 / 测试门禁、理解门禁、授权门禁。
- 只是产品专家或架构师已有能力的细化，例如验收种子、TDD、Runbook、发布检查。
- 只是外部文章中的工具名、hooks、marketplace 或组织实践，当前仓库没有对应运行时能力。

## 3. 产品侧细化

产品专家被 AI Native 调用时，应优先补三类能力：

- **产品验证种子**：正常、边界、异常、运营、数据、风险和人工兜底的可观察样例。
- **业务事实锚点**：目标、非目标、业务 owner、核心对象、不变量、状态流转、规则版本、数据口径和验收方。
- **工程交接边界**：哪些是已确认事实，哪些是 MVP / 原型观察，哪些是假设或待确认，哪些明确不进入本轮。

产品专家不负责把验收种子实现成测试，也不负责判断 GSD/CAD 准入；它只把产品事实交给 AI Native 编排和架构师承接。

产品侧交接物统一收敛为 Product Context Card / 产品上下文交接卡：业务目标、非目标、owner、事实证据、核心对象、状态、不变量、流程规则、验收种子、风险、待确认和专业确认方。产品专家不生成 Engineering Handoff Card、Production Loop Card、Plan Grant、Execution Grant 或 CAD Grant。

## 4. 架构侧细化

架构师被 AI Native 调用时，应优先补四类能力：

- **代码质量与 Review**：源码锚点、架构坏味、契约破坏、测试缺口、安全和生产风险。
- **Runbook 与生产诊断**：症状、影响、定位、止血、恢复、回滚、验收和复盘。
- **CI/CD 与发布门禁**：构建、测试、灰度、监控、告警阈值、回滚和风险接受。
- **基础设施操作**：dry-run、备份、分批、审计、最小权限、显式确认和不可逆操作停止条件。

架构师不负责补产品语义，也不把 AI Native 的流程判断写成 Execution Grant；写入、Git、联网、生产和不可逆操作仍按仓库授权边界执行。

架构侧消费 Engineering Handoff Card 和必要时的 Production Loop Card：先检查 Goal、Spec/AC、Wave/Task、写入范围、验证命令、停止条件、失败回写、授权策略、状态载体、隔离执行、Maker / Checker、独立验证、预算、人工接管和发布/回滚。可消费后才进入 OpenSpec、Harness、GSD 任务包、CAD 候选、TDD、源码级 CR 或发布风险设计。

## 5. 回流与验证

任何细化都必须落到至少一种可复核载体：

- `SKILL.md` 只放定位、触发、边界和 reference 指针。
- `references/` 放矩阵、清单、模板和方法。
- `scripts/` 放确定性校验、生成和审计。
- `fixtures/` 放正负触发样例。
- `source-map.md` 放公开来源、读取状态和不吸收边界。

CR 时检查：

- 是否仍由 AI Native 做主入口和编排。
- 是否明确产品专家、架构师、代码生成器的 owner 边界。
- 是否有验证证据，而不是只有“流程更完整”的描述。
- 是否避免把 Claude Code / 外部 Skill 的内部机制写成本仓库默认能力。
