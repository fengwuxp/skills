# SDK 生成配置能力

本文用于设计、审查和解释 API SDK 生成配置。配置目标是让使用者能够明确控制扫描范围、生成目标、输出目录、契约映射和执行风险，而不是依赖不可审查的默认值。

## 1. 配置原则

- **显式配置优先**：用户明确给出的 `scanPackages`、Provider、输出目录、忽略规则优先于技能推断。
- **项目规则优先**：已有项目生成器、Maven/Gradle 插件、Builder、脚本或历史 SDK 产物时，先抽取并对标其中的 profile、包名映射、类型映射、过滤规则和模板风格；内置生成器不得默认宣称等价替代。
- **内置生成兜底**：标准 OpenAPI 3 输入可使用技能自带 `scripts/generate_sdk.py` 生成基础 SDK，避免在没有项目生成入口时完全不可用。
- **生成动作优先**：用户明确要求“生成”时，配置不是最终交付物；必须实际执行生成，或创建可运行的生成入口并完成一次验证。
- **可推断但要说明**：可以根据项目结构推断 Controller 包、OpenAPI 版本、输出目录建议，但必须在输出中标明“推断来源”和“待确认项”。
- **生成目录可回收**：输出目录应指向可删除、可重建的生成目录；手写扩展代码必须和生成代码分离。
- **风险动作要确认**：清理输出目录、覆盖已有 SDK、上传到 codegen-server、暴露内部接口、生成敏感接口前必须确认。
- **配置可复用**：同一项目应沉淀为 Maven 插件、Builder、项目内 codegen 类或团队配置模板，避免每次靠口头参数重新拼装。

## 2. 最小配置闭环

生产级生成前至少确认这些配置：

| 类别 | 必填项 | 说明 |
| --- | --- | --- |
| 输入源 | `sourceType` | `JAVA_CLASSPATH`、`JAVA_SOURCE`、`OPENAPI_V2`、`OPENAPI_V3` 或 `MIXED`。 |
| 扫描范围 | `scanPackages` / `openapi.pathOrUrl` | Java 模式需要 Controller 包；OpenAPI 模式需要文档路径或 URL。 |
| 生成目标 | `providers` | 例如 `RETROFIT`、`TYPESCRIPT_FEIGN_FUNC`、`AXIOS`。 |
| 运行时 | `javaRuntime` / `typescriptRuntime` | Java SDK 必须确认目标 JDK、Spring/Boot 代际和 Validation 命名空间。 |
| 输出位置 | `outputPath` | 必须确认是否允许覆盖或清理。 |
| 契约策略 | `responseWrapper`、`pagination`、`typeMappings` | 统一响应、分页、文件、枚举、日期、金额、ID 等映射策略。 |
| 项目生成器规则 | `packageMap`、`typeMappings`、`sharedVariables`、`postProcessors`、`ignoreRules` | 从 `OpenApiSdkCodegen`、Builder、Maven 插件或历史产物中抽取，不能硬编码在技能逻辑里。 |
| 暴露边界 | `include/exclude` | 排除内部 Controller、测试接口、后台接口和敏感接口。 |
| 验证方式 | `verifyCommands` | 生成后的编译、类型检查、lint、契约 diff 或关键接口联调。 |

如果缺少 `scanPackages`、`providers`、`outputPath` 或覆盖策略，不应直接执行生成；应先给出建议配置并等待确认。

## 3. 生成执行策略

当用户说“生成 SDK”“跑一下生成”“对这个模块生成代码”时，应按以下顺序执行：

