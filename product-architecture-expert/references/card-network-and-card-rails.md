# 卡组织与卡支付轨道参考

本文提炼卡组织和卡支付轨道中对产品架构专家最有价值的支付专项设计模式，重点覆盖四方模型、授权清算结算、争议与拒付、tokenization、PCI 边界和费用口径。它不替代 Visa / Mastercard / 银联等卡组织规则、收单协议、发卡协议或法务合规结论。

## 适用场景

- 设计银行卡收单、企业卡、员工卡、虚拟卡、卡钱包、卡支付路由和卡账务系统。
- 设计 card-present / card-not-present、预授权、增量授权、capture、refund、void、chargeback 和 tokenization。
- 设计卡网络相关的支付订单、商户入网、结算、费用和争议处理流程。

## 四方模型

- **持卡人 / Cardholder**
- **商户 / Merchant**
- **发卡行 / Issuer**
- **收单行 / Acquirer**
- **卡组织 / Network**：Visa、Mastercard、银联等，在四方模型中承担规则、网络和清算协调角色。

产品方案必须分别说明：谁承担信用风险、谁承担拒付风险、谁承担商户风险、谁负责客户关系、谁负责争议证据、谁决定 token 生命周期。

## 卡组织网络与三/四方模式

卡组织不是普通通道，它同时提供网络、规则、品牌、路由标识、清算协调和争议规则。产品方案要先识别模式：

- **四方模式**：持卡人、商户、发卡行、收单行通过卡组织网络协作，常见于 Visa、Mastercard、银联等开放网络。
- **三方模式**：同一机构同时承担网络、发卡和收单等角色，规则、账务和商户关系会更集中，但仍要拆分责任边界。
- **卡 BIN / IIN 路由**：卡号前缀、卡品牌、发卡行、卡类型和地区会影响网络路由、费用、风控、汇率和争议规则。
- **专线与前置系统**：卡组织网络往往要求专线、前置、报文协议、认证测试和生产切量流程；不能只按普通 HTTP API 接入理解。

## 卡网络能力栈与角色定位

Mastercard、Visa 等卡网络类产品不能只按“接一个支付通道”设计。产品方案要把它视为一套 payment network + rules + responsibility + billing + governance 的基础设施，并至少拆成五类能力：

- **Transaction processing**：authorization、clearing、settlement、network management、reversal、advice、SAF 等交易处理链路。
- **Participant role**：issuer、acquirer、processor、gateway、sponsor/affiliate、principal member、merchant service provider 等角色和责任。
- **Responsibility management**：dispute、chargeback、retrieval、compliance、data integrity、网络监控和违规责任。
- **Cost and billing**：interchange、scheme fee、switching fee、processor fee、cross-border fee、billing file 和费用追溯。
- **Network governance**：准入、认证、版本升级、测试、参数治理、release window、生产切量和持续监控。

任何“接入 Mastercard / 接入卡组织 / 做外卡收单”的产品方案，先回答当前主体到底是在做 issuing、acquiring、processing、gateway、network enablement 还是 sponsor 模式下的业务协作。角色不同，licensing、certification、数据责任、争议责任、费用承担、清结算边界和运营动作都不同。

## 授权、清算、结算三段式

- **Authorization**：校验可用额度、风控和规则，成功不等于最终入账。
- **Clearing / Presentment**：商户或收单侧提交 Financial Presentment，决定最终入账金额、费用口径、账务责任和后续追溯依据。
- **Settlement**：网络与银行侧完成资金划拨和净额结算。

不要把授权成功当成“支付完成”，也不要把 capture / clearing 成功当成“商户已经收到可用资金”。

跨境卡交易还要额外区分四个口径：交易币种、授权汇率、清算/入账汇率、商户结算币种；卡组织、发卡行、收单行、处理商和平台可能分别产生费用。

## 授权网络与前置裁决

卡授权不是“发卡行批不批”的单次接口调用，而是卡网络交易生命周期的前置裁决层。产品方案要把授权拆成五类问题：

- 交易是否可被网络、收单侧和发卡侧接受。
- 授权占用如何影响持卡人的 open-to-buy、可用额度或可用余额。
- 后续 clearing / presentment 如何匹配原始授权、增量授权、completion 和 reversal。
- 授权数据如何支撑争议、检索、对账、风控和网络监控。
- 失败、超时、迟到响应、网络代理裁决和恢复消息如何进入最终一致性闭环。

