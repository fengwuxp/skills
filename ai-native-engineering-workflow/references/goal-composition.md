# Goal 组合编排

本文定义 AI Native 流程中的 Goal 组合方式。Goal 是显式目标管理和持续推进契约，用来说明为什么持续推进、做到什么才算完成、预算 / 时间盒如何约束、何时停止、如何验证和交接；它不等于当前会话自动创建运行时 Goal，也不替代测试通过或发布批准。用户明确要求 `GSD + Goal 按任务计划推进` 时，Goal 可以挂接 Plan Grant，让范围内低风险本地任务按计划推进。

## 使用时机

- 用户要求 `GSD + Goal`、`CAD + Goal`、`Spec + Goal`、`GSD + Goal + Loop`、目标驱动推进、持续推进、长任务 Goal、目标状态、预算 / 时间盒、停止条件或跨轮交接。
- 中大型项目需要把业务目标、GSD Wave、CAD 候选、Spec 模板、质量门禁、发布复盘挂到同一目标链路。
- 多 Agent、多 owner 或多轮任务容易出现目标漂移、状态过期、验证证据断裂或交接丢失。
- 需要把产品专家的业务目标和验收种子，转换成架构师可消费的 Goal 卡、GSD Wave / Goal 映射和验证矩阵。
- 需要防止 GSD 目标漂移成“多做几个 AI 任务”或“搭一些看上去可用的 demo”，必须重新锚定到生产可用能力。
- 需要把 GSD/CAD 默认授权和阶段提交收敛到 Goal / Plan Grant / Wave / CAD Grant，减少每个任务重复审批但保留高风险硬门禁。
- GSD/CAD 默认授权收敛到 Goal / Plan Grant / Wave / CAD Grant；只有在用户明确要求按任务计划推进且 Plan Grant 字段齐备时，才允许范围内低风险任务默认推进。
- 需要把 `/goal`、`/loop`、auto mode、后台 Agent 或持续编排挂到 Goal，避免 Loop 漂移、无限循环或把执行轮数误当完成证据。

## 不适用场景

- 用户只是要求在当前 Codex 会话创建 Goal。运行时 Goal 必须由用户明确要求，并按当前工具协议处理。
- 只写普通 PRD、产品方案或 Backlog 决策，优先交给 `产品架构专家`。
- 只做架构设计、代码 Review、Bug 修复、测试或生产变更，优先交给 `资深架构师`。
- 用 Goal 替代产品确认、OpenSpec、Harness、测试证据、CR 结论或上线审批；或把没有任务计划、写入范围、验证命令和停止条件的 Goal 当作 Plan Grant。

## 读取后必须产出

- 一张 Goal 卡：Goal ID、目标、owner、参与方、成功标准、非目标、范围、预算 / 时间盒、状态、停止条件、验证证据和交接要求。
- 一份组合判断：当前适合 `GSD + Goal`、`CAD + Goal`、`Spec + Goal`、`CR/发布 + Goal` 还是 `产品到工程 + Goal`。
- 若涉及持续编排，一份 `GSD + Goal + Loop` 判断：Loop ID、状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测、停止条件和交接物。
- 一份 Goal 状态结论：`Draft / Ready / Active / Blocked / Verified / Closed / Superseded` 之一，并说明证据。
- 一份 Goal Ledger 更新：最近证据、变化假设、开放风险、提交切片、下一 owner、下一动作和复盘回流位置。
- 明确说明 Goal 不会自动创建运行时 Goal，不会自动扩大写入范围、提交权限或 Codex 替我审批范围；GSD 规划必须给出提交切片，实际 `git add` / `git commit` 只有在用户明确授权 Git 策略且 Plan Grant 字段齐备时执行。

## 需要继续读取的 reference

