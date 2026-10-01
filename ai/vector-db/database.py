"""
ChromaDB database manager for P8 Vector Database.
Manages persistent client initialization, collection lifecycle, idempotent upserting,
and semantic vector similarity queries with cosine distance metrics.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from config import CHROMA_PATH, COLLECTION_NAME, DISTANCE_METRIC
from models import StoredVectorRecord, SearchResult, CollectionStats


class ChromaManager:
    """
    Manages persistent ChromaDB client, collections, idempotent upserts, and vector queries.
    """

    def __init__(
        self,
        chroma_path: Optional[str] = None,
        collection_name: Optional[str] = None,
        metric: Optional[str] = None
    ):
        self.chroma_path = chroma_path or CHROMA_PATH
        self.collection_name = collection_name or COLLECTION_NAME
        self.metric = metric or DISTANCE_METRIC

        # Initialize persistent ChromaDB client with telemetry disabled
        self.client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.get_or_create_collection()

    def get_or_create_collection(self):
        """
        Creates or retrieves the persistent collection configured with explicit distance metric.
        In ChromaDB, 'hnsw:space' defines the distance metric (cosine, l2, or ip).
        """
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": self.metric}
        )

    def count(self) -> int:
        """Returns the total number of records currently stored in the collection."""
        return self.collection.count()

    def upsert_records(self, records: List[StoredVectorRecord]) -> int:
        """
        Idempotently inserts or updates records in ChromaDB using their deterministic chunk_id.
        Running upsert multiple times will update existing IDs without creating duplicates.
        """
        if not records:
            return 0

        ids = [rec.chunk_id for rec in records]
        embeddings = [rec.embedding for rec in records]
        documents = [rec.text for rec in records]
        metadatas = [rec.to_chroma_metadata() for rec in records]

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return len(records)

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Performs vector similarity search against stored embeddings.
        Returns a ranked list of SearchResult objects.
        """
        if not query_embedding or len(query_embedding) == 0:
            raise ValueError("Query embedding cannot be empty.")

        query_kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, max(1, self.count())),
            "include": ["documents", "metadatas", "distances"]
        }

        if where:
            query_kwargs["where"] = where

        response = self.collection.query(**query_kwargs)

        results: List[SearchResult] = []
        ids_list = response.get("ids", [[]])[0]
        docs_list = response.get("documents", [[]])[0]
        metas_list = response.get("metadatas", [[]])[0]
        dists_list = response.get("distances", [[]])[0]

        for rank, (cid, doc, meta, dist) in enumerate(zip(ids_list, docs_list, metas_list, dists_list), start=1):
            distance_val = float(dist)
            # In ChromaDB cosine metric: distance = 1 - cosine_similarity
            # Derived similarity: 1.0 - distance (clamped between 0.0 and 1.0 for positive cosine space)
            if self.metric == "cosine":
                similarity_val = round(max(0.0, min(1.0, 1.0 - distance_val)), 4)
            else:
                similarity_val = round(max(0.0, 1.0 / (1.0 + distance_val)), 4)

            result = SearchResult(
                rank=rank,
                chunk_id=cid,
                document_id=meta.get("document_id", ""),
                document_type=meta.get("document_type", ""),
                title=meta.get("title", ""),
                source=meta.get("source", ""),
                distance=round(distance_val, 6),
                similarity=similarity_val,
                text=doc,
                metadata=meta
            )
            results.append(result)

        return results

    def get_stats(self) -> CollectionStats:
        """Returns statistical overview of the persistent collection."""
        return CollectionStats(
            collection_name=self.collection_name,
            record_count=self.count(),
            chroma_path=self.chroma_path,
            distance_metric=self.metric
        )

    def delete_collection(self):
        """Deletes the collection (used for test teardown)."""
        self.client.delete_collection(name=self.collection_name)
