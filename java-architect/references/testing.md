# 测试驱动设计与测试资产治理

测试不是编码完成后的补丁，而是架构设计、行为约束和长期演进的安全网。架构师必须把测试视为生产级资产：可读、可改、可运行、可诊断、可持续维护。

## 目录

- `1. 核心定位`
- `2. TDD 设计闭环`
- `3. 测试分层`
- `4. 测试代码整洁`
- `5. 测试资产治理`
- `6. 三类常见代码测试实践`
- `7. 长期演进价值`
- `8. Review 清单`
- `9. 与其他规范的关系`

## 1. 核心定位

- **测试驱动设计**：TDD 用测试先描述行为、边界和不变量，再反推接口、模型、依赖方向和实现。
- **测试即活文档**：测试应说明业务场景、输入条件、触发行为、期望输出和边界含义。
- **测试保护演进**：测试套件用于支撑重构、依赖升级、模块拆分、接口调整、数据库迁移和缺陷修复。
- **测试代码等同生产代码**：测试命名、结构、数据、断言、辅助方法和测试基建都需要长期维护。
- **测试成本必须可控**：测试应快速、独立、可重复、自验证、及时，避免慢、脆、难定位。

## 2. TDD 设计闭环

TDD 的价值不在“先写测试”这个动作，而在用可执行行为约束设计。

```text
业务行为/验收语义
-> 失败测试
-> 最小实现
-> 重构设计
-> 边界固化
-> 回归保护
```

实践原则：

- 先写失败测试，确认行为尚未被实现。
- 只写刚好让测试通过的实现，避免提前设计。
- 通过重构改善命名、结构、边界和依赖，不改变行为。
- 用测试表达业务不变量、异常语义、权限、幂等、状态流转和边界条件。
- 用可测试性反推架构边界：核心规则不依赖容器、数据库、远程服务和系统时间。

适用场景：

- 复杂业务规则、金额、库存、权限、状态机、幂等、一致性。
- 缺陷修复：先写复现失败的回归测试，再修复。
- 重构前：先补行为保护，再改结构。
- 核心接口和领域模型设计：先明确调用方期待，再实现内部细节。

不适合机械套用的场景：

- 一次性脚本、纯配置、低风险样板代码。
- UI 视觉细节或交互体验探索阶段。
- 外部依赖行为尚不明确且缺少可控替身时。

## 3. 测试分层

| 类型 | 目标 | 典型工具 | 重点 |
|------|------|----------|------|
| 单元测试 | 验证纯业务规则、工具、领域服务 | JUnit 5、AssertJ、Mockito | 快、稳、隔离副作用 |
| 应用服务测试 | 验证用例编排、事务边界、权限和异常 | Spring Boot Test 按需加载 | 不滥用完整上下文 |
| 数据访问测试 | 验证 Mapper、Repository、SQL、索引假设 | H2、Testcontainers | 数据准备清晰，可重复 |
| 集成测试 | 验证外部适配器、自动装配、协议转换 | Spring Boot Test、WireMock | 覆盖真实集成风险 |
| 契约测试 | 保护模块、API、消息、SDK 边界 | OpenAPI、Pact、JSON Schema | 防止调用方/提供方漂移 |
| 架构测试 | 验证依赖方向、包结构、分层规则 | ArchUnit、Maven Enforcer | 把架构规则自动化 |
| 回归测试 | 防止历史 bug 复现 | JUnit 5、集成测试 | 每个缺陷沉淀保护 |
| E2E 测试 | 验证关键用户路径 | Playwright、Cypress | 少而关键，避免全靠 E2E |
| 性能/并发测试 | 验证容量、竞争、幂等和稳定性 | JMH、JCStress、压测工具 | 只覆盖高风险路径 |

分层原则：

