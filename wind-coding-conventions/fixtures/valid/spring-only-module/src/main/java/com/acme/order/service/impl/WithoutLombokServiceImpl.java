package com.acme.order.service.impl;

import org.springframework.stereotype.Service;

@Service
public class WithoutLombokServiceImpl {

    private final Object orderRepository;

    public WithoutLombokServiceImpl(Object orderRepository) {
        this.orderRepository = orderRepository;
    }
}
