# P_311 — Knowledge-Driven IoT Fault Diagnosis Assistant
## Comprehensive Project Documentation (Phase 24)

---

## 1. Project Title & Identifier

- **Project Title:** Knowledge-Driven IoT Fault Diagnosis Assistant
- **Project Identifier:** P_311
- **Target Domain:** Industrial IoT (IIoT), Predictive Maintenance, Knowledge Retrieval-Augmented Generation (RAG), Operations Monitoring

---

## 2. Abstract

The **Knowledge-Driven IoT Fault Diagnosis Assistant (P_311)** is an end-to-end industrial software and artificial intelligence platform designed to ingest, monitor, persist, analyze, and diagnose real-time IoT equipment telemetry. Industrial rotating machinery and pneumatic systems produce continuous multivariate telemetry streams (temperature, vibration, motor current, pressure, humidity) that are difficult for operators to interpret in isolation during emerging failure states.

P_311 solves this challenge through a hybrid engineering architecture consisting of two logically isolated workstreams:
1. **Live Operational Pipeline:** Edge-simulated sensor telemetry is published over MQTT (Mosquitto) to a robust Spring Boot backend. Telemetry is validated, evaluated for threshold violations (generating automated alerts with deduplication cooldowns), and persisted in PostgreSQL. An authenticated React dashboard and a multi-panel Grafana operations console provide real-time visual telemetry monitoring. When abnormal conditions arise, telemetry triggers an on-demand AI fault diagnosis workflow: an asynchronous Python bridge retrieves authoritative technical maintenance literature from a ChromaDB vector database using semantic embeddings (`nomic-embed-text`) and synthesizes an explainable, structured diagnosis using a locally hosted Large Language Model (`qwen2.5:1.5b` via Ollama). The structured diagnosis (identifying primary faults, confidence levels, physical evidence, root causes, and recommended maintenance actions) is permanently persisted in PostgreSQL relational tables and displayed in the React frontend.
2. **Offline Industrial Dataset Validation Workstream:** To ground and validate physical diagnostic rules against real-world machinery, P_311 incorporates a dedicated offline analysis pipeline using the real-world **MetroPT-3** dataset (1,516,948 observations from an operational metro train Air Production Unit screw compressor). This separate pipeline benchmarks compressor operating states and thermal/electrical degradation across four verified air leak maintenance failure events without modifying the live operational pipeline.

---

## 3. Problem Statement

Modern industrial operations rely heavily on continuous sensor telemetry from critical rotating assets such as motors, pumps, and air compressors. However, industrial maintenance teams face severe operational bottlenecks:
- **Multivariate Cognitive Overload:** An isolated reading (e.g., elevated temperature or current) cannot distinguish between high normal workload and serious failure (e.g., severe air leak vs. bearing seizure). Operators require multi-signal context.
- **Knowledge Siloing:** Authoritative troubleshooting guidelines, ISO vibration severity standards, and manufacturer maintenance manuals reside in static documentation and are rarely linked directly to real-time telemetry.
- **Hallucination Risks in Generic AI:** Directly prompting general-purpose cloud LLMs with raw numbers often produces ungrounded, fabricated, or dangerous maintenance recommendations.
- **Traceability and Persistence Deficits:** Temporary diagnosis outputs that disappear after inference prevent post-mortem auditing, root-cause tracking, and historical reliability engineering.

P_311 addresses these challenges by grounding local AI reasoning in curated technical manuals using Retrieval-Augmented Generation (RAG), enforcing persistent database storage, providing operator alerting and visual observability, and benchmarking against real industrial datasets.

> [!NOTE]
> P_311 is an **operator decision-support assistant**. It does not perform autonomous equipment control or closed-loop physical repairs.

---

## 4. Project Objectives