1. 查找现有入口：Maven 插件、Gradle task、`main` 方法、项目内 `Codegen` 类、脚本、CI 命令或历史 SDK 产物。
2. 复用现有入口：项目已有入口优先作为基准，因为它通常沉淀了团队的包名映射、类型映射、忽略规则、profile 和输出目录。
3. 对标项目规则：读取生成配置，至少记录扫描范围、profile、provider、包名映射、类型映射、统一响应解包、分页、QueryMap、忽略类/方法/字段和输出路径。
4. 判断是否存在标准 OpenAPI 3 文档；如果存在且没有项目生成入口，可使用内置生成器 `scripts/generate_sdk.py` 生成基础 SDK。
5. 判断是否只有 Spring Controller 源码；如果没有 OpenAPI 文档，可用 `scripts/spring_source_to_openapi.py` 导出 OpenAPI 3 草案，再交给内置生成器生成，但必须标记为草案。
6. 补齐缺失入口：没有标准 OpenAPI 文档也没有入口时，基于项目技术栈创建最小可运行生成入口或脚本；生成入口应靠近测试源码、工具模块或专用 codegen 模块。
7. 执行生成命令：实际运行 Python 内置生成器、源码导出器、Maven、Gradle、脚本或 Builder。涉及外部目录写入、清理输出目录、下载依赖或上传远程服务时，先取得用户确认。
8. 处理环境问题：确认 Python、JDK、Maven/Gradle、classpath、`MAVEN_OPTS`、`--add-opens`、网络仓库、依赖版本和模块编译参数。
9. 生成后审查：检查文件数量、目标目录、关键接口、Provider 注解、统一响应、分页、Validation、目标 JDK、敏感接口和 profile 边界。
10. 汇报结果：明确说明“实际生成由哪个入口执行”“是否对标项目生成器”“输出到哪里”“运行了什么命令”“哪些验证通过”“哪些风险待确认”。

执行角色边界：

- 技能负责把输入契约转成实际 SDK 产物，不能只做咨询。
- 项目已有 `OpenApiSdkCodegen`、Maven 插件或 Builder 是生产基准适配器；技能负责选择、配置、运行、对标和审查这些适配器。
- 内置 `scripts/generate_sdk.py` 是标准 OpenAPI 的基础执行引擎，不依赖 Java 环境，但不自动等价于团队生成器。
- 内置 `scripts/spring_source_to_openapi.py` 是 Spring 源码输入的草案导出器，用于没有标准 OpenAPI 文档时建立生成链路；其结果必须按源码 AST 风险审查。
- 如果内置生成器与项目基准产物不一致，必须报告差异，不得把“能生成”说成“可替代”。
- 如果内置生成器或项目生成器能力不足，技能应指出缺口，并优先补生成入口或配置；无法补齐时才降级为方案输出。

### 项目生成器配置抽取项

已有 `OpenApiSdkCodegen`、Maven 插件、Builder 或历史 SDK 产物时，应先把项目生成器里沉淀的团队规则抽取成中立配置。抽取目标不是复制某个类，而是识别哪些行为必须可配置、可复用、可对标。

| 配置域 | 必须抽取的内容 | 为什么重要 |
| --- | --- | --- |
| 生成入口 | 入口类、命令、模块路径、运行 JDK、必要 `MAVEN_OPTS`、是否需要测试 classpath | 决定生成是否能复现，也能区分生成器运行环境和 SDK 目标运行时。 |
| SDK profile | profile 名称、扫描包、输出目录、include/exclude 类、差异化忽略方法 | 同一服务常生成 enterprise、personal、partner、internal 等不同 SDK，不能合并成单一输出。 |
| Provider 与模板风格 | 目标语言、Client Provider、是否 Retrofit/OpenFeign/TS Feign、返回值是否裸类型、是否生成 `Call<T>` | 直接影响调用方 API 形态；模板风格不一致就是不兼容。 |
| 包名/目录映射 | Controller、DTO、Request、Query、Enum、Core、三方类型的 packageMap / directoryMap | 决定生成文件组织、import、调用方兼容性和升级成本。 |
| 类型映射 | 文件、统一响应、分页、Query 对象、排序、枚举、金额、日期、ID、Void 等映射 | 决定 SDK 类型是否符合团队运行时和业务约定。 |
| 统一响应处理 | 是否使用 postProcessor 解包响应、保留哪些错误字段、成功响应返回类型 | 影响所有接口签名和错误处理边界。 |
| Query 对象策略 | `@QueryMap`、查询对象父类、sharedVariables、query 参数是否展开 | 影响查询接口签名和分页/排序能力。 |
| 分页策略 | 源分页类型、目标分页类型、items/records/total 字段、是否使用共享分页类 | 影响列表接口返回值和兼容性。 |
| 忽略规则 | 忽略类、方法、字段、枚举字段、废弃接口、敏感接口及原因 | 决定暴露边界；不能仅靠扫描包隐式控制。 |
| 命名策略 | Client 后缀、Controller 到 Client 的转换、operationId/方法名、冲突处理 | 决定调用方 API 稳定性。 |
| 输出策略 | 是否删除输出目录、是否备份、是否 dry-run、是否生成 index/export | 影响安全性和可回滚性。 |
| 对标策略 | 文件数量、Client 列表、方法签名、返回类型、包结构、编译命令 | 用于判断新生成器是草案、可迁移还是可替代。 |

