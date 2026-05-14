# 架构场景识别与方案路由

本文用于在处理架构、评审、编码、生产变更和技术治理任务前，快速判断应读取哪些 reference、输出什么产物、守住哪些红线。它是知识路由，不是组织流程审批，也不是生产变更授权。

## 使用顺序

1. **识别任务类型**：Review、系分、架构方案、技术选型、生产变更、代码修改、遗留系统改造、AI 编码协作、AI 输出审查。
2. **识别技术栈**：Java/Spring、Go、Node.js/TypeScript、Python、Rust、前端、数据工程或混合技术栈。
3. **识别风险等级**：是否涉及资金、权限、租户、敏感数据、公共契约、数据库、异步消息、生产发布、外部依赖或不可逆操作。
4. **识别目标产物**：代码修改、Review 结论、系分文档、ADR、迁移计划、上线检查、回滚方案或测试计划。
5. **选择最小参考集**：只加载当前任务需要的 reference；不为了显得完整一次性加载所有文档。

## 快速路由表

| 场景 | 必读参考 | 输出重点 |
| --- | --- | --- |
| 通用架构设计 | `architecture.md`、`review-and-output-templates.md` | 背景、目标、非目标、边界、数据、可靠性、安全、验证、发布和取舍。 |
| 跨语言方案或非 Java 项目 | `language-agnostic-architecture.md`、`workflow.md` | 先识别本地生态，再迁移通用原则，不强套 Java/Spring 规则。 |
| Java/Spring 设计或 Review | `coding-standards.md`、`coding-review-deep-dive.md`、`project-governance-standards.md`、`workflow.md` | Java 约规、模块边界、服务分层、空值契约、Lombok/MapStruct、测试与验证。 |
| 代码 Review / PR Review | `review-and-output-templates.md`、`coding-review-deep-dive.md`、`clean-code.md`、`negative-constraints.md` | 问题优先，按 P0-P3 给文件行号、风险、证据、建议和验证。 |
| 系统分析设计 / 系分 | `system-analysis-design.md`、`architecture.md`、`production-readiness.md` | 背景、目标、概要、详细、非功能、研发计划、评审清单。 |
| 技术选型 / 架构取舍 | `adr-and-tradeoff.md`、`architecture.md` | 备选方案、决策理由、放弃理由、代价、风险、复审条件。 |
| 分布式一致性 / MQ / 对账 / 补偿 | `distributed-consistency.md`、`production-readiness.md` | 业务不变量、事务边界、幂等、去重、补偿、对账、告警和一致性窗口。 |
| 遗留系统改造 / 迁移 | `evolutionary-architecture.md`、`adr-and-tradeoff.md`、`production-readiness.md` | 防腐层、契约测试、双写/回填/切流、灰度、回滚、下线标准。 |
| 安全架构 / 权限 / 租户 / 敏感数据 | `security-architecture.md`、`negative-constraints.md` | 资产、主体、边界、威胁、认证授权、隔离、密钥、审计和安全测试。 |
| 生产变更 / 上线评审 | `production-readiness.md`、`review-and-output-templates.md`、`negative-constraints.md` | 影响范围、灰度、开关、监控、应急、回滚、审计、验收。 |
| 数据库迁移 / 修数 / 回填 | `production-readiness.md`、`review-and-output-templates.md`、`negative-constraints.md` | dry-run、备份、分批、校验、审计、回滚和新旧版本兼容。 |
| 微服务拆分判断 | `evolutionary-architecture.md`、`architecture.md`、`adr-and-tradeoff.md` | 业务边界、数据归属、团队运维能力、故障隔离；边界不清优先模块化单体。 |
| 性能与容量问题 | `production-readiness.md`、`language-agnostic-architecture.md` | SLO、容量基线、压测、瓶颈、限流降级、观测指标和回滚阈值。 |
| AI 编码协作 / OpenSpec 到代码 / 多 Agent 编排 | `ai-assisted-engineering.md`、`workflow.md`、`negative-constraints.md` | 用 OpenSpec 定标准，用 Superpowers 保 TDD、Review、Refactor 和验证纪律，用 Harness 管分工、写入范围、上下文、交接和集成。 |
| AI 生成代码审查 | `skill-tree.md`、`negative-constraints.md`、`workflow.md` | 查幻觉、越界修改、缺失测试、无主依赖、Git 操作和高风险擅自决策。 |
| 技能自检 / 模拟验收 | `acceptance-scenarios.md`、`skill-tree.md` | 一致性、自解释、可执行、克制性和生产意识。 |

