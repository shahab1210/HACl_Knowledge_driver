"""
P10 Local LLM - Prompt Builder

Constructs controlled, grounded prompts for the Local LLM by combining
user/telemetry queries with retrieved RAG context and industrial IoT
diagnostic directives.
"""

from typing import Any, Dict, List, Optional, Union
from config import DEFAULT_SYSTEM_PROMPT
from models import LLMValidationError


class PromptBuilder:
    """
    Constructs prompts and message structures for local LLM generation.
    Enforces grounding, source citation, anti-hallucination, and uncertainty constraints.
    """

    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt.strip() if system_prompt and system_prompt.strip() else DEFAULT_SYSTEM_PROMPT

    def _normalize_context(self, context: Any) -> str:
        """
        Normalize various context formats (str, dict from P9 output, list of search results)
        into a consistent string representation.
        """
        if context is None:
            return "No relevant knowledge context was provided."

        if isinstance(context, str):
            clean_ctx = context.strip()
            return clean_ctx if clean_ctx else "No relevant knowledge context was provided."

        # Handle P9 RAG output dictionary (e.g. {"query": ..., "context": ..., "results": ...})
        if isinstance(context, dict):
            if "context" in context and isinstance(context["context"], str):
                clean_ctx = context["context"].strip()
                return clean_ctx if clean_ctx else "No relevant knowledge context was provided."
            elif "results" in context and isinstance(context["results"], list):
                return self._format_results_list(context["results"])
            else:
                return "No relevant knowledge context was provided."

        # Handle list of result dictionaries
        if isinstance(context, list):
            return self._format_results_list(context)

        return str(context).strip()

    def _format_results_list(self, results: List[Dict[str, Any]]) -> str:
        """Format a list of retrieval result dictionaries into context text."""
        if not results:
            return "No relevant knowledge context was provided."

        parts = []
        for idx, item in enumerate(results, start=1):
            if not isinstance(item, dict):
                continue
            title = item.get("title", "Unknown Title")
            doc_id = item.get("document_id", "Unknown ID")
            source = item.get("source", "Unknown Source")
            sim = item.get("similarity", 0.0)
            text = str(item.get("text", "")).strip()

            if not text:
                continue

            sim_str = f"{sim:.4f}" if isinstance(sim, (int, float)) else str(sim)
            parts.append(
                f"Knowledge Source {idx}\n"
                f"Title: {title}\n"
                f"Document ID: {doc_id}\n"
                f"Source: {source}\n"
                f"Similarity: {sim_str}\n\n"
                f"{text}"
            )

        if not parts:
            return "No valid knowledge content was retrieved."

        return "\n---\n\n".join(parts)

    def validate_query(self, query: Any) -> str:
        """Validate that the query is a non-empty string."""
        if query is None or not isinstance(query, str):
            raise LLMValidationError(f"Query must be a non-empty string, got {type(query).__name__}.")
        clean_q = query.strip()
        if not clean_q:
            raise LLMValidationError("Query cannot be empty or whitespace only.")
        return clean_q

    def build_prompt(
        self,
        query: str,
        context: Any,
        system_instructions: Optional[str] = None
    ) -> str:
        """
        Build a single unified text prompt suitable for Ollama's /api/generate endpoint.
        """
        clean_query = self.validate_query(query)
        clean_context = self._normalize_context(context)
        system_text = system_instructions.strip() if system_instructions and system_instructions.strip() else self.system_prompt

        prompt = (
            f"### SYSTEM INSTRUCTIONS\n"
            f"{system_text}\n\n"
            f"### RETRIEVED KNOWLEDGE CONTEXT\n"
            f"{clean_context}\n\n"
            f"### TELEMETRY SYMPTOMS & QUERY\n"
            f"{clean_query}\n\n"
            f"### DIAGNOSTIC ANALYSIS & EXPLANATION\n"
        )
        return prompt

    def build_messages(
        self,
        query: str,
        context: Any,
        system_instructions: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build a chat message sequence suitable for Ollama's /api/chat endpoint.
        """
        clean_query = self.validate_query(query)
        clean_context = self._normalize_context(context)
        system_text = system_instructions.strip() if system_instructions and system_instructions.strip() else self.system_prompt

        user_content = (
            f"Retrieved Knowledge Context:\n"
            f"{clean_context}\n\n"
            f"Observed Telemetry Symptoms / Query:\n"
            f"{clean_query}\n\n"
            f"Please provide your diagnosis and explanation based on the knowledge context above."
        )

        return [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_content}
        ]


# Convenience functional interfaces
_default_builder = PromptBuilder()


def build_prompt(
    query: str,
    context: Any,
    system_instructions: Optional[str] = None
) -> str:
    """Helper function to build a prompt using default prompt builder."""
    if system_instructions:
        builder = PromptBuilder(system_prompt=system_instructions)
        return builder.build_prompt(query, context)
    return _default_builder.build_prompt(query, context)


def build_messages(
    query: str,
    context: Any,
    system_instructions: Optional[str] = None
) -> List[Dict[str, str]]:
    """Helper function to build chat messages using default prompt builder."""
    if system_instructions:
        builder = PromptBuilder(system_prompt=system_instructions)
        return builder.build_messages(query, context)
    return _default_builder.build_messages(query, context)
