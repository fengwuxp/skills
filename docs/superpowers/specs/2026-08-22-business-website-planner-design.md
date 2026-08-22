# 业务官网规划师 Skill 设计

日期：2026-08-22
Skill ID：`business-website-planner`
中文名称：业务官网规划师
状态：设计已由 Owner 确认

## 一、目标与定性

`business-website-planner` 是业务官网规划专业能力。它把公司真实业务、可公开事实、可用证明材料、品牌约束和公开参考，转化为独特、可信、可设计、可验收的 Business Website Contract。

官网用于清晰说明和辅助佐证业务，不替代合同、发票、资质、交易记录、客户确认、专业审批或监管结论。

本 Skill 只持有官网业务契约，不负责 UI 绘制、Figma 写入、图片生成、代码实现、法律文本定稿或发布准入。跨阶段目标与调度仍由 `wise-agent` 持有。

官网设计稿默认使用 Figma。只有使用者明确指定墨刀、截图、HTML 原型或其他载体时才切换；默认载体不等于 Figma 写入授权，实际创建或修改 Figma 文件仍按工具和任务授权执行。

## 二、触发与边界

### 触发

- 从零规划或重构企业官网、公司官网、业务说明站。
- 按广告、代采购、电商、SaaS、制造、物流等业务类型设计官网内容和结构。
- 需要用官网说明公司定位、业务范围、工作方式、交付能力和联系渠道。
- 需要与关联品牌、旧模板或参考网站形成可解释的内容与视觉差异。
- 需要规划业务指标参考示例值、图片内容、多屏适配要求和按需 Legal 页面。

### 不触发

- 单纯 UI 绘制、Figma 写入、Logo 设计或视觉润色。
- 已确认 Figma 设计到代码的工程还原。
- 电商商城的商品、购物车、订单、账户、支付或履约产品设计。
- 单纯 SEO、广告投放、法律文本、隐私审查、代码实现或生产发布。
- 与公司业务说明无关的营销落地页、活动页、个人作品集或内容站。

## 三、最小输入

- 公司主体、业务类型、目标客户和实际服务或产品范围。
- 已知事实、允许公开内容、现有网站、品牌资产和参考材料。
- 业务责任边界、交付方式、地区、语言和浏览器客户端范围。
- 可用案例、资质、客户授权、经营数据、指标或其他证明材料。
- 表单、Cookie、账户、交易、支付、物流和数据处理事实。
- 不得相似的品牌、网站、内容组织、视觉指纹和素材。
- 最终确认 Owner 与本轮非目标。

缺少会改变业务定位、公开声明或 Legal/Data 判断的关键输入时，停止在待确认项，不按现有页面或模型常识反推业务事实。

## 四、核心输出

Business Website Contract 至少包含：

- Business Positioning：公司做什么、服务谁、核心价值和明确边界。
- Suggested Module Manifest：建议内容模块、组合方式、导航关系和条件模块。
- Business Type Adapter：命中的业务类型及该类型的内容、证据和图片重点。
- Content Contract：各模块回答的问题、主要文案事实、CTA 和 Owner。
- Claim and Evidence Notes：关键声明对应的来源、确认人或待确认状态。
- Metric Suggestions：指标项、参考示例值和使用者确认值。
- Asset Brief：Logo、图片、图标、视频和业务素材的用途、来源与许可要求。
- Reference DNA：参考网站可采用的结构方法、拒绝项和独特性要求。
- Responsive Media Brief：图片职责、焦点、安全区、裁切版本、目标视口和交接要求。
- Legal and Data Conditions：按实际数据、交易和地区事实决定的条件页面或专业交接。
- Handoff and Acceptance：UI、Figma、工程和独立验收的输入、Owner 与停止条件。

## 五、页面与模块组织

页面不是固定清单。Skill 先按业务复杂度选择组织方式：

