# P11 — RAG + LLM Integration Layer

The **P11 RAG + LLM Integration Layer** provides a clean, unified, and reusable application-level interface that seamlessly coordinates **P9 RAG Retrieval** (ChromaDB + `nomic-embed-text`) with **P10 Local LLM Generation** (Ollama + `qwen2.5:1.5b`) for the **Knowledge-Driven IoT Fault Diagnosis Assistant**.

---

## 1. Purpose & Objective

While P9 handles dense semantic retrieval and P10 manages local LLM inference, P11 orchestrates both stages into a single application pipeline:
- Validates user and telemetry queries.
- Executes P9 semantic retrieval across the 18 domain fault, sensor, and procedure documents in ChromaDB.
- Preserves complete retrieval evidence (`rank`, `chunk_id`, `document_id`, `similarity`, `distance`, `metadata`).
- Constructs grounded, safety-constrained prompts via P10.
- Invokes the local Ollama LLM to generate technical fault explanations.
- Returns a structured `DiagnosisResponse` object containing the diagnosis, prompt, context, source traceability, and generation telemetry.

---

## 2. Architecture & Data Flow

```text
                        Telemetry / Operator Query
                                    ↓
                       +-------------------------+
                       |   Query Validation      |
                       +-------------------------+
                                    ↓
                       +-------------------------+
                       |    P9 RAG Retrieval     |
                       |  (ChromaDB + Embeddings)|
                       +-------------------------+
                                    ↓
                       +-------------------------+
                       |  Evidence Preservation  |
                       | (Sources, Chunks, Sims) |
                       +-------------------------+
                                    ↓
                       +-------------------------+
                       |   P10 Prompt Builder    |
                       |  (Grounding & Rules)    |
                       +-------------------------+
                                    ↓
                       +-------------------------+
                       |     Local Ollama LLM    |
                       |     (qwen2.5:1.5b)      |
                       +-------------------------+
                                    ↓
                       +-------------------------+
                       |    DiagnosisResponse    |
                       |  (Structured Output)    |
                       +-------------------------+
```

---

## 3. Directory Structure

```text
ai/integration/
├── src/
│   ├── __init__.py           # Public exports (RAGLLMPipeline, DiagnosisResponse, etc.)
│   ├── config.py             # Hyperparameters, endpoints, and default models
│   ├── exceptions.py         # Specialized exception hierarchy
│   ├── models.py             # Data models (DiagnosisResponse, RetrievalEvidence, SourceEvidence)
│   ├── loader.py             # Component loader & context isolation (prevents namespace collisions)
│   └── pipeline.py           # Core RAGLLMPipeline orchestrator
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # Model serialization and JSON validation
│   ├── test_errors.py        # Validation and error handling unit tests
│   ├── test_pipeline.py      # Pipeline orchestration unit tests (mocked dependencies)
│   └── test_live_integration.py # Real end-to-end integration test with Ollama & ChromaDB
├── cli.py                    # Standalone CLI interface
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## 4. Configuration & Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama HTTP endpoint |
| `LLM_MODEL` | `qwen2.5:1.5b` | Local generative LLM model |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Dense embedding model (for ChromaDB retrieval) |
| `RAG_TOP_K` | `3` | Number of knowledge chunks retrieved |
| `LLM_TEMPERATURE` | `0.2` | Sampling temperature for factual diagnosis |
| `LLM_MAX_TOKENS` | `1024` | Maximum tokens generated (`num_predict`) |
| `LLM_TIMEOUT` | `120.0` | HTTP timeout in seconds |

---

## 5. Python API Usage

```python
from integration.src import RAGLLMPipeline

# 1. Initialize the pipeline
pipeline = RAGLLMPipeline(
    top_k=3,
    model="qwen2.5:1.5b",
    embedding_model="nomic-embed-text",
    base_url="http://localhost:11434"
)

# 2. Execute diagnosis on telemetry symptoms
query = "The motor temperature is 95°C and vibration is 7.2. What could be the problem?"
result = pipeline.run(query)

# 3. Access structured diagnosis response
print("Diagnosis:\n", result.diagnosis)
print("Model Used:", result.model)
print("Sources Retrieved:", result.retrieval.result_count)

for source in result.retrieval.sources:
    print(f"  [{source.rank}] {source.document_id} - {source.title} (Similarity: {source.similarity:.4f})")

# 4. Serialize to JSON
json_output = result.to_json(indent=2)
```

---

## 6. CLI Usage

The P11 CLI allows rapid diagnosis testing directly from the shell.

### 1. Human-Readable Diagnosis Mode
```bash
python3 ai/integration/cli.py diagnose \
  --query "The motor temperature is 95°C and vibration is 7.2. What could be the problem?" \
  --top-k 3 \
  --model qwen2.5:1.5b
```

*Example CLI Output:*
```text
========================================
P11 RAG + LLM Integration: Fault Diagnosis
========================================
Query:           'The motor temperature is 95°C and vibration is 7.2. What could be the problem?'
Generative Model: qwen2.5:1.5b
Embedding Model:  nomic-embed-text
Ollama Endpoint:  http://localhost:11434
Top-K Retrieval:  3
----------------------------------------
Executing retrieval & local generation...

----------------------------------------
Retrieved Knowledge Sources (3):
----------------------------------------
  [1] FAULT-003: Motor Overheating
      Chunk:      FAULT-003_chunk_001
      Similarity: 0.7390 (Distance: 0.2610)
      Source:     faults/motor-overheating.md
  [2] FAULT-005: Excessive Motor Vibration
      Chunk:      FAULT-005_chunk_001
      Similarity: 0.7363 (Distance: 0.2637)
      Source:     faults/motor-vibration.md
  [3] FAULT-003: Motor Overheating
      Chunk:      FAULT-003_chunk_002
      Similarity: 0.7305 (Distance: 0.2695)
      Source:     faults/motor-overheating.md

----------------------------------------
Generated Fault Diagnosis:
----------------------------------------
Based on the retrieved knowledge sources, the motor is showing symptoms of Motor Overheating (FAULT-003) and Excessive Motor Vibration (FAULT-005)...

----------------------------------------
Generation Telemetry & Statistics:
----------------------------------------
  Model:            qwen2.5:1.5b
  Tokens Generated: 941
  Total Duration:   52.22s
========================================
```

### 2. Structured JSON Output Mode
```bash
python3 ai/integration/cli.py diagnose \
  --query "Motor overheating" \
  --top-k 1 \
  --json
```

---

## 7. Testing & Verification

### Unit Tests
All unit tests are fully isolated and pass without requiring external services:
```bash
pytest ai/integration/tests/test_models.py ai/integration/tests/test_errors.py ai/integration/tests/test_pipeline.py -v
```
*Result:* `18/18 passed`

### Regression Verification
Existing modules continue to function without any regressions:
- P9 RAG Retrieval: `pytest ai/rag/tests/ -v` -> `30/30 passed`
- P10 Local LLM: `pytest ai/llm/tests/ -v` -> `47/47 passed`

---

## 8. Strict P11 Boundary

The P11 layer is strictly limited to the application-level orchestration of RAG retrieval and local LLM text generation. It explicitly **does not** implement:
- MQTT broker telemetry ingestion
- Spring Boot REST APIs
- PostgreSQL database diagnosis storage
- React dashboard UI
- Hardcoded rule-based thresholds or diagnosis engines
- Cloud LLMs / Cloud embeddings
