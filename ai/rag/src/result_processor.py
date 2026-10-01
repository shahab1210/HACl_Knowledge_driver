"""
P9 RAG Pipeline - Result Processor

Processes semantic search results returned by P8.

The processor validates results and organizes them
for the later RAG context-building stage.
"""

from typing import Any, Dict, List

from models import SearchResult


def validate_results(results: List[SearchResult]) -> None:
    """
    Validate the basic structure of retrieved search results.
    """

    if not isinstance(results, list):
        raise TypeError("Results must be provided as a list.")

    for result in results:
        if not isinstance(result, SearchResult):
            raise TypeError(
                "Every result must be a SearchResult object."
            )

        if not result.chunk_id:
            raise ValueError("Search result is missing chunk_id.")

        if not result.document_id:
            raise ValueError("Search result is missing document_id.")

        if not result.text.strip():
            raise ValueError(
                f"Search result {result.chunk_id} has empty text."
            )

        if not 0.0 <= result.similarity <= 1.0:
            raise ValueError(
                f"Invalid similarity for {result.chunk_id}: "
                f"{result.similarity}"
            )


def process_results(
    results: List[SearchResult]
) -> List[Dict[str, Any]]:
    """
    Convert P8 SearchResult objects into structured P9 retrieval results.

    Results remain chunk-level, but document identity is preserved so
    later stages can reason about multiple chunks from the same document.
    """

    validate_results(results)

    processed = []

    for result in results:
        processed.append(
            {
                "rank": result.rank,
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "document_type": result.document_type,
                "title": result.title,
                "source": result.source,
                "distance": result.distance,
                "similarity": result.similarity,
                "text": result.text,
                "metadata": result.metadata,
            }
        )

    return processed


def group_by_document(
    results: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group processed chunks by document_id.

    Example:

        FAULT-003
            ├── chunk_001
            └── chunk_002
    """

    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for result in results:
        document_id = result["document_id"]

        if document_id not in grouped:
            grouped[document_id] = []

        grouped[document_id].append(result)

    return grouped