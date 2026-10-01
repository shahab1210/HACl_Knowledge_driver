"""
Data models for P12 Diagnosis Engine Layer.

Defines standardized machine-readable containers for primary and alternative
fault diagnoses, confidence levels, telemetry evidence, knowledge source traceability,
and recommended diagnostic actions.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union


VALID_CONFIDENCE_LEVELS = {"high", "medium", "low", "insufficient"}


@dataclass
class FaultReference:
    """
    Structured domain reference to an identified fault.
    """
    fault_id: str
    title: str
    severity: Optional[str] = None
    equipment: Optional[str] = None
    document_type: str = "fault"
    similarity: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FaultReference":
        return cls(
            fault_id=str(data.get("fault_id", "")).strip(),
            title=str(data.get("title", "")).strip(),
            severity=data.get("severity"),
            equipment=data.get("equipment"),
            document_type=str(data.get("document_type", "fault")),
            similarity=float(data.get("similarity")) if data.get("similarity") is not None else None
        )

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "fault_id": self.fault_id,
            "title": self.title,
            "document_type": self.document_type
        }
        if self.severity is not None:
            d["severity"] = self.severity
        if self.equipment is not None:
            d["equipment"] = self.equipment
        if self.similarity is not None:
            d["similarity"] = round(self.similarity, 4)
        return d


@dataclass
class ConfidenceInfo:
    """
    Controlled uncertainty representation for the diagnosis.
    """
    level: str  # "high", "medium", "low", "insufficient"
    reason: str = ""

    def __post_init__(self):
        self.level = self.level.lower().strip()
        if self.level not in VALID_CONFIDENCE_LEVELS:
            self.level = "insufficient"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfidenceInfo":
        return cls(
            level=str(data.get("level", "insufficient")),
            reason=str(data.get("reason", "")).strip()
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "reason": self.reason
        }


@dataclass
class TelemetryEvidence:
    """
    Telemetry parameter observation parsed from the query or sensor telemetry.
    """
    parameter: str
    type: str = "telemetry"
    value: Optional[Union[float, int, str]] = None
    unit: Optional[str] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryEvidence":
        return cls(
            parameter=str(data.get("parameter", "")),
            type=str(data.get("type", "telemetry")),
            value=data.get("value"),
            unit=data.get("unit"),
            status=data.get("status")
        )

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "type": self.type,
            "parameter": self.parameter
        }
        if self.value is not None:
            d["value"] = self.value
        if self.unit is not None:
            d["unit"] = self.unit
        if self.status is not None:
            d["status"] = self.status
        return d


@dataclass
class KnowledgeSourceInfo:
    """
    Traceable reference to a retrieved P5 knowledge chunk that grounded the diagnosis.
    """
    rank: int
    document_id: str
    chunk_id: str
    title: str
    source: str
    similarity: float
    distance: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeSourceInfo":
        return cls(
            rank=int(data.get("rank", 0)),
            document_id=str(data.get("document_id", "")),
            chunk_id=str(data.get("chunk_id", "")),
            title=str(data.get("title", "")),
            source=str(data.get("source", "")),
            similarity=float(data.get("similarity", 0.0)),
            distance=float(data.get("distance", 0.0))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "title": self.title,
            "source": self.source,
            "similarity": round(self.similarity, 4),
            "distance": round(self.distance, 4)
        }


@dataclass
class StructuredDiagnosis:
    """
    Complete, standardized, machine-readable fault diagnosis report produced by P12.
    """
    query: str
    primary_fault: Optional[FaultReference] = None
    alternative_faults: List[FaultReference] = field(default_factory=list)
    confidence: ConfidenceInfo = field(default_factory=lambda: ConfidenceInfo(level="medium", reason=""))
    evidence: List[TelemetryEvidence] = field(default_factory=list)
    possible_causes: List[str] = field(default_factory=list)
    recommended_checks: List[str] = field(default_factory=list)
    additional_information_required: List[str] = field(default_factory=list)
    knowledge_sources: List[KnowledgeSourceInfo] = field(default_factory=list)
    raw_llm_response: str = ""
    model: str = ""
    generation_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "primary_fault": self.primary_fault.to_dict() if self.primary_fault else None,
            "alternative_faults": [f.to_dict() for f in self.alternative_faults],
            "confidence": self.confidence.to_dict(),
            "evidence": [e.to_dict() for e in self.evidence],
            "possible_causes": self.possible_causes,
            "recommended_checks": self.recommended_checks,
            "additional_information_required": self.additional_information_required,
            "knowledge_sources": [k.to_dict() for k in self.knowledge_sources],
            "raw_llm_response": self.raw_llm_response,
            "model": self.model,
            "generation_details": self.generation_details
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuredDiagnosis":
        primary = FaultReference.from_dict(data["primary_fault"]) if data.get("primary_fault") else None
        alternatives = [FaultReference.from_dict(f) for f in data.get("alternative_faults", []) if f]
        confidence = ConfidenceInfo.from_dict(data.get("confidence", {}))
        evidence = [TelemetryEvidence.from_dict(e) for e in data.get("evidence", [])]
        sources = [KnowledgeSourceInfo.from_dict(k) for k in data.get("knowledge_sources", [])]

        return cls(
            query=str(data.get("query", "")),
            primary_fault=primary,
            alternative_faults=alternatives,
            confidence=confidence,
            evidence=evidence,
            possible_causes=data.get("possible_causes", []),
            recommended_checks=data.get("recommended_checks", []),
            additional_information_required=data.get("additional_information_required", []),
            knowledge_sources=sources,
            raw_llm_response=str(data.get("raw_llm_response", "")),
            model=str(data.get("model", "")),
            generation_details=data.get("generation_details", {})
        )
