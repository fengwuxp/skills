# Skills

本仓库用于维护可安装到 Codex 的 Skills。它不是轻量 prompt 集，而是一套可长期演进的 Agent 运行时资产库。

仓库采用分层治理：`AGENTS.md` 保存每个会话都应知道的默认规则和安全边界；各技能的 `SKILL.md` 保存特定任务的入口、路由和红线；详细知识、模板和方法论放在对应技能的 `references/` 中；确定性生成、验证、同步和安全检查放在 `scripts/` 中；使用者长期学习数据只保存在用户目录 `~/.skill-learning/` 或 `SKILL_LEARNING_HOME`，不进入仓库。

## 用户使用指南

安装或同步后，Codex 会根据每个 `SKILL.md` 的 `name` 和 `description` 自动判断是否触发对应技能。使用者也可以在提示中直接点名，例如“用产品架构专家……”“用资深架构师……”“用 java-service-code-generator……”。同步后如果触发不符合预期，先重启 Codex 或开启新会话。

### 先选哪个 Skill

[产品架构专家](./product-architecture-expert)

- 适合：PRD、产品方案、需求说明、原型/HTML/页面截图/交互稿反推 PRD、能力地图、业务流程、状态机、规则矩阵、运营后台、数据指标、验收标准和产品架构图。支付与资金是重点能力，覆盖账户/账本、清结算、对账、外卡收单、ACH、VCC、争议和跨境支付。
- 不适合：不替代法务、合规、财务、税务、持牌机构或卡组织规则确认；不负责工程实现、代码 Review 和生产排障。
- 常用说法：“用产品架构专家写一版 PRD”“根据页面截图反推可评审 PRD”“画一个 VCC 交易流程”“梳理清结算和对账能力地图”“评审这个需求是否可开发可验收”。

[资深架构师](./senior-software-architect)

- 适合：架构设计、系统分析设计、技术方案、ADR、代码 Review、Bug 修复、测试/TDD、生产变更、架构图和工程治理。擅长 Java/Spring/Wind，也能先识别非 Java 项目的本地生态。
- 不适合：不替代产品专家定义复杂业务语义、PRD 和金融产品规则；不在缺少边界、风险和验收时直接给可上线方案。
- 常用说法：“用资深架构师做一轮 CR”“评审这个系统设计”“分析这个 Bug 根因并补测试”“画一张服务架构图”。

[java-service-code-generator](./java-service-code-generator)

- 适合：根据 DDL/SQL、Java 类、字段表格或 schema 生成 Wind/Nobe 风格 Java Service 配套代码，包括 Entity、Mapper、DTO、Request、Query、Converter、Service、ServiceImpl 和测试夹具。
- 不适合：不从纯自然语言直接生成生产代码；不替代架构师、DBA 或业务负责人确认表结构、索引、状态机和金额精度；不默认覆盖已有文件。
- 常用说法：“根据这段 DDL 生成 Java Service 配套代码”“把这个字段表格转换成脚手架”“先生成到评审目录，不覆盖已有文件”。

### 如何选择

- 先定业务和验收，用 `产品架构专家`；再定工程结构、代码、测试和发布，用 `资深架构师`。
- 有原型、页面截图、HTML、交互稿或模糊想法，需要反推需求、流程、规则和待确认问题，用 `产品架构专家`。
- 已有代码、报错、测试失败、工程坏味或生产现象，直接用 `资深架构师`。
- 已经有明确表结构、字段表格或 Java 类，并且目标是生成配套代码，用 `java-service-code-generator`。
- 需要图形化交付时，架构师和产品专家都会默认产出 SVG；PNG、PDF、截图、Mermaid 或 Markdown 草图只有在使用者明确提出时才处理。
- 如果需要更复杂、更好看的技术图、能力图、架构图或风格化图形，先让产品专家或架构师产出图形语义、对象边界和 SVG 初稿；需要继续美化、风格化或复杂图形工程时，可以明确调用 `$fireworks-tech-graph` 续作。
- 涉及金融、支付、资金、卡组织、ACH、跨境、合规或监管时，先让产品专家标出主体、法域、资金归属、外部规则来源、待确认方和验收边界，再进入工程设计。

### 常用组合路线

- 从想法到工程：`产品架构专家` 先把目标、对象、流程、规则、验收和待确认项定清楚；`资深架构师` 再承接系统设计、代码、测试和发布风险。
- 从原型到 PRD：`产品架构专家` 根据原型、HTML、页面截图或交互稿反推 PRD，先补角色、对象、状态、规则、数据和验收，不只描述页面控件。
- 从 PRD 到代码生成：先用 `产品架构专家` 或 `资深架构师` 确认对象、状态、字段、索引和金额精度；已有 DDL、字段表格或 Java 类后，再用 `java-service-code-generator` 生成配套代码。
- 从普通图到复杂图：先用 `产品架构专家` 或 `资深架构师` 产出语义稳定的 SVG；需要更复杂的布局、风格系统或精细视觉时，再调用 `$fireworks-tech-graph` 续作。
- 从金融产品到上线方案：`产品架构专家` 先标出主体、法域、资金归属、外部规则和专业确认方；`资深架构师` 再处理系统边界、数据一致性、可靠性、安全和发布回滚。

