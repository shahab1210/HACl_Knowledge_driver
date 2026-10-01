package com.iot.iotfaultdiagnosis;

import com.iot.iotfaultdiagnosis.entity.DiagnosisAlternativeFaultEntity;
import com.iot.iotfaultdiagnosis.entity.DiagnosisEntity;
import com.iot.iotfaultdiagnosis.entity.DiagnosisEvidenceEntity;
import com.iot.iotfaultdiagnosis.entity.DiagnosisKnowledgeSourceEntity;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class DiagnosisEntityTest {

    @Test
    void testDiagnosisEntityGettersAndSetters() {
        DiagnosisEntity entity = new DiagnosisEntity();
        entity.setId(1L);
        entity.setDiagnosisId("diag-001");
        entity.setDeviceId("ESP32_001");
        entity.setTopic("iot/ESP32_001/telemetry");
        LocalDateTime now = LocalDateTime.now();
        entity.setCreatedAt(now);
        entity.setLatencySeconds(2.5);
        entity.setQuery("Query test");
        entity.setModel("qwen2.5:1.5b");
        entity.setRawLlmResponse("Raw response text");

        entity.setTelemetryTemperature(85.5);
        entity.setTelemetryHumidity(45.0);
        entity.setTelemetryVibration(12.3);
        entity.setTelemetryCurrent(22.1);
        entity.setTelemetryPressure(1.5);
        entity.setTelemetryRecordedAt("2026-10-01T01:00:00");

        entity.setPrimaryFaultId("FAULT-001");
        entity.setPrimaryFaultTitle("Bearing Degradation");
        entity.setPrimaryFaultSimilarity(0.89);

        entity.setConfidenceLevel("HIGH");
        entity.setConfidenceReason("Consistent high vibration");

        entity.setGenTotalDuration(5000000000L);
        entity.setGenEvalCount(150);
        entity.setGenEvalDuration(4000000000L);
        entity.setGenPromptEvalCount(250);

        assertEquals(1L, entity.getId());
        assertEquals("diag-001", entity.getDiagnosisId());
        assertEquals("ESP32_001", entity.getDeviceId());
        assertEquals("iot/ESP32_001/telemetry", entity.getTopic());
        assertEquals(now, entity.getCreatedAt());
        assertEquals(2.5, entity.getLatencySeconds());
        assertEquals("Query test", entity.getQuery());
        assertEquals("qwen2.5:1.5b", entity.getModel());
        assertEquals("Raw response text", entity.getRawLlmResponse());

        assertEquals(85.5, entity.getTelemetryTemperature());
        assertEquals(45.0, entity.getTelemetryHumidity());
        assertEquals(12.3, entity.getTelemetryVibration());
        assertEquals(22.1, entity.getTelemetryCurrent());
        assertEquals(1.5, entity.getTelemetryPressure());
        assertEquals("2026-10-01T01:00:00", entity.getTelemetryRecordedAt());

        assertEquals("FAULT-001", entity.getPrimaryFaultId());
        assertEquals("Bearing Degradation", entity.getPrimaryFaultTitle());
        assertEquals(0.89, entity.getPrimaryFaultSimilarity());

        assertEquals("HIGH", entity.getConfidenceLevel());
        assertEquals("Consistent high vibration", entity.getConfidenceReason());

        assertEquals(5000000000L, entity.getGenTotalDuration());
        assertEquals(150, entity.getGenEvalCount());
        assertEquals(4000000000L, entity.getGenEvalDuration());
        assertEquals(250, entity.getGenPromptEvalCount());
    }

    @Test
    void testPrePersistSetsCreatedAt() {
        DiagnosisEntity entity = new DiagnosisEntity();
        assertNull(entity.getCreatedAt());
        entity.prePersist();
        assertNotNull(entity.getCreatedAt());
    }

    @Test
    void testChildEntityAssociations() {
        DiagnosisEntity entity = new DiagnosisEntity();
        entity.setDiagnosisId("diag-assoc-01");

        DiagnosisAlternativeFaultEntity alt = new DiagnosisAlternativeFaultEntity("FAULT-002", "Misalignment", 0.45);
        entity.addAlternativeFault(alt);

        DiagnosisEvidenceEntity ev = new DiagnosisEvidenceEntity("telemetry", "vibration", 12.3, "mm/s", "critical");
        entity.addEvidence(ev);

        DiagnosisKnowledgeSourceEntity ks = new DiagnosisKnowledgeSourceEntity(1, "doc-01", "chunk-01", "Bearing Doc", "kb/bearing.md", 0.92);
        entity.addKnowledgeSource(ks);

        entity.setPossibleCauses(List.of("Lubrication loss"));
        entity.setRecommendedChecks(List.of("Inspect bearing assembly"));
        entity.setAdditionalInformationRequired(List.of("Acoustic ultrasound sensor readings"));

        assertEquals(1, entity.getAlternativeFaults().size());
        assertSame(entity, entity.getAlternativeFaults().get(0).getDiagnosis());
        assertEquals("FAULT-002", entity.getAlternativeFaults().get(0).getFaultId());

        assertEquals(1, entity.getEvidenceList().size());
        assertSame(entity, entity.getEvidenceList().get(0).getDiagnosis());
        assertEquals(12.3, entity.getEvidenceList().get(0).getValue());

        assertEquals(1, entity.getKnowledgeSources().size());
        assertSame(entity, entity.getKnowledgeSources().get(0).getDiagnosis());
        assertEquals(0.92, entity.getKnowledgeSources().get(0).getSimilarity());

        assertEquals(1, entity.getPossibleCauses().size());
        assertEquals("Lubrication loss", entity.getPossibleCauses().get(0));

        assertEquals(1, entity.getRecommendedChecks().size());
        assertEquals("Inspect bearing assembly", entity.getRecommendedChecks().get(0));

        assertEquals(1, entity.getAdditionalInformationRequired().size());
        assertEquals("Acoustic ultrasound sensor readings", entity.getAdditionalInformationRequired().get(0));
    }
}
