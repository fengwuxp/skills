# 原型标注契约

本 reference 统一产品事实、HTML / Figma 载体和验证证据的关系。它不定义业务口径，也不把 Figma 注释、截图或 HTML 文本提升为事实源；产品事实由 `product-architecture-expert` 持有，UI Skill 只负责把事实投影到可审阅载体。

## 使用时机

- 产品设计、系分、业务数据或验收需要追到 HTML / Figma 的具体页面、状态、元素或节点。
- HTML 与 Figma 之间切换，或两端发生多轮变更，需要判断是否仍是同一条标注事实。
- 需要区分标注结构通过、设计工具交接、浏览器行为和业务验收证据。

单纯视觉创作、没有产品事实或验收追踪的草图不强制建立本契约。

## 单一事实与三层投影

### 1. Product Fact

产品层每条事实使用稳定且唯一的 `annotation_id`，至少能回到：

`annotation_id / requirement_id / acceptance_id / carrier_id / fact_status / owner / product_revision / source_ref`

跨载体 `annotation_id` 统一以字母开头，仅含字母、数字、下划线或连字符；切换 HTML / Figma 时保留同一 ID，不使用 HTML checker 不接受的点号或冒号。

`fact_status` 只取 `confirmed / inferred / pending`。涉及派生或异步交付结果的页面还应引用对应业务标识和来源 revision；数据未就绪、过期或来源冲突时，页面必须表达 `pending / stale / error` 等已确认状态，不能用原型中的示例数字替代业务事实。

产品层决定“必须呈现、可操作、可观察什么”。缺少 Owner、来源、版本、需求或 AC 时，标注停在 `pending` / `blocked`，不由载体自行补义。

### 2. Design Carrier

HTML 与 Figma 是同一 Product Fact 的不同适配器，不得各自复制一份业务标注表：

| 载体 | 必要定位 | 载体专属字段 | 最低证据 |
| --- | --- | --- | --- |
| standalone HTML | `#element-id` 或 `[data-name="value"]` | `target / content / revision` | `check_ui_source.py` 静态检查 + 浏览器任务 / 键盘焦点走查 |
| Figma | 精确 `node-id` 或节点 URL | `exact_node / figma_revision / annotation_type / content` | 计划校验 + exact node 回读 + Prototype Preview / Dev Mode 证据 |

两种适配器都必须带回 `annotation_id`、`product_revision`、Owner 和来源引用。HTML 选择器不能使用像素坐标、DOM 层级或 `nth-child`；Figma 不能用“当前选中层”或模糊 frame 名代替节点。工具的 annotation / description / status 只承载交接上下文，不改变 Product Fact。

### 3. Evidence

证据记录载体版本、检查动作、结果和限制。静态 JSON、Figma evidence 行、截图或 MCP 输出只能证明结构 / 设计交接的一层；不能单独证明产品语义、浏览器可用、业务数据正确或线上收益。对齐状态使用 `aligned / source-newer / target-newer / conflict / blocked`，缺少 exact node、selector、revision 或 Owner 时保持 `blocked` / `stale`。

## 工具选择与升级

| 要回答的问题 | 最低载体 | 可以证明 | 不能越权证明 |
| --- | --- | --- | --- |
| 页面、状态、对象和 AC 是否闭合 | L0 产品 / 流程契约 | 范围、状态、追踪关系 | 可点击、可访问、生产可用 |
| 视觉结构、组件、变量和设计反应 | L1 Figma | 节点、结构、交互反应和交接 | 浏览器运行或真实数据 |
| 键盘、焦点、响应式、失败恢复和真实任务 | L2 浏览器 HTML / 代码 | 运行时行为和载体证据 | 样本外用户收益或产品批准 |

选择较低层级能够回答问题时不升级工具；从 HTML 切到 Figma 或反向切换时保留同一 `annotation_id / requirement_id / acceptance_id / product_revision / state_matrix`，只替换 carrier adapter。Figma 无法写入时保持 `pending_target=figma`，不得把 HTML 截图写成 Figma 已同步。

## 业务数据、派生交付与原型对齐

当页面展示业务数据或其派生结果时，按以下链路核对：

`Domain Fact (业务语义/Owner/revision) -> Optional Derived Delivery (若存在预计算、快照或异步交付，由承责方定义输入/状态/刷新/失败边界) -> API/查询契约 (资源结果/状态/权限/兼容) -> Prototype Annotation (annotation_id/业务标识/状态/载体锚点) -> Evidence`

任一上游 revision 变化，只把受影响的下游标为 `stale`；不以页面绘制、任务成功、HTTP 200、截图或静态 checker 通过替代业务事实确认、派生交付验收或 API 兼容验证。Web API 的资源、方法、状态码、幂等和兼容裁决归 `senior-software-architect`，原型不反向发明接口路径。

## 评审最小问题

- 这条标注对应哪条已命名的产品事实、需求和 AC？Owner、来源和 revision 是否可回读？
- HTML selector 或 Figma exact node 是否稳定、唯一、可回读？载体变化有没有单独列出 annotation delta？
- 当前证据到底是 L0、L1 还是 L2？是否把静态结构、设计交接、浏览器行为、数据验收或产品批准混为一谈？
- 若展示业务数据或派生结果，业务语义、交付状态、API 响应和原型状态是否同一 revision；数据 pending / stale / error 是否有明确表达和恢复入口？
- 工具不可用、权限缺失、节点 / 锚点不存在或两端同时变化时，是否停止在 `blocked` / `conflict` 并交给 Owner？
