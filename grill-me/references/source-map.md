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

- [Matt Pocock skills](https://github.com/mattpocock/skills)：2026-08-07 核验上游 `main` 的 README、CHANGELOG、`grill-me`、`grilling`、`grill-with-docs` 和 `domain-modeling`；CHANGELOG 当前版本为 `1.2.3`。上游 `grill-me` 仍只调用 `/grilling`，而 `/grilling` 已于 2026-07-16 通过提交 [`a4b2009`](https://github.com/mattpocock/skills/commit/a4b2009a1a3ac9575506c10b4c84f08f9bba7a38) 从一次一问改为每轮询问整个 frontier。
- 微信文章 [《热门Skill研究：Grill-Me，凭什么火遍整个开发者圈？》](https://mp.weixin.qq.com/s/K4CN1LxsZgFR2FYv7f8Y3w)：2026-07-08 通过移动端微信 UA 公开 HTML 读取标题、账号、页面时间字段和正文，只吸收一次一问、推荐答案、Facts 自查、Decisions 等 Owner 和 shared understanding。
- 微信文章 [《如何看待 grill-me（拷问我）这个 Skill？》](https://mp.weixin.qq.com/s/jw7pqTwco_lLGnN_KmExig)：作者 / 账号为 `LastWhisperDev`，页面显示发布时间为 2026-07-10 15:50；2026-07-13 通过本机 Chrome headless 等价浏览器读取标题、作者、发布时间和正文，只吸收 Taste Injection、Shared Context、Issue / PR、Hand-off Prompt 和执行前 Finalize 的可迁移方法。
- 微信文章 [《grill-me SKILL 的失败模式》](https://mp.weixin.qq.com/s/9keJ9vfryl3RAmhVWTZnFA)：作者 / 账号为 `徐道AI` / `老徐`，页面显示发布时间为 2026-07-24；2026-07-29 通过浏览器读取标题、作者、发布时间和正文，只吸收高保真问题先观察、按独立决策包交接与并行、人与 Agent 共同收敛的可迁移方法。文中约 120k token 的说法只属作者经验，不作为固定阈值或项目事实。
- 微信文章 [《Grill-Me 史诗级升级！Matt Skills v1.1 彻底解决 AI 编码最大痛点（附最佳配置）》](https://mp.weixin.qq.com/s/_4exXmzaNRbCqPgUFSvnKw)：作者 / 账号为 `MurphyGao` / `程序员MurphyGao`，页面显示发布时间为 2026-08-07 08:00；2026-08-07 通过浏览器读取标题、作者、发布时间和正文。文章关于 v1.1 恢复一次一问的描述与当前上游及其变更历史冲突，只把批量问题过载、过早执行、Facts / Decisions 混淆视为失败类别线索，不把文章当作当前版本权威。

## 项目吸收结论

自 2026-07-18 起，本仓库维护项目自有独立 `grill-me`。上游与文章只作内容来源，不是安装权威；项目增加问题台账、语义去重、证据自决、红线记录、问题保真度、决策包和决策快照，并由 `wise-agent` 按需装载和消费结果。上游 `/grilling` 当前按 frontier 批量询问，本项目基于用户可核对性和既有行为契约，仍坚持一次只问一个主 blocker；这是主动分歧，不随上游同步。

2026-08-27 的本地实践会商补充了过程资产缺口：小说、文档、产品和 UI 设计中的承重细节不能随最终结论丢失，但也不能自动升格为正典或领域 Owner 决策。项目吸收“过程资产索引 + 领域载荷引用 + 独立状态/效力”的最小做法；验证以 fixture 和静态门禁确认结构，不把字符串校验冒充真实行为证明。

同日后续小说实践又暴露三项边界：过程资产模式会沿场景无限下钻、组合答案会把行动意图误写成既成效果、每个微小确认会反复扇出派生文档。项目据此补充“当前交付 + 设计分辨率”门槛、独立 `queue_state: active / deferred` 与 `deferred_until`、行动意图和结果分离、写回检查点。新增行为 contract 只建立可复跑用例；没有同一 runner/model 的基线与候选响应、独立盲评和安装同步前，不宣称行为提升或发布准入。

2026-08-27 曾执行 R1-R4 临时行为复评，但仓库未登记可复核 artifact，因此不保留精确分数，只记录高风险 criteria 未全部通过。该结果不进入 scored release gate；cases 仅接入 `evidence-gates.json` 的 cases-only 门禁，重新评测前不得据此声称行为提升或发布准入。

## 不吸收边界

- 不安装上游全仓库，不保留 `/grilling` alias，不运行 npm、Claude plugin、hooks、Trellis、外部任务系统或跳过权限模式。
- 不复制上游 Skill 或文章原文、图片、示例、作者口吻和传播性结论。
- 不把文章中的固定五阶段链路、工具排名、模型表现、最佳配置或 TDD 阶段调整设为默认规则。
- 不把盘问、自决或 shared understanding 写成执行、Git、发布、生产、测试通过、CR 通过或 Owner 授权。
- 上游版本变化只有形成真实行为差异、失败样例和最小验证路径时才进入升级评审。
