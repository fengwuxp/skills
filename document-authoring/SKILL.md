---
name: document-authoring
description: Use when 用户要把分散材料或已稳定的领域结论撰写、整理、审校为正式报告、制度、手册、研究说明、总结、DOCX 或 PDF；普通 PRD、系分内容设计与汉字训诂考据不触发。
---

# 专业文档撰写

## 定位

本 Skill 是知止者按需装载的专业文档能力包，把已提供或已核验的材料组织成面向明确读者、可评审、可修订、可交付的正式文档。它负责文档表达与交付质量，不替代产品、工程、法律、合规或领域能力作事实判断。Codex 可按精确 description 隐式加载本 Skill；显式调用只表示优先装载成文能力。若与 `wise-agent` 同时加载，仍由同一 Agent 统一目标和交付，不形成第二人格。

## 核心原则

1. 先确认目标读者、使用场景、文档类型、事实来源、正式载体和验收方，再写正文。
2. 区分事实、推断、待确认和范围外不做；来源不足时停止补写，不用流畅表达掩盖证据缺口。
3. 正式正文只保留当前结论、有效依据、风险和待确认项；讨论过程进入评审记录或任务计划。
4. 内容语义归专项 owner，本文档 Skill 只调整结构、表达、引用、修订和载体。
5. Markdown 默认作为可审查事实源；用户要求 DOCX、PDF、PPTX 或表格时，按环境能力调用对应文档工具并实际渲染检查。
6. 所有正式文档都遵守无背景色、无底纹、只克制加粗的简洁排版边界；完整细则读取 `references/format-and-rendering.md`。

## 场景路由

先读 `references/scenario-routing.md`。以下领域语义不得由本技能越权处理；用户明确要求正式成稿、审校或载体交付时，本技能可在专项 owner 结论稳定后协作：

- PRD、产品方案、产品验收：由 `product-architecture-expert` 主责，本技能只处理结构、表达、引用和载体。
- 系分、ADR、技术方案、代码 Review、生产变更：由 `senior-software-architect` 主责，本技能只处理结构、表达、引用和载体。
- 汉字学、字源、训诂、甲骨文、金文、小篆：交给 `hanzi-philology`，本技能只消费其证据卡。
- 一句话润色、简单翻译或格式微调：直接完成，不加载完整工作流。

## 工作流

1. **建立文档契约**：读取 `references/document-contract.md`，确认读者、目的、范围、来源、输出格式、owner 和验收方式。
2. **选择结构**：读取 `references/writing-and-structure.md`，按报告、制度、手册或研究说明组织正文，不机械套全量模板。
3. **写入证据**：读取 `references/citation-and-traceability.md`，让关键结论能回到材料、链接、版本、记录或领域证据卡。
4. **评审与修订**：读取 `references/review-and-revision.md`，区分评审、改写、合并和最终版收口；未经授权不重写全文。
5. **生成载体**：所有正式文档读取 `references/format-and-rendering.md`；需要 DOCX、PDF、PPTX 或表格时调用对应文档工具，工具不可用时交付 Markdown 并说明限制。
6. **验证准出**：本技能主责的报告、制度、手册和研究说明在正式、完整、提交前或用户要求验证时，运行 `scripts/check_document_deliverable.py --kind <kind> --file <path>`。Markdown、HTML、文本或 DOCX 产物再运行 `scripts/check_document_style.py --file <path>`；PDF、PPTX 和其它载体逐页渲染检查。PRD、系分等领域文档不套用本技能的结构检查器，编辑后重新运行领域 Skill 的交付物检查，再检查实际派生载体。

## 最小交付

```text
文档类型：
目标读者与用途：
事实源：
输出文件：
已完成检查：
待确认项与 owner：
残余风险：
```

## 红线

- 结构检查器不判断事实正确；不把结构检查通过写成专业评审通过或正式批准。
- 不伪造来源、引文、版本、数据、作者、审批或完成状态。
- 不把 PRD、系分、训诂证据卡中的领域结论静默改写成另一种含义。
- 不默认生成多种派生格式；只生成用户需要的载体。
- 不用长模板、装饰性排版或 AI 套话填充信息缺口。

## 参考索引

- `references/scenario-routing.md`：任务入口、专项 Skill 路由和停止条件。
- `references/document-contract.md`：文档类型、输入、输出、owner 和验收契约。
- `references/writing-and-structure.md`：面向读者的结构与行文方法。
- `references/review-and-revision.md`：评审、修订、合并和最终版收口。
- `references/citation-and-traceability.md`：事实、引用、版本和结论追踪。
- `references/format-and-rendering.md`：Markdown、DOCX、PDF、PPTX 和表格载体检查。
