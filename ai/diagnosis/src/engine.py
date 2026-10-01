"""
P12 Diagnosis Engine - Orchestrator

Integrates the P11 RAG+LLM layer with the DiagnosisParser and DiagnosisValidator
to produce standardized, machine-readable StructuredDiagnosis outputs.

Architecture:
Query
  ↓
P11 RAG + LLM Integration Layer
  ↓
DiagnosisResponse (RAG Evidence + LLM Text)
  ↓
P12 DiagnosisParser
  ↓
P12 DiagnosisValidator
  ↓
StructuredDiagnosis (Final Standardized Domain Model)
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union

from models import StructuredDiagnosis
from parser import DiagnosisParser
from validator import DiagnosisValidator
from exceptions import DiagnosisInputError, DiagnosisEngineError
from loader import load_p11_pipeline


class DiagnosisEngine:
    """
    High-level industrial IoT diagnosis engine that transforms unstructured
    LLM reasoning and retrieval evidence into structured, validated domain diagnoses.
    """

    def __init__(
        self,
        pipeline: Optional[Any] = None,
        parser: Optional[DiagnosisParser] = None,
        validator: Optional[DiagnosisValidator] = None,
        top_k: int = 3,
        model: Optional[str] = None,
        embedding_model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ):
        self.parser = parser or DiagnosisParser()
        self.validator = validator or DiagnosisValidator()

        if pipeline is not None:
            self.pipeline = pipeline
        else:
            self.pipeline = load_p11_pipeline(
                top_k=top_k,
                model=model,
                embedding_model=embedding_model,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

    def analyze(self, p11_result: Any) -> StructuredDiagnosis:
        """
        Parse and validate an existing P11 DiagnosisResponse into StructuredDiagnosis.
        """
        if p11_result is None:
            raise DiagnosisInputError("Cannot analyze None input.")

        try:
            diagnosis = self.parser.parse(p11_result)
        except Exception as e:
            if isinstance(e, DiagnosisInputError):
                raise
            raise DiagnosisEngineError(f"Diagnosis parsing failed: {e}") from e

        # Validate the resulting structured diagnosis
        self.validator.validate(diagnosis)
        return diagnosis

    def diagnose(
        self,
        query: str,
        top_k: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> StructuredDiagnosis:
        """
        Execute end-to-end diagnosis from a raw query: P11 RAG+LLM -> P12 structuring & validation.
        """
        if not query or not str(query).strip():
            raise DiagnosisInputError("Diagnosis query cannot be empty or whitespace only.")

        try:
            p11_output = self.pipeline.run(
                query=query.strip(),
                top_k=top_k,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            raise DiagnosisEngineError(f"P11 pipeline execution failed: {e}") from e

        return self.analyze(p11_output)
