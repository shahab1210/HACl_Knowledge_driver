# P_311 — Comprehensive Viva Voce & Technical Interview Guide (Phase 25)

This guide provides concise, technically rigorous answers to 42 core questions covering all aspects of **P_311: Knowledge-Driven IoT Fault Diagnosis Assistant**.

---

## 1. IoT & Edge Communication

### Q1: What is IoT and what role does it play in P_311?
**Answer:** The Internet of Things (IoT) connects physical equipment embedded with sensors to computing networks for monitoring and analysis. In P_311, IoT devices (represented by the Python ESP32 simulator) continuously capture multi-modal operational signals (temperature, vibration, current, pressure, humidity) and transmit them over standard networking protocols for real-time anomaly detection and diagnosis.

### Q2: Why use MQTT instead of HTTP REST for sensor telemetry?
**Answer:** MQTT (Message Queuing Telemetry Transport) is a lightweight binary/text protocol designed for constrained edge devices and unstable networks:
- **Low Packet Overhead:** Fixed 2-byte header versus verbose HTTP headers (often 500+ bytes).
- **Asynchronous Decoupling:** Publishers push data without waiting for database writes or server-side thread allocation.
- **Push Architecture:** Eliminates client polling overhead; the broker immediately pushes data to all active subscribers.

### Q3: Why Mosquitto for the MQTT broker?
**Answer:** Eclipse Mosquitto is an open-source, highly efficient MQTT v3.1.1/v5.0 broker written in C. It provides predictable low-latency message routing (<5ms), minimal RAM footprint (<10 MB), and robust socket management capable of handling thousands of concurrent sensor streams.

### Q4: What is an MQTT topic and what topic structure is used in P_311?
**Answer:** An MQTT topic is a UTF-8 hierarchical string used by the broker to route messages to appropriate subscribers. P_311 uses the structured hierarchy:
`iot/{deviceId}/telemetry` (e.g., `iot/ESP32_001/telemetry`), allowing wildcards like `iot/+/telemetry` for the Spring Boot backend to ingest data across an entire device fleet simultaneously.

### Q5: What is the Publish/Subscribe pattern?
**Answer:** A messaging pattern where senders (publishers) do not send messages directly to specific receivers. Instead, messages are published to topics on an intermediary broker. Senders and receivers remain completely decoupled in space, time, and synchronization.

---

## 2. Backend Architecture

### Q6: Why Spring Boot for the backend?
**Answer:** Spring Boot provides a production-grade enterprise Java framework with mature dependency injection, robust transaction management (`@Transactional`), built-in thread pooling, seamless integration with Spring Security, and clean reactive/asynchronous integrations via Spring Integration MQTT.

### Q7: Why PostgreSQL for data persistence?
**Answer:** PostgreSQL 18 is an advanced object-relational database providing strict ACID guarantees, strong schema enforcement, high-throughput time-series indexing (B-Tree timestamps), and relational foreign keys necessary to maintain referential integrity across normalized diagnosis trees.

### Q8: What is the role of the REST API?
**Answer:** The Spring Boot REST API exposes standardized, secure JSON endpoints over HTTP/HTTPS for client interactions: operator authentication (`/api/v1/auth`), alert monitoring and acknowledgement (`/api/v1/alerts`), and AI diagnosis retrieval and execution (`/api/v1/diagnosis`).

### Q9: How does MQTT integrate with Spring Boot?
**Answer:** Spring Boot utilizes the `org.springframework.integration.mqtt` adapter and Eclipse Paho client. A message-driven channel adapter (`MqttPahoMessageDrivenChannelAdapter`) listens on topic `iot/+/telemetry`, converts incoming payloads to strings via an inbound channel, and dispatches them to `MqttTelemetrySubscriber` without blocking the main web server threads.

---

## 3. Artificial Intelligence & RAG Pipeline

### Q10: What is Retrieval-Augmented Generation (RAG)?
**Answer:** RAG is an AI architecture that enhances Large Language Models by retrieving relevant factual documents from an external authoritative knowledge base before generating a response. It grounds the LLM in domain truths, substantially mitigating hallucination.

### Q11: What are embeddings?
**Answer:** Embeddings are high-dimensional numerical vector representations of text where semantic similarity is captured as geometric proximity. Texts with similar meanings or operational contexts map to nearby coordinates in vector space.

### Q12: Why ChromaDB?
**Answer:** ChromaDB is an open-source, developer-friendly vector database embedded directly in Python. It supports HNSW (Hierarchical Navigable Small World) indexing for ultra-fast nearest-neighbor searches, persists collections to disk (`ai/vector-db/data/chroma`), and requires no external container overhead.

