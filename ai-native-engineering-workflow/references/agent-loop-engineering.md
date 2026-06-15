# Agent Loop Engineering

本文定义 AI Native 流程中的统一 Loop 设计与治理方式。Loop 不是更长的 Prompt，也不是无条件自动执行；它是围绕目标、状态、计划、动作、观察、判断、验证、预算、停止和人工接管组织起来的可审执行循环。

核心纲要：**Build the loop, stay the engineer**。AI Native 工程师的高杠杆工作不是一轮轮提示 Agent，而是设计一个能读取状态、调用 Agent、检查结果、决定下一步、保存记忆并在关键边界停下来的工程循环。Loop 可以提高推进速度，但不能替代人的理解、责任和关键判断。

AI Native 对外只推荐一个主机制：**AI Native Engineering Loop**。GSD、CAD、Goal、Harness 和 Grant 不再作为同级模式暴露，而是 Loop 内部层：

| 内部层 | 作用 |
| --- | --- |
| Goal | 定义为什么做、做到什么算完成、预算 / 时间盒、停止条件和交接要求。 |
| GSD / Wave | 定义大项目分几波做、任务顺序、依赖和提交切片。 |
| CAD / Atomic | 定义单个原子任务如何受控执行、验证、回写和停止。 |
| Harness | 定义谁做、按什么顺序做、能改哪里、怎么验证、怎么交接。 |
| Grant | 定义当前真实授权范围，不能由 Loop 自行扩大。 |

## 使用时机

- 用户提到 Agent Loop、Loop Engineering、`/goal`、`/loop`、auto mode、后台 Agent、持续编排、多 Agent 监督、定时执行或“让 Agent 自己写 Prompt”。
- 用户希望把 GSD + Goal、Plan Grant、Wave、CAD 或质量门禁压缩进一个可持续推进的执行循环。
- AI 编码已经能生成代码，但缺少反馈、验证、预算、停止条件、恢复入口或交接证据。
- 需要判断某个自动化线程、定时任务、监控、Review Agent 或多 Agent 编排是否可以进入 AI Native 工作流。
- 用户要求把 AI 工作流 Loop、Agent 闭环工程或后台 Agent 做到生产可用，而不是只靠手工 Prompt、定时任务或看上去会跑的自动化。
- 用户明确提到“不是提示 AI，而是设计循环”“人设计 loop、loop 调用 agent、agent 执行、loop 检查并决定下一步”“Build the loop, stay the engineer”。
- 用户要求把 Loop 用到真实项目编码任务，例如“按 Loop 跑代码任务”“实际项目编码 Loop”“GSD + Goal + Loop 编码推进”“让 Agent 按任务计划持续改代码并验证”。
- 用户希望减少 GSD、CAD、Goal 多模式选择成本，把它们统一成只读理解、产研交付、验证发布或知识回流 Loop。
- 需要把重复执行经验沉淀为 Skill、reference、fixture 或脚本，而不是每轮重新写 Prompt。
- 用户要求反馈闭环成熟度、L2/L3/L4/L5、验证簇、不变量验证、生产重放、变异 / 对抗测试或证明“测试通过后系统没有变坏”。

## 不适用场景

- 只优化一段 Prompt、只写普通 PRD、只做单次代码修改或单个源码级 CR；按对应 Skill 处理。
- 目标、范围、验收、写入边界或验证命令不清楚时，不设计 Loop；先回到 Round 0、Goal 卡、OpenSpec 或 Harness。
- Git、联网、依赖安装、生产、密钥、部署、不可逆操作、高风险资金 / 权限 / 合规任务不能因为放进 Loop 就默认授权。
- 外部文章、工具宣传、`/goal`、`/loop` 或 auto mode 只作为方法线索；当前工具是否可用必须按当前会话和官方来源重新核验。

## 读取后必须产出

