# 设计稿保真与还原审查

## 使用时机

当用户要求审查 Figma、墨刀、截图、原型设计稿或浏览器实现，重点检查内容是否确实、页面是否完整、布局是否变形、文字是否意外换行或截断、资产是否可信、状态是否一致时读取。实现后浏览器 Design QA 继续读取 `usability-validation-and-design-qa.md`。

## 不适用场景

- 没有来源类型、精确定位、版本、内容来源或目标视口时，不宣称完成保真审查。
- 静态截图不能证明 reaction、键盘、焦点、浏览器响应式或生产行为。
- 本 reference 不批准产品事实、法律文本、图片 / 字体许可或视觉方向；冲突项交回对应 Owner。

## 读取后必须产出

- `Review Contract`：来源类型、定位、版本、访问方式、限制、内容权威、资产登记、视口集合、证据等级、reviewer 和状态。
- `Review Checks`：内容、布局、文字、溢出、响应式、资产和状态的预期 / 实际 / 样例 / 证据 / Owner。
- 按 P0-P3 排序的 findings、最小修复、复测集合和不能由当前证据支持的结论。

## 需要继续读取的 reference

- 内容和页面权威读取 `figma-design-contract.md`。
- Figma 文件、Auto Layout、组件与 Dev Mode 证据读取 `figma-file-engineering.md`。
- 排版、栅格、长内容和资产韧性读取 `design-foundations.md`。
- 浏览器、可访问性和可用性复测读取 `usability-validation-and-design-qa.md`。

## 1. 先分清审查对象

| 对象 | 可检查 | 不能直接证明 |
| --- | --- | --- |
| Figma 节点与 metadata | frame 尺寸、层级、组件、变量、Auto Layout、文本属性、节点状态 | 浏览器实际换行、字体加载、DOM 与可访问性 |
| Figma screenshot | 当前视口下的重叠、裁切、视觉层级、明显换行和资产状态 | 其它视口、reaction、焦点和动态内容 |
| Figma Preview | 已走查的 reaction、overlay、返回、关闭和状态路径 | 浏览器 CSS、真实网络、WCAG 完成度 |
| 墨刀分享 / 标注 | 已实际打开的页面、状态、间距、字体、CSS 和可下载资产 | Figma variables、Code Connect、未分享页面或浏览器实现 |
| 墨刀 / 其它工具导出物 | 导出时刻的静态页面、标注、切图或代码起点 | 在线版本、完整交互、其它状态或生产代码 |
| 浏览器实现 | 实际字体、换行、溢出、响应式、键盘、焦点、网络和控制台 | 未覆盖数据、设备和目标用户总体表现 |

审查顺序固定为：先核对来源与页面集合，再核对内容与资产，最后检查布局 / 排版 / 状态。来源错误时，即使视觉精美也不能通过。

## 2. Review Contract

至少声明：

`review_id / source_kind / source_locator / source_version / access_mode / source_limitations / target_role / version / source_of_truth / content_manifest / asset_registry / viewport_set / viewports / evidence_level / reviewer / status`

- `target_role` 只能表示草稿、待审或已批准设计角色；目标稿不能反向成为产品内容权威。
- `target_role` 使用 `current-draft-only`、`approved-design`、`reference-only` 或 `runtime-implementation`；浏览器实现只能使用 `runtime-implementation`。
- `source_kind` 使用 `figma`、`mockingbot`、`screenshot` 或 `runtime`；`source_locator` 必须能回到精确 node、分享链接、带哈希导出物或运行页面。
- `source_version` 和 `access_mode` 记录实际审查的版本与读取方式；`source_limitations` 明确不可见页面、缺少标注、静态导出、字体或浏览器证据等限制。
- 每个 Web 客户端范围至少审查两个已声明目标视口；不能从单一 frame 外推其它宽度。
- `layout-fit` 和 `responsive` 的证据必须分别覆盖每个已声明视口，不能用同一截图重复充数。
- `E1` 只证明契约，不能标为 `approved`；`E2` 可证明已走查原型，`E3` 才能证明浏览器实现。`approved` 不得包含 `fail` 或 `blocked` 检查，截图数量也不会自动升级证据等级。
- `E4` 除 E3 浏览器证据外，还必须包含可复核的目标用户任务记录或生产运行观测；`browser` 与 `screenshot` 不能单独升级为 E4。

## 3. 来源接入与证据降级

同一套 Review Checks 不要求设计工具内部结构相同，只要求来源、限制和证据等级名实相符：

| `source_kind` | 主路径 | 最高证据 | 必须停止或降级的情况 |
| --- | --- | --- | --- |
| `figma` | 精确 node 的 `get_design_context`，结合 variables、Code Connect、annotations 与 screenshot | E2 | 只有全文件链接、截图或过期 mapping |
| `mockingbot` | 分享链接的 Preview / 标注，记录页面与状态清单、间距、字体、CSS 和切图 | E2 | 只有导出包、D2C 代码或不可访问链接时降为 E1 |
| `screenshot` | 带版本或哈希的静态图片 | E1 | 不得声明交互、响应式或浏览器行为 |
| `runtime` | 真实浏览器中的 DOM、字体、状态、网络与截图 | E3；有目标用户 / 运行证据时才可能到 E4 | 只有静态截图或未覆盖状态 |

