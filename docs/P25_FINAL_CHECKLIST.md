# P_311 — Final Presentation Checklist & Backup Strategy (Phase 25)

This checklist serves as the authoritative operational verification guide before, during, and after academic or technical demonstrations.

---

## 1. Pre-Presentation Verification Checklist

Complete this checklist at least 30 minutes before presentation commencement:

### Infrastructure & Services
- [x] **Project Directory:** Root directory verified at `/Users/shahabahmad/Documents/P_311`.
- [x] **PostgreSQL (Port 5432):** Running (`PostgreSQL 18.6`); password verified as `Arisha`.
- [x] **Mosquitto (Port 1883):** Daemon running and accepting TCP connections.
- [x] **Ollama (Port 11434):** Running locally; models `qwen2.5:1.5b` and `nomic-embed-text` verified via `ollama list`.
- [x] **ChromaDB Vector Store:** Collection `iot_fault_knowledge` populated at `ai/vector-db/data/chroma`.
- [x] **AI Diagnosis Bridge (Port 5001):** Active at `http://localhost:5001/health`.
- [x] **Spring Boot (Port 8080):** Compiled and running with active Spring Security JWT filter.
- [x] **React Frontend (Port 5173):** Vite development server running; assets compiled.
- [x] **Grafana (Port 3000):** Dashboard `P_311 — IoT Fault Diagnosis Operations` open and connected to PostgreSQL.

### Data & Credentials
- [x] **Operator Credentials:** Username: `demo_operator`, Password: `Password123!` (Role: `ADMIN`).
- [x] **Demo Target Device:** `ESP32_001` configured and verified.
- [x] **Demo Payloads:** Normal, High-Temp, High-Vibration, and Multi-Sensor payloads tested and ready in [`docs/P25_DEMO_RUNBOOK.md`](file:///Users/shahabahmad/Documents/P_311/docs/P25_DEMO_RUNBOOK.md).
- [x] **MetroPT-3 Validation Report:** `docs/P22_METROPT3_VALIDATION_REPORT.md` and dataset scripts verified.
- [x] **Documentation Pack:** All 10 documentation files in `docs/` and root `README.md` verified.
- [x] **Emergency Backup:** Local archive created following the backup strategy below.

---

## 2. Live Presentation Execution Checklist

Follow this linear sequence during the 10–15 minute live presentation:

- [ ] **1. Problem & Context:** State the challenge of ungrounded LLMs in mission-critical industrial maintenance.
- [ ] **2. System Architecture:** Present the dual-path design (Live IoT stream vs. Offline MetroPT-3 validation).
- [ ] **3. Live Telemetry:** Start simulator on scenario `normal`; display terminal stream on `iot/ESP32_001/telemetry`.
- [ ] **4. Relational Storage:** Execute SQL query demonstrating real-time row insertion into `sensor_readings`.
- [ ] **5. Inject Abnormality:** Trigger scenario `high_temp` (temperature > 85°C).
- [ ] **6. Demonstrate Alert:** Show immediate (<5ms) CRITICAL alert creation in terminal/React banner and explain deduplication cooldown.
- [ ] **7. Trigger AI Diagnosis:** Click **Run Manual Diagnosis** in React dashboard (or execute `POST /api/v1/diagnosis`).
- [ ] **8. Explain RAG Workflow:** Walk through `nomic-embed-text` vector embedding and ChromaDB top-$k$ manual retrieval.
- [ ] **9. Inspect Structured Output:** Review primary fault, confidence score, evidence citations, and recommended inspection steps.
- [ ] **10. Demonstrate Persistence:** Query PostgreSQL `diagnoses` and child tables to prove database normalization.
- [ ] **11. Operator Web UI:** Tour React dashboard: telemetry cards, live alerts, manual triggers, and RBAC logout/login.
- [ ] **12. Operations Observability:** Demonstrate Grafana 12-panel dashboard: time-range filtering, device variables, and diagnosis metrics.
- [ ] **13. Industrial Dataset (MetroPT-3):** Present the 1.5M-row railway compressor analysis and explain why vibration/humidity are omitted.
- [ ] **14. Limitations & Defense:** Discuss CPU LLM inference latency (~30-50s) and outline production GPU/TimescaleDB scaling steps.

---

## 3. Safe Project Backup Strategy

To ensure zero risk of accidental data loss or environment corruption, execute the following non-destructive snapshot script.

### What is Included in Backup:
1. Complete Git source code repository.
2. Domain knowledge base markdown documents (`ai/ingestion/data/`).
3. ChromaDB vector database index files (`ai/vector-db/data/chroma/`).
4. PostgreSQL database schema definition (`docs/DATABASE_SCHEMA.md` and pg_dump DDL).
5. Spring Boot and Vite configuration files.
6. Complete `docs/` technical documentation suite.
7. MetroPT-3 analysis scripts and summary outputs.

*(Note: Sensitive runtime passwords and giant temporary log files are excluded).*

### Backup Command (Run in terminal):
```bash
# Create timestamped presentation backup archive
BACKUP_DIR="/Users/shahabahmad/Documents/P_311_BACKUP_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 1. Export PostgreSQL schema & data (excluding passwords from script)
PGPASSWORD=Arisha pg_dump -U postgres -h localhost -d iot_fault_diagnosis -F c -b -v -f "$BACKUP_DIR/iot_fault_diagnosis.dump"

# 2. Export database DDL schema in plain text
PGPASSWORD=Arisha pg_dump -U postgres -h localhost -d iot_fault_diagnosis --schema-only -f "$BACKUP_DIR/schema.sql"

# 3. Copy source files, configuration, and documentation
rsync -av --progress \
  --exclude 'target/' \
  --exclude 'node_modules/' \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude '.git/' \
  /Users/shahabahmad/Documents/P_311/ "$BACKUP_DIR/codebase/"

echo "Backup complete at: $BACKUP_DIR"
```
