# 产品架构专家公开资料来源与提炼边界

本文只维护通用产品架构、产品判断、PRD、业务架构和产品验证来源。支付、资金、卡组织、ACH、VCC、跨境与支付监管来源由 `payment-expert/references/source-map.md` 维护。

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
- 支付资金场景和对应专项 reference 使用 `payment-expert`。
- 合规、监管、外部支付规则与官方来源边界使用 `payment-expert`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核对外部文章是否可吸收 | `读取与归因规则`、`本地证据归档规则` | 不读取整份来源清单 |
| 查找已参考来源和用途 | 先看 `来源主题索引`，再到 `已参考的公开来源` 中按 URL 或主题条目定位 | 不把条目描述当成原文逐字引用 |
| 新增来源或修正来源状态 | `读取与归因规则`、`本地证据归档规则`、`提炼边界` | 不把未抓取正文的文章标为公开内容用于参考 |
| 判断支付专项提炼边界 | `提炼边界`，必要时使用 `payment-expert` | 不把厂商文档、文章观点或第三方索引写成行业标准 |
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

- 支付与资金专项来源：使用 `payment-expert/references/source-map.md`；本文不重复维护支付来源。
- AI / Skill / 通用复杂度：检索“Agent Skills”“代码不再稀缺”“复杂度”“低成本生成”。
- 产品头脑风暴与假设挑战：检索“product-brainstorming”“问题探索”“HMW”“第一性原理”“OODA”“逆向头脑风暴”“假设挑战”。
- AI Native 产品上下文：检索“AI Native”“Product Builder”“业务 dogfooding”“MVP harden”“PRD 可执行上下文”“放下 PRD”“Hardened Candidate”。
- AI 产品发心与定位复盘：检索“置身钉内”“AI 产品发心”“AI 产品定位”“真实工作流”“用户张力”“灰度止损”。
- 模糊需求到可开发系统：检索“从一份模糊需求”“AI 全栈工作流”“内容系统”“多端平台”“结构化需求文档”“业务流”“高保真 HTML 原型”“开发任务”。
- 产品洞察与机会雷达：检索“产品洞察”“需求洞察”“机会雷达”“资料资产化”“客户视角”“竞品视角”“标杆视角”“证据推理链”。
- Backlog 决策与机会收敛：检索“Backlog”“机会清单”“需求池”“BV/EE”“User Story”“AC”“技术现实主义”“三桌校验”。
- 产品判断动作链：检索“pm-skills”“产品判断成流程”“产品动作链”“路线图取舍”“发布复盘”“增长实验”“不只是写文档”。
- AI-shaped 产品工作成熟度：检索“ai-shaped-readiness-advisor”“AI-shaped”“AI-first”“Context Design”“Agent Orchestration”“Outcome Acceleration”。
- 产品经理方法论与基础能力：检索“产品经理方法论”“赵丹阳”“BRD/MRD/PRD”“流程图”“原型图”“产品架构图”“需求管理”“用户研究”“数据分析”。
- 需求分析与产品定义：检索“架构30”“架构思维：需求分析”“根源需求”“产品定义”“产品边界”“稳定点”“变化点”“边界坐标”。
- 产品价值 / 成本函数与业务同质性：检索“所有的技术架构，本质上都是业务架构”“兑现那个问题”“价值函数”“成本函数”“主要矛盾”“业务同质性”“技术平台不是产品”。
- 业务架构规划与项目组合：检索“业务架构到底有什么用”“业务架构规划”“业务能力地图”“战略到项目组合”“能力-项目-系统映射”“投资决策支持”“知识库回流”。
- 需求标准与可验证 PRD：检索“标准不是摆设”“需求标准”“设计标准”“编码标准”“需求是软件的根本”“需求基线”“可验证性”“可追踪性”“衍生需求”。
- 产品 DNA 与规则先行：检索“软件工程最大的 Bug”“系统生长顺序”“产品 DNA”“系统 DNA”“业务不变量”“状态流转”“演化规则”“功能先行、规则后补”。
- 问题核心、概念定名与需求止损：检索“欲读经典，先开心门”“产品的创新｜需求是无止境的吗？”“如何抓住问题的核心？”“概念定名”“价值 / 意义边界”“需求止损”“整体 / 系统 / 科学”。
- 产品图形化与服务蓝图：检索“用户旅程”“服务蓝图”“UX mapping”“AI 画图”“draw.io”。
- 需求分析与设计基础：检索“功能定义”“功能分配”“需求分析”“设计活动”“可见价值行为”。
- AI 辅助 PRD 与问题地图：检索“AI 写 PRD”“用户反馈”“问题地图”“证据强度”。
- PRD 输入模式与低摩擦追问：检索“Digital--PRD-SKILL”“从零构思”“优化已有 PRD”“增量需求”“字段规范”“异常处理”。
- 产品合议评审与多 Agent PRD：检索“产品大师”“MAGI”“多 Agent”“PM Reviewer Controller”“合议评审”“AI 生成 PRD”。
- 概念生命周期与退役：检索“架构腐朽”“Loop Engineering”“概念膨胀”“事实源分裂”“只加不减”“旧规则退役”“可删除性”。
- PRD 文档质量治理：检索“高质量需求文档”“PRD/MRD/BRD”“版本管理”“评审机制”。
- 需求评审 AI 预扫描与决策收敛：检索“完整不等于可测”“需求评审”“完整性”“一致性”“可测试性”“二义性”“AI 预扫描”“评审入口”“待决策队列”。
- 领域命名与工程可读性：检索“代码注释”“可读性重构”“领域术语”“业务命名”“注释债”。
- 通用产品架构与业务驱动验证：检索“Impact Mapping”“BDD”“业务目标”“验收场景”“产品到架构交接”。
- PRD 模板与发布验证：检索“Atlassian PRD”“assumptions”“success metrics”“release criteria”“bidirectional traceability”。
- 官方规则与监管：检索“Nacha”“Visa Core Rules”“Mastercard Rules”“监管来源”，并继续使用 `payment-expert` 核验。

## 已参考的公开来源

