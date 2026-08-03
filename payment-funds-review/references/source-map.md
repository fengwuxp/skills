# 来源图

## 来源隔离

本候选仅从用户明确提供的本地一手资金系统产品设计、系分、源码和测试提炼。独立 Maker 未读取课程 PDF、课程知识库、现有 `payment-expert`、旧产品专家支付 references、既有 holdout、Git 历史或 memory。本说明只证明本轮任务协议下的来源隔离，不构成法律 clean-room、许可或发布结论。

## 关键锚点

| 能力 | 设计/实现锚点 | 测试锚点 | 复核边界 |
| --- | --- | --- | --- |
| F01 账本身份与幂等 | `ledger/impl/.../LedgerTransactionServiceImpl.java:138,171,247`；`DefaultLedgerTransactionPostingServiceImpl.java:54` | `DefaultLedgerTransactionPostingServiceImplTests`: `testPostShouldNotDuplicateLedgerFactsOrBalancesForSameTransaction`、`testPostShouldRejectSameTransactionSnWithDifferentPostingFacts` | 测试未在本轮执行；不证明目标 MySQL |
| F02 冻结释放来源守恒 | `BalanceControlFundsInstructionRouteResolver.resolveFreeze/resolveUnfreeze` | `FundsWithdrawalAfterPartialUnfreezeFlowTests` 的部分解冻、超额和全额解冻场景 | 不证明外部提现通道或银行到账 |
| F03 授权拒绝隔离 | `AuthorizationFundsInstructionRouteResolver.resolveAuthorize` | `FundsAuthorizationTransactionFlowTests.testAuthorizationDeclinedShouldRecordRejectedFactWithoutLedgerPosting` | 不证明卡组织拒绝码或风控模型 |
| F04 关联退款原路径 | `DefaultRouteReplayService.resolve/requireReplaySnapshot/selectReplayLegs/buildReplayLeg` | `FundsDirectTransactionFlowTests` 的缺原事实、原路回放和并发超退场景 | 不证明费用、争议或无原路径退款政策 |
| F05 清结算与出款门禁 | `ClearingSettlementGateConsumerServiceImpl.inspectGate`；`PayoutPreflightServiceImpl.checkPayoutPreflight` | 对应 `ClearingSettlementGateConsumerServiceTests`、`PayoutPreflightServiceTests` | gate/preflight 不等于提交、到账或生产批准 |

## 许可与成熟度

- 当前只保留本地未安装、未同步、未提交的 `candidate`；不得推定团队共享或公开发布许可。
- 文档处于设计/Review、源码和测试证据层；目标 MySQL、宿主 IAM/审批/审计、外部通道、监控和 Runbook 另行验证。
- KYC/KYB/AML、客户资金归属、税务、会计、合同、跨境和外汇规则由专业 Owner 确认。
