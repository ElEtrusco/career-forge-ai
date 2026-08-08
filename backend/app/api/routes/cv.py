from fastapi import APIRouter, UploadFile, File, Form, HTTPException

import io
import pdfplumber

from app.services.cv_analyzer import CVAnalyzer
from app.services.cv_tailor import CVTailor


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
            detail=f"Error extracting PDF text: {str(e)}",
        )


@router.post("/cv/upload")
async def upload_cv(
    file: UploadFile = File(...),
):
    """
    Sube un CV en PDF y realiza el análisis tradicional.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    try:
        file_bytes = await file.read()

        extracted_text = extract_text_from_pdf(file_bytes)

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF",
            )

        analysis = analyzer.analyze(extracted_text)

        return {
            "message": "CV uploaded and analyzed successfully",
            "filename": file.filename,
            "analysis": analysis,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}",
        )


@router.post("/cv/match")
async def match_cv(
    file: UploadFile = File(...),
    job_text: str = Form(...),
):
    """
    Flujo completo:

    PDF
    ↓
    Extracción de texto
    ↓
    Análisis CV
    ↓
    Comparación con oferta
    ↓
    Optimización con Ollama
    ↓
    Resultado final
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    if not job_text or not job_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is required",
        )

    try:
        # ---------------------------------------------
        # 1. Leer PDF
        # ---------------------------------------------

        file_bytes = await file.read()


        # ---------------------------------------------
        # 2. Extraer texto
        # ---------------------------------------------

        extracted_text = extract_text_from_pdf(file_bytes)

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF",
            )


        # ---------------------------------------------
        # 3. Analizar CV original
        # ---------------------------------------------

        analysis = analyzer.analyze(
            extracted_text
        )


        # ---------------------------------------------
        # 4. Match CV vs oferta
        # ---------------------------------------------

        match_result = analyzer.match_with_job(
            cv_skills=analysis["skills"],
            job_text=job_text,
        )


        # ---------------------------------------------
        # 5. Optimizar CV con Ollama
        # ---------------------------------------------

        tailored_result = await tailor.tailor(
            cv_text=extracted_text,
            job_text=job_text,
            match_result=match_result,
        )


        # ---------------------------------------------
        # 6. Respuesta
        # ---------------------------------------------

        return {
            "message": "CV matched and optimized successfully",

            "filename": file.filename,

            "analysis": analysis,

            "match": match_result,

            "tailored_cv": tailored_result,
        }


    except HTTPException:
        raise


    except Exception as e:
        print(
            "CV MATCH ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=f"CV matching and tailoring failed: {str(e)}",
        )