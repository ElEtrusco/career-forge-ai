from fastapi import APIRouter

from app.services.ai_service import AIService


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.get("/test")
async def test_ai():

    service = AIService()

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
