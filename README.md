# Skills

本仓库用于维护可安装到 Codex 的 Skills。它不是轻量 prompt 集，而是一套可长期演进的 Agent 运行时资产库。

仓库采用分层治理：`AGENTS.md` 保存每个会话都应知道的默认规则和安全边界；各技能的 `SKILL.md` 保存特定任务的入口、路由和红线；详细知识、模板和方法论放在对应技能的 `references/` 中；确定性生成、验证、同步和安全检查放在 `scripts/` 中；使用者长期学习数据只保存在用户目录 `~/.skill-learning/` 或 `SKILL_LEARNING_HOME`，不进入仓库。

## 用户使用指南

安装或同步后，Codex 会根据每个 `SKILL.md` 的 `name` 和 `description` 自动判断是否触发对应技能。使用者也可以直接点名，例如“用产品架构专家……”“用资深架构师……”“用 java-service-code-generator……”。同步后如果触发不符合预期，先重启 Codex 或开启新会话。

使用时不用先背 Skill 名称，先把交付目标、现有材料、范围边界、授权方式和验证要求说清楚。拿不准入口时，直接说“先帮我选路”，让 Codex 先判断最小流程、owner、交接物和停止条件。

### 1. 先会用：一句话讲清目标

最小公式：

```text
我想交付 <生产可用能力 / PRD / 系分 / 代码 / 图>；已有 <材料或路径>；边界是 <不做什么 / 风险 / 是否允许写入>；验证要求是 <检查命令 / 证据 / 残余风险说明>。
```

这句话里最重要的是五件事：

- 目标：是产品定义、工程设计、代码实现、验证发布，还是完整生产可用能力。
- 材料：需求、PRD、页面、截图、DDL、代码路径、日志、测试输出或外部文章。
- 边界：哪些不做，是否允许写文件，是否允许联网、安装、提交或同步。
- 风险：是否涉及资金、合规、生产、密钥、部署、删除或不可逆操作。
- 验证：希望运行什么检查，或者至少要求给出证据、残余风险和待确认项。

常用起手：

- `先帮我选路`：根据当前材料判断应该用 AI Native、产品架构专家、资深架构师还是 java-service-code-generator；说明理由、缺口、下一步 owner 和停止条件。
- `用产品架构专家`：把想法、反馈、原型、页面、PRD 草稿或业务材料整理成可评审的产品产物。
- `用资深架构师`：处理系分、架构设计、代码 CR、Bug、测试、TDD、生产风险或工程验证。
- `进入 AI Native 交付 Loop`：以交付生产可用能力为目标，从产品分析、系分、编码、TDD、CR 到验证发布；旧说法“进入 GSD 产研协同研发流程”会映射到这个入口。

### 2. 再会选：按交付物找入口

- 产品语义 / PRD / Backlog / 验收：用 `产品架构专家`，先把用户、主体、目标、对象、流程、规则、验收和待确认项讲清楚。
- 产研协同 / GSD / CAD / Goal / Spec / Harness：用 `AI Native Engineering Loop`，它负责 Loop Profile、owner、顺序、交接物、门禁、授权策略和停止条件；GSD/CAD/Goal 是内部层，不替代正文产物或源码实现。
- 系分 / 架构 / 代码 / Bug / 测试 / CR / 发布：用 `资深架构师`，直接进入工程事实、源码锚点、验证命令和生产风险。
- Java Service 脚手架：只有 DDL、schema、Java 类或字段表格齐全时，才用 `java-service-code-generator`；业务语义和表设计仍需先确认。
- 图形化交付：产品语义图用产品专家，工程架构图用架构师；复杂可编辑架构图、代码库结构转图或架构描述转图先由架构师判断是否使用 Architecture Diagram Generator；复杂视觉续作用 `$fireworks-tech-graph`。正式图形默认 SVG，PNG 仅在明确要求时导出。

### 3. 再会编排：体用原则

- 体：业务目标、用户/主体、生产边界、风险责任、验收标准和证据边界。
- 用：Skill、工具、模板、图、代码、测试、提交和发布动作。
- 先定体，再调度用。目标和验收不清时，不急着进入执行 Loop、代码生成或工具安装。
- 体用合一：每个产物和工具调用都要回指交付目标、风险边界和验证证据。
- 避免体用混一：不要把 AI 原型、GSD/CAD/Goal、Architecture Diagram Generator、代码生成、图或测试替身当成业务价值本身。
- 阴阳互根：产品专家负责价值、对象和验收种子；架构师负责实现、约束和工程风险；AI Native 把两侧接成闭环。
- 执简驭繁：小任务直接用专门 Skill；跨角色、跨阶段、跨工具或高风险任务，再让 AI Native 编排。

### 4. 顶层处事原则

所有 Skill 共用一组顶层原则，完整约规见 `AGENTS.md`。日常使用时可以记成一句话：先看事实，先定核心，先明边界；以体统用，以证据闭环，以真实交付为准。

- 先读事实，后生判断：先看一手材料、源码、测试、日志、用户原话和明确证据。
- 先抓核心，后开药方：先区分症状、结构证据和真正的问题机制，再决定流程、工具、重构或测试。
- 先定名、定向、定性、定位，再定量：概念、方向、性质和落点未定前，不急着谈工期、容量、覆盖率或任务数。
- 以真实交付为准：GSD、CAD、Goal、Loop、代码生成和图形化交付都要回到可验证、可接手、可上线或可明确停止的真实能力。
- 事实、推断、待确认、范围外不做分层表达：证据不足时停止补上下文，不把猜测包装成结论。

### 5. 常用短句

- `进入 AI Native 交付 Loop`：产品专家先做需求分析、产品设计、确认和验收种子，架构师再做系分设计、编码、TDD、CR 和验证，AI Native 只编排流程和门禁；GSD/CAD/Goal 作为内部层自动选择。
- `进入只读理解 Loop`：阅读分析代码库、对齐设计和代码、评估工具准入或做事实边界检查；默认不写文件、不联网、不安装。
- `进入验证发布 Loop`：编排测试矩阵、质量门禁、CR 前置条件、发布监控、失败回退和复盘。
- `进入知识回流 Loop`：把已验证经验沉淀到 Skill、reference、fixture、脚本、用户指南或 source-map。
- `进入知识表达门禁`：把口头目标、文章观点、AI 草稿或模糊想法整理成目标、对象、规则、约束、验收样例、反馈源和缺口 owner；不满足时不进入执行 Loop 或编码。
- `进入非标问题模式`：老板、客户、运营或工程问题没有标准答案时，先定义真实问题、影响面、关键不确定性、候选方案、最小可逆实验、验证标准和停止条件。
- `GSD + Goal 按任务计划推进`：作为交付 Loop 的 Goal + GSD 内部层形成 Plan Grant，范围内低风险本地任务按计划推进；Goal 不替代 Execution Grant，Git、联网、生产、密钥、部署和不可逆操作仍需显式授权。
- `生产可用 Loop 门禁`：检查 Agent Loop 是否有自动化心跳、隔离执行、可复现状态、独立验证、观测审计、人工接管和发布/回滚；能自动跑不等于能上线。
- `进入实际项目编码 Loop`：把一个真实代码库 Goal / Wave / Task 变成 Read-only scout、RED、Implement、Verify、Checker、状态回写和提交候选；必须有写入范围、失败测试或验收样例、验证命令和独立 Checker。
- `进入反馈闭环成熟度 / 验证簇门禁`：当测试通过、覆盖率提升或 AI 补测仍不能证明高风险业务没变坏时，围绕业务不变量建立验证簇，输出场景测试、属性 / 变形测试、历史回归、生产重放样本、有限变异 / 对抗检查、置信度、CI 分层和停止条件。
- `三卡交接`：产品专家给 Product Context Card，AI Native 给 Engineering Handoff Card，生产可用 Loop 再给 Production Loop Card；三卡都不是 Execution Grant、测试通过或上线审批。
- `做 PRD / 系分合议预审`：用 MAGI 三角色先挑刺，输出 `ACCEPT/REJECT/PENDING` 决策日志和下一步路由。
- `提炼顶层原则 / 处事方式`：先判断哪些规则应进入 `AGENTS.md`，哪些只属于 AI Native、产品专家、架构师或某个 reference；不要把一次性启发写成跨技能硬规则。
- `做事实边界检查`：区分事实、推断、待确认和范围外不做，禁止无根据猜测、模型脑补或超出用户目标的实现扩张。
- `阅读分析代码库`：只有代码库级理解、设计-代码对齐、上下文工程或工具准入才走 AI Native；单个文件、函数、报错或 PR diff 直接用资深架构师。
- `评估 Understand Anything / 代码库知识图谱工具`：只在大型代码库理解、团队共享图谱、diff impact 或 onboarding 明确需要时纳入工具准入；默认不安装、不写 `.understand-anything/`、不启用 auto-update / hook、不提交图谱。
- `判断是否使用 Architecture Diagram Generator`：复杂可编辑架构图、代码库结构转图、架构描述转图或多层架构图由架构师先做准入；来源未审查时只输出准入缺口，不安装、不联网、不执行脚本。
- `整理最终 PRD / 系分`：正式交付文档只保留当前有效结论、范围、规则、风险、待确认和验收；讨论过程、迭代草稿、AI 推理轨迹和被拒方案进入评审报告、Decision Log、Goal Ledger、ADR 或任务计划。

