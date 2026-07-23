package com.acme.order.service.impl;

@NullMarked
public class ValidJSpecifyChecks {

    String normalize(String value) {
        return value.trim();
    }

    String nullableCode(@Nullable OrderDTO value) {
        return value == null ? null : value.getCode();
    }

    String requireExternalValue(@NonNull @RequestBody String value) {
        return Objects.requireNonNull(value).trim();
    }
}
