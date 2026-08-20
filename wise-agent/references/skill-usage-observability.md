# Skill 使用观测

本文定义知止者本地使用观测的精度、数据边界、启停、汇总和学习回流边界。它只生成使用证据，不新增运行模式，不评价业务正确性，也不自动修改 Skill。

## 使用时机

- 用户显式要求开启、关闭、检查或汇总知止者的 Skill 使用记录。
- 需要比较完整 reference 与章节级 JIT 的真实 token、加载状态和验证结果。
- 需要为 Skill 路由或内容优化准备可复核的成本与使用证据。

## 不适用场景

- 未取得用户明确授权时自动开启 Hook、OTel、本地持久化或修改 `~/.codex/config.toml`。
- 用 token 数、加载次数或 Agent 自述证明 Skill 命中正确、任务成功或改进应晋升。
- 扫描 transcript、历史对话、用户私有目录、客户资料、生产数据或密钥。

## 读取后必须产出

- 当前模式、数据目录、记录范围和数据精度。
- 可用事实、静态估算、独立效果评测和缺失数据。
- 继续试点、形成 candidate 或停止观测的门禁结论。

## 按任务读取索引

| 任务 | 优先读取 |
| --- | --- |
| 开启或配置观测 | `1. 证据与精度`、`2. 授权与数据边界`、`3. 启停` |
| 查看本地用量 | `1. 证据与精度`、`4. 汇总与解释` |
| 评估 JIT 价值与实际生效 | `4. 汇总与解释`、`4A. JIT 价值评测契约`、`6. 验收与停止` |
| 评估上下文压缩价值 | `4. 汇总与解释`、`4A. JIT 价值评测契约`、`6. 验收与停止` |
| 用证据改进 Skill | `4. 汇总与解释`、`5. 评测与回流`、`6. 验收与停止` |

## 1. 证据与精度

| 需要回答的问题 | 证据源 | 精度 |
| --- | --- | --- |
| Skill 是否注入、线程启用 / 保留 / 截断数量、每轮 token | Codex OTel 的 `codex.skill.injected`、`codex.thread.skills.*`、`codex.turn.token_usage` 和 `response.completed` | 精确遥测；以当前 Codex 实际字段为准 |
| 哪个 reference、哪些标题被 JIT 加载 | `read-reference-sections.py` 的 JSON 结果和 `PostToolUse` Hook | 文件、标题、内容 SHA 精确；token 为静态估算 |
| Skill 是否命中正确、是否提高任务质量 | 已标注 fixture、人工反馈、真实验证和同条件 baseline / candidate 对比 | 独立效果评测 |

原生遥测只能给出线程或轮次 token，不能把全部 token 精确归因到单个 Skill。报告必须分开标注“精确遥测”“静态估算”“独立效果评测”，不得伪造单 Skill 精确消耗。

上述 Codex OTel 与 Hook 字段按官方文档于 `2026-08-14` 核验；平台升级后必须先跑受控试点，不把旧字段当长期稳定协议。

## 2. 授权与数据边界

默认数据根为 `$SKILL_USAGE_HOME/wise-agent`，未设置时使用 `~/.skill-usage/wise-agent`。只有执行 `skill-usage-observability.py enable` 后才接受 Hook 或 OTel 事件；目录权限为 `0700`，文件权限为 `0600`。

允许保存：由脱敏事件字段生成的确定性事件 ID、时间、会话 / 轮次 ID、模型、事件状态、Skill 名、reference 相对路径、标题路径、内容 SHA、token 数或估算区间、工作区路径哈希。相同事件 ID 的 Hook / OTLP 重放在写入前去重；事件 ID 不包含正文或原始载荷。

不得保存 prompt、回答正文、源码正文或原始遥测载荷；不得保存绝对工作区路径、Hook 的完整命令与工具输入输出。OTLP 接收器只监听 `127.0.0.1`，拒绝超过 `2 MiB` 的请求，只接收 JSON；成功响应使用 OTLP JSON 的空响应对象 `{}`。

启用记录不代表授权联网、安装依赖、修改 Codex 配置、执行 Git、删除历史数据或写学习回流 candidate。观测账本和 `$SKILL_LEARNING_HOME` 候选账本必须隔离。

## 3. 启停

先验证脚本，再显式启用：

```bash
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py --self-test
python3 ~/.codex/skills/wise-agent/scripts/test_skill_usage_observability.py
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py enable
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py config
```

`config` 只打印候选配置，不修改 `~/.codex/config.toml`。审查配置、信任 Hook、启动本地接收器和重启 Codex 都是独立动作，必须另有明确授权。获准后接收 OTel：

```bash
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py serve
```

停止新增记录：

```bash
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py disable
```

`disable` 不删除既有记录、不停止外部启动的进程，也不回滚 Codex 配置。

## 4. 汇总与解释

```bash
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py status
python3 ~/.codex/skills/wise-agent/scripts/skill-usage-observability.py report
```

`status` 分开显示持久化开关与接收器健康；`enabled` 只代表允许写入，只有 `receiver.health=live` 才证明指定端口上的本地接收器可达。

OTel `Delta` 只累加去重后的事件；`Gauge` 与 `Cumulative` 按时间戳和维度取最新值。缺少 `timeUnixNano` 或 Sum / Histogram 缺少 `aggregationTemporality` 时拒绝入账，避免把未知语义伪装成精确统计。报告遇到最后一条未完整写入的 JSONL 时保留此前记录，并在 `integrity.rejected_tail_records` 计数；中间损坏仍失败并指出文件与行号。

