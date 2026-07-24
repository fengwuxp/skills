# 交付生命周期

本文只定义知止者的 SDLC 阶段导航：从业务意图、需求收集、产品 / 交互设计、设计评审、TDD / 测试设计、真实编码、编码评审、可用性 / 安全性 / 可靠性评估、验证发布到运行支持、维护退役和反馈回流。能力 owner 以 `capability-routing.md` 为准，跨轮状态以 `delivery-execution-control.md` 为准，验证准出以 `verification-review-release.md` 为准；本文不重复三者，也不替代专业交付与人类责任。

目标、计划、原子执行、执行契约和授权边界都是本流程的内部层。对外默认只问“当前处于哪个生命周期阶段”，再按上下文归位内部实现，不把 Loop、SDLC、Agentic DevOps、GSD、CAD 或 Harness 展示成用户需要选择的并列流程。

## 使用时机

- 用户要求把 AI 工作流从意图 / 需求收集推进到生产交付闭环。
- 用户要求区分产品专家、UED、架构师、AI Agent、测试 / 质量门禁、发布 owner 等角色分工。
- 用户要求 AI 工作流控制不同 Skill 完成任务，例如产品专家做需求和验收、架构师做系分和编码、Java 代码生成器做基础服务和模型、Wind 约规配合 CR、代码阅读工具和画图工具辅助理解。
- 用户要求输出分角色 Loop、Skill、工具、框架的协作判断矩阵。
- 用户要求参考 Andrew Ng / 吴恩达对 Loop Engineering 的理解，区分 AI 编码、开发者方向修正、真实用户 / 市场反馈三种不同时间尺度的 Loop。
- 用户要求把 Superpowers、GSD、GStack、Trellis、SDD / Harness、`grill-me`、Ponytail、Open Code Review、Gemini、WorkBuddy 等外部框架或工具纳入分角色 Loop，并希望 AI 根据上下文选择最合适策略。
- 用户要求按设计、设计评审、TDD、编码、编码评审、可用性 / 安全性 / 可靠性评估分别切换视角。
- 用户提供 `/office-hours`、CEO Review、Eng Review、Design Review、`/review`、`/qa`、`/ship` 等 GStack 角色链，并要求整理成生产交付流程。
- 用户希望 AI 工作流达到团队协作、协同检查、Maker / Checker 分离和多角色互相制衡的效果。
- 用户要求 AI 能自我挖掘需求和代码上下文、确认边界、设计并 CR 需求，再执行 TDD、编码、CR、验证和完成判断。
- 用户说“进入 GSD 产研协同研发流程”“从需求到上线闭环”“Loop 从意图到交付”“多个角色每个阶段怎么分工”。
- 现有流程只强调 AI 自动执行、GSD / 工程执行/Goal/Loop 机制，但缺少每一阶段 owner、交接物、门禁和停止条件。

## 不适用场景

- 只写普通 PRD、产品方案、Backlog 决策或原型说明时，回到 `product-architecture-expert`。
- 只做系统设计、编码、测试、代码 Review、Bug 修复或生产变更时，回到 `senior-software-architect`。
- 只评估 Loop 运行机制、状态、Maker / Checker、自动化心跳、Worktree、连接器或理解债时，读 `delivery-execution-control.md`。

## 读取后必须产出

