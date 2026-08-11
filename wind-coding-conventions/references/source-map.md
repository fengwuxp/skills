# Java/Wind 编码约规来源索引

本文记录本 Skill 外部来源的读取状态、采纳边界和不吸收项。规则正文仍以 `java-coding-conventions.md` 和 `wind-coding-conventions.md` 为准。

## 使用时机

- 核验阿里 Java 手册或 Wind 项目族样本如何进入约规。
- 更新外部来源、读取状态、版本边界或不吸收项。

## 不适用场景

- 普通约规检查不必读取本文件。
- 不把来源索引当成当前项目事实、执行授权或源码 CR 结论。

## 读取后必须产出

- 来源、读取日期、采纳边界、不吸收项和需要重新核验的内容。

## 需要继续读取的 reference

- 通用 Java 规则读 `java-coding-conventions.md`，Wind 专项读 `wind-coding-conventions.md`，项目族模式读 `wind-architecture-patterns.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核验阿里手册采纳 | `阿里 Java 开发手册` | 不复制手册正文和旧版环境参数 |
| 核验 Clean Code 启发 | `《代码整洁之道》公开学习材料` | 不把读书笔记或启发式建议升级成机械强制规则 |
| 核验 Bean Validation 语义与触发边界 | `Bean Validation / Jakarta Validation / Spring MVC 官方文档` | 不把注解声明误写成已执行验证 |
| 核验 Spring Bean 依赖注入与 Lombok 构造器 | `Spring Dependency Injection / Lombok constructor 官方文档` | 不把 Lombok 构造器生成误写成 Spring 装配已验证 |
| 核验 JSpecify 空值语义 | `JSpecify 官方文档` | 不把静态契约误写成运行时校验 |
| 核验 Wind 项目族经验 | `Wind 项目族公开样本` | 不把公开样本当当前项目事实 |

## 阿里 Java 开发手册

- 来源：[《阿里巴巴Java开发手册》](https://www.yuque.com/iv8gga/qgf69v)，页面版本历史包含 1.3.1（2017-11-30）。
- 读取状态：2026-07-16 已通过 Codex 应用内浏览器逐章读取目录中的编程规约、异常日志、单元测试、安全、MySQL、工程结构和附录。
- 采纳边界：只吸收仍稳定且能补足现有规则的对象比较、序列化兼容、`finally`、依赖治理、SQL 投影和索引类型一致性等内容。
- 不吸收：不复制正文、示例或完整目录；不吸收机械作者日期、固定覆盖率、所有 POJO 必须包装类型、固定数据库字段、统一禁用外键和服务器运行参数。`testXxx` 是团队规则，不归因于该手册。

## 《代码整洁之道》公开学习材料

- 来源：[《代码整洁之道，读书笔记》](https://www.yuque.com/suiyuerufeng-akjad/fenguwuxp/xuz373n9zhrnaswq)，作者“岁月如风”，发布于 2025-05-01 18:54；它是公开读书笔记，不代替 Robert C. Martin 原著。
- 原著公开核验：[InformIT 书目页](https://www.informit.com/store/clean-code-a-handbook-of-agile-software-craftsmanship-9780132350884)与[官方样章 What Is Clean Code?](https://www.informit.com/articles/article.aspx?p=1235624)；作者 Robert C. Martin，2008-08-01 出版，ISBN `9780132350884`。
- 读取状态：2026-07-19 已通过 Codex 应用内浏览器读取语雀页面标题、作者、发布时间和完整正文，并通过出版社书目、目录与官方样章复核原著范围；公开材料覆盖命名、函数、注释、对象与数据结构、错误处理、边界、单元测试、类、系统、迭进和并发。
- 采纳边界：只吸收能补足通用 Java 规则且可形成 Review / 测试证据的命令与查询分离、FIRST 测试质量和第三方依赖学习 / 兼容测试；源码级审美、重构与架构裁决仍归 `senior-software-architect`。
- 不吸收：不复制原文、示例、作者口吻或完整目录；不把每个测试一个断言、统一未检查异常、全面禁止 null、固定函数 / 类行数或顺手清理所有旧代码升级成机械强制规则。

## Wind 知识库与项目族公开样本

- 来源：[Wind 语雀知识库](https://www.yuque.com/suiyuerufeng-akjad/wind)（book id `37135667`）、[wind-middleware](https://github.com/fengwuxp/wind-middleware)、Wind 企业集成组件和[wind-security](https://github.com/fengwuxp/wind-security)。
- 知识库读取状态：2026-08-11 已通过 Codex 应用内浏览器逐页读取 `article#content`；目录 63 篇，63/63 正文非空且标题匹配。页面公开可读但未声明再分发许可，本仓库只保留来源、读取状态、结构化提炼和冲突，不保存正文、图片或大段摘录。
- 源码证据规则：公开样本可按当前版本复核；本地对照源码只在当前任务明确授权内读取，历史授权不得外推。只有已跟踪源码和有效断言测试可作为局部证据，未提交工作区不作为稳定契约。
- 采纳边界：知识库用于理解项目意图、用法和团队约规，当前源码与已跟踪测试用于核对 API 和局部行为；只提炼端口适配、Starter、Trace、请求签名、安全和企业集成等可迁移模式，具体见 `wind-architecture-patterns.md`。
- 证据边界：模块、接口、适配器或单元测试存在，不等于当前消费方已解析、装配、启用或通过真实环境集成，更不等于已发布或生产可用。未跟踪、`@Disabled`、占位凭据或只打印无断言的测试不作为通过证据。
- 不吸收：不复制实现、正文或厂商操作手册；不把固定 JVM、容器、K8s、云效参数或历史目录写成稳定规则；不吸收“timestamp + nonce 已防重放”“签名可替代 TLS”“内网路径等于可信身份”“四类 Service 必须全部存在”等与当前证据冲突的结论。

