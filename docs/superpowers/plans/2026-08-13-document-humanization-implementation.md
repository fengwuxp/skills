# 正式文档保真去模板化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `document-authoring` 在“去 AI 味、说人话、改自然”类正式文档修订中，先冻结语义不变量，再做受控局部改写并逐项回读，避免责任、效力、条件、数字、归属和证据强度漂移。

**Architecture:** 不新增通用 humanizer Skill。先用正式文档压力场景测试现有能力；只有 baseline 失败时，才在 `review-and-revision.md` 增加一处保真修订协议，并用一个行为 fixture 固定边界。外部方法只取 `protected spans -> bounded rewrite -> fidelity reread`，不复制词表、阈值或语料。

**Tech Stack:** Markdown reference、JSON 行为 fixture、`scripts/evaluate-skill-behavior.py`、`scripts/validate-trigger-paths.py`、`scripts/validate.sh`。

---

### Task 1: 建立 RED 行为场景

**Files:**
- Create conditionally: `fixtures/skill-eval/document-authoring-humanization-behavior-cases.json`

- [x] 写入正式制度、事故复盘、只改表达三个高风险场景，并按 evaluator 的 5 个案例下限补会议归属与样本外推两个同职责边界案例，固定主体、效力词、条件、数字、归属、引文和不确定性边界。
- [x] 使用现有 `improvement` release gate，静态校验只证明 fixture 契约有效。
- [x] 用当前未修改的 `document-authoring` 运行三个同模型 Worker，保留逐案原答和 pass/fail。
- [x] baseline 出现真实 RED：3/3 弱化制度效力词，2/3 把相关性升级为因果，3/3 压缩有安全作用的重复；因此继续最小实现，未触发 `STOP_NO_RED`。

### Task 2: 最小 GREEN

**Files:**
- Modify conditionally: `document-authoring/references/review-and-revision.md`
- Modify conditionally: `references/source-map.md`

- [x] 只针对 baseline 的具体失败补充：先列不得漂移项；按授权范围修订；回读主体、谓词方向、完成态、效力词项与次数、条件、数量对象、归属和不确定性。
- [x] 不新增禁词表、句长比例、检测器阈值、整篇洗稿或作者身份判断。
- [x] 只在真实采用外部方法时记录来源 commit、MIT 许可、使用范围与未吸收项。

### Task 3: GREEN、回归与准出

**Files:**
- Modify conditionally: `scripts/validate.sh`
- Modify conditionally: `scripts/validate-trigger-paths.py`

- [x] 将通过 RED 的行为 fixture 接入静态校验和触发路径指纹。
- [x] 让同一批 Worker 使用修改后的 Skill 重跑相同场景；原样对抗提示下 3/3 守住因果与安全重复，效力词在补充“词项及次数一致”门禁后 3/3 通过。
- [x] 运行：

```bash
python3 scripts/evaluate-skill-behavior.py validate \
  --cases fixtures/skill-eval/document-authoring-humanization-behavior-cases.json
python3 scripts/validate-trigger-paths.py
bash scripts/validate.sh
git diff --check
./sync-skills.sh --dry-run document-authoring
```

- [x] 只报告真实行为增量；静态通过不得冒充改善。无 Git、正式同步、安装、push 或 PR。

### Task 4: Owner 交付

- [x] 报告吸收项、已覆盖项、拒绝项、baseline/candidate 证据、验证结果和残余风险。
- [x] Git 与正式同步等待 Owner 另行授权。

### Task 5: 空泛评价的事实承重

**Files:**
- Modify: `fixtures/skill-eval/document-authoring-humanization-behavior-cases.json`
- Modify: `document-authoring/references/review-and-revision.md`
- Modify: `references/source-map.md`
- Modify: `scripts/validate-trigger-paths.py`

- [x] 用三个独立同模型 Worker 建立 baseline：机械过渡、重复收尾和缺数据场景均通过；宣传性空话只有 1/3 删除，另 2/3 仅以较轻近义词保留，形成窄 RED。
- [x] 先把“空泛评价不得只降调换词；无事实、判断或行动功能时删除，并让可核实事实承重”写入现有行为 fixture；结构校验通过，契约指纹按预期从 `addacdec...` 变为 `ca3971...` 并触发 RED。
- [x] 只在现有保真去模板化协议补一条对应规则，不吸收英文词表、固定标点 / 句式规则、伪造数字、检测评分或自动工作流。
- [x] 由同一批 Worker 重跑原样场景；3/3 删除无依据的空泛评价，只保留三项功能事实且未补造信息。
- [x] 运行 fixture 校验、触发路径、全仓校验、`git diff --check` 和 `document-authoring` 同步 dry-run；不执行 Git 或正式同步。

### Task 6: 空结构自述与不可追溯归因

**Files:**
- Modify: `fixtures/skill-eval/document-authoring-humanization-behavior-cases.json`
- Modify: `document-authoring/references/review-and-revision.md`
- Modify: `scripts/validate-trigger-paths.py`

- [x] 用三个独立同模型 Worker 建立 baseline：短段结构自述 3/3 只换词不删除；无来源“业内人士”归因 2/3 换壳保留；正式语体 3/3 保留 `应当 / 可以 / 不得`，不形成 RED。
- [x] 先新增两个行为案例并确认契约指纹 RED：8 案例结构有效，契约指纹按预期从 `ca3971...` 变为 `79e119...`。
- [x] 只在 `保真去模板化` 的功能判断与保真回读中各补一句，不修改 `novelist`，不新增正式语体规则。
- [x] 同一批 Worker 重跑原样场景；结构自述和重复收尾 3/3 删除，正文顺序与事实保持；模糊归因 3/3 删除换壳、保留证据缺口与建议属性。
- [x] 运行 fixture、触发路径、全仓校验、`git diff --check` 和 `document-authoring` 同步 dry-run；不执行 Git 或正式同步。

### Task 7: CR 修复与可复核准出

**Files:**
- Modify: `document-authoring/references/review-and-revision.md`
- Modify: `fixtures/skill-eval/document-authoring-humanization-behavior-cases.json`
- Create: `fixtures/skill-eval/document-authoring-humanization-responses.jsonl`
- Create: `fixtures/skill-eval/document-authoring-humanization-scores.jsonl`
- Modify: `scripts/validate-trigger-paths.py`
- Modify: `scripts/validate.sh`

- [x] 消除“只改措辞不得删句”与“删除无功能套话”的冲突：只保护承载独有语义的句子，允许删除不承载独有语义的套话、结构自述和重复收尾。
- [x] 将“没有具名来源或公开文件”收紧为“缺少可核验的公开文件或具名来源”，不得扩大成没有任何来源支持。
- [x] 以最终 candidate reference 重跑 3 个同模型 Worker × 8 个案例，保存 48 条 baseline / candidate 原始响应；固定 seed 盲化后，由 3 个独立 Checker 保存 48 条 A / B 评分。
- [x] 首轮真实 `score` 因事故案例一次新引入“起开始”复沓而失败；补充新病句回读规则并重跑所有 candidate 后，最终 baseline `3.7563`、7 blockers，candidate `5.0`、0 blockers，release gate 通过。
- [x] 全仓校验重新执行 `blind -> score`，并以 SHA-256 同时锁定 cases、responses 和 scores，防止原答变化后静默沿用旧评分。
