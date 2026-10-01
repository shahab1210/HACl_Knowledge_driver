"""
P10 Local LLM - Ollama Client

Local HTTP client for Ollama LLM inference.
Provides direct communication with local Ollama service (/api/generate, /api/chat, /api/tags),
robust error handling, parameter management, model readiness verification, and no cloud dependencies.
"""

import os
import json
from typing import List, Dict, Any, Optional, Union

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

from config import (
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_TIMEOUT,
    KNOWN_EMBEDDING_MODELS,
)
from models import (
    GenerationOptions,
    GenerationResponse,
    LLMError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaModelTypeError,
    OllamaResponseError,
    LLMValidationError,
)


class LocalLLMClient:
    """
    Reusable HTTP client for interacting with local Ollama generative LLM service.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        default_options: Optional[Union[GenerationOptions, Dict[str, Any]]] = None,
        session: Optional[Any] = None
    ):
        raw_url = base_url or os.getenv("OLLAMA_BASE_URL") or os.getenv("LLM_BASE_URL") or DEFAULT_OLLAMA_BASE_URL
        self.base_url = raw_url.rstrip("/")
        self.model = model or os.getenv("LLM_MODEL") or os.getenv("OLLAMA_MODEL") or DEFAULT_LLM_MODEL
        self.timeout = float(timeout if timeout is not None else os.getenv("LLM_TIMEOUT", DEFAULT_TIMEOUT))

        if default_options is None:
            self.default_options = GenerationOptions()
        elif isinstance(default_options, dict):
            self.default_options = GenerationOptions.from_dict(default_options)
        elif isinstance(default_options, GenerationOptions):
            self.default_options = default_options
        else:
            raise LLMValidationError(f"Invalid default_options type: {type(default_options).__name__}")

        self.session = session if session is not None else (requests.Session() if HAS_REQUESTS else None)

    # -----------------------------------------------------------------
    # HTTP Transport Helpers
    # -----------------------------------------------------------------

    def _http_get(self, path: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Perform an HTTP GET request against the Ollama server."""
        url = f"{self.base_url}{path}"
        req_timeout = timeout if timeout is not None else self.timeout

        if HAS_REQUESTS:
            try:
                resp = self.session.get(url, timeout=req_timeout)
                if resp.status_code != 200:
                    raise OllamaResponseError(f"GET {path} failed with HTTP {resp.status_code}: {resp.text}")
                return resp.json()
            except requests.exceptions.ConnectionError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama server at {self.base_url}: {e}") from e
            except requests.exceptions.Timeout as e:
                raise OllamaConnectionError(f"Timeout connecting to Ollama server at {self.base_url} after {req_timeout}s: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON returned from {path}: {e}") from e
        else:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=req_timeout) as response:
                    if response.status != 200:
                        raise OllamaResponseError(f"GET {path} returned HTTP {response.status}")
                    raw = response.read().decode("utf-8")
                    return json.loads(raw)
            except urllib.error.URLError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama server at {self.base_url}: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON returned from {path}: {e}") from e

    def _http_post(self, path: str, payload: Dict[str, Any], timeout: Optional[float] = None) -> Dict[str, Any]:
        """Perform an HTTP POST request against the Ollama server."""
        url = f"{self.base_url}{path}"
        req_timeout = timeout if timeout is not None else self.timeout

        if HAS_REQUESTS:
            try:
                resp = self.session.post(url, json=payload, timeout=req_timeout)
                if resp.status_code != 200:
                    error_body = resp.text
                    if resp.status_code == 404 and "not found" in error_body.lower():
                        target_model = payload.get("model", self.model)
                        raise OllamaModelNotFoundError(
                            f"Model '{target_model}' not found in Ollama. "
                            f"Run 'ollama pull {target_model}' to install it."
                        )
                    raise OllamaResponseError(f"POST {path} failed with HTTP {resp.status_code}: {error_body}")
                return resp.json()
            except requests.exceptions.ConnectionError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama server at {self.base_url}: {e}") from e
            except requests.exceptions.Timeout as e:
                raise OllamaConnectionError(f"Timeout during LLM generation after {req_timeout}s: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON returned from {path}: {e}") from e
        else:
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=json_bytes,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=req_timeout) as response:
                    if response.status != 200:
                        raise OllamaResponseError(f"POST {path} returned HTTP {response.status}")
                    raw = response.read().decode("utf-8")
                    return json.loads(raw)
            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8") if e.fp else str(e)
                if e.code == 404 and "not found" in error_body.lower():
                    target_model = payload.get("model", self.model)
                    raise OllamaModelNotFoundError(
                        f"Model '{target_model}' not found in Ollama. "
                        f"Run 'ollama pull {target_model}' to install it."
                    )
                raise OllamaResponseError(f"POST {path} failed with HTTP {e.code}: {error_body}") from e
            except urllib.error.URLError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama server at {self.base_url}: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON returned from {path}: {e}") from e

    # -----------------------------------------------------------------
    # Server & Model Discovery
    # -----------------------------------------------------------------

    def is_server_running(self) -> bool:
        """Check whether the local Ollama server is active and reachable."""
        try:
            data = self._http_get("/api/version", timeout=3.0)
            return "version" in data
        except Exception:
            try:
                data = self._http_get("/api/tags", timeout=3.0)
                return "models" in data
            except Exception:
                return False

    def list_models_detailed(self) -> List[Dict[str, Any]]:
        """Fetch list of all installed Ollama models with metadata."""
        data = self._http_get("/api/tags")
        return data.get("models", [])

    def list_models(self) -> List[str]:
        """Fetch simple list of model names currently available in Ollama."""
        models = self.list_models_detailed()
        names = []
        for m in models:
            if isinstance(m, dict) and "name" in m:
                names.append(m["name"])
        return names

    def is_embedding_model(self, model_name: Optional[str] = None) -> bool:
        """
        Check whether a model is an embedding model (e.g., nomic-embed-text)
        rather than a generative LLM.
        """
        target = (model_name or self.model).lower().strip()
        base_name = target.split(":")[0]

        # Check known embedding prefixes
        for known in KNOWN_EMBEDDING_MODELS:
            if known in base_name or base_name in known:
                return True

        # Check capabilities from Ollama /api/tags if available
        try:
            detailed = self.list_models_detailed()
            for m in detailed:
                m_name = m.get("name", "").lower()
                if m_name == target or m_name.startswith(f"{base_name}:") or target.startswith(f"{m_name.split(':')[0]}:"):
                    caps = m.get("capabilities", [])
                    if caps == ["embedding"] or ("embedding" in caps and "completion" not in caps and "chat" not in caps):
                        return True
        except Exception:
            pass

        return False

    def is_model_available(self, model_name: Optional[str] = None) -> bool:
        """
        Check whether the target model is installed in Ollama.
        Matches exact tag or base name (e.g. 'llama3.2:3b' matches 'llama3.2:3b' or 'llama3.2:3b-instruct').
        """
        target = (model_name or self.model).lower().strip()
        target_base = target.split(":")[0]

        try:
            available = self.list_models()
        except OllamaConnectionError:
            return False

        for m in available:
            m_lower = m.lower()
            m_base = m_lower.split(":")[0]
            if m_lower == target or (m_base == target_base and ":" in target and ":" in m_lower and target.split(":")[1] == m_lower.split(":")[1]) or (m_base == target and ":" not in target):
                return True
            if m_lower.startswith(f"{target}:") or target.startswith(f"{m_base}:"):
                return True
        return False

    def validate_model_readiness(self, model_name: Optional[str] = None) -> None:
        """
        Verify that:
        1. Ollama server is running.
        2. Target model is NOT an embedding model.
        3. Target model is installed.
        Raises descriptive exceptions if any check fails.
        """
        target = model_name or self.model

        if not self.is_server_running():
            raise OllamaConnectionError(
                f"Ollama server is not reachable at {self.base_url}. "
                f"Please ensure Ollama is running (e.g. execute 'ollama serve' or open the Ollama app)."
            )

        if self.is_embedding_model(target):
            raise OllamaModelTypeError(
                f"Model '{target}' is an embedding model and cannot be used for text generation in P10. "
                f"Please use a generative model (e.g. 'llama3.2:3b', 'mistral:7b', 'phi3:mini')."
            )

        if not self.is_model_available(target):
            raise OllamaModelNotFoundError(
                f"Generative model '{target}' is not installed in local Ollama. "
                f"Run: 'ollama pull {target}' to download and install it."
            )

    # -----------------------------------------------------------------
    # Generation & Chat Inference
    # -----------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        options: Optional[Union[GenerationOptions, Dict[str, Any]]] = None,
        timeout: Optional[float] = None
    ) -> GenerationResponse:
        """
        Generate a completion for the given prompt using local Ollama /api/generate.
        """
        if prompt is None or not isinstance(prompt, str):
            raise LLMValidationError(f"Prompt must be a non-empty string, got {type(prompt).__name__}.")

        clean_prompt = prompt.strip()
        if not clean_prompt:
            raise LLMValidationError("Prompt cannot be empty or whitespace only.")

        target_model = model or self.model

        # Guard against using embedding models for generation
        if self.is_embedding_model(target_model):
            raise OllamaModelTypeError(
                f"Cannot generate text with embedding model '{target_model}'. "
                f"Use a generative model such as 'llama3.2:3b' instead."
            )

        # Resolve options
        if options is None:
            opts_obj = self.default_options
        elif isinstance(options, GenerationOptions):
            opts_obj = options
        elif isinstance(options, dict):
            opts_obj = GenerationOptions.from_dict(options)
        else:
            raise LLMValidationError(f"Invalid options type: {type(options).__name__}")

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": clean_prompt,
            "stream": False,
            "options": opts_obj.to_ollama_options()
        }

        if system:
            payload["system"] = system.strip()

        resp_data = self._http_post("/api/generate", payload, timeout=timeout)
        return GenerationResponse.from_ollama_response(resp_data, prompt=clean_prompt, fallback_model=target_model)

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        options: Optional[Union[GenerationOptions, Dict[str, Any]]] = None,
        timeout: Optional[float] = None
    ) -> GenerationResponse:
        """
        Generate a chat completion for a list of messages using local Ollama /api/chat.
        """
        if not messages or not isinstance(messages, list):
            raise LLMValidationError("Messages must be a non-empty list of message dictionaries.")

        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise LLMValidationError(f"Message at index {idx} must be a dict with 'role' and 'content' keys.")
            if not str(msg["content"]).strip():
                raise LLMValidationError(f"Message content at index {idx} cannot be empty or whitespace only.")

        target_model = model or self.model

        if self.is_embedding_model(target_model):
            raise OllamaModelTypeError(
                f"Cannot chat with embedding model '{target_model}'. "
                f"Use a generative model such as 'llama3.2:3b' instead."
            )

        if options is None:
            opts_obj = self.default_options
        elif isinstance(options, GenerationOptions):
            opts_obj = options
        elif isinstance(options, dict):
            opts_obj = GenerationOptions.from_dict(options)
        else:
            raise LLMValidationError(f"Invalid options type: {type(options).__name__}")

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": opts_obj.to_ollama_options()
        }

        resp_data = self._http_post("/api/chat", payload, timeout=timeout)
        user_prompt = messages[-1]["content"] if messages else ""
        return GenerationResponse.from_ollama_response(resp_data, prompt=user_prompt, fallback_model=target_model)