### 6. 默认闭环

1. 产品发现：`产品架构专家` 收束问题、证据、对象、规则、验收种子和待确认项。
2. 三卡交接：产品专家输出 Product Context Card，AI Native 输出 Engineering Handoff Card；需要持续推进时补 Production Loop Card。
3. 编排准入：`AI Native 研发流程编排` 判断输入成熟度、owner、交接物、授权策略、门禁、停止条件和下一步分派。
4. AI Native 交付 Loop：中大型项目先固定 Goal、GSD Wave、Spec/Harness、预算 / 时间盒、状态、写入范围、验证命令和交接节奏。
5. 实际项目编码 Loop：需要持续推进真实代码任务时，AI Native 先固定 Coding Loop Contract，再由 `资深架构师` 承接 TDD、实现、验证和 CR。
6. 工程执行：`资深架构师` 承接系统设计、编码、TDD、补测试、CAD 门禁、源码级 CR 和发布风险。
7. 质量理解门禁：AI Native 编排测试矩阵、验证顺序、理解门禁、工具准入和影响范围证据。
8. 交付复盘：检查一次通过率、返工率、CR 轮次、缺陷密度、知识回流和残余风险。

### 7. 不要这样用

- 只写一份普通 PRD、产品方案或 Backlog 决策：不要让 AI Native 代写正文，直接用 `产品架构专家`。
- 只做系统设计、代码 CR、Bug、测试或生产变更：不要让产品专家接工程问题，直接用 `资深架构师`。
- 只有自然语言需求、没有字段结构或表名：不要让 `java-service-code-generator` 从纯自然语言直接生成生产代码。
- 只说“画图”但没有对象、关系、受众和视图类型：先补图形 brief，再由产品专家或架构师出 SVG。
- GSD、CAD、Goal、Loop、Codex 替我审批都不是无条件授权；越过 Grant 范围、写入边界、验证失败或高风险业务时必须停下确认。
- GSD 模式的目标是交付生产可用能力，不允许让 AI 随机推进模拟模块、无业务入口 demo、内存版业务 Service 或看上去可用的样子货。
- 涉及安装、联网、覆盖文件、Git、同步到 Codex、生产数据、密钥、部署或不可逆操作：先明确授权、写入范围、dry-run 和停止条件。

### 8. 最小输入清单

- `AI Native 研发流程编排`：当前材料成熟度、目标产物、涉及 owner、写入/只读边界、授权策略、验证要求、是否需要 GSD/CAD/Goal/工具准入。
- `产品架构专家`：业务目标、用户/主体、范围/非目标、输入材料、希望输出的产品产物、验收和待确认项。
- `资深架构师`：代码或文档路径、现象/目标、运行环境、约束、期望验证命令、是否允许改代码或只做 CR。
- `java-service-code-generator`：DDL/schema/Java 类/字段表格、表名、业务模块、输出目录、是否允许覆盖已有文件。
- Architecture Diagram Generator：来源/安装包、是否已审查、架构描述或代码库锚点、视图层级、节点/分组、箭头语义、输出格式、是否允许联网/读写/安装。
- Understand Anything：官方来源、安装方式、扫描范围、排除目录、是否允许联网 / clone / dashboard、是否允许写 `~/.understand-anything` 和项目 `.understand-anything/`、是否允许 auto-update / hook / 提交图谱、敏感文件处理、图谱用途和人工 CR owner。
- `$fireworks-tech-graph`：图形语义、节点关系、受众、风格要求、输出格式和是否需要基于已有 SVG 续作。

### 9. 不同场景最佳实践

- **不知道该用哪个 Skill**：先说 `先帮我选路`，并给出目标、材料、边界和验证要求。最佳输出不是正文，而是“推荐入口、为什么、缺什么、下一步 owner、什么时候停”。
- **只写普通 PRD、产品方案或 Backlog 决策**：直接用 `产品架构专家`。最佳实践是先收束主体、对象、流程、规则、验收种子和待确认项；正式 PRD 只放最终结论，讨论过程放评审报告、Decision Log 或任务计划。
- **从想法推进到可开发方案**：先由 `产品架构专家` 产出 Product Context Card，再由 `AI Native Engineering Loop` 判断进入只读理解、产研交付、验证发布还是知识回流，最后交给 `资深架构师` 做系分、TDD、CR 和验证。
- **大项目要进入交付 Loop**：用 `AI Native Engineering Loop` 固定真实交付目标、成功标准、GSD Wave、Atomic Task、CAD 候选、Plan Grant、验证证据和停止条件。最佳实践是按阶段形成可验证切片，Git 提交仍需授权；避免让 AI 推进模拟模块、无业务入口 demo 或内存版业务 Service。
- **需要持续自动推进或后台 Agent**：先做 `生产可用 Loop 门禁`。最佳实践是检查状态载体、隔离执行、Maker / Checker、预算 / 时间盒、独立验证、人工接管、发布 / 回滚和残余风险；能自动跑不等于能上线。
- **真实代码任务要用 Loop 推进**：说 `进入实际项目编码 Loop`。最佳实践是先绑定一个 Task ID，明确写入范围、只读范围、失败测试或验收样例、验证命令、Checker 输入、状态回写位置、提交切片和回滚方式；缺这些时只做只读侦察或补上下文。
- **高风险域要证明没变坏**：说 `进入反馈闭环成熟度 / 验证簇门禁`。最佳实践是先确认 3-5 个业务不变量，再让 AI Native 判断 L2/L3/L4/L5 候选，由架构师把验证簇落到测试、生产重放证据、有限变异 / 对抗检查、置信度和 CI 分层；生产重放只能作为证据，不能反向定义需求。
- **阅读分析代码库或对齐设计和代码**：代码库级理解、设计-代码对齐、工具准入或知识图谱用 `AI Native 研发流程编排`；单个文件、函数、报错或 PR diff 直接用 `资深架构师`。最佳实践是要求源码锚点、入口路径、影响模块、测试证据和残余风险。
- **系统设计、Bug、测试、CR 或生产变更**：直接用 `资深架构师`。最佳实践是提供代码路径、现象、日志、测试命令、运行环境和不允许触碰的边界；评审时先列 P0/P1/P2 风险，再给验证建议。
- **根据结构化输入生成 Java Service 代码**：用 `java-service-code-generator`，但只在 DDL/schema/Java 类/字段表格清楚时使用。最佳实践是先生成到评审目录，明确是否允许覆盖，再由架构师做源码级 CR 和测试补强。
- **画产品图、流程图、架构图或代码库图**：先确定受众、对象、关系、视图类型和输出格式。产品语义图走产品专家，工程架构图走架构师；复杂可编辑架构图先由架构师判断 Architecture Diagram Generator 准入；正式图形默认 SVG，PNG 仅在明确要求时导出。
- **吸收外部文章、仓库或工具经验**：先实际读取正文、仓库文件或官方材料，再提炼可迁移原则、路由、检查项和边界。最佳实践是先出建议和影响范围，再决定是否改 Skill、reference、fixture 或脚本。
- **提交、同步或安装到 Codex**：先做 CR、触发验证和 `./scripts/validate.sh`；同步前先执行 dry-run 并确认目标目录。Git、联网、安装、删除、覆盖、生产、密钥、部署和不可逆操作都需要明确授权。

