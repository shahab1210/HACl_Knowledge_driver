"""
Configuration settings for P11 RAG + LLM Integration Layer.
"""

import os
from dataclasses import dataclass

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)

DEFAULT_LLM_MODEL = "qwen2.5:1.5b"
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", os.getenv("GENERATION_MODEL", DEFAULT_LLM_MODEL)))

DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)

DEFAULT_TOP_K = 3
TOP_K = int(os.getenv("RAG_TOP_K", DEFAULT_TOP_K))

DEFAULT_TEMPERATURE = 0.2
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))

DEFAULT_MAX_TOKENS = 1024
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", DEFAULT_MAX_TOKENS))

DEFAULT_TIMEOUT = 120.0
TIMEOUT = float(os.getenv("LLM_TIMEOUT", DEFAULT_TIMEOUT))


@dataclass
class PipelineConfig:
    """
    Encapsulates all runtime configuration parameters for the integrated RAG+LLM pipeline.
    """
    base_url: str = DEFAULT_OLLAMA_BASE_URL
    model: str = DEFAULT_LLM_MODEL
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    top_k: int = DEFAULT_TOP_K
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    timeout: float = DEFAULT_TIMEOUT

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL),
            model=os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", os.getenv("GENERATION_MODEL", DEFAULT_LLM_MODEL))),
            embedding_model=os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
            top_k=int(os.getenv("RAG_TOP_K", DEFAULT_TOP_K)),
            temperature=float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
            timeout=float(os.getenv("LLM_TIMEOUT", DEFAULT_TIMEOUT))
        )
