"""
Unit tests for P8 Validator module.
Tests schema validation of input embeddings, dimensionality checks, NaN/Inf detection,
and post-insertion collection integrity checks.
"""

import sys
import unittest
from pathlib import Path

# Ensure ai/vector-db is in module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validator import validate_embeddings_file, validate_collection_integrity


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.sample_record = {
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
            "text": "# Bearing Overheating\n\nContent here.",
            "embedding": [0.0123] * 768,
            "embedding_dimension": 768,
            "embedding_model": "nomic-embed-text"
        }

    def test_validate_embeddings_file_success(self):
        data = {"embeddings": [self.sample_record]}
        res, records = validate_embeddings_file(data)

        self.assertTrue(res.is_valid)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].chunk_id, "FAULT-001_chunk_001")
        self.assertEqual(records[0].embedding_dimension, 768)

    def test_validate_embeddings_file_missing_key(self):
        data = {"documents": []}
        res, records = validate_embeddings_file(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("missing required 'embeddings' list" in e for e in res.errors))

    def test_validate_embeddings_file_empty_list(self):
        data = {"embeddings": []}
        res, records = validate_embeddings_file(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("is empty" in e for e in res.errors))

    def test_validate_embeddings_file_missing_required_field(self):
        bad_rec = dict(self.sample_record)
        del bad_rec["text"]
        data = {"embeddings": [bad_rec]}
        res, records = validate_embeddings_file(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("missing required field: 'text'" in e for e in res.errors))

    def test_validate_embeddings_file_inconsistent_dimensions(self):
        rec2 = dict(self.sample_record)
        rec2["chunk_id"] = "FAULT-001_chunk_002"
        rec2["embedding"] = [0.0123] * 384  # 384 vs 768

        data = {"embeddings": [self.sample_record, rec2]}
        res, records = validate_embeddings_file(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("Dimensionality mismatch" in e for e in res.errors))

    def test_validate_embeddings_file_nan_detection(self):
        bad_vec = list(self.sample_record["embedding"])
        bad_vec[10] = float("nan")
        bad_rec = dict(self.sample_record)
        bad_rec["embedding"] = bad_vec

        data = {"embeddings": [bad_rec]}
        res, records = validate_embeddings_file(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("NaN/Inf" in e for e in res.errors))

    def test_validate_embeddings_file_duplicate_chunk_id(self):
        data = {"embeddings": [self.sample_record, dict(self.sample_record)]}
        res, records = validate_embeddings_file(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("Duplicate chunk_id" in e for e in res.errors))

    def test_validate_collection_integrity_success(self):
        class FakeCollection:
            name = "test_col"
            def count(self):
                return 32

        col = FakeCollection()
        res = validate_collection_integrity(col, expected_count=32)
        self.assertTrue(res.is_valid)

    def test_validate_collection_integrity_mismatch(self):
        class FakeCollection:
            name = "test_col"
            def count(self):
                return 15

        col = FakeCollection()
        res = validate_collection_integrity(col, expected_count=32)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("mismatch" in e for e in res.errors))


if __name__ == "__main__":
    unittest.main()
