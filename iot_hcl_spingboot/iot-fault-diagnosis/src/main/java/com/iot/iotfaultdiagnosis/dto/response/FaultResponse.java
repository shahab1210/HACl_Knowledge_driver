package com.iot.iotfaultdiagnosis.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class FaultResponse {

    private String faultId;
    private String title;
    private Double similarity;

    public FaultResponse() {
    }

    public FaultResponse(String faultId, String title, Double similarity) {
        this.faultId = faultId;
        this.title = title;
        this.similarity = similarity;
    }

    public String getFaultId() {
        return faultId;
    }

    public void setFaultId(String faultId) {
        this.faultId = faultId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public Double getSimilarity() {
        return similarity;
    }

    public void setSimilarity(Double similarity) {
        this.similarity = similarity;
    }
}
