# Wind 项目编码最佳实践示例

本文只在已读取 `wind-project-coding-conventions.md` 后使用，用少量正反例帮助判断服务分层、模型归属、DAL 和测试边界；它不是代码生成模板。

## 使用时机

- 用户要求 Wind 项目编码约规的最佳实践、示例、正反例或落地参照。
- AI Maker / Checker 对 ApplicationService、基础服务、DTO/Entity、MyBatis Flex 或测试替身边界拿不准。

## 不适用场景

- 项目未在本地 `AGENTS.md`、任务说明或用户要求中 opt-in Wind 项目编码约规。
- 需要生成完整 Java Service 脚手架时，交给 `java-service-code-generator`；本文件只辅助判断，不替代项目附近代码风格。

## 读取后必须产出

- 命中的示例卡、当前代码更接近反例还是正例、最小整改动作和验证点。

## 需要继续读取的 reference

- 规则原文读 `wind-project-coding-conventions.md`；Java 强规约读 `coding-standards.md`；Service/API/DTO 细节读 `project-governance-service-api-modeling.md`；测试落地读 `testing.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 最佳实践 / 正反例 / 新人或 AI Maker 纠偏 | 下方 `示例卡` | 不把示例当模板复制，不为示例新增无业务入口代码 |

## 示例卡

### 1. ApplicationService 不是透传层

- 反例：`XxxApplicationService.submit(request)` 只调用 `xxxService.submit(request)`，没有用例编排、事务边界、权限审计或外部副作用。
- 正例：只有需要把订单、支付、审计、消息、事务或外部调用编排成一个完整用例时才保留；否则直接由稳定的 Face Service / `ServiceImpl` 承接。
- 验证点：删除或合并该层后调用方语义是否不变；若不变，优先收敛浅层。

### 2. 基础服务不是 Mapper 包装

- 反例：`XxxBasicService.findById(id)` 只转发 `mapper.selectOneById(id)`，没有查询语义、分页、排序、selective 写库或异常契约。
- 正例：基础服务沉淀稳定查询、QueryWrapper helper、分页上限、排序白名单、selective 更新和基础数据访问语义。
- 验证点：测试覆盖 QueryWrapper 条件、Mapper 语义、分页/排序、事务事实和异常语义。

### 3. 模型边界不穿透

- 反例：Controller、face 或跨模块接口直接暴露 Entity，DTO/Request/Query 使用 primitive 字段表达可空或缺省。
- 正例：`Request` 表达写入命令，`Query` 表达查询条件，`DTO` 表达对外契约，`Entity` 只在 impl / DAL 内部流转。
- 验证点：公共契约有 Javadoc、Bean Validation / JSpecify 语义明确，MapStruct 转换测试覆盖字段、枚举、空值和默认值。

### 4. MyBatis Flex 查询集中表达

- 反例：Service 到处手写裸字符串字段、散落 `QueryWrapper`，排序字段直接信任外部入参。
- 正例：用 `XxxRefs` 和统一 helper 构造查询；分页有 cap，排序有白名单，复杂 SQL 说明索引、数据量和慢查询风险。
- 验证点：单测断言查询条件、分页上限、排序白名单、selective 写库和 null 更新语义。

### 5. TDD 测真实链路，不测内部表演

- 反例：mock 内部 Repository / Converter / Policy 后只验证调用次数，业务状态和持久化事实没有断言。
- 正例：ApplicationService / ServiceImpl 测试保留真实内部协作者、转换器、Repository、事务和状态变化，只替换第三方 HTTP、MQ、Redis、时间、ID、随机数等外部边界。
- 验证点：先有失败的行为测试；红变绿靠生产实现修正，不靠硬凑 fixture、放宽断言或迎合当前实现。
