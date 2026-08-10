from __future__ import annotations

from typing import Any, Dict, List

from app.services.job_keyword_analyzer import (
    JobKeywordAnalyzer,
    job_keyword_analyzer,
)
from app.services.job_profile_analyzer import (
    JobProfileAnalyzer,
    job_profile_analyzer,
)
from app.services.skill_extractor import SkillExtractor


class JobMatcher:
    """
    Compares a candidate CV against a job offer.

    The matcher combines three complementary signals:

    1. SkillExtractor
       Detects known hard skills, soft skills and languages.

    2. JobKeywordAnalyzer
       Detects domain-agnostic keywords and phrases from the job
       description and compares them against the CV.

    3. JobProfileAnalyzer
       Builds a structured representation of the job offer:
       sector, seniority, responsibilities, requirements,
       ATS keywords, etc.

    Important design principle:

        SkillExtractor
            -> explicit known skills

        JobKeywordAnalyzer
            -> terminology and ATS keywords

        JobProfileAnalyzer
            -> semantic/job structure

        JobMatcher
            -> final compatibility score

    The matcher must never invent candidate skills.
    A missing keyword means that the CV does not provide evidence
    for that keyword.
    """

    # ------------------------------------------------------------------
    # SCORING WEIGHTS
    # ------------------------------------------------------------------

    # These weights are intentionally separated so that we can later
    # tune the algorithm without rewriting the matcher.

    SKILL_SCORE_WEIGHT = 40.0
    KEYWORD_SCORE_WEIGHT = 35.0
    REQUIRED_SCORE_WEIGHT = 20.0
    PROFILE_SCORE_WEIGHT = 5.0

    # ------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------

    def __init__(
        self,
        skill_extractor: SkillExtractor | None = None,
        keyword_analyzer: JobKeywordAnalyzer | None = None,
        profile_analyzer: JobProfileAnalyzer | None = None,
    ) -> None:

        self.skill_extractor = (
            skill_extractor
            or SkillExtractor()
        )

        self.keyword_analyzer = (
            keyword_analyzer
            or job_keyword_analyzer
        )

        self.profile_analyzer = (
            profile_analyzer
            or job_profile_analyzer
        )

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def extract_skills_from_text(
        self,
        text: str,
    ) -> Dict[str, List[str]]:
        """
        Extract known skills from a job description.

        This preserves the previous JobMatcher API.
        """

        if not text:
            return {
                "hard_skills": [],
                "soft_skills": [],
                "languages": [],
            }

        try:
            result = self.skill_extractor.extract_all(
                text,
                expand_concepts=False,
            )
        except Exception:
            return {
                "hard_skills": [],
                "soft_skills": [],
                "languages": [],
            }

        return {
            "hard_skills": sorted(
                set(
                    result.get(
                        "hard_skills",
                        [],
                    )
                )
            ),
            "soft_skills": sorted(
                set(
                    result.get(
                        "soft_skills",
                        [],
                    )
                )
            ),
            "languages": sorted(
                set(
                    result.get(
                        "languages",
                        [],
                    )
                )
            ),
        }

    # ------------------------------------------------------------------
    # LEGACY-COMPATIBLE MATCH
    # ------------------------------------------------------------------

    def match(
        self,
        cv_skills: Dict,
        job_text: str,
        cv_text: str | None = None,
    ) -> Dict[str, Any]:
        """
        Compare CV skills against a job description.

        Parameters
        ----------
        cv_skills:
            Existing structured skills extracted from the CV.

        job_text:
            Full job description.

        cv_text:
            Optional complete CV text.

            If provided, the matcher can perform keyword-level
            ATS analysis.

            If omitted, the matcher still performs the traditional
            skill matching.

        Returns
        -------
        dict
            Complete matching result.
        """

        if not job_text or not job_text.strip():
            raise ValueError(
                "job_text is required"
            )

        cv_skills = (
            cv_skills
            if isinstance(cv_skills, dict)
            else {}
        )

        # --------------------------------------------------------------
        # JOB SKILLS
        # --------------------------------------------------------------

        job_skills = (
            self.extract_skills_from_text(
                job_text
            )
        )

        # --------------------------------------------------------------
        # CV SKILLS
        # --------------------------------------------------------------

        cv_hard = self._normalize_set(
            cv_skills.get(
                "hard_skills",
                [],
            )
        )

        cv_soft = self._normalize_set(
            cv_skills.get(
                "soft_skills",
                [],
            )
        )

        cv_languages = self._normalize_set(
            cv_skills.get(
                "languages",
                [],
            )
        )

        # --------------------------------------------------------------
        # JOB SKILLS
        # --------------------------------------------------------------

        job_hard = self._normalize_set(
            job_skills.get(
                "hard_skills",
                [],
            )
        )

        job_soft = self._normalize_set(
            job_skills.get(
                "soft_skills",
                [],
            )
        )

        job_languages = self._normalize_set(
            job_skills.get(
                "languages",
                [],
            )
        )

        # --------------------------------------------------------------
        # MATCHES
        # --------------------------------------------------------------

        hard_match = (
            cv_hard & job_hard
        )

        soft_match = (
            cv_soft & job_soft
        )

        language_match = (
            cv_languages & job_languages
        )

        # --------------------------------------------------------------
        # GAPS
        # --------------------------------------------------------------

        missing_hard = (
            job_hard - cv_hard
        )

        missing_soft = (
            job_soft - cv_soft
        )

        missing_languages = (
            job_languages - cv_languages
        )

        # --------------------------------------------------------------
        # TRADITIONAL SKILL SCORE
        # --------------------------------------------------------------

        skill_score = self._calculate_skill_score(
            hard_match=hard_match,
            job_hard=job_hard,
            soft_match=soft_match,
            job_soft=job_soft,
            language_match=language_match,
            job_languages=job_languages,
        )

        # --------------------------------------------------------------
        # KEYWORD ANALYSIS
        # --------------------------------------------------------------

        keyword_analysis: Dict[str, Any] = {
            "keywords": [],
            "required_keywords": [],
            "preferred_keywords": [],
            "high_priority_keywords": [],
            "keyword_count": 0,
            "matched_count": 0,
            "missing_count": 0,
            "coverage": {
                "overall": 0.0,
                "required": 0.0,
                "preferred": 0.0,
                "high_priority": 0.0,
            },
        }

        if cv_text and cv_text.strip():

            keyword_analysis = (
                self.keyword_analyzer.compare(
                    job_text=job_text,
                    cv_text=cv_text,
                )
            )

        # --------------------------------------------------------------
        # KEYWORD SCORE
        # --------------------------------------------------------------

        keyword_score = (
            self._calculate_keyword_score(
                keyword_analysis
            )
        )

        # --------------------------------------------------------------
        # REQUIRED KEYWORD SCORE
        # --------------------------------------------------------------

        required_score = (
            self._calculate_required_score(
                keyword_analysis
            )
        )

        # --------------------------------------------------------------
        # JOB PROFILE
        # --------------------------------------------------------------

        job_profile = (
            self.profile_analyzer.analyze_sync(
                job_text
            )
        )

        # --------------------------------------------------------------
        # PROFILE SCORE
        # --------------------------------------------------------------

        profile_score = (
            self._calculate_profile_score(
                job_profile=job_profile,
                cv_skills=cv_skills,
                cv_text=cv_text,
            )
        )

        # --------------------------------------------------------------
        # FINAL SCORE
        # --------------------------------------------------------------

        final_score = (
            skill_score
            * (
                self.SKILL_SCORE_WEIGHT
                / 100.0
            )
            +
            keyword_score
            * (
                self.KEYWORD_SCORE_WEIGHT
                / 100.0
            )
            +
            required_score
            * (
                self.REQUIRED_SCORE_WEIGHT
                / 100.0
            )
            +
            profile_score
            * (
                self.PROFILE_SCORE_WEIGHT
                / 100.0
            )
        )

        final_score = round(
            min(
                max(
                    final_score,
                    0.0,
                ),
                100.0,
            ),
            2,
        )

        # --------------------------------------------------------------
        # RESULT
        # --------------------------------------------------------------

        return {
            "match_score": final_score,

            # ----------------------------------------------------------
            # Traditional skill matching
            # ----------------------------------------------------------

            "skill_score": round(
                skill_score,
                2,
            ),

            "hard_match": sorted(
                hard_match
            ),

            "soft_match": sorted(
                soft_match
            ),

            "language_match": sorted(
                language_match
            ),

            "missing_skills": sorted(
                missing_hard
            ),

            "missing_hard_skills": sorted(
                missing_hard
            ),

            "missing_soft_skills": sorted(
                missing_soft
            ),

            "missing_languages": sorted(
                missing_languages
            ),

            # ----------------------------------------------------------
            # Keyword / ATS analysis
            # ----------------------------------------------------------

            "keyword_score": round(
                keyword_score,
                2,
            ),

            "required_keyword_score": round(
                required_score,
                2,
            ),

            "keyword_analysis": keyword_analysis,

            "matched_keywords": [
                item
                for item in keyword_analysis.get(
                    "keywords",
                    [],
                )
                if item.get(
                    "matched",
                    False,
                )
            ],

            "missing_keywords": [
                item
                for item in keyword_analysis.get(
                    "keywords",
                    [],
                )
                if not item.get(
                    "matched",
                    False,
                )
            ],

            "required_keywords": (
                keyword_analysis.get(
                    "required_keywords",
                    [],
                )
            ),

            "missing_required_keywords": [
                item
                for item in keyword_analysis.get(
                    "required_keywords",
                    [],
                )
                if not item.get(
                    "matched",
                    False,
                )
            ],

            "preferred_keywords": (
                keyword_analysis.get(
                    "preferred_keywords",
                    [],
                )
            ),

            # ----------------------------------------------------------
            # Job profile
            # ----------------------------------------------------------

            "profile_score": round(
                profile_score,
                2,
            ),

            "job_profile": job_profile,

            # ----------------------------------------------------------
            # Job skills
            # ----------------------------------------------------------

            "job_skills_detected": {
                "hard_skills": sorted(
                    job_hard
                ),
                "soft_skills": sorted(
                    job_soft
                ),
                "languages": sorted(
                    job_languages
                ),
            },

            # ----------------------------------------------------------
            # Coverage
            # ----------------------------------------------------------

            "coverage": keyword_analysis.get(
                "coverage",
                {
                    "overall": 0.0,
                    "required": 0.0,
                    "preferred": 0.0,
                    "high_priority": 0.0,
                },
            ),
        }

    # ==================================================================
    # ADVANCED MATCH
    # ==================================================================

    def match_cv_text(
        self,
        cv_text: str,
        job_text: str,
        cv_skills: Dict[str, List[str]] | None = None,
    ) -> Dict[str, Any]:
        """
        Full CV-to-job analysis.

        This is the preferred method for the new architecture.

        If cv_skills are not supplied, they are extracted automatically
        from the CV text.
        """

        if not cv_text or not cv_text.strip():
            raise ValueError(
                "cv_text is required"
            )

        if not job_text or not job_text.strip():
            raise ValueError(
                "job_text is required"
            )

        if cv_skills is None:

            cv_skills = (
                self.skill_extractor.extract_all(
                    cv_text,
                    expand_concepts=False,
                )
            )

        return self.match(
            cv_skills=cv_skills,
            job_text=job_text,
            cv_text=cv_text,
        )

    # ==================================================================
    # ASYNC ADVANCED MATCH
    # ==================================================================

    async def match_with_ai(
        self,
        cv_text: str,
        job_text: str,
        cv_skills: Dict[str, List[str]] | None = None,
        use_ai: bool = True,
    ) -> Dict[str, Any]:
        """
        Advanced matching with optional AI job-profile enrichment.

        The deterministic matcher is always executed first.

        AI enrichment is deliberately kept optional because the
        deterministic matching system must remain usable without an
        external AI provider.
        """

        if not cv_text or not cv_text.strip():
            raise ValueError(
                "cv_text is required"
            )

        if not job_text or not job_text.strip():
            raise ValueError(
                "job_text is required"
            )

        if cv_skills is None:

            cv_skills = (
                self.skill_extractor.extract_all(
                    cv_text,
                    expand_concepts=False,
                )
            )

        result = self.match(
            cv_skills=cv_skills,
            job_text=job_text,
            cv_text=cv_text,
        )

        if not use_ai:
            return result

        # --------------------------------------------------------------
        # AI profile enrichment
        #
        # The analyzer itself decides whether an AI service exists.
        # --------------------------------------------------------------

        try:

            ai_profile = (
                await self.profile_analyzer.analyze(
                    job_text,
                    use_ai=True,
                )
            )

        except Exception:
            ai_profile = result.get(
                "job_profile",
                {},
            )

        result["job_profile"] = ai_profile

        # Recalculate profile-related information if useful.
        result["profile_score"] = round(
            self._calculate_profile_score(
                job_profile=ai_profile,
                cv_skills=cv_skills,
                cv_text=cv_text,
            ),
            2,
        )

        # Recalculate final score.
        result["match_score"] = round(
            self._calculate_final_score(
                skill_score=result.get(
                    "skill_score",
                    0.0,
                ),
                keyword_score=result.get(
                    "keyword_score",
                    0.0,
                ),
                required_score=result.get(
                    "required_keyword_score",
                    0.0,
                ),
                profile_score=result.get(
                    "profile_score",
                    0.0,
                ),
            ),
            2,
        )

        return result

    # ==================================================================
    # SKILL SCORING
    # ==================================================================

    def _calculate_skill_score(
        self,
        hard_match: set[str],
        job_hard: set[str],
        soft_match: set[str],
        job_soft: set[str],
        language_match: set[str],
        job_languages: set[str],
    ) -> float:
        """
        Calculate the traditional skill score.

        Internally this is normalized to 0-100.
        """

        hard_score = (
            len(hard_match)
            / len(job_hard)
            * 70.0
            if job_hard
            else 0.0
        )

        soft_score = (
            len(soft_match)
            / len(job_soft)
            * 20.0
            if job_soft
            else 0.0
        )

        language_score = (
            len(language_match)
            / len(job_languages)
            * 10.0
            if job_languages
            else 0.0
        )

        total = (
            hard_score
            + soft_score
            + language_score
        )

        # If the job contains no skills recognized by SkillExtractor,
        # don't penalize the candidate with a meaningless zero.
        #
        # The general keyword analyzer will handle the domain-agnostic
        # comparison.
        if (
            not job_hard
            and not job_soft
            and not job_languages
        ):
            return 0.0

        return min(
            total,
            100.0,
        )

    # ==================================================================
    # KEYWORD SCORING
    # ==================================================================

    def _calculate_keyword_score(
        self,
        keyword_analysis: Dict[str, Any],
    ) -> float:
        """
        Calculate general keyword coverage.

        Unlike SkillExtractor, this works with arbitrary professional
        terminology and therefore also supports domains such as:

            agriculture
            agronomy
            engineering
            healthcare
            finance
            law
            education
            manufacturing
            etc.
        """

        coverage = keyword_analysis.get(
            "coverage",
            {},
        )

        overall = float(
            coverage.get(
                "overall",
                0.0,
            )
        )

        preferred = float(
            coverage.get(
                "preferred",
                0.0,
            )
        )

        high_priority = float(
            coverage.get(
                "high_priority",
                0.0,
            )
        )

        # General keyword coverage is weighted mostly by overall
        # terminology, while high-priority terms receive extra weight.
        score = (
            overall * 0.50
            + high_priority * 0.35
            + preferred * 0.15
        )

        return min(
            max(
                score,
                0.0,
            ),
            100.0,
        )

    # ==================================================================
    # REQUIRED KEYWORD SCORING
    # ==================================================================

    def _calculate_required_score(
        self,
        keyword_analysis: Dict[str, Any],
    ) -> float:
        """
        Required keywords are particularly important for ATS-oriented
        matching.

        A CV that misses several explicitly required terms should not
        receive the same score as one that matches them.
        """

        required_keywords = (
            keyword_analysis.get(
                "required_keywords",
                [],
            )
        )

        if not required_keywords:
            return 100.0

        matched = sum(
            1
            for item in required_keywords
            if item.get(
                "matched",
                False,
            )
        )

        return round(
            matched
            / len(required_keywords)
            * 100.0,
            2,
        )

    # ==================================================================
    # PROFILE SCORING
    # ==================================================================

    def _calculate_profile_score(
        self,
        job_profile: Dict[str, Any],
        cv_skills: Dict[str, Any],
        cv_text: str | None,
    ) -> float:
        """
        Calculate a small semantic/profile consistency score.

        This intentionally has low weight.

        We do NOT want the profile classifier to dominate the actual
        evidence-based keyword and skill matching.
        """

        if not isinstance(
            job_profile,
            dict,
        ):
            return 0.0

        score_parts: list[float] = []

        # --------------------------------------------------------------
        # Sector
        # --------------------------------------------------------------

        sector = job_profile.get(
            "sector"
        )

        if sector:
            score_parts.append(
                self._sector_evidence_score(
                    sector=sector,
                    cv_text=cv_text,
                )
            )

        # --------------------------------------------------------------
        # Seniority
        # --------------------------------------------------------------

        seniority = job_profile.get(
            "seniority"
        )

        if seniority:
            score_parts.append(
                self._seniority_evidence_score(
                    seniority=seniority,
                    cv_text=cv_text,
                )
            )

        # --------------------------------------------------------------
        # Requirements
        # --------------------------------------------------------------

        required_requirements = (
            job_profile.get(
                "required_requirements",
                [],
            )
        )

        if cv_text and required_requirements:

            normalized_cv = (
                cv_text.lower()
            )

            matches = 0

            for requirement in (
                required_requirements
            ):

                if isinstance(
                    requirement,
                    dict,
                ):
                    requirement_text = str(
                        requirement.get(
                            "text",
                            "",
                        )
                    ).strip()

                else:
                    requirement_text = str(
                        requirement
                    ).strip()

                if not requirement_text:
                    continue

                if (
                    requirement_text.lower()
                    in normalized_cv
                ):
                    matches += 1

            valid_requirements = [
                item
                for item in required_requirements
                if (
                    isinstance(
                        item,
                        dict,
                    )
                    and str(
                        item.get(
                            "text",
                            "",
                        )
                    ).strip()
                )
                or (
                    not isinstance(
                        item,
                        dict,
                    )
                    and str(item).strip()
                )
            ]

            if valid_requirements:

                score_parts.append(
                    matches
                    / len(
                        valid_requirements
                    )
                    * 100.0
                )

        if not score_parts:
            return 0.0

        return min(
            max(
                sum(score_parts)
                / len(score_parts),
                0.0,
            ),
            100.0,
        )

    # ==================================================================
    # SECTOR EVIDENCE
    # ==================================================================

    def _sector_evidence_score(
        self,
        sector: str,
        cv_text: str | None,
    ) -> float:
        """
        Conservative sector evidence check.

        This does NOT infer that a candidate belongs to a sector merely
        because the job does.

        It only looks for explicit evidence in the CV.
        """

        if not cv_text:
            return 0.0

        normalized_cv = (
            cv_text.lower()
        )

        signals = {
            "technology": (
                "software",
                "developer",
                "programador",
                "programadora",
                "python",
                "javascript",
                "java",
                "sql",
                "programación",
                "programacion",
            ),
            "agriculture": (
                "agriculture",
                "agricultural",
                "agronomy",
                "agronomía",
                "agronomia",
                "agronomist",
                "agricultor",
                "agricultura",
                "cultivo",
                "cultivos",
                "riego",
                "irrigation",
                "fertilización",
                "fertilizacion",
            ),
            "engineering": (
                "engineer",
                "engineering",
                "ingeniero",
                "ingeniera",
                "ingeniería",
                "ingenieria",
            ),
            "finance": (
                "finance",
                "financial",
                "accounting",
                "accountant",
                "finanzas",
                "contabilidad",
                "contable",
            ),
            "healthcare": (
                "healthcare",
                "medical",
                "nurse",
                "nursing",
                "médico",
                "medico",
                "enfermería",
                "enfermeria",
            ),
            "marketing": (
                "marketing",
                "seo",
                "sem",
                "social media",
                "marketing digital",
            ),
            "sales": (
                "sales",
                "ventas",
                "commercial",
                "comercial",
                "business development",
            ),
            "legal": (
                "lawyer",
                "legal",
                "abogado",
                "abogada",
                "derecho",
                "compliance",
            ),
            "logistics": (
                "logistics",
                "supply chain",
                "warehouse",
                "logística",
                "logistica",
                "almacén",
                "almacen",
            ),
            "human_resources": (
                "human resources",
                "recruitment",
                "talent acquisition",
                "recursos humanos",
                "selección",
                "seleccion",
            ),
            "hospitality": (
                "hospitality",
                "hotel",
                "restaurant",
                "hostelería",
                "hosteleria",
                "hotelero",
            ),
        }

        sector_signals = signals.get(
            str(sector).lower(),
            (),
        )

        if not sector_signals:
            return 0.0

        matches = sum(
            1
            for signal in sector_signals
            if signal in normalized_cv
        )

        if matches == 0:
            return 0.0

        if matches >= 3:
            return 100.0

        if matches == 2:
            return 75.0

        return 50.0

    # ==================================================================
    # SENIORITY EVIDENCE
    # ==================================================================

    def _seniority_evidence_score(
        self,
        seniority: str,
        cv_text: str | None,
    ) -> float:
        """
        Very conservative seniority evidence.

        Seniority is not a hard rejection criterion because job titles
        and years of experience can vary substantially across domains.
        """

        if not cv_text:
            return 0.0

        normalized_cv = (
            cv_text.lower()
        )

        patterns = {
            "intern": (
                "intern",
                "internship",
                "trainee",
                "becario",
                "becaria",
                "prácticas",
                "practicas",
            ),
            "junior": (
                "junior",
                "jr",
                "entry level",
                "graduate",
                "early career",
            ),
            "mid": (
                "mid-level",
                "mid level",
                "intermediate",
            ),
            "senior": (
                "senior",
                "sr",
                "senior-level",
                "senior level",
            ),
            "lead": (
                "lead",
                "team lead",
                "tech lead",
                "technical lead",
            ),
            "manager": (
                "manager",
                "director",
                "head of",
                "gerente",
            ),
        }

        level_patterns = patterns.get(
            str(seniority).lower(),
            (),
        )

        if any(
            pattern in normalized_cv
            for pattern in level_patterns
        ):
            return 100.0

        # Experience years can also provide supporting evidence.
        if str(seniority).lower() in {
            "senior",
            "lead",
            "manager",
        }:

            if self._cv_has_experience_years(
                normalized_cv,
                minimum=5,
            ):
                return 75.0

        if str(seniority).lower() == "mid":

            if self._cv_has_experience_years(
                normalized_cv,
                minimum=2,
            ):
                return 75.0

        return 0.0

    # ==================================================================
    # EXPERIENCE DETECTION
    # ==================================================================

    def _cv_has_experience_years(
        self,
        cv_text: str,
        minimum: int,
    ) -> bool:
        """
        Detect explicit years of experience in the CV.

        Examples:

            5 years experience
            5 years of experience
            5 años de experiencia
            7+ years
            más de 5 años
        """

        patterns = (
            r"(\d+)\+?\s+years?\s+(?:of\s+)?experience",
            r"(\d+)\+?\s+anos?\s+de\s+experiencia",
            r"(\d+)\+?\s+años?\s+de\s+experiencia",
            r"more\s+than\s+(\d+)\s+years?",
            r"más\s+de\s+(\d+)\s+años?",
            r"mas\s+de\s+(\d+)\s+anos?",
        )

        for pattern in patterns:

            matches = __import__(
                "re"
            ).finditer(
                pattern,
                cv_text,
                flags=__import__(
                    "re"
                ).IGNORECASE,
            )

            for match in matches:

                try:
                    years = int(
                        match.group(
                            1
                        )
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                if years >= minimum:
                    return True

        return False

    # ==================================================================
    # FINAL SCORE
    # ==================================================================

    def _calculate_final_score(
        self,
        skill_score: float,
        keyword_score: float,
        required_score: float,
        profile_score: float,
    ) -> float:
        """
        Calculate the final weighted compatibility score.
        """

        score = (
            skill_score
            * (
                self.SKILL_SCORE_WEIGHT
                / 100.0
            )
            +
            keyword_score
            * (
                self.KEYWORD_SCORE_WEIGHT
                / 100.0
            )
            +
            required_score
            * (
                self.REQUIRED_SCORE_WEIGHT
                / 100.0
            )
            +
            profile_score
            * (
                self.PROFILE_SCORE_WEIGHT
                / 100.0
            )
        )

        return min(
            max(
                score,
                0.0,
            ),
            100.0,
        )

    # ==================================================================
    # NORMALIZATION
    # ==================================================================

    def _normalize_set(
        self,
        values: Any,
    ) -> set[str]:
        """
        Normalize a list of skills for set comparison.
        """

        if not isinstance(
            values,
            (list, tuple, set),
        ):
            return set()

        result: set[str] = set()

        for value in values:

            if value is None:
                continue

            normalized = (
                str(value)
                .strip()
                .lower()
            )

            if normalized:
                result.add(
                    normalized
                )

        return result


# ============================================================================
# MODULE-LEVEL INSTANCE
# ============================================================================

job_matcher = JobMatcher()