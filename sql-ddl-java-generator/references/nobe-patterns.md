# Nobe DDL Generation Patterns

- Typical module layout: `xxx-face/src/main/java` for DTO/request/query/service and `xxx-impl/src/main/java` for entity/mapper/converter/service implementation.
- Infer base package from existing Java package declarations in the selected face/impl modules.
- MyBatis-Flex annotation import: `com.mybatisflex.annotation.Column`.
- Common special columns:
  - `tenant_id`: `@Column(tenantId = true)`
  - `version`: `@Column(version = true)`
  - `is_deleted`: `@Column(value = "is_deleted", isLogicDelete = true)`
  - `u_id`: Java field `uid` with `@Column("u_id")`
  - `is_enabled`: Java field `enabled` with `@Column("is_enabled")`
