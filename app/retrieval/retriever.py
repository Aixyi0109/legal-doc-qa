from app.ingestion.embedder import Embedder
from app.ingestion.store import VectorStore


class Retriever:
    def __init__(self, embedder: "Embedder", vector_store: "VectorStore"):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5, source_file: str = None) -> list[dict]:
        query_embedding = self.embedder.embed_query(query)
        results = self.vector_store.query(query_embedding=query_embedding, top_k=top_k, source_file=source_file)
        return results