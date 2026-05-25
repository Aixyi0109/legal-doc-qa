from app.ingestion.pipeline import IngestionPipeline
from app.ingestion import chunker, embedder, parser, store

if __name__ == "__main__":
    pipeline = IngestionPipeline(
        chunker=chunker.Chunker(300, 30),
        embedder=embedder.Embedder(),
        parser=parser.PDFParser(),
        store=store.VectorStore()
    )
    pipeline.ingest("data/民法典.pdf")