# 角色协作 Loop：意图到生产交付

本文定义 AI Native 的核心主流程：从业务意图、需求收集、产品 / 交互设计、设计评审、TDD / 测试设计、真实编码、编码评审、可用性 / 安全性 / 可靠性评估、验证发布到反馈回流的端到端角色协作 Loop。它用于 AI Native 编排，不替代产品专家 PRD、架构师系分、源码级 CR、测试实现、发布审批或生产 owner 决策。

GSD、CAD、Goal、Harness、Grant、Agent Loop 都是本流程的内部处理层或边缘流程：Goal 定义完成线，GSD 拆分 Wave，CAD 执行原子任务，Harness 固定执行契约，Grant 管授权边界。对外默认先问“当前处于哪个角色协作阶段”，再决定是否需要这些内部层。

## 使用时机

- 用户要求把 AI 工作流从意图 / 需求收集推进到生产交付闭环。
- 用户要求区分产品专家、UED、架构师、AI Agent、测试 / 质量门禁、发布 owner 等角色分工。
- 用户要求按设计、设计评审、TDD、编码、编码评审、可用性 / 安全性 / 可靠性评估分别切换视角。
- 用户希望 AI 工作流达到团队协作、协同检查、Maker / Checker 分离和多角色互相制衡的效果。
- 用户说“进入 GSD 产研协同研发流程”“从需求到上线闭环”“Loop 从意图到交付”“多个角色每个阶段怎么分工”。
- 现有流程只强调 AI 自动执行、GSD/CAD/Goal/Loop 机制，但缺少每一阶段 owner、交接物、门禁和停止条件。

## 不适用场景

- 只写普通 PRD、产品方案、Backlog 决策或原型说明时，回到 `product-architecture-expert`。
- 只做系统设计、编码、测试、代码 Review、Bug 修复或生产变更时，回到 `senior-software-architect`。
- 只评估 Loop 运行机制、状态、Maker / Checker、自动化心跳、Worktree、连接器或理解债时，读 `agent-loop-engineering.md`。

## 读取后必须产出

- Role Collaboration Loop Map / Intent-to-Production Role Loop Map：阶段、主责 owner、协作角色、AI Maker、AI Checker、能力 / 约规来源、输入、交接物、验证门禁和停止条件。
- 角色分工结论：只写当前任务涉及角色的主责、不替代项和下一步；通用职责以 `2. 角色边界` 为唯一权威来源。
- 交接链路：产品上下文卡、工程执行交接卡、生产 Loop 交接卡、验证证据、发布 / 回滚证据和反馈回流位置。
- 若信息不足，输出缺口 owner 和停止条件，不把模糊意图改写成可执行任务。

## 需要继续读取的 reference

