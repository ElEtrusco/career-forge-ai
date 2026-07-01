from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.cv_analyzer import CVAnalyzer
import pdfplumber
import io

router = APIRouter()

analyzer = CVAnalyzer()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extrae texto de un PDF en memoria.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)

        text = ""

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text.strip()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting PDF text: {str(e)}"
        )


@router.post("/cv/upload")
async def upload_cv(file: UploadFile = File(...)):
    """
    Endpoint para subir CV en PDF y analizarlo con el CV Intelligence Engine.
    """

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    try:
        file_bytes = await file.read()

        # 1. Extraer texto del PDF
        extracted_text = extract_text_from_pdf(file_bytes)

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        # 2. Analizar CV con IA engine
        analysis = analyzer.analyze(extracted_text)

        return {
            "message": "CV uploaded and analyzed successfully",
            "filename": file.filename,
            "analysis": analysis
        }

    except HTTPException as he:
        raise he

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )