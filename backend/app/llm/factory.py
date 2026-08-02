from app.core.config import settings

from app.llm.base import LLMService
from app.llm.openai_provider import OpenAIProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.claude_provider import ClaudeProvider


class LLMFactory:
    """
    Factory responsable de crear el proveedor LLM configurado.

    Lee la configuración del entorno y devuelve
    una implementación compatible con LLMService.
    """

    @staticmethod
    def get_provider() -> LLMService:
        """
        Crea y devuelve el proveedor LLM seleccionado.

        Los proveedores disponibles son:
        - OpenAI
        - Ollama
        - Gemini
        - Claude
        """

        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            return OpenAIProvider()

        if provider == "ollama":
            return OllamaProvider()

        if provider == "gemini":
            return GeminiProvider()

        if provider == "claude":
            return ClaudeProvider()

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )