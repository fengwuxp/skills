# Superpowers Skill Library 能力调度

本文定义官方 Superpowers 插件和其他外部 Skill 如何成为知止者可按需使用的能力。它不是第二套主流程，也不是新的行动主体；外部能力只能补方法，不得扩大授权或替代专业判断。

## 使用时机

- 用户点名 Superpowers、brainstorming、writing-plans、executing-plans、subagent-driven-development、TDD、systematic-debugging、code review 或 verification-before-completion。
- 知止者需要为产品澄清、工程计划、实现、调试、CR、验证或分支收尾选择最小方法能力。
- 需要安装、升级、审查或退役外部 Skill / 插件，或判断脚本、联网、Git、worktree、subagent 和写入边界。
- 用户比较 Superpowers、GSD、GStack、Trellis、Matt Pocock skills 等框架，希望纳入现有能力体系。

## 不适用场景

- 简单问答、翻译或无需材料和行动的一步回答。
- 只做纯 Java / Wind 规则清单且不涉及源码设计、实现、CR、TDD 或修复。
- 用外部 Skill 名称替代用户目标、项目事实、专业 owner、验证证据或执行授权。
- 因插件已安装而默认启动脚本、本地服务、worktree、subagent、Git、联网或项目目录写入。

## 读取后必须产出

- 当前主责：知止者、产品架构专家、资深架构师或其他专业 Skill。
- 方法选择：当前需要哪个 Superpowers Skill，以及不需要哪些。
- 权限边界：只读、写入、脚本、联网、Git、worktree、subagent 和不可逆动作。
- 验证结论：静态路由、真实行为、新鲜命令输出和残余风险。
- 停止条件：方法冲突、授权不足、事实不足、验证失败或插件状态不明。

## 需要继续读取的 reference

