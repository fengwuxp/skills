
# Skills

本仓库用于维护可安装到 Codex 的 Skills。它不是轻量 prompt 集，而是一套可长期演进的 Agent 运行时资产库。

仓库采用分层治理：`AGENTS.md` 保存每个会话都应知道的默认规则和安全边界；各技能的 `SKILL.md` 保存特定任务的入口、路由和红线；详细知识、模板和方法论放在对应技能的 `references/` 中；确定性生成、验证、同步和安全检查放在 `scripts/` 中；使用者长期学习数据只保存在用户目录 `~/.skill-learning/` 或 `SKILL_LEARNING_HOME`，不进入仓库。

## 5 分钟上手

```bash
git clone https://github.com/fengwuxp/skills.git
cd skills

# 先预览，不写入 ~/.codex/skills
./sync-skills.sh --dry-run all

# 同步单个技能
./sync-skills.sh senior-software-architect

# 同步全部技能
./sync-skills.sh all

# 同步后重启 Codex 或开启新会话，再通过 $ 调用技能
```

仓库目录名可以自定义，不要求必须叫 `skills`。`sync-skills.sh` 会优先把脚本所在目录识别为技能仓库根，并同步同级的技能目录。

如需同步到非默认 Codex Home：

```bash
CODEX_HOME=/path/to/codex-home ./sync-skills.sh --dry-run all
CODEX_HOME=/path/to/codex-home ./sync-skills.sh all
```

## 验证

修改技能、同步脚本或代码生成器后，建议执行统一验证：

```bash
./scripts/validate.sh
```

该脚本会检查：

- `sync-skills.sh` Bash 语法。
- Skill 脚本是否包含需要人工复核的高风险模式。
- `SKILL.md` frontmatter 和 `agents/openai.yaml` YAML。
- `SKILL.md` 中引用的 `references/` 文件是否存在。
- 架构师和产品专家关键触发路径、三级加载、reference 头部和核心门禁是否保持一致。
- `java-service-code-generator` Python 编译。
- DDL、Java 类、Markdown 字段表格三组代码生成 fixture。
- `sync-skills.sh --dry-run all`。
- `git diff --check` 空白问题。

## 同步安全

`sync-skills.sh` 使用 `rsync --delete` 保持安装目录和仓库技能目录一致。正式同步前会备份已有目标技能目录到 `$CODEX_HOME/skills/.backups/`，但仍建议先执行 `--dry-run`，确认 `CODEX_HOME` 和目标技能列表正确。

不要把使用者长期学习数据放在本仓库或安装后的技能目录中；技能同步可能删除安装目录里的额外文件。长期学习数据应保存在用户目录 `~/.skill-learning/`，或由 `SKILL_LEARNING_HOME` 指定的位置。

## SkillX 导出规范

如需把 SkillX 或类似系统生成的规划技能、功能技能、原子技能转换为 Codex Skill Package，先按 [SkillX 到 Codex Skill Package 导出规范](./references/skillx-to-codex-skill-package.md) 做输入契约、安全门禁、三层映射、生成流程和验证流程审查。第一版只允许离线转换人工审查后的 JSON，不自动读取历史轨迹、不采集用户数据、不引入外部训练流水线，也不自动同步到 Codex。

离线候选包必须符合 `schemas/skillx-candidate.schema.json`，可用 `scripts/skillx_export_adapter.py` 生成可评审的 Skill 目录草案。生成结果会包含 `REVIEW.md` 和 `fixtures/trigger-prompts.md`，用于评审可用性、验证命令、待确认项和正负触发样例：

```bash
python3 scripts/skillx_export_adapter.py --check-input --input fixtures/skillx/sample-candidate.json
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out --dry-run
python3 scripts/skillx_export_adapter.py --input fixtures/skillx/sample-candidate.json --output-dir /tmp/skillx-out
python3 scripts/skillx_export_adapter.py --validate-output /tmp/skillx-out/skillx-product-reviewer --input fixtures/skillx/sample-candidate.json
```

## 外部参考来源

