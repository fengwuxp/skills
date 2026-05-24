# 支付与资金场景识别与方案路由

本文用于在回答前快速判断支付问题属于哪类场景、应读取哪些参考、输出什么产物、优先检查哪些红线。它是知识路由，不是支付交易路由；不要把本文中的“路由”理解为生产系统里的通道路由规则。

## 使用时机

- 用户问题涉及支付、资金、账户、账本、清结算、对账、商户结算、分账分润、支付通道、银行卡/卡组织、ACH/银行转账、收单/发卡、VCC、风控欺诈、争议拒付、跨境支付、稳定币/Web3、AI 代理支付或业财一体化。
- 已经通过 `product-scenario-routing.md` 判断为支付与资金专项，需要选择最小 reference 集合。
- 需要先判断法域、主体、资金归属、支付轨道、目标产物和待确认项。

## 不适用场景

- 不涉及真实资金、支付轨道、账户账务或金融数据的普通产品方案；此时优先回到 `product-scenario-routing.md`。
- 用户只问工程实现、代码 Review、测试设计或系统架构实现细节；此时优先使用 `资深架构师`，必要时再引用本文做业务语义补充。
- 用户要求法律、合规、税务、会计、监管或外部机构规则的最终结论；本文只能提供产品架构检查框架和待确认项。

## 读取后必须产出

- 场景类型、组织语境、支付轨道、资金复杂度、目标产物和最小 reference 集合。
- 复杂或高风险支付资金问题，先用 `payment-methodology.md` 的金融业务总纲回答主轴和六个控制面，再选择专项 reference。
- 涉及真实资金或金融数据时，明确是否已读取 `regulatory-baseline.md`，并列出法域、主体、资质、资金归属、数据边界和待专业确认项。
- 输出方案时必须区分业务流、支付信息流、账户/账务流和真实资金流，不能把支付成功、清算完成、结算完成和资金可用混为一个状态。

## 需要继续读取的 reference

- 支付/资金方案的总纲、四流、单据、能力地图和专家交付口径读 `payment-methodology.md`。
- 真实资金、牌照、客户资金、个人信息、金融数据、跨境、稳定币/Web3 或 AI 代理付款读 `regulatory-baseline.md`。
- 清结算、对账、账户科目、账务矩阵和结算系统读 `clearing-settlement.md` 与 `payment-design-checklists.md`。
- 通道路由、商户风控、争议退款、ACH/银行转账、卡组织、VCC、跨境或新支付形态按下方快速路由表继续读取专项 reference。
- 公开资料来源和提炼边界读 `source-map.md`。

## 使用方式

先按以下顺序识别场景，再选择参考文件：

复杂或高风险场景先按 `payment-methodology.md` 的金融业务总纲收敛：谁的钱，因什么业务，在什么主体和账户下，沿哪条支付轨道，以什么规则流转，何时可用，谁承担风险，谁最终确认。主轴不清时，先输出假设、澄清问题、待确认项和最小补齐计划，不直接下钻到单个支付轨道或页面方案。

1. **组织语境**：普通企业/平台、第三方支付机构、银行/清算机构、跨境/全球支付、Web3/稳定币/AI 代理支付。
2. **业务动作**：收款、付款、退款、撤销、出款、分账、结算、对账、调账、争议、报表、风控、发卡、VCC、ACH debit/credit。
3. **支付轨道**：卡组织、ACH/银行转账、钱包、本地支付方式、Swift/代理行、链上/稳定币。
4. **资金复杂度**：客户资金、待结算资金、备付金、保证金、准备金、垫资、负余额、授信/额度、跨币种。
5. **目标产物**：PRD、清结算方案、账务矩阵、对账方案、争议证据方案、VCC 产品方案、通道路由方案、风控方案、评审清单。

如果涉及真实资金、牌照、客户资金、个人信息、金融数据、跨境、稳定币/Web3 或 AI 代理付款，先读 `regulatory-baseline.md`。

## 快速路由表

