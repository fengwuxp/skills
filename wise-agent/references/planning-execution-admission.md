# 计划与执行准入

本文定义知止者中对中大型任务的计划与执行准入判断。GSD 不再作为对外独立模式，而是产研交付视图的分波计划层；CAD 不再作为对外独立模式，而是单个原子任务的受控执行子循环。本文只回答是否需要 GSD Round 0、如何形成 Wave / Atomic Task 候选、哪些缺口阻断 CAD、下一步交给谁；不替代资深架构师的工程任务包、`cad-mode.md` 或 Execution Grant。

## 使用时机

- 用户明确有中大型项目、长任务、上下文衰减、多 Agent / Wave 编排、GSD-like 工作流或 CAD 自动推进诉求。
- 用户要求把 GSD、CAD、Goal 多个工作模式统一压缩进 Loop，但仍需要保留大项目分波和原子执行能力。
- 产品上下文包、PRD-Lite、OpenSpec 草案、AI 原型/eval 或 dogfooding 反馈已经出现，需要判断能否进入工程侧 GSD Round 0。
- 用户要求“结合 GSD 与 CAD”“自动推进哪些任务”“默认授权哪些任务”“按什么顺序交给架构师或 Agent”“任务阶段是否提交代码”“Execution Grant 还缺什么”。
- 用户希望减少每个任务审批，希望在 GSD/CAD 模式下默认授权、自动推进，或提到 Codex 的“替我审批”模式。
- 用户担心大项目被拆散、上下文漂移、多个 Agent 互相覆盖、CAD 被误用于整个 Roadmap。
- 目标大致存在，但到达目标的路线仍模糊、明显超过一次会话可可靠形成 Spec 或计划，需要先消除决策不确定性。
- 用户要求 GSD 模式支持 Superpowers skills、TDD、Review、verification-before-completion 或外部工程纪律接入。
- 用户要求把 Agent Loop、`/goal`、`/loop`、auto mode、后台 Agent 或多 Agent 监督接入 GSD/CAD，并希望持续推进但可验证、可停止、可交接。
- AI 产品、企业协作 AI、Agent 入口或组织级 AI 助手要从战略叙事、AI 原型、发布会目标或 dogfooding 进入工程化，需要先判断是否真的值得进入真实工作流。

## 不适用场景

- 只写普通 PRD、产品方案或 Backlog 决策；正文交给 `产品架构专家`。
- 只做架构设计、代码 Review、Bug 修复、测试或生产变更；工程执行交给 `资深架构师`。
- 已经选定单个原子任务并要求判断 CAD Mode 进入门禁；详细规则交给 `senior-software-architect/references/cad-mode.md`。
- 用户要求真实执行 Git、联网、部署、生产数据或不可逆操作；必须另有用户授权和工具层许可，不能进入默认授权。

## 读取后必须产出

- 知止者的产研交付视图准入结论：轻量执行、进入 GSD Round 0、只做只读侦察、可形成 CAD 候选，或必须停止补上下文。
- GSD / Loop / CAD 协同状态机：当前处于 Round 0、GSD Candidate、Wave Plan、Plan Grant Active、Loop Candidate、CAD Candidate、CAD Loop Active、Verified、Paused、Escalated 还是 Closed。
- GSD Round 0 缺口：目标、非目标、对象/规则、OpenSpec、owner、写入范围、验证命令、风险确认方和停止条件。
- 决策寻路结论：是否需要建图、当前 Destination、低分辨率地图、Next decision 和进入 Spec / Goal Ready 的阻断项。
- Wave / Atomic Task 候选：只给候选形态、依赖顺序、owner、写入/只读边界、生产可用能力锚点、事实/推断/待确认边界和验证证据，不写成执行授权。
- Superpowers 方法门禁：当前 GSD 是否需要参考 brainstorming、writing-plans、test-driven-development、requesting/receiving-code-review、verification-before-completion 等外部 skill，以及对应的 TDD、CR 和完成前验证要求。
- AI 产品工程化准入卡：业务 context、真实工作流、用户收益/负担、权限与责任、旧系统接入、灰度止损、成本稳定性和事实边界是否足够。
- CAD 候选缺口：Task ID、写入范围、验证命令、工作区状态、Execution Grant、人工确认点和风险阻断项。
- GSD/CAD 授权策略卡：当前适合只读、计划内低风险执行、Plan Grant、Wave Grant、CAD Grant、Codex 替我审批通道，Git 策略是仅建议提交还是验证后阶段提交，还是必须显式确认。
- Agent Loop 准入卡：Loop 是否有 Goal、状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件、授权策略和交接物；缺失时只输出补齐项，不进入自动循环。
- Engineering Handoff Card：跨知止者、GSD、Loop 和 CAD 交接时固定包含 Goal ID、Wave/Task ID、状态载体、写入范围、验证命令、反馈源、停止条件、Git 策略和下一 owner。
- 三卡交接结论：Product Context Card 是否足以支撑工程，Engineering Handoff Card 是否足以交给架构师，生产交付卡是否足以进入生产可用 Loop；缺失时说明回退 owner。
- 下一步 owner：产品专家、资深架构师、代码生成器、人类 owner 或当前流程继续补齐。

