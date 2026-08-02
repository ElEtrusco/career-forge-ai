from app.core.config import settings

from app.llm.openai_provider import OpenAIProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.claude_provider import ClaudeProvider


class LLMFactory:

    @staticmethod
    def get_provider():

        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            return OpenAIProvider()

        if provider == "ollama":
            return OllamaProvider()

        if provider == "gemini":
            return GeminiProvider()

        if provider == "claude":
            return ClaudeProvider()

        raise ValueError(f"Unsupported LLM provider: {provider}")