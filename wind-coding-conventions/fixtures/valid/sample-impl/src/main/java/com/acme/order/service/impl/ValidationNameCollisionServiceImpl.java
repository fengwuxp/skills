package com.acme.order.service.impl;

public class ValidationNameCollisionServiceImpl {

    private final jakarta.validation.Validator validator;

    ValidationNameCollisionServiceImpl(jakarta.validation.Validator validator) {
        this.validator = validator;
    }

    void prepare(jakarta.validation.Validator validator) {
        // The Bean Validator is not invoked.
    }

    void execute(DomainValidator validator, Object command) {
        validator.validate(command);
    }

    interface DomainValidator {
        void validate(Object command);
    }
}
