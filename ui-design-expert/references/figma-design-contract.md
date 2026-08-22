# Figma 设计契约

本 reference 用于“需要在 Figma 规划完整网站、区分参考稿与目标稿、或要求设计稿可稳定还原代码”的任务。它解决的是来源、页面、状态、命名和交接边界，不替代产品规则、品牌事实或视觉评审。

## 使用时机

在进入 Figma 工具前，或发现参考稿、当前稿、导航规划、页面命名和内容来源不一致时读取。

## 不适用场景

- 不用本 reference 定义产品业务规则、品牌事实或法律文本。
- 已确认设计的纯代码还原不重新设计页面；只读取这里的来源与范围门禁，再交给工程能力。

## 读取后必须产出

- 一份含 `Design Contract`、`Page Manifest`、导航映射、状态覆盖和 Owner 的本地计划。
- 明确参考稿 / 目标稿角色、客户端范围、变更模式、待确认冲突和停止条件。

## 需要继续读取的 reference

- Figma 文件组织、组件、变量、Auto Layout 和代码交接读取 `figma-file-engineering.md`。
- 原型层级、交互证据和浏览器验证读取 `prototype-output.md`。
- 具体产品事实和内容来源回到产品 brief、术语表、资产登记和品牌边界文件。

## 1. 先冻结权威边界

在任何 Figma 写入前，先在本地计划中声明 `Design Contract`：

| 字段 | 要求 |
| --- | --- |
| `project_id` | 项目唯一标识，不能用“最新版”等模糊词 |
| `client_scope` | 明确 Web 客户端范围；使用 `web-pc` 或 `web-mobile`，不同端分别建清单 |
| `change_mode` | `visual-adjustment`、`visual-adjustment-with-bounded-content-optimization`、`system-expansion`、`new-interface` 或 `redesign` |
| `product_source` / `brief_source` | 产品事实与已确认 brief 的来源 |
| `reference_figma` | 参考文件或节点；只提供内容 / 宏观布局 / 视觉 DNA 等明确作用 |
| `target_figma` / `target_role` | 当前目标文件及角色；草稿不得声明为内容权威 |
| `terminology_source` / `asset_registry` / `brand_boundary` | 术语、图片与品牌边界的单一来源 |
| `owner` / `status` | 责任人和 `draft`、`ready-for-figma`、`ready-for-code`、`approved`、`superseded` 状态 |

推荐的最小权威顺序为：产品事实与已确认 brief > 术语 / 资产 / 品牌边界 > 参考 Figma 的明确采用轴 > 当前目标 Figma 草稿 > 局部截图或模型推断。冲突项列为待确认，不通过绘图“猜解”。

`product_source`、`brief_source`、`terminology_source`、`asset_registry` 和 `brand_boundary` 均不得指向当前 `target_figma`；目标稿只能作为待审设计对象，不能反向批准自身内容。

## 2. 用 Page Manifest 先定义整站

每个页面在写入 Figma 前必须有一条 `Page Manifest`，至少包含：

`id / route / display_name / figma_name / purpose / source_node / states / state_exclusions / state_notes / content_source / nav_label / client_scope / status / is_current`

页面命名采用固定层级：

```text
<Web PC|Web Mobile> / <两位顺序> <页面语义名> / <状态或视图> / <基准宽度> / <Draft|Approved|Superseded>
```

约束如下：

- 顺序、路由、导航标签和 Figma frame 名必须一一对应；不使用 `Page 1`、`Final`、`最新版` 等不可检索名称。
- 命名前缀必须与 `client_scope` 一致，末尾状态必须与页面 `status` 一致。
- `source_node` 必须能回到精确节点；参考节点与目标节点不得混写。
- 每页至少声明 `default`，并覆盖 `loading`、`empty`、`error`、`success`、权限、弱网、长内容等适用状态；不适用也要写明理由。
- `state_exclusions` 显式列出不适用的 `loading`、`empty`、`error`、`success`、`permission`、`return`、`close`；没有排除项写 `none`，不能只在自由文本中笼统说明。
- `state_notes` 说明入口、退出、返回、取消、重置、焦点和失败恢复；只画最终成功屏不能算完整页面。
- `content_source` 指向已确认内容；图片、数字、导航术语和法律文本不能由占位内容替代。
- `is_current=true` 的页面才进入导航映射；被替代页面标成 `Superseded`，不从导航中隐式复活。

导航映射必须覆盖全部 current page，并校验 `page_id / route / label` 与清单一致。这样页面、路径和后续代码路由共享同一份可审计输入。

## 3. 设计稿完整性门禁

在 Figma 写入前检查：

1. 页面清单覆盖入口、核心任务、Inquiry / 表单、成功与失败恢复、Legal / Privacy 等承诺页面。
2. 每个页面的文字、图片、数据、导航和 CTA 都来自同一套来源；不要出现“图片像一个业务、文案像另一个业务”的跨页漂移。
3. 参考稿只按已确认采用轴吸收；视觉调整不应意外改写产品定位、业务术语、协议名或合规事实。
4. 同一交互在各页面使用同一命名、状态语义、焦点与反馈；差异必须记录为例外并有 Owner。
5. `target_role`、页面状态、证据引用和 Figma 工程项通过本目录的确定性校验器后，才进入人工 Figma review。

`ready-for-code` 或 `approved` 只接受 `verified` / `completed` 的工程证据；`code_connect` 在前置条件不成立时可标为 `not-applicable` 并保留理由，其余 `planned` 项不能随状态一同准出。

`ready-for-code` 或 `approved` 还要求 `target_role=approved-design`，并且全部 `is_current=true` 页面均为 `approved`；contract 不得越过页面生命周期单独准出。

```bash
python3 ui-design-expert/scripts/check_figma_design_plan.py --file plan.md
```

校验器只证明结构契约成立，不证明视觉质量、可用性、响应式实现或线上收益；这些结论必须由人工评审、浏览器 Design QA 或真实用户证据补足。

## 4. 原型层级与 Figma 写入门禁

| 层级 | 能证明什么 | 不能宣称什么 |
| --- | --- | --- |
| L0 | 页面图、状态图、交互表和范围边界 | Figma 可点击、可访问或可实现 |
| L1 | Figma 结构、组件、变量、Auto Layout、反应和精确节点交接 | 浏览器可用、生产代码或线上收益 |
| L2 | 目标代码库中的浏览器流程、真实内容、响应式、键盘 / 焦点和失败恢复证据 | 样本外总体可用性或商业因果 |

只有在 `owner` 已确认、目标文件 / 节点和写入权限明确、版本基线已记录、页面契约通过校验后，才允许执行 Figma 写入。权限、来源或关键内容发生冲突时止于 L0/L1 计划，列出冲突，不用工具结果替代确认。
