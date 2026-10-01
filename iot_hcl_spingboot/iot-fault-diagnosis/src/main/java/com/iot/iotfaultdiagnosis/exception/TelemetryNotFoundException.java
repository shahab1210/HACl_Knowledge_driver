package com.iot.iotfaultdiagnosis.exception;

public class TelemetryNotFoundException extends RuntimeException {

    public TelemetryNotFoundException(String message) {
        super(message);
    }
}
