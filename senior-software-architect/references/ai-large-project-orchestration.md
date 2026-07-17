# AI 大项目编排工作流

本文定义类似 GSD 的大项目 AI 编码编排能力：用持久化上下文、阶段计划、原子任务、Wave 依赖、验证闭环和交接记录，支撑中大型项目的持续稳定推进。它是本技能的内建流程，不依赖外部 GSD 工具，也不复制外部命令体系。

## 使用时机

- 用户明确有中大型项目、长任务、多阶段实现、跨模块改造、AI 编码连续推进或多 Agent 协作需求。
- 主会话开始出现上下文衰减：目标、决策、阻塞项、禁止事项、验证证据散落在长对话里。
- 任务需要分阶段推进，每阶段都有设计、计划、执行、验证、Review 和恢复入口。
- 用户希望用 Codex thread、automation、goal、side panel 或 artifact 把工作从单次对话推进为持续工作流。
- 用户要求类似 GSD、规格驱动开发、阶段状态、并行 Wave、任务恢复或 AI 编码项目管理能力。
- 用户从 AI Native 的 Agent Loop、`/goal`、`/loop`、auto mode、后台 Agent 或 GSD + Goal + Loop 准入进入工程侧，需要把持续编排落成可恢复、可验证、可停止的 Wave。

## 不适用场景

- 3 分钟内可完成的小修、简单文案、格式、注释、单文件明确修改。
- 快速 MVP demo、一次性原型或探索性试验，除非用户明确要求保留可恢复状态。
- 需求不清、产品语义不清、验收标准缺失时，不直接进入执行编排；先回 OpenSpec、产品设计或系分补齐。
- 未获得用户明确授权时，不执行 Git 写操作、自动提交、外部联网、部署、生产数据操作或不可逆动作；但 GSD 规划必须输出提交切片和建议 commit message，供阶段收口或用户确认后执行。
- 不安装、不调用、不复刻外部 GSD 工具；需要真实工具集成时必须另走供应链安全审查。

## 读取后必须产出

- 是否启用大项目编排，以及启用理由：上下文衰减、跨模块复杂度、阶段依赖或多 Agent 需求。
- 项目上下文账本位置、写入范围、只读范围、阶段状态和恢复入口。
- 阶段切分、Wave 依赖、原子任务计划、验证矩阵、Loop 反馈/预算/停止条件和人工确认点。
- 本轮允许执行什么、不允许执行什么、如何暂停、如何恢复、如何收口。

## 需要继续读取的 reference

- AI 协作总纲读 `ai-assisted-engineering.md`。
- 端到端 AI Native 产品到研发流程、角色编排和 GSD/CAD 准入判断先由 `wise-agent/references/planning-execution-admission.md` 编排；本文件只消费已确认的 GSD/CAD 编排准入结论，并在已经进入工程侧大项目编排后细化任务包、上下文账本、Wave 和验证矩阵。产品侧上下文缺口回到 `product-architecture-expert/references/ai-native-product-context.md`。
- 生命周期、验证命令和 Git 边界读 `workflow.md`。
- CAD Mode、Execution Grant、自动分轮推进和自动提交边界读 `cad-mode.md`。
- Java 代码修改读项目本地规范、`wind-coding-conventions` 通用层和 `coding-review-deep-dive.md`；Wind/Nobe 专项按依赖或上下文启用；测试读 `testing.md`。
- 生产、数据、安全或外部依赖读 `production-readiness.md`、`negative-constraints.md` 和对应专项 reference。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否启用大项目编排 | 1、2 | 不先写项目状态文件 |
| 初始化项目账本 | 3、4、5 | 不展开执行 Wave |
| 规划阶段和原子任务 | 6、7 | 不进入 CAD Mode 细节 |
| GSD-CAD 组合判断 | 先消费 `wise-agent/references/planning-execution-admission.md` 的准入结论，再读 8 和 `cad-mode.md` | 不对整个大项目直接开 CAD |
| GSD + Goal + Loop 进入工程 | 先消费 `wise-agent/references/delivery-execution-control.md` 和 `planning-execution-admission.md`，再读 6、7、10 | 不把 Loop 当整个 Roadmap 授权 |
| AI Native 编排结论进入工程 | 8A，并消费 `wise-agent` 或产品侧交接材料 | 不把业务 MVP 直接当 CAD 授权 |
| 多 Agent / Wave 执行 | 7、9、10 | 不跳过验证 |
| Codex automation / goal / artifact 协作 | 10、11、12 | 不把平台能力当授权 |
| 暂停、恢复或跨会话继续 | 12 | 不依赖聊天记忆 |
| 收口、Review、阶段提交和交付 | 13、14 | 不把提交建议当 Git 授权 |

