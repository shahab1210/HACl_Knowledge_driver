#!/usr/bin/env python3
"""
CLI entry point for P11 RAG + LLM Integration Layer.

Commands:
- diagnose: Perform end-to-end RAG retrieval + local LLM diagnosis on a telemetry query
"""

import sys
import argparse
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import (
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_TOP_K,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
)
from pipeline import RAGLLMPipeline
from exceptions import IntegrationError


def cmd_diagnose(args):
    """Execute end-to-end RAG + LLM diagnosis."""
    try:
        pipeline = RAGLLMPipeline(
            top_k=args.top_k,
            model=args.model,
            embedding_model=args.embedding_model,
            base_url=args.base_url,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout
        )
    except Exception as e:
        print(f"ERROR initializing pipeline: {e}", file=sys.stderr)
        return 1

    if not args.json:
        print("========================================")
        print("P11 RAG + LLM Integration: Fault Diagnosis")
        print("========================================")
        print(f"Query:           '{args.query}'")
        print(f"Generative Model: {args.model}")
        print(f"Embedding Model:  {args.embedding_model}")
        print(f"Ollama Endpoint:  {args.base_url}")
        print(f"Top-K Retrieval:  {args.top_k}")
        print("----------------------------------------")
        print("Executing retrieval & local generation...")

    try:
        result = pipeline.run(
            query=args.query,
            top_k=args.top_k,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
    except IntegrationError as e:
        print(f"\n❌ Pipeline failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(result.to_json(indent=2))
        return 0

    print("\n----------------------------------------")
    print(f"Retrieved Knowledge Sources ({result.retrieval.result_count}):")
    print("----------------------------------------")
    for s in result.retrieval.sources:
        print(f"  [{s.rank}] {s.document_id}: {s.title}")
        print(f"      Chunk:      {s.chunk_id}")
        print(f"      Similarity: {s.similarity:.4f} (Distance: {s.distance:.4f})")
        print(f"      Source:     {s.source}")
        excerpt = s.text.replace("\n", " ").strip()
        if len(excerpt) > 140:
            excerpt = excerpt[:140] + "..."
        print(f"      Excerpt:    {excerpt}")

    print("\n----------------------------------------")
    print("Generated Fault Diagnosis:")
    print("----------------------------------------")
    print(result.diagnosis)

    print("\n----------------------------------------")
    print("Generation Telemetry & Statistics:")
    print("----------------------------------------")
    details = result.generation_details
    eval_count = details.get("eval_count", 0)
    total_dur_ns = details.get("total_duration") or 0
    total_dur_s = total_dur_ns / 1e9
    print(f"  Model:            {result.model}")
    print(f"  Tokens Generated: {eval_count}")
    print(f"  Total Duration:   {total_dur_s:.2f}s")
    print("========================================")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="P11 RAG + LLM Integration CLI for IoT Fault Diagnosis Assistant"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=DEFAULT_OLLAMA_BASE_URL,
        help=f"Ollama base URL (default: {DEFAULT_OLLAMA_BASE_URL})"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_LLM_MODEL,
        help=f"Generative LLM model (default: {DEFAULT_LLM_MODEL})"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help=f"Embedding model (default: {DEFAULT_EMBEDDING_MODEL})"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: diagnose
    diag_p = subparsers.add_parser("diagnose", help="Run end-to-end RAG retrieval + LLM diagnosis")
    diag_p.add_argument("--query", type=str, required=True, help="User or telemetry query")
    diag_p.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help=f"Top-K knowledge chunks (default: {DEFAULT_TOP_K})")
    diag_p.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE, help=f"Sampling temperature (default: {DEFAULT_TEMPERATURE})")
    diag_p.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help=f"Max tokens to generate (default: {DEFAULT_MAX_TOKENS})")
    diag_p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"Inference timeout (default: {DEFAULT_TIMEOUT}s)")
    diag_p.add_argument("--base-url", type=str, default=DEFAULT_OLLAMA_BASE_URL, help=f"Ollama base URL (default: {DEFAULT_OLLAMA_BASE_URL})")
    diag_p.add_argument("--model", type=str, default=DEFAULT_LLM_MODEL, help=f"Generative LLM model (default: {DEFAULT_LLM_MODEL})")
    diag_p.add_argument("--embedding-model", type=str, default=DEFAULT_EMBEDDING_MODEL, help=f"Embedding model (default: {DEFAULT_EMBEDDING_MODEL})")
    diag_p.add_argument("--json", action="store_true", help="Output pure JSON")

    args = parser.parse_args()

    if not args.command:
        # Default to diagnose if query is passed
        parser.print_help()
        sys.exit(1)

    if args.command == "diagnose":
        sys.exit(cmd_diagnose(args))


if __name__ == "__main__":
    main()
