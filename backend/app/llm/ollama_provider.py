import httpx

from app.llm.base import LLMService, Message
from app.core.config import settings


class OllamaProvider(LLMService):

    def __init__(self):

        self.url = "http://localhost:11434/api/chat"
        self.model = settings.OPENAI_MODEL


    async def chat(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 1024,
                "num_predict": max_tokens,
            }
        }

        async with httpx.AsyncClient(timeout=120) as client:

            response = await client.post(
                self.url,
                json=payload
            )

            response.raise_for_status()

            data = response.json()

            return data["message"]["content"]