The P_311 system was designed and verified to fulfill the following core engineering objectives:
1. **Real-Time Telemetry Acquisition:** Collect 5-channel continuous IoT telemetry (temperature, humidity, vibration, current, pressure) from emulated industrial microcontrollers.
2. **Standardized MQTT Transport:** Ingest telemetry messages via lightweight, industry-standard MQTT protocols (Eclipse Mosquitto broker).
3. **Robust Backend Processing:** Receive, validate, and persist telemetry into a production-grade relational database (PostgreSQL 16) using Spring Boot 4 / Java 27.
4. **Automated Alert Detection:** Detect abnormal threshold violations across critical sensor parameters in real-time with deduplication cooldowns and authenticated operator acknowledgement.
5. **Knowledge-Grounded Retrieval (RAG):** Extract relevant troubleshooting procedures and fault documents from a ChromaDB vector database using dense vector embeddings (`nomic-embed-text`).
6. **Local LLM Inference:** Generate explainable diagnostic assessments locally via Ollama using `qwen2.5:1.5b`, ensuring zero dependency on external third-party cloud APIs.
7. **Structured Diagnosis Persistence:** Parse LLM outputs into structured entities (fault title, confidence level, evidence mappings, recommended checks, knowledge source citations) and store them permanently in PostgreSQL.
8. **Operator User Interface:** Provide a responsive, authenticated React/Vite dashboard for viewing live telemetry, manual diagnosis execution, and alert management.
9. **Infrastructure Observability:** Deliver a comprehensive Grafana operations dashboard querying PostgreSQL directly to monitor telemetry trends, diagnosis latencies, and storage health.
10. **Real-World Industrial Validation:** Validate thermodynamic and electrical operating state dynamics using the real-world MetroPT-3 urban railway compressor dataset (1.51M rows) in a strictly isolated offline workstream.

---

## 5. System Architecture

The project maintains two strictly decoupled pipelines:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     LIVE OPERATIONAL PIPELINE                          │
│                                                                        │
│   Python Sensor Simulator (ESP32 emulation)                            │
│              ↓                                                         │
│      MQTT Mosquitto (port 1883)                                        │
│              ↓                                                         │
│    Spring Boot Backend (port 8080)                                     │
│         ├──────────────────────────┐                                   │
│         ↓                          ↓                                   │
│    Alert Detection          PostgreSQL 16 (port 5432)                  │
│    (Threshold / Cooldown)   (sensor_readings, diagnoses, alerts)       │
│         │                          │                                   │
│         └───────────┬──────────────┘                                   │
│                     ↓                                                  │
│         ┌───────────────────────┐                                      │
│         │                       │                                      │
│    React Frontend (5173)   Grafana (3000)                              │
│         │                                                              │
│         ↓                                                              │
│    Trigger Diagnosis Request                                           │
│         ↓                                                              │
│    Python AI Bridge (port 5001)                                        │
│         ↓                                                              │
│    P12 Diagnosis Engine                                                │
│         ↓                                                              │
│    P11 RAG + Local Ollama LLM (port 11434)                             │
│         ├──────────────────────────┐                                   │
│         ↓                          ↓                                   │
│    ChromaDB (Vector Search)   qwen2.5:1.5b (Local Inference)           │
│         └───────────┬──────────────┘                                   │
│                     ↓                                                  │
│         Structured Diagnosis Response                                  │
│                     ↓                                                  │
│         Spring Boot Persistence → PostgreSQL                           │
└────────────────────────────────────────────────────────────────────────┘

                                  ≠ (STRICTLY ISOLATED)

┌────────────────────────────────────────────────────────────────────────┐
│                   OFFLINE P22 VALIDATION PIPELINE                      │
│                                                                        │
│   MetroPT-3 CSV (208 MB, 1,516,948 observations)                       │
│              ↓                                                         │
│   MetroPTLoader (Data quality audit: 0 nulls, 0 duplicates)            │
│              ↓                                                         │
│   MetroPTValidator (Schema, physical bounds & isolation enforcement)   │
│              ↓                                                         │
│   MetroPTFeatureExtractor (Continuous statistics & state duty cycles)  │
│              ↓                                                         │
│   MetroPTAnalyzer (Operating states & ground truth failure evaluation) │
│              ↓                                                         │
│   MetroPTReportGenerator (Markdown report, JSON artifacts & 6 plots)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. P5–P24 Implementation Phase History

