# Figma 文件工程规范

本 reference 用于已稳定 `Design Contract` 和 `Page Manifest` 后的 Figma 文件组织、组件化和代码交接。它把设计稿当作可维护工程资产，不把截图或 MCP 输出当成生产代码。

## 使用时机

页面契约通过校验、Owner 已确认且准备创建或维护 Figma 文件时读取；已有确认设计要还原到代码时，用它核对交接证据。

## 不适用场景

- 不用它代替产品事实、内容审批、视觉质量评审或浏览器可用性验证。
- 没有目标文件、写权限或代码库时，不把文件结构建议升级为 Figma 写入、生产代码或线上收益。

## 读取后必须产出

- 可检索的 Figma 页面 / frame / layer / component / variant 结构，以及变量、状态、资产和字体登记。
- 精确节点、版本、代码组件映射、已知偏离和 Design QA Owner 的交接清单。

## 需要继续读取的 reference

- 页面权威、命名和状态覆盖读取 `figma-design-contract.md`。
- 原型层级、反应、焦点和浏览器证据读取 `prototype-output.md`。
- 工具调用按当前官方 Figma Skill 路由，不复制外部 Skill 正文。

## 1. 文件骨架

Web 项目推荐使用可检索的顶层页面：

```text
00 Brief
01 Foundations
02 Components
10 Web PC | 10 Web Mobile
90 Archive
```

- `00 Brief` 只放目标、范围、来源、页面清单、状态矩阵和待确认项。
- `01 Foundations` 放颜色、字体、间距、圆角、阴影、网格、断点和语义变量。
- `02 Components` 放可复用组件、变体、状态和交互说明；页面专用组合留在页面目录。
- `10 Web PC` 或 `10 Web Mobile` 按 `client_scope` 和 Page Manifest 的两位顺序组织页面 frame；每个页面的状态和视图保持稳定层级。
- `90 Archive` 只保存被替代版本，并标注日期、原因和替代节点；不让归档稿出现在导航或代码交接入口。

页面、frame、layer、component 和 variant 使用稳定语义名，不用颜色、位置或临时迭代号命名组件。容器优先使用 Auto Layout 和明确的填充、间距、最小 / 最大尺寸；重复结构不要靠手工坐标堆叠。variant 名称表达状态或尺寸，例如 `State=Default`、`State=Error`、`Size=Large`，不要使用 `Copy 2`。

## 2. 组件、变量和状态

组件最小契约为：

`组件 / 来源 | 语义 tokens | 状态 | 交互与反馈 | 响应式 | 可访问性 | 偏离项 | Owner`

- 优先复用已确认的本项目组件；新组件必须说明为什么现有组件不能覆盖。
- 变量按语义命名，例如 `color.text.primary`、`space.layout.section`、`type.body.medium`；页面内不要散落同义硬编码。
- 组件状态至少考虑 `default`、`hover`、`focus-visible`、`pressed`、`disabled`、`loading`、`error`、`success`，按业务适用范围裁剪并记录不适用项。
- 交互反馈、错误恢复、焦点去向和可访问名称属于组件契约，不用一张静态截图代替。
- 组件偏离必须记录来源、理由、影响页面、Owner 和回收条件；不能无声复制另一站点或参考稿的品牌、密度和导航模板到当前站点。

真实内容、示例数据、图片和字体至少登记：`asset_id / source / usage / license / crop-or-ratio / owner / expiry-or-review-date`。没有来源或许可边界的图片、字体和品牌资产不能作为“已完成”交付。

组件变体和状态需要一份可独立复核的 `state_matrix`：每行记录 `component / props-or-variables / state / mock-data / expected-feedback / keyboard-or-focus / visual-evidence`。有目标代码库时可用 Storybook 或同类组件 explorer 隔离这些状态；没有 explorer 时，至少保留等价的 Figma component playground、L1 Preview 任务或浏览器 fixture。状态样例是证据，不是要求安装某个工具。

## 3. 页面与交接

每个交付页面要能从精确节点继续追踪到：

1. 页面 route、状态、真实内容来源和导航项。
2. 组件实例、变量、Auto Layout 约束和响应式规则。
3. 交互反应、overlay、返回 / 取消 / 重置、失败恢复和焦点行为。
4. 开发资源、实现备注、代码组件映射和已知偏离。

在设计到代码前，使用 Figma MCP 的精确节点上下文、metadata、screenshot 和项目实际代码 / tokens / 路由 / 状态 / 数据模式交叉核对；Figma 结构或截图只提供视觉与结构证据，不能推断未确认的业务规则。Code Connect 适用于组件与真实代码组件的稳定映射，不能用来掩盖组件契约缺失。

官方 Figma 能力（例如文件 / 节点读取、变量、Auto Layout、反应、开发资源和 Code Connect）只负责操作或读取 Figma；本项目的 `Design Contract`、`Page Manifest`、L0/L1/L2 证据等级、浏览器 Design QA 和停止条件是本地交付约定，不能把官方工具返回值当作这些证据。

Dev Mode 交接至少记录：`exact_node / ready_for_dev_status / dev_resources / component_playground / variables / annotations / code_connect / reviewer / version`。Code Connect 只有在账号计划、席位、仓库映射和设计 / 工程 review 均明确时才标记为 `verified`；否则保留 `planned` 或 `not-applicable`，不把“有链接”写成已连接。

Auto Layout 默认服务于动态内容和响应式变化：对文字、按钮和可扩展容器优先使用 hug / fill 与明确的 min / max；固定尺寸只用于真实规格或稳定的 icon / control。`ignore auto layout` 只作为局部叠层或特殊定位例外，并在 annotations / 偏离表记录原因、父容器、响应式影响和代码等价物。

## 4. 交付前检查

- 文件顶层页面、页面 frame、组件名、变量名和代码映射可检索。
- 1440 基准视图与窄屏 / 长内容约束已声明，至少记录一组目标断点 / 网格；布局不依赖截图裁剪。
- 页面、状态、导航、文字、图片和 CTA 能回到同一份 manifest / source。
- Figma preview 可走通入口、关闭、返回、重置、成功和失败恢复；交互证据与实现证据分开记录。
- component playground 或等价状态 fixture 能覆盖关键 props / state；视觉回归截图只用于比较，不取代人工 Design QA。
- 精确 node、Figma context、项目实现、浏览器结果和残余风险已交接给编码 / Design QA Owner。

以下事项仍需人工或浏览器验证：视觉层级是否合理、内容是否真实一致、键盘与焦点是否可用、响应式是否稳定、实现是否产生真实线上收益。
