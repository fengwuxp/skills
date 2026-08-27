# Ant Design Cross-application Adoption

## Adoption Profile

| 应用 / 客户端 | 项目当前版本 | 采用深度 | 主题策略 | 组件映射 | 偏离项 | Owner | 兼容性证据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 运营 Web | 5.x 待工程复核 | 完整采用 | 现有 theme 与语义 tokens | Table、Form、Drawer | 密度按任务调整 | 后台 Owner | 待走查 |
| C 端浏览器 | 现有品牌体系 | 只共享语义和行为 | 独立品牌 tokens | 现有组件 | 不使用后台模板 | C 端 Owner | 待走查 |
| H5 | 现有移动体系 | 只共享语义和行为 | 独立触控与内容节奏 | 现有移动组件 | Ant Design Mobile 另评 | H5 Owner | 待走查 |

## 真实路径验证

| 应用 / 客户端 | 真实任务与入口到结果 | 必验状态 | 键盘与焦点或触控 | 后台模板污染检查 | 实际证据 | 停止条件 | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 运营 Web | 订单入口到筛选、编辑、失败恢复和成功 | loading、empty、error、success、disabled、focus | 键盘和焦点回归 | 不适用 | 未验证 | 焦点或恢复失败即停止 | 后台 Owner |
| H5 | 订单入口到详情、失败重试和返回 | loading、error、success、disabled、focus | 触控与返回焦点 | 检查无表格、侧栏和桌面弹层污染 | 未验证 | 模板污染或溢出即停止 | H5 Owner |
