# P_311 — Troubleshooting & Diagnostic Guide

This guide documents verified troubleshooting procedures for issues encountered during development, startup, and testing of **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant**.

---

## Issue 1: Port 8080 Occupied by Foreign Java Application

### Problem Symptom
Spring Boot fails to start or endpoints return HTTP 500 / unexpected schemas from a different application.
### Root Cause
Another Java project (e.g., `/Users/shahabahmad/hcl-main/backend` or another daemon) is running on port 8080.
### Solution
Identify and terminate the conflicting process:
```bash
# Check PID listening on 8080
lsof -i :8080

# Terminate foreign process
kill -9 <PID>

# Restart P_311 Spring Boot application
mvn spring-boot:run -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml &
```
### Verification
```bash
curl -s -i http://localhost:8080/api/v1/auth/health
```

---

## Issue 2: AI Diagnosis Bridge Unreachable (Port 5001 Connection Refused)

### Problem Symptom
Calling `POST /api/v1/diagnosis` returns `HTTP 503 Service Unavailable`:
*"AI Diagnosis Service is currently unreachable at http://localhost:5001. Ensure the P13 AI bridge is running."*
### Root Cause
The persistent Python HTTP server bridge (`ai/mqtt/src/server.py`) has not been started.
### Solution
Start the AI bridge using the project virtual environment:
```bash
./ai/vector-db/.venv/bin/python3 ai/mqtt/src/server.py &
```
### Verification
```bash
curl -s http://localhost:5001/health
# Expected: {"status": "UP", "service": "ai-diagnosis-bridge", ...}
```

---

## Issue 3: PostgreSQL Authentication Prompt Hanging Commands

### Problem Symptom
Terminal commands using `psql` hang indefinitely waiting for manual password entry.
### Root Cause
PostgreSQL user `shahabahmad` requires password authentication as configured in `application.properties`.
### Solution
Export the database password in the command environment:
```bash
export PGPASSWORD=Arisha
psql -h localhost -U shahabahmad -d iot_fault_diagnosis -c "SELECT count(*) FROM diagnoses;"
```
### Verification
PostgreSQL executes the query non-interactively and returns table statistics.

---

## Issue 4: Ollama Service Offline or Missing Required Models

### Problem Symptom
AI Bridge or tests report `requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=11434)` or `model not found`.
### Root Cause
Ollama is not running locally or the models `qwen2.5:1.5b` or `nomic-embed-text` have not been pulled into local storage.
### Solution
Start the Ollama daemon and pull the models:
```bash
# Start Ollama
ollama serve &

# Pull required models
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```
### Verification
```bash
curl -s http://localhost:11434/api/tags
# Expected: JSON containing "qwen2.5:1.5b" and "nomic-embed-text:latest"
```

---

## Issue 5: Mosquitto MQTT Connection Refused (Port 1883)

### Problem Symptom
Spring Boot logs `Unable to connect to server: Connection refused` or Python simulator fails to connect.
### Root Cause
The Mosquitto broker service is stopped.
### Solution
Start Mosquitto:
```bash
brew services start mosquitto
```
### Verification
```bash
nc -z -v -G 2 localhost 1883
# Expected: Connection to localhost port 1883 succeeded!
```

---

## Issue 6: Module Name Collisions when Running Batch `pytest` across all Subsystems

### Problem Symptom
Running `pytest ai/` in one single invocation fails with `import file mismatch: imported module 'test_validator' has this __file__ attribute...`.
### Root Cause
Multiple decoupled subsystems (`ai/ingestion/`, `ai/mqtt/`, `ai/diagnosis/`, `ai/dataset/metropt/`) independently define top-level module names like `models.py`, `validator.py`, and `test_validator.py`.
### Solution
Execute test suites individually per package or use the provided test runner loop:
```bash
for d in ai/ingestion ai/vector-db ai/embeddings ai/llm ai/rag ai/diagnosis ai/mqtt ai/integration ai/dataset/metropt; do
  ./ai/vector-db/.venv/bin/pytest "$d/tests" -q
done
```
### Verification
All 9 test suites execute cleanly and independently without module namespace collisions.

---

## Issue 7: Grafana PostgreSQL Datasource Authentication Failure

### Problem Symptom
Grafana displays error: `pq: password authentication failed for user "shahabahmad"` on panel queries.
### Root Cause
The PostgreSQL datasource password in Grafana does not match `spring.datasource.password=Arisha`.
### Solution
Update datasource configuration in Grafana (`http://localhost:3000/datasources`):
- Host: `localhost:5432`
- Database: `iot_fault_diagnosis`
- User: `shahabahmad`
- Password: `Arisha`
- SSL Mode: `disable`
### Verification
Run [`scripts/verify_grafana_dashboard.py`](file:///Users/shahabahmad/Documents/P_311/scripts/verify_grafana_dashboard.py).
