from fastapi import APIRouter, HTTPException

from app.services.ai_service import AIService


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.get("/test")
async def test_ai():

    try:
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

    except Exception as e:

        print("AI ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
