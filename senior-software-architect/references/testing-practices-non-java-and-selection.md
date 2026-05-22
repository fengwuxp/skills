# 测试专项实践：非 Java 与选择清单

本文从 `testing-practices.md` 拆出，承载非 Java 技术栈适配和专项实践选择清单。

## 使用时机

- 需要把测试原则迁移到 Go、Node.js、Python、Rust、前端或数据工程。
- 需要用选择清单快速决定专项实践。

## 不适用场景

- Java/Spring 具体测试模板读对应 Java 专题 reference。

## 读取后必须产出

- 技术栈识别、测试层次、验证命令和专项实践选择结果。

## 需要继续读取的 reference

- 跨语言架构读 `language-agnostic-architecture.md`。
- 工作流和验证读 `workflow.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 非 Java 技术栈 | 4 | Java/Spring 模板 |
| 专项实践选择 | 5 | 语言适配细节 |

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