## 需要继续读取的 reference

- 产品上下文、PRD-Lite 和 AI 原型交接读 `product-to-engineering-lifecycle.md`。
- OpenSpec、Superpowers、Harness、Agent 权限和多 Agent 治理读 `engineering-governance.md`。
- Agent Loop、`/goal`、`/loop`、auto mode、后台 Agent 和循环停止条件读 `delivery-execution-control.md`。
- Superpowers 官方插件状态、方法调度矩阵、MIT 许可和执行边界读 `superpowers-skill-library.md`。
- 验证矩阵、CR、发布和质量/测试门禁读 `verification-review-release.md`。
- 工程侧大项目任务包、上下文账本、阶段状态和 Wave 执行细则交给 `senior-software-architect/references/ai-large-project-orchestration.md`。
- 单个原子任务的 CAD Mode、Execution Grant 和自动分轮执行细则交给 `senior-software-architect/references/cad-mode.md`。
- 单个关键决策需要盘问、历史去重或 Owner 裁决时装载独立 `grill-me`；本文只持有地图和选择下一决策。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否进入 GSD Round 0 | 1、2、3 | 不生成完整工程任务包 |
| 目标存在但路线仍模糊 | 1、2、2A | 不生成 Spec、Wave 或实施计划 |
| 拆 Wave / Atomic Task 候选 | 3、4 | 不写 CAD 每轮执行计划 |
| 判断 CAD 候选缺口 | 5、6 | 不把候选当 Execution Grant |
| 优化 GSD/CAD 授权策略或阶段提交 | 5、6、6A、6B | 不把全部动作默认通过 |
| 梳理 Loop/GSD/CAD 协同状态机和交接卡 | 1、2、6、7、7A | 不直接进入 CAD |
| 判断 GSD/CAD 是否可接入 Agent Loop | 1、2、3、6，再读 `delivery-execution-control.md` | 不把 Loop 写成 Execution Grant |
| AI 产品或 Agent 工作流是否值得工程化 | 3A，并回读 `product-to-engineering-lifecycle.md` | 不把战略风口、发布会、DAU 或 demo 当准入证据 |
| 给 GSD 补 Superpowers/TDD/Review 门禁 | 3、4、5，并回读 `superpowers-skill-library.md` | 已安装不等于脚本、Git 或 subagent 授权 |
| 产品上下文进入工程 | 7，并回读 `product-to-engineering-lifecycle.md` | 不把 MVP 当工程授权 |
| 流程评审或 CR 前置 | 8、9，并回读 `verification-review-release.md` | 不替代源码级 CR |

## 1. 职责边界

GSD 的目标是交付生产可用能力，不是让 AI 随机推进一组看上去有进展的模拟模块。所有 GSD Round、Wave、Atomic Task 和 CAD 候选都必须回答：它服务哪个真实业务目标，落在哪个生产边界或真实入口，如何由验收种子、测试、CR、发布/回滚条件或人工确认来证明可用。回答不了时，只能做 Round 0 补齐或只读侦察。

工程实现层的额外红线：除了缓存能力、测试替身、fixture、沙盒模拟或明确标注的 demo，业务代码不应提供内存版 Service 实现来冒充生产能力。`InMemoryXxxService`、`FakeXxxService`、`MockXxxService`、Map/List 存储型业务实现或只在进程内保留状态的应用服务，如果进入生产源码路径，必须被标记为阻断项并交给 `资深架构师` 做编码/CR 处理。

事实边界红线：GSD/CAD 候选不得基于无根据猜测、模型脑补、工具总结、外部文章观点或超出用户目标的功能扩张。凡是没有用户目标、来源材料、源码锚点、验收种子或验证证据支撑的内容，只能写入 `推断 / 待确认 / 范围外不做`，不能写成任务、实现、准入结论或授权缺口。

GSD/CAD 在知止者中分五层：

| 层级 | 回答的问题 | owner |
| --- | --- | --- |
| 知止者 | 是否进入知止者，当前采用只读理解、产研交付、验证发布或知识回流哪个场景视图，谁接下一步。 | 本技能 |
| GSD-like 大项目编排 | 什么可以被执行，如何用 Stage/Wave/Atomic Task 和上下文账本保持可恢复。 | `资深架构师` |
| Agent Loop | 每轮如何读取状态、执行动作、吸收反馈、验证、停止和交接。 | 本技能编排，执行侧按 owner 分派 |
| CAD Mode | 已选定的单个原子任务是否可以受控自动推进。 | `资深架构师` |
| Plan Grant / Execution Grant | 用户实际授权做什么、能改哪里、能否 Git、是否阶段提交、何时停止。 | 用户 + 工具权限 |

