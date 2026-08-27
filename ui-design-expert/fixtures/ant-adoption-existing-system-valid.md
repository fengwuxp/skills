# Existing Consumer System Adoption

## Adoption Profile

| 应用 / 客户端 | 项目当前版本 | 采用深度 | 主题策略 | 组件映射 | 偏离项 | Owner | 兼容性证据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 运营 Web | Ant 版本待核验 | 完整采用 | 当前项目 theme | Table、Form、Drawer | 后台密度按任务调整 | 后台 Owner | 待验证 |
| C 端浏览器 | 稳定品牌体系 | 维持现状 | 中立语义 tokens | 现有品牌组件 | 不引用 Ant 内部 token、class、DOM 或桌面模板 | C 端 Owner | 已有体系待复核 |

## 两端真实路径

| 应用 / 客户端 | 真实任务与入口到结果 | 必验状态 | 键盘与焦点或触控 | 实际证据 | 停止条件 | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| 运营 Web | 订单筛选、编辑失败恢复和成功 | loading、error、success、disabled、focus | 键盘与焦点 | 未验证 | 恢复失败即停止 | 后台 Owner |
| C 端浏览器 | 浏览、提交失败、恢复和成功 | loading、error、success、disabled、focus | 键盘与焦点 | 未验证 | 语义不一致即停止 | C 端 Owner |

## 迁移门禁

没有迁移收益和兼容证据时维持 C 端现状。确需迁移时另列迁移 Owner、成本、回退路径和停止条件；无法回退或任务收益不足时不启动替换。
