# Web UI 生态与选型

## 使用时机

当任务需要比较或选择设计系统、组件库、无样式行为原语或开放代码分发方案时读取。本盘点核验于 2026-07-30，Ant Design 专项于 2026-08-21、Astryx / Agent-Ready 专项于 2026-09-02 复核；实际引入前必须重新核验维护状态、当前版本、包级许可证和项目兼容性。

## 不适用场景

- 项目已有设计系统且本轮没有替换授权。
- 只凭 stars、截图风格或“流行”决定技术和设计选型。
- 直接安装依赖；本文件不授予联网、安装、升级或迁移权限。

## 读取后必须产出

- 项目当前设计与技术事实、候选所属类别及排除理由。
- 任务/领域、技术栈、状态、可访问性、tokens/theme、维护、迁移和许可的对照。
- 一个主选、必要的备选、验证试片和停止条件；不输出脱离项目的总冠军。

## 需要继续读取的 reference

- 设计基础读 `design-foundations.md`。
- 具体页面模式读 `common-scenario-patterns.md`。
- 来源与许可边界读 `source-map.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 新项目选型 | `一`、`二`、`三` | 不先安装或做全量迁移 |
| 现有项目补复杂控件 | `一`、`五` | 不因一个控件替换整套体系 |
| 中后台或运营工具 | `二` 的企业体系与中文生态、`三` | 不选展示型模板代替系统 |
| Ant Design 跨应用采用 | `四`、`三` | 不把后台视觉外推到 C 端 / H5 |
| Agent-Ready / Astryx 评估 | `三 A`、`三` | 不把内部 StyleX、厂商自评或 AGENTS.md 文字当项目准出 |
| 自有品牌设计系统 | `五`、`三` | 不把无样式原语当完整设计体系 |

## 一、先分清资产类别

| 类别 | 提供什么 | 不自动提供什么 |
| --- | --- | --- |
| 完整设计体系 | 原则、foundations、tokens、组件、模式、设计资源与实现 | 对当前产品语义的适配和端到端可访问性结论 |
| 领域设计体系 | 面向企业、协作、基础设施、商业等特定语境的完整方案 | 脱离其领域后的品牌中立性 |
| 组件库 | 可复用组件和主题能力 | 完整原则、页面模式、内容策略和治理 |
| 无样式行为原语 | 复杂控件的语义、键盘、焦点和行为基础 | 品牌视觉、tokens、页面层级和内容设计 |
| 开放代码分发 | 把可修改的组件源码交给项目维护 | 包升级式维护、一致性治理和自动可访问性保证 |

## 二、代表性生态盘点

以下是选型入口，不是排名或完整目录。

| 资产 | 严格类别 | 更匹配的场景 | 技术与边界 |
| --- | --- | --- | --- |
| [Material 3](https://m3.material.io/) | 完整通用设计体系 | 跨平台消费产品、Google/Android 生态 | 设计语言不等于某个 Web 实现；Web 组件维护状态另核验 |
| [GOV.UK Design System](https://design-system.service.gov.uk/) | 公共服务设计体系 | 高责任、表单密集的公共服务 | 模式强调完整任务、内容和恢复；品牌样式不外推到其他组织 |
| [USWDS](https://designsystem.digital.gov/) | 公共服务设计体系 | 美国联邦网站与数字服务 | 可按原则、UX 指南和代码分层采用；项目适用性与法定要求另核验 |
| [Ant Design](https://ant.design/) | 企业 Web 设计体系 + React 组件库 | 中后台、表单、数据密集业务 | 三层 tokens 和主题算法成熟；服从项目当前主版本，不自动升级 |
| [Astryx](https://astryx.atmeta.com/) | React 设计体系 + 组件 / 模式 + CLI / MCP | React 19+、希望用一致 API 与语义 tokens 支撑人与 Agent 共用的 Web 项目 | 2026-09-02 为 Beta、core/CLI `0.5.2`；StyleX 约束作者侧且仍为 peer dependency，消费者默认用预编译 CSS、typed props 与 `className`；只维护最新版本安全更新，须单路径试片 |
| [Fluent 2](https://fluent2.microsoft.design/) | 完整通用设计体系 | Microsoft 生态、生产力工具 | global/alias tokens，支持 light/dark/high-contrast/brand；代码与品牌资产许可分开 |
| [Carbon](https://carbondesignsystem.com/) | 完整企业设计体系 | 数据密集 B2B、IBM 风格产品 | 有组件、模式、tokens 和可访问性指南；品牌识别较强 |
| [Spectrum / React Spectrum](https://react-spectrum.adobe.com/) | 完整体系 + React 实现 | 创意工具、复杂专业工作台 | 可访问、响应式和国际化基础完整；深改视觉时评估 React Aria |
| [PatternFly](https://www.patternfly.org/) | 领域型企业设计体系 | 云、基础设施和运维控制台 | 包含 foundations、patterns、React/HTML 与 a11y；领域语言和密度明显 |
| [Primer](https://primer.style/product/) | 企业产品设计体系 | 开发者工具、代码协作 | foundations、React/CSS 和可访问性资源面向 GitHub 产品语境 |
| [Atlassian Design System](https://atlassian.design/) | 企业产品设计体系 | 协作、项目管理、知识工作 | tokens 与组件指南可参考；逐包核验对外可用性和许可 |
| [TDesign](https://github.com/Tencent/tdesign) | 跨栈企业设计体系 | 中文企业产品、跨 Vue/React/小程序 | MIT；各目标平台成熟度需分别核验 |
| [Arco Design](https://github.com/arco-design) | 企业设计体系 + React/Vue 组件 | 中后台、主题与物料扩展 | MIT 代码仓为主；按 React/Vue 子库分别核验维护和 a11y |
| [Semi Design](https://semi.design/) | React 企业设计体系 / 组件库 | React 中后台、深度品牌定制 | tokens 和设计资源丰富；项目仍需验证组合后的键盘、焦点和读屏 |
| [Element Plus](https://element-plus.org/) | Vue 3 组件库 | 已确定 Vue 3、需要成熟常用组件 | MIT；不能因组件多就视为完整设计体系，a11y 按组件实测 |

## 三、选型矩阵

按顺序裁决，不用总分掩盖硬门槛：

1. **继承与领域**：现有体系能否覆盖；候选是否匹配任务、领域、受众和品牌，而不是只看外观。
2. **技术与维护**：框架、渲染模式、浏览器、包体、维护状态、破坏性升级和团队能力是否匹配。
3. **任务覆盖**：表格、表单、导航、反馈、国际化、主题和关键复杂控件是否覆盖真实场景。
4. **可访问性证据**：是否公开语义、键盘、焦点和测试说明；官方自述只是基础，项目组合仍需验证。
5. **tokens 与定制**：能否通过语义 tokens 和受支持 API 适配；若必须大量覆盖内部样式，应降低优先级。
6. **许可与资产**：代码、字体、图标、Logo、商标、Figma 资源分别核验，MIT/Apache 代码许可不能外推到全部资产。
7. **采用层级**：按 `原则 -> UX 指南 -> 代码` 判断实际采用深度；复用组件不等于原则、模式、内容和治理已经成熟。
8. **迁移与退出**：先用一个真实关键路径做试片；定义升级责任、替换成本和不通过时的停止条件。

## 三 A、Agent-Ready 设计系统门禁

`Agent-Ready` 是待验证属性，不是设计系统类别、厂商标签或采用结论。先区分两层约束：

- **系统作者侧**：用 typed props、语义 tokens、统一 API、lint / typecheck、组件测试和可访问性门禁约束进入系统的实现，减少原始值、分叉惯例和隐式行为。
- **业务消费者侧**：优先使用受支持的组件、props、主题和模式，同时保留明确的 `className`、slot、theme、swizzle 或其它 escape hatch；逃生口必须记录缺口、影响、Owner 和是否应回流系统，不能靠禁止定制掩盖组件缺失。

评估时使用同一组描述**用户体验、内容、状态和任务结果**的 prompt，不在 prompt 中给出组件名或 props 答案；固定 runner、model、输入、来源版本和环境，隔离各条件上下文，再由独立 Judge 横向评审。至少观察：

1. **发现正确性**：是否选到存在且适合的组件、import 和 props，出现哪些幻觉或命名混淆。
2. **决策负担**：每个 UI 元素还需由 Agent 自行决定多少布局、样式、状态和可访问性细节；只作条件间相对比较，不设跨项目固定阈值。
3. **语义约束**：语义 tokens、受支持 variants 和组件行为的使用情况，是否散落原始颜色、像素值和重复 CSS。
4. **escape hatch**：何处退出组件体系、为何退出、是否仍保持主题、键盘、焦点、状态和升级能力；零逃生口不是机械目标。
5. **真实结果**：目标任务、loading / empty / error / success、长内容、响应式、键盘焦点和可访问性是否在运行环境成立；静态源码和厂商文档不替代运行证据。
6. **可恢复性**：组件 / props 未发现、API 变化或升级失败时，能否从当前源码生成的 CLI / 机器可读文档、错误信息和 codemod 回到正确路径。

Agent-Ready 结论必须把四层写成一条可执行链：`约束载体 | 当前版本来源入口 | 错误 / 升级恢复路径 | 运行验收证据与 Owner`。只写规则、只加 lint、只提供文档或只展示一次成功都不能替代其余三层；缺组件、错误 prop、API 变化和过度 escape hatch 必须各有可发现、可恢复、可验证的处理路径。

`AGENTS.md` 只保存项目实际采用后的精简入口、当前版本和权威命令，不复制完整组件索引或设计规则。稳定约束应进入组件 API、tokens、类型、lint、测试和构建门禁；外部 CLI / MCP 只能在审查供应链并获得安装或联网授权后使用。

Astryx 的官方材料能证明其当前公开结构和项目自测方法，不能独立证明目标项目效果。采用前填写：`项目当前体系 / React 与渲染范围 | Astryx 精确版本与状态 | 作者侧约束 | 消费侧 API / escape hatch | CLI / 文档 / 源码版本一致性 | 任务覆盖 / a11y / 主题 | breaking changes 与 codemod 覆盖盲区 | canary / 安全支持 | 试片证据 | 退出成本 | Owner`。截至 2026-09-02，它要求 React 19+，core 和 CLI 为 `0.5.2`，仍处 Beta；`@stylexjs/stylex` 是 peer dependency，部分包仅 canary，安全策略只覆盖最新版本。已有体系稳定、版本不兼容、需要大量内部覆盖、组件发现 / 幻觉 props / escape hatch 未改善，或升级与回退不能验证时，不采用或停止扩大。

## 四、Ant Design B+ 采用边界

Ant Design 是运营 / 管理类 Web 的完整采用候选，不是所有 Web 客户端的统一皮肤。先为每个应用 / 客户端记录 Ant Design Adoption Profile：`应用 / 客户端 | 项目当前版本 | 采用深度 | 主题策略 | 组件映射 | 偏离项 | Owner | 兼容性证据`。

- **共享内核**：只跨端共享业务语义、语义 tokens 与组件行为，包括主次操作、危险动作、输入与校验、选择、反馈、Modal / Drawer，以及 focus、disabled、loading、empty、error 和 success。跨端权威不暴露 Ant Design 内部 token 名、class、DOM 结构或桌面布局模板。
- **运营 / 管理 Web**：产品姿态明确为“完整采用”且项目兼容时，优先使用当前项目版本的表格、表单、筛选、分页、Tabs、Drawer、Modal、Notification 等组件与模式；密度按高频任务校准，通过受支持的 theme、语义 token 和 component token 定制，不散落覆盖内部选择器。
- **C 端浏览器 / H5**：默认只继承共享内核，品牌、信息密度、导航、页面模板、触控目标和内容节奏独立设计；不把运营后台的表格密度、侧栏、筛选区或弹层习惯机械复制过去。若考虑 Ant Design Mobile，按独立候选重新核验，不因采用桌面 Ant Design 自动纳入。
- **版本与兼容门禁**：先记录项目已安装的精确主版本、React 与浏览器范围、图标包、现有主题入口和自定义选择器。若采用或迁移 v6，按官方迁移说明核对 React 18 及以上、现代浏览器与 CSS variables、`@ant-design/icons` 6 及以上，以及依赖内部 DOM / class 的样式；版本未知或需升级时止于方案和试片，不安装、不迁移。
- **验证试片**：至少选一条运营真实路径验证表格、筛选、表单、错误恢复、键盘和焦点；再选一条 C 端或 H5 路径验证共享语义成立且品牌、密度、导航和触控没有被后台模板污染。官方组件或可访问性说明不替代组合后的项目验证。

组件规范最小字段：`组件 / 来源 | 语义 tokens | 状态 | 交互与反馈 | 响应式 | 可访问性 | 偏离项 | Owner`。偏离必须回指任务、品牌或兼容证据；无证据的偏离归零，无法满足关键任务或兼容门禁则停止采用。

B+ 采用结论还必须逐端填写真实路径试片：`应用 / 客户端 | 真实任务与入口到结果 | loading / empty / error / success / disabled / focus | 键盘与焦点或触控 | 长内容 / 目标设备 | 后台模板污染检查 | 实际证据 | 停止条件 | Owner`。静态检查、截图、官方组件说明或“完整状态”概述不能替代逐项结果；未走查的项明确标为未验证。

不得只写“建立 / 记录 Adoption Profile”或“做真实路径验证”：最终结论必须展开上述表头和 Adoption Profile 表头，并为范围内每个应用 / 客户端至少填写一行当前值。混合采用或维持既有 C 端体系时，仍须分别给出后台与 C 端的当前 Profile 和当前真实路径；未来单组件迁移试片只能追加，不能替代这两端证据。

- Ant Design Mobile 的独立候选结论必须补维护状态、包级许可、真实任务覆盖、现有移动体系迁移成本和退出条件，不因同属 Ant 自动通过。
- 已有稳定设计系统的替换候选必须补迁移 Owner、成本、回退路径和停止条件；缺任一项时维持现状，不启动替换。

## 五、无样式原语与开放代码

| 资产 | 正确定位 | 适合 | 不负责 |
| --- | --- | --- | --- |
| [React Aria](https://react-spectrum.adobe.com/react-aria/) | React 无样式组件与 hooks | 自建设计系统，需要可访问性、国际化和多输入行为基础 | 品牌视觉、tokens、页面模式 |
| [Radix Primitives](https://www.radix-ui.com/primitives/docs/overview/introduction) | React 无样式行为原语 | 自建设计系统，复用 dialog/menu/popover 等复杂行为 | 完整组件库、视觉系统、端到端内容与 a11y 验收 |
| [shadcn/ui](https://ui.shadcn.com/docs) | 开放代码分发 | 希望拥有并直接修改组件源码的团队 | 传统包式升级、完整设计系统和项目治理 |

shadcn/ui 不是传统组件库，官方定位是组件集合与代码分发平台；复制源码后，升级、修复、安全、一致性和可访问性责任转移给项目。React Aria 和 Radix Primitives 也不是完整设计体系，不能因为复杂控件可用就跳过视觉基础、页面模式和治理。

## 六、最小选型结论格式

```text
项目事实与继承项：
候选类别与候选：
硬门槛 / 排除项：
领域、技术、状态与 a11y 对照：
tokens、维护、迁移与许可：
Agent-Ready 证据（适用时）：
主选 / 备选及理由：
真实路径试片：
停止条件与 Owner：
```
