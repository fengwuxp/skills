# Figma UI 设计与还原能力增强实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Each task must retain the repository's Skill ownership and verification gates.

**Goal:** 把本项目的 Figma/UI 能力从“能规划一张稿、能调用 Figma 工具”增强为“能锁定页面权威、产出完整一致的 Figma 工程稿，并以可复核证据交接给代码还原”。

**Architecture:** 不复制或替代官方 Figma Skills；由 `ui-design-expert` 持有 Web 设计契约、页面/状态/视觉一致性和验收边界，新增 references 承载 Figma 工程规则，新增确定性脚本校验设计计划与页面清单，官方 `figma-*` Skills 负责实际 Figma API 路由，`senior-software-architect` 负责代码实现和 Design QA。产品事实继续由 `product-architecture-expert` 持有。

**Tech Stack:** Markdown、Python 标准库校验脚本、现有 `ui-design-expert` fixtures/validators、Figma MCP 官方工具与 Skills、Code Connect、Figma variables、Auto Layout、Playwright（只在有目标代码库的 L2 验证中使用）。

---

## 1. 方案状态与边界

状态：第一阶段已实现并通过针对性回归测试；行为盲评与 Pilot 待完成；未写入或修改任何 Figma 文件。

本计划解决的是 Skill 的设计判断、Figma 工程结构、页面一致性和代码交接能力，不解决：

- Figma 账号、团队席位、远程 MCP 连接或写权限的获取。
- 业务事实、法律文本、品牌注册、图片版权或真实广告投放规则的最终确认。
- 自动把 Figma MCP 输出直接当生产代码。
- 自动发布 Code Connect、自动提交 Git、自动部署或自动改生产页面。
- 为本仓库复制一套平行的 `figma` 大 Skill；官方 Figma Skills 继续作为执行能力来源。

## 2. 事实来源与证据边界

### 2.1 双站点设计反馈

本轮用户提供的双站点设计反馈只作为过程证据，不把历史助手结论或私有项目细节升级为仓库事实。关键可复用信号如下：

| 记录信号 | 暴露的问题 | 对 Skill 的要求 |
|---|---|---|
| 用户要求两个站点在内容、设计、布局、风格、文案和协议上可区分 | 网站差异目标没有在页面、品牌、内容和协议之间形成统一验收 | 增加跨站差异化约束、术语/资产一致性和负例检查 |
| 用户先确认“调整而不是大改或重做”，同时又确认视觉层面可以大改 | 变更范围和视觉/内容的变化轴没有锁定 | 每轮必须声明基准、继承项、允许变化项和禁止变化项 |
| 用户指出导航与规划不一致、应以重构文档为基准 | Figma 当前稿反向成为内容权威 | 建立产品文档 > brief > 参考稿 > 目标稿的权威链，目标稿只作现状 |
| 用户要求以指定参考稿为基准，内容只优化、主要调整视觉 | 参考文件、目标文件、历史草稿角色混淆 | 文件角色、页面 ID、状态和基准节点必须进入设计契约 |
| 用户指定只做 Web PC | 端范围容易在 Figma 中扩张或被默认补齐 | 页面清单必须带 `client_scope`，范围外端不生成、不验收 |
| 用户要求字体无版权问题，且标志不能因结构相似而接近另一站点 | 字体、Logo、图像和品牌距离没有成为可验证设计资产 | 增加字体许可、Logo 结构、真实图像和跨站相似性检查 |
| 用户确认 Dashboard/虚构数据可保留，但必须符合业务定位 | 虚构内容未标记为示例，导致内容与业务边界混淆 | 数据状态必须标注 `illustrative`，并检查业务语义和展示范围 |
| 用户发现目标稿只具备部分状态/页面，Inquiry 只有默认与成功 | 静态画面覆盖不等于完整流程 | 页面清单必须覆盖状态、返回、关闭、失败恢复和 Preview 走查 |

已脱敏的问题摘要为：参考稿与目标稿角色混淆、导航不一致、目标稿含未经确认指标、页面不完整、视觉系统未统一、Inquiry 状态不完整、Legal 不能直接作为最终协议。原始外部项目路径与对话标识不进入 Skills 仓库。

