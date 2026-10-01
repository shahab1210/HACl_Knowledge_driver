"""
Data models for the P7 Embedding Layer.
Defines ChunkRecord (input representation from P6), EmbeddingRecord (embedded chunk),
and EmbeddingOutput (complete serialization schema for embeddings.json).
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class ChunkRecord:
    """Represents a validated text chunk ingested from P6 chunks.json."""
    chunk_id: str
    document_id: str
    document_type: str
    source: str
    chunk_index: int
    title: str
    text: str
    category: Optional[str] = None
    equipment: Optional[str] = None
    severity: Optional[str] = None
    sensors: List[str] = field(default_factory=list)
    section_heading: Optional[str] = None
    token_estimate: Optional[int] = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkRecord":
        """Instantiate ChunkRecord from a dictionary, safely handling optional fields."""
        return cls(
            chunk_id=str(data.get("chunk_id", "")).strip(),
            document_id=str(data.get("document_id", "")).strip(),
            document_type=str(data.get("document_type", "")).strip(),
            source=str(data.get("source", "")).strip(),
            chunk_index=int(data.get("chunk_index", 0)),
            title=str(data.get("title", "")).strip(),
            text=str(data.get("text", "")).strip(),
            category=data.get("category"),
            equipment=data.get("equipment"),
            severity=data.get("severity"),
            sensors=data.get("sensors") or [],
            section_heading=data.get("section_heading"),
            token_estimate=data.get("token_estimate", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ChunkRecord to a dictionary."""
        return asdict(self)


@dataclass
class EmbeddingRecord:
    """Represents a chunk enriched with dense embedding vector and model metadata."""
    chunk_id: str
    document_id: str
    document_type: str
    source: str
    chunk_index: int
    title: str
    category: Optional[str]
    equipment: Optional[str]
    severity: Optional[str]
    sensors: List[str]
    text: str
    embedding: List[float]
    embedding_dimension: int
    embedding_model: str

    @classmethod
    def from_chunk(
        cls,
        chunk: ChunkRecord,
        embedding: List[float],
        embedding_model: str
    ) -> "EmbeddingRecord":
        """Construct an EmbeddingRecord from an input ChunkRecord and its computed vector."""
        return cls(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            document_type=chunk.document_type,
            source=chunk.source,
            chunk_index=chunk.chunk_index,
            title=chunk.title,
            category=chunk.category,
            equipment=chunk.equipment,
            severity=chunk.severity,
            sensors=chunk.sensors,
            text=chunk.text,
            embedding=embedding,
            embedding_dimension=len(embedding),
            embedding_model=embedding_model,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize EmbeddingRecord to a dictionary."""
        return asdict(self)


@dataclass
class EmbeddingOutput:
    """Top-level container for serialized embeddings artifact."""
    generated_at: str
    source: str
    embedding_model: str
    document_count: int
    chunk_count: int
    embedding_dimension: int
    embeddings: List[EmbeddingRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete output payload."""
        return {
            "generated_at": self.generated_at,
            "source": self.source,
            "embedding_model": self.embedding_model,
            "document_count": self.document_count,
            "chunk_count": self.chunk_count,
            "embedding_dimension": self.embedding_dimension,
            "embeddings": [emb.to_dict() for emb in self.embeddings]
        }
