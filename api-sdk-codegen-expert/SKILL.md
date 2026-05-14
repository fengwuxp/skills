---
name: api-sdk-codegen-expert
description: 面向 Java/Spring、Java 源码 AST、Swagger/OpenAPI 契约和多语言 API SDK 生成的专家技能。适用于实际生成 API SDK、分析 common-codegen / Loong Codegen 生成方案，配置 Maven 插件或 Builder，选择 TypeScript、Axios、Umi、Dart、OpenFeign、Retrofit、Spring HTTP 等客户端，并审查生成结果的契约一致性、类型准确性、兼容性和生产可用性。
---

# API SDK 代码生成专家

当用户要求根据 Java Controller、Swagger/OpenAPI 注解、标准 OpenAPI 文档、源码或接口契约生成 API SDK，或评估、配置、审查 common-codegen / Loong Codegen 时，使用本技能。

本技能不是 DDL 到后端 Service 代码生成器；DDL、字段表格、Java Entity 到 MyBatis-Flex Service 脚手架的场景使用 `java-service-code-generator`。普通架构设计、代码 Review 和生产风险审查可结合 `资深架构师`。

## 本地协作学习机制

本地协作学习机制默认关闭。只有用户明确同意启用，且本地学习目录存在 `consent.md` 并标记为启用、授权当前技能或全局范围时，才读取或写入学习记录。默认目录为 `~/.skill-learning/`；如设置了 `SKILL_LEARNING_HOME`，则优先使用该目录。

如果尚未启用，应先按仓库 `AGENTS.md` 中的学习时机判定算法判断当前任务是否已经出现稳定偏好、团队约规、业务背景、反复决策方式等长期沉淀价值；只有达到问询阈值，且不会打断关键任务时，才可以用一句话询问用户是否启用。用户拒绝时，不创建目录或文件，不在当前会话再次提示，除非用户主动提及。

用户在当前技能场景下同意时，默认只开启 `api-sdk-codegen-expert`；只有用户明确要求“所有技能”或“全局开启”时，才对所有技能生效。启用后默认采用混合模式与协作型学习模型：记录前必须先经过候选识别、价值评分、风险门禁和动作决策；低风险常规观察可静默进入 `Pending Observations`，可能影响长期行为、跨技能复用、业务/合规/隐私边界或强约束偏好的记录必须显示确认；发现用户判断或设计可能存在错误、逻辑漏洞或红线风险时，必须显示提示并讨论改进方式。未经用户明确确认，不得提升为 `Confirmed Agreements`，也不得提交、上传或共享到远程。学习记录不得写入本技能目录或 Codex 的技能安装目录。

## 核心定位

API SDK 代码生成的目标不是“把接口代码机械翻译成客户端代码”，而是把服务端接口契约实际转为可调用、可审查、可演进的客户端资产：

```text
输入源识别 -> 契约建模 -> 生成模式选择 -> 配置设计 -> 执行生成 -> 生成结果审查 -> 交付与演进建议
```

核心原则：

- **契约优先**：路径、HTTP 方法、参数位置、请求体、响应体、枚举、必填、可空、分页、统一响应和错误语义必须明确。
- **输入分层**：编译产物、源码 AST、标准 OpenAPI 和混合输入各有可信边界，不相互替代。
- **项目规则优先**：当项目已经存在 `OpenApiSdkCodegen`、Maven 插件、Builder 或历史生成产物时，它们通常沉淀了团队的 profile、包名映射、类型映射、过滤规则和模板风格，应作为基准或适配器优先使用。
- **内置生成兜底**：标准 OpenAPI 输入可使用技能自带 `scripts/generate_sdk.py` 生成基础 SDK；只有 Spring Controller 源码时，可先用 `scripts/spring_source_to_openapi.py` 导出 OpenAPI 草案，再执行生成。内置生成器是无项目生成入口时的兜底与验证工具，不默认等价替代团队生成器。
- **生成优先**：用户明确要求“生成”时，必须实际产出 SDK 源码、生成配置、生成入口或可执行脚本；不能只停留在方案和评审。
- **生成可审查**：SDK 生成结果必须能被人工和自动化检查，不能把生成成功等同于契约正确。
- **生产可控**：不得默认覆盖调用方已改造 SDK，不得默认上传到 codegen-server，不得写入密钥、生产地址或内部凭证。

## 场景路由

