# Java Service 代码生成规程

本文承接 `SKILL.md` 中的代码生成细则。只有在需要实际生成、调整、审查 Wind/Nobe 风格 Java Service 配套代码时读取；普通技能识别和路由不需要加载本文。本生成器输出的基础服务、DTO、Request、Query、Entity、Mapper、Converter、Service 和 ServiceImpl 是 Wind 项目编码约规的标准模板实现面；规则权威来源是 `wind-project-coding-conventions` Skill。

## 使用时机

- 用户明确要求根据 DDL/SQL、schema、Java 类或字段表格生成 Wind/Nobe 风格 Java Service 配套代码。
- 需要维护 `scripts/generate_scaffold.py`、更新 fixture/golden hash，或审查生成器输出是否符合团队规程。

## 不适用场景

- 代码 Review、Bug 修复、补测试或架构评审优先交给 `资深架构师`。
- 只有自然语言业务描述、缺少字段结构/表名/模块时，不直接生成生产代码。

## 读取后必须产出

- 输入可信度、脚本参数、写入范围、待确认项、生成/验证动作和剩余风险。

## 需要继续读取的 reference

- Wind/Nobe 模块风格读 `nobe-patterns.md`；具体代码红线、Entity 不外露和服务接口职责规则审查交给 `wind-project-coding-conventions`，源码级 Review 交给 `资深架构师`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断输入可信度 | 输入源路由、参数推断 | 生成细则 |
| 运行脚本生成 | 参数推断、命令示例、脚本安全边界见 `SKILL.md` | Fixture 维护 |
| 维护生成器 fixtures | Fixture 与黄金输出契约、生成后验证 | 类型映射细节 |
| 审查生成结果 | 代码生成规程、Entity/Request/Query/Service/类型映射、生成后验证 | 命令示例 |

## 输入源路由

根据使用者提供的内容选择输入路径：

- SQL DDL / schema：最高可信输入。直接解析 `CREATE TABLE`，保留 SQL 注释、类型、主键、默认值、自增、逻辑删除、租户和版本字段。
- Java 类：适用于用户已有 Entity、DTO、DO、PO、VO、Request 或 Query。优先解析类名、字段名、字段类型、JavaDoc、`@Schema`、`@Column`、`@Id`、`@NotNull`、`@NotBlank`；表名可由 `@Table` 或类名推导。Java 类无法完整表达索引、精度、默认值和数据库方言时，应标记为推断。
- 表格结构的字段说明：适用于 PRD、Excel、Markdown 表格、CSV、TSV。推荐字段列包括“字段名/列名、Java 属性名、类型/SQL 类型/Java 类型、说明、是否主键、是否必填、默认值、是否自增”。字段表格可额外生成 DDL 草案，但 DDL 草案必须作为待 DBA/架构师确认的输出。
- 普通 SQL 语句：如果包含 `CREATE TABLE`，按 DDL 处理；如果是查询 SQL、插入 SQL 或视图 SQL，只能辅助推断字段、表名和查询模型，不能当作完整表结构。
- JSON 示例或 JSON Schema：适合推导 DTO/Request 字段，但数据库类型、主键、索引和约束需要确认。
- OpenAPI/Swagger schema：适合推导 API 模型和校验注解，生成持久化结构前需要确认表名和存储约束。
- Protobuf/Avro/IDL：适合推导跨服务模型，落库语义需要确认。
- Excel/CSV 数据样例：只能辅助推断字段和类型，不应直接推断主键、唯一约束或资金/状态语义。
- ER 图、数据库设计文档、Markdown 字段清单：适合生成初稿，约束缺失时必须保留待确认项。

输入可信度原则：DDL/schema > Java Entity > 结构化字段表格 > API/IDL schema > 数据样例或自然语言描述。低可信输入可以生成草案，但不得把推断结果包装成已确认的生产设计。

## 参数推断

