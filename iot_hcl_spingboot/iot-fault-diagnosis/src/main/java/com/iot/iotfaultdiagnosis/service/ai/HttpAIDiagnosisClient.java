package com.iot.iotfaultdiagnosis.service.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.*;
import com.iot.iotfaultdiagnosis.exception.DiagnosisServiceUnavailableException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Component
public class HttpAIDiagnosisClient implements AIDiagnosisClient {

    private static final Logger log = LoggerFactory.getLogger(HttpAIDiagnosisClient.class);

    private final RestClient aiRestClient;
    private final ObjectMapper objectMapper;

    public HttpAIDiagnosisClient(RestClient aiRestClient, ObjectMapper objectMapper) {
        this.aiRestClient = aiRestClient;
        this.objectMapper = objectMapper;
    }

    @Override
    public DiagnosisResponse diagnose(TelemetryRequest request) {
        log.info("Sending telemetry diagnosis request for device: {}", request.getDeviceId());

        String rawJson;
        try {
            String requestJson = objectMapper.writeValueAsString(request);
            rawJson = aiRestClient.post()
                    .uri("/api/v1/diagnose")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(requestJson)
                    .retrieve()
                    .body(String.class);
        } catch (RestClientException e) {
            log.error("Failed to connect to AI diagnosis bridge: {}", e.getMessage());
            throw new DiagnosisServiceUnavailableException(
                    "AI Diagnosis Service is currently unreachable at http://localhost:5001. Ensure the P13 AI bridge is running.",
                    e
            );
        } catch (Exception e) {
            log.error("Unexpected error during AI diagnosis communication: {}", e.getMessage(), e);
            throw new DiagnosisServiceUnavailableException("Error communicating with AI diagnosis engine: " + e.getMessage(), e);
        }

        if (rawJson == null || rawJson.trim().isEmpty()) {
            throw new DiagnosisServiceUnavailableException("AI diagnosis service returned empty response");
        }

        return parseDiagnosisJson(rawJson, request);
    }