- 产品上下文、需求分析、PRD-Lite、产品 / 系统 DNA 和三卡交接读 `product-to-engineering-lifecycle.md`。
- 产品 / 交互设计、PRD、验收种子和产品合议由 `产品架构专家` 执行；按场景读取 `product-architecture-expert/references/product-scenario-routing.md`、`product-architecture-expert/references/product-design-and-prd.md`、`product-architecture-expert/references/product-prd-quality-gates.md`、`product-architecture-expert/references/product-deliberation-workflow.md` 或 `product-architecture-expert/references/ai-native-product-context.md`。
- 系分、TDD、编码、CR、安全可靠和发布风险由 `资深架构师` 执行；按场景读取 `senior-software-architect/references/system-analysis-design.md`、`senior-software-architect/references/testing.md`、`senior-software-architect/references/workflow.md`、`senior-software-architect/references/coding-standards.md`、`senior-software-architect/references/coding-review-deep-dive.md`、`senior-software-architect/references/security-architecture.md` 或 `senior-software-architect/references/production-readiness.md`。
- PRD / 系分合议预审、多角色挑战、ACCEPT/REJECT/PENDING 决策日志读 `prd-system-design-review.md`。
- OpenSpec、Harness、权限边界、事实边界和多 Agent 治理读 `agentic-engineering-governance.md`。
- 实际编码 Loop、状态载体、Maker / Checker、自动化心跳、Worktrees、理解债和停止条件读 `agent-loop-engineering.md`。
- 测试矩阵、质量门禁、CR、发布、监控、回滚和复盘读 `verification-review-release.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 从意图到生产交付流程 | `1. 端到端阶段`、`2. 角色边界`、`3. 阶段交接门禁` | 不展开完整 PRD 或系分模板 |
| 梳理多角色分工 | `2. 角色边界`、`4. 分工输出模板` | 不把 AI 角色写成 owner |
| 进入角色协作 Loop | `1. 端到端阶段`、`1.1 阶段能力与约规来源`、`1.2 角色视角顺序`、`3. 阶段交接门禁` | 不把 GSD/CAD/Goal 当主流程 |
| 评审现有 Loop 是否闭环 | `1. 端到端阶段`、`5. 反模式` | 不只看自动化能否运行 |

## 1. 端到端阶段

```text
意图 / 反馈 / 业务目标
-> 需求收集与事实分层
-> 产品 / 交互设计与验收种子
-> 设计评审 / PRD-系分合议预审
-> TDD / 测试设计
-> 编码实现 / AI Maker 执行
-> 编码评审 / AI Checker / 架构师 CR
-> 可用性 / 安全性 / 可靠性评估
-> 验证发布 / 监控 / 回滚准备
-> 生产反馈 / 复盘 / 知识回流
```

每一阶段只推进一个判断：当前材料是否足以进入下一环。Loop 的价值不是多跑 Agent，而是让意图、上下文、行动、验证和交接持续闭合。

| 阶段 | 主责 owner | AI 角色 | 交接物 | 门禁 / 停止 |
| --- | --- | --- | --- | --- |
| 意图收集 | 业务 owner / 产品专家 | 整理事实、问题和不确定性 | 原始意图、证据、影响面、成功/失败信号 | 缺少主体、场景、证据或验收方时停止 |
| 产品 / 交互设计 | 产品专家 / UED | 辅助梳理流程、用例、交互状态和验收种子 | 产品上下文卡、流程 / 用例 / 页面状态、验收种子 | 产品只传话、未解释业务问题或影响面时停止 |
| 设计评审 | AI Native 编排，产品 / 架构 owner 决策 | Design Reviewer / MAGI / Checker 提出挑战与风险 | ACCEPT/REJECT/PENDING、风险清单、owner | AI 预审不能替代 owner 决策 |
| TDD / 测试设计 | 资深架构师 / 质量门禁 | 辅助把验收种子转成失败测试候选和验证矩阵 | 测试策略、失败测试候选、验证命令 | 缺业务规则、不变量或验收样例时停止 |
| 编码实现 | 资深架构师 / 工程 owner | AI Maker 在授权范围内实现，按 TDD 推进 | 失败测试、实现、提交切片、状态回写 | 不允许模拟模块、内存版业务 Service 或无业务入口 demo |
| 编码评审 | AI Checker + 架构师 | 对照 Spec、测试和源码锚点找问题 | CR 发现、测试结果、残余风险 | 写代码的 Agent 不能自证通过 |
| 可用性 / 安全性 / 可靠性评估 | UED / 架构师 / 安全或发布 owner | 辅助检查交互恢复、权限、敏感数据、监控和回滚 | 可用性风险、安全风险、可靠性风险、人工确认方 | 高风险项无 owner 或证据时停止 |
| 验证发布 | 发布 owner / 架构师 / 运维 owner | 汇总证据、监控、回滚和交接 | 发布计划、监控指标、回滚方案、Runbook | 没有观测、回滚、人工接管或审批时停止 |
| 反馈回流 | AI Native + 对应 owner | 整理复盘、知识归位和 fixture 缺口 | Decision Log、Goal Ledger、Skill / fixture / 脚本更新建议 | 不把未经验证经验沉淀为规则 |

### 1.1 阶段能力与约规来源

阶段名只是编排坐标，不是能力来源。每个阶段必须回指专项 Skill、reference 或脚本；缺少能力来源时，只能输出分派建议和补齐清单，不允许 AI Native 自行补写 PRD、测试策略、代码实现或发布结论。

| 阶段 | 能力 / 约规来源 | 触发的专项约规 | 不允许 |
| --- | --- | --- | --- |
| 意图收集 / 产品设计 | `产品架构专家` | `product-scenario-routing.md`、`product-architecture-methodology.md`、`product-design-and-prd.md`、`product-prd-quality-gates.md`、`ai-native-product-context.md` | AI Native 不自行编 PRD、验收种子或交互结论。 |
| 设计评审 / PRD-系分合议预审 | AI Native 编排 + `产品架构专家` + `资深架构师` | `prd-system-design-review.md`、`product-deliberation-workflow.md`、`product-prd-quality-gates.md`、`senior-software-architect/references/system-analysis-design.md`、`senior-software-architect/references/review-and-output-templates.md` | 预审不替代产品 owner、架构 owner 或正式评审决策。 |
| TDD / 测试设计 | `资深架构师` | `senior-software-architect/references/testing.md`、`senior-software-architect/references/testing-practices.md`、`senior-software-architect/references/workflow.md` | AI Native 不直接自由发挥测试策略、测试代码或通过结论。 |
| 编码实现 / AI Maker 执行 | `资深架构师`；结构化 Java Service 可转 `java-service-code-generator` | `senior-software-architect/references/workflow.md`、`senior-software-architect/references/coding-standards.md`、`senior-software-architect/references/ai-assisted-engineering.md`、`senior-software-architect/references/cad-mode.md`、`java-service-code-generator/references/code-generation-rules.md` | 不越过 Grant，不生成模拟模块、内存版业务 Service 或无业务入口 demo。 |
| 编码评审 / AI Checker | `资深架构师` | `senior-software-architect/references/coding-review-deep-dive.md`、`senior-software-architect/references/clean-code.md`、`senior-software-architect/references/negative-constraints.md`、`senior-software-architect/references/coding-standards.md` | Maker 不自审，不把 AI 总结当 CR 证据。 |
| 可用性 / 安全性 / 可靠性评估 | UED / `产品架构专家` + `资深架构师` + 安全或发布 owner | `product-design-and-prd.md`、`product-prd-quality-gates.md`、`senior-software-architect/references/security-architecture.md`、`senior-software-architect/references/production-readiness.md` | 不用流程编排替代 UED、安全、合规、SRE 或发布 owner 确认。 |
| 验证发布 | `资深架构师` / 发布 owner | `verification-review-release.md`、`senior-software-architect/references/testing.md`、`senior-software-architect/references/production-readiness.md`、`senior-software-architect/references/review-and-output-templates.md` | 测试通过不等于上线审批，发布证据不足时停止。 |
| 反馈回流 | AI Native + 对应 owner | `skill-type-owner-routing.md`、`source-map.md`、仓库 `AGENTS.md` | 未验证经验不进入正式约规或长期学习记录。 |

### 1.2 角色视角顺序

角色协作 Loop 默认按下列视角切换。当前任务不涉及的视角可以跳过，但不能把 Maker 和 Checker 合并成自证。

| 视角 | 主要问题 | 输出 |
| --- | --- | --- |
| Design Owner | 要解决什么问题，用户 / 主体 / 对象 / 状态 / 规则 / 验收是什么？ | 产品设计、交互状态、系分或设计输入。 |
| Design Reviewer | 方案是否完整、可测试、可开发、可运营、可发布，是否存在过度设计或证据缺口？ | 设计评审结论、ACCEPT/REJECT/PENDING。 |
| TDD / Test Designer | 先用什么失败测试、验证矩阵或验收样例证明要做对？ | 测试策略、失败测试候选、验证命令。 |
| Implementation Maker | 在授权范围内如何最小实现？ | 代码变更、状态回写、提交切片候选。 |
| Code Reviewer | 实现是否对齐 Spec、源码锚点、契约、测试和项目约规？ | CR 发现、风险等级、修复建议。 |
| Usability / Safety / Security Reviewer | 用户路径、错误恢复、权限、敏感数据、审计、监控、回滚是否可信？ | 可用性 / 安全性 / 可靠性风险和人工确认方。 |
| Release / Quality Gate | 当前证据是否足以发布、回滚、观测和复盘？ | 发布门禁、残余风险、知识回流位置。 |

## 2. 角色边界

- **AI Native 编排者**：决定当前阶段、owner、交接物、验证门禁和停止条件；不替代 PRD、系分、代码、测试、CR 或发布审批。
- **产品专家**：理解业务、识别真正问题、提供解决方案、定义对象 / 规则 / 边界 / 验收种子；不是被动传话筒。
- **UED / 交互设计**：属于产品岗，负责用户路径、信息架构、交互状态、错误恢复和可用性证据；不替代产品决策或工程设计。
- **资深架构师**：把已确认产品事实转为系统边界、模块、接口、数据、测试、TDD、CR、发布风险和生产兜底。
- **AI Maker**：在 Grant 范围内执行只读分析、测试、实现、文档或脚本任务；不自行扩大目标、写生产审批或修改高风险边界。
- **AI Checker**：独立检查 Spec 对齐、测试证据、源码锚点、回归风险、理解债和残余不确定性；不与 Maker 合并为同一自证角色。
- **Design Reviewer**：只做设计挑战和准出判断，不直接代写最终 PRD 或系分，不把 AI 共识当 owner 决策。
- **Code Reviewer**：只做实现挑战和风险判断，不替代测试通过、发布审批或生产 owner。
- **Usability / Safety / Security Reviewer**：从用户路径、错误恢复、权限、敏感数据、审计、监控、回滚和人工接管检查风险；不替代 UED、法务、合规、安全或 SRE 正式确认。
- **质量 / 测试门禁**：编排测试矩阵、验证顺序、CR 前置条件、失败回退和证据交接；测试设计与实现继续调用资深架构师的测试能力。
- **发布 owner**：决定发布、灰度、监控、回滚、人工接管和生产交接；AI 只能整理证据和缺口。

## 3. 阶段交接门禁

每一环交接前都用同一张轻量卡：

```text
当前阶段:
主责 owner:
协作角色:
AI Maker:
AI Checker:
角色视角:
能力 / 约规来源:
已读取 / 需读取 reference 或 script:
输入事实:
合理推断:
待确认:
本阶段交接物:
进入下一阶段的证据:
停止条件:
下一 owner:
```

进入真实编码前必须额外具备：真实业务入口、写入范围、只读范围、失败测试或验收样例、验证命令、独立 Checker、状态回写位置、提交切片、回滚方式和停止条件。

## 4. 分工输出模板

```text
Role Collaboration Loop Map / Intent-to-Production Role Loop Map

