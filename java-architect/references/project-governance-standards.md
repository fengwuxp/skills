# Java 项目长期演进规范

本文面向 Java 企业项目的长期维护、团队协作和架构演进，融合团队现有规范、Wind 项目族实践、Clean Code、Clean Architecture、重构实践，以及 SOFAStack 模块化/可扩展架构思想。

## 0. 规范目标

项目规范的目标不是“统一格式”这么窄，而是让项目具备以下长期能力：

- **可读**：新人能通过模块名、包名、类名、方法名理解系统结构和业务语义。
- **可改**：改动影响范围可预期，边界清晰，测试可保护。
- **可共享**：团队能复用统一模型、组件、规范和工具，而不是每个模块各写一套。
- **可演进**：单体可演进为模块化单体，模块可演进为服务，服务可演进为平台能力。
- **可验证**：架构规则、编码规则、测试规则和发布规则都能通过工具或清单检查。

## 1. 核心设计原则

### 1.1 基本原则

- **业务优先**：模块和接口首先表达业务能力，不按数据库表或技术组件机械拆分。
- **边界优先**：先定义模块边界、服务边界、数据边界和安全边界，再写实现。
- **依赖倒置**：高层业务策略依赖抽象，基础设施提供实现。
- **接口隔离**：按使用场景定义小接口，避免大而全的 Service。
- **单一职责**：模块、类、方法只承担一个主要变化原因。
- **KISS**：优先简单、清晰、团队能掌控的方案。
- **YAGNI**：禁止为不确定未来添加接口、配置、抽象层或扩展点。
- **DRY with Care**：消除真实重复，但不要过早抽象。
- **可测试性优先**：核心业务逻辑应能脱离 Web、DB、MQ、缓存独立测试。
- **渐进式演进**：重构必须小步、可验证、行为保持，不做大爆炸式重写。
- **协作克制**：不清楚需求、背景和约束时，不用知识洪流替代澄清；最多给 3 条建议或选项，等用户确认后再深入。

### 1.2 规范等级

- **强制**：违反后会造成架构腐化、协作成本上升、线上风险或安全风险，必须遵守。
- **推荐**：默认应遵守，确有上下文理由可以偏离，但需要在 PR 或设计文档说明。
- **参考**：提供思路和模板，不强制绑定具体实现。

## 2. 代码库类型分层治理

架构师需要从系统全链路视角管理不同类型代码库。不能用同一把尺子粗暴衡量所有仓库：基础设施中间件更关注可靠性、安全性、兼容性和可观测性；公共业务代码更关注职责边界、复用契约和演进成本；业务项目代码更关注按需求快速、正确、规范地落地。

### 2.1 全场景通用底线

以下规则适用于所有 Java 代码库：

- **代码整洁**：命名准确、函数短小、职责单一、注释解释意图而非掩盖坏代码。
- **架构整洁**：依赖方向清晰，业务规则不被框架、数据库、Web、MQ 等细节绑死。
- **阿里 Java 规约**：命名、集合、并发、异常、日志、数据库等基础约束必须遵守。
- **可读性优先**：代码首先为团队成员阅读和修改服务，其次才是机器执行。
- **长期维护优先**：避免临时补丁式设计、无边界工具类、隐式约定和不可测试逻辑。
- **面向接口编程**：稳定能力先定义契约，具体实现可替换、可测试、可演进。
- **最小修改原则**：只改任务明确要求的范围，不顺手重构、不顺手格式化无关文件。
- **可验证交付**：任何改动都应有对应编译、测试、静态检查、评审或验收证据。

### 2.2 代码库类型与关注重点

| 类型 | 示例 | 首要目标 | 架构师关注重点 |
|------|------|----------|----------------|
| 基础设施/中间件代码 | RPC、MQ、配置中心、Trace、限流、序列号、日志组件 | 稳定、可靠、安全、兼容 | API 兼容性、线程安全、失败隔离、性能、可观测性、扩展点、灰度能力 |
| 框架/Starter 代码 | Spring Boot Starter、自动装配、插件框架、SDK 封装 | 可插拔、低侵入、易集成 | 条件装配、默认实现、覆盖机制、配置模型、版本兼容、最小依赖 |
| 公共业务代码 | 会员、账户、权限、消息、文件、工作流等共享业务能力 | 职责清晰、复用稳定、边界明确 | 领域边界、接口契约、数据隔离、扩展点、向后兼容、跨团队使用成本 |
| 业务项目（APP）代码 | 具体业务系统、运营后台、C 端/B 端应用 | 按需求正确落地、可维护、可交付 | 需求闭环、分层规范、服务命名、测试覆盖、发布风险、团队一致性 |
| 实验/工具/脚本代码 | 一次性迁移脚本、研发工具、验证 Demo | 快速验证、风险隔离 | 作用范围、可回滚、数据安全、不要污染主工程架构 |

### 2.3 基础设施/中间件代码标准

基础设施和中间件代码的复用半径最大，故障影响面最大，规范门槛最高。

强制要求：

- 公共 API 必须稳定，破坏性变更必须走废弃周期：`@Deprecated`、替代方案、迁移文档、删除版本。
- 必须考虑向后兼容、配置兼容、序列化兼容和默认行为兼容。
- 必须显式处理超时、重试、限流、熔断、降级、隔离和资源释放。
- 必须具备结构化日志、指标、Trace、健康检查和关键错误码。
- 必须关注线程安全、内存泄漏、连接池、线程池、阻塞调用和背压。
- 必须最小化外部依赖，避免把重量级依赖传递给业务项目。
- 必须有单元测试、并发/边界测试、集成测试和兼容性测试。
- 配置项必须有默认值、说明、单位、范围和风险提示。

