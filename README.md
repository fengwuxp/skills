# Skills

本仓库维护可安装到 Codex 的 Skills。它不是 prompt 集，而是一套按需加载、可验证、可同步和可持续演进的 Agent 运行时资产。

仓库按三级加载组织：`AGENTS.md` 保存全仓规则和安全边界；`SKILL.md` 保存触发、核心流程和红线；`references/` 保存详细知识与模板；确定性生成、验证和同步进入 `scripts/`。

## 用户使用指南

### 1. 30 秒上手

仓库把知止者设计为默认交互与责任模型，`$wise-agent` 是显式协同入口，不表示每个任务都必须加载它。日常不需要选角色或背 Skill 名称，直接说清交付物、事实源、范围、授权和完成证据即可。单一领域且边界清楚的任务可直接加载对应专业 Skill；跨专业、跨阶段、跨轮，或需要 Goal、Loop、Worker、Checker、状态恢复和知识回流时，再加载 `$wise-agent`。多 Skill 只为同一 Agent 补充专业上下文，不产生第二人格或重复 Owner。

通用任务模板：

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；请读取 <材料或路径>；只处理 <范围>，不做 <非目标>；允许 <只读 / 写入路径 / 其他授权>；用 <检查命令 / 评审证据 / 验收标准> 证明完成。信息足够就直接推进，只在关键决策或高风险授权处问我。
```

不确定流程、角色或 Skill 时，不要先替 Agent 设计接力顺序，直接使用上面的模板。任务明显跨专业、跨阶段、跨轮，或你想强制知止者持有目标和状态时，再在前面加 `$wise-agent：`；只想强制一个专业能力时，直接调用该 Skill。

一次完整交付至少应让你看到：实际产物或明确结论、采用的关键事实与决策、验证证据，以及尚未消除的风险或待确认项；不要求用户阅读内部能力清单和推理轨迹。

常见任务可以直接这样说：

| 任务 | 友好指令 |
| --- | --- |
| 自主推进 | `$wise-agent：读取当前项目事实，自己判断并推进；只在关键决策或高风险授权处问我，完成后给出产物、验证和残余风险。` |
| 只读 CR | `我有 PRD 和代码路径，只做只读 CR，不改代码；请给出源码证据、严重级别和残余风险。` |
| 产品设计 | `根据 <访谈/需求/原型> 写一版可评审 PRD，区分事实、推断、待确认和范围外不做。` |
| 工程交付 | `基于 <PRD/系分/源码> 完成 <Bug/TDD/重构/代码>，写入范围是 <路径>，验证命令是 <命令>。` |
| 决策盘问 | `使用 $grill-me 盘一下这个方案：先查历史问题和项目事实，一次只问一个主 blocker，记录每个问题和结论。` |
| 经世决策 | `使用 $huaxia-practical-wisdom：基于这些事实校准当前取舍，给出最小行动、止损和验证，不要只讲古语。` |
| 知识回流 | `进入知识回流视图：把这轮 CR 结论沉淀到项目约规，并说明权威落点和证据。` |
| 发布准入 | `做生产交付审查：只判断能不能发布，列证据、回退、人工确认点和停止条件。` |
| 项目约规 | `初始化/更新项目 AGENTS.md：只做最小项目约规 patch。` |

同步后触发不符合预期，先重启 Codex 或开启新会话。

### 2. 任务与专业能力

下表用于查边界，不是使用前必须选择的菜单。不知道选谁时回到第 1 节，直接描述任务；显式调用某个专业 Skill 只表示强制或优先使用。

| 你要交付 | 专业能力与路径 | 最小输入 | 边界 |
| --- | --- | --- | --- |
| 跨领域真实工作、目标控制、能力组合、验证和知识演进 | `知止者`，路径：[wise-agent](./wise-agent) | 目标、事实源、范围、授权、完成证据 | 不限于产研；不获得无限自治或高风险授权 |
| 产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图 | 产品架构专家，ID：`product-architecture-expert`，路径：[product-architecture-expert](./product-architecture-expert) | 用户/主体、目标、材料、范围、验收 | 不负责工程实现、代码 Review 和生产排障 |
| 系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图 | 资深架构师，ID：`senior-software-architect`，路径：[senior-software-architect](./senior-software-architect) | 路径、现象/目标、约束、验证命令、写入授权 | 不替代产品专家定义复杂业务语义、PRD 和金融产品规则 |
| 正式报告、制度、手册、研究说明、材料合并、文档审校、DOCX/PDF | `document-authoring`，路径：[document-authoring](./document-authoring) | 读者、用途、事实源、载体、验收方 | 不替代产品、工程、法律、合规或领域事实判断 |
| 汉字学、训诂、字源、甲骨文、金文、小篆、通假、异体考据 | `hanzi-philology`，路径：[hanzi-philology](./hanzi-philology) | 对象、时代、文本范围、材料、结论等级 | 《说文解字》只作证据之一，不单独证明本义 |
| 华夏经典视角下的现实决策、组织协作、长期成长和行动取舍 | 华夏经世智慧，ID：`huaxia-practical-wisdom`，路径：[huaxia-practical-wisdom](./huaxia-practical-wisdom) | 现实事实、目标、约束、主体、时限、最坏损失 | 不作古籍训诂、医学诊疗、占卜命理，不替代专业结论 |
| 方案、计划或设计的逐项盘问、历史去重和决策快照 | `grill-me`，路径：[grill-me](./grill-me) | 方案、已有材料、历史决策、Owner 和风险边界 | 未达到 shared understanding 不执行；自决不扩大授权 |
| DDL/schema/Java 类/字段表格到 Java Service 脚手架 | `java-service-code-generator`，路径：[java-service-code-generator](./java-service-code-generator) | 结构化输入、表名、模块、输出目录、覆盖授权 | 不从纯自然语言直接生成生产代码 |
| Java 项目通用编码约规，或按依赖/上下文启用 Wind/Nobe 专项 | `wind-coding-conventions`，路径：[wind-coding-conventions](./wind-coding-conventions) | Java 源码证据、依赖/包名、规则问题 | 只做规则判断和偏差说明；源码设计、CR、TDD、修复和验证由架构师主责 |

没有 Wind/Nobe 高置信度信号时不加载 Wind face/impl、API 或模型专项。Wind 项目按实际依赖和上下文补专项入口；普通 Java 源码 CR 由架构师统一消费通用 Java 约规。

图形化交付按语义归属：产品业务流程、状态和验收视图交给产品专家；系统模块、接口时序、实现状态和部署视图交给架构师。复杂可编辑架构图、代码库结构转图或架构描述转图，先稳定语义，再按需使用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。

常见组合：

- 从 AI 原型到工程化：先稳定产品语义，再完成系分、TDD、源码 CR 和发布验证。
- 产品材料分散或提到 `pm-skills`：知止者装载产品判断动作链，形成产品上下文包并继续持有后续目标、验证和停止条件。
- 从训诂考据到正式报告：先形成证据卡，再由 `document-authoring` 成稿，不改变证据等级。
- 从普通图到复杂图：先由产品专家或架构师稳定语义，再评估专用出图能力。

### 3. 知止者如何工作

加载 `$wise-agent` 时，知止者不是流程路由器，而是持续读取事实、作出取舍并完成工作的统一行动主体。它按“察 -> 辨 -> 谋 -> 行 -> 验 -> 化”推进：先读事实，再辨问题，选择最小能力，完成实际工作，独立验证并回写结果。它不是不行动，而是让行动有方向、有分寸、有收口。

简单任务直接完成；复杂任务才使用计划、SDLC、Goal、Loop、Worker 或 Checker。判断顺序是：先看能否本轮直接完成；跨交付阶段才展开 SDLC；跨轮持续推进才建立 Goal；同一目标需要反复执行才进入 Loop；存在可冻结且不冲突的子任务才派 Worker；风险或证据要求足够高才增加 Checker。

专业能力按需渐进加载；产品、架构、文档、考据、生成和约规不是平级角色。人类责任 Owner、知止者、专业能力和独立 Checker 分开，无论内部用了多少能力，对用户只形成一个综合结论。

### 3.1 什么时候启用 SDLC、Goal、Loop、Worker、Checker

日常只需描述任务，不需要主动选择机制；知止者默认直接完成，再按下面的证据升级。需要强制某种控制时，可使用最后一列的友好指令。

| 机制 | 什么时候自动启用 | 不该启用 | 你可以这样说 |
| --- | --- | --- | --- |
| SDLC | 任务跨产品、设计、工程、验证、发布或运行阶段，需要交接和阶段门禁 | 单阶段、单文件或一步任务 | `按完整 SDLC 覆盖这个需求到发布，但只展开当前需要的阶段。` |
| Goal | 任务跨会话、跨 Wave 或要持续推进，需要成功标准、状态、预算和停止线 | 当前会话能完成；未明确要求时不创建运行时 Goal | `为这项工作建立 Goal 并持续推进，成功标准是 <...>，停止条件是 <...>。` |
| Loop | 同一 Goal 下要反复读取状态、执行、观察和验证，且有状态载体、反馈源和轮次边界 | 一次执行即可完成，或没有反馈与停止条件 | `允许进入 Loop，最多 <N> 轮；状态写到 <位置>，连续 <N> 轮无进展就停止。` |
| Worker | 存在输入可冻结、写入不重叠、低耦合的独立子任务，并行明显更快 | 同一文件、强耦合调用链或连续判断 | `这些子任务互不依赖，可并行时再派 Worker；共享文件必须串行。` |
| Checker | 高风险、公共契约、重要交付、发布准出或需要独立 CR | 低风险任务已有回读、测试或 validator | `增加独立 Checker，直接读取原始产物和证据，不只审 Maker 摘要。` |

五者不是一套固定流水线：SDLC 是阶段地图，Goal 保存完成线，Loop 管反复运行，Worker 管执行分工，Checker 管独立证明。可以只有 Checker 没有 Worker，也可以只用 Goal 而不进入 Loop。

决策寻路不是第六个控制机制。它只在目标大致明确，但路线仍模糊、超过一次会话且还不能可靠形成 Spec 或计划时使用，处在问题地图之后、Spec / Goal Ready 之前。你可以说：`进入决策寻路：先定义 Destination，区分 Frontier、Not yet specified 和 Out of scope，一次关闭一个决策；不要生成 Spec、计划或执行任务。` 如果路线已经清楚，知止者会跳过建图。

“视图”只是强调任务边界的可选短句，不是前置流程：只读理解视图用于只读事实核验，默认不写文件、不联网、不安装；交付推进视图用于完成真实产物；验证发布视图用于给出 Ready / Not Ready / Human Approval Required；知识回流视图用于把已验证经验归位到约规、上下文、ADR、reference、fixture 或脚本。涉及上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀时，也可说 `进入知识生产`，形成可维护的上下文资产。

### 3.2 什么时候会停下来问你

决策澄清门禁只处理真正未决的 Decisions；Facts 先从材料、源码、测试或日志自答，Decisions 才问 owner。复杂或模糊任务一次只问一个主 blocker。结果只能是：`自决推进 / 询问 owner / 继续收敛 / 停止交接`。

`grill-me` 是升级盘问，不是每个任务的必经流程：

- 触发：关键分叉未决、回答含糊、连续返工，或下一步会改变公共契约、状态机、验收、写入范围或发布风险。
- 交互：你只需要回答接受建议、改答案、补材料或停止；用户说 `按你建议推进` 时只关闭当前 blocker。
- 历史：每问前检查问题台账、决策快照、文档、代码、测试和知识库；已确认或已排除的问题不得换个说法重问。
- 自决：可查 Facts、已有 Owner 结论及低风险可逆默认项由 Agent 自答并留痕；新价值取舍、公共契约、高风险和红线仍问 Owner。
- 退出：确认 shared understanding 并形成决策快照，未确认前不执行。
- 红线：红线、底线、不能碰、不可、禁止、必须等字眼必须进入决策快照或待确认项。

常用短句只用于强调边界：`进入知止者`、`进入只读理解视图`、`做质量门禁`、`做源码质量评审`、`做生产交付审查`、`进入知识回流视图`。

### 4. 编写文档的友好指令

不需要记模板文件名，先说材料、文档类型、读者、目标路径、写入授权和验收要求。产品、系分、重构三类正式设计文档各有一个权威模板入口：产品设计用 `product-prd-template.md`，系分设计用 `system-analysis-template.md`，迁移型重构用 `refactoring-design-template.md`。

- `基于 <需求或材料路径> 编写可评审产品设计，保存到 <目标路径>；区分事实、推断和待确认，按复杂度裁剪模板。`
- `基于 <产品文档> 和 <源码/接口/DDL> 编写系分，保存到 <目标路径>；补齐边界、流程、规则、接口、数据、测试、发布和回滚证据。`
- `基于 <现状证据> 判断是否需要独立重构设计；需要时输出可验证、可暂停、可回退的 MIG 切片，不需要时只给任务卡和测试保护。`
- `只评审 <文档路径>，不要改文件；列出必改项、待确认项、证据缺口和能否进入下一阶段。`
- `更新 <既有文档路径>，保持文件名和已确认结论；只补本轮变化，不保留讨论过程。`
- `把 <权威 Markdown> 整理成 <DOCX/PDF>；不改变产品或工程语义，并检查目录、分页、表格、图片和中文字体。`

已有正式文档默认原路径更新，不因模板升级另建“新版”“最终版”或日期副本；讨论过程、被拒方案和修订轨迹进入评审报告、Decision Log、Goal Ledger、ADR 或任务记录。

### 5. 边界与授权

- 不要先设计一套角色接力再描述任务，也不要让多个专业 Skill 分别向用户作最终承诺。
- 不要把工具、模板、目标、计划或授权机制名当主流程；先看交付物、风险和证据。
- 不允许交付模拟模块、无业务入口 demo、内存版业务 Service 或看上去可用的样子货。
- 外部 Skill、工具、联网、安装、覆盖文件、Git、同步、生产数据、密钥、部署、删除或不可逆操作，必须先完成安全审查并取得对应授权。

## 安装

```bash
git clone https://github.com/fengwuxp/skills.git
cd skills
./sync-skills.sh --dry-run all
./sync-skills.sh all
scripts/validate-installed-skills.sh
```

同步单个 Skill 使用 `./sync-skills.sh senior-software-architect`。非默认目录使用 `CODEX_HOME=/path/to/codex-home`。同步 `wise-agent` 时，脚本会备份并退役旧 `delivery-collab`；同步后重启 Codex 或开启新会话。

## 验证与同步安全

修改 Skill、脚本或 fixture 后先验证，再预览同步：

```bash
./scripts/validate.sh
git diff --check
./sync-skills.sh --dry-run all
```

正式同步后运行 `scripts/validate-installed-skills.sh`，确认仓库管理的 Skill 文件一致且退役 Skill 已移除。`sync-skills.sh` 使用 `rsync --delete`，已有目标会备份到 `$CODEX_HOME/skills/.backups/`；`--dry-run` 不写入安装目录。

`scripts/evaluate-skills.py` 只做离线静态预检，不能替代真实 Agent 行为。完成正式同步后，可运行行为 smoke；它会先检查安装一致性，再通过配置的 Codex provider 发起只读请求，并把结果写到指定目录。`all` 覆盖通用产品、工程、三类 Superpowers 协同、轻量任务和跨轮状态恢复；只验证 Superpowers 时使用 `superpowers`，只验证控制机制时使用 `governance`：

```bash
scripts/smoke-wise-agent-behavior.sh --mode all --output-dir /tmp/wise-agent-smoke
scripts/smoke-wise-agent-behavior.sh --mode superpowers --output-dir /tmp/wise-agent-superpowers-smoke
scripts/smoke-wise-agent-behavior.sh --mode governance --output-dir /tmp/wise-agent-governance-smoke
scripts/smoke-wise-agent-behavior.sh --mode grill-me --runs 3 --output-dir /tmp/grill-me-smoke
```

`grill-me` 专项 smoke 会让真实 Agent 读取 PRD、决策记录、知识库、Java 源码和测试夹具，分别验证“证据已关闭时不提问”和“证据冲突时只问一个问题”；`--runs 3` 用于观察同一 prompt 的行为方差。该 smoke 仍只证明样例行为满足契约，不能单独证明所有任务的路由稳定性。跨轮任务需要审计状态一致性时，可把已有 Goal Ledger、Issue 或任务状态投影为 JSON 后运行 `python3 wise-agent/scripts/check_state_contract.py <contract.json>`；普通任务不需要手写状态契约。维护者同步或更新项目自有 `grill-me` 后，运行 `VALIDATE_GRILL_ME_INSTALL=1 ./scripts/validate.sh`；安装或更新官方 Superpowers 插件后，运行 `VALIDATE_SUPERPOWERS_INSTALL=1 ./scripts/validate.sh`。普通使用这些能力不需要运行安装校验。

## 维护者与高级扩展

### SkillX 导出规范

把 SkillX 或类似系统的候选能力转换为 Codex Skill Package 前，先读 [SkillX 到 Codex Skill Package 导出规范](./references/skillx-to-codex-skill-package.md)，完成输入契约、安全门禁、三层映射、生成流程和验证流程审查。第一版只接受人工审查后的离线 JSON，不自动读取历史轨迹、不采集用户数据、不引入外部训练流水线。

输入必须符合 `schemas/skillx-candidate.schema.json`；`scripts/skillx_export_adapter.py` 生成的候选包包含 `REVIEW.md` 和 `fixtures/trigger-prompts.md`：

```bash
python3 scripts/skillx_export_adapter.py --check-input --input fixtures/skillx/sample-candidate.json
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out
python3 scripts/skillx_export_adapter.py --validate-output /tmp/skillx-out/skillx-product-reviewer --input fixtures/skillx/sample-candidate.json
```

### 来源与自我改进

公开来源、读取状态和不吸收边界统一查 [仓库级来源索引](./references/source-map.md)；各 Skill 的专题证据保存在自己的 `references/source-map.md`，README 不复制来源正文。

Skill 内循环执行真实任务；外循环只把重复问题、验证失败、CR 结论和人工反馈转成最小改进 diff。不得从单次失败泛化永久规则，不得吸收个人偏好、私有轨迹、客户资料、生产数据、密钥、外部文章原文或 Agent 自述，也不得自动提交、同步或发布。完整约定见 [AGENTS.md](./AGENTS.md)。
