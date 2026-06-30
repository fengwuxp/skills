# Wind 项目编码示例兼容索引

本文是 `资深架构师` Skill 的兼容索引。Wind 项目编码最佳实践示例已迁入独立 `wind-project-coding-conventions` Skill，避免架构师目录和规则 Skill 保留两份内容导致漂移。

## 使用时机

- 架构师在 Wind opt-in 项目中做源码级设计、TDD、CR 或实现验收，需要参考服务分层、模型边界、MyBatis Flex、ServiceImpl 包位或测试替身边界的正反例。

## 不适用场景

- 只需要查看 Wind 示例本身时，不读取本文件，直接读取独立 `wind-project-coding-conventions` Skill 的示例 reference。
- 未 opt-in Wind 约规的项目，不强行使用这些示例。

## 读取后必须产出

- 当前任务是否需要 Wind 示例；应读取的权威示例 reference；架构师继续执行的源码级检查点和验证命令。

## 需要继续读取的 reference

- 示例权威：`wind-project-coding-conventions` Skill 的 `references/wind-project-coding-examples.md`。
- 规则权威：`wind-project-coding-conventions` Skill 的 `references/wind-project-coding-conventions.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| Wind 示例 / 正反例 / AI Maker 纠偏 | 独立 `wind-project-coding-conventions` Skill 示例 reference | 不把本索引当示例正文 |
| 源码级 TDD / CR / 验证 | 先取 Wind 示例，再回架构师测试和 CR reference | 不停留在示例类比 |
