# 🔗 P_311 — ALL TEST LINKS

Below are the **actual, currently implemented and verified URLs** for manual browser-based verification:

| Category | Service / Page | Verified URL | Notes |
|:---|:---|:---|:---|
| **Frontend** | **React Master Dashboard** | `http://localhost:5173/` | Main operator dashboard (requires login) |
| **Frontend** | **User Login** | `http://localhost:5173/login` | Public authentication page |
| **Frontend** | **User Registration** | `http://localhost:5173/register` | Public account creation page |
| **Frontend** | **Device Detail View** | `http://localhost:5173/device/ESP32_001` | Specific IoT device history & trends |
| **Frontend** | **Diagnosis Detail View** | `http://localhost:5173/diagnosis/diag-ESP32_001-1790835660376` | Verified real persisted diagnosis ID |
| **Observability** | **Grafana Console** | `http://localhost:3000` | Login: `admin` / `admin` |
| **Observability** | **Grafana Operations Dashboard**| `http://localhost:3000/d/p311-operations` | 13 live telemetry and AI panels |
| **Backend AI** | **AI Bridge Health Probe** | `http://localhost:5001/health` | Returns JSON `{"status": "UP"}` |
| **Backend LLM**| **Ollama Model Catalog** | `http://localhost:11434/api/tags` | Lists `qwen2.5:1.5b` & `nomic-embed-text` |
| **Backend API**| **Spring Boot Security Probe** | `http://localhost:8080/api/v1/auth/login` | Responds with HTTP 400 (server active) |

---

# 1. React Application Routes

The React application runs on port `5173` via Vite. Routes are declared in `frontend/src/App.jsx`:

| Page | URL | Login Required | What I Should See |
|:---|:---|:---:|:---|
| **Login** | `http://localhost:5173/login` | **No** | Clean industrial login card with Username/Email and Password inputs, and link to Register. |
| **Register** | `http://localhost:5173/register` | **No** | Registration form with Username, Email, Password, and Role selection dropdown (`USER` or `ADMIN`). |
| **Dashboard** | `http://localhost:5173/` | **Yes** | Complete operator cockpit: KPI metrics, Active Alerts banner, Latest Diagnosis card, Telemetry cards, Telemetry Trend Chart, Primary Fault analysis, Evidence, Knowledge Sources, and Diagnosis History. |
| **Device Detail** | `http://localhost:5173/device/ESP32_001` | **Yes** | Device header badge, current sensor readings grid, historical telemetry line chart, and historical diagnoses table filtered to `ESP32_001`. |
| **Diagnosis Detail**| `http://localhost:5173/diagnosis/<id>` | **Yes** | Deep-dive record view: Primary fault, confidence level, telemetry snapshot, quantitative evidence rows, cited knowledge source chunks with similarity scores, and execution metadata. |
| **Wildcard Catch** | `http://localhost:5173/*` | **Yes** | Automatically redirects any undefined route back to `http://localhost:5173/`. |

> **How to obtain a real Diagnosis `<id>`:**
> 1. Look at the **Persisted Diagnosis History** table on the Main Dashboard (`http://localhost:5173/`) and click on any row or "View Details" button.
> 2. Query PostgreSQL directly in terminal:
>    ```bash
>    PGPASSWORD=Arisha psql -U postgres -h localhost -d iot_fault_diagnosis -c "SELECT diagnosis_id FROM diagnoses ORDER BY id DESC LIMIT 1;"
>    ```
> 3. Use the verified live diagnosis ID: `diag-ESP32_001-1790835660376`.

---

# 2. Main Dashboard Test Checklist (`http://localhost:5173/`)

When you open `http://localhost:5173/` while authenticated, verify each of the following components:

### 1. API Status & Header
* **EXPECTED:** Top navigation bar displays "IoT Fault Diagnosis P_311", current username/role badge, a green "API Online" status pill, "Manual Diagnosis" button, and "Sign Out" button.
* **TEST:** Look at top right header.
* **RESULT:** Green indicator confirms Spring Boot backend on port 8080 is reachable.

