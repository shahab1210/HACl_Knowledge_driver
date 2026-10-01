"""
P10 Local LLM / Ollama Generation Layer Package
"""

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

from config import (
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_TIMEOUT,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    DEFAULT_TOP_K,
    DEFAULT_SYSTEM_PROMPT,
    KNOWN_EMBEDDING_MODELS,
    LLMConfig,
)

from prompt_builder import (
    PromptBuilder,
    build_prompt,
    build_messages,
)

from client import (
    LocalLLMClient,
)

from llm_pipeline import (
    LLMPipeline,
)

__all__ = [
    # Core Classes
    "LocalLLMClient",
    "PromptBuilder",
    "LLMPipeline",
    "LLMConfig",
    # Data Models
    "GenerationOptions",
    "GenerationResponse",
    "LLMPipelineOutput",
    # Functions
    "build_prompt",
    "build_messages",
    # Constants
    "DEFAULT_OLLAMA_BASE_URL",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TOP_P",
    "DEFAULT_TOP_K",
    "DEFAULT_SYSTEM_PROMPT",
    "KNOWN_EMBEDDING_MODELS",
    # Exceptions
    "LLMError",
    "OllamaConnectionError",
    "OllamaModelNotFoundError",
    "OllamaModelTypeError",
    "OllamaResponseError",
    "LLMValidationError",
]
