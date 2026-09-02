# 小说家外部能力来源索引

## 使用时机

仅在复核小说家能力来源、继续吸收外部写作资料、判断许可证边界，或追查某条方法从何而来时读取。普通构思、写作和评审不加载本文。

## 不适用场景

- 不把外部仓库当作当前作品的事实库、正典或运行时依赖。
- 不按仓库规模、Star、文件数量或宣传语判断写作质量。
- 不复制外部原文、模板、示例或语料；需要示例时读取本仓库的合成案例库。

## 读取后必须产出

```text
来源与固定快照：
实际读取范围：
可迁移方法：
许可证与归因边界：
不得吸收：
仍待验证：
```

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 查来源与许可证 | `来源矩阵` | 其他来源展开 |
| 继续吸收方法 | `来源矩阵` | 外部示例正文与语料 |
| 为创作找案例 | `craft-case-library.md` | 本文来源展开 |
| 验证写作能力 | 行为 fixture、同 runner/model 多次执行与盲评 | 用静态索引替代实测 |

## 来源矩阵

### SRC-NOVEL-01 `zy-zmc/tianming-skill`

- 固定快照：[`b5ef6e30817e086022ecbd09f9c2d2e781dd8b43`](https://github.com/zy-zmc/tianming-skill/tree/b5ef6e30817e086022ecbd09f9c2d2e781dd8b43)。
- 实际读取：仓库树、`LICENSE`、`SKILL.md`、会话状态、体检协议、角色档案模板与 mini-volume 说明；不是全仓逐字审读。
- 许可证：`CC BY-NC-SA 4.0`，GitHub API 标记为 `NOASSERTION`，以仓库 `LICENSE` 原文为准。
- 可迁移：用户作品事实外置、按任务渐进加载、变更后体检、用最小完整样例覆盖关键链路。
- 拒绝：固定五文件结构、人格化启动/热启动、强制 `FATAL_ERROR`、固定字数/节奏/章节配额、数值关系向量和自动写回事实库。

### SRC-NOVEL-02 `modoojunko/awesome-novel-agent`

- 固定快照：[`e7d19936bac10e165ab42cb744f7d5c549c19f77`](https://github.com/modoojunko/awesome-novel-agent/tree/e7d19936bac10e165ab42cb744f7d5c549c19f77)。
- 实际读取：README、`SKILL.md`、架构、许可证、人物规划/更新/读者审查，以及情节、场景、对白、转场、反派、标题、类型和格式资料。
- 许可证：`GPL-3.0`。
- 可迁移：人物选择沙盘、跨章信息差、场景变化、对手主动适应与读者视角复核。
- 拒绝：复制 GPL 文本/模板/脚本、八角色编排、自动记忆晋升、固定技法配额和自动写回正典。

### SRC-NOVEL-03 `XINGANLIU/web-novel-writing-skill`

- 固定快照：[`308ae728abf1c5526cfc533cde47904ff1f63584`](https://github.com/XINGANLIU/web-novel-writing-skill/tree/308ae728abf1c5526cfc533cde47904ff1f63584)。
- 实际读取：README、`SKILL.md`、阶段方法、质量说明、模板和许可证。
- 许可证：`MIT`；本仓库仍以重写后的方法结论为主，不复制其文档和模板。
- 可迁移：章级事实指针、恢复简报、状态增量、人物声纹复读、对手随损失和新情报改变行动。
- 拒绝：固定阶段/人格编排、黄金三章、固定字数/钩子期限、数值人格、反 AI 禁词和自动写回正典。

### SRC-NOVEL-04 `Tomsawyerhu/Chinese-WebNovel-Skill`

- 固定快照：[`4e0332eec0da62bf160eb284944a4c0def40b4c9`](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/tree/4e0332eec0da62bf160eb284944a4c0def40b4c9)。
- 实际读取：`v2` 的方法目录、分析资料结构、示例与语料目录清单；方法结论已归入 `web-serial-craft.md`。
- 许可证：未发现标准许可证，且含抓取正文；只保留独立重述的方法结论。
- 可迁移：题材/卖点/主角处境/故事发动机/体量分层，以及开篇、单章、连载中期的持续力诊断。
- 拒绝：原始语料、抓取正文、示例摘录、作者模仿、固定开篇字数、黄金三章和逐章强制配额。

### SRC-NOVEL-05 幻想、想象与创造认知公开来源

- 核验日期：2026-08-26。实际读取了刘勰《文心雕龙·神思》的公开文本页、Runco 与 Jaeger 2012 年论文正文、Finke 1996 年论文摘要、Beaty 等 2015 年论文正文、Sio 与 Ormerod 2009 年元分析摘要，以及 Ursula K. Le Guin 官方站的 `Plausibility Revisited` 与 `The Carrier Bag Theory of Fiction` 页面；未把检索摘要冒充全文通读。
- 来源：[`《文心雕龙·神思》`](https://ctext.org/wenxin-diaolong/shen-si/zh)、[`The Standard Definition of Creativity`](https://doi.org/10.1080/10400419.2012.650092)、[`Imagery, Creativity, and Emergent Structure`](https://doi.org/10.1006/ccog.1996.0024)、[`Default and Executive Network Coupling Supports Creative Idea Production`](https://doi.org/10.1038/srep10964)、[`Does incubation enhance problem solving?`](https://doi.org/10.1037/a0014212)、[`Plausibility Revisited`](https://www.ursulakleguin.com/plausibility-revisited)、[`The Carrier Bag Theory of Fiction`](https://www.ursulakleguin.com/the-carrier-bag-theory-of-fiction)。
- 可迁移：区分想象生成、幻想候选、成形探索与作品准入；发散期保护原创核，成形期再检查适切性；自发联想与认知控制采用同一创作主体内的动态往返，不拆成固定人格或 Agent；幻想可以违背外部现实的可行性，但须保持作品内部一致、人物选择与后果连续；故事不必缩成线性英雄征服结构。
- 华夏镜片：以《神思》的积学、感物与神思远行为文学参照，以变与不变、有无相用和正名校准幻想核、留白、成形与正典状态；这些只提供创作追问，不是现代实验结论、古义定论或题材古风化要求。
- 不吸收：论文和创作者原文、案例、固定模板、作者口吻、神经脑区还原论、发散测试分数、机械阶段论、用现实有用性提前扼杀文学候选，以及把孵化解释成无需准备或验证的神秘灵感。

### SRC-NOVEL-06 公开小说跨类型对照学习

- 核验日期：2026-09-01。实际读取十部作品三十个完整功能单元；《诛仙》因未确认作者持有的官方修订版或正版实体书保持未读，《文理双修》因未找到可核实的逐浪原作官方正文入口保持未读。
- 公版来源：蒲松龄《聊斋志异》的[维基文库公开文本](https://zh.wikisource.org/zh-hans/%E8%81%8A%E9%BD%8B%E5%BF%97%E5%BC%82)，实读《尸变》《画壁》《婴宁》；吴敬梓《儒林外史》的[维基文库公开文本](https://zh.wikisource.org/wiki/%E5%84%92%E6%9E%97%E5%A4%96%E5%8F%B2)，实读第三、第五、第四十一回。
- 官方公开来源：忘语《凡人修仙传》[起点公开第一章](https://www.qidian.com/bookrecommend/sqb330ce61fd24adaa)、爱潜水的乌贼《诡秘之主》[起点公开第一章](https://www.qidian.com/chapter/1010868264/402733549/)、志鸟村《大医凌然》[起点公开第一章](https://www.qidian.com/chapter/1011486666/406583253/)、猫腻《庆余年》[起点公开第一卷第一章](https://www.qidian.com/chapter/114559/2989904/)、情何以甚《赤心巡天》[起点公开第一章](https://www.qidian.com/chapter/1016530091/497000549/)、东海镇守《蜀山镇世地仙》[起点公开第一章](https://www.qidian.com/chapter/1039775049/788426280/)、贱宗首席弟子《大魏宫廷》[起点公开第一章](https://www.qidian.com/chapter/3662715/90831945/)、李兴禹《我的美女大小姐》[阅文官方公开章节](https://www.qidian.com/chapter/154696/4179489/)。每部实读开篇、关系或日常、压力或转折三类单元；没有绕过登录、订阅、客户端或付费门禁。
- 可迁移且现有资产已覆盖：神异先成为身体、欲望与选择，解释只到当前行动够用；私人欲望可以发动低风险场景；钱物、礼数、办理动作与生活中介使制度和历史可感；职业步骤由瓶颈、权限、交接与失败风险推进；文化通过制作、使用、传授、误读和承接成为行动；群像各线保留自己的时钟和成功标准。
- 本轮新增候选：共同事件的压力级别须由人物独立时钟、题面事实和类型承诺决定。相同 runner/model 的十八份 prechange baseline 中，幻想、人物、都市关系、职业与长史题均已表现稳定；群像题三次都把未限定危险级别的地方庆典意外收敛为灯架或灯船灾害，继而重复救援、记录与承责，故只对该缺口制作最小 reference 与 cases-only fixture。
- 不吸收：任何作品的原文、作者口吻、人物、设定、力量体系、关系结构或独创情节；不把男性凝视、身体侵犯、性侵威胁、性别物化、胁迫求饶和操控恋爱对象当作人物鲜活或喜剧技巧；不按书名建立题材模板，也不把古典专名、古语数量或半文半白语气等同古典气象。
- 证据边界：阅读卡、长摘要与 baseline 保留在授权任务的临时载体，不进入本仓库。当前只形成 W4 候选回流；静态 fixture、reference diff 与 source-set digest 不证明行为提升，W5 仍须用同 runner/model、六个 holdout、每题三次生成 candidate 并独立盲评。

## 证据与维护边界

- 来源行只证明“读过什么、允许借鉴什么”，不证明方法有效，更不证明真实写作行为已经提升。
- 外部快照变化、许可证变化或拟吸收范围扩大时重新核验；不以 `main`、`v2` 等浮动分支替代固定提交。
- 外部仓库不作为运行时依赖；创作时只读取本仓库已经归位的方法和合成案例。
- 静态案例可发现不等于真实写作行为提升。真实提升需在同一 runner/model 下做 baseline/candidate 多次执行、盲评或可复现评分，并保持高风险 blocker 为零。

### 当前行为复评（2026-08-27）

- 曾按 `novelist-current` source profile 对 6 组 contract 做临时 baseline/candidate 复评，但仓库未登记可复核 artifact，因此不保留精确分数或逐组结论。所有组继续保持 `cases-only`；重新激活前须按当前 source 重新采集、盲评并定位失败机制，不能只放宽 gate 或刷新指纹。

## 需要继续读取的 reference

- 需要方法正文时，按 `SKILL.md` 的场景路由读取对应专项 reference。
- 需要示例对照时读取 `craft-case-library.md`；需要真实项目事实时回读作者指定的当前权威材料。
