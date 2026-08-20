# Fiction Visual Designer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增处于 `candidate` 状态的 `fiction-visual-designer` Skill，把小说语义或独立创意转成可审查的视觉设计契约，并以东方幻想作为首个按需 reference。

**Architecture:** `novelist` 持有故事语义与正典，`fiction-visual-designer` 持有视觉转译与视觉验收，`imagegen` 持有图片生成执行。Skill 使用通用五轴方法，东方幻想专项通过一手实物、工艺、植物与生态证据约束幻想变形；没有独立行为证据前不开放安装或隐式触发。

**Tech Stack:** Markdown、YAML、JSON、仓库现有 Ruby/Python/Shell 校验器，以及可选使用 Pillow 的本地确定性拼版脚本；不自动安装依赖或新增供应商适配。

**Authority:** `docs/superpowers/specs/2026-08-19-fiction-visual-designer-design.md` 是本实现的设计权威。当前工作区已有其他未提交修改；只编辑本计划列出的文件，不清理、不覆盖、不暂存、不提交其他变更。本轮联网只用于用户已确认的公开来源核验；Git、安装、同步和发布不在本计划授权内。

---

## File Map

**Create:**

- `fiction-visual-designer/SKILL.md`：触发、职责、核心流程、交接、路由和红线。
- `fiction-visual-designer/admission.json`：候选状态和未完成行为验证 blocker。
- `fiction-visual-designer/agents/openai.yaml`：UI metadata，默认关闭隐式调用。
- `fiction-visual-designer/references/visual-design-method.md`：通用五轴方法、对象专项与视觉验收。
- `fiction-visual-designer/references/eastern-fantasy.md`：东方幻想的证据到幻想转换方法。
- `fiction-visual-designer/references/artifact-rendering.md`：已确认器物设计的多视图生成、连续性验收与拼版边界。
- `fiction-visual-designer/references/source-map.md`：本轮实际读取来源、许可、时效、吸收与拒绝边界。
- `fiction-visual-designer/assets/visual-design-sheet-template.md`：按任务裁剪的视觉设计单模板。
- `fiction-visual-designer/scripts/compose-design-sheet.py`：把四张已验收源图确定性拼成 PNG 设计单；不联网、不生成图像、不覆盖既有文件。
- `fixtures/skill-eval/fiction-visual-designer-behavior-cases.json`：8 个行为压力样例和 release gate。

**Modify:**

- `README.md`：新增用户入口、能力路由和小说到图片的协作链；不复制 Skill 正文。
- `scripts/validate.sh`：把新行为 fixture 的结构验证接入统一校验。
- `fixtures/skill-eval/prompt-cases.json`：补足新 Skill 的静态正向与硬负例触发样例；不作为行为准入证据。
- `scripts/audit-skill-eval-fixtures.py`：登记新 Skill ID、识别别名和已有 `imagegen` 交接目标；不改变审计契约或阈值。

**Do not modify:**

- `novelist/**`：本轮只建立交接契约，不改变小说家现有职责或行为证据。
- `sync-skills.sh`、安装目录和用户配置：候选准入应由现有脚本自动阻止。

---

### Task 1: Establish The Behavior Contract And RED Evidence Boundary

**Files:**

- Create: `fixtures/skill-eval/fiction-visual-designer-behavior-cases.json`

- [ ] **Step 1: Write the behavior case contract before creating the Skill**

Create version `1` with the existing five weighted dimensions:

```json
{
  "correctness": 0.35,
  "autonomy": 0.2,
  "actionability": 0.25,
  "safety": 0.15,
  "concision": 0.05
}
```

Use an `improvement` release gate: candidate blockers must be zero, correctness and safety regression limits are `0.0`, weighted score must improve, auditable judgments are required, and high-risk candidate criteria pass rate must be `1.0`.

Add exactly eight cases:

| Case ID | Prompt focus | Required evidence |
| --- | --- | --- |
| `fiction-visual-should-design-qiu-shui-sword-with-canon-boundary` | 有轮回故事与秋水意象约束的秋水剑 | 剑/刀正名、故事事实与视觉候选分层、结构/材质/状态、负面约束、未确认项不写成正典 |
| `fiction-visual-should-design-character-across-life-stages` | 同一角色三个年龄阶段与旧伤 | 不可变身份锚点、身体/职业/关系造成的可变状态、服装支持动作、不是衣柜清单 |
| `fiction-visual-should-build-sect-cross-asset-language` | 宗门人物、建筑、器物共享语法 | 材质/结构/母题跨对象一致，建筑可生活，人物与器物不被同一纹样淹没 |
| `fiction-visual-should-ground-living-fantasy-assets` | 同一生境中的灵药与灵兽 | 植物形态、采制状态、骨骼运动、食性生态、能力代价与可见痕迹成立，不靠换色发光或特征拼贴 |
| `fiction-visual-should-review-generated-sword-image` | 审查一张把剑画成刀的生成图 | 按设计契约指出结构漂移，区分设计问题与模型限制，不因图片好看改正典 |
| `fiction-visual-should-route-combined-story-design-generation` | 同时要求补故事、设计兵器并出图 | 明确 `novelist -> fiction-visual-designer -> imagegen` 顺序和各自验收，不吞并职责 |
| `fiction-visual-should-design-patterned-inscribed-credential-artifacts` | 篆文、云纹与祥纹、凭符和碑刻共同参与启闸 | 载文、纹样、凭证和空间工器分型；制作、验合、权限与损耗可复核 |
| `fiction-visual-should-render-confirmed-artifact-design-sheet` | 已确认器物设计的四视图与拼版 | 先验收身份锚图，再继承不可变锚点生成其余视图，源图通过后确定性拼版 |

每个 case 提供 3-5 条可独立判断的 `criteria`；不得在 case 中放本地绝对路径、来源结论或预期完整答案。

- [ ] **Step 2: Validate the unbound fixture schema**

Run:

```bash
scripts/evaluate-skill-behavior.py validate \
  --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json
```

Expected: `OK behavior cases=8`。此时只证明契约结构合法，不证明 baseline 失败或候选有效。

- [ ] **Step 3: Capture RED only in an uncontaminated fresh run**

When execution mode permits a fresh subagent, run at least the two high-risk cases `qiu-shui-sword` and `route-combined-story-design-generation` without loading the candidate Skill. Save raw task-local responses under `/tmp/fiction-visual-designer-baseline/` and record which criteria failed.

Expected RED: baseline 至少出现一次提示词化、视觉候选越过正典、剑刀结构混淆或职责吞并。若 baseline 全部满足标准，不得伪造失败；重新判断新 Skill 是否仍有非平庸价值。

If no fresh execution is authorized, leave behavior evidence absent and retain blocker `FVD-001`; static fixture validation is not RED evidence.

**Git checkpoint:** none; Git requires separate user authorization.

---

### Task 2: Initialize The Candidate Skill And Write The Core Contract

**Files:**

- Create: `fiction-visual-designer/SKILL.md`
- Create: `fiction-visual-designer/agents/openai.yaml`
- Create: `fiction-visual-designer/admission.json`

- [ ] **Step 1: Initialize only the approved resource directories**

Run:

```bash
python3 /Users/wuxp/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  fiction-visual-designer \
  --path . \
  --resources references,assets \
  --interface 'display_name=小说视觉设计师' \
  --interface 'short_description=把叙事语义转成可审查、可生成、可验收的视觉设计与连续性' \
  --interface 'default_prompt=使用 $fiction-visual-designer 把当前故事语义或独立创意转成视觉设计契约，并区分正典、视觉候选与生成执行。'
```

Expected: only `SKILL.md`、`agents/openai.yaml`、`references/` and `assets/` are created under `fiction-visual-designer/`; no examples or scripts directory exists.

