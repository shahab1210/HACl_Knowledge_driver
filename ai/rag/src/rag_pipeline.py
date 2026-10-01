"""
P9 RAG Pipeline - Orchestrator

Connects the complete P9 retrieval pipeline:

Query
  ↓
Retriever
  ↓
Result Processor
  ↓
Context Builder
  ↓
Structured RAG Output

This stage does not generate an AI diagnosis.
Local LLM generation belongs to P10/P11.
"""

from typing import Any, Dict, Optional

from retriever import RAGRetriever
from result_processor import process_results
from context_builder import build_context


class RAGPipeline:
    """
    Main entry point for the P9 RAG retrieval pipeline.
    """

    def __init__(
        self,
        top_k: int = 5,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.retriever = RAGRetriever(
            top_k=top_k,
            model=model,
            base_url=base_url
        )

    def run(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete P9 retrieval pipeline.
        """

        if not query or not query.strip():
            raise ValueError(
                "RAG pipeline query cannot be empty or whitespace only."
            )

        clean_query = query.strip()

        # Step 1: Retrieve relevant knowledge
        retrieved_results = self.retriever.retrieve(
            query=clean_query,
            top_k=top_k
        )

        # Step 2: Validate and structure retrieval results
        processed_results = process_results(
            retrieved_results
        )

        # Step 3: Build context for future LLM usage
        context = build_context(
            processed_results
        )
        return {
            "query": clean_query,
            "result_count": len(processed_results),
            "results": processed_results,
            "context": context
        }