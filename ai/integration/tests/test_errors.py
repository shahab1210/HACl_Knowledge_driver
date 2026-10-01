"""
Unit tests for P11 validation and error handling.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipeline import RAGLLMPipeline
from exceptions import (
    PipelineConfigError,
    QueryValidationError,
    RetrievalError,
    GenerationError,
)


def test_empty_query_raises_query_validation_error():
    pipeline = RAGLLMPipeline(
        rag_pipeline=MagicMock(),
        llm_pipeline=MagicMock()
    )
    with pytest.raises(QueryValidationError):
        pipeline.run("")


def test_whitespace_query_raises_query_validation_error():
    pipeline = RAGLLMPipeline(
        rag_pipeline=MagicMock(),
        llm_pipeline=MagicMock()
    )
    with pytest.raises(QueryValidationError):
        pipeline.run("   \t\n  ")


def test_non_string_query_raises_query_validation_error():
    pipeline = RAGLLMPipeline(
        rag_pipeline=MagicMock(),
        llm_pipeline=MagicMock()
    )
    with pytest.raises(QueryValidationError):
        pipeline.run(None)


def test_invalid_top_k_init_raises_config_error():
    with pytest.raises(PipelineConfigError):
        RAGLLMPipeline(
            top_k=0,
            rag_pipeline=MagicMock(),
            llm_pipeline=MagicMock()
        )


def test_negative_top_k_init_raises_config_error():
    with pytest.raises(PipelineConfigError):
        RAGLLMPipeline(
            top_k=-5,
            rag_pipeline=MagicMock(),
            llm_pipeline=MagicMock()
        )


def test_invalid_temperature_init_raises_config_error():
    with pytest.raises(PipelineConfigError):
        RAGLLMPipeline(
            temperature=2.5,
            rag_pipeline=MagicMock(),
            llm_pipeline=MagicMock()
        )


def test_invalid_max_tokens_init_raises_config_error():
    with pytest.raises(PipelineConfigError):
        RAGLLMPipeline(
            max_tokens=0,
            rag_pipeline=MagicMock(),
            llm_pipeline=MagicMock()
        )


def test_invalid_top_k_run_override_raises_config_error():
    pipeline = RAGLLMPipeline(
        rag_pipeline=MagicMock(),
        llm_pipeline=MagicMock()
    )
    with pytest.raises(PipelineConfigError):
        pipeline.run("Test query", top_k=-1)


def test_retrieval_failure_raises_retrieval_error():
    mock_rag = MagicMock()
    mock_rag.run.side_effect = RuntimeError("ChromaDB connection lost")

    pipeline = RAGLLMPipeline(
        rag_pipeline=mock_rag,
        llm_pipeline=MagicMock()
    )

    with pytest.raises(RetrievalError) as exc:
        pipeline.run("Motor overheating")
    assert "RAG retrieval stage failed" in str(exc.value)


def test_generation_failure_raises_generation_error():
    mock_rag = MagicMock()
    mock_rag.run.return_value = {
        "query": "Motor overheating",
        "results": [],
        "context": "Context"
    }

    mock_llm = MagicMock()
    mock_llm.generate_from_rag.side_effect = RuntimeError("Ollama server timeout")

    pipeline = RAGLLMPipeline(
        rag_pipeline=mock_rag,
        llm_pipeline=mock_llm
    )

    with pytest.raises(GenerationError) as exc:
        pipeline.run("Motor overheating")
    assert "LLM generation stage failed" in str(exc.value)
