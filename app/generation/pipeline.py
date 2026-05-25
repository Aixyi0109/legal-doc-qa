from .generator import Generator
from app.retrieval.retriever import Retriever

class RAGPipeline:
    def __init__(self, retriever: "Retriever", generator: "Generator"):
        self.retriever = retriever
        self.generator = generator

    def query(self, query: str, source_file: str) -> dict:
        retrieved_chunks = self.retriever.retrieve(query, source_file=source_file)
        answer = self.generator.generate(query, retrieved_chunks)
        return {"answer": answer, "sources": retrieved_chunks}
    
    def query_stream(self, query: str, source_file: str):
        retrieved_chunks = self.retriever.retrieve(query, source_file=source_file)
        for token in self.generator.generate_stream(query, retrieved_chunks):
            yield {"type": "token", "data": token}
        yield {"type": "sources", "data": retrieved_chunks}
    