"""
P9 RAG Pipeline - Retriever

Connects the P9 RAG pipeline with the existing P8
SemanticSearchEngine.

P9 does not implement vector search itself.
It reuses P8's proven semantic retrieval functionality.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

P8_DIR = Path(__file__).resolve().parents[2] / "vector-db"

if str(P8_DIR) not in sys.path:
    sys.path.insert(0, str(P8_DIR))

from search import SemanticSearchEngine
from models import SearchResult


class RAGRetriever:
    """
    P9 retrieval layer.

    Uses the existing P8 SemanticSearchEngine to retrieve
    relevant knowledge chunks from ChromaDB.
    """

    def __init__(
        self,
        top_k: int = 5,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.top_k = top_k

        self.search_engine = SemanticSearchEngine(
            model=model,
            base_url=base_url
        )

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Retrieve relevant knowledge chunks for a query.
        """

        if not query or not query.strip():
            raise ValueError(
                "RAG retrieval query cannot be empty or whitespace only."
            )

        k = top_k if top_k is not None else self.top_k

        if k <= 0:
            raise ValueError("top_k must be greater than zero.")

        return self.search_engine.search(
            query=query.strip(),
            top_k=k,
            where=where
        )