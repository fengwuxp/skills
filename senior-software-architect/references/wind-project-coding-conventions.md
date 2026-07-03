# Wind 项目编码约规兼容索引

本文是 `资深架构师` Skill 的兼容索引。项目本地 `AGENTS.md` 明确 opt-in Wind 项目编码约规时，权威规则优先使用独立 `wind-project-coding-conventions` Skill；架构师只负责源码级设计、TDD、CR、风险判断和验证闭环。

## 使用时机

- 架构师正在处理 Java/Spring/Wind/Nobe 项目，且项目 `AGENTS.md`、任务说明或用户明确要求遵守 Wind 项目编码约规。
- 任务涉及 face/impl、ServiceImpl、ApplicationService、基础服务、DTO/Request/Query/Command、Entity 不外露、MyBatis Flex、callback/spi、listener、webhook、core、infrastructure 或 TDD/CR。

## 不适用场景

- 未 opt-in 的普通 Java/Spring 项目，不强行套 Wind 约规；先按 `coding-standards.md`、`project-governance-service-api-modeling.md` 和附近代码判断。
- 只需要规则判断、包位归属或正反例时，不在本文件展开规则，直接读取 `wind-project-coding-conventions` Skill。

## 读取后必须产出

- 是否命中 Wind opt-in；需要交给 `wind-project-coding-conventions` 的规则问题；架构师继续负责的源码设计、TDD、CR、验证和残余风险。

## 需要继续读取的 reference

- Wind 规则权威：`wind-project-coding-conventions` Skill 的 `references/wind-project-coding-conventions.md`。
- Wind 示例权威：`wind-project-coding-conventions` Skill 的 `references/wind-project-coding-examples.md`。
- 源码级实现、测试或 CR：回到 `coding-standards.md`、`project-governance-service-api-modeling.md`、`coding-review-deep-dive.md`、`testing.md` 和 `testing-practices.md`。
- 低成本结构守卫：可运行 `wind-project-coding-conventions/scripts/check_wind_conventions.py --root <project>`，再由架构师按源码事实、测试结果和项目本地规则定级。

## 重复规则归位

- 通用 Java 命名、异常、技术日志、敏感信息、数据库 DDL、依赖治理、Spring/Lombok/MapStruct 使用和测试方法论，仍以架构师通用 reference 为准。
- Wind opt-in 后的 face/impl、模型包位、基础服务模板、服务查询方法、`XxxQuery` 字段后缀、内网 API `/inc/basic` / `/inc/secure`、系统字典/国际化和业务事件 Key，回到 `wind-project-coding-conventions`。
- 两边都提到 Service/API/DTO/Query 时，架构师负责源码事实、测试和风险闭环，Wind Skill 负责项目特化规则；不要把通用四层服务模型机械强套到 Wind 项目，也不要用 Wind 项目特化规则替代所有 Java 项目治理。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Wind opt-in 规则判断 / 包位归属 / 示例 | `wind-project-coding-conventions` Skill | 不复制本文件作为规则全文 |
| Wind opt-in 源码设计 / TDD / CR / 验证 | 先取 Wind 规则，必要时运行结构守卫，再读架构师源码级 reference | 不把规则判断或脚本输出替代真实源码验证 |
