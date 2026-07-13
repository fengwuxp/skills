# Superpowers Skill Library 外部参考

本文记录 `obra/superpowers` 和 Matt Pocock skills 的审查结果、供应链边界和 AI Native 调度方式。它是外部参考索引，不是本仓库的顶层可安装 Skill，也不是当前会话的自动执行授权。

## 使用时机

- 用户点名 Superpowers、Superpowers skills、brainstorming、writing-plans、executing-plans、subagent-driven-development、test-driven-development、requesting-code-review、verification-before-completion 等外部技能。
- 用户点名 Matt Pocock skills、`grill-me`、Trellis、轻量问询、盘问式澄清、Loop 推进中进入 `grill-me` 或一次一个问题的需求 / 设计收敛。
- 用户点名 GStack、Trellis 或“四大 AI 编码框架”，要求判断 Superpowers / GSD / GStack / Trellis 如何纳入 AI Native，而不是新增一堆流程。
- 需要把 Superpowers 的 Spec -> Plan -> TDD -> Review -> Verification 工作法接入 AI Native 研发流程编排。
- 需要评估或升级 SDD / Superpowers 6.x 套件、`subagent-driven-development`、任务评审、文件化交接或 Harness 版本。
- 需要把模糊意图先收敛为关键分叉、建议答案、验收标准和任务树真相源，再交给产品专家、架构师或 AI Maker。
- 需要判断某个 AI 编码任务应参考哪类工程纪律：澄清、计划、TDD、并行 Agent、代码评审、调试、完成前验证或分支收尾。
- 需要审查外部 skill 包是否可作为方法来源、是否可复制、是否可安装或是否会引入脚本 / hooks / Git 操作风险。

## 不适用场景

- 不直接安装 Superpowers 插件，不注册 marketplace，不运行外部 hooks，不执行外部脚本。
- 不直接安装 Matt Pocock skills 全仓库、不运行 npm/package 脚本、不接入 Claude plugin 或 hooks；只在用户授权后考虑安装已审查的最小 Markdown skill。
- 不把 Superpowers 的英文默认文档路径、自动提交、Git 推送、worktree 或 subagent 流程写成本仓库默认行为。
- 不把 GStack、Trellis、`grill-me` 或任一外部 skill 写成默认依赖、默认联网、默认任务系统、默认执行授权或默认安装结果。
- 不用外部 skill 的硬门禁覆盖用户授权、仓库 `AGENTS.md`、Codex 当前工具能力、项目验证命令或 `资深架构师` 的工程判断。
- 不把外部 skill 原文当作当前项目事实、测试通过、CR 结论、Execution Grant、发布批准或合规结论。

## 读取后必须产出

- 调度结论：当前任务应参考哪些 Superpowers skill，或为什么不应参考。
- 边界结论：哪些只是方法来源，哪些需要项目本地规则、人类 owner 或架构师继续确认。
- 安全结论：是否涉及安装、脚本、联网、hooks、Git 推送、worktree、subagent 或写入范围扩大；如涉及，必须列为待授权或停止条件。
- AI Native 映射：Superpowers skill 对应 OpenSpec、Harness、GSD/CAD、Spec 模板、TDD、CR 或验证发布的哪一段。
- 轻量问询映射：`grill-me` 对应角色协作 Loop 的意图收集、自我挖掘、产品发现、设计评审或任务树真相源的哪一段。
- 框架分层映射：Superpowers、GSD、GStack、Trellis 分别对应方法纪律、上下文状态、角色链审查和仓库级记忆的哪一层；当前任务只选最小缺口层。

## 需要继续读取的 reference

