package com.iot.iotfaultdiagnosis.service.telemetry;

import com.iot.iotfaultdiagnosis.dto.response.TelemetryResponse;
import com.iot.iotfaultdiagnosis.entity.SensorReading;
import com.iot.iotfaultdiagnosis.exception.TelemetryNotFoundException;
import com.iot.iotfaultdiagnosis.repository.SensorReadingRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class TelemetryService {

    private static final Logger log = LoggerFactory.getLogger(TelemetryService.class);
    private static final int DEFAULT_LIMIT = 20;
    private static final int MAX_LIMIT = 100;
    private static final DateTimeFormatter ISO_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    private final SensorReadingRepository sensorReadingRepository;

    public TelemetryService(SensorReadingRepository sensorReadingRepository) {
        this.sensorReadingRepository = sensorReadingRepository;
    }

    public TelemetryResponse getLatestTelemetry(String deviceId) {
        log.debug("Fetching latest telemetry reading for deviceId: {}", deviceId);

        SensorReading reading;
        if (deviceId != null && !deviceId.trim().isEmpty() && !deviceId.equalsIgnoreCase("All")) {
            reading = sensorReadingRepository.findFirstByDeviceIdOrderByRecordedAtDescIdDesc(deviceId.trim())
                    .orElseThrow(() -> new TelemetryNotFoundException("No telemetry readings found for device: " + deviceId));
        } else {
            reading = sensorReadingRepository.findFirstByOrderByRecordedAtDescIdDesc()
                    .orElseThrow(() -> new TelemetryNotFoundException("No telemetry readings found in database"));
        }

        return mapToResponse(reading);
    }

    public List<TelemetryResponse> getTelemetryHistory(String deviceId, Integer limit) {
        int effectiveLimit = (limit == null || limit <= 0) ? DEFAULT_LIMIT : Math.min(limit, MAX_LIMIT);
        log.debug("Fetching telemetry history for deviceId: {}, limit: {}", deviceId, effectiveLimit);

        List<SensorReading> readings;
        PageRequest pageRequest = PageRequest.of(0, effectiveLimit);

        if (deviceId != null && !deviceId.trim().isEmpty() && !deviceId.equalsIgnoreCase("All")) {
            readings = sensorReadingRepository.findByDeviceIdOrderByRecordedAtDescIdDesc(deviceId.trim(), pageRequest);
        } else {
            readings = sensorReadingRepository.findByOrderByRecordedAtDescIdDesc(pageRequest);
        }

        if (readings.isEmpty()) {
            return Collections.emptyList();
        }

        // Create mutable copy to reverse from newest-first (DB) to chronological oldest-first (for charts)
        List<SensorReading> chronological = new ArrayList<>(readings);
        Collections.reverse(chronological);

        return chronological.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private TelemetryResponse mapToResponse(SensorReading reading) {
        String formattedTime = reading.getRecordedAt() != null
                ? reading.getRecordedAt().format(ISO_FORMATTER)
                : null;

        return new TelemetryResponse(
                reading.getDeviceId(),
                reading.getTemperature(),
                reading.getHumidity(),
                reading.getVibration(),
                reading.getCurrentValue(),
                reading.getPressure(),
                formattedTime
        );
    }
}
