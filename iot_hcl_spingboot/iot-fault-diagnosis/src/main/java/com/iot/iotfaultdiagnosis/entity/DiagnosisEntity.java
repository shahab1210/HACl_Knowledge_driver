package com.iot.iotfaultdiagnosis.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "diagnoses", indexes = {
        @Index(name = "idx_diag_id", columnList = "diagnosis_id", unique = true),
        @Index(name = "idx_diag_device_id", columnList = "device_id"),
        @Index(name = "idx_diag_created_at", columnList = "created_at")
})
public class DiagnosisEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "diagnosis_id", nullable = false, unique = true)
    private String diagnosisId;

    @Column(name = "device_id", nullable = false)
    private String deviceId;

    @Column(name = "topic")
    private String topic;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "latency_seconds")
    private Double latencySeconds;

    @Column(name = "query", columnDefinition = "TEXT")
    private String query;

    @Column(name = "model")
    private String model;

    @Column(name = "raw_llm_response", columnDefinition = "TEXT")
    private String rawLlmResponse;

    // --- Telemetry Fields ---
    @Column(name = "telemetry_temperature")
    private Double telemetryTemperature;

    @Column(name = "telemetry_humidity")
    private Double telemetryHumidity;

    @Column(name = "telemetry_vibration")
    private Double telemetryVibration;

    @Column(name = "telemetry_current")
    private Double telemetryCurrent;

    @Column(name = "telemetry_pressure")
    private Double telemetryPressure;

    @Column(name = "telemetry_recorded_at")
    private String telemetryRecordedAt;

    // --- Primary Fault Fields ---
    @Column(name = "primary_fault_id")
    private String primaryFaultId;

    @Column(name = "primary_fault_title")
    private String primaryFaultTitle;

    @Column(name = "primary_fault_similarity")
    private Double primaryFaultSimilarity;

    // --- Confidence Fields ---
    @Column(name = "confidence_level")
    private String confidenceLevel;

    @Column(name = "confidence_reason", columnDefinition = "TEXT")
    private String confidenceReason;

    // --- Generation Details Fields ---
    @Column(name = "gen_total_duration")
    private Long genTotalDuration;

    @Column(name = "gen_eval_count")
    private Integer genEvalCount;

    @Column(name = "gen_eval_duration")
    private Long genEvalDuration;

    @Column(name = "gen_prompt_eval_count")
    private Integer genPromptEvalCount;

    // --- One-to-Many Child Relationships ---
    @OneToMany(mappedBy = "diagnosis", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.EAGER)
    private List<DiagnosisAlternativeFaultEntity> alternativeFaults = new ArrayList<>();

    @OneToMany(mappedBy = "diagnosis", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.EAGER)
    private List<DiagnosisEvidenceEntity> evidenceList = new ArrayList<>();

    @OneToMany(mappedBy = "diagnosis", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.EAGER)
    private List<DiagnosisKnowledgeSourceEntity> knowledgeSources = new ArrayList<>();

    // --- Element Collections for string lists ---
    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "diagnosis_possible_causes", joinColumns = @JoinColumn(name = "diagnosis_record_id"))
    @Column(name = "cause", columnDefinition = "TEXT")
    private List<String> possibleCauses = new ArrayList<>();

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "diagnosis_recommended_checks", joinColumns = @JoinColumn(name = "diagnosis_record_id"))
    @Column(name = "check_item", columnDefinition = "TEXT")
    private List<String> recommendedChecks = new ArrayList<>();

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "diagnosis_additional_info", joinColumns = @JoinColumn(name = "diagnosis_record_id"))
    @Column(name = "info_item", columnDefinition = "TEXT")
    private List<String> additionalInformationRequired = new ArrayList<>();

    public DiagnosisEntity() {
    }

    @PrePersist
    public void prePersist() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }

    // Helper methods for child associations
    public void addAlternativeFault(DiagnosisAlternativeFaultEntity fault) {
        if (fault != null) {
            fault.setDiagnosis(this);
            this.alternativeFaults.add(fault);
        }
    }

    public void addEvidence(DiagnosisEvidenceEntity evidence) {
        if (evidence != null) {
            evidence.setDiagnosis(this);
            this.evidenceList.add(evidence);
        }
    }

    public void addKnowledgeSource(DiagnosisKnowledgeSourceEntity source) {
        if (source != null) {
            source.setDiagnosis(this);
            this.knowledgeSources.add(source);
        }
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getDiagnosisId() {
        return diagnosisId;
    }

    public void setDiagnosisId(String diagnosisId) {
        this.diagnosisId = diagnosisId;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public Double getLatencySeconds() {
        return latencySeconds;
    }

    public void setLatencySeconds(Double latencySeconds) {
        this.latencySeconds = latencySeconds;
    }

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public String getRawLlmResponse() {
        return rawLlmResponse;
    }

    public void setRawLlmResponse(String rawLlmResponse) {
        this.rawLlmResponse = rawLlmResponse;
    }

    public Double getTelemetryTemperature() {
        return telemetryTemperature;
    }

    public void setTelemetryTemperature(Double telemetryTemperature) {
        this.telemetryTemperature = telemetryTemperature;
    }

    public Double getTelemetryHumidity() {
        return telemetryHumidity;
    }

    public void setTelemetryHumidity(Double telemetryHumidity) {
        this.telemetryHumidity = telemetryHumidity;
    }

    public Double getTelemetryVibration() {
        return telemetryVibration;
    }

    public void setTelemetryVibration(Double telemetryVibration) {
        this.telemetryVibration = telemetryVibration;
    }

    public Double getTelemetryCurrent() {
        return telemetryCurrent;
    }

    public void setTelemetryCurrent(Double telemetryCurrent) {
        this.telemetryCurrent = telemetryCurrent;
    }

    public Double getTelemetryPressure() {
        return telemetryPressure;
    }

    public void setTelemetryPressure(Double telemetryPressure) {
        this.telemetryPressure = telemetryPressure;
    }

    public String getTelemetryRecordedAt() {
        return telemetryRecordedAt;
    }

    public void setTelemetryRecordedAt(String telemetryRecordedAt) {
        this.telemetryRecordedAt = telemetryRecordedAt;
    }

    public String getPrimaryFaultId() {
        return primaryFaultId;
    }

    public void setPrimaryFaultId(String primaryFaultId) {
        this.primaryFaultId = primaryFaultId;
    }

    public String getPrimaryFaultTitle() {
        return primaryFaultTitle;
    }

    public void setPrimaryFaultTitle(String primaryFaultTitle) {
        this.primaryFaultTitle = primaryFaultTitle;
    }

    public Double getPrimaryFaultSimilarity() {
        return primaryFaultSimilarity;
    }

    public void setPrimaryFaultSimilarity(Double primaryFaultSimilarity) {
        this.primaryFaultSimilarity = primaryFaultSimilarity;
    }

    public String getConfidenceLevel() {
        return confidenceLevel;
    }

    public void setConfidenceLevel(String confidenceLevel) {
        this.confidenceLevel = confidenceLevel;
    }

    public String getConfidenceReason() {
        return confidenceReason;
    }

    public void setConfidenceReason(String confidenceReason) {
        this.confidenceReason = confidenceReason;
    }

    public Long getGenTotalDuration() {
        return genTotalDuration;
    }

    public void setGenTotalDuration(Long genTotalDuration) {
        this.genTotalDuration = genTotalDuration;
    }

    public Integer getGenEvalCount() {
        return genEvalCount;
    }

    public void setGenEvalCount(Integer genEvalCount) {
        this.genEvalCount = genEvalCount;
    }

    public Long getGenEvalDuration() {
        return genEvalDuration;
    }

    public void setGenEvalDuration(Long genEvalDuration) {
        this.genEvalDuration = genEvalDuration;
    }

    public Integer getGenPromptEvalCount() {
        return genPromptEvalCount;
    }

    public void setGenPromptEvalCount(Integer genPromptEvalCount) {
        this.genPromptEvalCount = genPromptEvalCount;
    }

    public List<DiagnosisAlternativeFaultEntity> getAlternativeFaults() {
        return alternativeFaults;
    }

    public void setAlternativeFaults(List<DiagnosisAlternativeFaultEntity> alternativeFaults) {
        this.alternativeFaults = alternativeFaults != null ? alternativeFaults : new ArrayList<>();
    }

    public List<DiagnosisEvidenceEntity> getEvidenceList() {
        return evidenceList;
    }

    public void setEvidenceList(List<DiagnosisEvidenceEntity> evidenceList) {
        this.evidenceList = evidenceList != null ? evidenceList : new ArrayList<>();
    }

    public List<DiagnosisKnowledgeSourceEntity> getKnowledgeSources() {
        return knowledgeSources;
    }

    public void setKnowledgeSources(List<DiagnosisKnowledgeSourceEntity> knowledgeSources) {
        this.knowledgeSources = knowledgeSources != null ? knowledgeSources : new ArrayList<>();
    }

    public List<String> getPossibleCauses() {
        return possibleCauses;
    }

    public void setPossibleCauses(List<String> possibleCauses) {
        this.possibleCauses = possibleCauses != null ? possibleCauses : new ArrayList<>();
    }

    public List<String> getRecommendedChecks() {
        return recommendedChecks;
    }

    public void setRecommendedChecks(List<String> recommendedChecks) {
        this.recommendedChecks = recommendedChecks != null ? recommendedChecks : new ArrayList<>();
    }

    public List<String> getAdditionalInformationRequired() {
        return additionalInformationRequired;
    }

    public void setAdditionalInformationRequired(List<String> additionalInformationRequired) {
        this.additionalInformationRequired = additionalInformationRequired != null ? additionalInformationRequired : new ArrayList<>();
    }
}
