# UI 设计实践来源与吸收边界

## 使用时机

当需要复核本 Skill 的外部实践来源、版本、正文读取状态、许可、时效性和未吸收内容时读取。

## 不适用场景

- 不把来源列表当作运行时依赖、外部 Skill 安装说明或当前项目设计事实。
- 不用搜索摘要、star 数或作者声誉代替正文、源码和标准核验。

## 读取后必须产出

- 对具体设计方法的来源归因、适用范围和冲突裁决。
- 对时效性、许可、工具依赖和未吸收内容的明确说明。

## 需要继续读取的 reference

- 本 Skill 的执行方法读取 `design-and-review-workflow.md`。
- 外部来源仅在获得联网授权且需要复核时重新访问；当前运行不依赖这些仓库或网站在线可用。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 复核候选 Skill | `一、候选 Skill`、`五、供应链判断` | 不执行安装命令或 Hooks |
| 复核标准与评审依据 | `二、开放标准与评审依据` | 不把自动检查或启发式等同于合规 |
| 复核 Figma 原型与工程交接 | `二、开放标准与评审依据` 的 Figma 小节 | 不把 MCP 输出当生产代码 |
| 复核 UI 生态选型 | `三、设计系统与 UI 生态` | 不输出永久排名或自动安装 |
| 复核东方审美转译 | `四、华夏与东方审美边界` | 不把现代类比冒充古籍定论 |
| 检查吸收边界 | `六、已吸收`、`七、未吸收` | 不复制外部正文和脚本 |

## 一、候选 Skill

### Anthropic frontend-design

- 来源：`https://github.com/anthropics/skills/tree/main/skills/frontend-design`
- 核验日期：2026-07-30。
- 读取状态：`SKILL.md` 与 `LICENSE.txt` 正文已读取；main 分支未提供独立版本号。
- 许可：Apache License 2.0。
- 使用范围：核对“先理解目的、受众与约束，再建立有意图的视觉方向”和生产级可用界面要求。

### Impeccable

- 来源：`https://github.com/pbakaus/impeccable`
- 核验版本：Skill frontmatter `4.0.4`；核验日期 2026-07-30。
- 读取状态：仓库 README、Skill 正文、`shape`、`new-work`、`operate`、`critique`、`harden` 相关 reference 与许可证已读取。
- 许可：Apache License 2.0。
- 使用范围：核对设计前 brief、变更范围、界面任务类型、任务型产品界面、状态完备、韧性和有边界的评审方法。

### Vercel Web Interface Guidelines

- Skill 来源：`https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines`
- 规则来源：`https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md`
- 核验版本：Skill metadata `1.0.0`；核验日期 2026-07-30。
- 读取状态：Skill 正文与规则正文已读取；上游仓库声明 MIT License。
- 使用范围：核对语义 HTML、焦点、表单、动效、内容范围、导航状态、触控、本地化和 UI 代码评审线索。

### UI/UX Pro Max

- 来源：`https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`
- 核验日期：2026-07-30。
- 读取状态：README、`.claude/skills/ui-ux-pro-max/SKILL.md` 与许可证已读取；仓库声明 MIT License。
- 使用范围：只参考把设计系统、风格、排版、配色和场景建议组织成可检索设计情报的方式；不复制 CLI、数据集、脚本或持久化产物。

### Google Stitch Skills

- 来源：`https://github.com/google-labs-code/stitch-skills`
- 核验日期：2026-07-30；2026-08-20 补读 `plugins/stitch-design/skills/generate-design/SKILL.md`。
- 读取状态：README、`skills/taste-design/SKILL.md`、`plugins/stitch-design/skills/generate-design/SKILL.md` 与许可证已读取；仓库声明 Apache License 2.0。
- 使用范围：只参考“先建立设计方向和评审口径，再调用生成工具”以及按屏幕生成、定向修改、变体和 HTML / 截图交付的分层；该仓库依赖 Stitch / MCP，不是通用 UI 标准或本 Skill 的运行依赖。

### Effective HTML

