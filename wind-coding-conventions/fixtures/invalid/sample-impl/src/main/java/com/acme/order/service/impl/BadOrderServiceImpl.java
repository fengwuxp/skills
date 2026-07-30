package com.acme.order.service.impl;

import org.springframework.validation.annotation.Validated;

@Validated
public class BadOrderServiceImpl {

    void update(OrderMapper orderMapper, Object entity) {
        orderMapper.update(entity);
    }

    interface OrderMapper {
        void update(Object entity);
    }
}