授权阶段通常不是正式 posting，也不等于 actual settlement。设计卡授权时，必须区分 authorization request/response、authorization advice、ack/nack、reversal、network management、clearing 和 settlement，避免用单一“授权成功”状态覆盖全链路。

## Stand-In、SAF 与授权恢复

对 Mastercard、Visa 等卡网络类场景，不能把 issuer 超时或不可达简单写成“失败重试”。需要识别是否存在网络侧代理裁决、store-and-forward/advice、reversal 和数据回补机制。产品设计至少说明：

- Stand-In 或等价代理裁决是否由网络规则或发卡方参数允许，触发条件是什么。
- 代理裁决不是默认放行，而是受 issuer 预设参数、账户列表、限额、验证、风控和网络规则约束。
- 当 issuer 响应迟到、未被采用或 stand-in 结果未被采用时，哪条结果是最终有效授权结论，未采用路径如何 reversal。
- SAF / advice 如何把临时授权结果送回 issuer，帮助更新 open-to-buy、velocity、风险视图和账务恢复。
- 未投递 advice、长期未回收结果或参数失准，会影响网络完整性、客户解释、后续授权判断和争议/对账。

产品方案中不要把 stand-in 当普通容灾开关；它是一套需要持续维护的授权代理机制，包括参数治理、响应时效、运营告警、补偿处理和对账闭环。

## 授权数据与生命周期追踪

Trace ID、原始授权关联字段、Original Data Elements、商户/终端/位置字段等不是接口细节，而是授权到清算、撤销、增量授权、completion、争议和对账的生命周期资产。增量授权、预授权完成、撤销和 clearing presentment 需要能回指原始授权；授权数据质量还会影响 fraud detection、clearing match、dispute evidence、network monitoring 和客服解释。

产品方案要提前定义授权数据的生成方、传递方、持久化边界、脱敏边界、对账用途和运营排查用途。不要等到清算、争议或客服阶段才补“关联字段”。

## 授权核心建模

卡授权能力不应落成“卡组织接口层”。如果产品涉及 Mastercard、Visa 或多卡组织扩展，应先定义统一 Authorization Core，再把网络差异放进 scheme adapter。产品方案至少说明：

- **Authorization Lifecycle**：授权请求、批准/拒绝、adopted decision、late response、non-adopted response、advice、reversal、SAF recovery 和最终有效结果。
- **Authorization / Hold / Reference Chain**：授权聚合、authorization hold / reservation、completion、incremental auth、partial capture 和原始授权关联链。
- **Network session boundary**：08xx、sign-on、echo、heartbeat、SAF、network connectivity 和 session lifecycle 属于网络连接边界，不应污染业务授权核心。
- **ISO 8583 semantic carrier**：ISO 8583 是网络语义载体，不是产品对象模型本身；原始报文要转换为 authorization、advice、reversal、SAF recovery 等领域事件。
- **Scheme adapter**：Mastercard、Visa、Diners 或本地网络的字段、原因码、响应码、文件和参数差异放进适配层，核心保留统一状态机、hold 模型、reference chain 和恢复语义。
- **Operational controls**：timeout budget、idempotency / replay、raw message archive、HSM/key lifecycle、issuer-adopted ratio、stand-in ratio、late-response ratio、SAF backlog 和网络参数变更审计。

产品评审时，不要只看“能不能发请求、能不能收到 00 响应”，还要看迟到响应、未采用响应、撤销、补送、重复消息、网络恢复和发卡侧可用额度恢复是否可解释、可追踪、可对账。

## 典型卡交易事件

- 授权成功 / 失败
- authorization advice、ack/nack、network management
- 预授权、增量授权、部分 capture、void / reversal
- 清算入账、退款、争议、拒付、re-presentment、仲裁
- 卡费、网络费、收单费、汇率费、跨境费、争议费

同一笔卡交易通常是多事件链路，必须用事件级模型追踪，不要用单一状态字段覆盖。

## 标准卡交易流程

典型卡交易方案至少要能解释以下标准时序：

