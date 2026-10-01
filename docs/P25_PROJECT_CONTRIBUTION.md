# P_311 — System Contributions & Innovations (Phase 25)

This document provides a concise academic and technical summary of the core contributions of **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant**.

---

## 1. IoT Telemetry Ingestion
- Real-time ingestion of multi-modal industrial sensor data (temperature, vibration, current, pressure, humidity).
- Resilient JSON payload parsing with schema validation and malformed-message rejection.

## 2. Decoupled MQTT Communication
- Asynchronous messaging architecture using Mosquitto (port 1883) and Eclipse Paho MQTT client in Spring Boot.
- Topic-based addressing (`iot/{deviceId}/telemetry`) enabling clean horizontal scaling and isolation of physical devices from analytics backends.

## 3. Persistent Industrial Telemetry Storage
- PostgreSQL 18 relational persistence for high-throughput sensor telemetry with millisecond timestamp indexing.
- Provides an immutable historical audit trail for compliance, post-mortem incident investigation, and time-series analysis.

## 4. Curated Industrial Domain Knowledge Base
- Ingestion of structured maintenance manuals, operating thresholds, failure modes, and OEM troubleshooting standards (P5 corpus).
- Structured document chunking with metadata tagging preserving fault codes, machine components, and operating limits.

## 5. Semantic Vector Retrieval (RAG)
- Dense semantic vector search using `nomic-embed-text` (768-dimensional embeddings) and ChromaDB (`iot_fault_knowledge`).
- Contextual k-nearest neighbor retrieval matching current anomalous telemetry to relevant manual sections.

## 6. Zero-Cloud Local LLM Diagnosis
- Local inference via Ollama using `qwen2.5:1.5b`, ensuring strict industrial data privacy, zero telemetry leakage, and zero cloud API dependency.
- Dynamic grounding prompt forcing the LLM to base conclusions strictly on retrieved engineering documentation.

## 7. Structured Diagnosis Engine
- Strict enforcement of the P12 industrial diagnosis contract: primary fault, confidence score (0.00–1.00), verifiable evidence citations, knowledge manual references, and ranked action checklists.
- Deterministic heuristic fallback mechanism guaranteeing valid structured outputs even during LLM timeout or unparseable responses.

## 8. Real-Time Alert Detection & Deduplication
- Low-latency (<5ms) threshold violation detection evaluating safety envelopes for temperature, vibration, current, and pressure.
- State-aware alert deduplication preventing alarm fatigue by suppressing repeated alerts during continuous fault conditions.

## 9. Role-Based Authentication & Authorization (RBAC)
- Stateless Spring Security architecture with JWT tokens (HS512 signing) and BCrypt password hashing.
- Segregated roles (`OPERATOR` vs `ADMIN`) protecting sensitive operational controls, manual diagnosis triggers, and alert acknowledgements.

## 10. Responsive Industrial Web Dashboard
- Modern React 18 / Vite single-page application with responsive telemetry cards, live alert banners, and interactive diagnosis drill-downs.
- Deep explainability views allowing engineers to inspect the exact engineering manual passages and similarity scores backing every diagnosis.

## 11. Operational Infrastructure Monitoring
- Turnkey Grafana 13 operations dashboard with 12 specialized panels for real-time telemetry trends, alert counts, and AI diagnosis latency metrics.
- Native PostgreSQL time-series datasource queries eliminating the need for complex intermediate metric scrapers.

## 12. Real Industrial Dataset Validation (MetroPT-3)
- Comprehensive offline empirical validation on 1,516,948 records from the real-world MetroPT-3 urban train compressor dataset.
- Successfully verified operational compressor states (Standby, Offloaded, UnderLoad) and detected all 4 documented air-leak failure events.
