#!/usr/bin/env python3
"""
CLI entry point for P8 Vector Database.
Provides command-line interfaces for:
- load: Load and idempotently upsert P7 embeddings into ChromaDB
- search: Execute semantic similarity search using local Ollama query embedding
- stats: Display current collection statistics and persistence state
"""

import sys
import argparse
from pathlib import Path

from config import CHROMA_PATH, COLLECTION_NAME, EMBEDDINGS_FILE, DEFAULT_TOP_K
from database import ChromaManager
from loader import load_embeddings_into_chroma
from search import SemanticSearchEngine


def cmd_load(args):
    """Execute loading of embeddings into ChromaDB."""
    print("========================================")
    print("P8 Vector Database: Loading Embeddings")
    print("========================================")
    print(f"Source file:     {args.file}")
    print(f"Collection name: {args.collection}")
    print(f"Storage path:    {args.chroma_path}")
    print()

    manager = ChromaManager(
        chroma_path=args.chroma_path,
        collection_name=args.collection
    )

    try:
        report = load_embeddings_into_chroma(
            embeddings_file=args.file,
            chroma_manager=manager
        )
    except Exception as e:
        print(f"ERROR: Loading failed: {e}", file=sys.stderr)
        return 1

    print("========================================")
    print("Loading Status:       SUCCESS")
    print(f"Collection:           {report['collection_name']}")
    print(f"Records loaded:       {report['records_loaded']}")
    print(f"Total in collection:  {report['total_collection_count']}")
    print(f"Vector dimension:     {report['embedding_dimension']}")
    print(f"Distance metric:      {report['distance_metric']}")
    print(f"ChromaDB location:    {report['chroma_path']}")
    print("========================================")
    return 0


def cmd_search(args):
    """Execute semantic similarity query."""
    manager = ChromaManager(
        chroma_path=args.chroma_path,
        collection_name=args.collection
    )

    if manager.count() == 0:
        print("ERROR: ChromaDB collection is empty. Run 'python3 cli.py load' first.", file=sys.stderr)
        return 1

    engine = SemanticSearchEngine(
        chroma_manager=manager,
        base_url=args.base_url,
        model=args.model
    )

    print("========================================")
    print("P8 Vector Database: Semantic Search")
    print("========================================")
    print(f"Query:        '{args.query}'")
    print(f"Model:        {engine.model}")
    print(f"Metric:       {manager.metric} (lower distance = higher similarity)")
    print(f"Top-K:        {args.top_k}")
    print("----------------------------------------")

    try:
        results = engine.search(query=args.query, top_k=args.top_k)
    except Exception as e:
        print(f"ERROR: Search failed: {e}", file=sys.stderr)
        return 1

    if not results:
        print("No matching records found.")
        return 0

    for res in results:
        print(f"\n[Rank {res.rank}] {res.chunk_id}")
        print(f"  Title:      {res.title} ({res.document_type})")
        print(f"  Source:     {res.source}")
        print(f"  Distance:   {res.distance:.6f} (Cosine Distance)")
        print(f"  Similarity: {res.similarity:.4f} (Derived Cosine Sim)")
        if res.metadata.get("sensors"):
            print(f"  Sensors:    {res.metadata.get('sensors')}")
        if res.metadata.get("severity"):
            print(f"  Severity:   {res.metadata.get('severity')}")

        # Text preview (first 180 chars, normalized)
        preview = res.text.replace("\n", " ").strip()
        if len(preview) > 180:
            preview = preview[:180] + "..."
        print(f"  Excerpt:    {preview}")

    print("\n========================================")
    return 0


def cmd_stats(args):
    """Display statistics for the ChromaDB collection."""
    manager = ChromaManager(
        chroma_path=args.chroma_path,
        collection_name=args.collection
    )
    stats = manager.get_stats()

    print("========================================")
    print("P8 Vector Database Statistics")
    print("========================================")
    print(f"Collection Name: {stats.collection_name}")
    print(f"Record Count:    {stats.record_count}")
    print(f"Distance Metric: {stats.distance_metric}")
    print(f"Storage Path:    {stats.chroma_path}")
    print("========================================")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="P8 Vector Database CLI: Manage persistent ChromaDB collections and run semantic queries."
    )
    parser.add_argument(
        "--chroma-path",
        type=str,
        default=CHROMA_PATH,
        help=f"Path to ChromaDB storage directory (default: {CHROMA_PATH})"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=COLLECTION_NAME,
        help=f"Collection name (default: {COLLECTION_NAME})"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: load
    load_parser = subparsers.add_parser("load", help="Load P7 embeddings into ChromaDB")
    load_parser.add_argument(
        "--file",
        type=str,
        default=EMBEDDINGS_FILE,
        help=f"Path to embeddings.json (default: {EMBEDDINGS_FILE})"
    )

    # Command: search
    search_parser = subparsers.add_parser("search", help="Perform semantic similarity search")
    search_parser.add_argument("query", type=str, help="Search query string")
    search_parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Number of top results to return (default: {DEFAULT_TOP_K})"
    )
    search_parser.add_argument(
        "--model",
        type=str,
        default="nomic-embed-text",
        help="Ollama model name for query embedding"
    )
    search_parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama service base URL"
    )

    # Command: stats
    subparsers.add_parser("stats", help="Display collection statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "load":
        sys.exit(cmd_load(args))
    elif args.command == "search":
        sys.exit(cmd_search(args))
    elif args.command == "stats":
        sys.exit(cmd_stats(args))


if __name__ == "__main__":
    main()
