---
name: sql-ddl-java-generator
description: Generate Nobe project Java scaffold code from SQL DDL or schema files. Use when given a schema file or DDL, table name, and business module to infer parameters and create MyBatis-Flex entity, mapper, DTO, request/query, MapStruct converter, service, and service implementation code.
---

# SQL DDL Java Generator

Use this skill when asked to turn SQL `CREATE TABLE` DDL or a schema file table into Java code for this Nobe repository.

The user should not need to know the script parameters. If the user provides a schema file, table name, and business module, first analyze the repository and infer the needed parameters yourself.

## 本地协作学习机制

本地协作学习机制默认关闭。只有用户明确同意启用，且本地学习目录存在 `consent.md` 并标记为启用、授权当前技能或全局范围时，才读取或写入学习记录。默认目录为 `~/.skill-learning/`；如设置了 `SKILL_LEARNING_HOME`，则优先使用该目录。

如果尚未启用，可以在当前任务已出现稳定偏好、团队约规或业务背景等长期沉淀价值，且不会打断关键任务时，用一句话询问用户是否启用。用户拒绝时，不创建目录或文件，不在当前会话再次提示，除非用户主动提及。

用户在当前技能场景下同意时，默认只开启 `sql-ddl-java-generator`；只有用户明确要求“所有技能”或“全局开启”时，才对所有技能生效。启用后默认采用混合模式与协作型学习模型：低风险常规观察可静默进入 `Pending Observations`，可能影响长期行为、跨技能复用、业务/合规/隐私边界或强约束偏好的记录必须显示确认；发现用户判断或设计可能存在错误、逻辑漏洞或红线风险时，必须显示提示并讨论改进方式。未经用户明确确认，不得提升为 `Confirmed Agreements`，也不得提交、上传或共享到远程。学习记录不得写入本技能目录或 Codex 的技能安装目录。

## Workflow

1. Read the user's inputs: schema file path, target table name, and business module. If the user gives raw DDL instead of a schema file, use that DDL.
2. Inspect the business module before running the script:
   - locate `*-face/src/main/java` and `*-impl/src/main/java`
   - infer the base package from existing Java `package` declarations, for example `com.capte.nobe.kyc`
   - inspect nearby entity/model/service files for local package deviations and naming conventions
3. If a real ambiguity remains, ask the user to choose before generating. Do not guess for ambiguous module pairs, bounded contexts, base packages, enum types, or class names.
4. Read the target table DDL from the schema file and identify table name, table comment, columns, primary key, nullability, defaults, auto increment, and column comments.
5. Use the bundled `scripts/generate_from_ddl.py` for deterministic generation. In a global Codex install it lives at `/Users/qingweifan/.codex/skills/sql-ddl-java-generator/scripts/generate_from_ddl.py`.
6. Prefer generating into a review directory first when uncertain. Generate directly into module source roots only when the requested business module and package are clear.
7. Compare generated code with nearby existing code before finalizing. The closest references are:
   - `template/*.ftl`
   - `user-domain/user-impl/src/main/java/com/capte/nobe/kyc/dal/entities/KycPersonaVerification.java`
   - existing entity files with `@Column` usage.

## Parameter Inference

When the user says “schema 文件 + 表名 + 业务模块”, do this yourself:

- `--schema-file`: the supplied schema file path.
- `--table-name`: the supplied table name.
- `--business-module`: the supplied module directory or module name.
- `--repo-root`: the current repository root.
- `--base-package`: infer from existing Java files under the module. If the module contains multiple bounded contexts, inspect matching nearby files or ask only when ambiguous.
- `--face-src` / `--impl-src`: normally do not ask the user; infer from `*-face/src/main/java` and `*-impl/src/main/java`. Pass explicit values only if auto inference would be ambiguous.
- `--class-name`: infer from table name after removing leading `t_`; override only when nearby code or user naming indicates a different class name.
- `--author`: use the existing local convention, usually `qingweifan`, unless the user specifies another author.

Ask the user when:

- the supplied business module contains multiple face/impl pairs, for example `rbac` and `user`, and the table name does not clearly select one
- multiple base packages are plausible inside the selected modules
- a column should map to a project enum but the correct enum type is not uniquely inferable
- the generated class name from the table name conflicts with existing naming in nearby code

## Command

Generate from schema file and business module, letting the script infer module roots and package:

```bash
python3 /Users/qingweifan/.codex/skills/sql-ddl-java-generator/scripts/generate_from_ddl.py \
  --schema-file /path/to/schema.sql \
  --table-name t_kyc_persona_verification \
  --business-module user-domain \
  --repo-root /Users/qingweifan/IdeaProjects/capteProjects/nobe \
  --author qingweifan
```

Generate into a review directory:

```bash
python3 /Users/qingweifan/.codex/skills/sql-ddl-java-generator/scripts/generate_from_ddl.py \
  --ddl-file /path/to/table.sql \
  --base-package com.capte.nobe.kyc \
  --author qingweifan \
  --output-dir /tmp/nobe-ddl-generated
```

Generate directly into Nobe face/impl modules:

```bash
python3 /Users/qingweifan/.codex/skills/sql-ddl-java-generator/scripts/generate_from_ddl.py \
  --ddl-file /path/to/table.sql \
  --base-package com.capte.nobe.kyc \
  --author qingweifan \
  --face-src user-domain/user-face/src/main/java \
  --impl-src user-domain/user-impl/src/main/java
```

