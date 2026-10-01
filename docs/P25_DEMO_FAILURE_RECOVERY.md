# P_311 — Presentation Emergency Failure Recovery Plan (Phase 25)

This document provides immediate, deterministic recovery procedures for presentation and viva demonstrations if any service fails or disconnects.

---

## Quick Reference Recovery Matrix

| Service | Port | Quick Check Command | Emergency Restart Command | Recovery Time |
|:---|:---:|:---|:---|:---:|
| **PostgreSQL** | 5432 | `pg_isready -h localhost -p 5432` | `brew services restart postgresql@18` | ~3 sec |
| **Mosquitto** | 1883 | `nc -z -v -G 2 localhost 1883` | `brew services restart mosquitto` | ~1 sec |
| **Ollama** | 11434 | `curl -s http://localhost:11434/api/tags` | `brew services restart ollama` | ~4 sec |
| **AI Bridge** | 5001 | `curl -s http://localhost:5001/health` | `./ai/vector-db/.venv/bin/python3 ai/mqtt/src/server.py &` | ~2 sec |
| **Spring Boot** | 8080 | `curl -s -i http://localhost:8080/api/v1/auth/login` | `lsof -ti:8080 \| xargs kill -9 && mvn spring-boot:run -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml &` | ~10 sec |
| **React** | 5173 | `curl -s http://localhost:5173` | `cd frontend && npm run dev &` | ~2 sec |
| **Grafana** | 3000 | `curl -s http://localhost:3000/api/health` | `brew services restart grafana` | ~3 sec |

---

## Detailed Service Recovery Procedures

### 1. PostgreSQL (Port 5432)
* **Failure Symptom:**
  - Spring Boot crashes on startup with `Cannot create PoolableConnectionFactory (Connection refused)`.
  - Terminal commands fail with `psql: error: connection to server at "localhost" failed`.
* **Quick Check:**
  ```bash
  pg_isready -h localhost -p 5432
  ```
* **Restart Command:**
  ```bash
  brew services restart postgresql@18 || brew services restart postgresql
  ```
* **Expected Recovery:**
  `pg_isready` reports `accepting connections`. Re-run any interrupted Spring Boot operations.

---

### 2. Mosquitto MQTT Broker (Port 1883)
* **Failure Symptom:**
  - Python simulator reports `ConnectionRefusedError: [Errno 61] Connection refused`.
  - Spring Boot logs `MqttException: Unable to connect to server`.
* **Quick Check:**
  ```bash
  nc -z -v -G 2 localhost 1883
  ```
* **Restart Command:**
  ```bash
  brew services restart mosquitto
  ```
* **Expected Recovery:**
  Spring Boot automatically reconnects to MQTT within 10 seconds. Simulator can immediately resume publishing.

---

### 3. Ollama LLM Service (Port 11434)
* **Failure Symptom:**
  - AI Bridge logs `requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=11434)`.
  - Diagnosis requests hang or trigger the deterministic fallback engine.
* **Quick Check:**
  ```bash
  curl -s http://localhost:11434/api/tags
  ```
* **Restart Command:**
  ```bash
  brew services restart ollama || (ollama serve &)
  ```
* **Expected Recovery:**
  `curl http://localhost:11434/api/tags` returns `qwen2.5:1.5b` and `nomic-embed-text:latest`.

---

### 4. Python AI Diagnosis Bridge (Port 5001)
* **Failure Symptom:**
  - React modal or Spring Boot returns `HTTP 503 Service Unavailable: AI Diagnosis Service is currently unreachable`.
* **Quick Check:**
  ```bash
  curl -s http://localhost:5001/health
  ```
* **Restart Command:**
  ```bash
  lsof -ti:5001 | xargs kill -9 2>/dev/null
  cd /Users/shahabahmad/Documents/P_311
  ./ai/vector-db/.venv/bin/python3 ai/mqtt/src/server.py &
  ```
* **Expected Recovery:**
  `curl http://localhost:5001/health` returns `{"status": "UP", "service": "ai-diagnosis-bridge"}`.

---

### 5. Spring Boot Application (Port 8080)
* **Failure Symptom:**
  - React displays `Unable to connect to Spring Boot backend`.
  - API returns HTTP 404 or connection refused on `localhost:8080`.
* **Quick Check:**
  ```bash
  curl -s -i http://localhost:8080/api/v1/auth/login
  ```
* **Restart Command:**
  ```bash
  lsof -ti:8080 | xargs kill -9 2>/dev/null
  cd /Users/shahabahmad/Documents/P_311
  mvn spring-boot:run -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml &
  ```
* **Expected Recovery:**
  Console outputs `Started IotFaultDiagnosisApplication in ...`. React immediately reconnects on page refresh.

---

### 6. React Frontend Application (Port 5173)
* **Failure Symptom:**
  - Browser displays `This site can’t be reached: localhost refused to connect`.
* **Quick Check:**
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5173
  ```
* **Restart Command:**
  ```bash
  lsof -ti:5173 | xargs kill -9 2>/dev/null
  cd /Users/shahabahmad/Documents/P_311/frontend
  npm run dev &
  ```
* **Expected Recovery:**
  Vite server starts within 500ms; reload browser at `http://localhost:5173`.

---

### 7. Grafana Operations Dashboard (Port 3000)
* **Failure Symptom:**
  - Browser reports connection refused on `http://localhost:3000`.
  - Dashboard panels show red exclamation marks.
* **Quick Check:**
  ```bash
  curl -s http://localhost:3000/api/health
  ```
* **Restart Command:**
  ```bash
  brew services restart grafana
  ```
* **Expected Recovery:**
  `curl http://localhost:3000/api/health` returns HTTP 200 `database: ok`.
