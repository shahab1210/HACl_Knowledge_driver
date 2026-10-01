#!/usr/bin/env python3
"""
CLI entry point for P7 Embedding Generation.
Loads P6 chunks.json, connects to local Ollama embedding service, generates dense vectors,
validates dimensionality and numerical sanity, and writes ai/embeddings/output/embeddings.json.
"""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import ChunkRecord, EmbeddingRecord, EmbeddingOutput
from client import (
    OllamaClient,
    OllamaClientError,
    OllamaConnectionError,
    OllamaModelNotFoundError
)
from validator import validate_chunks_input, validate_embeddings_output


def run_embedding_pipeline(
    input_file: Path,
    output_file: Path,
    model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
    batch_size: int = 16,
    client: Optional[OllamaClient] = None
) -> bool:
    """
    Executes the P7 embedding generation pipeline.
    Returns True on success, False if validation or embedding generation fails.
    """
    input_file = input_file.resolve()
    output_file = output_file.resolve()

    # Step 1: Load and validate chunks.json
    if not input_file.exists():
        print(f"ERROR: Input chunks file does not exist: {input_file}", file=sys.stderr)
        return False

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse JSON from {input_file}: {e}", file=sys.stderr)
        return False

    val_res, chunks = validate_chunks_input(raw_data)
    if not val_res.is_valid:
        print("ERROR: Input chunks validation failed:", file=sys.stderr)
        for err in val_res.errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    # Extract distinct document count
    doc_ids = {c.document_id for c in chunks}
    document_count = len(doc_ids)
    chunk_count = len(chunks)

    # Step 2: Initialize Ollama client and verify service
    ollama = client or OllamaClient(base_url=base_url, model=model)

    print(f"Connecting to Ollama service at {ollama.base_url}...")
    if not ollama.is_server_running():
        print(f"ERROR: Ollama server is not running or unreachable at {ollama.base_url}", file=sys.stderr)
        print("Please start the Ollama service using: 'ollama serve' or 'brew services start ollama'", file=sys.stderr)
        return False

    print(f"Checking model availability: '{ollama.model}'...")
    if not ollama.is_model_available():
        available_models = ollama.list_models()
        print(f"ERROR: Model '{ollama.model}' is not installed in local Ollama instance.", file=sys.stderr)
        print(f"Currently available models: {available_models or 'None'}", file=sys.stderr)
        print(f"Please install the model by running: 'ollama pull {ollama.model}'", file=sys.stderr)
        return False

    # Step 3: Generate embeddings
    print(f"Generating embeddings for {chunk_count} chunks using model '{ollama.model}'...")
    embedding_records: List[EmbeddingRecord] = []

    # Process in batches
    for i in range(0, chunk_count, batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_texts = [c.text for c in batch_chunks]
        end_idx = min(i + batch_size, chunk_count)
        print(f"  - Processing chunks {i + 1}..{end_idx} of {chunk_count}...")

        try:
            vectors = ollama.embed_batch(batch_texts)
        except Exception as e:
            print(f"ERROR: Failed during batch embedding ({i + 1}..{end_idx}): {e}", file=sys.stderr)
            return False

        if len(vectors) != len(batch_chunks):
            print(
                f"ERROR: Vector count mismatch in batch ({i + 1}..{end_idx}): expected {len(batch_chunks)}, got {len(vectors)}",
                file=sys.stderr
            )
            return False

        for chunk_obj, vec in zip(batch_chunks, vectors):
            rec = EmbeddingRecord.from_chunk(chunk_obj, vec, ollama.model)
            embedding_records.append(rec)

    # Step 4: Validate generated embeddings
    out_val = validate_embeddings_output(embedding_records, chunk_count, ollama.model)
    if not out_val.is_valid:
        print("ERROR: Output embedding validation failed:", file=sys.stderr)
        for err in out_val.errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    detected_dimension = out_val.stats["embedding_dimension"]

    # Step 5: Serialize output to embeddings.json
    output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = EmbeddingOutput(
        generated_at=datetime.now(timezone.utc).isoformat(),
        source=str(input_file),
        embedding_model=ollama.model,
        document_count=document_count,
        chunk_count=chunk_count,
        embedding_dimension=detected_dimension,
        embeddings=embedding_records
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload.to_dict(), f, indent=2, ensure_ascii=False)

    # Step 6: Print formatted summary report
    print("========================================")
    print("P7 Embedding Pipeline")
    print("=====================")
    print()
    print(f"Input chunks:        {chunk_count}")
    print()
    print(f"Embedding model:     {ollama.model}")
    print()
    print(f"Embeddings generated:{len(embedding_records)}")
    print()
    print(f"Embedding dimension: {detected_dimension}")
    print()
    print("Validation:          PASSED")
    print()
    print("Output:")
    print(f"{output_file}")
    print("========================================")

    return True


def main():
    script_dir = Path(__file__).parent.resolve()
    default_input = script_dir.parent / "ingestion" / "output" / "chunks.json"
    default_output = script_dir / "output" / "embeddings.json"

    parser = argparse.ArgumentParser(
        description="P7 Embedding Layer: Generate local vector embeddings for P6 knowledge chunks."
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=default_input,
        help="Path to P6 chunks.json (default: ../ingestion/output/chunks.json)"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=default_output,
        help="Path to destination embeddings.json (default: output/embeddings.json)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="nomic-embed-text",
        help="Local Ollama embedding model name (default: nomic-embed-text)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Number of chunks to embed per request batch (default: 16)"
    )

    args = parser.parse_args()

    success = run_embedding_pipeline(
        input_file=args.input_file,
        output_file=args.output_file,
        model=args.model,
        base_url=args.base_url,
        batch_size=args.batch_size
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
