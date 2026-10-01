"""
Unit tests for P6 Parser module.
Tests YAML front matter parsing, fault metadata extraction, sensor/procedure classification,
text normalization, and empty/malformed handling.
"""

import sys
import unittest
from pathlib import Path

# Ensure ai/ingestion is in Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser import (
    extract_front_matter,
    parse_yaml_fallback,
    normalize_text,
    infer_metadata,
    parse_markdown_file,
    discover_documents
)


class TestParser(unittest.TestCase):

    def test_extract_front_matter_valid(self):
        content = """---
id: FAULT-001
title: Bearing Overheating
category: mechanical
equipment: motor
severity: high
sensors:
  - temperature
  - vibration
  - current
---
# Bearing Overheating
## Description
Bearing is hot.
"""
        meta, body = extract_front_matter(content)
        self.assertEqual(meta.get("id"), "FAULT-001")
        self.assertEqual(meta.get("title"), "Bearing Overheating")
        self.assertEqual(meta.get("category"), "mechanical")
        self.assertEqual(meta.get("equipment"), "motor")
        self.assertEqual(meta.get("severity"), "high")
        self.assertEqual(meta.get("sensors"), ["temperature", "vibration", "current"])
        self.assertIn("# Bearing Overheating", body)
        self.assertNotIn("---", body)

    def test_parse_yaml_fallback(self):
        yaml_text = """
id: FAULT-002
title: Bearing Wear
category: mechanical
equipment: motor
severity: high
sensors:
  - vibration
  - temperature
"""
        parsed = parse_yaml_fallback(yaml_text)
        self.assertEqual(parsed["id"], "FAULT-002")
        self.assertEqual(parsed["title"], "Bearing Wear")
        self.assertEqual(parsed["sensors"], ["vibration", "temperature"])

    def test_fault_metadata_extraction(self):
        rel_path = Path("faults/bearing-overheating.md")
        fm = {
            "id": "FAULT-001",
            "title": "Bearing Overheating",
            "category": "mechanical",
            "equipment": "motor",
            "severity": "high",
            "sensors": ["temperature", "vibration"]
        }
        body = "# Bearing Overheating\n\n## Description\nContent here."
        inferred = infer_metadata(rel_path, fm, body)

        self.assertEqual(inferred["document_id"], "FAULT-001")
        self.assertEqual(inferred["document_type"], "fault")
        self.assertEqual(inferred["category"], "mechanical")
        self.assertEqual(inferred["equipment"], "motor")
        self.assertEqual(inferred["severity"], "high")
        self.assertEqual(inferred["sensors"], ["temperature", "vibration"])

    def test_sensor_document_classification(self):
        rel_path = Path("sensors/temperature.md")
        body = "# Temperature Sensor in Industrial IoT\n\n## 1. What the Sensor Measures\nContent."
        inferred = infer_metadata(rel_path, {}, body)

        self.assertEqual(inferred["document_id"], "SENSOR-TEMPERATURE")
        self.assertEqual(inferred["document_type"], "sensor")
        self.assertEqual(inferred["category"], "instrumentation")
        self.assertEqual(inferred["equipment"], "sensor")
        self.assertIsNone(inferred["severity"])
        self.assertEqual(inferred["sensors"], ["temperature"])

    def test_procedure_document_classification(self):
        # Motor inspection
        rel_path_motor = Path("procedures/motor-inspection.md")
        body_motor = "# Electric Motor Inspection Checklist\n\n## Purpose\nInspect motor."
        inferred_motor = infer_metadata(rel_path_motor, {}, body_motor)

        self.assertEqual(inferred_motor["document_id"], "PROC-MOTOR-INSPECTION")
        self.assertEqual(inferred_motor["document_type"], "procedure")
        self.assertEqual(inferred_motor["equipment"], "motor")

        # Pump inspection
        rel_path_pump = Path("procedures/pump-inspection.md")
        body_pump = "# Centrifugal Pump Inspection Checklist\n\n## Purpose\nInspect pump."
        inferred_pump = infer_metadata(rel_path_pump, {}, body_pump)

        self.assertEqual(inferred_pump["document_id"], "PROC-PUMP-INSPECTION")
        self.assertEqual(inferred_pump["document_type"], "procedure")
        self.assertEqual(inferred_pump["equipment"], "pump")

    def test_markdown_cleaning_and_normalization(self):
        messy_text = "Line 1   \r\n\r\n\r\n\r\nLine 2 with spaces   \r\n\n\nLine 3"
        cleaned = normalize_text(messy_text)

        self.assertNotIn("\r", cleaned)
        self.assertNotIn("   \n", cleaned)
        self.assertNotIn("\n\n\n", cleaned)
        self.assertTrue(cleaned.startswith("Line 1"))
        self.assertTrue(cleaned.endswith("Line 3"))

    def test_empty_front_matter_handling(self):
        plain_md = "# Plain Document\n\nJust markdown without YAML front matter."
        meta, body = extract_front_matter(plain_md)
        self.assertEqual(meta, {})
        self.assertEqual(body.strip(), plain_md.strip())

    def test_discover_documents_excludes_kb_readme(self):
        kb_root = Path(__file__).resolve().parent.parent.parent / "knowledge-base"
        files = discover_documents(kb_root, exclude_readme=True)
        filenames = [f.name for f in files]

        self.assertNotIn("README.md", filenames)
        self.assertEqual(len(files), 18)


if __name__ == "__main__":
    unittest.main()
