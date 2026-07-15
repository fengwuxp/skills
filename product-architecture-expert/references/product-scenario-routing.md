# 产品架构场景识别与方案路由

本文用于在回答前快速判断产品架构问题属于哪类场景、应读取哪些参考、输出什么产物、优先检查哪些红线。它是知识路由，不是生产系统里的功能路由、支付通道路由或资金清结算路由。

## 使用时机

- 用户要求写作、生成、完善、补全或改写 PRD、产品需求文档、产品方案、业务流程、状态机、规则矩阵、运营后台或验收标准。
- 用户提供原型、HTML、页面截图、页面说明或交互稿，要求反推、补写或改写 PRD。
- 用户提供客户访谈、工单、竞品动态、行业/政策资料、标杆实践、Markdown 笔记或知识库资料，要求做产品洞察、需求洞察、机会挖掘或机会雷达。
- 用户提到 `pm-skills`、产品判断成流程、产品动作链、产品判断动作链、路线图取舍、发布复盘或增长实验，需要把分散材料串成证据、判断、取舍、不做项、下一产物和 owner。
- 用户给出洞察、机会清单、需求池、老板/销售/客户诉求或路线图候选，要求做 Backlog 决策、需求优先级、User Story、AC 或研发可执行条目。
- 用户要求业务架构规划、业务 IT 对齐、业务能力地图、战略落项目、项目组合治理、投资取舍、重复建设识别、能力-项目-系统映射或按业务域 / 模块规划知识库回流。
- 用户要求产品头脑风暴、问题探索、假设挑战、HMW、第一性原理拆解、OODA、逆向头脑风暴或在写 PRD 前先把想法想透。
- 用户提供老板/销售/客户/运营的模糊诉求、非标问题、跨团队问题或“先想一个方案”，需要产品专家先判断真实问题和解决方案责任。
- 用户要求判断产品阶段、PMF 前后团队缺什么贡献方式，或讨论产品团队不按岗位分工、原型验证、真实交付、复杂度清扫、增长放大和可靠维护。
- 用户提到概念膨胀、新旧概念并存、需求只加不减、事实源分裂、旧规则退役、旧入口下线或产品概念生命周期。
- 用户要求从 AI Native 产品流程、Product Builder、业务 dogfooding、MVP/原型进入工程 harden 或 PRD 可执行上下文中提炼产品侧交接材料。
- 用户要求多个 AI、PM / Reviewer、产品大师、MAGI、多视角、合议式评审 PRD / 产品方案 / AI 生成方案 / 原型候选，或希望按阶段确认前置依赖、方案概要、交互和 PRD。
- 用户要求需求评审、PRD 评审会前扫描、需求评审 Skill、AI 先扫 PRD、完整性 / 一致性 / 可测试性 / 二义性检查。
- 不确定应进入通用产品架构、PRD 模板、支付资金专项还是能力评估。
- 需要先澄清用户、主体、目标、边界、对象、规则、数据和风险。

## 不适用场景

- 用户只问工程实现、代码 Review 或测试设计；此时优先使用 `资深架构师`。
- 用户只给错误截图、日志截图或测试失败截图，并要求定位根因、修复代码或补回归测试；此时优先使用 `资深架构师`，除非用户明确要求反推产品需求或页面流程。
- 已明确进入支付资金专项时，继续读取 `payment-scenario-routing.md`，但仍保留本文件的产品语义判断。

## 读取后必须产出

- 场景类型、业务复杂度、关键对象、风险等级和目标产物判断。
- 最小 reference 集合，以及待确认项。
- 输出形态：PRD、产品方案、流程、规则矩阵、指标口径或支付资金方案。

## 需要继续读取的 reference

