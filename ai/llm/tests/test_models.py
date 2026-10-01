"""
Unit tests for P10 LLM data models and exception hierarchies.
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models import (
    GenerationOptions,
    GenerationResponse,
    LLMPipelineOutput,
    LLMError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaModelTypeError,
    OllamaResponseError,
    LLMValidationError,
)


def test_generation_options_defaults():
    opts = GenerationOptions()
    assert opts.temperature == 0.2
    assert opts.top_p == 0.9
    assert opts.top_k == 40
    assert opts.num_predict == 1024
    ollama_dict = opts.to_ollama_options()
    assert ollama_dict["temperature"] == 0.2
    assert ollama_dict["top_p"] == 0.9
    assert ollama_dict["top_k"] == 40
    assert ollama_dict["num_predict"] == 1024


def test_generation_options_validation():
    with pytest.raises(LLMValidationError):
        GenerationOptions(temperature=2.5)

    with pytest.raises(LLMValidationError):
        GenerationOptions(temperature=-0.1)

    with pytest.raises(LLMValidationError):
        GenerationOptions(top_p=0.0)

    with pytest.raises(LLMValidationError):
        GenerationOptions(top_p=1.5)

    with pytest.raises(LLMValidationError):
        GenerationOptions(num_predict=0)


def test_generation_options_from_dict():
    data = {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.95,
        "top_k": 50,
        "stop": ["END"]
    }
    opts = GenerationOptions.from_dict(data)
    assert opts.temperature == 0.7
    assert opts.num_predict == 2048
    assert opts.top_p == 0.95
    assert opts.top_k == 50
    assert opts.stop == ["END"]


def test_generation_response_from_ollama_generate():
    data = {
        "model": "llama3.2:3b",
        "response": "Motor bearing is overheated.",
        "done": True,
        "total_duration": 1200000000,
        "prompt_eval_count": 45,
        "eval_count": 20
    }
    resp = GenerationResponse.from_ollama_response(data, prompt="Diagnose motor")
    assert resp.text == "Motor bearing is overheated."
    assert resp.model == "llama3.2:3b"
    assert resp.total_duration == 1200000000
    assert resp.done is True

    serialized = resp.to_dict()
    assert serialized["text"] == "Motor bearing is overheated."
    assert serialized["model"] == "llama3.2:3b"


def test_generation_response_from_ollama_chat():
    data = {
        "model": "llama3.2:3b",
        "message": {"role": "assistant", "content": "Check lubrication."},
        "done": True
    }
    resp = GenerationResponse.from_ollama_response(data, prompt="Check")
    assert resp.text == "Check lubrication."
    assert resp.model == "llama3.2:3b"


def test_generation_response_raises_on_ollama_error_field():
    data = {"error": "CUDA out of memory"}
    with pytest.raises(OllamaResponseError) as exc:
        GenerationResponse.from_ollama_response(data, prompt="test")
    assert "CUDA out of memory" in str(exc.value)


def test_generation_response_raises_on_non_dict():
    with pytest.raises(OllamaResponseError):
        GenerationResponse.from_ollama_response("not a dict", prompt="test")


def test_pipeline_output_to_dict():
    output = LLMPipelineOutput(
        query="Motor vibration",
        context="Context info",
        prompt="Prompt info",
        response="Response diagnosis",
        model="llama3.2:3b",
        result_count=3,
        generation_details={"eval_count": 50}
    )
    d = output.to_dict()
    assert d["query"] == "Motor vibration"
    assert d["result_count"] == 3
    assert d["generation_details"]["eval_count"] == 50


def test_exception_inheritance():
    assert issubclass(OllamaConnectionError, LLMError)
    assert issubclass(OllamaModelNotFoundError, LLMError)
    assert issubclass(OllamaModelTypeError, LLMError)
    assert issubclass(OllamaResponseError, LLMError)
    assert issubclass(LLMValidationError, LLMError)
    assert issubclass(LLMValidationError, ValueError)
