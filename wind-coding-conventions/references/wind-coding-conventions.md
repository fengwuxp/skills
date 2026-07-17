# Wind 编码约规

本文是 `wind-coding-conventions` Skill 的 Wind 专项规则。只有入口 Skill 根据项目 `AGENTS.md`、任务说明、依赖坐标、包名/import、Wind 类型或模块上下文判定命中 Wind/Nobe 后才读取；项目本地规则、OpenSpec/ADR、CI 与附近代码风格优先。

## 使用时机

- 项目本地 `AGENTS.md`、任务说明或用户明确要求遵守 Wind 编码约规。
- Maven/Gradle 依赖、包名/import、Wind 类型或模块上下文提供 Wind/Nobe 高置信度信号。
- 评审 face/impl 模块边界、接口放置、基础服务、方法签名、服务/模型/枚举命名、应用层服务、DTO/Request/Query/Entity、查询字段命名、内网 API、安全等级、系统字典/国际化、模型包归位、分包规则、MyBatis Flex、外部集成端口或代码生成后审查。
- 初始化或改进遵循 Wind 约规项目的本地 `AGENTS.md`，让 知止者能按项目规则调度产品、架构、Wind 规则和代码生成能力。

## 不适用场景

- 非 Java/Spring/Wind 项目先读架构师 `references/language-agnostic-architecture.md`，不得强套本规约。
- 项目 `AGENTS.md`、OpenSpec、ADR、CI 或附近代码已有更具体规则时，以项目本地规则为准。

## 读取后必须产出

- 当前项目命中的 Wind/Nobe 上下文证据；命中的模块、接口、服务、模型、DAL、外部调用和测试规则；违反项的最小整改建议与验证方式。

## 需要继续读取的 reference

- Java/Spring 编码细则读本 Skill 的 `java-coding-conventions.md`；Wind 项目族端口、Starter、Trace、安全和企业集成模式读 `wind-architecture-patterns.md`；Service/API/DTO/Query 的通用设计、测试/TDD、模块依赖和深度源码 CR 仍交 `资深架构师`；需要最佳实践正反例时读 `wind-coding-examples.md`。

重复规则归位：所有 Java 项目的通用编码细则归 `java-coding-conventions.md`；命中 Wind/Nobe 后的 face/impl、模型包位、基础服务模板、查询方法语义、`XxxQuery` 后缀、内网 API 路径安全等级、系统字典/国际化和业务事件 Key 归本文件；通用架构、源码级 CR、调试、测试策略和生产风险归 `资深架构师`。有冲突时，项目本地 `AGENTS.md` / OpenSpec / ADR 优先，其次才是已命中的 Wind 项目特化规则。

专项启用分三层：

| 层级 | 启用条件 | 规则示例 |
| --- | --- | --- |
| Wind 通用专项 | 已命中 Wind/Nobe 高置信度信号 | face/impl、Entity 不外露、服务与模型边界；出现币种字段时无条件统一使用 `CurrencyIsoCode` |
| 依赖专项 | 对应依赖、import 或源码上下文存在 | JSpecify、Bean Validation、Lombok、MapStruct、MyBatis Flex |
| 项目数据库专项 | 项目 `AGENTS.md`、既有 schema 或数据库约规已采用对应 Wind MySQL 表约规 | `id`、`gmt_create`、`gmt_modified` 等字段与类型 |

不得为了启用依赖专项新增依赖；但 `CurrencyIsoCode` 是 Wind 币种契约本身，当前模块不能引用时应修正模块依赖或契约归属，不得退回 `String`、整数或业务私有币种枚举。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Wind 声明 / 项目 AGENTS 初始化或改进 | `wind-project-agents-template.md`，再按本地项目事实填充 | 不猜测构建命令、生产流程、模块事实或团队授权 |
| 模块 / 分包 / 接口放置 / 模型包归位 / Service / 基础服务模板 / 方法签名 / 查询命名 / 内网 API / 字典国际化 / DAL / 外部集成 / TDD-CR | 下方 `规则清单`，再按需读相关 reference | 不猜测所有 Java 项目都适用；不复制通用 Java/测试大全 |
| 最佳实践 / 示例 / 正反例参照 | `wind-coding-examples.md` | 不把示例当完整模板或代码生成规则 |
| Java/Spring 编码、契约、异常日志、数据库和安全 | `java-coding-conventions.md` | 不把通用项目本地规则改写成 Wind 默认 |
| Wind 项目族端口、Starter、Trace、安全和企业集成模式 | `wind-architecture-patterns.md` | 不把公开项目样本当当前项目事实 |

