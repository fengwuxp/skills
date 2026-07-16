# 测试专项实践：普通类与数据库

本文从 `testing-practices.md` 拆出，承载普通类/工具类测试和数据库依赖测试。

## 使用时机

- 测试对象是纯 Java 类、值对象、工具类、Mapper、Repository、DAO、事务或 SQL 行为。

## 不适用场景

- HTTP 层读 `testing-practices-java-web.md`。
- Application Service 流程读 `testing-practices-java-service-flow.md`。

## 读取后必须产出

- 测试层次、真实依赖边界、测试数据构造方式和断言重点。

## 需要继续读取的 reference

- 测试总纲读 `testing.md`。
- Java 编码约规读项目本地规范和 `wind-coding-conventions` 通用层；Wind/Nobe 专项按依赖或上下文启用。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 普通类、值对象、工具类 | 1.1 | 数据库配置 |
| Mapper/Repository/事务 | 1.2 | 普通类示例 |

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
