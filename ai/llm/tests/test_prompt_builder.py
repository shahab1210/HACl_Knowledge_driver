"""
Unit tests for P10 Prompt Builder.
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from prompt_builder import PromptBuilder, build_prompt, build_messages
from models import LLMValidationError


def test_build_prompt_with_valid_query_and_context():
    query = "The motor temperature is 95C and vibration is 7.2 mm/s."
    context = (
        "Knowledge Source 1\n"
        "Title: Motor Overheating\n"
        "Document ID: FAULT-003\n"
        "Source: faults/motor-overheating.md\n"
        "Similarity: 0.8920\n\n"
        "Motor overheating occurs when winding temperatures exceed 80C."
    )
    prompt = build_prompt(query=query, context=context)

    assert isinstance(prompt, str)
    assert query in prompt
    assert "Motor Overheating" in prompt
    assert "FAULT-003" in prompt
    assert "SYSTEM INSTRUCTIONS" in prompt
    assert "RETRIEVED KNOWLEDGE CONTEXT" in prompt
    assert "TELEMETRY SYMPTOMS & QUERY" in prompt


def test_build_prompt_empty_query_raises_validation_error():
    builder = PromptBuilder()
    with pytest.raises(LLMValidationError):
        builder.build_prompt(query="", context="Some context")


def test_build_prompt_whitespace_query_raises_validation_error():
    builder = PromptBuilder()
    with pytest.raises(LLMValidationError):
        builder.build_prompt(query="   \n\t  ", context="Some context")


def test_build_prompt_non_string_query_raises_validation_error():
    builder = PromptBuilder()
    with pytest.raises(LLMValidationError):
        builder.build_prompt(query=12345, context="Some context")


def test_build_prompt_empty_context_handled_gracefully():
    prompt = build_prompt(
        query="Motor vibration anomaly",
        context=""
    )
    assert "No relevant knowledge context was provided." in prompt
    assert "Motor vibration anomaly" in prompt


def test_build_prompt_none_context_handled_gracefully():
    prompt = build_prompt(
        query="Motor vibration anomaly",
        context=None
    )
    assert "No relevant knowledge context was provided." in prompt


def test_build_prompt_from_rag_output_dict():
    rag_output = {
        "query": "Bearing high temp",
        "result_count": 1,
        "results": [
            {
                "title": "Bearing Overheating",
                "document_id": "FAULT-001",
                "source": "faults/bearing-overheating.md",
                "similarity": 0.85,
                "text": "Bearing temperature above 75C indicates lack of lubrication."
            }
        ],
        "context": "Knowledge Source 1\nTitle: Bearing Overheating\nDocument ID: FAULT-001\nBearing temp above 75C."
    }
    prompt = build_prompt(query=rag_output["query"], context=rag_output)
    assert "Bearing Overheating" in prompt
    assert "FAULT-001" in prompt


def test_build_prompt_from_results_list():
    results = [
        {
            "title": "Pump Cavitation",
            "document_id": "FAULT-005",
            "source": "faults/pump-cavitation.md",
            "similarity": 0.9123,
            "text": "Cavitation produces crackling noise and pressure fluctuations."
        }
    ]
    prompt = build_prompt(query="Pump crackling sound", context=results)
    assert "Knowledge Source 1" in prompt
    assert "Pump Cavitation" in prompt
    assert "FAULT-005" in prompt
    assert "Similarity: 0.9123" in prompt


def test_build_prompt_contains_grounding_directives():
    prompt = build_prompt(query="Test query", context="Test context")
    assert "Grounding: Base your diagnosis" in prompt
    assert "No Hallucination" in prompt
    assert "Source Citation" in prompt
    assert "Knowledge vs Hypotheses" in prompt
    assert "Insufficient Context" in prompt
    assert "Calibrated Certainty" in prompt


def test_custom_system_instructions():
    custom_sys = "Custom system instructions for test."
    builder = PromptBuilder(system_prompt=custom_sys)
    prompt = builder.build_prompt(query="Test query", context="Context")
    assert "Custom system instructions for test." in prompt


def test_build_messages_format():
    messages = build_messages(
        query="Motor vibration high",
        context="Knowledge Source 1: Vibration info"
    )
    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "Industrial IoT Fault Diagnosis Assistant" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "Motor vibration high" in messages[1]["content"]
    assert "Vibration info" in messages[1]["content"]
