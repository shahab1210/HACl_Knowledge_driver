"""
Markdown and YAML front-matter parser for P6 Document Ingestion.
Extracts structured metadata, classifies document types, and normalizes text.
"""

import os
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from models import Document


def parse_yaml_fallback(yaml_text: str) -> Dict[str, Any]:
    """
    Lightweight fallback parser for YAML front-matter when PyYAML is not installed.
    Supports scalars, lists, and key-value pairs used in knowledge documents.
    """
    result: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_list: Optional[List[str]] = None

    for line in yaml_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue

        # Check for list item under current key
        list_match = re.match(r"^\s*-\s+(.*)$", line)
        if list_match and current_key:
            item = list_match.group(1).strip().strip("'\"")
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            current_list.append(item)
            continue

        # Check for key: value
        kv_match = re.match(r"^([a-zA-Z0-9_\-]+)\s*:\s*(.*)$", line)
        if kv_match:
            key = kv_match.group(1).strip()
            value = kv_match.group(2).strip()

            current_key = key
            current_list = None

            if value == "":
                # Could be starting a list on next lines
                result[key] = []
                current_list = result[key]
            else:
                # Strip quotes if string
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                result[key] = value

    return result


def extract_front_matter(raw_text: str) -> Tuple[Dict[str, Any], str]:
    """
    Extracts YAML front matter enclosed between triple dashes ('---') and returns
    the parsed metadata dictionary along with the remaining body text.
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.search(pattern, raw_text, flags=re.DOTALL)
    if not match:
        return {}, raw_text

    yaml_block = match.group(1)
    body = raw_text[match.end():]

    if HAS_YAML:
        try:
            metadata = yaml.safe_load(yaml_block) or {}
            if not isinstance(metadata, dict):
                metadata = {}
        except Exception:
            metadata = parse_yaml_fallback(yaml_block)
    else:
        metadata = parse_yaml_fallback(yaml_block)

    return metadata, body


def normalize_text(text: str) -> str:
    """
    Normalizes text while strictly preserving Markdown headings, tables, bullet lists,
    and technical math/symbols:
    - Normalizes Windows CRLF to standard LF.
    - Trims trailing whitespace from each line.
    - Replaces sequences of three or more newlines with two newlines (single blank line).
    - Trims leading and trailing whitespace of the whole text.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Clean trailing whitespace on each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_first_heading(text: str, default: str = "") -> str:
    """Extracts the title from the first level-1 Markdown heading (# Heading)."""
    match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return default


def infer_metadata(
    rel_path: Path,
    raw_front_matter: Dict[str, Any],
    body_text: str
) -> Dict[str, Any]:
    """
    Infers document metadata based on directory structure, file naming conventions,
    and any existing front matter.
    """
    parent_dir = rel_path.parent.name
    filename = rel_path.name
    stem = rel_path.stem

    # Detect document type from parent directory
    if parent_dir == "faults":
        doc_type = "fault"
    elif parent_dir == "sensors":
        doc_type = "sensor"
    elif parent_dir == "procedures":
        doc_type = "procedure"
    elif filename.lower() == "readme.md":
        doc_type = "documentation"
    else:
        doc_type = "general"

    title_from_heading = extract_first_heading(body_text, default=stem.replace("-", " ").title())

    if doc_type == "fault":
        doc_id = raw_front_matter.get("id") or f"FAULT-{stem.upper()}"
        title = raw_front_matter.get("title") or title_from_heading
        category = raw_front_matter.get("category")
        equipment = raw_front_matter.get("equipment")
        severity = raw_front_matter.get("severity")
        sensors = raw_front_matter.get("sensors") or []
    elif doc_type == "sensor":
        doc_id = f"SENSOR-{stem.upper()}"
        title = title_from_heading
        category = "instrumentation"
        equipment = "sensor"
        severity = None
        sensors = [stem.lower()]
    elif doc_type == "procedure":
        doc_id = f"PROC-{stem.upper()}"
        title = title_from_heading
        category = "procedure"
        # Infer equipment from filename
        if "motor" in stem:
            equipment = "motor"
            sensors = ["temperature", "vibration", "current"]
        elif "pump" in stem:
            equipment = "pump"
            sensors = ["pressure", "vibration", "current"]
        else:
            equipment = "general"
            sensors = ["temperature", "vibration", "current", "pressure", "humidity"]
        severity = None
    else:  # documentation / general
        doc_id = f"DOC-{stem.upper()}"
        title = title_from_heading
        category = "documentation"
        equipment = None
        severity = None
        sensors = []

    return {
        "document_id": doc_id,
        "title": title,
        "document_type": doc_type,
        "category": category,
        "equipment": equipment,
        "severity": severity,
        "sensors": sensors,
    }


def parse_markdown_file(file_path: Path, kb_root: Path) -> Document:
    """
    Parses a single Markdown file into a structured Document model.
    """
    rel_path = file_path.relative_to(kb_root)
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    raw_front_matter, body = extract_front_matter(raw_content)
    cleaned_content = normalize_text(body)

    inferred = infer_metadata(rel_path, raw_front_matter, cleaned_content)

    return Document(
        document_id=inferred["document_id"],
        title=inferred["title"],
        document_type=inferred["document_type"],
        source=str(rel_path),
        category=inferred["category"],
        equipment=inferred["equipment"],
        severity=inferred["severity"],
        sensors=inferred["sensors"],
        content=cleaned_content,
        metadata={**raw_front_matter, "source_file": str(rel_path)}
    )


def discover_documents(kb_root: Path, exclude_readme: bool = True) -> List[Path]:
    """
    Recursively discovers Markdown (*.md) files in the knowledge base directory.
    When exclude_readme is True, root-level README.md is excluded from diagnostic ingestion.
    """
    if not kb_root.exists() or not kb_root.is_dir():
        raise FileNotFoundError(f"Knowledge base directory does not exist: {kb_root}")

    md_files = sorted(kb_root.rglob("*.md"))

    if exclude_readme:
        # Exclude README.md at the root of the knowledge base
        md_files = [
            f for f in md_files
            if not (f.name.lower() == "readme.md" and f.parent.resolve() == kb_root.resolve())
        ]

    return md_files
