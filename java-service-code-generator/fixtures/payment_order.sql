CREATE TABLE `t_payment_order` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `order_no` varchar(64) NOT NULL COMMENT '支付订单号',
  `amount` decimal(18,2) NOT NULL COMMENT '支付金额',
  `currency` varchar(3) NOT NULL DEFAULT 'CNY' COMMENT '币种',
  `status` varchar(32) NOT NULL COMMENT '订单状态',
  `tenant_id` bigint NOT NULL COMMENT '租户 ID',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '逻辑删除',
  `gmt_create` datetime NOT NULL COMMENT '创建时间',
  `gmt_modified` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) COMMENT='支付订单';
