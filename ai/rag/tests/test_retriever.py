import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest

from retriever import RAGRetriever


def test_retrieve_returns_results():
    retriever = RAGRetriever(top_k=3)

    results = retriever.retrieve(
        "The motor temperature is very high and the vibration is excessive."
    )

    assert isinstance(results, list)
    assert len(results) == 3


def test_retrieve_results_are_search_results():
    retriever = RAGRetriever(top_k=3)

    results = retriever.retrieve(
        "The motor temperature is very high and the vibration is excessive."
    )

    for result in results:
        assert result.chunk_id
        assert result.document_id
        assert result.title
        assert result.text
        assert 0.0 <= result.similarity <= 1.0


def test_top_k_can_be_overridden():
    retriever = RAGRetriever(top_k=5)

    results = retriever.retrieve(
        "Motor overheating and excessive vibration",
        top_k=2
    )

    assert len(results) == 2


def test_empty_query_raises_error():
    retriever = RAGRetriever(top_k=3)

    with pytest.raises(ValueError):
        retriever.retrieve("")


def test_whitespace_query_raises_error():
    retriever = RAGRetriever(top_k=3)

    with pytest.raises(ValueError):
        retriever.retrieve("   ")


def test_invalid_top_k_raises_error():
    retriever = RAGRetriever(top_k=3)

    with pytest.raises(ValueError):
        retriever.retrieve(
            "Motor overheating",
            top_k=0
        )