- PRD/产品文档读 `product-prd-template.md` 和 `product-design-and-prd.md`；正式评审或提交前自检加读 `product-prd-quality-gates.md`；支付资金 PRD 加读 `product-prd-financial-appendix.md`；运营、通知、数据、发布加读 `product-prd-operations-and-data.md`。
- AI Native 产品上下文、Product Builder、业务 dogfooding、MVP/原型进入工程 harden 和产品侧交接读 `ai-native-product-context.md`；端到端研发流程、GSD/CAD 准入、Harness/Agent 编排由 `delivery-collab` 处理。
- 复杂 PRD、AI 生成方案、原型候选、多方争议、PM / Reviewer / 产品大师 / MAGI 多视角评审读 `product-deliberation-workflow.md`；它只提供产品合议评审流程，不替代 PRD 主模板、Backlog 决策或 AI Native 研发编排。
- 通用产品架构读 `product-architecture-methodology.md`。
- 业务架构规划、业务能力地图、战略到项目组合、项目组合治理、能力-项目-系统映射和知识库回流读 `business-architecture-planning.md`；复杂图形化表达加读 `diagram-output.md`。
- `pm-skills`、产品判断成流程、产品动作链、产品判断动作链、路线图取舍、发布复盘或增长实验场景，读 `product-judgment-action-chain.md`；它只串产品判断动作和交接路由，不安装外部 Skill。
- 产品方案需要交给架构师继续做系统设计或业务驱动架构交接时，读 `product-architecture-methodology.md` 的“与技术架构的交接”和“业务驱动验证口径”，必要时加读 `product-prd-quality-gates.md`。
- 产品洞察、资料资产化、客户/竞品/标杆情报分拣、证据推理链或机会雷达场景，读 `product-insight-analyst.md`；机会需要排序或转研发候选时，再读 `po-backlog-manager.md`。
- 机会清单、需求池、Backlog 决策、优先级、路线图候选、User Story 或 AC 场景，读 `po-backlog-manager.md`，再按目标产物读取 `product-design-and-prd.md`。
- 产品头脑风暴、问题探索、方案发散或假设挑战，读 `product-architecture-methodology.md` 的“2.0E 产品头脑风暴纪律”；产出只作为问题地图、机会雷达、Backlog 或 PRD 前置材料，不直接写成研发任务。
- 非标产品问题、老板/销售/客户只给方向、跨团队诉求或产品岗容易退化成传话筒时，读 `product-architecture-methodology.md` 的“1.4 非标问题与解决方案责任”。
- 产品阶段、PMF 前后团队能力配比、产品团队不按岗位分工或五类贡献方式诊断时，读 `product-architecture-methodology.md` 的“2.0F 产品阶段与贡献方式诊断”。
- 概念膨胀、新旧概念并存、需求只加不减、事实源分裂、旧规则退役或旧入口下线时，读 `product-concept-lifecycle.md`。
- 图形化产品交付读 `diagram-output.md`。
- 支付资金场景读 `payment-scenario-routing.md` 和 `regulatory-baseline.md`；外卡收单、Mastercard、卡组织清算、Clearing Core、商户到账或收单风控同样先进入支付资金专项。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 产品场景初判 | 使用方式、产品语义门禁、快速路由表 | 输出路由细节 |
| PRD/产品方案 | 快速路由表、输出路由，并继续读 PRD reference | 支付资金专项，除非命中资金场景 |
| 原型/HTML/页面截图/交互稿反推 PRD | 使用方式、产品语义门禁、快速路由表，并继续读 PRD reference | 只描述页面控件 |
| 复杂 PRD / AI 生成方案 / 多视角合议评审 | 快速路由表、产品语义门禁，并继续读 `product-deliberation-workflow.md`、`product-prd-quality-gates.md` | 不新增独立产品大师 Skill，不照搬外部多 Agent 工具 |
| PRD 文档质量治理 / 文档过厚过薄 / 版本评审同步 | 快速路由表、产品语义门禁，并继续读 `product-design-and-prd.md` 与 `product-prd-quality-gates.md` | 支付资金专项，除非命中资金场景 |
| PRD / 需求评审会前 AI 预扫描 | 快速路由表、产品语义门禁，并继续读 `product-prd-quality-gates.md` 的“AI 预扫描四维度” | 不把 AI 扫描结果当已确认缺陷，不替代正式评审 |
| 产品洞察 / 资料分析 / 机会雷达 | 快速路由表、产品语义门禁，并继续读 `product-insight-analyst.md` | 不把资料摘要当机会决策 |
| 产品判断动作链 / pm-skills 工作流参考 | 快速路由表、产品语义门禁，并继续读 `product-judgment-action-chain.md`，按缺口再读 `product-insight-analyst.md`、`po-backlog-manager.md` 或 PRD reference | 不安装或照搬外部 `pm-skills`，不把路线图愿望清单当产品判断 |
| 产品头脑风暴 / 问题探索 / 假设挑战 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“2.0E 产品头脑风暴纪律” | 不把发散想法直接当 PRD、Backlog 或研发任务 |
| 非标产品问题 / 老板客户只给方向 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“1.4 非标问题与解决方案责任” | 不做传话筒，不把诉求原样丢给研发 |
| 产品阶段 / 团队贡献方式诊断 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“2.0F 产品阶段与贡献方式诊断” | 不把贡献方式等同岗位、组织架构或绩效标准 |
| 概念膨胀 / 新旧概念并存 / 只加不减 / 概念生命周期与退役 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“1.3 概念定名与需求止损”和 `product-concept-lifecycle.md` | 不只加新名词，不把概念退役写成工程删除授权 |
| Backlog 决策 / 机会清单优先级 / User Story/AC | 快速路由表、产品语义门禁，并继续读 `po-backlog-manager.md` 和 `product-design-and-prd.md` | 不把洞察清单直接当研发任务 |
| 产品经理方法论 / 产品专家基础能力补齐 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“2B. 产品经理基础方法校准”和 `skill-tree.md` | 不把基础岗位清单替代复杂产品架构 |
| AI 产品工作成熟度 / AI-shaped readiness / AI 工作流改造 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“2A. AI-shaped 产品工作成熟度” | 不安装外部 advisor，不把外部术语当团队结论 |
| AI Native Product Builder / 业务 dogfooding / MVP harden / 放下 PRD | 快速路由表、产品语义门禁，并继续读 `ai-native-product-context.md` | 不把 AI Demo 直接当需求，不把产品上下文包当 Execution Grant |
| 业务流程/状态/规则 | 产品语义门禁、快速路由表、通用场景识别问题 | PRD 模板正文 |
| 业务架构规划 / 战略落项目 / 项目组合治理 | 快速路由表、产品语义门禁，并继续读 `business-architecture-planning.md`；复杂图形化表达加读 `diagram-output.md` | 不画全公司大图，不把部门 / 系统 / 页面当业务能力 |
| 业务驱动架构交接 / 产品方案交给架构师 | 产品语义门禁、快速路由表、`product-architecture-methodology.md` 的 5/5.1 | 页面控件或技术模块清单 |
| 图形化交付 | 快速路由表、输出路由，并读 `diagram-output.md` | 支付规则细节 |
| 支付资金场景 | 使用方式、产品语义门禁、快速路由表，并读 `payment-scenario-routing.md` | 普通产品方法扩写 |
| 评审/触发验证 | 产品语义门禁、外部规则时效性、产品交付物脚本门禁、输出路由 | 学习路径 |

