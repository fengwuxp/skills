# 验收证据路由

## 使用时机

在决定“这个条件应在哪一层验证、需要什么证据、是否值得自动化”时读取。原则是最低充分证据层，而不是把所有条件写成浏览器 E2E。

## 一、证据矩阵

| 验收类型 | 优先证据 | 常见工具 | 不能单独证明 |
| --- | --- | --- | --- |
| `business-logic` | 单元/服务测试、数据库或审计事实 | 项目现有测试框架 | 真实外部集成、生产运行 |
| `api-contract` | 契约报告、真实请求/响应 | 项目已有契约或 API 测试 | 完整业务结果 |
| `data-side-effect` | DB、消息、投影、审计前后事实 | 测试容器、查询、日志 | UI 是否可用 |
| `ui-interaction` | 浏览器 trace 或行为断言 | 项目已有 Playwright/浏览器工具 | 业务持久化正确、视觉完全一致 |
| `visual-fidelity` | 设计上下文 + 运行截图 + 独立复核 | Figma/墨刀读取、浏览器截图 | 交互、可访问性、目标用户可用性 |
| `accessibility` | 自动报告 + 键盘/焦点/语义运行检查 | 项目现有 a11y/浏览器工具 | 完整 WCAG 合规 |
| `runtime-observation` | 指标、审计或生产观测 | 已授权监控/日志 | 未观测场景 |
| `manual-owner` | 人工决策记录 | 评审/签字证据 | 自动回归覆盖 |

## 二、自动化选择

优先自动化同时满足的条件：规则稳定、结果可观测、执行可重复、失败可定位、维护成本低于重复人工成本。否则保留人工检查，但必须写清方法、Owner、证据和限制。

选择顺序：

1. 复用现有单元、集成和契约测试。
2. 复用已有 Playwright、Storybook 或浏览器设施。
3. 只为真实缺口补最小测试代码。
4. 新框架、托管视觉平台或依赖安装必须有持续价值和明确授权。

## 三、Web UI 最小证据

- 使用用户可见的 role、label、text 或 test id 定位，避免依赖易变 DOM 结构。
- 每个测试独立建立状态，不依赖前序用例。
- 核对操作前状态、动作、反馈、最终状态、重复操作、错误恢复、键盘/焦点和控制台。
- 视觉验收声明具体视口、字体、内容和状态；检查缺图、裁切、重叠、溢出、意外换行和跨页不一致。
- 截图差异需要人工复核；更新基线是验收基线变更，必须由 Owner 确认。

### 3.1 静态 UI 源码契约的边界

对静态 JSX、TSX、HTML 或 CSS 的源码契约可以补充检查 section 范围、语义文案、route、breakpoint token 和明确禁止项。为减少假阳性，断言应限定目标 section 或同一对象边界，并至少用一个 mutation 证明目标错误会使检查失败。

这类证据仍只观察实现结构：

- 不能证明浏览器实际字体、换行、裁切、重叠、滚动或响应式布局。
- 不能证明点击、键盘、焦点、错误恢复或数据副作用。
- 组件重构后实现细节断言可能失效，即使用户可见行为未变。
- 不得单独把 visual-fidelity 或 ui-interaction 判为 pass。

视觉通过仍需要 design-context、声明视口的 runtime-screenshot 和独立 visual-review；交互通过仍需要 browser-trace 或 browser-assertion。缺少这些证据时按 required 条件输出 blocked 或 cant-tell，不用源码契约补成 Pass。

## 四、需求到示例

复杂规则先列：规则、具体正反例、未决问题、范围外项。`Given / When / Then` 可用于表达可执行示例，但不要求引入 Cucumber，也不能用格式完整掩盖需求未定。

## 五、跨能力责任

- `product-architecture-expert`：提供业务对象、规则、状态和验收种子，不自证实现通过。
- `senior-software-architect`：实现或修复测试与生产代码，提供工程证据。
- `ui-design-expert`：提供设计权威、视觉/交互契约和 Design QA 专业判断。
- `payment-expert`、`security-engineering-expert` 等：定义领域不变量与高风险检查。
- `requirement-acceptance-testing`：冻结条件、组织执行、核验证据充分性和输出独立裁决。
- 人类 Owner：确认价值取舍、人工条件、基线更新和发布授权。
