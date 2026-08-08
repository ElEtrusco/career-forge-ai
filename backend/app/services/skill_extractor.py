import re
from typing import Dict, List

class SkillExtractor:
"""
Extrae y normaliza habilidades, idiomas y conceptos profesionales.

```
La expansión de conceptos puede activarse o desactivarse.
Esto permite utilizar el extractor de forma diferente para:

- CVs: podemos inferir skills a partir de conceptos.
- Ofertas: debemos detectar únicamente skills explícitamente mencionadas.
"""

def __init__(self):
    # ============================================================
    # HARD SKILLS
    # ============================================================

    self.hard_skills = {
        "python",
        "java",
        "javascript",
        "typescript",
        "fastapi",
        "django",
        "flask",
        "react",
        "nextjs",
        "node",
        "nodejs",
        "postgresql",
        "mysql",
        "mongodb",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "git",
        "github",
        "linux",
        "html",
        "css",
        "rest api",
        "api",
        "microservices",
        "machine learning",
        "deep learning",
        "pandas",
        "numpy",
        "sql",
    }

    # ============================================================
    # SOFT SKILLS
    # ============================================================

    self.soft_skills = {
        "teamwork",
        "leadership",
        "communication",
        "problem solving",
        "adaptability",
        "critical thinking",
        "time management",
        "creativity",
        "collaboration",
        "organization",
    }

    # ============================================================
    # SPANISH -> ENGLISH
    # ============================================================

    self.es_en_map = {
        "trabajo en equipo": "teamwork",
        "colaboración": "collaboration",
        "comunicación": "communication",
        "resolución de problemas": "problem solving",
        "adaptabilidad": "adaptability",
        "pensamiento crítico": "critical thinking",
        "gestión del tiempo": "time management",
        "creatividad": "creativity",
        "organización": "organization",
    }

    # ============================================================
    # CONCEPTOS -> HARD SKILLS
    # ============================================================

    self.concept_map = {
        "programación": ["python", "javascript"],
        "desarrollo web": ["html", "css", "javascript"],
        "bases de datos": ["sql", "mysql", "postgresql"],
        "backend": ["python", "fastapi", "django"],
        "frontend": ["html", "css", "javascript", "react"],
        "cloud": ["aws", "azure", "gcp"],
    }

    # ============================================================
    # LANGUAGES
    # ============================================================

    self.languages = {
        "english": [
            "english",
            "inglés",
            "ingles",
        ],
        "spanish": [
            "spanish",
            "español",
            "espanyol",
        ],
        "french": [
            "french",
            "francés",
            "frances",
        ],
        "german": [
            "german",
            "alemán",
            "aleman",
        ],
        "italian": [
            "italian",
            "italiano",
        ],
        "portuguese": [
            "portuguese",
            "portugués",
            "portugues",
        ],
    }

# ================================================================
# NORMALIZATION
# ================================================================

def normalize_text(self, text: str) -> str:
    """
    Normaliza el texto antes de realizar las búsquedas.
    """

    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# ================================================================
# HARD SKILLS
# ================================================================

def extract_hard_skills(
    self,
    text: str,
    expand_concepts: bool = True,
) -> List[str]:
    """
    Extrae hard skills directamente mencionadas.

    expand_concepts=True:
        También infiere skills a partir de conceptos profesionales.

    expand_concepts=False:
        Solo devuelve skills explícitamente mencionadas.
        Esto es especialmente importante para ofertas de empleo.
    """

    text = self.normalize_text(text)

    found = set()

    # ------------------------------------------------------------
    # Direct skills
    # ------------------------------------------------------------

    for skill in self.hard_skills:
        if skill == "rest api":
            pattern = r"(?<!\w)rest\s+apis?(?!\w)"
        else:
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found.add(skill)

    # ------------------------------------------------------------
    # Concept expansion
    # ------------------------------------------------------------

    if expand_concepts:
        for concept, skills in self.concept_map.items():
            if concept in text:
                found.update(skills)

    return sorted(found)

# ================================================================
# SOFT SKILLS
# ================================================================

def extract_soft_skills(self, text: str) -> List[str]:
    """
    Extrae soft skills en inglés y español.
    """

    text = self.normalize_text(text)

    found = set()

    for skill in self.soft_skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found.add(skill)

    for es_term, en_term in self.es_en_map.items():
        if es_term in text:
            found.add(en_term)

    return sorted(found)

# ================================================================
# LANGUAGES
# ================================================================

def extract_languages(self, text: str) -> List[str]:
    """
    Detecta idiomas mencionados en el texto.
    """

    text = self.normalize_text(text)

    found = set()

    for language, variants in self.languages.items():
        for variant in variants:
            pattern = r"(?<!\w)" + re.escape(variant) + r"(?!\w)"

            if re.search(pattern, text):
                found.add(language)
                break

    cefr_levels = r"(a1|a2|b1|b2|c1|c2)"

    if re.search(
        rf"\benglish\s*{cefr_levels}\b",
        text,
    ):
        found.add("english")

    if re.search(
        rf"\bfranc[eé]s\s*{cefr_levels}\b",
        text,
    ):
        found.add("french")

    return sorted(found)

# ================================================================
# MAIN EXTRACTION
# ================================================================

def extract_all(
    self,
    text: str,
    expand_concepts: bool = True,
) -> Dict[str, List[str]]:
    """
    Extrae todas las categorías disponibles.

    expand_concepts=True:
        Pensado principalmente para CVs.

    expand_concepts=False:
        Pensado para ofertas cuando queremos evitar
        inventar requisitos que no aparecen explícitamente.
    """

    text = self.normalize_text(text)

    return {
        "hard_skills": self.extract_hard_skills(
            text,
            expand_concepts=expand_concepts,
        ),
        "soft_skills": self.extract_soft_skills(text),
        "languages": self.extract_languages(text),
    }
```
