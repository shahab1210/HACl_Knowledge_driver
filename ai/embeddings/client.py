"""
Dedicated Ollama client for P7 Embedding Generation.
Handles server availability checks, model discovery, embedding generation
(supporting both /api/embed and legacy /api/embeddings endpoints), batching, and error handling.
"""

import os
import json
from typing import List, Dict, Any, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error


class OllamaClientError(Exception):
    """Base exception for all Ollama client errors."""
    pass


class OllamaConnectionError(OllamaClientError):
    """Raised when Ollama server cannot be reached."""
    pass


class OllamaModelNotFoundError(OllamaClientError):
    """Raised when the specified embedding model is not installed on Ollama."""
    pass


class OllamaResponseError(OllamaClientError):
    """Raised when Ollama returns an unexpected or malformed response."""
    pass


class OllamaClient:
    """
    HTTP client for local Ollama embedding services.
    Configurable via parameters or environment variables (OLLAMA_BASE_URL, EMBEDDING_MODEL).
    """

    DEFAULT_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL = "nomic-embed-text"

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
        session: Optional[Any] = None
    ):
        raw_url = base_url or os.getenv("OLLAMA_BASE_URL") or self.DEFAULT_BASE_URL
        self.base_url = raw_url.rstrip("/")
        self.model = model or os.getenv("EMBEDDING_MODEL") or self.DEFAULT_MODEL
        self.timeout = float(timeout)
        self.session = session if session is not None else (requests.Session() if HAS_REQUESTS else None)

    def _http_get(self, path: str) -> Dict[str, Any]:
        """Perform an HTTP GET request to the Ollama server."""
        url = f"{self.base_url}{path}"
        if HAS_REQUESTS:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code != 200:
                    raise OllamaResponseError(f"GET {path} returned HTTP {resp.status_code}: {resp.text}")
                return resp.json()
            except requests.exceptions.ConnectionError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama at {self.base_url}: {e}") from e
            except requests.exceptions.Timeout as e:
                raise OllamaConnectionError(f"Timeout connecting to Ollama at {self.base_url}: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON from {path}: {e}") from e
        else:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise OllamaResponseError(f"GET {path} returned HTTP {response.status}")
                    raw_data = response.read().decode("utf-8")
                    return json.loads(raw_data)
            except urllib.error.URLError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama at {self.base_url}: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON from {path}: {e}") from e

    def _http_post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform an HTTP POST request to the Ollama server."""
        url = f"{self.base_url}{path}"
        if HAS_REQUESTS:
            try:
                resp = self.session.post(url, json=payload, timeout=self.timeout)
                if resp.status_code != 200:
                    raise OllamaResponseError(f"POST {path} returned HTTP {resp.status_code}: {resp.text}")
                return resp.json()
            except requests.exceptions.ConnectionError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama at {self.base_url}: {e}") from e
            except requests.exceptions.Timeout as e:
                raise OllamaConnectionError(f"Timeout connecting to Ollama at {self.base_url}: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON from {path}: {e}") from e
        else:
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=json_bytes,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise OllamaResponseError(f"POST {path} returned HTTP {response.status}")
                    raw_data = response.read().decode("utf-8")
                    return json.loads(raw_data)
            except urllib.error.URLError as e:
                raise OllamaConnectionError(f"Could not connect to Ollama at {self.base_url}: {e}") from e
            except json.JSONDecodeError as e:
                raise OllamaResponseError(f"Malformed JSON from {path}: {e}") from e

    def is_server_running(self) -> bool:
        """Check whether the Ollama server is running and reachable."""
        try:
            # Check version or tags
            data = self._http_get("/api/version")
            return "version" in data
        except Exception:
            try:
                data = self._http_get("/api/tags")
                return "models" in data
            except Exception:
                return False

    def list_models(self) -> List[str]:
        """Fetch list of model names currently pulled and available in Ollama."""
        data = self._http_get("/api/tags")
        models = data.get("models", [])
        return [m.get("name", "") for m in models if isinstance(m, dict) and "name" in m]

    def is_model_available(self, model_name: Optional[str] = None) -> bool:
        """
        Check whether the target model (or default model) is available in Ollama.
        Matches exact tag or base name (e.g. 'nomic-embed-text' matches 'nomic-embed-text:latest').
        """
        target = (model_name or self.model).lower()
        available = self.list_models()
        for m in available:
            m_lower = m.lower()
            if m_lower == target or m_lower.startswith(f"{target}:") or target.startswith(f"{m_lower.split(':')[0]}:"):
                return True
        return False

    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a single string.
        Attempts new /api/embed endpoint first, falling back to legacy /api/embeddings.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty or whitespace-only text.")

        # Try /api/embed first (Ollama modern API)
        try:
            payload = {"model": self.model, "input": text}
            data = self._http_post("/api/embed", payload)
            embeddings = data.get("embeddings")
            if embeddings and isinstance(embeddings, list) and len(embeddings) > 0:
                vector = embeddings[0]
                if isinstance(vector, list) and len(vector) > 0:
                    return [float(x) for x in vector]
            raise OllamaResponseError(f"/api/embed response missing valid 'embeddings' list: {data}")
        except OllamaResponseError as err:
            # If 404 or unsupported, attempt legacy /api/embeddings
            if "HTTP 404" in str(err):
                return self._embed_legacy(text)
            raise

    def _embed_legacy(self, text: str) -> List[float]:
        """Fallback to legacy /api/embeddings endpoint."""
        payload = {"model": self.model, "prompt": text}
        data = self._http_post("/api/embeddings", payload)
        vector = data.get("embedding")
        if vector and isinstance(vector, list) and len(vector) > 0:
            return [float(x) for x in vector]
        raise OllamaResponseError(f"/api/embeddings response missing valid 'embedding' list: {data}")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for a batch of strings.
        Attempts batch request to /api/embed; falls back to sequential calls if needed.
        """
        if not texts:
            return []

        # Validate non-empty
        for idx, t in enumerate(texts):
            if not t or not t.strip():
                raise ValueError(f"Batch item at index {idx} is empty or whitespace-only.")

        # Attempt batch call via /api/embed
        try:
            payload = {"model": self.model, "input": texts}
            data = self._http_post("/api/embed", payload)
            embeddings = data.get("embeddings")
            if embeddings and isinstance(embeddings, list) and len(embeddings) == len(texts):
                return [[float(x) for x in vec] for vec in embeddings]
        except Exception:
            # Fall back to sequential processing
            pass

        results: List[List[float]] = []
        for t in texts:
            results.append(self.embed_text(t))
        return results
