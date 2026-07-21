"""
rag/pipeline.py — the RAG pipeline: retrieve relevant context, build a
grounded prompt, and generate an answer with Gemma 4.

This is the plain-RAG stage of the project (no agent/tool-calling yet —
that's the next layer, built on top of this).
"""

import config
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.generator import OllamaGenerator


def format_context(hits):
    """Turn retrieved chunks into a labeled context block for the prompt."""
    if not hits:
        return "(No relevant context found in the knowledge base.)"

    blocks = []
    for i, hit in enumerate(hits, start=1):
        blocks.append(f"[Source {i}: {hit['source']}]\n{hit['text']}")
    return "\n\n".join(blocks)


class RAGPipeline:
    def __init__(self, top_k=None):
        # Shared embedder instance so the model is only loaded once.
        embedder = Embedder()
        store = VectorStore()

        self.retriever = Retriever(embedder=embedder, store=store)
        self.generator = OllamaGenerator()
        self.top_k = top_k or config.TOP_K_DEFAULT

    def answer(self, query, top_k=None, return_sources=True):
        """
        Run the full RAG flow for a single query.

        Returns a dict: {"answer": str, "sources": [...], "context_used": str}
        """
        hits = self.retriever.retrieve(query, top_k=top_k or self.top_k)
        context = format_context(hits)

        user_message = (
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer using only the context above."
        )

        answer_text = self.generator.generate(
            system_prompt=config.SYSTEM_PROMPT,
            user_message=user_message,
        )

        result = {"answer": answer_text}
        if return_sources:
            result["sources"] = [
                {"source": h["source"], "distance": round(h["distance"], 4)}
                for h in hits
            ]
            result["context_used"] = context
        return result
