# ACH 与银行转账轨道参考

本文提炼 ACH 和银行转账轨道中对产品架构专家最有价值的支付专项设计模式，重点覆盖角色分工、授权与结算时序、退回与更正、跨境差异和运营风险。它不替代银行协议、Nacha Operating Rules、当地支付系统规则或法务合规结论。

## 使用时机

- 设计美国 ACH credit / debit、银行代扣、批量付款、工资代发、平台出金和退款回退。
- 设计银行转账类支付轨道，如本地清算、RTP、FedNow、代理行汇款、SWIFT/GPI、本地代付。
- 设计跨境银行转账、企业付款、供应商付款和高客单价低频支付场景。

## 不适用场景

- 只做卡组织、VCC 或钱包产品时，优先读对应专项 reference。
- Nacha、银行、本地清算网络、跨境报文和代理行规则必须按最新官方规则、协议或合作方确认。

## 读取后必须产出

- 角色分工、授权凭证、提交/结算时序、return/NOC/reversal 语义、批次、trace/reference、Payouts 对象、失败处理和待确认项。

## 需要继续读取的 reference

- 支付总纲读 `payment-methodology.md`；清结算读 `clearing-settlement.md`；争议证据读 `dispute-refund-and-chargeback-operations.md`；风控读 `payment-risk-fraud-and-merchant-operations.md`；跨境读 `global-payment-emerging.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| ACH debit/credit 方案 | 核心角色、关键差异、授权提交与结算时序、ACH 特有设计点 | 跨境代理行细节 |
| ACH return/NOC/reversal | Return/NOC/Reversal 语义、ACH 授权与争议举证日志、设计落地检查 | Payouts 对象模型 |
| 银行转账/本地清算 | 核心角色、银行转账与跨境特有设计点、设计落地检查 | ACH 授权证据细节 |
| Payouts/批量付款 | Payouts 对象模型、授权提交与结算时序、设计落地检查 | dispute 证据扩写 |
| 跨境银行转账 | 银行转账与跨境特有设计点，并读 `global-payment-emerging.md` | Same Day ACH 细节 |
| 争议/证据/风控 | ACH 授权与争议举证日志，并读 `dispute-refund-and-chargeback-operations.md`、`payment-risk-fraud-and-merchant-operations.md` | 普通付款建模 |

## 核心角色

- **发起方 / Originator**：业务上发起付款或收款请求的一方。
- **发起行 / ODFI 或付款银行**：代发起方进入清算网络的一方。
- **接收行 / RDFI 或收款银行**：接收清算结果并记账的一方。
- **清算网络 / Clearing Operator**：例如 ACH Network、本地清算系统、RTP 网络、SWIFT 报文网络。
- **受益人 / Receiver / Beneficiary**：最终收款或被扣款的一方。

产品方案里要分别说明：谁发起、谁承诺支付、谁承担退回风险、谁掌握授权凭证、谁负责网络侧格式和时间窗。

## ACH 与银行转账的关键差异

- ACH 更像批处理清算网络，强调文件、批次、结算窗口、退回和更正机制。
- 实时银行转账更强调即时确认、不可逆、资金实时可用和 24x7 可达。
- 代理行或跨境汇款更强调报文网络、账户网络、资金网络分离，消息到达不等于资金到账。
- 银行转账产品设计不能把“支付已提交”“银行已接收”“清算已完成”“资金已可用”混成一个状态。

## 授权、提交与结算时序

- 对 debit / 代扣类轨道，授权取得、授权留存、授权撤销和争议处理是主线，不只是“收款请求”。
- 对 credit / 代发类轨道，核心在付款指令、余额校验、失败退回、限额和到账通知。
- 对 ACH 类轨道，要区分文件生成时间、提交时间、network 处理时间、settlement date、funds availability 和 return window。
- 对实时银行转账，要区分支付确认、银行接收、收款人可用、异常退回和人工处理窗口。

## Return / NOC / Reversal 语义

- **Return**：网络或接收行拒绝、失败或退回已提交交易，需区分原因码、责任方、时效和重试策略。
- **NOC（Notification of Change）**：账户或路由信息需要更新，不等于交易失败，但需要修改主数据。
- **Reversal**：对错误文件或重复发送等场景的纠正，不应被当作普通退款。
- 产品方案必须区分“失败重试”“退回重发”“更正主数据”“冲正原交易”四种动作，不能用一个“重试”按钮概括。

## ACH 特有设计点

- 批次维度要明确：公司批次、文件批次、条目批次、批次状态、批次重跑和重复提交防护。
- 需要支持 Same Day ACH 与普通批次的时效差异、费用差异和 cut-off 差异。
- 对 IAT、跨境相关或高风险场景，要额外说明合规、信息字段和筛查要求。
- 返回码、未达账、拒付、撤销授权和 disputed debit 要有标准化运营动作。

## ACH 授权与争议举证日志

ACH debit / 代扣场景必须把授权证据作为一等对象设计。可复用 `dispute-refund-and-chargeback-operations.md` 中的 Dispute Evidence Activity Log，但证据包必须按 ACH / 银行转账语义生成，不得套用卡 chargeback 模板。

ACH 证据日志至少覆盖：

- debit authorization 展示版本、确认动作、授权时间、授权主体、授权金额、扣款频次、扣款日期和撤销方式。
- 账户绑定、micro-deposit、instant verification、routing/account 校验、账户持有人匹配和验证结果。
- 授权撤销、取消代扣、退款申请、客服沟通、投诉处理和通知用户记录。
- ACH entry、batch、file、trace number、ODFI/RDFI、settlement date、return code、NOC、reversal 和 retry 决策。
- 对 unauthorized return、disputed debit、administrative return、insufficient funds、account closed 等原因码的差异化处理。

设计原则：

- 前端勾选或点击只能作为辅助证据，不能替代授权凭证、授权文本、服务端确认记录和账户验证结果。
- return、NOC、reversal、refund、retry 必须分开建模；不同动作对应不同规则、时限、账务和用户通知。
- 重试扣款前必须检查授权是否仍有效、return code 是否允许、账户主数据是否被 NOC 更新、是否触发风控或人工复核。
- ACH evidence package 应面向银行、ODFI/RDFI、通道或内部风控调查组织材料，不应直接提交全量行为日志或无关个人信息。
- Nacha Operating Rules、银行协议、ODFI/RDFI 要求和通道规则具有时效性；return code、授权保留和重试限制必须按最新规则核验。

## 银行转账与跨境特有设计点

- 要区分消息网络、账户网络和资金网络，不能把 SWIFT 报文发送成功当作资金到账。
- 跨境场景要额外说明代理行、费用分担方式、汇率、退汇路径、受益人姓名校验和合规材料。
- 高价值转账通常需要更强的审批、反欺诈、白名单、回拨确认和异常冻结机制。

## Payouts 对象模型

参考 Airwallex 等公开全球付款文档时，不要把 Payouts 只理解为“代付接口”。更稳定的产品模型包括：

- **Transfer**：付款指令和状态主对象，承载金额、币种、付款方式、受益人、付款人、外部 reference、费用、预计到账、失败原因和回执。
- **Beneficiary**：受益人和收款账户对象，承载主体信息、银行信息、本地字段、验证状态、可用付款方式和资料版本。
- **Payer**：付款人或出款主体对象，承载平台、商户、企业、内部账户、法域、出款权限和资金来源。
- **Batch Transfer**：批量付款对象，承载批次号、明细数量、金额合计、审批状态、提交状态、部分成功、失败明细和重跑策略。
- **Approval**：付款审批对象，承载审批人、四眼复核、限额、白名单、异常触发、撤销和审计。
- **Confirmation / Receipt**：付款确认、回单或证明对象，承载对外可解释的付款事实，不等同于内部状态字段。

产品设计时要把 transfer、beneficiary、payer、batch、approval 和 confirmation 分开建模。受益人字段、银行清单、地区要求和税务材料具有强时效性，不应写死在通用 PRD 中；应作为 schema / form / ruleset 由官方文档、银行协议或合规确认动态约束。

## 设计落地检查

1. 是否区分发起方、发起行、接收行、清算网络和受益人。
2. 是否区分提交成功、清算成功、资金到账、资金可用和对账完成。
3. 对 debit 场景，是否说明授权取得、留存、撤销和争议处理。
4. 是否区分 return、NOC、reversal、refund 和 retry。
5. 是否有批次号、文件号、网络参考号、业务事件号和防重复机制。
6. 是否说明 Same Day / 普通批次 / 实时轨道在时效和费用上的差异。
7. 是否覆盖失败重试、退回重发、主数据纠正、人工处理和告警。
8. 是否有 ACH 授权与争议举证日志，覆盖授权文本版本、确认动作、账户验证、授权撤销、return code、NOC、reversal 和 retry 决策。
9. ACH evidence package 是否按银行、ODFI/RDFI、通道或 Nacha 规则裁剪，而不是套用卡争议证据包。
10. 跨境或银行转账场景下，是否说明消息网络、资金网络、费用路径和退汇路径。
11. Payouts 场景下，是否拆清 transfer、beneficiary、payer、batch transfer、approval、failure reason、confirmation 和出款对账。
12. 是否说明受益人字段和国家/地区规则如何动态校验，而不是把某一平台 API 字段当成通用模型。

## 官方参考方向

- Nacha Operating Rules：`https://www.nacha.org/rules/operating-rules`
- Nacha Definition of IAT Entries：`https://www.nacha.org/rules/definition-iat-entries`
