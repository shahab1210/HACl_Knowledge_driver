#!/usr/bin/env python3
"""
CLI entry point for P12 Diagnosis Engine Layer.

Commands:
- diagnose: Execute end-to-end RAG + LLM diagnosis and produce structured machine-readable output
"""

import sys
import argparse
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from engine import DiagnosisEngine
from exceptions import DiagnosisEngineError


def cmd_diagnose(args):
    """Execute end-to-end diagnosis and format output."""
    try:
        engine = DiagnosisEngine(
            top_k=args.top_k,
            model=args.model,
            embedding_model=args.embedding_model,
            base_url=args.base_url,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout
        )
    except Exception as e:
        print(f"ERROR initializing Diagnosis Engine: {e}", file=sys.stderr)
        return 1

    if not args.json:
        print("========================================")
        print("P12 Diagnosis Engine")
        print("========================================")
        print(f"Query:            '{args.query}'")
        print(f"Generative Model: {args.model}")
        print(f"Embedding Model:  {args.embedding_model}")
        print(f"Top-K Retrieval:  {args.top_k}")
        print("----------------------------------------")
        print("Analyzing telemetry and synthesizing structured diagnosis...")

    try:
        result = engine.diagnose(
            query=args.query,
            top_k=args.top_k,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
    except DiagnosisEngineError as e:
        print(f"\n❌ Diagnosis failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(result.to_json(indent=2))
        return 0

    print("\n----------------------------------------")
    print("Structured Diagnosis Results:")
    print("----------------------------------------")

    # Primary Fault
    if result.primary_fault:
        sim_str = f" (Similarity: {result.primary_fault.similarity:.4f})" if result.primary_fault.similarity else ""
        print(f"Primary Fault:       [{result.primary_fault.fault_id}] {result.primary_fault.title}{sim_str}")
    else:
        print("Primary Fault:       None / Insufficient Evidence")

    # Alternative Faults
    if result.alternative_faults:
        print("Alternative Faults:")
        for alt in result.alternative_faults:
            sim_str = f" (Similarity: {alt.similarity:.4f})" if alt.similarity else ""
            print(f"  • [{alt.fault_id}] {alt.title}{sim_str}")
    else:
        print("Alternative Faults:  None")

    # Confidence
    print(f"Confidence Level:    {result.confidence.level.upper()}")
    print(f"Confidence Reason:   {result.confidence.reason}")

    # Telemetry Evidence
    if result.evidence:
        print("\nTelemetry Evidence:")
        for ev in result.evidence:
            val_str = f"{ev.value} {ev.unit or ''}".strip() if ev.value is not None else "observed"
            status_str = f" [Status: {ev.status}]" if ev.status else ""
            print(f"  • {ev.parameter}: {val_str}{status_str}")

    # Possible Causes
    if result.possible_causes:
        print(f"\nPossible Causes ({len(result.possible_causes)}):")
        for idx, cause in enumerate(result.possible_causes, 1):
            print(f"  {idx}. {cause}")

    # Recommended Checks
    if result.recommended_checks:
        print(f"\nRecommended Checks ({len(result.recommended_checks)}):")
        for idx, check in enumerate(result.recommended_checks, 1):
            print(f"  {idx}. {check}")

    # Additional Info Required
    if result.additional_information_required:
        print(f"\nAdditional Information Required ({len(result.additional_information_required)}):")
        for idx, info in enumerate(result.additional_information_required, 1):
            print(f"  • {info}")

    # Knowledge Sources
    print(f"\nKnowledge Sources Grounding ({len(result.knowledge_sources)}):")
    for ks in result.knowledge_sources:
        print(f"  [{ks.rank}] {ks.document_id}: {ks.title} (Chunk: {ks.chunk_id}, Similarity: {ks.similarity:.4f})")

    # Generation Details
    print("\nGeneration Details:")
    print(f"  Model:            {result.model}")
    details = result.generation_details or {}
    eval_count = details.get("eval_count", 0)
    dur_s = (details.get("total_duration") or 0) / 1e9
    if eval_count:
        print(f"  Tokens Generated: {eval_count}")
    if dur_s:
        print(f"  Duration:         {dur_s:.2f}s")
    print("========================================")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="P12 Diagnosis Engine CLI for IoT Fault Diagnosis Assistant"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen2.5:1.5b",
        help="Generative LLM model (default: qwen2.5:1.5b)"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="nomic-embed-text",
        help="Embedding model (default: nomic-embed-text)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    diag_p = subparsers.add_parser("diagnose", help="Execute structured diagnosis")
    diag_p.add_argument("--query", type=str, required=True, help="User or telemetry query")
    diag_p.add_argument("--top-k", type=int, default=3, help="Top-K knowledge chunks (default: 3)")
    diag_p.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature (default: 0.2)")
    diag_p.add_argument("--max-tokens", type=int, default=1024, help="Max tokens (default: 1024)")
    diag_p.add_argument("--timeout", type=float, default=120.0, help="Inference timeout (default: 120s)")
    diag_p.add_argument("--base-url", type=str, default="http://localhost:11434", help="Ollama base URL")
    diag_p.add_argument("--model", type=str, default="qwen2.5:1.5b", help="Generative model")
    diag_p.add_argument("--embedding-model", type=str, default="nomic-embed-text", help="Embedding model")
    diag_p.add_argument("--json", action="store_true", help="Output pure JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "diagnose":
        sys.exit(cmd_diagnose(args))


if __name__ == "__main__":
    main()
