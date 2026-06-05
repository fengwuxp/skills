# PRD 与系分合议预审

本文定义 AI Native 流程中的 PRD / 系分预审门禁。它吸收 MAGI 三角色与多视角虚拟评审的可迁移方法，但不要求真实启动多个 Agent，也不替代正式产品评审、架构评审、代码 CR 或专业审批。

## 使用时机

- 用户要求对 PRD、PRD-Lite、OpenSpec 输入、系统分析设计、系分、详细设计、Harness Plan 或 GSD 任务包做预审、合议评审、多视角评审、MAGI 三角色评审、A2A 虚拟评审或 IPD 式互审。
- PRD 或系分已经由 AI 生成，担心只是写得快，但产品判断、工程判断、验收和风险没有被充分反向拷问。
- 正式评审前希望先暴露低级问题、分歧、风险和待确认项，避免评审会变成补文档现场。
- 产品专家与架构师交接前，需要判断 PRD 是否足以进入 OpenSpec，或系分是否足以进入 Harness/GSD/CAD 候选。
- 多角色意见很多，但缺少 owner 决策、接受/拒绝/待定理由和后续动作。

## 不适用场景

- 只写一份普通 PRD 或产品方案：优先交给 `产品架构专家`。
- 只写或评审完整系统设计正文：优先交给 `资深架构师` 的系统分析设计 reference。
- 只做源码级 CR、Bug 修复、测试实现或生产变更：优先交给 `资深架构师`。
- 不把虚拟评审当作正式 IPD、真实客户证据、商业取舍、合规责任或上线批准。
- 不能替代产品 owner、架构 owner、正式评审、测试通过或 Execution Grant。
- 不复制外部多 Agent 平台、CrewAI/Codex/Claude 互调方式、Computer Use 做法、长 prompt、示例正文或作者表达。

## 读取后必须产出

- 当前是否需要 PRD / 系分合议预审，以及触发原因。
- 评审对象、阶段、来源材料、owner、停止条件和下一步路由。
- 三角色分工：流程控制位、主笔 / 决策 owner、挑战者位。
- 三个硬任务结果：`review_task`、`evaluation_task`、`reporting_task`。
- 决策日志：每条关键反馈必须落为 `ACCEPT`、`REJECT` 或 `PENDING`，并说明理由、动作、owner 和验证方式。
- 准出判断：能否进入 PRD 修订、OpenSpec、系分修订、Harness/GSD、CAD 候选或必须回到 Round 0。

## 需要继续读取的 reference

- 产品到工程成熟度、PRD-Lite 和交接包读 `product-to-engineering-lifecycle.md`。
- OpenSpec、Harness、GSD/CAD 和 Agent 权限边界读 `agentic-engineering-governance.md`。
- 验证矩阵、CR、发布和复盘读 `verification-review-release.md`。
- PRD 正文、产品合议细节和产品质量门禁回到 `product-architecture-expert`。
- 系统设计正文、架构质量、测试和生产风险回到 `senior-software-architect`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| PRD 预审 | `1. 三角色壳`、`2. 三个硬任务`、`3. PRD 预审门禁` | 不重写完整 PRD |
| 系分预审 | `1. 三角色壳`、`2. 三个硬任务`、`4. 系分预审门禁` | 不替架构师写完整设计 |
| PRD 到系分交接 | `3. PRD 预审门禁`、`5. 双向追踪` | 不直接开 CAD |
| 系分到 Harness/GSD | `4. 系分预审门禁`、`6. 准出与停止` | 不写 Execution Grant |
| 多意见收束 | `2. 三个硬任务`、`7. 输出格式` | 不输出一堆无主建议 |

## 1. 三角色壳

MAGI 三角色在本技能中不是固定人设，而是一个轻量协作壳：

| 工作位 | 职责 | 不做什么 |
| --- | --- | --- |
| 流程控制位 | 判断是否进入预审，限定评审对象、阶段、输入材料、证据锚点、停止条件和准出路径。 | 不替产品 owner 或架构 owner 拍板。 |
| 主笔 / 决策 owner | 对反馈做 `ACCEPT`、`REJECT`、`PENDING` 决策，说明理由、动作、owner 和进入哪个交付物。 | 不机械采纳所有建议，不把 AI 共识写成已确认事实。 |
| 挑战者位 | 从产品、市场、交付、技术、QA、UX、安全、SRE、数据和运维等视角挑刺。 | 不只给泛泛建议；每条意见必须引用源材料位置或明确“缺少来源”。 |

角色视角按评审对象裁剪：

- PRD 预审：优先选产品价值、客户/市场、交付运营、技术可行性、QA 验收、UX/服务体验。
- 系分预审：优先选需求追踪、架构边界、数据一致性、安全权限、测试验证、发布运维。

## 2. 三个硬任务

### review_task

挑战者位逐条挑刺，但每条意见必须有锚点：

- 引用 PRD / 系分原文、章节、条款、图、表、验收种子、OpenSpec 条款或源码 / 测试证据。
- 没有锚点时，必须标成“源材料缺失”，不能包装成事实。
- 每条意见说明影响：产品判断、客户现场、工程边界、状态一致性、安全权限、异常路径、测试、发布或运维。

### evaluation_task

主笔 / 决策 owner 对每条反馈做决策：

