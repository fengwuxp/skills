# 输入源识别与路由

API SDK 生成前必须先识别输入源。不同输入源的可信边界不同，不能把源码、编译产物和 OpenAPI 文档混为一谈。

## 1. 输入源类型

```text
JAVA_CLASSPATH
JAVA_SOURCE
OPENAPI_V2
OPENAPI_V3
MIXED
```

| 类型 | 典型输入 | 适用场景 | 主要风险 |
| --- | --- | --- | --- |
| `JAVA_CLASSPATH` | Maven/Gradle 项目、已编译类、Controller 包路径 | 项目可编译，依赖可解析，需要真实签名和注解 | 编译失败无法生成；源码注释、SOURCE 级注解可能不足。 |
| `JAVA_SOURCE` | Java 源码文件、源码目录、未编译项目 | 项目尚未编译，或需要源码注释、Javadoc、源码级信息 | 泛型、继承、常量路径、Lombok、注解处理器和外部依赖解析复杂。 |
| `OPENAPI_V2` | Swagger 2.0 JSON/YAML | 已有标准接口文档，需要跨语言 SDK | nullable、oneOf/allOf 表达能力弱；文档可能落后于源码。 |
| `OPENAPI_V3` | OpenAPI 3.0/3.1 JSON/YAML | API-first、跨语言、跨框架、非 Java 服务 | 组合 schema、discriminator、nullable/required 策略必须明确。 |
| `MIXED` | 编译产物 + 源码 + OpenAPI 文档 | 需要互补或契约漂移检查 | 必须定义冲突优先级和合并策略。 |

## 2. 推荐优先级

默认可信度：

```text
已发布 OpenAPI 契约 / 编译产物真实签名
> 当前源码 AST
> 生成中的 OpenAPI 草案
> 自然语言接口描述
```

但具体取舍取决于目标：

- **以真实运行接口为准**：优先 `JAVA_CLASSPATH`。
- **以 API-first 契约为准**：优先 `OPENAPI_V3`。
- **以未编译代码快速生成草案**：使用 `JAVA_SOURCE`，并标记推断风险。
- **以一致性治理为目标**：使用 `MIXED`，比较源码、编译产物和 OpenAPI 差异。

## 3. 识别流程

1. 用户给的是 `pom.xml`、`build.gradle`、Controller 包名或 Java 项目路径：优先判断 `JAVA_CLASSPATH`。
2. 用户给的是 `.java` 文件、源码片段或源码目录：判断 `JAVA_SOURCE`。
3. 用户给的是 `.json`、`.yaml`、`/v3/api-docs`、`/swagger.json` 或 API 文档地址：判断 `OPENAPI_V2` 或 `OPENAPI_V3`。
4. 用户同时给源码和 OpenAPI 文档：判断 `MIXED`，需要说明哪个是主契约。
5. 用户只给自然语言描述：不能直接给生产级 SDK 生成结论，应先转为 OpenAPI 草案或接口清单。

## 4. JAVA_CLASSPATH 模式

适合：

- 服务端是 Java/Spring 项目。
- Maven/Gradle 依赖可解析。
- Controller、DTO、Enum、统一响应类已在 classpath 中。
- 需要读取真实注解、泛型签名和反射信息。

生成前检查：

- 构建工具：Maven 或 Gradle。
- JDK 版本，common-codegen 当前参考仓库使用 Java 21。
- Spring MVC / Spring HTTP Exchange / Swagger2 / OpenAPI3 注解版本。
- Controller 包路径是否明确。
- 是否存在统一响应类型，例如 `ServiceResponse<T>`、`PageInfo<T>`。
- 是否需要忽略内部 Controller、后台接口或隐藏参数。

风险：

- 项目无法编译时，生成链路会中断。
- Lombok 生成方法可能影响反射可见结构。
- `SOURCE` 级注解和部分源码注释不可见。
- 多模块项目需要正确 classpath。

## 5. JAVA_SOURCE 模式

适合：

- 用户只提供源码，尚未完成编译。
- 希望读取 Javadoc、字段注释、方法注释。
- 希望在 AI 编码流程中先生成 SDK 草案或做接口审查。

建议边界：

- 首版只支持 Spring Controller、DTO、Request、Response、Enum。
- 支持 `@RequestMapping`、`@GetMapping`、`@PostMapping`、`@PutMapping`、`@DeleteMapping`、`@PatchMapping`、`@HttpExchange` 等常见注解。
- 支持 `@RequestParam`、`@PathVariable`、`@RequestBody`、`@RequestHeader`、`@CookieValue`、`@RequestPart`。
- 支持 Swagger2 / OpenAPI3 注释注解、Jakarta Validation、Jackson 命名和格式注解。

风险：

- 静态常量路径需要符号解析。
- 父类、接口、泛型边界和外部 DTO 需要源码路径或 classpath。
- Lombok、MapStruct、注解处理器生成内容不一定可见。
- 条件装配和运行时行为不能靠源码 AST 确认。

## 6. OPENAPI 模式

适合：

- 服务端不是 Java，或不希望依赖服务端源码。
- 已有 API-first 契约。
- 需要对外发布 SDK。
- 多语言团队共享接口契约。

生成前检查：

- OpenAPI 版本：2.0、3.0.x、3.1.x。
- 文档来源：文件、URL、CI 产物、网关导出、服务运行时导出。
- 文档时间、版本、commit 或发布环境。
- `operationId` 是否稳定。
- `tags` 是否能映射 service。
- `components.schemas` 是否完整。
- `required`、`nullable`、`default`、`example`、`deprecated` 是否准确。

风险：

- 文档可能落后于服务端实现。
- `operationId` 缺失会导致方法名不稳定。
- 统一响应、错误码和分页可能没有标准化表达。
- `oneOf/allOf/anyOf/discriminator` 需要明确生成策略。

## 7. MIXED 模式

适合：

- 需要验证 OpenAPI 文档是否和 Java Controller 一致。
- 编译产物提供类型准确性，源码提供注释，OpenAPI 提供外部契约。
- 需要做契约漂移检查。

推荐优先级：

| 信息 | 推荐来源 |
| --- | --- |
| HTTP 路径、方法、参数位置 | OpenAPI 或 Controller 注解，冲突时必须报告。 |
| Java 泛型和实际类型 | 编译产物。 |
| 字段注释和方法说明 | OpenAPI description 或源码 Javadoc，按契约来源优先级合并。 |
| required / nullable | OpenAPI 契约优先；Java Validation 可补充。 |
| 统一响应解包 | 项目配置显式声明，不从返回类名猜测。 |

冲突处理：

- 不静默覆盖。
- 输出差异表：字段、路径、方法、参数、类型、必填、可空、枚举。
- 让用户确认主契约来源。
- 高风险差异需要先修正契约，再生成 SDK。

