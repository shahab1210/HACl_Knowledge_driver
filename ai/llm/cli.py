#!/usr/bin/env python3

"""
CLI entry point for P10 Local LLM Generation Layer.

Commands:

- status: Check Ollama server connectivity and list installed generative/embedding models

- prompt: Construct and display the formatted prompt for a given query and context

- generate: Perform local LLM inference on a query + context (or end-to-end with P9 RAG)
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DEFAULT_OLLAMA_BASE_URL, DEFAULT_LLM_MODEL
from client import LocalLLMClient
from prompt_builder import PromptBuilder, build_prompt
from llm_pipeline import LLMPipeline
from models import GenerationOptions, LLMError, OllamaModelNotFoundError, OllamaModelTypeError


def cmd_status(args):
    """Check Ollama service status and inspect installed models."""
    print("========================================")
    print("P10 Local LLM: Service & Model Status")
    print("========================================")
    print(f"Ollama Endpoint: {args.base_url}")
    print(f"Target LLM Model: {args.model}")
    print("----------------------------------------")

    client = LocalLLMClient(base_url=args.base_url, model=args.model)

    if not client.is_server_running():
        print("❌ Server Status: NOT REACHABLE")
        print("   Ensure Ollama is running ('ollama serve' or open Ollama app).")
        return 1

    print("✅ Server Status: RUNNING & REACHABLE")

    try:
        models = client.list_models_detailed()
    except Exception as e:
        print(f"❌ Failed to query models: {e}")
        return 1

    if not models:
        print("⚠️ No models currently installed in Ollama.")
    else:
        print(f"\nInstalled Models ({len(models)}):")
        for m in models:
            name = m.get("name", "unknown")
            size_mb = m.get("size", 0) / (1024 * 1024)
            is_embed = client.is_embedding_model(name)
            model_type = (
                "Embedding Model (P7/P8)"
                if is_embed
                else "Generative LLM (P10 Compatible)"
            )
            tag = "📦" if is_embed else "🤖"
            print(
                f"  {tag} {name:<25} "
                f"[{size_mb:>7.1f} MB] -> {model_type}"
            )

    print("----------------------------------------")
    print("Model Readiness Check for P10:")

    try:
        client.validate_model_readiness(args.model)
        print(
            f"✅ Model '{args.model}' is READY for local generation."
        )

    except OllamaModelTypeError as e:
        print(f"❌ Model Type Error: {e}")

    except OllamaModelNotFoundError as e:
        print(f"⚠️ Model Not Found: {e}")
        print(f"   To install, run: ollama pull {args.model}")

    except LLMError as e:
        print(f"❌ Error: {e}")

    print("========================================")
    return 0


def cmd_prompt(args):
    """Construct and preview prompt."""
    builder = PromptBuilder()

    context = args.context

    if args.context_file and os.path.isfile(args.context_file):
        with open(args.context_file, "r", encoding="utf-8") as f:
            context = f.read()

    try:
        prompt_text = builder.build_prompt(
            query=args.query,
            context=context
        )

    except Exception as e:
        print(
            f"ERROR building prompt: {e}",
            file=sys.stderr
        )
        return 1

    print("========================================")
    print("P10 Prompt Builder: Constructed Prompt")
    print("========================================")
    print(prompt_text)
    print("========================================")

    return 0


def cmd_generate(args):
    """Perform local LLM generation."""

    client = LocalLLMClient(
        base_url=args.base_url,
        model=args.model,
        timeout=args.timeout
    )

    pipeline = LLMPipeline(client=client)

    context = args.context
    rag_count = 0

    # Optional P9 RAG retrieval integration
    if args.use_rag:
        try:
            # ---------------------------------------------------------
            # IMPORTANT:
            # P10 and P8/P9 contain modules with generic names such as
            # config.py, models.py and client.py.
            #
            # P10's modules are already loaded when this CLI starts.
            # P9 -> P8 therefore needs its own module resolution.
            # ---------------------------------------------------------

            p10_module_names = {
                "config",
                "models",
                "client",
                "prompt_builder",
            }

            # Save currently loaded P10 modules
            saved_modules = {
                name: sys.modules.get(name)
                for name in p10_module_names
                if name in sys.modules
            }

            # Remove P10 modules temporarily from Python's module cache
            for name in p10_module_names:
                sys.modules.pop(name, None)

            # Remove P10 src directory temporarily
            p10_src_path = str(SRC_DIR)

            if p10_src_path in sys.path:
                sys.path.remove(p10_src_path)

            # Add P9 and P8 paths
            P9_SRC = (
                Path(__file__).resolve().parents[1]
                / "rag"
                / "src"
            )

            P8_DIR = (
                Path(__file__).resolve().parents[1]
                / "vector-db"
            )

            if str(P9_SRC) not in sys.path:
                sys.path.insert(0, str(P9_SRC))

            if str(P8_DIR) not in sys.path:
                sys.path.insert(0, str(P8_DIR))

            # Import P9 only after P10 generic modules are removed
            from rag_pipeline import RAGPipeline

            rag = RAGPipeline(
                top_k=args.top_k,
                base_url=args.base_url
            )

            rag_res = rag.run(args.query)

            context = rag_res["context"]
            rag_count = rag_res["result_count"]

            print(
                f"[RAG] Retrieved "
                f"{rag_count} knowledge sources from ChromaDB."
            )

            # ---------------------------------------------------------
            # Restore P10 module environment
            # ---------------------------------------------------------

            for name in p10_module_names:
                sys.modules.pop(name, None)

            for name, module in saved_modules.items():
                if module is not None:
                    sys.modules[name] = module

            if p10_src_path not in sys.path:
                sys.path.insert(0, p10_src_path)

        except Exception as e:
            print(
                f"ERROR during RAG retrieval: {e}",
                file=sys.stderr
            )
            return 1

    elif args.context_file and os.path.isfile(args.context_file):
        with open(args.context_file, "r", encoding="utf-8") as f:
            context = f.read()

    opts = GenerationOptions(
        temperature=args.temperature,
        num_predict=args.max_tokens,
        top_p=args.top_p
    )

    print("========================================")
    print("P10 Local LLM: Fault Explanation Generation")
    print("========================================")
    print(f"Model:       {args.model}")
    print(f"Endpoint:    {args.base_url}")
    print(f"Query:       '{args.query}'")
    print("----------------------------------------")
    print("Generating response from Local LLM...")

    try:
        output = pipeline.generate(
            query=args.query,
            context=context,
            options=opts
        )

    except OllamaModelNotFoundError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        print(
            f"Please run: ollama pull {args.model}",
            file=sys.stderr
        )
        return 1

    except OllamaModelTypeError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(
            f"\n❌ Generation failed: {e}",
            file=sys.stderr
        )
        return 1

    print("\n----------------------------------------")
    print("Generated Fault Explanation:")
    print("----------------------------------------")
    print(output.response)

    print("\n----------------------------------------")

    details = output.generation_details

    eval_count = details.get("eval_count", 0)

    total_dur_s = (
        details.get("total_duration") or 0
    ) / 1e9

    print(f"Tokens Generated: {eval_count}")
    print(f"Total Duration:   {total_dur_s:.2f}s")
    print("========================================")

    return 0


def main():

    common_parser = argparse.ArgumentParser(
        add_help=False
    )

    common_parser.add_argument(
        "--base-url",
        type=str,
        default=DEFAULT_OLLAMA_BASE_URL,
        help=(
            "Ollama base URL "
            f"(default: {DEFAULT_OLLAMA_BASE_URL})"
        )
    )

    common_parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_LLM_MODEL,
        help=(
            "Generative LLM model name "
            f"(default: {DEFAULT_LLM_MODEL})"
        )
    )

    parser = argparse.ArgumentParser(
        description=(
            "P10 Local LLM Generation CLI "
            "for IoT Fault Diagnosis Assistant"
        ),
        parents=[common_parser]
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )

    # Command: status
    subparsers.add_parser(
        "status",
        parents=[common_parser],
        help=(
            "Check Ollama service status "
            "and available models"
        )
    )

    # Command: prompt
    prompt_p = subparsers.add_parser(
        "prompt",
        parents=[common_parser],
        help=(
            "Construct and preview prompt "
            "for a query and context"
        )
    )

    prompt_p.add_argument(
        "--query",
        type=str,
        required=True,
        help="User/telemetry query"
    )

    prompt_p.add_argument(
        "--context",
        type=str,
        default="",
        help="Context text string"
    )

    prompt_p.add_argument(
        "--context-file",
        type=str,
        help="Path to file containing context text"
    )

    # Command: generate
    gen_p = subparsers.add_parser(
        "generate",
        parents=[common_parser],
        help=(
            "Generate fault explanation "
            "using local LLM"
        )
    )

    gen_p.add_argument(
        "--query",
        type=str,
        required=True,
        help="User/telemetry query"
    )

    gen_p.add_argument(
        "--context",
        type=str,
        default="",
        help="Context text string"
    )

    gen_p.add_argument(
        "--context-file",
        type=str,
        help="Path to file containing context text"
    )

    gen_p.add_argument(
        "--use-rag",
        action="store_true",
        help="Retrieve context automatically via P9 RAG"
    )

    gen_p.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Top-K RAG retrieval count (default: 5)"
    )

    gen_p.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2)"
    )

    gen_p.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Maximum generated tokens (default: 1024)"
    )

    gen_p.add_argument(
        "--top-p",
        type=float,
        default=0.9,
        help="Top-p nucleus sampling (default: 0.9)"
    )

    gen_p.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Generation timeout in seconds (default: 120)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        sys.exit(cmd_status(args))

    elif args.command == "prompt":
        sys.exit(cmd_prompt(args))

    elif args.command == "generate":
        sys.exit(cmd_generate(args))


if __name__ == "__main__":
    main()