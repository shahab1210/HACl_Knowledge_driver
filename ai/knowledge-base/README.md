# Knowledge Base for Industrial IoT Fault Diagnosis Assistant (P5)

## 1. Purpose of the Knowledge Base
The **Knowledge Base (P5)** serves as the authoritative, curated domain intelligence repository for project **P_311 — Knowledge-Driven IoT Fault Diagnosis Assistant**. 

Modern industrial condition-monitoring systems collect high-frequency time-series telemetry (such as temperature, vibration, current, pressure, and humidity) from rotating electro-mechanical machinery (e.g., electric induction motors and centrifugal process pumps). However, raw numerical telemetry alone cannot diagnose machinery failures without deep domain engineering knowledge.

This knowledge base codifies:
- Physical failure mechanisms of industrial assets.
- Cross-sensor symptom patterns and telemetry correlations.
- Ranked differential diagnoses to prevent false or oversimplified conclusions.
- Safe, standard operating inspection checklists and verification procedures.

---

## 2. Folder Structure
The knowledge base is structured into dedicated, modular directories located at the project root under `ai/knowledge-base/`:

```
P_311/
├── python/                  # Existing Python IoT sensor simulator
├── springboot/              # Existing Spring Boot MQTT subscriber & PostgreSQL backend
└── ai/
    └── knowledge-base/      # P5 Knowledge Base Root
        ├── README.md        # Architecture overview & documentation guide
        ├── faults/          # Standardized industrial fault documents (10 faults)
        │   ├── bearing-overheating.md
        │   ├── bearing-wear.md
        │   ├── motor-overheating.md
        │   ├── motor-overcurrent.md
        │   ├── motor-vibration.md
        │   ├── pump-cavitation.md
        │   ├── pump-dry-running.md
        │   ├── low-pressure.md
        │   ├── high-pressure.md
        │   └── sensor-anomaly.md
        ├── sensors/         # Industrial sensor behavior & diagnostic roles (5 sensors)
        │   ├── temperature.md
        │   ├── vibration.md
        │   ├── current.md
        │   ├── pressure.md
        │   └── humidity.md
        └── procedures/      # Standard inspection and diagnosis procedures (3 procedures)
            ├── general-diagnosis.md
            ├── motor-inspection.md
            └── pump-inspection.md
```

---

## 3. Fault Documents (`faults/`)
The `faults/` directory contains 10 standardized technical fault dossiers covering the primary electro-mechanical, hydraulic, and instrumentation failure modes in industrial pumping and motor drive systems:

1. **FAULT-001 — Bearing Overheating (`bearing-overheating.md`):** Excessive friction, lubricant failure, or misalignment leading to bearing thermal degradation.
2. **FAULT-002 — Bearing Wear (`bearing-wear.md`):** Progressive fatigue, spalling, and flaking of raceways and rolling elements.
3. **FAULT-003 — Motor Overheating (`motor-overheating.md`):** Stator winding thermal stress and insulation breakdown risks.
4. **FAULT-004 — Motor Overcurrent (`motor-overcurrent.md`):** Sustained electrical draw exceeding full-load design ratings.
5. **FAULT-005 — Excessive Motor Vibration (`motor-vibration.md`):** Kinetic oscillations driven by unbalance, misalignment, looseness, or resonance.
6. **FAULT-006 — Pump Cavitation (`pump-cavitation.md`):** Hydraulic vapor bubble formation and violent implosion eroding impellers.
7. **FAULT-007 — Pump Dry Running (`pump-dry-running.md`):** Operation without fluid lubrication destroying mechanical seal faces and wear rings.
8. **FAULT-008 — Low Pressure (`low-pressure.md`):** Pipeline breaches, excessive internal wear ring clearances, or suction starvation.
9. **FAULT-009 — High Pressure (`high-pressure.md`):** Downstream blockages, closed discharge valves, or dead-head churning.
10. **FAULT-010 — Sensor Anomaly (`sensor-anomaly.md`):** Instrumentation failures, flatlines, telemetry drops, or physical contradictions.

Each fault dossier includes:
- Unique FAULT-ID and structured metadata.
- Engineering description of the failure mechanism.
- Observable operational symptoms.
- Mechanical, electrical, or process root causes.
- Markdown correlation table of sensor indicators (Temperature, Vibration, Current, Pressure, Humidity).
- Recommended diagnostic checks.
- Critical personnel and machinery safety precautions.
- Cross-references to related fault modes.

---

## 4. Sensor Documents (`sensors/`)
The `sensors/` directory details the diagnostic capabilities and limitations of each telemetry channel:
- **`temperature.md`:** Measures thermodynamic dissipation and friction; early detection of bearing distress and electrical overloads.
- **`vibration.md`:** Measures dynamic acceleration and velocity; captures unbalance, misalignment, bearing raceway defects, and cavitation shocks.
- **`current.md`:** Measures electrical power draw and shaft load torque; reveals electrical anomalies and driven load conditions.
- **`pressure.md`:** Measures hydraulic and pneumatic system head; diagnoses blockages, pipeline breaks, and cavitation.
- **`humidity.md`:** Measures environmental moisture and seal leaks; flags condensation risks and process fluid spray.

