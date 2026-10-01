"""
Unit tests for P11 data models.
"""

import sys
import json
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import SourceEvidence, RetrievalEvidence, DiagnosisResponse


def test_source_evidence_serialization():
    data = {
        "rank": 1,
        "chunk_id": "FAULT-003_chunk_001",
        "document_id": "FAULT-003",
        "document_type": "fault",
        "title": "Motor Overheating",
        "source": "faults/motor-overheating.md",
        "similarity": 0.8920,
        "distance": 0.1080,
        "text": "Motor winding temperature exceeds 80C.",
        "metadata": {"severity": "high", "equipment": "motor"}
    }
    source = SourceEvidence.from_dict(data)
    assert source.rank == 1
    assert source.chunk_id == "FAULT-003_chunk_001"
    assert source.document_id == "FAULT-003"
    assert source.similarity == 0.8920
    assert source.metadata["severity"] == "high"

    serialized = source.to_dict()
    assert serialized["title"] == "Motor Overheating"
    assert serialized["distance"] == 0.1080


def test_retrieval_evidence_serialization():
    source = SourceEvidence(
        rank=1,
        chunk_id="FAULT-001_chunk_001",
        document_id="FAULT-001",
        document_type="fault",
        title="Bearing Overheating",
        source="faults/bearing-overheating.md",
        similarity=0.85,
        distance=0.15,
        text="Bearing temperature exceeds 75C."
    )
    retrieval = RetrievalEvidence(
        query="Motor bearing temp high",
        result_count=1,
        top_k=3,
        sources=[source],
        context="Knowledge Source 1: Bearing Overheating"
    )
    data = retrieval.to_dict()
    assert data["query"] == "Motor bearing temp high"
    assert data["result_count"] == 1
    assert data["top_k"] == 3
    assert len(data["sources"]) == 1
    assert data["sources"][0]["document_id"] == "FAULT-001"


def test_diagnosis_response_serialization_and_json():
    retrieval = RetrievalEvidence(
        query="Motor overheating",
        result_count=1,
        top_k=1,
        sources=[],
        context="Context"
    )
    resp = DiagnosisResponse(
        query="Motor overheating",
        diagnosis="Motor is overheating due to excessive load.",
        retrieval=retrieval,
        context="Context",
        prompt="Prompt text",
        response="Motor is overheating due to excessive load.",
        model="qwen2.5:1.5b",
        generation_details={"eval_count": 45, "total_duration": 1200000}
    )

    d = resp.to_dict()
    assert d["query"] == "Motor overheating"
    assert d["diagnosis"] == "Motor is overheating due to excessive load."
    assert d["model"] == "qwen2.5:1.5b"
    assert d["generation_details"]["eval_count"] == 45

    json_str = resp.to_json()
    parsed = json.loads(json_str)
    assert parsed["query"] == "Motor overheating"
    assert parsed["model"] == "qwen2.5:1.5b"