## 完整能力索引

下面是完整能力索引。日常使用优先按上面的选路和默认流程短句下指令；只有需要确认边界、参考来源或不适用场景时，再看本节详细说明。

[AI Native Engineering Loop](./ai-native-engineering-workflow)

- 适合：AI 时代产品到研发编码流程、Agentic Engineering、产品专家到架构师交接、AI 原型 / 评测到 PRD-Lite/OpenSpec/Harness、统一 Loop 准入、GSD/CAD/Goal 内部层、Agent Loop Engineering / `/goal` / `/loop` 准入、Spec/SDD 模板最佳实践、PRD/系分合议预审、AI 代码交付闭环、AI 原生工具协作、Gemini CLI/AgentRC/Understand Anything 等代码理解工具安装与调用准入、设计-代码对齐、代码库知识图谱准入、质量/测试门禁、代码库理解结论包、变更可理解性/影响可视化门禁、验证矩阵、CR 流程门禁、发布复盘和组织职责边界。
- 边界：可以作为 PRD、Backlog、架构设计、代码 CR、测试、生产变更或 Java Service 代码生成的流程入口，但只负责成熟度、owner、交接物、停止条件和工具边界；具体产物继续分派给产品专家、架构师或代码生成器。
- 常用说法：“进入 AI Native 交付 Loop”“进入只读理解 Loop”“进入验证发布 Loop”“进入知识回流 Loop”“设计一套 AI 时代产品到研发编码流程”“把产品专家、架构师和 Codex/Claude/Copilot 这类 AI 工具协同起来”“对 PRD 和系分做 MAGI 三角色合议预审”“评审我们的 AI 编码流程是否有 OpenSpec、Harness、验证矩阵和 CR 闭环”“落地 Spec 模板最佳实践”“编码提速了但交付没有体感，做 AI 代码交付闭环评审”“做 GSD + Goal，把目标、成功标准、Wave、CAD 候选、验证证据和停止条件串起来”“进入 Agent Loop Engineering 模式，让 /goal / /loop / auto mode 按状态、反馈、验证和停止条件持续推进”“判断大项目是否进入 GSD Round 0、Wave、Atomic Task 和 CAD 候选”“评估是否安装 Gemini CLI / AgentRC / Understand Anything 阅读代码”“评估代码库知识图谱工具”“用 AI 快速阅读代码库并整理结论包”“对齐设计和代码实现”“AI 生成代码后怎么让团队看懂结构和影响范围”“从 AI 原型到工程化怎么交接”。

[产品架构专家](./product-architecture-expert)

- 适合：PRD、产品方案、需求说明、产品洞察/机会雷达、机会清单/Backlog 决策、需求优先级、User Story/AC、原型/HTML/页面截图/交互稿反推 PRD、能力地图、业务流程、状态机、规则矩阵、运营后台、数据指标、验收标准和产品架构图。支付与资金是重点能力，覆盖账户/账本、清结算、对账、外卡收单、ACH、VCC、争议和跨境支付。
- 进阶模式：复杂 PRD、AI 生成方案、原型候选、多方争议或用户要求多个 AI / PM / Reviewer / 产品大师 / MAGI 合议评审时，先做阶段门、共识、分歧、必改、待确认、owner 和验证方式，再决定是否进入正式 PRD、Backlog、AI Native 编排或架构师交接。
- 不适合：不替代法务、合规、财务、税务、持牌机构或卡组织规则确认；不负责工程实现、代码 Review 和生产排障。
- 常用说法：“用产品架构专家写一版 PRD”“把这批客户访谈和竞品资料整理成机会雷达”“把这批机会清单做 Backlog 决策并转 User Story/AC”“根据页面截图反推可评审 PRD”“用产品大师/MAGI 方式多视角评审这个 AI 生成 PRD”“画一个 VCC 交易流程”“梳理清结算和对账能力地图”“评审这个需求是否可开发可验收”。

[资深架构师](./senior-software-architect)

- 适合：架构设计、系统分析设计、技术方案、ADR、代码 Review、Bug 修复、测试/TDD、生产变更、架构图和工程治理。擅长 Java/Spring/Wind，也能先识别非 Java 项目的本地生态。
- 不适合：不替代产品专家定义复杂业务语义、PRD 和金融产品规则；不在缺少边界、风险和验收时直接给可上线方案。
- 常用说法：“用资深架构师做一轮 CR”“评审这个系统设计”“分析这个 Bug 根因并补测试”“画一张服务架构图”。

[java-service-code-generator](./java-service-code-generator)

- 适合：根据 DDL/SQL、Java 类、字段表格或 schema 生成 Wind/Nobe 风格 Java Service 配套代码，包括 Entity、Mapper、DTO、Request、Query、Converter、Service、ServiceImpl 和测试夹具。
- 不适合：不从纯自然语言直接生成生产代码；不替代架构师、DBA 或业务负责人确认表结构、索引、状态机和金额精度；不默认覆盖已有文件。
- 常用说法：“根据这段 DDL 生成 Java Service 配套代码”“把这个字段表格转换成脚手架”“先生成到评审目录，不覆盖已有文件”。

### 如何选择

- 要设计 AI 时代产品到研发编码的整体工作流，用 `AI Native 研发流程编排`；其中产品语义由 `产品架构专家` 承接，工程实现由 `资深架构师` 承接。
- 先定业务和验收，用 `产品架构专家`；再定工程结构、代码、测试和发布，用 `资深架构师`。
- 有原型、页面截图、HTML、交互稿或模糊想法，需要反推需求、流程、规则和待确认问题，用 `产品架构专家`。
- 已有代码、报错、测试失败、工程坏味或生产现象，直接用 `资深架构师`。
- 已经有明确表结构、字段表格或 Java 类，并且目标是生成配套代码，用 `java-service-code-generator`。
- 需要图形化交付时，架构师和产品专家都会默认产出 SVG；PNG、PDF、截图、Mermaid 或 Markdown 草图只有在使用者明确提出时才处理。
- 需要复杂可编辑架构图、代码库结构转图、架构描述转图或多层架构图时，先让 `资深架构师` 判断是否使用 Architecture Diagram Generator；它只做可编辑架构图草案生成，不替代架构判断、CR、测试、发布验证，也不在来源未审查时安装或执行。
- 如果需要更复杂、更好看的技术图、能力图、架构图或风格化图形，先让产品专家或架构师产出图形语义、对象边界和 SVG 初稿；需要继续美化、风格化或复杂图形工程时，可以明确调用 `$fireworks-tech-graph` 续作。
- 涉及金融、支付、资金、卡组织、ACH、跨境、合规或监管时，先让产品专家标出主体、法域、资金归属、外部规则来源、待确认方和验收边界，再进入工程设计。

### 常用组合路线

