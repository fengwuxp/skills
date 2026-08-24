# Business Website Design-Code Skill Backflow Design

日期：2026-08-24
状态：Owner 已确认设计，待书面复核
目标仓库：当前 Skills 源仓库
证据项目：已脱敏的私有业务官网交付案例

## 一、目标

从私有业务官网案例的多轮规划、Figma 设计、设计到代码还原、内容审查、视觉对账、契约测试和工程交付中提炼可复用能力，并以最小改动归入现有 Skills。

本设计只形成回流规格，不修改 Skill 正文、reference、fixture、validator、安装目录或 Git 状态。

成功标准：

1. 每个候选能回到重复任务、人工纠偏、独立 Review 或可执行验证。
2. 优先增强现有权威，不创建平行 Figma 或网站设计 Skill。
3. 私有项目内容只作为证据，不进入共享 Skill 正文或 fixture。
4. 回流内容具有触发、非触发、输入、动作、失败分支、停止条件和验收。
5. 当前 candidate Skills 的 admission blocker 不因回顾性材料被错误关闭。

## 二、范围与非目标

### 范围

- 企业官网跨页面职责规划与内容去重。
- Figma 与代码在多轮修改中的双向对账。
- 静态 UI 源码契约作为补充证据时的使用边界。
- 对已有 Owner 排除项、Git 白名单和证据分层能力做去重判断。

### 非目标

- 不新建 figma-code-reconciliation 或其它顶层 Skill。
- 不复制 figma-use、figma-design-to-code 等官方 Figma Skill 的 API 操作规则。
- 不把私有品牌名、Figma file key、node id、公司文案、会话 id、本机路径写入共享 fixture。
- 不修改 business-website-planner 或 requirement-acceptance-testing 的 admission 状态。
- 不以本项目一次成功关闭 baseline/candidate 重复试验、独立盲评或跨业务 Pilot。
- 不执行 Git、同步、安装或发布。

## 三、来源与证据边界

| Source ID | 类型 | 可用证据 | 使用边界 |
| --- | --- | --- | --- |
| S-ROOT-BUSINESS | 主会话 | 业务定位、品牌隔离、内容与视觉变化轴、Owner 逐轮确认 | 私有会话，只抽象方法 |
| S-ROOT-DELIVERY | 主会话 | Figma 节点还原、代码同步、审查、提交和运行证据 | 私有会话，只抽象方法 |
| S-CHECKERS | 独立 Review | 断点错误、测试假阳性、截图证据不足、资产尺寸与配色检查 | 只保留问题机制与验收规则 |
| S-REPO | 源码与提交 | 页面、契约测试、QA 产物及高频返工文件 | 不复制公司专有文案和素材 |
| S-EXISTING-SKILLS | 现有 Skills | 已有业务官网、Figma、验收、排除项与 Git 交付能力 | 作为去重和归位权威 |

已读取范围包括两条主会话、相关子任务和独立审查结果、案例项目 Git 历史、Figma 对账文档、契约测试及现有 Skills。工具授权记录和重复运行日志不作为独立能力证据。

许可与隐私边界：

- 本地会话和项目材料是用户授权的私有证据，不提交原文。
- 共享行为样例必须使用合成公司、合成页面和合成节点。
- Figma 官方能力边界继续引用现有 source-map.md，不复制官方或第三方 Skill 正文。

## 四、冲突裁决

### 4.1 不要大改与视觉可以大改

两者分别约束不同变化轴。设计任务必须分别声明：

- content_change
- structure_change
- visual_change
- interaction_change

单一 change_mode 不足以表达“内容小改、视觉重构”。

### 4.2 Figma-first 与 Code-first

不存在全局固定顺序。每个变更切片必须声明当前权威端、同步方向、目标端，以及双端是否同时变化。双方均变化且没有 Owner 裁决时，状态为 conflict，不得覆盖任一端。

### 4.3 页面命名反复变化

页面名、导航名和 Figma 图层名必须有版本和 superseded 记录。被排除或被替代名称不能靠后续上下文自动复活；重新采用需要 Owner reopen。

