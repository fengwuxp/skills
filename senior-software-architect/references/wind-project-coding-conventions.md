# Wind 项目编码约规

本文用于项目本地 `AGENTS.md` 明确标明“遵守 Wind 项目编码约规”时，约束 Java/Spring/Wind/Nobe 风格项目的设计、编码、TDD 和 CR；项目本地规则、OpenSpec/ADR、CI 与附近代码风格优先。

## 使用时机

- 项目本地 `AGENTS.md` 明确标明、任务说明或用户要求遵守 Wind 项目编码约规。
- 评审 face/impl 模块边界、基础服务、应用层服务、DTO/Request/Query/Entity、分包规则、MyBatis Flex、外部集成端口或代码生成后审查。

## 不适用场景

- 非 Java/Spring/Wind 项目先读 `language-agnostic-architecture.md`，不得强套本规约。
- 项目 `AGENTS.md`、OpenSpec、ADR、CI 或附近代码已有更具体规则时，以项目本地规则为准。

## 读取后必须产出

- 当前项目是否 opt-in；命中的模块、服务、模型、DAL、外部调用和测试规则；违反项的最小整改建议与验证方式。

## 需要继续读取的 reference

- Java/Spring/Wind 强制规则读 `coding-standards.md`；Service/API/DTO/Query 读 `project-governance-service-api-modeling.md`；测试/TDD 读 `testing.md` 和 `testing-practices.md`；模块依赖读 `project-governance-codebase-and-modules.md`；深度 CR 读 `coding-review-deep-dive.md`；需要最佳实践正反例时读 `wind-project-coding-examples.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| opt-in / 模块 / 分包 / Service / 模型 / DAL / 外部集成 / TDD-CR | 下方 `规则清单`，再按需读相关 reference | 不猜测所有 Java 项目都适用；不复制通用 Java/测试大全 |
| 最佳实践 / 示例 / 正反例参照 | `wind-project-coding-examples.md` | 不把示例当完整模板或代码生成规则 |

## 1. 启用、模块与分包

- 启用：项目本地 `AGENTS.md` 写明即可，例如“本项目遵守 Wind 项目编码约规”；启用后仍按项目 `AGENTS.md`、OpenSpec、ADR、CI、附近代码、本规约的顺序取舍。

- 模块：`*-face` 只放对外契约：`service/services`、`dto`、`request`、`query`、`enums`、`constants`；`*-impl` 放 `service/impl`、`impl`、`dal/entities`、`dal/mapper`、`mapstruct`、`support`、`configuration`；Controller 不直接访问 Mapper/Entity。

## 2. 服务层

- Face Service 是对外稳定契约，`ServiceImpl` 承接校验、状态、事务和数据访问协调；ApplicationService 只在完整用例编排、事务边界、权限/审计、跨服务协调或外部副作用明确时使用。
- 内部基础服务可以封装稳定查询或基础数据访问，但不能只是 Mapper 透传；接口、Service、Facade、Adapter 必须有真实业务职责，不新增一行 wrapper、改名转发、浅模块或似是而非抽象。
- `DomainService` / `DomainQueryService` 不是 Wind 项目强制分层；只有确有领域规则、状态变化、查询模型或统计读模型时才引入，不为套分层新增浅服务。
- 写操作用业务动词，例如 submit、approve、reject、freeze、unfreeze、pay、refund、settle；查询按 `get/find/query/exists/count/stats` 区分必然存在、可空、条件查询和统计，不用 handle/process/doXxx 掩盖语义。
- 事务边界放在真实用例边界；事务内避免不可控远程调用、长耗时计算和无上限循环，确需调用时说明超时、补偿和失败处理。

## 3. 模型与契约

- 模型：`Request` 写入命令，`Query` 查询条件，`DTO` 对外或跨模块契约，`Entity` 只表达持久化结构；Controller、face、跨模块调用和 ApplicationService 对外返回不得暴露 Entity/Mapper/Repository。
- `DTO`、`Request`、`Query`、`Response`、`Command`、`Event` 不使用 Java primitive 或 Atomic 类型承载契约字段；使用包装类型、枚举、值对象或明确业务类型表达缺省、精度和序列化语义。
- 公共接口、公有方法、DTO/Request/Query、配置属性和扩展点要有 Javadoc，说明职责、调用方、空值、异常、权限、幂等、事务和副作用；注释说明 Why / Why not，不翻译代码。
- 内部 Java 空值契约用 JSpecify；API 入参用 Bean Validation；业务前置条件和状态条件用项目断言工具。已由 JSpecify 标为非空的值，不再加无业务语义的空判断。
- 金额必须明确币种、精度和舍入规则；时间必须明确格式、时区和精度；ID 必须考虑唯一性、可追踪、并发和外部暴露风险。
- Spring Bean 优先构造注入；Lombok 只减少样板代码，不隐藏业务不变量、状态变化、副作用或敏感字段。
- MapStruct 放 `mapstruct`，命名 `XxxConverter`，方法 `convertToXxx`；只做转换和确定性派生值，不做业务校验、权限、远程调用、数据库查询、状态流转或审计。字段重命名、枚举、空值策略和默认值必须显式声明并补测试。

## 4. DAL 与外部集成

- MyBatis Flex 使用 `XxxRefs` 和统一 helper 构造 `QueryWrapper`；禁止新增 `LambdaQueryWrapper` 或裸字符串字段名；分页有上限，排序白名单，写库默认 selective。
- QueryWrapper 构造逻辑优先沉淀到 helper 或基础服务，避免到处手写条件；复杂 SQL 说明索引、分页、排序、数据量和慢查询风险。
- 需要把字段更新为 null 时，必须显式指定更新列，说明业务语义，并处理 `gmt_modified`。
- 外部调用先定义端口再写适配器；异步、Webhook、MQ、批处理和回调必须有超时、重试、幂等、补偿、告警、审计和时间边界三问。
- 生产实现：生产源码路径不得新增 `InMemoryXxxService`、`FakeXxxService`、`MockXxxService`、Map/List 存储型业务实现或进程内状态应用服务来承载真实业务能力。

## 5. 测试与 CR

- 测试验证外显行为、业务事实、接口契约、状态流转、持久化事实、SQL 条件、幂等、异常和边界；不测私有方法、内部调用顺序、临时字段、内部 Mock 交互或当前实现步骤。
- TDD 先写能失败的行为测试，再做最小实现；红变绿必须修改生产实现，不通过硬凑 fixture、放宽断言或 mock 内部步骤制造虚假绿灯。
- ApplicationService / ServiceImpl 流程测试保留真实内部协作者、转换器、策略、Repository、事务和状态变化；只替换第三方通道、远程 HTTP、MQ、Redis、时间、ID、随机数等外部边界。
- 基础服务测试重点验证 QueryWrapper、Mapper 语义、分页、排序、selective 写库、事务事实和异常语义；不要只断言调用成功或对象非空。
- MapStruct 转换测试覆盖字段完整性、枚举、空值、默认值、嵌套对象和集合转换。
- Bug 修复先补能复现失败的回归测试；新增资金、权限、审计、状态机、幂等或并发逻辑时补对应红线断言。
- 测试说明放在测试方法名、Javadoc 或方法级注释中，表达场景、输入、行为、输出和红线；测试结构优先 Given/When/Then 或 Arrange/Act/Assert。
- 完成 TDD 或 AI 生成实现后做设计质量回看：是否新增浅服务、透传接口、无主依赖、过度抽象、内部链路 mock、AI 注释噪声或只为过测试的战术实现。
- CR 检查 opt-in、face/impl、Controller、Service 职责、模型归属、Javadoc/契约、MapStruct、MyBatis Flex、外部端口、内存服务、测试层级、真实链路、替身边界和验证命令。