## 组合场景处理

- **系分 + 生产变更**：先用 `system-analysis-design.md` 固定背景、目标、边界和详细设计，再用 `production-readiness.md` 检查 SLO、容量、灰度、监控、应急和回滚。
- **技术选型 + 新依赖**：先用 `adr-and-tradeoff.md` 比较备选方案，再用 `negative-constraints.md` 检查依赖必要性、许可证、安全风险和维护责任。
- **Java Review + 公共契约变更**：先用 `coding-standards.md` 和 `project-governance-standards.md` 查代码与分层，再用 `review-and-output-templates.md` 检查兼容性治理。
- **Java Review + 代码质量深化**：先用 `coding-review-deep-dive.md` 按业务语义、边界方向、契约完整性、失败路径和工程一致性检查，再回到具体强规约。
- **微服务拆分 + 数据一致性**：先确认业务边界、数据归属和团队能力，再设计事务边界、幂等、补偿、对账、告警和人工兜底。
- **遗留系统迁移 + 生产发布**：优先小步迁移，使用防腐层、双写/回填/切流、契约测试和灰度观测，避免一次性替换核心链路。
- **安全改造 + 遗留系统**：先识别现有权限和数据隔离缺口，再用防腐层、灰度开关和回归测试逐步收敛，不一次性重写认证授权体系。
- **AI 编码协作 + Java/Spring 修改**：先用 `ai-assisted-engineering.md` 定义 OpenSpec、Superpowers 和 Harness，再加载 `coding-standards.md`、`coding-review-deep-dive.md` 和项目本地规范约束具体代码。
- **AI 编码协作 + 高风险生产行为**：先确认 OpenSpec 中的业务不变量、验收场景和回滚边界，再补充 `production-readiness.md`、`negative-constraints.md` 和专项安全/一致性规范。

## 输出路由

- 用户要“审查”：输出问题优先的 Review，给严重级别、证据、建议和验证。
- 用户要“设计”：输出架构方案或系分结构，必须包含目标、非目标、边界、数据、可靠性、安全、验证和发布。
- 用户要“选型”：输出 ADR 风格的取舍，不只给结论。
- 用户要“上线”：输出生产就绪检查、风险清单、回滚和监控。
- 用户要“改代码”：先识别技术栈和本地规范，小步修改并运行对应验证。
- 用户要“用 AI 写代码 / 多 Agent 协作”：先输出或确认 OpenSpec 与 Harness Plan，再执行小步实现和 Superpowers 验证闭环。
- 用户只要“建议”：克制输出不超过 3 个高价值方向，必要时说明假设。

## 路由红线

1. 不得只按关键词路由；必须结合业务风险、技术栈、目标产物和生产影响。
2. 不得把 Java/Spring 规则强套到非 Java 项目。
3. 不得把 Review 输出成泛泛总结；发现问题时必须问题优先。
4. 不得在边界、数据归属、运维能力不清时建议微服务拆分。
5. 不得对生产变更给“可直接上线”结论，除非已覆盖验证、灰度、监控、回滚和残余风险。
6. 不得把安全、数据一致性和遗留系统迁移当作普通 CRUD 或简单重构处理。
7. 不得为了完整性加载所有 reference；只加载对当前判断有用的最小集合。
