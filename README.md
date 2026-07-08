# Skills

本仓库用于维护可安装到 Codex 的 Skills。它不是轻量 prompt 集，而是一套可长期演进的 Agent 运行时资产库。

仓库采用分层治理：`AGENTS.md` 保存每个会话都应知道的默认规则和安全边界；各技能的 `SKILL.md` 保存特定任务的入口、路由和红线；详细知识、模板和方法论放在对应技能的 `references/` 中；确定性生成、验证、同步和安全检查放在 `scripts/` 中；Skill 改进只基于脱敏后的执行记录、验证结果、CR 结论和人工反馈。

## 用户使用指南

安装或同步后，Codex 会根据每个 `SKILL.md` 的 `name` 和 `description` 自动触发技能；也可以直接点名。同步后如果触发不符合预期，先重启 Codex 或开启新会话。

使用时不用先背 Skill 名称。先说目标、材料、边界、风险和验证；拿不准入口时，直接说 `先帮我选路`。

### 1. 一句话讲清目标

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；已有 <材料或路径>；边界是 <不做什么 / 是否允许写入 / 风险>；验证要求是 <检查命令 / 证据 / 残余风险说明>。
```

这句话里最重要的是：目标、材料、边界、风险、验证。材料可以是需求、PRD、页面、截图、DDL、代码路径、日志、测试输出或外部文章；风险要特别说明资金、合规、生产、密钥、部署、删除和不可逆操作。

### 2. 按交付物选入口

- 产品语义 / 业务架构规划 / 产品判断动作链 / PRD / Backlog / 验收：用 `产品架构专家`，先讲清用户/主体、目标、对象、流程、规则、验收和待确认项；业务架构要补战略意图、业务能力、项目组合、能力-项目-系统映射和知识库回流落点。
- 系分 / 架构 / 代码 / Bug / 测试 / CR / 发布：用 `资深架构师`，直接给源码锚点、现象、约束、验证命令和生产风险。
- 跨角色产研交付 / 目标拆解 / 任务计划 / Spec / Harness / 质量发布 / 生产交付审查 / 知识生产闭环：用 `AI Native Engineering Loop`。它默认进入角色协作 Loop，按设计、设计评审、TDD、编码、编码评审、可用性/安全性评估、验证发布和复盘回流分角色推进；也可承接业务专家蒸馏；目标层、计划层、原子执行层和执行契约是内部层，不替代 PRD、系分、代码或发布审批。
- Java Service 脚手架：用 `java-service-code-generator`，但必须有 DDL/schema/Java 类/字段表格、表名、模块和覆盖边界。
- 图形化交付：产品语义图用产品专家，工程架构图用架构师。复杂可编辑架构图、代码库结构转图或架构描述转图先由架构师判断 Architecture Diagram Generator 准入；复杂视觉续作再用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。
- 外部 Skill / 工具接入：先做供应链安全审查，再判断是否允许联网、安装、写配置或同步到 Codex。

### 3. AI Native 只做编排

`AI Native Engineering Loop` 是编排入口，不是万能执行入口。它回答“现在由谁做、交接什么、怎么验证、什么时候停”，产品正文交给 `产品架构专家`，工程实现交给 `资深架构师`。

默认先判断当前处于角色协作 Loop 的哪个阶段，再选最小场景视图：

- **只读理解视图**：阅读分析代码库、设计-代码对齐、工具准入、事实边界检查和影响范围识别；Gemini CLI 仅在本机可用、认证 / 读取范围获授权且当前状态核验通过时作为只读候选，失败则回退 Codex 内置工具，默认不写文件、不安装。
- **产研交付视图**：从产品事实、PRD/Spec、设计评审、TDD、编码、编码评审、可用性/安全性评估到生产发布和反馈回流，目标是交付真实、可验证、可接手的生产可用能力。
- **验证发布视图**：测试矩阵、质量门禁、源码质量评审、生产交付审查、失败回退、发布监控、残余风险和复盘。
- **知识回流视图**：把已验证经验沉淀到 Skill、reference、fixture、脚本、用户指南或 source-map；做上下文资产化、上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀时，可说“进入上下文治理视图”或“进入知识生产 Loop”，先落 Context System，再评估知识库工具，并说明验收 owner、更新频率和停用条件。

AI Native 的默认最小输出只保留：结论、当前阶段、owner、交接物、授权策略、验证与停止条件；需要时补证据边界和残余风险。证据边界必须区分事实、推断、待确认和范围外不做；授权策略必须区分只读、计划内低风险执行、受控执行授权和显式确认。只有用户要求完整方案、评审报告或模板，才展开 Loop Contract、RACI、验证矩阵、Goal Ledger 或内部实现层。

角色协作阶段只是编排坐标，不是能力来源。AI Native 输出时必须写明能力来源：产品 / 交互设计和验收种子回到 `产品架构专家`；业务架构规划、能力地图、项目组合和知识库回流计划也回到 `产品架构专家`；系分、TDD、编码、最小正确实现检查、CR、安全可靠和发布回到 `资深架构师`；结构化 Java Service 生成回到 `java-service-code-generator`；Wind 项目编码规则回到 `wind-project-coding-conventions`；代码阅读和图形化只作为理解与表达辅助。

产品材料散在访谈、工单、竞品、数据、路线图、PRD、发布复盘或增长实验中时，先让 `产品架构专家` 跑产品判断动作链，输出证据、判断动作、取舍结论、不做项、下一产物、owner 和验收 / 停止条件；AI Native 再判断是否足以进入系分、TDD、编码或质量门禁。

PRD、系分、产品设计文档、接口、事件、代码和测试证据已经比较完整，但团队反复解释同一业务域时，可让 AI Native 进入业务专家蒸馏；只生成可追溯 Skill Pack 草案和压力测试，不默认安装，不替代产品 owner、架构 owner 或正式评审。

轻量问询只服务 Ask-or-Decide：复杂或模糊任务一次只问一个主 blocker，并给建议答案、依据、影响和默认暂停点；能从材料、源码或测试自答的先自答。用户说“按你建议推进”时，先关闭当前 blocker，写入下一阶段输入，再挑下一最高价值 blocker，不重开全局规划。

角色协作 Loop 的处理步骤：

1. 识别目标、材料、写入边界、风险和验证要求。
2. 选择最小场景视图，并用 Ask-or-Decide 收敛缺口。
3. 分派能力来源：产品 / 交互回产品专家，系分、TDD、编码、CR 和发布回架构师，结构化代码生成回代码生成器；每个阶段都要写能力 / 约规来源。
4. 按 `意图 -> 产品/交互 -> 设计评审 -> TDD -> 编码 -> CR -> 质量评估 -> 验证发布 -> 复盘回流` 推进需要的阶段。
5. 任务结束责任闭环：阶段结束先自查交付、证据、残余风险和是否越界，再按 Ask-or-Decide 判断 Auto-Decide Next、Auto-Ask Owner、Auto-Loop 或 Stop-Handoff；需要继续时，只给下一任务计划问询或最小计划草案，且一次只推进一个 blocker。

### 4. 产品到工程的默认闭环

产品发现由 `产品架构专家` 收束问题、对象、规则、验收种子和待确认项；编排准入由 AI Native 判断成熟度、owner、授权、门禁和停止条件；角色协作按阶段切换产品、架构、Maker、Checker 和人工 owner；工程执行由 `资深架构师` 承接系统设计、编码、TDD、源码级 CR 和发布风险；质量理解门禁负责测试、CR、影响范围和残余风险；交付复盘回看返工、缺陷、知识回流和停止条件。需要持续推进时，进入三卡交接：Product Context Card、Engineering Handoff Card 和 Production Loop Card；三卡都不是 Execution Grant、测试通过或上线审批。

### 5. 体用原则

先定体，再调度用。体：业务目标、用户/主体、生产边界、风险责任、验收标准和证据边界。用：Skill、工具、模板、图、代码、测试、提交和发布动作。体用合一，避免体用混一；阴阳互根，产品价值和工程约束互相校验；执简驭繁，小任务直接用专门 Skill，跨角色、跨阶段、跨工具或高风险任务再让 AI Native 编排。

### 6. 常用短句

- `先帮我选路`：判断应该用 AI Native、产品架构专家、资深架构师还是代码生成器；输出理由、缺口、下一步 owner 和停止条件。
- `进入角色协作 Loop` / `进入产研交付视图`：AI Native 主入口，按设计、评审、TDD、编码、CR、质量评估、验证发布和复盘分角色推进，目标是交付真实生产可用能力。
- `进入只读理解视图`：读代码库、对齐设计和代码、评估工具准入或做事实边界检查；默认不写文件、不联网、不安装。
- `做生产交付审查` / `做质量门禁`：按价值、范围、设计、实现、CR、QA、观测、回滚、人工接管和下一 owner 判断 Ready / Not Ready / Human Approval Required；需要时补测试矩阵、验证顺序、CR 前置条件、失败回退和残余风险交接。
- `进入产品判断动作链`：产品专家把访谈、工单、竞品、数据、路线图、PRD、发布复盘或增长实验串成证据、取舍、不做项、owner 和下一产物；需要工程化时再交 AI Native 判断准入。
- `做业务架构规划`：产品专家把战略意图、业务能力、价值流、核心对象、项目组合、能力-项目-系统映射和知识库回流计划串成可决策结构；需要工程化时再交 AI Native 判断准入。
- `按你建议推进`：AI Native 只关闭当前主 blocker、写入下一阶段输入，再挑下一最高价值 blocker；不重新摊开全局方案。
- `做源码质量评审`：结合项目约规、架构原则、代码坏味道、测试证据和工具补扫，输出 P 级发现、证据、最小修复和残余风险。
- `蒸馏业务专家`：阅读 PRD、系分、产品设计文档、接口、事件、代码和测试证据，输出证据地图、成熟度、事实/推断/待确认/范围外不做、owner 追认和压力测试。
- `进入知识回流视图`：梳理 L0/L1/L2 Context System，把已验证经验沉淀到 `AGENTS.md`、`CONTEXT.md`、ADR、reference、fixture、脚本、用户指南或 source-map，不吸收一次性试错。
- `初始化/更新项目 AGENTS.md`：让 AI Native 进入项目约规入口；需要启用 Wind 约规时，新项目生成本地 `AGENTS.md` 草案，已有文件只给最小 patch，规则权威回到 `wind-project-coding-conventions`。

### 7. 最小输入清单

- `AI Native 研发流程编排`：当前材料成熟度、目标产物、涉及 owner、写入/只读边界、授权策略、验证要求、是否需要目标拆解、任务计划、执行契约或工具准入。
- `业务专家蒸馏`：目标业务域、材料路径、资料版本/owner、用途、允许写入位置、敏感边界、期望成熟度、是否需要 owner 追认和 test-prompts。
- `业务架构规划`：战略意图、真实问题、决策场景、范围边界、业务域/模块、当前项目/系统、资料来源、业务 owner、验收方式和知识库保存规划。
- `产品架构专家`：业务目标、用户/主体、范围/非目标、输入材料、希望输出的产品产物、验收和待确认项。
- `资深架构师`：代码或文档路径、现象/目标、运行环境、约束、期望验证命令、是否允许改代码或只做 CR。
- `Wind 项目编码约规`：如果某个项目要采用，在该项目 `AGENTS.md` 标明“本项目遵守 Wind 项目编码约规”；没有项目 `AGENTS.md` 时，让 AI Native Engineering Loop 进入项目约规入口，再路由 `wind-project-coding-conventions` 读取初始化模板；已有 `AGENTS.md` 时，只补 Wind 约规入口、owner 路由、授权边界、验证命令和待确认事实。之后用 `wind-project-coding-conventions` 做规则判断，编码、TDD、源码级 CR 和生产风险仍交给 `资深架构师`。
- `java-service-code-generator`：DDL/schema/Java 类/字段表格、表名、业务模块、输出目录、是否允许覆盖已有文件。
- 画图 / 工具准入：说明对象、关系、受众、视图类型、输出格式、来源是否已审查，以及是否允许联网、安装、读写或提交。

### 8. 不要这样用

- 只写一份普通 PRD、产品方案或 Backlog 决策：直接用 `产品架构专家`。
- 只做系统设计、代码 CR、Bug、测试或生产变更：直接用 `资深架构师`。
- 只有自然语言需求、没有字段结构或表名：不要让 `java-service-code-generator` 从纯自然语言直接生成生产代码。
- 不要把工具、模板、目标、计划或授权机制名当主流程；默认先进入角色协作 Loop，再判断是否需要内部执行层。
- 角色协作 Loop 的目标是交付生产可用能力，不允许让 AI 随机推进模拟模块、无业务入口 demo、内存版业务 Service 或看上去可用的样子货。
- 涉及安装、联网、覆盖文件、Git、同步到 Codex、生产数据、密钥、部署或不可逆操作：先明确授权、写入范围、dry-run 和停止条件。

## 进阶能力索引

日常使用优先看上面的快速指南。本节给维护者和需要精确路由的人查技能边界、典型触发和常见组合。

### AI Native Engineering Loop

- 路径：[ai-native-engineering-workflow](./ai-native-engineering-workflow)。
- 适合：跨产品、UED、架构、AI Maker / Checker、质量门禁和发布复盘的产研交付流程；也处理目标拆解、任务计划、Spec/Harness、代码库理解、工具准入、设计-代码对齐和知识回流。
- 边界：只负责成熟度、owner、交接物、停止条件、授权策略和工具边界；产品正文交给产品专家，工程实现、最小正确实现检查和过度设计 CR 交给架构师，结构化代码生成交给代码生成器。
- 内部路由：Spec/SDD、AI 代码交付闭环、Agent Loop Engineering、架构排熵、Wisdom Lens、代码库知识图谱、Gemini CLI / AgentRC / Understand Anything / Ponytail / Open Code Review 准入，都先回到角色协作 Loop 再判断。
- 常用说法：`进入角色协作 Loop`、`进入只读理解视图`、`进入产研交付视图`、`蒸馏业务专家`、`做生产交付审查`、`做源码质量评审`、`评估 Gemini CLI / AgentRC / Understand Anything / Ponytail / Open Code Review`。

### 产品架构专家

- 路径：[product-architecture-expert](./product-architecture-expert)。
- 适合：PRD、产品方案、需求说明、业务架构规划、产品洞察/机会雷达、Backlog 决策、User Story/AC、概念生命周期、原型/HTML/页面截图/交互稿反推 PRD、能力地图、业务流程、状态机、规则矩阵、运营后台、数据指标、验收标准和产品架构图。
- 产品材料分散或提到 `pm-skills`、产品判断成流程、产品动作链、路线图取舍、发布复盘、增长实验时，先输出产品判断动作链卡，再按缺口转产品洞察、Backlog、PRD、合议评审或 AI Native 前置门禁。
- 支付与资金是重点能力，覆盖账户/账本、清结算、对账、外卡收单、ACH、VCC、争议和跨境支付。
- 使用时说明：输入材料、目标产物、业务边界、评审重点、验证要求。交给 AI Native 或架构师前，最好形成 Product Context Card：业务目标、非目标、角色 / 主体、核心对象与状态、主流程与异常、关键规则、验收种子、风险与待确认项、专业确认方。
- 不适合：不替代法务、合规、财务、税务、持牌机构或卡组织规则确认；不负责工程实现、代码 Review 和生产排障。

### 资深架构师

- 路径：[senior-software-architect](./senior-software-architect)。
- 适合：架构设计、系统分析设计、技术方案、ADR、代码 Review、Bug 修复、测试/TDD、生产变更、架构图、遗留系统改造、架构腐朽 / 排熵 / 可删除性评审和工程治理。
- 使用时说明：代码或文档路径、现象/目标、运行环境、约束、期望验证命令、是否允许改代码或只做 CR。
- Open Code Review / OCR 可作为外部代码评审 Checker，先由 AI Native 判断 CLI、插件、LLM provider、读取范围、规则来源和授权边界；输出仍由架构师按源码事实、测试证据、项目规范和 Wind opt-in 规则裁决。
- Wind/Nobe 风格项目如需统一 face/impl、基础服务、应用层服务、DTO/Request/Query/Entity、分包、MyBatis Flex 和外部集成规则，在项目 `AGENTS.md` opt-in “Wind 项目编码约规”，再用 `wind-project-coding-conventions` 作为规则权威；真实编码、TDD 和源码级 CR 仍由 `资深架构师` 承接。
- 不适合：不替代产品专家定义复杂业务语义、PRD 和金融产品规则；不在缺少边界、风险和验收时直接给可上线方案。

### Wind 项目编码约规

- 路径：[wind-project-coding-conventions](./wind-project-coding-conventions)。
- 适合：项目 `AGENTS.md` 已 opt-in Wind 约规后，判断 face/impl、服务分层、模型归位、Entity 不外露、ServiceImpl、MyBatis Flex 和 TDD/CR 是否符合项目约规；也可初始化或改进 Wind 项目本地 `AGENTS.md` 模板。
- 触发方式：新项目说“用 AI Native Engineering Loop 初始化项目 AGENTS.md，这个项目遵守 Wind 项目编码约规”；已有文件说“用 AI Native Engineering Loop 更新项目 AGENTS.md，这个项目已 opt-in Wind 约规，只做最小 patch”。需要直接查规则时，再说“用 `wind-project-coding-conventions` 检查 Wind 约规”。
- 边界：只做规则判断和偏差说明；真实编码、TDD、源码级 CR、Bug 修复和生产风险仍交给 `资深架构师`，结构化代码生成交给 `java-service-code-generator`。
- 与 OCR 协作：Wind 约规可作为 `.opencodereview/rule.json` 或 `ocr review --background` 的规则输入；OCR 不是 Wind 规则权威，发现项仍需架构师判读。
- 不适合：未 opt-in 的普通 Java/Spring 项目，不强套 Wind 约规。

### java-service-code-generator

- 路径：[java-service-code-generator](./java-service-code-generator)。
- 适合：根据 DDL/SQL、Java 类、字段表格或 schema 生成 Wind/Nobe 风格 Java Service 配套代码，包括 Entity、Mapper、DTO、Request、Query、Converter、Service、ServiceImpl 和测试夹具。
- 使用时说明：DDL/schema/Java 类/字段表格、表名、业务模块、输出目录、是否允许覆盖已有文件。
- 不适合：不从纯自然语言直接生成生产代码；不替代架构师、DBA 或业务负责人确认表结构、索引、状态机和金额精度。

### 常见组合

- 从 AI 原型到工程化：AI Native 先进入角色协作 Loop，定义阶段、owner、门禁和验证矩阵；产品专家补产品上下文包、Backlog 和 PRD-Lite；架构师补 OpenSpec、Harness、测试策略、TDD、源码级 CR 和发布风险。
- 从战略到项目组合：产品专家先做业务架构规划，输出业务架构准入卡、能力地图、价值流、能力-项目-系统映射、差距/依赖/优先级、路线图和按业务域或模块分区的知识库回流计划；AI Native 只判断交接成熟度、owner、验证和停止条件。
- 从想法到工程：产品专家先把目标、对象、流程、规则、验收和待确认项定清楚；架构师再承接系统设计、代码、测试和发布风险。
- 从 PRD 到代码生成：先由产品专家或架构师确认对象、状态、字段、索引和金额精度；已有 DDL、字段表格或 Java 类后，再用 `java-service-code-generator` 生成配套代码。
- 从普通图到复杂图：先由产品专家或架构师产出语义稳定的 SVG；需要复杂可编辑架构图、代码库结构转图或多层架构图时，再由架构师判断 Architecture Diagram Generator；需要精细视觉时再调用 `$fireworks-tech-graph`。
- 从金融产品到上线方案：产品专家先标出主体、法域、资金归属、外部规则和专业确认方；架构师再处理系统边界、数据一致性、可靠性、安全和发布回滚。

### 提示词示例

可直接复制这些示例；不需要同时塞满所有字段，关键是写清目标、材料、边界、风险和验证。

```text
用 AI Native Engineering Loop：按当前材料进入角色协作 Loop，只输出结论、当前阶段、owner、交接物、授权策略、验证与停止条件；需要时补证据边界和残余风险。

