"""
P12 Diagnosis Engine - Response Parser

Extracts structured diagnostic entities (primary/alternative faults,
telemetry evidence, confidence levels, possible causes, recommended checks,
and additional telemetry requirements) from P11 DiagnosisResponse and raw LLM text.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union

from models import (
    FaultReference,
    ConfidenceInfo,
    TelemetryEvidence,
    KnowledgeSourceInfo,
    StructuredDiagnosis,
)
from exceptions import DiagnosisInputError


class DiagnosisParser:
    """
    Parses P11 RAG+LLM response into a standardized StructuredDiagnosis model.
    """

    # Sensor keywords & extraction patterns
    TELEMETRY_PATTERNS = [
        # Temperature: 95°C, 95C, 95 deg C, 95 degrees C
        (
            "temperature",
            r"(?:temperature|temp)[^\d\n]*?(\d+(?:\.\d+)?)\s*(?:°\s*C|°C|deg\s*C|degrees?\s*C|C\b)",
            "°C"
        ),
        # Vibration: 7.2 mm/s, vibration is 7.2, vibration 7.2 mm/s
        (
            "vibration",
            r"(?:vibration(?: is| level| of)?\s*)(\d+(?:\.\d+)?)\s*(?:mm/s|m/s2)?",
            "mm/s"
        ),
        # Current: 25 A, current is 25A
        (
            "current",
            r"(?:current(?: is| of)?\s*)(\d+(?:\.\d+)?)\s*(?:A|amps|amperes)\b",
            "A"
        ),
        # Pressure: 4.5 bar, 60 psi
        (
            "pressure",
            r"(?:pressure(?: is| of)?\s*)(\d+(?:\.\d+)?)\s*(?:bar|psi|kPa)\b",
            "bar"
        ),
        # Humidity: 85%
        (
            "humidity",
            r"(?:humidity(?: is| of)?\s*)(\d+(?:\.\d+)?)\s*%",
            "%"
        ),
    ]

    INSUFFICIENT_CONTEXT_PHRASES = [
        "insufficient knowledge in context",
        "insufficient context",
        "insufficient sensor data",
        "insufficient evidence",
        "cannot be confirmed",
        "cannot conclusively confirm",
        "further sensor telemetry or physical inspection is required",
        "additional context is required",
        "no relevant knowledge was retrieved",
        "no valid knowledge content was retrieved",
    ]

    def parse(self, p11_input: Any) -> StructuredDiagnosis:
        """
        Main entry point to parse a P11 response (object or dict) into StructuredDiagnosis.
        """
        norm_data = self._normalize_input(p11_input)

        query = norm_data.get("query", "").strip()
        raw_llm_response = norm_data.get("diagnosis") or norm_data.get("response") or ""
        model = norm_data.get("model", "")
        gen_details = norm_data.get("generation_details", {})
        raw_retrieval = norm_data.get("retrieval", {})

        # Step 1: Parse authoritative knowledge sources from retrieval evidence
        sources = self._extract_knowledge_sources(raw_retrieval)

        # Step 2: Extract telemetry evidence from query
        evidence = self._extract_telemetry_evidence(query, raw_llm_response)

        # Step 3: Extract fault candidates from retrieval metadata & LLM text
        fault_candidates = self._extract_fault_candidates(sources, raw_llm_response)

        # Step 4: Parse sections from LLM text (causes, checks, additional info)
        possible_causes = self._extract_section_list(
            raw_llm_response,
            header_patterns=[r"###\s*4?\.\s*Possible Causes", r"###\s*Possible Causes", r"Possible Causes:", r"Root Causes:"]
        )
        recommended_checks = self._extract_section_list(
            raw_llm_response,
            header_patterns=[r"###\s*5?\.\s*Recommended Checks", r"###\s*Recommended Checks", r"Recommended Checks:", r"Recommended Actions:", r"Inspection Steps:"]
        )
        additional_info = self._extract_section_list(
            raw_llm_response,
            header_patterns=[r"###\s*6?\.\s*Additional Considerations", r"###\s*Additional Considerations", r"Insufficient Context:", r"Additional Information Required:", r"Additional Sensor Data:"]
        )

        # Step 5: Evaluate confidence and assign primary vs alternative faults
        is_insufficient = self._detect_insufficient_context(raw_llm_response, len(sources))
        primary_fault, alternative_faults, confidence = self._evaluate_diagnosis(
            fault_candidates,
            is_insufficient,
            raw_llm_response,
            sources
        )

        return StructuredDiagnosis(
            query=query,
            primary_fault=primary_fault,
            alternative_faults=alternative_faults,
            confidence=confidence,
            evidence=evidence,
            possible_causes=possible_causes,
            recommended_checks=recommended_checks,
            additional_information_required=additional_info,
            knowledge_sources=sources,
            raw_llm_response=raw_llm_response,
            model=model,
            generation_details=gen_details
        )

    def _normalize_input(self, p11_input: Any) -> Dict[str, Any]:
        """Convert DiagnosisResponse dataclass, object, or dict to normalized dict."""
        if p11_input is None:
            raise DiagnosisInputError("P11 input cannot be None.")

        if hasattr(p11_input, "to_dict") and callable(p11_input.to_dict):
            return p11_input.to_dict()

        if isinstance(p11_input, dict):
            return p11_input

        # Fallback for generic object
        data = {}
        for attr in ["query", "diagnosis", "response", "retrieval", "context", "prompt", "model", "generation_details"]:
            if hasattr(p11_input, attr):
                val = getattr(p11_input, attr)
                if hasattr(val, "to_dict") and callable(val.to_dict):
                    val = val.to_dict()
                data[attr] = val
        if data:
            return data

        raise DiagnosisInputError(f"Unsupported P11 input type: {type(p11_input).__name__}")

    def _extract_knowledge_sources(self, raw_retrieval: Union[Dict[str, Any], Any]) -> List[KnowledgeSourceInfo]:
        """Extract KnowledgeSourceInfo records from retrieval metadata."""
        if not raw_retrieval:
            return []

        sources_data = []
        if isinstance(raw_retrieval, dict):
            sources_data = raw_retrieval.get("sources", [])
        elif hasattr(raw_retrieval, "sources"):
            sources_data = getattr(raw_retrieval, "sources")

        knowledge_sources = []
        for s in sources_data:
            if hasattr(s, "to_dict") and callable(s.to_dict):
                s = s.to_dict()
            if isinstance(s, dict):
                knowledge_sources.append(KnowledgeSourceInfo.from_dict(s))

        return knowledge_sources

    def _extract_telemetry_evidence(self, query: str, raw_text: str) -> List[TelemetryEvidence]:
        """Extract observed telemetry values and units from the query text."""
        evidence_list: List[TelemetryEvidence] = []
        combined_text = f"{query}\n{raw_text[:300]}"

        for param, pattern, unit in self.TELEMETRY_PATTERNS:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                val_str = match.group(1)
                try:
                    val = float(val_str) if "." in val_str else int(val_str)
                except ValueError:
                    val = val_str

                status = None
                if param == "temperature" and "high" in query.lower():
                    status = "high"
                elif param == "vibration" and ("excessive" in query.lower() or "high" in query.lower()):
                    status = "excessive"

                evidence_list.append(TelemetryEvidence(
                    parameter=param,
                    type="telemetry",
                    value=val,
                    unit=unit,
                    status=status
                ))

        # Check qualitative symptoms if no numerical match was found
        if not any(e.parameter == "temperature" for e in evidence_list):
            if "temperature" in query.lower() or "overheating" in query.lower():
                evidence_list.append(TelemetryEvidence(
                    parameter="temperature",
                    type="telemetry",
                    value="high",
                    status="elevated"
                ))

        if not any(e.parameter == "vibration" for e in evidence_list):
            if "vibration" in query.lower() or "shaking" in query.lower():
                evidence_list.append(TelemetryEvidence(
                    parameter="vibration",
                    type="telemetry",
                    value="excessive",
                    status="abnormal"
                ))

        return evidence_list

    def _extract_fault_candidates(
        self,
        sources: List[KnowledgeSourceInfo],
        raw_text: str
    ) -> List[FaultReference]:
        """Extract unique fault candidates grounded in retrieved fault sources."""
        seen_fault_ids = set()
        candidates: List[FaultReference] = []

        # 1. Primary extraction from authoritative retrieved knowledge sources
        for s in sources:
            doc_id = s.document_id
            if doc_id.startswith("FAULT-") and doc_id not in seen_fault_ids:
                seen_fault_ids.add(doc_id)
                candidates.append(FaultReference(
                    fault_id=doc_id,
                    title=s.title,
                    document_type="fault",
                    similarity=s.similarity
                ))

        # 2. Supplementary scan in LLM text if no fault in retrieval
        if not candidates:
            fault_matches = re.findall(r"(FAULT-\d{3})", raw_text)
            for fid in fault_matches:
                if fid not in seen_fault_ids:
                    seen_fault_ids.add(fid)
                    candidates.append(FaultReference(
                        fault_id=fid,
                        title=f"Fault {fid}",
                        document_type="fault"
                    ))

        return candidates

    def _detect_insufficient_context(self, raw_text: str, source_count: int) -> bool:
        """Check whether the LLM or retrieval indicates insufficient context."""
        if source_count == 0:
            return True

        lower_text = raw_text.lower()
        for phrase in self.INSUFFICIENT_CONTEXT_PHRASES:
            if phrase in lower_text:
                return True
        return False

    def _evaluate_diagnosis(
        self,
        fault_candidates: List[FaultReference],
        is_insufficient: bool,
        raw_text: str,
        sources: List[KnowledgeSourceInfo]
    ) -> Tuple[Optional[FaultReference], List[FaultReference], ConfidenceInfo]:
        """Determine primary fault, alternative faults, and calibrated confidence level."""
        if not sources and not fault_candidates:
            return (
                None,
                [],
                ConfidenceInfo(
                    level="insufficient",
                    reason="No relevant fault knowledge was retrieved from the knowledge base."
                )
            )

        if not fault_candidates:
            return (
                None,
                [],
                ConfidenceInfo(
                    level="insufficient" if is_insufficient else "low",
                    reason="No specific FAULT document could be matched to the observed telemetry."
                )
            )

        # If multiple candidates exist
        if len(fault_candidates) > 1:
            primary = fault_candidates[0]
            alternatives = fault_candidates[1:]
            if is_insufficient:
                reason = "Multiple retrieved fault modes match the observed symptoms; physical inspection required to confirm."
                conf_level = "insufficient"
            else:
                reason = "Multiple retrieved fault modes match the observed symptoms."
                conf_level = "medium"
            return primary, alternatives, ConfidenceInfo(level=conf_level, reason=reason)

        # Single candidate
        single = fault_candidates[0]
        if is_insufficient:
            return (
                single,
                [],
                ConfidenceInfo(
                    level="insufficient",
                    reason="Partial evidence identified candidate fault, but context is insufficient to confirm root cause."
                )
            )

        sim = single.similarity or 0.0
        if sim >= 0.75:
            conf_level = "high"
            reason = f"Strong grounding match with {single.fault_id} ({single.title})."
        elif sim >= 0.60:
            conf_level = "medium"
            reason = f"Moderate similarity match with {single.fault_id} ({single.title})."
        else:
            conf_level = "low"
            reason = f"Low similarity match with {single.fault_id}."

        return single, [], ConfidenceInfo(level=conf_level, reason=reason)

    def _extract_section_list(self, text: str, header_patterns: List[str]) -> List[str]:
        """Extract bullet/numbered list items under specified markdown headers."""
        if not text:
            return []

        # Find starting point of the section
        start_idx = -1
        for pattern in header_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_idx = match.end()
                break

        if start_idx == -1:
            return []

        # Extract text from start_idx up to next major header (### or ##)
        remaining = text[start_idx:]
        next_header_match = re.search(r"\n#{2,3}\s+", remaining)
        section_content = remaining[:next_header_match.start()] if next_header_match else remaining

        items: List[str] = []
        for line in section_content.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Match bullet (*, -, +) or numbered list (1., 2.)
            cleaned = re.sub(r"^[-*+•]\s+", "", line)
            cleaned = re.sub(r"^\d+[\.\)]\s+", "", cleaned)
            # Remove bolding on leading prefixes if present, e.g. **Electrical Overload:** -> Electrical Overload:
            cleaned = re.sub(r"^\*\*(.+?)\*\*[:\s]*", r"\1: ", cleaned).strip()

            if len(cleaned) > 5 and not cleaned.startswith("#"):
                items.append(cleaned)

        return items