## 使用方式

先按以下顺序识别场景，再选择最小参考集：

1. **任务目标**：写作、生成、完善、补全、评审或从原型/HTML/页面截图/交互稿反推 PRD/产品需求文档/需求说明书/产品方案，产品定位、业务流程、状态机、规则矩阵、运营后台、数据指标、评审清单、支付与资金专项。
2. **业务复杂度**：单角色单流程、多角色协作、多状态流转、多规则版本、多系统协同、多法域/多主体/多资金方。
3. **关键对象**：用户、客户、商户、订单、账户、合同、权益、任务、审批、工单、报表、资金、凭证。
4. **风险等级**：资金、合规、隐私、安全、权限、生产运营、跨团队契约、外部机构规则。
5. **目标产物**：产品架构方案、PRD、能力地图、业务流程图、状态机、规则矩阵、指标口径、运营后台方案、验收标准。

如果涉及支付、账户、账本、清结算、对账、商户结算、分账分润、通道路由、银行卡/卡组织、外卡收单、Mastercard、Clearing Core、商户到账、ACH/银行转账、VCC、风控欺诈、争议拒付、跨境支付、稳定币/Web3、AI 代理支付或业财一体化，再读取 `payment-scenario-routing.md`。

## 产品语义门禁

输出确定性产品方案前，必须先判断以下语义是否已经清楚；不清楚时只能写成待确认、假设或澄清问题，不得包装成已确认结论。