边界句：

- 知止者决定“是否进入产研交付视图、是否启用 GSD/CAD 内部层，以及下一步 owner”。
- GSD-like 决定“哪些阶段和任务可以被执行”。
- CAD Mode 决定“当前选中的原子任务是否可以自动执行”。
- Agent Loop 决定“每轮如何读取状态、执行动作、吸收反馈、验证和停止”。
- Plan Grant / Execution Grant 决定“本轮实际允许做什么”。

授权策略不是让每个任务都重新问一次，也不是让所有动作无条件通过。GSD/CAD 应把授权前移到 Goal 任务计划、Wave 或 CAD Grant 层：用户明确说 `GSD + Goal 按任务计划推进`、`按任务计划自动推进` 或等价意图时，如果任务计划已经列清目标、写入范围、验证命令、停止条件和显式确认边界，可以形成 Plan Grant；在 Plan Grant 有效期内，低风险原子任务直接推进，不再逐任务索要 Execution Grant。一旦越过范围、触发高风险动作或验证失败，必须停止并升级确认。

Codex 的“替我审批”只能作为当前会话已经由用户开启的运行时审批模式：它可以承接低风险、可回滚、范围内的工具审批噪音，但不能被 Skill 自行开启，也不能绕过项目规则、sandbox、用户授权、Git/联网/生产等硬门禁。

Agent Loop 只能建立在 Goal、GSD、Harness 和授权策略之上。`/goal`、`/loop`、auto mode、后台 Agent 或多 Agent 监督若没有状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测和停止条件，只能作为待补齐的 Loop 候选，不能进入自动推进。

Superpowers 在 GSD 中只作为方法纪律层：它回答“怎么高质量地做”，例如澄清、计划、TDD、Review、完成前验证和分支收尾检查；不回答“能不能做”“能改哪里”“是否授权”。官方插件可以独立安装并由知止者按需调度，但启用状态不能成为运行脚本、创建 worktree、启动 subagent、采用外部 Git 默认动作或扩大项目写入的授权。

### 1A. GSD / Loop / CAD 协同状态机

复杂任务进入自动推进前，先用一个状态机描述当前位置，不用多个模式口头并行推进：

```text
Round 0
-> GSD Candidate
-> Wave Plan
-> Plan Grant Active
-> Loop Candidate
-> CAD Candidate
-> CAD Loop Active
-> Verified / Paused / Escalated / Closed
```

状态含义：

- `Round 0`：目标、主体、证据、边界、验收或风险仍需补齐。
- `GSD Candidate`：值得进入大项目编排，但 Wave / Atomic Task 仍是候选。
- `Wave Plan`：Wave 顺序、Task 候选、验证矩阵和提交切片已经形成，但未必授权。
- `Plan Grant Active`：用户已授权按任务计划推进低风险本地任务，且写入范围、验证命令、停止条件和显式确认边界清楚。
- `Loop Candidate`：Goal、状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测和停止条件正在补齐。
- `CAD Candidate`：已有单个原子任务、写入范围、验证命令和授权草案，等待架构师检查 CAD 门禁。
- `CAD Loop Active`：资深架构师在单个原子任务内执行受控 Red / Green / Review / Verify 闭环。
- `Verified`：本轮验证证据足够，可更新状态、提交切片或进入下一 Task。
- `Paused`：用户中断、预算耗尽、上下文不足或等待 owner 补材料。
- `Escalated`：命中高风险、授权外动作、验证异常、用户改动冲突或业务口径选择。
- `Closed`：Goal 或子 Goal 完成，已记录验证、残余风险、提交建议和知识回流。

状态跃迁必须通过 `Engineering Handoff Card` 交接。没有交接卡时，只能停在当前状态补齐，不能从 GSD 直接跳到 CAD，也不能把 Loop 当作授权。

## 2. 准入分级

先按输入成熟度分级：

