---
name: wind-coding-conventions
description: Java 项目编码约规 Skill。用户要求检查包含 Java 源码的 Java/Spring 项目编码规范或初始化项目 AGENTS.md 时触发；项目声明、依赖、包名或类型表明属于 Wind/Nobe 时叠加专项约规。仅有 JVM、Maven 或 Gradle 上下文不触发；源码设计、代码 CR、Bug 修复、TDD、验证和代码生成不触发。
---

# Java/Wind 编码约规

## 定位

本 Skill 是知止者按需装载的 Java 项目分层约规能力包。Codex 可按精确 description 隐式加载本 Skill；若与 `wise-agent` 同时加载，仍由同一 Agent 统一目标和交付，不形成第二人格。所有包含 Java 源码的项目先使用通用 Java 约规；Spring、JSpecify、Lombok、MapStruct、MyBatis 等规则按实际依赖或源码上下文启用；只有命中 Wind/Nobe 信号时，才叠加 face/impl、服务分层、模型归位、Entity 不外露、ServiceImpl、基础服务并发/锁边界、查询字段/方法、内网 API 和字典国际化等 Wind 专项规则。`CurrencyIsoCode` 是 Wind 项目币种字段的通用强制项，不属于依赖按需规则。

本 Skill 只回答“当前 Java 项目应启用哪层约规、具体约规是什么、当前设计或代码是否偏离约规”。纯约规检查由本 Skill 主责；源码设计、代码 CR、Bug 修复、TDD 和验证不触发本 Skill 主责，只把本 Skill 的通用 Java 与按需 Wind 规则作为输入交给 `senior-software-architect`；结构化 Java Service 生成继续交给 `java-service-code-generator`。

## 触发条件

- 用户要求检查包含 Java 源码的 Java/Spring 项目编码规范、契约、异常日志、依赖适配、数据库访问、测试代码或项目 `AGENTS.md` 约规；Maven、Gradle 或 JVM 只能作为构建上下文，不能单独证明适用本 Skill。
- 项目 `AGENTS.md`、任务说明、依赖坐标、包名、import、类型或模块结构表明项目属于 Wind/Nobe 项目族。
- 用户要求检查 Wind/Nobe 风格项目的 `face` / `impl` 模块边界、接口放置、模型归属、分包规则或 ServiceImpl 实现方式。
- 用户要求判断 DTO、Request、Query、Command、Event、VO、Entity、Mapper、MapStruct、Converter、callback/spi、listener、webhook、core、infrastructure 应放在哪个模块或包。
- 用户要求基于 Wind 约规判断服务层、基础服务、并发与锁边界、方法签名、服务命名、模型命名、枚举命名、ApplicationService、Entity 不外露或 MyBatis Flex 查询等规则条目与正反例；真实源码 CR 或 TDD 交给 `senior-software-architect`。
- 用户要求检查服务查询方法 `get/find/query/exists/count/stats/summary`、`XxxQuery` 字段后缀、`/inc/basic` / `/inc/secure` 内网 API、安全等级、系统字典、国际化 Key 或业务事件 `eventKey`。
- 用户要求判断 ServiceImpl 是否应移除 Mapper 直连、是否应补强实体基础服务，或组合、生命周期、应用层服务应依赖哪个服务契约。
- 用户要求为遵循 Wind 约规的项目初始化或改进项目本地 `AGENTS.md`，让 知止者能按项目约规调度产品、架构、Wind 规则和代码生成能力。
- 用户要求把 Wind 约规接入 Open Code Review / OCR、`.opencodereview/rule.json` 或外部代码评审工具时，只提供规则摘要和边界判断。

## 工作流程

1. 先读项目 `AGENTS.md`、`pom.xml` / Gradle 配置、相关源码包与 import、模块结构和用户任务上下文，记录实际技术信号；不能读取时只使用用户已给事实，不猜依赖。
2. 任何包含 Java 源码的项目都先读取 `references/java-coding-conventions.md`；只启用与当前 JDK、框架、依赖和任务匹配的章节，不因 reference 提到某个库就要求项目新增该库。
3. 普通 Java 项目初始化或改进 `AGENTS.md` 时，只根据项目事实给最小 patch：记录 JDK/构建工具、项目本地规范优先级、实际依赖对应的约规章节、构建/测试/静态检查命令和验证边界；不读取 Wind 项目模板，不写 face/impl、Wind API 或 Wind 类型规则。
4. 出现以下任一高置信度信号时叠加 Wind 专项：用户、任务或 `AGENTS.md` 明确声明 Wind/Nobe；Maven/Gradle 坐标、包名或 import 明确属于 Wind/Nobe；源码使用 `WindPagination`、`WindQuery`、`CurrencyIsoCode` 等 Wind 类型；`face` / `impl` 结构与 Wind 类型或项目族上下文同时出现。只有孤立的 `face`、`impl`、`ServiceImpl` 或通用 MyBatis 用法时，不判为 Wind。
5. 命中 Wind 后读取 `references/wind-coding-conventions.md`：face/impl、Entity 不外露、服务/模型边界和所有币种字段使用 `CurrencyIsoCode` 属于 Wind 通用专项；JSpecify、MapStruct、MyBatis Flex 等依赖专项仍按实际依赖或源码启用；固定数据库字段只按项目已采用的 Wind MySQL 表约规启用。用户要求初始化或改进 Wind 项目 `AGENTS.md` 时再读 `references/wind-project-agents-template.md`；需要正反例时读 `references/wind-coding-examples.md`；涉及 Wind 项目族端口、Starter、Trace、安全或企业集成能力时读 `references/wind-architecture-patterns.md`。
6. 输出时把结论分成：适用层级、上下文证据、触发约规、当前偏差、建议改法、需要回到架构师或代码生成器的后续动作。
7. 如果涉及真实源码修改、TDD、深度 CR、生产发布或风险回滚，只给规则判断和路由建议，不替代 `senior-software-architect` 的执行与验证。
8. 如果涉及 Open Code Review / OCR，只说明哪些 Wind 约规可作为 `.opencodereview/rule.json` 或 `--background` 的规则输入；OCR 输出仍交 `senior-software-architect` 做源码级判读。
9. 需要低成本结构守卫时，普通 Java 项目运行 `scripts/check_wind_conventions.py --profile java --root <project>`，Wind 项目运行默认的 `--profile wind`；脚本只检查高信号红线，不替代源码级 CR、测试或项目本地规则。

