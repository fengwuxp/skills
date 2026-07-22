# Wind 项目编码最佳实践示例

本文是 `wind-coding-conventions` Skill 的示例参考，只在已读取 `wind-coding-conventions.md` 后使用，用少量正反例和类型头 Javadoc 模板帮助判断服务分层、模型归属、DAL、注释和测试边界；它不是代码生成模板。

## 使用时机

- 用户要求 Wind 编码约规的最佳实践、示例、正反例、Java 类型头模板或落地参照。
- AI Maker / Checker 对 ApplicationService、基础服务、DTO/Entity、MyBatis Flex 或测试替身边界拿不准。

## 不适用场景

- 项目没有 Wind/Nobe 声明、依赖、包名、类型或模块上下文等高置信度信号。
- 需要生成完整 Java Service 脚手架时，交给 `java-service-code-generator`；本文件只辅助判断，不替代项目附近代码风格。

## 读取后必须产出

- 命中的示例卡、当前代码更接近反例还是正例、最小整改动作和验证点。

## 需要继续读取的 reference

- 规则原文读本 Skill 的 `wind-coding-conventions.md`，Java/Spring 细则读 `java-coding-conventions.md`；Service/API/DTO 通用设计和测试落地仍交 `资深架构师`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 最佳实践 / 正反例 / 新人或 AI Maker 纠偏 | 下方 `示例卡` | 不把示例当模板复制，不为示例新增无业务入口代码 |
| Java 类型头 Javadoc | 下方 `Java 类型头 Javadoc 模板` | 不批量改存量类型，不维护修改流水账 |

## Java 类型头 Javadoc 模板

```java
/**
 * 负责<核心业务职责>，边界是<不负责事项或关键约束>。
 *
 * @author <项目账号或维护团队>
 * @since <yyyy-MM-dd>
 */
public class XxxType {
}
```

- 同一模板必须紧贴在 `class`、`interface`、`record`、`enum` 或注解类型 `@interface` 声明前；类型说明写职责、边界或关键约束，不重复类型名。匿名类、局部类和工具生成代码不机械补模板。
- 泛型类型参数写 `@param <T>`，`record` 组件写 `@param componentName`；公开构造器、方法、枚举值和注解元素的参数、返回、异常及副作用继续按实际契约补充 Javadoc。
- `@author` 只填项目可核验身份，AI 不得填写自己或猜测用户名；`@since` 只记录首次引入日期，项目已统一使用发布版本时沿用版本格式。
- Git 负责修改历史；不新增 `@description`、`@date`、修改人或最后修改时间，不因普通修改刷新类型头。

## 示例卡

### 1. ApplicationService 不是透传层

- 反例：`XxxApplicationService.submit(request)` 只调用 `xxxService.submit(request)`，没有用例编排、事务边界、权限审计或外部副作用。
- 正例：只有需要把订单、支付、审计、消息、事务或外部调用编排成一个完整用例时才保留；否则直接由稳定的 Face Service / `ServiceImpl` 承接。
- 验证点：删除或合并该层后调用方语义是否不变；若不变，优先收敛浅层。

### 2. 基础服务不是 Mapper 包装

- 反例：`XxxBasicService.findById(id)` 只转发 `mapper.selectOneById(id)`，没有查询语义、分页、排序、selective 写库或异常契约。
- 正例：基础服务沉淀稳定查询、QueryWrapper helper、分页上限、排序白名单、selective 更新和基础数据访问语义。
- 验证点：测试覆盖 QueryWrapper 条件、Mapper 语义、分页/排序、事务事实和异常语义。

### 3. Mapper default 不承载业务状态机

- 反例：`UserCouponMapper.confirmLocked(...)` 用 default 方法直接更新锁定、核销、释放、退回等业务状态，`ServiceImpl` 把它当核心用例步骤调用；或把无生产调用的 `releaseXxx` 预留方法包装成服务。
- 正例：业务状态动作迁到 `*-impl/service` 的内部基础服务，例如 `UserCouponService.confirmLockedUserCoupon(...)`，实现放 `service/impl` 并在内部使用 Mapper / `UpdateChain`；无调用的预留 default 直接删除，单一低层资源占用的原子更新可暂留 Mapper。
- 验证点：先 `rg` 查调用方；Mapper 只保留 `BaseMapper`、必要自定义 SQL 或贴近 SQL 的原子条件更新；内部基础服务不暴露 Entity / QueryWrapper，测试覆盖影响行数、状态前置条件和并发幂等。