- Role Collaboration Loop Map / Intent-to-Production Role Loop Map：阶段、主责 owner、协作角色、AI Maker、AI Checker、能力 / 约规来源、输入、交接物、验证门禁和停止条件。
- 自主交付控制卡：可自我挖掘、可自我规划、可自动执行、必须人工确认、置信度、下一步和停止条件。
- 轻量问询结论：复杂 / 模糊任务的关键分叉、建议答案、依据、已自答项、需 owner 判断项和进入下一阶段的输入。
- `grill-me` 盘问结论：Loop 推进中关键分叉、含糊回答或连续返工触发的决策树分支、`question_id`、已问问题、答案状态、推荐答案、已确认选择、被排除方案、待确认项和写回位置。
- GStack 角色链审查结论：forcing questions、范围收敛、工程评审、交互评审、实现、源码 CR、QA、发布准出的 owner、证据和停止条件。
- 小闭环决策澄清门禁结论：每个阶段完成后先自我问询并用证据自答，再给出 自决推进、询问 owner、继续收敛或停止交接，并写清下一阶段输入。
- 阶段责任结论：只写当前任务涉及的人类责任、阶段职责、不替代项和下一步；四类责任与能力 owner 直接引用 `capability-routing.md`，本文不另立权威。
- 阶段能力投影：当前任务处于哪个生命周期节点、`capability-routing.md` 选择了什么主能力和 Checker、交接物是什么、哪些工具 / 框架只补方法缺口。
- 生产生效验证结论：按代码变更、配置 / 开关 / prompt 变更、文档 / Skill-only 变更或高风险变更选择准出证据。
- 三层反馈节奏：当前任务主要处于 Agentic Coding、Developer Feedback 还是 External Feedback；外层慢反馈如何修正 Vision，中层如何修正 Spec，内层如何执行和验证。
- 协同策略选择：当前更适合产品优先、架构优先、代码生成链、只读理解、质量门禁、发布准出还是知识回流；外部框架 / 工具只作为对应节点的策略补强。
- 交接链路：产品上下文卡、工程执行交接卡、生产 Loop 交接卡、验证证据、发布 / 回滚证据和反馈回流位置。
- 若信息不足，输出缺口 owner 和停止条件，不把模糊意图改写成可执行任务。

## 需要继续读取的 reference

