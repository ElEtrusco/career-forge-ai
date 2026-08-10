from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from typing import Any


@dataclass
class JobKeyword:
    """
    A keyword or phrase extracted from a job description.
    """

    text: str
    normalized: str
    category: str
    importance: str
    occurrences: int
    score: float


class JobKeywordAnalyzer:
    """
    Extracts and compares job-description keywords.

    The implementation is intentionally domain-agnostic. It does not rely
    on a hard-coded list of technologies or professions.

    It is designed to be used before:
        - job matching
        - ATS scoring
        - CV tailoring
        - XYZ optimization
    """

    DEFAULT_STOPWORDS = {
        # Spanish
        "a",
        "al",
        "algo",
        "alguna",
        "algunas",
        "alguno",
        "algunos",
        "ante",
        "antes",
        "como",
        "con",
        "contra",
        "cual",
        "cuales",
        "cuando",
        "de",
        "del",
        "desde",
        "donde",
        "durante",
        "e",
        "el",
        "ella",
        "ellas",
        "ellos",
        "en",
        "entre",
        "era",
        "es",
        "esa",
        "esas",
        "ese",
        "eso",
        "esos",
        "esta",
        "estas",
        "este",
        "esto",
        "estos",
        "ha",
        "han",
        "hasta",
        "la",
        "las",
        "lo",
        "los",
        "más",
        "me",
        "mediante",
        "para",
        "pero",
        "por",
        "que",
        "qué",
        "se",
        "sea",
        "ser",
        "si",
        "sin",
        "sobre",
        "son",
        "su",
        "sus",
        "también",
        "te",
        "tiene",
        "tienen",
        "un",
        "una",
        "uno",
        "unos",
        "y",
        "ya",

        # English
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "our",
        "that",
        "the",
        "their",
        "this",
        "to",
        "with",
        "you",
        "your",
    }

    SECTION_IMPORTANCE = {
        "requirements": 1.35,
        "required": 1.35,
        "qualifications": 1.30,
        "must": 1.40,
        "responsibilities": 1.20,
        "skills": 1.25,
        "experience": 1.20,
        "preferred": 1.05,
        "benefits": 0.70,
        "about": 0.60,
        "other": 1.00,
    }

    REQUIRED_MARKERS = (
        "required",
        "requirements",
        "must have",
        "must-have",
        "mandatory",
        "essential",
        "required skills",
        "requisitos",
        "requisitos mínimos",
        "imprescindible",
        "obligatorio",
        "obligatoria",
        "se requiere",
        "necesario",
        "necesaria",
    )

    PREFERRED_MARKERS = (
        "preferred",
        "nice to have",
        "nice-to-have",
        "desired",
        "bonus",
        "preferred qualifications",
        "valoramos",
        "se valorará",
        "deseable",
        "valorable",
    )

    RESPONSIBILITY_MARKERS = (
        "responsibilities",
        "responsibility",
        "you will",
        "what you will do",
        "duties",
        "responsabilidades",
        "funciones",
        "tareas",
        "qué harás",
        "que harás",
    )

    SKILL_MARKERS = (
        "skills",
        "technical skills",
        "competencies",
        "competence",
        "skills required",
        "habilidades",
        "competencias",
        "conocimientos",
        "capacidades",
    )

    def __init__(
        self,
        stopwords: set[str] | None = None,
        max_ngram: int = 4,
    ) -> None:
        self.stopwords = stopwords or self.DEFAULT_STOPWORDS
        self.max_ngram = max(1, min(max_ngram, 6))

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(
        self,
        job_text: str,
        cv_text: str | None = None,
    ) -> dict[str, Any]:
        """
        Analyze a job description and optionally compare its keywords
        against a candidate CV.
        """

        if not job_text or not job_text.strip():
            raise ValueError("Job description is required")

        job_text = self._clean_text(job_text)
        cv_text = self._clean_text(cv_text or "")

        sections = self._detect_sections(job_text)

        candidates = self._extract_candidates(
            job_text=job_text,
            sections=sections,
        )

        keywords = self._score_candidates(candidates)

        if cv_text:
            matches = self._match_keywords(
                keywords=keywords,
                cv_text=cv_text,
            )
        else:
            matches = []

        required = [
            item
            for item in matches
            if item["importance"] == "required"
        ]

        preferred = [
            item
            for item in matches
            if item["importance"] == "preferred"
        ]

        high_priority = [
            item
            for item in matches
            if item["importance"] == "high"
        ]

        return {
            "keywords": matches,
            "required_keywords": required,
            "preferred_keywords": preferred,
            "high_priority_keywords": high_priority,
            "keyword_count": len(matches),
            "matched_count": sum(
                1 for item in matches if item["matched"]
            ),
            "missing_count": sum(
                1 for item in matches if not item["matched"]
            ),
            "coverage": self._calculate_coverage(matches),
        }

    def extract_keywords(
        self,
        job_text: str,
    ) -> list[dict[str, Any]]:
        """
        Extract keywords without requiring a CV.
        """

        result = self.analyze(job_text)

        return result["keywords"]

    def compare(
        self,
        job_text: str,
        cv_text: str,
    ) -> dict[str, Any]:
        """
        Compare job-description keywords against a CV.
        """

        return self.analyze(
            job_text=job_text,
            cv_text=cv_text,
        )

    # ------------------------------------------------------------------
    # TEXT NORMALIZATION
    # ------------------------------------------------------------------

    def normalize(self, value: str) -> str:
        """
        Normalize text for comparison while preserving the original
        display value separately.
        """

        value = value.lower().strip()

        value = unicodedata.normalize(
            "NFKD",
            value,
        )

        value = "".join(
            char
            for char in value
            if not unicodedata.combining(char)
        )

        value = re.sub(r"[^\w\s+#./&-]", " ", value)

        value = re.sub(r"\s+", " ", value)

        return value.strip()

    def _clean_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

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

    # ------------------------------------------------------------------
    # SECTION DETECTION
    # ------------------------------------------------------------------

    def _detect_sections(
        self,
        text: str,
    ) -> list[dict[str, Any]]:
        """
        Split a job description into rough semantic sections.

        This is deliberately heuristic. Later we can replace or enrich
        it with an LLM-based structured job parser.
        """

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return []

        sections: list[dict[str, Any]] = []

        current_name = "other"
        current_lines: list[str] = []

        for line in lines:
            detected = self._detect_section_name(line)

            if detected:
                if current_lines:
                    sections.append(
                        {
                            "name": current_name,
                            "text": " ".join(current_lines),
                        }
                    )

                current_name = detected
                current_lines = []
                continue

            current_lines.append(line)

        if current_lines:
            sections.append(
                {
                    "name": current_name,
                    "text": " ".join(current_lines),
                }
            )

        return sections

    def _detect_section_name(
        self,
        line: str,
    ) -> str | None:
        normalized = self.normalize(line)

        if len(normalized) > 100:
            return None

        if any(
            marker in normalized
            for marker in self.REQUIRED_MARKERS
        ):
            return "requirements"

        if any(
            marker in normalized
            for marker in self.PREFERRED_MARKERS
        ):
            return "preferred"

        if any(
            marker in normalized
            for marker in self.RESPONSIBILITY_MARKERS
        ):
            return "responsibilities"

        if any(
            marker in normalized
            for marker in self.SKILL_MARKERS
        ):
            return "skills"

        if normalized in {
            "requirements",
            "requisitos",
            "qualifications",
            "responsibilities",
            "responsabilidades",
            "skills",
            "habilidades",
            "competencies",
            "competencias",
            "experience",
            "experiencia",
            "preferred",
            "deseable",
        }:
            return normalized

        return None

    # ------------------------------------------------------------------
    # KEYWORD EXTRACTION
    # ------------------------------------------------------------------

    def _extract_candidates(
        self,
        job_text: str,
        sections: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []

        if sections:
            for section in sections:
                section_text = section["text"]

                section_candidates = self._extract_ngrams(
                    section_text
                )

                for candidate in section_candidates:
                    candidate["section"] = section["name"]
                    candidates.append(candidate)
        else:
            candidates.extend(
                self._extract_ngrams(job_text)
            )

        return candidates

    def _extract_ngrams(
        self,
        text: str,
    ) -> list[dict[str, Any]]:
        normalized_text = self.normalize(text)

        tokens = normalized_text.split()

        if not tokens:
            return []

        candidates: list[dict[str, Any]] = []

        for size in range(1, self.max_ngram + 1):
            for index in range(
                0,
                len(tokens) - size + 1,
            ):
                gram = tokens[
                    index:index + size
                ]

                if not self._valid_ngram(gram):
                    continue

                normalized = " ".join(gram)

                candidates.append(
                    {
                        "text": normalized,
                        "normalized": normalized,
                    }
                )

        return candidates

    def _valid_ngram(
        self,
        tokens: list[str],
    ) -> bool:
        if not tokens:
            return False

        if all(
            token in self.stopwords
            for token in tokens
        ):
            return False

        if len(tokens) == 1:
            token = tokens[0]

            if token in self.stopwords:
                return False

            if len(token) < 2:
                return False

            if token.isdigit():
                return False

            return True

        meaningful_tokens = [
            token
            for token in tokens
            if token not in self.stopwords
        ]

        if not meaningful_tokens:
            return False

        if len(meaningful_tokens) == 1:
            # Allow phrases such as:
            # "project management"
            # "data analysis"
            return True

        return True

    # ------------------------------------------------------------------
    # KEYWORD SCORING
    # ------------------------------------------------------------------

    def _score_candidates(
        self,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        counts = Counter(
            candidate["normalized"]
            for candidate in candidates
        )

        section_map: dict[str, list[str]] = {}

        for candidate in candidates:
            section_map.setdefault(
                candidate["normalized"],
                [],
            ).append(
                candidate.get("section", "other")
            )

        results: list[JobKeyword] = []

        for normalized, occurrences in counts.items():
            sections = section_map[normalized]

            importance_multiplier = max(
                self.SECTION_IMPORTANCE.get(
                    section,
                    1.0,
                )
                for section in sections
            )

            length_bonus = self._length_bonus(normalized)

            frequency_bonus = min(
                occurrences * 0.15,
                0.75,
            )

            score = (
                1.0
                + length_bonus
                + frequency_bonus
            ) * importance_multiplier

            importance = self._classify_importance(
                sections=sections,
                score=score,
            )

            results.append(
                JobKeyword(
                    text=normalized,
                    normalized=normalized,
                    category=self._guess_category(normalized),
                    importance=importance,
                    occurrences=occurrences,
                    score=round(score, 3),
                )
            )

        results.sort(
            key=lambda item: (
                item.score,
                len(item.normalized),
                item.occurrences,
            ),
            reverse=True,
        )

        # Keep the list manageable. The most useful terms normally
        # appear at the top after scoring.
        results = results[:150]

        return [
            asdict(item)
            for item in results
        ]

    def _classify_importance(
        self,
        sections: list[str],
        score: float,
    ) -> str:
        if "requirements" in sections:
            return "required"

        if "preferred" in sections:
            return "preferred"

        if score >= 2.2:
            return "high"

        if score >= 1.5:
            return "medium"

        return "low"

    def _length_bonus(
        self,
        keyword: str,
    ) -> float:
        token_count = len(
            keyword.split()
        )

        if token_count >= 4:
            return 0.60

        if token_count == 3:
            return 0.45

        if token_count == 2:
            return 0.25

        return 0.0

    def _guess_category(
        self,
        keyword: str,
    ) -> str:
        """
        Conservative category classification.

        We intentionally avoid a domain-specific dictionary here.
        Later the LLM job analyzer can provide a richer classification.
        """

        normalized = self.normalize(keyword)

        if any(
            marker in normalized
            for marker in (
                "years experience",
                "anos experiencia",
                "years of experience",
                "anos de experiencia",
            )
        ):
            return "experience"

        if any(
            marker in normalized
            for marker in (
                "degree",
                "bachelor",
                "master",
                "phd",
                "grado",
                "licenciatura",
                "master",
                "doctorado",
            )
        ):
            return "education"

        if any(
            marker in normalized
            for marker in (
                "language",
                "idioma",
                "english",
                "spanish",
                "espanol",
                "frances",
                "french",
                "german",
                "aleman",
            )
        ):
            return "language"

        return "skill_or_term"

    # ------------------------------------------------------------------
    # CV MATCHING
    # ------------------------------------------------------------------

    def _match_keywords(
        self,
        keywords: list[dict[str, Any]],
        cv_text: str,
    ) -> list[dict[str, Any]]:
        normalized_cv = self.normalize(cv_text)

        results: list[dict[str, Any]] = []

        for keyword in keywords:
            normalized_keyword = keyword["normalized"]

            exact_match = self._contains_term(
                normalized_cv,
                normalized_keyword,
            )

            fuzzy_match = False
            fuzzy_score = 0.0

            if not exact_match:
                fuzzy_score = self._fuzzy_match(
                    normalized_keyword,
                    normalized_cv,
                )

                fuzzy_match = fuzzy_score >= 0.88

            matched = exact_match or fuzzy_match

            item = dict(keyword)

            item.update(
                {
                    "matched": matched,
                    "match_type": (
                        "exact"
                        if exact_match
                        else "fuzzy"
                        if fuzzy_match
                        else "missing"
                    ),
                    "fuzzy_score": round(
                        fuzzy_score,
                        3,
                    ),
                }
            )

            results.append(item)

        return results

    def _contains_term(
        self,
        text: str,
        term: str,
    ) -> bool:
        """
        Word-aware matching.

        This avoids matching:
            "java"
        inside:
            "javascript"
        """

        escaped = re.escape(term)

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

    def _fuzzy_match(
        self,
        keyword: str,
        cv_text: str,
    ) -> float:
        """
        Conservative fuzzy matching.

        It is intentionally not aggressive because an ATS optimizer
        must never assume that two different professional skills are
        equivalent without evidence.
        """

        keyword_tokens = keyword.split()

        if not keyword_tokens:
            return 0.0

        cv_tokens = cv_text.split()

        if not cv_tokens:
            return 0.0

        window_size = len(keyword_tokens)

        best_score = 0.0

        for index in range(
            0,
            len(cv_tokens) - window_size + 1,
        ):
            window = " ".join(
                cv_tokens[
                    index:index + window_size
                ]
            )

            score = SequenceMatcher(
                None,
                keyword,
                window,
            ).ratio()

            best_score = max(
                best_score,
                score,
            )

            if best_score >= 0.98:
                break

        return best_score

    # ------------------------------------------------------------------
    # COVERAGE
    # ------------------------------------------------------------------

    def _calculate_coverage(
        self,
        keywords: list[dict[str, Any]],
    ) -> dict[str, float]:
        if not keywords:
            return {
                "overall": 0.0,
                "required": 0.0,
                "preferred": 0.0,
                "high_priority": 0.0,
            }

        def coverage(
            items: list[dict[str, Any]],
        ) -> float:
            if not items:
                return 100.0

            matched = sum(
                1
                for item in items
                if item["matched"]
            )

            return round(
                matched / len(items) * 100,
                2,
            )

        required = [
            item
            for item in keywords
            if item["importance"] == "required"
        ]

        preferred = [
            item
            for item in keywords
            if item["importance"] == "preferred"
        ]

        high_priority = [
            item
            for item in keywords
            if item["importance"] in {
                "required",
                "high",
            }
        ]

        return {
            "overall": coverage(keywords),
            "required": coverage(required),
            "preferred": coverage(preferred),
            "high_priority": coverage(high_priority),
        }


# ----------------------------------------------------------------------
# MODULE-LEVEL INSTANCE
# ----------------------------------------------------------------------

job_keyword_analyzer = JobKeywordAnalyzer()