### 4. 模型边界不穿透

- 反例：Face Service 返回 `XxxEntity`，ApplicationService 对外方法接收 `XxxEntity`，Controller、Facade、Adapter 或事件消息 payload 直接透传 Entity；DTO/Request/Query 使用 primitive 字段表达可空或缺省。
- 正例：face Service 返回 `XxxDTO`，写入使用 `CreateXxxRequest` / `UpdateXxxRequest`，查询使用 `XxxQuery`，跨模块和消息契约使用 DTO/Command/Event；`Entity` 只在 impl / DAL / Mapper / Repository 内部流转，出边界前由 MapStruct 转换。
- 运行时变量反例：DTO/Context 的 `toVariables()` 调用 Supplier、Cache、当前用户或租户解析器，或先 `put(key, null)` 再由服务覆盖。
- 运行时变量正例：DTO/Context 只展开自身字段和调用方传入的扩展变量；ServiceImpl/ApplicationService 组装运行时派生变量，有值才写入变量表，测试分别锁住模型边界和服务行为。
- 验证点：公开接口签名不得出现 Entity、Mapper、Repository 或 MyBatis `Page`；公共契约有 Javadoc、Bean Validation / JSpecify 语义明确，MapStruct 转换测试覆盖字段、枚举、空值和默认值。

### 5. 模型包归位清晰

- 反例：把 Web 页面 VO 放进 `*-face` 的 DTO 包，把业务模块私有 Request 放进 `core`，把 `domain` 当杂物包，把跨模块事件放在 impl 内部，把只给本模块用的接口提前放进 face/core，或在 web Controller 直接复用 Entity。
- 正例：业务契约模型新代码优先放 `*-face` 的 `model/dto`、`model/request`、`model/query`、`model/command`，对应 Java 包名 `*.model.dto`、`*.model.request`、`*.model.query`、`*.model.command`，历史兼容既有 `dto/request/query/command`；跨模块稳定 Service 放 `*-face/service`，完整用例契约放 `*-face/application`，回调入口和业务 SPI 放 `*-face/callback/*`；同一 face 内有多个业务子域时，用 `transaction/model/dto`、`channel/model/request`、`domain/model/dto|request` 等子包表达稳定业务语义，兼容既有 `transaction/dto`、`channel/request`、`domain/dto|request`；持久化模型放 `*-impl` 的 `dal/entities`、`dal/mapper`、`mapstruct`；业务/通道事件适配 Converter 可放 `*-impl/converter`；内部领域规则放 `*-impl/domain|domain/impl`，内部 DTO/Request/Query/Command 只能留在 impl 内部；Web VO 和登录/表单 Request 放 `web-api` / `web-security`；跨模块稳定公共能力放 `core`，技术适配和框架配置放 `infrastructure`。
- 验证点：按包名能判断模型 owner、生命周期和调用边界；移动模型时同步检查 import 方向、公共契约兼容性和 MapStruct 转换。

### 6. MyBatis Flex 查询集中表达

- 反例：Service 到处手写裸字符串字段、散落 `QueryWrapper`，排序字段直接信任外部入参。
- 正例：公开接口返回 `WindPagination<DTO>`，入参使用 `XxxQuery` 与 `WindQuery<? extends QueryOrderField>`；`ServiceImpl` 用 `MybatisQueryHelper.from(options)` 或项目 helper 创建 `QueryWrapper`，通过 `XxxNameRefs` 拼条件，再走 `MybatisQueryHelper.<Entity, DTO>query(queryWrapper).counter(mapper::selectCountByQuery).resultQueryFunc(mapper::selectListByQuery).converter(XxxConverter.INSTANCE::convertToXxxDTO).query(options)` 统一输出 DTO 分页；前置检索无结果时返回 `Pagination.empty()`。
- 验证点：单测断言查询条件、分页上限、排序白名单、selective 写库、null 更新语义、无结果分支和 Entity 到 DTO 转换。

### 7. TDD 测真实链路，不测内部表演

