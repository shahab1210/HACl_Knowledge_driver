"""
Unit tests for P6 Validator module.
Tests validation rules, duplicate detection, missing field detection, and invalid ordering detection.
"""

import sys
import unittest
from pathlib import Path

# Ensure ai/ingestion is in Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Document, Chunk
from validator import validate_knowledge_base, validate_documents, validate_chunks


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.valid_doc = Document(
            document_id="FAULT-001",
            title="Bearing Overheating",
            document_type="fault",
            source="faults/bearing-overheating.md",
            category="mechanical",
            equipment="motor",
            severity="high",
            sensors=["temperature", "vibration"],
            content="Valid content"
        )
        self.valid_chunk = Chunk(
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
            text="Valid chunk text",
            token_estimate=50
        )

    def test_knowledge_base_missing_dir(self):
        res = validate_knowledge_base(Path("/nonexistent/kb/path"), [])
        self.assertFalse(res.is_valid)
        self.assertTrue(any("does not exist" in e for e in res.errors))

    def test_document_validation_success(self):
        kb_root = Path(__file__).resolve().parent.parent.parent / "knowledge-base"
        res = validate_documents([self.valid_doc], kb_root)
        self.assertTrue(res.is_valid)

    def test_document_validation_duplicate_fault_id(self):
        kb_root = Path(__file__).resolve().parent.parent.parent / "knowledge-base"
        doc_dup = Document(
            document_id="FAULT-001",
            title="Another Fault with Duplicate ID",
            document_type="fault",
            source="faults/bearing-overheating.md",
            category="mechanical",
            equipment="motor",
            severity="high",
            sensors=["temperature"],
            content="Duplicate ID content"
        )
        res = validate_documents([self.valid_doc, doc_dup], kb_root)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Duplicate fault ID" in e for e in res.errors))

    def test_document_validation_missing_required_fields(self):
        kb_root = Path(__file__).resolve().parent.parent.parent / "knowledge-base"
        invalid_doc = Document(
            document_id="",
            title="",
            document_type="fault",
            source="faults/bearing-overheating.md",
            category=None,
            equipment=None,
            severity=None,
            sensors=[],
            content=""
        )
        res = validate_documents([invalid_doc], kb_root)
        self.assertFalse(res.is_valid)
        self.assertGreater(len(res.errors), 0)

    def test_chunk_validation_success(self):
        res = validate_chunks([self.valid_chunk], [self.valid_doc])
        self.assertTrue(res.is_valid)

    def test_chunk_validation_duplicate_chunk_id(self):
        chunk2 = Chunk(
            chunk_id="FAULT-001_chunk_001",  # Same ID!
            document_id="FAULT-001",
            document_type="fault",
            source="faults/bearing-overheating.md",
            chunk_index=1,
            title="Bearing Overheating",
            category="mechanical",
            equipment="motor",
            severity="high",
            sensors=["temperature"],
            text="Second chunk text",
            token_estimate=50
        )
        res = validate_chunks([self.valid_chunk, chunk2], [self.valid_doc])
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Duplicate chunk_id" in e for e in res.errors))

    def test_chunk_validation_discontinuous_index(self):
        chunk_bad_idx = Chunk(
            chunk_id="FAULT-001_chunk_003",
            document_id="FAULT-001",
            document_type="fault",
            source="faults/bearing-overheating.md",
            chunk_index=5,  # Skipped 1, 2, 3, 4!
            title="Bearing Overheating",
            category="mechanical",
            equipment="motor",
            severity="high",
            sensors=["temperature"],
            text="Third chunk text",
            token_estimate=50
        )
        res = validate_chunks([self.valid_chunk, chunk_bad_idx], [self.valid_doc])
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Discontinuous chunk_index" in e for e in res.errors))

    def test_chunk_validation_empty_text(self):
        empty_chunk = Chunk(
            chunk_id="FAULT-001_chunk_002",
            document_id="FAULT-001",
            document_type="fault",
            source="faults/bearing-overheating.md",
            chunk_index=1,
            title="Bearing Overheating",
            category="mechanical",
            equipment="motor",
            severity="high",
            sensors=["temperature"],
            text="   ",  # whitespace only
            token_estimate=0
        )
        res = validate_chunks([self.valid_chunk, empty_chunk], [self.valid_doc])
        self.assertFalse(res.is_valid)
        self.assertTrue(any("empty text" in e for e in res.errors))


if __name__ == "__main__":
    unittest.main()
