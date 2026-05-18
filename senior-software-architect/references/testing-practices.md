# 测试专项实践

本文承接 `testing.md` 的总纲，用于 Java/Spring/Wind 项目、复杂业务测试、资金域测试和非 Java 技术栈适配。

## 1. Java/Spring 常见测试实践

Java/Spring 测试的核心不是“启动多少 Spring”，而是判断测试目标需要哪些真实代码、哪些真实装配、哪些外部边界替身。

### 1.1 普通类、工具类测试

适用对象：

- 纯函数、工具类、值对象、枚举、格式化器、签名/加密算法、金额、序列号、字符串处理。
- 不需要 Spring 容器、不需要数据库、不需要真实外部服务的领域规则或基础能力。

默认策略：

- 不启动 Spring，优先使用 JUnit 5 + AssertJ/JUnit Assertions。
- 能 `new` 就直接构造对象，依赖少量协作者时使用 fake/stub/mock。
- 覆盖正常、异常、边界，例如空值、空集合、特殊字符、币种不匹配、签名失败、状态非法。
- 断言返回值、异常消息/错误码、状态变化、序列值、格式化结果，不只断言非空。
- 确需随机数据时，不让随机值决定断言；核心断言应稳定可重复。

Wind 实践提炼：

- `StringMatchUtilsTests`、`MoneyTests`、`ApiSignatureRequestTests` 使用无 Spring 的快速单测验证普通类行为。
- `WindSystemConfigRepositoryTests`、`RedissonTemporalSequenceSupportTests` 对外部协作者使用 Mockito 替身，避免连接真实存储或 Redis。
- `MybatisQueryMethodHelperTests` 不连数据库，只验证 QueryWrapper 生成的 SQL 语义。

### 1.2 数据库依赖测试

适用对象：

- Mapper、Repository、DAO、基础 Service、事务逻辑、SQL 生成、分页排序、唯一约束、乐观锁、数据初始化。
- 必须验证数据库行为，而不是只验证 Java 分支逻辑的代码。

默认策略：

- 优先 H2 内存库：`jdbc:h2:mem:*;MODE=MySQL`。
- 高风险 SQL、锁、索引、方言和性能问题补 Testcontainers 或专门集成测试。
- 使用 `@SpringJUnitConfig`、`@ContextConfiguration`、`@ImportAutoConfiguration` 精确导入配置，不默认全量 `@SpringBootTest`。
- JPA 场景优先评估 `@DataJpaTest`；MyBatis/MyBatis Flex 场景优先使用最小 `@SpringJUnitConfig` + 显式配置类。
- 沉淀 `AbstractJdbcTest` / `AbstractServiceTest`，统一数据源、事务、SQL 初始化、MyBatis 配置和测试属性。
- 使用 `@Transactional(rollbackFor = Exception.class)` 自动回滚。
- 通过 `jdbc-schema.sql`、`jdbc-data.sql`、`spring.sql.init.*` 或 `@Sql` 构造稳定初始状态。
- H2 不支持的 MySQL 函数通过统一初始化器补齐，例如 `H2FunctionInitializer`。

Wind 实践提炼：

- `AbstractJdbcTest` 使用 H2、`DataSourceTransactionManagerAutoConfiguration`、`JdbcTemplateAutoConfiguration`、SQL 初始化和事务回滚。
- `AbstractServiceTest` 为 MyBatis Flex 场景导入 `MybatisFlexAutoConfiguration`、`MybatisFlexTestConfiguration` 和统一 `JdbcTemplate`。
- `JdbcSequenceRepositoryTests` 通过 `@ContextConfiguration(classes = TestConfig.class)` 只装配 `SequenceRepository` 所需 Bean。

### 1.3 Spring Controller 测试

适用对象：

- Controller、Filter、Interceptor、参数绑定、校验、统一响应、异常处理、签名、安全、国际化、序列化。

默认策略：

- 优先 MockMvc，验证 HTTP 层行为，避免启动真实 Tomcat。
- 通过 `@ContextConfiguration`、测试专用 `@SpringBootApplication(scanBasePackages = ...)`、`@Import` 或 `@ComponentScan` 控制 Bean 范围。
- Nacos、MQ、Redis、OSS、KMS 等外部依赖应禁用或替换为 Mock/Fake。
- Filter/Interceptor 可直接使用 `MockHttpServletRequest`、`MockHttpServletResponse`、`MockFilterChain`。
- Controller 可使用 `webAppContextSetup` 或 standalone MockMvc。
- 断言 HTTP 状态、响应 JSON、错误码、错误消息、Header、签名属性、国际化结果和安全拦截结果。
- 只有需要验证全局异常处理、参数转换、拦截器链、消息转换器时，才使用 WebApplicationContext。

