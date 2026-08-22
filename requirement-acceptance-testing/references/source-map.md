# 来源与吸收边界

核验日期：2026-08-22。以下均读取公开的一手页面；只吸收可迁移的方法和边界，不复制原文、代码或厂商专属流程。

| 来源 | 吸收内容 | 未吸收与复核边界 |
| --- | --- | --- |
| [Cucumber Example Mapping](https://cucumber.io/docs/bdd/example-mapping/) | 用规则、具体示例、未决问题和新发现故事澄清验收条件 | 不要求采用 Cucumber、彩色卡片或固定会议形式 |
| [Cucumber Gherkin Reference](https://cucumber.io/docs/gherkin/reference/) | `Given / When / Then` 可作为业务可读的可执行示例结构 | 不把语法完整等同于需求正确或测试充分 |
| [Playwright Best Practices](https://playwright.dev/docs/best-practices) | 测试用户可见行为、测试隔离、优先面向用户的定位方式 | 不默认安装 Playwright；只在项目已有或获授权时使用 |
| [Pact: How Pact works](https://docs.pact.io/getting_started/how_pact_works) 与 [Consumer testing](https://docs.pact.io/consumer) | 契约测试核对消费方与提供方共享交互 | 不把契约通过外推为业务功能、数据副作用或端到端通过 |
| [Storybook: Tests](https://storybook.js.org/docs/writing-tests) | 组件交互、视觉与可访问性检查可复用已有组件隔离设施 | 不为一次验收默认引入 Storybook 或托管平台 |
| [W3C ACT Rules Format 1.1](https://www.w3.org/TR/act-rules-format/) | 原子/组合规则、适用性、期望、假设、示例与多值结果启发本契约 | 本 Skill 不是 ACT Rules 实现，也不据此宣称 WCAG 合规 |
| [OpenAI frontend-testing-debugging Skill](https://github.com/openai/plugins/blob/main/plugins/build-web-apps/skills/frontend-testing-debugging/SKILL.md) | 目标流程、浏览器交互、截图、控制台和剩余风险的证据习惯 | 其范围偏前端，不覆盖本 Skill 的业务、API、数据与 Owner 裁决 |
| [OpenAI game-playtest Skill](https://github.com/openai/plugins/blob/main/plugins/game-studio/skills/game-playtest/SKILL.md) | 结构化 playtest、DOM 不足时的视觉证据、严重度与复现信息 | 不吸收游戏领域规则或专用工具链 |
| [Martin Fowler: Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html) | 多用低层快速测试，少量高层端到端测试 | 作为测试分层启发，不机械规定比例 |

仓库内权威边界：`AGENTS.md` 将该类能力定义为 `product verification`；`product-architecture-expert` 提供验收种子，`senior-software-architect` 负责工程测试实现，`ui-design-expert` 提供视觉与交互专业证据，`wise-agent` 可消费最终裁决但不替代独立 Checker。