## 1. 启用、模块与分包

- 启用：项目本地 `AGENTS.md` 明确声明是最强信号；明确的 Wind/Nobe 依赖坐标、包名/import、Wind 类型或项目族上下文也可启用。启用后仍按项目 `AGENTS.md`、OpenSpec、ADR、CI、附近代码、本规约的顺序取舍。

- 源码观察边界：本规约已抽样对照 `wind-integration / nobe / capte-domain 源码观察`，提炼的是稳定共性，不把某个仓库的历史包名、业务模块名或临时实现照搬成强制规则；具体项目仍以本地 `AGENTS.md`、附近代码和 CI 为准。

- 放置四问：先问谁调用、生命周期归谁、变化 owner 在哪、依赖方向是否越界。对外或跨模块调用进 `*-face`；模块内部实现进 `*-impl`；Web 展示和入口进 `web-api` / `web-security`；跨模块稳定公共能力进 `core`；技术适配和框架配置进 `infrastructure`。依赖 Web/DAL/第三方 SDK/具体框架实现的类型不得进入 face/core。

- 模块：`*-face` 只放对外契约：`service/services`、必要的 `application` 契约、`model/dto`、`model/request`、`model/query`、`model/command`、`enums`、`constants`、明确需要跨模块消费的 `event`，以及回调入口、扩展点或业务 SPI 的 `callback/spi`、`callback/request`、`callback/service`；历史兼容场景允许继续使用既有 `dto`、`request`、`query`、`command` 包。同一 face 有多个业务子域时，可按业务名继续分包，例如 `transaction/model/dto`、`channel/model/request`、`domain/model/dto`、`domain/model/request`，兼容既有 `transaction/dto`、`channel/request`、`domain/dto`、`domain/request`，但 `domain` 必须表示稳定业务语义，不得作为杂物包。`*-impl` 放内部 `service` / `service/impl`、`application/impl`、`domain` / `domain/impl`、`impl`、`dal/entities`、`dal/mapper`、`mapstruct`、业务/通道 `converter`、`support`、`configuration`、`listener`、`webhook` 和内部枚举；`*-impl` 一般不放对外 DTO/Request/Query/Command，除非是实现层内部模型且不对外暴露。`web-api` / `web-security` 放 Controller、Web VO、Web 登录/表单 Request 和 Web 层 Converter。`core` 放跨模块稳定基础契约、值对象、枚举、事件、上下文、规则、告警、缓存兑换、操作人等公共能力，不放业务模块私有 DTO/Request/Query/Command/Entity、Web VO、Mapper/Repository 或具体业务实现。`infrastructure` 放消息发送、KMS、MyBatis Flex helper、通用工具和框架配置等技术适配，不放业务契约、Controller、业务 Service 或业务 Entity。Controller 不直接访问 Mapper/Entity。

- 包名判断：源码样本中 `*-face` 常见 `service/services`、`application`、`dto|model/dto`、`request|model/request`、`query|model/query`、`event`、`callback/spi`；`*-impl` 常见 `service/impl`、`application/impl`、`dal/entities`、`dal/mapper`、`mapstruct`、`converter`、`listener`、`webhook`；`web-api` 常见 `controller`；`core` 常见跨模块 `enums`、`event`、`context`、`operator`；`infrastructure` 常见 `dal` helper、外部技术 adapter 和 framework config。新代码优先按这些 owner 放置，不把 web、dal、第三方 SDK 或具体实现依赖上推到 face/core。

- capte-domain platform 样本补充：`platform/*-face` 中稳定出现 `service`、`dto`、`request`、`query`、`enums`、`task`，`platform/*-impl` 中稳定出现 `service/impl`、`dal/entities`、`dal/mapper`、`mapstruct`、`configuration`、`notification`；这说明历史项目可沿用直连 `dto/request/query/enums` 包，但不改变新代码优先 `model/*` 的规则。

## 2. 服务层

