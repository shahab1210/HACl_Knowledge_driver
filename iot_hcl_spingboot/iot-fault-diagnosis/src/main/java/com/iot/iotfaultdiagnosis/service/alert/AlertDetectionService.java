package com.iot.iotfaultdiagnosis.service.alert;

import com.iot.iotfaultdiagnosis.config.AlertThresholdProperties;
import com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse;
import com.iot.iotfaultdiagnosis.entity.AlertEntity;
import com.iot.iotfaultdiagnosis.entity.AlertSeverity;
import com.iot.iotfaultdiagnosis.entity.AlertType;
import com.iot.iotfaultdiagnosis.entity.SensorReading;
import com.iot.iotfaultdiagnosis.repository.AlertRepository;
import com.iot.iotfaultdiagnosis.service.notification.NotificationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lightweight real-time alert detection service.
 * Evaluates telemetry against authoritative knowledge base thresholds
 * without running heavy AI inference.
 * Implements deduplication and cooldown to prevent alert flooding.
 */
@Service
public class AlertDetectionService {

    private static final Logger log = LoggerFactory.getLogger(AlertDetectionService.class);

    private final AlertRepository alertRepository;
    private final NotificationService notificationService;
    private final AlertThresholdProperties thresholdConfig;

    // Cache of last emitted alert timestamp: key -> "deviceId:alertType:parameter:severity"
    private final Map<String, LocalDateTime> alertCooldownCache = new ConcurrentHashMap<>();

    public AlertDetectionService(
            AlertRepository alertRepository,
            NotificationService notificationService,
            AlertThresholdProperties thresholdConfig) {
        this.alertRepository = alertRepository;
        this.notificationService = notificationService;
        this.thresholdConfig = thresholdConfig;
    }

