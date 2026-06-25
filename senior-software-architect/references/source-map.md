# 架构师公开来源与应用记录
本文记录 `资深架构师` Skill 已参考的公开工程资料、读取状态、应用位置和不吸收边界。它不是架构方法论正文；处理具体架构、Review、测试、生产变更或 AI 协作时，仍应读取对应专项 reference。
## 使用时机
- 需要核对架构师 Skill 吸收过哪些公开来源、来源许可证、读取日期和应用位置。
- 用户要求继续从外部工程实践仓库、文章或指南中提炼可迁移规则。
- 修改 `README.md` 外部参考来源、`coding-review-deep-dive.md`、`workflow.md`、`production-readiness.md` 或相关验证脚本前，需要确认既有归因边界。
## 不适用场景
- 不用于直接回答代码 Review、架构方案、生产变更或测试设计；这些任务应回到对应 reference。
- 不把外部资料当作当前项目事实、组织制度或生产审批结论。
- 不复制外部仓库的脚本、模板、品牌表达、大段原文或未审查资产。
## 读取后必须产出
- 来源状态：URL、读取日期、许可证或归因要求、读取到的公开内容范围。
- 应用记录：迁移成了哪些规则，落到哪些仓库文件。
- 不吸收边界：哪些内容不适合进入本 Skill，原因是什么。
## 需要继续读取的 reference
- 代码 Review 方法读 `coding-review-deep-dive.md`。
- PR、提交、验证和 Git 边界读 `workflow.md`。
- 生产、紧急变更和上线边界读 `production-readiness.md`。
- 外部来源安全和仓库级治理读根目录 `AGENTS.md`。
## 按任务读取索引
| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 核对 Google 工程实践应用记录 | `已参考的公开来源`、`应用记录` | 不重新读取所有 Review 正文 |
| 核对业务用例驱动架构文章应用记录 | `微信公众号文章：软件架构别再瞎设计了`、`应用记录` | 不把宣导性原文当作完整架构方法论 |
| 核对 Clean Architecture 整洁架构文章应用记录 | `微信公众号文章：Clean Architecture 整洁架构`、`应用记录` | 不把四层图、比喻或原文表格复制为固定模板 |
| 核对架构设计三原则文章应用记录 | `微信公众号文章：架构设计三原则`、`应用记录` | 不复制文章案例、代码示例或宣导表达 |
| 核对架构设计真功夫文章应用记录 | `微信公众号文章：认知跃迁16-如何练成架构设计真功夫`、`https://mp.weixin.qq.com/s/6EFJZpH39ryWA3u_Wlxuzw`、作者：`李文强`、2026-06-03 15:54:27、`拆分与合并的 V 字判断`、长期交付成本、小闭环 Ask-or-Decide | 不能替代功能归类、边界划分、颗粒度和长期交付成本判断 |
| 核对架构师底层思维文章应用记录 | `微信公众号文章：架构师底层思维能力要求`、`应用记录` | 不复制原文图片、书籍推荐或鸡汤式表达 |
| 核对通信复杂度文章应用记录 | `微信公众号文章：软件复杂性的本质是通信复杂性`、`应用记录` | 不把通信复杂度绝对化为唯一复杂度来源 |
| 核对软件设计哲学读书笔记应用记录 | `微信公众号文章：《软件设计的哲学》读书笔记组`、`应用记录` | 不把读书笔记写成官方标准或吞异常依据 |
| 核对问题核心诊断与变化治理来源 | `微信公众号文章：问题核心诊断与变化治理组`、`应用记录` | 不把传统文化或医学类比写成架构结论 |
| 核对 DDD、开发原则和架构取舍文章应用记录 | `微信公众号文章：DDD、开发原则与架构取舍组`、`应用记录` | 不复制表格、代码示例、参考资料列表或作者表达 |
| 核对 AI 辅助画图和架构图来源 | `AI 辅助画图与架构图公开来源组`、`应用记录` | 不把工具输出当作架构质量结论 |
| 核对 AI 编码 GSD 工作流文章应用记录 | `微信公众号文章：GSD 工作流`、`应用记录` | 不照搬外部命令、文件体系或自动提交习惯 |
| 核对 Codex 官方团队运行时协作文章应用记录 | `微信公众号文章：Codex 官方团队：如何把 Codex 用到极致`、`应用记录` | 不把平台功能当成当前工具可用性或执行授权 |
| 核对 Ponytail 最小正确实现来源 | `Ponytail Codex 插件`、`应用记录` | 不把插件 hook 或“少写代码”当作默认工程授权 |
| 核对 AI Native 架构师文章应用记录 | `微信公众号文章：放下代码：AI Native是通往架构师的快车道`、`应用记录` | 不把“少写代码”当成放弃编码能力、验证或生产责任 |
| 核对 AI 产品进入旧系统复盘来源 | `微信公众号文章：置身钉内`、`应用记录` | 不把公开转述/OCR 材料当官方事实或架构结论 |
| 核对 AI 全栈工作流文章应用记录 | `微信公众号文章：从一份模糊需求，到一套可开发系统`、`应用记录` | 不把原型或页面愿望当工程边界 |
| 核对需求分析与设计基础文章应用记录 | `微信公众号文章：需求分析和设计活动关键要点总结`、`应用记录` | 不复制 GJB 章节表述、推荐书目或作者表达 |
| 核对业务驱动架构与验证来源 | `业务驱动架构与验证公开来源组`、`应用记录` | 不把通用方法论当作项目事实 |
| 核对业务架构 / 技术架构同质性来源 | `业务驱动架构与验证公开来源组`、`应用记录` | 不把技术平台当产品本身 |
| 新增外部来源 | `读取与归因规则`、`提炼边界` | 不把未读正文的来源标为已吸收 |
| 审查来源是否可继续使用 | `读取与归因规则`、`已参考的公开来源` | 不用历史记录替代最新核验 |
| 需要最新外部 API、SDK、云产品、法规或安全基线结论 | 本文确认来源历史，再回 `workflow.md` 的外部知识时效性门禁 | 不把读取日期当成当前核验日期 |
## 读取与归因规则
- 分析、提炼或吸收外部资料时，必须以实际读取到的正文、仓库文件或官方页面为依据。
- 微信文章等动态页面必须先通过 Playwright 或等价浏览器自动化读取标题、作者、发布时间和正文；如果 Playwright 当前通道失败，但公开 HTML 中可读取到标题、作者、发布时间和正文，也可以写成“公开内容用于参考”，但条目必须同时记录 Playwright 尝试状态、公开 HTML 读取状态和读取日期。
- 未读取到正文、页面删除、只剩验证页或正文为空的条目，只能标为“当前不可复核”或“历史索引线索”，不得作为已吸收来源。
- 对无法读取正文、只剩验证页、动态页面失败、仓库不可访问或许可证不明的来源，只能标为待核验，不得作为已吸收来源。
- 条目中的英文术语、分层名称和能力边界可能是 Skill 为统一输出做的标准化表达，不代表原文逐字表述；需要引用作者原话时必须重新读取正文并核对。
- 进入 Skill 的内容只保留可迁移的方法、检查项、路由和边界；不复制原文、示例、图像、品牌表达或组织内部流程。
- 从文章吸收的内容只作为工程判断问题、检查项、路由和边界，不作为生产、资金、安全、合规、外部 API、SDK、云产品、法规规则或上线结论。
- 涉及许可证、归因或派生要求时，README 或本文必须记录来源和边界；需要复用具体文本、脚本或资产时必须另做许可证确认和供应链安全审查。
- 本文只记录历史读取状态和应用位置，不代表来源仍然最新可用；具体任务涉及外部 API、SDK、云产品、法规、安全基线或支付清算网络时，必须回到 `workflow.md` 的外部知识时效性门禁，重新记录来源、版本或发布日期、适用范围、核验日期和确认方。
## 已参考的公开来源：软件本质与非标工程问题
- 来源/读取/应用：`https://mp.weixin.qq.com/s/rIyajlYyWD38ppLJ9bBSbg`；标题：`回到本质：软件到底应该怎么造？`；作者字段：`建国`；页面 `ct` 字段：`1777106205`；读取日期：2026-06-15。已通过移动端微信 UA 公开 HTML 读取标题、作者、meta 描述和正文。应用到 `architecture.md` 的知识表达与工程验证边界，强调架构师要把业务知识落到对象、规则、约束、接口、测试、监控和反馈，不把代码生成速度当成工程质量。
- 来源/读取/应用：`https://mp.weixin.qq.com/s/j1NQJDM7wpOOI9sIi2SLPA`；标题：`高水平工程师都擅长解决“非标问题”`；作者字段：`杨光西`；页面 `ct` 字段：`1781356080`；读取日期：2026-06-15。已通过移动端微信 UA 公开 HTML 读取标题、作者、meta 描述和正文。应用到 `architecture.md` 和 `scenario-routing.md` 的非标工程问题入口，要求先输出问题机制、影响面、证据、关键不确定性、候选方案、最小可逆实验、验证命令和停止条件，再进入 TDD、实现、重构或 GSD/CAD。
- 未吸收内容：不复制原文、故事、图片、作者表达或标题传播话术；不把外部文章观点写成组织制度、岗位评价、项目事实、执行授权、测试通过、CR 结论或生产审批；不把“回到本质”解释为跳过产品确认、系分、OpenSpec、Harness、测试、发布和回滚。
## 已参考的公开来源：AI Coding 反馈闭环与验证簇
- 来源/读取/应用：`https://mp.weixin.qq.com/s/FwCCJUdAZ2T4RGZMDo_5Fw`；标题：`AI Coding 的反馈闭环：从测试、生产证据到自举验证系统`；作者字段：`证明与计算`；页面 `ct` 字段：`1778945451`；读取日期：2026-06-15。已通过移动端微信 UA 公开 HTML 读取标题、作者、页面时间字段和正文。应用到 `testing.md` 的不变量支撑验证簇，要求把支付、账务、权限、幂等和状态机等高风险事实落到场景测试、属性 / 变形测试、历史回归入口、生产重放样本、有限变异 / 对抗检查、置信度、来源和 CI 分层。
- 未吸收内容：不复制原文、图片、作者表达或标题传播话术；不把测试通过、覆盖率提高、bug 下降、AI 生成测试数量、生产重放、变异测试或对抗测试写成业务正确性事实、项目默认能力、执行授权、CR 结论或生产审批；L5 只作为目标架构，不写成当前已具备能力。
## 已参考的公开来源：架构腐朽与排熵 Loop
- 来源/读取/应用/边界：`https://mp.weixin.qq.com/s/wINKSDQCroWBvf29h567zA`；标题：`深度思考：架构腐朽 & Loop Engineering`；作者字段：`lencx`；账号字段：`浮之静`；读取日期：2026-06-17，2026-06-22 再次读取。`web.open` 未取得正文，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者/账号、meta 描述和正文。应用到 `evolutionary-architecture.md` 的 Architecture Entropy Review（架构腐朽与排熵评审），覆盖可删除性、局部推理边界、承重行为、废弃 API / dead path、概念膨胀、事实源分裂、治理自腐、守卫自检、可执行约束 / 可追溯理由链、时间边界三问、复杂度棘轮、熵增仪表、理由保鲜、非对称稳定性、契约测试、灰度/回滚和最小排熵计划；应用到 `architecture.md` 的架构规则执行点与理由链，应用到 `coding-review-deep-dive.md` 的时间边界 CR 检查。AI Native 和产品专家分别吸收 Loop 编排与产品概念生命周期边界。不复制原文、图片、比喻、作者表达或标题传播话术；不把自动扫描、Loop、Checker 或规则检查写成可以自动删除、迁移、重写、合并、测试通过、CR 结论、执行授权或上线审批。
## 已参考的公开来源：软件设计哲学读书笔记组
- 来源/读取/应用：`https://mp.weixin.qq.com/s/gXhOwvKH5t6BxsxcoqUS2w`；标题：`《软件设计的哲学》：复杂性的本质与模块化设计`；账号字段：`深安斯帕克`；作者字段：`南山斯帕克`；页面 `ct` 字段换算为 2026-06-22 10:38:07 Asia/Shanghai；读取日期：2026-06-23。已通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、账号、发布时间和正文。
- 来源/读取/应用：`https://mp.weixin.qq.com/s/J9d5Ws6rIdsATPbT-UutAA`；标题：`《软件设计的哲学》：实践智慧与超越代码的哲学`；账号字段：`深安斯帕克`；作者字段：`南山斯帕克`；页面 `ct` 字段换算为 2026-06-23 07:47:00 Asia/Shanghai；读取日期：2026-06-23。已通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、账号、发布时间和正文。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `SKILL.md` | 补充深模块与信息隐藏原则，要求用简单接口封装复杂度，警惕浅模块、直通方法、直通变量和公共知识泄露。 |
| `architecture.md` | 增加 `5.3.2 深模块与信息隐藏`，把深模块 / 浅模块、信息隐藏、按任务职责分解、设计两次、多文件小改动信号和“长度不是坏味本身，复杂性才是”纳入架构评审。 |
| `coding-standards.md` | 补充复杂度可控、错误处理低层屏蔽 / 高层聚合、谨慎使用“定义错误不存在”、注释先行、命名面向读者和 TDD 后设计质量回看。 |
| `coding-review-deep-dive.md` | 增加复杂性投资检查，识别浅模块堆叠、直通包装、信息泄露、多文件小改动、战术 AI 代码和 Classitis。 |
| `ai-native-engineering-workflow/SKILL.md`、`references/agent-loop-engineering.md` | 在角色协作 Loop 中增加复杂度投资门禁，要求 AI 生成代码不能只追求测试变绿、PR 变多或代码更短，必须检查理解成本和维护成本。 |
| `README.md`、`scripts/validate-trigger-paths.py` | 补充公开来源记录和防漂移断言。 |
未吸收内容：
- 不复制文章原文、书籍内容、案例、标题传播话术、作者表达或可能受版权保护的材料。
- 不把读书笔记当作 `A Philosophy of Software Design` 官方标准、团队制度、执行授权、测试通过、CR 结论或生产审批。
- 不把“定义错误不存在”解释为吞异常、隐藏资金 / 权限 / 状态机 / 一致性 / 安全 / 审计风险，必须只用于有明确业务语义和测试保护的场景。
- 不把 TDD 反思写成反对测试；测试通过后仍要回看设计是否降低复杂度。
- 不把 AI 生成代码默认判为错误；只把浅模块、直通包装、重复公共知识、AI 注释噪声和只为过测试的实现作为需要设计 / CR 复核的信号。
## 已参考的公开来源：Ponytail 最小正确实现
Ponytail Codex 插件：`https://github.com/DietrichGebert/ponytail`。2026-06-23 通过 Codex marketplace 安装 `ponytail@ponytail` 4.7.0，已读取 manifest、两个 skill 和 lifecycle hooks；manifest 标注 MIT，能力为 Instructions 和 Lifecycle hooks。
应用到 `SKILL.md`、`coding-standards.md`、`coding-review-deep-dive.md` 和 `evolutionary-architecture.md`：只吸收最小正确实现、复用已有代码 / 标准库 / 平台原生 / 已安装依赖、过度设计专项 CR 和可删除复杂度候选；不复制插件内容、命令或 hook，不把 lifecycle hook 写成默认行为，也不把“少写”写成删除必要校验、错误处理、安全/权限/资金兜底、可访问性、持久化意图、幂等、审计或测试的理由。
## 已参考的公开来源：工程实践仓库
### google/eng-practices
- 来源：`https://github.com/google/eng-practices`
- 公开页面：`https://google.github.io/eng-practices/`
- 读取日期：2026-05-27
- 读取状态：GitHub 仓库公开可读；目录树显示公开内容集中在 `review/` 下的 Code Review Guidelines、Reviewer Guide、Change Author Guide 和 emergencies 文档。
- 许可证：仓库 README 声明文档使用 CC-BY 3.0；本仓库只保留提炼后的规则和来源链接，不复制大段原文。
已读取文件：`README.md`、`review/reviewer/standard.md`、`review/reviewer/looking-for.md`、`review/reviewer/navigate.md`、`review/reviewer/speed.md`、`review/reviewer/comments.md`、`review/reviewer/pushback.md`、`review/developer/cl-descriptions.md`、`review/developer/small-cls.md`、`review/developer/handling-comments.md`、`review/emergencies.md`。
应用记录：`README.md` 记录 CC-BY 3.0 来源边界；`coding-review-deep-dive.md` 吸收代码健康、评论分级、争议处理、Review 导航和范围说明；`workflow.md` 吸收自包含小变更、测试随变更、提交/PR 说明质量；`production-readiness.md` 吸收紧急变更边界；`scripts/validate-trigger-paths.py` 增加防漂移断言。
未吸收内容：
- 不把 `google/eng-practices` 扩展为完整架构设计、DDD、分布式一致性、安全架构或生产韧性方法论。
- 不复制 Google 内部术语、示例、组织流程、评审时效数字或只适用于 Google 工具链的表达。
- 不引入外部脚本、GitHub Action、站点构建配置或仓库运行逻辑。
## 已参考的公开来源：架构文章
### 微信公众号文章：软件架构别再瞎设计了
- 来源：`https://mp.weixin.qq.com/s/oZEUWEWEbuKfsafgFOcr8w`
- 标题：`软件架构别再瞎设计了！真正靠谱的架构，从来都是业务用例说了算`
- 公众号：`Linux学`
- 作者：`红煜`
- 发布时间：2026-04-30 07:00
- 读取日期：2026-05-28
- 读取状态：`curl` 返回微信“环境异常”验证页；后续使用 Playwright + 本机 Chrome 成功读取标题、公众号、作者、发布时间和正文。
- 许可证：未见明确复用许可证；本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、图片或作者表达。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `architecture.md` | 在架构评审关注点中补充“核心业务用例、主干流程和验收场景是否先于技术栈、分层、服务拆分和扩展点被定义”；在常见反模式中补充“技术先行架构”。 |
| `fixtures/skill-eval/prompt-cases.json` | 增加架构师正例，验证面对“先定微服务、缓存、MQ、分层”等技术栈先行提示时，技能是否能拉回业务用例、闭环、变化频率和验收场景。 |
未吸收内容：
- 不把文章的宣导性表述、情绪化标题、段落结构或营销语言写入 Skill。
- 不把“业务用例驱动”绝对化为唯一架构约束；正式架构仍必须同时考虑质量属性、团队能力、合规安全、遗留系统、发布运维和可验证性。
- 不新增独立方法论 reference；当前内容与 `architecture.md`、`diagram-output.md` 中“从业务和用例推导技术骨架”的原则一致，只做反模式命名和评审强化。
### 微信公众号文章：Clean Architecture 整洁架构
- 来源：`https://mp.weixin.qq.com/s/7zj5v-B_-fClCYyR3SnMLA`
- 标题：`Clean Architecture 整洁架构`
- 账号：`智氪AI`
- 发布时间：2026-06-03 09:00:00 Asia/Shanghai
- 读取日期：2026-06-03
- 读取状态：已通过移动端微信 UA 公开 HTML 读取标题、账号、发布时间和正文；本轮未执行 Playwright 等价浏览器取证，正文抽取仅用于结构化提炼，不归档文章全文到仓库。
- 许可证：未见明确复用许可证；本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、图示、比喻、表格或作者表达。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `clean-code.md` | 补充 Clean Architecture 以依赖规则为核心的诊断段，明确层数可变、依赖方向不可逆、内层定义 port、外层实现 adapter、Entities 与 DDD Entity 不机械等同。 |
| `coding-review-deep-dive.md` | 增加“伪 Clean 分层”“端口倒置失败”和“Clean Architecture 反向依赖”坏味，要求 Review 看源代码依赖、端口位置和容器外可测试性。 |
| `testing.md` | 增加 Clean Architecture 核心业务与用例测试形态，强调业务规则和用例流程应能不启动数据库、Web 容器或真实 SDK 被验证。 |
| `project-governance-codebase-and-modules.md` | 强化 Wind 模块中的依赖规则落点：`core/biz` 定义 port 和业务契约，`infrastructure` 提供 adapter，不机械套四层模板。 |
| `architecture.md` | 在架构评审问题中补充源代码依赖方向、端口位置、adapter 边界和核心业务可测试性检查。 |
| `README.md` | 新增公开来源记录，说明只吸收依赖规则、依赖反转、业务规则/用例规则分离和可测试性诊断。 |
| `scripts/validate-trigger-paths.py` | 增加关键字符串断言，防止来源记录和 Clean Architecture 诊断规则漂移。 |
未吸收内容：
- 不把 Clean Architecture 固化为必须四层、固定目录名或一套唯一模块模板。
- 不复制文章原文、图示、比喻、表格、标题传播话术或作者表达。
- 不把文章中的示例技术栈、数据库、框架或外部工具写成项目默认选择。
- 不用 Clean / Hexagonal / Onion 的术语争论替代项目本地依赖方向、端口契约、测试和静态扫描。
- 不把“业务逻辑在 Use Case 层”理解为所有业务规则都必须塞进应用服务；稳定领域规则仍应回到领域模型、值对象或领域服务。
## 已参考的公开来源：架构验证方法组
### 业务驱动架构与验证公开来源组
- 读取日期：2026-05-28
- 读取状态：已通过公开网页、官方文档或 Markdown 输出读取正文/页面元数据；`Use-Case 2.0` 官方站点本轮 `curl` 返回 Cloudflare 阻断页，未作为已吸收来源；SEI `Quality Attribute Workshop` 旧直链返回 404，未作为已吸收来源。
- 许可证：SEI、Microsoft Learn、AWS Docs、Dan North 站点未在本轮复用原文；Impact Mapping 站点页脚声明站点内容在未另行说明时使用 CC-BY 4.0。本仓库只保留来源链接、结构化提炼和归因边界，不复制外部正文、图片、示例、模板或脚本。
已读取来源：
- SEI Architecture Tradeoff Analysis Method Collection：`https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/`。公开页面说明 ATAM 用于围绕质量属性目标评估软件架构。
- Microsoft Azure Architecture Center《Use domain analysis to model microservices》：`https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis`。2026-02-23 文档；已读取 Markdown 输出，公开内容用于参考业务域分析、业务能力、限界上下文、统一语言、领域模型和服务边界。
- AWS Well-Architected Framework REL03-BP02：`https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_service_architecture_business_domains.html`。公开内容用于参考围绕业务域和功能定义服务、用限界上下文隔离业务逻辑、按领域差异定义可靠性要求，以及避免按 UI、middleware、database 等技术域组织服务。
- Dan North《Introducing BDD》：`https://dannorth.net/blog/introducing-bdd/`。公开内容用于参考业务价值、行为、故事模板、场景和 Given / When / Then 验收标准如何连接需求、测试和实现。
- Impact Mapping 官方图书页：`https://www.impactmapping.org/book.html`。公开内容用于参考目标、参与方、行为影响和交付物之间的验证链路；具体产品侧交接矩阵以 `product-architecture-expert/references/source-map.md` 和 `product-architecture-methodology.md` 为准，本技能只吸收架构承接所需的追踪边界。
- NASA SWE-052 Bidirectional Traceability：`https://swehb.nasa.gov/x/AwIfBg`。公开内容用于参考需求、设计、代码和测试之间的双向追踪；本仓库只吸收追踪 ID 和验证资产映射，不复制 NASA 流程或表述。
- arc42 Template Overview：`https://arc42.org/overview`。公开内容用于参考架构文档的上下文、构建块、运行时、部署、决策、质量和风险视图；本仓库只吸收设计视图清单，不复制模板正文。
- C4 Model Diagrams：`https://c4model.com/diagrams`。公开内容用于参考 System Context、Container、Component、Code、Dynamic、Deployment 等架构图层次；本仓库只吸收“按需列出设计视图”的检查项，不复制图示。
- ISO/IEC 25010 质量模型公开摘要：`https://iso25000.com/index.php/en/iso-25000-standards/iso-25010`。公开内容用于参考质量属性分类；本仓库只吸收质量属性场景表的提示，不复制标准文本。
- 微信公众号文章《所有的技术架构，本质上都是业务架构》：`https://mp.weixin.qq.com/s/4mOd-ZbtE-J6O-aDPOSUQg` 与《兑现那个问题“产品需要做什么”》：`https://mp.weixin.qq.com/s/dHXUnZI6rVGYqpyqPnjo4w`。作者字段均为 `大象无棱`，页面时间字段分别为 2026-04-25 09:32 与 2026-06-10 09:11 Asia/Shanghai；2026-06-11 首篇通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文，第二篇普通 `curl` 返回微信验证页，随后通过 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文；公开内容用于参考 `architecture.md` 的技术架构服务业务架构、业务同质性、技术平台不是产品和复制成本门禁，`product-architecture-methodology.md` 的价值 / 成本函数，以及 AI Native 生命周期的 GSD/CAD 准入；不复制原文、故事经历、比喻、图片、作者表达或标题传播话术，不把文章观点写成组织制度、客户事实、合规结论、架构批准或 Execution Grant。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `README.md` | 新增业务驱动架构与验证来源组，保留来源链接和不复制边界。 |
| `architecture.md` | 补充质量属性场景化，把业务 driver、触发条件、受影响资产、期望响应、度量验收和架构取舍作为架构评审门禁；补充业务域/限界上下文驱动边界和质量属性口号化反模式。 |
| `product-design.md` | 补充业务驱动验证闭环和业务驱动验证到 TDD 映射矩阵，把目标、参与方、行为、对象/规则、业务域、质量属性和验收示例追踪到工程证据、失败测试、监控数据和人工确认门禁。 |
| `system-analysis-template.md` | 补充产品语义输入追踪 ID、设计视图清单、业务驱动追踪 ID、质量属性场景表和业务驱动验证承接 ID。 |
| `scenario-routing.md` | 强化 PRD/产品方案到系统设计路径，要求业务 driver 先转成服务/模块边界和质量属性场景。 |
| `testing.md` | 补充业务驱动验证进入 TDD 前的可代码化、可观测化和可评审化归类，避免把业务确认、合规确认或运营验收强行写成单元测试。 |
| `fixtures/skill-eval/prompt-cases.json` | 继续使用业务驱动系统设计、业务驱动验证到 TDD 映射、页面/模块先行纠偏和验收种子交接 fixture 验证触发。 |
未吸收内容：
- 不把 ATAM、DDD、BDD、Impact Mapping 或云厂商 Well-Architected 条目写成单一强制流程；项目设计仍以本地业务事实、现有系统、团队能力、生产约束和用户授权为准。
- 不复制外部示例、图、模板、代码、工作坊材料或站点资产。
- 不把云厂商服务建议等同于非云项目或 Wind 项目族的技术选型结论。
## 已参考的公开来源：架构原则与复杂度文章
### 微信公众号文章：架构设计三原则
- 来源：`https://mp.weixin.qq.com/s/wc3xeSbBqb6ktEDz2ZuK7g`
- 标题：`架构8：架构设计三原则`
- 公众号：`泛终端操作系统`
- 作者：`开心就好TF`
- 发布时间：2026-05-18 18:06
- 读取日期：2026-05-28
- 读取状态：已通过移动端微信 UA 公开 HTML 读取标题、公众号、作者、发布时间和正文；随后使用本机 Chrome headless 作为等价浏览器自动化读取到同一页面 DOM 与正文。
- 许可证：未见明确复用许可证；本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、案例、图片、代码示例或作者表达。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `architecture.md` | 将“合适、简单、演化”落成架构决策和评审规则：方案必须匹配当前人力、技术积累、业务规模、运行约束和验证成本；新增组件和抽象要评估结构复杂度、逻辑复杂度、故障面和排障成本；演进式设计应给出当前最小稳定结构、复审触发条件和下一阶段路径。 |
| `README.md` | 新增公开参考来源记录，说明只吸收架构原则、复杂度评审和演进式设计边界。 |
| `scripts/validate-trigger-paths.py` | 增加关键字符串断言，防止架构原则和来源记录漂移。 |
未吸收内容：
- 不复制文章中的公司案例、比喻、可用性计算代码、输出示例、总结段落或原文表达。
- 不把三原则写成替代性完整架构方法论；正式架构仍必须结合业务 driver、质量属性、安全合规、生产约束、团队能力和验证证据。
- 不把“合适、简单、演化”理解为拒绝复杂架构；当业务规模、风险、合规、安全或运行证据真实触发时，仍应通过 ADR、测试、压测、监控、迁移和发布门禁升级架构形态。