- OpenSpec、Superpowers、Harness、GSD、CAD 和权限边界读 `agentic-engineering-governance.md`。
- Spec / SDD / OpenSpec 模板、AC 编号和测试映射读 `spec-template-practices.md`。
- AI 代码交付闭环、独立验证、CR 减负和知识回流读 `code-delivery-closed-loop.md`。
- 验证矩阵、CR、发布和复盘读 `verification-review-release.md`。
- 来源、许可证、下载状态和不吸收边界读 `source-map.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断 Superpowers 如何接入 AI Native | `1. 来源和下载状态`、`2. 调度矩阵`、`3. 安全边界` | 不展开全部外部 skill 原文 |
| 判断 AI 编码框架如何分层 | `2A. AI 编码框架分层映射`、`3. 安全边界`，再读 `agent-loop-engineering.md` | 不新增并列流程、不默认安装 GStack / Trellis |
| 升级 SDD / Superpowers 6.x 套件 | `1B. Superpowers v6.x / SDD 套件升级结论`、`2. 调度矩阵`、`3. 安全边界` | 不默认运行 helper、不默认启用 `.superpowers/sdd/` |
| 判断 Matt Pocock skills 是否接入 | `1A. Matt Pocock skills 审查状态`、`2. 调度矩阵`、`3. 安全边界` | 不安装全仓库、不运行 npm、不启用 Claude plugin |
| 复杂 / 模糊需求轻量问询或 Loop 推进中关键分叉未决 | `grill-me` 方法摘要，再回 `intent-to-production-loop.md` 和产品专家 | 不连续抛出多问题，不把问询过程写进正式 PRD |
| 需求澄清 / Spec 前置 | `external-superpowers/brainstorming/SKILL.md`，再回 `product-to-engineering-lifecycle.md` | 不强制保存 `docs/superpowers/specs` |
| 写实施计划 | `external-superpowers/writing-plans/SKILL.md`，再回 `spec-template-practices.md` | 不复制默认 plan 路径和提交步骤 |
| 执行计划 / 多 Agent | `external-superpowers/executing-plans/SKILL.md`、`external-superpowers/subagent-driven-development/SKILL.md`、`external-superpowers/dispatching-parallel-agents/SKILL.md`，再回 `gsd-cad-admission.md` | 不默认启动 subagent、worktree 或并行写入 |
| TDD / 测试纪律 | `external-superpowers/test-driven-development/SKILL.md`，再回 `senior-software-architect/references/testing.md` | 不用外部规则替代项目测试策略 |
| Debug / 修复验证 | `external-superpowers/systematic-debugging/SKILL.md`、`external-superpowers/verification-before-completion/SKILL.md`，再回 `verification-review-release.md` | 不把一次命令输出当完整验收 |
| 代码评审 | `external-superpowers/requesting-code-review/SKILL.md`、`external-superpowers/receiving-code-review/SKILL.md`，再回 `verification-review-release.md` 和 `资深架构师` | 不替代源码级 CR |
| 分支收尾 | `external-superpowers/finishing-a-development-branch/SKILL.md`、`external-superpowers/using-git-worktrees/SKILL.md` | 不默认 push、merge、PR 或清理 worktree |
| Skill 维护 | `external-superpowers/writing-skills/SKILL.md`，再回仓库 `AGENTS.md` 和 `skill-creator` | 不覆盖本仓库三级加载规则 |

## 1. 来源和下载状态

- 来源仓库：`https://github.com/obra/superpowers`
- 下载日期：2026-06-07
- 读取方式：GitHub API 读取 skills 目录和 README，下载 `main.zip` 到临时目录后解压审查。
- main commit：`6fd4507659784c351abbd2bc264c7162cfd386dc`
- zip SHA256：`ef1bc33f981e2eb2a3c53722eef3ee710d107beac783e97a0b280dd07e32dfa3`
- 许可证：MIT License，已保存 `external-superpowers/LICENSE`。
- 本仓库复制范围：初始导入仅复制 `skills/` 下 Markdown 资源和 LICENSE；2026-06-30 仅对 `subagent-driven-development` 做 v6.0.3 替换覆盖式升级，并纳入 `task-reviewer-prompt.md`、`implementer-prompt.md` 和三个本地 helper。
- 排除范围：除上述本地 helper 外，不复制或运行 hooks、插件 manifest、package 脚本、shell/js/ts 其他可执行文件、图片资产和安装流程；helper 只在明确进入 SDD 执行并获得用户授权时运行。

已下载的 14 个外部 skill：