推荐实践：

- 对外能力采用端口接口，例如 `XxxClient`、`XxxOperations`、`XxxTemplate`。
- 多实现扩展点采用 SPI、Spring Bean、`supports(...)`、`getName()` 或策略枚举。
- 重要能力支持灰度开关、降级开关和运行时诊断。
- 文档至少包含快速开始、配置说明、扩展点说明、故障排查和升级指南。

### 2.4 框架/Starter 代码标准

框架代码的目标是“降低业务接入成本，而不是把业务绑死”。

强制要求：

- 自动装配只负责装配，不承载复杂业务流程。
- 使用 `@ConditionalOnProperty` 提供开关。
- 使用 `@ConditionalOnMissingBean` 允许业务覆盖默认实现。
- 使用 `@ConditionalOnBean` 避免无依赖时强行装配。
- 配置类统一命名为 `XxxProperties`，并绑定明确 prefix。
- 禁止在 starter 中扫描过宽包路径，避免污染业务上下文。
- 禁止 starter 隐式修改全局行为，必须通过配置或文档说明。

推荐实践：

- 提供最小可用默认实现。
- 提供业务可替换的接口端口。
- 使用 `AutoConfiguration.imports` 管理自动装配。
- 提供 auto-configuration 测试，验证开启、关闭、覆盖默认 Bean 等场景。

### 2.5 公共业务代码标准

公共业务代码介于基础设施与业务项目之间，既承载业务语义，又被多个项目复用。

强制要求：

- 必须有清晰领域边界和统一语言，禁止公共模块变成“业务垃圾桶”。
- 对外接口不得暴露 Entity、Mapper、Repository、内部状态机实现细节。
- 接口契约必须稳定，字段新增、枚举新增、错误码新增必须考虑调用方兼容。
- 必须显式建模租户、环境、权限、资源归属、审计等共享约束。
- 必须有权限边界和数据隔离策略。
- 必须提供可复用测试样例和典型使用方式。

推荐实践：

- 采用 ApplicationService + DomainService + DomainQueryService + 基础 Service 分层。
- 通过 DTO/Command/Query/Event 表达跨模块契约。
- 共享能力优先沉淀为内部 starter、client 或 adapter。
- 多项目复用前先明确 owner、版本策略、变更流程和兼容承诺。

### 2.6 业务项目（APP）代码标准

业务项目代码最接近需求变化，重点是正确交付、可读可改、团队一致。

强制要求：

- 按需求范围最小实现，不添加未来扩展。
- Controller 不写业务规则，不直接访问 Repository/Mapper。
- ApplicationService 负责编排，DomainService 承载状态变更，DomainQueryService 承载读模型。
- 查询使用 `XxxQuery`，分页和排序遵守统一 Query 规范。
- 对外 API 返回 DTO/VO/统一响应，不返回 Entity。
- 每个需求必须有对应测试或明确验证步骤。
- 任何临时方案必须有注释、风险说明或技术债记录。

推荐实践：

- 优先复用公共业务代码和基础设施能力。
- 复杂需求先写用例流程和状态机，再编码。
- 小步提交、小 PR、小范围重构。
- 对需求不确定处先提问，不自行脑补。

### 2.7 实验/工具/脚本代码标准

实验和脚本可以更轻，但不能突破安全和数据底线。

强制要求：

- 明确作用范围、运行环境、输入输出和回滚方式。
- 涉及数据修改必须 dry-run 或备份方案。
- 禁止把一次性脚本逻辑混入生产业务代码。
- 禁止硬编码密钥、token、生产地址和个人凭证。

推荐实践：

- 脚本放入 `tools`、`scripts` 或迁移专用目录。
- 重要脚本保留执行日志和参数样例。
- 验证完成后及时删除临时代码或转为正式工具。

## 3. 工程模块划分

### 3.1 推荐模块结构

默认采用“模块化单体优先，保留服务化演进路径”的结构：

```text
{app}
├── {app}-dependencies          # 依赖版本/BOM，统一管理第三方版本
├── {app}-core                  # 核心抽象、常量、枚举、基础模型、领域共享接口
├── {app}-common                # 通用工具，按需引入，禁止变成业务垃圾桶
├── {app}-face / {app}-api      # 对外暴露的接口契约、DTO、Client，可被其他服务依赖
├── {app}-biz                   # 业务模块集合，承载 application/domain/service 等业务代码
├── {app}-infrastructure        # 基础设施实现：DB、Cache、MQ、RPC、OSS、KMS、第三方 SDK
├── {app}-web                   # Web/Controller/Adapter/API 协议适配层
├── {app}-bootstrap             # Spring Boot 启动层，只做应用装配和启动
└── {app}-tests                 # 测试模块，集中提供测试基类、测试配置和集成测试
```

如果项目规模较小，可以合并 `face` 和 `core`；如果业务域复杂，可以将 `biz` 拆成多个业务域子模块。

### 3.2 模块职责

| 模块 | 职责 | 禁止 |
|------|------|------|
| dependencies | 管理依赖版本、插件版本、BOM | 写业务代码 |
| core | 稳定抽象、通用模型、错误码、枚举、资源定义 | 依赖 Web、DB、MQ、具体框架实现 |
| common | 通用工具、通用基础能力 | 放业务规则、业务常量、业务 DTO |
| face/api | 对外契约、DTO、Request、Client 接口 | 暴露 Entity、Mapper、内部实现类 |
| biz | 应用服务、领域服务、基础服务、业务规则 | 直接依赖 Controller、直接调用外部 SDK |
| infrastructure | Repository/Mapper、第三方 SDK 适配、缓存、消息实现 | 承载业务主流程 |
| web | Controller、Filter、Interceptor、协议转换 | 写领域规则、直接访问 Repository |
| bootstrap | 应用启动、配置装配 | 写业务逻辑 |
| tests | 测试基类、测试配置、集成测试 | 被生产模块依赖 |

