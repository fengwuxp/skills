---
name: java-service-code-generator
description: 根据 DDL/SQL、Java 类、字段表格等结构化输入生成 Wind/Nobe 风格 Java Service 配套代码。适用于给定业务结构、表名和业务模块后，自动推断参数并生成 MyBatis-Flex Entity、Mapper、DTO、Request、Query、MapStruct Converter、Service 和 ServiceImpl。
---

# Java Service 代码生成

当用户要求把 SQL `CREATE TABLE` DDL、schema 文件、Java 类、字段说明表格或其他结构化模型转换为 Java Service 配套代码时使用本技能。使用者不需要了解脚本参数；如果用户提供结构来源、表名和业务模块，应先分析仓库并自行推断参数。

本技能的代码生成规程参考 `https://github.com/fengwuxp/wind-middleware/tree/main/tools/mybatis-flex-codegen`，并叠加 `资深架构师` 技能中的代码约规与审查红线。

## 本地协作学习机制

本地协作学习机制遵循仓库 `AGENTS.md`；本技能不保存学习数据，学习记录只允许在用户明确同意后写入 `~/.skill-learning/` 或 `SKILL_LEARNING_HOME`。

## 工作流程

1. 读取用户输入：DDL/SQL、schema 文件路径、Java 类、字段说明表格、目标表名、业务模块；优先根据用户已有材料生成，不强制要求用户补 DDL。输入源与详细规程见 `references/code-generation-rules.md`。
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

根据使用者提供的内容选择输入路径；完整可信度和字段推断规则见 `references/code-generation-rules.md`。

- DDL/schema：最高可信输入。
- Java 类：适用于已有 Entity、DTO、DO、PO、VO、Request 或 Query。
- 字段说明表格：适用于 PRD、Excel、Markdown 表格、CSV、TSV，可额外生成待确认 DDL 草案。
- 普通 SQL：包含 `CREATE TABLE` 时按 DDL 处理；查询/插入/视图 SQL 只能辅助推断。
- JSON Schema、OpenAPI、Protobuf、Avro、IDL、ER 图、数据库设计文档和数据样例：可生成草案，但持久化语义、主键、索引、约束、金额/状态语义必须标记为待确认。

## 参数推断

用户提供“结构来源 + 表名 + 业务模块”时，应自行推断脚本参数；完整参数清单和命令示例见 `references/code-generation-rules.md`。

只有以下场景需要询问用户：

- 指定业务模块下存在多个 face/impl 模块对，且表名无法明确选择。
- 目标模块内存在多个可能的基础包名。
- 某个字段应映射为项目枚举，但无法唯一确定枚举类型。
- Java 类或字段表格缺少主键、表名、必填约束、默认值、精度、逻辑删除语义等生产必要信息。
- 表名推导出的 Java 类名与本地已有命名风格冲突。
- 生成会覆盖已有文件，而用户未明确允许覆盖。

## 生成规程与参考

- 详细代码生成规程、Entity/Request/Query/Service/MyBatis-Flex/类型映射规则见 `references/code-generation-rules.md`。
- Wind/Nobe 项目风格、模块约定和已知模式见 `references/nobe-patterns.md`。
- 生成必须优先使用 `scripts/generate_scaffold.py`；脚本是确定性执行面，Skill 负责输入识别、参数推断和审查。

## 脚本安全边界

- `scripts/generate_scaffold.py` 只接收本地 DDL/SQL、Java 类、字段表格和命令参数，不访问网络、不上传文件、不读取密钥。
- 写入范围仅限 `--output-dir`、`--face-src`、`--impl-src` 和 `--emit-ddl` 指定路径；未明确目标模块时先写入评审目录。
- 默认不覆盖已有文件；只有用户明确允许覆盖并确认影响范围后，才可使用 `--overwrite`。
- `scripts/verify_fixtures.py` 仅用于本仓库 fixture 校验，写入临时输出目录，不作为业务项目生成入口。

## 生成后验证

- 至少使用代表性 DDL、Java 类和字段表格分别跑一次脚本或对应 fixture，检查生成文件是否稳定输出。
- 本仓库维护时，`scripts/verify_fixtures.py` 还必须覆盖负向路径：已有文件不允许覆盖、多个 face/impl 模块对存在歧义、字段表格缺少目标表名。
- Java 类或字段表格输入如果生成 DDL 草案，必须提示用户该 DDL 是推断结果，需要 DBA/架构师确认。
- 检查 Entity、Request、Query、Service、ServiceImpl、Converter 是否符合 `references/code-generation-rules.md` 与 `资深架构师` 编码约规。
- 如果写入真实项目模块，条件允许时运行受影响模块的定向 Maven 编译或测试。
- 最终向用户报告生成/修改的文件、关键假设和剩余风险；本仓库 Git 操作默认由用户执行。

## 不适用场景

- 不在输入只有自然语言描述、缺少字段结构、表名、主键或业务模块时直接生成生产代码；此时只能生成草案或先询问关键缺口。
- 不替代架构师、DBA 或业务负责人确认表设计、索引、唯一约束、金额精度、状态机、枚举和数据生命周期。
- 不在未检查目标模块、基础包名、本地命名风格和已有文件冲突时写入真实源码目录。
- 不默认覆盖已有文件；需要覆盖时必须先说明影响范围并取得用户确认。
- 不生成绕过 `资深架构师` 编码红线的代码，包括超过 5 个公有参数、伪复用、无意义一行方法抽取、吞异常、裸日志、敏感信息泄露或模糊空值契约。
- 不把 Java 类、字段表格、JSON、OpenAPI、IDL 或数据样例推断出的 DDL 当作已确认生产 DDL；必须标记为待 DBA/架构师确认。
