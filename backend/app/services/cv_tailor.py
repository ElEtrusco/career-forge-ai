from typing import Dict, Any

from app.services.ai_service import AIService
from app.services.skill_extractor import SkillExtractor
from app.services.job_matcher import JobMatcher
from app.services.ats_scorer_v2 import ATSScorerV2

class CVTailor:

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
        Analiza el CV original, lo adapta a una oferta mediante Ollama
        y vuelve a analizar el resultado para medir la mejora.

        Importante:
        - No inventa experiencia.
        - No inventa tecnologías.
        - No inventa estudios.
        - No inventa certificaciones.
        - No inventa idiomas.
        - La adaptación se basa únicamente en información presente
        en el CV original.
        """

        if not cv_text or not cv_text.strip():
            raise ValueError("CV text is required")

        if not job_text or not job_text.strip():
            raise ValueError("Job description is required")

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
        # 2. CONSTRUIR PROMPT PARA OLLAMA
        # ==========================================================

        prompt = f"""

    Eres un experto en selección de personal, CV y sistemas ATS.

    Tu tarea es adaptar el CV de un candidato a una oferta de empleo
    concreta.

    OBJETIVO:

    Mejorar las posibilidades del candidato frente a esta oferta,
    pero manteniendo estrictamente la información verdadera del CV.

    REGLAS ABSOLUTAS:

    1. NO inventes experiencia profesional.
    2. NO inventes empresas.
    3. NO inventes puestos de trabajo.
    4. NO inventes estudios.
    5. NO inventes certificaciones.
    6. NO inventes idiomas.
    7. NO inventes tecnologías.
    8. NO inventes herramientas.
    9. NO inventes proyectos.
    10. NO inventes años de experiencia.
    11. NO inventes porcentajes.
    12. NO inventes métricas.
    13. NO conviertas conocimientos básicos en experiencia profesional.
    14. NO afirmes que el candidato ha trabajado con una tecnología
        si el CV original no lo demuestra.
    15. NO añadas una habilidad únicamente porque aparece en la oferta.
    16. Puedes reorganizar información existente.
    17. Puedes mejorar la redacción.
    18. Puedes hacer más profesional el perfil.
    19. Puedes utilizar terminología de la oferta cuando esté respaldada
        por información real del CV.
    20. Puedes destacar habilidades que ya aparecen en el CV.
    21. Puedes mejorar los títulos de las secciones.
    22. Puedes convertir responsabilidades existentes en frases
        profesionales orientadas a resultados, pero SIN inventar resultados.
    23. Mantén el idioma principal del CV.
    24. El resultado debe ser limpio y compatible con ATS.
    25. No utilices tablas, columnas, gráficos, iconos ni elementos
        que puedan dificultar la lectura ATS.

    IMPORTANTE:

    Las habilidades que faltan NO deben incorporarse artificialmente
    al CV.

    Si la oferta solicita una tecnología que el candidato no tiene,
    debe permanecer ausente.

    OFERTA DE EMPLEO:

    {job_text}

    SKILLS DETECTADAS EN EL CV:

    {original_skills}

    SKILLS REQUERIDAS POR LA OFERTA QUE NO ESTÁN EN EL CV:

    HARD SKILLS:
    {missing_hard}

    SOFT SKILLS:
    {missing_soft}

    IDIOMAS:
    {missing_languages}

    CV ORIGINAL:

    {cv_text}

    TAREA:

    Devuelve una versión mejorada del CV adaptada específicamente
    a esta oferta.

    Prioriza:

    * Perfil profesional
    * Experiencia profesional
    * Competencias técnicas
    * Proyectos
    * Formación
    * Palabras clave ATS respaldadas por el CV

    No inventes información para cubrir carencias.

    Devuelve ÚNICAMENTE el CV final.

    No escribas explicaciones.
    No escribas comentarios.
    No escribas "CV mejorado".
    No escribas introducciones.
    No escribas conclusiones.

    Empieza directamente con el contenido del CV.
    """

        # ==========================================================
        # 3. OLLAMA / IA
        # ==========================================================

        improved_cv = await self.ai.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert CV and ATS optimization "
                        "assistant. You must never invent candidate "
                        "information. Only rewrite and reorganize "
                        "information supported by the original CV."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=900,
        )

        if not improved_cv:
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

        ats_improvement = (
            improved_ats
            - original_ats
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
