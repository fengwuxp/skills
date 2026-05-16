---
name: java-service-code-generator
description: 根据 DDL/SQL、Java 类、字段表格等结构化输入生成 Wind/Nobe 风格 Java Service 配套代码。适用于给定业务结构、表名和业务模块后，自动推断参数并生成 MyBatis-Flex Entity、Mapper、DTO、Request、Query、MapStruct Converter、Service 和 ServiceImpl。
---

# Java Service 代码生成

当用户要求把 SQL `CREATE TABLE` DDL、schema 文件、Java 类、字段说明表格或其他结构化模型转换为 Java Service 配套代码时使用本技能。使用者不需要了解脚本参数；如果用户提供结构来源、表名和业务模块，应先分析仓库并自行推断参数。

本技能的代码生成规程参考 `https://github.com/fengwuxp/wind-middleware/tree/main/tools/mybatis-flex-codegen`，并叠加 `资深架构师` 技能中的代码约规与审查红线。

## 本地协作学习机制

本地协作学习机制默认关闭。只有用户明确同意启用，且本地学习目录存在 `consent.md` 并标记为启用、授权当前技能或全局范围时，才读取或写入学习记录。默认目录为 `~/.skill-learning/`；如设置了 `SKILL_LEARNING_HOME`，则优先使用该目录。

如果尚未启用，应先按仓库 `AGENTS.md` 中的学习时机判定算法判断当前任务是否已经出现稳定偏好、团队约规、业务背景、反复决策方式等长期沉淀价值；只有达到问询阈值，且不会打断关键任务时，才可以用一句话询问用户是否启用。用户拒绝时，不创建目录或文件，不在当前会话再次提示，除非用户主动提及。

用户在当前技能场景下同意时，默认只开启 `java-service-code-generator`；只有用户明确要求“所有技能”或“全局开启”时，才对所有技能生效。启用后默认采用混合模式与协作型学习模型：记录前必须先经过候选识别、价值评分、风险门禁和动作决策；低风险常规观察可静默进入 `Pending Observations`，可能影响长期行为、跨技能复用、业务/合规/隐私边界或强约束偏好的记录必须显示确认；发现用户判断或设计可能存在错误、逻辑漏洞或红线风险时，必须显示提示并讨论改进方式。未经用户明确确认，不得提升为 `Confirmed Agreements`，也不得提交、上传或共享到远程。学习记录不得写入本技能目录或 Codex 的技能安装目录。

## 工作流程

1. 读取用户输入：DDL/SQL、schema 文件路径、Java 类、字段说明表格、目标表名、业务模块；优先根据用户已有材料生成，不强制要求用户补 DDL。
2. 生成前先检查业务模块：
   - 定位 `*-face/src/main/java` 和 `*-impl/src/main/java`。
   - 从已有 Java `package` 声明推断基础包名，例如 `com.capte.nobe.kyc`。
   - 检查相邻 Entity、Model、Service、Mapper、Converter，确认本地命名、包路径和注解风格。
3. 只有存在真实歧义时才询问用户；不要猜测有歧义的模块对、限界上下文、基础包名、枚举类型或类名。
4. 将输入源归一为内部表结构模型，识别表名、表注释、字段、主键、空值约束、默认值、自增、字段注释和逻辑删除/租户/版本字段。
5. 优先使用内置 `scripts/generate_scaffold.py` 做确定性生成；在本仓库维护时可使用 `python3 java-service-code-generator/scripts/generate_scaffold.py`，安装到 Codex 后可使用 `$CODEX_HOME/skills/java-service-code-generator/scripts/generate_scaffold.py`。
6. 不确定时先生成到评审目录；业务模块和包名明确时，才直接生成到模块源码目录。
7. 生成后对比附近已有代码，并按 `资深架构师` 的代码约规做一次审查，重点检查注释、空指针处理、参数数量、伪复用、MapStruct、Lombok、不可变对象、验证注解和查询链路可读性。

## 输入源路由

根据使用者提供的内容选择输入路径：

