# 需求验收测试 Skill 实施计划

**Goal:** 新建 `requirement-acceptance-testing` candidate Skill，把权威需求转成可执行验收测试与跨层证据，并给出需求级 `Pass / Fail / Blocked / Need Owner` 裁决。

**Architecture:** 该 Skill 的主类型是 `product verification`。它独立持有验收契约、证据路由和裁决，不定义需求、不修实现、不替代业务或发布 Owner；测试代码与自动化执行优先复用目标项目现有能力，必要的工程写入仍遵循 `senior-software-architect` 和项目规则。

**Tech Stack:** Markdown、Python 标准库 validator、公开行为 fixtures；运行时按目标项目复用现有单测、API / 契约测试、Browser / Playwright、Storybook、数据库或观测工具，不新增默认依赖。

---

## 1. 经世决策卡

事实与待确认：仓库已有产品验收种子、工程测试、UI Design QA 和发布门禁，但没有独立需求级验收测试入口；公开资料支持规则 / 样例 / 问题分离、用户可见行为测试、API 契约验证、组件多维测试与原子 / 组合验收规则。真实业务和 Web UI Pilot 尚未完成。

名相与责任：名称为 `requirement-acceptance-testing`，中文名“需求验收测试”；它是独立 Checker 和自动化验收能力，不是万能 QA 平台、需求 Owner、实现 Maker 或发布审批者。

时势与变化：Figma / 墨刀视觉证据、Browser / Playwright 和现有测试框架已经具备局部能力，当前适合建立统一契约，不适合重造测试框架或强制 Cucumber、Pact、Storybook。

关键取舍：采用“统一验收契约 + 薄证据路由”；每条标准选择能观察真实结果的最低测试层级，只让少量关键跨层场景进入 E2E。

最小行动：先建立 validator、正负 fixtures、Skill 路由和静态行为候选；随后分别用一个业务逻辑需求和一个 Web UI / 视觉需求做真实 Pilot。

止损与停止：缺权威需求版本、实现目标、测试环境、数据、访问权限或 Owner 时输出 `Blocked`；未经授权不安装依赖、不修改生产、不提交或同步 Skill。

验证与复盘：validator 与 fixtures 只证明契约结构；真实行为改善必须使用相同 runner / model 采集 baseline / candidate，独立盲评后再调整 admission。

采用儒家 / 法家“正名与责任”、周易“变与不变”、道家“知止与少干预”三个镜片；未采用兵家和中医系统观，因为当前核心是职责归位与最小可逆试验，不是竞争、事故或运行病机。

## 2. 文件边界

新建：

- `requirement-acceptance-testing/SKILL.md`
- `requirement-acceptance-testing/admission.json`
- `requirement-acceptance-testing/agents/openai.yaml`
- `requirement-acceptance-testing/references/acceptance-contract.md`
- `requirement-acceptance-testing/references/evidence-routing.md`
- `requirement-acceptance-testing/references/source-map.md`
- `requirement-acceptance-testing/scripts/check_requirement_acceptance.py`
- `requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py`
- `requirement-acceptance-testing/scripts/verify_fixtures.py`
- `requirement-acceptance-testing/fixtures/*.md`
- `fixtures/skill-eval/requirement-acceptance-testing-behavior-cases.json`

最小修改：

- `README.md`
- `wise-agent/references/capability-routing.md`
- `scripts/validate.sh`
- `scripts/validate-trigger-paths.py`

不修改：产品、工程和 UI 专业 Skill 的领域规则；不创建测试框架包装器、浏览器驱动、持久化目录、Hook 或 CI 平台。

## 3. TDD 顺序

1. 先写有效跨层验收报告和四类无效报告：缺需求权威、无证据 Pass、整体 Pass 含必选失败项、截图冒充 UI 交互。
2. 先写 validator 测试并运行，确认因脚本不存在或行为缺失而失败。
3. 实现最小 Markdown parser 与状态 / 引用 / 裁决门禁。
4. 运行测试与 fixtures，修到 GREEN；不在本轮增加测试执行框架。
5. 再写 Skill 正文、证据路由、来源边界、metadata 和 candidate admission。
6. 接入 README、能力地图、统一验证和静态行为契约。

## 4. 验收规则

- 每个 criterion 必须回链 `requirement_anchor`，描述前置条件、动作、可观察结果、不可接受结果和 Owner。
- criterion outcome 使用 `pass / fail / blocked / cant-tell / untested / not-applicable`。
- evidence 必须绑定类型、来源、指纹、环境、方法、结果、时间、生产者、独立 reviewer 和限制。
- UI interaction 不能只凭截图通过；visual fidelity 不能缺设计来源、运行截图和人工视觉复核；manual-owner 不能缺人工决定证据。
- 总体 `Pass` 只在全部 required criterion 通过时成立；required fail -> `Fail`，blocked / untested -> `Blocked`，cant-tell -> `Need Owner`。
- 需求、实现或环境版本变化后旧 evidence 标为失效，重新执行前不得复用。

## 5. 准入与停止

初始 `admission.json` 为 `candidate`，至少保留：

- `RAT-001`：未完成可复现实验的 baseline / candidate 行为盲评。
- `RAT-002`：未完成真实业务逻辑验收 Pilot。
- `RAT-003`：未完成真实 Web UI / 视觉还原验收 Pilot。

静态 validator、fixture 或公开资料均不能关闭以上 blocker。未关闭前不正式同步、安装或宣称生产级需求验收能力。
