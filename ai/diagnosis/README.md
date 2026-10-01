# P12 — Diagnosis Engine

The **P12 Diagnosis Engine** provides a standardized, machine-readable fault diagnosis layer for the **Knowledge-Driven IoT Fault Diagnosis Assistant**. It processes the structured retrieval evidence and natural language reasoning produced by **P11 (RAG + LLM Integration Layer)** to synthesize a validated, schema-compliant, and fully traceable diagnostic report.

---

## 1. Objective & Role

P12 sits directly above P11:
```text
P5 Knowledge Base
        ↓
P6 Ingestion & P7 Embeddings
        ↓
P8 ChromaDB Vector Database
        ↓
P9 Semantic RAG Retrieval
        ↓
P10 Local LLM (qwen2.5:1.5b)
        ↓
P11 RAG + LLM Integration
        ↓
P12 Diagnosis Engine
        ↓
Structured Machine-Readable Diagnosis
```

> [!IMPORTANT]
> P12 is **NOT** a rule engine with arbitrary hardcoded thresholds (e.g. `temperature > 90 -> Overheating`).
> P12 interprets, structures, validates, and preserves the grounded evidence and LLM reasoning generated from the P5 knowledge base.

---

## 2. Key Responsibilities

1. **Primary & Alternative Fault Identification**:
   - Identifies the primary fault mode (`FAULT-XXX`) based on grounded knowledge and similarity.
   - Preserves alternative/candidate fault modes when symptoms overlap across multiple subsystems.

2. **Calibrated Confidence & Uncertainty Representation**:
   - Represents uncertainty explicitly using discrete, controlled levels: `high`, `medium`, `low`, `insufficient`.
   - Avoids inventing uncalibrated pseudo-probabilities (e.g., "87.3% confident").

3. **Telemetry & Knowledge Evidence Preservation**:
   - Extracts observed telemetry parameters, numerical values, units, and qualitative statuses.
   - Retains full traceability to retrieved knowledge chunks (`rank`, `document_id`, `chunk_id`, `similarity`, `distance`, `source`).

4. **Actionable Insights Extraction**:
   - Structures root causes into `possible_causes`.
   - Structures maintenance and inspection procedures into `recommended_checks`.
   - Explicitly records `additional_information_required` when symptoms are incomplete.

5. **Schema Validation & Error Handling**:
   - Validates all fields against domain integrity rules.
   - Rejects empty queries, invalid confidence levels, or malformed inputs.

---

## 3. Directory Structure

```text
ai/diagnosis/
├── src/
│   ├── __init__.py           # Package exports (DiagnosisEngine, StructuredDiagnosis, etc.)
│   ├── models.py             # Domain models (FaultReference, ConfidenceInfo, TelemetryEvidence, StructuredDiagnosis)
│   ├── parser.py             # Parses P11 DiagnosisResponse into StructuredDiagnosis
│   ├── validator.py          # Validates structural and semantic integrity
│   ├── loader.py             # Isolated component loader (prevents module collisions)
│   ├── exceptions.py         # Specialized error hierarchy
│   └── engine.py             # Core DiagnosisEngine orchestrator
├── tests/
│   ├── test_models.py        # 5 unit tests for models & serialization
│   ├── test_parser.py        # 5 unit tests for extraction & insufficient-context parsing
│   ├── test_validator.py     # 8 unit tests for schema & integrity validation
│   └── test_engine.py        # 5 unit tests for engine orchestration (mocked P11)
├── cli.py                    # Standalone CLI with human-readable and JSON modes
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## 4. Structured Diagnosis Schema

```json
{
  "query": "The motor temperature is 95°C and vibration is 7.2.",
  "primary_fault": {
    "fault_id": "FAULT-003",
    "title": "Motor Overheating",
    "document_type": "fault",
    "similarity": 0.7390
  },
  "alternative_faults": [
    {
      "fault_id": "FAULT-005",
      "title": "Excessive Motor Vibration",
      "document_type": "fault",
      "similarity": 0.7363
    }
  ],
  "confidence": {
    "level": "medium",
    "reason": "Multiple retrieved fault modes match the observed symptoms."
  },
  "evidence": [
    {
      "type": "telemetry",
      "parameter": "temperature",
      "value": 95,
      "unit": "°C"
    },
    {
      "type": "telemetry",
      "parameter": "vibration",
      "value": 7.2,
      "unit": "mm/s"
    }
  ],
  "possible_causes": [
    "Electrical overload on stator windings",
    "Phase voltage unbalance",
    "Restricted cooling airflow",
    "Mechanical unbalance / rotor unbalance"
  ],
  "recommended_checks": [
    "Measure surface temperature profile using an infrared camera",
    "Measure three-phase currents using a true-RMS clamp meter",
    "Perform winding insulation resistance (Megger test)",
    "Perform vibration spectrum analysis"
  ],
  "additional_information_required": [
    "Additional sensor telemetry is needed to isolate single root cause"
  ],
  "knowledge_sources": [
    {
      "rank": 1,
      "document_id": "FAULT-003",
      "chunk_id": "FAULT-003_chunk_001",
      "title": "Motor Overheating",
      "source": "faults/motor-overheating.md",
      "similarity": 0.7390,
      "distance": 0.2610
    }
  ],
  "raw_llm_response": "...",
  "model": "qwen2.5:1.5b",
  "generation_details": {
    "eval_count": 886,
    "total_duration": 62300000000
  }
}
```

---

## 5. Python API Usage

```python
from diagnosis.src import DiagnosisEngine

# 1. Initialize the engine
engine = DiagnosisEngine(
    top_k=3,
    model="qwen2.5:1.5b",
    embedding_model="nomic-embed-text"
)

# 2. Execute end-to-end diagnosis
query = "The motor temperature is 95°C and vibration is 7.2. What could be the problem?"
diagnosis = engine.diagnose(query)

# 3. Inspect structured diagnosis
print("Primary Fault:", diagnosis.primary_fault.title if diagnosis.primary_fault else "None")
print("Confidence:", diagnosis.confidence.level)

for alt in diagnosis.alternative_faults:
    print(f"Alternative: {alt.fault_id} - {alt.title}")

print("\nRecommended Checks:")
for check in diagnosis.recommended_checks:
    print(f"  • {check}")

# 4. Export to JSON
json_output = diagnosis.to_json(indent=2)
```

---

## 6. CLI Usage

### Human-Readable Diagnosis
```bash
python3 ai/diagnosis/cli.py diagnose \
  --query "The motor temperature is 95°C and vibration is 7.2. What could be the problem?" \
  --top-k 3 \
  --model qwen2.5:1.5b
```

### JSON Output
```bash
python3 ai/diagnosis/cli.py diagnose \
  --query "Motor overheating" \
  --top-k 1 \
  --json
```

---

## 7. Testing & Verification

All P12 unit tests run offline with zero network dependencies:
```bash
pytest ai/diagnosis/tests/ -v
```
*Result:* `23/23 passed`

---

## 8. Strict P12 Boundary

The P12 layer is strictly responsible for diagnosis structuring, validation, and domain interpretation. It explicitly **does not** implement:
- MQTT broker ingestion or publishing
- Spring Boot REST backend APIs
- PostgreSQL database persistence
- React frontend dashboards
- Hardcoded rule-based diagnosis engines
- Cloud LLM/embedding APIs