| 成熟度 | 结论 | 典型动作 |
| --- | --- | --- |
| 想法 / 文章观点 / 工具宣传 | 不进入 GSD/CAD。 | Round 0 补目标、主体、证据、风险、验收。 |
| AI 原型 / eval / dogfooding | 可进入产品到工程交接。 | 补产品上下文包、PRD-Lite 缺口、验收种子。 |
| 产品上下文包 / OpenSpec 草案 | 可进入 GSD Round 0 候选。 | 输出 GSD Round 0 缺口和架构师交接要求。 |
| OpenSpec + Harness 摘要 | 可形成 Wave / Atomic Task 候选。 | 输出 Wave 顺序、任务候选、验证矩阵草案。 |
| 单个原子任务 + 验证命令 + 授权缺口清楚 | 可标记 CAD 候选。 | 交给资深架构师检查 CAD Mode 和授权策略。 |
| GSD + Goal 任务计划 + 验证命令 + 低风险写入范围 + 停止条件清楚 | 可形成 Plan Grant。 | 按任务计划推进范围内低风险本地任务，命中硬门禁时停止。 |
| 单个原子任务 + 验证命令 + 低风险写入范围 + 停止条件清楚 | 可形成 CAD Grant 候选。 | 在 Grant 有效期内默认推进低风险动作，命中硬门禁时停止。 |
| Goal + 状态载体 + 反馈源 + 验证者 + 预算/最大轮次 + 无进展检测 + 停止条件 | 可形成 Agent Loop 候选。 | 只在授权范围内循环推进，达到停止条件或硬门禁时交接。 |

GSD 规划还必须给出提交切片：每个 Wave / Task 完成验证后应如何组成一个可独立理解、验证和回滚的提交单元。默认 Git 策略为 `summary_only`，只输出建议提交单元和建议 commit message；只有用户明确要求“阶段提交 / 任务提交 / 自动提交本地 commit”，且 Grant 写清 Git 范围时，才可进入 `commit_after_verified_task`。

## 2A. 决策寻路准入

决策寻路不是新的 Skill、Goal 或执行流程，而是 `Round 0 / Goal Draft` 中消除不确定性的临时工作方式。只有同时满足以下条件才进入：

- 能用一两句话命名 Destination，即完成寻路后应得到的 Spec、决策或可计划状态。
- 通往 Destination 的关键路线仍模糊，当前不能可靠写成 Spec 或最小计划。
- 工作明显超过一次会话可承载，跨轮恢复或多人协作确有价值。

只有可查 Facts、路线已经清楚、当前会话可闭环，或用户已提供确认过的 Spec / 计划时，跳过决策寻路，直接进入对应专业交付与验证。

优先复用用户指定位置或项目已有 Issue、Goal Ledger、Spec、Decision Log、任务状态。没有获准载体时只在当前任务输出；不得自动创建 Issue、分支、Worker 或外部任务系统。地图只作索引，每个决策正文只保留一个权威位置，地图只写名称、状态、摘要和链接：

```text
Destination: 寻路完成后应达到的清晰状态。
Decisions so far: 已关闭决策的名称、单行摘要和权威链接。
Frontier: 已能准确表述，且未关闭、未阻塞、未占用的决策。
Not yet specified: 已知在前方，但当前还无法准确表述的问题区域。
Out of scope: 与本轮 Destination 无关，不会自动复活的内容。
Next decision: 当前只选择一个最高价值 Frontier 决策。
Handoff condition: 何时可进入 Spec、最小计划或 Goal Ready。
```

`Frontier` 与 `Not yet specified` 的分界不是能否回答，而是现在能否准确写出待裁决命题；不能准确表述的迷雾不得预拆成任务。决策关闭后才把新近可表述的内容提升到 Frontier；若新结论使旧节点失效、越界或重新阻塞，应更新、关闭或移入 Out of scope，不保留僵尸任务。

每轮最多关闭一个决策，并按节点性质复用现有能力：

| 节点性质 | 路由 | 边界 |
| --- | --- | --- |
| 需要 Owner 价值取舍或公共契约裁决 | `grill-me` | 一次一个问题，结论写回原权威载体。 |
| 缺外部文档、API、项目材料或知识库事实 | `research`：使用现有读取与检索能力 | Worker 仅在输入可冻结、互不写入且已有授权时使用。 |
| 需要低成本具体产物才能判断行为或形态 | `prototype`：路由产品或工程主能力 | 原型只服务决策，不冒充最终交付。 |
| 必须先获取账号、环境、数据或人工操作结果 | `prerequisite task` | 只完成解锁决策所需动作，仍服从联网、权限和写入授权。 |

地图存在开放 Frontier，或 Not yet specified 中仍有阻断 Destination 的迷雾时，Goal 保持 `Draft`，不得生成完整 Spec、Wave、Atomic Task、Plan Grant 或执行方案。路线清晰后才进入 Spec、最小计划或 Goal Ready；若初始梳理没有迷雾，立即停止建图并回到当前任务的最短交付路径。

## 3. GSD Round 0 判断

进入 GSD Round 0 前至少要能回答：

