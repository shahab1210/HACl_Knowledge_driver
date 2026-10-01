# P6 — Document Ingestion Pipeline

## 1. Purpose of P6
The **P6 Document Ingestion Pipeline** transforms the curated Markdown knowledge base produced in **P5** into structured, normalized, and validated text chunks stored in a standard JSON format (`output/chunks.json`).

This pipeline bridges domain authoring (P5 Markdown documents) and downstream semantic vector representation (P7 Embeddings & Vector Database), ensuring that documents are properly parsed, enriched with structural metadata, and split into semantically coherent segments optimized for dense vector retrieval.

> [!IMPORTANT]
> **Strict Scope Boundary:**
> P6 is strictly a document ingestion and chunking module. P6 does **NOT** perform embedding generation, vector database indexing, vector similarity search, RAG orchestration, or LLM inference. Those capabilities are deferred to P7 and subsequent phases.

---

## 2. Why Python Is Used
Python was selected for the ingestion subsystem for the following engineering reasons:
- **Natural Markdown and Text Processing:** Python's rich text manipulation capabilities, regular expressions, and parsing libraries make it ideal for document processing.
- **Seamless Downstream AI/ML Compatibility:** Future embedding and vector database libraries (such as sentence-transformers, ChromaDB, PGvector, and LangChain/LlamaIndex) are native to the Python ecosystem.
- **Architectural Decoupling:** Keeping document ingestion and the AI/RAG pipeline in an independent Python environment ensures that the existing Spring Boot MQTT subscriber and PostgreSQL backend remain completely undisturbed.
- **Lightweight Dependencies:** The module relies almost exclusively on Python standard library modules (`dataclasses`, `pathlib`, `re`, `json`, `argparse`, `unittest`) with only `PyYAML` and `pytest` as minimal external dependencies.

---

## 3. Input Location
The ingestion pipeline reads all knowledge documents from the P5 Knowledge Base:

```
P_311/
└── ai/
    ├── knowledge-base/        # Input source directory
    │   ├── README.md          # Architectural guide (classified as documentation, excluded from diagnostic chunks)
    │   ├── faults/            # 10 fault dossier documents (*.md)
    │   ├── sensors/           # 5 sensor specification documents (*.md)
    │   └── procedures/        # 3 standard procedure documents (*.md)
    └── ingestion/             # P6 Ingestion Pipeline Root
```

---

## 4. Document Discovery
Document discovery is implemented in `parser.py` via `discover_documents()`:
- Recursively traverses `knowledge-base/` to discover all `*.md` files.
- Automatically handles directory nesting without hard-coded filenames, allowing future documents to be added seamlessly.
- **KB README Handling:** The knowledge base root `README.md` is explicitly classified as project documentation and excluded from diagnostic ingestion by default (`exclude_readme=True`). This ensures that administrative documentation does not pollute diagnostic knowledge chunks.

---

## 5. Metadata Extraction and Inference
The parser extracts and infers structured metadata for each discovered document:
- **Fault Documents (`faults/`):** Extracts YAML front-matter attributes (`id`, `title`, `category`, `equipment`, `severity`, `sensors`).
- **Sensor Documents (`sensors/`):** Infers `document_id` (`SENSOR-<NAME>`), extracts the title from the primary heading, sets `category="instrumentation"`, `equipment="sensor"`, and links the corresponding sensor telemetry channel.
- **Procedure Documents (`procedures/`):** Infers `document_id` (`PROC-<NAME>`), extracts the title from the primary heading, sets `category="procedure"`, infers target equipment (`motor`, `pump`, or `general`), and links applicable telemetry sensors.

Each parsed document produces a `Document` object (`models.py`) containing:
- `document_id`: Unique identifier (e.g., `FAULT-001`, `SENSOR-TEMPERATURE`, `PROC-MOTOR-INSPECTION`).
- `title`: Formal technical title.
- `document_type`: Classification (`fault`, `sensor`, `procedure`, or `documentation`).
- `source`: Relative file path within the knowledge base.
- `category`: Domain category (`mechanical`, `electrical`, `hydraulic`, `instrumentation`, `thermal`, `procedure`).
- `equipment`: Target asset (`motor`, `pump`, `sensor`, `general`).
- `severity`: Severity classification (`critical`, `high`, `medium`, `low`, or null).
- `sensors`: List of associated telemetry channels.
- `content`: Cleaned, normalized Markdown body.
- `metadata`: Raw front-matter dictionary and source attributes.

---

## 6. Text Normalization
Text normalization (`parser.py::normalize_text`) cleans raw document content while strictly preserving technical semantics:
- Strips YAML front-matter blocks from body text.
- Normalizes all line endings to Unix LF (`\n`).
- Trims trailing whitespace from each line.
- Collapses sequences of three or more blank lines into two newlines.
- **Strict Semantic Preservation:** Does **not** strip punctuation, remove mathematical notation (e.g., $I^2R$, $\Delta P$, $H = \frac{\Delta P}{\rho g}$), stem words, or alter Markdown headings, checklists, or tables.

