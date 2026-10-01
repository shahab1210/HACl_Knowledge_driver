# P8 — Vector Database (ChromaDB)

## 1. What a Vector Database Is
A **Vector Database** is a specialized storage and indexing system engineered to manage high-dimensional vector embeddings. Unlike relational databases (which index scalar strings or numbers using B-trees) or document databases, a vector database indexes dense mathematical vectors using **Approximate Nearest Neighbor (ANN)** indexing algorithms (such as HNSW — Hierarchical Navigable Small World graphs). This enables sub-millisecond similarity queries across continuous vector space.

---

## 2. Why P_311 Needs a Vector Database
In **P_311 (Knowledge-Driven IoT Fault Diagnosis Assistant)**, real-time sensor anomalies (e.g., vibration surges, motor thermal escalation, hydraulic pressure loss) must be resolved against domain knowledge.

A vector database provides:
- **Instant Semantic Lookups:** Maps incoming telemetry descriptions to the most relevant knowledge chunks out of the entire knowledge corpus.
- **Hybrid Metadata Filtering:** Allows filtering by equipment type (e.g. `equipment == "pump"`) or telemetry channels (e.g. `sensors CONTAINS "vibration"`) combined with dense semantic search.
- **Decoupled Architecture:** Serves as the persistent knowledge index connecting P7 vectorization with P9 Retrieval-Augmented Generation (RAG).

### Conceptual Architecture
```
       Knowledge Chunks (P6)
                 ↓
       P7 Local Embeddings (768-dim)
                 ↓
       Persistent ChromaDB Collection (P8)
                 ↓
          Similarity Search
                 ↓
       Top-K Relevant Chunks
                 ↓
       P9 Retrieval-Augmented Generation (RAG)
```

---

## 3. Why ChromaDB Was Selected
- **100% Local & Embedded:** Runs directly in-process within Python; requires no external cloud accounts, API keys, or heavy external daemon clusters.
- **Built-in HNSW Indexing:** Provides fast approximate nearest neighbor search optimized for dense vector spaces.
- **Local SQLite / Parquet Persistence:** The entire database is stored on disk in `ai/vector-db/data/chroma/`, surviving system restarts.
- **Clean Separation of Concerns:** ChromaDB acts strictly as a storage and search index, separating vector retrieval from LLM inference.

---

## 4. Input from P7 (`ai/embeddings/output/embeddings.json`)
P8 strictly consumes the validated output of Phase 7:
```
P5 Knowledge Base (Markdown)
             ↓
P6 Document Ingestion (chunks.json)
             ↓
P7 Local Embeddings (embeddings.json)
             ↓
P8 Vector Database (ChromaDB)
```

> [!IMPORTANT]
> **P8 does not regenerate embeddings for knowledge chunks.**
> P7 is the single source of truth for all 32 knowledge vectors.

---

## 5. Collection Structure
- **Collection Name:** `iot_fault_knowledge`
- **Document ID:** Uses P7 `chunk_id` directly (e.g., `FAULT-001_chunk_001`). No random or detached IDs are generated, ensuring complete end-to-end traceability back to the P5 Markdown source file.
- **Document Text:** The full normalized chunk text is stored in the `document` field, allowing downstream P9 RAG prompts to incorporate verbatim knowledge without re-reading files from disk.
- **Vector Record Count:** Exactly 32 vectors (768 dimensions each).

---

## 6. Metadata Storage
Each vector record in ChromaDB is enriched with metadata attributes:
- `document_id`: e.g. `FAULT-001`, `SENSOR-TEMPERATURE`, `PROC-PUMP-INSPECTION`
- `document_type`: `fault`, `sensor`, `procedure`
- `source`: e.g. `faults/bearing-overheating.md`
- `chunk_index`: integer (0, 1, ...)
- `title`: e.g. `Bearing Overheating`
- `category`: `mechanical`, `electrical`, `hydraulic`, `thermal`, `instrumentation`, `procedure`
- `equipment`: `motor`, `pump`, `sensor`, `general`
- `severity`: `critical`, `high`, `medium`, `low`, or empty
- `sensors`: Comma-separated list of sensitive telemetry channels (e.g. `"temperature,vibration,current"`)
- `embedding_model`: `"nomic-embed-text"`

