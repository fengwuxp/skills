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
| 复核人物厚度、内心表达与跨题材方法 | `SRC-NOVEL-08` | 不把某家写法变成普遍配额 |
| 复核文学审美、句读与分角色试写 | `SRC-NOVEL-09` | 不以古雅、字少或固定心理链评定所有作品 |
| 动作齐全却像流程、句段生硬或叙述没有轻重 | `SRC-NOVEL-10` | 不把口语、短句或删省设为统一文风 |
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
- 后续状态覆盖（2026-09-04）：W5 已执行并在 release gate 被拒，后续 R2、R3、R4 与轮动第一轮仍为 `accepted=0`；最新横向复盘只增强项目私有检索资产，未发现现有 `novelist` 尚未覆盖且具独立行为改善证据的新能力。该进度只修正本来源的准入状态，不把项目知识库变成默认运行时依赖，也不在此同步后续阅读流水。
- 行为复评覆盖（2026-09-05）：修复 source profile 冻结与评测契约后，`novelist-local-material-use` 在隔离 `gpt-5.6-sol/high`、五题各三次的 baseline/candidate 盲评中通过 release gate；`novelist-public-fiction-learning` 虽达到 candidate `58/60 criteria`、零 blocker 和总体改善，仍在书展与悬疑题各有一次 pairwise correctness 回退，继续 `FAIL / NOT_ADMITTED`。live responses、blind、scores 与 reports 只保留在当前任务临时证据目录，未进入本仓库；因此整体仍为 `contract-only / accepted=0`，不更新 admission，不把局部通过写成整个 Skill 的行为准入。

### SRC-NOVEL-07 韩非、法术势与制度叙事

