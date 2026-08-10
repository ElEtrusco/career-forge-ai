from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List


class ATSScorerV2:
    """
    ATS scorer orientado a una oferta de empleo concreta.

    El objetivo no es simplemente determinar si un CV "parece bueno",
    sino medir qué tan bien está preparado para una oferta determinada.

    El sistema combina:

        1. Coincidencia de keywords de la oferta
        2. Coincidencia de requisitos obligatorios
        3. Coincidencia de skills
        4. Estructura ATS del CV
        5. Métricas y resultados
        6. Verbos de acción
        7. Penalizaciones
        8. Detección de keywords ausentes

    IMPORTANTE:

    El sistema NO recomienda añadir una skill que el candidato
    realmente no posee.

    Una keyword faltante debe convertirse posteriormente en una
    recomendación para revisar el CV, no en una invención.
    """

    # ================================================================
    # CONFIGURACIÓN
    # ================================================================

    MAX_SCORE = 100

    # Peso de cada componente del score.
    #
    # La coincidencia con la oferta tiene mucho más peso que la
    # estructura genérica del CV.

    KEYWORD_WEIGHT = 40
    REQUIRED_WEIGHT = 20
    SKILL_WEIGHT = 15
    STRUCTURE_WEIGHT = 10
    METRICS_WEIGHT = 5
    ACTION_VERBS_WEIGHT = 5
    READABILITY_WEIGHT = 5

    # ================================================================
    # PUBLIC API
    # ================================================================

    def calculate(
        self,
        skills: Dict[str, List[str]],
        text: str,
        job_profile: Dict[str, Any] | None = None,
        job_text: str | None = None,
    ) -> int:
        """
        Calcula un ATS score de 0 a 100.

        Parámetros:

            skills:
                Skills extraídas del CV.

            text:
                Texto completo del CV.

            job_profile:
                Perfil estructurado generado por JobProfileAnalyzer.

            job_text:
                Texto original de la oferta.

        Compatibilidad:

            calculate(skills, text)

        sigue funcionando como antes.

        Pero para obtener el verdadero ATS score adaptado a una
        oferta:

            calculate(
                skills,
                cv_text,
                job_profile=profile,
                job_text=job_text,
            )
        """

        if not text:
            return 0

        text_normalized = self._normalize_text(text)

        # ------------------------------------------------------------
        # 1. KEYWORDS DE LA OFERTA
        # ------------------------------------------------------------

        keyword_score = self._calculate_keyword_score(
            text_normalized=text_normalized,
            job_profile=job_profile,
            job_text=job_text,
        )

        # ------------------------------------------------------------
        # 2. REQUISITOS OBLIGATORIOS
        # ------------------------------------------------------------

        required_score = self._calculate_required_score(
            text_normalized=text_normalized,
            job_profile=job_profile,
        )

        # ------------------------------------------------------------
        # 3. SKILLS
        # ------------------------------------------------------------

        skill_score = self._calculate_skill_score(
            skills=skills,
            text_normalized=text_normalized,
            job_profile=job_profile,
        )

        # ------------------------------------------------------------
        # 4. ESTRUCTURA ATS
        # ------------------------------------------------------------

        structure_score = self._calculate_structure_score(
            text_normalized
        )

        # ------------------------------------------------------------
        # 5. MÉTRICAS
        # ------------------------------------------------------------

        metrics_score = self._calculate_metrics_score(
            text_normalized
        )

        # ------------------------------------------------------------
        # 6. VERBOS DE ACCIÓN
        # ------------------------------------------------------------

        action_score = self._calculate_action_verbs_score(
            text_normalized
        )

        # ------------------------------------------------------------
        # 7. LEGIBILIDAD / LONGITUD
        # ------------------------------------------------------------

        readability_score = self._calculate_readability_score(
            text_normalized
        )

        # ------------------------------------------------------------
        # SCORE FINAL
        # ------------------------------------------------------------

        score = (
            keyword_score
            + required_score
            + skill_score
            + structure_score
            + metrics_score
            + action_score
            + readability_score
        )

        return max(
            0,
            min(
                int(round(score)),
                self.MAX_SCORE,
            ),
        )

    # ================================================================
    # DETAILED SCORE
    # ================================================================

    def calculate_detailed(
        self,
        skills: Dict[str, List[str]],
        text: str,
        job_profile: Dict[str, Any] | None = None,
        job_text: str | None = None,
    ) -> Dict[str, Any]:
        """
        Devuelve el score completo y el diagnóstico.

        Esto será especialmente útil para el frontend porque permite
        mostrar al usuario:

            ATS Score: 78

            Keywords: 82%
            Required: 90%
            Skills: 75%
            Structure: 100%
            Metrics: 60%
            Action verbs: 80%

        además de:

            - keywords encontradas
            - keywords ausentes
            - requisitos obligatorios ausentes
            - recomendaciones
        """

        if not text:
            return self._empty_result()

        text_normalized = self._normalize_text(text)

        keyword_result = self._analyze_keywords(
            text_normalized=text_normalized,
            job_profile=job_profile,
            job_text=job_text,
        )

        required_result = self._analyze_required_keywords(
            text_normalized=text_normalized,
            job_profile=job_profile,
        )

        skill_result = self._analyze_skills(
            skills=skills,
            text_normalized=text_normalized,
            job_profile=job_profile,
        )

        structure_score = self._calculate_structure_score(
            text_normalized
        )

        metrics_score = self._calculate_metrics_score(
            text_normalized
        )

        action_score = self._calculate_action_verbs_score(
            text_normalized
        )

        readability_score = self._calculate_readability_score(
            text_normalized
        )

        keyword_score = (
            keyword_result["score"]
        )

        required_score = (
            required_result["score"]
        )

        skill_score = (
            skill_result["score"]
        )

        total = (
            keyword_score
            + required_score
            + skill_score
            + structure_score
            + metrics_score
            + action_score
            + readability_score
        )

        total = max(
            0,
            min(
                int(round(total)),
                self.MAX_SCORE,
            ),
        )

        recommendations = (
            self._generate_recommendations(
                keyword_result=keyword_result,
                required_result=required_result,
                skill_result=skill_result,
                structure_score=structure_score,
                metrics_score=metrics_score,
                action_score=action_score,
            )
        )

        return {
            "score": total,

            "components": {
                "keywords": round(
                    keyword_score,
                    2,
                ),
                "required_keywords": round(
                    required_score,
                    2,
                ),
                "skills": round(
                    skill_score,
                    2,
                ),
                "structure": round(
                    structure_score,
                    2,
                ),
                "metrics": round(
                    metrics_score,
                    2,
                ),
                "action_verbs": round(
                    action_score,
                    2,
                ),
                "readability": round(
                    readability_score,
                    2,
                ),
            },

            "keyword_analysis": keyword_result,

            "required_analysis": required_result,

            "skill_analysis": skill_result,

            "recommendations": recommendations,
        }

    # ================================================================
    # KEYWORD ANALYSIS
    # ================================================================

    def _calculate_keyword_score(
        self,
        text_normalized: str,
        job_profile: Dict[str, Any] | None,
        job_text: str | None,
    ) -> float:
        """
        Calcula la cobertura de keywords de la oferta.

        Si todavía no se proporciona una oferta, devuelve 0.

        Esto es intencional: un ATS score realmente adaptado a una
        oferta necesita comparar ambos documentos.
        """

        result = self._analyze_keywords(
            text_normalized=text_normalized,
            job_profile=job_profile,
            job_text=job_text,
        )

        return result["score"]

    def _analyze_keywords(
        self,
        text_normalized: str,
        job_profile: Dict[str, Any] | None,
        job_text: str | None,
    ) -> Dict[str, Any]:

        keywords = self._get_job_keywords(
            job_profile=job_profile,
            job_text=job_text,
        )

        if not keywords:
            return {
                "score": 0.0,
                "total": 0,
                "matched": 0,
                "missing": 0,
                "coverage": 0.0,
                "matched_keywords": [],
                "missing_keywords": [],
            }

        matched = []
        missing = []

        total_weight = 0.0
        matched_weight = 0.0

        for keyword in keywords:

            if isinstance(keyword, str):
                keyword_text = keyword
                importance = "medium"
                weight = 1.0

            else:
                keyword_text = str(
                    keyword.get(
                        "keyword",
                        keyword.get(
                            "text",
                            "",
                        ),
                    )
                ).strip()

                importance = keyword.get(
                    "importance",
                    "medium",
                )

                weight = self._keyword_weight(
                    importance
                )

            if not keyword_text:
                continue

            normalized_keyword = (
                self._normalize_text(
                    keyword_text
                )
            )

            if not normalized_keyword:
                continue

            total_weight += weight

            if self._contains_term(
                text_normalized,
                normalized_keyword,
            ):
                matched.append(
                    keyword_text
                )

                matched_weight += weight

            else:
                missing.append(
                    {
                        "keyword": keyword_text,
                        "importance": importance,
                    }
                )

        if total_weight == 0:
            coverage = 0.0

        else:
            coverage = (
                matched_weight
                / total_weight
                * 100
            )

        score = (
            coverage
            / 100
            * self.KEYWORD_WEIGHT
        )

        return {
            "score": score,
            "total": len(
                matched
            ) + len(
                missing
            ),
            "matched": len(
                matched
            ),
            "missing": len(
                missing
            ),
            "coverage": round(
                coverage,
                2,
            ),
            "matched_keywords": matched,
            "missing_keywords": missing,
        }

    # ================================================================
    # REQUIRED KEYWORDS
    # ================================================================

    def _calculate_required_score(
        self,
        text_normalized: str,
        job_profile: Dict[str, Any] | None,
    ) -> float:

        result = self._analyze_required_keywords(
            text_normalized=text_normalized,
            job_profile=job_profile,
        )

        return result["score"]

    def _analyze_required_keywords(
        self,
        text_normalized: str,
        job_profile: Dict[str, Any] | None,
    ) -> Dict[str, Any]:

        if not job_profile:
            return {
                "score": 0.0,
                "total": 0,
                "matched": 0,
                "missing": 0,
                "coverage": 0.0,
                "matched_requirements": [],
                "missing_requirements": [],
            }

        requirements = job_profile.get(
            "required_requirements",
            [],
        )

        if not isinstance(
            requirements,
            list,
        ):
            requirements = []

        matched = []
        missing = []

        for requirement in requirements:

            if isinstance(
                requirement,
                dict,
            ):
                value = requirement.get(
                    "text",
                    "",
                )

            else:
                value = str(
                    requirement
                )

            value = str(
                value
            ).strip()

            if not value:
                continue

            normalized = (
                self._normalize_text(
                    value
                )
            )

            if self._contains_term(
                text_normalized,
                normalized,
            ):
                matched.append(
                    value
                )

            else:
                missing.append(
                    value
                )

        total = (
            len(matched)
            + len(missing)
        )

        coverage = (
            len(matched)
            / total
            * 100
            if total
            else 0.0
        )

        return {
            "score": (
                coverage
                / 100
                * self.REQUIRED_WEIGHT
            ),
            "total": total,
            "matched": len(
                matched
            ),
            "missing": len(
                missing
            ),
            "coverage": round(
                coverage,
                2,
            ),
            "matched_requirements": matched,
            "missing_requirements": missing,
        }

    # ================================================================
    # SKILLS
    # ================================================================

    def _calculate_skill_score(
        self,
        skills: Dict[str, List[str]],
        text_normalized: str,
        job_profile: Dict[str, Any] | None,
    ) -> float:

        result = self._analyze_skills(
            skills=skills,
            text_normalized=text_normalized,
            job_profile=job_profile,
        )

        return result["score"]

    def _analyze_skills(
        self,
        skills: Dict[str, List[str]],
        text_normalized: str,
        job_profile: Dict[str, Any] | None,
    ) -> Dict[str, Any]:

        if not isinstance(
            skills,
            dict,
        ):
            skills = {}

        cv_skills = set()

        for category in (
            "hard_skills",
            "soft_skills",
            "languages",
        ):
            values = skills.get(
                category,
                [],
            )

            if isinstance(
                values,
                list,
            ):
                for value in values:
                    normalized = (
                        self._normalize_text(
                            str(value)
                        )
                    )

                    if normalized:
                        cv_skills.add(
                            normalized
                        )

        if not job_profile:

            generic_count = len(
                cv_skills
            )

            return {
                "score": min(
                    generic_count * 2,
                    self.SKILL_WEIGHT,
                ),
                "coverage": 0.0,
                "matched_skills": [],
                "missing_skills": [],
            }

        job_skills = job_profile.get(
            "skills",
            {},
        )

        if not isinstance(
            job_skills,
            dict,
        ):
            job_skills = {}

        job_skill_values = []

        for category in (
            "hard_skills",
            "soft_skills",
            "languages",
        ):

            values = job_skills.get(
                category,
                [],
            )

            if isinstance(
                values,
                list,
            ):
                job_skill_values.extend(
                    values
                )

        job_skill_values = [
            self._normalize_text(
                str(value)
            )
            for value in job_skill_values
            if str(value).strip()
        ]

        job_skill_values = list(
            dict.fromkeys(
                job_skill_values
            )
        )

        if not job_skill_values:
            return {
                "score": 0.0,
                "coverage": 0.0,
                "matched_skills": [],
                "missing_skills": [],
            }

        matched = []
        missing = []

        for skill in job_skill_values:

            if (
                skill in cv_skills
                or self._contains_term(
                    text_normalized,
                    skill,
                )
            ):
                matched.append(
                    skill
                )

            else:
                missing.append(
                    skill
                )

        coverage = (
            len(matched)
            / len(job_skill_values)
            * 100
        )

        score = (
            coverage
            / 100
            * self.SKILL_WEIGHT
        )

        return {
            "score": score,
            "coverage": round(
                coverage,
                2,
            ),
            "matched_skills": matched,
            "missing_skills": missing,
        }

    # ================================================================
    # STRUCTURE
    # ================================================================

    def _calculate_structure_score(
        self,
        text: str,
    ) -> float:

        sections = [
            (
                "experience",
                "experiencia",
            ),
            (
                "education",
                "formación",
                "formacion",
                "educacion",
            ),
            (
                "skills",
                "competencias",
                "habilidades",
                "aptitudes",
            ),
            (
                "projects",
                "proyectos",
            ),
            (
                "languages",
                "idiomas",
            ),
        ]

        found = 0

        for variants in sections:

            if any(
                self._contains_term(
                    text,
                    variant,
                )
                for variant in variants
            ):
                found += 1

        return (
            found
            / len(sections)
            * self.STRUCTURE_WEIGHT
        )

    # ================================================================
    # METRICS
    # ================================================================

    def _calculate_metrics_score(
        self,
        text: str,
    ) -> float:

        numbers = re.findall(
            r"\b\d+(?:[.,]\d+)?%?\b",
            text,
        )

        if not numbers:
            return 0.0

        return min(
            len(numbers),
            self.METRICS_WEIGHT,
        )

    # ================================================================
    # ACTION VERBS
    # ================================================================

    def _calculate_action_verbs_score(
        self,
        text: str,
    ) -> float:

        action_verbs = {
            # English
            "developed",
            "built",
            "created",
            "implemented",
            "optimized",
            "designed",
            "led",
            "managed",
            "improved",
            "automated",
            "analyzed",
            "coordinated",
            "delivered",
            "increased",
            "reduced",
            "launched",
            "maintained",
            "engineered",

            # Spanish
            "desarrollo",
            "desarrolló",
            "desarrollado",
            "implementó",
            "implementado",
            "gestionó",
            "gestionado",
            "lideró",
            "liderado",
            "creó",
            "creado",
            "optimizó",
            "optimizado",
            "analizó",
            "analizado",
            "diseñó",
            "diseñado",
            "mantuvo",
            "mantenido",
            "coordinó",
            "coordinado",
            "aumentó",
            "incrementó",
            "redujo",
            "lanzó",
            "automatizó",
        }

        found = 0

        for verb in action_verbs:

            if self._contains_term(
                text,
                verb,
            ):
                found += 1

        return min(
            found * 0.5,
            self.ACTION_VERBS_WEIGHT,
        )

    # ================================================================
    # READABILITY
    # ================================================================

    def _calculate_readability_score(
        self,
        text: str,
    ) -> float:

        if not text:
            return 0.0

        length = len(text)

        score = 0.0

        # CV demasiado corto.
        if length >= 800:
            score += 2.5

        # CV razonablemente desarrollado.
        if length >= 1500:
            score += 1.5

        # CV demasiado largo no recibe automáticamente más puntos.
        if length <= 10000:
            score += 1.0

        return min(
            score,
            self.READABILITY_WEIGHT,
        )

    # ================================================================
    # JOB KEYWORDS
    # ================================================================

    def _get_job_keywords(
        self,
        job_profile: Dict[str, Any] | None,
        job_text: str | None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene keywords preferentemente del JobProfileAnalyzer.

        Si no existe job_profile pero existe job_text, hacemos una
        extracción básica de términos.

        La integración completa con JobKeywordAnalyzer se puede
        conectar posteriormente desde el servicio que construye
        el JobProfile.
        """

        if job_profile:

            keywords = job_profile.get(
                "ats_keywords",
                [],
            )

            if isinstance(
                keywords,
                list,
            ) and keywords:
                return [
                    item
                    for item in keywords
                    if isinstance(
                        item,
                        dict,
                    )
                ]

            keywords = job_profile.get(
                "keywords",
                [],
            )

            if isinstance(
                keywords,
                list,
            ):
                return [
                    item
                    for item in keywords
                    if isinstance(
                        item,
                        dict,
                    )
                ]

        # Sin perfil estructurado no intentamos generar un listado
        # artificial de keywords aquí.
        #
        # JobKeywordAnalyzer será el responsable de esa tarea.

        return []

    def _keyword_weight(
        self,
        importance: str,
    ) -> float:

        return {
            "required": 3.0,
            "high": 2.5,
            "preferred": 1.5,
            "medium": 1.0,
            "low": 0.5,
        }.get(
            str(
                importance
            ).lower(),
            1.0,
        )

    # ================================================================
    # TEXT UTILITIES
    # ================================================================

    def _normalize_text(
        self,
        text: str,
    ) -> str:

        if not text:
            return ""

        text = str(
            text
        ).lower()

        text = unicodedata.normalize(
            "NFKD",
            text,
        )

        text = "".join(
            char
            for char in text
            if not unicodedata.combining(char)
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def _contains_term(
        self,
        text: str,
        term: str,
    ) -> bool:

        if not text or not term:
            return False

        escaped = re.escape(
            term
        )

        pattern = (
            rf"(?<![\w])"
            rf"{escaped}"
            rf"(?![\w])"
        )

        return re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ) is not None

    # ================================================================
    # RECOMMENDATIONS
    # ================================================================

    def _generate_recommendations(
        self,
        keyword_result: Dict[str, Any],
        required_result: Dict[str, Any],
        skill_result: Dict[str, Any],
        structure_score: float,
        metrics_score: float,
        action_score: float,
    ) -> List[Dict[str, Any]]:

        recommendations = []

        missing_required = (
            required_result.get(
                "missing_requirements",
                [],
            )
        )

        if missing_required:

            recommendations.append(
                {
                    "priority": "critical",
                    "type": "required_keywords",
                    "message": (
                        "Revisa los requisitos "
                        "obligatorios que no "
                        "aparecen en el CV."
                    ),
                    "items": missing_required[
                        :10
                    ],
                }
            )

        missing_keywords = (
            keyword_result.get(
                "missing_keywords",
                [],
            )
        )

        if missing_keywords:

            high_priority = [
                item
                for item in missing_keywords
                if item.get(
                    "importance"
                ) in {
                    "required",
                    "high",
                }
            ]

            if high_priority:

                recommendations.append(
                    {
                        "priority": "high",
                        "type": "ats_keywords",
                        "message": (
                            "Hay keywords "
                            "importantes de la "
                            "oferta que no aparecen "
                            "en el CV."
                        ),
                        "items": high_priority[
                            :15
                        ],
                    }
                )

        missing_skills = (
            skill_result.get(
                "missing_skills",
                [],
            )
        )

        if missing_skills:

            recommendations.append(
                {
                    "priority": "medium",
                    "type": "skills",
                    "message": (
                        "Estas habilidades "
                        "detectadas en la oferta "
                        "no aparecen claramente "
                        "en el CV."
                    ),
                    "items": missing_skills[
                        :15
                    ],
                }
            )

        if structure_score < (
            self.STRUCTURE_WEIGHT * 0.6
        ):

            recommendations.append(
                {
                    "priority": "medium",
                    "type": "structure",
                    "message": (
                        "Mejora la estructura del "
                        "CV utilizando secciones "
                        "claras y reconocibles "
                        "por sistemas ATS."
                    ),
                }
            )

        if metrics_score < (
            self.METRICS_WEIGHT * 0.4
        ):

            recommendations.append(
                {
                    "priority": "medium",
                    "type": "metrics",
                    "message": (
                        "Añade resultados "
                        "cuantificables cuando "
                        "sean reales y verificables."
                    ),
                }
            )

        if action_score < (
            self.ACTION_VERBS_WEIGHT * 0.4
        ):

            recommendations.append(
                {
                    "priority": "low",
                    "type": "action_verbs",
                    "message": (
                        "Describe la experiencia "
                        "utilizando verbos de acción "
                        "claros."
                    ),
                }
            )

        return recommendations

    # ================================================================
    # EMPTY RESULT
    # ================================================================

    def _empty_result(
        self,
    ) -> Dict[str, Any]:

        return {
            "score": 0,

            "components": {
                "keywords": 0,
                "required_keywords": 0,
                "skills": 0,
                "structure": 0,
                "metrics": 0,
                "action_verbs": 0,
                "readability": 0,
            },

            "keyword_analysis": {
                "score": 0,
                "total": 0,
                "matched": 0,
                "missing": 0,
                "coverage": 0,
                "matched_keywords": [],
                "missing_keywords": [],
            },

            "required_analysis": {
                "score": 0,
                "total": 0,
                "matched": 0,
                "missing": 0,
                "coverage": 0,
                "matched_requirements": [],
                "missing_requirements": [],
            },

            "skill_analysis": {
                "score": 0,
                "coverage": 0,
                "matched_skills": [],
                "missing_skills": [],
            },

            "recommendations": [],
        }