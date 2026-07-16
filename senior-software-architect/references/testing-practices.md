# 测试专项实践

本文承接 `testing.md` 的总纲，用于 Java/Spring/Wind 项目、复杂业务测试、资金域测试和非 Java 技术栈适配。

## 使用时机

- 已读取 `testing.md`，并命中 Java/Spring、复杂业务、资金域或非 Java 专项测试场景。
- 需要测试模板、测试替身边界、Spring 最小上下文或专项测试手段。

## 不适用场景

- 只需要判断测试类型或测试层次时，优先停留在 `testing.md`。
- Java 代码实现细则读项目本地规范和 `wind-coding-conventions` 通用层；Wind/Nobe 专项按依赖或上下文启用。

## 读取后必须产出

- 测试目标、测试层次、真实代码/替身边界、测试数据、断言重点和验证命令。

## 需要继续读取的 reference

- Java 编码约规读项目本地规范和 `wind-coding-conventions` 通用层；Wind/Nobe 专项按依赖或上下文启用。
- Bug 修复读 `debugging-diagnosis.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Java/Spring 测试底座、最小上下文、外部依赖替身 | `testing-practices-java-spring-common.md` | 具体 Controller / Service 模板 |
| 普通类、工具类、值对象、数据库测试 | `testing-practices-java-unit-db.md` | Controller、资金域、非 Java |
| Controller、Filter、Interceptor、HTTP 层测试 | `testing-practices-java-web.md` | 数据库和资金域专项 |
| Application Service / Use Case 流程测试 | `testing-practices-java-service-flow.md` | Controller 模板细节 |
| 状态机、幂等、并发、遗留保护、资金域 | `testing-practices-business-funds.md` | Spring 启动模板 |
| 非 Java 技术栈或选择清单 | `testing-practices-non-java-and-selection.md` | Java/Spring 细节 |

## 专题 reference 路由

- `testing-practices-java-spring-common.md`：Java/Spring 测试底座、最小上下文、外部依赖替身、公共测试基础设施和 SpringBoot 测试减负。
- `testing-practices-java-unit-db.md`：普通类、工具类、数据库、Mapper、Repository 和事务测试。
- `testing-practices-java-web.md`：Controller、Filter、Interceptor、MockMvc 和 HTTP 层测试。
- `testing-practices-java-service-flow.md`：Spring Application Service / Use Case 流程测试和 SpringBoot 测试减负。
- `testing-practices-business-funds.md`：参数化、状态机、幂等并发、Characterization、Property-based 和资金域测试。
- `testing-practices-non-java-and-selection.md`：非 Java 技术栈适配和专项实践选择清单。
