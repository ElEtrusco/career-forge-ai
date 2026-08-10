from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from app.services.job_keyword_analyzer import (
    JobKeywordAnalyzer,
    job_keyword_analyzer,
)

from app.services.skill_extractor import SkillExtractor


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class JobRequirement:
    """
    A requirement detected in a job offer.

    This is deliberately domain-agnostic. It can represent:
        - technical skills
        - agricultural knowledge
        - engineering requirements
        - healthcare requirements
        - education
        - experience
        - languages
        - certifications
        - other professional requirements
    """

    text: str
    category: str
    importance: str
    required: bool
    evidence: str | None = None


@dataclass
class JobProfile:
    """
    Structured representation of a job offer.
    """

    title: str | None = None

    company: str | None = None

    sector: str | None = None

    domain: str | None = None

    role_family: str | None = None

    seniority: str | None = None

    location: str | None = None

    work_mode: str | None = None

    employment_type: str | None = None

    summary: str | None = None

    responsibilities: list[str] = field(
        default_factory=list
    )

    required_requirements: list[JobRequirement] = field(
        default_factory=list
    )

    preferred_requirements: list[JobRequirement] = field(
        default_factory=list
    )

    skills: dict[str, list[str]] = field(
        default_factory=lambda: {
            "hard_skills": [],
            "soft_skills": [],
            "languages": [],
            "certifications": [],
        }
    )

    experience_requirements: list[str] = field(
        default_factory=list
    )

    education_requirements: list[str] = field(
        default_factory=list
    )

    language_requirements: list[str] = field(
        default_factory=list
    )

    certification_requirements: list[str] = field(
        default_factory=list
    )

    keywords: list[dict[str, Any]] = field(
        default_factory=list
    )

    ats_keywords: list[dict[str, Any]] = field(
        default_factory=list
    )

    source_text: str = ""


# ============================================================================
# JOB PROFILE ANALYZER
# ============================================================================