| 用户任务 | 必读参考 | 输出要求 |
| --- | --- | --- |
| 了解 common-codegen / Loong Codegen 能力 | `references/common-codegen-overview.md` | 说明模块边界、生成链路、核心入口、适用和不适用场景。 |
| 判断应使用源码、编译产物还是 OpenAPI | `references/input-source-routing.md` | 识别输入类型、可信度、风险、推荐模式和待确认项。 |
| 设计或审查生成配置 | `references/generation-configuration.md` | 给出扫描范围、目标 Provider、输出目录、项目生成器配置抽取项、包名映射、覆盖策略和验证命令。 |
| 选择目标 SDK / Client Provider | `references/provider-matrix.md` | 根据调用方技术栈选择 TypeScript、Axios、Umi、Dart、OpenFeign、Retrofit、Spring HTTP 等 provider。 |
| 生成 Maven 插件或 Builder 配置 | `references/integration-recipes.md`、`references/common-codegen-overview.md` | 给出 scanPackages、clientProviderTypes、openApiType、outputPath、类型映射、包名映射和自定义生成器建议。 |
| 实际执行 SDK 生成 | `references/generation-configuration.md`、`references/integration-recipes.md`、`references/generated-sdk-review-checklist.md` | 选择或创建生成入口，执行生成命令，处理环境问题，并审查生成结果。 |
| 使用内置生成器从 OpenAPI 生成 | `references/openapi-support-design.md`、`references/generation-configuration.md`、`scripts/generate_sdk.py` | 直接从 OpenAPI 3 JSON/YAML 生成 Java Retrofit 或 TypeScript fetch SDK。 |
| 从 Spring 源码生成 SDK 草案 | `references/source-ast-support-design.md`、`references/generation-configuration.md`、`scripts/spring_source_to_openapi.py`、`scripts/generate_sdk.py` | 先从 Spring Controller 源码导出 OpenAPI 3 草案，再生成 SDK，并标记源码解析风险。 |
| 对标项目已有生成器 | `references/generation-configuration.md`、`references/generated-sdk-review-checklist.md` | 先运行或读取项目已有生成结果，抽取 profile、包名映射、类型映射、过滤规则和方法签名，沉淀为中立配置，再判断内置生成是否只是草案、可迁移还是可替代。 |
| 设计标准 OpenAPI 支持 | `references/openapi-support-design.md` | 按 OpenAPI v2/v3 解析 paths、operationId、parameters、requestBody、responses、schemas、required、nullable 和组合 schema。 |
| 设计 Java 源码 AST 支持 | `references/source-ast-support-design.md` | 说明源码解析边界、JavaParser/SymbolSolver 能力、Lombok/泛型/常量路径风险和混合解析策略。 |
| 审查生成的 SDK | `references/generated-sdk-review-checklist.md` | 检查契约一致性、类型准确性、兼容性、空值、必填、枚举、文件上传、分页、统一响应和验证结果。 |

## 输入源路由

| 输入源 | 适用场景 | 可信边界 |
| --- | --- | --- |
| `JAVA_CLASSPATH` | Maven/Gradle 项目可编译，Controller/DTO/Enum 已在 classpath 中 | 类型和注解较准确，但源码注释、未编译代码、SOURCE 级信息可能不足。 |
| `JAVA_SOURCE` | 用户只有源码，或希望未编译前生成/审查 SDK | 注释和源码信息丰富，但泛型、继承、常量路径、Lombok、注解处理器和依赖解析复杂。 |
| `OPENAPI_V2` | Swagger 2.0 JSON/YAML 契约 | 通用性强，但 schema 表达能力、nullable、组合类型能力有限。 |
| `OPENAPI_V3` | OpenAPI 3.0/3.1 JSON/YAML 契约 | 行业标准输入，适合 API-first；oneOf/allOf/anyOf/discriminator 需要明确策略。 |
| `MIXED` | 同时有编译产物、源码和 OpenAPI 文档 | 能互补和做契约漂移检查，但必须明确冲突优先级。 |

输入可信度建议：

```text
已发布 OpenAPI 契约 / 编译产物真实签名 > 当前源码 AST > 生成中的 OpenAPI 草案 > 自然语言接口描述
```

## 生成目标

common-codegen 当前可作为核心参考实现，主要支持：

- TypeScript Feign：`TYPESCRIPT_FEIGN`
- TypeScript Function Feign：`TYPESCRIPT_FEIGN_FUNC`
- Umi Request：`UMI_REQUEST`
- Axios：`AXIOS`
- Dart Feign：`DART_FEIGN`
- Spring Cloud OpenFeign：`SPRING_CLOUD_OPENFEIGN`
- OpenFeign：`OPENFEIGN`
- Retrofit：`RETROFIT`
- Spring HTTP Interface：`SPRING_HTTP`

选择原则：

- React/Vue/普通 Web 前端优先评估 `AXIOS`、`UMI_REQUEST` 或 `TYPESCRIPT_FEIGN`。
- Java 微服务调用优先评估 `SPRING_CLOUD_OPENFEIGN`、`SPRING_HTTP` 或 `OPENFEIGN`。
- Android 或移动端 Java 场景评估 `RETROFIT`。
- Flutter/Dart 场景评估 `DART_FEIGN`。
- 未确认调用方技术栈时，不默认生成所有 SDK；先给 2-3 个可选方案和影响。

## 配置能力