| Phase | Milestone Purpose | Key Deliverables & Implementation Highlights | Status |
| :---: | :--- | :--- | :---: |
| **P5** | Knowledge Base Design | Authored industrial technical documentation across 3 categories: Faults (`FAULT-001` to `FAULT-005`), Sensors (`temperature`, `vibration`, `current`, `pressure`, `humidity`), and Maintenance Procedures (`INSPECT-BEARING`, `LUBRICATE-MOTOR`, etc.). | **Complete** |
| **P6** | Document Ingestion Pipeline | Implemented markdown parsers, semantic chunkers, and schema validators with metadata preservation in `ai/ingestion/`. | **Complete** |
| **P7** | Embedding Generation | Integrated local dense vector embeddings using `nomic-embed-text` via Ollama, generating 768-dimensional normalized vectors in `ai/embeddings/`. | **Complete** |
| **P8** | Vector Database Persistence | Deployed ChromaDB persistent collection (`iot_fault_knowledge`) with cosine similarity indexing in `ai/vector-db/`. | **Complete** |
| **P9** | RAG Retrieval Pipeline | Built query builder, ChromaDB similarity search, rank-ordering, and context builder in `ai/rag/`. | **Complete** |
| **P10** | Local LLM Integration | Connected local `qwen2.5:1.5b` via Ollama REST API with prompt templates, temperature controls, and error handling in `ai/llm/`. | **Complete** |
| **P11** | RAG + LLM Integration | Orchestrated end-to-end telemetry question-answering combining vector retrieval evidence and LLM inference in `ai/integration/`. | **Complete** |
| **P12** | Structured Diagnosis Engine | Developed `DiagnosisEngine`, response parser, confidence scorers, and Pydantic schema validators in `ai/diagnosis/`. | **Complete** |
| **P13** | MQTT + AI Worker | Built asynchronous MQTT subscriber worker in `ai/mqtt/` linking live Mosquitto topics to the diagnosis pipeline. | **Complete** |
| **P14** | Spring Boot REST API | Built Java 27 / Spring Boot REST controllers, DTOs, and HTTP AI client communicating with persistent Python bridge on port 5001. | **Complete** |
| **P15** | Diagnosis Database Persistence | Created PostgreSQL JPA entities, repositories, and foreign-key relational mappings (`diagnoses`, `diagnosis_evidence`, `diagnosis_knowledge_sources`, etc.). | **Complete** |
| **P16** | React Frontend Baseline | Scaffolded React / Vite single-page application with Tailwind CSS, Axios API service, and core views on port 5173. | **Complete** |
| **P17** | Diagnosis Dashboard Enhancement | Extended React UI with interactive telemetry charts, latest diagnosis cards, evidence visualizers, and manual diagnosis execution. | **Complete** |
| **P18** | Grafana Operations Dashboard | Provisioned PostgreSQL datasource and 13-panel operational dashboard (`p311-operations`) in Grafana on port 3000. | **Complete** |
| **P19** | Authentication & Authorization | Implemented Spring Security JWT authentication, BCrypt password hashing, user registration/login, and React route guards. | **Complete** |
| **P20** | Alerts & Notifications | Built `AlertDetectionService` with real-time threshold checking, duplicate suppression cooldown, operator acknowledgement, and UI alert badges. | **Complete** |
| **P21** | Comprehensive Testing & QA | Established 329-test automated baseline across Spring Boot (70), React (42), and Python AI (217). | **Complete** |
| **P22** | MetroPT-3 Industrial Dataset | Implemented offline validation pipeline over 1.51M real APU compressor readings, validating 4 air leak events and generating 6 figures. | **Complete** |
| **P23** | Full System Integration | Executed live end-to-end validation across all 7 services; verified failure recovery, RAG cases, persistence across restarts, and 343 regression tests. | **Complete** |
| **P24** | Comprehensive Documentation | Authored complete, accurate, verified technical documentation, architecture specifications, API catalogs, schema guides, and viva notes. | **Complete** |