- Face Service 是对外稳定契约，`ServiceImpl` 承接校验、状态、事务和数据访问协调；ApplicationService 只在完整用例编排、事务边界、权限/审计、跨服务协调或外部副作用明确时使用。若 ApplicationService 作为对外用例契约出现，接口放 `*-face/application`，实现放 `*-impl/application/impl`，签名仍只用 Request/DTO/Query/值对象。
- 接口落位：跨模块稳定业务能力放 `*-face/service`；完整用例契约才放 `*-face/application`；回调入口、扩展点和业务 SPI 放 `*-face/callback/*`；只被本模块实现层使用的接口留在 `*-impl/service`、`*-impl/domain` 或 `*-impl/support`，不因“可能复用”放进 face/core。
- 服务层接口先按调用方契约设计：face Service 和跨模块接口只暴露 `DTO`、`Request`、`Query`、`Command`、枚举或值对象，不暴露 `Entity`；`ServiceImpl` 可在内部读取和更新 `Entity`，但不得把 `Entity` 透传给 Controller、face、ApplicationService 对外方法、Facade、Adapter 或其他域。
- 包位：新代码的 face Service 生产实现默认放 `*-impl/.../service/impl`；`*-impl/.../impl` 根包只作为历史兼容或附近代码已有明确约定时保留，不作为新 ServiceImpl 默认落点。
- 基础服务落位：被其他模块、组合 Service 或外部适配层稳定消费时，接口放 `*-face/service`；只封装本 impl 内 Mapper、QueryWrapper 或内部状态流转时，留在 `*-impl/service`；只是 Mapper 透传时不应新增服务。
- 内部基础服务可以封装稳定查询或基础数据访问，但不能只是 Mapper 透传；接口、Service、Facade、Adapter 必须有真实业务职责，不新增一行 wrapper、改名转发、浅模块或似是而非抽象。
- 服务、接口、策略、工厂、状态机、规则层和配置化必须来自真实变化轴：业务规则、状态行为、外部通道、平台差异或技术选型已有来源、owner、验收样例和测试边界时才封装；只有“未来可能”的变化先保留显式代码，不为套设计模式新增浅服务或单实现抽象。
- 组合服务、生命周期服务、应用层服务和外部适配层优先依赖实体对应的基础服务或稳定 face Service，不直接拿多个 Entity Mapper 拼业务流程；若对应基础服务缺少必要读写能力，先补强基础服务签名和 DTO/Request/Query，再改调用方。只有实体自身基础服务实现、贴近 SQL 的内部 helper 或确有性能/批量原因并有测试说明时，才直接依赖 Mapper。
- Mapper default 方法只适合承载贴近 SQL 的 MyBatis Flex 原子条件更新或小型查询组合；一旦方法表达业务状态转换，或被 `ServiceImpl` 当作核心用例步骤调用，应迁到 `*-impl/service` 内部基础服务，由 `*-impl/service/impl` 依赖 Mapper / `UpdateChain` 实现。迁移前先 `rg` 查调用方：无生产调用的预留 default 直接删除，不包装成服务；只有单一调用且仍是低层资源占用的原子更新，可暂留 Mapper，等出现多个稳定调用方再提服务。
- 基础服务通用模板：公开基础服务命名为 `XxxService`，实现为 `XxxServiceImpl`；创建用 `createXxx(CreateXxxRequest)` 返回 `@NonNull Long`，创建/更新统一入口才用 `saveXxx(SaveXxxRequest)`；更新用 `updateXxx(UpdateXxxRequest)` 返回 `void`；删除用 `deleteXxxByIds(@NonNull Long... ids)`，单删可提供 `default deleteXxxById(id)` 代理；必然存在查询用 `@NonNull XxxDTO getXxxById(id)`，可能不存在查询用 `findXxx...` 并显式 `@Nullable`；分页查询用 `WindPagination<XxxDTO> queryXxxs(XxxQuery query, WindQuery<? extends QueryOrderField> options)`；非分页列表查询只在业务确需时提供 `List<XxxDTO> get/queryXxxs(XxxQuery query)`；状态动作使用明确业务动词，例如 `enable/disable/cancel/execute`，不得用泛化 `handle/process/doXxx`。
- 基础服务公开签名不得使用 Entity、Mapper、QueryWrapper；入参按 Create/Update/Query/业务动作 Request 或业务标识，出参用 DTO、分页或明确结果对象。实现层可私有读取 Entity，但离开 `*-impl/service/impl` 前必须完成转换。
- ServiceImpl 通用实现：`@Service` + 构造注入，Mapper 字段 `final`；Request 先经 `XxxConverter.INSTANCE.convertToXxx` 转 Entity；新增优先 `insertSelective`，保存类入口可用 `insertOrUpdateSelective`。更新不机械执行“先查再写”：只确认存在时直接更新并校验影响行数，状态流转使用带旧状态的条件更新，一般读改写使用版本号乐观锁；只有业务规则、审计或返回契约确实需要旧值时才读取，并同时提供并发保护。删除先校验 ids 非空和影响行数；查询条件集中在 `createQueryWrapper` 或 `fillQueryWrapper`，使用 `MybatisQueryHelper.from(options)`、`XxxNameRefs`、`counter`、`resultQueryFunc`、`converter` 输出 DTO。
- 查询服务形态：公开查询接口优先返回 `DTO` 或 `WindPagination<DTO>`，查询选项使用 `WindQuery<? extends QueryOrderField>` 或项目既有分页选项；`ServiceImpl` 内部再组合 `QueryWrapper`、Mapper、Converter 和 result enricher。默认方法只用于复用已有公开契约上的小型断言或组合查询，不新增绕过实现层的业务状态。
- 多实现组合：同一 face Service 有多个生产实现时，保留一个主对外实现做组合编排，其他实现必须承担清晰业务职责；通过 `@Primary`、明确 bean name 或项目统一装配规则解决注入歧义，不用 `Processor`、`Handler` 这类泛名掩盖服务职责。
- 横切控制 wrapper：普通一行转发 wrapper 不应新增；但分布式锁、幂等、鉴权、审计、灰度、限流、通道适配等横切控制逻辑可以用 wrapper 隔离。wrapper 应实现同一 face Service，内部委托真实业务实现；默认入口通过 `@Primary`、明确 bean name 或项目统一装配规则确定。真实业务 `ServiceImpl` 仍实现原接口，并保留业务规则、状态流转、声明式事务和持久化协调，不把横切控制细节混入业务主流程。
- 四类服务是判断框，不是强制新增层：`XxxService` 承接基础契约，`XxxDomainService` 承接真实领域写规则，`XxxDomainQueryService` 承接真实领域读模型，`XxxApplicationService` 承接完整业务场景编排。`DomainService` / `DomainQueryService` 不是 Wind 项目强制分层；没有稳定领域规则、读写分离、跨对象场景、事务/权限/审计/外部副作用时，不新增 DomainService、DomainQueryService 或 ApplicationService；已有 `service/services/application/domain` 历史包名时，以职责、owner、生命周期和调用边界判断，不为迁移名称而改。
- 新服务命名避免 `Manager`、`BizService`、泛化 `Facade` 这类职责不明后缀；若项目已有 Adapter/Facade 边界，必须表示协议适配或门面入口，不得作为服务层杂物筐。
- 写操作用业务动词，例如 submit、approve、reject、freeze、unfreeze、pay、refund、settle；不用 handle/process/doXxx 掩盖语义。
- 查询方法命名：`get` 表示必然存在，找不到抛业务异常；`find` 表示可能不存在，返回 `@Nullable` 或 `Optional` 并写清空值契约；`query` 表示条件查询、列表、分页或统计，入参优先 `XxxQuery`，不要散落多个查询参数；`exists`、`count`、`stats/summary` 分别表示存在性、数量、统计/汇总。服务层不得使用 `select/load/fetch` 这类 Repository/SQL 语义；历史 `queryXxxById` 仅在附近代码已经统一使用时兼容，新代码优先按 `get/find` 表达是否必然存在。
- 事务边界放在真实用例边界；事务内避免不可控远程调用、长耗时计算和无上限循环，确需调用时说明超时、补偿和失败处理。
- 并发控制准入：基础服务必须识别并发下的业务不变量，但不得仅因“未来可能并发”预埋 `synchronized`、本地锁、分布式锁或锁 Wrapper。先区分唯一性、状态流转和一般读改写，分别优先使用表内业务 UK 或联合 UK、带前置状态的原子条件更新和乐观锁。事务只保证本地操作的原子提交和回滚；普通 `SELECT -> Java 校验 -> UPDATE` 即使使用 `@Transactional` 也不能单独防止丢失更新。只有这些机制不足以保护已确认业务不变量，并有明确并发入口、冲突资源、失败场景、测试或生产证据时才引入锁；没有证据时删除预埋锁。
- 分布式锁和事务边界分开：确需锁时放在用例、wrapper、adapter 或基础设施冲突边界，业务 `ServiceImpl` 仍用声明式事务表达本地一致性。只使用已验证持有者身份、安全释放、租约续期或有界执行语义的平台原语，并说明等待超时、业务执行超时、失锁处理以及 fencing token 或数据库版本检查；锁粒度绑定单个稳定冲突资源，不锁对象集合。没有平台契约和时长证据时，不给出可直接复制的固定等待/租约常量模板。