抽取流程建议：

1. 读取或运行现有生成入口，记录真实输出目录和 profile。
2. 从 Builder/Maven 配置中提取扫描范围、Provider、packageMap、typeMappings、postProcessors、sharedVariables、ignore rules 和清理策略。
3. 从历史 SDK 产物反推模板风格，例如 Client 包结构、返回值是否裸类型、查询参数是否 `@QueryMap`、分页类型是否复用共享类。
4. 把项目专用类名保留在配置中，把生成能力表达为中立字段，例如 `response_unwrap_strategy`、`query_object_strategy`、`pagination_strategy`。
5. 生成迁移版本后，按 profile 对比文件数量、Client 列表、方法签名、关键类型、包结构和编译结果。
6. 只有对标差异可解释且调用方兼容时，才能说“可替代”；否则只能说“可作为草案生成器”或“需要补齐适配器”。

源码输入模式下，配置还必须说明 `source_roots` 是否覆盖了常量、DTO、Query、Enum 和 core 类型所在模块。仅扫描 Controller 模块通常会导致 Header 常量、Query 字段、枚举值、分页类型和包映射失真。

### 内置生成器命令

OpenAPI 3 -> Java Retrofit：

```bash
python3 api-sdk-codegen-expert/scripts/generate_sdk.py \
  --input ./openapi.json \
  --output ./generated-sdk/java \
  --language java \
  --provider retrofit \
  --base-package com.example.api \
  --target-jdk 8 \
  --validation-namespace javax.validation \
  --clean
```

OpenAPI 3 -> TypeScript fetch：

```bash
python3 api-sdk-codegen-expert/scripts/generate_sdk.py \
  --input ./openapi.json \
  --output ./generated-sdk/typescript \
  --language typescript \
  --provider typescript-fetch \
  --package-name example-api \
  --clean
```

Spring Controller 源码 -> OpenAPI 3 草案：

```bash
python3 api-sdk-codegen-expert/scripts/spring_source_to_openapi.py \
  --source-root ./src/main/java \
  --source-root ../domain/src/main/java \
  --controller-package com.example.web.openapi.controller \
  --output ./generated-contract/openapi-source-draft.json \
  --title "Source Generated API" \
  --version 0.1.0
```

能力边界：

- 支持 OpenAPI 3.x JSON；YAML 需要本地 Python 环境安装 PyYAML。
- Java 输出当前覆盖 Retrofit interface、POJO model、enum、path/query/header/body 参数、`javax.validation` / `jakarta.validation` 基础必填注解。
- TypeScript 输出当前覆盖 fetch 函数、interface/type、path/query/header/body 参数。
- Spring 源码导出当前覆盖常见 Spring MVC Controller、Mapping 注解、路径常量、请求头、路径参数、请求体、无注解 query object、Swagger `@Operation/@Schema`、Validation 必填和基础隐藏字段。
- Spring 源码导出不是 Java 编译器，复杂泛型、父类继承字段、运行时路由、条件装配、Lombok 生成结构、复杂 Jackson/Fastjson 规则必须作为待审查风险。
- 暂不完整支持复杂 `oneOf/anyOf/discriminator`、外部 `$ref`、复杂 multipart、OAuth 客户端、SDK 工程文件和运行时错误处理框架。
- 内置生成器输出后仍必须按 `generated-sdk-review-checklist.md` 审查。

