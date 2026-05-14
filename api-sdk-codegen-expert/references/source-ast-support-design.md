# Java 源码 AST 支持设计

Java 源码 AST 输入适合在项目未编译、依赖不完整或需要读取源码注释时使用。它应作为编译产物模式的补充，而不是替代。

## 1. 核心定位

源码 AST 解析的目标：

```text
Java 源码
-> Controller / DTO / Enum AST
-> 注解、Javadoc、字段、方法、参数、泛型
-> 统一 API 契约模型
-> SDK 生成或契约审查
```

推荐使用 JavaParser / SymbolSolver 一类能力解析源码结构和符号。已有 common-codegen 中的源码注释增强可以作为基础，但完整 AST 生成需要新增解析主链路。

技能内置 `scripts/spring_source_to_openapi.py` 作为轻量级源码导出器，用于没有标准 OpenAPI 文档、且用户希望先验证生成链路时：

```text
Spring Controller 源码
-> OpenAPI 3 草案
-> scripts/generate_sdk.py
-> Java Retrofit / TypeScript fetch SDK
```

它不是完整 JavaParser，也不替代编译产物模式；导出的 OpenAPI 只能作为草案或验证输入，生产使用前必须做源码/编译产物/运行时契约复核。

## 2. 首版支持边界

优先支持：

- Spring MVC Controller。
- Spring HTTP Exchange 接口。
- DTO、Request、Response、Query、VO、Enum。
- Java `record`、普通 class、interface。
- 常见 HTTP 注解：
  - `@RequestMapping`
  - `@GetMapping`
  - `@PostMapping`
  - `@PutMapping`
  - `@DeleteMapping`
  - `@PatchMapping`
  - `@HttpExchange`
  - `@GetExchange`
  - `@PostExchange`
- 常见参数注解：
  - `@RequestParam`
  - `@PathVariable`
  - `@RequestBody`
  - `@RequestHeader`
  - `@CookieValue`
  - `@RequestPart`
- Swagger2 / OpenAPI3 注释注解。
- Jakarta / Javax Validation。
- Jackson 命名、格式化、忽略字段等注解。
- Fastjson `@JSONField(serialize = false)`、Jackson `@JsonIgnore` 这类基础隐藏字段。

暂不承诺：

- 完整支持所有 Spring 条件装配和运行时路由。
- 完整展开 Lombok 生成的构造器、getter、setter、builder。
- 完整解析复杂泛型协变、递归泛型和多模块符号。
- 完整解析静态内部类、匿名类、局部类和由注解处理器生成的类型；源码草案可保留占位或生成可编译的降级类型，但必须报告 warning。
- 解析运行时动态注册的路由。
- 完整解析同名类冲突、复杂静态常量表达式和跨模块继承字段。

## 3. 解析流程

```text
源码根目录
-> 建立源码索引
-> 解析 import、package、class/interface/record/enum
-> 解析 Controller 路由和方法
-> 解析参数位置、请求体、响应体
-> 解析 DTO 字段、注解、Javadoc、枚举
-> 尝试符号解析
-> 标记推断项和无法解析项
-> 生成统一契约模型
```

源码根选择必须覆盖 Controller 以及契约依赖的源码，不应只扫描 Controller 模块。至少纳入：

- Controller 所在模块，例如 `web/openapi/src/main/java`。
- DTO、Request、Query、Enum 所在模块，例如 `openapi-domain/*-face/src/main/java`。
- 被 API 暴露的 core/domain enum 和 value object 所在模块。
- 静态路径、Header 名、租户名等常量所在模块，例如 `web/configuration/src/main/java`。
- QueryMap 父类、分页类型、排序类型的源码或配置映射；无法纳入源码时，必须通过 `typeMappings`、`ignore_parameter_schema_names` 或共享类型配置显式处理。

如果只扫描 Controller 模块，常见退化包括：`@RequestHeader(CONSTANT)` 变成常量名字符串、Query 对象字段为空、枚举退化为 `String`、分页类被生成成 `PaginationOfXxx`、项目忽略参数被错误暴露。