### Q13: Why Ollama?
**Answer:** Ollama is an open-source local model execution runtime that packages LLM weights, configurations, and quantization runtimes into unified local daemons. It enables self-hosted, offline inference via a clean REST API (`http://localhost:11434`) without cloud subscription costs or external data leakage.

### Q14: Why `qwen2.5:1.5b`?
**Answer:** `qwen2.5:1.5b` is a 1.5B-parameter instruction-tuned model developed by Alibaba Cloud. It delivers state-of-the-art reasoning and structured output adherence in its parameter class, operates within ~1 GB of system RAM, and runs reliably on standard CPU hardware.

### Q15: Why `nomic-embed-text`?
**Answer:** `nomic-embed-text` is an open-weights 768-dimensional text embedding model optimized for long context windows (up to 8,192 tokens). It outperforms standard miniLM models in semantic retrieval benchmarks while maintaining low embedding latency.

### Q16: How does semantic retrieval work in P_311?
**Answer:**
1. Observed sensor readings are converted into a structured text query summarizing machine operating state and anomalies.
2. The query is embedded into a 768-dimensional vector using `nomic-embed-text`.
3. ChromaDB computes cosine distance against all indexed chunks in the `iot_fault_knowledge` collection.
4. The top-$k$ most relevant manual chunks are retrieved and injected into the LLM system prompt.

---

## 4. Diagnosis Engine & Fallbacks

### Q17: How is a fault selected by the system?
**Answer:** The LLM evaluates the observed telemetry against the retrieved maintenance manuals, matches failure criteria (e.g., temperature > 85°C with normal vibration indicates cooling fan failure), and outputs the standardized primary fault code. If the LLM output is malformed, a deterministic rule-based engine acts as fallback.

### Q18: What is confidence and how is it scored?
**Answer:** Confidence is a normalized score (0.00–1.00) reflecting the diagnostic certainty. It combines the semantic similarity of retrieved knowledge sources, the degree to which sensor readings exceed critical thresholds, and the internal consistency of the LLM's reasoning.

### Q19: What constitutes diagnostic evidence?
**Answer:** Evidence consists of specific, verified quantitative observations (e.g., *"Temperature 92.4°C exceeds critical threshold 85.0°C by 7.4°C"*) directly extracted from the telemetry payload and matched to domain manual limits.

### Q20: How are knowledge sources preserved?
**Answer:** Knowledge chunks retrieved from ChromaDB include source metadata (`source_name`, `document_id`, `chunk_id`, and `similarity_score`). These are persisted directly to the relational `diagnosis_knowledge_sources` table in PostgreSQL, linking every diagnosis to its supporting documentation.

### Q21: How are possible causes and recommended checks generated?
**Answer:** The LLM synthesizes root causes and rank-orders physical inspection steps based on the retrieved OEM manual procedures (e.g., *"Check cooling fan power supply"*, *"Inspect heatsink thermal paste"*).

---

## 5. Security & Access Control

### Q22: What is JWT and how is it used?
**Answer:** JSON Web Tokens (JWT) provide stateless authentication. Upon successful login (`/api/v1/auth/login`), Spring Boot issues a cryptographically signed token containing user claims (`sub`, `role`, `iat`, `exp`). Subsequent client requests include this token in the `Authorization: Bearer <token>` HTTP header.

### Q23: Why BCrypt for password hashing?
**Answer:** BCrypt is an adaptive, one-way cryptographic hashing algorithm incorporating an automatic salt and configurable work factor. It is computationally expensive by design, protecting stored credentials against dictionary and rainbow-table attacks.

### Q24: How are protected routes implemented?
**Answer:**
- **Backend:** Spring Security's `SecurityFilterChain` inspects the JWT on incoming requests; unauthenticated requests receive `HTTP 401 Unauthorized`.
- **Frontend:** React Router's `<ProtectedRoute>` component checks the local `AuthContext`; unauthenticated sessions are redirected to `/login`.

### Q25: What are the USER and ADMIN roles?
**Answer:** Role-Based Access Control (RBAC) separates duties:
- `USER` / `OPERATOR`: Can view real-time telemetry, inspect historical diagnoses, and view alerts.
- `ADMIN`: Has elevated permissions to trigger manual AI diagnoses, acknowledge active system alerts, and manage system configuration.

---

## 6. Database Architecture

### Q26: What is the diagnosis schema design?
**Answer:** The diagnosis subsystem uses a normalized 1-to-many schema rooted in the `diagnoses` table, with foreign-keyed child tables: `diagnosis_evidence`, `diagnosis_knowledge_sources`, `diagnosis_possible_causes`, `diagnosis_recommended_checks`, `diagnosis_alternative_faults`, and `diagnosis_additional_info`.

### Q27: Why separate evidence and knowledge sources into distinct tables?
**Answer:** Normalization avoids string concatenation or unstructured blobs. It enables SQL queries to aggregate evidence types, perform analytical lookups on cited manual frequency, and maintain strict referential integrity.

