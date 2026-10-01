"""
Exceptions for P11 RAG + LLM Integration Layer.
"""


class IntegrationError(Exception):
    """Base exception for all P11 integration errors."""
    pass


class PipelineConfigError(IntegrationError, ValueError):
    """Raised when pipeline configuration or parameters fail validation."""
    pass


class QueryValidationError(IntegrationError, ValueError):
    """Raised when user/telemetry query is empty, whitespace, or invalid type."""
    pass


class RetrievalError(IntegrationError):
    """Raised when P9 RAG retrieval fails."""
    pass


class GenerationError(IntegrationError):
    """Raised when P10 Local LLM generation fails."""
    pass
