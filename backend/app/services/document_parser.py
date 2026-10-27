"""
Document text extraction service.
Supports PDF (via PyPDF2), plain text, and Markdown.
Returns a list of text chunks ready for indexing.
"""

import os
from typing import List


CHUNK_SIZE = 800   # characters
CHUNK_OVERLAP = 100


def parse_document(file_path: str, ext: str) -> List[str]:
    """Extract text from file and split into overlapping chunks."""
    text = _extract_text(file_path, ext)
    if not text or not text.strip():
        raise ValueError("No readable text could be extracted from the document.")
    return _chunk_text(text)


def _extract_text(file_path: str, ext: str) -> str:
    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def _extract_pdf(file_path: str) -> str:
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF parsing. Install it with: pip install PyPDF2")

    text_parts = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks of roughly CHUNK_SIZE characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks
