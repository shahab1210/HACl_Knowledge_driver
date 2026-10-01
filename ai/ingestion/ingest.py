#!/usr/bin/env python3
"""
CLI entry point for P6 Document Ingestion.
Discovers knowledge documents, extracts metadata, normalizes text,
generates section-aware chunks, validates integrity, and writes chunks.json.
"""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

from parser import discover_documents, parse_markdown_file
from chunker import MarkdownChunker
from validator import validate_knowledge_base, validate_documents, validate_chunks


def run_ingestion(
    kb_dir: Path,
    output_path: Path,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    include_readme: bool = False
) -> bool:
    """
    Executes the document ingestion pipeline.
    Returns True on success, False if validation fails.
    """
    kb_dir = kb_dir.resolve()
    output_path = output_path.resolve()

    # Step 1: Discover documents
    try:
        discovered_files = discover_documents(kb_dir, exclude_readme=not include_readme)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False

    kb_val = validate_knowledge_base(kb_dir, discovered_files)
    if not kb_val.is_valid:
        print("ERROR: Knowledge base validation failed:", file=sys.stderr)
        for err in kb_val.errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    # Step 2: Parse and normalize documents
    documents = []
    for file_path in discovered_files:
        doc = parse_markdown_file(file_path, kb_dir)
        documents.append(doc)

    doc_val = validate_documents(documents, kb_dir)
    if not doc_val.is_valid:
        print("ERROR: Document validation failed:", file=sys.stderr)
        for err in doc_val.errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    # Step 3: Chunk documents
    chunker = MarkdownChunker(
        chunk_size_tokens=chunk_size,
        chunk_overlap_tokens=chunk_overlap
    )

    all_chunks = []
    for doc in documents:
        doc_chunks = chunker.chunk_document(doc)
        all_chunks.extend(doc_chunks)

    # Step 4: Validate chunks
    chunk_val = validate_chunks(all_chunks, documents)
    if not chunk_val.is_valid:
        print("ERROR: Chunk validation failed:", file=sys.stderr)
        for err in chunk_val.errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    # Step 5: Write output JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_directory": str(kb_dir),
        "chunk_size_tokens": chunk_size,
        "chunk_overlap_tokens": chunk_overlap,
        "document_count": len(documents),
        "chunk_count": len(all_chunks),
        "chunks": [chunk.to_dict() for chunk in all_chunks]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)

    # Step 6: Print report
    stats = doc_val.stats
    print("========================================")
    print("P5 Knowledge Base Ingestion")
    print("===========================")
    print()
    print(f"Documents discovered: {stats['total_documents']}")
    print(f"Fault documents:     {stats['fault_documents']}")
    print(f"Sensor documents:    {stats['sensor_documents']}")
    print(f"Procedure documents: {stats['procedure_documents']}")
    print()
    print(f"Chunks generated:    {len(all_chunks)}")
    print()
    print("Validation:          PASSED")
    print()
    print("Output:")
    print(f"{output_path}")
    print("========================================")

    return True


def main():
    script_dir = Path(__file__).parent.resolve()
    default_kb = script_dir.parent / "knowledge-base"
    default_output = script_dir / "output" / "chunks.json"

    parser = argparse.ArgumentParser(
        description="Ingest, normalize, and chunk P_311 knowledge base Markdown documents."
    )
    parser.add_argument(
        "--kb-dir",
        type=Path,
        default=default_kb,
        help="Path to knowledge-base directory (default: ../knowledge-base)"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=default_output,
        help="Path to destination JSON file (default: output/chunks.json)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=800,
        help="Target maximum chunk size in token equivalents (default: 800)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Target chunk overlap in token equivalents (default: 100)"
    )
    parser.add_argument(
        "--include-readme",
        action="store_true",
        help="Include knowledge base root README.md in ingestion (default: False)"
    )

    args = parser.parse_args()

    success = run_ingestion(
        kb_dir=args.kb_dir,
        output_path=args.output_file,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        include_readme=args.include_readme
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
