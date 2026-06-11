# Agentic Engineering 治理

本文定义 AI 原生工具进入研发编码流程时的治理方式：OpenSpec 定义做什么，Superpowers 定义怎么高质量地做，Harness 定义谁做、按什么顺序做、能改哪里、怎么验证、怎么交接。跨轮或中大型任务再叠加 Goal：定义为什么持续推进、做到什么算完成、状态如何更新、预算 / 时间盒如何约束、何时停止和如何交接。

## 使用时机

- 用户要求设计 AI 编码流程、Agentic Engineering、OpenSpec、Harness、GSD、CAD 或多 Agent 协作。
- 用户要求 GSD + Goal、CAD + Goal、目标驱动推进、持续推进、目标状态、预算 / 时间盒、停止条件或跨轮交接。
- 用户要求设计 Agent Loop、`/goal`、`/loop`、auto mode、后台 Agent、持续编排、多 Agent 监督、自我验证或 Loop 停止条件。
- 用户希望 GSD/CAD 自动推进、默认授权、减少每个任务审批，或希望用 Codex “替我审批”模式承接低风险工具审批。
- 产品上下文包已经形成，需要进入系统设计、任务拆分、Agent 执行或 CAD 候选判断。
- 团队使用 Codex、Claude Code、GitHub Copilot coding agent、Cursor、MCP、自动化线程或其他 AI 原生工具协作。

## 不适用场景

- 需求仍处于问题发现阶段时，不直接进入 Harness 或 CAD。
- 小范围低风险修改不需要完整 GSD；可用目标、写入范围和验证命令轻量执行。
- 不用本文替代 GSD/CAD 编排准入、`资深架构师` 的 `ai-assisted-engineering.md`、`ai-large-project-orchestration.md` 和 `cad-mode.md`。

## 读取后必须产出

- 当前任务属于轻量执行、OpenSpec、Harness/GSD、CAD 候选还是只读评审。
- AI 原生工具职责、权限边界、写入范围、验证方式和停止条件。
- 需要架构师继续生成的 OpenSpec、完整 Harness Plan、验证矩阵或 Execution Grant 缺口。
- 若任务跨轮推进，一份 Goal 组合判断：Goal ID、成功标准、状态、预算 / 时间盒、验证证据、停止条件和 GSD Wave / CAD 候选关联。
- 一份授权策略判断：当前适合只读、默认低风险授权、Wave Grant、CAD Grant、Codex 替我审批通道，还是必须显式确认。
- 一份可执行性判断：当前材料能否让 Agent 开始写、只能只读侦察，还是必须先补规格。
- 一份事实边界判断：已知事实、合理推断、待确认事项和范围外不做；无根据猜测或超出用户目标的实现扩张必须被标记为停止条件。
- 若存在持续编排或后台 Agent，一份 Loop 准入判断：状态载体、反馈源、验证者、预算、最大轮次、无进展检测、停止条件和交接物是否齐备。
- 一份最小 Harness 摘要：Task ID、owner、写入范围、只读范围、依赖顺序、验证命令、停止条件、变更可理解性要求和交接要求。

## 需要继续读取的 reference

