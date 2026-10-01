package com.iot.iotfaultdiagnosis.service;

import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse;
import com.iot.iotfaultdiagnosis.exception.DiagnosisNotFoundException;
import com.iot.iotfaultdiagnosis.exception.InvalidTelemetryException;
import com.iot.iotfaultdiagnosis.service.ai.AIDiagnosisClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DiagnosisService {

    private static final Logger log = LoggerFactory.getLogger(DiagnosisService.class);

    private final DiagnosisStore store;
    private final AIDiagnosisClient aiDiagnosisClient;

    public DiagnosisService(
            DiagnosisStore store,
            AIDiagnosisClient aiDiagnosisClient
    ) {
        this.store = store;
        this.aiDiagnosisClient = aiDiagnosisClient;
    }

    public DiagnosisResponse getLatestDiagnosis() {
        return store.getLatest()
                .orElseThrow(() -> new DiagnosisNotFoundException("No diagnosis records found"));
    }

    public DiagnosisResponse getDiagnosisById(String id) {
        if (id == null || id.trim().isEmpty()) {
            throw new InvalidTelemetryException("Diagnosis ID cannot be blank");
        }
        return store.getById(id.trim())
                .orElseThrow(() -> new DiagnosisNotFoundException("Diagnosis not found for id: " + id));
    }

    public List<DiagnosisResponse> getDiagnosesByDeviceId(String deviceId) {
        if (deviceId == null || deviceId.trim().isEmpty()) {
            throw new InvalidTelemetryException("Device ID cannot be blank");
        }
        List<DiagnosisResponse> list = store.getByDeviceId(deviceId.trim());
        if (list.isEmpty()) {
            throw new DiagnosisNotFoundException("No diagnosis records found for device: " + deviceId);
        }
        return list;
    }

    public DiagnosisResponse triggerDiagnosis(TelemetryRequest request) {
        validateTelemetryRequest(request);

        DiagnosisResponse response = aiDiagnosisClient.diagnose(request);
        store.save(response);
        log.info("Triggered and saved diagnosis {} for device {}", response.getId(), response.getDeviceId());
        return response;
    }

    public DiagnosisResponse ingestMqttDiagnosis(String jsonPayload) {
        if (jsonPayload == null || jsonPayload.trim().isEmpty()) {
            log.warn("Received empty MQTT diagnosis payload");
            return null;
        }

        try {
            DiagnosisResponse response = aiDiagnosisClient.parseDiagnosisJson(jsonPayload, null);
            store.save(response);
            log.info("Ingested and saved diagnosis for device '{}' (ID: {}) from MQTT", response.getDeviceId(), response.getId());
            return response;
        } catch (Exception e) {
            log.error("Failed to parse and store MQTT diagnosis: {}", e.getMessage(), e);
            return null;
        }
    }

    private void validateTelemetryRequest(TelemetryRequest request) {
        if (request == null) {
            throw new InvalidTelemetryException("Telemetry request cannot be null");
        }

        if (request.getDeviceId() == null || request.getDeviceId().trim().isEmpty()) {
            throw new InvalidTelemetryException("deviceId must not be blank");
        }

        if (!request.hasAtLeastOneReading()) {
            throw new InvalidTelemetryException("Telemetry message must contain at least one valid numeric sensor reading");
        }

        // Validate numeric fields for finite values
        validateNumericField("temperature", request.getTemperature());
        validateNumericField("humidity", request.getHumidity());
        validateNumericField("vibration", request.getVibration());
        validateNumericField("current", request.getCurrent());
        validateNumericField("pressure", request.getPressure());
    }

    private void validateNumericField(String name, Double value) {
        if (value != null && (!Double.isFinite(value) || Double.isNaN(value))) {
            throw new InvalidTelemetryException("Field '" + name + "' contains invalid non-finite value: " + value);
        }
    }
}
