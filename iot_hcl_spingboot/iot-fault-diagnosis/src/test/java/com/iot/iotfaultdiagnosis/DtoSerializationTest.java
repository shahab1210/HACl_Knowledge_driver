package com.iot.iotfaultdiagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class DtoSerializationTest {

    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    }

    @Test
    void testTelemetryRequestSerialization() throws Exception {
        String json = """
                {
                  "deviceId": "ESP32_001",
                  "temperature": 92.5,
                  "humidity": 45.0,
                  "vibration": 6.8,
                  "current": 8.1,
                  "pressure": 2.2
                }
                """;

        TelemetryRequest req = objectMapper.readValue(json, TelemetryRequest.class);
        assertEquals("ESP32_001", req.getDeviceId());
        assertEquals(92.5, req.getTemperature());
        assertEquals(45.0, req.getHumidity());
        assertEquals(6.8, req.getVibration());
        assertEquals(8.1, req.getCurrent());
        assertEquals(2.2, req.getPressure());
        assertTrue(req.hasAtLeastOneReading());
    }

    @Test
    void testTelemetryRequestAliasDeserialization() throws Exception {
        String json = """
                {
                  "device_id": "ESP32_002",
                  "temp": 85.0,
                  "hum": 50.0,
                  "vib": 5.0,
                  "currentValue": 7.0,
                  "press": 2.0
                }
                """;

        TelemetryRequest req = objectMapper.readValue(json, TelemetryRequest.class);
        assertEquals("ESP32_002", req.getDeviceId());
        assertEquals(85.0, req.getTemperature());
        assertEquals(50.0, req.getHumidity());
        assertEquals(5.0, req.getVibration());
        assertEquals(7.0, req.getCurrent());
        assertEquals(2.0, req.getPressure());
    }

    @Test
    void testDiagnosisResponseSerialization() throws Exception {
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
        detail.setQuery("Device ESP32_001 query");
        detail.setPrimaryFault(new FaultResponse("FAULT-003", "Motor Overheating", 0.88));
        detail.setConfidence(new ConfidenceResponse("high", "Verified temperature match"));
        detail.setEvidence(List.of(new EvidenceResponse("telemetry", "temperature", 95.0, "°C", "critical")));
        detail.setKnowledgeSources(List.of(new KnowledgeSourceResponse(1, "SENSOR-TEMPERATURE", "chunk-01", "Temp Sensor", "sensors/temp.md", 0.88)));

        DiagnosisResponse response = new DiagnosisResponse(
                "diag-12345",
                "ESP32_001",
                "iot/ESP32_001/telemetry",
                LocalDateTime.of(2026, 10, 1, 1, 30, 0),
                telemetry,
                detail,
                3.14
        );

        String json = objectMapper.writeValueAsString(response);
        assertTrue(json.contains("\"id\":\"diag-12345\""));
        assertTrue(json.contains("\"deviceId\":\"ESP32_001\""));
        assertTrue(json.contains("\"faultId\":\"FAULT-003\""));
        assertTrue(json.contains("\"title\":\"Motor Overheating\""));

        DiagnosisResponse deserialized = objectMapper.readValue(json, DiagnosisResponse.class);
        assertEquals("diag-12345", deserialized.getId());
        assertEquals("ESP32_001", deserialized.getDeviceId());
        assertEquals(95.0, deserialized.getTelemetry().getTemperature());
        assertEquals("FAULT-003", deserialized.getDiagnosis().getPrimaryFault().getFaultId());
    }

    @Test
    void testErrorResponseSerialization() throws Exception {
        ErrorResponse error = new ErrorResponse(404, "Not Found", "Diagnosis not found", "/api/v1/diagnosis/latest");
        String json = objectMapper.writeValueAsString(error);
        assertTrue(json.contains("\"status\":404"));
        assertTrue(json.contains("\"error\":\"Not Found\""));
        assertTrue(json.contains("\"message\":\"Diagnosis not found\""));
        assertTrue(json.contains("\"path\":\"/api/v1/diagnosis/latest\""));
    }
}
