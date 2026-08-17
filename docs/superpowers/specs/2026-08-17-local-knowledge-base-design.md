# AI 本地知识库 Skill 设计

## 1. 目标

新增专业 Skill `local-knowledge-base`，把用户明确指定的本地资料编译为可追溯、互相链接、便于人阅读且便于 AI 快速定位的 Markdown 知识库。

本设计采用开放文件协议，不依赖 Obsidian 专有能力。Obsidian、Codex 和其他能够读取 Markdown 的 Agent 可以消费同一套知识，不建立平行事实源。

核心操作为：

```text
Init -> Ingest -> Query -> Lint
```

## 2. 适用边界

`local-knowledge-base` 负责：

- 初始化符合契约的本地 Markdown Vault。
- 把明确授权读取的资料登记为来源，并生成知识变更候选。
- 根据索引按需读取知识页和来源卡，回答问题并提供引用。
- 检查知识库结构、链接、状态、时效和索引健康度。
- 在明确命令下修复生成索引等确定性结构问题。

`local-knowledge-base` 不负责：

- 替代项目内 PRD、ADR、源码、测试、小说正典或其它领域权威。
- 保存用户协作偏好或 Skill 学习记录。
- 裁决产品、工程、支付、法律、历史或创作领域事实。
- 默认联网、扫描未授权目录、执行 Git、安装依赖或自动晋升候选知识。
- 建设向量库、图数据库、后台服务、Obsidian 插件或万能格式转换器。

用户提供材料把该方法归因于“卡帕西在 4 月初的分享”，但当前没有原始发布内容可核验。实现只能把方法视为用户提供的参考材料，不能把作者与时间写成已核验事实。

## 3. 与现有能力的关系

| 能力 | 职责 |
| --- | --- |
| `local-knowledge-base` | Vault 初始化、资料编译、查询、双链和健康巡检。 |
| `wise-agent` | 跨任务目标、知识晋升、专业能力组合和最终收口。 |
| 领域 Skill | 判断领域含义和事实边界，不直接改变知识状态。 |
| `document-authoring` | 正式报告、制度和出版载体，不接管 Wiki。 |
| `resource-capability-distiller` | 资料需要转化为可复用 Agent 能力时负责能力提炼与归位。 |
| `novelist` | 小说正典、候选、旧稿和创作连续性仍由创作项目权威管理。 |
| 用户协作档案 | 仅保存已确认协作偏好，与知识库物理隔离。 |
| Skill 学习账本 | 仅保存 Skill 改进候选，与知识库物理隔离。 |

新 Skill 初始状态为 `candidate`，`agents/openai.yaml` 必须设置 `allow_implicit_invocation: false`。只有结构、脚本、触发和真实行为证据通过独立评审后，才允许转为 `installable` 并评估是否开放隐式调用。

## 4. 总体架构

### 4.1 权威顺序

```text
项目权威文件 / 原始资料
        ↓
来源卡 sources/
        ↓
候选变更 candidates/
        ↓ Owner 确认
正式知识 wiki/
        ↓
生成索引 indexes/
```

- 项目权威文件和原始资料提供事实证据。
- 来源卡只登记来源、读取状态、摘要和适用边界，不取代原文。
- 候选可以参与探索，但不能作为已确认事实。
- 正式 Wiki 只保存已确认、可复用且已归位的知识。
- 索引只负责导航，可以重建，不能承载唯一事实。
- `.compiled/` 是可再生中间产物，不能作为事实权威。

项目事实与全局 Wiki 冲突时，必须回到项目 Owner 和项目权威文件裁决。当前代码也不能自动覆盖已批准的业务契约。

### 4.2 Vault 目录

```text
knowledge/
├── AGENTS.md
├── index.md
├── inbox/
├── archive/
├── .compiled/
├── sources/
├── wiki/
│   ├── concepts/
│   ├── entities/
│   ├── methods/
│   └── decisions/
├── projects/
├── candidates/
│   ├── insights/
│   └── conflicts/
├── indexes/
│   ├── catalog.md
│   ├── status.md
│   └── domains/
└── logs/
    └── changes.md
```

目录职责：

- `inbox/`：用户明确放入或指定的待处理材料。
- `archive/`：已处理原件，只读保留；项目权威文件不复制到这里。
- `.compiled/`：非 Markdown 材料的临时 Markdown 副本，可重新生成。
- `sources/`：来源卡。
- `wiki/`：唯一正式知识页面。
- `projects/`：项目入口、权威路径和适用范围，不复制项目事实。
- `candidates/`：待确认洞察和冲突。
- `indexes/`：脚本生成的目录和状态视图。
- `logs/changes.md`：结构化、简短、不可替代事实权威的操作日志。