---

## 7. Knowledge Base (P5)

The authoritative knowledge base resides in markdown format and is indexed into ChromaDB. It consists of three curated categories:

1. **Fault Diagnostic Documents (`faults/`):**
   - `FAULT-001`: Stator Winding Insulation Breakdown (inter-turn short circuit, overcurrent, thermal degradation).
   - `FAULT-002`: Bearing Inner/Outer Race Fluting & Fatigue (vibration harmonics, acoustic degradation).
   - `FAULT-003`: Rotor Dynamic Unbalance & Misalignment (1X/2X rotational vibration peaks).
   - `FAULT-004`: Mechanical Looseness & Soft Foot (sub-harmonic vibration, phase instability).
   - `FAULT-005`: Pneumatic Discharge Valve Leakage (pressure drop, prolonged compressor duty cycle).
2. **Sensor Characteristic Documents (`sensors/`):**
   - `temperature.md`: Thermocouple/RTD characteristics, normal ranges (40–65°C), warning (80°C), critical (90°C).
   - `vibration.md`: Piezoelectric accelerometer thresholds based on ISO 10816-3 (normal < 4.5 mm/s, critical > 7.1 mm/s).
   - `current.md`: CT/Hall effect sensors, Full Load Amps (FLA) limits, starting surge vs sustained overcurrent.
   - `pressure.md`: Piezoresistive pressure transmitters, governor cut-in (8.2 bar) and safety limits (7.0 bar).
   - `humidity.md`: Environmental humidity limits and condensation prevention.
3. **Maintenance Procedure Documents (`procedures/`):**
   - Standard operating procedures for bearing inspection, motor re-lubrication, alignment verification, and pneumatic filter replacement.

---

## 8. RAG Pipeline & Knowledge Grounding

```text
Incoming Telemetry Observation
           ↓
[QueryBuilder] Formats natural language diagnostic query
           ↓
[Ollama nomic-embed-text] Generates 768-dimensional normalized query vector
           ↓
[ChromaDB] Cosine distance search across "iot_fault_knowledge" collection
           ↓
[Retriever] Selects top-k knowledge chunks (k=3) with similarity scores
           ↓
[ContextBuilder] Assembles retrieved technical chunks + telemetry values
           ↓
[PromptBuilder] Constructs strict system prompt preventing hallucination
           ↓
[Ollama qwen2.5:1.5b] Generates grounded diagnostic explanation
           ↓
[DiagnosisParser] Extracts structured fault, confidence, and recommended actions
```

### Why RAG is Essential for Industrial Diagnosis
Asking general-purpose LLMs to diagnose industrial sensor telemetry based solely on pretrained weights leads to ungrounded reasoning and severe hallucinations. In P_311:
- The vector retrieval step supplies the LLM with exact, verified manufacturer limits and failure criteria.
- The retrieved knowledge chunks are recorded in the diagnosis payload (`knowledgeSources`), providing complete auditability.
- When no specific fault document matches the observed telemetry, the system transparently reports `confidence: low` rather than inventing a false diagnosis.

---

## 9. Local Large Language Model (P10)

- **LLM Model:** `qwen2.5:1.5b` (Q4_K_M quantized, 1.5 billion parameters)
- **Embedding Model:** `nomic-embed-text` (768 dimensions, F16)
- **Serving Runtime:** Local Ollama daemon (`http://localhost:11434`)
- **Execution Platform:** Local CPU / Apple Silicon unified memory (no cloud API keys, zero network data egress)
- **Observed Inference Latency:** ~30 – 50 seconds per diagnostic request on CPU

---

## 10. Diagnosis Engine & Structured Output (P12)

