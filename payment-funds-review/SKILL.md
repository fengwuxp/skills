---
name: payment-funds-review
description: |
  用户明确要求对支付资金方案、实现证据或测试结果做独立准出审查，或高风险支付任务需要 Checker，并出现账本交易、冻结解冻、授权拒绝、原路退款、清结算/出款门禁、幂等冲突或失败无副作用等信号时触发。支付产品规划、普通 PRD、源码实现或修复和生产操作不触发。
---

# 支付资金审查

## 定位

审查支付资金动作是否形成一致、可追溯、失败无副作用的事实链。本 Skill 是独立 Checker：消费 `payment-expert` 提供的支付事实或 `senior-software-architect` 提供的实现证据，输出可复核裁决；不定义支付产品路线，不修改实现，也不替代法务合规、会计政策、生产审批或人类 Owner。

## 边界

- 支付产品、轨道、通道、卡组织、ACH、VCC、跨境或监管产品设计使用 `payment-expert`。
- 普通产品语义和 PRD 使用 `product-architecture-expert`；系统设计、源码 CR、TDD、修复和生产变更使用 `senior-software-architect`。这些主能力形成事实和证据后，本 Skill 只独立核对资金不变量与失败副作用，不接管 Maker 工作。
- 只有“账户”“退款”“订单”等孤立词时不触发；必须存在真实资金动作、账务事实、来源引用或准入门禁。
- 源码、H2 测试和设计文档只能证明相应证据层，不得外推目标数据库、宿主接入、外部通道或生产可用。
- Maker 的结论或摘要不能自证通过；无法读取原始方案、源码锚点、测试结果或事实快照时输出 `PENDING`。

## 审查流程

1. **冻结输入**：读取原始方案或实现证据，确认资金主体、币种、金额、原事实、业务/账务身份、来源引用、当前动作、规则版本和验收 Owner；缺关键输入则停止自动放行。
2. **展开事实链**：逐项核对 `business fact -> route snapshot -> posting plan -> ledger transaction/entry -> balance bucket -> projection/audit`，不得用状态成功替代任一后续事实。
3. **选择专项规则**：读取 `references/funds-review.md`，只进入命中的幂等、冻结、授权拒绝、原路退款或清结算/出款章节。
4. **裁决并闭合失败**：输出 `PASS / BLOCK / PENDING / OUT_OF_SCOPE`。任何 `BLOCK` 都必须明确：相关账户桶、交易、route、posting、ledger transaction/entry、投影和审计事实哪些不得新增或变化；转人工不是继续入账许可。
5. **标记证据等级**：区分设计契约、源码/测试、目标数据库/宿主和生产观测。证据不足时保留待确认项，不写成上线或专业批准。

## 输出契约

- `裁决`：结果及直接原因。
- `事实`：已给材料和可复核锚点证明什么。
- `阻断项`：缺失、冲突、超额、未知或越权事实。
- `失败无副作用`：余额桶、交易、路由、账务、投影和审计的明确断言。
- `补证据动作`：责任 Owner、所需证据和重新校验点。
- `范围外不做`：合规、会计、通道或生产结论的专业边界。
- `交还主能力`：产品事实缺口交 `payment-expert`，实现或测试缺口交 `senior-software-architect`；本 Skill 不直接修复。

## 验证与来源

- 五类审查规则与反例：`references/funds-review.md`。
- 来源、成熟度和复核边界：`references/source-map.md`。
- 行为回归题：`test-prompts.json`；候选准入状态：`admission.json`。

## 红线

- 不把同一身份下不同金额、币种、主体、账目、周期、posting facts 或结果当作幂等重放。
- 不用总余额覆盖冻结来源、累计释放量或原交易可退额度。
- 不把授权拒绝写成 chargeback、posting、entry 或余额变化。
- 不按当前支付工具绑定替代原交易路径；原事实不足时停止且零副作用。
- 不把清结算 gate 或出款 preflight 通过当成提交、到账或生产授权。
- 不以本地设计、源码、测试或 Checker 通过宣称法律合规、会计正确、外部网络兼容或生产可用。
