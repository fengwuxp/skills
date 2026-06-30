# Wind 项目 AGENTS.md 模板

本文是 `wind-project-coding-conventions` Skill 的项目本地 `AGENTS.md` 模板，用于 Wind/Nobe 风格 Java 项目初始化或改进 Agent 运行约规。模板提炼自 `wind-integration / nobe / capte-domain` 的稳定共性、Wind 项目编码约规、AI Native 角色协作 Loop 和 Karpathy-style 工程纪律；项目本地事实、OpenSpec/ADR、CI 与附近代码风格优先。

## 使用时机

- 新 Wind/Nobe Java 项目需要初始化 `AGENTS.md`，明确 opt-in Wind 项目编码约规。
- 既有项目已有 `AGENTS.md`，需要补齐 AI 协作入口、Wind 分层、测试/CR 红线或验证交接。
- AI Native Engineering Loop 需要为某个遵循 Wind 约规的项目生成或改进项目级 Agent 运行契约。

## 不适用场景

- 未 opt-in Wind 约规的普通 Java/Spring 项目；只可参考通用工程原则，不强套 face/impl、模型包位或基础服务规则。
- 已有项目 `AGENTS.md`、OpenSpec、ADR、CI 或团队规范更具体时，不覆盖本地规则，只做缺口建议。
- 不替代源码级架构设计、TDD、Bug 修复、代码 CR、发布审批或 Git 授权。

## 读取后必须产出

- 初始化时：一份可直接放入项目根目录的 `AGENTS.md` 草案，并标出必须由项目 owner 填写的命令、模块和验证项。
- 改进时：只输出最小 patch 建议，说明新增/替换位置、保留的本地规则、删除的重复项和验收标准。
- 必须区分事实、推断、待确认和范围外不做；不得把模板写成本项目已验证事实。

## 需要继续读取的 reference

- Wind 主规则读 `wind-project-coding-conventions.md`。
- 正反例读 `wind-project-coding-examples.md`。
- 跨产品、架构、AI Maker/Checker 和验证发布的流程编排读 `ai-native-engineering-workflow`。
- 源码级设计、TDD、CR 和生产风险交给 `资深架构师`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 初始化 Wind 项目 `AGENTS.md` | 下方 `模板正文`，再按项目填充命令和模块 | 不生成未验证的构建命令、发布流程或生产权限 |
| 改进既有 `AGENTS.md` | 下方 `改进规则`，再对照本地文件做最小 patch | 不重写已有团队规则，不保留重复近义条款 |

## 模板正文

复制到项目根目录 `AGENTS.md` 后，先替换 `<...>` 占位符；不知道的项保留为“待确认”，不要猜。

