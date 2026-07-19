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

## Wind 项目族公开样本

- 来源：[wind-middleware](https://github.com/fengwuxp/wind-middleware)、[wind-integration](https://github.com/fengwuxp/wind-integration)、[wind-security](https://github.com/fengwuxp/wind-security)。
- 读取状态：历史提炼已落入 `wind-architecture-patterns.md`，原始读取日期和 commit/tag 未留存；2026-07-17 本轮只复核本地提炼与来源链接，未重新读取公开仓库。涉及当前目录、API、依赖版本或实现事实时，必须重新读取并记录 commit/tag。
- 采纳边界：只提炼端口适配、Starter、Trace、安全和企业集成等稳定模式；具体规则见 `wind-architecture-patterns.md`。
- 不吸收：不复制实现，不把公开仓库的历史目录、依赖版本或临时实现写成当前项目必须照搬的事实。