## 1. 能力定位

大项目编排解决的是“长任务持续稳定推进”，不是“让 AI 更自由”。它把 AI 编码从主会话即兴输出，转成项目内可恢复、可评审、可验证的执行系统：

```text
OpenSpec 定目标
-> 项目账本保上下文
-> 阶段计划控范围
-> 原子任务控写入
-> Wave 控并行
-> Loop 控反馈和停止
-> 验证矩阵控质量
-> 交接记录控恢复
```

核心收益：

- 把目标、约束、决策、阻塞、验证证据从长对话迁移到可版本化材料。
- 让每个执行任务都有清晰输入、写入范围、验证方式和完成条件。
- 让多 Agent / 多轮推进在依赖关系下并行，不在同一职责范围里互相踩踏。
- 让持续编排每轮都有反馈、验证、预算、无进展检测和停止条件。
- 让会话中断、上下文清理或阶段切换后可以恢复，而不是从头解释。

AI Native 产品到工程的端到端链路由 `wise-agent` 维护，GSD/CAD 编排准入由 `wise-agent/references/planning-execution-admission.md` 产出。进入本文件时，只保留工程侧最小链路：

```text
AI Native 交接结论
-> OpenSpec / context ledger / verification matrix
-> GSD Stage / Wave / Atomic Task
-> Agent Loop 候选 / 反馈源 / 停止条件
-> CAD 候选 / Execution Grant 缺口
```

产品上下文包回答“这个产品候选是否值得工程化、工程化必须保留哪些业务事实”。知止者持续持有端到端目标与状态，并按需装载产品、工程和验证能力。GSD-like 计划层回答“哪些阶段和任务可以被执行”，CAD Mode 只回答“当前选中的原子任务是否可以自动执行”。状态载体、能力和执行机制不得互相替代。

## 2. 启用门槛

满足任一条件即可建议启用，但仍需结合成本判断：

| 信号 | 启用理由 |
| --- | --- |
| 任务跨多个模块、服务、接口、状态机或测试层级 | 需要阶段和依赖控制。 |
| 一次对话难以承载完整目标、设计、计划和执行细节 | 需要上下文账本。 |
| 用户希望多轮自动推进、暂停恢复或长期持续开发 | 需要阶段状态和恢复入口。 |
| 需要多个 Agent 或并行探索/实现/验证 | 需要 Wave 依赖和交接规范。 |
| 需要后台 Agent、`/goal`、`/loop` 或持续编排 | 需要状态载体、反馈源、验证者、预算和停止条件。 |
| 修改涉及公共契约、资金、权限、生产行为、数据迁移或安全 | 需要人工确认点、验证矩阵和回滚边界。 |
| 需要 thread automation、goal 或 side panel artifact 持续迭代 | 需要明确 verifier、停止条件、状态位置和人工确认点。 |

不满足启用门槛时，用轻量 OpenSpec + 普通工作流即可；不要为了“流程完整”创建额外文档。

## 3. 项目上下文账本

默认优先复用项目已有文档，例如 `docs/`、OpenSpec、系分、ADR、任务清单、测试矩阵、项目本地 `AGENTS.md`。如果没有合适位置，可建议创建一个任务专属目录，例如：

```text
docs/ai-orchestration/<initiative-id>/
  00-open-spec.md
  01-context-ledger.md
  02-roadmap.md
  03-state.md
  04-harness-plan.md
  05-verification-matrix.md
  handoffs/
```

创建前必须说明：

