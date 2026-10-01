"""
P12 Diagnosis Engine - Structured Diagnosis Validator

Validates schema correctness, confidence constraints, fault references,
and knowledge source integrity for StructuredDiagnosis instances.
"""

from typing import Any
from models import (
    StructuredDiagnosis,
    FaultReference,
    ConfidenceInfo,
    TelemetryEvidence,
    KnowledgeSourceInfo,
    VALID_CONFIDENCE_LEVELS,
)
from exceptions import DiagnosisValidationError


class DiagnosisValidator:
    """
    Validates the structural integrity and semantic consistency of StructuredDiagnosis objects.
    """

    def validate(self, diagnosis: Any) -> bool:
        """
        Validate a StructuredDiagnosis object. Raises DiagnosisValidationError on failure.
        """
        if not isinstance(diagnosis, StructuredDiagnosis):
            raise DiagnosisValidationError(
                f"Expected StructuredDiagnosis object, got {type(diagnosis).__name__}"
            )

        # 1. Validate Query
        if not diagnosis.query or not diagnosis.query.strip():
            raise DiagnosisValidationError("Diagnosis query cannot be empty or whitespace only.")

        # 2. Validate Confidence
        if not isinstance(diagnosis.confidence, ConfidenceInfo):
            raise DiagnosisValidationError("diagnosis.confidence must be a ConfidenceInfo object.")

        if diagnosis.confidence.level not in VALID_CONFIDENCE_LEVELS:
            raise DiagnosisValidationError(
                f"Invalid confidence level '{diagnosis.confidence.level}'. "
                f"Allowed levels: {sorted(list(VALID_CONFIDENCE_LEVELS))}"
            )

        # 3. Validate Primary Fault (if present)
        if diagnosis.primary_fault is not None:
            if not isinstance(diagnosis.primary_fault, FaultReference):
                raise DiagnosisValidationError("primary_fault must be a FaultReference instance or None.")
            if not diagnosis.primary_fault.fault_id or not diagnosis.primary_fault.fault_id.strip():
                raise DiagnosisValidationError("primary_fault.fault_id cannot be empty.")
            if not diagnosis.primary_fault.title or not diagnosis.primary_fault.title.strip():
                raise DiagnosisValidationError("primary_fault.title cannot be empty.")

        # 4. Validate Alternative Faults
        if not isinstance(diagnosis.alternative_faults, list):
            raise DiagnosisValidationError("alternative_faults must be a list.")

        for idx, alt in enumerate(diagnosis.alternative_faults):
            if not isinstance(alt, FaultReference):
                raise DiagnosisValidationError(
                    f"alternative_faults[{idx}] must be a FaultReference instance, got {type(alt).__name__}."
                )
            if not alt.fault_id or not alt.fault_id.strip():
                raise DiagnosisValidationError(f"alternative_faults[{idx}].fault_id cannot be empty.")
            if not alt.title or not alt.title.strip():
                raise DiagnosisValidationError(f"alternative_faults[{idx}].title cannot be empty.")

        # 5. Validate Knowledge Sources
        if not isinstance(diagnosis.knowledge_sources, list):
            raise DiagnosisValidationError("knowledge_sources must be a list.")

        for idx, ks in enumerate(diagnosis.knowledge_sources):
            if not isinstance(ks, KnowledgeSourceInfo):
                raise DiagnosisValidationError(
                    f"knowledge_sources[{idx}] must be a KnowledgeSourceInfo instance, got {type(ks).__name__}."
                )
            if not ks.document_id:
                raise DiagnosisValidationError(f"knowledge_sources[{idx}].document_id cannot be empty.")
            if not 0.0 <= ks.similarity <= 1.0:
                raise DiagnosisValidationError(
                    f"knowledge_sources[{idx}].similarity ({ks.similarity}) must be in range [0.0, 1.0]."
                )

        # 6. Validate Telemetry Evidence
        if not isinstance(diagnosis.evidence, list):
            raise DiagnosisValidationError("evidence must be a list.")

        for idx, ev in enumerate(diagnosis.evidence):
            if not isinstance(ev, TelemetryEvidence):
                raise DiagnosisValidationError(
                    f"evidence[{idx}] must be a TelemetryEvidence instance, got {type(ev).__name__}."
                )
            if not ev.parameter or not ev.parameter.strip():
                raise DiagnosisValidationError(f"evidence[{idx}].parameter cannot be empty.")

        return True


# Convenience functional interface
_default_validator = DiagnosisValidator()


def validate_diagnosis(diagnosis: StructuredDiagnosis) -> bool:
    """Helper function to validate a StructuredDiagnosis object."""
    return _default_validator.validate(diagnosis)