用户提供“结构来源 + 表名 + 业务模块”时，应自行推断以下参数：

- `--input-file`：用户提供的 Java 类、字段表格、DDL/SQL 文件路径。
- `--input-type`：默认 `auto`；输入类型明确时可传 `ddl`、`java` 或 `table`。
- `--schema-file`：用户提供的 schema 文件路径。
- `--table-name`：schema 输入时表示要提取的目标表；Java/字段表格输入时表示要生成的表名。
- `--table-comment`：Java/字段表格输入时的表中文说明。
- `--business-module`：用户提供的模块目录或模块名。
- `--repo-root`：当前仓库根目录。
- `--base-package`：从模块已有 Java 文件推断；如果同一模块存在多个限界上下文，先检查相邻代码，仍不明确时再问用户；无法从源码推断时必须要求显式传入，不使用真实项目包名兜底。
- `--face-src` / `--impl-src`：通常不询问用户，优先从 `*-face/src/main/java` 和 `*-impl/src/main/java` 推断；只有自动推断存在歧义时才显式传入。
- `--class-name`：DDL/字段表格默认由表名去掉前缀 `t_` 后转为 PascalCase；Java 类默认使用类名去掉 DTO/DO/VO/PO/BO/Entity/Request/Query 后缀。
- `--author`：默认使用当前系统用户名；如果项目已有明确作者约定或用户指定作者，则遵循已有约定。
- `--emit-ddl`：当输入来自 Java 类或字段表格时，可额外输出 DDL 草案供 DBA/架构师确认。

需要询问用户的场景：

- 指定业务模块下存在多个 face/impl 模块对，且表名无法明确选择。
- 目标模块内存在多个可能的基础包名。
- 某个字段应映射为项目枚举，但无法唯一确定枚举类型。
- Java 类或字段表格缺少主键、表名、必填约束、默认值、精度、逻辑删除语义等生产必要信息。
- 表名推导出的 Java 类名与本地已有命名风格冲突。
- 生成会覆盖已有文件，而用户未明确允许覆盖。

## 命令示例

通过 schema 文件和业务模块生成，并让脚本自动推断模块根目录和基础包名：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --schema-file /path/to/schema.sql \
  --table-name t_sample_verification \
  --business-module sample-domain \
  --repo-root /path/to/repo \
  --author codex
```

通过 Java 类生成，并额外输出 DDL 草案：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --input-file /path/to/SampleOrder.java \
  --input-type java \
  --table-name t_sample_order \
  --table-comment 示例订单 \
  --base-package com.example.skill.codegen \
  --emit-ddl /tmp/sample_order.sql \
  --output-dir /tmp/skill-codegen-sample
```

通过 Markdown/CSV/TSV 字段表格生成：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --input-file /path/to/sample_order_fields.md \
  --input-type table \
  --table-name t_sample_order \
  --table-comment 示例订单 \
  --base-package com.example.skill.codegen \
  --emit-ddl /tmp/sample_order.sql \
  --output-dir /tmp/skill-codegen-sample
```

先生成到评审目录：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --ddl-file /path/to/table.sql \
  --base-package com.example.skill.codegen \
  --author codex \
  --output-dir /tmp/skill-codegen-sample
```

直接生成到 face/impl 模块：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --ddl-file /path/to/table.sql \
  --base-package com.example.skill.codegen \
  --author codex \
  --face-src sample-domain/sample-face/src/main/java \
  --impl-src sample-domain/sample-impl/src/main/java
