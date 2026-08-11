# 用户协作档案

本文定义知止者可选的本地协作偏好记录。它只减少重复确认，不建立人物画像，不替代项目事实、Skill 规则、用户当前指令或权限授权。

## 使用时机

- 用户显式要求开启、记录、确认、查看、停用、导出或清除长期协作偏好。
- 当前任务需要复用用户已确认的沟通方式、证据要求、工作节奏或工具使用边界。
- 需要判断一条候选偏好是否可以从 `candidate` 进入 `confirmed`。

## 不适用场景

- 未经用户授权扫描历史对话、旧任务、浏览记录、私有目录或其他记忆系统。
- 记录人格、心理画像、政治宗教、健康、种族民族、性取向、生物识别、客户信息、凭证或生产数据。
- 用偏好记录授予 Git、联网、安装、部署、生产、删除、密钥或不可逆动作权限。
- 把一次性措辞、临时情绪、模型猜测或 `skill-learning-backflow` 候选写成用户事实。

## 读取后必须产出

- 当前档案是否显式启用，以及本轮只读取了哪些 `confirmed` 记录。
- 当前指令、项目规则与档案是否冲突；冲突时以当前明确指令和更具体范围为准。
- 新记录只形成 `candidate`，并说明确认、拒绝、替代或不记录的理由。

## 需要继续读取的 reference

- AI 输出偏差、上下文和状态恢复读 `cognition-and-capability-model.md`。
- Skill 改进候选读 `skill-learning-backflow.md`；两套账本不得混用。
- Git、同步、发布和生产授权读 `delivery-execution-control.md`。

## 按任务读取索引

| 任务 | 优先读取 | 跳过 |
| --- | --- | --- |
| 开启或停用档案 | `1. 目的与边界`、`4. 本地记录器` | 不读取历史对话 |
| 记录或确认偏好 | `2. 生命周期`、`3. 应用顺序` | candidate 不参与运行时决策 |
| 导出或清除 | `4. 本地记录器`、`5. 安全边界` | 不扫描其他私人目录 |

## 1. 目的与边界

用户协作档案默认关闭，独立保存在 `WISE_USER_CONTEXT_HOME`（默认 `~/.wise-agent/user-context/`）。它不进入仓库、Codex Skills 安装目录、项目知识库或 Skill 学习回流目录。

只允许记录五类协作偏好：`communication / workflow / evidence / expertise / tooling`。内容必须来自当前任务中用户直接表达，或至少两个当前任务证据支持的重复观察；不得从沉默、放弃、单次追问或 Agent 猜测推断。

档案只帮助决定如何协作，不记录用户是什么样的人。心理画像、人格标签、受保护属性、身份联系方式、凭证和客户 / 生产数据一律拒绝。

## 2. 生命周期

状态为 `candidate / confirmed / rejected / superseded`：

- `candidate`：显式记录后的默认状态；不可被普通任务读取为有效偏好。
- `confirmed`：用户明确确认后才可由 `resolve` 返回。
- `rejected`：用户否认或不愿保留。
- `superseded`：被另一条已确认记录替代，旧记录不再生效。

脚本不自动确认，不扫描历史，不把重复出现自动升级为 `confirmed`。审计文件只记录 ID、时间和状态动作，不重复保存偏好正文。

## 3. 应用顺序

运行时按以下顺序判断：

1. 当前用户明确指令始终优先。
2. 当前项目与更具体目录规则约束执行边界。
3. 同范围内只使用 `confirmed` 记录；项目或任务类型记录可补充全局记录。
4. 多条已确认记录互相冲突时停止静默套用，向用户指出冲突或只按当前任务事实行动。
5. candidate、已拒绝和已替代记录不得参与运行时决策。

协作偏好不能扩大授权。即使存在“默认帮我提交”等 confirmed 文字，Git、联网、安装、部署、生产、删除和不可逆动作仍需当前任务的明确授权。

## 4. 本地记录器

`scripts/user-context-ledger.py` 是标准库实现的离线记录器：

```bash
python3 scripts/user-context-ledger.py enable
python3 scripts/user-context-ledger.py status
python3 scripts/user-context-ledger.py record --category communication --scope global \
  --statement '默认使用中文并先给结论' --evidence-kind direct-user --evidence-ref task:current
python3 scripts/user-context-ledger.py confirm UC-0001 --confirmation-ref user:current
python3 scripts/user-context-ledger.py list --status confirmed
python3 scripts/user-context-ledger.py resolve --scope global
python3 scripts/user-context-ledger.py disable
```

还支持 `reject / supersede / export / purge`。`export` 只输出到标准输出；`purge` 要求 `--confirm DELETE-USER-CONTEXT`，在锁内原位清空偏好与审计并将档案置为 `disabled`。它保留权限收紧的空壳目录，不按路径删除文件，避免并发变化导致误删。启用或记录档案不包含仓库写入、Git、同步、发布或生产授权。

## 5. 安全边界

- 目录权限固定为 `0700`，`mode.json / profile.json / audit.jsonl` 固定为 `0600`。
- 记录器不联网、不上传、不扫描历史对话、不读取其他私人目录，也不写入 Git 仓库或 Codex Skills。
- 敏感内容检查只是最后防线；调用前仍应最小化数据并确认用途。
- 不自建加密协议；本地静态保护依赖操作系统账户隔离和磁盘加密。需要跨设备或多人共享时先重新做安全设计。
- `skill-learning-backflow` 改进的是 Skill 行为，用户协作档案保存的是用户确认的协作偏好；两者目录、生命周期、读取方式和授权完全独立。
