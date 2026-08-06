# 跨上下文交接与同级权威会商

本文是 `Continue / Branch / Worker / Checker` 正名、临时上下文分叉、出站交接、返回对账和同级权威契约会商的唯一权威来源。它只规定上下文、契约问题和证据如何往返，不新增顶层 Skill、状态类型、控制机制、外部协议依赖或执行授权。

## 使用时机

- 下一会话需要判断是继续既有任务，还是把独立问题放入干净上下文取证后回传。
- 主线 Goal 仍需保持稳定，但原型、真实页面、基准、源码核验或受控调研适合隔离处理。
- 需要跨 Agent 或跨工具交接，且能够写清下一上下文的目的和期望返回证据。
- 两个及以上长期上下文分别持有独立事实权威，需要围绕公共契约或共享决策短期发现、版本化裁决和验证。

## 不适用场景

- 下一会话只是按既有 Goal、决策集合、恢复入口和下一动作继续工作。
- 只因达到固定 token 阈值、会话轮数、仓库星数、作者使用频率或工具宣传而创建交接。
- 任务不能冻结输入，或返回结果没有明确写回位置和裁决责任人。
- 单一上下文可以直接完成，参与方没有独立权威或可复核证据，或任务可拆成独立 Worker 后直接汇合。

## 读取后必须产出

- `Continue / Branch / Worker / Checker` 中的一个语义判断。
- 命中 Branch 时的一份最小出站契约，以及证据返回时的一份返回契约。
- 命中双边契约会商时的一份 `Contract Inquiry`、提供方证据响应、消费者对账和 Checker 准出结论。
- 命中主持式多方会商时的一份 `Meeting Charter`、各方 `Position Card`、`Conflict Matrix`、`Meeting Resolution` 和 Checker 准出结论。
- 运输方式、脱敏结果、授权边界、停止条件和失效条件。

## 需要继续读取的 reference

