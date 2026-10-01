"""
Unit tests for P10 LocalLLMClient with mocked HTTP interactions.
"""

import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import DEFAULT_LLM_MODEL
from client import LocalLLMClient
from models import (
    GenerationOptions,
    GenerationResponse,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaModelTypeError,
    OllamaResponseError,
    LLMValidationError,
)


def test_client_initialization_defaults():
    client = LocalLLMClient()
    assert client.base_url == "http://localhost:11434"
    assert client.model == DEFAULT_LLM_MODEL
    assert client.timeout == 120.0
    assert client.default_options.temperature == 0.2


def test_client_custom_initialization():
    opts = GenerationOptions(temperature=0.5, num_predict=512)
    client = LocalLLMClient(
        base_url="http://127.0.0.1:11434/",
        model="mistral:7b",
        timeout=45.0,
        default_options=opts
    )
    assert client.base_url == "http://127.0.0.1:11434"
    assert client.model == "mistral:7b"
    assert client.timeout == 45.0
    assert client.default_options.temperature == 0.5
    assert client.default_options.num_predict == 512


def test_empty_prompt_raises_validation_error():
    client = LocalLLMClient()
    with pytest.raises(LLMValidationError):
        client.generate("")


def test_whitespace_prompt_raises_validation_error():
    client = LocalLLMClient()
    with pytest.raises(LLMValidationError):
        client.generate("   \n\t  ")


def test_non_string_prompt_raises_validation_error():
    client = LocalLLMClient()
    with pytest.raises(LLMValidationError):
        client.generate(None)


def test_embedding_model_rejected_for_generation():
    client = LocalLLMClient(model="nomic-embed-text")
    with pytest.raises(OllamaModelTypeError) as exc:
        client.generate("Diagnose motor overheating")
    assert "embedding model" in str(exc.value)


def test_embedding_model_rejected_for_chat():
    client = LocalLLMClient(model="all-minilm")
    with pytest.raises(OllamaModelTypeError) as exc:
        client.chat([{"role": "user", "content": "Hello"}])
    assert "embedding model" in str(exc.value)


def test_generate_success_mocked():
    client = LocalLLMClient(model="llama3.2:3b")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "model": "llama3.2:3b",
        "response": "The motor is experiencing overheating due to bearing friction (FAULT-003).",
        "done": True,
        "total_duration": 1500000000,
        "load_duration": 200000000,
        "prompt_eval_count": 55,
        "eval_count": 30,
        "eval_duration": 1300000000,
        "created_at": "2026-10-01T00:00:00Z"
    }

    with patch.object(client.session, "post", return_value=mock_resp) as mock_post:
        result = client.generate(
            prompt="Diagnose motor overheating symptoms.",
            system="Be concise."
        )

        assert isinstance(result, GenerationResponse)
        assert "overheating" in result.text
        assert result.model == "llama3.2:3b"
        assert result.done is True
        assert result.eval_count == 30
        assert result.total_duration == 1500000000

        # Verify payload sent
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        payload = kwargs["json"]
        assert payload["model"] == "llama3.2:3b"
        assert payload["system"] == "Be concise."
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0.2


def test_chat_success_mocked():
    client = LocalLLMClient(model="llama3.2:3b")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "model": "llama3.2:3b",
        "message": {
            "role": "assistant",
            "content": "Check lubrication and bearing alignment."
        },
        "done": True
    }

    with patch.object(client.session, "post", return_value=mock_resp):
        messages = [
            {"role": "system", "content": "IoT Assistant"},
            {"role": "user", "content": "What to inspect?"}
        ]
        result = client.chat(messages=messages)
        assert result.text == "Check lubrication and bearing alignment."


def test_generate_handles_server_connection_error():
    client = LocalLLMClient()
    import requests
    with patch.object(client.session, "post", side_effect=requests.exceptions.ConnectionError("Connection refused")):
        with pytest.raises(OllamaConnectionError) as exc:
            client.generate("Test prompt")
        assert "Could not connect to Ollama server" in str(exc.value)


def test_generate_handles_server_timeout():
    client = LocalLLMClient()
    import requests
    with patch.object(client.session, "post", side_effect=requests.exceptions.Timeout("Read timed out")):
        with pytest.raises(OllamaConnectionError) as exc:
            client.generate("Test prompt")
        assert "Timeout during LLM generation" in str(exc.value)


