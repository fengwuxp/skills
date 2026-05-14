# 生成 SDK 审查清单

SDK 生成成功不等于契约正确。生成后必须检查契约一致性、类型准确性、兼容性和调用方可用性。

## 0. 与基准生成器对标

如果项目已有 `OpenApiSdkCodegen`、Maven 插件、Builder 或上一版 SDK 产物，审查必须先对标基准；没有完成对标前，不得宣称新生成结果可以替代项目生成器。

- Profile 是否一致，例如 enterprise、personal、partner 是否分别生成，而不是合并成单一 SDK。
- 每个 profile 的扫描包、忽略类、忽略方法、忽略字段和敏感接口边界是否一致。
- 文件数量、Client 列表、Client 包路径、模型包路径是否与基准一致，差异是否可解释。
- 方法签名是否一致：方法名、参数顺序、参数注解、`@Body`、`@Path`、`@Header`、`@QueryMap` / `@Query` 是否一致。
- 返回类型是否一致：裸类型、`Call<T>`、统一响应包装、`Void`、分页类型是否符合基准。
- Query 对象是否符合团队约定，例如是否继承共享 QueryMap 父类，是否保留分页、排序、过滤字段。
- 统一响应解包、post processor、sharedVariables、类型映射和 packageMap 是否已经抽取为配置项。
- TypeScript、Java、Dart 等不同目标的 provider、模板风格、index/export 策略是否与基准一致。
- 编译或类型检查是否在目标 SDK 工程内通过，而不是只检查生成器自身成功。

对标结论建议分级：

| 结论 | 判定标准 |
| --- | --- |
| 可替代 | profile、包结构、方法签名、返回类型、QueryMap、分页、忽略规则和编译结果均可对齐，差异可解释且调用方兼容。 |
| 可迁移 | 大部分规则可配置复现，但仍有少量模板、命名或运行时差异，需要迁移计划和调用方适配。 |
| 草案可用 | 可生成接口草案或辅助审查，但不能作为生产 SDK 发布。 |
| 不建议使用 | 暴露边界、签名、类型、分页、统一响应或兼容性存在关键差异。 |

## 1. 契约一致性

- 路径是否与服务端或 OpenAPI 文档一致。
- HTTP 方法是否正确。
- path 参数是否全部出现在路径模板中。
- query、header、cookie、body、form、multipart 参数位置是否正确。
- `consumes` / `produces` / content type 是否正确。
- 文件上传和下载是否使用正确类型。
- 接口是否遗漏、重复或生成了内部接口。
- 废弃接口是否保留 `deprecated` 提示。

## 2. 类型准确性

- Java / OpenAPI 基础类型是否映射正确。
- Java SDK 是否符合目标 JDK：Java 8 不应出现 `record`、`var`、`List.of`、`Map.of`、sealed class、pattern matching 等不兼容写法。
- 长整型 ID 在 TypeScript 中是否需要使用 `string`，避免精度丢失。
- 金额字段是否明确精度、币种和类型策略。
- 日期时间是否明确格式、时区和序列化策略。
- 枚举值、枚举名、枚举描述是否完整。
- 泛型、数组、Map、嵌套对象是否正确。
- `oneOf`、`allOf`、`anyOf`、discriminator 是否按策略生成。

## 3. 必填与可空

- OpenAPI `required` 是否映射到目标语言必填字段。
- `nullable` 是否正确表达。
- Java Validation 是否映射为注释或类型约束。
- Java SDK 的 Validation 命名空间是否与目标运行时一致：Java 8 / Spring Boot 2 常见 `javax.validation`，Spring Boot 3 / Spring 6 常见 `jakarta.validation`。
- TypeScript 可选字段 `?` 是否和契约一致。
- Java Client 是否明确 `@Nullable`、Validation 或文档说明。
- 不要把空集合、空对象和 `null` 混为一谈。

## 4. 统一响应与分页

- 是否需要解包统一响应。
- 是否保留错误码、错误消息、traceId、requestId。
- 分页结构是否正确，例如 page、size、total、records/items。
- 成功响应和错误响应是否区分。
- SDK 内部是否承担错误处理，还是交给业务层。

## 5. 命名和目录

- Service、Client、Request、Response、Enum 命名是否稳定。
- `operationId` 缺失导致的方法名是否已确认。
- 包名/目录映射是否符合调用方项目规范。
- 生成目录和手写扩展目录是否分离。
- index/export 文件是否完整。
- 是否符合目标语言格式化和 lint 规则。

## 6. 兼容性

- 公共 SDK 是否保持向后兼容。
- Java SDK 是否明确最低 JDK、`maven-compiler-plugin` 的 `release/source/target`、依赖版本和 Spring/Boot 代际。
- 服务端 JDK、生成器 JDK 和 SDK 目标 JDK 是否被区分。
- 删除接口、改路径、改方法、改参数、改字段类型是否有迁移说明。
- 可选字段变必填、返回结构变化、枚举删除或重命名是否标记为破坏性变更。
- 是否需要同时保留旧 SDK 版本。
- 是否需要 changelog 或迁移说明。

## 7. 安全与生产风险

- 不得包含 token、密钥、cookie、生产账号或内部凭证。
- 不得硬编码生产域名、内网地址或临时测试地址。
- 鉴权头、租户头、traceId、幂等键是否保留扩展点。
- 敏感字段是否避免在日志、错误消息、示例中明文出现。
- 生成 SDK 是否会暴露内部管理接口或测试接口。

## 8. 验证建议

按目标语言执行：

| 目标 | 建议验证 |
| --- | --- |
| TypeScript | `npm run typecheck`、`npm test`、`npm run lint`、关键接口 mock 调用。 |
| Java | 按目标 JDK 分别执行 `mvn -DskipTests compile`、`mvn test`，必要时用 Java 8 与 Java 17+ 双矩阵验证。 |
| Dart | `dart analyze`、`dart test`。 |
| 多语言 SDK | 至少验证每种目标语言可编译，并抽样关键接口调用。 |

契约验证：

- 和 OpenAPI 文档做 diff。
- 和上一次生成结果做 diff。
- 抽样生成请求 URL、query、body、header。
- 对文件上传、分页、枚举、错误响应、鉴权头做专项验证。

## 9. Review 输出模板

```text
结论：可用 / 有条件可用 / 不建议使用

主要问题：
- P0/P1/P2/P3：问题、证据、影响、建议

契约检查：
- 路径/方法：
- 参数：
- 请求体：
- 响应体：
- 枚举：
- 必填/可空：
- 统一响应/分页：

验证情况：
- 已运行：
- 未运行及原因：
- 替代验证：

残余风险：
- 文档时效：
- 兼容性：
- 调用方适配：
```