- `brainstorming`
- `dispatching-parallel-agents`
- `executing-plans`
- `finishing-a-development-branch`
- `receiving-code-review`
- `requesting-code-review`
- `subagent-driven-development`
- `systematic-debugging`
- `test-driven-development`
- `using-git-worktrees`
- `using-superpowers`
- `verification-before-completion`
- `writing-plans`
- `writing-skills`

## 1B. Superpowers v6.x / SDD 套件升级结论

- 本地 SDD 核心版本：2026-06-30 本仓库对 `external-superpowers/subagent-driven-development` 做 v6.0.3 替换覆盖式升级；`v6.0.3` 发布时间为 2026-06-18，tag commit 为 `896224c4b1879920ab573417e68fd51d2ccc9072`。
- 本地审查包：`v6.0.3` GitHub archive zip SHA256 为 `45e79c9525328a9dd6653c2d01d49895eaf083cf321a4902ea71d7ba5705bbf0`。
- 上游最新核验：2026-07-01 通过 GitHub Releases API 核验 `obra/superpowers` latest release 为 `v6.1.0`，发布于 `2026-06-30T18:42:18Z`，tag commit 为 `f268f7c953744036f0fa7e9d4b73535c04e57cb8`。
- v6.1.0 取舍结论：本轮只记录上游状态，不覆盖本地 vendored SDD 核心。该版本主要压缩 `using-superpowers` bootstrap 与 harness reference、补 Codex marketplace manifest、移除 Codex SessionStart hook，并因 Gemini CLI 于 2026-06-18 EOL 而移除 Gemini CLI 支持。
- v6 关键变化：`subagent-driven-development` 把 `spec-reviewer-prompt.md` 与 `code-quality-reviewer-prompt.md` 合并为 `task-reviewer-prompt.md`，按一次 diff 读取同时给出 spec-compliance 和 quality 两类结论。
- v6 关键变化：任务交接从会话粘贴改为文件化，核心脚本包括 `task-brief`、`review-package` 和 `sdd-workspace`；`v6.0.3` 把 task brief、implementer report、review diff 和 progress ledger 放到工作区 `.superpowers/sdd/`。
- v6 关键变化：执行前增加 pre-flight plan review，先检查计划内部冲突、会被 reviewer 判为缺陷的要求和跨任务接口不一致。
- v6 关键变化：每次 dispatch 必须声明 model，并按任务风险选择合适成本层；最终再做一次 whole-branch broad review。
- 升级结论：本仓库已 vendored v6.0.3 的 `task-reviewer-prompt.md`、`implementer-prompt.md`、`task-brief`、`review-package` 和 `sdd-workspace`；其他 Superpowers skill 保持原基线，不复制 hooks、插件 manifest、package 脚本、server 或安装流程。上游 v6.1.0 暂不覆盖本地 SDD helper。
- AI Native 映射：pre-flight plan review 进入 Harness v3 准入；`task-reviewer-prompt.md` 映射为单一 Task Reviewer 角色；文件化 handoff 映射为本仓库任务文档 / review package / 验证证据；progress ledger 映射为 Goal Ledger、Harness Plan、任务文档或当前项目允许的状态文件；`task-brief`、`review-package`、`sdd-workspace` 只作为授权后的本地 helper，不等于默认安装外部 Harness。
- 停止条件：`task-brief`、`review-package` 和 `sdd-workspace` 只允许在当前任务明确进入 SDD 执行且用户授权写入本地工作区时运行；缺授权时只能使用方法规则，不创建 `.superpowers/sdd/`，不声明已启用外部 SDD 执行套件。

## 1A. Matt Pocock skills 审查状态

