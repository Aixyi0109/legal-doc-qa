from pathlib import Path
from pypdf import PdfReader
from unstructured.partition.pdf import partition_pdf


class PDFParser:
    def parse(self, file_path: Path) -> list[dict]:
        """返回 [{"page": 1, "text": "..."}, ...]"""
        reader = PdfReader(file_path)
        return [
            {"page": i + 1, "text": page.extract_text()}
            for i, page in enumerate(reader.pages)
        ]


class UnstructuredParser:
    def parse(self, file_path: Path) -> list[dict]:
        """返回 [{"page": 1, "text": "...", "category": "Title"}, ...]"""
        elements = partition_pdf(file_path)
        return [
            {"page": e.metadata.page_number, "text": e.text, "category": e.category}
            for e in elements
        ]
