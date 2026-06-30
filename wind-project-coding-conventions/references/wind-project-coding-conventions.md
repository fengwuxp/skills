# Wind 项目编码约规

本文是 `wind-project-coding-conventions` Skill 的主规则，用于项目本地 `AGENTS.md` 明确标明“遵守 Wind 项目编码约规”时，约束 Java/Spring/Wind/Nobe 风格项目的设计、编码、TDD 和 CR；项目本地规则、OpenSpec/ADR、CI 与附近代码风格优先。

## 使用时机

- 项目本地 `AGENTS.md` 明确标明、任务说明或用户要求遵守 Wind 项目编码约规。
- 评审 face/impl 模块边界、接口放置、基础服务、应用层服务、DTO/Request/Query/Entity、模型包归位、分包规则、MyBatis Flex、外部集成端口或代码生成后审查。

## 不适用场景

- 非 Java/Spring/Wind 项目先读 `language-agnostic-architecture.md`，不得强套本规约。
- 项目 `AGENTS.md`、OpenSpec、ADR、CI 或附近代码已有更具体规则时，以项目本地规则为准。

## 读取后必须产出

- 当前项目是否 opt-in；命中的模块、接口、服务、模型、DAL、外部调用和测试规则；违反项的最小整改建议与验证方式。

## 需要继续读取的 reference

