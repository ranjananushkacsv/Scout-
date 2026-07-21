"""
ingestion/build_index.py — the main ingestion entrypoint.

Run this whenever you add/update documents in data/documents or
data/tabular. It rebuilds the vector store from scratch.

Usage:
    python -m ingestion.build_index
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from .load_documents import load_all_documents
from .load_tabular import load_all_tabular
from .chunker import chunk_text
from rag.embedder import Embedder
from rag.vector_store import VectorStore


def build_chunks():
    """
    Load every source (PDFs + CSVs), split PDFs into overlapping chunks,
    and return a flat list of {"id", "text", "source"} records ready to embed.
    """
    records = []

    print("Loading PDF documents...")
    documents = load_all_documents(config.DOCS_DIR)
    print(f"  Found {len(documents)} PDF(s)")

    for doc in documents:
        chunks = chunk_text(
            doc["text"],
            chunk_size=config.CHUNK_SIZE_CHARS,
            overlap=config.CHUNK_OVERLAP_CHARS,
        )
        for i, chunk in enumerate(chunks):
            records.append({
                "id": f"{doc['source']}::chunk_{i}",
                "text": chunk,
                "source": doc["source"],
            })
        print(f"  {doc['source']}: {len(chunks)} chunks")

    print("\nLoading tabular data (CSV rows as cards)...")
    tabular_records = load_all_tabular(config.TABULAR_DIR)
    print(f"  Found {len(tabular_records)} row(s) across CSV files")

    for i, rec in enumerate(tabular_records):
        records.append({
            "id": f"{rec['source']}::row_{i}",
            "text": rec["text"],
            "source": rec["source"],
        })

    return records


def main():
    records = build_chunks()

    if not records:
        print("\nNo data found. Add PDFs to data/documents/ and/or CSVs to data/tabular/ first.")
        return

    print(f"\nTotal chunks/cards to index: {len(records)}")

    embedder = Embedder()
    store = VectorStore()

    print("\nResetting existing collection (clean rebuild)...")
    store.reset()

    print("Embedding and indexing...")
    batch_size = 64
    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]
        texts = [r["text"] for r in batch]
        ids = [r["id"] for r in batch]
        metadatas = [{"source": r["source"]} for r in batch]

        embeddings = embedder.embed_documents(texts)
        store.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    print(f"\nDone. Vector store now contains {store.count()} items at: {config.CHROMA_DIR}")


if __name__ == "__main__":
    main()
