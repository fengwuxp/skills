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

- 安全设计读 `security-architecture.md`。
- 测试总纲读 `testing.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Controller / MockMvc | 1.3 | 数据库和资金域 |
| Filter / Interceptor | 1.3 中直接请求/响应测试 | Controller 模板扩展 |

## 1. Java/Spring 常见测试实践

Java/Spring 测试的核心不是“启动多少 Spring”，而是判断测试目标需要哪些真实代码、哪些真实装配、哪些外部边界替身。

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
