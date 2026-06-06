# GSD/CAD 编排准入

本文定义 AI Native 流程中对中大型 AI 编码任务的 GSD/CAD 准入判断。它只回答是否需要 GSD Round 0、如何形成 Wave/Atomic Task 候选、哪些缺口阻断 CAD、下一步交给谁；不替代资深架构师的工程任务包、`cad-mode.md` 或 Execution Grant。

## 使用时机

- 用户明确有中大型项目、长任务、上下文衰减、多 Agent / Wave 编排、GSD-like 工作流或 CAD 自动推进诉求。
- 产品上下文包、PRD-Lite、OpenSpec 草案、AI 原型/eval 或 dogfooding 反馈已经出现，需要判断能否进入工程侧 GSD Round 0。
- 用户要求“结合 GSD 与 CAD”“自动推进哪些任务”“按什么顺序交给架构师或 Agent”“Execution Grant 还缺什么”。
- 用户担心大项目被拆散、上下文漂移、多个 Agent 互相覆盖、CAD 被误用于整个 Roadmap。

## 不适用场景

- 只写普通 PRD、产品方案或 Backlog 决策；正文交给 `产品架构专家`。
- 只做架构设计、代码 Review、Bug 修复、测试或生产变更；工程执行交给 `资深架构师`。
- 已经选定单个原子任务并要求判断 CAD Mode 进入门禁；详细规则交给 `senior-software-architect/references/cad-mode.md`。
- 用户要求真实执行 Git、联网、部署、生产数据或不可逆操作；必须另有用户授权和工具层许可。

## 读取后必须产出

- GSD/CAD 编排准入结论：轻量执行、进入 GSD Round 0、只做只读侦察、可形成 CAD 候选，或必须停止补上下文。
- GSD Round 0 缺口：目标、非目标、对象/规则、OpenSpec、owner、写入范围、验证命令、风险确认方和停止条件。
- Wave / Atomic Task 候选：只给候选形态、依赖顺序、owner、写入/只读边界、生产可用能力锚点、事实/推断/待确认边界和验证证据，不写成执行授权。
- CAD 候选缺口：Task ID、写入范围、验证命令、工作区状态、Execution Grant、人工确认点和风险阻断项。
- 下一步 owner：产品专家、资深架构师、代码生成器、人类 owner 或当前流程继续补齐。

## 需要继续读取的 reference