### 微信公众号文章：架构师底层思维能力要求
- 来源：`https://mp.weixin.qq.com/s/Veb3P2ug8XVmyBFmIoDJ7Q`
- 标题：`架构师底层思维能力要求-这7种尽早练习`
- 公众号：`面汤放盐`
- 作者：`面汤放盐-uzong`
- 发布时间：2026-04-10 14:42
- 读取日期：2026-05-28
- 读取状态：已通过移动端微信 UA 公开 HTML 读取标题、公众号、作者、发布时间和正文；随后使用本机 Chrome headless 作为等价浏览器自动化读取到同一页面 DOM 与正文。
- 许可证：未见明确复用许可证；本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、图片、书籍推荐、排版结构或作者表达。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `architecture.md` | 在架构师定位中补充底层思维能力表：抽象、逻辑、结构化、批判、成长型、复盘、数据，并把它们转成架构设计、Review、诊断和生产风险判断中的落点与常见误区。 |
| `README.md` | 新增公开参考来源记录，说明只吸收底层思维能力框架和架构判断落点。 |
| `scripts/validate-trigger-paths.py` | 增加关键字符串断言，防止底层思维能力表和来源记录漂移。 |
未吸收内容：
- 不复制文章图片、排版结构、推荐书目、表情符号、原文段落或作者口吻。
- 不把七种思维写成新的完整方法论或评价个人能力的标签；只作为架构师执行设计、Review、诊断和复盘时的判断框架。
- 不把成长型思维、复盘思维或数据思维泛化为用户画像、个人长期偏好或 Skill 自我改进证据。
### 微信公众号文章：软件复杂性的本质是通信复杂性
- 来源：`https://mp.weixin.qq.com/s/1MbijKDxD2B4wa1E9QTnAw`
- 标题：`软件复杂性的本质是通信复杂性`
- 公众号：`高盛盛`
- 作者：`高盛盛`
- 发布时间：2026-03-30 19:31
- 读取日期：2026-05-29
- 读取状态：已通过移动端微信 UA 公开 HTML 读取标题、公众号、作者、发布时间和正文；随后使用本机 Chrome headless 作为等价浏览器自动化读取到同一页面 DOM 与正文。
- 许可证：未见明确复用许可证；本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、图片、SVG 插图、案例段落或作者表达。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `architecture.md` | 补充通信复杂度视角：把架构复杂度落到节点、边、状态传播和可观测性；强调技术选型通常转移复杂度而非消灭复杂度；将解耦、抽象、治理转成边密度、复合节点、环路/隐式状态治理检查；补充通过明确假设删除节点或边的取舍记录。 |
| `scenario-routing.md` | 在技术选型和新依赖组合场景中补充关键节点/通信边、复杂度转移、隐藏状态、观测入口和退出策略。 |
| `adr-and-tradeoff.md` | 在 ADR 模板和取舍维度中补充复杂度位置、关键通信边、隐藏状态、观测入口、退出策略和复审触发条件。 |
| `review-and-output-templates.md` | 在架构方案模板中补充通信复杂度字段，使正式方案能说明关键节点/边、状态传播、隐藏边和复杂度转移。 |
| `product-design.md`、`testing.md` | 补充通信复杂度与业务驱动架构、TDD 的桥接：业务目标、用例和验收示例用于判断节点/边是否必要；测试、观测和评审门禁用于证明关键边上的业务事实、状态传播和失败语义。 |
| `ai-assisted-engineering.md` | 在 OpenSpec 和 AI 生成代码审查中补充隐藏通信边、工具调用、上下文传递、异步任务和重试链路的可追踪、可观测、可复现要求。 |
| `knowledge-graph.md`、`skill-tree-architecture-design.md` | 补充导航和能力地图入口，让通信复杂度可从架构取舍、框架/SDK/Agent 编排和图形表达任务中被发现。 |
| `diagram-output.md` | 补充通信复杂度图形检查：节点责任、边语义、边过密/依赖环、隐藏边、状态传播和故障传播需要在架构图中可见或拆图表达。 |
| `scripts/validate-trigger-paths.py` | 增加关键字符串断言，防止通信复杂度视角、业务驱动/TDD 桥接、图形检查和来源记录漂移。 |
未吸收内容：
- 不复制文章正文、SVG 插图、示例段落、产品对比、作者表达或排版结构。
- 不把 Kolmogorov 复杂性解释扩展为本 Skill 的复杂度理论基础；本仓库只吸收可迁移的架构评审视角和检查项。
- 不把“通信复杂性”绝对化为软件复杂度的唯一来源；正式架构仍必须同时考虑业务语义、领域不变量、数据质量、组织协作、合规安全、生产风险和演进历史。
- 不把文章中的具体框架或工具例子写成产品选型结论；外部框架、Agent 编排、SDK 和工作流工具仍需按项目事实、可观测性、调试成本和维护责任单独评估。
- 系统生长顺序与生命化架构组：微信文章《软件工程最大的 Bug：我们把系统生长顺序做反了》：`https://mp.weixin.qq.com/s/YM0BI6tCXLpwEf8hZuYvYA`；《为什么优秀架构越来越像生命？》：`https://mp.weixin.qq.com/s/95YFNicYQnDRt9SZHrpKnQ`。作者/账号均为 `霍旭东` / `ThinkingInDev`，页面时间字段为 2026-06-08 20:19:14 与 2026-06-09 07:00:00 Asia/Shanghai；2026-06-11 首篇 `web.open` 未取得正文，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考系统 DNA、核心不变量、状态流转、边界、演化规则和事故沉淀式架构，以及复杂系统分化、事件驱动协作、失败可恢复、可观测性、自治/协作平衡；落到 `architecture.md`、`system-analysis-design.md`、`README.md`、AI Native / 产品专家 source-map 与 `scripts/validate-trigger-paths.py`。未吸收原文、图片、比喻、标题传播话术、作者表达或“数字生命”推测；不把生命类比写成架构标准，不把文章观点写成组织制度、项目事实、技术选型结论或执行授权。
### 微信公众号文章：问题核心诊断与变化治理组
- 来源：微信公众号文章《欲读经典，先开心门》：`https://mp.weixin.qq.com/s/qWIVEdD5uSLAQXP7nh1ckA`、《产品的创新｜需求是无止境的吗？》：`https://mp.weixin.qq.com/s/ld3ZqgNL_wJcOCUQz6em2Q`、《一阖一辟谓之变，往来不穷谓之通｜变通》：`https://mp.weixin.qq.com/s/H6dCG9d_RTBHLlKKtMse_Q`、《如何抓住问题的核心？》：`https://mp.weixin.qq.com/s/AMdz3s4GEPDgNibPlq8_2g`。账号字段为 `心性之学`，后三篇作者字段为 `复闲`，页面时间字段分别为 2025-11-21 10:23:51、2025-01-09 05:02:37、2025-05-06 02:29:50、2025-12-19 19:13:26 Asia/Shanghai；2026-06-12 本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文；补充记录：四篇文章均已通过移动端微信 UA `curl` 公开 HTML 读取标题、账号、作者线索、页面时间字段和正文 / meta 正文，其中首篇正文主体来自页面 meta / JS 描述字段。公开内容用于参考反幻觉证据边界、产品概念定名、需求止损、变化治理中的定向、定性、定位、定量顺序，以及整体 / 系统 / 科学和病 / 证 / 症式工程问题分层。应用记录：`architecture.md` 落成 `1.2 问题核心诊断` 与 `5.11 四定变化治理`，`SKILL.md` 落成“先抓病机再开药方”，AI Native 和产品专家分别落成 Round 0D、概念定名与需求止损，README 和 validator 保留来源及防漂移断言。未吸收内容：不复制原文、经典引文、医学/文化判断、图片、标题传播话术或作者表达；不把传统文化、医学类比或个人修习语境写成架构标准、项目事实、合规结论、生产审批或 Execution Grant；不把“病 / 证 / 症”变成医学诊断；不替代源码、测试、监控、用户确认、合规确认或生产事实核验。
### 微信公众号文章：DDD、开发原则与架构取舍组
- 读取日期：2026-06-03
- 读取状态：三篇文章均已通过移动端微信 UA 公开 HTML 读取标题、账号、作者、发布时间和正文；本轮未执行 Playwright 等价浏览器取证，正文抽取仅用于结构化提炼，不归档文章全文到仓库。
- 许可证：未见明确复用许可证；本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、表格、代码示例、图示、参考资料列表或作者表达。
- 微信公众号文章《用了 DDD 还是写不好业务代码？因为你把它当成了架构模式》：`https://mp.weixin.qq.com/s/3A5SAp1Dzw8s3sECM2SNhQ`。账号/作者为 `智氪AI`，发布时间为 2026-06-02 09:00:00 Asia/Shanghai；公开内容用于参考 DDD 战略设计/战术设计、通用语言、限界上下文、上下文映射、防腐层、聚合边界、Repository 语义和应用服务职责。Playwright 未在本轮执行；公开 HTML 中可读取到标题、作者、发布时间和正文。
- 微信公众号文章《7 条开发原则你都知道，但一条都用不对》：`https://mp.weixin.qq.com/s/zJphqS80r3fg_wLXHaFmHQ`。账号/作者为 `智氪AI`，发布时间为 2026-06-01 09:00:00 Asia/Shanghai；公开内容用于参考 DRY、KISS、YAGNI、POLA、Boy Scout Rule、Fail Fast 和 SoC 的判断问题、原则冲突和 CR 表达。Playwright 未在本轮执行；公开 HTML 中可读取到标题、作者、发布时间和正文。
- 微信公众号文章《学了那么多软件架构，现实工作我们该怎么权衡》：`https://mp.weixin.qq.com/s/e1ft2s2Js8K0Zaw6PNfYMQ`。账号/作者为 `智氪AI`，发布时间为 2026-06-01 09:00:00 Asia/Shanghai；公开内容用于参考 DDD、Clean/Hexagonal/Onion、Microservices/SOA、CQRS/Event Sourcing、PACELC/BASE/FLP、12-Factor/Reactive 的收益、代价、前置条件和取舍框架。Playwright 未在本轮执行；公开 HTML 中可读取到标题、作者、发布时间和正文。
应用记录：`architecture.md` 补充 `5.10 架构风格取舍框架`、DDD 战略设计/战术设计分层和常见误读；`clean-code.md` 补充 `1.1 开发原则判断框架`、原则冲突和 Review 表达；`coding-review-deep-dive.md` 补充领域语言判断、DDD 战略缺失、Repository 退化 DAO、原则误用、架构风格误用和原则误用 CR 提示；`README.md` 记录公开参考来源；`scripts/validate-trigger-paths.py` 增加防漂移断言。
未吸收内容：不复制文章原文、表格、代码示例、图示、参考资料列表、标题传播话术、作者表达或具体排版结构；不把 DDD、Clean、微服务、CQRS、Event Sourcing、12-Factor 或 Reactive 写成默认架构套餐；不把 DDD 术语当作命名装饰；不把 DRY、KISS、YAGNI 等原则名直接写成 Review 结论；不把微信公众号文章当作官方标准、法规、安全基线、云产品、SDK/API 或生产上线依据。
## 已参考的公开来源：AI 辅助画图与架构图
### AI 辅助画图与架构图公开来源组
- 读取日期：2026-06-01；追加读取日期：2026-06-07
- 读取状态：微信公众号文章《架构师必备--让AI画架构图》已通过移动端微信 UA 公开 HTML 读取标题、作者/账号、发布时间和正文；本机 Chrome headless 等价浏览器尝试返回异常，未作为正文来源。微信公众号文章《如何让 AI 画出高质量架构图，一个Skill搞定》2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文。C4 Model 与 arc42 沿用“业务驱动架构与验证公开来源组”的既有读取记录，本轮只补充图形化应用；draw.io 官方页面已通过公开 HTML 读取正文。
- 许可证：C4 Model 页面声明站点和示例图使用 CC-BY 4.0；arc42、draw.io 与微信文章本轮不复用原文、模板、图示或站点资产。本仓库只保留来源说明、结构化提炼和归因边界。
已读取来源：
- 微信公众号文章《架构师必备--让AI画架构图》：`https://mp.weixin.qq.com/s/_oR0ycOVQBX9PNkwDspFOg`。作者/账号为 `方兴集`，发布时间为 2026-04-30 16:28:31；公开内容用于参考 AI + draw.io 的自然语言生成、文档转图、图像参考、版本历史、可编辑 draw.io XML 和本地模型/凭据边界。
- 微信公众号文章《如何让 AI 画出高质量架构图，一个Skill搞定》：`https://mp.weixin.qq.com/s/tE0kfJ2ZHeGGz6xCgEp3Zg`。2026-06-07 普通 `curl` 返回微信环境异常验证页；本地 Node Playwright 包不可用，未新增依赖；随后通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文，页面作者字段为 `Davon Dong`，既有账号线索保留 `日积月码`，页面时间字段为 2026-05-12；公开内容用于参考陌生代码库先形成架构描述、再生成可编辑架构图、并通过组件和连接关系迭代校验的图形化理解工作法。
- C4 Model Diagrams：沿用上文既有来源记录，公开内容用于参考 System Context、Container、Component、Code、Dynamic、Deployment 等图形视图，以及按不同 zoom level 面向不同读者讲不同故事。
- arc42 Template Overview：沿用上文既有来源记录，公开内容用于参考架构文档中的 Introduction & Goals、Constraints、Context & Scope、Solution Strategy、Building Block View、Runtime View、Deployment View、Quality Requirements、Risks & Technical Debt 等视图。
- draw.io 官方 GitHub 集成文档：`https://www.drawio.com/docs/integrations/github/`。公开内容用于参考可编辑图文件和源码/文档同库维护、GitHub 权限边界和文件大小提示。
应用记录：
| 应用位置 | 已吸收内容 |
| --- | --- |
| `diagram-output.md` | 新增 AI 辅助可编辑图治理，要求先给出图形 brief，按业务上下文、容器/应用、组件、运行时交互、部署、数据/消息和观测分层拆解；保留 SVG、draw.io XML、Mermaid 或生成脚本等可编辑源；检查敏感信息、版权边界、远程资源、错误连线、异常路径、颜色语义和文本溢出。 |
| `diagram-output.md` | 新增陌生代码库图形化理解包，要求只读提取组件、入口、启动顺序、认证权限、外部系统、数据/消息/状态流、源码锚点和未确认连接，再判断能否进入实现或 CR。 |
| `ai-native-engineering-workflow/references/agentic-engineering-governance.md` | 补充 AI Native Harness 对图形化理解 brief 的调度要求，避免陌生代码库或多模块变更只靠文字总结进入实现。 |
| `skill-tree-platform-leadership-ai.md` | 在技术表达与图文能力中补充 AI 辅助画图只是可编辑草案，架构师仍需校验视图层级、节点责任、箭头语义、敏感信息、版权边界和工程验证闭环。 |
| `README.md` | 新增公开参考来源记录，说明只吸收 AI + draw.io、C4、arc42、draw.io 官方文档中的通用方法和治理边界。 |
| `scripts/validate-trigger-paths.py` | 增加关键字符串断言，防止 AI 辅助可编辑图治理、来源记录和图形能力入口漂移。 |
未吸收内容：
- 不复制微信文章示例图、提示词、项目安装说明、工具宣传语、截图、作者表达或具体工具链配置；不安装《如何让 AI 画出高质量架构图，一个Skill搞定》中提到的外部 Skill。
- 不把 next-ai-draw-io、draw.io、Mermaid、SVG 或 `$fireworks-tech-graph` 的生成结果写成架构质量结论；架构质量仍需回到业务目标、模块边界、接口契约、数据、测试、监控、发布和回滚。
- 不默认把内部文档、代码、客户资料、生产配置或密钥上传到云端 AI 画图工具；涉及 API Key、OAuth 或仓库访问时必须说明数据边界、凭据边界、联网行为和写入范围。
- 不复制 C4、arc42 或 draw.io 的图示、模板、品牌资产、站点样式或完整流程；只吸收视图选择、文档结构和版本化治理的轻量检查项。
## 已参考的公开来源：AI 编码流程治理
### 微信公众号文章：GSD 工作流
- 来源：`https://mp.weixin.qq.com/s/VA_GhniSSrcJotXWlgk_lw`
- 标题：`让AI编程从"越写越烂"到"持续稳定输出"：GSD工作流-适合中大型项目的精准框架。`
- 公众号/作者：`暴走的xiao松鼠`
- 发布时间：2026-05-09 23:53:10 Asia/Shanghai
- 读取日期：2026-06-02
- 读取状态：已通过移动端微信 UA 公开 HTML 读取标题、作者/账号、发布时间、meta 描述和正文；本轮正文抽取仅用于结构化提炼，不归档文章全文到仓库。
- 许可证：未见明确复用许可证；本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、图片、动图、命令说明、XML 示例或作者表达。
应用记录：`ai-assisted-engineering.md` 保留 OpenSpec / Superpowers / Harness / CAD Mode 路由；`ai-large-project-orchestration.md` 落成类 GSD 的大项目编排工作流，覆盖项目上下文账本、初始化流程、阶段拆分、原子任务包、Wave 依赖、GSD-CAD 双层协议、验证矩阵、暂停恢复和收口；`workflow.md`、`scenario-routing.md`、`skill-tree.md`、`skill-tree-platform-leadership-ai.md`、`knowledge-graph.md`、`README.md` 和 `scripts/validate-trigger-paths.py` 同步治理入口与防漂移断言。
未吸收内容：
- 不复制 GSD 命令体系、文件模板、XML 示例、动图、截图、工具宣传语、作者口吻或完整外部流程。
- 不默认在项目中创建 `PROJECT.md`、`STATE.md`、`ROADMAP.md`、`CONTEXT.md` 等文件；状态载体优先复用项目已有 OpenSpec、ADR、任务计划、测试矩阵或本地文档。
- 不把“子 Agent + Wave 并行”写成默认开发方式；小修、一次性 demo、快速 MVP 验证和需求不清场景应先走轻量澄清、OpenSpec 或产品/系分补齐。
- 不把自动原子提交视为默认授权；Git 写操作仍遵循项目规则、工具权限和用户明确授权。
- 不把外部工具的命令、术语或自动化习惯凌驾于本仓库 `AGENTS.md`、项目本地规范、OpenSpec、Harness Plan、测试和安全边界之上。
### 微信公众号文章：Codex 官方团队：如何把 Codex 用到极致
- 来源：`https://mp.weixin.qq.com/s/6t8hu_XU48jC3T-fc_B5FQ`
- 标题：`Codex 官方团队：如何把 Codex 用到极致`
- 公众号：`产品设计频道BackChannel`
- 作者：`Daniel`
- 发布时间：2026-05-21 18:51:32 Asia/Shanghai
- 读取日期：2026-06-02
- 读取状态：已通过移动端微信 UA 公开 HTML 读取标题、公众号、作者、发布时间内嵌元数据和正文；本轮正文抽取仅用于结构化提炼，不归档文章全文到仓库。
- 许可证与官方性边界：未见明确复用许可证；该微信文章只作为公开文章来源，不作为 OpenAI 官方当前产品能力、模型、工具可用性或官方承诺依据；涉及 Codex 当前能力时必须核验 OpenAI 官方文档或当前会话工具状态。本仓库只保留来源链接、读取状态、可迁移方法和吸收边界，不复制原文、示例、提示语、目录结构、平台宣传语或作者表达。
应用记录：`ai-assisted-engineering.md` 新增 Codex 运行时协作模式，把 durable / pinned thread、voice / transcript、steering / queuing、thread automation / scheduled automation、goal、side panel / artifact 和 shared written context 转成工程协作入口；`ai-large-project-orchestration.md` 要求 automation、goal、artifact 和 written context 绑定 verifier、停止条件、状态位置、权限边界和人工确认点；`README.md` 和 `scripts/validate-trigger-paths.py` 记录来源边界与防漂移断言。
未吸收内容：
- 不把 Codex app 功能清单写成当前会话一定可用的工具能力，也不把该微信文章当作 OpenAI 官方当前能力、产品可用性、模型、工具或路线图承诺；涉及 Codex 当前能力时必须核验 OpenAI 官方文档或当前会话工具状态。
- 不默认创建 pinned thread、automation、goal、vault、外部 connector、长期 memory，不默认访问 Slack、Gmail、Calendar、浏览器登录态、桌面 GUI、外部 API、客户数据、生产配置或私有资料。
- 不把 voice/transcript、thread transcript、queue 或 automation 当作规格、授权、验证结果或 Git/部署许可；不复制文章示例、提示语、目录结构、作者表达、平台宣传语或未核验的未来能力。
### 微信公众号文章：放下代码：AI Native是通往架构师的快车道
- 来源/读取/应用：`https://mp.weixin.qq.com/s/fhEzrPbeez-_2bmJHqExCQ`；标题：`放下代码：AI Native是通往架构师的快车道`；公众号/作者：`大数据随笔`；发布时间：2026-05-23 12:00:00 Asia/Shanghai；读取日期：2026-06-02。已通过移动端微信 UA 公开 HTML 读取标题、作者、发布时间和正文；本轮未再执行 Playwright 等价浏览器取证，不归档文章全文。应用到 `ai-assisted-engineering.md` 的 AI Native 架构师工作面，覆盖 hardened 标准和 Agent 工作流设计；`ai-large-project-orchestration.md` 转成 OpenSpec、context ledger、GSD Stage/Wave/Atomic Task、验证矩阵和 CAD 候选缺口；`cad-mode.md`、`product-design.md`、`scenario-routing.md`、`README.md` 和 `scripts/validate-trigger-paths.py` 维护 Hardened Candidate 不能直接作为 Execution Grant 的边界。不把“放下代码”理解为放弃编码能力、代码审查、测试、验证或生产责任，不复制文章中的引用案例、岗位判断、作者表达、情绪化标题或传播性措辞。
- 不把 AI 生成 PR 数量、自动化轮数或外部团队案例写成工程质量结论，不把 Agent review / Agent test 替代高风险变更中的人工确认、架构审查、测试证据和生产门禁，不把岗位转型观点写成组织制度、绩效口径、裁员建议或团队角色结论。
### 微信公众号文章：置身钉内
- 来源/读取/应用：`https://mp.weixin.qq.com/s/_D20O0vpPXjSzjAKJmBYuA`；标题：`阿里内网万言离职书《置身钉内》原文，已刷屏`；公众号：`爬梯意外簿`；作者：`Corgi/滕雅辛`；发布时间：2026-06-05 16:21；读取日期：2026-06-07。普通 `curl` 返回微信验证页，随后使用 Codex in-app Browser 的 Playwright 接口读取标题、公众号、作者、发布时间和正文；页面声明内容由 AI 识图整理，仅作为公开转述/OCR 复盘材料。应用到 `ai-assisted-engineering.md` 的“AI 进入旧系统的架构门禁”，覆盖 context 架构、权限与权力边界、旧系统技术债、多端一致性、任务闭环、成本稳定性、可观测审计和演进切片；AI Native 流程和产品专家分别维护“AI 产品工程化准入卡”与“AI 产品发心、定位和用户张力门禁”。不复制原文、项目细节、组织评价、作者表达或标题传播话术；不把公开转述/OCR 内容写成钉钉、ONE 或阿里官方事实，不把单个企业协作产品复盘绝对化为所有 AI 产品或所有 SaaS 的通用结论。
### 微信公众号文章：从一份模糊需求，到一套可开发系统
- 来源/读取/应用：`https://mp.weixin.qq.com/s/HzbdrmNkT-OTRKdQh0c0Ug`；标题：`从一份模糊需求，到一套可开发系统：AI 全栈工作流的一次实战`；作者/账号：`KEEN的创享`；发布时间：2026-06-04 21:39；读取日期：2026-06-07。普通 `curl` / `web.open` 未取得正文或返回微信验证页，随后通过移动端微信 UA 公开 HTML 和 Codex in-app Browser 的 Playwright 接口读取标题、作者、发布时间和正文。应用到 `ai-assisted-engineering.md` 的“可开发系统工程化门禁”，要求从模糊需求、内容/多端原型或高保真 HTML 进入工程前，确认目标/非目标、前后台和多端边界、业务流、对象状态、规则权限、数据安全、接口候选、测试验收和发布路径；AI Native 流程和产品专家维护产品到工程秩序链路。不复制原文、案例项目、页面设计、提示词、技术选型、图片或作者表达；不把高保真原型、AI 生成页面或示例系统当成当前项目工程边界、OpenSpec、Harness Plan 或 Execution Grant。
### 微信公众号文章：架构30：架构思维：需求分析
- 来源/读取/应用：`https://mp.weixin.qq.com/s/B8Rap_MmAKmVN3f7eAnvCw`；标题：`架构30：架构思维：需求分析`；作者字段：`开心就好TF`；页面时间字段：2026-06-07 09:34:00 Asia/Shanghai；读取日期：2026-06-09。`web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文（发布时间取页面时间字段）；用于 `product-design.md` 的需求澄清门禁、`system-analysis-design.md` 的系分前需求分析门禁，以及 AI Native / 产品专家的需求分析结论卡；不复制原文、案例、作者表达、标题传播话术或时间投入比例，不把单篇文章观点写成组织制度、项目事实、执行授权或架构师必须越过产品 owner 的理由。
### 微信公众号文章：标准与需求基线
- 来源/读取/应用：`https://mp.weixin.qq.com/s/W44YHT-9bUCrSjsrZIYItw`；标题：`[013] 标准不是摆设——需求标准、设计标准、编码标准怎么写`。`https://mp.weixin.qq.com/s/MO8EsLHm9QNauNLDQ1Z05Q`；标题：`[014] 85%返工都是需求的锅——为啥说需求是软件的根本`。作者/账号字段为 `AIIIIlIIII`；页面时间字段分别为 2026-05-23 07:24:00 与 2026-05-26 06:21:00 Asia/Shanghai；读取日期：2026-06-09。首篇 `web.open` 未取得正文，随后两篇均通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。应用到 `system-analysis-design.md` 的需求基线和高层/详细设计分工、`coding-standards.md` 的规则原因/示例/验证方式与防御式编程、`testing.md` 的需求驱动测试门禁，并由 AI Native / 产品专家维护需求 / 设计 / 编码标准门禁。不复制原文、适航/DO-178C 语境、标题比例、案例、作者表达或标准条文；不把单篇文章写成通用合规结论、项目制度或 Execution Grant。
- 微信公众号文章《编写高质量代码注释与可读性重构指南》：`https://mp.weixin.qq.com/s/oDZRKB4rNlIrgbuP-qDbDA`。作者字段为 `techfightyang`，账号字段为 `秋之筠的技术哲思`，页面 `ct` 字段转换为 2026-06-13 21:14:40 Asia/Shanghai；2026-06-16 `web.open` 未取得正文，本轮未执行 Playwright 等价浏览器取证，随后通过移动端微信 UA `curl` 公开 HTML 读取标题、作者、发布时间和正文。公开内容用于参考 `coding-standards.md` 的注释规约和 `coding-review-deep-dive.md` 的注释与可读性重构 CR 门禁，要求先用命名、方法抽取、常量/枚举、强类型/值对象和测试表达意图，注释只补充业务约束、设计取舍、外部规则、历史坑点和 Why not；不得用注释掩盖弱命名、长方法、魔法值、弱类型、隐式契约或缺测试。不复制原文、代码示例、表格、排版、作者表达或标题传播话术；不把注释写成替代产品语义、架构设计、测试、源码阅读、CR 结论或验证证据的手段；不擅自删除承载历史决策、兼容说明、迁移参考或用户明确要求保留的注释。
### 微信公众号文章：需求分析和设计活动关键要点总结
- 来源/读取：`https://mp.weixin.qq.com/s/L5npvArj6EZhy20o-AsJ1Q`；标题：`需求分析和设计活动关键要点总结`；公众号：`软件需求分析和设计`；作者：`常识`；发布时间：2026-05-26 10:29:23；读取日期：2026-06-01。已通过移动端微信 UA 公开 HTML 读取标题、公众号、作者、发布时间和正文；随后使用本机 Chrome headless 作为 Playwright 等价浏览器读取到标题、作者、发布时间和正文；未见明确复用许可证。
- 应用记录：`system-analysis-design.md` 补充功能不是头脑风暴功能点，而是对象对外提供的可见、有价值交互行为、正向分解和逆向追溯，以及需求分析外部视角和设计内部视角；`skill-tree-architecture-design.md`、`README.md` 和 `scripts/validate-trigger-paths.py` 同步功能分配追溯、需求/设计分工与防漂移断言。
- 未吸收内容：不复制文章中的 GJB 章节表述、书籍推荐、课程机构推荐、作者自述或原文表达；不把军标/适航语境直接写成通用软件项目强制流程；不把“功能分配”绝对化为排斥用户反馈、业务探索或产品发现。
## 提炼边界
- 代码评审类来源适合沉淀为 Review 判断顺序、评论分级、协作礼仪、变更颗粒度和提交说明质量。
- 不复制文章正文、付费内容、仓库示例、站点图像、品牌表达、组织内部流程或外部脚本。
- 不声称技能代表外部作者、组织或云厂商观点。
- 对当前不可复核、已删除或只剩索引页的文章，不得继续作为已吸收来源；相关能力只能按通用工程方法、项目事实或其他可核验来源表达，并标明待核验。
- 生产、资金、安全、合规、外部 API、SDK、云产品或法规规则，不能从通用 Review 指南推导结论，必须回到对应官方来源和项目事实。
- 外部 API、SDK、云产品、开源组件、法规标准和安全基线具有时效性。引用这类来源时，必须按最新官方来源、项目 lockfile、本地依赖树、合同或专业确认结果复核，并记录核验日期。
- 不把外部文章中的传统文化、医学类比、个人修习语境或作者价值判断写成工程结论；只可吸收问题核心诊断、变化治理、反脑补证据边界和产品/架构协作门禁。
- 与现有 Skill 规则重复时，只升级一个权威位置；其他文件只做摘要和链接，避免规则漂移。
