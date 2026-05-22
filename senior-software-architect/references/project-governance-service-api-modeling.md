# 项目治理：服务、API 与模型

本文从 `project-governance-standards.md` 拆出，承载服务分层、方法命名、Query/DTO、API 设计和编码原则。

## 使用时机

- 需要评审 Service 调用链、Entity 暴露边界、API/DTO/Query 或方法命名。
- 需要检查编码原则、模型命名、Lombok/MapStruct、空值、异常、时间和金额约束。

## 不适用场景

- 数据库、日志、安全、测试治理读 `project-governance-data-security-quality.md`。
- 单文件 Java 编码细则优先读 `coding-standards.md`。

## 读取后必须产出

- 服务边界、接口契约、模型命名、兼容性风险和验证建议。

## 需要继续读取的 reference

- 深度编码规范读 `coding-standards.md`。
- 代码 Review 定级读 `coding-review-deep-dive.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Service 分层和调用链 | 5 | API 和编码细则 |
| 方法命名、Query/DTO | 6、7 | 服务层背景 |
| API 设计 | 8 | 命名细节 |
| 编码原则和模型规范 | 9 | API 细节 |

## 5. 服务层划分与调用关系

### 5.1 四类 Service

服务层只允许以下四类：

| 类型 | 命名 | 职责 | 返回模型 |
|------|------|------|----------|
| 基础服务 | `{实体}Service` | 数据访问协调、基础 CRUD、简单查询 | Entity/DTO/Optional |
| 领域写服务 | `{实体}DomainService` | 聚合规则、状态变更、领域事件 | Entity/基本类型/void |
| 领域读服务 | `{实体}DomainQueryService` | 查询模型、列表、分页、统计 | DTO/VO/Page/List |
| 场景服务 | `{业务场景}ApplicationService` | 用例编排、事务边界、跨领域流程 | DTO/Result/void |

禁止新增含义模糊的类型：`Manager`、`Facade`、`BizService`、`HandlerService` 等，除非它是明确的基础设施或框架扩展点，并在设计文档中说明。

### 5.2 调用链

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

### 5.3 Entity 暴露边界

为明确 Entity 使用边界，统一规定：

- **Controller / Web API / face/api 对外契约禁止暴露 Entity**。
- **ApplicationService 对外返回 DTO/VO/Result，不返回 Entity**。
- **DomainQueryService 返回 DTO/VO，不返回 Entity**。
- **DomainService 和基础 `{实体}Service` 可在模块内部返回 Entity**，但不得跨边界泄露到 Web/API。

一句话：Entity 可以在内部领域边界流动，不能出现在对外接口边界。

## 6. 服务方法命名

### 6.1 查询动词

| 动词 | 语义 | 返回 | 规则 |
|------|------|------|------|
| `getXxx` | 必然存在 | Entity/VO/DTO | 查不到抛业务异常，不返回 Optional |
| `findXxx` | 可能不存在 | Optional/可空 VO | 查不到是正常情况 |
| `queryXxx` | 条件查询/列表/分页 | List/Page/Pagination | 参数使用 `XxxQuery` |
| `existsXxx` | 是否存在 | boolean | 不抛不存在异常 |
| `countXxx` | 数量统计 | long | 返回数量 |
| `statsXxx` | 统计 | DTO | 多指标统计 |
| `summaryXxx` | 汇总 | DTO | 汇总视图 |

禁止：

- `getXxxList`、`findXxxPage`、`queryXxx` 返回单个必然存在对象。
- 服务层使用 Repository 语义：`select`、`fetch`、`load`。
- 查询方法使用多个散装参数，除非只有唯一标识条件。

### 6.2 写操作动词

领域写服务只允许使用业务变更动词：

```text
create / update / save
bind / unbind
submit / approve / reject
freeze / unfreeze
enable / disable
close / cancel
pay / refund / settle
```

写方法必须表达业务意图，不要用 `handle`、`process`、`doXxx` 这类模糊词。

### 6.3 实体型与场景型判定

- 回答“对象怎么变” → `DomainService`。
- 回答“业务怎么走” → `ApplicationService`。

命中下列两条及以上，优先归为场景服务：

- 跨实体/跨聚合。
- 返回 DTO/Result。
- 方法名是业务场景动词，如 login、pay、submit。
- 流程中包含权限、事务、外部调用、消息或多个领域对象编排。

## 7. Query DTO 与查询字段命名

### 7.1 基本规则

查询字段命名使用：

```text
<field><OperatorSuffix>
```

默认等值查询不加后缀：

```text
status       -> status = ?
name         -> name = ?
```

语义优先于 SQL，推荐使用业务语义后缀，不直接表达 SQL 细节。

### 7.2 标准后缀

| 类型 | 后缀 | 示例 |
|------|------|------|
| 不等于 | `Ne` | `statusNe` |
| 包含集合 | `In` | `statusIn` |
| 不包含集合 | `NotIn` | `statusNotIn` |
| 包含匹配 | `Contains` | `nameContains` |
| 前缀匹配 | `StartsWith` | `codeStartsWith` |
| 后缀匹配 | `EndsWith` | `emailEndsWith` |
| 自定义 LIKE | `Like` | `nameLike` |
| 大于 | `Gt` | `amountGt` |
| 大于等于 | `Gte` | `amountGte` |
| 小于 | `Lt` | `amountLt` |
| 小于等于 | `Lte` | `amountLte` |
| 最小值，含边界 | `Min` | `createdAtMin` |
| 最大值，含边界 | `Max` | `createdAtMax` |
| 区间 | `Between` | `createdAtBetween` |
| 为空 | `IsNull` | `deletedAtIsNull` |
| 非空 | `IsNotNull` | `deletedAtIsNotNull` |

时间和数值范围统一使用 `Min/Max`，禁止同一项目混用 `Start/End`、`Begin/End`、`From/To`。

### 7.3 Query 对象规则

- 查询对象统一命名为 `XxxQuery`。
- 分页查询继承统一分页基类。
- 分页大小必须有最大值限制。
- 排序字段使用枚举或字段常量白名单，禁止前端直接传数据库字段名。
- 排序参数统一为 `orderFields` + `orderTypes`。
- 深分页优先使用游标分页。

## 8. API 设计规范

### 8.1 Web API

- Controller 只做协议适配、参数校验、权限入口和响应转换。
- Controller 不写业务规则，不访问 Repository/Mapper。
- 对外 API 返回统一响应模型，必须包含 traceId。
- API 入参使用 Request/Query，不直接接收 Entity。
- API 出参使用 DTO/VO，不直接返回 Entity。
- 错误码、错误消息、HTTP 状态码或 RPC 错误契约必须统一。

### 8.2 内网 API

内网 API 路径统一：

```text
/inc/{security-level}/{domain}/{resource}/{action}
```

安全等级：

| 前缀 | 用途 | 策略 |
|------|------|------|
| `/inc/basic/**` | 低风险内网基础接口 | 仅限内网访问，可不验签 |
| `/inc/secure/**` | 用户数据、资金、权限、关键业务操作 | 内网访问 + 强制接口验签 |
| `/api/**` | 公网 API | OAuth/Token/Session 等公网认证 |

强制规则：

- `/inc` 只允许内网调用，禁止公网暴露。
- `/inc/secure/**` 必须校验 appKey、timestamp、nonce、signature。
- 安全等级由路径表达，不依赖 Header 或参数临时判断。
- 网关、拦截器、AOP 至少一层强制执行安全策略。

### 8.3 外部集成 API

- 业务代码依赖端口接口，例如 `WindOssClient`、`WindCryptoClient`、`MessageSender`。
- 厂商 SDK 封装在 infrastructure 或独立 adapter 模块。
- 外部调用必须考虑超时、重试、限流、幂等、降级、告警和审计。
- 对外部异常进行包装，不向业务层泄露 SDK 原始异常。

## 9. 编码原则

### 9.1 命名

- 类名使用 `UpperCamelCase`，方法/变量使用 `lowerCamelCase`，常量使用 `UPPER_UNDERSCORE`。
- 禁止拼音、中文、无意义缩写。
- 名称表达业务意图，不表达实现细节。
- 设计模式参与命名时应体现模式，如 `XxxStrategy`、`XxxFactory`、`XxxAdapter`。
- 枚举必须实现 `DescriptiveEnum` 或等价描述接口。
- 同一业务概念必须使用同一术语，禁止同义词混用，例如 account、wallet、balance 未定义前不得混用。
- 禁止使用过宽词汇掩盖职责，例如 `handle`、`process`、`manager`、`data`、`info`、`logic`。

### 9.2 模型命名

| 类型 | 命名 |
|------|------|
| 创建请求 | `CreateXxxRequest` |
| 更新请求 | `UpdateXxxRequest` |
| 不区分创建/更新 | `SaveXxxRequest` |
| 命令对象 | `XxxCommand` |
| 查询对象 | `XxxQuery` |
| DTO | `XxxDTO` / `XxxDetailDTO` / `XxxListDTO` |
| VO | `XxxVO` |
| 事件 | `XxxEvent` |
| 转换器 | `XxxConverter` |

MapStruct 方法命名：`convertToXxx`、`convertToXxxDTO`、`convertToEntity`。

### 9.3 Lombok 与 MapStruct 使用边界

Lombok 和 MapStruct 是团队可使用的工程提效工具，但它们必须服务可读性、边界清晰和转换一致性，不能成为隐藏业务语义的黑盒。

Lombok 使用规则：

- 简单数据载体（DTO、VO、Query、Command、Event、配置属性）可使用 `@Getter`、`@Setter`、`@NoArgsConstructor`、`@AllArgsConstructor`、`@Builder`。
- 领域对象、聚合根、状态机对象、有业务不变量的类，不使用 `@Data` 和全量 `@Setter`；应通过有语义的方法表达状态变化。
- Entity 使用 Lombok 时必须谨慎处理 `equals`、`hashCode`、`toString`，避免把数据库 ID、懒加载关联、大字段或敏感字段带入默认实现。
- Spring Bean 推荐使用 `final` 依赖字段 + `@AllArgsConstructor` 做构造器注入；禁止字段注入，禁止为了省代码牺牲依赖显式性。
- 当 Bean 中存在非依赖状态、可选依赖或特殊构造逻辑时，应改用显式构造器并说明原因，避免 `@AllArgsConstructor` 把非依赖字段错误纳入注入契约。
- 对外契约类即使使用 Lombok，也必须通过字段命名、Javadoc、校验注解和测试说明空值、默认值、枚举和兼容语义。

MapStruct 使用规则：

- 转换器放在 `mapstruct` 包或项目既有等价转换包中，命名为 `XxxConverter`，方法命名遵循 `convertToXxx`、`convertToXxxDTO`、`convertToEntity`。
- MapStruct 只做模型转换，不做业务校验、数据库查询、远程调用、权限判断、状态流转和审计写入。
- 字段名不同、语义不同、类型不同、枚举转换、默认值、空值处理、忽略字段必须显式使用 `@Mapping` 或配置说明。
- 更新已有对象时必须明确 null 处理策略，避免把源对象的 null 意外覆盖到目标对象。
- 关键转换必须有单元测试，覆盖字段完整性、枚举、空值、默认值、嵌套对象和集合转换。
- 禁止在核心业务路径混用 MapStruct、`BeanUtils`、反射拷贝和手写拷贝，确需混用时必须说明原因并控制范围。

### 9.4 函数与类

- 方法短小，只做一件事。
- 参数超过 5 个必须抽取参数对象；公共方法超过 3 个参数应优先考虑参数对象。
- 函数内抽象层级一致，不把校验、查询、转换、持久化、通知揉在一起。
- 类职责单一，避免上帝类。
- 优先组合而非继承。
- 公共 API 必须有 Javadoc，说明意图、参数约束、返回语义和异常。

### 9.5 注释与技术表达

代码注释和技术文档是系统可维护性的一部分，必须服务理解和协作。

强制规则：

- 公共接口、公有方法、DTO/Request/Query、配置属性、扩展点必须有 Javadoc。
- 注释说明“为什么这样做、边界是什么、风险是什么”，不重复代码显而易见的行为。
- 复杂规则必须给出业务语义、输入输出、边界条件和示例。
- 临时方案必须标注原因、影响范围、替代方案或计划清理时间。
- 禁止保留大段注释掉的废弃代码。

推荐表达：

```java
/**
 * 查询用户明细。
 *
 * <p>用于后台用户详情页。用户不存在或已逻辑删除时抛出业务异常。
 *
 * @param userId 用户 ID
 * @return 用户明细
 */