- Java/Spring/Wind 强制规则读 `coding-standards.md`；Service/API/DTO/Query 读 `project-governance-service-api-modeling.md`；测试/TDD 读 `testing.md` 和 `testing-practices.md`；模块依赖读 `project-governance-codebase-and-modules.md`；深度 CR 读 `coding-review-deep-dive.md`；需要最佳实践正反例时读 `wind-project-coding-examples.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| opt-in / 模块 / 分包 / 接口放置 / 模型包归位 / Service / DAL / 外部集成 / TDD-CR | 下方 `规则清单`，再按需读相关 reference | 不猜测所有 Java 项目都适用；不复制通用 Java/测试大全 |
| 最佳实践 / 示例 / 正反例参照 | `wind-project-coding-examples.md` | 不把示例当完整模板或代码生成规则 |

## 1. 启用、模块与分包

- 启用：项目本地 `AGENTS.md` 写明即可，例如“本项目遵守 Wind 项目编码约规”；启用后仍按项目 `AGENTS.md`、OpenSpec、ADR、CI、附近代码、本规约的顺序取舍。

- 源码观察边界：本规约已抽样对照 `wind-integration / nobe / capte-domain 源码观察`，提炼的是稳定共性，不把某个仓库的历史包名、业务模块名或临时实现照搬成强制规则；具体项目仍以本地 `AGENTS.md`、附近代码和 CI 为准。

- 放置四问：先问谁调用、生命周期归谁、变化 owner 在哪、依赖方向是否越界。对外或跨模块调用进 `*-face`；模块内部实现进 `*-impl`；Web 展示和入口进 `web-api` / `web-security`；跨模块稳定公共能力进 `core`；技术适配和框架配置进 `infrastructure`。依赖 Web/DAL/第三方 SDK/具体框架实现的类型不得进入 face/core。

- 模块：`*-face` 只放对外契约：`service/services`、必要的 `application` 契约、`model/dto`、`model/request`、`model/query`、`model/command`、`enums`、`constants`、明确需要跨模块消费的 `event`，以及回调入口、扩展点或业务 SPI 的 `callback/spi`、`callback/request`、`callback/service`；历史兼容场景允许继续使用既有 `dto`、`request`、`query`、`command` 包。同一 face 有多个业务子域时，可按业务名继续分包，例如 `transaction/model/dto`、`channel/model/request`、`domain/model/dto`、`domain/model/request`，兼容既有 `transaction/dto`、`channel/request`、`domain/dto`、`domain/request`，但 `domain` 必须表示稳定业务语义，不得作为杂物包。`*-impl` 放内部 `service` / `service/impl`、`application/impl`、`domain` / `domain/impl`、`impl`、`dal/entities`、`dal/mapper`、`mapstruct`、业务/通道 `converter`、`support`、`configuration`、`listener`、`webhook` 和内部枚举；`*-impl` 一般不放对外 DTO/Request/Query/Command，除非是实现层内部模型且不对外暴露。`web-api` / `web-security` 放 Controller、Web VO、Web 登录/表单 Request 和 Web 层 Converter。`core` 放跨模块稳定基础契约、值对象、枚举、事件、上下文、规则、告警、缓存兑换、操作人等公共能力，不放业务模块私有 DTO/Request/Query/Command/Entity、Web VO、Mapper/Repository 或具体业务实现。`infrastructure` 放消息发送、KMS、MyBatis Flex helper、通用工具和框架配置等技术适配，不放业务契约、Controller、业务 Service 或业务 Entity。Controller 不直接访问 Mapper/Entity。

- 包名判断：源码样本中 `*-face` 常见 `service/services`、`application`、`dto|model/dto`、`request|model/request`、`query|model/query`、`event`、`callback/spi`；`*-impl` 常见 `service/impl`、`application/impl`、`dal/entities`、`dal/mapper`、`mapstruct`、`converter`、`listener`、`webhook`；`web-api` 常见 `controller`；`core` 常见跨模块 `enums`、`event`、`context`、`operator`；`infrastructure` 常见 `dal` helper、外部技术 adapter 和 framework config。新代码优先按这些 owner 放置，不把 web、dal、第三方 SDK 或具体实现依赖上推到 face/core。

## 2. 服务层

- Face Service 是对外稳定契约，`ServiceImpl` 承接校验、状态、事务和数据访问协调；ApplicationService 只在完整用例编排、事务边界、权限/审计、跨服务协调或外部副作用明确时使用。若 ApplicationService 作为对外用例契约出现，接口放 `*-face/application`，实现放 `*-impl/application/impl`，签名仍只用 Request/DTO/Query/值对象。
- 接口落位：跨模块稳定业务能力放 `*-face/service`；完整用例契约才放 `*-face/application`；回调入口、扩展点和业务 SPI 放 `*-face/callback/*`；只被本模块实现层使用的接口留在 `*-impl/service`、`*-impl/domain` 或 `*-impl/support`，不因“可能复用”放进 face/core。
- 服务层接口先按调用方契约设计：face Service 和跨模块接口只暴露 `DTO`、`Request`、`Query`、`Command`、枚举或值对象，不暴露 `Entity`；`ServiceImpl` 可在内部读取和更新 `Entity`，但不得把 `Entity` 透传给 Controller、face、ApplicationService 对外方法、Facade、Adapter 或其他域。
- 包位：新代码的 face Service 生产实现默认放 `*-impl/.../service/impl`；`*-impl/.../impl` 根包只作为历史兼容或附近代码已有明确约定时保留，不作为新 ServiceImpl 默认落点。
- 基础服务落位：被其他模块、组合 Service 或外部适配层稳定消费时，接口放 `*-face/service`；只封装本 impl 内 Mapper、QueryWrapper 或内部状态流转时，留在 `*-impl/service`；只是 Mapper 透传时不应新增服务。
- 内部基础服务可以封装稳定查询或基础数据访问，但不能只是 Mapper 透传；接口、Service、Facade、Adapter 必须有真实业务职责，不新增一行 wrapper、改名转发、浅模块或似是而非抽象。
- 查询服务形态：公开查询接口优先返回 `DTO` 或 `WindPagination<DTO>`，查询选项使用 `WindQuery<? extends QueryOrderField>` 或项目既有分页选项；`ServiceImpl` 内部再组合 `QueryWrapper`、Mapper、Converter 和 result enricher。默认方法只用于复用已有公开契约上的小型断言或组合查询，不新增绕过实现层的业务状态。
- 多实现组合：同一 face Service 有多个生产实现时，保留一个主对外实现做组合编排，其他实现必须承担清晰业务职责；通过 `@Primary`、明确 bean name 或项目统一装配规则解决注入歧义，不用 `Processor`、`Handler` 这类泛名掩盖服务职责。
- `DomainService` / `DomainQueryService` 不是 Wind 项目强制分层；只有确有领域规则、状态变化、查询模型或统计读模型时才在 `*-impl` 内部 `domain` / `domain/impl` 落位，不为套分层新增浅服务或 Mapper 包装。
- 写操作用业务动词，例如 submit、approve、reject、freeze、unfreeze、pay、refund、settle；查询按 `get/find/query/exists/count/stats` 区分必然存在、可空、条件查询和统计，不用 handle/process/doXxx 掩盖语义。
- 事务边界放在真实用例边界；事务内避免不可控远程调用、长耗时计算和无上限循环，确需调用时说明超时、补偿和失败处理。

## 3. 模型与契约

- 模型：`Request` 写入命令，`Query` 查询条件，`DTO` 对外或跨模块契约，`Entity` 只表达持久化结构。Controller、face Service、ApplicationService 对外方法、Facade、Adapter、跨模块接口、事件/消息契约不得以 Entity、Mapper、Repository 或 MyBatis `Page` 作为入参、返回值或泛型；离开 `*-impl` 边界前必须转换为 `DTO`、`Request`、`Query`、`Command`、`Event` 或值对象。
- 模型包归位：新代码的 `DTO`、`Request`、`Query`、`Command` 优先放在 `*-face` 或 `core` 的 `model/dto`、`model/request`、`model/query`、`model/command` 下，对应 Java 包名通常是 `*.model.dto`、`*.model.request`、`*.model.query`、`*.model.command`；历史兼容场景允许继续使用既有 `dto`、`request`、`query`、`command` 包，对应 `*.dto`、`*.request`、`*.query`、`*.command`。业务模块自己的 `enums`、`event` 优先放在对应 `*-face` 的业务包下；同一 face 内多个子域可用 `xxx/model/dto`、`xxx/model/request`、`xxx/model/query`、`xxx/event` 分包，兼容既有 `xxx/dto`、`xxx/request`、`xxx/query`、`domain/dto|request`，其中 `domain` 仅用于跨子域、稳定业务概念，不得当杂物包。持久化 `Entity`、Mapper、Repository、MyBatis `Refs` 和 MapStruct Converter 放在对应 `*-impl` 的 `dal/*` 或 `mapstruct` 下；`*-impl` 一般不放 DTO/Request/Query/Command，除非是内部模型且不进入 Controller、face Service、ApplicationService 对外方法、Facade、Adapter、事件/消息或跨模块接口。业务/通道事件 Converter 可放 `*-impl` 的 `converter` 或 `support`，但只做适配转换，不承载公共契约或核心业务决策。Web 展示 VO、登录/表单 Request 和页面组合模型放 `web-api` / `web-security`，不得回流到 face 契约；跨域共享模型只有在两个以上业务模块稳定复用且不依赖 Web/DAL 时，才放 `core` 的 `model`、`enums` 或 `event`。
- 事件/消息契约跟业务 owner 走：模块对外事件放 `*-face/event` 或子域 `event`；平台公共事件放 `core/event`；事件监听器、Webhook handler、投递 executor 放 `*-impl/listener` 或 `*-impl/webhook`。

| 对象 | 默认位置 |
| --- | --- |
| Service 接口、DTO、Request、Query、Command、对外枚举、常量、事件契约 | `*-face`；模型新代码优先 `model/dto`、`model/request`、`model/query`、`model/command`，兼容既有 `dto/request/query/command` |
| ServiceImpl、内部服务、规则、Converter、配置、监听器、Webhook handler | `*-impl` |
| Entity、Mapper、MyBatis `Refs`、持久化 helper | `*-impl/dal` 或 `*-impl/mapstruct` |
| Controller、Web VO、Web 表单 Request、Web Converter | `web-api` / `web-security` |
| 跨模块稳定公共值对象、枚举、事件、上下文 | `core` |
| 框架配置、通用技术适配、MyBatis Flex helper | `infrastructure` |

- `DTO`、`Request`、`Query`、`Response`、`Command`、`Event` 不使用 Java primitive 或 Atomic 类型承载契约字段；使用包装类型、枚举、值对象或明确业务类型表达缺省、精度和序列化语义。
- 公共接口、公有方法、DTO/Request/Query、配置属性和扩展点要有 Javadoc，说明职责、调用方、空值、异常、权限、幂等、事务和副作用；注释说明 Why / Why not，不翻译代码。
- 内部 Java 空值契约用 JSpecify；API 入参用 Bean Validation；业务前置条件和状态条件用项目断言工具。已由 JSpecify 标为非空的值，不再加无业务语义的空判断。
- 金额必须明确币种、精度和舍入规则；时间必须明确格式、时区和精度；ID 必须考虑唯一性、可追踪、并发和外部暴露风险。
- Spring Bean 优先构造注入；Lombok 只减少样板代码，不隐藏业务不变量、状态变化、副作用或敏感字段。
- MapStruct 放 `mapstruct`，命名 `XxxConverter`，方法 `convertToXxx`；只做转换和确定性派生值，不做业务校验、权限、远程调用、数据库查询、状态流转或审计。字段重命名、枚举、空值策略和默认值必须显式声明并补测试。

## 4. DAL 与外部集成

- MyBatis Flex 使用 `XxxRefs` 和统一 helper 构造 `QueryWrapper`；禁止新增 `LambdaQueryWrapper` 或裸字符串字段名；分页有上限，排序白名单，写库默认 selective。
- QueryWrapper 构造逻辑优先沉淀到 helper 或基础服务，避免到处手写条件；源码样本中的标准链路是 `MybatisQueryHelper.from(options)` 或项目 helper 构造排序/分页，再用 `XxxNameRefs` 拼条件，最后通过 `MybatisQueryHelper.<Entity, DTO>query(queryWrapper).counter(mapper::selectCountByQuery).resultQueryFunc(mapper::selectListByQuery).converter(XxxConverter.INSTANCE::convertToXxxDTO).query(options)` 输出分页 DTO。复杂 SQL 说明索引、分页、排序、数据量和慢查询风险。
- 空结果分支：关键词、权限、外部检索等前置条件查不到数据时，优先返回 `Pagination.empty()` / `CursorPagination.empty()` 这类统一空分页，不返回 null、不伪造一页空对象、不绕过总数语义。
- 需要把字段更新为 null 时，必须显式指定更新列，说明业务语义，并处理 `gmt_modified`。
- 外部调用先定义端口再写适配器；回调和扩展点在 face 可用 `callback/spi` 表达端口，impl 的 `webhook`、`listener`、`handler`、`executor` 负责协议解析、签名校验、状态映射、幂等和投递。异步、Webhook、MQ、批处理和回调必须有超时、重试、幂等、补偿、告警、审计和时间边界三问。
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
- CR 检查 opt-in、face/impl、Controller、Service 职责、接口放置、Entity 是否泄漏到服务层/接口契约、模型包归位、core/infrastructure 是否变成公共垃圾桶、Javadoc/契约、MapStruct、MyBatis Flex、外部端口、内存服务、测试层级、真实链路、替身边界和验证命令。
- Wind opt-in 项目可加低成本结构守卫：`*ServiceImpl` 不落错误根包；face 公开签名不出现 Entity、Mapper、Repository 或 MyBatis `Page`；impl 内部基础服务接口不暴露 Entity 或 QueryWrapper；同一 Service 多实现时存在唯一主对外实现或明确装配规则。
