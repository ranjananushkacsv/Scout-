"""
rag/embedder.py — wraps the local, free embedding model (BAAI/bge-small-en-v1.5)
used for both indexing document chunks and embedding user queries.

Loading the model is done once and reused (it's a few hundred MB, downloaded
once from Hugging Face on first run and cached locally after that).
"""

from sentence_transformers import SentenceTransformer

import config


class Embedder:
    def __init__(self, model_name=None):
        self.model_name = model_name or config.EMBEDDING_MODEL_NAME
        print(f"Loading embedding model: {self.model_name} (first run downloads it, then it's cached)")
        self.model = SentenceTransformer(self.model_name)

    def embed_documents(self, texts):
        """Embed a list of document chunks (no instruction prefix)."""
        return self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True,
        ).tolist()

    def embed_query(self, query):
        """Embed a single user query. bge models want a search-instruction prefix here."""
        prefixed = config.BGE_QUERY_PREFIX + query
        return self.model.encode(
            [prefixed],
            normalize_embeddings=True,
        )[0].tolist()
