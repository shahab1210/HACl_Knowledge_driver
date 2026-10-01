"""
Unit tests for P12 DiagnosisEngine orchestrator.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from engine import DiagnosisEngine
from models import StructuredDiagnosis
from exceptions import DiagnosisInputError, DiagnosisEngineError


def test_engine_analyze_p11_response_mocked():
    mock_p11 = MagicMock()
    mock_p11.to_dict.return_value = {
        "query": "The motor temperature is 95C and vibration is 7.2 mm/s.",
        "diagnosis": (
            "### Diagnostic Analysis\n"
            "Motor is overheating (FAULT-003) with excessive vibration (FAULT-005).\n\n"
            "### Possible Causes\n"
            "- Electrical overload on stator.\n\n"
            "### Recommended Checks\n"
            "- Measure current with true-RMS clamp meter.\n"
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
                    "similarity": 0.89,
                    "distance": 0.11
                },
                {
                    "rank": 2,
                    "document_id": "FAULT-005",
                    "chunk_id": "FAULT-005_chunk_001",
                    "title": "Excessive Motor Vibration",
                    "source": "faults/motor-vibration.md",
                    "similarity": 0.87,
                    "distance": 0.13
                }
            ]
        }
    }

    engine = DiagnosisEngine(pipeline=MagicMock())
    result = engine.analyze(mock_p11)

    assert isinstance(result, StructuredDiagnosis)
    assert result.primary_fault.fault_id == "FAULT-003"
    assert result.alternative_faults[0].fault_id == "FAULT-005"
    assert result.confidence.level == "medium"
    assert len(result.possible_causes) == 1
    assert len(result.recommended_checks) == 1


def test_engine_diagnose_end_to_end_mocked():
    mock_pipeline = MagicMock()
    mock_pipeline.run.return_value = {
        "query": "Bearing high temp",
        "diagnosis": "Bearing is overheating per FAULT-001.",
        "model": "qwen2.5:1.5b",
        "retrieval": {
            "result_count": 1,
            "sources": [
                {
                    "rank": 1,
                    "document_id": "FAULT-001",
                    "chunk_id": "c1",
                    "title": "Bearing Overheating",
                    "source": "s1",
                    "similarity": 0.88,
                    "distance": 0.12
                }
            ]
        }
    }

    engine = DiagnosisEngine(pipeline=mock_pipeline)
    result = engine.diagnose("Bearing high temp", top_k=2)

    assert isinstance(result, StructuredDiagnosis)
    assert result.primary_fault.fault_id == "FAULT-001"
    assert result.confidence.level == "high"
    mock_pipeline.run.assert_called_once_with(query="Bearing high temp", top_k=2, temperature=None, max_tokens=None)


def test_engine_empty_query_raises_input_error():
    engine = DiagnosisEngine(pipeline=MagicMock())
    with pytest.raises(DiagnosisInputError):
        engine.diagnose("")


def test_engine_none_input_to_analyze_raises_input_error():
    engine = DiagnosisEngine(pipeline=MagicMock())
    with pytest.raises(DiagnosisInputError):
        engine.analyze(None)


def test_engine_propagates_pipeline_error():
    mock_pipeline = MagicMock()
    mock_pipeline.run.side_effect = RuntimeError("ChromaDB error")

    engine = DiagnosisEngine(pipeline=mock_pipeline)
    with pytest.raises(DiagnosisEngineError) as exc:
        engine.diagnose("Motor overheating")
    assert "P11 pipeline execution failed" in str(exc.value)
