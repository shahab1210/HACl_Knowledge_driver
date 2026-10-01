package com.iot.iotfaultdiagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.security.JwtTokenProvider;
import com.iot.iotfaultdiagnosis.service.DiagnosisStore;
import com.iot.iotfaultdiagnosis.service.ai.AIDiagnosisClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.mockito.ArgumentMatchers.any;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class DiagnosisIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private DiagnosisStore store;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @MockitoBean
    private AIDiagnosisClient aiDiagnosisClient;

    private String authToken;

    @BeforeEach
    void setUp() {
        store.clear();
        authToken = "Bearer " + jwtTokenProvider.generateToken("operator", "USER");

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
        detail.setPrimaryFault(new FaultResponse("FAULT-003", "Motor Overheating", 0.91));
        detail.setConfidence(new ConfidenceResponse("high", "Consistent with motor thermal distress"));

        DiagnosisResponse sample = new DiagnosisResponse(
                "diag-ESP32_001-INTEGRATION",
                "ESP32_001",
                "iot/ESP32_001/telemetry",
                LocalDateTime.now(),
                telemetry,
                detail,
                1.85
        );

        Mockito.when(aiDiagnosisClient.diagnose(any(TelemetryRequest.class))).thenReturn(sample);
    }

    @Test
    void testEndToEndDiagnosisFlow() throws Exception {
        // 1. Verify GET latest returns 404 when store is empty (with auth)
        mockMvc.perform(get("/api/v1/diagnosis/latest")
                        .header("Authorization", authToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404));

        // 2. Trigger on-demand POST diagnosis
        TelemetryRequest request = new TelemetryRequest(
                "ESP32_001",
                95.0,
                45.0,
                7.2,
                8.4,
                2.1
        );

        mockMvc.perform(post("/api/v1/diagnosis")
                        .header("Authorization", authToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value("diag-ESP32_001-INTEGRATION"))
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"))
                .andExpect(jsonPath("$.diagnosis.primaryFault.faultId").value("FAULT-003"));

        // 3. Verify GET latest returns the newly stored diagnosis
        mockMvc.perform(get("/api/v1/diagnosis/latest")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("diag-ESP32_001-INTEGRATION"))
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"));

        // 4. Verify GET by ID
        mockMvc.perform(get("/api/v1/diagnosis/diag-ESP32_001-INTEGRATION")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("diag-ESP32_001-INTEGRATION"));

        // 5. Verify GET by device
        mockMvc.perform(get("/api/v1/diagnosis/device/ESP32_001")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value("diag-ESP32_001-INTEGRATION"));
    }
}

