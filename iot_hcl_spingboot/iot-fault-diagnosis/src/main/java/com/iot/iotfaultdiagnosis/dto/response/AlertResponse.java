package com.iot.iotfaultdiagnosis.dto.response;

import com.iot.iotfaultdiagnosis.entity.AlertEntity;
import com.iot.iotfaultdiagnosis.entity.AlertSeverity;
import com.iot.iotfaultdiagnosis.entity.AlertType;

import java.time.LocalDateTime;

public class AlertResponse {

    private Long id;
    private String deviceId;
    private AlertType alertType;
    private AlertSeverity severity;
    private String message;
    private String source;
    private String sensorParameter;
    private Double sensorValue;
    private Double thresholdValue;
    private LocalDateTime createdAt;
    private boolean acknowledged;
    private LocalDateTime acknowledgedAt;
    private String acknowledgedBy;

    public AlertResponse() {
    }

    public AlertResponse(AlertEntity entity) {
        if (entity != null) {
            this.id = entity.getId();
            this.deviceId = entity.getDeviceId();
            this.alertType = entity.getAlertType();
            this.severity = entity.getSeverity();
            this.message = entity.getMessage();
            this.source = entity.getSource();
            this.sensorParameter = entity.getSensorParameter();
            this.sensorValue = entity.getSensorValue();
            this.thresholdValue = entity.getThresholdValue();
            this.createdAt = entity.getCreatedAt();
            this.acknowledged = entity.isAcknowledged();
            this.acknowledgedAt = entity.getAcknowledgedAt();
            this.acknowledgedBy = entity.getAcknowledgedBy();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public AlertType getAlertType() {
        return alertType;
    }

    public void setAlertType(AlertType alertType) {
        this.alertType = alertType;
    }

    public AlertSeverity getSeverity() {
        return severity;
    }

    public void setSeverity(AlertSeverity severity) {
        this.severity = severity;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getSensorParameter() {
        return sensorParameter;
    }

    public void setSensorParameter(String sensorParameter) {
        this.sensorParameter = sensorParameter;
    }

    public Double getSensorValue() {
        return sensorValue;
    }

    public void setSensorValue(Double sensorValue) {
        this.sensorValue = sensorValue;
    }

    public Double getThresholdValue() {
        return thresholdValue;
    }

    public void setThresholdValue(Double thresholdValue) {
        this.thresholdValue = thresholdValue;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public boolean isAcknowledged() {
        return acknowledged;
    }

    public void setAcknowledged(boolean acknowledged) {
        this.acknowledged = acknowledged;
    }

    public LocalDateTime getAcknowledgedAt() {
        return acknowledgedAt;
    }

    public void setAcknowledgedAt(LocalDateTime acknowledgedAt) {
        this.acknowledgedAt = acknowledgedAt;
    }

    public String getAcknowledgedBy() {
        return acknowledgedBy;
    }

    public void setAcknowledgedBy(String acknowledgedBy) {
        this.acknowledgedBy = acknowledgedBy;
    }
}