class JobProfileAnalyzer:
    """
    Converts an unstructured job description into a structured JobProfile.

    Architecture:

        Job description
              |
              +--> JobKeywordAnalyzer
              |
              +--> SkillExtractor
              |
              +--> deterministic analysis
              |
              +--> optional AI enrichment
              |
              v
          JobProfile

    Important design principle:

        Deterministic extraction
        ------------------------
        Provides evidence directly present in the offer.

        AI enrichment
        -------------
        Provides semantic interpretation.

    The AI layer must never be used to invent candidate skills.
    """

    # ------------------------------------------------------------------
    # SENIORITY
    # ------------------------------------------------------------------

    SENIORITY_PATTERNS = {
        "intern": (
            "intern",
            "internship",
            "internship program",
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
            "entry-level",
            "graduate",
            "early career",
            "sin experiencia",
        ),
        "mid": (
            "mid",
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
            "technical lead",
            "tech lead",
            "responsable de equipo",
            "jefe de equipo",
            "jefa de equipo",
        ),
        "manager": (
            "manager",
            "people manager",
            "engineering manager",
            "hiring manager",
            "gerente",
            "director",
            "directora",
            "head of",
        ),
    }

    # ------------------------------------------------------------------
    # WORK MODE
    # ------------------------------------------------------------------

    WORK_MODE_PATTERNS = {
        "remote": (
            "remote",
            "remotely",
            "fully remote",
            "100% remote",
            "remote position",
            "teletrabajo",
            "trabajo remoto",
            "trabajo en remoto",
        ),
        "hybrid": (
            "hybrid",
            "hybrid work",
            "hybrid model",
            "modelo híbrido",
            "modelo hibrido",
            "híbrido",
            "hibrido",
        ),
        "onsite": (
            "on-site",
            "onsite",
            "on site",
            "office-based",
            "presencial",
            "trabajo presencial",
        ),
    }

    # ------------------------------------------------------------------
    # EMPLOYMENT TYPE
    # ------------------------------------------------------------------

    EMPLOYMENT_PATTERNS = {
        "full_time": (
            "full time",
            "full-time",
            "fulltime",
            "jornada completa",
            "tiempo completo",
        ),
        "part_time": (
            "part time",
            "part-time",
            "parttime",
            "media jornada",
            "tiempo parcial",
        ),
        "temporary": (
            "temporary",
            "temporary contract",
            "fixed term",
            "fixed-term",
            "contrato temporal",
            "temporal",
            "contrato de duración determinada",
        ),
        "internship": (
            "internship",
            "intern",
            "prácticas",
            "practicas",
            "becario",
            "becaria",
        ),
        "freelance": (
            "freelance",
            "contractor",
            "independent contractor",
            "autónomo",
            "autonomo",
        ),
    }

    # ------------------------------------------------------------------
    # SECTION DETECTION
    # ------------------------------------------------------------------

    SECTION_PATTERNS = {
        "responsibilities": (
            "responsibilities",
            "responsibility",
            "what you will do",
            "what you'll do",
            "what you will be doing",
            "duties",
            "key responsibilities",
            "responsabilidades",
            "funciones",
            "tareas",
            "qué harás",
            "que harás",
        ),
        "requirements": (
            "requirements",
            "required",
            "qualifications",
            "required qualifications",
            "basic qualifications",
            "minimum qualifications",
            "requisitos",
            "requisitos mínimos",
            "requisitos minimos",
            "requisitos obligatorios",
            "imprescindible",
            "obligatorio",
            "obligatoria",
        ),
        "preferred": (
            "preferred",
            "preferred qualifications",
            "preferred requirements",
            "nice to have",
            "nice-to-have",
            "desired",
            "desired qualifications",
            "bonus",
            "deseable",
            "valorable",
            "se valorará",
            "se valorara",
        ),
        "education": (
            "education",
            "educational background",
            "degree",
            "education requirements",
            "academic background",
            "educación",
            "educacion",
            "formación",
            "formacion",
            "titulación",
            "titulacion",
        ),
        "experience": (
            "experience",
            "professional experience",
            "years of experience",
            "required experience",
            "experiencia",
            "experiencia profesional",
            "años de experiencia",
            "anos de experiencia",
        ),
        "skills": (
            "skills",
            "technical skills",
            "required skills",
            "competencies",
            "competences",
            "habilidades",
            "competencias",
            "conocimientos",
            "capacidades",
        ),
        "languages": (
            "languages",
            "language requirements",
            "idiomas",
            "idiomas requeridos",
            "lenguas",
        ),
        "certifications": (
            "certifications",
            "certification",
            "certificates",
            "certificaciones",
            "certificación",
            "certificacion",
            "certificados",
        ),
        "benefits": (
            "benefits",
            "perks",
            "what we offer",
            "qué ofrecemos",
            "que ofrecemos",
            "beneficios",
        ),
    }

    # ------------------------------------------------------------------
    # SECTOR SIGNALS
    #
    # This is intentionally conservative.
    #
    # We don't want a huge hard-coded dictionary because the project must
    # support many professions.
    #
    # The AI layer can later provide richer classification.
    # ------------------------------------------------------------------

    SECTOR_SIGNALS = {
        "technology": (
            "software engineer",
            "software developer",
            "backend developer",
            "frontend developer",
            "full stack",
            "full-stack",
            "devops",
            "data engineer",
            "data scientist",
            "machine learning",
            "cloud engineer",
            "programador",
            "programadora",
            "desarrollador",
            "desarrolladora",
        ),
        "agriculture": (
            "agronom",
            "agriculture",
            "agricultural",
            "crop management",
            "crop production",
            "irrigation",
            "precision agriculture",
            "agricultura",
            "agrícola",
            "agricola",
            "cultivos",
            "cultivo",
            "riego",
            "fertilización",
            "fertilizacion",
            "fitosanitario",
            "fitosanitaria",
        ),
        "engineering": (
            "mechanical engineer",
            "civil engineer",
            "industrial engineer",
            "electrical engineer",
            "chemical engineer",
            "ingeniero mecánico",
            "ingeniero mecanico",
            "ingeniero civil",
            "ingeniería industrial",
            "ingenieria industrial",
            "ingeniero eléctrico",
            "ingeniero electrico",
            "ingeniero químico",
            "ingeniero quimico",
        ),
        "finance": (
            "finance",
            "financial",
            "accounting",
            "accountant",
            "contabilidad",
            "contable",
            "finanzas",
            "auditoría",
            "auditoria",
            "auditor",
        ),
        "healthcare": (
            "healthcare",
            "nurse",
            "nursing",
            "doctor",
            "physician",
            "medical",
            "hospital",
            "enfermero",
            "enfermera",
            "enfermería",
            "enfermeria",
            "sanidad",
            "médico",
            "medico",
            "medicina",
            "hospitalario",
        ),
        "marketing": (
            "marketing",
            "digital marketing",
            "content marketing",
            "seo",
            "sem",
            "social media marketing",
            "marketing digital",
            "marketing de contenidos",
        ),
        "sales": (
            "sales",
            "sales representative",
            "account executive",
            "business development",
            "ventas",
            "comercial",
            "desarrollo de negocio",
        ),
        "legal": (
            "lawyer",
            "attorney",
            "legal counsel",
            "legal advisor",
            "compliance",
            "abogado",
            "abogada",
            "jurídico",
            "juridico",
            "derecho",
            "asesor jurídico",
            "asesor juridico",
        ),
        "logistics": (
            "logistics",
            "supply chain",
            "warehouse",
            "procurement",
            "logística",
            "logistica",
            "cadena de suministro",
            "almacén",
            "almacen",
            "compras",
        ),
        "human_resources": (
            "human resources",
            "hr",
            "talent acquisition",
            "recruitment",
            "people operations",
            "recursos humanos",
            "selección",
            "seleccion",
            "reclutamiento",
        ),
        "hospitality": (
            "hotel",
            "hospitality",
            "restaurant",
            "front desk",
            "guest services",
            "hostelería",
            "hosteleria",
            "hotelero",
            "recepción",
            "recepcion",
        ),
    }

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __init__(
        self,
        keyword_analyzer: JobKeywordAnalyzer | None = None,
        skill_extractor: SkillExtractor | None = None,
        ai_service: Any | None = None,
    ) -> None:

        self.keyword_analyzer = (
            keyword_analyzer
            or job_keyword_analyzer
        )

        self.skill_extractor = (
            skill_extractor
            or SkillExtractor()
        )

        self.ai_service = ai_service

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def analyze(
        self,
        job_text: str,
        use_ai: bool = False,
    ) -> dict[str, Any]:
        """
        Analyze a complete job description.

        Deterministic analysis always runs.

        AI enrichment is optional and only runs when:
            use_ai=True
            AND
            an AI service was supplied.
        """

        self._validate_job_text(
            job_text
        )

        clean_text = self._clean_text(
            job_text
        )

        profile = self._build_deterministic_profile(
            clean_text
        )

        if use_ai and self.ai_service:
            profile = await self._enrich_with_ai(
                profile
            )

        return self._serialize_profile(
            profile
        )

    def analyze_sync(
        self,
        job_text: str,
    ) -> dict[str, Any]:
        """
        Synchronous deterministic analysis.

        This is useful for:
            - tests
            - local processing
            - API endpoints that don't require AI
            - debugging
        """

        self._validate_job_text(
            job_text
        )

        clean_text = self._clean_text(
            job_text
        )

        profile = self._build_deterministic_profile(
            clean_text
        )

        return self._serialize_profile(
            profile
        )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def _validate_job_text(
        self,
        job_text: str,
    ) -> None:

        if not isinstance(
            job_text,
            str,
        ):
            raise TypeError(
                "job_text must be a string"
            )

        if not job_text.strip():
            raise ValueError(
                "Job description is required"
            )

    # =========================================================================
    # DETERMINISTIC PROFILE
    # =========================================================================

    def _build_deterministic_profile(
        self,
        job_text: str,
    ) -> JobProfile:

        keyword_analysis = (
            self.keyword_analyzer.analyze(
                job_text
            )
        )

        # Existing extractor is used as an additional signal.
        #
        # It is NOT the only source of skills because the project must
        # support domains such as agriculture, healthcare, finance, etc.
        extracted_skills = (
            self._extract_skills_safely(
                job_text
            )
        )

        sections = self._split_sections(
            job_text
        )

        title = self._extract_title(
            job_text
        )

        responsibilities = (
            self._extract_list_from_section(
                sections,
                "responsibilities",
            )
        )

        experience_requirements = (
            self._extract_list_from_section(
                sections,
                "experience",
            )
        )

        education_requirements = (
            self._extract_list_from_section(
                sections,
                "education",
            )
        )

        language_requirements = (
            self._extract_language_requirements(
                job_text
            )
        )

        certification_requirements = (
            self._extract_list_from_section(
                sections,
                "certifications",
            )
        )

        required_requirements = (
            self._build_requirements(
                keyword_analysis.get(
                    "required_keywords",
                    [],
                ),
                required=True,
            )
        )

        preferred_requirements = (
            self._build_requirements(
                keyword_analysis.get(
                    "preferred_keywords",
                    [],
                ),
                required=False,
            )
        )

        profile = JobProfile(
            title=title,
            sector=self._infer_sector(
                job_text
            ),
            seniority=self._detect_seniority(
                job_text,
                title,
            ),
            work_mode=self._detect_work_mode(
                job_text
            ),
            employment_type=(
                self._detect_employment_type(
                    job_text
                )
            ),
            responsibilities=responsibilities,
            required_requirements=(
                required_requirements
            ),
            preferred_requirements=(
                preferred_requirements
            ),
            skills=extracted_skills,
            experience_requirements=(
                experience_requirements
            ),
            education_requirements=(
                education_requirements
            ),
            language_requirements=(
                language_requirements
            ),
            certification_requirements=(
                certification_requirements
            ),
            keywords=keyword_analysis.get(
                "keywords",
                [],
            ),
            ats_keywords=self._build_ats_keywords(
                keyword_analysis
            ),
            source_text=job_text,
        )

        return profile

    # =========================================================================
    # TEXT CLEANING
    # =========================================================================

    def _clean_text(
        self,
        text: str,
    ) -> str:

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    # =========================================================================
    # TITLE
    # =========================================================================

    def _extract_title(
        self,
        text: str,
    ) -> str | None:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return None

        title_markers = (
            "job title",
            "position",
            "role",
            "title",
            "puesto",
            "cargo",
            "vacante",
            "posición",
            "posicion",
        )

        for line in lines[:20]:

            for marker in title_markers:

                pattern = (
                    rf"^{re.escape(marker)}"
                    rf"\s*[:\-]\s*(.+)$"
                )

                match = re.search(
                    pattern,
                    line,
                    flags=re.IGNORECASE,
                )

                if match:
                    value = match.group(
                        1
                    ).strip()

                    if value:
                        return value

        first_line = lines[0]

        if (
            len(first_line) <= 100
            and len(first_line.split()) <= 12
            and not first_line.endswith(".")
        ):
            return first_line

        return None

    # =========================================================================
    # SENIORITY
    # =========================================================================

    def _detect_seniority(
        self,
        text: str,
        title: str | None = None,
    ) -> str | None:

        haystack = (
            f"{title or ''} {text}"
        ).lower()

        matches: list[
            tuple[str, int]
        ] = []

        for level, patterns in (
            self.SENIORITY_PATTERNS.items()
        ):

            score = 0

            for pattern in patterns:

                if pattern in haystack:
                    score += 1

            if score:
                matches.append(
                    (
                        level,
                        score,
                    )
                )

        if not matches:
            return None

        matches.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return matches[0][0]

    # =========================================================================
    # WORK MODE
    # =========================================================================

    def _detect_work_mode(
        self,
        text: str,
    ) -> str | None:

        normalized = text.lower()

        matches: list[
            tuple[str, int]
        ] = []

        for mode, patterns in (
            self.WORK_MODE_PATTERNS.items()
        ):

            score = sum(
                1
                for pattern in patterns
                if pattern in normalized
            )

            if score:
                matches.append(
                    (
                        mode,
                        score,
                    )
                )

        if not matches:
            return None

        matches.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return matches[0][0]

    # =========================================================================
    # EMPLOYMENT TYPE
    # =========================================================================

    def _detect_employment_type(
        self,
        text: str,
    ) -> str | None:

        normalized = text.lower()

        matches: list[
            tuple[str, int]
        ] = []

        for employment_type, patterns in (
            self.EMPLOYMENT_PATTERNS.items()
        ):

            score = sum(
                1
                for pattern in patterns
                if pattern in normalized
            )

            if score:
                matches.append(
                    (
                        employment_type,
                        score,
                    )
                )

        if not matches:
            return None

        matches.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return matches[0][0]

    # =========================================================================
    # SECTION PARSING
    # =========================================================================

    def _split_sections(
        self,
        text: str,
    ) -> dict[str, list[str]]:

        sections: dict[
            str,
            list[str],
        ] = {}

        current_section = "other"

        for raw_line in text.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            detected = self._detect_section(
                line
            )

            if detected:

                current_section = detected

                sections.setdefault(
                    current_section,
                    [],
                )

                continue

            sections.setdefault(
                current_section,
                [],
            ).append(line)

        return sections

    def _detect_section(
        self,
        line: str,
    ) -> str | None:

        normalized = (
            line.lower()
            .strip()
            .rstrip(":")
            .strip()
        )

        if len(normalized) > 100:
            return None

        for section, patterns in (
            self.SECTION_PATTERNS.items()
        ):

            for pattern in patterns:

                if normalized == pattern:
                    return section

                if normalized.startswith(
                    pattern + ":"
                ):
                    return section

        return None

    def _extract_list_from_section(
        self,
        sections: dict[str, list[str]],
        section_name: str,
    ) -> list[str]:

        lines = sections.get(
            section_name,
            [],
        )

        results: list[str] = []

        for line in lines:

            # A job description often contains bullet points.
            # Some sources provide plain paragraphs.
            cleaned = self._clean_list_item(
                line
            )

            if not cleaned:
                continue

            if len(cleaned) < 3:
                continue

            results.append(
                cleaned
            )

        return self._deduplicate(
            results
        )

    def _clean_list_item(
        self,
        value: str,
    ) -> str:

        value = value.strip()

        value = re.sub(
            r"^[•●▪◦\-*]+\s*",
            "",
            value,
        )

        value = re.sub(
            r"^\d+[\.)]\s*",
            "",
            value,
        )

        return value.strip()

    # =========================================================================
    # SKILL EXTRACTION
    # =========================================================================

    def _extract_skills_safely(
        self,
        text: str,
    ) -> dict[str, list[str]]:

        default_result = {
            "hard_skills": [],
            "soft_skills": [],
            "languages": [],
            "certifications": [],
        }

        try:
            result = (
                self.skill_extractor.extract_all(
                    text,
                    expand_concepts=False,
                )
            )

        except Exception:
            return default_result

        if not isinstance(
            result,
            dict,
        ):
            return default_result

        for key in default_result:

            value = result.get(
                key,
                [],
            )

            if isinstance(
                value,
                list,
            ):
                default_result[key] = (
                    self._deduplicate(
                        [
                            str(item)
                            for item in value
                            if str(item).strip()
                        ]
                    )
                )

        return default_result

    # =========================================================================
    # REQUIREMENTS
    # =========================================================================

    def _build_requirements(
        self,
        keywords: list[dict[str, Any]],
        required: bool,
    ) -> list[JobRequirement]:

        results: list[
            JobRequirement
        ] = []

        for keyword in keywords:

            if not isinstance(
                keyword,
                dict,
            ):
                continue

            text = keyword.get(
                "text"
            )

            if not text:
                continue

            category = keyword.get(
                "category",
                "skill_or_term",
            )

            importance = (
                "required"
                if required
                else "preferred"
            )

            results.append(
                JobRequirement(
                    text=str(text),
                    category=str(
                        category
                    ),
                    importance=importance,
                    required=required,
                )
            )

        return self._deduplicate_requirements(
            results
        )

    # =========================================================================
    # LANGUAGES
    # =========================================================================

    def _extract_language_requirements(
        self,
        text: str,
    ) -> list[str]:

        try:

            languages = (
                self.skill_extractor.extract_languages(
                    text
                )
            )

        except Exception:
            return []

        if not isinstance(
            languages,
            list,
        ):
            return []

        return self._deduplicate(
            [
                str(language)
                for language in languages
                if str(language).strip()
            ]
        )

    # =========================================================================
    # SECTOR
    # =========================================================================

    def _infer_sector(
        self,
        text: str,
    ) -> str | None:

        normalized = text.lower()

        scores: list[
            tuple[str, int]
        ] = []

        for sector, signals in (
            self.SECTOR_SIGNALS.items()
        ):

            score = 0

            for signal in signals:

                if signal in normalized:
                    score += 1

            if score:
                scores.append(
                    (
                        sector,
                        score,
                    )
                )

        if not scores:
            return None

        scores.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scores[0][0]

    # =========================================================================
    # ATS KEYWORDS
    # =========================================================================

    def _build_ats_keywords(
        self,
        keyword_analysis: dict[str, Any],
    ) -> list[dict[str, Any]]:

        keywords = keyword_analysis.get(
            "keywords",
            [],
        )

        if not isinstance(
            keywords,
            list,
        ):
            return []

        ats_keywords: list[
            dict[str, Any]
        ] = []

        for keyword in keywords:

            if not isinstance(
                keyword,
                dict,
            ):
                continue

            importance = keyword.get(
                "importance",
                "low",
            )

            if importance not in {
                "required",
                "high",
                "preferred",
            }:
                continue

            ats_keywords.append(
                {
                    "keyword": keyword.get(
                        "text"
                    ),
                    "normalized": keyword.get(
                        "normalized"
                    ),
                    "importance": importance,
                    "category": keyword.get(
                        "category"
                    ),
                    "occurrences": keyword.get(
                        "occurrences",
                        0,
                    ),
                    "score": keyword.get(
                        "score",
                        0.0,
                    ),
                    "safe_to_add": False,
                }
            )

        ats_keywords.sort(
            key=lambda item: (
                self._importance_rank(
                    item.get(
                        "importance",
                        "low",
                    )
                ),
                float(
                    item.get(
                        "score",
                        0.0,
                    )
                ),
            ),
            reverse=True,
        )

        return ats_keywords

    def _importance_rank(
        self,
        importance: str,
    ) -> int:

        return {
            "required": 4,
            "high": 3,
            "preferred": 2,
            "medium": 1,
            "low": 0,
        }.get(
            importance,
            0,
        )

    # =========================================================================
    # AI ENRICHMENT
    # =========================================================================

    async def _enrich_with_ai(
        self,
        profile: JobProfile,
    ) -> JobProfile:
        """
        Optional semantic enrichment.

        The exact AI adapter is deliberately injected through ai_service.
        This avoids coupling this analyzer to a specific provider.

        Expected interface:

            await ai_service.chat(
                messages=[...],
                temperature=...,
                max_tokens=...,
            )

        If the provider has another interface, we will adapt it when
        connecting the project's actual AI service.
        """

        prompt = self._build_ai_prompt(
            profile
        )

        try:

            response = await self.ai_service.chat(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert job "
                            "description analyzer. "
                            "Return valid JSON only. "
                            "Never invent information."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=3500,
            )

        except Exception:
            # AI enrichment must never break the basic
            # deterministic analysis.
            return profile

        data = self._parse_ai_json(
            response
        )

        if not data:
            return profile

        return self._merge_ai_profile(
            profile,
            data,
        )

    def _build_ai_prompt(
        self,
        profile: JobProfile,
    ) -> str:

        profile_json = json.dumps(
            asdict(profile),
            ensure_ascii=False,
            indent=2,
        )

        return f"""
Analyze the following job offer.

The deterministic analyzer has already extracted
ATS-relevant information.

Your job is to enrich the semantic interpretation.

IMPORTANT RULES:

1. Never invent requirements.
2. Never invent skills.
3. Never invent company information.
4. Never invent experience requirements.
5. Preserve important terminology from the original job.
6. Distinguish required and preferred requirements.
7. Identify the professional sector.
8. Identify the domain when there is enough evidence.
9. Identify the role family when there is enough evidence.
10. Do not analyze or modify the candidate CV.
11. Do not create keywords that are not supported by the offer.
12. Return valid JSON only.

The system must support many professional domains, including but
not limited to:

- technology
- agriculture
- agronomy
- engineering
- healthcare
- finance
- law
- logistics
- sales
- marketing
- education
- hospitality
- manufacturing
- administration

Existing deterministic analysis:

{profile_json}

Return exactly this JSON structure:

{{
    "title": "string or null",
    "company": "string or null",
    "sector": "string or null",
    "domain": "string or null",
    "role_family": "string or null",
    "seniority": "string or null",
    "location": "string or null",
    "work_mode": "string or null",
    "employment_type": "string or null",
    "summary": "string or null",

    "responsibilities": [
        "string"
    ],

    "required_requirements": [
        {{
            "text": "string",
            "category": "skill|experience|education|language|certification|other",
            "importance": "required",
            "required": true
        }}
    ],

    "preferred_requirements": [
        {{
            "text": "string",
            "category": "skill|experience|education|language|certification|other",
            "importance": "preferred",
            "required": false
        }}
    ],

    "experience_requirements": [
        "string"
    ],

    "education_requirements": [
        "string"
    ],

    "language_requirements": [
        "string"
    ],

    "certification_requirements": [
        "string"
    ]
}}
"""

    # =========================================================================
    # AI JSON PARSING
    # =========================================================================

    def _parse_ai_json(
        self,
        response: Any,
    ) -> dict[str, Any] | None:

        if response is None:
            return None

        # Some providers return a plain string.
        if isinstance(
            response,
            str,
        ):
            content = response.strip()

        # Some adapters may return:
        # {"content": "..."}
        elif isinstance(
            response,
            dict,
        ):

            content = response.get(
                "content"
            )

            if not isinstance(
                content,
                str,
            ):
                return None

            content = content.strip()

        else:
            return None

        if not content:
            return None

        # Remove Markdown code fences.
        content = re.sub(
            r"^```json\s*",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"^```\s*",
            "",
            content,
        )

        content = re.sub(
            r"\s*```$",
            "",
            content,
        )

        # Direct JSON parse.
        try:

            parsed = json.loads(
                content
            )

            if isinstance(
                parsed,
                dict,
            ):
                return parsed

        except json.JSONDecodeError:
            pass

        # Try extracting the first JSON object.
        start = content.find(
            "{"
        )

        end = content.rfind(
            "}"
        )

        if start == -1 or end == -1:
            return None

        try:

            parsed = json.loads(
                content[
                    start:end + 1
                ]
            )

            if isinstance(
                parsed,
                dict,
            ):
                return parsed

        except json.JSONDecodeError:
            return None

        return None

    # =========================================================================
    # AI MERGE
    # =========================================================================

    def _merge_ai_profile(
        self,
        profile: JobProfile,
        data: dict[str, Any],
    ) -> JobProfile:

        scalar_fields = (
            "title",
            "company",
            "sector",
            "domain",
            "role_family",
            "seniority",
            "location",
            "work_mode",
            "employment_type",
            "summary",
        )

        for field_name in scalar_fields:

            value = data.get(
                field_name
            )

            if value is None:
                continue

            if not str(value).strip():
                continue

            setattr(
                profile,
                field_name,
                str(value).strip(),
            )

        # ---------------------------------------------------------------
        # Responsibilities
        # ---------------------------------------------------------------

        ai_responsibilities = (
            self._safe_string_list(
                data.get(
                    "responsibilities",
                    [],
                )
            )
        )

        profile.responsibilities = (
            self._deduplicate(
                profile.responsibilities
                + ai_responsibilities
            )
        )

        # ---------------------------------------------------------------
        # Requirements
        # ---------------------------------------------------------------

        profile.required_requirements = (
            self._merge_requirements(
                existing=(
                    profile.required_requirements
                ),
                incoming=data.get(
                    "required_requirements",
                    [],
                ),
                required=True,
            )
        )

        profile.preferred_requirements = (
            self._merge_requirements(
                existing=(
                    profile.preferred_requirements
                ),
                incoming=data.get(
                    "preferred_requirements",
                    [],
                ),
                required=False,
            )
        )

        # ---------------------------------------------------------------
        # Experience
        # ---------------------------------------------------------------

        profile.experience_requirements = (
            self._deduplicate(
                profile.experience_requirements
                + self._safe_string_list(
                    data.get(
                        "experience_requirements",
                        [],
                    )
                )
            )
        )

        # ---------------------------------------------------------------
        # Education
        # ---------------------------------------------------------------

        profile.education_requirements = (
            self._deduplicate(
                profile.education_requirements
                + self._safe_string_list(
                    data.get(
                        "education_requirements",
                        [],
                    )
                )
            )
        )

        # ---------------------------------------------------------------
        # Languages
        # ---------------------------------------------------------------

        profile.language_requirements = (
            self._deduplicate(
                profile.language_requirements
                + self._safe_string_list(
                    data.get(
                        "language_requirements",
                        [],
                    )
                )
            )
        )

        # ---------------------------------------------------------------
        # Certifications
        # ---------------------------------------------------------------

        profile.certification_requirements = (
            self._deduplicate(
                profile.certification_requirements
                + self._safe_string_list(
                    data.get(
                        "certification_requirements",
                        [],
                    )
                )
            )
        )

        return profile

    def _merge_requirements(
        self,
        existing: list[JobRequirement],
        incoming: Any,
        required: bool,
    ) -> list[JobRequirement]:

        result = list(
            existing
        )

        if not isinstance(
            incoming,
            list,
        ):
            return result

        existing_texts = {
            self._normalize_comparison(
                item.text
            )
            for item in result
        }

        for item in incoming:

            if not isinstance(
                item,
                dict,
            ):
                continue

            text = str(
                item.get(
                    "text",
                    "",
                )
            ).strip()

            if not text:
                continue

            normalized = (
                self._normalize_comparison(
                    text
                )
            )

            if normalized in existing_texts:
                continue

            category = str(
                item.get(
                    "category",
                    "other",
                )
            ).strip()

            result.append(
                JobRequirement(
                    text=text,
                    category=(
                        category
                        or "other"
                    ),
                    importance=(
                        "required"
                        if required
                        else "preferred"
                    ),
                    required=required,
                )
            )

            existing_texts.add(
                normalized
            )

        return result

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _safe_string_list(
        self,
        value: Any,
    ) -> list[str]:

        if not isinstance(
            value,
            list,
        ):
            return []

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    def _normalize_comparison(
        self,
        value: str,
    ) -> str:

        value = value.lower().strip()

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value

    def _deduplicate(
        self,
        values: list[str],
    ) -> list[str]:

        result: list[str] = []

        seen: set[str] = set()

        for value in values:

            value = str(
                value
            ).strip()

            if not value:
                continue

            normalized = (
                self._normalize_comparison(
                    value
                )
            )

            if normalized in seen:
                continue

            seen.add(
                normalized
            )

            result.append(
                value
            )

        return result

    def _deduplicate_requirements(
        self,
        requirements: list[JobRequirement],
    ) -> list[JobRequirement]:

        result: list[
            JobRequirement
        ] = []

        seen: set[str] = set()

        for requirement in requirements:

            normalized = (
                self._normalize_comparison(
                    requirement.text
                )
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(
                normalized
            )

            result.append(
                requirement
            )

        return result

    def _serialize_profile(
        self,
        profile: JobProfile,
    ) -> dict[str, Any]:

        return asdict(
            profile
        )


# ============================================================================
# MODULE-LEVEL INSTANCE
# ============================================================================

job_profile_analyzer = JobProfileAnalyzer()