    public DiagnosisResponse parseDiagnosisJson(String json, TelemetryRequest requestFallback) {
        try {
            JsonNode root = objectMapper.readTree(json);

            String deviceId = root.path("device_id").asText(
                    requestFallback != null ? requestFallback.getDeviceId() : "UNKNOWN"
            );
            String topic = root.path("topic").asText("iot/" + deviceId + "/telemetry");

            // Latency
            JsonNode latencyNode = root.path("latency");
            Double latencySeconds = getDoubleValue(latencyNode, "total_latency_seconds", null);

            // Telemetry Node
            JsonNode telNode = root.path("telemetry");
            Double temp = getDoubleValue(telNode, "temperature", requestFallback != null ? requestFallback.getTemperature() : null);
            Double hum = getDoubleValue(telNode, "humidity", requestFallback != null ? requestFallback.getHumidity() : null);
            Double vib = getDoubleValue(telNode, "vibration", requestFallback != null ? requestFallback.getVibration() : null);
            Double curr = getDoubleValue(telNode, "current", requestFallback != null ? requestFallback.getCurrent() : null);
            Double press = getDoubleValue(telNode, "pressure", requestFallback != null ? requestFallback.getPressure() : null);
            String recAt = telNode.has("recorded_at") ? telNode.path("recorded_at").asText() : LocalDateTime.now().toString();

            TelemetryResponse telResp = new TelemetryResponse(
                    deviceId,
                    temp,
                    hum,
                    vib,
                    curr,
                    press,
                    recAt
            );

            // Diagnosis Node
            JsonNode diagNode = root.path("diagnosis");
            DiagnosisDetailResponse diagDetail = new DiagnosisDetailResponse();
            diagDetail.setQuery(diagNode.path("query").asText(""));
            diagDetail.setModel(diagNode.path("model").asText("qwen2.5:1.5b"));
            diagDetail.setRawLlmResponse(diagNode.path("raw_llm_response").asText(""));

            // Primary Fault
            JsonNode primaryNode = diagNode.path("primary_fault");
            if (!primaryNode.isMissingNode() && !primaryNode.isNull()) {
                FaultResponse primaryFault = new FaultResponse(
                        primaryNode.has("fault_id") && !primaryNode.path("fault_id").isNull() ? primaryNode.path("fault_id").asText() : null,
                        primaryNode.has("title") && !primaryNode.path("title").isNull() ? primaryNode.path("title").asText() : null,
                        getDoubleValue(primaryNode, "similarity", null)
                );
                diagDetail.setPrimaryFault(primaryFault);
            }

            // Alternative Faults
            JsonNode altNodes = diagNode.path("alternative_faults");
            if (altNodes.isArray()) {
                List<FaultResponse> altList = new ArrayList<>();
                for (JsonNode an : altNodes) {
                    altList.add(new FaultResponse(
                            an.has("fault_id") && !an.path("fault_id").isNull() ? an.path("fault_id").asText() : null,
                            an.has("title") && !an.path("title").isNull() ? an.path("title").asText() : null,
                            getDoubleValue(an, "similarity", null)
                    ));
                }
                diagDetail.setAlternativeFaults(altList);
            }

            // Confidence
            JsonNode confNode = diagNode.path("confidence");
            if (!confNode.isMissingNode() && !confNode.isNull()) {
                diagDetail.setConfidence(new ConfidenceResponse(
                        confNode.path("level").asText("medium"),
                        confNode.path("reason").asText("")
                ));
            }

            // Evidence
            JsonNode evNodes = diagNode.path("evidence");
            if (evNodes.isArray()) {
                List<EvidenceResponse> evList = new ArrayList<>();
                for (JsonNode ev : evNodes) {
                    evList.add(new EvidenceResponse(
                            ev.path("type").asText("telemetry"),
                            ev.path("parameter").asText(""),
                            getDoubleValue(ev, "value", null),
                            ev.path("unit").asText(""),
                            ev.has("status") && !ev.path("status").isNull() ? ev.path("status").asText() : null
                    ));
                }
                diagDetail.setEvidence(evList);
            }

            // Possible Causes
            JsonNode causesNode = diagNode.path("possible_causes");
            if (causesNode.isArray()) {
                List<String> causes = new ArrayList<>();
                for (JsonNode c : causesNode) {
                    causes.add(c.asText());
                }
                diagDetail.setPossibleCauses(causes);
            }

            // Recommended Checks
            JsonNode checksNode = diagNode.path("recommended_checks");
            if (checksNode.isArray()) {
                List<String> checks = new ArrayList<>();
                for (JsonNode ch : checksNode) {
                    checks.add(ch.asText());
                }
                diagDetail.setRecommendedChecks(checks);
            }

            // Additional Info Required
            JsonNode addInfoNode = diagNode.path("additional_information_required");
            if (addInfoNode.isArray()) {
                List<String> addInfo = new ArrayList<>();
                for (JsonNode ai : addInfoNode) {
                    addInfo.add(ai.asText());
                }
                diagDetail.setAdditionalInformationRequired(addInfo);
            }

            // Knowledge Sources
            JsonNode ksNodes = diagNode.path("knowledge_sources");
            if (ksNodes.isArray()) {
                List<KnowledgeSourceResponse> ksList = new ArrayList<>();
                for (JsonNode ks : ksNodes) {
                    ksList.add(new KnowledgeSourceResponse(
                            ks.path("rank").asInt(1),
                            ks.path("document_id").asText(""),
                            ks.path("chunk_id").asText(""),
                            ks.path("title").asText(""),
                            ks.path("source").asText(""),
                            getDoubleValue(ks, "similarity", null)
                    ));
                }
                diagDetail.setKnowledgeSources(ksList);
            }

            // Generation Details
            JsonNode genNode = diagNode.path("generation_details");
            if (!genNode.isMissingNode() && !genNode.isNull()) {
                Long totalDur = genNode.has("total_duration") && !genNode.path("total_duration").isNull() ? genNode.path("total_duration").asLong() : null;
                Integer evalCnt = genNode.has("eval_count") && !genNode.path("eval_count").isNull() ? genNode.path("eval_count").asInt() : null;
                Long evalDur = genNode.has("eval_duration") && !genNode.path("eval_duration").isNull() ? genNode.path("eval_duration").asLong() : null;
                Integer promptEvalCnt = genNode.has("prompt_eval_count") && !genNode.path("prompt_eval_count").isNull() ? genNode.path("prompt_eval_count").asInt() : null;
                diagDetail.setGenerationDetails(new GenerationDetailsResponse(
                        totalDur,
                        evalCnt,
                        evalDur,
                        promptEvalCnt
                ));
            }

            String id = "diag-" + deviceId + "-" + System.currentTimeMillis();
            return new DiagnosisResponse(
                    id,
                    deviceId,
                    topic,
                    LocalDateTime.now(),
                    telResp,
                    diagDetail,
                    latencySeconds
            );

        } catch (Exception e) {
            log.error("Failed to parse diagnosis JSON: {}", e.getMessage(), e);
            throw new DiagnosisServiceUnavailableException("Malformed response from AI diagnosis engine: " + e.getMessage(), e);
        }
    }

    private Double getDoubleValue(JsonNode parent, String fieldName, Double fallback) {
        if (parent != null && parent.has(fieldName) && !parent.path(fieldName).isNull()) {
            return parent.path(fieldName).asDouble();
        }
        return fallback;
    }
}