- 反例：mock 内部 Repository / Converter / Policy 后只验证调用次数；为凑绿断言私有方法、内部调用顺序、临时字段或 Mapper 调用次数，业务状态和持久化事实没有断言。
- 正例：从 Controller / face Service / ApplicationService / ServiceImpl 的公开契约写失败测试，断言 DTO/分页结果、状态流转、持久化事实、异常、幂等、审计或可观察副作用；测试保留真实内部协作者、转换器、Repository、事务和状态变化，只替换第三方 HTTP、MQ、Redis、时间、ID、随机数等外部边界。
- 验证点：先有失败的行为测试；红变绿靠生产实现修正，不靠硬凑 fixture、放宽断言、mock 内部步骤或迎合当前实现；如果必须窥探内部才能测试，先调整服务契约或验收种子。

### 8. ServiceImpl 包位和多实现组合清晰

- 反例：新 `XxxServiceImpl` 落在 `*-impl/.../impl` 根包；同一 `XxxService` 多个实现靠 `Processor`、`Handler` 泛名区分，调用方不知道哪个是对外入口。
- 正例：face Service 实现默认落 `*-impl/.../service/impl`；多实现时保留一个主对外实现组合编排，其他实现用职责命名并通过 `@Primary`、bean name 或项目统一装配规则消除注入歧义。
- 验证点：结构守卫能发现错误包位；Spring 装配测试能证明同一 Service 的默认注入唯一且符合业务入口。

### 9. 横切控制 wrapper 隔离锁和事务

- 反例：为了“未来可能并发”直接给普通单表基础服务增加本地锁、分布式锁或 LocksWrapper；或者业务 `ServiceImpl` 一个方法里同时做参数校验、加锁、注册事务同步释放、遍历批量对象、访问 Mapper、改状态和执行业务规则。
- 正例：先证明锁的准入条件，并按不变量选择数据库保护：唯一性用业务 UK，状态流转用带旧状态的条件更新，一般读改写用版本号；普通事务不能单独防止无条件读后写的丢失更新。只有这些机制不足且有并发入口、冲突资源和失败证据时，才让 `XxxServiceLocksWrapper` 承接锁控制并委托真实业务实现；使用的平台锁必须明确持有者身份、安全释放、续期或有界执行、失锁处理以及 fencing/version 防护。
- 不提供可直接复制的固定租约锁模板；等待时间、租约和续期策略必须来自平台契约、业务执行时长证据和故障模型，不能从示例常量推导生产配置。
- 验证点：锁粒度绑定单个稳定冲突资源，不锁用户列表或对象集合；wrapper 不直接访问 Mapper、不做业务判断、不注册事务同步回调；测试覆盖并发进入、获取超时、执行超时、租约失效、安全释放和重复副作用防护。

### 10. 源码样本只提炼稳定共性

- 反例：看到 nobe 有 `services/impl`、capte-domain 有 `dto/request/query` 直连包、某个模块叫 `global-face`，就把这些历史路径全部写成新项目强制模板。
- 正例：从 `wind-integration / nobe / capte-domain 源码观察` 中只提炼稳定判断：face 放公开契约，impl 放 `dal/entities`、`dal/mapper`、`mapstruct` 和实现层协作，web-api 放 Controller，core 放跨模块稳定对象，infrastructure 放技术 helper；新代码优先用 `model/dto|request|query|command`，历史项目兼容既有包名。
- 验证点：新增规则能回答“谁调用、生命周期归谁、变化 owner 在哪、依赖方向是否越界”，而不是复刻某个仓库的目录树。

### 11. 平台基础服务模板可复用但不硬套

- 反例：为每张表生成 `create/update/delete/get/query` 全套接口，哪怕业务没有公开入口；或者把 `saveXxx`、`createXxx`、`updateXxx` 混用，调用方无法判断幂等和新增/更新语义。
- 正例：平台基础能力优先使用 `XxxService` / `XxxServiceImpl`，公开契约只暴露 `Request`、`Query`、`DTO` 和业务枚举；常见签名是 `createXxx(CreateXxxRequest) -> Long`、`updateXxx(UpdateXxxRequest)`、`deleteXxxByIds(Long... ids)`、`getXxxById(id) -> XxxDTO`、`queryXxxs(XxxQuery, WindQuery<? extends QueryOrderField>) -> WindPagination<XxxDTO>`。只有新增/更新确实统一时才用 `saveXxx(SaveXxxRequest)`，状态动作使用 `enable/disable/cancel/execute` 等业务动词。
- 验证点：`ServiceImpl` 是否只在内部接触 Entity、Mapper 和 QueryWrapper；是否用 `XxxConverter` 做边界转换；查询条件是否集中在 `createQueryWrapper/fillQueryWrapper`；是否存在无业务语义的一行 Mapper 包装。