### 3.3 依赖方向

强制依赖方向：

```text
bootstrap
   ↓
web
   ↓
biz
   ↓
core / face
   ↑
infrastructure
```

更准确地说：

```text
web -> biz -> core
infrastructure -> core / biz 中定义的 port
bootstrap -> web / biz / infrastructure
face/api -> core
biz 不直接依赖 infrastructure 的实现细节
```

强制规则：

- **禁止循环依赖**。
- **禁止 core 依赖 infrastructure、web、bootstrap**。
- **禁止 web 直接访问 Mapper/Repository**。
- **禁止业务代码直接依赖第三方 SDK**，应通过 `XxxClient` / `XxxGateway` / `XxxOperations` 端口隔离。
- **tests 可以依赖所有模块**，生产模块不得依赖 tests。

### 3.4 业务域包结构

推荐在业务域内按职责组织，而不是把所有类堆到 `service`：

```text
com.xxx.user
├── application                  # 场景服务 / 用例编排
│   └── UserLoginApplicationService
├── domain                       # 领域模型与领域服务
│   ├── UserDomainService
│   └── UserDomainQueryService
├── service                      # 基础服务，封装数据访问
│   ├── UserService
│   └── impl
├── infrastructure / dal          # Mapper、Repository、Entity、TypeHandler
│   ├── entities
│   ├── enums
│   └── mapper
├── model
│   ├── command
│   ├── dto
│   ├── query
│   ├── request
│   └── vo
├── converter / mapstruct         # 模型转换
├── enums
└── event
```

如果项目沿用 `dal/services/model/mapstruct` 风格，可以保留，但必须保证职责不混乱。

### 3.5 模块命名

- `groupId`：`com.{company}.{app}[.{domain}]`
- `artifactId`：`{app}-{module}` 或 `{app}-{domain}-{module}`
- 应用名：字母开头，只包含小写字母、数字、短横线或下划线，长度建议 3~20。
- 业务模块名使用英文业务语义，禁止拼音、中文和无意义缩写。

## 4. 依赖管理

### 4.1 Maven/BOM 规则

- **强制**：根 POM、父 POM 或 `{app}-dependencies` 统一管理所有第三方依赖版本。
- **强制**：子模块引用依赖时不写版本号。
- **强制**：插件版本统一放在 `pluginManagement`。
- **强制**：禁止同一依赖多个版本并存。
- **推荐**：内部模块版本由根版本统一控制。
- **推荐**：使用 Maven Enforcer 检查依赖收敛、Java 版本、重复类和禁止依赖。

### 4.2 依赖引入原则

- 引入新依赖前先确认项目是否已有等价能力。
- 基础库优先选择成熟、维护活跃、团队熟悉的方案。
- 禁止为了少量代码引入重量级框架。
- 安全、序列化、表达式、脚本、反射、字节码类依赖必须特别评审。
- Web、DB、MQ、Redis、OSS、KMS 等外部能力必须通过基础设施适配层隔离。

### 4.3 Starter/AutoConfiguration 规则

参考 Spring Boot Starter 和 SOFAStack 模块化思想，通用能力应做成可插拔模块：

- 自动装配类命名：`XxxAutoConfiguration`。
- 配置模型命名：`XxxProperties`。
- 使用 `@ConditionalOnProperty` 控制开关。
- 使用 `@ConditionalOnMissingBean` 允许业务方覆盖默认实现。
- 使用 `@ConditionalOnBean` 组合已有能力。
- AutoConfiguration 只做装配，不写复杂业务逻辑。
- Spring Boot 3+ 使用 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 注册自动装配。

## 5. 服务层划分与调用关系

### 5.1 四类 Service

服务层只允许以下四类：

| 类型 | 命名 | 职责 | 返回模型 |
|------|------|------|----------|
| 基础服务 | `{实体}Service` | 数据访问协调、基础 CRUD、简单查询 | Entity/DTO/Optional |
| 领域写服务 | `{实体}DomainService` | 聚合规则、状态变更、领域事件 | Entity/基本类型/void |
| 领域读服务 | `{实体}DomainQueryService` | 查询模型、列表、分页、统计 | DTO/VO/Page/List |
| 场景服务 | `{业务场景}ApplicationService` | 用例编排、事务边界、跨领域流程 | DTO/Result/void |

禁止新增含义模糊的类型：`Manager`、`Facade`、`BizService`、`HandlerService` 等，除非它是明确的基础设施或框架扩展点，并在设计文档中说明。

### 5.2 调用链

```text
Controller / Adapter
   ↓
ApplicationService
   ↓
DomainService       DomainQueryService
   ↓                     ↓
{实体}Service        {实体}Service
   ↓
Repository / Mapper
```

强制规则：

- `DomainService` 不得调用 `DomainQueryService`。
- `DomainQueryService` 不得调用 `DomainService`。
- 除 `{实体}Service` 外，其他 Service 不得直接访问 Repository/Mapper。
- ApplicationService 负责编排，不沉淀细粒度领域规则。
- DomainService 负责对象如何变化，不处理列表/分页查询。
- DomainQueryService 只读，不修改状态。

### 5.3 Entity 暴露边界

为明确 Entity 使用边界，统一规定：

