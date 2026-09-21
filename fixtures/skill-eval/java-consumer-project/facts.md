# 隔离 Java 消费项目

这是声明采用 Wind 服务边界的合成工程样本，用于验证 Skill 消费与局部代码修复，不是生产 Service、Spring 集成或数据库事务证据。项目不包含 Skills 源仓库的 AGENTS.md，也不要求创建它。

已确认需求：公开查询入口返回启用订单的名称，去掉前后空白；订单不存在、名称为空或订单未启用时返回空字符串。Controller 使用既有 OrderService 契约；基础 OrderServiceImpl 拥有查询与结果规则，可以使用自己的 OrderMapper。不新增服务、接口、包装层或数据库依赖。

只允许修改 OrderController.java、OrderServiceImpl.java 和 OrderLabelTests.java。复用现有可执行测试，增加所需边界断言，测试方法以 test 开头。测试内 Mapper 替身只隔离存储输入，不证明持久化、事务或 Spring 装配。

项目格式以 idea-code-style.xml 为准，.editorconfig 只补充缩进和换行；Java 右边距为 160，与通用阅读建议 120 不同。使用本机已有 IDEA 命令行格式器时显式指定这份配置，不修改个人 IDEA 配置；工具不可用时注明格式未自动验证。

验收：编译全部源码，运行 sample.OrderLabelTests，并从临时安装目录运行 Wind 约规守卫；核对接口消费、三目与职责边界。IDEA 检查单列证据，不用守卫通过冒充格式正确。
