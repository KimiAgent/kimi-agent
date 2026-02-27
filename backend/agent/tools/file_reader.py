"""
File Reader Tool — extracts text from PDF, DOCX, and plain text files.
"""

import os
from pathlib import Path
from typing import Tuple


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}
MAX_CHARS = 50_000  # trim very long docs


def extract_text(file_path: str) -> Tuple[str, str]:
    """
    Extract text from a file.

    Returns:
        (text, detected_type) — e.g. ("Hello world...", "pdf")

    Raises:
        ValueError if the file type is unsupported.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    if ext == ".pdf":
        return _read_pdf(path), "pdf"
    elif ext == ".docx":
        return _read_docx(path), "docx"
    else:
        return _read_text(path), ext.lstrip(".")


def _read_pdf(path: Path) -> str:
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(path))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text[:MAX_CHARS]
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install PyMuPDF")


def _read_docx(path: Path) -> str:
    try:
        from docx import Document

        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return text[:MAX_CHARS]
    except ImportError:
        raise RuntimeError("python-docx not installed. Run: pip install python-docx")


def _read_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()[:MAX_CHARS]


def summarize_prompt(text: str, file_name: str) -> str:
    """Build a prompt asking the agent to summarize the document."""
    return (
        f"The user has uploaded a file named '{file_name}'. "
        f"Here are its contents:\n\n---\n{text}\n---\n\n"
        "Please provide a concise summary and highlight the key points."
    )
