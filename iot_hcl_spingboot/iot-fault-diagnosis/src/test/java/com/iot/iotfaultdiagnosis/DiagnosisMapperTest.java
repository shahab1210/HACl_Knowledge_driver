package com.iot.iotfaultdiagnosis;

import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.entity.DiagnosisEntity;
import com.iot.iotfaultdiagnosis.mapper.DiagnosisMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class DiagnosisMapperTest {

    private DiagnosisMapper mapper;

    @BeforeEach
    void setUp() {
        mapper = new DiagnosisMapper();
    }

    @Test
    void testToEntityAndBackToDto_FullFidelity() {
        TelemetryResponse telemetry = new TelemetryResponse(
                "ESP32_001",
                92.5,
                48.0,
                14.2,
                26.8,
                2.4,
                "2026-10-01T02:00:00"
        );

        DiagnosisDetailResponse detail = new DiagnosisDetailResponse();
        detail.setQuery("Observation: high vibration 14.2");
        detail.setModel("qwen2.5:1.5b");
        detail.setRawLlmResponse("Detailed LLM diagnostic reasoning output");
        detail.setPrimaryFault(new FaultResponse("FAULT_BEARING_001", "Bearing Degradation", 0.94));
        detail.setConfidence(new ConfidenceResponse("HIGH", "Vibration threshold exceeded"));
        detail.setGenerationDetails(new GenerationDetailsResponse(3200000000L, 210, 2900000000L, 340));
        detail.setAlternativeFaults(List.of(new FaultResponse("FAULT_MISALIGN_002", "Shaft Misalignment", 0.38)));
        detail.setEvidence(List.of(new EvidenceResponse("telemetry", "vibration", 14.2, "mm/s", "critical")));
        detail.setKnowledgeSources(List.of(new KnowledgeSourceResponse(1, "KB_BEARING_01", "chunk_03", "Bearing Signatures", "kb/bearing.md", 0.94)));
        detail.setPossibleCauses(List.of("Lubricant contamination", "Excessive radial load"));
        detail.setRecommendedChecks(List.of("Check lubricant viscosity", "Measure vibration spectra"));
        detail.setAdditionalInformationRequired(List.of("Acoustic ultrasound emission data"));

        LocalDateTime timestamp = LocalDateTime.of(2026, 10, 1, 2, 0, 0);
        DiagnosisResponse originalDto = new DiagnosisResponse(
                "diag-ESP32_001-TEST",
                "ESP32_001",
                "iot/ESP32_001/telemetry",
                timestamp,
                telemetry,
                detail,
                3.14
        );

        // 1. Convert to entity
        DiagnosisEntity entity = mapper.toEntity(originalDto);
        assertNotNull(entity);
        assertEquals("diag-ESP32_001-TEST", entity.getDiagnosisId());
        assertEquals("ESP32_001", entity.getDeviceId());
        assertEquals(92.5, entity.getTelemetryTemperature());
        assertEquals(14.2, entity.getTelemetryVibration());
        assertEquals("FAULT_BEARING_001", entity.getPrimaryFaultId());
        assertEquals("HIGH", entity.getConfidenceLevel());
        assertEquals(1, entity.getAlternativeFaults().size());
        assertEquals(1, entity.getEvidenceList().size());
        assertEquals(1, entity.getKnowledgeSources().size());
        assertEquals(2, entity.getPossibleCauses().size());
        assertEquals(2, entity.getRecommendedChecks().size());
        assertEquals(1, entity.getAdditionalInformationRequired().size());

        // 2. Convert back to DTO
        DiagnosisResponse reconstructedDto = mapper.toDto(entity);
        assertNotNull(reconstructedDto);
        assertEquals(originalDto.getId(), reconstructedDto.getId());
        assertEquals(originalDto.getDeviceId(), reconstructedDto.getDeviceId());
        assertEquals(originalDto.getTopic(), reconstructedDto.getTopic());
        assertEquals(originalDto.getTimestamp(), reconstructedDto.getTimestamp());
        assertEquals(originalDto.getLatencySeconds(), reconstructedDto.getLatencySeconds());

        assertNotNull(reconstructedDto.getTelemetry());
        assertEquals(92.5, reconstructedDto.getTelemetry().getTemperature());
        assertEquals(14.2, reconstructedDto.getTelemetry().getVibration());

        assertNotNull(reconstructedDto.getDiagnosis());
        assertEquals("FAULT_BEARING_001", reconstructedDto.getDiagnosis().getPrimaryFault().getFaultId());
        assertEquals("HIGH", reconstructedDto.getDiagnosis().getConfidence().getLevel());
        assertEquals(1, reconstructedDto.getDiagnosis().getAlternativeFaults().size());
        assertEquals("FAULT_MISALIGN_002", reconstructedDto.getDiagnosis().getAlternativeFaults().get(0).getFaultId());
        assertEquals(1, reconstructedDto.getDiagnosis().getEvidence().size());
        assertEquals(14.2, reconstructedDto.getDiagnosis().getEvidence().get(0).getValue());
        assertEquals(1, reconstructedDto.getDiagnosis().getKnowledgeSources().size());
        assertEquals("KB_BEARING_01", reconstructedDto.getDiagnosis().getKnowledgeSources().get(0).getDocumentId());
        assertEquals(2, reconstructedDto.getDiagnosis().getPossibleCauses().size());
        assertEquals(2, reconstructedDto.getDiagnosis().getRecommendedChecks().size());
        assertEquals(1, reconstructedDto.getDiagnosis().getAdditionalInformationRequired().size());
    }

    @Test
    void testNullSafety() {
        assertNull(mapper.toEntity(null));
        assertNull(mapper.toDto(null));

        DiagnosisResponse emptyDto = new DiagnosisResponse();
        DiagnosisEntity entity = mapper.toEntity(emptyDto);
        assertNotNull(entity);
        assertNotNull(entity.getDiagnosisId()); // auto-generated fallback ID

        DiagnosisEntity emptyEntity = new DiagnosisEntity();
        DiagnosisResponse dto = mapper.toDto(emptyEntity);
        assertNotNull(dto);
    }
}
