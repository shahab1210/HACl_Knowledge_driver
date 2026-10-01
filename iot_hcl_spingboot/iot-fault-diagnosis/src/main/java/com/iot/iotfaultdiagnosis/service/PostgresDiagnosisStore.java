package com.iot.iotfaultdiagnosis.service;

import com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse;
import com.iot.iotfaultdiagnosis.entity.DiagnosisEntity;
import com.iot.iotfaultdiagnosis.mapper.DiagnosisMapper;
import com.iot.iotfaultdiagnosis.repository.DiagnosisRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

/**
 * Production PostgreSQL-backed persistent storage for P15 diagnosis results.
 */
@Service
@Primary
public class PostgresDiagnosisStore implements DiagnosisStore {

    private static final Logger log = LoggerFactory.getLogger(PostgresDiagnosisStore.class);

    private final DiagnosisRepository diagnosisRepository;
    private final DiagnosisMapper mapper;

    public PostgresDiagnosisStore(DiagnosisRepository diagnosisRepository, DiagnosisMapper mapper) {
        this.diagnosisRepository = diagnosisRepository;
        this.mapper = mapper;
    }

    @Override
    @Transactional
    public void save(DiagnosisResponse diagnosis) {
        if (diagnosis == null || diagnosis.getId() == null) {
            log.warn("Attempted to persist null diagnosis or diagnosis with null ID");
            return;
        }

        try {
            // If already exists, delete previous and flush to prevent unique constraint violation
            Optional<DiagnosisEntity> existing = diagnosisRepository.findByDiagnosisId(diagnosis.getId());
            if (existing.isPresent()) {
                diagnosisRepository.delete(existing.get());
                diagnosisRepository.flush();
            }

            DiagnosisEntity entity = mapper.toEntity(diagnosis);
            diagnosisRepository.save(entity);
            log.debug("Persisted diagnosis record to PostgreSQL: {}", diagnosis.getId());
        } catch (Exception e) {
            log.error("Failed to persist diagnosis record {} to PostgreSQL: {}", diagnosis.getId(), e.getMessage(), e);
            throw e;
        }
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<DiagnosisResponse> getLatest() {
        return diagnosisRepository.findTopByOrderByCreatedAtDesc()
                .map(mapper::toDto);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<DiagnosisResponse> getById(String id) {
        if (id == null || id.trim().isEmpty()) {
            return Optional.empty();
        }
        return diagnosisRepository.findByDiagnosisId(id.trim())
                .map(mapper::toDto);
    }

    @Override
    @Transactional(readOnly = true)
    public List<DiagnosisResponse> getByDeviceId(String deviceId) {
        if (deviceId == null || deviceId.trim().isEmpty()) {
            return Collections.emptyList();
        }
        return diagnosisRepository.findByDeviceIdOrderByCreatedAtDesc(deviceId.trim())
                .stream()
                .map(mapper::toDto)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<DiagnosisResponse> getAll() {
        return diagnosisRepository.findAll()
                .stream()
                .map(mapper::toDto)
                .toList();
    }

    @Override
    @Transactional
    public void clear() {
        diagnosisRepository.deleteAll();
    }

    @Override
    @Transactional(readOnly = true)
    public int size() {
        return (int) diagnosisRepository.count();
    }
}
