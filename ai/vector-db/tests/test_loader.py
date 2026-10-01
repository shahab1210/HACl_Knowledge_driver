"""
Unit tests for P8 Loader module.
Tests loading P7 embeddings JSON into persistent ChromaDB, validating schema,
post-insertion verification, and idempotency across repeated runs.
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path

# Ensure ai/vector-db is in module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import ChromaManager
from loader import load_embeddings_into_chroma


class TestLoader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.chroma_path = str(self.temp_path / "chroma_test")

        self.sample_payload = {
            "generated_at": "2026-09-30T00:00:00Z",
            "source": "ai/ingestion/output/chunks.json",
            "embedding_model": "nomic-embed-text",
            "document_count": 2,
            "chunk_count": 2,
            "embedding_dimension": 768,
            "embeddings": [
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
                    "sensors": ["temperature", "vibration"],
                    "text": "# Bearing Overheating\n\nHigh bearing temperature.",
                    "embedding": [0.05] * 768,
                    "embedding_dimension": 768,
                    "embedding_model": "nomic-embed-text"
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
                    "text": "# Current Sensor\n\nMeasures electrical current.",
                    "embedding": [-0.05] * 768,
                    "embedding_dimension": 768,
                    "embedding_model": "nomic-embed-text"
                }
            ]
        }

        self.json_file = self.temp_path / "test_embeddings.json"
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.sample_payload, f)

        self.manager = ChromaManager(
            chroma_path=self.chroma_path,
            collection_name="test_loader_col"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_embeddings_success(self):
        report = load_embeddings_into_chroma(
            embeddings_file=str(self.json_file),
            chroma_manager=self.manager
        )

        self.assertEqual(report["status"], "SUCCESS")
        self.assertEqual(report["records_loaded"], 2)
        self.assertEqual(report["total_collection_count"], 2)
        self.assertEqual(report["embedding_dimension"], 768)

    def test_load_idempotency(self):
        # Run first load
        load_embeddings_into_chroma(str(self.json_file), self.manager)
        self.assertEqual(self.manager.count(), 2)

        # Run second load with same file
        load_embeddings_into_chroma(str(self.json_file), self.manager)
        self.assertEqual(self.manager.count(), 2, "Second load must not double record count")

    def test_load_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            load_embeddings_into_chroma(
                embeddings_file="/nonexistent/path/to/embeddings.json",
                chroma_manager=self.manager
            )

    def test_load_invalid_embeddings_raises_error(self):
        bad_file = self.temp_path / "bad.json"
        with open(bad_file, "w", encoding="utf-8") as f:
            json.dump({"embeddings": [{"chunk_id": "BAD", "text": ""}]}, f)

        with self.assertRaises(ValueError):
            load_embeddings_into_chroma(str(bad_file), self.manager)


if __name__ == "__main__":
    unittest.main()
