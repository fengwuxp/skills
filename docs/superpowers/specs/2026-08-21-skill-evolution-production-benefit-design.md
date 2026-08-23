# Skill 自动持续进化与线上收益方案

状态：方案候选，未授权生产实施

## 1. 架构类型、结论与设计边界

架构类型：产品架构 + 系统架构方案。

本方案允许 Skill 自动产生候选、自动评估、自动进入受控线上实验，并在满足线上收益与风险门槛后自动切换运行时版本；**第一轮必须人工确认**。自动化不直接覆盖源仓库中的 `SKILL.md`，而是切换生产 Skill Registry 中的不可变版本指针；源仓库只由人工审查后的 Promotion PR 写回。

线上收益的定义是：在预先登记的真实业务主指标上，相对当前生产版本取得可复核的增量，并且合规、质量、成本和稳定性护栏没有退化。方案不承诺必然增长，也不把离线分数、LLM Judge 分数或一次成功运行当作收益证明。

## 2. 业务目标、目标与非目标

业务目标：让经人工确认的 Skill 候选能够在可审计、可回滚的条件下持续验证并产生可归因的线上收益。

### 2.1 目标

- 把“经验 -> 候选 Skill -> 评估 -> 人工确认 / 自动晋升 -> 线上反馈”做成可追溯闭环。
- 首轮以人工确认建立一个 Skill 的自动化资格档案。
- 后续只在明确的编辑区、预算、数据集、业务指标和风险护栏内自动进化。
- 通过灰度实验直接验证线上主指标，收益成立后再自动切换运行时版本。
- 任一版本可在分钟级回退到最近的 last-known-good 版本。

### 2.2 非目标

- 不自动修改冻结的合规红线、权限、工具调用策略或安全规则。
- 不自动修改模型权重，不建设通用 Skill Bank，不做无限制的跨领域迁移。
- 不把原始用户内容、生产密钥、个人信息或未脱敏轨迹送入优化器。
- 不以自动提交 Git、自动同步 Codex 安装目录或自动发布源仓库作为生产闭环。
- 不用离线代理指标替代真实线上业务指标。

## 3. 现状、当前事实与关键假设

现状：Skill 候选可以离线生成和评估，但生产写回、线上收益归因、自动回滚和自动晋升资格尚未形成统一控制面。

### 3.1 已知事实

- SkillOpt 的有效机制是有界文本编辑、留出集门控、拒绝反馈和可审计版本，而不是无条件重写。
- Push 文案等主观任务通常没有可靠离线 CTR，只能先用合规和质量代理指标筛候选，再用线上实验判断业务收益。
- 当前仓库已有学习回流、候选账本、独立验证和 Owner 裁决边界；这些边界不能被“自动进化”绕过。

### 3.2 假设

- 生产执行器可以在请求或任务级记录脱敏后的 `skill_version`、实验分组和业务结果归因键。
- 业务方能够定义一个主指标和不超过五个护栏指标，并提供最小实验观察窗口。
- 线上流量可以按稳定随机单元分组，且存在当前生产版本作为控制组。

### 3.3 待确认项

| 项目 | 影响 | 确认方 |
|---|---|---|
| 真实主指标是 CTR、转化、有效提交还是其他结果 | 决定线上晋升门槛 | 业务 Owner |
| 随机化单元与归因窗口 | 决定实验是否可解释 | 数据 / 增长 Owner |
| 哪些 Skill 可进入自动化档案 | 决定系统边界 | Skill Owner |
| 合规红线与人工复核范围 | 决定硬门禁 | 合规 / 业务 Owner |
| 生产 Registry、权限与回滚接口 | 决定工程落点 | 平台 / SRE Owner |

## 4. 产品定位与责任边界

产品定性：**Skill 版本进化与收益验证控制面**，不是“会自己改规则的 Agent”。

| 角色 | 责任 | 不得做什么 |
|---|---|---|
| Skill Owner | 定义目标、冻结区、业务指标、首轮确认和自动化授权 | 不把一次实验成功解释成普遍规律 |
| Evolution Runner | 采集脱敏证据、生成候选、执行离线门禁 | 不直接修改生产指针 |
| Independent Checker | 盲测、hard-negative、合规和回归检查 | 不替 Owner 做价值取舍 |
| Online Experiment Controller | 分流、曝光、指标计算、灰度和回滚 | 不在指标缺失时自动晋升 |
| SRE / 业务值班人 | 告警、止血、回退、事故升级 | 不修改候选内容绕过审计 |
| 生产 Skill Registry | 保存不可变版本和当前指针 | 不保存可变的“最后一次文本” |

## 5. 能力地图与能力范围

