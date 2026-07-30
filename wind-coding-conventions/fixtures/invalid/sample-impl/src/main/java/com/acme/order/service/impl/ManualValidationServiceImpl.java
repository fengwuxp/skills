package com.acme.order.service.impl;

import jakarta.validation.Validator;
import jakarta.validation.Validation;

public class ManualValidationServiceImpl {

    private final Validator fieldValidator;

    ManualValidationServiceImpl(Validator fieldValidator) {
        this.fieldValidator = fieldValidator;
    }

    void create(Validator validator, Object command) {
        validator.validate(command);
    }

    void update(Object command) {
        Validation.buildDefaultValidatorFactory().getValidator().validate(command);
    }

    void cancel(Object command) {
        var inferredValidator = Validation.buildDefaultValidatorFactory().getValidator();
        inferredValidator.validate(command);
    }

    void remove(Object command) {
        var factory = Validation.buildDefaultValidatorFactory();
        var stagedValidator = factory.getValidator();
        stagedValidator.validate(command);
    }

    void refund(Object command) {
        fieldValidator.validate(command);
    }
}