UserDetailDTO getUserDetail(Long userId);
```

表达原则：

- 先讲业务语义，再讲技术实现。
- 主语、动作、对象、条件、结果必须明确。
- 中文说明追求短、准、稳，避免空泛词。
- 中英文混排保持一致，技术词不硬翻，业务词不乱拼音。

### 9.6 空值与断言

- 不会暴露到 API 层的内部服务、领域服务、应用服务和端口契约，使用 `org.jspecify.annotations` 相关注解表达 nullability。
- 会暴露到 API 层的参数、Request/Response/DTO/Query/Command 等数据模型，使用 `javax.validation` 的 `@NotNull`、`@NotBlank`、`@NotEmpty` 等 Bean Validation 注解；项目已迁移 Jakarta EE / Spring Boot 3+ 时，使用 `jakarta.validation` 等价注解。
- 已由 JSpecify 标注为非空的普通参数、返回值和字段，不再重复写无业务语义的空判断。
- 其他业务前置条件、状态条件、不可达分支和内部防御式编程，优先使用项目统一的 `AssertUtils`。
- 返回集合时返回空集合，不返回 null。
- `findXxx` 推荐返回 `Optional<T>`。
- `getXxx` 查不到必须抛业务异常。

### 9.7 异常

- 业务异常继承或使用 `BaseException`。
- 异常必须携带错误码或可归类的异常类型。
- 禁止吞异常。
- 事务方法中捕获异常后必须重新抛出或显式回滚。
- 包装第三方异常时保留 cause。
- 对用户提示和内部诊断信息分层处理。

### 9.8 时间与金额

- 时间使用 `LocalDateTime`、`LocalDate`、`LocalTime`，禁止新代码使用 `Date`。
- 默认前后端格式：`yyyy-MM-dd HH:mm:ss`、`yyyy-MM-dd`、`HH:mm:ss`。
- 金额使用 `BigDecimal`，禁止 `new BigDecimal(double)`。
- 金额字段必须明确币种、精度、舍入规则。
