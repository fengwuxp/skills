# 需求验收契约

## 使用时机

在把需求拆成可执行验收条件、记录证据或形成总裁决时读取。该契约约束“证据能证明什么”，不替代领域判断。

## 一、验收基线

开始前冻结：

- `requirement_source / requirement_version / requirement_fingerprint`：需求权威、版本和内容指纹。
- `implementation_target / implementation_version`：被验收实现及版本。
- `scope / non_goals`：本轮覆盖和明确不覆盖。
- `environment / test_data`：实际环境和可重复数据。
- `risk_level`：`low / medium / high / critical`。
- `requirement_owner / acceptance_owner / checker`：定义、验收责任和独立复核责任。
- `authorization_boundary`：允许的读取、测试执行和外部动作。

任一关键项未知且会改变结论时停止；不要用 `latest`、当前截图或测试通过反推需求版本。

## 二、原子验收条件

每项条件只验证一个可判定结果：

| 字段 | 含义 |
| --- | --- |
| `id` | 稳定条件 ID |
| `requirement_anchor` | 可回读的需求锚点 |
| `verification_kind` | 证据路由类型 |
| `required` | 是否阻断总通过 |
| `preconditions` | 执行前事实 |
| `action` | 可复现动作 |
| `expected` | 必须出现的结果 |
| `unacceptable` | 明确反例与失败副作用 |
| `owner` | 失败或阻断的承责方 |
| `outcome` | 原子结果 |
| `evidence_refs` | 证据 ID 列表 |
| `finding_id` | 失败发现；非失败可为 `none` |
| `retest_scope` | 修复后的最小重测边界 |
| `rationale` | 取舍、阻断或不适用理由 |

可用结果：

- `pass`：期望得到充分、相符且可复核的证据。
- `fail`：观察到与需求冲突的事实，并记录 finding。
- `blocked`：前置条件、环境、权限或依赖阻止验证。
- `cant-tell`：现有证据互相冲突或不足以判断，需要 Owner/专家裁决。
- `untested`：在范围内但尚未执行；必选项导致总裁决 `Blocked`。
- `not-applicable`：经理由证明不适用，只允许非必选项。

## 三、证据记录

每条证据至少包含：`id`、关联条件、类型、来源、SHA-256 指纹、环境、命令或方法、结果、采集时间、生产者、独立复核者和限制。

证据失效条件：

- 需求、实现、环境、数据或测试工具的实质版本已变化。
- 证据无法回读、指纹不符或只剩摘要。
- 测试经过未批准的跳过、重试、mock 或基线更新。
- 同一 Maker 同时生成并裁决高风险通过，且无独立复核。
- 静态截图被用于证明交互、业务副作用、响应式或可访问性。

## 四、总裁决

只对 `required: true` 的条件决定准出：

1. 任一 `fail` -> `Fail`。
2. 否则任一 `blocked` 或 `untested` -> `Blocked`。
3. 否则任一 `cant-tell` -> `Need Owner`。
4. 其余必选项全部 `pass` -> `Pass`。

`Pass` 只覆盖声明的版本、环境、数据和范围；残余风险、非目标和下一 Owner 必须保留。高风险与关键风险通过证据应有独立复核者。

校验器默认只验证报告是否合法，并原样输出 `verdict`；报告合法但裁决为 `Fail / Blocked / Need Owner` 时仍可返回结构校验成功。只有调用方显式使用 `--require-pass` 时，非 `Pass` 裁决才作为自动准出失败返回非零；结构或证据契约无效使用独立错误码。
