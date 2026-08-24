# 可操作原型与 Figma 工程交接

## 使用时机

当任务要求输出可操作原型、在 Figma 创建或维护设计、建立可点击交互，或把 Figma 交给开发者 / AI 编码还原时读取。

## 不适用场景

- 已确认的 Figma 只需实现代码时，本 Skill 不重新设计，由 `senior-software-architect` 主责工程还原。
- 只需静态线框、流程说明或局部视觉参考时，不为“更完整”强制创建 Figma 文件。
- 原生 iOS / Android、3D、游戏或非浏览器应用不套用本 reference。

## 读取后必须产出

- 明确选择一个原型层级，并产出目标问题、范围、页面/状态图、交互契约、真实内容边界、验证证据和停止条件。
- L0 产出流程契约及 Owner 确认证据；L1 另产出 Figma 文件结构、可点击路径和精确 frame/node；L2 另产出浏览器实现约束和运行验证证据。
- 需要开发或 AI 编码还原时，再补充工程交接字段。
- 设计责任、Figma 操作责任和代码实现责任的明确边界。
- 原型库与设计系统的版本、运行时和状态样例来源；原型版本不能默默复制已过期组件代码。

## 需要继续读取的 reference

- Figma 与代码多轮双向同步、节点级漂移和待写回状态读取 design-code-reconciliation.md。

