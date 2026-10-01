package com.iot.iotfaultdiagnosis;

import com.iot.iotfaultdiagnosis.config.AlertThresholdProperties;
import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.entity.AlertEntity;
import com.iot.iotfaultdiagnosis.entity.AlertSeverity;
import com.iot.iotfaultdiagnosis.entity.AlertType;
import com.iot.iotfaultdiagnosis.entity.SensorReading;
import com.iot.iotfaultdiagnosis.repository.AlertRepository;
import com.iot.iotfaultdiagnosis.service.alert.AlertDetectionService;
import com.iot.iotfaultdiagnosis.service.notification.NotificationService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class AlertDetectionServiceTest {

    @Mock
    private AlertRepository alertRepository;

    @Mock
    private NotificationService notificationService;

    private AlertThresholdProperties thresholdConfig;
    private AlertDetectionService alertDetectionService;

    @BeforeEach
    void setUp() {
        thresholdConfig = new AlertThresholdProperties();
        // default config:
        // tempWarning: 75.0, tempCritical: 90.0
        // vibrationWarning: 4.5, vibrationCritical: 7.1
        // currentLowCritical: 3.0, currentWarning: 9.5, currentCritical: 10.5
        // pressureLowCritical: 1.5, pressureWarning: 3.8, pressureCritical: 4.5
        // humidityWarning: 80.0, humidityCritical: 90.0
        // cooldownSeconds: 60

        alertDetectionService = new AlertDetectionService(alertRepository, notificationService, thresholdConfig);

        lenient().when(alertRepository.save(any(AlertEntity.class))).thenAnswer(invocation -> invocation.getArgument(0));
    }

    @Test
    void testNormalTelemetry_GeneratesNoAlerts() {
        SensorReading reading = new SensorReading();
        reading.setDeviceId("ESP32_001");
        reading.setTemperature(30.0);
        reading.setVibration(2.0);
        reading.setCurrentValue(6.0);
        reading.setPressure(2.5);
        reading.setHumidity(55.0);

        List<AlertEntity> alerts = alertDetectionService.checkTelemetry(reading);

        assertThat(alerts).isEmpty();
        verify(alertRepository, never()).save(any());
        verify(notificationService, never()).sendNotification(any());
    }

    @Test
    void testTemperatureThreshold_WarningAndCritical() {
        // Warning: 78 C (>= 75 C)
        SensorReading warnReading = new SensorReading();
        warnReading.setDeviceId("ESP32_001");
        warnReading.setTemperature(78.0);

        List<AlertEntity> warnAlerts = alertDetectionService.checkTelemetry(warnReading);
        assertThat(warnAlerts).hasSize(1);
        assertThat(warnAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.WARNING);
        assertThat(warnAlerts.get(0).getSensorParameter()).isEqualTo("temperature");
        assertThat(warnAlerts.get(0).getThresholdValue()).isEqualTo(75.0);

        // Escalation to Critical: 95 C (>= 90 C)
        SensorReading critReading = new SensorReading();
        critReading.setDeviceId("ESP32_001");
        critReading.setTemperature(95.0);

        List<AlertEntity> critAlerts = alertDetectionService.checkTelemetry(critReading);
        assertThat(critAlerts).hasSize(1);
        assertThat(critAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.CRITICAL);
        assertThat(critAlerts.get(0).getThresholdValue()).isEqualTo(90.0);

        verify(notificationService, times(2)).sendNotification(any());
    }

    @Test
    void testVibrationThreshold_WarningAndCritical() {
        // Warning: 5.2 mm/s (>= 4.5)
        SensorReading warnReading = new SensorReading();
        warnReading.setDeviceId("ESP32_001");
        warnReading.setVibration(5.2);

        List<AlertEntity> warnAlerts = alertDetectionService.checkTelemetry(warnReading);
        assertThat(warnAlerts).hasSize(1);
        assertThat(warnAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.WARNING);
        assertThat(warnAlerts.get(0).getSensorParameter()).isEqualTo("vibration");

        // Critical: 8.5 mm/s (>= 7.1)
        SensorReading critReading = new SensorReading();
        critReading.setDeviceId("ESP32_001");
        critReading.setVibration(8.5);

        List<AlertEntity> critAlerts = alertDetectionService.checkTelemetry(critReading);
        assertThat(critAlerts).hasSize(1);
        assertThat(critAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.CRITICAL);
    }

    @Test
    void testCurrentThreshold_OverloadAndDryRunning() {
        // High Critical Overcurrent: 11.2 A (>= 10.5)
        SensorReading overReading = new SensorReading();
        overReading.setDeviceId("ESP32_001");
        overReading.setCurrentValue(11.2);

        List<AlertEntity> overAlerts = alertDetectionService.checkTelemetry(overReading);
        assertThat(overAlerts).hasSize(1);
        assertThat(overAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.CRITICAL);
        assertThat(overAlerts.get(0).getMessage()).contains("overcurrent");

        // Low Critical Dry-running: 2.1 A (< 3.0)
        SensorReading dryReading = new SensorReading();
        dryReading.setDeviceId("ESP32_002");
        dryReading.setCurrentValue(2.1);

        List<AlertEntity> dryAlerts = alertDetectionService.checkTelemetry(dryReading);
        assertThat(dryAlerts).hasSize(1);
        assertThat(dryAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.CRITICAL);
        assertThat(dryAlerts.get(0).getMessage()).contains("dry-running");
    }

    @Test
    void testPressureThreshold_OverpressureAndLoss() {
        // High Critical Overpressure: 5.0 bar (>= 4.5)
        SensorReading overReading = new SensorReading();
        overReading.setDeviceId("ESP32_001");
        overReading.setPressure(5.0);

        List<AlertEntity> overAlerts = alertDetectionService.checkTelemetry(overReading);
        assertThat(overAlerts).hasSize(1);
        assertThat(overAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.CRITICAL);

        // Low Critical Pressure Depressed: 1.1 bar (< 1.5)
        SensorReading lowReading = new SensorReading();
        lowReading.setDeviceId("ESP32_002");
        lowReading.setPressure(1.1);

        List<AlertEntity> lowAlerts = alertDetectionService.checkTelemetry(lowReading);
        assertThat(lowAlerts).hasSize(1);
        assertThat(lowAlerts.get(0).getSeverity()).isEqualTo(AlertSeverity.CRITICAL);
        assertThat(lowAlerts.get(0).getMessage()).contains("Depressed pressure");
    }

    @Test
    void testHumidityThreshold_WarningAndCritical() {
        SensorReading critReading = new SensorReading();
        critReading.setDeviceId("ESP32_001");
        critReading.setHumidity(94.0); // >= 90.0

        List<AlertEntity> alerts = alertDetectionService.checkTelemetry(critReading);
        assertThat(alerts).hasSize(1);
        assertThat(alerts.get(0).getSeverity()).isEqualTo(AlertSeverity.CRITICAL);
        assertThat(alerts.get(0).getSensorParameter()).isEqualTo("humidity");
    }

    @Test
    void testCooldownDeduplication_SuppressesRepeatedAlertWithinWindow() {
        SensorReading reading1 = new SensorReading();
        reading1.setDeviceId("ESP32_001");
        reading1.setTemperature(92.0); // Critical

        List<AlertEntity> firstBatch = alertDetectionService.checkTelemetry(reading1);
        assertThat(firstBatch).hasSize(1);

        // Second reading immediately after with same severity: should be suppressed
        SensorReading reading2 = new SensorReading();
        reading2.setDeviceId("ESP32_001");
        reading2.setTemperature(93.5); // Still Critical

        List<AlertEntity> secondBatch = alertDetectionService.checkTelemetry(reading2);
        assertThat(secondBatch).isEmpty(); // Suppressed by cooldown

        // Save was only called once
        verify(alertRepository, times(1)).save(any());
    }

    @Test
    void testPhysicalPlausibility_SystemAnomalyAlert() {
        SensorReading reading = new SensorReading();
        reading.setDeviceId("ESP32_001");
        reading.setTemperature(350.0); // Out of physical range [-20, 250]

        List<AlertEntity> alerts = alertDetectionService.checkTelemetry(reading);
        assertThat(alerts).hasSize(2); // System anomaly + temperature critical
        assertThat(alerts.stream().anyMatch(a -> a.getAlertType() == AlertType.SYSTEM_ANOMALY)).isTrue();
    }

    @Test
    void testDiagnosisCriticalAlert_TriggeredForHighConfidenceCriticalFault() {
        DiagnosisDetailResponse detail = new DiagnosisDetailResponse();
        detail.setPrimaryFault(new FaultResponse("FAULT-003", "Motor Overheating", 0.92));
        detail.setConfidence(new ConfidenceResponse("HIGH", "Thermal distress corroborated"));

        DiagnosisResponse diag = new DiagnosisResponse(
                "diag-123",
                "ESP32_001",
                "iot/ESP32_001/telemetry",
                LocalDateTime.now(),
                null,
                detail,
                1.5
        );

        AlertEntity alert = alertDetectionService.checkDiagnosis(diag);
        assertThat(alert).isNotNull();
        assertThat(alert.getAlertType()).isEqualTo(AlertType.DIAGNOSIS_CRITICAL);
        assertThat(alert.getSeverity()).isEqualTo(AlertSeverity.CRITICAL);
        assertThat(alert.getMessage()).contains("FAULT-003");

        verify(notificationService, times(1)).sendNotification(alert);
    }
}
