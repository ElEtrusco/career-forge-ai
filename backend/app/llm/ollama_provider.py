import httpx

from app.core.config import settings
from app.llm.base import LLMService, Message


class OllamaProvider(LLMService):
    """
    Proveedor LLM usando Ollama local.
    """

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

                "num_ctx": settings.OLLAMA_CONTEXT_SIZE,

                "num_predict": max_tokens,
            },
        }


        url = f"{settings.OLLAMA_URL}/api/chat"


        print("--------------------------------")
        print("OLLAMA URL:", url)
        print("OLLAMA MODEL:", settings.OLLAMA_MODEL)
        print("OLLAMA PAYLOAD:", payload)
        print("--------------------------------")


        async with httpx.AsyncClient() as client:

            response = await client.post(
                url,
                json=payload,
                timeout=settings.OLLAMA_TIMEOUT,
            )


            print("OLLAMA STATUS:", response.status_code)

            print(
                "OLLAMA RESPONSE:",
                response.text[:500]
            )


            response.raise_for_status()


            data = response.json()


            if "message" not in data:
                raise RuntimeError(
                f"Unexpected Ollama response: {data}"
                )

            return data["message"]["content"]

