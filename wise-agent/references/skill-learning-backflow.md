# Skill 学习回流

本文定义候选证据、可修订问题模式、改动版本与结果之间的关联，以及学习回流的授权边界。它不新增顶层流程，不替代 `code-delivery.md` 的知识归位，也不让 Skill 自行改写。

## 使用时机

- 用户显式要求开启、关闭或检查知止者学习回流模式。
- 当前任务出现重复失败、确认纠偏、fixture / validator 失败、CR 根因或权威来源失效，且需要形成可复核候选。
- 需要评审候选经验是否应进入 Skill、reference、fixture 或 script。
- 用户显式要求维护已有经验、查询失败方案、修订问题模式或回链版本试验结果。

## 不适用场景

- 单次偏好、一次性措辞、仅仅讲过或执行过、文章观点、Agent 自述或工具宣传。
- 未脱敏的私有对话、客户资料、生产数据、密钥或未经授权执行轨迹。
- 直接修改 Skill、确认产品 / 架构结论、Git、同步、发布或生产操作。

## 读取后必须产出

- 是否命中候选记录门禁，以及使用的当前任务证据。
- 目标 Skill、去重结果、候选记录位置，或不记录原因。
- 下一人工评审结论只能由证据与 Owner 裁决为 `candidate / confirmed / promoted / rejected / superseded`；自动化最高只能写入 `candidate` 账本文件。
- 显式维护时给出 `skill_id / pattern_id`、当前修订及证据、关联的改动版本与结果；无记录或证据不足时明确说明，不自动补历史。

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
| 查询、修订问题模式或回链结果 | `1. 模式与授权`、`3. 生命周期`、`5. 确定性记录器` | 不遍历其它 Skill、不自动改源文件 |
| 行为评测采集、失败归因与恢复 | `7. 行为评测 Harness 归因与恢复` | 不把 Harness 错误计为 Skill 得分 |

## 1. 模式与授权

用户显式执行 `scripts/skill-learning-ledger.py enable` 后，只授予 `$SKILL_LEARNING_HOME/wise-agent/`（默认 `~/.skill-learning/wise-agent/`）下的候选记录写入权。没有 `mode.json`、状态不是 `enabled` 或 candidate-only Grant 不完整时不得写入。专业 Skill 不复制模式声明，知止者在任务收口时统一分发和归位。

该 Grant 不包含仓库、Codex Skills 安装目录、历史对话、其他私人目录、联网、Git、同步或发布。关闭模式只撤销后续候选写入，不删除已有记录。

`lookup`、`revise-pattern`、`record-impact` 只在用户显式要求评审或维护学习经验时使用，不是开启模式后的自动动作。后两者须另有当前任务的本地维护授权，并显式填写 reviewer 与 `public-safe`；这些参数记录责任和脱敏声明，不替代用户授权。维护可在自动记录关闭或未初始化时进行，不创建或改变 `mode.json`。普通任务不读取模式库，不把其中任何内容作为运行时指令。

## 2. 候选门禁

可自动记录的证据限于当前任务明确提供、已脱敏且可复核的材料：

- 同一问题有两个独立任务证据。
- 明确 fixture / validator 失败。
- 已确认人工纠偏。
- 已确认 CR 根因。
- 权威来源失效或规则过期。

不得记录单次偏好、一次性措辞、仅仅讲过或执行过、未验证推断、文章观点、Agent 自述、工具宣传、私有对话、客户 / 生产敏感数据和密钥。候选只用于显式回流评审，不参与普通任务决策。

## 3. 生命周期

经验采纳的评审生命周期仍是 `candidate -> confirmed -> promoted`，也允许进入 `rejected` 或 `superseded`。不要把它与某个改动版本的成败混为同一个状态机：

- `candidate`：自动化所能达到的最高状态。
- `confirmed`：Owner 已确认经验可复用、目标 Skill 和权威落点正确；在 `confirmed` 状态内执行受控改进试验并生成最小改进 diff。
- `promoted`：改进已进入权威 Skill、reference、fixture 或 script，并有独立验证证据。
- `rejected / superseded`：证据不足、归位错误或已被新记录替代；保留状态用于防止旧候选复活。

`confirmed` 是人工评审结论，原始 candidate 文件保持不变；`confirmed / promoted / rejected / superseded` 采纳裁决仍引用当前任务、CR 或 Decision Log，不就地改写原始观察。显式维护时用以下对象连接证据与裁决：

- **证据记录**：保留原始观察及引用；关联已有记录时保存其摘要指纹，不扫描或复制私有对话。
- **问题模式**：以 `skill_id / pattern_id` 为稳定标识，包含问题摘要、适用范围、可复用策略、反例与证据。`active` 表示当前评审版本，`retracted` 表示已被反证或不再适用；两者都不是运行时启用状态。新证据通过完整修订替换当前知识，旧修订仅保留为历史。
- **改动与结果**：以内容 hash 标识具体改动版本，并关联问题模式、父版本、产物位置、Checker / canary 结果、人工拒绝、晋升和回滚事件。拒绝方案只否定该干预，不自动否定问题；反过来，撤回问题模式也不自动部署或回滚 Skill。

candidate 账本与 confirmed 评审结论不得反向充当 Skill 指令。运行时行为只能来自已经晋升的权威内容。

受控改进试验不是生命周期状态，不得写成 `RSI Mode` 或第六个控制机制。Owner 只同意探索、但尚未确认复用范围、目标 Skill 或权威落点时，记录仍保持 `candidate`，不得生成仓库改进 diff。

## 4. 去重与字段

每次写入前只读取目标 Skill 下的活跃记录做去重，不扫描历史对话、其他私人目录或全部 Skill。按 `目标 Skill + 观察失败 + 期望行为` 生成指纹；重复候选不得再次写入。

记录字段为：`Status / Target Skill / Evidence Kind / Task Ref / Observed Failure / Expected Behavior / Evidence Refs / Reuse Scope / Proposed Authority / Validation / Sensitivity Check`。

## 5. 确定性记录器

`scripts/skill-learning-ledger.py` 是离线载体：`enable / disable / status / record / list` 保持原有 candidate-only 行为；`lookup / revise-pattern / record-impact` 用于显式维护。它不联网、不扫描历史、不自动确认或晋升经验、不修改仓库或 Codex Skills，也不执行 Git。

`record` 必须显式传入当前任务引用、证据类型、证据引用、观察失败、期望行为、复用范围、建议权威落点、验证方式和 `public-safe` 检查。`repeated-failure` 至少需要两个不同证据引用。

账本目录权限固定为 `0700`，模式和候选文件固定为 `0600`；记录器拒绝凭证以及带明确标签的身份证、手机号和银行卡号。该检查只作最后一道防线，不能替代调用前脱敏。

### 5.1 存储与修订

复用 `$SKILL_LEARNING_HOME/wise-agent/`，不新建数据库或后台服务：

```text
mode.json                                        原有自动记录开关
records/<skill-id>/<number>-<slug>.md              不改写的原始候选
patterns/<skill-id>/<pattern-id>/<revision>.json   完整问题模式修订
patterns/<skill-id>/<pattern-id>/impacts/          按版本与序号保存的结果
```

修订包含 `status / summary / scope / strategies / counterexamples / record_refs / evidence_refs / reason`。`evidence_refs` 必须非空，其他列表可以为空；`record_refs` 只能指向本 Skill 已存在的候选相对路径。每次显式提交完整修订，不让已失效的旧策略继续作为当前知识；旧观察、旧修订和旧版本结果不删除。重复 `record` 仍只去重，新证据由显式修订纳入，不借机扩张自动记录范围。

示例输入是已脱敏、已人工评审的 `pattern-review.json`，不是模型自行确认的经验：

```json
{
  "status": "active",
  "summary": "交付时遗漏输出契约检查",
  "scope": "有明确输出契约的 Skill 维护任务",
  "strategies": ["只核对本任务明确要求的输出"],
  "counterexamples": ["纯文字任务不需要全仓构建"],
  "record_refs": [],
  "evidence_refs": ["fixture:output-contract-failure"],
  "reason": "Owner 已确认问题与适用范围"
}
```

以下命令从源仓库根目录执行；实际记录必须使用本任务的证据而非示例引用：

```bash
python3 wise-agent/scripts/skill-learning-ledger.py lookup --skill demo-skill
python3 wise-agent/scripts/skill-learning-ledger.py revise-pattern \
  --skill demo-skill --pattern-id output-contract --input pattern-review.json \
  --reviewer skill-owner --sensitivity-check public-safe
```

`lookup --skill` 只读指定 Skill，可加 `--pattern-id` 精确定位；返回当前修订、历史修订和全部已回链结果。目录不存在时返回空结果，不创建目录或修改权限。新修订以独占、原子发布方式写入私有文件，不覆盖旧修订；遇到并发冲突、损坏文件或链接路径时明确失败，不自动覆盖修复。