### 4.4 证据等级

Figma metadata、Figma screenshot、源码契约、HTTP 200、浏览器运行证据、目标用户证据和生产观测相互独立。缺少浏览器证据时，只能保留已取得的确定性结果并把视觉条件标为 blocked 或 cant-tell。

## 五、能力单元

## 5.1 Design-Code Reconciliation Contract

状态：accepted

建议落点：

- 增强 ui-design-expert。
- 新增一层直连 reference：ui-design-expert/references/design-code-reconciliation.md。
- SKILL.md 和 prototype-output.md 只增加路由摘要，不复制详细契约。
- 第一阶段只增加 reference、fixture 和行为用例，不增加同步脚本。

稳定职责：在同一页面或区段经历 Figma-first、Code-first、copy-only、geometry、asset 或 interaction 修改时，显式管理权威端、目标端、节点/代码映射、版本、待写回状态和验证证据。

触发：

- 先改设计稿再改代码。
- 代码改完同步回 Figma。
- 做一轮 Figma 与源码对账。
- 这个 node 对不上。
- 跨轮恢复一个未完成的 Figma writeback。

非触发：

- 新建单向 Figma 文件。
- 已确认 Figma 的一次性代码实现，且无回写要求。
- 纯代码 Bug、纯文案讨论或纯视觉审查。
- 只有截图且没有可定位设计源。

前置条件：

- 页面与区段职责已经确认。
- 有 exact Figma node 或明确的 code-only 目标。
- 有代码文件与稳定锚点。
- 当前权威端、目标端、Owner 和写入授权明确。

最小字段：

~~~
reconciliation_id
page_id
section_role
authoritative_surface: figma | code | approved-copy
sync_mode: design-first | code-first | reconcile-only
figma_file
figma_node
figma_revision
code_file
code_anchor
code_revision
content_fingerprint
geometry_fingerprint
pending_target
write_authorization
verification_evidence
status: aligned | source-newer | target-newer | conflict | blocked
owner
~~~

执行顺序：

1. 回读页面职责、当前权威和 Owner 决策。
2. 读取 exact node 与代码锚点，不用截图或旧摘要代替。
3. 分离 copy、geometry、asset、interaction 四类 delta。
4. 判断 design-first、code-first 或 reconcile-only。
5. 只修改目标端；未授权端只记录 pending。
6. 回读目标端，核对内容、节点、字体、尺寸和映射。
7. 按证据层执行 Figma screenshot、契约测试、构建或浏览器 Design QA。
8. 只有双端内容和必要证据一致时标记 aligned。

失败分支：

- exact node 不存在：blocked，重新定位，不猜 node。
- 双端同时变化：conflict，列出差异并交 Owner。
- 无 Figma 写入权限：保留 pending_target=figma，不得用其它设计工具替代。
- 固定文本框溢出：先缩短文案或调整已授权尺寸，截图复测后再继续。
- 浏览器被阻止：确定性验证可以通过，运行视觉条件保持 blocked。

输出：

- 节点级对账表。
- 已执行 delta。
- 未执行 writeback。
- 双端状态与证据。
- 冲突、阻塞和下一 Owner。

验收：

- exact node 与 code anchor 均可回读。
- 同步方向唯一。
- 不存在未说明的双端覆盖。
- copy-only 修改不带入结构重构。
- aligned 行有双端 readback 和最低充分验证。

## 5.2 Cross-Page Role Separation

状态：accepted

建议落点：

- 增强 business-website-planner/references/business-website-contract.md。
- 扩展 website-modules fixture 和 validator。
- SKILL.md 只增加“多页职责去重”路由摘要。

稳定职责：为企业官网的 Home、Services、About、How It Works、Cases 等页面声明唯一主要业务问题、内容深度和跨页交接，避免多个页面重复展开同一套流程。

触发：

- 多页企业官网规划或重构。
- 用户指出 Home、Services、About 内容或布局过于相似。
- 多个区段使用同一流程、卡片组或价值主张。

非触发：