- W3C《Web Content Accessibility Guidelines (WCAG) 2.2》：`https://www.w3.org/TR/WCAG22/`。2026-08-21 已读取公开规范，吸收 Web/移动 Web 的键盘可用、焦点顺序、焦点不被遮挡、内容重排（reflow）、输入方式和目标尺寸检查项，用于 `product-client-interaction.md` 的体验验收；不把 WCAG 合规等级等同于产品可用性、视觉质量或上线批准。
- Apple《Human Interface Guidelines - Layout》《Accessibility》：`https://developer.apple.com/design/human-interface-guidelines/layout`、`https://developer.apple.com/design/human-interface-guidelines/accessibility`。2026-08-21 已读取公开页面，吸收跨窗口/方向/安全区/动态字体/多输入方式、层级、渐进披露、平台控制尺寸与可访问性检查项；不复制 Apple 组件、素材、token 或把 iOS/macOS 约束外推到其他平台。
- Material Design 3《Canonical layout examples》与 Android Developers《Design an Adaptive Layout with Material Design》：`https://m3.material.io/foundations/layout/canonical-examples/overview`、`https://developer.android.com/codelabs/adaptive-material-guidance`。2026-08-21 已读取公开页面，吸收按窗口可用空间和人体工学选择断点、列表-详情/多栏等布局策略、在断点之间保持弹性和系统栏上下文的检查项；不把 Material 的窗口尺寸、组件或 Compose 实现当作本项目标准。
- Microsoft Fluent 2《Layout》《Design principles》：`https://fluent2.microsoft.design/layout`、`https://fluent2.microsoft.design/design-principles`。2026-08-21 已读取公开页面，吸收 responsive/adaptive 的区别，以及重排、缩放、显隐和重构页面结构的适配决策；不复制 Fluent 的设计语言、token、断点或组件实现。
- web.dev《Introduction to responsive design》《Accessible responsive design》：`https://web.dev/learn/design/intro`、`https://web.dev/articles/accessible-responsive-design`。2026-08-21 已读取公开页面，吸收移动视口、流式布局、内容驱动的响应式和可访问响应式检查项；不把教程示例或浏览器实现细节当作产品事实。