| 门禁 | 必须确认 | 不清楚时的处理 |
| --- | --- | --- |
| 术语 | 用户说法、业务术语、运营口径、系统命名和已有文档是否一致。 | 列出术语对照和冲突点，要求业务/产品确认。 |
| 主体 | 谁是用户、客户、商户、平台、运营方、外部机构、风险承担方和验收方。 | 拆分主体与责任，不把“用户”泛化成所有参与者。 |
| 目标 | 业务目标、用户目标、运营目标、数据目标和非目标是否可验证。 | 用目标/非目标表固定边界，不能只写愿景。 |
| 对象 | 核心概念、业务抽象、核心对象、字段口径、生命周期、状态和不变量是否能解释流程。 | 先补概念定义、抽象边界、对象模型和状态，不直接堆功能点。 |
| 流程 | 主流程、逆向流程、异常流程、人工流程、通知和 SLA 是否闭环。 | 输出待补流程分支和人工兜底，不只给成功路径。 |
| 规则 | 权限、审批、额度、计费、风控、通知、数据留存是否有版本和优先级。 | 用规则矩阵表达，标注规则 owner 和待确认项。 |
| 数据 | 指标、报表、埋点、审计、追溯、导出和数据源是否有口径归属。 | 标注口径负责人、数据源和校验方式。 |
| 风险 | 是否涉及资金、合规、隐私、安全、生产运营、外部规则或跨团队契约。 | 进入专项 reference，并列出专业确认方。 |
| 验收 | 正常、边界、异常、运营、数据和风险路径是否可测试。 | 补验收矩阵；无法验收的需求不写成可开发完成。 |

外部规则、政策、通道协议、卡组织/ACH/银行规则、云产品限制、第三方平台 API 或 SDK 版本会随时间变化。产品方案引用这类内容时，必须记录来源、版本或发布日期、适用范围、核验日期和确认方；无法确认最新版本时，只能列为待确认项。涉及真实资金、金融数据或支付网络时，继续读取 `regulatory-baseline.md`。

正式、完整、可评审、提交前或触发验证场景中，涉及外部规则时必须运行 `scripts/check_external_rules.py` 检查本地文本或显式传入的本地文件。该脚本只做完整性检查，不联网、不写文件、不替代规则真实性、适用性或可上线性的专业确认；无法运行时必须说明原因、人工检查结果和残余风险。

正式、完整、可评审、提交前、CR 或触发验证场景中，PRD、产品架构方案、图形 brief 或产品合议评审报告必须运行 `scripts/check_product_deliverable.py --kind prd`、`--kind product-architecture`、`--kind diagram-brief` 或 `--kind product-review`。该脚本只做本地文本完整性检查，不联网、不写文件、不替代产品判断、业务确认、合规审查或图形质量评审；无法运行时必须说明原因、人工检查结果和残余风险。

## 快速路由表

