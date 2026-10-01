package com.iot.iotfaultdiagnosis.exception;

public class InvalidTelemetryException extends RuntimeException {
    public InvalidTelemetryException(String message) {
        super(message);
    }
}