- 来源仓库：`https://github.com/mattpocock/skills`
- 审查日期：2026-06-28
- 读取方式：GitHub API / raw 读取仓库目录、`package.json`、LICENSE 和目标 skill；`git clone` 与 zip 下载在当前网络环境下超时，未完成全量落盘。
- 许可证：MIT License。
- 已审查最小目标：`skills/productivity/grill-me/SKILL.md` 为纯 Markdown Skill，无脚本、hooks 或依赖；`grill-me` 为唯一入口，废弃本地 `grilling`。
- 安装状态：2026-07-13 按用户授权移除旧本地 `grill-me` 和 `grilling`，从 `mattpocock/skills` `v1.1.0` 安装并本地收敛为 `grill-me`；后续更新仍走官方 skill-installer 或用户显式授权路径，但完成条件是 `scripts/validate-grill-me-install.py` 通过，未通过不得宣称完成。
- 可吸收方法：以 `grill-me` 为 canonical；复杂或模糊计划先沿设计树一次问一个问题；每问给建议答案并等待反馈；Facts 用代码库或材料自答，Decisions 才交给 owner；未达成 shared understanding 不进入执行；Loop 推进中遇到关键分叉、含糊回答、半答或连续返工时做阶段性盘问，必要时给半答案 strawman 让 owner 反驳；问询结论进入任务树、产品上下文卡、工程交接卡、验证矩阵或下一阶段输入。
- 不吸收项：不安装全仓库，不运行 npm、package scripts、Claude plugin、Trellis、hooks 或外部任务系统；不复制原文长提示；不采用 `dangerously-skip-permissions` 或任何跳过权限的默认模式。

## 2. 调度矩阵

| Superpowers skill | AI Native 位置 | 调度方式 |
| --- | --- | --- |
| `brainstorming` | Round 0、PRD-Lite、OpenSpec 前置澄清 | 吸收“先澄清目标、约束、成功标准，再进设计”的方法；产品语义仍交给 `产品架构专家`。 |
| `writing-plans` | OpenSpec / Harness / GSD 任务拆解 | 吸收小步任务、明确文件、验证命令和 TDD 步骤；完整工程计划仍交给 `资深架构师`。 |
| `executing-plans` | GSD Wave 执行节奏 | 作为批次执行和检查点参考；不替代 Execution Grant。 |
| `subagent-driven-development` | 多 Agent / GSD 编排 | 已替换为 SDD v6.0.3 vendored skill：先做 pre-flight plan review，再由 AI Maker 执行，单一 Task Reviewer 同时检查规格符合度和代码质量，交接以文件 / 任务文档 / review package / progress ledger 为状态载体；仅在当前会话有可用 subagent 工具且用户授权时运行 helper。 |
| `dispatching-parallel-agents` | 并行只读侦察或互不重叠任务 | 只用于依赖清楚、写入范围不重叠的场景；否则回到人工串行。 |
| `test-driven-development` | TDD、补测试、回归验证 | 作为红绿重构纪律参考；具体测试设计和代码实现交给 `资深架构师`。 |
| `systematic-debugging` | Bug / 生产问题前置诊断 | 映射到时间线、假设、证据和根因路径；具体排障交给 `资深架构师`。 |
| `verification-before-completion` | 完成前验证门禁 | 映射到“先运行验证、再声明完成”；AI Native 只编排证据，不能替代测试结果。 |
| `requesting-code-review` | CR 前置准备 | 映射到 Review 输入包、严重级别和独立审查；源码级 CR 仍交给 `资深架构师`。 |
| `receiving-code-review` | CR 反馈处理 | 映射到反馈分类、接受 / 拒绝 / 待确认和复核；不把外部反馈当命令。 |
| `using-git-worktrees` | 隔离开发环境 | 仅作为可选工程策略；本仓库不默认创建 worktree。 |
| `finishing-a-development-branch` | 分支收尾 / PR / merge 决策 | 只作为收尾检查清单；不默认 push、merge 或 PR。 |
| `writing-skills` | Skill 维护 | 只吸收测试、评估和渐进加载思路；本仓库以 `skill-creator` 和 `AGENTS.md` 为准。 |
| `using-superpowers` | 外部库导览 | 只用于理解 Superpowers skill system，不作为执行入口。 |
| `grill-me` | 意图收集、自我挖掘、产品发现、设计评审、任务树前置、Loop 推进中关键分叉复核 | `grill-me` 是 canonical 入口；只吸收“一次一个问题 + 给建议答案 + 等待反馈 + Facts 自查 + Decisions 等 owner + shared understanding 确认 + 模糊回答 push back + 结构化决策摘要”；正式产品结论仍交给 `产品架构专家`，工程结论仍交给 `资深架构师`。 |

