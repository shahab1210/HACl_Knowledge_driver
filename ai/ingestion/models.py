"""
Data models for the P6 Document Ingestion Pipeline.
Defines Document and Chunk data structures used across parsing,
chunking, validation, and JSON export.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class Document:
    """Represents a fully parsed and normalized knowledge document."""
    document_id: str
    title: str
    document_type: str  # 'fault', 'sensor', 'procedure', 'documentation'
    source: str         # Relative path within knowledge-base (e.g. 'faults/bearing-overheating.md')
    category: Optional[str] = None
    equipment: Optional[str] = None
    severity: Optional[str] = None
    sensors: List[str] = field(default_factory=list)
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Document instance to dictionary."""
        return asdict(self)


@dataclass
class Chunk:
    """Represents a coherent text chunk derived from a document, ready for embedding."""
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
    section_heading: Optional[str] = None
    token_estimate: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert Chunk instance to dictionary."""
        return asdict(self)
