package com.iot.iotfaultdiagnosis.service.notification;

import com.iot.iotfaultdiagnosis.entity.AlertEntity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Local operational notification service for industrial alerts.
 * Operates local delivery channels:
 * 1. High-priority structured industrial console & file logging
 * 2. In-memory notification event log for real-time operator queries
 * 3. Extensible integration point for local MQTT / webhook dispatch
 */
@Service
public class LocalNotificationService implements NotificationService {

    private static final Logger log = LoggerFactory.getLogger(LocalNotificationService.class);

    private final List<AlertEntity> notificationHistory = new CopyOnWriteArrayList<>();

    @Override
    public void sendNotification(AlertEntity alert) {
        if (alert == null) {
            return;
        }

        notificationHistory.add(alert);
        if (notificationHistory.size() > 500) {
            notificationHistory.remove(0);
        }

        switch (alert.getSeverity()) {
            case CRITICAL -> log.error(
                    "🚨 [CRITICAL ALERT DISPATCHED] Device: {} | Type: {} | Parameter: {}={}{} | Message: {}",
                    alert.getDeviceId(),
                    alert.getAlertType(),
                    alert.getSensorParameter() != null ? alert.getSensorParameter() : "N/A",
                    alert.getSensorValue() != null ? alert.getSensorValue() : 0.0,
                    alert.getThresholdValue() != null ? " (Limit: " + alert.getThresholdValue() + ")" : "",
                    alert.getMessage()
            );
            case WARNING -> log.warn(
                    "⚠️ [WARNING ALERT DISPATCHED] Device: {} | Type: {} | Parameter: {}={}{} | Message: {}",
                    alert.getDeviceId(),
                    alert.getAlertType(),
                    alert.getSensorParameter() != null ? alert.getSensorParameter() : "N/A",
                    alert.getSensorValue() != null ? alert.getSensorValue() : 0.0,
                    alert.getThresholdValue() != null ? " (Limit: " + alert.getThresholdValue() + ")" : "",
                    alert.getMessage()
            );
            case INFO -> log.info(
                    "ℹ️ [INFO ALERT DISPATCHED] Device: {} | Type: {} | Message: {}",
                    alert.getDeviceId(),
                    alert.getAlertType(),
                    alert.getMessage()
            );
        }
    }

    public List<AlertEntity> getNotificationHistory() {
        return Collections.unmodifiableList(new ArrayList<>(notificationHistory));
    }

    public void clearHistory() {
        notificationHistory.clear();
    }
}