- 来源：`https://github.com/plannotator/effective-html` 与 `https://github.com/plannotator/effective-html/blob/main/skills/html-prototype/SKILL.md`。
- 核验日期：2026-08-20。
- 读取状态：README、`skills/html-prototype/SKILL.md` 与 MIT 许可证已读取。
- 使用范围：只参考无目标代码库时用自包含 HTML 验证一条可信流程、真实状态、键盘 / 焦点、响应式和浏览器行为，并显式标注生产系统接管点；不复制其正文或把原型当生产实现。

### Claude Design Skill

- 来源：`https://github.com/jiji262/claude-design-skill`。
- 核验日期：2026-07-30。
- 读取状态：README、Skill、reference、测试和 MIT 许可证已读取。
- 使用范围：只参考“单文件浏览器原型 + 真实浏览器验证”的轻量交付方式；其自述来源包含对 Anthropic 内部设计提示的改编，未复制文字、模板或品牌表达。

### Huashu Design

- 来源：`https://github.com/alchaincyf/huashu-design`。
- 核验日期：2026-07-30。
- 读取状态：README、Skill、reference、scripts、assets 和 MIT 许可证已抽样读取。
- 使用范围：只参考可点击 HTML 原型、Playwright 任务验证和交接证据；仓库包含云端能力、脚本、资产和较重工作流，本项目未安装或复制。

### Hallmark

- 二手文章：`https://mp.weixin.qq.com/s/Um3OHfpuBoNwH8qQqIdoeQ`，《又一个神级 skill ，做页面夯爆了。》，账号“AI之后”，发布时间 2026-08-04 19:23；2026-08-05 通过 Codex 桌面内置浏览器实际读取标题、账号、发布时间和正文。
- 一手来源：`https://github.com/Nutlope/hallmark` 与其 `skills/hallmark/SKILL.md`；2026-08-05 实际读取 README、Skill 正文和许可证，仓库为 MIT License，Skill frontmatter `1.1.0`。
- 时效边界：文章、官方 README 与 Skill 正文对主题数和门禁数的表述不一致，数量存在版本漂移，不把精确数量沉淀为稳定能力事实。
- 使用范围：只参考表达型页面的结构指纹检查，以及 URL / 截图参考设计学习中的先诊断、来源能力边界和非复刻原则。

### 产品构建师：视觉层级

- 来源：`https://mp.weixin.qq.com/s/Rp7wIJquOoCy8xAhSaiuxQ`，《产品构建师 | 视觉层级，是审美的第一关》；页面作者显示为“秋哥聊成长”，发布时间 2026-08-12 19:31。
- 读取状态：2026-08-12 常规网页读取失败，随后通过 Codex 桌面内置浏览器实际读取标题、作者、发布时间和正文。
- 使用范围：只吸收“注意顺序与操作顺序分开，视觉权重回指当前首先需要判断的信息”及模糊 / 眯眼、灰度等低成本启发式检查；不复制原文、示例、固定字号或作者表达。
- 边界：不把 `0.5 秒`、字号差两级或位置天然优先等经验写成跨场景硬规则，也不把模糊 / 眯眼、灰度或倒置检查当作眼动、可用性或目标用户证据。

## 二、开放标准与评审依据

### WCAG 2.2

- 来源：`https://www.w3.org/TR/WCAG22/`
- 版本：W3C Recommendation，2024-12-12；核验日期 2026-07-30。
- 使用范围：作为可感知、可操作、可理解和健壮性的可测试标准来源；默认设计基线为 AA，但项目是否符合仍需逐项验证。

### ARIA Authoring Practices Guide

- 来源：`https://www.w3.org/WAI/ARIA/apg/`
- 核验日期：2026-07-30。
- 使用范围：核对常见 widget 的角色、状态、属性、键盘支持、landmark、可访问名称和功能示例；优先原生语义，不把 ARIA 当作补丁。

### GOV.UK Design System

- 来源：`https://design-system.service.gov.uk/` 与 `https://www.gov.uk/guidance/government-design-principles`。
- 核验日期：2026-07-30。
- 使用范围：参考从用户需求出发、以完整任务而非页面为单位设计，以及问题页、确认页、错误恢复和服务不可用等高责任公共服务模式；不把英国政府品牌样式套到其他项目。

### USWDS

