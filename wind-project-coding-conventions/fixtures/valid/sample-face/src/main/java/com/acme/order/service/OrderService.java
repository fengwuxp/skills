package com.acme.order.service;

import com.acme.order.model.dto.OrderDTO;

public interface OrderService {
    OrderDTO getOrderById(Long id);
}
