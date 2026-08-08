from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.cv_analyzer import CVAnalyzer
from app.services.cv_tailor import CVTailor

import pdfplumber
import io


router = APIRouter()

analyzer = CVAnalyzer()
tailor = CVTailor()


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
async def upload_cv(
    file: UploadFile = File(...)
):
    """
    Endpoint para subir CV en PDF y analizarlo.
    """

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    try:

        file_bytes = await file.read()

        extracted_text = extract_text_from_pdf(
            file_bytes
        )

        if not extracted_text:

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        analysis = analyzer.analyze(
            extracted_text
        )

        return {
            "message": "CV uploaded and analyzed successfully",
            "filename": file.filename,
            "analysis": analysis
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/cv/match")
async def match_cv(
    file: UploadFile = File(...),
    job_text: str = Form(...)
):
    """
    Compara las skills del CV con una oferta.
    """

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    try:

        file_bytes = await file.read()

        extracted_text = extract_text_from_pdf(
            file_bytes
        )

        if not extracted_text:

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        analysis = analyzer.analyze(
            extracted_text
        )

        result = analyzer.match_with_job(
            cv_skills=analysis["skills"],
            job_text=job_text
        )

        return {
            "analysis": analysis,
            "match": result
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/cv/tailor")
async def tailor_cv(
    file: UploadFile = File(...),
    job_text: str = Form(...)
):
    """
    Adapta un CV a una oferta utilizando Ollama.

    El sistema:
    1. Analiza el CV.
    2. Compara el CV con la oferta.
    3. Envía CV + oferta + gaps a Ollama.
    4. Genera un CV adaptado.
    5. Vuelve a calcular ATS y match.
    """

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    if not job_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description is required"
        )

    try:

        file_bytes = await file.read()

        extracted_text = extract_text_from_pdf(
            file_bytes
        )

        if not extracted_text:

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        result = await tailor.tailor(
            cv_text=extracted_text,
            job_text=job_text,
        )

        return {
            "message": "CV tailored successfully",
            "filename": file.filename,
            "result": result,
        }

    except HTTPException:
        raise

    except Exception as e:

        print("CV TAILOR ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"CV tailoring failed: {str(e)}"
        )
