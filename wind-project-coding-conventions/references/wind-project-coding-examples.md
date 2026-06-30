# Wind 项目编码最佳实践示例

本文是 `wind-project-coding-conventions` Skill 的示例参考，只在已读取 `wind-project-coding-conventions.md` 后使用，用少量正反例帮助判断服务分层、模型归属、DAL 和测试边界；它不是代码生成模板。

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

- 反例：Face Service 返回 `XxxEntity`，ApplicationService 对外方法接收 `XxxEntity`，Controller、Facade、Adapter 或事件消息 payload 直接透传 Entity；DTO/Request/Query 使用 primitive 字段表达可空或缺省。
- 正例：face Service 返回 `XxxDTO`，写入使用 `CreateXxxRequest` / `UpdateXxxRequest`，查询使用 `XxxQuery`，跨模块和消息契约使用 DTO/Command/Event；`Entity` 只在 impl / DAL / Mapper / Repository 内部流转，出边界前由 MapStruct 转换。
- 验证点：公开接口签名不得出现 Entity、Mapper、Repository 或 MyBatis `Page`；公共契约有 Javadoc、Bean Validation / JSpecify 语义明确，MapStruct 转换测试覆盖字段、枚举、空值和默认值。

### 4. 模型包归位清晰

- 反例：把 Web 页面 VO 放进 `*-face` 的 DTO 包，把业务模块私有 Request 放进 `core`，把 `domain` 当杂物包，把跨模块事件放在 impl 内部，把只给本模块用的接口提前放进 face/core，或在 web Controller 直接复用 Entity。
- 正例：业务契约模型新代码优先放 `*-face` 的 `model/dto`、`model/request`、`model/query`、`model/command`，对应 Java 包名 `*.model.dto`、`*.model.request`、`*.model.query`、`*.model.command`，历史兼容既有 `dto/request/query/command`；跨模块稳定 Service 放 `*-face/service`，完整用例契约放 `*-face/application`，回调入口和业务 SPI 放 `*-face/callback/*`；同一 face 内有多个业务子域时，用 `transaction/model/dto`、`channel/model/request`、`domain/model/dto|request` 等子包表达稳定业务语义，兼容既有 `transaction/dto`、`channel/request`、`domain/dto|request`；持久化模型放 `*-impl` 的 `dal/entities`、`dal/mapper`、`mapstruct`；业务/通道事件适配 Converter 可放 `*-impl/converter`；内部领域规则放 `*-impl/domain|domain/impl`，内部 DTO/Request/Query/Command 只能留在 impl 内部；Web VO 和登录/表单 Request 放 `web-api` / `web-security`；跨模块稳定公共能力放 `core`，技术适配和框架配置放 `infrastructure`。
- 验证点：按包名能判断模型 owner、生命周期和调用边界；移动模型时同步检查 import 方向、公共契约兼容性和 MapStruct 转换。

### 5. MyBatis Flex 查询集中表达

- 反例：Service 到处手写裸字符串字段、散落 `QueryWrapper`，排序字段直接信任外部入参。
- 正例：公开接口返回 `WindPagination<DTO>`，入参使用 `XxxQuery` 与 `WindQuery<? extends QueryOrderField>`；`ServiceImpl` 用 `MybatisQueryHelper.from(options)` 或项目 helper 创建 `QueryWrapper`，通过 `XxxNameRefs` 拼条件，再走 `MybatisQueryHelper.<Entity, DTO>query(queryWrapper).counter(mapper::selectCountByQuery).resultQueryFunc(mapper::selectListByQuery).converter(XxxConverter.INSTANCE::convertToXxxDTO).query(options)` 统一输出 DTO 分页；前置检索无结果时返回 `Pagination.empty()`。
- 验证点：单测断言查询条件、分页上限、排序白名单、selective 写库、null 更新语义、无结果分支和 Entity 到 DTO 转换。

### 6. TDD 测真实链路，不测内部表演

- 反例：mock 内部 Repository / Converter / Policy 后只验证调用次数，业务状态和持久化事实没有断言。
- 正例：ApplicationService / ServiceImpl 测试保留真实内部协作者、转换器、Repository、事务和状态变化，只替换第三方 HTTP、MQ、Redis、时间、ID、随机数等外部边界。
- 验证点：先有失败的行为测试；红变绿靠生产实现修正，不靠硬凑 fixture、放宽断言或迎合当前实现。

### 7. ServiceImpl 包位和多实现组合清晰

- 反例：新 `XxxServiceImpl` 落在 `*-impl/.../impl` 根包；同一 `XxxService` 多个实现靠 `Processor`、`Handler` 泛名区分，调用方不知道哪个是对外入口。
- 正例：face Service 实现默认落 `*-impl/.../service/impl`；多实现时保留一个主对外实现组合编排，其他实现用职责命名并通过 `@Primary`、bean name 或项目统一装配规则消除注入歧义。
- 验证点：结构守卫能发现错误包位；Spring 装配测试能证明同一 Service 的默认注入唯一且符合业务入口。

### 8. 源码样本只提炼稳定共性

- 反例：看到 nobe 有 `services/impl`、capte-domain 有 `dto/request/query` 直连包、某个模块叫 `global-face`，就把这些历史路径全部写成新项目强制模板。
- 正例：从 `wind-integration / nobe / capte-domain 源码观察` 中只提炼稳定判断：face 放公开契约，impl 放 `dal/entities`、`dal/mapper`、`mapstruct` 和实现层协作，web-api 放 Controller，core 放跨模块稳定对象，infrastructure 放技术 helper；新代码优先用 `model/dto|request|query|command`，历史项目兼容既有包名。
- 验证点：新增规则能回答“谁调用、生命周期归谁、变化 owner 在哪、依赖方向是否越界”，而不是复刻某个仓库的目录树。
