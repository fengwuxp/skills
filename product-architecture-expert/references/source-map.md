# 公开资料来源与支付专项提炼边界

本文主要约束产品架构专家中支付与资金垂直分支的公开资料来源、引用边界和时效性风险；少量通用产品架构、PRD、Skill 和业务驱动验证来源也在此记录。通用产品架构方法见 `product-architecture-methodology.md`，产品洞察与机会雷达见 `product-insight-analyst.md`，PO Backlog 决策见 `po-backlog-manager.md`，产品方案与 PRD 结构见 `product-design-and-prd.md`。

## 使用时机

- 需要核对产品专家吸收过哪些公开来源、哪些来源可复核、哪些只能作为历史索引线索。
- 用户要求引用、复盘、对齐或质疑外部文章、厂商文档、官方规则来源时，用本文确认归因边界。
- 新增外部资料、归档本地证据、处理无法抓取或已删除文章时，用本文校准记录口径。

## 不适用场景

- 需要直接产出产品方案、PRD、能力地图、架构图或支付资金方案时，先读对应业务 reference；本文只解决来源可信度和提炼边界。
- 需要最新监管、卡组织、ACH、PCI、银行、通道、云产品、SDK/API 或外部服务规则结论时，必须重新联网核验官方来源、合同或专业确认结果，不能只依赖本文历史索引。
- 未通过 Playwright 或等价浏览器读取到正文的文章，不得仅凭 URL 或标题写成已吸收内容。

## 读取后必须产出

- 明确来源状态：公开可复核、官方来源、第三方索引、历史索引线索、当前不可复核或本地私有归档。
- 明确可吸收边界：只吸收问题框架、产品检查项、对象关系、流程边界和风险提示，不复制正文、字段清单、规则结论或商业承诺。
- 对无法复核、已删除、付费墙、验证页或正文为空的来源，输出待核验状态和风险，不把它们当作事实依据。
- 涉及时效性外部规则时，必须输出来源、版本或发布日期、核验日期、适用主体、适用法域和确认方。

## 需要继续读取的 reference

