"""
Unit tests for P8 Database module (ChromaManager).
Tests persistent collection lifecycle, idempotent upserting, record count,
distance metric configuration, and vector similarity querying using temporary directories.
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Ensure ai/vector-db is in module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import StoredVectorRecord
from database import ChromaManager


class TestChromaManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.chroma_path = self.temp_dir.name
        self.collection_name = "test_iot_knowledge"
        self.manager = ChromaManager(
            chroma_path=self.chroma_path,
            collection_name=self.collection_name,
            metric="cosine"
        )

        self.sample_record_1 = StoredVectorRecord(
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
            text="# Bearing Overheating\n\nHigh bearing temperature.",
            embedding=[0.1] * 768,
            embedding_dimension=768,
            embedding_model="nomic-embed-text"
        )

        self.sample_record_2 = StoredVectorRecord(
            chunk_id="FAULT-006_chunk_001",
            document_id="FAULT-006",
            document_type="fault",
            source="faults/pump-cavitation.md",
            chunk_index=0,
            title="Pump Cavitation",
            category="hydraulic",
            equipment="pump",
            severity="critical",
            sensors=["pressure", "vibration"],
            text="# Pump Cavitation\n\nCavitation noise and erratic pressure.",
            embedding=[-0.1] * 768,
            embedding_dimension=768,
            embedding_model="nomic-embed-text"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_collection_count_is_zero(self):
        self.assertEqual(self.manager.count(), 0)

    def test_upsert_records_and_count(self):
        inserted = self.manager.upsert_records([self.sample_record_1, self.sample_record_2])
        self.assertEqual(inserted, 2)
        self.assertEqual(self.manager.count(), 2)

    def test_idempotent_upsert_does_not_duplicate(self):
        self.manager.upsert_records([self.sample_record_1, self.sample_record_2])
        self.assertEqual(self.manager.count(), 2)

        # Upsert the exact same records a second time
        self.manager.upsert_records([self.sample_record_1, self.sample_record_2])
        self.assertEqual(self.manager.count(), 2, "Second upsert must not create duplicate records")

    def test_query_vector_returns_ordered_results(self):
        self.manager.upsert_records([self.sample_record_1, self.sample_record_2])

        # Query with vector identical to record 1
        results = self.manager.query(query_embedding=[0.1] * 768, top_k=2)

        self.assertEqual(len(results), 2)
        # Top result should be record 1 with near zero cosine distance
        self.assertEqual(results[0].chunk_id, "FAULT-001_chunk_001")
        self.assertAlmostEqual(results[0].distance, 0.0, places=4)
        self.assertAlmostEqual(results[0].similarity, 1.0, places=4)
        self.assertEqual(results[0].title, "Bearing Overheating")
        self.assertEqual(results[0].document_type, "fault")
        self.assertIn("temperature", results[0].metadata["sensors"])

    def test_persistence_reopening_preserves_records(self):
        self.manager.upsert_records([self.sample_record_1, self.sample_record_2])
        self.assertEqual(self.manager.count(), 2)

        # Reopen a new manager instance pointing to the same disk path
        reopened_manager = ChromaManager(
            chroma_path=self.chroma_path,
            collection_name=self.collection_name,
            metric="cosine"
        )
        self.assertEqual(reopened_manager.count(), 2)

        # Confirm querying against reopened manager works
        results = reopened_manager.query(query_embedding=[0.1] * 768, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk_id, "FAULT-001_chunk_001")


if __name__ == "__main__":
    unittest.main()
