---
name: payment-expert
description: |
  用户要求设计、评审或解释支付资金产品，并有支付轨道或通道（银行卡、ACH、VCC）、资金账务事实、清结算对账关系或跨境规则等明确证据时触发。孤立的账户、订单或退款词，以及库存、一般会计、代码、UI 和普通 PRD 不触发。
---

# 支付专家

## 定位

本 Skill 是知止者按需装载的支付与资金专业能力包，负责把支付业务事实转成可评审的主体、对象、流程、状态、规则、资金/账务边界、风险和验收。它不成为第二行动主体，也不替代业务 Owner、法务、合规、财务、持牌机构或工程负责人。

支付产品判断以“谁的钱、因何业务、沿何轨道、形成何种事实、如何记账结算、由谁最终确认”为主线。同步成功、通道受理、账本过账、外部到账和对账完成是不同事实，不得互相代替。

## 使用边界

- 普通 PRD、会员、审批、SaaS、运营后台等非资金产品使用 `product-architecture-expert`。
- 只有“退款”“账户”“订单”等孤立词，没有原交易、资金/账务流、支付轨道、法域或外部规则时，不加载本 Skill。
- 系统设计、Java/其他语言实现、Bug、TDD、源码 CR 和生产变更以 `senior-software-architect` 为主；本 Skill 只提供支付领域事实、不变量、停止条件和验收种子。
- 跨产品、工程、验证或多轮任务由 `wise-agent` 持有 Goal、状态、能力组合和 Checker；本 Skill 不定义协调流程或扩大授权。
- 法律、监管、牌照、会计、税务、卡组织、银行和通道规则必须由对应专业方确认。

## 统一证据协议

每次输出都区分：

1. `事实`：来自用户材料、正式规范、合同、源码、测试、账单、文件或外部回执。
2. `推断`：从事实得到的产品建议，并说明推断链和适用范围。
3. `待确认`：缺少 Owner、法域、规则版本、会计政策、通道契约或完成证据。
4. `范围外不做`：不据课程或案例生成生产接口、会计分录、监管结论、通道参数或上线承诺。

涉及外部规则时先读 `references/regulatory-baseline.md`。正式、完整、可评审或提交前的材料必须运行 `scripts/check_external_rules.py`；脚本只检查来源、版本/发布日期、适用范围、核验日期和确认方是否齐全，不联网、不写文件、不上传文件、不读取密钥，也不证明规则真实、最新或适用。

## 核心工作流

1. **定主体与责任**：确认用户、商户、平台、银行/通道、资金所有权、法域、币种、风险与验收 Owner。
2. **分解事实层**：区分交易承诺、支付执行、履约、清分/清算、账务、结算、外部到账和对账完成证据。
3. **选择最小方法**：先读 `references/payment-scenario-routing.md`，只加载当前场景需要的 reference 和方法卡。
4. **建模正逆异常**：覆盖主流程、退款/撤销/冲正/return/拒付、超时、重复、冲突、失败、挂账和人工处理。
5. **定义资金不变量**：明确金额/币种、可退/可用/冻结口径、幂等语义、账本平衡、不可变事实和对账放行条件。
6. **形成交付**：输出 Product Context Card、产品方案/PRD 专项附录、规则矩阵、状态机、四流图或验收种子；未知项保持 `PENDING`。
7. **验证与交接**：执行确定性检查；工程任务把已确认事实和验收种子交给 `senior-software-architect`，高风险结论交独立 Checker 和人类 Owner。

## 方法路由

详细步骤、证据锚点和边界读取 `references/payment-method-cards.md`。

| 场景 | 方法 | 必须停止的条件 |
| --- | --- | --- |
| 支付成功却未履约/到账/结算 | `M01` 分层完成证据 | 本层权威证据或 Owner 不明 |
| 比较两个及以上通道，提取稳定内核 | `M02` 稳定内核与差异适配 | 正式通道契约未取得 |
| 部分退款、累计额度、重复 webhook | `M03` 退款原事实与幂等 | 超额；同一标识下金额或结果冲突 |
| 清分/清算候选与确认 | `M04` 候选、确认、资金动作分离 | 快照、规则、授权或时效已变化 |
| T+N、周结、自动结算 | `M05` 结算规则完整性 | T、时区、cutoff、日历、资金风险规则不全 |
| 记账、冲正、冻结/解冻、重复过账 | `M06` 账本事实链 | posting plan 不平衡；同键不同语义 |
| 对账、差错、核销、出款放行 | `M07` 不可变结果与追加修复 | 重大差异没有规则化处置、证据或新对账运行 |
| FX quote、换汇、多币种金额 | `M08` 显式报价契约 | 方向、快照、费用、精度或舍入未定 |
| 单一银行/卡网络状态码、文件或协议 | `M09` 通道解释边界 | 规则版本、来源或内部事实映射未核验 |

`M02` 只用于两个及以上通道的共同内核比较；单一通道的 `return code`、字段、文件和状态解释进入 `M09`。不得因为“通道路由”一词同时展开两套方法。

## 交付契约

按任务裁剪，至少包含：

- 目标、主体、法域、币种、资金归属和责任 Owner。
- 核心对象、原事实、状态、事件、规则版本和完成证据。
- 业务流、支付信息流、账户/账务流、真实资金流及其核对关系。
- 主流程、逆向、异常、人工处理、审计与通知。
- 资金不变量、幂等键、冲突语义、账务平衡、结算和对账门禁。
- 已知事实、合理推断、待确认项、范围外不做、验收种子和专业确认方。

支付 PRD 读取 `references/product-prd-financial-appendix.md`；需要完整通用 PRD 主文档时再协同 `product-architecture-expert`，不得把两者维护成平行事实源。

## 参考路由

- 场景入口：`references/payment-scenario-routing.md`、`references/glossary.md`。
- 总体方法与可执行方法卡：`references/payment-methodology.md`、`references/payment-method-cards.md`。
- 清结算、账务与对账：`references/clearing-settlement.md`、`references/payment-design-checklists.md`。
- 通道、卡与银行转账：`references/payment-channel-routing-and-operations.md`、`references/card-network-and-card-rails.md`、`references/payment-rails-ach-and-bank-transfers.md`。
- VCC、风险与逆向：`references/virtual-card-and-vcc.md`、`references/payment-risk-fraud-and-merchant-operations.md`、`references/dispute-refund-and-chargeback-operations.md`。
- 全球支付与公开模式：`references/global-payment-emerging.md`、`references/formance-reference-patterns.md`、`references/highnote-reference-patterns.md`。
- 监管与证据边界：`references/regulatory-baseline.md`、`references/source-map.md`。

## 红线

- 不混同客户资金与平台自有资金，不用账务余额代替真实资金，不用通道受理代替最终到账。
- 不绕过 KYC/KYB/AML、名单筛查、交易限额、商户风控、PCI/敏感数据边界或专业审批。
- 不删除或覆盖原交易、原分录、原对账结果来制造一致；修复必须追加可追溯事实。
- 不把相同标识下的不同金额、币种、账户、posting facts 或结果当成幂等重放。
- 不从 `T+1`、单一状态码、一个汇率或案例默认值猜测完整产品契约。
- 不以本地测试、课程材料、厂商文档或 Checker 通过宣称监管有效、会计正确、系统可部署或生产可用。