Wind 实践提炼：

- `AbstractControllerTest` 使用 `@SpringJUnitConfig`、`@WebAppConfiguration` 和 `MockMvcBuilders.webAppContextSetup`，同时禁用 Nacos 配置。
- `RequestSignFilterTests` 直接构造请求、响应和过滤器链，验证签名缺失、签名成功、签名过期等 HTTP 安全场景。
- `IpAccessControlFilterTests` 直接测试过滤器，不启动 Web 容器，断言状态码和错误消息。
- `RestfulApiRespFactoryTests` 通过测试消息源和 Locale 验证统一响应与国际化。

### 1.4 Spring 应用服务流程测试

适用对象：

- ApplicationService、业务 flow、资金/订单/库存/审批等跨多个内部协作者的用例流程。
- 需要验证真实 Bean 装配、事务边界、状态迁移、幂等短路、异常回滚和业务副作用的场景。

默认策略：

- 使用最小 Spring 上下文，优先 `@SpringJUnitConfig`、精确 `@Import`、测试专用 `TestConfig`。
- 使用 H2 或 Testcontainers 初始化真实表结构。
- 使用 `@Transactional(rollbackFor = Exception.class)` 自动回滚。
- 真实注入 service、converter、resolver、orchestrator、assembler、posting service、lifecycle 等内部协作者。
- 只替换第三方通道、远程 HTTP、MQ、Redis、时间、ID 生成器等外部依赖或测试基础设施。
- 避免手工 new 内部链路，避免绕过真实 Spring 装配、事务、AOP、条件 Bean 和配置约束。
- 只有需要验证完整自动装配、切面、全局配置或跨模块集成时，才升级到更重的 Spring Boot 测试。

流程测试必须断言：

- 输入被正确转化为业务命令或领域对象。
- route、resolver、assembler、lifecycle 等内部链路真实执行。
- 状态、持久化记录、输出端口、事件或消息符合业务预期。
- 失败时事务回滚，不留下半成功事实。
- 重复执行、并发或幂等键命中时不会产生重复副作用。

### 1.5 SpringBoot 测试减负

- 先问“这个测试到底需要哪些 Bean”，再决定是否启动 Spring。
- `@SpringBootTest` 是最后选项，不是默认选项。
- 通过 `classes`、`@ContextConfiguration`、`@Import`、`@ComponentScan`、`excludeAutoConfiguration` 限定上下文。
- 通过 `@MockBean` / `@MockitoBean` / `@SpyBean`、`@Primary`、`@Conditional*` 替换重依赖。
- Web 测试尽量不启动服务器，数据库测试尽量不连接共享测试库。
- 大型项目可评估 `spring-context-indexer`，但它只是优化扫描成本，不替代测试上下文减负。

## 2. 复杂业务测试手段

### 2.1 参数化测试

适用场景：

- 金额边界、币种组合、状态枚举、权限矩阵、风控规则、格式化规则、错误码映射。

实践要点：

- 参数名要表达业务含义，不要只用 `arg0`、`case1`。
- 每组参数都应说明输入、预期和边界意义。
- 不要把无关场景硬塞进同一个参数化测试；同一测试仍然只保护一个行为。

### 2.2 状态机测试

适用场景：

- 订单、支付、授权、结算、退款、审批、任务流、库存锁定、账户状态。

实践要点：

- 明确合法迁移、非法迁移和终态。
- 每个测试至少断言当前状态、事件、下一状态和副作用。
- 逆向交易、撤销、回滚、过期、重复事件必须单独覆盖。

### 2.3 幂等与并发测试

适用场景：

- 重复请求、重试、消息重复投递、唯一约束、锁、库存扣减、余额变更、任务抢占。

实践要点：

- 幂等测试要断言第二次执行不会产生重复副作用。
- 并发测试要断言最终事实，而不是只断言没有异常。
- 数据库唯一键、乐观锁、悲观锁、幂等表和状态条件更新都应有测试保护。
- 对不可稳定复现的并发风险，应补专项压力测试或 JCStress/JMH 等工具验证。

### 2.4 Characterization Tests

适用场景：

- 遗留系统改造、重构前保护、外部行为不清晰但必须保持兼容的代码。

实践要点：

