package com.iot.iotfaultdiagnosis.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.LocalDateTime;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class DiagnosisResponse {

    private String id;
    private String deviceId;
    private String topic;
    private LocalDateTime timestamp;
    private TelemetryResponse telemetry;
    private DiagnosisDetailResponse diagnosis;
    private Double latencySeconds;

    public DiagnosisResponse() {
    }

    public DiagnosisResponse(String id, String deviceId, String topic, LocalDateTime timestamp,
                             TelemetryResponse telemetry, DiagnosisDetailResponse diagnosis, Double latencySeconds) {
        this.id = id;
        this.deviceId = deviceId;
        this.topic = topic;
        this.timestamp = timestamp;
        this.telemetry = telemetry;
        this.diagnosis = diagnosis;
        this.latencySeconds = latencySeconds;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public TelemetryResponse getTelemetry() {
        return telemetry;
    }

    public void setTelemetry(TelemetryResponse telemetry) {
        this.telemetry = telemetry;
    }

    public DiagnosisDetailResponse getDiagnosis() {
        return diagnosis;
    }

    public void setDiagnosis(DiagnosisDetailResponse diagnosis) {
        this.diagnosis = diagnosis;
    }

    public Double getLatencySeconds() {
        return latencySeconds;
    }

    public void setLatencySeconds(Double latencySeconds) {
        this.latencySeconds = latencySeconds;
    }
}
