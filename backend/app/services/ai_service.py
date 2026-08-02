from app.core.config import settings

from app.llm.base import LLMService
from app.llm.ollama_provider import OllamaProvider


class AIService:
    """
    Servicio principal de IA.

    Esta capa abstrae el proveedor LLM.
    Los endpoints no deben saber si usamos Ollama,
    OpenAI u otro proveedor.
    """

    def __init__(self):
        self.provider: LLMService = self._get_provider()

    def _get_provider(self) -> LLMService:
        """
        Selecciona el proveedor configurado en .env.
        """

        provider = settings.LLM_PROVIDER.lower()

        if provider == "ollama":
            return OllamaProvider()

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )

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



"""from app.core.config import settings

from app.llm.base import LLMService
from app.llm.ollama_provider import OllamaProvider


class AIService:
    """
    Servicio principal de IA.

    Esta capa abstrae el proveedor LLM.
    Los endpoints no deben saber si usamos Ollama,
    OpenAI u otro proveedor.
    """

    def __init__(self):
        self.provider: LLMService = self._get_provider()

    def _get_provider(self) -> LLMService:
        """
        Selecciona el proveedor configurado en .env.
        """

        provider = settings.LLM_PROVIDER.lower()

        if provider == "ollama":
            return OllamaProvider()

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )

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
        )"""