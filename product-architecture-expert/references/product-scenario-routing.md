# 产品架构场景识别与方案路由

本文用于在回答前快速判断产品架构问题属于哪类场景、应读取哪些参考、输出什么产物、优先检查哪些红线。它是知识路由，不是生产系统里的功能路由、支付通道路由或资金清结算路由。

## 使用时机

- 用户要求写作、生成、完善或评审 PRD、产品需求文档、产品方案、业务流程、状态机、规则矩阵、运营后台或验收标准。
- 用户提供原型、HTML、页面截图、页面说明或交互稿，要求反推、补写或评审 PRD。
- 用户提供客户访谈、工单、竞品动态、行业/政策资料、标杆实践、Markdown 笔记或知识库资料，要求做产品洞察、需求洞察、机会挖掘或机会雷达。
- 用户给出洞察、机会清单、需求池、老板/销售/客户诉求或路线图候选，要求做 Backlog 决策、需求优先级、User Story、AC 或研发可执行条目。
- 用户要求评估 AI Native 产品流程、Product Builder、业务 dogfooding、MVP/原型进入工程 harden、PRD 可执行上下文或交给架构师/GSD/CAD。
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
- AI Native 产品上下文、Product Builder、业务 dogfooding、MVP/原型进入工程 harden 和 GSD/CAD 产品侧交接读 `ai-native-product-context.md`。
- 通用产品架构读 `product-architecture-methodology.md`。
- 产品方案需要交给架构师继续做系统设计或业务驱动架构交接时，读 `product-architecture-methodology.md` 的“与技术架构的交接”和“业务驱动验证口径”，必要时加读 `product-prd-quality-gates.md`。
- 产品洞察、资料资产化、客户/竞品/标杆情报分拣、证据推理链或机会雷达场景，读 `product-insight-analyst.md`；机会需要排序或转研发候选时，再读 `po-backlog-manager.md`。
- 机会清单、需求池、Backlog 决策、优先级、路线图候选、User Story 或 AC 场景，读 `po-backlog-manager.md`，再按目标产物读取 `product-design-and-prd.md`。
- 图形化产品交付读 `diagram-output.md`。
- 支付资金场景读 `payment-scenario-routing.md` 和 `regulatory-baseline.md`；外卡收单、Mastercard、卡组织清算、Clearing Core、商户到账或收单风控同样先进入支付资金专项。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 产品场景初判 | 使用方式、产品语义门禁、快速路由表 | 输出路由细节 |
| PRD/产品方案 | 快速路由表、输出路由，并继续读 PRD reference | 支付资金专项，除非命中资金场景 |
| 原型/HTML/页面截图/交互稿反推 PRD | 使用方式、产品语义门禁、快速路由表，并继续读 PRD reference | 只描述页面控件 |
| PRD 文档质量治理 / 文档过厚过薄 / 版本评审同步 | 快速路由表、产品语义门禁，并继续读 `product-design-and-prd.md` 与 `product-prd-quality-gates.md` | 支付资金专项，除非命中资金场景 |
| 产品洞察 / 资料分析 / 机会雷达 | 快速路由表、产品语义门禁，并继续读 `product-insight-analyst.md` | 不把资料摘要当机会决策 |
| Backlog 决策 / 机会清单优先级 / User Story/AC | 快速路由表、产品语义门禁，并继续读 `po-backlog-manager.md` 和 `product-design-and-prd.md` | 不把洞察清单直接当研发任务 |
| 产品经理方法论 / 产品专家基础能力补齐 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“2B. 产品经理基础方法校准”和 `skill-tree.md` | 不把基础岗位清单替代复杂产品架构 |
| AI 产品工作成熟度 / AI-shaped readiness / AI 工作流改造 | 快速路由表、产品语义门禁，并继续读 `product-architecture-methodology.md` 的“2A. AI-shaped 产品工作成熟度” | 不安装外部 advisor，不把外部术语当团队结论 |
| AI Native Product Builder / 业务 dogfooding / MVP harden / 放下 PRD | 快速路由表、产品语义门禁，并继续读 `ai-native-product-context.md` | 不把 AI Demo 直接当需求，不把产品上下文包当 Execution Grant |
| 业务流程/状态/规则 | 产品语义门禁、快速路由表、通用场景识别问题 | PRD 模板正文 |
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
| 对象 | 核心对象、字段口径、生命周期、状态和不变量是否能解释流程。 | 先补对象模型和状态，不直接堆功能点。 |
| 流程 | 主流程、逆向流程、异常流程、人工流程、通知和 SLA 是否闭环。 | 输出待补流程分支和人工兜底，不只给成功路径。 |
| 规则 | 权限、审批、额度、计费、风控、通知、数据留存是否有版本和优先级。 | 用规则矩阵表达，标注规则 owner 和待确认项。 |
| 数据 | 指标、报表、埋点、审计、追溯、导出和数据源是否有口径归属。 | 标注口径负责人、数据源和校验方式。 |
| 风险 | 是否涉及资金、合规、隐私、安全、生产运营、外部规则或跨团队契约。 | 进入专项 reference，并列出专业确认方。 |
| 验收 | 正常、边界、异常、运营、数据和风险路径是否可测试。 | 补验收矩阵；无法验收的需求不写成可开发完成。 |

