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

Controller 测试基类与子类模板：

```java
@ContextConfiguration(classes = {AbstractControllerTest.TestConfig.class})
@SpringJUnitConfig
@WebAppConfiguration
@TestPropertySource(properties = "spring.cloud.nacos.config.enabled=false")
public abstract class AbstractControllerTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    protected MockMvc mvc;

    @BeforeEach
    void setup() {
        mvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Configuration
    static class TestConfig {
    }
}

@Import(ExampleControllerTests.TestConfig.class)
class ExampleControllerTests extends AbstractControllerTest {

    @Autowired
    private ExampleApplicationService exampleApplicationService;

    /**
     * 场景：创建 Example。
     * 输入：合法 JSON 请求、Header 和查询参数。
     * 行为：调用 Controller 创建 Example。
     * 输出：HTTP 200，响应包含业务 ID。
     * 红线：请求参数不能丢失，Controller 不直接写业务规则。
     */
    @Test
    void testCreateExample() throws Exception {
        Mockito.when(exampleApplicationService.createExample(Mockito.any()))
                .thenReturn(new ExampleDTO("example-id", "created"));

        MvcResult mvcResult = mvc.perform(MockMvcRequestBuilders.post("/api/v1/examples/{accountId}/items",
                                "example-account")
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .header(HttpHeaders.HOST, "localhost")
                        .header("X-Request-Id", "request-001")
                        .queryParam("source", "example")
                        .content("""
                                {
                                  "name": "demo",
                                  "amount": 100
                                }
                                """))
                .andReturn();

        Assertions.assertEquals(200, mvcResult.getResponse().getStatus());
        Assertions.assertTrue(mvcResult.getResponse().getContentAsString().contains("example-id"));
    }

    /**
     * 场景：请求参数不合法。
     * 输入：缺少必填字段的 JSON 请求。
     * 行为：触发参数绑定和校验。
     * 输出：HTTP 4xx，响应包含错误信息。
     * 红线：非法请求不能进入业务服务。
     */
    @Test
    void testRejectInvalidExampleRequest() throws Exception {
        MvcResult mvcResult = mvc.perform(MockMvcRequestBuilders.post("/api/v1/examples/{accountId}/items",
                                "example-account")
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .content("{}"))
                .andReturn();

        Assertions.assertTrue(mvcResult.getResponse().getStatus() >= 400);
        Mockito.verifyNoInteractions(exampleApplicationService);
    }

    /**
     * 场景：查询 Example 详情。
     * 输入：路径参数和查询参数。
     * 行为：调用 Controller 查询详情。
     * 输出：HTTP 200，响应为指定 ID 的详情。
     * 红线：不能串账号、不能忽略路径参数。
     */
    @Test
    void testGetExampleDetail() throws Exception {
        Mockito.when(exampleApplicationService.getExampleDetail("example-account", "example-id", "zh-CN"))
                .thenReturn(new ExampleDTO("example-id", "created"));

        MvcResult mvcResult = mvc.perform(MockMvcRequestBuilders.get("/api/v1/examples/{accountId}/items/{exampleId}",
                                "example-account", "example-id")
                        .accept(MediaType.APPLICATION_JSON_VALUE)
                        .queryParam("locale", "zh-CN"))
                .andReturn();

        Assertions.assertEquals(200, mvcResult.getResponse().getStatus());
        Assertions.assertTrue(mvcResult.getResponse().getContentAsString().contains("example-id"));
    }

    @Configuration
    @Import(ExampleController.class)
    static class TestConfig {

        @Bean
        public ExampleApplicationService exampleApplicationService() {
            return Mockito.mock(ExampleApplicationService.class);
        }

        @Bean
        public I18nMetadataService i18nMetadataService() {
            return Mockito.mock(I18nMetadataService.class);
        }
    }
}
```

使用要点：

- 基类负责 Web 测试底座：`WebApplicationContext`、`MockMvc` 构建、测试属性和通用 Web 配置。
- 子类负责目标 Controller、必要配置和外部依赖替身；不要把全量业务 Bean、远程客户端、MQ、Redis、Nacos 等带进 Controller 测试。
- `@WebMvcTest` 适合验证单个或少量 Controller 的 HTTP 行为；如果使用 `@WebMvcTest`，不要再混入会扫描全应用的 `@SpringBootApplication(scanBasePackages = ...)`。
- 使用 `@ContextConfiguration` 基类时，子类优先通过精确 `@Import(ExampleController.class)` 装配目标 Controller；确需 `scanBasePackages` 时使用真实基础包名，不使用通配符表达式。
- 每个测试方法上方写清场景、输入、行为、输出和红线；不要把说明塞进方法体内部。
- 断言至少覆盖 HTTP 状态、响应内容、错误码/错误消息、Header、路径参数、查询参数、请求体绑定和校验结果；不要只断言响应非空。
- Controller 测试可以 mock 应用服务或外部端口，但不能 mock 掉参数绑定、校验、序列化、异常处理和安全拦截这些 HTTP 层语义。

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
