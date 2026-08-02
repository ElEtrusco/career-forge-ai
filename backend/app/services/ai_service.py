from app.llm.factory import LLMFactory
from app.llm.base import Message


class AIService:

    def __init__(self):

        self.provider = LLMFactory.get_provider()


    async def chat(
        self,
        messages: list[Message],
    ) -> str:

        return await self.provider.chat(
            messages=messages
        )