- 单元测试保护业务规则，数量最多，运行最快。
- 集成测试保护适配器和基础设施，不替代单元测试。
- 契约测试保护跨模块、跨服务、前后端和消息协议。
- E2E 只覆盖关键链路，不承载全部业务规则验证。
- 架构测试用于自动守住依赖方向和分层约束。

## 4. 测试代码整洁

测试代码必须像生产代码一样被设计和维护。

- **命名表达场景**：测试类、测试方法和变量名应表达业务意图，不使用空泛命名。
- **结构清晰**：优先使用 Given/When/Then 或 Arrange/Act/Assert。
- **输入输出明确**：测试数据要说明输入条件，断言要表达期望输出和业务含义。
- **一个测试聚焦一个行为**：可以有多个必要断言，但应服务同一个场景。
- **测试数据有语义**：避免无意义的 `foo`、`test1`、`123`；金额、状态、时间、权限等数据应服务测试意图。
- **辅助方法可读**：测试 fixture、builder、factory 应降低理解成本，而不是隐藏关键条件。
- **断言要具体**：避免只断言不为 null 或没有异常；应断言业务结果、状态变化和副作用。
- **失败信息可诊断**：测试失败后应能快速定位是输入、行为、断言还是环境问题。

推荐结构：

```java
@Test
void testPayOrderWithInsufficientBalance() {
    // given
    UserAccount account = accountWithBalance("100.00");
    PayCommand command = payCommand("150.00");

    // when
    BaseException exception = assertThrows(BaseException.class, () -> paymentService.pay(account, command));

    // then
    assertThat(exception.getCode()).isEqualTo(PaymentErrorCode.INSUFFICIENT_BALANCE);
    assertThat(account.getBalance()).isEqualByComparingTo("100.00");
}
```

## 5. 测试资产治理

测试会腐化，必须治理。没有治理的测试套件会从安全网变成负担。

常见坏味道：

- **慢测试过多**：所有场景都启动 Spring 上下文或真实外部依赖。
- **脆弱测试**：依赖执行顺序、系统时间、随机数、环境状态或数据库残留数据。
- **断言过宽**：只断言不报错、不为空，不验证业务结果。
- **Mock 过度**：把实现细节都 mock 掉，测试只验证 mock 行为，不验证业务行为。
- **测试数据混乱**：大量复制粘贴 fixture，字段含义不明。
- **测试耦合实现**：过度验证私有方法、调用次数和内部步骤，导致重构困难。
- **失败难诊断**：失败日志不能说明场景、输入、期望和实际差异。

治理原则：

- 定期清理重复测试、无效测试、长期跳过测试和随机失败测试。
- 对慢测试分层管理，区分快速单测、集成测试和 E2E 测试。
- 把公共测试数据构造沉淀为清晰的 builder 或 fixture。
- 对外部依赖建立稳定替身，如 fake、stub、WireMock、Testcontainers。
- 生产缺陷必须转化为回归测试，避免同类问题再次发生。
- 测试基类、测试容器、测试配置也要被视为基础设施资产维护。

## 6. 三类常见代码测试实践

本节吸收 Wind 项目族测试实践和 SpringBoot 测试减负经验，按普通类/工具类、数据库依赖类、Spring Controller 三类给出默认策略。

### 6.1 普通类、工具类测试

适用对象：

- 纯函数、工具类、值对象、枚举、格式化器、签名/加密算法、金额、序列号、字符串处理。
- 不需要 Spring 容器、不需要数据库、不需要真实外部服务的领域规则或基础能力。

默认策略：

- **不启动 Spring**：优先使用 JUnit 5 + AssertJ/JUnit Assertions，保持毫秒级反馈。
- **直接构造对象**：能 `new` 就不要注入容器；依赖少量协作者时使用 fake/stub/mock。
- **覆盖正常、异常、边界**：例如空值、空集合、特殊字符、币种不匹配、签名失败、状态非法。
- **断言具体结果**：断言返回值、异常消息/错误码、状态变化、序列值、格式化结果，不只断言非空。
- **测试数据表达语义**：金额、币种、IP、签名文本、SQL 片段等数据应能说明测试意图。
- **避免随机不可控**：确需随机数据时，不让随机值决定断言；核心断言应稳定可重复。

