import os
from fastapi import APIRouter, UploadFile, File

from app.services.cv_parser import extract_text_from_pdf

router = APIRouter(prefix="/cv", tags=["CV"])


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_cv(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)

    return {
        "filename": file.filename,
        "extracted_text": text,
        "length": len(text)
    }
