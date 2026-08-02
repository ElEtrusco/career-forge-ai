from abc import ABC, abstractmethod
from typing import Optional


class LLMService(ABC):
    """
    Abstract base class for all LLM providers.

    Every provider (OpenAI, Gemini, Ollama, Claude...)
    must implement this interface.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a response from the language model.
        """
        raise NotImplementedError