The `DiagnosisEngine` transforms raw LLM natural language text into a strict, validated schema (`StructuredDiagnosis`) containing:
- `diagnosisId`: Unique identifier (`diag-{deviceId}-{timestamp}`)
- `deviceId`: Target IoT asset identifier
- `primaryFault`: Extracted primary fault title and matching fault ID
- `confidence`: Object with `level` (`high`, `medium`, `low`) and explicit `reason`
- `evidence`: Array of physical telemetry parameters observed (`type`, `parameter`, `value`, `unit`, `status`)
- `possibleCauses`: List of potential root causes deduced from retrieved context
- `recommendedChecks`: Specific actionable maintenance steps for field technicians
- `knowledgeSources`: Exact citations of retrieved chunks (`rank`, `documentId`, `chunkId`, `title`, `source`, `similarity`)
- `latencySeconds`: Total inference and parsing execution duration

---

## 11. MQTT Telemetry Architecture (P13)

- **Broker:** Eclipse Mosquitto on port `1883`
- **Telemetry Ingestion Topic:** `iot/{deviceId}/telemetry` (e.g., `iot/ESP32_001/telemetry`)
- **Diagnosis Broadcast Topic:** `iot/{deviceId}/diagnosis`
- **Payload Schema:**
```json
{
  "device_id": "ESP32_001",
  "temperature": 27.50,
  "humidity": 55.00,
  "vibration": 2.10,
  "current": 5.20,
  "pressure": 2.80
}
```

---

## 12. Spring Boot Backend Architecture (P14, P15, P19, P20)

- **Framework:** Spring Boot 4.1.1 on Java 27
- **Database Access:** Spring Data JPA with Hibernate 7.4 and HikariCP connection pooling
- **Security:** Spring Security with stateless JWT Bearer token authentication and BCrypt password hashing
- **Core Components:**
  - `MqttSubscriber`: Asynchronous Eclipse Paho MQTT client subscribing to telemetry and diagnosis topics.
  - `AlertDetectionService`: Evaluates incoming telemetry against authoritative thresholds, applies deduplication cooldowns, and persists alert records.
  - `DiagnosisService`: Orchestrates manual and automatic diagnosis triggering, interacts with the HTTP AI bridge, and coordinates relational persistence.
  - `PostgresDiagnosisStore`: Implements persistent storage for full diagnosis entity graphs.
  - `HttpAIDiagnosisClient`: REST client communicating with the Python AI bridge on port 5001.

---

## 13. Database Architecture & Relational Entities

PostgreSQL 16 hosts 10 verified relational tables in database `iot_fault_diagnosis`:

1. `sensor_readings`: Stores historical time-series telemetry (`id`, `device_id`, `temperature`, `humidity`, `vibration`, `current_value`, `pressure`, `recorded_at`).
2. `diagnoses`: Primary diagnosis entity (`id`, `diagnosis_id`, `device_id`, `primary_fault_title`, `primary_fault_id`, `primary_fault_similarity`, `confidence_level`, `confidence_reason`, `latency_seconds`, `query`, `raw_llm_response`, `created_at`, telemetry snapshots).
3. `diagnosis_evidence`: 1-to-many child table storing sensor parameter evidence rows linked to `diagnosis_record_id`.
4. `diagnosis_knowledge_sources`: 1-to-many child table recording retrieved chunk IDs, titles, file sources, and similarity scores.
5. `diagnosis_possible_causes`: 1-to-many child table storing identified root causes.
6. `diagnosis_recommended_checks`: 1-to-many child table storing maintenance check items.
7. `diagnosis_alternative_faults`: 1-to-many child table recording secondary considered faults.
8. `diagnosis_additional_info`: 1-to-many child table storing additional diagnostic notes.
9. `users`: Authentication store (`id`, `username`, `email`, `password_hash`, `role`, `created_at`).
10. `alerts`: System alert records (`id`, `device_id`, `alert_type`, `sensor_parameter`, `sensor_value`, `threshold_value`, `severity`, `message`, `acknowledged`, `acknowledged_by`, `acknowledged_at`, `created_at`).

---

## 14. Authentication & Authorization (P19)

