# Java 项目长期演进规范

本文面向 Java 企业项目的长期维护、团队协作和架构演进，融合团队现有规范、Wind 项目族实践、Clean Code、Clean Architecture、重构实践，以及 SOFAStack 模块化/可扩展架构思想。

## 使用时机

本文是项目级综合治理规范，内容较重。只有当任务涉及模块划分、服务分层、API、数据库、日志、安全、测试、Git、前端、Kubernetes 或跨团队长期演进治理时才读取；普通代码修改、单点 Review、测试实践或 AI 编码协作应优先读取对应专项 reference。

## 不适用场景

- 单点代码 Review 优先读 `coding-review-deep-dive.md`。
- 具体 Java 编码规约优先读 `coding-standards.md`。
- 测试实践优先读 `testing.md` 和 `testing-practices.md`。
- AI 编码协作优先读 `ai-assisted-engineering.md`。

## 读取后必须产出

- 明确治理主题、应读取的专题 reference、需要跳过的细节，以及最终检查项。

## 需要继续读取的 reference

- 代码库、模块和依赖读 `project-governance-codebase-and-modules.md`。
- API、DTO、Query 和服务建模读 `project-governance-service-api-modeling.md`。
- 数据、安全、日志和质量治理读 `project-governance-data-security-quality.md`。
- Git、发布、平台和长期演进读 `project-governance-delivery-and-platform.md`。
- 项目 `AGENTS.md` 明确 opt-in Wind 项目编码约规时，读 `wind-project-coding-conventions.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断代码库类型和治理强度 | `project-governance-codebase-and-modules.md` 的 0-2，必要时读 `project-governance-delivery-and-platform.md` 的 20 | 前端、Kubernetes、SOFAStack 细节 |
| 模块划分、依赖方向、服务边界 | `project-governance-codebase-and-modules.md` | Git、前端、Kubernetes |
| API、DTO、Query、方法命名 | `project-governance-service-api-modeling.md` | 容器化和前端协作 |
| Wind 项目编码约规 opt-in | `wind-project-coding-conventions.md` | 不把 Wind 规则强套到未声明项目 |
| 数据库、日志、安全、测试治理 | `project-governance-data-security-quality.md` | SOFAStack 和 Git 细节 |
| 前端、Git、Kubernetes、演进治理 | `project-governance-delivery-and-platform.md` | Java 服务层细则 |
| 系分或长期演进评审 | `project-governance-delivery-and-platform.md` 的 16、17、20、21 | 只读当前任务无关专题 |

## 专题 reference 路由

- `project-governance-codebase-and-modules.md`：规范目标、设计原则、代码库类型、工程模块、依赖管理。
- `project-governance-service-api-modeling.md`：Service 划分、方法命名、Query/DTO、API 设计和编码原则。
- `wind-project-coding-conventions.md`：项目 opt-in 后的 Wind 项目编码约规、face/impl 边界、服务分层、模型归属、分包、DAL、外部集成和 CR 清单。
- `project-governance-data-security-quality.md`：数据访问、数据库、日志、安全和测试治理。
- `project-governance-delivery-and-platform.md`：前端协作、Git/PR、评审、重构演进、Kubernetes、SOFAStack、最小门禁和系分门禁。

## 后续维护规则

- 本文件只保留总入口和路由，不再追加专题长知识。
- 新增治理主题时，优先放入对应专题 reference；如果一个专题超过 500 行，再继续拆分。
- 修改专题 reference 后，必须运行 `scripts/audit-reference-indexes.py` 和 `./scripts/validate.sh`。