### 2.2 本项目现有能力

- `ui-design-expert` 已有任务类型、最小 brief、信息架构、状态矩阵、响应式、可访问性、L0/L1/L2 原型分层和 Design QA。
- `ui-design-expert/references/prototype-output.md` 已规定 Figma 路由、组件/variables/Auto Layout/语义命名/annotations/dev resources、reactions 和代码交接。
- `ui-design-expert/scripts/check_ui_design_deliverable.py` 已能检查原型计划的结构字段，但不能校验页面命名、跨页一致性、文件角色和代码映射完整性。
- 仓库已有 Figma 相关行为 fixtures 和 trigger smoke，但主要检查“是否提到正确工具/边界”，不检查设计计划本身能否作为单一页面权威。

### 2.3 官方 Figma 能力边界

Figma 官方资料要求文件优先使用 components、Code Connect、variables、语义命名、Auto Layout、annotations 和 dev resources，并建议在生成代码前取得精确节点的 design context；官方也明确 MCP 提供结构化上下文和参考代码，不是“一键完美生产代码”。

本计划采用这些作为工程规则来源：

- [Structure your Figma file for better code](https://developers.figma.com/docs/figma-mcp-server/structure-figma-file/)
- [Figma MCP introduction](https://developers.figma.com/docs/figma-mcp-server/)
- [MCP tools and prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
- [Code Connect integration](https://developers.figma.com/docs/figma-mcp-server/code-connect-integration/)
- [What the MCP sends vs. what the agent does](https://developers.figma.com/docs/figma-mcp-server/mcp-vs-agent/)
- [`setReactionsAsync` / reactions](https://developers.figma.com/docs/plugins/api/properties/nodes-reactions/)

本轮二次公开核验补充以下一手资料：

- [Figma Dev Mode guide](https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode)：`dev resources`、component playground、Ready for dev、图层属性与 Code Connect 交接。
- [Figma Code Connect](https://help.figma.com/hc/en-us/articles/23920389749655-Code-Connect)：组件映射、属性映射、真实代码示例、账号计划 / 席位和设计工程 review 前置条件。
- [Figma auto layout guide](https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout)：动态内容、fixed / min / max 尺寸和 `ignore auto layout` 例外。
- [GOV.UK prototyping](https://design-system.service.gov.uk/get-started/prototyping/) 与 [GOV.UK get started](https://design-system.service.gov.uk/get-started/)：原型 Kit / Design System 版本边界、可访问响应式组件和研究后扩展。
- [Storybook component explorers](https://storybook.js.org/tutorials/visual-testing-handbook/react/en/component-explorers/) 与 [visual testing](https://storybook.js.org/tutorials/ui-testing-handbook/react/en/visual-testing)：组件隔离、props / state 样例和视觉回归分层。
- [Material 3 states](https://m3.material.io/foundations/interaction/states/overview) 与 [Carbon Figma kits](https://carbondesignsystem.com/designing/kits/figma/)：状态层、变量、组件变体和响应式网格的公开实践。

吸收边界：上述资料只提供可迁移的工程方法；不吸收品牌、Logo、字体、图片、固定色值、内部 DOM / class、组件源码、安装步骤或平台专属模板。

## 3. 根因判断

当前缺口不是单纯“视觉审美不足”，而是五个权威层没有闭合：

1. **产品权威未进入 Figma 页面清单**：页面名称、路由、内容主题、业务边界和 Owner 仍靠对话记忆。
2. **参考稿、目标稿和历史稿没有状态模型**：目标稿中的错误内容会被误当成基准，造成导航、页面数量和内容骨架漂移。
3. **Figma 文件没有工程化结构契约**：组件、变量、Auto Layout、语义层级、页面状态和节点链接没有稳定命名和可复核规则。
4. **全站内容与资产没有统一注册表**：文案、Logo、图像、字体、CTA、术语和真实/示例数据可以跨页面漂移，也无法检查两个站点之间的差异。
5. **设计到代码没有证据闭环**：截图、MCP 输出、Figma 节点、Code Connect、项目组件、运行时状态和浏览器验证没有绑定为同一交接对象。

## 4. 产品架构与治理对象

### 4.1 业务目标与用户价值

业务目标：让设计 Owner 能在进入 Figma 写入前确认“哪些页面、哪些状态、哪些内容和哪些视觉变化可以被实现”，让前端能从同一份契约还原页面，而不是从截图猜页面。

用户价值：减少导航/页面漏项、内容与品牌串站、重复画组件、设计稿不可还原和交接时反复返工。成功指标是页面 manifest 校验通过率、设计计划到 Figma 的页面映射完整率、代码交接缺口数和关键路径 Design QA 阻断数；这些指标只评估流程质量，不承诺业务转化增长。

非目标：不以自动校验替代设计 Owner、产品 Owner、法务/隐私 Owner 或工程评审；不把页面数量、截图相似度或组件数量当作设计质量的单一指标。

### 4.2 能力地图

能力地图分为六个能力域：

1. 设计源管理：权威链、基准文件、目标稿、历史稿和变更模式。
2. 页面与内容管理：页面 ID、路由、导航、状态、术语、真实内容和示例数据。
3. Figma 工程设计：页面结构、组件、variants、variables、Auto Layout、annotations、dev resources、component playground 和 Ready for dev。
4. 视觉与品牌一致性：排版、颜色、资产、字体许可、站点差异和跨页复用。
5. 原型与交互证据：L0/L1/L2、reactions、Preview、状态走查和失败恢复。
6. 代码交接与 Design QA：exact node、design context、Code Connect、项目组件/token、state matrix、浏览器验证和偏差记录。

### 4.3 业务对象、字段口径与生命周期

| 业务对象 | 关键字段口径 | 生命周期 |
|---|---|---|
| `DesignContract` | 项目、端范围、变更模式、权威链、Owner、状态 | draft -> ready-for-figma -> ready-for-code -> approved/superseded |
| `PageManifest` | 页面 ID、路由、展示名、Figma 名、目的、来源节点、状态集合、内容源 | proposed -> checked -> approved -> superseded |
| `AssetRecord` | 资产角色、来源、许可、裁切、alt、使用页面、状态 | discovered -> cleared -> placed -> rejected |
| `ComponentContract` | 组件名、属性、variants、tokens、状态、代码映射 | proposed -> mapped -> verified -> deprecated |
| `HandoffRecord` | Figma 版本、精确节点、context、screenshot、mapping、浏览器证据、偏差 | prepared -> checked -> accepted/rejected |

### 4.4 业务流程、状态机与人工兜底

主流程：`产品事实/brief -> DesignContract -> PageManifest -> L0 结构确认 -> L1 Figma 构建 -> Preview 走查 -> L2/代码交接 -> Design QA`。

异常流程：权威冲突、页面缺失、命名不一致、状态不可达、组件未映射、资产许可不明、Figma 无写权限或浏览器验证失败时，回到人工确认，不自动补页面、不自动改产品事实、不自动标记完成。

状态机至少覆盖 `draft / checked / approved / superseded / blocked`；每次从 `checked` 到 `approved` 都要保留 Owner、版本和验证证据。

### 4.5 规则矩阵

| 规则 | 触发条件 | 判断逻辑 | 优先级 | 版本 |
|---|---|---|---|---|
| 页面权威 | 文档、参考稿和目标稿冲突 | 产品文档/已确认 brief 高于参考稿，目标稿只作现状 | P0 | contract-v1 |
| 页面命名 | route、nav、Figma frame 或代码 route 不一致 | 任一映射缺失即阻断 | P0 | contract-v1 |
| 状态完整 | 主任务包含提交、返回、关闭或异步反馈 | 未提供状态或“不适用原因”即阻断 | P1 | state-v1 |
| 视觉复用 | 同动作/同组件跨页重复 | 复用 component/variant/token，不新画孤立副本 | P1 | file-v1 |
| 内容与资产 | 文案、Logo、图片、字体或示例数据无来源 | 标记待确认，禁止写成最终 | P1 | content-v1 |
| 代码交接 | 设计已确认但缺 exact node、mapping 或运行证据 | 只能交 `ready-for-code`，不能宣称还原完成 | P0 | handoff-v1 |

### 4.6 运营、指标、报表与审计

运营侧最小记录包括：设计计划版本、页面覆盖率、状态覆盖率、组件复用率、未映射组件数、内容/资产待确认数、Figma Preview 走查结果、代码偏差和 Design QA findings。报表按项目、页面、状态和版本分层，不用总平均数掩盖单页阻断；所有人工确认、拒绝、回退和 superseded 记录保留审计索引。

## 5. 目标能力模型

### 4.1 Source & Scope Contract

每次 Figma 设计任务先生成一份设计契约，至少包含：

```yaml
project_id: website-a
client_scope: web-pc
change_mode: visual-adjustment-with-bounded-content-optimization
authority:
  product_source: product-source-v1.md
  brief_source: approved-brief-v1.md
  reference_figma: figma-file-reference-with-node-links
  target_figma: figma-file-target
  target_role: current-draft-only
inherit:
  - page-count
  - section-order
  - business-topic
editable:
  - visual-system
  - component-structure
  - necessary-copy-correction
forbidden:
  - unconfirmed-business-claims
  - platform-logos
  - new-client-scope
  - legal-finalization-without-owner
status: draft | ready-for-figma | ready-for-code | approved
owner: business-owner
```

`change_mode` 必须明确区分局部优化、体系扩展、新界面和重设计；没有 Owner、基准文件、端范围或验收目标时，停止进入 Figma 写入。

### 4.2 Page & Content Manifest

页面不再只用展示标题命名，而是用稳定 ID、路由、业务目的和状态绑定：

```yaml
pages:
  - id: home
    route: /
    display_name: Home
    figma_name: Web PC / 10 Home / Approved
    purpose: explain-service-positioning
    source_node: exact-figma-node-url
    states: [default, inquiry-open, inquiry-validation, inquiry-success, inquiry-close, inquiry-return]
    state_exclusions: [loading, empty, permission]
    content_source: brief-section-home
    client_scope: web-pc
    status: draft | approved | superseded
```

命名规则：

- 页面 ID 只允许稳定的业务名，不使用 `Frame 123`、临时序号或仅视觉描述。
- Figma page 使用 `00 Brief`、`01 Foundations`、`02 Components`、`10 Web PC`、`90 Archive` 等固定层级。
- 页面 frame 使用 `Web PC / 10 Home / default / 1440 / Approved` 这一类稳定结构，具体值来自 manifest。
- 路由、导航标签、Figma frame、代码路由和交付文档中的页面名必须一一映射；命名不一致即阻断准入。

### 4.3 Figma File Engineering Contract

每个进入 L1/L2 的文件至少满足：

- 重复对象优先 component/variant，禁止重复画出同一按钮、导航、字段和卡片。
- 颜色、间距、圆角、排版和状态使用语义 variables，变量名表达用途，不表达临时色值。
- 有结构关系的容器使用 Auto Layout；调整目标视口后验证 resize，不以绝对坐标代替布局意图。
- layer、component、variant 和 page 使用语义名称；复杂行为写 annotations；节点绑定 dev resources。
- 组件状态必须有 `state_matrix`；可用 component playground、Storybook 或等价 fixture 隔离 props / state，不能只交一张默认截图。
- Dev Mode 交接至少保留 `ready_for_dev`、`dev_resources`、`component_playground`、reviewer 和版本；Code Connect 未满足账号、席位、仓库映射和 review 前置条件时保持 planned。
- Auto Layout 优先服务动态内容和响应式变化；记录 fixed / min / max 尺寸，`ignore auto layout` 只作为有理由的局部例外。
- 页面、状态、真实内容、示例数据、图片来源、字体许可、CTA 和交互说明能回指 manifest 或 brief。
- 每一页保留可复用的组件实例，而不是把页面截图或扁平化大图当设计稿。

### 4.4 Cross-page Consistency Contract

全站一致性以注册表而不是“看起来差不多”判定：

| 维度 | 统一事实 | 差异允许范围 |
|---|---|---|
| 品牌 | Logo、品牌名、域名、字体许可、语义色 | 页面用途导致的密度和强调级别 |
| 导航 | 页面 ID、路由、标签、当前项状态 | 当前页的 active 表现 |
| 内容 | 业务定位、术语、CTA、免责声明、示例数据标记 | 页面对应的说明深度 |
| 组件 | Button、Field、Header、Footer、Inquiry、Step 等组件 API | 页面组合方式和内容数量 |
| 状态 | default/loading/empty/error/success/权限/返回/关闭 | 不适用状态必须说明原因 |
| 资产 | 图片角色、裁切规则、alt、来源和许可 | 页面所需的真实对象不同 |
| 站点差异 | 与另一站点的品牌、命名、内容和视觉距离 | 业务事实相同导致的必要共性 |

### 4.5 Design-to-code Contract

进入代码交接时，必须提供：

1. 精确 Figma file/node 链接和版本。
2. page manifest、状态矩阵、交互表和不可自行决定项。
3. `get_design_context` 结果；范围过大时先 metadata 定位再缩小节点。
4. screenshot 作为视觉参照，但不把截图当行为证据。
5. Code Connect 映射或明确的未映射组件清单。
6. variables/tokens 与代码 token 的映射表。
7. 现有代码组件、路由、数据、状态和资源处理方式。
8. 浏览器 Design QA：桌面/移动（若在范围内）、键盘/焦点、真实内容、错误恢复和控制台/网络证据。

## 6. Skill 结构调整方案

### Task 1：扩展 `ui-design-expert/SKILL.md`

**Files:**

- Modify: `ui-design-expert/SKILL.md`
- Test: `fixtures/skill-eval/prompt-cases.json` 中现有 Figma 路由样例和新增行为样例

变更内容：

- 在触发后先判断 `design-source-authority`、`change_mode`、`client_scope` 和页面完整性，再选择 Figma 工具。
- 把“页面准确命名、页面清单、跨页内容/资产一致性、Figma 文件工程结构、代码交接”加入必要设计契约。
- 明确：已确认 Figma 只做还原时不重新设计；无目标代码库时不把 Figma 交接升级为生产代码；未有写权限时止于 L0/L1 计划。
- 将 `figma-generate-design`、`figma-generate-library`、`figma-use`、`figma-design-to-code`、`figma-code-connect` 保持为外部能力路由，不复制其正文。

验收：对“导航与规划不一致”“只做视觉调整”“已有 Figma 只还原”“需要完整网站三页和状态”四组 prompt，输出的主责、范围、页面契约和工具路由正确。

### Task 2：新增 `ui-design-expert/references/figma-design-contract.md`

**Files:**

- Create: `ui-design-expert/references/figma-design-contract.md`

内容固定为：

- source authority 和文件角色矩阵。
- `change_mode` 与 `client_scope`。
- page/content manifest 字段和命名规则。
- 页面、状态、内容、资产、术语和审批状态关系。
- L0/L1/L2 选择门禁。
- Figma 写入前的 owner、权限、版本和停止条件。

验收：不出现不可执行的“保持一致”“设计合理”等空判断，每条要求都能落到字段、状态、节点或验证证据。

### Task 3：新增 `ui-design-expert/references/figma-file-engineering.md`

**Files:**

- Create: `ui-design-expert/references/figma-file-engineering.md`

内容固定为：

- Page/frame/layer/component/variant 的命名约定。
- `00 Brief / 01 Foundations / 02 Components / 10 Web PC / 90 Archive` 文件骨架。
- variables、tokens、Auto Layout、annotations、dev resources 和 Code Connect 的使用条件。
- 真实内容、示例数据、图片、字体和许可的登记字段。
- 设计到代码的节点、版本和 mapping 交接格式。
- 哪些能力来自官方 Figma，哪些是本项目的 L0/L1/L2 证据约定。

验收：该 reference 能独立指导一名执行者创建可维护的三页 Web Figma 文件，不要求阅读外部 Skill 原文。

### Task 4：新增确定性页面计划校验器

**Files:**

- Create: `ui-design-expert/scripts/check_figma_design_plan.py`
- Create: `ui-design-expert/fixtures/figma-design-plan-valid.md`
- Create: `ui-design-expert/fixtures/figma-design-plan-invalid-page-naming.md`
- Create: `ui-design-expert/fixtures/figma-design-plan-invalid-authority.md`
- Create: `ui-design-expert/fixtures/figma-design-plan-invalid-state-coverage.md`
- Create: `ui-design-expert/scripts/test_check_figma_design_plan.py`

校验器只读本地 Markdown，不联网、不读取 Figma、不上传、不读取密钥。它必须拒绝：

- 缺少 `project_id`、`client_scope`、`change_mode`、Owner、权威链或状态。
- 页面缺少稳定 `id`、`route`、`figma_name`、`purpose`、`source_node`、`states`、`state_exclusions` 或 `status`。
- 同一 `id` 对应多个路由、多个 frame 名或页面命名不符合规则。
- 导航标签、路由、manifest 页面和交付文档页面集合不一致。
- 目标稿被声明为内容权威，或 `superseded` 页面仍被标为当前入口。
- 组件/variables/Auto Layout/annotations/dev resources/Code Connect/component playground/Ready for dev/state matrix 被写成“已完成”，但没有对应证据字段。
- 页面缺失适用的默认、错误、成功、返回、关闭或权限状态，且没有“不适用原因”。
- `ready-for-code` 或 `approved` 的 contract 仍引用 draft current page 或非 `approved-design` 目标角色。

测试先写失败样例，再实现最小解析和规则检查；不把脚本通过写成视觉质量或 Figma 实际可用。

### Task 5：扩充行为验证 fixtures 与仓库门禁

**Files:**

- Modify: `fixtures/skill-eval/prompt-cases.json`
- Modify: `scripts/validate-trigger-paths.py`
- Modify: `scripts/validate.sh`
- Modify: `scripts/smoke-wise-agent-behavior.sh`（只补与 Figma 页面权威和工程交接直接相关的 smoke）
- Create: `fixtures/skill-eval/ui-design-figma-page-contract-behavior-cases.json`

新增正负样例：

- 正：先建立页面 manifest、命名和状态，再创建 L1 Figma 原型。
- 正：已确认 Figma 只还原，走 `figma-design-to-code` 和工程验证，不重新设计。
- 正：设计系统组件、variables、Auto Layout、Code Connect、annotations、dev resources 和 exact node 交接。
- 负：用截图证明可点击、用 MCP 输出冒充生产代码、把目标稿反向当内容权威、只给一张 Hero 图却宣称整站完整。
- 负：将 `Home / Solutions / About` 与已确认页面规划不一致而不报告冲突。

验收：正例稳定触发正确 Skill 和工具边界，负例不能通过；既有 Figma 路由 fixture 继续通过。

### Task 6：建立双站点 Pilot 设计契约

**Files:**

- Create: `ui-design-expert/fixtures/multi-site-differentiation-plan-valid.md`
- Create: `ui-design-expert/fixtures/multi-site-differentiation-plan-invalid.md`

Pilot 只使用脱敏后的会话事实和已公开/已确认的规划，不写入生产 Figma：

- 两个站点作为不同 `project_id`，分别拥有品牌、导航、术语、资产和协议状态。
- 参考稿、目标稿、历史稿分别标记角色；目标稿不能成为产品内容权威。
- 页面数量、路由、导航和状态矩阵一一映射。
- `illustrative` 数据、未确认 Legal、字体许可、图片来源和站点差异都可追踪。
- 只做视觉大改或内容小改时，校验器能识别允许/禁止变化轴。

验收：Pilot 计划能复现会话中“导航对不上”“Figma 与文档差距”“不想重做只想调整”的问题，并在写入前阻断。

### Task 7：更新文档与工具路由

**Files:**

- Modify: `ui-design-expert/references/prototype-output.md`
- Modify: `ui-design-expert/references/source-map.md`
- Modify: `ui-design-expert/agents/openai.yaml`
- Modify: `ui-design-expert/admission.json`

内容要求：

- `prototype-output.md` 引用新的 page manifest 和 file engineering reference，保持 L0/L1/L2 与 Figma 官方能力边界分开。
- `source-map.md` 增加本次 Figma 官方资料的核验日期、链接、时效性和未吸收边界。
- `agents/openai.yaml` 的展示信息只描述增强后的触发和交付能力，不塞入长流程。
- `admission.json` 的状态与实际验证证据一致，未完成真实 Figma 写入/Preview 走查时不宣称候选 Skill 已具备生产级 Figma 能力。

## 7. 验证矩阵

| 层级 | 验证命令/动作 | 能证明什么 | 不能证明什么 |
|---|---|---|---|
| 结构 | `python3 ui-design-expert/scripts/check_figma_design_plan.py --file plan.md` | 页面权威、命名、状态、交接字段完整 | Figma 画布真实状态 |
| Skill 行为 | `python3 scripts/evaluate-skill-behavior.py blind ...` | 触发、路由、负例边界 | 视觉质量或真实 Figma 写入 |
| Figma 文件 | 只读 `use_figma` 查询 page/frame/layer/component/variable | 节点、命名、组件和变量实际存在 | 目标用户可用性 |
| L1 原型 | Preview 从入口走到成功、失败和恢复，保存精确 frame/node 链接 | reactions、overlay、返回和状态路径实际可走 | 浏览器 DOM、WCAG 完成度、生产代码 |
| L2/代码 | `get_design_context`、Code Connect、截图对照、浏览器/Playwright QA | 设计到代码的结构、视觉、状态和运行证据 | 发布审批、容量、安全和业务事实 |
| 站点一致性 | manifest/术语/资产/token 对照 + 人工独立评审 | 跨页、跨站品牌和内容一致性 | 自动证明审美正确 |

最低准出不是“截图像”，而是：页面集合正确、命名可追踪、状态可走查、组件与 tokens 可复用、代码交接可定位、真实内容和差异化约束可验证。

## 8. 实施顺序与阶段门

### Phase 0：事实和契约冻结

- 读取本计划、现有 `ui-design-expert`、现有 Figma fixtures 和官方 Figma 资料。
- 先完成 page/content manifest 和 authority contract 的 fixtures。
- 不改 Figma、不新增外部依赖。

准入：页面命名、路由、端范围、参考稿/目标稿角色、Owner 和变更模式均可被校验器表达。

### Phase 1：Skill 规则与确定性校验

- 完成 Tasks 1-4。
- 运行新脚本的正负 fixture、现有 UI validator、引用链接和 frontmatter 检查。

准入：新规则能阻断会话中已发生的导航、页面完整性和权威漂移问题。

### Phase 2：行为回归与 Pilot

- 完成 Tasks 5-6。
- 运行 Figma 路由 smoke、行为盲测和独立人工评审。

准入：双站点 Pilot 在不写入 Figma 的前提下能完整输出页面、状态、视觉和工程交接契约。

### Phase 3：受控 Figma 执行

- 仅在用户明确授权 Figma 写入、目标文件/节点、团队和 Owner 后启用官方 Figma 写入 Skill。
- 先建立 `00 Brief`、`01 Foundations`、`02 Components` 和一页 `Web PC / Approved`，验证后再复制到其他页面。
- 每次写入后只读回读节点 ID、命名、变量、Auto Layout、组件、reactions 和精确链接。

准入：L1 Preview 走查完成，任何未走查状态仍明确标为未验证；没有“自动完成整站”的表述。

### Phase 4：代码交接与持续治理

- 对已确认设计使用 `figma-design-to-code`，先取 exact node 的 design context，再按项目现有组件/tokens/routing/state 实现。
- 为高频组件建立 Code Connect；发布前用 CLI dry-run/preview 和代码评审确认 mapping。
- 运行浏览器 Design QA，之后才把页面标为 `ready-for-code` 或 `ready-for-release-review`。

准入：设计、代码、浏览器状态和页面 manifest 的版本/节点/组件映射一致；偏差有记录，不把 MCP 输出或像素一致写成生产准出。

## 9. 责任边界

| 责任 | Owner |
|---|---|
| 产品对象、业务定位、页面价值、协议事实 | `product-architecture-expert` / 业务 Owner |
| 页面任务流、视觉系统、状态、页面 manifest 和 Figma 工程契约 | `ui-design-expert` |
| Figma API 操作、文件写入、节点回读和 Preview 证据 | 官方 `figma-*` Skills + 获授权执行者 |
| 组件到代码映射、前端实现、浏览器 QA | `figma-code-connect` + `senior-software-architect` |
| 独立结构/行为验证 | fixtures、validator、smoke 和人工 Checker |
| 法律、隐私、图片/字体许可、生产发布 | 对应 Owner，不由 Skill 自行批准 |

## 10. 停止条件与残余风险

遇到以下任一情况停止 Figma 写入或代码准入：

- 页面名称、路由、基准节点或 Owner 不唯一。
- 参考稿、brief、产品文档和目标稿对页面数量/内容/范围存在未解决冲突。
- 需要以目标稿中的未经确认内容补齐业务事实、协议、指标、平台合作或市场覆盖。
- 只有截图，没有 reactions、状态矩阵、精确节点或 Preview 走查证据。
- Code Connect、variables 或组件 API 已过期，却要求零偏差自动还原。
- 字体、Logo、图片、图标或外部资产的许可/来源未确认。
- 目标代码库不存在或未授权，却要求把 L1 设计直接称为生产实现。

残余风险：静态 validator 无法判断真实视觉质量；Figma Preview 无法证明浏览器可访问性；Code Connect 无法替代工程测试；公开 Figma 文档和工具权限属于时效事实，执行前需重新核验。

## 11. 计划完成标准

本计划进入可执行状态需同时满足：

1. 新增 reference、validator、fixtures 和行为样例均已写入并通过本地检查。
2. 新规则能复现并阻断双站点反馈中已暴露的页面权威、命名、完整性和一致性问题。
3. `ui-design-expert` 仍保持与 `product-architecture-expert`、`senior-software-architect` 和官方 Figma Skills 的边界，不复制外部 Skill。
4. 现有 Figma 路由、L0/L1/L2、可访问性和 Design QA 证据不回退。
5. 未有 Figma 写入、Code Connect 发布、生产部署或法律/业务最终批准的误宣称。

## 12. 已确认的 1 + 3 组合执行切片

Owner 已确认采用“Figma 专项增强 + 统一契约与薄来源适配”：Figma 是结构化主路径，墨刀与截图只提供来源受限的适配入口，所有来源最终进入同一套还原交接与浏览器 Design QA。不得为表面统一建立跨工具节点模型，也不得复制官方 Figma Skills。

本批次只完成以下源仓库能力，不同步安装目录、不提交 Git、不写入 Figma，也不把静态 fixture 写成 E3 浏览器证据：

1. 在现有设计稿保真审查中增加 `source_kind`、`source_locator`、`source_version`、访问方式和来源限制，支持 `figma`、`mockingbot`、`screenshot` 与 `runtime`。
2. Figma 分支要求精确 node、design context、组件 / token 映射和 screenshot 证据；墨刀分支要求分享链接或导出物、页面 / 状态清单、标注 / 切图 / 字体 / CSS 可见性和限制；截图分支不得升级为可点击、响应式或生产实现证据。
3. 先写校验器失败测试，再做最小实现；新增行为 fixture，阻断“墨刀 D2C 代码即生产代码”“截图即高保真还原”“Figma 全文件链接即可还原”等错误行为。
4. Figma Pilot 只使用当前已实际读取的脱敏节点证据形成 E2 交接样例；真实代码还原必须在获授权且可写的目标前端仓库中完成，并以 Playwright / 浏览器证据升级到 E3。
5. Storybook 只在目标项目已安装时复用；Playwright 视觉断言属于目标项目测试，不在 Skills 仓库建立新的前端运行平台。

本切片的停止条件：来源版本或定位不唯一、墨刀分享不可访问且无导出物、Figma 缺精确节点、目标代码库不可写、字体 / 图片许可缺失，或任何步骤需要未经授权的安装、同步、Git、Figma 写入和生产动作。

本轮脱敏 Pilot 证据（2026-08-22）：对一个已获授权审查的真实 Web PC Figma section 调用 exact node `get_design_context` 成功，返回结构化布局、文本、节点标识和截图；`get_variable_defs` 取得 3 个语义颜色变量。Code Connect 因当前账号计划 / 席位门禁不可用，且目标前端仓库不在本轮可写范围，因此 Pilot 状态保持 E2，未生成或修改代码，未写入 Figma，也未持久化 file key、node id 或截图。
