# P_311 — AI & Knowledge-Driven RAG Pipeline Specification

This document details the Artificial Intelligence, Vector Database, Semantic Retrieval, and Large Language Model architecture implemented across phases P5–P12.

---

## 1. RAG Architecture Overview

Retrieval-Augmented Generation (RAG) grounds generative AI reasoning in authoritative domain knowledge. In P_311, raw IoT telemetry is transformed into structured diagnostic intelligence through a 7-stage pipeline:

```text
1. Curated Knowledge Base (Markdown manuals in P5)
                  ↓
2. Document Ingestion & Semantic Chunking (P6)
                  ↓
3. Dense Vector Embedding via nomic-embed-text (P7)
                  ↓
4. ChromaDB Vector Database Indexing (P8)
                  ↓
5. Telemetry Query Construction & Similarity Search (P9)
                  ↓
6. Context Assembly & Grounded Prompt Synthesis (P10/P11)
                  ↓
7. LLM Inference via qwen2.5:1.5b & Pydantic Output Validation (P12)
```

---

## 2. Document Ingestion & Chunking (P6)

The ingestion pipeline (`ai/ingestion/`) converts technical maintenance documents into searchable chunks:
- **Chunking Strategy:** Heading-aware recursive semantic splitting. Chunks preserve markdown hierarchy (H1, H2, H3), ensuring tables, sensor thresholds, and maintenance instructions remain intact within individual chunks.
- **Chunk Size & Overlap:** Chunks average 300–600 tokens with a 50-token semantic overlap to avoid information truncation across boundaries.
- **Metadata Tagging:** Each chunk is tagged with:
  - `document_id`: E.g., `FAULT-001`, `SENSOR-TEMPERATURE`.
  - `chunk_id`: E.g., `FAULT-001_chunk_001`.
  - `title`: Human-readable title.
  - `category`: `fault`, `sensor`, or `procedure`.
  - `source`: Relative file path.

---

## 3. Embedding Model (P7)

- **Model:** `nomic-embed-text` (latest release)
- **Serving Runtime:** Local Ollama daemon (`http://localhost:11434/api/embeddings`)
- **Dimensionality:** 768 floating-point dimensions.
- **Vector Normalization:** L2 normalized (`||v|| = 1.0`), enabling exact cosine similarity computation via standard dot product.
- **Preprocessing:** Query text is prefixed with domain-specific search intent: `search_query: <text>` to optimize bi-encoder attention masks.

---

## 4. ChromaDB Vector Store (P8)

- **Vector Database:** ChromaDB (embedded Python runtime)
- **Storage Location:** `ai/vector-db/data/chroma/` (persistent disk storage)
- **Collection Name:** `iot_fault_knowledge` (32 indexed chunks across 18 domain files)
- **Distance Metric:** Cosine distance ($D_{cosine} = 1 - \cos(\theta)$).
- **Index Type:** Hierarchical Navigable Small World (HNSW) graph for fast nearest-neighbor retrieval.

---

## 5. Semantic Retrieval Pipeline (P9)

1. **`QueryBuilder`:** Formats incoming numerical telemetry into an information-dense query:
   ```text
   "Device ESP32_001 telemetry observation: temperature is 96.0 °C, vibration is 7.2 mm/s, current is 11.0 A, pressure is 2.1 bar, humidity is 45.0 %. What is the equipment fault diagnosis, root cause, and recommended action?"
   ```
2. **`Retriever`:**
   - Queries ChromaDB with $k=3$ (top-3 most similar chunks).
   - Extracts document text, metadata, and computes similarity score: $\text{similarity} = 1.0 - \text{distance}$.
3. **`ContextBuilder`:**
   - Formats the retrieved chunks into clean markdown sections tagged with chunk identifiers for strict LLM context referencing.

---

## 6. Local Large Language Model & Prompting (P10, P11)

- **Model:** `qwen2.5:1.5b` (Q4_K_M quantized, 1.5B parameters)
- **Inference Runtime:** Local Ollama REST API (`/api/generate`)
- **Temperature:** `0.1` (low temperature ensures deterministic, factual adherence).
- **System Prompt Design:**
  The system prompt instructs the model to act as an industrial maintenance expert:
  - Rely exclusively on the provided technical context chunks.
  - Do NOT hallucinate unobserved sensor parameters or invented failure modes.
  - Cite the specific knowledge chunk ID for every conclusion.
  - Output sections covering: Equipment Fault Diagnosis, Root Cause Analysis, and Recommended Actions.

---

## 7. Structured Diagnosis Engine & Parsing (P12)

The `DiagnosisEngine` (`ai/diagnosis/src/engine.py`) post-processes the generative response into a validated JSON structure:
- **Fault Extraction:** Scans response for standardized fault patterns (`FAULT-001` through `FAULT-005`) and compares them against top retrieved chunks.
- **Confidence Computation:**
  - `HIGH`: Primary fault matched in context with similarity $\ge 0.80$ and physical evidence corroborates threshold exceedance.
  - `MEDIUM`: Primary fault identified with similarity between $0.65$ and $0.80$.
  - `LOW`: Query does not match any specific fault document; transparently indicates uncertainty.
- **Evidence Mapping:** Maps all 5 incoming telemetry variables into structured evidence rows.
- **Action Items Extraction:** Parses recommended checks and inspection procedures into clean bullet arrays for field technicians.
