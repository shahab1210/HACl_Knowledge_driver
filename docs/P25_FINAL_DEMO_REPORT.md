# P_311 — Final Presentation & Demo Report (Phase 25)

## 1. P25 STATUS: COMPLETE

The demonstration preparation, live subsystem health verification, presentation runbook, failure recovery plan, viva voce notes, and cross-document consistency audit are completed and verified against the live environment.

---

## 2. Environment (Verified Runtimes & Configurations)

- **Java JDK Target:** Java 21 (`<java.version>21</java.version>` in `pom.xml`)
- **Java System Runtime:** OpenJDK 27 (`/opt/homebrew/Cellar/openjdk/27`) / Oracle Java 24 (`24.0.2+12-54`)
- **Apache Maven:** 3.9.16
- **Python:** Python 3.14.2 (virtual environment at `./ai/vector-db/.venv`)
- **Node.js & npm:** Node v22.19.0, npm 10.9.3
- **PostgreSQL Server:** PostgreSQL 18.6 (Darwin 64-bit), database `iot_fault_diagnosis`
- **Mosquitto MQTT Broker:** 2.1.2 (listening on port 1883)
- **Ollama Local LLM Runtime:** 0.35.0 (serving `qwen2.5:1.5b` and `nomic-embed-text:latest`)
- **Grafana Dashboard Server:** 13.2.2 (listening on port 3000)

---

## 3. Subsystem Health Status

| Service Name | Port | Protocol | PID / Process | HTTP / Socket Status | Verified Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| **PostgreSQL** | 5432 | TCP | Homebrew service | `accepting connections` | **UP (PASS)** |
| **Mosquitto** | 1883 | MQTT | PID 723 | Port 1883 open & listening | **UP (PASS)** |
| **Ollama** | 11434 | HTTP | PID 742 | `http://localhost:11434/api/tags` 200 OK | **UP (PASS)** |
| **Python AI Bridge** | 5001 | HTTP | PID 8302 | `http://localhost:5001/health` UP (200 OK) | **UP (PASS)** |
| **Spring Boot** | 8080 | HTTP | PID 8255 | `http://localhost:8080/api/v1/auth/login` 400 | **UP (PASS)** |
| **React Frontend** | 5173 | HTTP | PID 3907 | `http://localhost:5173` 200 OK | **UP (PASS)** |
| **Grafana** | 3000 | HTTP | PID 735 | `http://localhost:3000/api/health` 200 OK | **UP (PASS)** |

---

## 4. Verification Checkpoint Results

- **Demo Scenario:** **PASS** (10–15 minute deterministic 14-step walkthrough documented in [`docs/P25_DEMO_RUNBOOK.md`](file:///Users/shahabahmad/Documents/P_311/docs/P25_DEMO_RUNBOOK.md)).
- **Telemetry:** **PASS** (Live MQTT publish on `iot/ESP32_001/telemetry` ingested into PostgreSQL `sensor_readings` ID 998 with sub-18ms latency).
- **Alerts:** **PASS** (Threshold violation detected; CRITICAL alert ID 66 generated in `alerts` table in 18ms; acknowledged via authenticated REST API).
- **AI Diagnosis:** **PASS** (Executed live `POST /api/v1/diagnosis` with Bearer JWT token; returned diagnosis `diag-ESP32_001-1790835660376` in 44.237s).
- **RAG Pipeline:** **PASS** (Retrieved top-3 relevant knowledge chunks from ChromaDB collection `iot_fault_knowledge` with similarity scores 0.768–0.781; cited in response).
- **React Frontend:** **PASS** (Vite server active on `http://localhost:5173`; 42/42 Vitest unit and context tests passing; authenticated login and dashboard views operational).
- **Grafana Dashboard:** **PASS** (Active on `http://localhost:3000`; 12 panels verified with live PostgreSQL queries and zero syntax errors).
- **MetroPT-3 Validation:** **PASS** (14/14 automated tests passing; offline validation of 1,516,948 rows and 4 ground-truth leak failures verified in 6.40s).
- **Documentation:** **PASS** (All P24 and P25 documentation files complete, cross-linked, and verified).
- **Viva Preparation:** **PASS** (42 comprehensive questions and answers categorized across 11 technical areas in [`docs/VIVA_NOTES.md`](file:///Users/shahabahmad/Documents/P_311/docs/VIVA_NOTES.md)).
- **Final Consistency:** **PASS** (All ports, versions, database column names, and collection names reconciled across documentation and code).

---

## 5. Issues Encountered & Resolved

1. **ChromaDB Collection Name Discrepancy:**  
   *Issue:* Documentation referenced `fault_diagnosis_kb`, whereas `ai/vector-db/config.py` and the persistent Chroma store use `iot_fault_knowledge` (32 indexed chunks across 18 domain files).  
   *Resolution:* Updated all documentation references to `iot_fault_knowledge`.
2. **Java Runtime vs. Compilation Target:**  
   *Issue:* Documentation stated "Java 27" without qualification.  
   *Resolution:* Clarified that Maven executes with system OpenJDK 27 while `pom.xml` strictly specifies `<java.version>21</java.version>` target compatibility.
3. **PostgreSQL Version Alignment:**  
   *Issue:* Legacy documents referred to PostgreSQL 16.  
   *Resolution:* Verified live server version as PostgreSQL 18.6 and updated all documentation.
4. **Relational Database Column Names in Queries:**  
   *Issue:* Initial runbook queries referenced `current` and `timestamp` in `sensor_readings`, and `primary_fault` / `confidence` in `diagnoses`.  
   *Resolution:* Reconciled runbook SQL with actual PostgreSQL columns (`current_value`, `recorded_at`, `primary_fault_title`, `confidence_level`, `reading_value`, and foreign key `diagnosis_record_id`).
5. **Simulator CLI Path:**  
   *Issue:* Conceptual path `simulator/src/main.py` was referenced in initial runbook draft.  
   *Resolution:* Corrected to actual project simulator file `Iot_hcl_Python/mqtt_sender.py`.

---

## 6. Documented Limitations (Honest Presentation Boundaries)

1. **CPU LLM Inference Latency:** Local Ollama inference with `qwen2.5:1.5b` takes 32.6s to 50.2s per diagnosis on CPU (Apple Silicon unaccelerated threads). Cold-start initial inference requires an additional ~8.6s memory allocation.
2. **Single-Node Relational Storage:** PostgreSQL 18 is running as a single-node database; high-frequency multi-device partitioning (TimescaleDB hypertables) remains a future enhancement.
3. **MetroPT-3 Sensor Coverage:** The railway APU dataset does not include vibration or humidity sensors, which is explicitly maintained to avoid synthetic sensor fabrication.