当用户要求生成、执行、迁移或审查 SDK 生成方案时，必须提供可审查的配置能力，而不是只给一段不可解释的生成代码。配置至少覆盖：

- 扫描范围：`scanPackages`、源码目录、编译模块、OpenAPI 文件或 URL、include/exclude 规则。
- 生成目标：目标语言、Client Provider、SDK profile、输出目录、包名/目录映射和命名策略。
- 项目生成器规则：已有 `OpenApiSdkCodegen`、Maven 插件或 Builder 中的 profile、packageMap、typeMappings、sharedVariables、postProcessors、ignore rules、QueryMap、统一响应解包、分页和模板风格必须抽取成配置项。
- Java 运行时：Java SDK 必须明确目标 JDK、Spring/Boot 代际、Validation 命名空间和可用语言特性。
- 契约策略：统一响应、分页、错误码、枚举、文件上传、日期时间、金额、ID、必填和可空映射。
- 执行策略：是否清理输出目录、是否备份、是否 dry-run、生成后验证命令和差异审查方式。

配置优先级为：用户显式配置 > 项目已有 codegen 配置 > 团队约定 > 技能推断建议。涉及扫描根包、输出目录覆盖、删除旧输出、上传到外部服务、暴露内部接口时，必须显式确认。详细配置模板见 `references/generation-configuration.md`。

## 工作流程

1. 识别输入：确认用户提供的是 Java 项目、源码片段、Controller 包路径、OpenAPI 文件、Swagger 文档地址、生成结果目录还是配置片段。
2. 明确配置：确认或推断扫描范围、目标调用方、Client Provider、输出语言、输出目录、覆盖策略、统一响应解包、分页模型、文件上传、枚举和错误码映射；如果项目已有 `OpenApiSdkCodegen`、Maven 插件或 Builder，先把其中的团队规则抽取为中立配置，不把单项目逻辑写死为技能默认行为。
3. 选择模式：按输入源选择 `JAVA_CLASSPATH`、`JAVA_SOURCE`、`OPENAPI_V2`、`OPENAPI_V3` 或 `MIXED`。
4. 准备生成入口：Java 项目已有 Maven 插件、Builder、LoongCodeGenerator、`OpenApiSdkCodegen` 或历史 SDK 产物时，先把它作为基准生成入口，并输出配置抽取表；标准 OpenAPI 3 输入且没有团队生成器时，使用 `scripts/generate_sdk.py`；只有 Spring Controller 源码时，先用 `scripts/spring_source_to_openapi.py` 生成 OpenAPI 草案，再交给内置生成器。
5. 执行生成：用户明确要求生成时，实际运行生成命令并处理 JDK、classpath、依赖、模块开放、输出目录等环境问题；需要写入或清理外部目录时先确认。
6. 审查结果：检查生成 SDK 的路径、方法、参数、请求体、响应体、必填、可空、枚举、泛型、统一响应、目标运行时和命名。
7. 给出交付建议：说明已生成文件、验证命令、人工检查点、契约漂移风险、是否需要接入 CI 或 codegen-server。

## 红线

- 不得把 SDK 生成成功视为接口契约正确性的证明。
- 不得在用户明确要求生成时只输出方案、清单或建议；除非缺少必要授权或环境条件，应实际生成可用代码或可运行生成入口。
- 不得在未对标项目已有生成器或历史产物时，宣称内置生成器可以替代 `OpenApiSdkCodegen`、Maven 插件或团队 Builder。
- 不得把内置源码导出或 OpenAPI 生成的草案 SDK，包装成与团队生成器等价的生产 SDK。
- 不得把 Spring 源码导出的 OpenAPI 草案包装成发布契约；涉及生产 SDK 时必须标记常量、泛型、继承、隐藏字段和运行时路由的解析风险。
- 不得在 OpenAPI `required`、`nullable`、`oneOf/allOf/anyOf` 不明确时自行猜测。
- 不得忽略统一响应、分页、错误码、泛型解包、文件上传和媒体类型策略。
- 不得生成后跳过人工审查、调用方编译和关键接口联调验证。
- 不得把源码 AST 解析结果直接视为真实运行时契约；高风险场景应结合编译产物或 OpenAPI 契约校验。
- 不得在未确认目标 Provider 的情况下默认生成所有 SDK。
- 不得在未确认目标 JDK 的情况下生成 Java SDK；Java 8、Java 11、Java 17+ 的语言特性、依赖和 Validation 注解命名空间必须明确。
- 不得默认上传生成结果到 codegen-server 或调用外部服务。
- 不得把密钥、内部仓库凭证、token、生产接口地址写入配置、日志或生成代码。
- 不得直接覆盖调用方已改造过的 SDK 目录，除非用户明确确认。
- 不得扫描整个业务根包或默认清理输出目录；扫描范围和删除策略必须可解释、可确认、可回滚。
- 不得复制 common-codegen 仓库源码或模板到技能中；技能只沉淀流程、配置、审查方法和必要引用。
