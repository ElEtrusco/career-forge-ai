import httpx

from app.core.config import settings
from app.llm.base import LLMService, Message


class OllamaProvider(LLMService):

    async def chat(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:

        payload = {
            "model": settings.LLM_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 1024,
                "num_predict": max_tokens,
            },
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                "http://localhost:11434/api/chat",
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            return data["message"]["content"]