### 2. Auto-Poll Control
* **EXPECTED:** Toggle labeled "Auto-Poll (10s)" with active checkbox in top-right controls.
* **TEST:** Toggle the checkbox off and on.
* **RESULT:** Disables or enables 10-second background polling of `/api/v1/diagnosis/latest` and `/api/v1/alerts`.

### 3. KPI Summary Grid
* **EXPECTED:** 4 KPI stat cards:
  1. *Connection Status:* "Connected" (green indicator).
  2. *Monitored Device:* "ESP32_001" (clickable link to `/device/ESP32_001`).
  3. *Diagnostic Certainty:* Confidence badge ("LOW", "MEDIUM", or "HIGH").
  4. *Stored Diagnoses:* Total count of records in PostgreSQL.
* **TEST:** Click on the device link `ESP32_001`.
* **RESULT:** Smoothly navigates to `http://localhost:5173/device/ESP32_001`.

### 4. Industrial Alerts & Notifications Widget (P20)
* **EXPECTED:** If unacknowledged alerts exist, a prominent alert banner appears showing alert type (`SENSOR_THRESHOLD`), severity badge (`CRITICAL` red or `WARNING` yellow), parameter breaching threshold, limit value, timestamp, and an "Acknowledge" button.
* **TEST:** Click "Acknowledge" on any active alert.
* **RESULT:** The alert card transitions to acknowledged state with an operator name stamp.

### 5. Latest Diagnosis Card
* **EXPECTED:** Card displaying primary fault title (e.g., "Bearing Overheating" or "General Diagnosis"), confidence rating badge, latency in seconds (e.g., `44.24s`), MQTT topic (`iot/ESP32_001/telemetry`), and relative timestamp.
* **TEST:** Inspect card header and timestamp.
* **RESULT:** Matches the newest record persisted in PostgreSQL.

### 6. Real-Time Telemetry Grid
* **EXPECTED:** 5 responsive sensor cards:
  - **Temperature:** e.g., `96.5 °C`
  - **Humidity:** e.g., `40.0 %`
  - **Vibration:** e.g., `7.8 mm/s`
  - **Current:** e.g., `11.2 A`
  - **Pressure:** e.g., `2.0 bar`
* **TEST:** Verify values match the telemetry recorded during the latest diagnosis.
* **RESULT:** Colored status indicator (green for normal, amber/red for thresholds).

### 7. Historical Telemetry Progression Chart
* **EXPECTED:** Multi-line SVG chart tracking temperature, vibration, current, and pressure over historical diagnosis evaluations.
* **TEST:** Hover cursor over chart data points.
* **RESULT:** Interactive tooltips display parameter values at specific timestamps.

### 8. Primary Fault & Diagnostic Analysis
* **EXPECTED:** Natural language query submitted to LLM followed by full markdown diagnostic reasoning explaining the thermal, electrical, and hydraulic findings.
* **TEST:** Read explanation text.
* **RESULT:** Text is generated by local `qwen2.5:1.5b` grounded in the retrieved engineering manuals.

### 9. Quantitative Evidence Section
* **EXPECTED:** Table listing parameter names, observed readings, physical units, and telemetry source tags.
* **TEST:** Verify evidence parameters.
* **RESULT:** Matches the exact values received from the sensor reading.

### 10. Knowledge Sources Table (RAG Citations)
* **EXPECTED:** Table listing the top-3 retrieved engineering chunks from ChromaDB:
  - *Rank:* 1, 2, 3
  - *Document ID:* e.g., `SENSOR-TEMPERATURE`, `SENSOR-HUMIDITY`
  - *Chunk ID:* e.g., `SENSOR-TEMPERATURE_chunk_002`
  - *Title:* Technical manual chapter title
  - *Source File:* Relative path in `ai/knowledge-base/`
  - *Similarity Score:* Cosine similarity (e.g., `0.7815`, `0.7729`)
* **TEST:** Inspect similarity scores.
* **RESULT:** Proves local vector search retrieved authoritative technical documentation.