- [ ] **Step 2: Replace the generated `SKILL.md` with the approved Level 2 contract**

The frontmatter must be:

```yaml
---
name: fiction-visual-designer
description: Use when 用户要设计、延展、审查或统一小说、漫画、影视、动画或游戏叙事中的人物外形、服饰、场景、建筑、兵器、器物、植物、药物、灵物、怪物或其他视觉资产；小说正文与情节、纯图片生成、Web UI、纯史实考据和正式设定集整理不触发。
---
```

Keep the body under 500 lines and include only:

1. 定位与作者/`novelist`/`imagegen`/`document-authoring` 职责边界。
2. 通用五轴：叙事身份、结构与功能、材质与工艺、环境与关系、状态与连续性。
3. 八步流程：继承权威、判定任务、建立母题、完成五轴、标注证据、锁定连续性、形成设计单、验收生成结果。
4. 视觉候选、已确认设计、已验收图像三种状态。
5. 按任务读取三个 reference 和一个 asset 的场景路由。
6. 最小交付、停止条件和不越权红线。

Do not copy the complete category checklist, source details or template fields into `SKILL.md`.

- [ ] **Step 3: Make the agent metadata candidate-only**

Ensure `agents/openai.yaml` contains:

```yaml
interface:
  display_name: "小说视觉设计师"
  short_description: "把叙事语义转成可审查、可生成、可验收的视觉设计与连续性"
  default_prompt: "使用 $fiction-visual-designer 把当前故事语义或独立创意转成视觉设计契约，并区分正典、视觉候选与生成执行。"
policy:
  allow_implicit_invocation: false
```

- [ ] **Step 4: Add a fail-closed admission record**

Create:

```json
{
  "status": "candidate",
  "updated_at": "2026-08-19",
  "blockers": [
    {
      "id": "FVD-001",
      "summary": "尚未取得同一 runner/model 的 baseline/candidate 重复执行、盲评与可复核准入证据",
      "owner": "用户/仓库 Owner"
    }
  ]
}
```

- [ ] **Step 5: Run the first structural checks**

Run:

```bash
ruby scripts/validate-skill-frontmatter.rb .
python3 scripts/check-skill-admission.py --status fiction-visual-designer
```

Expected: frontmatter passes and admission status prints `candidate`.

**Git checkpoint:** none; Git requires separate user authorization.

---

### Task 3: Write The General Method And Design Sheet

**Files:**

- Create: `fiction-visual-designer/references/visual-design-method.md`
- Create: `fiction-visual-designer/assets/visual-design-sheet-template.md`

- [ ] **Step 1: Write the general method reference**

Start with the repository reference contract:

```markdown
## 使用时机
## 不适用场景
## 读取后必须产出
## 需要继续读取的 reference
## 按任务读取索引
```

Then define:

- The five common axes and their acceptance questions.
- Visual-system tasks versus single-object tasks.
- Category-specific checks for character, costume, architecture/environment, weapon/object, botanical/medicine, and creature/spirit object.
- Immutable identity anchors, mutable states, state ladders and continuity review.
- Media-neutral generation handoff fields.
- Render review that distinguishes contract defects, generation defects and tool limits.
- Failures: canon conflict, missing evidence, cross-object drift and tool incapability.
- An optional artifact block for object duty, structural interfaces, materials and making, inscriptions and permissions, supernatural state, damage and repair.

Do not include Chinese historical claims or external source prose; those belong in `eastern-fantasy.md` and `source-map.md`.

- [ ] **Step 2: Write the reusable design sheet**

The asset must contain these headings and status choices:

```markdown
# 视觉设计单

状态：视觉候选 / 已确认设计 / 已验收图像
任务模式：独立设计 / novelist 交接 / 现有设计审查 / 生成结果验收

## 权威与边界
## 设计结论
## 视觉母题
## 五轴设计
## 不可变锚点与允许变化
## 事实、推演与虚构边界
## 负面约束
## 待作者确认
## 生成交接规格
## 验收结果
```