## 4. 推荐配置模型

下面是给 AI、团队评审和项目 codegen 类使用的中立配置模板，不要求与 common-codegen 原生参数一一对应：

```yaml
sdk_codegen:
  generator_baseline:
    name: OpenApiSdkCodegen
    kind: project_builder
    entrypoint: com.example.sdk.codegen.OpenApiSdkCodegen
    module_path: /path/to/openapi-module
    command: mvn -DskipTests test-compile exec:java -Dexec.mainClass=com.example.sdk.codegen.OpenApiSdkCodegen
    runtime_jdk: 21
    compatibility_target: loong_wind_retrofit
    compare_outputs:
      file_count_by_profile: true
      client_method_signature: true
      package_layout: true
      compile_generated_sdk: true

  source:
    source_type: JAVA_CLASSPATH
    module_path: /path/to/service-module
    source_roots:
      - src/main/java
    scan_packages:
      - com.example.openapi.controller.**
    openapi:
      version:
      path_or_url:
    build:
      tool: maven
      command: mvn -DskipTests test-compile

  profiles:
    - name: enterprise
      scan_packages:
        - com.example.openapi.controller.**
      exclude_classes:
        - com.example.openapi.controller.WebhookExampleController
      exclude_methods:
        com.example.openapi.controller.InternalController:
          - internalOnly
      exclude_fields:
        com.example.openapi.enums.BusinessScene:
          - internalCode
      output_targets:
        - enterprise-java
        - enterprise-typescript

    - name: personal
      scan_packages:
        - com.example.openapi.controller.vcc.**
      exclude_classes:
        - com.example.openapi.controller.wallet.TenantWalletController
      exclude_methods:
        com.example.openapi.controller.vcc.VccController:
          - internalOnlyForEnterprise
      output_targets:
        - personal-java

  targets:
    - name: enterprise-java
      profile: enterprise
      language: JAVA
      provider: RETROFIT
      template_style: loong_wind_retrofit
      return_style: bare_unwrapped
      query_object_strategy: query_map
      pagination_strategy: shared_immutable_pagination
      java_runtime:
        target_jdk: 8
        source_compatibility: 8
        validation_namespace: javax.validation
        spring_generation: spring5
        allowed_language_features:
          - class
          - interface
          - enum
        forbidden_language_features:
          - record
          - sealed
          - var
      output_path: ../sdk/enterprise-sdk/src/main/java
      base_package: com.example.api
      package_map:
        com.example.openapi.controller.**: "{0}client"
        com.example.openapi.**.request: model.request
        com.example.openapi.**.dto: model.dto
        com.example.**.query: model.query
        com.example.**.enums: model.enums
        com.example.core.**: core
      class_name_transformers:
        controller_suffix: ApiClient
        base_package: com.example.api
        client_names:
          CreateVccTask: VccTaskApiClient
          VccTransactionDetails: VccTransactionDetailsApiClient
      client_segment_map:
        TenantWallet: wallet
        UserWallet: wallet
        CreateVccTask: vcc
      shared_variables:
        queryObjectShareClassName: AbstractPageQueryMap
        queryObjectShareDependencies:
          - com.wind.client.retrofit.query.AbstractPageQueryMap
      post_processors:
        - type: remove_client_response_type
          response_meta: JAVA_API_RESPONSE
      delete_output_directory: false
      backup_before_delete: true

    - name: personal-java
      profile: personal
      language: JAVA
      provider: RETROFIT
      template_style: loong_wind_retrofit
      return_style: bare_unwrapped
      query_object_strategy: query_map
      pagination_strategy: shared_immutable_pagination
      java_runtime:
        target_jdk: 8
        source_compatibility: 8
        validation_namespace: javax.validation
        spring_generation: spring5
      output_path: ../sdk/personal-sdk/src/main/java
      base_package: com.example.api
      package_map:
        com.example.openapi.controller.vcc.**: clients.vcc
        com.example.openapi.**.request: model.request
        com.example.openapi.**.dto: model.dto
        com.example.**.query: model.query
        com.example.**.enums: model.enums
      delete_output_directory: false
      backup_before_delete: true

    - name: enterprise-typescript
      profile: enterprise
      language: TYPESCRIPT
      provider: TYPESCRIPT_FEIGN_FUNC
      template_style: typescript_feign_func
      output_path: ../sdk-ts/packages/enterprise/src
      package_map:
        com.example.openapi.controller.**: clients
        com.example.openapi.**.request: model/request
        com.example.openapi.**.dto: model/dto
      delete_output_directory: false

  contract:
    response_wrapper:
      source: com.example.ApiResp
      unwrap_success_data: true
      preserve_error_fields:
        - code
        - message
        - traceId
    pagination:
      source: com.example.Pagination
      items_field: records
      total_field: total
    type_mappings:
      java.io.File: file
      org.springframework.web.multipart.MultipartFile: file
      java.math.BigDecimal: decimal
      java.time.OffsetDateTime: datetime
      java.lang.Long: string-in-typescript
      java.lang.Void: void-wrapper
      com.example.ApiResp: api-response-wrapper
      com.example.Pagination: shared-pagination
      com.example.AbstractPageQuery: query-map
    nullability:
      java_validation_annotations: true
      java_nullability_annotations:
        enabled: false
        namespace:
      openapi_required_first: true
    enum:
      preserve_value: true
      preserve_description: true

  execution:
    dry_run_first: true
    allow_delete_output_directory: false
    diff_after_generation: true
    verify_commands:
      - mvn compile
      - npm run typecheck
```

