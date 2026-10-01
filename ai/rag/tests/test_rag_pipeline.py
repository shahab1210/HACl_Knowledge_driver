import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest

from rag_pipeline import RAGPipeline


def test_rag_pipeline_returns_complete_output():
    pipeline = RAGPipeline(top_k=5)

    output = pipeline.run(
        "The motor temperature is very high and the vibration is excessive."
    )

    assert isinstance(output, dict)

    assert output["query"]
    assert output["result_count"] == 5
    assert len(output["results"]) == 5
    assert output["context"]


def test_rag_pipeline_contains_required_output_fields():
    pipeline = RAGPipeline(top_k=3)

    output = pipeline.run(
        "Motor overheating and excessive vibration"
    )

    assert "query" in output
    assert "result_count" in output
    assert "results" in output
    assert "context" in output


def test_rag_pipeline_respects_top_k():
    pipeline = RAGPipeline(top_k=5)

    output = pipeline.run(
        "Motor overheating",
        top_k=2
    )

    assert output["result_count"] == 2
    assert len(output["results"]) == 2


def test_rag_pipeline_context_contains_knowledge():
    pipeline = RAGPipeline(top_k=5)

    output = pipeline.run(
        "The motor temperature is very high and the vibration is excessive."
    )

    context = output["context"]

    assert "Knowledge Source" in context
    assert "FAULT-" in context
    assert "Similarity:" in context


def test_empty_query_raises_error():
    pipeline = RAGPipeline(top_k=5)

    with pytest.raises(ValueError):
        pipeline.run("")


def test_whitespace_query_raises_error():
    pipeline = RAGPipeline(top_k=5)

    with pytest.raises(ValueError):
        pipeline.run("   ")