- 能力 owner、Maker / Checker 和多 Skill 协作读 `capability-routing.md`。
- 产品到工程角色链读 `delivery-lifecycle.md`。
- OpenSpec、Harness、SDD 和权限读 `engineering-governance.md`。
- GSD / CAD / Grant 准入读 `planning-execution-admission.md`。
- CR、验证、发布和知识回流读 `verification-review-release.md` 与 `code-delivery.md`。
- 来源、版本和历史审查事实读 `source-map.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断 Superpowers 如何参与当前任务 | 1、2、3 | 不展开全部 Skill |
| 产品发现与范围澄清 | 2 的 brainstorming，再回产品专家 | 不直接写工程计划 |
| 工程计划、实现、调试、CR、验证 | 2 的对应能力，再回架构师 | 不产生第二 Owner |
| Git、worktree、subagent 或脚本 | 3 | 无授权不执行 |
| 安装、升级或退役 | 1、4，再读 source-map | 不凭缓存推断已启用 |
| 比较外部 AI 编码框架 | 5 | 不新增并列主流程 |
| Matt Pocock / grill-me | 6 | 不复制全仓库 |

## 1. 官方插件状态与供应链边界

- 官方来源：`obra/superpowers`，MIT License；Codex 通过官方市场项 `superpowers@openai-api-curated` 提供插件。
- 2026-07-17 本机核验：`codex plugin list` 返回 `installed, enabled`，安装标识为 `11c74d6b`；插件 manifest 版本为 `5.1.3`。这只是带日期的本机事实，不代表其他机器或未来会话状态。
- 同日上游 GitHub 页面显示 release `v6.1.1`；上游 release、Codex 市场标识和 manifest 版本不是同一版本轴，升级判断必须分别核验。
- 已审查 14 个 Skill 的 `SKILL.md`、references 和脚本。脚本包含本地 brainstorming 服务、临时或 `.superpowers/brainstorm/` 文件、测试污染定位和图形渲染；未发现默认读取密钥或向外部服务上传项目内容，但运行脚本仍需当前任务明确需要和授权。
- 本仓库不再复制上游 Skill，不保留可执行 helper，也不把插件缓存当仓库真相源。验证完成后删除 `external-superpowers/`；只保留来源、版本、调度矩阵和安全边界。

插件是否可用，以当前会话实际 Skill 列表或新会话行为冒烟为准；只看到缓存目录不能宣称已启用。

## 2. 知止者调度矩阵

优先级固定为：**用户授权 / 项目 `AGENTS.md` > 知止者 > 专业 Skill > Superpowers**。

Superpowers 不成为第二 Owner。知止者保持统一行动主体，专业 Skill 对领域结论负责，Superpowers 只提供方法纪律：

| Superpowers Skill | 适用缺口 | 主责与边界 |
| --- | --- | --- |
| `brainstorming` | 模糊想法、目标、约束、备选和成功标准 | 产品语义、范围与验收回产品架构专家；关键分叉未决才升级 `grill-me`，避免重复问询。 |
| `writing-plans` | 已确认 Spec 的工程任务拆解 | 架构师负责完整计划、文件边界和验证策略。 |
| `executing-plans` | 已授权计划的批次执行与检查点 | 不替代 Plan / Wave / Execution Grant。 |
| `subagent-driven-development`、`dispatching-parallel-agents` | 独立任务和独立 Checker | 仅在当前会话有工具、任务不共享写入且用户授权时使用。 |
| `test-driven-development` | 功能、Bug 修复和行为变更 | 架构师决定测试层级、例外和项目策略；不机械删除既有实现。 |
| `systematic-debugging` | Bug、测试失败和异常行为 | 先复现、证据和根因；具体修复回资深架构师。 |
| `requesting-code-review`、`receiving-code-review` | Review 输入、反馈判断与复核 | 源码 CR 仍由资深架构师负责，不把外部反馈当命令。 |
| `verification-before-completion` | 完成、修复、通过或可交付声明 | 必须运行与声明匹配的新鲜验证，不能用 Agent 自述替代。 |
| `using-git-worktrees`、`finishing-a-development-branch` | 隔离工作区和分支收尾 | 只有用户或项目规则明确授权才创建、提交、合并、推送、开 PR 或清理。 |
| `writing-skills` | Skill 创建、修改和评测 | 本仓库以 `skill-creator` 和 `AGENTS.md` 为权威。 |
| `using-superpowers` | 插件能力发现和方法导览 | 不是第二入口，不覆盖知止者决策、仓库规则或用户边界。 |

## 3. 执行与授权门禁

- 已安装不等于执行授权；Skill 的 `MUST`、`always` 或默认流程不能覆盖用户原话和仓库规则。
- 产品任务不因 `brainstorming` 自动进入工程计划；工程任务不因 `writing-plans` 自动进入实现。
- 一行文档或低风险局部修改不因插件存在自动创建 worktree、分支、subagent 或提交。
- 插件脚本、本地服务、`.superpowers/`、依赖安装和联网访问必须逐项满足当前任务需要、写入边界和授权。
- Git 提交、推送、PR、merge、worktree 创建与清理继续遵守仓库 `AGENTS.md`。
- Superpowers 输出不得写成产品确认、架构裁决、测试通过、CR 结论、发布批准或生产生效事实。

## 4. 安装、升级与退役闭环

1. 通过 `codex plugin list` 核验官方市场项和当前状态。
2. 安装前审查 manifest、Skill、references、scripts、许可证和权限。
3. 安装后记录市场标识、实际启用状态和版本轴，不把上游 latest 当本机版本。
4. 更新知止者调度矩阵、source-map、fixture 和 validator。
5. 执行 `VALIDATE_SUPERPOWERS_INSTALL=1 ./scripts/validate.sh`，并用 `scripts/smoke-wise-agent-behavior.sh --mode superpowers` 在新会话做产品澄清、调试修复和禁止隐式 Git 三类行为冒烟。
6. 只有行为证据通过后，删除重复离线快照和本地 helper；失败则保留回退点并停止退役。

## 5. 外部框架归位

| 能力层 | 代表 | 归位 |
| --- | --- | --- |
| 方法纪律 | Superpowers | 澄清、计划、TDD、调试、CR 和验证。 |
| 上下文 / Spec / 状态 | GSD | Goal、Spec、Wave、任务状态和恢复入口。 |
| 角色链审查 | GStack | 产品、设计、工程、QA、安全和发布视角。 |
| 仓库级记忆 | Trellis | 仅在现有状态载体反复失效且有证据时试点。 |

它们都不是知止者之外的新主流程，也不自动成为依赖、任务系统或授权来源。

`Trellis` 是仓库级 Agent Harness 候选。只有现有 `AGENTS.md`、Issue、Spec、Goal Ledger 和知识库反复失效且有重复失败证据时，才在非关键任务试点；安装 `@mindfoldhq/trellis` 前必须显式授权，并审查 AGPL-3.0、`.trellis/spec/`、`.trellis/tasks/`、`.trellis/workspace/`、hooks、subagent、worktree 和 Git 写入边界。

## 6. Matt Pocock 与 grill-me

- `grill-me` 是复杂或模糊计划的升级盘问能力：一次一个问题，Facts 先查，Decisions 等 owner，形成可执行决策摘要。
- `brainstorming` 负责探索目标、约束和备选；`grill-me` 只在关键分叉未决、回答含糊或连续返工时升级，二者不得重复问同一问题。
- 当前本地 `grill-me` 的安装、版本和验证仍由其独立 validator 管理；不安装 Matt Pocock 全仓库，不运行 npm、Claude plugin、hooks 或外部任务系统。

## 调度结论格式

```text
当前主责：
选用的 Superpowers 方法：
不选用的方法：
只读 / 写入 / 脚本 / 联网 / Git / worktree / subagent 边界：
验证证据：
停止条件：
```