- 单页官网。
- 纯视觉换色、字体或图片调整。
- Header、Footer、CTA 等明确共享组件。
- 不涉及业务官网的后台、商城或内容站。

新增字段：

~~~
page_role
primary_question
client_value
content_depth: summary | decision-support | detailed
handoff_to
overlap_with
overlap_disposition: none | keep-shared | summarize | deep-link | merge | remove
~~~

判定规则：

1. 每个核心页面只有一个 primary_question。
2. 同一完整流程不能在多个页面以 detailed 重复。
3. Home 默认负责定位、价值和下一步，不承担完整服务说明。
4. Services/Products 默认负责服务范围、交付与责任。
5. About 默认负责公司身份、原则和可信依据，不再复制完整服务流程。
6. 共享 Header、Footer、品牌和 CTA 必须标为 keep-shared。
7. 所有重复模块必须有非 none 的 overlap_disposition，不能静默保留；没有重复时 overlap_with 和 overlap_disposition 均为 none。
8. 页面角色来自业务与客户决策路径，不固定要求三页或四页。

输出：

- Page Role Matrix。
- Module Overlap Matrix。
- 每个重复区段的保留、摘要、深链、合并或删除结论。

验收：

- 每个页面能用一句话回答“本页主要解决什么问题”。
- 相邻页面不存在未声明的 detailed 重复。
- 每页有明确 handoff，不形成信息死路。
- 单页与纯视觉任务不会误触发拆页。

## 5.3 Bounded Static UI Source Contracts

状态：candidate

建议落点：

- 不进入 senior-software-architect 的通用测试红线。
- 在 requirement-acceptance-testing/references/evidence-routing.md 增加限制性说明。
- 增加一个 hard-negative fixture，证明源码正则不能单独准出视觉。

有效经验：

- 先提取目标 section，再断言语义和 breakpoint token。
- 对扁平对象使用同对象边界，避免 regex 跨对象匹配。
- 使用负断言防止旧 breakpoint、旧文案或错误路由回流。
- 用 mutation 证明测试会因目标错误而失败。

限制：

- 源码契约观察实现结构，不是最终用户行为。
- 不能替代浏览器布局、截图、交互、键盘、焦点和生产证据。
- 组件重构会使实现细节断言失效。
- 尚无第二个独立项目证据，不晋升为通用工程能力。

第一阶段只增加 fixture 与证据边界，不增加 parser、AST 工具或新依赖。

## 六、去重与拒绝项

| 经验 | 当前权威 | 结论 |
| --- | --- | --- |
| 业务权威先于官网内容 | business-website-planner | 已覆盖 |
| 参考网站只吸收 DNA | business-website-planner | 已覆盖 |
| Page Manifest、Figma 权威链 | ui-design-expert | 已覆盖 |
| text-wrap、overflow、多视口 | design-draft-fidelity-review.md | 已覆盖 |
| Figma 字体加载、Plugin API gotchas | 官方 figma-use | 拒绝复制 |
| exact node 的设计到代码 | 官方 Figma Skills 与 prototype-output.md | 已覆盖 |
| Owner 排除项防复活 | wise-agent state contract | 已覆盖 |
| 白名单暂存、提交、推送授权 | wise-agent code delivery | 已覆盖 |
| 截图不能证明交互 | requirement-acceptance-testing | 已覆盖 |
| 本地浏览器受限时证据降级 | RAT/UI evidence routing | 已覆盖，可补 fixture |
| 单次图片尺寸和禁紫扫描 | 项目内证据 | 暂不沉淀 |
| Figma 405、授权链接和网关白名单 | 工具或环境问题 | 不进入领域 Skill |

## 七、第一阶段实施白名单

