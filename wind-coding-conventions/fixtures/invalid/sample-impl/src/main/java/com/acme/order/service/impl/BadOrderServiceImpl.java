package com.acme.order.service.impl;

public class BadOrderServiceImpl {

    void update(OrderMapper orderMapper, Object entity) {
        orderMapper.update(entity);
    }

    interface OrderMapper {
        void update(Object entity);
    }
}
