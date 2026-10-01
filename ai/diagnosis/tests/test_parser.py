"""
Unit tests for P12 DiagnosisParser.
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parser import DiagnosisParser
from exceptions import DiagnosisInputError


def test_parser_extracts_primary_and_alternative_faults():
    parser = DiagnosisParser()

    p11_data = {
        "query": "The motor temperature is 95°C and vibration is 7.2 mm/s.",
        "diagnosis": (
            "### Diagnostic Analysis\n"
            "The motor is experiencing overheating (FAULT-003) and excessive vibration (FAULT-005).\n\n"
            "### Possible Causes\n"
            "- Electrical overload on motor windings.\n"
            "- Mechanical unbalance and coupling misalignment.\n\n"
            "### Recommended Checks\n"
            "- Measure current using clamp meter.\n"
            "- Perform vibration spectrum analysis.\n"
        ),
        "model": "qwen2.5:1.5b",
        "retrieval": {
            "result_count": 2,
            "sources": [
                {
                    "rank": 1,
                    "document_id": "FAULT-003",
                    "chunk_id": "FAULT-003_chunk_001",
                    "title": "Motor Overheating",
                    "source": "faults/motor-overheating.md",
                    "similarity": 0.8920,
                    "distance": 0.1080
                },
                {
                    "rank": 2,
                    "document_id": "FAULT-005",
                    "chunk_id": "FAULT-005_chunk_001",
                    "title": "Excessive Motor Vibration",
                    "source": "faults/motor-vibration.md",
                    "similarity": 0.8715,
                    "distance": 0.1285
                }
            ]
        }
    }

    result = parser.parse(p11_data)

    assert result.primary_fault is not None
    assert result.primary_fault.fault_id == "FAULT-003"
    assert result.primary_fault.title == "Motor Overheating"
    assert len(result.alternative_faults) == 1
    assert result.alternative_faults[0].fault_id == "FAULT-005"
    assert result.confidence.level == "medium"
    assert len(result.possible_causes) == 2
    assert "Electrical overload" in result.possible_causes[0]
    assert len(result.recommended_checks) == 2
    assert "clamp meter" in result.recommended_checks[0]


def test_parser_extracts_telemetry_evidence():
    parser = DiagnosisParser()

    p11_data = {
        "query": "Motor temperature is 95°C, vibration is 7.2 mm/s, and current is 35A.",
        "diagnosis": "Analysis...",
        "retrieval": {"sources": []}
    }

    result = parser.parse(p11_data)

    params = {e.parameter: e for e in result.evidence}
    assert "temperature" in params
    assert params["temperature"].value == 95
    assert params["temperature"].unit == "°C"

    assert "vibration" in params
    assert params["vibration"].value == 7.2
    assert params["vibration"].unit == "mm/s"

    assert "current" in params
    assert params["current"].value == 35
    assert params["current"].unit == "A"


def test_parser_handles_insufficient_context():
    parser = DiagnosisParser()

    p11_data = {
        "query": "Unknown sensor fluctuation",
        "diagnosis": (
            "### Diagnostic Analysis\n"
            "Insufficient knowledge in context to confirm diagnosis. Further sensor telemetry or physical inspection is required.\n\n"
            "### Additional Considerations\n"
            "- Additional sensor telemetry is needed for vibration spectra.\n"
            "- Physical inspection of bearings is required.\n"
        ),
        "retrieval": {
            "result_count": 1,
            "sources": [
                {
                    "rank": 1,
                    "document_id": "FAULT-001",
                    "chunk_id": "FAULT-001_chunk_001",
                    "title": "Bearing Overheating",
                    "source": "faults/bearing-overheating.md",
                    "similarity": 0.55,
                    "distance": 0.45
                }
            ]
        }
    }

    result = parser.parse(p11_data)

    assert result.confidence.level == "insufficient"
    assert "Insufficient" in result.confidence.reason or "insufficient" in result.confidence.reason
    assert len(result.additional_information_required) >= 1


def test_parser_handles_empty_retrieval():
    parser = DiagnosisParser()

    p11_data = {
        "query": "Unrelated question",
        "diagnosis": "No relevant knowledge was retrieved.",
        "retrieval": {"result_count": 0, "sources": []}
    }

    result = parser.parse(p11_data)

    assert result.primary_fault is None
    assert len(result.alternative_faults) == 0
    assert result.confidence.level == "insufficient"


def test_parser_rejects_none_input():
    parser = DiagnosisParser()
    with pytest.raises(DiagnosisInputError):
        parser.parse(None)
