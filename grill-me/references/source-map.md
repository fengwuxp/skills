# Grill Me 来源索引

## 使用时机

审查 `grill-me` 的来源、版本、吸收边界、升级依据或供应链安全时读取。日常盘问只读 `question-ledger.md`。

## 不适用场景

- 不用于替代问题台账、决策快照或执行前对账。
- 不因为上游更新就自动安装、覆盖或同步本项目 Skill。
- 不把文章观点、社区热度或工具宣传写成项目事实。

## 读取后必须产出

- 当前项目能力与上游来源的关系。
- 已吸收方法、未吸收内容、核验日期与升级门禁。
- 涉及安装或更新时的来源、权限、验证和停止条件。

## 需要继续读取的 reference

- 盘问协议、历史去重与决策快照读 `question-ledger.md`。
- 跨阶段执行前对账读 `wise-agent/references/delivery-execution-control.md`。
- 需要经典决策校准时装载 `huaxia-practical-wisdom`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核对上游来源 | `公开来源`、`项目吸收结论` | 不读取盘问模板 |
| 评估升级 | `项目吸收结论`、`不吸收边界` | 不因版本号自动覆盖 |
| 做供应链审查 | `公开来源`、`不吸收边界` | 不运行上游脚本或 hooks |

## 公开来源

- [Matt Pocock skills](https://github.com/mattpocock/skills)：2026-07-15 核验上游 `main` 提交 `e9fcdf95b402d360f90f1db8d776d5dd450f9234`、README、`grill-me`、`grilling`、`grill-with-docs` 和 `domain-modeling`。上游当时的 `grill-me` 只调用 `/grilling`，不适合作为本项目安装权威。
- 微信文章 [《热门Skill研究：Grill-Me，凭什么火遍整个开发者圈？》](https://mp.weixin.qq.com/s/K4CN1LxsZgFR2FYv7f8Y3w)：2026-07-08 通过移动端微信 UA 公开 HTML 读取标题、账号、页面时间字段和正文，只吸收一次一问、推荐答案、Facts 自查、Decisions 等 Owner 和 shared understanding。
- 微信文章 [《如何看待 grill-me（拷问我）这个 Skill？》](https://mp.weixin.qq.com/s/jw7pqTwco_lLGnN_KmExig)：作者 / 账号为 `LastWhisperDev`，页面显示发布时间为 2026-07-10 15:50；2026-07-13 通过本机 Chrome headless 等价浏览器读取标题、作者、发布时间和正文，只吸收 Taste Injection、Shared Context、Issue / PR、Hand-off Prompt 和执行前 Finalize 的可迁移方法。

## 项目吸收结论

自 2026-07-18 起，本仓库维护项目自有独立 `grill-me`。上游与文章只作内容来源，不是安装权威；项目增加问题台账、语义去重、证据自决、红线记录和决策快照，并由 `wise-agent` 按需装载和消费结果。

## 不吸收边界

- 不安装上游全仓库，不保留 `/grilling` alias，不运行 npm、Claude plugin、hooks、Trellis、外部任务系统或跳过权限模式。
- 不复制上游 Skill 或文章原文、图片、示例、作者口吻和传播性结论。
- 不把盘问、自决或 shared understanding 写成执行、Git、发布、生产、测试通过、CR 通过或 Owner 授权。
- 上游版本变化只有形成真实行为差异、失败样例和最小验证路径时才进入升级评审。
