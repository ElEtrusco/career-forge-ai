from abc import ABC, abstractmethod
from typing import List, TypedDict


class Message(TypedDict):
    """
    Standard message format used by all LLM providers.
    """

    role: str
    content: str


class LLMService(ABC):
    """
    Abstract interface implemented by every LLM provider.
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send messages to the language model and return response.
        """

        raise NotImplementedError