- 产品交接和 PRD-Lite 读 `product-to-engineering-lifecycle.md`。
- PRD / 系分合议预审、多视角评审、MAGI 三角色或 IPD 式互审读 `prd-system-design-review.md`。
- GSD/CAD 编排准入、GSD Round 0、Wave/Atomic Task 候选、CAD 候选缺口和 Execution Grant 缺口读 `gsd-cad-admission.md`。
- Goal 组合、GSD + Goal、CAD + Goal、状态机、Ledger、预算 / 时间盒和跨轮交接读 `goal-composition.md`。
- Agent Loop、`/goal`、`/loop`、auto mode、后台 Agent、多 Agent 监督和循环停止条件读 `agent-loop-engineering.md`。
- 验证、CR、发布和复盘读 `verification-review-release.md`。
- Spec / SDD / OpenSpec 模板、AC 编号、Given-When-Then、测试映射、spec-lint、AC 覆盖和漂移检查读 `spec-template-practices.md`。
- AI Coding / SDD / Spec / Harness 最终代码交付闭环、CR 减负、知识回流和指标读 `code-delivery-closed-loop.md`。
- Superpowers skills 下载资源、外部 skill 调度矩阵、MIT 许可和安全边界读 `superpowers-skill-library.md`。
- 详细工程规则回到 `senior-software-architect/references/ai-assisted-engineering.md`、`ai-large-project-orchestration.md` 和 `cad-mode.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断需要哪种 AI 编码流程 | `1. 分级模型`、`2. OpenSpec / Superpowers / Harness` | 不展开工具清单 |
| 调度 Superpowers skills | `2. OpenSpec / Superpowers / Harness`，再读 `superpowers-skill-library.md` | 不直接安装插件或执行外部脚本 |
| 落地 Spec 模板 | 先读 `spec-template-practices.md`，再读 `3. Harness 最小契约` | 不复制外部 ASD/SSD Harness |
| 做 GSD + Goal / Goal 组合 | 先读 `goal-composition.md`，再读 `3. Harness 最小契约`、`5. Wave 和交接` | 不把 Goal 写成 Execution Grant |
| 设计 Agent Loop / `/goal` / `/loop` | 先读 `agent-loop-engineering.md`，再读 `3. Harness 最小契约`、`6. 权限边界` | 不把 Loop 当自动授权 |
| 设计默认授权 / 自动推进 | 先读 `gsd-cad-admission.md`，再读 `3. Harness 最小契约`、`6. 权限边界` | 不把所有审批自动通过 |
| 多 Agent / GSD 编排 | 先读 `gsd-cad-admission.md`，再读 `3. Harness 最小契约`、`5. Wave 和交接` | 不直接开 CAD |
| PRD / 系分合议预审 | 先读 `prd-system-design-review.md`，再读 `2. OpenSpec / Superpowers / Harness`、`3. Harness 最小契约` | 不把预审结论写成 Execution Grant |
| CAD 候选判断 | 先读 `gsd-cad-admission.md`，再读 `4. CAD 只处理原子任务`、`6. 权限边界` | 不把整个项目授权给 CAD |
| AI 原生工具接入 | `6. 权限边界`、`7. 工具角色` | 不把工具能力当组织授权 |
| AI 代码库理解与影响结论包 | `3. Harness 最小契约`、`5. Wave 和交接`、`7. 工具角色` | 不把 AI 总结、可视化或上下文生成当测试或 CR 结论 |
| AI 代码交付闭环 | 先读 `3. Harness 最小契约`，再读 `code-delivery-closed-loop.md` | 不只优化编码速度或加厚 Spec |
| 流程治理评审 | `8. 治理清单`、`9. 反模式` | 不只看效率指标 |

## 1. 分级模型

按风险和复杂度选择流程：

| 级别 | 适用场景 | 最小门禁 |
| --- | --- | --- |
| 轻量执行 | 单文件、低风险、可快速验证。 | 目标、写入范围、验证命令。 |
| OpenSpec | 涉及契约、状态、权限、数据或多模块。 | 目标、范围、非目标、规则、验收、技术约束。 |
| Harness / GSD | 长任务、多 Agent、跨模块或上下文衰减。 | Task ID、owner、写入范围、依赖顺序、验证矩阵、交接。 |
| CAD 候选 | 单个边界清楚、验证明确的原子任务。 | OpenSpec + Harness + Execution Grant + 停止条件。 |
| 人工主导 | 资金、合规、安全、生产数据、不可逆操作、高不确定架构。 | 人工确认、专业审批、dry-run、回滚和审计。 |

## 2. OpenSpec / Superpowers / Harness

三层责任不可互相替代：

| 层级 | 回答 | 典型产物 |
| --- | --- | --- |
| OpenSpec | 要做什么，做到什么程度。 | 目标、范围、非目标、业务规则、接口契约、数据约束、验收。 |
| Superpowers | 怎么高质量地做。 | TDD、Review、Refactor、最小变更、编码红线、测试门禁。 |
| Harness | 谁做、按什么顺序做、能改哪里、怎么验证、怎么交接。 | Task ID、owner、写入范围、只读范围、依赖、验证命令、停止条件、交接。 |

Goal 是跨层目标契约，不替代三层责任：它把目标、成功标准、状态、预算 / 时间盒、验证证据和交接节奏挂到 GSD Wave、CAD 候选、Spec、CR 和发布复盘上。

Loop 是运行循环契约，不替代三层责任和 Goal：它只回答每一轮如何读取状态、选择动作、吸收反馈、验证结果、判断继续或停止。Loop 必须依附 Goal、Harness 和授权策略；没有反馈源、验证者、预算 / 最大轮次、无进展检测和停止条件时，不应进入自动循环。

`obra/superpowers` 已作为外部 skill library 下载并隔离到 `external-superpowers/`，调度入口读 `superpowers-skill-library.md`。调度时只吸收它的工程纪律：brainstorming 用于前置澄清，writing-plans 用于计划拆解，test-driven-development 用于红绿重构纪律，subagent-driven-development / executing-plans 用于受控任务执行参考，requesting-code-review / receiving-code-review 用于 CR 反馈闭环，verification-before-completion 用于完成前证据门禁。外部 skill 的默认目录、插件安装、hooks、worktree、自动提交、Git 推送和 subagent 连续执行要求不能覆盖本仓库权限边界。

## 3. Harness 最小契约

任何进入 AI 编码实现的任务，至少写清：

```text
Task ID:
Goal ID:
Goal 状态:
Goal 成功标准:
目标:
Owner:
来源上下文:
写入范围:
只读范围:
依赖顺序:
禁止事项:
验收场景:
AC 编号与测试映射:
spec-lint / AC 覆盖 / 漂移检查:
验证命令:
停止条件:
Goal Ledger 更新:
事实 / 推断 / 待确认 / 范围外不做:
授权策略: 只读 / 默认低风险授权 / Wave Grant / CAD Grant / 显式确认
Loop: 不适用 / 只读 Loop / Plan Grant Loop / Wave Loop / CAD Loop
Loop 反馈源:
Loop 验证者:
Loop 预算 / 最大轮次 / 无进展检测:
Codex 替我审批: 未启用 / 已启用但仅低风险 / 不适用
变更可理解性:
代码库理解结论包:
独立验证证据:
知识回流位置:
交付指标:
交接要求:
恢复入口:
CAD 候选:
Execution Grant / 显式确认缺口:
```

如果写入范围只能写“整个项目”，或者验证命令为空，不应进入 Agent 执行。

易用性要求：

- 小任务只输出 Harness 摘要，不展开完整 GSD 模板。
- 中大型任务先给 Wave 顺序和每个 Wave 的 owner/写入范围，再展开单个任务。
- 使用 Goal 组合时，Harness 摘要必须写清 Goal ID、Goal 状态、成功标准、预算 / 时间盒、停止条件和 Ledger 更新；Goal 不能扩大写入范围。
- CAD 候选只写“候选”和“缺口”，不把候选描述成执行授权。
- GSD/CAD 授权必须按风险分级：已授权范围内的低风险动作可以默认推进，Git、联网、依赖安装、生产、密钥、部署、不可逆操作和高风险业务必须显式确认。
- Codex “替我审批”只能记录为当前会话已启用的低风险审批通道，不得写成 Skill 自行开启的权限，也不得替代 Execution Grant、项目规则或工具 sandbox。
- 输出中必须把“能读什么”“能改什么”“不能碰什么”分开写，避免权限边界混在目标描述里。
- 对陌生代码库侦察、多文件 AI 变更或重构计划，Harness 摘要必须要求交接时说明业务意图、入口路径、影响模块、关键调用关系、边界变化、源码锚点、验证证据和残余不确定性。
- 对陌生代码库、多模块 Agent 平台或 AI 生成多文件变更，Harness 摘要应要求先形成图形化理解包：组件/入口、启动顺序、认证权限、外部系统、数据/消息/状态流、源码锚点、未确认连接和进入实现/CR 的结论；图只能降低认知负荷，不能替代源码、测试、Review 或架构师判断。
- 对 AI 代码交付闭环，Harness 摘要必须说明 Spec 强度、独立验证证据、CR 高频问题是否机器化、知识回流位置和交付指标；如果只能证明“代码已生成”，不能进入合并或发布判断。
- 对 Spec 模板落地，Harness 摘要必须说明模板强度、AC 编号规则、Given-When-Then 映射、测试证据、spec-lint、AC 覆盖、漂移检查和风险自查；如果只能证明“文档已生成”，不能进入实现判断。
- 对任何 AI Native 编排，Harness 摘要必须说明哪些来自用户目标或源材料、哪些只是模型推断、哪些需要确认、哪些超出目标不做；不能把无根据猜测、外部文章观点、工具总结或模型脑补写成任务、实现或授权。
- 对任何 Agent Loop、`/goal`、`/loop`、auto mode 或后台 Agent，Harness 摘要必须说明状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件和交接物；不能只写“循环直到完成”。

## 4. CAD 只处理原子任务

CAD 不是“整个大项目自动驾驶”，只适合已具备以下条件的原子任务：

- 产品上下文和 OpenSpec 清楚。
- 写入文件范围明确且可独立 Review。
- 依赖顺序清楚，不会和其他任务互相踩踏。
- 有可运行测试、编译、lint、静态检查或人工验收方式。
- 停止条件明确：测试失败、契约不清、权限不足、风险升级、用户中断。
- 用户已明确授权当前任务的执行范围；授权不自动外推到提交、联网、部署或生产操作。
- 当前任务若属于已批准的 Wave Grant 或 CAD Grant，且只触发低风险、本地、可验证、可回滚动作，可以按默认授权推进；命中显式确认边界时停止。

## 5. Wave 和交接

中大型任务按 Wave 组织：

```text
Wave 0：只读侦察、代码库理解结论包、规格补齐、风险确认。
Wave 1：公共契约、领域模型、测试夹具和验证底座。
Wave 2：互不重叠的实现任务。
Wave 3：集成验证、CR、文档、发布准备。
```

交接必须包含：

- 已完成内容和未完成内容。
- 变更文件和关键决策。
- 业务意图、入口路径、影响模块、关键调用关系、边界变化和源码锚点。
- 关联 Goal、Goal 状态、成功标准完成情况和 Ledger 更新。
- 验证命令、结果和失败证据。
- 残余风险、阻塞项和下一步。
- 回滚或恢复入口。

## 6. 权限边界

AI 原生工具常见权限必须显式授权：

| 权限 | 默认状态 | 需要说明 |
| --- | --- | --- |
| 读仓库文件 | 可在工作区内按任务读取。 | 不读取无关私有目录。 |
| 写仓库文件 | 需任务范围明确。 | 写入目录、文件类型、是否可覆盖。 |
| 运行测试/构建 | 可按项目命令执行。 | 失败原因、残余风险和环境影响。 |
| 联网查询 | 需任务需要且遵守来源约规。 | 来源、时效性、版权和隐私。 |
| Git stage/commit | 需用户明确要求。 | 只 stage 当前任务文件。 |
| Push/PR/部署 | 需明确授权。 | 目标分支、环境、回滚和审批。 |
| 生产数据/配置 | 默认禁止。 | dry-run、备份、审批、审计和回滚。 |

默认授权边界：

- `只读侦察` 可默认读取工作区内相关文件、查引用、运行只读检查。
- `默认低风险授权` 可在用户已要求推进且范围明确时编辑声明范围内文件、运行本地测试/校验、记录结果。
- `Wave Grant` 可覆盖同一 Wave 内互不冲突的低风险 Atomic Task，但不能跨 Wave、改公共契约或触发 Git/联网。
- `CAD Grant` 只覆盖一个原子任务的 Red/Green/Review/Verify 本地动作。
- `显式确认` 覆盖 Git stage/commit/push/PR/merge、联网、依赖安装、读取密钥、生产数据、部署、数据库迁移、真实支付/资金、不可逆操作、高风险权限/租户/审计/合规变更。

## 7. 工具角色

| 工具/Agent 类型 | 适合做 | 不适合做 |
| --- | --- | --- |
| 产品 Agent | 反馈整理、问题地图、原型、PRD-Lite、验收种子。 | 最终业务决策和合规结论。 |
| 架构 Agent | OpenSpec、Harness、任务拆分、边界和验证矩阵。 | 无产品上下文时直接编码。 |
| 编码 Agent | 原子任务实现、测试补齐、局部重构。 | 修改公共契约或生产行为而无人审。 |
| Review Agent | 初筛越界、测试缺口、坏味、结构影响和风险。 | 替代人工 CR 和责任签字。 |
| 预审 Agent | 对 PRD、OpenSpec 输入、系分或 Harness 候选做多视角预审，输出锚点化反馈和 `ACCEPT/REJECT/PENDING` 决策日志。 | 替代产品 owner、架构 owner、正式评审会或 Execution Grant。 |
| 代码库理解辅助 | 只读快速阅读代码、生成入口路径、模块图、调用导览、上下文文件、源码锚点、影响说明和图形化理解 brief。 | 替代源码阅读、测试、人工判断或默认安装外部工具。 |
| Delivery Gate Agent | 汇总独立验证、CR 减负、发布观测、知识回流和指标证据。 | 替代架构师源码级 CR、测试实现、上线审批或生产责任。 |
| Loop Orchestrator | 在已授权范围内读取状态、派发动作、收集反馈、判断继续或停止。 | 自行扩大写入范围、跳过验证、无限循环或替代授权。 |
| Eval Agent | 构造样例、失败案例、回归矩阵。 | 把 eval 通过当作上线批准。 |
| 自动化/线程 | 周期检查、状态恢复、反馈循环。 | 未授权持续写入或发送外部消息。 |

## 8. 治理清单

- 是否从产品上下文包进入工程，而不是从一句 prompt 进入编码。
- PRD / 系分是否已在需要时做合议预审，并形成锚点化问题、接受项、拒绝项、待定项、分歧、风险清单、owner 和验证方式。
- 是否有 OpenSpec 固定范围、非目标、规则和验收。
- 中大型或跨轮任务是否有 Goal 卡固定目标、成功标准、预算 / 时间盒、状态、停止条件和验证证据。
- 是否有可评审 Spec 模板，覆盖五段式骨架、AC 与测试映射、风险自查和闸门证据。
- 是否有 Harness 固定 owner、写入范围、顺序、验证和交接。
- 是否有授权策略，能区分只读、默认低风险授权、Wave Grant、CAD Grant、Codex 替我审批和显式确认边界。
- 是否有 Loop 准入，能区分状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件和交接物。
- 是否有事实边界门禁，能区分事实、推断、待确认和范围外不做，避免 AI 幻觉进入任务包或实现建议。
- 是否有代码库理解与变更可理解性门禁，能让人复述业务意图、入口路径、影响模块、调用关系、边界变化、源码锚点和残余风险。
- 对陌生代码库或多模块变更，是否有图形化理解 brief，能让人看到组件/入口、启动顺序、认证权限、外部系统、数据/消息/状态流、源码锚点和未确认连接。
- 是否区分轻量任务、GSD Wave 和 CAD 候选。
- 是否有测试、lint、CR、监控或人工验收闭环。
- 是否有 AI 代码交付闭环，覆盖最小 Spec 强度、Harness 独立验证、CR 减负、知识回流和一次通过率 / 返工率 / 缺陷密度等指标。
- 是否记录工具权限、外部来源和专业确认边界。
- 是否避免多个 Agent 同时写同一职责范围。
- 是否把失败、阻塞和恢复入口写入显式材料。
- 是否避免把 Goal、Goal 状态或 GSD + Goal 当作 Execution Grant、测试通过、CR 结论或上线批准。
- 是否避免把 Loop、`/goal`、`/loop` 或 auto mode 当作无条件执行授权。

完整性自检：

- **能不能做**：目标、非目标、输入证据和验收是否足够。
- **是否有根据**：事实、推断、待确认和范围外不做是否分开；无来源、无源码锚点、无验收种子或无验证证据的内容是否被阻断。
- **谁来做**：人类 owner、Agent 角色和交接责任是否明确。
- **能改哪里**：写入范围、只读范围、禁止事项是否明确。
- **能否自动推进**：默认授权范围、Codex 替我审批适用条件、显式确认边界和停止条件是否明确。
- **怎么验证**：测试、lint、静态检查、人工验收和不可执行原因是否明确。
- **是否看懂**：入口路径、影响模块、调用关系、边界变化、源码锚点、验证证据和剩余不确定性是否能被 Review 者复述。
- **何时停止**：权限不足、规格不清、验证失败、风险升级和用户中断是否明确。
- **目标是否闭环**：Goal 成功标准、验证证据、Ledger 更新和交接 owner 是否明确。

## 9. 反模式

- 让 Agent 先写代码，再补需求和测试。
- 用“模型更强了”替代 OpenSpec、Harness 和 Review。
- 多个 Agent 共用同一模糊上下文，互相迎合或覆盖。
- 把无根据猜测、模型脑补、工具总结、外部文章观点或超出用户目标的功能扩张写成结论、任务、实现或授权。
- 把 Loop 当成更长的 Prompt、cron 或无限自动执行，缺少反馈、验证、预算和停止条件。
- 把“自动推进”“默认授权”或 Codex “替我审批”写成无条件放行，绕过 Git、联网、依赖安装、生产、密钥、部署、不可逆操作和高风险业务门禁。
- 把工具的 PR 工作流当成完整质量保证。
- 用大段 AI 总结替代结构理解，Review 者无法定位入口路径、关键源码、调用关系和边界变化。
- 把 AI 快速阅读、上下文生成或可视化工具输出当成默认事实，不回链源码、OpenSpec、Harness 和验证证据。
- 自动提交、自动合并、自动部署默认开启。
- Goal 只有口号和状态，没有成功标准、验证证据、预算 / 时间盒、停止条件和 Ledger。
- 指标只看代码量、PR 数、执行轮数，不看返工率、缺陷率、验证质量和上线结果。
- 只做 SDD / Spec / Harness 的前半程，不把 CR 高频问题、测试失败、发布问题和复盘发现回流到知识、模板、测试、fixture、脚本或门禁。