- 一份 Loop 准入结论：不进入 Loop / 只读理解 Loop / 产研交付 Loop / 验证发布 Loop / 知识回流 Loop / 必须人工主导。
- 一份最小 Loop 契约：Loop Profile、Goal、状态载体、计划层、决策输入、可调用 Skill / 工具、允许动作、禁止动作、反馈源、验证者、预算、最大轮次、无进展检测、停止条件、恢复入口、交接物和人类理解检查。
- 一份授权策略：只读、计划内低风险执行、Plan Grant、Wave Grant、CAD Grant、Codex 替我审批通道或显式确认。
- 一份反馈与验证设计：测试、lint、CR、源码锚点、用户反馈、eval、发布监控或人工验收如何进入下一轮。
- 一份状态与失败回写设计：状态载体选什么，验证失败、需求不清、边界冲突、授权不足、连续无进展时回写到哪里。
- 一份生产可用 Loop 门禁：自动化心跳、隔离执行、Skill 上下文、连接器权限、Maker / Checker 解耦、可复现状态、观测审计、人工接管、发布/回滚、理解债控制和责任 owner。
- 面向真实代码库时，必须额外产出 Coding Loop Contract：任务 ID、代码写入范围、只读范围、失败测试 / 验收样例、实现顺序、验证命令、独立 Checker、状态回写位置、提交切片、回滚方式和停止条件。
- 面向高风险业务 Loop 时，必须额外产出 Verification Cluster Gate：业务不变量、验证簇 ID、证据类型、生产重放边界、独立 Checker、预算 / CI 分层、置信度、状态回写和停止条件。
- 一份知识回流判断：哪些重复动作应沉淀为 Skill / reference / fixture / script，哪些只是一次性探索。

## 需要继续读取的 reference

