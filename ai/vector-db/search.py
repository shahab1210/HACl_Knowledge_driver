"""
Semantic Search module for P8 Vector Database.
Implements the Query Flow:
Query Text -> Local Ollama (nomic-embed-text) -> Query Vector -> ChromaDB -> Top-K SearchResults.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import OLLAMA_BASE_URL, EMBEDDING_MODEL, DEFAULT_TOP_K
from models import SearchResult
from database import ChromaManager

# Import OllamaClient from P7 embeddings module
P7_DIR = Path(__file__).resolve().parent.parent / "embeddings"
if str(P7_DIR) not in sys.path:
    sys.path.insert(0, str(P7_DIR))

try:
    from client import OllamaClient
except ImportError:
    # Graceful fallback if path structure shifts
    OllamaClient = None


class SemanticSearchEngine:
    """
    Orchestrates semantic similarity queries against the local ChromaDB vector database.
    Embeds input queries using the exact same local Ollama model (nomic-embed-text) used in P7.
    """

    def __init__(
        self,
        chroma_manager: Optional[ChromaManager] = None,
        ollama_client: Optional[Any] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.chroma_manager = chroma_manager or ChromaManager()
        self.model = model or EMBEDDING_MODEL
        self.base_url = base_url or OLLAMA_BASE_URL

        if ollama_client is not None:
            self.client = ollama_client
        elif OllamaClient is not None:
            self.client = OllamaClient(base_url=self.base_url, model=self.model)
        else:
            raise RuntimeError("Could not import OllamaClient from ai/embeddings/client.py")

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Executes semantic similarity search for a natural language or telemetry query:
        1. Validates query text
        2. Embeds query text into 768-dim vector via local Ollama nomic-embed-text
        3. Queries ChromaDB collection using cosine similarity metric
        4. Returns top-K ranked SearchResult objects
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty or whitespace only.")

        # Step 1: Embed query text via Ollama
        query_vector = self.client.embed_text(query.strip())

        # Step 2: Query ChromaDB collection
        results = self.chroma_manager.query(
            query_embedding=query_vector,
            top_k=top_k,
            where=where
        )

        return results
