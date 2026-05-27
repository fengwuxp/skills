# 架构师公开来源与应用记录

本文记录 `资深架构师` Skill 已参考的公开工程资料、读取状态、应用位置和不吸收边界。它不是架构方法论正文；处理具体架构、Review、测试、生产变更或 AI 协作时，仍应读取对应专项 reference。

## 使用时机

- 需要核对架构师 Skill 吸收过哪些公开来源、来源许可证、读取日期和应用位置。
- 用户要求继续从外部工程实践仓库、文章或指南中提炼可迁移规则。
- 修改 `README.md` 外部参考来源、`coding-review-deep-dive.md`、`workflow.md`、`production-readiness.md` 或相关验证脚本前，需要确认既有归因边界。

## 不适用场景

- 不用于直接回答代码 Review、架构方案、生产变更或测试设计；这些任务应回到对应 reference。
- 不把外部资料当作当前项目事实、组织制度或生产审批结论。
- 不复制外部仓库的脚本、模板、品牌表达、大段原文或未审查资产。

## 读取后必须产出

- 来源状态：URL、读取日期、许可证或归因要求、读取到的公开内容范围。
- 应用记录：迁移成了哪些规则，落到哪些仓库文件。
- 不吸收边界：哪些内容不适合进入本 Skill，原因是什么。

## 需要继续读取的 reference

- 代码 Review 方法读 `coding-review-deep-dive.md`。
- PR、提交、验证和 Git 边界读 `workflow.md`。
- 生产、紧急变更和上线边界读 `production-readiness.md`。
- 外部来源安全和仓库级治理读根目录 `AGENTS.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核对 Google 工程实践应用记录 | `已参考的公开来源`、`应用记录` | 不重新读取所有 Review 正文 |
| 新增外部来源 | `读取与归因规则`、`提炼边界` | 不把未读正文的来源标为已吸收 |
| 审查来源是否可继续使用 | `读取与归因规则`、`已参考的公开来源` | 不用历史记录替代最新核验 |

## 读取与归因规则

- 分析、提炼或吸收外部资料时，必须以实际读取到的正文、仓库文件或官方页面为依据。
- 对无法读取正文、只剩验证页、动态页面失败、仓库不可访问或许可证不明的来源，只能标为待核验，不得作为已吸收来源。
- 进入 Skill 的内容只保留可迁移的方法、检查项、路由和边界；不复制原文、示例、图像、品牌表达或组织内部流程。
- 涉及许可证、归因或派生要求时，README 或本文必须记录来源和边界；需要复用具体文本、脚本或资产时必须另做许可证确认和供应链安全审查。

## 已参考的公开来源

### google/eng-practices

- 来源：`https://github.com/google/eng-practices`
- 公开页面：`https://google.github.io/eng-practices/`
- 读取日期：2026-05-27
- 读取状态：GitHub 仓库公开可读；目录树显示公开内容集中在 `review/` 下的 Code Review Guidelines、Reviewer Guide、Change Author Guide 和 emergencies 文档。
- 许可证：仓库 README 声明文档使用 CC-BY 3.0；本仓库只保留提炼后的规则和来源链接，不复制大段原文。

已读取文件：

- `README.md`
- `review/reviewer/standard.md`
- `review/reviewer/looking-for.md`
- `review/reviewer/navigate.md`
- `review/reviewer/speed.md`
- `review/reviewer/comments.md`
- `review/reviewer/pushback.md`
- `review/developer/cl-descriptions.md`
- `review/developer/small-cls.md`
- `review/developer/handling-comments.md`
- `review/emergencies.md`

应用记录：

| 应用位置 | 已吸收内容 |
| --- | --- |
| `README.md` | 新增公开参考来源记录，说明只吸收 Review 与 Change Author 原则，并保留 CC-BY 3.0 归因边界。 |
| `coding-review-deep-dive.md` | 补充代码健康优先于完美主义、评论分级、争议处理、评论代码不评论人、Review 导航顺序和审查范围说明。 |
| `workflow.md` | 补充自包含小变更、测试随变更、重构与功能拆分、提交/PR 说明质量和长期版本记录要求。 |
| `production-readiness.md` | 补充紧急变更边界，区分真实紧急情况与软期限，并要求事后完整 Review、测试和复盘。 |
| `scripts/validate-trigger-paths.py` | 增加关键字符串断言，防止来源记录和核心 Review/PR/紧急变更规则漂移。 |

未吸收内容：

- 不把 `google/eng-practices` 扩展为完整架构设计、DDD、分布式一致性、安全架构或生产韧性方法论。
- 不复制 Google 内部术语、示例、组织流程、评审时效数字或只适用于 Google 工具链的表达。
- 不引入外部脚本、GitHub Action、站点构建配置或仓库运行逻辑。

## 提炼边界

- 代码评审类来源适合沉淀为 Review 判断顺序、评论分级、协作礼仪、变更颗粒度和提交说明质量。
- 生产、资金、安全、合规、外部 API、SDK、云产品或法规规则，不能从通用 Review 指南推导结论，必须回到对应官方来源和项目事实。
- 与现有 Skill 规则重复时，只升级一个权威位置；其他文件只做摘要和链接，避免规则漂移。