- OpenSpec、Superpowers、Harness、权限边界和多 Agent 治理读 `agentic-engineering-governance.md`。
- GSD/CAD 内部层、Wave、Atomic Task、Plan Grant 和授权边界读 `gsd-cad-admission.md`。
- Goal 目标层、状态、预算 / 时间盒、Ledger 和 GSD / CAD / Spec 关联读 `goal-composition.md`。
- 代码交付反馈、Spec 回写、独立验证、CR 减负和指标读 `code-delivery-closed-loop.md`。
- 验证矩阵、质量门禁、CR、发布和复盘读 `verification-review-release.md`。
- 具体 CAD 每轮执行细节回到 `senior-software-architect/references/cad-mode.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否需要 Agent Loop | `1. Loop 边界`、`2. 最小契约`、`2A. Loop 组件清单` | 不直接写执行计划 |
| 设计 `/goal` / `/loop` / auto mode 准入 | `2. 最小契约`、`5. 授权与工具边界` | 不把工具能力当授权 |
| 统一 GSD / CAD / Goal 为 Loop | `3. 内部层映射`，再读 `goal-composition.md` 和 `gsd-cad-admission.md` | 不把内部层重新暴露成多个入口 |
| 提升代码交付闭环 | `4. 反馈与验证`，再读 `code-delivery-closed-loop.md` | 不只优化生成速度 |
| 跑真实项目编码 Loop | `4C. 实际项目编码 Loop`，再读 `code-delivery-closed-loop.md`、`verification-review-release.md` 和架构师 `testing.md` | 不让 Loop 直接无约束改代码 |
| 做反馈闭环成熟度 / 验证簇准入 | `4D. 反馈闭环成熟度与验证簇`，再读 `verification-review-release.md` 和架构师 `testing.md` | 不把覆盖率或测试数量当事实 |
| 控制成本与停止 | `6. 预算和停止条件` | 不允许无限循环 |
| 绑定 Plan Grant 与 Loop 预算 | `5. 授权与工具边界`、`6. 预算和停止条件` | 不让授权无限期有效 |
| 设计失败回写路径 | `4. 反馈与验证`、`6A. 失败回写` | 不靠换 Prompt 硬跑 |
| 让 Loop 生产可用 | `7. 生产可用 Loop 门禁`、`7A. 价值指标与理解债`，再读 `code-delivery-closed-loop.md` 和 `verification-review-release.md` | 不把能自动跑当能上线 |
| 做知识回流 | `8. Skill 是复用单位` | 不复制文章或工具宣传 |

## 1. Loop 边界

Agent Loop 回答：在一个目标下，Agent 如何反复读取状态、决定下一步、执行动作、吸收反馈、验证结果，并在满足条件时停止或交接。

最小模型：

```text
Goal -> State -> Plan -> Act -> Observe -> Decide -> Verify -> Stop / Handoff
```

边界：

- Goal 定义目标和完成线。
- GSD 定义分波计划和任务顺序。
- CAD 定义单个原子任务的受控执行子循环。
- Harness 定义执行契约。
- Plan Grant / Execution Grant 定义实际允许做什么。

Loop 不能替代 Goal、OpenSpec、Harness、测试、CR、发布审批或用户授权。没有状态载体、反馈源和停止条件的“自动执行”，不是可用 Loop。

生产可用 Loop 不是“少写 Prompt”，而是把一个可复现、可验证、可接管的小型工程系统装到 AI Native 流程里。可迁移的结构是：自动化提供心跳，隔离工作区承载并发执行，Skill 注入项目上下文，连接器接入真实工具链，Maker / Checker 解耦交付与验证，状态载体落盘保存进度和断点。缺任一关键件时，Loop 只能按候选或只读模式处理。

工程师在 Loop 中保留五项责任：

- 定义目标、非目标、业务不变量和成功标准。
- 设计状态载体、反馈源、验证者、预算和停止条件。
- 审查关键结果，能解释为什么做、改了什么、证据在哪里、风险是什么。
- 控制权限边界、成本、并发隔离、发布和回滚。
- 把反复有效的上下文沉淀为 Skill、reference、fixture 或脚本。

如果 Loop 只让人类持续点同意，却无法复述目标、状态、证据和风险，它不是工程自动化，而是认知外包。

## 2. 最小契约

Loop 契约建议写成短卡：

```text
Loop ID:
Loop Profile: 只读理解 / 产研交付 / 验证发布 / 知识回流
关联 Goal:
内部层: Goal / GSD-Wave / CAD-Atomic / Harness / Grant
触发条件:
状态载体:
计划层:
决策输入:
调用 Skill / 工具:
允许动作:
禁止动作:
反馈源:
验证者:
预算 / 时间盒 / 上下文预算:
最大轮次:
无进展检测:
停止条件:
恢复入口:
交接物:
知识回流位置:
授权策略:
生产可用门禁:
人类理解检查:
```

四类 Profile：

| Profile | 典型用途 | 默认动作 |
| --- | --- | --- |
| 只读理解 Loop | 代码库阅读、设计-代码对齐、工具准入、事实边界检查。 | 只读、输出理解包和缺口，不写文件。 |
| 产研交付 Loop | 产品专家到架构师的端到端交付、大项目分波、真实代码任务推进。 | 先补 Goal / GSD / Harness，再按授权进入 CAD 原子子循环。 |
| 验证发布 Loop | 测试矩阵、CR、发布门禁、监控、回滚、复盘。 | 先收集验证证据，再判断准出、回退或交接。 |
| 知识回流 Loop | Skill、reference、fixture、脚本、用户指南和 source-map 回流。 | 只沉淀已验证经验，不复制外部文章原文或工具宣传。 |

真实项目编码 Loop 额外字段：

```text
Coding Loop Contract:
任务 ID / 关联 Goal / Wave:
代码写入范围:
只读范围:
失败测试 / 验收样例:
TDD 顺序:
实现限制:
验证命令:
独立 Checker:
状态回写位置:
提交切片:
回滚 / 撤销方式:
停止条件:
高风险业务不变量:
验证簇 ID:
验证证据类型:
验证簇置信度:
生产证据是否可用:
```

准入判断：

- 缺 Goal、成功标准或验收种子时，不能进入执行 Loop。
- 缺状态载体时，Loop 只能停留在单轮任务，不适合跨轮推进。
- 缺反馈源时，Loop 只会放大猜测和错误。
- 缺验证者时，Loop 不能形成交付证据。
- 缺最大轮次、无进展检测或预算上限时，Loop 不能自动运行。
- 缺隔离执行、落盘状态、观测审计、人工接管或回滚路径时，Loop 不能声明生产可用。

状态载体优先级：

- `Goal Ledger`：跨轮记录目标、当前状态、验证证据、预算消耗、阻塞和下一 owner。
- `GSD 状态账本 / Wave plan`：记录 Wave、Task、依赖、提交切片和阶段进度。
- `Harness Plan`：记录 owner、写入范围、验证命令、顺序、停止条件和恢复入口。
- `OpenSpec tasks / AC / SDD`：记录业务事实、验收标准、实现约束和漂移项。
- `verification matrix / CR report`：记录测试、lint、源码锚点、Review 发现和准出证据。
- `git commit message / task summary`：仅作为已验证切片的历史证据，不能单独承担状态载体。

没有明确状态载体时，Loop 只能做单轮分析或执行；不能跨轮承诺持续推进。

### 2A. Loop 组件清单

设计可运行 Loop 时，至少判断下列组件是否存在；缺失组件必须写进 Loop 缺口，而不是用更长 Prompt 补偿。

| 组件 | 作用 | 不足时的处理 |
| --- | --- | --- |
| Automations | 提供定时、事件或手动触发入口，例如 CI 失败、Issue 更新、监控告警或每日巡检。 | 没有自动化时只能做手动单轮 Loop，不承诺持续运行。 |
| Worktrees / 隔离工作区 | 让多个 Agent 或多轮执行互不踩文件，支持回滚和并发。 | 没有隔离时限制为只读、单任务或人工串行执行。 |
| Skills | 注入项目规则、历史约定、构建方式、模板和踩坑经验。 | 没有 Skill 时先补上下文包或规则索引，不让 Agent 猜项目约定。 |
| Plugins / Connectors | 接入 Git、Issue、CI、监控、数据库、测试环境或协作系统。 | 没有连接器时只使用当前可验证材料，不编造外部状态。 |
| Sub-agents / Maker-Checker | 分离执行者和检查者，形成不同视角的复核。 | 没有 Checker 时不能把 Agent 自述当准出证据。 |
| Memory / 状态载体 | 保存完成了什么、下一步是什么、失败原因、证据和断点。 | 没有落盘状态时不能跨轮持续推进。 |

组件不是越多越好；每个组件都必须服务 Goal、验证或停止条件。工具能力、Agent 数量、PR 数量和自动化频率都不能替代业务价值。

## 3. 内部层映射

旧说法 `GSD + Goal + Loop`、`GSD/CAD`、`CAD + Goal` 统一映射为产研交付 Loop：

```text
Goal 固定目标和完成线
-> GSD 固定 Wave 和任务顺序
-> Harness 固定 owner、写入范围、验证和交接
-> Loop 固定每轮状态、计划、动作、观察、判断、验证和停止
-> Plan Grant / CAD Grant 固定低风险默认推进边界
```

使用要求：

- 每个 Loop 必须服务一个 Goal 或子 Goal，不能为了“让 Agent 跑起来”而创建。
- 每个 Wave 可以有 Loop，但 Wave Loop 不能跨 Wave 自动扩大写入范围。
- 每个 CAD 原子任务本质上是产研交付 Loop 中的受控子循环；具体执行细节交给架构师 `cad-mode.md`。
- Plan Grant 只能让范围内低风险本地任务按计划推进；不能扩展到 Git push、联网、生产、密钥、部署或高风险业务。
- Plan Grant 必须绑定 Loop 预算、最大轮次、无进展检测和失败回写位置；授权不能比 Loop 状态更长寿。
- Loop 交接必须更新 Goal Ledger、验证矩阵、任务状态或等价材料。
- 用户仍可说“进入 GSD 产研协同研发流程”“GSD + Goal 按任务计划推进”“做 GSD/CAD 准入”，但输出应显示为产研交付 Loop，而不是要求用户继续在多模式之间选择。

## 4. 反馈与验证

Loop 的可信度取决于反馈和验证，不取决于执行轮数。

反馈源可以是：

- 测试、编译、lint、静态检查、类型检查、契约测试。
- CR 发现、源码锚点、影响模块、入口路径和调用关系。
- 产品验收种子、用户反馈、eval 样例、发布监控和告警。
- Spec / AC / OpenSpec 漂移检查和上下文过期检查。

验证规则：

- 生成者不能自己给自己签字；准出证据必须可复核。
- Agent 可以解释验证结果，但不能把自述“已完成”当证据。
- 连续失败时，不只是换 Prompt；应回写 Spec、AC、测试、Harness 或项目规则。
- Review Agent 只能初筛，不能替代架构师、产品 owner、安全或发布责任人。

### 4A. 失败回写路径

Loop 失败后先回写事实源，再决定是否继续：

- 测试、编译、lint 或契约验证失败：回写测试策略、验证矩阵、Harness Plan 或工程任务包。
- 需求、验收或产品边界不清：回写产品上下文包、PRD-Lite、AC 或产品 owner 待确认项。
- 系分、接口、数据、状态机或模块边界冲突：回写 OpenSpec、SDD、ADR 或架构师系分。
- 授权不足、写入范围不清或工具要求额外审批：回写 Plan Grant / Execution Grant。
- 连续两轮无新增证据、缺口不收敛或同类错误重复：回写 Goal Ledger，并暂停交给人类 owner。
- 工具输出无法回链源码、测试或用户材料：标为待确认，不得写成结论或执行依据。

### 4B. Maker / Checker 解耦

生产 Loop 中，写代码或改文档的执行者与验收者必须分离：

- Maker 负责提出方案、做最小变更、补测试或更新状态。
- Checker 负责基于 Spec / AC / Harness / 测试 / 源码锚点复核结果，不能只复述 Maker 的结论。
- Checker 可以是独立 Agent、架构师、产品 owner、测试门禁或 CI，但必须有不同输入视角和可复核证据。
- 关键链路只在值得购买第二意见时拉起独立 Checker；成本、token、耗时和人类 Review 带宽也必须进入预算。
- 如果 Checker 无法复述“改了什么、为何可接受、证据在哪里、还剩什么风险”，不能进入合并或发布判断。

### 4C. 实际项目编码 Loop

实际项目编码 Loop 不是“让 Agent 一直改代码”，而是把一个明确的 Goal / Wave / Task 变成可反复验证、可停止、可接手的工程执行循环。它适用于已有代码库、已有目标和可运行验证命令的场景；具体代码设计、TDD、补测试、实现和源码级 CR 仍交给 `资深架构师`。

准入条件：

1. 有可追溯的业务目标、验收样例或 OpenSpec / PRD-Lite / Engineering Handoff Card。
2. 有单一任务 ID、代码写入范围、只读范围和不得修改的边界。
3. 行为变更优先有失败测试、验收样例或可复现缺陷；确实无法先写测试时，必须记录原因、替代验证和残余风险。
4. 有可执行的验证命令，至少覆盖编译 / 测试 / lint / 契约检查中的相关项。
5. 有独立 Checker 或 CR 门禁，且 Checker 使用源码锚点、测试输出和验收标准复核。
6. 有状态回写位置，例如 Goal Ledger、GSD Wave、Harness Plan、OpenSpec tasks、验证矩阵或任务文档。
7. 有提交切片和回滚方式；不得把多个无关 Loop 混进同一个提交候选。

推荐运行路径：

```text
Read-only scout
-> Spec / AC gap check
-> RED / reproduce
-> Implement smallest change
-> Verify
-> Independent Checker / CR
-> State writeback
-> Commit candidate / Stop
```

编码 Loop 的硬规则：

- 没有失败测试、验收样例或可复现证据时，不直接进入生产代码修改。
- Maker 不能用“我已验证”替代测试输出、源码锚点、CR 结论或人工验收。
- Loop 每轮只处理一个提交切片；发现 scope drift 时回写任务状态并停止。
- 连续两轮无新增证据、同一错误重复、验证命令不可运行或 Checker 无法理解改动时停止。
- 测试通过但无法映射到业务验收、OpenSpec、Harness 或用户目标时，不能声明完成。
- 业务代码不得为了让 Loop 跑通而引入无业务入口 demo、内存版业务 Service 或模拟生产能力。

输出模板：

```text
Coding Loop 准入结论:
任务 ID / Goal:
当前阶段: 只读侦察 / RED / Implement / Verify / Checker / Handoff
代码写入范围:
只读范围:
失败测试 / 验收样例:
实现限制:
验证命令:
Checker 输入:
状态回写位置:
提交切片:
停止条件:
下一 owner:
```

### 4D. 反馈闭环成熟度与验证簇

反馈闭环成熟度先做分级，不直接加更多测试：

- **L2**：有基础单测、集成、E2E、覆盖率或冒烟；能发现一部分回归，但语义保护弱。
- **L3**：AI 能按 Spec / Harness / TDD 修复、补测试、回写失败；仍依赖人类判断业务事实。
- **L4**：围绕高风险业务不变量建立不变量支撑的验证簇，验证同一事实的多类证据互相校验。
- **L5**：生产证据、实现图谱、选择性失效和自动再生形成闭环；L5 只能作为目标架构，不得写成当前已具备能力。

核心规则：测试通过、覆盖率提高和 bug 下降都只是证据，不是事实本身。L4 先选 3-5 个业务不变量，不为全系统铺满验证簇；生产重放样本只能作为证据，不能反向定义需求。

Verification Cluster Gate:

```text
成熟度判断: L2 / L3 / L4 / L5 候选
业务不变量:
验证簇 ID:
场景测试:
属性 / 变形测试:
历史回归入口:
生产重放样本:
有限变异 / 对抗检查:
置信度:
来源:
独立 Checker:
预算 / CI 分层:
状态回写位置:
停止条件:
```

停止条件：业务 owner 未确认不变量、生产样本缺少脱敏 / 授权、验证簇无法回链需求或源码、CI 预算超过收益、同一失败重复两轮、Checker 不能解释证据含义，均停止并回写 Goal Ledger、验证矩阵或 Harness。

## 5. 授权与工具边界

`/goal`、`/loop`、auto mode、定时任务、后台 Agent、多 Agent 调度和 Codex 替我审批都只能作为运行方式或低风险审批通道，不能自行创造授权。

默认边界：

- 只读 Loop 可以读取工作区内相关文件、查引用、生成理解包和建议。
- Plan Grant Loop 可以在任务计划内做低风险本地读写、测试、lint、文档/Skill 更新和状态回写。
- CAD Loop 只覆盖一个已选定原子任务的 Red / Green / Review / Verify 本地动作。
- Git stage / commit 必须由 Grant 明确写清；push、PR、merge、部署、联网、依赖安装和生产操作必须显式确认。
- 工具要求额外审批时，工具权限优先于流程设计；不得绕过 sandbox、审批或项目规则。

Plan Grant 与 Loop 预算绑定的最低字段：

```text
适用 Goal / Wave / Task:
状态载体:
反馈源:
验证者:
预算 / 时间盒:
最大轮次:
无进展检测:
失败回写位置:
预算耗尽处理:
授权失效条件:
```

如果 Grant 没有这些字段，只能作为计划内低风险执行候选，不能升级为持续自动推进。

## 6. 预算和停止条件

Loop 必须有硬停止条件：

- 最大轮次达到上限。
- 连续两轮没有新增验证证据、状态变化或缺口收敛。
- token、费用、时间盒、上下文预算或验证成本达到上限。
- 目标、范围、OpenSpec、Harness、写入边界或授权出现冲突。
- 测试、lint、编译、CR 或人工验收失败，且继续修改会掩盖真实问题。
- 触发 Git、联网、生产、密钥、部署、不可逆操作或高风险业务边界。
- 出现用户中断、owner 变化、上下文漂移、工具输出无法回链源码或证据。
- 人类 owner 无法理解变更逻辑、责任边界或发布后兜底方式。

停止不是失败。停止后应输出状态、证据、阻塞原因、下一 owner、恢复入口和需要用户确认的最小问题。

## 7. 生产可用 Loop 门禁

生产可用 Loop 的准出必须同时回答“能不能运行、能不能证明、出事谁接、怎么停下”。最小门禁：

- **真实目标**：关联真实业务目标、OpenSpec / AC、生产边界和发布条件；不交付模拟模块、无入口 demo 或内存版业务 Service。
- **可复现状态**：每轮写入状态载体，记录 round id、输入材料、动作、变更范围、验证结果、预算消耗、失败原因和下一 owner；不能只依赖会话上下文。
- **隔离执行**：并发 Agent、后台任务或候选修复必须在独立 worktree、分支、目录或等价沙盒中执行，避免互相覆盖。
- **上下文固化**：项目规约、历史坑点、禁止事项和验证命令进入 Skill / reference / AGENTS / CONTEXT / Harness，而不是每轮临时手写长 Prompt。
- **权限最小化**：连接器、MCP、CI、Issue、Slack、数据库或 Staging API 只按任务需要授权；联网、安装、生产、密钥、部署、Git push、PR、merge 和不可逆操作仍显式确认。
- **独立验证**：Maker / Checker 解耦；准出证据必须来自测试、lint、静态检查、契约验证、CR、用户验收、发布监控或人工 owner 复核。
- **观测 / 审计**：保留可追溯日志、验证命令、产物链接、失败回写、成本 / token / 时间盒、审批记录和残余风险。
- **发布 / 回滚**：进入生产前必须有灰度、feature flag、dry-run、回滚步骤、告警指标和人工兜底 owner；无法回滚时必须升级人工主导。
- **理解债控制**：人类 owner 必须能读懂入口路径、影响模块、关键调用关系、边界变化和验证证据；Loop 不能用“自动完成”掩盖理解缺口。
- **停止与接管**：预算耗尽、连续无进展、验证失败、权限越界、工具输出无法回链证据或 owner 无法兜底时，暂停并交接。

生产可用 Loop 输出模板：

```text
Loop ID:
生产目标 / 非目标:
运行环境 / 隔离方式:
状态载体 / round id:
自动化心跳:
Skill / 上下文资产:
连接器 / 权限:
Maker:
Checker / 独立验证:
观测 / 审计:
发布 / 回滚:
人工接管 owner:
理解债检查:
预算 / 停止:
恢复入口:
```

只有这些字段具备可执行证据时，才能把 Loop 标记为可生产化；字段不齐时输出缺口和下一 owner，而不是放大自动执行。

### 7A. 价值指标与理解债

Loop 的价值不看“跑了多少轮、开了多少 PR、用了多少 Agent、是否能手机审批”，而看真实交付质量和团队理解是否提高。

优先指标：

- 合并率、一次通过率、返工率、缺陷率、回滚率、线上告警率。
- CR 成本、平均修复时间、验证等待时间、阻塞交接次数。
- 用户价值、业务目标完成度、验收样例命中率和生产反馈。
- 团队理解程度：owner 是否能复述目标、入口路径、变更范围、关键取舍、证据和残余风险。
- 知识回流质量：重复问题是否沉淀为 Skill、fixture、脚本、测试、OpenSpec、ADR 或项目规则。

认知外包红线：

- 人类 owner 只剩“同意 / 通过 / 合并”动作，但说不清 Loop 为什么继续或停止。
- Maker、Checker、测试和发布全由 AI 自述串起来，缺少独立证据和人工责任人。
- PR 数量上升，但返工、缺陷、回滚、CR 负担或理解债同步上升。
- 状态只存在于会话里，没有落盘到 Goal Ledger、Harness、验证矩阵、Issue 或任务文档。
- 团队为了让 Loop 跑通而降低验收、扩大模拟实现或绕开真实业务入口。

## 8. Skill 是复用单位

Loop 里可复用的单位应是 Skill、reference、fixture、script 或项目规则，而不是每轮重新写 Prompt。

沉淀顺序：

- 重复的判断流程进入 Skill / reference。
- 可机械验证的问题进入脚本、fixture、lint、测试或 CI。
- 项目事实和历史坑点进入项目 `AGENTS.md`、`CONTEXT.md`、ADR、OpenSpec 或等价位置。
- 用户长期偏好只有在授权后进入 `~/.skill-learning/`，不进入仓库或安装目录。

不新增顶层 Skill 的默认判断：

- 如果只是 AI Native 流程中的一个执行循环，留在本 reference。
- 如果是架构师具体代码执行、TDD、CR 或 CAD，每轮细节回到 `资深架构师`。
- 如果是产品反馈、PRD 或验收种子，回到 `产品架构专家`。
- 只有跨项目反复出现、边界独立、产物稳定、验证方式明确时，才评估独立 Skill。

## 9. 输出模板

Loop 准入卡：

```text
结论:
关联 Goal:
Loop 类型:
状态载体:
可调用 Skill / 工具:
允许动作:
禁止动作:
反馈与验证:
预算 / 最大轮次:
无进展检测:
停止条件:
授权策略:
生产可用门禁:
交接物:
下一 owner:
```

Loop 复盘卡：

```text
Loop ID:
执行轮次:
完成证据:
失败 / 阻塞:
消耗预算:
是否触发停止:
回写位置:
下一步:
```

## 10. 反模式

- 把 Loop 当成更高级的 Prompt，缺少状态、反馈、验证和停止条件。
- 把工程师降级为 Prompt 操作者或审批点击者，缺少目标、边界、证据和风险理解。
- 为了减少审批，把 Git、联网、生产、密钥、部署或不可逆操作塞进默认 Loop。
- 用执行轮数、生成代码量、PR 数量代替交付证据。
- Loop 发现失败后继续堆提示词，不回写 Spec、AC、测试或 Harness。
- 多个 Loop 同时写同一模块、同一契约、同一状态机或同一测试夹具。
- 把外部工具的 `/goal`、`/loop`、auto mode 或后台 Agent 能力写成当前会话默认能力。
- 不把 Loop 写成无条件自动授权。
- Loop 只会继续，不会停；或停下后没有状态、证据、owner 和恢复入口。