```

只有在表名无法生成期望类名时才使用 `--class-name`。只有检查过已有文件并确认允许覆盖后才使用 `--overwrite`。

## Fixture 与黄金输出契约

本仓库维护代码生成器时，`scripts/verify_fixtures.py` 是确定性回归入口，不只是 smoke test。它必须同时覆盖：

- DDL、Java 类和字段表格三类输入。
- 关键生成文件的 normalized golden hash，过滤 `@date` 和 `serialVersionUID` 这类运行时噪声后比较模板结构。
- 负向路径：已有文件不允许覆盖、多个 face/impl 模块对存在歧义、字段表格缺少目标表名。

当确实需要调整模板结构时，先人工审查生成 diff，再同步更新 golden hash；不得只为通过验证而更新 hash。

## 代码生成规程

- Entity 包：`${basePackage}.dal.entities`
- Mapper 包：`${basePackage}.dal.mapper`
- Converter 包：`${basePackage}.services.mapstruct`
- ServiceImpl 包：`${basePackage}.services.impl`
- DTO、Request、Query、Service 通常位于 face 模块下的 `${basePackage}.model.*` 和 `${basePackage}.services`。
- face 模块生成的 Service 契约只暴露 DTO/Request/Query/WindQuery/分页结果，不暴露 Entity、Mapper、Repository 或 MyBatis `Page`；Entity 只在 impl/DAL/Converter 内部流转。
- 生成描述尽可能使用中文：
  - 表注释、字段注释优先来自 SQL DDL。
  - 有 SQL 注释时，JavaDoc、`@Schema(description = "...")`、断言消息和服务方法说明应尽量使用中文。
  - SQL 注释缺失时，不臆造业务含义；字段不生成虚假的 JavaDoc 或 `@Schema`，类和方法只使用中性中文描述。
- 生成的类和方法必须有 JavaDoc；每个类 JavaDoc 必须包含 `@author` 和 `@date`。
- Service、ServiceImpl、Converter、私有辅助方法的 `@param`、`@return` 使用中文描述。
- DTO 使用 `@Data` 即可，不默认添加 `@AllArgsConstructor`、`@NoArgsConstructor` 或 `@Builder`。
- Spring Bean 构造注入优先使用 Lombok `@AllArgsConstructor`。
- MapStruct Converter 只承载对象转换，不夹带业务判断、查询、断言或副作用。

## Entity 规程

- 使用 `@Data`。
- 使用 `@Table(Entity.TABLE_NAME)`。
- 声明 `public static final String TABLE_NAME = "...";`。
- 实现 `Serializable`。
- `serialVersionUID` 使用 `@Serial`，并导入 `java.io.Serial`。
- 自增主键使用 `@Id(keyType = KeyType.Auto)`。
- 主键使用 `@NotNull`。
- 非空且无默认值的 `String` 字段使用 `@NotBlank`，其他非空字段使用 `@NotNull`。
- 字段 JavaDoc 保留 SQL 字段注释；缺失 SQL 注释时不臆造字段注释。

## MyBatis-Flex 字段规程

当任一字段需要 `@Column` 时，必须导入 `com.mybatisflex.annotation.Column`。

- 物理列名无法自然映射到 Java 字段名时，添加 `@Column("column_name")` 或 `@Column(value = "column_name")`。
- `tenant_id` 或字段名 `tenantId` 使用 `@Column(tenantId = true)`。
- `version`、`lock_version`，或字段注释包含“乐观锁”“版本号”时，使用 `@Column(version = true)`。
- `is_deleted`、`deleted`，或字段注释包含“逻辑删除”时，使用 `@Column(value = "实际列名", isLogicDelete = true)`。
- Boolean 类型 `is_*` 字段默认去掉 `is` 前缀，例如 `is_enabled -> enabled`，并保留 `@Column("is_enabled")`。
- `u_id` 转为 Java 字段 `uid`，并保留 `@Column("u_id")`。
- Java 保留字必须重命名并保留 `@Column`，例如 `group -> groupValue`；如果相邻代码有其他约定，遵循本地约定。

## Request 与 Query 规程

- `Create***Request` 不包含主键和 `gmt_create`、`gmt_modified`。
- `Update***Request` 包含主键 ID，并且只对主键 ID 添加必填校验；其他字段不添加 `@NotNull`、`@NotBlank` 等必填校验。
- Query 类不继承分页基类，分页参数通过服务方法的 `WindQuery<? extends QueryOrderField> options` 传入。
- Query 类固定包含 `minGmtCreate`、`maxGmtCreate`、`minGmtModified`、`maxGmtModified`，类型为 `LocalDateTime`，并使用中文 `@Schema` 描述。
- 查询服务方法在方法签名上一行添加 `@NonNull`，方法形如 `WindPagination<XxxDTO> queryXxxs(@NonNull XxxQuery query, @NonNull WindQuery<? extends QueryOrderField> options);`。
- 查询实现优先内联构造 `QueryWrapper`：使用 `MybatisQueryHelper.from(options).select().from(nameRefs)`，再追加生成的 `.where/.and` 条件。除非本地代码已有复杂分支需求，不为了“提取而提取”拆出辅助方法。

## Service 规程

- Service 接口和实现方法参数使用 `org.jspecify.annotations.NonNull`。
- 会暴露到 API 的模型字段使用 `jakarta.validation`/`javax.validation` 校验注解；内部服务参数使用 `org.jspecify.annotations.NonNull`。
- ServiceImpl 不对已经由 `@NonNull` 表达的普通参数重复生成 `AssertUtils.notNull`；只有集合或数组的非空/非空集合约束、状态条件、查不到数据等运行时业务事实才使用 `AssertUtils`。
- 集合或数组参数使用 `AssertUtils.notEmpty(ids, "参数 ids 不能为空")`，用于表达集合内容约束，而不是重复表达 JSpecify 的 nullability。
- 生成批量删除方法 `void deleteXxxByIds(@NonNull Long... ids);`。
- 单 ID 删除方法作为 Service 接口 default 方法直接委托批量删除：`default void deleteXxxById(@NonNull Long id) { deleteXxxByIds(id); }`。这是稳定服务契约，不视为无意义的一行方法复用。
- ServiceImpl 只实现批量删除方法，使用 `mapper.deleteBatchByIds(Arrays.asList(ids))`，并断言影响行数与传入 ID 数一致。
- 公有方法参数不得超过 5 个；如果生成或重构需要超过 5 个参数，必须先和用户确认。

## 类型映射规程

- 整型主键和 `bigint` 映射为 `Long`。
- `int`、`integer`、`smallint`、`mediumint` 映射为 `Integer`。
- `tinyint(1)`、`bit(1)` 映射为 `Boolean`；其他 `tinyint` 映射为 `Integer`。
- `decimal`、`numeric` 映射为 `BigDecimal`。
- `datetime`、`timestamp` 映射为 `LocalDateTime`。
- `date` 映射为 `LocalDate`。
- `time` 映射为 `LocalTime`。
- `char`、`varchar`、`text`、`json` 默认映射为 `String`。
- 类枚举字段默认保持 `String`；只有用户提供枚举映射或相邻代码能唯一确认枚举类型时，才生成枚举类型。

## 生成后验证

- 使用代表性 DDL、Java 类和字段表格分别跑一次脚本，检查生成文件是否能稳定输出。
- Java 类或字段表格输入如果生成了 DDL 草案，必须提示用户该 DDL 是推断结果，需要 DBA/架构师确认。
- 检查 Entity 注解、字段类型、字段注释、`@Schema`、`@Column`、逻辑删除、租户、版本字段是否正确。
- 检查 Request 校验是否符合创建/更新语义。
- 检查 Service/ServiceImpl 是否符合 `资深架构师` 编码约规：不超过 5 个公有参数、不做伪复用、不出现无意义一行方法抽取、空指针处理一致、Lombok/MapStruct 使用边界清晰。
- 如果写入真实项目模块，条件允许时运行受影响模块的定向 Maven 编译或测试。
- 最终向用户报告生成/修改的文件、关键假设和剩余风险；本仓库 Git 操作默认由用户执行。