- 先记录当前公开行为，不急于判断行为是否优雅。
- 覆盖调用方真实依赖的输入、输出、异常和副作用。
- 重构后用同一测试证明行为没有被无意改变。
- 发现历史行为本身错误时，先补 ADR/需求确认，再修改测试预期。

### 2.5 Property-based Testing

适用场景：

- 金额计算、格式转换、序列化/反序列化、排序分页、规则组合、解析器、编码解码。

实践要点：

- 先定义不变量，例如可逆性、单调性、守恒、幂等、无精度丢失。
- 随机输入不能决定测试是否稳定；失败样本要能复现。
- 适合补强输入空间大的逻辑，不替代具体业务场景测试。

## 3. 资金域测试专项

资金域测试优先验证资金事实，不以代码覆盖率或 mock 调用次数作为主要目标。

至少考虑：

- **路由事实**：route 是否正确，通道、账户、资金方向、业务类型和规则版本是否匹配。
- **账务计划**：posting plan 是否借贷平衡，金额、币种、方向、科目、bucket 和 subject 是否正确。
- **账本事实**：ledger transaction 是否可追溯到业务单、原交易、幂等键和外部流水。
- **分录事实**：ledger entry 的 subject、bucket、方向、金额、币种和业务含义是否正确。
- **余额事实**：余额桶每一步变化是否正确，可用、冻结、在途、待清算、待结算等口径不能混淆。
- **冻结/解冻**：冻结、解冻、占用、释放只能在同主体、同币种、同资金桶语义内移动，不得凭空增减。
- **原交易回放**：授权、撤销、结算、退款、拒付、return、reversal 必须按原交易事实回放，不得另造事实。
- **幂等事实**：重复执行不会重复入账、重复冻结、重复释放或重复发出外部指令。
- **失败回滚**：异常、外部失败、数据库失败或中途校验失败时，不留下半成功账务、状态或消息。
- **可追溯关系**：业务单、指令、账务交易、分录、外部流水、对账记录之间能相互追踪。

资金域测试反模式：

- 只断言服务调用成功，不断言余额、分录、状态和可追溯关系。
- mock 掉 posting assembler 或 ledger posting service 后声称验证了资金流程。
- 只验证 `orchestrator.post()` 被调用，不验证 posting plan 的业务语义。
- 忽略幂等重复执行、失败回滚、原交易约束和逆向交易差异。
- 把冻结、结算、退款、撤销、冲正、return、reversal 混成同一种测试断言。

## 4. 非 Java 技术栈适配

架构师应迁移测试原则，而不是强套 Java/Spring 工具。

| Java/Spring 概念 | 非 Java 等价方向 |
| --- | --- |
| JUnit/AssertJ | Go `testing`、Python `pytest`、Node.js Jest/Vitest、Rust `cargo test` 等。 |
| Spring 最小上下文 | 对应语言的依赖注入、模块装配、测试容器或轻量应用上下文。 |
| MockMvc | HTTP handler/router 测试、ASGI/WSGI 测试客户端、SuperTest、Playwright API 测试。 |
| H2/Testcontainers | SQLite/临时库/Testcontainers/本地容器化依赖。 |
| WireMock/Fake 端口 | HTTP fake server、contract stub、in-memory adapter、recording port。 |
| ArchUnit/Maven Enforcer | lint、module boundary checker、dep graph checker、workspace rule、custom script。 |

适配原则：

- 保持业务行为优先、真实内部链路优先、外部依赖边界替换、契约可验证。
- 先尊重项目已有测试框架、构建命令、fixture、CI 约定和目录结构。
- 不把 Java 注解、Spring 上下文、H2 方案强套到 Go、Node.js、Python、Rust、前端或数据工程项目。
- 涉及金额、权限、幂等、审计、状态机等高风险逻辑时，测试红线不因语言不同而降低。

## 5. 专项实践选择清单

- 普通类、值对象、工具方法：优先读 `1.1`。
- SQL、Mapper、Repository、事务：优先读 `1.2`。
- Controller、Filter、Interceptor、HTTP 协议：优先读 `1.3`。
- ApplicationService、业务 flow、事务状态流：优先读 `1.4`。
- Spring 测试过慢或上下文过重：优先读 `1.5`。
- 状态机、幂等、并发、遗留重构或输入空间复杂：读 `2`。
- 资金、账本、余额、原交易、追溯：读 `3`。
- 非 Java 项目：读 `4`，再结合项目本地规范选择等价工具。
