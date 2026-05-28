# 项目治理：代码库、模块与依赖

本文从 `project-governance-standards.md` 拆出，承载代码库类型、模块划分和依赖管理的评审入口。具体编码细则回到 `coding-standards.md`，不在本文重复展开。

## 使用时机

- 需要判断代码库类型、治理强度、模块职责或依赖方向。
- 需要设计模块结构、业务域包结构、Maven/BOM 或 starter 依赖边界。

## 不适用场景

- 只评审 API/DTO/Query 或数据库细则时，读取对应治理专题。
- 只处理发布、Git、Kubernetes 或长期演进时，读取 `project-governance-delivery-and-platform.md`。

## 读取后必须产出

- 代码库类型、模块职责、依赖方向、禁止依赖和验证方式。

## 需要继续读取的 reference

- API/服务建模读 `project-governance-service-api-modeling.md`。
- 数据、安全、测试读 `project-governance-data-security-quality.md`。
- 编码细则读 `coding-standards.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断治理强度 | 0、1、2 | Maven 和包结构细节 |
| 模块拆分和依赖方向 | 3、4 | 代码库类型说明 |
| starter 或依赖引入 | 4、5 | 包结构细节 |

## 0. 治理目标

项目治理不是统一格式，而是保证项目长期可读、可改、可共享、可演进、可验证。架构师评审时先识别代码库类型，再决定治理强度。

## 1. 通用底线

- 模块和接口首先表达业务能力，不按数据库表或技术组件机械拆分。
- 先定义模块边界、服务边界、数据边界和安全边界，再写实现。
- 业务规则不依赖 Web、DB、MQ、缓存、第三方 SDK 等外部细节。
- 只改任务明确要求的范围，不顺手重构、不顺手格式化无关文件。
- 任何改动都应有编译、测试、静态检查、评审或验收证据。
- 不清楚需求、背景和约束时，最多给 3 条建议或选项，等用户确认后再深入。

## 2. 代码库类型与治理强度

| 类型 | 首要目标 | 架构师关注重点 |
| --- | --- | --- |
| 基础设施/中间件 | 稳定、可靠、安全、兼容 | API 兼容、线程安全、失败隔离、性能、可观测性、灰度能力 |
| 框架/Starter | 可插拔、低侵入、易集成 | 条件装配、默认实现、覆盖机制、配置模型、版本兼容、最小依赖 |
| 公共业务代码 | 职责清晰、复用稳定、边界明确 | 领域边界、接口契约、数据隔离、向后兼容、跨团队使用成本 |
| 业务项目（APP） | 正确交付、可维护、可发布 | 需求闭环、分层规范、服务命名、测试覆盖、发布风险 |
| 实验/工具/脚本 | 快速验证、风险隔离 | 作用范围、可回滚、数据安全，不污染主工程架构 |

## 3. 模块职责与依赖方向

默认采用模块化单体优先，保留服务化演进路径。

```text
{app}
├── {app}-dependencies
├── {app}-core
├── {app}-common
├── {app}-face / {app}-api
├── {app}-biz
├── {app}-infrastructure
├── {app}-web
├── {app}-bootstrap
└── {app}-tests
```

强制依赖方向：

```text
web -> biz -> core
infrastructure -> core / biz 中定义的 port
bootstrap -> web / biz / infrastructure
face/api -> core
biz 不直接依赖 infrastructure 的实现细节
```

强制规则：

- 禁止循环依赖。
- 禁止 core 依赖 infrastructure、web、bootstrap。
- 禁止 web 直接访问 Mapper/Repository。
- 禁止业务代码直接依赖第三方 SDK，应通过 `XxxClient`、`XxxGateway`、`XxxOperations` 端口隔离。
- tests 可以依赖所有模块，生产模块不得依赖 tests。

## 4. 业务域包结构

业务域内按职责组织，而不是把所有类堆到 `service`：

```text
com.xxx.user
├── application
├── domain
├── service
├── infrastructure / dal
├── model
│   ├── command
│   ├── dto
│   ├── query
│   ├── request
│   └── vo
├── mapstruct
├── enums
└── event
```

如果项目沿用历史风格，可以保留；新代码必须保证职责清楚。模型转换优先放入 `mapstruct` 或项目既有等价转换包。

## 5. 依赖与 starter 边界

- 根 POM、父 POM 或 `{app}-dependencies` 统一管理依赖和插件版本；子模块不写版本号。
- 引入新依赖前先确认项目是否已有等价能力，不为少量代码引入重量级框架。
- 安全、序列化、表达式、脚本、反射、字节码类依赖必须特别评审。
- Web、DB、MQ、Redis、OSS、KMS 等外部能力必须通过基础设施适配层隔离。
- Starter 只做装配，不承载复杂业务流程；用 `@ConditionalOnProperty` 控制开关，用 `@ConditionalOnMissingBean` 允许业务覆盖默认实现。
- 自动装配禁止扫描过宽包路径，禁止隐式修改全局行为。

## 6. 评审清单

- 当前代码库类型是什么，治理强度是否匹配影响面。
- 模块名、包名和依赖方向是否表达业务边界。
- core/face/biz/infrastructure/web/bootstrap 是否职责清楚。
- 是否存在循环依赖、反向依赖、web 直连 Mapper 或业务直连第三方 SDK。
- 新依赖是否有 owner、版本策略、安全风险和替代方案。
- 是否有编译、测试、ArchUnit、依赖收敛或人工评审证据。