能力地图：离线进化、人工确认、线上实验、收益归因、版本注册、自动晋升和回滚共同组成 Skill 进化控制面。

### 5.1 离线进化能力

- 运行轨迹脱敏与证据摘要。
- 失败 / 成功样本分组和 hard-negative 采样。
- Optimizer 生成 `add / replace / delete` 有界编辑。
- 受保护区、编辑预算、重复编辑和冲突检查。
- `train / selection / test` 三划分评估。
- 候选报告、diff、指标、证据指纹和拒绝原因。

### 5.2 人工确认能力

审核页或等价审查载体必须展示：

- 当前版本与候选版本的完整 diff。
- 受影响段落、冻结区命中结果和规则解释。
- 基线 / 候选的离线指标、样本数、配置、模型与 harness 版本。
- 稳定样例、失败样例、邻近 hard-negative 和多语言样例。
- 独立 Checker 结果、残余风险、预期线上主指标和回滚版本。
- `approve_for_canary / reject / request_revision` 三种结论及理由。

### 5.3 线上收益能力

- 同一随机化单元稳定进入 control 或 candidate，避免请求级抖动。
- 记录 `experiment_id`、`skill_version`、曝光时间、结果归因键和指标版本。
- 支持 shadow、canary、full rollout 三个阶段。
- 主指标、护栏指标、样本比异常、数据延迟和分层结果可查询。
- 通过规则门禁后自动提升流量；触发风险时自动回退指针。

## 6. 业务对象、核心对象与状态

### 6.1 对象

| 对象 | 关键字段 | 权威用途 |
|---|---|---|
| `SkillProfile` | `skill_id`、可编辑区、冻结区、Owner、自动化策略 | 定义某个 Skill 是否有资格自动进化 |
| `SkillVersion` | `version_id`、内容 hash、父版本、diff、配置 hash | 不可变运行时产物 |
| `EvolutionRun` | 数据集、模型、harness、预算、开始 / 结束、运行状态 | 一次离线进化事实 |
| `EvaluationSnapshot` | split、指标版本、样本数、分数、置信区间、Checker 结论 | 候选比较证据 |
| `PromotionDecision` | 决策类型、规则、操作者 / 自动策略、理由、时间 | 晋升审计事实 |
| `Experiment` | 分组、流量、主指标、护栏、观察窗口、停止规则 | 线上收益实验事实 |
| `RollbackEvent` | 触发原因、旧版本、新版本、恢复时间、操作者 | 回退事实 |

### 6.2 状态机

```text
GENERATED
  -> CHECKED
  -> PENDING_HUMAN_REVIEW
  -> APPROVED_FOR_CANARY
  -> RUNNING_CANARY
  -> PROMOTED

CHECKED -> REJECTED
PENDING_HUMAN_REVIEW -> REJECTED / REQUEST_REVISION
RUNNING_CANARY -> ROLLED_BACK / EXPIRED
PROMOTED -> SUPERSEDED / ROLLED_BACK
```

第一轮必须经过 `PENDING_HUMAN_REVIEW -> APPROVED_FOR_CANARY`。进入自动化档案后，自动流程可以跳过重复的人工审批，但不能跳过硬门禁、独立评估、线上观察窗口和回滚能力。

## 7. 业务流程与端到端流程

### 7.1 阶段 A：首轮人工确认

1. Owner 注册 `SkillProfile`，指定 `editable_sections`、`frozen_sections`、数据边界、主指标和护栏。
2. Runner 只读取脱敏轨迹和注册数据集，生成一个候选版本。
3. Deterministic Gate 检查 frontmatter、引用、冻结区 hash、禁止词、工具权限和输出 schema。
4. Independent Checker 做盲测、稳定样例、hard-negative 和多语言检查。
5. Owner 审阅完整 diff，批准候选进入小流量 canary，或拒绝 / 要求修改。
6. Experiment Controller 以当前生产版本为 control，候选只进入限定流量。
7. 观察窗口结束后，Owner 根据线上主指标和护栏确认：`PROMOTE / ROLLBACK / KEEP_CANARY`。
8. 只有 `PROMOTE` 才生成自动化资格档案；源仓库仍由人工提交 Promotion PR。

首轮的通过条件：所有硬门禁通过、独立 Checker PASS、主指标没有统计意义上的负向结果、护栏不退化、数据归因完整，并有明确回滚记录。单次“某个样例变好”不算通过。

### 7.2 阶段 B：受限自动进化

自动流程每次只做以下动作：

1. 在登记的数据窗内收集证据。
2. 生成不超过 `max_edit_budget` 的候选 diff。
3. 执行硬门禁与 selection split 评估。
4. 通过后先进入 shadow 或 canary，不直接全量。
5. 线上达到主指标和护栏门槛后自动切换 Registry 指针。
6. 生成待人工审查的 Promotion PR 和实验报告；人工审查只影响源仓库归档，不阻塞已满足策略的运行时回退。

