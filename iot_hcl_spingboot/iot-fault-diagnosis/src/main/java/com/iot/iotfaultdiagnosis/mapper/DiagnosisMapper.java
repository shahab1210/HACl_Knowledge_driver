package com.iot.iotfaultdiagnosis.mapper;

import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.entity.*;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Component
public class DiagnosisMapper {

    public DiagnosisEntity toEntity(DiagnosisResponse dto) {
        if (dto == null) {
            return null;
        }

        DiagnosisEntity entity = new DiagnosisEntity();
        entity.setDiagnosisId(dto.getId() != null ? dto.getId() : "diag-" + dto.getDeviceId() + "-" + System.currentTimeMillis());
        entity.setDeviceId(dto.getDeviceId());
        entity.setTopic(dto.getTopic());
        entity.setCreatedAt(dto.getTimestamp() != null ? dto.getTimestamp() : LocalDateTime.now());
        entity.setLatencySeconds(dto.getLatencySeconds());

        // Map telemetry
        if (dto.getTelemetry() != null) {
            TelemetryResponse tel = dto.getTelemetry();
            entity.setTelemetryTemperature(tel.getTemperature());
            entity.setTelemetryHumidity(tel.getHumidity());
            entity.setTelemetryVibration(tel.getVibration());
            entity.setTelemetryCurrent(tel.getCurrent());
            entity.setTelemetryPressure(tel.getPressure());
            entity.setTelemetryRecordedAt(tel.getRecordedAt());
            if (entity.getDeviceId() == null) {
                entity.setDeviceId(tel.getDeviceId());
            }
        }

        // Map diagnosis details
        if (dto.getDiagnosis() != null) {
            DiagnosisDetailResponse detail = dto.getDiagnosis();
            entity.setQuery(detail.getQuery());
            entity.setModel(detail.getModel());
            entity.setRawLlmResponse(detail.getRawLlmResponse());

            if (detail.getPrimaryFault() != null) {
                FaultResponse pf = detail.getPrimaryFault();
                entity.setPrimaryFaultId(pf.getFaultId());
                entity.setPrimaryFaultTitle(pf.getTitle());
                entity.setPrimaryFaultSimilarity(pf.getSimilarity());
            }

            if (detail.getConfidence() != null) {
                ConfidenceResponse conf = detail.getConfidence();
                entity.setConfidenceLevel(conf.getLevel());
                entity.setConfidenceReason(conf.getReason());
            }

            if (detail.getGenerationDetails() != null) {
                GenerationDetailsResponse gen = detail.getGenerationDetails();
                entity.setGenTotalDuration(gen.getTotalDuration());
                entity.setGenEvalCount(gen.getEvalCount());
                entity.setGenEvalDuration(gen.getEvalDuration());
                entity.setGenPromptEvalCount(gen.getPromptEvalCount());
            }

            // Alternative faults
            if (detail.getAlternativeFaults() != null) {
                for (FaultResponse alt : detail.getAlternativeFaults()) {
                    if (alt != null) {
                        entity.addAlternativeFault(new DiagnosisAlternativeFaultEntity(
                                alt.getFaultId(),
                                alt.getTitle(),
                                alt.getSimilarity()
                        ));
                    }
                }
            }

            // Evidence
            if (detail.getEvidence() != null) {
                for (EvidenceResponse ev : detail.getEvidence()) {
                    if (ev != null) {
                        entity.addEvidence(new DiagnosisEvidenceEntity(
                                ev.getType(),
                                ev.getParameter(),
                                ev.getValue(),
                                ev.getUnit(),
                                ev.getStatus()
                        ));
                    }
                }
            }

            // Knowledge sources
            if (detail.getKnowledgeSources() != null) {
                for (KnowledgeSourceResponse ks : detail.getKnowledgeSources()) {
                    if (ks != null) {
                        entity.addKnowledgeSource(new DiagnosisKnowledgeSourceEntity(
                                ks.getRank(),
                                ks.getDocumentId(),
                                ks.getChunkId(),
                                ks.getTitle(),
                                ks.getSource(),
                                ks.getSimilarity()
                        ));
                    }
                }
            }

            // String collections
            if (detail.getPossibleCauses() != null) {
                entity.setPossibleCauses(new ArrayList<>(detail.getPossibleCauses()));
            }
            if (detail.getRecommendedChecks() != null) {
                entity.setRecommendedChecks(new ArrayList<>(detail.getRecommendedChecks()));
            }
            if (detail.getAdditionalInformationRequired() != null) {
                entity.setAdditionalInformationRequired(new ArrayList<>(detail.getAdditionalInformationRequired()));
            }
        }

        return entity;
    }