- Goal、跨轮状态和恢复入口读 `goal-governance.md`、`delivery-execution-control.md`。
- Worker、Checker 和文件化交接读 `engineering-governance.md`。
- 高保真问题、决策包和原问题台账读 `../../grill-me/references/question-ledger.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 继续已确认任务 | `1. 正名与准入` | 不生成 Branch 材料 |
| 临时分叉取证 | `1. 正名与准入`、`2. 运输和出站契约` | 不复制完整会话或长期状态 |
| 接收分叉结果 | `3. 返回契约与对账` | 不凭摘要覆盖原决策 |
| 双边契约会商 | `1. 正名与准入`、`4.1` 至 `4.3` | 不把双方变成平级 Goal owner，不永久互聊 |
| 主持式多方会商 | `1. 正名与准入`、`4.1`、`4.4` | 不自由群聊，不让参与方互改权威载体 |

## 1. 正名与准入

跨上下文先正名为 `Continue / Branch / Worker / Checker`：

- `Continue`：下一会话继续同一 Goal 和已确认动作；从 Goal Ledger、Spec、Issue 或任务文档恢复，不另建交接材料。
- `Branch`：主线状态冻结，只把一个目的明确、可以独立取证且适合干净上下文的问题临时分叉；证据返回后回到原问题裁决。
- `Worker`：在冻结输入和授权范围内执行低耦合任务；仍受写入、验证和状态回写契约约束。
- `Checker`：独立核验原始产物和证据；不得只消费 Maker 摘要或推理轨迹。

Branch 不是新的控制机制，不要求生成 `work_graph`，也不自动派 Worker 或 Checker。只有上下文隔离对取证质量有明确收益，并且能够写清期望返回证据时才使用；固定 token 阈值和外部经验不能单独触发 Branch。

## 2. 运输和出站契约

优先复用平台原生 handoff；当前平台没有原生能力时，才把脱敏 Markdown 放在操作系统临时目录，不写入当前仓库。需要长期审计或多人持续维护时，按授权写回既有状态载体，不再称为临时 Branch。不得自行创建永久 `HANDOFF.md`、状态目录或第二真相源。

```text
Context Branch Handoff:
目的 / 非目标:
主线 Goal / 决策快照:
权威材料指针: Spec / Plan / ADR / Issue / Commit / Diff / 源码路径，只引用不复制
已确认事实 / red_lines / 待确认:
建议加载的最小 Skills / references:
允许动作 / 禁止动作:
期望返回证据:
原问题写回位置:
预算 / 停止 / 失效条件:
敏感信息检查: API key / 密码 / PII / 客户或生产敏感信息已清理
```

## 3. 返回契约与对账

返回契约只带新增信息，不回灌整段对话：

```text
Context Branch Return:
新增证据 / 来源锚点:
改变的判断 / 理由:
未决阻塞 / 置信边界:
产物锚点 / 验证结果:
建议写回项:
原决策快照对账: confirmed / conflict / reopen
```

主线 Goal、Owner 决策和 red_lines 始终高于 Branch 摘要。返回后必须与原决策快照对账；证据冲突时停止覆盖并交 Owner 裁决。Branch 不创造写仓库、Git、联网、安装、生产、密钥、部署或不可逆操作授权。由 `grill-me` 发起的高保真取证继续使用其决策包字段，本文件只提供运输语义。临时材料达到返回或失效条件后停止引用；是否清理由当前平台或人类 Owner 按权限处理。

## 4. 同级权威会商

两个及以上长期上下文分别拥有独立事实权威，且需要围绕公共契约或共享决策短期共同发现时，使用“限时会商 -> 定契 -> 验证 -> 裁决 -> 退场”。这是既有 Goal 下的场景路由，不是 Branch、handoff、新控制机制、群聊模式或常驻多 Agent 组织。

### 4.1 准入与一主、多权、独立证

- **准入**：两方共享消费者与提供方契约时走双边会商；只有三个及以上独立权威必须裁定同一共享决策，且不能拆成独立双边议题时，才进入多方会商。可拆任务走双边会商或 Worker 并行后汇合。
- **一主**：知止者持有总 Goal、议程、决策快照、冲突裁决路径和综合结论，不吞并领域事实。
- **多权**：每个参与方只维护自己稳定的事实、责任和版本；双边特例中，消费者拥有场景、业务语义与验收，提供方拥有公共契约、实现边界和验证证据。
- **独立证**：Checker 读取各方最终产物、原始证据和接受版本，验证契约、冲突裁决与越界写入；不只复述会议摘要。

不设固定参与数上限，参与方数量由独立权威、决策必要性和预算约束；议题可分时拆成多轮。多方会商采用主持式星型拓扑：主持者逐方发送同一议题契约、收集独立陈述并只回传差异，参与方不彼此自由广播或修改他方载体。共享消息流、评论和会议共识都不是权威事实。

边界未定时，各方先从一手材料形成事实、不变量、疑问和非目标，再讨论差异与冲突，避免被他方方案锚定。会商一旦形成可验证契约或决议就结束高带宽讨论，转为低交互供给、执行或验收。

### 4.2 双边定契与版本

```text
Contract Inquiry:
inquiry_id / goal_id:
消费者权威指针 / consumer_revision:
提供方基线指针 / provider_baseline_revision:
真实场景 / 业务不变量 / 非目标:
待回答的公共契约问题:
期望证据 / 双方写入边界:
回复状态 / 停止条件 / 失效条件:
```

同一 `inquiry_id + consumer_revision + provider_baseline_revision` 的 `Contract Inquiry` 重试不得产生第二份请求。响应另按证据版本化：同一响应键重试只能返回同一结果；任一权威修订、引用证据变化或失效条件命中时，旧响应标记为 `stale`，新响应递增 `response_revision`、生成新的 `evidence_fingerprint` 并用 `supersedes` 指向旧响应，不得改写基线版本或更换 `inquiry_id` 规避重开。消息、评论、任务摘要和会商共识都不是权威版本。

### 4.3 双边验供与归复

```text
Provider Evidence Response:
inquiry_id / consumer_revision / provider_revision / response_revision:
evidence_fingerprint / supersedes?:
逐项结论: supported / conditional / gap / out_of_scope
公共契约 / 副作用 / 兼容边界:
源码 / 测试 / Spec / 运行证据锚点:
Owner Gate / 未决项 / 失效条件:

