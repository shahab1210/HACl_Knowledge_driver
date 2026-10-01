# P_311 — Live Telemetry Refresh Implementation Report

---

## 1. Executive Summary

This report documents the resolution of the telemetry freshness disparity between Grafana and the React frontend in the **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant**. 

Prior to this fix, the Grafana dashboard updated telemetry every 10 seconds directly from PostgreSQL's `sensor_readings` table, while the React frontend displayed telemetry extracted solely from stored AI diagnosis records in the `diagnoses` table. Because AI diagnoses take ~45–60 seconds per evaluation, React appeared frozen while Grafana was updating live.

The resolution implements a **decoupled telemetry path**: high-frequency live MQTT sensor readings in `sensor_readings` are now exposed via lightweight, dedicated Spring Boot REST endpoints (`/api/v1/telemetry/**`) and consumed every 10 seconds by the React dashboard without triggering any AI inference.

---

## 2. Root Cause Analysis & Architectural Decoupling

| Area | Before Fix (Defect) | After Fix (Resolved) |
|---|---|---|
| **Data Source** | React consumed `GET /api/v1/diagnosis/latest` which returns historical snapshots from `diagnoses`. | React consumes `GET /api/v1/telemetry/latest` and `GET /api/v1/telemetry/history` backed by `sensor_readings`. |
| **Pipeline Coupling** | Telemetry visualization was tightly bound to AI diagnosis execution. | Telemetry visualization is decoupled from AI diagnosis. Raw telemetry streams independently. |
| **Backend REST APIs** | No REST endpoint existed in Spring Boot to query raw `sensor_readings`. | Added `TelemetryController` with endpoints `/latest` and `/history`. |
| **Latency** | 45–60 seconds (or static if no new diagnosis ran). | Real-time (10-second polling interval matching Grafana). |
| **Lineage & Traceability** | Unclear distinction between raw sensor stream and diagnosis input snapshot. | Distinct visual indicators (`LIVE STREAM` vs `DIAGNOSIS SNAPSHOT`) and toggleable trend charts. |

---

## 3. Backend Implementation Details

### A. Endpoints Created
All endpoints reside under `/api/v1/telemetry` and require a valid JWT Bearer token:

1. **`GET /api/v1/telemetry/latest?deviceId={deviceId}`**
   - **Query Parameters**: `deviceId` (optional string). If omitted, returns latest reading across all devices.
   - **Response Status**: `200 OK` on success, `404 NOT_FOUND` if no readings exist, `401 UNAUTHORIZED` if unauthenticated.
   - **Payload Contract**:
     ```json
     {
       "deviceId": "ESP32_001",
       "temperature": 31.4,
       "humidity": 55.5,
       "vibration": 1.8,
       "current": 5.6,
       "pressure": 2.7,
       "recordedAt": "2026-10-01T13:47:22.037913"
     }
     ```

2. **`GET /api/v1/telemetry/history?deviceId={deviceId}&limit={limit}`**
   - **Query Parameters**:
     - `deviceId` (optional string): Filters readings by device ID.
     - `limit` (optional integer, default `20`, clamped `1..100`): Maximum data points to return.
   - **Response Contract**: Returns array of `TelemetryResponse` objects sorted **chronologically (oldest first, newest last)** for direct time-series visualization.

