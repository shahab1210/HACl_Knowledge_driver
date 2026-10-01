# P_311 — System Setup & Deployment Guide

This guide provides exact step-by-step instructions to initialize and run the complete **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant** system.

---

## 1. Prerequisites & Environment Versions

Ensure the following runtimes and tools are installed:

| Tool | Verified Version | Purpose |
| :--- | :--- | :--- |
| **Java JDK** | OpenJDK 27 runtime (pom.xml targets Java 21) | Spring Boot backend compilation and execution |
| **Apache Maven** | 3.9+ | Backend build & dependency manager |
| **Python** | Python 3.14 (or 3.11+) | AI/RAG engine, data validation, simulator |
| **Node.js & npm** | Node v22+ (v18+ LTS) | React frontend build toolchain |
| **PostgreSQL** | PostgreSQL 18.6 (or 16+) | Relational data store (database `iot_fault_diagnosis`) |
| **Eclipse Mosquitto** | Mosquitto 2.0+ | Lightweight MQTT messaging broker |
| **Ollama** | Latest local version | Local LLM and embedding server |
| **Grafana** | Grafana 10+ / 13+ | Infrastructure and operations dashboard |

---

## 2. Directory Structure Overview

```text
P_311/
├── Iot_hcl_Python/            # Python edge sensor simulator (mqtt_sender.py)
├── ai/                        # AI & RAG subsystems
│   ├── ingestion/             # Document parsing and chunking
│   ├── embeddings/            # Embedding generation
│   ├── vector-db/             # ChromaDB vector collection & virtual environment
│   ├── llm/                   # Ollama LLM integration
│   ├── rag/                   # Semantic query and retrieval pipeline
│   ├── diagnosis/             # DiagnosisEngine & output parsing
│   ├── mqtt/                  # MQTT worker & AI HTTP bridge server (port 5001)
│   └── dataset/metropt/       # Offline MetroPT-3 industrial validation pipeline
├── iot_hcl_spingboot/         # Spring Boot backend application
├── frontend/                  # React / Vite operator dashboard
├── scripts/                   # Verification and QA audit scripts
└── docs/                      # Technical documentation
```

---

## 3. Step-by-Step Service Startup

### Step 1: Start PostgreSQL
Ensure PostgreSQL is active on port `5432` and database `iot_fault_diagnosis` is initialized:

```bash
# Start PostgreSQL (macOS Homebrew example)
brew services start postgresql@16

# Verify database connection
PGPASSWORD=Arisha psql -h localhost -U shahabahmad -d iot_fault_diagnosis -c "\dt"
```

### Step 2: Start Eclipse Mosquitto MQTT Broker
Ensure Mosquitto is active on port `1883`:

```bash
# Start Mosquitto
brew services start mosquitto

# Verify port 1883 is listening
nc -z -v -G 2 localhost 1883
```

### Step 3: Start Ollama & Pull Required Models
Ensure Ollama daemon is running on port `11434` and the verified models are downloaded:

```bash
# Start Ollama service (if not already running as desktop app)
ollama serve &

# Pull required LLM and Embedding models
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text

# Verify loaded models
curl -s http://localhost:11434/api/tags
```

### Step 4: Prepare Python Virtual Environment & Start AI Bridge
The Python AI subsystems share the virtual environment in `ai/vector-db/.venv`:

```bash
# Activate virtual environment
source ai/vector-db/.venv/bin/activate

# Install requirements
pip install -r ai/vector-db/requirements.txt
pip install -r ai/dataset/metropt/requirements.txt

# Start AI Diagnosis HTTP Bridge on port 5001
./ai/vector-db/.venv/bin/python3 ai/mqtt/src/server.py &

# Verify AI Bridge healthcheck
curl -s http://localhost:5001/health
```

### Step 5: Start Spring Boot Backend
Start the Java backend application on port `8080`:

```bash
# Run Spring Boot via Maven wrapper or installed Maven
mvn spring-boot:run -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml &

# Verify Spring Boot application startup
curl -s -i http://localhost:8080/api/v1/auth/health
```

### Step 6: Start React Operator Frontend
Start the Vite development server on port `5173`:

```bash
cd frontend
npm install
npm run dev &
cd ..

# Verify React frontend is accessible
curl -s -I http://localhost:5173
```

### Step 7: Start Grafana Operations Dashboard
Ensure Grafana is active on port `3000`:

```bash
# Start Grafana
brew services start grafana

# Verify Grafana health
curl -s http://localhost:3000/api/health

# Run automated dashboard query verification script
python3 scripts/verify_grafana_dashboard.py
```

### Step 8: Start Python IoT Sensor Simulator
To publish continuous real-time telemetry into the live pipeline:

```bash
./ai/vector-db/.venv/bin/python3 Iot_hcl_Python/mqtt_sender.py
```

---

## 4. Running the Offline Industrial Validation Pipeline (MetroPT-3)

The MetroPT-3 benchmark pipeline runs independently of the live MQTT streaming services:

```bash
# Run full MetroPT-3 validation pipeline (processes 1.51M observations & generates 6 figures)
./ai/vector-db/.venv/bin/python3 ai/dataset/metropt/src/run_pipeline.py
```

Outputs will be generated in `ai/dataset/metropt/output/`:
- `dataset_summary.json`
- `feature_summary.json`
- `anomaly_summary.json`
- `validation_report.md`
- `plots/*.png` (6 analytical figures)

---

## 5. Running Full Automated Test Suites

To verify end-to-end regression across all tiers:

```bash
# 1. Run all Python AI and MetroPT tests (231 tests)
for d in ai/ingestion ai/vector-db ai/embeddings ai/llm ai/rag ai/diagnosis ai/mqtt ai/integration ai/dataset/metropt; do
  ./ai/vector-db/.venv/bin/pytest "$d/tests" -q
done

# 2. Run Spring Boot backend tests (70 tests)
mvn test -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml

# 3. Run React frontend tests (42 tests)
cd frontend && npm test -- --run && cd ..
```
