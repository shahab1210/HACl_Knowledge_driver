# P9 - Retrieval-Augmented Generation Pipeline

## 1. Purpose

P9 implements the Retrieval-Augmented Generation (RAG) retrieval layer
for the IoT Fault Diagnosis Assistant.

The purpose of P9 is to take an IoT/user query, retrieve relevant
industrial knowledge from the P8 vector database, process the retrieved
results, and construct a clean context for a future Local LLM.

P9 does not generate the final AI diagnosis.

---

## 2. Position in the Project

The current AI pipeline is:

Sensor Telemetry
        ↓
Query Representation
        ↓
P9 RAG Pipeline
        ↓
P8 ChromaDB
        ↓
Relevant Knowledge
        ↓
RAG Context
        ↓
P10/P11 Local LLM

The existing telemetry pipeline remains separate:

Python Sensor Simulator
        ↓
MQTT
        ↓
Mosquitto
        ↓
Spring Boot MQTT Subscriber
        ↓
PostgreSQL
        ↓
Grafana

---

## 3. P9 Responsibilities

P9 is responsible for:

- Building a semantic query from telemetry information
- Sending the query to the P8 semantic retrieval layer
- Retrieving configurable Top-K knowledge chunks
- Validating retrieved results
- Preserving document and chunk metadata
- Grouping retrieved chunks by document
- Building structured RAG context
- Returning a complete structured retrieval output
- Handling invalid and empty queries
- Providing automated tests

P9 does NOT implement:

- Local LLM generation
- Final fault diagnosis
- MQTT integration
- Spring Boot integration
- React frontend
- Grafana integration
- Diagnosis database

---

## 4. Components

### query_builder.py

Converts telemetry data into a natural-language semantic query.

Example:

Input:

{
    "device_id": "MOTOR_01",
    "temperature": 92.4,
    "humidity": 43.2,
    "vibration": 8.1,
    "current": 12.7,
    "pressure": 2.4
}

Generated query:

Device MOTOR_01 has temperature 92.4°C,
humidity 43.2%, vibration 8.1,
current 12.7 A, pressure 2.4 bar.
Identify relevant industrial faults.

---

### retriever.py

Provides the P9 retrieval interface.

It reuses the P8 `SemanticSearchEngine` rather than implementing
another vector-search system.

The retriever supports configurable Top-K retrieval.

---

### result_processor.py

Validates and structures the results returned by P8.

It preserves:

- rank
- chunk ID
- document ID
- document type
- title
- source
- distance
- similarity
- text
- metadata

It can also group chunks by document ID.

---

### context_builder.py

Converts processed retrieval results into a structured textual
context.

Example structure:

Knowledge Source 1
Title: Excessive Motor Vibration
Document ID: FAULT-005
Source: faults/motor-vibration.md
Similarity: 0.7814

[Retrieved knowledge]

---

### rag_pipeline.py

Acts as the main P9 orchestrator.

It connects:

Query
  ↓
Retriever
  ↓
Result Processor
  ↓
Context Builder
  ↓
Structured RAG Output

Example:

pipeline = RAGPipeline(top_k=5)

output = pipeline.run(
    "The motor temperature is very high and the vibration is excessive."
)

The output contains:

- query
- result_count
- results
- context

---

## 5. Example Retrieval

Example query:

The motor temperature is very high and the vibration is excessive.
What could be the problem?

The P8 vector database retrieves relevant knowledge such as:

- Excessive Motor Vibration
- Motor Overheating
- Bearing Overheating

Multiple chunks from the same document can be retained because
different chunks may contain different useful information such as
causes, sensor indicators, recommended checks, safety information,
or related faults.

---

## 6. Testing

P9 contains automated tests for:

- Query Builder
- Retriever
- Result Processor
- Context Builder
- Complete RAG Pipeline

Final test result:

30 tests passed.

Test breakdown:

| Component | Tests |
|-----------|------:|
| Query Builder | 5 |
| Retriever | 6 |
| Result Processor | 6 |
| Context Builder | 7 |
| RAG Pipeline | 6 |
| Total | 30 |

All P9 tests passed successfully.

---

## 7. Dependencies

P9 reuses the existing P8 infrastructure:

- ChromaDB
- P8 SemanticSearchEngine
- Ollama embedding service
- nomic-embed-text
- Existing P8 vector collection

No cloud LLM or cloud embedding API is required by P9.

---

## 8. Boundary with P10/P11

P9 produces knowledge context.

It does not answer:

"What is the final fault?"

The future Local LLM stage will consume the retrieved context
and generate an explanation/diagnosis.

Therefore:

P8 = Store and search knowledge

P9 = Retrieve and prepare knowledge context

P10 = Local LLM capability

P11 = RAG + Local LLM integration

P12 = Diagnosis Engine