结论:
当前阶段:
角色 Loop 场景视图:
阶段链路:
角色视角:
能力 / 约规来源:
角色边界:
交接物:
验证门禁:
停止条件:
各角色下一步:
AI Maker / Checker 使用边界:
证据边界:
```

## 5. 反模式

- 只把 Loop 设计成定时器、自动脚本或 Prompt 循环，却没有 owner、交接物、验证者和停止条件。
- 产品岗只转述需求，不解释业务问题、影响面、解决方案和验收种子。
- UED 被误放到工程或视觉附属角色，导致交互状态、错误恢复和用户路径缺口没有产品 owner。
- 架构师在产品事实未确认时用技术方案补猜；或产品专家在系统风险未评估时承诺交付。
- Maker 和 Checker 不分离，AI 自己写、自己审、自己宣布完成。
- 把阶段名当能力来源，只写“产品 / 架构 / TDD / 编码”而不回到产品专家、架构师或代码生成器的专项约规。
- 用 GSD/CAD/Goal 等机制名替代角色协作，导致设计、评审、TDD、编码、CR、安全 / 可用性评估和发布门禁混在一个 Agent 输出里。
- Loop 自动产出很多 PR，但团队无法复述目标、关键变更、证据、风险和回滚方式。
- 过程文档、讨论草稿、AI 推理轨迹混入正式 PRD、系分或 OpenSpec，导致交付契约不清。
