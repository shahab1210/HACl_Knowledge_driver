package com.iot.iotfaultdiagnosis.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Authoritative sensor thresholds and alert configuration.
 * Default values directly sourced from P5 Knowledge Base documents:
 * - ai/knowledge-base/sensors/temperature.md & motor-overheating.md (Normal 24-70 C, Warning 75 C, Critical 90 C)
 * - ai/knowledge-base/sensors/vibration.md & ISO 10816 Class I/II (Normal < 2.8 mm/s, Warning 4.5 mm/s, Critical 7.1 mm/s)
 * - ai/knowledge-base/sensors/current.md & motor-overcurrent.md (Normal 4-9.5 A, Low Critical < 3 A, Warning 9.5 A, Critical 10.5 A)
 * - ai/knowledge-base/sensors/pressure.md & high-pressure.md (Normal 1.5-3.5 bar, Low Critical < 1.5 bar, Warning 3.8 bar, Critical 4.5 bar)
 * - ai/knowledge-base/sensors/humidity.md (Normal 30-75 %, Warning 80 %, Critical 90 %)
 */
@Component
@ConfigurationProperties(prefix = "app.alerts")
public class AlertThresholdProperties {

    // Temperature (Celsius)
    private double tempWarning = 75.0;
    private double tempCritical = 90.0;

    // Vibration (mm/s RMS)
    private double vibrationWarning = 4.5;
    private double vibrationCritical = 7.1;

    // Current (Amperes)
    private double currentLowCritical = 3.0;
    private double currentWarning = 9.5;
    private double currentCritical = 10.5;

    // Pressure (bar)
    private double pressureLowCritical = 1.5;
    private double pressureWarning = 3.8;
    private double pressureCritical = 4.5;

    // Humidity (% RH)
    private double humidityWarning = 80.0;
    private double humidityCritical = 90.0;

    // Cooldown duration in seconds to avoid alert flooding
    private long cooldownSeconds = 60;

    public AlertThresholdProperties() {
    }

    public double getTempWarning() {
        return tempWarning;
    }

    public void setTempWarning(double tempWarning) {
        this.tempWarning = tempWarning;
    }

    public double getTempCritical() {
        return tempCritical;
    }

    public void setTempCritical(double tempCritical) {
        this.tempCritical = tempCritical;
    }

    public double getVibrationWarning() {
        return vibrationWarning;
    }

    public void setVibrationWarning(double vibrationWarning) {
        this.vibrationWarning = vibrationWarning;
    }

    public double getVibrationCritical() {
        return vibrationCritical;
    }

    public void setVibrationCritical(double vibrationCritical) {
        this.vibrationCritical = vibrationCritical;
    }

    public double getCurrentLowCritical() {
        return currentLowCritical;
    }

    public void setCurrentLowCritical(double currentLowCritical) {
        this.currentLowCritical = currentLowCritical;
    }

    public double getCurrentWarning() {
        return currentWarning;
    }

    public void setCurrentWarning(double currentWarning) {
        this.currentWarning = currentWarning;
    }

    public double getCurrentCritical() {
        return currentCritical;
    }

    public void setCurrentCritical(double currentCritical) {
        this.currentCritical = currentCritical;
    }

    public double getPressureLowCritical() {
        return pressureLowCritical;
    }

    public void setPressureLowCritical(double pressureLowCritical) {
        this.pressureLowCritical = pressureLowCritical;
    }

    public double getPressureWarning() {
        return pressureWarning;
    }

    public void setPressureWarning(double pressureWarning) {
        this.pressureWarning = pressureWarning;
    }

    public double getPressureCritical() {
        return pressureCritical;
    }

    public void setPressureCritical(double pressureCritical) {
        this.pressureCritical = pressureCritical;
    }

    public double getHumidityWarning() {
        return humidityWarning;
    }

    public void setHumidityWarning(double humidityWarning) {
        this.humidityWarning = humidityWarning;
    }

    public double getHumidityCritical() {
        return humidityCritical;
    }

    public void setHumidityCritical(double humidityCritical) {
        this.humidityCritical = humidityCritical;
    }

    public long getCooldownSeconds() {
        return cooldownSeconds;
    }

    public void setCooldownSeconds(long cooldownSeconds) {
        this.cooldownSeconds = cooldownSeconds;
    }
}
