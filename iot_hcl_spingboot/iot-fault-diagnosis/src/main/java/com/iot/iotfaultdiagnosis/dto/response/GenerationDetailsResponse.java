package com.iot.iotfaultdiagnosis.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class GenerationDetailsResponse {

    private Long totalDuration;
    private Integer evalCount;
    private Long evalDuration;
    private Integer promptEvalCount;

    public GenerationDetailsResponse() {
    }

    public GenerationDetailsResponse(Long totalDuration, Integer evalCount, Long evalDuration, Integer promptEvalCount) {
        this.totalDuration = totalDuration;
        this.evalCount = evalCount;
        this.evalDuration = evalDuration;
        this.promptEvalCount = promptEvalCount;
    }

    public Long getTotalDuration() {
        return totalDuration;
    }

    public void setTotalDuration(Long totalDuration) {
        this.totalDuration = totalDuration;
    }

    public Integer getEvalCount() {
        return evalCount;
    }

    public void setEvalCount(Integer evalCount) {
        this.evalCount = evalCount;
    }

    public Long getEvalDuration() {
        return evalDuration;
    }

    public void setEvalDuration(Long evalDuration) {
        this.evalDuration = evalDuration;
    }

    public Integer getPromptEvalCount() {
        return promptEvalCount;
    }

    public void setPromptEvalCount(Integer promptEvalCount) {
        this.promptEvalCount = promptEvalCount;
    }
}