### OpenApiSdkCodegen 抽取示例

以项目内 `OpenApiSdkCodegen` 这类 Builder 为例，至少应抽取出下面这些配置项：

```yaml
sdk_codegen:
  generator_baseline:
    name: OpenApiSdkCodegen
    kind: loong_builder
    compatibility_target: loong_wind_retrofit

  profiles:
    - name: enterprise
      scan_packages:
        - com.capte.nobe.web.openapi.controller.**
      exclude_classes:
        - WebhookExampleController
        - LanguageCode
        - DefaultPageQueryOptions
      exclude_methods:
        VccController:
          - allocateVccToSubUsers
        UserWalletController:
          - queryWalletDetailsDeprecated
          - queryFundsTransactionsDeprecated

    - name: personal
      scan_packages:
        - com.capte.nobe.web.openapi.controller.vcc.**
      exclude_classes:
        - TenantWalletController
        - UserWalletController
        - WebhookExampleController
        - LanguageCode
      exclude_methods:
        VccController:
          - freezeVcc
          - unfreezeVcc
          - withdrawVcc
          - deleteVcc
          - shareVccAdjustLimit
          - queryShareVccLimit
        VccBinController:
          - queryTenantAvailableVccBins
        VccTransactionDetailsController:
          - queryVccTransactionDetailsFinishedLogs

  targets:
    - name: java-retrofit
      language: JAVA
      provider: RETROFIT
      template_style: loong_wind_retrofit
      base_package: com.capte.nobe.api
      return_style: bare_unwrapped
      query_object_strategy: query_map
      pagination_strategy: wind_immutable_pagination
      shared_pagination_type: ImmutablePagination
      shared_pagination_import: com.wind.common.query.supports.ImmutablePagination
      java_runtime:
        target_jdk: 8
        validation_namespace: javax.validation
      package_map:
        com.capte.nobe.web.openapi.controller: com.capte.nobe.api.clients
        com.capte.nobe.**.model.dto: com.capte.nobe.api.model.dto
        com.capte.nobe.**.model.query: com.capte.nobe.api.model.query
        com.capte.nobe.**.model.request: com.capte.nobe.api.model.request
        com.capte.nobe.**.model.enums: com.capte.nobe.api.model.enums
        com.capte.nobe.**.enums: com.capte.nobe.api.model.enums
        com.capte.nobe.core.enums: com.capte.nobe.api.enums
        com.wind.**: com.capte.nobe.api.wind
        com.capte.vcc.**: com.capte.nobe.api.core.vcc
        com.capte.transaction.core.**: com.capte.nobe.api.core.transaction
        com.capte.nobe.core.**: com.capte.nobe.api.core
        com.capte.vcc.sdk.**: com.capte.nobe.api.core.sdk
        com.capte.nobe.sdk.**: com.capte.nobe.api.core.sdk
      type_mappings:
        MultipartFile: FILE
        Void: VOID_WRAPPER
        ApiResp: JAVA_API_RESPONSE
        Pagination: JAVA_PAGINATION
        AbstractPageQuery: JAVA_ABSTRACT_PAGE_QUERY_MAP
        DefaultOrderField: JAVA_DEFAULT_ORDER_FIELD
        QueryOrderType: JAVA_QUERY_ORDER_TYPE
        QueryType: JAVA_QUERY_TYPE
      shared_variables:
        queryObjectShareClassName: AbstractPageQueryMap
        queryObjectShareDependencies:
          - com.wind.client.retrofit.query.AbstractPageQueryMap
      # 源码模式或内置生成器可使用这些中立字段表达项目忽略规则；
      # Loong Builder 中对应 ignoreClasses / ignoreMethodNames / matcher。
      class_name_transformers:
        controller_suffix: ApiClient
        client_names:
          Create VCC Task: VccTaskApiClient
          Vcc Transaction: VccTransactionDetailsApiClient
      client_segment_map:
        Create VCC Task: vcc
        TenantWallet: wallet
        UserWallet: wallet
      exclude_tags:
        - WebHook Example
      exclude_operation_ids:
        - allocateVccToSubUsers
      ignore_parameter_schema_names:
        - DefaultPageQueryOptions
      ignore_schema_names:
        - DefaultPageQueryOptions
        - OpenApiWebhookRequest
      post_processors:
        - RemoveClientResponseTypePostProcessor: JAVA_API_RESPONSE
      ignore_fields:
        VccTransactionBusinessScene:
          - code
          - category
          - formatPattern
          - positive
          - BANK_SIDE_SCENES
          - FEE_REFUND_CASHBACK_SCENES

    - name: typescript-feign-func
      language: TYPESCRIPT
      provider: TYPESCRIPT_FEIGN_FUNC
      template_style: typescript_feign_func
      package_map:
        com.capte.nobe.web.openapi.controller: clients
        com.capte.nobe.**.model: model
        com.capte.transaction.**: model.transaction
        com.capte.nobe.core.**: model.core
        com.capte.vcc.sdk.**: model.sdk
        com.capte.nobe.**.enums: model.enums
      type_mappings:
        ApiResp: TS_API_RESPONSE
        Pagination: TS_PAGINATION
        AbstractPageQuery: TS_ABSTRACT_PAGE_QUERY
        DefaultOrderField: TS_DEFAULT_ORDER_FIELD
        QueryOrderType: TS_QUERY_ORDER_TYPE
        QueryType: TS_QUERY_TYPE
```

