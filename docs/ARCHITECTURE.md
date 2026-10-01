# P_311 — System Architecture Specification

This document provides the formal technical architecture for **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant**.

---

## 1. Architectural Overview & Philosophy

P_311 is architected around the core principle of **domain isolation** and **knowledge grounding**:
1. **Zero Hallucination Tolerance:** Rather than querying an unconstrained LLM, the system forces diagnosis generation through a strict Retrieval-Augmented Generation (RAG) pipeline where every recommendation must be cited from indexed technical manuals.
2. **Strict Dual-Pipeline Isolation:** The real-time live IoT streaming pipeline is physically and logically separated from the offline industrial validation pipeline (MetroPT-3).
3. **Stateless Scalability with Relational Persistence:** The ingestion and AI inference tiers operate statelessly while state and historical audit logs are persisted in PostgreSQL.

---

## 2. Dual-Path Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      PATH 1: LIVE OPERATIONAL PATH                     │
│                                                                        │
│   Python Sensor Simulator (ESP32 emulation)                            │
│              │                                                         │
│              ▼ [TCP:1883 - MQTT JSON]                                  │
│   Eclipse Mosquitto Broker                                             │
│              │                                                         │
│              ▼ [Sub: iot/+/telemetry]                                  │
│   Spring Boot Backend (Port 8080)                                      │
│         ├──────────────────────────┐                                   │
│         ▼                          ▼                                   │
│   AlertDetectionService     PostgreSQL 16 (Port 5432)                  │
│   (Threshold & Cooldown)    (sensor_readings, diagnoses, alerts)       │
│         │                          ▲                                   │
│         │                          │ [Direct SQL Queries]              │
│         ▼                          │                                   │
│   React UI (Port 5173) ◄───────────┴── Grafana Dashboard (Port 3000)   │
│         │                                                              │
│         ▼ [POST /api/v1/diagnosis]                                     │
│   Spring Boot Diagnosis Controller                                     │
│         │                                                              │
│         ▼ [HTTP REST JSON: Port 5001]                                  │
│   Python AI Bridge (ai/mqtt/src/server.py)                             │
│         │                                                              │
│         ▼                                                              │
│   P12 Diagnosis Engine (ai/diagnosis/)                                 │
│         │                                                              │
│         ▼                                                              │
│   P11 RAG Pipeline (ai/rag/ & ai/integration/)                         │
│         ├──────────────────────────┐                                   │
│         ▼ [Dense Vector Query]     ▼ [Prompt + Context]                │
│   ChromaDB (iot_fault_knowledge)  Ollama LLM (qwen2.5:1.5b: Port 11434)│
│         └───────────┬──────────────┘                                   │
│                     ▼                                                  │
│         Structured Diagnosis Response                                  │
│                     ▼                                                  │
│   Spring Boot PostgresDiagnosisStore ──► PostgreSQL (diagnoses table)  │
└────────────────────────────────────────────────────────────────────────┘

                                  ≠ (STRICTLY ISOLATED)

┌────────────────────────────────────────────────────────────────────────┐
│               PATH 2: OFFLINE INDUSTRIAL VALIDATION PATH               │
│                                                                        │
│   MetroPT-3 Raw CSV (208 MB, 1,516,948 observations)                   │
│              │                                                         │
│              ▼                                                         │
│   MetroPTLoader (ai/dataset/metropt/src/loader.py)                     │
│   - Parses timestamps, audits missing values (0 nulls, 0 dups)         │
│              │                                                         │
│              ▼                                                         │
│   MetroPTValidator (ai/dataset/metropt/src/validator.py)               │
│   - Validates schema, domain ranges, verifies NO humidity/vibration    │
│              │                                                         │
│              ▼                                                         │
│   MetroPTFeatureExtractor (ai/dataset/metropt/src/features.py)         │
│   - Computes continuous distributions and machine state duty cycles    │
│              │                                                         │
│              ▼                                                         │
│   MetroPTAnalyzer (ai/dataset/metropt/src/analyzer.py)                 │
│   - Evaluates operating regimes and 4 ground truth failure events      │
│              │                                                         │
│              ▼                                                         │
│   MetroPTReportGenerator (ai/dataset/metropt/src/report.py)            │
│   - Generates JSON summaries, validation_report.md & 6 visual figures  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Subsystem Breakdown

### 3.1 Edge / Sensor Simulator (`Iot_hcl_Python/mqtt_sender.py`)
- Simulates an ESP32 industrial edge node.
- Periodically publishes 5-channel continuous telemetry to `iot/ESP32_001/telemetry`:
  - `temperature` (°C)
  - `humidity` (%)
  - `vibration` (mm/s)
  - `current` (A)
  - `pressure` (bar)

