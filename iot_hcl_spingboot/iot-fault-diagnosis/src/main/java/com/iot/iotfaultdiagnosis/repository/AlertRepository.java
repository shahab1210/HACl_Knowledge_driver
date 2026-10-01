package com.iot.iotfaultdiagnosis.repository;

import com.iot.iotfaultdiagnosis.entity.AlertEntity;
import com.iot.iotfaultdiagnosis.entity.AlertSeverity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AlertRepository extends JpaRepository<AlertEntity, Long> {

    List<AlertEntity> findAllByOrderByCreatedAtDesc();

    List<AlertEntity> findByAcknowledgedOrderByCreatedAtDesc(boolean acknowledged);

    List<AlertEntity> findByDeviceIdOrderByCreatedAtDesc(String deviceId);

    List<AlertEntity> findByDeviceIdAndAcknowledgedOrderByCreatedAtDesc(String deviceId, boolean acknowledged);

    List<AlertEntity> findBySeverityOrderByCreatedAtDesc(AlertSeverity severity);

    Optional<AlertEntity> findTopByOrderByCreatedAtDesc();

    List<AlertEntity> findTop20ByOrderByCreatedAtDesc();

    List<AlertEntity> findTop20ByAcknowledgedOrderByCreatedAtDesc(boolean acknowledged);

    long countByAcknowledgedFalse();
}