- 来源：`https://designsystem.digital.gov/`。
- 核验日期：2026-07-30。
- 使用范围：参考设计系统按 `原则 -> UX 指南 -> 代码` 逐层成熟的治理方式；组件采用不等于产品已具备设计系统能力。

### Nielsen 十项可用性启发式

- 来源：`https://www.nngroup.com/articles/ten-usability-heuristics/`。
- 核验日期：2026-07-30。
- 使用范围：作为专家评审的通用问题分类语言；它不是强制标准、目标用户证据或严重度结论。

### Design Tokens Community Group

- 来源：`https://www.designtokens.org/tr/drafts/format/`。
- 核验版本：稳定版 `v2025.10`；核验日期 2026-07-30。
- 使用范围：需要跨工具交换 design tokens 时，参考 `$type`、`$value`、别名、分组和扩展的格式契约。该规范不是 W3C Standards Track，也不替代命名、Owner、版本、弃用和质量治理。

### Figma MCP、Code Connect 与 Plugin API

- 官方来源：`https://developers.figma.com/docs/figma-mcp-server/`、`https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/`、`https://developers.figma.com/docs/figma-mcp-server/structure-figma-file/`、`https://developers.figma.com/docs/figma-mcp-server/code-connect-integration/`、`https://developers.figma.com/docs/figma-mcp-server/add-custom-rules/`、`https://developers.figma.com/docs/figma-mcp-server/mcp-vs-agent/`、`https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/`、`https://developers.figma.com/docs/plugins/api/properties/nodes-reactions/` 与 `https://developers.figma.com/docs/code-connect/`。
- 官方 Skill 来源：`https://github.com/figma/mcp-server-guide/blob/main/skills/figma-use/SKILL.md`；OpenAI curated 设计生成 Skill 来源：`https://github.com/openai/skills/blob/main/skills/.curated/figma-generate-design/SKILL.md`。
- 核验日期：2026-07-30；Figma MCP、Code Connect 和工具能力属于时效知识，使用前应复核当前状态、权限和客户端支持。
- 官方推荐要点：多数用户优先 Remote MCP，写入画布时配合官方 Agent Skills；文件优先 components、Code Connect、variables、语义命名、Auto Layout、annotations 和 dev resources；设计到代码先取精确节点的 design context，必要时用 metadata 缩小范围，再以 screenshot 校准，并继续遵守项目组件与工程规范。
- 边界：Figma 官方明确 MCP 不是“一键完美生产代码”；Plugin API 的 `setReactionsAsync` 能建立 reactions，但它不是官方强制原型流程，静态截图也不能证明导航、变量、条件或失败恢复已可用。L0/L1/L2 是本项目的工程化证据分层，不是 Figma 官方术语。

本轮本地能力增强（核验日期：2026-08-22）：`figma-design-contract.md` 与 `figma-file-engineering.md` 将上述官方能力落到来源权威、页面清单、命名、文件骨架、资产登记和代码交接字段。它们是本仓库的交付约定，不是 Figma 官方标准；Figma 权限、工具行为和 Code Connect 支持仍需执行前按官方文档重新核验。

### 二轮公开核验：Figma 原型与状态交接（2026-08-22）