| 场景信号 | 优先读取 | 典型输出 |
| --- | --- | --- |
| 支付术语、清算/结算/备付金口径不清 | `glossary.md`, `regulatory-baseline.md` | 术语定义、主体语境、风险提示 |
| 收单、支付订单、支付尝试、在线支付 | `payment-methodology.md`, `card-network-and-card-rails.md`, `highnote-reference-patterns.md` | 支付流程、状态机、订单/尝试模型、事件集成 |
| 清结算、商户结算、分账分润、结算周期 | `clearing-settlement.md`, `payment-design-checklists.md` | 清结算方案、账户科目、账务矩阵、结算规则 |
| 多业务线清结算全局规划、线下 Excel 核算、财务人工打款、清结算中台 | `clearing-settlement.md`, `payment-design-checklists.md`, `diagram-output.md` | 现状问题盘点、资金路径、五中心能力切分、分期迁移路线、全局规划图 |
| 支付清算生态、网联/银联/央行/银行、备付金、跨机构清算 | `clearing-settlement.md`, `regulatory-baseline.md` | 生态参与者分层、跨机构清算链路、备付金/额度口径、待专业确认项 |
| 钱包、余额、账本、资金账户、内部转账 | `formance-reference-patterns.md`, `clearing-settlement.md` | 钱包/账本模型、账户关系、账务事件矩阵 |
| 对账、差错、长短款、批处理、资金到账 | `clearing-settlement.md`, `formance-reference-patterns.md`, `payment-design-checklists.md` | 对账方案、差错生命周期、重跑和核销机制 |
| 多 PSP/多银行/多支付方式、通道路由、降级 | `payment-channel-routing-and-operations.md` | 通道路由方案、通道健康、熔断、成本/成功率口径 |
| 商户入网、KYB、欺诈、拒付率、准备金 | `payment-risk-fraud-and-merchant-operations.md`, `regulatory-baseline.md` | 风控方案、商户生命周期、风险规则和运营闭环 |
| 支付合规、KYC/KYB/KYT/KYA、AML/CFT、大额交易、可疑交易 | `regulatory-baseline.md`, `payment-risk-fraud-and-merchant-operations.md` | 合规生命周期、客户/商户/交易/地址尽调、持续监控、待专业确认项 |
| 退款、撤销、拒付、争议、证据、chargeback | `dispute-refund-and-chargeback-operations.md`, `card-network-and-card-rails.md` | 逆向交易状态机、证据模型、争议运营流程 |
| ACH debit/credit、银行代扣、批量付款、return/NOC/reversal | `payment-rails-ach-and-bank-transfers.md`, `dispute-refund-and-chargeback-operations.md`, `payment-risk-fraud-and-merchant-operations.md` | ACH 轨道方案、授权证据、return/NOC/reversal 处理 |
| 卡组织、银行卡收单、预授权、Stand-In/SAF、open-to-buy、tokenization、PCI、BIN/IIN、三方/四方模式 | `card-network-and-card-rails.md`, `dispute-refund-and-chargeback-operations.md` | 卡交易流程、授权/清算/结算、授权恢复、争议、网络费用和 PCI 边界 |
| 外卡收单、Mastercard、卡网络角色、Authorization Core、Financial Presentment、Clearing Core、ARN、scheme fee、merchant payout、收单风控 | `card-network-and-card-rails.md`, `clearing-settlement.md`, `payment-risk-fraud-and-merchant-operations.md`, `dispute-refund-and-chargeback-operations.md` | 卡网络角色定位、授权核心、清算生命周期治理、商户可用资金、结算净额、replay / investigation 和风控闭环 |
| 企业卡、员工卡、VCC、共享额度、一次性卡 | `virtual-card-and-vcc.md`, `highnote-reference-patterns.md`, `card-network-and-card-rails.md` | VCC 产品方案、授权控制、卡账务、证据和报表 |
| 报表、数据共享、运营数据面、负余额监控 | `highnote-reference-patterns.md`, `payment-design-checklists.md`, `clearing-settlement.md` | 报表模型、字段口径、异步生成、数据面边界 |
| 跨境支付、多币种、Swift/GPI、Nostro/Vostro、代理行、本地清算网络、外清内结 | `global-payment-emerging.md`, `regulatory-baseline.md`, `clearing-settlement.md` | 跨境五层拆解、资金流、币种/汇率/费用、合规待确认项 |
| 稳定币/Web3、链上链下账本、托管钱包 | `global-payment-emerging.md`, `regulatory-baseline.md`, `formance-reference-patterns.md` | 链上链下账户映射、出入金、合规红线 |
| AI 代理支付、自动付款、代理授权 | `global-payment-emerging.md`, `regulatory-baseline.md`, `payment-risk-fraud-and-merchant-operations.md` | 授权范围、限额、人工确认、审计和撤销机制 |

