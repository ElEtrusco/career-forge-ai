from typing import Dict, List

from app.services.skill_extractor import SkillExtractor


class JobMatcher:
    """
    Compara las habilidades de un candidato con las habilidades
    detectadas en una oferta de empleo.

    El catálogo de skills pertenece a SkillExtractor.
    JobMatcher se encarga únicamente de la comparación y el scoring.
    """

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extrae las habilidades de una oferta utilizando SkillExtractor.
        """

        if not text:
            return {
                "hard_skills": [],
                "soft_skills": [],
                "languages": [],
            }

        return self.skill_extractor.extract_all(text, expand_concepts=False)

    def match(self, cv_skills: Dict, job_text: str) -> Dict:
        """
        Compara las skills del CV con las skills detectadas en la oferta.
        """

        # ------------------------------------------------------------
        # Extraer skills de la oferta
        # ------------------------------------------------------------

        job_skills = self.extract_skills_from_text(job_text)

        # ------------------------------------------------------------
        # Skills del CV
        # ------------------------------------------------------------

        cv_hard = set(cv_skills.get("hard_skills", []))
        cv_soft = set(cv_skills.get("soft_skills", []))
        cv_languages = set(cv_skills.get("languages", []))

        # ------------------------------------------------------------
        # Skills de la oferta
        # ------------------------------------------------------------

        job_hard = set(job_skills.get("hard_skills", []))
        job_soft = set(job_skills.get("soft_skills", []))
        job_languages = set(job_skills.get("languages", []))

        # ------------------------------------------------------------
        # Coincidencias
        # ------------------------------------------------------------

        hard_match = cv_hard & job_hard
        soft_match = cv_soft & job_soft
        language_match = cv_languages & job_languages

        # ------------------------------------------------------------
        # Gaps
        # ------------------------------------------------------------

        missing_hard = job_hard - cv_hard
        missing_soft = job_soft - cv_soft
        missing_languages = job_languages - cv_languages

        # ------------------------------------------------------------
        # Scoring
        #
        # Mantenemos inicialmente el criterio actual:
        #   HARD      = 70 puntos
        #   SOFT      = 20 puntos
        #   LANGUAGES = 10 puntos
        #
        # Más adelante revisaremos este algoritmo.
        # ------------------------------------------------------------

        hard_score = (
            len(hard_match) / len(job_hard) * 70
            if job_hard
            else 0
        )

        soft_score = (
            len(soft_match) / len(job_soft) * 20
            if job_soft
            else 0
        )

        language_score = (
            len(language_match) / len(job_languages) * 10
            if job_languages
            else 0
        )

        score = round(
            min(
                hard_score + soft_score + language_score,
                100,
            ),
            2,
        )

        # ------------------------------------------------------------
        # Resultado
        # ------------------------------------------------------------

        return {
            "match_score": score,

            "hard_match": sorted(hard_match),

            "soft_match": sorted(soft_match),

            "language_match": sorted(language_match),

            "missing_skills": sorted(missing_hard),

            "missing_hard_skills": sorted(missing_hard),

            "missing_soft_skills": sorted(missing_soft),

            "missing_languages": sorted(missing_languages),

            "job_skills_detected": {
                "hard_skills": sorted(job_hard),
                "soft_skills": sorted(job_soft),
                "languages": sorted(job_languages),
            },
        }