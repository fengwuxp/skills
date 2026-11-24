# Business Website Contract

## 使用时机

在选择官网组织方式、建议模块、内容、指标、素材和交接时读取。本契约约束官网规划产物，不证明业务事实或设计质量。

## 一、业务权威

开始前记录：公司主体、业务权威来源、业务类型、目标客户、真实范围、非目标、地区/语言、浏览器客户端、允许公开内容、Owner 和停止条件。

缺少会改变定位或公开声明的关键事实时停止。现有网站、参考网站和模型推断都不能反向定义业务。

公开参考使用 `reference_mode`：`none` 表示本轮不使用参考；`public` 表示实际读取公开官网正文；`user-provided` 表示使用者直接提供材料。只有后两种模式需要 reference 记录，`public` 不得用搜索摘要或 `user-provided` 状态代替正文读取。

## 二、组织方式

- `single-page`：业务简单、证据较少或早期公司。
- `core-plus-conditional`：默认建议，按内容密度和客户决策路径组合。
- `multi-business`：多个业务线、客户群或地区，共享公司事实，不复制同构页面。

内容模块是建议，不是固定页面。常用候选包括 Positioning、Services/Products、How It Works、About/Company、Contact/Inquiry，以及按事实生成的 Cases、Industries、Credentials、Resources、FAQ 和 Policies。每个模块记录 `kind: suggested|conditional`、角色、放置建议、证据与 Owner。

## 三、内容契约

每个模块只回答一个明确业务问题：公司做什么、服务谁、提供什么、怎样工作、交付什么、客户承担什么、公司承担什么、为什么可信、下一步是什么。

关键声明必须回到业务权威、Owner 确认、真实案例、资质或其他可复核材料。`Leading`、`Global`、`Official Partner`、效果承诺、市场覆盖和客户 Logo 等强声明没有证据时删除。

规划进入 `ready-for-ui` 时，每个交给 UI 的模块（含条件模块）须在 `evidence` 指明依据，在 `owner` 指明责任人。纯导航可引用已确认的站点结构或目标入口。草稿和待 Owner 审阅的规划可标记待核字段。标记为 `overlap_disposition: remove` 的模块退出交付范围，保留模块的 `handoff_to` 只能指向保留的模块。检查器拦截显式占位值，业务责任人核验依据是否支持实际文案。

### 3.1 跨页面职责契约

多页官网的每个模块除基础字段外，还要声明：

~~~text
page_role
primary_question
client_value
content_depth: summary | decision-support | detailed
handoff_to
overlap_with
overlap_disposition: none | keep-shared | summarize | deep-link | merge | remove
~~~

- page_role 表示模块主要服务的页面职责，不固定页面数量或名称。
- primary_question 是该模块主要回答的一个客户问题；同一问题不能在多个页面以 detailed 重复展开。
- content_depth 区分首页摘要、决策支持和详细说明，不用字数机械判断。
- handoff_to 指向客户完成本模块后应继续阅读或执行的模块；没有下一步写 none。
- overlap_with 使用模块 id；没有重复写 none。
- 有 overlap_with 时必须选择非 none 的 overlap_disposition；没有重复时两项都写 none。
- Header、Footer、品牌和共享 CTA 可以 keep-shared；业务流程、服务详情和公司说明仍需按页面职责判断。
- 单页官网不因本契约被强制拆页；纯视觉调整不重新定义页面职责。

规划结果至少能形成 Page Role Matrix 和 Module Overlap Matrix。每个页面应能用一句话说明主要问题和客户价值，且不存在未声明的 detailed 重复。

## 四、简单指标建议

需要用数字支撑客户判断时，按业务类型和公司成熟度给出相应指标。用户需要填写参考时提供示例值，直接公布已有指标只需对应的确认值。

| 字段 | 含义 |
| --- | --- |
| 指标项 | 当前业务最有说明力的规模、质量、效率、覆盖或结果指标 |
| 业务意义 | 为什么该指标有助于说明业务 |
| 参考示例值 | 一个填写示例，不是事实、区间或行业基准 |
| 使用者确认值 | 使用者确认、替换或删除后的值 |

未确认的参考示例值不得发布。没有确认值时删除数字，或改用不含规模数字的结构性业务说明。

## 五、素材与多屏 Brief

每项媒体记录职责、真实对象、来源、许可、焦点、文字安全区、允许/禁止裁切、横竖版本、目标视口和 Owner。业务证据图片优先保留完整信息，纯装饰图才允许较自由裁切。

多屏细则不在本 Skill 重复，交 `ui-design-expert` 的 Responsive Media Contract。

## 六、设计载体与交接

设计载体按本次交付约定填写。选用 Figma 时单独核对目标与写入授权。

形成交接时，按本轮接收方记录 UI、工程或验收责任及适用的数据条件和停止条件。仅约定内容规划时可止于内容契约。

## 七、结构化格式

结构检查读取以下 fenced blocks。核心块为 `business-website-plan`、`website-modules`。

- `business-website-plan`
- `website-modules`，包含 `[module]`
- `metric-suggestions`（按需），每个 `[metric]` 保留业务意义、确认值及发布状态。
- `reference-dna`（使用公开参考或用户提供的材料时），包含 `[reference]`
- `responsive-media`（含媒体时），各 `[media]` 声明自己的目标视口。计划块提供 `media_target_viewports` 时须列出具体视口，媒体记录须共同覆盖全部约定视口。含媒体的旧计划省略该字段时沿用移动端与大屏覆盖要求。
- `website-handoff`（`ready-for-ui` 或实际交接时）。计划和交接约定 `design_carrier` 时两处须一致；历史 `design_carrier_override` 可继续标记用户明确指定的载体。

每条记录的起止标记须配对。字段和正负例以 `fixtures/` 为可执行权威；本文件不复制完整 fixture。
