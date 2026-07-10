# Skills

本仓库用于维护可安装到 Codex 的 Skills。它不是轻量 prompt 集，而是一套可长期演进的 Agent 运行时资产库。

分层约定很简单：`AGENTS.md` 放全仓默认规则和安全边界；每个 `SKILL.md` 放触发入口、角色定位、核心流程和红线；详细方法、模板和知识放到对应 `references/`；确定性生成、验证、同步和安全检查放到 `scripts/`。Skill 改进只吸收脱敏后的执行记录、验证结果、CR 结论和人工反馈。

## 用户使用指南

Codex 会根据 `SKILL.md` 的 `name` 和 `description` 自动触发技能，也可以直接点名。同步后触发不符合预期，先重启 Codex 或开启新会话。

使用时不用背 Skill 名称。先说目标、材料、边界、风险和验证；拿不准入口时，直接说 `先帮我选路`。

### 1. 一句话讲清目标

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；已有 <材料或路径>；边界是 <不做什么 / 是否允许写入 / 风险>；验证要求是 <检查命令 / 证据 / 残余风险说明>。
```

材料可以是需求、PRD、页面、截图、DDL、代码路径、日志、测试输出或外部文章。风险要特别说明资金、合规、生产、密钥、部署、删除和不可逆操作。

### 2. 按交付物选入口

| 你要交付 | 默认入口 | 最小输入 |
| --- | --- | --- |
| 产品语义、业务架构规划、产品判断动作链、PRD、Backlog、验收、产品图 | `产品架构专家` | 业务目标、用户/主体、范围/非目标、材料、期望产物、验收、待确认项 |
| 系分、架构、代码、Bug、测试、CR、发布、生产变更、工程图 | `资深架构师` | 代码或文档路径、现象/目标、运行环境、约束、验证命令、是否允许改代码 |
| 跨角色产研交付、目标拆解、任务计划、Spec/Harness、质量门禁、生产交付审查、知识回流 | `AI Native Engineering Loop` | 当前材料成熟度、owner、写入/只读边界、授权策略、验证要求、停止条件 |
| DDL/schema/Java 类/字段表格到 Java Service 脚手架 | `java-service-code-generator` | 结构化输入、表名、业务模块、输出目录、是否允许覆盖 |
| Wind/Nobe 项目约规判断或项目 `AGENTS.md` Wind opt-in | `wind-project-coding-conventions` | 项目已 opt-in 的证据、待检查路径、规则问题、是否只做 CR |

图形化交付按语义归属选入口：产品语义图用产品专家，工程架构图用架构师。复杂可编辑架构图、代码库结构转图或架构描述转图先由架构师判断准入；复杂视觉续作再用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。

外部 Skill、工具、联网、安装、写配置或同步到 Codex，先做供应链安全审查和授权确认。

### 3. AI Native 只做编排

`AI Native Engineering Loop` 回答“现在由谁做、交接什么、怎么验证、什么时候停”，不是万能执行入口。产品正文回 `产品架构专家`，工程实现、TDD、源码级 CR 和发布风险回 `资深架构师`，结构化 Java Service 生成回 `java-service-code-generator`，Wind 约规回 `wind-project-coding-conventions`。

默认最小输出只保留：结论、当前阶段、owner、交接物、授权策略、验证与停止条件。需要时再补事实 / 推断 / 待确认 / 范围外不做、残余风险和下一 owner。只有用户要求完整方案、评审报告或模板，才展开 Loop Contract、RACI、验证矩阵、Goal Ledger 或内部实现层。

常用视图：

- **只读理解视图**：读代码库、对齐设计和代码、评估工具准入、做事实边界检查；默认不写文件、不联网、不安装。
- **产研交付视图**：按产品/交互、设计评审、TDD、编码、CR、质量评估、验证发布和复盘分角色推进。
- **验证发布视图**：覆盖测试矩阵、质量门禁、源码质量评审、生产交付审查、失败回退、发布监控和残余风险。
- **知识回流视图**：把已验证经验沉淀到 `AGENTS.md`、`CONTEXT.md`、ADR、reference、fixture、脚本、用户指南或 source-map；做上下文资产化、上下文治理、知识库、技术早报、培训、代码库教程、调研沉淀时，也可说 `进入知识生产 Loop`。

问决门禁是小闭环总门禁，`grilling` 是命中升级条件后的升级盘问。复杂或模糊任务一次只问一个主 blocker；能从材料、源码或测试自答的先自答；需要问 owner 时给建议答案、依据、影响和默认暂停点。角色 Loop 自动触发 `grilling` 只看四类信号：关键分叉未决、回答含糊 / 半答、连续返工、下一阶段会改变公共契约 / 状态机 / 验收样例 / 写入范围 / 发布风险。

用户说 `按你建议推进` 时，只关闭当前主 blocker、写入下一阶段输入，再挑下一最高价值 blocker；不重开全局规划。任务结束先做交付责任自检，再按问决门禁判断 `自决推进 / 询问 owner / 继续收敛 / 停止交接`。

### 4. 常用短句

- `先帮我选路`：判断入口、缺口、下一步 owner 和停止条件。
- `进入角色协作 Loop` / `进入产研交付视图`：按阶段分派产品、架构、Maker、Checker 和人工 owner。
- `进入只读理解视图`：只读分析代码库或材料，默认不写文件、不联网、不安装。
- `做生产交付审查` / `做质量门禁`：判断 Ready / Not Ready / Human Approval Required，并交代验证、回退和残余风险。
- `做业务架构规划`：产品专家输出业务能力、价值流、核心对象、能力-项目-系统映射和知识库回流计划。
- `做源码质量评审`：架构师按源码事实、项目约规、测试证据和风险给 P 级发现。
- `做 grilling 盘问` / `grill 一下这个方案`：只盘一个决策分支；每轮只回答接受建议、改答案、补材料或停止。
- `蒸馏业务专家`：生成可追溯 Skill Pack 草案、证据地图、成熟度、owner 追认问题和压力测试，不默认安装。
- `进入知识回流视图`：把已验证经验放到合适载体，不吸收一次性试错。
- `初始化/更新项目 AGENTS.md`：让 AI Native 进入项目约规入口；Wind 项目只做最小 opt-in patch。

### 5. 不要这样用

- 只写普通 PRD、产品方案或 Backlog 决策：直接用 `产品架构专家`。
- 只做系统设计、代码 CR、Bug、测试或生产变更：直接用 `资深架构师`。
- 只有自然语言需求、没有字段结构或表名：不要让 `java-service-code-generator` 直接生成生产代码。
- 不要把工具、模板、目标、计划或授权机制名当主流程；默认先看交付物和风险。
- 不允许交付模拟模块、无业务入口 demo、内存版业务 Service 或看上去可用的样子货。
- 涉及安装、联网、覆盖文件、Git、同步到 Codex、生产数据、密钥、部署或不可逆操作：先明确授权、写入范围、dry-run 和停止条件。

## 进阶能力索引

日常使用优先看上面的快速指南。本节只给维护者和需要精确路由的人查边界。

### AI Native Engineering Loop

- 路径：[ai-native-engineering-workflow](./ai-native-engineering-workflow)。
- 适合：跨产品、UED、架构、AI Maker / Checker、质量门禁和发布复盘的产研交付；也处理目标拆解、任务计划、Spec/Harness、代码库理解、工具准入、设计-代码对齐、知识回流和生产交付审查。
- 边界：只负责成熟度、owner、交接物、停止条件、授权策略和工具边界；产品正文交给产品专家，工程实现、最小正确实现检查和过度设计 CR 交给架构师，结构化代码生成交给代码生成器。

### 产品架构专家

- 路径：[product-architecture-expert](./product-architecture-expert)。
- 适合：PRD、产品方案、需求说明、业务架构规划、产品洞察、Backlog 决策、User Story/AC、概念生命周期、原型/HTML/页面截图/交互稿反推 PRD、能力地图、业务流程、状态机、规则矩阵、运营后台、数据指标、验收标准和产品架构图。
- 产品材料分散或提到 `pm-skills`、产品判断成流程、产品动作链、路线图取舍、发布复盘、增长实验时，先跑产品判断动作链。
- 边界：不替代法务、合规、财务、税务、持牌机构或卡组织规则确认；不负责工程实现、代码 Review 和生产排障。

### 资深架构师

- 路径：[senior-software-architect](./senior-software-architect)。
- 适合：架构设计、系统分析设计、技术方案、ADR、代码 Review、Bug 修复、测试/TDD、生产变更、架构图、遗留系统改造、架构排熵和工程治理。
- 边界：不替代产品专家定义复杂业务语义、PRD 和金融产品规则；不在缺少边界、风险和验收时直接给可上线方案。

### Wind 项目编码约规

- 路径：[wind-project-coding-conventions](./wind-project-coding-conventions)。
- 适合：项目 `AGENTS.md` 已 opt-in Wind 约规后，判断 face/impl、服务分层、模型归位、Entity 不外露、ServiceImpl、MyBatis Flex 和 TDD/CR 是否符合项目约规；也可初始化或改进 Wind 项目本地 `AGENTS.md` 模板。
- 边界：只做规则判断和偏差说明；未 opt-in 的普通 Java/Spring 项目不强套 Wind 约规；真实编码、TDD、源码级 CR、Bug 修复和生产风险仍交给 `资深架构师`。

### java-service-code-generator

- 路径：[java-service-code-generator](./java-service-code-generator)。
- 适合：根据 DDL/SQL、Java 类、字段表格或 schema 生成 Wind/Nobe 风格 Java Service 配套代码。
- 边界：不从纯自然语言直接生成生产代码；不替代架构师、DBA 或业务负责人确认表结构、索引、状态机和金额精度。

### 常见组合

- 从 AI 原型到工程化：AI Native 定义阶段、owner、门禁和验证矩阵；产品专家补产品上下文包；架构师补系统设计、TDD、源码级 CR 和发布风险。
- 从战略到项目组合：产品专家做业务架构规划；AI Native 只判断交接成熟度、owner、验证和停止条件。
- 从 PRD 到代码生成：先确认对象、状态、字段、索引和金额精度；已有 DDL、字段表格或 Java 类后，再用代码生成器。
- 从普通图到复杂图：先由产品专家或架构师产出语义稳定的 SVG；复杂可编辑架构图再评估 `$fireworks-tech-graph`。

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
```

仓库目录名可以自定义，不要求必须叫 `skills`。`sync-skills.sh` 会优先把脚本所在目录识别为技能仓库根，并同步同级的技能目录。同步后重启 Codex 或开启新会话，再通过 `$` 调用技能。

如需同步到非默认 Codex Home：

```bash
CODEX_HOME=/path/to/codex-home ./sync-skills.sh --dry-run all
CODEX_HOME=/path/to/codex-home ./sync-skills.sh all
```

## 验证与同步安全

修改技能、同步脚本或代码生成器后，执行统一验证：

```bash
./scripts/validate.sh
```

该脚本会检查 Bash 语法、供应链风险、YAML/frontmatter、reference 链接、关键触发路径、fixture、Python 编译、代码生成器、SkillX 导出、sync dry-run 和 `git diff --check`。

`sync-skills.sh` 使用 `rsync --delete` 保持安装目录和仓库技能目录一致。正式同步前必须先执行 `--dry-run`，确认 `CODEX_HOME` 和目标技能列表正确；正式同步会备份已有目标技能目录到 `$CODEX_HOME/skills/.backups/`。

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

详细约定见 [AGENTS.md](./AGENTS.md)。