## 3. 模型与契约

- 模型：`Request` 写入命令，`Query` 查询条件，`DTO` 对外或跨模块契约，`Entity` 只表达持久化结构。Controller、face Service、ApplicationService 对外方法、Facade、Adapter、跨模块接口、事件/消息契约不得以 Entity、Mapper、Repository 或 MyBatis `Page` 作为入参、返回值或泛型；离开 `*-impl` 边界前必须转换为 `DTO`、`Request`、`Query`、`Command`、`Event` 或值对象。
- 模型对象职责：DTO、Request、Query、Command、Context 只表达契约字段、输入范围和确定性自有派生；不得依赖 Service、Supplier、Cache、当前用户/租户解析器、远程端口或数据库查询。规则变量、租户名称、当前操作者等运行时派生值由 ServiceImpl、ApplicationService 或 Adapter 在用例边界组装，有值才写入变量上下文，不写无业务语义的 `null` 占位。
- 模型包归位：新代码的 `DTO`、`Request`、`Query`、`Command` 优先放在 `*-face` 或 `core` 的 `model/dto`、`model/request`、`model/query`、`model/command` 下，对应 Java 包名通常是 `*.model.dto`、`*.model.request`、`*.model.query`、`*.model.command`；历史兼容场景允许继续使用既有 `dto`、`request`、`query`、`command` 包，对应 `*.dto`、`*.request`、`*.query`、`*.command`。业务模块自己的 `enums`、`event` 优先放在对应 `*-face` 的业务包下；同一 face 内多个子域可用 `xxx/model/dto`、`xxx/model/request`、`xxx/model/query`、`xxx/event` 分包，兼容既有 `xxx/dto`、`xxx/request`、`xxx/query`、`domain/dto|request`，其中 `domain` 仅用于跨子域、稳定业务概念，不得当杂物包。持久化 `Entity`、Mapper、Repository、MyBatis `Refs` 和 MapStruct Converter 放在对应 `*-impl` 的 `dal/*` 或 `mapstruct` 下；`*-impl` 一般不放 DTO/Request/Query/Command，除非是内部模型且不进入 Controller、face Service、ApplicationService 对外方法、Facade、Adapter、事件/消息或跨模块接口。业务/通道事件 Converter 可放 `*-impl` 的 `converter` 或 `support`，但只做适配转换，不承载公共契约或核心业务决策。Web 展示 VO、登录/表单 Request 和页面组合模型放 `web-api` / `web-security`，不得回流到 face 契约；跨域共享模型只有在两个以上业务模块稳定复用且不依赖 Web/DAL 时，才放 `core` 的 `model`、`enums` 或 `event`。
- 模型命名：对外读模型用 `XxxDTO`；写入模型按语义用 `CreateXxxRequest`、`UpdateXxxRequest`、`SaveXxxRequest`、`ExecuteXxxRequest`，只有确实统一新增/更新时才用 `Save`；查询条件用 `XxxQuery`，历史兼容可保留 `XxxQueryParams`；导出、任务、回调等执行型输入用业务动词前缀；Web 展示对象用 `XxxVO` 且只留在 Web 模块。
- 查询字段命名：`XxxQuery` 字段用 `<field><OperatorSuffix>` 表达业务语义，默认等值查询不加后缀，例如 `status`；集合用 `In/NotIn`；模糊用 `Contains/StartsWith/EndsWith`，只有确需暴露 SQL 语义时才用 `Like`；比较用 `Gt/Gte/Lt/Lte`；时间、金额和数量范围优先用 `Min/Max`，不用 `Start/End`、`Begin/End`、`From/To`；闭区间可用 `Between`；空值用 `IsNull/IsNotNull`。字段名表达业务条件，不表达 SQL 拼接方式；未来若引入自动 Query Parser，必须另有设计、测试和兼容策略，不因命名规范自动获得解析能力。
- 事件/消息契约跟业务 owner 走：模块对外事件放 `*-face/event` 或子域 `event`；平台公共事件放 `core/event`；事件监听器、Webhook handler、投递 executor 放 `*-impl/listener` 或 `*-impl/webhook`。