用 AI Native Engineering Loop 进入产研交付视图：目标是交付生产可用能力，请按产品/交互、设计评审、TDD、编码、CR、可用性/安全性/可靠性评估、验证发布分角色推进，并写明每阶段 owner、证据、授权和停止条件。

用 AI Native Engineering Loop 进入角色协作 Loop 问询推进：我接受你对当前 blocker 的建议，按你建议推进；请关闭当前 blocker、写入下一阶段输入，再挑下一最高价值 blocker，不重开全局规划。

用 AI Native Engineering Loop 做生产交付审查：请按产品价值、范围收敛、工程设计、交互可用、实现证据、独立 CR、QA 验证、发布观测、回滚/人工接管和下一 owner 判断 Ready / Not Ready / Human Approval Required。

用 AI Native Engineering Loop 进入只读理解视图：阅读这个代码库/模块，对齐设计和代码，输出入口路径、影响范围、源码锚点、事实/推断/待确认、验证建议和停止条件；默认不写文件、不联网、不安装。

用 AI Native Engineering Loop 蒸馏业务专家：阅读 docs/prd、docs/system-design 和相关接口/事件/测试，把支付账务域沉淀为可追溯 Skill Pack 草案；输出证据地图、D0-D3 成熟度、事实/推断/待确认/范围外不做、owner 追认问题和 test-prompts，不默认安装。

