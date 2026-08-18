# 知止者与 Codex Skills

本仓库维护一组可安装、可验证、可组合、可持续演进的 Codex Skills。它不是 prompt 集，也不是角色接力系统：当前 Agent 始终对用户负责，专业 Skill 只是按需装载的能力包。

仓库把知止者设计为默认交互与责任模型，`$wise-agent` 是显式协同入口，但不表示每个任务都必须加载它。简单任务直接完成；单一领域且边界清楚的任务可直接加载对应专业 Skill；任务跨专业、跨阶段、跨轮，或需要状态恢复、独立验证和知识回流时，再由知止者持有完整目标。

## 项目定位

知止者不是流程路由器，而是统一智能行动主体：先读事实，再判断问题，装载最小能力，完成真实工作，用独立证据验证并归位结果。多 Skill 只为同一 Agent 补充专业上下文，不产生第二人格或重复 Owner；运行时只读取当前任务必要的 reference。

体系按“体、枢、用、证”归位：`AGENTS.md` 守体，`wise-agent` 持枢，专业 Skill 各安其用，fixtures、validator、测试与人工评审独立作证；上层只声明边界和路由，不复制下层说明书。

责任始终分为四层：

- **人类责任 Owner**：确认价值取舍、公共契约、高风险授权、发布和不可逆责任。
- **知止者**：理解目标、选择能力、保持状态、执行工作并综合最终交付。
- **专业能力**：项目 Skills、references、scripts 和工具，提供专项知识与动作。
- **独立 Checker**：测试、validator、人工评审或外部证据，负责证明而不是自证。

人类责任 Owner、知止者、专业能力和独立 Checker 分开；内部可以协作，最终责任不能混写。

运行时资产按职责归位：

| 位置 | 保存内容 |
| --- | --- |
| `AGENTS.md` | 每次会话都应遵守的仓库规则、安全边界和维护门禁 |
| `<skill>/SKILL.md` | Skill 的触发、定位、核心流程、场景路由和红线 |
| `<skill>/references/` | 详细知识、模板、清单、证据和复杂分支 |
| `<skill>/scripts/` | 确定性生成、解析、校验和状态检查 |
| `fixtures/`、`<skill>/fixtures/` | 触发正负例、行为契约和可执行回归样例 |
| `<skill>/agents/openai.yaml` | Codex 展示信息、默认调用提示和隐式触发策略 |

## 用户使用指南

**适用对象**：希望让 Codex 完成分析、设计、实现、评审、文档或 Skill 维护任务的使用者；不要求预先理解 Skill、项目执行规范、Loop 或 Checker。

