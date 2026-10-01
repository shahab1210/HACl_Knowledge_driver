"""
P9 RAG Pipeline - Context Builder

Builds a clean textual context from processed retrieval results.

This context will later be provided to the Local LLM.
P9 only prepares the context; it does not generate a diagnosis.
"""

from typing import Any, Dict, List


def build_context(
    results: List[Dict[str, Any]]
) -> str:
    """
    Convert processed retrieval results into a structured RAG context.
    """

    if not isinstance(results, list):
        raise TypeError("Results must be provided as a list.")

    if not results:
        return "No relevant knowledge was retrieved."

    context_parts = []

    for index, result in enumerate(results, start=1):

        title = result.get("title", "Unknown")
        document_id = result.get("document_id", "Unknown")
        source = result.get("source", "Unknown")
        similarity = result.get("similarity", 0.0)
        text = result.get("text", "").strip()

        if not text:
            continue

        context_parts.append(
            f"""Knowledge Source {index}
Title: {title}
Document ID: {document_id}
Source: {source}
Similarity: {similarity:.4f}

{text}
"""
        )

    if not context_parts:
        return "No valid knowledge content was retrieved."

    return "\n---\n\n".join(context_parts)
