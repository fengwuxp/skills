# SkillX 到 Codex Skill Package 导出规范

本文定义如何把 SkillX 产出的规划技能、功能技能、原子技能转换为本仓库可维护、可验证、可安装的 Codex Skill Package。它是导出契约，不是自动学习授权，也不是要求引入 SkillX 训练流水线。

## 使用时机

- 需要把 SkillX 或类似系统提炼出的技能知识库转换为本仓库技能目录。
- 需要评审自动生成的 Skill 候选包是否符合三级加载、供应链安全、隐私边界和验证要求。
- 需要设计或执行 `SkillX -> Codex Skill Package` adapter 或导出脚本。

## 不适用场景

- 不用于自动读取历史对话、用户私有目录、生产日志、客户数据、内部代码或密钥。
- 不用于绕过本仓库 `AGENTS.md`、本地协作学习授权、供应链安全审查和统一验证。
- 不用于把 SkillX 的外部代码、训练流水线、数据集或未审查脚本直接复制进本仓库。

## 读取后必须产出

- SkillX 输入是否可以安全进入转换流程。
- Planning / Functional / Atomic 三层技能分别映射到哪些 Codex Skill 文件。
- 需要拒绝、脱敏、合并、拆分或人工确认的内容。
- 生成后必须执行的验证命令和同步 dry-run。

## 需要继续读取的 reference

- 仓库级规则读 `AGENTS.md`。
- 新建或重构技能读系统 `skill-creator`。
- 架构师 AI 协作和经验沉淀读 `senior-software-architect/references/ai-assisted-engineering.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 判断 SkillX 输出能否进入转换 | 目标边界、安全门禁、输入契约 | 目录结构细节 |
| 设计或执行导出脚本 | 输入契约、映射规则、生成流程、验证流程、Adapter 第一版范围 | 背景说明 |
| 评审生成的 Skill 包 | 质量门禁、安全门禁、验证流程 | 输入 schema 示例 |
| 只想理解三层映射 | 映射规则 | 生成流程和脚本约束 |

## 目标边界

SkillX 负责发现候选经验，本仓库负责把候选经验治理成运行时资产：

```text
SkillX 候选技能
-> 安全与来源审查
-> 三层映射
-> Codex Skill Package
-> 脚本与 fixture 验证
-> sync dry-run
```

转换目标不是生成一次性提示词，而是生成能长期维护的技能包：

```text
<skill-id>/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
  fixtures/
```

其中 `scripts/` 和 `fixtures/` 只有在确实存在确定性执行或负例验证价值时才创建。

## 输入契约

SkillX 输出进入转换前，应先归一化为候选包，并满足 `schemas/skillx-candidate.schema.json`：

```text
skill_id: 稳定目录名，使用小写字母、数字和连字符
display_name: 人可读名称
description: 触发识别说明，约 100 词以内
source:
  type: skillx | manual | mixed
  repository_or_paper: 来源链接或说明
  generated_at: 生成时间
  reviewer: 人工审查者或待确认
planning_skills:
  - name
    trigger
    plan_steps
    branch_rules
    stop_conditions
functional_skills:
  - name
    task
    inputs
    outputs
    workflow
    references
atomic_skills:
  - name
    tool_or_script
    schema
    constraints
    failure_modes
    negative_cases
safety:
  contains_private_data: true | false | unknown
  contains_external_code: true | false | unknown
  requires_network: true | false | unknown
  requires_user_consent: true | false | unknown