### 11. Recommended Checks & Actionable Steps
* **EXPECTED:** Actionable checklist for maintenance technicians (e.g., "Check bearing lubrication", "Inspect heatsink mounting").
* **TEST:** Read recommended procedures.
* **RESULT:** Provides structured corrective actions directly relevant to the fault.

### 12. Generation Details Card
* **EXPECTED:** Technical LLM execution metrics:
  - *Model:* `qwen2.5:1.5b`
  - *Total Duration:* e.g., `42.94s`
  - *Prompt Evaluation Tokens:* e.g., `2,376 tokens`
  - *Evaluation Tokens:* e.g., `526 tokens`
* **TEST:** Confirm metrics are non-zero.
* **RESULT:** Confirms genuine local Ollama token generation.

### 13. Persisted Diagnosis History Table
* **EXPECTED:** Tabular log of historical diagnoses with timestamp, device ID, primary fault, confidence badge, latency, and a "View Details" button.
* **TEST:** Click "View Details" on any row.
* **RESULT:** Opens `http://localhost:5173/diagnosis/<id>`.

---

# 3. Login & Authentication Flow

* **Login URL:** `http://localhost:5173/login`

### Existing Documented User Accounts
The following verified test accounts exist in the PostgreSQL `users` table:

| Username | Password | Role | Description |
|:---|:---|:---:|:---|
| `demo_operator` | `Password123!` | `ADMIN` | Primary demonstration account (created in P25 facts) |
| `chief_operator`| `ChiefPassword123` | `ADMIN` | Secondary operator account (used in automated QA scripts) |

### Step-by-Step Test Procedure:
1. **Open Login Page:** Navigate to `http://localhost:5173/login`.
2. **Enter Credentials:** Type `demo_operator` in the Username/Email field and `Password123!` in Password.
3. **Submit:** Click "Sign In".
4. **Confirm Dashboard Opens:** URL changes to `http://localhost:5173/` and header displays `demo_operator (ADMIN)`.
5. **Test Protected Route Redirection:**
   - Open a private/incognito browser window.
   - Navigate directly to `http://localhost:5173/device/ESP32_001` or `http://localhost:5173/`.
   - **CONFIRM:** React Router immediately intercepts the unauthenticated session and redirects to `http://localhost:5173/login`.
6. **Test Logout:**
   - On the authenticated dashboard, click the "Sign Out" button in the top right.
   - **CONFIRM:** JWT token is cleared from `localStorage` and page redirects to `/login`.
7. **Test Post-Logout Protection:**
   - Press the browser "Back" button.
   - **CONFIRM:** Protected content does not load; you remain on `/login`.

---

# 4. User Registration Flow

* **Registration URL:** `http://localhost:5173/register`

### Field Specifications:
- **Username:** *Required*, string (minimum 3 characters).
- **Email:** *Required*, valid email containing `@` and `.` (e.g., `operator2@factory.com`).
- **Password:** *Required*, string (minimum 6 characters).
- **Account Role:** Dropdown selector:
  - `USER`: Standard operator (monitoring and alerts).
  - `ADMIN`: Administrator (on-demand AI triggers, alert acknowledgements).

### Step-by-Step Test Procedure:
1. Navigate to `http://localhost:5173/register` (or click "Create an account" on the login page).
2. **Test Validation 1 (Short Password):** Enter `new_user`, `new@test.com`, password `123`. Click "Register".  
   *EXPECTED ERROR:* Banner displays `"Password must be at least 6 characters long."`
3. **Test Validation 2 (Invalid Email):** Enter `new_user`, `invalidemail`, password `Secret123`.  
   *EXPECTED ERROR:* Banner displays `"Please provide a valid email address."`
4. **Successful Registration:** Enter:
   - Username: `operator_test`
   - Email: `operator_test@factory.com`
   - Password: `Password123!`
   - Role: `ADMIN`
   - Click "Register".
5. **CONFIRM:** Registration automatically issues a JWT Bearer token, authenticates the session, and navigates directly to `http://localhost:5173/`.

> **⚠️ Known Production Security Limitation:**  
> The self-registration form allows any registrant to assign themselves the `ADMIN` role from the dropdown selector. In an enterprise production deployment, role assignment would be restricted to administrative invitation or LDAP/SSO synchronization.

