# 场景化角色合议配置

本文是角色、站位、视角、主张依据和场景化工作位选择的通用权威。它为 `wise-agent` 的主持式会商及专业 Skill 内部的多视角讨论提供共同语义，不新增顶层模式、人格、事实源、决策 Owner、Checker 或执行授权。

## 使用时机

- 用户显式要求角色讨论、多视角碰撞、合议、辩论、红队或让不同责任方共同审视一个决策。
- 同一决策同时影响多个真实主体、责任、证据边界或不可接受后果，单一视角容易漏掉承重约束。
- `context-handoff.md` 的主持式多方会商需要确定谁应进入 `Position Card` 阶段。

## 不适用场景

- 事实和方案都已确认，只需执行一个边界清楚的局部动作。
- 只有多个可独立完成的任务，没有共享决策；应走 Worker 或分别处理后汇合。
- 只是希望输出显得热闹、模拟多个职业口吻或用角色数量代替证据。
- 缺少影响决策的真实分歧；普通专业任务继续由对应 Skill 直接完成。

## 读取后必须产出

- `task_phase`、`domain_object`、`decision_questions` 和讨论停止条件。
- 一份按当前问题裁剪的 `Discussion Role Matrix`，或简单任务不启用角色合议的结论。
- 每个工作位的责任、代表对象、保护结果、检查视角、权威范围、主张依据和决策权。
- 冲突裁决路径、`decision_owner`、`checker_required: yes / no`、判断依据与失效条件；需要 Checker 时再声明独立验证者。

## 需要继续读取的 reference

- 跨上下文、双边契约和主持式多方会商协议读 `context-handoff.md`。
- UI 设计角色包读 `../../ui-design-expert/references/deliberation-role-configuration.md`。
- 小说剧情、历史、世界、神话、人物、文明发展与正文写作角色包读 `../../novelist/references/deliberation-role-configuration.md`。
- 产品合议与 PRD 评审继续读 `../../product-architecture-expert/references/product-deliberation-workflow.md`；系分和工程判断继续由 `senior-software-architect` 承担。

## 一、四个概念必须分开

| 概念 | 回答的问题 | 不能冒充 |
| --- | --- | --- |
| 角色 `role` | 承担什么责任、提供什么独特贡献 | 人格、职业表演或事实权威 |
| 站位 `position` | 代表谁、保护什么结果、拒绝什么后果 | 永久立场或天然否决权 |
| 视角 `lens` | 用哪些问题和证据审视当前决策 | 完整结论或独立 Checker |
| 依据 `perspective_basis` | 主张来自 `authority / evidence / stakeholder_need / hypothesis` 中哪一类 | 角色名称、模型数量或多数意见 |

角色名称本身不授予权威。一个“合规角色”若没有当前法域、规则或责任锚点，只能以 `hypothesis` 提出核验问题；一个“用户角色”若没有访谈、工单、任务测试或运行证据，只能表达待验证的 `stakeholder_need`，不能冒充目标用户结论。

## 二、按阶段与对象选择工作位

先冻结两个正交坐标，再选角色：

- `task_phase`：当前在发现、发散、收敛、规划、起草、评审、验证、恢复或治理中的哪一阶段。使用贴合任务的名称即可，不建立固定枚举。
- `domain_object`：当前真正被裁定的对象，例如需求、产品方案、界面任务、公共契约、候选 diff、事故恢复、历史设定、人物选择或正文场景。

同一专业对象在不同阶段需要不同工作位。例如 UI 新方向发散需要任务、内容与视觉差异，Design QA 需要契约、实现和证据；小说幻想发散保护原始核，正文起草则必须回到单一叙述主体。不得只按“UI”“小说”“架构”等名词加载固定角色表。

选择顺序：

1. 冻结 `decision_questions`、`task_phase`、`domain_object`、事实基线和期望产出。
2. 沿每个问题识别受影响主体、结果责任人、能力消费者与提供者、风险承担方、证据持有者和最终裁决者。
3. 只把能提供独特责任、证据、约束、反证或决策权的候选变成工作位。
4. 同质工作位合并；同一参与者可承担兼容职责，但存在利益冲突、自审或越权时必须拆开。
5. 先按风险判断 `checker_required`：高风险、公共契约、重要交付或发布准出为 `yes`；低风险、可逆且只形成候选时可以为 `no`，但必须写清 `checker_basis`。需要 Checker 时，只有独立 Checker 可以 `verify`。
6. 没有真实差异或角色不能改变任何 `decision_question` 时，停止配置并直接完成专业任务。

## 三、通用席位

通用席位是选择类别，不是每次必须凑齐的固定名单：

