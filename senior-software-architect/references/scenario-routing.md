# 架构场景识别与方案路由

本文用于在处理架构、评审、编码、生产变更和技术治理任务前，快速判断应读取哪些 reference、输出什么产物、守住哪些红线。它是知识路由，不是组织流程审批，也不是生产变更授权。

## 使用时机

- 用户任务同时涉及任务类型、技术栈、风险等级或目标产物选择。
- 不确定应读取 `architecture.md`、`testing.md`、`debugging-diagnosis.md`、`production-readiness.md` 还是其他专项 reference。
- 需要做触发路径自检、模拟验收或防止一次性加载过多 reference。

## 不适用场景

- 用户只问单个 reference 内的具体规则，且入口已经明确。
- 项目本地 `AGENTS.md`、OpenSpec、Harness Plan 或代码上下文已经给出更具体的执行路径。

## 读取后必须产出

- 当前任务类型、技术栈、风险等级和目标产物判断。
- 最小 reference 集合，以及不读取其他 reference 的理由。
- 对应输出形态和关键红线。

## 需要继续读取的 reference

- 按“快速路由表”和“组合场景处理”选择；不要为了完整性继续读取所有 reference。

## 使用顺序

1. **识别任务类型**：Review、系分、架构方案、技术选型、Bug 修复、调试诊断、根因分析、写测试、补测试、加测试、按 TDD 推进、测试选择、测试分层、生产变更、代码修改、遗留系统改造、AI 编码协作、AI 输出审查。
2. **识别技术栈**：Java/Spring、Go、Node.js/TypeScript、Python、Rust、前端、数据工程或混合技术栈。
3. **识别风险等级**：是否涉及资金、权限、租户、敏感数据、公共契约、数据库、异步消息、生产发布、外部依赖或不可逆操作。
4. **识别目标产物**：代码修改、Review 结论、系分文档、ADR、迁移计划、上线检查、回滚方案或测试计划。
5. **选择最小参考集**：只加载当前任务需要的 reference；不为了显得完整一次性加载所有文档。

## 快速路由表

