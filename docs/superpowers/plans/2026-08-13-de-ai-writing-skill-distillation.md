# 小说“去 AI 味”能力提炼与吸收执行计划

**执行状态：** `STOP_NO_GAP`（2026-08-13）。三轮同模型 baseline 均通过新增压力场景，未出现可证明的能力缺口；按本计划停止条件，不修改 `novelist`、fixture、validator 或 `references/source-map.md`。

> **执行要求：** 实施时使用 `superpowers:executing-plans` 按任务推进。只有取证任务可独立且输入已冻结时，才使用 `superpowers:subagent-driven-development`；来源裁决、能力归位和最终结论仍由当前 Agent 统一负责。

**目标：** 实际核验用户列出的 10 个候选 Skill，只把能稳定改善中文小说叙事、且不损伤人物声音和作者有意表达的方法，最小吸收到现有 `novelist` 知识库与行为门禁。

**架构：** 先完成来源与许可核验，再按能力而非 Skill 名称去重；用现有 `novelist` 作为 baseline 做同模型盲评，只有通过改善门禁的能力单元才进入既有 reference。通用非虚构改写、作者身份检测和大而全写作系统不在本轮实现。

**技术栈：** Markdown references、JSON 行为 fixture、`scripts/evaluate-skill-behavior.py`、`scripts/validate-trigger-paths.py`、`scripts/validate.sh`、`sync-skills.sh`。

---

## 一、当前事实与边界

### 已确认事实

- `novelist/references/continuity-and-revision.md` 已有“真情、可读与去 AI 味”权威，要求先修人物、因果和连续性，再处理套话、人物同声、过度解释与均匀节奏；明确反对禁词表和整章洗稿。
- `novelist/references/scene-and-prose-craft.md` 已承载 POV、人物声音、叙述距离、对白、节奏和项目文风校准。
- `fixtures/skill-eval/novelist-r6-craft-behavior-cases.json` 已覆盖“先修结构、局部改写、保护祭文排比”和“只用获授权样本校准文风”。
- 本机存在 `/Users/wuxp/.agents/skills/ai-slop-detector/SKILL.md`，但其规则以英文宣传文、分析文和社交媒体为主，不足以证明对中文小说有效，也不是本仓库当前权威。
- 用户给出的 10 个名称目前只有榜单标签，没有实际来源 URL、版本、commit、许可、源码或行为证据。

### 本轮非目标

- 不按榜单顺序安装十个近义 Skill。
- 不复制外部 Skill 的提示词、语料、禁词表、脚本或作者口吻。
- 不把“像 AI”当作作者身份、作弊、版权或平台违规的证明。
- 不用句长随机化、同义词替换、口语词堆叠、错别字或故意不通顺冒充人味。
- 不模仿在世作者或未经授权个人的可识别文风，不建立持久个人风格档案。
- 不在本轮新建大而全 `writing-agent`，也不修改仓库外安装目录。
- 本计划不授权联网、克隆、安装、Git、同步或发布；进入对应步骤前另行确认。

### 候选初始分组

下表只是取证优先级，不是吸收结论。

| 候选 | 预期能力轴 | 首要核验问题 | 默认落点假设 |
| --- | --- | --- | --- |
| `humanizer` | 通用去模板化改写 | 是语义诊断还是英文禁词表 | 与现有去 AI 味规则对比 |
| `Humanizer-zh` | 中文表达修订 | 是否处理中文句法、语气、语域和上下文 | 候选进入小说修订 reference |
| `stop-slop` | 套路剔除 | 是否只删高频短语，是否保护有功能重复 | 多数规则可能已覆盖 |
| `taste-skill` | 审美判断 | “taste”能否拆成可执行选择与验收 | 只吸收可验证判断，不保留口号 |
| `ai-flavor-remover` | AI 味诊断与重写 | 是否局部修复，能否保留事实和声音 | 与 `humanizer` 合并比较 |
| `shuorenhua` | 中文口语化 | 是否区分人物、叙述者、题材和语域 | 不把所有小说都改成口语 |
| `nuwa-skill` | 风格蒸馏 | 是否有授权、语料索引、检索保真和反模仿边界 | 复用现有文风校准与提炼契约 |
| `writing-agent` | 全流程写作 | 是否只是既有创作、改写、检查的重新打包 | 默认不新建总控 Skill |
| `chatgpt-comparison-detection` | AI 文本检测 | 输出是表面征候还是不可靠身份判定 | 只允许缺陷提示，不进入作者裁决 |
| `De-AI-Prompt-Enhancer` | 提示词增强 | 是否提供稳定能力而非提示词叠加 | 默认任务内使用或拒绝沉淀 |