1. **支付发起**：商户创建 payment order / payment attempt，采集 PAN 或 token、金额、币种、商户信息和风控上下文。
2. **授权请求**：商户或收单方向卡组织提交 authorization，请求发卡行校验额度、状态、风险和规则。
3. **授权响应**：发卡行批准或拒绝；批准后通常形成 authorization hold / reserved amount，但这仍不是最终入账。
4. **capture / void 决策**：商户根据履约情况做全额 capture、部分 capture、增量授权、void 或超时释放。
5. **clearing / presentment**：商户或收单侧提交清算，带来最终入账金额、费用口径和网络侧正式交易事实。
6. **issuer posting**：发卡侧把清算结果正式入账，并释放、核销或调整之前的授权占用。
7. **network settlement**：卡组织和银行侧完成净额结算，收单侧再进入商户资金可用和商户 payout。
8. **post-transaction events**：交易完成后还可能出现 refund、chargeback、re-presentment、仲裁、费用补记和争议调整。

产品方案里要明确每一步的状态对象、责任方、超时语义和失败动作。尤其要区分：

- authorization success != capture success
- capture / clearing success != merchant payout
- refund != chargeback
- void / reversal != refund

## Clearing Core 与账务承接

Clearing 不是“收一个文件、改一个状态”，而是把授权后的交易转成卡网络正式承认的 financial claim。产品方案要把商户或订单侧的 capture，与网络侧 Financial Presentment 分开建模。

Clearing Core 至少要覆盖四个核心能力：

- **Matching Core**：把 Financial Presentment 绑定到 Authorization Lifecycle、Hold Context 和 Reference Chain，支持一对一、一对多、授权链、迟到清算和异常匹配。
- **ARN / Reference Model**：把 ARN、acquirer reference、retrieval reference、original authorization reference 等设计成生命周期锚点，而不是普通查询字段。
- **Fee & Amount Decomposition**：把 principal、interchange、scheme fee、processing fee、FX、settlement amount、merchant fee 和调整金额拆成结构化口径，避免报表阶段临时补算。
- **Posting Model**：把 clearing 事实翻译为账务/会计可消费的语义事件，例如 Merchant Receivable Event、Network Cost Event、Fee Posting Event、Settlement Preparation Event 和 Correction Posting Event。

匹配结果不要只输出 `matched=true`，而要输出 lifecycle context、amount interpretation、hold completion / release、posting readiness 和 exception classification。匹配失败、金额差异、重复清算、漏清算、迟到清算或引用缺失，应进入异常隔离、人工复核和审计轨迹，而不是直接落账或静默丢弃。

## Settlement 与商户可用资金

Settlement 不是“给商户打一笔款”，而是从网络成员资金结果到商户可用资金的连续链路。外卡收单方案至少拆出五段：

1. **Network member settlement**：卡组织或网络层完成 issuer/acquirer 成员间应收应付和资金义务。
2. **Acquirer receipt and internal settlement**：收单机构或平台接收上游结算资金、结算文件或入账结果。
3. **Platform allocation and netting**：平台按商户、门店、币种、费率、退款、争议和风险规则做清分、扣减和净额计算。
4. **Merchant settlement / payout**：按商户账期、结算模板、reserve、rolling reserve、delayed settlement 和风险策略释放可结金额。
5. **Bank arrival**：实际出款路径完成银行入账或商户可提余额更新。

产品方案要显式区分 gross amount、deductions、net settlement amount、withheld amount、available amount、in-transit amount 和 paid amount。商户问“为什么清算完成还没到账”时，系统应能解释是上游结算、平台清分、商户账期、risk reserve、payout 还是银行到账环节卡住。

## 收单风控闭环

外卡收单风控不是交易前拦截器，而是 merchant onboarding、authorization、capture / fulfillment、settlement、dispute / chargeback 和 merchant operations 的全链路控制体系。

成熟方案应把风险动作落到不同阶段：

- **准入阶段**：主体、BO、MCC、经营网址、商品服务、履约周期、国家地区、禁限售和历史风险。
- **交易阶段**：3DS、AVS/CVV、设备、IP、BIN、速度、金额、国家、商户画像、规则和评分。
- **请款/履约阶段**：高风险订单是否禁止自动 capture、延迟发货、人工复核或补充履约证据。
- **结算阶段**：暂停结算、提高保证金、rolling reserve、delayed settlement、商户风险等级和资金释放条件。
- **争议反馈阶段**：RDR / Ethoca、Inquiry、Retrieval、Chargeback、representment 结果回流规则、模型、商户管理和结算策略。