| 场景 | 必读参考 | 输出重点 |
| --- | --- | --- |
| 通用架构设计 | `architecture.md`、`review-and-output-templates.md` | 背景、目标、非目标、边界、数据、可靠性、安全、验证、发布和取舍。 |
| 跨语言方案或非 Java 项目 | `language-agnostic-architecture.md`、`workflow.md` | 先识别本地生态，再迁移通用原则，不强套 Java/Spring 规则。 |
| Java/Spring 设计或 Review | `coding-standards.md`、`coding-review-deep-dive.md`、`workflow.md` | Java 约规、空值契约、Lombok/MapStruct、测试与验证；涉及模块/服务/API/DB 综合治理时再读 `project-governance-standards.md`。 |
| Bug 修复 / 调试诊断 / 根因分析 / 测试失败 | `debugging-diagnosis.md`、`testing.md`、`workflow.md`，Java 项目再读 `coding-standards.md` | 先建立可重复反馈环和最小复现，再假设验证、证据采集、最小修复和回归测试。 |
| 写测试 / 补测试 / 加测试 / 按 TDD 推进 / 先写失败测试 / 测试选择 / 测试分层 | `testing.md`，Java 项目再读 `coding-standards.md` | 先读 `testing.md` 第 2 节选择测试形态，再定业务事实、保护对象、风险来源、真实链路和替身边界；只有命中 `testing.md` 第 6/12 节专项条件时再读 `testing-practices.md`。 |
| 代码 Review / PR Review | `review-and-output-templates.md`、`coding-review-deep-dive.md`、`clean-code.md`、`negative-constraints.md` | 问题优先，按 P0-P3 给文件行号、风险、证据、建议和验证。 |
| 系统分析设计 / 系分 | `system-analysis-design.md`、`architecture.md`、`production-readiness.md` | 背景、目标、概要、详细、非功能、研发计划、评审清单。 |
| 技术选型 / 架构取舍 | `adr-and-tradeoff.md`、`architecture.md` | 备选方案、决策理由、放弃理由、代价、风险、复审条件。 |
| 分布式一致性 / MQ / 对账 / 补偿 | `distributed-consistency.md`、`production-readiness.md` | 业务不变量、事务边界、幂等、去重、补偿、对账、告警和一致性窗口。 |
| 遗留系统改造 / 迁移 | `evolutionary-architecture.md`、`adr-and-tradeoff.md`、`production-readiness.md` | 防腐层、契约测试、双写/回填/切流、灰度、回滚、下线标准。 |
| 安全架构 / 权限 / 租户 / 敏感数据 | `security-architecture.md`、`negative-constraints.md` | 资产、主体、边界、威胁、认证授权、隔离、密钥、审计和安全测试。 |
| 生产变更 / 上线评审 | `production-readiness.md`、`review-and-output-templates.md`、`negative-constraints.md` | 影响范围、灰度、开关、监控、应急、回滚、审计、验收。 |
| 生产现象 / 线上异常 / 故障排查 | `debugging-diagnosis.md`、`production-readiness.md`、`negative-constraints.md` | 先定影响面、时间线、止血和只读证据，再做根因假设、最小修复、回滚和复盘。 |
| 数据库迁移 / 修数 / 回填 | `production-readiness.md`、`review-and-output-templates.md`、`negative-constraints.md` | dry-run、备份、分批、校验、审计、回滚和新旧版本兼容。 |
| 外部 API / SDK / 云产品 / 第三方服务 / 版本升级 | `workflow.md`、`adr-and-tradeoff.md`、`production-readiness.md`、`negative-constraints.md` | 先过外部知识时效性门禁，核验官方文档、release notes、项目 lockfile 或本地依赖树，再说明兼容、安全、许可、成本、回滚和 owner。 |
| 微服务拆分判断 | `evolutionary-architecture.md`、`architecture.md`、`adr-and-tradeoff.md` | 业务边界、数据归属、团队运维能力、故障隔离；边界不清优先模块化单体。 |
| 性能与容量问题 | `production-readiness.md`、`language-agnostic-architecture.md` | SLO、容量基线、压测、瓶颈、限流降级、观测指标和回滚阈值。 |
| AI 编码协作 / OpenSpec 到代码 / 多 Agent 编排 | `workflow.md`、`ai-assisted-engineering.md`、`negative-constraints.md` | 先过工程生命周期门禁，再用 OpenSpec 定标准，用 Superpowers 保 TDD、Review、Refactor 和验证纪律，用 Harness 管分工、写入范围、上下文、交接和集成。 |
| AI 生成代码审查 | `skill-tree.md`、`negative-constraints.md`、`workflow.md` | 查幻觉、越界修改、缺失测试、无主依赖、Git 操作和高风险擅自决策。 |
| 技能自检 / 模拟验收 | `acceptance-scenarios.md`、`skill-tree.md` | 一致性、自解释、可执行、克制性和生产意识。 |

## 组合场景处理