该示例中的类名可以替换为其他项目自己的类型；真正必须保留的是配置维度：多 profile、模板风格、包映射、类型映射、响应解包、QueryMap、分页共享类型、忽略规则和输出策略。

## 5. 参数说明

### 输入与扫描

- `source_type`：决定使用编译产物、源码 AST、标准 OpenAPI 还是混合模式。
- `module_path`：生成命令执行目录；多模块项目应指向 API 所在模块或聚合构建根目录。
- `scan_packages`：只扫描公开 API Controller 包，不扫描 `com.example.**` 这类过宽根包。
- `source_roots`：源码 AST 模式下用于定位 Controller、DTO、Enum、常量和注释。
- `openapi.path_or_url`：标准 OpenAPI 模式下的文档来源；URL 需要说明环境、版本和时间。

### Profile 与暴露边界

- `profiles` 用于同一服务生成不同 SDK，例如 enterprise、personal、partner、internal-test。
- 每个 profile 可以有独立 `scan_packages`、`exclude_classes`、`exclude_methods`、`exclude_fields`。
- 忽略规则应该写明原因：内部接口、历史废弃、权限不允许、敏感字段、调用方不需要。
- 对敏感接口不要只靠忽略规则兜底，还应要求服务端权限、审计和文档标识一致。