## Reference 路由

- `references/java-coding-conventions.md`：所有 Java 项目的通用入口；Java/Spring 编码、契约、异常日志、Lombok/MapStruct、数据库、MyBatis Flex、安全和测试代码细则按依赖与任务读取；普通 Java `AGENTS.md` 初始化也只从本文件提炼最小项目 patch。
- `references/wind-coding-conventions.md`：Wind 编码约规主规则；只有命中 Wind/Nobe 高置信度信号时读取。
- `references/wind-architecture-patterns.md`：Wind 项目族端口、Starter、Trace、安全、查询和企业集成模式；涉及能力复用或架构模式时读取。
- `references/wind-project-agents-template.md`：Wind 项目本地 `AGENTS.md` 初始化 / 改进模板；只有已经命中 Wind/Nobe 高置信度信号且用户要求项目 AGENTS 初始化、改进或 `wise-agent` 项目约规入口时读取。
- `references/wind-coding-examples.md`：正反例和最佳实践；只有用户要求示例、参考或 AI Maker 落地参照时读取。
- `references/source-map.md`：外部来源、读取状态、采纳边界和不吸收项；核验规则来源或演进约规时读取。
- `scripts/check_wind_conventions.py`：离线结构守卫；普通 Java 用 `--profile java`，Wind 项目使用默认的 `--profile wind`，需要扫描真实项目或做规则自测时运行。

## 输出要求

优先使用简短的 Java Rule Check Card：

```text
适用层级：通用 Java / 依赖专项 / Wind 专项
上下文证据：
触发约规：
当前偏差：
建议改法：
后续 owner：
验证方式：
```

## 红线

- 所有 Java 项目都加载通用约规；没有 Wind/Nobe 高置信度信号时，不加载 Wind face/impl、基础服务或模型包专项规则。
- 对外接口、Controller、Facade、Adapter、跨模块接口和事件契约不得暴露 Entity、Mapper、Repository 或 MyBatis Page。
- 只有 Wind 专项启用后，币种字段才统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode`，不得用 String、业务私有枚举或魔法常量承载。
- 业务唯一性和请求重放幂等分层处理：业务身份与业务不变量优先由表内业务 UK、联合 UK、状态条件或版本约束保护；外部 `Idempotency-Key` / `requestSn` 可以用于请求重放去重，但不得冒充业务身份，必须定义作用域、参数摘要、有效期、冲突和结果回放语义。
- 基础服务必须识别并发下的业务不变量，但不得仅因“未来可能并发”预埋本地锁、分布式锁或锁 Wrapper；按唯一性、状态流转和一般读改写分别优先使用表内业务 UK 或联合 UK、带前置状态的原子条件更新和乐观锁。事务只保证本地操作的原子提交和回滚，普通 `SELECT -> Java 校验 -> UPDATE` 即使使用 `@Transactional` 也不能单独防止丢失更新；只有上述机制不足且有可复核证据时才引入已验证安全语义的锁原语。
- 只有 Wind 专项启用后，服务查询方法和 `XxxQuery` 字段才按 Wind 的 `get/find/query`、字段后缀和查询契约统一规则检查。
- 只有 Wind 专项启用后，内网 API 才按 `/inc/basic/**` 与 `/inc/secure/**` 的显式安全等级检查。
- 只有 Wind 专项启用后，系统字典、国际化和业务事件才按 Wind 的稳定 Key + params 规则检查。
- 测试与 TDD 必须按公开契约黑盒验证，观察 Controller、face Service、ApplicationService、ServiceImpl 的业务结果、状态流转、持久化事实、异常、幂等和可观察副作用；不得为凑绿感知私有方法、内部调用顺序、Mapper/Repository 调用次数、临时字段、内部 Mock 交互或当前实现步骤。
- 不为了套分层新增浅服务、透传接口、似是而非的 ApplicationService 或 Mapper 包装。
- 生产源码路径不得新增内存版业务 Service、模拟模块或看上去可用的样子货。
- 项目统一编码规范、构建检查和附近代码风格优先；没有统一规范时，先按通用 Java 约规收敛，命中 Wind/Nobe 信号后再叠加 Wind 专项。
