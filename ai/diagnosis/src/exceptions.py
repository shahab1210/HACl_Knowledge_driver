"""
Exceptions for P12 Diagnosis Engine Layer.
"""


class DiagnosisEngineError(Exception):
    """Base exception for all P12 diagnosis engine errors."""
    pass


class DiagnosisInputError(DiagnosisEngineError, ValueError):
    """Raised when input provided to the diagnosis engine or parser is invalid."""
    pass


class DiagnosisValidationError(DiagnosisEngineError, ValueError):
    """Raised when structured diagnosis data fails schema or integrity validation."""
    pass


class DiagnosisParsingError(DiagnosisEngineError):
    """Raised when raw LLM response or retrieval evidence cannot be parsed."""
    pass