1. 单页官网：适合业务简单、证据较少或早期公司。
2. 核心页加条件页：默认建议，按内容密度和客户决策路径组织。
3. 多业务官网：适合多个业务线、客户群或地区，共享公司事实，不复制多套同构页面。

可建议的内容模块包括：

- Business Positioning。
- Services、Products 或 Capabilities。
- How It Works、Operating Model 或 Engagement Process。
- About、Company 或 Team。
- Contact、Inquiry 或 Booking。
- Cases、Work、Clients、Industries、Markets、Credentials、Resources、FAQ。
- Privacy、Terms、Cookie、Shipping、Returns、SLA、Support 或其他政策。

上述模块可合并、拆分或删除。只有具备相应业务事实、数据行为、交易行为、案例、资质或专业依据时，才建议条件模块。

## 六、指标建议

指标设计保持简单。Skill 根据公司业务定性和成熟度，给出三至六个适合说明业务的指标项，并为每项给一个参考示例值。

最小字段：

| 字段 | 含义 |
| --- | --- |
| 指标项 | 适合当前业务的规模、质量、效率、覆盖或结果指标 |
| 业务意义 | 为什么该指标有助于说明业务 |
| 参考示例值 | 一个用于理解填写方式和实力量级的示例值 |
| 使用者确认值 | 使用者确认、替换或删除后的最终值 |

示例：

| 业务 | 指标项 | 参考示例值 |
| --- | --- | --- |
| 广告服务 | Advertising engagements | `50+` |
| 代采购 | Verified suppliers | `200+` |
| 电商运营 | Marketplace brands supported | `30+` |
| SaaS / IT | Software implementations | `20+` |
| 物流履约 | On-time dispatch rate | `98%` |

参考示例值不是事实、行业基准、承诺或可发布内容。正式官网只能使用使用者确认值；没有确认值时删除数值，或改用不含规模数字的业务说明。

## 七、业务类型适配

第一版覆盖以下常用业务家族，统一放入一个业务类型 reference，不拆成多个 Skill：

1. 广告、营销、创意、媒体和代理服务。
2. 代采购、供应商搜寻、贸易、质检和供应链协调。
3. 电商、Marketplace、店铺、目录、广告和运营服务。
4. SaaS、软件、IT、系统集成、开发和托管服务。
5. 制造、品牌、OEM/ODM、批发和分销。
6. 物流、仓储、履约、货运、清关和 3PL。
7. 咨询、财税、法务、人力、招聘和研究等专业服务。
8. 工程、建筑、施工、能源、维护和技术项目。
9. 教育、培训、人才和本地预约型服务。
10. 内容、媒体、摄影、视频、影视、出版和活动制作。
11. 金融、医疗和其他高监管业务。
12. 无法预分类的其他业务。

每个适配器只定义该类业务通常需要回答的问题、可用证明材料、指标候选、图片重点、常见越权声明和条件页面。高监管业务必须路由到对应专业能力和人类 Owner，不由本 Skill 自行给出批准结论。

## 八、公开参考与独特性

需要参考同类或相邻业务官网时：

1. 实际读取官网正文、服务页、案例页、About、Contact 和适用政策页。
2. 记录来源、读取日期、业务类型、可观察事实和适用边界。
3. 分别提炼 Content、Layout、Visual、Interaction 四类 Reference DNA。
4. 每个采用项说明为什么适合当前公司；每个拒绝项记录不可复制的品牌、文案、素材和视觉指纹。
5. 不复制参考网站的完整页面顺序、文案、客户、数字、Logo、图片、代码或视觉组合。
6. 无法读取正文时停止吸收，不根据标题、截图或搜索摘要宣布已参考。

官网之间的差异必须回到业务类型、客户决策、内容证据、品牌资产和使用场景，不通过随机换色、换字体或装饰差异制造独特性。

结构化契约使用 `reference_mode: none|public|user-provided`。没有参考时允许 `none` 且不生成 reference 记录；公开参考模式必须实际读取正文；使用者直接提供材料时记录为 `user-provided`。