- **Endpoints:** `/api/v1/auth/register`, `/api/v1/auth/login`
- **Token Mechanism:** Stateless HMAC-SHA512 signed JWT Bearer tokens with 24-hour expiration.
- **Roles:** `USER` (operator access), `ADMIN` (administrator access).
- **Access Control:** Protected endpoints (`/api/v1/diagnosis/**`, `/api/v1/alerts/**`) strictly require valid JWT Bearer authentication; unauthenticated requests return `HTTP 401 Unauthorized`.
- **Known Limitation:** Self-registration currently accepts a `role` field. Production deployment should restrict `ADMIN` role assignment to authorized administrative approval workflows.

---

## 15. Alert System & Deduplication (P20)

- **Authoritative Industrial Thresholds:**
  - `temperature`: Warning at >= 80.0°C, Critical at >= 90.0°C.
  - `vibration`: Warning at >= 4.50 mm/s, Critical at >= 7.10 mm/s.
  - `current`: Warning at >= 8.50 A, Critical at >= 10.50 A.
  - `pressure`: Warning at <= 1.50 bar, Critical at <= 1.00 bar.
  - `humidity`: Warning at >= 75.0%, Critical at >= 85.0%.
- **Deduplication Cooldown:** Identical alert types on the same device parameter are suppressed for 60 seconds to prevent alert storms.
- **Acknowledgement:** Authenticated operators acknowledge alerts via `/api/v1/alerts/{id}/acknowledge`, stamping `acknowledged_by` and `acknowledged_at`.
- **Known Limitation:** Notifications are dispatched locally via `LocalNotificationService` logs; external SMS/Email gateways are stubbed for production deployment.

---

## 16. React Operator Frontend (P16, P17)

- **Technology:** React 18, Vite, Tailwind CSS, Lucide icons, Axios.
- **Port:** `http://localhost:5173`
- **Core Views:**
  - `Login` & `Register`: Secure authentication pages with JWT persistence.
  - `Dashboard`: Live sensor gauges, multi-channel telemetry timeline charts, active alert banners, latest diagnosis summary, and manual on-demand diagnosis modal.
  - `DiagnosisDetail`: In-depth breakdown showing confidence badges, evidence tables, cited knowledge source cards with similarity meters, and maintenance checklists.
  - `DeviceDetail`: Device-specific telemetry history and diagnosis log.
  - `Alerts`: Filterable table of unacknowledged and acknowledged alerts with one-click operator acknowledgement.

---

## 17. Grafana Operations Dashboard (P18)

- **Port:** `http://localhost:3000`
- **Dashboard Title:** `P_311 — IoT Fault Diagnosis Operations` (`uid: p311-operations`)
- **Datasource:** PostgreSQL 16 (direct SQL queries over public schema)
- **13 Verified Operational Panels:**
  1. Stat: Latest Temperature (°C)
  2. Stat: Latest Humidity (%)
  3. Stat: Latest Vibration (mm/s)
  4. Stat: Latest Current (A)
  5. Stat: Latest Pressure (bar)
  6. Stat: Total Stored Diagnoses
  7. Time Series: Real-Time Multi-Channel Telemetry Trend
  8. Time Series: AI Diagnosis Latency Progression
  9. Bar Chart: Primary Fault Classification Distribution
  10. Pie Chart: Diagnosis Confidence Level Distribution
  11. Table: Persisted AI Fault Diagnosis History
  12. Table: PostgreSQL Database Storage Health
  13. Table: System Alerts & Notifications (P20)

---

## 18. MetroPT-3 Real Industrial Dataset Validation (P22)