---

# 5. Device Detail Page Test

* **Device URL:** `http://localhost:5173/device/ESP32_001`

### What to Test:
1. **Navigation:** Click on `ESP32_001` anywhere in the dashboard, or type `http://localhost:5173/device/ESP32_001` in the address bar.
2. **Header Information:**
   - "Back to Dashboard" link.
   - "Device: ESP32_001" cyan identifier badge.
3. **Latest Telemetry Cards:** Displays the most recent sensor values for `ESP32_001`.
4. **Historical Telemetry Chart:** Renders time-series trends specific to device `ESP32_001`.
5. **Device Diagnosis History Table:** Displays historical AI diagnoses strictly filtered to `ESP32_001`.
6. **Back Navigation:** Click "Back to Dashboard" -> confirms return to `http://localhost:5173/`.

---

# 6. Diagnosis Detail Page Test

* **Direct URL:** `http://localhost:5173/diagnosis/diag-ESP32_001-1790835660376`

### How to Access:
- Click "View Details" on the first row of the Diagnosis History Table on the Main Dashboard, or paste the direct URL above into your browser.

### What Should Appear on the Page:
1. **Header Bar:** "Back to Dashboard" link and "Record ID: diag-ESP32_001-1790835660376".
2. **Diagnosis Overview Card:**
   - Primary Fault title.
   - Confidence level badge (`LOW` with explanation tooltip).
   - Execution latency badge (e.g., `44.24s`).
   - Device ID and evaluation timestamp.
3. **Telemetry Snapshot Grid:** All 5 physical parameters recorded at the instant of diagnosis:
   - Temperature: `96.5 °C`
   - Humidity: `40.0 %`
   - Vibration: `7.8 mm/s`
   - Current: `11.2 A`
   - Pressure: `2.0 bar`
4. **Primary Fault Card:** Full diagnostic reasoning text explaining why temperature is critical and why hydraulic/environmental signals are within normal envelopes.
5. **Quantitative Evidence Table:** 5 verified sensor evidence rows with parameters, values, and units.
6. **Knowledge Sources Table:**
   - Citations of `sensors/temperature.md` (similarity `0.7815` and `0.7729`).
   - Citation of `sensors/humidity.md` (similarity `0.7683`).
7. **Actionable Checklist:** Recommended inspection steps for mechanical bearings and lubrication.
8. **Generation Metrics:** Model name `qwen2.5:1.5b`, token count, and total inference duration.

---

# 7. Live On-Demand AI Diagnosis Test (Frontend UI)

Trigger a real-time AI fault diagnosis directly from the browser:

### Step-by-Step UI Procedure:
1. On the Main Dashboard (`http://localhost:5173/`), click the **"Manual Diagnosis"** button in the top navigation bar.
2. The **"Trigger On-Demand AI Diagnosis"** modal will open with prefilled parameters:
   - Device Identifier: `ESP32_001`
   - Temperature: `92.5`
   - Vibration: `14.8`
   - Current: `28.5`
   - Humidity: `45.0`
   - Pressure: `2.1`
3. Click the cyan **"Run AI Diagnosis"** button at the bottom of the modal.
4. **Expected UI Behavior:**
   - Button changes to a spinning indicator: *"Running local AI diagnosis (qwen2.5:1.5b via Ollama)... Typically takes 30-50s on CPU."*
   - **Expected Duration:** Approximately **35 to 50 seconds** (CPU-based local LLM token generation).
5. **Completion:**
   - The modal automatically closes.
   - The Main Dashboard instantly refreshes with the newly generated diagnosis.
   - New primary fault, confidence badge, latency gauge, and RAG knowledge citations appear.
   - The new diagnosis row is added to the top of the **Persisted Diagnosis History** table.

### Verification in PostgreSQL (Terminal):
```bash
PGPASSWORD=Arisha psql -U postgres -h localhost -d iot_fault_diagnosis -c "
SELECT diagnosis_id, device_id, confidence_level, latency_seconds, created_at 
FROM diagnoses 
ORDER BY id DESC LIMIT 1;
"
```