Use `--class-name` when the table name does not produce the desired Java class name. Use `--overwrite` only after checking existing files.

## Project Rules

- Entity package: `${basePackage}.dal.entities`
- Mapper package: `${basePackage}.dal.mapper`
- Converter package: `${basePackage}.services.mapstruct`
- Service implementation package: `${basePackage}.services.impl`
- DTO/request/query/service packages are under `${basePackage}.model.*` and `${basePackage}.services`, typically in the face module.
- Entity style:
  - `@Data`
  - `@Table(Entity.TABLE_NAME)`
  - `public static final String TABLE_NAME = "...";`
  - `implements Serializable`
  - `serialVersionUID` must be annotated with `@Serial` and import `java.io.Serial`.
  - `@Id(keyType = KeyType.Auto)` for auto-increment primary key.
  - `@NotNull` for non-null fields, `@NotBlank` for non-null string/varchar/text fields without a default.
  - Preserve column comments as JavaDoc.
- Generated classes and methods must have JavaDoc comments. Every generated class JavaDoc must include `@author` and `@date`. Service, ServiceImpl, Converter, and private helper methods should include English `@param` and `@return` where applicable.
- Prefer SQL table and column comments for generated class comments, field JavaDoc, and `@Schema` in Entity, DTO, Request, and Query classes. If a SQL column comment is missing, do not invent field JavaDoc or `@Schema(description = ...)` for that field.
- For non-field comments that must be invented by the generator, prefer English.
- DTO style:
  - Use `@Data` only; do not add `@AllArgsConstructor`, `@NoArgsConstructor`, or `@Builder`.
  - `@Schema(description = "...")` for commented fields.
- Query style:
  - Query classes do not extend pagination base classes; pagination is passed separately through service method options.
  - Query classes always include fixed time range fields: `minGmtCreate`, `maxGmtCreate`, `minGmtModified`, `maxGmtModified`, all as `LocalDateTime` with `@Schema` descriptions `查询到最小gmtCreate`, `查询到最大gmtCreate`, `查询到最小gmtModified`, `查询到最大gmtModified`.
  - Query service methods put `@NonNull` on the line above the method signature, followed by `WindPagination<XxxDTO> queryXxxs(@NonNull XxxQuery query, @NonNull WindQuery<? extends QueryOrderField> options);`.
  - Query service implementations should build `QueryWrapper` inline with `MybatisQueryHelper.from(options).select().from(nameRefs)` plus generated `.where/.and` conditions, then return `MybatisQueryHelper.<Entity, DTO>query(queryWrapper).counter(mapper::selectCountByQuery).resultQueryFunc(mapper::selectListByQuery).converter(Converter.INSTANCE::convertToDTO).query(options)`. Do not split wrapper construction into a helper method unless the local codebase already needs custom query branching.
- Update request style:
  - `Update***Request` includes validation only for the primary key ID. Other fields must not receive `@NotNull`, `@NotBlank`, or similar required validation annotations.
- Service parameter style:
  - Service interface and implementation parameters use `org.jspecify.annotations.NonNull`.
  - Public service implementation methods must assert required parameters with `AssertUtils.notNull(param, "argument param must not null")`; collection/array parameters should use `AssertUtils.notEmpty(param, "argument param must not empty")`.

## MyBatis-Flex Column Rules

Always import and use `com.mybatisflex.annotation.Column` in entities when any generated field needs it.

- If the physical column name does not map cleanly to the Java field name, add `@Column("column_name")` or `@Column(value = "column_name")`.
- `tenant_id` or a field named `tenantId` should be `@Column(tenantId = true)`.
- `version`, `lock_version`, or columns whose comment mentions `乐观锁` or `版本号` should be `@Column(version = true)`.
- `is_deleted`, `deleted`, or columns whose comment mentions `逻辑删除` should be `@Column(value = "is_deleted", isLogicDelete = true)` when the physical column is `is_deleted`; otherwise use the actual column name.
- Boolean `is_*` columns should normally become Java fields without the `is` prefix, for example `is_enabled -> enabled`, and must keep `@Column("is_enabled")`.
- `u_id` should become `uid` and keep `@Column("u_id")`.
- Java reserved words must be renamed and keep `@Column(value = "...")`, for example `group -> groupValue` or local project convention if nearby code uses a different name.

## Type Rules

- Integer primary keys and `bigint` map to `Long`.
- `int`, `integer`, `tinyint`, `smallint`, `mediumint` map to `Integer`, except `tinyint(1)` and `bit(1)` map to `Boolean`.
- `decimal`, `numeric` map to `BigDecimal`.
- `datetime`, `timestamp` map to `LocalDateTime`.
- `date` maps to `LocalDate`.
- `time` maps to `LocalTime`.
- `char`, `varchar`, `text`, `json` map to `String`.
- Enum-like columns remain `String` unless the user supplies an enum mapping or nearby code clearly establishes one.

## Validation

After generation:

- Run the script with a representative DDL and inspect generated entity annotations.
- If writing into project modules, run a targeted Maven compile for the affected module when feasible.
- Report files created and any assumptions, especially enum fields or reserved-word renames.