- **Controller / Web API / face/api 对外契约禁止暴露 Entity**。
- **ApplicationService 对外返回 DTO/VO/Result，不返回 Entity**。
- **DomainQueryService 返回 DTO/VO，不返回 Entity**。
- **DomainService 和基础 `{实体}Service` 可在模块内部返回 Entity**，但不得跨边界泄露到 Web/API。

一句话：Entity 可以在内部领域边界流动，不能出现在对外接口边界。

## 6. 服务方法命名

### 6.1 查询动词

| 动词 | 语义 | 返回 | 规则 |
|------|------|------|------|
| `getXxx` | 必然存在 | Entity/VO/DTO | 查不到抛业务异常，不返回 Optional |
| `findXxx` | 可能不存在 | Optional/可空 VO | 查不到是正常情况 |
| `queryXxx` | 条件查询/列表/分页 | List/Page/Pagination | 参数使用 `XxxQuery` |
| `existsXxx` | 是否存在 | boolean | 不抛不存在异常 |
| `countXxx` | 数量统计 | long | 返回数量 |
| `statsXxx` | 统计 | DTO | 多指标统计 |
| `summaryXxx` | 汇总 | DTO | 汇总视图 |

禁止：

- `getXxxList`、`findXxxPage`、`queryXxx` 返回单个必然存在对象。
- 服务层使用 Repository 语义：`select`、`fetch`、`load`。
- 查询方法使用多个散装参数，除非只有唯一标识条件。

### 6.2 写操作动词

领域写服务只允许使用业务变更动词：

```text
create / update / save
bind / unbind
submit / approve / reject
freeze / unfreeze
enable / disable
close / cancel
pay / refund / settle
```

写方法必须表达业务意图，不要用 `handle`、`process`、`doXxx` 这类模糊词。

### 6.3 实体型与场景型判定

- 回答“对象怎么变” → `DomainService`。
- 回答“业务怎么走” → `ApplicationService`。

命中下列两条及以上，优先归为场景服务：

- 跨实体/跨聚合。
- 返回 DTO/Result。
- 方法名是业务场景动词，如 login、pay、submit。
- 流程中包含权限、事务、外部调用、消息或多个领域对象编排。

## 7. Query DTO 与查询字段命名

### 7.1 基本规则

查询字段命名使用：

```text
<field><OperatorSuffix>
```

默认等值查询不加后缀：

```text
status       -> status = ?
name         -> name = ?
```

语义优先于 SQL，推荐使用业务语义后缀，不直接表达 SQL 细节。

### 7.2 标准后缀

| 类型 | 后缀 | 示例 |
|------|------|------|
| 不等于 | `Ne` | `statusNe` |
| 包含集合 | `In` | `statusIn` |
| 不包含集合 | `NotIn` | `statusNotIn` |
| 包含匹配 | `Contains` | `nameContains` |
| 前缀匹配 | `StartsWith` | `codeStartsWith` |
| 后缀匹配 | `EndsWith` | `emailEndsWith` |
| 自定义 LIKE | `Like` | `nameLike` |
| 大于 | `Gt` | `amountGt` |
| 大于等于 | `Gte` | `amountGte` |
| 小于 | `Lt` | `amountLt` |
| 小于等于 | `Lte` | `amountLte` |
| 最小值，含边界 | `Min` | `createdAtMin` |
| 最大值，含边界 | `Max` | `createdAtMax` |
| 区间 | `Between` | `createdAtBetween` |
| 为空 | `IsNull` | `deletedAtIsNull` |
| 非空 | `IsNotNull` | `deletedAtIsNotNull` |

时间和数值范围统一使用 `Min/Max`，禁止同一项目混用 `Start/End`、`Begin/End`、`From/To`。

### 7.3 Query 对象规则

- 查询对象统一命名为 `XxxQuery`。
- 分页查询继承统一分页基类。
- 分页大小必须有最大值限制。
- 排序字段使用枚举或字段常量白名单，禁止前端直接传数据库字段名。
- 排序参数统一为 `orderFields` + `orderTypes`。
- 深分页优先使用游标分页。

## 8. API 设计规范

### 8.1 Web API

- Controller 只做协议适配、参数校验、权限入口和响应转换。
- Controller 不写业务规则，不访问 Repository/Mapper。
- 对外 API 返回统一响应模型，必须包含 traceId。
- API 入参使用 Request/Query，不直接接收 Entity。
- API 出参使用 DTO/VO，不直接返回 Entity。
- 错误码、错误消息、HTTP 状态码或 RPC 错误契约必须统一。

### 8.2 内网 API

内网 API 路径统一：

```text
/inc/{security-level}/{domain}/{resource}/{action}
```

安全等级：

| 前缀 | 用途 | 策略 |
|------|------|------|
| `/inc/basic/**` | 低风险内网基础接口 | 仅限内网访问，可不验签 |
| `/inc/secure/**` | 用户数据、资金、权限、关键业务操作 | 内网访问 + 强制接口验签 |
| `/api/**` | 公网 API | OAuth/Token/Session 等公网认证 |

强制规则：

- `/inc` 只允许内网调用，禁止公网暴露。
- `/inc/secure/**` 必须校验 appKey、timestamp、nonce、signature。
- 安全等级由路径表达，不依赖 Header 或参数临时判断。
- 网关、拦截器、AOP 至少一层强制执行安全策略。

### 8.3 外部集成 API

- 业务代码依赖端口接口，例如 `WindOssClient`、`WindCryptoClient`、`MessageSender`。
- 厂商 SDK 封装在 infrastructure 或独立 adapter 模块。
- 外部调用必须考虑超时、重试、限流、幂等、降级、告警和审计。
- 对外部异常进行包装，不向业务层泄露 SDK 原始异常。

## 9. 编码原则