~~~
current approved backflow design document
current implementation plan document
ui-design-expert/SKILL.md
ui-design-expert/references/prototype-output.md
ui-design-expert/references/design-code-reconciliation.md
ui-design-expert/fixtures/design-code-reconciliation-valid.md
ui-design-expert/fixtures/design-code-reconciliation-invalid-conflict.md
fixtures/skill-eval/ui-design-visual-reproduction-behavior-cases.json
fixtures/skill-eval/business-website-planner-behavior-cases.json
fixtures/skill-eval/requirement-acceptance-testing-behavior-cases.json
business-website-planner/SKILL.md
business-website-planner/references/business-website-contract.md
business-website-planner/fixtures/business-website-plan-valid.md
business-website-planner/fixtures/business-website-plan-invalid-authority.md
business-website-planner/fixtures/business-website-plan-invalid-metric.md
business-website-planner/fixtures/business-website-plan-invalid-overlap.md
business-website-planner/scripts/check_business_website_plan.py
business-website-planner/scripts/test_check_business_website_plan.py
requirement-acceptance-testing/references/evidence-routing.md
requirement-acceptance-testing/fixtures/acceptance-invalid-source-contract-overclaim.md
requirement-acceptance-testing/scripts/test_check_requirement_acceptance.py
~~~

本白名单只是设计输入，不构成写入或 Git 授权。实施时必须重新检查 dirty worktree，按文件和 hunk 避开现有无关修改。

## 八、验证设计

### 8.1 Design-Code Reconciliation

正例：

1. Figma-first copy-only：先改 exact node，再更新代码和内容契约，双端 readback 后 aligned。
2. Code-first layout fix：代码完成后生成 Figma pending writeback，未授权时不伪装完成。
3. Reconcile-only：双端不同但 Owner 指定权威端，输出最小 delta。

硬负例：

1. 新建单向 Figma 页面，不生成 reconciliation ledger。
2. 只有截图，没有 exact node，不宣称已同步。
3. 双端均变化且无 Owner，不覆盖任一端。
4. Figma 无权限时，不切换墨刀或创建第二文件替代。

### 8.2 Cross-Page Role Separation

正例：

1. 广告官网：Home=定位与价值，Services=范围与交付，About=身份与原则。
2. SaaS 官网：Home=价值，Product=能力，Security=控制，About=公司。

硬负例：

1. 单页早期公司，不强制拆页。
2. 纯视觉重构，不重新定义页面职责。
3. Header、Footer、CTA 合法共享，不判为重复内容。

### 8.3 Source Contract Candidate

- 正则跨区匹配的 invalid fixture 必须失败。
- 删除目标 token 的 mutation 必须使对应断言失败。
- 即使源码契约通过，缺少浏览器证据的视觉条件仍不得判 Pass。

### 8.4 Admission 边界

- ui-design-expert 保持 installable；新增能力需通过静态 fixture 和现有行为门禁。
- business-website-planner 保持 candidate。该案例只能作为 retrospective golden case，不能关闭 BWP-001 或其它跨业务 Pilot。
- requirement-acceptance-testing 保持 candidate。该案例不能替代 baseline/candidate 重复响应与独立盲评。

## 九、实施顺序

1. 先实现 ui-design-expert 的 reconciliation reference、fixture 和行为用例。
2. 再实现 business-website-planner 的 page-role/overlap fields、validator 和 fixtures。
3. 最后只补 RAT 的 source-contract overclaim hard negative。
4. 运行目标脚本、fixture、trigger paths 和仓库统一验证。
5. 由独立 Checker 做规格与质量复核。
6. Owner 决定 promote、继续 candidate 或回退。

## 十、停止条件

- 现有 dirty worktree 与目标文件出现无法安全分离的 hunk。
- 需要修改 Skill 主职责才能容纳候选。
- validator 只能验证文档存在，不能验证目标字段或冲突。
- behavior case 只复述私有案例，无法处理合成新场景。
- 发现 reconciliation 与官方 Figma Skill 的执行规则重复。
- 缺少 Git、同步或安装授权。

## 十一、设计验收

- 不新增顶层 Skill。
- 两个 accepted 能力都有稳定职责、触发、非触发、失败和验收。
- source-contract 保持 candidate，不冒充浏览器证据。
- 现有能力去重明确。
- 私有项目事实不进入共享资产。
- 第一阶段不新增依赖或执行同步。
- 所有修改都能落到白名单和可执行验证。
