# 接入配方

本文用于给出 common-codegen / Loong Codegen 的接入建议。输出配置前应先完成输入源识别和 Provider 选择。

如果用户需要“可配置能力”或项目级生成方案，应先读取 `generation-configuration.md`，明确扫描范围、目标 Provider、输出目录、覆盖策略、类型映射和验证命令，再选择 Maven 插件、LoongCodeGenerator 或 Builder 接入方式。

## 1. Maven 插件最小接入

```xml
<build>
    <plugins>
        <plugin>
            <groupId>com.wuxp.codegen</groupId>
            <artifactId>wuxp-codegen-loong-maven-plugin</artifactId>
            <version>${project.version}</version>
            <configuration>
                <skip>false</skip>
                <scanPackages>
                    <scanPackage>com.example.**.controller</scanPackage>
                </scanPackages>
                <openApiType>SWAGGER_3</openApiType>
                <clientProviderTypes>typescript_feign,axios</clientProviderTypes>
                <outputPath>${project.build.directory}/generated-sdk</outputPath>
            </configuration>
        </plugin>
    </plugins>
</build>
```

注意：

- `openApiType` 在当前 common-codegen 中主要表示 Swagger 注解版本，不等同于标准 OpenAPI JSON/YAML 输入。
- `scanPackages` 应尽量指向 Controller 包，不要扫描整个根包。
- `outputPath` 应指向可清理的生成目录，避免覆盖手写代码。
- `clientProviderTypes` 用逗号分隔，值会转为大写后匹配 `ClientProviderType`。

## 2. LoongCodeGenerator 简化接入

适合按约定快速生成：

```java
LoongCodeGenerator generator = new LoongCodeGenerator("com.example.**.controller");
generator.setOutputPath("target/generated-sdk");
generator.setClientProviderTypes(List.of(ClientProviderType.TYPESCRIPT_FEIGN, ClientProviderType.AXIOS));
generator.generate();
```

适合场景：

- 项目接口结构简单。
- 包名映射使用默认约定即可。
- 统一响应、分页、类型映射没有复杂定制。

## 3. Builder 定制接入

适合需要自定义类型映射、包名映射、统一响应解包或输出结构：

```java
Map<String, String> packageMap = new LinkedHashMap<>();
packageMap.put("com.example.**.controller", "{0}services");
packageMap.put("com.example.**.request", "req");
packageMap.put("com.example.**.response", "resp");
packageMap.put("com.example.**.enums", "enums");

Swagger3FeignTypescriptCodegenBuilder.builder(true)
        .languageDescription(LanguageDescription.TYPESCRIPT)
        .clientProviderType(ClientProviderType.TYPESCRIPT_FEIGN)
        .typeMappings(ServiceResponse.class, TypescriptClassMeta.PROMISE)
        .customJavaTypeMapping(ServicePageResponse.class, new Class<?>[]{ServiceResponse.class, PageInfo.class})
        .packageMapStrategy(new TypescriptPackageMapStrategy(packageMap, Collections.emptyMap()))
        .outPath("target/generated-sdk/typescript")
        .scanPackages(new String[]{"com.example.**.controller"})
        .isDeletedOutputDirectory(true)
        .buildCodeGenerator()
        .generate();
```

定制点：

- `typeMappings`：基础类型映射，例如文件类型、Promise、统一响应。
- `customJavaTypeMapping`：把一个包装类型展开为多个类型，例如统一响应 + 分页。
- `packageMapStrategy`：控制输出目录和包名。
- `sharedVariables`：向模板传递共享变量，例如 QueryMap 父类名称、额外 import、运行时工具类型。
- `elementParsePostProcessors`：对解析后的接口模型做后处理，例如移除统一响应包装、调整返回类型。
- `ignorePackages` / `ignoreClasses`：排除内部接口。
- `ignoreMethodNames` / `ignoreFieldNames`：排除不参与 SDK 的方法或字段。
- `enableFieldUnderlineStyle`：字段命名策略。
- `ignoreEnumField`：枚举字段生成策略。

## 4. 从项目 Codegen 类抽取配置

如果项目中已有 `OpenApiSdkCodegen`、`ProjectSdkCodeGenerator`、Maven 插件或历史 SDK 产物，优先把它当成生产基准，而不是绕过它重新发明默认规则。抽取时要把代码里的生成行为转成中立配置，供后续替换生成引擎或扩展 OpenAPI 输入时复用。

建议按下面的顺序抽取：

1. 入口与环境：入口类、执行命令、模块路径、运行 JDK、Maven/Gradle 参数、是否需要 test classpath。
2. Profile：enterprise、personal、partner、internal 等 profile 的扫描包、输出目录、include/exclude 类和方法。
3. Provider：目标语言、Client Provider、模板风格、返回值是否裸类型、Java SDK 是否使用 Retrofit/OpenFeign/Spring HTTP。
4. 包映射：Controller、DTO、Request、Query、Enum、Core、第三方公共类型到目标包或目录的映射。
5. 类型映射：统一响应、分页、文件、`Void`、Query 对象、排序类型、枚举、金额、日期、ID 等映射。
6. 模板变量和后处理：`sharedVariables`、QueryMap 父类、额外 import、统一响应解包 post processor。
7. 忽略规则：忽略类、忽略方法、忽略字段、忽略枚举字段，并补充忽略原因。
8. 输出策略：是否删除输出目录、是否生成 index、是否备份、是否允许覆盖调用方已改造目录。
9. 对标策略：生成后比较文件数量、Client 列表、方法签名、返回类型、包结构、关键 import 和编译结果。