### 3.2 Messaging Bus (Eclipse Mosquitto)
- Standard lightweight MQTT broker running on TCP port `1883`.
- Decouples edge producers from backend consumers.
- Supports QoS 0/1 messaging with multi-tenant wildcard subscriptions (`iot/+/telemetry`).

### 3.3 Backend Tier (Spring Boot 4.1.1 / Java 27)
- **Ingestion:** `MqttSubscriber` implements Paho callback listeners to parse JSON telemetry asynchronously.
- **Persistence:** Ingested readings are saved directly to PostgreSQL `sensor_readings` using JPA `SensorReadingRepository`.
- **Alert Detection:** `AlertDetectionService` intercepts readings and triggers warning/critical alerts upon threshold violations with a 60-second duplicate suppression window.
- **Security:** `SecurityConfig` enforces stateless JWT validation via `JwtAuthenticationFilter`, protecting REST endpoints.
- **AI Orchestration:** `DiagnosisService` delegates diagnostic requests to `HttpAIDiagnosisClient`, and persists returned structured graphs into `diagnoses`, `diagnosis_evidence`, and `diagnosis_knowledge_sources`.

### 3.4 AI & Knowledge Tier
- **ChromaDB Vector Store:** Embedded persistent database storing chunked technical documents in collection `iot_fault_knowledge`.
- **Embeddings:** `nomic-embed-text` produces 768-dimensional normalized dense vectors.
- **LLM Engine:** Local Ollama instance serving `qwen2.5:1.5b`.
- **AI Bridge Server:** `ai/mqtt/src/server.py` runs a lightweight HTTP server on port `5001` with endpoints:
  - `GET /health`: Healthcheck probe.
  - `POST /api/v1/diagnose`: Accepts telemetry payload, runs retrieval and inference, and returns validated JSON.

### 3.5 Operator Dashboards
- **React Frontend (Port 5173):** User-facing operational cockpit providing telemetry charts, active alerts, on-demand diagnosis triggers, and cited knowledge inspection.
- **Grafana Dashboard (Port 3000):** Operations console (`p311-operations`) with 13 panels querying PostgreSQL directly for multi-channel trends, latency progression, fault distributions, and database storage health.

---

## 4. Sequence Diagrams

### 4.1 Telemetry Ingestion & Alerting Flow
```text
Simulator            Mosquitto           Spring Boot          PostgreSQL          Operator UI
    │                    │                    │                    │                   │
    ├── Publish JSON ───►│                    │                    │                   │
    │                    ├── Deliver Msg ────►│                    │                   │
    │                    │                    ├── Save Reading ───►│                   │
    │                    │                    │                    │                   │
    │                    │                    ├── Check Thresholds │                   │
    │                    │                    │   (Exceeded)       │                   │
    │                    │                    ├── Save Alert ─────►│                   │
    │                    │                    │                    │                   │
    │                    │                    │◄── Poll / Alerts ──────────────────────┤
    │                    │                    ├──── Return Alert List ────────────────►│
```

### 4.2 On-Demand AI Diagnosis Flow
```text
Operator UI          Spring Boot          AI Bridge            ChromaDB             Ollama (LLM)
    │                    │                    │                    │                    │
    ├── POST /diagnosis ─►│                    │                    │                    │
    │   (Auth Token)     ├── POST /diagnose ─►│                    │                    │
    │                    │   (Telemetry)      ├── Query Vector ───►│                    │
    │                    │                    │◄── Top-3 Chunks ───┤                    │
    │                    │                    │                                         │
    │                    │                    ├── Prompt + Context ────────────────────►│
    │                    │                    │◄── Diagnostic Reasoning ────────────────┤
    │                    │                    │                                         │
    │                    │                    ├── Parse & Validate                      │
    │                    │◄── Structured JSON ┤                                         │
    │                    ├── Save to Postgres │                                         │
    │◄── 201 Created ────┤                    │                                         │
```

---

## 5. Network Port Allocation

| Component | Port | Transport Protocol | Security / Auth |
| :--- | :---: | :---: | :--- |
| Mosquitto MQTT | 1883 | TCP / MQTT | Unauthenticated (local sandbox) |
| Python AI Bridge | 5001 | TCP / HTTP | Local internal loopback |
| PostgreSQL DB | 5432 | TCP / PostgreSQL Wire | Username / Password (`shahabahmad:Arisha`) |
| Spring Boot API | 8080 | TCP / HTTP | JWT Bearer Token (HMAC-SHA512) |
| React UI (Vite) | 5173 | TCP / HTTP | Web Browser User Session |
| Grafana Console | 3000 | TCP / HTTP | Basic Auth (`admin:admin`) |
| Ollama Service | 11434 | TCP / HTTP | Local REST daemon |
