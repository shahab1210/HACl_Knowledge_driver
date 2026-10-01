"""
Unit tests for P12 data models.
"""

import sys
import json
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import (
    FaultReference,
    ConfidenceInfo,
    TelemetryEvidence,
    KnowledgeSourceInfo,
    StructuredDiagnosis,
)


def test_fault_reference_serialization():
    fault = FaultReference(
        fault_id="FAULT-003",
        title="Motor Overheating",
        severity="high",
        equipment="motor",
        similarity=0.89201
    )
    d = fault.to_dict()
    assert d["fault_id"] == "FAULT-003"
    assert d["title"] == "Motor Overheating"
    assert d["severity"] == "high"
    assert d["equipment"] == "motor"
    assert d["similarity"] == 0.8920

    reconstructed = FaultReference.from_dict(d)
    assert reconstructed.fault_id == "FAULT-003"
    assert reconstructed.title == "Motor Overheating"


def test_confidence_info_normalization():
    conf1 = ConfidenceInfo(level="HIGH", reason="Strong grounding")
    assert conf1.level == "high"
    assert conf1.reason == "Strong grounding"

    conf2 = ConfidenceInfo(level="invalid_level", reason="Invalid")
    assert conf2.level == "insufficient"


def test_telemetry_evidence_serialization():
    ev = TelemetryEvidence(
        parameter="temperature",
        value=95.5,
        unit="°C",
        status="high"
    )
    d = ev.to_dict()
    assert d["parameter"] == "temperature"
    assert d["value"] == 95.5
    assert d["unit"] == "°C"
    assert d["status"] == "high"
    assert d["type"] == "telemetry"

    reconstructed = TelemetryEvidence.from_dict(d)
    assert reconstructed.value == 95.5


def test_knowledge_source_info_serialization():
    ks = KnowledgeSourceInfo(
        rank=1,
        document_id="FAULT-003",
        chunk_id="FAULT-003_chunk_001",
        title="Motor Overheating",
        source="faults/motor-overheating.md",
        similarity=0.73902,
        distance=0.2610
    )
    d = ks.to_dict()
    assert d["rank"] == 1
    assert d["document_id"] == "FAULT-003"
    assert d["similarity"] == 0.7390
    assert d["distance"] == 0.2610


def test_structured_diagnosis_to_dict_and_to_json():
    primary = FaultReference(fault_id="FAULT-003", title="Motor Overheating", similarity=0.85)
    alt = FaultReference(fault_id="FAULT-005", title="Excessive Motor Vibration", similarity=0.80)
    conf = ConfidenceInfo(level="medium", reason="Multiple overlapping faults")
    ev = TelemetryEvidence(parameter="temperature", value=95, unit="°C")
    ks = KnowledgeSourceInfo(rank=1, document_id="FAULT-003", chunk_id="c1", title="Motor Overheating", source="s1", similarity=0.85)

    diag = StructuredDiagnosis(
        query="The motor temperature is 95°C",
        primary_fault=primary,
        alternative_faults=[alt],
        confidence=conf,
        evidence=[ev],
        possible_causes=["Electrical overload", "Phase unbalance"],
        recommended_checks=["Measure current with clamp meter", "Check fan cowl"],
        additional_information_required=["Current telemetry", "Vibration spectra"],
        knowledge_sources=[ks],
        raw_llm_response="Motor is overheating.",
        model="qwen2.5:1.5b"
    )

    data = diag.to_dict()
    assert data["query"] == "The motor temperature is 95°C"
    assert data["primary_fault"]["fault_id"] == "FAULT-003"
    assert len(data["alternative_faults"]) == 1
    assert data["alternative_faults"][0]["fault_id"] == "FAULT-005"
    assert data["confidence"]["level"] == "medium"
    assert len(data["possible_causes"]) == 2
    assert len(data["recommended_checks"]) == 2

    json_str = diag.to_json()
    parsed = json.loads(json_str)
    assert parsed["primary_fault"]["title"] == "Motor Overheating"

    rebuilt = StructuredDiagnosis.from_dict(parsed)
    assert rebuilt.primary_fault.fault_id == "FAULT-003"
    assert len(rebuilt.alternative_faults) == 1