3DS 是重要认证能力，但不是完整风控体系。产品设计应同时覆盖 rules、scoring、manual review、funds strategy、dispute feedback 和策略效果复盘，避免用单点工具替代风险闭环。

## 常见卡交易分支

- **预授权场景**：酒店、租车、加油、押金等通常先 hold，再做增量授权、部分 capture 或释放剩余金额。
- **部分履约场景**：商户可能只 capture 部分金额，剩余授权释放；要避免把原授权金额直接当最终成交金额。
- **延迟清算场景**：授权批准后较晚才 presentment，期间用户余额和可用额度展示要能自解释。
- **跨境与多币种场景**：authorization 汇率、clearing 汇率、最终记账汇率可能不同，费用也可能分阶段出现。
- **争议场景**：退款路径和 chargeback 路径必须分开建模，证据链、责任方和时限都不同。
- **issuer 超时或不可达场景**：需要说明 stand-in、SAF/advice、reversal、open-to-buy 恢复、未采用响应和最终有效结果。

## Tokenization 与 PCI 边界

- 在线收单和卡钱包场景下，tokenization 不是“锦上添花”，而是敏感数据隔离和风险收敛手段。
- 需要区分 PAN、network token、merchant token、device token 和 vault token 的责任边界与生命周期。
- PCI DSS 范围要在方案中显式表达：哪些系统接触 PAN、哪些只接 token、哪些需要脱敏日志和密钥管理。
- 不要把“拿到 token”误解为“不再需要授权、争议和清算设计”。

## 争议与拒付

- chargeback / dispute 不是普通退款。它是网络规则驱动的逆向资金流程，包含证据提交、时限、责任判断和可能的二次申诉。
- 产品方案要说明 dispute case 对账、账户冻结、商户准备金、证据链和运营处理动作。
- 高风险商户、订阅扣款、CNP 场景和跨境卡交易，需要更明确的争议管理和 descriptor 策略。

## 费用与结算口径

- 要区分 interchange、scheme / network fee、processor fee、MDR、跨境费、汇率加点和争议相关费用。
- “手续费”不能只放一个字段，至少要能表达收单成本、商户收费、平台补贴和净收入。
- 跨币种卡交易要区分交易币种、清算币种、结算币种和记账本位币。

## 设计落地检查

1. 是否区分 cardholder、merchant、issuer、acquirer、network 的职责边界。
2. 是否区分 authorization、clearing、settlement、funds availability 和 merchant payout。
3. 是否覆盖 preauth、incremental auth、partial capture、void、refund、chargeback 等多事件链路。
4. 是否区分 PAN、token 和其各自生命周期、责任边界与 PCI 范围。
5. 是否说明 descriptor、争议证据、拒付责任和商户准备金策略。
6. 是否区分 interchange、network fee、processor fee、MDR 和平台净收入。
7. 是否覆盖跨境卡交易的汇率、跨境费和网络规则差异。
8. 是否把授权视为网络级前置裁决，而不是简单的 issuer approve / decline 接口。
9. 是否覆盖 open-to-buy、authorization hold、completion、reversal、SAF/advice 和 stand-in 恢复闭环。
10. 是否把 Trace ID、Original Data Elements 和授权数据准确性纳入清算、争议、对账和风控生命周期。
11. 是否先识别 issuer、acquirer、processor、gateway、sponsor/affiliate、principal member 等参与角色和责任边界。
12. 是否建立 Authorization Core，而不是把卡组织报文适配层当成交易核心。
13. 是否把 Financial Presentment、Matching Core、ARN / Reference Model、Fee & Amount Decomposition 和 Posting Model 纳入 Clearing Core。
14. 是否区分 network member settlement、平台清分净额、商户可结算、merchant payout 和 bank arrival。
15. 是否把收单风控贯穿准入、交易、请款/履约、结算和争议反馈，而不是只做交易前规则拦截。

## 官方参考方向

- Visa Core Rules and Visa Product and Service Rules：`https://usa.visa.com/dam/VCOM/download/about-visa/visa-rules-public.pdf`
- Mastercard Rules：`https://www.mastercard.us/content/dam/public/mastercardcom/na/global-site/documents/mastercard-rules.pdf`
