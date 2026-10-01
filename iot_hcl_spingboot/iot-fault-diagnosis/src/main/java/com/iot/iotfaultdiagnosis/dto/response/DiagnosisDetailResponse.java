package com.iot.iotfaultdiagnosis.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.ArrayList;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class DiagnosisDetailResponse {

    private String query;
    private FaultResponse primaryFault;
    private List<FaultResponse> alternativeFaults = new ArrayList<>();
    private ConfidenceResponse confidence;
    private List<EvidenceResponse> evidence = new ArrayList<>();
    private List<String> possibleCauses = new ArrayList<>();
    private List<String> recommendedChecks = new ArrayList<>();
    private List<String> additionalInformationRequired = new ArrayList<>();
    private List<KnowledgeSourceResponse> knowledgeSources = new ArrayList<>();
    private String rawLlmResponse;
    private String model;
    private GenerationDetailsResponse generationDetails;

    public DiagnosisDetailResponse() {
    }

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public FaultResponse getPrimaryFault() {
        return primaryFault;
    }

    public void setPrimaryFault(FaultResponse primaryFault) {
        this.primaryFault = primaryFault;
    }

    public List<FaultResponse> getAlternativeFaults() {
        return alternativeFaults;
    }

    public void setAlternativeFaults(List<FaultResponse> alternativeFaults) {
        this.alternativeFaults = alternativeFaults != null ? alternativeFaults : new ArrayList<>();
    }

    public ConfidenceResponse getConfidence() {
        return confidence;
    }

    public void setConfidence(ConfidenceResponse confidence) {
        this.confidence = confidence;
    }

    public List<EvidenceResponse> getEvidence() {
        return evidence;
    }

    public void setEvidence(List<EvidenceResponse> evidence) {
        this.evidence = evidence != null ? evidence : new ArrayList<>();
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

    public List<KnowledgeSourceResponse> getKnowledgeSources() {
        return knowledgeSources;
    }

    public void setKnowledgeSources(List<KnowledgeSourceResponse> knowledgeSources) {
        this.knowledgeSources = knowledgeSources != null ? knowledgeSources : new ArrayList<>();
    }

    public String getRawLlmResponse() {
        return rawLlmResponse;
    }

    public void setRawLlmResponse(String rawLlmResponse) {
        this.rawLlmResponse = rawLlmResponse;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public GenerationDetailsResponse getGenerationDetails() {
        return generationDetails;
    }

    public void setGenerationDetails(GenerationDetailsResponse generationDetails) {
        this.generationDetails = generationDetails;
    }
}
