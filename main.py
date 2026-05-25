from fastapi import FastAPI
from app.api.upload import router
from app.api.query import router as query_router
from contextlib import asynccontextmanager
from app.ingestion.pipeline import IngestionPipeline
from app.generation.pipeline import RAGPipeline
from app.ingestion.parser import PDFParser
from app.ingestion.chunker import Chunker
from app.ingestion.embedder import Embedder
from app.ingestion.store import VectorStore
from app.generation import generator
from app.retrieval import retriever

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时执行的代码
    app.state.pipeline = IngestionPipeline(parser=PDFParser(), chunker=Chunker(300, 30), embedder=Embedder(), store=VectorStore())
    app.state.retriever = retriever.Retriever(embedder=app.state.pipeline.embedder, vector_store=app.state.pipeline.store)
    app.state.rag_pipeline = RAGPipeline(retriever=app.state.retriever, generator=generator.Generator())

    yield
    # 在应用关闭时执行的代码

app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.include_router(query_router)
def main():
    print("Hello from legal-doc-qa!")


if __name__ == "__main__":
    main()