用产品架构专家进入产品判断动作链：这里有访谈、工单、竞品、路线图和 PRD 草稿，请先判断做什么、为什么做、先不做什么、下一产物和 owner，再决定是否交给 AI Native 进入工程。

用产品架构专家做业务架构规划：这里有战略目标、现有项目、系统清单和流程资料，请输出业务架构准入卡、业务能力地图、价值流、核心对象与规则、能力-项目-系统映射、差距/优先级、项目组合和按业务域或模块分区的知识库回流计划。

用产品架构专家梳理 VCC 发卡业务的产品架构，输出能力地图、核心对象、交易流程、资金流、风险和验收标准，默认 SVG 画图。

用资深架构师评审这个设计文档，重点看模块边界、数据一致性、可靠性、安全、测试和发布回滚，并给出 P0/P1/P2 问题。

用 wind-project-coding-conventions 检查这个已 opt-in Wind 约规的项目，重点看 face/impl、服务分层、模型归位、Entity 不外露、ServiceImpl 和 MyBatis Flex。

用 AI Native Engineering Loop 初始化项目 AGENTS.md：这个项目遵守 Wind 项目编码约规，请先读取项目结构和现有约束，只生成最小可用的根目录 AGENTS.md。

用 AI Native Engineering Loop 更新项目 AGENTS.md：这个项目已 opt-in Wind 约规，请只补项目约规入口、owner 路由、授权边界、验证命令和待确认事实，不重写已有规则。