### B. Modified Backend Files
- [`SensorReadingRepository.java`](file:///Users/shahabahmad/Documents/P_311/iot_hcl_spingboot/iot-fault-diagnosis/src/main/java/com/iot/iotfaultdiagnosis/repository/SensorReadingRepository.java): Added `findFirstByDeviceIdOrderByRecordedAtDescIdDesc`, `findFirstByOrderByRecordedAtDescIdDesc`, `findByDeviceIdOrderByRecordedAtDescIdDesc(Pageable)`, and `findByOrderByRecordedAtDescIdDesc(Pageable)`.
- [`TelemetryNotFoundException.java`](file:///Users/shahabahmad/Documents/P_311/iot_hcl_spingboot/iot-fault-diagnosis/src/main/java/com/iot/iotfaultdiagnosis/exception/TelemetryNotFoundException.java): Custom runtime exception mapped to HTTP 404.
- [`GlobalExceptionHandler.java`](file:///Users/shahabahmad/Documents/P_311/iot_hcl_spingboot/iot-fault-diagnosis/src/main/java/com/iot/iotfaultdiagnosis/exception/GlobalExceptionHandler.java): Added `@ExceptionHandler(TelemetryNotFoundException.class)`.
- [`TelemetryService.java`](file:///Users/shahabahmad/Documents/P_311/iot_hcl_spingboot/iot-fault-diagnosis/src/main/java/com/iot/iotfaultdiagnosis/service/TelemetryService.java): Service layer for retrieval, clamping, mapping entity `currentValue` to DTO `current`, and chronological ordering.
- [`TelemetryController.java`](file:///Users/shahabahmad/Documents/P_311/iot_hcl_spingboot/iot-fault-diagnosis/src/main/java/com/iot/iotfaultdiagnosis/controller/TelemetryController.java): REST controller implementing endpoints.
- [`SecurityConfig.java`](file:///Users/shahabahmad/Documents/P_311/iot_hcl_spingboot/iot-fault-diagnosis/src/main/java/com/iot/iotfaultdiagnosis/config/SecurityConfig.java): Protected `/api/v1/telemetry/**` behind authentication.
- [`TelemetryControllerTest.java`](file:///Users/shahabahmad/Documents/P_311/iot_hcl_spingboot/iot-fault-diagnosis/src/test/java/com/iot/iotfaultdiagnosis/TelemetryControllerTest.java): Comprehensive MockMvc integration tests (7 tests).

---

## 4. Frontend Implementation Details

### A. Modified Frontend Files
- [`api.js`](file:///Users/shahabahmad/Documents/P_311/frontend/src/services/api.js): Exported `getLatestTelemetry(deviceId = null)` and `getTelemetryHistory(deviceId = null, limit = 20)`.
- [`TelemetryGrid.jsx`](file:///Users/shahabahmad/Documents/P_311/frontend/src/components/telemetry/TelemetryGrid.jsx): Added `isLive` prop, pulsing green `LIVE STREAM` badge vs amber `DIAGNOSIS SNAPSHOT` badge, and timestamp of latest reading.
- [`TelemetryTrendChart.jsx`](file:///Users/shahabahmad/Documents/P_311/frontend/src/components/telemetry/TelemetryTrendChart.jsx): Added `liveHistory` prop, data lineage caption, and interactive source toggle (`Live Raw` vs `Diagnosis Records`) so time-series lines are never intermingled.
- [`Dashboard.jsx`](file:///Users/shahabahmad/Documents/P_311/frontend/src/pages/Dashboard.jsx): Integrated 10-second polling for live telemetry and history, passing live data with fallback to diagnosis telemetry if no raw stream exists.
- [`DeviceDetail.jsx`](file:///Users/shahabahmad/Documents/P_311/frontend/src/pages/DeviceDetail.jsx): Added 10-second live telemetry refresh for the active device.
- Frontend Tests: Updated [`api.test.js`](file:///Users/shahabahmad/Documents/P_311/frontend/src/test/api.test.js), [`components.test.jsx`](file:///Users/shahabahmad/Documents/P_311/frontend/src/test/components.test.jsx), and [`Dashboard.test.jsx`](file:///Users/shahabahmad/Documents/P_311/frontend/src/test/Dashboard.test.jsx).

---

## 5. Test Suite Verification & Progression

| Test Suite | Before Fix | After Fix | Net Change | Status |
|---|---|---|---|---|
| **Spring Boot (JUnit 5 / MockMvc)** | 70 passed | **77 passed** | +7 tests | **PASS (100%)** |
| **React Frontend (Vitest)** | 42 passed | **48 passed** | +6 tests | **PASS (100%)** |
| **Python AI Engine (pytest)** | 231 passed | **231 passed** | 0 | **PASS (100%)** |
| **TOTAL SYSTEM TESTS** | **343 passed** | **356 passed** | **+13 tests** | **PASS (100%)** |

All 356 tests execute and pass with zero failures or skips.

---

## 6. Live End-to-End MQTT Verification Evidence

A live test was conducted using real network calls and real database verification:

### 1. Published Distinct Telemetry Packet
```bash
mosquitto_pub -h localhost -p 1883 -t "iot/ESP32_001/telemetry" \
  -m '{"device_id":"ESP32_001","temperature":31.4,"humidity":55.5,"vibration":1.8,"current":5.6,"pressure":2.7}'
```

### 2. Confirmed Row Insertion in PostgreSQL
Query:
```sql
SELECT id, device_id, temperature, humidity, vibration, current_value, pressure, recorded_at 
FROM sensor_readings ORDER BY recorded_at DESC, id DESC LIMIT 1;
```
Result:
```text
  id  | device_id | temperature | humidity | vibration | current_value | pressure |        recorded_at         
------+-----------+-------------+----------+-----------+---------------+----------+----------------------------
 1021 | ESP32_001 |        31.4 |     55.5 |       1.8 |           5.6 |      2.7 | 2026-10-01 13:47:22.037913
```

### 3. Confirmed REST API Response from Spring Boot
Request:
```bash
curl -s -H "Authorization: Bearer <TOKEN>" "http://localhost:8080/api/v1/telemetry/latest?deviceId=ESP32_001"
```
Response (`HTTP 200 OK`):
```json
{
  "deviceId": "ESP32_001",
  "temperature": 31.4,
  "humidity": 55.5,
  "vibration": 1.8,
  "current": 5.6,
  "pressure": 2.7,
  "recordedAt": "2026-10-01T13:47:22.037913"
}
```

### 4. Confirmed Frontend & Grafana Behavior
- **React Frontend**: Refreshed within 10 seconds, displaying `31.4°C` on the Temperature card with the pulsing `LIVE STREAM` indicator and recorded timestamp.
- **Trend Chart**: Added point `#4` (`31.4°C`) to the multi-channel SVG progression trend chart under the `Live Raw` source mode.
- **Grafana (Port 3000)**: Continued normal 10-second dashboard refresh without interruption (`HTTP 200 OK` at `/api/health`).
- **AI Bridge (Port 5001)**: Remained healthy (`HTTP 200 OK` at `/health`) and was NOT triggered by the telemetry polling.
