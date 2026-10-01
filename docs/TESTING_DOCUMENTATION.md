# P_311 — Testing & Quality Assurance Documentation

This document specifies the multi-tier testing strategy, test suites, coverage metrics, and failure recovery verifications across all components of **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant**.

---

## 1. Regression Test Summary

As verified during Phase 23 integration testing, the system maintains **343 passing automated tests** across four distinct tiers:

```text
========================================================================
P_311 Test Suite Breakdown
========================================================================
1. P22 MetroPT-3 Industrial Dataset Tests:    14 / 14  PASSED
2. Python AI Core Test Suites (P5–P21):      217 / 217 PASSED
3. Spring Boot Backend Tests (JUnit 5):       70 / 70  PASSED
4. React Frontend Tests (Vitest):             42 / 42  PASSED
------------------------------------------------------------------------
TOTAL AUTOMATED TEST SUITE:                  343 / 343 PASSED (100% Green)
========================================================================
```

---

## 2. Python AI & RAG Test Suites (231 Tests)

Executed via `pytest` inside the `ai/vector-db/.venv` virtual environment:

| Module / Package | Tests | Scope & Coverage |
| :--- | :---: | :--- |
| `ai/ingestion/tests/` | 22 | Markdown parser, header preservation, semantic chunking boundaries, metadata validation. |
| `ai/vector-db/tests/` | 23 | ChromaDB client lifecycle, collection creation, cosine distance query assertions, document storage. |
| `ai/embeddings/tests/`| 24 | Ollama embedding client, 768-dim vector normalization, dimension validation, error handling. |
| `ai/llm/tests/` | 47 | Prompt builder templates, temperature parameterization, generation parsing, fallback handling. |
| `ai/rag/tests/` | 30 | Telemetry query builder, ChromaDB similarity retrieval, top-k rank ordering, context builder formatting. |
| `ai/diagnosis/tests/` | 23 | `DiagnosisEngine`, response parser regex extraction, confidence scoring calculation, Pydantic validation. |
| `ai/mqtt/tests/` | 29 | Telemetry message deserialization, topic parser regex, payload validator, worker subscription loops. |
| `ai/integration/tests/`| 19 | Live RAG+LLM pipeline execution, mocked inference pipelines, input validation, Ollama connection checks. |
| `ai/dataset/metropt/tests/`| 14 | MetroPT-3 loader, timestamp monotonicity, schema validator, isolation check (NO humidity/vibration), feature extraction, operating state classification, IQR/Z-score anomaly detection, report generation. |
| **Total Python Tests** | **231** | **All 231 tests pass with zero failures.** |

---

## 3. Spring Boot Backend Test Suites (70 Tests)

Executed via Maven (`mvn test -f iot_hcl_spingboot/iot-fault-diagnosis/pom.xml`):

| Test Class | Tests | Test Type | Verification Focus |
| :--- | :---: | :---: | :--- |
| `DiagnosisEntityTest` | 3 | Unit | Entity mappings, builder methods, equals/hashCode contracts. |
| `DtoSerializationTest` | 4 | Unit | Jackson JSON serialization / deserialization of request and response DTOs. |
| `DiagnosisMapperTest` | 2 | Unit | Mapping between database entities and REST API response models. |
| `DiagnosisServiceTest` | 11 | Unit / Mockito | Business logic, on-demand triggering, MQTT ingestion, store delegation, fallback logic. |
| `DiagnosisIntegrationTest` | 1 | Integration | End-to-end MockMvc invocation of `/api/v1/diagnosis`, database persistence, and rollback. |
| `DiagnosisRepositoryTest` | 4 | Data JPA | Relational database operations against PostgreSQL, custom query methods, ordering by creation date. |
| `AlertControllerTest` | 9 | Integration | MockMvc testing of `/api/v1/alerts`, filtering by device, severity, and acknowledgement. |
| Additional Unit Suites | 36 | Unit | Exception handling, JWT token provider, password encoding, user details service. |
| **Total Backend Tests** | **70** | **All 70 tests pass with zero failures.** |

---

## 4. React Frontend Test Suites (42 Tests)

Executed via Vitest (`npm test -- --run` in `frontend/`):

| Test File | Tests | Coverage Focus |
| :--- | :---: | :--- |
| `src/test/auth.test.jsx` | 10 | Login form validation, registration flow, password length enforcement, duplicate user handling, `ProtectedRoute` redirect logic, user profile header state. |
| `src/test/components.test.jsx`| 11 | TelemetryCard rendering, gauge boundary coloring, status badges, confidence visualizers, loading spinners. |
| `src/test/alerts.test.jsx` | 6 | AlertWidget badge counts, critical banner rendering, operator acknowledgement button dispatch, filter tabs. |
| `src/test/pages.test.jsx` | 2 | Top-level routing, 404 fallback page rendering. |
| `src/test/Dashboard.test.jsx` | 3 | Dashboard mount, live telemetry card grid, trigger diagnosis modal interaction. |
| `src/test/api.test.js` | 6 | Axios interceptors, Authorization header injection, error response normalization. |
| `src/test/formatters.test.js` | 4 | Timestamp formatting, numerical rounding, unit label generation. |
| **Total Frontend Tests** | **42** | **All 42 tests pass with zero failures.** |

---

## 5. Grafana Automated Dashboard Verification (13 Panels)

Automated script [`scripts/verify_grafana_dashboard.py`](file:///Users/shahabahmad/Documents/P_311/scripts/verify_grafana_dashboard.py) executes live against Grafana (`http://localhost:3000`):
- Verifies Grafana database health: `OK`.
- Verifies PostgreSQL Datasource connection: `OK`.
- Queries raw SQL for all 13 panels against live PostgreSQL:
  1. `Latest Temperature`: PASS
  2. `Latest Humidity`: PASS
  3. `Latest Vibration`: PASS
  4. `Latest Current`: PASS
  5. `Latest Pressure`: PASS
  6. `Total Stored Diagnoses`: PASS
  7. `Real-Time Telemetry Trend (Multi-Channel)`: PASS
  8. `AI Diagnosis Latency Progression`: PASS
  9. `Primary Fault Classification Distribution`: PASS
  10. `Diagnosis Confidence Level Distribution`: PASS
  11. `Persisted AI Fault Diagnosis History`: PASS
  12. `PostgreSQL Database Storage Health`: PASS
  13. `System Alerts & Notifications (P20)`: PASS

---

## 6. Failure Recovery & Boundary Verification

The system was subjected to deliberate fault injection during Phase 23:

1. **AI Bridge Downtime:** Stopped Python AI bridge on port 5001. Called `POST /api/v1/diagnosis`. Spring Boot caught `ResourceAccessException`, returned `HTTP 503 Service Unavailable` with message: *"Diagnosis service unavailable: AI Diagnosis Service is currently unreachable at http://localhost:5001"*. Backend remained healthy.
2. **Malformed MQTT Payload:** Published non-JSON string `MALFORMED_NON_JSON_DATA{{{` to `iot/ESP32_001/telemetry`. Caught by `JsonParseException`; subscriber logged error and remained listening without thread termination.
3. **Incomplete Telemetry Payload:** Published payload missing `device_id`. PostgreSQL non-null constraint caught error; subscriber logged violation safely.
4. **Backend Restart Survivability:** Created diagnosis `diag-ESP32_001-1790833907713`. Terminated Spring Boot process. Re-launched application. Queried diagnosis by ID; all 5 evidence rows and 3 cited knowledge sources were retrieved intact from PostgreSQL.
