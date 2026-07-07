---
name: java-service-code-generator
description: 根据 DDL/schema、Java 类或字段表格生成 Wind/Nobe Java Service 脚手架；仅在用户明确要求生成、转换、脚手架或配套代码，且有结构化输入时触发。代码评审、Bug 修复和补测试优先交给架构师。
---

# Java Service 代码生成

当用户要求把 SQL `CREATE TABLE` DDL、schema 文件、Java 类、字段说明表格或其他结构化模型转换为 Java Service 配套代码时使用本技能。使用者不需要了解脚本参数；如果用户提供结构来源、表名和业务模块，应先分析仓库并自行推断参数。

本技能的基础服务、DTO、Request、Query、Entity、Mapper、MapStruct、Service、ServiceImpl 模板是 Wind 项目编码约规的标准生成面；权威规则以 `wind-project-coding-conventions` Skill 为准，本技能只保存可确定生成的模板细节，避免复制一套会漂移的约规。

## Skill 自我改进外循环

Skill 自我改进外循环遵循仓库 `AGENTS.md`。本技能只接收基于生成失败、fixture 失败、CR 反馈或项目约规偏差的最小改进；不保存个人长期偏好或私有轨迹，不把业务私有 schema 或生产配置写入仓库。

## 工作流程

1. 读取用户输入：DDL/SQL、schema 文件路径、Java 类、字段说明表格、目标表名、业务模块；优先根据用户已有材料生成，不强制要求用户补 DDL。输入源与详细规程见 `references/code-generation-rules.md`。
2. 被 AI Native 分派时，先消费 Engineering Handoff Card、授权策略和写入范围；缺少结构化输入、目标模块、覆盖边界或验证命令时，只输出缺口，不直接写源码。
3. 生成前先检查业务模块：
   - 定位 `*-face/src/main/java` 和 `*-impl/src/main/java`。
   - 从已有 Java `package` 声明推断基础包名，例如 `com.example.skill.codegen`；无法从源码推断时必须要求用户显式提供 `--base-package`，不要使用真实项目包名兜底。
   - 检查相邻 Entity、Model、Service、Mapper、Converter，确认本地命名、包路径和注解风格。
4. 只有存在真实歧义时才询问用户；不要猜测有歧义的模块对、限界上下文、基础包名、枚举类型或类名。
5. 将输入源归一为内部表结构模型，识别表名、表注释、字段、主键、空值约束、默认值、自增、字段注释和逻辑删除/租户/版本字段。
6. 优先使用内置 `scripts/generate_scaffold.py` 做确定性生成；在本仓库维护时可使用 `python3 java-service-code-generator/scripts/generate_scaffold.py`，安装到 Codex 后可使用 `$CODEX_HOME/skills/java-service-code-generator/scripts/generate_scaffold.py`。
7. 不确定时先生成到评审目录；业务模块和包名明确时，才直接生成到模块源码目录。
8. 生成后对比附近已有代码，并按 `资深架构师` 的代码约规做一次审查，重点检查注释、空指针处理、参数数量、伪复用、MapStruct、Lombok、不可变对象、验证注解和查询链路可读性。

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
- Wind/Nobe 项目风格、模块约定和已知模式见 `references/nobe-patterns.md`；生成后规则审查回到 `wind-project-coding-conventions`，源码级 CR / TDD 回到 `资深架构师`。
- 生成必须优先使用 `scripts/generate_scaffold.py`；脚本是确定性执行面，Skill 负责输入识别、参数推断和审查。

## 脚本安全边界

- `scripts/generate_scaffold.py` 只接收本地 DDL/SQL、Java 类、字段表格和命令参数，不访问网络、不上传文件、不读取密钥。
- 写入范围仅限 `--output-dir`、`--face-src`、`--impl-src` 和 `--emit-ddl` 指定路径；未明确目标模块时先写入评审目录。
- 默认不覆盖已有文件；只有用户明确允许覆盖并确认影响范围后，才可使用 `--overwrite`。
- `scripts/verify_fixtures.py` 仅用于本仓库 fixture 校验，写入临时输出目录，不作为业务项目生成入口。

## 生成后验证

- 至少使用代表性 DDL、Java 类和字段表格分别跑一次脚本或对应 fixture，检查生成文件是否稳定输出。
- 本仓库维护时，`scripts/verify_fixtures.py` 还必须覆盖关键生成文件 golden hash、Java 关键字 / 保留字 / 受限标识符命名净化，以及负向路径：已有文件不允许覆盖、多个 face/impl 模块对存在歧义、字段表格缺少目标表名。
- Java 类或字段表格输入如果生成 DDL 草案，必须提示用户该 DDL 是推断结果，需要 DBA/架构师确认。
- 检查 Entity、Request、Query、Service、ServiceImpl、Converter 是否符合 `references/code-generation-rules.md`，并用 `wind-project-coding-conventions` 做生成后规则审查；源码级 CR 交回 `资深架构师`，重点确认 Entity 不外露、服务接口不透传、MapStruct 不夹带业务逻辑。
- 如果写入真实项目模块，条件允许时运行受影响模块的定向 Maven 编译或测试。
- 最终向用户报告生成/修改的文件、关键假设和剩余风险；本仓库 Git 操作默认由用户执行。

生成后交接卡至少包含：

- 生成 / 修改文件、写入目录和是否覆盖既有文件。
- 输入来源、结构化字段、脚本参数和推断假设。
- 需要架构师、DBA 或业务 owner 确认的表设计、索引、枚举、金额精度、生命周期和状态机问题。
- 已执行的验证命令、结果、未执行原因和残余风险。
- 交回 AI Native / 架构师的下一步 owner、验证门禁和停止条件。

## 不适用场景

- 不在输入只有自然语言描述、缺少字段结构、表名、主键或业务模块时直接生成生产代码；此时只能生成草案或先询问关键缺口。
- 不替代架构师、DBA 或业务负责人确认表设计、索引、唯一约束、金额精度、状态机、枚举和数据生命周期。
- 不在未检查目标模块、基础包名、本地命名风格和已有文件冲突时写入真实源码目录。
- 不默认覆盖已有文件；需要覆盖时必须先说明影响范围并取得用户确认。
- 不生成绕过 `资深架构师` 编码红线的代码，包括 Java 关键字 / 保留字 / 受限标识符命名、超过 5 个公有参数、伪复用、无意义一行方法抽取、吞异常、裸日志、敏感信息泄露或模糊空值契约。
- 不把 Java 类、字段表格、JSON、OpenAPI、IDL 或数据样例推断出的 DDL 当作已确认生产 DDL；必须标记为待 DBA/架构师确认。