| 对象 | 默认位置 |
| --- | --- |
| Service 接口、DTO、Request、Query、Command、对外枚举、常量、事件契约 | `*-face`；模型新代码优先 `model/dto`、`model/request`、`model/query`、`model/command`，兼容既有 `dto/request/query/command` |
| ServiceImpl、内部服务、规则、Converter、配置、监听器、Webhook handler | `*-impl` |
| Entity、Mapper、MyBatis `Refs`、持久化 helper | `*-impl/dal` 或 `*-impl/mapstruct` |
| Controller、Web VO、Web 表单 Request、Web Converter | `web-api` / `web-security` |
| 跨模块稳定公共值对象、枚举、事件、上下文 | `core` |
| 框架配置、通用技术适配、MyBatis Flex helper | `infrastructure` |

- `DTO`、`Request`、`Query`、`Response`、`Command`、`Event` 的 primitive 或包装类型按缺省、零值和序列化语义选择，不机械装箱；并发 Atomic 类型不得进入数据传输契约。
- Wind 项目一旦出现币种字段，必须统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode` 枚举，覆盖 DTO、Request、Query、Command、Entity、事件和内部模型；不得用 `String currency`、Integer、业务私有币种枚举或魔法常量承载。外部协议中的字符串币种只在 Adapter/Converter 边界转换，进入服务契约和领域处理前必须归一为 `CurrencyIsoCode`。
- 枚举命名和模板：生命周期用 `XxxState`，分类用 `XxxType`，动作/指令用 `XxxAction`；对外枚举放 `*-face/enums` 或稳定公共 `core/enums`，只给 impl 使用的内部枚举留在 `*-impl`。公开枚举优先实现 `DescriptiveEnum`，使用 `@Getter`、`@AllArgsConstructor`、`private final String desc`，枚举值使用大写下划线；需要颜色、层级或前端展示时通过 DTO/Converter 输出，不把展示字段随意塞进业务枚举。
- 系统字典、国际化和业务事件：Key 是稳定契约，展示文案可调整；业务逻辑、持久化判断和状态机只能依赖 code、enum、errorCode 或 eventKey，不依赖中文、英文文案或翻译结果。Key 按场景分命名空间，常用前缀为 `ui.`、`enum.`、`error.`、`event.`、`config.`；同一中文在不同业务场景也不要复用 Key。业务事件、审计展示和可回放消息存 `{eventKey, params}`，不存渲染后的中文句子；params 放业务 code 或变量值，不放“已支付”这类可变文案。Key 只能新增和废弃，语义改变必须新建 Key，历史 Key 不随意删除。
- 公共接口、公有方法、DTO/Request/Query、配置属性和扩展点要有 Javadoc，说明职责、调用方、空值、异常、权限、幂等、事务和副作用；注释说明 Why / Why not，不翻译代码。
- 项目已依赖 JSpecify 时，内部 Java 空值契约使用 JSpecify；项目已使用 Bean Validation 时，API 入参沿用对应注解；业务前置条件和状态条件使用项目断言工具。已由 JSpecify 标为非空的值，不再加无业务语义的空判断。若 `ServiceImpl` 会为 Request 字段补默认值，该字段的 Bean Validation 必须允许缺省，默认值应在服务入口归一化后再参与幂等查询、唯一键判断、转换和落库；不得把基础服务内部默认值泄露给调用方或上层 ApplicationService。
- 金额必须明确币种、精度和舍入规则；时间必须明确格式、时区和精度；ID 必须考虑唯一性、可追踪、并发和外部暴露风险。
- Spring Bean 优先构造注入；Lombok 只减少样板代码，不隐藏业务不变量、状态变化、副作用或敏感字段。
- 项目已使用 MapStruct 时，Converter 放 `mapstruct`，命名 `XxxConverter`，方法 `convertToXxx`；只做转换和确定性派生值，不做业务校验、权限、远程调用、数据库查询、状态流转或审计。字段重命名、枚举、空值策略和默认值必须显式声明并补测试。

## 4. DAL 与外部集成

- 项目已采用 Wind MySQL 表约规时，数据表强制包含 `id bigint`、`gmt_create datetime`、`gmt_modified datetime`；`creator`、`modifier`、`order_index int` 按需使用，前两者类型遵循项目约规。其他数据库或已有 schema 先服从项目本地数据约规，不机械迁移字段。新增必填字段必须有兼容迁移方案；没有真实业务默认值时不得虚构默认值。
- 业务如果有唯一约束，必须使用数据库唯一键约束，以保证可靠性；没有自然业务唯一约束时不得虚构联合唯一键。

通用表字段：

| 字段名称 | 数据库类型 | 字段说明 | 要求 |
| --- | --- | --- | --- |
| `id` | `bigint` | 主键 | 强制 |
| `gmt_create` | `datetime` | 创建时间 | 强制 |
| `gmt_modified` | `datetime` | 最后更新时间 | 强制 |
| `creator` | 项目约规类型 | 创建人 | 可选 |
| `modifier` | 项目约规类型 | 修改人 | 可选 |
| `order_index` | `int` | 排序 | 可选 |

- 项目实际使用 MyBatis Flex 时，使用 `XxxRefs` 和统一 helper 构造 `QueryWrapper`；禁止新增 `LambdaQueryWrapper` 或裸字符串字段名；分页有上限，排序白名单，写库默认 selective。
- QueryWrapper 构造逻辑优先沉淀到 helper 或基础服务，避免到处手写条件；源码样本中的标准链路是 `MybatisQueryHelper.from(options)` 或项目 helper 构造排序/分页，再用 `XxxNameRefs` 拼条件，最后通过 `MybatisQueryHelper.<Entity, DTO>query(queryWrapper).counter(mapper::selectCountByQuery).resultQueryFunc(mapper::selectListByQuery).converter(XxxConverter.INSTANCE::convertToXxxDTO).query(options)` 输出分页 DTO。排序入参优先使用项目统一的 `orderFields` / `orderTypes` 或 `WindQuery<? extends QueryOrderField>`，必须白名单校验字段和方向；复杂 SQL 说明索引、分页、排序、数据量和慢查询风险。
- 空结果分支：关键词、权限、外部检索等前置条件查不到数据时，优先返回 `Pagination.empty()` / `CursorPagination.empty()` 这类统一空分页，不返回 null、不伪造一页空对象、不绕过总数语义。
- 需要把字段更新为 null 时，必须显式指定更新列，说明业务语义，并处理 `gmt_modified`。
- 业务唯一性和请求重放幂等分层处理：有自然业务唯一约束时使用表内业务 UK 或联合 UK 兜底，并在唯一冲突后做一致性回读或差异校验；没有自然业务 UK 时不得为了形式完整虚构联合 UK。外部 `Idempotency-Key` / `requestSn` 可以用于请求重放去重，但不得冒充业务身份；必须定义租户或调用方与接口作用域、参数摘要、有效期、并发冲突、结果回放和过期后重用语义。`traceId` 只用于追踪。请求幂等键与业务 UK 各自保护不同不变量，不机械要求合并成一个唯一键。
- 外部调用先定义端口再写适配器；回调和扩展点在 face 可用 `callback/spi` 表达端口，impl 的 `webhook`、`listener`、`handler`、`executor` 负责协议解析、签名校验、状态映射、幂等和投递。异步、Webhook、MQ、批处理和回调必须有超时、重试、幂等、补偿、告警、审计和时间边界三问。
- 内网 API 路径表达安全分类：默认形态为 `/inc/{security-level}/{domain}/{resource}/{action}`。`/inc/basic/**` 只用于低风险内部查询和无敏感副作用能力；涉及用户数据、资金、权限、配置变更、关键业务状态或可被重放造成影响的操作，必须走 `/inc/secure/**`。路径只表达分类，不构成安全控制；所有内网请求都应默认拒绝并逐请求鉴权，`secure` 额外校验内部来源、appKey/timestamp/nonce/signature 或项目等价凭据，并用安全配置或契约测试证明规则生效。
- 生产实现：生产源码路径不得新增 `InMemoryXxxService`、`FakeXxxService`、`MockXxxService`、Map/List 存储型业务实现或进程内状态应用服务来承载真实业务能力。

## 5. 测试与 CR

- 测试与 TDD 以契约黑盒为准：验证 Controller、face Service、ApplicationService、ServiceImpl 等被测对象的公开契约、业务事实、接口结果、状态流转、持久化事实、SQL 条件、异常、幂等、权限/审计和可观察副作用；不测私有方法、内部调用顺序、Mapper/Repository 调用次数、临时字段、内部 Mock 交互或当前实现步骤。
- TDD 先写能失败的行为测试，再做最小实现；红变绿必须修改生产实现，不通过硬凑 fixture、放宽断言、mock 内部步骤或迎合当前实现制造虚假绿灯。若只有窥探内部才能验证，先重审服务契约、验收种子和可观察结果，按 TDD 反推契约，不按实现倒推测试。
- ApplicationService / ServiceImpl 流程测试保留真实内部协作者、转换器、策略、Repository、事务和状态变化；只替换第三方通道、远程 HTTP、MQ、Redis、时间、ID、随机数等外部边界。
- 基础服务测试重点验证 QueryWrapper、Mapper 语义、分页、排序、selective 写库、事务事实和异常语义；不要只断言调用成功或对象非空。
- MapStruct 转换测试覆盖字段完整性、枚举、空值、默认值、嵌套对象和集合转换。
- 规则变量或上下文模型测试同时覆盖模型边界和服务组装边界：模型自身不包含运行时派生 key；服务在运行时依赖和值存在时补齐变量并驱动业务行为。
- Bug 修复先补能复现失败的回归测试；新增资金、权限、审计、状态机、幂等或并发逻辑时补对应红线断言。
- 测试说明放在测试方法名、Javadoc 或方法级注释中，表达场景、输入、行为、输出和红线；测试结构优先 Given/When/Then 或 Arrange/Act/Assert。
- 完成 TDD 或 AI 生成实现后做设计质量回看：是否新增浅服务、透传接口、无主依赖、过度抽象、内部链路 mock、AI 注释噪声或只为过测试的战术实现。
- CR 检查 Wind/Nobe 启用证据、face/impl、Controller、Service 职责、接口放置、Entity 是否泄漏到服务层/接口契约、模型包归位、查询方法语义、`XxxQuery` 字段后缀、`/inc/basic` / `/inc/secure` 安全分类与鉴权、字典/国际化 Key、core/infrastructure 是否变成公共垃圾桶、Javadoc/契约、MapStruct、MyBatis Flex、外部端口、内存服务、测试层级、真实链路、替身边界和验证命令。
- 普通 Java 项目可运行 `wind-coding-conventions/scripts/check_wind_conventions.py --profile java --root <project>` 检查 `testXxx`；Wind 项目使用默认的 `--profile wind` 叠加 String 币种字段、部分 face 导入/单行签名泄漏、`queryXxxById` 命名、部分非 selective 更新和生产内存 Service 预检。脚本不承诺识别完整 Java 语法、依赖方向、多实现装配或锁语义；需要确定性约束时优先在目标项目使用 Checkstyle、PMD、ArchUnit、编译或契约测试。
- 接入 Open Code Review / OCR 时，Wind 约规可作为项目 `.opencodereview/rule.json` 或 `ocr review --background` 的规则输入，重点覆盖 face/impl、模型归位、Entity 不外露、基础服务、查询命名、内网 API、字典/国际化、MyBatis Flex、币种枚举、测试黑盒和内存服务红线；但 OCR 不是 Wind 规则权威，工具输出必须由 `资深架构师` 按源码事实、项目 `AGENTS.md`、测试结果和本 Skill 重新判读。
