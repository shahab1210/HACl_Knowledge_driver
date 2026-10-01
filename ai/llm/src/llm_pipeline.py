"""
P10 Local LLM Pipeline - Generation Orchestrator

Integrates the Prompt Builder and LocalLLMClient to produce grounded,
natural language fault explanations from RAG retrieved context.

Pipeline Flow:
Retrieved Context (from P9) + Query
               ↓
         Prompt Builder
               ↓
        Local LLM Client
               ↓
    Structured Pipeline Output
"""

from typing import Any, Dict, Optional, Union
from client import LocalLLMClient
from prompt_builder import PromptBuilder
from models import GenerationOptions, LLMPipelineOutput, LLMValidationError


class LLMPipeline:
    """
    High-level generation pipeline for Local LLM inference.
    """

    def __init__(
        self,
        client: Optional[LocalLLMClient] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        default_options: Optional[Union[GenerationOptions, Dict[str, Any]]] = None
    ):
        self.client = client if client is not None else LocalLLMClient(
            base_url=base_url,
            model=model,
            timeout=timeout,
            default_options=default_options
        )
        self.prompt_builder = prompt_builder if prompt_builder is not None else PromptBuilder()

    def generate(
        self,
        query: str,
        context: Any,
        options: Optional[Union[GenerationOptions, Dict[str, Any]]] = None,
        system_instructions: Optional[str] = None
    ) -> LLMPipelineOutput:
        """
        Build prompt and generate natural language diagnosis from query and context.
        """
        clean_query = self.prompt_builder.validate_query(query)
        normalized_ctx = self.prompt_builder._normalize_context(context)

        prompt = self.prompt_builder.build_prompt(
            query=clean_query,
            context=normalized_ctx,
            system_instructions=system_instructions
        )

        gen_resp = self.client.generate(
            prompt=prompt,
            options=options
        )

        # Count results if context is list or dict
        result_count = 0
        if isinstance(context, dict) and "result_count" in context:
            result_count = int(context["result_count"])
        elif isinstance(context, list):
            result_count = len(context)

        return LLMPipelineOutput(
            query=clean_query,
            context=normalized_ctx,
            prompt=prompt,
            response=gen_resp.text,
            model=gen_resp.model,
            result_count=result_count,
            generation_details=gen_resp.to_dict()
        )

    def generate_from_rag(
        self,
        rag_output: Dict[str, Any],
        options: Optional[Union[GenerationOptions, Dict[str, Any]]] = None,
        system_instructions: Optional[str] = None
    ) -> LLMPipelineOutput:
        """
        Convenience method to generate a response directly from a P9 RAG output dictionary.
        """
        if not isinstance(rag_output, dict):
            raise LLMValidationError(f"Expected dict for rag_output, got {type(rag_output).__name__}")

        query = rag_output.get("query")
        if not query:
            raise LLMValidationError("rag_output dictionary must contain a non-empty 'query' key.")

        context = rag_output.get("context", "")
        result_count = rag_output.get("result_count", 0)

        output = self.generate(
            query=query,
            context=context,
            options=options,
            system_instructions=system_instructions
        )
        output.result_count = result_count
        return output
