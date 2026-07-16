# Wind/Nobe DDL 生成模式

参考模块：`https://github.com/fengwuxp/wind-middleware/tree/main/tools/mybatis-flex-codegen`

该模块使用 Freemarker 模板生成 DTO、Request、Query、Mapper、MapStruct、Service、ServiceImpl 等代码。本技能不直接复刻全部实现，但应吸收以下稳定规程。这些生成模板视为 Wind 编码约规的标准实现样本；若模板规则和项目约规冲突，以 `wind-coding-conventions` 和项目本地 `AGENTS.md` 为准。

## 使用时机

- 需要确认 Wind/Nobe 风格模块布局、中文描述、DTO/Request/Query、Entity/MyBatis-Flex 和 Service 生成惯例。

## 不适用场景

- 需要完整脚本参数、输入可信度或 golden fixture 维护时，读 `code-generation-rules.md`。

## 读取后必须产出

- 本地模块布局判断、包名推断依据、生成风格差异和需要人工确认的项目约定。

## 需要继续读取的 reference

- 生成规程和验证读 `code-generation-rules.md`；Wind 规则审查交给 `wind-coding-conventions`，源码级 Review 交给 `资深架构师`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断模块布局 | 模块布局 | 审查要点 |
| 生成 DTO/Request/Query | 中文描述、DTO / Request / Query | Entity 细节 |
| 生成 Entity/MyBatis-Flex | Entity 与 MyBatis-Flex | Service 细节 |
| 生成 Service/ServiceImpl | Service / ServiceImpl、资深架构师审查要点 | 输入源路由 |

## 输入源路由

- DDL/schema 是最高可信输入，可直接进入生产代码生成链路。
- Java Entity/DTO/DO/PO/VO 可作为输入源，解析类名、字段名、Java 类型、JavaDoc、`@Schema`、`@Column`、`@Id` 和验证注解；无法表达的数据库约束必须作为待确认项。
- Markdown/CSV/TSV 字段表格可作为输入源，字段列建议包含“字段名、Java 属性名、类型、说明、是否主键、是否必填、默认值、是否自增”。
- 字段表格和 Java 类可以生成 DDL 草案，但 DDL 草案需要 DBA/架构师确认后才能作为正式数据库设计。
- 查询 SQL、JSON 示例、OpenAPI schema、Protobuf/Avro/IDL、Excel 数据样例可以辅助推导模型，但主键、索引、唯一约束、金额精度、状态语义、逻辑删除、租户隔离等生产约束不得盲推。

## 模块布局

- `xxx-face/src/main/java`：DTO、Request、Query、Service。
- `xxx-impl/src/main/java`：Entity、Mapper、MapStruct Converter、ServiceImpl。
- 基础包名优先从选定 face/impl 模块已有 Java `package` 声明推断。
- 如果模块下存在多个限界上下文或多个基础包名，先根据表名前缀和相邻代码判断；仍不明确时询问用户。

## 中文描述

- 生成的 JavaDoc、`@Schema`、断言消息和异常提示尽量使用中文。
- 表和字段业务描述优先来自 SQL 注释。
- SQL 注释缺失时，不臆造字段业务含义；类级和方法级描述可以使用“实体”“服务”“创建请求”“查询条件”等中性中文兜底。
- 断言消息保持业务可读，例如“参数 request 不能为空”“创建客户失败”“客户不存在或已删除”。

## DTO / Request / Query

- DTO 保持简单数据承载，不默认生成构造器、Builder 或业务方法。
- DTO / Request / Query / Service 是 face 对外契约；不得把 Entity、Mapper、Repository 或 MyBatis `Page` 暴露到 face、Controller、Facade、Adapter、跨模块接口或事件消息契约。
- 创建请求排除主键、`gmt_create`、`gmt_modified`。
- 更新请求只对主键 ID 保留必填校验，其他字段不生成必填校验，避免破坏局部更新语义。
- 查询对象不承载分页继承关系；分页和排序由服务方法的 `WindQuery<? extends QueryOrderField> options` 承载。
- 查询对象固定补充 `minGmtCreate`、`maxGmtCreate`、`minGmtModified`、`maxGmtModified` 时间范围字段。

## Entity 与 MyBatis-Flex

- Entity 使用 `@Table(Entity.TABLE_NAME)` 和 `public static final String TABLE_NAME`。
- Entity 实现 `Serializable`，`serialVersionUID` 使用 `@Serial`。
- 任一字段需要 `@Column` 时，导入 `com.mybatisflex.annotation.Column`。
- 常见特殊字段：
  - `tenant_id`：`@Column(tenantId = true)`
  - `version` / `lock_version`：`@Column(version = true)`
  - `is_deleted` / `deleted`：`@Column(value = "实际列名", isLogicDelete = true)`
  - `u_id`：Java 字段 `uid`，并添加 `@Column("u_id")`
  - `is_enabled`：Java 字段 `enabled`，并添加 `@Column("is_enabled")`

## Service / ServiceImpl

- Spring Bean 构造注入优先使用 Lombok `@AllArgsConstructor`。
- 内部服务参数使用 `org.jspecify.annotations.NonNull`；实现方法内不再重复写无业务语义的 `AssertUtils.notNull`，只对集合内容、状态条件和查不到数据等运行时业务事实使用断言。
- 单 ID 删除可以作为接口 default 方法委托批量删除，这是服务契约便利方法；必然存在的 ID 查询使用 `getXxxById`；ServiceImpl 只实现批量删除。
- 币种字段使用 `com.wind.transaction.core.enums.CurrencyIsoCode`，不生成 `String currency`。
- 查询实现优先内联 `QueryWrapper` 构造，除非本地已有复杂分支，不为了“复用”提取一行方法或伪工具类。
- 公共方法参数不得超过 5 个。生成代码当前以 Request/Query/Options 聚合参数，避免长参数列表。
- Entity 只在 ServiceImpl、DAL、Mapper 和 Converter 内部流转；离开 impl 边界前必须转换为 DTO、Request、Query、Command、Event 或值对象。

## 资深架构师审查要点

- 不因 DTO 构建或简单转换逻辑相似就提取公共方法。
- 避免无意义的一行方法复用和过深调用链。
- MapStruct 只做对象转换，不承载业务判断或副作用。
- Lombok 只用于减少样板代码，不隐藏关键领域约束。
- API 模型使用验证注解，内部服务参数使用 JSpecify 注解；业务前置条件、集合内容和状态事实使用 `AssertUtils`。
- 生成结果必须可读、可审查、可按本地项目规范继续演进。
