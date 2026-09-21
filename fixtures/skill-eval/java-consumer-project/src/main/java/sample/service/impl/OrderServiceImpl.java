package sample.service.impl;

import sample.dal.OrderRow;
import sample.dal.mapper.OrderMapper;
import sample.face.OrderService;

public final class OrderServiceImpl implements OrderService
{
 private final OrderMapper orderMapper;

 public OrderServiceImpl(OrderMapper orderMapper)
 {
  this.orderMapper = orderMapper;
 }

 @Override
 public String getOrderLabel(long id)
 {
  OrderRow order = orderMapper.findOrderById(id);
  return order == null ? "" : order.getLabel() == null ? "" : order.isEnabled() ? order.getLabel() : "";
 }
}
