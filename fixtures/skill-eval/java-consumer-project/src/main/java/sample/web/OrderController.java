package sample.web;

import sample.dal.OrderRow;
import sample.dal.mapper.OrderMapper;

public final class OrderController
{
 private final OrderMapper orderMapper;

 public OrderController(OrderMapper orderMapper)
 {
  this.orderMapper = orderMapper;
 }

 public String getOrderLabel(long id)
 {
  OrderRow order = orderMapper.findOrderById(id);
  return order == null ? "" : order.getLabel() == null ? "" : order.isEnabled() ? order.getLabel() : "";
 }
}