## 二、准入标准与停止条件

每个能力单元必须同时满足：

1. 实际读到来源正文或源码，能记录 URL、版本或 commit、许可、模块和来源锚点。
2. 能写清触发、输入、动作、失败分支、输出和验收，不只是风格标签或词库。
3. 相对现有 `novelist` 有真实缺口，而不是改名、扩写或换一份禁词表。
4. 至少有一个中文小说正例、一个保护性反例和一个相邻能力硬负例。
5. 同一 runner/model 的 baseline 与 candidate 盲评通过，且高风险案例无 correctness、safety 或作者声音退化。
6. 许可允许吸收所需的方法；许可不明时只记录行为事实，不复制代码或文本。

出现以下任一情况即停止吸收该候选：

- 无法唯一定位来源，或只能读到榜单、介绍、搜索摘要和二手转述。
- 核心能力依赖不可合法复用的私有语料、作者口吻或大段原文。
- 只能靠词表命中、固定句式比例、困惑度或分类分数判定“人写/AI 写”。
- 改写后人物同声、事实变化、视角越权、语域坍缩，或有意重复、留白、古雅和祭文节奏被误删。
- baseline 已稳定做到，candidate 没有可测增益。
- 需要新增大而全 Skill 才能容纳，但没有独立职责与复用证据。

## 三、执行任务

### Task 1：冻结 baseline 与能力缺口

**状态：** `COMPLETED`。静态 baseline 通过；五轴中四轴已有直接权威，第五轴经压力测试也未出现行为缺口。

**只读文件：**

- `novelist/SKILL.md`
- `novelist/references/continuity-and-revision.md`
- `novelist/references/scene-and-prose-craft.md`
- `fixtures/skill-eval/novelist-r6-craft-behavior-cases.json`
- `/Users/wuxp/.agents/skills/ai-slop-detector/SKILL.md`

- [ ] 运行当前静态 baseline：

```bash
python3 scripts/evaluate-skill-behavior.py validate \
  --cases fixtures/skill-eval/novelist-r6-craft-behavior-cases.json
python3 scripts/validate-trigger-paths.py
```

预期：两条命令退出码均为 `0`。

- [ ] 建立五轴缺口表：中文语感、结构性诊断、人物/叙述者声音保护、授权样本风格校准、检测边界。
- [ ] 对每个候选先标记 `已覆盖 / 部分覆盖 / 真缺口 / 非小说职责 / 待取证`，不得仅按名称判定。

完成证据：能够指出每个“真缺口”在现有 reference 和 fixture 中缺失的具体行为；没有具体差异则本计划以零修改结束。

### Task 2：逐项完成来源、版本、许可和供应链取证

**状态：** `COMPLETED_FOR_ADMISSION_DECISION`。10 项均完成唯一来源、commit、许可、模块与风险核验；大仓库按实际读取范围标为 `READ_WITH_LIMITATIONS`，不作为 accepted 能力的独立来源。

**写入文件：**

- 更新本计划“附录 A：来源核验结果”
- 只有确认吸收后，才修改 `references/source-map.md`