- [Figma Dev Mode guide](https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode)：实际读取。吸收 `dev resources`、component playground、Ready for dev、变量 / 图层属性和 Code Connect 作为交接证据；不把自动生成 code snippet 当生产实现。
- [Figma Code Connect](https://help.figma.com/hc/en-us/articles/23920389749655-Code-Connect)：实际读取。吸收“先规划组件映射，再由设计与工程共同 review Dev Mode 输出”；记录 Organization / Enterprise 与 Full / Dev seat 前置条件，不默认项目可用。
- [Figma auto layout guide](https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout)：实际读取。吸收动态内容、fixed / min / max 尺寸和明确记录 `ignore auto layout` 例外；不把绝对定位当默认布局。
- [GOV.UK prototyping](https://design-system.service.gov.uk/get-started/prototyping/) 与 [GOV.UK get started](https://design-system.service.gov.uk/get-started/)：实际读取。吸收原型 Kit / Design System 版本边界、可访问响应式组件和“先用当前组件、再按本服务研究扩展”；不复制 GOV.UK 品牌模板。
- [Storybook component explorers](https://storybook.js.org/tutorials/visual-testing-handbook/react/en/component-explorers/) 与 [visual testing](https://storybook.js.org/tutorials/ui-testing-handbook/react/en/visual-testing)：实际读取。吸收组件隔离、props / state 样例、手工核对与截图回归的分层；不把 Storybook 作为所有项目的硬依赖。
- [Material 3 states](https://m3.material.io/foundations/interaction/states/overview)：实际读取。吸收状态层需可区分、可组合且不能只靠颜色表达；不把 Material 的色值、形状或平台组件套到 Web 项目。
- [Carbon Figma kits](https://carbondesignsystem.com/designing/kits/figma/)：实际读取。吸收组件变体、变量化色彩和多断点画布记录；不复制 Carbon 的品牌、主题或网格模板。

### 设计稿保真审查公开核验（2026-08-22）

- [Figma text resizing](https://help.figma.com/hc/en-us/articles/27378154668951-Adjust-text-dimensions-and-resizing) 与 [Auto Layout properties](https://help.figma.com/hc/en-us/articles/360040451373-Explore-auto-layout-properties)：实际读取。吸收 Auto width / Auto height / Fixed size、hug / fill / fixed / min / max 对换行和重叠的影响；不把 Figma 画布表现外推为浏览器结果。
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) 与 [Understanding Text Spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing)：实际读取。吸收 320 CSS px 重排、文字缩放和用户覆盖文字间距时不得丢失内容或功能的实现复测要求；这些要求用于浏览器证据层，不用静态 Figma 稿宣称 WCAG 符合。
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)：实际读取。吸收在固定浏览器、操作系统、字体和渲染条件下保存并复核截图差异；截图回归只能发现视觉变化，不能替代内容来源、语义、任务或人工判断。

本轮未吸收：任何外部设计系统的 Logo、字体、图片、组件代码、内部 DOM / class、品牌配色、固定断点或项目安装步骤；这些资料只提供可迁移的方法和验证边界。

### 三轮公开核验：视觉还原与跨工具来源（2026-08-22）

- [Figma Tools and prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)、[MCP vs. agent](https://developers.figma.com/docs/figma-mcp-server/mcp-vs-agent/) 与 [Code to canvas](https://developers.figma.com/docs/figma-mcp-server/code-to-canvas/)：实际读取。吸收精确节点 design context、metadata 定位、variables、screenshot、Code Connect 和 code-to-canvas 回环的职责边界；不把 MCP 返回代码或捕获画布当成生产实现。
- [Figma Create skills](https://developers.figma.com/docs/figma-mcp-server/create-skills/) 与 [OpenAI figma-design-to-code](https://github.com/openai/plugins/blob/main/plugins/figma/skills/figma-design-to-code/SKILL.md)：实际读取。吸收“团队专用重复流程才值得建 Skill”“先读 exact node、再适配目标代码库”的边界；不复制外部 Skill 正文，也不新建平行 Figma Skill。
- [Storybook visual testing](https://storybook.js.org/tutorials/ui-testing-handbook/react/en/visual-testing) 与 [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)：实际读取。吸收组件状态隔离、人工核对、固定渲染环境和截图差异复核；Storybook 只在目标项目已有时复用，Playwright 断言进入目标项目测试，不在 Skills 仓库建立前端运行平台。
- [DTCG 2025.10](https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/)：实际读取。它是 W3C Community Group Report，不是 W3C Recommendation；只在真实跨工具 token 交换出现时采用，不把交换格式升级为统一设计工具节点模型。
- [墨刀原型与标注](https://modao.cc/prototyping/create-a-prototype.html)、[设计协作](https://modao.cc/usergrowth/designer.html) 与 [D2C 能力边界](https://modao.cc/ad/blog/ai-prototype-to-vue-code.html)：实际读取。确认公开产品支持分享、Preview、标注、字体 / CSS、切图、导出和生成代码；本轮未发现可供 Agent 使用的公开结构化节点 API，因此只建立分享 / 标注 / 导出薄适配。厂商生成代码按其自身说明也只是基础结构起点，不作为生产准出。

归位结论：Figma 是结构化主路径；墨刀、截图和 PDF 进入统一 Review Contract，但不统一各工具内部节点。该取舍以名实、时位和知止校准：证据名称必须对应实际能力，按当前工具成熟度选择不同路径，并在来源不可访问或证据不足时停止升级结论。

## 三、设计系统与 UI 生态

以下官方来源均于 2026-07-30 核验。类别、适用边界和选型结论以 `ui-library-landscape.md` 为唯一权威；本节只保留复核入口和来源边界。

- 设计体系与实现：[GOV.UK Design System](https://design-system.service.gov.uk/)、[USWDS](https://designsystem.digital.gov/)、[Material 3](https://m3.material.io/)、[Ant Design](https://ant.design/docs/spec/overview/)、[Ant Design theme](https://ant.design/docs/react/customize-theme/)、[Fluent 2](https://fluent2.microsoft.design/)、[Fluent design tokens](https://fluent2.microsoft.design/design-tokens)、[Fluent accessibility](https://fluent2.microsoft.design/accessibility)、[Carbon](https://carbondesignsystem.com/all-about-carbon/what-is-carbon/)、[Carbon accessibility](https://carbondesignsystem.com/guidelines/accessibility/overview/)、[PatternFly](https://www.patternfly.org/get-started/about-patternfly/)、[Spectrum](https://spectrum.adobe.com/)、[React Spectrum](https://react-spectrum.adobe.com/)、[Primer](https://primer.style/product/getting-started/foundations/)、[Atlassian Design System](https://atlassian.design/foundations)。
- Ant Design 专项于 2026-08-21 复核：[主题与 tokens](https://ant.design/docs/react/customize-theme/)、[v6 迁移](https://ant.design/docs/react/migration-v6/)、[Data Entry](https://ant.design/docs/spec/data-entry/)、[Data Display](https://ant.design/docs/spec/data-display/)。只吸收三层 token / 组件 token、数据任务模式和迁移兼容门禁；不固定 latest 版本，不把内部 DOM / class 或运营端视觉写成跨端权威。
- 中文企业生态与组件：[TDesign](https://github.com/Tencent/tdesign)、[Arco Design](https://github.com/arco-design)、[Semi Design](https://semi.design/)、[Element Plus](https://element-plus.org/)。
- 行为原语与源码分发：[React Aria](https://react-spectrum.adobe.com/react-aria/)、[Radix Primitives](https://www.radix-ui.com/primitives/docs/overview/introduction)、[Radix accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility)、[shadcn/ui](https://ui.shadcn.com/docs)。

这些来源属于时效知识，项目选型前重新核验版本、维护状态和兼容性。代码包许可证不能外推到字体、图标、Logo、商标、Figma 或其他设计资产；任何安装、升级或迁移仍需项目证据与用户授权。本仓库不记录 stars、永久“最佳”排名或精确 latest 版本。

## 四、华夏与东方审美边界

- 本仓库 `huaxia-practical-wisdom/references/classical-lenses.md` 与 `decision-practice.md` 提供“名实、时位、知止、最小行动与验证”的现代工程判断镜片。
- `visual-style-directions.md` 把其中少量问题转译为视觉取舍，并补充留白/虚实、疏密/节律、层次/路径、含蓄/显露、色彩/材质和 CJK 排版等可观察变量。
- 这些内容是本项目的现代设计转译，不是古籍原文、唯一思想解释、WCAG、浏览器标准或普遍东方美学定律；需要原典、字源或训诂证据时转交 `hanzi-philology`。
- “文质相称”在本 Skill 中只是形式服务内容和任务的设计检查语，不据此声称已完成古籍考据。

## 五、供应链判断

- Anthropic 与 Vercel 候选体量小、来源明确，适合吸收方法，但各自偏“直接实现”或“代码审查”，不能单独承担完整 UI 设计责任。
- Impeccable 方法覆盖更完整且有公开许可证，但整包包含安装器、Hooks、状态目录、脚本、浏览器流程和持久化约定；本仓库未安装、复制或执行这些资产。
- UI/UX Pro Max 包含可检索数据和生成脚本，Google Stitch Skills 绑定外部生成工具；Effective HTML、Claude Design Skill 与 Huashu Design 还包含原型壳、脚本或额外工作流。它们只提供组织和验证启发，不进入本 Skill 的运行依赖。
- Hallmark 包含主题目录、门禁集合、项目日志和生成约定；本仓库未安装或复制，也不采用 `.hallmark/log.json`、强制 `tokens.css`、CSS 自评分注释或项目持久化机制。
- 本 Skill 只吸收经标准校正后的抽象方法，不依赖外部仓库、联网抓取、npm 包、Hooks、subagent 数量或项目状态目录。

## 六、已吸收

- 设计前先确认目的、用户、真实内容、约束和现有视觉权威。
- 区分局部优化、体系扩展、新界面和重设计，避免局部需求引发无关视觉重构。
- 以任务型、转化型、阅读型和展示型界面校准信息密度、熟悉度和表现力。
- 新建或重设计转化、展示界面时检查结构指纹，让差异回指受众、内容、行动或真实资产；任务型界面不机械追求结构多样性。
- 学习 URL 或截图时按来源能力先做设计 DNA 诊断，区分观察、推断、待确认和来源归因，确认采用轴后再设计，并守住非复刻与使用权边界。
- 把信息架构、关键路径、状态矩阵、响应式、可访问性和失败恢复写成设计契约。
- 任务型产品界面优先熟悉、一致和高效，营销或展示界面才提高视觉表达权重。
- 评审结合独立设计判断、源码/浏览器证据和确定性检查，并限制无休止润色。
- 把设计契约、可操作原型、实现证据和用户/运行证据分层表达；用任务测试与 Design QA 补足“设计说明不等于可用”的证据缺口。
- 将原型分为 L0 流程契约、L1 Figma 可点击原型和 L2 浏览器可运行原型；按验证问题选择最低层级。无目标代码库时，L2 可收敛为一个自包含 HTML 和一条可信流程；Figma 到代码交接仍要求 components、Code Connect、variables、语义命名、Auto Layout、精确节点、design context、screenshot 和浏览器验证。
- 以 WCAG 2.2 和 ARIA APG 校正审美型建议，不让视觉差异性压过键盘、焦点、语义和恢复能力。
- 以 Nielsen 十项可用性启发式统一专家评审语言，但让任务影响和恢复成本决定严重度。
- 以 GOV.UK 的完整任务与错误恢复模式补强高责任服务场景，以 USWDS 的分层成熟模型校准设计系统建设。
- 只在跨工具 token 交换确有需要时采用 DTCG `v2025.10` 格式，不把交换格式冒充治理体系。
- 把完整设计体系、领域设计体系、组件库、无样式行为原语和开放代码分发分开选型，不输出跨项目总冠军。
- 东方审美按用户目标和真实资产加载，以名实、时位和知止约束留白、疏密、层次、色材与 CJK 排版，不套传统符号包。

## 七、未吸收

- 未吸收原生 iOS / Android 的 HIG、Material Design 或平台控件规范；本 Skill 只负责 Web 与浏览器应用界面。
- 未复制外部 Skill 原文、命令表、代码、规则文件、数据集、脚本、安装器、Hooks、状态目录或持久化机制。
- 未吸收每次运行都在线抓取最新规则、自动安装依赖、修改项目配置或写入用户目录的行为。
- 未吸收强制多 Agent、固定评审轮数、随机概念选择、固定候选数量或必须生成设计上下文文件的流程。
- 未吸收 Hallmark 的批量主题/结构目录、精确门禁数量、`.hallmark/log.json`、强制 `tokens.css`、CSS 自评分注释或自动项目记忆。
- 未把“禁用某字体、颜色或构图”写成跨场景绝对规则；任务型产品、既有品牌和用户明确 brief 优先。
- 未把 star 数、厂商宣传、自动 detector 或静态截图当作设计质量和可访问性已经成立的证据。
- 未安装或复制上述候选 Skill、设计系统、组件库、CLI、Stitch / MCP 或 Figma 资产，也未授权项目升级、迁移和依赖变更；运行时只在当前环境已提供且任务需要时路由官方 Figma 能力。
- 未把水墨、米色、红金、书法、印章、窗棂或屏风写成东方审美默认答案。