用 java-service-code-generator 根据 docs/order.sql 生成订单模块配套代码，先输出到 /tmp/order-scaffold 评审目录，不覆盖现有文件。
```

### 最佳实践

- 小任务直接点名专项 Skill；跨角色、跨阶段、跨工具或高风险时，再让 `AI Native Engineering Loop` 先选最小流程。
- 先给目标、材料、边界、风险和验收；让 AI Native 输出 owner、交接物、授权策略和停止条件，再进入产品、架构、编码或验证。
- 产品事实不稳先找产品专家，工程边界不稳先找架构师，结构化代码骨架才找代码生成器；AI Native 不替代这些能力来源。
- 业务专家蒸馏只在资料足够、来源可追溯、能做 owner 追认时使用；否则先停在证据地图和待确认问题。
- 修改技能后先运行 `./scripts/validate.sh`；需要安装到 Codex 时先运行 `./sync-skills.sh --dry-run all`，确认目标目录后再正式同步。
- 不要把 AI 原生工具的产品宣传或历史文章能力描述当作当前会话可用工具、执行授权、合规结论或生产审批。

## 5 分钟上手

```bash
git clone https://github.com/fengwuxp/skills.git
cd skills

# 先预览，不写入 ~/.codex/skills
./sync-skills.sh --dry-run all

