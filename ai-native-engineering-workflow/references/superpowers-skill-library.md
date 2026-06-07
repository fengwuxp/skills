# Superpowers Skill Library 外部参考

本文记录 `obra/superpowers` skills 下载结果、供应链边界和 AI Native 调度方式。它是外部参考索引，不是本仓库的顶层可安装 Skill，也不是当前会话的自动执行授权。

## 使用时机

- 用户点名 Superpowers、Superpowers skills、brainstorming、writing-plans、executing-plans、subagent-driven-development、test-driven-development、requesting-code-review、verification-before-completion 等外部技能。
- 需要把 Superpowers 的 Spec -> Plan -> TDD -> Review -> Verification 工作法接入 AI Native 研发流程编排。
- 需要判断某个 AI 编码任务应参考哪类工程纪律：澄清、计划、TDD、并行 Agent、代码评审、调试、完成前验证或分支收尾。
- 需要审查外部 skill 包是否可作为方法来源、是否可复制、是否可安装或是否会引入脚本 / hooks / Git 操作风险。

## 不适用场景

- 不直接安装 Superpowers 插件，不注册 marketplace，不运行外部 hooks，不执行外部脚本。
- 不把 Superpowers 的英文默认文档路径、自动提交、Git 推送、worktree 或 subagent 流程写成本仓库默认行为。
- 不用外部 skill 的硬门禁覆盖用户授权、仓库 `AGENTS.md`、Codex 当前工具能力、项目验证命令或 `资深架构师` 的工程判断。
- 不把外部 skill 原文当作当前项目事实、测试通过、CR 结论、Execution Grant、发布批准或合规结论。

## 读取后必须产出

- 调度结论：当前任务应参考哪些 Superpowers skill，或为什么不应参考。
- 边界结论：哪些只是方法来源，哪些需要项目本地规则、人类 owner 或架构师继续确认。
- 安全结论：是否涉及安装、脚本、联网、hooks、Git 推送、worktree、subagent 或写入范围扩大；如涉及，必须列为待授权或停止条件。
- AI Native 映射：Superpowers skill 对应 OpenSpec、Harness、GSD/CAD、Spec 模板、TDD、CR 或验证发布的哪一段。

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
- 本仓库复制范围：仅复制 `skills/` 下 Markdown 资源和 LICENSE。
- 排除范围：未复制外部脚本、hooks、插件 manifest、package 脚本、shell/js/ts 可执行文件、图片资产和安装流程。

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

## 2. 调度矩阵

| Superpowers skill | AI Native 位置 | 调度方式 |
| --- | --- | --- |
| `brainstorming` | Round 0、PRD-Lite、OpenSpec 前置澄清 | 吸收“先澄清目标、约束、成功标准，再进设计”的方法；产品语义仍交给 `产品架构专家`。 |
| `writing-plans` | OpenSpec / Harness / GSD 任务拆解 | 吸收小步任务、明确文件、验证命令和 TDD 步骤；完整工程计划仍交给 `资深架构师`。 |
| `executing-plans` | GSD Wave 执行节奏 | 作为批次执行和检查点参考；不替代 Execution Grant。 |
| `subagent-driven-development` | 多 Agent / GSD 编排 | 作为“任务隔离 + 规格审查 + 质量审查”的参考；仅在当前会话有可用 subagent 工具且用户授权时使用。 |
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

## 3. 安全边界

- 外部 skill 原文里出现的 Git 提交、Git 推送、worktree、subagent、插件安装、默认目录和持续执行要求，只是来源语境，不是本仓库默认动作。
- 当前仓库 Git 操作仍遵守 `AGENTS.md`：除非用户明确要求，否则只做验证、审查和确认。
- 当前仓库 OpenSpec / Superpowers / Harness 生成的文档或计划默认使用中文，除非用户明确要求其他语言。
- 涉及资金、合规、安全、生产数据、不可逆操作或外部规则变化时，Superpowers 只能作为方法参考，必须保留专业确认、dry-run、回滚和审计边界。
- 如果需要安装官方 Superpowers 插件，应另开工具准入判断：核验当前 Codex 插件状态、用户授权、目标目录、联网需求、同步影响和回滚方式。

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
