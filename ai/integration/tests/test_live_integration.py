"""
Live Integration Tests for P11 RAG + LLM Pipeline.
Executes real end-to-end inference against local ChromaDB and Ollama service.
"""

import sys
from pathlib import Path
import pytest
import requests

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipeline import RAGLLMPipeline
from models import DiagnosisResponse


def is_ollama_available(base_url="http://localhost:11434"):
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


@pytest.mark.skipif(not is_ollama_available(), reason="Local Ollama server is not running")
def test_live_pipeline_diagnosis():
    pipeline = RAGLLMPipeline(
        top_k=3,
        model="qwen2.5:1.5b",
        embedding_model="nomic-embed-text"
    )

    query = "The motor temperature is 95°C and vibration is 7.2. What could be the problem?"
    result = pipeline.run(query)

    assert isinstance(result, DiagnosisResponse)
    assert result.query == query
    assert result.retrieval.result_count > 0
    assert len(result.retrieval.sources) > 0
    assert result.diagnosis and len(result.diagnosis.strip()) > 0
    assert result.model == "qwen2.5:1.5b"
    assert "eval_count" in result.generation_details
