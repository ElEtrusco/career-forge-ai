from app.llm.base import LLMService
from app.llm.factory import LLMFactory


class AIService:
    """
    Servicio principal de IA.

    Esta capa abstrae el proveedor LLM.
    Los endpoints no deben saber si usamos Ollama,
    OpenAI u otro proveedor.
    """

    def __init__(self):
        self.provider: LLMService = LLMFactory.get_provider()

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Ejecuta una conversación con el modelo.
        """

        return await self.provider.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )