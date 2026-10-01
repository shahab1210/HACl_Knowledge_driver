# P_311 — Verified System Facts & Technical Parameters (Phase 25)

This document contains only strictly verified facts, counts, versions, and performance figures from the active **P_311** codebase and runtime environment.

---

## 1. Verified Software Versions & Environment

| Component | Verified Version | Configuration / Location |
|:---|:---|:---|
| **Java Compiler Target** | Java 21 (`<java.version>21</java.version>`) | Configured in `iot_hcl_spingboot/iot-fault-diagnosis/pom.xml` |
| **Java System Runtime** | OpenJDK 27 / Oracle Java 24 | `/opt/homebrew/Cellar/openjdk/27`, default `java -version` 24.0.2 |
| **Apache Maven** | 3.9.16 | Homebrew `/opt/homebrew/Cellar/maven/3.9.16` |
| **Python Runtime** | Python 3.14.2 | System & Virtualenv at `./ai/vector-db/.venv` |
| **Node.js** | v22.19.0 | Active runtime (`node -v`) |
| **npm** | 10.9.3 | Active CLI (`npm -v`) |
| **PostgreSQL Server** | 18.6 (Darwin 64-bit) | Database: `iot_fault_diagnosis`, Port: 5432 |
| **Mosquitto MQTT Broker** | 2.1.2 | Homebrew `/opt/homebrew/Cellar/mosquitto/2.1.2_1/sbin/mosquitto`, Port: 1883 |
| **Ollama Server** | 0.35.0 | Port: 11434 (`http://127.0.0.1:11434`) |
| **Grafana Server** | 13.2.2 | Port: 3000 (`http://localhost:3000`) |

---

## 2. Artificial Intelligence & Knowledge Base Specifications

| Parameter | Verified Value | Verification Source |
|:---|:---|:---|
| **Domain Knowledge Base Path** | `ai/knowledge-base/` | 18 structured Markdown files across `faults/` (10), `sensors/` (5), `procedures/` (3) |
| **Total Indexed Chunks** | 32 chunks | ChromaDB collection `iot_fault_knowledge` (`col.count()`) |
| **Vector Store Collection** | `iot_fault_knowledge` | ChromaDB PersistentClient at `ai/vector-db/data/chroma` |
| **Dense Embedding Model** | `nomic-embed-text:latest` | 768 dimensions, 8,192 token context window (274 MB) |
| **Generative LLM** | `qwen2.5:1.5b` | 1.54B parameters, Q4_K_M quantization (986 MB via Ollama) |
| **Vector Similarity Metric** | Cosine Distance ($1 - \cos(\theta)$) | ChromaDB HNSW space configuration |
| **Fallback Mechanism** | Deterministic Heuristic Engine | `ai/diagnosis/src/engine.py` rule-based safety net |

---

## 3. Network Architecture & Service Ports

| Service Name | Port | Protocol | Binding Address | Health Endpoint |
|:---|:---:|:---:|:---:|:---|
| **PostgreSQL** | 5432 | TCP (Postgres Wire) | `127.0.0.1` | `pg_isready -h localhost -p 5432` |
| **Mosquitto Broker** | 1883 | TCP (MQTT v3.1.1) | `0.0.0.0` | `nc -z -v -G 2 localhost 1883` |
| **Ollama Local LLM** | 11434 | HTTP / REST | `127.0.0.1` | `GET http://localhost:11434/api/tags` |
| **Python AI Bridge** | 5001 | HTTP / REST | `0.0.0.0` | `GET http://localhost:5001/health` |
| **Spring Boot Backend** | 8080 | HTTP / REST | `0.0.0.0` | `GET http://localhost:8080/api/v1/auth/login` |
| **React Frontend (Vite)** | 5173 | HTTP | `localhost / [::1]` | `GET http://localhost:5173` |
| **Grafana Dashboard** | 3000 | HTTP | `0.0.0.0` | `GET http://localhost:3000/api/health` |

---

## 4. Relational Database Schema (PostgreSQL 18.6)