- 通用产品架构方法读 `product-architecture-methodology.md`。
- 产品洞察、资料资产化、客户/竞品/标杆情报分拣、机会雷达和证据推理链读 `product-insight-analyst.md`。
- PO Backlog 决策、机会清单、需求池、BV/EE、P0/P1/P2、User Story 和 AC 读 `po-backlog-manager.md`。
- 产品方案和 PRD 结构读 `product-design-and-prd.md` 与 PRD 相关拆分 reference。
- 支付资金场景读 `payment-scenario-routing.md`，再按任务读取对应专项 reference。
- 合规、监管、外部规则与官方来源边界读 `regulatory-baseline.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核对外部文章是否可吸收 | `读取与归因规则`、`本地证据归档规则` | 不读取整份来源清单 |
| 查找已参考来源和用途 | 先看 `来源主题索引`，再到 `已参考的公开来源` 中按 URL 或主题条目定位 | 不把条目描述当成原文逐字引用 |
| 新增来源或修正来源状态 | `读取与归因规则`、`本地证据归档规则`、`提炼边界` | 不把未抓取正文的文章标为公开内容用于参考 |
| 判断支付专项提炼边界 | `提炼边界`，必要时回到 `payment-scenario-routing.md` | 不把厂商文档、文章观点或第三方索引写成行业标准 |
| 需要最新规则或准确引用 | `读取与归因规则`、`提炼边界`，然后重新联网核验官方来源 | 不依赖历史索引直接给确定性结论 |

## 读取与归因规则

- 微信文章等动态页面必须先通过 Playwright 或等价浏览器自动化读取标题、作者、发布时间和正文；如果 Playwright 当前通道失败，但公开 HTML 中可读取到标题、作者、发布时间和正文，也可以写成“公开内容用于参考”，但条目必须同时记录 Playwright 尝试状态、公开 HTML 读取状态和读取日期。
- 未读取到正文、页面删除、只剩验证页或正文为空的条目，只能标为“当前不可复核”或“历史索引线索”，不得作为已吸收来源。
- 条目中的英文术语、分层名称和能力边界可能是 Skill 为统一输出做的标准化表达，不代表原文逐字表述；需要引用作者原话时必须重新读取正文并核对。
- 从文章吸收的内容只作为产品架构问题、检查项、路由和边界，不作为监管、合同、卡组织规则、财务准则或上线结论。
- 本文只记录历史读取状态和应用位置，不把读取日期当成当前核验日期，不代表来源仍然最新可用；具体任务涉及金融、合规、监管、云产品、SDK/API、外部服务、卡组织、ACH、银行、通道、税务或会计准则时，必须进入外部知识时效性门禁，按最新公开来源、官方规则、项目 lockfile、本地依赖树、合同或专业确认结果复核，并记录核验日期和确认方。

## 本地证据归档规则

- 对高价值且可能删除的文章，可用 `scripts/archive-source-evidence.py` 将已读取到的本地证据文件归档到仓库外目录，默认 `~/.skill-source-archive/`，或由 `SKILL_SOURCE_ARCHIVE_HOME` 指定。
- 本文件只记录公开索引、读取状态、提炼边界、`archive_id`、`evidence_sha256` 和读取日期等轻量 metadata；不得写入文章全文、原图、截图包、MHTML、PDF、付费内容或大段摘录。
- `archive_id` 只能作为本机私有证据定位符，不代表公开来源仍可访问；需要引用或复核时仍要优先重新读取公开页面或官方来源。
- 删除、验证页、空正文或无法复核的条目，即使存在本地归档，也不得写成“公开内容用于参考”，只能说明归档证据来源、读取日期、当前复核状态和剩余风险。

## 来源主题索引

- 支付系统与支付账本：检索“支付系统”“账本”“清算/结算”“对账”“账务核心”。
- 卡组织、发卡与 VCC：检索“Mastercard”“Visa”“Issuing”“VCC”“虚拟卡”“授权”“Clearing”。
- 全球支付与基础设施：检索“Airwallex”“WorldFirst”“全球支付”“跨境”“Payouts”“Global Accounts”“embedded finance”“AI 出海”“全球资金管理”。
- 收单、争议与风险运营：检索“外卡收单”“收单风控”“争议”“Chargeback”“Fraud”。
- AI / Skill / 通用复杂度：检索“Agent Skills”“代码不再稀缺”“复杂度”“低成本生成”。
- 产品头脑风暴与假设挑战：检索“product-brainstorming”“问题探索”“HMW”“第一性原理”“OODA”“逆向头脑风暴”“假设挑战”。
- AI Native 产品上下文：检索“AI Native”“Product Builder”“业务 dogfooding”“MVP harden”“PRD 可执行上下文”“放下 PRD”“Hardened Candidate”。
- AI 产品发心与定位复盘：检索“置身钉内”“AI 产品发心”“AI 产品定位”“真实工作流”“用户张力”“灰度止损”。
- 模糊需求到可开发系统：检索“从一份模糊需求”“AI 全栈工作流”“内容系统”“多端平台”“结构化需求文档”“业务流”“高保真 HTML 原型”“开发任务”。
- 产品洞察与机会雷达：检索“产品洞察”“需求洞察”“机会雷达”“资料资产化”“客户视角”“竞品视角”“标杆视角”“证据推理链”。
- Backlog 决策与机会收敛：检索“Backlog”“机会清单”“需求池”“BV/EE”“User Story”“AC”“技术现实主义”“三桌校验”。
- AI-shaped 产品工作成熟度：检索“ai-shaped-readiness-advisor”“AI-shaped”“AI-first”“Context Design”“Agent Orchestration”“Outcome Acceleration”。
- 产品经理方法论与基础能力：检索“产品经理方法论”“赵丹阳”“BRD/MRD/PRD”“流程图”“原型图”“产品架构图”“需求管理”“用户研究”“数据分析”。
- 需求分析与产品定义：检索“架构30”“架构思维：需求分析”“根源需求”“产品定义”“产品边界”“稳定点”“变化点”“边界坐标”。
- 产品价值 / 成本函数与业务同质性：检索“所有的技术架构，本质上都是业务架构”“兑现那个问题”“价值函数”“成本函数”“主要矛盾”“业务同质性”“技术平台不是产品”。
- 需求标准与可验证 PRD：检索“标准不是摆设”“需求标准”“设计标准”“编码标准”“需求是软件的根本”“需求基线”“可验证性”“可追踪性”“衍生需求”。
- 产品 DNA 与规则先行：检索“软件工程最大的 Bug”“系统生长顺序”“产品 DNA”“系统 DNA”“业务不变量”“状态流转”“演化规则”“功能先行、规则后补”。
- 产品图形化与服务蓝图：检索“用户旅程”“服务蓝图”“UX mapping”“AI 画图”“draw.io”。
- 需求分析与设计基础：检索“功能定义”“功能分配”“需求分析”“设计活动”“可见价值行为”。
- AI 辅助 PRD 与问题地图：检索“AI 写 PRD”“用户反馈”“问题地图”“证据强度”。
- 产品合议评审与多 Agent PRD：检索“产品大师”“MAGI”“多 Agent”“PM Reviewer Controller”“合议评审”“AI 生成 PRD”。
- PRD 文档质量治理：检索“高质量需求文档”“PRD/MRD/BRD”“版本管理”“评审机制”。
- 需求评审 AI 预扫描：检索“完整不等于可测”“需求评审”“完整性”“一致性”“可测试性”“二义性”“AI 预扫描”。
- 通用产品架构与业务驱动验证：检索“Impact Mapping”“BDD”“业务目标”“验收场景”“产品到架构交接”。
- PRD 模板与发布验证：检索“Atlassian PRD”“assumptions”“success metrics”“release criteria”“bidirectional traceability”。
- 官方规则与监管：检索“Nacha”“Visa Core Rules”“Mastercard Rules”“监管来源”，并继续回到 `regulatory-baseline.md` 核验。

## 已参考的公开来源

- 陈天宇宙个人内容站：`https://chentianyuzhou.com/`。公开页面显示其主题覆盖支付学习社区、支付全链路设计、全球支付、跨境支付、Web3 支付、业财一体化、清结算等。
- 微信公众号“陈天宇宙”，微信号 `chentianyuzhou`。第三方公开索引显示其定位为支付架构师内容号，主题覆盖国内支付、全球跨境支付清算、银行核心及支付场景数字化；该信息来自索引站，不作为作者官方确认源。
- 新榜公众号主页：`https://www.newrank.cn/profile/gongzhonghao/E24A763156B3CCD5244168A76D16C524?from=ranklist`。公开页展示公众号账号信息、简介、代表作方向和近 7 日样例数据。
- 今天看啥公众号历史文章索引：`https://www.jintiankansha.com/column/lxUuto3M0B`。公开页列出公众号近期文章主题，如银行核心、稳定币、Swift/跨境支付、Web3、全球支付清算、支付名词等。
- OpenI 公众号收录页：`https://openi.cn/sites/239167.html`。公开页展示公众号微信号、简介、注册和历史数据等索引信息。
- PM 老猫作者页：`https://www.mroldcat.top/u/84`。公开简介称其为支付领域作者，代表作包含《支付32真经》《上帝视角看支付》《支付之门》等，并持续发布支付主题文章。
- 人人都是产品经理作者页：`https://www.woshipm.com/u/94217`。公开文章列表包含 Swift/跨境支付、三方支付架构、电子钱包、日切、支付清算生态、支付单据等主题。
- 人人都是产品经理文章《万字：清结算体系，全局方案深度解析》：`https://www.woshipm.com/pd/6063150.html`。公开内容围绕清结算全局核算、四段数据、在途、对账和备付金核算。
- 人人都是产品经理文章《万字：“清算、结算、清结算”的区别》：`https://www.woshipm.com/pd/6046875.html`。公开内容强调清算、结算概念需要先约定语境。
- 人人都是产品经理文章《拆解支付产品经理的3大底层能力》：`https://www.woshipm.com/pd/5892058.html`。公开内容聚焦支付流分析、模式化设计和架构能力。
- 人人都是产品经理文章《清算系统设计方法》：`https://www.woshipm.com/pd/4620599.html`。公开内容介绍清算系统、利益计算和分配。
- 微信公众号文章《3.5万字：一文搞懂“支付系统”》：`https://mp.weixin.qq.com/s/7sZhZPeBE7XmBLjik8al8w`。公开内容用于参考支付系统五层拆解、支付核心主流程、收银台、路由、通道管理、退款和广义通道等支付产品架构视角。
- 微信公众号文章《图解支付清算生态全景》：`https://mp.weixin.qq.com/s/4P1PuButME_rr5anXeK2ng`。公开内容用于参考支付清算生态分层、跨机构清算、备付金/额度口径、清算机构、商业银行和央行支付系统等宏观架构视角。
- 微信公众号文章《一文搞懂“全球支付清算”基础原理，建立国际支付底层认知》：`https://mp.weixin.qq.com/s/86gPuhw8eUYb65gRhALH6A`。公开内容用于参考全球支付清算基础、Nostro/Vostro、外清内结、清算行/代理行/NRA 模式、Swift/GPI 与跨境到账追踪。
- 微信公众号文章《全球支付「信息流和资金流」5层分析法，一张图掌握最底层的原理！》：`https://mp.weixin.qq.com/s/FM6h2bbN5xLXZQLJYG-cWg`。公开内容用于参考全球支付信息流和资金流五层拆解：交易层、支付处理层、代理结算层、清算网络层和最终清算层。
- 微信公众号文章《理解了这2个字，就悟透了支付！》：`https://mp.weixin.qq.com/s/r2bUyLICOvWV40GOIfBbGw`。公开内容用于参考支付账本观、多套账本、清算/结算双层、代理结算模式和客户备付金/内部账本关系。
- 微信公众号文章《500个支付知识点，看完秒变支付大师！》：`https://mp.weixin.qq.com/s/atTMCmIoQaG0EIsed2TATg`。公开内容仅用于支付知识体系主题索引和能力地图校准，不复制知识点清单或原文结构。
- 微信公众号文章《一文搞懂：全球卡组织「支付清结算」原理》：`https://mp.weixin.qq.com/s/NVmy4mKSB83bP18u6XEzHA`。公开内容用于参考卡组织支付清结算、四方/三方模式、BIN 路由、授权、清算、结算和跨境卡费用口径。
- 微信公众号文章《21张图，讲清楚三方机构「支付全链路」处理逻辑与架构》：`https://mp.weixin.qq.com/s/ZhKc64tXXguEFJYxozuMtw`。公开内容用于参考三方支付机构全链路、接入层/业务层/交易层/支付处理层/风控层/支付通道，以及收款、付款、退款、清算、结算、账务处理。
- 微信公众号文章《做好支付，需要懂的会计基础》：`https://mp.weixin.qq.com/s/04oIhVhypiZv7sRWygtOoA`。公开内容用于参考会计恒等式、会计循环、总账/明细账、日记账、凭证、科目、借贷方向和试算平衡。
- 微信公众号文章《详解账务核心，从入门到精通》：`https://mp.weixin.qq.com/s/WWhjG9ACi3qmqeqPFvBaaA`。公开内容用于参考账务核心架构、账户体系、热点账户、账户合并、会计日切、营销账务、清结算账务和外围系统驱动。
- 微信公众号文章《账务核心的核算、架构、产品》：`https://mp.weixin.qq.com/s/GdUQICxGjOAudeAdC-H6FA`。公开内容用于参考账务核心的账户层、账务层、账簿层、总账层分层，日间联机账务与日终总账核算，实时/缓冲记账，科目、分户账、凭证、分录流水、试算平衡、总分核对和后台管理面；具体科目层级、性能策略和财务处理方式需结合主体、财务制度和账务负责人确认。
- 微信公众号文章《一文搞懂「支付合规」全局：反洗钱、KYC、KYT、大额交易……》：`https://mp.weixin.qq.com/s/FVx1lUcxCF3jUl0Xh6UydA`。公开内容用于参考支付合规、KYC/KYB/KYT/KYA、持续监控、交易限额、反洗钱/反恐怖融资、欺诈和 Web3 合规主题。
- 微信公众号文章《一文说清楚“清算、结算、清结算”的区别》：`https://mp.weixin.qq.com/s/vQh7wUILKVTLP9xq6xDvmw`。公开内容用于参考清算、结算、清结算在理论概念、机构命名、平台产品和企业信息层处理语境中的差异。
- 微信公众号文章《头部大厂，怎么做清结算全局规划，分享一个真实案例！》：`https://mp.weixin.qq.com/s/vHJ7LlePC8o5qV84XVtU4Q`。2026-05-26 Playwright 核验结果为页面已被发布者删除，正文不可复核；仅保留为历史索引线索，不得作为已吸收来源。既有“多业务线清结算全局规划”能力只能按通用支付清结算实践、项目事实和其他可核验来源重新确认。
- 微信公众号文章《清结算和「对账」不是一回事——我们曾因此对错账、赔过钱》：`https://mp.weixin.qq.com/s/oXTAGAvE_OwNJfq1JXLZ0w`。公开内容用于参考清账、结算和对账的边界，尤其是先清账再结算、先对清账再对结算、调账/冲正/负项必须进入清账模型的案例化门禁。
- 微信公众号文章《Mastercard 授权体系的真正重点》：`https://mp.weixin.qq.com/s/Dh22dNM6Ze4fHgytthN0ng`。公开内容用于参考 Mastercard 授权作为网络级前置裁决、授权消息家族、Stand-In/SAF/Advice/Reversal、open-to-buy 管理、Trace ID 和授权数据准确性等产品架构视角；具体规则、字段、费用和适用条件以 Mastercard 官方规则、CIS/授权手册或机构合同为准。
- 微信公众号文章《Mastercard 到底在做什么？》：`https://mp.weixin.qq.com/s/gyLFP4J0syasU4DahMYy9A`。公开内容用于参考 Mastercard 作为支付网络、交易处理、参与方角色、责任管理、成本计收和网络治理的能力栈视角；文中商业数据、时间点和产品路线需以 Mastercard 官方资料和最新合同规则复核。
- 微信公众号文章《Mastercard全栈深度解析（3）：Mastercard授权架构设计（构建可扩展的卡支付实时交易核心）》：`https://mp.weixin.qq.com/s/rgZSbR_2zfkISFhSuHmMPg`。公开内容用于参考 Authorization Core、Authorization Lifecycle、Hold/Reference Chain、network session boundary、ISO 8583 semantic carrier、scheme adapter、SAF recovery 和授权可观测性。
- 微信公众号文章《Mastercard全栈深度解析（4）：Mastercard Clearing 体系设计（上篇）》：`https://mp.weixin.qq.com/s/uuEwioL-Xx3JKeGvG7AyCg`。公开内容用于参考 Clearing 不是文件状态更新，而是 Financial Presentment、账务进入、费用拆分和后续争议追溯的入口。
- 微信公众号文章《Mastercard全栈深度解析（4）：Mastercard Clearing 体系设计（中篇）》：`https://mp.weixin.qq.com/s/iSvq8LO0zjHlW20ZUf_S6Q`。公开内容用于参考 Matching Core、ARN / Reference Model、Fee & Amount Decomposition、Posting Model、异常处理/隔离和清算到账务承接。
- 微信公众号文章《Mastercard全栈深度解析（4）：Mastercard Clearing 体系设计（下篇）》：`https://mp.weixin.qq.com/s/sU_Opre7z9cRVdtOB1y-Zg`。公开内容用于参考 Clearing Core 作为生命周期治理能力，覆盖 transaction lifecycle、accounting consistency、reference continuity、dispute traceability、replay / investigation、四层 reconciliation、清算异常按交易链影响分类，以及多卡组核心语义与适配边界。
- 微信公众号文章《外卡收单体系全景（4）：清算之网》：`https://mp.weixin.qq.com/s/Y1O4BsLo4DD0HgkKYSRQnw`。公开内容用于参考外卡收单中 authorization、clearing、settlement 的语义差异，以及清算连接交易、账务、费用、责任、对账和争议的产品视角。
- 微信公众号文章《外卡收单体系全景（5）：结算之路》：`https://mp.weixin.qq.com/s/hilJTPiiakSQvDLYAzHtuA`。公开内容用于参考 settlement 不是商户打款动作，而是成员级结算、平台内部分配/轧差、商户结算/打款、银行到账、保证金/延迟结算和商户可用资金管理。
- 微信公众号文章《外卡收单体系全景（6）：风控之盾》：`https://mp.weixin.qq.com/s/MXKNyFtROB-F-mEM1nNoPQ`。公开内容用于参考外卡收单风控贯穿商户准入、交易、capture / 履约、结算、争议反馈和资金策略，而不是单点交易拦截。
- 微信公众号文章《你不是在接卡组，你是在组织一张网》：`https://mp.weixin.qq.com/s/IpEWgr-8pMzUP480TDWlFw`。公开内容用于参考外卡收单从接卡组/API 升级为全球支付编排能力，覆盖卡组、钱包、本地支付方式、APM/RTP/A2A、PSP/网关、认证风控、结算资金、争议治理和运营闭环；涉及 Visa、Mastercard、稳定币结算或 PSP 趋势的时效性判断必须回到官方公开资料和合同规则复核。
- 微信公众号文章《全球支付的真相，被Airwallex捅破了》：`https://mp.weixin.qq.com/s/ezAitX0UGWv9H2FnM3x3ew`。公开内容用于参考全球支付平台评估中的表层功能同质化、底层基础设施控制力、复杂性承接、客户侧确定性和三类路径判断；文中对具体公司、增长、竞争格局和商业判断的描述仅作案例线索，不作为行业标准或确定事实。
- Airwallex 官方博客《CEO 致员工信｜难走的路，才是出路：Airwallex 构建全球支付基础设施的关键抉择》：`https://www.airwallex.com/cn/blog/the-path-of-max-resistance-the-spectrum-of-global-payments-infrastructure`。公开内容用于交叉参考全球支付基础设施自建、牌照、本地网络和长期投入的厂商视角；不把厂商观点直接等同于产品架构规范。
- Airwallex 官方博客《全球支付的最后一公里》：`https://www.airwallex.com/cn/blog/the-last-mile-of-global-payments`。公开内容用于交叉参考全球支付最后一公里、本地支付体验、统一基础设施栈和多市场对账的厂商视角；具体产品能力、覆盖地区和时效需以最新官方页面或合同确认为准。
- Airwallex Docs Home：`https://www.airwallex.com/docs`。公开产品文档用于参考全球金融平台能力分层，覆盖 Connected Accounts、Accounts、Payments、Billing、Transactional FX、Payouts、Issuing、Spend、Global Treasury、Banking as a Service、Payments for Platforms、Developer tools、Webhooks 和 Sandbox；只吸收产品能力地图、对象边界、状态/事件/报表/测试闭环，不固化覆盖国家、币种、费率、接口字段或商业承诺。
- Airwallex Accounts Docs：`https://www.airwallex.com/docs/accounts/overview`。公开文档用于参考多币种账户、Global Accounts、本地清算或 SWIFT 入账、direct debit 授权、账户状态、入账状态、受监管地区差异和账户类 integration checklist；具体地区、账户能力和直接扣款规则需以最新官方文档、合同和合规确认结果为准。
- Airwallex Payments Docs：`https://www.airwallex.com/docs/payments/overview`。公开文档用于参考在线收单、一次性/周期性付款、多本地支付方式、支付状态、webhook、退款/取消、欺诈、争议、settlement report、activity export、fee / FX / rounding 和 go-live checklist 的产品闭环；不照搬支付方式列表、状态枚举、错误码或 API 字段。
- Airwallex Payouts Docs：`https://www.airwallex.com/docs/payouts/overview`。公开文档用于参考全球付款的 transfer、beneficiary、payer、batch transfer、approval、failure reason、confirmation letter、regulatory requirement、beneficiary schema、tax reporting 和 status simulation 的对象化设计；不把国家字段、银行清单或税务要求写成通用规则。
- Airwallex Issuing Docs：`https://www.airwallex.com/docs/issuing/overview`。公开文档用于参考发卡、VCC、cardholder、card、issuing balance、card control、remote authorization、3DS、transaction lifecycle、dispute、overcapture、fraud feedback 和 transaction simulation 的产品设计模式；不替代发卡资质、卡组织规则、PCI DSS、银行协议或最新安全要求。
- 微信公众号文章《万里汇，太牛了！AI出海的全球资金管理，算是让它玩明白了》：`https://mp.weixin.qq.com/s/mTLMJVO4_NNlENZP8utZGA`。2026-05-29 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，并用本机 Chrome headless 作为 Playwright 等价浏览器加载页面做核验。公开内容用于参考 AI 出海企业全球资金管理的场景拆解，覆盖全球收款、多币种账户、FX、批量付款、VCC / Agent 支付控制、token / 用量计费和嵌入式金融组合；不吸收厂商覆盖国家、币种、时效、牌照数量、费率、AI 外汇预测能力、商业判断或产品可用性承诺，具体能力需回到最新官方资料、合同和合规确认。
- 微信公众号文章《代码不再稀缺，稀缺的是你如何对抗复杂度》：`https://mp.weixin.qq.com/s/TxU2D0Plf__Xh-yUD2zjPA`。2026-05-26 已尝试 Playwright，当前浏览器通道加载为空白；随后通过公开 HTML 读取到标题、作者、发布时间和正文，公开内容用于参考 AI 代码生成时代实现成本下降、复杂度/注意力成本上升、系统设计、前置约束和问题定义能力的重要性；只吸收问题框架和能力定位，不复制原文或作者表达。
- 微信公众号文章《放下 PRD：写给AI Native时代的产品经理朋友们》：`https://mp.weixin.qq.com/s/5TEAxFYueNc6MD5ngKEgGg`。作者/账号为 `大数据随笔`，发布时间为 2026-05-25 18:00:00；2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未再执行 Playwright 等价浏览器取证。公开内容用于参考 AI Native 下 PRD 从静态翻译文档转为可运行证据、对象规则、验收种子和工程交接门禁的上下文包，覆盖 Product Builder、业务 owner + Agent、业务 dogfooding、MVP/原型 harden 和产品侧交接；端到端 GSD/CAD 准入与 AI 工具编排交给 `ai-native-engineering-workflow`，不复制原文、标题表达、作者判断、引用案例、传播性措辞或岗位评价，也不把“放下 PRD”理解为跳过产品语义、评审、留痕、合规和验收。
- 微信公众号文章《软件工程最大的 Bug：我们把系统生长顺序做反了》：`https://mp.weixin.qq.com/s/YM0BI6tCXLpwEf8hZuYvYA` 与《为什么优秀架构越来越像生命？》：`https://mp.weixin.qq.com/s/95YFNicYQnDRt9SZHrpKnQ`。作者/账号均为 `霍旭东` / `ThinkingInDev`，页面时间字段分别为 2026-06-08 20:19:14 与 2026-06-09 07:00:00 Asia/Shanghai；2026-06-11 首篇 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考 `product-architecture-methodology.md` 的产品 DNA、核心对象、业务不变量、生命周期 / 状态、责任边界、演化规则、验收方式和“功能先行、规则后补”反模式，以及 `product-prd-template.md` 的产品 DNA 卡；不复制原文、图片、比喻、标题传播话术、作者表达或“数字生命”推测，也不把产品 DNA 写成替代用户研究、业务 owner 确认、合规确认、系统设计或 Execution Grant。
- 微信公众号文章《所有的技术架构，本质上都是业务架构》：`https://mp.weixin.qq.com/s/4mOd-ZbtE-J6O-aDPOSUQg` 与《兑现那个问题“产品需要做什么”》：`https://mp.weixin.qq.com/s/dHXUnZI6rVGYqpyqPnjo4w`。作者字段均为 `大象无棱`，页面时间字段分别为 2026-04-25 09:32 与 2026-06-10 09:11 Asia/Shanghai；2026-06-11 首篇通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文，第二篇普通 `curl` 返回微信验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文。公开内容用于参考 `product-architecture-methodology.md` 的价值 / 成本函数、主要矛盾、用户逻辑、业务同质性、技术平台不是产品、产品到开发语言转译和强行平台化风险；不复制原文、故事经历、比喻、图片、作者表达或标题传播话术，也不把文章观点写成组织制度、客户事实、合规结论或 Execution Grant。
- 微信公众号文章《阿里内网万言离职书〈置身钉内〉原文，已刷屏》：`https://mp.weixin.qq.com/s/_D20O0vpPXjSzjAKJmBYuA`。作者为 `Corgi/滕雅辛`，公众号为 `爬梯意外簿`，发布时间为 2026-06-05 16:21；2026-06-07 普通 `curl` 返回微信“环境异常”验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、账号、作者、发布时间和正文，页面正文声明内容由 AI 识图整理，故只作为公开转述/OCR 复盘材料。公开内容用于参考 `product-architecture-methodology.md` 中 AI 产品发心、定位、用户张力、真实工作流、灰度止损和反模式门禁；不复制原文、项目细节、组织评价、作者表达或标题传播话术，也不把文章内容写成钉钉/ONE 官方事实、行业结论或产品成败定论。
- 微信公众号文章《从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战》：`https://mp.weixin.qq.com/s/HzbdrmNkT-OTRKdQh0c0Ug`。作者/账号为 `KEEN的创享`，发布时间为 2026-06-04 21:39；2026-06-07 普通抓取返回微信验证页或无正文，随后通过移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文。公开内容用于参考 `product-architecture-methodology.md` 中模糊需求到内容/多端系统的结构化需求、业务流、对象规则、原型说明和开发交接秩序；不复制原文、项目案例、页面设计、提示词、图片或作者表达，也不把文章示例项目写成通用产品模板。
- 微信公众号文章《`product-brainstorming` Skill 原文中文版》：`https://mp.weixin.qq.com/s/cz-9HnmlC_VNcVpdd_e0Vw`。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `进击的肖恩`，既有账号线索保留 `AIML实验室`，页面时间字段为 2026-04-21。正文标注原始文件为 `knowledge-work-plugins/product-management/skills/product-brainstorming/SKILL.md` 并给出 GitHub 仓库链接；本轮尝试读取 GitHub raw 原始 `SKILL.md` 未及时返回，因此只把微信译文作为已读公开材料，原始 GitHub 作为待进一步核验线索。公开内容用于参考 `product-architecture-methodology.md` 的产品头脑风暴纪律：问题探索、方案发散、假设挑战、HMW、第一性原理、类比、反转、OODA 和逆向头脑风暴；不复制原文角色提示、问题清单、外部 Skill 结构或作者表达，也不把头脑风暴输出直接写成 PRD、Backlog 或研发任务。
- 微信公众号文章《放下代码：AI Native是通往架构师的快车道》：`https://mp.weixin.qq.com/s/fhEzrPbeez-_2bmJHqExCQ`。作者/账号为 `大数据随笔`，发布时间为 2026-05-23 12:00:00；2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未再执行 Playwright 等价浏览器取证。公开内容用于参考 `资深架构师` AI Native 架构师工作面；产品专家只借鉴其与产品上下文交接相关的 harden 思路，不复制原文、引用案例、岗位判断或作者表达。
- 微信公众号文章《架构师必备--让AI画架构图》：`https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg`。作者/账号为 `方兴集`，发布时间为 2026-04-30 16:28:31；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（本机 Chrome headless）加载取证但返回异常。公开内容用于参考 AI + draw.io 的自然语言生成、文档转图、图像参考、版本历史、可编辑 draw.io XML 和本地模型/凭据边界；不复制原文示例图、提示词、项目安装说明、工具宣传语或作者表达，也不把具体工具能力写成产品图质量结论。
- 微信公众号文章《架构30：架构思维：需求分析》：`https://mp.weixin.qq.com/s/B8Rap_MmAKmVN3f7eAnvCw`。作者字段为 `开心就好TF`，页面时间字段为 2026-06-07 09:34:00 Asia/Shanghai；2026-06-09 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文（发布时间取页面时间字段）。公开内容用于参考 `product-architecture-methodology.md` 与 `product-design-and-prd.md` 中根源需求、产品定义、产品边界、上下游分工、稳定点 / 变化点和边界坐标门禁；不复制原文、案例、作者表达、标题传播话术或时间投入比例，也不把文章观点写成组织制度、项目事实或执行授权。
- 微信公众号文章《[013] 标准不是摆设——需求标准、设计标准、编码标准怎么写》：`https://mp.weixin.qq.com/s/W44YHT-9bUCrSjsrZIYItw`；《[014] 85%返工都是需求的锅——为啥说需求是软件的根本》：`https://mp.weixin.qq.com/s/MO8EsLHm9QNauNLDQ1Z05Q`。作者/账号字段为 `AIIIIlIIII`，页面时间字段分别为 2026-05-23 07:24:00 与 2026-05-26 06:21:00 Asia/Shanghai；2026-06-09 首篇 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考 `product-prd-quality-gates.md` 与 `product-design-and-prd.md` 的需求条目标准、图文追踪、系统/外部需求未确认不下钻、衍生需求、可验证性和可追踪性门禁；不复制原文、适航/DO-178C 语境、标题比例、作者表达、案例或标准条文，也不把文章观点写成产品团队制度、合规结论或执行授权。
- 微信公众号文章《需求分析和设计活动关键要点总结》：`https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q`。作者为 `常识`，公众号为 `软件需求分析和设计`，发布时间为 2026-05-26 10:29:23；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（本机 Chrome headless）加载取证。公开内容用于参考功能定义、功能分配追溯、需求分析外部视角和设计内部视角的分工；不复制原文中的 GJB 章节表述、推荐书目、课程机构推荐或作者表达，也不把军标/适航语境写成通用产品强制流程。
- 微信公众号文章《清算文件迟到 24 小时：财务骂网关之前，该对齐的 5 个问题》：`https://mp.weixin.qq.com/s?__biz=MzI3ODQ1MjQwOA==&mid=2247484523&idx=1&sn=bab6c18e89728feaf921bccbc5cb88d3`。公开内容用于参考外卡/跨境收单清算文件延迟排查，覆盖交易日/清算日/入账结算日、cut-off、processing calendar、时区、ACK/reject、批次 ID、三段链路归因和资金链路事故升级信号。
- 微信公众号文章《外卡收单钱收到了，战争才刚开始》：`https://mp.weixin.qq.com/s?__biz=MzI3ODQ1MjQwOA==&mid=2247484517&idx=1&sn=a171eb833dc25e6e83be75c407ad69ff`。公开内容用于参考外卡收单争议治理，覆盖 Alert / Inquiry / Retrieval / Chargeback / Representment / Pre-arbitration / Arbitration 链路、卡争议与非卡争议分轨、争议率/CB 率红线、止血/组证/representment 决策和反馈回流；Visa/Mastercard 监控阈值、生效日和区域规则以官方资料、收单行或通道合同为准。
- 微信公众号文章《Agent Skills 实战：把 PRD 需求文档写成 Skill》：`https://mp.weixin.qq.com/s/IvaaVh_li9ysvghSjUjnhQ`。公开内容用于参考 PRD Skill 化、团队模板清单化、生成/补全/符合性评审双模式、必填章节检查、用户故事/验收标准可验证性和 scripts/reference 分层；不复制原文模板或另建重复 PRD Skill。
- 微信公众号文章《产品经理的PRD写作武器：一个Skills让写PRD从3小时缩到3分钟》：`https://mp.weixin.qq.com/s/qRv1Qe3GjQ_jbQqWGQcHfQ`。2026-05-27 普通 curl 返回环境异常验证页；随后通过移动端微信 UA 公开 HTML 读取到标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（Chrome headless）加载取证，公开内容用于参考 PRD 作为产品思考结构、模糊需求连续追问、原型/HTML/页面截图/交互稿反推 PRD、需求 ID、优先级、文档状态和评审清单；不复制原文模板、安装说明、外部 Skill 结构或效率营销表述。
- 微信公众号文章《产品经理别再只让 AI 写 PRD 了，先把用户反馈整理成一张问题地图》：`https://mp.weixin.qq.com/s/sY6cw6wE5ePyrZmRYbXApg`。2026-05-28 普通 curl 初始因沙箱 DNS 失败；随后通过移动端微信 UA 公开 HTML 读取到标题、作者、发布时间和正文，并已尝试 Browser/Playwright 等价浏览器加载取证但页面加载超时/会话重置。公开内容用于参考 AI 辅助 PRD 前的用户反馈证据整理、问题地图、原始反馈到真实问题的转换、证据强度和潜在机会字段，以及 AI 初稿的人工判断门禁；不复制原文表格、图片、作者表达或外部工具营销。
- 微信公众号文章《我让3个AI吵了一整天架，它们把PRD写完了》：`https://mp.weixin.qq.com/s/13wn5wS8AwyMNBrMQpTyEg`。作者为 `Kira2red`，账号为 `产品异兽 Prod.Monster`，发布时间字段为 2026-05-17 10:05:10 Asia/Shanghai；2026-06-05 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未执行 Playwright 等价浏览器取证。公开内容用于参考 `product-deliberation-workflow.md` 中复杂 PRD、AI 生成方案和原型候选的产品合议评审：Controller / PM / Reviewer 工作位、强制阶段门、用户确认点、指定 Skill / 模板约束、SOP、复杂度评估、类型分流、分批产出和准出检查；不复制原文、图片、外部平台工具调用、watchdog 脚本、车载专项规则、作者表达或标题传播话术。
- GitHub 仓库 `Kira2red/magi-product`：`https://github.com/Kira2red/magi-product`。2026-06-05 已读取公开 README、仓库文件树、`部署包-product-master/SKILL.md`、`lead-pm-prompt.md` 和 `reviewer-prompt.md`。本仓库只吸收三角色产品工作位、阶段确认、证据审查、PRD 类型判定、分批产出、格式门禁和上下文污染防范的可迁移方法；不复制 OpenClaw/Hermes 专属命令、外部 delegate_task 机制、/tmp 标记、watchdog 脚本、车载国标细节、Demo 代码陷阱或长 prompt。
- GitHub 仓库 `Kira2red/Kira-product-monster-skills`：`https://github.com/Kira2red/Kira-product-monster-skills`。2026-06-05 已读取公开 README、仓库文件树、`Kira-product-monster-prd/SKILL.md`、`Kira-product-monster-featurelist/SKILL.md`、`2red-product-whitepaper/SKILL.md`、`Kira-product-monster-prd/references/examples.md` 和 `gbg-holy-grail-war/SKILL.md`。本仓库只吸收 PRD 共享层/模块层分离、PRD 类型判定、界面状态与异常覆盖、图形触发条件、验收覆盖、Feature List 颗粒度和白皮书增量维护的检查思路；不复制外部 Skill 结构、README、示例正文，不复制游戏 Skill、纯中文绝对化约束、PlantUML 图片生成要求或产品白皮书全量维护流程。
- 微信公众号文章《为什么你的 AI 只能写总结，别的产品经理已经用AI在挖需求机会了？附skill模板和调试方法》：`https://mp.weixin.qq.com/s/jsuVbuvKJxEXl8dZyzh23g`。作者为 `糖糖`，公众号为 `产品AI力学`，发布时间为 2026-04-23 19:30:00 Asia/Shanghai；2026-06-03 普通 curl/mobile UA 返回微信验证页，随后通过本机 Chrome headless 等价浏览器读取标题、作者、公众号、发布时间和正文。公开内容用于参考 `product-insight-analyst.md` 中产品洞察与机会雷达：资料资产化、客户/竞品/标杆三类情报分拣、证据与推理链、机会雷达、宁缺毋滥和产品负责人决策边界；不复制原文、模板正文、固定路径、外部 Skill 名称体系、作者表达或标题传播话术。
- 微信公众号文章《有了洞察还不够，产品负责人真正值钱的是 Backlog 决策》：`https://mp.weixin.qq.com/s/stj1HjCpaG5PzXhxfxlWSg`。作者为 `糖糖`，公众号为 `产品AI力学`，发布时间为 2026-04-10 07:30:00 Asia/Shanghai；2026-06-03 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未执行 Playwright 等价浏览器取证。公开内容用于参考 `po-backlog-manager.md` 中洞察/机会清单到 Backlog 的收敛：BV/EE、业务/用户/工程三桌校验、P0/P1/P2、User Story、AC、技术现实主义、拒绝或延后理由和决策偏好自检；不复制原文图片、外部 Skill 名称体系、作者表达、标题传播话术或前置文章内容。
- 微信公众号文章《现在我敢评测这个 skill 了，产品负责人来看看这个自评卡吧》：`https://mp.weixin.qq.com/s/ZUwtGYYTzt-c2YRXn8ryJw`。作者为 `糖糖`，公众号为 `产品AI力学`，发布时间为 2026-05-02 10:00:00；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文；本轮未再执行 Playwright 等价浏览器取证，后续如需精确引用原文或图片应重新浏览器核验。公开内容用于参考对 `ai-shaped-readiness-advisor` 的产品负责人视角评测：该 Skill 值得读但不宜原样推广，应把 AI-shaped、Context Design、Agent Orchestration、Outcome Acceleration、Team-AI Facilitation 和 Strategic Differentiation 翻译为团队可执行、可复盘、可担责的产品工作语言；不复制原文表达、图片、自评卡排版、作者类比或外部工具营销。
- GitHub 仓库 `deanpeters/Product-Manager-Skills` 中的 `ai-shaped-readiness-advisor`：`https://github.com/deanpeters/Product-Manager-Skills`，原始文件入口 `https://raw.githubusercontent.com/deanpeters/Product-Manager-Skills/main/skills/ai-shaped-readiness-advisor/SKILL.md`。2026-06-01 已读取公开 `SKILL.md`，其定位为 15-20 分钟交互式 AI 产品组织成熟度评估，覆盖 Context Design、Agent Orchestration、Outcome Acceleration、Team-AI Facilitation 和 Strategic Differentiation。本仓库只吸收“区分 AI 提效与工作系统重构、上下文边界、可追溯流程、学习周期、人工责任和差异化指标”的可迁移检查项；当前不安装该 Skill、不复制交互协议、评分 rubrics、示例案例、关联 Skill 链接或外部执行流程。
- 图书《产品经理方法论：构建完整的产品知识体系》及同作者同系列公开书目信息：读书网公开图书页 `https://m.dushu.com/book/13884861/`。该公开页显示作者为赵丹阳，出版社为人民邮电出版社，出版时间为 2021-11-01，ISBN 为 9787115571144；得到公开页面另显示同作者《产品经理方法论》和第2版推荐项等系列线索。2026-06-02 已读取公开图书页、内容简介、作者简介和目录，只按公开书目信息和目录结构做方法校准。本仓库只吸收公开目录呈现的产品经理基础知识体系，覆盖文档分型、流程图、原型图、产品架构图、用户研究、需求管理、数据分析、技术协作、项目管理、行业/商业分析、产品实践、学习方法和职业进阶；不复制书籍正文、章节内容、示例、图表、训练材料或作者表达，也不把基础岗位知识体系替代复杂业务产品架构专家能力。
- 微信公众号文章《B端产品经理实战经验分享系列 - 如何写出高质量的需求文档》：`https://mp.weixin.qq.com/s/_KU0j5sy1HBMdx03bhlYGg`。作者/账号为 `AI产品经理老李`，发布时间为 2026-04-22 08:00；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（Chrome headless）加载取证。公开内容用于参考 B 端需求文档质量治理，覆盖文档目标与受众、PRD/MRD/BRD 类型区分、复杂度裁剪、功能范围、验收标准、版本记录、变更同步和评审闭环；不复制原文案例、指标数字、图片、排版或作者表达，也不把文章中的轻量结构替代本仓库已有产品架构/PRD 模板。
- 微信公众号文章《完整不等于可测：需求评审的四个AI新维度》：`https://mp.weixin.qq.com/s/7EiFz1Oka1tYQmfbBferQg`。作者/账号为 `Maywen测开AI手记`，页面时间字段为 2026-06-08 12:52:41 Asia/Shanghai；2026-06-08 `web.open` 未取得正文，随后通过移动端微信 UA 读取标题、作者、发布时间和正文。公开内容用于参考需求评审前 AI 预扫描的四维检查框架：完整性、一致性、可测试性和二义性，以及“AI 只列疑似问题和追问点，人工过滤、排序和 owner 决策”的边界；不复制原文、效果数字、示例句子、标题传播话术或作者表达，也不把预扫描替代正式需求评审、QA 测试设计或产品 owner 决策。
- 微信公众号文章《别再手工看政策和竞品了，让 AI 帮你做“递归式洞察”》：`https://mp.weixin.qq.com/s?__biz=MzY5MTIxNDA0MQ==&mid=2247483929&idx=1&sn=d832c54aa5a58e0f429d82a969e7f928&scene=21#wechat_redirect`。2026-05-28 普通 curl 返回微信验证页；Browser/Playwright 核验结果为页面加载超时/会话重置，正文不可复核；仅保留为同号历史索引线索，不得作为已吸收来源。
- 搜狗微信搜索《产品AI力学》结果页：`https://weixin.sogou.com/weixin?type=2&query=%E4%BA%A7%E5%93%81AI%E5%8A%9B%E5%AD%A6`。2026-05-28 公开结果页可读取部分同号文章标题与摘要；后续结果跳转和更多正文读取触发反爬/验证页，Browser/Playwright 核验结果为正文不可复核；仅保留为选题分布与历史索引线索，不得作为已吸收来源。
- Impact Mapping 官方图书页：`https://www.impactmapping.org/book.html`。2026-05-28 已读取公开页面；页脚声明站点内容在未另行说明时使用 CC-BY 4.0，公开内容用于参考业务与交付对齐、目标导向规划、把工作拆成仍有业务价值的小块和可适应变化的路线图；本仓库只吸收目标、参与方、行为影响和交付物之间的验证链路，不复制图书内容、图示、海报、工作坊材料或站点资产。
- Dan North 文章《Introducing BDD》：`https://dannorth.net/blog/introducing-bdd/`。2026-05-28 已读取公开页面，公开内容用于参考业务价值、行为、故事模板、场景和 Given / When / Then 验收标准如何连接需求、测试和实现；本仓库进一步落成产品侧验收种子交接矩阵，只保留业务前置条件、触发行为、可观察结果和风险红线的结构化方法；不复制原文、代码示例、ATM 场景或工具实现细节。
- Atlassian Product Requirements：`https://www.atlassian.com/agile/product-management/requirements` 与 Product Requirements 模板页 `https://www.atlassian.com/software/confluence/templates/product-requirements`。2026-05-28 已读取公开页面；公开内容用于参考 PRD 中 assumptions、user stories、success metrics、scope、release 和 open questions 的组织方式；本仓库只吸收假设/待决策、发布后验证和验收追踪槽位，不复制模板正文或示例。
- NN/g 文章《UX Mapping Methods Compared: A Cheat Sheet》：`https://www.nngroup.com/articles/ux-mapping-cheat-sheet/`。2026-06-01 已读取公开页面；公开内容用于参考 empathy map、customer journey map、experience map 和 service blueprint 的适用边界，尤其是按目标用户、场景、时间顺序、前后台触点、支撑流程和证据来源选择图型；不复制文章表格、图示、模板、课程材料或案例细节。
- NN/g 文章《Service Blueprints: Definition》：`https://www.nngroup.com/articles/service-blueprints-definition/`。2026-06-01 已读取公开页面；公开内容用于参考服务蓝图把客户动作、前台动作、后台动作、支撑流程和证据/物料关联到特定用户旅程；不复制文章图示、案例、模板或课程材料。
- draw.io 官方 GitHub 集成文档：`https://www.drawio.com/docs/integrations/github/`。2026-06-01 已读取公开页面；公开内容用于参考可编辑图资产与代码/文档同库维护、GitHub 权限边界和文件大小提示；不复制工具文档、集成步骤或品牌表达。
- NASA SWE-052 Bidirectional Traceability：`https://swehb.nasa.gov/x/AwIfBg`。公开内容用于参考需求、设计、代码和测试之间的双向追踪；本仓库只吸收需求ID、验收种子ID、质量属性ID 和后续验证资产映射，不复制 NASA 流程或表述。
- 《支付之门：支付原理、架构与产品全链路设计》公开图书页：如当当云阅读 `https://e.dangdang.com/products/1901384633.html`。公开简介说明其面向支付系统底层逻辑、会计知识和支付系统设计方法论。
- Formance Wallets Introduction：`https://docs.formance.com/modules/wallets/introduction`。公开文档用于参考业务钱包、余额和钱包操作的分层设计。
- Formance Ledger Introduction：`https://docs.formance.com/modules/ledger/introduction`。公开文档用于参考产品账本、账户、交易、分录和元数据设计。
- Formance Reconciliation Introduction：`https://docs.formance.com/modules/reconciliation/introduction`。公开文档用于参考内部账本与外部资金池、银行或通道数据之间的对账闭环。
- Formance Connectivity Introduction：`https://docs.formance.com/modules/connectivity/introduction`。公开文档用于参考外部支付服务商、银行、开放银行、虚拟账户和现金池连接器设计。
- Formance Numscript Introduction：`https://docs.formance.com/modules/numscript/introduction`。公开文档用于参考受限记账 DSL、规则表达和可审查账务脚本设计。
- Formance Flows Introduction：`https://docs.formance.com/modules/flows/introduction`。公开文档用于参考长事务支付流程、事件等待、重试和补偿编排设计。
- Nacha Operating Rules：`https://www.nacha.org/rules/operating-rules`。公开文档用于参考 ACH Operating Rules、生效日期、规则更新与 ACH 轨道设计边界。
- Nacha Definition of IAT Entries：`https://www.nacha.org/rules/definition-iat-entries`。公开文档用于参考 IAT 与跨境相关 ACH 约束。
- Nacha Risk Management Topics - Fraud Monitoring Phase 2：`https://www.nacha.org/rules/risk-management-topics-fraud-monitoring-phase-2`。公开文档用于参考 2026 年 ACH fraud monitoring、credit-push fraud 和风险监测职责变化；具体适用主体与日期以 Nacha 最新规则为准。
- Visa Core Rules and Visa Product and Service Rules：`https://usa.visa.com/dam/VCOM/download/about-visa/visa-rules-public.pdf`。公开文档用于参考卡组织授权、清算、争议和规则边界。
- Mastercard Rules：`https://www.mastercard.us/content/dam/public/mastercardcom/na/global-site/documents/mastercard-rules.pdf`。公开文档用于参考卡组织规则、争议与网络费用边界。
- Highnote Docs Home：`https://docs.highnote.com/docs/`。公开文档目录，覆盖 issuing、acquiring、money movement、reporting 等产品能力。
- Highnote About Developer Resources：`https://docs.highnote.com/docs/developers/about-developers`。公开文档用于确认 Highnote 的开发者能力面，覆盖 GraphQL API、SDK、Event Notifications 和 Data Share，并说明大多数共享数据在 3 小时内可用。
- Highnote Notifications：`https://docs.highnote.com/docs/developers/events/notifications`。公开文档用于参考 webhook、签名校验、重放标记、幂等处理、异步消费和通知目标生命周期。
- Highnote About Data Share：`https://docs.highnote.com/docs/developers/data-share/about-datashare`。公开文档用于参考 Data Share 的数据面定位和使用边界。
- Highnote Connect to Snowflake：`https://docs.highnote.com/docs/developers/data-share/connect-to-snowflake`。公开文档用于参考 Snowflake 共享接入流程、交付时效和共享数据消费方式。
- Highnote Issuing Data Dictionary：`https://docs.highnote.com/docs/developers/data-share/dictionary-issuing`。公开文档用于参考 issuing 侧 card transaction event、financial event、ledger entry 等数据对象和字段语义。
- Highnote Acquiring Data Dictionary：`https://docs.highnote.com/docs/developers/data-share/dictionary-acquiring`。公开文档用于参考 acquiring 侧 payment order、payment transaction event 和 payout 等数据对象与字段语义。
- Highnote Issuing Overview：`https://docs.highnote.com/docs/issuing/about-issuing`。公开文档用于参考发卡平台、Program、持卡人和卡产品设计视角。
- Highnote Using Ledgers：`https://docs.highnote.com/docs/issuing/accounts/funding/using-ledgers`。公开文档用于参考金融账户下多 ledger、journal entry 和资金事件到账务分录的映射设计。
- Highnote On-demand Funding：`https://docs.highnote.com/docs/issuing/accounts/funding/on-demand-funding`。公开文档用于参考主资金池、子账户实时补资、预算额度与真实余额分离的设计模式。
- Highnote Spend Rules：`https://docs.highnote.com/docs/issuing/spend-controls/spend-rules`。公开文档用于参考授权控制、消费规则和限制模型。
- Highnote Transaction Lifecycle：`https://docs.highnote.com/docs/issuing/transactions/transaction-lifecycle`。公开文档用于参考卡交易事件生命周期拆分。
- Highnote About Reporting：`https://docs.highnote.com/docs/issuing/reporting/about-reporting`。公开文档用于参考报表作为独立数据面、异步生成、字段扩展兼容和事件级报表设计。
- Highnote About Acquiring：`https://docs.highnote.com/docs/acquiring/about-acquiring`。公开文档用于参考收单产品能力分层、支付订单与商户资金视角。
- Highnote Payment Orders：`https://docs.highnote.com/docs/acquiring/payments/payment-orders`。公开文档用于参考支付订单作为收单主对象的建模方式。
- Stripe Radar：`https://docs.stripe.com/radar`。公开文档用于参考支付欺诈识别、风险规则和交易风险运营的产品边界，不作为团队风控模型或合规结论。
- Stripe Disputes Responding：`https://docs.stripe.com/disputes/responding`。公开文档用于参考争议证据、响应流程和 dispute case 运营模式；具体时限和责任以最新通道/网络规则为准。
- Stripe Visa CE 3.0 Disputes：`https://docs.stripe.com/disputes/api/visa-ce3`。公开文档用于参考 card-absent fraud 场景中历史交易、IP、设备、邮箱、地址等可迁移的举证数据元素；具体适用条件以 Visa/通道最新规则为准。
- Stripe Issuing Virtual Cards：`https://docs.stripe.com/issuing/cards/virtual`。公开文档用于参考虚拟卡、持卡人、卡生命周期、PAN/CVC 展示和 PCI 边界。
- Adyen Risk Management：`https://docs.adyen.com/risk-management/`。公开文档用于参考收单风险、交易风控和风险规则治理的产品设计视角。
- Adyen Dispute Defense Requirements：`https://help.adyen.com/en_US/knowledge/risk/dispute-management/what-are-the-specific-defense-requirements`。公开帮助文档用于参考争议 defense material、证据提交边界和敏感材料限制；具体提交要求以最新通道/卡组织规则为准。
- Marqeta Cards API：`https://www.marqeta.com/docs/core-api/cards`。公开文档用于参考发卡处理、卡片对象、虚拟卡和卡生命周期的通用产品设计问题。
- Visa Virtual Card for Business：`https://corporate.visa.com/en/products/virtual-card.html`。公开页面用于参考企业虚拟卡、商业支付、费用控制和按需发卡场景；不替代 Visa 规则、发卡协议或银行合同。
- Mastercard Virtual Cards：`https://www.mastercard.com/global/en/business/large-enterprise/mastercard-corporate-solutions/virtual-cards.html`。公开页面用于参考商业虚拟卡、一次性卡号、支出控制和企业付款场景；不替代 Mastercard 规则或发卡协议。
- 官方监管来源见 `references/regulatory-baseline.md`，优先用于合规、安全、客户资金和数据保护相关判断。