---

# 8. Real-Time Alert Generation & Acknowledgement Test

### Step 1: Inject Abnormal Telemetry via MQTT
Open your terminal and run this one-line command to publish a high-temperature threshold violation:

```bash
./ai/vector-db/.venv/bin/python3 -c "
import paho.mqtt.client as mqtt, json
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect('localhost', 1883)
payload = {
    'device_id': 'ESP32_001',
    'temperature': 98.4,
    'humidity': 38.0,
    'vibration': 8.5,
    'current': 12.0,
    'pressure': 1.9
}
client.publish('iot/ESP32_001/telemetry', json.dumps(payload))
client.disconnect()
print('Abnormal MQTT telemetry published successfully!')
"
```

### Step 2: Observe Live Reaction in React Frontend
1. Keep `http://localhost:5173/` open in your browser.
2. Within 10 seconds (or immediately upon clicking the Refresh icon in the header), observe the **Industrial Alerts & Notifications** widget at the top of the page.
3. **What You Should See:**
   - A red **CRITICAL** alert card appears.
   - Parameter: `current` or `temperature`.
   - Observed value: `98.4 °C` or `12.0 A` exceeding safety limit.
   - Red pulsing indicator.
   - "Acknowledge" button with a checkmark icon.

### Step 3: Acknowledge the Alert from the UI
1. Click the **"Acknowledge"** button on the alert card.
2. **What You Should See:**
   - The card immediately updates.
   - A green badge appears: `Acknowledged by demo_operator`.
   - The acknowledge button is replaced by a verified timestamp.

### Step 4: Verify in PostgreSQL (Terminal):
```bash
PGPASSWORD=Arisha psql -U postgres -h localhost -d iot_fault_diagnosis -c "
SELECT id, device_id, alert_type, severity, sensor_parameter, sensor_value, threshold_value, acknowledged, acknowledged_by 
FROM alerts 
ORDER BY id DESC LIMIT 1;
"
```

---

# 9. Grafana Operations Dashboard Test

* **Grafana URL:** `http://localhost:3000`
* **Direct Dashboard URL:** `http://localhost:3000/d/p311-operations`
* **Default Credentials:** Username: `admin`, Password: `admin`

### Panel Verification Checklist (All 13 Panels):

| Panel ID | Panel Title | Visualization Type | What to Check in Browser |
|:---:|:---|:---:|:---|
| **1** | **Latest Temperature** | Stat Gauge | Shows latest reading (e.g. `96.5°C`), colored green/orange/red based on threshold. |
| **2** | **Latest Humidity** | Stat Gauge | Shows current humidity (e.g. `40.0%`). |
| **3** | **Latest Vibration** | Stat Gauge | Shows current vibration (e.g. `7.8 mm/s`). |
| **4** | **Latest Current** | Stat Gauge | Shows motor current (e.g. `11.2 A`). |
| **5** | **Latest Pressure** | Stat Gauge | Shows pneumatic pressure (e.g. `2.0 bar`). |
| **6** | **Total Stored Diagnoses** | Stat Counter | Number matches total rows in PostgreSQL `diagnoses` table. |
| **7** | **Real-Time Telemetry Trend** | Multi-Line Timeseries | Continuous historical curves for Temperature, Vibration, Current, and Pressure. |
| **8** | **AI Diagnosis Latency Progression**| Timeseries Line | Execution time progression per diagnosis (typically 30–50s). |
| **9** | **Primary Fault Classification** | Bar Chart | Frequency distribution of detected fault types across the device fleet. |
| **10**| **Diagnosis Confidence Distribution**| Donut / Pie Chart | Breakdown of diagnoses by confidence level (`low`, `medium`, `high`). |
| **11**| **Persisted AI Fault Diagnosis History**| Data Table | Tabular log of diagnosis records with timestamps, device IDs, and faults. |
| **12**| **PostgreSQL Database Storage Health**| Data Table | Disk usage bytes and row counts for `sensor_readings`, `diagnoses`, `alerts`. |
| **13**| **System Alerts & Notifications** | Data Table | Historical log of threshold alerts, severity, and acknowledgement status. |

