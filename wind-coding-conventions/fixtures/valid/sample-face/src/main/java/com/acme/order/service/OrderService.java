package com.acme.order.service;

import com.acme.order.model.dto.OrderDTO;
import jakarta.validation.constraints.NotNull;

public interface OrderService {
    String VALIDATION_EXAMPLE = "@Validated";

    /* @Valid belongs at an actual protocol entry. */
    OrderDTO getOrderById(@NotNull Long id);
}
