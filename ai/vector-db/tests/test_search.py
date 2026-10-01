"""
Unit tests for P8 Search module (SemanticSearchEngine).
Tests query embedding generation flow (mocked client), top-k retrieval,
search result structure, and input validation without requiring live Ollama.
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Ensure ai/vector-db is in module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import StoredVectorRecord
from database import ChromaManager
from search import SemanticSearchEngine


class FakeOllamaClient:
    """Test fake client that produces deterministic query embeddings."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.model = "nomic-embed-text"

    def embed_text(self, text: str):
        # Deterministic vector based on query keywords
        if "motor" in text.lower() or "temperature" in text.lower():
            return [0.1] * self.dimension
        elif "pump" in text.lower() or "pressure" in text.lower():
            return [-0.1] * self.dimension
        else:
            return [0.0] * self.dimension


class TestSemanticSearch(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.chroma_path = self.temp_dir.name
        self.manager = ChromaManager(
            chroma_path=self.chroma_path,
            collection_name="test_search_col",
            metric="cosine"
        )

        # Seed database with sample records
        self.rec_motor = StoredVectorRecord(
            chunk_id="FAULT-001_chunk_001",
            document_id="FAULT-001",
            document_type="fault",
            source="faults/bearing-overheating.md",
            chunk_index=0,
            title="Bearing Overheating",
            category="mechanical",
            equipment="motor",
            severity="high",
            sensors=["temperature", "vibration"],
            text="# Bearing Overheating\n\nMotor bearing is overheating.",
            embedding=[0.1] * 768,
            embedding_dimension=768,
            embedding_model="nomic-embed-text"
        )

        self.rec_pump = StoredVectorRecord(
            chunk_id="FAULT-008_chunk_001",
            document_id="FAULT-008",
            document_type="fault",
            source="faults/low-pressure.md",
            chunk_index=0,
            title="Low Pressure",
            category="hydraulic",
            equipment="pump",
            severity="medium",
            sensors=["pressure"],
            text="# Low Pressure\n\nPump discharge pressure is low.",
            embedding=[-0.1] * 768,
            embedding_dimension=768,
            embedding_model="nomic-embed-text"
        )

        self.manager.upsert_records([self.rec_motor, self.rec_pump])
        self.fake_client = FakeOllamaClient(dimension=768)
        self.engine = SemanticSearchEngine(
            chroma_manager=self.manager,
            ollama_client=self.fake_client
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_search_motor_query_retrieves_motor_record_first(self):
        results = self.engine.search("motor temperature is rising", top_k=2)

        self.assertEqual(len(results), 2)
        # First result should be the motor record
        self.assertEqual(results[0].rank, 1)
        self.assertEqual(results[0].chunk_id, "FAULT-001_chunk_001")
        self.assertEqual(results[0].title, "Bearing Overheating")
        self.assertAlmostEqual(results[0].distance, 0.0, places=4)
        self.assertAlmostEqual(results[0].similarity, 1.0, places=4)

    def test_search_pump_query_retrieves_pump_record_first(self):
        results = self.engine.search("pump pressure is abnormal", top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].rank, 1)
        self.assertEqual(results[0].chunk_id, "FAULT-008_chunk_001")
        self.assertEqual(results[0].title, "Low Pressure")

    def test_search_top_k_limits_output(self):
        results = self.engine.search("equipment query", top_k=1)
        self.assertEqual(len(results), 1)

    def test_search_empty_query_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.engine.search("")
        with self.assertRaises(ValueError):
            self.engine.search("   \n\t  ")

    def test_search_result_fields_populated(self):
        results = self.engine.search("motor test", top_k=1)
        res = results[0]

        self.assertIsNotNone(res.chunk_id)
        self.assertIsNotNone(res.document_id)
        self.assertIsNotNone(res.document_type)
        self.assertIsNotNone(res.source)
        self.assertIsNotNone(res.title)
        self.assertIsInstance(res.distance, float)
        self.assertIsInstance(res.similarity, float)
        self.assertTrue(len(res.text) > 0)
        self.assertIsInstance(res.metadata, dict)


if __name__ == "__main__":
    unittest.main()