### 生成目标

- `targets` 可以一对多，同一 profile 可生成 Java、TypeScript、Dart 等多个 SDK。
- `provider` 必须来自调用方技术栈，不因为生成器支持就全部生成。
- `output_path` 应优先使用 `target/generated-sdk`、`build/generated-sdk` 或独立 SDK 包中的生成代码目录。
- `base_package` 和 `package_map` 控制包名、目录和导出结构；变更会影响调用方兼容性。
- `delete_output_directory` 默认建议为 `false`。如果必须开启，应同时确认输出目录完全由生成器管理。

### Java 目标运行时

生成 Java SDK 时必须确认 `java_runtime`，不能把生成器运行所用 JDK 当成 SDK 目标 JDK。常见差异：

| 目标 | 适用场景 | 约束 |
| --- | --- | --- |
| Java 8 | 公共 SDK、外部合作方、老 Spring Boot 2 / Android 兼容场景 | 不使用 `record`、`var`、`List.of`、`Map.of`、sealed class、pattern matching；Validation 通常使用 `javax.validation`。 |
| Java 11 | 部分企业服务基线 | 可使用 Java 11 编译目标，但仍要避免 Java 17 语法；依赖版本需确认。 |
| Java 17+ | Spring Boot 3+、Spring Framework 6+、内部新服务 | 可以使用较新语言特性；Validation 通常使用 `jakarta.validation`；Spring HTTP Interface 更适配该代际。 |

必须确认：

- `target_jdk`：SDK 调用方最低 JDK，而不是服务端 JDK。
- `source_compatibility` / `target_compatibility`：编译产物兼容级别。
- `validation_namespace`：`javax.validation` 或 `jakarta.validation`，不得混用。
- `spring_generation`：`spring5` / `spring6` / `none`，影响 Spring 注解、HTTP Interface 和依赖坐标。
- `client_dependency_versions`：OpenFeign、Retrofit、OkHttp、Spring Cloud、Jackson、Validation API 等依赖版本。
- `language_features`：是否允许 `record`、`sealed`、`var`、`List.of`、`Optional` 字段等。

Java SDK 默认建议：

- 面向外部合作方或不清楚调用方环境时，优先建议 Java 8 兼容输出，并把 Java 17+ 作为可选 profile。
- `SPRING_HTTP` 通常只建议用于 Java 17+ / Spring 6+ 调用方。
- `RETROFIT`、`OPENFEIGN`、`SPRING_CLOUD_OPENFEIGN` 需要结合依赖版本判断 Java 8/11/17 兼容性。
- 生成的 DTO 不应默认使用 `record`；除非用户明确要求 Java 17+ 且调用方接受该兼容性边界。

### 契约映射

- `response_wrapper`：说明是否解包统一响应，以及错误码、错误消息、traceId/requestId 是否保留。
- `pagination`：说明列表字段、总数字段、页码字段和目标语言分页模型。
- `type_mappings`：覆盖文件、金额、日期时间、长整型 ID、枚举、Map、泛型等高风险类型。
- `nullability`：OpenAPI `required/nullable` 优先；Java Validation 可作为补充依据。Java SDK 还要确认是否使用 JSpecify、JetBrains、Spring `@Nullable` 或只保留文档说明。
- `enum`：说明枚举名、值、描述、废弃项是否保留。

