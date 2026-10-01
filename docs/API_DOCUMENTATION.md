# P_311 — REST API Catalog & Integration Specification

This document provides the complete API specification for the Spring Boot backend (`http://localhost:8080`) and the Python AI Bridge (`http://localhost:5001`).

---

## 1. Authentication & Security Headers

All protected endpoints require a JWT Bearer token supplied in the HTTP `Authorization` request header:

```http
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

If the token is missing, expired, or invalid, the backend returns:
```json
{
  "timestamp": "2026-10-01T05:47:47.785Z",
  "status": 401,
  "error": "Unauthorized",
  "message": "Full authentication is required to access this resource",
  "path": "/api/v1/diagnosis/latest"
}
```

---

## 2. Authentication Endpoints (`/api/v1/auth`)

### 2.1 User Registration
- **Method:** `POST`
- **Path:** `/api/v1/auth/register`
- **Auth Required:** No (Public)
- **Request Body:**
```json
{
  "username": "operator1",
  "email": "operator1@p311.iot",
  "password": "Password123!",
  "role": "ADMIN"
}
```
- **Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzUxMiJ9...",
  "username": "operator1",
  "email": "operator1@p311.iot",
  "role": "ADMIN",
  "expiresInSeconds": 86400,
  "tokenType": "Bearer"
}
```
- **Errors:**
  - `400 Bad Request`: Validation failure (username < 3 chars, password < 6 chars, invalid email).
  - `409 Conflict`: Username or email already registered (`UserAlreadyExistsException`).

