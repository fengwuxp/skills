package com.acme.order.service.impl;

public class RedundantJSpecifyChecks {

    String normalize(String value) {
        return Objects.requireNonNull(value).trim();
    }

    String extract(@NonNull OrderDTO value, @NonNull String code) {
        AssertUtils.notNull(value, "value must not be null");
        Objects.requireNonNull(code);
        return value.getCode();
    }

    String nullableCode(@NonNull OrderDTO value) {
        return value == null ? null : value.getCode();
    }
}
