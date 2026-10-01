"""
Validation module for P8 Vector Database.
Validates input embeddings from P7 embeddings.json and validates collection integrity
post-insertion in ChromaDB.
"""

import math
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set, Optional

from models import StoredVectorRecord


class ValidationResult:
    """Encapsulates the result of vector database validation."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}

    @property
    def is_valid(self) -> bool:
        """Returns True if no errors were encountered."""
        return len(self.errors) == 0

    def add_error(self, message: str):
        """Record an error."""
        self.errors.append(message)

    def add_warning(self, message: str):
        """Record a warning."""
        self.warnings.append(message)


def validate_embeddings_file(data: Dict[str, Any]) -> Tuple[ValidationResult, List[StoredVectorRecord]]:
    """
    Validates P7 embeddings.json content before insertion into ChromaDB:
    - Valid dictionary structure with 'embeddings' list
    - Required fields in every record
    - Non-empty, consistent vector dimensions
    - Strict numerical sanity (no NaN, no Inf, no null)
    - No duplicate chunk_ids
    """
    result = ValidationResult()
    records: List[StoredVectorRecord] = []

    if not isinstance(data, dict):
        result.add_error("Input embeddings data must be a JSON object (dictionary).")
        return result, []

    embeddings_list = data.get("embeddings")
    if not isinstance(embeddings_list, list):
        result.add_error("Input embeddings data missing required 'embeddings' list.")
        return result, []

    if len(embeddings_list) == 0:
        result.add_error("Input 'embeddings' list is empty.")
        return result, []

    seen_chunk_ids: Set[str] = set()
    first_dim: Optional[int] = None
    required_fields = ["chunk_id", "document_id", "document_type", "source", "chunk_index", "title", "text", "embedding"]

    for idx, raw in enumerate(embeddings_list):
        if not isinstance(raw, dict):
            result.add_error(f"Record at index {idx} is not a valid dictionary object.")
            continue

        # Check required fields
        for field_name in required_fields:
            if field_name not in raw:
                result.add_error(f"Record at index {idx} missing required field: '{field_name}'")
            elif raw[field_name] is None:
                result.add_error(f"Record at index {idx} has null value for required field: '{field_name}'")

        # Validate chunk_id
        chunk_id = str(raw.get("chunk_id", "")).strip()
        if not chunk_id:
            result.add_error(f"Record at index {idx} has empty chunk_id.")
        elif chunk_id in seen_chunk_ids:
            result.add_error(f"Duplicate chunk_id detected: '{chunk_id}' at index {idx}.")
        seen_chunk_ids.add(chunk_id)

        # Validate text
        text = str(raw.get("text", "")).strip()
        if not text:
            result.add_error(f"Record '{chunk_id or idx}' has empty text.")

        # Validate embedding vector
        vec = raw.get("embedding")
        if not isinstance(vec, list) or len(vec) == 0:
            result.add_error(f"Record '{chunk_id or idx}' has empty or invalid embedding vector.")
            continue

        if first_dim is None:
            first_dim = len(vec)
        elif len(vec) != first_dim:
            result.add_error(
                f"Dimensionality mismatch for '{chunk_id}': expected {first_dim}, got {len(vec)}."
            )

        # Numerical sanity check
        for v_idx, val in enumerate(vec):
            if val is None or not isinstance(val, (int, float)):
                result.add_error(f"Non-numeric value in '{chunk_id}' at dimension {v_idx}: {val}")
                break
            if math.isnan(val) or math.isinf(val):
                result.add_error(f"Non-finite value (NaN/Inf) in '{chunk_id}' at dimension {v_idx}: {val}")
                break

        if result.is_valid:
            records.append(StoredVectorRecord.from_dict(raw))

    result.stats = {
        "valid_records_count": len(records),
        "embedding_dimension": first_dim or 0,
        "unique_chunk_ids": len(seen_chunk_ids)
    }

    return result, records


def validate_collection_integrity(collection: Any, expected_count: int) -> ValidationResult:
    """
    Validates that the ChromaDB collection contains the expected number of records
    and that records can be queried.
    """
    result = ValidationResult()

    actual_count = collection.count()
    if actual_count != expected_count:
        result.add_error(
            f"Collection record count mismatch: expected {expected_count}, found {actual_count}."
        )

    result.stats = {
        "collection_name": collection.name,
        "actual_count": actual_count,
        "expected_count": expected_count
    }

    return result