## 5. 页面契约

### 5.1 通用规则

- ID 创建后不可改变；文件名采用 `<ID>-<清晰主题>.md`。
- Frontmatter 只使用扁平 `key: value` 和行内数组 `[a, b]`，不使用嵌套对象或多行 YAML，以便标准库脚本稳定解析。
- 标题和正文使用自然中文，不为机器检索堆砌关键词。
- 一页只回答一个稳定问题；是否拆页按职责、Owner 和变化周期判断，不设置机械字数阈值。
- 页面开头先给一句话结论和适用边界。
- 双链必须带有上下文或关系说明，不能只堆链接。
- 时间使用 ISO 日期；时效知识必须声明核验和复核时间。

### 5.2 来源卡

```yaml
---
id: SRC-20260817-001
type: source
read_status: read
origin: /path/to/source
source_sha256: <sha256>
captured_at: 2026-08-17
applicable_scope: <scope>
---
```

正文至少包含：

- 摘要。
- 读取方式和读取限制。
- 许可、隐私和使用边界。
- 关联知识页。
- 冲突、未知或无法核验项。

本地副本存在时记录 `source_sha256`。项目权威或不能复制的来源改为记录可复核路径、revision 或版本，不伪造文件哈希。AI 生成摘要不是原始证据。

### 5.3 正式知识页

```yaml
---
id: KB-0001
type: concept
status: confirmed
domains: [ai, knowledge-management]
source_refs: [SRC-20260817-001]
candidate_refs: []
updated_at: 2026-08-17
verified_at: 2026-08-17
review_after:
aliases: []
---
```

`type` 允许 `concept / entity / method / decision`。正文固定保留：

```text
结论
适用边界
依据与来源
相关知识
冲突与退役记录
```

稳定知识可以不填写 `review_after`。工具版本、平台限制、外部规范等时效知识必须填写 `verified_at` 和 `review_after`。

### 5.4 候选页

```yaml
---
id: CAND-0001
type: insight
status: candidate
target: KB-0001
derived_from: [KB-0002, SRC-20260817-001]
promoted_to:
created_at: 2026-08-17
owner: <owner>
---
```

正文记录候选变化、推理依据、影响范围、验证方式和待裁决项。`type` 只允许 `insight / conflict`；`status` 只允许 `candidate / conflict / promoted / rejected / superseded`。来源冲突同时使用 `type: conflict` 和 `status: conflict`，并列保存各方主张、来源、版本和适用范围，不静默合并。

### 5.5 项目入口页

```yaml
---
id: PROJECT-skills
type: project
status: active
domains: [ai, skills]
authority_paths: [/absolute/path/to/project/AGENTS.md]
updated_at: 2026-08-17
---
```

项目入口页只记录项目身份、适用范围、权威文件路径和领域索引。它不复制项目事实，不把本地路径可访问等同于内容已经核验。

### 5.6 状态

候选记录和正式知识页使用两条生命周期，不能原地改 ID 或 `type`：

```text
CAND: candidate -> conflict -> promoted / rejected / superseded
      candidate -----------> promoted / rejected / superseded
KB:   confirmed -----------> deprecated
```

- `candidate / conflict`：候选尚未生效；查询中引用时必须标明状态，冲突不能自动合并为单一结论。
- `promoted`：Owner 已采纳候选；另行创建或更新 `KB-*` 正式页，候选页保留 `CAND-*`、原 `type`，并以 `promoted_to` 指向正式页。
- `rejected / superseded`：保留最小裁决记录和替代指针，避免相同候选反复出现。
- `confirmed / deprecated`：只用于 `KB-*` 正式页；退役页保留历史链接并指向替代页面。

晋升是一个原子变更：创建或更新正式页，在正式页 `candidate_refs` 回链候选，把候选改为 `promoted` 并填写 `promoted_to`，再同步索引和引用。任一步失败都不把候选视为已生效。同一事实只保留一个当前正式页面；确认新值时还要同步检查旧值、反向链接、引用页面和其他未决候选。

## 6. 面向人和 AI 的检索设计

同一套 Markdown 同时服务人和 AI，不维护第二套知识正文。