### 9.1 命名

- 类名使用 `UpperCamelCase`，方法/变量使用 `lowerCamelCase`，常量使用 `UPPER_UNDERSCORE`。
- 禁止拼音、中文、无意义缩写。
- 名称表达业务意图，不表达实现细节。
- 设计模式参与命名时应体现模式，如 `XxxStrategy`、`XxxFactory`、`XxxAdapter`。
- 枚举必须实现 `DescriptiveEnum` 或等价描述接口。
- 同一业务概念必须使用同一术语，禁止同义词混用，例如 account、wallet、balance 未定义前不得混用。
- 禁止使用过宽词汇掩盖职责，例如 `handle`、`process`、`manager`、`data`、`info`、`logic`。

### 9.2 模型命名

| 类型 | 命名 |
|------|------|
| 创建请求 | `CreateXxxRequest` |
| 更新请求 | `UpdateXxxRequest` |
| 不区分创建/更新 | `SaveXxxRequest` |
| 命令对象 | `XxxCommand` |
| 查询对象 | `XxxQuery` |
| DTO | `XxxDTO` / `XxxDetailDTO` / `XxxListDTO` |
| VO | `XxxVO` |
| 事件 | `XxxEvent` |
| 转换器 | `XxxConverter` |

MapStruct 方法命名：`convertToXxx`、`convertToXxxDTO`、`convertToEntity`。

### 9.3 函数与类

- 方法短小，只做一件事。
- 参数超过 5 个必须抽取参数对象；公共方法超过 3 个参数应优先考虑参数对象。
- 函数内抽象层级一致，不把校验、查询、转换、持久化、通知揉在一起。
- 类职责单一，避免上帝类。
- 优先组合而非继承。
- 公共 API 必须有 Javadoc，说明意图、参数约束、返回语义和异常。

### 9.4 注释与技术表达

代码注释和技术文档是系统可维护性的一部分，必须服务理解和协作。

强制规则：

- 公共接口、公有方法、DTO/Request/Query、配置属性、扩展点必须有 Javadoc。
- 注释说明“为什么这样做、边界是什么、风险是什么”，不重复代码显而易见的行为。
- 复杂规则必须给出业务语义、输入输出、边界条件和示例。
- 临时方案必须标注原因、影响范围、替代方案或计划清理时间。
- 禁止保留大段注释掉的废弃代码。

推荐表达：

```java
/**
 * 查询用户明细。
 *
 * <p>用于后台用户详情页。用户不存在或已逻辑删除时抛出业务异常。
 *
 * @param userId 用户 ID
 * @return 用户明细
 */
UserDetailDTO getUserDetail(Long userId);
```

表达原则：

- 先讲业务语义，再讲技术实现。
- 主语、动作、对象、条件、结果必须明确。
- 中文说明追求短、准、稳，避免空泛词。
- 中英文混排保持一致，技术词不硬翻，业务词不乱拼音。

### 9.5 空值与断言

- 公共 API 使用 `@Nullable` / `@NonNull` / `@NotNull` / `@NotBlank` 表达契约。
- 参数校验优先使用 `AssertUtils` 或 Bean Validation。
- 返回集合时返回空集合，不返回 null。
- `findXxx` 推荐返回 `Optional<T>`。
- `getXxx` 查不到必须抛业务异常。

### 9.6 异常

- 业务异常继承或使用 `BaseException`。
- 异常必须携带错误码或可归类的异常类型。
- 禁止吞异常。
- 事务方法中捕获异常后必须重新抛出或显式回滚。
- 包装第三方异常时保留 cause。
- 对用户提示和内部诊断信息分层处理。

### 9.7 时间与金额

- 时间使用 `LocalDateTime`、`LocalDate`、`LocalTime`，禁止新代码使用 `Date`。
- 默认前后端格式：`yyyy-MM-dd HH:mm:ss`、`yyyy-MM-dd`、`HH:mm:ss`。
- 金额使用 `BigDecimal`，禁止 `new BigDecimal(double)`。
- 金额字段必须明确币种、精度、舍入规则。

## 10. 数据访问与数据库规范

### 10.1 MyBatis Flex

- 强制：查询禁止使用 `LambdaQueryWrapper`，优先使用生成的字段常量类，如 `XxxRefs`。
- 一般插入使用 `insertSelective`。
- 一般更新使用 `update` 或指定列更新，注意 null 忽略行为。
- 需要将字段更新为 null 时必须显式指定更新列，并处理 `gmt_modified`。
- QueryWrapper 构造逻辑应集中在 helper 或基础服务，避免到处手写条件。

### 10.2 数据库设计

- 表必须包含：`id`、`gmt_create`、`gmt_modified`。
- 可选通用字段：`creator`、`modifier`、`order_index`。
- 业务唯一约束必须使用数据库唯一键保证。
- 新增必填字段必须有默认值，否则字段应允许为空并配合兼容逻辑。
- 删除字段、改字段名、改字段类型必须先做兼容发布，再执行 DDL。
- 禁止数据库外键和级联删除，外键关系在应用层管理。
- 逻辑删除字段查询时必须在基础服务或查询 helper 中统一处理。

### 10.3 索引与查询

- 高频查询条件必须评估索引。
- 排序字段需要结合索引设计。
- 禁止无条件大列表查询。
- 分页大小必须限制。
- 深分页使用游标分页、搜索引擎或离线导出方案。
- 模糊查询优先评估前缀匹配、全文索引或搜索服务，不滥用 `%keyword%`。

## 11. 日志规范

### 11.1 基本原则

