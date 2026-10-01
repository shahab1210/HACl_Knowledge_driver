package com.iot.iotfaultdiagnosis.controller;

import com.iot.iotfaultdiagnosis.dto.request.TelemetryRequest;
import com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse;
import com.iot.iotfaultdiagnosis.service.DiagnosisService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/diagnosis")
public class DiagnosisController {

    private final DiagnosisService diagnosisService;

    public DiagnosisController(DiagnosisService diagnosisService) {
        this.diagnosisService = diagnosisService;
    }

    /**
     * Retrieve the most recent fault diagnosis across all devices.
     */
    @GetMapping("/latest")
    public ResponseEntity<DiagnosisResponse> getLatestDiagnosis() {
        DiagnosisResponse latest = diagnosisService.getLatestDiagnosis();
        return ResponseEntity.ok(latest);
    }

    /**
     * Retrieve a specific diagnosis by its unique diagnosis ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<DiagnosisResponse> getDiagnosisById(@PathVariable("id") String id) {
        DiagnosisResponse diagnosis = diagnosisService.getDiagnosisById(id);
        return ResponseEntity.ok(diagnosis);
    }

    /**
     * Retrieve all diagnosis records for a specific IoT device.
     */
    @GetMapping("/device/{deviceId}")
    public ResponseEntity<List<DiagnosisResponse>> getDiagnosesByDeviceId(@PathVariable("deviceId") String deviceId) {
        List<DiagnosisResponse> diagnoses = diagnosisService.getDiagnosesByDeviceId(deviceId);
        return ResponseEntity.ok(diagnoses);
    }

    /**
     * Submit raw IoT sensor telemetry to trigger an on-demand AI fault diagnosis.
     */
    @PostMapping
    public ResponseEntity<DiagnosisResponse> triggerDiagnosis(@Valid @RequestBody TelemetryRequest request) {
        DiagnosisResponse diagnosis = diagnosisService.triggerDiagnosis(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(diagnosis);
    }
}