- 从 AI 原型到工程化：`AI Native 研发流程编排` 先定义阶段、门禁、owner、AI 工具角色、GSD/CAD 编排准入、Goal 组合、Agent Loop Engineering、AI 代码交付闭环、质量/测试门禁、代码库理解结论包、变更可理解性/影响可视化门禁和验证矩阵；`产品架构专家` 补产品上下文包、Backlog 和 PRD-Lite；`资深架构师` 补 OpenSpec、Harness、GSD/CAD 工程任务包、测试策略、TDD、补测试、源码级 CR 和发布风险。
- 从想法到工程：`产品架构专家` 先把目标、对象、流程、规则、验收和待确认项定清楚；`资深架构师` 再承接系统设计、代码、测试和发布风险。
- 从原型到 PRD：`产品架构专家` 根据原型、HTML、页面截图或交互稿反推 PRD，先补角色、对象、状态、规则、数据和验收，不只描述页面控件。
- 从 PRD 到代码生成：先用 `产品架构专家` 或 `资深架构师` 确认对象、状态、字段、索引和金额精度；已有 DDL、字段表格或 Java 类后，再用 `java-service-code-generator` 生成配套代码。
- 从普通图到复杂图：先用 `产品架构专家` 或 `资深架构师` 产出语义稳定的 SVG；需要更复杂的布局、风格系统或精细视觉时，再调用 `$fireworks-tech-graph` 续作。
- 从架构描述到可编辑架构图：先用 `资深架构师` 固定视图层级、源码/配置/测试锚点、节点/箭头语义和风险边界；来源已审查且工具可用时，再让 Architecture Diagram Generator 生成可编辑草案，最后回到架构师做校验。
- 从金融产品到上线方案：`产品架构专家` 先标出主体、法域、资金归属、外部规则和专业确认方；`资深架构师` 再处理系统边界、数据一致性、可靠性、安全和发布回滚。

### 产品架构专家怎么用

`产品架构专家` 是产品语义和产品交付物的主入口。它适合回答“这个需求到底要解决什么、对象和规则是什么、谁验收、怎么让研发接得住”，不负责工程实现、代码 CR、生产排障或 GSD/CAD 执行授权。

优先直接用它的场景：

- **想法 / 口头需求 / 原型候选**：先补目标、用户、主体、范围、非目标、核心对象、主流程、风险和验收种子。
- **PRD / 产品方案**：生成、精简、重构或评审可读、可开发、可测试、可运营的正文。
- **需求评审前置扫描**：评审会前用完整性、一致性、可测试性、二义性四维度先找疑似问题和追问点，再由 owner 决策。
- **AI 生成方案 / 多方争议**：用产品大师 / MAGI / PM / Reviewer 合议评审，先收束共识、分歧、必改、待确认、owner 和验证方式。
- **客户访谈 / 工单 / 竞品 / 行业资料**：整理机会雷达、证据链、Backlog 候选、User Story 和 AC。
- **支付与资金产品**：先确认主体、法域、资金归属、账户/账务边界、外部规则来源、专业确认方和验收边界。
- **产品图形化交付**：输出用例图、能力地图、业务流程图、状态机、规则矩阵、运营后台结构或资金流图；默认 SVG。

使用时尽量给清楚五类信息：

```text
用产品架构专家：
输入材料：想法 / 访谈 / 竞品 / 原型 / 截图 / PRD 草稿 / 支付规则
目标产物：PRD / 产品方案 / 机会雷达 / Backlog / 验收标准 / 产品架构图
业务边界：目标、非目标、主体、用户、法域、资金或数据边界
评审重点：可读性 / 准确性 / 可开发 / 可测试 / 可运营 / 合规待确认
验证要求：列待确认项、owner、验收种子；正式交付前运行产品交付物检查
```

产品专家交给 AI Native 或架构师前，最好形成一个轻量交接包：业务目标、非目标、角色 / 主体、核心对象与状态、主流程与异常、关键规则、验收种子、风险与待确认项、专业确认方。缺这些时，不要急着进入系分、GSD/CAD 或代码生成。

如果进入 AI Native 流程，这个轻量交接包应整理成 Product Context Card：它只交产品事实和验收种子，不判定 GSD/CAD 准入，不生成 Engineering Handoff Card、Production Loop Card 或 Execution Grant。

### AI Native Engineering Loop 怎么用

`AI Native Engineering Loop` 是编排入口，不是万能执行入口。它适合回答“现在应该进入哪个 Loop、由谁做、做到哪一步、交接什么、怎么验证、什么时候停”，再把产品语义交给 `产品架构专家`，把工程实现和生产风险交给 `资深架构师`。

它承接 AI Native 产品研发流程，但不直接替代 PRD 正文、系分正文、代码实现、测试通过、CR 结论或上线审批；核心职责是把 Goal、State、Plan、Action、Observe、Decide、Verify、Stop/Handoff、owner、交接物、授权策略和验证门禁排成可执行链路。

优先用它的场景是跨角色、跨阶段、跨工具的流程问题：从 AI 原型到 PRD-Lite / OpenSpec / Harness，产品专家和架构师如何接力，大项目如何用 GSD Wave 做计划、用 CAD Atomic 做原子执行、用 Goal 保持目标和状态一致，编码提速如何转成最终代码交付能力，质量 / 测试 / CR / 发布门禁如何闭环，Gemini CLI / AgentRC / Understand Anything 等工具是否允许安装或调用。只写一份 PRD、只做产品方案或 Backlog 决策时，直接用 `产品架构专家`；只做系统设计、代码 CR、Bug、测试或生产变更时，直接用 `资深架构师`。

瘦身后的职责边界：`产品架构专家` 只补产品上下文包、验收种子和产品侧交接条件，不直接判定 GSD/CAD 准入或 Execution Grant；`AI Native Engineering Loop` 负责端到端 Loop 准入、GSD/CAD 内部层准入、授权策略、AI 代码交付闭环、质量/测试门禁、代码库理解结论包和变更可理解性/影响可视化协作位，只编排 GSD Round 0、Wave/Atomic Task 候选、CAD 候选缺口、授权策略缺口、Spec 强度、独立验证证据、CR 减负、知识回流、测试矩阵、验证顺序、CR 前置条件、失败回退、入口路径、源码锚点、结构影响说明和残余风险交接；`资深架构师` 只消费已确认的 AI Native 交接结论，继续做 OpenSpec、Harness、工程编排、CAD 门禁、测试策略、TDD、补测试、源码级 CR 和风险，不在架构师侧重建产品流程。

新流程默认用三张卡降低协作噪声：Product Context Card 由产品专家给出业务事实、对象规则和验收种子；Engineering Handoff Card 由 AI Native 给出 Goal、Spec/AC、Wave/Task、写入范围、验证命令、授权策略和停止条件；Production Loop Card 只在 Loop、auto mode、后台 Agent 或持续推进时补充状态载体、自动化心跳、隔离执行、Maker / Checker、独立验证、预算、人工接管和发布/回滚。三卡都不能替代 Execution Grant、测试通过、CR 结论或上线审批。

最短触发方式：

- `进入 AI Native 交付 Loop`：以交付生产可用能力为目标，产品专家先做需求分析、产品设计、确认和验收种子，架构师再做系分、编码、TDD、CR 和验证；旧说法“进入 GSD 产研协同研发流程”映射到这里。
- `进入只读理解 Loop`：阅读分析代码库、设计-代码对齐、工具准入、事实边界检查或影响范围识别；默认只读。
- `进入验证发布 Loop`：编排测试矩阵、CR、发布门禁、监控、回滚、残余风险和复盘。
- `进入知识回流 Loop`：把已验证经验沉淀到 Skill、reference、fixture、脚本、用户指南或 source-map。
- `GSD + Goal`：作为交付 Loop 的 Goal + GSD 内部层，把业务目标、生产可用能力、成功标准、GSD Wave、CAD 候选、验证证据、预算 / 时间盒、停止条件、Goal 状态和交接节奏串起来。
- `GSD + Goal 按任务计划推进`：把 Goal 任务计划升级为 Plan Grant，低风险本地任务按计划推进，不再每个任务都停下来等 Execution Grant；默认给提交切片，授权后可按已验证任务做本地 commit。
- `生产可用 Loop 门禁`：把 Agent Loop 从自动执行候选升级为可生产化门禁，检查状态落盘、隔离执行、Maker / Checker 解耦、观测审计、人工接管、发布/回滚和理解债。
- `做 PRD / 系分合议预审`：用 MAGI 三角色先挑刺，再输出 `ACCEPT/REJECT/PENDING` 决策日志和下一步路由。
- `做 PRD 评审会前预扫描`：产品专家先按完整性、一致性、可测试性、二义性输出疑似问题，AI Native 再把结果接入合议预审和决策日志。
- `做 GSD/CAD 准入`：判断是否需要 Round 0、Wave/Atomic Task、CAD 候选缺口、授权策略和显式确认缺口。
- `开启 GSD/CAD 计划内授权策略`：把自动推进拆成只读、计划内低风险执行、Plan Grant、Wave Grant、CAD Grant、阶段提交策略和显式确认；Codex “替我审批”只作为已启用的低风险审批通道。
- `落地 Spec 模板最佳实践`：先区分 PRD / SDD / 实现 Spec 三层是否齐备，再输出 Spec 强度、五段式骨架、AC 与测试映射、spec-lint、AC 覆盖、漂移检查、风险自查和轻重切换。
- `做 AI 代码交付闭环`：判断编码提速为何没有交付体感，补 Spec 强度、Harness 独立验证、CR 减负、知识回流和指标。
- `做质量门禁`：编排测试矩阵、验证顺序、CR 前置条件、失败回退和残余风险交接。
- `做理解门禁`：让代码库、AI 生成 diff 或重构计划具备入口路径、源码锚点、影响模块和验证证据。
- `评估 Gemini CLI / AgentRC / Understand Anything`：只做工具准入、权限边界、只读范围、隐私风险和人工替代路径；不默认安装、联网、写 `.understand-anything/`、启用 hook 或提交图谱。

