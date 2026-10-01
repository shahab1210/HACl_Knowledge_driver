package com.iot.iotfaultdiagnosis.service;

import com.iot.iotfaultdiagnosis.dto.response.DiagnosisResponse;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicReference;

/**
 * In-memory thread-safe storage for diagnosis results.
 * Retained for lightweight testing and development; production uses PostgresDiagnosisStore.
 */
@Component
public class InMemoryDiagnosisStore implements DiagnosisStore {

    private final Map<String, DiagnosisResponse> byId = new ConcurrentHashMap<>();
    private final Map<String, List<DiagnosisResponse>> byDeviceId = new ConcurrentHashMap<>();
    private final AtomicReference<DiagnosisResponse> latest = new AtomicReference<>();
    private final List<DiagnosisResponse> allDiagnoses = new CopyOnWriteArrayList<>();

    @Override
    public void save(DiagnosisResponse diagnosis) {
        if (diagnosis == null || diagnosis.getId() == null) {
            return;
        }

        byId.put(diagnosis.getId(), diagnosis);
        latest.set(diagnosis);
        allDiagnoses.add(0, diagnosis); // newest first

        if (diagnosis.getDeviceId() != null) {
            byDeviceId.computeIfAbsent(diagnosis.getDeviceId(), k -> new CopyOnWriteArrayList<>())
                    .add(0, diagnosis);
        }
    }

    @Override
    public Optional<DiagnosisResponse> getLatest() {
        return Optional.ofNullable(latest.get());
    }

    @Override
    public Optional<DiagnosisResponse> getById(String id) {
        if (id == null) {
            return Optional.empty();
        }
        return Optional.ofNullable(byId.get(id));
    }

    @Override
    public List<DiagnosisResponse> getByDeviceId(String deviceId) {
        if (deviceId == null) {
            return Collections.emptyList();
        }
        List<DiagnosisResponse> list = byDeviceId.get(deviceId);
        return list != null ? Collections.unmodifiableList(list) : Collections.emptyList();
    }

    @Override
    public List<DiagnosisResponse> getAll() {
        return Collections.unmodifiableList(allDiagnoses);
    }

    @Override
    public void clear() {
        byId.clear();
        byDeviceId.clear();
        latest.set(null);
        allDiagnoses.clear();
    }

    @Override
    public int size() {
        return byId.size();
    }
}