```markdown
# AGENTS.md

本项目遵守 Wind 项目编码约规。任何 AI Agent、脚本化改动或人工协作都必须先读本文件，再读任务相关源码、测试、OpenSpec/ADR 和附近代码风格。

## 项目身份

- 项目类型：<Java/Spring/Wind/Nobe 服务>
- 核心业务：<一句话说明真实业务能力>
- 主要模块：<列出 face / impl / web-api / core / infrastructure 等模块>
- 默认验证命令：<如 mvn test / ./gradlew test / just test；未知则写待确认>

## 顶层原则

- 不知道就问；动机、目标、对象、边界或验收不清时，先停下来澄清。
- 没要求的不写，只改被要求的部分；每一行修改都要能回到用户目标、验收标准、源码事实或失败测试。
- 给验收标准、验证结果和停止条件，不用长步骤、模板套话或无关解释填充。
- 从第一性原理看原始需求和问题本质，不从惯例、模板或历史实现出发；如果目标清晰但路径不是最短，直接说明更短路径。
- 遇到问题追根因，不打补丁；每个关键决策都要能回答“为什么”。
- 输出说重点，砍掉不改变决策的信息；事实、推断、待确认和范围外不做必须分层表达。
- 项目统一编码规范和附近代码风格优先；没有更具体规则时，再按 Wind 项目编码约规收敛。

## AI 协作入口

- 普通 PRD、产品方案、Backlog 或验收种子：使用产品专家。
- 架构设计、系统分析、源码修改、TDD、Bug 修复、代码 CR、生产风险：使用资深架构师。
- 跨产品、架构、AI Maker/Checker、质量门禁、发布复盘的端到端协作：进入 AI Native Engineering Loop，只输出当前阶段、owner、交接物、授权策略、验证与停止条件。
- Wind face/impl、模型归位、Entity 不外露、ServiceImpl、MyBatis Flex 和测试边界规则判断：使用 `wind-project-coding-conventions`。
- 结构化 Java Service 脚手架生成：使用 `java-service-code-generator`；必须有 DDL/schema/Java 类/字段表格，不从纯自然语言生成生产代码。

## 授权与范围

- 只读分析默认允许读取仓库内源码、测试和文档；读取仓库外文件、联网、安装依赖、修改 Git 历史、删除文件、访问密钥、部署或生产操作必须显式授权。
- 低风险本地改动只能在用户指定范围内进行，并在完成后给出验证命令和结果。
- Git add/commit/push、同步 Codex、发布、回滚和不可逆操作必须单独确认。

## Wind 编码约规

- `*-face` 放对外契约：Service、Application 契约、DTO、Request、Query、Command、对外枚举、常量、事件和 callback/spi。
- `*-impl` 放实现：ServiceImpl、内部服务、Application 实现、domain、dal/entities、dal/mapper、mapstruct、converter、configuration、listener、webhook。
- `web-api` / `web-security` 放 Controller、Web VO、Web 表单 Request 和 Web Converter。
- `core` 只放跨模块稳定公共能力；`infrastructure` 只放技术适配、框架配置和通用 helper。
- 新 DTO/Request/Query/Command 优先放 `*.model.dto`、`*.model.request`、`*.model.query`、`*.model.command`；历史项目可兼容既有 `*.dto`、`*.request`、`*.query`、`*.command`。
- Entity、Mapper、Repository、MyBatis Page 和 QueryWrapper 不得出现在 Controller、face Service、ApplicationService 对外方法、Facade、Adapter、跨模块接口或事件消息契约中。
- Service / ApplicationService / Facade / Adapter 必须有真实业务职责；不得新增一行透传方法、Mapper 包装、浅服务或似是而非抽象。
- ApplicationService 只在完整用例编排、事务边界、权限/审计、跨服务协调或外部副作用明确时使用。
- MyBatis Flex 查询使用 `XxxRefs` 和项目统一 helper；禁止裸字符串字段名和新增 `LambdaQueryWrapper`。
- 币种字段统一使用 `com.wind.transaction.core.enums.CurrencyIsoCode`；外部字符串币种只在 Adapter/Converter 边界转换。
- 生产源码路径不得新增内存版业务 Service、Fake/Mock 业务实现、模拟模块或看上去可用的样子货。

## 测试与 CR

- TDD 和测试按公开契约黑盒验证，观察 Controller、face Service、ApplicationService、ServiceImpl 的业务结果、状态流转、持久化事实、异常、幂等和可观察副作用。
- 不为凑绿感知私有方法、内部调用顺序、Mapper/Repository 调用次数、临时字段、内部 Mock 交互或当前实现步骤。
- Bug 修复先补能复现失败的回归测试；红变绿必须修改生产实现，不靠放宽断言、硬凑 fixture 或迎合当前实现。
- 完成实现后检查是否新增浅模块、直通包装、无主依赖、AI 注释噪声、过度抽象、内部链路 mock 或只为过测试的战术实现。

## 交付格式

完成任务时只报告：

- 改了什么：
- 验收标准：
- 验证结果：
- 残余风险：
- 下一 owner：

不得把“可继续推进”写成“已经授权”，不得把测试通过、CR 结论、Git 授权或上线审批互相替代。
```

## 改进规则

- 已有 `AGENTS.md` 有同义规则时，不新增近义条款；只补缺失的 Wind opt-in、AI 路由、授权边界、验证命令或项目特有模块。
- 模板里的 `<...>` 占位符必须由项目事实填充；无法确认时保留“待确认”，不要推断。
- 不把 `capte-domain`、`nobe`、`wind-integration` 的历史包名、业务模块名或命令照搬成新项目事实。
- 改进结论优先给最小 patch 和验收标准；不输出冗长操作步骤。
