# Skills

本仓库维护可安装到 Codex 的 Skills。它不是 prompt 集，而是一套可验证、可同步、可持续演进的 Agent 运行时资产。

仓库按三级加载组织：`AGENTS.md` 保存全仓规则和安全边界，`SKILL.md` 保存触发入口、核心流程和红线，`references/` 保存详细知识与模板；确定性生成、验证和同步放在 `scripts/`。Skill 改进只吸收脱敏后的执行记录、验证结果、CR 结论和人工反馈。

## 用户使用指南

Codex 会根据 `SKILL.md` 的 `name` 和 `description` 自动触发技能，也可以直接点名。同步后触发不符合预期，先重启 Codex 或开启新会话。

使用时不用背 Skill 名称。先说明目标、材料、边界、风险和验证；拿不准入口时，直接说 `先帮我选路`。

### 1. 一句话讲清目标

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；已有 <材料或路径>；边界是 <不做什么 / 是否允许写入 / 风险>；验证要求是 <检查命令 / 证据 / 残余风险说明>。
```

材料可以是需求、PRD、页面、截图、DDL、代码路径、日志、测试输出或外部文章。资金、合规、生产、密钥、部署、删除和不可逆操作必须明确风险与授权。

常见任务可以直接这样说：

- `先帮我选路：我有 PRD 和代码路径，只想做 CR，不改代码。`
- `$delivery-collab：先做轻量生命周期定位和角色路由，只输出当前阶段、主 Skill、主 blocker、交接物、验证和停止条件。`
- `做 grill-me 盘问：盘一下这个方案，只问一个主 blocker。`
- `进入知识回流视图：把这轮 CR 结论沉淀到项目约规。`
- `做生产交付审查：只判断能不能发布，列证据和停止条件。`
- `初始化/更新项目 AGENTS.md：只做最小项目约规 patch。`

### 编写文档的友好指令

不需要记模板文件名，直接说明材料、目标路径和是否允许写入。产品、系分、重构三类正式设计文档各有一个权威模板入口：产品设计用 `product-prd-template.md`，系分设计用 `system-analysis-template.md`，跨模块或迁移型重构用 `refactoring-design-template.md`；同目录的 `product-design-and-prd.md` 与 `system-analysis-design.md` 是写作约规，不是旧模板。

- `基于 <需求或材料路径> 编写一份可评审的产品设计文档，保存到 <目标路径>；区分事实、推断和待确认，按需求复杂度裁剪模板，完成后自检。`
- `基于 <产品文档路径> 和 <源码/接口/DDL 路径> 编写系分设计，保存到 <目标路径>；复用产品主题，补齐边界、流程、规则、接口、数据、测试、发布与回滚证据。`
- `基于 <当前源码或现状证据> 和 <目标系分路径> 判断是否需要独立重构设计；需要时输出可验证、可暂停、可回退的 MIG 切片，不需要时只给任务卡和测试保护。`
- `只评审 <文档路径>，不要改文件；列出必改项、待确认项、证据缺口和能否进入下一阶段。`
- `更新 <既有文档路径>，保持文件名和已确认结论；只补本轮变化，删除被新结论取代的旧正文，不保留讨论过程。`
- `把 <权威 Markdown 路径> 整理成 <DOCX/PDF>；不改变产品或工程语义，完成后检查目录、分页、表格、图片和中文字体。`

已有正式文档默认原路径更新，不因模板升级另建“新版”“最终版”或日期副本；历史讨论、被拒方案和完整修订过程放到评审报告、Decision Log、ADR 或任务记录。

### 2. 按交付物选入口

| 你要交付 | 默认入口 | 最小输入 |
| --- | --- | --- |
| 产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图 | `产品架构专家` | 目标、用户/主体、范围/非目标、材料、验收、待确认项 |
| 系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图 | `资深架构师` | 路径、现象/目标、环境、约束、验证命令、是否允许修改 |
| 正式报告、制度、手册、研究说明、材料合并、文档审校、DOCX/PDF | `document-authoring` | 读者、用途、文档类型、事实源、载体、验收方 |
| 汉字学、训诂、字源、甲骨文、金文、小篆、通假、异体考据 | `hanzi-philology` | 研究对象、时代与文本范围、已读材料、所需结论等级 |
| 跨角色交付编排、工程治理、目标计划、质量门禁、生产交付审查、知识演进 | `产研协同体系` / `$delivery-collab` | 材料成熟度、owner、读写边界、授权、验证、停止条件 |
| DDL/schema/Java 类/字段表格到 Java Service 脚手架 | `java-service-code-generator` | 结构化输入、表名、模块、输出目录、覆盖授权 |
| Java 项目通用编码约规，或按依赖/上下文启用 Wind/Nobe 专项 | `wind-coding-conventions` | Java 技术栈、依赖/包名/类型证据、规则问题、是否仅检查规则 |

图形化交付按语义归属选入口：产品业务流程、业务状态和验收视图用产品专家，系统模块、接口时序、实现状态和部署视图用架构师。只说“画状态机/流程图”且没有产品语义或工程落点时，先澄清一次，不让两个 Skill 同时抢占；复杂可编辑架构图、代码库结构转图或架构描述转图先由架构师判断准入，再按需使用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。

外部 Skill、工具、联网、安装、写配置或同步到 Codex，必须先完成供应链安全审查和授权确认。

### 3. 产研协同体系

`产研协同体系` 包含三个稳定能力域：交付编排、工程治理、知识演进。它只回答“现在由谁做、交接什么、怎么验证、什么时候停”：产品正文回 `产品架构专家`，工程实现、TDD、源码级 CR 和发布风险回 `资深架构师`，结构化 Java Service 生成回 `java-service-code-generator`，Java/Wind 编码约规回 `wind-coding-conventions`。

默认先做轻量生命周期定位，只判断当前阶段和下一交接；跨阶段、生产、维护退役或高风险任务才展开完整 SDLC 覆盖审查。SDLC 用于防遗漏，角色 Loop 用于定角色和交接；二者都不替代专项 Skill、owner、验证或授权。

角色 Loop 按“当前阶段 -> 主责角色 -> 主 Skill -> 交接物 -> 验证与停止条件”串行推进，一次只处理一个主 blocker，完成后写回下一阶段输入；AI Maker 与 AI Checker 不合并自证。

默认最小输出只保留：结论、当前阶段、owner、交接物、授权策略、验证与停止条件；需要路由时补主 Skill 和主 blocker。需要时再补事实 / 推断 / 待确认 / 范围外不做和残余风险；只有明确要求完整方案、评审报告或模板时才展开内部实现层。

| 视图 | 适用任务 | 默认边界 |
| --- | --- | --- |
| 只读理解视图 | 读代码库、设计-代码对齐、工具准入、事实边界检查 | 默认不写文件、不联网、不安装 |
| 产研交付视图 | 按产品/交互、设计评审、TDD、编码、CR、质量评估、验证发布和复盘分角色推进 | 按阶段路由专项 Skill 和 owner |
| 验证发布视图 | 测试矩阵、质量门禁、源码质量评审、生产交付审查和失败回退 | 不替代测试、Git、部署或上线审批 |
| 知识回流视图 | 把已验证经验写入 `AGENTS.md`、`CONTEXT.md`、ADR、reference、fixture、脚本或用户指南 | 不吸收一次性试错和私有轨迹；上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀可说 `进入知识生产`，形成可维护的上下文资产 |

决策澄清门禁是小闭环总门禁，`grill-me` 是命中升级条件后的升级盘问；只在关键分叉未决、回答含糊、连续返工或下一步将改变公共契约、状态机、验收样例、写入范围、发布风险时进入。复杂或模糊任务一次只问一个主 blocker；Facts 先从材料、源码、测试或日志自答，Decisions 才问 owner。

`grill-me` 使用方式：

- 你只需要回答：接受建议、改答案、补材料或停止。
- 结束条件：确认 shared understanding，并形成决策快照；未确认前不执行。
- 红线、底线、不能碰、不可、禁止、必须等字眼必须进入决策快照或待确认项。

用户说 `按你建议推进` 时，只关闭当前 blocker、写回下一阶段输入，再处理下一最高价值 blocker。任务结束按决策澄清门禁判断 `自决推进 / 询问 owner / 继续收敛 / 停止交接`。

### 4. 常用短句

| 你可以说 | 行为 |
| --- | --- |
| `先帮我选路` | 判断入口、缺口、下一 owner 和停止条件 |
| `进入产研协同体系` / `进入产研交付视图` | 编排跨角色、跨阶段交付 |
| `$delivery-collab 按轻量生命周期定位 + 角色 Loop 推进，一次只处理一个主 blocker` | 先定位当前阶段，再按主 Skill 串行交接；不展开无关阶段 |
| `这次涉及跨阶段/生产/维护退役/高风险，展开完整 SDLC 覆盖审查` | 检查构想、开发、运行支持、维护演进和退役是否有遗漏 |
| `进入只读理解视图` | 只读分析，默认不写文件、不联网、不安装 |
| `做生产交付审查` / `做质量门禁` | 输出 Ready / Not Ready / Human Approval Required 及证据、回退和风险 |
| `做业务架构规划` | 路由产品专家输出能力、价值流、对象、映射和知识库回流计划 |
| `做源码质量评审` | 路由架构师按源码、约规、测试和风险给 P 级发现 |
| `做 grill-me 盘问` / `grill 一下这个方案` | 每轮只盘一个决策分支，未形成 shared understanding 不执行 |
| `蒸馏业务专家` | 生成可追溯 Skill Pack 草案、证据地图、成熟度和压力测试 |
| `进入知识回流视图` | 把已验证经验归位到权威载体 |
| `初始化/更新项目 AGENTS.md` | 只做最小项目约规 patch；Wind 项目按实际依赖和上下文补专项入口 |

### 5. 不要这样用

- 只写普通 PRD、产品方案或 Backlog 决策：直接用 `产品架构专家`。
- 只做系统设计、代码 CR、Bug、测试或生产变更：直接用 `资深架构师`。
- 只有自然语言需求、没有字段结构或表名：不要让代码生成器直接生成生产代码。
- 不要把工具、模板、目标、计划或授权机制名当主流程；先看交付物和风险。
- 不允许交付模拟模块、无业务入口 demo、内存版业务 Service 或看上去可用的样子货。
- 涉及安装、联网、覆盖文件、Git、同步、生产数据、密钥、部署或不可逆操作：先明确授权、写入范围、dry-run 和停止条件。

## 进阶能力索引

日常使用优先看上面的快速指南；本节只供需要精确路由或维护边界时查阅。

### 产研协同体系

- 路径：[delivery-collab](./delivery-collab)；显式调用：`$delivery-collab`。
- 适合：跨业务、产品、UED、架构、AI Maker / Checker、质量和发布的协同；覆盖交付编排、工程治理、目标计划、代码库理解、工具准入、设计-代码对齐、质量门禁和知识演进。
- 边界：只负责成熟度、owner、交接物、停止条件、授权策略和工具边界；产品正文交给产品专家，工程实现、最小正确实现检查和过度设计 CR 交给架构师，结构化代码生成交给代码生成器。

### 产品架构专家

- 路径：[product-architecture-expert](./product-architecture-expert)。
- 适合：PRD、产品方案、需求说明、业务架构规划、产品洞察、Backlog 决策、原型/HTML/页面截图/交互稿反推 PRD，以及能力地图、业务流程、状态机、规则矩阵和产品图。
- 产品材料分散或提到 `pm-skills` 时，先跑产品判断动作链；产品专家补产品上下文包，产研协同体系只判断交接成熟度、owner、验证和停止条件。
- 边界：不替代法务、合规、财务或持牌机构确认；不负责工程实现、代码 Review 和生产排障。

### 资深架构师

- 路径：[senior-software-architect](./senior-software-architect)。
- 适合：架构设计、系统分析设计、技术方案、ADR、代码 Review、Bug 修复、测试/TDD、生产变更、工程图、遗留系统改造和架构排熵。
- 边界：不替代产品专家定义复杂业务语义、PRD 和金融产品规则。

### 专业文档撰写

- 路径：[document-authoring](./document-authoring)；显式调用：`$document-authoring`。
- 适合：把已提供或已核验材料整理、合并、审校和收口为正式报告、制度、手册、研究说明、DOCX 或 PDF。
- 边界：不替代产品、工程、法律、合规或领域专家判断事实；PRD、系分和训诂考据先回对应专项 Skill。

### 汉字学与训诂专家

- 路径：[hanzi-philology](./hanzi-philology)；显式调用：`$hanzi-philology`。
- 适合：分析汉字形音义、字源、本义、甲骨文、金文、小篆、通假、假借、古今字、异体及具体文句训诂。
- 边界：出土材料、传世文献、传统训释、音韵与现代研究相互校正；《说文解字》只作参考材料之一，不单独证明本义或古文字形。

### Java/Wind 编码约规

- 路径：[wind-coding-conventions](./wind-coding-conventions)。
- 适合：所有 Java 项目的通用编码约规检查；检测到 Wind/Nobe 依赖、包名、类型、模块结构或明确上下文时叠加 Wind 专项，也可初始化项目 `AGENTS.md` 规则入口。
- 边界：只做规则判断和偏差说明；没有 Wind/Nobe 高置信度信号时不加载 Wind face/impl、API 或模型专项；源码设计、CR、TDD、修复和验证只由架构师主责并消费相应规则。
- 友好指令：`只检查这个 Java 项目应启用哪些约规，不做源码 CR`；需要执行时改用：`由资深架构师 CR 这段 Java 源码，统一加载通用 Java 约规；有 Wind/Nobe 证据时再加载专项`。

### java-service-code-generator

- 路径：[java-service-code-generator](./java-service-code-generator)。
- 适合：根据 DDL/SQL、Java 类、字段表格或 schema 生成 Wind/Nobe Java Service 配套代码。
- 边界：不从纯自然语言直接生成生产代码，不替代业务、架构或 DBA 判断。

### 常见组合

- 从 AI 原型到工程化：产研协同体系定义阶段、owner 和门禁；产品专家补产品上下文包；架构师补系统设计、TDD、源码 CR 和发布风险。
- 从战略到项目组合：产品专家做业务架构规划；产研协同体系只判断交接成熟度、owner、验证和停止条件。
- 从 PRD 到代码生成：先确认对象、状态、字段、索引和金额精度，再把结构化输入交给代码生成器。
- 从训诂考据到正式报告：`hanzi-philology` 先交付训诂证据卡，`document-authoring` 再成稿和生成载体，不改变证据等级。
- 从普通图到复杂图：先由产品专家或架构师稳定语义，再评估 `$fireworks-tech-graph`。

## 5 分钟上手

```bash
git clone https://github.com/fengwuxp/skills.git
cd skills
./sync-skills.sh --dry-run all
./sync-skills.sh all
scripts/validate-installed-skills.sh
```

同步单个 Skill 使用 `./sync-skills.sh senior-software-architect`。非默认目录使用 `CODEX_HOME=/path/to/codex-home`；同步后重启 Codex 或开启新会话，再通过 `$` 调用技能。

## 验证与同步安全

修改 Skill、脚本或 fixture 后先验证，再预览同步：

```bash
./scripts/validate.sh
git diff --check
./sync-skills.sh --dry-run all
```

正式同步后运行 `scripts/validate-installed-skills.sh` 回读仓库管理的 Skill，确认文件一致且退役 Skill 已移除；也可使用 `VALIDATE_INSTALLED_SKILLS=1 ./scripts/validate.sh` 把真实安装态检查并入完整验证。该检查只读，不修改安装目录。

`scripts/evaluate-skills.py` 只做离线静态预检，不执行真实 Agent；评分用于发现结构、触发样例和验证资产缺口，不能替代 Codex 行为 smoke、领域事实复核或人工 CR。

`sync-skills.sh` 使用 `rsync --delete` 保持安装目录与仓库一致，正式同步前必须确认 `CODEX_HOME` 和目标 Skill；已有目标会备份到 `$CODEX_HOME/skills/.backups/`。`--dry-run` 不写入目标目录。不要在安装目录保存额外文件，也不要在 Skill 的任何子目录保留名为 `SKILL.md` 的外部参考，以免被 Codex 误识别为独立 Skill；离线上游入口统一改名为 `upstream-skill.md`。

维护者复装或更新外部 `grill-me` 后，运行 `VALIDATE_GRILL_ME_INSTALL=1 ./scripts/validate.sh` 或 `scripts/validate-grill-me-install.py`；普通使用 `grill-me` 不需要运行这些命令。

## 维护者与高级扩展

### SkillX 导出规范

把 SkillX 或类似系统的候选能力转换为 Codex Skill Package 前，先读 [SkillX 到 Codex Skill Package 导出规范](./references/skillx-to-codex-skill-package.md)，完成输入契约、安全门禁、三层映射、生成流程和验证流程审查。第一版只接受人工审查后的离线 JSON，不自动读取历史轨迹、不采集用户数据、不引入外部训练流水线。

输入必须符合 `schemas/skillx-candidate.schema.json`；`scripts/skillx_export_adapter.py` 生成的候选包包含 `REVIEW.md` 和 `fixtures/trigger-prompts.md`：

```bash
python3 scripts/skillx_export_adapter.py --check-input --input fixtures/skillx/sample-candidate.json
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out
python3 scripts/skillx_export_adapter.py --validate-output /tmp/skillx-out/skillx-product-reviewer --input fixtures/skillx/sample-candidate.json
```

### 外部参考来源

公开来源、读取状态和不吸收边界统一查 [仓库级来源索引](./references/source-map.md)；各 Skill 的专题证据保存在自己的 `references/source-map.md`，README 不复制来源正文。

### Skill 自我改进外循环

内循环执行真实任务；外循环只把重复问题、验证失败、CR 结论和人工反馈转成最小 Skill 改进 diff。进入外循环前记录：目标 Skill、触发样例、错误表现、反馈证据、最小修改位置、验证方式、不得吸收。

不得从单次失败泛化永久规则，不得吸收个人偏好、私有轨迹、客户资料、生产数据、密钥、外部文章原文或 Agent 自述，也不得自动提交、同步或发布。完整约定见 [AGENTS.md](./AGENTS.md)。
