# CAD Mode 与 Execution Grant

本文定义资深架构师在中高复杂度编码任务中的受控自治开发模式（Controlled Autonomous Development Mode，简称 CAD Mode）和 Execution Grant 授权边界。CAD Mode 不是普通“继续执行”，而是在规格、计划、纪律、验证和授权都成立后，才允许自动分轮推进。

## 使用时机

- 用户询问是否进入 CAD Mode、自动分轮推进、连续执行、自动提交或受控自治开发。
- 任务已具备产品设计、系分设计、OpenSpec、Harness Plan、Superpowers/TDD 纪律、验收场景和验证矩阵，且需要多轮实现、测试、重构和验证。

## 不适用场景

- 用户只要求普通代码 Review、概念讨论、方案评估或一次性小改动。
- 目标、范围、验收、写入范围、验证命令、停止条件、用户已有改动或高风险人工确认点仍不清楚。

## 读取后必须产出

- CAD Mode 进入门禁结论；若不满足，列出缺口并给出 Round 0 补齐路径。
- Execution Grant 的任务、范围、Git 策略、禁止事项、人工确认点、撤销方式、每轮闭环和停止条件。

## 需要继续读取的 reference

- AI 协作总纲、OpenSpec、Superpowers、Harness 读 `ai-assisted-engineering.md`。
- 中大型项目、长任务、上下文衰减或 Wave 编排读 `ai-large-project-orchestration.md`；CAD 只消费其中已满足门禁的单个任务包或阶段切片。
- AI Native 端到端产品到研发流程、角色编排和 GSD/CAD 编排准入先由 `ai-native-engineering-workflow/references/gsd-cad-admission.md` 判断；本文件不判断端到端是否需要 GSD/CAD，不生成 AI Native 准入结论，只处理已选定原子任务的 CAD 门禁和授权。
- 工程生命周期、验证命令和 Git 基础规约读 `workflow.md`。
- 禁止行为、高风险操作和生产风险读 `negative-constraints.md`、`production-readiness.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断能否进入 CAD Mode | 1、2、3、4 | 每轮执行细节 |
| 补齐 Round 0 | 3、4、5 | 自动提交细节 |
| 编写 Execution Grant | 4、8 | OpenSpec 基础解释 |
| 自动分轮推进 | 5、6、7 | CAD 建议话术 |
| 判断是否必须停止 | 7、8、9 | 普通低风险流程 |
| 任务完成或中断收口 | 6、7、9 | 模式介绍 |
| 从 GSD-like 编排进入 CAD | 先确认 `gsd-cad-admission.md` 和 `ai-large-project-orchestration.md` 已选定单个任务包，再读 2、3、4、8 | 不消费整个 Roadmap |
| 从 AI Native 产品上下文或 MVP harden 进入 CAD | 先消费 `ai-native-engineering-workflow/references/gsd-cad-admission.md` 或产品侧交接结论，再回读 `ai-large-project-orchestration.md` 的工程输入转换，最后读 2、3、4、8 | 不把产品上下文包、Hardened Candidate 或业务 MVP 当 Execution Grant |

## 1. 模式边界

受控自治开发模式用于中高复杂度编码任务：在明确规格、计划和授权边界下，自动分轮完成测试、实现、重构、验证、变更摘要记录和必要提交处理，直到目标完成、用户中断、发生严重错误或出现需要用户判断的不确定点。

Git 策略由 Execution Grant 和工具层权限共同决定：`auto_commit` 表示权限可用时每轮验证后提交本轮变更；`summary_only` 表示无权限或权限不足时每轮只记录摘要，最终由用户主动提交。两种策略都不得绕过平台权限、沙箱或用户授权；不得包含 `git push`、创建 PR、merge、rebase、reset hard 或强制覆盖历史。

## 2. CAD Mode 建议机制

当目标、范围、非目标、验收标准、产品设计、系分设计、OpenSpec、Harness Plan、Superpowers/TDD 纪律和验证矩阵已经可审查，且任务需要多轮小步实现、测试补充、重构和反复验证时，可以建议用户进入 CAD Mode。建议只是候选提醒，不等于授权。

中大型项目中的 CAD 只建议作用于一个已选定的原子任务包或阶段切片。AI Native 先判断 GSD/CAD 编排准入；GSD-like 编排负责大项目上下文、Stage、Wave、任务包和恢复入口；CAD 不直接消费整个 Roadmap，不跨 Wave 自动推进，不把 GSD 计划解释为 Execution Grant。

不得建议进入 CAD Mode 的场景：

- 需求仍停留在想法层，目标、边界、验收或禁止事项不清楚。
- 涉及资金、权限、生产数据、数据库迁移、外部接口或真实通道，但尚未建立人工确认点。
- 写入范围、验证命令、停止条件或用户已有改动无法识别。
- 用户只给了 GSD-like Roadmap、Wave 或任务清单，但没有选定单个任务包、写入范围、验证命令和 Execution Grant。
- 用户只要求审查、评估、讨论方案或明确表示不希望自动推进。

## 3. CAD Mode 进入门禁

CAD Mode 是受控自动推进模式，不是普通执行模式。即使用户主动要求开启，也必须先检查进入门禁；门禁不满足时不得自动逐轮推进，只能列出缺口，并先补齐产品设计、系分设计、OpenSpec、Harness Plan 或 Superpowers 执行纪律。

进入 CAD Mode 必须同时满足：

- 产品设计可审查：用户价值、业务流程、边界、异常场景和验收标准清楚。
- 系分设计可审查：模块边界、接口契约、数据模型、状态流转、非功能约束、风险和研发计划清楚。
- OpenSpec 已形成：目标、范围、非目标、业务规则、接口/数据契约、验收场景和验证方式清楚。
- Harness Plan 已形成：Task ID、Owner、任务拆分、写入范围、只读范围、依赖顺序、验证命令、停止条件、交接方式和恢复入口清楚；需要正式检查时通过 `scripts/check_harness_plan.py --kind cad-candidate` 或人工等价检查。
- Superpowers 执行纪律已明确：TDD、Review、Refactor、编码红线、测试门禁和 AI 产物复核清楚。
- Execution Grant 已形成：授权范围、可执行命令、禁止事项、人工确认点和撤销方式清楚。
- 工作区状态已检查：能区分用户已有改动和本次自动推进改动。
- 若来自 GSD-like 编排，必须已选定单个 Task ID 或阶段切片，且该任务包具备所属 Stage、Wave、写入文件、只读参考、验收场景、验证命令、交接要求和回滚提示。
- 若来自 AI Native 产品上下文、Product Builder、业务 dogfooding 或 MVP/原型 harden，必须已经有 `ai-native-engineering-workflow` 或产品侧 Hardened Candidate 交接结论，并由架构师转成 OpenSpec、Harness Plan、验证矩阵和单个 CAD 候选任务；不得把业务 MVP、PRD、产品上下文包、AI Native 编排结论或 GSD Roadmap 直接当 Execution Grant。

缺门禁时使用短句收口：`当前还不能进入 CAD Mode，缺少：<缺口列表>。我可以先补齐 Round 0，待你确认 Execution Grant 后再进入自动推进。`

## 4. Round 0 与启动条件

启动前必须完成 Round 0 校准：目标、范围、非目标、验收场景、测试策略、风险点、摘要策略、Git 策略和停止条件。Round 0、OpenSpec、Harness Plan、Execution Grant、每轮计划、变更摘要、提交建议和交付总结默认使用中文；代码标识符、协议字段、框架 API、错误码和项目已有英文规范保持原样。

启动条件：

- 产品设计、系分设计、OpenSpec、Harness Plan、Superpowers 执行纪律和 Execution Grant 均已形成，并通过进入门禁检查。
- 用户明确授权自动推进，并明确 Git 策略为 `auto_commit` 或 `summary_only`。
- 已识别写入范围、禁止修改范围、验证命令、摘要记录方式、建议提交粒度和停止条件。
- 已确认 Harness Plan 中的写入范围与 Execution Grant 的授权范围一致；若不一致，以更窄范围为准并先请求用户确认。
- 涉及公共契约、资金、权限、生产数据、数据库迁移或外部接口时，已设置人工确认点。

## 5. 每轮执行闭环

每轮执行闭环固定为：Pick 选择本轮最小目标 -> Red 写失败测试或验收用例 -> Green 最小实现 -> Review 检查架构边界、编码红线、测试质量和无关修改 -> Refactor 在测试保护下必要重构 -> Verify 运行本轮验证 -> Record 记录变更、验证和风险 -> Commit 按 Git 策略处理 -> Pause 留出 5 秒人工中断窗口 -> Next 无阻塞进入下一轮。

若用户在 5 秒中断窗口内提出暂停、修改方向、调整授权、补充约束或要求人工审查，必须停止自动推进并处理用户输入。严重错误优先于中断窗口，一旦发生立即停止。

每轮摘要至少记录本轮目标、实际完成内容、主要文件或模块、验证命令和结果、风险/失败/跳过原因、Git 处理结果。

## 6. Git 策略与自动提交

每轮自动提交必须同时满足：

- `git add` / `git commit` 已在 Execution Grant 中明确授权，并且工具层权限可用。
- 提交前已检查 `git status` 和 `git diff`，确认只包含本轮授权范围内的变更，且未混入用户已有改动。
- 本轮相关验证已通过；若验证失败、跳过或可信度不足，不得自动提交，应停止或进入人工确认。
- 提交信息使用非交互式中文提交说明，说明本轮目标、范围和验证结果。

自动提交失败、权限被拒绝或 `.git` 状态异常时，不得反复重试；切换为 `summary_only`，记录原因并继续下一轮或按停止条件暂停。任务完成或中断时，`auto_commit` 列出每轮提交信息、文件范围和验证结果；`summary_only` 给出建议提交粒度、建议提交信息、每轮摘要和文件清单。

## 7. 自动停止条件

出现以下任一情况，必须停止自动推进并回到人工确认：

- 可能导致数据破坏、资金损失、权限绕过、敏感信息泄露、生产不可用、仓库状态不可控或不可逆操作。
- 验证命令出现无法解释的严重失败，继续修改可能掩盖真实问题、扩大影响或破坏测试可信度。
- OpenSpec 与现有代码、测试或业务规则冲突。
- 公共 API、DTO、枚举、错误码、数据库结构需要破坏性变更。
- 公有方法可能超过 5 个参数，或需要引入新依赖。
- 涉及资金、权限、租户、审计、生产数据、密钥、外部接口或真实支付/资金通道。
- 工作区混有用户改动，无法干净区分本轮变更。
- 需要选择业务口径、产品规则、兼容策略、迁移路径或风险取舍。

## 8. Execution Grant：执行授权包

Execution Grant 是 CAD Mode 的权限边界。它只能约束当前任务链，任务完成、用户暂停或授权被撤销后失效；不得被理解为永久授权或跨任务授权。

最小授权结构：适用任务、有效期限、写入范围、验证范围、Git 策略、Git 范围、清理范围、外部访问、停止条件。

默认可纳入授权包的低风险操作：读取仓库代码/配置/测试/文档，修改 Harness Plan 中声明的写入范围，新增或修改测试，运行本地测试/编译/lint/格式化/codegen，清理本轮生成的临时文件或构建产物，查看 `git status` / `git diff` / `git log`，记录每轮变更摘要。

必须显式列出的操作：每轮自动执行 `git add` / `git commit`，创建或切换分支，安装依赖或更新 lock 文件，启动 Docker/数据库/MQ/本地服务，访问公网文档或外部 API，运行耗时全量测试，修改公共契约、数据库迁移、跨模块架构、权限、安全或资金逻辑，写入仓库外目录。

即使已进入 CAD Mode，也不得静默执行：

- 未在 Execution Grant 中明确授权、或工具层未允许的 Git 写操作。
- `git push`、创建 PR、merge、rebase、reset hard 或强制覆盖历史。
- 删除用户未授权目录或不属于本轮的文件。
- 操作生产环境、生产数据库、真实外部 API 或真实支付/资金通道。
- 读取、写入或提交密钥、token、生产配置、客户敏感数据。
- 引入新中间件、新框架、新运行时代理或大版本依赖升级。
- 改变资金、权限、审计、合规、风控、结算等业务规则口径。

平台权限边界优先于 Execution Grant。若 Codex/工具层要求额外授权，应按工具规则请求；不得通过脚本绕过授权、沙箱或安全限制。

## 9. 结束收口与 Review 清单

结束时必须输出已执行验证、未执行验证、残余风险和最终是否仍需用户执行 Git 操作。

- 资深架构师审查：是否符合 OpenSpec、架构红线、编码约规、测试要求、验证要求和交付边界。
- 产品架构专家审查：涉及复杂业务、PRD、角色流程、状态机、规则矩阵、运营后台、指标或验收标准时执行；涉及支付、账户、资金、清结算、对账、VCC、ACH、卡、风控、争议或金融数据时启用支付与资金分支。
- CAD 专项审查：门禁是否满足，授权是否明确，每轮是否按闭环推进，自动提交是否只包含授权范围内已验证变更，是否区分用户已有改动，结束收口是否完整。
- GSD-CAD 联动审查：来自大项目编排的 CAD 任务必须回写阶段状态、验证矩阵和 handoff，说明当前 Task ID 是否完成、是否满足退出条件、是否可以进入下一任务包或必须暂停。
