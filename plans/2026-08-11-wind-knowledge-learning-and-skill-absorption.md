# Wind 知识库学习笔记与 Skill 吸收规划

> 状态：学习与最小 Skill 吸收完成，已通过独立 Checker
> 日期：2026-08-11
> 范围：Wind 公开语雀知识库、`wind-middleware`、Wind 企业集成组件、`wind-security`
> 停止点：本阶段已更新 `wind-coding-conventions` 的来源、模式和行为 fixture；不修改安装目录或三个源码仓库，不执行 Git、正式同步、发布或生产动作。

## 1. 结论摘要

1. Wind 知识库是项目族的意图、用法和团队约规入口，不是当前 API、运行行为或安全性的唯一权威。它混合了框架能力、集成教程、安全说明、运维部署、编码约规、外部链接和升级笔记，证据强度与时效性不一。
2. 三个源码仓库共同形成清晰边界：`wind-middleware` 承担运行底座与基础协议，Wind 企业集成组件承担外部系统端口和适配器，`wind-security` 承担认证、JWT、验证码与 MFA。这个能力已经由 `wind-coding-conventions` 的 `wind-architecture-patterns.md` 承载，因此不新建顶层 Skill。
3. 最小吸收落点是增强现有 `wind-coding-conventions` 的来源索引、架构模式和行为 fixture。`security-engineering-expert` 与 `senior-software-architect` 继续分别负责安全判定和源码交付，不复制 Wind 专项正文。
4. 文档与源码存在实质冲突：请求签名尚未验证 nonce 重放，幂等工具未证明并发原子占位，KMS 阿里云测试未纳入版本控制且整类禁用，`/inc/basic/**` 不能等同于无需逐请求身份校验，四类 Service 不能机械强制。上述内容必须先保留为风险或候选，不得晋升成“已具备能力”。

## 2. 来源矩阵