- 任务结构与设计契约读取 `design-and-review-workflow.md`。
- 完整网站的来源权威、页面命名、Page Manifest 和跨页一致性读取 `figma-design-contract.md`。
- Figma 文件骨架、组件、变量、Auto Layout、资产登记和代码映射读取 `figma-file-engineering.md`。
- 组件、tokens、响应式与可访问性读取 `design-foundations.md`。
- 任务测试和实现后核对读取 `usability-validation-and-design-qa.md`。
- 来源、时效性与供应链边界读取 `source-map.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 选择原型层级 | `一、原型层级`、`二、最小原型契约` | 不先选工具 |
| 在 Figma 创建可点击原型 | `三、Figma 能力路由`、`四、文件结构`、`五、交互验证` | 不把截图当交互证据 |
| Figma 交给开发或 AI 编码 | `六、设计到代码交接`、`七、代码到画布回环` | 不把 MCP 输出当生产代码 |
| 验收原型 | `八、验证矩阵`、`九、停止条件` | 不用“看起来像”替代任务验证 |

## 一、原型层级

- **L0 流程契约**：页面/状态图、内容样例和交互表足以关闭结构分叉；不创建画布。
- **L1 Figma 可点击原型**：需要让 Owner、用户或工程逐步操作页面、弹层、变量和失败路径；交付原生可编辑 Figma 节点与 reactions。
- **L2 浏览器可运行原型**：需要验证真实键盘、焦点、表单、URL、响应式、数据边界或错误恢复；有目标代码库时使用项目技术栈，并由工程能力实现。

选择能回答当前验证问题的最低层级。该分层是本项目的工程化证据模型，不是 Figma 官方命名；它表示交互证据强度，不表示代码质量、生产可用性或发布成熟度。

无目标代码库且验证问题只需一条任务链时，可交付轻量独立 L2：

- 由本 Skill 稳定设计契约，再由 `senior-software-architect` 用一个自包含 `.html` 文件实现；内联必要 CSS / JS，不接认证、真实 API 或外部服务，也不为原型引入构建链。
- 只实现一条可信流程及其相关成功、失败和恢复状态；所有可见控件必须可操作或明确禁用，不留死按钮、假链接和不可到达状态。
- 在真实浏览器验证宽窄视口、键盘、焦点、长内容、控制台和溢出；交付绝对路径、已验证任务、已知缺口和真实系统接管点。
- 原型只证明所走查的交互，不证明生产代码、容量、安全、真实集成或发布就绪。

## 二、最小原型契约

开始画布操作前至少稳定：

1. 用户、场景、验证问题、成功结果、范围、非目标、假设和 Owner。
2. 每个应用 / 客户端的设计系统姿态、继承或参考来源、品牌与密度边界、例外及 Owner；具体选型读取 `ui-library-landscape.md`。
3. 入口、退出、返回、取消、重置，以及页面图和状态图。
4. default、loading、empty、error、success、权限、弱网、长内容和真实数据范围。
5. 交互表：`source / trigger / condition / action / destination / feedback / failure`。
6. 响应式、键盘、焦点、可访问名称、对比、缩放和减少动效要求。
7. 交付文件、精确 frame/node、版本、证据、残余风险和停止条件。
8. 涉及完整网站时，补充 `Design Contract`、`Page Manifest`、导航映射、内容 / 资产来源和页面状态覆盖；未通过 `check_figma_design_plan.py` 不进入 Figma 写入。
9. 涉及组件交接时，补充 `state_matrix`、`component_playground` 或等价状态 fixture、`ready_for_dev_status` 和 reviewer；没有这些证据时只能标为 planned。

组件规范最小字段为 `组件 / 来源 | 语义 tokens | 状态 | 交互与反馈 | 响应式 | 可访问性 | 偏离项 | Owner`。跨端只共享已经确认的语义和行为；页面结构、品牌和密度是否共享由各应用 / 客户端姿态决定。

产品规则、权限和成功口径未确认时停止，不用原型发明业务事实。

## 二 A、可迭代原型变更契约

原型出现多个可独立验收切片、共享状态 / 样式 / 数据、反复局部修改伤及非目标区域，或需要多人 / Agent 协作时，增加 `Prototype Change Slice`：

```text
prototype_id / revision
authoritative_surface / source_form / delivery_artifact
target_slice / reads / writes
preserved_invariants / forbidden_scope
state_delta / merge_owner
regression_baseline / regression_scope
evidence / status
```

- 一条可信流程、一次性交付、一个维护者且无目标代码库时，可使用 `authoritative_surface=code`、`source_form=standalone-html`，自包含 HTML 同时作为 `delivery_artifact`；不为形式引入框架、构建链、Storybook 或多 Agent。
- 只有 `authoritative_surface=code`、`source_form=standalone-html`，且多切片、共享状态或持续迭代已经造成代码局部修改扩散时，才把 `source_form` 升级为 `modular-project`；单文件 HTML 只由源码生成作为 `delivery_artifact`，禁止双向手改，并记录 revision 与生成方式。
- `authoritative_surface=figma` 且没有代码目标时，继续用 components、variants、variables、Auto Layout 和语义 frame 管理多屏与状态，不为持续设计迭代引入代码工程；只有 L2 / 生产代码目标与 Owner 授权成立后才建立 code target，双端继续变化时转入 `design-code-reconciliation.md`。
- `target_slice` 按可独立理解和验收的任务、状态与职责划分，不按视觉矩形机械拆分；读写范围重叠时先稳定共享契约或改为串行，`merge_owner` 只汇合已验收 delta，不重新设计。
- 信息架构、内容层级或视觉方向是当前最大不确定性时可以先冻结静态基线；状态、交互或失败恢复是核心风险时先建任务流和状态契约，不把“静态优先”设为固定阶段。
- 局部修改完成后同时验证目标、原主任务、`preserved_invariants` 和 `regression_scope`；模型自述“未改其它区域”不是证据。

## 三、Figma 能力路由

按当前可用能力最小组合，不建立平行 Figma Skill：

- 新建 Figma 文件：先加载 `figma-create-new-file`。
- 读取或修改 Figma / FigJam / Slides：先加载 `figma-use`，并遵守相应上下文 Skill。
- 把页面、视图或多屏任务写入 Figma：组合 `figma-generate-design`。
- 建立或维护设计系统、组件、variants 和 variables：组合 `figma-generate-library`。
- 维护 Figma 动效：组合 `figma-use-motion`；代码动效实现使用 `figma-implement-motion`。
- 已确认设计到代码：由工程能力组合 `figma-design-to-code`。
- 建立或维护组件到代码映射：组合 `figma-code-connect`。

若当前能力清单没有独立“Figma 原型”能力，点击、导航、overlay、variables、conditionals 和 multiple actions 可由 `figma-use` 通过 Plugin API 的 `setReactionsAsync` 建立。它是官方支持的 API 能力，不是官方强制工作流；工具执行不替代本 Skill 的原型契约和验收判断。

## 四、Figma 文件结构

为人类开发和 AI 编码共同优化：

- 复用 components 与 variants，不把重复界面画成互不关联的 frame。
- 核心和高频组件优先维护 Code Connect；无映射时模型只能猜测代码组件。
- 用 Figma variables 表达颜色、间距、圆角和排版等设计决策，名称采用稳定语义而非临时视觉值。
- 使用 Auto Layout，并在交接前把 frame 调整到目标视口，验证 resize 行为。
- layer、component 和 variant 使用语义命名；给复杂行为添加 annotations，给节点添加 dev resources。
- 先检查当前文件和团队约定再修改，不在同一任务中顺便重建整套设计系统。

## 五、交互建立与验证

- 为主路径、失败恢复、返回、取消、重试和重置建立 reactions；条件分支与变量变化必须能回到交互表。
- 用 `setReactionsAsync` 写入 Figma 节点，不以静态连线说明冒充可点击原型。
- 在 Figma preview 从真实入口逐步操作到成功、失败和恢复结果；复测 overlay 的打开/关闭、焦点意图和返回目标。
- 记录 Figma 文件版本、原型库 / 设计系统版本与运行环境；若组件库已升级，重新核对组件变体、状态样例和代码映射，不沿用旧原型的隐式假设。
- 截图只证明某一时刻的静态画面，不证明 reaction、条件、变量、导航或恢复路径成立。
- 保存精确 frame 链接、文件版本、验证任务和实际结果；未走查的路径保持未验证。

## 六、设计到代码交接

官方推荐方向是“结构化设计上下文 + 项目约束 + 代码映射 + 可视验证”，不是截图转代码：

1. 明确 Figma 文件、精确 node、目标框架、代码目录、现有设计系统和不得改变的产品契约。
2. 先检查目标代码库的 components、tokens、routing、state、data fetching 和资源处理方式。
3. 对精确节点调用 `get_design_context`；结果截断或范围过大时，先用 `get_metadata` 定位，再缩小节点范围重取。
4. 调用 `get_screenshot` 作为视觉参照，并读取 Code Connect map、variables、annotations 和 dev resources。
5. Code Connect 的 component name、props、import、framework label 和团队指令必须与真实代码 API 同步；映射过期时先修映射或记录偏差。
6. 由 `senior-software-architect` 使用项目现有组件、tokens、路由、状态和数据模式实现，不机械接受生成代码或新增占位资产。
7. 在真实浏览器验证布局、交互、响应式、键盘/焦点、状态和请求失败；记录与设计契约的有意偏差。

MCP 输出不是生产代码。它提供结构化上下文和参考实现信息；代码仍需适配项目、测试和工程审查。像素一致也不能替代任务、语义、状态和失败恢复验证。

## 七、代码到画布回环

当回环不是一次性的单向捕获，而是 Figma 与代码都可能继续变化时，先读取 design-code-reconciliation.md。每个页面或区段必须声明 authoritative_surface、sync_mode、exact node、code anchor、版本、Owner、授权和 pending target；双方均有独立变化时保持 conflict，不能先后互相覆盖。

已有可运行界面需要设计评审时，可采用官方 code-to-canvas 回环：运行目标页面，把真实 UI 捕获为可编辑 Figma frame，设计者批注或修改，再把精确 frame 链接交回工程实现。该回环适合消除“静态稿与真实代码状态不同步”，但不自动证明捕获页面覆盖了全部状态或数据。

## 八、验证矩阵

| 对象 | 最低证据 | 不能证明 |
| --- | --- | --- |
| L0 流程契约 | 页面/状态图、交互表、Owner 确认 | 可点击、可访问或可实现 |
| L1 Figma 原型 | 原生节点、reactions、preview 任务走查、精确链接 | 浏览器行为、生产代码或 WCAG 合规 |
| L2 浏览器原型 | 真实浏览器任务、桌面/移动、键盘/焦点、状态与失败请求 | 生产容量、安全或发布就绪 |
| 代码还原 | 设计上下文、Code Connect、截图对照、测试和 Design QA | 目标用户已能正确完成任务 |

正式交付可运行：

```bash
python3 ui-design-expert/scripts/check_ui_design_deliverable.py \
  --kind prototype-plan --file <prototype-plan.md>
```

脚本按文档中明确选择的 L0、L1 或 L2 检查对应结构和显式字段，不读取 Figma、不访问网络，也不判断视觉质量或交互真实可用。

## 九、停止条件

- 设计事实或代码目标不唯一，无法确定哪个 Figma node / branch / component 是权威。
- Code Connect、variables 或组件 API 明显过期，却要求无偏差自动还原。
- 关键 reaction、失败恢复、返回或重置路径未走查，却要求宣称“可点击原型已完成”。
- 浏览器行为是核心问题，却只授权静态 Figma 证据。
- 需要联网、安装、Figma 写入、Git 或部署但未获得相应授权。