## 2A. AI 编码框架分层映射

当用户把 Superpowers、GSD、GStack、Trellis 放在一起比较时，AI Native 只做分层吸收：

| 能力层 | 代表框架 | 归入角色协作 Loop | 不吸收 |
| --- | --- | --- | --- |
| 方法纪律 | Superpowers | 澄清、计划、TDD、CR、验证前置和完成前检查。 | 不复制外部 hooks、默认目录、自动 Git、强制话术。 |
| 上下文 / Spec / 状态 | GSD | 目标、Spec、Wave、Atomic Task、状态账本和恢复入口。 | 不默认创建外部规划目录，不复刻命令体系。 |
| 角色链审查 | GStack | 产品价值、UED 体验、工程方案、源码质量、QA、安全、发布多视角审查。 | 不新建虚拟团队 Skill，不替代产品专家、架构师、质量门禁或发布 owner。 |
| 仓库级记忆 | Trellis | Task Tree、Goal Ledger、状态回写、知识回流和 Finish 复盘。 | 不默认安装 npm，不创建 `.trellis/`，不替代项目已有状态载体。 |

GStack slash commands 在 AI Native 中只作为触发别名：`/office-hours` -> 产品思考，`/plan-ceo-review` -> 范围收敛，`/plan-eng-review` -> 工程评审，`/plan-design-review` -> 交互评审，`/review` -> 源码 CR，`/qa` -> QA 验证，`/ship` -> 生产交付审查 / 发布准出；开发实现仍回到 TDD、Grant、项目约规和 `资深架构师` 执行链。

结论格式保持一句话：当前任务缺哪一层、由 AI Native 读哪个 reference、回到哪个专项 Skill、哪些外部默认行为不采用。

## 3. 安全边界

- 外部 skill 原文里出现的 Git 提交、Git 推送、worktree、subagent、插件安装、默认目录和持续执行要求，只是来源语境，不是本仓库默认动作。
- 当前仓库 Git 操作仍遵守 `AGENTS.md`：除非用户明确要求，否则只做验证、审查和确认。
- 当前仓库 OpenSpec / Superpowers / Harness 生成的文档或计划默认使用中文，除非用户明确要求其他语言。
- 涉及资金、合规、安全、生产数据、不可逆操作或外部规则变化时，Superpowers 只能作为方法参考，必须保留专业确认、dry-run、回滚和审计边界。
- 如果需要安装官方 Superpowers 插件，应另开工具准入判断：核验当前 Codex 插件状态、用户授权、目标目录、联网需求、同步影响和回滚方式。
- 如果需要安装 Matt Pocock skills，只安装已审查的最小 Markdown skill：`grill-me`，并通过 Codex 官方 installer 或用户明确授权的安全路径执行；安装失败或审批被拦截时，不绕过权限边界。
- Superpowers v6 的 `task-brief`、`review-package`、`sdd-workspace` 会在运行时创建 `.superpowers/sdd/` 和 progress ledger；未获授权前不得在项目中创建目录、写 scratch 文件、运行脚本或把它们写成默认 Harness。

## 4. 调度输出模板

```text
Superpowers 调度结论：
建议参考的外部 skill：
映射到 AI Native 阶段：
当前只读 / 写入 / Git / 联网 / subagent 边界：
需要产品专家 / 架构师继续确认：
验证门禁：
停止条件：
不采用的外部默认流程：
```

## 5. 不吸收项

- 不复制 Superpowers 插件安装步骤、marketplace 注册方式、hooks、同步脚本、package 脚本或跨平台安装流程。
- 不采用外部默认 `docs/superpowers/*` 文档路径，除非用户或项目规则明确要求。
- 不采用外部默认自动提交、自动推送、自动 merge、自动 PR 或自动清理 worktree。
- 不复制外部长 prompt、示例代码、图示、作者表达或与本仓库无关的贡献流程。
- 不把外部 skill 的强制话术写入本仓库 Skill body；AI Native 只保留路由、门禁和边界。
- 不把 GStack 的角色链、Trellis 的仓库记忆或 GSD 的目录约定写成新的对外主流程；它们只作为角色协作 Loop 的内部能力层。
