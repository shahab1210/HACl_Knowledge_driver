package com.iot.iotfaultdiagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.exception.DiagnosisNotFoundException;
import com.iot.iotfaultdiagnosis.exception.InvalidTelemetryException;
import com.iot.iotfaultdiagnosis.service.DiagnosisService;
import com.iot.iotfaultdiagnosis.service.InMemoryDiagnosisStore;
import com.iot.iotfaultdiagnosis.service.ai.AIDiagnosisClient;
import com.iot.iotfaultdiagnosis.service.ai.HttpAIDiagnosisClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.web.client.RestClient;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;

public class DiagnosisServiceTest {

    private InMemoryDiagnosisStore store;
    private AIDiagnosisClient aiDiagnosisClient;
    private DiagnosisService diagnosisService;
    private ObjectMapper objectMapper;

    private DiagnosisResponse sampleDiagnosis;

    @BeforeEach
    void setUp() {
        store = new InMemoryDiagnosisStore();
        aiDiagnosisClient = Mockito.mock(AIDiagnosisClient.class);
        objectMapper = new ObjectMapper();
        diagnosisService = new DiagnosisService(store, aiDiagnosisClient);

        TelemetryResponse telemetry = new TelemetryResponse(
                "ESP32_001",
                95.0,
                45.0,
                7.2,
                8.4,
                2.1,
                "2026-10-01T01:30:00"
        );

        DiagnosisDetailResponse detail = new DiagnosisDetailResponse();
        detail.setPrimaryFault(new FaultResponse("FAULT-003", "Motor Overheating", 0.88));
        detail.setConfidence(new ConfidenceResponse("high", "Thermal distress confirmed"));

        sampleDiagnosis = new DiagnosisResponse(
                "diag-ESP32_001-001",
                "ESP32_001",
                "iot/ESP32_001/telemetry",
                LocalDateTime.now(),
                telemetry,
                detail,
                2.5
        );
    }

    @Test
    void testGetLatestDiagnosis_WhenPresent() {
        store.save(sampleDiagnosis);

        DiagnosisResponse result = diagnosisService.getLatestDiagnosis();
        assertNotNull(result);
        assertEquals("diag-ESP32_001-001", result.getId());
        assertEquals("ESP32_001", result.getDeviceId());
    }

    @Test
    void testGetLatestDiagnosis_WhenEmpty_ThrowsException() {
        assertThrows(DiagnosisNotFoundException.class, () -> diagnosisService.getLatestDiagnosis());
    }

    @Test
    void testGetDiagnosisById_Success() {
        store.save(sampleDiagnosis);

        DiagnosisResponse result = diagnosisService.getDiagnosisById("diag-ESP32_001-001");
        assertNotNull(result);
        assertEquals("diag-ESP32_001-001", result.getId());
    }

    @Test
    void testGetDiagnosisById_NotFound_ThrowsException() {
        assertThrows(DiagnosisNotFoundException.class, () -> diagnosisService.getDiagnosisById("missing-id"));
    }

    @Test
    void testGetDiagnosesByDeviceId_Success() {
        store.save(sampleDiagnosis);

        List<DiagnosisResponse> list = diagnosisService.getDiagnosesByDeviceId("ESP32_001");
        assertEquals(1, list.size());
        assertEquals("ESP32_001", list.get(0).getDeviceId());
    }

    @Test
    void testGetDiagnosesByDeviceId_NotFound_ThrowsException() {
        assertThrows(DiagnosisNotFoundException.class, () -> diagnosisService.getDiagnosesByDeviceId("UNKNOWN_DEVICE"));
    }

    @Test
    void testTriggerDiagnosis_Valid() {
        TelemetryRequest request = new TelemetryRequest(
                "ESP32_001",
                95.0,
                45.0,
                7.2,
                8.4,
                2.1
        );

        Mockito.when(aiDiagnosisClient.diagnose(any(TelemetryRequest.class))).thenReturn(sampleDiagnosis);

        DiagnosisResponse result = diagnosisService.triggerDiagnosis(request);
        assertNotNull(result);
        assertEquals("diag-ESP32_001-001", result.getId());

        // Verify it was saved to store
        assertTrue(store.getById("diag-ESP32_001-001").isPresent());
    }

    @Test
    void testTriggerDiagnosis_InvalidBlankDeviceId() {
        TelemetryRequest request = new TelemetryRequest(
                "  ",
                95.0,
                45.0,
                7.2,
                8.4,
                2.1
        );

        assertThrows(InvalidTelemetryException.class, () -> diagnosisService.triggerDiagnosis(request));
    }

    @Test
    void testTriggerDiagnosis_InvalidEmptySensors() {
        TelemetryRequest request = new TelemetryRequest("ESP32_001", null, null, null, null, null);
        assertThrows(InvalidTelemetryException.class, () -> diagnosisService.triggerDiagnosis(request));
    }

    @Test
    void testTriggerDiagnosis_InvalidNonFiniteValue() {
        TelemetryRequest request = new TelemetryRequest(
                "ESP32_001",
                Double.NaN,
                45.0,
                7.2,
                8.4,
                2.1
        );
        assertThrows(InvalidTelemetryException.class, () -> diagnosisService.triggerDiagnosis(request));
    }

    @Test
    void testIngestMqttDiagnosis_ValidJson() {
        String mqttJson = """
                {
                  "device_id": "ESP32_001",
                  "topic": "iot/ESP32_001/telemetry",
                  "telemetry": {
                    "temperature": 95.0,
                    "vibration": 7.2
                  },
                  "diagnosis": {
                    "query": "Device test query",
                    "primary_fault": {
                      "fault_id": "FAULT-003",
                      "title": "Motor Overheating",
                      "similarity": 0.88
                    },
                    "confidence": {
                      "level": "high",
                      "reason": "Thermal match"
                    }
                  },
                  "latency": {
                    "total_latency_seconds": 3.1
                  }
                }
                """;

        Mockito.when(aiDiagnosisClient.parseDiagnosisJson(Mockito.eq(mqttJson), Mockito.isNull()))
                .thenReturn(sampleDiagnosis);

        DiagnosisResponse result = diagnosisService.ingestMqttDiagnosis(mqttJson);
        assertNotNull(result);
        assertEquals("ESP32_001", result.getDeviceId());
        assertEquals("FAULT-003", result.getDiagnosis().getPrimaryFault().getFaultId());
        assertEquals("high", result.getDiagnosis().getConfidence().getLevel());

        // Check store
        assertEquals(1, store.size());
        assertEquals("ESP32_001", store.getLatest().get().getDeviceId());
    }
}
