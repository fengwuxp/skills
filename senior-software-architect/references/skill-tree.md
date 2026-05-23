# 资深架构师技能树

本文定义资深架构师的能力地图，用于系统设计、编码实现、代码审查、设计评审、技术方案和团队规范落地。Java/Spring 是核心专长，但架构判断和工程治理能力必须能迁移到其他语言与技术栈。

## 使用时机

- 用户询问资深架构师能力模型、成长路径、能力地图或技能评估。
- 需要快速定位架构师能力域，再按任务进入专题 reference。

## 不适用场景

- 需要具体编码规则时，直接读取 `coding-standards.md`。
- 需要系统设计模板时，直接读取 `system-analysis-design.md`。

## 读取后必须产出

- 能力域定位、当前短板、推荐阅读 reference 和下一步训练/交付路径。

## 需要继续读取的 reference

- 架构设计读 `architecture.md`、`system-analysis-design.md`。
- 代码质量读 `coding-standards.md`、`coding-review-deep-dive.md`。
- AI 协作读 `ai-assisted-engineering.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 回答“架构师能力模型/成长路径” | 本文件的提炼依据、总定义和专题路由 | 专题细节 |
| 产品语义到工程设计 | `skill-tree-architecture-design.md` | 平台和 AI 细节 |
| 模块边界、接口、数据、状态设计 | `skill-tree-architecture-design.md` | 技术领导力 |
| 代码 Review、调试诊断、测试能力 | `skill-tree-engineering-quality.md` | 产品和 K8s 细节 |
| 生产治理、可观测性、安全、K8s | `skill-tree-engineering-quality.md`、`skill-tree-platform-leadership-ai.md` | 代码命名细节 |
| Java/Spring/Wind 专项 | `skill-tree-engineering-quality.md`，并按需读 `coding-standards.md` | 通用能力地图重复解释 |

## 提炼依据

- 《代码整洁之道》：命名、函数、注释、格式、对象、错误处理、边界、单元测试、类、系统、并发、逐步改进、代码坏味道与启发。参考：https://github.com/glen9527/Clean-Code-zh
- 《架构整洁之道》：编程范式、SOLID、组件聚合与耦合、边界、策略与层次、业务逻辑、整洁架构、测试边界、数据库/Web/框架是实现细节。参考：https://github.com/leewaiho/Clean-Architecture-zh
- 《重构：改善既有代码的设计》：在测试保护下，通过小步、行为保持的结构调整，消除坏味道并改善可理解性、可维护性和可演进性。参考：https://martinfowler.com/books/refactoring.html
- 《凤凰架构》：大型分布式系统的架构演进、可靠性治理、服务化、可观测性、流量治理、云原生与基础设施吸收复杂度。参考：https://icyfenix.cn/
- Java/Spring 企业应用实践：DDD、模块化单体、微服务、Spring Boot、MyBatis/JPA、数据库、缓存、消息、可观测性、安全和工程治理。
- 多语言工程实践：Go、Node.js/TypeScript、Python、Rust、前端和数据工程中的构建、测试、lint、部署、可观测性和生产治理方式。
- AI 编码协作实践：以 OpenSpec 定标准、Superpowers 保纪律、Harness 管团队，把 AI 编码纳入需求规格、TDD、Review、Refactor、协作编排和验证闭环。
- 公开 AI Skill 方法论：参考 `obra/superpowers`（https://github.com/obra/superpowers）、`multica-ai/andrej-karpathy-skills`（https://github.com/multica-ai/andrej-karpathy-skills）和 `mattpocock/skills`（https://github.com/mattpocock/skills）中可迁移的工程纪律，例如先澄清再编码、简单优先、最小变更、目标驱动验证、领域语言对齐、TDD、诊断闭环和 Review 防越界；只吸收原则，不复制仓库结构、安装流程或技能菜单。

## 总定义

架构师不是只画架构图的人，而是对系统长期结构质量负责的人：理解业务复杂度，识别关键边界，做出技术取舍，设计可演进的结构，并通过代码、评审、测试、规范和协作把设计落地。

## 专题 reference 路由

- `skill-tree-architecture-design.md`：架构原则、产品语义、模块管理、接口/类/数据/流程设计。
- `skill-tree-engineering-quality.md`：编码技术栈、质量保障、评审、调试、稳定性、安全、可观测性。
- `skill-tree-platform-leadership-ai.md`：Kubernetes、前端协作、工程治理、技术领导力、表达能力、AI 协作和 Wind 实践。