成本比较必须固定任务集、模型、推理强度、工具环境和验证门槛。`codex.skill.injected` 只证明注入发生；命中率和误触率必须来自人工或 fixture 标签。加载更少不等于效果更好，JIT 静态估算只有同时满足真实 token 未恶化、任务质量未下降时才可支持优化结论。

### 4A. JIT 价值评测契约

完整 reference 与章节级 JIT 必须使用同一任务集、runner、模型、推理强度、工具环境、试验次数和验证门槛。每次 JIT 运行先保留 `read-reference-sections.py` 返回的 `status`、`source`、`source_sha256`、`heading_path` 和选择 / 扩大原因；`ambiguous`、`not-found` 或高风险语境不足时按脚本结果扩大读取，不把强行节省算作命中。

JIT 价值必须沿同一条上下文成本链比较，不能用局部输出压缩率替代端到端结果：

| 层级 | 最小证据 | 解释边界 |
| --- | --- | --- |
| 局部输出 | reference / 工具输出字符、静态 token 估算 | 只说明本次返回变短，不证明总成本下降 |
| 行动路径 | `search`、`read`、`test`、`test_failure`、`retry`、`native_replay` 次数 | 识别因漏线索或不确定性产生的补偿动作；单轮相关性不冒充因果 |
| 上下文寿命 | 各轮 / 各阶段 cached、non-cached input token 与重复携带情况 | 只使用平台真实可得字段；缺失时标为未知，不反推伪精确寿命 |
| 最终结果 | 总 token、可得时的耗时 / 成本、最终产物、确定性验证和独立盲评 | 质量与安全门禁优先于成本收益 |

成本侧使用同轮 OTel token 作为精确遥测，章节 token 估算只作解释；效果侧保留最终产物、确定性验证结果和独立盲评。runner 可以在 response JSONL 中成对提供脱敏的 `execution_evidence` 字符串列表，格式只允许 `tool:<id>:<status>`、`validation:<id>:<status>` 或 `artifact:<sha256>:<status>`，其中 status 为 `passed`、`failed`、`completed` 或 `skipped`；两侧缺一即拒绝。该字段只传确定性摘要，不得写入 condition、prompt、回答 / 源码正文、绝对路径、密钥或原始遥测载荷。

成本链明细不得进入盲评 response JSONL。评测 runner 只能在盲评完成后，用独立脱敏记录按 `case_id + trial + condition` 关联 `stage / turn`、可得 token 字段、`tool_output_chars`、上述动作计数、`fallback_reason`、`artifact_sha256` 和 `quality_report_ref`；不得记录命令、prompt、回答 / 源码正文、绝对路径或原始工具输出。缺少稳定关联键、任一侧产物指纹或同条件数据时，结论只能是 `insufficient`。

裁决只允许：`adopt` 表示 JIT 选择正确、真实总 token 下降、补偿动作未抵消收益、正确性 / 安全性不回退且最终产物通过同一门槛；`restricted` 表示只在已声明任务分层内重复成立，并绑定适用范围与原生回退；`reject` 表示质量 / 安全回归或端到端成本恶化，局部输出变短不能抵消；`insufficient` 表示只有静态估算、关键字段缺失、配对条件不一致或方差尚无法裁决。原生遥测无法精确归因到单个 Skill 时，只报告轮次级差异，不反推伪精确的 Skill ROI，也不照搬外部材料的固定阈值。

## 5. 评测与回流

观测事件不是学习 candidate。只有出现重复场景、明确纠偏、fixture / validator 失败或可复核验证证据，才按 `skill-learning-backflow.md` 形成最小候选；同一 runner、模型和参数下用 `scripts/evaluate-skill-behavior.py` 做 blind 对比。

Owner 确认、Checker 复核、Skill diff、Git、同步和发布继续使用各自门禁；观测不得自动触发任何一步。

## 6. 验收与停止

首次受控试点至少包含一轮显式调用 `$wise-agent` 和一轮不应命中的对照任务。JIT 配对任务还应覆盖明确标题、歧义查询、跨章节依赖和高风险红线四类，使用相同重复次数观察方差；未形成当前项目基线前不预设收益阈值。原始 Hook / OTLP 请求只能在进程内或临时目录出现，不得进入账本或仓库。

JIT 或压缩输出缺少预期线索、为空、截断或 schema 漂移时，立即原生回放并记录 `fallback_reason`；若候选输出后仍重复执行其声称替代的同类搜索或读取，该次计为新增步骤而非节省。最终验收必须回读原始产物或权威来源，不以压缩摘要准出。

出现下列任一情况立即停止试点：关键字段缺失或 schema 漂移、会话 / 轮次无法稳定关联、任何正文或绝对路径落盘、Hook / 接收器引入可观察错误或延迟，或正确性验证回归。单次 JIT token 未下降不触发立即停止；完成预声明重复次数并结合方差与补偿动作裁决，端到端成本稳定恶化时判为 `reject`，仍无法裁决时判为 `insufficient`。

仓库 fixture 只证明本地解析、脱敏和汇总契约，不证明当前 Codex Desktop 的真实事件 schema；完成一次真实受控试点前，运行状态只能是 `PILOT_PENDING`。

## 官方时效来源

- [Codex advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)，核验日期：`2026-08-14`。
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)，核验日期：`2026-08-14`。
