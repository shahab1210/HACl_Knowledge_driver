package com.iot.iotfaultdiagnosis.service.ai;

import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse;

public interface AIDiagnosisClient {

    /**
     * Sends telemetry to the AI diagnosis bridge and retrieves the structured diagnosis.
     *
     * @param request Validated telemetry request
     * @return Structured diagnosis response
     */
    DiagnosisResponse diagnose(TelemetryRequest request);

    /**
     * Parses raw diagnosis JSON into a standardized DiagnosisResponse.
     *
     * @param json Raw JSON string
     * @param requestFallback Optional fallback telemetry request
     * @return Standardized DiagnosisResponse
     */
    DiagnosisResponse parseDiagnosisJson(String json, TelemetryRequest requestFallback);
}
