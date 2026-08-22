# Web 审批可点击原型计划

## 目标、层级与边界

目标用户是审批运营，验证问题是能否从待办进入详情、发现风险并完成退回。选择 L1 Figma 可点击原型；范围覆盖待办、详情、退回弹层和结果页，非目标是不接真实后端、不宣称生产就绪。产品规则与权限由产品 Owner 确认，当前假设单人审批。

## 页面、状态与真实内容

入口为待办列表，退出为结果页，重置回到同一条待办。页面图与状态图覆盖 default、loading、empty、error、success、权限不足和弱网；使用脱敏但真实长度的数据，说明长文本、溢出和无权限状态。

## 交互与失败恢复

交互表逐项记录 source、trigger、condition、action、destination、feedback 和 failure。点击退回打开 overlay，条件不满足时阻止提交并把焦点移到错误摘要；失败时保留用户输入，可关闭弹层返回详情。Figma 交互使用 `setReactionsAsync`，同时验证返回与重置路径。

## 工程交接与可访问性

设计系统姿态为继承项目现有体系；组件来源、语义 tokens、组件状态、偏离项和 Owner 均写入组件规范。组件优先复用现有 Figma components，并核对 Code Connect、Figma variables、Auto Layout、语义命名、annotations 和 dev resources。交接给 AI 编码时提供 exact node，先取 `get_design_context`；截断时先用 `get_metadata` 缩小范围，再取 `get_screenshot`。实现继续复用项目组件、tokens、路由、状态和数据模式，由 `senior-software-architect` 负责。响应式覆盖桌面与移动，键盘、焦点、可访问名称、对比和 200% 缩放进入验收。

## 验证证据与停止条件

在 Figma preview 走通成功、校验失败、网络失败、返回和重置路径，保存精确 frame 链接、版本和任务走查记录。截图只证明静态画面，不证明可点击；MCP 输出不是生产代码。关键 reaction、错误恢复或产品规则未验证时停止交接，记录残余风险和 Owner。
