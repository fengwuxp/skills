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
| 核验 Wind 项目族经验 | `Wind 项目族公开样本` | 不把公开样本当当前项目事实 |

## 阿里 Java 开发手册

- 来源：[《阿里巴巴Java开发手册》](https://www.yuque.com/iv8gga/qgf69v)，页面版本历史包含 1.3.1（2017-11-30）。
- 读取状态：2026-07-16 已通过 Codex 应用内浏览器逐章读取目录中的编程规约、异常日志、单元测试、安全、MySQL、工程结构和附录。
- 采纳边界：只吸收仍稳定且能补足现有规则的对象比较、序列化兼容、`finally`、依赖治理、SQL 投影和索引类型一致性等内容。
- 不吸收：不复制正文、示例或完整目录；不吸收机械作者日期、固定覆盖率、所有 POJO 必须包装类型、固定数据库字段、统一禁用外键和服务器运行参数。`testXxx` 是团队规则，不归因于该手册。

## Wind 项目族公开样本

- 来源：[wind-middleware](https://github.com/fengwuxp/wind-middleware)、[wind-integration](https://github.com/fengwuxp/wind-integration)、[wind-security](https://github.com/fengwuxp/wind-security)。
- 读取状态：历史提炼已落入 `wind-architecture-patterns.md`，原始读取日期和 commit/tag 未留存；2026-07-17 本轮只复核本地提炼与来源链接，未重新读取公开仓库。涉及当前目录、API、依赖版本或实现事实时，必须重新读取并记录 commit/tag。
- 采纳边界：只提炼端口适配、Starter、Trace、安全和企业集成等稳定模式；具体规则见 `wind-architecture-patterns.md`。
- 不吸收：不复制实现，不把公开仓库的历史目录、依赖版本或临时实现写成当前项目必须照搬的事实。
