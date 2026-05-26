# 公开资料来源与支付专项提炼边界

本文主要约束产品架构专家中支付与资金垂直分支的公开资料来源、引用边界和时效性风险。通用产品架构方法见 `product-architecture-methodology.md`，产品方案与 PRD 结构见 `product-design-and-prd.md`。

## 使用时机

- 需要核对产品专家吸收过哪些公开来源、哪些来源可复核、哪些只能作为历史索引线索。
- 用户要求引用、复盘、对齐或质疑外部文章、厂商文档、官方规则来源时，用本文确认归因边界。
- 新增外部资料、归档本地证据、处理无法抓取或已删除文章时，用本文校准记录口径。

## 不适用场景

- 需要直接产出产品方案、PRD、能力地图、架构图或支付资金方案时，先读对应业务 reference；本文只解决来源可信度和提炼边界。
- 需要最新监管、卡组织、ACH、PCI、银行或通道规则结论时，必须重新联网核验官方来源，不能只依赖本文历史索引。
- 未通过 Playwright 或等价浏览器读取到正文的文章，不得仅凭 URL 或标题写成已吸收内容。

## 读取后必须产出

- 明确来源状态：公开可复核、官方来源、第三方索引、历史索引线索、当前不可复核或本地私有归档。
- 明确可吸收边界：只吸收问题框架、产品检查项、对象关系、流程边界和风险提示，不复制正文、字段清单、规则结论或商业承诺。
- 对无法复核、已删除、付费墙、验证页或正文为空的来源，输出待核验状态和风险，不把它们当作事实依据。

## 需要继续读取的 reference

- 通用产品架构方法读 `product-architecture-methodology.md`。
- 产品方案和 PRD 结构读 `product-design-and-prd.md` 与 PRD 相关拆分 reference。
- 支付资金场景读 `payment-scenario-routing.md`，再按任务读取对应专项 reference。
- 合规、监管、外部规则与官方来源边界读 `regulatory-baseline.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核对外部文章是否可吸收 | `读取与归因规则`、`本地证据归档规则` | 不读取整份来源清单 |
| 查找已参考来源和用途 | `已参考的公开来源` 中对应 URL 或主题条目 | 不把条目描述当成原文逐字引用 |
| 新增来源或修正来源状态 | `读取与归因规则`、`本地证据归档规则`、`提炼边界` | 不把未抓取正文的文章标为公开内容用于参考 |
| 判断支付专项提炼边界 | `提炼边界`，必要时回到 `payment-scenario-routing.md` | 不把厂商文档、文章观点或第三方索引写成行业标准 |
| 需要最新规则或准确引用 | `读取与归因规则`、`提炼边界`，然后重新联网核验官方来源 | 不依赖历史索引直接给确定性结论 |

## 读取与归因规则

- 微信文章等动态页面必须先通过 Playwright 或等价浏览器自动化读取到标题、作者、发布时间和正文，才能写成“公开内容用于参考”。
- 未读取到正文、页面删除、只剩验证页或正文为空的条目，只能标为“当前不可复核”或“历史索引线索”，不得作为已吸收来源。
- 条目中的英文术语、分层名称和能力边界可能是 Skill 为统一输出做的标准化表达，不代表原文逐字表述；需要引用作者原话时必须重新读取正文并核对。
- 从文章吸收的内容只作为产品架构问题、检查项、路由和边界，不作为监管、合同、卡组织规则、财务准则或上线结论。

## 本地证据归档规则

- 对高价值且可能删除的文章，可用 `scripts/archive-source-evidence.py` 将已读取到的本地证据文件归档到仓库外目录，默认 `~/.skill-source-archive/`，或由 `SKILL_SOURCE_ARCHIVE_HOME` 指定。
- 本文件只记录公开索引、读取状态、提炼边界、`archive_id`、`evidence_sha256` 和读取日期等轻量 metadata；不得写入文章全文、原图、截图包、MHTML、PDF、付费内容或大段摘录。
- `archive_id` 只能作为本机私有证据定位符，不代表公开来源仍可访问；需要引用或复核时仍要优先重新读取公开页面或官方来源。
- 删除、验证页、空正文或无法复核的条目，即使存在本地归档，也不得写成“公开内容用于参考”，只能说明归档证据来源、读取日期、当前复核状态和剩余风险。

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
- 微信公众号文章《清算文件迟到 24 小时：财务骂网关之前，该对齐的 5 个问题》：`https://mp.weixin.qq.com/s?__biz=MzI3ODQ1MjQwOA==&mid=2247484523&idx=1&sn=bab6c18e89728feaf921bccbc5cb88d3`。公开内容用于参考外卡/跨境收单清算文件延迟排查，覆盖交易日/清算日/入账结算日、cut-off、processing calendar、时区、ACK/reject、批次 ID、三段链路归因和资金链路事故升级信号。
- 微信公众号文章《外卡收单钱收到了，战争才刚开始》：`https://mp.weixin.qq.com/s?__biz=MzI3ODQ1MjQwOA==&mid=2247484517&idx=1&sn=a171eb833dc25e6e83be75c407ad69ff`。公开内容用于参考外卡收单争议治理，覆盖 Alert / Inquiry / Retrieval / Chargeback / Representment / Pre-arbitration / Arbitration 链路、卡争议与非卡争议分轨、争议率/CB 率红线、止血/组证/representment 决策和反馈回流；Visa/Mastercard 监控阈值、生效日和区域规则以官方资料、收单行或通道合同为准。
- 微信公众号文章《Agent Skills 实战：把 PRD 需求文档写成 Skill》：`https://mp.weixin.qq.com/s/IvaaVh_li9ysvghSjUjnhQ`。公开内容用于参考 PRD Skill 化、团队模板清单化、生成/补全/符合性评审双模式、必填章节检查、用户故事/验收标准可验证性和 scripts/reference 分层；不复制原文模板或另建重复 PRD Skill。
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
- 外部规则具有时效性。引用法律法规、卡组织规则、Nacha/ACH、PCI DSS、银行/通道协议、税务或会计准则时，必须按最新公开来源、合同或专业确认结果复核，并记录核验日期。
- 若需要准确引用、最新课程/书籍信息、监管规则或机构政策，必须联网核验并给出来源链接。
- 监管资料优先使用人民银行、全国人大、国务院、网信办等官方来源；第三方索引只用于发现主题，不用于下合规结论。