先判断输入成熟度，再选最小 Loop Profile：

- **Round 0 补齐**：只有想法、文章观点、口头需求、原型截图或工具宣传时，先补问题、证据、owner、风险、验收和待确认项。
- **交接包模式**：已有 AI 原型/eval、dogfooding 反馈、MVP 或业务目标时，整理产品上下文包、PRD-Lite 缺口和交给架构师的最小材料。
- **只读理解 Loop**：代码库阅读、设计-代码对齐、工具准入、事实边界检查和影响范围识别；输出理解包、源码锚点、缺口和下一 owner，不写文件。
- **产研交付 Loop**：说“进入 AI Native 交付 Loop”或旧说法“进入 GSD 产研协同研发流程”时，以交付生产可用能力为目标，先让产品专家做需求分析、产品设计、方案确认和验收种子，再让架构师做系分设计、编码、TDD、测试、CR 和验证发布；本技能只编排 owner、交接物、门禁和停止条件，不让 AI 随机推进模拟模块、内存版业务 Service 或样子货。
- **Goal 目标层**：说 `GSD + Goal`、`CAD + Goal` 或目标驱动推进时，输出 Goal 卡、GSD Wave / Goal 映射、CAD 候选关联、Spec / AC 映射、Goal 状态、预算 / 时间盒、验证证据、提交切片、Plan Grant 判断、授权策略、停止条件、交接节奏和 Ledger 更新；Goal 不等于 Execution Grant，只有 Plan Grant 字段齐备时才推进范围内低风险任务。
- **GSD/CAD 内部层**：已有产品上下文、OpenSpec 或明确变更目标时，在交付 Loop 内设计 GSD/CAD 编排准入结论、Harness 摘要、GSD Wave 建议、CAD 候选缺口、授权策略、显式确认缺口和验证矩阵草案。
- **授权策略模式**：用户要求 GSD/CAD 计划内授权、按任务计划推进、自动推进、阶段提交或 Codex “替我审批”时，输出只读 / 计划内低风险执行 / Plan Grant / Wave Grant / CAD Grant / Git 策略 / 显式确认分级；Plan Grant 字段齐备后，范围内低风险本地任务直接推进，Git 提交只有授权后才执行，联网、生产等硬边界仍显式确认。
- **PRD / 系分预审模式**：PRD、PRD-Lite、OpenSpec 输入、系分、详细设计或 Harness 候选需要正式评审前预审时，按 MAGI 三角色做多视角合议，输出锚点化问题、`ACCEPT/REJECT/PENDING` 决策日志、接受项、分歧项、风险清单、owner、验证方式和下一步路由。
- **PRD AI 预扫描模式**：PRD 评审会前先由产品专家按完整性、一致性、可测试性、二义性找疑似问题和建议追问，再由 AI Native 接入 `review_task / evaluation_task / reporting_task`，人工 owner 决定采纳、拒绝或待确认。
- **最终文档准出模式**：PRD、系分、Spec 或 OpenSpec 已经混入讨论过程、迭代草稿、AI 推理轨迹或被拒方案时，先区分当前有效结论与过程资产；正文只保留目标、范围、规则、设计取舍、风险、待确认、验收和必要版本状态，过程内容外置到评审报告、Decision Log、Goal Ledger、ADR 或任务计划。
- **Spec 模板模式**：需要落地 Spec / SDD / OpenSpec 模板、AC 验收、测试映射、spec-lint、AC 覆盖或漂移检查时，先区分 PRD / SDD / 实现 Spec 三层是否齐备，再输出可审骨架、AC 表、闸门证据、风险自查和轻重切换。
- **代码交付闭环模式**：AI Coding / SDD / Spec / Harness 已经落地但交付体感不足时，先判断瓶颈在需求、上下文、Spec 层数、Harness、CR、测试、发布还是知识回流，再输出最小 Spec 强度、独立验证证据、CR 减负、知识回流、指标和停止条件。
- **Superpowers 调度模式**：需要下载、评估或接入 Superpowers skills 时，先输出外部 skill 适用范围、AI Native 阶段映射、只读 / 写入 / Git / 联网 / subagent 边界、验证门禁、停止条件和不采用的外部默认流程。
- **质量门禁模式**：需要测试策略、TDD、补测试或 CR 验证时，先设计测试矩阵、验证顺序、CR 前置条件、失败回退和残余风险交接，再路由到 `资深架构师` 的 `testing.md` 能力。
- **理解门禁模式**：陌生代码库、AI 代码变更、diff、重构计划或 PR 说明已经出现，但团队看不清结构关系和影响范围时，先设计代码库理解结论包，覆盖业务意图、入口路径、影响模块、关键调用关系、边界变化、源码锚点、可视化辅助、owner 复述和残余风险交接，再路由到 `资深架构师` 做源码级 CR。
- **工具准入模式**：点名 Gemini CLI、AgentRC、Understand Anything 或同类代码理解 / 上下文工程 / 知识图谱工具，或要求代码库级阅读/分析、对齐设计和代码、检查 AI-readiness / instructions / eval / 上下文漂移、生成团队共享图谱时，先判断是否值得安装或调用、是否只读、是否联网/认证/写文件、输出如何回链源码和验证，再决定是否交给资深架构师或用户授权执行。
- **CR/发布模式**：已有代码变更、测试结果或发布计划时，评审验证缺口、代码 CR 重点、发布门禁、监控、回滚和复盘。

默认输出骨架固定为：结论、Loop Profile、Owner / 下一步分派、交接物、Loop Contract、证据边界、内部层、授权策略、验证门禁、停止条件、残余风险 / 需要确认。证据边界必须区分事实、推断、待确认和范围外不做；授权策略必须区分只读、计划内低风险执行、Wave Grant、CAD Grant 和显式确认；只有用户要求完整方案、评审报告或模板时，再展开阶段表、RACI、验证矩阵或 Goal Ledger。

使用时建议直接说明：

```text
当前输入成熟度：想法 / 原型 / 产品上下文包 / OpenSpec / 代码变更 / 发布计划
目标产物：流程评审 / 交接包 / GSD/CAD 编排准入结论 / Harness 摘要 / GSD Wave 建议 / CAD 候选缺口 / 授权策略卡 / Spec 模板落地包 / AI 代码交付闭环报告 / 工具安装与调用准入 / 质量门禁 / 代码库理解结论包 / 理解门禁 / 验证矩阵草案 / 发布复盘
边界：只做流程编排，不写 PRD / 不改代码 / 不提交 / 不部署
验证要求：列出缺口、停止条件、需要产品专家或架构师继续处理的事项
证据边界：事实 / 推断 / 待确认 / 范围外不做；禁止无根据猜测或超出用户目标的实现
授权策略：只读 / 计划内低风险执行 / Plan Grant / Wave Grant / CAD Grant / 显式确认；Codex 替我审批仅限当前 Grant 范围内低风险动作
```

