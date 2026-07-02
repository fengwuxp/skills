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

- 产品语义 / PRD / Backlog / 验收：用 `产品架构专家`，先讲清用户/主体、目标、对象、流程、规则、验收和待确认项。
- 系分 / 架构 / 代码 / Bug / 测试 / CR / 发布：用 `资深架构师`，直接给源码锚点、现象、约束、验证命令和生产风险。
- 跨角色产研交付 / 目标拆解 / 任务计划 / Spec / Harness / 质量发布 / 知识生产闭环：用 `AI Native Engineering Loop`（`AI Native Engineering Workflow` 旧称也会路由到同一 Skill）。它默认进入角色协作 Loop，按设计、设计评审、TDD、编码、编码评审、可用性/安全性评估、验证发布和复盘回流分角色推进；目标层、计划层、原子执行层和执行契约是内部层，不替代 PRD、系分、代码或发布审批。
- Java Service 脚手架：用 `java-service-code-generator`，但必须有 DDL/schema/Java 类/字段表格、表名、模块和覆盖边界。
- 图形化交付：产品语义图用产品专家，工程架构图用架构师。复杂可编辑架构图、代码库结构转图或架构描述转图先由架构师判断 Architecture Diagram Generator 准入；复杂视觉续作再用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。
- 外部 Skill / 工具接入：先做供应链安全审查，再判断是否允许联网、安装、写配置或同步到 Codex。

### 3. AI Native 只做编排

`AI Native Engineering Loop` 是编排入口，不是万能执行入口。它回答“现在由谁做、交接什么、怎么验证、什么时候停”，产品正文交给 `产品架构专家`，工程实现交给 `资深架构师`。

默认先判断当前处于角色协作 Loop 的哪个阶段，再选最小场景视图：

- **只读理解视图**：阅读分析代码库、设计-代码对齐、工具准入、事实边界检查和影响范围识别；Gemini CLI 仅在本机可用、认证 / 读取范围获授权且当前状态核验通过时作为只读候选，失败则回退 Codex 内置工具，默认不写文件、不安装。
- **产研交付视图**：从产品事实、PRD/Spec、设计评审、TDD、编码、编码评审、可用性/安全性评估到生产发布和反馈回流，目标是交付真实、可验证、可接手的生产可用能力。
- **验证发布视图**：测试矩阵、质量门禁、CR 前置条件、失败回退、发布监控、残余风险和复盘。
- **知识回流视图**：把已验证经验沉淀到 Skill、reference、fixture、脚本、用户指南或 source-map；做技术早报、培训、代码库教程、调研沉淀时，可说“进入知识生产 Loop”，先把来源、业务背景、模板和历史坑点固化为上下文资产，再说明验收 owner、更新频率和停用条件。

AI Native 的默认最小输出只保留：结论、当前阶段、owner、交接物、授权策略、验证与停止条件；需要时补证据边界和残余风险。证据边界必须区分事实、推断、待确认和范围外不做；授权策略必须区分只读、计划内低风险执行、受控执行授权和显式确认。只有用户要求完整方案、评审报告或模板，才展开 Loop Contract、RACI、验证矩阵、Goal Ledger 或内部实现层。

角色协作阶段只是编排坐标，不是能力来源。AI Native 输出时必须写明能力来源：产品 / 交互设计和验收种子回到 `产品架构专家`；系分、TDD、编码、最小正确实现检查、CR、安全可靠和发布回到 `资深架构师`；结构化 Java Service 生成回到 `java-service-code-generator`。

轻量问询只服务 Ask-or-Decide：复杂或模糊任务一次只问一个关键问题，并给建议答案；能从材料、源码或测试自答的先自答，再把结论写入下一阶段输入。

角色协作 Loop 的处理步骤：

1. 识别目标、材料、写入边界、风险和验证要求。
2. 选择最小场景视图，并用 Ask-or-Decide 收敛缺口。
3. 分派能力来源：产品 / 交互回产品专家，系分、TDD、编码、CR 和发布回架构师，结构化代码生成回代码生成器；每个阶段都要写能力 / 约规来源。
4. 按 `意图 -> 产品/交互 -> 设计评审 -> TDD -> 编码 -> CR -> 质量评估 -> 验证发布 -> 复盘回流` 推进需要的阶段。
5. 任务结束责任闭环：阶段结束先自查交付、证据、残余风险和是否越界，再按 Ask-or-Decide 判断 Auto-Decide Next、Auto-Ask Owner、Auto-Loop 或 Stop-Handoff；需要继续时，只给下一任务计划问询或最小计划草案。

### 4. 产品到工程的默认闭环

产品发现由 `产品架构专家` 收束问题、对象、规则、验收种子和待确认项；编排准入由 AI Native 判断成熟度、owner、授权、门禁和停止条件；角色协作按阶段切换产品、架构、Maker、Checker 和人工 owner；工程执行由 `资深架构师` 承接系统设计、编码、TDD、源码级 CR 和发布风险；质量理解门禁负责测试、CR、影响范围和残余风险；交付复盘回看返工、缺陷、知识回流和停止条件。需要持续推进时，进入三卡交接：Product Context Card、Engineering Handoff Card 和 Production Loop Card；三卡都不是 Execution Grant、测试通过或上线审批。

### 5. 体用原则

先定体，再调度用。体：业务目标、用户/主体、生产边界、风险责任、验收标准和证据边界。用：Skill、工具、模板、图、代码、测试、提交和发布动作。体用合一，避免体用混一；阴阳互根，产品价值和工程约束互相校验；执简驭繁，小任务直接用专门 Skill，跨角色、跨阶段、跨工具或高风险任务再让 AI Native 编排。

### 6. 常用短句

- `先帮我选路`：判断应该用 AI Native、产品架构专家、资深架构师还是代码生成器；输出理由、缺口、下一步 owner 和停止条件。
- `进入角色协作 Loop`：AI Native 主入口，按设计、评审、TDD、编码、CR、质量评估、验证发布和复盘分角色推进。
- `按目标和任务计划推进`：用目标定义完成线，用任务计划拆阶段和提交切片；目标不等于执行授权，不要把目标当授权。
- `进入只读理解 Loop`：读代码库、对齐设计和代码、评估工具准入或做事实边界检查；默认不写文件、不联网、不安装。
- `做质量门禁`：输出测试矩阵、验证顺序、CR 前置条件、失败回退和残余风险交接。
- `请老祖宗做 CR`：用 Wisdom Lens 做取舍校准，输出严重级别、证据、残余风险和修复优先级，不替代事实、测试、CR 或授权。
- `初始化/更新项目 AGENTS.md`：让 AI Native 进入项目约规入口；需要启用 Wind 约规时，新项目生成本地 `AGENTS.md` 草案，已有文件只给最小 patch，规则权威回到 `wind-project-coding-conventions`。

### 7. 最小输入清单

- `AI Native 研发流程编排`：当前材料成熟度、目标产物、涉及 owner、写入/只读边界、授权策略、验证要求、是否需要目标拆解、任务计划、执行契约或工具准入。
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
- 内部路由：Spec/SDD、AI 代码交付闭环、架构排熵、Wisdom Lens、代码库知识图谱、Gemini CLI / AgentRC / Understand Anything / Ponytail 准入，都先回到角色协作 Loop 再判断。
- 常用说法：`进入角色协作 Loop`、`进入只读理解 Loop`、`做质量门禁`、`按目标和任务计划推进`、`评估 Gemini CLI / AgentRC / Understand Anything / Ponytail`。

### 产品架构专家

- 路径：[product-architecture-expert](./product-architecture-expert)。
- 适合：PRD、产品方案、需求说明、产品洞察/机会雷达、Backlog 决策、User Story/AC、概念生命周期、原型/HTML/页面截图/交互稿反推 PRD、能力地图、业务流程、状态机、规则矩阵、运营后台、数据指标、验收标准和产品架构图。
- 支付与资金是重点能力，覆盖账户/账本、清结算、对账、外卡收单、ACH、VCC、争议和跨境支付。
- 使用时说明：输入材料、目标产物、业务边界、评审重点、验证要求。交给 AI Native 或架构师前，最好形成 Product Context Card：业务目标、非目标、角色 / 主体、核心对象与状态、主流程与异常、关键规则、验收种子、风险与待确认项、专业确认方。
- 不适合：不替代法务、合规、财务、税务、持牌机构或卡组织规则确认；不负责工程实现、代码 Review 和生产排障。

