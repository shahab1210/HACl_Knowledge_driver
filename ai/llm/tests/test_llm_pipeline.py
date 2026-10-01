"""
Unit tests for P10 LLMPipeline orchestration.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from llm_pipeline import LLMPipeline
from prompt_builder import PromptBuilder
from client import LocalLLMClient
from models import (
    GenerationResponse,
    GenerationOptions,
    LLMPipelineOutput,
    LLMValidationError,
    OllamaConnectionError,
)


def test_pipeline_generate_from_query_and_context():
    mock_client = MagicMock(spec=LocalLLMClient)
    mock_client.generate.return_value = GenerationResponse(
        text="Based on Knowledge Source 1 (FAULT-003), the motor is overheating.",
        model="llama3.2:3b",
        prompt="Sample prompt"
    )

    pipeline = LLMPipeline(client=mock_client)

    output = pipeline.generate(
        query="Motor temperature is 95C",
        context="Knowledge Source 1: Motor Overheating (FAULT-003)"
    )

    assert isinstance(output, LLMPipelineOutput)
    assert output.query == "Motor temperature is 95C"
    assert "FAULT-003" in output.context
    assert "overheating" in output.response
    assert output.model == "llama3.2:3b"
    assert mock_client.generate.called


def test_pipeline_generate_from_rag_output():
    mock_client = MagicMock(spec=LocalLLMClient)
    mock_client.generate.return_value = GenerationResponse(
        text="Bearing wear is detected per FAULT-002.",
        model="llama3.2:3b",
        prompt="Sample prompt"
    )

    pipeline = LLMPipeline(client=mock_client)

    rag_output = {
        "query": "High vibration on bearing housing",
        "result_count": 2,
        "results": [
            {"title": "Bearing Wear", "document_id": "FAULT-002", "text": "Bearing wear causes vibration."}
        ],
        "context": "Knowledge Source 1\nTitle: Bearing Wear\nDocument ID: FAULT-002\nBearing wear causes vibration."
    }

    output = pipeline.generate_from_rag(rag_output)

    assert isinstance(output, LLMPipelineOutput)
    assert output.query == "High vibration on bearing housing"
    assert output.result_count == 2
    assert "Bearing wear" in output.response
    assert output.model == "llama3.2:3b"


def test_pipeline_empty_query_raises_validation_error():
    pipeline = LLMPipeline(client=MagicMock(spec=LocalLLMClient))
    with pytest.raises(LLMValidationError):
        pipeline.generate(query="", context="Some context")


def test_pipeline_empty_rag_output_raises_validation_error():
    pipeline = LLMPipeline(client=MagicMock(spec=LocalLLMClient))
    with pytest.raises(LLMValidationError):
        pipeline.generate_from_rag({})


def test_pipeline_invalid_rag_output_type_raises_validation_error():
    pipeline = LLMPipeline(client=MagicMock(spec=LocalLLMClient))
    with pytest.raises(LLMValidationError):
        pipeline.generate_from_rag("not a dict")


def test_pipeline_empty_context_handling():
    mock_client = MagicMock(spec=LocalLLMClient)
    mock_client.generate.return_value = GenerationResponse(
        text="Insufficient knowledge in context to confirm diagnosis. Further vibration analysis needed.",
        model="llama3.2:3b",
        prompt="Prompt text"
    )

    pipeline = LLMPipeline(client=mock_client)

    output = pipeline.generate(
        query="Unknown sensor anomaly",
        context=""
    )

    assert "No relevant knowledge context was provided." in output.context
    assert "Insufficient knowledge in context" in output.response


def test_pipeline_output_serialization():
    mock_client = MagicMock(spec=LocalLLMClient)
    mock_client.generate.return_value = GenerationResponse(
        text="Diagnosis result",
        model="llama3.2:3b",
        prompt="Prompt text",
        total_duration=123456
    )

    pipeline = LLMPipeline(client=mock_client)
    output = pipeline.generate(query="Test query", context="Test context")

    data = output.to_dict()
    assert isinstance(data, dict)
    assert data["query"] == "Test query"
    assert data["response"] == "Diagnosis result"
    assert data["model"] == "llama3.2:3b"
    assert data["generation_details"]["total_duration"] == 123456


def test_pipeline_propagates_connection_error():
    mock_client = MagicMock(spec=LocalLLMClient)
    mock_client.generate.side_effect = OllamaConnectionError("Ollama server down")

    pipeline = LLMPipeline(client=mock_client)

    with pytest.raises(OllamaConnectionError):
        pipeline.generate(query="Test query", context="Test context")
