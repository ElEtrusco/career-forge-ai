from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_ai_service
from app.services.ai_service import AIService
from app.core.config import settings


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.get("/test")
async def test_ai(
    service: AIService = Depends(get_ai_service),
):
    """
    Endpoint de prueba para verificar
    que el proveedor LLM responde.
    """

    try:

        response = await service.chat(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant.",
                },
                {
                    "role": "user",
                    "content": "Say hello in Spanish.",
                },
            ]
        )


        return {
            "response": response,
        }


    except Exception as e:

        print("AI ERROR:", repr(e))


        raise HTTPException(
            status_code=500,
            detail=str(e),
        )



@router.get("/health")
async def ai_health():
    """
    Estado del proveedor de IA configurado.
    No ejecuta una llamada al modelo.
    """

    try:

        if settings.LLM_PROVIDER == "ollama":

            model = settings.OLLAMA_MODEL


        elif settings.LLM_PROVIDER == "openai":

            model = settings.OPENAI_MODEL


        elif settings.LLM_PROVIDER == "gemini":

            model = settings.GEMINI_MODEL


        elif settings.LLM_PROVIDER == "anthropic":

            model = settings.CLAUDE_MODEL


        else:

            model = "unknown"



        return {
            "status": "available",

            "provider": settings.LLM_PROVIDER,

            "model": model,
        }


    except Exception as e:

        print("AI HEALTH ERROR:", repr(e))


        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