- 产品上下文、PRD-Lite 和 AI 原型交接读 `product-to-engineering-lifecycle.md`。
- OpenSpec、Superpowers、Harness、Agent 权限和多 Agent 治理读 `agentic-engineering-governance.md`。
- 验证矩阵、CR、发布和质量/测试门禁读 `verification-review-release.md`。
- 工程侧大项目任务包、上下文账本、阶段状态和 Wave 执行细则交给 `senior-software-architect/references/ai-large-project-orchestration.md`。
- 单个原子任务的 CAD Mode、Execution Grant 和自动分轮执行细则交给 `senior-software-architect/references/cad-mode.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否进入 GSD Round 0 | 1、2、3 | 不生成完整工程任务包 |
| 拆 Wave / Atomic Task 候选 | 3、4 | 不写 CAD 每轮执行计划 |
| 判断 CAD 候选缺口 | 5、6 | 不把候选当 Execution Grant |
| 产品上下文进入工程 | 7，并回读 `product-to-engineering-lifecycle.md` | 不把 MVP 当工程授权 |
| 流程评审或 CR 前置 | 8、9，并回读 `verification-review-release.md` | 不替代源码级 CR |

## 1. 职责边界

GSD 的目标是交付生产可用能力，不是让 AI 随机推进一组看上去有进展的模拟模块。所有 GSD Round、Wave、Atomic Task 和 CAD 候选都必须回答：它服务哪个真实业务目标，落在哪个生产边界或真实入口，如何由验收种子、测试、CR、发布/回滚条件或人工确认来证明可用。回答不了时，只能做 Round 0 补齐或只读侦察。

工程实现层的额外红线：除了缓存能力、测试替身、fixture、沙盒模拟或明确标注的 demo，业务代码不应提供内存版 Service 实现来冒充生产能力。`InMemoryXxxService`、`FakeXxxService`、`MockXxxService`、Map/List 存储型业务实现或只在进程内保留状态的应用服务，如果进入生产源码路径，必须被标记为阻断项并交给 `资深架构师` 做编码/CR 处理。

事实边界红线：GSD/CAD 候选不得基于无根据猜测、模型脑补、工具总结、外部文章观点或超出用户目标的功能扩张。凡是没有用户目标、来源材料、源码锚点、验收种子或验证证据支撑的内容，只能写入 `推断 / 待确认 / 范围外不做`，不能写成任务、实现、准入结论或授权缺口。

GSD/CAD 在 AI Native 流程中分四层：

| 层级 | 回答的问题 | owner |
| --- | --- | --- |
| AI Native 编排准入 | 是否需要 GSD Round 0、能否形成 Wave/Atomic Task 候选、谁接下一步。 | 本技能 |
| GSD-like 大项目编排 | 什么可以被执行，如何用 Stage/Wave/Atomic Task 和上下文账本保持可恢复。 | `资深架构师` |
| CAD Mode | 已选定的单个原子任务是否可以受控自动推进。 | `资深架构师` |
| Execution Grant | 用户实际授权做什么、能改哪里、能否 Git、何时停止。 | 用户 + 工具权限 |

边界句：

- AI Native 决定“是否进入 GSD/CAD 编排候选，以及下一步 owner”。
- GSD-like 决定“哪些阶段和任务可以被执行”。
- CAD Mode 决定“当前选中的原子任务是否可以自动执行”。
- Execution Grant 决定“本轮实际允许做什么”。

## 2. 准入分级

先按输入成熟度分级：

| 成熟度 | 结论 | 典型动作 |
| --- | --- | --- |
| 想法 / 文章观点 / 工具宣传 | 不进入 GSD/CAD。 | Round 0 补目标、主体、证据、风险、验收。 |
| AI 原型 / eval / dogfooding | 可进入产品到工程交接。 | 补产品上下文包、PRD-Lite 缺口、验收种子。 |
| 产品上下文包 / OpenSpec 草案 | 可进入 GSD Round 0 候选。 | 输出 GSD Round 0 缺口和架构师交接要求。 |
| OpenSpec + Harness 摘要 | 可形成 Wave / Atomic Task 候选。 | 输出 Wave 顺序、任务候选、验证矩阵草案。 |
| 单个原子任务 + 验证命令 + 授权缺口清楚 | 可标记 CAD 候选。 | 交给资深架构师检查 CAD Mode 和 Execution Grant。 |

## 3. GSD Round 0 判断

进入 GSD Round 0 前至少要能回答：

- 业务目标、非目标、成功标准和失败成本是什么。
- 关键对象、状态、规则、异常路径和验收种子是否清楚。
- 生产可用能力是什么：真实业务入口、运行边界、数据/权限/资金/租户影响、发布和回滚要求是否能说明。
- 哪些材料是事实，哪些是推断，哪些需要产品、人类 owner 或专业方确认。
- 是否存在无根据猜测、超出用户目标的功能扩张或 AI 幻觉风险；存在时必须停止在 Round 0。
- 工程写入范围、只读范围、禁止事项和高风险边界是否能初步收敛。
- 验证命令、人工验收方式、CR 前置条件和发布门禁是否有候选。
- 是否需要上下文账本、阶段状态、恢复入口和多 Agent / Wave 编排。

缺任一关键项时，只输出补齐清单，不建议 CAD。

## 4. Wave / Atomic Task 候选

AI Native 只输出候选形态，不替代架构师生成正式任务包：

```text
Wave 0：只读侦察、产品/工程上下文补齐、风险确认、代码库理解结论包。
Wave 1：OpenSpec、公共契约、模型、测试夹具和验证底座。
Wave 2：互不重叠的实现任务、适配器、页面或批处理。
Wave 3：集成验证、CR、发布准备和复盘材料。
```

Atomic Task 候选至少描述：

- 候选 Task ID 或临时编号。
- 目标和非目标。
- owner 候选。
- 写入范围候选、只读范围候选和禁止事项。
- 依赖哪个 Wave、哪个契约或哪个任务完成。
- 生产可用能力锚点：真实业务入口、受影响的生产路径、上线/回滚边界或人工确认方。
- 事实依据、推断依据、待确认项和范围外不做；没有依据的内容不得进入任务目标或实现建议。
- 验收场景和验证证据候选。
- 是否可能成为 CAD 候选，以及阻断原因。

同一 Wave 的候选任务不得共享同一写入文件、公共契约、状态机或测试夹具；如果共享，必须拆顺序或交给架构师重切。

## 5. CAD 候选缺口

CAD 候选只写“候选”和“缺口”，不写成执行授权。判断时逐项检查：

- 是否只有一个已选定的 Task ID 或阶段切片。
- 写入范围是否足够窄，且能区分只读参考。
- 是否有可运行或可替代的验证命令。
- 是否有停止条件：规格不清、验证失败、权限不足、风险升级、用户中断。
- 是否已经区分事实、推断、待确认和范围外不做；未区分时不能进入 CAD。
- 是否有工作区状态检查，能识别用户已有改动。
- 是否需要 Git、联网、依赖安装、Docker/服务启动、数据库迁移或生产操作；需要时必须列入 Execution Grant 缺口。
- 是否涉及资金、权限、租户、审计、合规、风控、结算或生产行为；涉及时必须设置人工确认点。

结论只能是：

- `不是 CAD 候选`：缺 OpenSpec、任务边界、验证或风险确认。
- `CAD 候选但缺授权`：任务边界和验证清楚，但缺 Execution Grant 或工具层权限。
- `可交给架构师检查 CAD Mode`：已有单个原子任务、验证和授权草案，下一步读 `cad-mode.md`。

## 6. Execution Grant 缺口

AI Native 可以指出 Execution Grant 缺什么，但不能替用户授权。缺口通常包括：

- 任务范围：Task ID、目标、有效期限。
- 写入范围：允许修改的目录、文件、测试和生成物。
- 验证范围：命令、人工验收、失败处理。
- Git 策略：是否允许 `git add` / `git commit`，不含 push、PR、merge 或部署。
- 外部访问：是否允许联网、安装依赖、启动服务、访问外部 API。
- 禁止事项：生产数据、密钥、真实支付/资金通道、不可逆操作。
- 停止条件：何时暂停、何时交还用户、何时回滚或转人工。

如果用户只说“继续”“按建议推进”“自动跑起来”，只能视为流程意向，不是 Execution Grant。

## 7. 交接给架构师

交接给 `资深架构师` 时，应形成一页式准入包：

```text
GSD/CAD 编排准入结论:
输入成熟度:
是否需要 GSD:
GSD Round 0 缺口:
建议 Wave:
Atomic Task 候选:
CAD 候选缺口:
Execution Grant 缺口:
质量/测试门禁:
代码库理解结论包:
事实边界:
下一步 owner:
停止条件:
路由:
```

路由写法：

- 需要工程侧大项目编排：交给 `senior-software-architect/references/ai-large-project-orchestration.md`。
- 需要单个任务 CAD 门禁：交给 `senior-software-architect/references/cad-mode.md`。
- 需要测试策略、TDD 或补测试：交给 `senior-software-architect/references/testing.md`。
- 产品语义仍不足：回到 `产品架构专家` 的产品上下文包或 PRD-Lite。

## 8. 质量 / 测试门禁联动

GSD/CAD 准入必须同时给出质量门禁位置：

- OpenSpec 规定测什么业务事实。
- 产品专家提供验收种子和不可代码化的人工验收边界。
- 资深架构师设计测试分层、TDD 切入点、补测试和测试代码 CR。
- 本技能编排测试矩阵、验证顺序、CR 前置条件、失败回退和残余风险交接。

没有验证矩阵或测试结果交接路径时，不建议进入 CAD。

## 9. 反模式

- 把整个 Roadmap、GSD 计划或 Wave 清单当成 CAD 授权。
- 只因为项目大，就强制创建完整 GSD 文件体系。
- 只因为用户说“继续”，就默认允许 Git、联网、部署或生产操作。
- 把 AI 原型、MVP、PRD、产品上下文包或 AI Native 准入结论当成 Execution Grant。
- 把无根据猜测、模型脑补、工具总结、外部文章观点或超出用户目标的功能扩张写成 GSD Wave、Atomic Task、CAD 候选或实现建议。
- 让 AI 随机推进模拟模块、mock 流程、无业务入口 demo、空服务骨架或看上去可用的样子货，并把它当成 GSD 进展。
- 只检查页面能打开、接口能返回假数据或测试桩能跑通，却没有回链真实业务入口、验收种子、生产边界和发布/回滚条件。
- 把内存版业务 Service、Map/List 存储实现、Fake/Mock 服务或进程内状态当成生产实现；缓存、测试替身、fixture 和沙盒模拟必须隔离在对应边界内。
- 在 AI Native 中复制 CAD 每轮 Pick / Red / Green / Review / Refactor / Verify / Record 细则。
- 让多个 Agent 同时写同一文件、同一公共契约、同一状态机或同一测试夹具。