### 12. 枚举是业务语言，不是字符串常量袋

- 反例：`String state`、`Integer type`、`String currency` 或私有魔法常量出现在 DTO、Request、Entity、事件或公开服务签名中。
- 正例：状态、类型、动作分别命名为 `XxxState`、`XxxType`、`XxxAction`，公开枚举放 face/core 的 `enums`，实现 `DescriptiveEnum` 并提供 `desc`；币种统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode`，外部字符串只在 Adapter/Converter 边界转换。
- 验证点：公共契约、Entity、MapStruct 和测试是否都使用同一枚举类型；前端展示所需的名称、颜色、树结构是否通过 DTO/Converter 输出，而不是污染业务枚举。

### 13. Query 字段命名表达语义

- 反例：`startTime`、`endTime`、`nameLike`、`statusList`、`selectByStatus` 混用，调用方不知道是闭区间、模糊匹配、集合查询还是 SQL 直译。
- 正例：默认等值不加后缀，例如 `status`；模糊用 `nameContains`；时间和金额范围用 `createdAtMin` / `createdAtMax`、`amountMin` / `amountMax`；集合用 `statusIn`；空值用 `deletedAtIsNull`。服务方法按 `get/find/query/exists/count/stats/summary` 表达存在性、条件查询和统计。
- 验证点：`XxxQuery` 字段是否只表达业务条件；Service 是否避免 `select/load/fetch`；历史 `queryXxxById` 是否只是附近代码兼容，新代码能否改成 `get/find`。

### 14. 内网 API 路径表达分类但不替代鉴权

- 反例：所有内部接口都放 `/inc/order/query`，再靠 header、备注或调用方约定区分是否需要签名；涉及资金、权限或用户数据的写操作仍走低风险路径。
- 正例：低风险内部查询走 `/inc/basic/{domain}/{resource}/{action}`；涉及用户数据、资金、权限、关键配置或业务状态变化的接口走 `/inc/secure/{domain}/{resource}/{action}`。路径只表达分类，网关或拦截器仍应默认拒绝并逐请求鉴权；`secure` 额外验证内部来源、appKey、timestamp、nonce 和 signature。
- 验证点：`basic` 是否只承载低风险能力；所有内网请求是否默认拒绝并逐请求鉴权；`secure` 是否有签名、重放防护、审计和契约测试。

### 15. 字典国际化不驱动业务逻辑

- 反例：业务判断依赖 `"已支付"`、`"Paid"` 或前端展示名称；业务事件直接保存一整句中文，历史记录随文案修改而漂移。
- 正例：业务逻辑依赖 `PaymentState.PAID`、`error.payment.order-not-found` 或 `event.payment.order-paid`；业务事件保存 `{eventKey, params}`，params 放订单号、金额、状态 code 等变量值，展示层再按语言渲染。
- 验证点：Key 是否按 `ui.`、`enum.`、`error.`、`event.`、`config.` 等命名空间区分；同一中文在不同场景是否避免复用 Key；语义变化是否新增 Key 而不是改旧 Key。

### 16. 公共契约和日志必须有真实消费方

- 反例：模块另建 `CouponOperator` 复制操作人字段；`queryCouponOverview(query, activityOptions, couponOptions)` 同时承载两套分页；为单个 `reason` 新建无校验、无复用的值对象；生成 `correlationId` 后只写库、返回或打印。日志整体打印 Request / Entity，在事务提交前宣称“已持久化提交”，或为每条普通成功日志注册事务同步；事件名已经表示失败仍固定输出 `failureStage` / `failureType`，捕获异常后只打印 `getSimpleName()` 再原样抛出。
- 正例：公共契约直接复用 `com.wind.integration.operator.WindOperator`；每个分页方法只接收一个 `WindQuery`，独立结果集拆成独立查询；操作原因留在对应 Request / Command；无人消费的 `correlationId` / `version` 删除。事务内按真实语义记录处理完成、状态更新或等待提交；只有明确依赖提交事实的审计、通知、外部副作用或日志才进入 after-commit。异常堆栈只由一个明确 owner 输出，纯字符串字面量可跨行组合，运行时值统一使用占位符。
- 验证点：操作人与查询类型是否复用现有公共契约；字段能否指出生成方和真实消费者；每个分页是否独立；成功日志是否可能早于回滚；日志维度是否被告警、统计或检索消费；同一异常是否只有一份完整堆栈。
