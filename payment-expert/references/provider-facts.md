# 厂商时效事实

读取时机：目标为 Stripe、Airwallex 或 Highnote，且需要对象、状态、事件、scope、版本或报告形态时读取。以下为公开文档矩阵的事实性转述，读取日均为 **2026-08-03**；精确契约须在目标账户、环境、endpoint 与版本下复核。不要将这些名称推广为行业通则，也不要复制完整 schema。

## Stripe

- [Payment Intents](https://docs.stripe.com/payments/payment-intents)：`PaymentIntent` 追踪支付生命周期，恢复结账复用同一 Intent 与幂等键；它不等于账务对象或每次确认的 Attempt。
- [PaymentIntent object](https://docs.stripe.com/api/payment_intents/object)：矩阵读取时默认 API 为 `2026-07-29.dahlia`；`latest_charge` 不是完整尝试历史。`PaymentAttemptRecord` 属于 `2025-12-15.preview` 的 Payment Record 体系，必须隔离并复核。
- [Refund](https://docs.stripe.com/api/refunds/object) 与 [disputes](https://docs.stripe.com/disputes/how-disputes-work)：退款是独立对象，争议会有独立扣款、费用和银行裁决；不要覆盖原交易。
- [Connect webhooks](https://docs.stripe.com/connect/webhooks) 与 [accounts v2](https://docs.stripe.com/connect/accounts-v2/connected-account-configuration)：平台与 connected-account 事件 scope、对象查询和 v1/v2 规则不同；费用、负余额和 KYC 责任须按目标配置与合同复核。
- [Payout reconciliation](https://docs.stripe.com/payouts/reconciliation) 与 [reports](https://docs.stripe.com/reports/select-a-report)：自动 payout 可按关联余额活动分析，手工 payout 不能据此精确推出明细；余额报告与 payout 问题的日期口径不同。
- [Testing](https://docs.stripe.com/testing)：sandbox/live 对象隔离；模拟结果不等于真实网络、结算、Identity 或生产批准。升级 API、SDK 或 webhook endpoint 时复核 [versioning](https://docs.stripe.com/api/versioning)。

## Airwallex

- [Payments data model](https://www.airwallex.com/docs/payments/about-airwallex-payments/payments-data-model) 与 [Payment Attempts API](https://www.airwallex.com/docs/api/2024-08-07/payments/payment_attempts)：一个 PaymentIntent 可关联多个 PaymentAttempt；重试保留新 Attempt，矩阵读取的该 API 合约为 `2024-08-07`，查询留存不是永久保证。
- [Payment webhooks](https://www.airwallex.com/docs/payments/reference/payments-webhooks) 与 [webhook overview](https://www.airwallex.com/docs/developer-tools/webhooks/webhooks-overview)：授权、捕获、收单结算和钱包入账是不同事实；按原始 body 验签，重复和乱序可能发生，订阅/API 版本须复核。
- [Transfer statuses](https://www.airwallex.com/docs/payouts/transfers/create-a-transfer/transfer-statuses)：在适用版本与轨道下，已观察到的支付状态后仍可能迟到失败；不要将其写成跨厂商终态。
- [Transaction reconciliation report](https://www.airwallex.com/docs/banking-as-a-service/reporting/financial-reports/transaction-reconciliation-report) 与 [settlement report](https://www.airwallex.com/docs/payments/payment-operations/reporting/settlement-report)：交易对账、结算批次和报告生成状态有不同口径；矩阵读取的交易报告为 `v1.1.0`，报告 schema/账户日期版本须复核并容忍新增字段。

## Highnote

- [Transaction basics](https://support.highnote.com/hc/en-us/articles/23305971456653-Transaction-basics) 与 [ledgers](https://support.highnote.com/hc/en-us/articles/23332256167949-Highnote-ledgers)：授权、清算、冲正、退款与账本分层；事件名称不是封闭状态机或资金结论。
- [Notifications](https://docs.highnote.com/docs/developers/events/notifications) 与 [Fetching Events](https://docs.highnote.com/docs/developers/events/fetching-events)：通知可能重复、乱序、超时和重试；事件可查询/replay，但不产生业务 exactly-once，留存期须在使用时复核。
- [Reporting](https://docs.highnote.com/docs/issuing/reporting/about-reporting)：报表 schema 会演进，应按列名读取、容忍未知列，只在必需语义缺失时阻断。单笔、批量和报告各自适用不同判断。
- [Testing](https://docs.highnote.com/docs/developers/api/testing-the-api) 与 [disputes](https://support.highnote.com/hc/en-us/articles/36403730976013-Disputes-and-chargebacks)：Test 可覆盖部分交易情景，仍不等同 Live 或生产；争议临时贷记及撤销会继续改变资金事实。

若厂商未列于此处、实际版本未知、文档发生变更或事项涉及合同/法域，记录为待确认并由相应 Owner 提供权威材料；不要从本文件推定字段、状态、费用、责任、保留期或报告列。
