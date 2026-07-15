---
name: wind-project-coding-conventions
description: Wind/Nobe Java 项目编码约规 Skill。项目 AGENTS.md 明确 opt-in Wind 约规，或用户要求初始化改进 Wind 项目 AGENTS；审查 face-impl、服务模型边界、Entity、幂等唯一键、基础服务并发/锁边界、查询 API 字典和 TDD CR 时触发。
---

# Wind Project Coding Conventions

## 定位

你是 Wind/Nobe Java 项目编码约规的权威规则包，负责在项目明确 opt-in 后提供 face/impl、服务分层、模型归位、Entity 不外露、MyBatis Flex、ServiceImpl、基础服务并发/锁边界、查询字段/方法、内网 API、字典国际化和测试边界的判断标准。

本 Skill 只回答“这个项目是否应该按 Wind 约规做、具体约规是什么、当前设计或代码是否偏离约规”。源码级架构设计、TDD、Bug 修复、代码 CR 和生产风险判断继续交给 `资深架构师`；结构化 Java Service 生成继续交给 `java-service-code-generator`。

## 触发条件

- 项目 `AGENTS.md`、任务说明或用户明确写明“遵守 Wind 项目编码约规”。
- 用户要求检查 Wind/Nobe 风格项目的 `face` / `impl` 模块边界、接口放置、模型归属、分包规则或 ServiceImpl 实现方式。
- 用户要求判断 DTO、Request、Query、Command、Event、VO、Entity、Mapper、MapStruct、Converter、callback/spi、listener、webhook、core、infrastructure 应放在哪个模块或包。
- 用户要求基于 Wind 约规做服务层、基础服务、并发与锁边界、方法签名、服务命名、模型命名、枚举命名、ApplicationService、Entity 不外露、MyBatis Flex 查询或 TDD/CR 的正反例判断。
- 用户要求检查服务查询方法 `get/find/query/exists/count/stats/summary`、`XxxQuery` 字段后缀、`/inc/basic` / `/inc/secure` 内网 API、安全等级、系统字典、国际化 Key 或业务事件 `eventKey`。
- 用户要求判断 ServiceImpl 是否应移除 Mapper 直连、是否应补强实体基础服务，或组合、生命周期、应用层服务应依赖哪个服务契约。
- 用户要求为遵循 Wind 约规的项目初始化或改进项目本地 `AGENTS.md`，让 产研协同体系能按项目约规调度产品、架构、Wind 规则和代码生成能力。
- 用户要求把 Wind 约规接入 Open Code Review / OCR、`.opencodereview/rule.json` 或外部代码评审工具时，只提供规则摘要和边界判断。

## 工作流程

1. 先确认项目是否 opt-in：以项目 `AGENTS.md`、用户明确说明或任务上下文为准；没有 opt-in 时，不把 Wind 约规强套到普通 Java 项目。
2. 读取 `references/wind-project-coding-conventions.md`，按任务定位模块边界、模型归位、服务职责、Entity 边界、DAL/外部端口和测试约束。
3. 用户要求初始化或改进项目 `AGENTS.md` 时，读取 `references/wind-project-agents-template.md`，只输出项目本地模板草案或最小 patch 建议。
4. 用户要求最佳实践、示例、正反例或 AI Maker 参照时，再读取 `references/wind-project-coding-examples.md`。
5. 输出时把结论分成：适用性、触发的 Wind 约规、当前偏差、建议改法、需要回到架构师或代码生成器的后续动作。
6. 如果涉及真实源码修改、TDD、深度 CR、生产发布或风险回滚，只给规则判断和路由建议，不替代 `资深架构师` 的执行与验证。
7. 如果涉及 Open Code Review / OCR，只说明哪些 Wind 约规可作为 `.opencodereview/rule.json` 或 `--background` 的规则输入；OCR 输出仍交 `资深架构师` 做源码级判读。
8. 需要低成本结构守卫时，可运行 `scripts/check_wind_conventions.py --root <project>`；脚本只检查高信号红线，不替代源码级 CR、测试或项目本地规则。

## Reference 路由

- `references/wind-project-coding-conventions.md`：Wind 项目编码约规主规则；任何 opt-in Wind 约规任务都应读取。
- `references/wind-project-agents-template.md`：Wind 项目本地 `AGENTS.md` 初始化 / 改进模板；只有用户要求项目 AGENTS 初始化、改进或 AI Native 项目约规入口时读取。
- `references/wind-project-coding-examples.md`：正反例和最佳实践；只有用户要求示例、参考或 AI Maker 落地参照时读取。
- `scripts/check_wind_conventions.py`：离线结构守卫；只有需要扫描真实 Wind Java 项目或做规则自测时运行。

## 输出要求

优先使用简短的 Wind Rule Check Card：

```text
适用性：
触发约规：
当前偏差：
建议改法：
后续 owner：
验证方式：
```

## 红线

- 未 opt-in 的普通 Java/Spring 项目，不强行套 Wind face/impl、基础服务或模型包规则。
- 对外接口、Controller、Facade、Adapter、跨模块接口和事件契约不得暴露 Entity、Mapper、Repository 或 MyBatis Page。
- 币种字段统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode`，不得用 String、业务私有枚举或魔法常量承载。
- 业务唯一性和请求重放幂等分层处理：业务身份与业务不变量优先由表内业务 UK、联合 UK、状态条件或版本约束保护；外部 `Idempotency-Key` / `requestSn` 可以用于请求重放去重，但不得冒充业务身份，必须定义作用域、参数摘要、有效期、冲突和结果回放语义。
- 基础服务必须识别并发下的业务不变量，但不得仅因“未来可能并发”预埋本地锁、分布式锁或锁 Wrapper；按唯一性、状态流转和一般读改写分别优先使用表内业务 UK 或联合 UK、带前置状态的原子条件更新和乐观锁。事务只保证本地操作的原子提交和回滚，普通 `SELECT -> Java 校验 -> UPDATE` 即使使用 `@Transactional` 也不能单独防止丢失更新；只有上述机制不足且有可复核证据时才引入已验证安全语义的锁原语。
- 服务查询方法和 `XxxQuery` 字段必须表达业务语义：`get/find/query` 不混用，默认等值查询不加后缀，范围/模糊/集合/空值后缀统一；不得把 `select/load/fetch`、SQL 词或 Repository 语义扩散到服务层契约。
- 内网 API 路径必须显式安全等级：`/inc/basic/**` 只承载低风险内部查询，涉及用户数据、资金、权限或关键业务操作必须走 `/inc/secure/**` 并保留签名/鉴权边界；不得用 header/query 参数隐藏安全等级。
- 系统字典、国际化和业务事件必须使用稳定 Key + params；业务逻辑只能依赖 code、enum 或 errorCode，不得依赖展示文案、中文描述或可变翻译。
- 测试与 TDD 必须按公开契约黑盒验证，观察 Controller、face Service、ApplicationService、ServiceImpl 的业务结果、状态流转、持久化事实、异常、幂等和可观察副作用；不得为凑绿感知私有方法、内部调用顺序、Mapper/Repository 调用次数、临时字段、内部 Mock 交互或当前实现步骤。
- 不为了套分层新增浅服务、透传接口、似是而非的 ApplicationService 或 Mapper 包装。
- 生产源码路径不得新增内存版业务 Service、模拟模块或看上去可用的样子货。
- 项目统一编码规范和附近代码风格优先；没有统一规范时，再按 Wind 约规和已有代码风格收敛。
