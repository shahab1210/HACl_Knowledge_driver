"""
Unit tests for P11 RAGLLMPipeline orchestration using mocked components.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipeline import RAGLLMPipeline
from models import DiagnosisResponse, SourceEvidence, RetrievalEvidence


def test_pipeline_initialization():
    pipeline = RAGLLMPipeline(
        top_k=5,
        model="qwen2.5:1.5b",
        temperature=0.3,
        max_tokens=512,
        rag_pipeline=MagicMock(),
        llm_pipeline=MagicMock()
    )
    assert pipeline.top_k == 5
    assert pipeline.model == "qwen2.5:1.5b"
    assert pipeline.temperature == 0.3
    assert pipeline.max_tokens == 512


def test_pipeline_run_flow_mocked():
    mock_rag = MagicMock()
    mock_rag.run.return_value = {
        "query": "The motor temperature is 95C and vibration is 7.2 mm/s.",
        "result_count": 2,
        "results": [
            {
                "rank": 1,
                "chunk_id": "FAULT-003_chunk_001",
                "document_id": "FAULT-003",
                "document_type": "fault",
                "title": "Motor Overheating",
                "source": "faults/motor-overheating.md",
                "similarity": 0.8920,
                "distance": 0.1080,
                "text": "Motor winding temperature above 80C indicates overheating.",
                "metadata": {"severity": "high"}
            },
            {
                "rank": 2,
                "chunk_id": "FAULT-005_chunk_001",
                "document_id": "FAULT-005",
                "document_type": "fault",
                "title": "Excessive Motor Vibration",
                "source": "faults/motor-vibration.md",
                "similarity": 0.8715,
                "distance": 0.1285,
                "text": "Vibration velocity above 7.0 mm/s indicates severe mechanical unbalance.",
                "metadata": {"severity": "critical"}
            }
        ],
        "context": "Knowledge Source 1\nTitle: Motor Overheating\n...\n\nKnowledge Source 2\nTitle: Excessive Motor Vibration\n..."
    }

    mock_llm_output = MagicMock()
    mock_llm_output.response = "Based on FAULT-003 and FAULT-005, the motor is experiencing overheating and severe vibration."
    mock_llm_output.model = "qwen2.5:1.5b"
    mock_llm_output.prompt = "### SYSTEM INSTRUCTIONS\n...\n### RETRIEVED KNOWLEDGE CONTEXT\n..."
    mock_llm_output.generation_details = {"eval_count": 82, "total_duration": 4500000000}

    mock_llm = MagicMock()
    mock_llm.generate_from_rag.return_value = mock_llm_output

    pipeline = RAGLLMPipeline(
        top_k=2,
        model="qwen2.5:1.5b",
        rag_pipeline=mock_rag,
        llm_pipeline=mock_llm
    )

    query = "The motor temperature is 95C and vibration is 7.2 mm/s."
    result = pipeline.run(query)

    assert isinstance(result, DiagnosisResponse)
    assert result.query == query
    assert "FAULT-003" in result.diagnosis
    assert result.model == "qwen2.5:1.5b"
    assert result.prompt == mock_llm_output.prompt
    assert result.generation_details["eval_count"] == 82

    # Verify retrieval evidence
    assert isinstance(result.retrieval, RetrievalEvidence)
    assert result.retrieval.result_count == 2
    assert result.retrieval.top_k == 2
    assert len(result.retrieval.sources) == 2
    assert result.retrieval.sources[0].title == "Motor Overheating"
    assert result.retrieval.sources[0].similarity == 0.8920
    assert result.retrieval.sources[1].title == "Excessive Motor Vibration"
    assert result.retrieval.sources[1].similarity == 0.8715

    # Verify mock invocations
    mock_rag.run.assert_called_once_with(query=query, top_k=2)
    mock_llm.generate_from_rag.assert_called_once()


def test_pipeline_diagnose_alias():
    mock_rag = MagicMock()
    mock_rag.run.return_value = {"query": "Test", "results": [], "context": "None"}

    mock_llm_out = MagicMock(response="Diagnosis", model="qwen2.5:1.5b", prompt="P", generation_details={})
    mock_llm = MagicMock()
    mock_llm.generate_from_rag.return_value = mock_llm_out

    pipeline = RAGLLMPipeline(
        rag_pipeline=mock_rag,
        llm_pipeline=mock_llm
    )

    res = pipeline.diagnose("Motor anomaly")
    assert res.diagnosis == "Diagnosis"


def test_pipeline_top_k_override():
    mock_rag = MagicMock()
    mock_rag.run.return_value = {"query": "Test", "results": [], "context": "None"}

    mock_llm_out = MagicMock(response="Diagnosis", model="qwen2.5:1.5b", prompt="P", generation_details={})
    mock_llm = MagicMock()
    mock_llm.generate_from_rag.return_value = mock_llm_out

    pipeline = RAGLLMPipeline(
        top_k=5,
        rag_pipeline=mock_rag,
        llm_pipeline=mock_llm
    )

    pipeline.run("Motor anomaly", top_k=2)
    mock_rag.run.assert_called_once_with(query="Motor anomaly", top_k=2)


def test_pipeline_insufficient_context_handling():
    mock_rag = MagicMock()
    mock_rag.run.return_value = {
        "query": "Unknown fault code 999",
        "results": [],
        "context": "No relevant knowledge was retrieved."
    }

    mock_llm_out = MagicMock(
        response="Insufficient knowledge in context to confirm diagnosis. Additional sensor telemetry is required.",
        model="qwen2.5:1.5b",
        prompt="Prompt with empty context",
        generation_details={}
    )
    mock_llm = MagicMock()
    mock_llm.generate_from_rag.return_value = mock_llm_out

    pipeline = RAGLLMPipeline(
        rag_pipeline=mock_rag,
        llm_pipeline=mock_llm
    )

    result = pipeline.run("Unknown fault code 999")
    assert result.retrieval.result_count == 0
    assert "Insufficient knowledge in context" in result.diagnosis