### 5.2 版本结果回链

源仓库已有的 `scripts/skill-evolution-control.py` 继续管理不可变改动产物和 registry 版本指针。使用该控制器的试验可在 `register` 时传 `--pattern-id`；它在现有 Checker、canary、promote、rollback 动作中记录有序结果，`reject --reason --actor --evidence-ref` 记录人工拒绝。重复注册同一版本不得清空裁决或改绑问题模式。控制器不读写学习目录，也不因此放宽既有验证条件。

已获指定 registry 的回滚授权时，`VERSION_ID` 固定为本次确认要撤回的当前版本，不是 `last_known_good`；完整参数可通过 `python3 scripts/skill-evolution-control.py rollback --help` 查看：

```bash
python3 scripts/skill-evolution-control.py rollback \
  --registry registry.json --expected-current-version "$VERSION_ID" \
  --reason "已确认当前版本违反护栏" --actor skill-owner
```

当前版本与预期不一致时，命令拒绝且不写入 registry；先重新核对变化，不自动替换预期版本重试。回滚后的结果回链仍使用被撤回的 `VERSION_ID`，不要换成恢复后的版本。

每次明确的试验结论后，无论成败，获本地维护授权才显式回链：

```bash
python3 wise-agent/scripts/skill-learning-ledger.py record-impact \
  --skill demo-skill --pattern-id output-contract \
  --registry registry.json --version-id "$VERSION_ID" \
  --reviewer skill-owner --sensitivity-check public-safe
```

回链只读取用户指定的 registry，不打开其中的产物或外部证据引用；保存父版本、改动内容 hash、产物引用及有序结果。重复导入幂等，同一版本和序号的已保存结果不能被重写。原始判断由 Checker、试验与 Owner 提供；回链器不评分、不证明证据真实性，也不把一次正向结果自动改写为永久策略。

版本晋升或回滚只改变该 registry 的指针，不等于修改源仓库或本机安装；学习历史保持不变。要将试验结果转成新的策略、反例或撤回结论，仍需显式修订问题模式。未使用该 registry 的普通 Skill 修改沿用原有流程，不强制新增 canary 或安装验证。

### 5.3 兼容与验证边界

旧 `mode.json` 与候选记录保持兼容，不迁移、不自动关联历史；不带 `pattern_id / outcomes` 的旧 registry 可以继续使用原命令，但回链不会根据最终状态猜造过去的事件。新的带关联版本从明确记录的试验结果开始积累。

`scripts/test-skill-learning-loop.py` 覆盖原始证据保留、模式修订与撤回、拒绝后再试验、晋升与回滚、幂等和文件安全；由 `scripts/validate.sh` 聚合。它只证明离线契约，不证明 Skill 已取得行为收益。没有真实 baseline / candidate 行为评测，不声明任务成功率或模型能力提升。同步脚本不消费此模式库或这些验证门禁。

## 6. 晋升门禁

Owner 确认候选后，人工评审结论为 `confirmed`，candidate 账本文件仍保持 `candidate`，再回到 `code-delivery.md` 生成最小可审查 diff。在 `confirmed` 状态内执行受控改进试验：`失败归因假设 -> 最小候选 diff -> 目标样例 / 邻近 hard-negative / 稳定样例对照 -> 独立 Checker -> Owner 裁决`。基线与候选分别绑定原始输出、配置和证据指纹；Checker 同时寻找替代解释与反证，Owner 最终选择 `promote / reject / supersede`，并写清回退条件与责任人。一次目标样例转绿、发布时间压力或 Agent 自述不能直接晋升。

产品、文档、图形和创意等含主观质量的任务，可先写任务级价值判断卡：`期望效果 / 正向参照 / 不期望效果 / 可接受取舍 / 人工判断点 / 最终 Owner`。它只限定当前任务的评价方向；只有重复出现、可复核且经 Owner 确认的模式，才重新进入 candidate 门禁。

独立验证通过后，Owner 才能在任务证据中裁决为 `promoted`；Git、同步和发布仍需单独授权。

候选涉及隐私、金融、合规、安全、生产上线、权限边界或未来默认行为时，即使证据充分也必须人工确认。无法确定权威落点、验证方式或旧值清除范围时停止晋升。

## 7. 行为评测 Harness 归因与恢复

行为评测同时区分三种状态，不能用一个 `PASS / FAIL` 覆盖：