- 文件用途和是否会提交到版本库。
- 哪些内容会写入，哪些内容不得写入。
- 是否包含敏感信息、客户数据、生产配置、密钥或内部不可公开材料。
- 是否由用户确认、AI 维护，还是只作为本轮临时产物。

文件职责：

| 文件 | 目的 | 必须包含 |
| --- | --- | --- |
| `00-open-spec.md` | 固定目标和验收。 | 目标、范围、非目标、规则、接口、数据、验收、风险。 |
| `01-context-ledger.md` | 固定项目事实和决策。 | 术语、约束、架构决策、禁止事项、外部依赖、待确认项。 |
| `02-roadmap.md` | 固定阶段和里程碑。 | 阶段目标、依赖、交付物、退出条件。 |
| `03-state.md` | 固定当前状态。 | 当前阶段、已完成、阻塞、最新验证、下一步、恢复入口。 |
| `04-harness-plan.md` | 固定执行协作契约。 | Owner、Task ID、写入范围、只读范围、依赖顺序、Wave、验证命令、停止条件、交接和恢复入口。 |
| `05-verification-matrix.md` | 固定验证要求。 | 测试、编译、lint、Review、人工验收、回归和发布门禁。 |

如果项目已有等价文档，不重复创建；只在 `03-state.md` 或现有任务文件中留下入口索引。

Harness Plan 最小模板：

```text
Task ID:
任务目标:
Owner:
所属阶段 / Wave:
写入范围:
只读范围:
依赖顺序:
禁止事项:
验收场景:
验证命令:
停止条件:
Loop 反馈源:
Loop 预算 / 最大轮次 / 无进展检测:
交接要求:
恢复入口:
CAD 候选: 是/否，原因:
Execution Grant 关联: 无/待确认/已确认；提交切片: summary_only / commit_after_verified_task / explicit_confirm；建议 commit message:
```

Harness Plan 必须体现一句话原则：OpenSpec 规定要做什么，Superpowers 规定怎么高质量地做，Harness 规定谁做、按什么顺序做、能改哪里、怎么验证、怎么交接。若这些字段无法填清，只能进入 Round 0 补齐，不进入执行 Wave。

可选本地检查：

```bash
senior-software-architect/scripts/check_harness_plan.py --kind gsd-wave --file docs/ai-orchestration/<initiative-id>/04-harness-plan.md
```

脚本只做结构完整性检查；通过不代表可以进入 CAD Mode，也不代表用户已授权 Git、联网、部署或生产操作。

## 4. 初始化流程

初始化不直接改代码，先完成 Round 0：

```text
识别项目和技术栈
-> 收集现有权威文档与代码入口
-> 明确目标、范围、非目标和风险等级
-> 生成或更新上下文账本
-> 切分阶段和里程碑
-> 确认验证命令和人工确认点
```

Round 0 产出：

- 项目事实：仓库、模块、技术栈、构建命令、测试命令、关键入口。
- 业务事实：目标、主体、对象、状态、规则、验收标准。
- 工程边界：允许写入、只读参考、禁止触碰、外部依赖、配置和数据边界。
- 风险分级：低/中/高风险以及对应确认点。
- 初始化结论：可进入规划、需要补产品/系分、需要用户确认或不适合编排。

## 5. 阶段拆分

阶段按业务能力、风险边界和验证闭环切分，不按“看起来工作量差不多”切分。

阶段模板：

```text
阶段编号：
阶段目标：
业务/工程价值：
前置依赖：
写入范围：
非目标：
验收场景：
验证命令：
人工确认点：
退出条件：
```

阶段原则：

- 先打通最小可验证主链路，再扩展异常、兼容、运营和边界能力。
- 公共契约、数据模型、状态机和测试底座优先稳定。
- 每阶段必须有退出条件；不能用“差不多完成”进入下一阶段。
- 阶段间必须说明依赖，不允许后置阶段倒逼前置契约重写。

## 6. 原子任务包

原子任务包是执行者的最小输入单元。每个任务包必须足够明确，能独立 Review、独立验证、必要时独立回退。

任务包模板：

