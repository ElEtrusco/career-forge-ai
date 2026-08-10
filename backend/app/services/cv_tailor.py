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
    match_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    if not cv_text or not cv_text.strip():
        raise ValueError("CV text is required")

    if not job_text or not job_text.strip():
        raise ValueError("Job description is required")

    # --------------------------------------------------
    # 1. ANALIZAR CV ORIGINAL
    # --------------------------------------------------

    original_skills = self.skill_extractor.extract_all(
        cv_text
    )

    original_ats = self.ats_scorer.calculate(
        original_skills,
        cv_text,
    )

    # Si el endpoint ya calculó el match, reutilizarlo.
    # Esto evita hacer el mismo análisis dos veces.
    if match_result is not None:
        original_match = match_result
    else:
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

    missing_keywords = original_match.get(
        "missing_keywords",
        [],
    )

    missing_required_keywords = original_match.get(
        "missing_required_keywords",
        [],
    )

    # --------------------------------------------------
    # 2. PEDIR A OLLAMA QUE ADAPTE EL CV
    # --------------------------------------------------

    prompt = f"""
```

Eres un experto en CV, ATS y selección de personal.

Tu tarea es mejorar el CV del candidato específicamente para
la oferta de empleo proporcionada.

OBJETIVO:

Aumentar la relevancia del CV para esta oferta utilizando
ÚNICAMENTE información verdadera y demostrable del CV original.

REGLAS OBLIGATORIAS:

* No inventes experiencia.
* No inventes empresas.
* No inventes puestos.
* No inventes estudios.
* No inventes certificaciones.
* No inventes idiomas.
* No inventes tecnologías.
* No añadas años de experiencia que no aparezcan en el CV.
* No añadas porcentajes inexistentes.
* No añadas métricas inexistentes.
* No añadas responsabilidades que el candidato no haya realizado.
* No afirmes que el candidato domina una tecnología que no aparece
  en el CV original.
* No conviertas una palabra de la oferta en una habilidad del
  candidato si no existe evidencia en el CV.
* Puedes mejorar la redacción.
* Puedes reorganizar la información.
* Puedes eliminar redundancias.
* Puedes mejorar el perfil profesional.
* Puedes mejorar la descripción de experiencias reales.
* Puedes destacar tecnologías que ya aparecen en el CV.
* Puedes destacar competencias que ya aparecen en el CV.
* Puedes utilizar palabras clave de la oferta cuando estén
  respaldadas por información existente en el CV.
* Mantén la información verdadera del candidato.
* El resultado debe ser compatible con sistemas ATS.
* Utiliza una estructura clara y fácil de leer.
* Conserva el idioma principal del CV.
* No escribas explicaciones fuera del CV.

OFERTA DE EMPLEO:

{job_text}

SKILLS DETECTADAS EN EL CV:

{original_skills}

SKILLS REQUERIDAS POR LA OFERTA QUE NO ESTÁN DETECTADAS:

Hard skills:
{missing_hard}

Soft skills:
{missing_soft}

Idiomas:
{missing_languages}

KEYWORDS DE LA OFERTA QUE NO APARECEN EN EL CV:

{missing_keywords}

KEYWORDS OBLIGATORIAS QUE NO APARECEN EN EL CV:

{missing_required_keywords}

IMPORTANTE:

Las keywords ausentes NO deben añadirse al CV como si el candidato
las conociera.

Solo puedes incorporar una keyword si existe evidencia equivalente
en el CV original.

CV ORIGINAL:

{cv_text}

INSTRUCCIONES DE SALIDA:

Devuelve únicamente el CV mejorado.

No incluyas explicaciones.
No incluyas comentarios.
No escribas "CV mejorado".
No escribas análisis.
No escribas recomendaciones.

Devuelve directamente el contenido final del CV.
"""

```
    improved_cv = await self.ai.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert CV and ATS optimization "
                    "assistant. Never invent candidate information. "
                    "Only rewrite and reorganize information supported "
                    "by the original CV."
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
    # 3. ANALIZAR CV MEJORADO
    # --------------------------------------------------

    improved_skills = self.skill_extractor.extract_all(
        improved_cv
    )

    improved_ats = self.ats_scorer.calculate(
        improved_skills,
        improved_cv,
    )

    # Importante:
    # pasar el texto completo del CV mejorado permite que
    # JobKeywordAnalyzer compare las keywords de la oferta
    # contra el CV real.
    improved_match = self.job_matcher.match(
        cv_skills=improved_skills,
        job_text=job_text,
        cv_text=improved_cv,
    )

    # --------------------------------------------------
    # 4. CALCULAR MEJORAS
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 5. RESULTADO COMPLETO
    # --------------------------------------------------

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

        "missing_keywords_before": missing_keywords,

        "missing_required_keywords_before": (
            missing_required_keywords
        ),

        "missing_keywords_after": (
            improved_match.get(
                "missing_keywords",
                [],
            )
        ),

        "missing_required_keywords_after": (
            improved_match.get(
                "missing_required_keywords",
                [],
            )
        ),
    }

