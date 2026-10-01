package com.iot.iotfaultdiagnosis.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class ConfidenceResponse {

    private String level;
    private String reason;

    public ConfidenceResponse() {
    }

    public ConfidenceResponse(String level, String reason) {
        this.level = level;
        this.reason = reason;
    }

    public String getLevel() {
        return level;
    }

    public void setLevel(String level) {
        this.level = level;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }
}