- 发现来源：[《法家绝顶识人术，背下来，行走世间皆顺遂》](https://mp.weixin.qq.com/s/lpOhaL_l9VHOUGpO4VK3jg)，作者 / 账号“老黄闲叨”，页面发布时间 2026-09-10 19:31。2026-09-29 普通网页读取失败后，通过 Codex in-app Browser 读取标题、作者、时间与五节完整正文。文章是个人处世方向的现代转述，不是法家体系原典；未见可复用许可，不复制正文、配图或宣传性效果保证。
- 补充输入：用户提供的评论节选与关系图已读取，用于提出个人自保、制度运行和纠错的比较问题。评论身份与网页发布状态未独立核实；只作现代解释线索，不保存评论者身份、地区、原图或完整评论，不把图中人性命题和制度效果当作事实。
- 原典核读：以下维基文库传世电子文本已读取相关段落及上下文。其平台编辑内容声明 CC BY-SA 4.0；本库仅保留链接、必要定位短语和独立重述，不复制全文或现代注解。此次未逐字比对影印底本，不能作为校勘定本，也未完成篇章作者考证。

| 篇章 | 已核范围与用途 |
| --- | --- |
| [《主道》](https://zh.wikisource.org/wiki/韓非子/主道) | 隐好恶、虚静、形名参同、去智绝能及君臣语境；页面修订号 2327639 |
| [《扬权》](https://zh.wikisource.org/wiki/韓非子/揚權) | 事在四方、中央执要、分任与信息；页面修订号 2327675 |
| [《初见秦》](https://zh.wikisource.org/wiki/韓非子/01#初見秦第一) | 战战栗栗句及前后军政说辞，保留篇中“臣闻之”的引语身份 |
| [《外储说左下》](https://zh.wikisource.org/wiki/韓非子/外儲說左下) | 经四、说四中的禁利相反、毁誉考察、去蚁驱蝇与任官；页面修订号 2327663 |
| [《定法》](https://zh.wikisource.org/wiki/韓非子/定法) | 法术相须、新旧法令、守职与进言、功绩与适任之别；页面修订号 2327670 |
| [《难三》](https://zh.wikisource.org/wiki/韓非子/難三) | 不依赖个人耳目遍知、参核与法显术隐；页面修订号 2327686 |
| [《难势》](https://zh.wikisource.org/wiki/韓非子/難勢) | 势与贤能的问难往复、中者与抱法处势，保留反论；页面修订号 2327688 |
| [《二柄》](https://zh.wikisource.org/wiki/韓非子/二柄) | 赏罚权柄、刑名与侵官叙述，不将其视为现代权利保障 |

- 读取限制：中国哲学书电子化计划曾返回 403，浏览器访问显示连接检查页，未取得可用正文，不据搜索摘要立证；最终以上述已读取电子文本为此次依据。
- 应用位置：`knowledge-library.md` 提供按需索引，`knowledge-hanfeizi.md` 保存专题辨析与原创合成情境，`SKILL.md` 与 `worldbuilding-and-research.md` 提供调用入口。保留法、术、势的相互条件、有限知情和制度后果；不吸收读心术、永不妥协、普遍自利、计谋必胜、制度必然纠错或现代法治等同古代法家等结论。
- 证据边界：知识条目可供当前创作参考，不构成法家全体系、历史制度复原、正典确认或写作行为提升证据；新底本、异文、时代或具体制度适配发生争议时，回到相应篇章及专业考据复核。

### SRC-NOVEL-08 跨题材人物厚度与表达取舍

2026-10-09 核读下列正文的指定部分，只提炼方法，不复制原文、人物、情节或作者声音：

| 实读材料 | 本轮用途 | 不外推 |
| --- | --- | --- |
| [《庄子·养生主》](https://zh.wikisource.org/wiki/莊子/養生主)，庖丁段；公开电子本，另以 CText 浏览器正文互核 | 顺着对象已有条件行动，遇难处减慢、细察；用于校准作者强排 | 原文不是人物写作手册；四问是本项目现代转译，不作为古義或心理学定论 |
| [《红楼梦》第六回](https://zh.wikisource.org/wiki/紅樓夢/第006回)，刘姥姥决定进城及入府求助段 | 处境、自重与关系位置在同一行动中显现，人物有自身缘由 | 只作一个叙事样本，不把古典声口、家族秩序或贫困情境推广到其他题材 |
| [E. M. Forster, Aspects of the Novel](https://www.gutenberg.org/cache/epub/70492/pg70492-images.html)，People 续篇与 The Plot 开头关于内心生活的段落 | 可令人意外而可信；人物相互关联；内心不必被外部行为穷尽 | 不要求所有角色圆满复杂，不按惊奇次数评分，不沿用与当前 POV 契约冲突的自由换视角主张 |
| [OpenLearn, Week 5: Creating convincing characters](https://www.open.edu/openlearn/mod/oucontent/view.php?id=20435&printable=1)，5.1、5.1.1、5.2、5.3 | 由相牵的欲望生成场面，以观察、自身经验和想象打开人物差异 | 课程及第三方节选许可分别存在；不复制示例，不采用人人须缺陷、危机或改变的公式，不用单一经历推定人格 |
| [Ursula K. Le Guin, Navigating the Ocean of Story: Session 2, Round 1](https://www.ursulakleguin.com/bvc-navigating-the-ocean-of-story-session-2-round-1)，2016-02-29，回答 2、3 | 从整体寻找合适发展；相处、承受与变化也可推动叙事 | 不把冲突设为唯一发动方式，也不反向禁止冲突；不复制原文或将作者偏好当普遍标准 |

归位于 `character-craft.md` 的四问及从人物到场景、人物模板和 `craft-case-library.md` 的 `CASE-07`。华夏智慧持判断原则，其他材料补方法与反例；适用现代、历史、科幻、奇幻等题材，人物的文化、身体、世界与语体由作品决定。电子文本仅支持本轮实际读到的段落，未作版本学考证或整本通读；来源差异和借鉴不证明生成质量或读者共情已经提升。

### SRC-NOVEL-09 感物、声气与整体成篇

2026-10-11 核读以下公开正文，只作方法参照；不同作者、体裁与时代的判断不拼成一套古今通则，不复制原文、图像、人物或情节。

| 来源与实读范围 | 可迁移的方法与归位 | 不能推出 |
| --- | --- | --- |
| 刘勰《文心雕龙》[神思](https://zh.wikisource.org/zh/文心雕龍/神思)、[物色](https://zh.wikisource.org/zh/文心雕龍/物色)；实读两篇正文，前者网页读取，后者另经浏览器回读 | 广泛取材须归于当前作品；物象、感受、选词相互牵动。用于场景文风和分角色试写的现代转译 | CText 两篇常规读取 403，浏览器也显示网络访问拒绝，未取到该站正文；本轮依据维基文库电子文本，未作底本校勘、训诂定论或字形溯源 |
| [《红楼梦》程甲本第四十回](https://zh.wikisource.org/zh-hant/紅樓夢（程甲本）/四十)；浏览器实读入园、宴席笑态及饭后对话相关段落 | 同一场事经不同身体、身份和关系形成群像；言语、动作与后续回应共同生出情味。用于人物内演和整场回读 | 不把此回推广为全书统一声腔，不复制笑态清单、人物关系或程甲本字词形态；未逐字核对影印底本 |
| 鲁迅[《作文秘诀》](https://zh.wikisource.org/zh-hans/作文秘訣)全文，页面标注 1933 年、《南腔北调集》 | 辨清讽刺语境，避免靠生僻字、压短句子和卖弄来制造文学性；用于古白话学习边界 | 不把白描推成禁用铺陈、内心、比兴或华美语言的永久规则 |
| Ursula K. Le Guin 官方站 [Navigating the Ocean of Story: Session 2, Round 1](https://www.ursulakleguin.com/bvc-navigating-the-ocean-of-story-session-2-round-1)，2016-02-29，实读问题 1—3 的答复 | 连续朗读检查散文流动；结尾从整体故事生长；变化不只有冲突。用于角色回读与去同构校准 | 不据个人写作方法取消冲突、规划或结构分析，不把模型默读当作真人朗读反馈；未借此宣称读完《Steering the Craft》 |

既有训诂接口继续负责语境义、语体和时代证据，本轮不新增古义定论。方法归入 `scene-and-prose-craft.md`、`classical-vernacular-style.md`、`creative-inertia.md` 与 `deliberation-role-configuration.md`；配套试写只证明观察到的局部行为，不证明普遍审美提升。

### SRC-NOVEL-10 叙述轻重与语言流动

2026-10-11 通过网页实际核读下列正文，用于复核现有场景方法；只保留独立重述，不复制原句、人物、桥段或作者声腔。

- 鲁迅[《社戏》](https://zh.wikisource.org/wiki/社戲)：实读出航、候戏、归航吃豆及次日回望等段落。观察动作、感官、等待与概述如何随人物期待改变分量；这是本轮阅读判断，不把行船或吃豆场景转成通用故事模板，也不把回望式收尾设成必选。电子文本未作底本校勘。
- 汪曾祺[《小说里边最重要的是什么？》](https://www.chinawriter.com.cn/n1/2021/1024/c404032-32262629.html)：实读正文，网页标注 2021-10-26，注明原载 1991 年第四期《写作》；另读[《创作并非不可教授》](https://www.chinawriter.com.cn/n1/2018/0323/c404032-29886037.html)中语言整体联系、习作后讲得失与贴近人物的段落，网页标注 2018-03-23。用于校准句段联系及先看实际试片再讲方法；不把作者个人偏好的疏淡、朴素或乐观设成统一标准，不吸收其关于中外语言、声调的泛化论断，也不把叙述者与人物声音强行等同。
- 归位：`scene-and-prose-craft.md` 的“场景承重与展开”明确区分事实承接和展开分量；既有文风校准、对白与连续复读继续复用。学习和来源核验本身不证明自然流畅或写作能力提升。

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