- 统一使用 SLF4J，不使用 `System.out.println`。
- 日志必须服务定位问题，不打印无意义流水账。
- 日志必须带关键上下文：traceId、业务 id、用户 id、租户、请求来源、外部调用目标。
- 敏感信息必须脱敏，包括手机号、邮箱、身份证、银行卡、密码、token、密钥。
- 错误日志必须打印错误消息和异常堆栈。

### 11.2 格式

推荐格式：

```java
logger.info("Processing trade, tradeId = {}, symbol = {}", tradeId, symbol);
logger.error("Handle payment error, orderNo = {}, message = {}", orderNo, exception.getMessage(), exception);
```

强制规则：

- 使用占位符，不使用字符串拼接。
- 英文逗号后加空格。
- key/value 风格保持一致。
- `error` 日志最后一个参数传异常对象。
- 不重复打印同一个异常；异常如果会被全局处理器打印，业务层只在必要时补充上下文。

### 11.3 日志级别

| 级别 | 场景 |
|------|------|
| ERROR | 影响请求成功、任务失败、数据不一致、外部依赖异常 |
| WARN | 可恢复异常、降级、重试、配置异常、边界风险 |
| INFO | 关键业务节点、状态变更、外部调用摘要 |
| DEBUG | 诊断信息、条件分支、调试细节 |
| TRACE | 极细粒度调试，默认关闭 |

## 12. 安全规范

- 公网 API 必须经过认证与授权。
- 内网 secure API 必须验签。
- 权限模型应区分资源、角色、权限、用户/主体。
- Token 必须考虑过期、刷新、撤销、设备隔离。
- 验证码必须考虑有效期、验证次数、发送次数和流控。
- MFA 用于高风险动作，如资金、权限、敏感信息变更。
- 日志和异常响应禁止泄露密钥、token、SQL、内部路径和敏感个人信息。
- 文件上传必须校验类型、大小、扩展名、内容嗅探、存储路径和访问权限。
- 引入依赖必须关注漏洞扫描和许可证风险。

## 13. 测试实践

测试驱动设计、测试分层、测试代码整洁、测试资产治理和 Review 清单详见 `testing.md`。本节只保留项目级落地规则。

### 13.1 测试分层

| 类型 | 目标 | 工具 |
|------|------|------|
| 单元测试 | 验证纯业务规则、工具、领域服务 | JUnit 5、Mockito、AssertJ |
| 应用服务测试 | 验证用例编排和事务边界 | Spring Boot Test 按需加载 |
| 数据访问测试 | 验证 Mapper/Repository/SQL | H2/Testcontainers |
| 集成测试 | 验证外部适配器、AutoConfiguration | Spring Boot Test、WireMock |
| 架构测试 | 验证依赖方向和分层规则 | ArchUnit |
| 回归测试 | 防止历史 bug 复现 | 针对 bug 补测试 |

### 13.2 测试规则

- 强制：所有测试统一写到 `tests` 模块或项目统一测试模块。
- 强制：测试类以 `Test` 结尾。
- 强制：测试方法以 `test` 开头。
- 强制：测试类包名与被测试类保持一致。
- 强制：每个测试方法至少一个断言。
- 强制：测试代码等同生产代码维护，命名、结构、测试数据、辅助方法和断言都必须清晰。
- 强制：每个测试用例必须能表达测试场景、业务意图、输入条件和期望输出；复杂场景使用注释或局部变量名说明。
- 推荐：一个测试只验证一个逻辑分支。
- 推荐：异常和边界场景使用 `testXxxWithYyy` 命名。
- 推荐：测试结构采用 Given/When/Then 或 Arrange/Act/Assert，避免准备、执行和断言混杂。
- 推荐：Spring 上下文按需加载，不滥用全量启动。

### 13.3 可测试设计

- 时间、随机数、外部接口、线程池、副作用通过接口注入。
- 私有复杂逻辑优先提取为可测试的小对象；确需放宽可见性时使用 `@VisibleForTesting`。
- 新增缺陷修复必须补回归测试。
- 修改接口契约时，测试、实现、转换、落库、断言必须闭环。
- 测试坏味道、慢测试、脆弱测试、过度 Mock 和测试资产治理要求统一参考 `testing.md`。

## 14. 前端项目协作规范

架构师介入前端项目时，目标是帮助前后端分离项目形成清晰契约、稳定工程边界和可维护实现，而不是用后端习惯替代前端实践。

### 14.1 介入前必读

进入前端代码库前，必须先阅读项目自身规范：

- `package.json`：脚本、依赖、包管理器、Node 版本约束。
- `tsconfig.json`：TypeScript 严格程度、路径别名、模块解析。
- ESLint：`.eslintrc*`、`eslint.config.*`。
- Prettier：`.prettierrc*`。
- Stylelint：`.stylelintrc*`。
- Husky / lint-staged：提交前检查规则。
- 项目 README、目录规范、组件库约定、路由和权限约定。

强制规则：

- 不删除 ESLint、Husky、类型检查、格式化配置。
- 不绕过 Husky 检测提交。
- 不在不了解影响范围时修改全局样式。
- 不使用 `any` 逃避类型设计；确需使用必须说明原因并收敛作用域。

### 14.2 前端代码原则

- 可读写优先：组件、Hook、工具函数职责清晰，命名表达业务语义。
- 易用性优先：页面流程清楚，反馈及时，错误提示可理解。
- 可维护性优先：状态边界清晰，副作用集中，组件不过度抽象。
- 类型安全优先：用 TypeScript 表达接口、状态、事件和 API 响应约束。
- 复用优先：已有组件库和工具库能满足需求时，不重复手写。
- 局部影响：样式和状态优先局部化，避免全局污染。

### 14.3 文件与组件命名