*Serialization Note:* Because ChromaDB requires primitive metadata types (`str`, `int`, `float`, `bool`), the `sensors` list is serialized as a deterministic comma-delimited string (e.g., `"temperature,vibration,current"`), ensuring zero metadata loss.

---

## 7. Persistence
ChromaDB is configured in persistent disk mode (`PersistentClient`):
- **Storage Location:** `ai/vector-db/data/chroma/`
- Records persist across application shutdowns and server reboots.
- Opening the database at any future time immediately restores the full 32-record collection without re-indexing.

---

## 8. Distance Metric & Similarity Interpretation
The collection is explicitly configured with the **Cosine Distance** metric (`metadata={"hnsw:space": "cosine"}`):
- **Cosine Distance ($D_c$):**
  $$D_c = 1 - \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
  - Range: `0.0` (identical orientation) to `2.0` (opposite orientation).
  - Lower distance values represent higher semantic similarity.
- **Derived Cosine Similarity ($S_c$):**
  $$S_c = 1.0 - D_c$$
  - Normalized between `0.0` and `1.0` for positive cosine space.
  - Reported alongside raw distance for operator readability.

> [!NOTE]
> Cosine distance measures vector angular orientation rather than magnitude, which makes it ideal for semantic text embeddings where passage lengths vary.

---

## 9. Query Embedding Flow
When an operator or automated telemetry alert submits a natural language search query:
```
User / Telemetry Query:
"motor has high temperature and increased vibration"
                       ↓
   Local Ollama Service (http://localhost:11434)
             (Model: nomic-embed-text)
                       ↓
         768-dimensional Query Vector
                       ↓
          ChromaDB Collection Query
                       ↓
         Ranked Top-K Search Results
```
The vector database does **not** invent or substitute an embedding model; it utilizes the exact same local Ollama model (`nomic-embed-text`) that generated the knowledge base embeddings in P7.

---

## 10. Idempotent Loading
The loader (`loader.py`) implements idempotent upsert logic:
- Uses deterministic `chunk_id` keys (`FAULT-001_chunk_001`).
- Running `python3 cli.py load` once inserts 32 records.
- Running `python3 cli.py load` again updates existing records in place, maintaining a total count of exactly 32 (preventing duplication to 64).

---

## 11. CLI Commands & Usage

### 1. Load Embeddings into ChromaDB
```bash
./.venv/bin/python cli.py load
```
Output:
```
========================================
Loading Status:       SUCCESS
Collection:           iot_fault_knowledge
Records loaded:       32
Total in collection:  32
Vector dimension:     768
Distance metric:      cosine
ChromaDB location:    /path/to/ai/vector-db/data/chroma
========================================
```

### 2. Inspect Collection Statistics
```bash
./.venv/bin/python cli.py stats
```

### 3. Run Semantic Similarity Search
```bash
./.venv/bin/python cli.py search "motor has high temperature and increased vibration" --top-k 3
```

---

## 12. Automated Testing
The test suite in `tests/` tests all database operations without requiring an active Ollama daemon:
- `test_database.py`: Tests `ChromaManager` collection creation, upserting, query ordering, distance metrics, and persistence across manager restarts.
- `test_loader.py`: Tests JSON loading, validation, error handling, and idempotent upserts.
- `test_search.py`: Tests `SemanticSearchEngine` query flow, top-K slicing, field population, and empty query validation using a deterministic test double (`FakeOllamaClient`).
- `test_validator.py`: Tests schema constraints, duplicate prevention, and NaN/Inf vector validation.

Run tests:
```bash
./.venv/bin/pytest tests/ -v
```

---

## 13. How P9 RAG Will Consume Search Results
In Phase 9 (Retrieval-Augmented Generation):
1. **Anomaly Trigger:** Telemetry rule engine detects `vibration=4.8 mm/s`, `temperature=88 °C`.
2. **Context Retrieval:** P9 calls `SemanticSearchEngine.search("elevated motor vibration and high bearing temperature", top_k=3)`.
3. **Prompt Augmentation:** P9 formats the retrieved `SearchResult.text` into an LLM context block:
   ```
   [Context from Knowledge Base]:
   - FAULT-001: Bearing Overheating (symptoms, causes, checklist)
   - FAULT-005: Excessive Motor Vibration (symptoms, causes, checklist)
   ```
4. **Local LLM Inference:** Local Ollama model synthesizes diagnostic findings and recommended checks grounded strictly in verified domain knowledge.
