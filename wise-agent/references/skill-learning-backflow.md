# Skill 学习回流

本文定义知止者学习回流模式的候选经验账本、证据门禁、生命周期、受控改进试验、去重和授权边界。它不新增顶层流程，不替代 `code-delivery.md` 的知识归位，也不让 Skill 自行改写。

## 使用时机

- 用户显式要求开启、关闭或检查知止者学习回流模式。
- 当前任务出现重复失败、确认纠偏、fixture / validator 失败、CR 根因或权威来源失效，且需要形成可复核候选。
- 需要评审候选经验是否应进入 Skill、reference、fixture 或 script。

## 不适用场景

- 单次偏好、一次性措辞、仅仅讲过或执行过、文章观点、Agent 自述或工具宣传。
- 未脱敏的私有对话、客户资料、生产数据、密钥或未经授权执行轨迹。
- 直接修改 Skill、确认产品 / 架构结论、Git、同步、发布或生产操作。

## 读取后必须产出

- 是否命中候选记录门禁，以及使用的当前任务证据。
- 目标 Skill、去重结果、候选记录位置，或不记录原因。
- 下一人工评审结论只能由证据与 Owner 裁决为 `candidate / confirmed / promoted / rejected / superseded`；自动化最高只能写入 `candidate` 账本文件。

## 需要继续读取的 reference

- 知识归位、Skill Improvement Card 和仓库改进流程读 `code-delivery.md`。
- Loop 状态、授权与停止条件读 `delivery-execution-control.md`。
- 源码、测试、CR 和发布证据读 `verification-review-release.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 开启或关闭模式 | `1. 模式与授权`、`5. 确定性记录器` | 不读取历史候选正文 |
| 任务收口记录候选 | `2. 候选门禁`、`3. 生命周期`、`4. 去重与字段` | 不扫描历史对话或全部 Skill |
| 评审候选并生成改进 diff | `3. 生命周期`、`6. 晋升门禁`，再读 `code-delivery.md` | 候选不充当运行时指令 |

## 1. 模式与授权

用户显式执行 `scripts/skill-learning-ledger.py enable` 后，只授予 `$SKILL_LEARNING_HOME/wise-agent/`（默认 `~/.skill-learning/wise-agent/`）下的候选记录写入权。没有 `mode.json`、状态不是 `enabled` 或 candidate-only Grant 不完整时不得写入。专业 Skill 不复制模式声明，知止者在任务收口时统一分发和归位。

该 Grant 不包含仓库、Codex Skills 安装目录、历史对话、其他私人目录、联网、Git、同步或发布。关闭模式只撤销后续候选写入，不删除已有记录。

## 2. 候选门禁

可自动记录的证据限于当前任务明确提供、已脱敏且可复核的材料：

- 同一问题有两个独立任务证据。
- 明确 fixture / validator 失败。
- 已确认人工纠偏。
- 已确认 CR 根因。
- 权威来源失效或规则过期。

不得记录单次偏好、一次性措辞、仅仅讲过或执行过、未验证推断、文章观点、Agent 自述、工具宣传、私有对话、客户 / 生产敏感数据和密钥。候选只用于显式回流评审，不参与普通任务决策。

## 3. 生命周期

评审生命周期是 `candidate -> confirmed -> promoted`，也允许进入 `rejected` 或 `superseded`。它不是记录器状态机：

- `candidate`：自动化所能达到的最高状态。
- `confirmed`：Owner 已确认经验可复用、目标 Skill 和权威落点正确；在 `confirmed` 状态内执行受控改进试验并生成最小改进 diff。
- `promoted`：改进已进入权威 Skill、reference、fixture 或 script，并有独立验证证据。
- `rejected / superseded`：证据不足、归位错误或已被新记录替代；保留状态用于防止旧候选复活。

当前确定性记录器不提供状态迁移命令。`confirmed` 是人工评审结论，写入当前任务、CR 或 Decision Log；candidate 账本文件仍保持 `candidate`，不得绕过记录器直接修改私有文件。后续 `promoted / rejected / superseded` 裁决也留在可审计的任务证据中，直到未来另有显式授权、审计和确定性迁移入口。

candidate 账本与 confirmed 评审结论不得反向充当 Skill 指令。运行时行为只能来自已经晋升的权威内容。

受控改进试验不是生命周期状态，不得写成 `RSI Mode` 或第六个控制机制。Owner 只同意探索、但尚未确认复用范围、目标 Skill 或权威落点时，记录仍保持 `candidate`，不得生成仓库改进 diff。

## 4. 去重与字段

每次写入前只读取目标 Skill 下的活跃记录做去重，不扫描历史对话、其他私人目录或全部 Skill。按 `目标 Skill + 观察失败 + 期望行为` 生成指纹；重复候选不得再次写入。

记录字段为：`Status / Target Skill / Evidence Kind / Task Ref / Observed Failure / Expected Behavior / Evidence Refs / Reuse Scope / Proposed Authority / Validation / Sensitivity Check`。

## 5. 确定性记录器

`scripts/skill-learning-ledger.py` 是离线载体，只提供 `enable / disable / status / record / list`。它不联网、不扫描历史、不确认或晋升记录、不修改仓库或 Codex Skills，也不执行 Git。

`record` 必须显式传入当前任务引用、证据类型、证据引用、观察失败、期望行为、复用范围、建议权威落点、验证方式和 `public-safe` 检查。`repeated-failure` 至少需要两个不同证据引用。

账本目录权限固定为 `0700`，模式和候选文件固定为 `0600`；记录器拒绝凭证以及带明确标签的身份证、手机号和银行卡号。该检查只作最后一道防线，不能替代调用前脱敏。

## 6. 晋升门禁

Owner 确认候选后，人工评审结论为 `confirmed`，candidate 账本文件仍保持 `candidate`，再回到 `code-delivery.md` 生成最小可审查 diff。在 `confirmed` 状态内执行受控改进试验：`失败归因假设 -> 最小候选 diff -> 目标样例 / 邻近 hard-negative / 稳定样例对照 -> 独立 Checker -> Owner 裁决`。基线与候选分别绑定原始输出、配置和证据指纹；Checker 同时寻找替代解释与反证，Owner 最终选择 `promote / reject / supersede`，并写清回退条件与责任人。一次目标样例转绿、发布时间压力或 Agent 自述不能直接晋升。

产品、文档、图形和创意等含主观质量的任务，可先写任务级价值判断卡：`期望效果 / 正向参照 / 不期望效果 / 可接受取舍 / 人工判断点 / 最终 Owner`。它只限定当前任务的评价方向；只有重复出现、可复核且经 Owner 确认的模式，才重新进入 candidate 门禁。

独立验证通过后，Owner 才能在任务证据中裁决为 `promoted`；Git、同步和发布仍需单独授权。

候选涉及隐私、金融、合规、安全、生产上线、权限边界或未来默认行为时，即使证据充分也必须人工确认。无法确定权威落点、验证方式或旧值清除范围时停止晋升。