### 执行与验证

- `dry_run_first`：首次接入或迁移时建议开启，先输出配置和风险清单。
- `allow_delete_output_directory`：只有用户确认输出目录可删除时才允许为 `true`。
- `diff_after_generation`：生成后必须比较和上一版本 SDK 的差异。
- `verify_commands`：按目标语言配置编译、类型检查、lint、测试或关键接口 mock 调用。

## 6. 默认推断规则

允许推断：

- 单一 Spring API 模块中，Controller 包可从 `@RestController` / `@RequestMapping` 分布推断。
- 已有 codegen 类或 Maven 插件配置时，可复用其中的 `scanPackages`、Provider、类型映射和包名映射。
- 输出目录可以建议为 `target/generated-sdk/<provider>` 或团队现有 SDK 包的生成代码目录。
- `openApiType` 可由 Swagger2 / OpenAPI3 注解依赖推断，但要说明它不等同于标准 OpenAPI 文件版本。
- Java SDK 目标 JDK 可以从调用方项目 `maven-compiler-plugin`、`release`、`source/target`、Gradle toolchain 或已有 SDK `pom.xml` 推断，但必须标注为待确认。

不允许静默推断：

- 把服务端 JDK 或生成器运行 JDK 当成 Java SDK 目标 JDK。
- 在未确认 Java SDK 目标 JDK 时使用 Java 17+ 语法、Spring 6 API 或 `jakarta.validation`。
- 在 Java 8 目标中生成 `record`、`var`、`List.of`、`Map.of`、sealed class、pattern matching 等不兼容写法。
- 覆盖或删除已有 SDK 目录。
- 把内部 Controller、后台接口、测试接口纳入公开 SDK。
- 将敏感接口或敏感字段暴露给外部合作方。
- 将生产域名、token、密钥、内部网关地址写入 SDK。
- 在缺少 `required/nullable` 证据时自行决定字段必填和可空。

## 7. 输出格式建议

当用户要求“给出配置”或“审查配置”时，建议输出：

```text
结论：可执行 / 有条件可执行 / 暂不建议执行

配置摘要：
- 输入源：
- 扫描范围：
- SDK profile：
- 目标 Provider：
- 目标运行时：
- 输出目录：
- 覆盖策略：

待确认项：
- ...

风险与红线：
- ...

建议配置：
- Maven 插件 / Builder / 项目 codegen 类片段

验证命令：
- ...
```

当用户要求“生成”时，建议输出：

```text
结论：生成成功 / 生成失败 / 有条件生成成功

实际执行：
- 生成入口：
- 执行命令：
- 运行 JDK / Node / Dart：
- 输出目录：

生成结果：
- 文件数量：
- SDK profile：
- 关键 Client：

生成后检查：
- 路径/方法：
- 参数：
- 响应/分页：
- 目标运行时：
- 敏感接口：

待确认风险：
- ...
```

## 8. 结合真实模块时的检查点

对于类似 `nobe/web/openapi` 这类 Java 编译产物生成 SDK 的模块，重点检查：

- 生成入口是否位于测试源码或专用 codegen 模块，避免混入生产启动逻辑。
- `scanPackages` 是否区分 enterprise、personal、partner 等 profile。
- 输出目录是否位于相邻 SDK 仓库或模块，清理前必须确认目录完全由生成器管理。
- 统一响应解包后，错误码、错误消息、traceId/requestId 是否仍有调用方可用的处理方式。
- 多路径映射、Header 常量、查询对象、分页对象、敏感接口和忽略规则是否生成后专项验证。
- Java SDK 输出是否明确目标 JDK、Validation 命名空间、Spring/Boot 代际和依赖版本；外部 SDK 不默认升级到 Java 17+。
