"""
rag/vector_store.py — thin wrapper around ChromaDB (persistent, local,
free) for storing and querying embedded chunks.
"""

import chromadb
from chromadb.config import Settings

import config


class VectorStore:
    def __init__(self, persist_dir=None, collection_name=None):
        self.persist_dir = persist_dir or config.CHROMA_DIR
        self.collection_name = collection_name or config.COLLECTION_NAME

        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self):
        """Wipe the collection — useful when re-ingesting from scratch."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, ids, embeddings, documents, metadatas):
        """Upsert a batch of chunks into the collection."""
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, query_embedding, top_k=None):
        """
        Return the top_k most similar chunks to `query_embedding`.

        Returns a list of dicts: {"text": ..., "source": ..., "distance": ...}
        """
        top_k = top_k or config.TOP_K_DEFAULT
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        hits = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, dists):
            hits.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "distance": dist,
            })
        return hits

    def count(self):
        return self.collection.count()