```text
Task ID:
目标：
所属阶段：
所属 Wave：
Owner：
写入文件：
只读参考：
依赖顺序：
允许动作：
禁止动作：
实现约束：
验收场景：
验证命令：
停止条件：
完成条件：
交接要求：
恢复入口：
回滚提示：
CAD 候选：是/否，原因：
Execution Grant 要求：
```

原子任务包红线：

- 不允许一个任务包同时改公共契约、数据迁移、业务实现和前端接入，除非它们无法独立验证且用户确认。
- 不允许写入文件为空或过宽，例如“整个 src 目录”。
- 不允许只有实现动作，没有验证命令和完成条件。
- 不允许任务之间写入同一文件而仍放在同一 Wave。
- 不允许没有交接要求和恢复入口的任务包进入跨会话或多 Agent 执行。

## 7. Wave 依赖编排

Wave 是并行边界，不是速度口号。

```text
Wave 0：只读侦察、规格补齐、测试底座和风险确认。
Wave 1：稳定公共契约、模型、接口边界、测试夹具。
Wave 2：互不重叠的业务实现、适配器、页面或批处理任务。
Wave 3：集成验证、回归修复、文档和发布准备。
```

Wave 规则：

- 同一 Wave 内任务必须互不重叠、无顺序依赖、可独立验证。
- 跨 Wave 依赖必须写清楚：依赖哪个 Task ID、哪个文件、哪个契约或哪个测试。
- Wave 完成后先更新 `03-state.md` 和验证矩阵，再进入下一 Wave。
- 如果出现冲突、验证失败归因不清、需求变更或公共契约漂移，暂停当前 Wave，重新规划。

## 8. GSD-CAD 双层协议

端到端 GSD/CAD 准入、GSD Round 0 缺口、Wave/Atomic Task 候选和 Plan Grant / Execution Grant 缺口先由 `wise-agent/references/planning-execution-admission.md` 输出。本节只说明资深架构师拿到准入包后，如何把工程侧大项目编排和 CAD Mode 组合起来。

GSD-like 编排管大盘，CAD Mode 跑单元。大项目编排负责定义“哪些任务可以被执行”，CAD Mode 负责判断“某一个任务是否可以自动执行”。不得对整个大项目直接开启 CAD。

双层协议：

```text
GSD Round 0
-> 固化 OpenSpec / context ledger / roadmap / verification matrix
-> 拆 Stage / Wave / Atomic Task
-> 选择一个原子任务包或阶段切片
-> 检查 CAD 门禁
-> 确认 Plan Grant / Execution Grant
-> CAD 自动分轮执行
-> 回写 state / verification matrix / handoff
-> 进入下一个任务包或暂停
```

职责边界：

| 层次 | 负责什么 | 不能做什么 |
| --- | --- | --- |
| GSD-like 编排 | 固定大项目目标、阶段、Wave、任务包、上下文账本、验证矩阵和恢复入口。 | 不授予自动执行权限，不把计划当作 Git、联网、部署或生产操作授权。 |
| CAD Mode | 在单个任务包或阶段切片内按 Pick -> Red -> Green -> Review -> Refactor -> Verify -> Record 推进。 | 不消费整个 Roadmap，不跨越写入范围，不处理未选定任务包。 |
| Plan Grant / Execution Grant | 明确本轮 CAD 的写入范围、验证命令、Git 策略、禁止事项、人工确认点和撤销方式。 | 不扩大为跨阶段、跨 Wave、跨任务链的永久授权。 |
| Verification | 决定是否继续、暂停、回滚、人工确认或进入下一任务包。 | 不用“看起来完成”替代测试、lint、Review 或人工验收。 |

硬规则：

- GSD defines what can be executed.
- CAD decides whether it may be executed automatically.
- Plan Grant / Execution Grant decides what is actually allowed.
- Validation decides whether it may continue.

CAD 候选任务必须同时满足：

