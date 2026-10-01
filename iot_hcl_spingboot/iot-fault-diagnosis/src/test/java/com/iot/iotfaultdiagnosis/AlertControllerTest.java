package com.iot.iotfaultdiagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iot.iotfaultdiagnosis.entity.AlertEntity;
import com.iot.iotfaultdiagnosis.entity.AlertSeverity;
import com.iot.iotfaultdiagnosis.entity.AlertType;
import com.iot.iotfaultdiagnosis.repository.AlertRepository;
import com.iot.iotfaultdiagnosis.repository.UserRepository;
import com.iot.iotfaultdiagnosis.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class AlertControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private AlertRepository alertRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    private String authToken;

    @BeforeEach
    void setUp() {
        alertRepository.deleteAll();
        userRepository.deleteAll();
        authToken = "Bearer " + jwtTokenProvider.generateToken("test_operator", "USER");
    }

    @Test
    void testGetAlerts_UnauthorizedWithoutToken() throws Exception {
        mockMvc.perform(get("/api/v1/alerts"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void testGetAlerts_AuthorizedEmptyList() throws Exception {
        mockMvc.perform(get("/api/v1/alerts")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(content().json("[]"));
    }

    @Test
    void testGetAlerts_WithData() throws Exception {
        AlertEntity alert1 = new AlertEntity(
                "ESP32_001",
                AlertType.SENSOR_THRESHOLD,
                AlertSeverity.WARNING,
                "Elevated temperature",
                "TELEMETRY_INGESTION",
                "temperature",
                78.5,
                75.0
        );
        AlertEntity alert2 = new AlertEntity(
                "ESP32_001",
                AlertType.SENSOR_THRESHOLD,
                AlertSeverity.CRITICAL,
                "Critical motor overcurrent",
                "TELEMETRY_INGESTION",
                "current",
                11.0,
                10.5
        );
        alertRepository.save(alert1);
        alertRepository.save(alert2);

        mockMvc.perform(get("/api/v1/alerts")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].deviceId").value("ESP32_001"));
    }

    @Test
    void testGetLatestAlert_Success() throws Exception {
        AlertEntity alert = new AlertEntity(
                "ESP32_001",
                AlertType.SENSOR_THRESHOLD,
                AlertSeverity.CRITICAL,
                "Severe vibration detected",
                "TELEMETRY_INGESTION",
                "vibration",
                8.2,
                7.1
        );
        alertRepository.save(alert);

        mockMvc.perform(get("/api/v1/alerts/latest")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"))
                .andExpect(jsonPath("$.severity").value("CRITICAL"))
                .andExpect(jsonPath("$.sensorParameter").value("vibration"));
    }

    @Test
    void testGetLatestAlert_NotFoundWhenEmpty() throws Exception {
        mockMvc.perform(get("/api/v1/alerts/latest")
                        .header("Authorization", authToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404));
    }

    @Test
    void testGetAlertById_Success() throws Exception {
        AlertEntity alert = new AlertEntity(
                "ESP32_001",
                AlertType.SENSOR_THRESHOLD,
                AlertSeverity.WARNING,
                "High discharge pressure",
                "TELEMETRY_INGESTION",
                "pressure",
                4.0,
                3.8
        );
        AlertEntity saved = alertRepository.save(alert);

        mockMvc.perform(get("/api/v1/alerts/" + saved.getId())
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(saved.getId()))
                .andExpect(jsonPath("$.message").value("High discharge pressure"));
    }

    @Test
    void testGetAlertById_NotFound() throws Exception {
        mockMvc.perform(get("/api/v1/alerts/999999")
                        .header("Authorization", authToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404));
    }

    @Test
    void testFilterAlertsByAcknowledgedAndDeviceId() throws Exception {
        AlertEntity active = new AlertEntity("ESP32_001", AlertType.SENSOR_THRESHOLD, AlertSeverity.CRITICAL,
                "Active alert", "TELEMETRY", "temperature", 92.0, 90.0);
        AlertEntity acked = new AlertEntity("ESP32_001", AlertType.SENSOR_THRESHOLD, AlertSeverity.WARNING,
                "Acknowledged alert", "TELEMETRY", "temperature", 77.0, 75.0);
        acked.setAcknowledged(true);
        acked.setAcknowledgedAt(LocalDateTime.now());
        acked.setAcknowledgedBy("admin");

        alertRepository.save(active);
        alertRepository.save(acked);

        mockMvc.perform(get("/api/v1/alerts?deviceId=ESP32_001&acknowledged=false")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].acknowledged").value(false))
                .andExpect(jsonPath("$[0].message").value("Active alert"));
    }

    @Test
    void testAcknowledgeAlert_Success() throws Exception {
        AlertEntity alert = new AlertEntity(
                "ESP32_001",
                AlertType.SENSOR_THRESHOLD,
                AlertSeverity.CRITICAL,
                "Critical condition needing acknowledgement",
                "TELEMETRY_INGESTION",
                "temperature",
                91.0,
                90.0
        );
        AlertEntity saved = alertRepository.save(alert);
        assertThat(saved.isAcknowledged()).isFalse();

        mockMvc.perform(post("/api/v1/alerts/" + saved.getId() + "/acknowledge")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(saved.getId()))
                .andExpect(jsonPath("$.acknowledged").value(true))
                .andExpect(jsonPath("$.acknowledgedBy").value("test_operator"))
                .andExpect(jsonPath("$.acknowledgedAt").isNotEmpty());

        AlertEntity updatedInDb = alertRepository.findById(saved.getId()).orElseThrow();
        assertThat(updatedInDb.isAcknowledged()).isTrue();
        assertThat(updatedInDb.getAcknowledgedBy()).isEqualTo("test_operator");
    }
}