| 场景信号 | 优先读取 | 典型输出 |
| --- | --- | --- |
| 产品方向、业务目标、产品边界不清 | `product-architecture-methodology.md` | 目标、用户、范围、非目标、成功指标、关键风险 |
| 业务架构规划、业务 IT 对齐、战略落项目、业务能力地图、项目组合治理、投资取舍、重复建设识别、能力-项目-系统映射 | `business-architecture-planning.md`, `product-architecture-methodology.md`；复杂图形化表达加读 `diagram-output.md` | 业务架构准入卡、能力地图、价值流、核心对象与规则、能力-项目-系统映射、差距 / 依赖 / 优先级、项目组合 / 路线图和按业务域或模块分区的知识库回流计划 |
| 写 PRD、生成 PRD、完善 PRD、补全 PRD、改写 PRD、从原型/HTML/页面截图/交互稿反推 PRD、产品方案、产品需求文档、需求说明书、需求文档模板、PRD 模板 | `product-prd-template.md`, `product-design-and-prd.md`, `product-architecture-methodology.md`；支付资金加读 `product-prd-financial-appendix.md`，运营数据发布加读 `product-prd-operations-and-data.md`，提交前自检加读 `product-prd-quality-gates.md` | 可复制 PRD、产品方案、用户故事、验收标准、待确认项 |
| PRD 文档过厚、过薄、未更新、未评审、版本状态不清或过程稿混入正文 | `product-design-and-prd.md`, `product-prd-quality-gates.md` | 文档目标/受众、裁剪建议、必改项、版本状态/过程记录链接和最终正文准出机制 |
| 需求评审、PRD 评审会前扫描、需求评审 Skill、完整性/一致性/可测试性/二义性检查 | `product-prd-quality-gates.md`, `product-design-and-prd.md` | AI 预扫描疑似问题清单：锚点、维度、影响、建议追问、建议改法、决策状态、owner、验证方式；只做评审前广度扫描，不替代正式评审 |
| 多 AI、PM/Reviewer、产品大师、MAGI、合议式评审复杂 PRD、AI 生成方案、HTML Demo 或产品方案 | `product-deliberation-workflow.md`, `product-prd-quality-gates.md`，需要正文时再读 `product-prd-template.md` 和 `product-design-and-prd.md` | 合议评审结论：触发原因、阶段门、共识、分歧、必改、建议、待确认、owner、验证方式和下一步去向 |
| 产品经理方法论、产品专家能力补齐、产品经理知识体系、基础工作法校准 | `product-architecture-methodology.md`, `skill-tree.md` | 能力校准：文档分型、流程表达、原型注释、产品架构图、用户研究、需求管理、数据分析、技术/项目协作、行业商业分析、知识库沉淀；并提升到复杂业务对象、规则、验收和交接能力 |
| AI 产品工作成熟度、AI-shaped readiness、产品团队 AI 工作流改造、AI 是否形成产品优势 | `product-architecture-methodology.md` | AI 产品工作成熟度评审：业务优势、流程变化、上下文结构化、可追溯任务、人工责任、验证周期/决策质量/返工率指标；不安装外部 advisor，不照搬外部话术 |
| pm-skills、产品判断成流程、产品动作链、路线图取舍、发布复盘、增长实验 | `product-judgment-action-chain.md`，按材料类型再读 `product-insight-analyst.md`、`po-backlog-manager.md`、PRD reference 或 `ai-native-product-context.md` | 产品判断动作链卡：已知事实 / 证据、合理推断、待确认、判断动作、取舍结论、不做项、下一产物、owner、验收 / 停止条件和交接路由；不安装外部 Skill |
| 产品洞察、需求洞察、资料资产化、客户/竞品/标杆情报、机会雷达、证据推理链 | `product-insight-analyst.md`, `product-architecture-methodology.md` | 产品洞察报告：资料资产表、三类情报分拣、机会雷达、证据与推理链、置信度、待验证和建议去向；机会需要排序时再读 `po-backlog-manager.md` |
| 产品头脑风暴、问题探索、方案发散、假设挑战、HMW、第一性原理、OODA、逆向头脑风暴 | `product-architecture-methodology.md` | 头脑风暴结论：探索模式、核心问题、目标用户、当前替代方式、关键假设、发散选项、删除/少做选项、反模式、下一步验证动作和进入问题地图/机会雷达/Backlog/PRD 的结论 |
| 非标产品问题、老板/销售/客户/运营只给方向、跨团队诉求、需要产品专家判断解决方案 | `product-architecture-methodology.md` | 非标产品问题卡：真实问题、影响面、失败成本、现有替代方式、解决方案假设、验收种子、验证动作和进入 PRD/Backlog/AI Native 的结论 |
| 产品阶段、PMF 前后、产品团队不按岗位分工、原型验证、真实交付、复杂度清扫、增长放大、可靠维护 | `product-architecture-methodology.md` | 产品阶段与贡献方式诊断卡：阶段证据、主要缺口、需要 / 暂缓的贡献方式、下一产物、owner 和验收 / 停止条件 |
| 概念膨胀、新旧规则并存、需求只加不减、事实源分裂、旧入口下线或概念生命周期 | `product-concept-lifecycle.md` | Concept Lifecycle Card：核心概念、事实源、新增/替代关系、净增概念数、旧概念关系、进入条件、收敛/合并/废弃规则、迁移路径、用户/运营影响面、验收种子、下线 owner、复审日期、退役条件和待确认项 |
| 洞察太多、机会清单、需求池、路线图候选、Backlog 决策、优先级、P0/P1/P2、User Story、AC | `po-backlog-manager.md`, `product-design-and-prd.md` | Backlog 决策包：BV/EE、业务/用户/工程三桌校验、P0/P1/P2、拒绝理由、User Story、AC、技术现实主义风险和待确认项 |
| AI Native Product Builder、业务 dogfooding、MVP/原型 harden、放下 PRD、PRD 可执行上下文、交给 AI Native 编排/架构师 | `ai-native-product-context.md`, `product-architecture-methodology.md`；端到端流程和 GSD/CAD 准入交给 `delivery-collab`；正式 PRD 再读 PRD reference | AI Native 产品上下文包、Hardened Candidate 门禁、MVP 证据、对象规则、验收种子、风险确认和产品侧交接条件；不把可运行等同于可上线 |
| 产品方案要交给架构师继续系统设计、业务驱动架构交接、产品语义到工程验证、验收种子到 TDD 交接 | `product-architecture-methodology.md`, `product-design-and-prd.md`, `product-prd-quality-gates.md` | 业务驱动架构交接包：目标/非目标/成功指标、参与方/owner、核心用例、对象状态、规则矩阵、验收样例、质量属性种子、待确认项；必要时输出验收种子交接矩阵 |
| 能力地图、模块关系、产品架构 | `product-architecture-methodology.md` | 能力地图、模块边界、前后台能力、交付拆分 |
| 画图、流程图、状态机、关系图、产品架构图、资金流图、运营后台结构图、可视化产物 | `diagram-output.md`，按场景再读 `product-architecture-methodology.md`、`product-design-and-prd.md` 或支付资金专项 reference | 默认生成 SVG，报告用途、假设、验证和待确认项；Mermaid/Markdown 草图、PNG/PDF/截图等其他格式需用户明确提出 |
| 复杂业务流程、跨角色协作 | `product-architecture-methodology.md`, `product-design-and-prd.md` | 主流程、逆向流程、异常流程、人工流程、SLA |
| 状态机、生命周期、对象建模 | `product-architecture-methodology.md` | 对象模型、状态机、状态迁移、事件和不变量 |
| 规则体系、额度、计费、审批、风控 | `product-architecture-methodology.md`, `product-design-and-prd.md` | 规则矩阵、优先级、版本、灰度、回滚和验收样例 |
| 运营后台、人工处理、审批复核 | `product-design-and-prd.md` | 后台功能、权限、审批、复核、日志、导出、告警 |
| 指标、报表、数据产品、经营分析 | `product-architecture-methodology.md`, `product-design-and-prd.md` | 指标口径、事件埋点、报表模型、数据验收 |
| 支付、资金、账本、清结算、对账、VCC、ACH、银行卡/卡组织、外卡收单、Mastercard、Clearing Core、商户到账、争议 | `payment-scenario-routing.md`, `regulatory-baseline.md` | 支付与资金产品架构、账户/账务、资金流、金融红线 |
| 用户要求学习路径或能力评估 | `skill-tree.md` | 能力树、分级、短板、学习路径 |

