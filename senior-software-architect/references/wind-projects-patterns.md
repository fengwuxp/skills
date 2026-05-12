# Wind 项目族架构与 API 提炼

本文从以下仓库提炼资深架构师在 Java/Spring/Wind 项目中的项目级实践样本：

- wind-middleware：https://github.com/fengwuxp/wind-middleware
- wind-integration：https://github.com/fengwuxp/wind-integration
- wind-security：https://github.com/fengwuxp/wind-security

## 目录

- `1. 总体架构定位`
- `2. API 设计风格`
- `3. 编码风格提炼`
- `4. 架构模式提炼`
- `5. 模块治理提炼`
- `6. 对资深架构师 Skill 的 Java/Wind 落地要求`
- `7. 可复用检查清单`

## 1. 总体架构定位

### 1.1 项目族分层

```text
业务应用
  ↓
wind-security      安全、认证、授权、验证码、MFA、JWT
wind-integration   企业集成：OSS、KMS、消息、IM、Office、指标、工作流、基础设施扩展
wind-middleware    通用基础架构与中间件：Core、Web、Trace、Config、Client、Sentinel、RocketMQ、Sequence、Script、Mask、Archetype
  ↓
Spring / MyBatis Flex / Redis / MQ / OSS / KMS / Kafka / ElasticJob / Sentinel / JVM
```

架构设计思路：

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

### 2.1 接口优先

典型接口：

- `ApiResponse<T>`：统一响应模型，包含 data、success、errorCode、errorMessage、traceId。
- `WindTracer`：上下文追踪抽象，提供 traceId/spanId/context 读取和作用域执行。
- `WindOssClient`：OSS 能力抽象，隐藏云厂商 SDK。
- `MessageDefinition<T>` / `MessageSender<M>`：消息定义与发送通道解耦。
- `AuthenticationTokenCodecService`：认证 token 生成、解析、验证、撤销。
- `CaptchaManager` / `CaptchaStorage` / `CaptchaContentGenerator`：验证码生成、存储、发送、验证分离。
- `MultiFactorAuthenticator`：MFA 类型与验证实现解耦。

落地原则：

- 面向能力定义接口，不面向具体框架定义接口。
- 接口方法体现业务语义，例如 `generateToken`、`parseAndValidateToken`、`revokeAllToken`、`verify`、`uploadFile`。
- 可选能力使用 default 方法提供便利重载，核心能力保留抽象方法。
- 支持扩展的接口必须提供 `supports(...)` 或唯一 `getName()` 识别机制。

### 2.2 统一响应与异常

- 响应模型包含 traceId，便于请求链路关联。
- 成功与失败通过 `ExceptionCode.SUCCESSFUL` 等错误码统一判断。
- `BaseException` 包含 `ExceptionCode`、消息模板、日志级别，支持友好异常、未授权、禁止、未找到等静态工厂方法。
- Web 层通过统一过滤器和响应工厂将异常转换为 API 响应。

落地原则：

- 业务异常必须携带错误码和可诊断消息。
- 对外响应必须包含 traceId。
- 异常转换应集中处理，避免 Controller 分散 try/catch。
- 友好提示与内部错误诊断信息要分层处理。

### 2.3 空值与参数约束

- 大量使用 `org.jspecify.annotations.Nullable` / `@NonNull` 表达空值契约。
- 使用 `jakarta.validation` 的 `@NotNull`、`@NotBlank`、`@NotEmpty` 表达 API 入参约束。
- 查询对象、实体和接口均通过注解说明契约，而不是依赖口头约定。

落地原则：

- 公共 API 必须显式声明 nullability。
- 入参约束优先使用标准注解，业务断言使用 `AssertUtils`。
- 可空返回值必须通过注解或 Optional 明确表达。

## 3. 编码风格提炼

### 3.1 命名风格

- 统一前缀：基础能力使用 `Wind` 前缀，例如 `WindTracer`、`WindOssClient`、`WindSecurityAccessOperations`。
- 不可变模型使用 `ImmutableXxx`，例如 `ImmutableApiResponse`、`ImmutableCaptcha`。
- 配置类使用 `XxxProperties`，自动装配类使用 `XxxAutoConfiguration`。
- 能力抽象使用 `XxxClient`、`XxxOperations`、`XxxManager`、`XxxStorage`、`XxxFactory`、`XxxProvider`、`XxxRepository`。
- 领域枚举实现 `DescriptiveEnum`，通过 `getDesc()` 提供展示语义。

