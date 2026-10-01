# P_311: Knowledge-Driven IoT Fault Diagnosis Assistant

[![Java](https://img.shields.io/badge/Java-27-orange.svg)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-4.1.1-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![MQTT](https://img.shields.io/badge/MQTT-Mosquitto%202.0-red.svg)](https://mosquitto.org/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/Local%20LLM-Ollama%20qwen2.5-black.svg)](https://ollama.ai/)
[![Tests](https://img.shields.io/badge/Tests-343%2F343%20Passed-success.svg)](#testing)

An end-to-end industrial software and artificial intelligence platform designed to ingest, monitor, persist, alert, and diagnose multi-channel IoT sensor telemetry using **Retrieval-Augmented Generation (RAG)** grounded in technical maintenance manuals.

---

## 1. System Architecture

The platform maintains two logically isolated pipelines:

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

## 2. Key Features

- **Multi-Channel MQTT Ingestion:** Ingests high-frequency telemetry (temperature, vibration, current, pressure, humidity) from edge simulators via Mosquitto.
- **Relational Persistence:** Persists sensor streams and full diagnosis entity graphs across 10 PostgreSQL tables.
- **Grounded AI Diagnosis (RAG):** Eliminates hallucinations by retrieving relevant engineering troubleshooting chunks from ChromaDB using `nomic-embed-text` embeddings.
- **Local LLM Inference:** Generates structured diagnostic reasoning locally using `qwen2.5:1.5b` via Ollama with zero external cloud dependencies.
- **Automated Threshold Alerting:** Detects abnormal conditions with a 60-second duplicate suppression cooldown and authenticated operator acknowledgement.
- **Dual Visual Cockpits:** Responsive React/Vite operator dashboard on port `5173` and an infrastructure operations dashboard in Grafana on port `3000` (13 panels).
- **Real Industrial Dataset Validation:** Offline benchmark pipeline validating compressor duty cycles and air leak failures against 1.51M observations from the **MetroPT-3** railway dataset.

---

## 3. Technology Stack

| Tier | Technologies Used |
| :--- | :--- |
| **Edge / IoT** | Python 3.14, Paho MQTT Client, Eclipse Mosquitto (port 1883) |
| **Backend** | Java 27, Spring Boot 4.1.1, Spring Data JPA, Spring Security (JWT), Hibernate 7.4 |
| **Database** | PostgreSQL 16 (port 5432) |
| **AI / RAG** | ChromaDB, Ollama (`qwen2.5:1.5b`, `nomic-embed-text`), Pydantic, Python HTTP Bridge (port 5001) |
| **Frontend** | React 18, Vite, Tailwind CSS, Axios, Lucide Icons (port 5173) |
| **Observability** | Grafana 13 (port 3000), Direct PostgreSQL Datasource |
| **Validation** | Pandas 3.0, NumPy 2.5, Matplotlib 3.11 (MetroPT-3 benchmark) |

---

## 4. Repository Structure

```text
P_311/
├── README.md                  # This file
├── docs/                      # Comprehensive technical documentation (P24 & P25)
│   ├── P24_PROJECT_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── SETUP_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── AI_RAG_DOCUMENTATION.md
│   ├── DATASET_DOCUMENTATION.md
│   ├── TESTING_DOCUMENTATION.md
│   ├── TROUBLESHOOTING.md
│   ├── VIVA_NOTES.md
│   ├── P25_DEMO_RUNBOOK.md
│   ├── P25_PROJECT_CONTRIBUTION.md
│   ├── P25_DEMO_FAILURE_RECOVERY.md
│   ├── P25_FINAL_CHECKLIST.md
│   ├── P25_PROJECT_FACTS.md
│   └── P25_FINAL_DEMO_REPORT.md
├── Iot_hcl_Python/            # Sensor simulator (mqtt_sender.py)
├── iot_hcl_spingboot/         # Spring Boot backend application
├── frontend/                  # React / Vite operator dashboard
├── ai/                        # AI & RAG subsystems
│   ├── ingestion/             # Document parsing & chunking
│   ├── embeddings/            # Vector embeddings
│   ├── vector-db/             # ChromaDB vector collection
│   ├── llm/                   # Ollama LLM integration
│   ├── rag/                   # Query & context retrieval
│   ├── diagnosis/             # Structured DiagnosisEngine
│   ├── mqtt/                  # MQTT worker & AI HTTP bridge (port 5001)
│   └── dataset/metropt/       # Offline MetroPT-3 validation pipeline
└── scripts/                   # Verification and QA scripts
```

---

## 5. Quickstart

### 1. Prerequisites
- Java JDK 27, Maven 3.9+, Python 3.14+, Node.js 18+, PostgreSQL 16, Mosquitto, Ollama, Grafana.

### 2. Start Services
```bash
# 1. Start PostgreSQL (Port 5432)
brew services start postgresql@16

# 2. Start Mosquitto MQTT (Port 1883)
brew services start mosquitto

# 3. Start Ollama and pull models (Port 11434)
ollama serve &
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text

# 4. Start Python AI Bridge (Port 5001)
./ai/vector-db/.venv/bin/python3 ai/mqtt/src/server.py &

# 5. Start Spring Boot Backend (Port 8080)
mvn spring-boot:run -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml &

# 6. Start React Frontend (Port 5173)
cd frontend && npm run dev & cd ..

# 7. Start Grafana (Port 3000)
brew services start grafana
```

### 3. Publish Simulated Telemetry
```bash
./ai/vector-db/.venv/bin/python3 Iot_hcl_Python/mqtt_sender.py
```

### 4. Run Offline MetroPT-3 Validation
```bash
./ai/vector-db/.venv/bin/python3 ai/dataset/metropt/src/run_pipeline.py
```

---

## 6. Testing

The repository maintains **343 automated tests** passing at 100%:

```bash
# Python AI & MetroPT-3 tests (231 tests)
for d in ai/ingestion ai/vector-db ai/embeddings ai/llm ai/rag ai/diagnosis ai/mqtt ai/integration ai/dataset/metropt; do
  ./ai/vector-db/.venv/bin/pytest "$d/tests" -q
done

# Spring Boot tests (70 tests)
mvn test -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml

# React frontend tests (42 tests)
cd frontend && npm test -- --run && cd ..
```

---

## 7. Documentation Index

For complete architectural and technical details, refer to the documents in [`docs/`](docs/):
- **[`docs/P24_PROJECT_DOCUMENTATION.md`](docs/P24_PROJECT_DOCUMENTATION.md)**: Main project documentation and phase history.
- **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)**: Subsystem architecture and message flow sequences.
- **[`docs/SETUP_GUIDE.md`](docs/SETUP_GUIDE.md)**: Complete step-by-step setup and operational runbook.
- **[`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)**: Full REST API endpoint specification.
- **[`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md)**: PostgreSQL table schemas, constraints, and ER diagrams.
- **[`docs/AI_RAG_DOCUMENTATION.md`](docs/AI_RAG_DOCUMENTATION.md)**: Dense retrieval, ChromaDB vector store, and LLM prompting.
- **[`docs/DATASET_DOCUMENTATION.md`](docs/DATASET_DOCUMENTATION.md)**: MetroPT-3 benchmark analysis, signals, and failure validation.
- **[`docs/TESTING_DOCUMENTATION.md`](docs/TESTING_DOCUMENTATION.md)**: Comprehensive quality assurance metrics.
- **[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)**: Common failure modes, port conflicts, and resolutions.
- **[`docs/VIVA_NOTES.md`](docs/VIVA_NOTES.md)**: 42 oral examination questions and answers.
- **[`docs/P25_DEMO_RUNBOOK.md`](docs/P25_DEMO_RUNBOOK.md)**: Deterministic 10–15 minute presentation script and payload runbook.
- **[`docs/P25_FRONTEND_TEST_GUIDE.md`](docs/P25_FRONTEND_TEST_GUIDE.md)**: Manual browser-based testing guide with verified URLs and checklists.
- **[`docs/P25_PROJECT_CONTRIBUTION.md`](docs/P25_PROJECT_CONTRIBUTION.md)**: Summary of technical contributions and innovations.
- **[`docs/P25_DEMO_FAILURE_RECOVERY.md`](docs/P25_DEMO_FAILURE_RECOVERY.md)**: Quick-restart disaster recovery procedures.
- **[`docs/P25_FINAL_CHECKLIST.md`](docs/P25_FINAL_CHECKLIST.md)**: Pre-presentation checklist and backup strategy.
- **[`docs/P25_PROJECT_FACTS.md`](docs/P25_PROJECT_FACTS.md)**: Verified parameters, benchmarks, and dataset statistics.
- **[`docs/P25_FINAL_DEMO_REPORT.md`](docs/P25_FINAL_DEMO_REPORT.md)**: Final verification status and environment audit.
