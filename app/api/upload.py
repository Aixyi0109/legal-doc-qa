from fastapi import APIRouter, UploadFile, File, Request
from pathlib import Path

router = APIRouter()
UPLOAD_DIR = Path("data/uploaded")


@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    content = await file.read()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        f.write(content)
    pipeline = request.app.state.pipeline
    result = pipeline.ingest(save_path)
    return {
        "filename": file.filename,
        "pages": result["pages"],
        "chunks": result["chunks"]
    }