> **Dashboard Controls to Test:**
> - **Device Variable Filter:** Click the `$device_id` dropdown in the top left; switch between `ESP32_001` and other devices.
> - **Time Range:** Switch the top right picker between `Last 15 minutes`, `Last 1 hour`, and `Last 24 hours`.

---

# 10. Backend Health & Service Status URLs

Open these URLs in your browser or run via `curl` to verify background service health:

| Service | Browser-Accessible URL | Expected Response |
|:---|:---|:---|
| **Python AI Bridge** | `http://localhost:5001/health` | `{"service": "ai-diagnosis-bridge", "status": "UP", "timestamp": ...}` |
| **Ollama LLM Engine**| `http://localhost:11434/api/tags` | JSON containing `qwen2.5:1.5b` and `nomic-embed-text:latest` |
| **Grafana Server** | `http://localhost:3000/api/health` | `{"commit": "...", "database": "ok", "version": "13.2.2"}` |
| **React Development**| `http://localhost:5173` | Vite development server serving single-page application |
| **Spring Boot Auth** | `http://localhost:8080/api/v1/auth/login` | HTTP 400 Bad Request (confirms Spring Security is active) |

---

# 11. Backend REST API Testing Guide

Use curl or Postman to test the backend API controllers:

### 1. Register Account
- **METHOD:** `POST`
- **URL:** `http://localhost:8080/api/v1/auth/register`
- **Authentication:** None (Public)
- **Request:**
  ```json
  {
    "username": "api_tester",
    "email": "tester@factory.com",
    "password": "Password123!",
    "role": "ADMIN"
  }
  ```
- **Expected Response:** HTTP 201 Created with JSON containing `token`, `username`, `role`, `expiresInSeconds`.

### 2. Login & Obtain JWT Token
- **METHOD:** `POST`
- **URL:** `http://localhost:8080/api/v1/auth/login`
- **Authentication:** None (Public)
- **Request:**
  ```json
  {
    "username": "demo_operator",
    "password": "Password123!"
  }
  ```
- **Expected Response:** HTTP 200 OK with `token: "eyJhbGciOiJIUzUxMiJ9..."`.

### 3. Get Current User Profile
- **METHOD:** `GET`
- **URL:** `http://localhost:8080/api/v1/auth/me`
- **Authentication:** `Authorization: Bearer <TOKEN>`
- **Expected Response:** HTTP 200 OK with user profile details.

### 4. Fetch Latest Diagnosis
- **METHOD:** `GET`
- **URL:** `http://localhost:8080/api/v1/diagnosis/latest`
- **Authentication:** `Authorization: Bearer <TOKEN>`
- **Expected Response:** HTTP 200 OK with complete structured diagnosis JSON.

### 5. Fetch Diagnosis by ID
- **METHOD:** `GET`
- **URL:** `http://localhost:8080/api/v1/diagnosis/diag-ESP32_001-1790835660376`
- **Authentication:** `Authorization: Bearer <TOKEN>`
- **Expected Response:** HTTP 200 OK matching the specific diagnosis record.

### 6. Fetch Diagnoses for Device
- **METHOD:** `GET`
- **URL:** `http://localhost:8080/api/v1/diagnosis/device/ESP32_001`
- **Authentication:** `Authorization: Bearer <TOKEN>`
- **Expected Response:** HTTP 200 OK with array of historical diagnoses.

### 7. Trigger On-Demand AI Diagnosis
- **METHOD:** `POST`
- **URL:** `http://localhost:8080/api/v1/diagnosis`
- **Authentication:** `Authorization: Bearer <TOKEN>`
- **Request:**
  ```json
  {
    "deviceId": "ESP32_001",
    "temperature": 96.5,
    "vibration": 7.8,
    "current": 11.2,
    "pressure": 2.0,
    "humidity": 40.0
  }
  ```
- **Expected Response:** HTTP 201 Created with new diagnosis JSON (after 30-50s LLM execution).

