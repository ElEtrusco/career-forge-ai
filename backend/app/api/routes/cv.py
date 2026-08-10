from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import io
import traceback

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

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="PDF file is empty",
        )

    try:
        pdf_file = io.BytesIO(file_bytes)

        text_parts = []

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text_parts.append(page_text)

        text = "\n".join(text_parts).strip()

        return text

    except HTTPException:
        raise

    except Exception as e:
        print("PDF EXTRACTION ERROR:")
        traceback.print_exc()

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
        # ---------------------------------------------
        # 1. Leer PDF
        # ---------------------------------------------

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty",
            )

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
        # 3. Analizar CV
        # ---------------------------------------------

        analysis = analyzer.analyze(
            extracted_text
        )

        # ---------------------------------------------
        # 4. Respuesta
        # ---------------------------------------------

        return {
            "message": "CV uploaded and analyzed successfully",
            "filename": file.filename,
            "analysis": analysis,
        }

    except HTTPException:
        raise

    except Exception as e:
        print("CV UPLOAD ERROR:")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {repr(e)}",
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
    Análisis del CV optimizado
    ↓
    Resultado final
    """

    # ---------------------------------------------
    # VALIDACIONES
    # ---------------------------------------------

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

        print("CV MATCH: reading PDF...")

        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty",
            )

        # ---------------------------------------------
        # 2. Extraer texto
        # ---------------------------------------------

        print("CV MATCH: extracting PDF text...")

        extracted_text = extract_text_from_pdf(file_bytes)

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF",
            )

        print(
            f"CV MATCH: extracted {len(extracted_text)} characters"
        )

        # ---------------------------------------------
        # 3. Analizar CV original
        # ---------------------------------------------

        print("CV MATCH: analyzing original CV...")

        analysis = analyzer.analyze(
            extracted_text
        )

        print("CV MATCH: original CV analysis completed")

        # ---------------------------------------------
        # 4. Match CV vs oferta
        # ---------------------------------------------

        print("CV MATCH: matching CV against job...")

        match_result = analyzer.match_with_job(
            cv_skills=analysis["skills"],
            job_text=job_text,
        )

        print("CV MATCH: job matching completed")

        # ---------------------------------------------
        # 5. Optimizar CV con Ollama
        # ---------------------------------------------

        print("CV MATCH: starting CV tailoring...")

        # IMPORTANTE:
        # CVTailor.tailor() actualmente acepta solamente:
        #
        #   cv_text
        #   job_text
        #
        # NO pasar match_result aquí.
        #
        # CVTailor calcula internamente el match.

        tailored_result = await tailor.tailor(
            cv_text=extracted_text,
            job_text=job_text,
        )

        print("CV MATCH: CV tailoring completed")

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
        print("=" * 70)
        print("CV MATCH ERROR")
        print("=" * 70)
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception repr: {repr(e)}")
        print(f"Exception str: {str(e)}")
        traceback.print_exc()
        print("=" * 70)

        raise HTTPException(
            status_code=500,
            detail=(
                f"CV matching and tailoring failed: "
                f"{type(e).__name__}: {repr(e)}"
            ),
        )