    /**
     * Inspects a sensor telemetry reading and produces alerts if thresholds are breached.
     * @param reading the sensor telemetry data
     * @return list of newly created and persisted alerts
     */
    public List<AlertEntity> checkTelemetry(SensorReading reading) {
        List<AlertEntity> generatedAlerts = new ArrayList<>();
        if (reading == null || reading.getDeviceId() == null) {
            return generatedAlerts;
        }

        String deviceId = reading.getDeviceId();

        // 1. Physical Plausibility / System Anomaly Checks
        checkPhysicalPlausibility(reading, generatedAlerts);

        // 2. Temperature Threshold Evaluation (Normal 24-70 C, Warning 75 C, Critical 90 C)
        Double temp = reading.getTemperature();
        if (temp != null) {
            if (temp >= thresholdConfig.getTempCritical()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.CRITICAL,
                        String.format("Critical temperature (%.1f°C >= %.1f°C). Risk of stator winding thermal breakdown and bearing seizure.",
                                temp, thresholdConfig.getTempCritical()),
                        "TELEMETRY_INGESTION",
                        "temperature",
                        temp,
                        thresholdConfig.getTempCritical(),
                        generatedAlerts
                );
            } else if (temp >= thresholdConfig.getTempWarning()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.WARNING,
                        String.format("Elevated temperature (%.1f°C >= %.1f°C). Approaching maximum thermal operating boundary.",
                                temp, thresholdConfig.getTempWarning()),
                        "TELEMETRY_INGESTION",
                        "temperature",
                        temp,
                        thresholdConfig.getTempWarning(),
                        generatedAlerts
                );
            }
        }

        // 3. Vibration Threshold Evaluation (Normal < 2.8 mm/s, Warning 4.5 mm/s, Critical 7.1 mm/s per ISO 10816)
        Double vib = reading.getVibration();
        if (vib != null) {
            if (vib >= thresholdConfig.getVibrationCritical()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.CRITICAL,
                        String.format("Critical vibration (%.2f mm/s >= %.2f mm/s). Severe unbalance, misalignment, or bearing degradation detected.",
                                vib, thresholdConfig.getVibrationCritical()),
                        "TELEMETRY_INGESTION",
                        "vibration",
                        vib,
                        thresholdConfig.getVibrationCritical(),
                        generatedAlerts
                );
            } else if (vib >= thresholdConfig.getVibrationWarning()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.WARNING,
                        String.format("Elevated vibration (%.2f mm/s >= %.2f mm/s). Vibration exceeds ISO 10816 acceptable boundary.",
                                vib, thresholdConfig.getVibrationWarning()),
                        "TELEMETRY_INGESTION",
                        "vibration",
                        vib,
                        thresholdConfig.getVibrationWarning(),
                        generatedAlerts
                );
            }
        }

        // 4. Current Threshold Evaluation (Normal 4-9.5 A, Dry Run < 3 A, Warning 9.5 A, Overload > 10.5 A)
        Double current = reading.getCurrentValue();
        if (current != null) {
            if (current >= thresholdConfig.getCurrentCritical()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.CRITICAL,
                        String.format("Critical overcurrent (%.2f A >= %.2f A). Continuous electrical overload exceeding motor FLA capacity.",
                                current, thresholdConfig.getCurrentCritical()),
                        "TELEMETRY_INGESTION",
                        "current",
                        current,
                        thresholdConfig.getCurrentCritical(),
                        generatedAlerts
                );
            } else if (current >= thresholdConfig.getCurrentWarning()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.WARNING,
                        String.format("Elevated current (%.2f A >= %.2f A). Motor operating near full load amperage rating.",
                                current, thresholdConfig.getCurrentWarning()),
                        "TELEMETRY_INGESTION",
                        "current",
                        current,
                        thresholdConfig.getCurrentWarning(),
                        generatedAlerts
                );
            } else if (current > 0.0 && current < thresholdConfig.getCurrentLowCritical()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.CRITICAL,
                        String.format("Abnormally low motor current (%.2f A < %.2f A). Pump dry-running or uncoupled shaft condition.",
                                current, thresholdConfig.getCurrentLowCritical()),
                        "TELEMETRY_INGESTION",
                        "current",
                        current,
                        thresholdConfig.getCurrentLowCritical(),
                        generatedAlerts
                );
            }
        }

        // 5. Pressure Threshold Evaluation (Normal 1.5-3.5 bar, Rupture < 1.5 bar, Warning 3.8 bar, Deadhead > 4.5 bar)
        Double pressure = reading.getPressure();
        if (pressure != null) {
            if (pressure >= thresholdConfig.getPressureCritical()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.CRITICAL,
                        String.format("Dangerous overpressure (%.2f bar >= %.2f bar). Discharge line blockage or dead-head pump operation.",
                                pressure, thresholdConfig.getPressureCritical()),
                        "TELEMETRY_INGESTION",
                        "pressure",
                        pressure,
                        thresholdConfig.getPressureCritical(),
                        generatedAlerts
                );
            } else if (pressure >= thresholdConfig.getPressureWarning()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.WARNING,
                        String.format("High discharge pressure (%.2f bar >= %.2f bar). Elevated hydraulic system resistance.",
                                pressure, thresholdConfig.getPressureWarning()),
                        "TELEMETRY_INGESTION",
                        "pressure",
                        pressure,
                        thresholdConfig.getPressureWarning(),
                        generatedAlerts
                );
            } else if (pressure > 0.0 && pressure < thresholdConfig.getPressureLowCritical()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.CRITICAL,
                        String.format("Depressed pressure (%.2f bar < %.2f bar). Pipeline integrity loss, cavitation, or fluid starvation.",
                                pressure, thresholdConfig.getPressureLowCritical()),
                        "TELEMETRY_INGESTION",
                        "pressure",
                        pressure,
                        thresholdConfig.getPressureLowCritical(),
                        generatedAlerts
                );
            }
        }

        // 6. Humidity Threshold Evaluation (Normal 30-75 %, Warning 80 %, Critical 90 %)
        Double humidity = reading.getHumidity();
        if (humidity != null) {
            if (humidity >= thresholdConfig.getHumidityCritical()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.CRITICAL,
                        String.format("Critical humidity (%.1f%% >= %.1f%%). Imminent moisture condensation and insulation breakdown hazard.",
                                humidity, thresholdConfig.getHumidityCritical()),
                        "TELEMETRY_INGESTION",
                        "humidity",
                        humidity,
                        thresholdConfig.getHumidityCritical(),
                        generatedAlerts
                );
            } else if (humidity >= thresholdConfig.getHumidityWarning()) {
                evaluateAndTrigger(
                        deviceId,
                        AlertType.SENSOR_THRESHOLD,
                        AlertSeverity.WARNING,
                        String.format("High ambient humidity (%.1f%% >= %.1f%%). Elevated moisture condensation risk in enclosure.",
                                humidity, thresholdConfig.getHumidityWarning()),
                        "TELEMETRY_INGESTION",
                        "humidity",
                        humidity,
                        thresholdConfig.getHumidityWarning(),
                        generatedAlerts
                );
            }
        }

        return generatedAlerts;
    }

    /**
     * Inspects an AI diagnosis response and creates alerts for critical AI-detected conditions.
     */
    public AlertEntity checkDiagnosis(DiagnosisResponse diagnosis) {
        if (diagnosis == null || diagnosis.getDeviceId() == null || diagnosis.getDiagnosis() == null) {
            return null;
        }

        String deviceId = diagnosis.getDeviceId();
        var detail = diagnosis.getDiagnosis();
        var primaryFault = detail.getPrimaryFault();
        var confidence = detail.getConfidence();

        if (primaryFault != null) {
            String faultId = primaryFault.getFaultId();
            String faultTitle = primaryFault.getTitle();
            String confLevel = confidence != null && confidence.getLevel() != null
                    ? confidence.getLevel().toUpperCase()
                    : "NORMAL";

            // Trigger critical alert for known high-severity faults with high confidence
            boolean isCriticalFault = "FAULT-003".equalsIgnoreCase(faultId) || // Motor Overheating
                    "FAULT-007".equalsIgnoreCase(faultId) || // Pump Dry Running
                    "FAULT-009".equalsIgnoreCase(faultId) || // High Pressure
                    "FAULT-001".equalsIgnoreCase(faultId);   // Bearing Overheating

            if (isCriticalFault && "HIGH".equalsIgnoreCase(confLevel)) {
                String cooldownKey = deviceId + ":DIAGNOSIS_CRITICAL:" + faultId + ":CRITICAL";
                if (!isInCooldown(cooldownKey)) {
                    AlertEntity alert = new AlertEntity(
                            deviceId,
                            AlertType.DIAGNOSIS_CRITICAL,
                            AlertSeverity.CRITICAL,
                            String.format("AI Diagnosis Confirmed Critical Fault: %s (%s) with HIGH confidence. Immediate inspection required.",
                                    faultTitle, faultId),
                            "DIAGNOSIS_ENGINE",
                            "ai_fault",
                            primaryFault.getSimilarity() != null ? primaryFault.getSimilarity() : 1.0,
                            0.80
                    );

                    AlertEntity saved = alertRepository.save(alert);
                    alertCooldownCache.put(cooldownKey, LocalDateTime.now());
                    notificationService.sendNotification(saved);
                    return saved;
                }
            }
        }

        return null;
    }

    private void checkPhysicalPlausibility(SensorReading reading, List<AlertEntity> generatedAlerts) {
        String deviceId = reading.getDeviceId();

        if (reading.getTemperature() != null && (reading.getTemperature() < -20.0 || reading.getTemperature() > 250.0)) {
            evaluateAndTrigger(
                    deviceId,
                    AlertType.SYSTEM_ANOMALY,
                    AlertSeverity.WARNING,
                    String.format("Sensor telemetry plausibility violation: temperature value %.1f°C is out of physical range [-20, 250].",
                            reading.getTemperature()),
                    "DATA_INTEGRITY",
                    "temperature",
                    reading.getTemperature(),
                    250.0,
                    generatedAlerts
            );
        }

        if (reading.getVibration() != null && (reading.getVibration() < 0.0 || reading.getVibration() > 100.0)) {
            evaluateAndTrigger(
                    deviceId,
                    AlertType.SYSTEM_ANOMALY,
                    AlertSeverity.WARNING,
                    String.format("Sensor telemetry plausibility violation: vibration value %.2f mm/s is out of physical range [0, 100].",
                            reading.getVibration()),
                    "DATA_INTEGRITY",
                    "vibration",
                    reading.getVibration(),
                    100.0,
                    generatedAlerts
            );
        }
    }

    private void evaluateAndTrigger(
            String deviceId,
            AlertType alertType,
            AlertSeverity severity,
            String message,
            String source,
            String parameter,
            Double value,
            Double threshold,
            List<AlertEntity> outputList) {

        String cooldownKey = deviceId + ":" + alertType + ":" + parameter + ":" + severity;

        if (isInCooldown(cooldownKey)) {
            log.debug("Alert suppressed due to cooldown window: {}", cooldownKey);
            return;
        }

        AlertEntity alert = new AlertEntity(
                deviceId,
                alertType,
                severity,
                message,
                source,
                parameter,
                value,
                threshold
        );

        AlertEntity saved = alertRepository.save(alert);
        alertCooldownCache.put(cooldownKey, LocalDateTime.now());
        notificationService.sendNotification(saved);
        outputList.add(saved);
    }

    private boolean isInCooldown(String cooldownKey) {
        LocalDateTime lastEmitted = alertCooldownCache.get(cooldownKey);
        if (lastEmitted == null) {
            return false;
        }

        long elapsedSeconds = ChronoUnit.SECONDS.between(lastEmitted, LocalDateTime.now());
        return elapsedSeconds < thresholdConfig.getCooldownSeconds();
    }

    public void clearCooldownCache() {
        alertCooldownCache.clear();
    }
}
