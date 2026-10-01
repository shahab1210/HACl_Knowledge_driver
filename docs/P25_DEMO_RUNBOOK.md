# P_311 — Final Presentation & Demo Runbook (Phase 25)

This runbook provides the exact, deterministic, and college-presentation-ready procedure for demonstrating the complete **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant** system.

---

## 1. System Startup Sequence (Steps 1–8)

Follow these steps in strict sequence. All services must be operational before starting the live demonstration.

```
PostgreSQL (5432) ──► Mosquitto (1883) ──► Ollama (11434)
                            │                   │
                            ▼                   ▼
                     Spring Boot (8080) ◄── Python AI Bridge (5001)
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
         React (5173)              Grafana (3000)
```

---

### Step 1 — Start PostgreSQL (Port 5432)
* **Command:**
  ```bash
  brew services start postgresql@18 || brew services start postgresql
  ```
* **Expected Output:**
  `Successfully started postgresql`
* **Health Check:**
  ```bash
  pg_isready -h localhost -p 5432
  # Expected: localhost:5432 - accepting connections
  ```
* **Troubleshooting:**
  If password prompt blocks scripts, export `PGPASSWORD=Arisha`. See [`docs/TROUBLESHOOTING.md`](file:///Users/shahabahmad/Documents/P_311/docs/TROUBLESHOOTING.md#issue-3).

---

### Step 2 — Start Mosquitto MQTT Broker (Port 1883)
* **Command:**
  ```bash
  brew services start mosquitto
  ```
* **Expected Output:**
  `Successfully started mosquitto`
* **Health Check:**
  ```bash
  nc -z -v -G 2 localhost 1883
  # Expected: Connection to localhost port 1883 succeeded!
  ```
* **Troubleshooting:**
  If port is refused, verify listener config in `/opt/homebrew/etc/mosquitto/mosquitto.conf`. See [`docs/TROUBLESHOOTING.md`](file:///Users/shahabahmad/Documents/P_311/docs/TROUBLESHOOTING.md#issue-5).

---

### Step 3 — Start Ollama Local LLM Server (Port 11434)
* **Command:**
  ```bash
  brew services start ollama || ollama serve &
  ```
* **Expected Output:**
  Daemon listening on `127.0.0.1:11434`.
* **Health Check:**
  ```bash
  curl -s http://localhost:11434/api/tags | grep -E "qwen2.5:1.5b|nomic-embed-text"
  # Expected: Lists both models as installed
  ```
* **Troubleshooting:**
  If models are missing: `ollama pull qwen2.5:1.5b` and `ollama pull nomic-embed-text`. See [`docs/TROUBLESHOOTING.md`](file:///Users/shahabahmad/Documents/P_311/docs/TROUBLESHOOTING.md#issue-4).

---

### Step 4 — Start Python AI Diagnosis Bridge (Port 5001)
* **Command:**
  ```bash
  cd /Users/shahabahmad/Documents/P_311
  ./ai/vector-db/.venv/bin/python3 ai/mqtt/src/server.py &
  ```
* **Expected Output:**
  `[AI Bridge] Running on http://0.0.0.0:5001`
* **Health Check:**
  ```bash
  curl -s http://localhost:5001/health
  # Expected: {"service": "ai-diagnosis-bridge", "status": "UP", ...}
  ```
* **Troubleshooting:**
  Verify ChromaDB collection `iot_fault_knowledge` is populated. See [`docs/TROUBLESHOOTING.md`](file:///Users/shahabahmad/Documents/P_311/docs/TROUBLESHOOTING.md#issue-2).

---

### Step 5 — Start Spring Boot Backend (Port 8080)
* **Command:**
  ```bash
  cd /Users/shahabahmad/Documents/P_311
  mvn spring-boot:run -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml &
  ```
* **Expected Output:**
  `Started IotFaultDiagnosisApplication in X.XXX seconds (process running for ...)`
* **Health Check:**
  ```bash
  curl -s -i http://localhost:8080/api/v1/auth/login
  # Expected: HTTP 400 Bad Request (Spring Security active and endpoint responding)
  ```
* **Troubleshooting:**
  If port 8080 is in use, kill conflicting PID: `lsof -ti:8080 | xargs kill -9`. See [`docs/TROUBLESHOOTING.md`](file:///Users/shahabahmad/Documents/P_311/docs/TROUBLESHOOTING.md#issue-1).

---

### Step 6 — Start React Frontend Dashboard (Port 5173)
* **Command:**
  ```bash
  cd /Users/shahabahmad/Documents/P_311/frontend
  npm run dev &
  ```
* **Expected Output:**
  `VITE v5.4.14 ready in XXX ms. Local: http://localhost:5173/`
* **Health Check:**
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5173
  # Expected: 200
  ```
* **Troubleshooting:**
  Ensure Node dependencies are installed via `npm install`.

---

### Step 7 — Start Grafana Operations Dashboard (Port 3000)
* **Command:**
  ```bash
  brew services start grafana
  ```
* **Expected Output:**
  `Successfully started grafana`
* **Health Check:**
  ```bash
  curl -s http://localhost:3000/api/health
  # Expected: {"commit": "...", "database": "ok", "version": "13.2.2"}
  ```
* **Troubleshooting:**
  Verify PostgreSQL datasource password in Grafana is `Arisha`. See [`docs/TROUBLESHOOTING.md`](file:///Users/shahabahmad/Documents/P_311/docs/TROUBLESHOOTING.md#issue-7).

---

### Step 8 — Start Python IoT Sensor Simulator
* **Command:**
  ```bash
  cd /Users/shahabahmad/Documents/P_311
  ./ai/vector-db/.venv/bin/python3 Iot_hcl_Python/mqtt_sender.py &
  ```
* **Expected Output:**
  `Connected to MQTT broker! Starting IoT sensor simulation... Published: {"device_id": "ESP32_001", ...}`
* **Health Check:**
  Check latest persisted reading in PostgreSQL:
  ```bash
  PGPASSWORD=Arisha psql -U postgres -h localhost -d iot_fault_diagnosis -c "SELECT device_id, temperature, vibration, current_value, recorded_at FROM sensor_readings ORDER BY id DESC LIMIT 1;"
  ```

---

## 2. 10–15 Minute Demo Script & Walkthrough

| Min | Step | Presentation Action | Demonstration Screen / Terminal | Key Speaking Point |
|:---:|:---|:---|:---|:---|
| **0–2** | **1. Architecture & Problem** | Open [`docs/ARCHITECTURE.md`](file:///Users/shahabahmad/Documents/P_311/docs/ARCHITECTURE.md) or slide overview. | Architecture diagram on screen. | "Industrial IoT operations require real-time anomaly detection coupled with transparent, explainable fault diagnosis. P_311 uses a dual-path design: a live IoT telemetry pipeline and an offline industrial validation path." |
| **2–3** | **2. Service Health Check** | Show terminal with 7 active ports or run health check script. | Terminal: `lsof -i:5432,1883,11434,5001,8080,5173,3000` | "All seven core subsystems run as decoupled services communicating over standard protocols: MQTT, HTTP REST, and PostgreSQL." |
| **3–4** | **3. MQTT Ingestion** | Show simulator publishing messages and Mosquitto broker log. | Terminal: simulator output publishing to `iot/ESP32_001/telemetry`. | "The ESP32 simulator sends JSON sensor packets over MQTT. Mosquitto dispatches them to Spring Boot's asynchronous subscriber with sub-15ms latency." |
| **4–5** | **4. PostgreSQL Telemetry** | Query PostgreSQL `sensor_readings` table. | Terminal: `psql` query showing newest rows. | "Spring Boot validates and persists incoming sensor readings in relational storage for downstream auditability and Grafana visualization." |
| **5–6** | **5. Abnormality Injection** | Switch simulator to abnormal scenario or publish abnormal payload. | Terminal: `python3 simulator/src/main.py --device ESP32_001 --scenario high_temp --burst 1` | "We simulate a critical industrial failure scenario: cooling fan failure causing temperature to spike past 85°C." |
| **6–7** | **6. Alert Generation** | Show alert generated in Spring Boot and query `alerts` table. | React Alert Banner or SQL `SELECT * FROM alerts ORDER BY created_at DESC LIMIT 1;` | "Spring Boot detects the threshold violation immediately (<5ms), generates a CRITICAL alert, and prevents duplicate alerts during persistent failure states." |
| **7–9** | **7. AI RAG Diagnosis Trigger** | Click **Run Manual Diagnosis** on React Dashboard or trigger API call. | React modal or API `POST /api/v1/diagnosis` | "The operator requests an AI diagnosis. Spring Boot delegates to the Python AI Bridge, providing current telemetry." |
| **9–10** | **8. Knowledge Retrieval (RAG)** | Show bridge retrieving top-k chunks from ChromaDB. | Terminal log: ChromaDB semantic search against `iot_fault_knowledge`. | "Rather than asking the LLM to guess, our RAG pipeline embeds the telemetry using `nomic-embed-text` and retrieves authoritative domain manual chunks." |
| **10–11** | **9. Structured LLM Output** | Show local LLM response formatted strictly into P12 schema. | React Diagnosis Detail view. | "`qwen2.5:1.5b` runs 100% locally via Ollama, generating primary fault, confidence (0.0–1.0), evidence, and recommended checks with zero cloud leakage." |
| **11–12** | **10. Relational Persistence** | Show diagnosis split across 7 normalized database tables. | Terminal: `SELECT primary_fault, confidence FROM diagnoses;` | "Diagnosis records are fully normalized in PostgreSQL, separating root causes, evidence, and knowledge source citations for audit compliance." |
| **12–13** | **11. Operator Dashboard** | Navigate React Dashboard (`http://localhost:5173`). | React Dashboard, Device Detail, History. | "Operators monitor live status, view telemetry trends, inspect cited knowledge manuals, and acknowledge active alerts with role-based access control." |
| **13–14** | **12. Grafana Operations View** | Open Grafana Operations Dashboard (`http://localhost:3000`). | Grafana 12-panel dashboard. | "Grafana provides real-time time-series telemetry trends, alert counts, and AI diagnosis latency metrics directly from PostgreSQL." |
| **14–15** | **13. MetroPT-3 Validation & Limitations** | Show [`docs/DATASET_DOCUMENTATION.md`](file:///Users/shahabahmad/Documents/P_311/docs/DATASET_DOCUMENTATION.md) and report. | Terminal: `python3 ai/dataset/metropt/src/analyzer.py` output. | "We independently validated our methodology against the MetroPT-3 real industrial dataset (1.5M rows), detecting all 4 documented compressor air-leak events." |

---

## 3. Demo Payloads (Supported & Tested)

### Payload 1: Normal Operation
```json
{
  "device_id": "ESP32_001",
  "temperature": 45.2,
  "vibration": 0.08,
  "current": 4.8,
  "pressure": 6.8,
  "humidity": 48.0
}
```
* **Expected Result:** Status NORMAL, Alert Count 0, Confidence High, Primary Fault: "NORMAL_OPERATION".

### Payload 2: High Temperature Abnormality (Cooling Failure)
```json
{
  "device_id": "ESP32_001",
  "temperature": 92.4,
  "vibration": 0.12,
  "current": 5.1,
  "pressure": 6.7,
  "humidity": 42.0
}
```
* **Expected Result:** Alert CRITICAL (Temperature 92.4 > 85.0°C), Primary Fault: "OVERHEATING_CRITICAL" or "COOLING_FAN_FAILURE", Recommended Check: "Inspect heat sink and verify cooling fan operation".

### Payload 3: High Vibration Abnormality (Bearing Defect)
```json
{
  "device_id": "ESP32_001",
  "temperature": 52.0,
  "vibration": 0.85,
  "current": 6.2,
  "pressure": 6.6,
  "humidity": 45.0
}
```
* **Expected Result:** Alert CRITICAL (Vibration 0.85 > 0.50 g), Primary Fault: "BEARING_WEAR" or "MECHANICAL_IMBALANCE", Recommended Check: "Check motor mountings and bearing lubrication".

### Payload 4: Combined Multi-Sensor Failure
```json
{
  "device_id": "ESP32_001",
  "temperature": 96.8,
  "vibration": 0.92,
  "current": 14.5,
  "pressure": 4.1,
  "humidity": 38.0
}
```
* **Expected Result:** Multiple Alerts (Temperature, Vibration, Current, Pressure), Primary Fault: "MOTOR_OVERLOAD_BEARING_FAILURE", Confidence: >0.85.

---

## 4. Live Demo Visual Checkpoints

### Checkpoint A: MQTT Telemetry Stream
* **Topic:** `iot/ESP32_001/telemetry`
* **Verified via CLI:**
  ```bash
  mosquitto_sub -h localhost -p 1883 -t "iot/+/telemetry" -v
  ```
* **Expected:** Continuous JSON stream every 2 seconds.

### Checkpoint B: PostgreSQL Persistence
* **Table:** `sensor_readings`
* **Query:**
  ```sql
  SELECT id, device_id, temperature, vibration, current_value, pressure, recorded_at 
  FROM sensor_readings ORDER BY id DESC LIMIT 3;
  ```

### Checkpoint C: Alert System
* **Table:** `alerts`
* **Query:**
  ```sql
  SELECT id, device_id, alert_type, severity, sensor_parameter, sensor_value, threshold_value, acknowledged 
  FROM alerts ORDER BY id DESC LIMIT 3;
  ```

### Checkpoint D: AI RAG Diagnosis Record
* **Table:** `diagnoses` join `diagnosis_knowledge_sources`
* **Query:**
  ```sql
  SELECT d.diagnosis_id, d.primary_fault_title, d.confidence_level, k.title, k.similarity
  FROM diagnoses d
  LEFT JOIN diagnosis_knowledge_sources k ON d.id = k.diagnosis_record_id
  ORDER BY d.created_at DESC LIMIT 3;
  ```

### Checkpoint E: React UI Inspection
* **URL:** `http://localhost:5173`
* **Credentials:** Username: `demo_operator`, Password: `Password123!`
* **Visual Elements:** Real-time telemetry cards, Latest Diagnosis card, Cited Manual excerpts, Alert badge, Diagnosis History table.

### Checkpoint F: Grafana Operations Monitoring
* **URL:** `http://localhost:3000`
* **Dashboard:** `P_311 — IoT Fault Diagnosis Operations`
* **Visual Elements:** Telemetry time-series graphs (Temperature, Vibration, Current, Pressure), Active Alert counts, Diagnosis Latency gauge, Diagnosis Fault Distribution pie chart.

---

## 5. Concise Concepts for Presentation & Viva

### RAG (Retrieval-Augmented Generation)
```
Live Telemetry ──► Formulate Query ──► nomic-embed-text (768d)
                                              │
                                              ▼
Local LLM (qwen2.5) ◄── Grounded Prompt ◄── ChromaDB Retrieval (Top-k Chunks)
        │
        ▼
Structured JSON Diagnosis (P12 Schema)
```
> *"RAG grounds the local LLM in authoritative engineering manuals before generating diagnoses. By retrieving verbatim chunks from ChromaDB, the system provides traceable evidence citations and minimizes hallucination without requiring fine-tuning."*

### MQTT Architecture
```
Publisher (ESP32 Simulator) ──[TCP:1883]──► Mosquitto Broker ──► Subscriber (Spring Boot)
```
> *"MQTT is an ultra-lightweight publish/subscribe protocol optimized for constrained IoT networks. It separates telemetry publishers from consumers, ensuring reliable asynchronous message buffering and sub-15ms processing."*

### MetroPT-3 Industrial Validation
```
Live Path:      ESP32 Simulator ──► MQTT ──► Spring Boot ──► PostgreSQL ──► UI / Grafana
Offline Path:   MetroPT-3 CSV (1.5M rows) ──► Pandas Validation ──► Failure Signatures Report
```
> *"MetroPT-3 is a real-world dataset from an urban passenger train compressor containing 1.5 million rows and 4 documented air-leak failures. We used it for offline validation to prove that compressor operating states and current/pressure correlations match real industrial behavior. It is intentionally isolated from the live simulator stream."*