Add one instruction at the top: delete unused sections; template completeness does not authorize inventing facts.

- [ ] **Step 3: Check discoverability and duplication**

Run:

```bash
rg -n 'visual-design-method|visual-design-sheet-template' fiction-visual-designer/SKILL.md
rg -n '来源矩阵|SRC-' fiction-visual-designer/references/visual-design-method.md
```

Expected: `SKILL.md` links both resources; the second command returns no matches because source details are not duplicated into the method reference.

**Git checkpoint:** none; Git requires separate user authorization.

---

### Task 4: Write The Eastern Fantasy Specialization And Source Boundary

**Files:**

- Create: `fiction-visual-designer/references/eastern-fantasy.md`
- Create: `fiction-visual-designer/references/source-map.md`

- [ ] **Step 1: Write the specialization as a transformation method**

Use the same five mandatory reference headings as Task 3. Make the central chain authoritative:

```text
真实原型
-> 结构与工艺
-> 文化母题及使用边界
-> 故事功能
-> 有限幻想变形
-> 可见代价、磨损与历史痕迹
```

Cover the six category checks from the design spec and include explicit anti-patterns:

- 剑刀不分、只堆发光纹路和宝石。
- 长发宽袍、云海悬浮和水墨作为通用仙侠答案。
- 龙凤、饕餮和云雷纹脱离时代与使用语境随机拼贴。
- 巨构建筑没有结构、交通、生活、仪式和维护。
- 灵药只给普通植物换颜色，灵兽只给动物加角、翅膀和粒子。
- 稀有度越高就材质越多、形体越复杂、光效越强。
- 把篆书、云纹、祥纹、印玺、符节、符箓和阵图混成同一种发光纹样。

For supernatural, patterned and inscribed artifacts, use mythology and ritual, historical objects, construction logic and making processes as four evidence lenses. Distinguish inscribed components, pattern and decorative crafts, credential devices, ritual media and spatial tools before designing their motifs, organization, carriers, permissions, interfaces, activation and wear.

- [ ] **Step 2: Write a traceable source map from the already-read material**

Use source IDs and record URL or repository, read date `2026-08-19`, read scope, license or usage boundary, transferable method, rejected content and freshness risk. Include at minimum:

- `liyue-aigc/xianxia-visual-director`：许可未明确；只吸收空间、构图、尺度、光色和材质检查。
- `khanhhuyenngo985-sys/character-scene-design-skills`：仓库未见 LICENSE；只吸收身份锚点、三视图、状态与连续性方法。
- `Donchitos/Claude-Code-Game-Studios` 的 `art-bible` 与 `asset-spec`：MIT；只吸收视觉语法和对象设计单。
- `jwynia/agent-skills` 的 `systemic-worldbuilding` 与 `settlement-design`：许可未明确；只吸收系统后果和聚落因果。
- 网易雷火《永劫无间》的美术探索复盘与《九畿：岐风之旅》访谈：作为制作复盘，不作为史实权威。
- UNESCO、故宫博物院、中国国家博物馆、Met、香港浸会大学中药材图像数据库、Kew、SFWA 与可信生物设计文章：分别约束建筑、兵器、服饰、植物、生态和生物结构。

Do not copy source prose, images, prompts, templates or code. Mark floating repository branches as freshness risks instead of inventing commit hashes.

- [ ] **Step 3: Run reference and source audits**

Run:

```bash
python3 scripts/audit-reference-indexes.py
scripts/audit-source-map.py
```

Expected: both commands pass; every `references/*.md` has use timing, non-applicability, required output, next-reference routing and task reading index.

**Git checkpoint:** none; Git requires separate user authorization.

---

### Task 5: Complete The Behavior Source Binding

**Files:**

- Modify: `fixtures/skill-eval/fiction-visual-designer-behavior-cases.json`

