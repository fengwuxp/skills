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

## 授权、清算、结算三段式

- **Authorization**：校验可用额度、风控和规则，成功不等于最终入账。
- **Clearing / Presentment**：商户或收单侧提交清算，决定最终入账金额和费用口径。
- **Settlement**：网络与银行侧完成资金划拨和净额结算。

不要把授权成功当成“支付完成”，也不要把 capture / clearing 成功当成“商户已经收到可用资金”。

跨境卡交易还要额外区分四个口径：交易币种、授权汇率、清算/入账汇率、商户结算币种；卡组织、发卡行、收单行、处理商和平台可能分别产生费用。

## 典型卡交易事件

- 授权成功 / 失败
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

## 常见卡交易分支

- **预授权场景**：酒店、租车、加油、押金等通常先 hold，再做增量授权、部分 capture 或释放剩余金额。
- **部分履约场景**：商户可能只 capture 部分金额，剩余授权释放；要避免把原授权金额直接当最终成交金额。
- **延迟清算场景**：授权批准后较晚才 presentment，期间用户余额和可用额度展示要能自解释。
- **跨境与多币种场景**：authorization 汇率、clearing 汇率、最终记账汇率可能不同，费用也可能分阶段出现。
- **争议场景**：退款路径和 chargeback 路径必须分开建模，证据链、责任方和时限都不同。

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

## 官方参考方向

- Visa Core Rules and Visa Product and Service Rules：`https://usa.visa.com/dam/VCOM/download/about-visa/visa-rules-public.pdf`
- Mastercard Rules：`https://www.mastercard.us/content/dam/public/mastercardcom/na/global-site/documents/mastercard-rules.pdf`
