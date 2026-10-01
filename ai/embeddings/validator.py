"""
Validation module for P7 Embeddings.
Validates input chunks from P6 against required schemas and validates generated embeddings
for dimensionality consistency, numerical sanity (finite, non-NaN), and metadata completeness.
"""

import math
from typing import List, Dict, Any, Tuple, Set, Optional
from models import ChunkRecord, EmbeddingRecord


class ValidationResult:
    """Encapsulates the result of embedding validation."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}

    @property
    def is_valid(self) -> bool:
        """Returns True if no validation errors occurred."""
        return len(self.errors) == 0

    def add_error(self, message: str):
        """Record an error."""
        self.errors.append(message)

    def add_warning(self, message: str):
        """Record a warning."""
        self.warnings.append(message)


def validate_chunks_input(data: Dict[str, Any]) -> Tuple[ValidationResult, List[ChunkRecord]]:
    """
    Validates that P6 chunks.json data satisfies all required schema constraints.
    Returns (ValidationResult, List[ChunkRecord]).
    """
    result = ValidationResult()
    chunk_records: List[ChunkRecord] = []

    if not isinstance(data, dict):
        result.add_error("Input chunks data must be a JSON object (dictionary).")
        return result, []

    raw_chunks = data.get("chunks")
    if not isinstance(raw_chunks, list):
        result.add_error("Input chunks data missing required 'chunks' list.")
        return result, []

    if len(raw_chunks) == 0:
        result.add_error("Input 'chunks' list is empty.")
        return result, []

    seen_chunk_ids: Set[str] = set()
    required_fields = ["chunk_id", "document_id", "document_type", "source", "chunk_index", "title", "text"]

    for idx, raw in enumerate(raw_chunks):
        if not isinstance(raw, dict):
            result.add_error(f"Chunk at index {idx} is not a valid dictionary object.")
            continue

        # Check required fields
        for field_name in required_fields:
            if field_name not in raw:
                result.add_error(f"Chunk at index {idx} missing required field: '{field_name}'")
            elif raw[field_name] is None:
                result.add_error(f"Chunk at index {idx} has null value for required field: '{field_name}'")

        # Specific field validations
        chunk_id = str(raw.get("chunk_id", "")).strip()
        if not chunk_id:
            result.add_error(f"Chunk at index {idx} has empty or blank chunk_id.")
        elif chunk_id in seen_chunk_ids:
            result.add_error(f"Duplicate chunk_id detected: '{chunk_id}' at index {idx}.")
        seen_chunk_ids.add(chunk_id)

        text = str(raw.get("text", "")).strip()
        if not text:
            result.add_error(f"Chunk '{chunk_id or idx}' has empty or whitespace-only text.")

        if result.is_valid:
            record = ChunkRecord.from_dict(raw)
            chunk_records.append(record)

    result.stats = {
        "input_chunks_count": len(chunk_records),
        "unique_chunk_ids": len(seen_chunk_ids)
    }

    return result, chunk_records


def validate_embeddings_output(
    embeddings: List[EmbeddingRecord],
    expected_chunk_count: int,
    expected_model: str
) -> ValidationResult:
    """
    Validates generated EmbeddingRecords:
    - Number of embeddings matches expected count
    - All vectors are non-empty and strictly numeric
    - Dimensionality is consistent across all records and > 0
    - All vector values are finite (no NaN, no Inf)
    - Metadata and chunk_id integrity preserved
    - Model name is recorded
    """
    result = ValidationResult()

    if len(embeddings) != expected_chunk_count:
        result.add_error(
            f"Embedding count mismatch: expected {expected_chunk_count} embeddings, got {len(embeddings)}."
        )

    if not embeddings:
        result.add_error("No embeddings provided for output validation.")
        return result

    first_dim = embeddings[0].embedding_dimension
    if first_dim <= 0:
        result.add_error(f"Invalid detected embedding dimension: {first_dim} (must be > 0).")

    seen_ids: Set[str] = set()

    for idx, emb in enumerate(embeddings):
        # Check chunk ID
        if not emb.chunk_id or not emb.chunk_id.strip():
            result.add_error(f"EmbeddingRecord at index {idx} has empty chunk_id.")
        elif emb.chunk_id in seen_ids:
            result.add_error(f"Duplicate chunk_id in embeddings: '{emb.chunk_id}'")
        seen_ids.add(emb.chunk_id)

        # Check model name
        if not emb.embedding_model or not emb.embedding_model.strip():
            result.add_error(f"EmbeddingRecord '{emb.chunk_id}' missing embedding_model.")
        elif expected_model and not (
            emb.embedding_model.lower() == expected_model.lower() or
            emb.embedding_model.lower().startswith(expected_model.lower()) or
            expected_model.lower().startswith(emb.embedding_model.lower())
        ):
            result.add_warning(
                f"Embedding model mismatch for '{emb.chunk_id}': expected '{expected_model}', got '{emb.embedding_model}'"
            )

        # Check vector consistency
        vector = emb.embedding
        if not isinstance(vector, list) or len(vector) == 0:
            result.add_error(f"EmbeddingRecord '{emb.chunk_id}' has empty or invalid embedding vector.")
            continue

        if len(vector) != first_dim:
            result.add_error(
                f"Dimensionality mismatch for '{emb.chunk_id}': expected {first_dim}, got {len(vector)}."
            )

        if emb.embedding_dimension != len(vector):
            result.add_error(
                f"Dimension metadata mismatch for '{emb.chunk_id}': field says {emb.embedding_dimension}, vector has {len(vector)}."
            )

        # Semantic/numerical sanity check: finite floats, no NaN, no Inf
        for v_idx, val in enumerate(vector):
            if val is None or not isinstance(val, (int, float)):
                result.add_error(f"Non-numeric value in vector '{emb.chunk_id}' at dimension {v_idx}: {val}")
                break
            if math.isnan(val) or math.isinf(val):
                result.add_error(f"Non-finite value (NaN/Inf) in vector '{emb.chunk_id}' at dimension {v_idx}: {val}")
                break

        # Check required text and metadata
        if not emb.text or not emb.text.strip():
            result.add_error(f"EmbeddingRecord '{emb.chunk_id}' has empty text.")
        if not emb.document_id:
            result.add_error(f"EmbeddingRecord '{emb.chunk_id}' missing document_id.")
        if not emb.source:
            result.add_error(f"EmbeddingRecord '{emb.chunk_id}' missing source.")

    result.stats = {
        "total_embeddings": len(embeddings),
        "embedding_dimension": first_dim,
        "embedding_model": expected_model,
        "unique_chunk_ids": len(seen_ids)
    }

    return result
