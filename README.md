# Skills

本仓库维护可安装到 Codex 的 Skills。它不是 prompt 集，而是一套按需加载、可验证、可同步和可持续演进的 Agent 运行时资产。

仓库按三级加载组织：`AGENTS.md` 保存全仓规则和安全边界；`SKILL.md` 保存触发、核心流程和红线；`references/` 保存详细知识与模板；确定性生成、验证和同步进入 `scripts/`。

## 用户使用指南

### 1. 30 秒上手

仓库把 `知止者` / `$wise-agent` 设计为默认智能行动主体。Codex 会根据各 Skill 的精确 description 隐式匹配当前任务所需能力，也可在同一 Agent 中加载多个 Skill；多 Skill 只是增加专业上下文，不产生第二人格或重复 Owner。日常不需要选角色或背 Skill 名称，直接说明目标、材料、边界、授权和验证即可；需要强制某项能力时再显式调用。

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；已有 <材料或路径>；边界是 <不做什么 / 是否允许写入 / 风险>；验证要求是 <检查命令 / 证据 / 残余风险说明>。
```

常见任务可以直接这样说：

| 任务 | 友好指令 |
| --- | --- |
| 自主推进 | `$wise-agent：读取当前项目事实，自己判断并推进；只在关键决策或高风险授权处问我，完成后给出产物、验证和残余风险。` |
| 只读 CR | `我有 PRD 和代码路径，只做只读 CR，不改代码；请给出源码证据、严重级别和残余风险。` |
| 产品设计 | `根据 <访谈/需求/原型> 写一版可评审 PRD，区分事实、推断、待确认和范围外不做。` |
| 工程交付 | `基于 <PRD/系分/源码> 完成 <Bug/TDD/重构/代码>，写入范围是 <路径>，验证命令是 <命令>。` |
| 决策盘问 | `做 grill-me 盘问：盘一下这个方案，一次只问一个主 blocker。` |
| 知识回流 | `进入知识回流视图：把这轮 CR 结论沉淀到项目约规，并说明权威落点和证据。` |
| 发布准入 | `做生产交付审查：只判断能不能发布，列证据、回退、人工确认点和停止条件。` |
| 项目约规 | `初始化/更新项目 AGENTS.md：只做最小项目约规 patch。` |

同步后触发不符合预期，先重启 Codex 或开启新会话。

### 2. 任务与专业能力

下表用于理解边界，不是使用前必须选择的菜单。所有专业 Skill 都允许依靠精确 description 隐式匹配；显式调用只表示强制或优先使用。

| 你要交付 | 专业能力与路径 | 最小输入 | 边界 |
| --- | --- | --- | --- |
| 跨领域真实工作、目标控制、能力组合、验证和知识演进 | `知止者`，路径：[wise-agent](./wise-agent) | 目标、事实源、范围、授权、完成证据 | 不限于产研；不获得无限自治或高风险授权 |
| 产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图 | `产品架构专家`，路径：[product-architecture-expert](./product-architecture-expert) | 用户/主体、目标、材料、范围、验收 | 不负责工程实现、代码 Review 和生产排障 |
| 系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图 | `资深架构师`，路径：[senior-software-architect](./senior-software-architect) | 路径、现象/目标、约束、验证命令、写入授权 | 不替代产品专家定义复杂业务语义、PRD 和金融产品规则 |
| 正式报告、制度、手册、研究说明、材料合并、文档审校、DOCX/PDF | `document-authoring`，路径：[document-authoring](./document-authoring) | 读者、用途、事实源、载体、验收方 | 不替代产品、工程、法律、合规或领域事实判断 |
| 汉字学、训诂、字源、甲骨文、金文、小篆、通假、异体考据 | `hanzi-philology`，路径：[hanzi-philology](./hanzi-philology) | 对象、时代、文本范围、材料、结论等级 | 《说文解字》只作证据之一，不单独证明本义 |
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

知止者不是流程路由器，而是持续读取事实、作出取舍并完成工作的统一行动主体。它按“察 -> 辨 -> 谋 -> 行 -> 验 -> 化”推进：先读事实，再辨问题，选择最小能力，完成实际工作，独立验证并回写结果。它不是不行动，而是让行动有方向、有分寸、有收口。

简单任务直接完成；复杂任务才使用计划、SDLC、Goal、Loop、Worker 或 Checker。专业能力按需渐进加载；产品、架构、文档、考据、生成和约规不是平级角色。人类责任 Owner、知止者、专业能力和独立 Checker 分开，无论内部用了多少能力，对用户只形成一个综合结论。

| 视图 | 适用任务 | 默认边界 |
| --- | --- | --- |
| 只读理解视图 | 代码库理解、设计-代码对齐、事实边界检查 | 默认不写文件、不联网、不安装 |
| 交付推进视图 | 产品、设计、TDD、编码、CR、验证发布和复盘回流 | 保持一个目标与行动主体，按阶段加载能力 |
| 验证发布视图 | 质量门禁、生产交付审查、失败回退 | 输出 Ready / Not Ready / Human Approval Required，不替代上线审批 |
| 知识回流视图 | 将已验证经验归位到约规、上下文、ADR、reference、fixture 或脚本 | 上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀可说 `进入知识生产`，形成可维护的上下文资产 |

决策澄清门禁只处理真正未决的 Decisions；Facts 先从材料、源码、测试或日志自答，Decisions 才问 owner。复杂或模糊任务一次只问一个主 blocker。结果只能是：`自决推进 / 询问 owner / 继续收敛 / 停止交接`。

`grill-me` 是升级盘问，不是每个任务的必经流程：

- 触发：关键分叉未决、回答含糊、连续返工，或下一步会改变公共契约、状态机、验收、写入范围或发布风险。
- 交互：你只需要回答接受建议、改答案、补材料或停止；用户说 `按你建议推进` 时只关闭当前 blocker。
- 退出：确认 shared understanding 并形成决策快照，未确认前不执行。
- 红线：红线、底线、不能碰、不可、禁止、必须等字眼必须进入决策快照或待确认项。

常用短句：`进入知止者`、`自己判断并推进`、`进入只读理解视图`、`做质量门禁`、`做源码质量评审`、`做生产交付审查`、`进入知识回流视图`。

### 4. 编写文档的友好指令

不需要记模板文件名，直接说明材料、目标路径和是否允许写入。产品、系分、重构三类正式设计文档各有一个权威模板入口：产品设计用 `product-prd-template.md`，系分设计用 `system-analysis-template.md`，迁移型重构用 `refactoring-design-template.md`。

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

`scripts/evaluate-skills.py` 只做离线静态预检，不能替代真实 Agent 行为。完成正式同步后，可运行行为 smoke；它会先检查安装一致性，再通过配置的 Codex provider 发起两个只读请求，并把结果写到指定目录：

```bash
scripts/smoke-wise-agent-behavior.sh --mode all --output-dir /tmp/wise-agent-smoke
```

该 smoke 只证明样例行为满足契约，不能单独证明所有任务的路由稳定性。维护者复装或更新外部 `grill-me` 后，运行 `VALIDATE_GRILL_ME_INSTALL=1 ./scripts/validate.sh`；普通使用 `grill-me` 不需要运行这些命令。

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