- **系分 + 生产变更**：先用 `system-analysis-design.md` 固定背景、目标、边界和详细设计，再用 `production-readiness.md` 检查 SLO、容量、灰度、监控、应急和回滚。
- **技术选型 + 新依赖**：先用 `adr-and-tradeoff.md` 比较备选方案，再用 `negative-constraints.md` 检查依赖必要性、许可证、安全风险和维护责任。
- **外部 API / SDK / 云产品版本变化**：先用 `workflow.md` 的外部知识时效性门禁核验权威来源、版本、生效/发布日期和本地实际依赖，再用 `adr-and-tradeoff.md`、`production-readiness.md` 和 `negative-constraints.md` 检查兼容、安全、成本、上线和回滚。
- **Java Review + 公共契约变更**：先用 `coding-standards.md` 和 `coding-review-deep-dive.md` 查代码、边界与契约语义，再用 `review-and-output-templates.md` 检查兼容性治理；涉及项目级模块/API/DB 约规时再读 `project-governance-standards.md`。
- **Java Review + 代码质量深化**：先用 `coding-review-deep-dive.md` 按业务语义、边界方向、契约完整性、失败路径和工程一致性检查，再回到具体强规约。
- **Bug 修复 + TDD**：先用 `debugging-diagnosis.md` 建立稳定失败反馈环，再用 `testing.md` 选择回归测试形态；修复后必须证明原失败路径通过且旧行为未回退。
- **生产现象 + 代码修复**：先只读采集影响面、时间线、日志、指标和数据事实，再按 `debugging-diagnosis.md` 收敛根因；需要上线或数据处理时补充 `production-readiness.md` 和 `negative-constraints.md`。
- **DDD/分层架构 + 写测试/TDD**：先用 `testing.md` 第 2 节选择测试形态，再用第 6 节定位保护事实和测试层级；只有命中 Domain Service / Policy / Specification、Application Service / Use Case、Repository / DAO / Mapper 或第 12 节专项条件时，再读 `testing-practices.md`。
- **微服务拆分 + 数据一致性**：先确认业务边界、数据归属和团队能力，再设计事务边界、幂等、补偿、对账、告警和人工兜底。
- **遗留系统迁移 + 生产发布**：优先小步迁移，使用防腐层、双写/回填/切流、契约测试和灰度观测，避免一次性替换核心链路。
- **安全改造 + 遗留系统**：先识别现有权限和数据隔离缺口，再用防腐层、灰度开关和回归测试逐步收敛，不一次性重写认证授权体系。
- **AI 编码协作 + Java/Spring 修改**：先用 `ai-assisted-engineering.md` 定义 OpenSpec、Superpowers 和 Harness，再加载 `coding-standards.md`、`coding-review-deep-dive.md` 和项目本地规范约束具体代码。
- **AI 编码协作 + 高风险生产行为**：先确认 OpenSpec 中的业务不变量、验收场景和回滚边界，再补充 `production-readiness.md`、`negative-constraints.md` 和专项安全/一致性规范。

## 输出路由

- 用户要“审查”：输出问题优先的 Review，给严重级别、证据、建议和验证。
- 用户要“设计”：输出架构方案或系分结构，必须包含目标、非目标、边界、数据、可靠性、安全、验证和发布。
- 用户要“写测试 / 补测试 / 加测试 / 按 TDD 推进”：先输出或执行测试选择，说明测试层级、真实链路、替身边界、断言事实和验证命令；TDD 场景先构造失败测试，再推进实现。
- 用户要“修 Bug / 查异常 / 诊断失败”：先输出或执行复现与证据计划，说明反馈环、假设、插桩边界、最小修复和回归验证。
- 用户要“选型”：输出 ADR 风格的取舍，不只给结论。
- 用户要“上线”：输出生产就绪检查、风险清单、回滚和监控。
- 用户要“改代码”：先按 `workflow.md` 过 Clarify、Design、Plan、Build、Verify、Review/Ship 生命周期门禁，再识别技术栈和本地规范，小步修改并运行对应验证。
- 用户要“用 AI 写代码 / 多 Agent 协作”：先按 `workflow.md` 过生命周期门禁，再输出或确认 OpenSpec 与 Harness Plan，执行小步实现和 Superpowers 验证闭环。
- 用户只要“建议”：克制输出不超过 3 个高价值方向，必要时说明假设。

## 路由红线

1. 不得只按关键词路由；必须结合业务风险、技术栈、目标产物和生产影响。
2. 不得把 Java/Spring 规则强套到非 Java 项目。
3. 不得把 Review 输出成泛泛总结；发现问题时必须问题优先。
4. 不得在边界、数据归属、运维能力不清时建议微服务拆分。
5. 不得对生产变更给“可直接上线”结论，除非已覆盖验证、灰度、监控、回滚和残余风险。
6. 不得把安全、数据一致性和遗留系统迁移当作普通 CRUD 或简单重构处理。
7. 不得为了完整性加载所有 reference；只加载对当前判断有用的最小集合。
8. 不得在没有复现、证据或可验证假设时直接大范围改代码。
