"""
Configuration settings for P10 Local LLM Generation Layer.

Defines default endpoints, model selection, generation hyperparameters,
safety directives, and environment variable overrides.
"""

import os
from dataclasses import dataclass, field
from typing import Set, Optional
from models import GenerationOptions

# Default Ollama Service Endpoint
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("LLM_BASE_URL", DEFAULT_OLLAMA_BASE_URL))

# Default Generative LLM Model (practical for Apple Silicon MacBook)
# DEFAULT_LLM_MODEL = "llama3.2:3b"
DEFAULT_LLM_MODEL = "qwen2.5:1.5b"
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", os.getenv("GENERATION_MODEL", DEFAULT_LLM_MODEL)))

# Inference Hyperparameters
DEFAULT_TIMEOUT = 120.0  # seconds
TIMEOUT = float(os.getenv("LLM_TIMEOUT", DEFAULT_TIMEOUT))

DEFAULT_TEMPERATURE = 0.2
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))

DEFAULT_MAX_TOKENS = 1024
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", DEFAULT_MAX_TOKENS))

DEFAULT_TOP_P = 0.9
TOP_P = float(os.getenv("LLM_TOP_P", DEFAULT_TOP_P))

DEFAULT_TOP_K = 40
TOP_K = int(os.getenv("LLM_TOP_K", DEFAULT_TOP_K))

# Known Embedding-only models that should never be used for generation
KNOWN_EMBEDDING_MODELS: Set[str] = {
    "nomic-embed-text",
    "all-minilm",
    "bge-large",
    "bge-small",
    "bge-m3",
    "mxbai-embed-large",
    "snowflake-arctic-embed",
    "paraphrase-multilingual",
}

# Standard Industrial IoT Fault Diagnosis System Prompt
DEFAULT_SYSTEM_PROMPT = (
    "You are an expert Industrial IoT Fault Diagnosis Assistant.\n"
    "Your task is to analyze equipment symptoms, sensor telemetry anomalies, and operational observations "
    "strictly using the provided Knowledge Base context.\n\n"
    "Diagnostic Directives:\n"
    "1. Grounding: Base your diagnosis and technical explanations strictly on the provided Knowledge Context.\n"
    "2. No Hallucination: Do NOT invent unsupported facts, root causes, sensor thresholds, or maintenance actions.\n"
    "3. Source Citation: Explicitly cite the specific Knowledge Sources, Document IDs, or Fault Titles that support each part of your response.\n"
    "4. Knowledge vs Hypotheses: Clearly distinguish retrieved domain knowledge from secondary inferences or operational assumptions.\n"
    "5. Insufficient Context: If the provided knowledge context is insufficient to determine the fault or root cause, "
    "explicitly state: 'Insufficient knowledge in context to confirm diagnosis' and specify what additional sensor telemetry "
    "or physical inspection procedures are required.\n"
    "6. Calibrated Certainty: Do not express absolute certainty when symptoms are ambiguous or match multiple potential fault modes."
)


@dataclass
class LLMConfig:
    """
    Encapsulates all runtime configuration for P10 Local LLM inference.
    """
    base_url: str = DEFAULT_OLLAMA_BASE_URL
    model: str = DEFAULT_LLM_MODEL
    timeout: float = DEFAULT_TIMEOUT
    options: GenerationOptions = field(
        default_factory=lambda: GenerationOptions(
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            top_k=DEFAULT_TOP_K,
            num_predict=DEFAULT_MAX_TOKENS,
        )
    )
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Build LLMConfig reading environment variables with fallback defaults."""
        opts = GenerationOptions(
            temperature=float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
            top_p=float(os.getenv("LLM_TOP_P", DEFAULT_TOP_P)),
            top_k=int(os.getenv("LLM_TOP_K", DEFAULT_TOP_K)),
            num_predict=int(os.getenv("LLM_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
        )
        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", os.getenv("LLM_BASE_URL", DEFAULT_OLLAMA_BASE_URL)),
            model=os.getenv("LLM_MODEL", os.getenv("OLLAMA_MODEL", os.getenv("GENERATION_MODEL", DEFAULT_LLM_MODEL))),
            timeout=float(os.getenv("LLM_TIMEOUT", DEFAULT_TIMEOUT)),
            options=opts,
            system_prompt=os.getenv("LLM_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
        )
