"""
Unit and integration tests for P7 embed pipeline.
Tests pipeline execution, schema conversion, mock client embedding generation,
dynamic dimension detection, and output file serialization.
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path

# Ensure ai/embeddings is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from client import OllamaClient
from embed import run_embedding_pipeline


class FakeOllamaClient(OllamaClient):
    """Test fake client that does not make network calls."""

    def __init__(self, dimension: int = 768, running: bool = True, model_available: bool = True):
        super().__init__(base_url="http://fake-host:11434", model="nomic-embed-text")
        self.dimension = dimension
        self.running = running
        self.model_available = model_available

    def is_server_running(self) -> bool:
        return self.running

    def is_model_available(self, model_name=None) -> bool:
        return self.model_available

    def list_models(self):
        return ["nomic-embed-text:latest"] if self.model_available else []

    def embed_text(self, text: str):
        # Deterministic fake embedding based on string length
        val = (len(text) % 100) / 100.0
        return [val] * self.dimension

    def embed_batch(self, texts):
        return [self.embed_text(t) for t in texts]


class TestEmbeddingPipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create sample chunks.json
        self.sample_chunks = {
            "generated_at": "2026-09-30T00:00:00Z",
            "source_directory": "ai/knowledge-base",
            "document_count": 2,
            "chunk_count": 2,
            "chunks": [
                {
                    "chunk_id": "FAULT-001_chunk_001",
                    "document_id": "FAULT-001",
                    "document_type": "fault",
                    "source": "faults/bearing-overheating.md",
                    "chunk_index": 0,
                    "title": "Bearing Overheating",
                    "category": "mechanical",
                    "equipment": "motor",
                    "severity": "high",
                    "sensors": ["temperature", "vibration", "current"],
                    "text": "# Bearing Overheating\n\nBearing temperature is high."
                },
                {
                    "chunk_id": "SENSOR-CURRENT_chunk_001",
                    "document_id": "SENSOR-CURRENT",
                    "document_type": "sensor",
                    "source": "sensors/current.md",
                    "chunk_index": 0,
                    "title": "Current Sensor",
                    "category": "instrumentation",
                    "equipment": "sensor",
                    "severity": None,
                    "sensors": ["current"],
                    "text": "# Current Sensor\n\nMeasures electrical current."
                }
            ]
        }

        self.input_file = self.temp_path / "chunks.json"
        with open(self.input_file, "w", encoding="utf-8") as f:
            json.dump(self.sample_chunks, f)

        self.output_file = self.temp_path / "embeddings.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_pipeline_success_with_fake_client(self):
        client = FakeOllamaClient(dimension=768)
        success = run_embedding_pipeline(
            input_file=self.input_file,
            output_file=self.output_file,
            model="nomic-embed-text",
            client=client
        )

        self.assertTrue(success)
        self.assertTrue(self.output_file.exists())

        # Verify output content
        with open(self.output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["embedding_model"], "nomic-embed-text")
        self.assertEqual(data["embedding_dimension"], 768)
        self.assertEqual(data["chunk_count"], 2)
        self.assertEqual(len(data["embeddings"]), 2)

        emb1 = data["embeddings"][0]
        self.assertEqual(emb1["chunk_id"], "FAULT-001_chunk_001")
        self.assertEqual(emb1["title"], "Bearing Overheating")
        self.assertEqual(emb1["category"], "mechanical")
        self.assertEqual(len(emb1["embedding"]), 768)

    def test_pipeline_dynamic_dimension_detection(self):
        # Test with custom dimension (e.g., 384 for MiniLM-style models)
        client = FakeOllamaClient(dimension=384)
        success = run_embedding_pipeline(
            input_file=self.input_file,
            output_file=self.output_file,
            model="nomic-embed-text",
            client=client
        )

        self.assertTrue(success)
        with open(self.output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["embedding_dimension"], 384)
        self.assertEqual(len(data["embeddings"][0]["embedding"]), 384)

    def test_pipeline_fails_when_server_not_running(self):
        client = FakeOllamaClient(running=False)
        success = run_embedding_pipeline(
            input_file=self.input_file,
            output_file=self.output_file,
            client=client
        )
        self.assertFalse(success)

    def test_pipeline_fails_when_model_not_installed(self):
        client = FakeOllamaClient(model_available=False)
        success = run_embedding_pipeline(
            input_file=self.input_file,
            output_file=self.output_file,
            client=client
        )
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
