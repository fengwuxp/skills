package com.acme.order.service;

import com.acme.order.dal.entities.OrderEntity;
import jakarta.validation.Valid;

public interface BadOrderService {
    OrderEntity queryOrderById(@Valid Long id);
}
