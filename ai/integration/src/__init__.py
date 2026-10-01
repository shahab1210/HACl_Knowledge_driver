"""
P11 RAG + LLM Integration Layer Package
"""

from exceptions import (
    IntegrationError,
    PipelineConfigError,
    QueryValidationError,
    RetrievalError,
    GenerationError,
)

from models import (
    SourceEvidence,
    RetrievalEvidence,
    DiagnosisResponse,
)

from config import (
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_TOP_K,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    PipelineConfig,
)

from pipeline import (
    RAGLLMPipeline,
)

__all__ = [
    # Core Pipeline
    "RAGLLMPipeline",
    # Data Models
    "SourceEvidence",
    "RetrievalEvidence",
    "DiagnosisResponse",
    # Configuration
    "PipelineConfig",
    "DEFAULT_OLLAMA_BASE_URL",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_TOP_K",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TIMEOUT",
    # Exceptions
    "IntegrationError",
    "PipelineConfigError",
    "QueryValidationError",
    "RetrievalError",
    "GenerationError",
]