## 九、图片与多屏适配

`business-website-planner` 只输出 Responsive Media Brief，详细规则由 `ui-design-expert` 持有。

Brief 至少说明：

- 图片是业务证据、内容说明还是纯装饰。
- 真实对象、人物、产品、设施或状态以及素材来源与许可。
- 主体焦点、文字安全区、允许裁切和不得裁切内容。
- 桌面、超宽屏、移动/H5、响应式 Web 和嵌入式 WebView 的目标视口。
- 是否需要横版、竖版、主体特写或不同分辨率资源。
- Logo、标签、产品规格、质检缺陷、地图文字等不得因 `cover` 丢失的信息。

`ui-design-expert` 的 `design-foundations.md` 增加 Responsive Media Contract，作为以下规则的唯一权威：

- media query 与 container query 的适用边界。
- `<picture>` Art Direction。
- `srcset + sizes` 与 `image-set()` Resolution Switching。
- `aspect-ratio`、`object-fit`、`object-position`、背景图和焦点 token。
- 超宽屏放大上限、裁切安全区、LCP、布局位移和 1x/2x 清晰度。
- 1280、1440、1920、2560、3440 及移动视口的验证要求。

原生 App、小程序和桌面原生客户端不在本契约内，交对应平台能力。

## 十、Legal、数据与交易边界

- Contact、Inquiry 或 Booking 必须说明是否真实提交、收集哪些数据、谁响应和下一步。
- Privacy、Terms、Cookie 等页面按真实数据流、地区、公司主体和专业意见决定，不作为固定模板。
- 商城交易、退款、支付、账户和资金责任交 `payment-expert` 与工程能力。
- 身份、权限、敏感数据、供应链脚本或运行风险交 `security-engineering-expert`。
- 法律、监管、医疗或其他专业结论保留人类专业 Owner。
- `document-authoring` 可整理已确认政策和正式载体，不创设专业事实。

## 十一、Skill 协作

| 能力 | 责任 |
| --- | --- |
| `wise-agent` | 持有跨阶段目标、授权、调度和最终收口 |
| `business-website-planner` | 形成 Business Website Contract |
| `product-architecture-expert` | 补齐或确认业务定位、对象、流程、规则和验收种子 |
| `grill-me` | 逐一关闭会改变定位、指标、公开声明或页面范围的关键分叉 |
| `ui-design-expert` | 形成页面、视觉、交互、响应式和 Responsive Media Contract |
| Figma Skills | 作为官网设计稿默认执行载体，在 UI 契约确认并获得写入授权后执行设计系统、页面和原型写入 |
| `imagegen` | 根据已确认 Asset Brief 生成或编辑图片 |
| `senior-software-architect` | 代码实现、框架图片组件、性能、浏览器行为和工程验证 |
| `requirement-acceptance-testing` | 独立验收业务逻辑、内容、交互、视觉和多屏证据 |
| `security-engineering-expert` | 数据、隐私、安全和高风险边界 |
| `payment-expert` | 支付、资金、退款、交易和商户责任 |
| `document-authoring` | 整理已确认的正式政策与交付文档 |

Maker 不自证 Checker 通过。Figma 截图不证明浏览器交互、响应式、业务真实性或生产可用。

## 十二、候选包结构

```text
business-website-planner/
├── SKILL.md
├── admission.json
├── agents/
│   └── openai.yaml
├── references/
│   ├── business-website-contract.md
│   ├── business-type-patterns.md
│   ├── reference-research-and-distinctiveness.md
│   └── source-map.md
├── fixtures/
│   ├── business-website-plan-valid.md
│   ├── business-website-plan-invalid-metric.md
│   └── business-website-plan-invalid-authority.md
└── scripts/
    ├── check_business_website_plan.py
    └── test_check_business_website_plan.py
```

仓库级同步更新：