- 业务目标、非目标、成功标准和失败成本是什么。
- 关键对象、状态、规则、异常路径和验收种子是否清楚。
- 产品 / 系统 DNA 是否清楚：核心对象、不变量、状态流转、责任边界、演化规则和验证方式能否从产品上下文追踪到系分、测试、监控和 CR。
- 生产可用能力是什么：真实业务入口、运行边界、数据/权限/资金/租户影响、发布和回滚要求是否能说明。
- 哪些材料是事实，哪些是推断，哪些需要产品、人类 owner 或专业方确认。
- 是否存在无根据猜测、超出用户目标的功能扩张或 AI 幻觉风险；存在时必须停止在 Round 0。
- 工程写入范围、只读范围、禁止事项和高风险边界是否能初步收敛。
- 验证命令、人工验收方式、CR 前置条件和发布门禁是否有候选。
- 是否需要 Superpowers 方法门禁：需求澄清是否需要 `brainstorming`，任务拆解是否需要 `writing-plans`，实现是否需要 `test-driven-development`，CR 是否需要 `requesting-code-review` / `receiving-code-review`，完成前是否需要 `verification-before-completion`。
- 是否需要上下文账本、阶段状态、恢复入口和多 Agent / Wave 编排。
- 是否需要 Agent Loop；如果需要，状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测和停止条件是否清楚。
- 当前授权策略是否清楚：只读、计划内低风险执行、Plan Grant、Wave Grant、CAD Grant、Codex 替我审批，还是需要显式确认。

缺任一关键项时，只输出补齐清单，不建议 CAD。

### 3A. AI 产品工程化准入卡

当输入来自 AI 产品复盘、企业协作 AI、Agent 入口、AI 原型、发布会节点、dogfooding 或“AI 已经能做一些事”的材料时，先判断它是否值得进入 GSD Round 0。知止者只做工程化准入，不替代产品专家确认发心、定位和用户张力；若产品侧仍未回答清楚，应先退回 `产品架构专家`。

准入卡至少检查八项：

| 检查项 | 准入问题 | 阻断信号 |
| --- | --- | --- |
| 业务 context | 是否有足够组织关系、对象、权限、历史数据、任务状态和术语口径支撑 AI 判断。 | 只有聊天总结、页面草图或孤立 prompt。 |
| 真实工作流 | AI 是否进入用户已经发生的任务链，并能推动任务完成。 | 只新增入口、卡片、提醒、看板或汇总层。 |
| 用户收益 / 负担 | 受益用户和被影响用户是否分开验证，收益是否大于新增操作和被监督风险。 | 只证明管理者、发信人或组织侧收益。 |
| 权限与责任 | AI 能看什么、做什么、谁确认、谁申诉、谁审计、谁承担错误后果。 | 默认站在组织或强势角色一侧，缺可解释/可关闭/可申诉边界。 |
| 旧系统接入 | 是否识别端侧差异、权限系统、客户定制、消息/审批/日程等既有系统技术债。 | demo 可运行但生产路径、端侧一致性或兼容改造不清。 |
| 灰度与止损 | 是否有内测、灰度、反馈纠偏、暂停条件、回滚和退场路径。 | 发布会倒排、舆论先行、全量上线前缺真实用户验证。 |
| 成本与稳定性 | token/算力、延迟、失败率、兜底、人工接管和运营成本是否可观测。 | 只看 DAU、曝光、生成量或功能上线数量。 |
| 事实边界 | 哪些来自用户材料、源码、数据、eval 或真实反馈，哪些只是外部文章观点或组织期待。 | 把外部文章、竞品叙事、模型能力宣传或管理愿望写成任务事实。 |

输出格式：

```text
AI 产品工程化准入卡

当前结论: 不进入 GSD / 只做 Round 0 / 可进入产品到工程交接 / 可进入 GSD Round 0 候选
主发心与首批用户:
真实工作流:
context / 权限 / 责任:
旧系统与生产路径:
灰度止损:
成本稳定性:
事实 / 推断 / 待确认 / 范围外不做:
下一步 owner:
```

不满足准入卡时，只能输出 Round 0 补齐清单或回到产品专家，不得生成 Wave、Atomic Task 或 CAD 候选。

## 4. Wave / Atomic Task 候选

知止者只输出候选形态，不替代架构师生成正式任务包：

```text
Wave 0：只读侦察、产品/工程上下文补齐、风险确认、代码库理解结论包。
Wave 1：OpenSpec、公共契约、模型、测试夹具和验证底座。
Wave 2：互不重叠的实现任务、适配器、页面或批处理。
Wave 3：集成验证、CR、发布准备和复盘材料。
```

Atomic Task 候选至少描述：

- 候选 Task ID 或临时编号。
- 目标和非目标。
- owner 候选。
- 写入范围候选、只读范围候选和禁止事项。
- 依赖哪个 Wave、哪个契约或哪个任务完成。
- 生产可用能力锚点：真实业务入口、受影响的生产路径、上线/回滚边界或人工确认方。
- 产品 / 系统 DNA 锚点：本任务保护或改变哪些不变量、状态流转、边界或演化规则；没有锚点时不能写成实现任务。
- 事实依据、推断依据、待确认项和范围外不做；没有依据的内容不得进入任务目标或实现建议。
- 验收场景和验证证据候选。
- Superpowers 方法纪律候选：TDD 切入点、最小 Review 输入包、完成前验证命令和不采用的外部默认流程。
- 是否可能成为 CAD 候选，以及阻断原因。
- 是否可能成为 Loop 候选，以及状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测和停止条件缺口。
- 建议授权模式：只读、计划内低风险执行、Wave Grant、CAD Grant 或显式确认。

