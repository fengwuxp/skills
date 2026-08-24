# Figma 与代码双向对账

## 使用时机

当同一页面或区段在 Figma 与代码两端经历多轮修改，用户要求“先改设计再改代码”“代码完成后写回 Figma”“继续未完成的 writeback”“逐节点对账”，或两端都可能发生漂移时读取。

单向新建设计、一次性 design-to-code、纯代码 Bug、纯视觉审查和只有截图而无可定位设计源时不使用本契约。

## 读取后必须产出

- 当前权威端、同步方向、目标端、Owner 和写入授权。
- exact Figma node 与稳定 code anchor 的逐行映射。
- copy、geometry、asset、interaction 四类 delta。
- 已执行修改、未执行 writeback、冲突与阻塞。
- 双端 readback 和最低充分验证证据。

## 需要继续读取的 reference

- 页面权威、Page Manifest 和命名读取 figma-design-contract.md。
- Figma 文件结构和代码交接读取 figma-file-engineering.md。
- design-to-code 与 code-to-canvas 工具路由读取 prototype-output.md。
- 文字裁切、溢出和多视口读取 design-draft-fidelity-review.md。
- Figma 读写使用当前官方 Figma Skills；本 reference 不复制 Plugin API、字体加载、Code Connect 或工具参数。

## 1. 对账契约

每个需要同步的页面或区段记录：

~~~text
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

- authoritative_surface 表示本切片允许决定内容或结构的权威，不表示另一个载体可以被无条件覆盖。
- approved-copy 适用于文案已经独立确认、Figma 与代码都只是消费端的场景。
- design-first 表示 Figma 是本轮先行载体；code-first 表示代码先行；reconcile-only 只比较和裁决，不默认写入。
- revision 使用可回读版本、commit、文件指纹或设计版本；latest、current 等浮动值不构成版本。
- fingerprint 只用于发现变化，不能替代内容与视觉判断。
- pending_target 使用 figma、code、both 或 none；未授权端必须保持 pending。

## 2. 执行顺序

1. 回读 Design Contract、Page Manifest、Owner 最新决策和被替代名称。
2. 读取 exact Figma node 与代码锚点；无法定位时停止，不猜 node 或组件。
3. 分离四类 delta：copy、geometry、asset、interaction。
4. 比较双端 revision 与 fingerprint，裁决同步方向。
5. 只修改已授权目标端；另一个端只记录 pending。
6. 回读实际目标，核对文本、字体、尺寸、资源、节点名和代码映射。
7. 按 delta 选择最低充分证据：copy 使用双端 readback 和内容契约；geometry/asset 使用声明视口的设计与浏览器截图；interaction 使用 Preview 或浏览器行为证据。
8. 只有双端一致且必要证据闭合时标记 aligned。

## 3. 状态与分支

| 状态 | 含义 | 下一动作 |
| --- | --- | --- |
| aligned | 双端与权威一致，证据充分 | 结束本切片 |
| source-newer | 权威端较新 | 只更新已授权目标端 |
| target-newer | 目标端包含未回写变化 | 重新裁决权威，不反向覆盖 |
| conflict | 双端均有独立变化或 Owner 决策冲突 | 列差异并停止，交 Owner |
| blocked | 缺 node、anchor、版本、权限或必要工具 | 记录解除条件 |

### 双端同时变化

双端均有变化时不得先后互相覆盖。输出 copy/geometry/asset/interaction 差异表，标明每项来源、Owner 和可保留部分，等待 Owner 指定权威或逐项合并。

### Figma 不可写

保留 pending_target=figma，不切换到另一设计工具、不创建第二真相源，也不把代码截图冒充 Figma 已同步。

### 固定文本框溢出

先读取字体、文本框尺寸和原行数预算。copy-only 任务优先选择不扩大布局的文案；若仍溢出，必须取得 geometry 修改授权。修改后对目标节点截图复测。

### 浏览器证据不可得

契约测试、类型检查、构建和 HTTP 回读可以分别报告，但不能升级为浏览器视觉通过。相关检查保持 blocked 或 cant-tell，并记录环境限制。

## 4. 验收

- authoritative_surface、sync_mode、Owner 和授权均唯一明确。
- exact node 与 code anchor 可回读。
- 双端变化没有被静默覆盖。
- copy-only 修改没有顺带重构 geometry、asset 或 interaction。
- 已执行和 pending 写回分开记录。
- aligned 行具有双端 readback 和该 delta 所需的最低充分证据。
- 任何截图、MCP 输出、源码断言或 HTTP 200 都没有被扩大解释。

## 5. 常见错误

- 依据当前目标稿反向定义业务或页面职责。
- 把“设计已确认”理解为永久 Figma-first。
- 只记录页面级状态，遗漏发生漂移的具体 section。
- 用旧截图或会话摘要代替 exact node 和当前代码。
- Figma 无权限时改用其它工具并声称已写回。
- 浏览器受限时把构建通过写成视觉通过。
