package com.iot.iotfaultdiagnosis.dto.request;

import com.fasterxml.jackson.annotation.JsonAlias;
import jakarta.validation.constraints.NotBlank;
import java.time.LocalDateTime;

public class TelemetryRequest {

    @NotBlank(message = "deviceId must not be blank")
    @JsonAlias({"device_id", "deviceId", "device"})
    private String deviceId;

    @JsonAlias({"temperature", "temp", "temperature_c"})
    private Double temperature;

    @JsonAlias({"humidity", "hum", "humidity_pct"})
    private Double humidity;

    @JsonAlias({"vibration", "vib", "vibration_mms"})
    private Double vibration;

    @JsonAlias({"current", "currentValue", "current_value", "curr", "amps"})
    private Double current;

    @JsonAlias({"pressure", "press", "pressure_bar"})
    private Double pressure;

    @JsonAlias({"recorded_at", "recordedAt", "timestamp", "time"})
    private LocalDateTime recordedAt;

    public TelemetryRequest() {
    }

    public TelemetryRequest(String deviceId, Double temperature, Double humidity, Double vibration, Double current, Double pressure) {
        this.deviceId = deviceId;
        this.temperature = temperature;
        this.humidity = humidity;
        this.vibration = vibration;
        this.current = current;
        this.pressure = pressure;
        this.recordedAt = LocalDateTime.now();
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public Double getTemperature() {
        return temperature;
    }

    public void setTemperature(Double temperature) {
        this.temperature = temperature;
    }

    public Double getHumidity() {
        return humidity;
    }

    public void setHumidity(Double humidity) {
        this.humidity = humidity;
    }

    public Double getVibration() {
        return vibration;
    }

    public void setVibration(Double vibration) {
        this.vibration = vibration;
    }

    public Double getCurrent() {
        return current;
    }

    public void setCurrent(Double current) {
        this.current = current;
    }

    public Double getPressure() {
        return pressure;
    }

    public void setPressure(Double pressure) {
        this.pressure = pressure;
    }

    public LocalDateTime getRecordedAt() {
        return recordedAt;
    }

    public void setRecordedAt(LocalDateTime recordedAt) {
        this.recordedAt = recordedAt;
    }

    public boolean hasAtLeastOneReading() {
        return temperature != null || humidity != null || vibration != null || current != null || pressure != null;
    }
}