- 产品上下文、PRD-Lite 和产品专家交接读 `product-to-engineering-lifecycle.md`。
- OpenSpec、Superpowers、Harness、GSD、CAD 和权限边界读 `agentic-engineering-governance.md`。
- Agent Loop、`/goal`、`/loop`、auto mode、后台 Agent 和循环停止条件读 `agent-loop-engineering.md`。
- GSD Round 0、Wave/Atomic Task、CAD 候选缺口和 Execution Grant 缺口读 `gsd-cad-admission.md`。
- Spec / SDD / OpenSpec 模板、AC 编号、测试映射和漂移检查读 `spec-template-practices.md`。
- AI 代码交付闭环、独立验证、CR 减负、知识回流和指标读 `code-delivery-closed-loop.md`。
- 验证矩阵、CR、发布和复盘读 `verification-review-release.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 做 `GSD + Goal` | `1. Goal 边界`、`3. GSD + Goal`，再读 `gsd-cad-admission.md` | 不展开 CAD 执行细则 |
| 做 `GSD + Goal + Loop` | `1. Goal 边界`、`3B. GSD + Goal + Loop`，再读 `agent-loop-engineering.md` | 不把 Loop 当授权或完成证据 |
| 做 `CAD + Goal` | `1. Goal 边界`、`4. CAD + Goal`，再读 `agentic-engineering-governance.md` | 不把 Goal 当 Execution Grant |
| 将默认授权挂到 Goal | `1. Goal 边界`、`3. GSD + Goal`、`4. CAD + Goal`，再读 `gsd-cad-admission.md` | 不把 Goal 状态当授权 |
| 按任务计划自动推进或阶段提交 | `1. Goal 边界`、`3A. Plan Grant`，再读 `gsd-cad-admission.md` | 不逐任务索要 Execution Grant |
| 做 `Spec + Goal` | `1. Goal 边界`、`5. Spec + Goal`，再读 `spec-template-practices.md` | 不重复写完整 Spec 模板 |
| 做 CR / 发布 Goal 验证 | `6. CR/发布 + Goal`，再读 `verification-review-release.md` | 不把测试通过当 Goal 自动关闭 |
| 长任务状态交接 | `2. Goal 卡`、`7. 状态和 Ledger` | 不用长报告替代状态更新 |

## 1. Goal 边界

Goal 回答：为什么持续做、做到什么叫完成、预算 / 时间盒如何约束、何时停止、如何交接。

在 GSD 场景中，Goal 的完成线必须是生产可用能力，而不是 AI 产物数量、模拟模块数量或表面可运行效果。Goal 必须能映射到真实业务入口、生产边界、验收种子、验证证据、发布/回滚条件和责任 owner；否则只能停在 `Draft` 或 `Blocked`，不能进入 GSD Wave 或 CAD 候选。

相邻概念的边界：

| 概念 | 回答的问题 | 不能替代 |
| --- | --- | --- |
| Goal | 目标、成功标准、状态、预算、停止和交接。 | 测试、CR、发布批准。 |
| GSD | 分几波做、先做什么、谁接下一波。 | 业务目标和成功标准。 |
| CAD | 当前原子任务能否受控自动执行。 | 整个项目自动驾驶。 |
| Harness | 谁做、按什么顺序做、能改哪里、怎么验证、怎么交接。 | 产品确认和上线审批。 |
| Plan Grant | 在已确认 Goal 任务计划内默认允许哪些低风险本地任务推进，以及 Git 是否仅建议或验证后提交。 | Git push、PR、联网、生产、密钥、部署、不可逆操作和高风险业务确认。 |
| Loop | 每轮如何读取状态、执行动作、吸收反馈、验证和停止。 | Goal、Harness、授权、测试、CR、上线审批。 |
| Execution Grant | 单个 CAD 任务或高风险动作实际允许做什么。 | 长期目标或跨轮授权。 |

原则：

- Goal 可以约束 GSD Wave 和 CAD 候选，但不能单独授予提交、联网、部署或生产操作权限。
- Goal 可以挂接 Plan Grant、Wave Grant 或 CAD Grant 来减少重复审批；Plan Grant 必须单独写清任务计划、写入范围、验证命令、Git 策略、默认审批通道和显式确认边界。
- Goal 可以挂接 Loop，但 Loop 必须有状态载体、反馈源、验证者、预算 / 最大轮次、无进展检测和停止条件；Goal Active 不代表 Loop 可以无限运行。
- GSD 规划必须给出阶段/任务提交切片；默认只建议提交，只有用户明确授权 `commit_after_verified_task` 时才在验证通过后执行本地 commit。
- Goal 状态必须有证据，不能只靠“感觉已完成”。
- Goal 的成功标准应能映射到验收种子、AC、测试、CR 检查点、发布监控或人工确认方。
- Goal 过大时先拆父子 Goal；子 Goal 必须继承父 Goal 的目标意图、非目标、风险边界和停止条件。

## 2. Goal 卡

最小 Goal 卡：

```text
Goal ID:
状态: Draft / Ready / Active / Blocked / Verified / Closed / Superseded
目标:
业务意图:
生产可用能力:
Owner:
参与方:
来源材料:
成功标准:
非目标:
范围:
预算 / 时间盒 / 上下文预算:
验收种子 / AC:
验证矩阵:
停止条件:
交接要求:
最近证据:
开放风险:
下一复核点:
```

写作要求：

- 先写 3-5 行摘要：当前目标、状态、能否继续、下一 owner 和阻塞点。
- 成功标准要可验证，不写“提升体验”“尽快完成”这类不可判断目标。
- 生产可用能力要说明真实业务入口、生产边界、上线/回滚要求或人工确认方，不用“demo 可跑”“mock 已通”替代。
- 预算可以是时间盒、轮次、上下文预算、验证成本或风险上限；不要用预算掩盖范围不清。
- 状态变化必须带证据，例如测试、CR、产品确认、人工审批、发布监控或明确的阻塞输入。

## 3. GSD + Goal

`GSD + Goal` 是中大型项目的默认目标组合：GSD 管 Wave 和任务顺序，Goal 管目标、成功标准、状态、预算、停止条件、验证证据和交接节奏。

输出结构：

```text
父 Goal:
GSD Round 0 目标:
Wave 0 Goal: 只读侦察 / 规格补齐 / 风险确认
Wave 1 Goal: 公共契约 / 领域模型 / 验证底座
Wave 2 Goal: 互不重叠的实现任务
Wave 3 Goal: 集成验证 / CR / 发布准备
每个 Wave 的成功标准:
每个 Wave 的停止条件:
每个 Wave 的验证证据:
每个 Wave 的授权策略: 只读 / 默认低风险授权 / Plan Grant / Wave Grant / 显式确认
每个 Wave 的提交切片: summary_only / commit_after_verified_task / explicit_confirm
下一 Wave 准入:
```

门禁：

- Round 0 未补齐业务目标、对象、风险、验收种子和 owner 时，不展开多 Wave 计划。
- 未说明生产可用能力、真实业务入口、生产边界和发布/回滚要求时，不展开多 Wave 计划。
- 每个 Wave 只允许有一个主目标；混合目标拆成子 Goal。
- Wave 完成不是“文件改完”，而是成功标准、验证证据和交接要求已满足。
- Wave 之间必须记录变更假设、残余风险和下一 owner，防止跨轮漂移。
- 当用户明确要求按任务计划推进，且每个 Wave / Task 已列明写入范围、验证命令、停止条件和显式确认边界时，输出 `Plan Grant: Active`，范围内低风险本地任务直接推进。
- 每个 Wave / Task 完成验证后都必须输出建议提交单元、涉及文件、验证证据和建议 commit message；若 Git 策略为 `commit_after_verified_task`，还要在提交前检查工作区状态并确认没有混入用户已有改动。
- Wave Grant 只能覆盖该 Wave 内互不冲突、低风险、可验证、可回滚的任务；公共契约、Git、联网、依赖安装、生产、密钥、部署、不可逆操作和高风险业务必须显式确认。

### 3A. Plan Grant

Plan Grant 用来把 `GSD + Goal` 从目标管理变成可推进的低风险执行边界，避免每个任务都被 `Execution Grant：xxx` 阻塞。

最小结构：

```text
Plan Grant: Draft / Active / Suspended
适用 Goal:
任务计划:
允许写入:
允许验证:
Git 策略:
提交切片:
默认推进:
显式确认:
停止条件:
审计交接:
```

`Active` 条件：

- 用户明确要求 `GSD + Goal 按任务计划推进`、`按任务计划自动推进`、`不希望每个任务手动授权` 或等价表达。
- Goal 为 `Ready / Active`，任务计划含 Wave / Task ID、顺序、owner、写入范围、验证命令和停止条件。
- 默认推进仅限当前工作区低风险本地读写、测试、lint、文档更新、Skill 更新、小步业务代码修改和状态/Ledger 回写。
- Git 策略默认为 `summary_only`；只有用户明确授权 `commit_after_verified_task`，且每个提交对应已验证 Wave / Task ID、不混入用户已有改动时，才执行本地 `git add` / `git commit`。
- Git push、PR、联网、依赖安装、生产、密钥、部署、数据库迁移、真实支付/资金、不可逆操作、高风险权限/租户/审计/合规决策仍显式确认。
- 验证失败、范围漂移、用户改动冲突、工具要求额外审批或风险升级时，Plan Grant 立即转 `Suspended` 并交还用户。

### 3B. GSD + Goal + Loop

`GSD + Goal + Loop` 用于持续推进但必须可停止的中大型任务。输出时把三者分清：

```text
Goal: 为什么做、做到什么算完成
GSD: 分几波做、每波谁接、怎么交接
Loop: 每轮读什么状态、做什么动作、读什么反馈、谁验证、何时停止
```

最小输出：

```text
Loop ID:
关联 Goal:
所属 Wave / Task:
状态载体:
反馈源:
验证者:
预算 / 最大轮次:
无进展检测:
停止条件:
授权策略:
Ledger 更新:
```

红线：

- Loop 不得扩大 Goal 范围、GSD Wave 写入范围或 Plan Grant 授权范围。
- `/goal`、`/loop`、auto mode 和后台 Agent 只能作为运行方式，不能替代成功标准、验证证据、CR 或上线审批。
- Loop 完成只代表某轮循环达到停止条件；Goal 是否 Verified / Closed 仍要看成功标准和交接回流是否满足。

## 4. CAD + Goal

`CAD + Goal` 只用于已经被拆成原子任务的候选。Goal 负责说明该原子任务服务哪个目标、成功标准和停止条件；若 Plan Grant 覆盖该任务，CAD 可消费 Plan Grant 作为低风险本地动作授权；不覆盖时仍按 CAD Grant / Execution Grant 处理。

准入判断：

```text
关联 Goal:
Goal 状态是否 Ready / Active:
原子任务边界:
写入范围:
验证命令:
Execution Grant:
Plan Grant:
授权策略:
Codex 替我审批:
停止条件:
失败恢复:
```

红线：

- Goal Ready 不代表 CAD 可执行。
- 父 Goal Active 不代表所有子任务都被 Plan Grant / CAD Grant 覆盖。
- Codex 替我审批只可作为当前 CAD Grant 范围内低风险工具审批通道，不代表 Git、联网、生产或高风险动作自动放行。
- CAD 执行失败时，更新 Goal Ledger 的阻塞证据和下一 owner，不把失败隐藏成“继续推进”。

## 5. Spec + Goal

`Spec + Goal` 用 Goal 防止 Spec 漂移。Spec 解释可接受实现空间，Goal 解释本轮为什么做、做到什么叫完成、如何判断成功。

映射关系：

- Goal 目标 -> Spec 摘要和业务意图。
- Goal 成功标准 -> AC、测试映射、CR 检查点和发布监控。
- Goal 非目标 -> Spec 范围外、禁止事项和不做清单。
- Goal 停止条件 -> Harness 停止条件、spec-lint、AC 覆盖、漂移检查和人工升级。
- Goal 证据 -> 验证矩阵和复盘回流。

如果 Spec 已经很厚但 Goal 仍然不清，优先回到 Goal 卡；如果 Goal 清楚但实现空间不清，继续补 Spec 模板和架构师系分。

## 6. CR/发布 + Goal

CR 和发布阶段要验证 Goal 是否真的达成，而不是只验证代码是否合并。

CR 前检查：

- 这次变更服务哪个 Goal 和哪条成功标准。
- 代码入口、影响模块、源码锚点、AC 和验证证据是否能回链 Goal。
- 未满足的 Goal 成功标准是否进入残余风险、人工确认或下一子 Goal。
- 是否有 Goal 范围外变更、隐性扩张或未授权写入。

发布前检查：

```text
Goal ID:
成功标准完成情况:
已执行验证:
未执行验证和原因:
人工确认方:
灰度 / 监控:
回滚 / 恢复:
是否可 Verified / Closed:
残余风险:
```

Goal `Verified` 只代表证据满足成功标准；Goal `Closed` 还需要完成交接、知识回流和残余风险处理。

## 7. 状态和 Ledger

状态机：

```text
Draft -> Ready -> Active -> Verified -> Closed
Active -> Blocked
Active -> Superseded
Blocked -> Active
Verified -> Closed
```

状态定义：

- `Draft`：目标尚未清楚，不能执行。
- `Ready`：目标、成功标准、非目标、owner、预算、停止条件和验证方式已明确。
- `Active`：已进入 GSD Wave、Spec、CAD 候选或验证闭环。
- `Blocked`：出现明确阻塞，需要用户、产品、架构、权限、验证环境或专业确认输入。
- `Verified`：成功标准已有可复核证据。
- `Closed`：验证、交接、知识回流和残余风险处理完成。
- `Superseded`：目标被新的目标替代，必须说明替代原因和迁移关系。

Goal Ledger 最小更新：

```text
Goal ID:
当前状态:
最近证据:
变化假设:
开放风险:
下一 owner:
下一动作:
复盘 / 知识回流位置:
```

触发更新：

- GSD Wave 进入或结束。
- Plan Grant / CAD Grant 消耗、失败或回退。
- Spec / AC / 验证矩阵发生实质变化。
- 测试、CR、发布或人工确认失败。
- 交接 owner 变化。
- 复盘发现目标、范围或成功标准需要修订。

## 8. 反模式

- Goal 只是口号，没有成功标准、非目标、预算、停止条件或 owner。
- Goal 只追求 AI 任务推进数量、模拟模块数量或 demo 可运行，没有生产可用能力锚点。
- `GSD + Goal` 只写父目标，不给 Wave Goal 和验证证据。
- Goal 状态长期停在 Active，没有 Ledger 更新。
- 用 Goal 扩大写入范围、跳过 Plan Grant / CAD Grant、跳过测试或跳过 CR。
- 用 Goal、Wave 状态或 Codex 替我审批扩大默认授权范围，跳过 Git/联网/生产/密钥/部署/不可逆操作的显式确认。
- 把 “测试通过” 直接等同于 Goal Closed。
- 目标过大，无法在一次 Wave、一次 CR 或一次发布中判断完成。
- Goal 与 Spec、Harness、验证矩阵、发布复盘各写一套，导致目标漂移。