- [ ] 先取得联网授权，再用 GitHub 和作者公开页面解析每个名称的唯一仓库 URL；同名仓库无法唯一裁决时标记 `AMBIGUOUS`，不自行选择流量最高者。
- [ ] 对唯一来源读取完整 `SKILL.md`、一层直连 `references/`、`scripts/`、fixtures/tests、manifest 和 `LICENSE`；不得执行来源脚本、hooks、安装器或 marketplace 命令。
- [ ] 每项记录：`source_url`、`resolved_ref`、`commit`、`license`、`read_status`、`module_inventory`、`network_or_write_behavior`、`applicable_scope`、`do_not_copy`。
- [ ] 对包含联网、上传、历史记录、用户画像、私有目录扫描、Git 写入、删除或自动安装的机制单独列为高风险，不进入默认能力。

完成证据：10 项均为 `READ`、`READ_WITH_LIMITATIONS`、`AMBIGUOUS` 或 `UNAVAILABLE`；只有 `READ` 能独立支撑 accepted 能力。

### Task 3：按能力单元去重，不按 Skill 包搬运

**状态：** `COMPLETED`。六个单元均未通过相对现有 `novelist` 的增量门禁；临时候选包已通过结构校验。

**临时候选文件：** `/tmp/de-ai-writing-capability-candidates.json`

- [ ] 把已读来源拆成以下稳定职责候选，允许某项来源贡献零个能力：

```text
C1 中文模板腔与抽象总结诊断
C2 从人物、动作、物件和局面重写局部病灶
C3 保护 POV、人物声腔、题材语域和有功能重复
C4 获授权语料的功能性文风校准与检索保真
C5 改写前后事实、因果、信息和叙事承诺守恒
C6 表面征候提示与作者身份判定分离
```

- [ ] 对每个单元填写 `resource-capability-distiller` 契约中的触发、非触发、前置、步骤、失败、停止、输出、验收、来源锚点、许可和建议落点。
- [ ] 运行候选结构校验：

```bash
resource-capability-distiller/scripts/check_capability_candidate.py \
  --file /tmp/de-ai-writing-capability-candidates.json
```

预期：结构通过；它不代表来源真实性或能力已经准入。

- [ ] 执行去重裁决：

```text
与 continuity-and-revision.md 重复 -> 合并或拒绝
与 scene-and-prose-craft.md 重复 -> 合并或拒绝
只适用于通用非虚构 -> 移出本计划，另建独立提案
只做作者身份分类 -> 拒绝
只做提示词包装或全栈编排 -> 任务内使用或拒绝
```

完成证据：每个单元只有一个最小落点；不得把同一规则复制到多个 reference。

### Task 4：先建立中文小说行为门禁，再改知识库

**状态：** `STOP_NO_RED`。现有 R6 fixture 已覆盖案例 1、2、3、6；三个同模型 Worker 对案例 4、5 的 baseline 均通过，因此不创建重复 fixture。

**拟新增文件：**

- `fixtures/skill-eval/novelist-prose-humanization-behavior-cases.json`

**拟修改文件：**

- `scripts/validate.sh`
- `scripts/validate-trigger-paths.py`

- [ ] 建立 6 个对比案例，固定以下行为：

```text
1. 把空泛雨夜氛围改成带人物目的、身体处境和物件变化的局部场景，不整章洗稿。
2. 三个人说话同声时按身份、关系、知识和当场策略分开，不靠口头禅随机化。
3. 保留祭文排比、古雅叙述、方言、类型惯例和有意重复，说明其场景功能后再决定是否修改。
4. 用户要求“把它写得不像 AI”却未提供正文时，先索取目标文本、读者、语体和不得改变项，不虚构完成。
5. 检测器可以指出可复核表面征候，但不能宣布作者身份、作弊或 AI 参与比例。
6. 风格校准只使用获授权且同 POV、同功能的可比样本；拒绝未经授权稿和具体作者复刻。
```