- [yizhiyanhua-ai/fireworks-tech-graph](https://github.com/yizhiyanhua-ai/fireworks-tech-graph)：作为图形化 Skill 产品化、风格系统、语义形状/箭头、模板化、fixture 化、SVG 导出和渲染校验思路的公开参考来源。本仓库只吸收通用方法，不默认复制外部脚本、模板、图形资产或安装流程；PNG/PDF/截图等派生格式只在使用者明确提出时处理；引入外部可执行内容前必须按 `AGENTS.md` 做供应链安全审查。
- [Ivy-piger/Ivy-skills](https://github.com/Ivy-piger/Ivy-skills)：作为架构师陌生代码库侦察、Java 架构坏味启发式扫描、生产故障时间线、5-Why 复盘草稿和 Spring Boot 安全检查清单的公开参考来源。本仓库只吸收可复用流程和检查项，不安装或复制 Claude Code 专用 frontmatter、`CLAUDE.md` 流程、外部脚本或服务端运行逻辑；如需复用具体文本、脚本或资产，必须保留来源、确认许可证并执行供应链安全审查。
- [cg0x-skills/cg0x-frame-analysis](https://github.com/cg0x-skills/cg0x-frame-analysis)：作为探索期反路径锁定、多框架分析、假设/盲区/失败条件自检的公开参考来源。本仓库只吸收通用方法到产品专家和架构师 reference，不引入 `alwaysApply`、`/on` `/off` 开关、单文件长 Skill 或默认不收敛的交付方式；复杂问题先展开问题地图，正式交付仍必须回到可评审、可验证、可验收的产物。
- [zjunlp/SkillX](https://github.com/zjunlp/SkillX) 与论文 [SkillX: Automatically Constructing Skill Knowledge Bases for Agents](https://arxiv.org/abs/2604.04804)：作为从 Agent 执行轨迹提炼规划技能、功能技能、原子技能，迭代精炼、合并过滤和探索扩展技能知识库的公开参考来源。本仓库只吸收“经验分层、过滤噪音、合并重复、工具约束和失败模式进入确定性验证”的方法，不引入自动读取历史轨迹、自动学习用户数据、外部训练流水线或未审查代码；任何长期学习仍必须遵守 `AGENTS.md` 的本地协作学习授权和隐私边界。

## 本地协作学习机制

本仓库只维护技能定义和协议，不保存使用者个人学习数据。本地协作学习机制用于提升使用者与技能的配合度，并在合适场景下协助使用者改进判断、表达和设计质量。该机制是可选项，默认关闭；只有用户明确同意启用后，才会在用户目录下创建 `~/.skill-learning/` 并保存长期使用习惯、团队决策偏好、业务背景和技能演进记录。如需自定义位置，可以设置 `SKILL_LEARNING_HOME`。

首次问询不是第一次使用技能时必问，而是先通过“学习时机判定算法”判断当前任务是否已经出现稳定偏好、团队约规、业务背景、反复决策方式等长期沉淀价值，并且不会打断关键任务时才询问。用户在单个技能场景下同意时，默认只开启当前技能；只有明确要求“所有技能”或“全局开启”时，才对所有技能生效。

学习时机判定采用轻量算法：先识别候选观察，再从稳定性、复用价值、证据强度、可执行性、安全性五个维度评分，之后经过风险门禁决定不学习、静默进入 `Pending Observations`、显示确认后记录，或只做纠偏讨论。涉及隐私、金融/合规/安全、生产上线、权限边界、强约束偏好或用户可能错误判断时，不得静默学习。

推荐结构：

```text
~/.skill-learning/
  consent.md
  global.md          # 可选：仅全局授权或明确跨技能约定时创建
  skills/
    <skill-id>.md
  archive/
```

- `consent.md` 保存本地协作学习机制的启用标记。
- `global.md` 保存跨技能通用约定，仅在全局授权或明确跨技能约定时创建。
- `skills/<skill-id>.md` 保存单个技能的长期学习记录。
- 技能目录只保存技能定义和 references，避免同步或重构时覆盖学习数据。
- 用户明确拒绝启用时，不创建学习目录或文件，后续也不主动提示，除非用户主动提及。
- 用户同意启用但未说明范围时，默认只开启当前技能。
- 启用后默认采用混合模式：低风险常规观察可静默保存到 `Pending Observations`；可能影响长期行为、跨技能复用、业务/合规/隐私边界或强约束偏好的记录需要显示确认。
- 启用后也不是所有观察都记录；必须先经过学习时机判定，并且去重、可追溯、可撤销。
- 用户可以随时切换为静默模式、显示确认模式或混合模式。
- 启用后默认采用协作型学习模型；用户可以切换为记录型、协作型或审查型。
- 如果发现用户判断或设计可能存在错误、逻辑漏洞或红线风险，需要显示提示用户，并讨论确认改进方式。
- 协作时会按当前话题动态判断用户专业程度，用于校准解释深度和纠偏强度；该判断不得固化为用户全局标签。
- 提交、上传或共享到远程前需要用户确认。
- 未经用户确认，不应把 `Pending Observations` 提升为 `Confirmed Agreements`。

详细约定见 [AGENTS.md](./AGENTS.md)。

## AI Skills

- [senior-software-architect](./senior-software-architect) 资深架构师（Java/Spring 核心专长）
- [product-architecture-expert](./product-architecture-expert) 产品架构专家（支付与资金系统为重点垂直能力）
- [java-service-code-generator](./java-service-code-generator) Java Service 代码生成
