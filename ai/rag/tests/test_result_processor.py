import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest

from retriever import RAGRetriever
from result_processor import process_results, group_by_document
from models import SearchResult


def get_sample_results():
    retriever = RAGRetriever(top_k=5)

    return retriever.retrieve(
        "The motor temperature is very high and the vibration is excessive."
    )


def test_process_results_returns_list():
    results = get_sample_results()

    processed = process_results(results)

    assert isinstance(processed, list)
    assert len(processed) == 5


def test_processed_result_contains_required_fields():
    results = get_sample_results()

    processed = process_results(results)

    required_fields = {
        "rank",
        "chunk_id",
        "document_id",
        "document_type",
        "title",
        "source",
        "distance",
        "similarity",
        "text",
        "metadata"
    }

    for result in processed:
        assert required_fields.issubset(result.keys())


def test_process_results_rejects_invalid_input():
    with pytest.raises(TypeError):
        process_results("invalid results")


def test_process_results_rejects_invalid_result_object():
    with pytest.raises(TypeError):
        process_results([{"invalid": "result"}])


def test_group_by_document():
    results = get_sample_results()

    processed = process_results(results)
    grouped = group_by_document(processed)

    assert isinstance(grouped, dict)
    assert len(grouped) == 3

    total_chunks = sum(
        len(chunks)
        for chunks in grouped.values()
    )

    assert total_chunks == 5


def test_group_by_document_preserves_document_identity():
    results = get_sample_results()

    processed = process_results(results)
    grouped = group_by_document(processed)

    for document_id, chunks in grouped.items():
        for chunk in chunks:
            assert chunk["document_id"] == document_id