### 提示词公式

```text
用 <Skill 名称> + <任务类型> + <输入材料> + <目标产物> + <边界/风险> + <验证要求>
```

示例要点：

- `<Skill 名称>`：产品架构专家、资深架构师、java-service-code-generator，或明确 `$fireworks-tech-graph`。
- `<任务类型>`：生成 PRD、反推 PRD、系统设计、代码 CR、补测试、生成脚手架、画图、触发验证。
- `<输入材料>`：需求描述、原型/页面截图/HTML/交互稿、PRD、设计文档、DDL、Java 类、字段表格、报错日志或本地文件路径。
- `<目标产物>`：PRD、能力地图、架构图、规则矩阵、验收标准、ADR、代码修改、测试、评审报告或脚手架目录。
- `<边界/风险>`：不要覆盖已有文件、默认只输出 SVG、涉及支付资金需列待确认方、只做 CR 不改代码。
- `<验证要求>`：运行 `./scripts/validate.sh`、做触发验证、执行 dry-run、检查外部规则来源或说明无法验证的残余风险。

### 推荐提示词

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
- 不要在没有明确授权时要求覆盖已有文件、读取私有目录、同步安装目录或提交变更；高影响动作先 dry-run 或 CR。
- 不要把外部文章、仓库或论文直接搬进 Skill；只能吸收可迁移的方法、边界、检查项和验证方式，并保留来源和安全审查。

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

