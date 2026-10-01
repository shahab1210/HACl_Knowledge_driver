package com.iot.iotfaultdiagnosis.repository;

import com.iot.iotfaultdiagnosis.entity.DiagnosisEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DiagnosisRepository extends JpaRepository<DiagnosisEntity, Long> {

    Optional<DiagnosisEntity> findByDiagnosisId(String diagnosisId);

    Optional<DiagnosisEntity> findTopByOrderByCreatedAtDesc();

    List<DiagnosisEntity> findByDeviceIdOrderByCreatedAtDesc(String deviceId);

    Optional<DiagnosisEntity> findTopByDeviceIdOrderByCreatedAtDesc(String deviceId);

    boolean existsByDiagnosisId(String diagnosisId);

    void deleteByDiagnosisId(String diagnosisId);
}
