from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.base import LLMService, Message


class OpenAIProvider(LLMService):

    def __init__(self):

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = settings.OPENAI_MODEL


    async def chat(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:

        response = await self.client.responses.create(
            model=self.model,
            input=messages,
            max_output_tokens=max_tokens,
        )

        return response.output_text