```

任何 `unknown` 都不得直接进入自动生成；必须先人工确认或降级为待确认项。

## 映射规则

### Planning Skills -> 路由与计划

Planning Skills 只能映射到轻量入口和路由，不得把长流程塞进 `SKILL.md`：

- `SKILL.md` frontmatter `description`：只保留触发识别词和核心适用边界。
- `SKILL.md` body：保留角色定位、核心流程、场景路由、何时读取 reference、必要红线。
- `references/*scenario-routing.md` 或 workflow reference：承载阶段顺序、分支条件、停止条件和复杂路由。
- `scripts/validate-trigger-paths.py`：加入关键触发 fixture，避免触发路径漂移。

### Functional Skills -> Reference 方法

Functional Skills 映射为 `references/` 中的工作流、模板、清单和方法论：

- 每个 reference 开头应包含使用时机、不适用场景、读取后必须产出、需要继续读取的 reference。
- 大 reference 应提供按任务读取索引，避免一次性加载全部知识。
- 同一规则只保留一个权威来源，其他层只摘要和链接。
- 领域知识、模板、检查清单和案例进入 reference，不进入 `SKILL.md`。

### Atomic Skills -> 脚本、fixture 与工具约束

Atomic Skills 优先映射为确定性资产：

- 可重复、容易写错、需要解析/生成/校验的能力进入 `scripts/`。
- 工具参数、输入输出 schema、失败模式、负例进入脚本文档、fixture 或验证脚本。
- 不存在工具、无效参数、无法复现的调用模式必须被过滤。
- 只有自然语言即可表达的判断原则不应强行脚本化。

## 安全门禁

进入生成前必须拒绝以下内容：

- 用户历史对话、私人目录、密钥、token、客户数据、内部合同、生产配置、生产日志或不可公开组织信息。
- 未经许可的外部代码、脚本、数据集、模板、图片、Logo 或版权不明资产。
- 默认联网、上传文件、读取密钥、修改 Git 历史、执行不可逆操作或访问生产环境的能力。
- 未经用户明确同意的长期学习记录、团队偏好、业务背景或协作习惯。

安全处理原则：

- 能脱敏则脱敏，不能脱敏则拒绝进入技能包。
- 能人工确认则标记待确认，不能确认则不生成。
- 外部代码必须先完成许可证、供应链安全和执行边界审查。
- 任何长期学习仍必须写入 `~/.skill-learning/` 或 `SKILL_LEARNING_HOME`，不得写入仓库。

## 质量门禁

生成的 Skill Package 至少满足：

- Metadata 能触发：`name` 和 `description` 短、准、覆盖核心场景。
- Skill Body 可执行：`SKILL.md` 不超过仓库建议复杂度，能说明流程、路由、红线和 reference 读取时机。
- Bundled Resources 可发现：`references/` 一层直连，脚本和 fixture 有明确用途。
- 经验已过滤：去除探索、回退、试错、临时偏好、重复技能和未经验证结论。
- 原子约束可验证：关键工具约束、失败模式、负例和生成结果进入脚本或 fixture。
- 来源可追溯：README 或 source map 记录公开来源、提炼边界和不复制外部资产的说明。

## 生成流程

1. **Normalize**：把 SkillX 输出归一化为输入契约，标出 unknown、敏感、外部代码和网络需求。
2. **Filter**：删除不可移植、不可组合、无工具依据、含敏感信息或缺少来源的候选技能。
3. **Merge / Split**：合并重复技能；过大技能拆成规划、功能、原子三类资产。
4. **Package**：生成 `SKILL.md`、`agents/openai.yaml`、必要 reference、必要 script 和 fixture。
5. **Validate**：运行触发、引用、脚本、fixture、同步 dry-run 和空白检查。
6. **Review**：人工审查触发边界、供应链安全、隐私边界、验证证据和残余风险。

## 验证流程

生成后至少执行：

```bash
python3 scripts/validate-trigger-paths.py
./scripts/validate.sh
git diff --check
./sync-skills.sh --dry-run all
```

若新增脚本，还必须说明：

- 输入、输出和写入范围。
- 失败行为和退出码。
- 是否访问网络。
- 是否读取仓库外路径。
- 是否可能删除、覆盖或提交文件。

## Adapter 第一版范围

第一版 adapter 只做离线转换，不做训练、不做自动轨迹采集、不做联网探索。当前仓库入口是 `scripts/skillx_export_adapter.py`，输入契约是 `schemas/skillx-candidate.schema.json`，示例输入是 `fixtures/skillx/sample-candidate.json`：

```bash
python3 scripts/skillx_export_adapter.py --check-input --input fixtures/skillx/sample-candidate.json
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out --dry-run
python3 scripts/skillx_export_adapter.py --validate-output /tmp/skillx-out/skillx-product-reviewer --input fixtures/skillx/sample-candidate.json
python3 scripts/skillx_export_adapter.py --self-test
```

```text
输入：人工审查后的 SkillX JSON
输出：候选 Codex Skill Package 目录
动作：检查输入、生成文件、生成验证 fixture、输出 `REVIEW.md` 人工审查报告和可用性摘要
禁止：读取历史对话、调用生产系统、安装依赖、执行外部代码、自动同步到 Codex
```

第一版成功标准：

- 能生成一个可被 `./scripts/validate.sh` 检查的候选技能目录。
- 能把 Planning / Functional / Atomic 三类经验放到正确层级。
- 能拒绝含敏感数据、未知工具、未知网络访问或外部未审查代码的输入。
- 能用 `--check-input` 在写文件前输出只读输入评估、预计生成文件和可用性摘要。
- 能用 `fixtures/trigger-prompts.md` 对生成 Skill 的正负触发样例做回归检查。
- 能用 `--validate-output` 单独复核已生成候选目录的必要文件、触发样例和输入一致性。
- 能输出清晰的人工待确认项，而不是假装自动判断完毕。
