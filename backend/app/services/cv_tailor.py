from typing import Any, Dict

from app.services.ai_service import AIService
from app.services.skill_extractor import SkillExtractor
from app.services.job_matcher import JobMatcher
from app.services.ats_scorer_v2 import ATSScorerV2

class CVTailor:
    """
    Adapta un CV a una oferta de empleo utilizando un LLM.


    El flujo es:

        CV original
            ↓
        análisis de skills
            ↓
        análisis ATS
            ↓
        matching con oferta
            ↓
        optimización mediante IA
            ↓
        análisis del CV optimizado
            ↓
        resultado final

    La IA solamente puede reorganizar y mejorar información
    existente en el CV original.
    """

    def __init__(self) -> None:
        self.ai = AIService()
        self.skill_extractor = SkillExtractor()
        self.job_matcher = JobMatcher()
        self.ats_scorer = ATSScorerV2()

    async def tailor(
        self,
        cv_text: str,
        job_text: str,
    ) -> Dict[str, Any]:
        """
        Analiza el CV original, lo adapta a la oferta y
        vuelve a analizar el resultado.

        La IA no debe inventar:
        - experiencia
        - empresas
        - puestos
        - estudios
        - certificaciones
        - idiomas
        - tecnologías
        - herramientas
        - proyectos
        - años de experiencia
        - métricas
        - resultados
        """

        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is required")

        if not job_text or not job_text.strip():
            raise ValueError("Job description is required")

        cv_text = cv_text.strip()
        job_text = job_text.strip()

        # ==========================================================
        # 1. ANALIZAR CV ORIGINAL
        # ==========================================================

        original_skills = self.skill_extractor.extract_all(
            cv_text,
            expand_concepts=False,
        )

        original_ats = self.ats_scorer.calculate(
            original_skills,
            cv_text,
        )

        original_match = self.job_matcher.match(
            cv_skills=original_skills,
            job_text=job_text,
            cv_text=cv_text,
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

        # ==========================================================
        # 2. CONSTRUIR PROMPT
        # ==========================================================

        prompt = f"""
    ```

    Adapta el siguiente CV a la oferta de empleo.

    REGLA PRINCIPAL:
    Solo puedes utilizar información que aparezca explícitamente
    en el CV original.

    NO inventes ni completes información que no exista.

    NO inventes:

    * nombres
    * datos personales
    * empresas
    * puestos
    * experiencia
    * años de experiencia
    * tecnologías
    * herramientas
    * frameworks
    * estudios
    * certificaciones
    * idiomas
    * proyectos
    * responsabilidades
    * resultados
    * métricas
    * porcentajes

    IMPORTANTE:
    Si una información no aparece en el CV original, simplemente
    NO la escribas.

    NO utilices placeholders como:
    [Tu nombre]
    [Tu dirección]
    [Tu teléfono]
    [Descripción...]
    [Empresa]
    [Fecha]
    [Logros]

    No añadas secciones vacías.

    Puedes:

    * reorganizar información existente;
    * mejorar la redacción;
    * corregir errores;
    * hacer el perfil más profesional;
    * destacar habilidades que ya existen;
    * utilizar palabras de la oferta cuando estén respaldadas
    por información real del CV;
    * mejorar la estructura para ATS.

    Las habilidades que aparecen en la oferta pero no en el CV
    deben permanecer ausentes.

    OFERTA:

    {job_text}

    SKILLS DEL CV:

    {original_skills}

    SKILLS DE LA OFERTA QUE NO APARECEN EN EL CV:

    Hard skills:
    {missing_hard}

    Soft skills:
    {missing_soft}

    Idiomas:
    {missing_languages}

    CV ORIGINAL:

    {cv_text}

    OBJETIVO:

    Devuelve únicamente una versión mejorada del CV.

    Mantén el idioma principal del CV.

    Prioriza:

    * Perfil profesional
    * Experiencia
    * Competencias técnicas
    * Proyectos existentes
    * Formación existente
    * Palabras clave ATS respaldadas por el CV

    No escribas explicaciones.
    No escribas comentarios.
    No escribas conclusiones.
    No escribas "CV mejorado".
    No escribas texto antes del CV.

    Empieza directamente con el contenido del CV.
    """

    ```
        # ==========================================================
        # 3. OPTIMIZAR CON IA
        # ==========================================================

        improved_cv = await self.ai.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert CV and ATS optimization "
                        "assistant. Rewrite only information supported "
                        "by the original CV. Never invent candidate "
                        "information. Never create placeholders. "
                        "If information is missing, omit it."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=500,
        )

        if not improved_cv or not improved_cv.strip():
            raise ValueError(
                "AI returned an empty CV"
            )

        improved_cv = improved_cv.strip()

        # ==========================================================
        # 4. ANALIZAR CV MEJORADO
        # ==========================================================

        improved_skills = self.skill_extractor.extract_all(
            improved_cv,
            expand_concepts=False,
        )

        improved_ats = self.ats_scorer.calculate(
            improved_skills,
            improved_cv,
        )

        improved_match = self.job_matcher.match(
            cv_skills=improved_skills,
            job_text=job_text,
            cv_text=improved_cv,
        )

        # ==========================================================
        # 5. CALCULAR MEJORAS
        # ==========================================================

        ats_improvement = round(
            improved_ats - original_ats,
            2,
        )

        job_match_improvement = round(
            improved_match.get(
                "match_score",
                0.0,
            )
            - original_match.get(
                "match_score",
                0.0,
            ),
            2,
        )

        # ==========================================================
        # 6. RESULTADO
        # ==========================================================

        return {
            "original_cv": cv_text,

            "improved_cv": improved_cv,

            "original_skills": original_skills,

            "improved_skills": improved_skills,

            "original_ats_score": original_ats,

            "improved_ats_score": improved_ats,

            "ats_improvement": ats_improvement,

            "original_job_match": original_match,

            "improved_job_match": improved_match,

            "job_match_improvement": job_match_improvement,

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