### 资深架构师

- 路径：[senior-software-architect](./senior-software-architect)。
- 适合：架构设计、系统分析设计、技术方案、ADR、代码 Review、Bug 修复、测试/TDD、生产变更、架构图、遗留系统改造、架构腐朽 / 排熵 / 可删除性评审和工程治理。
- 使用时说明：代码或文档路径、现象/目标、运行环境、约束、期望验证命令、是否允许改代码或只做 CR。
- Wind/Nobe 风格项目如需统一 face/impl、基础服务、应用层服务、DTO/Request/Query/Entity、分包、MyBatis Flex 和外部集成规则，在项目 `AGENTS.md` opt-in “Wind 项目编码约规”，再用 `wind-project-coding-conventions` 作为规则权威；真实编码、TDD 和源码级 CR 仍由 `资深架构师` 承接。
- 不适合：不替代产品专家定义复杂业务语义、PRD 和金融产品规则；不在缺少边界、风险和验收时直接给可上线方案。

### Wind 项目编码约规

- 路径：[wind-project-coding-conventions](./wind-project-coding-conventions)。
- 适合：项目 `AGENTS.md` 已 opt-in Wind 约规后，判断 face/impl、服务分层、模型归位、Entity 不外露、ServiceImpl、MyBatis Flex 和 TDD/CR 是否符合项目约规；也可初始化或改进 Wind 项目本地 `AGENTS.md` 模板。
- 触发方式：新项目说“用 AI Native Engineering Loop 初始化项目 AGENTS.md，这个项目遵守 Wind 项目编码约规”；已有文件说“用 AI Native Engineering Loop 更新项目 AGENTS.md，这个项目已 opt-in Wind 约规，只做最小 patch”。需要直接查规则时，再说“用 `wind-project-coding-conventions` 检查 Wind 约规”。
- 边界：只做规则判断和偏差说明；真实编码、TDD、源码级 CR、Bug 修复和生产风险仍交给 `资深架构师`，结构化代码生成交给 `java-service-code-generator`。
- 不适合：未 opt-in 的普通 Java/Spring 项目，不强套 Wind 约规。

### java-service-code-generator

- 路径：[java-service-code-generator](./java-service-code-generator)。
- 适合：根据 DDL/SQL、Java 类、字段表格或 schema 生成 Wind/Nobe 风格 Java Service 配套代码，包括 Entity、Mapper、DTO、Request、Query、Converter、Service、ServiceImpl 和测试夹具。
- 使用时说明：DDL/schema/Java 类/字段表格、表名、业务模块、输出目录、是否允许覆盖已有文件。
- 不适合：不从纯自然语言直接生成生产代码；不替代架构师、DBA 或业务负责人确认表结构、索引、状态机和金额精度。

### 常见组合

- 从 AI 原型到工程化：AI Native 先进入角色协作 Loop，定义阶段、owner、门禁和验证矩阵；产品专家补产品上下文包、Backlog 和 PRD-Lite；架构师补 OpenSpec、Harness、测试策略、TDD、源码级 CR 和发布风险。
- 从想法到工程：产品专家先把目标、对象、流程、规则、验收和待确认项定清楚；架构师再承接系统设计、代码、测试和发布风险。
- 从 PRD 到代码生成：先由产品专家或架构师确认对象、状态、字段、索引和金额精度；已有 DDL、字段表格或 Java 类后，再用 `java-service-code-generator` 生成配套代码。
- 从普通图到复杂图：先由产品专家或架构师产出语义稳定的 SVG；需要复杂可编辑架构图、代码库结构转图或多层架构图时，再由架构师判断 Architecture Diagram Generator；需要精细视觉时再调用 `$fireworks-tech-graph`。
- 从金融产品到上线方案：产品专家先标出主体、法域、资金归属、外部规则和专业确认方；架构师再处理系统边界、数据一致性、可靠性、安全和发布回滚。

### 提示词示例

可直接复制这些示例；不需要同时塞满所有字段，关键是写清目标、材料、边界、风险和验证。

```text
用 AI Native Engineering Loop：按当前材料进入角色协作 Loop，只输出结论、当前阶段、owner、交接物、授权策略、验证与停止条件；需要时补证据边界和残余风险。

用产品架构专家梳理 VCC 发卡业务的产品架构，输出能力地图、核心对象、交易流程、资金流、风险和验收标准，默认 SVG 画图。

用资深架构师评审这个设计文档，重点看模块边界、数据一致性、可靠性、安全、测试和发布回滚，并给出 P0/P1/P2 问题。

用 wind-project-coding-conventions 检查这个已 opt-in Wind 约规的项目，重点看 face/impl、服务分层、模型归位、Entity 不外露、ServiceImpl 和 MyBatis Flex。

用 AI Native Engineering Loop 初始化项目 AGENTS.md：这个项目遵守 Wind 项目编码约规，请先读取项目结构和现有约束，只生成最小可用的根目录 AGENTS.md。

用 AI Native Engineering Loop 更新项目 AGENTS.md：这个项目已 opt-in Wind 约规，请只补项目约规入口、owner 路由、授权边界、验证命令和待确认事实，不重写已有规则。

用 java-service-code-generator 根据 docs/order.sql 生成订单模块配套代码，先输出到 /tmp/order-scaffold 评审目录，不覆盖现有文件。
```

### 最佳实践

- 提供背景、目标产物、范围边界、已知约束、风险等级和验收标准，比只说“优化一下”更容易得到可评审结果。
- 能用短句表达时，先让 `AI Native Engineering Loop` 判断最小流程；不要一开始就要求完整执行计划、完整 Harness 或大而全模板。
- 复杂金融产品通常先由产品专家产出对象、流程、规则和验收，再由架构师承接系统设计、代码、测试和发布。
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

