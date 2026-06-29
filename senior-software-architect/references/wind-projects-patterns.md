# Wind 项目族架构与 API 提炼

本文从以下仓库提炼资深架构师在 Java/Spring/Wind 项目中的项目级实践样本：

- wind-middleware：https://github.com/fengwuxp/wind-middleware
- wind-integration：https://github.com/fengwuxp/wind-integration
- wind-security：https://github.com/fengwuxp/wind-security

## 使用时机

- 用户正在处理 Java/Spring/Wind 项目族、Wind/Nobe 风格项目或需要复用 Wind 基础能力。
- 需要判断统一响应、Trace、端口适配、Spring Boot Starter、查询分页、安全域、企业集成和模块治理的本地风格。
- 需要从公开 Wind 项目族中提炼可迁移的工程模式，但不直接复制实现。

## 不适用场景

- 非 Java/Wind 项目先读 `language-agnostic-architecture.md`。
- 具体编码强规约优先读 `coding-standards.md`，项目级治理优先读 `project-governance-standards.md`。
- 不把公开项目样本当成当前项目必须照抄的架构；仍以当前仓库事实和用户目标为准。

## 读取后必须产出

- 当前任务是否命中 Wind 项目族能力，以及应复用的端口、模式、模块边界或约规。
- 明确哪些是可迁移模式，哪些需要读取当前项目代码后确认。
- 对新增能力优先检查是否已有 WindXxx 接口、starter、helper、query、trace、安全或集成能力。

## 需要继续读取的 reference

- Java/Spring/Wind 强制约规读 `coding-standards.md`。
- 项目治理综合规范读 `project-governance-standards.md`。
- Review 输出读 `coding-review-deep-dive.md`；生产和安全读对应专项 reference。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Wind 项目族能力识别 | `1. 总体架构定位`、`5. 模块治理提炼` | 不把模块地图当作当前项目真实依赖 |
| API 和契约风格 | `2. API 设计风格` | 不绕过统一响应、traceId、错误码和空值契约 |
| 编码风格和公共模型 | `3. 编码风格提炼` | 不替代 `coding-standards.md` |
| 端口适配和 Starter 模式 | `4. 架构模式提炼` | 不让业务代码直接依赖厂商 SDK |
| Java/Wind 落地 Review | `6. 对资深架构师 Skill 的 Java/Wind 落地要求`、`7. 可复用检查清单` | 不重复造已有基础能力 |

## 1. 总体架构定位

### 1.1 项目族分层

- `wind-middleware` 提供应用运行底座和基础协议，优先沉淀跨项目通用能力。
- `wind-integration` 提供企业应用集成能力，重点是外部服务抽象、适配器和基础设施扩展。
- `wind-security` 专注安全域，围绕认证、授权、验证码、MFA、JWT 建立独立能力层。
- 三者共同采用“接口定义核心能力 + 适配器实现外部细节 + Spring Boot 自动装配”的模式。

### 1.2 能力分层原则

- 核心 API 使用接口、record、不可变对象和领域命名表达业务能力。
- 外部厂商、框架、中间件实现放在独立模块，例如 `wind-oss-alibabacloud`、`wind-kms-alibabacloud`、`wind-oss-spring-boot-starter`。
- 自动装配模块使用 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 暴露 Spring Boot starter 能力。
- 项目模板使用 face/biz/core/infrastructure/web/bootstrap/tests 多模块结构，示范应用边界。

## 2. API 设计风格

典型接口：`ApiResponse<T>`、`WindTracer`、`WindOssClient`、`MessageDefinition<T>` / `MessageSender<M>`、`AuthenticationTokenCodecService`、`CaptchaManager`、`MultiFactorAuthenticator`。

- 面向能力定义接口，不面向具体框架定义接口。
- 接口方法体现业务语义，例如 `generateToken`、`parseAndValidateToken`、`revokeAllToken`、`verify`、`uploadFile`。
- 可选能力使用 default 方法提供便利重载，核心能力保留抽象方法。
- 支持扩展的接口必须提供 `supports(...)` 或唯一 `getName()` 识别机制。

### 2.1 统一响应与异常

- 业务异常必须携带错误码和可诊断消息。
- 对外响应必须包含 traceId。
- 异常转换应集中处理，避免 Controller 分散 try/catch。
- 友好提示与内部错误诊断信息要分层处理。

### 2.2 空值与参数约束

- 内部 Java 契约用 JSpecify，API 数据契约用 Bean Validation，其他前置条件和状态条件用 `AssertUtils`。
- 已由 JSpecify 标注为非空的普通参数、返回值和字段，不再重复写无业务语义的空判断。
- 可空返回值必须通过注解或 Optional 明确表达。

## 3. 编码风格提炼

- 命名：基础能力使用 `Wind` 前缀；不可变模型用 `ImmutableXxx`；配置类用 `XxxProperties`；自动装配类用 `XxxAutoConfiguration`；能力抽象常用 `XxxClient`、`XxxOperations`、`XxxManager`、`XxxStorage`、`XxxFactory`、`XxxProvider`、`XxxRepository`。
- 类结构：工具类防实例化；简单模型可用 Lombok 或 record；组合模式可用 record 简化；可测试可见性用 `@VisibleForTesting`，不随意扩大生产 API。
- 文档与错误：公共接口、公有方法和核心模型保留 Javadoc；业务前置条件优先 `AssertUtils`；错误信息包含参数名、资源名、场景名；可忽略异常必须限制范围并写明意图。

## 4. 架构模式提炼

### 4.1 Port-Adapter / SPI 模式

典型样本：

