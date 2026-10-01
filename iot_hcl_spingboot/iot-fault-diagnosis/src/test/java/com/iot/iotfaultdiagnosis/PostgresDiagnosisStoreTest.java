package com.iot.iotfaultdiagnosis;

import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.service.PostgresDiagnosisStore;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
public class PostgresDiagnosisStoreTest {

    @Autowired
    private PostgresDiagnosisStore store;

    private DiagnosisResponse sample;

    @BeforeEach
    void setUp() {
        store.clear();

        TelemetryResponse tel = new TelemetryResponse("ESP32_001", 91.0, 42.0, 13.5, 25.0, 2.0, "2026-10-01T02:00:00");
        DiagnosisDetailResponse detail = new DiagnosisDetailResponse();
        detail.setPrimaryFault(new FaultResponse("FAULT-001", "Bearing Degradation", 0.92));
        detail.setConfidence(new ConfidenceResponse("HIGH", "Thermal and vibration signatures match"));
        detail.setAlternativeFaults(List.of(new FaultResponse("FAULT-002", "Misalignment", 0.40)));
        detail.setEvidence(List.of(new EvidenceResponse("telemetry", "vibration", 13.5, "mm/s", "critical")));
        detail.setKnowledgeSources(List.of(new KnowledgeSourceResponse(1, "KB_BEARING_01", "chunk_01", "Bearing Signatures", "kb/bearing.md", 0.92)));
        detail.setPossibleCauses(List.of("Lubrication loss"));
        detail.setRecommendedChecks(List.of("Inspect bearing"));

        sample = new DiagnosisResponse(
                "diag-pg-store-001",
                "ESP32_001",
                "iot/ESP32_001/telemetry",
                LocalDateTime.now(),
                tel,
                detail,
                2.15
        );
    }

    @Test
    void testSaveAndGetById() {
        store.save(sample);

        Optional<DiagnosisResponse> retrieved = store.getById("diag-pg-store-001");
        assertTrue(retrieved.isPresent());
        assertEquals("diag-pg-store-001", retrieved.get().getId());
        assertEquals("ESP32_001", retrieved.get().getDeviceId());
        assertEquals(91.0, retrieved.get().getTelemetry().getTemperature());
        assertEquals("FAULT-001", retrieved.get().getDiagnosis().getPrimaryFault().getFaultId());
        assertEquals(1, retrieved.get().getDiagnosis().getAlternativeFaults().size());
        assertEquals(1, retrieved.get().getDiagnosis().getEvidence().size());
        assertEquals(1, retrieved.get().getDiagnosis().getKnowledgeSources().size());
    }

    @Test
    void testGetLatest() {
        store.save(sample);

        Optional<DiagnosisResponse> latest = store.getLatest();
        assertTrue(latest.isPresent());
        assertEquals("diag-pg-store-001", latest.get().getId());
    }

    @Test
    void testGetByDeviceId() {
        store.save(sample);

        List<DiagnosisResponse> list = store.getByDeviceId("ESP32_001");
        assertEquals(1, list.size());
        assertEquals("diag-pg-store-001", list.get(0).getId());

        List<DiagnosisResponse> emptyList = store.getByDeviceId("NON_EXISTENT");
        assertTrue(emptyList.isEmpty());
    }

    @Test
    void testIdempotentSaveDuplicateId() {
        store.save(sample);
        assertEquals(1, store.size());

        // Update title and save same diagnosis ID
        sample.getDiagnosis().getPrimaryFault().setTitle("Updated Bearing Degradation");
        store.save(sample);

        assertEquals(1, store.size());
        Optional<DiagnosisResponse> updated = store.getById("diag-pg-store-001");
        assertTrue(updated.isPresent());
        assertEquals("Updated Bearing Degradation", updated.get().getDiagnosis().getPrimaryFault().getTitle());
    }

    @Test
    void testClearAndSize() {
        store.save(sample);
        assertEquals(1, store.size());

        store.clear();
        assertEquals(0, store.size());
        assertTrue(store.getLatest().isEmpty());
    }
}