# 同步单个技能
./sync-skills.sh senior-software-architect

# 同步全部技能
./sync-skills.sh all

# 同步后重启 Codex 或开启新会话，再通过 $ 调用技能
```

仓库目录名可以自定义，不要求必须叫 `skills`。`sync-skills.sh` 会优先把脚本所在目录识别为技能仓库根，并同步同级的技能目录。

如需同步到非默认 Codex Home：

```bash
CODEX_HOME=/path/to/codex-home ./sync-skills.sh --dry-run all
CODEX_HOME=/path/to/codex-home ./sync-skills.sh all
```

## 验证与同步安全

修改技能、同步脚本或代码生成器后，建议执行统一验证：

```bash
./scripts/validate.sh
```

该脚本会检查：

- `sync-skills.sh` Bash 语法。
- Skill 脚本是否包含需要人工复核的高风险模式。
- `SKILL.md` frontmatter 和 `agents/openai.yaml` YAML。
- `SKILL.md` 中引用的 `references/` 文件是否存在。
- 架构师和产品专家关键触发路径、三级加载、reference 头部和核心门禁是否保持一致。
- `java-service-code-generator` Python 编译。
- DDL、Java 类、Markdown 字段表格三组代码生成 fixture。
- `sync-skills.sh --dry-run all`。
- `git diff --check` 空白问题。

`sync-skills.sh` 使用 `rsync --delete` 保持安装目录和仓库技能目录一致。正式同步前会备份已有目标技能目录到 `$CODEX_HOME/skills/.backups/`，但仍建议先执行 `--dry-run`，确认 `CODEX_HOME` 和目标技能列表正确。

不要把个人长期偏好、私有对话轨迹、客户资料、生产数据或敏感配置放在本仓库或安装后的技能目录中；技能同步可能删除安装目录里的额外文件。

## 维护者与高级扩展

### SkillX 导出规范

如需把 SkillX 或类似系统生成的规划技能、功能技能、原子技能转换为 Codex Skill Package，先按 [SkillX 到 Codex Skill Package 导出规范](./references/skillx-to-codex-skill-package.md) 做输入契约、安全门禁、三层映射、生成流程和验证流程审查。第一版只允许离线转换人工审查后的 JSON，不自动读取历史轨迹、不采集用户数据、不引入外部训练流水线，也不自动同步到 Codex。

离线候选包必须符合 `schemas/skillx-candidate.schema.json`，可用 `scripts/skillx_export_adapter.py` 生成可评审的 Skill 目录草案。生成结果会包含 `REVIEW.md` 和 `fixtures/trigger-prompts.md`，用于评审可用性、验证命令、待确认项和正负触发样例：

```bash
python3 scripts/skillx_export_adapter.py --check-input --input fixtures/skillx/sample-candidate.json
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out --dry-run
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out
python3 scripts/skillx_export_adapter.py --validate-output /tmp/skillx-out/skillx-product-reviewer --input fixtures/skillx/sample-candidate.json
```

### 外部参考来源

公开来源、读取状态和不吸收边界已迁入 [仓库级来源索引](./references/source-map.md)。README 只保留使用和维护入口；按技能细分的证据继续保存在各 Skill 的 `references/source-map.md`。

### Skill 自我改进外循环

Skill 改进分为内外循环：内循环按现有 Skill 执行真实任务；外循环基于脱敏后的执行记录、验证结果、CR 结论和人工反馈，生成最小 Skill 改进 diff。

进入外循环前先写 Skill Improvement Card：

```text
目标 Skill:
触发样例:
错误表现:
反馈证据:
最小修改位置:
验证方式:
不得吸收:
```

不得从单次失败泛化永久规则；不得把个人长期偏好、私有对话轨迹、客户资料、生产数据、密钥、外部文章原文、工具宣传或 Agent 自述写入仓库；不得自动提交、同步或发布。
- 未经用户确认，不应把 `Pending Observations` 提升为 `Confirmed Agreements`。

详细约定见 [AGENTS.md](./AGENTS.md)。
