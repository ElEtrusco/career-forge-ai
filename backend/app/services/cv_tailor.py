from typing import Dict, Any

from app.services.ai_service import AIService
from app.services.skill_extractor import SkillExtractor
from app.services.job_matcher import JobMatcher
from app.services.ats_scorer_v2 import ATSScorerV2


class CVTailor:

    def __init__(self):
        self.ai = AIService()
        self.skill_extractor = SkillExtractor()
        self.job_matcher = JobMatcher()
        self.ats_scorer = ATSScorerV2()

    async def tailor(
        self,
        cv_text: str,
        job_text: str,
    ) -> Dict[str, Any]:

        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is required")

        if not job_text or not job_text.strip():
            raise ValueError("Job description is required")

        # --------------------------------------------------
        # 1. Analizar CV ORIGINAL
        # --------------------------------------------------

        original_skills = self.skill_extractor.extract_all(cv_text)

        original_ats = self.ats_scorer.calculate(
            original_skills,
            cv_text,
        )

        original_match = self.job_matcher.match(
            cv_skills=original_skills,
            job_text=job_text,
        )

        missing_hard = original_match.get(
            "missing_hard_skills",
            [],
        )

        missing_soft = original_match.get(
            "missing_soft_skills",
            [],
        )

        missing_languages = original_match.get(
            "missing_languages",
            [],
        )

        # --------------------------------------------------
        # 2. Pedir a Ollama que adapte el CV
        # --------------------------------------------------

        prompt = f"""
Eres un experto en CV, ATS y selección de personal.

Tu tarea es mejorar el CV del candidato para la oferta de empleo.

REGLAS OBLIGATORIAS:

- No inventes experiencia.
- No inventes empresas.
- No inventes puestos.
- No inventes estudios.
- No inventes certificaciones.
- No inventes idiomas.
- No inventes tecnologías.
- No añadas años que no aparezcan en el CV.
- No añadas porcentajes ni métricas inexistentes.
- No afirmes que el candidato conoce una tecnología si el CV original no lo demuestra.
- Puedes mejorar la redacción.
- Puedes mejorar la estructura.
- Puedes reorganizar información existente.
- Puedes mejorar el resumen profesional.
- Puedes utilizar palabras clave de la oferta únicamente cuando estén respaldadas por el CV.
- Mantén la información verdadera del candidato.
- El resultado debe ser compatible con ATS.
- Conserva el idioma principal del CV.

OFERTA DE EMPLEO:

{job_text}

SKILLS DETECTADAS EN EL CV:

{original_skills}

SKILLS QUE LA OFERTA REQUIERE Y NO APARECEN EN EL CV:

Hard skills:
{missing_hard}

Soft skills:
{missing_soft}

Idiomas:
{missing_languages}

CV ORIGINAL:

{cv_text}

Devuelve únicamente el CV mejorado.

No incluyas explicaciones.
No incluyas comentarios.
No escribas "CV mejorado".
Devuelve directamente el contenido final del CV.
"""

        improved_cv = await self.ai.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert CV and ATS optimization "
                        "assistant. Never invent candidate information."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=1800,
        )

        improved_cv = improved_cv.strip()

        # --------------------------------------------------
        # 3. Analizar CV MEJORADO
        # --------------------------------------------------

        improved_skills = self.skill_extractor.extract_all(
            improved_cv
        )

        improved_ats = self.ats_scorer.calculate(
            improved_skills,
            improved_cv,
        )

        improved_match = self.job_matcher.match(
            cv_skills=improved_skills,
            job_text=job_text,
        )

        # --------------------------------------------------
        # 4. Resultado completo
        # --------------------------------------------------

        return {
            "original_cv": cv_text,

            "improved_cv": improved_cv,

            "original_skills": original_skills,

            "improved_skills": improved_skills,

            "original_ats_score": original_ats,

            "improved_ats_score": improved_ats,

            "ats_improvement": improved_ats - original_ats,

            "original_job_match": original_match,

            "improved_job_match": improved_match,

            "job_match_improvement": round(
                improved_match["match_score"]
                - original_match["match_score"],
                2,
            ),

            "missing_skills_before": {
                "hard_skills": missing_hard,
                "soft_skills": missing_soft,
                "languages": missing_languages,
            },

            "missing_skills_after": {
                "hard_skills": improved_match.get(
                    "missing_hard_skills",
                    [],
                ),
                "soft_skills": improved_match.get(
                    "missing_soft_skills",
                    [],
                ),
                "languages": improved_match.get(
                    "missing_languages",
                    [],
                ),
            },
        }
