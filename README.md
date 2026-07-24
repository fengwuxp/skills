# 知止者与 Codex Skills

本仓库维护一组可安装、可验证、可组合、可持续演进的 Codex Skills。它不是 prompt 集，也不是角色接力系统：当前 Agent 始终对用户负责，专业 Skill 只是按需装载的能力包。

仓库把知止者设计为默认交互与责任模型，`$wise-agent` 是显式协同入口，但不表示每个任务都必须加载它。简单任务直接完成；单一领域且边界清楚的任务可直接加载对应专业 Skill；任务跨专业、跨阶段、跨轮，或需要状态恢复、独立验证和知识回流时，再由知止者持有完整目标。

## 项目定位

知止者不是流程路由器，而是统一智能行动主体：先读事实，再判断问题，装载最小能力，完成真实工作，用独立证据验证并归位结果。多 Skill 只为同一 Agent 补充专业上下文，不产生第二人格或重复 Owner。

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

### 1. 30 秒上手

日常不需要选角色或背 Skill 名称。通用任务模板只要求说明交付物、事实源、范围、授权和完成证据：

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；
请读取 <材料或路径>；只处理 <范围>，不做 <非目标>；
允许 <只读 / 写入路径 / 其它授权>；
用 <检查命令 / 评审证据 / 验收标准> 证明完成。
信息足够就直接推进，只在关键决策或高风险授权处问我。
```

任务明显跨专业、跨阶段、跨轮，或你希望 Agent 自己判断并推进、持续保持目标和状态时，再在前面加 `$wise-agent：`。单一专业任务可直接点名对应 Skill；不确定时只描述任务，不要先设计角色接力。

常见任务可以直接这样说：

| 任务 | 友好指令 |
| --- | --- |
| 自主推进 | `$wise-agent：读取当前项目事实，自己判断并推进；只在关键决策或高风险授权处问我，完成后给出产物、验证和残余风险。` |
| 复杂长任务 | `$wise-agent：为这项跨轮工作建立 Goal；存在真实分支、汇合或并行时再附加可校验 work_graph，保持状态并在停止条件命中时交还我。` |
| 需求讨论 | `先做能力归位：判断这个需求是在使用、增强、组合还是新增哪项稳定能力；默认审视不等于默认展开。` |
| 产品设计 | `根据 <访谈/需求/原型> 写一版可评审 PRD；先提炼稳定能力、共性和有证据的特殊性，再展开场景、流程、规则和验收。` |
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

#### 默认能力视角

所有需求讨论和设计都先做能力归位，判断是在使用、增强、组合还是新增哪项稳定能力。默认审视不等于默认展开：

- Bug、文案调整、局部字段、一次性迁移等局部需求，只说明影响的既有能力并走最小实现，不展开能力地图。
- 出现多场景、多主体、跨渠道、跨模块、存在生命周期或真实变化轴等证据时，再提炼共同目标、对象、不变量和契约，把差异承载到规则、参数、策略或适配边界，并用代表性场景验证能力边界。

不需要每次复述完整方法，直接说：`先做能力归位，默认审视、按证据展开；局部需求最小实现，多场景再提炼共性、特殊性和变化轴。`

#### 快速编码怎么用

简单任务、确定性高的场景和小范围代码调整会默认走快速编码：先读相关源码、调用方、测试和项目约规，连续完成最小实现，再集中补测试、验证和 CR。你也可以说：`快速改这个方法，先完成实现，测试最后统一补；只改 <路径>，最终运行 <命令>。`

“仅编码”只表示当前阶段编码先行，不表示永久跳过测试。代码写完但验证尚未完成时，只能视为“实现已完成，测试与验证待补”；涉及公共契约、数据库、资金、权限、租户、安全、生产操作、新依赖或跨模块调整时不会默认走快速路径。

`CAD` 现在只作为内部文件路由标识，不需要用户选择。简单局部任务走快速编码，普通一次性交付走标准工程流程；只有单个任务已选定、关键决策冻结，状态载体、反馈源、验证者、写入与验证边界、预算、停止条件和适用授权齐备，且明显需要多轮反馈时，才进入受控工程执行 Loop。适用授权是覆盖当前任务的 Plan Grant，或单任务 Execution Grant；不要求重复授权，也不新增状态或授权类型。Goal 仍只使用 `Draft / Ready / Active / Blocked / Verified / Closed / Superseded`。

需要让所有仓库默认继承知止者的最小行动原则时，可在明确授权后，把[全局行动内核](./wise-agent/assets/codex-global-agents.md)合并到 `$CODEX_HOME/AGENTS.md`。它不会强制每轮加载完整 `$wise-agent`；已有规则不得直接覆盖。

### 2. 任务与专业能力

下表用于确认边界，不是使用前必须选择的菜单。产品、架构、文档、考据、生成和约规不是平级角色，它们是知止者按需使用的专业能力。

| 你要交付 | 专业能力与路径 | 最小输入 | 边界 |
| --- | --- | --- | --- |
| 跨领域真实工作、目标控制、能力组合、验证和知识演进 | 知止者，ID：`wise-agent`，路径：[wise-agent](./wise-agent) | 目标、事实源、范围、授权、完成证据 | 不限于产研；不获得无限自治或高风险授权 |
| 产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图 | 产品架构专家，ID：`product-architecture-expert`，路径：[product-architecture-expert](./product-architecture-expert) | 用户、主体、目标、材料、范围、验收 | 不负责工程实现、代码 Review 和生产排障 |
| 系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图 | 资深架构师，ID：`senior-software-architect`，路径：[senior-software-architect](./senior-software-architect) | 路径、目标或现象、约束、验证命令、写入授权 | 不替代产品专家定义复杂业务语义、PRD 和金融产品规则 |
| 正式报告、制度、手册、研究说明、文档审校、DOCX/PDF | `document-authoring`，路径：[document-authoring](./document-authoring) | 读者、用途、事实源、载体、验收方 | 不改变产品、工程、法律、合规或考据结论 |
| 教程、视频、代码、文档、规范和产物到可复用能力候选 | 资源炼技，ID：`resource-capability-distiller`，路径：[resource-capability-distiller](./resource-capability-distiller) | 可读取材料、复用目标、目标环境、许可与验收方式 | 先提炼能力单元并逐项归位；不默认创建新 Skill，不自动安装、同步、提交或晋升 |
| 汉字学、训诂、字源、甲骨文、金文、小篆、通假和异体 | `hanzi-philology`，路径：[hanzi-philology](./hanzi-philology) | 对象、时代、文本范围、材料、结论等级 | 《说文解字》只是证据之一；不用于测字起名或普通工程命名 |
| 华夏经典视角下的现实决策、组织协作、长期成长和行动取舍 | 华夏经世智慧，ID：`huaxia-practical-wisdom`，路径：[huaxia-practical-wisdom](./huaxia-practical-wisdom) | 事实、目标、约束、主体、时限、最坏损失 | 不作医学诊疗、占卜命理或古籍训诂，不替代专业结论 |
| 方案、计划或设计的关键分叉、历史去重和决策快照 | `grill-me`，路径：[grill-me](./grill-me) | 方案、材料、历史决策、Owner、风险边界 | 未达到 shared understanding 不执行；自决不扩大授权 |
| DDL/schema/Java 类/字段表格到 Java Service 脚手架 | `java-service-code-generator`，路径：[java-service-code-generator](./java-service-code-generator) | 结构化输入、表名、模块、输出目录、覆盖授权 | 不从纯自然语言直接生成生产代码；生成后仍要编译、测试和源码 CR |
| Java 项目通用编码约规，或按依赖/上下文启用 Wind/Nobe 专项 | `wind-coding-conventions`，路径：[wind-coding-conventions](./wind-coding-conventions) | Java 源码证据、依赖/包名、规则问题 | 只做规则判断和偏差说明；源码设计、CR、TDD、修复和验证由架构师主责 |

没有 Wind/Nobe 高置信度信号时不加载 Wind face/impl、API 或模型专项；Wind 项目按实际依赖和上下文补专项入口。普通 Java 源码 CR 由架构师主责，并消费通用 Java 约规。

图形化交付按语义归属：产品流程、状态、资金流和验收视图由产品专家负责；系统模块、接口时序、部署和实现状态由架构师负责。复杂可编辑架构图、代码库结构转图或架构描述转图，应先稳定语义，再按需调用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。

常见组合仍只保留一个最终 Owner：

- 从 AI 原型到工程化：产品专家稳定对象、流程、规则和验收，架构师完成系分、TDD、源码 CR 和生产验证，知止者持有跨阶段目标。
- 材料包含访谈、工单、竞品、路线图、PRD、发布复盘或提到 `pm-skills` 时，知止者装载产品判断动作链，形成产品上下文包并继续持有后续目标、验证和停止条件。
- 从训诂考据到正式报告：`hanzi-philology` 先形成证据卡，`document-authoring` 只负责成文与载体，不改变证据等级。
- 从普通图到复杂图：先由产品专家或架构师稳定语义，再决定是否使用专用出图能力。
- 官方 Superpowers 插件只补 brainstorming、TDD、调试、CR、验证等方法缺口，不替代产品或工程主能力，也不扩大 Git、worktree、subagent 或安装授权。

专项使用细节、状态契约和校验命令以对应 Skill 的 `SKILL.md`、reference 与 script 为准；README 只保留用户入口和职责边界，不复制专业说明书。

### 3. 知止者如何工作

加载 `$wise-agent` 时，知止者按 **察 -> 辨 -> 谋 -> 行 -> 验 -> 化** 推进：读取一手事实，区分事实/推断/待确认，选择最小能力和路径，完成实际工作，独立验证，再把状态、决策和经验归位。它不是不行动，而是让行动有方向、有分寸、有收口。

简单任务直接完成；复杂任务才使用计划、SDLC、Goal、Loop、Worker 或 Checker。专业能力按需渐进加载，无论内部用了多少能力，对用户只形成一个综合结论。

四类场景视图只用于强调当前边界，不是并列流程：

- **只读理解视图**：核验材料、源码、测试和日志；默认不写文件、不联网、不安装。
- **交付推进视图**：产出真实 PRD、系分、代码、测试、图或知识资产。
- **验证发布视图**：用原始证据做质量门禁、源码质量评审或生产交付审查。
- **知识回流视图**：把已验证经验归位到项目上下文、知识库、ADR、约规、fixture 或脚本。

常用短句：`进入知止者`、`进入只读理解视图`、`做质量门禁`、`做源码质量评审`、`做生产交付审查`、`进入知识回流视图`。

#### 3.1 什么时候启用 SDLC、Goal、Loop、Worker、Checker

五者不是固定流水线。默认直接完成，再按真实证据增加控制：

| 机制 | 何时启用 | 不该启用 | 友好指令 |
| --- | --- | --- | --- |
| SDLC | 跨产品、设计、工程、验证、发布或运行阶段，需要阶段门禁和交接 | 单阶段或一步任务 | `按完整 SDLC 覆盖这个需求到发布，但只展开当前需要的阶段。` |
| Goal | 跨会话、跨 Wave，需要保存成功标准、状态、预算和停止线 | 当前会话能闭环 | `为这项工作建立 Goal 并持续推进，成功标准是 <...>，停止条件是 <...>。` |
| Loop | 同一 Goal 需要反复执行、观察和验证，且有状态载体与轮次边界 | 一次执行即可完成 | `允许进入 Loop，最多 <N> 轮；连续 <N> 轮无进展就停止。` |
| Worker | 子任务输入可冻结、写入不重叠、低耦合，并行收益明确 | 同一文件、强耦合调用链 | `这些子任务互不依赖，可并行时再派 Worker；共享文件串行。` |
| Checker | 高风险、公共契约、重要交付、发布准出或需要独立 CR | 低风险任务已有回读或测试 | `增加独立 Checker，直接读取原始产物和证据，不只审 Maker 摘要。` |

SDLC 是阶段地图，Goal 是跨轮目标契约，Loop 是反复执行契约，Worker 是执行拓扑，Checker 是独立验证机制。Worker 与 Checker 不是顺序阶段，可以只用 Checker 而不派 Worker。

##### 3.1.1 复杂工作图怎么用

工作拓扑投影不是新的 `Graph Mode`，也不是另一份任务真相源。简单、线性、单文件或一次可完成的任务直接执行；只有至少三个节点存在分支 / 汇合依赖、并行 Worker、跨 Wave 交接或动态取消 / 重排时，才在现有 Goal 状态契约中附加 `work_graph`。

按复杂度逐层增加字段，不为完整而补空结构：

| 已有事实 | 增加内容 |
| --- | --- |
| 只有节点依赖、状态、风险和写入范围 | 使用最小 `work_graph`，不加运行语义 |
| 下游必须读取上游的明确产物 | 增加 `state_inputs / consumes / produces / writeback` |
| 可核验条件会改变下一节点 | 增加带唯一 `default` 的 `transitions` |
| 外部调用确有暂时失败和重试价值 | 增加有界 `failure_policy` |

使用时守住四条边界：写回路径同时属于节点和 Goal 的 `write_scope`；一个有效状态键只有一个产出节点；依赖、条件路由和 fallback 合并后仍无环；节点 `max_attempts` 不得超过 Goal 的 `max_iterations`。并行节点写入范围不能重叠，高风险节点必须有独立 Checker。

可以直接这样说：

```text
$wise-agent：这个 Goal 存在 <分支 / 汇合 / 并行 / 跨 Wave>，
请基于现有 Goal Ledger 投影可校验的 work_graph。
只在确有跨节点数据、条件路由或可重试调用时增加对应运行语义；
检查写回授权、状态键唯一产出、无环执行边、重试预算和高风险 Checker。
不要创建第二份真相源，也不要扩大写入或执行授权。
```

生成或恢复状态后运行：

```bash
python3 wise-agent/scripts/check_state_contract.py <current.json> --previous <previous.json>
```

首版省略 `--previous`。退出码为 `0` 只证明状态契约、授权和执行边结构可接受，不代表节点工作、测试或发布已经通过。

决策寻路也不是第六个控制机制。只有目标大致明确，但路线仍模糊、超过一次会话且无法可靠形成 Spec 或计划时才启用；此时只维护决策地图，不要生成 Spec、计划或执行任务。路线清楚时直接跳过。

#### 3.2 决策澄清与 Grill Me

决策澄清门禁只处理真正未决的 Decisions。Facts 先从材料、源码、测试或日志自答，Decisions 才问 owner；复杂或模糊任务一次只问一个主 blocker。每轮结果只有：`自决推进 / 询问 owner / 继续收敛 / 停止交接`。

`grill-me` 是升级盘问，不是每个任务的必经流程：

- 关键分叉未决、回答含糊、连续返工，或下一步会改变公共契约、状态机、验收和风险时触发。
- 每次提问前先读问题台账、决策快照、文档、代码、测试和知识库；已确认或已排除的问题不得换个说法重问。
- 可查 Facts、已有 Owner 结论和低风险可逆默认项由 Agent 自答并留痕；新价值取舍、公共契约、高风险和红线交给 Owner。
- 你只需要回答接受建议、改答案、补材料或停止；说“按你建议推进”只关闭当前 blocker。
- 退出：确认 shared understanding，形成决策快照；未确认前不执行。
- 红线、底线、不能碰、不可、禁止、必须等表达必须记录，执行前逐项对账。

#### 3.3 知识、上下文与学习回流

知识回流不是把任务总结整篇复制进知识库。先确认结论已被材料、源码、测试、日志或 Owner 验证，再按业务域或模块找到已有权威位置；没有权威位置或写入授权时，只给候选落点。

| 类型 | 适合保存 | 要求 |
| --- | --- | --- |
| 稳定知识 | 概念、责任边界、核心流程、长期不变量、证据规则 | 进入项目约规、领域知识库或 ADR；变更时清除旧值并说明影响 |
| 时效知识 | 工具版本、平台限制、外部规范、近期策略 | 记录来源、核验日期、适用范围和复核条件 |
| 任务知识 | 本轮材料、计划、验证、临时判断、待确认项 | 默认留在 Issue、Goal Ledger、评审或任务记录，验证后再晋升 |

需要把上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀变成可维护资产时，可说 `进入知识生产`；产物必须形成可检索、可更新、可验证的上下文资产，而不是一次性长文。

开启学习回流模式后，只会把当前任务中已脱敏、可复核、命中门禁的经验记录为 `candidate`；候选不会成为运行时指令，也不会触发历史扫描、自动确认、改 Skill、提交或同步：

```bash
python3 ~/.codex/skills/wise-agent/scripts/skill-learning-ledger.py enable
python3 ~/.codex/skills/wise-agent/scripts/skill-learning-ledger.py status
python3 ~/.codex/skills/wise-agent/scripts/skill-learning-ledger.py disable
```

### 4. 编写文档的友好指令

产品、系分、重构三类正式设计文档各有一个权威模板入口：产品设计用 `product-prd-template.md`，系分设计用 `system-analysis-template.md`，迁移型重构用 `refactoring-design-template.md`。不需要记路径，直接说明材料、文档类型、读者、目标文件和验收要求：

- `基于 <需求或材料路径> 编写可评审产品设计，保存到 <目标路径>；先做能力归位，多场景才提炼共性、特殊性和变化轴；正文按背景、目标、定性、概要、详细设计、流程、规则和产品接口抽象展开，验收摘要放在最后。`
- `基于 <产品文档> 和 <源码/接口/DDL> 编写系分，保存到 <目标路径>；先说明能力归位、共同对象、不变量和真实变化轴，再讲背景、目标、定性、概要、详细设计、流程、业务规则、接口抽象、数据与风险。`
- `为 <产品设计/系分> 另建执行计划，承接详细验收矩阵、AC 与测试映射、验证命令、执行 owner、任务状态、发布和回滚；不要把这些控制字段铺进正式正文。`
- `基于 <现状证据> 判断是否需要独立重构设计；需要时输出可验证、可暂停、可回退的 MIG 切片。`
- `只评审 <文档路径>，不要改文件；列出必改项、待确认项、证据缺口和能否进入下一阶段。`
- `更新 <既有文档路径>，保持文件名和已确认结论；只补本轮变化。`
- `把 <权威 Markdown> 整理成 <DOCX/PDF>；不改变产品或工程语义，并检查目录、分页、表格、图片和中文字体。`

已有正式文档默认原路径更新，不因模板升级另建“新版”“最终版”或日期副本。正式 PRD、系分、ADR 和 OpenSpec/SDD 只保留当前结论；讨论过程进入评审报告、Decision Log、Goal Ledger 或任务记录。

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

同步单个 Skill 使用 `./sync-skills.sh senior-software-architect`；非默认目录使用 `CODEX_HOME=/path/to/codex-home`。同步使用 `rsync --delete`，会先备份已有安装，并按替代关系退役 `wind-project-coding-conventions`、`delivery-collab` 和 `huaxia-wisdom`。完成后重启 Codex 或开启新会话。

## 验证与同步安全

修改 Skill、reference、script、fixture 或 README 后运行：

```bash
./scripts/validate.sh
git diff --check
./sync-skills.sh --dry-run all
```

正式同步后运行 `scripts/validate-installed-skills.sh`。`--dry-run` 不写安装目录；正式同步需要对应授权，备份保存在 `$CODEX_HOME/skills/.backups/`。

`scripts/evaluate-skills.py` 只做离线静态预检，不能替代真实 Agent 行为。真实 smoke 会先检查安装一致性，通过当前 Codex provider 发起只读请求，并把结果写到指定目录：

```bash
scripts/smoke-wise-agent-behavior.sh --mode all --output-dir /tmp/wise-agent-smoke
scripts/smoke-wise-agent-behavior.sh --mode design-composition --runs 3 --output-dir /tmp/wise-agent-design-smoke
scripts/smoke-wise-agent-behavior.sh --mode superpowers --output-dir /tmp/wise-agent-superpowers-smoke
scripts/smoke-wise-agent-behavior.sh --mode governance --output-dir /tmp/wise-agent-governance-smoke
scripts/smoke-wise-agent-behavior.sh --mode self-improvement --runs 3 --output-dir /tmp/wise-agent-self-improvement-smoke
scripts/smoke-wise-agent-behavior.sh --mode grill-me --runs 3 --output-dir /tmp/grill-me-smoke
scripts/smoke-wise-agent-behavior.sh --mode huaxia --runs 3 --output-dir /tmp/huaxia-wisdom-smoke
```

`all` 覆盖产品、工程、设计分层与文档主线、Superpowers 协同、轻量治理、状态恢复、学习回流、`grill-me` 和华夏决策校准；`--runs 3` 用于观察方差。真实 smoke 仍只证明样例行为满足契约。维护者更新项目自有 `grill-me` 后可运行 `VALIDATE_GRILL_ME_INSTALL=1 ./scripts/validate.sh`；更新官方 Superpowers 插件后可运行 `VALIDATE_SUPERPOWERS_INSTALL=1 ./scripts/validate.sh`。普通使用这些能力不需要运行安装校验。

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