## 组合场景路由

- **ACH 争议 / unauthorized return**：读 `payment-rails-ach-and-bank-transfers.md` + `dispute-refund-and-chargeback-operations.md` + `payment-risk-fraud-and-merchant-operations.md`。重点输出 debit authorization evidence、账户验证、return code、NOC、reversal、retry、证据包和用户通知。
- **VCC 争议 / 企业卡拒付**：读 `virtual-card-and-vcc.md` + `card-network-and-card-rails.md` + `dispute-refund-and-chargeback-operations.md`。重点输出 cardholder、卡、授权控制、清算、退款、争议证据和 PCI 边界。
- **收单 + 商户结算 + 对账**：读 `payment-methodology.md` + `clearing-settlement.md` + `card-network-and-card-rails.md` + `payment-design-checklists.md`。重点输出支付单据、清分规则、结算批次、通道对账和资金到账对账。
- **多业务线清结算全局规划**：读 `clearing-settlement.md` + `payment-design-checklists.md` + `diagram-output.md`。重点输出线下线上断点、报表不记账、对账无差错闭环、能力重复建设、五中心能力边界、迁移优先级和全局规划图。
- **多通道收款优化**：读 `payment-channel-routing-and-operations.md` + `payment-risk-fraud-and-merchant-operations.md` + 对应支付轨道文件。重点输出路由决策、健康熔断、成本口径、风险约束和通道对账。
- **钱包/账本 + 清结算**：读 `formance-reference-patterns.md` + `clearing-settlement.md`。重点输出钱包层、账本层、对账层、账户科目和账务矩阵。
- **跨境 + 多币种 + 商户结算**：读 `global-payment-emerging.md` + `regulatory-baseline.md` + `clearing-settlement.md`。重点输出法域、主体、币种、汇率、费用、清算路径和待确认项。

## 场景识别问题

用户描述不完整时，先补齐以下关键假设，不要急着给上线方案：

- 组织主体：普通平台、支付机构、银行、商户服务商、跨境服务商还是发卡/收单项目。
- 法域和客群：面向中国境内、美国、欧盟、跨境、多法域还是链上用户。
- 资金归属：客户资金、商户待结算、平台自有资金、保证金、准备金、授信额度还是预算额度。
- 支付轨道：卡、ACH/银行转账、钱包、本地支付方式、跨境汇款、稳定币/Web3。
- 当前动作：正向支付、退款、撤销、结算、出款、对账、争议、风控、报表、证据提交。
- 外部依赖：银行、支付机构、清算网络、卡组织、PSP、发卡处理商、账本服务、数据仓库。

## 输出路由

- **用户要方案**：输出背景、范围、角色、四流、状态机、账户/账务、对账、结算、风险、验收标准。
- **用户要评审**：优先使用 `payment-design-checklists.md`，按资质、资金、账务、对账、风控、隐私、外部规则时效性排序。
- **用户要账务**：输出账户科目、余额方向、业务事件、借贷分录、真实资金动作和对账来源。
- **用户要争议/证据**：输出争议类型、原因码、证据模型、EvidenceActivityLog、EvidencePackage、脱敏和提交审计。
- **用户要学习路径**：使用 `skill-tree.md`，按基础、产品、账务、对账、清结算、风控、架构、跨境、新支付形态分层。

## 路由红线

- 不要只凭关键词路由。比如“清算”可能是平台内部清分，也可能是持牌清算机构语境，必须先定主体和法域。
- 不要把卡 chargeback 模板套到 ACH unauthorized return，也不要把 ACH reversal 当成 refund。
- 不要把通道路由、知识路由和资金清结算路由混为一谈。
- 不要为了回答完整而加载所有参考；只加载和当前场景相关的 reference。
- 不要在缺少法域、主体、资金归属和外部规则版本时输出确定性上线结论。