The **MetroPT-3** dataset (INESC TEC / Metro do Porto) provides a rigorous offline empirical benchmark:
- **Total Observations:** 1,516,948 rows across 16 columns (Feb 2020 – Sep 2020).
- **Physical Cleanliness:** 0 null values, 0 duplicate timestamps, nominal 10-second sampling.
- **Measured Signals:** `Oil_temperature`, `Motor_current`, 5 pneumatic pressures (`TP2`, `TP3`, `H1`, `DV_pressure`, `Reservoirs`), and 8 digital control signals (`COMP`, `DV_eletric`, `Towers`, `MPG`, `LPS`, etc.).
- **Signal Boundary Enforcement:** **MetroPT-3 contains NO humidity and NO vibration signals.** The validator explicitly prevents conflating MetroPT-3 with the live ESP32 simulator schema.
- **Operational Regimes:**
  - Standby (`Motor_current < 1.0 A`): 54.65% of time (~0.04 A, mean temp 59.3°C)
  - Offloaded (`1.0 <= Motor_current < 5.5 A`): 32.06% of time (~3.88 A, mean temp 66.9°C)
  - Under Load (`Motor_current >= 5.5 A`): 13.29% of time (~5.89 A, mean temp 66.2°C)
- **Ground Truth Failure Detection:** All 4 published air leak failure events were 100% detected through severe duty cycle elongation (UnderLoad skyrocketing from 13.3% normal up to 83.6% failure, a 6.3x increase) and thermal stress (oil temperature peaking at 89.05°C).
- **Strict Isolation:** Zero rows inserted into the live `sensor_readings` table.

---

## 19. Quality Assurance & Regression Test Suite

The system maintains a 100% passing test suite across all application tiers:

```text
========================================================================
P_311 Test Suite Regression Results
========================================================================
P22 MetroPT-3 Dataset Tests:         14 / 14  PASSED
Python AI Core Test Suites (P5–P21): 217 / 217 PASSED
Spring Boot Backend Tests:            70 / 70  PASSED
React Frontend Tests:                 42 / 42  PASSED
------------------------------------------------------------------------
TOTAL REGRESSION SUITE:              343 / 343 PASSED (100% Green)
========================================================================
```

---

## 20. Performance Characteristics

- **MQTT Ingestion to Database:** ~8 – 15 ms
- **Alert Detection Hook:** < 5 ms
- **AI Diagnosis Roundtrip (Local CPU):** 32.6 – 50.2 seconds (`qwen2.5:1.5b` CPU inference)
- **Diagnosis Entity Graph Persistence:** 12 – 25 ms
- **Grafana Panel SQL Execution:** 4 – 18 ms per panel
- **MetroPT-3 Full Pipeline (1.51M rows):** 6.40 seconds

---

## 21. Known System Limitations

1. **CPU LLM Inference Latency:** Local Ollama inference on CPU requires 30–50 seconds per diagnosis request. This is an expected hardware constraint of local CPU execution.
2. **Single Active Emulated Device:** Demonstrations focus on device `ESP32_001`, although backend database schemas and MQTT wildcards support arbitrary multi-device scaling.
3. **MetroPT-3 Domain Differentiation:** MetroPT-3 is real train compressor data lacking vibration and humidity; it is used strictly for offline thermodynamic benchmark validation and does not feed the live pipeline.
4. **Local Alert Notifications:** Notifications are logged locally via `LocalNotificationService`; external SMS/Email webhooks are architectural stubs.
5. **Role Assignment during Registration:** In P19, the self-registration endpoint permits specifying the `ADMIN` role. Production deployment should restrict admin roles to internal administrative workflows.

---

## 22. Future Enhancements

The following extensions are identified as future work beyond Phase 24:
- **GPU Inference Acceleration:** Deploy Ollama on CUDA/Metal GPUs to reduce inference latency from ~40s to < 2s.
- **External Alert Notification Gateways:** Connect `NotificationService` to Twilio (SMS), SendGrid (Email), or enterprise Webhooks (Slack/Teams).
- **Physical Edge Hardware Deployment:** Flash genuine ESP32 boards equipped with DHT22, MPU6050, and CT sensors to publish live telemetry over Wi-Fi.
- **Streaming LLM Token Delivery:** Implement Server-Sent Events (SSE) / WebSockets to stream LLM diagnostic reasoning tokens directly to the React UI in real-time.
- **Enterprise SSO & RBAC:** Integrate OAuth2 / OpenID Connect (Keycloak / Okta) for enterprise identity federation.