Consumer Reconciliation:
inquiry_id / accepted_consumer_revision / accepted_provider_revision:
逐场景验收 / 集成产物锚点:
对账: confirmed / conflict / reopen / stale
未决项 / Owner / 下一动作:
```

响应幂等键为 `inquiry_id + consumer_revision + provider_revision + evidence_fingerprint`。提供方的自述不等于支持；必须回传与当前版本绑定的实现和验证证据。消费者也不能只接收摘要，必须以真实场景独立验收。Checker 最后核对：双方权威是否越界、接受的版本是否一致、公共契约是否有原始证据、业务场景是否偷渡未承诺能力、冲突是否有 Owner。

### 4.4 主持式多方会商

多方会商不复制双边请求响应链，也不让所有参与方维护同一结论。主持者先定会议契约，各方在看到他方方案前独立陈述，再只处理冲突：

```text
Meeting Charter:
meeting_id / goal_id / charter_revision:
议题 / decision_questions / 非目标:
主持者 / decision_owner / participant_authority_refs:
允许消息 / 写入边界 / 期望证据:
预算 / 停止条件 / 失效条件:

Position Card:
meeting_id / charter_revision / participant / authority_revision:
事实 / 不变量 / 主张 / 异议:
证据 / 置信边界 / Owner Gate:

Conflict Matrix:
meeting_id / charter_revision / issue_id / 各方版本:
共同事实 / 冲突:
可选裁决 / decision_owner / 所需新证据:

Meeting Resolution:
meeting_id / charter_revision / resolution_revision:
accepted_authority_revisions:
evidence_fingerprint / supersedes?:
逐项裁决: accepted / rejected / pending
依据 / 行动项 / Owner / Checker:
停止条件 / 重开条件 / 失效条件:
```

决议幂等键为 `meeting_id + charter_revision + accepted_authority_revisions + evidence_fingerprint`；同一键重试不得产生第二份裁决。议程或参与方版本变化时按新 revision 重开；只有证据变化时，旧卡片与旧决议标记为 `stale`，新决议递增 `resolution_revision`、生成新的 `evidence_fingerprint` 并用 `supersedes` 指向旧决议。主持者只归并共同事实、差异和依赖，不替各方改写权威内容。`decision_owner` 逐项裁决，不强求共识；`pending` 必须绑定 Owner、新证据和下一动作。Checker 最后回读原始证据、各方接受版本、`Conflict Matrix` 和 `Meeting Resolution`，会议纪要或共享消息流不能单独准出。

### 4.5 停止、重开与授权

- 提供方证据响应完成、消费者返回 `confirmed`、Checker 无阻断项后，停止高带宽会商；Goal 只保存裁决和权威指针，不复制双方正文。
- 多方议题全部形成 `accepted / rejected`，或 `pending` 已绑定 Owner 与下一证据，且 Checker 无阻断项后退场；Goal 只保存 `Meeting Resolution` 和各方权威指针。
- 没有新事实、差异、阻塞或验证证据时暂停讨论，不用重复消息制造进展。
- 只有新增场景、公共契约变化、接受版本不一致、证据失效或运行反馈推翻假设时，才以新 revision `reopen`。
- 任何会商、响应、确认或 Checker 结论都不产生仓库写入、Git、联网、安装、发布、生产、密钥、部署或不可逆操作授权。