## 本地业务项目源码样本

- 来源：两个本地业务 Java 仓库的只读源码快照；项目标识和 commit 已脱敏。
- 读取状态：2026-07-30 已核对根 POM、代表性 face/impl POM、face 模型、ApplicationService / ServiceImpl 与集中测试。工作区在途变更和无关脏项均未作为规则依据。
- 采纳边界：两个样本共同支持 face/impl 契约分层与入口模块装配；代表性 impl 依赖自身 face 和 infrastructure，跨业务 impl 依赖只作为耦合风险样例；以 `@ContextConfiguration` / `@Import` 按接口注入服务的测试用于提炼最小 Spring 装配证据。face 模型中的 ORM 注解和第三方 SDK 类型只作为契约泄漏样例。
- 不吸收：不复制私有业务代码、包名或依赖版本，不把存量反例升级为推荐实践，不据此要求全仓批量迁移；只约束新建和本次修改，并由目标项目 owner 决定存量治理顺序。

## JSpecify 官方文档

- 来源：[JSpecify Nullness User Guide](https://jspecify.dev/docs/user-guide/) 与 [Annotation API](https://jspecify.dev/docs/api/)；JSpecify 1.0.0 定义 `@Nullable`、`@NonNull`、`@NullMarked`、`@NullUnmarked` 四个注解。
- 读取状态：2026-07-22 已核对官方 User Guide、`@NullMarked` API 和注解总览。
- 采纳边界：按注解及实际作用域区分非空、可空和未指定空值语义；明确 JSpecify 是静态分析契约，不替代不可信边界的运行时参数校验。
- 不吸收：不要求未使用 JSpecify 的项目新增依赖，不把分析器告警级别或特定工具行为写成统一规则。

## Bean Validation 与 Spring MVC 官方文档

- 来源：[Bean Validation 2.0 规范](https://beanvalidation.org/2.0/spec/)、[Jakarta Validation 3.1](https://jakarta.ee/specifications/bean-validation/3.1/)与[Spring MVC Validation](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html)。
- 读取状态：2026-07-22 已核对 `javax.validation` / `jakarta.validation` 的 `@NotNull`、`@NotBlank`、`@NotEmpty`、`@Valid` 语义及 Spring MVC 控制层触发条件。
- 采纳边界：按当前 artifact 与调用路径区分运行时协议入口和公共能力提供方；前者使用 `@Valid` / `@Validated` 执行输入验证，Service / ServiceImpl 不出现这两个触发注解。Service 参数及其 Request、Command、DTO 可以用约束注解声明调用前置契约；调用路径未证明或公共 Service 可被直接调用时，由显式业务断言或领域校验保护必要前置条件。
- 不吸收：不把注解存在、依赖在 classpath 或 Service 被 Spring 管理当成运行时验证已执行的证据；不把 Service 方法校验作为入口验证的替代方案，不禁止 Service 契约使用 `jakarta.validation.constraints.*` 声明前置条件，也不因能力 artifact 没有 Controller 而判缺陷。

## Spring 依赖注入与 Lombok 构造器

- 来源：[Spring Framework Dependency Injection](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html) 与 [Lombok constructor annotations](https://projectlombok.org/features/constructor)。
- 读取状态：2026-07-30 已核对 Spring 对必需依赖使用构造器、可选依赖使用 setter / 配置方法的建议，以及 Lombok `@RequiredArgsConstructor` 和 `@AllArgsConstructor` 的字段选择语义。
- 采纳边界：Spring Bean 的必需依赖使用构造注入；模块已有 Lombok 时，用 `private final` 字段 + `@RequiredArgsConstructor` 生成必需参数构造器，没有 Lombok 或装配契约特殊时使用显式构造器。
- 不吸收：不要求项目新增 Lombok，不把 setter 注入机械判错，不把生成构造器、stereotype 或编译通过写成 Bean 唯一装配和 Spring 上下文验证已经完成。
