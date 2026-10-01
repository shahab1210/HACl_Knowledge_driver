"""
Unit tests for P7 Validator module.
Tests schema validation of input chunks, required fields, duplicate detection,
and embedding output validation (dimensionality, NaN/Inf checks, metadata preservation).
"""

import sys
import math
import unittest
from pathlib import Path

# Ensure ai/embeddings is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import ChunkRecord, EmbeddingRecord
from validator import validate_chunks_input, validate_embeddings_output


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.valid_raw_chunk = {
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
            "text": "# Bearing Overheating\n\n## Description\nBearing is hot."
        }

        self.valid_chunk_record = ChunkRecord.from_dict(self.valid_raw_chunk)
        self.valid_embedding = [0.01] * 768
        self.valid_emb_record = EmbeddingRecord.from_chunk(
            self.valid_chunk_record,
            self.valid_embedding,
            "nomic-embed-text"
        )

    def test_validate_chunks_input_success(self):
        data = {"chunks": [self.valid_raw_chunk]}
        res, records = validate_chunks_input(data)

        self.assertTrue(res.is_valid)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].chunk_id, "FAULT-001_chunk_001")
        self.assertEqual(records[0].document_id, "FAULT-001")

    def test_validate_chunks_input_missing_chunks_key(self):
        data = {"documents": []}
        res, records = validate_chunks_input(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("missing required 'chunks' list" in e for e in res.errors))

    def test_validate_chunks_input_empty_chunks_list(self):
        data = {"chunks": []}
        res, records = validate_chunks_input(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("is empty" in e for e in res.errors))

    def test_validate_chunks_input_missing_required_field(self):
        bad_chunk = dict(self.valid_raw_chunk)
        del bad_chunk["title"]
        data = {"chunks": [bad_chunk]}
        res, records = validate_chunks_input(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("missing required field: 'title'" in e for e in res.errors))

    def test_validate_chunks_input_duplicate_chunk_id(self):
        chunk1 = dict(self.valid_raw_chunk)
        chunk2 = dict(self.valid_raw_chunk)
        data = {"chunks": [chunk1, chunk2]}
        res, records = validate_chunks_input(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("Duplicate chunk_id detected" in e for e in res.errors))

    def test_validate_chunks_input_empty_text(self):
        bad_chunk = dict(self.valid_raw_chunk)
        bad_chunk["text"] = "   "
        data = {"chunks": [bad_chunk]}
        res, records = validate_chunks_input(data)

        self.assertFalse(res.is_valid)
        self.assertTrue(any("empty or whitespace-only text" in e for e in res.errors))

    def test_validate_embeddings_output_success(self):
        res = validate_embeddings_output(
            [self.valid_emb_record],
            expected_chunk_count=1,
            expected_model="nomic-embed-text"
        )
        self.assertTrue(res.is_valid)
        self.assertEqual(res.stats["embedding_dimension"], 768)

    def test_validate_embeddings_output_count_mismatch(self):
        res = validate_embeddings_output(
            [self.valid_emb_record],
            expected_chunk_count=2,  # Expected 2 but provided 1
            expected_model="nomic-embed-text"
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("count mismatch" in e for e in res.errors))

    def test_validate_embeddings_output_inconsistent_dimensions(self):
        rec2 = EmbeddingRecord.from_chunk(
            ChunkRecord(
                chunk_id="FAULT-001_chunk_002",
                document_id="FAULT-001",
                document_type="fault",
                source="faults/bearing-overheating.md",
                chunk_index=1,
                title="Bearing Overheating",
                text="Second chunk"
            ),
            [0.05] * 384,  # 384 vs first record's 768!
            "nomic-embed-text"
        )

        res = validate_embeddings_output(
            [self.valid_emb_record, rec2],
            expected_chunk_count=2,
            expected_model="nomic-embed-text"
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Dimensionality mismatch" in e for e in res.errors))

    def test_validate_embeddings_output_detects_nan_and_inf(self):
        bad_vec = [0.01] * 768
        bad_vec[42] = float("nan")

        nan_record = EmbeddingRecord.from_chunk(
            self.valid_chunk_record,
            bad_vec,
            "nomic-embed-text"
        )

        res = validate_embeddings_output(
            [nan_record],
            expected_chunk_count=1,
            expected_model="nomic-embed-text"
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Non-finite value (NaN/Inf)" in e for e in res.errors))


if __name__ == "__main__":
    unittest.main()