### 3.2 类结构

- 工具类使用 `final class + private constructor + AssertionError` 防实例化。
- 数据模型使用 Lombok 或 record，减少样板代码。
- 不可变响应和事件模型倾向 final 字段、构造器和 Jackson 注解。
- 组合模式使用 record 简化，例如 `CompositeMessageSender`、`CompositeMultiFactorAuthenticator`。
- 可测试可见性使用 `@VisibleForTesting` 标识，不随意扩大生产 API。

### 3.3 注释与文档

- 公共接口、公有方法、核心模型字段保留 Javadoc。
- 注释重点说明业务意图、边界、约束和第三方协议细节。
- 对复杂算法或边界条件使用示例说明，例如游标分页和全文索引查询。
- 外部协议常量、内网接口、安全约束需要写明风险边界。

### 3.4 断言与错误处理

- 业务前置条件优先使用 `AssertUtils`。
- 不直接返回模糊错误；错误信息尽量包含参数名、资源名、场景名。
- 允许“测试便利”分支，但必须有注释说明，例如无 Web 请求时设备类型回退为 UNKNOWN。
- 可忽略异常必须限制范围并写明意图。

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

典型样本：

- `WindSecurityAutoConfiguration`。
- `CaptchaAutoConfiguration`。
- `WindOssAutoConfiguration`。

落地原则：

- 使用 `@ConditionalOnProperty` 控制能力开关。
- 使用 `@ConditionalOnMissingBean` 支持业务方覆盖默认实现。
- 使用 `@ConditionalOnBean` 组合已有能力，避免硬绑定。
- 使用 `@ConfigurationProperties` 暴露配置模型。
- AutoConfiguration 只做装配，不写复杂业务逻辑。

### 4.4 上下文传播模式

典型样本：

- `WindTracer` / `WindTraceContext` 管理 traceId、spanId 和上下文变量。
- `TraceFilter` 从请求头、IP、Host、Referer、User-Agent 等提取上下文并写回响应头。
- `ContextPropagationTaskDecorator` 用于异步任务上下文传播。
- 日志配置将 traceId、spanId、tenant、userId、requestUrl 等写入结构化日志。

落地原则：

- 入口处创建或接收 traceId，出口处返回 traceId。
- 异步任务、线程池、消息消费必须显式传播上下文。
- 日志、指标、响应和错误处理都应带 traceId。
- 上下文变量应有统一 key，不在业务代码中散落魔法字符串。

### 4.5 查询与分页模式

典型样本：

- `AbstractCursorQuery` 限制最大查询大小，要求游标字段参与排序。
- `MybatisQueryHelper` 将统一 Query 对象转换为 MyBatis Flex `QueryWrapper`、`Page`、`Pagination`。
- 查询排序使用 `QueryOrderField` / `QueryOrderType`，避免前端直接传 SQL 字段。

落地原则：

- 查询必须使用 Query 对象，禁止 Controller 传散装查询参数进入 Mapper。
- 排序字段必须白名单化。
- 深分页场景优先游标分页。
- 分页转换、游标计算、排序构建应集中在 helper，不散落在 Service。

### 4.6 安全域模式

典型样本：

- JWT：`JwtTokenCodec` 负责签发、解析、校验 access/refresh token。
- Token 状态：`AuthenticationTokenUserMapFactory` 维护 user/device 与 token id 的映射，用于撤销和单设备控制。
- RBAC：`WindRbacRole`、`WindRbacPermission`、`WebRequestAuthorizationManager` 抽象请求权限加载和校验。
- 验证码：生成、存储、发送、验证、流控分离。
- MFA：注解 `@MultiFactorAuthentication` + AOP 拦截 + 状态管理 + Sentinel 限流。

落地原则：

- 身份认证、权限校验、二次认证、验证码流控必须分层建模。
- Token 不应只校验签名，还应具备撤销、设备隔离和刷新令牌管理能力。
- 安全动作必须具备限流、防重放、失败次数控制、审计和错误收敛。
- 权限模型应以资源、角色、权限、请求加载器解耦，避免硬编码 URL 权限。