---

## 7. Chunking Strategy
Chunking is implemented in `chunker.py` using a **Section-Aware Chunking Strategy**:
- **Initial Recommended Settings:**
  - `chunk_size_tokens`: 800 tokens equivalent (~600 words).
  - `chunk_overlap_tokens`: 100 tokens equivalent (~75 words).
  - `tokens_per_word`: 1.33 (standard English technical text conversion).
- **Section Preservation:**
  - Documents are split into semantic units along Markdown headings (`## Section Name`).
  - Headings remain bound to their respective bodies (e.g., `## Sensor Indicators` stays bound to its Markdown table; `## Recommended Checks` stays bound to its checklist).
  - If an entire document fits within the target token size (such as 550–600 words), it is retained as a single, complete chunk.
  - If a document exceeds the target token size, sections are grouped into sequential chunks up to `max_words`.
  - Oversized sections are safely split along paragraph (`\n\n`) boundaries.
  - Adjacent chunks carry over `overlap_words` to maintain cross-chunk semantic continuity.
  - Every subsequent chunk is prepended with the document title context (`# <Document Title>`) so dense embeddings retain asset identification.

---

## 8. Chunk Metadata Schema
Every generated chunk object contains complete traceability back to its source document:

```json
{
  "chunk_id": "FAULT-001_chunk_001",
  "document_id": "FAULT-001",
  "document_type": "fault",
  "source": "faults/bearing-overheating.md",
  "chunk_index": 0,
  "title": "Bearing Overheating",
  "category": "mechanical",
  "equipment": "motor",
  "severity": "high",
  "sensors": [
    "temperature",
    "vibration",
    "current"
  ],
  "text": "# Bearing Overheating\n\n## Description...",
  "section_heading": null,
  "token_estimate": 734
}
```

---

## 9. Output Format (`output/chunks.json`)
The complete ingestion output is saved to `output/chunks.json` with the following top-level structure:

```json
{
  "generated_at": "2026-09-30T06:18:11.758826+00:00",
  "source_directory": "/.../ai/knowledge-base",
  "chunk_size_tokens": 800,
  "chunk_overlap_tokens": 100,
  "document_count": 18,
  "chunk_count": 32,
  "chunks": [ ... ]
}
```

---

## 10. Validation Rules
The validation module (`validator.py`) enforces strict data integrity:
1. Knowledge-base directory exists and contains discovered Markdown files.
2. Exactly 18 domain knowledge documents are processed (10 faults, 5 sensors, 3 procedures).
3. Root `README.md` is excluded from diagnostic chunks.
4. Every fault document possesses a unique ID starting with `FAULT-`.
5. All required metadata fields (`category`, `equipment`, `severity`, `sensors`) are present in fault documents.
6. Every chunk has a unique `chunk_id`.
7. Every chunk has valid `source`, `document_id`, `document_type`, and non-empty `text`.
8. Chunk indexes start at 0 and form a strictly continuous sequence for every document.
9. No duplicate chunk IDs exist across the dataset.

---

## 11. Testing and Execution

### Running the Ingestion Pipeline
From the `ai/ingestion` directory:
```bash
# Using python directly:
python3 ingest.py

# Or using the local virtual environment:
./.venv/bin/python ingest.py
```

### Optional Command Line Arguments
```bash
python3 ingest.py --help
# Options:
#   --kb-dir PATH          Custom path to knowledge-base
#   --output-file PATH     Custom destination for chunks.json
#   --chunk-size INT       Target tokens per chunk (default: 800)
#   --chunk-overlap INT    Target overlap tokens (default: 100)
#   --include-readme       Include KB README.md in ingestion
```

### Running Automated Tests
```bash
# Run via pytest (venv):
./.venv/bin/pytest tests/ -v

# Run via Python built-in unittest:
python3 -m unittest discover -s tests
```

---

## 12. How P7 Will Consume `chunks.json`
In the subsequent phase (**P7 — Embeddings & Vector Storage**):
1. **P7 Loader:** Reads `ai/ingestion/output/chunks.json`.
2. **Dense Embeddings:** Iterates over `chunks`, passing each chunk's `text` to an embedding model (such as `all-MiniLM-L6-v2` or `nomic-embed-text`) to compute a dense vector representation (e.g., 384 or 768 dimensions).
3. **Vector Database Ingestion:** Inserts the vector along with the chunk metadata (`chunk_id`, `document_id`, `document_type`, `category`, `equipment`, `severity`, `sensors`, `source`) into a vector index (ChromaDB / PGvector / Qdrant).
4. **Metadata Filtering:** When live telemetry from `ESP32_001` flags high vibration on a motor, P7/P8 can execute a hybrid query:
   - Filter: `equipment == "motor"` AND `sensors CONTAINS "vibration"`
   - Semantic Vector Search: Match live anomaly symptoms against indexed chunk text.