| 入口 | 主要使用者 | 内容 |
| --- | --- | --- |
| `index.md` | 人 | 领域、项目、最近更新和待处理入口。 |
| `indexes/catalog.md` | AI | ID、标题、类型、状态、领域、一句话摘要和路径。 |
| `indexes/domains/*.md` | 人与 AI | 按领域组织的知识地图。 |
| `indexes/status.md` | 人与 AI | 候选、冲突、待复核和已退役内容。 |
| `projects/*.md` | 人与 AI | 项目权威入口、适用范围和可读取路径。 |

AI 查询顺序固定为：

```text
问题
-> 精确 ID / 别名 / 标题
-> catalog 或领域索引
-> 最少必要 Wiki 页面
-> 必要来源卡
-> 高风险或冲突时回到原始资料 / 项目权威
```

普通 Query 不扫描整个 Vault。只有 Lint、明确的全局盘点或索引重建可以全库扫描。索引只保存路由信息，不复制知识正文。

## 7. 操作流程

### 7.1 Init

1. 确认 Vault 根目录、允许写入范围、是否已有文件和隐私边界。
2. 从 `vault-AGENTS.template.md` 创建 Vault 规则。
3. 创建缺失目录、空索引和日志，不覆盖已有文件。
4. 运行只读检查，确认目录、权限和页面契约可用。

### 7.2 Ingest

```text
发现资料
-> 校验读取范围、来源和权限
-> 计算指纹并查重
-> 必要时转换临时 Markdown
-> 创建或更新来源卡
-> 检索已有知识页
-> 生成新增 / 修改 / 冲突候选
-> Owner 确认
-> 更新唯一知识页
-> 重建索引
-> 原件归档并记录日志
```

失败分支：

- 相同 SHA-256：复用现有来源卡，不创建重复知识页。
- 主题相同：生成既有页面的修改候选，不另建同义页面。
- 观点冲突：写入 `candidates/conflicts/`，不覆盖当前结论。
- 格式无法读取：标记 `unavailable`，不得生成虚假摘要。
- 来源、许可或适用范围不明：只停留在候选。
- 项目事实：只创建或更新项目入口，不复制项目权威正文。

任意格式转 Markdown 由 Agent 使用当前环境中已经可用的工具完成。首版不新增转换依赖；工具缺失时停止并说明未读取范围。

### 7.3 Query

```text
自然语言问题
-> 识别领域、对象、时间和证据等级
-> 读取 catalog 和相关领域索引
-> 读取最少必要页面
-> 必要时回读来源卡或项目权威
-> 区分已确认事实、综合推断和待确认
-> 输出带页面与来源引用的答案
-> 符合门禁时生成 insight candidate
```

不是每次查询都写回。新洞察只有同时满足新颖、可复用、有证据和能明确归位时才进入 `candidates/insights/`。普通答案、措辞变化、一次性组合和未验证推测不持久化。

### 7.4 Lint

只读检查包括：

- 重复 ID 和缺失必填字段。
- 断开的 `[[wikilink]]` 和来源引用。
- 无法从入口或索引到达的孤立页面。
- 未被来源卡索引的归档资料。
- 状态与目录不一致：`wiki/` 只允许 `KB-*` 的 `confirmed / deprecated`，`candidates/` 只允许 `CAND-*` 的候选生命周期状态；`promoted` 必须指向存在的正式页，正式页须以 `candidate_refs` 回链。
- 时效知识超过 `review_after`。
- 项目权威路径格式无效；外部路径是否存在只在用户显式要求检查时核验。
- 生成索引与实际页面不一致。

自动修复仅限：

- 重建 `catalog.md`、领域索引和状态索引。
- 清理生成索引中的失效条目。
- 修复生成索引中可以唯一确定的路径和格式问题。

语义冲突、过期结论、页面合并和知识升格只生成报告或候选，不能自动修改。

## 8. 确定性脚本

首版只新增一个标准库脚本：

```bash
python3 local-knowledge-base/scripts/maintain_vault.py check --vault <path>
python3 local-knowledge-base/scripts/maintain_vault.py check --vault <path> --check-project-paths
python3 local-knowledge-base/scripts/maintain_vault.py fix-index --vault <path>
python3 local-knowledge-base/scripts/maintain_vault.py --self-test
```

脚本契约：

