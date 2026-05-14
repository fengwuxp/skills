# common-codegen / Loong Codegen 概览

本文用于理解 `https://github.com/fengwuxp/common-codegen` 的代码生成能力边界。该仓库适合作为 API SDK 代码生成的核心参考实现，但技能不复制仓库源码和模板。

## 1. 核心定位

common-codegen 的核心目标是：

```text
Java Controller / Swagger 注解 / OpenAPI 契约
-> 统一接口元数据
-> 多语言类型模型
-> Freemarker 模板
-> API SDK / Client 代码
```

它不是 DDL 到后端 CRUD Service 生成器，而是接口契约到客户端 SDK 的生成平台。

## 2. 模块边界

| 模块 | 责任 |
| --- | --- |
| `core` | 顶层接口、解析器、匹配器、事件、配置、工具类；核心入口是 `CodeGenerator#generate()`。 |
| `model` | 统一中间模型，例如类、字段、方法、注解、枚举、语言描述和扩展 schema。 |
| `annotation-meta` | Spring、Swagger、Validation、Jackson 等注解转换为代码生成元数据。 |
| `language-annotations` | 面向 Retrofit 等客户端库的注解转换。 |
| `languages` | Java、TypeScript、Dart 类型解析、字段/方法解析、后处理、注释增强。 |
| `swagger2-codegen` | Swagger2 / Springfox 注解解析和生成器 Builder。 |
| `swagger3-codegen` | OpenAPI3 / Swagger3 注解解析和生成器 Builder。 |
| `template` | Freemarker 模板加载。 |
| `code-formatter` | Java、TypeScript、Dart 代码格式化适配。 |
| `loong-codegen` | 聚合生成能力、模板策略、包名映射、统一响应处理、SDK 上传。 |
| `loong-codegen-starter` | 约定式入口 `LoongCodeGenerator`，按 Swagger2/3 和 Provider 创建生成器。 |
| `loong-maven-plugin` | Maven 插件，goal 为 `api-sdk-codegen`。 |
| `loong-quick` | codegen-server、npm client、client maven plugin 等平台化能力。 |
| `examples` | Swagger2/3 到 TypeScript、Dart、Java Client 的示例和断言结果。 |

## 3. 当前主链路

当前稳定主链路偏向 `JAVA_CLASSPATH`：

```text
Maven/Gradle classpath
-> 扫描 Controller 包
-> 读取 Class<?> / Method / Field / Parameter / Annotation
-> 解析 CommonCodeGenClassMeta / MethodMeta / FieldMeta
-> matcher 过滤和注解转换
-> typeMappings / customJavaTypeMapping 映射目标语言类型
-> postProcessor 调整方法、注解、响应包装、枚举和模板标签
-> packageMapStrategy 转换包名、文件路径和 Client 名称
-> 目标语言类型映射
-> Client Provider 模板输出
```

源码能力目前主要用于注释增强，例如从 Javadoc 补充类、字段、方法和参数说明；尚不是完整源码 AST 生成主链路。

标准 OpenAPI 文档输入已有方向和空壳，例如 `OpenApiSchemaCodeGenerator`，但不应假定当前仓库已经完整支持 OpenAPI JSON/YAML 到 SDK 的全链路生成。

## 4. 核心入口

常见入口：

- `com.wuxp.codegen.core.CodeGenerator#generate()`：顶层生成接口。
- `com.wuxp.codegen.starter.LoongCodeGenerator`：约定式生成入口，支持设置 `scanPackages`、`openApiType`、`outputPath`、`clientProviderTypes`。
- `Swagger2Feign*CodegenBuilder` / `Swagger3Feign*CodegenBuilder`：按 Swagger 版本和目标语言创建生成器。
- `wuxp-codegen-loong-maven-plugin`：Maven 插件，goal 为 `api-sdk-codegen`。

## 4.1 核心设计层次

common-codegen 的关键设计不是“直接从接口渲染文件”，而是分成稳定的中间层：

| 层次 | 关键类 / 概念 | 作用 |
| --- | --- | --- |
| 输入扫描 | `LoongClassCodeGenerator`、Spring `ClassPathScanningCandidateComponentProvider` | 从 classpath 扫描 `@Controller` / `@RestController`，并应用忽略包、忽略类、显式包含类。 |
| 统一元数据 | `CommonCodeGenClassMeta`、`CommonCodeGenMethodMeta`、`CommonCodeGenFiledMeta` | 把类、方法、字段、枚举、泛型、注解、依赖、注释统一描述。 |
| 匹配过滤 | `JavaClassElementMatcher`、`JavaMethodMatcher`、`JavaFieldMatcher`、Swagger matcher、`@Hidden` matcher | 决定哪些类、方法、字段、参数参与生成。 |
| 类型映射 | `MappingJavaTypeDefinitionParser`、`MappingTypescriptTypeDefinitionParser`、`JavaTypeMapper` | 将 Java 类型映射为目标语言类型，支持基础映射和一个 Java 类型展开为多个类型。 |
| 后处理 | `RemoveClientResponseTypePostProcessor`、`HttpRequestDestinationPostProcessor`、`EnumDefinitionPostProcessor`、`TypeScriptMethodDefinitionPostProcessor` | 解包统一响应、补 HTTP 目标注释、处理枚举、调整 TS 方法形态。 |
| 包名映射 | `JavaPackageMapStrategy`、`TypescriptPackageMapStrategy`、`AbstractPackageMapStrategy` | 根据 packageMap、classNameTransformers 和文件后缀生成目标包名、目录和 Client 名称。 |
| 模板输出 | `LoongSimpleTemplateStrategy`、`FreemarkerTemplateLoader`、`clients/<provider>/*.ftl` | 根据 provider 选择 Freemarker 模板生成文件，再执行格式化。 |
| 事件扩展 | `CodeGenEventListener`、`TypeScriptIndexGenEventListener` | 生成完成后补充 index/export 或其他聚合文件。 |