### 7.3 阶段 C：持续收益回流

- 已晋升版本产生的线上轨迹进入下一轮脱敏样本池。
- 只把重复、可复核、与 Skill 行为直接相关的失败归因送入候选生成。
- 线上收益下降、指标漂移或业务规则变更时，自动暂停进化并回退到 last-known-good。
- 版本达到最大连续自动晋升次数后强制人工复核，避免长期无审查漂移。

## 8. 规则矩阵与自动化资格策略

规则矩阵：候选状态、编辑权限、评估门禁、人工审批、线上晋升和回滚均按版本化策略判断。

`SkillProfile` 必须显式配置以下策略；缺省即关闭自动化：

```yaml
automation:
  enabled: false
  first_round_human_approval: true
  editable_sections: []
  frozen_sections: []
  max_edit_budget: 2
  min_selection_margin: 0
  max_canary_ratio: 0.10
  max_consecutive_auto_promotions: 3
  cooldown: required
  require_independent_checker: true
  require_online_primary_metric: true
  auto_rollback: true
```

以下任一情况必须转人工：

- 触碰冻结区、权限、工具策略或合规红线。
- 主指标与代理指标方向冲突。
- 样本比异常、数据延迟、归因缺失或分层结果相互矛盾。
- 进入新语言、新业务类别、新模型或新 harness。
- 需要增加外部依赖、读取新数据源或扩大数据权限。
- 连续两次候选被拒绝，或连续两次自动晋升后收益不再显著。
- 线上护栏触发、用户投诉上升、成本或延迟越界。

## 9. 线上指标与收益归因

### 9.1 指标层级

| 层级 | 示例 | 晋升用途 |
|---|---|---|
| 主指标 | CTR、有效提交率、转化率、任务成功率 | 决定是否产生业务收益 |
| 质量指标 | 人工质量分、事实正确率、格式通过率、多语言自然度 | 判断收益是否以质量换来 |
| 护栏指标 | 合规违规率、投诉率、错误率、延迟、Token 成本、人工返工率 | 任一越界即暂停 / 回退 |
| 诊断指标 | 多样性、泛化折扣、编辑接受率、样本覆盖率 | 解释原因，不单独决定晋升 |

### 9.2 晋升判据

自动晋升必须同时满足：

```text
primary_metric(candidate) 的统计下界 > primary_metric(control)
且所有 guardrail 不低于基线容忍线
且样本比、归因完整性、数据新鲜度均通过
且没有硬门禁或人工否决标记
```

统计口径、最小样本量、观察窗口和置信水平由数据 Owner 确认后写入 `Experiment`，不能由 Optimizer 自行决定。多语言、多品类、多模型必须分别报告，不能只报总平均值。

## 10. 运行时、接口契约与接口抽象

接口契约：候选生成、门禁评估、人工审批、实验观测、版本晋升和回滚接口必须保持幂等、可审计和失败可恢复。

首版采用模块化单体或现有平台内的离线任务，不因“持续进化”直接拆微服务。

```text
CandidateGenerator.generate(EvolutionRun) -> SkillVersion(candidate)
Gate.evaluate(candidate, baseline, EvaluationSnapshot) -> GateDecision
Review.approve(candidate, reviewer) -> PromotionDecision
Experiment.start(candidate, control, policy) -> Experiment
Experiment.observe(experiment_id) -> ExperimentSnapshot
PromotionController.promote(experiment_id) -> PointerUpdate
RollbackController.rollback(skill_id, reason) -> RollbackEvent
```

契约要求：

- `SkillVersion` 内容不可变，使用 content hash 去重。
- `PromotionController` 以 `(skill_id, version_id, experiment_id)` 做幂等键。
- Registry 指针采用 compare-and-set；旧指针保留，切换失败不得部分生效。
- 所有拒绝、晋升和回退都带规则版本、配置 hash、证据指纹和责任主体。
- 运行时只读取 Registry 当前指针，不读取“最新生成文件”或可变工作目录。

## 11. 数据、一致性与安全

### 11.1 数据方案

- Skill Registry 保存不可变版本、父子关系、hash、状态和当前指针。
- Evaluation Store 保存数据集版本、配置、模型 / harness、指标结果和证据索引。
- Experiment Store 保存分组、曝光、归因结果、指标窗口和决策。
- Audit Store 保存 diff、审查、策略命中、自动动作、回退和异常。

原始用户内容默认不进入长期 Skill 训练库；需要人工复核时只提供脱敏、最小化、带访问审计的样本。

