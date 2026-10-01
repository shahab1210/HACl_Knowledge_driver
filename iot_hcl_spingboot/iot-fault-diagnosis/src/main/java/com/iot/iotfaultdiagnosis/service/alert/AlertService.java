package com.iot.iotfaultdiagnosis.service.alert;

import com.iot.iotfaultdiagnosis.dto.response.AlertResponse;
import com.iot.iotfaultdiagnosis.entity.AlertEntity;
import com.iot.iotfaultdiagnosis.entity.AlertSeverity;
import com.iot.iotfaultdiagnosis.exception.AlertNotFoundException;
import com.iot.iotfaultdiagnosis.repository.AlertRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class AlertService {

    private final AlertRepository alertRepository;

    public AlertService(AlertRepository alertRepository) {
        this.alertRepository = alertRepository;
    }

    public List<AlertResponse> getAlerts(String deviceId, Boolean acknowledged, AlertSeverity severity) {
        List<AlertEntity> entities;

        if (deviceId != null && !deviceId.isBlank()) {
            if (acknowledged != null) {
                entities = alertRepository.findByDeviceIdAndAcknowledgedOrderByCreatedAtDesc(deviceId, acknowledged);
            } else {
                entities = alertRepository.findByDeviceIdOrderByCreatedAtDesc(deviceId);
            }
        } else if (acknowledged != null) {
            entities = alertRepository.findByAcknowledgedOrderByCreatedAtDesc(acknowledged);
        } else if (severity != null) {
            entities = alertRepository.findBySeverityOrderByCreatedAtDesc(severity);
        } else {
            entities = alertRepository.findAllByOrderByCreatedAtDesc();
        }

        return entities.stream().map(AlertResponse::new).collect(Collectors.toList());
    }

    public AlertResponse getLatestAlert() {
        return alertRepository.findTopByOrderByCreatedAtDesc()
                .map(AlertResponse::new)
                .orElseThrow(() -> new AlertNotFoundException("No alerts found"));
    }

    public AlertResponse getAlertById(Long id) {
        return alertRepository.findById(id)
                .map(AlertResponse::new)
                .orElseThrow(() -> new AlertNotFoundException(id));
    }

    @Transactional
    public AlertResponse acknowledgeAlert(Long id, String acknowledgedBy) {
        AlertEntity alert = alertRepository.findById(id)
                .orElseThrow(() -> new AlertNotFoundException(id));

        alert.setAcknowledged(true);
        alert.setAcknowledgedAt(LocalDateTime.now());
        alert.setAcknowledgedBy(acknowledgedBy != null ? acknowledgedBy : "anonymous");

        AlertEntity updated = alertRepository.save(alert);
        return new AlertResponse(updated);
    }
}
