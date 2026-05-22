# 测试专项实践：Spring 服务流程

本文从 `testing-practices.md` 拆出，承载 Spring Application Service / Use Case 流程测试和 SpringBoot 测试减负。

## 使用时机

- 测试对象是应用服务、用例编排、事务边界、状态变化、持久化副作用或内部协作者协同。

## 不适用场景

- 纯 Java 类或数据库行为读 `testing-practices-java-unit-db.md`。
- HTTP 层读 `testing-practices-java-web.md`。

## 读取后必须产出

- 流程测试边界、真实内部链路、外部端口替身、断言事实和 Spring 上下文裁剪方式。

## 需要继续读取的 reference

- 复杂业务测试读 `testing-practices-business-funds.md`。
- 测试总纲读 `testing.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Application Service / Use Case | 1.4 | Controller 模板 |
| SpringBoot 测试减负 | 1.5 | 资金域专项 |

## 1. Java/Spring 常见测试实践

Java/Spring 测试的核心不是“启动多少 Spring”，而是判断测试目标需要哪些真实代码、哪些真实装配、哪些外部边界替身。

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

Spring Boot 4.x 服务测试基类最佳实践：

- 可参考 `wind-integration` 的 `AbstractServiceTest`，把服务测试公共基础设施沉淀为抽象基类，面向 Spring Boot 4.x、H2、MyBatis Flex、事务、缓存、锁、国际化、审计和测试上下文统一治理。
- 基类负责“测试运行底座”，不负责“业务测试目标”：统一 `@SpringJUnitConfig`、`@ImportAutoConfiguration`、`@TestPropertySource`、`@Transactional(rollbackFor = Exception.class)`、`@EnableAspectJAutoProxy`、数据源、事务管理、SQL 初始化、`JdbcTemplate`、测试锁、测试缓存、测试事件发布器和基础上下文工具。
- H2 数据源建议在统一 `DataSource` Bean 创建时执行 `H2FunctionInitializer.initialize(dataSource)`，保证 SQL 初始化、Mapper 测试和 Service 流程测试都能使用 MySQL 兼容函数。
- MyBatis Flex 测试配置可集中处理 `@MapperScan`、`ConfigurationCustomizer`、`LocaleTypeHandler`、SQL 审计日志、字段行为函数和测试态加解密 TypeHandler；这些是测试基础设施，不应散落到每个用例。
- 需要租户、用户、区域、语言、审计上下文时，在基类 `@PostConstruct` 建立，在 `@PreDestroy` 清理；禁止让线程上下文、租户 ID、静态工具类或审计配置污染其他测试。
- 对 `SpringApplicationContextUtils`、`SpringEventPublishUtils` 这类静态工具的测试态初始化，应集中在基类或测试配置中，并明确这是为了兼容历史基础设施，不作为新代码设计范式。
- 基类可以提供 `LockFactory`、`LockTemplate`、`CacheManager`、`LoggingMeterRegistry`、`WindMessageSourceProperties` 等稳定测试基础设施；外部通道、远程 HTTP、MQ、Redis、第三方 SDK 仍由子类或专项测试配置显式替换。
- 子类结合 `@ContextConfiguration(classes = ...)`、`@Import` 或测试专用配置类，精确实例化测试目标类需要的内部依赖；不在基类中默认扫描整个业务包，不把所有业务 Bean 都塞进公共上下文。
- 子类仍必须按业务行为断言状态、落库事实、事务回滚、幂等、副作用和输出结果，不能因为继承了基类就只验证“调用成功”。

服务测试基类结构示例：

```java
@SpringJUnitConfig
@Import(AbstractServiceTest.TestConfig.class)
@ImportAutoConfiguration({
        DataSourceTransactionManagerAutoConfiguration.class,
        JdbcTemplateAutoConfiguration.class,
        DataSourceInitializationAutoConfiguration.class,
        AbstractServiceTest.H2InitializationAutoConfiguration.class,
        MybatisFlexAutoConfiguration.class
})
@Transactional(rollbackFor = Exception.class)
@TestPropertySource(locations = {"classpath:application-h2.properties", "classpath:application-test.properties"})
@EnableAspectJAutoProxy(proxyTargetClass = true)
public abstract class AbstractServiceTest {

    @Configuration
    @Import({MybatisTestConfiguration.class, TestMockRedissonConfiguration.class})
    static class TestConfig {

        @Autowired
        private ApplicationContext applicationContext;

        @PostConstruct
        public void init() {
            ThreadContextTenantIdHolder.setTenantId(1L);
            new SpringApplicationContextUtils().setApplicationContext(applicationContext);
            mockPublishEvent();
            AuditManager.setAuditEnable(true);
        }

        @PreDestroy
        public void stop() {
            ThreadContextTenantIdHolder.remove();
        }

        @Bean
        public LockFactory lockFactory() {
            return new JdkLockFactory();
        }

        @Bean
        @Primary
        public JdbcTemplate jdbcTemplate(DataSource dataSource) {
            return new JdbcTemplate(dataSource);
        }

