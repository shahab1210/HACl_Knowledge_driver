"""
Unit tests for P12 DiagnosisValidator.
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from validator import DiagnosisValidator, validate_diagnosis
from models import (
    StructuredDiagnosis,
    FaultReference,
    ConfidenceInfo,
    TelemetryEvidence,
    KnowledgeSourceInfo,
)
from exceptions import DiagnosisValidationError


def test_validator_accepts_valid_diagnosis():
    validator = DiagnosisValidator()
    diag = StructuredDiagnosis(
        query="Motor temperature high",
        primary_fault=FaultReference(fault_id="FAULT-003", title="Motor Overheating"),
        confidence=ConfidenceInfo(level="high", reason="Strong match"),
        evidence=[TelemetryEvidence(parameter="temperature", value=95, unit="°C")],
        knowledge_sources=[
            KnowledgeSourceInfo(rank=1, document_id="FAULT-003", chunk_id="c1", title="Motor Overheating", source="s", similarity=0.85)
        ]
    )
    assert validator.validate(diag) is True
    assert validate_diagnosis(diag) is True


def test_validator_rejects_non_structured_diagnosis():
    validator = DiagnosisValidator()
    with pytest.raises(DiagnosisValidationError):
        validator.validate({"query": "Motor overheating"})


def test_validator_rejects_empty_query():
    validator = DiagnosisValidator()
    diag = StructuredDiagnosis(
        query="",
        confidence=ConfidenceInfo(level="medium")
    )
    with pytest.raises(DiagnosisValidationError):
        validator.validate(diag)


def test_validator_rejects_invalid_confidence_level():
    validator = DiagnosisValidator()
    diag = StructuredDiagnosis(
        query="Motor overheating",
        confidence=ConfidenceInfo(level="medium")
    )
    # Bypass post_init to test validator guard
    diag.confidence.level = "unsupported_level"
    with pytest.raises(DiagnosisValidationError):
        validator.validate(diag)


def test_validator_rejects_invalid_primary_fault():
    validator = DiagnosisValidator()
    diag = StructuredDiagnosis(
        query="Motor overheating",
        primary_fault=FaultReference(fault_id="", title="Motor Overheating"),
        confidence=ConfidenceInfo(level="high")
    )
    with pytest.raises(DiagnosisValidationError):
        validator.validate(diag)


def test_validator_rejects_invalid_alternative_faults():
    validator = DiagnosisValidator()
    diag = StructuredDiagnosis(
        query="Motor overheating",
        alternative_faults=[FaultReference(fault_id="FAULT-005", title="")],
        confidence=ConfidenceInfo(level="medium")
    )
    with pytest.raises(DiagnosisValidationError):
        validator.validate(diag)


def test_validator_rejects_invalid_knowledge_source_similarity():
    validator = DiagnosisValidator()
    diag = StructuredDiagnosis(
        query="Motor overheating",
        confidence=ConfidenceInfo(level="medium"),
        knowledge_sources=[
            KnowledgeSourceInfo(rank=1, document_id="FAULT-003", chunk_id="c1", title="T", source="s", similarity=1.5)
        ]
    )
    with pytest.raises(DiagnosisValidationError):
        validator.validate(diag)


def test_validator_rejects_invalid_telemetry_evidence():
    validator = DiagnosisValidator()
    diag = StructuredDiagnosis(
        query="Motor overheating",
        confidence=ConfidenceInfo(level="medium"),
        evidence=[TelemetryEvidence(parameter="")]
    )
    with pytest.raises(DiagnosisValidationError):
        validator.validate(diag)
