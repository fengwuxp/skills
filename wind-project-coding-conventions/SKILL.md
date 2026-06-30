---
name: wind-project-coding-conventions
description: Wind/Nobe Java 项目编码约规 Skill。项目 AGENTS.md 明确 opt-in Wind 约规，或用户要求判断 face/impl、服务分层、模型归位、Entity 不外露、ServiceImpl 和 TDD/CR 是否符合项目约规时触发。
---

# Wind Project Coding Conventions

## 定位

你是 Wind/Nobe Java 项目编码约规的权威规则包，负责在项目明确 opt-in 后提供 face/impl、服务分层、模型归位、Entity 不外露、MyBatis Flex、ServiceImpl 和测试边界的判断标准。

本 Skill 只回答“这个项目是否应该按 Wind 约规做、具体约规是什么、当前设计或代码是否偏离约规”。源码级架构设计、TDD、Bug 修复、代码 CR 和生产风险判断继续交给 `资深架构师`；结构化 Java Service 生成继续交给 `java-service-code-generator`。

## 触发条件

- 项目 `AGENTS.md`、任务说明或用户明确写明“遵守 Wind 项目编码约规”。
- 用户要求检查 Wind/Nobe 风格项目的 `face` / `impl` 模块边界、接口放置、模型归属、分包规则或 ServiceImpl 实现方式。
- 用户要求判断 DTO、Request、Query、Command、Event、VO、Entity、Mapper、MapStruct、Converter、callback/spi、listener、webhook、core、infrastructure 应放在哪个模块或包。
- 用户要求基于 Wind 约规做服务层、基础服务、方法签名、服务命名、模型命名、枚举命名、ApplicationService、Entity 不外露、MyBatis Flex 查询或 TDD/CR 的正反例判断。

## 工作流程

1. 先确认项目是否 opt-in：以项目 `AGENTS.md`、用户明确说明或任务上下文为准；没有 opt-in 时，不把 Wind 约规强套到普通 Java 项目。
2. 读取 `references/wind-project-coding-conventions.md`，按任务定位模块边界、模型归位、服务职责、Entity 边界、DAL/外部端口和测试约束。
3. 用户要求最佳实践、示例、正反例或 AI Maker 参照时，再读取 `references/wind-project-coding-examples.md`。
4. 输出时把结论分成：适用性、触发的 Wind 约规、当前偏差、建议改法、需要回到架构师或代码生成器的后续动作。
5. 如果涉及真实源码修改、TDD、深度 CR、生产发布或风险回滚，只给规则判断和路由建议，不替代 `资深架构师` 的执行与验证。

## Reference 路由

- `references/wind-project-coding-conventions.md`：Wind 项目编码约规主规则；任何 opt-in Wind 约规任务都应读取。
- `references/wind-project-coding-examples.md`：正反例和最佳实践；只有用户要求示例、参考或 AI Maker 落地参照时读取。

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
- 不为了套分层新增浅服务、透传接口、似是而非的 ApplicationService 或 Mapper 包装。
- 生产源码路径不得新增内存版业务 Service、模拟模块或看上去可用的样子货。
- 项目统一编码规范和附近代码风格优先；没有统一规范时，再按 Wind 约规和已有代码风格收敛。