        @Bean
        public CacheManager cacheManager() {
            return new CaffeineCacheManager();
        }
    }

    @AllArgsConstructor
    @AutoConfiguration
    @EnableConfigurationProperties({DataSourceProperties.class, SqlInitializationProperties.class})
    public static class H2InitializationAutoConfiguration {

        @Bean
        public DataSource dataSource(DataSourceProperties properties) {
            properties.setType(HikariDataSource.class);
            DataSource dataSource = properties.initializeDataSourceBuilder().build();
            H2FunctionInitializer.initialize(dataSource);
            return dataSource;
        }
    }

    @EnableTransactionManagement
    @Configuration
    @MapperScan({"com.wind.**.dal.mapper"})
    public static class MybatisTestConfiguration {

        static {
            AbstractEncryptBaseTypeHandler.setTextEncryptor(new TextEncryptor() {
                @Override
                public String encrypt(String text) {
                    return text;
                }

                @Override
                public String decrypt(String encryptedText) {
                    return encryptedText;
                }
            });
            QueryColumnBehavior.setIgnoreFunction(MybatisFlexQueryBehaviorFuncs::ignoreFunction);
        }

        @Bean
        public ConfigurationCustomizer configurationCustomizer() {
            return configuration -> configuration.getTypeHandlerRegistry()
                    .register(Locale.class, LocaleTypeHandler.class);
        }
    }
}

@Configuration
public class TestMockRedissonConfiguration {

    private static final RedisServer redisServer;

    static {
        try {
            redisServer = new RedisServer(6379);
            redisServer.start();
            Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {
                @Override
                public void run() {
                    if (redisServer.isActive()) {
                        try {
                            redisServer.stop();
                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        }
                    }
                }
            }));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @Bean
    public RedissonClient redissonClient() {
        return Redisson.create();
    }
}
```

服务测试子类示例：

```java
@ContextConfiguration(classes = ExampleMessageServiceTests.TestConfig.class)
class ExampleMessageServiceTests extends AbstractServiceTest {

    @Autowired
    private ExampleMessageService exampleMessageService;

    private ExampleMessageDTO exampleMessage;

    @BeforeEach
    void setup() {
        ExampleMessage message = ExampleMessage.builder()
                .id(RandomStringUtils.secure().nextAlphanumeric(12))
                .sender(ExampleMessageActor.ofUser(RandomStringUtils.secure().nextAlphanumeric(12)))
                .body(List.of(ExampleMessageContent.of(ExampleMessageContentType.TEXT, "hello world")))
                .gmtCreate(LocalDateTime.now())
                .sessionId(RandomStringUtils.secure().nextAlphanumeric(12))
                .sequenceId(RandomUtils.secure().randomLong())
                .build();
        exampleMessage = exampleMessageService.getExampleMessageById(exampleMessageService.createExampleMessage(message));
    }

    /**
     * 场景：更新消息状态。
     * 输入：已存在的消息 ID，目标状态为 UNREAD。
     * 行为：调用服务更新消息状态。
     * 输出：再次查询时状态已变更为 UNREAD。
     * 红线：不能更新不存在的消息，不能影响其他会话消息。
     */
    @Test
    void testUpdateExampleMessageState() {
        exampleMessageService.updateExampleMessageState(exampleMessage.getId(), ExampleMessageState.UNREAD);

        ExampleMessageDTO current = exampleMessageService.getExampleMessageById(exampleMessage.getId());

        Assertions.assertEquals(ExampleMessageState.UNREAD, current.getState());
    }

    /**
     * 场景：撤销消息。
     * 输入：已存在的消息 ID、发送者 ID 和撤销时间。
     * 行为：调用服务撤销消息。
     * 输出：再次查询时状态为 REVOKED。
     * 红线：非发送者不能撤销，超过撤销窗口不能撤销。
     */
    @Test
    void testRevokeExampleMessage() {
        exampleMessageService.revokeExampleMessage(exampleMessage.getId(), exampleMessage.getSenderId(), LocalDateTime.now());

        ExampleMessageDTO current = exampleMessageService.getExampleMessageById(exampleMessage.getId());

        Assertions.assertEquals(ExampleMessageState.REVOKED, current.getState());
    }

    /**
     * 场景：查询会话最新消息。
     * 输入：已存在消息所属的会话 ID。
     * 行为：调用服务查询会话最新消息。
     * 输出：返回该会话最新消息。
     * 红线：不能串到其他会话，不能返回已物理删除数据。
     */
    @Test
    void testFindSessionLatestExampleMessage() {
        ExampleMessageDTO latestMessage = exampleMessageService.findSessionLatestExampleMessage(exampleMessage.getSessionId());

        Assertions.assertNotNull(latestMessage);
        Assertions.assertEquals(exampleMessage.getSessionId(), latestMessage.getSessionId());
    }

    @Configuration
    @Import({ExampleMessageServiceImpl.class})
    static class TestConfig {
    }
}
```

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