同一 Wave 的候选任务不得共享同一写入文件、公共契约、状态机或测试夹具；如果共享，必须拆顺序或交给架构师重切。

Wave Loop 与 CAD Loop 的差异：

- `Wave Loop` 负责状态推进、任务分派、验证矩阵更新、提交切片建议和 owner 交接；默认不直接改业务代码。
- `CAD Loop` 只覆盖一个已选定原子任务的代码 / 测试 / 文档小步变更，必须由资深架构师按 `cad-mode.md` 执行。
- Wave Loop 发现两个任务共享写入范围、公共契约、状态机或测试夹具时，必须拆顺序或暂停，不能并行推进。
- CAD Loop 完成后必须把验证证据、残余风险、文件范围和下一步状态回写给 Wave Loop 或 Goal Ledger。

## 5. CAD 候选缺口

CAD 候选只写“候选”和“缺口”，不写成执行授权。判断时逐项检查：

- 是否只有一个已选定的 Task ID 或阶段切片。
- 写入范围是否足够窄，且能区分只读参考。
- 是否有可运行或可替代的验证命令。
- 是否有停止条件：规格不清、验证失败、权限不足、风险升级、用户中断。
- 是否已经区分事实、推断、待确认和范围外不做；未区分时不能进入 CAD。
- 是否已有 Superpowers/TDD/Review/Verification 方法门禁，或明确说明当前任务为何不需要；缺少时只能标为 CAD 候选缺口。
- 是否有工作区状态检查，能识别用户已有改动。
- 是否需要 Git、联网、依赖安装、Docker/服务启动、数据库迁移或生产操作；需要时必须列入显式授权缺口。
- 是否涉及资金、权限、租户、审计、合规、风控、结算或生产行为；涉及时必须设置人工确认点。

结论只能是：

- `不是 CAD 候选`：缺 OpenSpec、任务边界、验证或风险确认。
- `CAD 候选但缺授权策略`：任务边界和验证清楚，但缺默认推进范围、显式确认边界或工具层权限。
- `CAD Grant 候选`：任务边界、低风险写入范围、验证命令、停止条件和默认审批通道清楚，可在 Grant 有效期内默认推进。
- `可交给架构师检查 CAD Mode`：已有单个原子任务、验证和授权草案，下一步读 `cad-mode.md`。

## 6. 授权策略与 Execution Grant 缺口

知止者可以设计授权策略、形成 Plan Grant 草案和指出 Execution Grant 缺什么，但不能替用户开启工具权限。授权策略分六档：

| 档位 | 含义 | 可默认通过 | 必须停止 |
| --- | --- | --- | --- |
| 只读侦察 | 仅读取工作区和公开项目文件，形成理解包。 | 读仓库、查引用、运行只读检查。 | 读取无关私有目录、联网、写文件。 |
| 计划内低风险执行 | 用户已要求推进，且任务在当前工作区、低风险、可回滚、有验证命令。 | 编辑已声明范围内文件、运行本地测试/校验、记录结果。 | 改范围外文件、覆盖用户改动、验证失败后继续扩张。 |
| Plan Grant | 用户明确要求按任务计划推进，且 Goal、任务计划、写入范围、验证命令、停止条件和显式确认边界已列明。 | 任务计划内低风险本地读写、测试、lint、文档/Skill/业务代码小步修改、Ledger/状态更新。 | Git 提交、联网、依赖安装、生产/密钥/部署/不可逆操作、高风险业务、计划外写入、验证失败。 |
| Wave Grant | 用户批准一组 Wave / Goal 的写入范围、验证矩阵和停止条件。 | Wave 内互不冲突的低风险 Atomic Task。 | 公共契约变更、跨 Wave 写入、高风险业务、Git/联网。 |
| CAD Grant | 用户批准一个原子任务的写入范围、验证命令、停止条件和失败恢复。 | CAD Red/Green/Review/Verify 内的本地低风险动作。 | Grant 外写入、测试持续失败、任务目标漂移、需要外部权限。 |
| 显式确认 | 高风险或超出默认策略的动作。 | 无。 | 必须等待用户、项目 owner 或专业确认。 |

Plan Grant / Grant 最小字段：

