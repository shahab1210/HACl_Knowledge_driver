package com.iot.iotfaultdiagnosis.controller;

import com.iot.iotfaultdiagnosis.dto.response.AlertResponse;
import com.iot.iotfaultdiagnosis.entity.AlertSeverity;
import com.iot.iotfaultdiagnosis.service.alert.AlertService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;
import java.util.List;

@RestController
@RequestMapping("/api/v1/alerts")
public class AlertController {

    private static final Logger log = LoggerFactory.getLogger(AlertController.class);

    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    @GetMapping
    public ResponseEntity<List<AlertResponse>> getAlerts(
            @RequestParam(required = false) String deviceId,
            @RequestParam(required = false) Boolean acknowledged,
            @RequestParam(required = false) AlertSeverity severity) {

        log.debug("REST request to fetch alerts - deviceId: {}, acknowledged: {}, severity: {}",
                deviceId, acknowledged, severity);
        List<AlertResponse> alerts = alertService.getAlerts(deviceId, acknowledged, severity);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/latest")
    public ResponseEntity<AlertResponse> getLatestAlert() {
        log.debug("REST request to fetch latest alert");
        return ResponseEntity.ok(alertService.getLatestAlert());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AlertResponse> getAlertById(@PathVariable Long id) {
        log.debug("REST request to fetch alert by id: {}", id);
        return ResponseEntity.ok(alertService.getAlertById(id));
    }

    @PostMapping("/{id}/acknowledge")
    public ResponseEntity<AlertResponse> acknowledgeAlert(
            @PathVariable Long id,
            Principal principal) {

        String operator = principal != null ? principal.getName() : "operator";
        log.info("REST request to acknowledge alert {} by {}", id, operator);
        AlertResponse response = alertService.acknowledgeAlert(id, operator);
        return ResponseEntity.ok(response);
    }
}
