import asyncio

from app.services.ai_service import AIService

CV_TEXT = """
John Doe
Backend Developer

Professional Summary:
Backend developer with experience building web applications and APIs.

Experience:
Backend Developer - Example Company

* Developed REST APIs using Python and FastAPI.
* Worked with PostgreSQL databases.
* Used Docker for application deployment.
* Collaborated with frontend developers.
* Maintained Git repositories.

Skills:
Python, FastAPI, PostgreSQL, Docker, Git

Languages:
English, Spanish
"""

async def main():
ai = AIService()

```
messages = [
    {
        "role": "system",
        "content": """
```

You are an ATS CV analyst.

Analyze the CV in Spanish.

Do not invent information.

Return only:

1. Perfil profesional
2. Hard skills
3. Soft skills
4. Idiomas
5. Mejoras ATS
   """,
   },
   {
   "role": "user",
   "content": f"CV:\n\n{CV_TEXT}",
   },
   ]

   print("Enviando CV a Ollama...")

   result = await ai.chat(
   messages=messages,
   temperature=0.1,
   max_tokens=250,
   )

   print("\n========== RESULTADO IA ==========\n")
   print(result)

if **name** == "**main**":
asyncio.run(main())