- 任务范围：Task ID、目标、有效期限。
- 写入范围：允许修改的目录、文件、测试和生成物。
- 验证范围：命令、人工验收、失败处理。
- 默认审批通道：是否允许当前会话的 Codex “替我审批”承接低风险工具审批；未开启时不得假定开启。
- Git 策略：是否允许 `git add` / `git commit`，不含 push、PR、merge 或部署；未说明时 Git 默认需要显式确认。
- 提交切片：按 Wave / Task ID 输出建议提交单元、包含文件、验证证据和建议 commit message；未授权 Git 时只建议不执行。
- Loop 预算：状态载体、反馈源、验证者、预算 / 时间盒、最大轮次、无进展检测和预算耗尽后的停止动作；缺失时不得进入自动循环。
- 失败回写：验证失败、需求不清、边界冲突、授权不足、连续无进展时分别回写 Spec / AC、产品上下文、OpenSpec、Grant 或 Goal Ledger。
- 外部访问：是否允许联网、安装依赖、启动服务、访问外部 API。
- 禁止事项：生产数据、密钥、真实支付/资金通道、不可逆操作。
- 停止条件：何时暂停、何时交还用户、何时回滚或转人工。

如果用户只说“继续”“按建议推进”“自动跑起来”，只能视为流程意向，最多进入计划内低风险执行候选。若用户明确说 `GSD + Goal 按任务计划推进`、`不希望每个任务手动授权`、`直接按照任务计划推进` 或等价表达，并且任务计划已经列明写入范围、验证命令、停止条件和显式确认边界，则可升级为 Plan Grant；之后范围内低风险任务不再因缺少逐任务 Execution Grant 停止。

### 6A. Codex 替我审批通道

当用户明确希望使用 Codex 的“替我审批”或当前会话已经处于自动审批模式时，知止者可以把它记录为授权策略中的审批通道：

```text
Codex 替我审批:
适用: 当前 Grant 范围内、低风险、可回滚、本地工作区动作
不适用: Git stage/commit/push/PR/merge、联网、安装依赖、读取密钥、生产数据、部署、数据库迁移、真实支付/资金、不可逆操作、高风险权限/租户/审计/合规变更
失败处理: 验证失败、范围漂移、用户改动冲突或风险升级时停止并交还用户
审计: 记录命令、文件、验证结果、失败证据和残余风险
```

Skill 只能识别和利用已经存在的审批模式，不负责打开或伪造该模式。若当前工具仍弹出审批，按工具实际状态处理；不要在文档里承诺一定自动通过。

### 6B. Plan Grant 计划授权

Plan Grant 是为了避免 GSD + Goal 每个任务都卡在 `Execution Grant：xxx`。它不是无条件授权，而是把授权锚定到已确认任务计划：

```text
Plan Grant:
触发语: GSD + Goal 按任务计划推进 / 按任务计划自动推进 / 不希望每个任务手动授权
适用 Goal:
任务计划: Wave / Task ID / 顺序 / owner
允许写入:
允许验证:
Git 策略: summary_only / commit_after_verified_task / explicit_confirm
提交切片:
Loop 预算: 状态载体 / 反馈源 / 验证者 / 最大轮次 / 无进展检测 / 预算耗尽处理
失败回写:
默认审批通道:
显式确认边界:
停止条件:
审计交接:
```

满足以下条件时，知止者和架构师应直接推进，不再要求用户逐任务确认 Execution Grant：

- 用户已明确表达按任务计划推进或默认授权意图。
- 任务计划内每个任务都有目标、非目标、写入范围、验证命令和停止条件。
- Plan Grant 已绑定 Loop 预算：状态载体、反馈源、验证者、预算 / 时间盒、最大轮次、无进展检测和失败回写位置清楚。
- 操作局限在当前工作区的低风险本地读写、测试、lint、文档更新或小步代码修改。
- Git 策略默认为 `summary_only`；若用户明确授权 `commit_after_verified_task`，每次提交必须对应已验证的 Wave / Task ID，先检查 `git status` / `git diff`，不混入用户已有改动，并使用非交互式提交说明。
- 不触发未授权 Git 提交、联网、依赖安装、生产、密钥、部署、数据库迁移、真实支付/资金、不可逆操作或高风险业务口径选择。
- 能区分用户已有改动和本轮改动，并能在验证失败时停止。

触发以下任一情况时，Plan Grant 失效并升级显式确认：计划外文件、公共契约破坏性变更、跨 Wave 扩张、验证失败且原因不清、用户改动冲突、工具要求额外审批、Git/联网/生产/密钥/部署/不可逆动作、高风险资金/权限/租户/审计/合规决策。

## 7. 交接给架构师

交接给 `资深架构师` 时，应形成一页式 `Engineering Handoff Card`；没有这张卡，不得把 GSD / Loop 候选直接写成 CAD 执行任务：

