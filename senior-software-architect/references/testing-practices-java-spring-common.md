# 测试专项实践：Java/Spring 公共测试底座

本文从 Java/Spring 测试专项中抽出公共判断：是否启动 Spring、如何裁剪上下文、哪些依赖用真实代码、哪些边界用替身，以及如何沉淀稳定测试基础设施。Web、Service Flow、数据库和复杂业务专项只保留各自差异。

## 使用时机

- 已读取 `testing-practices.md`，并命中 Java/Spring 测试场景。
- 需要判断是否启动 Spring、是否使用最小上下文、如何替换外部依赖、如何设计测试基类。
- Web、Service Flow、数据库测试中出现重复的 Spring 装配、H2、MyBatis、缓存、锁、上下文清理或测试属性配置。

## 不适用场景

- 只判断测试层次时，先读 `testing.md`。
- 纯 Java 类、值对象、工具类无需 Spring 时，读 `testing-practices-java-unit-db.md`。
- Controller、Filter、Interceptor 和 MockMvc 细节读 `testing-practices-java-web.md`。
- Application Service / Use Case 流程、事务和副作用断言读 `testing-practices-java-service-flow.md`。

## 读取后必须产出

- 是否启动 Spring、最小上下文范围、真实代码范围、外部依赖替身、测试基础设施归属和禁止过重启动的理由。

## 需要继续读取的 reference

- 普通类和数据库行为读 `testing-practices-java-unit-db.md`。
- HTTP 层读 `testing-practices-java-web.md`。
- 应用服务流程读 `testing-practices-java-service-flow.md`。
- 复杂业务和资金域读 `testing-practices-business-funds.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否启动 Spring | 1 | 具体 Controller/Service 模板 |
| 最小上下文和依赖替身 | 2 | 资金域专项 |
| 公共测试基类和基础设施 | 3 | HTTP 断言细节 |
| SpringBoot 测试减负 | 4 | 业务流程样例 |
| 测试底座红线 | 5 | 具体业务断言 |

## 1. Java/Spring 测试核心判断

Java/Spring 测试的核心不是“启动多少 Spring”，而是判断测试目标需要哪些真实代码、哪些真实装配、哪些外部边界替身。

- 能直接 `new` 的纯规则、值对象、转换器和工具类，不启动 Spring。
- 需要验证 Bean 装配、事务、AOP、配置条件、Mapper/Repository、Web 绑定或全局异常处理时，才进入 Spring 上下文。
- 测试目标需要真实内部协作者时，保留内部链路；第三方通道、远程 HTTP、MQ、Redis、时间、ID 生成器、对象存储等外部边界优先替换。
- 断言业务事实、持久化事实、HTTP 事实、异常和副作用，不只断言调用成功或对象非空。

## 2. 最小 Spring 上下文

- 优先 `@SpringJUnitConfig`、`@ContextConfiguration`、精确 `@Import` 和测试专用 `TestConfig`。
- `@SpringBootTest` 是最后选项，只用于验证完整自动装配、切面、全局配置或跨模块集成。
- 通过 `classes`、`@Import`、`@ComponentScan`、`excludeAutoConfiguration` 限定上下文。
- 通过 `@MockBean` / `@MockitoBean` / `@SpyBean`、`@Primary`、`@Conditional*` 替换重依赖。
- Web 测试尽量不启动真实服务器，数据库测试尽量不连接共享测试库。
- 大型项目可评估 `spring-context-indexer`，但它只是优化扫描成本，不替代上下文减负。

## 3. 公共测试基础设施

- 测试基类负责“运行底座”，不负责“业务测试目标”：统一测试属性、事务、数据源、SQL 初始化、通用 Mock/Fake、测试上下文初始化和清理。
- 子类负责目标 Bean、必要内部依赖和外部边界替身；不要在基类中默认扫描整个业务包。
- H2 数据源、MyBatis Flex 配置、SQL 初始化、加解密 TypeHandler、测试缓存、测试锁、测试事件发布器等可以沉淀到公共测试配置。
- 租户、用户、区域、语言、审计上下文必须在测试前建立、测试后清理，禁止污染其他测试。
- 对 `SpringApplicationContextUtils`、`SpringEventPublishUtils` 等历史静态工具的测试态初始化，应集中在基类或测试配置中，并说明这是兼容历史基础设施，不作为新设计范式。

测试基类只给骨架，不把业务 Bean 塞进公共上下文：

```java
@SpringJUnitConfig
@ContextConfiguration(classes = ExampleTest.TestConfig.class)
@TestPropertySource(locations = "classpath:application-test.properties")
@Transactional(rollbackFor = Exception.class)
abstract class AbstractExampleSpringTest {
}
```

## 4. H2、MyBatis 与外部边界

- H2 可用于稳定验证 SQL 初始化、Mapper 语义、事务回滚和基础约束；高风险 SQL、锁、索引、方言和性能问题补 Testcontainers 或专门集成测试。
- MyBatis / MyBatis Flex 测试配置可集中处理 `@MapperScan`、`ConfigurationCustomizer`、TypeHandler、字段行为函数和审计日志。
- Redis、MQ、HTTP、对象存储、KMS、第三方 SDK 默认作为外部边界替换；只有需要验证协议兼容或真实集成时才进入更重的集成测试。

## 5. 测试底座红线

- 不用全量 Spring 上下文掩盖测试目标不清。
- 不在公共基类中扫描全业务包或塞入所有业务 Bean。
- 不因为继承了测试基类就只验证“调用成功”。
- 不让线程上下文、租户、静态工具、缓存、锁或审计配置污染其他测试。
- 不把外部系统不可用变成单元测试失败原因。
