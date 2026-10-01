package com.iot.iotfaultdiagnosis.exception;

public class DiagnosisNotFoundException extends RuntimeException {
    public DiagnosisNotFoundException(String message) {
        super(message);
    }
}
