"""
Data models and exceptions for the P10 Local LLM Generation Layer.

Defines generation options, response structures, pipeline outputs,
and specialized exception classes for local Ollama LLM interactions.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


# =====================================================================
# Exception Hierarchy
# =====================================================================

class LLMError(Exception):
    """Base exception for all P10 Local LLM errors."""
    pass


class OllamaConnectionError(LLMError):
    """Raised when the Ollama HTTP server cannot be reached or times out."""
    pass


class OllamaModelNotFoundError(LLMError):
    """Raised when the requested generative LLM model is not installed in Ollama."""
    pass


class OllamaModelTypeError(LLMError):
    """Raised when an embedding-only model (e.g., nomic-embed-text) is used for generation."""
    pass


class OllamaResponseError(LLMError):
    """Raised when Ollama returns an error code, error message, or malformed response."""
    pass


class LLMValidationError(LLMError, ValueError):
    """Raised when input parameters (query, prompt, options) fail validation."""
    pass


# =====================================================================
# Generation Options & Payloads
# =====================================================================

@dataclass
class GenerationOptions:
    """
    Tunable generation parameters for Ollama LLM inference.
    """
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 40
    num_predict: int = 1024
    stop: Optional[List[str]] = None
    seed: Optional[int] = None

    def __post_init__(self):
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise LLMValidationError(f"Temperature must be between 0.0 and 2.0, got {self.temperature}")
        if self.top_p <= 0.0 or self.top_p > 1.0:
            raise LLMValidationError(f"Top-p must be in (0.0, 1.0], got {self.top_p}")
        if self.num_predict <= 0:
            raise LLMValidationError(f"num_predict must be positive, got {self.num_predict}")

    def to_ollama_options(self) -> Dict[str, Any]:
        """Convert to the dictionary format expected in Ollama's 'options' field."""
        opts: Dict[str, Any] = {
            "temperature": float(self.temperature),
            "top_p": float(self.top_p),
            "top_k": int(self.top_k),
            "num_predict": int(self.num_predict),
        }
        if self.stop is not None:
            opts["stop"] = self.stop
        if self.seed is not None:
            opts["seed"] = int(self.seed)
        return opts

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationOptions":
        """Instantiate from a dictionary."""
        valid_keys = {"temperature", "top_p", "top_k", "num_predict", "max_tokens", "stop", "seed"}
        filtered = {}
        for k, v in data.items():
            if k == "max_tokens":
                filtered["num_predict"] = v
            elif k in valid_keys:
                filtered[k] = v
        return cls(**filtered)


@dataclass
class GenerationResponse:
    """
    Standardized response from the Local LLM client.
    """
    text: str
    model: str
    prompt: str
    total_duration: Optional[int] = None  # nanoseconds
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    done: bool = True
    created_at: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

    @classmethod
    def from_ollama_response(
        cls,
        data: Dict[str, Any],
        prompt: str,
        fallback_model: str = ""
    ) -> "GenerationResponse":
        """
        Parse Ollama /api/generate or /api/chat response JSON.
        """
        if not isinstance(data, dict):
            raise OllamaResponseError(f"Expected dict response from Ollama, got {type(data).__name__}")

        # Check for error field
        if "error" in data:
            raise OllamaResponseError(f"Ollama returned error: {data['error']}")

        # /api/generate returns 'response', /api/chat returns message.content
        text = ""
        if "response" in data:
            text = str(data.get("response", "")).strip()
        elif "message" in data and isinstance(data["message"], dict):
            text = str(data["message"].get("content", "")).strip()

        model_name = str(data.get("model", fallback_model))

        return cls(
            text=text,
            model=model_name,
            prompt=prompt,
            total_duration=data.get("total_duration"),
            load_duration=data.get("load_duration"),
            prompt_eval_count=data.get("prompt_eval_count"),
            eval_count=data.get("eval_count"),
            eval_duration=data.get("eval_duration"),
            done=bool(data.get("done", True)),
            created_at=data.get("created_at"),
            raw_response=data
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize response to a dictionary."""
        return {
            "text": self.text,
            "model": self.model,
            "prompt": self.prompt,
            "total_duration": self.total_duration,
            "load_duration": self.load_duration,
            "prompt_eval_count": self.prompt_eval_count,
            "eval_count": self.eval_count,
            "eval_duration": self.eval_duration,
            "done": self.done,
            "created_at": self.created_at,
        }


@dataclass
class LLMPipelineOutput:
    """
    Structured output returned by the P10 LLMPipeline.
    """
    query: str
    context: str
    prompt: str
    response: str
    model: str
    result_count: int = 0
    generation_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize output to a dictionary."""
        return {
            "query": self.query,
            "context": self.context,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "result_count": self.result_count,
            "generation_details": self.generation_details
        }