## 4. 路由解析规则

- 类级 `@RequestMapping` 与方法级 Mapping 合并。
- `value`、`path`、数组路径和空路径都要处理。
- HTTP 方法来自专用 Mapping 注解或 `@RequestMapping(method = ...)`。
- 路径常量引用需要符号解析；轻量导出器支持简单 `static final String` 常量和 `A + B` 拼接，无法解析时标记为待确认。
- 静态导入常量也必须能在源码索引中找到；找不到时应保留 warning，并在生成后检查 Header/Path 是否仍为 Java 常量名。
- `produces`、`consumes` 应映射到媒体类型。
- 父类 Controller 和接口默认方法需要谨慎处理，缺少符号时不要静默忽略。

## 5. 参数解析规则

| 参数来源 | SDK 映射 |
| --- | --- |
| `@PathVariable` | path 参数，必须出现在路径模板中。 |
| `@RequestParam` | query 或 form 参数，取决于 consumes 和方法。 |
| `@RequestBody` | JSON request body。 |
| `@RequestHeader` | header 参数，注意鉴权、租户、trace 等公共头。 |
| `@CookieValue` | cookie 参数。 |
| `@RequestPart` | multipart 参数或文件上传。 |
| 无注解复杂对象 | Spring MVC 常作为 query/form model，需要结合 consumes 和项目约定确认。 |

Query 对象策略：

- Loong/Wind 风格通常保留一个 `@QueryMap QueryObject query` 参数，而不是把 Query 对象字段展开成多个 `@Query` 参数。
- 如果方法有多个无注解复杂参数，应结合项目生成器的忽略规则处理，例如 `DefaultPageQueryOptions` 这类分页/排序运行时参数通常不应暴露到 SDK 方法签名。
- 内置导出器会用 `x-java-query-object` 标记无注解复杂对象，后续 `scripts/generate_sdk.py` 可按 `query_object_strategy: query_map` 生成 `@QueryMap`。

## 6. DTO 和字段解析

必须保留：

- 字段名和 Java 类型。
- 泛型参数。
- Javadoc 或字段注释。
- Validation 必填、长度、格式、范围。
- Jackson 字段名、日期格式、忽略字段。
- Swagger/OpenAPI description、example、required、hidden、deprecated。
- 枚举常量和枚举说明。
- 源 Java package 和 full name；后续包映射必须能按原始 package 映射到目标 SDK package。

不确定项：

- Lombok `@Data` 并不等于字段全部可写入 API。
- 字段可空性不能只从 Java 原始类型推断；优先使用 Validation、JSpecify、OpenAPI schema 和项目约定。
- 继承字段需要能追踪来源；无法解析父类时应提示。

## 7. 与编译产物混合

推荐混合策略：

| 信息 | 优先来源 |
| --- | --- |
| 方法真实签名、泛型擦除前结构 | 编译产物或符号解析。 |
| Javadoc、源码注释、源码级描述 | 源码 AST。 |
| OpenAPI 对外契约 | OpenAPI 文档。 |
| Validation、Jackson、Swagger 注解 | 三者可互补，冲突时报告。 |

混合模式可以做契约漂移检查：

- Controller 路径和 OpenAPI 路径不一致。
- 请求参数必填不一致。
- DTO 字段类型不一致。
- 枚举值不一致。
- `nullable` 和 Validation 不一致。
- deprecated 状态不一致。

## 8. 源码 AST 红线

- 不得把源码解析结果包装成真实运行时契约。
- 不得静默忽略无法解析的父类、接口、泛型或常量路径。
- 不得把 Lombok 注解自动等价为完整运行时代码。
- 不得凭字段名猜测业务含义、统一响应解包或错误码。
- 不得在存在 OpenAPI 发布契约时，用源码草案静默覆盖发布契约。
- 高风险 SDK 应结合编译产物或 OpenAPI 契约做二次校验。