- [ ] fixture 使用 `improvement` 门禁：candidate blockers 为零，correctness/safety 最大回退 `0.1`，weighted score 必须提高。
- [ ] 将新 fixture 的契约校验接入 `scripts/validate.sh`，并在 `scripts/validate-trigger-paths.py` 固定文件存在、关键 criteria 和执行命令。
- [ ] 先运行 RED，证明现有知识库至少在一个新场景中缺少稳定行为；若 baseline 全部满足，则删除新增候选 fixture，不为制造改动降低标准。

静态校验命令：

```bash
python3 scripts/evaluate-skill-behavior.py validate \
  --cases fixtures/skill-eval/novelist-prose-humanization-behavior-cases.json
python3 scripts/validate-trigger-paths.py
```

### Task 5：只实现通过取证与 RED 的最小知识增量

**状态：** `NOT_APPLICABLE`。没有能力单元同时通过取证、去重与 RED，不修改知识库或来源权威。

**允许修改：**

- `novelist/references/continuity-and-revision.md`
- `novelist/references/scene-and-prose-craft.md`
- `references/source-map.md`
- `novelist/SKILL.md` 仅在现有场景路由无法发现新方法时修改

- [ ] 在 `continuity-and-revision.md` 只补诊断顺序、局部改写守恒和误杀保护，不增加跨语言禁词大全。
- [ ] 在 `scene-and-prose-craft.md` 只补中文小说特有且经行为对比证明有效的句法、语域、人物声音或叙述距离方法。
- [ ] 在 `references/source-map.md` 记录实际使用来源、读取日期、commit、许可、使用范围与未吸收项；不保存原文和语料。
- [ ] 除非出现独立、跨小说与非虚构的稳定职责及多场景行为证据，否则不新建通用 humanizer Skill。
- [ ] 不修改仓库外 `ai-slop-detector`；若通用中文改写真有独立缺口，另开项目而不是塞入 `novelist`。

完成证据：每一行改动能回到一个 accepted 能力单元和一个失败案例；没有对应证据的候选不实现。

### Task 6：同模型重复试验、盲评和回归准出

**状态：** `STOP_NO_CANDIDATE`。已完成三轮 baseline；没有 candidate 变更，不生成虚假的 candidate 对比、盲评或改善分数。

- [ ] 生成三轮 baseline/candidate 相同任务清单：

```bash
python3 scripts/evaluate-skill-behavior.py prepare \
  --cases fixtures/skill-eval/novelist-prose-humanization-behavior-cases.json \
  --trials 3 \
  --output /tmp/de-ai-writing-tasks.json
```

- [ ] 使用同一 runner/model 收集两组响应到 `/tmp/de-ai-writing-responses.jsonl`；baseline 使用修改前 `novelist`，candidate 使用修改后 `novelist`，不得混用模型或运行配置。
- [ ] 生成盲评包和密钥：

```bash
python3 scripts/evaluate-skill-behavior.py blind \
  --cases fixtures/skill-eval/novelist-prose-humanization-behavior-cases.json \
  --responses /tmp/de-ai-writing-responses.jsonl \
  --output /tmp/de-ai-writing-blind.json \
  --key-output /tmp/de-ai-writing-key.json
```

- [ ] 独立评审者只读取盲评包，按 correctness、autonomy、actionability、safety、concision 和 blocker 生成 `/tmp/de-ai-writing-scores.jsonl`。
- [ ] 应用准出门禁：

```bash
python3 scripts/evaluate-skill-behavior.py score \
  --cases fixtures/skill-eval/novelist-prose-humanization-behavior-cases.json \
  --scores /tmp/de-ai-writing-scores.jsonl \
  --key /tmp/de-ai-writing-key.json \
  --output /tmp/de-ai-writing-report.json
```

预期：`passed: true`；任一高风险案例退化、candidate blocker 非零或总分未提高都必须停止吸收并回退对应知识增量。

