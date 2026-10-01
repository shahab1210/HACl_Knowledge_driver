"""
P11 RAG + LLM Integration Pipeline - Orchestrator

Integrates P9 RAG retrieval and P10 Local LLM generation into a single,
reusable, application-level fault diagnosis pipeline.

Pipeline Flow:
User/Telemetry Query
        ↓
Input Validation
        ↓
P9 RAG Retrieval (ChromaDB + nomic-embed-text)
        ↓
Retrieved Evidence Preservation & Grounded Context
        ↓
P10 Prompt Construction & Safety Directives
        ↓
Local LLM Generation (Ollama / qwen2.5:1.5b)
        ↓
DiagnosisResponse (Structured Output)
"""

from typing import Optional, Dict, Any, Union

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
from exceptions import (
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
from loader import load_rag_pipeline, load_llm_pipeline


class RAGLLMPipeline:
    """
    Unified application-level pipeline orchestrating P9 RAG retrieval
    and P10 Local LLM generation for industrial IoT fault diagnosis.
    """

    def __init__(
        self,
        top_k: int = DEFAULT_TOP_K,
        model: Optional[str] = None,
        embedding_model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        rag_pipeline: Optional[Any] = None,
        llm_pipeline: Optional[Any] = None
    ):
        # Validate configuration
        if not isinstance(top_k, int) or top_k <= 0:
            raise PipelineConfigError(f"top_k must be a positive integer, got {top_k}")

        self.top_k = top_k
        self.model = model or DEFAULT_LLM_MODEL
        self.embedding_model = embedding_model or DEFAULT_EMBEDDING_MODEL
        self.base_url = (base_url or DEFAULT_OLLAMA_BASE_URL).rstrip("/")
        self.temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS
        self.timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

        if self.temperature < 0.0 or self.temperature > 2.0:
            raise PipelineConfigError(f"temperature must be between 0.0 and 2.0, got {self.temperature}")
        if self.max_tokens <= 0:
            raise PipelineConfigError(f"max_tokens must be positive, got {self.max_tokens}")

        # Initialize or inject P9 RAG Pipeline
        if rag_pipeline is not None:
            self.rag_pipeline = rag_pipeline
        else:
            self.rag_pipeline = load_rag_pipeline(
                top_k=self.top_k,
                model=self.embedding_model,
                base_url=self.base_url
            )

        # Initialize or inject P10 LLM Pipeline
        if llm_pipeline is not None:
            self.llm_pipeline = llm_pipeline
        else:
            self.llm_pipeline = load_llm_pipeline(
                model=self.model,
                base_url=self.base_url,
                timeout=self.timeout
            )

    def validate_query(self, query: Any) -> str:
        """
        Validate that the query input is a non-empty, non-whitespace string.
        """
        if query is None or not isinstance(query, str):
            raise QueryValidationError(f"Query must be a non-empty string, got {type(query).__name__}.")
        clean_q = query.strip()
        if not clean_q:
            raise QueryValidationError("Query cannot be empty or whitespace only.")
        return clean_q

    def run(
        self,
        query: str,
        top_k: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> DiagnosisResponse:
        """
        Execute end-to-end RAG retrieval and local LLM diagnosis generation.
        """
        clean_query = self.validate_query(query)
        effective_top_k = top_k if top_k is not None else self.top_k
        if not isinstance(effective_top_k, int) or effective_top_k <= 0:
            raise PipelineConfigError(f"top_k must be a positive integer, got {effective_top_k}")

        eff_temp = temperature if temperature is not None else self.temperature
        eff_tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Step 1: P9 RAG Retrieval
        try:
            rag_output = self.rag_pipeline.run(
                query=clean_query,
                top_k=effective_top_k
            )
        except Exception as e:
            raise RetrievalError(f"RAG retrieval stage failed: {e}") from e

        # Step 2: Extract and structure retrieval evidence
        raw_results = rag_output.get("results", [])
        sources = [SourceEvidence.from_dict(item) for item in raw_results]
        retrieval_evidence = RetrievalEvidence(
            query=clean_query,
            result_count=len(sources),
            top_k=effective_top_k,
            sources=sources,
            context=rag_output.get("context", "")
        )

        # Step 3: P10 Prompt Construction & LLM Generation
        gen_opts = {
            "temperature": eff_temp,
            "max_tokens": eff_tokens,
            "num_predict": eff_tokens
        }

        try:
            llm_output = self.llm_pipeline.generate_from_rag(
                rag_output=rag_output,
                options=gen_opts
            )
        except Exception as e:
            raise GenerationError(f"LLM generation stage failed: {e}") from e

        # Step 4: Assemble structured diagnosis response
        response_text = getattr(llm_output, "response", "")
        model_name = getattr(llm_output, "model", self.model)
        prompt_text = getattr(llm_output, "prompt", "")
        gen_details = getattr(llm_output, "generation_details", {})

        return DiagnosisResponse(
            query=clean_query,
            diagnosis=response_text,
            retrieval=retrieval_evidence,
            context=retrieval_evidence.context,
            prompt=prompt_text,
            response=response_text,
            model=model_name,
            generation_details=gen_details
        )

    def diagnose(
        self,
        query: str,
        top_k: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> DiagnosisResponse:
        """Alias for run()."""
        return self.run(query=query, top_k=top_k, temperature=temperature, max_tokens=max_tokens)
