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