- 能力 owner、专业 Skill、Worker / Checker 和最小装载规则统一读取 `capability-routing.md`；本文只消费其结果。
- 产品上下文、需求分析、PRD-Lite、产品 / 系统 DNA 和三卡交接读 `product-to-engineering-lifecycle.md`。
- 产品 / 交互设计、PRD、验收种子和产品合议由 `产品架构专家` 执行；按场景读取 `product-architecture-expert/references/product-scenario-routing.md`、`product-architecture-expert/references/product-design-and-prd.md`、`product-architecture-expert/references/product-prd-quality-gates.md`、`product-architecture-expert/references/product-deliberation-workflow.md` 或 `product-architecture-expert/references/ai-native-product-context.md`。
- 系分、TDD、编码、CR、安全可靠和发布风险由 `资深架构师` 执行；按场景读取 `senior-software-architect/references/system-analysis-design.md`、`senior-software-architect/references/testing.md`、`senior-software-architect/references/workflow.md`、`senior-software-architect/references/coding-review-deep-dive.md`、`senior-software-architect/references/security-architecture.md` 或 `senior-software-architect/references/production-readiness.md`。具体编码先服从项目本地规范；Java 项目读取 `wind-coding-conventions` 的通用层，Wind/Nobe 专项按依赖或上下文启用。
- 结构化 Java Service 基础服务、DTO / Request / Query / Entity / Mapper / Converter / Service / ServiceImpl 骨架生成由 `java-service-code-generator` 执行；生成后回 `wind-coding-conventions` 检查通用 Java 约规并按依赖/上下文叠加 Wind/Nobe 专项，再回 `资深架构师` 做源码级设计 / TDD / CR。
- Java 项目编码指导和规则由 `wind-coding-conventions` 执行；它提供通用 Java 约规，并在命中 Wind/Nobe 信号后提供专项规则和模板样例，架构裁决、测试策略、源码级 Review 和生产风险仍回 `资深架构师`。
- 代码阅读理解、设计-代码对齐和外部理解工具准入读 `code-understanding-tools.md`；工具输出只是只读证据，不替代源码锚点、测试、CR 或 owner 判断。
- 产品图和工程图分别回 `产品架构专家` / `资深架构师` 的 `diagram-output.md`；Archify 或 `$fireworks-tech-graph` 只在语义 brief 已确认、能力已安装可用或获得明确授权后作为可选生成后端。
- 外部框架或工具只按当前角色节点补强：Superpowers / SDD / Harness 补工程纪律和独立验证，GStack 补角色链审查，`grill-me` 补轻量问询，Ponytail 补最小正确实现，Open Code Review 补外部 Checker，Gemini / AgentRC / WorkBuddy 补只读理解或本地执行准入；来源与边界读 `superpowers-skill-library.md`、`code-understanding-tools.md`、`source-map.md`。
- PRD / 系分合议预审、多角色挑战、ACCEPT/REJECT/PENDING 决策日志读 `prd-system-design-review.md`。
- OpenSpec、Harness、权限边界、事实边界和多 Agent 治理读 `engineering-governance.md`。
- 实际编码 Loop、状态载体、Maker / Checker、自动化心跳、Worktrees、理解债和停止条件读 `delivery-execution-control.md`。
- 测试矩阵、质量门禁、CR、发布、监控、回滚和复盘读 `verification-review-release.md`。
- 生产交付审查、生产生效验证、业务场景模拟验收、发布准出、回滚和人工接管标准读 `verification-review-release.md` 的 `7A. 生产交付审查标准`、`7B. 生产生效验证门禁` 和 `7C. 业务场景模拟验收`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 从意图到生产交付流程 | `1. 端到端阶段`、`2. 角色边界`、`3. 阶段交接门禁` | 不展开完整 PRD 或系分模板 |
| 梳理多角色分工 | `2. 角色边界`、`4. 分工输出模板` | 不把 AI 角色写成 owner |
| 控制不同 Skill 完成任务 | 先读 `capability-routing.md`，再读 `1A. 阶段与能力衔接`、`3. 阶段交接门禁` | 不让知止者直接代写专项产物 |
| 判断角色 / Skill / 工具 / 框架协作方式 | 先读 `capability-routing.md`，再读 `1A. 阶段与能力衔接`、`1.1A 外部框架 / 工具协同策略` | 不让工具或框架替代主能力 |
| 选择外部框架或工具策略 | `1.1A 外部框架 / 工具协同策略`、`1.2 角色视角顺序` | 不把工具名变成主流程或默认依赖 |
| 校准三层反馈 Loop | `1.0A 三层反馈节奏`、`1.2 角色视角顺序`，需要经典视角时装载 `huaxia-practical-wisdom` | 不让内层 AI 自测替代产品判断或真实用户反馈 |
| 进入知止者 | `1. 端到端阶段`、`1A. 阶段与能力衔接`、`1.2 角色视角顺序`、`3. 阶段交接门禁`，具体主能力与协同能力回到 `capability-routing.md` 判断 | 不把 GSD / 工程执行/Goal 当主流程 |
| 接入 GStack 角色链模板 | `1.2 角色视角顺序`、`1.2A GStack 角色链映射`、`3. 阶段交接门禁`，再读 `verification-review-release.md` 的 `7A. 生产交付审查标准` | 不把 slash 命令当外部工具或新流程菜单 |
| 做预发 / 生产生效验证 | `1. 端到端阶段`、`3. 阶段交接门禁`，再读 `verification-review-release.md` 的 `7B. 生产生效验证门禁` 和 `7C. 业务场景模拟验收` | 不把“已部署 / 已推配置 / 能打开页面”当环境 OK |
| 让 AI 自主推进到交付 | `1. 端到端阶段`、`1B. 自主挖掘与确认边界`，再读 `delivery-execution-control.md` | 不把自我规划当授权 |
| 评审现有 Loop 是否闭环 | `1. 端到端阶段`、`5. 反模式` | 不只看自动化能否运行 |

## 1. 端到端阶段