- SQL DDL / schema：最高可信输入。直接解析 `CREATE TABLE`，保留 SQL 注释、类型、主键、默认值、自增、逻辑删除、租户和版本字段。
- Java 类：适用于用户已有 Entity、DTO、DO、PO、VO、Request 或 Query。优先解析类名、字段名、字段类型、JavaDoc、`@Schema`、`@Column`、`@Id`、`@NotNull`、`@NotBlank`；表名可由 `@Table` 或类名推导。Java 类无法完整表达索引、精度、默认值和数据库方言时，应标记为推断。
- 表格结构的字段说明：适用于 PRD、Excel、Markdown 表格、CSV、TSV。推荐字段列包括“字段名/列名、Java 属性名、类型/SQL 类型/Java 类型、说明、是否主键、是否必填、默认值、是否自增”。字段表格可额外生成 DDL 草案，但 DDL 草案必须作为待 DBA/架构师确认的输出。
- 普通 SQL 语句：如果包含 `CREATE TABLE`，按 DDL 处理；如果是查询 SQL、插入 SQL 或视图 SQL，只能辅助推断字段、表名和查询模型，不能当作完整表结构。
- 其他可补充输入：
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
- `--base-package`：从模块已有 Java 文件推断；如果同一模块存在多个限界上下文，先检查相邻代码，仍不明确时再问用户。
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
  --table-name t_kyc_persona_verification \
  --business-module user-domain \
  --repo-root /path/to/repo \
  --author wuxp
```

通过 Java 类生成，并额外输出 DDL 草案：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --input-file /path/to/PaymentOrder.java \
  --input-type java \
  --table-name t_payment_order \
  --table-comment 支付订单 \
  --base-package com.capte.nobe.payment \
  --emit-ddl /tmp/payment_order.sql \
  --output-dir /tmp/nobe-ddl-generated
```

通过 Markdown/CSV/TSV 字段表格生成：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --input-file /path/to/payment_order_fields.md \
  --input-type table \
  --table-name t_payment_order \
  --table-comment 支付订单 \
  --base-package com.capte.nobe.payment \
  --emit-ddl /tmp/payment_order.sql \
  --output-dir /tmp/nobe-ddl-generated
```

先生成到评审目录：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --ddl-file /path/to/table.sql \
  --base-package com.capte.nobe.kyc \
  --author wuxp \
  --output-dir /tmp/nobe-ddl-generated
```

直接生成到 face/impl 模块：

```bash
python3 java-service-code-generator/scripts/generate_scaffold.py \
  --ddl-file /path/to/table.sql \
  --base-package com.capte.nobe.kyc \
  --author wuxp \
  --face-src user-domain/user-face/src/main/java \
  --impl-src user-domain/user-impl/src/main/java
```

只有在表名无法生成期望类名时才使用 `--class-name`。只有检查过已有文件并确认允许覆盖后才使用 `--overwrite`。

## 代码生成规程

- Entity 包：`${basePackage}.dal.entities`
- Mapper 包：`${basePackage}.dal.mapper`
- Converter 包：`${basePackage}.services.mapstruct`
- ServiceImpl 包：`${basePackage}.services.impl`
- DTO、Request、Query、Service 通常位于 face 模块下的 `${basePackage}.model.*` 和 `${basePackage}.services`。
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
- ServiceImpl 公共方法必须使用 `AssertUtils` 对必填参数做运行时断言，例如 `AssertUtils.notNull(request, "参数 request 不能为空")`。
- 集合或数组参数使用 `AssertUtils.notEmpty(ids, "参数 ids 不能为空")`。
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

## 不适用场景

- 不在输入只有自然语言描述、缺少字段结构、表名、主键或业务模块时直接生成生产代码；此时只能生成草案或先询问关键缺口。
- 不替代架构师、DBA 或业务负责人确认表设计、索引、唯一约束、金额精度、状态机、枚举和数据生命周期。
- 不在未检查目标模块、基础包名、本地命名风格和已有文件冲突时写入真实源码目录。
- 不默认覆盖已有文件；需要覆盖时必须先说明影响范围并取得用户确认。
- 不生成绕过 `资深架构师` 编码红线的代码，包括超过 5 个公有参数、伪复用、无意义一行方法抽取、吞异常、裸日志、敏感信息泄露或模糊空值契约。
- 不把 Java 类、字段表格、JSON、OpenAPI、IDL 或数据样例推断出的 DDL 当作已确认生产 DDL；必须标记为待 DBA/架构师确认。
