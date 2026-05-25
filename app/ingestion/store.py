import chromadb

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="legal_docs")

    def add(self, chunks: list[dict]):
        ids = [chunk["chunk_id"] for chunk in chunks]
        pages = [chunk["page"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        embeddings = [chunk["embedding"] for chunk in chunks]
        source_files = [chunk["source_file"] for chunk in chunks]
        chunk_indexes = [chunk["chunk_index"] for chunk in chunks]

        self.collection.add(
            ids=ids,
            metadatas=[{"page": page, "source_file": source_file, "chunk_index": chunk_index} for page, source_file, chunk_index in zip(pages, source_files, chunk_indexes)],
            documents=texts,
            embeddings=embeddings
        )
    
    def query(self, query_embedding: list[float], top_k: int = 5, source_file: str = None):
        kwargs = {"query_embeddings": [query_embedding], "n_results": top_k}
        if source_file:
            kwargs["where"] = {"source_file": source_file}
        results = self.collection.query(**kwargs)
        
        # 处理成list[dict]的格式
        return [
            {
                "id": id,
                "text": document,
                "page": metadata["page"],
                "source_file": metadata["source_file"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance    
            }
            for id, document, metadata, distance in zip(results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0])
        ]