## 通用场景识别问题

用户描述不完整时，先补齐以下关键假设，不要急着给确定方案：

- 语义一致：用户说法、业务术语、既有 PRD/系分/OpenSpec、代码命名和运营口径是否一致。
- 语义追问：当用户目标、对象、流程或规则含混时，先用少量高价值问题把假设暴露出来；不要用工程代理式执行计划替代产品语义澄清。
- 用户和主体：谁使用、谁付费、谁运营、谁承担风险、谁验收。
- 业务目标：增长、效率、风控、合规、降本、体验、数据化、商业化中的哪一个优先。
- 范围边界：本期做什么、不做什么、依赖哪些系统或团队。
- 核心对象：主要业务对象是什么，生命周期和状态是否清楚。
- 核心概念与业务抽象：哪些词会被业务、运营、系统或研发以不同含义使用；哪些能力、规则或关系需要抽象，哪些内容本期不抽象。
- 业务流程：主流程、逆向流程、异常流程、人工处理是否都需要覆盖。
- 规则体系：计费、额度、权限、审批、通知、风控、数据留存是否有版本和例外。
- 数据验收：指标、报表、埋点、审计、追溯和口径归属是否明确。
- 风险边界：是否涉及资金、合规、隐私、安全、生产运营或外部规则。

设计进入工程前，必须把稳定术语、核心对象、状态、规则和验收口径落到现有权威文档体系中，例如 PRD、产品设计、系分设计、OpenSpec 或 Harness Plan；共享语言服务于产品对象、规则和验收，不是额外文档本身。不要为此额外创建分散的 `CONTEXT.md` 或零散 ADR，除非项目本地规范明确要求。

