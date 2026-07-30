package com.acme.order.service.impl;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class FieldInjectedOrderServiceImpl {

    @Autowired
    private Object orderRepository;
}
