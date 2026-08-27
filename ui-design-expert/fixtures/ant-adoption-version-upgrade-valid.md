# Ant Design v6 Upgrade Gate

## 当前工程信息

当前 Ant Design 精确主版本、React 版本、浏览器范围、`@ant-design/icons`、主题入口和内部 DOM / class 依赖均待工程 Owner 只读核验。

## v6 兼容门禁

迁移前必须核对 React 18 及以上、现代浏览器与 CSS variables、`@ant-design/icons` 6 及以上，以及内部 DOM / class 选择器依赖。当前不假定兼容。

## 最小试片与授权

不改依赖，先用当前版本完成一条订单筛选、校验失败、恢复和成功的原型试片。工程 Owner 补齐版本与依赖证据前，不联网、不安装、不升级、不改主题；兼容失败或无法回退时停止迁移。