Total Tables: **10** in database `iot_fault_diagnosis`:
1. `sensor_readings` (Time-series telemetry storage)
2. `diagnoses` (Primary diagnosis records with confidence and fault classifications)
3. `diagnosis_evidence` (Quantitative sensor evidence backing diagnosis)
4. `diagnosis_knowledge_sources` (Cited domain manual chunks and relevance scores)
5. `diagnosis_possible_causes` (Rank-ordered root cause hypotheses)
6. `diagnosis_recommended_checks` (Actionable inspection procedures)
7. `diagnosis_alternative_faults` (Secondary differential diagnoses)
8. `diagnosis_additional_info` (Arbitrary structured key-value metadata)
9. `users` (RBAC user accounts with BCrypt password hashes)
10. `alerts` (Threshold violation events with deduplication and acknowledgement flags)

---

## 5. Comprehensive Test Execution Stats

Total Automated Tests: **343 / 343 Passed (100% Pass Rate)**

| Subsystem | Test Framework | Test Count | Status | Execution Time |
|:---|:---|:---:|:---:|:---:|
| **Python Ingestion** | pytest | 22 | PASS | 0.05s |
| **Python Vector DB** | pytest | 23 | PASS | 1.49s |
| **Python Embeddings** | pytest | 24 | PASS | 0.12s |
| **Python LLM Integration** | pytest | 47 | PASS | 0.19s |
| **Python RAG Pipeline** | pytest | 30 | PASS | 2.50s |
| **Python Diagnosis Engine** | pytest | 23 | PASS | 0.03s |
| **Python MQTT Bridge** | pytest | 29 | PASS | 2.13s |
| **Python End-to-End Live** | pytest | 19 | PASS | 68.19s |
| **Python MetroPT-3 Validation**| pytest | 14 | PASS | 2.63s |
| **Subtotal Python AI** | **pytest 9.1.1** | **231** | **PASS** | **~77s** |
| **Spring Boot Backend** | Maven / JUnit 5 | 70 | PASS | ~14s |
| **React Frontend** | Vitest / Testing Library | 42 | PASS | ~5.4s |
| **Total Automated Tests** | | **343** | **PASS** | **~97s** |

---

## 6. Empirical Performance Benchmarks

| Metric / Pipeline Step | Measured Real Value | Conditions / Notes |
|:---|:---:|:---|
| **MQTT Ingestion Latency** | 8 – 15 ms | Publisher to Spring Boot JPA insert |
| **Alert Detection Latency** | < 5 ms | In-memory evaluation during telemetry ingest |
| **AI LLM Inference (CPU)** | 32.6 – 50.2 s | `qwen2.5:1.5b` executed via Ollama on Apple Silicon CPU |
| **LLM Cold Start Delay** | ~8.6 s | Initial loading of model weights into system RAM |
| **Database Diagnosis Insert** | 12 – 25 ms | Normalized write across 7 relational tables |
| **Grafana Query Latency** | 4 – 18 ms | Indexed SQL queries against PostgreSQL 18.6 |
| **MetroPT-3 Processing Speed** | 6.40 s | Pandas loading, cleaning, state classifying 1,516,948 rows |

---

## 7. MetroPT-3 Real Industrial Dataset Facts

- **Total Rows:** 1,516,948 observations (sampled at 1 Hz from an active passenger train APU).
- **Total Features:** 16 physical and electrical columns (0 null values).
- **Signals Included:** Pneumatic pressures (`TP2`, `TP3`, `H1`, `DV_pressure`, `Reservoirs`), motor electrical current (`Motor_current`), oil temperature (`Oil_temperature`), and electrical state flags (`COMP`, `DV_eletric`, `Towers`, `MPG`, `LPS`, `Pressure_switch`, `Oil_level`, `Caudal_impulses`).
- **Signals Omitted by Physical Design:** Humidity and Vibration (never instrumented by transit authority).
- **Operating States Discovered:** Standby (54.65%), Offloaded (32.06%), UnderLoad (13.29%).
- **Ground Truth Failures Detected:** 4 of 4 documented air leak failure events (April 18, May 29, June 5, July 15, 2020).