- 已有明确 Task ID、所属阶段、所属 Wave、写入范围、只读参考、验收场景和验证命令。
- 不与同一 Wave 中其他任务写入同一文件、同一契约、同一状态机或同一公共测试夹具。
- 不需要尚未确认的业务口径、兼容策略、迁移路径、资金/权限/生产规则取舍。
- 已检查工作区状态，能区分用户已有改动和本轮 CAD 改动。
- 已准备 Plan Grant / Execution Grant；涉及 Git 写操作、外部访问、依赖安装、Docker/服务启动、数据库迁移或生产行为时必须显式列出。
- 已准备提交切片；默认 `summary_only`，若要求阶段提交或自动提交，必须在 Plan Grant / Execution Grant 中写明 `commit_after_verified_task`、提交范围、验证条件和失败回退。

CAD 输出必须回写阶段状态、验证矩阵和 handoff：完成内容、验证结果、失败/跳过原因、残余风险、Git 处理结果、下一任务建议。只有原子任务包满足 CAD 门禁时，才建议进入 CAD；门禁不满足时，回到本文件的 Round 0、阶段拆分或任务包补齐。

## 8A. 消费 AI Native 编排交接结论

当输入来自业务方或产品侧 AI 生成原型、MVP、Product Builder 方案、业务 dogfooding 结果或“放下 PRD”的流程改造时，先确认是否已有 `wise-agent` 或 `产品架构专家` 给出的产品侧交接结论。没有 Hardened Candidate 或产品侧交接条件时，不进入 GSD/CAD，只回到产品上下文补齐。

进入 GSD Round 0 时，本文件只消费以下工程输入：

- 产品侧交接结论：业务 owner、目标/非目标、对象状态、流程规则、验收种子、风险确认方和停止条件。
- AI Native 编排结论：当前成熟度、下一步 owner、GSD/CAD 编排准入结论、是否进入 OpenSpec、是否需要 Harness/GSD、GSD Round 0 缺口、Wave/Atomic Task 候选、CAD 候选缺口和 Plan Grant / Execution Grant 缺口。
- 已确认材料入口：PRD-Lite、产品上下文包、OpenSpec 草案、原型/eval 证据、待确认项。

架构侧把这些输入转成：

- OpenSpec 的目标、范围、非目标、业务规则、接口/数据约束和验收场景。
- Context ledger 的术语、对象、规则、MVP 证据、已知限制、禁止事项和待确认项。
- Roadmap 的阶段切片和退出条件。
- Harness Plan 的写入范围、只读范围、Owner、Wave、任务包和停止条件。
- Verification matrix 的 TDD、契约、集成、运营、数据、风险和人工验收证据。

进入 CAD 前必须再次确认：已选定单个 Task ID 或阶段切片，写入范围、验证命令、Git 策略、人工确认点和停止条件明确。产品上下文包、Hardened Candidate、AI Native 编排结论或 GSD Roadmap 都不是 Plan Grant / Execution Grant；只有 AI Native 输出 `Plan Grant: Active` 时，才默认推进任务计划内低风险本地动作。

反模式：

- 业务方能跑通 MVP，就直接让 CAD 改代码。
- 产品侧只给页面和按钮，没有对象、状态、规则、验收和风险 owner。
- 架构师绕过 `wise-agent` 和产品侧交接结论，直接按原型补接口和表结构。
- 把 PRD、GSD 计划或产品上下文包当成自动提交、联网、部署或生产操作授权。

## 9. 执行协议

执行前检查：

- 工作区状态是否清楚，是否存在用户未提交变更。
- 当前 Wave 是否已确认。
- 任务包是否有明确写入范围、验证命令、完成条件。
- 是否涉及高风险操作、Git 写操作、外部联网、生产配置或数据操作。
- 若任务包标记为 CAD 候选，是否已继续读取 `cad-mode.md` 并形成 Plan Grant / Execution Grant。

执行中：

- 一次只处理一个任务包，除非工具明确支持隔离并行。
- 每个 diff 必须回指 Task ID、OpenSpec 条款或验收场景。
- 发现任务包不完整、代码事实冲突或验证不可运行，停止并更新状态，不硬做。

执行后：