### Q28: How does the database handle telemetry volume?
**Answer:** The `sensor_readings` table utilizes B-Tree indexes on `device_id` and `timestamp DESC`, allowing sub-millisecond retrieval of the latest telemetry and fast range filtering for Grafana time-series graphs.

---

## 7. Frontend Interface

### Q29: Why React 18 and Vite?
**Answer:** Vite offers rapid hot-module reloading and optimized bundling. React's declarative component architecture and virtual DOM ensure high-frequency UI updates without layout lag as new sensor telemetry arrives.

### Q30: What does the React Dashboard display?
**Answer:**
1. Current device connection status and live telemetry metric cards.
2. Active warning and critical alert banners with one-click acknowledgement.
3. Latest AI diagnosis card displaying primary fault, confidence badge, and timestamp.
4. Deep explainability panel showing cited knowledge source excerpts and similarity scores.
5. Historical diagnosis log with searchable device filtering.

---

## 8. Monitoring & Observability

### Q31: Why Grafana for operations monitoring?
**Answer:** Grafana is an industry-standard visualization platform optimized for operations centers. It provides high-density multi-panel dashboards, dynamic dashboard variables (`$device_id`), time-range scrubbing, and automatic refresh intervals.

### Q32: Why use a direct PostgreSQL datasource in Grafana?
**Answer:** Querying PostgreSQL directly eliminates the need to run, configure, and maintain an intermediate metric scraper (such as Prometheus). Grafana's native PostgreSQL engine executes indexed SQL time-series queries with latency under 15ms.

---

## 9. MetroPT-3 Industrial Dataset

### Q33: What is the MetroPT-3 dataset?
**Answer:** MetroPT-3 is an open benchmark dataset collected from the Air Production Unit (APU) compressor of an urban passenger train operated by Metro do Porto, Portugal. It contains 1,516,948 real industrial observations sampled at 1 Hz across 16 physical signals.

### Q34: What signals does MetroPT-3 provide?
**Answer:** Pneumatic pressures (compressor outlet TP2, air dryer outlet TP3, main reservoir), motor electrical current, oil temperature, and electrical control signals (solenoids, motor contactors).

### Q35: Why does MetroPT-3 lack humidity and vibration?
**Answer:** The real railway APU instrument cluster was engineered strictly for pneumatic system health; transit engineers did not install accelerometers or hygrometers on the physical train. P_311 documents this limitation honestly and does not fabricate missing signals.

### Q36: What failure events are documented in MetroPT-3?
**Answer:** Four documented air-leak failure events occurring in April, May, June, and July 2020. Our offline analyzer successfully detected the anomalous pressure-drop and continuous compressor pumping signatures for all 4 events.

---

## 10. Testing & Quality Assurance

### Q37: How many tests pass in the system?
**Answer:** A total of **343 automated tests** pass with 100% success rate:
- **Python Subsystems:** 231 tests (ingestion: 22, vector-db: 23, embeddings: 24, llm: 47, rag: 30, diagnosis: 23, mqtt: 29, integration: 19, metropt: 14).
- **Spring Boot Backend:** 70 unit and mock MVC integration tests.
- **React Frontend:** 42 Vitest component and context tests.

### Q38: What types of testing were performed?
**Answer:** Unit testing of individual validators and parsers, mock-integration testing of Spring Boot controllers and repositories, end-to-end integration testing connecting live Ollama and ChromaDB, and regression test suites.

### Q39: How was end-to-end fault persistence verified?
**Answer:** By publishing an abnormal telemetry payload, verifying alert generation in Spring Boot, triggering AI diagnosis, confirming write operations across all 7 database tables, restarting the backend service, and verifying full record retrieval from PostgreSQL.

---

## 11. System Limitations & Future Work

### Q40: Why does local AI inference take 30–50 seconds?
**Answer:** `qwen2.5:1.5b` executes on local CPU hardware using unaccelerated quantized CPU threads (~16 tokens/second). Dedicated GPU acceleration (e.g., CUDA or Apple Metal) reduces inference time to under 2 seconds.

### Q41: Why are external SMS/Email notifications not implemented?
**Answer:** To preserve a strictly self-contained, offline-capable architecture that functions without external cloud SMTP/SMS gateways or third-party API dependencies. Alert notification is delivered in-app via the React UI and persisted in PostgreSQL.

### Q42: What would be the next engineering steps for production?
**Answer:**
1. GPU-accelerated local inference cluster for sub-second LLM responses.
2. TimescaleDB hypertables for automatic partitioning of multi-gigabyte telemetry streams.
3. Multi-tenant device management with MQTT client certificate authentication (mTLS).
