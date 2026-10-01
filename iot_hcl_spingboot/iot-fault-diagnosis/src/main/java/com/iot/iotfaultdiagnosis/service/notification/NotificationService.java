package com.iot.iotfaultdiagnosis.service.notification;

import com.iot.iotfaultdiagnosis.entity.AlertEntity;

public interface NotificationService {

    /**
     * Dispatch an alert notification across active local notification channels.
     * @param alert the triggered and persisted AlertEntity
     */
    void sendNotification(AlertEntity alert);
}