- 支付课程、支付公众号文章与全球支付厂商来源已迁移到 `payment-expert/references/source-map.md`；未带正文读取证据的旧条目不再作为产品专家已吸收来源。
- 微信公众号文章《代码不再稀缺，稀缺的是你如何对抗复杂度》：`https://mp.weixin.qq.com/s/TxU2D0Plf__Xh-yUD2zjPA`。2026-05-26 已尝试 Playwright，当前浏览器通道加载为空白；随后通过公开 HTML 读取到标题、作者、发布时间和正文，公开内容用于参考 AI 代码生成时代实现成本下降、复杂度/注意力成本上升、系统设计、前置约束和问题定义能力的重要性；只吸收问题框架和能力定位，不复制原文或作者表达。
- 微信公众号文章《放下 PRD：写给AI Native时代的产品经理朋友们》：`https://mp.weixin.qq.com/s/5TEAxFYueNc6MD5ngKEgGg`。作者/账号为 `大数据随笔`，发布时间为 2026-05-25 18:00:00；2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未再执行 Playwright 等价浏览器取证。公开内容用于参考 AI Native 下 PRD 从静态翻译文档转为可运行证据、对象规则、验收种子和工程交接门禁的上下文包，覆盖 Product Builder、业务 owner + Agent、业务 dogfooding、MVP/原型 harden 和产品侧交接；端到端 GSD/CAD 准入与 AI 工具编排交给 `wise-agent`，不复制原文、标题表达、作者判断、引用案例、传播性措辞或岗位评价，也不把“放下 PRD”理解为跳过产品语义、评审、留痕、合规和验收。
- 微信公众号文章《软件工程最大的 Bug：我们把系统生长顺序做反了》：`https://mp.weixin.qq.com/s/YM0BI6tCXLpwEf8hZuYvYA` 与《为什么优秀架构越来越像生命？》：`https://mp.weixin.qq.com/s/95YFNicYQnDRt9SZHrpKnQ`。作者/账号均为 `霍旭东` / `ThinkingInDev`，页面时间字段分别为 2026-06-08 20:19:14 与 2026-06-09 07:00:00 Asia/Shanghai；2026-06-11 首篇 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考 `product-architecture-methodology.md` 的产品 DNA、核心对象、业务不变量、生命周期 / 状态、责任边界、演化规则、验收方式和“功能先行、规则后补”反模式，以及 `product-prd-template.md` 的产品 DNA 卡；不复制原文、图片、比喻、标题传播话术、作者表达或“数字生命”推测，也不把产品 DNA 写成替代用户研究、业务 owner 确认、合规确认、系统设计或 Execution Grant。
- 微信公众号文章《所有的技术架构，本质上都是业务架构》：`https://mp.weixin.qq.com/s/4mOd-ZbtE-J6O-aDPOSUQg` 与《兑现那个问题“产品需要做什么”》：`https://mp.weixin.qq.com/s/dHXUnZI6rVGYqpyqPnjo4w`。作者字段均为 `大象无棱`，页面时间字段分别为 2026-04-25 09:32 与 2026-06-10 09:11 Asia/Shanghai；2026-06-11 首篇通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文，第二篇普通 `curl` 返回微信验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文。公开内容用于参考 `product-architecture-methodology.md` 的价值 / 成本函数、主要矛盾、用户逻辑、业务同质性、技术平台不是产品、产品到开发语言转译和强行平台化风险；不复制原文、故事经历、比喻、图片、作者表达或标题传播话术，也不把文章观点写成组织制度、客户事实、合规结论或 Execution Grant。
- 微信公众号文章《业务架构到底有什么用？》：`https://mp.weixin.qq.com/s/Xvu7hT4IH8D3BBY2PrTbnA`。账号 / 作者字段为 `企业架构EA之家`，页面 `ct` 字段换算为 2026-07-07 13:50:00 Asia/Shanghai；2026-07-08 普通 `curl` 返回微信“环境异常”验证页，Playwright 等价浏览器通道本轮未能完成可用取证，随后通过 Android MicroMessenger UA 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考 `business-architecture-planning.md` 的共同业务语言、业务能力地图、战略到项目组合、能力-项目-系统映射、投资决策支持、从真实问题切入和知识库回流；不复制原文、图片、作者表达、顾问话术、企业案例或标题传播话术，也不把文章观点写成组织制度、预算审批、系统设计、Execution Grant 或上线审批。
- 微信公众号文章《什么是业务架构？业务架构到底包含什么？》：`https://mp.weixin.qq.com/s/0sYKrBGcN-0kNL_cAy_5Lw`。页面账号 / 作者字段为 `EA韩老师` / `架构实践方法`，发布时间为 2026-08-17 12:25 Asia/Shanghai；2026-08-17 已通过 Codex in-app Browser 读取标题、作者、发布时间和正文。公开内容用于参考 `business-architecture-planning.md` 区分价值流、业务能力和业务流程，并按决策问题选择最小视图组合；三者只作为参考性工作基线，不写成 BIZBOK、TOGAF、BACM 共同规定的普遍标准、完整元模型或固定交付清单。本轮没有保存可复核的 OMG BACM、TOGAF 或 BIZBOK 官方页面记录，因此不据此写入具体标准结论；不复制文章原文、图片、作者表达、顾问话术或未经核验的标准断言。
- 微信公众号文章《欲读经典，先开心门》：`https://mp.weixin.qq.com/s/qWIVEdD5uSLAQXP7nh1ckA`、《产品的创新｜需求是无止境的吗？》：`https://mp.weixin.qq.com/s/ld3ZqgNL_wJcOCUQz6em2Q`、《一阖一辟谓之变，往来不穷谓之通｜变通》：`https://mp.weixin.qq.com/s/H6dCG9d_RTBHLlKKtMse_Q` 与《如何抓住问题的核心？》：`https://mp.weixin.qq.com/s/AMdz3s4GEPDgNibPlq8_2g`。页面账号字段为 `心性之学`，后三篇作者字段为 `复闲`；页面时间字段分别为 2025-11-21 10:23:51、2025-01-09 05:02:37、2025-05-06 02:29:50、2025-12-19 19:13:26 Asia/Shanghai；2026-06-12 本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文，其中首篇正文主体来自页面 meta / JS 描述字段。公开内容用于参考 `product-architecture-methodology.md` 的概念定名、需求止损、价值 / 意义边界、整体 / 系统 / 科学三层问题诊断，以及 AI 辅助产品输出前的反脑补证据边界；不复制原文、经典引文、医学/文化论断、作者表达、图片、标题传播话术或个人修习语境，也不把传统文化或医学观点写成产品事实、用户研究结论、Backlog 决策、合规结论或 Execution Grant。
- 微信公众号文章《阿里内网万言离职书〈置身钉内〉原文，已刷屏》：`https://mp.weixin.qq.com/s/_D20O0vpPXjSzjAKJmBYuA`。作者为 `Corgi/滕雅辛`，公众号为 `爬梯意外簿`，发布时间为 2026-06-05 16:21；2026-06-07 普通 `curl` 返回微信“环境异常”验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、账号、作者、发布时间和正文，页面正文声明内容由 AI 识图整理，故只作为公开转述/OCR 复盘材料。公开内容用于参考 `product-architecture-methodology.md` 中 AI 产品发心、定位、用户张力、真实工作流、灰度止损和反模式门禁；不复制原文、项目细节、组织评价、作者表达或标题传播话术，也不把文章内容写成钉钉/ONE 官方事实、行业结论或产品成败定论。
- 微信公众号文章《从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战》：`https://mp.weixin.qq.com/s/HzbdrmNkT-OTRKdQh0c0Ug`。作者/账号为 `KEEN的创享`，发布时间为 2026-06-04 21:39；2026-06-07 普通抓取返回微信验证页或无正文，随后通过移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文。公开内容用于参考 `product-architecture-methodology.md` 中模糊需求到内容/多端系统的结构化需求、业务流、对象规则、原型说明和开发交接秩序；不复制原文、项目案例、页面设计、提示词、图片或作者表达，也不把文章示例项目写成通用产品模板。
- 微信公众号文章《`product-brainstorming` Skill 原文中文版》：`https://mp.weixin.qq.com/s/cz-9HnmlC_VNcVpdd_e0Vw`。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `进击的肖恩`，既有账号线索保留 `AIML实验室`，页面时间字段为 2026-04-21。正文标注原始文件为 `knowledge-work-plugins/product-management/skills/product-brainstorming/SKILL.md` 并给出 GitHub 仓库链接；本轮尝试读取 GitHub raw 原始 `SKILL.md` 未及时返回，因此只把微信译文作为已读公开材料，原始 GitHub 作为待进一步核验线索。公开内容用于参考 `product-architecture-methodology.md` 的产品头脑风暴纪律：问题探索、方案发散、假设挑战、HMW、第一性原理、类比、反转、OODA 和逆向头脑风暴；不复制原文角色提示、问题清单、外部 Skill 结构或作者表达，也不把头脑风暴输出直接写成 PRD、Backlog 或研发任务。
- 微信公众号文章《放下代码：AI Native是通往架构师的快车道》：`https://mp.weixin.qq.com/s/fhEzrPbeez-_2bmJHqExCQ`。作者/账号为 `大数据随笔`，发布时间为 2026-05-23 12:00:00；2026-06-02 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未再执行 Playwright 等价浏览器取证。公开内容用于参考 `资深架构师` AI Native 架构师工作面；产品专家只借鉴其与产品上下文交接相关的 harden 思路，不复制原文、引用案例、岗位判断或作者表达。
- 微信公众号文章《架构师必备--让AI画架构图》：`https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg`。作者/账号为 `方兴集`，发布时间为 2026-04-30 16:28:31；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（本机 Chrome headless）加载取证但返回异常。公开内容用于参考 AI + draw.io 的自然语言生成、文档转图、图像参考、版本历史、可编辑 draw.io XML 和本地模型/凭据边界；不复制原文示例图、提示词、项目安装说明、工具宣传语或作者表达，也不把具体工具能力写成产品图质量结论。
- 微信公众号文章《架构30：架构思维：需求分析》：`https://mp.weixin.qq.com/s/B8Rap_MmAKmVN3f7eAnvCw`。作者字段为 `开心就好TF`，页面时间字段为 2026-06-07 09:34:00 Asia/Shanghai；2026-06-09 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文（发布时间取页面时间字段）。公开内容用于参考 `product-architecture-methodology.md` 与 `product-design-and-prd.md` 中根源需求、产品定义、产品边界、上下游分工、稳定点 / 变化点和边界坐标门禁；不复制原文、案例、作者表达、标题传播话术或时间投入比例，也不把文章观点写成组织制度、项目事实或执行授权。
- 微信公众号文章《[013] 标准不是摆设——需求标准、设计标准、编码标准怎么写》：`https://mp.weixin.qq.com/s/W44YHT-9bUCrSjsrZIYItw`；《[014] 85%返工都是需求的锅——为啥说需求是软件的根本》：`https://mp.weixin.qq.com/s/MO8EsLHm9QNauNLDQ1Z05Q`。作者/账号字段为 `AIIIIlIIII`，页面时间字段分别为 2026-05-23 07:24:00 与 2026-05-26 06:21:00 Asia/Shanghai；2026-06-09 首篇 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考 `product-prd-quality-gates.md` 与 `product-design-and-prd.md` 的需求条目标准、图文追踪、系统/外部需求未确认不下钻、衍生需求、可验证性和可追踪性门禁；不复制原文、适航/DO-178C 语境、标题比例、作者表达、案例或标准条文，也不把文章观点写成产品团队制度、合规结论或执行授权。
- 微信公众号文章《编写高质量代码注释与可读性重构指南》：`https://mp.weixin.qq.com/s/oDZRKB4rNlIrgbuP-qDbDA`。作者字段为 `techfightyang`，账号字段为 `秋之筠的技术哲思`，页面 `ct` 字段转换为 2026-06-13 21:14:40 Asia/Shanghai；2026-06-16 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考产品上下文交接中的领域术语、业务命名建议、规则名、状态名、异常名和验收种子，减少下游工程只能靠注释解释未命名业务规则的注释债；不复制原文、代码示例、表格、作者表达或标题传播话术，也不把产品命名建议替代架构师模块/类/接口设计、代码 CR 或验证证据。
- 微信公众号文章《需求分析和设计活动关键要点总结》：`https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q`。作者为 `常识`，公众号为 `软件需求分析和设计`，发布时间为 2026-05-26 10:29:23；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（本机 Chrome headless）加载取证。公开内容用于参考功能定义、功能分配追溯、需求分析外部视角和设计内部视角的分工；不复制原文中的 GJB 章节表述、推荐书目、课程机构推荐或作者表达，也不把军标/适航语境写成通用产品强制流程。

