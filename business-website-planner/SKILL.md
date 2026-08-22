---
name: business-website-planner
description: |
  用户要求从零规划或重构用于说明和辅助佐证公司真实业务的企业官网，并需要按广告、代采购、电商、SaaS、制造、物流等业务类型梳理定位、建议模块、内容、指标参考示例值、公开参考差异、图片多屏要求、联系方式或按需 Legal 页面时触发。单纯 UI/Figma、建站编码、商城交易、SEO 或法律文本不触发。
---

# 业务官网规划师

## 定位

本 Skill 把公司真实业务、可公开事实、证明材料、品牌约束和公开参考转化为 Business Website Contract。官网用于清晰说明和辅助佐证业务，不替代合同、发票、资质、交易记录、客户确认、专业审批或监管结论。

本 Skill 只持有官网业务契约，不负责 UI 绘制、Figma 写入、图片生成、代码实现、法律文本定稿或发布准入。跨阶段目标和授权仍由 `wise-agent` 持有。

当前为候选能力，仅在用户显式调用时使用；准入状态见 `admission.json`。

## 核心流程

1. **冻结业务权威**：确认公司主体、业务类型、目标客户、真实范围、责任边界、允许公开内容、Owner 和非目标。缺少会改变定位或公开声明的事实时停止，不按现有页面反推业务。
2. **选择业务适配器**：读取 `references/business-type-patterns.md`，只加载命中的业务家族；不能归类时从主体、对象、服务/交易流程、交付物和证据动态推导。
3. **研究公开参考**：先声明 `reference_mode: none|public|user-provided`。用户要求联网参考或提供公开站点时，读取 `references/reference-research-and-distinctiveness.md`，实际读取正文并提炼 Content、Layout、Visual、Interaction DNA，不复制完整组合；没有参考时不伪造来源。
4. **组织建议模块**：按业务复杂度选择单页、核心页加条件页或多业务官网。页面与区段只是建议，可合并、拆分或删除；详细契约读取 `references/business-website-contract.md`。
5. **给出内容与指标**：为每个模块说明业务问题、事实、CTA、证据和 Owner；按业务定性建议三至六个指标项及参考示例值，由使用者确认、替换或删除。未确认值不得进入正式官网。
6. **形成素材与多屏 Brief**：说明图片职责、真实对象、来源许可、焦点、安全区、裁切版本和目标视口。详细 Responsive Media Contract 由 `ui-design-expert` 持有。
7. **交接与停止**：输出 UI、默认 Figma 载体、工程和独立验收交接。涉及数据、交易、支付、安全、法律或监管时交对应专业能力和人类 Owner。

## 默认设计载体

官网设计稿默认使用 Figma。只有使用者明确指定墨刀、截图、HTML 原型或其他载体时才切换。默认载体不等于写入授权；创建或修改 Figma 文件仍需明确目标文件和写入许可，并按当前 Figma Skills 执行。

## 场景路由

- **广告、采购、电商、SaaS、制造、物流等常用业务**：读取 `references/business-type-patterns.md` 中唯一命中的适配器，不套用跨行业页面模板。
- **公开搜索与参考学习**：读取 `references/reference-research-and-distinctiveness.md`；`public` 模式正文不可读时停止吸收，`none` 模式允许不提供 reference 记录。
- **建议模块、指标和交接契约**：读取 `references/business-website-contract.md`；指标只使用“指标项、业务意义、参考示例值、使用者确认值”。
- **业务定位尚未确认**：交 `product-architecture-expert` 稳定主体、对象、流程、规则和验收种子。
- **关键分叉影响定位、公开声明、指标或页面范围**：按需使用 `grill-me` 一次关闭一个 Owner 决策。
- **页面、视觉、交互和多屏媒体设计**：交 `ui-design-expert`；Figma 是默认执行载体。
- **图片生成或编辑**：在 Asset Brief 已确认后交 `imagegen`，生成结果仍需来源、内容和视觉验收。
- **代码实现**：交 `senior-software-architect`，由工程能力选择框架图片组件和性能策略。
- **实现验收**：交 `requirement-acceptance-testing` 独立检查业务、内容、交互、视觉与多屏证据。
- **支付、安全与正式政策**：分别交 `payment-expert`、`security-engineering-expert` 和 `document-authoring`；专业批准保留人类 Owner。

需要复核公开来源、读取状态、时效和未吸收内容时读取 `references/source-map.md`。

## 最小输出

- Business Positioning 与业务权威。
- Suggested Module Manifest 与组织方式。
- Business Type Adapter。
- Content Contract 与关键声明证据。
- Metric Suggestions：指标项、业务意义、参考示例值、使用者确认值。
- Asset Brief、Reference DNA 与 Responsive Media Brief。
- Legal/Data 条件、协作交接、待确认项和停止条件。

结构化计划可运行：

```bash
python3 business-website-planner/scripts/check_business_website_plan.py --file plan.md
```

脚本通过只表示结构满足窄契约，不证明业务真实、视觉合格、法律充分、Figma 已写入、代码可用或生产就绪。

## 停止条件

- 公司主体、业务权威、实际服务/产品范围或最终 Owner 缺失。
- 参考网站正文不可读，却要求声明已参考。
- 参考示例值未确认，却要求直接发布为业务事实。
- 表单、Cookie、账户、交易、支付、物流或数据处理事实不明。
- 与现有品牌或参考站点仍存在无法解释的同源内容或视觉组合。
- 需要联网、Figma 写入、安装、Git、部署、生产、删除或不可逆动作但未获授权。

## 红线

- 不发明客户、案例、规模、效果、市场覆盖、资质、合作伙伴或监管结论。
- 不把参考示例值、搜索摘要、截图、模型推断或现有页面当成业务事实。
- 不固定 Home、Business、About、Contact 为四个独立页面。
- 不复制参考网站的页面顺序、文案、数字、Logo、图片、代码和视觉组合。
- 不把 Figma 截图当作浏览器响应式、真实交互、业务证明或生产完成证据。
- 不接管 `wise-agent` 的调度、产品事实、UI 设计、工程实现或独立验收责任。
