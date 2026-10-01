"""
Section-aware Markdown chunking engine for P6 Document Ingestion.
Preserves Markdown headings, tables, bullet lists, and semantic boundaries.
Produces structured Chunk objects with document metadata and configurable token targets.
"""

import re
from typing import List, Tuple, Optional
from models import Document, Chunk


class MarkdownChunker:
    """
    Section-aware Markdown chunker.
    Splits documents into coherent chunks based on Markdown headings and paragraphs
    while maintaining document context, configurable chunk size, and overlap.
    """

    def __init__(
        self,
        chunk_size_tokens: int = 800,
        chunk_overlap_tokens: int = 100,
        tokens_per_word: float = 1.33
    ):
        """
        Initialize the Markdown chunker.

        :param chunk_size_tokens: Target maximum tokens per chunk (default 800).
        :param chunk_overlap_tokens: Target token overlap between adjacent chunks (default 100).
        :param tokens_per_word: Ratio of tokens per word for English technical prose (default 1.33).
        """
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens
        self.tokens_per_word = tokens_per_word

        # Approximate word limits based on token conversion
        self.max_words = max(5, int(chunk_size_tokens / tokens_per_word))
        self.overlap_words = max(1, int(chunk_overlap_tokens / tokens_per_word))

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from whitespace-delimited word count."""
        words = len(text.split())
        return int(words * self.tokens_per_word)

    def split_into_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Splits Markdown text into semantic sections based on level-2 headings (## ).
        Returns a list of (heading, section_text) tuples.
        """
        lines = text.split("\n")
        sections: List[Tuple[str, str]] = []
        current_heading = ""
        current_lines: List[str] = []

        for line in lines:
            if re.match(r"^##\s+", line):
                if current_lines:
                    content = "\n".join(current_lines).strip()
                    if content:
                        sections.append((current_heading, content))
                    current_lines = []
                current_heading = line.strip()
                current_lines.append(line)
            else:
                current_lines.append(line)

        if current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                sections.append((current_heading, content))

        return sections

    def _split_oversized_block(self, heading: str, block_text: str) -> List[str]:
        """
        Safely splits a single section that exceeds max_words by paragraph or line boundaries.
        Ensures each piece maintains heading context.
        """
        paragraphs = block_text.split("\n\n")
        sub_chunks: List[str] = []
        curr_paras: List[str] = []
        curr_words = 0

        for para in paragraphs:
            para_words = len(para.split())
            if curr_words + para_words <= self.max_words or not curr_paras:
                curr_paras.append(para)
                curr_words += para_words
            else:
                sub_chunks.append("\n\n".join(curr_paras).strip())
                curr_paras = [para]
                curr_words = para_words

        if curr_paras:
            sub_chunks.append("\n\n".join(curr_paras).strip())

        # Ensure each sub-chunk includes the section heading if not present
        result = []
        for sc in sub_chunks:
            if heading and not sc.startswith(heading) and not sc.startswith("#"):
                sc = f"{heading}\n\n{sc}"
            result.append(sc)

        return result

    def chunk_document(self, doc: Document) -> List[Chunk]:
        """
        Chunks a Document into a list of Chunk objects.
        If the entire document fits within max_words, a single chunk is returned.
        Otherwise, section-aware grouping with overlap is applied.
        """
        content = doc.content.strip()
        words = content.split()

        # Case 1: Entire document fits comfortably within chunk_size_tokens
        if len(words) <= self.max_words:
            chunk = Chunk(
                chunk_id=f"{doc.document_id}_chunk_001",
                document_id=doc.document_id,
                document_type=doc.document_type,
                source=doc.source,
                chunk_index=0,
                title=doc.title,
                category=doc.category,
                equipment=doc.equipment,
                severity=doc.severity,
                sensors=doc.sensors,
                text=content,
                section_heading=None,
                token_estimate=self.estimate_tokens(content)
            )
            return [chunk]

        # Case 2: Document exceeds chunk_size_tokens -> split into semantic sections
        raw_sections = self.split_into_sections(content)

        # Break any individual section that is larger than max_words
        processed_sections: List[Tuple[str, str]] = []
        for heading, body in raw_sections:
            body_words = len(body.split())
            if body_words > self.max_words:
                sub_blocks = self._split_oversized_block(heading, body)
                for sb in sub_blocks:
                    processed_sections.append((heading, sb))
            else:
                processed_sections.append((heading, body))

        # Group sections into chunks respecting max_words and overlap_words
        raw_chunks: List[str] = []
        current_group: List[Tuple[str, str]] = []
        current_words = 0

        for heading, body in processed_sections:
            body_words = len(body.split())
            if current_words + body_words <= self.max_words or not current_group:
                current_group.append((heading, body))
                current_words += body_words
            else:
                # Finalize current group
                chunk_text = "\n\n".join(b for _, b in current_group).strip()
                raw_chunks.append(chunk_text)

                # Compute overlap from end of current group
                overlap_group: List[Tuple[str, str]] = []
                overlap_accum = 0
                for h, b in reversed(current_group):
                    bw = len(b.split())
                    if overlap_accum + bw <= self.overlap_words:
                        overlap_group.insert(0, (h, b))
                        overlap_accum += bw
                    else:
                        break

                current_group = overlap_group + [(heading, body)]
                current_words = sum(len(b.split()) for _, b in current_group)

        if current_group:
            chunk_text = "\n\n".join(b for _, b in current_group).strip()
            raw_chunks.append(chunk_text)

        # Construct final Chunk objects with title context
        title_prefix = f"# {doc.title}"
        chunks: List[Chunk] = []

        for index, raw_text in enumerate(raw_chunks):
            # Prepend title context if the chunk doesn't start with a level-1 heading
            text_to_use = raw_text
            if not text_to_use.startswith("# "):
                text_to_use = f"{title_prefix}\n\n{text_to_use}"

            chunk_id = f"{doc.document_id}_chunk_{index + 1:03d}"
            chunk = Chunk(
                chunk_id=chunk_id,
                document_id=doc.document_id,
                document_type=doc.document_type,
                source=doc.source,
                chunk_index=index,
                title=doc.title,
                category=doc.category,
                equipment=doc.equipment,
                severity=doc.severity,
                sensors=doc.sensors,
                text=text_to_use,
                section_heading=None,
                token_estimate=self.estimate_tokens(text_to_use)
            )
            chunks.append(chunk)

        return chunks
