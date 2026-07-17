# AI 代码理解工具入口

本文定义 Gemini CLI、AgentRC、Understand Anything、Ponytail、Open Code Review、WorkBuddy 或同类 AI 原生代码理解 / 上下文工程 / 知识图谱 / 最小正确实现工具 / 外部代码评审工具 / 本地执行型 Coding Agent 工具在知止者研发流程中的触发入口、安装准入、调用边界和交接要求。它只用于判断何时可引入工具辅助阅读代码、对齐设计和代码、生成上下文结论、做过度设计门禁、提供外部 Review 证据或生成候选 diff；不把任何工具写成默认依赖，也不替代 Context System、源码阅读、测试、CR、项目编码约规或用户授权。

## 使用时机

- 用户直接点名 Gemini CLI、AgentRC、Understand Anything、Ponytail、Open Code Review、OCR、WorkBuddy、本地执行型 Coding Agent、AI 快速阅读代码、上下文工程工具、代码库理解工具、知识图谱工具、AI 代码评审工具、最小正确实现、过度设计 CR 或“安装/调用某个工具分析代码 / 审查代码”。
- 陌生代码库需要快速形成入口路径、模块职责、关键调用关系、运行方式和风险结论。
- PRD、OpenSpec、系统设计、Harness Plan 或 ADR 已有，但需要对齐真实代码实现、模块边界、测试和运行脚本。
- AI 生成了多文件 diff、重构计划、接口迁移或状态机调整，团队看不清影响范围。
- 仓库指令、Agent instructions、MCP 配置、eval、AI-readiness 或上下文漂移需要评估。

## 不适用场景

- 普通代码 Review、Bug 修复、补测试或生产排障，优先交给 `资深架构师`。
- 只写 PRD、产品方案、Backlog 或验收标准，优先交给 `产品架构专家`。
- 项目禁止联网、禁止安装依赖、禁止外部模型读取仓库内容，或用户未授权安装/调用工具。
- 代码含客户敏感数据、密钥、生产配置、内部合同或不可外传材料，且无法做本地只读、安全隔离和脱敏。

## 读取后必须产出

- 工具触发结论：不用工具、只读侦察、建议安装/调用 Gemini CLI、建议安装/调用 AgentRC、建议安装/调用 Understand Anything、建议启用 Ponytail 最小正确实现门禁、建议调用 Open Code Review 作为外部代码评审 Checker、建议按 WorkBuddy 类本地执行型 Agent 准入生成候选 diff，或只记录人工替代路径。
- 安装 / 调用准入：来源、安装方式、认证要求、联网需求、写入范围、隐私边界、是否 dry-run、用户授权缺口。
- 代码库理解任务包：目标、输入材料、只读范围、禁止事项、期望输出、源码锚点、验证证据和残余风险。
- 设计-代码对齐结论：设计条款、代码入口、实现状态、偏差、测试证据、需架构师确认的问题。
- 本地执行型 Coding Agent 准入：项目上下文扫描、项目编码约规来源、写入范围、依赖 / 配置变更、候选 diff、验证命令、冲突决策澄清门禁、架构师 CR 和回写位置。
- 工具输出交接：事实 / 推断、置信度、文件路径、函数/类型/配置锚点、命令证据、上下文漂移检查和下一步 owner。
- 知识库工具判断：先确认 L0/L1/L2 权威上下文、隐私边界、读取范围和回链证据，再判断是否需要知识图谱、向量库或外部知识库；工具摘要不得替代源码、测试、CR 或 owner 结论。

## 需要继续读取的 reference

