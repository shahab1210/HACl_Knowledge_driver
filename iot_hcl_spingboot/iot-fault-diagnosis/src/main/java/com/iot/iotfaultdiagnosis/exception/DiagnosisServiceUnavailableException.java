package com.iot.iotfaultdiagnosis.exception;

public class DiagnosisServiceUnavailableException extends RuntimeException {
    public DiagnosisServiceUnavailableException(String message) {
        super(message);
    }

    public DiagnosisServiceUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
