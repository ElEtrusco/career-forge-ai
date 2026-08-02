from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_ai_service
from app.services.ai_service import AIService
from app.core.config import settings


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.get("/test")
async def test_ai(
    service: AIService = Depends(get_ai_service),
):

    try:

        response = await service.chat(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant."
                },
                {
                    "role": "user",
                    "content": "Say hello in Spanish."
                }
            ]
        )

        return {
            "response": response
        }

    except Exception as e:

        print("AI ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/health")
async def ai_health(
    service: AIService = Depends(get_ai_service),
):

    try:

        return {
            "status": "available",
            "provider": settings.LLM_PROVIDER,
            "model": (
                settings.OLLAMA_MODEL
                if settings.LLM_PROVIDER == "ollama"
                else settings.OPENAI_MODEL
            )
        }

    except Exception as e:

        print("AI HEALTH ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
