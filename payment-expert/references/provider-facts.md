# 厂商时效事实

读取时机：目标为 Stripe、Airwallex 或 Highnote，且需要对象、状态、事件、scope、版本或报告形态时读取。以下为已读取公开文档的事实性转述，读取日均为 **2026-08-03**；精确契约须在目标账户、环境、endpoint 与版本下复核。不要将这些名称推广为行业通则，也不要复制完整 schema。

## Stripe

- [Payment Intents](https://docs.stripe.com/payments/payment-intents)：`PaymentIntent` 追踪支付生命周期，恢复结账复用同一 Intent 与幂等键；它不等于账务对象或每次确认的 Attempt。
- [PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) 与 [Setup Intents](https://docs.stripe.com/payments/setup-intents)：支付重试和异步 `processing` 属于支付意图生命周期；`SetupIntent` 用于未来凭证设置，不创建 Charge，也不等于零金额支付或未来免认证承诺。
- [PaymentIntent object](https://docs.stripe.com/api/payment_intents/object)：`latest_charge` 只指向最近创建的 Charge，不是完整尝试历史；attempt 级对象或字段必须按目标 API 版本和直接官方文档复核。
- [Charge](https://docs.stripe.com/api/charges/object)、[Refund](https://docs.stripe.com/api/refunds/object) 与 [disputes](https://docs.stripe.com/disputes/how-disputes-work)：Charge、退款、争议和各自的余额影响是关联但独立的事实；单个 Charge 的 BalanceTransaction 不包含后续退款或争议影响，不要覆盖原交易。
- [Connect charges](https://docs.stripe.com/connect/charges)、[Connect webhooks](https://docs.stripe.com/connect/webhooks) 与 [accounts v2](https://docs.stripe.com/connect/accounts-v2/connected-account-configuration)：direct、destination、separate charges and transfers 会改变对象归属与资金路径；平台与 connected-account 事件 scope、对象查询和 v1/v2 责任规则不同，费用、负余额和 KYC 必须按目标配置与合同复核。
- [Balance transaction types](https://docs.stripe.com/reports/balance-transaction-types) 与 [reporting categories](https://docs.stripe.com/reports/reporting-categories)：余额流入流出按 BalanceTransaction 追踪；财务分类优先核对 `reporting_category`，不要把 `type` 直接推广为统一会计分类。
- [Payout reconciliation](https://docs.stripe.com/payouts/reconciliation) 与 [reports](https://docs.stripe.com/reports/select-a-report)：自动 payout 可按关联余额活动分析，手工 payout 不能据此精确推出明细；余额报告与 payout 问题的日期口径不同。
- [Testing](https://docs.stripe.com/testing)：sandbox/live 对象隔离；模拟结果不等于真实网络、结算、Identity 或生产批准。升级 API、SDK 或 webhook endpoint 时复核 [versioning](https://docs.stripe.com/api/versioning)。

## Airwallex

- [Connected accounts](https://www.airwallex.com/docs/connected-accounts/get-started/get-started-with-connected-accounts) 与 [wallets and funds flow](https://www.airwallex.com/docs/connected-accounts/about/wallets-and-funds-flow)：平台和 Connected Account 钱包、各币种余额及能力类型彼此有界；CA Transfer、Charge、Global Account、Conversion 与 Payout 的方向和责任不能合成一个通用 transfer。
- [Global Accounts](https://www.airwallex.com/docs/global-treasury/get-started/global-accounts)：Global Account 经本地清算或 SWIFT 收款进入 Wallet；申请能力或创建请求不等于目标 feature 已支持或账户已同步可用。
- [Payments data model](https://www.airwallex.com/docs/payments/about-airwallex-payments/payments-data-model) 与 [Payment Attempts API](https://www.airwallex.com/docs/api/2024-08-07/payments/payment_attempts)：一个 PaymentIntent 可关联多个 PaymentAttempt；重试保留新 Attempt，读取时该 API 合约为 `2024-08-07`，查询留存不是永久保证。
- [Payment webhooks](https://www.airwallex.com/docs/payments/reference/payments-webhooks) 与 [webhook overview](https://www.airwallex.com/docs/developer-tools/webhooks/webhooks-overview)：授权、捕获、收单结算和钱包入账是不同事实；按原始 body 验签，重复和乱序可能发生，订阅/API 版本须复核。
- [Transfer statuses](https://www.airwallex.com/docs/payouts/transfers/create-a-transfer/transfer-statuses)：在适用版本与轨道下，已观察到的支付状态后仍可能迟到失败；不要将其写成跨厂商终态。
- [FX solution](https://www.airwallex.com/docs/transactional-fx/get-started/choose-your-fx-solution) 与 [Conversion API](https://www.airwallex.com/docs/api/transactional_fx/conversion/api)：Rate 与 Quote 的适用条件不同；Conversion 的取消、修改、成本和账务影响必须按目标版本的直接官方文档复核，不预设为无成本撤销。
- [Transaction reconciliation report](https://www.airwallex.com/docs/banking-as-a-service/reporting/financial-reports/transaction-reconciliation-report) 与 [settlement report](https://www.airwallex.com/docs/payments/payment-operations/reporting/settlement-report)：交易对账、结算批次和报告生成状态有不同口径；读取时交易报告为 `v1.1.0`，报告 schema/账户日期版本须复核并容忍新增字段。

## Highnote

- [Card product basics](https://support.highnote.com/hc/en-us/articles/23090196700173-Card-product-basics)、[financial accounts](https://support.highnote.com/hc/en-us/articles/23258486562061-Financial-account-basics) 与 [account closure](https://support.highnote.com/hc/en-us/articles/28127332635917-Close-a-financial-account)：产品、账户、卡、Pending/Posted 和退款是不同事实层；关户前需处理在途授权/转账、余额、关联卡和未结权益，暂停与永久关闭不可混同。
- [Transaction basics](https://support.highnote.com/hc/en-us/articles/23305971456653-Transaction-basics) 与 [ledgers](https://support.highnote.com/hc/en-us/articles/23332256167949-Highnote-ledgers)：授权、清算、冲正、退款与账本分层；事件名称不是封闭状态机或资金结论。
- [Notifications](https://docs.highnote.com/docs/developers/events/notifications) 与 [Fetching Events](https://docs.highnote.com/docs/developers/events/fetching-events)：通知可能重复、乱序、超时和重试；事件可查询/replay，但不产生业务 exactly-once，留存期须在使用时复核。
- [Reporting](https://docs.highnote.com/docs/issuing/reporting/about-reporting)、[Card Transaction Activity Report](https://docs.highnote.com/docs/issuing/reporting/card-transaction-activity-report) 与 [Ledger Entry Report](https://docs.highnote.com/docs/issuing/reporting/ledger-entry-report)：报表 schema 会演进，应按列名读取并容忍未知列；用 transaction ID 聚合生命周期、financial-event ID 区分财务事件，再关联 ledger entry。单笔、批量和报告各自适用不同判断。
- [Testing](https://docs.highnote.com/docs/developers/api/testing-the-api) 与 [disputes](https://support.highnote.com/hc/en-us/articles/36403730976013-Disputes-and-chargebacks)：Test 可覆盖部分交易情景，仍不等同 Live 或生产；争议临时贷记及撤销会继续改变资金事实。
- [API errors](https://docs.highnote.com/docs/developers/api/error-handling)、[idempotency](https://docs.highnote.com/docs/developers/api/idempotency) 与 [API changes](https://docs.highnote.com/docs/developers/api/status-changes)：mutation 使用稳定 `IdempotencyKey` 并保留 `requestId`；同时处理顶层 GraphQL errors 与 union `UserError`，且不能把 schema changelog 当作事件、报表和 Dashboard 的全平台变更记录。
- [Transfer basics](https://support.highnote.com/hc/en-us/articles/23466535831309-Transfer-basics) 与 [ACH transfer details](https://support.highnote.com/hc/en-us/articles/42192273972621-ACH-transfer-details)：转账类型、方向、时点和 trace number 可作为适配事实；不要据此虚构所有 ACH 都遵循固定 `PROCESSED -> RETURNED` 状态迁移。

这些条目只保留运行时会用到的厂商适配事实；已退役的研究矩阵不是第二权威来源，也不能让 course-enriched 专项 reference 自动变成来源独立能力。若厂商未列于此处、实际版本未知、文档发生变更或事项涉及合同/法域，记录为待确认并由相应 Owner 提供权威材料；不要从本文件推定字段、状态、费用、责任、保留期或报告列。
