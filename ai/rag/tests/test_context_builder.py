import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest

from retriever import RAGRetriever
from result_processor import process_results
from context_builder import build_context


def get_processed_results():
    retriever = RAGRetriever(top_k=5)

    results = retriever.retrieve(
        "The motor temperature is very high and the vibration is excessive."
    )

    return process_results(results)


def test_build_context_returns_string():
    processed = get_processed_results()

    context = build_context(processed)

    assert isinstance(context, str)
    assert len(context) > 0


def test_context_contains_retrieved_titles():
    processed = get_processed_results()

    context = build_context(processed)

    assert "Excessive Motor Vibration" in context
    assert "Motor Overheating" in context
    assert "Bearing Overheating" in context


def test_context_contains_document_information():
    processed = get_processed_results()

    context = build_context(processed)

    assert "FAULT-005" in context
    assert "FAULT-003" in context
    assert "FAULT-001" in context


def test_context_contains_similarity_scores():
    processed = get_processed_results()

    context = build_context(processed)

    assert "Similarity:" in context


def test_empty_results_return_message():
    context = build_context([])

    assert context == "No relevant knowledge was retrieved."


def test_invalid_results_type_raises_error():
    with pytest.raises(TypeError):
        build_context("invalid results")


def test_context_contains_knowledge_source_labels():
    processed = get_processed_results()

    context = build_context(processed)

    assert "Knowledge Source 1" in context
    assert "Knowledge Source 2" in context