### 2.2 User Login
- **Method:** `POST`
- **Path:** `/api/v1/auth/login`
- **Auth Required:** No (Public)
- **Request Body:**
```json
{
  "username": "operator1",
  "password": "Password123!"
}
```
- **Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzUxMiJ9...",
  "username": "operator1",
  "email": "operator1@p311.iot",
  "role": "ADMIN",
  "expiresInSeconds": 86400,
  "tokenType": "Bearer"
}
```
- **Errors:**
  - `401 Unauthorized`: Invalid username or password.

---

## 3. Diagnosis Endpoints (`/api/v1/diagnosis`)

### 3.1 Trigger On-Demand AI Diagnosis
- **Method:** `POST`
- **Path:** `/api/v1/diagnosis`
- **Auth Required:** Yes (`Bearer <token>`)
- **Purpose:** Submits raw IoT sensor telemetry, executes RAG vector retrieval, prompts local Ollama LLM, parses structured results, and persists to PostgreSQL.
- **Request Body:**
```json
{
  "deviceId": "ESP32_001",
  "temperature": 96.0,
  "humidity": 45.0,
  "vibration": 7.2,
  "current": 11.0,
  "pressure": 2.1
}
```
- **Response:** `201 Created`
```json
{
  "id": "diag-ESP32_001-1790833783866",
  "deviceId": "ESP32_001",
  "topic": "api/manual/trigger",
  "timestamp": "2026-10-01T11:19:43.872",
  "latencySeconds": 50.194,
  "telemetry": {
    "temperature": 96.0,
    "humidity": 45.0,
    "vibration": 7.2,
    "current": 11.0,
    "pressure": 2.1
  },
  "diagnosis": {
    "primaryFault": {
      "id": "FAULT-001",
      "title": "Stator Winding Insulation Breakdown"
    },
    "confidence": {
      "level": "high",
      "reason": "Combined thermal and electrical load exceeds operational limits."
    },
    "evidence": [
      { "type": "telemetry", "parameter": "temperature", "value": 96.0, "unit": "°C" },
      { "type": "telemetry", "parameter": "vibration", "value": 7.2, "unit": "mm/s" },
      { "type": "telemetry", "parameter": "current", "value": 11.0, "unit": "A" }
    ],
    "possibleCauses": [
      "Inter-turn winding short circuit",
      "Motor cooling fan blockage",
      "Severe mechanical unbalance"
    ],
    "recommendedChecks": [
      "Measure stator insulation resistance with megohmmeter",
      "Inspect bearing housing for overheating",
      "Check phase-to-phase current balance"
    ],
    "knowledgeSources": [
      {
        "rank": 1,
        "documentId": "FAULT-001",
        "chunkId": "FAULT-001_chunk_001",
        "title": "Stator Winding Insulation Breakdown",
        "source": "faults/FAULT-001.md",
        "similarity": 0.8142
      }
    ],
    "rawLlmResponse": "### Diagnostic Analysis & Explanation...",
    "model": "qwen2.5:1.5b"
  }
}
```
- **Errors:**
  - `400 Bad Request`: Incomplete or invalid telemetry parameters (`InvalidTelemetryException`).
  - `401 Unauthorized`: Missing or invalid JWT.
  - `503 Service Unavailable`: AI Python Bridge or Ollama daemon unreachable (`DiagnosisServiceUnavailableException`).

### 3.2 Get Latest Diagnosis
- **Method:** `GET`
- **Path:** `/api/v1/diagnosis/latest`
- **Auth Required:** Yes (`Bearer <token>`)
- **Response:** `200 OK` (Returns newest `DiagnosisResponse` object).
- **Errors:**
  - `404 Not Found`: No diagnoses currently recorded in the database.

### 3.3 Get Diagnosis by Unique ID
- **Method:** `GET`
- **Path:** `/api/v1/diagnosis/{id}`
- **Auth Required:** Yes (`Bearer <token>`)
- **Response:** `200 OK`
- **Errors:**
  - `404 Not Found`: Diagnosis ID does not exist (`DiagnosisNotFoundException`).

### 3.4 Get Diagnoses by Device ID
- **Method:** `GET`
- **Path:** `/api/v1/diagnosis/device/{deviceId}`
- **Auth Required:** Yes (`Bearer <token>`)
- **Response:** `200 OK` (Array of `DiagnosisResponse` objects ordered by creation date descending).

---

## 4. Alert Endpoints (`/api/v1/alerts`)

### 4.1 List System Alerts
- **Method:** `GET`
- **Path:** `/api/v1/alerts`
- **Auth Required:** Yes (`Bearer <token>`)
- **Query Parameters:**
  - `deviceId` (optional string): Filter by device ID (e.g., `ESP32_001`).
  - `acknowledged` (optional boolean): Filter by ack status (`true` or `false`).
  - `severity` (optional string): Filter by severity (`WARNING` or `CRITICAL`).
- **Response:** `200 OK`
```json
[
  {
    "id": 61,
    "deviceId": "ESP32_001",
    "alertType": "SENSOR_THRESHOLD",
    "sensorParameter": "temperature",
    "sensorValue": 95.0,
    "thresholdValue": 90.0,
    "severity": "CRITICAL",
    "message": "Critical temperature (95.0°C >= 90.0°C). Risk of stator winding thermal breakdown.",
    "source": "TELEMETRY_INGESTION",
    "acknowledged": false,
    "acknowledgedBy": null,
    "acknowledgedAt": null,
    "createdAt": "2026-10-01T11:17:14.672"
  }
]
```

### 4.2 Acknowledge Alert
- **Method:** `POST`
- **Path:** `/api/v1/alerts/{id}/acknowledge`
- **Auth Required:** Yes (`Bearer <token>`)
- **Purpose:** Flags an active alert as acknowledged by the currently authenticated operator.
- **Response:** `200 OK`
```json
{
  "id": 61,
  "deviceId": "ESP32_001",
  "acknowledged": true,
  "acknowledgedBy": "operator1",
  "acknowledgedAt": "2026-10-01T11:18:38.307",
  "severity": "CRITICAL"
}
```
- **Errors:**
  - `404 Not Found`: Alert ID does not exist (`AlertNotFoundException`).

---

## 5. Python AI Bridge Internal API (`http://localhost:5001`)

### 5.1 Health Check
- **Method:** `GET`
- **Path:** `/health`
- **Response:** `200 OK`
```json
{
  "status": "UP",
  "service": "ai-diagnosis-bridge",
  "timestamp": 1790833493.519
}
```

### 5.2 Execute Diagnostic Inference
- **Method:** `POST`
- **Path:** `/api/v1/diagnose`
- **Request Body:**
```json
{
  "device_id": "ESP32_001",
  "temperature": 96.0,
  "humidity": 45.0,
  "vibration": 7.2,
  "current": 11.0,
  "pressure": 2.1
}
```
- **Response:** `200 OK` (JSON matching `StructuredDiagnosis` schema).