经流程入口分派时这样用：

- 可以让它先判断普通 PRD、产品方案或 Backlog 是否成熟，再把正文产物分派给 `产品架构专家`。
- 可以让它先对 PRD、PRD-Lite、OpenSpec 输入、系分或 Harness 候选做合议预审；预审只能提前暴露问题和沉淀决策日志，不能替代产品 owner、架构 owner、正式评审、测试通过或 Execution Grant。
- 可以让它先判断架构设计、代码 CR、Bug 修复、测试或生产变更是否需要 OpenSpec、Harness、验证矩阵和发布闭环，再把工程执行分派给 `资深架构师`。
- 可以让它先判断中大型项目是否进入 GSD Round 0、如何形成 Wave/Atomic Task 候选、哪些是 CAD 候选缺口和授权策略缺口，再把工程任务包、CAD Mode 门禁和执行策略分派给 `资深架构师`。
- 可以让它先做 `GSD + Goal`，把父 Goal、Wave Goal、成功标准、预算 / 时间盒、验证证据、授权策略、停止条件、交接 owner 和 Ledger 更新串起来；`GSD + Goal 按任务计划推进` 会形成 Plan Grant，但 Goal 状态不能替代测试通过或发布批准。
- 可以让它先做 `开启 GSD/CAD 计划内授权策略`，减少每个任务重复审批；Plan Grant 覆盖任务计划内低风险本地动作，但 Git、联网、依赖安装、生产、密钥、部署、不可逆操作和高风险业务仍必须显式确认。
- 可以让它先判断 PRD / SDD / 实现 Spec 三层是否齐备、Spec / SDD / OpenSpec 模板应该使用轻量任务卡、可评审 Spec、Harness/GSD Spec、CAD 候选 Spec 还是人工主导，再把产品上下文、系统设计、测试和源码级 CR 分派给对应 owner。
- 可以让它先判断 AI Coding / SDD / Spec / Harness 为什么没有带来端到端交付体感，是否需要减层、补上下文、补机器验证、调整 Spec 强度、前移 CR 高频问题和建立知识回流，再把测试、代码和源码级 CR 分派给 `资深架构师`。
- 可以让它先判断测试策略、TDD、补测试或 CR 验证需要放在哪个质量门禁、按什么顺序验证、失败后如何回退，再把测试设计与实现分派给 `资深架构师`。
- 可以让它先判断陌生代码库、AI 生成代码、diff、重构计划或 PR 说明是否能让团队看懂业务意图、入口路径、影响模块、源码锚点、调用关系和边界变化，再把源码级 CR 分派给 `资深架构师`。
- 可以让它先判断是否值得安装或调用 Gemini CLI、AgentRC、Understand Anything 这类工具来阅读代码、生成上下文、对齐设计和代码、检查上下文漂移或生成代码库知识图谱；需要安装、联网、认证、写文件、写 `.understand-anything/`、启用 hook、启动 dashboard 或改配置时必须先列授权缺口。
- 只要求阅读某个文件、函数、类、报错、测试失败或具体 PR diff 时，优先直接用 `资深架构师`；除非目标是代码库级理解、设计-代码对齐、上下文工程、知识图谱或工具准入，否则不要默认触发 Gemini CLI / AgentRC / Understand Anything。
- 可以让它先判断 DDL、字段表格或 Java 类是否具备结构化输入、写入范围和覆盖风险，再把配套代码生成分派给 `java-service-code-generator`。
- 不要把外部文章、工具宣传或历史平台能力当作当前会话可用工具、执行授权或生产审批。

### 提示词公式

```text
用 <Skill 名称> + <任务类型> + <输入材料> + <目标产物> + <边界/风险> + <验证要求>
```

示例要点：

- `<Skill 名称>`：AI Native 研发流程编排、产品架构专家、资深架构师、java-service-code-generator，或明确 `$fireworks-tech-graph`。
- `<任务类型>`：生成 PRD、反推 PRD、GSD/CAD 准入、GSD + Goal、Goal 组合、Spec 模板最佳实践、SDD 生产代码门禁、AI 代码交付闭环、质量门禁、理解门禁、系统设计、代码 CR、补测试、生成脚手架、画图、触发验证。
- `<输入材料>`：需求描述、原型/页面截图/HTML/交互稿、PRD、设计文档、DDL、Java 类、字段表格、报错日志或本地文件路径。
- `<目标产物>`：PRD、能力地图、架构图、规则矩阵、验收标准、SDD 生产代码门禁包、ADR、代码修改、测试、评审报告或脚手架目录。
- `<边界/风险>`：不要覆盖已有文件、默认只输出 SVG、涉及支付资金需列待确认方、只做 CR 不改代码。
- `<验证要求>`：运行 `./scripts/validate.sh`、做触发验证、执行 dry-run、检查外部规则来源或说明无法验证的残余风险。

### 推荐提示词

```text
用 AI Native Engineering Loop：按当前材料选 Loop Profile，输出 owner、交接物、Loop Contract、验证门禁、停止条件和下一步分派。
```

```text
进入 AI Native 交付 Loop：以交付生产可用能力为目标，产品专家先做需求分析、产品设计和确认，架构师再做系分设计、编码、TDD、CR 和验证；GSD/CAD/Goal 作为内部层自动选择，不交付模拟模块、内存版业务 Service 或样子货。
```

```text
进入只读理解 Loop：阅读分析代码库、对齐设计和代码、评估工具准入或做事实边界检查；默认不写文件、不安装、不联网。
```

```text
进入验证发布 Loop：编排测试矩阵、CR 前置条件、发布监控、失败回退、残余风险和复盘回流。
```

```text
进入知识回流 Loop：把已验证经验沉淀到 Skill、reference、fixture、脚本、用户指南或 source-map。
```

```text
做事实边界检查：区分事实、推断、待确认和范围外不做；禁止无根据猜测、模型脑补或超出用户目标的实现扩张。
```

```text
进入 GSD 产研协同研发流程：这是兼容旧说法，会映射到 AI Native 交付 Loop；目标仍是交付生产可用能力。
```

```text
GSD + Goal：作为交付 Loop 的 Goal + GSD 内部层，把目标、生产可用能力、成功标准、预算 / 时间盒、GSD Wave、CAD 候选、验证证据、提交切片、停止条件和交接节奏串起来；不要把 Goal 当 Execution Grant。

GSD + Goal 按任务计划推进：形成 Plan Grant，按已确认任务计划推进低风险本地任务；默认输出提交切片，只有授权 `commit_after_verified_task` 后才做本地 commit；不要把它扩大到联网、生产、密钥、部署、不可逆操作或高风险业务。
```

```text
生产可用 Loop 门禁：检查 Agent Loop 是否具备真实目标、状态落盘、隔离执行、Skill 上下文、连接器权限、Maker / Checker 解耦、独立验证、观测审计、人工接管、发布/回滚和停止条件。
```

```text
三卡交接：产品专家输出 Product Context Card；AI Native 输出 Engineering Handoff Card；需要持续推进时补 Production Loop Card；缺任一卡就停在对应 owner 补齐，不进入实现、CAD 或自动 Loop。
```

```text
对 PRD 和系分做 MAGI 三角色合议预审：输出 review_task、evaluation_task、reporting_task、ACCEPT/REJECT/PENDING 决策日志和下一步路由。
```

```text
做 GSD/CAD 准入：判断是否进入 Round 0、Wave/Atomic Task、CAD 候选缺口和 Execution Grant 缺口。
```

```text
开启 GSD/CAD 计划内授权策略：把每个任务都问授权收敛成只读、计划内低风险执行、Plan Grant、Wave Grant、CAD Grant 和显式确认；Codex 替我审批只用于当前 Grant 范围内低风险本地动作。
```

```text
落地 Spec 模板最佳实践：先区分 PRD / SDD / 实现 Spec 三层是否齐备，再输出 Spec 强度、五段式骨架、AC 与测试映射、spec-lint、AC 覆盖、漂移检查、风险自查和轻重切换。
```

