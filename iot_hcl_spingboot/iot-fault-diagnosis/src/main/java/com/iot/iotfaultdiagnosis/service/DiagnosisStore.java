package com.iot.iotfaultdiagnosis.service;

import com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse;

import java.util.List;
import java.util.Optional;

public interface DiagnosisStore {

    /**
     * Persist or update a diagnosis response.
     */
    void save(DiagnosisResponse diagnosis);

    /**
     * Retrieve the most recent diagnosis record.
     */
    Optional<DiagnosisResponse> getLatest();

    /**
     * Retrieve diagnosis by its unique diagnosis ID.
     */
    Optional<DiagnosisResponse> getById(String id);

    /**
     * Retrieve all diagnosis records for a given device ID ordered newest first.
     */
    List<DiagnosisResponse> getByDeviceId(String deviceId);

    /**
     * Retrieve all diagnosis records.
     */
    List<DiagnosisResponse> getAll();

    /**
     * Clear diagnosis records (useful for testing).
     */
    void clear();

    /**
     * Return the count of saved diagnosis records.
     */
    int size();
}
