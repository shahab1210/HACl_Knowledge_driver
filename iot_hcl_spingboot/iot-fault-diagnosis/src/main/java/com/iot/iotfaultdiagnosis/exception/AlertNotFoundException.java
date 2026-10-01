package com.iot.iotfaultdiagnosis.exception;

public class AlertNotFoundException extends RuntimeException {

    public AlertNotFoundException(String message) {
        super(message);
    }

    public AlertNotFoundException(Long id) {
        super("Alert not found with id: " + id);
    }
}
