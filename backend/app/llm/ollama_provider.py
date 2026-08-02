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
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 1024,
                "num_predict": max_tokens,
            },
        }

        url = f"{settings.OLLAMA_URL}/api/chat"

        print("OLLAMA URL:", url)
        print("OLLAMA MODEL:", settings.OLLAMA_MODEL)
        print("OLLAMA PAYLOAD:", payload)

        async with httpx.AsyncClient() as client:

            response = await client.post(
                url,
                json=payload,
                timeout=120,
            )

            print("OLLAMA STATUS:", response.status_code)

            if response.status_code != 200:
                print("OLLAMA ERROR:", response.text)

            response.raise_for_status()

            data = response.json()

            return data["message"]["content"]
