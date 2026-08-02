from app.llm.base import LLMService, Message


class AIService:
    """
    Servicio principal de inteligencia artificial.

    Esta capa desacopla los endpoints FastAPI
    del proveedor concreto (Ollama, OpenAI, etc.).
    """


    def __init__(
        self,
        llm: LLMService,
    ):
        self.llm = llm



    async def chat(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Envía mensajes al proveedor LLM activo.
        """

        return await self.llm.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
