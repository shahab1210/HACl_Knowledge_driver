"""
Data models for P11 RAG + LLM Integration Layer.

Defines structured containers for retrieval evidence, generation metadata,
and the unified diagnosis response.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class SourceEvidence:
    """
    Represents an individual retrieved knowledge chunk with full domain traceability.
    """
    rank: int
    chunk_id: str
    document_id: str
    document_type: str
    title: str
    source: str
    similarity: float
    distance: float
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceEvidence":
        return cls(
            rank=int(data.get("rank", 0)),
            chunk_id=str(data.get("chunk_id", "")),
            document_id=str(data.get("document_id", "")),
            document_type=str(data.get("document_type", "")),
            title=str(data.get("title", "")),
            source=str(data.get("source", "")),
            similarity=float(data.get("similarity", 0.0)),
            distance=float(data.get("distance", 0.0)),
            text=str(data.get("text", "")),
            metadata=data.get("metadata") or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievalEvidence:
    """
    Encapsulates all knowledge retrieved from ChromaDB during the RAG stage.
    """
    query: str
    result_count: int
    top_k: int
    sources: List[SourceEvidence] = field(default_factory=list)
    context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "result_count": self.result_count,
            "top_k": self.top_k,
            "sources": [s.to_dict() for s in self.sources],
            "context": self.context,
        }


@dataclass
class DiagnosisResponse:
    """
    Unified structured response containing the generated diagnosis,
    grounded prompt, preserved retrieval evidence, and LLM telemetry.
    """
    query: str
    diagnosis: str
    retrieval: RetrievalEvidence
    context: str
    prompt: str
    response: str
    model: str
    generation_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "diagnosis": self.diagnosis,
            "retrieval": self.retrieval.to_dict(),
            "context": self.context,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "generation_details": self.generation_details
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