- [yizhiyanhua-ai/fireworks-tech-graph](https://github.com/yizhiyanhua-ai/fireworks-tech-graph)：作为图形化 Skill 产品化、风格系统、语义形状/箭头、模板化、fixture 化、SVG 导出和渲染校验思路的公开参考来源。本仓库只吸收通用方法，不默认复制外部脚本、模板、图形资产或安装流程；PNG/PDF/截图等派生格式只在使用者明确提出时处理；引入外部可执行内容前必须按 `AGENTS.md` 做供应链安全审查。
- [google/eng-practices](https://github.com/google/eng-practices)：作为 `资深架构师` 代码评审标准、评论分级、变更颗粒度、作者/评审者协作和持续改善代码健康的公开参考来源。本仓库只吸收可迁移的 Review 与 Change Author 原则，不把它扩展为完整架构设计方法论；复用具体文本、示例或派生产物时必须保留来源、确认 CC-BY 3.0 归因要求并避免复制大段原文。
- [Ivy-piger/Ivy-skills](https://github.com/Ivy-piger/Ivy-skills)：作为架构师陌生代码库侦察、Java 架构坏味启发式扫描、生产故障时间线、5-Why 复盘草稿和 Spring Boot 安全检查清单的公开参考来源。本仓库只吸收可复用流程和检查项，不安装或复制 Claude Code 专用 frontmatter、`CLAUDE.md` 流程、外部脚本或服务端运行逻辑；如需复用具体文本、脚本或资产，必须保留来源、确认许可证并执行供应链安全审查。
- [cg0x-skills/cg0x-frame-analysis](https://github.com/cg0x-skills/cg0x-frame-analysis)：作为探索期反路径锁定、多框架分析、假设/盲区/失败条件自检的公开参考来源。本仓库只吸收通用方法到产品专家和架构师 reference，不引入 `alwaysApply`、`/on` `/off` 开关、单文件长 Skill 或默认不收敛的交付方式；复杂问题先展开问题地图，正式交付仍必须回到可评审、可验证、可验收的产物。
- [zjunlp/SkillX](https://github.com/zjunlp/SkillX) 与论文 [SkillX: Automatically Constructing Skill Knowledge Bases for Agents](https://arxiv.org/abs/2604.04804)：作为从 Agent 执行轨迹提炼规划技能、功能技能、原子技能，迭代精炼、合并过滤和探索扩展技能知识库的公开参考来源。本仓库只吸收“经验分层、过滤噪音、合并重复、工具约束和失败模式进入确定性验证”的方法，不引入自动读取历史轨迹、自动学习用户数据、外部训练流水线或未审查代码；任何长期学习仍必须遵守 `AGENTS.md` 的本地协作学习授权和隐私边界。
- 微信文章 [《架构8：架构设计三原则》](https://mp.weixin.qq.com/s/wc3xeSbBqb6ktEDz2ZuK7g)：作为 `资深架构师` 合适、简单、演化三类架构评审原则的公开参考来源。2026-05-28 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收当前约束匹配、结构/逻辑复杂度评估和演进式设计门禁，不复制文章案例、代码示例、图片或作者表达。
- 微信文章 [《架构师底层思维能力要求-这7种尽早练习》](https://mp.weixin.qq.com/s/Veb3P2ug8XVmyBFmIoDJ7Q)：作为 `资深架构师` 抽象、逻辑、结构化、批判、成长型、复盘和数据思维的公开参考来源。2026-05-28 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收底层思维能力框架、架构判断落点和常见误区，不复制原文图片、推荐书目、排版结构或作者表达。
- 微信文章 [《软件复杂性的本质是通信复杂性》](https://mp.weixin.qq.com/s/1MbijKDxD2B4wa1E9QTnAw)：作为 `资深架构师` 通信复杂度、节点/边/状态传播、抽象隐藏边、复杂度转移检查，以及业务驱动架构/TDD 桥接的公开参考来源。2026-05-29 已通过公开 HTML 和本机 Chrome headless 读取标题、公众号、作者、发布时间和正文；本仓库只吸收架构评审、业务验证、测试资产和图形检查项，不复制原文、SVG 插图、产品对比或作者表达，也不把通信复杂度绝对化为唯一复杂度来源。
- 微信文章 [《架构师必备--让AI画架构图》](https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg)：作为 `资深架构师` 与 `产品架构专家` AI 辅助可编辑画图、文档转图、draw.io XML、版本历史和本地模型/凭据边界的公开参考来源。2026-06-01 已通过公开 HTML 读取标题、账号、作者、发布时间和正文，并尝试本机 Chrome headless 等价浏览器；本仓库只吸收可迁移的图形 brief、可编辑源文件、人工校验、权限和敏感信息边界，不复制示例图、提示词、项目安装说明或工具宣传语。
- 微信文章 [《让AI编程从"越写越烂"到"持续稳定输出"：GSD工作流-适合中大型项目的精准框架。》](https://mp.weixin.qq.com/s/VA_GhniSSrcJotXWlgk_lw)：作为 `资深架构师` 中大型 AI 编码流程治理、上下文衰减、阶段状态、多 Agent 编排、Wave 依赖、原子可追溯和 Git 版本化意识的公开参考来源。2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、作者/账号、发布时间和正文；本仓库只吸收持久化上下文、阶段循环、交接验证和轻重流程选择，不复制 GSD 命令体系、文件模板、XML 示例、动图、截图、工具宣传语或作者表达，也不把自动提交视为默认授权。
- 微信文章 [《需求分析和设计活动关键要点总结》](https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q)：作为 `资深架构师` 与 `产品架构专家` 功能定义、功能分配追溯、需求分析外部视角和设计内部视角分工的公开参考来源。2026-06-01 已通过移动端微信 UA 公开 HTML 和本机 Chrome headless 读取标题、账号、作者、发布时间和正文；本仓库只吸收功能不是头脑风暴清单、功能来自上层对象分配、正逆追溯和需求/设计分工检查项，不复制原文推荐书目、GJB 章节表述、课程/书籍引导或作者表达。
- 微信文章 [《如何评估你写的 SKILL.md 质量？一套完整的 Eval 方法论》](https://mp.weixin.qq.com/s/JWz6EscFlcDeHhTjsDybgg)：作为 Skill Eval 触发准确率、输出质量、效率指标、真实 prompt、难负例、对照实验和方差检查的公开参考来源。2026-05-28 已通过浏览器自动化读取标题、账号、作者、发布时间和正文；本仓库只吸收评估方法、prompt fixture 结构和离线校验边界，不复制文章原文、策略案例、社群引导或未逐篇读取的外部链接。
- 微信文章 [《产品经理别再只让 AI 写 PRD 了，先把用户反馈整理成一张问题地图》](https://mp.weixin.qq.com/s/sY6cw6wE5ePyrZmRYbXApg)：作为 AI 辅助 PRD 前置发现、用户反馈证据链和问题地图字段的公开参考来源。2026-05-28 已通过公开 HTML 读取标题、账号、作者、发布时间和正文，并尝试浏览器自动化；本仓库只吸收反馈到问题、证据强度、人工判断门禁和 PRD 前置发现流程，不复制原文表格、图片或外部工具营销。
- 微信文章 [《B端产品经理实战经验分享系列 - 如何写出高质量的需求文档》](https://mp.weixin.qq.com/s/_KU0j5sy1HBMdx03bhlYGg)：作为 `产品架构专家` PRD 文档质量治理、文档目标/受众、PRD/MRD/BRD 类型区分、版本记录、评审闭环和同步机制的公开参考来源。2026-06-01 已通过公开 HTML 读取标题、账号、作者、发布时间和正文，并用本机 Chrome headless 加载取证；本仓库只吸收可迁移的质量门禁、裁剪方法和评审机制，不复制原文案例、指标数字、图片或作者表达。
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