配置抽取示例：

```yaml
targets:
  - name: enterprise-java
    profile: enterprise
    language: JAVA
    provider: RETROFIT
    template_style: loong_wind_retrofit
    return_style: bare_unwrapped
    query_object_strategy: query_map
    pagination_strategy: wind_immutable_pagination
    package_map:
      com.example.web.openapi.controller: com.example.api.clients
      com.example.**.model.dto: com.example.api.model.dto
      com.example.**.model.query: com.example.api.model.query
      com.example.**.model.request: com.example.api.model.request
      com.example.**.enums: com.example.api.model.enums
    type_mappings:
      MultipartFile: FILE
      ApiResp: JAVA_API_RESPONSE
      Pagination: JAVA_PAGINATION
      AbstractPageQuery: JAVA_ABSTRACT_PAGE_QUERY_MAP
      Void: VOID_WRAPPER
    shared_variables:
      queryObjectShareClassName: AbstractPageQueryMap
      queryObjectShareDependencies:
        - com.wind.client.retrofit.query.AbstractPageQueryMap
    post_processors:
      - RemoveClientResponseTypePostProcessor: JAVA_API_RESPONSE
```

抽取结论必须说明：哪些是项目私有规则，哪些是通用 SDK 生成能力，哪些能力当前生成器还不支持。只有当 profile、包结构、方法签名、返回类型、QueryMap、分页和编译结果都能对标时，才可以把新方案称为替代方案；否则应称为草案生成、迁移方案或能力缺口清单。

## 5. 自定义 Maven 插件生成器

适合把复杂 Builder 配置封装到项目代码中：

```xml
<configuration>
    <clientProviderTypes>spring_cloud_openfeign,typescript_feign</clientProviderTypes>
    <pluginCodeGeneratorClass>com.example.codegen.ProjectSdkCodeGenerator</pluginCodeGeneratorClass>
</configuration>
```

自定义类可实现项目内统一策略：

```java
public class ProjectSdkCodeGenerator implements MavenPluginInvokeCodeGenerator {

    @Override
    public void generate(String output, List<ClientProviderType> types) {
        LoongCodeGenerator generator = new LoongCodeGenerator("com.example.**.controller");
        generator.setOutputPath(output);
        generator.setClientProviderTypes(types);
        generator.generate();
    }
}
```

适合：

- 多模块项目。
- 需要统一包名映射。
- 需要统一响应解包。
- 需要统一排除内部接口。
- 需要生成后上传或归档。

## 6. 生成前检查清单

- Controller 包路径是否明确。
- 是否只扫描公开 API，不扫描内部、管理后台或测试 Controller。
- 目标 Provider 是否由调用方技术栈决定。
- Java SDK 是否确认目标 JDK、Spring/Boot 代际、Validation 命名空间和依赖版本。
- 输出目录是否完全由生成器管理，是否允许清理或覆盖。
- 是否确认统一响应解包策略。
- 是否确认分页、枚举、文件上传、日期时间、金额、ID 类型映射。
- 是否确认 Query 对象使用 `@QueryMap` 还是展开为多个 `@Query`。
- 是否确认项目生成器中的 `sharedVariables`、post processor、ignore rules 已转成配置项。
- 是否确认输出目录可覆盖。
- 是否需要生成前备份旧 SDK。
- 是否需要 CI 校验生成结果是否有差异。

## 7. 生成后建议验证

根据项目生态选择：

- Java SDK：`mvn test`、`mvn compile`、`./gradlew compileJava`。
- TypeScript SDK：`npm run typecheck`、`npm test`、`npm run lint`。
- Dart SDK：`dart analyze`、`dart test`。
- 生成目录差异：`git diff -- generated-sdk` 或项目约定脚本。
- 契约联调：至少选择关键接口做真实调用或 mock server 调用。
- 基准对标：与项目已有生成器或上一版 SDK 对比 profile、文件数量、Client 列表、方法签名、返回类型、包结构、QueryMap、分页类型和编译结果。

## 8. codegen-server 使用边界

codegen-server 适合平台化场景：

- 多项目集中生成 SDK。
- 通过项目名和分支拉取代码。
- 生成结果可下载。
- 团队希望统一 SDK 生成入口。

红线：

- 不默认开启或调用 codegen-server。
- 不把内部仓库凭证、token、生产地址写入配置。
- 上传生成结果前必须确认目标服务、项目名、分支和权限。
- 本地单项目生成优先使用 Maven 插件或 Builder。