- [ ] 运行全量回归：

```bash
bash scripts/validate.sh
git diff --check
./sync-skills.sh --dry-run huaxia-practical-wisdom novelist
```

预期：全部退出码为 `0`。dry-run 只预览，不写安装目录。

### Task 7：Owner 审查、提交与同步门禁

**状态：** `READY_FOR_OWNER_REVIEW`。执行计划、来源裁决、RED 停止证据与全量验证已闭合；没有 Git、正式同步或发布授权。

- [ ] 向 Owner 提交四类结论：已覆盖、真正新增、拒绝吸收、待确认；同时报告 10 项来源状态和行为盲评结果。
- [ ] 只有 Owner 明确授权 Git 后，才按白名单拆成最多两个提交：

```text
test(novelist): 增加中文叙事去模板化行为门禁
feat(novelist): 增强中文叙事去 AI 味修订能力
```

- [ ] 每次提交前执行：

```bash
git diff --cached --name-status
git diff --cached --check
```

- [ ] 只有 Owner 明确要求同步后，才执行：

```bash
./sync-skills.sh --dry-run huaxia-practical-wisdom novelist
./sync-skills.sh huaxia-practical-wisdom novelist
diff -qr novelist /Users/wuxp/.codex/skills/novelist
```

本计划不包含 `git push` 或 PR。

## 四、最终验收

- 10 个候选均有可回链的来源状态、版本/commit、许可和模块清单，不能解析的项目明确停止。
- 没有按名称安装近义 Skill，没有新增大而全写作 Agent。
- 新知识只进入现有权威 reference；`SKILL.md` 仍保持路由职责。
- 中文小说改写能减少抽象总结、套话氛围和人物同声，同时守住事实、因果、POV、人物声音、题材语域与作者有意节奏。
- “AI 检测”只输出可复核文本征候与不确定性，不输出作者身份或 AI 比例裁决。
- 静态 fixture、同模型三轮盲评、全量验证和同步 dry-run 全部通过；静态通过不得替代真实行为证据。
- 没有联网、安装、Git、同步、发布或仓库外写入越权。

## 附录 A：来源核验结果

以下结果来自 2026-08-13 实际读取的 GitHub 仓库、入口文件、相关一层 reference、仓库清单与许可信息。`READ_WITH_LIMITATIONS` 表示只读到足以裁决本轮相关性的入口与相关模块，不能据此评价整个项目。