- [ ] **Step 1: Bind baseline and candidate source profiles**

Use baseline paths `[]` with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Candidate paths, in this exact order:

```json
[
  "fiction-visual-designer/SKILL.md",
  "fiction-visual-designer/references/visual-design-method.md",
  "fiction-visual-designer/references/eastern-fantasy.md",
  "fiction-visual-designer/references/artifact-rendering.md",
  "fiction-visual-designer/references/source-map.md",
  "fiction-visual-designer/assets/visual-design-sheet-template.md",
  "fiction-visual-designer/scripts/compose-design-sheet.py"
]
```

Compute the candidate digest with the evaluator's path/NUL/content/NUL contract:

```bash
python3 -c 'import hashlib; from pathlib import Path; paths=["fiction-visual-designer/SKILL.md","fiction-visual-designer/references/visual-design-method.md","fiction-visual-designer/references/eastern-fantasy.md","fiction-visual-designer/references/artifact-rendering.md","fiction-visual-designer/references/source-map.md","fiction-visual-designer/assets/visual-design-sheet-template.md","fiction-visual-designer/scripts/compose-design-sheet.py"]; d=hashlib.sha256(); [(d.update(p.encode()),d.update(b"\0"),d.update(Path(p).read_bytes()),d.update(b"\0")) for p in paths]; print(d.hexdigest())'
```

Insert the exact printed digest as `source_profiles.candidate.sha256` with candidate ID `fiction-visual-designer-current`.

- [ ] **Step 2: Validate the bound contract and prepare the execution manifest**

Run:

```bash
scripts/evaluate-skill-behavior.py validate \
  --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json
scripts/evaluate-skill-behavior.py prepare \
  --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json \
  --trials 3 \
  --output /tmp/fiction-visual-designer-tasks.jsonl
```

Expected: validation reports eight cases and prepare writes 48 tasks: 8 cases x 3 trials x 2 conditions.

- [ ] **Step 3: Preserve the evidence boundary**

Do not create response, score or report artifacts in the repository unless the full baseline/candidate runs and independent blind judgments actually occur. Fixture validity and task-manifest generation do not clear `FVD-001`.

**Git checkpoint:** none; Git requires separate user authorization.

---

### Task 6: Add The Repository Routing And Unified Validation

**Files:**

- Modify: `README.md`
- Modify: `scripts/validate.sh`

- [ ] **Step 1: Add the minimal README user entry**

Add one prompt example near the existing novel/UI entries:

```text
$fiction-visual-designer：继承 <小说正典或独立创意>，为 <人物/服饰/建筑/兵器/灵药/灵物> 形成视觉设计契约；区分视觉候选、已确认设计和已验收图像，确认后再交 imagegen。
```

Add one capability-table row marked `candidate`, and update the novel delivery composition to state:

```text
novelist 稳定故事语义与正典 -> fiction-visual-designer 完成视觉转译与验收 -> imagegen 执行生成 -> 需要正式设定集时交 document-authoring
```

Do not copy the five-axis checklist or external source list into `README.md`.

- [ ] **Step 2: Add one deterministic fixture validation gate**

Near the existing novelist behavior-case validations in `scripts/validate.sh`, add:

```bash
echo "==> fiction visual designer behavior cases"
run_gate scripts/evaluate-skill-behavior.py validate \
  --cases "fixtures/skill-eval/fiction-visual-designer-behavior-cases.json"
```

Do not add model calls, generated responses or score claims to `validate.sh`.

- [ ] **Step 3: Verify candidate routing remains fail closed**

Run:

```bash
python3 scripts/check-skill-admission.py --status fiction-visual-designer
./sync-skills.sh --dry-run fiction-visual-designer
```

Expected: the first command prints `candidate`; the dry-run refuses with `Skill is not installable: fiction-visual-designer (candidate)`. The refusal is the expected pass condition.

**Git checkpoint:** none; Git requires separate user authorization.

---

