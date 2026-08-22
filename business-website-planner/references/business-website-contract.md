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

## 四、简单指标建议

按业务类型和公司成熟度给出三至六项：

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

## 六、默认设计载体与交接

官网设计稿默认使用 Figma。使用者明确指定其他载体时记录 override；Figma 默认不构成写入授权。

交接至少记录 UI Owner、design carrier、Figma 写入授权状态、工程 Owner、验收 Owner、Legal/Data 条件和停止条件。

## 七、结构化格式

校验器使用六个 fenced blocks：

- `business-website-plan`
- `website-modules`，包含 `[module]`
- `metric-suggestions`，包含 `[metric]`
- `reference-dna`，包含 `[reference]`
- `responsive-media`，包含 `[media]`
- `website-handoff`

字段和正负例以 `fixtures/` 为可执行权威；本文件不复制完整 fixture。