## 提炼边界

- 可以使用公开文章主题、通用支付概念和行业方法，整理成原创工作流、清单和模板。
- 不复制文章正文、付费课程内容、书籍章节、原图、课件、原型或专有案例。
- 不声称技能代表作者本人观点；当用户要求“陈天宇宙怎么说”时，应改为“公开资料中常见的提炼是……”。
- 对当前不可复核、已删除或只剩索引页的文章，不得继续作为已吸收来源；相关能力只能按通用方法、项目事实或其他可核验来源表达，并标明待核验。
- 不把 Formance 的产品模型直接等同于团队架构、行业标准或监管要求；只提炼可迁移的钱包、账本和对账设计模式。
- 不把 Highnote 的产品对象、字段命名或平台流程直接等同于团队架构、卡组织规则或监管要求；只提炼可迁移的卡产品、授权控制、交易生命周期、收单和数据面模式。
- 不把 Stripe、Adyen、Marqeta、Visa 或 Mastercard 的产品能力、字段、API 或商业页面直接等同于团队架构、行业标准或监管要求；只提炼可迁移的风控、争议、发卡、虚拟卡和通道运营设计问题。
- 不把 Airwallex 或其他全球支付厂商的品牌叙事、增长数据、覆盖地区、速度承诺、商业立场、API 字段、状态枚举或国家/币种清单直接等同于行业事实、团队架构或监管结论；只提炼可迁移的全球支付底层控制力、复杂性承接、客户侧确定性、对象建模、状态事件、报表和沙盒验证模式。
- 不把支付账务文章中的实时记账、缓冲记账、单边余额更新、科目层级、错账平衡或人工总账处理方式直接写成强制实现；这些只能作为账务产品和架构设计问题，具体方案必须经过财务、账务负责人和工程负责人确认。
- 不把第三方平台的争议证据字段直接照搬为团队最小必要采集范围；证据日志和证据包必须结合争议原因码、法域、隐私要求、PCI 边界和通道模板裁剪。
- 外部规则具有时效性。引用法律法规、卡组织规则、Nacha/ACH、PCI DSS、银行/通道协议、税务、会计准则、云产品、SDK/API 或外部服务规则时，必须按最新公开来源、官方规则、项目 lockfile、本地依赖树、合同或专业确认结果复核，并记录来源、版本或发布日期、核验日期和确认方。
- 若需要准确引用、最新课程/书籍信息、监管规则或机构政策，必须联网核验并给出来源链接。
- 监管资料优先使用人民银行、全国人大、国务院、网信办等官方来源；第三方索引只用于发现主题，不用于下合规结论。
