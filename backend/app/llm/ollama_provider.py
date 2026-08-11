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
        temperature: float = 0.1,
        max_tokens: int = 500,
    ) -> str:
        """
        Envía una conversación a Ollama y devuelve la respuesta generada.
        """

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 2048,
                "num_predict": max_tokens,
            },
        }

        url = f"{settings.OLLAMA_URL}/api/chat"

        print("--------------------------------")
        print("OLLAMA URL:", url)
        print("OLLAMA MODEL:", settings.OLLAMA_MODEL)
        print("OLLAMA CONTEXT:", 2048)
        print("OLLAMA MAX TOKENS:", max_tokens)
        print("OLLAMA TEMPERATURE:", temperature)
        print("--------------------------------")

        async with httpx.AsyncClient(
            timeout=settings.OLLAMA_TIMEOUT
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

        print("OLLAMA STATUS:", response.status_code)
        print("OLLAMA RESPONSE:", response.text[:500])

        response.raise_for_status()

        data = response.json()

        if "message" not in data:
            raise RuntimeError(
                f"Unexpected Ollama response: {data}"
            )

        content = data["message"].get("content")

        if not content:
            raise RuntimeError(
                f"Ollama returned an empty response: {data}"
            )

        return content

