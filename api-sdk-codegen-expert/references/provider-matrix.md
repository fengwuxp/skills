# Client Provider 选择矩阵

本文用于根据调用方技术栈选择目标 SDK 类型。不要在用户未确认目标调用方时默认生成所有 Provider。

## 1. Provider 列表

| Provider | 目标语言 | 适用场景 |
| --- | --- | --- |
| `AXIOS` | TypeScript | React、Vue、普通 Web 前端，团队使用 axios 请求栈。 |
| `UMI_REQUEST` | TypeScript | Umi / Ant Design Pro / umi-request 技术栈。 |
| `TYPESCRIPT_FEIGN` | TypeScript | 团队已使用 fengwuxp typescript feign 风格，偏装饰器和服务类调用。 |
| `TYPESCRIPT_FEIGN_FUNC` | TypeScript | 偏函数式接口封装，不希望生成 class/decorator 风格。 |
| `DART_FEIGN` | Dart | Flutter/Dart 客户端。 |
| `SPRING_CLOUD_OPENFEIGN` | Java | Spring Cloud 微服务内部调用。 |
| `OPENFEIGN` | Java | 非 Spring Cloud 或轻量 Java Feign Client。 |
| `RETROFIT` | Java / Android | Android、移动端 Java/Kotlin 或 OkHttp/Retrofit 调用栈。 |
| `SPRING_HTTP` | Java | Spring 6+ HTTP Interface 风格，适合 Spring Boot 3+/4+。 |

## 2. 选择流程

1. 先识别调用方：Web 前端、Node 服务、Java 服务、Android、Flutter、外部合作方。
2. 再识别项目已有请求库：axios、umi-request、Feign、Retrofit、Spring HTTP Interface。
3. 如果目标是 Java SDK，确认调用方最低 JDK、Spring/Boot 代际、Validation 命名空间和依赖版本。
4. 检查团队是否已有 SDK 风格约定和目录结构。
5. 检查是否需要统一错误处理、鉴权头、租户头、traceId、重试、超时、取消请求。
6. 给出最多 3 个候选 Provider，说明优缺点和迁移成本。

## 3. 场景建议

| 场景 | 推荐 Provider | 说明 |
| --- | --- | --- |
| React/Vue 前端，已有 axios 封装 | `AXIOS` | 更贴近前端常见实践，便于接入拦截器和错误处理。 |
| Umi / Ant Design Pro 项目 | `UMI_REQUEST` | 与 umi-request 和已有工程习惯一致。 |
| 已有 TypeScript Feign 装饰器体系 | `TYPESCRIPT_FEIGN` | 保持服务类和装饰器风格一致。 |
| 希望轻量函数式 SDK | `TYPESCRIPT_FEIGN_FUNC` | 适合不希望引入 class/decorator 的项目。 |
| Spring Cloud 服务间调用 | `SPRING_CLOUD_OPENFEIGN` | 对接 Spring Cloud OpenFeign 生态。 |
| Spring Boot 3+/4+，希望使用接口式 HTTP Client | `SPRING_HTTP` | 适合 Spring Framework 6 HTTP Interface。 |
| Android / OkHttp 技术栈 | `RETROFIT` | 移动端成熟调用栈。 |
| Flutter | `DART_FEIGN` | 面向 Dart 客户端。 |

## 4. Java 运行时选择

Java Provider 不能只按调用库选择，还要按目标 JDK 和框架代际选择：

| 目标运行时 | Provider 建议 | 注意事项 |
| --- | --- | --- |
| Java 8 | `RETROFIT`、`OPENFEIGN`、兼容 Java 8 的 `SPRING_CLOUD_OPENFEIGN` | 公共 SDK 常见基线；Validation 多为 `javax.validation`；不得生成 Java 9+ 集合工厂、`record`、`var`、sealed 等写法。 |
| Java 11 | `RETROFIT`、`OPENFEIGN`、部分 Spring Cloud OpenFeign | 仍需避免 Java 17 语法；依赖版本要和调用方基线一致。 |
| Java 17+ / Spring 6+ | `SPRING_HTTP`、新版本 Spring Cloud OpenFeign、OpenFeign、Retrofit | Spring 6 / Boot 3 生态通常使用 `jakarta.validation`；可以考虑新语言特性，但公共 SDK 仍应谨慎。 |

`javax.validation` 与 `jakarta.validation` 是二进制和包名层面的生态分界，不应由生成器自动替换。服务端是 Spring Boot 3 / Java 17+ 并不代表外部 SDK 调用方也能使用 `jakarta.validation` 或 Java 17 语法。

## 5. 必须确认的问题

- SDK 使用方是谁？前端、移动端、Java 服务、外部合作方还是测试自动化？
- 是否已有请求基建，例如鉴权、签名、trace、租户、语言包、错误弹窗？
- Java SDK 的最低 JDK 是多少？使用 `javax.validation` 还是 `jakarta.validation`？
- Java SDK 是否允许依赖 Spring 6、Boot 3、HTTP Interface 或 Java 17+ 语言特性？
- SDK 目录是否允许覆盖？是否有手写扩展代码？
- 目标语言是否需要 strict null、eslint、prettier、formatter、包管理配置？
- 是否需要生成 mock、测试、文档或示例调用？
- 是否需要保留历史 SDK 兼容层？

## 6. Provider 红线

- 不得只因为 common-codegen 支持某 Provider 就默认生成。
- 不得忽略调用方已有请求封装和错误处理基建。
- 不得把服务端 JDK 或生成器 JDK 直接当成 Java SDK 调用方 JDK。
- 不得在未确认目标 JDK 时默认使用 Java 17+ 语法、Spring 6 API 或 `jakarta.validation`。
- 不得让生成 SDK 绕过鉴权、签名、租户、traceId、幂等键等必需头。
- 不得把生产域名、token、密钥或内部环境地址硬编码进 SDK。
- 不得覆盖调用方手写扩展目录；生成目录和手写目录应分离。
- 不得在未确认 TypeScript strict/null 策略时随意把字段生成成可选或必填。