### 8. Fetch Alerts
- **METHOD:** `GET`
- **URL:** `http://localhost:8080/api/v1/alerts?acknowledged=false`
- **Authentication:** `Authorization: Bearer <TOKEN>`
- **Expected Response:** HTTP 200 OK with array of active unacknowledged alerts.

### 9. Acknowledge Alert
- **METHOD:** `POST`
- **URL:** `http://localhost:8080/api/v1/alerts/66/acknowledge`
- **Authentication:** `Authorization: Bearer <TOKEN>`
- **Expected Response:** HTTP 200 OK with `acknowledged: true`, `acknowledgedBy: "demo_operator"`.

---

# 12. Complete 17-Step Manual Test Flow

Follow this sequence to test the entire system step-by-step:

```
[TEST 01] Open Browser at http://localhost:5173/
   ↓
[TEST 02] Verify redirection to /login
   ↓
[TEST 03] Login using demo_operator / Password123!
   ↓
[TEST 04] Verify Dashboard loads with KPI cards and header
   ↓
[TEST 05] Click device link to view http://localhost:5173/device/ESP32_001
   ↓
[TEST 06] Publish normal telemetry via simulator
   ↓
[TEST 07] Verify updated readings on Dashboard
   ↓
[TEST 08] Publish abnormal telemetry (temperature > 85°C)
   ↓
[TEST 09] Verify critical alert banner appears in React
   ↓
[TEST 10] Click Acknowledge button on the alert card
   ↓
[TEST 11] Verify alert status updates to Acknowledged
   ↓
[TEST 12] Click Manual Diagnosis button and submit form
   ↓
[TEST 13] Wait ~40s and verify newly generated diagnosis appears
   ↓
[TEST 14] Open diagnosis detail at http://localhost:5173/diagnosis/<id>
   ↓
[TEST 15] Inspect RAG knowledge sources and similarity scores
   ↓
[TEST 16] Open Grafana at http://localhost:3000/d/p311-operations
   ↓
[TEST 17] Logout from React and confirm protected routes redirect
```

---

# 13. Comprehensive Manual Verification Table (20 Tests)

Use this table to record your manual test results:

| # | Test Case Description | User Action to Perform | Expected System Behavior | Result (PASS / FAIL) |
|:---:|:---|:---|:---|:---:|
| **T01** | **Unauthenticated Route Guard** | Open `http://localhost:5173/` in private tab. | Immediately redirected to `/login`. | |
| **T02** | **Invalid Login Validation** | Enter invalid password on `/login`. | Displays error: "Invalid username or password". | |
| **T03** | **Successful Login** | Enter `demo_operator` / `Password123!`. | Redirects to `/` with operator username badge. | |
| **T04** | **Registration Password Check** | Try registering with 3-char password. | Form displays: "Password must be at least 6 characters". | |
| **T05** | **New User Registration** | Register with valid unique username. | Automatically logs in and opens Dashboard. | |
| **T06** | **Backend Connectivity Pill** | Check top header pill on Dashboard. | Displays green "API Online" badge. | |
| **T07** | **Auto-Refresh Polling** | Toggle "Auto-Poll (10s)" checkbox. | Network tab polls `/api/v1/alerts` every 10s. | |
| **T08** | **Device Page Routing** | Click `ESP32_001` link on Dashboard. | Navigates to `/device/ESP32_001`. | |
| **T09** | **Device Telemetry Chart** | Inspect chart on `/device/ESP32_001`. | Multi-line SVG chart renders time-series lines. | |
| **T10** | **MQTT Simulator Ingestion** | Run `mqtt_sender.py` in terminal. | Terminal logs published JSON packets every 5s. | |
| **T11** | **Telemetry Persistence** | Query `sensor_readings` in PostgreSQL. | New sensor rows appear with millisecond timestamp. | |
| **T12** | **Alert Threshold Violation** | Publish payload with temperature `98.4°C`. | Red CRITICAL alert card appears in React. | |
| **T13** | **Alert UI Acknowledgement** | Click "Acknowledge" button in alert widget. | Badge turns green: "Acknowledged by <user>". | |
| **T14** | **Manual Diagnosis Modal Open** | Click "Manual Diagnosis" in header. | Modal dialog opens with pre-filled inputs. | |
| **T15** | **On-Demand AI Execution** | Click "Run AI Diagnosis" inside modal. | Loading spinner appears; executes for ~35–50s. | |
| **T16** | **Diagnosis Result Rendering** | Inspect Dashboard after modal closes. | New primary fault and confidence badge appear. | |
| **T17** | **RAG Knowledge Citations** | Inspect Knowledge Sources card. | Displays 3 chunks with similarity scores > 0.75. | |
| **T18** | **Diagnosis Detail View** | Open `/diagnosis/<id>` in browser. | Full page opens with evidence and reasoning. | |
| **T19** | **Grafana Dashboard Access** | Open `http://localhost:3000/d/p311-operations`. | 13 panels load with live data and zero errors. | |
| **T20** | **Session Logout** | Click "Sign Out" button in header. | Token cleared; redirected to `/login`. | |