- 组件文件使用 PascalCase，例如 `UserProfileCard.tsx`。
- 非组件文件使用 lowerCamelCase，例如 `formatAmount.ts`、`useUserQuery.ts`。
- Hooks 使用 `useXxx`。
- 高阶组件使用 `withXxx`。
- 常量按项目规范使用 `UPPER_UNDERSCORE` 或具名对象集中管理。
- 单组件不超过 400 行；新增复杂功能建议控制在 200 行左右并主动拆分。

### 14.4 React/TypeScript 实践

- 组件拆分优先按职责：容器组件、展示组件、表单组件、业务 Hook、工具函数。
- 三目运算只允许一层，复杂条件提取为具名变量或函数。
- 避免在 JSX 中堆复杂表达式。
- API 响应、表单模型、路由参数、组件 Props 必须有类型。
- 副作用放入 Hook，并明确依赖项。
- 列表渲染必须使用稳定 key。
- 表单、表格、筛选、分页、弹窗、空状态、错误状态优先遵循团队组件库或 Ant Design 模式。

### 14.5 前后端契约

- 接口字段命名、错误码、分页、排序、筛选、日期时间格式必须前后端统一。
- API 变更必须兼容旧前端或同步发布，禁止后端单方面删除字段或改变语义。
- 前端需要明确处理 loading、empty、error、permission denied、timeout 等状态。
- 鉴权、刷新 token、权限路由、菜单资源、按钮权限需要与后端权限模型对齐。
- traceId 应在错误提示、日志或问题反馈链路中可追踪。

### 14.6 前端评审清单

- 是否先遵守项目自身 ESLint/Prettier/tsconfig/Husky？
- 是否引入 `any`、嵌套三目、超大组件或复杂 JSX？
- 是否修改了全局样式，影响范围是否明确？
- 是否复用了已有组件库，而不是重复造轮子？
- Props、API 响应、表单值、路由参数是否类型完整？
- loading、empty、error、权限不足、接口超时是否处理？
- 前后端字段、错误码、分页、排序、时间格式是否一致？
- 是否有必要的单元测试、组件测试或 E2E 验证？

## 15. Git 协作与 PR

### 15.1 分支

- `feature_{版本号或功能tag}`：功能/需求分支。
- `dev_{开发者}`：个人开发分支。
- `pr_{开发者或功能tag}`：PR 临时分支，可选，合并后删除。
- `bugfix_{bugtag或开发者}`：线上修复分支。
- `master`：发布主分支。
- `tag/{版本或功能或bugfix}`：上线后打 tag。

强制规则：

- 禁止 force push 到共享分支。
- 热修复上线后必须合并回 master，并打 tag。
- 无用开发分支及时清理。
- 解决冲突时不得覆盖他人代码；不确定必须找相关开发一起处理。

### 15.2 Commit

推荐格式：

```text
<type>(<scope>): <subject>

<body>
```

`type`：`feat`、`fix`、`docs`、`style`、`refactor`、`test`、`chore`。

AI 参与时追加：

```text
Assisted-by: [Model Name] via [Tool Name]
```

### 15.3 PR

- PR 要小而完整，建议 15~20 个文件以内；大量 DTO/生成代码需说明。
- 按层提交：dal/entity -> service/domain -> application -> web -> tests。
- PR 必须说明：背景、改动点、验证方式、风险、回滚方案。
- 频繁小 PR，避免攒到最后导致冲突和审查失效。
- 合并前必须通过编译、相关测试和静态检查。

## 16. 代码评审与设计评审

### 16.1 设计评审清单

- 模块边界是否清晰？
- 依赖方向是否符合规范？
- 领域模型是否表达业务不变量？
- 服务类型是否归类正确？
- 数据模型是否支持唯一约束、状态流转和审计？
- API 是否暴露 Entity 或内部实现？
- 内网 API 安全等级是否正确？
- 外部调用是否考虑超时、重试、幂等、限流和补偿？
- 日志、指标、traceId 是否贯通？
- 测试和验收标准是否明确？
- 文档是否说明背景、目标、非目标、约束、取舍、风险和回滚？
- 关键术语是否定义清楚，是否存在同一概念多种叫法？

### 16.2 代码评审清单

- 是否有无关改动或顺手重构？
- `get/find/query` 是否误用？
- Query 字段后缀是否符合规范？
- Service 是否直接访问 Mapper？
- Controller 是否写业务逻辑？
- 是否暴露 Entity 到 Web/API？
- 是否使用 `BaseException` / `AssertUtils`？
- 是否有 `System.out.println`、`e.printStackTrace()`？
- 错误日志是否包含 message 和异常栈？
- 敏感信息是否脱敏？
- 测试是否覆盖正常、异常、边界场景？
- 命名、注释和 Javadoc 是否准确表达业务语义？
- 是否存在空泛命名，如 `handleData`、`processInfo`、`doLogic`？

### 16.3 文档评审清单

- 是否明确读者是谁：产品、研发、测试、运维、管理者？
- 是否先说明问题，再说明方案？
- 是否区分目标和非目标？
- 是否有边界、约束、风险、取舍和验收标准？
- 是否有必要的图、表、示例、反例或检查清单？
- 是否言辞简练，删除了空话、套话和重复话？
- 是否主语明确、动作明确、对象明确、条件明确、结果明确？
- 是否同一术语前后一致？
- 是否能被新人按文档独立理解和执行？

## 17. 重构与演进

### 17.1 重构原则

