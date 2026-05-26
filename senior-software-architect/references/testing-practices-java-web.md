# 测试专项实践：Web 与 Controller

本文从 `testing-practices.md` 拆出，承载 Controller、Filter、Interceptor 和 MockMvc 测试实践。

## 使用时机

- 测试对象是 HTTP 参数绑定、校验、统一响应、异常处理、Filter、Interceptor、安全或国际化。

## 不适用场景

- 数据库行为读 `testing-practices-java-unit-db.md`。
- 业务流程编排读 `testing-practices-java-service-flow.md`。

## 读取后必须产出

- HTTP 层测试范围、MockMvc 装配方式、外部依赖替身和响应断言。

## 需要继续读取的 reference

- Java/Spring 测试底座、最小上下文和外部依赖替身读 `testing-practices-java-spring-common.md`。
- 安全设计读 `security-architecture.md`。
- 测试总纲读 `testing.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Controller / MockMvc | 1、2、3 | 数据库和资金域 |
| Filter / Interceptor | 1 中直接请求/响应测试 | Controller 模板扩展 |
| Review Web 测试质量 | 1、4 | 模板代码 |

## 1. Web 与 Controller 测试策略

Java/Spring 公共测试底座、最小上下文、外部依赖替身和测试基类治理先读 `testing-practices-java-spring-common.md`。本文只保留 HTTP 层差异。

适用对象：

- Controller、Filter、Interceptor、参数绑定、校验、统一响应、异常处理、签名、安全、国际化、序列化。

默认策略：

- 优先 MockMvc，验证 HTTP 层行为，避免启动真实 Tomcat。
- 通过 `@ContextConfiguration`、精确 `@Import` 或测试专用配置控制 Bean 范围。
- Nacos、MQ、Redis、OSS、KMS 等外部依赖应禁用或替换为 Mock/Fake；公共替身边界按 `testing-practices-java-spring-common.md`。
- Filter/Interceptor 可直接使用 `MockHttpServletRequest`、`MockHttpServletResponse`、`MockFilterChain`。
- Controller 可使用 `webAppContextSetup` 或 standalone MockMvc。
- 断言 HTTP 状态、响应 JSON、错误码、错误消息、Header、签名属性、国际化结果和安全拦截结果。
- 只有需要验证全局异常处理、参数转换、拦截器链、消息转换器时，才使用 WebApplicationContext。

Wind 实践提炼：

- `AbstractControllerTest` 使用 `@SpringJUnitConfig`、`@WebAppConfiguration` 和 `MockMvcBuilders.webAppContextSetup`，同时禁用 Nacos 配置。
- `RequestSignFilterTests` 直接构造请求、响应和过滤器链，验证签名缺失、签名成功、签名过期等 HTTP 安全场景。
- `IpAccessControlFilterTests` 直接测试过滤器，不启动 Web 容器，断言状态码和错误消息。
- `RestfulApiRespFactoryTests` 通过测试消息源和 Locale 验证统一响应与国际化。

## 2. Controller 测试基类

Controller 测试最小模板：

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
```

## 3. Controller 测试子类示例

```java
@Import(ExampleControllerTests.TestConfig.class)
class ExampleControllerTests extends AbstractControllerTest {

    @Autowired
    private ExampleApplicationService exampleApplicationService;

    @Test
    void createExampleReturnsBusinessId() throws Exception {
        Mockito.when(exampleApplicationService.createExample(Mockito.any()))
                .thenReturn(new ExampleDTO("example-id", "created"));

        MvcResult mvcResult = mvc.perform(MockMvcRequestBuilders.post("/api/v1/examples/{accountId}/items",
                                "example-account")
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .header("X-Request-Id", "request-001")
                        .content("{\"name\":\"demo\",\"amount\":100}"))
                .andReturn();

        Assertions.assertEquals(200, mvcResult.getResponse().getStatus());
        Assertions.assertTrue(mvcResult.getResponse().getContentAsString().contains("example-id"));
    }

    @Test
    void invalidRequestDoesNotEnterApplicationService() throws Exception {
        MvcResult mvcResult = mvc.perform(MockMvcRequestBuilders.post("/api/v1/examples/{accountId}/items",
                                "example-account")
                        .contentType(MediaType.APPLICATION_JSON_VALUE)
                        .content("{}"))
                .andReturn();

        Assertions.assertTrue(mvcResult.getResponse().getStatus() >= 400);
        Mockito.verifyNoInteractions(exampleApplicationService);
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

## 4. 使用要点

- 基类负责 Web 测试底座：`WebApplicationContext`、`MockMvc` 构建、测试属性和通用 Web 配置。
- 子类负责目标 Controller、必要配置和外部依赖替身；不要把全量业务 Bean、远程客户端、MQ、Redis、Nacos 等带进 Controller 测试。
- 每个测试方法上方或方法名必须表达场景、输入、行为、输出和红线；复杂场景再补短注释。
- `@WebMvcTest` 适合验证单个或少量 Controller 的 HTTP 行为；如果使用 `@WebMvcTest`，不要再混入会扫描全应用的 `@SpringBootApplication(scanBasePackages = ...)`。
- 使用 `@ContextConfiguration` 基类时，子类优先通过精确 `@Import(ExampleController.class)` 装配目标 Controller；确需扫描时使用真实基础包名，不使用通配符表达式。
- 断言至少覆盖 HTTP 状态、响应内容、错误码/错误消息、Header、路径参数、查询参数、请求体绑定和校验结果；不要只断言响应非空。
- Controller 测试可以 mock 应用服务或外部端口，但不能 mock 掉参数绑定、校验、序列化、异常处理和安全拦截这些 HTTP 层语义。