---

# 14. Operational Troubleshooting

### 1. Frontend Doesn't Open (`localhost:5173 refused to connect`)
* **Check:** Vite development server status.
* **Command:** `lsof -i :5173`
* **Restart Command:** `cd frontend && npm run dev &`
* **Expected Result:** `VITE v5.4.14 ready in XXX ms. Local: http://localhost:5173/`

### 2. Login Fails with "Invalid username or password"
* **Check:** Account existence in PostgreSQL `users` table.
* **Command:** `PGPASSWORD=Arisha psql -U postgres -h localhost -d iot_fault_diagnosis -c "SELECT username, role FROM users;"`
* **Resolution:** Use `demo_operator` with `Password123!` or create a new account at `http://localhost:5173/register`.

### 3. Dashboard Displays "API Offline" or "Spring Boot API Connection Error"
* **Check:** Spring Boot process on port 8080.
* **Command:** `lsof -i :8080`
* **Restart Command:** `mvn spring-boot:run -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml &`
* **Expected Result:** `Started IotFaultDiagnosisApplication in ...`

### 4. Telemetry Doesn't Update on Dashboard
* **Check:** Mosquitto MQTT broker status and simulator execution.
* **Command:** `nc -z -v -G 2 localhost 1883`
* **Restart Command:** `brew services restart mosquitto`
* **Simulator Command:** `./ai/vector-db/.venv/bin/python3 Iot_hcl_Python/mqtt_sender.py &`

### 5. Diagnosis Request Takes 40–50 Seconds
* **Explanation:** This is **normal and expected**. `qwen2.5:1.5b` executes on local CPU hardware using quantized inference via Ollama without dedicated GPU acceleration.
* **Verification:** Check AI bridge status at `http://localhost:5001/health`.

### 6. Alert Doesn't Appear in React Widget
* **Check:** Threshold criteria (temperature must exceed 85.0°C or current exceed 10.5A) and deduplication cooldown.
* **Command:** `PGPASSWORD=Arisha psql -U postgres -h localhost -d iot_fault_diagnosis -c "SELECT * FROM alerts ORDER BY id DESC LIMIT 3;"`
* **Resolution:** Click the manual "Refresh" icon on the Alerts widget header in the UI.

### 7. Grafana Panels Display "No Data" or Red Exclamation Mark
* **Check:** PostgreSQL datasource authentication in Grafana.
* **Resolution:** Ensure password for user `postgres` / `shahabahmad` in Grafana datasource is set to `Arisha`. Run `python3 scripts/verify_grafana_dashboard.py`.

---

# 🔗 P_311 — ALL TEST LINKS (Summary)

```text
Main Dashboard:
http://localhost:5173/

Login:
http://localhost:5173/login

Register:
http://localhost:5173/register

Device Page:
http://localhost:5173/device/ESP32_001

Diagnosis Detail:
http://localhost:5173/diagnosis/diag-ESP32_001-1790835660376

Grafana Operations Dashboard:
http://localhost:3000/d/p311-operations

Python AI Bridge Health:
http://localhost:5001/health

Ollama Model Catalog:
http://localhost:11434/api/tags

Spring Boot Backend Probe:
http://localhost:8080/api/v1/auth/login
```
