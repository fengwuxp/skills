| 字段名 | Java 属性名 | SQL 类型 | 说明 | 是否主键 | 是否必填 | 默认值 | 是否自增 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | id | bigint | 主键 ID | 是 | 是 |  | 是 |
| batch_no | batchNo | varchar(64) | 结算批次号 | 否 | 是 |  | 否 |
| total_amount | totalAmount | decimal(18,2) | 结算总金额 | 否 | 是 |  | 否 |
| status | status | varchar(32) | 批次状态 | 否 | 是 |  | 否 |
| gmt_create | gmtCreate | datetime | 创建时间 | 否 | 是 |  | 否 |
| gmt_modified | gmtModified | datetime | 更新时间 | 否 | 是 |  | 否 |
