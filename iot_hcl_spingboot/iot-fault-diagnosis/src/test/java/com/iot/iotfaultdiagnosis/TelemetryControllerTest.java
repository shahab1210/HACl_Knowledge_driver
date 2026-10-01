package com.iot.iotfaultdiagnosis;

import com.iot.iotfaultdiagnosis.entity.SensorReading;
import com.iot.iotfaultdiagnosis.repository.SensorReadingRepository;
import com.iot.iotfaultdiagnosis.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class TelemetryControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private SensorReadingRepository sensorReadingRepository;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    private String authToken;

    @BeforeEach
    void setUp() {
        sensorReadingRepository.deleteAll();
        authToken = "Bearer " + jwtTokenProvider.generateToken("test_operator", "USER");
    }

    @Test
    void testGetLatest_UnauthorizedWithoutToken() throws Exception {
        mockMvc.perform(get("/api/v1/telemetry/latest"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void testGetLatest_EmptyDatabase_Returns404() throws Exception {
        mockMvc.perform(get("/api/v1/telemetry/latest")
                        .header("Authorization", authToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error").value("Not Found"));
    }

    @Test
    void testGetLatest_WithReadings_ReturnsNewest() throws Exception {
        SensorReading r1 = new SensorReading();
        r1.setDeviceId("ESP32_001");
        r1.setTemperature(25.0);
        r1.setHumidity(50.0);
        r1.setVibration(1.2);
        r1.setCurrentValue(4.5);
        r1.setPressure(2.1);
        r1.setRecordedAt(LocalDateTime.now().minusMinutes(5));
        sensorReadingRepository.save(r1);

        SensorReading r2 = new SensorReading();
        r2.setDeviceId("ESP32_001");
        r2.setTemperature(31.4);
        r2.setHumidity(55.5);
        r2.setVibration(1.8);
        r2.setCurrentValue(5.6);
        r2.setPressure(2.7);
        r2.setRecordedAt(LocalDateTime.now());
        sensorReadingRepository.save(r2);

        mockMvc.perform(get("/api/v1/telemetry/latest?deviceId=ESP32_001")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"))
                .andExpect(jsonPath("$.temperature").value(31.4))
                .andExpect(jsonPath("$.humidity").value(55.5))
                .andExpect(jsonPath("$.vibration").value(1.8))
                .andExpect(jsonPath("$.current").value(5.6))
                .andExpect(jsonPath("$.pressure").value(2.7))
                .andExpect(jsonPath("$.recordedAt").isNotEmpty());
    }

    @Test
    void testGetLatest_FilterByDeviceId() throws Exception {
        SensorReading r1 = new SensorReading();
        r1.setDeviceId("ESP32_001");
        r1.setTemperature(28.0);
        r1.setCurrentValue(4.0);
        r1.setRecordedAt(LocalDateTime.now());
        sensorReadingRepository.save(r1);

        SensorReading r2 = new SensorReading();
        r2.setDeviceId("ESP32_002");
        r2.setTemperature(85.0);
        r2.setCurrentValue(12.0);
        r2.setRecordedAt(LocalDateTime.now());
        sensorReadingRepository.save(r2);

        mockMvc.perform(get("/api/v1/telemetry/latest?deviceId=ESP32_001")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.deviceId").value("ESP32_001"))
                .andExpect(jsonPath("$.temperature").value(28.0));

        mockMvc.perform(get("/api/v1/telemetry/latest?deviceId=ESP32_002")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.deviceId").value("ESP32_002"))
                .andExpect(jsonPath("$.temperature").value(85.0));
    }

    @Test
    void testGetHistory_UnauthorizedWithoutToken() throws Exception {
        mockMvc.perform(get("/api/v1/telemetry/history"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void testGetHistory_EmptyDatabase_ReturnsEmptyList() throws Exception {
        mockMvc.perform(get("/api/v1/telemetry/history")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void testGetHistory_ChronologicalOrderingAndLimit() throws Exception {
        // Save 3 readings with different timestamps
        LocalDateTime now = LocalDateTime.now();

        SensorReading r1 = new SensorReading();
        r1.setDeviceId("ESP32_001");
        r1.setTemperature(20.0);
        r1.setCurrentValue(3.0);
        r1.setRecordedAt(now.minusSeconds(30));
        sensorReadingRepository.save(r1);

        SensorReading r2 = new SensorReading();
        r2.setDeviceId("ESP32_001");
        r2.setTemperature(25.0);
        r2.setCurrentValue(4.0);
        r2.setRecordedAt(now.minusSeconds(20));
        sensorReadingRepository.save(r2);

        SensorReading r3 = new SensorReading();
        r3.setDeviceId("ESP32_001");
        r3.setTemperature(30.0);
        r3.setCurrentValue(5.0);
        r3.setRecordedAt(now.minusSeconds(10));
        sensorReadingRepository.save(r3);

        // Fetch history with limit=2 (should get the 2 newest, ordered oldest-to-newest for chart: r2, r3)
        mockMvc.perform(get("/api/v1/telemetry/history?deviceId=ESP32_001&limit=2")
                        .header("Authorization", authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].temperature").value(25.0))
                .andExpect(jsonPath("$[1].temperature").value(30.0));
    }
}
