package com.iot.iotfaultdiagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iot.iotfaultdiagnosis.controller.DiagnosisController;
import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.exception.DiagnosisNotFoundException;
import com.iot.iotfaultdiagnosis.exception.DiagnosisServiceUnavailableException;
import com.iot.iotfaultdiagnosis.exception.GlobalExceptionHandler;
import com.iot.iotfaultdiagnosis.service.DiagnosisService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.security.test.context.support.WithMockUser;

@WebMvcTest(DiagnosisController.class)
@Import(GlobalExceptionHandler.class)
@AutoConfigureMockMvc(addFilters = false)
public class DiagnosisControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockitoBean
    private DiagnosisService diagnosisService;

    @MockitoBean
    private com.iot.iotfaultdiagnosis.security.JwtAuthenticationFilter jwtAuthenticationFilter;

    @MockitoBean
    private com.iot.iotfaultdiagnosis.security.JwtTokenProvider jwtTokenProvider;

    @MockitoBean
    private com.iot.iotfaultdiagnosis.security.CustomUserDetailsService customUserDetailsService;

    private DiagnosisResponse sampleDiagnosis;

    @BeforeEach
    void setUp() {
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
        detail.setQuery("Device ESP32_001 observation: temperature 95.0");
        detail.setPrimaryFault(new FaultResponse("FAULT-003", "Motor Overheating", 0.88));
        detail.setConfidence(new ConfidenceResponse("high", "Matched thermal threshold"));
        detail.setEvidence(List.of(new EvidenceResponse("telemetry", "temperature", 95.0, "°C", "critical")));
        detail.setPossibleCauses(List.of("Inadequate cooling"));
        detail.setRecommendedChecks(List.of("Inspect cooling fan"));
        detail.setKnowledgeSources(List.of(new KnowledgeSourceResponse(1, "SENSOR-TEMPERATURE", "chunk-01", "Temp Sensor", "sensors/temp.md", 0.88)));
        detail.setModel("qwen2.5:1.5b");

        sampleDiagnosis = new DiagnosisResponse(
                "diag-ESP32_001-100",
                "ESP32_001",
                "iot/ESP32_001/telemetry",
                LocalDateTime.of(2026, 10, 1, 1, 30, 0),
                telemetry,
                detail,
                3.5
        );
    }

    @Test
    void testGetLatestDiagnosis_Success() throws Exception {
        Mockito.when(diagnosisService.getLatestDiagnosis()).thenReturn(sampleDiagnosis);

        mockMvc.perform(get("/api/v1/diagnosis/latest")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("diag-ESP32_001-100"))
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"))
                .andExpect(jsonPath("$.telemetry.temperature").value(95.0))
                .andExpect(jsonPath("$.diagnosis.primaryFault.faultId").value("FAULT-003"))
                .andExpect(jsonPath("$.diagnosis.primaryFault.title").value("Motor Overheating"))
                .andExpect(jsonPath("$.diagnosis.confidence.level").value("high"))
                .andExpect(jsonPath("$.latencySeconds").value(3.5));
    }

    @Test
    void testGetLatestDiagnosis_NotFound() throws Exception {
        Mockito.when(diagnosisService.getLatestDiagnosis())
                .thenThrow(new DiagnosisNotFoundException("No diagnosis records found"));

        mockMvc.perform(get("/api/v1/diagnosis/latest")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error").value("Not Found"))
                .andExpect(jsonPath("$.message").value("No diagnosis records found"))
                .andExpect(jsonPath("$.path").value("/api/v1/diagnosis/latest"));
    }

    @Test
    void testGetDiagnosisById_Success() throws Exception {
        Mockito.when(diagnosisService.getDiagnosisById("diag-ESP32_001-100")).thenReturn(sampleDiagnosis);

        mockMvc.perform(get("/api/v1/diagnosis/diag-ESP32_001-100")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("diag-ESP32_001-100"))
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"));
    }

    @Test
    void testGetDiagnosisById_NotFound() throws Exception {
        Mockito.when(diagnosisService.getDiagnosisById("non-existent"))
                .thenThrow(new DiagnosisNotFoundException("Diagnosis not found for id: non-existent"));

        mockMvc.perform(get("/api/v1/diagnosis/non-existent")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.message").value("Diagnosis not found for id: non-existent"));
    }

    @Test
    void testGetDiagnosesByDeviceId_Success() throws Exception {
        Mockito.when(diagnosisService.getDiagnosesByDeviceId("ESP32_001")).thenReturn(List.of(sampleDiagnosis));

        mockMvc.perform(get("/api/v1/diagnosis/device/ESP32_001")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].deviceId").value("ESP32_001"))
                .andExpect(jsonPath("$[0].diagnosis.primaryFault.faultId").value("FAULT-003"));
    }

    @Test
    void testGetDiagnosesByDeviceId_NotFound() throws Exception {
        Mockito.when(diagnosisService.getDiagnosesByDeviceId("UNKNOWN"))
                .thenThrow(new DiagnosisNotFoundException("No diagnosis records found for device: UNKNOWN"));

        mockMvc.perform(get("/api/v1/diagnosis/device/UNKNOWN")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404));
    }

    @Test
    void testTriggerDiagnosis_Success() throws Exception {
        TelemetryRequest request = new TelemetryRequest(
                "ESP32_001",
                95.0,
                45.0,
                7.2,
                8.4,
                2.1
        );

        Mockito.when(diagnosisService.triggerDiagnosis(any(TelemetryRequest.class))).thenReturn(sampleDiagnosis);

        mockMvc.perform(post("/api/v1/diagnosis")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value("diag-ESP32_001-100"))
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"))
                .andExpect(jsonPath("$.diagnosis.primaryFault.faultId").value("FAULT-003"));
    }

    @Test
    void testTriggerDiagnosis_InvalidBlankDeviceId() throws Exception {
        TelemetryRequest request = new TelemetryRequest(
                "",
                95.0,
                45.0,
                7.2,
                8.4,
                2.1
        );

        mockMvc.perform(post("/api/v1/diagnosis")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error").value("Bad Request"));
    }

    @Test
    void testTriggerDiagnosis_ServiceUnavailable() throws Exception {
        TelemetryRequest request = new TelemetryRequest(
                "ESP32_001",
                95.0,
                45.0,
                7.2,
                8.4,
                2.1
        );

        Mockito.when(diagnosisService.triggerDiagnosis(any(TelemetryRequest.class)))
                .thenThrow(new DiagnosisServiceUnavailableException("AI diagnosis service is offline"));

        mockMvc.perform(post("/api/v1/diagnosis")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.status").value(503))
                .andExpect(jsonPath("$.error").value("Service Unavailable"))
                .andExpect(jsonPath("$.message").value("AI diagnosis service is offline"));
    }
}