def test_generate_handles_404_model_not_found():
    client = LocalLLMClient(model="nonexistent-model:latest")
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = '{"error": "model \'nonexistent-model:latest\' not found"}'

    with patch.object(client.session, "post", return_value=mock_resp):
        with pytest.raises(OllamaModelNotFoundError) as exc:
            client.generate("Test prompt")
        assert "not found in Ollama" in str(exc.value)
        assert "ollama pull nonexistent-model:latest" in str(exc.value)


def test_generate_handles_500_response_error():
    client = LocalLLMClient()
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = '{"error": "internal server error"}'

    with patch.object(client.session, "post", return_value=mock_resp):
        with pytest.raises(OllamaResponseError) as exc:
            client.generate("Test prompt")
        assert "POST /api/generate failed with HTTP 500" in str(exc.value)


def test_is_server_running():
    client = LocalLLMClient()

    # Success case
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"version": "0.5.4"}

    with patch.object(client.session, "get", return_value=mock_resp):
        assert client.is_server_running() is True

    # Failure case
    import requests
    with patch.object(client.session, "get", side_effect=requests.exceptions.ConnectionError()):
        assert client.is_server_running() is False


def test_list_models():
    client = LocalLLMClient()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [
            {"name": "nomic-embed-text:latest"},
            {"name": "llama3.2:3b"}
        ]
    }

    with patch.object(client.session, "get", return_value=mock_resp):
        models = client.list_models()
        assert "nomic-embed-text:latest" in models
        assert "llama3.2:3b" in models


def test_is_model_available():
    client = LocalLLMClient()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [
            {"name": "nomic-embed-text:latest"},
            {"name": "llama3.2:3b"}
        ]
    }

    with patch.object(client.session, "get", return_value=mock_resp):
        assert client.is_model_available("llama3.2:3b") is True
        assert client.is_model_available("llama3.2") is True
        assert client.is_model_available("mistral:7b") is False


def test_validate_model_readiness_valid():
    client = LocalLLMClient(model="llama3.2:3b")

    # Mock server running and model available
    version_resp = MagicMock(status_code=200)
    version_resp.json.return_value = {"version": "0.5.4"}

    tags_resp = MagicMock(status_code=200)
    tags_resp.json.return_value = {
        "models": [{"name": "llama3.2:3b", "capabilities": ["chat", "completion"]}]
    }

    def mock_get(url, **kwargs):
        if "/api/version" in url:
            return version_resp
        return tags_resp

    with patch.object(client.session, "get", side_effect=mock_get):
        # Should not raise
        client.validate_model_readiness()


def test_validate_model_readiness_raises_on_embedding_model():
    client = LocalLLMClient(model="nomic-embed-text")

    version_resp = MagicMock(status_code=200)
    version_resp.json.return_value = {"version": "0.5.4"}

    tags_resp = MagicMock(status_code=200)
    tags_resp.json.return_value = {
        "models": [{"name": "nomic-embed-text:latest", "capabilities": ["embedding"]}]
    }

    def mock_get(url, **kwargs):
        if "/api/version" in url:
            return version_resp
        return tags_resp

    with patch.object(client.session, "get", side_effect=mock_get):
        with pytest.raises(OllamaModelTypeError) as exc:
            client.validate_model_readiness()
        assert "embedding model" in str(exc.value)


def test_validate_model_readiness_raises_on_missing_model():
    client = LocalLLMClient(model="llama3.2:3b")

    version_resp = MagicMock(status_code=200)
    version_resp.json.return_value = {"version": "0.5.4"}

    tags_resp = MagicMock(status_code=200)
    tags_resp.json.return_value = {
        "models": [{"name": "nomic-embed-text:latest"}]
    }

    def mock_get(url, **kwargs):
        if "/api/version" in url:
            return version_resp
        return tags_resp

    with patch.object(client.session, "get", side_effect=mock_get):
        with pytest.raises(OllamaModelNotFoundError) as exc:
            client.validate_model_readiness()
        assert "ollama pull llama3.2:3b" in str(exc.value)
