package com.iot.iotfaultdiagnosis.repository;

import com.iot.iotfaultdiagnosis.entity.SensorReading;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SensorReadingRepository extends JpaRepository<SensorReading, Long> {

    Optional<SensorReading> findFirstByDeviceIdOrderByRecordedAtDescIdDesc(String deviceId);

    Optional<SensorReading> findFirstByOrderByRecordedAtDescIdDesc();

    List<SensorReading> findByDeviceIdOrderByRecordedAtDescIdDesc(String deviceId, Pageable pageable);

    List<SensorReading> findByOrderByRecordedAtDescIdDesc(Pageable pageable);
}