- 微信公众号文章《Agent Skills 实战：把 PRD 需求文档写成 Skill》：`https://mp.weixin.qq.com/s/IvaaVh_li9ysvghSjUjnhQ`。公开内容用于参考 PRD Skill 化、团队模板清单化、生成/补全/符合性评审双模式、必填章节检查、用户故事/验收标准可验证性和 scripts/reference 分层；不复制原文模板或另建重复 PRD Skill。
- 微信公众号文章《Copilot 需求交付 Skill 如何实现数据需求24h交付》：`https://mp.weixin.qq.com/s/7JI5zJdT73OFbI-DVl3Oqg`。作者为 `冷星`，账号为 `大淘宝技术`，发布时间为 2026-07-20 14:44；2026-07-24 常规网页读取未取得正文，随后通过 Codex in-app Browser 的 Playwright 等价浏览器接口读取标题、作者、发布时间和正文。公开内容用于参考 PRD 与 SQL 之间的数据语义契约、阶段结果作为可恢复交接物、稳定口径/实时元数据/场景决策分层和关键决策人工门禁，并落实到既有数据产品 PRD 附录；不复制 P1-P4 命名、目录结构、提示词或作者表达，不引入 DataWorks/MaxCompute 依赖，也不把作者自述的 24 小时交付和效率提升写成 SLA 或已验证效果。
- 微信公众号文章《产品经理的PRD写作武器：一个Skills让写PRD从3小时缩到3分钟》：`https://mp.weixin.qq.com/s/qRv1Qe3GjQ_jbQqWGQcHfQ`。2026-05-27 普通 curl 返回环境异常验证页；随后通过移动端微信 UA 公开 HTML 读取到标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（Chrome headless）加载取证，公开内容用于参考 PRD 作为产品思考结构、模糊需求连续追问、原型/HTML/页面截图/交互稿反推 PRD、需求 ID、优先级、文档状态和评审清单；不复制原文模板、安装说明、外部 Skill 结构或效率营销表述。
- 微信公众号文章《产品经理别再只让 AI 写 PRD 了，先把用户反馈整理成一张问题地图》：`https://mp.weixin.qq.com/s/sY6cw6wE5ePyrZmRYbXApg`。2026-05-28 普通 curl 初始因沙箱 DNS 失败；随后通过移动端微信 UA 公开 HTML 读取到标题、作者、发布时间和正文，并已尝试 Browser/Playwright 等价浏览器加载取证但页面加载超时/会话重置。公开内容用于参考 AI 辅助 PRD 前的用户反馈证据整理、问题地图、原始反馈到真实问题的转换、证据强度和潜在机会字段，以及 AI 初稿的人工判断门禁；不复制原文表格、图片、作者表达或外部工具营销。
- 微信公众号文章《产品经理别一上来写 PRD，先想清这 9 件事》：`https://mp.weixin.qq.com/s/D04Ty2kQoSqedbSBENPjmQ`。作者 / 账号字段为 `硬件产品的AI实践`，发布时间为 2026-07-07 21:31；2026-08-19 已通过 Codex in-app Browser 的 Playwright 接口读取标题、账号、发布时间和正文。公开内容用于参考 PRD 前先判断产品定位、商业成立条件、核心用户 / 非用户、核心场景 / 当前替代方式、关键触点与断点、产品阶段 / 阶段证据、资源取舍和验证回流，并落实到既有 `product-judgment-action-chain.md` 的前置门禁与输出卡；不复制原文、图片、作者表达或九步排布，不新增固定九步模板或平行 Skill，也不把文章观点写成用户证据、商业成立结论、优先级裁决或上线效果证明。
- GitHub 仓库 `liuzhaowei1/Digital--PRD-SKILL`：`https://github.com/liuzhaowei1/Digital--PRD-SKILL`。2026-07-30 已读取公开 `README.md`、`SKILL.md` 和 `references/prd-template.md`，核验提交 `cf38ae2`，许可证为 MIT。公开内容用于参考从零构思、优化已有 PRD、既有产品增量需求三种输入模式，两阶段范围确认、带建议答案的低摩擦追问，以及界面需求中用户路径、状态、字段语义、文案反馈和异常恢复等易漏项。本仓库不安装或复制该 Skill，不新增概念 PRD 事实源，不采用固定功能批次和固定文件名，也不把技术栈、数据模型、API 或 Agent 禁行规则写入正式 PRD；工程控制继续归系分、Spec / Harness 与 `wise-agent`。该仓库未提供 scripts、fixtures 或行为验证资产，其 README 对上游视频和 Leader 经验的归因本轮未独立核验。
- 微信公众号文章《我让3个AI吵了一整天架，它们把PRD写完了》：`https://mp.weixin.qq.com/s/13wn5wS8AwyMNBrMQpTyEg`。作者为 `Kira2red`，账号为 `产品异兽 Prod.Monster`，发布时间字段为 2026-05-17 10:05:10 Asia/Shanghai；2026-06-05 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未执行 Playwright 等价浏览器取证。公开内容用于参考 `product-deliberation-workflow.md` 中复杂 PRD、AI 生成方案和原型候选的产品合议评审：Controller / PM / Reviewer 工作位、强制阶段门、用户确认点、指定 Skill / 模板约束、SOP、复杂度评估、类型分流、分批产出和准出检查；不复制原文、图片、外部平台工具调用、watchdog 脚本、车载专项规则、作者表达或标题传播话术。
- GitHub 仓库 `Kira2red/magi-product`：`https://github.com/Kira2red/magi-product`。2026-06-05 已读取公开 README、仓库文件树、`部署包-product-master/SKILL.md`、`lead-pm-prompt.md` 和 `reviewer-prompt.md`。本仓库只吸收三角色产品工作位、阶段确认、证据审查、PRD 类型判定、分批产出、格式门禁和上下文污染防范的可迁移方法；不复制 OpenClaw/Hermes 专属命令、外部 delegate_task 机制、/tmp 标记、watchdog 脚本、车载国标细节、Demo 代码陷阱或长 prompt。
- GitHub 仓库 `Kira2red/Kira-product-monster-skills`：`https://github.com/Kira2red/Kira-product-monster-skills`。2026-06-05 已读取公开 README、仓库文件树、`Kira-product-monster-prd/SKILL.md`、`Kira-product-monster-featurelist/SKILL.md`、`2red-product-whitepaper/SKILL.md`、`Kira-product-monster-prd/references/examples.md` 和 `gbg-holy-grail-war/SKILL.md`。本仓库只吸收 PRD 共享层/模块层分离、PRD 类型判定、界面状态与异常覆盖、图形触发条件、验收覆盖、Feature List 颗粒度和白皮书增量维护的检查思路；不复制外部 Skill 结构、README、示例正文，不复制游戏 Skill、纯中文绝对化约束、PlantUML 图片生成要求或产品白皮书全量维护流程。
- 微信公众号文章《为什么你的 AI 只能写总结，别的产品经理已经用AI在挖需求机会了？附skill模板和调试方法》：`https://mp.weixin.qq.com/s/jsuVbuvKJxEXl8dZyzh23g`。作者为 `糖糖`，公众号为 `产品AI力学`，发布时间为 2026-04-23 19:30:00 Asia/Shanghai；2026-06-03 普通 curl/mobile UA 返回微信验证页，随后通过本机 Chrome headless 等价浏览器读取标题、作者、公众号、发布时间和正文。公开内容用于参考 `product-insight-analyst.md` 中产品洞察与机会雷达：资料资产化、客户/竞品/标杆三类情报分拣、证据与推理链、机会雷达、宁缺毋滥和产品负责人决策边界；不复制原文、模板正文、固定路径、外部 Skill 名称体系、作者表达或标题传播话术。
- 微信公众号文章《有了洞察还不够，产品负责人真正值钱的是 Backlog 决策》：`https://mp.weixin.qq.com/s/stj1HjCpaG5PzXhxfxlWSg`。作者为 `糖糖`，公众号为 `产品AI力学`，发布时间为 2026-04-10 07:30:00 Asia/Shanghai；2026-06-03 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未执行 Playwright 等价浏览器取证。公开内容用于参考 `po-backlog-manager.md` 中洞察/机会清单到 Backlog 的收敛：BV/EE、业务/用户/工程三桌校验、P0/P1/P2、User Story、AC、技术现实主义、拒绝或延后理由和决策偏好自检；不复制原文图片、外部 Skill 名称体系、作者表达、标题传播话术或前置文章内容。
- 微信公众号文章《pm-skills：让产品判断成流程》：`https://mp.weixin.qq.com/s/LR6GB8m9lUSfJGZxUweg-g`。作者 / 账号字段为 `哒哒fan`，页面 `ct` 字段换算为 2026-06-20 10:23:21 Asia/Shanghai；2026-07-02 本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考“产品工作的问题不是缺文档，而是访谈、竞品、路线图、PRD、发布和增长中的判断散落各处”的可迁移方法，并落实为 `product-judgment-action-chain.md` 的证据、判断动作、取舍结论、不做项、下一产物、owner、验收和回流；不复制原文、图片、作者表达、标题传播话术、workflow 数量、工具宣传或示例材料，也不把 AI 文档生成替代产品 owner 判断。
- 微信公众号文章《未来产品团队，不再按岗位分工》：`https://mp.weixin.qq.com/s/DlHRKwuaR_MRD2N0UtngIQ`。账号 / 作者字段为 `AI 干货拆解`，页面显示发布时间为 2026-06-30 21:20 湖北；2026-07-07 普通 `curl` 返回微信“环境异常”验证页，随后通过 Codex in-app Browser 读取标题、作者、发布时间和 `#js_content` 正文。公开内容用于参考产品专家的“产品阶段与贡献方式诊断”：不按传统岗位机械分工，而按产品生命周期中需要解决的问题判断当前缺原型验证、真实交付、复杂度清扫、增长放大还是可靠维护，并把结论落到产品阶段、团队配比、交接 owner 和验收 / 停止条件；不复制原文、角色原型故事、作者表达、图片、博客二手来源或标题传播话术，也不把五类角色写成固定岗位、组织架构调整建议、招聘标准、绩效结论或工程执行授权。
- GitHub 仓库 `phuryn/pm-skills`：`https://github.com/phuryn/pm-skills`。2026-07-02 已通过 GitHub raw 读取公开 `README.md`；2026-08-21 进一步读取 `skills/product-strategy/SKILL.md`、`skills/opportunity-solution-tree/SKILL.md`、`skills/identify-assumptions-existing/SKILL.md`、`skills/prioritize-features/SKILL.md` 和仓库 MIT License。本仓库只吸收从目标结果到机会、方案、假设与验证的判断链，以及价值、可用性、商业成立、可行性风险的条件式检查；不安装该仓库，不复制固定画布、固定数量、68 个 skills、42 个 workflows、slash commands、plugins 或 PM toolkit，也不把外部优先级公式替代本仓库证据、owner、验收和停止条件。
- Silicon Valley Product Group《Product Model Concepts》：`https://www.svpg.com/product-model-concepts/`。2026-08-21 已读取公开正文。公开内容用于区分产品策略选择关键问题与结果、产品发现验证价值 / 可用性 / 可行性 / 商业成立风险、产品交付以结果而非功能上线衡量；本仓库将其收敛到三层产品判断主轴，不复制原文、课程内容、图示或厂商话术，也不把发现方法写成固定瀑布。
- GOV.UK Service Manual《How the discovery phase works》与《How the alpha phase works》：`https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works`、`https://www.gov.uk/service-manual/agile-delivery/how-the-alpha-phase-works`。2026-08-21 已读取公开正文。公开内容用于参考先理解问题与完整服务旅程、优先验证高风险假设、允许发现阶段得出停止结论，以及用 alpha 试验最有风险的方案假设；不复制英国政府流程、团队配置、检查清单或服务标准，也不把阶段名强制套到所有产品任务。
- Product Talk《Opportunity Solution Trees》：`https://www.producttalk.org/opportunity-solution-trees/`。2026-08-21 已读取公开正文。公开内容用于参考把目标结果、用户机会、候选方案和实验保持可追溯，并要求目标用户、价值主张、结果和研究证据先于方案扩张；不复制图示、课程材料、模板或作者表达，也不把树形画布作为每次交付的固定产物。
- 微信公众号文章《现在我敢评测这个 skill 了，产品负责人来看看这个自评卡吧》：`https://mp.weixin.qq.com/s/ZUwtGYYTzt-c2YRXn8ryJw`。作者为 `糖糖`，公众号为 `产品AI力学`，发布时间为 2026-05-02 10:00:00；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文；本轮未再执行 Playwright 等价浏览器取证，后续如需精确引用原文或图片应重新浏览器核验。公开内容用于参考对 `ai-shaped-readiness-advisor` 的产品负责人视角评测：该 Skill 值得读但不宜原样推广，应把 AI-shaped、Context Design、Agent Orchestration、Outcome Acceleration、Team-AI Facilitation 和 Strategic Differentiation 翻译为团队可执行、可复盘、可担责的产品工作语言；不复制原文表达、图片、自评卡排版、作者类比或外部工具营销。
- GitHub 仓库 `deanpeters/Product-Manager-Skills` 中的 `ai-shaped-readiness-advisor`：`https://github.com/deanpeters/Product-Manager-Skills`，原始文件入口 `https://raw.githubusercontent.com/deanpeters/Product-Manager-Skills/main/skills/ai-shaped-readiness-advisor/SKILL.md`。2026-06-01 已读取公开 `SKILL.md`，其定位为 15-20 分钟交互式 AI 产品组织成熟度评估，覆盖 Context Design、Agent Orchestration、Outcome Acceleration、Team-AI Facilitation 和 Strategic Differentiation。本仓库只吸收“区分 AI 提效与工作系统重构、上下文边界、可追溯流程、学习周期、人工责任和差异化指标”的可迁移检查项；当前不安装该 Skill、不复制交互协议、评分 rubrics、示例案例、关联 Skill 链接或外部执行流程。
- 图书《产品经理方法论：构建完整的产品知识体系》及同作者同系列公开书目信息：读书网公开图书页 `https://m.dushu.com/book/13884861/`。该公开页显示作者为赵丹阳，出版社为人民邮电出版社，出版时间为 2021-11-01，ISBN 为 9787115571144；得到公开页面另显示同作者《产品经理方法论》和第2版推荐项等系列线索。2026-06-02 已读取公开图书页、内容简介、作者简介和目录，只按公开书目信息和目录结构做方法校准。本仓库只吸收公开目录呈现的产品经理基础知识体系，覆盖文档分型、流程图、原型图、产品架构图、用户研究、需求管理、数据分析、技术协作、项目管理、行业/商业分析、产品实践、学习方法和职业进阶；不复制书籍正文、章节内容、示例、图表、训练材料或作者表达，也不把基础岗位知识体系替代复杂业务产品架构专家能力。
- 微信公众号文章《B端产品经理实战经验分享系列 - 如何写出高质量的需求文档》：`https://mp.weixin.qq.com/s/_KU0j5sy1HBMdx03bhlYGg`。作者/账号为 `AI产品经理老李`，发布时间为 2026-04-22 08:00；2026-06-01 已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，并已尝试 Playwright 等价浏览器（Chrome headless）加载取证。公开内容用于参考 B 端需求文档质量治理，覆盖文档目标与受众、PRD/MRD/BRD 类型区分、复杂度裁剪、功能范围、验收标准、版本记录、变更同步和评审闭环；不复制原文案例、指标数字、图片、排版或作者表达，也不把文章中的轻量结构替代本仓库已有产品架构/PRD 模板。
- 微信公众号文章《完整不等于可测：需求评审的四个AI新维度》：`https://mp.weixin.qq.com/s/7EiFz1Oka1tYQmfbBferQg`。作者/账号为 `Maywen测开AI手记`，页面时间字段为 2026-06-08 12:52:41 Asia/Shanghai；2026-06-08 `web.open` 未取得正文，随后通过移动端微信 UA 读取标题、作者、发布时间和正文。公开内容用于参考需求评审前 AI 预扫描的四维检查框架：完整性、一致性、可测试性和二义性，以及“AI 只列疑似问题和追问点，人工过滤、排序和 owner 决策”的边界；不复制原文、效果数字、示例句子、标题传播话术或作者表达，也不把预扫描替代正式需求评审、QA 测试设计或产品 owner 决策。
- 微信公众号文章《Skill资料系列04：需求评审Skill，让AI在评审前找出PRD里的逻辑漏洞》：`https://mp.weixin.qq.com/s/DujdZT4CHVxxa18oNayLBQ`。作者为 `老赵`，账号为 `老赵是个AI产品小白`，页面显示发布时间为 2026-07-23 13:50，浙江；2026-08-27 `web.open` 未取得正文，随后通过 Codex in-app Browser 的 Playwright 等价浏览器自动化读取标题、作者、发布时间和正文。公开内容用于参考评审对象、版本、阶段、重点等入口信息，以及把带锚点、影响、修改建议、owner 和阻断条件的问题收敛为待决策队列；不新建独立需求评审 Skill，不复制原文、完整模板、案例、S0-S3 分级或作者表达，也不把 AI 预扫描替代正式评审、产品 / 专业 owner 决策、QA 测试设计和工程验证；Given / When / Then 仍作为验收种子或执行计划细节，不强制堆入 PRD 主阅读路径。
- 微信公众号文章《高水平工程师都擅长解决“非标问题”》：`https://mp.weixin.qq.com/s/j1NQJDM7wpOOI9sIi2SLPA`。作者字段为 `杨光西`，页面 `ct` 字段为 `1781356080`；2026-06-15 通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，本轮未执行 Playwright 等价浏览器取证，发布时间取页面 `ct` 线索。公开内容用于参考产品专家处理老板、销售、客户、运营或 UED 非标诉求时的责任边界：先定义真实问题、影响面、失败成本、当前替代方式、解决方案假设、验收种子和验证动作，避免退化为传话筒；不复制原文、故事、作者表达、图片或标题传播话术，也不把文章观点写成组织制度、岗位考核结论或执行授权。
- 微信公众号文章《深度思考：架构腐朽 & Loop Engineering》：`https://mp.weixin.qq.com/s/wINKSDQCroWBvf29h567zA`。作者字段为 `lencx`，账号字段为 `浮之静`；2026-06-17 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文（发布时间取页面时间字段 / meta 线索）；2026-06-22 再次通过移动端微信 UA 读取公开 HTML。公开内容用于参考产品专家的概念生命周期与退役：当新旧概念、规则、入口、状态、报表或运营口径长期并存时，必须明确当前事实源、新增 / 替代关系、净增概念数、旧概念关系、收敛/合并/废弃规则、迁移路径、用户/运营/UED 影响、验收种子、下线 owner、复审日期、退役条件和待确认项；不复制原文、图片、比喻、作者表达或标题传播话术，也不把概念退役写成工程删除、数据迁移、公共契约变更、执行授权或上线审批。
- 微信公众号文章《别再手工看政策和竞品了，让 AI 帮你做“递归式洞察”》：`https://mp.weixin.qq.com/s?__biz=MzY5MTIxNDA0MQ==&mid=2247483929&idx=1&sn=d832c54aa5a58e0f429d82a969e7f928&scene=21#wechat_redirect`。2026-05-28 普通 curl 返回微信验证页；Browser/Playwright 核验结果为页面加载超时/会话重置，正文不可复核；仅保留为同号历史索引线索，不得作为已吸收来源。
- 搜狗微信搜索《产品AI力学》结果页：`https://weixin.sogou.com/weixin?type=2&query=%E4%BA%A7%E5%93%81AI%E5%8A%9B%E5%AD%A6`。2026-05-28 公开结果页可读取部分同号文章标题与摘要；后续结果跳转和更多正文读取触发反爬/验证页，Browser/Playwright 核验结果为正文不可复核；仅保留为选题分布与历史索引线索，不得作为已吸收来源。
- Impact Mapping 官方图书页：`https://www.impactmapping.org/book.html`。2026-05-28 已读取公开页面；页脚声明站点内容在未另行说明时使用 CC-BY 4.0，公开内容用于参考业务与交付对齐、目标导向规划、把工作拆成仍有业务价值的小块和可适应变化的路线图；本仓库只吸收目标、参与方、行为影响和交付物之间的验证链路，不复制图书内容、图示、海报、工作坊材料或站点资产。
- Dan North 文章《Introducing BDD》：`https://dannorth.net/blog/introducing-bdd/`。2026-05-28 已读取公开页面，公开内容用于参考业务价值、行为、故事模板、场景和 Given / When / Then 验收标准如何连接需求、测试和实现；本仓库进一步落成产品侧验收种子交接矩阵，只保留业务前置条件、触发行为、可观察结果和风险红线的结构化方法；不复制原文、代码示例、ATM 场景或工具实现细节。
- Atlassian Product Requirements：`https://www.atlassian.com/agile/product-management/requirements` 与 Product Requirements 模板页 `https://www.atlassian.com/software/confluence/templates/product-requirements`。2026-05-28 已读取公开页面；公开内容用于参考 PRD 中 assumptions、user stories、success metrics、scope、release 和 open questions 的组织方式；本仓库只吸收假设/待决策、发布后验证和验收追踪槽位，不复制模板正文或示例。
- NN/g 文章《UX Mapping Methods Compared: A Cheat Sheet》：`https://www.nngroup.com/articles/ux-mapping-cheat-sheet/`。2026-06-01 已读取公开页面；公开内容用于参考 empathy map、customer journey map、experience map 和 service blueprint 的适用边界，尤其是按目标用户、场景、时间顺序、前后台触点、支撑流程和证据来源选择图型；不复制文章表格、图示、模板、课程材料或案例细节。
- NN/g 文章《Service Blueprints: Definition》：`https://www.nngroup.com/articles/service-blueprints-definition/`。2026-06-01 已读取公开页面；公开内容用于参考服务蓝图把客户动作、前台动作、后台动作、支撑流程和证据/物料关联到特定用户旅程；不复制文章图示、案例、模板或课程材料。
- draw.io 官方 GitHub 集成文档：`https://www.drawio.com/docs/integrations/github/`。2026-06-01 已读取公开页面；公开内容用于参考可编辑图资产与代码/文档同库维护、GitHub 权限边界和文件大小提示；不复制工具文档、集成步骤或品牌表达。
- NASA SWE-052 Bidirectional Traceability：`https://swehb.nasa.gov/x/AwIfBg`。公开内容用于参考需求、设计、代码和测试之间的双向追踪；本仓库只吸收需求ID、验收种子ID、质量属性ID 和后续验证资产映射，不复制 NASA 流程或表述。
- GitHub 仓库 `microsoft/hve-core` 的 `requirements-author`：`https://github.com/microsoft/hve-core/tree/main/.github/skills/project-planning/requirements-author`。2026-08-21 已读取公开 Skill 与追踪 reference；2026-08-24 复核当前路径、Skill 1.1、CC-BY-4.0 声明、BRD/PRD 生命周期、需求-验收-目标追踪和 EARS 可选表达。公开内容用于参考稳定 ID、关系姿态、漏追踪检查、原子需求和验收连接；不安装该 Skill，不复制模板、阈值、状态机、平台字段或完整治理流程。
- IREB CPRE Foundation Level Syllabus 3.3.0：`https://hub.ireb.org/media/pages/resources/cpre-foundation-level-syllabus/9c084b1cfd-1787039954/cpre_foundationlevel_syllabus_en_v.3.3.0.pdf`。2026-08-24 实际读取公开 PDF。吸收需求适切、必要、无歧义、自包含、可理解、可验证，以及多需求一致、非冗余、可修改、可追踪等质量维度；吸收短句、统一术语、避免模糊表达和模板不能替代内容判断的边界，不复制课程正文、图表或完整方法。
- Business Rules Manifesto：`https://www.businessrulesgroup.org/brmanifesto.htm`。2026-08-24 实际读取公开正文。吸收规则独立于流程、基于术语和事实、声明式表达、业务可校验和规则间一致性；不复制正文，不引入形式逻辑、规则引擎或规则执行平台。
- OMG DMN 1.5：`https://www.omg.org/spec/DMN/1.5`。2026-08-24 读取官方规范页和公开 PDF 中的决策、输入、知识来源与决策表示例。只吸收复杂规则使用输入、输出、规则行和命中策略的可选表达；不要求所有 PRD 使用 DMN，不绑定工具或实现平台。
- RFC 2119：`https://datatracker.ietf.org/doc/rfc2119/`。2026-08-24 读取 IETF 官方页面。只借用绝对要求、默认要求和可选行为的规范强度分级，并转译为本项目中文约定；不宣称 RFC 写作规则直接适用于所有 PRD。
- Cucumber Example Mapping：`https://cucumber.io/docs/bdd/example-mapping/`。2026-08-24 读取公开正文。吸收故事、规则、具体例子和未决问题的澄清关系；不安装 Cucumber，不强制 Gherkin、固定会议形式或彩色卡片。
- GitHub 仓库 `product-on-purpose/pm-skills`：`https://github.com/product-on-purpose/pm-skills`。2026-08-24 读取 `deliver-prd`、`deliver-acceptance-criteria`、`deliver-edge-cases` 的公开 Skill，仓库声明 Apache-2.0。吸收 PRD、故事级验收和全功能边界场景的职责分离，以及条件式输出；不复制模板、示例、完整 Skill 包或外部记忆写回流程。
- GitHub 仓库 `linyindong/platform-product-skills`：`https://github.com/linyindong/platform-product-skills`。2026-08-24 读取 `platform-prd-builder`、`platform-prd-reviewer` 和 `platform-flow-modeler`。吸收 PM Input Normalizer、把技术问题翻译成业务问题、具体矛盾优先评审和 flow evidence；未单独核验许可证，不复制正文或实现，不安装仓库。
- `mattpocock/skills` 的 `to-prd`：`https://www.skills.sh/mattpocock/skills/to-prd`。2026-08-24 读取 skills.sh 展示的 Skill 正文并核对 GitHub 源仓库。只参考项目领域词汇和现有事实源优先；拒绝“不访谈直接合成”、自动发布 Issue 和自动加标签等越过事实补齐与外部写入授权的行为，不安装该 Skill。

