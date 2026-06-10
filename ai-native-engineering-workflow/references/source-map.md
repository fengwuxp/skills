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
- 微信文章 [《万字长文 | Spec 驱动开发实战：半年踩坑，我们如何让 AI 编码的交付真正闭环》](https://mp.weixin.qq.com/s/d1j7JCOkAFd5L-W1LK-Qug)：作为 AI Native 研发流程中 `code-delivery-closed-loop.md` 和 `spec-template-practices.md` 的公开参考来源。账号字段为 `dolphin07`，页面时间字段为 2026-06-04 21:22:27 Asia/Shanghai；2026-06-06 普通 `web.open` 未取得正文，随后通过移动端微信 UA 公开 HTML 读取标题、账号、页面时间字段和正文；2026-06-06 本轮再次通过移动端微信 UA 公开 HTML 读取正文并解析为本地纯文本用于复核。本仓库只吸收减层、上下文注入、机器验证、自适应强度、Form Follows Reviewer、Spec 五段式骨架、AC 编号、Given-When-Then、AC 与测试映射、spec-lint、AC 覆盖、漂移检查、风险自查、Orchestrator / Knowledge / Delivery 三层 Harness、独立验证、CR 减负、知识回流和轻重流程切换等可迁移方法；不复制原文、图片、案例细节、ASD / SSD Harness 命令体系、目录结构、脚本、长模板、作者表达或标题传播话术，也不把外部 Harness 写成当前会话默认依赖或执行授权。
- 微信文章 [《Spec 驱动开发：让 AI 知道该写什么，不该写什么》](https://mp.weixin.qq.com/s/VcITOOUVrw_BGxJQA_mtaw)：作为 AI Native 研发流程中 `spec-template-practices.md` 的公开参考来源。作者字段为 `凌小添`，页面时间字段为 2026-05-18 09:33:00 Asia/Shanghai；2026-06-08 普通 `web.open` 未取得正文，普通 `curl` 返回微信验证页，本地 Node Playwright 包不可用且未新增依赖，随后通过本机 Chrome headless 等价浏览器读取标题、作者、页面时间字段和正文。本仓库只吸收 PRD / SDD / 实现 Spec 三层边界、每层可轻量但不可缺失、实现 Spec 要写清背景、功能边界、模块、接口、技术约束、验收标准、项目规则文件与单需求 Spec 的分工、Spec 作为实现和 CR 检查清单以及偏差先更新 Spec 再修改实现等可迁移方法；不复制原文、示例需求、标题传播话术、作者表达或效率数字，也不把单篇文章写成跳过产品评审、系统设计、测试、CR 或 Execution Grant 的理由。
- 微信文章 [《规范驱动开发（SDD）：用 AI 写生产级代码的完整指南》](https://mp.weixin.qq.com/s/SOonScQJ18GGVCD-t9PJWA)：作为 AI Native 研发流程中 `spec-template-practices.md`、`code-delivery-closed-loop.md` 和 `verification-review-release.md` 的公开参考来源。账号字段为 `mmj学AI`，作者字段为空，页面时间字段为 2026-06-04 07:00:00 Asia/Shanghai；2026-06-10 通过移动端微信 UA 公开 HTML 读取标题、作者/账号、发布时间和正文，正文位于 `#js_content`。本仓库只吸收 Spec 作为事实来源、清晰 / 完整 / 上下文化 / 具体 / 可测试、结构化契约、正反例、测试计划、五支柱验证、AI 错误模式、失败回写 Spec 再重试、CI/CD 追踪和渐进落地等可迁移方法；不复制原文、示例 Auth 规范、工具清单、ROI / 效率数字、案例指标、作者表达或标题传播话术，也不把文中 AWS Kiro、Windsurf、Cursor、Claude Code、Aider、Amazon Q Developer、GitHub Copilot、GitHub Spec Kit、HumanLayer、Tessl、Lovable 等工具能力写成当前会话默认依赖、最新事实或执行授权。
- 微信文章 [《我们落地了 SDD，为什么团队效率没有体感提升？》](https://mp.weixin.qq.com/s/LEoZtLOyk-7qGY6Q-b7r2A)：作为 AI Native 研发流程中 AI Coding 端到端交付瓶颈、全栈 Spec、Harness Engineering、CR 高频问题机器化、知识回流和交付指标的公开参考来源。账号字段为 `dolphin07`，页面时间字段为 2026-05-21 19:46:29 Asia/Shanghai；2026-06-06 普通 `web.open` 未取得正文，随后通过移动端微信 UA 公开 HTML 读取标题、账号、页面时间字段和正文。本仓库只吸收编码提速不等于交付提速、上下文覆盖、Spec Review、CONTEXT.md / AGENTS.md / CLAUDE.md 等项目上下文资产、CR 高频问题转机器门禁、一次通过率 / 返工率 / 缺陷密度等指标和反馈飞轮；不复制原文、图示、数据口径、案例、模板、工具宣传、作者表达或标题传播话术，也不把文章中的比例和团队经验写成通用事实或项目当前指标。
- 微信文章 [《终于有人开始解决 AI Coding 最大的问题了：看不懂代码》](https://mp.weixin.qq.com/s/JWtKELqDYvdPZtDzeJNybQ)：作为 AI Native 研发流程中变更可理解性、结构上下文、影响可视化和 AI 代码 Review 交接门禁的公开参考来源。2026-06-04 已通过移动端微信 UA 公开 HTML 读取标题、作者、页面时间线索和正文；本仓库只吸收“AI 生成代码后需要共享结构视图、影响导览和源码锚点辅助 Review”的可迁移流程，不复制原文、工具宣传、命令示例、截图或作者表达，也不把任何外部可视化 CLI、IDE 插件或厂商预览能力写成默认依赖。
- 微信文章 [《PRD 评审总返工？跟我把IPD的6个强角色、3个硬任务塞进你的Agent系统》](https://mp.weixin.qq.com/s/Q7jtu6Cihr0Fs0Fy1-USUg)：作为 AI Native 研发流程中 `prd-system-design-review.md` 的公开参考来源。作者与账号字段均为 `产品AI力学`，发布时间字段为 2026-06-04 19:00:00 Asia/Shanghai；2026-06-05 普通 UA 返回微信“环境异常”验证页，随后通过移动端微信 UA 公开 HTML 读取标题、作者、账号、发布时间和正文。本仓库只吸收 A2A 虚拟评审、IPD 多角色反向拷问、Market/Delivery/Tech/QA/UX 挑战视角、PO 对反馈做 `ACCEPT/REJECT/PENDING` 决策、`review_task` / `evaluation_task` / `reporting_task` 三段任务、决策日志、接受项、分歧项和风险清单的可迁移方法；不复制原文、图片、案例细节、CrewAI/Codex/Claude 互调方式、Computer Use 做法、长 prompt、外部 Skill 原文、成本数字、作者表达或标题传播话术，也不把虚拟评审写成正式 IPD、合规确认、架构批准或 Execution Grant。
- 微信文章 [《完整不等于可测：需求评审的四个AI新维度》](https://mp.weixin.qq.com/s/7EiFz1Oka1tYQmfbBferQg)：作为 AI Native 研发流程中 PRD 评审会前 AI 预扫描和 `prd-system-design-review.md` 的产品专家接入参考来源。作者/账号为 `Maywen测开AI手记`，页面时间字段为 2026-06-08 12:52:41 Asia/Shanghai；2026-06-08 `web.open` 未取得正文，随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文。本仓库只吸收完整性、一致性、可测试性、二义性四维预扫描、疑似问题清单、人工过滤/排序和 owner 决策边界；不复制原文、效果数字、示例句子、标题传播话术或作者表达，也不把 AI 预扫描写成正式评审、测试设计或产品决策的替代品。
- 微信文章 [《阿里内网万言离职书〈置身钉内〉原文，已刷屏》](https://mp.weixin.qq.com/s/_D20O0vpPXjSzjAKJmBYuA)：作为 AI Native 研发流程中 `gsd-cad-admission.md` 的公开转述/OCR 复盘参考来源。作者为 `Corgi/滕雅辛`，公众号为 `爬梯意外簿`，发布时间为 2026-06-05 16:21；2026-06-07 普通 `curl` 返回微信“环境异常”验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、账号、作者、发布时间和正文；页面正文声明内容由 AI 识图整理。本仓库只吸收 AI 产品从战略叙事、AI 原型或发布会目标进入工程化前应检查业务 context、真实工作流、用户收益/负担、权限责任、旧系统接入、灰度止损、成本稳定性和事实边界；不复制原文、项目细节、组织评价、作者表达或标题传播话术，也不把文章内容写成钉钉/ONE 官方事实、行业结论、当前工具能力或 Execution Grant。
- 微信文章 [《从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战》](https://mp.weixin.qq.com/s/HzbdrmNkT-OTRKdQh0c0Ug)：作为 AI Native 研发流程中 `product-to-engineering-lifecycle.md` 的公开参考来源。作者/账号为 `KEEN的创享`，发布时间为 2026-06-04 21:39 Asia/Shanghai；2026-06-07 普通 `curl` / `web.open` 未取得正文或返回微信“环境异常”验证页，随后通过移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文。本仓库只吸收“模糊需求 -> 结构化需求文档 -> 业务流 -> 原型/页面说明 -> 开发执行任务 -> 验收发布路径”的可迁移系统组织链路；不复制原文、图片、项目案例细节、提示词、页面设计、技术选型或作者表达，也不把示例项目写成通用架构事实或执行授权。
- 微信文章 [《架构30：架构思维：需求分析》](https://mp.weixin.qq.com/s/B8Rap_MmAKmVN3f7eAnvCw)：作为 AI Native 研发流程中需求分析协同门禁、产品专家到架构师交接、PRD / 系分预审和 GSD Round 0 的公开参考来源。作者字段为 `开心就好TF`，页面时间字段为 2026-06-07 09:34:00 Asia/Shanghai；2026-06-09 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文（发布时间取页面时间字段）。本仓库只吸收用户表述到根源需求、产品定义、产品边界 / 上下游分工、稳定点 / 变化点必须带边界坐标、架构师参与需求澄清和反过度设计的可迁移方法；不复制原文、案例、作者表达、标题传播话术或时间投入比例，也不把文章观点写成组织制度、当前项目事实或执行授权。
- 微信文章 [《[013] 标准不是摆设——需求标准、设计标准、编码标准怎么写》](https://mp.weixin.qq.com/s/W44YHT-9bUCrSjsrZIYItw) 与 [《[014] 85%返工都是需求的锅——为啥说需求是软件的根本》](https://mp.weixin.qq.com/s/MO8EsLHm9QNauNLDQ1Z05Q)：作为 AI Native 研发流程中需求基线稳定性、需求 / 设计 / 编码标准门禁、Spec 模板和测试门禁的公开参考来源。账号/作者字段为 `AIIIIlIIII`；页面时间字段分别为 2026-05-23 07:24:00 与 2026-05-26 06:21:00 Asia/Shanghai；2026-06-09 首篇 `web.open` 未取得正文，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。本仓库只吸收需求条目质量、图文追踪、衍生需求、系统需求未确认不下钻、HLR/LLR 分工、需求驱动测试、编码规则原因/示例/验证方式和防御式编程门禁；不复制原文、适航/DO-178C 语境、标题比例、案例、作者表达或标准条文，也不把单篇文章写成通用合规结论、项目制度或 Execution Grant。
- 微信文章 [《一个让Codex变得越来越聪明的小方法》](https://mp.weixin.qq.com/s/G-tZjkhAd_yMAABBgNGVdw)：作为 AI Native 研发流程中知识回流、授权学习和 Skill 经验归位的公开参考来源。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `Dr.Joyi`，既有账号线索保留 `像素与咖啡时光`，页面时间字段为 2026-06-04。本仓库只吸收“反复踩坑来自稳定上下文缺失，执行经验、偏好理念和项目知识要进入合适载体”的可迁移方法，并落实到 `code-delivery-closed-loop.md` 的授权学习与经验归位；不复制原文、段落表达、个人经历、提示词或作者口吻，也不把用户长期偏好写入仓库、安装目录或未授权学习目录。
- 微信文章 [《如何让 AI 画出高质量架构图，一个Skill搞定》](https://mp.weixin.qq.com/s/tE0kfJ2ZHeGGz6xCgEp3Zg)：作为 AI Native 研发流程中陌生代码库图形化理解和代码库理解门禁的公开参考来源。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `Davon Dong`，既有账号线索保留 `日积月码`，页面时间字段为 2026-05-12。本仓库只吸收“先分析代码库形成架构描述，再生成可编辑架构图，并通过业务/组件/连接关系迭代校验”的方法，落到 `agentic-engineering-governance.md` 的图形化理解 brief；不安装文中提到的外部 Skill，不复制项目安装指令、示例提示词、截图、模板、工具宣传语或作者表达，也不把外部工具生成结果当作架构质量结论。
- `obra/superpowers`：`https://github.com/obra/superpowers`。2026-06-07 通过 GitHub API 读取 skills 目录和 README，下载 `main.zip` 到临时目录并审查 `skills/`、LICENSE、脚本和 hooks；main commit 为 `6fd4507659784c351abbd2bc264c7162cfd386dc`，zip SHA256 为 `ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3`，许可证为 MIT。已将 14 个 Markdown skill 资源和 LICENSE 复制到 `references/external-superpowers/`，并用 `superpowers-skill-library.md` 建立调度索引。本仓库只吸收 brainstorming、writing-plans、executing-plans、subagent-driven-development、test-driven-development、requesting-code-review、receiving-code-review、systematic-debugging、verification-before-completion、using-git-worktrees、finishing-a-development-branch 和 writing-skills 的可迁移工程纪律；不复制或运行外部脚本、hooks、插件 manifest、package 脚本、安装流程、图片资产或跨平台启动方式，也不把外部默认文档路径、自动提交、Git 推送、worktree、subagent 连续执行要求写成本仓库默认行为。
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
- 可以吸收 Superpowers skills 的 Spec 前置澄清、实施计划拆解、TDD 红绿重构、受控执行、代码评审、调试、完成前验证和分支收尾检查方法，但必须先经过 `superpowers-skill-library.md` 调度边界。
- 可以吸收模糊需求到可开发系统的秩序链路、前后台/多端/运营能力分工、业务流到原型再到开发任务的交接门禁。
- 可以吸收需求基线稳定性、需求标准、设计标准、编码标准、HLR/LLR 分工、图文追踪、衍生需求、防御式编程和需求驱动测试门禁；不得把行业专属标准原样写成所有项目强制流程。
- 可以吸收 AI Coding / SDD / Spec / Harness 最终代码交付闭环、Spec 模板最佳实践、PRD / SDD / 实现 Spec 三层边界、Spec 事实来源、结构化契约、正反例、五支柱验证、失败回写 Spec 重试环、减层、上下文注入、机器验证、自适应强度、Form Follows Reviewer、AC 与测试映射、spec-lint、AC 覆盖、漂移检查、风险自查、CR 减负、知识回流和交付指标方法。
- 可以吸收 PRD / 系分合议预审、MAGI 三角色、IPD 式互审、锚点化反馈、`ACCEPT/REJECT/PENDING` 决策日志、接受项、分歧项、风险清单和准出 / 停止条件。
- 可以吸收需求评审前 AI 预扫描的完整性、一致性、可测试性、二义性四维度，并把疑似问题接入 `review_task`、`evaluation_task` 和 `reporting_task`，但必须保留人工 owner 决策。
- 可以吸收 AI 代码变更可理解性、代码库理解结论包、结构上下文、入口路径、源码锚点、影响模块、调用关系、边界变化和可视化辅助 Review 的流程门禁。
- 可以吸收授权学习、经验归位、知识回流、图形化理解 brief 和陌生代码库架构描述转图的流程门禁。
- 可以吸收 AI 产品工程化前的业务 context、真实工作流、用户收益/负担、权限责任、旧系统接入、灰度止损、成本稳定性和事实边界门禁。
- 可以吸收 Gemini CLI、AgentRC 等官方工具的触发场景、安装准入、只读/写入边界、上下文漂移检查、设计-代码对齐和工具输出交接要求。
- 不复制文章正文、博客原文、PDF 大段内容、图示、截图、工具提示词、厂商案例或作者表达。
- 不把任一工具的能力写成当前会话必然可用；实际执行必须以当前 Codex 工具、项目权限和用户授权为准。
- 不把 AI 快速阅读、上下文生成、可视化或结构化思考工具写成默认依赖；只吸收“事实锚点、推断边界、验证证据、上下文漂移检查和人工 CR 交接”的方法。
- 不把用户长期偏好、个人工作方式或对话历史写入仓库、安装目录或未授权学习目录；长期学习必须遵守仓库 `AGENTS.md` 和 `~/.skill-learning/` 授权边界。
- 不把第三方安全、AI 风险或管理体系材料写成组织已满足的审计、合规或认证结论。
