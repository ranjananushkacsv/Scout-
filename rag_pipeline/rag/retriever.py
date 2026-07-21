"""
rag/retriever.py — given a user query, returns the most relevant chunks
from the vector store.
"""

from rag.embedder import Embedder
from rag.vector_store import VectorStore


class Retriever:
    def __init__(self, embedder=None, store=None):
        # Allow injecting shared instances (e.g. from the pipeline) to avoid
        # reloading the embedding model multiple times.
        self.embedder = embedder or Embedder()
        self.store = store or VectorStore()

    def retrieve(self, query, top_k=None):
        """
        Returns a list of hits: [{"text", "source", "distance"}, ...]
        sorted by relevance (most relevant first).
        """
        query_embedding = self.embedder.embed_query(query)
        return self.store.query(query_embedding, top_k=top_k)
