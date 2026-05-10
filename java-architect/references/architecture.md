# 架构规范（服务分层 + DDD + 整洁架构）

## 服务层分层规范（参考）

服务层**只允许**以下四类 Service：

| 分类 | 职责 | 命名规范 | 返回类型限制 |
|------|------|----------|--------------|
| 基础服务层 | 数据访问协调，薄而纯 | `{实体}Service` | 允许返回实体/DTO |
| 领域服务（写） | 聚合业务规则与状态变更 | `{实体}DomainService` | 只允许返回实体或基本类型，严禁返回 DTO |
| 领域服务（读） | 查询模型/列表/统计（CQRS Query Side） | `{实体}DomainQueryService` | 返回 DTO/VO |
| 场景服务（用例） | 业务流程编排 | `{业务场景}ApplicationService` | 返回 DTO/Result |

## 调用关系（强制）
```text
Controller
↓
ApplicationService（场景）
↓
DomainService（写） DomainQueryService（读）
↓
{实体}Service（基础服务）
↓
Repository / Mapper
```

### 禁止规则

- `DomainService` **不得调用** `DomainQueryService`
- `DomainQueryService` **不得调用** `DomainService`
- 任何 Service **不得直接访问 Repository**（除 `{实体}Service`）

## 方法命名速查（强制）

| 层级 | 允许动词 | 示例 |
|------|----------|------|
| 基础服务 | `get`（必然存在） / `find`（可选） / `query`（列表/分页） / `exists` / `count` | `User getById(Long id)` `Optional<User> findByEmail(String email)` |
| 领域写服务 | `create` / `update` / `bind` / `freeze` / `enable` / `disable` / `cancel` | `User createUser(CreateUserCommand)` `void disableUser(DisableUserCommand)` |
| 领域读服务 | `get` / `find` / `query` / `stats` / `summary` | `UserDetailDTO getUserDetail(Long id)` `Page<UserListDTO> queryUserPage(UserPageQuery)` |
| 场景服务 | 业务意图动词：`login` / `register` / `pay` / `submit` / `logout` | `UserDTO loginByPassword(LoginRequest)` |

### get vs find 语义

- `getXxx`：必然存在，不存在抛业务异常。
- `findXxx`：可能不存在，返回 `Optional<T>` 或可空 VO。

### queryXxx

- 返回列表/分页，必须使用 `XxxQuery` 参数对象（禁止零散查询参数）。

## 实体型 vs 场景型 Service 判定规则

**一句话判断法**：
- 如果回答「对象怎么变」→ 实体型（DomainService）
- 如果回答「业务怎么走」→ 场景型（ApplicationService）

**四个硬判断规则**（命中 ≥2 条 → 场景型）：

| 判断点 | 实体型 | 场景型 |
|--------|--------|--------|
| 是否聚合中心 | 是 | 否 |
| 是否跨实体 | 否 | 是 |
| 是否允许 DTO | 否 | 是 |
| 方法是否业务动词 | 否 | 是 |

## DDD 战术设计（可选）

- 聚合根（Aggregate Root）：负责维护业务一致性，通过聚合根访问内部实体。
- 值对象（Value Object）：不可变，无标识，如 `Address`、`Money`。
- 领域事件（Domain Event）：使用 `@DomainEvents` 或 `ApplicationEventPublisher` 发布。
- 仓库（Repository）：由 `{实体}Service` 封装，对外隐藏持久化细节。

## 整洁架构要点

- 核心业务逻辑（实体、用例）不依赖 Spring、JPA 等外部框架。
- 依赖倒置：高层模块（Domain）不依赖低层模块（Infrastructure），都依赖抽象。
- 边界清晰：将 Web、DB、MQ 等视为「可插拔」的外围插件。