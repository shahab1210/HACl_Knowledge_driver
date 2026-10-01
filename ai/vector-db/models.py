"""
Data models for the P8 Vector Database layer.
Defines StoredVectorRecord (representation of records in ChromaDB),
SearchResult (structured semantic similarity query output), and CollectionStats.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class StoredVectorRecord:
    """Represents a validated vector record ready for insertion or retrieval in ChromaDB."""
    chunk_id: str
    document_id: str
    document_type: str
    source: str
    chunk_index: int
    title: str
    text: str
    embedding: List[float]
    embedding_dimension: int
    embedding_model: str
    category: Optional[str] = None
    equipment: Optional[str] = None
    severity: Optional[str] = None
    sensors: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoredVectorRecord":
        """Instantiate StoredVectorRecord from a dictionary."""
        sensors_raw = data.get("sensors") or []
        if isinstance(sensors_raw, str):
            sensors = [s.strip() for s in sensors_raw.split(",") if s.strip()]
        else:
            sensors = list(sensors_raw)

        return cls(
            chunk_id=str(data.get("chunk_id", "")).strip(),
            document_id=str(data.get("document_id", "")).strip(),
            document_type=str(data.get("document_type", "")).strip(),
            source=str(data.get("source", "")).strip(),
            chunk_index=int(data.get("chunk_index", 0)),
            title=str(data.get("title", "")).strip(),
            text=str(data.get("text", "")).strip(),
            embedding=[float(x) for x in data.get("embedding", [])],
            embedding_dimension=int(data.get("embedding_dimension", len(data.get("embedding", [])))),
            embedding_model=str(data.get("embedding_model", "")).strip(),
            category=data.get("category"),
            equipment=data.get("equipment"),
            severity=data.get("severity"),
            sensors=sensors,
        )

    def to_chroma_metadata(self) -> Dict[str, Any]:
        """
        Converts attributes into ChromaDB-compatible metadata.
        ChromaDB metadata requires primitive values (str, int, float, bool).
        Lists such as 'sensors' are serialized to comma-separated strings.
        None values are stored as empty strings.
        """
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "source": self.source,
            "chunk_index": self.chunk_index,
            "title": self.title,
            "category": self.category or "",
            "equipment": self.equipment or "",
            "severity": self.severity or "",
            "sensors": ",".join(self.sensors) if self.sensors else "",
            "embedding_model": self.embedding_model,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize record to dictionary."""
        return asdict(self)


@dataclass
class SearchResult:
    """Represents a structured result returned from a semantic similarity query."""
    rank: int
    chunk_id: str
    document_id: str
    document_type: str
    title: str
    source: str
    distance: float
    similarity: float
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize search result to dictionary."""
        return asdict(self)


@dataclass
class CollectionStats:
    """Summary statistics for the ChromaDB collection."""
    collection_name: str
    record_count: int
    chroma_path: str
    distance_metric: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize statistics to dictionary."""
        return asdict(self)
