from app.llm.base import LLMService, Message


class ClaudeProvider(LLMService):

    async def chat(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:

        raise NotImplementedError(
            "Claude provider has not been implemented yet."
        )