- 运行任务包规定验证。
- 更新交接记录和阶段状态：改了什么、验证结果、残余风险、下一步；完成、阻塞、失败或需要用户确认。
- 更新提交切片：建议提交单元、文件范围、验证证据、建议 commit message；若 Grant 明确允许 `commit_after_verified_task`，验证通过后按切片执行本地 `git add` / `git commit`，失败或混入用户改动时降级为 `summary_only` 并暂停说明。

## 10. 验证矩阵

验证矩阵按“任务 -> 证据”组织：

| Task ID | 验收场景 | 验证方式 | 命令/证据 | 状态 | 残余风险 |
| --- | --- | --- | --- | --- | --- |

验证层级：

- 单元测试：纯业务规则、值对象、策略、工具类。
- 流程测试：应用服务、事务、状态流转、副作用。
- 契约测试：API、DTO、错误码、消息体、配置项。
- 架构测试：依赖方向、模块边界、禁止引用。
- 集成验证：数据库、MQ、外部端口替身、启动上下文。
- 人工验收：业务确认、合规确认、视觉/交互确认、运营流程确认。

未验证不得标记完成；无法验证必须说明原因、替代证据和残余风险。

## 11. Codex 持续协作边界

当大项目编排使用 Codex app 的 thread、automation、goal、side panel 或 artifact 时，先把平台能力转成工程协议：

| 能力 | 可用方式 | 编排约束 |
| --- | --- | --- |
| Durable / pinned thread | 作为长期工作空间，保留任务链上下文和交付 loop。 | 不把 thread transcript 当权威规格；关键事实仍写入 OpenSpec、阶段状态或项目已有文档。 |
| Steering / queuing | 用户执行中纠偏，或排入下一任务。 | 每次新指令都要判断是否改变范围、风险、Wave 依赖或验证矩阵。 |
| Thread automation | 定期回到同一 thread 检查反馈、刷新 artifact 或继续监控。 | 必须说明频率、触发条件、停止条件、输出位置和是否需要用户批准；不能默认发消息、上传、部署或修改生产。 |
| Scheduled automation | 从固定 workspace 定期开始重复任务。 | 适合周期性报告或定期仓库检查；必须把 workspace、验证命令、输出形态和失败处理写清楚。 |
| Goal | 给长期任务一个可判断的 finish line。 | 必须包含 outcome、success criterion、verifier、停止条件和失败处理；弱目标必须先改写。 |
| Side panel / artifact | 就地审查页面、文档、deck、表格、PDF、静态 HTML 或数据 app。 | 交付前应真实预览、渲染、截图或运行相应验证；用户标注必须回写到当前任务包或 Review 结论。 |
| Shared written context | 把跨会话关键上下文写到显式材料。 | 优先复用项目文档、AGENTS、OpenSpec、ADR、任务状态；不得写入个人长期偏好、私有对话轨迹、私有 vault 或无关目录。 |

持续协作红线：

- 不把 voice/transcript 的原始表达直接当规格；先转成目标、假设、待确认、验收和验证。
- 不把 automation、goal 或 queue 当成 Git、联网、外部消息、桌面 GUI、生产操作或长期记忆授权。
- 不为了“持久化”制造无意义文件变动；没有可复用事实、决策、阻塞或验证证据时不更新状态材料。
- 涉及 Slack、Gmail、Calendar、浏览器登录态、桌面 GUI、客户数据、生产配置或敏感信息时，必须先说明权限、数据边界和人工确认点。

## 12. 暂停与恢复

暂停前必须更新 `03-state.md` 或等价状态文件：

```text
当前阶段：
当前 Wave：
最近完成 Task：
未完成 Task：
阻塞项：
已运行验证：
失败验证：
用户待确认：
恢复入口：
下一步建议：
```

恢复时先读：

1. 项目本地 `AGENTS.md`。
2. `00-open-spec.md` 或等价规格。
3. `03-state.md` 或等价状态。
4. 当前 Wave 的任务包和验证矩阵。
5. `git status` 和当前 diff。

恢复后不要凭记忆继续；先复述当前状态、风险和下一步，再执行。

## 13. Git 与版本化边界

大项目编排鼓励原子可追溯，且必须在规划阶段给出提交切片；是否实际执行 Git 写操作由 Grant 和工具权限决定。

