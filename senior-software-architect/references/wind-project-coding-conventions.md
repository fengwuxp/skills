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

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Wind opt-in 规则判断 / 包位归属 / 示例 | `wind-project-coding-conventions` Skill | 不复制本文件作为规则全文 |
| Wind opt-in 源码设计 / TDD / CR / 验证 | 先取 Wind 规则，再读架构师源码级 reference | 不把规则判断替代真实源码验证 |