- `ACCEPT`：本轮必须改，写清改哪个交付物、改什么、谁负责、怎么验证。
- `REJECT`：明确拒绝理由，例如偏离目标、拉大 MVP、证据不足、成本过高或不属本期。
- `PENDING`：需要用户、业务 owner、法务/合规、架构 owner、QA、SRE 或外部方确认；写清未确认前的默认处理。

### reporting_task

报告只保留四块，不写成“各方一致认为”：

- 结论：当前能否进入下一阶段。
- 接受项：本轮必须修改或补充的内容。
- 分歧项：未达成一致、需要 owner 判断的取舍。
- 风险清单：影响评审、研发、测试、发布或专业确认的风险。

## 3. PRD 预审门禁

PRD 预审的目标不是润色文档，而是判断它能否作为工程输入。

重点检查：

- 问题、目标、非目标、成功指标和失败成本是否清楚。
- 用户、主体、业务 owner、验收方和风险承担方是否混用。
- 核心对象、状态、流程、规则、权限、数据和运营闭环是否支撑主链路。
- 验收种子是否覆盖正常、边界、异常、人工兜底、数据和风险路径。
- AI 原型、Demo 或页面说明是否被误写成已确认业务事实。
- 产品取舍是否有 `ACCEPT` / `REJECT` / `PENDING` 决策日志，而不是无主建议。

正式 PRD 或产品合议评审报告可回到 `产品架构专家`，并按需运行：

```bash
product-architecture-expert/scripts/check_product_deliverable.py --kind prd --file <PRD.md>
product-architecture-expert/scripts/check_product_deliverable.py --kind product-review --file <评审报告.md>
```

## 4. 系分预审门禁

系分预审的目标不是替架构师写方案，而是判断它能否进入 Harness/GSD/CAD 编排。

重点检查：

- 是否能从 PRD / OpenSpec 条款追踪到模块、接口、数据、状态、流程、测试和发布。
- 系统边界、数据边界、安全边界和外部依赖是否明确。
- 核心设计是否覆盖同步 / 异步、事务、一致性、幂等、补偿、并发写入和失败恢复。
- 接口契约、数据模型、状态机、错误码、权限和审计是否可实现、可测试、可演进。
- 测试设计是否覆盖单元、契约、集成、回归、数据校验和人工验收。
- 发布、灰度、回滚、监控、告警、Runbook 和残余风险是否能支撑上线评审。

正式系分或架构方案回到 `资深架构师`，并按需运行：

```bash
senior-software-architect/scripts/check_architecture_deliverable.py --kind system-design --file <系分.md>
senior-software-architect/scripts/check_architecture_deliverable.py --kind architecture-plan --file <技术方案.md>
```

## 5. 双向追踪

PRD 与系分预审必须形成双向追踪，而不是两个孤立文档：

```text
PRD 条款 / 验收种子：
OpenSpec / 系分条款：
模块 / 接口 / 数据 / 状态：
测试 / 验证证据：
偏差：
决策：ACCEPT / REJECT / PENDING
owner：
下一步：
```

追踪规则：

- PRD 中无验收种子的能力，不应直接进入 CAD 候选。
- 系分中无法回指业务目标、规则或质量属性的模块，先列入分歧或待确认。
- 只有图、Demo 或 AI 总结，没有对象、规则、验收和风险时，回退到产品上下文包或 Round 0。
- 设计-代码对齐、源码锚点和实现偏差继续读取 `code-understanding-tools.md` 与 `verification-review-release.md`。

## 6. 准出与停止

预审结论只能给准出建议，不给执行授权。

| 结论 | 含义 | 下一步 |
| --- | --- | --- |
| 可进入 PRD 修订 | PRD 问题可由产品专家补齐。 | 路由 `产品架构专家`。 |
| 可进入 OpenSpec / 系分 | 产品上下文足以让架构师承接。 | 路由 `资深架构师`。 |
| 可进入 Harness/GSD 候选 | 系分和验证证据足以拆任务，但仍需 Harness 细化。 | 读取 `agentic-engineering-governance.md` 与 `gsd-cad-admission.md`。 |
| 仅 CAD 候选缺口 | 原子任务边界可能成立，但缺 Execution Grant、写入范围或验证命令。 | 只列缺口，不执行。 |
| 必须回退 Round 0 | 缺目标、证据、owner、边界、验收、风险或专业确认。 | 补材料后再评审。 |

## 7. 输出格式

```text
PRD / 系分合议预审结论

评审对象：
当前阶段：
触发原因：
来源材料：
决策 owner：
停止条件：

三角色分工：
- 流程控制位：
- 主笔 / 决策 owner：
- 挑战者位：

review_task：
- 锚点：
- 问题：
- 影响：
- 建议：

evaluation_task：
- 决策：ACCEPT / REJECT / PENDING
- 理由：
- 动作：
- owner：
- 验证方式：

reporting_task：
- 结论：
- 接受项：
- 分歧项：
- 风险清单：
- 下一步路由：
```

## 8. 反模式

- 把多角色评审写成热闹的角色扮演，但没有锚点、决策 owner 和后续动作。
- 让 AI 只润色 PRD，而不质疑目标、证据、对象、规则、验收和风险。
- 把所有建议都接受，导致 MVP 失焦、系分膨胀或 Harness 失控。
- 把虚拟预审当作正式评审会、客户证据、合规确认、架构 owner 批准或 Execution Grant。
- PRD 评审不回到产品专家，系分评审不回到架构师，本技能越界写完整正文或直接授权执行。