外部规则、政策、通道协议、卡组织/ACH/银行规则、云产品限制、第三方平台 API 或 SDK 版本会随时间变化。产品方案引用这类内容时，必须记录来源、版本或发布日期、适用范围、核验日期和确认方；无法确认最新版本时，只能列为待确认项。涉及真实资金、金融数据或支付网络时，继续读取 `regulatory-baseline.md`。

正式、完整、可评审、提交前或触发验证场景中，涉及外部规则时必须运行 `scripts/check_external_rules.py` 检查本地文本或显式传入的本地文件。该脚本只做完整性检查，不联网、不写文件、不替代规则真实性、适用性或可上线性的专业确认；无法运行时必须说明原因、人工检查结果和残余风险。

正式、完整、可评审、提交前、CR 或触发验证场景中，PRD、产品架构方案或图形 brief 必须运行 `scripts/check_product_deliverable.py --kind prd`、`--kind product-architecture` 或 `--kind diagram-brief`。该脚本只做本地文本完整性检查，不联网、不写文件、不替代产品判断、业务确认、合规审查或图形质量评审；无法运行时必须说明原因、人工检查结果和残余风险。

## 快速路由表

| 场景信号 | 优先读取 | 典型输出 |
| --- | --- | --- |
| 产品方向、业务目标、产品边界不清 | `product-architecture-methodology.md` | 目标、用户、范围、非目标、成功指标、关键风险 |
| 写 PRD、生成 PRD、完善 PRD、评审 PRD、从原型/HTML/页面截图/交互稿反推 PRD、产品方案、产品需求文档、需求说明书、需求文档模板、PRD 模板 | `product-prd-template.md`, `product-design-and-prd.md`, `product-architecture-methodology.md`；评审加读 `product-prd-quality-gates.md`，支付资金加读 `product-prd-financial-appendix.md`，运营数据发布加读 `product-prd-operations-and-data.md` | 可复制 PRD、产品方案、用户故事、验收标准、待确认项 |
| PRD 文档过厚、过薄、未更新、未评审、版本不同步 | `product-design-and-prd.md`, `product-prd-quality-gates.md` | 文档目标/受众、裁剪建议、必改项、版本/评审/同步机制 |
| 产品经理方法论、产品专家能力补齐、产品经理知识体系、基础工作法校准 | `product-architecture-methodology.md`, `skill-tree.md` | 能力校准：文档分型、流程表达、原型注释、产品架构图、用户研究、需求管理、数据分析、技术/项目协作、行业商业分析、知识库沉淀；并提升到复杂业务对象、规则、验收和交接能力 |
| AI 产品工作成熟度、AI-shaped readiness、产品团队 AI 工作流改造、AI 是否形成产品优势 | `product-architecture-methodology.md` | AI 产品工作成熟度评审：业务优势、流程变化、上下文结构化、可追溯任务、人工责任、验证周期/决策质量/返工率指标；不安装外部 advisor，不照搬外部话术 |
| 产品洞察、需求洞察、资料资产化、客户/竞品/标杆情报、机会雷达、证据推理链 | `product-insight-analyst.md`, `product-architecture-methodology.md` | 产品洞察报告：资料资产表、三类情报分拣、机会雷达、证据与推理链、置信度、待验证和建议去向；机会需要排序时再读 `po-backlog-manager.md` |
| 洞察太多、机会清单、需求池、路线图候选、Backlog 决策、优先级、P0/P1/P2、User Story、AC | `po-backlog-manager.md`, `product-design-and-prd.md` | Backlog 决策包：BV/EE、业务/用户/工程三桌校验、P0/P1/P2、拒绝理由、User Story、AC、技术现实主义风险和待确认项 |
| AI Native Product Builder、业务 dogfooding、MVP/原型 harden、放下 PRD、PRD 可执行上下文、交给 GSD/CAD | `ai-native-product-context.md`, `product-architecture-methodology.md`；正式 PRD 再读 PRD reference | AI Native 产品上下文包、Hardened Candidate 门禁、MVP 证据、对象规则、验收种子、风险确认和交给架构师/GSD/CAD 的产品侧交接条件；不把可运行等同于可上线 |
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
- 业务流程：主流程、逆向流程、异常流程、人工处理是否都需要覆盖。
- 规则体系：计费、额度、权限、审批、通知、风控、数据留存是否有版本和例外。
- 数据验收：指标、报表、埋点、审计、追溯和口径归属是否明确。
- 风险边界：是否涉及资金、合规、隐私、安全、生产运营或外部规则。