### Task 7: Run Targeted And Repository Verification

**Files:**

- Verify all files listed in the File Map.

- [ ] **Step 1: Run targeted structural checks**

Run:

```bash
ruby scripts/validate-skill-frontmatter.rb .
python3 scripts/audit-reference-indexes.py
scripts/audit-source-map.py
python3 scripts/check-skill-admission.py
scripts/evaluate-skill-behavior.py validate \
  --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json
scripts/audit-skills.sh
```

Expected: all commands pass; admission audit accepts `candidate` with blocker and security audit finds no executable or credential-reading surface in the new Skill.

- [ ] **Step 2: Run whitespace and scope checks**

Run:

```bash
git diff --check
git status --short
git diff -- README.md scripts/validate.sh
```

Expected: no whitespace errors. Review only the new Skill, new plan/spec/fixture, and the narrow README/validator hunks; pre-existing dirty files remain untouched.

- [ ] **Step 3: Run the full repository validator**

Run:

```bash
./scripts/validate.sh
```

Expected: full suite passes. If an unrelated pre-existing fixture or stale evidence fails, record the exact command and failure without editing unrelated artifacts or claiming full validation.

- [ ] **Step 4: Self-review against the design authority**

Check every section of `docs/superpowers/specs/2026-08-19-fiction-visual-designer-design.md` against an implemented file or validation result. Search for placeholders and unintended scope:

```bash
rg -n 'TBD|TODO|待补|自动安装|自动写回|默认联网|allow_implicit_invocation: true' \
  fiction-visual-designer \
  fixtures/skill-eval/fiction-visual-designer-behavior-cases.json
```

Expected: no placeholders, no automatic high-risk behavior and no implicit invocation. Legitimate negative statements containing `自动安装`、`自动写回` or `默认联网` must be manually confirmed as prohibitions rather than capabilities.

**Git checkpoint:** none; report that Git was not run beyond read-only diff/status checks.

---

### Task 8: Optional Independent Behavior Gate

**Files:**

- Potentially modify after real evidence: `fiction-visual-designer/admission.json`
- Do not create repository evidence files unless the full evaluation is completed.

- [ ] **Step 1: Require explicit execution authority**

Before running fresh agents or an external model/provider, confirm the permitted execution method, cost/network boundary and evidence output location. This step is not authorized merely by approving local Skill implementation.

- [ ] **Step 2: Run the prepared baseline/candidate tasks**

Use `/tmp/fiction-visual-designer-tasks.jsonl` with the same runner/model for all 48 tasks. Baseline receives no Skill source; candidate receives only the declared candidate source paths. Preserve `case_sha256` and `source_sha256` in every response row.

- [ ] **Step 3: Blind and score only complete evidence**

Run:

```bash
scripts/evaluate-skill-behavior.py blind \
  --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json \
  --responses /tmp/fiction-visual-designer-responses.jsonl \
  --output /tmp/fiction-visual-designer-blind.jsonl \
  --key-output /tmp/fiction-visual-designer-key.json \
  --seed 731
scripts/evaluate-skill-behavior.py score \
  --cases fixtures/skill-eval/fiction-visual-designer-behavior-cases.json \
  --scores /tmp/fiction-visual-designer-scores.jsonl \
  --key /tmp/fiction-visual-designer-key.json \
  --blind /tmp/fiction-visual-designer-blind.jsonl \
  --output /tmp/fiction-visual-designer-report.json
```

Expected: candidate blockers are zero, every high-risk criterion passes, correctness and safety do not regress, and weighted score improves. A generated response without independent blind judgment is incomplete evidence.

- [ ] **Step 4: Keep admission fail closed unless every gate passes**

Only after reproducible evidence exists may a separate Owner decision update `admission.json` from `candidate` to `installable` and evaluate `allow_implicit_invocation`. This implementation plan does not authorize that promotion, installation or sync.

**Git checkpoint:** none; any stage/commit requires a separate explicit user request.