**前置条件**：已在 Codex 中打开任务材料或项目目录；需要使用本仓库能力但尚未安装时，先按[安装](#安装)操作。只读问答可以直接开始；普通且边界清楚的修改请求本身允许在目标范围内写入，联网、安装、Git、同步、部署等外部或高风险动作仍需明确授权。

### 1. 30 秒上手

日常不需要选角色或背 Skill 名称。最短指令只要说清楚“想得到什么”和“材料在哪里”；修改边界重要时补充写入范围，需要外部或高风险动作时再明确授权。下面的通用任务模板按需填写，不确定的项可以省略，不要为了填满模板补造信息：

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；
请读取 <材料或路径>；只处理 <范围>，不做 <非目标>；
需要时允许 <联网 / 安装 / Git / 同步 / 部署等外部动作>；
用 <检查命令 / 评审证据 / 验收标准> 证明完成。
信息足够就直接推进，只在关键决策或高风险授权处问我。
```

三个常用层级：

- 只要判断：`读取 <材料或路径>，回答 <问题>；只读，不改文件。`
- 需要交付：`基于 <材料或路径> 完成 <产物>，只改 <路径>，用 <标准或命令> 验证。`
- 需要外部动作：在上一句后明确增加 `允许 <联网 / 安装 / Git / 同步 / 部署等具体动作>`；没有这句时，Agent 不应自行扩大权限。

任务明显跨专业、跨阶段、跨轮，或你希望 Agent 自己判断并推进、持续保持目标和状态时，再在前面加 `$wise-agent：`。单一专业任务可直接点名对应 Skill；不确定时只描述任务，不要先设计角色接力。

### 常见任务与友好指令

常见任务可以直接这样说：

| 任务 | 友好指令 |
| --- | --- |
| 自主推进 | `$wise-agent：读取当前项目事实，自己判断并推进；只在关键决策或高风险授权处问我，完成后给出产物、验证和残余风险。` |
| 长任务执行规范 | `$wise-agent：把这项跨轮工作落入项目已有 OpenSpec / Spec / Issue / 任务计划，不创建运行时 Goal；一次只推进一个当前切片，记录验证证据、停止条件和下一入口。` |
| 双边契约会商 | `$wise-agent：协调 <消费者任务> 与 <提供方任务>，先确认讨论主题并充分交换事实、证据和缺口；信息充分后再围绕 <公共契约> 做版本化会商、双边对账和独立验证。` |
| 主持式多方会商 | `$wise-agent：协调 <任务列表> 围绕 <共享决策> 进入主持式多方会商；先确认主题和信息覆盖，充分交换后再独立形成立场、归并冲突、形成决议并交 Checker。` |
| 需求讨论 | `先做能力归位：判断这个需求是在使用、增强、组合还是新增哪项稳定能力；默认审视不等于默认展开。` |
| 产品设计 | `根据 <访谈/需求/原型> 写一版可评审 PRD；先提炼稳定能力、共性和有证据的特殊性，再展开场景、流程、规则和验收。` |
| 创见探索 | `$wise-agent：结合华夏经世智慧处理这个原创/非标设想；先保留原始意图和挑战的默认前提，再做最小可逆实验；不要以主流/文献数量单独否决，也不要把新颖直接当成正确。` |
| 小说构思、正文或单次评审 | `$novelist：通读 <当前稿件/必要上下文>，完成 <构思/正文/重写/评审>；区分权威稿、旧稿、创作候选和待确认，只在影响方向的主分叉处问我。` |
| 跨轮长篇小说 | `$wise-agent：以 novelist 为故事主能力持续推进 <作品>；维护权威稿、设定状态、未决分叉和后续回收，跨轮恢复时先对账，不把旧稿或候选自动写成正典。` |
| 创作设定集 | `$document-authoring：把作者或 novelist 已确认的设定整理成人物档案、时间线、世界规则和伏笔台账；保留授权范围、逐项状态与权威指针，不续写剧情，完成后交 novelist 做语义复核。` |
| 创作用字考据 | `$hanzi-philology：只核验 <人物名/地名/称号/古语> 的形音义、时代语感、文本证据和误读风险；不测吉凶，不替作者决定是否采用。` |
| 小说发布适配 | `$novelist：面向 <法域/平台/载体/受众> 核验当前生效规则，保留可恢复母稿并另建发布适配稿；区分官方规则、平台规则和专项行动，不承诺绝对合规。` |
| UI 设计 / 可用性 CR | `$ui-design-expert：基于 <需求/页面/源码/截图> 设计或评审 Web 界面，输出信息架构、交互状态、响应式、可访问性和验证证据；需要时比较设计系统、UI 库或东方视觉方向；已有 Figma 定稿只做还原时直接走工程实现。` |
| UI 可用性验证 / Design QA | `$ui-design-expert：按证据等级验证 <目标用户与关键任务>；设计契约或截图只作 E1 静态评审，可操作原型作 E2，真实实现作 E3 Design QA，目标用户测试或运行观测才作 E4；不得跨等级声称完成。` |
| 跨层安全设计 / 评审 | `$security-engineering-expert：基于 <业务/架构/协议/代码/运行证据> 评审 <范围>；从资产与资损、主体与信任边界、威胁和滥用路径出发，形成预防、检测、响应、恢复控制、验证证据与残余风险结论。` |
| 资金安全专项 | `$security-engineering-expert：消费已确认的支付对象与资金责任，评审 <交易/提现/退款/结算链路> 的账户接管、内部滥用、权限串用、指令冲突、回调重放、异常放款、监测止损和恢复证据；不改写支付语义。` |
| 系分设计 | `基于 <产品文档> 和 <源码/接口/DDL> 编写系分；先说明能力归位、共同对象与不变量，有真实变化轴才拆模块、策略或适配器。` |
| 只读 CR | `我有 PRD 和代码路径，只做只读 CR，不改代码；请给出源码证据、严重级别、测试缺口和残余风险。` |
| 工程交付 | `基于 <PRD/系分/源码> 完成 <Bug/TDD/重构/代码>，写入范围是 <路径>，验证命令是 <命令>。` |
| 快速编码 | `这是简单、确定的局部修改；请先连续完成最小实现，测试和 CR 最后集中补，不展开完整 SDLC。写入范围是 <路径>，最终验证是 <命令>。` |
| 多轮工程执行 | `这个原子任务的决策已经冻结，请按受控工程执行 Loop 连续推进；状态写入 <位置>，反馈来自 <来源>，验证者是 <Checker>，写入范围是 <路径>，验证是 <命令>，最多 <N> 轮，连续两轮无进展就停止；<Plan Grant 已覆盖当前任务 / 本任务 Execution Grant 已确认>。` |
| 决策盘问 | `使用 $grill-me 盘一下这个方案：先查历史问题和项目事实，一次只问一个主 blocker，记录每个问题和结论。` |
| 经世决策 | `使用 $huaxia-practical-wisdom：基于现实事实校准取舍，给出最小行动、止损和验证，不要只讲古语。` |
| 发布准入 | `做生产交付审查：只判断 Ready / Not Ready / Human Approval Required，列证据、回退、人工确认点和停止条件。` |
| 知识回流 | `进入知识回流视图：把这轮 CR 结论沉淀到项目约规或知识库；按业务域/模块和稳定/时效/任务知识归位。` |
| 项目约规 | `初始化/更新项目 AGENTS.md：读取当前技术栈和已有规则，只做最小项目约规 patch。` |
| 提交并推送 | `提交并推送当前分支：先检查工作区和验证证据，只暂存本轮文件；提交后核对提交范围，再推送当前分支。` |
| 同步 Skill 安装态 | `允许把 <Skill 列表> 同步到 <CODEX_HOME>；先 dry-run，确认目标和备份目录后正式同步，再校验安装一致性；不要执行 Git 提交或推送。` |

普通小说任务不需要默认加 `$wise-agent`：单次构思、正文、重写或评审直接调用 `$novelist`；跨轮、多稿权威、状态恢复或需要组合文档与考据能力时，再由 `$wise-agent` 持有目标和状态。`huaxia-practical-wisdom` 是小说家的必要叙事校准依赖，用户无需另行点名；`document-authoring` 和 `hanzi-philology` 只在对应交付物或证据问题实际出现时加载。

### 多任务会商怎么触发

最可靠的触发方式是使用 `$wise-agent`，同时写清参与任务、各自权威、共同议题和执行意图。具体协议以 [context-handoff.md](./wise-agent/references/context-handoff.md) 为准：

项目内跨模块定位与边界讨论可简写为：`$wise-agent 模块合议：<项目或边界议题>`。

- 两方优先使用双边契约会商，适合消费者与提供方围绕公共契约做版本对账。
- 三个及以上独立权威只有必须裁定同一共享决策，且不能拆成独立双边议题时，才进入多方会商。
- 双边和多方都先确认讨论主题并交换事实、证据、假设、未知项和依赖；信息不足时先补证据，不进入观点讨论或决策。
- 输入可冻结、写入不重叠的独立任务直接走 Worker 并行后汇合，不需要开会。

仅设计协作协议时可以这样说：

```text
$wise-agent：请为以下任务设计多方会商，但不要向其他任务发送消息。
参与任务与权威：<任务 A：...；任务 B：...；任务 C：...>
共享决策：<待共同裁定的问题>。
请先判断是否能拆成双边会商或 Worker；确需会商时，先确认主题和信息是否充分，再给出版本、冲突裁决、Checker 和停止条件。
```

需要实际推进时，提供可识别的任务名称或任务 ID，并明确要求执行：

```text
$wise-agent：请协调以下现有任务围绕 <共享决策> 进入主持式多方会商。
参与任务与权威：<任务名称或任务 ID + 各自权威>。
请实际向这些任务发送消息并推进，由当前任务先对齐主题、交换信息并确认信息充分，再主持形成版本化决议、交独立 Checker，并在停止条件满足后退场。
```

“协调现有任务”不会自动授权创建新任务；需要新建时应明确说明允许创建哪些任务。联网、Git、同步、部署、生产和其他高风险动作仍分别授权，不因进入会商而自动获得权限。

### 验收与继续推进

#### 怎样判断已经完成

一次可信的交付至少能回答四个问题：

1. **产物是什么**：给出真实文件、代码、图、提交或明确结论，而不是只给计划或操作过程。
2. **如何证明**：列出实际执行的测试、validator、回读、人工评审或运行证据及其结果。
3. **还有什么没证明**：区分未覆盖范围、残余风险和仍需 Owner 决策的事项。
4. **下一步由谁负责**：只有仍有动作时才说明下一 Owner；已经闭环时不制造额外流程。

结构检查、测试数量、Agent 自述、页面能打开或“已经部署”都不能单独证明真实可用。你可以直接追问：`请只列真实产物、验证证据、未验证项和残余风险。`

#### Agent 停下时怎么继续

| 停止原因 | 你需要补什么 | 可直接回复 |
| --- | --- | --- |
| 缺少可查事实 | 文件、日志、页面、接口、数据或权威结论 | `材料在 <路径/链接>，按原范围继续。` |
| 存在价值或契约分叉 | 明确选择、优先级、非目标或可接受取舍 | `选择 <方案>；不做 <范围>，按这个结论推进。` |
| 缺少高风险授权 | 具体动作、目标和边界，不给泛化权限 | `允许执行 <Git/联网/安装/同步等动作>，仅限 <目标>。` |
| 验证失败 | 是否允许在原范围继续修复，以及停止条件 | `在原写入范围继续修复并复测；若 <条件> 仍失败就停止报告。` |
| 外部条件暂不可用 | 等待条件、替代证据或下一 Owner | `先交付当前可验证部分，把 <缺口> 标为待 <Owner/环境> 处理。` |

### 进阶使用

#### 默认能力视角

所有需求讨论和设计都先做能力归位，判断是在使用、增强、组合还是新增哪项稳定能力。默认审视不等于默认展开：

- Bug、文案调整、局部字段、一次性迁移等局部需求，只说明影响的既有能力并走最小实现，不展开能力地图。
- 出现多场景、多主体、跨渠道、跨模块、存在生命周期或真实变化轴等证据时，再提炼共同目标、对象、不变量和契约，把差异承载到规则、参数、策略或适配边界，并用代表性场景验证能力边界。

不需要每次复述完整方法，直接说：`先做能力归位，默认审视、按证据展开；局部需求最小实现，多场景再提炼共性、特殊性和变化轴。`

#### 快速编码怎么用

简单任务、确定性高的场景和小范围代码调整会默认走快速编码：先读相关源码、调用方、测试和项目约规，连续完成最小实现，再集中补测试、验证和 CR。你也可以说：`快速改这个方法，先完成实现，测试最后统一补；只改 <路径>，最终运行 <命令>。`

“仅编码”只表示当前阶段编码先行，不表示永久跳过测试。代码写完但验证尚未完成时，只能视为“实现已完成，测试与验证待补”；涉及公共契约、数据库、资金、权限、租户、安全、生产操作、新依赖或跨模块调整时不会默认走快速路径。

`CAD` 现在只作为内部文件路由标识，不需要用户选择。简单局部任务走快速编码，普通一次性交付走标准工程流程；只有单个当前切片已选定、关键决策冻结，状态载体、反馈源、验证者、写入与验证边界、预算、停止条件和适用授权齐备，且明显需要多轮反馈时，才进入受控工程执行 Loop。适用授权是覆盖当前任务的 Plan Grant，或单任务 Execution Grant；不要求重复授权，也不新增状态或授权类型。项目执行规范只保存跨轮承重事实，切片内部由 Agent 选择最短可验证路径。

需要让所有仓库默认继承知止者的最小行动原则时，可在明确授权后，把[全局行动内核](./wise-agent/assets/codex-global-agents.md)合并到 `$CODEX_HOME/AGENTS.md`。它不会强制每轮加载完整 `$wise-agent`；已有规则不得直接覆盖。

### 2. 任务与专业能力

下表用于确认边界，不是使用前必须选择的菜单。产品、架构、文档、考据、生成和约规不是平级角色，它们是知止者按需使用的专业能力。

| 你要交付 | 专业能力与路径 | 最小输入 | 边界 |
| --- | --- | --- | --- |
| 跨领域真实工作、目标控制、能力组合、验证和知识演进 | 知止者，ID：`wise-agent`，路径：[wise-agent](./wise-agent) | 目标、事实源、范围、授权、完成证据 | 不限于产研；不获得无限自治或高风险授权 |
| 产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图 | 产品架构专家，ID：`product-architecture-expert`，路径：[product-architecture-expert](./product-architecture-expert) | 用户、主体、目标、材料、范围、验收 | 不负责工程实现、代码 Review 和生产排障 |
| 支付、资金账户、支付账本、清结算、对账、原支付退款、通道、卡组织、ACH、VCC、跨境和支付监管产品规则 | 支付专家，ID：`payment-expert`，路径：[payment-expert](./payment-expert)；本机安装已授权，`R-002` 禁止 Git push、团队共享/同步与公开发布 | 主体、法域、资金归属、原事实、轨道/通道、规则来源、验收 Owner | 不替代法务合规、会计政策、工程实现或生产准入 |
| 支付资金方案、实现证据或测试结果的独立准出审查 | 候选支付资金审查，ID：`payment-funds-review`，路径：[payment-funds-review](./payment-funds-review)；`PFR-001` 关闭前不可安装、同步、团队共享或公开发布 | 原始方案或实现证据、资金事实、来源引用、失败快照、验收 Owner | 只作独立 Checker；不定义产品路线，不做源码实现或修复，不替代专业审批 |
| Web UI 或浏览器应用界面、信息架构、任务流、界面状态、响应式、视觉系统和可用性评审 | UI 设计专家，ID：`ui-design-expert`，路径：[ui-design-expert](./ui-design-expert) | 用户任务、产品事实、真实内容、现有设计、平台约束 | 不负责定义产品业务语义或替代工程实现；原生 iOS/Android 走平台能力，已有 Figma 还原代码走工程能力 |
| 业务、资金、身份权限、数据、通信协议、软件供应链、系统架构与运行事件的安全设计、评审和准出 | 安全工程专家，ID：`security-engineering-expert`，路径：[security-engineering-expert](./security-engineering-expert) | 目标环境、资产与资损、主体、真实流程、信任边界、现有控制、证据与风险 Owner | 不替代产品/支付事实、代码实现、精确的 `codex-security:*` 能力、法律合规判断或生产授权 |
| 系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图 | 资深架构师，ID：`senior-software-architect`，路径：[senior-software-architect](./senior-software-architect) | 路径、目标或现象、约束、验证命令、写入授权 | 不替代产品专家定义复杂业务语义、PRD 和金融产品规则 |
| 实际代码写入，Karpathy Guidelines，或 AI 生成计划 / diff 的隐藏假设、过度设计、范围漂移、无关清理与弱验证专项审查 | LLM 编码卫生，ID：`llm-coding-hygiene`，路径：[llm-coding-hygiene](./llm-coding-hygiene) | 用户目标、计划或 diff、相关源码与测试、成功标准 | 实际代码写入时默认生效，但只作静默护栏，不替代工程实现、TDD、源码 CR 或项目编码约规 |
| 短篇小说、长篇小说、连载小说、世界观、人物弧光、故事/卷/章设计、正文、重写和连续性审查 | 小说家，ID：`novelist`，路径：[novelist](./novelist) | 类型承诺、当前创作单元、稿件权威、设定状态、允许改变范围、作者验收 | 以华夏经世智慧校准人情事势；不把旧稿、考据结论或创作候选自动升级为正典 |
| 正式报告、制度、手册、研究说明、创作设定集、文档审校、DOCX/PDF | `document-authoring`，路径：[document-authoring](./document-authoring) | 读者、用途、事实源、载体、验收方 | 不改变产品、工程、小说、法律、合规或考据结论，不负责小说正文 |
| 教程、视频、代码、文档、规范和产物到可复用能力候选 | 资源炼技，ID：`resource-capability-distiller`，路径：[resource-capability-distiller](./resource-capability-distiller) | 可读取材料、复用目标、目标环境、许可与验收方式 | 先提炼能力单元并逐项归位；不默认创建新 Skill，不自动安装、同步、提交或晋升 |
| 汉字学、训诂、字源、甲骨文、金文、小篆、通假、异体及创作名称的时代语感证据 | `hanzi-philology`，路径：[hanzi-philology](./hanzi-philology) | 对象、时代、文本范围、材料、结论等级 | 《说文解字》只是证据之一；不测字吉凶、不替作者起名、不负责普通工程命名 |
| 华夏经典视角下的现实决策、组织协作、长期成长和行动取舍 | 华夏经世智慧，ID：`huaxia-practical-wisdom`，路径：[huaxia-practical-wisdom](./huaxia-practical-wisdom) | 事实、目标、约束、主体、时限、最坏损失 | 不作医学诊疗、占卜命理或古籍训诂，不替代专业结论 |
| 方案、计划或设计的关键分叉、历史去重和决策快照 | `grill-me`，路径：[grill-me](./grill-me) | 方案、材料、历史决策、Owner、风险边界 | 未达到 shared understanding 不执行；自决不扩大授权 |
| DDL/schema/Java 类/字段表格到 Java Service 脚手架 | `java-service-code-generator`，路径：[java-service-code-generator](./java-service-code-generator) | 结构化输入、表名、模块、输出目录、覆盖授权 | 不从纯自然语言直接生成生产代码；生成后仍要编译、测试和源码 CR |
| Java 项目通用编码约规，或按依赖/上下文启用 Wind 专项 | `wind-coding-conventions`，路径：[wind-coding-conventions](./wind-coding-conventions) | Java 源码证据、依赖/包名、规则问题 | 只做规则判断和偏差说明；源码设计、CR、TDD、修复和验证由架构师主责 |

没有 Wind 高置信度信号时不加载 Wind face/impl、API 或模型专项；Wind 项目按实际依赖和上下文补专项入口。普通 Java 源码 CR 由架构师主责，并消费通用 Java 约规。

图形化交付按语义归属：业务架构定能力与投资，产品架构定产品语义，支付资金图先由支付专家稳定资金事实，系统架构定工程结构，技术架构定实现支撑；详细路由以 [capability-routing.md](./wise-agent/references/capability-routing.md) 为准。产品流程、状态和验收视图由产品专家负责，支付四流、账务与清结算语义由支付专家负责，系统模块、接口时序、部署和实现状态由架构师负责。只说“架构图”且材料不足以判断类型时，先确认它用于业务投资、产品语义、支付资金事实、系统结构还是技术实现决策。复杂可编辑架构图、代码库结构转图或架构描述转图，应先稳定语义，再按需调用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。

常见组合仍只保留一个最终 Owner：

- 从 AI 原型到工程化：产品专家稳定对象、流程、规则和验收，架构师完成系分、TDD、源码 CR 和生产验证，知止者持有跨阶段目标。
- 从 AI 编码计划到工程交付：知止者只在跨阶段时持有目标、状态与授权；实际代码写入默认装载 LLM 编码卫生，静默约束假设、简化、范围和成功证据；架构师持有实现、TDD、源码 CR 与生产风险。
- 从支付产品到工程化：支付专家稳定资金事实、支付不变量、外部规则边界和验收种子，架构师完成系统设计、代码、测试和生产证据，知止者只在跨阶段或跨轮时持有项目执行规范与 Checker。
- 从产品事实到可用界面：产品专家稳定业务语义和验收口径，UI 设计专家形成信息架构、交互状态、视觉与可用性契约，架构师实现并验证；Figma 能力只负责工具内执行或既有设计到代码。
- 材料包含访谈、工单、竞品、路线图、PRD、发布复盘或提到 `pm-skills` 时，知止者装载产品判断动作链，形成产品上下文包并继续持有后续目标、验证和停止条件。
- 从训诂考据到正式报告：`hanzi-philology` 先形成证据卡，`document-authoring` 只负责成文与载体，不改变证据等级。
- 从小说创见到长篇交付：`novelist` 持有故事与正文，以 `huaxia-practical-wisdom` 校准人情事势；确有字词证据问题时调用 `hanzi-philology`，设定稳定且需要权威整理或正式载体时调用 `document-authoring`。
- 从普通图到复杂图：先由产品专家或架构师稳定语义，再决定是否使用专用出图能力。
- 官方 Superpowers 插件只补 brainstorming、TDD、调试、CR、验证等方法缺口，不替代产品或工程主能力，也不扩大 Git、worktree、subagent 或安装授权。

专项使用细节、状态契约和校验命令以对应 Skill 的 `SKILL.md`、reference 与 script 为准；README 只保留用户入口和职责边界，不复制专业说明书。

### 3. 知止者如何工作

加载 `$wise-agent` 时，知止者按 **察 -> 辨 -> 谋 -> 行 -> 验 -> 化** 推进：读取一手事实，区分事实/推断/待确认，选择最小能力和路径，完成实际工作，独立验证，再把状态、决策和经验归位。它不是不行动，而是让行动有方向、有分寸、有收口。

复杂问题按“阴阳一体、互用互制”校准：阴是目标、事实、边界、权限、证据和止损，阳是假设、取舍、行动、反馈和交付；两者在同一行动主体和任务单元中互相成就、互相约束，不拆成两个 Agent 或并列模式。简单任务直接完成，不强制输出双面卡。可直接说：`$wise-agent：按阴阳一体、互用互制处理这个问题，同时给出约束面、推进面、最小动作和验证证据。`

简单任务直接完成；复杂任务才使用计划、SDLC、项目执行规范、Loop、Worker 或 Checker。专业能力按需渐进加载，无论内部用了多少能力，对用户只形成一个综合结论。

四类场景视图只用于强调当前边界，不是并列流程：

- **只读理解视图**：核验材料、源码、测试和日志；默认不写文件、不联网、不安装。
- **交付推进视图**：产出真实 PRD、系分、代码、测试、图或知识资产。
- **验证发布视图**：用原始证据做质量门禁、源码质量评审或生产交付审查。
- **知识回流视图**：把已验证经验归位到项目上下文、知识库、ADR、约规、fixture 或脚本。

常用短句：`进入知止者`、`进入只读理解视图`、`做质量门禁`、`做源码质量评审`、`做生产交付审查`、`进入知识回流视图`。

#### 3.1 什么时候启用 SDLC、项目执行规范、Loop、Worker、Checker

五者不是固定流水线。默认直接完成，再按真实证据增加控制：

| 机制 | 何时启用 | 不该启用 | 友好指令 |
| --- | --- | --- | --- |
| SDLC | 跨产品、设计、工程、验证、发布或运行阶段，需要阶段门禁和交接 | 单阶段或一步任务 | `按完整 SDLC 覆盖这个需求到发布，但只展开当前需要的阶段。` |
| 项目执行规范 | 跨会话、跨 Wave，需要保存成功标准、状态、预算和停止线 | 当前会话能闭环 | `为这项工作建立项目执行规范并持续推进，成功标准是 <...>，停止条件是 <...>。` |
| Loop | 同一项目执行规范需要反复执行、观察和验证，且有状态载体与轮次边界 | 一次执行即可完成 | `允许进入 Loop，最多 <N> 轮；连续 <N> 轮无进展就停止。` |
| Worker | 子任务输入可冻结、写入不重叠、低耦合，并行收益明确 | 同一文件、强耦合调用链 | `这些子任务互不依赖，可并行时再派 Worker；共享文件串行。` |
| Checker | 高风险、公共契约、重要交付、发布准出或需要独立 CR | 低风险任务已有回读或测试 | `增加独立 Checker，直接读取原始产物和证据，不只审 Maker 摘要。` |

SDLC 是阶段地图，项目执行规范是跨轮目标契约，Loop 是反复执行契约，Worker 是执行拓扑，Checker 是独立验证机制。Worker 与 Checker 不是顺序阶段，可以只用 Checker 而不派 Worker。

##### 3.1.1 复杂工作图怎么用

工作拓扑投影不是新的 `Graph Mode`，也不是另一份任务真相源。简单、线性、单文件或一次可完成的任务直接执行；只有两项同时满足，才在现有 执行状态契约中附加 `work_graph`：上下文隔离、并行、专业化交接或断点恢复有明确收益；至少三个节点存在分支、汇合、并行或跨 Wave 交接。

用户不需要手写节点字段、迁移规则或检查命令，直接说明为什么需要工作图、写入边界和完成证据：

```text
$wise-agent：这个 项目执行规范 存在 <分支 / 汇合 / 并行 / 跨 Wave>，
请基于现有 项目执行规范 投影可校验的 work_graph。
保持现有写入和执行授权，高风险节点增加独立 Checker；
不要创建第二份真相源，结构校验通过也不能替代真实任务证据。
```

节点字段、数据交接、条件路由、失败策略、迁移和 validator 规则以 [delivery-execution-control.md](./wise-agent/references/delivery-execution-control.md) 为唯一权威；README 只保留使用入口。

决策寻路也不是第六个控制机制。只有目标大致明确，但路线仍模糊、超过一次会话且无法可靠形成 Spec 或计划时才启用；此时只维护决策地图，不要生成 Spec、计划或执行任务。路线清楚时直接跳过。

#### 3.2 决策澄清与 Grill Me

决策澄清门禁只处理真正未决的 Decisions。Facts 先从材料、源码、测试或日志自答，Decisions 才问 owner；复杂或模糊任务一次只问一个主 blocker。每轮结果只有：`自决推进 / 询问 owner / 继续收敛 / 停止交接`。

`grill-me` 是升级盘问，不是每个任务的必经流程：

- 关键分叉未决、回答含糊、连续返工，或下一步会改变公共契约、状态机、验收和风险时触发。
- 每次提问前先读问题台账、决策快照、文档、代码、测试和知识库；已确认或已排除的问题不得换个说法重问。
- 可查 Facts、已有 Owner 结论和低风险可逆默认项由 Agent 自答并留痕；新价值取舍、公共契约、高风险和红线交给 Owner。
- 高保真问题先交给原型、真实页面、可执行样例或观测取证，再回到原问题裁决；不凭语言断言使用体验，也不把取证交接当 Owner 决策。
- 范围过大时按独立决策包交接，每包保留范围、Owner、输入快照、证据媒介、写回位置和停止条件；只有包之间没有共享决策、红线或写回位置时才并行。
- 你只需要回答接受建议、改答案、补材料或停止；说“按你建议推进”只关闭当前 blocker。
- 退出：确认 shared understanding，形成决策快照；未确认前不执行。
- 红线、底线、不能碰、不可、禁止、必须等表达必须记录，执行前逐项对账。

#### 3.3 知识、上下文与学习回流

知识回流不是把任务总结整篇复制进知识库。先确认结论已被材料、源码、测试、日志或 Owner 验证，再按业务域或模块找到已有权威位置；没有权威位置或写入授权时，只给候选落点。

| 类型 | 适合保存 | 要求 |
| --- | --- | --- |
| 稳定知识 | 概念、责任边界、核心流程、长期不变量、证据规则 | 进入项目约规、领域知识库或 ADR；变更时清除旧值并说明影响 |
| 时效知识 | 工具版本、平台限制、外部规范、近期策略 | 记录来源、核验日期、适用范围和复核条件 |
| 任务知识 | 本轮材料、计划、验证、临时判断、待确认项 | 默认留在 Issue、项目执行规范、评审或任务记录，验证后再晋升 |

需要把上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀变成可维护资产时，可说 `进入知识生产`；产物必须形成可检索、可更新、可验证的上下文资产，而不是一次性长文。

开启学习回流模式后，只会把当前任务中已脱敏、可复核、命中门禁的经验记录为 `candidate`；候选不会成为运行时指令，也不会触发历史扫描、自动确认、改 Skill、提交或同步：

```bash
python3 ~/.codex/skills/wise-agent/scripts/skill-learning-ledger.py enable
python3 ~/.codex/skills/wise-agent/scripts/skill-learning-ledger.py status
python3 ~/.codex/skills/wise-agent/scripts/skill-learning-ledger.py disable
```

`candidate` 只是待审证据，不代表 Skill 已改进。Owner 确认复用范围、目标 Skill 和权威落点后，人工评审结论为 `confirmed`，candidate 账本文件仍保持 `candidate`；受控试验在该状态内执行，不新增 `RSI Mode` 或其他生命周期状态。独立 Checker 复核后，由 Owner 作 `promote / reject / supersede` 裁决并留在任务证据中。学习模式只控制 candidate 账本写入；Skill 源仓库修改、Git、同步和发布分别需要对应授权。

知止者使用观测与学习候选账本相互独立。只有用户显式授权后才在本地启用 metadata-only 记录；脚本不修改 Codex 配置，先打印候选配置供人工审查：

```bash
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py enable
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py config
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py serve
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py status
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py report
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py disable
```

默认目录为 `~/.skill-usage/wise-agent`，只保存事件和资源标识、token 遥测或静态估算，不保存 prompt、回答或源码正文。确定性事件 ID 用于拦截 Hook / OTLP 重放；`status` 会分开报告写入开关与本地接收器健康。Hook 信任、修改 `~/.codex/config.toml`、启动接收器和真实试点仍需分别授权；完成真实试点前状态为 `PILOT_PENDING`。

需要跨任务保留已确认的沟通、工作流或证据偏好时，可另行显式开启“用户协作档案”。它默认关闭，不扫描历史对话，和 Skill 学习回流完全隔离；新记录先进入 candidate，candidate 不会生效，只有用户确认后才可读取。当前指令始终优先，档案也不能授予 Git、联网、安装、部署、生产或删除权限：

```bash
python3 ~/.codex/skills/wise-agent/scripts/user-context-ledger.py enable
python3 ~/.codex/skills/wise-agent/scripts/user-context-ledger.py status
python3 ~/.codex/skills/wise-agent/scripts/user-context-ledger.py record --category communication --scope global --statement '默认使用中文并先给结论' --evidence-kind direct-user --evidence-ref task:current
python3 ~/.codex/skills/wise-agent/scripts/user-context-ledger.py confirm UC-0001 --confirmation-ref user:current
python3 ~/.codex/skills/wise-agent/scripts/user-context-ledger.py resolve --scope global
python3 ~/.codex/skills/wise-agent/scripts/user-context-ledger.py disable
```

查看、拒绝、替代、导出与清除使用 `list / reject / supersede / export / purge`；其中 `purge` 需要明确确认口令，并会清空协作数据、停用档案但保留权限收紧的空壳目录。未显式执行 `enable` 和 `record` 时，知止者不会为用户创建任何本地档案。

遇到“更专业”“更有感染力”等主观要求时，可直接给出本次任务级价值判断：`期望效果 / 正向参照 / 不期望效果 / 可接受取舍 / 最终 Owner`。它只约束当前交付，不会把一次措辞偏好写成长期 Skill 规则。

### 4. 编写文档的友好指令

产品、系分、重构三类正式设计文档各有一个权威模板入口：产品设计用 `product-prd-template.md`，系分设计用 `system-analysis-template.md`，迁移型重构用 `refactoring-design-template.md`。不需要记路径，直接说明材料、文档类型、读者、目标文件和验收要求：

- `基于 <需求或材料路径> 编写可评审产品设计，保存到 <目标路径>；先做能力归位，多场景才提炼共性、特殊性和变化轴；正文按背景、目标、定性、概要、详细设计、流程、规则和产品接口抽象展开，验收摘要放在最后。`
- `基于 <产品文档> 和 <源码/接口/DDL> 编写系分，保存到 <目标路径>；先说明能力归位、共同对象、不变量和真实变化轴，再讲背景、目标、定性、概要、详细设计、流程、业务规则、接口抽象、数据与风险。`
- `为 <产品设计/系分> 另建执行计划，承接详细验收矩阵、AC 与测试映射、验证命令、执行 owner、任务状态、发布和回滚；不要把这些控制字段铺进正式正文。`
- `基于 <现状证据> 判断是否需要独立重构设计；需要时输出可验证、可暂停、可回退的 MIG 切片。`
- `只评审 <文档路径>，不要改文件；列出必改项、待确认项、证据缺口和能否进入下一阶段。`
- `更新 <既有文档路径>，保持文件名和已确认结论；只补本轮变化。`
- `把 <权威 Markdown> 整理成 <DOCX/PDF>；不改变产品或工程语义，并检查目录、分页、表格、图片和中文字体。`

已有正式文档默认原路径更新，不因模板升级另建“新版”“最终版”或日期副本。正式 PRD、系分、ADR 和 OpenSpec/SDD 只保留当前结论；讨论过程进入评审报告、Decision Log、项目执行规范 或任务记录。

### 5. 边界与授权

- 不要先设计一套角色接力再描述任务，也不要让多个专业 Skill 分别向用户作最终承诺。
- 不要把工具、模板、目标、计划或授权机制名当主流程；先看交付物、风险和证据。
- 不交付模拟模块、无业务入口 demo、内存版业务 Service 或看上去可用的样子货。
- 不绕过事实、测试、源码、日志、项目规则和人工审批，不把计划、测试数量或 Agent 自述写成完成。
- 外部 Skill、工具、联网、安装、覆盖文件、Git、同步、生产数据、密钥、部署、删除或不可逆操作，必须先完成安全审查并取得对应授权。

## 安装

```bash
git clone https://github.com/fengwuxp/skills.git
cd skills
./sync-skills.sh --dry-run all
./sync-skills.sh all
scripts/validate-installed-skills.sh
```

同步单个无依赖 Skill 使用 `./sync-skills.sh document-authoring`；非默认目录使用 `CODEX_HOME=/path/to/codex-home`。有 `admission.json.requires` 的 Skill 必须在同一命令中先列依赖、再列调用方；`all` 会按准入和依赖闭包选择安全批次。同步使用 `rsync --delete`，会先备份已有安装，并按替代关系退役 `wind-project-coding-conventions`、`delivery-collab` 和 `huaxia-wisdom`。完成后重启 Codex 或开启新会话。

## 验证与同步安全

修改 Skill、reference、script、fixture 或 README 后运行：

```bash
./scripts/validate.sh
git diff --check
./sync-skills.sh --dry-run all
```

正式同步后运行 `scripts/validate-installed-skills.sh`。`--dry-run` 不写安装目录；正式同步需要对应授权，备份保存在 `$CODEX_HOME/skills/.backups/`。

`scripts/evaluate-skills.py` 只做离线静态预检，不能替代真实 Agent 行为。默认检查项目目录；需要核对指定目录时，显式传入来源和路径，递归报告重复 Skill ID、完全重复的 `description` 与无效 metadata，指向同一真实目录的软链接只记为 alias。语义相似不做词法自动裁决；`fixtures/skill-eval/prompt-cases.json` 中同一 `competition_group` 的真实请求只声明并静态校验唯一触发 Owner 和竞争者 hard negative，真实触发行为仍需 live eval / smoke：

```bash
python3 scripts/evaluate-skills.py \
  --catalog-root "codex=${CODEX_HOME:-$HOME/.codex}/skills" \
  --catalog-root "agents=$HOME/.agents/skills"
```

上例覆盖用户 Skill 与 `.codex/skills/.system`，不覆盖插件缓存。需要供应链候选补扫时可追加 `--catalog-root "plugin-cache=${CODEX_HOME:-$HOME/.codex}/plugins/cache"`；缓存可能包含未启用或多版本插件，不得把扫描结果直接写成当前运行时启用清单。

跨 Skill 的 baseline/candidate 对照使用离线行为评测入口；它不调用 Agent 或网络，只准备同题任务、校验同一 runner/model 的成对回答、分离盲评材料与映射密钥，并根据独立评分执行准出门禁：

```bash
python3 scripts/evaluate-skill-behavior.py prepare --trials 3 --output /tmp/skill-behavior-plan.jsonl
# 使用同一 runner/model 收集 response JSONL：case_id、trial、condition、response、runner、model；可选 execution_evidence 必须成对提供，格式限 tool:id:status、validation:id:status 或 artifact:sha256:status
python3 scripts/evaluate-skill-behavior.py blind --responses /tmp/skill-behavior-responses.jsonl --output /tmp/skill-behavior-judge.jsonl --key-output /tmp/skill-behavior-key.json
# 独立评分 JSONL：pair_id、label、五项 rubric 分数、blocker、notes、blind_sha256
python3 scripts/evaluate-skill-behavior.py score --scores /tmp/skill-behavior-scores.jsonl --key /tmp/skill-behavior-key.json --blind /tmp/skill-behavior-judge.jsonl --output /tmp/skill-behavior-report.json
```

所有独立评分都须从 blind 文件原样保留 `blind_sha256`，`score` 始终核对 seed 映射、blind 正文与 scores；cases 声明 `source_profiles` 时，response 还必须原样保留 `prepare` 生成的 `case_sha256` 与 `source_sha256`。任一漂移即拒绝。

默认 8 个用例覆盖直接回答、Agent 自主完成、根因诊断、详细解释、破坏性操作、真实歧义、部分成功和来源证据边界。候选存在阻塞项、正确性或安全性实质回退、或加权得分未提升时，`score` 返回非零。真实 smoke 通过当前 Codex provider 发起只读请求，并把结果写到指定目录；`semantic-contract`、`module-deliberation` 与 `wind-validation` 单独模式直接读取源仓库规则，`spring-bean` 与 `ui-design` 也采用同一方式，其余模式先检查安装一致性：

```bash
scripts/smoke-wise-agent-behavior.sh --mode all --output-dir /tmp/wise-agent-smoke
scripts/smoke-wise-agent-behavior.sh --mode design-composition --runs 3 --output-dir /tmp/wise-agent-design-smoke
scripts/smoke-wise-agent-behavior.sh --mode superpowers --output-dir /tmp/wise-agent-superpowers-smoke
scripts/smoke-wise-agent-behavior.sh --mode governance --output-dir /tmp/wise-agent-governance-smoke
scripts/smoke-wise-agent-behavior.sh --mode module-deliberation --output-dir /tmp/wise-agent-module-deliberation-smoke
scripts/smoke-wise-agent-behavior.sh --mode self-improvement --runs 3 --output-dir /tmp/wise-agent-self-improvement-smoke
scripts/smoke-wise-agent-behavior.sh --mode grill-me --runs 3 --output-dir /tmp/grill-me-smoke
scripts/smoke-wise-agent-behavior.sh --mode huaxia --runs 3 --output-dir /tmp/huaxia-wisdom-smoke
scripts/smoke-wise-agent-behavior.sh --mode wind-validation --output-dir /tmp/wind-validation-smoke
scripts/smoke-wise-agent-behavior.sh --mode spring-bean --output-dir /tmp/spring-bean-smoke
scripts/smoke-wise-agent-behavior.sh --mode ui-design --output-dir /tmp/ui-design-smoke
scripts/smoke-wise-agent-behavior.sh --mode security --output-dir /tmp/security-routing-smoke
```

`all` 覆盖产品、工程、设计分层与文档主线、Superpowers 协同、轻量治理、状态恢复、学习回流、`grill-me`、华夏决策校准、Wind Service validation、Spring Bean 注册、Web UI 设计路由，以及安全设计、资金安全、代码修复、仓库扫描和 finding 路由；`--runs 3` 用于观察方差。真实 smoke 仍只证明样例行为满足契约。维护者更新项目自有 `grill-me` 后可运行 `VALIDATE_GRILL_ME_INSTALL=1 ./scripts/validate.sh`；更新官方 Superpowers 插件后可运行 `VALIDATE_SUPERPOWERS_INSTALL=1 ./scripts/validate.sh`。普通使用这些能力不需要运行安装校验。

## 维护者入口

新增或修改 Skill 时遵循 [AGENTS.md](./AGENTS.md)：保持 `SKILL.md` 精简，详细知识进入 `references/`，确定性动作进入 `scripts/`，真实正负例进入 fixtures；同时检查 `agents/openai.yaml`、引用、来源边界和同步 dry-run。一个规则只保留一个权威来源。

公开来源、读取状态和不吸收边界统一查[仓库级来源索引](./references/source-map.md)；专题来源进入各 Skill 的 `references/source-map.md`，README 不复制外部正文。

### SkillX 导出规范

把 SkillX 或类似系统的候选能力转换为 Codex Skill Package 前，先读 [SkillX 到 Codex Skill Package 导出规范](./references/skillx-to-codex-skill-package.md)，完成输入契约、安全门禁、三层映射、生成流程和验证流程。第一版只接受人工审查后的离线 JSON，不自动读取历史轨迹、不采集用户数据、不引入外部训练流水线。

输入必须符合 `schemas/skillx-candidate.schema.json`；`scripts/skillx_export_adapter.py` 生成的候选包包含 `REVIEW.md` 和 `fixtures/trigger-prompts.md`：

```bash
python3 scripts/skillx_export_adapter.py --check-input --input fixtures/skillx/sample-candidate.json
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out
python3 scripts/skillx_export_adapter.py --validate-output /tmp/skillx-out/skillx-product-reviewer --input fixtures/skillx/sample-candidate.json
```

### 来源与自我改进

Skill 内循环执行真实任务；外循环只把重复失败、CR 结论、fixture / validator 失败和人工纠偏转成最小可验证 diff。不得从单次失败泛化永久规则，不得吸收个人偏好、私有轨迹、客户资料、生产数据、密钥、外部文章原文或 Agent 自述，也不得自动提交、同步或发布。
