# Goal 输入兼容

本文只保留旧输入迁移，不再定义当前执行状态。Goal 不是运行模式；用户提出 Goal、长任务或持续推进时，读取 `execution-specification.md`，把目标落入项目已有 `OpenSpec / Spec / Issue / 任务计划`，不创建或恢复运行时 Goal。

## 使用时机

- 历史文档、旧 fixture 或用户原话仍使用 Goal / Goal Ledger / `/goal`。
- 需要判断旧状态怎样迁移为项目执行规范，而不形成双权威。

## 不适用场景

- 新任务不得以本文件创建 Goal 卡、Goal 状态机或 Goal Ledger。
- 不把旧 Goal ID、状态、摘要或工具状态作为授权、恢复入口或完成证据。

## 读取后必须产出

- 旧 Goal 到项目执行规范的唯一映射位置。
- 需要保留的 `origin / provenance` 和必须重新核验的承重字段。
- 明确结论：不创建或恢复运行时 Goal，后续只按当前切片推进。

## 需要继续读取的 reference

- 唯一执行权威：`execution-specification.md`。
- 切片内反馈循环：`delivery-execution-control.md`。
- 跨上下文恢复：`context-handoff.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 旧 Goal 请求 | `execution-specification.md` 的“正名与迁移” | 不创建运行时 Goal |
| 旧 Goal Ledger 恢复 | 当前项目执行规范与一手来源 | 不信任旧摘要 |
| 新增长任务 | 直接读取 `execution-specification.md` | 不再扩写本文件 |