| source_id | 类型与锚点 | 版本 / 读取状态 | 适用范围 | 使用与隐私边界 |
| --- | --- | --- | --- | --- |
| `YQ-WIND` | [Wind 语雀知识库](https://www.yuque.com/suiyuerufeng-akjad/wind)，book id `37135667` | 目录 63 篇；2026-08-11 通过应用内浏览器逐页读取 `article#content`；63/63 非空、63/63 标题匹配，共 72,814 个正文字符 | 项目意图、用法、约规提案、历史经验 | 页面公开可读但未声明再分发许可；只保存标题、slug、读取状态、结构化提炼和冲突，不保存正文、图片或大段摘录 |
| `MW-CODE` | `wind-middleware` 当前本地 checkout | HEAD `1c0f91ee2e4d399601f0f3299ff4dbcf54334c87`；工作区干净；revision `4.1.0-SNAPSHOT`；Java 25 | 运行底座、Trace、签名、幂等、脱敏、限流和 Web 协议的当前实现事实 | 只记录路径、符号和行为，不复制实现；未运行全仓测试，不外推生产启用状态 |
| `IN-CODE` | Wind 企业集成组件当前本地 checkout | HEAD `1911e5e55da908efbc5975c278f881c1520e046c`；revision `4.1.0-SNAPSHOT`；存在用户未跟踪目录 `wind-kms/alibabacloud/src/test/` | OSS、KMS、Office、IM 和外部适配器的当前实现事实 | 未跟踪文件不作为已提交契约；`@Disabled` 测试不作为运行通过证据；未读取或输出任何真实密钥 |
| `SEC-CODE` | `wind-security` 当前本地 checkout | HEAD `e1865fa8b5876ecc9434c979f13ad7650839c803`；工作区干净；revision `4.1.0-SNAPSHOT` | 认证、JWT、验证码、MFA 的当前实现事实 | 当前源码和测试只证明存在的契约与局部行为，不证明生产启用、抗攻击或合规 |
| `SKILL-CURRENT` | `wind-coding-conventions`、`security-engineering-expert`、`senior-software-architect` 当前正文与 references | 2026-08-11 回读 | 判断去重、权威归位、现有红线和验证责任 | 已有规则优先复用；知识库不能反向扩大 Skill 职责或用户授权 |

### 2.1 语雀目录覆盖

以下分组覆盖本轮读取的全部 63 篇正文，编号与语雀目录顺序一致：

| 编号 | 主题 | 正文标题 |
| --- | --- | --- |
| 0-10 | 框架与基础集成 | Quick Start；Wind 一个企业级开发框架；Features；从配置中心加载配置启动应用；数据库相关；Dynamic Thread Pool 集成；Sentinel 集成 & 扩展；RocketMq 集成；Elasticjob 集成；对象存储（OSS）集成；KMS（秘钥管理）集成 |
| 11-20 | Trace、安全与日志 | Wind-Tracer；Trace 相关介绍；数据脱敏支持；多因素认证（MFA）支持；通过签名方式访问接口；摘要签名；Sha256 With Rsa 签名；Logback 日志脱敏支持；Logback 日志写入 Kafka；操作（审计）日志记录支持 |
| 21-32 | 测试、数据与通用能力 | Jacoco 测试覆盖率采集；H2 Mysql 数据库模式自定义函数；SpringBoot 国际化支持；Spring HTTP Interface Client 使用；数据查询支持；游标查询处理大表分页查询；并发与限流任务装饰器使用；业务幂等通用工具；自增序列号生成支持；控制器方法参数注入支持；Excel 处理支持；即时通讯（IM）支持 |
| 33-45 | 可观测、构建与发布 | 请求链路、日志 Trace；SpringBoot 端点暴露、监控；挂载 Arthas 排查问题；GraalVM 镜像构建 Dockerfile；OpenJDK 构建 Dockerfile；使用云效构建 Java 镜像；容器应用安全相关；SpringBoot 项目镜像打包；滚动更新、优雅停机；通过云效部署应用到 K8s；应用启动时 JIT 预热；平滑部署；云效发布部署流水线 |
| 46-47 | Web 运行模式 | 多 UI（皮肤）开发模式；Service Worker |
| 48-56 | 团队约规 | Java 统一开发规范；项目开发规范；查询字段命名规范 v1.0；内网 API 命名及安全规范；服务层划分与命名规范；服务层查询方法命名规范；日志打印规范；前端开发规范；Git 开发协作流程简述 |
| 57-58 | 工具与前端集成 | Git 日志压缩清理脚本；react-awesome-query-builder 集成说明 |
| 59-62 | 升级与故障经验 | 从 Java21 升级到 25；SpringBoot 3.5.x 升级到 4.x；从 Java8 升级到 Java21；SpringApplicationUtils 使用踩坑记录 |

## 3. 整体理解

Wind 知识库要解决的核心问题，是让应用团队复用统一的 Java/Spring 运行底座、外部集成能力、安全能力和工程约规，减少业务项目重复接入。源码把这个目标拆成三个稳定职责：

```text
wind-middleware   -> HTTP/Trace/签名/幂等/脱敏/限流/MQ/配置等基础协议与运行能力
企业集成组件      -> OSS/KMS/Office/IM/消息等端口、厂商适配器和装配
wind-security     -> Authentication/JWT/Captcha/MFA 等安全域能力
```

知识库可以提供“为什么存在、怎样开始、团队希望怎样使用”；当前源码与测试才能约束“现在有哪些 API、默认怎样执行、哪些分支已验证”。发布、生产、安全和兼容结论还需要启用配置、构建产物、目标环境与运行证据，不能由文档或单元测试代替。

## 4. 文档主张与代码事实矩阵

| 主题与语雀锚点 | 当前代码锚点与事实 | 判定 | 最小归位 |
| --- | --- | --- | --- |
| [Wind-Tracer](https://www.yuque.com/suiyuerufeng-akjad/wind/mrzvfd5pz4e8fgd3)、[Trace 相关介绍](https://www.yuque.com/suiyuerufeng-akjad/wind/hbxwcuu4hym4887q)、[请求链路、日志 Trace](https://www.yuque.com/suiyuerufeng-akjad/wind/cwozn40mr41f4ea7) | `WindTracer.TRACER` 当前使用 `DefaultScopeValueTracer`；`TraceFilter` 对 ERROR/ASYNC redispatch 重新绑定上下文并提前回写响应 traceId；`TraceFilterTests.rebindsTraceContextWhenRequestIsRedispatchedAsError` 覆盖错误分派；异步工作仍需 `ContextPropagationTaskDecorator` 或显式 wrap | 核心模式有代码支撑；“Servlet 异步分派”不能替代“异步任务上下文传播” | 增强 `wind-architecture-patterns.md` 的入口、分派、异步任务三层边界，并加负例 fixture |
| [通过签名方式访问接口](https://www.yuque.com/suiyuerufeng-akjad/wind/zl1ygpq3pitl00qp)、[摘要签名](https://www.yuque.com/suiyuerufeng-akjad/wind/yfc5dmdpnxrtsmfu)、[SHA256 With RSA](https://www.yuque.com/suiyuerufeng-akjad/wind/soqzi3epvmbau6fr) | 当前默认头名由 `SignatureHttpHeaderNames` 生成：`Wind-Nonce`、`Wind-Timestamp`、`Wind-Access-Id`、`Wind-Secret-Version`、`Wind-Sign`；`ApiSignAlgorithm` 有 HMAC-SHA256/HMAC-SHA512/SHA256withRSA 测试；`RequestSignFilter` 校验时间窗，但 nonce 只参与签名，源码仍有 `TODO 随机串的验证` | 算法与规范化可作为当前事实；防重放未闭合，签名不替代 TLS、身份授权或幂等 | 在 Wind 架构 reference 建“签名契约核对卡”，安全判断仍路由 `security-engineering-expert` |
| [数据脱敏支持](https://www.yuque.com/suiyuerufeng-akjad/wind/oa8ikxo30elb0t0v) | `MapObjectMasker` Javadoc 明确原地改变 Map，`MapObjectMaskerTests.testMask` 验证输入对象被替换为脱敏值 | 文档与实现一致；副作用必须进入调用契约 | 补入 Wind 架构 reference 的 gotcha，不升级为通用 Java 规则 |
| [业务幂等通用工具](https://www.yuque.com/suiyuerufeng-akjad/wind/gm6ogkwsv8429t5o) | `HttpRequestIdempotentFilter` 使用 `Wind-Idempotent-Key`；`WindIdempotentExecuteUtils` 先查后执行再保存，`WindIdempotentKeyStorage` 没有原子占位、参数摘要、作用域或 TTL 契约；现有测试使用进程内 Map，只覆盖串行结果回放 | 只能证明串行去重/结果回放骨架；不能宣称并发幂等、跨实例一致性或安全重试 | 保持现有 Wind 幂等红线；增加“存储原子占位与冲突语义必须由实现证明”的 fixture，不吸收文档泛化结论 |
| [并发与限流任务装饰器](https://www.yuque.com/suiyuerufeng-akjad/wind/oa03yskghzk6mc7r) | `ConcurrencyLimiterTaskDecorator`、`RateLimiterTaskDecorator` 及对应测试存在；组合顺序是当前实现选择 | 可作为能力发现入口；具体先后顺序、容量和等待时间必须由场景决定 | 只补能力路由，不写统一容量或顺序强规约 |
| [OSS 集成](https://www.yuque.com/suiyuerufeng-akjad/wind/pc1gu9ukxahqwqe1) | `WindOssClient` 为端口，`AlibabaCloudOssClient` 为适配器，`WindOssAutoConfiguration` 使用条件装配并允许覆盖默认 `WindOssClient` | Port/Adapter/Starter 模式有源码支撑；没有真实云端集成通过证据 | 更新来源索引；保留现有企业集成模式，不新建 Skill |
| [KMS 集成](https://www.yuque.com/suiyuerufeng-akjad/wind/re1g3mtumxczglfe) | `WindCryptoClient`、`WindCredentialsClient`、`WindKmsClientProvider` 隔离端口；阿里云实现支持 OIDC 和默认凭据链；当前阿里云测试目录未跟踪且测试类 `@Disabled`；客户端初始化日志会输出 AK 前 5 位 | 端口和凭据入口有代码支撑；真实 KMS 可用性、生产凭据方式与安全日志未准出 | 只吸收端口/凭据边界；测试与 AK 日志列为单独工程/安全审查候选 |
| [Excel 处理](https://www.yuque.com/suiyuerufeng-akjad/wind/bybcrpnoq5g9tq9t) | `office/excel` 有 reader、writer、导入/导出任务和多个单元测试 | 能力存在；本轮未验证大文件资源上限、失败恢复或生产任务状态一致性 | 只登记能力地图，待真实场景再读取专题源码 |
| [IM 支持](https://www.yuque.com/suiyuerufeng-akjad/wind/uvy1wi99vbi4nqy2) | `JwtTokenAuthTokenListener` 校验 token 并绑定用户；`DefaultWindSocketSessionRegistry` 使用进程内连接缓存和 Redisson 依赖；`DataListenerTraceWrapper` 创建 trace；当前未发现 IM 模块行为测试 | 架构骨架存在；多设备策略、跨节点路由、重连、消息可靠性和授权边界未准出 | 保留为按需源码路由，不晋升完整 IM 能力包 |
| [MFA 支持](https://www.yuque.com/suiyuerufeng-akjad/wind/bgcf8hcd1ga1sxq0) | `MultiFactorAuthenticationMethodInterceptor` 使用 scene、设备、状态管理器和 Sentinel 资源；TOTP 有一个局部测试；未看到 AOP、状态 TTL、限流、重试/锁定和审计的端到端验证 | 不能吸收“TOTP 安全性最高”；只能记录现有扩展点和未闭合证据 | Wind reference 记录实现边界，威胁与控制验证交 `security-engineering-expert` |
| [查询字段命名](https://www.yuque.com/suiyuerufeng-akjad/wind/ggbylk3r2kgtc1ol)、[服务层划分](https://www.yuque.com/suiyuerufeng-akjad/wind/dmvqtwk48qcmtg1c)、[查询方法命名](https://www.yuque.com/suiyuerufeng-akjad/wind/dnu8ggfuslaego84) | 现有 `wind-coding-conventions.md` 已吸收 `get/find/query`、Query 后缀，并把“四类 Service”降为判断框：没有真实变化轴时不新增 Domain/Application 层 | 现有 Skill 比原文更符合最小分层和项目事实，不能退回机械强制 | 更新来源索引和负例 fixture；正文原则上无需扩写 |
| [内网 API 命名及安全规范](https://www.yuque.com/suiyuerufeng-akjad/wind/lynoufptdg3ml6bs) | 现有 Wind 约规已明确“路径只表达分类，不构成安全控制”，所有内网请求默认拒绝并逐请求鉴权，`secure` 再叠加来源和签名等控制 | 现有 Skill 已纠正文档把 `basic` 等同于内网可信的问题 | 只补来源与反例，不复制原文规则 |
| [构建、容器与发布](https://www.yuque.com/suiyuerufeng-akjad/wind/gws9ob2crzlk5tw3) 等 34-45 篇 | 文档同时出现旧 Java/CMS 参数、特定云效/K8s 配置和固定资源比例；本轮目标仓库源码不能证明当前 CI、镜像、集群和生产参数 | 时效与环境风险高，不能沉淀为稳定 Skill 规则 | 任务内保留来源索引；将来需目标部署仓库、环境指标和发布证据重新提炼 |
| Java/Spring 升级 59-61、SpringApplicationUtils 故障记录 62 | 当前三个仓库已使用 revision `4.1.0-SNAPSHOT`，`wind-middleware` 明确 Java 25；故障记录是一次 Nacos refresh 上下文覆盖案例 | 升级列表与故障故事可作排查线索，不能当所有项目的迁移清单或根因 | 不吸收为强规约；真实升级/故障任务按当前依赖与日志重新验证 |

## 5. 冲突矩阵

| conflict_id | 文档主张 / 差异 | 当前证据 | 裁决与旧值清除检查 |
| --- | --- | --- | --- |
| `WIND-C01` | 多篇签名文档混用 `Wind-Access-Key`、`Wind-App-Id`、`Wind-Access-Id` | `SignatureHttpHeaderNames` + `SignatureConstants` 的当前默认值是 `Wind-Access-Id` 等五个核心头 | 当前代码契约优先；不得把其它名称并列写成默认值，历史兼容必须有项目证据 |
| `WIND-C02` | timestamp + nonce 被描述成防重放 | `RequestSignFilter` 只有时间窗检查，nonce 验证仍是 TODO | 明确标记“nonce 已签名但未做服务端唯一性消费”；没有原子 nonce 存储与测试不得声称防重放 |
| `WIND-C03` | RSA 页面正文一处把生成算法写成 HmacSHA256 | `ApiSignAlgorithm.SHA256_WITH_RSA` 与 `ApiSignerTests.testSha256WithRsaSign` 使用 SHA256withRSA | 视为文档错误，不吸收 HMAC 说法 |
| `WIND-C04` | HTTP 与 HTTPS 都可通过签名访问，容易被理解为不需要 TLS | 安全权威明确签名、TLS、授权、幂等是不同控制 | Skill 必须写“签名不替代 TLS”；删除任何“有签名即可明文传输”的暗示 |
| `WIND-C05` | TOTP 被称为“目前安全性最高” | 当前代码只证明 TOTP 适配和局部校验，不提供比较基准或抗钓鱼证据 | 拒绝该绝对化结论；MFA 选择必须按威胁、恢复和运行控制判断 |
| `WIND-C06` | KMS 文档呈现为开箱可用 | 阿里云测试目录未跟踪，测试类整体禁用；没有真实环境执行结果 | 端口设计与运行就绪分开；不得把 disabled/untracked 测试写成通过证据 |
| `WIND-C07` | `/inc/basic/**` 只需内网访问 | 内网位置不是身份，路径也不是控制 | 保留现有 Skill 的默认拒绝和逐请求鉴权；不得降级 |
| `WIND-C08` | Service 只允许四类，跨层调用被绝对禁止 | 现有 Skill 已按稳定规则、查询模型、场景编排是否真实存在来决定层次 | 四类只作判断框；不得为了命名新建浅层、透传接口或迁移存量包名 |
| `WIND-C09` | `Wind-Idempotent-Key` 工具被描述成通用安全幂等 | 当前执行流程没有原子占位、参数摘要、调用方/接口作用域和 TTL 契约 | 保持 candidate；并发、冲突和回放语义未证明前不得晋升 |
| `WIND-C10` | 精确 JVM、容器资源、滚动发布参数被写成推荐值 | 内容跨 Java 8/CMS 到 Java 25，且没有当前负载和集群证据 | 不吸收固定数字；将来以目标环境测量、SLO 和回滚证据重建 |
| `WIND-C11` | KMS 文档强调凭据安全 | 当前阿里云客户端初始化日志输出 AK 前 5 位 | 不把该行为吸收成模式；另开安全 CR 时评估是否应完全移除凭据片段日志 |

## 6. 能力候选与归位

| capability_id | 稳定职责与输入输出 | 状态 | 推荐落点 | 验证种子 |
| --- | --- | --- | --- | --- |
| `WIND-KB-01` | 输入 Wind 任务和项目证据，输出“应复用的模块/端口、需继续读取的源码、不能声称的能力” | `accepted` | `wind-coding-conventions/references/wind-architecture-patterns.md` 与 `source-map.md` | OSS/KMS、Trace、签名和证据分层 fixture 已通过静态门禁与独立 Checker |
| `WIND-TRACE-01` | 区分入口绑定、Servlet redispatch、异步任务传播和执行后清理 | `accepted` | Wind 架构 reference；工程实现仍归 `senior-software-architect` | fixture 明确拒绝把 redispatch 测试当线程池传播证据，独立 Checker 回链当前源码通过 |
| `WIND-SIGN-01` | 核对当前头名、规范化、算法、时间窗、nonce 消费、TLS、授权和幂等边界 | `accepted` | Wind 架构 reference + 安全路由 fixture | fixture 要求指出 nonce 未消费和 TLS 独立控制，独立 Checker 回链当前源码通过 |
| `WIND-ENTERPRISE-01` | 从业务需求定位既有端口、适配器、自动装配、覆盖点和真实集成证据 | `accepted` | 现有企业集成章节，不新建 Skill | fixture 能定位 OSS/KMS 端口并拒绝 disabled/untracked 测试越级，独立 Checker 通过 |
| `WIND-IDEMPOTENCY-01` | 评审幂等键作用域、参数摘要、原子占位、结果回放、TTL、冲突和业务 UK | `duplicate` | 现有 `wind-coding-conventions.md` 已有权威红线 | 只补当前实现负例；不复制规则正文 |
| `WIND-CONVENTION-01` | 将查询命名、Service 分层、内网 API 当成带边界的 Wind 专项，而非机械模板 | `duplicate` | 现有 Wind 约规 + fixture | 拒绝“四类 Service 必须全建”和“basic 不鉴权”两个硬负例 |
| `WIND-DEPLOY-01` | 从知识库生成统一部署 Skill | `rejected` | 任务内 | 缺少当前 CI/镜像/集群/负载/生产证据，内容跨版本且依赖特定平台 |
| `WIND-KMS-CR-01` | 评审 KMS 凭据、日志和真实集成测试 | `candidate`，但不是知识吸收任务 | 未来单独交 `security-engineering-expert` + `senior-software-architect` | 需要用户授权的源码 CR、目标凭据方式、测试环境和脱敏日志证据 |

上述 `accepted` 只表示知识已进入现有 Skill 的 reference 与行为契约，并通过仓库门禁和独立 Checker；不表示三个源码仓库的缺口已修复、云集成已通过或生产能力已启用。没有新建 Skill 是预期结果，说明现有职责可以承接。

## 7. Skill 吸收规划

### Phase A：来源归档与旧值清理

最小修改文件：

1. `wind-coding-conventions/references/source-map.md`
   - 记录语雀 63/63 读取状态、book id、读取日期、公开但许可未声明的边界。
   - 记录三个仓库本轮 HEAD 与工作区状态。
   - 把原“未重新读取公开仓库、未留 commit/tag”的旧状态替换为本轮事实，不能保留新旧两个相互冲突的读取状态。
2. 不修改 `wise-agent`、`resource-capability-distiller`、`security-engineering-expert` 或 `senior-software-architect` 的来源索引；它们不是 Wind 专项来源的 Owner。

完成证据：来源可回链、旧状态已清除、没有原始正文或私有路径进入仓库。

### Phase B：最小模式补强

仅在现有正文缺口仍存在时修改 `wind-coding-conventions/references/wind-architecture-patterns.md`：

- Trace：补“入口绑定 / redispatch / 异步任务传播”三者不可互相代证。
- 请求签名：补当前头名来源、nonce 消费、TLS、授权和幂等边界；不复制算法教程。
- 幂等：只补“当前 helper 存在不等于存储提供原子占位”，详细业务红线继续引用 `wind-coding-conventions.md`。
- KMS：补“端口/适配器存在、凭据链、真实集成证据”三层；不写厂商操作手册。
- 脱敏：补 `MapObjectMasker` 原地修改这一项高价值 gotcha。

停止条件：若现有规则已完整表达同一语义，只更新来源或 fixture，不重复扩写正文。

### Phase C：行为验证

在现有 `fixtures/skill-eval/prompt-cases.json` 或其当前权威 fixture 中新增最小用例，不新建测试框架：

1. 正例：Wind 项目要接 OSS/KMS，能先找端口、适配器、starter 与真实集成证据。
2. 正例：询问签名是否防重放，能指出 nonce 只参与签名但未被唯一消费，且签名不替代 TLS。
3. 正例：询问 Trace 异步传播，能区分 redispatch 与线程池 decorator。
4. 硬负例：要求照文档强制建立四类 Service，必须拒绝无真实职责的浅层。
5. 硬负例：认为 `/inc/basic/**` 无需身份校验，必须维持默认拒绝与逐请求鉴权。
6. 证据负例：以未跟踪、`@Disabled` 的 KMS 测试声称集成通过，必须拒绝。

完成证据：fixture 契约校验通过；同一 runner/model 的 baseline/candidate 行为对比能证明减少错误外推；静态 fixture 本身不算行为改善。

### Phase D：统一验证与准出

按仓库现有命令执行最小闭环：

- YAML、Markdown 引用、触发路径和安全检查使用根 `scripts/validate.sh` 的现有校验集合。
- 正式同步前只执行现有 `sync-skills.sh` dry-run，并检查目标技能、备份目录和 `rsync --delete` 影响；本规划不授权正式同步。
- 检查 `git diff --check`、白名单文件差异和未关联修改，确保不混入当前工作区其它在途变更。
- 独立 Checker 回读语雀锚点、三个 HEAD、冲突矩阵与行为结果后，才可把 `candidate` 晋升为已吸收。

## 8. 明确拒绝与待确认

### 不吸收

- 不新建 `wind-knowledge`、`wind-framework-expert` 或按仓库拆出的三个顶层 Skill。
- 不复制语雀正文、图片、命令全文、作者口吻和外链文章结论。
- 不吸收“TOTP 安全性最高”“内网 basic 无需验签/鉴权”“有 nonce 和 timestamp 即防重放”“四类 Service 必须全部存在”等绝对化结论。
- 不吸收固定 JVM、GC、Docker、K8s、云效、资源比例和 Git 分支流程为全局默认。
- 不把模块存在、编译通过、单元测试、disabled 测试或文档示例写成已启用、已发布或生产可用。
- 不把本轮发现的源码风险顺手修复到三个仓库；那是需要单独目标、授权和验证的工程任务。

### 待确认 / 后续证据

- `RequestSignFilter` nonce 唯一消费、存储 TTL、集群一致性和失败策略由哪个 Owner 持有。
- `WindIdempotentKeyStorage` 的生产实现是否另有原子占位、参数摘要、调用方作用域和 TTL 契约。
- KMS 的目标凭据方式、真实测试环境、AK 片段日志处置和 untracked 测试归属。
- IM 的多设备连接策略、跨节点消息路由、重连、授权和可靠性验收证据。
- 部署/升级类内容对应的当前 CI 仓库、镜像基线、K8s 环境、SLO、容量数据和回滚演练。

上述任一项未闭合时，只能作为能力发现或评审问题，不能成为“Wind 已保证”的稳定规则。

## 9. 本轮落地与准出结果

- 来源层：`source-map.md` 已替换“未重新读取、未留 commit”的旧状态，记录语雀 63/63 读取边界、三个当前 HEAD、工作区状态和证据等级。
- 方法层：`wind-architecture-patterns.md` 已补 Trace 三层边界、签名/防重放/TLS 边界、企业集成证据链、幂等存储门禁和 `MapObjectMasker` 原地修改副作用。
- 证据层：`prompt-cases.json` 已新增六个 Wind 对抗样例；没有新增 Skill、runner、script，也没有修改 `SKILL.md` 或 `agents/openai.yaml`。
- 验证：JSON 解析、`audit-skill-eval-fixtures.py --self-test`、`git diff --check` 与根 `scripts/validate.sh` 全部通过；完整校验包含 YAML、引用、触发路径、来源索引、Skill admission、安装一致性和 `sync-skills.sh --dry-run`。
- 独立准出：规格 Checker 与安全/质量 Checker 均结论为通过，无阻断或重要问题。
- 未执行：未运行云端 KMS/OSS、生产或兄弟仓库测试；未修改三个源码仓库；未正式同步 Codex 安装态；未执行 Git stage、commit、push 或 PR。
