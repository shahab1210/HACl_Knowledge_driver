"""
Loader module for P8 Vector Database.
Reads and validates P7 embeddings.json, maps records to StoredVectorRecord models,
and idempotently upserts them into persistent ChromaDB.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from config import EMBEDDINGS_FILE
from models import StoredVectorRecord
from database import ChromaManager
from validator import validate_embeddings_file, validate_collection_integrity


def load_embeddings_into_chroma(
    embeddings_file: Optional[str] = None,
    chroma_manager: Optional[ChromaManager] = None
) -> Dict[str, Any]:
    """
    Loads, validates, and idempotently upserts embeddings from P7 embeddings.json into ChromaDB.
    Returns statistical report dictionary.
    """
    file_path = Path(embeddings_file or EMBEDDINGS_FILE).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"Embeddings source file does not exist: {file_path}")

    # Step 1: Read JSON
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Step 2: Validate structure and vectors
    val_res, records = validate_embeddings_file(raw_data)
    if not val_res.is_valid:
        error_msg = "; ".join(val_res.errors)
        raise ValueError(f"Embeddings validation failed: {error_msg}")

    # Step 3: Get or create ChromaDB manager
    manager = chroma_manager or ChromaManager()

    # Step 4: Idempotently upsert records
    upserted_count = manager.upsert_records(records)

    # Step 5: Post-insertion collection validation
    col_val = validate_collection_integrity(manager.collection, expected_count=len(records))
    if not col_val.is_valid:
        error_msg = "; ".join(col_val.errors)
        raise RuntimeError(f"Post-insertion collection validation failed: {error_msg}")

    return {
        "status": "SUCCESS",
        "collection_name": manager.collection_name,
        "input_source": str(file_path),
        "records_loaded": upserted_count,
        "total_collection_count": manager.count(),
        "embedding_dimension": val_res.stats.get("embedding_dimension", 0),
        "chroma_path": manager.chroma_path,
        "distance_metric": manager.metric
    }
