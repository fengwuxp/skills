# 项目治理：服务、API 与模型

本文从 `project-governance-standards.md` 拆出，承载服务分层、方法命名、Query/DTO 和 API 设计评审入口。通用 Java 编码细则以 `coding-standards.md` 为准。

## 使用时机

- 需要评审 Service 调用链、Entity 暴露边界、API/DTO/Query 或方法命名。
- 需要检查模型命名、Lombok/MapStruct、空值、异常、时间和金额约束。
- 项目本地 `AGENTS.md` 明确 opt-in Wind 项目编码约规时，先读 `wind-project-coding-conventions.md` 再回到本文做通用建模对照。

## 不适用场景

- 数据库、日志、安全、测试治理读 `project-governance-data-security-quality.md`。
- 单文件 Java 编码细则优先读 `coding-standards.md`。
- Wind/Nobe 风格项目的 face/impl、Processor/Executor、基础服务和分包约规优先读 `wind-project-coding-conventions.md`，不要机械套本文四类服务。

## 读取后必须产出

- 服务边界、接口契约、模型命名、兼容性风险和验证建议。

## 需要继续读取的 reference

- 深度编码规范读 `coding-standards.md`。
- 代码 Review 定级读 `coding-review-deep-dive.md`。
- Wind 项目编码约规 opt-in 时读 `wind-project-coding-conventions.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Service 分层和调用链 | 5；Wind opt-in 时先读 `wind-project-coding-conventions.md` | API 和编码细则 |
| 方法命名、Query/DTO | 6、7 | 服务层背景 |
| API 设计 | 8 | 命名细节 |
| 编码原则和模型规范 | 9 | API 细节 |

## 5. 服务层划分与调用关系

通用服务层建议优先归入以下四类；项目已有更具体的 face/impl、Processor/Executor、support 或应用层约规时，以项目规则为准，Wind opt-in 项目先读 `wind-project-coding-conventions.md`，不得为了套四类服务新增浅层透传。

| 类型 | 命名 | 职责 |
| --- | --- | --- |
| 基础服务 | `{实体}Service` | 数据访问协调、基础 CRUD、简单查询 |
| 领域写服务 | `{实体}DomainService` | 聚合规则、状态变更、领域事件 |
| 领域读服务 | `{实体}DomainQueryService` | 查询模型、列表、分页、统计 |
| 场景服务 | `{业务场景}ApplicationService` | 用例编排、事务边界、跨领域流程 |

调用链：

```text
Controller / Adapter
   ↓
ApplicationService
   ↓
DomainService       DomainQueryService
   ↓                     ↓
{实体}Service        {实体}Service
   ↓
Repository / Mapper
```

强制规则：

- `DomainService` 不得调用 `DomainQueryService`。
- `DomainQueryService` 不得调用 `DomainService`。
- 除 `{实体}Service` 外，其他 Service 不得直接访问 Repository/Mapper。
- ApplicationService 负责编排，不沉淀细粒度领域规则。
- DomainService 负责对象如何变化，不处理列表/分页查询。
- DomainQueryService 只读，不修改状态。

Entity 可以在内部领域边界流动，不能出现在 Web/API/face 对外契约、ApplicationService 对外返回或 DomainQueryService 返回模型中。

## 6. 服务方法命名

查询动词：

| 动词 | 语义 | 返回规则 |
| --- | --- | --- |
| `getXxx` | 必然存在 | 查不到抛业务异常 |
| `findXxx` | 可能不存在 | 推荐 `Optional` 或项目约定可空语义 |
| `queryXxx` | 条件查询/列表/分页 | 参数使用 `XxxQuery` |
| `existsXxx` | 是否存在 | 返回 boolean |
| `countXxx` | 数量统计 | 返回数量 |
| `statsXxx` / `summaryXxx` | 统计或汇总 | 返回统计 DTO |

写操作必须表达业务意图，例如 `submit`、`approve`、`reject`、`freeze`、`unfreeze`、`pay`、`refund`、`settle`。不要用 `handle`、`process`、`doXxx` 掩盖业务语义。

命中下列两条及以上，优先归为场景服务：跨实体/跨聚合、返回 DTO/Result、方法名是业务场景动词、流程包含权限/事务/外部调用/消息/多个领域对象编排。

## 7. Query DTO 与查询字段命名

查询字段命名使用 `<field><OperatorSuffix>`；默认等值查询不加后缀。

| 类型 | 后缀示例 |
| --- | --- |
| 集合 | `In`, `NotIn` |
| 文本匹配 | `Contains`, `StartsWith`, `EndsWith`, `Like` |
| 数值比较 | `Gt`, `Gte`, `Lt`, `Lte`, `Min`, `Max` |
| 空值 | `IsNull`, `IsNotNull` |
| 区间 | `Between` |

强制规则：

- 查询对象统一命名为 `XxxQuery`。
- 分页大小必须有最大值限制。
- 排序字段使用枚举或字段常量白名单，禁止前端直接传数据库字段名。
- 时间和数值范围统一使用 `Min/Max`，禁止同一项目混用 `Start/End`、`Begin/End`、`From/To`。
- 深分页优先使用游标分页。

## 8. API 设计规范

- Controller 只做协议适配、参数校验、权限入口和响应转换。
- Controller 不写业务规则，不访问 Repository/Mapper。
- 对外 API 入参使用 Request/Query，出参使用 DTO/VO，不暴露 Entity。
- 错误码、错误消息、HTTP 状态码或 RPC 错误契约必须统一。
- 内网 API 要显式区分低风险和高风险入口；用户数据、资金、权限、关键业务操作必须有签名、认证或等价保护。
- 外部集成 API 通过端口接口隔离厂商 SDK，并考虑超时、重试、限流、幂等、降级、告警和审计。

## 9. 编码原则和模型规范

本节只保留服务/API 建模相关原则，完整编码规则读 `coding-standards.md`。

- 类、方法、字段命名必须表达业务意图，同一业务概念只用一个术语。
- 枚举必须实现 `DescriptiveEnum` 或项目等价描述接口。
- DTO/Request/Query、配置属性、扩展点必须有 Javadoc，说明业务语义、空值、默认值、枚举和兼容语义。
- MapStruct 只做模型转换，不做业务校验、数据库查询、远程调用、权限判断、状态流转和审计写入。
- Lombok 服务可读性，不应用 `@Data` 或全量 setter 破坏领域不变量。
- 内部契约使用 JSpecify 表达 nullability；API 层模型使用 Bean Validation 表达入参约束。
- 返回集合时返回空集合，不返回 null。
- 金额必须明确币种、精度和舍入规则；时间必须明确格式、时区和精度。

## 10. 评审清单

- Service 类型是否归类正确，调用链是否越界。
- Entity 是否泄露到 API、face、ApplicationService 返回或 DomainQueryService 返回。
- 方法名是否表达业务意图，是否误用 `get/find/query`。
- Query 后缀、分页、排序和深分页是否符合项目约定。
- 外部集成是否通过端口隔离，是否有超时、重试、幂等、降级和告警。
- DTO/Request/Query、枚举、扩展点和公共 API 是否有 Javadoc 与契约测试或示例。
