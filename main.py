from fastapi import FastAPI
from app.api.upload import router
from contextlib import asynccontextmanager
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.parser import PDFParser
from app.ingestion.chunker import Chunker
from app.ingestion.embedder import Embedder
from app.ingestion.store import VectorStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时执行的代码
    app.state.pipeline = IngestionPipeline(parser=PDFParser(), chunker=Chunker(300, 30), embedder=Embedder(), store=VectorStore())
    yield
    # 在应用关闭时执行的代码

app = FastAPI(lifespan=lifespan)

app.include_router(router)

def main():
    print("Hello from legal-doc-qa!")


if __name__ == "__main__":
    main()
