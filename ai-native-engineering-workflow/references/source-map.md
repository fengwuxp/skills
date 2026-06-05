# AI Native 研发流程编排公开来源与边界

本文记录 `ai-native-engineering-workflow` Skill 的公开来源、读取状态、应用位置和不吸收边界。它不是流程正文；设计具体流程时仍应读取生命周期、Agentic Engineering 和验证发布 reference。

## 使用时机

- 需要核对 AI Native 产品研发流程参考了哪些公开来源。
- 用户要求继续从外部文章、官方文档或工具实践中吸收流程方法。
- 修改本 Skill 的来源边界、README 外部参考记录或触发验证前，需要确认归因口径。

## 不适用场景

- 不用于直接产出流程方案；流程方案应读取 `product-to-engineering-lifecycle.md`、`agentic-engineering-governance.md` 和 `verification-review-release.md`。
- 不把外部文章、厂商文档或工具产品能力当作当前会话可用工具、团队制度、官方承诺或执行授权。
- 未读取到正文的来源不得写成已吸收内容。

## 读取后必须产出

- 来源状态：可复核、官方来源、公开转述、验证页、当前不可复核或历史索引线索。
- 可吸收边界：只吸收流程方法、检查项、权限边界、验证方式和角色协作，不复制原文、图示、案例或厂商宣传。
- 时效性边界：涉及工具能力、模型能力、法律合规、安全基线和平台限制时，必须按最新官方来源或当前会话工具状态重新核验。

## 需要继续读取的 reference