设计进入工程前，必须把稳定术语、核心对象、状态、规则和验收口径落到现有权威文档体系中，例如 PRD、产品设计、系分设计、OpenSpec 或 Harness Plan；共享语言服务于产品对象、规则和验收，不是额外文档本身。不要为此额外创建分散的 `CONTEXT.md` 或零散 ADR，除非项目本地规范明确要求。

## 输出路由

- **用户要产品架构方案**：输出背景、目标、范围、用户、角色、能力地图、对象模型、流程、状态机、规则、权限、数据、运营、风险和验收。
- **用户要 AI Native 产品流程、Product Builder、业务 dogfooding、MVP harden 或 PRD 可执行上下文**：读取 `ai-native-product-context.md`，先判断输入是意图、问题地图、可运行 MVP、产品候选、Hardened Candidate 还是噪声，再输出产品上下文包、验收种子、风险确认和交给架构师/GSD/CAD 的门禁。
- **用户要交给架构师继续设计或业务驱动架构交接**：输出产品侧交接包，覆盖目标/非目标/成功指标、参与方与 owner、核心行为、对象状态、规则矩阵、验收样例、质量属性种子、待确认项和专业确认方。
- **用户要补齐产品经理方法论或产品专家基础能力**：读取 `product-architecture-methodology.md` 的“2B. 产品经理基础方法校准”和 `skill-tree.md`，把基础产品经理知识体系翻译为文档分型、流程表达、原型注释、产品架构图、用户研究、需求管理、数据分析、技术/项目协作、行业商业分析和知识库沉淀，并说明哪些能力已覆盖、哪些能力需要提升到复杂业务对象、规则、验收和交接。
- **用户要评估 AI 产品工作成熟度或 AI-shaped readiness**：读取 `product-architecture-methodology.md` 的“2A. AI-shaped 产品工作成熟度”，把外部 advisor 术语翻译成业务优势、流程变化、上下文结构化、任务可追溯、人工责任和验证指标；默认只借鉴方法，不安装或调用外部 Skill。
- **用户要基于资料、访谈、竞品、行业/政策或知识库做产品洞察、需求洞察或机会雷达**：读取 `product-insight-analyst.md`，先做资料资产化和客户/竞品/标杆情报分拣，再输出机会雷达、证据与推理链、置信度、待验证和建议去向；没有材料的类别明确留白，不用模型记忆补编。
- **用户要消化洞察、机会清单或需求池，做 Backlog 决策、优先级、User Story 或 AC**：读取 `po-backlog-manager.md`，先做输入归一化、BV/EE 和业务/用户/工程三桌校验，再输出 P0/P1/P2、拒绝/延后理由、User Story、AC、技术现实主义风险、owner 和待确认项；不要把洞察清单直接改写成研发任务。
- **用户要图形化产物**：读取 `diagram-output.md`，先判断图形目标和图形类型；正式图形化交付默认只生成 SVG；Mermaid/Markdown 草图、PNG/PDF/截图等其他格式只在用户明确提出时生成，并报告验证结论。
- **用户要写作、生成、完善或评审 PRD / 产品需求文档 / 需求说明书 / 模板**：优先读取 `product-prd-template.md`，输出可复制 PRD，覆盖问题背景、用户故事、功能范围、业务规则、页面/交互说明、异常处理、埋点报表、权限、非功能和验收标准；评审或提交前自检读取 `product-prd-quality-gates.md`；支付资金 PRD 读取 `product-prd-financial-appendix.md`；运营、通知、数据、发布读取 `product-prd-operations-and-data.md`；信息不足时保留“待确认”，不要只给提纲。用户给原型、HTML、页面截图、交互稿或页面说明时，先反推角色、对象、流程、规则、状态和验收，再生成 PRD；不要只描述页面控件。
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