## 提炼边界

- 可以使用公开文章主题、通用支付概念和行业方法，整理成原创工作流、清单和模板。
- 可以吸收 `pm-skills` 的产品判断动作化、workflow 链接和高频场景优先思路，用于串联资料、机会、Backlog、PRD、发布和增长复盘；不得安装、复制或照搬外部 Skill / commands / plugins，也不得让 AI 替产品 owner 做路线图取舍。
- 可以吸收领域术语、业务命名、规则名、状态名、异常名和验收种子对工程可读性的帮助；不得让产品专家替代架构师做模块、类、接口或代码级 Review 判断。
- 可以吸收概念生命周期与退役治理，用于处理概念膨胀、事实源分裂、新旧规则并存、需求只加不减和旧入口下线；不得把产品侧概念退役写成工程删除授权、数据迁移授权、公共契约变更或上线审批。
- 不复制文章正文、付费课程内容、书籍章节、原图、课件、原型或专有案例。
- 不声称技能代表作者本人观点；当用户要求“陈天宇宙怎么说”时，应改为“公开资料中常见的提炼是……”。
- 对当前不可复核、已删除或只剩索引页的文章，不得继续作为已吸收来源；相关能力只能按通用方法、项目事实或其他可核验来源表达，并标明待核验。
- 支付厂商、卡组织、账本、争议证据和全球支付来源的吸收边界由 `payment-expert/references/source-map.md` 维护，产品专家不重复定义。
- 不把外部文章中的经典阅读、传统文化、医学类比、修习语境或作者价值判断写成产品结论；只可吸收概念定名、问题核心诊断、需求止损、价值 / 意义边界和证据边界方法。
- 外部规则具有时效性。引用法律法规、卡组织规则、Nacha/ACH、PCI DSS、银行/通道协议、税务、会计准则、云产品、SDK/API 或外部服务规则时，必须按最新公开来源、官方规则、项目 lockfile、本地依赖树、合同或专业确认结果复核，并记录来源、版本或发布日期、核验日期和确认方。
- 若需要准确引用、最新课程/书籍信息、监管规则或机构政策，必须联网核验并给出来源链接。
- 监管资料优先使用人民银行、全国人大、国务院、网信办等官方来源；第三方索引只用于发现主题，不用于下合规结论。