- 产品到工程流程读 `product-to-engineering-lifecycle.md`。
- Agentic Engineering 治理读 `agentic-engineering-governance.md`。
- 验证、CR、发布和复盘读 `verification-review-release.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核对来源状态 | `读取与归因规则`、`已参考的公开来源` | 不读取流程正文 |
| 新增外部来源 | `读取与归因规则`、`提炼边界` | 不把未读正文来源标为已吸收 |
| 判断工具能力是否当前可用 | `时效性边界` | 不用历史来源替代当前工具状态 |

## 读取与归因规则

- 外部文章必须以实际读取到的正文或公开页面为依据；常规抓取失败时，应改用 Playwright 或等价浏览器自动化。
- 微信原文、本地转述、官方博客和第三方转载必须分开记录，不混写成同一证据。
- 未读取到正文、只剩验证页、动态页面失败或正文为空的来源，只能作为待核验线索，不得作为已吸收来源。
- 进入 Skill 的内容只保留可迁移方法、检查项、路由和边界；不复制原文、图示、标题传播话术、案例细节、作者表达或厂商宣传。
- 本文记录历史读取状态，不代表来源仍然最新可用；涉及 OpenAI、GitHub、Anthropic、Google、NIST、OWASP、ISO 或其他工具/标准的当前能力和规则时，应重新核验官方来源或当前会话工具状态。

## 已参考的公开来源

- 微信文章链接 `https://mp.weixin.qq.com/s/hRZ8zbkW4-PRyBYXn8bxbQ`：2026-06-04 普通 `curl` 返回微信“环境异常”验证页，未读取到正文；本仓库不把该链接作为已吸收来源，只作为用户提供的待核验线索。
- 微信文章 [《终于有人开始解决 AI Coding 最大的问题了：看不懂代码》](https://mp.weixin.qq.com/s/JWtKELqDYvdPZtDzeJNybQ)：作为 AI Native 研发流程中变更可理解性、结构上下文、影响可视化和 AI 代码 Review 交接门禁的公开参考来源。2026-06-04 已通过移动端微信 UA 公开 HTML 读取标题、作者、页面时间线索和正文；本仓库只吸收“AI 生成代码后需要共享结构视图、影响导览和源码锚点辅助 Review”的可迁移流程，不复制原文、工具宣传、命令示例、截图或作者表达，也不把任何外部可视化 CLI、IDE 插件或厂商预览能力写成默认依赖。
- 微信文章 [《PRD 评审总返工？跟我把IPD的6个强角色、3个硬任务塞进你的Agent系统》](https://mp.weixin.qq.com/s/Q7jtu6Cihr0Fs0Fy1-USUg)：作为 AI Native 研发流程中 `prd-system-design-review.md` 的公开参考来源。作者与账号字段均为 `产品AI力学`，发布时间字段为 2026-06-04 19:00:00 Asia/Shanghai；2026-06-05 普通 UA 返回微信“环境异常”验证页，随后通过移动端微信 UA 公开 HTML 读取标题、作者、账号、发布时间和正文。本仓库只吸收 A2A 虚拟评审、IPD 多角色反向拷问、Market/Delivery/Tech/QA/UX 挑战视角、PO 对反馈做 `ACCEPT/REJECT/PENDING` 决策、`review_task` / `evaluation_task` / `reporting_task` 三段任务、决策日志、接受项、分歧项和风险清单的可迁移方法；不复制原文、图片、案例细节、CrewAI/Codex/Claude 互调方式、Computer Use 做法、长 prompt、外部 Skill 原文、成本数字、作者表达或标题传播话术，也不把虚拟评审写成正式 IPD、合规确认、架构批准或 Execution Grant。
- Google Gemini CLI：`https://github.com/google-gemini/gemini-cli`。2026-06-04 本轮读取 GitHub README 和 get-started 文档；其公开描述为开源终端 AI Agent，支持查询和编辑大型代码库、文件操作、shell 命令、web fetch/search、MCP、项目上下文文件和脚本化输出；官方快速安装包含 `npx @google/gemini-cli`、`npm install -g @google/gemini-cli`、Homebrew 等方式，并要求认证。本仓库只吸收“代码库快速理解要输出入口路径、源码锚点、验证证据和不确定性”的流程方法，不默认安装、登录、联网、上传仓库或使用其写入能力。
- Microsoft AgentRC：`https://github.com/microsoft/agentrc`。2026-06-04 本轮读取 GitHub README；其公开描述为 AI coding agents 的 context engineering 工具，会读取代码库，评估 AI-readiness，生成仓库指令、eval 和开发配置，并在 CI 中监控上下文漂移；README 标注 Experimental，示例命令包含 `npx github:microsoft/agentrc`、`readiness`、`instructions`、`eval`，且生成物可能包括 `.github/copilot-instructions.md`、`.vscode/mcp.json`、`.vscode/settings.json` 和 `agentrc.eval.json`。本仓库只吸收“仓库上下文要可生成、可评估、可维护，且防止 stale context”的治理方法，不把 AgentRC 生成物当成本仓库默认文件，也不默认写入 `.github/`、`.vscode/` 或 CI。
- Microsoft Clarity Agent：`https://github.com/microsoft/clarity-agent`。2026-06-04 读取 GitHub README；其公开描述为结构化思考伙伴，可在仓库中形成 `.clarity-protocol/`，记录问题、方案、失败分析、决策和 stale tracking。本仓库只吸收“代码库理解结论包需要问题、方案、失败模式、决策和过期风险”的交接结构，不把它写成代码快速阅读工具或默认依赖。
- 智东西转载/转述文章《Claude产品团队工作模式被公开了！》：`https://zhidx.com/p/546178.html`。2026-06-04 公开 HTML 可读取标题和正文；公开内容用于参考 Claude 产品团队在 AI 时代的原型、eval、角色融合、模型能力复议和组织协作变化。不复制原文、图片、作者表达或媒体标题传播话术。
- Anthropic 官方博客《Product development in the agentic era》：`https://claude.com/blog/product-development-in-the-agentic-era`。公开内容用于参考 Agentic era 下产品开发方式、角色协作和 AI 工具介入产品流程的方向；涉及 Anthropic 产品能力和组织实践时需重新核验官方页面。
- OpenAI Codex 公开资料：`https://openai.com/index/introducing-codex/` 与 `https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf`。公开内容用于参考云端软件工程 Agent、隔离环境、日志、测试输出、人类 Review 和工程团队使用 Codex 的协作方式；具体 Codex 当前能力以官方文档和当前会话工具状态为准。
- GitHub Copilot coding agent 与 code review 文档：`https://docs.github.com/en/copilot/concepts/about-copilot-coding-agent`、`https://docs.github.com/en/copilot/concepts/agents/code-review`。公开内容用于参考后台 Agent、Pull Request 工作流、代码评审和人类审批边界；具体能力以 GitHub 当前官方文档和仓库权限为准。
- Google People + AI Guidebook：`https://pair.withgoogle.com/guidebook-v2/`。公开内容用于参考 AI 产品中的用户心智、反馈、控制、失败恢复和人机协作设计；不复制 guidebook 模板或图示。
- NIST AI Risk Management Framework Generative AI Profile：`https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence`。公开内容用于参考 AI 风险识别、评估、治理和验证闭环；不把其写成企业已满足的合规结论。
- OWASP Top 10 for LLM Applications 2025：`https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf`。公开内容用于参考 prompt injection、敏感信息泄漏、过度授权、供应链和 Agent 风险；具体安全控制仍需安全负责人确认。
- ISO/IEC 42001：`https://www.iso.org/standard/81230.html`。公开内容用于参考 AI 管理体系、责任、风险、控制和持续改进；不把其作为认证或合规结论。

## 提炼边界

- 可以吸收 AI Native 产品研发流程、Agentic Engineering、OpenSpec/Harness/GSD/CAD、验证矩阵、CR、发布和复盘方法。
- 可以吸收 PRD / 系分合议预审、MAGI 三角色、IPD 式互审、锚点化反馈、`ACCEPT/REJECT/PENDING` 决策日志、接受项、分歧项、风险清单和准出 / 停止条件。
- 可以吸收 AI 代码变更可理解性、代码库理解结论包、结构上下文、入口路径、源码锚点、影响模块、调用关系、边界变化和可视化辅助 Review 的流程门禁。
- 可以吸收 Gemini CLI、AgentRC 等官方工具的触发场景、安装准入、只读/写入边界、上下文漂移检查、设计-代码对齐和工具输出交接要求。
- 不复制文章正文、博客原文、PDF 大段内容、图示、截图、工具提示词、厂商案例或作者表达。
- 不把任一工具的能力写成当前会话必然可用；实际执行必须以当前 Codex 工具、项目权限和用户授权为准。
- 不把 AI 快速阅读、上下文生成、可视化或结构化思考工具写成默认依赖；只吸收“事实锚点、推断边界、验证证据、上下文漂移检查和人工 CR 交接”的方法。
- 不把第三方安全、AI 风险或管理体系材料写成组织已满足的审计、合规或认证结论。
