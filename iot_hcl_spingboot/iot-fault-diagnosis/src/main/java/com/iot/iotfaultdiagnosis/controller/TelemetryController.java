package com.iot.iotfaultdiagnosis.controller;

import com.iot.iotfaultdiagnosis.dto.response.TelemetryResponse;
import com.iot.iotfaultdiagnosis.service.telemetry.TelemetryService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/telemetry")
public class TelemetryController {

    private static final Logger log = LoggerFactory.getLogger(TelemetryController.class);

    private final TelemetryService telemetryService;

    public TelemetryController(TelemetryService telemetryService) {
        this.telemetryService = telemetryService;
    }

    /**
     * Retrieve the most recent raw sensor telemetry reading from PostgreSQL.
     * Optionally filtered by deviceId (e.g. ESP32_001).
     */
    @GetMapping("/latest")
    public ResponseEntity<TelemetryResponse> getLatestTelemetry(@RequestParam(required = false) String deviceId) {
        log.debug("REST request to fetch latest raw telemetry for device: {}", deviceId);
        TelemetryResponse response = telemetryService.getLatestTelemetry(deviceId);
        return ResponseEntity.ok(response);
    }

    /**
     * Retrieve recent raw sensor telemetry readings in chronological order for charting.
     * Default limit: 20 (max: 100).
     */
    @GetMapping("/history")
    public ResponseEntity<List<TelemetryResponse>> getTelemetryHistory(
            @RequestParam(required = false) String deviceId,
            @RequestParam(required = false, defaultValue = "20") Integer limit) {
        log.debug("REST request to fetch raw telemetry history for device: {}, limit: {}", deviceId, limit);
        List<TelemetryResponse> response = telemetryService.getTelemetryHistory(deviceId, limit);
        return ResponseEntity.ok(response);
    }
}
