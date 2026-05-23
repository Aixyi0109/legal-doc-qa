from pathlib import Path
from app.ingestion.parser import PDFParser

PDF_PATH = Path("data/民法典.pdf")


def test_parse_returns_list():
    parser = PDFParser()
    assert isinstance(parser.parse(PDF_PATH), list)


def test_parse_page_count():
    parser = PDFParser()
    assert len(parser.parse(PDF_PATH)) == 176


def test_parse_page_has_fields():
    parser = PDFParser()
    page = parser.parse(PDF_PATH)[0]
    assert "page" in page
    assert "text" in page