```text
意图 / 反馈 / 业务目标
-> 自我挖掘与确认边界
-> 需求收集与事实分层
-> 产品 / 交互设计与验收种子
-> 设计评审 / PRD-系分合议预审
-> TDD / 测试设计
-> 编码实现 / AI Maker 执行
-> 编码评审 / AI Checker / 架构师 CR
-> 可用性 / 安全性 / 可靠性评估
-> 验证发布 / 监控 / 回滚准备
-> 运行支持 / 维护演进 / 能力退役
-> 生产反馈 / 复盘 / 知识回流
```

每一阶段只推进一个判断：当前材料是否足以进入下一环。Loop 的价值不是多跑 Agent，而是让意图、上下文、行动、验证和交接持续闭合。

### 1.0 生命周期覆盖审查

SDLC 只作为生命周期覆盖框架，不替代知止者，也不与 Loop 并列。审查时确认当前任务覆盖了需要负责的构想 / 发现、开发、运行 / 支持、维护 / 演进和退役阶段；采购 / 供应仅在任务实际涉及外部软件、服务或依赖时纳入。安全、权限、风险、可追溯性和知识回流横贯所有阶段，不作为发布前一次性补项。

规划、执行、评估只是受控执行机制，不等于完整 SDLC；Loop 是阶段内和跨阶段的反馈机制，也不会被 SDLC 替代。外部概念进入本体系时，只映射到能力域、阶段、owner、交接物、验证和停止条件，不改主流程名称。

运行、维护或退役缺少生产 owner、观测证据、回滚 / 迁移方案、依赖方通知、数据处理边界或停止维护标准时，不得因为开发和测试完成就宣称生命周期闭环。

轻量问询优先于长方案审查：决策澄清门禁是小闭环总门禁，`grill-me` 是命中升级条件后的升级盘问。关键分叉、含糊回答、半答或连续返工时装载这一独立 Skill；完整盘问、问题台账、历史去重、自决和决策快照由该 Skill 负责。本生命周期只消费确认后的下一阶段输入，不把问询过程写进正式 PRD / 系分正文。

Loop 推进中适时装载 `grill-me`；盘问、问题去重、shared understanding、决策快照和红线记录读该 Skill，执行前对账读 `delivery-execution-control.md`。

每个阶段的小闭环完成后，先自问再问人：Loop 先从现有事实、源码、测试、约规和交接物中自我问询并自我回答；证据足够、风险低且仍在授权内时，自动把结论写入下一阶段输入；缺少 owner 责任判断时，只问 1-3 个聚焦问题；证据仍在收敛且预算允许时继续同阶段一轮；越权、无进展或无法验证时停止交接。

需求变更进入 Loop 时，先做影响识别再改文档或代码：检查 PRD 决策层 / 方案层 / 实现层、系分、接口 / 事件、规则 / 字段、验收种子、测试用例、发布风险、通知对象和过程记录链接。AI 可生成影响清单和同步建议，但业务取舍、公共契约和发布风险仍由对应 owner 确认。

设计和编码进入下一阶段前，必须先识别稳定点 / 变化点：业务规则、状态行为、外部依赖、平台差异、技术选型和同类扩展是否有真实证据。只有已出现或可由产品事实、源码事实、验收种子、生产风险支撑的变化轴，才允许进入接口、策略、工厂、状态机、规则层或配置化设计；没有 owner、验收方式和测试边界的未来想象，按过度设计风险处理，先保持最小显式实现。

规划到执行必须靠执行契约承接，不靠聊天记忆衔接：Spec / 设计 / 任务就绪后，先形成 Execution Contract，写清 owner、状态、写入范围、验证命令、Checker、停止条件和回写位置，再进入 TDD、编码和 CR。CR 或测试发现代码与 Spec 漂移时，先判断是代码偏离、Spec 缺失还是需求变化；代码偏离修代码，Spec 缺失先补 Spec，需求变化走影响识别。

### 1.0A 三层反馈节奏

三层 Loop 同时存在，但越外层越慢、越决定方向。内层可以自动化，中层必须有人类上下文，外层必须有真实用户、市场或生产证据。

| 层 | 时间尺度 | 主责 | 修正对象 | 准出证据 | 不替代 |
| --- | --- | --- | --- | --- | --- |
| Agentic Coding Loop | 分钟到小时 | AI Maker + 架构师 | 代码、测试、实现细节 | Spec、Evals、失败测试、独立验证 | 不决定要做什么 |
| Developer Feedback Loop | 小时到天 | 产品 / 架构 owner | Vision、范围、交互、Spec | 产品上下文、验收种子、设计评审、系分评审 | 不替代真实用户反馈 |
| External Feedback Loop | 天到周 | 业务 / 产品 / 发布 owner | 用户价值、市场判断、生产风险 | 试用反馈、A/B、数据、工单、监控、复盘 | 不直接改代码，也不被内层测试通过替代 |

节奏规则：先让外层反馈定方向，中层把方向翻译成 Spec，内层再执行和验证；如果只有内层绿灯，只能说明实现对当前 Spec 更接近，不能说明产品方向正确或可以发布。需要经典视角时装载 `huaxia-practical-wisdom`，但不能用经典框架替代真实反馈。

| 阶段 | 主责 owner | AI 角色 | 交接物 | 门禁 / 停止 |
| --- | --- | --- | --- | --- |
| 意图收集 | 业务 owner / 产品专家 | 整理事实、问题和不确定性 | 原始意图、证据、影响面、成功/失败信号 | 缺少主体、场景、证据或验收方时停止 |
| 自我挖掘与确认边界 | 知止者编排，业务 / 产品 / 架构 owner 确认关键判断 | 读取现有材料、代码、测试、历史反馈和约规，形成候选需求与边界 | 自主交付控制卡、事实/推断/待确认、人工确认点 | 无来源、冲突事实、目标取舍、范围扩张或高风险动作时停止转人工 |
| 产品 / 交互设计 | 产品专家 / UED | 辅助梳理流程、用例、交互状态和验收种子 | 产品上下文卡、流程 / 用例 / 页面状态、验收种子 | 产品只传话、未解释业务问题或影响面时停止 |
| 设计评审 | 知止者编排，产品 / 架构 owner 决策 | Design Reviewer / MAGI / Checker 提出挑战与风险 | ACCEPT/REJECT/PENDING、风险清单、owner | AI 预审不能替代 owner 决策 |
| TDD / 测试设计 | 资深架构师 / 质量门禁 | 辅助把验收种子转成失败测试候选和验证矩阵 | 测试策略、失败测试候选、验证命令 | 缺业务规则、不变量或验收样例时停止 |
| 编码实现 | 资深架构师 / 工程 owner | AI Maker 在授权范围内实现，按 TDD 推进 | 失败测试、实现、提交切片、状态回写 | 不允许模拟模块、内存版业务 Service 或无业务入口 demo |
| 编码评审 | AI Checker + 架构师 | 对照 Spec、测试和源码锚点找问题 | CR 发现、测试结果、残余风险 | 写代码的 Agent 不能自证通过 |
| 可用性 / 安全性 / 可靠性评估 | UED / 架构师 / 安全或发布 owner | 辅助检查交互恢复、权限、敏感数据、监控和回滚 | 可用性风险、安全风险、可靠性风险、人工确认方 | 高风险项无 owner 或证据时停止 |
| 验证发布 | 发布 owner / 架构师 / 运维 owner | 汇总测试、CR、版本回读、配置回读、冒烟、观测、回滚和交接 | 发布计划、生产生效验证卡、监控指标、回滚方案、Runbook | 没有版本 / 配置回读、冒烟、观测、回滚、人工接管或审批时停止 |
| 反馈回流 | 知止者 + 对应 owner | 整理复盘、知识归位和 fixture 缺口 | Decision Log、Goal Ledger、Skill / fixture / 脚本更新建议 | 不把未经验证经验沉淀为规则 |

## 1A. 阶段与能力衔接

阶段只回答“现在位于生命周期哪里”，能力路由只回答“当前需要什么专业能力和独立验证”。两者不得各自维护一套 owner 表：

1. 先用本文的端到端阶段表确定当前阶段、输入、交接物和停止条件。
2. 再按 `capability-routing.md` 选择一个主能力、必要的协同能力、明确不加载的能力和独立 Checker。
3. 外部工具或框架只能补当前阶段的一个方法缺口，不能改写能力 owner、扩大授权或成为第二行动主体。
4. 交接卡只记录本轮实际选择结果，不复制整张能力地图；能力边界变化时只修改 `capability-routing.md`。

高频衔接只作导航：产品阶段形成产品上下文与验收种子，工程阶段消费已确认事实并形成系分、代码与验证，结构化生成只产出候选骨架，纯约规只产出规则判断，发布阶段只汇总证据并等待发布 Owner。具体主能力与协同能力始终回到 `capability-routing.md` 判断。

### 1.1A 外部框架 / 工具协同策略

外部框架或工具不作为新流程入口，只按当前角色节点补一个缺口。先根据上下文选策略，再读对应 reference。

| 上下文缺口 | 优先策略 | 可吸收能力 | 不允许 |
| --- | --- | --- | --- |
| 需求模糊、范围发散 | 产品优先 | `grill-me` 的一次一个问题；GStack `/office-hours` forcing questions | 不把问询过程写进正式 PRD，不替代产品 owner |
| 工程方案不稳、任务较大 | 架构优先 | Superpowers 方法纪律、GSD 上下文 / Spec / 状态、渐进式 SDD / Harness 规范化 | 不新增并列流程，不默认运行外部脚本 |
| 同一方案需要多视角挑战 | 角色链审查 | GStack 角色链模板：CEO / Eng / Design / Review / QA / Ship | 命令名只作触发别名，不生成外部命令菜单 |
| 已有结构化 Java 输入 | 代码生成链 | `java-service-code-generator` 生成骨架，Wind 约规审查，架构师 TDD / CR | 代码生成不替代业务设计、测试或源码级 CR |
| 需要理解代码或对齐设计 | 只读理解 | Gemini / AgentRC / WorkBuddy / Understand Anything 作为候选只读工具 | 工具摘要不替代源码锚点、测试、CR 或 owner 确认 |
| 需要代码质量补扫 | 质量门禁 | Ponytail 查过度设计，Open Code Review 做外部 Checker，Wisdom Lens 做取舍校准 | 外部工具不自证通过，不替代资深架构师 |
| 要沉淀上下文或经验 | 知识回流 | Trellis 仓库级记忆思想、Context System、source-map、fixture | 不默认建设外部知识库，不沉淀未验证经验 |

策略选择规则：没有明确用户指令时，按“当前最大不确定性”选择一个策略；如果缺口同时存在，先产品事实，再架构边界，再生成 / 编码，再验证发布，最后知识回流。

### 1.2 角色视角顺序

知止者默认按下列视角切换。当前任务不涉及的视角可以跳过，但不能把 Maker 和 Checker 合并成自证。

| 视角 | 主要问题 | 输出 |
| --- | --- | --- |
| Design Owner | 要解决什么问题，用户 / 主体 / 对象 / 状态 / 规则 / 验收是什么？ | 产品设计、交互状态、系分或设计输入。 |
| Design Reviewer | 方案是否完整、可测试、可开发、可运营、可发布，是否存在过度设计或证据缺口？ | 设计评审结论、ACCEPT/REJECT/PENDING。 |
| TDD / Test Designer | 先用什么失败测试、验证矩阵或验收样例证明要做对？ | 测试策略、失败测试候选、验证命令。 |
| Implementation Maker | 在授权范围内如何最小实现？ | 代码变更、状态回写、提交切片候选。 |
| Code Reviewer | 实现是否对齐 Spec、源码锚点、契约、测试和项目约规？ | CR 发现、风险等级、修复建议。 |
| Usability / Safety / Security Reviewer | 用户路径、错误恢复、权限、敏感数据、审计、监控、回滚是否可信？ | 可用性 / 安全性 / 可靠性风险和人工确认方。 |
| Release / Quality Gate | 当前证据是否足以发布、回滚、观测和复盘？ | 发布门禁、残余风险、知识回流位置。 |

### 1.2A GStack 角色链映射

GStack 的 `/office-hours`、`/plan-ceo-review`、`/plan-eng-review`、`/plan-design-review`、开发、`/review`、`/qa`、`/ship` 只作为角色链审查模板接入知止者。它解决“同一任务要被不同角色视角连续挑战”的问题，不新增对外主流程、不要求用户记命令，也不替代产品专家、资深架构师、质量门禁或发布 owner。

GStack 的价值不是命令名，而是连续逼问：先问为什么做，再砍范围，再审工程和交互，最后用独立 CR、QA 和发布证据准出。

| GStack 模板段 | 知止者阶段 | 主责与能力来源 | 必须回答的问题 | 准出 / 停止 |
| --- | --- | --- | --- | --- |
| `/office-hours` 产品思考 | 意图收集 / 产品设计前置 | 产品专家 / UED，读产品上下文与验收种子相关 reference | 核心问题、现状替代方案、10-star 体验、MVP、技术风险、成功指标是什么？ | 不能说明业务问题、影响面或验收信号时停止。 |
| `/plan-ceo-review` 范围收敛 | 产品方案 / 目标层 Review | 知止者编排 + 产品 owner | 是否过大、是否可逆、MVP 是否足够、非目标和成功指标是否清楚？ | 业务取舍或优先级不明时回 owner。 |
| `/plan-eng-review` 工程评审 | 设计评审 / 系分前置 | 资深架构师，读系分、测试、编码约规 | 数据流、接口、边界、edge case、测试入口、发布风险是否成立？ | 无真实业务入口、契约或验证方式时停止。 |
| `/plan-design-review` 交互评审 | 产品 / UED 评审 | 产品专家 / UED | 页面状态、loading、错误恢复、空态、权限和可用性是否完整？ | 用户路径或关键状态缺失时回产品 / UED。 |
| 开发实现 | TDD / 编码实现 | 资深架构师 / AI Maker | 是否有失败测试候选、写入范围、项目约规、回写状态和停止条件？ | 未获 Grant、测试不可设计或范围外改动时停止。 |
| `/review` 源码 CR | 编码评审 / AI Checker | 资深架构师，读 coding-review-deep-dive 与项目约规 | 是否对齐 Spec、测试、源码锚点、架构原则和红线？ | Maker 不自证通过；高风险问题必须修复或交 owner。 |
| `/qa` QA 验证 | 质量 / 测试门禁 | 知止者质量门禁 + 资深架构师 testing 能力 | 正常、边界、失败、回归、安全、可靠性验证是否足够？ | 失败用例、残余风险或不可复现结果必须回写。 |
| `/ship` 发布准出 | 验证发布 / 交接 | 发布 owner / 资深架构师 | 测试、CR、版本回读、配置回读、冒烟、监控、回滚、变更说明、生产交付审查卡、生产生效验证卡和人工接管是否就绪？ | 缺生产生效证据、生产交付审查卡、观测、回滚或人工接管时停止；Git、PR、merge、部署和生产操作仍需显式授权。 |

使用规则：命令名只作触发别名；若用户只给一个阶段，就只输出该阶段的 owner、交接物、验证与停止条件。若用户给完整 GStack 模板，按知止者输出阶段链路和下一 owner，不复制外部命令体系。

八段准出链：Office Hours 只产出产品问题和验收信号；CEO Review 只收敛 MVP 和非目标；Eng Review 只判断契约、数据流和风险；Design Review 只判断用户路径和状态；开发只在 TDD / Grant 内最小实现；Review 只做源码证据裁决；QA 只按矩阵复现；Ship 只按生产交付审查卡和生产生效验证卡准出。

