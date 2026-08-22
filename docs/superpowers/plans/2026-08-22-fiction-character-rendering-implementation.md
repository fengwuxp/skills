# Fiction Character Rendering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 `fiction-visual-designer` 中补齐人物图片角色、制作与采用分轴、逐属性采用、局部编辑 / 整图重绘路由和每图一次定向修订上限。

**Architecture:** `novelist` 持有人物与正典，`fiction-visual-designer` 持有媒介中立的人物视觉契约、成图编排和验收，`imagegen` 持有真实生成与编辑执行。人物设计与人物成图拆成两个按需 reference；不新增顶层 Skill、脚本或供应商依赖。

**Tech Stack:** Markdown、YAML、JSON、仓库现有 Ruby / Python / Shell 校验器。

**Authority:** `docs/superpowers/specs/2026-08-22-fiction-character-rendering-design.md`。当前工作区已有相关未提交修改；只编辑本计划列出的文件，不覆盖无关改动，不执行 Git、同步或发布。

---

## File Map

**Create:**

- `fiction-visual-designer/references/character-rendering.md`：人物审美基准、身份锚图、生成修订和停止契约。

**Modify:**

- `fiction-visual-designer/references/character-visual-design.md`：图片角色与逐属性采用矩阵。
- `fiction-visual-designer/SKILL.md`：人物成图路由与状态边界。
- `fiction-visual-designer/agents/openai.yaml`：人物成图可发现性；保持显式调用策略。
- `fiction-visual-designer/assets/visual-design-sheet-template.md`：可裁剪人物专项字段。
- `fixtures/skill-eval/fiction-visual-designer-behavior-cases.json`：现有人物审美案例中的成图行为标准和候选 source hash。
- `fiction-visual-designer/admission.json`：更新候选日期，保留 `FVD-001`。
- `README.md`：更新候选能力入口，不宣称准入。

## Task 1: Freeze RED Evidence And Add Behavior Contract

- [ ] 记录只读基线中缺失的图片角色、逐属性采用、编辑 / 重绘路由和迭代预算；不提交原图或私有路径。
- [ ] 在现有人物审美案例中增加“审美基准不等于身份锚图”和“局部编辑优先于整图重绘”两组高风险标准，保持 fixture 的案例数量上限。
- [ ] 运行 `python3 scripts/evaluate-skill-behavior.py validate --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json`；更新实现前应只把新增案例视为 RED 契约，不把 schema 通过视为行为通过。

## Task 2: Implement Minimal Character Rendering Contract

- [ ] 新建 `character-rendering.md`，只覆盖输入门禁、图片角色、锚图顺序、制作与采用分轴、逐属性采用、编辑 / 重绘判断、每图一次定向修订和停止条件。
- [ ] 在 `character-visual-design.md` 引用人物成图 reference，并保留外貌、衣饰、阶段与关系的现有权威。
- [ ] 在 `SKILL.md` 和 `agents/openai.yaml` 增加已确认人物成图路由；`imagegen` 继续持有模型、参数、凭据和执行。
- [ ] 在视觉设计单增加人物图片角色、逐属性采用矩阵和最小差异字段，不新建第二套人物模板。
- [ ] 更新 README 和 `admission.json`；保持 `candidate / FVD-001`。

## Task 3: Refresh Deterministic Contracts

- [ ] 把 `character-rendering.md` 加入 fixture candidate source paths。
- [ ] 使用 `scripts/evaluate-skill-behavior.py` 的 source-set 算法重算 candidate SHA-256，不修改 baseline profile。
- [ ] 运行 fixture schema、frontmatter、reference 和同步 dry-run 校验；记录仓库已有的无关基线失败。

## Task 4: Forward Behavior Check

- [ ] 由新的只读评估者使用修改后的 Skill 处理相同四张人物图。
- [ ] 验证其明确区分四类图片角色、逐属性采用、局部编辑 / 整图重绘和一次修订停止条件。
- [ ] 不把单次文本行为检查称为真实绘制能力通过；保留 `FVD-001`，等待同一 runner/model 的重复生成与盲评。

## Task 5: Final Scope Review

- [ ] 运行 `git diff --check`，检查只修改 File Map 所列文件。
- [ ] 复核没有私有绝对路径、模型下载、API Key、自动写回、Git 或发布授权。
- [ ] 报告实际校验结果、基线阻塞和仍未完成的真实图片盲评。