Wind 实践提炼：

- `StringMatchUtilsTests`、`MoneyTests`、`ApiSignatureRequestTests` 使用无 Spring 的快速单测验证普通类行为。
- `WindSystemConfigRepositoryTests`、`RedissonTemporalSequenceSupportTests` 对外部协作者使用 Mockito 替身，避免连接真实存储或 Redis。
- `MybatisQueryMethodHelperTests` 不连数据库，只验证 QueryWrapper 生成的 SQL 语义，反馈更快。

### 6.2 需要依赖数据库的类测试

适用对象：

- Mapper、Repository、DAO、基础 Service、事务逻辑、SQL 生成、分页排序、唯一约束、乐观锁、数据初始化。
- 必须验证数据库行为，而不是只验证 Java 分支逻辑的代码。

默认策略：

- **优先 H2 内存库**：使用 `jdbc:h2:mem:*;MODE=MySQL`，让测试环境轻量、隔离、可重复。
- **最小化 Spring 上下文**：使用 `@SpringJUnitConfig`、`@ContextConfiguration`、`@ImportAutoConfiguration` 精确导入需要的配置，不默认全量 `@SpringBootTest`。
- **按技术栈选择切片测试**：JPA 场景优先评估 `@DataJpaTest`；MyBatis/MyBatis Flex 场景优先使用最小 `@SpringJUnitConfig` + 显式配置类。
- **集中测试基类**：沉淀 `AbstractJdbcTest` / `AbstractServiceTest`，统一数据源、事务、SQL 初始化、MyBatis 配置和测试属性。
- **事务自动回滚**：测试类使用 `@Transactional(rollbackFor = Exception.class)`，避免脏数据污染后续用例。
- **脚本初始化结构和基础数据**：通过 `jdbc-schema.sql`、`jdbc-data.sql`、`spring.sql.init.*` 或 `@Sql` 构造稳定初始状态。
- **兼容数据库函数**：H2 不支持的 MySQL 函数通过统一初始化器补齐，例如 `H2FunctionInitializer`。
- **只导入被测 Bean 和必要依赖**：测试类用内部 `TestConfig` 显式声明 Bean，避免扫描整个项目。

Wind 实践提炼：

- `AbstractJdbcTest` 使用 H2、`DataSourceTransactionManagerAutoConfiguration`、`JdbcTemplateAutoConfiguration`、SQL 初始化和事务回滚。
- `AbstractServiceTest` 为 MyBatis Flex 场景导入 `MybatisFlexAutoConfiguration`、`MybatisFlexTestConfiguration` 和统一 `JdbcTemplate`。
- `JdbcSequenceRepositoryTests` 通过 `@ContextConfiguration(classes = TestConfig.class)` 只装配 `SequenceRepository` 所需 Bean。

注意事项：

- H2 能覆盖大多数 SQL 与事务行为，但不能完全代表生产数据库；高风险 SQL、锁、索引、方言和性能问题应补 Testcontainers 或专门集成测试。
- 测试数据要最小且有语义，避免把大量生产数据搬入测试。
- 数据库测试比普通单测慢，应聚焦真实数据库风险，不要替代纯业务单测。

### 6.3 Spring Controller 相关测试

适用对象：

- Controller、Filter、Interceptor、参数绑定、校验、统一响应、异常处理、签名、安全、国际化、序列化。

默认策略：