## 1B. 自主挖掘与确认边界

自主推进不是让 AI 替人拍板，而是让 Loop 先把可机械完成的探索、整理和低风险验证做完，再把关键判断交回 owner。每次用户要求“AI 自己推进、自己规划、自己挖掘、自己确认、自己完成”时，先输出自主交付控制卡。

可自我挖掘：

- 已提供的用户目标、PRD、系分、OpenSpec、Issue、评审意见、测试、日志、代码、提交历史、项目 `AGENTS.md`、Skill reference 和 source-map。
- 真实代码入口、调用关系、状态机、数据对象、错误路径、验证命令和已有测试覆盖。
- 历史反馈、CR 高频问题、失败测试、生产监控摘要或复盘材料，但必须标明来源和时效。

可自我规划：

- 把候选需求拆为设计、需求 CR、TDD、编码、编码 CR、验证发布和回写步骤。
- 生成最小下一步、验证顺序、状态回写位置、失败回退、Maker / Checker 分工和停止条件。
- 对低风险本地任务提出受控执行授权候选，但不能自行扩大授权。

可自动执行：

- 只读阅读、检索、引用定位、影响面初筛、候选需求卡、验证矩阵草案、失败测试候选、CR 检查清单和本地低风险验证。
- 已在 Grant 范围内、写入范围清楚、可回滚、可验证、失败可停止的文档 / Skill / 测试 / 代码小切片。

必须人工确认：

- 业务价值、优先级、需求取舍、目标用户、产品方向、验收方和失败成本。
- 公共契约、数据迁移、状态机、资金 / 合规 / 安全 / 权限 / 隐私、生产数据、发布策略、不可逆操作和成本预算。
- Git stage / commit / push / PR / merge、联网、安装依赖、调用外部服务、读取密钥、部署和生产操作。
- 多方案取舍、事实冲突、目标不清、结果不可验证、置信度不足、连续两轮无新增证据或需要扩大范围。

自主交付控制卡：

```text
自主交付控制卡
关联 Goal / 业务目标:
已读事实源:
候选需求 / 问题:
可自我挖掘:
可自我规划:
可自动执行:
必须人工确认:
当前置信度: 高 / 中 / 低，理由:
轻量问询: 关键分叉 / 建议答案 / 已自答 / 需 owner 判断
自我问询:
自我回答:
下一阶段: 产品设计 / 需求 CR / TDD / 编码 / 编码 CR / 验证发布 / 停止
状态回写位置:
停止条件:
```

确认规则：AI 只能确认“材料中已经有证据支持的事实”和“当前授权内可执行的低风险动作”；不能确认业务意图、需求价值、用户验收、架构批准、测试通过、CR 准出、Git 授权或上线审批。

## 2. 角色边界

- **知止者**：需要跨阶段协同时持续持有目标与状态，决定当前阶段、交接物、验证门禁和停止条件；能力 owner 直接引用 `capability-routing.md`，不替代 PRD、系分、代码、测试、CR 或发布审批。
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
自主推进边界:
输入事实:
合理推断:
待确认:
轻量问询 / 建议答案:
`grill-me` 盘问结论: question_id / 已问问题 / 答案状态 / 缺失项 / 写回位置
本阶段交接物:
进入下一阶段的证据:
小闭环结论: 自决推进 / 询问 owner / 继续收敛 / 停止交接
自我问询:
自我回答:
自动问询 / 决策:
下一阶段输入:
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
- 用 GSD / 工程执行/Goal 等机制名替代角色协作，导致设计、评审、TDD、编码、CR、安全 / 可用性评估和发布门禁混在一个 Agent 输出里。
- Loop 自动产出很多 PR，但团队无法复述目标、关键变更、证据、风险和回滚方式。
- 过程文档、讨论草稿、AI 推理轨迹混入正式 PRD、系分或 OpenSpec，导致交付契约不清。