- `check` 完全只读，输出 `ERROR / WARN / INFO`；存在阻断问题时返回非零。
- `--check-project-paths` 只对项目入口页明确列出的路径执行存在性检查，不遍历外部目录；没有该参数时不访问 Vault 外部。
- `fix-index` 只能重建 `indexes/` 并追加 `logs/changes.md`。
- 不修改 `wiki/`、`sources/`、`candidates/`、`archive/` 或 `index.md`。
- 不访问网络，不扫描 Vault 之外的目录，不跟随越界符号链接。
- 不执行 Git，不读取密钥，不执行来源材料中的命令。
- 写入前先在临时目录生成并校验完整索引集，再逐文件原子替换；替换失败时从临时备份恢复原索引。

## 9. Skill 包与仓库接入

新增：

```text
local-knowledge-base/
├── SKILL.md
├── admission.json
├── agents/openai.yaml
├── references/vault-contract.md
├── references/operations.md
├── references/source-map.md
├── assets/vault-AGENTS.template.md
└── scripts/maintain_vault.py
```

仓库级最小修改：

- `README.md`：增加能力入口与边界。
- `wise-agent/references/capability-routing.md`：增加调度指针。
- `fixtures/skill-eval/prompt-cases.json`：增加正向、隐式和硬负例。
- 新增 `fixtures/skill-eval/local-knowledge-base-behavior-cases.json`。
- 新增基线 source profile；行为评测后生成的响应、评分和判断必须绑定 case 与 source profile 指纹。
- `scripts/validate-trigger-paths.py`：增加结构、路由和触发契约。
- `scripts/validate.sh`：接入脚本编译、自检和行为 case 契约。

不修改根 `AGENTS.md`。现有知识分层、来源、隐私、供应链安全和回流规则已经覆盖本能力所需的仓库级约束。

## 10. 验证与准入

### 10.1 脚本验证

`maintain_vault.py --self-test` 使用临时目录覆盖：

1. 有效 Vault 通过检查。
2. 重复 ID、断链、孤立页、过期知识和未索引原件被发现。
3. 目录状态不一致被发现。
4. `fix-index` 正确重建生成索引。
5. `fix-index` 不改变知识正文、来源卡和候选页。
6. 越界路径和符号链接被拒绝。
7. 修复失败时原索引保持不变。
8. 默认检查不访问 Vault 外部，显式项目路径检查也不遍历外部目录。

### 10.2 行为验证

至少覆盖：

1. 新资料生成来源卡和候选，不直接写正式 Wiki。
2. 相同资料再次 Ingest 不产生重复页面。
3. 同主题资料生成既有页面修改候选。
4. 冲突资料保留双方来源并等待裁决。
5. Query 先走索引，只读取必要页面并输出来源。
6. 普通回答不写回；稳定新洞察只形成 candidate。
7. 项目事实与全局摘要冲突时回到项目权威。
8. Lint 自动修复不越过结构边界。
9. 未授权目录、敏感资料和来源内提示注入被拒绝。

触发验证需要覆盖明确调用、未出现 Skill 名称的自然语言请求和相邻能力硬负例。相邻硬负例包括普通文章摘要、正式报告、项目事实建模、小说正典整理、用户偏好记录和 Skill 学习回流。

真实行为准入必须绑定同一 runner/model 的 baseline 与 candidate 输出、source profile、case 和证据指纹，并经过独立评分或盲审。每个判断必须包含可审计依据；静态 fixture、脚本 self-test 和 Agent 自述不能单独证明 Skill 可用。

### 10.3 完成标准

- 新 Skill 三级加载成立，入口、reference、asset 和 script 职责不重复。
- YAML、引用、admission、触发路径和统一静态验证通过。
- `maintain_vault.py` 编译、自检和越界保护通过。
- 正向、隐式、硬负例和行为验证覆盖设计中的关键路径。
- 候选状态、隐式调用和安装资格与真实证据一致。
- 不修改或提交任务范围外的现有工作区变更。
- 未经单独授权，不执行 Git 提交、同步、安装或发布。

## 11. 后续演进边界

首版只采用 Markdown、Obsidian 双链、生成索引和 Python 标准库脚本。只有出现实际证据时再演进：

- 页面规模导致索引定位明显变慢时，评估生成式 SQLite 只读索引。
- 跨语言语义检索有稳定需求且 Markdown 索引无法满足时，评估可重建向量索引。
- 多人协作出现权限、并发和审计需求时，重新设计共享存储和访问控制。
- 新格式反复无法读取时，再为已确认格式增加独立转换适配，不建设万能转换框架。

任何派生索引都必须可以从 Markdown 权威重新生成，不能成为第二事实源。