## 输出路由

- **用户要产品架构方案**：输出背景、目标、范围、用户、角色、能力地图、对象模型、流程、状态机、规则、权限、数据、运营、风险和验收。
- **用户要业务架构规划**：读取 `business-architecture-planning.md`，先判断战略意图、真实问题和决策场景，再输出业务架构准入卡、业务能力地图、价值流、核心对象与规则、能力-项目-系统映射、差距 / 依赖 / 优先级、项目组合 / 路线图、Product Context Card 和按业务域或模块分区的知识库回流计划；若需要图形化表达，继续读 `diagram-output.md`，正式图形化交付默认只生成 SVG；不把业务架构降级为组织架构图、系统清单、图形美观或 Execution Grant。
- **用户要 AI Native 产品流程、Product Builder、业务 dogfooding、MVP harden 或 PRD 可执行上下文**：读取 `ai-native-product-context.md`，先判断输入是意图、问题地图、可运行 MVP、产品候选、Hardened Candidate 还是噪声，再输出产品上下文包、验收种子、风险确认和交给 AI Native 编排/架构师的产品侧条件；若用户要求端到端流程、Harness/GSD/CAD 准入或 AI 工具协作，转 `delivery-collab`。
- **用户要交给架构师继续设计或业务驱动架构交接**：输出产品侧交接包，覆盖目标/非目标/成功指标、参与方与 owner、核心行为、对象状态、规则矩阵、验收样例、质量属性种子、待确认项和专业确认方。
- **用户要补齐产品经理方法论或产品专家基础能力**：读取 `product-architecture-methodology.md` 的“2B. 产品经理基础方法校准”和 `skill-tree.md`，把基础产品经理知识体系翻译为文档分型、流程表达、原型注释、产品架构图、用户研究、需求管理、数据分析、技术/项目协作、行业商业分析和知识库沉淀，并说明哪些能力已覆盖、哪些能力需要提升到复杂业务对象、规则、验收和交接。
- **用户要评估 AI 产品工作成熟度或 AI-shaped readiness**：读取 `product-architecture-methodology.md` 的“2A. AI-shaped 产品工作成熟度”，把外部 advisor 术语翻译成业务优势、流程变化、上下文结构化、任务可追溯、人工责任和验证指标；默认只借鉴方法，不安装或调用外部 Skill。
- **用户要参考 pm-skills、把产品判断成流程、串联访谈 / 竞品 / 路线图 / PRD / 发布复盘 / 增长实验**：读取 `product-judgment-action-chain.md`，输出产品判断动作链卡，覆盖已知事实 / 证据、合理推断、待确认、范围外不做、判断动作、取舍结论、不做项 / 延后项、下一产物、owner、验收 / 停止条件和交接路由；按缺口再转产品洞察、Backlog、PRD、合议评审或 AI Native 前置门禁；不安装、复制或照搬外部 `pm-skills`。
- **用户要基于资料、访谈、竞品、行业/政策或知识库做产品洞察、需求洞察或机会雷达**：读取 `product-insight-analyst.md`，先做资料资产化和客户/竞品/标杆情报分拣，再输出机会雷达、证据与推理链、置信度、待验证和建议去向；没有材料的类别明确留白，不用模型记忆补编。
- **用户要产品头脑风暴、问题探索或假设挑战**：读取 `product-architecture-methodology.md` 的“2.0E 产品头脑风暴纪律”，先判断是问题探索、方案发散还是假设挑战，再输出核心问题、目标用户、当前替代方式、关键假设、发散选项、删除/少做选项、反模式和下一步验证动作；需要落地时再转问题地图、机会雷达、Backlog 或 PRD，不直接变研发任务。
- **用户要处理非标产品问题、老板/销售/客户/运营只给方向或跨团队诉求**：读取 `product-architecture-methodology.md` 的“1.4 非标问题与解决方案责任”，先输出真实问题、影响面、失败成本、现有替代方式、解决方案假设、验收种子和验证动作；产品专家必须提供可评审解决方案，不把原始诉求直接转发给研发。
- **用户要判断产品阶段或团队贡献方式**：读取 `product-architecture-methodology.md` 的“2.0F 产品阶段与贡献方式诊断”，先判断当前产品处于 0-1、PMF 迹象期还是强 PMF 阶段，再输出需要的原型验证、真实交付、复杂度清扫、增长放大或可靠维护贡献方式；不得写成固定岗位、组织调整、招聘标准或绩效结论。
- **用户要治理概念膨胀、新旧概念并存、需求只加不减或旧规则退役**：读取 `product-architecture-methodology.md` 的“1.3 概念定名与需求止损”和 `product-concept-lifecycle.md`，输出 Concept Lifecycle Card，说明事实源、旧概念关系、收敛/合并/废弃规则、迁移路径、用户/运营/UED 影响、验收种子、下线 owner 和待确认项；产品专家不能只加新名词，也不能把概念退役写成工程删除授权。
- **用户要消化洞察、机会清单或需求池，做 Backlog 决策、优先级、User Story 或 AC**：读取 `po-backlog-manager.md`，先做输入归一化、BV/EE 和业务/用户/工程三桌校验，再输出 P0/P1/P2、拒绝/延后理由、User Story、AC、技术现实主义风险、owner 和待确认项；不要把洞察清单直接改写成研发任务。
- **用户要图形化产物**：读取 `diagram-output.md`，先判断图形目标和图形类型；正式图形化交付默认只生成 SVG；Mermaid/Markdown 草图、PNG/PDF/截图等其他格式只在用户明确提出时生成，并报告验证结论。
- **用户要写作、生成、完善、补全或改写 PRD / 产品需求文档 / 需求说明书 / 模板**：优先读取 `product-prd-template.md`，输出可复制 PRD，覆盖问题背景、用户故事、功能范围、核心概念、业务抽象、业务规则、页面/交互说明、异常处理、埋点报表、权限、非功能和验收标准；提交前自检读取 `product-prd-quality-gates.md`；支付资金 PRD 读取 `product-prd-financial-appendix.md`；运营、通知、数据、发布读取 `product-prd-operations-and-data.md`；信息不足时保留“待确认”，不要只给提纲。用户给原型、HTML、页面截图、交互稿或页面说明时，先反推角色、对象、流程、规则、状态和验收，再生成 PRD；不要只描述页面控件。
- **用户只要求需求评审、PRD 评审会前扫描或需求评审 Skill 化**：读取 `product-prd-quality-gates.md` 的“AI 预扫描四维度”，按完整性、一致性、可测试性、二义性输出疑似问题、章节锚点、影响、建议追问、建议改法、owner 和验证方式；只做评审前广度扫描和提问准备，不把 AI 结论当成已确认缺陷，也不替代正式评审，不默认重写全文。
- **用户要多视角、多个 AI、PM/Reviewer、产品大师、MAGI 或合议式评审**：读取 `product-deliberation-workflow.md`，先判断是否需要合议，再输出阶段门、共识、分歧、必改、建议、待确认、owner、验证方式和下一步去向；需要正式 PRD 时再回到 `product-prd-template.md` 和 `product-design-and-prd.md`，不要新增独立产品大师 Skill。
- **用户要从模糊想法直接出方案**：先过产品语义门禁，输出关键假设、待确认项和最小可评审结构；不要把假设写成已确认事实。
- **用户要流程**：输出角色、触发条件、主流程、逆向流程、异常流程、人工处理、通知、SLA 和审计。
- **用户要规则**：输出规则对象、触发条件、计算口径、优先级、版本、灰度、回滚、审批和验收样例。
- **用户要评审**：优先按目标一致性、边界完整性、对象清晰度、流程闭环、规则可验证、数据可追溯、风险可控排序。
- **用户要支付或资金方案**：进入 `payment-scenario-routing.md`，补充金融红线、资金流、账务、对账、结算和外部规则时效性。

## 路由红线

- 不要把页面功能清单当作产品架构。
- 不要只凭关键词路由；先判断用户真正需要的是产品方案、系统方案、运营方案还是支付专项。
- 不要为了回答完整而加载所有参考；只加载和当前场景相关的 reference。
- 不要在缺少用户、主体、目标、边界和验收标准时输出确定性方案。
- 不要在涉及资金、合规、隐私、安全和外部规则时跳过风险和待确认项。