- 重构必须行为保持，不和功能变更混在一个 PR。
- 重构前先补测试或确认已有测试保护。
- 每次只改一个维度：命名、拆方法、拆类、移动包、解耦依赖，不混杂。
- 大规模重构必须先写设计说明和迁移计划。
- 旧接口废弃必须使用 `@Deprecated` 并说明替代方案和删除版本。

### 17.2 模块演进路径

推荐演进路线：

```text
单体
 -> 分层单体
 -> 模块化单体
 -> 关键模块服务化
 -> 平台化/中台化能力
```

不要一开始就微服务化；只有当团队边界、发布边界、伸缩边界、数据边界都清晰时，才拆服务。

### 17.3 平台化沉淀

当一个能力满足以下条件时，可以沉淀为公共模块或 starter：

- 被两个以上业务域复用。
- 有稳定接口和清晰扩展点。
- 可以通过配置开关启用/禁用。
- 默认实现可被业务覆盖。
- 有单元测试、集成测试和使用样例。

## 18. 容器化与 Kubernetes 落地规范

容器化规范用于保证架构决策能在 Kubernetes 环境中稳定运行，而不是只停留在设计文档中。

### 18.1 镜像规范

- Dockerfile 使用多阶段构建，运行镜像只包含运行所需内容。
- 生产镜像禁止使用 `latest`，必须使用不可变 tag，例如版本号、commit id、构建号。
- 镜像内禁止写入环境配置、密钥、token、生产地址。
- Java 镜像必须明确 JDK/JRE 版本、时区、证书、字体和字符集需求。
- 容器应使用非 root 用户运行。
- 日志输出到 stdout/stderr，不写死本地日志目录作为唯一日志出口。

### 18.2 配置与密钥

- 普通配置使用 ConfigMap、环境变量或配置中心。
- 密钥使用 Secret 或专用密钥系统，禁止进入 Git、镜像和日志。
- 配置必须区分环境，禁止在代码中通过 `if prod` 之类逻辑硬编码环境差异。
- 配置变更必须有回滚方式，高风险配置应支持灰度。

### 18.3 资源与 JVM

- 必须配置 CPU/Memory `requests` 与 `limits`。
- JVM 参数必须适配容器资源限制，关注堆、直接内存、Metaspace、线程栈和 GC。
- 重点监控 OOMKilled、CPU throttling、GC pause、线程数、连接池耗尽。
- 线程池、连接池、队列大小不能只按物理机经验配置，必须结合 Pod 资源。

### 18.4 健康检查与优雅停机

- 必须配置 readinessProbe，避免未就绪流量进入。
- 必须配置 livenessProbe，避免僵死实例长期占用流量。
- 启动慢的 Java 应用建议配置 startupProbe。
- 优雅停机必须处理 SIGTERM、请求排空、线程池关闭、MQ 消费停止、定时任务中断和临时状态落盘。
- `terminationGracePeriodSeconds` 必须与应用最长安全停止时间匹配。

### 18.5 发布、扩缩容与回滚

- 默认支持滚动发布；高风险功能使用蓝绿、金丝雀或特性开关。
- 数据库变更必须向前兼容，避免新旧版本 Pod 并存时互相破坏。
- HPA 指标不能只看 CPU；核心业务可结合 QPS、RT、队列长度、消费堆积等指标。
- 关键服务配置 PodDisruptionBudget 和反亲和，降低节点故障影响。
- 回滚方案必须覆盖镜像、配置、数据库兼容和消息积压处理。

### 18.6 安全与网络

- 使用 Namespace 隔离环境或业务域。
- 使用 RBAC 和 ServiceAccount 做最小权限控制。
- 有条件时使用 NetworkPolicy 限制服务间访问路径。
- Ingress/Gateway 必须明确公网、内网、管理端入口边界。
- 镜像和依赖进入生产前必须做漏洞扫描。

### 18.7 K8s 评审清单

- 镜像是否不可变、可追溯、无密钥？
- 配置和 Secret 是否外置且可回滚？
- requests/limits 是否合理，JVM 是否适配容器内存？
- 探针是否区分启动、就绪、存活？
- 是否支持优雅停机？
- 发布时新旧版本是否兼容数据库、缓存、消息和外部接口？
- 是否具备日志、指标、trace、告警和仪表盘？
- 是否考虑副本数、PDB、反亲和、HPA 和容量基线？

## 19. SOFAStack 参考实践吸收

SOFAStack 的启发主要体现在三点：

- **模块化开发**：模块应具备独立代码、配置和上下文边界，模块间通过清晰 API 通信，而不是随意互相调用内部类。
- **分层插件化**：核心层定义扩展机制，功能实现层通过模块方式插入，降低核心与实现耦合。
- **类隔离/应用隔离思想**：当项目复杂到多版本依赖冲突、模块热部署或独立演进时，需要从普通模块化升级为更强的隔离机制。

落地到当前团队：

- 先把模块边界、依赖方向、接口契约和测试门禁做好。
- 公共能力优先做成内部 starter 或可插拔模块。
- 对厂商 SDK、外部系统、基础设施能力建立端口与适配器。
- 当普通 Maven 模块已无法解决依赖冲突或发布隔离时，再评估 SOFAArk 类隔离/插件化模型。

## 20. 最小落地门禁

每个项目至少具备以下门禁：

- 编译通过：`mvn compile`。
- 相关单测通过：`mvn test -Dtest=<相关测试类>`。
- 接口/实体/注解/重命名类变更后：`mvn clean test-compile`。
- 静态检查：P3C / PMD / SpotBugs / SonarLint 至少一种。
- PR 清单：说明改动、测试、风险、回滚。
- 禁止项扫描：`System.out.println`、`e.printStackTrace()`、密钥、token、`.env`。
- 架构边界检查：可逐步引入 ArchUnit。
