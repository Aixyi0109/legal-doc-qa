from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-m3')

    def embed(self, chunks: list[dict]) -> list[dict]:
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(texts).tolist()
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]
        return chunks
    
    def embed_query(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()