Figma 已有官方结构化路径，继续由 `figma-design-to-code`、`figma-use`、Code Connect 等当前能力执行，本 reference 不复制其工具步骤。墨刀当前按浏览器分享、标注和导出证据处理；厂商生成的 HTML / Vue / React 代码只是工程起点，必须回到目标项目组件、tokens、业务状态和浏览器验证。无法访问分享且没有可追踪导出物时停止，不凭宣传页或截图补内部结构。

`layout-fit` 与 `responsive` 只有标为 `pass` 时才要求覆盖全部目标视口；证据缺失时应标为 `blocked`，记录已取得证据、缺失视口、Owner 与解除条件，不用 `not-applicable` 或伪造引用绕过。

## 4. 内容确实与一致性

内容审查分开检查：

1. **来源一致**：标题、导航、CTA、表单字段、数字、Legal / Privacy 和免责声明逐项回到 `content_manifest` 或批准文档。
2. **内容完整**：逐页对照 `Page Manifest` 和内容清单，检查 section、正文、CTA、状态文案、Legal / Privacy、图片与替代文本是否缺失；空白占位不能算已交付。
3. **事实状态**：真实事实、示例数据、推断和待确认必须有标签；`illustrative` 不能伪装为线上指标。
4. **图文一致**：图片主体、文案、CTA 和页面目的描述同一对象；图片不能只因“好看”偏离业务。
5. **跨页一致**：同一术语、导航、CTA、联系信息、品牌名和协议状态跨页一致；站点差异按品牌边界保留。
6. **资产确实**：Logo、图片、图标和字体能回到来源、用途、许可、裁切与 Owner；占位资产不得标为 final。

发现来源冲突时标记 `blocked`，不由设计审查者补写事实。

## 5. 布局变形与溢出

每个目标视口至少检查：

- frame / section / grid / card / overlay 是否重叠、越界、坍缩、错位或意外重排。
- Auto Layout 的 hug / fill / fixed / min / max 是否表达真实布局意图；`ignore auto layout` 是否有明确例外说明。
- 文字层的 Auto width / Auto height / Fixed size 是否符合内容变化；流式区域中的固定尺寸文字层必须用边界内容证明不会裁切或重叠。
- 固定格式控件、图片、Logo、表格和表单是否保持稳定尺寸；内容变化不能导致无意义跳动。
- 横向溢出、隐藏裁切、遮挡、不可见 CTA、固定层盖住内容和滚动容器嵌套问题。
- 空、短、典型、极长、大数、多项、图片失败、权限和错误状态是否仍保持阅读与操作顺序。

Figma 阶段用精确节点、Auto Layout 属性和目标视口 screenshot 作为 E2 证据；浏览器阶段再用真实 CSS 布局、scrollWidth / clientWidth、bounding box、截图和键盘走查形成 E3 证据。需要声明 WCAG 2.2 实现证据时，还要覆盖 200% 文字缩放、等效 320 CSS px 重排和文字间距覆盖；这些测试不能在 Figma 阶段判定通过。

## 6. 文字换行与排版失真

文字审查必须使用真实或边界内容，不用 `Lorem ipsum`：

- **最长导航 / CTA / 状态标签**：检查单行预算、允许换行位置和控件高度；不能靠缩小字号或负字距临时塞入。
- **标题与正文**：检查批准的最大行数、行长、行高、孤行、标点挤压、CJK 与 Latin 混排；正文不因居中或固定高度被裁切。
- **最长不可断词**：域名、邮箱、URL、订单号、组织名和技术标识必须能换行、滚动或截断并提供完整值。
- **大数与本地化**：货币、百分比、日期、复数、中文 / 英文或其它目标语言变化不能撑坏组件。
- **字体失败**：替代字体加载后重新检查字宽、行高和按钮 / 标签高度；Figma 字体存在不等于线上字体可用。

`text-wrap` 的通过证据至少包含 `longest-label`、`cjk-latin`、`large-number`、`localized` 或 `long-content` 中适用样例，以及对应节点 / 截图 / 浏览器证据。

浏览器截图回归需固定浏览器、操作系统、字体和渲染条件，并由人复核差异；像素差只能证明画面变化，不能判断内容来源或业务语义。

## 7. 输出与严重度

每条 `Review Check` 至少包含：

`id / category / status / expected / observed / test_case / evidence / owner`

必查 ID 为：`content-source / content-completeness / content-consistency / layout-fit / text-wrap / overflow / responsive / asset-source / state-coverage`。不适用时写 `status: not-applicable` 和 `rationale`，不能直接删除。

严重度沿用 P0-P3：内容事实错误、主任务不可达、Legal / Privacy 冒充最终事实通常至少 P0/P1；核心视口重叠、主 CTA 被裁切、关键文字不可读通常 P1；边界内容下局部换行或视觉漂移按任务影响定 P1/P2；纯装饰偏差且不影响理解为 P3。

运行结构校验：

```bash
python3 ui-design-expert/scripts/check_design_draft_review.py --file review.md
```

通过只表示审查契约和证据字段完整，不表示设计稿真实无误、浏览器已验证或产品 Owner 已批准。
