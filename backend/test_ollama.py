import asyncio

from app.llm.factory import LLMFactory


async def main():
    provider = LLMFactory.get_provider()

    print("Proveedor:", provider.__class__.__name__)

    response = await provider.chat(
        [
            {
                "role": "user",
                "content": "Responde únicamente con: OLLAMA FUNCIONA",
            }
        ],
        temperature=0.1,
        max_tokens=20,
    )

    print("Respuesta:", response)


if __name__ == "__main__":
    asyncio.run(main())
