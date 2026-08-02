from abc import ABC, abstractmethod
from typing import TypedDict


class Message(TypedDict):
    """
    Formato estándar de mensajes para cualquier proveedor LLM.
    """

    role: str

    content: str



class LLMService(ABC):
    """
    Interfaz base para proveedores de modelos de lenguaje.
    """


    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Envía mensajes al modelo y devuelve una respuesta.
        """

        pass