- 代码库理解、影响可视化、CR 和发布门禁读 `verification-review-release.md`。
- OpenSpec、Harness、权限和 Agent 工具治理读 `engineering-governance.md`。
- GSD/CAD 编排准入读 `planning-execution-admission.md`。
- 具体源码级判断、测试和 CR 交给 `senior-software-architect` 对应 reference。
- 工具来源状态和时效性边界读 `source-map.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否安装/调用工具 | 1、2、3 | 不直接执行安装 |
| 陌生代码库阅读 | 4、6 | 不写源码级 CR |
| 设计-代码对齐 | 5、6 | 不替代架构师评审 |
| AgentRC 上下文工程 | 3、7 | 不默认写入 `.github/` 或 `.vscode/` |
| Gemini CLI 代码理解 | 3、8 | 不默认联网或授权写文件 |
| Understand Anything 代码库知识图谱 | 3、9 | 不默认安装插件、写 `.understand-anything/`、启用 hook 或提交图谱 |
| Context / 知识库工具治理 | 3、9 | 不把外部知识库、向量库或图谱摘要当权威事实 |
| Ponytail 最小正确实现 / 过度设计 CR | 3、10 | 不替代 correctness/security review、TDD 或架构师源码级判断 |
| Open Code Review 代码评审 Checker | 3、10A | 不替代项目编码约规、Wind 编码约规、TDD 或架构师 CR |
| WorkBuddy 类本地执行型 Agent | 3、6A、11 | 不替代项目编码约规、Wind 编码约规、TDD 或架构师 CR |
| 工具输出进入 CR | 6、11 | 不把总结当验证结果 |

## 1. 触发分级

按用户意图选择最小工具路径：

| 意图 | 结论 |
| --- | --- |
| “阅读/分析代码库，整理结论” | 先走代码库理解结论包；Gemini CLI 仅在本机可用、认证 / 读取范围获授权且当前状态核验通过时作为只读候选；不可用、未认证或命中敏感边界时回退人工 / Codex 内置工具。 |
| “对齐设计和代码” | 输出设计-代码追踪矩阵；工具只辅助找入口和锚点。 |
| “安装 Gemini CLI / 调用 Gemini 分析代码” | 先做安装准入和隐私/联网/认证检查。 |
| “安装 AgentRC / 生成 agent instructions / readiness” | 先做写入范围和生成物治理检查。 |
| “安装 Understand Anything / 生成知识图谱 / 打开 dashboard” | 先做插件安装、写入目录、hook、图谱提交和隐私边界检查。 |
| “安装 Ponytail / 用 Ponytail review / 做最小正确实现检查” | 先做 Codex 插件、lifecycle hook、Node 依赖、写入配置和 CR 范围检查。 |
| “安装 Open Code Review / 用 OCR review / 接入 AI 代码评审工具” | 先做 CLI、Codex plugin、LLM provider、联网 / token、读取范围、写入会话目录、项目规则来源和架构师裁决边界检查。 |
| “参考 WorkBuddy / 让本地 Agent 读项目、改代码、跑验证” | 先做本地执行型 Coding Agent 准入；只允许生成候选 diff，必须读取项目上下文、写入范围、验证命令和冲突决策澄清门禁。 |
| “让工具直接改代码/跑测试/提交” | 回到 Harness、Execution Grant 和 `资深架构师`；本技能不授权执行。 |

## 2. 安装 / 调用准入

任何安装或调用外部工具前，至少确认：

```text
工具:
官方来源:
使用目的:
是否必须安装:
可替代人工路径:
联网需求:
认证 / token:
读取范围:
写入范围:
是否允许上传仓库内容:
是否允许生成配置文件:
是否允许运行 shell:
是否允许修改代码:
验证方式:
停止条件:
用户授权缺口:
```

默认建议先选择只读、非写入、最小范围、可审计输出。需要 `npm install`、`npx`、OAuth、API key、GitHub token、LLM token、写入 `.github/`、`.vscode/`、`AGENTS.md`、CI、项目配置或用户级工具配置时，必须显式列出并等待用户授权。当前机器已验证 Gemini CLI `0.49.0` 可在 Node `20.20.2` 下启动；这只代表本地命令可用，不代表已登录、可联网、可搜索、可读取任意仓库或可写文件。

## 3. 工具选择

| 工具 | 适合 | 不适合 |
| --- | --- | --- |
| Gemini CLI | 终端内快速阅读代码、解释仓库结构、辅助找入口路径、生成代码理解草稿、按提示输出 JSON/文本结论。 | 默认安装、联网、登录、写文件、改配置，或替代源码级 CR 与测试。 |
| AgentRC | 评估仓库 AI-readiness、生成/评估 agent instructions、eval、开发配置、监控上下文漂移。 | 默认写入 `.github/copilot-instructions.md`、`.vscode/mcp.json`、`.vscode/settings.json`、`agentrc.eval.json`、CI 配置或组织级策略。 |
| Understand Anything | 把大型代码库、文档库或知识库转成可搜索、可点击、可提问的知识图谱；适合新人 onboarding、团队共享结构视图、diff impact、domain view 和代码库理解 dashboard。 | 默认安装插件、运行远端安装脚本、写 `.understand-anything/`、启用 post-commit hook、提交 graph、把图谱当架构事实或替代 CR。 |
| Ponytail | 编码实现前做最小正确实现门禁，编码评审时做过度设计专项检查，识别可复用现有代码、标准库、平台原生能力、已安装依赖、单实现抽象、无用配置和可删除复杂度。 | 作为新主流程、替代 TDD / correctness / security / 架构 CR，或以“少写”为理由删除边界校验、错误处理、资金/权限/安全兜底和必要测试。 |
| Open Code Review | 对 Git diff、commit 或分支差异做结构化 AI 代码评审；适合在架构师 CR 前提供文件覆盖、行级问题和外部 Checker 证据，也可用 `.opencodereview/rule.json` 承载项目规则。 | 替代架构师源码级判断、项目编码约规、Wind 约规、TDD、测试结果、发布审批、自动修复授权，或在 LLM provider 未配置时写成可用 CR 结论。 |
| WorkBuddy / 本地执行型 Coding Agent | 在已授权本地仓库中先读项目上下文，再按项目规则生成候选 diff、依赖 / 配置变更建议、验证结果和修复建议。 | 默认安装、联网、写文件、覆盖配置、替代 `AGENTS.md`、`wind-coding-conventions`、`资深架构师` 源码级 CR/TDD 或生产授权。 |
| 人工 / Codex 内置工具 | 只读查看源码、运行本地验证、生成可审查结论。 | 大规模跨仓库上下文治理或外部工具专有能力。 |

环境可用性记录规则：

- 通用 Skill 只记录工具来源、能力边界、准入条件和交接格式；不把某台机器的安装路径、版本、shell 配置或登录状态写成默认可用能力。
- 如果当前会话已按用户授权完成安装或验证，只能在本轮交接、运维记录或 source-map 环境附注中说明，并标注为“当前机器 / 当前会话事实”；后续调用仍需重新确认认证、联网、读取范围、搜索、写文件和输出交接格式。
- AgentRC 与 Understand Anything 默认不安装。只有出现仓库上下文治理、AI-readiness/eval，或大型代码库知识图谱 / onboarding / diff impact 的明确目标时，再按本文件重新做安装、写入、联网、hook 和提交边界评估。

## 4. 陌生代码库阅读入口

触发后先产出代码库理解任务包：

```text
目标:
业务问题:
只读范围:
禁止事项:
重点入口:
期望输出:
源码锚点格式:
验证证据:
工具候选:
下一步 owner:
```

期望输出至少包含入口路径、模块职责、关键调用关系、运行/测试脚本、设计假设、事实/推断、置信度、残余问题。

## 5. 设计-代码对齐入口

当用户要求“对齐代码和设计”“看设计是否落到代码”“从代码反查设计偏差”时，输出：

```text
设计条款 / OpenSpec:
预期代码入口:
实际代码入口:
实现状态:
偏差:
影响范围:
测试 / 验证证据:
需要产品确认:
需要架构师确认:
工具辅助:
```

工具只能辅助定位和总结；偏差判断仍要回链到源码、测试、OpenSpec 和架构师评审。

## 6. 工具输出交接格式

工具输出进入 CR 或工程交接前，必须转成可审查结论包：

```text
工具:
版本 / 来源:
运行方式:
读取范围:
写入范围:
结论摘要:
源码事实:
模型推断:
关键文件 / 函数 / 类型:
设计-代码偏差:
验证命令 / 证据:
不确定性:
下一步 owner:
是否可进入架构师 CR:
```

没有源码锚点、没有验证证据、不能区分事实和推断的工具输出，不进入合并、发布或 CAD 判断。

## 6A. 本地执行型 Coding Agent 准入

WorkBuddy 类工具的可取之处是本地 IDE / 文件系统上下文扫描和生成-验证-修复闭环，不是代码风格来源。进入 AI Maker 前使用最小顺序：

```text
读项目上下文 -> 对齐项目 / 架构 / Wind 约规 -> 明确写入范围 -> 生成候选 diff -> 依赖 / 配置冲突决策澄清门禁 -> 运行验证 -> 架构师 CR -> 回写经验
```

准入规则：

- 先读取 `AGENTS.md`、现有包名 / 分层 / 命名 / 测试 / 构建脚本；Java 项目以 `wind-coding-conventions` 的通用层为规则来源，Wind/Nobe 专项按声明、依赖、包名、类型或模块上下文启用。
- 生成物只能作为候选 diff；系统设计、TDD、源码级 CR、安全可靠性、生产风险和受控工程执行仍回 `资深架构师`。
- 新增依赖、配置、公共 API、消息 / 状态 / 权限 / 安全、数据库迁移、覆盖同名配置或写入外部目录时，必须显式确认。
- 冲突时走决策澄清门禁：能根据源码和项目规则自答则记录依据；仍涉及 owner 选择、兼容性或风险责任时只问关键问题。
- 验证必须给出命令、范围和结果；无法验证时只能交接为“候选修改”，不能写成完成、测试通过或可上线。

## 7. AgentRC 触发入口

AgentRC 适合用于上下文工程治理：

- 评估仓库 AI-readiness、缺失的构建/测试/lint/架构/服务上下文。
- 生成或评估 agent instructions、eval 和开发配置。
- 检查 instructions 是否随着代码演进而 stale。
- 为多 Agent 或跨团队仓库建立可维护的上下文资产。

触发时先问清是否允许生成或修改以下文件：`.github/copilot-instructions.md`、`.vscode/mcp.json`、`.vscode/settings.json`、`agentrc.eval.json`、`AGENTS.md`、CI 配置。若只做评估，优先要求 dry-run、JSON 输出或评审目录，不直接写入仓库根目录。

## 8. Gemini CLI 触发入口

Gemini CLI 适合用于快速代码理解和终端辅助：

- 分析现有代码库结构、入口路径和关键源码。
- 解释某个模块、接口、配置或调用链。
- 生成代码理解草稿、重构影响说明或 CR 前的结构导览。
- 在用户授权后使用非交互提示输出文本或 JSON 结论。

触发时必须检查是否需要 Google 账号/OAuth、API key、Google Cloud 项目、联网、搜索、文件写入或 shell 命令。若只是阅读代码，默认约束为只读、禁止写文件、禁止运行破坏性 shell、禁止上传敏感材料。当前机器可用命令为 `gemini 0.49.0`，但首次真实调用仍可能需要用户完成认证；应优先使用 `--approval-mode plan`、明确只读目录和结构化输出要求。

## 9. Understand Anything 触发入口

Understand Anything 适合用于大型代码库或团队共享理解视图：

- 生成代码库结构知识图谱、guided tours、layer visualization、domain view、diff impact analysis 或 onboarding guide。
- 把 `.understand-anything/knowledge-graph.json` 作为可审查的理解辅助产物，帮助 reviewer 看入口、模块、依赖和影响范围。
- 对知识库或文档库做图谱化探索，但仍要区分源码事实、LLM 语义摘要和人工确认结论。

默认评估结论：

- **不建议默认安装**：它是外部插件 / 多平台安装脚本，会克隆到 `~/.understand-anything/repo`，并可能写入项目 `.understand-anything/` 目录；只在大型代码库理解、团队共享图谱、diff impact 或 onboarding 明确需要时建议安装。
- **优先只读试点**：如需试用，先限定仓库/子目录、禁止 auto-update、禁止提交图谱、禁止 post-commit hook、禁止读取密钥和生产配置，输出到可评审目录或本地临时目录。
- **图谱是否提交另行决策**：README 建议可提交 `.understand-anything/` 中除 `intermediate/` 和 `diff-overlay.json` 外的图谱；本仓库默认不采用该建议，必须由项目 owner 决定是否纳入版本库、是否使用 Git LFS、是否包含敏感路径。

触发时必须检查：

```text
是否安装插件:
安装方式: Claude plugin / install.sh codex / 其他平台
是否允许联网和 clone:
是否允许写 ~/.understand-anything:
是否允许写项目 .understand-anything/:
是否允许 dashboard 本地服务:
是否允许 auto-update / post-commit hook:
是否允许提交 knowledge-graph.json:
扫描范围:
排除目录:
敏感文件 / 密钥 / 生产配置处理:
图谱用途: onboarding / CR / diff impact / domain view / 知识库
图谱进入 CR 的人工校验 owner:
```

工具输出交接必须包含：

```text
knowledge-graph 位置:
扫描范围:
生成命令:
写入文件:
结构事实:
LLM 摘要 / 推断:
入口节点:
关键模块:
diff impact:
源码锚点:
需要架构师确认:
是否允许提交图谱:
```

## 10. Ponytail 触发入口

Ponytail 适合用于“代码越写越臃肿”的局部纠偏：

- 编码前检查是否可以不做、复用仓库已有能力、使用标准库、使用平台原生能力、使用已安装依赖或用更小实现完成。
- 编码评审时只做过度设计专项 CR，找可删除代码、重复造轮子、无用抽象、单实现接口、未来化配置和无主依赖。
- 架构排熵时辅助识别低风险可删除候选，但删除生产路径、公共契约、兼容分支和核心依赖仍必须交给架构师和人工 owner。

Ponytail 插件准入必须检查：

```text
是否安装 Codex plugin:
插件来源与版本:
是否包含 lifecycle hooks:
是否需要 node:
是否需要联网 / marketplace:
是否写入 Codex 配置或插件 cache:
启用模式: lite / full / ultra
适用阶段: 编码实现 / 编码评审 / 架构排熵
不适用阶段: PRD 正文 / 系分主判断 / 安全评审 / 发布审批
是否允许修改代码:
是否允许 Git 操作:
源码级 Checker owner:
```

默认集成边界：

- **建议启用**：代码实现前的最小正确实现门禁、CR 中的过度设计专项 pass、架构排熵中的可删除性候选识别。
- **不建议默认全局化**：不覆盖产品专家、架构师、TDD、安全、可靠性和生产发布门禁。
- **不复制外部规则全文**：只吸收“少写但不省理解、不省验证”的方法；先读懂真实上下文、数据流和项目约规，再判断能否不写、复用或最小实现；插件 hook 和命令由用户显式安装和信任。
- **不把少写当目标**：代码变少是结果，不是 code golf；目标是只写任务需要且不牺牲输入校验、错误处理、安全、可访问性、资金 / 权限 / 生产兜底、持久化意图、幂等、审计和必要测试。
- **不把 benchmark 当项目事实**：外部 benchmark 和收益数据只能作为参考，项目内仍看 diff 体积、返工率、CR 轮次、缺陷率、回滚率和 owner 理解程度。

## 10A. Open Code Review 触发入口

Open Code Review 适合做“外部代码评审 Checker”，不是新的编码规范来源：

- 对当前 staged / unstaged / untracked diff 做结构化 Review，先用 `ocr review --preview` 看覆盖范围。
- 对单个 commit 或分支差异做 Review，使用 `--commit` 或 `--from` / `--to`。
- 用 `--background` 注入业务目标、OpenSpec、验收种子、Wind 约规或架构师 CR 重点，降低泛泛而谈。
- 用项目级 `.opencodereview/rule.json` 或 `--rule` 引用项目规则；Java 项目可注入通用约规，命中 Wind/Nobe 信号后再加入 Wind 专项摘要，权威仍是 `wind-coding-conventions` 和项目 `AGENTS.md`。

准入检查：

```text
CLI 是否可用:
Codex plugin 是否可用:
版本 / 来源:
LLM provider 是否配置并通过 ocr llm test:
是否允许联网 / 调 LLM:
是否允许上传 diff / 代码片段到模型端:
读取范围: workspace / commit / from-to / scan path
文件覆盖: preview 的 Will review / Excluded 清单是否覆盖本次关键文件
写入范围: ~/.opencodereview session / 项目 rule.json / 无
规则来源: 项目 AGENTS.md / 架构师通用工程红线 / Wind 约规 / 自定义 rule
是否只预览:
是否允许自动修复:
架构师 CR owner:
```

默认调用顺序：

```text
ocr review --preview
ocr llm test
ocr review --audience agent --background "<业务目标 / Spec / 约规 / Review 重点>"
```

边界：

- `ocr review --preview` 只证明文件选择可预览，不证明 LLM 连通、Review 有效或代码通过。
- 先检查 `ocr review --preview` 的 Will review / Excluded 清单；被 `unsupported_ext` 或规则过滤排除的 Markdown、Skill 文档、配置、SQL、脚本等关键文件，不能算入 OCR 覆盖证据，必须由架构师或对应 Skill 继续人工 / 脚本 CR。
- `ocr llm test` 未通过时，不进入 OCR AI Review；只能报告配置缺口和人工替代路径。
- OCR 输出必须按严重级别、源码锚点、真实性、是否符合项目 / Wind / 架构师约规重新判读；低置信度、定位失败或无上下文建议不得直接采纳。
- 自动修复必须单独授权，且修复后仍需 TDD / 测试 / 静态检查 / 架构师 CR；不能把 OCR 的 fix 建议当 Execution Grant、Git 授权或合并准出。
- 对敏感代码、生产配置、密钥、客户数据或禁止外发仓库，必须确认模型端、网关和脱敏边界；不清楚时不调用 OCR。

## 11. 红线

- 不把 Gemini CLI、AgentRC、Understand Anything、Ponytail、Open Code Review、WorkBuddy 或任何外部工具写成当前会话默认可用。
- 不默认安装、联网、登录、写文件、写配置或改代码；需要时必须列出授权缺口并等待用户确认。
- 不默认运行远端安装脚本、插件安装命令、lifecycle hook、`/understand`、`/understand --auto-update`、dashboard、本地服务、post-commit hook 或 Git LFS 配置。
- 不默认写入 `.github/copilot-instructions.md`、`.vscode/mcp.json`、`.vscode/settings.json`、`agentrc.eval.json`、`AGENTS.md`、CI 配置或组织级策略。
- 不默认写入、提交或同步 `.understand-anything/`、`knowledge-graph.json`、图谱中间产物、dashboard 产物或 hook。
- 不在未授权时安装 npm 包、运行 `npx`、登录 OAuth、读取 token、写配置、修改代码或启动 CI。
- 不把工具生成的说明文件、eval 或 MCP 配置直接当团队规范；必须进入 CR。
- 不把 WorkBuddy 类工具输出当成项目编码约规；默认先服从项目 `AGENTS.md`、项目已有代码风格、`wind-coding-conventions` 的通用 Java 规则、按上下文启用的 Wind/Nobe 专项和 `资深架构师` 源码级判断。
- 不把工具总结当作源码事实；关键结论必须回链文件路径、函数、类型、配置或验证命令。
- 不把 Ponytail 的“少写”当作删除输入校验、错误处理、安全、可访问性、资金/权限/生产兜底或必要测试的理由。
- 不把 Open Code Review 输出当作项目规范、架构师 CR 结论、测试通过、发布准出或自动修复授权；它只是外部 Checker 证据源。
- 不把外部 benchmark、star 数或插件生态热度写成当前项目收益、工程质量、测试通过、CR 结论或上线依据。
- 不把工具输出当作 Execution Grant、CAD 授权、测试通过、发布批准或合规结论。