- `README.md` 增加候选能力入口。
- `wise-agent/references/capability-routing.md` 增加业务官网规划路由。
- `fixtures/skill-eval/prompt-cases.json` 增加正例和 hard negative。
- 增加 `business-website-planner` 行为 fixture。
- `scripts/validate.sh` 与相关静态门禁接入校验器和行为 fixture。
- `ui-design-expert` 增强 Responsive Media Contract、来源和回归行为 fixture。

## 十三、确定性校验

`check_business_website_plan.py` 只做离线结构校验，不判断业务真实性或视觉质量。最小检查：

- 业务权威、业务类型、客户、范围、Owner 和非目标存在。
- 页面或模块被声明为建议组合，不要求固定四页。
- 指标建议包含指标项、业务意义、参考示例值和使用者确认位。
- 未确认参考示例值不能标为正式可发布值。
- 公开参考包含来源、读取状态、采用项和拒绝项。
- Asset Brief 与 Responsive Media Brief 可发现。
- Legal/Data 条件、交接能力、验收和停止条件存在。

脚本不联网、不写文件、不读取密钥、不执行 Figma、不生成页面，也不作法律、业务或发布准出。

## 十四、行为验证与候选准入

新 Skill 初始状态为 `candidate`，关闭以下门禁前不自动路由、安装、同步或发布：

1. 同一 runner/model 的 baseline/candidate 重复行为测试、独立盲评和可复核指纹尚未完成。
2. 广告服务真实任务试点尚未完成。
3. 代采购或供应链任务试点尚未完成。
4. 电商或 Marketplace 任务试点尚未完成。
5. `ui-design-expert` 的 Responsive Media Contract 尚未完成行为回归和浏览器证据验证。

行为 fixture 至少覆盖：

- 广告业务官网规划。
- 代采购官网规划。
- 电商官网规划。
- SaaS、制造或物流官网规划。
- 缺业务权威时停止。
- 参考示例值未经确认不得发布。
- 参考网站不得整站照抄。
- 单纯 UI、Figma、代码、SEO、法律文本和商城交易的 hard negative。

## 十五、公开来源与吸收边界

业务官网参考：

- [Ebiquity Digital Media Governance](https://ebiquity.com/digital-media-governance-digital-media-auditing/)：广告治理、服务范围和证据结构。
- [Tinuiti Case Study](https://tinuiti.com/work/creative-paid-social-case-study-boston-proper/)：问题、方法、结果和案例证据结构。
- [ForeignGo](https://www.foreigngo.com/)：供应商筛选、验厂、质检、订单管理、物流交接和现场证据结构。
- [China Sourcing Support](https://www.chinasourcingsupport.com/en/)：精简采购入口、需求字段、供应商比较、质检和发运支持表达。
- [Marketplace Velocity](https://marketplacevelocity.com/)：电商平台、账户责任、案例和联系表单结构。
- [CEVA Logistics Case Studies](https://www.cevalogistics.com/en/who-we-are/case-studies)：物流服务、行业与交付案例组织。
- [Grip Security Customer Stories](https://www.grip.security/success-story)：SaaS 客户故事与业务结果组织。

响应式媒体参考：

- [MDN Responsive Images](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)。
- [MDN Picture Element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/picture)。
- [MDN Container Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries)。
- [web.dev Responsive Images](https://web.dev/learn/design/responsive-images)。
- [Next.js Image Optimization](https://nextjs.org/learn/seo/images)。

只吸收可迁移的内容组织、证据方法、响应式标准和边界；不复制外部网站正文、数字、客户、Logo、图片、代码、视觉组合或厂商声明。

## 十六、完成定义

本设计进入实施计划的条件：

- Skill 名称、定性、触发与非触发已确认。
- 建议型页面模块和简单指标参考示例值规则已确认。
- 常用业务类型、浏览器客户端和多屏适配范围已确认。
- 协作责任、候选包结构、校验器和准入门禁无未决分叉。
- Owner 已复核本规格并授权进入实施计划。