| 席位 | 责任 | 边界 |
| --- | --- | --- |
| 主持位 | 冻结主题、版本、角色、消息和讨论预算，归并差异 | 不替领域 Owner 判断事实或拍板 |
| 责任立场位 | 代表真实主体、对象或能力责任，提供独特约束和后果 | 只在自身权威范围内陈述 |
| 挑战位 | 攻击承重假设、失败路径、盲区和不可逆后果 | 不为制造冲突而反对，不直接改正文或方案 |
| `decision_owner` | 对 `accepted / rejected / pending` 逐项裁决 | 不把多数意见或模型一致当依据 |
| Checker | `checker_required=yes` 时回读原始产物、证据、接受版本和越界情况 | 不参与方案投票，不只消费 Maker 或会议摘要；低风险候选不为凑席位强制增加 |

### Discussion Role Matrix

```text
deliberation_id / role_revision / role_fingerprint / supersedes?:
task_phase / domain_object / decision_questions:
checker_required: yes / no / checker_basis:
role_id / participant / accountability / represented_subject:
protected_outcome / optimization_target / unacceptable_result:
lenses / required_information / evidence_refs:
authority_scope / perspective_basis:
decision_right: advise / challenge / decide / verify
known_blind_spots / entry_reason / separation_constraints / exit_condition:
```

`perspective_basis` 可以声明工作位的主要依据；卡片中的具体事实、需求或假设仍须逐项回链，不因工作位已有一个 `authority_ref` 就把全部主张升级为权威。

`Discussion Role Matrix` 发布后不可原地改写。参与者、责任、代表对象、保护结果、视角、权威范围、决策权、Checker 门禁或退出条件任一变化时，递增 `role_revision`，对新矩阵生成 `role_fingerprint`，并用 `supersedes` 指向旧 revision；旧卡片与决议保持可追溯但标为 `stale`。由主持式会议承载时，`deliberation_id` 使用该会议的 `meeting_id`，不得为同一讨论另造身份。

## 四、通用场景路由

| 场景 | 优先责任站位 | 主要视角 |
| --- | --- | --- |
| 问题与需求发现 | 目标用户、业务结果、一线执行、证据、风险承担 | 真问题、频率、替代方式、失败成本、证据强度 |
| 方案探索与产品设计 | 结果、能力提供、能力消费、运营承接、成本风险 | 价值、可用、可行、可运营、成本、可逆 |
| 系分与架构边界 | 业务能力、领域或数据、消费者、提供者、可靠性或安全 | 对象、状态、契约、依赖、失败、演进 |
| 代码与交付评审 | 变更说明、契约消费、维护、测试、运行或安全 | 正确性、影响面、回归、兼容、观测、回滚 |
| 事故与恢复 | 事件主持、故障域、止损恢复、受影响主体、必要风险责任 | 止损、证据保全、定位、恢复、沟通、后续改进 |
| 投资与治理 | 价值受益、资源成本、执行、风险合规、长期维护 | 收益链、机会成本、责任承接、退出条件、长期负担 |
| UI 设计 | 转读 UI 专业角色包 | 任务类型、设计阶段、状态、可访问性与证据等级 |
| 小说创作 | 转读小说专业角色包 | 创作阶段、正典、人物、世界因果、读者承诺与叙述声腔 |

每次只选择一个主场景；只有另一场景中的现实约束能够推翻当前结论时，才增加一个挑战场景。主题跨多个对象时按 `decision_questions` 分轮，不一次跑满全部角色包。

事故恢复优先处理止损、证据保全、恢复和责任承接，不把高带宽讨论放在客户数据或生产风险继续变化之前。发散创作则允许候选暂时矛盾，但仍保留事实标签、授权和写回边界；这两类场景不得套用同一讨论节奏。

## 五、运行与裁决

完整顺序为：

`decision_questions -> task_phase / domain_object -> Discussion Role Matrix -> Shared Information Matrix -> Position Card -> Conflict Matrix -> decision_owner -> Checker?`

- 工作位先在同一信息版本上独立形成卡片，再交换差异，避免被先发方案锚定。
- 交叉质询只交换最强反证、被低估的约束和改变立场所需证据；没有新增事实、风险、反证或综合候选时停止。
- 事实冲突回到权威与证据版本，需求冲突回到真实主体和后果，取舍冲突交 `decision_owner`；`hypothesis` 不能取得否决权。
- `checker_required=yes` 时，`decision_owner`、Maker 与 Checker 必须分离；Maker 可以解释意图，不能自证准出。`checker_required=no` 只适用于低风险、可逆候选，不得据此声明正式验收、发布或高风险准出。
- 角色 revision 或 fingerprint、参与者权威、信息或证据版本变化时，相关卡片和决议标为 `stale`，只重开受影响问题。

## 六、停止条件

- 简单任务没有共享决策或真实分歧，直接退出角色配置。
- 必要角色缺少责任主体、权威材料或所需信息，保持 `blocked / pending` 并绑定 Owner，不用模拟角色补齐。
- 所有问题已被裁决，或未决项已有 Owner、所需证据和下一动作，并且 `checker_required=no` 或所需 Checker 已无阻断项时，结束高带宽讨论。
- 任何角色讨论、共识或 Checker 结论都不产生仓库写入、Git、联网、安装、发布、生产、密钥、部署或不可逆操作授权。