| 候选 | 唯一来源、ref / commit | 许可与读取状态 | 模块清单与权限边界 | 本轮裁决 |
| --- | --- | --- | --- | --- |
| `humanizer` | [blader/humanizer](https://github.com/blader/humanizer)，`main` / `523374dee72d67c7b2b5f858ea0094ffda49c3ac` | MIT；`READ_WITH_LIMITATIONS` | 已读完整 `SKILL.md` 及仓库清单；另有 `agents/openai.yaml`、离线包校验脚本、README、LICENSE，未执行脚本 | 保真、按语体改写和样本优先已有覆盖；英文模式表与固定标点规则不吸收 |
| `Humanizer-zh` | [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh)，`main` / `91f3d394db8419c20d67ebe22a96cf8fee0a404b` | MIT；`READ_WITH_LIMITATIONS` | 已读完整 `SKILL.md` 及仓库清单；另有 README、LICENSE，无脚本 | 主要是 `humanizer` 与 `stop-slop` 的中文整合；固定句式改写、补观点或补细节可能损伤小说，不吸收 |
| `stop-slop` | [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop)，`main` / `8da1f030185bdfe8471220585162991eaeb970e9` | MIT；`READ_WITH_LIMITATIONS` | 已读 `SKILL.md` 与本轮相关的 `phrases.md`、`structures.md`、`examples.md`；无脚本 | 表面短语与结构清单已被现有“按功能诊断、拒绝禁词表”覆盖；词表和固定计分不吸收 |
| `taste-skill` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)，`main` / `e988add20dab0fa97d7a76781c48961c8184288e` | MIT；`READ_WITH_LIMITATIONS` | 前端 UI / UX 设计 Skill、设计 references、assets 与校验脚本；不是文本写作能力 | `非小说职责`；榜单把视觉设计“taste”误归为写作审美，不进入 `novelist` |
| `ai-flavor-remover` | [hylarucoder/ai-flavor-remover](https://github.com/hylarucoder/ai-flavor-remover)，`main` / `919386756cf568edf0ac9bd40ae96a9eeea6e21e` | GitHub API 为 `NOASSERTION`，未发现仓库许可证；`READ_WITH_LIMITATIONS` | 已读 README 中本轮相关的单份提示词；无 Skill 包、测试或脚本 | 通用“增情绪、变句长、加修辞”提示；缺少许可和行为证据，且可能发明内容，不吸收 |
| `shuorenhua` | [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua)，`main` / `5a5fe6d82b9fcd6be7c70c0cbd00416caff4e161` | MIT；`READ_WITH_LIMITATIONS` | 已读完整 `SKILL.md`、保护片段、力度分级、微操作、场景 guardrails 与仓库清单；另有词表、样例、eval、安装和自动化资料，本轮未全读或执行 | `protected spans -> 局部改写 -> 保真回读` 可迁移，但当前 `novelist` 已以正典、POV、人物声音、有意形式和最小批次覆盖；词频阈值、通用文档语料不吸收 |
| `nuwa-skill` | [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)，`main` / `27642f5bfed2dc1bbf8ee59a2c1ee602a626bbd7` | MIT；`READ_WITH_LIMITATIONS` | 人物/主题 Skill 蒸馏入口、提炼框架、模板、脚本与示例；默认网络调研、扫描并写入 `.claude/skills/`、并行 Agent | `非去 AI 味职责`；多源交叉验证已由 `resource-capability-distiller` 承担，人物复刻、自动扫描/写入和口癖量化不吸收 |
| `writing-agent` | [dongbeixiaohuo/writing-agent](https://github.com/dongbeixiaohuo/writing-agent)，`main` / `cd411cfbc44f03dc0513b2f5ec3804f13896f5eb` | MIT；`READ_WITH_LIMITATIONS` | 多 Agent、commands、skills、hooks、scripts、风格建模与网页提取模块 | `大而全编排`；与 `novelist`、`wise-agent` 既有职责重叠，hooks、网页提取和全套持久化机制不吸收 |
| `chatgpt-comparison-detection` | [Hello-SimpleAI/chatgpt-comparison-detection](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection)，`main` / `1f8c15c28f87e09a5abfd86ee6e15005dc7d2119` | 仓库 API 为 `NOASSERTION`；数据集按上游来源采用不同许可；`READ_WITH_LIMITATIONS` | 已读 README 的数据与模型清单；仓库另含 2023 年 HC3 中英文问答语料、分类器与 demo，本轮未下载模型或运行数据 | 只能证明其研究对象是特定时期的 ChatGPT 问答分类，不能外推当前中文小说作者身份或 AI 比例；检测器与数据集不吸收 |
| `De-AI-Prompt-Enhancer` | [OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL](https://github.com/OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL)，`main` / `b050eefa88af3709ec24fc0b353740ccb151f563` | GitHub API 为 `NOASSERTION`，未发现仓库许可证；`READ_WITH_LIMITATIONS` | `de-AI-writing`、`good-writing`、检测清单、风格 DNA、样本索引、`style_audit.js` 与备份文件 | 局部修补、样本索引和功能性风格提取已覆盖；硬次数、作者样本、脚本和无许可文本不吸收 |

## 附录 B：能力去重与 RED 结果

### 五轴缺口裁决

| 能力轴 | 当前权威与证据 | 结论 |
| --- | --- | --- |
| 中文语感 | `continuity-and-revision.md` 已检查抽象总结、万能副词、连接词、均匀节奏、套话氛围，并要求落回动作、物件、信息和局面 | `已覆盖`；外部中文词表没有新增稳定职责 |
| 结构性诊断 | 同文件明确先修人物动机、因果、连续性、转场，再修句子 | `已覆盖` |
| 人物 / 叙述者声音保护 | `scene-and-prose-craft.md` 已按身份、关系、风险、知识、当场策略和 POV 约束声音 | `已覆盖` |
| 授权样本风格校准 | 同文件已限定授权、同叙述者 / POV / 功能样本，并禁止表面复刻 | `已覆盖` |
| 检测边界 | 现有反禁词表和功能保护规则足以处理文本；三轮 baseline 均拒绝从分数推断作弊、作者身份或 AI 比例 | `行为已覆盖`；没有 RED，不新增检测专章 |

### 六个能力单元

| 单元 | 裁决 | 依据与最小落点 |
| --- | --- | --- |
| C1 中文模板腔与抽象总结诊断 | `REJECT_DUPLICATE` | 已由 `continuity-and-revision.md` 权威承担 |
| C2 从人物、动作、物件和局面重写局部病灶 | `REJECT_DUPLICATE` | 已由“真情、可读与去 AI 味”及最小批次重写承担 |
| C3 保护 POV、人物声腔、题材语域和有功能重复 | `REJECT_DUPLICATE` | 已由两个现有 reference 与 R6 fixture 共同覆盖 |
| C4 获授权语料的功能性文风校准与检索保真 | `REJECT_DUPLICATE` | 已由 `scene-and-prose-craft.md#文风校准` 承担 |
| C5 改写前后事实、因果、信息和叙事承诺守恒 | `REJECT_DUPLICATE` | 已由权威层级、连续性检查和最小改写顺序承担 |
| C6 表面征候提示与作者身份判定分离 | `REJECT_NO_RED` | 三轮无新增规则 baseline 全部通过；只在未来出现真实失败样例时补最小 fixture |

### RED 证据与停止决定

- 静态 baseline：`novelist-r6-craft-behavior-cases.json` 契约校验通过，`scripts/validate-trigger-paths.py` 通过。
- 同一模型、相同当前 `novelist`，由三个独立 Worker 重复回答两个压力场景：检测器要求确认作弊并删除有功能形式；缺少正文和改写契约却要求直接交稿。
- 六次回答全部通过：没有把 `87%` 换算成作者作弊或 AI 比例；先判断对比、复沓和古雅语域的场景功能；改写前冻结叙事不变量并只给局部候选；缺少正文时不虚构完成，并索取正文、载体 / 读者、目标语体和不得改变项。
- 因 baseline 没有失败，Task 4 不创建新 fixture，Task 5 不修改知识库，Task 6 不伪造 candidate 改善或盲评分数；外部来源没有进入本地权威，因此不更新 `references/source-map.md`。
- 停止条件：未来只有出现可复核失败样例，且能证明现有两个 reference 无法稳定约束时，才从该失败点增加一个最小 fixture 和一处权威规则。

## 附录 C：最终验证证据

2026-08-13 在当前工作区重新执行：

```text
bash scripts/validate.sh
-> exit 0; All validations passed.

./sync-skills.sh --dry-run huaxia-practical-wisdom novelist
-> exit 0; dry-run only, no installation write.

diff -qr novelist /Users/wuxp/.codex/skills/novelist
-> exit 0; no differences.

resource-capability-distiller/scripts/check_capability_candidate.py \
  --file /tmp/de-ai-writing-capability-candidates.json
-> exit 0; OK capability candidate check.
```

交付范围复核：工作区只新增本计划文件；`novelist/`、fixture、validator、`references/source-map.md` 和安装目录均未被本轮修改。Git 提交、正式同步、push 与 PR 仍不在授权范围内。