因此，替代或对齐 common-codegen 时，应优先对齐“中间元数据 + 映射/后处理/模板风格”，而不是只让 OpenAPI 直接生成一批文件。

## 4.2 Retrofit / Loong 风格要点

从 `clients/retrofit/*.ftl` 和 Builder 默认行为看，Loong 风格 Java Retrofit SDK 有这些关键特征：

- Client 模板导入 `retrofit2.http.*`，方法返回值通常是解包后的裸类型，不是 `retrofit2.Call<T>`。
- `RemoveClientResponseTypePostProcessor` 通过移除统一响应类型实现返回值解包。
- Query 类如果名称以 `Query` 结尾，走专门模板，可通过 `queryObjectShareClassName` 继承共享 QueryMap 父类，并通过 `queryObjectShareDependencies` 注入 import。
- 分页和 QueryMap 通常通过类型映射复用团队运行时类，例如 `ImmutablePagination<T>` 和 `AbstractPageQueryMap`，而不是生成 `PaginationOfXxx`。
- `JavaPackageMapStrategy` 会把 Controller 转换为 Client，并支持 `fileNamSuffix`、base package、Ant 风格 packageMap 和 classNameTransformers。
- 生成器会递归生成依赖类型，并过滤重复字段、无效依赖和不需要 import 的依赖。
- classpath 模式能解析静态常量、注解真实值和完整 Java package；源码/标准 OpenAPI 模式若要对齐 Loong，必须额外保存 `x-java-package`、Query 对象标记、类型映射和忽略规则。

这些特征如果未对齐，只能称为“草案生成”，不能称为替代 `OpenApiSdkCodegen` 或 Loong Builder。

## 5. 关键配置

| 配置 | 含义 |
| --- | --- |
| `scanPackages` | 要扫描的 Controller 包，支持类似 Spring 包扫描/Ant 风格。 |
| `openApiType` | 当前用于区分 Swagger2、Swagger3 或默认类型；注意它不是标准 OpenAPI 文档输入类型。 |
| `clientProviderTypes` | 生成的客户端类型，例如 `AXIOS`、`UMI_REQUEST`、`SPRING_CLOUD_OPENFEIGN`。 |
| `outputPath` | 生成代码输出目录。 |
| `typeMappings` | Java 类型到目标语言类型的基础映射，例如文件、Promise、统一响应。 |
| `customJavaTypeMapping` | 一个 Java 类型展开为多个类型，例如统一响应 + 分页。 |
| `packageMapStrategy` | Java 包名到目标语言目录/包名的映射策略。 |
| `ignorePackages` / `ignoreClasses` | 忽略不参与生成的包或类。 |
| `ignoreMethodNames` / `ignoreFieldNames` | 忽略不参与生成的方法或字段。 |
| `enableFieldUnderlineStyle` | 字段下划线风格映射。 |
| `ignoreEnumField` | 忽略枚举常量字段定义。 |

## 6. Maven 插件接入

最小接入：

```xml
<build>
    <plugins>
        <plugin>
            <groupId>com.wuxp.codegen</groupId>
            <artifactId>wuxp-codegen-loong-maven-plugin</artifactId>
            <version>${project.version}</version>
        </plugin>
    </plugins>
</build>
```

常用配置：

```xml
<configuration>
    <skip>false</skip>
    <scanPackages>
        <scanPackage>com.example.**.controller</scanPackage>
    </scanPackages>
    <openApiType>SWAGGER_3</openApiType>
    <clientProviderTypes>spring_cloud_openfeign,typescript_feign</clientProviderTypes>
    <outputPath>${project.build.directory}/generated-sdk</outputPath>
</configuration>
```

定制生成器：

```xml
<configuration>
    <pluginCodeGeneratorClass>com.example.codegen.CustomSdkCodeGenerator</pluginCodeGeneratorClass>
</configuration>
```

`pluginCodeGeneratorClass` 优先级高于 `codeGeneratorClass`，适合需要自定义包名映射、统一响应解包、Provider 组合或上传策略的项目。

## 7. 适用场景

- Java/Spring 服务端接口需要生成前端 TypeScript SDK。
- Java 微服务之间希望生成 OpenFeign、Spring HTTP 或 Retrofit Client。
- Flutter/Dart 客户端需要生成 Dart Feign SDK。
- 需要统一处理枚举、分页、统一响应、文件上传、Validation 注释和 Swagger/OpenAPI 注释。
- 需要把接口变更沉淀为可审查、可重复生成的 SDK 资产。

## 8. 不适用场景

- 用户只需要根据数据库表生成后端 Service、Mapper、Entity。
- 项目接口契约尚不稳定，路径、参数、响应体还未确认。
- 目标调用方已经有深度手写 SDK，不能接受目录覆盖。
- 依赖无法解析、项目无法编译，且没有源码 AST 或 OpenAPI 替代输入。
- 用户希望凭自然语言描述直接生成生产 SDK。
