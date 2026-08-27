# Ant Design Component Specification

## 组件契约

| 组件 / 来源 | 语义 tokens | 状态 | 交互与反馈 | 响应式 | 可访问性 | 偏离项 | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 订单表格 / Ant Table | surface、text、danger | loading、empty、error、disabled、focus、success | 筛选失败保留输入并可重试 | 窄屏保持可读 | 表头关联、键盘可达、焦点可见 | 列宽按任务调整 | 后台 Owner |
| 订单详情 / H5 现有组件 | content、muted、status | loading、empty、error、disabled、focus、success | 弱网失败可重试并保持上下文 | 单列且长文不溢出 | 原生语义、触控目标、焦点可见 | 品牌和内容节奏独立 | H5 Owner |

## 真实路径与证据边界

| 应用 / 客户端 | 真实任务与入口到结果 | 必验状态 | 错误恢复 | 键盘与焦点或触控 | 实际证据 | 停止条件 | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 运营 Web | 订单入口到筛选、查看、失败重试和成功 | loading、empty、error、disabled、focus、success | 保留筛选条件 | 键盘与焦点回归 | 未验证 | 恢复失败即停止 | 后台 Owner |
| H5 | 订单入口到详情、失败重试和返回 | loading、empty、error、disabled、focus、success | 保留已展示内容 | 触控与返回焦点 | 未验证 | 触控或溢出失败即停止 | H5 Owner |

偏离必须回指任务、品牌或兼容证据。静态检查、截图或官方组件说明不能证明组合后可用。