```text
Engineering Handoff Card:
当前状态: Round 0 / GSD Candidate / Wave Plan / Plan Grant Active / Loop Candidate / CAD Candidate / CAD Loop Active / Verified / Paused / Escalated / Closed
输入成熟度:
Goal ID:
Wave / Task ID:
状态载体:
是否需要 GSD:
GSD Round 0 缺口:
产品 / 系统 DNA 缺口:
建议 Wave:
Atomic Task 候选:
CAD 候选缺口:
写入范围:
只读范围:
验证命令:
反馈源:
验证者:
授权策略:
Execution Grant / 显式确认缺口:
Git 策略:
Loop 预算 / 最大轮次 / 无进展检测:
失败回写位置:
Superpowers 方法门禁:
质量/测试门禁:
代码库理解结论包:
事实边界:
下一步 owner:
停止条件:
提交切片:
路由:
```

路由写法：

- 需要工程侧大项目编排：交给 `senior-software-architect/references/ai-large-project-orchestration.md`。
- 需要单个任务 CAD 门禁：交给 `senior-software-architect/references/cad-mode.md`。
- 需要测试策略、TDD 或补测试：交给 `senior-software-architect/references/testing.md`。
- 产品语义仍不足：回到 `产品架构专家` 的产品上下文包或 PRD-Lite。

### 7A. 三卡到架构师的消费规则

`Engineering Handoff Card` 是工程执行交接卡，但它必须能追溯另外两张卡：

- 上游必须有 Product Context Card：业务目标、对象、规则、不变量、验收种子和待确认项清楚；缺失时回 `产品架构专家`，不得由架构师或 Agent 猜测业务事实。
- 当前必须有 Engineering Handoff Card：Goal、Wave/Task、写入范围、验证命令、授权策略、失败回写和停止条件清楚；缺失时停在知止者，不进入 CAD。
- 若要求 Loop、auto mode、后台 Agent 或持续推进，必须有 生产交付卡：状态载体、自动化心跳、隔离执行、Maker / Checker、反馈源、独立验证、预算、无进展检测、观测审计、人工接管和发布/回滚清楚；缺失时只标记 Loop Candidate。

消费规则：

- Product Context Card 只提供产品事实和验收种子，不授予写代码、改数据库、提交 Git 或发布上线。
- Engineering Handoff Card 只提供工程执行边界，不替代测试通过、CR 结论、Plan Grant / Execution Grant 或生产审批。
- 生产交付卡只提供循环治理边界，不替代人工 owner、发布/回滚批准或高风险动作显式确认。
- 架构师收到三卡后，先检查是否可消费；可消费才进入 OpenSpec、Harness、GSD 任务包、TDD、CAD 门禁、源码级 CR 或发布风险设计。

## 8. 质量 / 测试门禁联动

GSD/CAD 准入必须同时给出质量门禁位置：

- OpenSpec 规定测什么业务事实。
- Superpowers 方法门禁规定怎么高质量地做：TDD 切入、Review 输入、反馈处理和完成前验证证据。
- 产品专家提供验收种子和不可代码化的人工验收边界。
- 资深架构师设计测试分层、TDD 切入点、补测试和测试代码 CR。
- 本技能编排测试矩阵、验证顺序、CR 前置条件、失败回退和残余风险交接。

没有验证矩阵或测试结果交接路径时，不建议进入 CAD。

## 9. 反模式

- 把整个 Roadmap、GSD 计划或 Wave 清单当成 CAD 授权。
- 只因为项目大，就强制创建完整 GSD 文件体系。
- 只因为用户说“继续”“自动推进”或“替我审批”，就默认允许 Git、联网、部署、生产操作、依赖安装、读取密钥或不可逆操作。
- 把计划内低风险执行写成无条件自动通过，或让 Codex 替我审批绕过工具权限、sandbox、项目规则和用户授权。
- 把 AI 原型、MVP、PRD、产品上下文包或知止者准入结论当成 Execution Grant；知止者准入结论不是 Execution Grant。
- 把 Superpowers skills 当成 GSD 的默认插件安装、默认外部脚本、默认 worktree、默认 subagent 或默认 Git 操作。
- 把无根据猜测、模型脑补、工具总结、外部文章观点或超出用户目标的功能扩张写成 GSD Wave、Atomic Task、CAD 候选或实现建议。
- 让 AI 随机推进模拟模块、mock 流程、无业务入口 demo、空服务骨架或看上去可用的样子货，并把它当成 GSD 进展。
- 只检查页面能打开、接口能返回假数据或测试桩能跑通，却没有回链真实业务入口、验收种子、生产边界和发布/回滚条件。
- 把内存版业务 Service、Map/List 存储实现、Fake/Mock 服务或进程内状态当成生产实现；缓存、测试替身、fixture 和沙盒模拟必须隔离在对应边界内。
- 在知止者中复制 CAD 每轮 Pick / Red / Green / Review / Refactor / Verify / Record 细则。
- 让多个 Agent 同时写同一文件、同一公共契约、同一状态机或同一测试夹具。
