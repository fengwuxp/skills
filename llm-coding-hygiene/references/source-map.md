# LLM 编码卫生来源地图

## 使用时机

需要追溯 Karpathy Guidelines 的原始原则、许可证或本仓库扩展边界时读取。执行普通编码卫生检查不必加载本文。

## 上游来源

- 仓库：[`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills)
- 固定版本：[`2c606141936f1eeef17fa3043a72095b4765b9c2`](https://github.com/multica-ai/andrej-karpathy-skills/blob/2c606141936f1eeef17fa3043a72095b4765b9c2/skills/karpathy-guidelines/SKILL.md)
- 核验日期：2026-08-18
- 许可证：MIT
- 吸收原则：`Think Before Coding`、`Simplicity First`、`Surgical Changes`、`Goal-Driven Execution`。

用户本轮还提供了 `forrestchang/andrej-karpathy-skills` 旧地址和完整文本；当前权威来源已归一到上述 `multica-ai` 固定版本，旧地址只保留为输入来源历史，不作为运行时依赖。

## 本仓库扩展

- 把“最小修改”补成共享根因规则：先检查全部调用方；同一语义在共享边界修一次，不同契约保留差异。
- 把“简单优先”补成安全边界：不得删除安全、权限、持久化、幂等、审计、错误处理或必要测试。
- 明确与知止者、`senior-software-architect`、`wind-coding-conventions`、`security-engineering-expert`、Ponytail 和 Superpowers 的 Owner 边界。
- 用触发 fixture、行为契约、validator 和前向压力测试验证，不把静态文字存在当成行为已经改善。

## 不吸收

- 不复制上游插件安装、市场、宣传、示例或完整正文。
- 不引入上游运行时依赖、Hook、持久化目录、联网、Git、发布或生产权限。
- 不把该来源替代项目规则、工程实现、TDD、源码 CR、独立 Checker 或人类 Owner。
