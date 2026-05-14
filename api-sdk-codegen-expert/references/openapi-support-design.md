# 标准 OpenAPI 支持设计

标准 OpenAPI 输入应成为 API SDK 代码生成的一等输入。它适合 API-first、非 Java 服务、跨语言团队和对外 SDK 发布场景。

本技能内置 `scripts/generate_sdk.py`，用于在没有项目内 Java 生成器、没有 Maven/Gradle 环境，或用户明确希望直接从 OpenAPI 文档生成时，生成 Java Retrofit 或 TypeScript fetch SDK。

## 1. 支持范围

优先支持：

- Swagger 2.0 JSON/YAML。
- OpenAPI 3.0.x JSON/YAML。
- OpenAPI 3.1.x JSON/YAML。

内置生成器 MVP 支持：

- OpenAPI 3.x JSON；YAML 在安装 PyYAML 时支持。
- Java Retrofit interface + 普通 POJO model + enum。
- TypeScript fetch function + interface/type。
- path/query/header/body 参数和基础 request/response schema。
- 基础 `required` 到 Java Validation / TypeScript 可选字段映射。

解析对象：

| OpenAPI 元素 | 生成含义 |
| --- | --- |
| `paths` | Service / Client 方法集合。 |
| `operationId` | 方法名；缺失时需要稳定命名策略或用户确认。 |
| `tags` | Service 分组或目录。 |
| `parameters` | path/query/header/cookie 参数。 |
| `requestBody` | JSON/form/multipart 请求对象。 |
| `responses` | 响应类型、状态码、错误响应。 |
| `components.schemas` | DTO、VO、Request、Response、Enum。 |
| `required` | 必填字段。 |
| `nullable` | 可空语义。 |
| `default` / `example` | 默认值和示例注释。 |
| `description` / `summary` | 注释和方法说明。 |
| `deprecated` | 废弃标记和兼容提示。 |

## 2. 解析流程

```text
OpenAPI 文档
-> 版本识别
-> paths/operations 解析
-> schemas 解析
-> 参数和 requestBody 归一
-> response 和错误响应归一
-> 统一 API 契约模型
-> Provider 模板输出
```

## 3. 必须保留的契约语义

- HTTP 方法、路径和 path 参数。
- 参数位置：path、query、header、cookie、body、form、multipart。
- `required` 和 `nullable`。
- 数组、对象、枚举、Map、文件上传。
- 响应状态码，至少保留成功响应和默认错误响应。
- 媒体类型，例如 `application/json`、`multipart/form-data`。
- `deprecated`。
- schema 引用和循环引用。

## 4. operationId 策略

`operationId` 是 SDK 方法名的最佳来源。缺失时不要随意生成不稳定命名。

推荐策略：

1. 优先使用 `operationId`。
2. 其次使用 `tags + method + normalizedPath`。
3. 再其次使用 `summary` 或路径语义推导，但必须标记为推断。
4. 对外 SDK 或公共 SDK 场景，缺少 `operationId` 应提示用户先修正文档。

## 5. schema 映射策略

| OpenAPI 类型 | TypeScript | Java | Dart |
| --- | --- | --- | --- |
| `string` | `string` | `String` | `String` |
| `integer` | `number` | `Integer` / `Long` | `int` |
| `number` | `number` | `BigDecimal` / `Double` | `num` / `double` |
| `boolean` | `boolean` | `Boolean` | `bool` |
| `array` | `T[]` / `Array<T>` | `List<T>` | `List<T>` |
| `object` | `Record<string, T>` 或 interface | `Map<String, T>` 或 class | `Map<String, T>` 或 class |
| `string` + `format: binary` | `File` / `Blob` | `Resource` / `MultipartFile` | 文件类型 |
| `string` + `format: date-time` | `string` / Date 策略 | `OffsetDateTime` / `LocalDateTime` | `DateTime` |

金额和 ID 不应只看 `type`：

- 金额字段优先要求明确格式、精度、币种和舍入规则。
- 长整型 ID 在 TypeScript 中需要确认是否使用 `string`，避免超过 `Number.MAX_SAFE_INTEGER`。

## 6. 组合 schema

| 结构 | 建议 |
| --- | --- |
| `allOf` | 优先映射为继承、交叉类型或合并对象；冲突字段必须报出。 |
| `oneOf` | 优先使用联合类型或 sealed/polymorphic 模型；需要 discriminator 或明确策略。 |
| `anyOf` | 风险最高，建议用户确认生成策略。 |
| `discriminator` | 保留类型判别字段和映射关系。 |

红线：

- 不得把 `oneOf`、`anyOf` 简单拍扁成普通对象。
- 不得静默丢弃 discriminator。
- 不得忽略 required/nullable 冲突。

## 7. 统一响应与错误码

OpenAPI 文档常见问题是只描述统一响应壳，例如：

```json
{
  "code": "0",
  "message": "success",
  "data": {}
}
```

生成 SDK 前必须确认：

- 是否要解包 `data`。
- 错误响应是否也使用同一结构。
- 分页结构是否需要解包。
- code/message/traceId/requestId 是否保留在 SDK 层。
- 调用方错误处理是在 SDK 内部还是业务层。

不得根据类名或字段名自动猜测解包策略；必须通过配置或用户确认。

## 8. OpenAPI 输入红线

- 文档版本、来源、生成时间或 commit 不清楚时，必须提示契约时效风险。
- 缺少 `operationId`、`required`、`nullable` 时，不能给“完全生产可用”的结论。
- 不得忽略 `deprecated` 字段和废弃接口。
- 不得把测试环境文档直接当生产契约。
- 不得在文档和源码冲突时静默选择一个来源。
- 不得硬编码 server URL、token、cookie 或生产地址到生成 SDK。
