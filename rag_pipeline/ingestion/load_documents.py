"""
ingestion/load_documents.py — extracts text from PDF documents (SOPs,
policies, glossary, FAQ) so they can be chunked and embedded.
"""

import os
from pypdf import PdfReader


def load_pdf_text(filepath):
    """Extract all text from a single PDF, page by page."""
    reader = PdfReader(filepath)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(text)
    return "\n\n".join(pages_text)


def load_all_documents(docs_dir):
    """
    Load every PDF in `docs_dir`.

    Returns a list of dicts: {"source": filename, "text": full_extracted_text}
    """
    documents = []
    if not os.path.isdir(docs_dir):
        return documents

    for filename in sorted(os.listdir(docs_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        filepath = os.path.join(docs_dir, filename)
        try:
            text = load_pdf_text(filepath)
        except Exception as e:
            print(f"  [warn] Failed to read {filename}: {e}")
            continue
        if text.strip():
            documents.append({"source": filename, "text": text})
    return documents
