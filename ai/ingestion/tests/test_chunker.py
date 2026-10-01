"""
Unit tests for P6 Chunker module.
Tests chunk generation, section preservation, chunk overlap, unique chunk IDs, and metadata propagation.
"""

import sys
import unittest
from pathlib import Path

# Ensure ai/ingestion is in Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Document
from chunker import MarkdownChunker


class TestChunker(unittest.TestCase):

    def setUp(self):
        self.sample_doc = Document(
            document_id="FAULT-001",
            title="Bearing Overheating",
            document_type="fault",
            source="faults/bearing-overheating.md",
            category="mechanical",
            equipment="motor",
            severity="high",
            sensors=["temperature", "vibration", "current"],
            content="""# Bearing Overheating

## Description
Bearing overheating occurs when operating temperature exceeds limits.

## Typical Symptoms
- Rapid temperature rise.
- Whining acoustic sound.

## Possible Causes
- Inadequate lubrication.
- Misalignment.

## Sensor Indicators
| Sensor | Reading | Note |
| --- | --- | --- |
| Temperature | High | Critical indicator |

## Recommended Checks
1. Check housing temp with pyrometer.
2. Inspect grease condition.

## Safety
- Thermal burn hazard.
- LOTO required.

## Related Faults
- FAULT-002: Bearing Wear
"""
        )

    def test_single_chunk_generation_when_small(self):
        # With large chunk size, small doc fits into single chunk
        chunker = MarkdownChunker(chunk_size_tokens=1000, chunk_overlap_tokens=100)
        chunks = chunker.chunk_document(self.sample_doc)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].chunk_id, "FAULT-001_chunk_001")
        self.assertEqual(chunks[0].chunk_index, 0)
        self.assertEqual(chunks[0].document_id, "FAULT-001")
        self.assertEqual(chunks[0].title, "Bearing Overheating")
        self.assertEqual(chunks[0].category, "mechanical")
        self.assertEqual(chunks[0].equipment, "motor")
        self.assertEqual(chunks[0].severity, "high")
        self.assertEqual(chunks[0].sensors, ["temperature", "vibration", "current"])
        self.assertIn("## Typical Symptoms", chunks[0].text)

    def test_multi_chunk_generation_with_small_chunk_size(self):
        # Configure small chunk size so splitting occurs
        chunker = MarkdownChunker(chunk_size_tokens=50, chunk_overlap_tokens=15)
        chunks = chunker.chunk_document(self.sample_doc)

        self.assertGreater(len(chunks), 1)
        # Verify continuous indexing starting at 0
        for i, chunk in enumerate(chunks):
            self.assertEqual(chunk.chunk_index, i)
            self.assertEqual(chunk.chunk_id, f"FAULT-001_chunk_{i+1:03d}")

    def test_unique_chunk_ids(self):
        chunker = MarkdownChunker(chunk_size_tokens=40, chunk_overlap_tokens=10)
        chunks = chunker.chunk_document(self.sample_doc)

        chunk_ids = [c.chunk_id for c in chunks]
        self.assertEqual(len(chunk_ids), len(set(chunk_ids)))

    def test_metadata_propagation_to_all_chunks(self):
        chunker = MarkdownChunker(chunk_size_tokens=50, chunk_overlap_tokens=15)
        chunks = chunker.chunk_document(self.sample_doc)

        for chunk in chunks:
            self.assertEqual(chunk.document_id, self.sample_doc.document_id)
            self.assertEqual(chunk.document_type, self.sample_doc.document_type)
            self.assertEqual(chunk.source, self.sample_doc.source)
            self.assertEqual(chunk.title, self.sample_doc.title)
            self.assertEqual(chunk.category, self.sample_doc.category)
            self.assertEqual(chunk.equipment, self.sample_doc.equipment)
            self.assertEqual(chunk.severity, self.sample_doc.severity)
            self.assertEqual(chunk.sensors, self.sample_doc.sensors)
            self.assertTrue(len(chunk.text.strip()) > 0)
            self.assertGreater(chunk.token_estimate, 0)

    def test_section_preservation(self):
        # Verify that section headings remain attached to their body
        chunker = MarkdownChunker(chunk_size_tokens=80, chunk_overlap_tokens=20)
        chunks = chunker.chunk_document(self.sample_doc)

        # In any chunk containing '## Recommended Checks', the checklist items follow
        found_checks = False
        for c in chunks:
            if "## Recommended Checks" in c.text:
                found_checks = True
                self.assertIn("Check housing temp", c.text)
        self.assertTrue(found_checks)

    def test_chunk_overlap_preserves_context(self):
        # Build document with distinct sections
        doc = Document(
            document_id="TEST-001",
            title="Test Doc",
            document_type="fault",
            source="test.md",
            category="test",
            equipment="test",
            severity="low",
            sensors=["test"],
            content="""# Test Doc

## Section Alpha
Alpha content detailed paragraph with sufficient words to force chunk boundary. Alpha alpha alpha.

## Section Beta
Beta content detailed paragraph with sufficient words. Beta beta beta beta beta.

## Section Gamma
Gamma content detailed paragraph with sufficient words. Gamma gamma gamma gamma gamma.
"""
        )
        chunker = MarkdownChunker(chunk_size_tokens=30, chunk_overlap_tokens=15)
        chunks = chunker.chunk_document(doc)

        self.assertGreater(len(chunks), 1)
        # All chunks should be non-empty and have document title prefix context
        for c in chunks:
            self.assertTrue(c.text.startswith("# Test Doc"))


if __name__ == "__main__":
    unittest.main()