- **优先 MockMvc**：使用 MockMvc 验证 HTTP 层行为，避免启动真实 Tomcat。
- **限定扫描范围**：通过 `@ContextConfiguration`、测试专用 `@SpringBootApplication(scanBasePackages = ...)`、`@Import` 或 `@ComponentScan` 控制 Bean 范围。
- **不连接真实中间件**：Nacos、MQ、Redis、OSS、KMS 等外部依赖应禁用或替换为 Mock/Fake。
- **按层选择测试方式**：Filter/Interceptor 可直接使用 `MockHttpServletRequest`、`MockHttpServletResponse`、`MockFilterChain`；Controller 可使用 `webAppContextSetup` 或 standalone MockMvc。
- **验证协议语义**：断言 HTTP 状态、响应 JSON、错误码、错误消息、Header、签名属性、国际化结果和安全拦截结果。
- **只在必要时启动完整上下文**：需要验证全局异常处理、参数转换、拦截器链、消息转换器时再使用 WebApplicationContext。

Wind 实践提炼：

- `AbstractControllerTest` 使用 `@SpringJUnitConfig`、`@WebAppConfiguration` 和 `MockMvcBuilders.webAppContextSetup`，同时禁用 Nacos 配置。
- `RequestSignFilterTests` 直接构造请求、响应和过滤器链，验证签名缺失、签名成功、签名过期等 HTTP 安全场景。
- `IpAccessControlFilterTests` 直接测试过滤器，不启动 Web 容器，断言状态码和错误消息。
- `RestfulApiRespFactoryTests` 通过测试消息源和 Locale 验证统一响应与国际化，不启动完整 Web 应用。

SpringBoot 测试减负原则：

- 先问“这个测试到底需要哪些 Bean”，再决定是否启动 Spring。
- `@SpringBootTest` 是最后选项，不是默认选项。
- 通过 `classes`、`@ContextConfiguration`、`@Import`、`@ComponentScan`、`excludeAutoConfiguration` 限定上下文。
- 通过 `@MockBean` / `@MockitoBean` / `@SpyBean`、`@Primary`、`@Conditional*` 替换重依赖。
- Web 测试尽量不启动服务器，数据库测试尽量不连接共享测试库。
- 大型项目可评估 `spring-context-indexer`，通过编译期候选组件索引降低 Spring 扫描成本，但它是补充优化，不替代测试上下文减负。

## 7. 长期演进价值

测试资产的最终价值，是让系统敢于演进。

- **重构安全网**：允许团队小步改善结构，而不担心行为被悄悄破坏。
- **依赖升级安全网**：升级 JDK、Spring、数据库驱动、中间件 SDK 时快速发现兼容问题。
- **模块拆分安全网**：通过单元、契约、集成测试验证拆分后行为一致。
- **接口演进安全网**：保护 API、消息、SDK、DTO、错误码、分页和排序语义。
- **数据迁移安全网**：验证 SQL、索引、默认值、兼容字段和历史数据处理。
- **团队协作安全网**：新成员通过测试理解业务规则和边界条件。
- **AI 协作安全网**：用测试约束 AI 生成代码，减少幻觉实现和隐性回归。

## 8. Review 清单

评审测试时优先看：

- 是否覆盖正常、异常、边界、权限、幂等、并发和兼容场景？
- 测试名称是否能说明业务场景和预期行为？
- 输入数据、触发行为、期望输出是否清楚？
- 断言是否验证业务结果，而不是只验证代码跑过？
- 测试是否隔离时间、随机数、外部接口、线程池和副作用？
- 是否存在过度 mock、慢测试、脆弱测试或重复测试数据？
- 新增缺陷是否已经沉淀为回归测试？
- 架构规则是否可以用 ArchUnit、静态扫描或脚本自动验证？

## 9. 与其他规范的关系

- `architecture.md`：定义 TDD 在架构决策中的价值和可测试性质量属性。
- `clean-code.md`：定义测试代码整洁原则。
- `project-governance-standards.md`：定义项目级测试落地规则。
- `workflow.md`：定义提交前和 PR 前的测试执行要求。
- `skill-tree.md`：定义架构师应具备的测试能力概览。
