# Loop 取舍校准 / Wisdom Lens for AI Native Loop

本文定义如何把 `huaxia-wisdom` 中的东方判断框架接入 AI Native Engineering Loop。对外名称使用 **Loop 取舍校准 / Wisdom Lens**，“东方判断层”只作为触发别名。它是轻量辅助判断镜片，用来帮助判断该不该动、怎么动、动到什么程度、什么时候停；不是流程主线，不替代事实、证据、测试、代码 Review、授权或上线审批。

## 使用时机

- 用户明确要求把 Loop 取舍校准、Wisdom Lens、`huaxia-wisdom`、东方智慧、东方判断层、阴阳平衡、中庸之道、先为不可胜、庖丁解牛、循名责实、无为而治、每日三省、知行合一或一张一弛接入 AI Native Loop。
- Loop 准入、GSD Wave 拆解、Plan Grant / CAD Grant 授权粒度、执行核验、失败回退或复盘回流出现“速度与治理”“自动推进与人工确认”“流程膨胀与真实交付”的张力。
- AI Native 输出已经具备事实、owner、边界和验证路径，但还需要一层取舍、止损、节奏或反偏判断。

## 不适用场景

- 不用于代写 PRD、系分、OpenSpec、Harness Plan、测试策略、代码实现、CR 结论或上线审批。
- 不在正式交付文档中保留文化化讨论过程、AI 推理轨迹、被拒方案或修辞性展开；正式文档只保留当前有效结论和证据边界。
- 不把传统智慧框架当作项目事实、合规结论、架构批准、Execution Grant、测试通过或生产审批。
- 不默认切换成“老祖宗口吻”；只有用户明确要求“用某个框架分析”或“请一位老祖宗”时，才按当前运行时可用 Skill 路由到 `huaxia-wisdom`。

## 读取后必须产出

- Loop 取舍校准准入结论：需要 / 不需要；如果不需要，说明直接走哪个角色 Loop 场景视图或专门 Skill。
- Loop 阶段：准入前、拆解时、执行中、复盘后，或协作冲突 / 授权纠偏。
- 推荐框架组合、反偏问题、底线问题、证据要求、回写位置和下一 owner。
- 边界声明：事实、推断、待确认、范围外不做，以及本辅助判断镜片不替代哪些门禁。

## 需要继续读取的 reference

- Loop 结构、状态载体、预算和停止条件读 `agent-loop-engineering.md`。
- GSD / CAD / Grant 准入读 `gsd-cad-admission.md`。
- Goal、预算 / 时间盒、Ledger 和目标组合读 `goal-composition.md`。
- 验证、CR、发布、复盘和质量门禁读 `verification-review-release.md`。
- 来源边界、已读材料和不吸收项读 `source-map.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断是否需要 Loop 取舍校准 | `四段式调度`、`输出模板` | 不读取全部 huaxia-wisdom 细节 |
| Loop 准入或授权粒度纠偏 | `工程化映射`、`反模式`、`gsd-cad-admission.md` | 不把框架写成 Execution Grant |
| GSD Wave / CAD Task 拆解 | `工程化映射`、`四段式调度`、`agent-loop-engineering.md` | 不替代架构师工程拆解 |
| 复盘和知识回流 | `四段式调度`、`输出模板`、`verification-review-release.md` | 不把复盘写成文化感想 |

## 工程化映射

| 框架 | 放入 Loop 的位置 | 关键判断 | 回到工程产物 |
| --- | --- | --- | --- |
| 阴阳平衡 | Loop 准入 | 速度收益和治理代价是否同时可见；AI 自治和人工确认是否互为条件 | 场景视图、授权策略、风险边界 |
| 中庸之道 | 授权粒度 | 既不每步阻塞，也不全部放行；找到 Plan / Wave / CAD 级别的刚好授权 | Plan Grant、Wave Grant、CAD Grant |
| 先为不可胜 | 高风险门禁 | 最坏失败是什么、如何先立于不败、失败后如何停止和回退 | Stop/Handoff、回滚、显式确认 |
| 庖丁解牛 | GSD / CAD 拆解 | 骨架、缝隙、阻力点和最小可验证切片在哪里 | GSD Wave、Atomic Task、Coding Loop Contract |
| 无为而治 | 流程瘦身 | 哪些动作只是干预感，删掉后反而更稳定 | 跳过项、owner 精简、门禁瘦身 |
| 循名责实 | 执行核验 | AI 说“完成”的名，是否有代码、测试、日志、CR 或用户证据之实 | Verification、CR 证据、状态回写 |
| 每日三省 | 复盘 | 是否偏离用户价值、协作责任和知识回流 | Review Summary、Decision Log、Goal Ledger |
| 知行合一 | 知识回流 | 已知规则是否真正进入脚本、fixture、reference 或默认流程 | Skill / reference / fixture / script 回写 |
| 一张一弛 | Loop 节奏 | 是否过度循环、过度验证、过度并行或疲劳审批 | 预算 / 时间盒、最大轮次、暂停条件 |

协作冲突时可按需借用 `己所不欲`、`共生之道`、`纵横捭阖`、`法术势` 等框架，但必须转译成 owner、责任边界、利益冲突、授权和验证问题，不进入修辞化表达。

## 四段式调度

1. 准入前：使用阴阳平衡和先为不可胜，判断是否值得进入 Loop、失败成本是否可控、是否需要显式确认。
2. 拆解时：使用庖丁解牛和中庸之道，判断 Wave / Atomic Task 是否顺着业务与代码纹理拆分，授权粒度是否刚好。
3. 执行中：使用循名责实和无为而治，检查 AI 自述是否有实证支撑，删除无价值干预和假进展。
4. 复盘后：使用每日三省、知行合一和一张一弛，把经验回到 Skill、fixture、脚本、Goal Ledger 或 Decision Log，并控制循环节奏。

## 输出模板

```text
Loop 取舍校准卡 / Wisdom Lens Card
触发原因：
Loop 阶段：
推荐框架：
关键反偏：
底线与证据：
回写位置：
下一 owner：
```

输出保持一屏内；不重复展开“不替代项”，只在结论中说明它不替代事实、测试、CR、Execution Grant、上线审批或专业确认。

## 调用 huaxia-wisdom 的边界

- 用户只说“把东方智慧加入 AI Native Loop”时，本技能默认只使用本文工程化映射，不读取或展开 `huaxia-wisdom` 全部内容。
- 用户明确说“用阴阳平衡分析”“请老祖宗分析”“用 huaxia-wisdom 输出”时，如果当前运行时已安装该 Skill，可按其 Skill 触发规则调用；AI Native 仍负责把结论转回 Loop Contract、Grant、Verification 和 Stop/Handoff。
- 输出保持工程语言，避免把正式 PRD、系分、Spec、CR 或发布报告写成文化化叙事。
- 不能引用框架名来代替来源材料、源码锚点、测试结果、日志证据或人工确认。

## 反模式

- 用东方智慧替代事实、源码、测试、日志、CR 或用户确认。
- 把中庸之道写成和稀泥，把无为而治写成不作为，把先为不可胜写成永不行动。
- 把阴阳平衡写成两边各退一步，而不是识别互相依存的约束和可验证的太极点。
- 在正式 PRD、系分、OpenSpec、Harness Plan 或代码评审中保留过程讨论、AI 推理轨迹或修辞性发挥。
- 把 `huaxia-wisdom` 写成默认安装、默认联网、默认审批、默认 Git 操作或默认生产授权。
