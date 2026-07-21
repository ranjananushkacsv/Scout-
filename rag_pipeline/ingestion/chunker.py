"""
ingestion/chunker.py — splits long text into overlapping chunks for embedding.

A simple, dependency-free recursive splitter: tries to break on paragraph
boundaries first, then sentences, then hard character limits as a fallback.
This avoids cutting a sentence in half mid-idea wherever possible.
"""

import re


def _split_on(text, separator):
    return [p for p in text.split(separator) if p.strip()]


def chunk_text(text, chunk_size=1200, overlap=200):
    """
    Split `text` into chunks of roughly `chunk_size` characters, with
    `overlap` characters repeated between consecutive chunks so context
    isn't lost at the boundary.

    Returns a list of strings.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    # Prefer splitting on paragraphs, then sentences, as building blocks.
    paragraphs = _split_on(text, "\n\n")
    if len(paragraphs) == 1:
        # No paragraph breaks found — fall back to sentence splitting.
        paragraphs = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current = ""

    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
                # start next chunk with the overlap tail of the previous one
                tail = current[-overlap:] if overlap < len(current) else current
                current = (tail + "\n\n" + para).strip()
            else:
                # a single paragraph longer than chunk_size — hard split it
                for i in range(0, len(para), chunk_size - overlap):
                    chunks.append(para[i:i + chunk_size].strip())
                current = ""

    if current:
        chunks.append(current.strip())

    return [c for c in chunks if c]
