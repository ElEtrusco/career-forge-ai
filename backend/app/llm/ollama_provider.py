import httpx

from app.core.config import settings
from app.llm.base import LLMService, Message


class OllamaProvider(LLMService):
    """
    Local LLM provider using Ollama API.
    """

    def __init__(self):
        self.url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL

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
                "num_predict": max_tokens,
            },
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{self.url}/api/chat",
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

        return data["message"]["content"]