- OSS：`WindOssClient` 是端口，`AlibabaCloudOssClient` 是适配器。
- KMS：`WindCryptoClient`、`WindKmsClientProvider` 是端口，阿里云 KMS 模块是适配器。
- 消息：`MessageSender` 是端口，钉钉、邮件等模块是适配器。
- 凭证：`WindCredentialsProvider` 通过 `META-INF/services` 提供 SPI 扩展。

落地原则：

- 先定义业务能力端口，再实现厂商适配器。
- 厂商 SDK 依赖不得泄露到核心接口。
- SPI 适合跨模块、低耦合、运行时发现的基础能力。
- Spring Bean 适合应用内可装配能力，SPI 适合库级可发现能力。

### 4.2 Composite + supports 扩展模式

典型样本：

- `CompositeMessageSender` 根据 `supports(messageType)` 分发到对应发送器。
- `DefaultCaptchaManager` 根据 `supports(type, scene)` 找到验证码生成器和发送器。
- `CompositeMultiFactorAuthenticator` 根据 MFA 类型选择认证器。

落地原则：

- 多实现扩展点优先定义 `supports(...)`。
- 组合器负责路由，单个实现只处理自身能力。
- 不支持的类型必须显式失败，避免静默吞掉业务动作。

### 4.3 Spring Boot Starter 自动装配模式

- 使用 `@ConditionalOnProperty` 控制能力开关。
- 使用 `@ConditionalOnMissingBean` 支持业务方覆盖默认实现。
- 使用 `@ConditionalOnBean` 组合已有能力，避免硬绑定。
- 使用 `@ConfigurationProperties` 暴露配置模型。
- AutoConfiguration 只做装配，不写复杂业务逻辑。

### 4.4 上下文传播模式

- `WindTracer` / `WindTraceContext`、`TraceFilter`、`ContextPropagationTaskDecorator` 承接 traceId/spanId/context；入口创建或接收，出口返回，异步任务、线程池、消息消费、日志、指标、响应和错误处理都要显式传播，不在业务代码散落魔法 key。

### 4.5 查询与分页模式

- `AbstractCursorQuery`、`MybatisQueryHelper`、`QueryOrderField` / `QueryOrderType` 用于 Query 对象、最大页大小、排序白名单、游标分页和 MyBatis Flex `QueryWrapper` 构造；禁止 Controller 传散装查询参数进入 Mapper。

### 4.6 安全域模式

- JWT、Token 状态、RBAC、验证码和 MFA 分层建模；Token 不只校验签名，还要考虑撤销、设备隔离和刷新令牌；安全动作必须有流控、防重放、失败次数控制、审计和错误收敛。

### 4.7 企业集成模式

- OSS/KMS/Email/DingTalk/IM/Office/Workflow 先定义业务端口再接具体实现；跨系统任务考虑幂等、重试、串行、限速、上下文和补偿；环境隔离、租户隔离、资源定义成为模型契约；内网接口有明确前缀和安全边界。

## 5. 模块治理提炼

- `wind-middleware` 侧重基础 API、统一响应、Web/Trace、Client、MQ、Sequence、幂等、脱敏和项目模板。
- `wind-integration` 侧重 OSS、KMS、消息、IM、Office、指标、工作流、MyBatis Flex 扩展和基础设施适配。
- `wind-security` 侧重认证、授权、JWT、验证码、MFA、Token 状态和请求权限管理。
- 模块地图只用于能力定位；当前项目的真实模块、依赖、包名和验证命令仍以本地仓库为准。

## 6. 对资深架构师 Skill 的 Java/Wind 落地要求

在处理使用 Wind 项目族的 Java 项目时，应优先遵循以下规则：

1. **先找已有端口**：新增 OSS、KMS、消息、安全、Trace、任务、查询能力前，先查是否已有 `WindXxx` 接口或扩展点。
2. **不要绕过统一响应**：Web API 返回应使用统一 `ApiResp` / `ApiResponse` 体系，错误响应带 traceId。
3. **不要绕过 Trace**：HTTP、异步任务、MQ、外部调用必须考虑 trace/context 传播。
4. **不要直接绑定厂商 SDK**：业务代码依赖 `WindOssClient`、`WindCryptoClient`、`MessageSender` 等端口，厂商实现放适配器模块。
5. **安全能力分层**：认证、授权、验证码、MFA、Token 撤销、设备隔离分别建模，不在 Controller 拼装。
6. **查询参数对象化**：分页、排序、游标、条件查询使用 Query 对象和 helper，排序字段白名单化。
7. **自动装配可覆盖**：默认 Bean 必须允许业务方通过 `@ConditionalOnMissingBean` 覆盖。
8. **公共 API 标注契约**：接口、DTO、配置属性使用 Javadoc、validation 和 nullability 注解说明约束。
9. **扩展点必须可路由**：多实现扩展点提供 `supports(...)`、`getName()`、枚举类型或场景标识。
10. **测试按模块边界写**：核心端口做单测，适配器做集成测试，自动装配做上下文加载测试。

## 7. 可复用检查清单

- 设计评审：是否复用已有 Wind 基础能力；核心接口是否隔离 Spring、厂商 SDK 和中间件细节；自动装配是否支持开关和 Bean 覆盖；Trace、错误码、日志、异常是否贯通；安全、查询和外部集成边界是否完整。
- 代码评审：公共接口是否有 Javadoc、validation、nullability；命名是否符合 `WindXxx`、`ImmutableXxx`、`XxxProperties`、`XxxAutoConfiguration`、`XxxClient` 风格；是否直接使用厂商 SDK、在 Controller 拼装安全/消息/OSS 流程、散落魔法 key、静默忽略不支持类型、吞异常或缺少 traceId。
