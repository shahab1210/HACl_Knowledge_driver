"""
Validation module for P6 Document Ingestion.
Enforces structural, semantic, and metadata integrity across discovered documents and generated chunks.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple
from models import Document, Chunk


class ValidationResult:
    """Encapsulates the outcome of the ingestion validation checks."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}

    @property
    def is_valid(self) -> bool:
        """Returns True if no validation errors were encountered."""
        return len(self.errors) == 0

    def add_error(self, message: str):
        """Record a validation failure error."""
        self.errors.append(message)

    def add_warning(self, message: str):
        """Record a validation warning."""
        self.warnings.append(message)


def validate_knowledge_base(kb_root: Path, discovered_files: List[Path]) -> ValidationResult:
    """
    Validates that the knowledge base directory exists and contains expected files.
    """
    result = ValidationResult()

    if not kb_root.exists():
        result.add_error(f"Knowledge base directory does not exist: {kb_root}")
        return result

    if not kb_root.is_dir():
        result.add_error(f"Knowledge base path is not a directory: {kb_root}")
        return result

    if not discovered_files:
        result.add_error(f"No Markdown files discovered under knowledge base directory: {kb_root}")
        return result

    return result


def validate_documents(documents: List[Document], kb_root: Path) -> ValidationResult:
    """
    Validates parsed Document objects for metadata integrity, required fields, and fault IDs.
    """
    result = ValidationResult()
    fault_ids = set()
    fault_count = 0
    sensor_count = 0
    procedure_count = 0
    doc_count = 0

    for doc in documents:
        # Check source file existence
        full_path = kb_root / doc.source
        if not full_path.exists():
            result.add_error(f"Source file does not exist on disk: {full_path}")

        # Check document ID
        if not doc.document_id or not doc.document_id.strip():
            result.add_error(f"Document missing required document_id (source: {doc.source})")

        # Check document type
        if doc.document_type not in ("fault", "sensor", "procedure", "documentation", "general"):
            result.add_error(f"Invalid document_type '{doc.document_type}' for document: {doc.document_id}")

        # Check title
        if not doc.title or not doc.title.strip():
            result.add_error(f"Document missing title: {doc.document_id}")

        # Check content
        if not doc.content or not doc.content.strip():
            result.add_error(f"Document has empty content: {doc.document_id}")

        # Type-specific validation
        if doc.document_type == "fault":
            fault_count += 1
            if not doc.document_id.startswith("FAULT-"):
                result.add_error(f"Fault document ID must start with 'FAULT-': {doc.document_id}")
            if doc.document_id in fault_ids:
                result.add_error(f"Duplicate fault ID detected: {doc.document_id}")
            fault_ids.add(doc.document_id)

            if not doc.category:
                result.add_error(f"Fault document missing category: {doc.document_id}")
            if not doc.equipment:
                result.add_error(f"Fault document missing equipment: {doc.document_id}")
            if not doc.severity:
                result.add_error(f"Fault document missing severity: {doc.document_id}")
            if not doc.sensors:
                result.add_error(f"Fault document has empty sensors list: {doc.document_id}")

        elif doc.document_type == "sensor":
            sensor_count += 1
            if not doc.sensors:
                result.add_error(f"Sensor document has empty sensors list: {doc.document_id}")

        elif doc.document_type == "procedure":
            procedure_count += 1

        elif doc.document_type == "documentation":
            doc_count += 1

    result.stats = {
        "total_documents": len(documents),
        "fault_documents": fault_count,
        "sensor_documents": sensor_count,
        "procedure_documents": procedure_count,
        "documentation_documents": doc_count,
        "unique_fault_ids": len(fault_ids)
    }

    return result


def validate_chunks(chunks: List[Chunk], documents: List[Document]) -> ValidationResult:
    """
    Validates generated Chunk objects:
    - Every chunk has unique chunk_id
    - Every chunk has source, document_id, document_type, text
    - No empty chunks
    - Chunk indexing continuous starting at 0 for each document
    - No duplicate chunk IDs
    """
    result = ValidationResult()

    if not chunks:
        result.add_error("No chunks were generated from the documents.")
        return result

    doc_ids = {doc.document_id for doc in documents}
    seen_chunk_ids = set()
    chunks_by_doc: Dict[str, List[Chunk]] = {}

    for chunk in chunks:
        # Check unique chunk_id
        if not chunk.chunk_id or not chunk.chunk_id.strip():
            result.add_error("Chunk has empty chunk_id")
        elif chunk.chunk_id in seen_chunk_ids:
            result.add_error(f"Duplicate chunk_id detected: {chunk.chunk_id}")
        seen_chunk_ids.add(chunk.chunk_id)

        # Check document_id association
        if not chunk.document_id:
            result.add_error(f"Chunk {chunk.chunk_id} missing document_id")
        elif chunk.document_id not in doc_ids:
            result.add_error(f"Chunk {chunk.chunk_id} references unknown document_id: {chunk.document_id}")

        # Check document_type
        if not chunk.document_type:
            result.add_error(f"Chunk {chunk.chunk_id} missing document_type")

        # Check source
        if not chunk.source:
            result.add_error(f"Chunk {chunk.chunk_id} missing source")

        # Check non-empty text
        if not chunk.text or not chunk.text.strip():
            result.add_error(f"Chunk {chunk.chunk_id} has empty text")

        # Group by document for ordering checks
        chunks_by_doc.setdefault(chunk.document_id, []).append(chunk)

    # Validate ordering and index continuity for each document
    for doc_id, doc_chunks in chunks_by_doc.items():
        doc_chunks.sort(key=lambda c: c.chunk_index)
        expected_index = 0
        for chunk in doc_chunks:
            if chunk.chunk_index != expected_index:
                result.add_error(
                    f"Discontinuous chunk_index in {doc_id}: expected {expected_index}, got {chunk.chunk_index}"
                )
            expected_index += 1

    result.stats = {
        "total_chunks": len(chunks),
        "unique_chunk_ids": len(seen_chunk_ids),
        "documents_with_chunks": len(chunks_by_doc)
    }

    return result
