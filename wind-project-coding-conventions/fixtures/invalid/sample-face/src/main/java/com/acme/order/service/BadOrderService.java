package com.acme.order.service;

import com.acme.order.dal.entities.OrderEntity;

public interface BadOrderService {
    OrderEntity queryOrderById(Long id);
}