```text
进入 SDD 生产代码模式：检查 Spec 是否能作为事实来源，补结构化契约、正反例、边界/错误处理、测试计划和五支柱验证；失败先回写 Spec 再重试。
```

```text
做 AI 代码交付闭环：评审 SDD / Spec / Harness 为什么没有交付体感，输出瓶颈、Spec 强度、独立验证、CR 减负、知识回流和指标。
```

```text
做质量门禁：输出测试矩阵、验证顺序、CR 前置条件、失败回退和架构师 testing.md 调用点。
```

```text
做理解门禁：把这次 diff / 重构计划整理成入口路径、影响模块、调用关系、源码锚点、验证证据和 CR 交接条件。
```

```text
做 Skill 类型路由：细化 AI 流程、产品专家和架构师能力，判断产品验证、代码质量、Runbook、CI/CD、模板脚手架、数据分析和基础设施操作的 owner、交接物、验证证据和是否需要补 reference / fixture / 脚本。
```

```text
阅读分析代码库：先做代码库理解结论包；评估是否需要 Gemini CLI / AgentRC / Understand Anything，但不要默认安装或联网。
```

```text
评估 Gemini CLI / AgentRC / Understand Anything：列来源、安装/认证/联网/写入边界、只读范围、隐私风险、人工替代路径和 CR 条件；Understand Anything 还要列 `.understand-anything/`、dashboard、auto-update、hook 和图谱提交边界。
```

```text
做设计-代码对齐：对齐 OpenSpec / 系分设计与当前代码，输出设计条款、代码入口、实现状态、偏差和测试证据。
```

```text
用产品架构专家梳理 VCC 发卡业务的产品架构，输出能力地图、核心对象、交易流程、资金流、风险和验收标准，默认 SVG 画图。
```

```text
用产品架构专家根据这份运营后台页面截图和交互稿反推可评审 PRD，补齐角色、对象、流程、规则、数据指标、验收标准和待确认问题。
```

```text
用资深架构师评审这个设计文档，重点看模块边界、数据一致性、可靠性、安全、测试和发布回滚，并给出 P0/P1/P2 问题。
```

```text
用 java-service-code-generator 根据 docs/order.sql 生成订单模块配套代码，先输出到 /tmp/order-scaffold 评审目录，不覆盖现有文件。
```

```text
这个产品架构图还需要更精致的视觉风格和更复杂的分组关系，继续调用 $fireworks-tech-graph 做 SVG 续作。
```

```text
对产品专家和架构师做一轮触发验证，检查哪些提示会触发、哪些不应触发，并说明是否需要调整 description。
```

```text
做一轮完整性、可用性和约规 CR；如果无明显问题，再执行 ./scripts/validate.sh。
```

### 最佳实践

- 提供背景、目标产物、范围边界、已知约束、风险等级和验收标准，比只说“优化一下”更容易得到可评审结果。
- 能用默认流程短句表达时，先让 `AI Native 研发流程编排` 判断最小流程；不要一开始就要求完整 GSD/CAD、完整 Harness 或大而全模板。
- 明确你要的是“方案”“PRD”“原型反推”“CR”“触发验证”“图”“代码生成”“同步到 Codex”还是“提交变更”；这些词会影响技能路由和验证动作。
- 对高风险问题保留待确认项。产品专家给产品和金融业务结构，架构师给工程验证和生产风险，外部规则仍要由法务、合规、财务、通道、银行或持牌机构确认。
- 让技能分层协作。复杂金融产品通常先由产品专家产出对象、流程、规则和验收，再由架构师承接系统设计、代码、测试和发布。
- 代码生成前先确认输入结构和目标模块。提供 DDL、字段表格、Java 类、业务模块和是否允许覆盖，会显著减少歧义。
- 修改技能后先运行 `./scripts/validate.sh`；需要安装到 Codex 时先运行 `./sync-skills.sh --dry-run all`，确认目标目录后再正式同步。

### 常见误用

- 不要让 `java-service-code-generator` 从纯自然语言直接生成生产代码；它需要 DDL、字段表格、Java 类或 schema 这类结构化输入。
- 不要把产品专家对支付、资金、卡组织或监管的输出当作最终合规结论；上线前仍需法务、合规、财务、通道、银行或持牌机构确认。
- 不要把错误截图、日志截图、测试失败截图交给产品专家定位；如果目标是根因分析、修复或补测试，应使用 `资深架构师`。
- 不要把“画图”只说成一句话；至少说明图给谁看、要表达什么对象关系、需要哪类视图、是否只要 SVG。
- 不要把 `AI Native 研发流程编排` 当作 PRD 正文、源码级 CR 或代码生成的替代品；它负责路由、门禁和交接，具体产物仍交给对应 Skill。
- 不要在没有明确授权时要求覆盖已有文件、读取私有目录、同步安装目录或提交变更；高影响动作先 dry-run 或 CR。
- 不要把外部文章、仓库或论文直接搬进 Skill；只能吸收可迁移的方法、边界、检查项和验证方式，并保留来源和安全审查。
- 不要把 AI 原生工具的产品宣传或历史文章能力描述当作当前会话可用工具、执行授权、合规结论或生产审批；需要执行时仍要回到当前工具状态、项目权限和用户授权。

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

