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

- Java/Spring 测试底座、最小上下文和外部依赖替身读 `testing-practices-java-spring-common.md`。
- 复杂业务测试读 `testing-practices-business-funds.md`。
- 测试总纲读 `testing.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Application Service / Use Case | 1、2、3、4 | Controller 模板 |
| SpringBoot 测试减负 | 5 | 资金域专项 |
| Review 流程测试质量 | 1、4、5 | 示例代码 |

## 1. Spring 服务流程测试策略

Java/Spring 公共测试底座、最小上下文、H2/MyBatis、外部依赖替身和测试基类治理先读 `testing-practices-java-spring-common.md`。本文只保留应用服务流程、事务和副作用断言。

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

## 2. 服务测试基类

服务测试基类只给最小骨架，公共基础设施细节见 `testing-practices-java-spring-common.md`：

```java
@SpringJUnitConfig
@Import(AbstractServiceTest.TestConfig.class)
@Transactional(rollbackFor = Exception.class)
@TestPropertySource(locations = {"classpath:application-h2.properties", "classpath:application-test.properties"})
public abstract class AbstractServiceTest {

    @Configuration
    static class TestConfig {
    }
}
```

## 3. 服务测试子类示例

服务测试子类示例：

```java
@ContextConfiguration(classes = ExampleMessageServiceTests.TestConfig.class)
class ExampleMessageServiceTests extends AbstractServiceTest {

    @Autowired
    private ExampleMessageService exampleMessageService;

    private ExampleMessageDTO exampleMessage;

    @BeforeEach
    void setup() {
        ExampleMessage message = ExampleMessage.example();
        exampleMessage = exampleMessageService.getExampleMessageById(exampleMessageService.createExampleMessage(message));
    }

    @Test
    void updateMessageStatePersistsBusinessFact() {
        exampleMessageService.updateExampleMessageState(exampleMessage.getId(), ExampleMessageState.UNREAD);

        ExampleMessageDTO current = exampleMessageService.getExampleMessageById(exampleMessage.getId());

        Assertions.assertEquals(ExampleMessageState.UNREAD, current.getState());
    }

    @Test
    void rejectIllegalBusinessOperation() {
        Assertions.assertThrows(BusinessException.class, () ->
                exampleMessageService.revokeExampleMessage(exampleMessage.getId(), "other-sender", LocalDateTime.now()));
    }

    @Configuration
    @Import({ExampleMessageServiceImpl.class})
    static class TestConfig {
    }
}
```

## 4. 流程测试断言清单

流程测试必须断言：

- 测试方法名或短注释说清场景、输入、行为、输出和红线。
- 输入被正确转化为业务命令或领域对象。
- route、resolver、assembler、lifecycle 等内部链路真实执行。
- 状态、持久化记录、输出端口、事件或消息符合业务预期。
- 失败时事务回滚，不留下半成功事实。
- 重复执行、并发或幂等键命中时不会产生重复副作用。

## 5. SpringBoot 测试减负

按 `testing-practices-java-spring-common.md` 的最小上下文规则执行。服务流程测试额外关注：真实内部协作者是否保留、事务是否回滚、外部端口是否替换、断言是否落到业务事实和持久化事实。