### 4.7 企业集成模式

典型样本：

- OSS/KMS/Email/DingTalk/IM/Office/Workflow 都先定义业务端口，再引入具体实现。
- `WindTaskDefinition`、`WindTaskRunnable` 表达可重试、可串行、可限速的业务任务。
- `LockTemplate`、`RedissonWindLock`、`ProgrammaticTransactionTemplate` 封装基础设施能力。
- `EnvIsolationObject`、`TenantIsolationObject`、`BaseEntity`、`TreeEntity` 建立通用数据模型约定。

落地原则：

- 企业集成模块必须隔离外部 SDK 和协议差异。
- 跨系统任务必须考虑幂等、重试、串行、限速、上下文和补偿。
- 环境隔离、租户隔离、资源定义应成为模型契约，而不是散落字段。
- 内网接口必须有明确前缀和安全边界，例如 `/inc/basic` 与 `/inc/secure`。

## 5. 模块治理提炼

### 5.1 wind-middleware 模块地图

- `wind-core`：基础 API、响应、异常、签名、查询、枚举、资源模型。
- `wind-common`：锁、配置、事件、Spring 工具、缓存 Map、限流等通用能力。
- `wind-web` / `wind-server`：Web 响应、TraceFilter、异常处理、审计、i18n、Actuator、过滤器自动装配。
- `wind-tracer`：trace 上下文和异步传播。
- `wind-client`：RestClient/Retrofit 客户端、签名、响应解包、请求日志。
- `wind-config-center`：配置仓储与 Nacos 适配。
- `wind-sentinel`：限流资源和配置中心数据源。
- `wind-rocketmq`：RocketMQ listener/producer 增强。
- `wind-sequence`：序列号生成与存储。
- `wind-idempotent`：幂等调用抽象。
- `object-mask` / `logback-kafka-appender`：脱敏与结构化日志。
- `wind-archetype`：应用项目模板。

### 5.2 wind-integration 模块地图

- `core`：消息、任务、工作流参与人、通用实体、资源定义。
- `extends/infra-commons`：Redisson 锁、KMS 加密器、事务模板等基础设施扩展。
- `extends/mybatis-flex-extends`：加密 TypeHandler、Locale TypeHandler、环境隔离插入监听、查询 helper。
- `office`：Office/Excel 导入导出任务模型。
- `wind-oss`：OSS API、阿里云适配器、starter。
- `wind-kms`：KMS API、阿里云适配器。
- `wind-message`：钉钉、邮件消息发送。
- `wind-im`：WebSocket/Socket.IO 即时通信。
- `wind-metrics`：指标聚合、标签、统计执行器。
- `wind-workflow`：审批流定义模型。

### 5.3 wind-security 模块地图

- `core`：安全访问操作、RBAC 资源、角色、权限、变更事件。
- `jwt`：JWT 编解码和过期异常。
- `authentication`：token 编解码、用户 token 映射、请求权限管理、自动装配。
- `captcha`：验证码类型、内容生成、存储、发送、流控、自动装配。
- `mfa`：TOTP、MFA 状态管理、MFA 注解与方法拦截。

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

### 7.1 设计评审

- 是否复用了已有 Wind 基础能力，而不是重复造轮子？
- 核心接口是否隔离了 Spring、厂商 SDK 和中间件细节？
- 自动装配是否支持配置开关和 Bean 覆盖？
- Trace、错误码、日志、异常是否贯通？
- 安全能力是否考虑撤销、流控、重放、失败次数和审计？
- 查询是否有最大页大小、排序白名单和深分页策略？
- 外部集成是否有幂等、重试、超时、限流和补偿？

### 7.2 代码评审

- 公共接口是否有 Javadoc、validation、nullability？
- 命名是否符合 `WindXxx`、`ImmutableXxx`、`XxxProperties`、`XxxAutoConfiguration`、`XxxClient` 等项目风格？
- 是否存在直接使用厂商 SDK 的业务代码？
- 是否存在 Controller 直接处理认证、验证码、MFA、消息发送、OSS 操作的流程编排？
- 是否存在魔法字符串形式的 trace key、header name、cache name、resource name？
- 是否存在不支持类型时静默失败的 Composite/Manager？
- 是否存在吞异常、缺少 traceId、缺少错误码或缺少日志上下文？