### 11.2 一致性不变量

- 生产指针只能指向 `CHECKED` 且通过晋升门禁的不可变版本。
- `PROMOTED` 版本必须存在对应 `Experiment` 和完整观察窗口。
- 任何版本切换均可追溯到唯一 `PromotionDecision`。
- 任何自动晋升均不可修改历史版本或历史指标。
- 统计未完成、数据延迟或审计写入失败时，默认拒绝晋升。

### 11.3 安全边界

- Optimizer 无生产写权限，只能提交候选对象。
- Candidate 不能新增工具、权限、网络访问、数据范围或系统指令。
- 冻结区用 hash 和结构化检查双重保护，不能只依赖 Prompt 指令。
- 轨迹采集、脱敏、保留期、访问角色和导出均需单独审计。
- 外部 Skill、脚本和模型配置按供应链规则审查，不把第三方运行指令当授权。

## 12. 发布、灰度与回滚

### 12.1 默认发布路径

```text
离线候选
  -> 人工首轮批准
  -> shadow
  -> 小流量 canary
  -> 观察窗口
  -> 自动 / 人工晋升
  -> 分阶段放量
```

具体流量比例由业务风险确认；高风险 Skill 默认只允许 shadow 和人工晋升。

### 12.2 回滚条件

- 主指标达到预设负向阈值。
- 任一合规、安全、投诉或质量护栏越界。
- 样本比异常、指标延迟或归因系统不可信。
- 发现候选存在数据泄露、提示注入、工具越权或跨租户影响。

回滚动作是原子切换 Registry 指针到 last-known-good，不删除候选和实验记录。回滚后自动暂停该 `SkillProfile`，等待人工复核。

## 13. 验证方案与验证矩阵

验证方案：采用结构检查、固定任务回放、独立 Checker、线上 A/B、告警演练和回滚演练的分层证据。

| 层级 | 验证内容 | 通过证据 |
|---|---|---|
| 结构 | frontmatter、引用、冻结区、编辑预算、权限 | Deterministic Gate 报告 |
| 行为 | baseline / candidate 同配置回放 | 固定任务集、原始输出和 diff |
| 对抗 | hard-negative、冲突规则、提示注入、空输入 | 独立 Checker PASS |
| 主观质量 | 盲评、多语言、业务样例 | 评审记录和一致性说明 |
| 线上实验 | 分流、样本比、主指标、护栏 | Experiment 报告 |
| 发布 | 灰度、告警、回退 | Runbook 演练和回滚记录 |

最低准出条件：不能只证明“候选比当前好一次”，必须同时证明没有硬门禁回退、线上主指标可归因、护栏未退化、回滚可执行。

## 14. 实施切片与停止条件

### 14.1 第一切片：人工首轮

- 选择一个已有客观 validator 和小型固定任务集的 Skill。
- 只做候选生成、diff 审查、离线 gate、人工批准和 shadow / canary。
- 不实现通用 Skill Bank、不实现自动写源仓库、不接多业务、多语言全量。

### 14.2 第二切片：受限自动晋升

- 增加 Registry 指针、Experiment、主指标归因、自动回退和策略配置。
- 只对首轮通过且 Owner 显式开启的 `SkillProfile` 生效。
- 运行时自动切换版本，源仓库继续人工 PR 归档。

### 14.3 停止条件

- 找不到可靠主指标或稳定归因键：停止线上自动晋升，只保留离线候选。
- 独立 Checker 无法区分真实改进与评估器偏差：停止自动化。
- 任何安全、合规、权限或数据边界无法证明：停止生产接入。
- 连续自动晋升未带来可重复线上收益：关闭该 Skill 的自动化档案。

## 15. 验收标准

- 首轮候选没有人工批准时，生产指针不会改变。
- 自动候选只能修改登记的可编辑区，冻结区 hash 不变。
- 线上晋升必须有完整 Experiment、主指标、护栏、配置 hash 和 PromotionDecision。
- 模拟主指标负向、样本比异常、数据延迟和审计失败时，系统自动拒绝或回滚。
- 回滚后可恢复 last-known-good，且候选和实验记录仍可审计。
- 业务 Owner 能回答“哪一个 Skill 版本、在什么流量、带来什么指标变化、是否有代价”。

## 16. 最终待确认与责任人

- 主指标、护栏指标、统计口径、最小样本量和观察窗口：数据 / 业务 Owner。
- Skill 的编辑区、冻结区和自动化资格：Skill Owner。
- Registry、实验分流、指针切换、告警和回滚：平台 / SRE Owner。
- 脱敏、保留期、访问权限和审计：安全 / 隐私 Owner。
- 首轮人工批准和自动化启用：业务 Owner + Skill Owner 双确认。