| 状态 | 含义 | 后续动作 |
| --- | --- | --- |
| `HARNESS_ERROR` | payload 漂移、模型或运行环境不一致、隔离逃逸、启动失败、launcher 与 source 冲突，或轨迹解析器误判。 | 停止评分，保留脱敏失败证据；修正 Harness 后按恢复规则处理。 |
| `BEHAVIOR_OBSERVED` | 单个任务已得到完整响应和原始轨迹；工具可以失败、重试或修正。 | 只记录行为事实，不由 collector 判断 Skill 优劣。 |
| `EVIDENCE_COMPLETE` | 同一 runner/model、source/input digest 和 payload 下的全量成对响应已完成盲化、独立 Judge 与 release gate。 | 才能进入当前 evidence gate 或 Owner 晋升裁决。 |

### 7.1 Collector、Judge 与触发语义

- Collector 只冻结并核对 payload，执行隔离、采集响应与原始轨迹，记录实际 source 读取、工具尝试、退出码和结果；缺响应、缺轨迹、越界读取、模型漂移或输入身份不一致时停止。
- Source-profile 对照必须证明被测来源实际进入模型上下文：可以把授权 source 正文按文件边界直接框入 Maker prompt，也可以要求 Maker 在隔离目录读取并由原始轨迹证明每个声明文件已读。只复制文件、列出路径、执行目录扫描或依赖模型自行发现，不算 candidate source 已加载；发现此类情况标为 `HARNESS_ERROR` 并从零重采。
- Maker 只接收同题用户请求、对应 condition 的授权 source 和固定输出契约；不得接收 acceptance criteria、rubric、release gate、blind label、预期答案或失败归因。criteria 只进入独立 Judge；否则 baseline/candidate 被同一目标答案饱和，不能形成增量证据。
- Judge 的每条评分必须回显 `pair_id` 和 A/B label，collector 按 `(pair_id, label)` 校验唯一性、全集和盲文件绑定后再计分；只要求数组顺序、再由位置推断 pair 的评分不可准入。批量评分出现未知 ID、遗漏、重复或备注串题时标为 `HARNESS_ERROR`，保留未变的 Maker / blind 证据，用新 Judge identity 按 case 或更小的语义完整批次从 0 完整重评；不得复用 partial 或手工搬移分数。
- Collector 回执固定为 `实际 source 读取 | 工具尝试 | 退出码 | 结果 | 原始轨迹指针`；它只记事实，不从 source、case ID 或 arm 推导“应该调用什么工具”，也不把自己的判断写成 Skill PASS / FAIL。
- Collector 不按 case ID、arm、关键词或预期答案复制专业 Skill 的工具触发规则，也不要求工具成功才保存响应。工具是否应调用，回到被测 source 中可观察的语义谓词，例如正式、完整、可评审或触发验证。
- Launcher 只声明入口、允许读取范围、隔离、授权和证明边界；不得成为第二领域权威。工具失败、修正后成功和未调用都作为行为事实保留，由盲化后的 Judge 按任务 criteria 裁决。
- `execution_evidence` 只使用 baseline/candidate 对称、不会泄露 arm 的安全摘要；原始轨迹与 blind key 分开保存，Maker、Judge 和 Owner 不互相替代。

### 7.2 续跑、重采与轨迹归一

- 恢复键至少包含 `payload_sha256 + case_id + trial + condition + runner/model + source/input digest`。这些值完全相同，且响应与原始轨迹均完整可复核时，才允许跳过已完成项继续采集；不得重复请求或补造轨迹。
- Launcher、prompt、任务集、source、允许文件、模型或其它已冻结外发内容发生变化时生成新 payload digest，从零重采；不同 payload 的部分结果不得合并。启动前网络错误或授权审查失败属于 `HARNESS_ERROR`，不产生响应证据。
- 新 payload 需要联网重采时，重新取得覆盖新 digest、模型、目的地和文件白名单的明确授权；旧授权不自动延伸到变化后的外发内容。
- 仅修正离线轨迹解析且未改变外发 payload 时，可以从原始响应与轨迹恢复同一任务。轨迹归一必须检查完成事件、退出码和聚合输出，覆盖直接命令、复合 shell 与交互 shell；不能只看外层命令字符串，也不能摘要掉“先失败、后修正通过”的过程。
- 全量采集前不生成盲评结论；盲评和 release gate 前再次核对当前 source/case digest。任一当前权威已变化时，将本轮标为 stale，不刷新 hash、不覆盖已有证据。
