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
| 复核可访问性依据 | `二、开放标准` | 不把自动检查等同于合规 |
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
- 核验版本：Skill frontmatter `4.0.3`；核验日期 2026-07-30。
- 读取状态：仓库 README、Skill 正文、`shape`、`new-work`、`operate`、`critique`、`harden` 相关 reference 与许可证已读取。
- 许可：Apache License 2.0。
- 使用范围：核对设计前 brief、变更范围、界面任务类型、任务型产品界面、状态完备、韧性和有边界的评审方法。

### Vercel Web Interface Guidelines

- Skill 来源：`https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines`
- 规则来源：`https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md`
- 核验版本：Skill metadata `1.0.0`；核验日期 2026-07-30。
- 读取状态：Skill 正文与规则正文已读取；上游仓库声明 MIT License。
- 使用范围：核对语义 HTML、焦点、表单、动效、内容范围、导航状态、触控、本地化和 UI 代码评审线索。

## 二、开放标准

### WCAG 2.2

- 来源：`https://www.w3.org/TR/WCAG22/`
- 版本：W3C Recommendation，2024-12-12；核验日期 2026-07-30。
- 使用范围：作为可感知、可操作、可理解和健壮性的可测试标准来源；默认设计基线为 AA，但项目是否符合仍需逐项验证。

### ARIA Authoring Practices Guide

- 来源：`https://www.w3.org/WAI/ARIA/apg/`
- 核验日期：2026-07-30。
- 使用范围：核对常见 widget 的角色、状态、属性、键盘支持、landmark、可访问名称和功能示例；优先原生语义，不把 ARIA 当作补丁。

## 三、设计系统与 UI 生态

以下官方来源均于 2026-07-30 核验。类别、适用边界和选型结论以 `ui-library-landscape.md` 为唯一权威；本节只保留复核入口和来源边界。

- 设计体系与实现：[Material 3](https://m3.material.io/)、[Ant Design](https://ant.design/docs/spec/overview/)、[Ant Design theme](https://ant.design/docs/react/customize-theme/)、[Fluent 2](https://fluent2.microsoft.design/)、[Fluent design tokens](https://fluent2.microsoft.design/design-tokens)、[Fluent accessibility](https://fluent2.microsoft.design/accessibility)、[Carbon](https://carbondesignsystem.com/all-about-carbon/what-is-carbon/)、[Carbon accessibility](https://carbondesignsystem.com/guidelines/accessibility/overview/)、[PatternFly](https://www.patternfly.org/get-started/about-patternfly/)、[Spectrum](https://spectrum.adobe.com/)、[React Spectrum](https://react-spectrum.adobe.com/)、[Primer](https://primer.style/product/getting-started/foundations/)、[Atlassian Design System](https://atlassian.design/foundations)。
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
- 本 Skill 只吸收经标准校正后的抽象方法，不依赖外部仓库、联网抓取、npm 包、Hooks、subagent 数量或项目状态目录。

## 六、已吸收

- 设计前先确认目的、用户、真实内容、约束和现有视觉权威。
- 区分局部优化、体系扩展、新界面和重设计，避免局部需求引发无关视觉重构。
- 以任务型、转化型、阅读型和展示型界面校准信息密度、熟悉度和表现力。
- 把信息架构、关键路径、状态矩阵、响应式、可访问性和失败恢复写成设计契约。
- 任务型产品界面优先熟悉、一致和高效，营销或展示界面才提高视觉表达权重。
- 评审结合独立设计判断、源码/浏览器证据和确定性检查，并限制无休止润色。
- 把设计契约、可操作原型、实现证据和用户/运行证据分层表达；用任务测试与 Design QA 补足“设计说明不等于可用”的证据缺口。
- 以 WCAG 2.2 和 ARIA APG 校正审美型建议，不让视觉差异性压过键盘、焦点、语义和恢复能力。
- 把完整设计体系、领域设计体系、组件库、无样式行为原语和开放代码分发分开选型，不输出跨项目总冠军。
- 东方审美按用户目标和真实资产加载，以名实、时位和知止约束留白、疏密、层次、色材与 CJK 排版，不套传统符号包。

## 七、未吸收

- 未吸收原生 iOS / Android 的 HIG、Material Design 或平台控件规范；本 Skill 只负责 Web 与浏览器应用界面。
- 未复制外部 Skill 原文、命令表、代码、规则文件、脚本、安装器、Hooks、状态目录或持久化机制。
- 未吸收每次运行都在线抓取最新规则、自动安装依赖、修改项目配置或写入用户目录的行为。
- 未吸收强制多 Agent、固定评审轮数、随机概念选择、固定候选数量或必须生成设计上下文文件的流程。
- 未把“禁用某字体、颜色或构图”写成跨场景绝对规则；任务型产品、既有品牌和用户明确 brief 优先。
- 未把 star 数、厂商宣传、自动 detector 或静态截图当作设计质量和可访问性已经成立的证据。
- 未安装、复制或依赖上述设计系统、组件库、CLI、MCP、Figma 资源或 Agent Skill，也未授权项目升级、迁移和依赖变更。
- 未把水墨、米色、红金、书法、印章、窗棂或屏风写成东方审美默认答案。
