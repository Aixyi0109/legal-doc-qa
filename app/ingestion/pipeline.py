from . import chunker, embedder, parser, store
from pathlib import Path


class IngestionPipeline:
    def __init__(self, chunker: "Chunker", embedder: "Embedder", parser: "PDFParser", store: "VectorStore"):
        self.chunker = chunker
        self.embedder = embedder
        self.parser = parser
        self.store = store

    def ingest(self, file_path: Path):
        file_path = Path(file_path)

        # Step 1: Parse the document
        parsed_content = self.parser.parse(file_path)

        # Step 2: Chunk the parsed content
        chunks = self.chunker.chunk(parsed_content)
        for chunk in chunks:
            chunk["source_file"] = file_path.name

        # Step 3: Embed the chunks
        embeddings = self.embedder.embed(chunks)

        # Step 4: Store the embeddings and associated metadata
        self.store.add(embeddings)