- [智东西《Claude产品团队工作模式被公开了！》](https://zhidx.com/p/546178.html)、[Anthropic《Product development in the agentic era》](https://claude.com/blog/product-development-in-the-agentic-era)、[OpenAI Codex](https://openai.com/index/introducing-codex/)、[OpenAI《How OpenAI uses Codex》](https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf)、[GitHub Copilot coding agent](https://docs.github.com/en/copilot/concepts/about-copilot-coding-agent)、[GitHub Copilot code review](https://docs.github.com/en/copilot/concepts/agents/code-review)、[Google Gemini CLI](https://github.com/google-gemini/gemini-cli)、[Microsoft AgentRC](https://github.com/microsoft/agentrc)、[Egonex-AI Understand Anything](https://github.com/Egonex-AI/Understand-Anything)、[Microsoft Clarity Agent](https://github.com/microsoft/clarity-agent)、[Google People + AI Guidebook](https://pair.withgoogle.com/guidebook-v2/)、[NIST AI RMF Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)、[OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf)、[ISO/IEC 42001](https://www.iso.org/standard/81230.html)、微信文章 [《万字长文 | Spec 驱动开发实战：半年踩坑，我们如何让 AI 编码的交付真正闭环》](https://mp.weixin.qq.com/s/d1j7JCOkAFd5L-W1LK-Qug)、[《Spec 驱动开发：让 AI 知道该写什么，不该写什么》](https://mp.weixin.qq.com/s/VcITOOUVrw_BGxJQA_mtaw)、[《我们落地了 SDD，为什么团队效率没有体感提升？》](https://mp.weixin.qq.com/s/LEoZtLOyk-7qGY6Q-b7r2A)、[《终于有人开始解决 AI Coding 最大的问题了：看不懂代码》](https://mp.weixin.qq.com/s/JWtKELqDYvdPZtDzeJNybQ) 与 [《PRD 评审总返工？跟我把IPD的6个强角色、3个硬任务塞进你的Agent系统》](https://mp.weixin.qq.com/s/Q7jtu6Cihr0Fs0Fy1-USUg)：作为 `ai-native-engineering-workflow` 的公开参考来源，用于 AI 时代产品到研发编码流程、Agentic Engineering、AI 原型/eval、产品上下文、PRD/系分合议预审、OpenSpec/Harness/GSD/CAD、Spec/SDD 模板最佳实践、PRD / SDD / 实现 Spec 三层边界、AI 代码交付闭环、AI 原生工具权限边界、代码库知识图谱准入、质量/测试门禁、代码库理解结论包、变更可理解性/影响可视化门禁、验证矩阵、CR、发布复盘和 AI 风险治理。2026-06-04 微信原链接 `https://mp.weixin.qq.com/s/hRZ8zbkW4-PRyBYXn8bxbQ` 只读取到微信“环境异常”验证页，未作为已吸收来源；2026-06-04 已通过移动端微信 UA 公开 HTML 读取《终于有人开始解决 AI Coding 最大的问题了：看不懂代码》标题、作者、页面时间线索和正文；2026-06-05 普通 UA 读取《PRD 评审总返工？跟我把IPD的6个强角色、3个硬任务塞进你的Agent系统》返回微信验证页，随后通过移动端微信 UA 公开 HTML 读取标题、作者、账号、发布时间和正文；2026-06-06 `web.open` 未取得《万字长文 | Spec 驱动开发实战：半年踩坑，我们如何让 AI 编码的交付真正闭环》和《我们落地了 SDD，为什么团队效率没有体感提升？》正文，随后通过移动端微信 UA 公开 HTML 读取两篇标题、账号、页面时间字段和正文；2026-06-06 再次通过移动端微信 UA 读取并解析《万字长文 | Spec 驱动开发实战：半年踩坑，我们如何让 AI 编码的交付真正闭环》正文，用于补充 Spec 模板最佳实践；2026-06-08 普通 `web.open` 未取得《Spec 驱动开发：让 AI 知道该写什么，不该写什么》正文，普通 `curl` 返回微信验证页，本地 Node Playwright 包不可用且未新增依赖，随后通过本机 Chrome headless 等价浏览器读取标题、作者、页面时间字段和正文；2026-06-12 已读取 Egonex-AI Understand Anything 的 GitHub README 和仓库 metadata，用于补充大型代码库知识图谱、diff impact、onboarding、dashboard 和图谱提交边界。本仓库只吸收可迁移流程和边界，不复制文章正文、图示、案例、数据口径、厂商宣传、CrewAI/Codex/Claude 互调方式、Computer Use 做法、长 prompt、示例需求、外部 Harness 命令体系、目录结构、脚本、Understand Anything 插件/安装脚本/dashboard/hook 或作者表达，也不把历史工具能力、AI 快速阅读工具、外部可视化 CLI、上下文生成器、知识图谱工具、虚拟评审、文章推荐工具、外部 Harness 或单篇文章当成当前会话授权、默认依赖、正式评审、官方最新承诺或 Execution Grant。
- 微信文章 [《规范驱动开发（SDD）：用 AI 写生产级代码的完整指南》](https://mp.weixin.qq.com/s/SOonScQJ18GGVCD-t9PJWA)：作为 `ai-native-engineering-workflow` 的 SDD 生产代码门禁参考来源，用于 Spec 事实来源、结构化契约、正反例、五支柱验证、失败回写 Spec 重试环和生产级代码准出；2026-06-10 已通过移动端微信 UA 公开 HTML 读取标题、作者/账号、发布时间和正文。本仓库只吸收可迁移方法，不复制原文、示例 Auth 规范、工具清单、ROI / 效率数字、案例指标或作者表达，也不把文中工具能力写成当前会话默认依赖、最新事实或 Execution Grant。
- 微信文章 [《阿里内网万言离职书〈置身钉内〉原文，已刷屏》](https://mp.weixin.qq.com/s/_D20O0vpPXjSzjAKJmBYuA)：作为 `产品架构专家`、`AI Native 研发流程编排` 和 `资深架构师` 的公开转述/OCR 复盘参考来源，用于 AI 产品发心与定位、用户张力、真实工作流、AI 产品工程化准入卡，以及 AI 进入旧系统的 context 架构、权限与权力边界、技术债、多端一致性、成本稳定性和灰度止损门禁。2026-06-07 普通 `curl` 返回微信“环境异常”验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、账号、作者、发布时间和正文；页面正文声明内容由 AI 识图整理。本仓库只吸收可迁移反模式和门禁，不复制原文、项目细节、组织评价或作者表达，也不把它写成钉钉/ONE 官方事实、行业结论、当前工具能力或 Execution Grant。
- 微信文章 [《从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战》](https://mp.weixin.qq.com/s/HzbdrmNkT-OTRKdQh0c0Ug)：作为 `AI Native 研发流程编排`、`产品架构专家` 和 `资深架构师` 的公开参考来源，用于模糊需求到结构化需求文档、业务流、原型/页面说明、开发任务和验收发布路径的系统组织链路。2026-06-07 普通 `curl` / `web.open` 未取得正文或返回微信验证页，随后通过移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文，作者/账号字段为 `KEEN的创享`。本仓库只吸收可迁移方法和交接门禁，不复制原文、项目案例、页面设计、图片、提示词或作者表达，也不把示例项目写成通用模板、当前工程事实或执行授权。
- 微信文章 [《架构30：架构思维：需求分析》](https://mp.weixin.qq.com/s/B8Rap_MmAKmVN3f7eAnvCw)：作为 `AI Native 研发流程编排`、`产品架构专家` 和 `资深架构师` 的公开参考来源，用于需求分析协同门禁、根源需求、产品定义、产品边界、上下游分工、稳定点 / 变化点、边界坐标、PRD / 系分预审和 GSD Round 0。作者字段为 `开心就好TF`，页面时间字段为 2026-06-07 09:34:00 Asia/Shanghai；2026-06-09 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文（发布时间取页面时间字段）。本仓库只吸收可迁移方法和门禁，不复制原文、案例、作者表达、标题传播话术或时间投入比例，也不把单篇文章观点写成组织制度、项目事实、执行授权或架构师必须越过产品 owner 的理由。
- 微信文章 [《[013] 标准不是摆设——需求标准、设计标准、编码标准怎么写》](https://mp.weixin.qq.com/s/W44YHT-9bUCrSjsrZIYItw) 与 [《[014] 85%返工都是需求的锅——为啥说需求是软件的根本》](https://mp.weixin.qq.com/s/MO8EsLHm9QNauNLDQ1Z05Q)：作为 `AI Native 研发流程编排`、`产品架构专家` 和 `资深架构师` 的公开参考来源，用于需求基线稳定性、需求标准、设计标准、编码标准、HLR/LLR 分工、图文追踪、衍生需求、需求驱动测试、防御式编程和标准可执行性门禁。作者/账号字段为 `AIIIIlIIII`；页面时间字段分别为 2026-05-23 07:24:00 与 2026-05-26 06:21:00 Asia/Shanghai；2026-06-09 首篇 `web.open` 未取得正文，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。本仓库只吸收可迁移门禁，不复制原文、适航/DO-178C 语境、标题比例、案例、作者表达或标准条文，也不把单篇文章写成通用合规结论、项目制度或 Execution Grant。
- 微信文章 [《软件工程最大的 Bug：我们把系统生长顺序做反了》](https://mp.weixin.qq.com/s/YM0BI6tCXLpwEf8hZuYvYA) 与 [《为什么优秀架构越来越像生命？》](https://mp.weixin.qq.com/s/95YFNicYQnDRt9SZHrpKnQ)：作为 `AI Native 研发流程编排`、`产品架构专家` 和 `资深架构师` 的公开参考来源，用于产品 / 系统 DNA 门禁、核心不变量、状态流转、责任边界、演化规则、验证方式、事故沉淀式架构、复杂系统分化、事件驱动协作、可恢复、可观测和自治/协作平衡。作者/账号字段为 `霍旭东` / `ThinkingInDev`；页面时间字段分别为 2026-06-08 20:19:14 与 2026-06-09 07:00:00 Asia/Shanghai；2026-06-11 首篇 `web.open` 未取得正文，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。本仓库只吸收可迁移门禁和检查项，不复制原文、图片、比喻、标题传播话术、作者表达或“数字生命”推测，也不把文章观点写成组织制度、项目事实、技术选型结论、执行授权或 AI 自主扩大范围的理由。
- 微信文章 [《所有的技术架构，本质上都是业务架构》](https://mp.weixin.qq.com/s/4mOd-ZbtE-J6O-aDPOSUQg) 与 [《兑现那个问题“产品需要做什么”》](https://mp.weixin.qq.com/s/dHXUnZI6rVGYqpyqPnjo4w)：作为 `产品架构专家`、`资深架构师` 和 `AI Native 研发流程编排` 的业务 / 产品 / 技术交叉准入参考来源，用于业务同质性、价值函数、成本函数、主要矛盾、技术平台不是产品、架构复用必须降低业务复制成本和产品任务到开发语言转译。2026-06-11 首篇通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文；第二篇普通 `curl` 返回微信验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文；作者字段均为 `大象无棱`，页面时间字段分别为 2026-04-25 09:32 与 2026-06-10 09:11 Asia/Shanghai。本仓库只吸收可迁移门禁，不复制原文、故事经历、比喻、图片或作者表达，也不把文章观点写成组织制度、客户事实、合规结论、架构批准或 Execution Grant。
- 微信文章 [《欲读经典，先开心门》](https://mp.weixin.qq.com/s/qWIVEdD5uSLAQXP7nh1ckA)、[《产品的创新｜需求是无止境的吗？》](https://mp.weixin.qq.com/s/ld3ZqgNL_wJcOCUQz6em2Q)、[《一阖一辟谓之变，往来不穷谓之通｜变通》](https://mp.weixin.qq.com/s/H6dCG9d_RTBHLlKKtMse_Q) 与 [《如何抓住问题的核心？》](https://mp.weixin.qq.com/s/AMdz3s4GEPDgNibPlq8_2g)：作为 `AI Native 研发流程编排`、`产品架构专家` 和 `资深架构师` 的公开参考来源，用于问题核心诊断、反脑补证据边界、概念定名、需求止损、价值 / 意义边界、定向 / 定性 / 定位 / 定量变化治理、整体 / 系统 / 科学三层诊断和“病 / 证 / 症”式工程问题分层。页面账号字段为 `心性之学`，后三篇作者字段为 `复闲`；页面时间字段分别为 2025-11-21 10:23:51、2025-01-09 05:02:37、2025-05-06 02:29:50、2025-12-19 19:13:26 Asia/Shanghai；2026-06-12 通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者线索、页面时间字段和正文 / meta 正文。本仓库只吸收可迁移的方法和边界，不复制原文、经典引文、医学/文化论断、作者表达、图片、标题传播话术或个人修习语境，也不把传统文化或医学观点写成产品事实、架构结论、合规结论、生产审批或 Execution Grant。
- 微信文章 [《重磅！Anthropic内部Skills经验公开了！》](https://mp.weixin.qq.com/s/FCKdRHxi9c6Vby2ZRKjVTw)：作为仓库级 Skill 治理和 `AI Native 研发流程编排` 的公开转述参考来源，用于 Skill 类型接入门禁、渐进式加载、gotchas 优先、验证优先、脚本化复用、setup 缺口、组合边界和高风险 guardrail。作者字段为 `Datawhale`，正文标注作者 `Anthropic团队`，页面时间字段为 2026-06-07 22:03:28 Asia/Shanghai；2026-06-11 通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者、发布时间和正文。本仓库只吸收可迁移 Skill 资产治理方法和类型分类，不复制原文、图片、内部案例细节、Claude Code 专用变量、hooks、marketplace、usage measurement 机制或作者表达，也不把 Anthropic 内部做法写成 Codex 当前能力、组织制度、执行授权、默认持久化记忆或默认外部插件机制。
- 微信文章 [《设计一个好 Skill，通用方法论》](https://mp.weixin.qq.com/s/KEDcjuDFFAeeL0iqsHejIQ)：作为仓库级 Skill 质量治理和 `AI Native 研发流程编排` metadata 瘦身的公开参考来源，用于单一职责、description 触发准确性、指令可验证、避免冲突、上下文窗口节制、渐进式加载、何时使用、迭代测试和把 Skill 当代码管理；2026-06-11 已通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、页面时间字段和正文，账号字段为 `雅东Talk`，页面时间字段为 2026-06-10 18:00:00 Asia/Shanghai（UTC 2026-06-10 10:00:00）。本仓库只吸收可迁移的设计质量标准和 advisory audit 思路，不复制原文、图片、案例、作者表达或平台宣传，也不把单篇文章写成新增顶层 Skill、硬性行数失败、自动安装外部工具或执行授权。
- 微信文章 [《Harness 工程之道：Skill 原理与最佳实践》](https://mp.weixin.qq.com/s/yo2f5edeNNkYtCte9P0yhQ)：作为仓库级 Skill 反向验证和 `AI Native 研发流程编排` 工程化参考来源，用于渐进性披露、`SKILL.md` 路由器、description 触发、资源加载契约、工具权限最小化、脚本确定性、状态快照、触发测试、功能走查和性能对比；作者字段为 `张梦杰`，账号字段为 `阿里云开发者`，页面 `ct` 字段换算为 2026-07-01 08:30:00 Asia/Shanghai；2026-07-01 普通 `curl` 返回微信“环境异常”验证页，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者、页面时间字段和正文。本仓库只吸收可迁移 Skill 工程化方法和验证维度，不复制原文、图片、案例、Claude Code 专用 frontmatter、allowed-tools、hooks、user-prefs、日志埋点、自动 git push、skill-creator 操作口吻或平台宣传，也不把外部机制写成当前 Codex 默认能力、执行授权、测试通过、CR 结论或上线审批。
- [obra/superpowers](https://github.com/obra/superpowers)：作为 `ai-native-engineering-workflow` 的外部 skills library 参考来源，用于 brainstorming、writing-plans、executing-plans、subagent-driven-development、test-driven-development、requesting-code-review、receiving-code-review、systematic-debugging、verification-before-completion、using-git-worktrees、finishing-a-development-branch 和 writing-skills 等工程纪律调度。2026-06-07 已通过 GitHub API 读取 skills 目录和 README，下载 main.zip 到临时目录并审查 LICENSE、scripts、hooks 和 plugin manifest；main commit 为 `6fd4507659784c351abbd2bc264c7162cfd386dc`，zip SHA256 为 `ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3`，许可证为 MIT。初始导入只复制 Markdown skill 资源和 LICENSE 到 `ai-native-engineering-workflow/references/external-superpowers/`，并通过 `superpowers-skill-library.md` 做按需调度；2026-06-30 仅对 `subagent-driven-development` 做 v6.0.3 替换覆盖式升级并纳入本地 helper；2026-07-01 核验上游 latest 已到 v6.1.0，但本仓库暂不覆盖本地 SDD helper；除此之外不复制或运行 hooks、插件 manifest、package 脚本、安装流程、图片资产或跨平台启动方式，也不把外部默认文档路径、自动提交、Git 推送、worktree、subagent 连续执行要求写成本仓库默认行为。
- [obra/superpowers v6.0.3](https://github.com/obra/superpowers/releases/tag/v6.0.3)：2026-06-30 已通过 GitHub Releases API 核验 release，并读取 v6.0.0 release 的 SDD 套件变化；随后对 `external-superpowers/subagent-driven-development` 做替换覆盖式升级，纳入 `task-reviewer-prompt.md` 单一评审、pre-flight plan review、文件化 handoff、progress ledger、final broad review、model/cost policy 以及 `task-brief` / `review-package` / `sdd-workspace` 本地 helper，并将 AI Native 内部 Harness 契约升级为 v3。其他 Superpowers skill 保持原基线；不复制 visual companion server、hooks、插件 manifest 或安装脚本，也不默认运行 helper 或创建 `.superpowers/sdd/`。
- [obra/superpowers v6.1.0](https://github.com/obra/superpowers/releases/tag/v6.1.0)：2026-07-01 已通过 GitHub Releases API 核验为上游 latest，发布于 2026-06-30；本仓库只记录其降低 bootstrap token 成本、Codex marketplace manifest、移除 Codex SessionStart hook 和移除 Gemini CLI 支持等工具准入影响，不把它写成本地已覆盖升级、默认安装、默认运行外部脚本、测试通过或执行授权。
- [yizhiyanhua-ai/fireworks-tech-graph](https://github.com/yizhiyanhua-ai/fireworks-tech-graph)：作为图形化 Skill 产品化、风格系统、语义形状/箭头、模板化、fixture 化、SVG 导出和渲染校验思路的公开参考来源。本仓库只吸收通用方法，不默认复制外部脚本、模板、图形资产或安装流程；PNG/PDF/截图等派生格式只在使用者明确提出时处理；引入外部可执行内容前必须按 `AGENTS.md` 做供应链安全审查。
- [google/eng-practices](https://github.com/google/eng-practices)：作为 `资深架构师` 代码评审标准、评论分级、变更颗粒度、作者/评审者协作和持续改善代码健康的公开参考来源。本仓库只吸收可迁移的 Review 与 Change Author 原则，不把它扩展为完整架构设计方法论；复用具体文本、示例或派生产物时必须保留来源、确认 CC-BY 3.0 归因要求并避免复制大段原文。
- [Ivy-piger/Ivy-skills](https://github.com/Ivy-piger/Ivy-skills)：作为架构师陌生代码库侦察、Java 架构坏味启发式扫描、生产故障时间线、5-Why 复盘草稿和 Spring Boot 安全检查清单的公开参考来源。本仓库只吸收可复用流程和检查项，不安装或复制 Claude Code 专用 frontmatter、`CLAUDE.md` 流程、外部脚本或服务端运行逻辑；如需复用具体文本、脚本或资产，必须保留来源、确认许可证并执行供应链安全审查。
- [cg0x-skills/cg0x-frame-analysis](https://github.com/cg0x-skills/cg0x-frame-analysis)：作为探索期反路径锁定、多框架分析、假设/盲区/失败条件自检的公开参考来源。本仓库只吸收通用方法到产品专家和架构师 reference，不引入 `alwaysApply`、`/on` `/off` 开关、单文件长 Skill 或默认不收敛的交付方式；复杂问题先展开问题地图，正式交付仍必须回到可评审、可验证、可验收的产物。
- [zjunlp/SkillX](https://github.com/zjunlp/SkillX) 与论文 [SkillX: Automatically Constructing Skill Knowledge Bases for Agents](https://arxiv.org/abs/2604.04804)：作为从 Agent 执行轨迹提炼规划技能、功能技能、原子技能，迭代精炼、合并过滤和探索扩展技能知识库的公开参考来源。本仓库只吸收“经验分层、过滤噪音、合并重复、工具约束和失败模式进入确定性验证”的方法，不引入自动读取历史轨迹、自动学习用户数据、外部训练流水线或未审查代码。
- 微信文章 [《Loop Engineering：让 AI 自己跑起来，你只管验收》](https://mp.weixin.qq.com/s/Ng_qit1H5t6yhqjVGNIHzg)：作为 `ai-native-engineering-workflow` 的意图到生产交付角色 Loop 和 Agent Loop Engineering 参考来源，用于 Automations、Worktrees、Skills、Connectors、Sub-agents、State、Maker / Checker 分离、状态落盘、人类验收、理解债和认知外包风险。2026-06-17 普通 `curl` 返回微信“环境异常”验证页，随后通过移动端微信 UA 公开 HTML 读取标题、作者/账号、meta 描述和正文；作者/账号字段为 `算法屋`，页面时间字段为 2026-06-11 08:00:00 Asia/Shanghai。本仓库只吸收可迁移方法，不复制原文、表格、比喻、引用表达、案例细节、作者口吻或标题传播话术，也不把 `/goal`、定时器、连接器、自动开 PR、sub-agent、worktree 或任何工具能力写成当前会话默认可用、默认授权、测试通过、CR 结论、合并判断或上线审批。
- 微信文章 [《Loop Engineering又是啥？一文讲清企业Agent落地的四层工程进化论》](https://mp.weixin.qq.com/s/3Zbx4RHB4fOdomI5aA_wIQ)：作为 `ai-native-engineering-workflow` 的 L1-L4 工程成熟度诊断参考来源，用于 Prompt / Context / Harness / Loop 四层嵌套、Agent 生产不稳分层诊断、L3 优先加固、最小 L4 试点、成本预算、组合可靠性和理解债 / 认知投降风险。作者字段为 `李伟山`，账号字段为 `腾讯云开发者`，页面 `ct` 字段换算为 2026-07-02 08:45:00 Asia/Shanghai；2026-07-02 普通 UA 返回微信“环境异常”验证页，本地 Playwright 浏览器缺失且系统 Chrome 受限，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、账号、页面时间字段和正文。本仓库只吸收可迁移诊断框架，不复制原文、图示、案例、模型/工具宣传、作者表达或标题传播话术，也不把单篇文章写成默认授权、工具能力、测试通过、CR 结论或上线审批。
- 微信文章 [《【译】别再手动写 Prompt 了，去写 Loop——但 Loop 到底是什么？》](https://mp.weixin.qq.com/s/cxRvqwWW4Yo4UmufAsXEEA)：作为 `ai-native-engineering-workflow` 的 Agent Loop Engineering 参考来源，用于 Loop 准入、GSD + Goal + Loop、状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件、反馈自检和 Skill 作为复用单位；2026-06-11 已通过移动端微信 UA 公开 HTML 读取标题、账号、页面时间字段和正文，页面时间字段为 2026-06-09 21:13:56 Asia/Shanghai。本仓库只吸收可迁移方法，不复制原文、推文、图片、成本数字、工具宣传、作者表达、命令示例或标题传播话术，也不把 `/goal`、`/loop`、auto mode、后台 Agent 或任一工具能力写成当前会话默认能力、最新事实、执行授权或上线审批。
- 微信文章 [《Loop Engineering（Agent 闭环工程）》](https://mp.weixin.qq.com/s/mbjdMlSTqQG1EptOGoo6og)：作为 `ai-native-engineering-workflow` 的生产可用 Loop 门禁参考来源，用于自动化心跳、隔离 worktree、Skill 上下文、连接器权限、Maker / Checker 解耦、状态持久化、质量卡口、成本预算、观测审计、人工接管、发布/回滚和理解债控制；2026-06-12 已通过移动端微信 UA 公开 HTML 读取标题、作者、账号、页面时间字段和正文。本仓库只吸收可迁移门禁，不复制原文、工具宣传、示例 Prompt 或命令，也不把 `/goal`、`/loop`、Automations、Worktrees、Connectors、Sub-agents 或任何当前工具能力写成默认可用、默认授权、测试通过、CR 结论、合并判断或上线审批。
- 微信文章 [《深度思考：架构腐朽 & Loop Engineering》](https://mp.weixin.qq.com/s/wINKSDQCroWBvf29h567zA)：作为 `ai-native-engineering-workflow`、`资深架构师` 和 `产品架构专家` 的架构排熵、可删除性、概念生命周期和治理自检参考来源。2026-06-17 `web.open` 未取得正文，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者/账号、meta 描述和正文；作者字段为 `lencx`，账号字段为 `浮之静`。2026-06-22 再次通过移动端微信 UA 读取公开 HTML，补充吸收“架构规则 = 可执行约束 x 可追溯理由链”、时间边界三问、复杂度棘轮、熵增仪表、理由保鲜、非对称稳定性和概念退场机制。本仓库只吸收持续排熵、可删除性、承重行为、概念膨胀、规则外置、Maker / Checker、Memory、守卫自检、人工 triage 和时间边界等可迁移门禁，不复制原文、图片、比喻、作者表达或标题传播话术，也不把自动扫描写成可以自动删除、迁移、重写、合并、测试通过、CR 结论、执行授权或上线审批。
- Gitee 仓库 [aiami/huaxia-wisdom](https://gitee.com/aiami/huaxia-wisdom.git)：作为 `ai-native-engineering-workflow` 的 Loop 取舍校准 / Wisdom Lens 参考来源，用于 Loop 准入、GSD 拆解、执行核验、授权纠偏和复盘回流中的取舍、止损、节奏和反偏判断。2026-06-16 已安装到本地 Codex 技能目录并读取 `SKILL.md` 与各 reference，安装时 HEAD 为 `eef49d54e6266b1afc568ef591a6a2d4abd5ad8e`。本仓库只吸收工程化判断映射，不复制原文、示例、口吻或经典表达，不默认切换成文化化输出，也不把传统智慧框架写成事实证据、项目制度、Execution Grant、测试通过、CR 结论、Git 授权或上线审批。
- 微信文章 [《一个让Codex变得越来越聪明的小方法》](https://mp.weixin.qq.com/s/G-tZjkhAd_yMAABBgNGVdw)：作为 `ai-native-engineering-workflow` 经验归位和知识回流的公开参考来源。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `Dr.Joyi`，既有账号线索保留 `像素与咖啡时光`，页面时间字段为 2026-06-04；本仓库只吸收“反复踩坑来自稳定上下文缺失，执行经验和项目知识要进入合适载体”的可迁移方法，不复制原文、个人经历、提示词或作者口吻，也不把个人长期偏好写入仓库或安装目录。
- 微信文章 [《如何为你的 Skills 构建自我改进循环》](https://mp.weixin.qq.com/s/nMLDamB1Esj5UoGQQ68LKQ)：作为 `ai-native-engineering-workflow` Skill 自我改进外循环和知识回流的公开参考来源。2026-06-23 普通 `curl` 返回微信环境异常验证页，随后通过移动端微信 UA 公开 HTML 读取标题、页面时间字段和正文。本仓库只吸收“内循环执行 Skill，外循环按执行记录和人工反馈审查并生成最小 Skill 改进 diff”的可迁移方法，落实到 `AGENTS.md`、`code-delivery-closed-loop.md` 和本 README；不复制原文、图片、案例、平台实现或作者表达，也不把外循环写成自动提交、自动同步、读取私有轨迹或个人记忆机制。
- 微信文章 [《有人把 5.7 万星 OpenSpec 和 24 万星 Superpowers 融合成一个工作流在 Github 开源......》](https://mp.weixin.qq.com/s/FpaEpKeP1hpz9B-tHEDfOA)：作为 `ai-native-engineering-workflow` 执行契约、状态机流转、Delta Spec 和漂移检查的公开参考来源。2026-06-30 通过移动端微信 UA 公开 HTML 读取标题、账号和正文；本仓库只吸收可迁移门禁，不安装 spec-superflow，不复制命令、目录、模板或工具宣传。
- 微信文章 [《Spec-First：每次 AI coding 的经验，都不应该消失》](https://mp.weixin.qq.com/s/LWEnocPanF-ekAFPncZDDw)：作为 `ai-native-engineering-workflow` Knowledge Harness 和任务收口经验沉淀的公开参考来源。2026-06-30 通过移动端微信 UA 公开 HTML 读取标题、账号和正文；本仓库只吸收症状、根因、解决方案、预防策略、适用条件和验证证据的最小经验卡方法，不默认新建 `docs/solutions/`，不复制原文、目录结构或触发器。
- 微信文章 [《架构8：架构设计三原则》](https://mp.weixin.qq.com/s/wc3xeSbBqb6ktEDz2ZuK7g)：作为 `资深架构师` 合适、简单、演化三类架构评审原则的公开参考来源。2026-05-28 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收当前约束匹配、结构/逻辑复杂度评估和演进式设计门禁，不复制文章案例、代码示例、图片或作者表达。
- 微信文章 [《认知跃迁16-如何练成架构设计真功夫》](https://mp.weixin.qq.com/s/6EFJZpH39ryWA3u_Wlxuzw)：作为 `ai-native-engineering-workflow` 和 `资深架构师` 的小闭环 Ask-or-Decide、架构角色分工协作、拆分 / 合并 V 字判断、稳定元素 / 变化关系和长期交付成本判断参考来源。2026-06-25 普通 `curl` 返回微信环境异常验证页，`web.open` 未取得正文，Playwright 通道受限，随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间字段和正文；作者字段为 `李文强`，页面 `ct` 字段换算为 2026-06-03 15:54:27 Asia/Shanghai。本仓库只吸收可迁移门禁和检查项，不复制原文、案例、作者表达或标题传播话术，也不把微服务、SOA、EDA、中台或任一架构形态写成默认答案、执行授权、测试通过、CR 结论或上线审批。
- 微信文章 [《「架构杂记」设计模式的本质——“找到变化，封装变化”》](https://mp.weixin.qq.com/s/oD70wjPWzikEQjBtR6XUJQ)：作为 `AI Native 研发流程编排`、`产品架构专家`、`资深架构师` 和 `wind-project-coding-conventions` 的设计 / CR 原则参考来源，用于真实变化轴、稳定边界、职责分离、依赖倒置、设计模式准入和过度设计防线。作者字段为 `xl杂记`，页面 `ct` 字段换算为 2026-05-27 00:15:08 Asia/Shanghai；2026-07-01 通过移动端微信 UA 公开 HTML 读取标题、作者、meta 描述、页面时间字段和正文。本仓库只吸收“先识别真实变化，再封装到稳定边界后面”的可迁移原则，不复制原文、示例代码、比喻、标题传播话术或作者表达，也不把策略、工厂、状态机、规则引擎、接口隔离或依赖倒置写成默认答案、执行授权、测试通过、CR 结论或上线审批。
- 微信文章 [《架构师底层思维能力要求-这7种尽早练习》](https://mp.weixin.qq.com/s/Veb3P2ug8XVmyBFmIoDJ7Q)：作为 `资深架构师` 抽象、逻辑、结构化、批判、成长型、复盘和数据思维的公开参考来源。2026-05-28 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收底层思维能力框架、架构判断落点和常见误区，不复制原文图片、推荐书目、排版结构或作者表达。
- 微信文章 [《软件复杂性的本质是通信复杂性》](https://mp.weixin.qq.com/s/1MbijKDxD2B4wa1E9QTnAw)：作为 `资深架构师` 通信复杂度、节点/边/状态传播、抽象隐藏边、复杂度转移检查，以及业务驱动架构/TDD 桥接的公开参考来源。2026-05-29 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收架构评审、业务验证、测试资产和图形检查项，不复制原文、SVG 插图、产品对比或作者表达，也不把通信复杂度绝对化为唯一复杂度来源。
- 微信文章 [《软件设计的哲学》：复杂性的本质与模块化设计](https://mp.weixin.qq.com/s/gXhOwvKH5t6BxsxcoqUS2w) 与 [《软件设计的哲学》：实践智慧与超越代码的哲学](https://mp.weixin.qq.com/s/J9d5Ws6rIdsATPbT-UutAA)：作为 `资深架构师` 和 `AI Native Engineering Loop` 的复杂性治理、深模块/浅模块、信息隐藏、设计两次、错误处理聚合、注释命名意图表达、AI 战术化编码风险和 TDD 后设计质量回看的公开参考来源。作者字段为 `南山斯帕克`，账号字段为 `深安斯帕克`，页面时间字段分别为 2026-06-22 10:38:07 与 2026-06-23 07:47:00 Asia/Shanghai；2026-06-23 已通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、账号、发布时间和正文。本仓库只吸收可迁移原则、门禁和检查项，不复制原文、书籍内容、案例、作者表达或标题传播话术，也不把读书笔记写成官方标准、执行授权、测试通过、CR 结论或 AI 自动扩大范围的理由。
- 微信文章 [《Clean Architecture 整洁架构》](https://mp.weixin.qq.com/s/7zj5v-B_-fClCYyR3SnMLA)：作为 `资深架构师` Clean Architecture 依赖规则、依赖反转、业务规则/用例规则分离和可测试性诊断的公开参考来源。2026-06-03 已通过移动端微信 UA 公开 HTML 读取标题、账号、发布时间和正文；本仓库只吸收源代码依赖方向、端口位置、adapter 边界和不启动数据库/Web 容器/真实 SDK 的核心业务测试诊断，不复制原文、图示、比喻、表格或作者表达，也不把 Clean Architecture 固化为必须四层或固定目录模板。
- 微信文章 [《用了 DDD 还是写不好业务代码？因为你把它当成了架构模式》](https://mp.weixin.qq.com/s/3A5SAp1Dzw8s3sECM2SNhQ)、[《7 条开发原则你都知道，但一条都用不对》](https://mp.weixin.qq.com/s/zJphqS80r3fg_wLXHaFmHQ) 与 [《学了那么多软件架构，现实工作我们该怎么权衡》](https://mp.weixin.qq.com/s/e1ft2s2Js8K0Zaw6PNfYMQ)：作为 `资深架构师` DDD 战略/战术分层、开发原则判断框架和架构风格取舍框架的公开参考来源。2026-06-03 已通过移动端微信 UA 公开 HTML 读取三篇文章标题、账号、作者、发布时间和正文；本仓库只吸收通用语言、限界上下文、上下文映射、原则冲突判断、架构族收益/代价/前置条件和 CR 检查项，不复制原文、表格、代码示例、参考资料列表、图示、标题传播话术或作者表达，也不把 DDD、Clean、微服务、CQRS、Event Sourcing、12-Factor 或 Reactive 写成默认架构套餐。
- 微信文章 [《架构师必备--让AI画架构图》](https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg)：作为 `资深架构师` 与 `产品架构专家` AI 辅助可编辑画图、文档转图、draw.io XML、版本历史和本地模型/凭据边界的公开参考来源。2026-06-01 已通过公开 HTML 读取标题、账号、作者、发布时间和正文，并尝试本机 Chrome headless 等价浏览器；本仓库只吸收可迁移的图形 brief、可编辑源文件、人工校验、权限和敏感信息边界，不复制示例图、提示词、项目安装说明或工具宣传语。
- 微信文章 [《如何让 AI 画出高质量架构图，一个Skill搞定》](https://mp.weixin.qq.com/s/tE0kfJ2ZHeGGz6xCgEp3Zg)：作为 `资深架构师` 和 `AI Native 研发流程编排` 陌生代码库图形化理解、架构描述转图和理解门禁的公开参考来源。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `Davon Dong`，既有账号线索保留 `日积月码`，页面时间字段为 2026-05-12；本仓库只吸收先分析代码库形成架构描述、再生成可编辑架构图、并通过组件/连接关系迭代校验的工作法，不安装文中提到的外部 Skill，不复制安装指令、示例提示词、截图、模板、工具宣传语或作者表达。
- 微信文章 [《让AI编程从"越写越烂"到"持续稳定输出"：GSD工作流-适合中大型项目的精准框架。》](https://mp.weixin.qq.com/s/VA_GhniSSrcJotXWlgk_lw)：作为 `资深架构师` 中大型 AI 编码流程治理、上下文衰减、阶段状态、多 Agent 编排、Wave 依赖、原子可追溯和 Git 版本化意识的公开参考来源。2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、作者/账号、发布时间和正文；本仓库只吸收持久化上下文、阶段循环、交接验证和轻重流程选择，不复制 GSD 命令体系、文件模板、XML 示例、动图、截图、工具宣传语或作者表达，也不把自动提交视为默认授权。
- 微信文章 [《Codex 官方团队：如何把 Codex 用到极致》](https://mp.weixin.qq.com/s/6t8hu_XU48jC3T-fc_B5FQ)：作为 `资深架构师` Codex 运行时协作、durable thread、voice/transcript、steering/queuing、tool reach、automation/goal、side panel/artifact 和 shared written context 的公开参考来源。2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、公众号、作者、发布时间内嵌元数据和正文；本仓库只吸收持续工作流治理、可验证 goal、显式上下文和权限边界，不复制示例、提示语、目录结构、平台宣传语或作者表达，也不把平台功能当成默认工具可用性或执行授权；涉及 Codex 当前产品能力、模型、工具可用性或官方承诺时，仍必须核验 OpenAI 官方文档或当前会话工具状态。
- 微信文章 [《放下代码：AI Native是通往架构师的快车道》](https://mp.weixin.qq.com/s/fhEzrPbeez-_2bmJHqExCQ)：作为 `资深架构师` AI Native 架构师角色升级、hardened 标准、Agent 工作流设计、系统判断和技术战略职责的公开参考来源。2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、账号、发布时间和正文；本仓库只吸收架构师从逐行实现转向系统边界、质量门禁、验证矩阵和 Agent 编排的可迁移方法，不复制原文、引用案例、播客转述、作者表达或岗位评价。
- 微信文章 [《放下 PRD：写给AI Native时代的产品经理朋友们》](https://mp.weixin.qq.com/s/5TEAxFYueNc6MD5ngKEgGg)：作为 `产品架构专家` AI Native Product Builder、业务 owner + Agent、业务 dogfooding、MVP/原型 harden 和 PRD 可执行上下文的公开参考来源。2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、账号、发布时间和正文；本仓库只吸收 PRD 从静态翻译文档升级为上下文包、验收种子和工程交接门禁的可迁移方法，不复制原文、作者判断、传播性措辞或岗位评价，也不把“放下 PRD”理解为跳过产品语义、评审、留痕、合规和验收。
- 微信文章 [《需求分析和设计活动关键要点总结》](https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q)：作为 `资深架构师` 与 `产品架构专家` 功能定义、功能分配追溯、需求分析外部视角和设计内部视角分工的公开参考来源。2026-06-01 已通过移动端微信 UA 公开 HTML 和本机 Chrome headless 读取标题、账号、作者、发布时间和正文；本仓库只吸收功能不是头脑风暴清单、功能来自上层对象分配、正逆追溯和需求/设计分工检查项，不复制原文推荐书目、GJB 章节表述、课程/书籍引导或作者表达。
- 微信文章 [《如何评估你写的 SKILL.md 质量？一套完整的 Eval 方法论》](https://mp.weixin.qq.com/s/JWz6EscFlcDeHhTjsDybgg)：作为 Skill Eval 触发准确率、输出质量、效率指标、真实 prompt、难负例、对照实验和方差检查的公开参考来源。2026-05-28 已通过浏览器自动化读取标题、账号、作者、发布时间和正文；本仓库只吸收评估方法、prompt fixture 结构和离线校验边界，不复制文章原文、策略案例、社群引导或未逐篇读取的外部链接。
- 微信文章 [《产品经理别再只让 AI 写 PRD 了，先把用户反馈整理成一张问题地图》](https://mp.weixin.qq.com/s/sY6cw6wE5ePyrZmRYbXApg)：作为 AI 辅助 PRD 前置发现、用户反馈证据链和问题地图字段的公开参考来源。2026-05-28 已通过公开 HTML 读取标题、账号、作者、发布时间和正文，并尝试浏览器自动化；本仓库只吸收反馈到问题、证据强度、人工判断门禁和 PRD 前置发现流程，不复制原文表格、图片或外部工具营销。
- 微信文章 [《`product-brainstorming` Skill 原文中文版》](https://mp.weixin.qq.com/s/cz-9HnmlC_VNcVpdd_e0Vw)：作为 `产品架构专家` 产品头脑风暴、问题探索、方案发散和假设挑战纪律的公开参考来源。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `进击的肖恩`，既有账号线索保留 `AIML实验室`，页面时间字段为 2026-04-21；正文标注原始文件为 `knowledge-work-plugins/product-management/skills/product-brainstorming/SKILL.md` 并给出 GitHub 仓库链接，本轮 GitHub raw 原始文件未成功拉取，后续精确引用需再核验。本仓库只吸收 HMW、第一性原理、类比、反转、OODA 和逆向头脑风暴等可迁移方法，不复制原文角色提示、问题清单、外部 Skill 结构或作者表达，也不把头脑风暴结果直接写成 PRD、Backlog 或研发任务。
- 微信文章 [《我让3个AI吵了一整天架，它们把PRD写完了》](https://mp.weixin.qq.com/s/13wn5wS8AwyMNBrMQpTyEg)、GitHub 仓库 [Kira2red/magi-product](https://github.com/Kira2red/magi-product) 与 [Kira2red/Kira-product-monster-skills](https://github.com/Kira2red/Kira-product-monster-skills)：作为 `产品架构专家` 内部 `product-deliberation-workflow.md` 的公开参考来源，用于复杂 PRD、AI 生成方案、原型候选和多方争议需求的产品合议评审。2026-06-05 已通过移动端微信 UA 公开 HTML 读取文章标题、作者、账号、发布时间字段和正文，并读取两个 GitHub 仓库的 README、文件树和核心 Skill / prompt 文件；本仓库只吸收 Controller / PM / Reviewer 工作位、强制阶段门、用户确认点、指定 Skill / 模板约束、SOP、复杂度评估、类型分流、分批产出、证据审查和准出检查，不复制原文、图片、外部平台工具调用、watchdog 脚本、车载专项规则、外部 Skill 结构、示例正文、游戏 Skill、纯中文绝对化约束或作者表达。
- 微信文章 [《为什么你的 AI 只能写总结，别的产品经理已经用AI在挖需求机会了？附skill模板和调试方法》](https://mp.weixin.qq.com/s/jsuVbuvKJxEXl8dZyzh23g)：作为 `产品架构专家` 内部 `product-insight-analyst.md` 的公开参考来源，用于产品洞察、资料资产化、客户/竞品/标杆情报分拣、机会雷达、证据与推理链和产品负责人决策边界。2026-06-03 普通 curl/mobile UA 返回微信验证页；随后通过本机 Chrome headless 等价浏览器读取标题、账号、作者、发布时间和正文；本仓库只吸收资料资产化、客户/竞品/标杆三篮分拣、证据与推理链、机会雷达、宁缺毋滥和产品负责人决策边界，不复制原文、模板正文、固定路径、外部 Skill 名称体系、作者表达或标题传播话术。
- 微信文章 [《有了洞察还不够，产品负责人真正值钱的是 Backlog 决策》](https://mp.weixin.qq.com/s/stj1HjCpaG5PzXhxfxlWSg)：作为 `产品架构专家` 内部 `po-backlog-manager.md` 的公开参考来源，用于洞察/机会清单到 Backlog 决策、BV/EE、业务/用户/工程三桌校验、User Story、AC、技术现实主义和 P0/P1/P2 排序。2026-06-03 已通过移动端微信 UA 公开 HTML 读取标题、账号、作者、发布时间和正文；本仓库只吸收机会收敛、拒绝/延后理由、研发可执行边界和决策偏好自检，不复制原文图片、外部 Skill 名称体系、作者表达或标题传播话术。
- 微信文章 [《B端产品经理实战经验分享系列 - 如何写出高质量的需求文档》](https://mp.weixin.qq.com/s/_KU0j5sy1HBMdx03bhlYGg)：作为 `产品架构专家` PRD 文档质量治理、文档目标/受众、PRD/MRD/BRD 类型区分、版本记录、评审闭环和同步机制的公开参考来源。2026-06-01 已通过公开 HTML 读取标题、账号、作者、发布时间和正文，并用本机 Chrome headless 加载取证；本仓库只吸收可迁移的质量门禁、裁剪方法和评审机制，不复制原文案例、指标数字、图片或作者表达。
- 微信文章 [《完整不等于可测：需求评审的四个AI新维度》](https://mp.weixin.qq.com/s/7EiFz1Oka1tYQmfbBferQg)：作为 `产品架构专家` PRD 质量门禁和 `AI Native 研发流程编排` PRD 预审接入的公开参考来源。2026-06-08 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文；本仓库只吸收完整性、一致性、可测试性、二义性四维度预扫描、疑似问题和人工过滤/排序/owner 决策边界，不复制原文、效果数字、示例句子、标题传播话术或作者表达，也不把 AI 预扫描写成正式需求评审、QA 设计或产品 owner 决策的替代品。
- 微信文章 [《现在我敢评测这个 skill 了，产品负责人来看看这个自评卡吧》](https://mp.weixin.qq.com/s/ZUwtGYYTzt-c2YRXn8ryJw) 与 [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) 中的 `ai-shaped-readiness-advisor`：作为 `产品架构专家` AI 产品工作成熟度、AI-first 与 AI-shaped 区分、上下文结构化、工作流编排、学习周期、人工责任和差异化指标的公开参考来源。2026-06-01 已通过移动端微信 UA 公开 HTML 读取文章标题、账号、作者、发布时间和正文，并读取公开 `SKILL.md`；本仓库只吸收可迁移检查项，不安装外部 Skill、不复制交互协议、评分 rubrics、示例案例、图片、自评卡排版或作者表达。
- 赵丹阳图书 [《产品经理方法论：构建完整的产品知识体系》](https://m.dushu.com/book/13884861/) 及同作者同系列公开书目信息：作为 `产品架构专家` 产品经理基础方法、知识体系和能力校准的公开参考来源。2026-06-02 已读取公开图书页、内容简介、作者简介和目录；本仓库只吸收文档分型、流程图、原型图、产品架构图、用户研究、需求管理、数据分析、技术协作、项目管理、行业/商业分析和知识库沉淀等可迁移能力，不复制书籍正文、章节内容、示例、图表或作者表达，也不把基础岗位知识体系替代复杂业务产品架构专家能力。
- 微信文章 [《万里汇，太牛了！AI出海的全球资金管理，算是让它玩明白了》](https://mp.weixin.qq.com/s/mTLMJVO4_NNlENZP8utZGA)：作为 `产品架构专家` AI 出海全球资金管理、全球收款、多币种财资、批量付款、Agent 支付/VCC、token / 用量计费和嵌入式金融场景的公开参考来源。2026-05-29 已通过公开 HTML 和本机 Chrome headless 读取标题、账号、作者、发布时间和正文；本仓库只吸收场景拆解、产品检查项和归因边界，不复制厂商营销数字、产品覆盖承诺、图片或作者表达。
- [SEI ATAM](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/)、[Microsoft Azure Domain Analysis](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis)、[AWS Well-Architected REL03-BP02](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_service_architecture_business_domains.html)、[Dan North: Introducing BDD](https://dannorth.net/blog/introducing-bdd/) 与 [Impact Mapping](https://www.impactmapping.org/book.html)：作为业务目标、业务域/限界上下文、质量属性场景、行为验收和产品到架构追踪的公开参考来源。本仓库只吸收可迁移的业务驱动验证方法，不复制原文、示例、图片、模板或外部脚本；Use-Case 2.0 官方站点本轮受 Cloudflare 阻断，未作为已吸收来源。
- [NASA SWE-052 Bidirectional Traceability](https://swehb.nasa.gov/x/AwIfBg)、[arc42](https://arc42.org/overview)、[C4 Model](https://c4model.com/diagrams)、[Atlassian PRD guide](https://www.atlassian.com/agile/product-management/requirements) 与 [ISO/IEC 25010 质量模型摘要](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)：作为需求到设计到验证的追踪、架构视图、质量属性和 PRD 假设/发布验证的公开参考来源。本仓库只吸收轻量检查项和模板槽位，不复制外部模板、图示、示例或品牌化流程。
- [NN/g UX Mapping Methods](https://www.nngroup.com/articles/ux-mapping-cheat-sheet/)、[NN/g Service Blueprints](https://www.nngroup.com/articles/service-blueprints-definition/) 与 [draw.io GitHub integration](https://www.drawio.com/docs/integrations/github/)：作为产品图形化中用户旅程、服务蓝图、体验地图、可编辑图资产和仓库化维护的公开参考来源。2026-06-01 已读取公开页面；本仓库只吸收图型选择、前后台触点、支撑流程、证据/物料、可编辑源文件和权限边界，不复制 NN/g 表格/图示/课程材料、draw.io 集成步骤或品牌表达。

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