- 默认输出建议提交单元和建议 commit message；每个建议提交应对应一个或少数紧密相关 Task ID，并能独立理解、验证和回滚。
- 只有用户明确要求并在 Plan Grant / Wave Grant / CAD Grant 中写明 `commit_after_verified_task` 或等价策略，才在任务验证通过后执行本地 `git add` / `git commit`；提交前必须检查 `git status` 和 `git diff`，确认只包含授权范围内且已验证的变更，混入用户已有改动、验证失败、跳过验证或范围不清时不得提交。
- `git push`、创建 PR、merge、rebase、reset hard、强制覆盖历史和部署永远不包含在 GSD 阶段提交默认策略内，必须单独显式确认；不把外部 GSD 的“每个任务自动提交”当成本仓库默认行为。
- 状态文件是否纳入版本库由项目规则和用户确认决定；包含敏感信息时不得提交。

## 14. 收口与 Review

阶段收口必须输出：

- 完成的 Task ID 和交付物。
- 已运行验证和结果。
- 未完成任务、阻塞项、延期项。
- 行为影响、兼容性影响、数据/生产/安全风险。
- 是否满足阶段退出条件。
- 下一阶段建议或停止条件。

大项目最终收口必须回到 `workflow.md` 的 Review/Ship：验证证据、残余风险、回滚/监控、Git 边界和需要用户判断的事项都要明确。

## 15. 外部 GSD 来源边界

微信公众号文章《让AI编程从"越写越烂"到"持续稳定输出"：GSD工作流-适合中大型项目的精准框架。》可作为上下文衰减、持久化状态、子 Agent 分工、Wave 依赖、原子可追溯和 Git 版本化意识的公开参考来源。

本技能只吸收可迁移方法：

- 上下文从长对话迁移到项目内状态材料。
- 长任务按阶段循环推进。
- 大任务拆成原子任务包。
- 同一 Wave 内任务互不重叠且可独立验证。
- 每个任务有交接、验证和回滚提示。

本技能不吸收：

- GSD 命令体系、文件模板、XML 示例、动图、截图、工具宣传语或作者表达。
- 默认创建 `PROJECT.md`、`STATE.md`、`ROADMAP.md`、`CONTEXT.md` 等固定文件名。
- 自动提交、自动部署、自动外部联网或绕过用户授权的执行习惯。
- 未审查外部工具代码、脚本、Hook、插件或安装流程。

## 16. Codex 官方团队文章来源边界

微信公众号文章《Codex 官方团队：如何把 Codex 用到极致》可作为 Codex app 运行时协作方式的公开参考来源，用于增强 thread、voice、steering/queuing、tool reach、automation、goal、side panel、artifact 和 shared written context 的工程编排意识。

该文章不作为 OpenAI 官方当前产品能力、模型、工具可用性或路线图承诺依据；涉及 Codex 当前能力、工具状态、产品规则或官方承诺时，必须核验 OpenAI 官方文档或当前会话工具状态。

本技能只吸收可迁移方法：

- 把 thread 视为长期工作空间，但把关键事实写入显式材料。
- 用 voice/transcript 捕获粗糙想法，再提炼成规格和验收。
- 用 steering/queuing 支持过程中纠偏和后续任务排队，并重新校准范围。
- 用 automation/goal 支持持续推进，但必须绑定 verifier、停止条件和人工确认点。
- 用 side panel/artifact 将产物审查留在同一工作 loop，并要求真实预览或验证。
- 用 shared written context 保存决策、阻塞、owner、日期和有用链接，避免仅依赖聊天记录。

本技能不吸收：

- 不把 Codex app 功能清单写成当前会话一定可用的工具能力。
- 不把该微信文章当作 OpenAI 官方当前能力、产品可用性、模型、工具或路线图承诺。
- 不默认创建 pinned thread、automation、goal、vault、外部 connector 或长期记忆。
- 不默认访问 Slack、Gmail、Calendar、浏览器登录态、桌面 GUI、外部 API 或私有数据。
- 不复制文章示例、提示语、目录结构、作者表达、平台宣传语或未核验的未来能力。
