from fastapi import APIRouter, UploadFile, File
from pathlib import Path
from app.ingestion.parser import PDFParser

router = APIRouter()
UPLOAD_DIR = Path("data/uploaded")


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(content)
    parser = PDFParser()
    pages = parser.parse(save_path)
    return {
        "pages": len(pages),
        "preview": pages[0]["text"][:200] if pages else ""
    }