    public DiagnosisResponse toDto(DiagnosisEntity entity) {
        if (entity == null) {
            return null;
        }

        DiagnosisResponse dto = new DiagnosisResponse();
        dto.setId(entity.getDiagnosisId());
        dto.setDeviceId(entity.getDeviceId());
        dto.setTopic(entity.getTopic());
        dto.setTimestamp(entity.getCreatedAt());
        dto.setLatencySeconds(entity.getLatencySeconds());

        // Build TelemetryResponse
        TelemetryResponse telemetry = new TelemetryResponse(
                entity.getDeviceId(),
                entity.getTelemetryTemperature(),
                entity.getTelemetryHumidity(),
                entity.getTelemetryVibration(),
                entity.getTelemetryCurrent(),
                entity.getTelemetryPressure(),
                entity.getTelemetryRecordedAt()
        );
        dto.setTelemetry(telemetry);

        // Build DiagnosisDetailResponse
        DiagnosisDetailResponse detail = new DiagnosisDetailResponse();
        detail.setQuery(entity.getQuery());
        detail.setModel(entity.getModel());
        detail.setRawLlmResponse(entity.getRawLlmResponse());

        if (entity.getPrimaryFaultId() != null || entity.getPrimaryFaultTitle() != null || entity.getPrimaryFaultSimilarity() != null) {
            detail.setPrimaryFault(new FaultResponse(
                    entity.getPrimaryFaultId(),
                    entity.getPrimaryFaultTitle(),
                    entity.getPrimaryFaultSimilarity()
            ));
        }

        if (entity.getConfidenceLevel() != null || entity.getConfidenceReason() != null) {
            detail.setConfidence(new ConfidenceResponse(
                    entity.getConfidenceLevel(),
                    entity.getConfidenceReason()
            ));
        }

        if (entity.getGenTotalDuration() != null || entity.getGenEvalCount() != null ||
                entity.getGenEvalDuration() != null || entity.getGenPromptEvalCount() != null) {
            detail.setGenerationDetails(new GenerationDetailsResponse(
                    entity.getGenTotalDuration(),
                    entity.getGenEvalCount(),
                    entity.getGenEvalDuration(),
                    entity.getGenPromptEvalCount()
            ));
        }

        // Alternative faults
        if (entity.getAlternativeFaults() != null && !entity.getAlternativeFaults().isEmpty()) {
            List<FaultResponse> altList = new ArrayList<>();
            for (DiagnosisAlternativeFaultEntity alt : entity.getAlternativeFaults()) {
                altList.add(new FaultResponse(alt.getFaultId(), alt.getTitle(), alt.getSimilarity()));
            }
            detail.setAlternativeFaults(altList);
        }

        // Evidence
        if (entity.getEvidenceList() != null && !entity.getEvidenceList().isEmpty()) {
            List<EvidenceResponse> evList = new ArrayList<>();
            for (DiagnosisEvidenceEntity ev : entity.getEvidenceList()) {
                evList.add(new EvidenceResponse(
                        ev.getType(),
                        ev.getParameter(),
                        ev.getValue(),
                        ev.getUnit(),
                        ev.getStatus()
                ));
            }
            detail.setEvidence(evList);
        }

        // Knowledge sources
        if (entity.getKnowledgeSources() != null && !entity.getKnowledgeSources().isEmpty()) {
            List<KnowledgeSourceResponse> ksList = new ArrayList<>();
            for (DiagnosisKnowledgeSourceEntity ks : entity.getKnowledgeSources()) {
                ksList.add(new KnowledgeSourceResponse(
                        ks.getRank(),
                        ks.getDocumentId(),
                        ks.getChunkId(),
                        ks.getTitle(),
                        ks.getSource(),
                        ks.getSimilarity()
                ));
            }
            detail.setKnowledgeSources(ksList);
        }

        // String collections
        if (entity.getPossibleCauses() != null) {
            detail.setPossibleCauses(new ArrayList<>(entity.getPossibleCauses()));
        }
        if (entity.getRecommendedChecks() != null) {
            detail.setRecommendedChecks(new ArrayList<>(entity.getRecommendedChecks()));
        }
        if (entity.getAdditionalInformationRequired() != null) {
            detail.setAdditionalInformationRequired(new ArrayList<>(entity.getAdditionalInformationRequired()));
        }

        dto.setDiagnosis(detail);
        return dto;
    }
}