不要把使用者长期学习数据放在本仓库或安装后的技能目录中；技能同步可能删除安装目录里的额外文件。长期学习数据应保存在用户目录 `~/.skill-learning/`，或由 `SKILL_LEARNING_HOME` 指定的位置。

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
- [obra/superpowers](https://github.com/obra/superpowers)：作为 `ai-native-engineering-workflow` 的外部 skills library 参考来源，用于 brainstorming、writing-plans、executing-plans、subagent-driven-development、test-driven-development、requesting-code-review、receiving-code-review、systematic-debugging、verification-before-completion、using-git-worktrees、finishing-a-development-branch 和 writing-skills 等工程纪律调度。2026-06-07 已通过 GitHub API 读取 skills 目录和 README，下载 main.zip 到临时目录并审查 LICENSE、scripts、hooks 和 plugin manifest；main commit 为 `6fd4507659784c351abbd2bc264c7162cfd386dc`，zip SHA256 为 `ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3`，许可证为 MIT。本仓库只复制 Markdown skill 资源和 LICENSE 到 `ai-native-engineering-workflow/references/external-superpowers/`，并通过 `superpowers-skill-library.md` 做按需调度；不复制或运行外部脚本、hooks、插件 manifest、package 脚本、安装流程、图片资产或跨平台启动方式，也不把外部默认文档路径、自动提交、Git 推送、worktree、subagent 连续执行要求写成本仓库默认行为。
- [yizhiyanhua-ai/fireworks-tech-graph](https://github.com/yizhiyanhua-ai/fireworks-tech-graph)：作为图形化 Skill 产品化、风格系统、语义形状/箭头、模板化、fixture 化、SVG 导出和渲染校验思路的公开参考来源。本仓库只吸收通用方法，不默认复制外部脚本、模板、图形资产或安装流程；PNG/PDF/截图等派生格式只在使用者明确提出时处理；引入外部可执行内容前必须按 `AGENTS.md` 做供应链安全审查。
- [google/eng-practices](https://github.com/google/eng-practices)：作为 `资深架构师` 代码评审标准、评论分级、变更颗粒度、作者/评审者协作和持续改善代码健康的公开参考来源。本仓库只吸收可迁移的 Review 与 Change Author 原则，不把它扩展为完整架构设计方法论；复用具体文本、示例或派生产物时必须保留来源、确认 CC-BY 3.0 归因要求并避免复制大段原文。
- [Ivy-piger/Ivy-skills](https://github.com/Ivy-piger/Ivy-skills)：作为架构师陌生代码库侦察、Java 架构坏味启发式扫描、生产故障时间线、5-Why 复盘草稿和 Spring Boot 安全检查清单的公开参考来源。本仓库只吸收可复用流程和检查项，不安装或复制 Claude Code 专用 frontmatter、`CLAUDE.md` 流程、外部脚本或服务端运行逻辑；如需复用具体文本、脚本或资产，必须保留来源、确认许可证并执行供应链安全审查。
- [cg0x-skills/cg0x-frame-analysis](https://github.com/cg0x-skills/cg0x-frame-analysis)：作为探索期反路径锁定、多框架分析、假设/盲区/失败条件自检的公开参考来源。本仓库只吸收通用方法到产品专家和架构师 reference，不引入 `alwaysApply`、`/on` `/off` 开关、单文件长 Skill 或默认不收敛的交付方式；复杂问题先展开问题地图，正式交付仍必须回到可评审、可验证、可验收的产物。
- [zjunlp/SkillX](https://github.com/zjunlp/SkillX) 与论文 [SkillX: Automatically Constructing Skill Knowledge Bases for Agents](https://arxiv.org/abs/2604.04804)：作为从 Agent 执行轨迹提炼规划技能、功能技能、原子技能，迭代精炼、合并过滤和探索扩展技能知识库的公开参考来源。本仓库只吸收“经验分层、过滤噪音、合并重复、工具约束和失败模式进入确定性验证”的方法，不引入自动读取历史轨迹、自动学习用户数据、外部训练流水线或未审查代码；任何长期学习仍必须遵守 `AGENTS.md` 的本地协作学习授权和隐私边界。
- 微信文章 [《【译】别再手动写 Prompt 了，去写 Loop——但 Loop 到底是什么？》](https://mp.weixin.qq.com/s/cxRvqwWW4Yo4UmufAsXEEA)：作为 `ai-native-engineering-workflow` 的 Agent Loop Engineering 参考来源，用于 Loop 准入、GSD + Goal + Loop、状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件、反馈自检和 Skill 作为复用单位；2026-06-11 已通过移动端微信 UA 公开 HTML 读取标题、账号、页面时间字段和正文，页面时间字段为 2026-06-09 21:13:56 Asia/Shanghai。本仓库只吸收可迁移方法，不复制原文、推文、图片、成本数字、工具宣传、作者表达、命令示例或标题传播话术，也不把 `/goal`、`/loop`、auto mode、后台 Agent 或任一工具能力写成当前会话默认能力、最新事实、执行授权或上线审批。
- 微信文章 [《Loop Engineering（Agent 闭环工程）》](https://mp.weixin.qq.com/s/mbjdMlSTqQG1EptOGoo6og)：作为 `ai-native-engineering-workflow` 的生产可用 Loop 门禁参考来源，用于自动化心跳、隔离 worktree、Skill 上下文、连接器权限、Maker / Checker 解耦、状态持久化、质量卡口、成本预算、观测审计、人工接管、发布/回滚和理解债控制；2026-06-12 已通过移动端微信 UA 公开 HTML 读取标题、作者、账号、页面时间字段和正文。本仓库只吸收可迁移门禁，不复制原文、工具宣传、示例 Prompt 或命令，也不把 `/goal`、`/loop`、Automations、Worktrees、Connectors、Sub-agents 或任何当前工具能力写成默认可用、默认授权、测试通过、CR 结论、合并判断或上线审批。
- 微信文章 [《一个让Codex变得越来越聪明的小方法》](https://mp.weixin.qq.com/s/G-tZjkhAd_yMAABBgNGVdw)：作为 `ai-native-engineering-workflow` 授权学习、经验归位和知识回流的公开参考来源。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `Dr.Joyi`，既有账号线索保留 `像素与咖啡时光`，页面时间字段为 2026-06-04；本仓库只吸收“反复踩坑来自稳定上下文缺失，执行经验、偏好理念和项目知识要进入合适载体”的可迁移方法，不复制原文、个人经历、提示词或作者口吻，也不把用户长期偏好写入仓库、安装目录或未授权学习目录。
- 微信文章 [《架构8：架构设计三原则》](https://mp.weixin.qq.com/s/wc3xeSbBqb6ktEDz2ZuK7g)：作为 `资深架构师` 合适、简单、演化三类架构评审原则的公开参考来源。2026-05-28 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收当前约束匹配、结构/逻辑复杂度评估和演进式设计门禁，不复制文章案例、代码示例、图片或作者表达。
- 微信文章 [《架构师底层思维能力要求-这7种尽早练习》](https://mp.weixin.qq.com/s/Veb3P2ug8XVmyBFmIoDJ7Q)：作为 `资深架构师` 抽象、逻辑、结构化、批判、成长型、复盘和数据思维的公开参考来源。2026-05-28 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收底层思维能力框架、架构判断落点和常见误区，不复制原文图片、推荐书目、排版结构或作者表达。
- 微信文章 [《软件复杂性的本质是通信复杂性》](https://mp.weixin.qq.com/s/1MbijKDxD2B4wa1E9QTnAw)：作为 `资深架构师` 通信复杂度、节点/边/状态传播、抽象隐藏边、复杂度转移检查，以及业务驱动架构/TDD 桥接的公开参考来源。2026-05-29 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收架构评审、业务验证、测试资产和图形检查项，不复制原文、SVG 插图、产品对比或作者表达，也不把通信复杂度绝对化为唯一复杂度来源。
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

### 本地协作学习机制

本仓库只维护技能定义和协议，不保存使用者个人学习数据。本地协作学习机制用于提升使用者与技能的配合度，并在合适场景下协助使用者改进判断、表达和设计质量。该机制是可选项，默认关闭；只有用户明确同意启用后，才会在用户目录下创建 `~/.skill-learning/` 并保存长期使用习惯、团队决策偏好、业务背景和技能演进记录。如需自定义位置，可以设置 `SKILL_LEARNING_HOME`。

首次问询不是第一次使用技能时必问，而是先通过“学习时机判定算法”判断当前任务是否已经出现稳定偏好、团队约规、业务背景、反复决策方式等长期沉淀价值，并且不会打断关键任务时才询问。用户在单个技能场景下同意时，默认只开启当前技能；只有明确要求“所有技能”或“全局开启”时，才对所有技能生效。

学习时机判定采用轻量算法：先识别候选观察，再从稳定性、复用价值、证据强度、可执行性、安全性五个维度评分，之后经过风险门禁决定不学习、静默进入 `Pending Observations`、显示确认后记录，或只做纠偏讨论。涉及隐私、金融/合规/安全、生产上线、权限边界、强约束偏好或用户可能错误判断时，不得静默学习。

推荐结构：

```text
~/.skill-learning/
  consent.md
  global.md          # 可选：仅全局授权或明确跨技能约定时创建
  skills/
    <skill-id>.md
  archive/
```

- `consent.md` 保存本地协作学习机制的启用标记。
- `global.md` 保存跨技能通用约定，仅在全局授权或明确跨技能约定时创建。
- `skills/<skill-id>.md` 保存单个技能的长期学习记录。
- 技能目录只保存技能定义和 references，避免同步或重构时覆盖学习数据。
- 用户明确拒绝启用时，不创建学习目录或文件，后续也不主动提示，除非用户主动提及。
- 用户同意启用但未说明范围时，默认只开启当前技能。
- 启用后默认采用混合模式：低风险常规观察可静默保存到 `Pending Observations`；可能影响长期行为、跨技能复用、业务/合规/隐私边界或强约束偏好的记录需要显示确认。
- 启用后也不是所有观察都记录；必须先经过学习时机判定，并且去重、可追溯、可撤销。
- 用户可以随时切换为静默模式、显示确认模式或混合模式。
- 启用后默认采用协作型学习模型；用户可以切换为记录型、协作型或审查型。
- 如果发现用户判断或设计可能存在错误、逻辑漏洞或红线风险，需要显示提示用户，并讨论确认改进方式。
- 协作时会按当前话题动态判断用户专业程度，用于校准解释深度和纠偏强度；该判断不得固化为用户全局标签。
- 提交、上传或共享到远程前需要用户确认。
- 未经用户确认，不应把 `Pending Observations` 提升为 `Confirmed Agreements`。

详细约定见 [AGENTS.md](./AGENTS.md)。
