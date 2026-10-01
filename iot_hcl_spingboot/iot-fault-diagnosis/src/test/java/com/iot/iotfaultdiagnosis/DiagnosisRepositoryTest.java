package com.iot.iotfaultdiagnosis;

import com.iot.iotfaultdiagnosis.entity.DiagnosisAlternativeFaultEntity;
import com.iot.iotfaultdiagnosis.entity.DiagnosisEntity;
import com.iot.iotfaultdiagnosis.entity.DiagnosisEvidenceEntity;
import com.iot.iotfaultdiagnosis.entity.DiagnosisKnowledgeSourceEntity;
import com.iot.iotfaultdiagnosis.repository.DiagnosisRepository;
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
public class DiagnosisRepositoryTest {

    @Autowired
    private DiagnosisRepository diagnosisRepository;

    @BeforeEach
    void setUp() {
        diagnosisRepository.deleteAll();
    }

    @Test
    void testSaveAndFindByDiagnosisId() {
        DiagnosisEntity entity = new DiagnosisEntity();
        entity.setDiagnosisId("diag-repo-001");
        entity.setDeviceId("ESP32_001");
        entity.setTopic("iot/ESP32_001/telemetry");
        entity.setCreatedAt(LocalDateTime.now());
        entity.setTelemetryTemperature(88.0);
        entity.setTelemetryVibration(11.5);
        entity.setPrimaryFaultId("FAULT-001");
        entity.setPrimaryFaultTitle("Bearing Wear");
        entity.setConfidenceLevel("HIGH");

        DiagnosisAlternativeFaultEntity alt = new DiagnosisAlternativeFaultEntity("FAULT-002", "Misalignment", 0.4);
        entity.addAlternativeFault(alt);

        DiagnosisEvidenceEntity ev = new DiagnosisEvidenceEntity("telemetry", "vibration", 11.5, "mm/s", "critical");
        entity.addEvidence(ev);

        DiagnosisKnowledgeSourceEntity ks = new DiagnosisKnowledgeSourceEntity(1, "doc-01", "chunk-01", "Bearing Signatures", "kb/bearing.md", 0.9);
        entity.addKnowledgeSource(ks);

        entity.setPossibleCauses(List.of("Lubrication loss"));
        entity.setRecommendedChecks(List.of("Check bearing"));

        DiagnosisEntity saved = diagnosisRepository.save(entity);
        assertNotNull(saved.getId());

        Optional<DiagnosisEntity> retrieved = diagnosisRepository.findByDiagnosisId("diag-repo-001");
        assertTrue(retrieved.isPresent());
        assertEquals("ESP32_001", retrieved.get().getDeviceId());
        assertEquals(88.0, retrieved.get().getTelemetryTemperature());
        assertEquals(1, retrieved.get().getAlternativeFaults().size());
        assertEquals(1, retrieved.get().getEvidenceList().size());
        assertEquals(1, retrieved.get().getKnowledgeSources().size());
        assertEquals(1, retrieved.get().getPossibleCauses().size());
    }

    @Test
    void testFindTopByOrderByCreatedAtDesc() {
        DiagnosisEntity e1 = new DiagnosisEntity();
        e1.setDiagnosisId("diag-old");
        e1.setDeviceId("ESP32_001");
        e1.setCreatedAt(LocalDateTime.now().minusHours(2));
        diagnosisRepository.save(e1);

        DiagnosisEntity e2 = new DiagnosisEntity();
        e2.setDiagnosisId("diag-new");
        e2.setDeviceId("ESP32_001");
        e2.setCreatedAt(LocalDateTime.now().minusMinutes(5));
        diagnosisRepository.save(e2);

        Optional<DiagnosisEntity> latest = diagnosisRepository.findTopByOrderByCreatedAtDesc();
        assertTrue(latest.isPresent());
        assertEquals("diag-new", latest.get().getDiagnosisId());
    }

    @Test
    void testFindByDeviceIdOrderByCreatedAtDesc() {
        DiagnosisEntity e1 = new DiagnosisEntity();
        e1.setDiagnosisId("diag-dev1-old");
        e1.setDeviceId("ESP32_001");
        e1.setCreatedAt(LocalDateTime.now().minusHours(1));
        diagnosisRepository.save(e1);

        DiagnosisEntity e2 = new DiagnosisEntity();
        e2.setDiagnosisId("diag-dev1-new");
        e2.setDeviceId("ESP32_001");
        e2.setCreatedAt(LocalDateTime.now());
        diagnosisRepository.save(e2);

        DiagnosisEntity e3 = new DiagnosisEntity();
        e3.setDiagnosisId("diag-dev2");
        e3.setDeviceId("ESP32_002");
        e3.setCreatedAt(LocalDateTime.now());
        diagnosisRepository.save(e3);

        List<DiagnosisEntity> dev1List = diagnosisRepository.findByDeviceIdOrderByCreatedAtDesc("ESP32_001");
        assertEquals(2, dev1List.size());
        assertEquals("diag-dev1-new", dev1List.get(0).getDiagnosisId());
        assertEquals("diag-dev1-old", dev1List.get(1).getDiagnosisId());

        List<DiagnosisEntity> dev2List = diagnosisRepository.findByDeviceIdOrderByCreatedAtDesc("ESP32_002");
        assertEquals(1, dev2List.size());
        assertEquals("diag-dev2", dev2List.get(0).getDiagnosisId());
    }

    @Test
    void testExistsByDiagnosisId() {
        DiagnosisEntity entity = new DiagnosisEntity();
        entity.setDiagnosisId("diag-exists-check");
        entity.setDeviceId("ESP32_001");
        entity.setCreatedAt(LocalDateTime.now());
        diagnosisRepository.save(entity);

        assertTrue(diagnosisRepository.existsByDiagnosisId("diag-exists-check"));
        assertFalse(diagnosisRepository.existsByDiagnosisId("diag-non-existent"));
    }
}