> **Operational Disclaimer:**
> Actual limits depend on the equipment specification, sensor location, operating conditions, and manufacturer recommendations.

---

## 5. Procedure Documents (`procedures/`)
The `procedures/` directory codifies step-by-step procedures to translate algorithmic detections into on-site maintenance actions:
- **`general-diagnosis.md`:** End-to-end industrial IoT diagnostic reasoning methodology—from continuous telemetry triage and sensor validation, to multi-sensor fusion, differential hypothesis ranking, and on-site verification.
- **`motor-inspection.md`:** Safety-first inspection checklist for electric motors covering LOTO, thermography, soft foot, alignment, bearing lubrication, and insulation resistance (Megger) testing.
- **`pump-inspection.md`:** Safety-first inspection checklist for process pumps covering hydraulic isolation, depressurization, suction strainer inspection, mechanical seal health, and wear ring clearances.

---

## 6. Document Metadata and Front Matter
All fault documents utilize standardized YAML front matter to support structured metadata extraction and automated document indexing:

```yaml
---
id: FAULT-001
title: Bearing Overheating
category: mechanical
equipment: motor
severity: high
sensors:
  - temperature
  - vibration
  - current
---
```

### Front Matter Fields:
- `id`: Unique fault identifier (`FAULT-001` through `FAULT-010`).
- `title`: Standardized engineering name of the fault.
- `category`: Primary technical classification (`mechanical`, `electrical`, `hydraulic`, `instrumentation`, `thermal`).
- `equipment`: Primary asset affected (`motor`, `pump`, `sensor`).
- `severity`: Operational risk level (`critical`, `high`, `medium`, `low`).
- `sensors`: List of telemetry channels directly sensitive to this fault mode.

---

## 7. How the Documents Will Later Be Used by P6
In the upcoming Phase 6 (P6) of Project P_311, these knowledge documents will serve as the grounding corpus for an intelligent AI Fault Diagnosis Assistant:

```
  +-------------------------------------------------------------+
  |              P5: Knowledge Base Markdown Files              |
  |             (Faults, Sensors, Procedures)                   |
  +------------------------------+------------------------------+
                                 |
                                 v  (P6 Ingestion)
  +-------------------------------------------------------------+
  |                  P6: Document Ingestion                     |
  |         (Markdown Parsing & Front-Matter Extraction)        |
  +------------------------------+------------------------------+
                                 |
                                 v  (P6 Chunking)
  +-------------------------------------------------------------+
  |               P6: Semantic Chunking Engine                  |
  |     (Chunk by Sections: Symptoms, Causes, Sensor Tables)    |
  +------------------------------+------------------------------+
                                 |
                                 v  (P6 Vectorization)
  +-------------------------------------------------------------+
  |               P6: Dense Text Embeddings                     |
  |                (Local Embedding Models)                     |
  +------------------------------+------------------------------+
                                 |
                                 v  (P6 Storage)
  +-------------------------------------------------------------+
  |               P6: Vector Database Storage                   |
  |         (ChromaDB / PGvector / Qdrant Storage)              |
  +------------------------------+------------------------------+
                                 |
                                 v  (P6 Retrieval)
  +-------------------------------------------------------------+
  |             P6: RAG Semantic Context Retrieval              |
  |   (Retrieve Relevant Fault Context based on Live Telemetry) |
  +------------------------------+------------------------------+
                                 |
                                 v  (P6 Generation)
  +-------------------------------------------------------------+
  |             P6: Local LLM Diagnostic Reasoning              |
  |         (Ollama / Mistral / Llama Fault Explanations)       |
  +-------------------------------------------------------------+
```

---

## 8. Relationship to RAG (Retrieval-Augmented Generation)
Large Language Models (LLMs) often suffer from domain hallucinations and lack specific industrial engineering context. By applying **Retrieval-Augmented Generation (RAG)**:
1. When real-time IoT telemetry exhibits an anomaly (e.g., high temperature + elevated vibration + high current), the system formulates a semantic query.
2. The vector retriever searches this knowledge base for chunks with high cosine similarity (e.g., `bearing-overheating.md`, `bearing-wear.md`, and `motor-inspection.md`).
3. The retrieved chunks are injected into the LLM system prompt as verified context.
4. The LLM generates factually grounded, deterministic diagnostic advice, root causes, and safe step-by-step inspection instructions.

---

## 9. Explicit Scope Boundaries (What P5 Is NOT)
> [!IMPORTANT]
> **P5 is exclusively dedicated to authoring the technical knowledge content.**
>
> In accordance with project architecture boundaries, the following components are **NOT** part of P5 and will be implemented in subsequent phases:
> - Document ingestion pipelines
> - Text chunking algorithms
> - Vector embedding generation
> - Vector database installation or configuration (e.g., ChromaDB, Milvus, PGvector)
> - Retrieval-Augmented Generation (RAG) orchestration
> - Local LLM integration (e.g., Ollama, llama.cpp)
> - AI microservice APIs or REST endpoints
> - Spring Boot AI controllers or service integrations
> - React AI user interface components
